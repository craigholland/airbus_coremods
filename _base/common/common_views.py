"""Common views for Double Helix app."""

import hashlib
import json
import logging
import os
import pprint
import socket
import webapp2
from webapp2_extras import jinja2

from google.appengine.api import app_identity
from google.appengine.api import datastore_errors
from google.appengine.api import memcache
from google.appengine.api import modules
from google.appengine.api import search
from google.appengine.api import users
from google.appengine.datastore import datastore_query
from google.appengine.ext import ndb
from google.appengine.runtime import apiproxy_errors

from google3.ops.netdeploy.netdesign.server.admin import admin_controller
from google3.ops.netdeploy.netdesign.server.admin import admin_messages
from google3.ops.netdeploy.netdesign.server.admin import admin_models
from google3.ops.netdeploy.netdesign.server.admin import setting_controller
from google3.ops.netdeploy.netdesign.server.bom import bom_controller
from google3.ops.netdeploy.netdesign.server.bom import bom_item_controller
from google3.ops.netdeploy.netdesign.server.capacity import capacity_controller
from google3.ops.netdeploy.netdesign.server.capacity import capacity_reference_controller
from google3.ops.netdeploy.netdesign.server.capacity import network_connection_controller
from google3.ops.netdeploy.netdesign.server.errors import error_collector
from google3.ops.netdeploy.netdesign.server.hardware import hardware_models
from google3.ops.netdeploy.netdesign.server.logical_locations import logical_locations_controller
from google3.ops.netdeploy.netdesign.server.logs import log_codes
from google3.ops.netdeploy.netdesign.server.logs import logs_api
from google3.ops.netdeploy.netdesign.server.metadata import metadata_api
from google3.ops.netdeploy.netdesign.server.metadata import metadata_utils
from google3.ops.netdeploy.netdesign.server.parts import parts_controller
from google3.ops.netdeploy.netdesign.server.paths import path_models
from google3.ops.netdeploy.netdesign.server.permissions import permissions_validations
from google3.ops.netdeploy.netdesign.server.search import search_api
from google3.ops.netdeploy.netdesign.server.user import user_preference_controller
from google3.ops.netdeploy.netdesign.server.user import user_utils
from google3.ops.netdeploy.netdesign.server.utils import authz
from google3.ops.netdeploy.netdesign.server.utils import constants
from google3.ops.netdeploy.netdesign.server.utils import conversion_utils
from google3.ops.netdeploy.netdesign.server.utils import csv_utils
from google3.ops.netdeploy.netdesign.server.utils import importer
from google3.ops.netdeploy.netdesign.server.utils import json_utils
from google3.ops.netdeploy.netdesign.server.utils import message_utils
from google3.ops.netdeploy.netdesign.server.utils import model_utils

MAX_HUGE_SORT = 10000


def TrySetMemCache(mkey, content, cache_timeout):
  """Populate the memcache if you can, but don't die if you can't."""
  try:
    memcache.set(mkey, content, cache_timeout)
  except ValueError:
    pass


class IndexView(webapp2.RequestHandler):
  """Main view that displays the ribbon."""

  @webapp2.cached_property
  def _Jinja2(self):
    """Returns a Jinja2 renderer cached in the app registry."""
    return jinja2.get_jinja2(app=self.app)

  def _RenderResponse(self, template, **context):
    """Renders a template and writes the result to the response.

    Args:
      template: str, The template filename.
      **context: dict, Arguments used as variables to render the template.
    """
    rv = self._Jinja2.render_template(template, **context)
    self.response.write(rv)

  def _GetRoutes(self, have_user):
    """Returns branch and routes.

    Args:
      have_user: Boolean, indicates if we have a logged-in user.  There should
        always be a user logged in, except for dev_appserver2 warmup requests.

    Returns:
      Two-tuple of str, a Branch key and the JSON-encoded list of routes.
    """
    branch = 'master'
    routes = admin_messages.Route(path='/')
    if have_user:
      version = self.request.GET.get('version')
      config_ctrl = admin_controller.ClientConfig(version=version)
      config, branch_key = config_ctrl.GetConfig()
      if config and config.routes:
        routes = config.routes
      if branch_key:
        branch = branch_key.id()
    return branch, message_utils.MessageToJson(routes)

  def get(self, *unused_args, **unused_kwargs):  # pylint: disable=g-bad-name
    """Return the index page."""
    user = users.get_current_user()
    if user is None:
      user_email = ''
      branch, routes = self._GetRoutes(False)
    else:
      user_email = user.email()
      branch, routes = self._GetRoutes(True)
    ldap_groups = set(user_utils.GetCurrentUserGroups(strip=True))
    app_id = app_identity.get_application_id()
    version_name = modules.get_current_version_name()
    media_url = '/static/%s/' % version_name
    dev_host = 'http://%s:5200' % socket.gethostname().split(':')[0]

    prod = app_id == constants.APP_IDENTITY_PROD
    devlocal = app_id == constants.APP_IDENTITY_DEVAPPSERVER
    environment = constants.APP_ID_BUCKET_SUFFIXES[app_id]

    user_prefs_future = user_preference_controller.ReadPrefs(user.nickname())

    user_details = authz.GetUserDetails()
    if user_details:
      user_full_name = user_details['fullName']
    else:
      user_full_name = ''

    # Google Analytics Settings
    settings_ctrl = setting_controller.SettingController()

    # Create a settings map for usage on the front-end.
    settings_dict = {s.name: s for s in settings_ctrl.Read()}
    logging.debug('Config Settings as READ: %s', pprint.pformat(settings_dict))
    # Fake a special setting when running on a developer local server.
    if 'IS_ENV_LOCALHOST' not in settings_dict:
      settings_dict['IS_ENV_LOCALHOST'] = {
          'key_name': 'IS_ENV_LOCALHOST',
          'text_value': 'true' if devlocal else 'false'
      }
    all_settings = json_utils.Dump(settings_dict)

    ga_settings = settings_ctrl.Read(name='GOOGLE_ANALYTICS_UA')
    if ga_settings:
      ga_property_id = ga_settings[0].text_value
    else:
      ga_property_id = constants.GA_PROPERTY_ID_DEFAULT

    # Get 'primary group' for sending to Google Analytics
    primary_groups_settings = settings_ctrl.Read(name='PRIMARY_GROUPS')
    try:
      primary_groups_setting = primary_groups_settings[0]
    except IndexError:
      logging.error('App Property PRIMARY_GROUPS not set')
      primary_group = 'not set'
    else:
      for group in primary_groups_setting.values_list:
        if group in ldap_groups:
          primary_group = group
          break
      else:
        primary_group = 'unknown'

    if prod:
      compiled = True
      local = False
    else:
      compiled = (os.environ.get('COMPILED', '') or
                  self.request.GET.get('compiled'))
      if app_id == constants.APP_IDENTITY_DEVAPPSERVER:
        local = False
      else:
        local = self.request.GET.get('local')
        if isinstance(local, basestring) and local.endswith('.corp.google.com'):
          dev_host = ('http://%s:5200' % local)
          media_url = ('http://%s:9000' % local) + media_url
        elif local:
          media_url = 'http://' + constants.SERVERS['local'][0] + media_url
        else:
          compiled = True

    user_pref_types, user_pref_values = user_prefs_future.get_result()
    user_pref_types = json_utils.Dump(user_pref_types)
    user_pref_values = json_utils.Dump(user_pref_values)

    self._RenderResponse(
        'index.html',
        all_settings=all_settings,
        branch=branch,
        compiled=compiled,
        ga_property_id=ga_property_id,
        groups=json_utils.Dump(ldap_groups),
        local=local,
        dev_host=dev_host,
        media_url=media_url,
        primary_group=primary_group,
        prod=prod,
        devlocal=devlocal,
        environment=environment,
        app_id=app_id,
        request=self.request,
        routes=routes,
        user_email=user_email,
        user_full_name=user_full_name,
        user_pref_types=user_pref_types,
        user_pref_values=user_pref_values,
        username=user,
        version_name=version_name,
    )


class InfoView(webapp2.RequestHandler):
  """View information about the logged in user."""

  def get(self):  # pylint: disable=g-bad-name
    """Handle GET requests."""
    user = users.get_current_user()
    user_info = 'Email: %s<br>ID: %s<br>Admin: %s<br>Nickname: %s<br>' % (
        user.email(), user.user_id(),
        users.is_current_user_admin(), user.nickname())
    self.response.write(user_info)

    auth_method = user_utils.GetAuthMethod()
    groups = 'Groups: %s<br>' % ', '.join(
        authz.GetGroups(method=auth_method, strip=True))
    self.response.write(groups)
    self.response.write('Auth Method: %s<br>' % auth_method.lower())


# TODO(sselph): Split this into 3 separate API calls and
# have the client pull all 3.
class RouterFaceView(webapp2.RequestHandler):
  """View for the RouterFace API."""

  def _ToStr(self, item):
    """Convert item to a str."""
    if isinstance(item, basestring):
      return item
    if isinstance(item, ndb.Key):
      return item.string_id()
    return str(item)

  def _ConvertToString(self, items):
    """Convert a list of models to strings.

    Args:
      items: list of ndb.Models.
    Returns:
      list of dict, each key is str of ndb.Key, value is str of ndb.Model.
    """
    out = []
    for item in items:
      out_dict = {}
      for key, value in item.to_dict().iteritems():
        if isinstance(value, list):
          value = [self._ToStr(x) for x in value]
        else:
          value = self._ToStr(value)
        out_dict[key] = value
      out.append(out_dict)
    return out

  def get(self, *unused_args, **unused_kwargs):  # pylint: disable=g-bad-name
    """Fetch hardware, circuit, interface data for a device."""
    self.response.content_type = 'application/json'
    dev = self.request.GET.get('k')
    if not dev:
      self.response.write(json_utils.Dump({
          'device': '',
          'paths': [],
          'interfaces': [],
          'hardware': []}))
      return
    dev_key = ndb.Key('Device', dev)
    paths = path_models.CircuitPath.query(
        path_models.CircuitPath.devices == dev_key,
        path_models.CircuitPath.state == 'ASBUILT').fetch()
    interfaces = path_models.PhysicalInterface.query(
        path_models.PhysicalInterface.device == dev_key).fetch()
    hardware_model = hardware_models.Hardware
    hardware = hardware_model.query(hardware_model.node == dev).fetch()
    hardware = self._ConvertToString(hardware)
    hardware = sorted(hardware, key=lambda x: x['name'])
    paths = self._ConvertToString(paths)
    interfaces = self._ConvertToString(interfaces)
    out = {
        'device': dev,
        'paths': paths,
        'interfaces': interfaces,
        'hardware': hardware,
    }
    self.response.write(json_utils.Dump(out))


def _GetPage(query, limit, cached_cursor, offset):
  """Retrieves a page of results from the data store.

  Args:
    query: The query to run.
    limit: The maximum number of results.
    cached_cursor: The cached cursor to use, if any.
    offset: The offset to apply, if any.

  Returns:
    The page of keys, and a cursor for the next page (if any), and a more flag.
  """
  if limit:
    if cached_cursor:
      keys, cursor, more = query.fetch_page(
          limit, keys_only=True, start_cursor=cached_cursor)
    else:
      keys, cursor, more = query.fetch_page(
          limit, keys_only=True, offset=offset)
  else:
    cursor = None
    more = False
    if cached_cursor:
      keys = query.fetch(keys_only=True, start_cursor=cached_cursor)
    else:
      keys = query.fetch(keys_only=True, offset=offset)
  return keys, cursor, more


class TableView(webapp2.RequestHandler):
  """Generic API view for Table Views.

  Attributes:
    page_size: int, default page size when not specified in query string.
    page_limit: int, maximum page size regardless of query string.
    key_kind: string, the model kind for the view.
    model: class, BaseModel subclass.
  """
  page_size = 60
  page_limit = 1000
  cache_timeout = 60  # Only 1 minute so that new rows aren't missed.
  key_kind = None
  model = None

  nc_controller = network_connection_controller.NetworkConnectionController
  cr_controller = capacity_reference_controller.CapacityReferenceController
  KIND_CONTROLLER_MAP = {
      'BOM': bom_controller.BOMController,
      'BOMItem': bom_item_controller.BOMItemController,
      'Metro': logical_locations_controller.MetroController,
      'CapacityReference': cr_controller,
      'DHTPS': capacity_controller.TpsController,
      'NetworkConnection': nc_controller,
      'Part': parts_controller.PartController,
  }

  def dispatch(self):  # pylint: disable=g-bad-name
    """Get Expando model before dispatching the request."""
    self.key_kind = self.request.route_kwargs.get('key_kind')
    self.model = model_utils.GetModel(self.key_kind)
    controller_class = self.KIND_CONTROLLER_MAP.get(self.key_kind, None)
    self.controller = controller_class() if controller_class else None
    super(TableView, self).dispatch()

  def post(self, *unused_args, **unused_kwargs):  # pylint: disable=g-bad-name
    """Handle CSV import."""

    # Check model level permissions on update.
    metadata = metadata_api.GetMetadata(self.key_kind)
    if metadata:
      logging.info('Checking model level update permissions for model %s',
                   self.key_kind)
      errors = error_collector.Errors()
      access_type = metadata.access_type
      permissions_validations.CheckModelLevelWriteAccess(
          self.key_kind, access_type, errors)
      if errors:
        result = {}
        self.error(403)
        result['type'] = 'error'
        result['errors'] = {0: errors.Get('__generic__')[0]}
        self.response.content_type = 'text/plain'
        self.response.write(json_utils.Dump(result))
        return

    batch_rows, fieldnames = self._ExtractRowsAndFields()
    if batch_rows:
      result = self._Import(batch_rows, fieldnames)
    else:
      result = {'type': 'fail'}
    self.response.content_type = 'text/plain'
    self.response.write(json_utils.Dump(result))

  def _Import(self, batch_rows, fieldnames):
    """Import rows and fields."""
    batch = self.request.GET.get('batch', None)
    part = self.request.GET.get('part', None)
    imp = importer.Importer(self.key_kind, batch_rows, fieldnames, batch, part)
    result = {}
    if imp.IsValid():
      results = imp.Import()
      if imp.errors:
        result['type'] = 'error'
        result['errors'] = imp.errors
      else:
        result['type'] = 'success'
        result['results'] = results
    else:
      result['type'] = 'invalid'
      result['batch_errors'] = imp.batch_errors
    return result

  def _ExtractRowsAndFields(self):
    """Extract rows and fields from the request."""
    post_data = self.request.POST
    batch_rows = fieldnames = None
    if 'csv' in post_data:
      if conversion_utils.ToBool(self.request.GET.get('is_final', False)):
        log_message = constants.CSVIMPORT_LOG % (
            users.get_current_user(), self.key_kind)
        logs_api.Info(log_codes.LOG_CSV, log_message, entity_kind=self.key_kind)
      csv_field = post_data.get('csv', None)
      csv_file = getattr(csv_field, 'file', None)
      if csv_file:
        defaults = json_utils.Get(self.request.GET, 'defaults', {})
        batch_rows = csv_utils.CsvReader(csv_file, defaults=defaults)
        fieldnames = batch_rows.field_names
    elif 'rows' in post_data:
      batch_rows = json_utils.Get(post_data, 'rows', [])
      fieldnames = json_utils.Get(post_data, 'columns', [])
    return batch_rows, fieldnames

  def _EnsureReadAccess(self):
    """Ensure that the user can read on the given model specified in key_kind.

    If the user does not have read access, this will set the response to a
    JSON-formatted error message.

    Returns:
      True if the user has read access, False otherwise.
    """

    errors = error_collector.Errors()
    permissions_validations.ValidateReadPermissions([], self.key_kind, errors)
    if errors:
      self.error(403)
      self.response.content_type = 'application/json'
      self.response.out.write(errors.AsJson())
    return not errors

  def get(self, *unused_args, **unused_kwargs):  # pylint: disable=g-bad-name
    """Return the data in the requested format."""
    if not self._EnsureReadAccess(): return
    if self.request.GET.get('csv'):
      self.response.content_type = 'text/csv'
    else:
      self.response.content_type = 'application/json'
    columns = admin_models.TableView.GetColumns(self.key_kind)

    filter_fields = self.request.GET.get('filterFields')
    if filter_fields and not self.request.GET.get('all_columns'):
      filter_fields = (field.strip() for field in filter_fields.split(','))
      columns = list(set(columns).intersection(filter_fields))

    if self.request.GET.get('csv'):
      # Restore the ordering to the columns as this will be visible.
      view = self.request.GET.get('view', None)
      if self.request.GET.get('all_columns') == '1':
        view = None
      columns = [column for column in
                 admin_models.TableView.GetColumns(self.key_kind, view)
                 if column in columns]
      # Insert columns necessary for import.
      if constants.KEY_VERSION not in columns:
        columns.insert(0, constants.KEY_VERSION)
      if constants.KEY_KIND not in columns:
        columns.insert(0, constants.KEY_KIND)
      if constants.DELETED not in columns:
        columns.append(constants.DELETED)

    try:
      limit = int(self.request.GET.get('limit', ''))
    except ValueError:
      limit = None

    try:
      offset = int(self.request.GET.get('offset', ''))
    except ValueError:
      offset = 0

    result = {'rows': [], 'logs': []}
    if self.request.GET.get('count'):
      count = self.GetCount(result['logs'].append)
      result['count'] = count
    else:
      try:
        keys = self.GetQueryKeys(limit=limit, offset=offset,
                                 log=result['logs'].append)
      except search_api.BadQueryException as bad_query:
        self.error(400)
        error_struct = json.dumps(
            {
                'error_message': str(bad_query),
                'error_name': 'Bad Request',
                'state': 'APPLICATION_ERROR'
            }
        )
        self.response.out.write(error_struct)
        return
      result['rows'].extend(self.GetRows(keys, columns, result['logs'].append))

    result['dir'] = str(dir(self.response))
    if self.request.GET.get('csv'):
      csv_utils.DumpCsv(self.response, columns, result['rows'])
    else:
      self.response.write(json_utils.Dump(result))

  def GetCount(self, log):
    """Return the number of records matching the query.

    Args:
      log: A function to append to the log.
    Returns:
      The number of matching records.
    Raises:
      BadRequestException: Upon failure to parse query parameters.
    """
    key_name = self.request.GET.get('k', '')

    if key_name:
      return 1

    query_string = self.request.GET.get('q', '')
    if query_string:
      try:
        _, count, _ = self._WalkSearch(query_string, 100000, None, False,
                                       log=log)
        return count
      except search_api.BadQueryException as bad_query:
        self.error(400)
        error_struct = json.dumps(
            {
                'error_message': str(bad_query),
                'error_name': 'Bad Request',
                'state': 'APPLICATION_ERROR'
            }
        )
        self.response.out.write(error_struct)
        return
      except (search.Error, apiproxy_errors.OverQuotaError):
        logging.exception('Search API Quota error.')
        return [], '', False

    return self.model.query().count()

  def _GetQueryKeysMkey(self, query_string, limit, descending, order_name,
                        offset):
    return 'GetQueryKeys:' + _Hexdigest('%s:%s:%d:%s:%d' % (
        self.key_kind, query_string, limit or 0,
        ('-%s' if descending else '%s') % order_name, offset or 0))

  def _GetQueryKeysCursorMkey(self, query_string, descending, order_name,
                              offset):
    return 'GetQueryKeysCursor:' + _Hexdigest('%s:%s:%s:%d' % (
        self.key_kind, query_string,
        ('-%s' if descending else '%s') % order_name, offset or 0))

  def _GetSkipSortKey(self, order_name):
    return 'SkipSortKey:' + _Hexdigest('%s:%s' % (self.key_kind, order_name))

  def _WalkSearch(self, query_string, offset, order_name, descending,
                  gather=False, log=lambda x: 0):
    """Search only works in limited size batches. Seek the target offset.

    Args:
      query_string: The search string.
      offset: The target offset.
      order_name: The field name to sort by.
      descending: Whether to sort in a descending order.
      gather: Return all the keys instead of a count and a cursor.
      log: A function to append to the result log.

    Returns:
      A cursor, or None if we run out of results before reaching the target.
      An integer, the number of entries seen.
      A list of results (empty if gather is false)
    """
    log('WalkSearch: %s %s %s %s' %
        (query_string, offset, order_name, descending))
    cursor = None
    effective_offset = 0
    all_results = []
    while offset > 0:
      if offset < search.MAXIMUM_SEARCH_OFFSET:
        limit = offset
      else:
        limit = search.MAXIMUM_SEARCH_OFFSET

      # Check if a cached cursor for the next batch exists.
      if not gather:
        request_cursor_key = self._GetQueryKeysCursorMkey(
            query_string, descending, order_name, effective_offset + limit)
        cached_cursor = memcache.get(request_cursor_key)
        if cached_cursor:
          log('Got cached cursor for effective offset %s' % effective_offset)
          if limit == offset:
            # We've found a cursor for the target offset; use it.
            return cached_cursor, effective_offset + limit, []
          # We've found the next cursor in the sequence, continue walking.
          cursor = cached_cursor
          offset -= limit
          effective_offset += limit
          continue

      request = search_api.BuildRequest(
          query_string, limit=limit, start_cursor=cursor)
      if order_name:
        request.orderBy = order_name
      if descending:
        request.sortOrder = 'descending'
      log('Getting search keys for %s' % request.__dict__)
      results, cursor, more = search_api.GetSearchKeys(self.key_kind, request)
      log('Got %d results...' % len(results))
      if gather:
        all_results.extend(results)
      # Cache the results; they may be useful.
      mkey = self._GetQueryKeysMkey(query_string, limit, descending, order_name,
                                    offset)
      TrySetMemCache(mkey, results, self.cache_timeout)

      if not more:
        return None, len(results) + effective_offset, all_results

      effective_offset += limit

      # Cache the cursor; it may be useful
      save_cursor_key = self._GetQueryKeysCursorMkey(
          query_string, descending, order_name, effective_offset)
      TrySetMemCache(save_cursor_key, cursor, self.cache_timeout)

      offset -= limit
    return cursor, effective_offset, all_results

  def GetQueryKeys(self, limit=None, offset=0, log=lambda x: 0):
    """Return query keys and optionally filter results.

    Args:
      limit: int, the maximum number of keys to return.
      offset: The number of results to skip.
      log: A logging function.
    Returns:
      A list of key objects, sorted if possible.
    Raises:
      BadRequestException: Upon failure to parse query parameters.
    """
    key_name = self.request.GET.get('k', '')

    if key_name:
      return [ndb.Key(self.key_kind, key_name)]

    query_string = self.request.GET.get('q', '')
    order_name = self.request.GET.get('order_by', '')
    descending = self.request.GET.get('dir', 'asc') != 'asc'

    # The client executes two requests in sequence, the first just retrieves
    # the count and cursor (so that the next page can be started in parallel),
    # the second retrieves the actual rows. The query/search results are cached
    # to improve the performance of the 2nd request.
    mkey = self._GetQueryKeysMkey(query_string, limit, descending, order_name,
                                  offset)
    cached = memcache.get(mkey)
    if cached is not None:
      return cached

    # Result set is large; data store sorting won't work. Get unordered and sort
    # in the server.
    huge = self.request.GET.get('huge')

    if not huge and query_string and order_name:
      order = getattr(self.model, order_name, self.model.key_order)
      # pylint: disable=protected-access
      metadata_field = metadata_utils.GetFieldByName(
          self.model._meta, order._name)
      if not metadata_field or not metadata_field.index_for_search:
        log('Unindexed field; falling back to huge mode.')
        huge = True
      else:
        log('Sorting on indexed field %s' % order._name)
      # pylint: enable=protected-access
    if huge and query_string and order_name:
      log('In huge mode; manual sorting')
      # Check memcache for sorted match
      ordered_mkey = self._GetQueryKeysMkey(query_string, 100000, False,
                                            order_name, 0)
      ordered_results = memcache.get(ordered_mkey)

      if not ordered_results:
        log('Sorted results not in memcache...')
        # Check memcache for general match.
        unordered_mkey = self._GetQueryKeysMkey(query_string, 100000, False,
                                                None, 0)
        unordered_results = memcache.get(unordered_mkey)
        if not unordered_results:
          log('Unsorted results not in memcache either...')
          _, _, unordered_results = self._WalkSearch(
              query_string, 100000, None, False, gather=True, log=log)
          log('Gathered unsorted results...')
          try:
            log('Storing unordered Tableview result data in memcache...')
            TrySetMemCache(unordered_mkey, unordered_results,
                           self.cache_timeout)
          except ValueError as e:
            log('Storing unordered data in memcache failed (probably too big).'
                ' Error: %s' % e)
        if len(unordered_results) < MAX_HUGE_SORT:
          mini_rows = self.GetRows(unordered_results, [order_name], log)
          log('Gathered sort field data...')
          sorted_rows = sorted(mini_rows, key=lambda x: x[order_name])
          log('Sorted results...')
          ordered_results = [ndb.Key(self.key_kind, row['key_name']) for row in
                             sorted_rows]
          try:
            log('ordered Tableview result data in memcache...')
            TrySetMemCache(ordered_mkey, ordered_results, self.cache_timeout)
          except ValueError:
            log('Storing ordered data in memcache failed (probably too big).'
                ' Error: %s' % e)
        else:
          log('Over %s records; not sorting.' % MAX_HUGE_SORT)
          ordered_results = unordered_results
      if descending:
        ordered_results.reverse()

      if limit:
        return ordered_results[offset:offset + limit]
      return ordered_results[offset:]

    log('Ordering by %s%s' % ('-' if descending else '', order_name))

    request_cursor_key = self._GetQueryKeysCursorMkey(query_string, descending,
                                                      order_name, offset)
    cached_cursor = memcache.get(request_cursor_key)

    if query_string:
      # At this point, we have a query string, which means that we have to
      # get entities indirectly after looking them up in the Search index, but
      # either the results are small or there is no ordering required.
      try:
        if cached_cursor:
          cursor = cached_cursor
          log('Using cached cursor...')
        elif not offset:
          cursor = None
          log('At start of data set...')
        else:
          # Get a cursor for the target offset.
          log('Walking to offset %s...' % offset)
          cursor, _, _ = self._WalkSearch(query_string, offset, order_name,
                                          descending, log=log)
          if not cursor:
            log('Ran out of results.')
            # Ran out of results; return nothing rather than the first batch.
            return []
        request = search_api.BuildRequest(query_string, limit=limit,
                                          start_cursor=cursor)
        if order_name:
          request.orderBy = order_name
        if descending:
          request.sortOrder = 'descending'
        log('Getting search keys for %s' % request.__dict__)
        results, cursor, more = search_api.GetSearchKeys(self.key_kind, request)
        # Cache results
        total_len = len(results)
        all_results = results
        while more and cursor:
          # Cache next cursor, if present.
          save_cursor_key = self._GetQueryKeysCursorMkey(
              query_string, descending, order_name,
              (offset or 0) + total_len)
          log('Saving cursor...')
          TrySetMemCache(save_cursor_key, cursor, self.cache_timeout)
          if limit is None or total_len < limit:
            request = search_api.BuildRequest(query_string, limit=limit,
                                              start_cursor=cursor)
            if order_name:
              request.orderBy = order_name
            if descending:
              request.sortOrder = 'descending'
            log('Getting next batch (offset: %s)' % (total_len + offset))
            results, cursor, more = search_api.GetSearchKeys(self.key_kind,
                                                             request)
            all_results += results
            total_len += len(results)
          else:
            break
        log('Saving %s results...' % len(all_results))
        TrySetMemCache(mkey, all_results, self.cache_timeout)
        return all_results
      except (search.Error, apiproxy_errors.OverQuotaError):
        logging.exception('Search API error.')
        return []

    # At this point, we don't have any search so we can go directly to ndb
    # rather than using the Search index.
    return self.GetAllKeysForKind(order_name, descending, limit, offset, log)

  def GetAllKeysForKind(self, order_name, descending, limit, offset,
                        log=lambda x: 0):
    """Returns a list of possibly-sorted keys of self.kind.

    Args:
      order_name: str, name to order by (None for unordered).
      descending: bool, True if the order should be descending.
      limit: int, the maximum number of keys to return.
      offset: The number of results to skip.
      log: A logging function.

    Returns:
      A list of the keys of all rows of self.kind, sorted if order_name is given
          and it is possible to sort by that key.
    """
    request_cursor_key = self._GetQueryKeysCursorMkey(
        '', descending, order_name, offset)
    cached_cursor = memcache.get(request_cursor_key)

    skip_sorting = False
    if cached_cursor:
      if order_name:
        # Sometimes a sorted query will return no results because the index does
        # not exist. So when we see 0 results, we try an unsorted query. This
        # checks to see if we used the unsorted query on a previous call.
        skip_sorting = memcache.get(self._GetSkipSortKey(order_name))
      try:
        cached_cursor = datastore_query.Cursor(urlsafe=cached_cursor)
      except datastore_errors.BadValueError:
        cached_cursor = None

    query = self.model.query()
    if order_name and not skip_sorting:
      # This odd way of setting the sort order is used because the Model for an
      # unmanaged model has no fields other than those from common_models so
      # the normal way of adding an order will fail. This method bypasses the
      # check of the Model.
      order_op = datastore_query.PropertyOrder(
          order_name,
          datastore_query.PropertyOrder.DESCENDING if descending else
          datastore_query.PropertyOrder.ASCENDING)
      log('Using order op: %s' % order_op)
      query = query.order(order_op)

    keys, cursor, _ = _GetPage(query, limit, cached_cursor, offset)
    if order_name and not keys and not cached_cursor and not skip_sorting:
      # We tried an ordered search and got no results, so try it unordered.
      log('Ordered query returned no results (unindexed field %s); falling '
          'back to unordered.' % order_name)
      query = self.model.query()
      keys, cursor, _ = _GetPage(query, limit, cached_cursor, offset)
      if keys:
        # Found rows without sorting, so use the unsorted query in the future.
        TrySetMemCache(
            self._GetSkipSortKey(order_name), True, self.cache_timeout)

    if limit and cursor:
      # Save the cursor into the cache. We can reuse this if the next page is
      # requested to speed up the query.
      save_cursor_key = self._GetQueryKeysCursorMkey(
          '', descending, order_name, (offset or 0) + limit)
      TrySetMemCache(save_cursor_key, cursor.urlsafe(), self.cache_timeout)

    mkey = self._GetQueryKeysMkey('', limit, descending, order_name, offset)
    TrySetMemCache(mkey, keys, self.cache_timeout)
    return keys

  def GetRows(self, keys, columns, log):
    """Process and return the rows.

    Args:
      keys: list, the list if keys to get.
      columns: list, the columns to include.
      log: a callable to append to the log.
    Yields:
      Dict of fields for each row.
    """
    json_columns = None
    max_rpc = max(10, int(len(keys) / 20))
    index = -1
    for row in ndb.get_multi(keys, max_entity_groups_per_rpc=max_rpc):
      index += 1
      if not row:
        log('Got blank row at index %s (%s) - %s' % (index, keys[index], row))
      if row:
        # Only do this on the first row.
        if json_columns is None:
          json_columns = {}
          for column in columns:
            # pylint: disable=protected-access
            prop = row._properties.get(column)
            if isinstance(prop, model_utils.DHJsonProperty):
              json_columns[column] = prop._repeated
            # pylint: enable=protected-access

            # TODO(rupalig): Filter by read permissions.
        fields = row.to_dict(include=columns, exclude=json_columns.keys())

        # Add any JSON properties. They will be double encoded.
        for column, repeated in json_columns.iteritems():
          value = getattr(row, column)
          # There's a slight chance of variance in the stored rows.
          if repeated and isinstance(value, list):
            fields[column] = [json_utils.Dump(v) for v in value]
          else:
            fields[column] = None if value is None else json_utils.Dump(value)

        fields['key_kind'] = self.key_kind
        fields['key_name'] = row.key.id()
        yield fields


class OAuthCallbackOnePlatformView(webapp2.RequestHandler):
  """Renders the OAuth2 oneplatform callback view."""

  @webapp2.cached_property
  def _Jinja2(self):
    """Returns a Jinja2 renderer cached in the app registry."""
    return jinja2.get_jinja2(app=self.app)

  def _RenderResponse(self, template, **context):
    """Renders a template and writes the result to the response.

    Args:
      template: str, The template filename.
      **context: dict, Arguments used as variables to render the template.
    """
    rv = self._Jinja2.render_template(template, **context)
    self.response.write(rv)

  def get(self):
    """Returns a Jinja2 renderer cached in the app registry."""
    self._RenderResponse('oauth2callback_oneplatform.html')


class ImportAdditional(webapp2.RequestHandler):
  """Adding additional foreign keys after lookup."""

  def post(self, *unused_args, **unused_kwargs):  # pylint: disable=g-bad-name
    """Handler for POST requests."""
    entities_str = self.request.get('data')
    if entities_str:
      entities = entities_str.split(',')
      importer.UpdateEntities(entities, 100)


def _Hexdigest(key):
  """Return a hex digest for a long key string."""
  if isinstance(key, unicode):
    # hashlib.md5() should not be given Unicode strings.  Cf. b/28757110
    key = key.encode('utf_8')
  return hashlib.md5(key).hexdigest()
