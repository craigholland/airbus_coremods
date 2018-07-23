"""Metadata utilities for Double Helix app."""

import copy
import logging
import operator
import uuid

from google.appengine.ext import ndb

from google3.pyglib.function_utils import memoize

from google3.ops.netdeploy.netdesign.server.errors import error_msg
from google3.ops.netdeploy.netdesign.server.metadata import metadata_conversions
from google3.ops.netdeploy.netdesign.server.metadata import metadata_messages
from google3.ops.netdeploy.netdesign.server.utils import constants
from google3.ops.netdeploy.netdesign.server.utils import yaml_utils

_KIND_FILENAME_DICT = None

# Flag value for static metadata that will cause the metadata value stored in
# the datastore to be reset to the default.
RESET = object()

# Reverse property mapping.
_PROPERTY_RMAP = {p: metadata_messages.PropertyType(n[0])
                  for p, n in metadata_messages.PROPERTY_TYPES.iteritems()}

# Sample Metadata
SAMPLE_METADATA = metadata_messages.Metadata(
    kind='Sample', apply_fks=False, backup=False, description='Sample Metadata',
    ui_readonly=True, update_fk_refs=False, ui_sort_column='sample_field1',
    allow_import=True, update_search=False, is_mv=True,
    fields=[{
        'name': 'sample_field1',
        'index_for_query': True,
        'property_type': metadata_messages.PropertyType.INTEGER,
        'default_value': '1',
        'choices': ['1', '2', '3'],
        'display_order': 50,
        'verbose_name': 'Sample Field',
        'description': 'A sample integer field.',
        'index_for_search': True,
        'range': [1.0, 3.0],
        'sort_order': 0,
        'speckle_column': 'SAMPLE_FIELD1',
        'ui_hidden': True,
        'ui_readonly': True,
    }, {
        'name': 'sample_field2',
        'required': True,
        'property_type': metadata_messages.PropertyType.STRING,
        'convert_case': metadata_messages.CaseType.UPPER,
        'regex': '^[A-Z]+$',
        'strip_whitespace': True,
        'href': 'https://www.google.com/#q={{ value }}',
    }, {
        'name': 'sample_field3',
        'repeated': True,
        'property_type': metadata_messages.PropertyType.STRUCT,
        'fields': [{'name': 'nested_field'}],
        'bigquery_transform': metadata_messages.BigQueryTransform.JSON
    }, {
        'name': 'sample_field4',
        'index_for_query': True,
        'property_type': metadata_messages.PropertyType.STRING,

    }, {
        'name': 'sample_field5',
        'property_type': metadata_messages.PropertyType.STRING,
    }, {
        'name': 'sample_field5corp',
        'property_type': metadata_messages.PropertyType.STRING,
    }], links=[{
        'name': 'link-one',
        'href': '/baseinfra/rack_elevation/?q={{ name }}',
        'css_class': 'css-class',
        'description': 'first description',
    }, {
        'name': 'link-two',
        'href': '/baseinfra/map/?q={{ name }}',
        'css_class': 'css-class',
        'description': 'second description',
    }], views=[{
        'name': 'View 1',
        'title': 'Title1',
        'filter': 'subtype',
        'columns': [{
            'name': 'sample_field1',
            'title': 'Sample Field 1',
        }, {
            'name': 'sample_field3',
            'separator': metadata_messages.SeparatorType.BOLD,
        }]
    }], forms=[{
        'name': 'Form 1',
        'description': 'Sample Form 1',
        'columns': [{
            'name': 'sample_column1',
            'description': 'Sample Column 1',
            'label_width_chars': 30,
            'field_width_chars': 30,
            'fields': [{
                'name': 'sample_field1',
                'label': 'Sample Field 1',
                'required': True,
            }, {
                'name': 'sample_field2',
                'label': 'Sample Field 2',
                'required': True,
                'ignore_save': True,
            }]
        }, {
            'name': 'sample_column2',
            'description': 'Sample Column 2',
            'label_width_chars': 30,
            'field_width_chars': 30,
            'fields': [{
                'name': 'sample_field3',
                'label': 'Sample Field 3',
                'required': True,
            }, {
                'name': 'sample_field4',
                'label': 'Sample Field 4',
                'required': True,
            }]
        }]
    }])


def UpdateMetadata(metadata, options):
  """Recursively updates a metadata message with provided dict of values.

  Args:
    metadata: metadata_messages.Metadata instance, the instance to update.
    options: dict, the metadata options to be merged into the metadata instance.
  """
  for key, value in options.iteritems():
    try:
      metadata_field = metadata.field_by_name(key)
    except KeyError:
      logging.warning('Metadata key %r does not exist in: %r', key, metadata)
      continue
    if value is RESET:
      if metadata_field.repeated:
        # TODO(davbennett): Use reset() once CL/66243971 goes live (1.9.6?).
        setattr(metadata, key, [])
      else:
        metadata.reset(key)
    elif metadata_field.repeated and isinstance(value, dict):
      # If we're merging a dict into a repeated field, assume it is a
      # repeated MessageField and that the message type has 'name' field.
      field_list = getattr(metadata, key)
      field_map = {f.name: f for f in field_list}
      for field_name, field_opts in value.iteritems():
        field = field_map.get(field_name)
        if field_opts is RESET:
          if field:
            field_list.remove(field)
        else:
          if field is None:
            if key == 'fields':
              field = _GetGenericField(field_name)
            else:
              field = metadata_field.message_type(name=field_name)
            field_list.append(field)
          UpdateMetadata(field, field_opts)
      if key == 'fields':
        # Always keep fields sorted.
        SortFields(field_list)
    else:
      if key == 'default_value' and value is not None:
        value = metadata_conversions.MaybeToString(value)
      elif key == 'choices':
        value = [metadata_conversions.MaybeToString(v)
                 for v in value if v is not None]
      setattr(metadata, key, value)


def ValidateMetadata(unused_prop, metadata):
  """Property validator that sorts fields and checks for duplicates.

  Args:
    metadata: metadata_messages.Metadata instance, the instance to validate.

  Raises:
    ValueError: if there is more than one field with the same name.
  """
  SortFields(metadata.fields)
  seen = set()
  for field in metadata.fields:
    if field.name in seen:
      raise ValueError('Duplicate metadata field name found: %r' % field.name)
    seen.add(field.name)


# TODO(rupalig): Move this method to metadata_api and possibly add memoize.
def ListRequiredFieldsWithNoDefaultVal(metadata, entity_fields=None):
  """Checks if there is any required field with no default value in dict.

  Args:
    metadata: metadata model.
    entity_fields: list, the list of entity fields, optional field.

  Returns:
    set of mandatory fields which have no default value.
  """
  required_fields = set()
  validation_list = list(metadata.fields) if metadata else []
  for validation in validation_list:
    field_name = validation.name
    if not entity_fields or field_name in entity_fields:
      # Skip the computed properties.
      if validation.property_type != metadata_messages.PropertyType.COMPUTED:
        if validation.required and validation.default_value is None:
          required_fields.add(field_name)
  return required_fields


# TODO(rupalig): Move this method to metadata_api and possibly add memoize.
def ListOptionalFieldsWithNoDefaultVal(entity_fields, metadata):
  """Checks if there is any optional field with no default value in dict.

  Args:
    entity_fields: list, the list of entity fields.
    metadata: metadata model.

  Returns:
    set of optional fields which have no default value.
  """
  optional_fields = set()
  validation_list = list(metadata.fields) if metadata else []
  for validation in validation_list:
    field_name = validation.name
    if field_name in entity_fields:
      # Skip the computer properties.
      if validation.property_type != metadata_messages.PropertyType.COMPUTED:
        if not validation.required and validation.default_value is None:
          optional_fields.add(field_name)
  return optional_fields


def SortFields(fields):
  """Sorts metadata fields by display_order, then name.

  Args:
    fields: list<metadata_messages.MetadataField>, the fields to sort.
  """
  fields.sort(key=operator.attrgetter('display_order', 'name'))


def GetFieldByName(metadata, name):
  """Returns the metadata field matching the given name.

  Args:
    metadata: metadata_messages.Metadata instance, the instance to use.
    name: str, the name of the field to return.

  Returns:
    metadata_messages.MetadataField if found, otherwise None.
  """
  return next((f for f in metadata.fields if f.name == name), None)


_RENAMED_FIELDS = {
    'allow_delete': 'allow_delete_if_deps',
    'ui_hide_field': 'ui_hidden',
}


def FixRenamedFields(message):
  """Fix renamed metadata settings.

  Args:
    message: Message instance, the message to be fixed.
  """
  for old_name in message.all_unrecognized_fields():
    new_name = _RENAMED_FIELDS.get(old_name)
    if new_name and message.get_assigned_value(new_name) is None:
      value, unused_variant = message.get_unrecognized_field_info(old_name)
      setattr(message, new_name, value)
      # ProtoRPC doesn't expose any way to clear unrecognized fields, so...
      # pylint: disable=protected-access
      del message._Message__unrecognized_fields[old_name]
      # pylint: enable=protected-access
  if getattr(message, 'fields', None):
    map(FixRenamedFields, message.fields)


def _GetGenericField(name, **kwargs):
  """Creates a new generic MetadataField instance.

  Args:
    name: str, the field name.
    **kwargs: dict, additional keyword properties to be set on the field.

  Returns:
    MetadataField instance.
  """
  kwargs.setdefault('index_for_query', True)
  kwargs.setdefault('index_for_search', True)
  return metadata_messages.MetadataField(
      name=name, property_type=metadata_messages.PropertyType.GENERIC, **kwargs)


def GetModelDefaults(properties):
  """Returns field defaults defined by model properties.

  Args:
    properties: dict, the model properties to process.

  Returns:
    dict, where the keys are field names and the values are dicts of options.
  """
  return {n: GetPropertyFieldDefaults(p) for n, p in properties.iteritems()}


def GetPropertyFieldDefaults(prop):
  """Converts an NDB Property instance into metadata field defaults.

  Args:
    prop: ndb.Property subclass instance, the property to convert.

  Returns:
    dict, the field defaults.
  """
  auto_add = auto_update = False
  sub_fields = {}
  # pylint: disable=protected-access
  if isinstance(prop, (ndb.StructuredProperty, ndb.LocalStructuredProperty)):
    sub_fields = GetModelDefaults(prop._modelclass._properties)
  elif isinstance(prop, ndb.DateTimeProperty):
    auto_add = prop._auto_now_add
    auto_update = prop._auto_now
  elif isinstance(prop, ndb.UserProperty):
    auto_add = prop._auto_current_user_add
    auto_update = prop._auto_current_user
  defaults = {
      'fields': sub_fields,
      'property_type': _PROPERTY_RMAP[type(prop)],
      'index_for_query': prop._indexed,
      'repeated': bool(prop._repeated),
  }
  # Only include auto_add, auto_update, required, default, choices, and
  # verbose_name if they're set.
  if auto_add:
    defaults['auto_add'] = auto_add
  if auto_update:
    defaults['auto_update'] = auto_update
  if prop._required:
    defaults['required'] = prop._required
  if prop._default is not None:
    defaults['default_value'] = prop._default
  if prop._choices:
    defaults['choices'] = list(prop._choices)
  if prop._verbose_name:
    defaults['verbose_name'] = prop._verbose_name
  if isinstance(prop, ndb.ComputedProperty):
    defaults['ui_readonly'] = True
  # pylint: enable=protected-access
  return defaults


def GetFieldProperty(field):
  """Converts a metadata field into an NDB Property instance.

  Args:
    field: metadata_messages.MetadataField instance, the field to convert.

  Returns:
    ndb.Property subclass instance.
  """
  return _GetFieldPropertyCached(_GetPropertyAttrs(field))


def MetadataDiff(kind, metadata1, metadata2):
  """Finds and reports the difference between two metadata.

  Args:
    kind: string, the kind being updated.
    metadata1: metadata_messages.Metadata, metadata to be updated.
    metadata2: metadata_messages.Metadata, metadata to compare against.
  Returns:
    errors: list of str, difference reported as list of errors.
  """
  errors = []
  properties = metadata2.all_fields()
  mismatch_properties = {
      f.name for f in properties
      if getattr(metadata1, f.name, None) != getattr(metadata2, f.name, None)}
  if 'fields' in mismatch_properties:
    mismatch_fields = GetMetadataFieldsDiff(
        metadata1, metadata2)
    mismatch_properties.remove('fields')
    if mismatch_fields:
      # Two metadatas can compare differently due to different orders of fields.
      # This will be detected by GetMetadataFieldsDiff() which will return no
      # differences in that case.
      errors.append(error_msg.OVERRIDE_FIELD % (kind, mismatch_fields))
  if mismatch_properties:
    if 'is_managed' in mismatch_properties:
      errors.append(error_msg.INCONSISTENT_IS_MANAGED % kind)
      mismatch_properties.remove('is_managed')
    if mismatch_properties:
      errors.append(
          error_msg.OVERRIDE_PROPERTY % (kind, sorted(mismatch_properties)))
  return errors


def GetMetadataFieldsDiff(metadata_one, metadata_two):
  """Returns field names that differ between two input metadata values."""
  diff_set = set()
  GetMetadataFieldsDiffSet(
      diff_set, '', metadata_one.fields, metadata_two.fields)
  return sorted(diff_set)


def MetadataDiffSet(diff_set, prefix, metadata_one, metadata_two):
  """Finds properties that are different between metadata_one and metadata_two.

  Args:
    diff_set: set, adds names of different elements to this set.
    prefix: str, prefixes the names of different elements with this.
    metadata_one: metadata_messages.Metadata, metadata to be updated.
    metadata_two: metadata_messages.Metadata, metadata to compare against.
  """
  properties = metadata_two.all_fields()
  for field in properties:
    if field != 'fields':
      if getattr(metadata_one, field.name, None) != getattr(
          metadata_two, field.name, None):
        diff_set.add(prefix + field.name)
    else:
      GetMetadataFieldsDiffSet(
          diff_set, prefix, metadata_one.fields, metadata_two.fields)


def GetMetadataFieldsDiffSet(diff_set, prefix, fields_one, fields_two):
  """Finds fields that are different between fields_one and fields_two.

  Args:
    diff_set: set, adds names of different elements to this set.
    prefix: str, prefixes the names of different elements with this.
    fields_one: metadata_messages.MetadataFields, fields to compare.
    fields_two: metadata_messages.MetadataFields, fields to compare.
  """
  fields1 = {f.name: f for f in fields_one}
  fields2 = {f.name: f for f in fields_two}

  for key in set(fields1) | set(fields2):
    field1 = fields1.get(key)
    field2 = fields2.get(key)
    key = str(key)
    if field1 and field2 and field1.fields and field2.fields:
      GetMetadataFieldsDiffSet(
          diff_set, prefix + key + '.', field1.fields, field2.fields)
      field1 = copy.copy(field1)
      field1.fields = []
      field2 = copy.copy(field2)
      field2.fields = []
      # Fall through to compare the rest of the fields.
    if field1 != field2:
      diff_set.add(prefix + key)


def _GetPropertyAttrs(field):
  """Converts a field into recursive tuples for memoization."""
  return (
      ('property_type', field.property_type),
      ('sub_attrs', tuple(_GetPropertyAttrs(f) for f in field.fields)),
      ('name', field.name),
      ('indexed', field.index_for_query),
      ('repeated', field.repeated),
      ('required', field.required),
      ('default', field.default_value),
      # NDB interprets an empty list to mean NO choices, which probably isn't
      # what anyone would want. So we use None to disable the restriction.
      ('choices', tuple(field.choices) if field.choices else None),
      ('verbose_name', field.verbose_name),
      ('auto_add', field.auto_add),
      ('auto_update', field.auto_update),
  )


@memoize.Memoize(warn_on_error=False)
def _GetFieldPropertyCached(property_attrs):
  """Converts property attributes into an NDB Property instance."""
  # The "required" and "choices" attributes are always disabled to avoid NDB
  # validation errors on existing data. Metadata validation should already cover
  # all new/changed data.
  property_attrs = dict(property_attrs, required=False, choices=None)
  property_type = property_attrs.pop('property_type')
  sub_attrs = property_attrs.pop('sub_attrs')
  auto_add = property_attrs.pop('auto_add')
  auto_update = property_attrs.pop('auto_update')
  default = property_attrs.get('default')
  cls = metadata_messages.PROPERTY_MAP[property_type]
  if cls is not ndb.GenericProperty and not issubclass(cls, ndb.TextProperty):
    if default is not None:
      property_attrs['default'] = metadata_conversions.MaybeFromString(default)
  if issubclass(cls, (ndb.StructuredProperty, ndb.LocalStructuredProperty)):
    properties = {}
    for attrs in sub_attrs:
      sub_prop = _GetFieldPropertyCached(attrs)
      # pylint: disable=protected-access
      properties[sub_prop._code_name] = sub_prop
      # pylint: enable=protected-access
    model = ndb.MetaModel(
        '_%s__Model' % uuid.uuid4(), (ndb.Expando,), properties)
    prop = cls(model, **property_attrs)
  elif issubclass(cls, ndb.DateTimeProperty):
    prop = cls(auto_now_add=auto_add, auto_now=auto_update, **property_attrs)
  elif issubclass(cls, ndb.UserProperty):
    prop = cls(auto_current_user_add=auto_add, auto_current_user=auto_update,
               **property_attrs)
  elif issubclass(cls, ndb.ComputedProperty):
    return None
  else:
    prop = cls(**property_attrs)
  prop._code_name = property_attrs['name']  # pylint: disable=protected-access
  return prop


def KindFilenameDict():
  """Return a dictionary of all kind: metadata file name pairs."""
  global _KIND_FILENAME_DICT
  if not _KIND_FILENAME_DICT:
    _KIND_FILENAME_DICT = yaml_utils.LoadFromFile(constants.METADATA_FILE_LIST)
  return _KIND_FILENAME_DICT

