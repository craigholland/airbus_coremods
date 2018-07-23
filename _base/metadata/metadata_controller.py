"""Controller class for metadata."""

import copy
import logging
import re

from google.appengine.ext import ndb

from google3.ops.netdeploy.netdesign.server.common import common_controller
from google3.ops.netdeploy.netdesign.server.common import common_validation
from google3.ops.netdeploy.netdesign.server.errors import error_collector
from google3.ops.netdeploy.netdesign.server.errors import error_msg
from google3.ops.netdeploy.netdesign.server.metadata import metadata_api
from google3.ops.netdeploy.netdesign.server.metadata import metadata_conditional
from google3.ops.netdeploy.netdesign.server.metadata import metadata_messages
from google3.ops.netdeploy.netdesign.server.metadata import metadata_models
from google3.ops.netdeploy.netdesign.server.metadata import metadata_utils
from google3.ops.netdeploy.netdesign.server.permissions import permissions_api
from google3.ops.netdeploy.netdesign.server.utils import conversion_utils
from google3.ops.netdeploy.netdesign.server.utils import model_utils


# Mapping and sets for metadata controller
NUMERICAL_TYPES = {
    metadata_messages.PropertyType.INTEGER: int,
    metadata_messages.PropertyType.DECIMAL: float,
    metadata_messages.PropertyType.FLOAT: float}


def _ValidateDate(value, field_metadata, errors, unused_cond_overrides):
  """Validate metadata_messages DATE property."""
  try:
    conversion_utils.ToDate(value)
  except conversion_utils.ConversionError:
    errors.Add(field_metadata.name, error_msg.INVALID_DATE % value)


def _ValidateCurrency(
    value, unused_field_metadata, unused_errors, unused_cond_overrides):
  """Validate metadata_messages CURRENCY property."""
  # Returns '0.00' whenever an invalid value is encountered.
  conversion_utils.ToCurrency(value)


RESTRICTION_CRITERIA_FIELD_TYPES = {
    metadata_messages.PropertyType.COMPUTED_CURRENCY: _ValidateCurrency,
    metadata_messages.PropertyType.CURRENCY: _ValidateCurrency,
    metadata_messages.PropertyType.DATE: _ValidateDate,
    metadata_messages.PropertyType.BOOLEAN: common_validation.CleanField,
    metadata_messages.PropertyType.DATETIME: common_validation.CleanField,
    metadata_messages.PropertyType.FLOAT: common_validation.CleanField,
    metadata_messages.PropertyType.DECIMAL: common_validation.CleanField,
    metadata_messages.PropertyType.INTEGER: common_validation.CleanField,
    metadata_messages.PropertyType.STRING: common_validation.CleanField,
    metadata_messages.PropertyType.TIMESTAMP: common_validation.CleanField
}

# Auto-generated fields.
AUTO_GENERATED = ['created_by', 'updated_by', 'created_on', 'updated_on']

_METADATA_UPDATE = 'Metadata for kind %s updated.'


def GetUnknownAttributeNames(metadata):
  """Returns all the unknown attribute names of the message and its fields.

  This does not handle the recursive hierarchy of fields, which is not
  currently enforced.

  Args:
    metadata: instance of metadata_messages.Metadata.

  Returns:
    list<str>, all the unknown attribute names in the metadata.
  """
  unknown_attributes = []
  unknown_attributes.extend(metadata.all_unrecognized_fields())
  for field in metadata.fields:
    unknown_attributes.extend(field.all_unrecognized_fields())
  return unknown_attributes


def GetUnknownFieldNames(metadata):
  """Returns all the unknown field names of the message and its fields.

  Args:
    metadata: instance of metadata_messages.Metadata.

  Returns:
    list<str>, all the unknown field names in the metadata.
  """
  model = model_utils.GetModel(metadata.kind)
  model_fields = set(model._properties)  # pylint: disable=protected-access
  model_fields.update(AUTO_GENERATED)
  metadata_fields = {f.name for f in metadata.fields}
  return list(model_fields ^ metadata_fields)


def List(kinds_only=False):
  """Gets list of metadata.

  Args:
    kinds_only: bool, return only kinds information.
  Returns:
    results: list of metadata_messages.Metadata, list of metadata.
  """
  kinds = metadata_api.GetKindsAsync().get_result()
  if kinds_only:
    results = [metadata_messages.Metadata(kind=k) for k in kinds]
  else:
    results = [metadata_api.GetMetadata(k) for k in kinds]
  return results


def Get(kind):
  """Gets metadata for specified kind.

  Args:
    kind: str, kind of metadata to fetch.
  Returns:
    metadata: metadata_messages.Metadata, metadata for kind.
  """
  if kind == 'Sample':
    return metadata_utils.SAMPLE_METADATA
  model = model_utils.GetModel(kind)
  metadata = getattr(model, '_meta', None)
  return metadata if metadata else metadata_api.GetMetadata(kind)


def Delete(kind):
  """Delete metadata for specified kind.

  Args:
    kind: str, kind of metadata to fetch.
  Returns:
    metadata: metadata_messages.Metadata, metadata that was deleted. or None if
      deletion fails.
  """
  key = ndb.Key('Metadata', kind)
  metadata_entity = key.get()
  if metadata_entity is not None:
    model = model_utils.GetModel(kind)
    if model.query().count(limit=1) == 0:
      errors = error_collector.Errors()
      common_controller.Delete(metadata_models.Metadata, kind, errors)
      if errors:
        logging.error(error_msg.METADATA_DELETE_FAIL, kind, errors)
        return
      permissions_api.Delete(kind)
    else:
      metadata_entity = None
  return metadata_entity


# TODO(gbelka): Refactor to use Errors.


def _ValidateUnique(field, unused_metadata=None):
  """Validation for unique property.

  The model must be both "required" and "index_for_query" in order
  to be unique.

  Args:
    field: metadata_messages.MetadatField, field for validation.
    unused_metadata: metadata_messages.Metadata, metadata field utilized by
      some _ValidateX functions, but not all.
  Returns:
    (valid, error), (bool, str), (if the value is valid, reason for failure.)
  """

  if not field.index_for_query:
    return False, error_msg.UNIQUE_VALIDATION % field.name
  return True, ''


def _ValidateDefaultValue(field, unused_metadata=None):
  """Validation for default_value property.

  For strings, the default_value should match:
    Choices available in metadata field property choices.
    Regular expression specified in metadata field property regex.

  For integer and decimals, the default_value should fall into metadata field
  property range (if it exists).

  Args:
    field: metadata_messages.MetadataField, field for validation.
    unused_metadata: metadata_messages.Metadata, metadata field utilized by
      some _ValidateX functions, but not all.
  Returns:
    (valid, error), (bool, str), (if the value is valid, reason for failure.)
  """
  # Checks string requirements.
  if field.property_type == metadata_messages.PropertyType.STRING:
    if field.choices and field.default_value not in field.choices:
      return False, error_msg.DEFAULT_VALUE_CHOICES % (
          field.default_value, field.choices)
    if field.regex and not re.match(field.regex, field.default_value):
      return False, error_msg.DEFAULT_VALUE_REGEX % (
          field.default_value, field.regex)
  # Checks numerical requirements.
  if field.property_type in NUMERICAL_TYPES and field.range:
    convert_function = NUMERICAL_TYPES.get(field.property_type)
    # Convert default value to appropriate type.
    try:
      value = convert_function(field.default_value)
    except ValueError:
      return False, error_msg.DEFAULT_VALUE_CONVERSION % field.default_value
    # Check if default value in range (inclusive).
    if value < field.range[0] or value > field.range[1]:
      return False, error_msg.DEFAULT_VALUE_RANGE % (value, field.range)
  return True, ''


def _ValidateRegex(field, unused_metadata=None):
  """Validation for regex property.

  Args:
    field: metadata_messages.MetadataField, field for validation.
    unused_metadata: metadata_messages.Metadata, metadata field utilized by
      some _ValidateX functions, but not all.
  Returns:
    (valid, error), (bool, str), (if the value is valid, reason for failure.)
  """
  try:
    re.compile(field.regex)
  except re.error as e:
    return (False, error_msg.INVALID_REGEX % (field.regex, str(e)))
  return True, ''


def _ValidateRange(field, unused_metadata=None):
  """Validation for range property.

  Range should comprise of a list that is size 2.

  Args:
    field: metadata_messages.MetadataField, field for validation.
    unused_metadata: metadata_messages.Metadata, metadata field utilized by
      some _ValidateX functions, but not all.
  Returns:
    (valid, error), (bool, str), (if the value is valid, reason for failure.)
  """
  if len(field.range) != 2:
    return False, error_msg.INVALID_RANGE_COUNT
  if field.property_type not in NUMERICAL_TYPES:
    return False, error_msg.INVALID_RANGE_TYPE
  return True, ''


def _ValidateAltKey(field, unused_metadata=None):
  """Validate alternate key field attributes.

  Args:
    field: metadata_messages.MetadataField, field for validation. Note: this
      method assumes that the passed field contains a configured alt_key
      property setting.
    unused_metadata: metadata_messages.Metadata, metadata field utilized by
      some _ValidateX functions, but not all.
  Returns:
    (valid, error). (bool, str), If successful returns (True, empty string),
      else if validation fails then return (False, error string).
  """
  if not field.alt_key.foreign_kind:
    return False, error_msg.UNDEFINED_FOREIGN_KIND % field.name
  if not field.alt_key.foreign_field:
    return False, error_msg.UNDEFINED_FOREIGN_FIELD% field.name
  if not field.alt_key.key_field:
    return False, error_msg.UNDEFINED_KEY_FIELD % field.name

  foreign_metadata = Get(field.alt_key.foreign_kind)
  foreign_field_metadata = metadata_utils.GetFieldByName(
      foreign_metadata, field.alt_key.foreign_field)
  if not foreign_field_metadata:
    return False, error_msg.NON_EXISTENT_FOREIGN_FIELD % (
        field.name, field.alt_key.foreign_field, field.alt_key.foreign_kind)

  if not field.alt_key.null_allowed and not foreign_field_metadata.required:
    return False, error_msg.FOREIGN_FIELD_REQUIRED % (
        foreign_field_metadata.name, foreign_metadata.kind, field.name)
  if not foreign_field_metadata.unique:
    return False, error_msg.FOREIGN_FIELD_UNIQUE % (
        foreign_field_metadata.name, foreign_metadata.kind, field.name)
  return True, ''


def _ValidateConditionals(field, metadata):
  """Function to validate conditionals for a given field.

  Args:
    field: metadata_messages.MetadataField, the metadata field that is to be
      validated.
    metadata: metadata_messages.Metadata, the metadata that the field is to be
      validated against.
  Returns:
    (boolean, str) If the validation is successful, this method will return
      True and an empty string. If validation fails, this method will return
      False and the returned string will have the error description message.
  """
  if len(field.conditionals) is 0:
    return False, error_msg.UNDEFINED_CONDITIONALS % field.name

  for conditional in field.conditionals:
    # Validate that rules exist.
    if len(conditional.rules) is 0:
      return False, error_msg.UNDEFINED_CONDITIONAL_RULES % field.name
    # Validate that overrides exist.
    if len(conditional.overrides) is 0:
      return False, error_msg.UNDEFINED_CONDITIONAL_OVERRIDES % field.name

    try:
      assembled_conditional = metadata_conditional.AssembledConditional(
          conditional, metadata)

      valid, error_message = assembled_conditional.Validate()
      if not valid:
        return valid, error_message

    except ValueError as ve:
      return False, ve.message
    except Exception as e:  # pylint: disable=broad-except
      msg = error_msg.UNKNOWN_CONDITIONAL_ASSEMBLY_ERROR % (
          field.name, e.message)
      return False, msg

  return True, ''


def _ValidateUpdateRestrictions(field, metadata):
  """Function to validate an update restriction for a given field.

  Args:
    field: metadata_messages.MetadataField, the metadata field that is to be
      validated.
    metadata: metadata_messages.Metadata, the metadata that the field is to be
      validated against.
  Returns:
    (boolean, str) If the validation is successful, this method will return
      True and an empty string. If validation fails, this method will return
      False and the returned string will have the error description message.
  """

  if not metadata.is_managed:
    return False, error_msg.SC_RESTRICT_MANAGED_ONLY

  # Validate criteria field.
  for criterion in field.update_restrictions.criteria:
    if not _ValidateUpdateRestrictionField(metadata, criterion.field):
      return False, error_msg.SC_CRITERIA_FIELD_MISSING % criterion.field
    # Must have either values or changes element.
    if not (criterion.values or criterion.changes):
      return (False, error_msg.SC_NO_VALUES_OR_CHANGES % field.name)
    # Validate criteria field values list.
    if criterion.values:
      for value in criterion.values:
        valid_value, message = _ValidateUpdateRestrictionValues(
            metadata, criterion.field, value)
        if not valid_value:
          return False, message
    # Validate value changes.
    if criterion.changes:
      for change in criterion.changes:
        # Change 'value' and 'to' returned sequentially, in 'from', 'to' order.
        if change.value:
          value = change.value
        # Check federated change 'value' and 'to' values.
        if change.to:
          valid_value, message = _ValidateUpdateRestrictionChanges(
              criterion.field, value, change.to)
          if not valid_value:
            return False, message
    # Validate groups.
    for group in criterion.groups:
      if not _ValidateUpdateRestrictionGroup(group):
        return (False, error_msg.SC_INVALID_GROUP_METADATA % (
            field.name, group))

  return True, ''


def _ValidateUpdateRestrictionField(metadata, field_name):
  """Make sure the update restriction criterion field is in the Model.

  Args:
    metadata: metadata_messages.Metadata, the metadata that the field is to be
      validated against.
    field_name: str, the name of the field in the update criterion.
  Returns:
    boolean: Returns True if the criterion field_name is present in the model,
    and does not begin with '_'; returns False otherwise.
  """
  # No special field names allowed.
  if field_name.startswith('_'):
    return False
  # Check that the field is in the model.
  return field_name in [field.name for field in metadata.fields]


def _ValidateUpdateRestrictionValues(metadata, field_name, value):
  """Validate criterion field and associated values.

  Make sure that the field designated in an update_restriction is of a supported
  type and that the passed value can be assigned to the field.

  Args:
    metadata: metadata_messages.Metadata, the metadata that the field is to be
      validated against.
    field_name: str, the name of the field in the update criterion.
    value: str, A string representation of the value to assign to the
    criterion field.
  Returns:
    (boolean, str) If the validation is successful, this method will return
      True and an empty string. If validation fails, this method will return
      False and the returned string will have the error description message.
  """
  field_metadata = None
  for field in metadata.fields:
    if field.name == field_name:
      field_metadata = field
  if field_metadata and field_metadata.property_type:
    if field_metadata.repeated:
      return False, error_msg.SC_REPEATING_CRITERIA_FIELD % field_name
    if field_metadata.property_type in RESTRICTION_CRITERIA_FIELD_TYPES:
      validation_function = RESTRICTION_CRITERIA_FIELD_TYPES.get(
          field_metadata.property_type)
      try:
        errors = error_collector.Errors()
        validation_function(value, field_metadata, errors, {})
        if errors:
          return False, error_msg.SC_CRITERIA_FIELD_VALIDATION_ERROR % (
              field_metadata.name, errors.Get(field_metadata.name))
        else:
          return True, ''
      except common_validation.ValidationError:
        return False, error_msg.SC_CRITERIA_FIELD_VALIDATION_EXCEPTION % (
            field_name, value)
    else:
      return False, error_msg.SC_INVALID_CRITERIA_FIELD_TYPE % (
          field_metadata.property_type)
  else:
    return False, error_msg.SC_FIELD_METADATA_NOT_FOUND % field_name


def _ValidateUpdateRestrictionChanges(field_name, value, to):
  """Validate "change" restrictions that contain a from and to value."""
  if value == to:
    return False, error_msg.SC_FROM_AND_TO_VALUES_THE_SAME % field_name
  else:
    return True, ''


def _ValidateUpdateRestrictionGroup(group):
  """Validate the format of update restriction group values."""
  # Check for tokens, like $DelegatePM (allow trailing upper case).
  if re.match(r'^\$([A-Z]+[a-z0-9A-Z]+)+$', group):
    return True
  # Otherwise, check that value is like this: 'doublehelix-supplychain'.
  return bool(re.match('^([a-z0-9]+(-[a-z0-9])?)+$', group))


# Metadata fields validation functions. This maps the metadata field property
# names to their validation functions.
METADATA_FIELDS_VALIDATORS = {
    'alt_key': _ValidateAltKey,
    'conditionals': _ValidateConditionals,
    'default_value': _ValidateDefaultValue,
    'range': _ValidateRange,
    'regex': _ValidateRegex,
    'update_restrictions': _ValidateUpdateRestrictions,
    'unique': _ValidateUnique,
}


def _ValidateFKFieldIndex(kind, field):
  """Validate that a FK reference field is indexed.

  Args:
    kind: string, kind in which the field appears.
    field: metadata_messages.MetadataField, field for validation.
  Returns:
    (valid, error), (bool, str), (if the value is valid, reason for failure.)
  """
  if not field.name.endswith('__key_name'):  # Only test fk fields.
    return True, ''

  if field.index_for_query:
    return True, ''
  else:
    return False, error_msg.FK_INVALID_INDEX_SETTING % (kind, field.name)


def Update(kind, metadata):
  """Validates and updates metadata.

  Any occurring error will be returned. Otherwise, update succeeds. Warnings
  could exist regardless of whether the update succeeeds.

  Args:
    kind: str, kind of metadata to be updated.
    metadata: metadata_messages.Metadata, metadata to be updated.
  Returns:
    errors, warnings: (list of str, list of str), errors if update failed.
  """
  # Validate metadata
  if kind != metadata.kind:
    return [error_msg.KIND_MISMATCH % (kind, metadata.kind)], []
  unknown_attrs = GetUnknownAttributeNames(metadata)
  if unknown_attrs:
    return [error_msg.UNKNOWN_ATTRIBUTES % (kind, ', '.join(unknown_attrs))], []

  # If managed model, do not allow new fields or delete fields.
  if kind in model_utils.GetManagedModels():
    unknown_fields = GetUnknownFieldNames(metadata)
    if unknown_fields:
      return [error_msg.MANAGED_FIELDS % (kind, ', '.join(unknown_fields))], []

  # Get metadata with model defaults.
  metadata_utils.SortFields(metadata.fields)
  input_metadata = copy.deepcopy(metadata)
  metadata = metadata_api.ApplyModelDefinedMetadata(kind, metadata)

  # Compare input metadata against metadata with model-based definitions.
  override_warnings = []
  if input_metadata != metadata:
    override_warnings = metadata_utils.MetadataDiff(
        kind, input_metadata, metadata)

  # Validate properties for metadata fields. Example: check if regex if valid,
  # if unique fields meet the pre-requisites, etc. Errors here will prevent
  # successful saves.
  validation_errors = []
  for field in metadata.fields:
    # Iterate through properties that require validation
    for prop, validation_function in METADATA_FIELDS_VALIDATORS.items():
      # If property has non-empty value in current field.
      if getattr(field, prop, None):
        valid, error = validation_function(field, metadata)
        if not valid:
          validation_errors.append(error)

    # If the field is a foreign key field, then it must be indexed.
    valid, error = _ValidateFKFieldIndex(kind, field)
    if not valid:
      validation_errors.append(error)

  # If there are any errors, return without saving the metadata update.
  if validation_errors:
    return validation_errors, []

  # Write metadata to ndb.
  try:
    metadata_models.Metadata(metadata=metadata).put(
        backup_description=_METADATA_UPDATE % kind)
  except ValueError as exc:
    return [str(exc)], []

  permissions_api.UpdatePermission(metadata)

  return [], override_warnings
