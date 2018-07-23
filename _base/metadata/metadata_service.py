"""Metadata API definitions."""

import logging

import endpoints

from protorpc import message_types
from protorpc import messages
from protorpc import protojson
from protorpc import remote

from google3.ops.netdeploy.netdesign.server.common import common_service
from google3.ops.netdeploy.netdesign.server.errors import error_msg
from google3.ops.netdeploy.netdesign.server.logs import log_codes
from google3.ops.netdeploy.netdesign.server.logs import logs_api
from google3.ops.netdeploy.netdesign.server.metadata import metadata_controller
from google3.ops.netdeploy.netdesign.server.metadata import metadata_messages
from google3.ops.netdeploy.netdesign.server.metadata import metadata_utils
from google3.ops.netdeploy.netdesign.server.utils import authz
from google3.ops.netdeploy.netdesign.server.utils import json_utils
from google3.ops.netdeploy.netdesign.server.utils import message_utils
from google3.ops.netdeploy.netdesign.server.utils import model_utils
from google3.ops.netdeploy.netdesign.server.utils import yaml_utils


_SAMPLE = 'Sample'


def _IsValidKind(kind):
  """Make sure that only valid kinds are retrieved and updated."""
  if kind == _SAMPLE:
    return True
  kinds = metadata_controller.List(kinds_only=True)
  return kind in (k.kind for k in kinds)


def _KindEmpty(kind):
  """Return True if kind has no models."""
  model = model_utils.GetModel(kind)
  return model.query().count(limit=1) == 0


@common_service.api_root.api_class()
class MetadataService(remote.Service):
  """Metadata API service."""

  @endpoints.method(metadata_messages.DELETE_METADATA_REQUEST,
                    message_types.VoidMessage,
                    path='metadata/{kind}', http_method='DELETE',
                    name='metadata.delete')
  @authz.EndpointsLoginRequired
  def Delete(self, request):
    """Delete Metadata.

    Args:
      request: DELETE_REQUEST, The HTTP request.

    Returns:
      message_types.VoidMessage, Void.
    """
    kind = request.kind
    if not _IsValidKind(kind):
      error = error_msg.METADATA_NONEXIST % (kind,)
      raise common_service.ConflictException(error)
    if not _KindEmpty(kind):
      error = error_msg.METADATA_NONEMPTY % (kind,)
      raise common_service.ConflictException(error)
    metadata_controller.Delete(kind)
    return message_types.VoidMessage()

  @endpoints.method(metadata_messages.LIST_METADATA_REQUEST,
                    metadata_messages.ListMetadataResponse,
                    path='metadata', http_method='GET',
                    name='metadata.list')
  @authz.EndpointsLoginRequired
  def List(self, request):
    items = metadata_controller.List(request.kinds_only)
    return metadata_messages.ListMetadataResponse(items=items)

  @endpoints.method(metadata_messages.GET_METADATA_REQUEST,
                    metadata_messages.GetMetadataResponse,
                    path='metadata/{kind}', http_method='GET',
                    name='metadata.get')
  @authz.EndpointsLoginRequired
  def Get(self, request):
    if not _IsValidKind(request.kind):
      raise endpoints.NotFoundException
    metadata = metadata_controller.Get(request.kind)
    has_items = not _KindEmpty(request.kind)
    if request.yaml:
      try:
        metadata_json = protojson.encode_message(metadata)
        metadata_dict = message_utils.SortMessageDict(
            metadata_messages.Metadata, json_utils.Load(metadata_json))
        metadata_yaml = yaml_utils.Dump(metadata_dict)
      except (yaml_utils.YAMLError, messages.Error, ValueError) as exc:
        raise endpoints.InternalServerErrorException(str(exc))
      return metadata_messages.GetMetadataResponse(metadata_yaml=metadata_yaml,
                                                   has_items=has_items)
    return metadata_messages.GetMetadataResponse(metadata=metadata,
                                                 has_items=has_items)

  @endpoints.method(metadata_messages.UPDATE_METADATA_REQUEST,
                    metadata_messages.UpdateMetadataResponse,
                    path='metadata/{kind}', http_method='PUT',
                    name='metadata.update')
  @authz.EndpointsLoginRequired
  def Update(self, request):
    # TODO(davbennett): Perform additional validation of metadata format.
    if request.yaml and request.metadata_yaml:
      try:
        metadata_json = json_utils.Dump(yaml_utils.Load(request.metadata_yaml))
        metadata = protojson.decode_message(
            metadata_messages.Metadata, metadata_json)
      except Exception as exc:
        raise endpoints.BadRequestException(str(exc))
    # we don't want to fallback on metadata
    elif request.metadata and not request.yaml:
      metadata = request.metadata
    else:
      raise endpoints.BadRequestException('Metadata missing')

    # TODO(davbennett): Update TableView columns.
    return UpdateFromMetadataMessage(request.kind, metadata)


class MetadataAdminService(remote.Service):
  """Metadata admin services."""

  @remote.method(metadata_messages.UpdateFromFileRequest,
                 metadata_messages.UpdateMetadataResponse)
  def UpdateFromFile(self, request):
    """Update metadata from the YAML file."""
    message = 'Importing %s metadata from file "%s"' % (
        request.kind, request.filename)
    logging.info(message)
    logs_api.Info(log_codes.ADMIN_IMPORT_METADATA, message)
    try:
      metadata_json = json_utils.Dump(yaml_utils.LoadFromFile(request.filename))
      metadata = protojson.decode_message(
          metadata_messages.Metadata, metadata_json)
    except (yaml_utils.YAMLError, messages.Error, TypeError, IOError) as exc:
      raise endpoints.BadRequestException(str(exc))
    return UpdateFromMetadataMessage(request.kind, metadata)

  @remote.method(message_types.VoidMessage,
                 metadata_messages.ListFilesResponse)
  def ListFiles(self, request):
    file_list = metadata_utils.KindFilenameDict()
    if file_list is None:
      return metadata_messages.ListFilesResponse(pairs=[])
    pairs = [metadata_messages.MetadataFilePair(kind=kind, filename=filename)
             for kind, filename in file_list.iteritems()]
    return metadata_messages.ListFilesResponse(pairs=pairs)

  @remote.method(metadata_messages.GetMetadataFileRequest,
                 metadata_messages.GetMetadataResponse)
  def GetMetadataFile(self, request):
    """Get metadata from the YAML file."""
    filename = metadata_utils.KindFilenameDict().get(request.kind)
    if not filename:
      raise endpoints.BadRequestException(
          error_msg.NO_METADATA_FILE_FOR_MODEL % request.kind)
    try:
      yaml_map = yaml_utils.LoadFromFile(filename)
      metadata_yaml = yaml_utils.Dump(yaml_map)
    except (yaml_utils.YAMLError, TypeError, IOError) as exc:
      raise endpoints.BadRequestException(str(exc))
    return metadata_messages.GetMetadataResponse(metadata_yaml=metadata_yaml)


def UpdateFromMetadataMessage(kind, metadata):
  """Update metadata.

  Args:
    kind: string, the kind of model.
    metadata: metadata_messages.UpdateMetadataResponse, the new metadata.

  Returns:
    metadata_messages.UpdateMetadataResponse
  """
  # TODO(dgudeman): I think _IsValidKind() is too permissive. It should at least
  # require a subclass of MetadataModel and maybe it should be BaseModel.
  if not _IsValidKind(kind):
    error = error_msg.METADATA_NONEXIST % kind
    return metadata_messages.UpdateMetadataResponse(errors=[error])
  if kind.upper() == _SAMPLE.upper():
    raise endpoints.BadRequestException(error_msg.SAMPLE_UPDATE)
  errors, warnings = metadata_controller.Update(kind, metadata)
  response = metadata_messages.UpdateMetadataResponse(warnings=warnings)
  if errors:
    response.errors = errors
  return response
