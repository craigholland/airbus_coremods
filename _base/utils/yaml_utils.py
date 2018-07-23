"""Utilities for working with YAML."""

import collections
import yaml

from _base.utils import bundle


YAMLError = yaml.YAMLError  # pylint: disable=g-bad-name


class OrderedDumper(yaml.SafeDumper):
  """Properly handles dumping OrderedDict instance properties in order."""

  def represent_ordered_dict(self, data):  # pylint: disable=g-bad-name
    """Ordered dict representation.

    Args:
      data: OrderedDict, the instance to map.

    Returns:
      The YAML mapping node.
    """
    return self.represent_mapping(u'tag:yaml.org,2002:map', data.items())

OrderedDumper.add_representer(
    collections.OrderedDict, OrderedDumper.represent_ordered_dict)


class OrderedLoader(yaml.SafeLoader):
  """Loads mappings into OrderedDict instances to preserve property order."""

  def construct_yaml_ordered_dict(self, node):  # pylint: disable=g-bad-name
    """Ordered dict constructor.

    Args:
      node: YAML node, The node to construct.

    Yields:
      An OrderedDict instance.
    """
    data = collections.OrderedDict()
    yield data
    data.update(self.construct_pairs(node))

OrderedLoader.add_constructor(
    u'tag:yaml.org,2002:map', OrderedLoader.construct_yaml_ordered_dict)


def Dump(obj, **kwargs):
  """Serialize a Python object into a YAML string.

  Produce only basic (safe) YAML tags.

  Args:
    obj: *, The object to serialize.
    **kwargs: dict, Inherited keyword arguments.

  Returns:
    The serialized YAML string.
  """
  kwargs.setdefault('default_flow_style', False)
  kwargs.setdefault('width', 10000)
  return yaml.dump_all([obj], Dumper=OrderedDumper, **kwargs)


def Load(data):
  """Parse a YAML string or file and produce a Python object.

  Resolve only basic (safe) YAML tags.

  Args:
    data: string or opened file, The YAML string or file to deserialize.

  Returns:
    The corresponding Python object.
  """
  return yaml.load(data, Loader=OrderedLoader)


def LoadFromFile(path):
  """Loads metadata from the YAML file at path.

  Args:
    path: string, path name of the YAML file.

  Returns:
    The corresponding Python object.
  """
  return Load(bundle.OpenFile(path))
