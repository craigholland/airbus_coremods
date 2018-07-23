"""Tools to work with files in the distribution bundle."""


import os

from _base.utils import constants


def OpenFile(filename):
  """Open filename.

  Args:
    filename: string, the relative path to the file from the server directory or
      the absolute path.

  Returns:
    file, the opened file object for filename.

  Raises:
    IOError
  """
  if os.path.isabs(filename):
    return open(filename)
  else:
    return open(os.path.join(constants.SERVER_PATH, filename))


def ReadFile(filename):
  """Get the string contents of filename.

  Args:
    filename: string, the relative path to the file from the server directory.

  Returns:
    string, the contents of filename.

  Raises:
    IOError
  """
  return OpenFile(filename).read()


def LocateMetadataYamlFiles():
  """Generates the paths of all metadata YAML files in the bundle."""
  for root, _, files in os.walk(constants.SERVER_PATH):
    for f in files:
      if f.endswith(constants.METADATA_FILE_END):
        relative_path = os.path.relpath(root, constants.SERVER_PATH)
        yield os.path.join(relative_path, f)


def ListMetadataYamlFiles():
  """Returns a list of the paths of all metadata YAML files in the bundle."""
  return list(LocateMetadataYamlFiles())
