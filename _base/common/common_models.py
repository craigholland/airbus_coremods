"""Common models for Double Helix app."""

import hashlib
import uuid

from google.appengine.ext import ndb

from _base.metadata import metadata_api
from _base.metadata import metadata_messages
from _base.metadata import metadata_models
from _base.utils import model_utils


class BaseModel(metadata_models.MetadataModel):
  """Base model for Airbus models."""
  key_name = model_utils.DHKeyNameProperty()
  key_subtype = ndb.StringProperty()
  key_version = ndb.IntegerProperty()
  key_order = ndb.StringProperty()
  attachment_count = ndb.IntegerProperty(default=0)

  class Meta(object):
    fields = {
        'key_name': {
            'display_order': 0,
            'index_for_search': False,
            'ui_readonly': True,
        },
        'attachment_count': {
            'display_order': 9991,
            'index_for_search': False,
            'ui_readonly': True,
        },
        # A total order used to give consistent row orders in the UI.
        'key_order': {
            'display_order': 9992,
            'index_for_search': False,
        },
        'key_version': {
            'display_order': 9993,
            'index_for_search': False,
            'ui_readonly': True,
        },
        # These properties are added dynamically so that they can be modified
        # at runtime.
        'created_by': {
            'auto_add': True,
            'display_order': 9995,
            'index_for_query': True,
            'index_for_search': False,
            'property_type': metadata_messages.PropertyType.USER,
            'ui_readonly': True,
        },
        'created_on': {
            'auto_add': True,
            'display_order': 9996,
            'index_for_query': True,
            'property_type': metadata_messages.PropertyType.DATETIME,
            'ui_readonly': True,
        },
        'updated_by': {
            'auto_update': True,
            'display_order': 9997,
            'index_for_query': True,
            'property_type': metadata_messages.PropertyType.USER,
            'ui_readonly': True,
        },
        'updated_on': {
            'auto_update': True,
            'display_order': 9998,
            'index_for_query': True,
            'property_type': metadata_messages.PropertyType.DATETIME,
            'ui_readonly': True,
        },
    }

  def GenerateKey(self):
    """Generate UUID for new entities."""
    self.key_name = self.key_name or str(uuid.uuid4())
    if self.key is None or not self.key.id():
      self.key = ndb.Key(self._get_kind(), self.key_name)
      return True
    return False

  def __init__(*args, **kwargs):  # pylint: disable=no-method-argument
    """Overridden to prevent key_name from clobbering id."""
    self, args = args[0], args[1:]  # Copied from ndb to allow 'self' kwarg.
    if 'id' in kwargs and 'key_name' in kwargs:
      kwargs.pop('key_name')
    super(BaseModel, self).__init__(*args, **kwargs)

  def _pre_put_hook(self):  # pylint: disable=g-bad-name
    """Generate UUID for new entities."""
    super(BaseModel, self)._pre_put_hook()  # pylint: disable=protected-access
    self.GenerateKey()

  def _get_parent_key(self):
    """Returns a parent ndb.Key if a parent is specified in metadata."""
    parent_kind = metadata_api.GetParentKind(self)
    if parent_kind:
      parent_key_field = metadata_api.GetParentKeyField(self)
      parent_key_name = getattr(self, parent_key_field, None)
      if parent_key_name:
        return ndb.Key(parent_kind, parent_key_name)
    return None


class HashModelMixin(object):
  """Adds a hash_str property.

  The hash is the md5 hash of a str of the id concatenated with a set of
  properties.

  If HASH_PROPERTIES is defined (as a tuple of properties), only those
  properties will be included in the hash.

  If HASH_EXCLUDE is defined (as a tuple of properties), those properties will
  be skipped. If only HASH_EXCLUDE is defined, other properties will be added by
  default.  Whenever a HASH_EXCLUDE tuple is defined, "internal" DH properties
  appended to list to prevent them from ever being included in the hash
  calculation.

  If both HASH_PROPERTIES and HASH_EXCLUDE are defined and if a property is
  listed in both, the exclude wins.

  By default, no properties are included.
  """

  HASH_PROPERTIES = None
  HASH_EXCLUDE = None

  def _PropList(self):
    """Build a list of properties.

    Returns:
      list<str>, sorted list of property names.
    """
    prop_list = []

    if self.HASH_PROPERTIES is None and self.HASH_EXCLUDE is None:
      return prop_list

    # TODO(ckl): comprehensive list of "internal" properties
    exclude_list = self.HASH_EXCLUDE or tuple()
    exclude_list += metadata_api.GetFieldNames(self, ui_readonly=True)
    # TODO(raulg): The deleted can be removed from the exclude_list after all
    # records have been purged of deleted fields.
    exclude_list += ('deleted', 'key_subtype', 'key_order', 'key_name')

    for prop in self._properties:
      if '__' in prop and not prop.endswith('key_name'):
        continue
      if self.HASH_PROPERTIES is not None and prop not in self.HASH_PROPERTIES:
        continue
      if self.HASH_EXCLUDE is not None and prop in exclude_list:
        continue
      prop_list.append(prop)

    prop_list.sort()
    return prop_list

  def _Hash(self):
    """Build a md5 hash of a model.

    Returns:
      str, md5 hash of the model.
    """
    out = [self.key.string_id()]
    properties = self._PropList()
    for prop in properties:
      out.append(unicode(getattr(self, prop, '')))
    to_hash = ''.join(out)
    return hashlib.md5(to_hash.encode('utf-8')).hexdigest()

  @property
  def hash_str(self):
    """Concatenated str of kind, id, hash."""
    return '___'.join([self.key.kind(), self.key.string_id(),
                       self._Hash()])


# def ValidEmail(prop, value):
#   mail.check_email_valid(value, prop)
#
#
# class Report(ndb.Model):
#   name = ndb.StringProperty(required=True)
#   recipients = ndb.StringProperty(repeated=True, validator=ValidEmail)
#   sender = ndb.StringProperty(
#       default='reports@netdesign-prod.appspotmail.com', validator=ValidEmail)
#
#
# class DHReportModel(metadata_models.MetadataModel):
#   """Base Model for DH Report."""
#   report_type = ndb.StringProperty()
#   event_type = ndb.StringProperty()
#   timestamp = ndb.DateTimeProperty(auto_now_add=True)
#   data_kind = ndb.StringProperty()
#   data_key = ndb.StringProperty()
#   data_value = ndb.StringProperty()
#   quantity = ndb.IntegerProperty()
#   report_sequence = ndb.IntegerProperty()
