"""Common Datapropagation for Double Helix app."""

import datetime
import inspect
import json

from google3.ops.netdeploy.netdesign.server.common import common_models
from google3.ops.netdeploy.netdesign.server.errors import error_collector
from google3.ops.netdeploy.netdesign.server.errors import error_msg
from google3.ops.netdeploy.netdesign.server.metadata import metadata_api
from google3.ops.netdeploy.netdesign.server.metadata import metadata_messages
from google3.ops.netdeploy.netdesign.server.metadata import metadata_models
from google3.ops.netdeploy.netdesign.server.utils import constants


class DataPropagation(object):
  """Class used to assign Triggers and Authoritative Sources to Fields.

  Definitions
    Trigger:  A server-side "event listener" assigned to a specific field of a
              model that when the field value changes, a pre-defined set of
              functions are executed (assuming the parameters of the "event"
              are fulfilled).

    Authoritative Source:
              A designation assigned to a specific field of a model that
              indicates the field derives its value from a field of another
              model. This relationship can be:
                  * Direct - a 1:1 relationship where the values are identical
                            between the target field and Authoritative Source.
                            (Ex: a foreign key relationship)
                  * Computed - The target field value is calculated based on
                            the value of the Authoritative Source. (Ex:
                            PowerRollUp, where the power consumption values of
                            a Device is an aggregate of the power consumption
                            values of its constituent Parts/Devices.
  """

  class Jobs(object):
    """Organizes the Job Queue for Triggers and Authoritative Sources.

    As a Trigger or Authoritative Source is discovered in the model and found
    to be "activated", a job package is created and placed in a queue.  Once
    the model is fully scanned, then all jobs in the queues are handled.

    Format of Job Queues:
      (<trigger object>, val)  - where 'val' is the new, updated value
    """

    def __init__(self):
      self.trigger_queue = []
      self.authoritativesource_queue = []

    def ClearJobs(self, job_type=None):
      """Clears all Jobs queues, unless job_type is specified.

      Args:
        job_type: str, None, Job Queue to be cleared (opt: None,
          'trigger_queue', or 'authoritativesource_queue').

      Returns:
        bool, returns True if Job Queues were cleared. Otherwise, False.
      """
      if job_type:
        if hasattr(self, job_type):
          setattr(self, job_type, [])
          return True
      else:
        self.trigger_queue = []
        self.authoritativesource_queue = []
        return True
      return False

  class Functions(object):
    """Subclass that locally-defined DP functions get imported into.
    """

    def __init__(self):
      self.listall = []

  class Errors(error_collector.Errors):
    """DP-specific Error-handling subclass."""

    def __init__(self):
      super(DataPropagation.Errors, self).__init__()
      self.error_count = 0

    def Add(self, key, message, *messages):
      self.error_count += 1
      super(DataPropagation.Errors, self).Add(key, message, *messages)

    def Clear(self):
      self.error_count = 0
      self._errors.clear()

  def LoadLocalFunctions(self, cls, prefix):
    """Imports local functions from subclass.  Referenced by local DP subclass.

    Where:
      DP := Parent DataPropagation object
      CH := Child DataPropagation object (e.g. - Device_DataPropagation())

    The purpose of this is mainly to keep model-specific code easier to
      maintain as it will be distributed to the local CH classes and leave
      the DP code untouched as DataPropagation grows and gets implemented.

    Methods defined in CH that are used for model-specific data propagation
    are identified by the naming convention: <prefix> + <function name>().
    These functions are imported into: DP.Functions.<function name> and
    are then more easily-executed from high-level DP methods responsible for
    controlling the general flow of Trigger/Authoritative_Source operations.

    Ex: (very generic)
      DP(object):
        ~~Parent DP object~~

      CH(DP):
        prefix = "test__"

        def __init__(self):
           super(CH, self).__init__(entity_or_model)
           self.LoadLocalFunctions(self, self.prefix)

        def test__ThisFunctionImported(self):
          pass

        def ThisFunctionNotImported(self):
          pass

      Now, as DP compiles the Trigger Jobs needing to be executed, the
      necessary functions are run by: DP.Functions.<function_name>.

    Args:
      cls: class, initiating subclass of DataPropagation parent.
      prefix: str, naming convention used to identify which methods to import.
    """

    for method in inspect.getmembers(cls):
      if method[0].startswith(prefix):
        new_function_name = method[0][len(prefix):]
        setattr(self.functions, new_function_name, getattr(cls, method[0]))
        self.functions.listall.append(new_function_name)

  def LoadTriggerMap(self):
    """Loads Trigger Map from subclass.

    Trigger Map is a local JSON file that is a dict of dicts that maps Trigger
    Names to the primary function defined in the model-specific DP object (e.g.-
    Device_DataPropagation) that performs the required tasks.

    The file has the following format:
    Key: <Trigger Name>
    Value: dict: {
      "local_function_name" : str, method name to be imported from Child object,
      "base_function_name"  : str, method name as it will be saved in DP object,
      "description" : str, brief description/purpose of Trigger
    }

    Ex:
      {
        "TestTrigger_A": {
          "local_function_name": "localDP_FunctionName1",
          "base_function_name": "FunctionName1",
          "description": "Description of TestTrigger_A"
        },

        "TestTrigger_B": {
          "local_function_name": "localDP_FunctionName2",
          "base_function_name": "FunctionName2",
          "description": "Description of TestTrigger_B"
        }
      }
    """

    with open(self.trigger_map_location) as f:
      self.trigger_map = json.load(f)

  def __init__(self, entity_or_model):
    self.is_entity = self._IsBaseModelSub(entity_or_model)
    self.properties = metadata_api.GetFieldNames(entity_or_model)

    if self.is_entity:
      self.entity = entity_or_model
      # pylint: disable=protected-access
      self.model = entity_or_model._lookup_model(entity_or_model.key.kind())
      # pylint: enable=protected-access
    else:
      self.entity = None
      self.model = entity_or_model

    self.kind = self.model._get_kind()  # pylint: disable=protected-access
    self.meta = self.model._meta  # pylint: disable=protected-access

    self.active_trigger_list = []

    self.trigger_object = None
    self.new_value = None

    self.trigger_map_location = None
    self.trigger_map = None

    self.subclass_name = None

    self._HasActiveTriggers()
    self.jobs = self.Jobs()
    self.functions = self.Functions()
    self.errors = self.Errors()

  @property
  def has_active_triggers(self):
    return self._HasActiveTriggers()

  def ValidateTrigger(self, field, trigger_object):
    """Rules for Triggers.

    Test for exceptions, otherwise return True.

    Args:
      field: str, Field the Trigger is being assigned to.
      trigger_object: Metadata.Messages.DataPropagationTrigger class, trigger
        object to be added.

    Returns:
      bool
    """
    # Trigger cannot target itself.
    if (trigger_object.target_kind == self.kind
       ) and (trigger_object.target_field == field):
      self.errors.Add(
          error_msg.ERRORKEY_BADTRIGGER, error_msg.ERRORMSG_SELFTRIGGER % field)
      return False

    # Trigger Field not found.
    if field not in self.properties:
      self.errors.Add(
          error_msg.ERRORKEY_BADTRIGGER,
          error_msg.ERRORMSG_FIELDNOTFOUND  % (field, self.kind))
      return False

    # Trigger already exists for assigned field.
    if trigger_object in self._GetMetaByFieldName(
        field, constants.DPMETA_TRIGGER):
      self.errors.Add(
          error_msg.ERRORKEY_BADTRIGGER,
          error_msg.ERRORMSG_TRIGGERNAMEEXISTS % (
              trigger_object.trigger_name, self.kind, field))
      return False
    return True

  def CreateTriggerObject(
      self, t_name, t_kind, t_field, kwargs=None, event_type=None):
    """Returns Trigger Object given name, target_kind, and target_field inputs.

    Args:
      t_name: str, Trigger Name - name of Trigger found in Trigger Map.
      t_kind: str, Target Kind - kind/model of Target.
      t_field: str, Target Field - field name of Target.
      kwargs: dict, (optional, default: empty dict) - dict object containing
       additional values to be passed to local functions.
      event_type: str, (optional, default: 'value_changed') - type of trigger
       event to listen for.

    Returns:
      metadata_messages.DataPropagationTrigger object.

    """
    if kwargs is None:
      kwargs = {}
    return metadata_messages.DataPropagationTrigger(
        event_type=event_type,
        trigger_name=t_name,
        target_kind=t_kind,
        target_field=t_field,
        opt_kwargs=self._ConvertKwargs(kwargs))

  def AddTriggerObject(self, field, trigger_object):
    """Validates and Adds trigger to DP object (but not committed to Meta).

    Args:
      field: str, name of field to attach Trigger to.
      trigger_object: metadata_messages.DataPropagationTrigger, the trigger.
    """
    if self.ValidateTrigger(field, trigger_object):
      existing_trigger = self._GetMetaByFieldName(
          field, constants.DPMETA_TRIGGER)
      existing_trigger.append(trigger_object)
    self._HasActiveTriggers()

  def DeleteTriggerObject(self, field, trigger_name):
    """Removes trigger from DP object.

    Args:
      field: str, name of field to detach Trigger from.
      trigger_name: str, name of trigger_object to remove.
    """
    existing_triggers = self._GetMetaByFieldName(
        field, constants.DPMETA_TRIGGER)
    for idx, trigger_object in enumerate(existing_triggers):
      if trigger_object.trigger_name == trigger_name:
        existing_triggers.pop(idx)
    self._HasActiveTriggers()

  def UpdateMeta(self):
    """Syncs DP.Meta with Model Meta.

    Args:
      None
    Returns:
      bool, Returns True upon successful completion of update.
    """
    if not self.errors:
      metadata_api.ApplyModelDefinedMetadata(self.kind, self.meta)
      return True
    return False

  def TriggerToJobQueue(self, updated_entity):
    """Checks an entity for triggers and stores in self.jobs.trigger_queue.

    Args:
      updated_entity: entity, dict, entity to be analyzed.
    """
    updated_entity_dict = updated_entity if isinstance(
        updated_entity, dict) else updated_entity.to_dict()

    if self.entity and self.trigger_map:
      entity_dict = self.entity.to_dict()
      for trigger_field in self.active_trigger_list:
        trigger_object_list = self._GetMetaByFieldName(
            trigger_field, constants.DPMETA_TRIGGER)
        for trigger_object in trigger_object_list:
          if self._TestTrigger(
              trigger_object, entity_dict,
              updated_entity_dict, trigger_field):
            job = (trigger_object, updated_entity_dict[trigger_field])
            if job not in self.jobs.trigger_queue:
              self.jobs.trigger_queue.append(job)

    elif self.trigger_map:
      self.errors.Add(
          error_msg.ERRORKEY_BADTRIGGER, error_msg.ERRORMSG_CANTINITIATE)
    else:
      self.errors.Add(error_msg.ERRORKEY_BADTRIGGER, error_msg.ERRORMSG_NOMAP)

  def InitiateTriggers(self):
    """Initiates triggers found in self.jobs.trigger_queue."""

    if self.jobs.trigger_queue:
      for trigger_object, new_value in self.jobs.trigger_queue:
        self.trigger_object, self.new_value = trigger_object, new_value
        if trigger_object.trigger_name in self.trigger_map:
          local_function_name = self.trigger_map[
              trigger_object.trigger_name]['base_function_name']
          run_function = self._GetLocalFunction(local_function_name)
          run_function()

  def _HasActiveTriggers(self):
    """Returns boolean if model/entity contains field that has defined Triggers.

    Also used to build/re-build self.active_trigger_list.

    Returns:
      bool
    """
    field_list = []
    for prop in self.properties:
      if self._GetMetaByFieldName(prop, constants.DPMETA_TRIGGER):
        field_list.append(prop)

    self.active_trigger_list = field_list

    if field_list:
      return True
    else:
      return False

  def _GetDPEventTypeByName(self, event_type):  # pylint: disable=g-bad-name
    """Returns Messages.DataPropagationEventType object by name.

    Args:
      event_type: str, name of event_type.

    Returns:
      metadata_messages.DataPropagationEventType.
    """
    return metadata_messages.DataPropagationEventType(event_type)

  def _GetMetaByFieldName(self, field_name, meta_field=None):
    """Returns Metadata for specific field of a model.

    If meta_field = None, return all Meta

    Args:
      field_name: str, name of model field.
      meta_field: str, specific meta field relative to model field.

    Returns:
      meta_value: str, bool, int, float, dict

    """
    meta = metadata_models.metadata_utils.GetFieldByName(self.meta, field_name)
    # pylint: disable=protected-access
    if meta_field and meta_field in meta._Message__by_name:
      meta_value = getattr(meta, meta_field)
    elif meta_field is None:
      meta_value = {}
      for prop in meta._Message__by_name.iteritems():
        meta_value[prop] = getattr(meta, prop)
    else:
      meta_value = None
    # pylint: enable=protected-access
    return meta_value

  def _ConvertKwargs(self, old_kwargs, to_json=True):
    """Encodes/Decodes Kwargs between dict and JSON strings.

    Metadata_messages can not handle dict objects, so kwarg dicts need to be
    converted to JSON strings to be saved in the Message.
    Likewise, stored JSON strings need to be reconverted back to dict objects.

    Args:
      old_kwargs: dict or stringified dict, kwargs to be added to trigger
        object.
      to_json: bool, direction of conversion.

    Returns:
      kwargs: dict or stringified dict, converted kwargs.
    """

    def _Byteify(data, ignore_dicts=False):
      """Simple utility to convert unicode to str during JSON conversions.

      Args:
        data: unicode, list, dict - data to analyze.
        ignore_dicts: bool, flag to ignore dict objects.

      Returns:
        converted data
      """

      # If this is a unicode string, return its string representation.
      if isinstance(data, unicode):
        return data.encode('utf-8')
      # If this is a list of values, return list of byteified values.
      if isinstance(data, list):
        return [_Byteify(item, ignore_dicts=True) for item in data]
      # If this is a dictionary, return dictionary of byteified keys and values
      # but only if we haven't already byteified it.
      if isinstance(data, dict) and not ignore_dicts:
        return {
            _Byteify(key, ignore_dicts=True):
                _Byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
      # If it's anything else, return it in its original form.
      return data

    if to_json:
      if not isinstance(old_kwargs, dict):
        self.errors.Add(
            error_msg.ERRORKEY_BADTRIGGER, error_msg.ERRORMSG_BADKWARGFORMAT)
        old_kwargs = {}
      kwargs = json.dumps(old_kwargs)

    else:
      kwargs = json.loads(old_kwargs)
      if not isinstance(kwargs, dict):
        self.errors.Add(
            error_msg.ERRORKEY_BADTRIGGER, error_msg.ERRORMSG_BADKWARGFORMAT)
        kwargs = {}
      kwargs = _Byteify(kwargs)

    return kwargs

  def _DecomposeTrigger(self, trigger_object):
    """Returns tuple of all Trigger Object properties.

    (Reverse of createTriggerObject)
    Args:
      trigger_object: Metadata.Messages.DataPropagationTrigger class.

    Returns:
      tuple, properties of Trigger object.
    """
    return (trigger_object.trigger_name,
            trigger_object.target_kind,
            trigger_object.target_field,
            self._ConvertKwargs(trigger_object.opt_kwargs, False),
            trigger_object.event_type)

  def _GetLocalFunction(self, function_name):
    return getattr(self.functions, function_name)

  def _IsNumericTypeCheck(self, val):
    """Checks to ensure input value is numeric or datetime type.

    Also checks to see if input value is a string that is able to be
      converted to acceptable types.

    Args:
      val: any, value to be checked.

    Returns:
      bool
    """

    allowable_types = (int, float, complex, long,
                       datetime.date, datetime.time)

    # TODO(hollandc): Add functionality to test for convertible strings.
    return True in [isinstance(val, val_type) for val_type in allowable_types]

  def _TestTrigger(self, trigger_object, old_entity_dict,
                   new_entity_dict, field_name):
    """Given old and new entities, test to see if trigger is activated.

    Will return False (no Trigger activated) unless a specific test is True for
      a specific event_type.

    Args:
      trigger_object: Metadata_messages.DataPropagationTrigger class, trigger
        object to be tested.
      old_entity_dict: dict, dict object of existing entity.
      new_entity_dict: dict, dict object of proposed updated entity.
      field_name: str, field name found in entities associated with Trigger.

    Returns:
      bool

    """
    event_type = trigger_object.event_type.name
    # Get field values from old and new entities.
    old_value = None if field_name not in old_entity_dict else old_entity_dict[
        field_name]
    new_value = None if field_name not in new_entity_dict else new_entity_dict[
        field_name]

    # Test trigger depending on Event Type.
    if event_type == constants.DPEVENT_VALUECHANGED:
      # Test for change in values.
      if old_value != new_value:
        return True
    elif event_type == constants.DPEVENT_VALUEADD:
      # Test for a value being added to the entity field.
      if old_value is None and new_value is not None:
        return True
    elif event_type == constants.DPEVENT_VALUEDEL:
      if old_value is not None and new_value is None:
        # Test for a value being removed from an entity field.
        return True
    elif self._IsNumericTypeCheck(
        old_value) and self._IsNumericTypeCheck(new_value):
      if event_type == constants.DPEVENT_VALUEDEC:
        # Test for a decrease in value
        if old_value > new_value:
          return True
      elif event_type == constants.DPEVENT_VALUEINC:
        # Test for an increase in value
        if old_value < new_value:
          return True
    return False

  def _IsBaseModelSub(self, cls):
    """Returns True if cls is instance of a BaseModel, False if entity."""
    return isinstance(cls, common_models.BaseModel)


