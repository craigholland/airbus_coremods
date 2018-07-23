"""Metadata utils for converting values to metadata types in Double Helix."""


from google3.ops.netdeploy.netdesign.server.errors import error_msg
from google3.ops.netdeploy.netdesign.server.metadata import metadata_messages
from google3.ops.netdeploy.netdesign.server.utils import conversion_utils
from google3.ops.netdeploy.netdesign.server.utils import json_utils


CONVERTERS = {
    metadata_messages.PropertyType.BOOLEAN: conversion_utils.ToBool,
    metadata_messages.PropertyType.COMPUTED_CURRENCY:
        conversion_utils.ToCurrency,
    metadata_messages.PropertyType.CURRENCY: conversion_utils.ToCurrency,
    metadata_messages.PropertyType.DATE: conversion_utils.ToDate,
    metadata_messages.PropertyType.DATETIME: conversion_utils.ToDateTime,
    metadata_messages.PropertyType.DECIMAL: conversion_utils.ToFloat,
    metadata_messages.PropertyType.FLOAT: conversion_utils.ToFloat,
    metadata_messages.PropertyType.GEOPT: conversion_utils.ToGeoPt,
    metadata_messages.PropertyType.INTEGER: conversion_utils.ToInt,
    metadata_messages.PropertyType.KEY: conversion_utils.ToKey,
    metadata_messages.PropertyType.STRING: conversion_utils.ToUnicode,
    metadata_messages.PropertyType.TEXT: conversion_utils.ToUnicode,
    metadata_messages.PropertyType.TIMESTAMP: conversion_utils.ToFloat,
    metadata_messages.PropertyType.USER: conversion_utils.ToUser,
}


def Convert(value, value_type):
  """Tries to convert a value to value_type.

  Args:
    value: *, the value to attempt to convert.
    value_type: str, the type in CONVERTERS if type isn't found assume unicode.

  Returns:
    The converted value.
  Raises:
    conversion_utils.ConversionError: If there is an error during conversion.
  """
  converter = CONVERTERS.get(value_type)
  if converter is None:
    return value
  try:
    return converter(value)
  except (LookupError, TypeError, ValueError, AttributeError, NameError):
    raise conversion_utils.ConversionError(
        error_msg.METADATA_CONVERSION % (value, value_type))


def MaybeToString(value):
  """JSON encodes a value if it isn't already a string."""
  return value if isinstance(value, basestring) else json_utils.Dump(value)


def MaybeFromString(value):
  """JSON decodes a value if it is a string."""
  return json_utils.Load(value) if isinstance(value, basestring) else value


def GetMetadataDefaultValues(metadata_fields):
  """Returns the field default values for a list of metadata fields.

  Default values will be coerced to the metadata field property types.

  Args:
    metadata_fields: metadata field definitions.

  Returns:
    dict, containing metadata-defined field names with coerced default values.
  """
  defaults_values = {}
  for field in metadata_fields:
    if field.default_value:
      try:
        # Only run JSON conversion for non-string types.
        if field.property_type in (
            metadata_messages.PropertyType.GENERIC,
            metadata_messages.PropertyType.STRING,
            metadata_messages.PropertyType.TEXT):
          fromjson = field.default_value
        else:
          fromjson = MaybeFromString(field.default_value)
        coerced = Convert(fromjson, field.property_type)
        if coerced is not None:
          defaults_values[field.name] = coerced
      except (conversion_utils.ConversionError, ValueError):
        # If the default value from the metadata can't be coerced, ignore it.
        pass
  return defaults_values
