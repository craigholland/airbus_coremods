"""Base class for business logic controllers in DH."""

import decimal
import logging
import time

import endpoints
from google.appengine.api import datastore_errors
from google.appengine.ext import ndb

from google3.ops.netdeploy.netdesign.server.common import common_validation
from google3.ops.netdeploy.netdesign.server.errors import error_msg
from google3.ops.netdeploy.netdesign.server.history import history_api
from google3.ops.netdeploy.netdesign.server.metadata import metadata_api
from google3.ops.netdeploy.netdesign.server.search import search_api
from google3.ops.netdeploy.netdesign.server.utils import constants
from google3.ops.netdeploy.netdesign.server.utils import conversion_utils
from google3.ops.netdeploy.netdesign.server.utils import dict_utils
from google3.ops.netdeploy.netdesign.server.utils import model_utils


OPS_UNKNOWN = 'Unknown'
OPS_INSERT = 'Insert'
OPS_UPDATE = 'Update'

AUTO_FIELDS = ('created_on', 'created_by', 'updated_on', 'updated_by')

DEFAULT_LIST_LIMIT = constants.LIST_DEFAULT_LIMIT


def AcceptDict(kind):
  """Decorator for entity-accepting controller methods to also accept dict.

  This is supposed to be temporary while we are in transition from controller
  methods that accept dictionaries (the "old" way) to methods that accept an
  entity (the "new" way). Using it allows existing tests to work.

  Args:
    kind: str: the model kind the controller method operates on.

  Returns:
    The decorated controller function, which now accepts either an entity or a
    dictionary.
  """
  def Decorated(controller_func):
    def Inner(self, entity, errors, **kwargs):
      if isinstance(entity, dict):
        try:
          entity = dict_utils.DictToModel(entity, kind)
        except (conversion_utils.ConversionError, ValueError) as e:
          entity = None
          errors.Add(None, '%s: %s' % (error_msg.MODEL_CONVERSION_FAIL, e))
      return controller_func(self, entity, errors, **kwargs)
    return Inner
  return Decorated


def AcceptKeyName(kind):
  """Decorator for entity-accepting controller methods to also accept key_name.

  This is supposed to be temporary while we are in transition from controller
  methods that accept key names (the "old" way) to methods that accept an
  entity (the "new" way). Using it allows existing tests to work.

  Args:
    kind: str: the model kind the controller method operates on.

  Returns:
    The decorated controller function, which now accepts either an entity or a
    key_name.
  """
  def Decorated(controller_func):
    def Inner(self, entity, errors, **kwargs):
      if isinstance(entity, basestring):
        model, key_name = model_utils.GetModel(kind), entity
        entity = Get(model, key_name)
        if not entity:
          errors.Add(key_name, error_msg.ENTITY_MISSING % (kind, key_name))
      return controller_func(self, entity, errors, **kwargs)
    return Inner
  return Decorated


@ndb.tasklet
def GetAsync(model, key_name, **kwargs):
  """Gets the model given key_name.

  Args:
    model: ndb.model, the model to query.
    key_name: str, the key_name.
    **kwargs: dict, optional parameters.

  Yields:
    entity to be fetched.
  """
  # When use_cache=True, then it was causing side effects in some parts of
  # code where common_controller.Get function was followed by controlller.Update
  # function, that was causing some functionality to fail. e.g. If the code
  # modifies the entity returned by Get function, then other code was using
  # in context cache to return entity rather than from datastore and it was
  # causing wrong data assertion. Making use_cache=False makes sure that
  # no such side effect is caused and performance of Get is also not affected as
  # permission validation code is removed in this cl/111376107. In fact there
  # is performance improvement in comparison with old code prior to this cl.
  kwargs.setdefault('use_cache', False)
  if key_name:
    entity = yield model.get_by_id_async(key_name, **kwargs)
  else:
    entity = None
  raise ndb.Return(entity)


def Get(model, key_name, **kwargs):
  return GetAsync(model, key_name, **kwargs).get_result()


@ndb.tasklet
def ListAsync(model, limit=DEFAULT_LIST_LIMIT, start_cursor=None, sort_by=None,
              q=None, filters=None):
  """Controller list method.

  Performs ndb fetch_page for requested model based on passed parameters.

  If query string q is passed, the search API will be leveraged instead
  of ndb fetch_page. Currently, it is not possible to apply both ndb filters
  and leverage the search API at the same time.

  Args:
    model: ndb.Model, model to query for.
    limit: int, maximum number of records to return.
    start_cursor: string, starting cursor.
    sort_by: string, name of field with '-' if descending.
    q: string, query string parameter for search api.
    filters: additional args, passed as filters.

  Yields:
    A tuple that consists of the list of ndb.Models, string cursor for
    next page request and true/false if there are more results.

  Raises:
    ValueError: missing model.
    BadQueryException: Thrown if failure to build or execute request occurs.
  """
  if not model:
    raise ValueError(error_msg.MODEL_NONE)
  kind = model._get_kind()  # pylint: disable=protected-access
  if q:
    try:
      search_request = search_api.BuildRequest(
          q, limit=limit, start_cursor=start_cursor)
      items, cursor, more = yield search_api.SearchGetEntitiesAsync(
          kind, search_request)
    except search_api.BadQueryException as bad_query:
      raise endpoints.BadRequestException(str(bad_query))
  else:
    items, cursor, more = yield model_utils.ReadAsync(
        model, limit=limit, start_cursor=start_cursor, sort_by=sort_by,
        filters=filters)
  raise ndb.Return((items, cursor, more))


def List(model, limit=DEFAULT_LIST_LIMIT, start_cursor=None, sort_by=None,
         q=None, filters=None):
  return ListAsync(model=model, limit=limit, start_cursor=start_cursor,
                   sort_by=sort_by, q=q, filters=filters).get_result()


def BatchGet(kind, key_names, errors):
  """Controller Batch Get method.

  Gets a batch of entities corresponding to the key_names provided. Returns None
  if one or more key_names do not exist.

  Args:
    kind: str, the kind name to query for.
    key_names: list<str>, a list of entity key_names.
    errors: error_collector.Errors, the errors object for BatchGet operation
      errors.
  Returns:
    A list of entities or None.
  """
  entities = ndb.get_multi([ndb.Key(kind, key_name) for key_name in key_names])

  # Checks the retrieved keys against the input keys list to find out which ones
  # don't exist.
  diff_keys = set(key_names) - set(e.key_name for e in entities if e)
  if diff_keys:
    errors.Add(None, (error_msg.ENTITIES_NOT_FOUND %
                      (', '.join(diff_keys), kind)))
    return None
  return entities


@ndb.tasklet
def DeleteAsync(model, key_name, errors):
  """Controller delete method, asynchronous version.

  Deletes model with specified key_name from ndb after validating that the
  entity is safe for deletion.

  Args:
    model: ndb.Model, model to search for key_name.
    key_name: str, key name of entity to delete.
    errors: error_collector, collects error.
  Raises:
    ValueError: missing model or key_name.
  Yields:
    Successfully deleted entity or None if validations failed.
  """
  if not model:
    raise ValueError(error_msg.MODEL_NONE)
  if not key_name:
    raise ValueError(error_msg.KEYNAME_NONE)

  entity = yield common_validation.ValidateEntityExistsAsync(
      model, key_name, errors)

  yield common_validation.ValidateDeleteAsync(entity, errors)

  if not errors:
    yield entity.key.delete_async()
    history_api.RecordDeletion(entity)

  raise ndb.Return(entity)


def Delete(model, key_name, errors):
  """Controller delete method.

  Deletes model with specified key_name from ndb after validating that the
  entity is safe for deletion.

  Args:
    model: ndb.Model, model to search for key_name.
    key_name: str, key name of entity to delete.
    errors: error_collector, collects error.
  Returns:
    Successfully deleted entity or None if validations failed.
  Raises:
    ValueError: missing model or key_name.
  """
  return DeleteAsync(model, key_name, errors).get_result()


@ndb.tasklet
def _PreCreateAsync(entity, errors):
  """Controller pre-create method, asynchronous version.

  Args:
    entity: ndb.Model, entity to insert.
    errors: error.Errors, aggregator used to collect
      any errors found during validation.
  Raises:
    ValueError: missing entity.
  Yields:
    The entity to be inserted.
  """
  if not entity:
    raise ValueError(error_msg.ENTITY_NONE)
  kind = entity._get_kind()  # pylint: disable=protected-access
  model = model_utils.GetModel(kind)

  if entity.key_name:
    existing_entity = yield model.get_by_id_async(entity.key_name)
    if existing_entity:
      errors.Add(
          constants.KEY_NAME,
          error_msg.DUPLICATE_KEYNAME % (kind, entity.key_name))
  # Performs common validations. This currently calls clean but ignores
  # any value changes.
  yield common_validation.CleanEntityAsync(entity, errors)
  if not errors:
    # Remove auto generated fields before put.
    for auto_field in AUTO_FIELDS:
      if hasattr(entity, auto_field):
        delattr(entity, auto_field)
  raise ndb.Return(entity)


@ndb.tasklet
def _PostCreateAsync(entity, errors, version_id=None):
  """Controller post-create method, asynchronous version.

  If version_id is set then this creates the regular object and also creates a
  PlannedChange to install it.

  Args:
    entity: ndb.Model, entity to insert.
    errors: error.Errors, aggregator used to collect
      any errors found during validation.
    version_id: str, version key_name for creating a planned change.
  Raises:
    The entity inserted or the PlannedChange entity if version_id is set.
  """
  if version_id and not errors:
    # After the original object has been added, add it as a version_id object.

    # Avoid circular import, pylint: disable=g-import-not-at-top
    from google3.ops.netdeploy.netdesign.server.plans import planning
    # pylint: enable=g-import-not-at-top

    # Have to work on a copy of entity because if you change it, then another
    # call to get the same key will return the changed object instead of the one
    # in the database.

    change = planning.CreateChange(entity, errors, version_key_name=version_id)
    # We return the PlannedChange entity rather than the created entity. This is
    # for consistency with Update which naturally returns the PlannedChange
    # entity since it does not touch the real entity at all.
    entity = change.Entity() if change else None
  raise ndb.Return(entity)


@ndb.tasklet
def CreateAsync(entity, errors, version_id=None):
  """Controller create method, asynchronous version.

  Performs ndb insert on entity passed via parameter after executing common,
  metadata-based validations.
  If version_id is set then this creates the regular object and also creates a
  PlannedChange to install it.

  Args:
    entity: ndb.Model, entity to insert.
    errors: error.Errors, aggregator used to collect
      any errors found during validation.
    version_id: str, version key_name for creating a planned change.
  Raises:
    ValueError: missing entity.
  Yields:
    The entity inserted or the PlannedChange entity if version_id is set.
  """
  yield _PreCreateAsync(entity, errors)
  if not errors:
    try:
      # pylint: disable=protected-access
      yield entity.put_async(
          backup_action='Insert', update_mvs=entity._meta.update_mvs)
    except (datastore_errors.BadValueError, ValueError) as e:
      errors.Add(None, str(e))
  yield _PostCreateAsync(entity, errors, version_id)
  raise ndb.Return(entity)


def Create(entity, errors, version_id=None):
  """Controller create method.

  Performs ndb insert on entity passed via parameter after executing common,
  metadata-based validations.

  Args:
    entity: ndb.Model, entity to insert.
    errors: error.Errors, aggregator used to collect
      any errors found during validation.
    version_id: str, version key_name for creating a planned change.
  Returns:
    The entity inserted.
  Raises:
    ValueError: missing entity.
  """
  return CreateAsync(entity, errors, version_id).get_result()


@ndb.tasklet
def BatchCreateAsync(entities, errors, version_id=None):
  """Controller batch create method, asynchronous version.

  Args:
    entities: list of ndb.Model, entities to insert.
    errors: error.Errors, aggregator used to collect
      any errors found during validation.
    version_id: str, version key_name for creating planned changes.
  Raises:
    ValueError: missing entity.
  Yields:
    The entities inserted or the PlannedChange entities if version_id is set.
  """
  if not entities:
    raise ValueError(error_msg.ENTITY_NONE)

  # Pre-processing.
  pre_ret_entities = []
  for entity in entities:
    pre_ret_entity = yield _PreCreateAsync(entity, errors)
    if errors:
      break
    pre_ret_entities.append(pre_ret_entity)

  # Body.
  if not errors:
    try:
      update_mvs = entities[0]._meta.update_mvs  # pylint: disable=protected-access
      yield ndb.put_multi_async(pre_ret_entities,
                                backup_action='Insert',
                                update_mvs=update_mvs)
    except (datastore_errors.BadValueError, ValueError) as e:
      errors.Add(None, str(e))

  # Post-processing.
  post_ret_entities = []
  if not errors:
    for entity in pre_ret_entities:
      post_ret_entity = yield _PostCreateAsync(entity, errors, version_id)
      if errors:
        break
      post_ret_entities.append(post_ret_entity)
  raise ndb.Return(post_ret_entities) if not errors else ndb.Return(None)


@ndb.tasklet
def UpdateAsync(entity, errors, update_description=None, version_id=None):
  """Controller update method, asynchronous version.

  Performs update on entity passed via parameter after patching and executing
  common, metadata-based validations.
  If version_id is set, then create a PlannedChange instead.

  Args:
    entity: ndb.Model, entity to update.
    errors: error.Errors, aggregator used to collect
      any errors found during validation.
    update_description: str, Update description for history API. Auto-generated
      if set to None.
    version_id: str, version key_name for creating a planned change.
  Raises:
    ValueError: missing entity.
  Yields:
    The entity updated or the PlannedChange entity if version_id is set,
    or None if there are errors.
  """
  if not entity:
    raise ValueError(error_msg.MODEL_NONE)
  yield common_validation.CleanEntityAsync(entity, errors)
  existing_entity = None
  # Ensure created_on and created_by are not changed.
  kind = entity._get_kind()  # pylint: disable=protected-access
  if entity.key_name is None:
    errors.Add(constants.KEY_NAME, error_msg.KEYNAME_MISSING % kind)
  else:
    existing_entity = yield entity.get_by_id_async(
        entity.key_name, use_cache=False, use_memcache=False)
    if existing_entity is None:
      errors.Add(
          constants.KEY_NAME,
          error_msg.ENTITY_MISSING % (kind, entity.key_name))
    else:
      entity.created_by = existing_entity.created_by
      entity.created_on = existing_entity.created_on
      entity.key_name = existing_entity.key_name

  # Check if the key version matches with the existing entity key version.
  # If not, raise the error.
  if existing_entity:
    existing_key_version = existing_entity.key_version
    new_key_version = getattr(entity, 'key_version', '')
    if existing_key_version != new_key_version:
      key_name = getattr(existing_entity, constants.KEY_NAME, '')
      errors.Add(kind, error_msg.KEY_VERSION_MISMATCH % key_name)

  if errors:
    raise ndb.Return(None)
  if not version_id:
    # Always generate new key_version on update if not a planned change.
    key_version = int(time.time())
    setattr(entity, 'key_version', key_version)
  try:
    if version_id:
      # Avoid circular import, pylint: disable=g-import-not-at-top
      from google3.ops.netdeploy.netdesign.server.plans import planning
      # pylint: enable=g-import-not-at-top
      change = planning.CreateChange(
          entity, errors, version_key_name=version_id)
      entity = change.Entity() if change else None
    else:
      if update_description is None:
        existing_dict = existing_entity.to_dict(exclude=AUTO_FIELDS)
        entity_dict = entity.to_dict(exclude=AUTO_FIELDS)
        modified_keys = sorted(dict_utils.DiffKeys(existing_dict, entity_dict))
        update_description = 'Modified: %s' % ', '.join(modified_keys)
      entity.put(backup_action='Update', backup_description=update_description,
                 update_mvs=entity._meta.update_mvs)  # pylint: disable=protected-access
  except (datastore_errors.BadValueError, ValueError) as e:
    errors.Add(None, str(e))
    entity = None
  raise ndb.Return(entity)


def Update(entity, errors, update_description=None, version_id=None):
  """Controller update method.

  Performs update on entity passed via parameter after patching and executing
  common, metadata-based validations.

  Args:
    entity: ndb.Model, entity to update.
    errors: error.Errors, aggregator used to collect
      any errors found during validation.
    update_description: str, update description for history API.
    version_id: str, version key_name for creating a planned change.
  Returns:
    The entity updated or None if there are errors.
  Raises:
    ValueError: missing entity.
  """
  return UpdateAsync(
      entity, errors, update_description, version_id).get_result()


class BaseController(object):
  """Base Controller.

    This is the base class for services controllers in Double Helix.
  """
  # Default page size for Read method.
  DEFAULT_READ_LIMIT = 100

  @property
  def _model_name(self):
    """Return the model/kind name."""
    return self.model._get_kind()  # pylint: disable=protected-access

  def _ValidateDecommission(self, entity_id, errors):
    """Validates if a entity can be decommissioned.

    This method will also test for dependent entities for the entity
    retrieved from the entity_id. For those dependent entities that have a
    physical_status field, a test will be performed to ensure that those
    entities are in a decommissioned state. An error will be generated for
    any dependent entities that are not in a decommissioned state.

    Args:
      entity_id: string, the entity id to be deleted.
      errors: error_collector.Errors, for collecting errors.

    Returns:
      common_model.BaseModel: The entity that was being validated.
    """
    entity = common_validation.ValidateEntityExists(
        self.model, entity_id, errors)
    common_validation.ValidateDecommissionAsync(entity, errors).get_result()
    return entity

  @classmethod
  def BuildEntity(cls, row, original_key_name=None, entity_model=None):
    """Map Function to build a materialized view entity.

    Args:
      row: dict, The row data.
      original_key_name: string, Original KEY_NAME of the entity.
      entity_model: common_model.BaseModel, The model to use for this
          entity.
    Returns:
      common.BazookaModel, Model for this row.
    """

    for key, value in row.iteritems():
      if isinstance(value, float) and value.is_integer():
        row[key] = int(value)
      if isinstance(value, decimal.Decimal):
        row[key] = float(value)
    if original_key_name:
      row['key_name'] = str(original_key_name)
      entity = entity_model(id=original_key_name, **row)
      entity.key_name = str(original_key_name)
    else:
      entity = entity_model(**row)
    return entity

  def _PreInsertValidations(self, entity, errors):
    """Checks the validation/business rules related to entities before insert.

    This method does nothing here and it's intended to be overridden
    by subclasses for implementing any entity specific function rules other than
    the metadata rules before the entity is actually inserted into datastore.
    The subclass version of this method may also do some transformations on the
    entity data.
    e.g. device entity function rules can be:
    1. The device depth can't exceed rack depth.
    2. device rmu is required for rack mounted devices.
    If this validation fails then the caller should not insert the entity
    into datastore. The subclass need not override this function if there
    aren't any pre-insert function rules.
    For triggering a failure, subclass should append a dict representing
    the error to the failed_list, so that the caller can check the
    failed_list to prevent the insert.

    Args:
      entity: dict, dict representing an entity.
      errors: Errors, for collecting errors.
    """
    self._InsertUpdatePreSaveValidations(entity, errors)

  def _PreUpdateValidations(self, entity, errors):
    """Checks the validation/business rules related to entities before update.

    This method does nothing here and it's intended to be overridden
    by subclasses for implementing any entity specific function rules other than
    the metadata rules before the entity is actually updated into datastore.
    The subclass need not override this function if there aren't any
    pre-update function rules.
    For triggering a failure, subclass should append a dict representing
    the error to the failed_list, so that the caller can check the
    failed_list to prevent the update.

    Args:
      entity: dict, dict representing an entity.
      errors: Errors, for collecting errors.
    """
    self._PreInsertValidations(entity, errors)

  def _PostSaveActions(self,
                       original_data,
                       inserted_data,
                       op_code=OPS_UNKNOWN):
    """Run optional tasks.

    This method should be implemented by subclasses.

    Args:
      original_data: dict, data to be inserted.
      inserted_data: common.BaseModel, inserted data.
      op_code: str, the type of operation that initiated the _PostSaveAction.
    """
    pass

  def _InsertUpdatePreSaveValidations(self, entity, errors):
    """Validate common operations on insert and update.

    This method should be implemented by sub classes.

    Args:
      entity: dict, The entity data from insert/update.
      errors: Errors, for collecting errors.
    """
    pass

  def _InsertUpdatePostSaveActions(self, entity, errors):
    """Actions to perform after saving the entity to datastore.

    This method should be implemented by sub classes.

    Args:
      entity: ndb.Model, The entity just saved.
      errors: Errors, for collecting errors.
    """
    pass

  def _CreateModel(self, entity_dict):
    """Creates the model from the supplied entity_dict.

    This method should be overridden by sub classes if necessary.

    Args:
      entity_dict: dict, the entity data from which the model should be created.

    Returns:
      Instance of self.model.
    """
    return self.model(**entity_dict)

  def Get(self, key_name, **kwargs):
    """Get an entity using the supplied key_name.

    Args:
      key_name: str, the entity key_name.
      **kwargs: dict, optional parameters for post get actions.

    Returns:
      common_models.BaseModel, The entity instance.
    """
    logging.debug('Executing get for %s: key_name=%s...',
                  self._model_name, key_name)
    entity = self.model.get_by_id(key_name)
    if entity:
      self._PostGetActions([entity], **kwargs)
    return entity

  def Insert2(self, entity, errors):
    """Performs the validation and insertion for a single entity.

    Args:
      entity: dict, dictionary of input values.
      errors: Errors, the errors object.

    Returns:
      inserted_entity: A dictionary representing the successfully inserted
      entity. None will be returned if there are any errors detected.
    """
    logging.debug('Executing common insert2 on %s ...', self._model_name)
    inserted_entity = None
    common_validation.Clean(entity, self._model_name, errors)

    if not errors:
      self._PreInsertValidations(entity, errors)
      if not errors:
        try:
          model_utils.MergeNotes(self.model, {}, entity)
          new_entity = self._CreateModel(entity)
          insert_result = new_entity.put(backup_action='Insert').id()
        except (datastore_errors.BadValueError, ValueError) as e:
          errors.Add(None, str(e))
          return None

        if insert_result:
          entity['key_name'] = insert_result
          inserted_entity = new_entity.to_dict()
          self._PostSaveActions(entity, new_entity, op_code=OPS_INSERT)

    return inserted_entity

  def Update2(self, entity, errors):
    """Performs the validation and update operation for a single entity."""

    logging.info('Executing update2 for %s...', self._model_name)
    updated_entity = None
    key_name = entity.get(constants.FK_KEY_NAME)
    if not key_name:
      errors.Add(
          constants.KEY_NAME, error_msg.KEYNAME_MISSING % self._model_name)

    # Do basic validations.

    if not errors:
      common_validation.Clean(entity, self._model_name, errors)

    if not errors:
      self._PreUpdateValidations(entity, errors)
      if errors:
        return None
      try:
        update_result = UpdateEntity(self.model, key_name, entity)
      except (datastore_errors.BadValueError, ValueError) as e:
        errors.Add(None, str(e))
        return None

      if update_result:
        entity_in_datastore = self.model.get_by_id(update_result)
        updated_entity = entity_in_datastore.to_dict()
        self._PostSaveActions(
            entity, entity_in_datastore, op_code=OPS_UPDATE)

    return updated_entity

  def _ExecuteUpdateToDataStore(self, entity):
    """Method to update an entity to backend data store.

    This helper method should only be used in special cases where it is
    necessary to bypass the usual validation involved entity updates.

    Args:
      entity: dict, entity to update.
    """
    update_result = UpdateEntity(self.model, entity[constants.KEY_NAME], entity)
    if update_result:
      entity_in_datastore = self.model.get_by_id(update_result)
      self._PostSaveActions(
          entity, entity_in_datastore, op_code=OPS_UPDATE)

  def _PostGetActions(self, entities, **kwargs):
    """Performs the post get actions on the entities.

    This method is for subclasses to override to perform any post get actions
    e.g excluding children from devices, this method may mutate the entities.
    It does nothing here.


    Args:
      entities: list<dict> The Devices.device entities.
      **kwargs: dict, filter string keys and their values.
    """

  def Read(
      self, limit=None, start_cursor=None, fields=None, sort_by=None, q=None,
      filters=None):
    """Executes the read operation for one or more entities.

    sort_by is the field to sort by, accompanied by the sort order. If the
    order is prefixed with a '-', then the order is sorted DESC, else
    it's sorted ASC.

    q and **kwargs query filters should be mutually exclusive. If q is passed,
    there should be no filters. If filters are passed, q should be None.

    Examples below:

      sort_by='-name'
      sort_by='description'

    Args:
      limit: int, maximum number of records per page.
      start_cursor: string, starting cursor.
      fields: list<string>, list of fields to return.
      sort_by: string, sort order.
      q: string, Query string for search api.
      filters: dict, Filter keys and their values.

    Returns:
      tuple, (list<Model> or list<dict>, string cursor, boolean more).
    """
    if limit is None:
      limit = self.DEFAULT_READ_LIMIT
    if filters is None:
      filters = {}
    cursor = more = None
    include_children = filters.pop('include_children', None)
    if q:
      try:
        search_request = search_api.BuildRequest(
            q, limit=limit, start_cursor=start_cursor)
        items, cursor, more = search_api.SearchGetEntities(
            self.model._get_kind(), search_request)  # pylint: disable=protected-access
      except search_api.BadQueryException as bad_query:
        raise endpoints.BadReqestException(str(bad_query))
    else:
      items, cursor, more = model_utils.Read(
          self.model, limit=limit, start_cursor=start_cursor, sort_by=sort_by,
          filters=filters)
    # TODO(gordonms): Deprecate detail and replace with fields.
    if fields:
      try:
        items = self.FilterToFields(items, fields)
      except AttributeError:
        items = []  # behavior expected by testReadNonExistentSingleField
    self._PostGetActions(items, include_children=include_children)
    return items, cursor, more

  def FilterToFields(self, entities, fields):
    """Return entities with some fields filtered out.

    Args:
      entities: list<entities>, list of entities.
      fields: list<string>, list of fields to use (not filter out).

    Returns:
      list<dict|entities>, filtered entities.
    """
    filtered_items = []
    for entity in entities:
      row = {'key_name': entity.key.id()}
      for field in fields:
        row[field] = getattr(entity, field)
      filtered_items.append(row)
    return filtered_items


def UpdateEntity(model, entity_id, properties_to_update):
  """Updates the record in Datastore.

  Args:
    model: BaseModel subclass, the model to update.
    entity_id: string, Identifier(key) of the entity.
    properties_to_update: dict, A dictionary of key and value pairs
        representing property names and its values to be updated.

  Returns:
    string, KEY_NAME if successful else None.
  """
  # TODO(bryany): Deprecate this method in favor of common controller update.
  e_key = None
  # Convert lat_long to GeoPt if they are provided as string.
  # A lat_long property name can be something like this: Building__lat_long.
  for key in properties_to_update:
    if 'lat_long' in key:
      if isinstance(properties_to_update[key], basestring):
        properties_to_update[key] = ndb.GeoPt(properties_to_update[key])
  entity = model.get_by_id(entity_id)
  if entity:
    exclude = metadata_api.GetFieldNames(entity, auto_add=True)
    exclude += metadata_api.GetFieldNames(entity, auto_update=True)
    existing_dict = entity.to_dict(exclude=exclude)
    # Copy the new property values from current model instance.
    for auto_field in AUTO_FIELDS:
      if properties_to_update.get(auto_field, None):
        properties_to_update.pop(auto_field)
    entity.populate(**properties_to_update)
    modified_keys = dict_utils.DiffKeys(existing_dict, properties_to_update)
    update_description = 'Modified: %s' % ', '.join(modified_keys)
    if not getattr(entity, 'key_version', ''):
      key_version = int(time.time())
      setattr(entity, 'key_version', key_version)
    e_key = entity.put(backup_action='Update',
                       backup_description=update_description)
  return e_key.id() if e_key else None
