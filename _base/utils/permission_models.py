"""Model definitions for permissions app.

Permissions are either kind wide or column wide.
"""

import enum

from google.appengine.ext import ndb

from _base.utils import model_utils


# TODO(rupalig): Update metadata to use the choices field for access type.
@enum.unique
class AccessType(enum.Enum):
  """Enum representing permission access types."""
  FIELD_READ_WRITE = 'field_read_write'
  FIELD_WRITE_ONLY = 'field_write_only'
  TABLE_READ_WRITE = 'table_read_write'
  TABLE_WRITE_ONLY = 'table_write_only'
  NONE = 'none'


class PermissionType(ndb.Model):
  """Permission type definitions.

  This model serves as a structured property for Permission model.

  Attributes:
    column: str, The name of the column.
    read: list of str, nicknames of users or groups allowed to read allowed to
        read this column. Groups are prefixed by '%'. There is a special group
        %everyone that allows anyone access.
    write: list of str, same format as read but for write permissions.
  """
  column = ndb.StringProperty(required=True)
  read = ndb.StringProperty(repeated=True)
  write = ndb.StringProperty(repeated=True)


class Permission(ndb.Model):
  """Permissions definitions.

  Attributes:
    model_name: str, The Model/Kind name the permission is for.
        This parameter is also used as the id.
    default: PermissionType, Permission used for any column not explicitly
        listed in columns.
    columns: list of PermissionType, Explicit permissions on columns.
  """
  model_level_read = ndb.StringProperty(repeated=True)
  model_level_write = ndb.StringProperty(repeated=True)
  # The possible values of access_type are defined in AccessType enum.
  access_type = ndb.StringProperty()
  model_name = ndb.StringProperty(required=True)
  default = model_utils.DHJsonProperty(required=True)
  columns = model_utils.DHJsonProperty(repeated=True)

  def _pre_put_hook(self):  # pylint: disable=g-bad-name
    """Sets the key_name to model_name."""
    key_name = self.model_name
    self.key = ndb.Key(self.__class__.__name__, key_name)
