"""Metadata pipelines."""

import logging

from protorpc import protojson
import webapp2

from google.appengine.api import app_identity
from google.appengine.ext import ndb

from google3.ops.netdeploy.netdesign.server.admin import setting_models
from google3.ops.netdeploy.netdesign.server.email import email_controller
from google3.ops.netdeploy.netdesign.server.errors import error_msg
from google3.ops.netdeploy.netdesign.server.logs import log_codes
from google3.ops.netdeploy.netdesign.server.logs import logs_api
from google3.ops.netdeploy.netdesign.server.metadata import metadata_api
from google3.ops.netdeploy.netdesign.server.metadata import metadata_controller
from google3.ops.netdeploy.netdesign.server.metadata import metadata_messages
from google3.ops.netdeploy.netdesign.server.utils import constants
from google3.ops.netdeploy.netdesign.server.utils import json_utils
from google3.ops.netdeploy.netdesign.server.utils import mapreduce_utils
from google3.ops.netdeploy.netdesign.server.utils import yaml_utils


def ReadMetadataFromFile(filename):
  """Read metadata from filename.

  Args:
    filename: string, the file to read from.

  Returns:
    dict: the metadata
  """
  metadata_json = json_utils.Dump(yaml_utils.LoadFromFile(filename))
  return protojson.decode_message(metadata_messages.Metadata, metadata_json)


def UpdateMetadataFromFiles(file_list, kind_set=None):
  """Update metadata from the YAML file for all members of UPDATED_METADATA.

  Args:
    file_list: dict of string:string, dict of kind:metadata-file
    kind_set: set of string, the set of known kinds. Defaults to all the kinds
        known in the system.

  Returns:
    Number of successful imports.
  """
  num_imports = 0
  if kind_set is None:
    kind_set = {k.kind for k in metadata_controller.List(kinds_only=True)}
  for kind, filename in file_list.iteritems():
    if kind in kind_set:
      try:
        errors, warnings = metadata_controller.Update(
            kind, ReadMetadataFromFile(filename))
        if errors:
          for msg in errors:
            logging.error(error_msg.MDP_ERROR_IMPORTING, kind, filename, msg)
            continue
        num_imports += 1
        logs_api.Info(log_codes.ADMIN_IMPORT_METADATA,
                      'Imported %s metadata from file "%s"' % (kind, filename))
        if warnings:
          for msg in warnings:
            logging.warning(
                error_msg.MDP_WARNING_IMPORTING, kind, filename, msg)
            continue
      except Exception as exc:  # pylint: disable=broad-except
        logging.error(error_msg.MDP_ERROR_READING, kind, filename, exc)
        continue
    else:
      logging.error(error_msg.MDP_KIND_DOES_NOT_EXIST, kind)
      continue
  return num_imports


class UpdateMetadataForReleasePipeline(mapreduce_utils.PipelineBase):
  """Update all metadata to the contents of the *_metadata.yaml file.

  This function is a backup, using a pipeline for doing the metadata update if
  it ever takes to long to do from the UI.
  """

  def run(self):
    with mapreduce_utils.PipelineRunManager(self):
      file_list = yaml_utils.LoadFromFile(constants.METADATA_FILE_LIST)
      UpdateMetadataFromFiles(file_list)


class UpdateMetadataForRelease(webapp2.RequestHandler):
  """Search ReIndex MapReduce Pipeline handler."""

  def get(self, *unused_args, **kwargs):
    """Starts a Pipeline to update metadata for the current release."""
    pipeline = UpdateMetadataForReleasePipeline()
    pipeline.start()
    body = ('UpdateMetadataForReleasePipeline Started: '
            '<a href="%s/status?root=%s">Status</a>' %
            (pipeline.base_path, pipeline.pipeline_id))
    self.response.write(body)


class CleanMetadataHandler(webapp2.RequestHandler):
  """Pipeline handler for sending email about deletable metadata."""

  def get(self, *unused_args, **unused_kwargs):  # pylint: disable=g-bad-name
    """Starts the pipeline and redirects to the status."""
    pipeline = CleanMetadataEmailPipeline()
    pipeline.start()
    body = ('CleanMetadataEmailPipeline Started: '
            '<a href="%s/status?root=%s">Status</a>' %
            (pipeline.base_path, pipeline.pipeline_id))
    self.response.write(body)


def SendCleanMetadataEmail(email_data):
  """Sends a clean metadata email.

  The email_data dict is expected to contain two entries: 'kinds' should be a
  list of string kind names that can be deleted, and 'apphost' should be the
  host name (e.g. netdesign-dev.googleplex.com) as a string.

  The kinds will be listed in an Unordered List element as hyperlinks to e.g.:
  https://<APPHOST>/admin/metadata/?name=<KIND>

  Args:
    email_data: dict, the data.
  """
  send_to = setting_models.Setting.get_by_id(
      constants.CLEAN_METADATA_EMAIL_RECIPIENTS)
  to_ = send_to and send_to.values_list or ['double-helix-team@google.com']
  email_controller.Notify(constants.CLEAN_METADATA, email_data, to_)


class CleanMetadataEmailPipeline(mapreduce_utils.PipelineBase):
  """Check all metadata and permission, remove those without entities."""

  EXCLUDED_KINDS = {'BaseModel'}

  def run(self):
    with mapreduce_utils.PipelineRunManager(self):
      apphost = app_identity.get_application_id()
      if apphost.startswith('google.com:'):
        apphost = apphost[11:]
      kinds = metadata_api.GetKindsAsync().get_result()

      # Fire off a bunch of async queries to see which still have entities.
      have_models = [(kind, ndb.Query(kind=kind).count_async(limit=1))
                     for kind in kinds if kind not in self.EXCLUDED_KINDS]

      # Wait on them and pass through the kinds that are "empty".
      expunge_us = [kind for kind, fut in have_models if not fut.get_result()]

      if expunge_us:
        SendCleanMetadataEmail({'kinds': expunge_us, 'apphost': apphost})
