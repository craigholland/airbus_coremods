"""Metadata API for Double Helix app."""

import logging
import threading

from google.appengine.ext import ndb

from google3.pyglib.function_utils import memoize

from google3.ops.netdeploy.netdesign.server.metadata import metadata_conditional
from google3.ops.netdeploy.netdesign.server.metadata import metadata_conversions
from google3.ops.netdeploy.netdesign.server.metadata import metadata_messages
from google3.ops.netdeploy.netdesign.server.metadata import metadata_models
from google3.ops.netdeploy.netdesign.server.metadata import metadata_utils
from google3.ops.netdeploy.netdesign.server.utils import constants
from google3.ops.netdeploy.netdesign.server.utils import model_utils

# Kinds that represent virtual base classes and should not be instantiated.
BASE_CLASS_KINDS = frozenset([
    'BaseModel',
    'BigQueryBaseRow',
    'CapacityModel',
    'MetadataMetaModel'
])


def ApplyModelDefinedMetadata(kind, metadata):
  """Apply model-defined metadata to a metadata instance.

  If there is conflict between metadata and properties defined in
  the model, the model always wins. This function takes a metadata
  object and applies the model-defined properties.

  Args:
    kind: str, the kind of the metadata.
    metadata: metadata_messages.Metadata, the metadata to modify.
  Returns:
    metadata: metadata_messages.Metadata, the model-defined metadata.
  """
  if not kind:
    return None

  # Get metadata defaults.
  # TODO(davbennett): Is there really a chance that a model exists but hasn't
  # been imported yet (maybe on warmup)? If so, maybe we could save a hint in
  # the datastore of where to find it (model.__module__).
  cls = metadata_models.METADATA_KIND_MAP.get(kind)
  if metadata or cls:
    if metadata is None:
      # A model might be defined in code but not have anything in datastore.
      metadata = metadata_messages.Metadata(kind=kind)
    else:
      # TODO(davbennett): Remove this once datastore has been updated.
      metadata_utils.FixRenamedFields(metadata)
    if cls is None:
      # Always include base metadata even if a class isn't defined.
      cls = metadata_models.MetadataModel
    # Meta class metadata is applied in reverse Method Resolution Order.
    for base_cls in reversed(cls.mro()):
      if isinstance(base_cls, metadata_models.MetadataMetaModel):
        base_kind = base_cls._get_kind()  # pylint: disable=protected-access
        defaults = metadata_models.METADATA_DEFAULTS.get(base_kind)
        if defaults:
          metadata_utils.UpdateMetadata(metadata, defaults)
    # Model properties override everything. It doesn't make sense for a model
    # to have inconsistent properties Meta vs. the class properties, so this
    # should not override anything in Meta. metadata.consistency_test checks
    # for this.
    properties = cls._properties  # pylint: disable=protected-access
    fields = metadata_utils.GetModelDefaults(properties)
    if fields:
      metadata_utils.UpdateMetadata(metadata, {'fields': fields})
    # Is_managed cannot be modified.
    is_managed = kind in model_utils.GetManagedModels()
    metadata_utils.UpdateMetadata(metadata, {'is_managed': is_managed})
  return metadata


@ndb.tasklet
def GetKindsAsync():
  """Returns a list of kinds that have metadata."""
  query = metadata_models.Metadata.query()
  keys = yield query.fetch_async(keys_only=True, batch_size=1000)
  kinds = set(metadata_models.METADATA_KIND_MAP) - BASE_CLASS_KINDS
  kinds.update(k.string_id() for k in keys)
  raise ndb.Return(sorted(filter(None, kinds)))


def GetMetadata(kind):
  """Returns metadata loaded from datastore with defaults applied.

  Note: Defaults might not be applied if the corresponding model hasn't been
  imported yet. This will not include any thread-local changes. Use model._meta
  for that instead.

  Args:
    kind: str, the model kind.

  Returns:
    metadata_messages.Metadata instance or None if not found.
  """
  # Get metadata from the datastore in a separate thread.
  result = []
  target = lambda: result.append(metadata_models.Metadata.get_by_id(kind))
  thread = threading.Thread(target=target)
  thread.start()
  thread.join()
  if result:
    entity = result[0]
  else:
    logging.error('Threading error retrieving metadata for %r.', kind)
    entity = None
  metadata = entity.metadata if entity else None
  return ApplyModelDefinedMetadata(kind, metadata)


def GetFieldNames(obj, **filters):
  """Returns the field names of a MetadataModel subclass or entity.

  Args:
    obj: MetadataModel subclass or entity to be queried.
    **filters: metadata setting values to filter on.

  Returns:
    tuple, the field names that match the given filters.
  """
  metadata = getattr(obj, '_meta', None)
  if not metadata:
    return ()
  fields = {f.name: f for f in metadata.fields}
  for key, value in filters.iteritems():
    for name, field in fields.items():
      if getattr(field, key) != value:
        del fields[name]
  sorted_fields = sorted(fields.values(), key=lambda f: f.display_order)
  return tuple([field.name for field in sorted_fields])


def GetParentKind(obj):
  """Returns a metadata-defined parent kind.

  Args:
    obj: MetadataModel subclass or instance.

  Returns:
    parent kind or None if the parent kind is not defined in metadata.
  """
  metadata = getattr(obj, '_meta', None)
  if metadata and metadata.parent:
    return metadata.parent.kind
  else:
    return None


def GetParentKeyField(obj):
  """Returns a metadata-defined parent key field.

  Args:
    obj: MetadataModel subclass or instance.

  Returns:
    parent key_field or None if the parent is not defined in metadata.
  """
  metadata = getattr(obj, '_meta', None)
  if metadata and metadata.parent:
    if metadata.parent.key_field:
      return metadata.parent.key_field
    else:
      return metadata.parent.kind + constants.FK_SEP + constants.FK_KEY_NAME
  else:
    return None


@memoize.Memoize(warn_on_error=False, timeout=600, cache_positions=[0])
def GetMetadataDefaultValuesCached(kind, metadata=None):
  """Returns the field default values for a metadata kind.

  Args:
    kind: str, the model kind.
    metadata: metadata_messages.Metadata instance.

  Returns:
    dict, containing metadata-defined field names with coerced default values.
  """
  metadata = metadata if metadata else GetMetadata(kind)
  if metadata and metadata.fields:
    return metadata_conversions.GetMetadataDefaultValues(metadata.fields)
  else:
    return None


def ApplyMetadataDefaultValues(metadata, model_dict):
  """Updates a model_dict with metadata default values for unset properties.

  Args:
    metadata: metadata_messages.Metadata instance.
    model_dict: dict, the model key, value pairs to process.
  """
  if not metadata:
    return None
  coerced_defaults = GetMetadataDefaultValuesCached(metadata.kind, metadata)
  if coerced_defaults:
    for field_name in coerced_defaults:
      if model_dict.get(field_name) is None:
        model_dict[field_name] = coerced_defaults[field_name]


def ApplyMetadataDefaultValuesToEntity(metadata, entity):
  """Updates a model with metadata default values for unset properties.

  Args:
    metadata: metadata_messages.Metadata instance.
    entity: ndb.Model, entitiy to apply default values to.
  """
  if not metadata:
    return None
  coerced_defaults = GetMetadataDefaultValuesCached(metadata.kind, metadata)
  if coerced_defaults:
    for field_name in coerced_defaults:
      if getattr(entity, field_name, None) is None:
        setattr(entity, field_name, coerced_defaults[field_name])


@memoize.Memoize(warn_on_error=False, timeout=600, cache_positions=[0])
def GetIndexedFieldsCached(kind, metadata=None):
  """Returns the fields that are indexed for a metadata kind.

  Args:
    kind: str, the model kind.
    metadata: metadata_messages.Metadata instance.

  Returns:
    set, containing metadata-defined indexed field names.
  """
  metadata = metadata if metadata else GetMetadata(kind)
  if metadata and metadata.fields:
    return {field.name for field in metadata.fields if field.index_for_query}
  return set()


@memoize.Memoize(timeout=600, memoize_parallel_calls=True)
def GetAlternateKeyConfigs(metadata_kind):
  """Retrieve the alternate key configurations from a given metadata model.

  The returned dictionary contains the alternate key names and will return the
  field name in the key field, with model and lookup field.

  {
    '<alt_key_field_name>': <metadata_messages.MetadataAlternateKey>,
    .....
  }

  Args:
    metadata_kind: str, the kind of metadata to get.

  Returns:
    dict, A dictionary with the alternate key configurations.
  """
  metadata = GetMetadata(metadata_kind)
  if not metadata:
    return {}
  alt_keys = {}
  for field in metadata.fields:
    if field.alt_key:
      alt_keys[field.name] = field.alt_key
  return alt_keys


@memoize.Memoize(warn_on_error=False, timeout=600, cache_positions=[0])
def GetMetadataForeignKeyFieldsCached(kind, metadata=None):
  """Returns the fields identified as foreign key fields.

  This could be easily extended to use metadata instead of the well-known
  foreign key naming convention.

  Args:
    kind: str, the model kind.
    metadata: metadata_messages.Metadata instance.

  Returns:
    dict<str, tuple>, metadata-defined field name with tuple containing foreign
        key kind and foreign key field name.
  """
  metadata = metadata if metadata else GetMetadata(kind)
  foreign_keys = {}
  if metadata and metadata.fields:
    fk_end = constants.FK_SEP + constants.KEY_NAME
    for field in metadata.fields:
      if field.name.endswith(fk_end):
        foreign_keys[field.name] = (
            field.name.split(constants.FK_SEP)[0], constants.KEY_NAME)
  return foreign_keys


def GetConditionalOverrides(kind, entity):
  """Evaluates metadata conditional rules to determine metadata overrides.

  This method will collect the metadata conditional rules configured in the
  metadata of the given kind, and evaluate the found rules against the given
  entity. For any given metadata conditional rules that evaluate to true, the
  corresponding metadata override will be reported in the methods returned
  dictionary.

  The return dictionary will be in the form:

    {'<property_name>' : {'metadata_property': '<override_setting>'}, ...}

  For example:

    {
      'prop1': {'ui_readonly': False, 'convert_case': 'UPPER'},
      'prop2': {'required': True},
    }

  Args:
    kind: str, the model kind for rule evaluation.
    entity: dict, the entity to target during metadata rule evaluation.

  Returns:
    dict, the metadata fields to be overridden with the respective
      override values. The returned dictionary will be empty if no metadata
      conditional rules evaluate as true.
  """
  # First get the metadata.
  metadata = GetMetadata(kind)
  # Then get the assembled conditionals.
  assembled_conditionals = metadata_conditional.GetAssembledConditionals(
      metadata)

  # Finally, resolve the conditionals and return any triggered overrides.
  return metadata_conditional.ResolveConditionals(entity,
                                                  assembled_conditionals)
