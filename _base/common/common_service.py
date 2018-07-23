"""Common API Messages for use behind Lily/Apiary."""

import functools
import hashlib
import httplib
import importlib
import logging
import operator
import sys

import endpoints
from protorpc import messages
from protorpc import protojson
from protorpc import remote
import webapp2

from google.appengine.api import memcache
from google.appengine.ext import ndb

from google3.ops.netdeploy.netdesign.server.common import autocomplete_controller
from google3.ops.netdeploy.netdesign.server.common import common_controller
from google3.ops.netdeploy.netdesign.server.common import common_messages
from google3.ops.netdeploy.netdesign.server.errors import error_collector
from google3.ops.netdeploy.netdesign.server.permissions import acl_api
from google3.ops.netdeploy.netdesign.server.user import user_utils
from google3.ops.netdeploy.netdesign.server.utils import authz
from google3.ops.netdeploy.netdesign.server.utils import constants
from google3.ops.netdeploy.netdesign.server.utils import conversion_utils
from google3.ops.netdeploy.netdesign.server.utils import json_utils
from google3.ops.netdeploy.netdesign.server.utils import message_utils
from google3.ops.netdeploy.netdesign.server.utils import model_utils


_ALL_MODULES = [
    'admin.admin_messages',
    'hardware.hardware_service',
    'locations.location_messages',
    'metadata.metadata_messages',
    'traffic.traffic_messages',
]

_EXCLUDE_PROPS = [
    'deleted',
]

# Cache to hold messages.
_message_cache = {}


# Common API
api_root = endpoints.api(
    name='netdeploy',
    version='v1',
    description='Manages network data',
    # Use scope integer values as described in go/feauthforswarm.
    # Note: email scope not required, see b/17189179.
    scopes=['40200'],  # https://www.googleapis.com/auth/netdeploy
    # Allow all client IDs since we validate by email.
    allowed_client_ids=endpoints.SKIP_CLIENT_ID_CHECK,
    # Disallow cookies to pass through to backend.
    auth=endpoints.api_config.ApiAuth(allow_cookie_auth=False),
    # Use frontend auth and pass through to backend on failure.
    auth_level=endpoints.AUTH_LEVEL.OPTIONAL_CONTINUE,
)


class ConflictException(endpoints.ServiceException):
  """Conflict exception that is mapped to a 409 response."""
  http_status = httplib.CONFLICT


def AssembleProtoListResponse(results, cursor, limit, model, response):
  """Assembles a List response given the results, cursor, and ordering info.

  This method does not fill in the values field, leaving that to the calling
  subclass.  It's meant as a convenience routine to provide a function call to
  eliminate boilerplate assignment code.

  It assumes the following fields are defined on the message:
      kind
      nextPageToken
      currentItemCount
      itemsPerPage

  Args:
    results: list<ndb.Model>, A list of the results.
    cursor: str, A datastore cursor for pagination.
    limit: integer, The limit of number of items to return.
    model: str, The model name.
    response: messages.Message, An existing response message.

  Returns:
    messages.Message, Completed response message.
  """
  response.kind = model
  response.nextPageToken = cursor  # pylint: disable=g-bad-name
  response.currentItemCount = len(results)  # pylint: disable=g-bad-name
  response.itemsPerPage = limit  # pylint: disable=g-bad-name
  return response


# TODO(sselph): Determine the best way to implement these 2 functions after
# protojson changes.
def _ModelToMessage(message, entity, api_kind=None):
  """Model to message that encodes all fields."""
  entity_dict = entity.to_dict()
  entity_dict['id'] = str(entity.key.id())
  if api_kind is None:
    # Create a lowerCamelCase version of the kind per style guide.
    kind = entity.key.kind()
    api_kind = kind[0].lower() + kind[1:]
  entity_dict['kind'] = 'netdeploy#' + api_kind
  return protojson.decode_message(message, json_utils.Dump(entity_dict))


def _MessageToDict(message):
  """Simple MessageToDict."""
  encoder = protojson.MessageJSONEncoder()
  msg_dict = encoder.default(message)
  if 'kind' in msg_dict:
    del msg_dict['kind']
  if msg_dict['id'].isdigit():
    msg_dict['id'] = int(msg_dict['id'])
  return msg_dict


# TODO(dlindquist): Consider changing default level to DEBUG and allow override
# from an application setting.
def RequestLogger(level=logging.INFO):
  """Decorator for logging endpoints method requests.

  Args:
    level: int, one of the standard logging levels, or None if logging should be
        disabled. Default is INFO.

  Returns:
    A decorator function for altering the endpoints method.
  """
  def Decorator(endpoints_func):
    @functools.wraps(endpoints_func)
    def Inner(self, request):
      if level:
        logging.log(
            level, '%s.%s request: %r', self.__class__.__name__,
            endpoints_func.__name__, request)
      return endpoints_func(self, request)
    return Inner
  return Decorator


def HashListRequest(kind, request):
  """Creates an ID for a collection based on the LIST_REQUEST.

  Args:
    kind: str, the kind name.
    request: common_messages.LIST_REQUEST, the request to hash.
  Returns:
    str, md5 hash of kind and all field values.
  """

  # Pages in the same collection should share the same ID.
  exclude = ('pageToken', 'maxResults')

  out = [kind]
  fields = request.all_fields()
  fields = sorted(fields, key=operator.attrgetter('name'))
  for field in fields:
    if field.name not in exclude:
      out.append(unicode(getattr(request, field.name, '')))
  to_hash = ''.join(out)
  return hashlib.md5(to_hash.encode('utf-8')).hexdigest()


def GetCache(key, message):
  """Get message from memcache and decode it.

  Args:
    key: str, the memcache key.
    message: messages.Message, the message type to use for decoding.

  Returns:
    message.Message instance or None if not in memcache.
  """
  response = memcache.get(key)
  if response is not None:
    response = protojson.decode_message(message, response)
  return response


def SetCache(key, data, timeout=86400):
  """Set decoded message in memcache.

  If data is >1MB it will not be set.

  Args:
    key: str, the memcache key.
    data: message.Message instance, the message to place in cache.
    timeout: int, the timeout in seconds for memcache.
  """
  try:
    memcache.set(key, protojson.encode_message(data), timeout)
  except ValueError:  # If data is >1MB
    pass


def ModelToMessage(entity, service='netdeploy', kind=None, message_class=None):
  """Converts a Model to a Message of the same name.

  Args:
    entity: ndb.Model instance.
    service: str, the service for the protorpc kind field (service#kind),
        This argument will get passed to nested models.
    kind: str, the kind for the protorpc kind field (service#kind) if None it
        will use the model name. If there are nested models there is no way to
        pass this argument to them.
    message_class: subclass of messages.Message, the message class to be used
        for storing the converted model data.

  Returns:
    messages.Message instance.
  """
  # pylint: disable=protected-access
  if message_class:
    message_type = message_class
  else:
    message_type = GetMessage(entity._get_kind())
  message_fields = {f.name for f in message_type.all_fields()}
  message_fields -= set(_EXCLUDE_PROPS)
  ikeys = (entity._projection or entity._properties).iterkeys()
  entity_dict = {n: getattr(entity, n) for n in ikeys if n in message_fields}
  # pylint: enable=protected-access

  if entity.key:
    entity_dict['id'] = entity.key.id()
  if service:
    k = kind or entity._get_kind().lower()  # pylint: disable=protected-access
    entity_dict['kind'] = '%s#%s' % (service, k)

  def GetDecoder(field):
    if message_utils.IsMessageField(field):
      return lambda v: ModelToMessage(v, service=service)
    p = entity._properties.get(field.name)  # pylint: disable=protected-access
    if isinstance(p, (
        ndb.DateTimeProperty, ndb.DateProperty, ndb.TimeProperty)):
      if isinstance(field, messages.IntegerField):
        return conversion_utils.ToInt
      elif isinstance(field, messages.StringField):
        return conversion_utils.DateObjToStr
    elif isinstance(p, ndb.KeyProperty):
      return lambda v: v.urlsafe()

  return message_utils.DictToMessage(
      message_type, entity_dict, decoder_factory=GetDecoder)


def GetMessage(name):
  """Get a message class by name.

  This function searches all modules in this package to find the named Message.

  Args:
    name: string, the name of the model class.

  Returns:
    The Message class or None if it can't be found.
  """
  if name in _message_cache:
    return _message_cache[name]

  modules = [__name__] + ['.'.join(
      [constants.BASE_MODULE, x]) for x in _ALL_MODULES]

  # Make sure all modules are imported.
  for module in modules:
    if module not in sys.modules:
      importlib.import_module(module)

  # Search the modules for valid messages.Message with the name.
  for module in modules:
    if name not in sys.modules[module].__dict__:
      continue
    m = sys.modules[module].__dict__.get(name)
    try:
      if issubclass(m, messages.Message):
        _message_cache[name] = m
        return m
    except TypeError:
      continue
  return None


@api_root.api_class()
class CommonService(remote.Service):
  """Common API calls.

  Attributes:
    METADATA: str, metadata name for API call.
    response: GeneralResponse, response message.
  """

  METADATA = 'netdeploy#'
  response = common_messages.GeneralResponse

  def _Get(self, request, current_user=None):
    """Get a single resource.

    Args:
      request: request, protorpc request.
      current_user: endpoints.User, current user.

    Returns:
      GeneralResponse, generated response message.

    Raises:
      endpoints.NotFoundException, when no entities found.
    """
    entity_id = request.id
    model = request.model
    if entity_id.isdigit():
      entity_id = int(entity_id)
    key = ndb.Key(model, entity_id)
    entity = key.get()
    if entity is None:
      raise endpoints.NotFoundException
    response = self.response()
    response.kind = '%s%s' % (self.METADATA, request.model)
    acl = acl_api.GetAclForKind(request.model)
    response.values = []
    groups = None
    # If the request is coming through Web ProtoRPC, endpoints current user
    # will be None. That way groups for current user can be determined using
    # cookie method, which is the default one. For requests that are coming
    # from endpoints, groups should be explicitly passed to FilterReadAsync().
    if current_user and not user_utils.IsCurrentUserServiceAccount():
      groups = authz.GetGroups(current_user.nickname(), method='rest')

    if user_utils.IsCurrentUserServiceAccount():
      response.values.append(json_utils.Dump(entity.to_dict()))
      logging.info('Service account %s is given read access.',
                   current_user.nickname())
    else:
      filtered_results = acl.FilterReadAsync(
          entity.to_dict(), groups=groups).get_result()
      response.values.append(json_utils.Dump(filtered_results))
    # pylint: disable=g-bad-name
    response.currentItemCount = 1
    # pylint: enable=g-bad-name
    return response

  @endpoints.method(common_messages.ID_MODEL_REQUEST,
                    common_messages.GeneralResponse,
                    path='common/{model}/{id}', http_method='GET',
                    name='common.get')
  @authz.EndpointsLoginRequired
  def Get(self, request):
    """Get a single resource.

    Args:
      request: request, protorpc request.

    Returns:
      GeneralResponse, generated response message.
    """
    user = endpoints.get_current_user()
    return self._Get(request, current_user=user)

  def _List(self, request, current_user=None):
    """Get all entities for given model.

    Args:
      request: request, protorpc request.
      current_user: endpoints.User, current user.

    Returns:
      GeneralResponse, generated response message.

    Raises:
      endpoints.NotFoundException, When no model is found.
    """
    limit = request.maxResults or constants.LIST_DEFAULT_LIMIT
    start_cursor = request.pageToken
    model = model_utils.GetModel(request.model)
    filters = {}
    name = getattr(request, 'name', None)
    if name:
      filters['name'] = name
    key_subtype = getattr(request, 'keySubtype', None)
    if key_subtype:
      filters['key_subtype'] = key_subtype
    alias = getattr(request, 'alias', None)
    if alias:
      filters['alias'] = alias

    q = getattr(request, 'q', None)
    if q and filters:
      raise endpoints.BadRequestException(constants.FILTER_AND_Q_ERROR)

    results, cursor, unused_more = common_controller.List(
        model, limit=limit, start_cursor=start_cursor, q=q, filters=filters)
    response = self.response()
    response.kind = '%s%s' % (self.METADATA, request.model)
    acl = acl_api.GetAclForKind(request.model)
    response.values = []
    groups = None
    # If the request is coming through Web ProtoRPC, endpoints current user
    # will be None. That way groups for current user can be determined using
    # cookie method, which is the default one. For requests that are coming
    # from endpoints, groups should be explicitly passed to FilterReadAsync().
    if current_user and not user_utils.IsCurrentUserServiceAccount():
      groups = authz.GetGroups(current_user.nickname(), method='rest')

    if user_utils.IsCurrentUserServiceAccount():
      logging.info('Service account %s is given read access.',
                   current_user.nickname())

    for r in results:
      if not user_utils.IsCurrentUserServiceAccount():
        filtered_results = acl.FilterReadAsync(
            r.to_dict(), groups=groups).get_result()
      else:
        filtered_results = r.to_dict()
      response.values.append(json_utils.Dump(filtered_results))

    response.nextPageToken = cursor  # pylint: disable=g-bad-name
    affected = len(response.values)
    if not results:
      logging_message = 'No %ss found!' % model
    else:
      plural = '' if affected == 1 else 's'
      logging_message = 'Returned %d %s%s.' % (affected, request.model, plural)

    logging.info(logging_message)
    response.currentItemCount = affected  # pylint: disable=g-bad-name
    response.itemsPerPage = limit  # pylint: disable=g-bad-name
    return response

  @endpoints.method(common_messages.ALL_REQUEST,
                    common_messages.GeneralResponse,
                    path='common/{model}', http_method='GET',
                    name='common.list')
  @authz.EndpointsLoginRequired
  def List(self, request):
    """Get all entities for given model.

    The main functionality of this function is in a private function to avoid
    mocking decorators in unit tests.

    Args:
      request: request, protorpc request.

    Returns:
      GeneralResponse, generated response message.
    """
    user = endpoints.get_current_user()
    return self._List(request, current_user=user)


class AutocompleteServiceView(webapp2.RequestHandler):
  """Provides operations for Autocomplete."""

  def get(self, *unused_args, **unused_kwargs):  # pylint: disable=g-bad-name
    """Executes GET autocomplete."""
    errors = error_collector.Errors()
    response = {}

    keyword = self.request.GET.get('keyword')
    max_results = int(
        self.request.GET.get('maxResults')) if self.request.GET.get(
            'maxResults') else 10
    kind = self.request.GET.get('model')
    model = model_utils.GetModel(kind)

    logging.info(
        'Autocomplete API for kind: %s keyword: %s, limit: %d', kind, keyword,
        max_results)

    result, more = autocomplete_controller.GetAutoComplete(
        model, errors, keyword=keyword, limit=max_results)

    # Format the results like the previous protoRPC service.
    response_data = []
    for r in result:
      response_data.append({'id': r[0], 'name': r[1]})

    response = {
        'items': response_data,
        'kind': 'netdeploy#' + kind,
        'more': more,
        'currentItemCount': len(result)
    }

    self.response.content_type = 'application/json; charset=utf-8'

    if errors:
      self.response.write(errors.AsJson())
    else:
      self.response.write(json_utils.Dump(response))
