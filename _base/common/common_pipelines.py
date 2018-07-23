"""Common Pipelines."""

import collections
import json
import logging

from google.appengine.ext import ndb

from google3.ops.netdeploy.netdesign.server.foreign_keys import fk_utils
from google3.ops.netdeploy.netdesign.server.netcracker import netcracker_sync
from google3.ops.netdeploy.netdesign.server.netcracker import netcracker_utils
from google3.ops.netdeploy.netdesign.server.utils import mapreduce_utils


class AggregateCountersPipeline(mapreduce_utils.PipelineBase):
  """Aggregate counter values."""

  def run(self, *args):
    """Aggregate counter values.

    Args:
      *args: dict, of counter names(str) and counter values(int, list).

    Returns:
      dict, the new dict with the al counters added together.
    """
    with mapreduce_utils.PipelineRunManager(self):
      list_out = collections.defaultdict(list)
      int_out = collections.defaultdict(int)

      for arg in args:
        if not arg:
          continue
        for k, v in arg.iteritems():
          if type(v) == int:
            int_out[k] += v
          elif type(v) == list:
            list_out[k].extend(v)
          else:
            try:
              if v:
                v_ = json.loads(v)
                if isinstance(v_, dict):
                  list_out[k].append(v_)
            except ValueError as ex:
              logging.warn('AggregateCountersPipeline, run error %s', ex)

      out = int_out.items()
      out.extend(list_out.items())
      return dict(out)


class CascadedUpdatesPipeline(mapreduce_utils.PipelineBase):
  """Pipeline to update all of an entity's children."""

  def run(self, urlsafe_key, field_mappings):
    """Update all of an entity's children direct or otherwise.

    Args:
      urlsafe_key: ndb.Key, the urlsafe key of the parent entity.
      field_mappings: dict, a mapping of the parent-child field relationships.
    """
    with mapreduce_utils.PipelineRunManager(self):
      entity_children_to_update = []
      entity = ndb.Key(urlsafe=urlsafe_key).get()
      for child_entity in fk_utils.GetAllChildEntities(entity):
        for parent_field, child_fields in field_mappings.iteritems():
          for field in child_fields:
            if hasattr(child_entity, field):
              setattr(child_entity, field, getattr(entity, parent_field))
              # Sometimes, a parent field name and its corresponding child field
              # name may be not be the same. The likelihood that one parent
              # field corresponds to multiple child fields is very low. Hence,
              # of the different possibilities defined in the values of
              # field_mappings it is safe to assume that if one child field is
              # set, the others can be ignored.
              break
        entity_children_to_update.append(child_entity)

        # pylint: disable=protected-access
        child_entity_kind = child_entity._get_kind()
        if child_entity_kind in netcracker_utils._MODEL_NAME_MAPPING.itervalues(
        ):
          nc_sync = netcracker_sync.SyncNetCracker2(child_entity_kind, 'Update')
          nc_sync(self._PutEntity)(child_entity)
        else:
          self._PutEntity(child_entity)
        # pylint: enable=protected-access

  def _PutEntity(self, entity):
    """Helper method for an ndb put_async operation.

    Args:
      entity: ndb.Model, the entity to be updated.

    Returns:
      The updated entity.
    """
    entity.put_async()
    return entity
