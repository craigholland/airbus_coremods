"""The common validation and clean methods for validating entity inputs."""

import copy
import datetime
import decimal
import json
import logging
import re

from google.appengine.ext import ndb

from google3.ops.netdeploy.netdesign.server.errors import error_collector
from google3.ops.netdeploy.netdesign.server.errors import error_msg
from google3.ops.netdeploy.netdesign.server.foreign_keys import fk_utils
from google3.ops.netdeploy.netdesign.server.metadata import metadata_api
from google3.ops.netdeploy.netdesign.server.metadata import metadata_conversions
from google3.ops.netdeploy.netdesign.server.metadata import metadata_messages
from google3.ops.netdeploy.netdesign.server.metadata import metadata_utils
from google3.ops.netdeploy.netdesign.server.user import user_utils
from google3.ops.netdeploy.netdesign.server.utils import constants
from google3.ops.netdeploy.netdesign.server.utils import conversion_utils
from google3.ops.netdeploy.netdesign.server.utils import model_utils


FIELD_CONVERT_CASE = 'convert_case'
FIELD_STRIP_WHITESPACE = 'strip_whitespace'


# The max size of a NDB indexed string.
STRING_MAX_SIZE = 1500

# Regex to match leading zeros in front of json fields.
_JSON_MISSING_LEADING_ZEROS = re.compile(r'.*(([^0-9])\.([0-9]+))')


def StripSpace(value):
  value = value.strip()
  value = ' '.join(value.split())
  return value


CASE_FUNCTION_MAP = {
    metadata_messages.CaseType.LOWER: lambda s: s.lower(),
    metadata_messages.CaseType.UPPER: lambda s: s.upper(),
    metadata_messages.CaseType.TITLE: lambda s: s.title(),
}


def CleanField(field_value, metadata_field, errors,
               conditional_overrides, convert=True):
  """Clean a single field based on metadata provided.

  This method applies metadata-based transformations to a single field value
  such as case-convert and whitespace removal.

  Args:
    field_value: value or list, entity value to clean.  This could be a list of
      values in the case of a repeated property.
    metadata_field: metadata_messages.MetadataField, The metadata field schema
      from metadata.
    errors: error_collector.Errors, for collecting errors.
    conditional_overrides: dict, A dictionary containing the metadata
      overrides for the given entity and model.
    convert: bool, whether metadata conversions should occur.

  Returns:
    The cleaned value.
  """
  if metadata_field and metadata_field.property_type:
    field_name = metadata_field.name
    if metadata_field.repeated:
      # Clean a repeatable/list field_value.
      if not isinstance(field_value, list):
        # If repeated by value is not list, ignore.
        logging.warning(error_msg.REPEATED_FAIL, field_name)
      else:
        values = []
        for list_value in field_value:
          value, error = _CleanField(
              list_value, metadata_field, conditional_overrides, convert)
          if error:
            errors.Add(field_name, error)
          else:
            values.append(value)
        field_value = values
    else:
      # Clean a non-repeatable/non-list field_value.
      field_value, error = _CleanField(
          field_value, metadata_field, conditional_overrides, convert)
      if error:
        ctx = errors.Context(
            errors.ContextOptions.IGNORE_MISSING_FIELD, field_name)
        if (error == error_msg.REQUIRED_FAIL % field_name and
            errors.HasContexts(ctx)):
          pass
        else:
          errors.Add(field_name, error)
  return field_value


@ndb.tasklet
def CleanEntityAsync(entity, errors):
  """Clean data based on metadata provided, asynchronous version.

  This method applies metadata default values as well as metadata-based
  transformations such as case-convert and whitespace removal.

  Args:
    entity: the ndb.Model, entity to clean.
    errors: error_collector.Errors, for collecting errors.

  Yields:
    Nothing
  """
  kind = entity._get_kind()  # pylint: disable=protected-access
  metadata = (getattr(entity, '_meta', None) or metadata_api.GetMetadata(kind))
  # metadata.fields can't be pickled, so it must be converted to a list.
  metadata_fields = list(metadata.fields) if metadata else None
  if not metadata_fields:
    raise ndb.Return(None)
  conditional_overrides = metadata_api.GetConditionalOverrides(kind, entity)

  # Apply metadata-defined defaults for unset properties.
  metadata_api.ApplyMetadataDefaultValuesToEntity(metadata, entity)
  # Do validation and transformation.
  for metadata_field in metadata_fields:
    field_name = metadata_field.name
    if hasattr(entity, field_name):
      if metadata_field.unique:
        yield ValidateUniqueFieldAsync(
            entity, field_name, entity.to_dict(), errors)
      field_value = getattr(entity, field_name, None)
      clean_value = CleanField(field_value, metadata_field, errors,
                               conditional_overrides, convert=False)
      # This step has the side-effect of making None (and perhaps
      # other) values into ndb.Property objects.
      if not errors and (field_value != clean_value or
                         not isinstance(clean_value, ndb.Property)):
        setattr(entity, field_name, clean_value)
  raise ndb.Return(None)


def CleanEntity(entity, errors):
  """Clean data based on metadata provided.

  This method applies metadata default values as well as metadata-based
  transformations such as case-convert and whitespace removal.

  Args:
    entity: the ndb.Model, entity to clean.
    errors: error_collector.Errors, for collecting errors.
  """
  CleanEntityAsync(entity, errors).get_result()


def _IsRequired(metadata_field, conditional_overrides):
  """Determines if a metadata field is required.

  Args:
    metadata_field: metadata_messages.MetadataField, The field that provides
      the default required configuration.
    conditional_overrides: dict, A dictionary containing the metadata
      overrides for the given entity and model. The conditional overrides are
      of the form:

        {
        '<metadata_property_name>': <property_setting_value>,
        ...
        }

  Returns:
    bool, True if the field is required, else returns False.
  """
  if metadata_field.name in conditional_overrides:
    # There are overrides defined for the metadata_field.name,
    # so the override for required is returned if present, else
    # just return the defined required.
    return conditional_overrides[metadata_field.name].get(
        'required', metadata_field.required)
  else:
    return metadata_field.required


def _ConvertCaseSetting(metadata_field, conditional_overrides):
  """Determines the case_conversion for a given field, if any.

  Args:
    metadata_field: metadata_messages.MetadataField, The field that provides
      the default required configuration.
    conditional_overrides: dict, A dictionary containing the metadata
      overrides for the given entity and model.

  Returns:
    str, The string representation of the case conversion. Will return None if
      no conversion is defined.
  """
  default_case_conversion = getattr(metadata_field, 'convert_case', None)

  if metadata_field.name in conditional_overrides:
    return conditional_overrides[metadata_field.name].get(
        'convert_case', default_case_conversion)
  else:
    return default_case_conversion


def Clean(entity_dict, kind, errors):
  """Cleans and Validates based on validation map provided.

  Clean operations that can be performed are white space stripping, upper
  casing, lower casing, and word capitalization.  Clean operation may modify
  field values.

  Validation does not occur till after Clean operations have been performed.

  Args:
    entity_dict: A dict containing a set of input values to validate.
        This value will be altered based on transformations.
    kind: str, name of the model used for validation.
    errors: error_collector.Errors, for collecting errors.
  """
  model = model_utils.GetModel(kind)
  metadata = (getattr(model, '_meta', None) or metadata_api.GetMetadata(kind))
  conditional_overrides = metadata_api.GetConditionalOverrides(
      kind, entity_dict)

  if metadata:
    # metadata.fields can't be pickled, so it must be converted to a list.
    metadata_fields = list(metadata.fields)
  else:
    # Return when there's no validation rules.
    logging.warn('No validation metadata found for model kind: %s', kind)
    return

  # Apply metadata-defined defaults for unset properties.
  metadata_api.ApplyMetadataDefaultValues(metadata, entity_dict)

  # Do validation, check the defined fields.
  for metadata_field in metadata_fields:
    field_name = metadata_field.name
    if field_name in entity_dict:
      # Check if field names needs to be unique.
      if metadata_field.unique:
        ValidateUniqueField(model, field_name, entity_dict, errors)
      # Check type if there is type validation and the value is not empty
      field_value = entity_dict[field_name]
      clean_value = CleanField(
          field_value, metadata_field, errors, conditional_overrides)
      if not errors and field_value != clean_value:
        entity_dict[field_name] = clean_value
    else:
      # If the field is not in the data, check to make sure it wasn't
      # required.
      if (_IsRequired(metadata_field, conditional_overrides) and
          metadata_field.default_value is None):
        ctx = errors.Context(
            errors.ContextOptions.IGNORE_MISSING_FIELD, field_name)
        if not errors.HasContexts(ctx):
          errors.Add(field_name, error_msg.REQUIRED_FAIL % metadata_field.name)


def _ValidateField(value, metadata_field, conditional_overrides):
  """Function to validate a value against a given metadata field.

  Args:
    value: object, A value to be tested.
    metadata_field: metadata_messages.MetadataField, The metadata field schema.
    conditional_overrides: dict, A dictionary containing the metadata
      overrides for the given entity and model.
  Returns:
    tuple (bool, str), (if the value is valid, reason for failure)
  """
  result = (True, '')
  if value is None:
    if (_IsRequired(metadata_field, conditional_overrides) and
        metadata_field.default_value is None):
      return False, error_msg.REQUIRED_FAIL % metadata_field.name
    return result
  if (metadata_field.choices and
      metadata_conversions.MaybeToString(value) not in metadata_field.choices):
    return False, error_msg.CHOICE_LIST_FAIL % (value, metadata_field.name)
  field_type = metadata_field.property_type
  validator = VALIDATORS.get(field_type)
  if validator is not None:
    result = validator(value, metadata_field, conditional_overrides)
  return result


def _ValidString(value, metadata_field, conditional_overrides):
  """Checks to make sure the given value is a valid String.

  Args:
    value: str, String to test.
    metadata_field: metadata_messages.MetadataField, field schema definitions..
    conditional_overrides: dict, A dictionary containing the metadata
      overrides for the given entity and model.
  Returns:
    tuple (bool, str), (if the value is valid, reason for failure)
  """
  if not isinstance(value, basestring):
    return False, error_msg.INVALID_TYPE
  if len(value) > STRING_MAX_SIZE:
    return False, error_msg.STRING_FAIL
  if not value and _IsRequired(metadata_field, conditional_overrides):
    return False, error_msg.REQUIRED_STRING_EMPTY
  if metadata_field.regex:
    return _ValidRegex(value, metadata_field, conditional_overrides)
  return True, ''


def _ValidRegex(value, metadata_field, unused_conditional_overrides):
  """Checks to make sure the given value matches the provided regex.

  Args:
    value: str, String to test.
    metadata_field: metadata_messages.MetadataField, field schema definition.
  Returns:
    tuple (bool, str), (if the value is valid, reason for failure)
  """
  regex = metadata_field.regex
  if value and not re.match(regex, value):
    return False, error_msg.REGEX_FAIL % (metadata_field.name, regex)
  return True, ''


def _ValidInt(value, metadata_field, unused_conditional_overrides):
  """Checks to make sure the given value is a valid Integer.

  If a range is provided, checks to make sure the value falls within the
  provided range.

  Args:
    value: int, Integer to test.
    metadata_field: metadata_messages.MetadataField, field schema definition.
  Returns:
    tuple (bool, str), (if the value is valid, reason for failure)
  """

  if not isinstance(value, (int, long)):
    return False, error_msg.INT_FAIL
  if metadata_field.range:
    range_list = metadata_field.range
    if value < range_list[0] or value > range_list[1]:
      return False, error_msg.INT_RANGE_FAIL % (value, range_list)
  return True, ''


def _ValidDecimal(value, metadata_field, unused_conditional_overrides):
  """Checks to make sure the given value is a valid Decimal.

  If a range is provided, checks to make sure the value falls within the
  provided range.

  Args:
    value: decimal.Decimal, Decimal to test.
    metadata_field: metadata_messages.MetadataField, field schema definition.
  Returns:
    tuple (bool, str), (if the value is valid, reason for failure)
  """

  if not isinstance(value, (decimal.Decimal, float)):
    return False, error_msg.DECIMAL_FAIL
  # Validate range.
  if metadata_field.range:
    range_list = metadata_field.range
    low = decimal.Decimal(str(range_list[0]))
    high = decimal.Decimal(str(range_list[1]))
    if value < low or value > high:
      return False, error_msg.DECIMAL_RANGE_FAIL % (value, range_list)
  return True, ''


def _ValidFloat(value, metadata_field, unused_conditional_overrides):
  """Checks to make sure the given value is a valid float.

  If a range is provided, checks to make sure the value falls within the
  provided range.

  Args:
    value: float, float to test.
    metadata_field: metadata_messages.MetadataField, field schema definition.
  Returns:
    tuple (bool, str), (if the value is valid, reason for failure)
  """
  if not isinstance(value, float):
    return False, error_msg.FLOAT_FAIL
  # Validate range.
  if metadata_field.range:
    range_list = metadata_field.range
    if value < range_list[0] or value > range_list[1]:
      return False, error_msg.FLOAT_RANGE_FAIL % (value, range_list)
  return True, ''


def _ValidTimestamp(
    value, unused_metadata_field, unused_conditional_overrides):
  """Checks to make sure the given value is a valid Timestamp.

  Args:
    value: decimal.Decimal, Decimal to test.
  Returns:
    tuple (bool, str), (if the value is valid, reason for failure)
  """
  # TODO(gordonms): Allow validation to the ISO string format for date
  # e.g. 2007-06-09T17:46:21
  # First see if a decimal number was provided.
  if not isinstance(value, (decimal.Decimal, float)):
    return False, error_msg.TIMESTAMP_FAIL
  return True, ''


def _ValidBoolean(
    value, unused_metadata_field, unused_conditional_overrides):
  """Checks to make sure the given value is a valid boolean.

  Args:
    value: bool, boolean to test.
  Returns:
    tuple (bool, str), (if the value is valid, reason for failure)
  """
  if not isinstance(value, bool):
    return False, error_msg.BOOLEAN_FAIL
  return True, ''


def _ValidDateTime(
    value, unused_metadata_field, unused_conditional_overrides):
  """Checks to make sure the given value is a valid datetime.

  Args:
    value: datetime.datetime, datetime to test.
  Returns:
    tuple (bool, str), (if the value is valid, reason for failure)
  """
  if not isinstance(value, datetime.datetime):
    return False, error_msg.DATETIME_FAIL
  return True, ''


def _ValidLdap(value, metadata_field, conditional_overrides):
  """Checks to make sure the given value is a valid LDAP.

  Args:
    value: str, LDAP to test.
    metadata_field: metadata_messages.MetadataField, field schema definition.
    conditional_overrides: dict, A dictionary containing the metadata
      overrides for the given entity and model.
  Returns:
    tuple (bool, str), (if the value is valid, reason for failure)
  Raises:
    stubby.RPCApplicationError, when ldap lookup fails.
  """
  if not value and not _IsRequired(metadata_field, conditional_overrides):
    return True, ''
  try:
    if not user_utils.IsUser(value):
      return False, error_msg.INVALID_LDAP % value
  except user_utils.GrouperConnectionError as e:
    return False, error_msg.GROUPER_LDAP % e.message
  return True, ''


VALIDATORS = {
    metadata_messages.PropertyType.STRING: _ValidString,
    metadata_messages.PropertyType.INTEGER: _ValidInt,
    metadata_messages.PropertyType.DECIMAL: _ValidDecimal,
    metadata_messages.PropertyType.FLOAT: _ValidFloat,
    metadata_messages.PropertyType.TIMESTAMP: _ValidTimestamp,
    metadata_messages.PropertyType.BOOLEAN: _ValidBoolean,
    metadata_messages.PropertyType.DATETIME: _ValidDateTime,
    metadata_messages.PropertyType.LDAP: _ValidLdap
}


def _CleanField(value, metadata_field, conditional_overrides, convert=True):
  """Clean and Validate a single field according to validation.

  The _CleanField function operates on a single field of an entity. The
  _CleanField function will perform transform operation on a given value, and
  subsequently perform validation check on the given value.
  Transformation and Validation operations are driven by the given validation
  rule.

  Args:
    value: *, The Field Value.
    metadata_field: metadata_messages.MetadataField, the metadata field schema.
    conditional_overrides: dict, A dictionary containing the metadata
      overrides for the given entity and model.
    convert: bool, whether metadata conversions should occur.
  Returns:
    tuple (value, validation_error), the returned value reported may be a value
      after transformation operations.
  Raises:
    conversion_utils.ConversionError, upon error in value conversion.
  """
  # If there is no value, simply validate the field, else continue on to check
  # if conversions are necessary, prior to
  if value is None or value == '':  # pylint: disable=g-explicit-bool-comparison
    # If a field has choices, but no value, then force the value to None.
    if metadata_field.choices:
      value = None
    # Move forward with validation.
    _, error = _ValidateField(value, metadata_field, conditional_overrides)
    return value, error

  try:
    if convert:
      value = metadata_conversions.Convert(value, metadata_field.property_type)

    # Check for whitespace stripping first.
    if getattr(metadata_field, 'strip_whitespace', False):
      value = StripSpace(value)

    # Check for conversion requirement if necessary.
    case_conversion = _ConvertCaseSetting(metadata_field, conditional_overrides)
    if case_conversion:
      value = CASE_FUNCTION_MAP[case_conversion](value)

  except conversion_utils.ConversionError:
    return value, error_msg.INVALID_TYPE

  _, error = _ValidateField(value, metadata_field, conditional_overrides)

  return value, error


@ndb.tasklet
def ValidateUniqueFieldAsync(model, field, request, errors):
  """Validates the entity name to check for duplicates, asynchronous version.

  Uniqueness validation is skipped if the value for the target field is None.

  Args:
    model: ndb.Model, The target model class for validation.
    field: str, The field_name to be validated for uniqueness.
    request: dict, The request data to be validated for uniqueness.
    errors: error_collector.Errors, for collecting errors.

  Yields:
    Nothing
  """
  # TODO(bryany): Make this method private in favor of using metadata.
  # If there is no value for the given field, then skip uniqueness validation.
  field_value = request.get(field)
  if field_value is None or field_value == '':  # pylint: disable=g-explicit-bool-comparison
    return

  # Check for field for duplicates, and error dict if one is found.
  model_query = model.query()
  model_query = model_query.filter(
      ndb.FilterNode(field, '=', field_value))
  query_results = yield model_query.fetch_async(2, keys_only=True)

  # If more than one duplicate found, error should be thrown.
  if len(query_results) > 1:
    # pylint: disable=protected-access
    errors.Add(field, error_msg.DUPLICATE_VALUE %
               (model._get_kind(), field, field_value))
    # pylint: enable=protected-access
    raise ndb.Return(None)

  duplicate_entity_key = query_results[0] if query_results else None

  if duplicate_entity_key:
    # Check whether this is an update operation and the update is attempting
    # to name the field the same as an existing one.
    key_name = request.get(constants.KEY_NAME)
    if key_name != duplicate_entity_key.id():
      # pylint: disable=protected-access
      errors.Add(field, error_msg.DUPLICATE_VALUE %
                 (model._get_kind(), field, field_value))
      raise ndb.Return(None)
      # pylint: enable=protected-access


def ValidateUniqueField(model, field, request, errors):
  """Validates the entity name to check for duplicates.

  Args:
    model: ndb.Model, The target model class for validation.
    field: str, The field_name to be validated for uniqueness.
    request: dict, The request data to be validated for uniqueness.
    errors: error_collector.Errors, for collecting errors.
  """
  ValidateUniqueFieldAsync(model, field, request, errors).get_result()


def ValidateModelDependency(entity, fk_model, fk_field_name):
  """Validates if the model has any foreign key relationship to the given model.

  Args:
    entity: ndb.Model instance, The target model class for validation.
    fk_model: ndb.Model, The model instance for the foreign key.
    fk_field_name: str, The name of the foreign key field.
  Returns:
    list<str>, list of entities having FK relationships to the given model.
  """
  fk_entities = fk_model.query(
      getattr(fk_model, fk_field_name) == entity.key.id()).fetch()
  result = []
  if fk_entities:
    for fk_entity in fk_entities:
      result.append(fk_entity.key.id())
  return result


def ValidateInSeq(validators, entity, errors):
  """Runs validations in sequence one by one until the first failure.

      Does not run validations if errors are not empty when called.
  Args:
    validators: list<callable> Validation functions called as f(entity, errors).
    entity: ndb.Model instance, The target model class for validation.
    errors: error_collector.Errors, for collecting errors.
  """
  for validator in validators:
    if errors:
      return
    validator(entity, errors)


def GetChanges(old, new, apply_metadata=False, exclude_fk=True):
  """Gets the changes between two entities.

  This function only compares properties that are present in both entities.

  Args:
    old: ndb.Model, the entity representing the previous state.
    new: ndb.Model, the entity representing the current state.
    apply_metadata: bool, if True, perform metadata transformations before
        determining changes.
    exclude_fk: bool, if True, changes to foreign key properties are not
        reported.

  Returns:
    A dictionary with keys being the properties that have changed between the
    two entities, and values in the format (old_value, new_value).
  """
  changes = {}
  if not old or not new:
    return changes
  # pylint: disable=protected-access
  for name in old._properties.viewkeys() & new._properties.viewkeys():
    if exclude_fk and constants.FK_SEP in name and not name.endswith(
        constants.FK_SEP + constants.KEY_NAME):
      continue
    changed, old_value, new_value = GetChange(
        old, new, name, apply_metadata=apply_metadata)
    if changed:
      changes[name] = (old_value, new_value)
  # pylint: enable=protected-access
  return changes


def GetChange(old, new, field_name, apply_metadata=False):
  """Gets the changes between two entities for a single field.

  Args:
    old: ndb.Model, the entity representing the previous state.
    new: ndb.Model, the entity representing the current state.
    field_name: sring, the field name to compare.
    apply_metadata: bool, if True, perform metadata transformations before
        determining changes.

  Returns:
    A tuple in the format (changed?, old_value, new_value).
  """
  old_value = getattr(old, field_name, None)
  new_value = getattr(new, field_name, None)
  if apply_metadata:
    metadata = old._meta  # pylint: disable=protected-access
    field = metadata_utils.GetFieldByName(metadata, field_name)
    errors = error_collector.Errors()
    old_value = CleanField(old_value, field, errors, old, metadata)
    new_value = CleanField(new_value, field, errors, new, metadata)
  return (old_value != new_value, copy.copy(old_value), copy.copy(new_value))


def CopyOnce(source_field, target_field, existing_entity, new_entity):
  """Copies a value from a source field to a target field on an entity one time.

  This function only copies a value from a source field to a target field if the
  target field has never been set (i.e. is None).

  Args:
    source_field: str, the field name of the source property to copy from.
    target_field: str, the field name of the target property to copy to.
    existing_entity: ndb.Model, the entity representing the previous state to
        copy from.
    new_entity: ndb.Model, the entity representing the current state to copy to.

  Returns:
    True, if the copy occurs (is the first time the target is populated), False
    otherwise.
  """
  if existing_entity:
    existing_value = getattr(existing_entity, target_field, None)
    if existing_value is not None:
      setattr(new_entity, target_field, existing_value)
    if getattr(new_entity, target_field, None) is None:
      for value in (getattr(existing_entity, source_field, None),
                    getattr(new_entity, source_field, None)):
        if value is not None:
          setattr(new_entity, target_field, value)
          return True
  else:
    value = getattr(new_entity, source_field, None)
    if value is not None:
      setattr(new_entity, target_field, value)
      return True
  return False


def ValidateRequiredFields(entity, required_fields, errors):
  """Validates if required fields exist in the entity.

  Args:
    entity: ndb.Model, the entity being checked.
    required_fields: list of str, required field names.
    errors: error_collector.Errors, for collecting errors during create.
  """
  kind = entity._get_kind()  # pylint: disable=protected-access
  for field in required_fields:
    attr = getattr(entity, field, None)
    if attr is None:  # Should be None check since attr can take 0 or False.
      errors.Add(kind, error_msg.REQUIRED_FAIL % field)


def ValidateImmutableFields(old_entity, new_entity, unchangeable_fields,
                            errors):
  """Validates if immutable fields should not be updated.

  Args:
    old_entity: ndb.Model, existing entity.
    new_entity: ndb.Model, updated entity.
    unchangeable_fields: list of str, unchangeable field names.
    errors: error_collector.Errors, for collecting errors during create.
  """
  kind = old_entity._get_kind()  # pylint: disable=protected-access
  for field in unchangeable_fields:
    old_value = getattr(old_entity, field, None)
    new_value = getattr(new_entity, field, None)
    if old_value != new_value:
      errors.Add(kind, error_msg.IMMUTABLE_FIELD_UPDATE_FAIL % field)


@ndb.tasklet
def ValidateEntityExistsAsync(model, key_name, errors):
  """Validates if an entity exists.

  Args:
    model: ndb.Model, the model to be validated for deletion.
    key_name: str, the key_name of the model.
    errors: error.Errors, aggregator used to collect
      any errors found during validation.
  Yields:
    Entity if it exists, None if validation fails.
  """
  kind = model._get_kind()  # pylint: disable=protected-access
  if not key_name:
    raise ndb.Return(None)
  entity = yield model.get_by_id_async(key_name, use_cache=False)
  if not entity:
    errors.Add(key_name, error_msg.ENTITY_MISSING % (kind, key_name))
    raise ndb.Return(None)
  raise ndb.Return(entity)


def ValidateEntityExists(model, key_name, errors):
  """Validates if an entity exists."""
  return ValidateEntityExistsAsync(model, key_name, errors).get_result()


@ndb.tasklet
def ValidateDeleteAsync(entity, errors):
  """Validates if an entity can be deleted.

  If validation fails, then None will be returned. If validation succeeds,
  the entity is returned.

  Args:
    entity: ndb.Model, the entity to be validated for deletion.
    errors: error.Errors, aggregator used to collect
      any errors found during validation.

  Yields:
    Nothing.
  """
  skip = entity and hasattr(entity, '_meta') and entity._meta.force_delete  # pylint: disable=protected-access
  if entity and not skip:
    dep_entities = yield fk_utils.GetAllChildEntitiesAsync(
        entity, include_views=False, direct_descendants=True)
    for dep_entity in dep_entities:
      errors.Add(entity.key.id(), error_msg.DEPENDENCY %
                 (model_utils.DisplayName(dep_entity), dep_entity.key.kind(),
                  entity.key.kind()))


def ValidateDelete(entity, errors):
  """Validates if an entity can be deleted."""
  ValidateDeleteAsync(entity, errors).get_result()


@ndb.tasklet
def ValidateDecommissionAsync(entity, errors, direct_descendants=True):
  """Validates if an entity can be decomissioned.

  Args:
    entity: ndb.Model, the entity to be validated for deletion.
    errors: error.Errors, aggregator used to collect
      any errors found during validation.
    direct_descendants: boolean, Include children of children if False else only
      include direct descendants.

  Yields:
    Nothing.
  """
  if entity:
    dep_entities = yield fk_utils.GetAllChildEntitiesAsync(
        entity, include_views=False, direct_descendants=direct_descendants)
    for dep_entity in dep_entities:
      status = None
      # TODO(mphegde): Use IsDecommissionable and status in BaseModel.
      for possible_status in (constants.PHYSICAL_STATUS,
                              constants.LOGICAL_STATUS,
                              constants.COMMISSIONING_STATUS):
        if hasattr(dep_entity, possible_status):
          status = possible_status
          if status:
            is_asbuilt = (
                getattr(dep_entity, status) and
                getattr(dep_entity, status, '').lower() ==
                constants.PHYSICAL_STATUS_ASBUILT)
            if is_asbuilt:
              errors.Add(entity.key.id(), error_msg.DEP_DECOMMISSION %
                         (model_utils.DisplayName(dep_entity),
                          dep_entity.key.kind()))


def ValidateDecommission(entity, errors, direct_descendants=True):
  """Validates if an entity can be decomissioned."""
  ValidateDecommissionAsync(
      entity, errors, direct_descendants=direct_descendants).get_result()


def ValidateJsonString(json_string, field_name, errors):
  """Validates and fixup a JSON string.

  Determines if a string contains valid JSON and attempts some basic
  fixes if the string is invalid.

  Args:
    json_string: str, the JSON string to inspect.
    field_name: str, the field name of the json string.
    errors: error.Errors, aggregator used to collect
        any errors found during validation.

  Returns:
    None if there are errors else the validated JSON.
  """
  try:
    # Optimistic validation check (throws ValueError if JSON str is invalid).
    json.loads(json_string)
    return json_string
  except ValueError:
    for char in json_string:
      if ord(char) > 127:
        errors.Add(field_name, error_msg.JSON_INVALID_ASCII % char)
        return
    # Scrub by stripping control chars and inserting leading zeros.
    stripped_json = ''.join(
        char for char in json_string if not 0 <= ord(char) <= 31)
    m = _JSON_MISSING_LEADING_ZEROS.match(stripped_json)
    while m:
      stripped_json = stripped_json.replace(
          m.group(1), '{0}0.{1}'.format(m.group(2), m.group(3)))
      m = _JSON_MISSING_LEADING_ZEROS.match(stripped_json)
    try:
      json.loads(stripped_json)
      return stripped_json
    except ValueError:
      errors.Add(field_name, error_msg.JSON_DECODE_FAIL)
