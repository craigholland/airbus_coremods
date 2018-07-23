"""Common service utils."""

import re
import types
import endpoints
from protorpc import message_types
from protorpc import remote

from google3.ops.netdeploy.netdesign.server.common import common_messages
from google3.ops.netdeploy.netdesign.server.common import common_service
from google3.ops.netdeploy.netdesign.server.errors import error_collector
from google3.ops.netdeploy.netdesign.server.errors import error_msg
from google3.ops.netdeploy.netdesign.server.metadata import metadata_api
from google3.ops.netdeploy.netdesign.server.permissions import permissions_validations
from google3.ops.netdeploy.netdesign.server.plans import planning
from google3.ops.netdeploy.netdesign.server.utils import authz
from google3.ops.netdeploy.netdesign.server.utils import constants
from google3.ops.netdeploy.netdesign.server.utils import json_utils
from google3.ops.netdeploy.netdesign.server.utils import message_utils
from google3.ops.netdeploy.netdesign.server.utils import model_utils

# Match 2 adjacent upper case characters.
_ADJACENT_UPCASE_RE = re.compile(r'.*[A-Z][A-Z]')


def _PatchEntity(model, existing_entity_dict, new_entity_dict):
  """Merges entity dictionaries for PATCH updates.

  New entity dictionary values overwrite those in the existing entity
  dictionary, with the exception of DHNoteProperty fields. Those values are
  combined so that new notes are appended. Subclasses can override this method
  if note appending behavior is undesirable.

  Args:
    model: ndb.Model, The model for patching.
    existing_entity_dict: dict, Current entity state as stored.
    new_entity_dict: dict, Subset of entity fields provided from client.
  Returns:
    dict, The complete updated entity.
  """
  model_utils.MergeNotes(model, existing_entity_dict, new_entity_dict)
  existing_entity_dict.update(new_entity_dict)
  return existing_entity_dict


def Get(key_name, controller, response_type, execution_date=None):
  """Get existing entity.

  Args:
    key_name: str, the key_name of the entity to get.
    controller: The entity specific controller.
    response_type: The entity ProtoRPC response type.
    execution_date: end date to fetch a planned object.

  Returns:
    MessageResponse, ProtoRPC response message for Get operation.

  Raises:
    endpoints.NotFoundException: When the entity is not found.
    endpoints.BadRequestException: When the request is not valid.
  """
  errors = error_collector.Errors()
  kind = controller.model._get_kind()  # pylint: disable=protected-access
  if not key_name:
    errors.Raise(
        endpoints.BadRequestException, None, error_msg.KEYNAME_MISSING % kind)
  with planning.PlanDate(execution_date):
    entity = controller.Get(key_name)
  if not entity:
    errors.Raise(endpoints.NotFoundException, None,
                 error_msg.ENTITY_MISSING % (kind, key_name))
  else:
    filtered_entity = permissions_validations.ValidateReadPermissions(
        [entity], kind, errors)[0]
    errors.RaiseIfAny(common_service.ConflictException)
    return message_utils.DictToMessage(response_type, filtered_entity.to_dict())


def ListFilter(request, kind, list_filter_fields=None):
  """List filters.

  Args:
    request: protorpc.messages.Message, message that containing request
        parameters.
    kind: str, the kind of the entity.
    list_filter_fields: None or [str | {str: str, ...}], field names to allow
        filtering on.  If None, then indexed fields' names from the controller's
         model will be used (retrieved via metadata).
        If list and an entry is a dict then it's keys will be assumed to be the
        request facing name of the field and the values are assumed to be the
        actual name of the field, otherwise the string value will be used for
        both the request attribute and name of the field.

  Returns:
    dict, filter items for this request.
  """
  list_filter_fields = (
      list_filter_fields or metadata_api.GetIndexedFieldsCached(kind))

  filters = {}
  for field in list_filter_fields:
    if isinstance(field, basestring):
      value = getattr(request, field, None)
      if value or value in (False, 0, ''):
        filters[field] = value
    elif isinstance(field, dict):
      for alias, actual in field.iteritems():
        value = getattr(request, alias, None)
        if value or value in (False, 0, ''):
          filters[actual] = value

  if filters and request.q:
    raise endpoints.BadRequestException(constants.FILTER_AND_Q_ERROR)

  return filters


def ListLimit(request):
  """List limit.

  Args:
    request: protorpc.messages.Message, message that containing request
        parameters.

  Returns:
    int, limit attribute from the request maxResults or the default limit.
  """
  max_results = getattr(request, 'maxResults', None)
  if max_results:
    return min(max_results, constants.LIST_MAX_LIMIT)
  else:
    return constants.LIST_DEFAULT_LIMIT


def ListSort(request):
  """List sort.

  Args:
    request: protorpc.messages.Message, message that containing request
        parameters.

  Returns:
    str, sort attribute with prefixed '-' for desc.
  """
  attribute_to_sort = getattr(request, 'orderBy', None)
  attribute_sort_order = getattr(request, 'sortOrder', None)
  sort_by = None

  if attribute_to_sort and attribute_sort_order:
    sort_order = attribute_sort_order.lower()
    if sort_order == 'desc':
      sort_by = '-' + attribute_to_sort
    elif sort_order == 'asc':
      sort_by = attribute_to_sort
    else:
      errors = error_collector.Errors()
      errors.Raise(common_service.ConflictException, 'sortOrder',
                   'must be either "asc" or "desc"')
  return sort_by


def ListResponse(request, kind, list_response_type,
                 list_response_items_field, entity_response_type, limit,
                 results, cursor, message_converter=None):
  """List response.

  Args:
    request: protorpc.messages.Message, message that containing request
        parameters.
    kind: str, the kind of the entity.
    list_response_type: protorpc.messages.Message, message type to return.
    list_response_items_field: str, attribute on list_response_type that should
        contain the entities.
    entity_response_type: protorpc.messages.Message | types.StringType, the
        message that each entity will be put in.  If types.StringType then each
        entity will be converted to a JSON string.
    limit: int, maximum number of records per page.
    results: list<Model>, read results for this list request.
    cursor: string, ending cursor.
    message_converter: optional message converter method.

  Returns:
    protorpc.messages.Message, instance of list_response_type
  """
  filter_fields = set(getattr(request, 'filterFields', ()))
  dict_args = {}
  if filter_fields:
    filter_fields.add('key_name')
    dict_args['include'] = filter_fields

  resp = list_response_type()
  resp.nextPageToken = cursor
  if entity_response_type is types.StringType:
    # convert to json
    setattr(resp, list_response_items_field,
            [json_utils.Dump(model_instance.to_dict(**dict_args))
             for model_instance in results])
  else:
    if message_converter:
      values = map(message_converter, results)
    else:
      values = [message_utils.DictToMessage(entity_response_type,
                                            model_instance.to_dict(**dict_args))
                for model_instance in results]
    setattr(resp, list_response_items_field, values)
  resp.currentItemCount = len(results)
  resp.itemsPerPage = limit

  if hasattr(resp, 'kind'): setattr(resp, 'kind', kind)
  return resp


def List(request, controller, list_response_type, list_response_items_field,
         entity_response_type, list_filter_fields):
  """List entities.

  Args:
    request: protorpc.messages.Message, message that containing request
        parameters.
    controller: controller instance to use for reading entities.
    list_response_type: protorpc.messages.Message, message type to return.
    list_response_items_field: str, attribute on list_response_type that should
        contain the entities.
    entity_response_type: protorpc.messages.Message | types.StringType, the
        message that each entity will be put in.  If types.StringType then each
        entity will be converted to a JSON string.
    list_filter_fields: None or [str | {str: str, ...}], field names to allow
        filtering on.  If None, then indexed fields' names from the controller's
         model will be used (retrieved via metadata).
        If list and an entry is a dict then it's keys will be assumed to be the
        request facing name of the field and the values are assumed to be the
        actual name of the field, otherwise the string value will be used for
        both the request attribute and name of the field.

  Returns:
    protorpc.messages.Message, instance of list_response_type
  """
  errors = error_collector.Errors()
  kind = controller.model._get_kind()  # pylint: disable=protected-access
  filters = ListFilter(request, kind, list_filter_fields)
  limit = ListLimit(request)
  sort_by = ListSort(request)

  if request.planDate and request.q:
    raise endpoints.BadRequestException(
        'Searching in planned entities is not supported.')
  with planning.PlanDate(request.planDate):
    # If request.planDate is None, the "with" will have no effect.
    results, cursor, _ = controller.Read(
        limit=limit, start_cursor=request.pageToken, filters=filters,
        q=request.q, sort_by=sort_by)
    filtered_results = permissions_validations.ValidateReadPermissions(
        results, kind, errors)
    errors.RaiseIfAny(common_service.ConflictException)
    resp = ListResponse(
        request, kind, list_response_type, list_response_items_field,
        entity_response_type, limit, filtered_results, cursor)
  return resp


# TODO(cupton): After service cleanup look at moving these into common_service.
def Delete(key_name, controller):
  """Delete existing entity.

  Args:
    key_name: str, the key_name of the entity to delete.
    controller: The entity specific controller.

  Returns:
    message_types.VoidMessage, Void.

  Raises:
    common_service.ConflictException: When delete fails due to bad request
    or validation.
  """
  errors = error_collector.Errors()
  kind = controller.model._get_kind()  # pylint: disable=protected-access
  if not key_name:
    errors.Raise(
        endpoints.BadRequestException, None, error_msg.KEYNAME_MISSING % kind)

  permissions_validations.ValidateDeletePermissions(kind, errors)
  errors.RaiseIfAny(common_service.ConflictException)

  controller.Delete(key_name, errors)
  errors.RaiseIfAny(common_service.ConflictException)
  return message_types.VoidMessage()


def Create(request, controller, response_type):
  """Create given entity.

  Args:
    request: messages.Message, message for entity creation.
    controller: The entity specific controller.
    response_type: messages.Message, the entity ProtoRPC response type.
  Returns:
    Message with the created entity.
  Raises:
    common_service.ConflictException: When failure occurs during validation
    and/or entity creation.
  """
  errors = error_collector.Errors()

  kind = controller.model._get_kind()  # pylint: disable=protected-access
  permissions_validations.ValidateCreatePermissions(kind, errors)
  errors.RaiseIfAny(common_service.ConflictException)

  entity_dict = message_utils.MessageToDict(request)
  model_utils.MergeNotes(controller.model, {}, entity_dict)
  with planning.VersionId(entity_dict.get('version_id', None)):
    created_entity = controller.Create(entity_dict, errors)
  errors.RaiseIfAny(common_service.ConflictException)
  return message_utils.DictToMessage(response_type, created_entity.to_dict())


def Update(request, controller, response_type, opt_exclusion=None,
           merge_by_permissions=False):
  """Updates given entity.

  Args:
    request: messages.Message, message for entity creation.
    controller: The entity specific controller.
    response_type: messages.Message, the entity ProtoRPC response type.
    opt_exclusion: List, values to strip from the Message if different from
      the defaults in message_utils.
    merge_by_permissions: bool, If True, merge only readonly values using the
      current user permissions.  If False, use the previous merge logic.

  Returns:
    Message with the created entity.

  Raises:
    common_service.ConflictException: When failure occurs during validation
    and/or entity creation.
  """
  entity_dict = message_utils.MessageToDict(request, None, opt_exclusion)
  errors = error_collector.Errors()
  model = controller.model
  kind = model._get_kind()  # pylint: disable=protected-access
  # Performs entity patching.
  key_name = entity_dict.get(constants.KEY_NAME)
  if not key_name:
    errors.Raise(
        common_service.ConflictException,
        constants.KEY_NAME, error_msg.KEYNAME_MISSING % kind)
  with planning.VersionId(entity_dict.get('version_id', None)):
    existing_entity = model.get_by_id(key_name)
    if existing_entity:
      if merge_by_permissions:
        existing_entity_dict = existing_entity.to_dict()
        permissions_validations.ValidateUpdatePermissions(
            existing_entity_dict, entity_dict, kind, errors)
        errors.RaiseIfAny(common_service.ConflictException)
        # TODO(rupalig): MergeNotes for entities with notes only.
        model_utils.MergeNotes(model, existing_entity_dict, entity_dict)
      else:
        exclude = set(metadata_api.GetFieldNames(model, ui_readonly=True))
        exclude -= set(metadata_api.GetFieldNames(model, required=True))
        existing_entity = existing_entity.to_dict(exclude=exclude)
        entity_dict = _PatchEntity(model, existing_entity, entity_dict)
    else:
      errors.Add(constants.KEY_NAME, error_msg.ENTITY_MISSING %
                 (kind, key_name))
    if not errors:
      updated_entity = controller.Update(entity_dict, errors)
  errors.RaiseIfAny(common_service.ConflictException)
  return message_utils.DictToMessage(response_type, updated_entity.to_dict(),
                                     None, opt_exclusion)


def _CamelPluralToCommonForm(s):
  """Transform the plural kind name to snake or lower case as needed."""

  # snake_case doesn't fit some models (e.g., BOM, OMS, LSOptics) so we
  # scan the string for an adjacent pair of upper-case characters and if
  # such a pair is found, we simply lower case the string. Otherwise,
  # convert to snake_case.
  if _ADJACENT_UPCASE_RE.match(s):
    return s.lower()

  buf = s[0].lower()
  for c in s[1:]:
    if c.isupper():
      buf += '_' + c.lower()
    else:
      buf += c
  return buf


def BuildService(name,
                 plural_name,
                 controller,
                 response,
                 list_request,
                 list_response,
                 create_request,
                 update_request,
                 list_filter_fields=None,
                 mixins=None,
                 api_path=None,
                 use_api_singular_name=True,
                 merge_by_permissions=False):
  """Builds a protorpc service class that has basic CRUD operations defined.

  Example usage:

  SubTopologyService = common_service_utils.BuildService(
    name='SubTopology',
    plural_name='SubTopologies',
    controller=sub_topology_controller.SubTopologyController,
    response=capacity_messages.SubTopologyResponse,
    list_request=capacity_messages.LIST_SUB_TOPOLOGIES_REQUEST,
    list_response=capacity_messages.ListSubTopologiesResponse,
    list_filter_fields=[
        'key_name', 'name',
        {'version': 'key_version',
         'capacity': 'CapacityReference__name'}
    ],
    create_request=capacity_messages.CreateSubTopologyRequest,
    update_request=capacity_messages.UPDATE_SUB_TOPOLOGY_REQUEST)

  The function call above results in a generated class that will have the
  following endpoints defined:

  /api/SubTopologies.CreateSubTopology     # appengine endpoint
  /.../subTopologies/subTopologies.create  # apiary endpoint
    create_request -> response             # input & output types

  /api/SubTopologies.UpdateSubTopology
  /.../subTopologies/subTopologies.update
    update_request -> response

  /api/SubTopologies.DeleteSubTopology
  /.../subTopologies/subTopologies.delete
    key_name -> protorpc.message_types.VoidMessage

  /api/SubTopologies.GetSubTopology
  /.../subTopologies/subTopologies.get
    key_name -> response

  /api/SubTopologies.ListSubTopology
  /.../subTopologies/subTopologies.list
    list_request -> list_response

  Custom endpoints can be mixed-in if necessary. E.g.

  class ListByContinentMixin(object):
    @endpoints.method(ListByContinentRequest,
                      ListSubTopologiesResponse,
                      path='subTopologies',
                      http_method='GET',
                      name='subTopologies.listByContinent')
    def ListByContinent(self, request):
      ...
      return response

  SubTopologyService = common_service_utils.BuildService(
    name='SubTopology',
    plural_name='SubTopologies',
    controller=sub_topology_controller.SubTopologyController,
    response=capacity_messages.SubTopologyResponse,
    list_request=capacity_messages.LIST_SUB_TOPOLOGIES_REQUEST,
    list_response=capacity_messages.ListSubTopologiesResponse,
    list_filter_fields=[
        'key_name', 'name',
        {'version': 'key_version',
         'capacity': 'CapacityReference__name'}
    ],
    create_request=capacity_messages.CreateSubTopologyRequest,
    update_request=capacity_messages.UPDATE_SUB_TOPOLOGY_REQUEST
    mixins=[ListByContinentMixin])

  Note the last 'mixin' parameter.  This creates an additional endpoint:

    /api/SubTopologies.ListByContinent                # appengine endpoint
    /.../subTopologies/subTopologies.listByContinent  # apiary endpoint

  Args:
    name: str, name of the resource for which the service is to be built
        (in CamelCase*).
    plural_name: str, the resource's plural name (in CamelCase*).
    controller: class, the controller for the resource to be used. The
                controller must have the following signature:

                # Create: dict, error_collector -> ndb.Model
                # Update: dict, error_collector -> ndb.Model
                # Delete: key_name:str, error_collector
                # Get:    key_name:str -> ndb.Model
                # Read:   same arguments and return as common_controller.List()
                          except that there is no model argument.
    response: protorpc.messages.Message, the message that the Read, Create, and
        Update endpoints will return.
    list_request: endpoints.ResourceContainer, type that the List endpoint
        accepts.  Note, this container must contain fields that are defined in
        common_messages.DefaultListParams.
    list_response: protorpc.messages.Message, type that the List endpoint will
        return.
    create_request: protorpc.messages.Message, type that the Create endpoint
        accepts.
    update_request: endpoints.ResourceContainer, type that the Update endpoint
        accepts.  Note that key_name must be part of the container.
    list_filter_fields: None or [str | {str: str, ...}], field names that the
        List endpoint will allow filtering on.  If None, then indexed fields'
        names from the controller's model will be used (retrieved via metadata).
        If list and an entry is a dict then it's keys will be assumed to be the
        request facing name of the field and the values are assumed to be the
        actual name of the field, otherwise the string value will be used for
        both the request attribute and name of the field.
    mixins: list, optional list of class types the generated class will
        inherit/mixin.
    api_path: str, optional path under which the endpoint is to be made
        available. Note that specifying this will override the generated path
        which is `plural_name` with the first letter lowercased.
          e.g. if api_path='dhSubTopologies' then the generated services will be
               made available under 'dhSubTopologies/...'.
    * The camel case transform doesn't happen to a value when the first two
      characters of the value are both upper-case. Instead, the value is
      simply translated into lower case.
    use_api_singular_name: boolean, a flag to indicate if singular naming
        convention should be used for generating API service name, by default
        this flag is True so singular names are generated for service name.
        If this flag is False, then plural name is used for
        generating service name.
    merge_by_permissions: boolean, If True, merge only readonly values using the
      current user permissions.  If False, use the previous merge logic
      (patching).

  Returns:
    A generated class with basic CRUD endpoints defined.
  """

  assert type(update_request) == endpoints.api_config.ResourceContainer, (
      'update_request must be a ResourceContainer')

  lcase_plural = plural_name[0].lower() + plural_name[1:]
  list_response_items_field = _CamelPluralToCommonForm(plural_name)
  api_path = api_path or lcase_plural

  @endpoints.method(create_request, response,
                    path=api_path,
                    http_method='POST',
                    name=api_path + '.create')
  @authz.EndpointsLoginRequired
  def _Create(self, request):
    """Create method which is forwarded to common_service_utils.Create."""
    return Create(request, self.controller, response)

  @endpoints.method(update_request, response,
                    path=api_path + '/{key_name}',
                    http_method='PUT',
                    name=api_path + '.update')
  @authz.EndpointsLoginRequired
  def _Update(self, request):
    """Update method which is forwarded to common_service_utils.Update."""
    return Update(request, self.controller, response,
                  merge_by_permissions=merge_by_permissions)

  @endpoints.method(common_messages.DELETE_REQUEST,
                    message_types.VoidMessage,
                    path=api_path + '/{key_name}',
                    http_method='DELETE',
                    name=api_path + '.delete')
  @authz.EndpointsLoginRequired
  def _Delete(self, request):
    """Delete method which is forwarded to common_service_utils.Delete."""
    return Delete(request.key_name, self.controller)

  @endpoints.method(common_messages.GET_REQUEST, response,
                    path=api_path + '/{key_name}',
                    http_method='GET',
                    name=api_path + '.get')
  @authz.EndpointsLoginRequired
  def _Get(self, request):
    """Get method which is forwarded to common_service_utils.Get."""
    return Get(request.key_name, self.controller, response, request.planDate)

  @endpoints.method(list_request, list_response,
                    path=api_path,
                    http_method='GET',
                    name=api_path + '.list')
  @authz.EndpointsLoginRequired
  def _List(self, request):
    """List method that returns paginated lists of the resource."""
    return List(request, self.controller, list_response,
                list_response_items_field, response, list_filter_fields)

  def _Init(self):
    self.controller = controller()
    # pylint: disable=protected-access
    if not getattr(self.controller, '_model_name', None):
      self.controller._model_name = self.controller.model._get_kind()
    self.list_filter_fields = (list_filter_fields or
                               metadata_api.GetIndexedFieldsCached(
                                   self.controller._model_name))
    # pylint: enable=protected-access

  methods = {
      '__init__': _Init,
      'List' + plural_name: _List,
      'Get' + name: _Get,
      'Create' + name: _Create,
      'Update' + name: _Update,
      'Delete' + name: _Delete
  }

  # since we are unable to fully utilize mixins w/remote methods (the
  # remote api only inspects base methods), patch in the mixin remote
  # methods on the class directly.
  if mixins:
    for mixin in mixins:
      for attr_name in mixin.__dict__:
        attr = mixin.__dict__[attr_name]
        if type(attr) == types.FunctionType and hasattr(attr, 'remote'):
          methods[attr_name] = attr

  # By default using singular service names for APIs.
  if (use_api_singular_name and
      name not in ('CapacityReference', 'NetworkConnection', 'RolePair')):
    service_prefix = name
  else:
    service_prefix = plural_name

  cls = type(service_prefix + 'Service', (remote.Service,), methods)
  return common_service.api_root.api_class()(cls)
