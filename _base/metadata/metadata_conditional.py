"""Classes and functions to support conditional metadata settings."""

import logging
import StringIO
import tokenize

from _base.errors import error_msg
from _base.metadata import metadata_messages
from _base.metadata import metadata_utils
from _base.utils import conversion_utils


# Boolean type metadata field properties.
BOOLEAN_METADATA_SETTINGS = {'ui_readonly', 'ui_hidden', 'required'}
BOOL_MAP = {'TRUE': True, 'FALSE': False}  # Map to convert string booleans.

# The list of data_types supported by Metadata conditional rules.
SUPPORTED_CONDITIONAL_DATATYPES = {
    'LDAP', 'STRING', 'CURRENCY', 'FLOAT', 'DECIMAL',
    'DATE', 'BOOLEAN', 'DATETIME', 'INTEGER', 'TIMESTAMP'
}

# The list of data types not supported by Metadata conditional rules.
UNSUPPORTED_CONDITIONAL_DATATYPES = {
    'JSON', 'PICKLE', 'KEY_NAME', 'NOTE', 'BASE64', 'COMPUTED', 'GENERIC',
    'GEOPT', 'ENTITY', 'LOCAL_STRUCT', 'STRUCT', 'TEXT', 'USER', 'KEY',
}

# The Metadata Conditional string types supported.
CONDITIONAL_STRING_DATATYPES = {
    'LDAP',
    'STRING',
    'CURRENCY',
}

# The Metadata Conditional float types supported.
CONDITIONAL_FLOAT_DATATYPES = {'FLOAT', 'DECIMAL',}

# The supported operations for conditional rules.
SUPPORTED_OPERATIONS = {'==', '!=', '>', '>=', '<', '<='}

# The Metadata properties allowed to be overridden.
ALLOWED_METADATA_PROPERTY_OVERRIDES = {
    'required', 'convert_case', 'regex', 'ui_hidden', 'ui_readonly'}

CASE_MAP = {
    'LOWER': metadata_messages.CaseType.LOWER,
    'UPPER': metadata_messages.CaseType.UPPER,
    'TITLE': metadata_messages.CaseType.TITLE,
}


def CoerceRuleValueDatatype(string_val, metadata_field):
  """Convert a string value to the type defined by metadata field.

  Args:
    string_val: string, the string representation of a value to be converted.
    metadata_field: metadata_messages.MetadataField, the metadata field
      definition to be used for conversion of string value.

  Returns:
    obj, the conversion of the string value to the appropriate data type as
      defined by the metadata field definition.

  Raises:
    ValueError: raised if an unsupported or unknown type is used in a
      conditional rule expression.
  """
  # Skip None values.
  if string_val is None:
    return string_val

  if metadata_field.property_type.name in CONDITIONAL_STRING_DATATYPES:
    if metadata_field.property_type.name == 'LDAP':
      return string_val.strip('"\'')
    else:
      return string_val
  elif metadata_field.property_type.name == 'BOOLEAN':
    return BOOL_MAP.get(string_val.upper())
  elif metadata_field.property_type.name == 'INTEGER':
    return int(string_val)
  elif metadata_field.property_type.name == 'DATE':
    return conversion_utils.ToDate(string_val.strip('"\''))
  elif metadata_field.property_type.name == 'DATETIME':
    return conversion_utils.ToDateTime(string_val.strip('"\''))
  elif metadata_field.property_type.name == 'TIMESTAMP':
    return conversion_utils.ToTime(string_val.strip('"\''))
  elif metadata_field.property_type.name in CONDITIONAL_FLOAT_DATATYPES:
    return float(string_val)
  elif metadata_field.property_type.name in UNSUPPORTED_CONDITIONAL_DATATYPES:
    raise ValueError(
        'Metadata conditional rules do not operate on type: %s'
        % metadata_field.property_type)
  else:
    raise ValueError('Unhandled Metadata type in conditional handling: %s'
                     % metadata_field.property_type)


class AssembledRule(object):
  """A representation of an individual conditional rule."""

  def __init__(self, rule_string, metadata):
    """Initialization of an AssembledRule.

    Args:
      rule_string: string, The rule in string form, to be parsed for
        rule assembly.
      metadata: metadata_messages.Metadata, The metadata to reference for rule
        construction, resolution, and validation.
    Raises:
      ValueError: Upon a failed attempt to parse the rule_string.
    """
    tokens = tokenize.generate_tokens(StringIO.StringIO(rule_string).readline)

    try:
      self.field = next(tokens)[1]
      self.op = next(tokens)[1]
      self.value = next(tokens)[1]
    except StopIteration:
      msg = error_msg.MALFORMED_CONDITIONAL_RULE % (rule_string, metadata.kind)
      logging.error(msg)
      raise ValueError(msg)

    self.metadata = metadata

  def __str__(self):
    return 'AssembledRule(field: %s, op: %s, value: %s)' % (
        self.field, self.op, self.value)

  def __repr__(self):
    return self.__str__()

  def Evaluate(self, entity):
    """Evaluate a given rule to determine the truth value.

    Args:
      entity: ndb.Model|dict, an entity instance to evaluate against
        the given rule.

    Returns:
      boolean, True if the given entity meets the rule conditions,
        else returns False.

    Raises:
      ValueError: Raised if an unknown opcode is detected.
    """
    if isinstance(entity, dict):
      field_value = entity.get(self.field, None)
    else:
      field_value = getattr(entity, self.field, None)

    if field_value is None:
      return False  # If there is no entity value, rule resolves to False.

    field_properties = metadata_utils.GetFieldByName(self.metadata, self.field)
    rule_value = CoerceRuleValueDatatype(self.value, field_properties)

    # If either field or rule value is None, then no valid
    # comparison is possible. Note: if both are None, then comparison may occur.
    if (field_value is None) ^ (rule_value is None):
      return

    if self.op == '==':
      return field_value == rule_value
    elif self.op == '!=':
      return field_value != rule_value
    elif self.op == '>':
      return field_value > rule_value
    elif self.op == '>=':
      return field_value >= rule_value
    elif self.op == '<':
      return field_value < rule_value
    elif self.op == '<=':
      return field_value <= rule_value
    else:
      msg = 'The rule operation code "%s" is invalid.' % self.op
      logging.error(msg)
      raise ValueError(msg)

  def Validate(self):
    """This method will test if the rule is valid.

    Returns:
      (boolean, string): Returns True and an empty string if not error is
        found. If error is found, then returns False and a string with an
        error description.
    """
    # Test that the target field exists.
    field = metadata_utils.GetFieldByName(self.metadata, self.field)
    if field is None:
      return False, error_msg.UNDEFINED_CONDITIONAL_RULE_REFERENCE % self.field

    # Test that the target field is a supported type.
    if field.property_type.name not in SUPPORTED_CONDITIONAL_DATATYPES:
      return False, error_msg.UNSUPPORTED_CONDITIONAL_TYPE % (
          field.property_type.name,
          self.field,
          sorted(SUPPORTED_CONDITIONAL_DATATYPES))

    # Test that the rule operation is supported.
    if self.op not in SUPPORTED_OPERATIONS:
      return False, error_msg.INVALID_CONDITIONAL_OPERATION % (
          self.op, ', '.join(sorted(SUPPORTED_OPERATIONS)))

    # Test that the conditional value is of valid type.
    try:
      CoerceRuleValueDatatype(self.value, field)
    except ValueError as ve:
      return False, error_msg.INVALID_CONDITIONAL_TYPE % ve.message

    return True, ''


class AssembledConditional(object):
  """Encapsulated metadata conditional definition for runtime evaluation."""

  def __init__(self, metadata_conditional, metadata):
    """Initialization of an AssembledConditional.

    Args:
      metadata_conditional: metadata_messages.Conditional, The rule in string
        form, to be parsed for rule assembly.
      metadata: metadata_messages.Metadata, The metadata to reference for rule
        construction, resolution, and validation.
    Raises:
      ValueError: Upon a failed attempt to parse the rule_string.
    """
    self.rules = []
    for raw_rule in metadata_conditional.rules:
      self.rules.append(AssembledRule(raw_rule, metadata))

    self.overrides = {}
    for override_string in metadata_conditional.overrides:
      try:
        tokens = tokenize.generate_tokens(
            StringIO.StringIO(override_string).readline)
        metadata_property = next(tokens)[1]
        next(tokens)  # Throw away the operator, as it is always =.
        override_setting = next(tokens)[1]

        # Convert override setting to Boolean if metadata property is boolean.
        if metadata_property in BOOLEAN_METADATA_SETTINGS:
          override_setting = BOOL_MAP.get(override_setting.upper())

        # Uppercase setting for 'convert_case' overrides.
        if metadata_property == 'convert_case':
          override_setting = CASE_MAP.get(
              override_setting.upper(), override_setting)

        # Record the override for subsequent return.
        self.overrides[metadata_property] = override_setting
      except StopIteration:
        msg = error_msg.MALFORMED_CONDITIONAL_OVERRIDE % (
            override_string, metadata.kind)
        logging.error(msg)
        raise ValueError(msg)

  def __str__(self):
    return 'AssembledConditional(rules: %s, overrides: %s)' % (
        str(self.rules), self.overrides)

  def __repr__(self):
    return self.__str__()

  def _ValidateOverrides(self):
    """This method will test if the assembled overrides are valid.

    Returns:
      (boolean, string): Returns True and an empty string if not error is
        found. If error is found, then returns False and a string with an
        error description.
    """
    for metadata_property, override_setting in self.overrides.iteritems():

      # Validate that the metadata property is supported for overriding.
      if metadata_property not in ALLOWED_METADATA_PROPERTY_OVERRIDES:
        return False, error_msg.INVALID_CONDITIONAL_OVERRIDE % (
            metadata_property, sorted(ALLOWED_METADATA_PROPERTY_OVERRIDES))

      # Validate conversion of the override setting for the given property.
      if metadata_property in BOOLEAN_METADATA_SETTINGS:
        if override_setting not in {True, False}:
          return False, error_msg.INVALID_BOOLEAN_PROPERTY_SETTING % (
              metadata_property)

      # Validate Case property override settings.
      if (metadata_property == 'convert_case' and
          override_setting not in {'LOWER', 'UPPER', 'TITLE'}):
        return False, error_msg.INVALID_CONVERT_CASE_SETTING % override_setting

    return True, ''

  def Evaluate(self, entity):
    """Test a given entity for possible triggering of conditional rules.

    The returned dictionary will be of the form:

      {
        '<metadata_property>': <setting_value>,
        ...
      }

    Where 'metadata_property' is the metadata field property is flagged to
    be overridden with the 'setting_value'.

    Args:
      entity: ndb.Model|dict, the entity that is to be evaluated for conditional
        expression.

    Returns:
      dict, A dictionary with the overrides applicable under the conditions of
        the given entity. If no conditional rules apply, the returned
        dictionary will be empty.
    """
    condition_met = all(rule.Evaluate(entity) for rule in self.rules)

    if condition_met:
      return self.overrides
    else:
      return {}

  def Validate(self):
    """This method will test if the conditional is valid.

    Returns:
      (boolean, string): Returns True and an empty string if not error is
        found. If error is found, then returns False and a string with an
        error description.
    """
    # Test that rules reference valid entity properties.
    for rule in self.rules:
      valid, error_message = rule.Validate()
      if not valid:
        return False, error_message

    # Test that overrides reference valid metadata properties.
    valid, error_message = self._ValidateOverrides()
    if not valid:
      return valid, error_message

    return True, ''


def GetConditionalRules(metadata):
  """Retrieve the conditional rule configurations from a given metadata model.

  The returned dictionary contains the conditional rules and will return the
  field name in the key field with model and lookup field.

  {
    '<conditional_rule_field_name': [<metadata_messages.Conditional>, ...]
  }

  Args:
    metadata: MetadataModel, Metadata definition for a given model.

  Returns:
    dict: A dictionary with the fields in the metadata that are configured with
      conditional rules.
  """
  conditionals = {}
  for field in metadata.fields:
    if field.conditionals:
      conditionals[field.name] = field.conditionals

  return conditionals


def GetAssembledConditionals(metadata):
  """Generate the AssembledConditionals from the given metadata.

  The returned result is of the form:

    {
      '<field_name>': [
        <AssembledConditional>,
        ...
      ],
      .....
    }

  Args:
    metadata: metadata_messages.Metadata, the metadata instance to be used for
      generating the AssembledConditionals.

  Returns:
    dict: A dictionary of AssembledConditionals generated from the
      given metadata.
  """
  raw_conditionals = GetConditionalRules(metadata)

  assembled_conditionals_map = {}
  for field_name, raw_conditionals in raw_conditionals.iteritems():
    assembled_conditionals = []
    for raw_conditional in raw_conditionals:
      assembled_conditionals.append(
          AssembledConditional(raw_conditional, metadata))
    assembled_conditionals_map[field_name] = assembled_conditionals

  return assembled_conditionals_map


def ResolveConditionals(entity, conditionals):
  """Resolve conditionals against a given entity to produce triggered overrides.

  This return dictionary format is of the form:

    {
      '<field_name>': {
        '<metadata_property>': <metadata_setting>,
        ...
      },
      .....
    }

  Where 'field_name' is the name of the field that is the target of the metadata
  override. The 'metadata_property' is the name of the metadata property whose
  value is to be overridden for the given field. The 'metadata_setting' is the
  value that will be used to override the metadata property for the given field.

  Args:
    entity: ndb.Model|dict, the entity to target during conditional resolution.
    conditionals: metadata_conditional.AssembledCondition.

  Returns:
    dict: A dictionary of field name keys with the corresponding overrides
      determined from resolving the conditionals against the given entity.
  """
  metadata_overrides = {}
  for field_name, assembled_conditions in conditionals.iteritems():
    field_overrides = {}
    for assembled_condition in assembled_conditions:
      overrides = assembled_condition.Evaluate(entity)
      field_overrides.update(overrides)

    if field_overrides:
      metadata_overrides[field_name] = field_overrides

  return metadata_overrides
