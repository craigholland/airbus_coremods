"""Metadata ProtoRPC messages."""

import itertools

import endpoints

from protorpc import messages

from google.appengine.ext import ndb

from _base.utils import permission_models
from _base.utils import model_utils

# Override the default package name exposed to clients.
package = 'metadata'

# Mapping of NDB property types to metadata property names. The first name is
# the default.
PROPERTY_TYPES = {
    model_utils.DHConditionalComputedProperty: ('CONDITIONAL_COMPUTED',),
    model_utils.DHComputedCurrencyProperty: ('COMPUTED_CURRENCY',),
    model_utils.DHCurrencyProperty: ('CURRENCY',),
    model_utils.DHDateProperty: ('DATE',),
    model_utils.DHJsonProperty: ('JSON', 'PICKLE'),
    model_utils.DHKeyNameProperty: ('KEY_NAME',),
    model_utils.DHLDAPProperty: ('LDAP',),
    model_utils.DHNoteProperty: ('NOTE',),
    model_utils.DHUpdateRestrictionComputedProperty: (
        'UPDATE_RESTRICTION_COMPUTED',),
    ndb.BlobProperty: ('BASE64',),
    ndb.BooleanProperty: ('BOOLEAN',),
    ndb.ComputedProperty: ('COMPUTED',),
    ndb.DateTimeProperty: ('DATETIME',),
    ndb.FloatProperty: ('FLOAT', 'DECIMAL'),
    ndb.GenericProperty: ('GENERIC',),
    ndb.GeoPtProperty: ('GEOPT',),
    ndb.IntegerProperty: ('INTEGER',),
    ndb.KeyProperty: ('KEY',),
    ndb.LocalStructuredProperty: ('ENTITY', 'LOCAL_STRUCT'),
    ndb.StringProperty: ('STRING',),
    ndb.StructuredProperty: ('STRUCT',),
    ndb.TextProperty: ('TEXT',),
    ndb.TimeProperty: ('TIMESTAMP',),
    ndb.UserProperty: ('USER',),
}

_PROPERTY_NAMES = sorted(
    itertools.chain.from_iterable(PROPERTY_TYPES.itervalues()))

# Valid property_type values.
PropertyType = type(  # pylint: disable=g-bad-name
    'PropertyType', (messages.Enum,),
    dict(map(reversed, enumerate(_PROPERTY_NAMES, 1))))


def _GeneratePropertyMap():
  """Helper for generating property map items."""
  for prop, names in PROPERTY_TYPES.iteritems():
    for name in names:
      yield PropertyType(name), prop

# Mapping of metadata property types to NDB property types.
PROPERTY_MAP = dict(_GeneratePropertyMap())


class CaseType(messages.Enum):
  """Valid convert_to_case values."""
  LOWER = 1
  UPPER = 2
  TITLE = 3


class SeparatorType(messages.Enum):
  """Valid show_horizontal_line values."""
  SINGLE = 1
  BOLD = 2
  DOUBLE = 3
  DASHED = 4


class BigQueryTransform(messages.Enum):
  """Valid bigquery_transform values."""
  EXCLUDE = 1
  JSON = 2


class MetadataFormField(messages.Message):
  """A field in form."""
  name = messages.StringField(1, required=True)
  # Label to be displayed on the form. If not specifed, default to title case
  # of the field name.
  # TODO(tsavigliano): Remove label after RC40 is deployed and all deployment
  # environments have their Order/OrderItem/BOM/BOMItem metadata updated.
  label = messages.StringField(2)
  # True if the field is required. If is False, use 'required' defined on the
  # model.
  required = messages.BooleanField(3, default=False)
  # If True, the clint should remove the field when submitting the form.
  ignore_save = messages.BooleanField(4, default=False)
  # Widget to use to render the field on form, if not specified, use
  # a text input.
  widget = messages.StringField(5)
  # Extra directive to render in the input widget. E.g., if
  # add_ons = 'dh-comma-sep-list' and the field is required. The field should be
  # rendered as the following:
  #   <input type="text" name="..." value={{ ... }} dh-comma-sep-list required>
  add_ons = messages.StringField(6, repeated=True)
  # This only applies to fields whose widget is text_only. E.g. if the
  # formatters is 'date : "MM/dd/yyyy HH:mm"' the field will be rendered as
  #   {{ ctrl.field | date : "MM/dd/yyyy HH:mm" }}
  formatters = messages.StringField(7, repeated=True)
  # Title to be displayed on the form.
  title = messages.StringField(8)


class MetadataFormColumn(messages.Message):
  """A column in form."""
  name = messages.StringField(1)
  description = messages.StringField(2)
  # Width of the label and field in number of chars
  label_width_chars = messages.IntegerField(
      3, default=20, variant=messages.Variant.UINT32)
  field_width_chars = messages.IntegerField(
      4, default=30, variant=messages.Variant.UINT32)
  fields = messages.MessageField(MetadataFormField, 5, repeated=True)


class MetadataForm(messages.Message):
  """A form which consists of columns."""
  name = messages.StringField(1)
  description = messages.StringField(2, required=False)
  columns = messages.MessageField(MetadataFormColumn, 3, repeated=True)


class MetadataReference(messages.Message):
  """Reference metadata.

  If present, indicates that the field is referencing a field in another table.
  If use_key is set to True, key value of the referenced entity will be stored,
  otherwise, value of the display_field in referenced entity will be stored.
  """
  kind = messages.StringField(1, required=True)
  display_field = messages.StringField(2, required=True)
  use_key = messages.BooleanField(3, default=False)


class DataPropagationEventType(messages.Enum):
  """Data Type used in DataPropagation_Trigger Message."""
  value_changed = 1
  value_increased = 2
  value_decreased = 3
  value_deleted = 4
  value_added = 5


class DataPropagationReferenceType(messages.Enum):
  direct = 1
  computed = 2


class DataPropagationTrigger(messages.Message):
  """If present, changes to the field may trigger changes to another field."""
  event_type = messages.EnumField(
      DataPropagationEventType, 1, default='value_changed')
  trigger_name = messages.StringField(2, required=True)
  target_kind = messages.StringField(3, required=True)
  target_field = messages.StringField(4, required=True)
  opt_kwargs = messages.StringField(5)


class DataPropagationAuthoritativeSource(messages.Message):
  kind = messages.StringField(1, required=True)
  field = messages.StringField(2, required=True)
  reference_type = messages.EnumField(DataPropagationReferenceType, 3)


class MetadataAlternateKey(messages.Message):
  """Metadata definition for alternate keys."""
  foreign_kind = messages.StringField(1, required=True)
  foreign_field = messages.StringField(2, required=True)
  key_field = messages.StringField(3, required=True)
  null_allowed = messages.BooleanField(4, default=False)


class Conditional(messages.Message):
  """A set of conditional rules with associated metadata overrides."""
  rules = messages.StringField(1, repeated=True)
  overrides = messages.StringField(2, repeated=True)


class Change(messages.Message):
  """Tuple for Criteria changes."""
  value = messages.StringField(1)
  to = messages.StringField(2)


class Criteria(messages.Message):
  """A set of field update permissions criteria."""
  field = messages.StringField(1)
  values = messages.StringField(2, repeated=True)
  changes = messages.MessageField(Change, 4, repeated=True)
  groups = messages.StringField(3, repeated=True)


class UpdateRestriction(messages.Message):
  """Model definition for field update restrictions."""
  criteria = messages.MessageField(Criteria, 1, repeated=True)


class MetadataField(messages.Message):
  """Model field metadata."""
  #
  # Primary metadata. These fields map to built-in NDB property attributes.
  #
  name = messages.StringField(1, required=True)
  fields = messages.MessageField('MetadataField', 2, repeated=True)
  property_type = messages.EnumField(
      PropertyType, 3, default=PropertyType.GENERIC)
  index_for_query = messages.BooleanField(4, default=False)
  # Repeated, required, and default_value are mutually exclusive.
  repeated = messages.BooleanField(5, default=False)
  required = messages.BooleanField(6, default=False)
  # If property_type is something other than STRING or TEXT, default_value and
  # choices should be JSON encoded.
  default_value = messages.StringField(7)
  choices = messages.StringField(8, repeated=True)
  verbose_name = messages.StringField(9)
  # Auto_add and auto_update only apply to user and date/time properties.
  auto_add = messages.BooleanField(10, default=False)
  auto_update = messages.BooleanField(11, default=False)
  #
  # Secondary metadata.
  #

  convert_case = messages.EnumField(CaseType, 12)
  decimal_digits = messages.IntegerField(13, variant=messages.Variant.UINT32)
  description = messages.StringField(14)
  display_order = messages.IntegerField(
      15, default=1000, variant=messages.Variant.UINT32)
  index_for_search = messages.BooleanField(16, default=True)
  range = messages.FloatField(18, repeated=True, variant=messages.Variant.FLOAT)
  regex = messages.StringField(19)
  sort_order = messages.IntegerField(
      20, default=100, variant=messages.Variant.UINT32)
  speckle_column = messages.StringField(21)
  strip_whitespace = messages.BooleanField(22, default=False)
  ui_hidden = messages.BooleanField(23, default=False)
  ui_readonly = messages.BooleanField(24, default=False)
  reference = messages.MessageField(MetadataReference, 25)

  bigquery_transform = messages.EnumField(BigQueryTransform, 26)
  unique = messages.BooleanField(27, default=False)
  href = messages.StringField(28)
  alt_key = messages.MessageField(MetadataAlternateKey, 29)
  radio_filter = messages.StringField(30)
  filter_display_name = messages.StringField(31)
  ui_readonly_on_update = messages.BooleanField(32, default=False)
  conditionals = messages.MessageField(Conditional, 33, repeated=True)
  update_restrictions = messages.MessageField(UpdateRestriction, 36)
  authoritative_source = messages.MessageField(
      DataPropagationAuthoritativeSource, 34)
  trigger = messages.MessageField(DataPropagationTrigger, 35, repeated=True)
  ui_date_pattern = messages.StringField(37)
  ui_column_max_width = messages.IntegerField(38)
  # Next ID: 39.


class MetadataLink(messages.Message):
  """Link metadata."""
  name = messages.StringField(1, required=True)
  href = messages.StringField(2)
  css_class = messages.StringField(3)
  description = messages.StringField(4)


class ViewColumn(messages.Message):
  """View column."""
  name = messages.StringField(1, required=True)
  title = messages.StringField(2)
  separator = messages.EnumField(SeparatorType, 3)


class MetadataView(messages.Message):
  """View metadata."""
  name = messages.StringField(1, required=True)
  title = messages.StringField(2)
  filter = messages.StringField(3)
  show_in_tableview = messages.BooleanField(4, default=True)
  columns = messages.MessageField(ViewColumn, 5, repeated=True)
  links = messages.MessageField(MetadataLink, 6, repeated=True)


class MetadataParent(messages.Message):
  """Parent metadata.

  If present, indicates that the entity for this metadata has a parent.  The
  parent key can be constructed using the specified kind and key_field value.
  {parent.kind}__key_name is the default key_field if the key_field is not
  specified.
  """
  kind = messages.StringField(1, required=True)
  # {parent.kind}__key_field is used if this is not set.
  key_field = messages.StringField(2)


class Metadata(messages.Message):
  """Model metadata."""
  #
  # Primary metadata. These fields map to built-in NDB model attributes.
  #
  kind = messages.StringField(1, required=True)
  fields = messages.MessageField(MetadataField, 2, repeated=True)
  #
  # Secondary metadata.
  #
  apply_fks = messages.BooleanField(3, default=True)
  backup = messages.BooleanField(4, default=True)
  description = messages.StringField(5)
  ui_readonly = messages.BooleanField(6, default=False)
  update_fk_refs = messages.BooleanField(7, default=True)
  update_search = messages.BooleanField(8, default=True)
  links = messages.MessageField(MetadataLink, 9, repeated=True)
  views = messages.MessageField(MetadataView, 10, repeated=True)
  forms = messages.MessageField(MetadataForm, 11, repeated=True)
  update_mvs = messages.BooleanField(12, default=True)
  parent = messages.MessageField(MetadataParent, 13)
  export_bigquery = messages.BooleanField(14, default=True)
  allow_import = messages.BooleanField(15, default=True)
  is_managed = messages.BooleanField(16, default=True)
  ui_sort_column = messages.StringField(17)
  is_mv = messages.BooleanField(18, default=False)
  ui_disable_add = messages.BooleanField(19, default=False)
  access_type = messages.StringField(
      20, default=permission_models.AccessType.TABLE_WRITE_ONLY.value)
  force_delete = messages.BooleanField(21, default=False)
  # Next index 39

LIST_METADATA_REQUEST = endpoints.ResourceContainer(
    kinds_only=messages.BooleanField(
        1, default=False))


class ListMetadataResponse(messages.Message):
  """List of model kinds that have metadata."""
  items = messages.MessageField(Metadata, 1, repeated=True)


DELETE_METADATA_REQUEST = endpoints.ResourceContainer(kind=messages.StringField(
    1, required=True))

GET_METADATA_REQUEST = endpoints.ResourceContainer(
    kind=messages.StringField(
        1, required=True),
    yaml=messages.BooleanField(
        2, default=False))


class GetMetadataResponse(messages.Message):
  """Metadata definition for a single model kind."""
  metadata = messages.MessageField(Metadata, 1)
  metadata_yaml = messages.StringField(2)
  errors = messages.StringField(3, repeated=True)
  has_items = messages.BooleanField(4, default=True)


class UpdateMetadataRequest(messages.Message):
  """Metadata definition for a single model kind."""
  metadata = messages.MessageField(Metadata, 1)
  metadata_yaml = messages.StringField(2)


UPDATE_METADATA_REQUEST = endpoints.ResourceContainer(
    UpdateMetadataRequest,
    kind=messages.StringField(
        1, required=True),
    yaml=messages.BooleanField(
        2, default=False))


class UpdateMetadataResponse(messages.Message):
  """Metadata definition for a single model kind."""
  errors = messages.StringField(1, repeated=True)
  warnings = messages.StringField(2, repeated=True)


class UpdateFromFileRequest(messages.Message):
  kind = messages.StringField(1)
  filename = messages.StringField(2)


class MetadataFilePair(messages.Message):
  kind = messages.StringField(1)
  filename = messages.StringField(2)


class ListFilesResponse(messages.Message):
  pairs = messages.MessageField(MetadataFilePair, 1, repeated=True)


class GetMetadataFileRequest(messages.Message):
  kind = messages.StringField(1)
