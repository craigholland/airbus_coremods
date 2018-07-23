"""Common ProtoRPC messages."""

import endpoints
from protorpc import message_types
from protorpc import messages

# pylint: disable=invalid-name

# Override the default package name exposed to clients.
package = 'common'


class GenericModel(messages.Message):
  """A generic model message."""
  id = messages.StringField(1, required=True)
  kind = messages.StringField(2, required=True)


class JsonMessage(messages.Message):
  """A container for JSON encoded objects."""
  json = messages.StringField(1, required=True)


def DefaultListParams(max_results_default=None):
  """Default URL parameters that should be implemented on every list method.

  Corresponds to the required messages in the Apiary URL Parameter Guide:
  http://sites/building-an-api/design/apiaryrestyle/urlparameters

  Args:
    max_results_default: int, default for maxResults parameter.

  Returns:
    dict, default fields to be used with endpoints.ResourceContainer.
  """
  return {
      # Search String.
      'q': messages.StringField(1001),
      # Continuation Token.
      'pageToken': messages.StringField(1002),
      # Max number of results to return
      'maxResults': messages.IntegerField(1003, default=max_results_default),
      # Field to order results by.
      'orderBy': messages.StringField(1004),
      # Used with orderBy, ascending or descending.
      'sortOrder': messages.StringField(1005),
      # RFC 3339 Date(not datetime).
      'publishedMin': messages.StringField(1006),
      # RFC 3339 Date(not datetime).
      'publishedMax': messages.StringField(1007),
      # RFC 3339 Date(not datetime).
      'updatedMin': messages.StringField(1008),
      # RFC 3339 Date(not datetime).
      'updatedMax': messages.StringField(1009),
      'filterFields': messages.StringField(1010, repeated=True),
      'planDate': messages.StringField(1011)
  }


# Message for list operations.
LIST_REQUEST = endpoints.ResourceContainer(
    **DefaultListParams(max_results_default=250))


class ListResponse(messages.Message):
  """A general response for the LIST_REQUEST."""
  # The ID for the collection.
  id = messages.StringField(1, required=True)
  # The collection kind.
  kind = messages.StringField(2, required=True)
  # Continuation Token, blank if no more results.
  nextPageToken = messages.StringField(3)
  # List of items in the collection.
  items = messages.MessageField(GenericModel, 4, repeated=True)
  # Number of Items in the response.
  currentItemCount = messages.IntegerField(5, variant=messages.Variant.UINT32)
  # The max number of results per page for the request.
  itemsPerPage = messages.IntegerField(6, variant=messages.Variant.UINT32)


ID_MODEL_REQUEST = endpoints.ResourceContainer(
    id=messages.StringField(1, required=True),
    model=messages.StringField(2, required=True))


ALL_REQUEST = endpoints.ResourceContainer(
    model=messages.StringField(1, required=True),
    name=messages.StringField(2),
    keySubtype=messages.StringField(3),
    alias=messages.StringField(4),
    **DefaultListParams(max_results_default=250))


AUTO_COMPLETE_REQUEST = endpoints.ResourceContainer(
    keyword=messages.StringField(1, required=True),
    model=messages.StringField(2, required=True),
    **DefaultListParams())


ID_REQUEST = endpoints.ResourceContainer(
    id=messages.StringField(1, required=True))


class AutoCompleteResponse(messages.Message):
  id = messages.StringField(1)
  name = messages.StringField(2)


class AutoCompleteResponses(messages.Message):
  id = messages.StringField(1)
  items = messages.MessageField(AutoCompleteResponse, 2, repeated=True)
  kind = messages.StringField(3)
  itemsPerPage = messages.IntegerField(4, variant=messages.Variant.UINT32)
  currentItemCount = messages.IntegerField(5, variant=messages.Variant.UINT32)
  more = messages.BooleanField(6)


class ErrorDetail(messages.Message):
  """Single error message.

  Corresponds to the error message format in the JSON style guide:

  http://google-styleguide.googlecode.com/svn/trunk/jsoncstyleguide.xml
  """
  field = messages.StringField(1)
  message = messages.StringField(2, repeated=True)


class ErrorResponse(messages.Message):
  """Single error message.

  Corresponds to the error message format in the JSON style guide:

  http://google-styleguide.googlecode.com/svn/trunk/jsoncstyleguide.xml
  """
  message = messages.MessageField(ErrorDetail, 1, repeated=True)
  values = messages.StringField(2)


class ErrorsResponse(messages.Message):
  """Wrapper for all error messages.

  Corresponds to the error message wrapper format in the JSON style guide:

  http://google-styleguide.googlecode.com/svn/trunk/jsoncstyleguide.xml
  """
  code = messages.IntegerField(1, variant=messages.Variant.UINT32)
  errors = messages.MessageField(ErrorResponse, 2, repeated=True)


class GeneralResponse(messages.Message):
  """General response for API requests."""
  id = messages.StringField(1001)
  message = messages.StringField(1002)
  values = messages.StringField(1003, repeated=True)
  error = messages.MessageField(ErrorsResponse, 1004)
  kind = messages.StringField(1005)
  fieldNames = messages.StringField(1006, repeated=True)
  itemsPerPage = messages.IntegerField(1007, variant=messages.Variant.UINT32)
  currentItemCount = messages.IntegerField(
      1008, variant=messages.Variant.UINT32)
  nextPageToken = messages.StringField(1009)


class Note(messages.Message):
  """Note message used as MessageField.

  See also: model_utils.DHNoteProperty.
  """
  user = messages.StringField(1)
  date = message_types.DateTimeField(2)
  text = messages.StringField(3)


GET_REQUEST = endpoints.ResourceContainer(
    key_name=messages.StringField(1),
    planDate=messages.StringField(2))


DELETE_REQUEST = endpoints.ResourceContainer(
    key_name=messages.StringField(1))
