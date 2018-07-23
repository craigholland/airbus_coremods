"""Metadata models for Double Helix app.

Subclasses of MetadataModel will get a thread-local "_meta" object that contains
all metadata for that model.

Defaults can be set by defining a "class Meta(object):" inside the subclass.

Example:

  class MyModel(metadata_models.MetadataModel):

    my_property = ndb.StringProperty()

    class Meta(object):
      ui_readonly = True
      fields = {
          'my_property': {
              'index_for_search': False,
          },
      }

See MetadataField and Metadata class in metadata_messages for all possible
metadata settings.
"""

import cPickle as pickle
import logging

from google.appengine.api import datastore_errors
from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop

from _base.metadata import metadata_messages
from _base.metadata import metadata_utils
from _base.utils import request_state
from _base.utils import signals


# Global mapping of metadata kinds to model classes.
METADATA_KIND_MAP = {}
# Global mapping of metadata defaults.
METADATA_DEFAULTS = {}


class Metadata(signals.SignalMixin, ndb.Model):
  """Storage for model metadata."""

  # Key version for tracking history. This field should not be modified.
  key_version = ndb.IntegerProperty()

  metadata = msgprop.MessageProperty(
      metadata_messages.Metadata, required=True, protocol='protojson',
      indexed_fields=['kind', 'fields.name'],
      validator=metadata_utils.ValidateMetadata)

  def _prepare_for_put(self):  # pylint: disable=g-bad-name
    """Override key to use model kind as ID."""
    self.key = ndb.Key(self._get_kind(), self.metadata.kind)
    super(Metadata, self)._prepare_for_put()

  def _put_async(self, **ctx_options):  # pylint: disable=invalid-name
    """Back up metadata."""
    ctx_options['backup'] = ctx_options.get('backup', True)
    return super(Metadata, self).put_async(**ctx_options)


class MetadataMetaModel(ndb.MetaModel):
  """Metaclass for MetadataModel.

  This metaclass provides a thread-local "_meta" property to model classes. The
  metadata is loaded from the datastore the first time it is accessed in a
  request/thread.

  If a model class has a nested class named "Meta", it will be used for defaults
  and will override any settings defined in the datastore. But note that any
  properties defined directly on a model will always override primary metadata
  from both datastore and Meta classes.

  Settings defined in "Meta" will be inherited by model subclasses, but any
  datastore settings or thread-local changes to a parent "_meta" property will
  not affect subclasses.
  """

  # This is a metaclass, so...
  # pylint: disable=bad-classmethod-argument,no-self-argument
  def __new__(mcs, name, bases, classdict):
    """Adds metadata models to a registry along with their static options."""
    meta_cls = classdict.pop('Meta', None)
    cls = super(MetadataMetaModel, mcs).__new__(mcs, name, bases, classdict)
    kind = cls._get_kind()  # pylint: disable=protected-access
    METADATA_KIND_MAP[kind] = cls
    if meta_cls is not None:
      METADATA_DEFAULTS[kind] = {k: v for k, v in vars(meta_cls).iteritems()
                                 if not k.startswith('_')}
    return cls

  @property
  def _meta(cls):
    """Lazy-loads thread-local model metadata."""
    kind = cls._get_kind()  # pylint: disable=protected-access
    rs = request_state.GetRequestState('metadata')
    metadata = rs.get(kind)
    if metadata is None:
      # Avoid circular import, pylint: disable=g-import-not-at-top
      from _base.metadata import metadata_api
      # pylint: enable=g-import-not-at-top
      metadata = metadata_api.GetMetadata(kind)
      rs[kind] = metadata
    return metadata

  @_meta.setter
  def _meta(cls, metadata):
    """Overrides thread-local model metadata. If a dict, it's merged instead."""
    kind = cls._get_kind()  # pylint: disable=protected-access
    if isinstance(metadata, dict):
      metadata_utils.UpdateMetadata(cls._meta, metadata)
    else:
      rs = request_state.GetRequestState('metadata')
      rs[kind] = metadata


# Create a mapping of field property types to _db_get_value methods.
# The _db_get_value method should probably be a @staticmethod (it doesn't use
# "self"), but since it isn't, im_func is used to get the unbound function.
_DB_GET_VALUE_MAP = {
    k: v._db_get_value.im_func  # pylint: disable=protected-access
    for k, v in metadata_messages.PROPERTY_MAP.iteritems()
    if not issubclass(v, (ndb.GenericProperty, ndb.StructuredProperty))
}


class MetadataModel(signals.SignalMixin, ndb.Model):
  """A base class for models defined by metadata.

  This class is essentially a clone of ndb.Expando, but requires properties to
  be defined in metadata.
  """

  __metaclass__ = MetadataMetaModel

  def _set_attributes(self, keywords):
    """Sets any keyword properties when the model is instantiated.

    This is called by __init__() and populate(), and is overridden to allow
    adding arbitrary properties.

    Args:
      keywords: dict, mapping of property names to values.
    """
    for name, value in keywords.iteritems():
      setattr(self, name, value)

  def _check_initialized(self, ignore=True):
    """Internal helper to check for uninitialized properties.

    Args:
      ignore: boolean, whether to ignore uninitialized properties (an error will
          still be logged).

    Raises:
      BadValueError if any uninitialized properties are found and ignore is set
      to False.
    """
    try:
      super(MetadataModel, self)._check_initialized()
    except datastore_errors.BadValueError as e:
      logging.error('%s: %s', self.key, e)
      if not ignore:
        raise

  def _pre_put_hook(self):
    """Checks for uninitialized required properties."""
    super(MetadataModel, self)._pre_put_hook()
    self._check_initialized(ignore=False)

  @classmethod
  def _unknown_property(cls, name):
    """Internal helper to handle an unknown property name.

    This is called by _check_properties() and is overridden to allow arbitrary
    property names.

    Args:
      name: str, the property name to check.
    """
    pass

  def _to_dict(self, include=None, exclude=None):
    """Initializes metadata properties before converting to dict."""
    self._populate_properties()
    return super(MetadataModel, self)._to_dict(include=include, exclude=exclude)
  to_dict = _to_dict

  def _prepare_for_put(self):
    """Initializes metadata properties before saving to datastore."""
    self._populate_properties()
    super(MetadataModel, self)._prepare_for_put()

  def _populate_properties(self):
    """Initializes metadata properties."""
    missing = []
    for field in self._meta.fields:
      prop = self._properties.get(field.name)
      if prop is None or (
          type(prop) != metadata_messages.PROPERTY_MAP[field.property_type]):
        missing.append(field)
    if missing:
      self._clone_properties()
      for field in missing:
        prop = metadata_utils.GetFieldProperty(field)
        if prop:
          self._properties[field.name] = prop

  def _clone_meta(self):
    """Helper to clone self._meta if necessary.

    Call this before mutating _meta if you want the changes to only affect a
    single model instance.

    Note: This method uses PEP-8 naming to be consistent with _clone_properties.
    """
    cls_meta = self.__class__._meta  # pylint: disable=protected-access
    if self._meta is cls_meta:
      # cPickle is considerably faster than both copy.deepcopy and protojson.
      self._meta = pickle.loads(pickle.dumps(cls_meta, pickle.HIGHEST_PROTOCOL))

  def __getattr__(self, name):
    """Returns a metadata-defined property value."""
    if name == '_meta':
      return self.__class__._meta  # pylint: disable=protected-access
    if name.startswith('_'):
      return super(MetadataModel, self).__getattr__(name)
    prop = self._properties.get(name)
    if prop is None:
      if metadata_utils.GetFieldByName(self._meta, name) is not None:
        return  # Don't fail if the property hasn't been created yet.
      return super(MetadataModel, self).__getattribute__(name)
    return prop._get_value(self)  # pylint: disable=protected-access

  def __setattr__(self, name, value):
    """Sets a metadata-defined property value."""
    if name == '_meta' and isinstance(value, dict):
      self._clone_meta()
      return metadata_utils.UpdateMetadata(self._meta, value)
    attr = getattr(self.__class__, name, None)
    if name.startswith('_') or isinstance(attr, (ndb.Property, property)):
      if not isinstance(attr, ndb.ComputedProperty):
        super(MetadataModel, self).__setattr__(name, value)
      return
    self._clone_properties()
    field = metadata_utils.GetFieldByName(self._meta, name)
    repeated = isinstance(value, list)
    # Foreign Key propagation needs to be able to dynamically change the
    # repeated flag on a property.
    if field is None or field.repeated != repeated:
      defaults = {'repeated': repeated}
      if isinstance(value, (ndb.Model, dict)) or (
          repeated and value and isinstance(value[0], (ndb.Model, dict))):
        defaults['property_type'] = metadata_messages.PropertyType.STRUCT
      self._meta = {'fields': {name: defaults}}
      field = metadata_utils.GetFieldByName(self._meta, name)
    prop = metadata_utils.GetFieldProperty(field)
    if prop:
      self._properties[name] = prop
      prop._set_value(self, value)  # pylint: disable=protected-access

  def __delattr__(self, name):
    """Deletes a metadata-defined property value."""
    if (name.startswith('_') or isinstance(
        getattr(self.__class__, name, None), (ndb.Property, property))):
      return super(MetadataModel, self).__delattr__(name)
    prop = self._properties.get(name)
    if not isinstance(prop, ndb.Property):
      raise TypeError('Model property "%s" must be Property instance; '
                      'not %r (%s)' % (name, prop, type(prop)))
    prop._delete_value(self)  # pylint: disable=protected-access
    if prop in self.__class__._properties:  # pylint: disable=protected-access
      raise RuntimeError('Property %s still in the list of properties for the '
                         'base class.' % name)
    del self._properties[name]  # pylint: disable=protected-access
