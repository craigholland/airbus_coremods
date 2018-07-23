"""Custom mix-in classes and properties to be used in NDB models."""

import cPickle as pickle
import datetime
import decimal
import importlib
import logging
import re
import sys
import threading
import zlib

from google.appengine.api import datastore_errors
from google.appengine.datastore import datastore_query
from google.appengine.ext import ndb
from google.appengine.ext.ndb import model as ndb_model


from _base.errors import error_msg
from _base.utils import memoize
from _base.utils import user_utils
from _base.utils import constants
from _base.utils import conversion_utils
from _base.utils import json_utils


_KIND_MAP_LOCK = threading.RLock()
_JSON_NONE = json_utils.Dump(None)
_JSON_MAX_RAW_BYTES = 1024 * 1024 // 2  # Half a MB.
_PICKLE_NONE = pickle.dumps(None, pickle.HIGHEST_PROTOCOL)
_PICKLE_STOP = '.'
_ZLIB_HEADERS = ('x\x01', 'x\x9c', 'x\xda')

_ASC = datastore_query.PropertyOrder.ASCENDING
_DESC = datastore_query.PropertyOrder.DESCENDING
_SORT_SYMBOL = '-'

# The range [!-~] includes all printable ASCII characters other than space. The
# range ["-~] is the same range but without '!'. So the following regexp matches
# a string of printable ASCII characters that does not begin with '!'.
_KEY_NAME_MATCH = re.compile('["-~][!-~]*$')
_KEY_NAME_NOMATCH = re.compile('__.*__$')


MIN_KEY_LENGTH = 8
MAX_KEY_LENGTH = 500


def BadKeyName(key_name):
  """Check if key_name is allowable as a model key name.

  Args:
    key_name: string, the name to check.

  Returns:
    False if the key_name is OK, otherwise an error message.
  """
  # We want all models to potentially be added to a search index using key_name
  # as the doc_id, so this check ensures that the key_name is a valid doc_id.
  n = len(key_name)
  if n < MIN_KEY_LENGTH or n > MAX_KEY_LENGTH:
    return 'key_name must be between %s and %s characters' % (
        MIN_KEY_LENGTH, MAX_KEY_LENGTH)
  if not _KEY_NAME_MATCH.match(key_name):
    return ('key_name must have only non-space printable ASCII and must not'
            ' begin with "!"')
  if _KEY_NAME_NOMATCH.match(key_name):
    return 'key_name must not begin and end with double underscore, "__"'
  return False


def IsEntity(entity):
  """Test if a an object is an entity."""
  return isinstance(entity, ndb.Model)


def GetSubclass(cls, name):
  """Return a dynamically named subclass of a model.

  Even though NDB lets you dynamically reference a model with
  ndb.Key('MyModel', 'key'), it still expects there to be a subclass
  with that name in memory.

  Subclasses are cached so that we only have a single one in memory.

  Args:
    cls: ndb.Model subclass, the model to subclass.
    name: string, a name for the model subclass.

  Returns:
    A subclass of the provided model.
  """
  # Prior to creating dynamic subclasses, snapshot all managed classes.
  GetManagedModels()

  # Make sure global kind map updates are thread-safe.
  assert issubclass(cls, ndb.Model), '%r is not a model' % cls
  with _KIND_MAP_LOCK:
    kind_map = ndb.Model._kind_map  # pylint: disable=protected-access
    subclass = kind_map.get(name)
    if not subclass:
      metaclass = type(cls)
      subclass = metaclass(str(name), (cls,), dict(__module__=__name__))
  return subclass


def _ImportModels():
  """Make sure all modules that define NDB models are imported."""
  _ImportModels.done = True
  for module in constants.MODEL_MODULES:
    importlib.import_module(module, package=constants.BASE_MODULE)
_ImportModels.done = False


@memoize.Memoize(warn_on_error=False, memoize_parallel_calls=True)
def GetManagedModels():
  """Returns the set of managed models.

  Maintains a frozenset of models available after a new instance have been
  started and models have been imported.

  Returns:
    A frozenset of kind names.
  """
  # Import packages if not imported.
  if not _ImportModels.done:
    _ImportModels()
  return frozenset(ndb.Model._kind_map)  # pylint: disable=protected-access


def IsModel(kind):
  """Is the specified kind known to ndb."""
  if not _ImportModels.done:
    _ImportModels()
  return kind in ndb.Model._kind_map.keys()  # pylint: disable=protected-access


def GetModel(name, base_kind='BaseModel'):
  """Get a model class by name.

  This function searches all modules in this package to find the named Model.
  If a model by that name doesn't exist it will return a BaseModel. This
  is used to allow dynamic model creation in appengine.

  Args:
    name: string, the name of the model class.
    base_kind: string, the base model to use when creating a new subclass.
  Returns:
    The model class or a dynamic subclass of BaseModel.
  Raises:
    KeyError: if, for some reason, BaseModel hasn't been imported.
  """
  if not _ImportModels.done:
    _ImportModels()

  kind_map = ndb.Model._kind_map  # pylint: disable=protected-access
  model = kind_map.get(name) or GetSubclass(kind_map[base_kind], name)
  # Make sure model metadata is already loaded to prevent recursion errors.
  getattr(model, '_meta', None)
  return model


def MakePropertyNameConstants(cls):
  """Generates module-level constants from the properties of a ndb model.

  When applied to a ndb.Model, creates constants in the same module as the
  model, with names being the uppercase property name, and the value being the
  property name as a string.

  This will silently overwrite existing module-level constants with the same
  name, so use with caution in modules that define such constants.

  Args:
    cls: ndb.Model subclass to decorate.

  Returns:
    The class, unmodified.
  """
  mod = sys.modules[cls.__module__]
  for name in cls._properties:  # pylint: disable=protected-access
    setattr(mod, name.upper(), name)
  return cls


@ndb.tasklet
def ReadAsync(model, limit=constants.LIST_MAX_LIMIT, start_cursor=None,
              sort_by=None, filters=None):
  """Reads the data for given entity.

  It's the subclass calling method that has responsibility for determining
  which parameter to pass for the equality operator.

  Example:
    result, cursor, more = Read(
        TestModel, limit=10, name='name_1', boolean_property=True)

  Args:
    model: class, the model to read.
    limit: int, maximum number of records per page.
    start_cursor: string, starting cursor.
    sort_by: string, sort order.
    filters: dict, Filter keys and their value.

  Yields:
    tuple, (list<Model>, string cursor, boolean more).
  """
  if start_cursor:
    start_cursor = datastore_query.Cursor(urlsafe=start_cursor)
  if limit is None:
    limit = constants.LIST_MAX_LIMIT

  query = _CreateQueryForModel(model)
  query = _AddQueryFilters(model, query, filters)
  query = _AddQuerySort(query, sort_by)

  entities, cursor, more = yield query.fetch_page_async(
      limit, start_cursor=start_cursor)
  if cursor:
    cursor = cursor.urlsafe()
  raise ndb.Return((entities, cursor, more))


def Read(model, limit=constants.LIST_MAX_LIMIT, start_cursor=None,
         sort_by=None, filters=None):
  return ReadAsync(model, limit=limit, start_cursor=start_cursor,
                   sort_by=sort_by, filters=filters).get_result()


@ndb.tasklet
def CountAsync(model, limit=None, filters=None):
  """Returns the count of entities matching the query filters.

  Example:
    count = Count(TestModel, name='name_1', boolean_property=True)

  Args:
    model: class, The model to read.
    limit: int, Maximum number of results to count.
    filters: dict, Filter keys and their value.

  Yields:
    int, Count of entities matching the criteria.
  """
  query = _CreateQueryForModel(model)
  query = _AddQueryFilters(model, query, filters)
  count = yield query.count_async(limit=limit)
  raise ndb.Return(count)


def Count(model, limit=None, filters=None):
  return CountAsync(model, limit=limit, filters=filters).get_result()


@ndb.tasklet
def ExistsAsync(model, filters=None):
  """Determines if any entity matches the query filters.

  Example:
    exists = Exists(TestModel, name='name_1', boolean_property=True)

  Args:
    model: class, The model to read.
    filters: dict, Filter keys and their value.

  Yields:
    boolean, True if at least one matching entity exists, False otherwise.
  """
  count = yield CountAsync(model, limit=1, filters=filters)
  raise ndb.Return(bool(count))


def Exists(model, filters=None):
  return ExistsAsync(model, filters=filters).get_result()


def _CreateQueryForModel(model):
  """Creates a NDB query for a model.

  Args:
    model: ndb.Model subclass, the model to read.

  Returns:
    query, A new query instance.
  """
  # Make sure model metadata is already loaded to prevent recursion errors.
  getattr(model, '_meta', None)
  return model.query()


def _AddQueryFilters(model, query, filters=None):
  """Adds query filters to a NDB query.

  Args:
    model: class, The model to read.
    query: ndb.Query, the query instance.
    filters: dict, filters to be applied to the query.

  Returns:
    query, A new query instance with filters applied.
  """
  if filters is None:
    filters = {}
  for key, value in filters.iteritems():
    if isinstance(value, (list, set, tuple)):
      if len(value) == 1:
        query = query.filter(ndb.FilterNode(key, '=', list(value)[0]))
      elif value:
        query = query.filter(ndb.FilterNode(key, 'in', value)).order(model.key)
    else:
      query = query.filter(ndb.FilterNode(key, '=', value))
  return query


def _AddQuerySort(query, sort_by):
  """Adds query sorts to a NDB query.

  Args:
    query: ndb.Query, the query instance.
    sort_by: str, sort operations to be applied to the query.

  Returns:
    query, A new query instance with sort applied.
  """
  if sort_by:
    # Set order by field.
    if sort_by[0] == _SORT_SYMBOL:
      order_op = datastore_query.PropertyOrder(sort_by[1:], _DESC)
    else:
      order_op = datastore_query.PropertyOrder(sort_by, _ASC)
    query = query.order(order_op)
  return query


class DHJsonProperty(ndb.TextProperty):
  """Custom JsonProperty.

  Handles broken compressed, None, and pickled values. It also automatically
  compresses values that are too large.
  """

  def _to_base_type(self, value):
    return json_utils.Dump(value)

  def _from_base_type(self, value):
    try:
      return json_utils.Load(value)
    except ValueError as err:
      # Handle loading of legacy pickle data while transitioning to json.
      if value.endswith(_PICKLE_STOP):
        return pickle.loads(str(value))
      if err.message == error_msg.JSON_DECODE_FAIL:
        # No valid JSON to return.
        logging.error(error_msg.JSON_PARSE_FAIL, value)
        return None
      raise
    except TypeError:
      # No valid JSON to return.
      logging.error(error_msg.JSON_PARSE_FAIL, value)
      return None

  def _get_base_value_unwrapped_as_list(self, entity):
    """Overridden to handle automatic compression."""
    values = super(DHJsonProperty, self)._get_base_value_unwrapped_as_list(
        entity)
    if not self._compressed and sum(
        len(v) for v in values if isinstance(v, str)) > _JSON_MAX_RAW_BYTES:
      for i, val in enumerate(values):
        if val:
          # pylint: disable=protected-access
          values[i] = ndb_model._CompressedValue(zlib.compress(val))
          # pylint: enable=protected-access
    return values

  def _get_user_value(self, entity):
    """Overridden to handle repeated None values."""
    value = super(DHJsonProperty, self)._get_user_value(entity)
    # Default JsonProperty lets you store None as a repeated property value,
    # but fails to decode it when reading.
    if self._repeated:
      for i, val in enumerate(value):
        if isinstance(val, unicode):
          val = val.encode('utf8')
        if val in (_JSON_NONE, _PICKLE_NONE):
          value[i] = None
    return value

  def _db_get_value(self, v, p):
    """Overridden to handle corrupted compressed values."""
    value = super(DHJsonProperty, self)._db_get_value(v, p)
    # Restoring from backup loses compression information, so headers are
    # checked for magic values.
    if isinstance(value, basestring) and value[:2] in _ZLIB_HEADERS:
      return ndb_model._CompressedValue(value)  # pylint: disable=protected-access
    return value


class DHLocalStructuredProperty(ndb.LocalStructuredProperty):
  """Custom LocalStructuredProperty.

  Handles broken compressed values.
  """

  def _db_get_value(self, v, p):
    """Overridden to handle corrupted compressed values."""
    value = super(DHLocalStructuredProperty, self)._db_get_value(v, p)
    # Restoring from backup loses compression information, so headers are
    # checked for magic values.
    if isinstance(value, basestring) and value[:2] in _ZLIB_HEADERS:
      return ndb_model._CompressedValue(value)  # pylint: disable=protected-access
    return value


# TODO(davbennett): Move this to a better location that won't cause a circular
# import.
class Note(ndb.Model):
  """Note model used as StructuredProperty.

  The Note model is a class to be used as a StructuredProperty in other data
  models that require a time and user-stamped note (comment).
  """
  user = ndb.StringProperty()
  date = ndb.DateTimeProperty(auto_now_add=True)
  text = ndb.TextProperty()


class DHNoteProperty(ndb.LocalStructuredProperty):
  """Custom LocalStructuredProperty for storing notes."""

  def __init__(self, *args, **kwargs):
    super(DHNoteProperty, self).__init__(Note, *args, **kwargs)


def MergeNotes(model, from_dict, to_dict):
  """Updates an entity dictionary with note properties of another dictionary.

  Note properties are combined so that new notes are appended to the list of
  existing notes.

  Args:
    model: ndb.Model instance the dictionaries represent.
    from_dict: the dictionary representing the existing entity state.
    to_dict: the dictionary representing the new entity state.
  """
  date_prop_name = Note.date._name  # pylint: disable=protected-access
  user_prop_name = Note.user._name  # pylint: disable=protected-access
  all_notes = []
  now = datetime.datetime.now()

  for prop_name in to_dict:
    prop = model._properties.get(prop_name)  # pylint: disable=protected-access
    if isinstance(prop, DHNoteProperty):
      all_notes = from_dict.get(prop_name, []) + to_dict.get(prop_name, [])

      # Ensures duplicate notes are removed, and notes sorted by timestamp.
      unique_notes = [dict(t)
                      for t in set(tuple(dict(n).items())
                                   for n in all_notes)]
      unique_notes.sort(  # Sorts by timestamp first, then original order.
          key=lambda d: (d.get(date_prop_name) or now, all_notes.index(d)))

      # Notes list may contain existing notes. New notes are differentiated
      # by the absence of a timestamp (date property), which will be set when
      # the note is persisted to datastore. User must be set manually.
      for note in unique_notes:
        if not note.get(date_prop_name):
          note[user_prop_name] = user_utils.GetCurrentUserLdap()

      to_dict[prop_name] = unique_notes


def _ReplaceKeyName(key, key_name):
  """Creates a new Key by replacing the key_name."""
  if not key:
    return None
  return ndb.Key(key.kind(), key_name, namespace=key.namespace(), app=key.app())


class DHKeyNameProperty(ndb.Property):
  """Custom property for accessing an entity's key_name."""

  def _set_value(self, entity, value):
    """Replaces the key_name on existing key, otherwise creates a new one."""
    entity.key = _ReplaceKeyName(entity.key, value) or ndb.Key(
        entity._get_kind(), value)  # pylint: disable=protected-access

  def _delete_value(self, entity):
    """Replaces the key_name on existing key with None, otherwise clears it."""
    entity.key = _ReplaceKeyName(entity.key, None)

  def _get_value(self, entity):
    """Returns the key_name of existing key, otherwise None."""
    key = entity.key
    return key.string_id() if key else None

  def _db_set_value(self, unused_v, unused_p, unused_value):
    pass

  def _db_get_value(self, unused_v, unused_p):
    pass


class DHDateProperty(ndb.DateProperty):
  """A DateProperty that accepts any value that can be converted to a date."""

  def _validate(self, value):
    """Validates the given value and converts to a datetime.date object.

    Args:
      value: the value to validate.

    Raises:
      datastore_errors.BadValueError, if the value cannot be converted to a
      date.

    Returns:
      datetime.date, the value as a date object.
    """
    try:
      return conversion_utils.ToDate(value)
    except conversion_utils.ConversionError as e:
      field_name = (self._verbose_name if self._verbose_name else self._name)
      message = 'Field %r failed: %s' % (field_name, e.message)
      e.message = message
      e.args = (message,)
      raise datastore_errors.BadValueError(e)


class DHLDAPProperty(ndb.StringProperty):
  """A LDAP property that accepts any value that is a valid ldap."""
  pass


class DHCurrencyProperty(ndb.StringProperty):
  """A currency property that stores exactly two decimal places."""

  def _Clean(self, value):
    return conversion_utils.ToCurrency(value, default=value)

  def _validate(self, value):
    try:
      decimal.Decimal(value)
    except (TypeError, decimal.InvalidOperation):
      raise TypeError('Invalid decimal value: %s' % value)

  def _set_value(self, entity, value):
    super(DHCurrencyProperty, self)._set_value(entity, self._Clean(value))


class DHComputedCurrencyProperty(ndb.ComputedProperty):
  """A computed currency property that stores exactly two decimal places."""

  def _Clean(self, value):
    return conversion_utils.ToCurrency(value, default=value)

  def _validate(self, value):
    try:
      decimal.Decimal(value)
    except (TypeError, decimal.InvalidOperation):
      raise TypeError('Invalid decimal value: %s' % value)

  def _get_value(self, entity):
    value = super(DHComputedCurrencyProperty, self)._get_value(entity)
    return self._Clean(value)


class DHConditionalComputedProperty(ndb.ComputedProperty):
  """ComputedProperty that computes a value only if some condition is satisfied.

  This property adds a `condition` parameter which should be a function that
  accepts the current entity and returns a boolean. If it returns True, the
  computation is performed and saved to the datastore. If False, the computation
  is not performed, and the existing value is returned. The default behavior (no
  condition function given), is identical to ComputedProperty (i.e. the
  computation is always performed).

  Usage:
      my_prop = DHConditionalComputedProperty(
                    _SomeComputationFunction,
                    condition=lambda self: self.do_computation)
  """

  def __init__(self, func, name=None, indexed=None,
               repeated=None, verbose_name=None, condition=None):
    super(DHConditionalComputedProperty, self).__init__(
        func, name=name, indexed=indexed, repeated=repeated,
        verbose_name=verbose_name)

    if condition is None:
      self._condition = lambda _: True
    else:
      self._condition = condition

  def _get_value(self, entity):
    if self._condition(entity):
      return super(DHConditionalComputedProperty, self)._get_value(entity)
    else:
      # Bypasses the computation be calling the grandparent (GenericProperty)
      # _get_value method.
      return super(ndb.ComputedProperty, self)._get_value(entity)


class DHUpdateRestrictionComputedProperty(ndb.ComputedProperty):
  """ComputedProperty used to declare field update restrictions.

  This property adds a 'update_restrictions' property to field definitions in
  ndb.Model YAML metadata files.

  Usage:
    - name: current_commit_date
      property_type: DATE ...
      update_restrictions:
      - criteria:
        - field: order_status
          values:
          - ApprovedForPartialShipping
          - Hold
          groups:
          - doublehelix-supplychain
          - doublehelix-supplychain-planner-tvcs
        - field: order_status
          changes:
          - value: Received
          - to: Canceled
          - value: Hold
          - to: Shipped
          groups:
          - doublehelix-supplychain
  """

  def __init__(self, func, name=None, indexed=None,
               repeated=None, verbose_name=None, update_restriction=None):
    super(DHUpdateRestrictionComputedProperty, self).__init__(
        func, name=name, indexed=indexed, repeated=repeated,
        verbose_name=verbose_name)

    if update_restriction is None:
      self._update_restriction = lambda _: True
    else:
      self._update_restriction = update_restriction

  def _get_value(self, entity):
    if self._update_restriction(entity):
      return super(DHUpdateRestrictionComputedProperty, self)._get_value(entity)
    else:
      return super(ndb.ComputedProperty, self)._get_value(entity)


def DisplayName(entity):
  """Return the display_name for an entity.

  Args:
    entity: the entity for which to make a display_name.

  Returns:
    string, the display_name for the entity.
  """
  display_name = getattr(entity, 'fk_display', None)
  if display_name is None:
    display_name = getattr(entity, 'name', None)
  if display_name is None:
    display_name = entity.key.id()
  return display_name


def CopyEntity(entity, props_to_omit=()):
  """Creates a copy of an entity.

  Args:
    entity: ndb.Model, the entity to copy.
    props_to_omit: sequence of property names to omit from copying.

  Returns:
    A new entity.
  """
  cls = entity.__class__
  props = {}
  # pylint: disable=protected-access
  # pylint: disable=unidiomatic-typecheck
  for name, prop in cls._properties.iteritems():
    if name not in props_to_omit and type(prop) is not ndb.ComputedProperty:
      props[prop._code_name] = prop.__get__(entity, cls)
  # pylint: enable=protected-access
  # pylint: enable=unidiomatic-typecheck
  return cls(**props)


@ndb.tasklet
def FetchKeysAsync(model, field_name, value, errors,
                   limit=constants.LIST_MAX_LIMIT):
  """Gets a list of entity keys that has the field_name = value.

  Args:
    model: class, the model to query.
    field_name: string, model field name.
    value: object, expected field value.
    errors: error_collector.Errors, for collecting errors during validation.
    limit: int, the number of keys.

  Yields:
    list of Keys, or None with errors.
  """
  query = model.query().filter(ndb.FilterNode(field_name, '=', value))
  keys = yield query.fetch_async(keys_only=True, limit=limit)

  if keys:
    raise ndb.Return(keys)
  else:
    kind = model._get_kind()  # pylint: disable=protected-access
    errors.Add(kind, error_msg.ENTITY_MISSING % (field_name, value))
    raise ndb.Return(None)


@ndb.tasklet
def GetKeyAsync(model, field_name, value, errors):
  """Gets an entity key that has the field_name of value.

  Args:
    model: class, the model to query.
    field_name: string, model field name.
    value: object, expected field value.
    errors: error_collector.Errors, for collecting errors during validation.

  Yields:
    Key, or None with errors.
  """
  keys = yield FetchKeysAsync(model, field_name, value, errors, limit=1)
  if keys:
    raise ndb.Return(keys[0])


def ListSubNodes(node, types=None, with_parent=False):
  """Generator to list sub nodes of a Device or Part.

  Searches through ports, slots and cards for subnodes of mathing types.  For
  example, if types is equal to ['cards'], all cards will be returned at any
  nested level.  If with_parent is True, a tuple will be returned containing
  the parent node along with the matching node.

  Args:
    node: dict, Device or Part data containing ports and slots.
    types: list<string>, list of types to match within SUB_NODE_TYPES.
    with_parent: bool, if True return the node and parent else return the node.

  Yields:
    subnode or tuple(parent, subnode), returns all nodes of the provided types.
  """
  types = types if types else constants.SUB_NODE_TYPES
  for node_type in constants.SUB_NODE_TYPES:
    try:
      for child in node.get(node_type, []):
        if node_type in types:
          yield (node, child) if with_parent else child
        for nested in ListSubNodes(child, types, with_parent=with_parent):
          yield nested
    except TypeError:
      # Contains any errors due to invalid device/part json.
      pass


def FindSubNodes(node, types=None, with_parent=False, **filters):
  """Generator to list sub nodes of a Device or Part filtered by kwargs.

  Searches through ports, slots and cards for subnodes of mathing types. For
  each matching subnode return only nodes that match the filters specified. If
  with_parent is True, a tuple will be returned containing the parent node
  along with the matching node.

  Args:
    node: dict, Device or Part data containing ports and slots.
    types: list<string>, list of types to match within SUB_NODE_TYPES.
    with_parent: bool, if True return the node and parent else return the node.
    **filters: dict, key values used to filter results.

  Yields:
    subnode or tuple(parent, subnode), returns all nodes of the provided types
    that match the filters.
  """
  for subnode in ListSubNodes(node, types, with_parent=with_parent):
    child = subnode[1] if with_parent else subnode
    if filters:
      if filters.viewitems() <= child.viewitems():
        yield subnode
    else:
      yield subnode
