"""Error messages for Double Helix.

This file will hold all error_messages used by Double Helix. Please do not
import packages to this file in order to avoid circular dependencies.

Notes on naming:
- Do not include private names (eg. '_ENTITY_MISSING').
- Do not include MSG or ERROR in name (eg. 'ENTITY_MISSING_ERROR')
- Maintain alphabetical order within sections.
"""

# Common.
# TODO(formans) Include details if available in MODEL_CONVERSION_FAIL message.
CATEGORY_MISSING = '%s requires category.'
CREATE_FAIL = 'Create failed for %s %s.'
DELETE_FAIL = '%s %s delete failed.'
DEP_ERROR = ('dependent_error')
DEP_DECOMMISSION = ('Dependent children are in "AsBuilt" physical '
                    'status. Cannot decommission %s of kind %s')
DEP_MISSING = ('No Dependent children for key_name %s.')
DEP_STATUS = ('Dependent children are in %s status. '
              'Cannot update the status of %s to %s.')
DEPENDENCY = ('%s in %s has dependency on the %s you are trying to '
              'delete.')
DETAIL_ASBUILT_DEPENDENCY = ('%s %s contains AsBuilt %s %s and hence'
                             ' cannot be %s.')
DEPENDENCY_MOVE = 'Cannot move %s to %s %s because of dependencies %s.'
DUPLICATE_KEYNAME = '%s with key name %s already exists.'
DUPLICATE_ID = '%s with id %s already exists.'
DUPLICATE_NAME = '%s with name %s already exists.'
ENTITY_MISSING = '%s %s does not exist.'
ENTITY_NONE = 'Entity cannot be None.'
ENTITY_NONE_IN = 'Entity cannot be None in %s.'
ENTITIES_NOT_FOUND = 'No entities found for %s of type %s.'
KEYNAME_MISSING = '%s key_name was not supplied.'
KEYNAMES_MISSING = '%s key_names were not supplied.'
KEYNAME_MULTIPLE_SEP = '%s:%s contains multiple parent key separators.'
KEYNAME_NONE = 'key_name cannot be None.'
KEYNAME_MISMATCH_NAME = 'Name must be equal to key_name: %s vs %s.'
KEYNAME_NOT_STRING = 'key name not a string: %s:%s'
KEYNAME_SEP_NO_PARENT = ('%s:%s contains a parent key separator but no parent '
                         'is specified in metadata')
NO_METADATA_FILE_FOR_MODEL = 'No metadata file found for %s'
NON_STANDARD_MODEL_DEF = 'Definition of %s kind does not follow standards.'
MESSAGE_CONVERSION_FAIL = 'Error occurred while converting to message.'
MISSING_REQUIRED_FIELD = 'Missing required field %r.'
MODEL_CONVERSION_FAIL = 'Error occurred while converting to model.'
MODEL_NONE = 'Model cannot be None.'
MODEL_NOT_FOUND = 'Model not found.'
NAME_MISSING = '%s requires name field.'
NOT_INTEGER = '%s should be integer. Found: %s'
PARAM_MISSING = 'Missing required parameter %s.'
SETTING_NOT_SET_NUM = 'Application setting %s is not set. Using default of %d.'
SETTING_NOT_SET_STR = 'Application setting %s is not set. Using default of %s.'
SYS_ERROR = 'Internal Server Error: %s.'
UPDATE_FAIL = 'Update failed for %s %s.'
UPDATE_NON_EXIST = '%s not found to update.'
KEY_ERROR = 'Key not found when fetching key "%s" from dictionary %s.'
NO_CONTROLLER_FOR_KIND = 'No controller found for %s'
FAILED_PROPAGATE_CHANGE = 'Failed to propagate %s %s change to %s %s'
INVALID_FORMAT = 'Got invalid format for %s, expected format %s'
PARENT_MISMATCH = 'Mismatch between %s\'s %s %s and %s %s %s.'
QUERY_IS_LOADING = 'Query is loading. Please try again in a few minutes.'

# Common validation.
BOOLEAN_FAIL = 'The input is not a boolean.'
CHOICE_LIST_FAIL = 'Value %r for property %s is not an allowed choice.'
DATETIME_FAIL = 'The input is not a datetime.'
DECIMAL_FAIL = 'The input is not a decimal.'
DECIMAL_RANGE_FAIL = 'The decimal value (%s) must be in range %s.'
DUPLICATE_VALUE = 'Duplicate %s %s detected: %s'
EMAIL_TEMPLATE_NOT_FOUND = 'Email template named \'%s\' does not exist.'
FLOAT_FAIL = 'The input is not a float.'
FLOAT_RANGE_FAIL = 'The float (%s) value must be in range %s.'
GROUPER_LDAP = 'Error on LDAP validation, please try again later: %s'
INT_FAIL = 'The input is not an integer.'
INT_RANGE_FAIL = 'The integer (%s) must be in range %s.'
INVALID_DATE = '%s is not a valid date.'
INVALID_EMAIL = '%s is not a valid email address.'
INVALID_FK = 'Value "%s" for field %s has no entry in %s.%s.'
INVALID_LDAP = '%s is not a valid ldap.'
INVALID_TYPE = 'Couldn\'t convert types.'
JSON_DECODE_FAIL = 'No JSON object could be decoded'
JSON_PARSE_FAIL = 'Unable to parse as JSON: %r.'
JSON_INVALID_ASCII = "Contains invalid (non-ASCII) character: '%s'."
MUST_BE_UNIQUE = '%s must be unique.'
REGEX_FAIL = 'Field %s did not match validation: %s.'
REPEATED_FAIL = 'Field %s does not accept list.'
REQUIRED_BOOL_EMPTY = 'Required boolean value is empty.'
REQUIRED_FAIL = 'Required field missing: %s.'
REQUIRED_STRING_EMPTY = 'Required string field is empty.'
STRING_FAIL = 'Length is too long for String field.'
TIMESTAMP_FAIL = 'The date/time must be provided in ms since the epoch.'
IMMUTABLE_FIELD_UPDATE_FAIL = 'Unchangeable fields are updated: %s'

# Foreign key.
FK_ALT_KEY_LOOKUP = 'Failed to find value for alternate key lookup.'
FK_DATASTORE_ERROR = 'Datastore error has occurred.'
FK_PARENT_NOT_FOUND = 'FK Parent not found: %r'
FK_RETRY_EXCEEDED = 'Exceeded transaction retries.'
FK_INVALID_INDEX_SETTING = (
    'In %s the field "%s" is a foreign key, and must be indexed.')

# Logs API.
LOG_EXCEPTION = 'Exception occurred in %s: %s'

# Metadata validation.
# TODO(dgudeman): lots of these need the kind added to the error message.
DEFAULT_VALUE_CHOICES = 'Default value %r not in choices %r'
DEFAULT_VALUE_CONVERSION = (
    'Default value %r cannot be converted to numerical')
DEFAULT_VALUE_RANGE = 'Default value %r does not fall into range %r'
DEFAULT_VALUE_REGEX = 'Default value %r does not match regex %r'
DUPLICATE_RENAME = 'Field %s has duplicate rename attribute value: %s'
FOREIGN_FIELD_REQUIRED = (
    'The foreign field %s of kind %s must be required for field %s.')
FOREIGN_FIELD_UNIQUE = (
    'The foreign field %s of kind %s must be unique for field %s.')
INVALID_RANGE_COUNT = 'Range value should contain two elements'
INVALID_RANGE_TYPE = 'Range value only valid for numerical types'
INVALID_REGEX = 'Regex value %r is invalid (%r)'
KIND_MISMATCH = 'Metadata kind should be %r; not %r'
MANAGED_FIELDS = (
    'Addition and deletion of fields not allowed for managed model %s -- %s')
METADATA_CONVERSION = '%r can\'t be converted to %r'
METADATA_NONEXIST = 'No metadata exist for kind %s.'
METADATA_NONEMPTY = 'Metadata kind %s still has entities.'
NON_EXISTENT_FOREIGN_FIELD = (
    'The field %s has non existent alternate key foreign field %s in kind %s.')
OVERRIDE_FIELD = 'Warning: Update of %s violates the ndb model fields: %s'
OVERRIDE_PROPERTY = (
    'Warning: Update of %s violates the ndb model properties: %s')
INCONSISTENT_IS_MANAGED = (
    'Managed kind %s is not listed in constants.MODEL_MODULES')
SAMPLE_UPDATE = 'Sample metadata cannot be updated.'
UNIQUE_VALIDATION = 'Unique field %s must be required and query indexed.'
UNKNOWN_ATTRIBUTES = 'Kind %s unknown attributes -- %s'
UNDEFINED_FOREIGN_FIELD = 'The alt_key.foreign_field must be defined for %s.'
UNDEFINED_FOREIGN_KIND = (
    'The alt_key.foreign_kind field must be defined for field %s.')
UNDEFINED_KEY_FIELD = 'The alt_key.key_field must be defined for %s.'
UNDEFINED_CONDITIONALS = 'Empty conditionals detected for field %s.'
UNDEFINED_CONDITIONAL_RULES = 'No rules defined for conditional on field %s'
UNDEFINED_CONDITIONAL_OVERRIDES = (
    'No overrides defined for conditional on field %s')
UNKNOWN_CONDITIONAL_ASSEMBLY_ERROR = (
    'Unknown exception during assembly of conditionals for field %s: %s')
UNDEFINED_CONDITIONAL_RULE_REFERENCE = (
    'The field %s is not defined in the metadata for use in conditional rules.')
UNSUPPORTED_CONDITIONAL_TYPE = (
    'Datatype %s is not supported by conditionals on field %s. '
    'Supported property types are: %s')
INVALID_CONDITIONAL_OPERATION = (
    'The conditional operation %s is unsupported. Supported operations are: %s')
INVALID_CONDITIONAL_TYPE = 'Conditional rule value is not valid type: %s'
MALFORMED_CONDITIONAL_RULE = (
    'Malformed conditional rule "%s" in metadata %s. '
    'Must be of the form "<field_name> <op> <value>".')
MALFORMED_CONDITIONAL_OVERRIDE = (
    'Malformed conditional override "%s" in metadata %s. '
    'Must be of the form "<metadata_property> = <setting_value>".')
INVALID_CONDITIONAL_OVERRIDE = (
    'The conditional override "%s" is unsupported. Supported overrides are: %s')
INVALID_BOOLEAN_PROPERTY_SETTING = (
    'Invalid boolean setting for "%s" override. Must be True or False.')
INVALID_CONVERT_CASE_SETTING = (
    'The convert_case setting "%s" is invalid. Must be LOWER, UPPER, or TITLE.')

# Metadata Pipelines (MDP)
MDP_KIND_DOES_NOT_EXIST = (
    'Error during metadata import: kind %s does not exist.')
MDP_ERROR_READING = 'Error reading %s metadata from file %s: %s'
MDP_ERROR_IMPORTING = 'Error importing %s metadata from file %s: %s'
MDP_WARNING_IMPORTING = 'Warning importing %s metadata from file %s: %s'

# Metadata deletion failure.
METADATA_DELETE_FAIL = 'Delete of kind %s failed. %r'

# CSV Importer.
IMPORT_BAD_CSV_FILENAME = "Invalid filename, must end in '.csv': %r"
IMPORT_EMPTY_FILE = 'Import file is empty.'
IMPORT_BATCH_PART = 'Import request missing batch and/or parts.'
IMPORT_CREATE_PERMISSION = 'User does not have permission to create new kinds.'
IMPORT_CTRL_MISSING = 'Managed kind: %s missing controller.'
IMPORT_INSERT_UPDATE_ROW_FAIL = (
    'Insert/Update failed for row id: %s with error %s')
IMPORT_KEY_NAME_MISSING = 'Key name column is missing.'
IMPORT_BAD_KEY_NAME = 'Key name %s is not allowed: %s.'
IMPORT_DUPLICATED_COLUMNS = 'These duplicated columns must be unique: %s'
IMPORT_DUPLICATED_COLUMNS_REGARDLESS_OF_CASE = (
    'These duplicated columns must be unique regardless of case: %s')
IMPORT_KEY_KIND_MISSING = 'Key kind column is missing or empty.'
IMPORT_KEY_KIND_NOT_ALLOWED = 'Cannot import Key kind "%s".'
IMPORT_MANAGED_METADATA = 'Import for managed model %s has unknown fields: %s.'
IMPORT_OVERRIDE_PERMISSION = (
    'User does not have permission to override validations')
IMPORT_RECORD_FAIL = 'Import %s failed record creation on line %s: %s'
IMPORT_RECORD_STATUS = 'One or more record creation has failed for import %s.'
IMPORT_RESERVED_NAME = 'Field name "%s" is reserved.'
IMPORT_STATUS_CREATE_FAIL = 'CSV ImportStatus creation failed: %s'
IMPORT_STATUS_MISSING = 'ImportStatus with keyname %s not found.'
IMPORT_UNKNOWN = 'Unknown error occurred during import.'
IMPORT_UNMANAGED_METADATA = 'Updating metadata for %r with new fields: %r'
INVALID_KEY_VERSION = 'Invalid key_version, please export latest.'
INVALID_KIND = 'Kind %s does not match import kind %s.'
MALFORMED_IMPORT = 'Malformed CSV import request: %s'
MISSING_KIND = 'Kind missing in row.'
PIPELINE_ABORTED = 'Pipeline aborted: '
IMPORT_NONEXISTING = ('Key_name "%s" does not exist and cannot be created with'
                      ' validation disabled.')
IMPORT_INVALID_FIELD_NAME = '%r is not a valid field name.'
IMPORT_FOREIGN_KEY_MISSING = ('Kind %r appears as a foreign kind, but there '
                              'is no key_name or alternate key column.')
IMPORT_CANCELLED_DUP = (
    'Cancelling import of %s because an import is in progress.')
IMPORT_CANCELLED_UNSET = (
    'Cancelling import of %s because the period has been unset.')
IMPORT_FAILED_UPLOAD = ('Upload failed for unknown reasons. Try clearing your'
                        ' cookies and then try the import again.')
IMPORT_MULTIFILE_UNSUPPORTED = 'Multi-file upload is not supported.'
IMPORT_LINE_FAILED = 'Import of line %s for kind %s failed: %s'
IMPORT_FILE_NOT_AVAILABLE = 'The import file is not available.'

# CSV Processing.
CSV_INVALID_HEADER = 'Invalid column headings.'
CSV_REQUIRED_COL_NOT_FOUND = 'Required column "%s" not found in input.'

# Google Cloud Storage.
GCS_FILE_MISSING = 'File cannot be found at %s.'
GCS_FORBIDDEN_ERROR = 'Forbidden from accessing file %s (Status 404).'
GCS_FILE_ILLEGAL = 'Unrecognized form for GCS file: %r'

# Rack messages.
RACK_CONFLICTING_DEVICE = 'Cannot change number_rails. Conflicting devices: '
RACK_COORD_DEP = '%s and %s should be set when %s and %s are set.'
RACK_COPY_BAD_STATUS = '%s is an invalid new rack status.'
RACK_COPY_NO_DECOM = 'Cannot copy decommissioned rack.'
RACK_COPY_TARGET_BAD = 'Target location occupied by rack %s.'
RACK_COPY_TOO_MANY = (
    '%d exceeds number of copies allowed in one copy operation (%d).')
RACK_COPY_DEVICE_FAIL = 'Unable to copy Device %s.'
RACK_COPY_FAIL = 'Unable to create Rack copy.'
RACK_COPY_SOCKET_FAIL = 'Unable to copy %ss.'
RACK_DECOM_NO_MOVE = 'Cannot change %s of a decommissioned rack.'
RACK_OVERLAP = 'The position and row number overlap with: %s.'
RACKROW_CONTAINS_ASBUILT = 'This row contains an AsBuilt rack.'
RACKROW_DUP_ROW = 'Row numbers cannot duplicate existing rows in the space.'
RACK_CREATE_FAIL = 'Fail to create rack. Unexpected Error: %s.'
RACK_RAIL_NUMBER_CHANGE = ('Changing the rail number on an existing rack '
                           'is rejected, please create a new rack.')
RACK_INVALID_RMU = ('Change is rejected, there are insufficient RU\'s to house'
                    ' all of the available devices.')
RACK_DIMENSION_CONFLICT = 'Cannot change dimension. Conflicting devices: '
RACK_NAME_MISSING = 'Name for rack %s is missing.'
RACK_SUB_TYPE_INVALID = 'RackRoleSubType should be one of %s.'
RACK_SUB_TYPE_NOT_REQUIRED = (
    'RackRoleType has no sub types; Rack should not have RackRoleSubType.')

# Rack naming messages.
RACK_NAME_NO_POP = (
    'Rack in space %s, position %s-%s, does not have a pop associated with it.')

# Building messages.
BUILDING_BASEMENTS_FLOORS_RANGE = ('There are spaces outside of floors'
                                   ' and basements new value range.')
BUILDING_BASEMENTS_FLOORS_NONE = 'Building must have at least one floor.'
BUILDING_LOCALITY_ID_EMPTY = 'GetLocality returns empty string.'
BUILDING_DATA_FAIL = 'GetBuildingData failed with error: %s.'

# BOM and BOMItem messages.
BOM_EMPTY_POP = 'One or more POP is required.'
BOM_FIELD_REQUIRED_FOR_ORDERED = (
    'The field %s is required when bom_status is set to Ordered')
BOM_INVALID_CREATE = 'The BOM must be created with status "New".'
BOM_INVALID_DELIVERY_DATE = (
    'The current_onsite_request_date must be greater than or equal '
    'to the current date UTC.')
BOM_INVALID_METRO = 'Invalid Metro key name: %r.'
BOM_INVALID_ORDER_GPN = (
    'The Order cannot be created because Part "%s" is missing either GPN '
    'or ordering_part_number.')
BOM_INVALID_ORDER_PART = (
    'The Order cannot be created because Part "%s" does not exist.')
BOM_INVALID_ORDER_POP = (
    'The Order cannot be created because one or more items is missing a POP.')
BOM_INVALID_ORDER_QTY = (
    'The Order cannot be created because it contains no items or all items '
    'have a zero quantity.')
BOM_INVALID_ORDER_STATUS = (
    'The Order cannot be created because Part "%s" has an invalid status "%s".')
BOM_INVALID_ORDER_CANCELED = (
    'The Order cannot be created because the BOM has a status of Canceled.')
BOM_MOCA_EMPTY_BTP_ID = (
    'MOCA validation failed. No BTP id was provided for validation.')
BOM_MOCA_INVALID_BTP_ID = (
    'MOCA validation failed. No deliverables found for BTP: %s.')
BOM_MOCA_INVALID_DATA_FORMAT = (
    'MOCA validation failed. Missing required column: %s in table %s.')
BOM_MOCA_NO_BOMS_FOUND = (
    'MOCA validation failed. No BOMs found for BTP: %s.')
BOM_MOCA_EMPTY_UNIT_DETAILS = (
    'MOCA validation failed. No unit_details received.')
BOM_MOCA_NO_ORDERABLE_PARTS = (
    'MOCA validation failed. No orderable parts found for BTP: %s.')
BOM_MOCA_NO_ORDERABLE_GPNS = (
    'MOCA validation failed. No orderable GPNs found for BTP: %s.')
BOM_MOCA_NO_BTP_PART = (
    'MOCA validation failed. unit_detail for part with gpn: %s '
    'not found in BTP: %s.')
BOM_MOCA_EXCESS_PART = (
    'MOCA validation failed. Part with gpn: %s being ordered in excess '
    'for BTP: %s.')
BOM_MOCA_BQ_TIMEOUT = (
    'MOCA validation failed. Timed out fetching BTP data for %s. Error: %s.')
BOM_INVALID_BTP = 'No BTP found for UUID: %s'
BOM_INVALID_POP = 'Invalid POP key name: \'%s\'.'
BOM_INVALID_POP_CHANGE = (
    'POP cannot be removed because BOMItems exist that reference it.')
BOM_INVALID_PART = (
    'BOMItem "%s" cannot be copied because Part "%s" does not exist.')
BOM_INVALID_PART_GPN = (
    'BOMItem "%s" cannot be copied because Part "%s" has no GPN.')
BOM_INVALID_PART_STATUS = (
    'The %s Part with status "%s" cannot be used in a BOM.')
BOM_INVALID_BOM_POP = 'BOMItem POP is not a valid POP from the parent BOM.'
BOM_INVALID_STATUS_DELETE = 'BOM with Ordered status cannot be deleted.'
BOM_INVALID_VALUE_DELETE = (
    'Value deleted for property %s but still has assignents in item %s.')
BOM_INVALID_VALUE_MODIFICATION = (
    'Multiple values for property %s were modified and cannot be propagated to '
    'items.')
BOM_MISSING_METRO = 'POP %s is not valid due to missing Metro.'
BOM_MISSING_REGION = 'POP %s is not valid due to missing Region.'
BOM_UNAUTH_ORDER_SUBMIT = ('User not authorized to submit this Order. Only the '
                           'Deploy PM may submit the Order.')
BOM_UNAUTH_MODIFY = 'User not authorized to modify this BOM.'
BOM_UNAUTH_DELETE = 'User not authorized to delete this BOM.'
BOM_UNAUTH_ORDER_MODIFY = (
    'User not authorized to modify a BOM that has been ordered.')
BOM_ACTIVE_MISSING = 'No active BOM found for project "%s".'
BOM_UNCHANGEABLE_STATUS = 'The status of an ordered BOM cannot be changed.'
BOM_UNCHANGEABLE_NAME = 'The BOM name cannot be changed after creation.'
BOM_ORDER_EXISTS = 'Order already exists for BOM %s.'
BOM_ORDER_CREATION_ERRORS = 'Errors encountered during Order creation.'
BOM_ORDER_ITEM_VALIDATION_ERRORS = (
    'Errors encountered during OrderItem validation.')
BOM_ORDER_ITEM_CREATION_ERRORS = (
    'Errors encountered during OrderItem creation.')
BOM_INVALID_ORDER_UPDATE = (
    'Cannot order a BOM using the BOMService.UpdateBOM API. Please use '
    'BOMService.SubmitBOMToOrder instead.')
BOM_INVALID_ROBO_ID = (
    'Robo ID is required for BOMs that are not Draft, MISC or Other.')
BOM_INVALID_BTP_ROBO_ID = (
    'The Robo ID "%s" for the BTP "%s" is invalid so a Robo ID must be '
    'specified in the CreateBOM request.')
BOM_INVALID_ROBO_ID_MATCH = (
    'The Robo ID "%s" specified in the CreateBOM request does not match the '
    'Robo ID "%s" of the requested BTP.')
BOM_BTP_DRAFT_NAME_MISMATCH = (
    'Draft BTP name \'%s\' does not match actual BTP name \'%s\'.')
BOM_BAD_DRAFT_TRANSITION = 'Cannot change BOM status from %s to %s.'
BOM_ITEM_INVALID_STATUS_DELETE = (
    'BOMItem with Ordered status cannot be deleted.')
BOM_ITEM_UNAUTH_MODIFY = 'User not authorized to modify this BOMItem.'
BOM_ITEM_UNAUTH_DELETE = 'User not authorized to delete this BOMItem.'
BOM_ITEM_UNAUTH_ORDER_MODIFY = (
    'User not authorized to modify a BOMItem that has been ordered.')
BOM_ORDER_DISQUALIFIED_PART = (
    'BOMItem %s contains a disqualified Part (%s). Please fix before ordering.')
BOM_ORDER_ITEM_MISSING_POP = (
    'BOMItem %s is missing Pop. Please fix before ordering.')
BOM_ORDER_ITEM_MISSING_ORDATE = (
    'BOMItem %s is missing Onsite Request Date. Please fix before ordering.')
BOM_COPY_NO_ITEMS = 'Source BOM has no items'
BOM_ITEM_INVALID_UPDATE_STATUS = 'BOMItem status may only be set to Canceled.'
BOM_ITEM_INVALID_CREATE_STATUS = (
    'BOMItem may not be created with Ordered status.')
BOM_ITEM_INVALID_CREATE_BOM_STATUS = (
    'BOMItems may only be created on BOMs with New status.')
BOM_LDAP_NOT_FOUND = 'LDAP: %s Not Found'
BOM_REMAP_MISSING_LDAP = 'Remap requires two LDAPs.'
BOM_CANNOT_SUBMIT_DRAFT_BOM = (
    'BOM is in Draft status, so it cannot be submitted.')
BOM_ITEM_MULTIPLE_BOMS_IN_BATCH = (
    'All BOMItems must be for the same BOM when using CreateBatch.')

# BTP (Build to Plan) Messages.
BTP_BAD_PROJ_ID = '%s is associated with bad project id: \'%s\'.'
BTP_CANCEL = 'Canceled %s %s, name=%s, num=%d.'
BTP_CANCEL_ERROR = 'Errors occurred while canceling %s %s: %s.'
BTP_CANCEL_ORDER_ITEM = 'Canceled OrderItem %s, name=%s.'
BTP_DELIVERY_SUMMARY_FIELD_NAME_NOT_FOUND = (
    '%s %s delivery summary field name "%s" not found in %s.')
BTP_DELIVERY_SUMMARY_NAME_CHANGE = (
    'Deliverable summary name changed from \'%s\' to \'%s\'.')
BTP_DUP_NAME_WITHIN_SAME_BTP_KIND = (
    'BTP kind %s contains multiple %s name value references.'
)
BTP_INCOMPLETE_BTP_KIND_REC = 'BTP Kind entry %s is incomplete.'
BTP_POR_KIND_NOT_FOUND = (
    'Removing %s %s that refers to non-existent POR kind %s and is not '
    'referenced by any BOMs.')
BTP_POR_NOT_FOUND = '%s %s search "%s" fetched nothing from POR %s.'
BTP_POR_REC_MISSING_UUID = '%s record \'%s\' is missing UUID.'
BTP_PROJECT_CANCELED = 'This project has been canceled from the built-to-plan.'
BTP_BIGQUERY_ERROR = 'Internal error reading %s from BigQuery. No row number.'
BTP_BIGQUERY_TIMEOUT = 'Timeout while reading %s from BigQuery.'
BTP_BIGQUERY_DATA_ERROR = (
    'Data error on %d rows while reading %s from BigQuery: %s.')

# Device Controller messages.
SLOTS_PORTS_LOAD_ERROR = (
    'Could not load slots/ports from cloud storage for device %s.')
DEVICE_LOCATION_REQUIRED = ('Device location not provided as Wallmounted '
                            'or Freestanding for a non rack mounted device.')
DEVICE_LOCATION_ERROR_MSG = ('Device should either be on a rack or '
                             'Freestanding/Wallmounted.')
UUID_MISSING_MSG = 'Device missing UUID.'
INSERT_FAIL_MSG = 'Insert failed for device %s.'
UPDATE_FAIL_MSG = 'Update failed for device %s.'
RMU_REQUIRED_MSG = 'RMU required for rack mounted device.'
DUPLICATE_NAME_MSG = ('Device with the name %s already exists in the '
                      'parent space.')
RACK_SIDE_REQUIRED_MSG = 'Rack Side required for rack mounted device %s.'
DEVICE_DEPTH_OVERLAP_MSG = ('Device %(1)s overlaps in depth'
                            ' with device %(2)s.')
DEVICE_RMU_OVERLAP_MSG = ('Device %(1)s can not be placed in the same rmu'
                          ' as that of device %(2)s.')
PLANNED_OVER_ASBUILT_NOT_ALLOWED = ('Device overlap. Planned device %(1)s can '
                                    'not be placed over As Built device %(2)s. '
                                    'Remove, Decommision, or move As Built '
                                    'device.')
ASBUILT_OVER_PLANNED_NOT_ALLOWED = ('Device overlap. As built device %(1)s can'
                                    'not be placed over Planned device %(2)s.')
RMU_BEGIN_INVALID_MSG = 'Device %(1)s begins in the device %(2)s space.'
RMU_END_INVALID_MSG = 'Device %(1)s height overlapping with device %(2)s.'
DEVICE_NO_PANEL_CATEGORY_ERROR_MSG = ('Device administrative category must be '
                                      'set if device is patch panel.')
DEVICE_NO_SC_CATEGORY_ERROR_MSG = ('Device Splice Closure category must be set '
                                   'if device is a splice closure.')
DEVICE_DEPTH_ERROR_MSG = ('Device depth exceeds rack depth (%s %s).  '
                          'If this is by design, please set the '
                          '"Allow Any Width/Depth" option.  Otherwise, '
                          'update the device depth to fit the rack depth.')
DEVICE_NAME_ERROR_MSG = 'Device name %s does not match Part regex: %s'
INVALID_DEVICE_ERROR_MSG = 'Device %s does not exist.'
INVALID_RU = '%s %s must be a multiple of %s.'
INVALID_DEVICE_RMU_ERROR_MSG = 'Device exceeds rack height ru.'
INVALID_DEVICE_RU_ERROR_MSG = 'Device height ru + rmu exceeds rack ru.'
INVALID_USER_ENTERED_DEVICE_RU_ERROR_MSG = ('height_ru is not approximately'
                                            ' the same size as the height '
                                            'in units.')
NAME_REQUIRED_FOR_TYPE_CHANGE = 'Name required for device type change.'

DEVICE_WIDTH_ERROR_MSG = ('Device width exceeds rack width (%s %s).  '
                          'If this is by design, please set the '
                          '"Allow Any Width/Depth" option.  Otherwise, '
                          'update the device width to fit the rack width.')
EXISTING_DEVICE_DEPTH_ERROR_MSG = ('Existing device %(1)s in rmu %(2)s '
                                   'occupies more than 75 percent of the '
                                   'rack depth.')
INVALID_RAIL_NUMBER = ('The rail number is invalid. May be greater than the'
                       ' number of rails in the given rack: %s')
DEVICE_TYPE_REQUIRED_MSG = ('A template_key_name or Part__key_name '
                            'value (exclusively) is required.')
SERIAL_NUMBER_REQUIRED_MSG = 'A serial number is required.'
EMPTY_OR_WHITE_SPACE_VALUE_MSG = ('%s can not have empty or white space as'
                                  ' value')

NO_SUCH_DEVICE = 'No such device.'
NO_SUCH_CARD = 'No such card in device.'

OMS_PROVISIONED = ('Logical device %s cannot be removed; the associated '
                   'physical device has one or more OMS\'s provisioned.')

VERTICAL_POSITION_IS_REQUIRED = ('The vertical position must be specified for a'
                                 ' vertical device.')
DEVICE_SPACE_MISMATCH_WITH_RACK = ('The Space for this Device is not the same '
                                   'as the Space for the parent Rack.')
DEVICE_HAS_NO_PORT = 'Device %s has no port %s.'
DEVICE_CONNECTOR_NOT_ON_PORT = 'Connector %s not on port %s.'
DEVICE_REQUIRES_LOGICAL_DEVICE = '%s device %s requires a logical device.'
DEVICE_LOGICAL_DEVICE_MISSING = (
    'Logical Device %s from Device %s does not exist.')
DEVICE_POP_NOT_LOGICAL_DEVICE_POP = (
    'Device %s: space pop %s does not match logical device pop %s.')
DEVICE_SERVER_FLOOR_INVALID_FIBER_PATH = ('Server floor patch panels may only '
                                          'have a fiber path value of "A" or '
                                          '"B".')
DEVICE_NEEDS_AUDIT_DATE = (
    'Last Audit Date must be specified for devices marked as audited.')

# Device rekey messages.
DEVICE_REKEY_EXP_NO_KEY = 'No key_name should be specified if rekey_all="true".'
DEVICE_REKEY_EXP_KEY = 'A key_name must be specified if rekey_all="false".'
DEVICE_REKEY_NOT_TEMPLATE = 'Device for key_name: "%s" is not a template.'
DEVICE_REKEY_INVALID_KEY = 'Device not found for key_name: "%s".'

# FileAttachment messages.
INVALID_DATA_URL = 'Not a valid base64 data url: %r.'
FILEATTACHMENT_CREATE_FAILED = ('Failed to create FileAttachment for'
                                ' kind: %s key_name: %s GCS: %s error: %r')
DEVICE_PART_DIMENSION = ('The Device %s "%s" does not equal the associated '
                         'Part %s "%s".')
DEVICE_JSON_NON_ITERABLE = 'The Device %s is set to a non-iterable value "%s".'

# History messages.
UNKNOWN_USER_INCIDENT = (
    'Incident %s: Failed to record user for revision history.')

# OMS messages.
OMS_LOGICAL_DEVICE_NOT_FOUND = 'Cannot find logical device named %s for %s.'
OMS_INFRA_PLATFORM_NOT_FOUND = 'Cannot find chassis vendor named %s for %s.'
OMS_MANU_PLATFORM_NOT_FOUND = 'Cannot find manufacturer named %s for %s.'

# Order messages.
ORDER_FIELD_STATUS_ERROR = 'Cannot change %s unless order in %s status.'
ORDER_INVALID_DELIVERY_DATE_PAST = (
    'The onsite_request_date must not be in the past.')
ORDER_INVALID_COMMIT_DATE = 'The current_commit_date must not be in the past.'
ORDER_INVALID_DELIVERY_DATE_STATUS = (
    'The onsite_request_date cannot be edited due to order status.')
ORDER_INVALID_EDIT_FOR_USER = 'Editing %s is reserved'
ORDER_INVALID_EXPORT = (
    'The OrderItem %s cannot be exported to gShip (needs Part Supplied GPN, '
    'quantity, and exportable status).')
ORDER_INVALID_EXPORT_DUP_GPN = (
    'OrderItems cannot be exported to gShip. Duplicate GPNs for the same '
    'POP, Warehouse and OnsiteRequestDate detected.')
ORDER_INVALID_ORDER_CANCEL = (
    'The Order cannot be canceled because some items have already shipped.')
ORDER_INVALID_SUPPLIED_PART_GPN = (
    'The OrderItem cannot be updated because the Supplied Part has no GPN.')
ORDER_ITEM_FIELD_STATUS_ERROR = (
    'Cannot change %s unless order item in %s status.')
ORDER_ITEM_FIELD_STATUS_EXCLUSION_ERROR = (
    'Cannot change %s when order item in status %s.')
ORDER_ITEM_QUANTITY_SHIPPED_ERROR = (
    'Shipped quantity cannot exceed quantity requested.')
ORDER_ITEM_QUANTITY_SHIPPED_NEGATIVE = 'Shipped quantity cannot be negative.'
ORDER_UNAUTH_ORDER_CANCEL = 'User not authorized to cancel orders.'
ORDER_UNAUTH_ORDER_MODIFY = 'User not authorized to modify orders.'
ORDER_UNAUTH_ORDER_ITEM_MODIFY = (
    'User not authorized to modify OrderItems with status in %s.')
ORDER_UNAUTH_TO_CHANGE = 'User not authorized to change %s.'
ORDER_CANNOT_UNCANCEL = 'Canceled orders cannot be uncanceled.'
ORDER_ITEM_REUSED_PART_ERR = (
    'Reused parts are not allowed for fulfillment of order items going to %s.')
ORDER_INVALID_EDIT_DELEGATE_PM = (
    'Editing delegate_pm is reserved for the Deploy PM and the Supply Chain '
    'team.')
ORDER_DELETE_NOT_ALLOWED = 'Delete is not supported for Orders'
ORDER_ITEM_DELETE_NOT_ALLOWED = 'Delete is not supported for OrderItems'
ORDER_RECIPIENT_CONTACT_STATUS = (
    'Cannot change recipient contact in this status')
ORDER_ITEM_NO_MAX_SHIPPED_DATE = (
    'No OrderItem returned from max() shipped_date call.')
ORDER_ITEM_INVALID_SHIPPED_DATE = 'Shipped Date cannot exceed Delivered Date.'

# Part messages.
PART_BUNDLED_MISSING_PARTS = 'Part is bundled but has no bundled parts.'
PART_BUNDLED_INVALID_PARTS = (
    'Part is bundled but has invalid bundled part key_name %s.')
PART_DESC_OR_NAME_ON_CREATE = 'Part description and/or name is required.'
PART_GPN_IS_FROZEN = (
    'GPN is already set for Part %s (%s) and cannot be changed.')
PART_INVALID_EDIT_FOR_USER = (
    'Editing %s is reserved for the Supply Chain Team.  '
    'Please go to go/netops_gpn_request to request updates to this field.')
PART_INVALID_DESIGN_EDIT_FOR_USER = (
    'Editing %s is reserved for the Design Team.')
PART_INVALID_EQUV_PART_GPN = 'Equivalent part with key_name %s has no GPN.'
PART_INVALID_EQUV_PART_KEY = (
    'Part equivalent_parts has invalid part key_name %s.')
PART_INVALID_EQUV_PART_STATUS = (
    'Equivalent Part with key_name %s has invalid part_status "%s".')
PART_INVALID_GPN_FOR_STATUS = 'Part GPN required for Parts in status %s.'
PART_INVALID_GPN_EXISTED = 'Part with GPN %s already exists.'
PART_MODEL_NUMBER_EXISTED = (
    'Part with model_number:manufacturer "%s":"%s" already exists.')
PART_NOT_UNIQUE_FOR_STATUS = (
    'Part %s must be unique within Planned and Generic statuses.')
PART_NPI_EXIT_DATE_LOCKED = (
    'Part npi_exit_date cannot be changed once it is locked.')
PART_STATUS_NPI_LOCKED = (
    'Part_status cannot be changed back to NPI (locked).')
PART_REQUIRED_FAIL = 'Required field "%s.%s" missing.'
PART_REQUIRED_STATUS_FOR_FIELD = 'Part %s required for Parts in status %s.'
UNMERGEABLE_PART = ('The old part (id=%s) has a %s so it cannot be '
                    'automatically deleted.')
PART_INVALID_STATUS = 'The supplied part with status \'%s\' cannot be used.'

# Plans messages.
VERSION_ALREADY_INSTANTIATED = ('Version was instantiated on %s. '
                                'No more changes are allowed.')
VERSION_DOES_NOT_EXIST = 'Version %s does not exist.'
PLANNED_CHANGE_EXISTS = 'Change for %s %s in Plan %s already exists'
PLANNED_CHANGE_DOES_NOT_EXIST = 'Change for %s %s in Plan %s does not exist'

# Pop messages.
POP_ASSOCIATION_ERROR = (
    'Space is associated to a Pop for a different Building.')
POP_CONTAINS_ASBUILT_SPACE = 'Pop %s contains an AsBuilt space named %s.'
POP_CONTAINS_ASBUILT_LOGICAL_DEVICE = (
    'Pop %s contains an AsBuilt logical device named %s.')
POP_INVALID_SPACES = 'One or more dependent Space for Pop %s is invalid.'
POP_INVALID_BUILDING = 'Building associated with Pop %s is invalid.'

# Space messages.
FLOOR_BUILDING_MISMATCH = ('Mismatch between space\'s building %s and'
                           ' floor building %s.')
FLOOR_OUT_OF_RANGE = ('Floor_number %r is out of building '
                      'basements and floors range (%r, %r)')
UNSET_FLOOR_NUMBER = 'Floor number is not set'

# Space messages.
SPACE_CONTENTS_MODIFICATION = (
    'Space contents was modified concurrently by multiple requests.')

# Splice messages.
SPLICE_NO_TOP_DEVICE = 'Top device %s not found.'

# Supply Chain permissions messages.
SC_BAD_CLASS_NAME = 'RulePluginBase classes must have a CamelCase name.'
SC_BAD_RULE_TYPE = 'Rules must be of type RulePluginBase.'
SC_BAD_RULES_PARAM = 'RegisterRules requires a list of type RulePluginBase.'
SC_CHANGE_CONFIG_BUT_NO_EXISTING = 'Change configured, but no existing record.'
SC_CRITERIA_FIELD_MISSING = 'Field %s: field is not found in the Model.'
SC_CRITERIA_FIELD_VALIDATION_ERROR = 'Criteria Field %s: %s'
SC_CRITERIA_FIELD_VALIDATION_EXCEPTION = '%s value %r not valid.'
SC_CUSTOM_RULE_EXCEPTION = 'Rule %s detected this error: %s'
SC_DELEGATE_PM_INVALID = 'Group token $DelegatePM only valid with Order kind.'
SC_DEPLOY_PM_INVALID = 'Group token $DeployPM only valid with Order kind.'
SC_FIELD_METADATA_NOT_FOUND = '%s field metadata not found.'
SC_FROM_AND_TO_VALUES_THE_SAME = '%s: changes from and to values are the same .'
SC_INVALID_CRITERIA_FIELD_TYPE = 'The criteria field cannot be of type %s.'
SC_INVALID_GROUP_METADATA = 'Field %s: group %s is not in the proper format.'
SC_LIST_AND_GROUPS_REQUIRED = 'Value list and groups specification required.'
SC_NO_VALUES_OR_CHANGES = '%s: has no values or changes elements.'
SC_ORDER_NOT_FOUND = 'Order associated with this OrderItem not found.'
SC_ORDER_STATUS_PREVENTS_UPDATE = 'Order status prevents update.'
SC_REPEATING_CRITERIA_FIELD = 'Criteria field %s cannot repeat.'
SC_RESTRICT_MANAGED_ONLY = 'Restrictions only allowed for managed models.'
SC_RULE_NOT_FOUND = 'Rule %s not found.'
SC_TOO_MANY_RESTRICTIONS = 'Too many restrictions found.'
SC_UPDATE_REQUEST_DENIED = 'Request denied due to update restrictions.'
SC_WRONG_CRITERIA_FIELD = 'Criteria field should be %s.'

# Metro messages.
METRO_IS_REFERENCED_IN_INTERMETRO = 'This Metro is referenced in InterMetro.'

# User Preference messages.
TOO_FEW_FIELDS = 'Must provide %s or %s.'
TOO_MANY_FIELDS = 'Cannot provide %s if %s provided.'
PREF_NOT_FOUND_MSG = 'User preference with key_name %s was not found.'

# Metro/POP API
NAME_INVALID = '%s name %s is invalid'

# Vendor API
VENDOR_CODE_INVALID = (
    'Vendor code %s should be five alphanumeric characters.')
VENDOR_CODE_REQUIRED = '%s vendor code is required'

# UNM convert messages.
UNM_CONVERT_ERROR = (
    "UNM convert: Failed to convert entity kind '%s', entity %s, error '%s'"
)
UNM_INVALID_CHASSIS_PARENT_TYPE = (
    "UNM convert: Chassis parent type must be Rack or Logical Device, got '%s'"
)

# UNM export messages.
UNM_BAD_CIRCUIT = "UNM export: Failed exporting Element %s of Circuit '%s'."
UNM_BAD_VALUE = "UNM export: Unknown value '%s' for %s of entity '%s'."
UNM_BATCH_UPDATE_FAILED = 'UNM export: Batch Update failed.'
UNM_CLEAN_FAILED = 'UNM export: Clean_relationships failed for %s: %s.'
UNM_DATA_EXCEPTION = 'UNM export: Data exception: '
UNM_DELETE_FAILED = 'UNM export: Delete failed for %s: %s.'
UNM_DELETE_NO_NAME = "UNM export: Couldn't find UNM name when deleting '%s'."
UNM_DELETE_NO_KIND = (
    "UNM export: Couldn't find UNM Kind when deleting Device '%s'. "
    "Guessing EK_CHASSIS.")
UNM_ENTITY_NO_NAME = 'UNM export: %s has no name for UNM.'
UNM_FULL_EXPORT_FAILED = 'UNM export: Full Export failed.'
UNM_FULL_EXPORT_FAILED_ENTITY = 'UNM export: Full export failed for %s: %s.'
UNM_FULL_EXPORT_FAILED_NO_HOST = 'UNM export: Full export failed, no proxy URL.'
UNM_FULL_EXPORT_FAILED_REASON = 'UNM export: Full Export failed: %s'
UNM_FULL_EXPORT_FAILED_SHARDING = (
    "UNM export: Full export failed, with sharding stride '%s'.")
UNM_FULL_EXPORT_REQUESTED = 'UNM export: Proxy server requested full export.'
UNM_HEARTBEAT_FAILED = 'UNM export: Heartbeat failed.'
UNM_INTERNAL_ERROR = "UNM export: Internal Error in '%s'"
UNM_NO_CIRCUIT = "UNM export: No circuit found for circuit element '%s'."
UNM_NO_CIRCUIT_ELEMENTS = 'UNM export: No circuit elements found for circuit %s'
UNM_NO_CIRCUIT_KEY = (
    "UNM export: No circuit key_name found for Circuit or CircuitElement '%s'.")
UNM_NO_PORT_FOR_CIRCUIT = 'UNM export: No port found for circuit %s, element %d'
UNM_PIPELINE_FAILURE = "UNM export: UNM pipeline failed: '%s'."
UNM_PIPELINE_SETUP_ERROR = 'UNM export: UNM pipeline setup error.'
UNM_PORT_NO_RESERVATION = "UNM export: Can't find reservation for port %s."
UNM_PREPARE_FULL_EXPORT_FAILED = (
    'UNM export: Prepare full export failed. Full export failed.')
UNM_RACK_NO_NAME = (
    "UNM export: Can't construct name for Rack '%s' due to missing Space.")
UNM_RENAME_FAILED = 'UNM export: Rename failed for %s: %s.'
UNM_SPACE_MULTIPLE = "UNM export: Multiple Space entities containing POP '%s'"
UNM_STREAMZ_UNKNOWN_OP = "UNM export: Unknown op '%s' for streamz."
UNM_STUBBY_ERROR = 'UNM export: stubby error contacting proxy server: %s.'
UNM_STUBBY_ERROR2 = 'UNM export: proxy server returned error %s, %s.'
UNM_SUBBUILDING_NO_NAME = "UNM export: Unknown UNM name for subbuilding '%s'."
UNM_UNKNOWN_DEVICE_TYPE = "UNM export: Unknown type_name for Device : '%s'."
UNM_UNKNOWN_CONNECTIVITY_DEVICE = (
    "UNM export: Unknown entity with key '%s' exporting device connectivity.")
UNM_UNKNOWN_ENTITY_KIND = "UNM export: Unknown entity kind: '%s'."
UNM_UNKNOWN_PARENT = "UNM export: Unknown parent %s for %s '%s'."
UNM_UNKNOWN_REALM = "UNM export: Unknown realm '%s' for %s '%s'."
UNM_UNKNOWN_ROLE = "UNM export: Unknown role '%s' for %s '%s'."
UNM_UNSUPPORTED_OPERATION = 'UNM export: Internal error %s.'
UNM_UNSUPPORTED_TYPE = 'UNM export: unsupported type %s.'
UNM_UPDATE_FAILED = 'UNM export: Incremental update failed for %s: %s. '
UNM_UPDATE_STUBBY_FAILED = 'UNM export: Incremental update failed.'
UNM_UPDATE_FAILED_NO_HOST = (
    'UNM export: Incremental update failed, no proxy URL.')
UNM_UPDATE_FAILED_REASON = 'UNM export: Incremental update failed: %s'
UNM_VENDOR_UNKNOWN = "UNM export: Unknown vendor '%s' for POP '%s'"
UNM_VENDOR_MULTIPLE = (
    "UNM export: Multiple entities for vendor '%s' for POP '%s'")

# Logical Device messages.
LOGICAL_DEVICE_DUPLICATE_NAME = (
    'A logical device with the same name and logical status already exists.')
LOGICAL_DEVICE_NAME_POP_INVALID = ('Pop portion of Name \'%s\' does not match'
                                   ' with Pop__key_name: %s')
LOGICAL_DEVICE_NAMING_INVALID = ('Name does not match with naming convention of'
                                 ' AB01.CDEF01.')

# Big Query.
BQ_SAME_NAME = 'Multiple BigQueryViews have the same name: %s'
BQ_MISSING = 'No BigQueryView named %s.'
BQ_NO_IMPORT_KIND = 'BigQueryView %s does not have an import_kind.'
BQ_IMPORT_KIND_NAME_ERROR = (
    'BigQueryView %s import_kind %s does not have the correct prefix.')
BQ_NO_QUERY = 'BigQueryView %s does not have a query.'
BQ_IMPORT_KIND_IS_MANAGED = 'BigQueryView %s import_kind %s is a managed model.'
BQ_KIND_IS_NOT_UNIQUE = 'BigQueryView %s import_kind %s already exists.'
BQ_CHANGING_NAME = 'Changing the name of a BigQueryView entry is not allowed.'
BQ_IMPORT_RECORDS_EXIST = (
    'Cannot delete BigQueryView %s because import entities for the query exist.'
    ' Delete all %s entities first.')
BQ_IMPORT_FAILED = 'BigQuery Import of %s failed: %s.'

# Release note messages.
RN_ACTIVE_RELEASE_NOT_FOUND = ('Active release for project_id %s not found')
RN_ACTIVE_RELEASE_POPULATE_FAILED = (
    'Populate error in PopulateActiveReleaseNames. error: %s')
RN_BLUEPRINT_NOT_FOUND = ('Blueprint %s for project %s not found')
RN_BUGANIZER_FAILED = ('Failed to get issues from Buganizer.')
RN_CL_GET_FAILED = ('RPC failure, could not get change list. error: %s')
RN_EMAIL_SEND_ERROR = ('Max number of retries hit while trying to send mail')
RN_EMPTY_BUG_LIST = ('Empty bug_list in PopulateBugs')
RN_EMPTY_CL_NUMBER_LIST = ('Empty cl_number_list')
RN_INVALID_ID = ('Faile get a release object with invalid id.')
RN_INVALID_RELEASE_NAME = ('Not an active release name %s')
RN_POPULATE_FAILED = ('Populate error in Release. error: %s')
RN_PROJECT_NOT_FOUND = ('Project %s not found')
RN_PUT_ERROR = ('Failed to put the release object.')
RN_RELEASE_NOT_FOUND = ('Releases for project_id %s not found')
RN_USER_ERROR = ('Action only available to Admin users.')

# key version error Message.
KEY_VERSION_MISMATCH = (
    'Key version should match with the existing entity for %s')

# Port Reservation messages.
PORT_BROKEN_ERRORS = ('Errors occurred during circuit element port replacement:'
                      ' %s')
PORT_BROKEN_UNREPLACED = 'No replacement port found for circuit element %s'
PORT_CLIENT_NONUNIQUE = 'Client ID %s and reservation ID %s non-unique.'
PORT_INVALID_PORT_NAME_FORMAT = (
    'Port %s with key name %s has undefined port name format. Patch panel port '
    'name should be eiter "port-[\\d]" or "[A-Z]+[\\d+]"')
PORT_INVALID_NAME = 'Port with key name %s has invalid name %s.'
PORT_IS_NULL = 'Port is null.'
PORT_MPO_TRACE_A_XCON_NOT_FOUND = (
    'PanelXcon for device %s (%s), port %s (%s) could not be found.'
)
PORT_MPO_TRACE_CABLE_CONN_NOT_FOUND = (
    'Cable Connector %s could not be found.'
)
PORT_MPO_TRACE_NO_OFFSET = (
    'Offset not found for device %s, (%s), port %s (%s), connector %s (%s).'
)
PORT_MPO_TRACE_DEVICE_NOT_FOUND = (
    'Device %s could not be found.'
)
PORT_MPO_TRACE_NO_CONN = 'Device %s (%s), Port %s (%s) has no connectors.'
PORT_MPO_TRACE_CABLE_CONN_INVALID_DEVICE_KEY_NAME = (
    'Cable Connector %s has NULL for column "top_device_key_name".'
)
PORT_MPO_TRACE_CABLE_CONN_INVALID_PLUGGED_KEY_NAME = (
    'Cable Connector %s has NULL for column "plugged_into_key_name".'
)
PORT_MPO_TRACE_PLUGGED_CABLE_CONN_NOT_FOUND = (
    'Cable Connector plugged into MPO Connector %s could not be found.'
)
PORT_MPO_TRACE_SPLICE_NOT_FOUND = (
    'Splice %s could not be found when tracing on Device %s (%s), Port %s (%s)'
)
PORT_MPO_TRACE_STRAND_NOT_FOUND = (
    'Strands for device %s (%s), port %s (%s) could not be found.'
)
PORT_MPO_TRACE_Z_XCON_NOT_FOUND = (
    'PanelXcons for target cable conn %s could not be found.'
)
PORT_MPO_TRACE_Z_XCON_OFFSET_INVALID = (
    'PanelXcon for Z-end cable connector %s, offset %d could not be found.'
)
PORT_NO_FRONT_PORT = ('Port with key name %s is not an available front port '
                      'in Device %s.')
PORT_NO_PATCH_PANEL = (
    'Top device for port %s with key_name %s is not a patch panel.')
PORT_NOT_AVAILABLE = 'Port with key name %s is not available: %s.'
PORT_NOT_FOUND = 'Port with key name %s not found.'
PORT_NOT_FOUND_IN_DEV = (
    'Port with key name %s not found in Device %s (key: %s).')
PORT_NOT_VALID = (
    'Port %s (key %s) in Device %s (key %s) is not valid for a new circuit: '
    'physical_status %s, logical_status %s.')

PORT_PHYSICAL_STATUS_CHANGE_NOT_ALLOWED = (
    'Port physical usage status cannot be changed from Occupied to Vacant if '
    'logical usage status is In Use (AsBuilt circuit uses this port '
    'and can not be released until Stoat reports that circuit is decommed).')
PORT_BROKEN_OPERATION_NOT_ALLOWED = (
    'Physical status change is not allowed for broken ports.')
PORT_BROKEN_LOGICAL_STATUS = ('Port cannot be set to broken if the logical '
                              'status is In Use.')
PORT_PHYSICAL_STATUS_UPDATE_NOT_ALLOWED = (
    'Port physical status for non-YAWN site devices cannot be updated through '
    'DoubleHelix. Please use NetCracker for such updates.')
# Release Ports.
PORT_RELEASE_INACTIVE_RESERVATION = (
    'Reservation with client_id %s, client_reservation_id %s '
    'has released already.')
PORT_RELEASE_INVALID_BUNDLE_ID = (
    'No ports found with bundle_id %s in Device %s (%s).')
PORT_RELEASE_INVALID_DEV_PORTS = (
    'Two simplex ports should be released simultaneously '
    'if they are connected to the same duplex port. Request: %s. '
    'A-end connector count %d, Z-end connector count: %d')
PORT_RELEASE_INVALID_RESV_INFO = (
    'Unknown client_id %s, client_reservation_id %s in Request.')
PORT_RELEASE_INVALID_PORT_OFFSETS = (
    'No ports found with bundle_id %s and port_offsets [%s] '
    'in Device %s (%s).')
PORT_RELEASE_MISMATCHED = 'Devices/Ports in request mismatch %r vs. %r.'
PORT_RELEASE_NO_BUNDLE_ID = (
    'bundle_id in Device %s (%s) should be specified with '
    'non-null port_offsets.')
PORT_RELEASE_NO_PORTS = 'No ports found to be released.'
PORT_RELEASE_UNRESERVED = 'Port %s in Device %s is unreserved.'

# Reserve Ports.
PORT_RESERVE_ARG_ERROR = ('Either device_port_counts or device_ports should be '
                          'specified in the request, but not both.')
PORT_RESERVE_IN_USE = 'In-use port %s cannot be reserved.'
PORT_RESERVE_COLLIDE = 'Please refresh and retry reservation.'
PORT_RESERVE_CONNECTORS = 'Partially reserved port not allowed.'
PORT_RESERVE_BROKEN = 'Broken port %s cannot be reserved.'
PORT_RESERVE_EXPIRATION = 'Reservation date past expired.'
PORT_RESERVE_DECOM = 'Port %s is pending decommission.'
PORT_RESERVE_DEVICE_DECOMMED = ('Unable to reserve ports on decomissionned '
                                'device %s.')
PORT_RESERVE_INSUFFICIENT = 'Device %s does not have %s valid ports available.'
PORT_RESERVE_INVALID_PORT_NAME = 'Unknown port name for device %s (%s): %s.'
PORT_RESERVE_NONE = 'No ports specified in request.'
PORT_RESERVE_NOT_FOUND = 'Reservation %s not found.'
PORT_RESERVE_OCCUPIED = 'Occupied port %s cannot be reserved.'
PORT_RESERVE_PILOT_SITE = 'Port reservation disabled for Pop %s'
PORT_RESERVE_PLANNED = 'Planned port %s cannot be reserved.'
PORT_RESERVE_POP_TRACE = 'Unable to find Pop for device %s'
PORT_RESERVE_RESERVED = 'Port %s on device %s is already reserved.'
PORT_RESERVE_UNAVAILABLE = 'Port %s is unavailable.'
PORT_RESERVE_UNCONNECTED_DEVICES = 'Unconnected devices in %s.'
PORT_RESERVE_UNKNOWN_SPLICE_TOP_DEVICE = (
    'splice.top_device_key_name %s is unknown in splice %s (%s).')
PORT_RESERVE_NULL_SPLICE_CONNECTOR = (
    'splice.connector_key_name is null in splice %s (%s).')
PORT_STATUS_MANAGEMENT_MANUAL = 'Management status cannot be manually updated.'
PORT_STATUS_UPDATE_UNKNOWN_STATUS_TYPE = (
    'Invalid port status %s; no such status exists')
PORT_TRACE_EXCEPTION = 'Exception occurred in device %s.'
PORT_TRACE_EXCEPTION_SPECIFIC = 'Exception occurred in device %s on port %s.'
PORT_UNKNOWN_CONNECTOR_TYPE = (
    'Port %s with key name %s has unknown connector type %s.')
PORT_UNRECOGNIZED_LOGICAL = 'Unrecognized logical port status: %s.'
PORT_UNRECOGNIZED_PHYSICAL = 'Unrecognized physical port status: %s.'
PORT_UNRECOGNIZED_STATUS = 'Unrecognized port status value: %s.'
PORT_UPDATE_COLLIDE = 'Please refresh and retry port status update.'
PORT_WITHOUT_CONNECTOR_TYPE = 'Port %s with key name %s has no connector type.'
PORT_WITHOUT_NAME = 'Port with key name %s has no name.'
PORT_WITHOUT_TOP_DEVICE_KEY = (
    'Port %s with key_name %s does not have top_device_key_name.')
PORT_ZERO_PORT_NUMBER = (
    'Port %s with key name %s has 0 in port number which should '
    'be a positive number.')

# Port Map messages.
PORT_MAP_REQUIRED_MISSING = 'Required field %s not in port map CSV.'

# Socket Model related messages.
SOCKET_ATTACHED = 'Cannot delete socket with cable attached.'
SOCKET_INVALID_RACK = 'Whip/Socket insert attempted without valid rack!'
SOCKET_INVALID_SPACE = 'Whip/Socket insert attempted without valid space!'
SOCKET_INVALID_RACK_INPUT = (
    'Socket should have either Rack key_name or row/position!')
SOCKET_CREATE_FAIL = 'Fail to create socket. Unexpected Error: %s.'

# InfraCap messages.
INFRA_CAP_UNKNOWN_KEY = 'Unknown pop %s, vendor %s or logical device %s.'
INFRA_CAP_UNKNOWN_FIELD = 'Unknown field %s.'
INFRA_CAP_UNKNOWN_VENDOR = 'Unknown vendor %s.'
INFRA_CAP_BIG_QUERY_ERROR = 'BigQuery error: %s.'
INFRA_CAP_TOTAL_CAP_NOT_FOUND = (
    'Total cap not found for pop %s, vendor %s and logical device %s.')

# paths package error messages.
PATH_ELEMENTS_UNBALANCED = 'Unbalanced PathElements in Path %s.'
PATH_ELEMENT_PORT_ALREADY_IN_USE = 'Port %s is already in use for %s'
PORT_RES_TYPE_UNKNOWN = 'Reservation %s cannot be checked for %s'
PORT_RES_FALLOUT = 'Reservation %s has fallouts for path %s'
PORT_RES_END_DEVICE_MISMATCH = 'Reservation %s A/Z device mismatch for %s'
PORT_RES_END_ELEMENT_MISMATCH = 'Reservation %s A/Z element mismatch for %s'
PORT_RES_NOT_FOUND = 'Reservation %s has fallouts for path %s'
PORT_RES_REFERENCE_MISMATCH = 'Reservation %s ExternalReference mismatch for %s'

PATH_PANEL_NOT_FOUND = 'Panel not found for element: %s'
PATH_PANEL_PORT_NOT_FOUND = 'Panel port not found for element: %s'

# EMAIL package error messages.
EMAIL_NOT_FROM_RIVERMINE = 'Email not from Rivermine.'

# Access denied error while viewing import status.
ACCESS_DENIED = 'Current user does not have permission to view import status.'

# Mutex exception messages.
MUTEX_CANNOT_ACQUIRE = 'Cannot acquire mutex: %s.'
MUTEX_NONEXIST = 'Cannot release nonexistent mutex: %s.'
MUTEX_TIMED_OUT = 'Mutex %s may have timed out during operation.'
MUTEX_UNHELD = 'Cannot release unheld mutex: %s.'

# Cable and Strand error messages.
CABLE_INVALID = 'Cable does not exist.'
CABLE_NOT_FOUND = 'Cable with key_name %s not found.'
CABLE_CREATE_FAIL = 'Could not create cable on behalf of strand %s.'
CABLE_MEDIA_TYPE_UPDATE_FAIL = 'Cannot change cable media_type.'
STRAND_INVALID = 'Strand does not exist.'
STRAND_LENGTH_ERROR = (
    'Supplied number of strands must be greater than the number of '
    'strands on the cable.')
STRAND_CABLE_KEY_NAME_UPDATE_FAIL = 'Cannot change Cable__key_name.'
A_PORT_CONNECTOR_IN_USE = 'a_port_connector in use'
Z_PORT_CONNECTOR_IN_USE = 'z_port_connector in use'

# Permission error messages.
CREATE_NO_PERMISSION = ('User does not have permission to create entity of '
                        'type %s.')
DELETE_NO_PERMISSION = ('User does not have permission to delete entity of '
                        'type %s.')
UPDATE_NO_PERMISSION = ('User does not have permission to update %s '
                        'fields of %s type.')
READ_MODEL_PERMISSION_ERROR = (
    'User does not have table level read permissions on %s model.')
WRITE_MODEL_PERMISSION_ERROR = (
    'User does not have table level write permissions on %s model.')

PERMISSION_SCREEN_UPDATE = 'Only admin user can update the permissions.'
MODEL_LEVEL_WRITE_NO_PERMISSION = ('User does not have permission to write '
                                   'entity of type %s.')

SET_PERMISSIONS_READ_ACL_CONFLICT = (
    'For model %s, groups %s which have write access on column "%s" does not '
    'have read access.')
SET_PERMISSIONS_WRITE_ACL_CONFLICT = (
    '%s does not have write permission to columns %s')
INVALID_PERMISSION_TABLE = (
    'kind %s does not have columns defined in permission table.')

PERMISSIONS_UPDATE_ERROR = ('Only admin user groups %s can update the '
                            'permissions.')
BAD_CABLEPAIR_GET_REQUEST = (
    'Must supply cable_key_name, device_key_names '
    'or rack_key_name for cable pair content lookup.')
STRAND_SOCKET_DEVICE_KEY_NAME_ERROR = (
    'Cannot have both socket and device key names exist for the same '
    'end of a strand.')
STRAND_A_Z_SOCKET_KEY_NAME_CONFLICT = (
    'Cannot have socket key names on both A and Z ends for a strand.')
A_SOCKET_KEY_NAME_EXISTS_WITH_OTHER_CABLE = (
    'There is another cable already connected to the A end socket.')
Z_SOCKET_KEY_NAME_EXISTS_WITH_OTHER_CABLE = (
    'There is another cable already connected to the Z end socket.')

# Bazooka error messages.
BZ_GUNS_NOT_FOUND = 'GUNS not found in BZ for %s with object_id: %s'
SPECKLE_SOCKET_NAME_NOT_FOUND = (
    '"SPECKLE_SOCKET_NAME" not found in settings. '
    'Please add setting "SPECKLE_SOCKET_NAME".')

# Spectrum Design messages
SPECTRUM_DESIGN_MULTI_MANUFACTURERS = (
    'Multiple manufacturers for OMS %s: %s in circuit paths %s')
SPECTRUM_DESIGN_NO_MANUFACTURER = ('No manufacturer for OMS %s')
SPECTRUM_DESIGN_NOT_TEMPLATE_MANUFACTURER = (
    'Manufacturer %s is not in template in circuit path %s')
SPECTRUM_DESIGN_UNKNOWN_SPECTRUM = (
    'No OMS %s, spectrum %.04f in %s SpectrumDesign templates')
SPECTRUM_DESIGN_UNKNOWN_HARDWARE = (
    'No Hardware with logical_device %s, chassis %s, line_card %s, '
    'manufacturer %s')
SPECTRUM_DESIGN_INVALID_PART_NUMBERS = (
    'No part_numbers in Hardware with logical_device %s, '
    'chassis %s, line_card %s')
SPECTRUM_DESIGN_UNKNOWN_HW_PART_MAPPING = (
    'No HardwarePartsMapping with part_number %s')
SPECTRUM_DESIGN_UNKNOWN_PART = ('No Part with part_keys %s')
SPECTRUM_DESIGN_NO_UNIT_DETAILS = ('No unit_details in Part with part_keys %s')
SPECTRUM_DESIGN_UNKNOWN_LSOPTICS = (
    'No LSOptics with unit_detail %s, manufacturer %s')
SPECTRUM_DESIGN_UNKNOWN_OMS_ID = ('No oms_id %s in OMS table')

# Reput Errors
REPUT_CLEAN_ENABLED = 'Cleaning entity "%s" of %s kind.'
REPUT_CLEAN_FAILURE = ('Error occurred in RePut of entity "%s" of type '
                       '"%s" during clean operations. Errors: %s')

# Circuit messages.
CIRCUIT_CAPREF_FAIL = ('Cannot create CapacityReference__name for %s and %s.')
CIRCUIT_CANNOT_CREATE = ('Circuit cannot be created.')
CIRCUIT_CANNOT_DELETE = (
    'Circuit %s cannot be deleted with commissioning_status %s.')
CIRCUIT_DEVICE_ERR = ('Cannot parse devices for %s and %s.')
CIRCUIT_EMPTY_RAW_PATH = ('Empty raw_path.')
CIRCUIT_ID_HAS_NO_POPS = ('Circuit (%s -> %s) has no POP names in Circuit ID.')
CIRCUIT_IDENTICAL_STATUS = (
    'Identical commissioning_status %s in UpdateStatus.')
CIRCUIT_INVALID_A_DEV = ('Mismatching NetworkConnection.a_device_key_name %s, '
                         'Circuit.a_logical_device_key_name %s.')
CIRCUIT_INVALID_CIRCUIT_ID = ('Invalid circuit id %s with origin %s.')
CIRCUIT_DELETE_INVALID_ORIGIN = ('Cannot delete circuit %s with origin %s.')
CIRCUIT_INVALID_CONTINENTS = (
    'Mismatching NetworkConnection.metro_continent %s, Circuit.continent %s.')
CIRCUIT_INVALID_FRAMING = ('Invalid %s.framing [%s]: %s.')
CIRCUIT_INVALID_KIND = 'Invalid circuit family.'
CIRCUIT_INVALID_METROS = (
    'Mismatching NetworkConnection.metro_name %s, Circuit.metros %s.')
CIRCUIT_INVALID_REGIONS = (
    'Mismatching NetworkConnection.metro_region %s, Circuit.region %s.')
CIRCUIT_INVALID_STATUS = ('Invalid %s.commissioning_status [%s]: %s.')
CIRCUIT_INVALID_NETWORKCONNECTION_KEY_NAME = (
    'Invalid NetworkConnection__key_name %s.')
CIRCUIT_INVALID_Z_DEV = ('Mismatching NetworkConnection.z_device_key_name %s, '
                         'Circuit.z_logical_device_key_name %s.')
CIRCUIT_NO_A_DEV = ('Null Circuit a_device_key_name.')
CIRCUIT_NO_Z_DEV = ('Null Circuit z_device_key_name.')
CIRCUIT_NO_FUNCTION = ('Cannot get capacity functions for %s and %s.')
CIRCUIT_NO_METROS = ('Cannot get metros from %s and/or %s.')
CIRCUIT_NO_REQUIRED_FIELDS = ('Circuit does not have all the required fields.')
CIRCUIT_STATUS_UPDATE_ERROR = (
    'Circuit commissioning_status cannot be updated along '
    'with other fields: %s.')
CIRCUIT_UNKNOWN_CIRCUIT_ID = ('Unknown circuit id %s.')

# CircuitElement messages.
CIRCUIT_ELEMENT_AND_CIRCUIT_MISMATCH = (
    'Mismatching Circuit vs. CircuitElement: %s.')
CIRCUIT_ELEMENT_AND_SUB_CIRCUIT_MISMATCH = (
    'Mismatching SubCircuit vs. CircuitElement: %s.')
CIRCUIT_ELEMENT_BATCH_CREATE_ERROR = (
    'Cannot batch create the circuit elements in non-empty circuit %s '
    'having %d circuit elements already.')
CIRCUIT_ELEMENT_COUNT_MISMATCH = (
    'New CircuitElements (%d) does not match existing entities (%d).')
CIRCUIT_ELEMENT_DELETE_NOT_SUPPORTED = (
    'Individual CircuitElement cannot be deleted. '
    'Need to delete the Circuit instead.')
CIRCUIT_ELEMENT_DEV_KEY_NAME_UPDATE_ERROR = (
    'Device__key_name updates not allowed for A/Z end circuit elements '
    'from %s to %s.')
CIRCUIT_ELEMENT_FOREIGN_DEV_NAME_UPDATE_ERROR = (
    'foreign_device_name updates not allowed for A/Z end circuit elements '
    'from %s to %s.')
CIRCUIT_ELEMENT_INVALID_ELEMENT_ID = (
    'CircuitElement has invalid element_id %s, expecting %s.')
CIRCUIT_ELEMENT_INVALID_FIELD = (
    'CircuitElement has invalid fields: %s.')
CIRCUIT_ELEMENT_INVALID_ORIGIN = (
    'CircuitElement has invalid origin %s, Circuit.origin %s.')
CIRCUIT_ELEMENT_INVALID_PARENT = (
    'CircuitElement %s should not have both Circiut__key_name and '
    'SubCircuit__key_name: %s and %s.')
CIRCUIT_ELEMENT_INVALID_RAW_ELEMENT = (
    'CircuitElement has invalid raw_element %s, expecting %s.')
CIRCUIT_ELEMENT_NO_PARENT = (
    'CircuitElement %s does not have valid parent key name.')
CIRCUIT_ELEMENT_NOT_IN_SAME_CIRCUIT = (
    'CircuitElements are bound to multiple circuits: %s.')
CIRCUIT_ELEMENT_UNKNOWN_ELEMENT_ID = ('Unknown circuit element id %s.')

# ACT path creation messages.
CIRCUIT_ACT_CIRCUIT_COUNT_ERROR = ('Circuit count error: %d.')
CIRCUIT_ACT_CONNECTION_CNT_ERROR = (
    'Mismatching connection count. circuit_element[0]: %d, '
    'circuit_element[%d]: %d.')
CIRCUIT_ACT_DEVICE_TYPE_ERROR = (
    'The circuit_element[%d].connections[0] represents %s device, '
    'but the circuit_element[%d].connections[%d] does not.')
CIRCUIT_ACT_INACTIVE_RESERVATION_INFO = (
    'No active reservation found for circuit_element[%d] '
    'with client_id %s, client_reservation_id %s. '
    'Current reservation has %s status.')
CIRCUIT_ACT_INVALID_CONNECTIONS = (
    'The circuit_element[%d] does not have connections.')
CIRCUIT_ACT_INVALID_DEV_NAME = (
    'Unknown device_name in circuit_element[%d]: %s.')
CIRCUIT_ACT_INVALID_OFFSET_IN_RESERVATION_INFO = (
    'Invalid offset %0d (port index: %0d, front port count: %0d) '
    'in circuit_element[%d] for %s (%s)')
CIRCUIT_ACT_MIN_DEV_PORTS = ('Less than minimum device/ports: %d < %d.')
CIRCUIT_ACT_NO_CONNECTION = (
    'No connection in DeviceConnectivityView between %s '
    '(%s) in circuit_element[%d] and %s (%s) in circuit_element[%d]: %s.')
CIRCUIT_ACT_NO_MATCHING_RESERVATION_INFO = (
    'No matching port reservation in circuit_element[%d] '
    'with device_name %s, client_id %s, client_reservation_id %s.')
CIRCUIT_ACT_NO_CONNECTIONS = ('No connections in circuit_element[%d].')
CIRCUIT_ACT_NO_OFFSET_IN_RESERVATION_INFO = (
    'Missing offset in '
    'circuit_element[%d].connections[%d].')
CIRCUIT_ACT_NO_PORT = ('No ports in circuit_element[%d].')
CIRCUIT_ACT_NO_PORT_CONNECTIONS = (
    'The ports %s in %s (circuit_element[%d].connections[%d]) '
    'are not connected to the ports %s in %s '
    '(circuit_element[%d].connections[%d]).')
CIRCUIT_ACT_NONE_CONNECT_REQUEST = ('ConnectACTPathsRequest is None.')
CIRCUIT_ACT_PORT_CONNECTION_CNT_ERROR = (
    'Mismatching port connector count. circuit_element[0]: %d, '
    'circuit_element[%d]: %d.')
CIRCUIT_ACT_PORT_ERROR_INVALID_ARG = (
    'Null element/device/port_names for port validation '
    'in circuit_element[%d].')
CIRCUIT_ACT_UNAVAILABLE_PORTS = (
    'All the ports in Device %s in circuit_element[%d] are not available.')
CIRCUIT_ACT_UNAVAILABLE_RESERVED_PORTS = (
    'All the reserved ports in Device %s in circuit_element[%d] are '
    'not available: %s.')
CIRCUIT_ACT_UNKNOWN_PORT_IN_RESERVATION_INFO = (
    'Port %s:%s in local_index %0d (port offset in reservation: %0d) '
    'is not reserved with (client_id: %s, reservation_id: %s) '
    'in circuit_element[%d].')
CIRCUIT_ACT_UNKNOWN_RESERVATION_INFO = (
    'No reservation found for circuit_element[%d] '
    'with client_id %s, client_reservation_id %s.')
CIRCUIT_ACT_UNKNOWN_RESERVED_PORT = (
    'Reserved ports %s not defined in Device %s in circuit_element[%d].')

ACT_CLOUD_STORAGE_WRITE_ERROR = (
    'Cannot write to Cloud Storage file %s, contents %s. Exception: %s'
)
ACT_CLOUD_STORAGE_READ_ERROR = (
    'Cannot read from Cloud Storage file %s. Exception: %s'
)
ACT_UNM_A_ENTITY_ERROR = 'Expected one A-entity for %s %s %s::%s.'
ACT_UNM_ERROR = (
    'Error on parsing %s in EK_PHYSICAL_PACKET_LINK %s.')
ACT_UNM_EXCEPTION = (
    'Exception on parsing %s in EK_PHYSICAL_PACKET_LINK %s: %s.')
ACT_UNM_INVALID_DEV_NAME = (
    'Unknown device_name %s in EK_PHYSICAL_PACKET_LINK %s.')
ACT_UNM_INVALID_TEST_FILE = 'Read UNM model from test file %s failed: %s.'
ACT_UNM_MISSING_RESV_INFO = (
    'Invalid client_id %s or reservation_id %s in EK_PORT %s.')
ACT_UNM_NO_MODEL_NAME = 'model_name should not be None.'
ACT_UNM_NO_PHYSICAL_PACKET_LINK = 'EK_PHYSICAL_PACKET_LINK not found in %s.'
ACT_UNM_NO_A_PORT = 'EK_PHYSICAL_PACKET_LINK %s does not have a-end port.'
ACT_UNM_NO_Z_PORT = 'EK_PHYSICAL_PACKET_LINK %s does not have z-end port.'
ACT_UNM_PATH_ERROR = 'ACT UNM path model error: %s.'
ACT_UNM_RPC_ERROR = 'Exception reading model %s from %s: %s.'
ACT_UNM_Z_ENTITY_ERROR = 'Expected one Z-entity for %s::%s %s %s.'
ACT_UNM_PATHS_DESERIALIZE_ERROR = 'Unable to deserialize unm_paths.'
ACT_ZERO_PATH_ELEMENTS_ERROR = 'unm path %s has 0 unm path elements.'

# SubCircuit messages.
SUB_CIRCUIT_INVALID_PARENT = (
    'SubCircuit %s should not have both Circiut__key_name and '
    'SubCircuit__key_name: %s and %s.')
SUB_CIRCUIT_NO_PARENT = 'SubCircuit %s does not have valid parent key name.'
SUB_CIRCUIT_UNKNOWN_ID = 'Unknown sub-circuit id %s.'

# Chipmunk path creation messages.
CHIPMUNK_PATH_CREATE_FAILED = 'Chipmunk path creation failed for %s: %s'
CHIPMUNK_PATH_CREATE_RPC_ERROR = 'Unable to reach CircuitsManagerService: %s'
CHIPMUNK_PATH_DELETE_API_ERROR_NULL_PATH_ID = 'Path id is empty'
CHIPMUNK_PATH_DELETE_RPC_ERROR = 'Unable to reach CircuitsManagerService: %s'
STOAT_LOCK_ERROR = 'Could not lock'
STOAT_CACHE_OUT_OF_SYNC_ERROR = ('Stoat server cache out of sync. Please '
                                 'retry after some time.')

# Stoat path validation messages.
PATH_VALIDATION_FAILED = 'Path validation failed for %s: %s'
PATH_VALIDATION_RPC_ERROR = 'Unable to reach PathValidationService: %s'

# Capacity messages
CANNOT_DECOMM_WITH_CHILD = (
    'Cannot update the status to Decommed with active children for %s')
TRAFFIC_GROUP_MISSING = (
    'Traffic Group is required when include_in_dashboard is set.')
IMPORT_FUNCTION_MISSING = (
    'Import Function is required when include_in_dashboard is set.')


# Setting related Errors.
FLOAT_SETTING_INVALID = 'Setting %s requested by ReadFloat is not a float.'
INT_SETTING_INVALID = 'Setting %s requested by ReadInt is not an int.'

# FK Ancestry related messages
ENTITY_KIND_NOT_PROVIDED = 'Expecting an entity kind.'
ENTITY_INSTANCE_NOT_PROVIDED = 'Expecting an entity instance.'
ENTITY_NOT_IN_ANCESTRY = 'Entity kind: %s not in ancestry.'
END_ENTITY_NOT_IN_ANCESTRY = 'End Entity kind: %s not in ancestry.'

# Search API error messages.
INVALID_KEYNAME_IN_SEARCH = 'Invalid keyname for %s %s in Search API: %s'
VALUE_ERROR_IN_SEARCH = 'ValueError in Search API for index %s: %s'
ERROR_IN_SEARCH = 'Exception in Search API for index %s: %s'
SEARCH_ILLEGAL_INDEX_NAME = ('ReIndexPipeline skipping %r because it is not a '
                             'valid search index name: %s')
SEARCH_FIELD_ERROR = 'Cannnot add search field value for %r: %s'

# Device naming related messages.
ANCESTRY_NOT_FOUND = 'No Ancestry for device: %s.'
BUILDING_NOT_FOUND = 'Building not found for device %s.'
CORP_DEVICE_NAMED = 'Corp %s: %s, name: %s, sequencing attr: %s.'
CORP_DEVICE_NO_REWS_ID = (
    'Corp %s: %s, rews_id undefined; building: %s, rews_id: %s.')
DEVICE_ANCESTRY = 'Ancestry is %s.'
HWOPS_NGF_PANEL_HAS_INVALID_RAIL = (
    'Hwops ngf panel: %s, rack rail: %s is invalid; expecting <= %s.')
HWOPS_NGF_PANEL_HAS_INVALID_RMU = (
    'Hwops ngf panel: %s, rmu %s, is invalid; expecting <= %s.')
HWOPS_NGF_PANEL_NAMED = 'Hwops ngf panel: %s, rack rail: %s, name: %s.'
HWOPS_NON_NGF_PANEL_NAMED = 'Hwops panel: %s, name: %s, sequencing attr: %s.'
HWOPS_NON_NGF_SPACE_FUNCTION_INVALID = (
    'Hwops panel: %s, space function not recognized: %s.')
HWOPS_DEVICE_NO_POP = 'Hwops %s: %s, pop is undefined.'
NOT_A_AUTONAMED_DEVICE = (
    'Device %s, type %s does not have special naming rules.')
REWS_ID_NOT_FOUND = 'REWS ID not found for building named %s.'
UNRECOGNIZED_DEVICE_CATEGORY = 'Device %s: type: %s, category: %s is invalid.'
VENDOR_PANEL_NAMED = 'Vendor panel: %s, name: %s.'
GOOGLE_DEVICE_RMU_DOESNT_EXIST = ('Google %s: rmu does not exist for '
                                  'device %s.')
GOOGLE_DEVICE_NO_POP = 'Google %s: %s, pop is undefined.'

# Device rename related messages.
DEVICE_NAME_UNCHANGED_DUP_NAME = (
    'Name of this device cannot be changed: %s, fqn: %s, '
    'sequencing attr %s, exists')
DEVICE_NAME_UNCHANGED_CATEGORY_INVALID = (
    'Name of this device cannot be changed: %s, fqn: %s, '
    'Device type is unsupported: %s')
DEVICE_NAME_UNCHANGED_NAME_REQUIRED = (
    'Name of this device cannot be changed: Name is required.')
DEVICE_NAME_UNCHANGED_RE_MISMATCH = (
    'Name of this device cannot be changed: Name %s does not follow rules: %s')
DEVICE_NAME_UNCHANGED_REWS_ID_MISMATCH = (
    'Rews-id component of device name may not be changed: Old: %s, New: %s.')
DEVICE_NAME_UNCHANGED_NAMESEQUENCE_REQUIRED = (
    'The existing device %s, fqn: %s, has no namesequence for %s.')
# Device rename related log messages.
NAMESEQUENCE_RESET = (
    'Device rename: %s->%s, NameSequence for %s was reset to %s, was %s.')
NAMESEQUENCE_DELETED = (
    'Device rename: %s->%s, NameSequence for %s was deleted, was %s.')

# Traffic related error messages.
TRAFFIC_MISSING_FIELDS = 'Required fields are missing'
TRAFFIC_INVARIANT_MISSING_DELIVERABLE = 'Missing Deliverable info for %s'

# Datapropagation related messages.
ERRORKEY_BADTRIGGER = 'Invalid Trigger.'
ERRORKEY_BADAUTHSOURCE = 'Invalid Authoritative Source.'
ERRORMSG_BADKWARGFORMAT = (
    'Invalid provided Kwarg format; Kwargs must be dict object.')
ERRORMSG_SELFTRIGGER = 'A field (%s) cannot target itself.'
ERRORMSG_FIELDNOTFOUND = 'Field (%s) not found in model: %s.'
ERRORMSG_CANTINITIATE = 'Can\'t Initiate Trigger; No Entity Detected.'
ERRORMSG_TRIGGERNAMEEXISTS = (
    'A Trigger with this name (%s) for this Kind (%s) '
    'and Field (%s) already exists.')
ERRORMSG_NOMAP = 'Can\'t Initiate Trigger; No Trigger Map Loaded.'

# FiberConnection related messages.
FIBER_CONNECTION_CONVERSION_FAILED = (
    'Couldn\'t convert to FiberConnection object.')
FIBER_CONNECTION_SPLICE_STRAND_LIST_EMPTY = (
    'splice_strand_list can\'t be empty.')
FIBER_CONNECTION_SPLICE_NOT_TERM = '%s should be a term or edge splice.'
FIBER_CONNECTION_Z_SPLICE_WRONG_POSITION = (
    'Expected term/egde splice at the end of strand_splice_list.')

# ThirdPartyTransport related messages.
A_Z_ALPHABETICALLY_ORDERED = (
    'The A/Z ends %s/%s must be ordered alphabetically.')
OTS_SINGLE_BU = (
    'Branching units can be specified in either A or Z end but not both.')
JOINT_FAILURE_PROBABILITY = ('Joint Failure Probability is required if either '
                             'Overlapping Distance or Separation Distance is '
                             'missing.')
REQUIRE_OMS_OR_3PT = ('For each Physical SPOF, there should be at least one '
                      'OMS span or 3PT entry')

# NetcrackerSync related error messages.
NCSYNC_STUBBY_HOST_NOT_FOUND = '%s -- Stubby host not found'

# Pipeline/job related error messages.
JOBSTATUS_JOB_ID_NOT_FOUND = 'Job id %s not found.'
PIPELINE_CALLBACK_TASK_NOT_ADDED = '%s -- Failed to add callback task.'

# Sculptor error messages.
INVALID_SCULPTOR_HANDLER = 'Sculptor blade address %s not valid'

# Sculptor update error.
UPDATE_PATH_ERROR = 'There was an error updating stoat path %s'
CIRCUIT_FIX_REQUIRED = ('This circuit path %s requires manual fix'
                        ' to add available ports.')
INVALID_CIRCUIT_STATE = ('ASBUILT Circuit %s should be decommissioned in Stoat'
                         ' first to change the status of the port to broken.')
SCULPTOR_UPDATE_FAIL = 'Could not update stoat paths for broken port %s'
DEVICE_NOT_PATCH_PANEL = 'Parent device %s of port %s must be patch panel type'
INVALID_PORT_LOGICAL_STATUS = (
    'Invalid port logical status %s. Please decomission the circuit in Stoat'
    ' first to mark this port %s as broken.')
NO_Z_PATH_ELEMENT = 'Z Path element not found for A port %s'
NO_Z_END_DEVICE = 'No Z End device for this A port %s'
