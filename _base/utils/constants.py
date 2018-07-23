import collections
import re
import string

#
# App identity settings.
#
APP_IDENTITY_DEV = 'google.com:netdesign-dev'
APP_IDENTITY_TEST = 'google.com:netdesign-test'
APP_IDENTITY_DEMO = 'google.com:netdesign-demo'
APP_IDENTITY_STAGING = 'google.com:netdesign-staging'
APP_IDENTITY_PRODBACKUP = 'google.com:netdesign-prodbackup'
APP_IDENTITY_ACT = 'google.com:netdesign-act'
APP_IDENTITY_ACT2 = 'google.com:netdesign-act2'
APP_IDENTITY_PROD = 'google.com:netdesign'
APP_IDENTITY_ANT = 'google.com:netdesign-ant'
APP_IDENTITY_ANTBOM = 'google.com:netdesign-antbom'
APP_IDENTITY_TESTBED = 'testbed-test'
APP_IDENTITY_DEVAPPSERVER = 'auto'
DEFAULT_MODULE_NAME = 'default'
IMPORT_MODULE_NAME = 'importer'

#
# App Engine server map.
#
SERVERS = {
    'local': ('localhost:9000', 'dev~auto'),
    'dev': ('netdesign-dev.googleplex.com', 's~google.com:netdesign-dev'),
    'test': ('netdesign-test.googleplex.com', 's~google.com:netdesign-test'),
    'demo': ('netdesign-demo.googleplex.com', 's~google.com:netdesign-demo'),
    'staging': ('netdesign-staging.googleplex.com',
                's~google.com:netdesign-staging'),
    'prodbackup': ('netdesign-prodbackup.googleplex.com',
                   's~google.com:netdesign-prodbackup'),
    'act': ('netdesign-act.googleplex.com', 's~google.com:netdesign-act'),
    'ant': ('netdesign-ant.googleplex.com', 's~google.com:netdesign-ant'),
    'antbom': ('netdesign-antbom.googleplex.com',
               's~google.com:netdesign-antbom'),
    'act2': ('netdesign-act2.googleplex.com', 's~google.com:netdesign-act2'),
    'prod': ('netdesign.googleplex.com', 's~google.com:netdesign'),
    'testbed': (None, None),
}

#
# Tasks module related settings.
#
TASKS_MODULE_NAME = 'tasks'

# Queue names.
ACT_QUEUE_NAME = 'act'
BACKUP_QUEUE_NAME = 'backup'
BATCH_QUEUE_NAME = 'batch'
BOM_QUEUE_NAME = 'bom-jobs'
DB_RESTORE_QUEUE_NAME = 'db-restore'
FK_QUEUE_NAME = 'fks'
EXTERNAL_QUEUE_NAME = 'external'
EXTERNAL_BAZOOKA_QUEUE_NAME = 'external-bazooka'
EXTERNAL_HARDWARE_QUEUE_NAME = 'external-hardware'
EXTERNAL_TRAFFIC_QUEUE_NAME = 'external-traffic'
EXTERNAL_NCSYNC_QUEUE_NAME = 'external-ncsync'
HISTORY_QUEUE_NAME = 'history'
IMPORTER_QUEUE_NAME = 'importer'
TASKS_QUEUE_NAME = TASKS_MODULE_NAME
UNM_EXPORT_QUEUE_NAME = 'unm-export'
UNM_UPDATE_QUEUE_NAME = 'unm-update'

# The base application module. Used for relative imports.
BASE_MODULE = '_base'

# Constants for metadata.
METADATA_BACKUP = 'backup'
METADATA_UPDATE_SEARCH = 'update_search'

# A list of modules to search for Models (relative to BASE_MODULE). The order
# of the modules is not maintained, and every Model should have a unique name.
MODEL_MODULES = ()
# MODEL_MODULES = (
#     '.admin.admin_models',
#     '.bigquery.bigquery_models',
#     '.capacity.capacity_models',
#     '.bom.bom_item_models',
#     '.bom.bom_models',
#     '.btp.btp_models',
#     '.cables.cable_models',
#     '.circuits.circuit_models',
#     '.circuits.circuit_element_models',
#     '.circuits.subcircuits.sub_circuit_models',
#     '.common.common_models',
#     '.capacity.activities_models',
#     '.devices.device_models',
#     '.devices.logical_device_models',
#     '.devices.splice_models',
#     '.email.email_models',
#     '.fallout.fallout_models',
#     '.file_attachments.file_attachments_models',
#     '.hardware.hardware_models',
#     '.history.history_models',
#     '.importer.importer_models',
#     '.locations.building.building_models',
#     '.locations.floor.floor_models',
#     '.locations.inventory.inventory_location_models',
#     '.locations.osp_container.osp_container_models',
#     '.locations.space.space_models',
#     '.locations.subbuilding.subbuilding_models',
#     '.locations.location_models',
#     '.logical_locations.logical_location_models',
#     '.logs.logs_models',
#     '.manufacturers.manufacturer_models',
#     '.metadata.metadata_models',
#     '.mutex.mutex_models',
#     '.netcracker.netcracker_models',
#     '.on_network_inventory_mapping.on_network_inventory_mapping_models',
#     '.optical_span.optical_span_models',
#     '.orders.order_item_models',
#     '.orders.order_models',
#     '.parts.part_models',
#     '.paths.path_models',
#     '.permissions.permission_models',
#     '.ports.port_status_models',
#     '.ports.reservation_models',
#     '.racks.rack_models',
#     '.recon.device_recon_models',
#     '.sequences.sequence_models',
#     '.sockets.socket_models',
#     '.traffic.traffic_models',
#     '.user.user_preference_models',
#     '.vcs.vcs_refs',
#     '.vendors.vendor_models',
#     '.transport.physical_spof.physical_spof_models',
#     '.transport.submarine_oms_ots.submarine_oms_ots_models',
#     '.transport.thirdparty_transport.thirdparty_transport_models',
#     '.transport.transport_models',
#     '.circuits.act_path_tx_models',
#     '.netcracker.bazooka_models',
#     '.cron.cron_models',)

# Groups.
DH_ADMIN_GROUP = '%doublehelix-admin'
DH_DESIGN_GROUP = '%doublehelix-design'
DH_RO_GROUP = '%doublehelix-ro'
DH_RW_GROUP = '%doublehelix-rw'
DH_SUPPLYCHAIN_GROUP = '%doublehelix-supplychain'
DH_SUPPLYCHAIN_LOGISTICS_TVCS_GROUP = '%doublehelix-supplychain-logistics-tvcs'
DH_SUPPLYCHAIN_PLANNER_TVCS_GROUP = '%doublehelix-supplychain-planner-tvcs'
NETDESIGN_GROUP = '%netdesign'

# Default model permissions.
# Keep in sync with matching client constants.
PERMISSIONS_DEFAULT_READ = [
    DH_ADMIN_GROUP,
    DH_DESIGN_GROUP,
    DH_RO_GROUP,
    DH_RW_GROUP,
    DH_SUPPLYCHAIN_GROUP,
    NETDESIGN_GROUP,
]

PERMISSIONS_DEFAULT_WRITE = [
    DH_ADMIN_GROUP,
    DH_DESIGN_GROUP,
    DH_RW_GROUP,
    DH_SUPPLYCHAIN_GROUP,
    NETDESIGN_GROUP,
]

# The processes which can update the model permissions
ADMIN_SCREEN = 'Admin screen'
PERMISSIONS_YAML_UPLOAD = 'Permissions yaml upload'
METADATA_UPDATES = 'Metadata updates'

# The environments label
ENV_PROD = 'prod'
ENV_STAGING = 'staging'
ENV_PRODBACKUP = 'prodbackup'

# TODO(logant@) Put all DH application settings constants here.
# Application setting constants
DH_SETTING_BTP_ERROR_NOTIFY_ADDRESS = 'BTP_ERROR_NOTIFY_ADDRESS'

# Constants for SpaceContents/Rack View Generation.
DEEP_DEVICE_PERCENT = 0.75
DEFAULT_RU_TOLERANCE = 0.15

# Constants for GeoSpatial/Map View objects.
GEOCODING_SCOPE = 'https://www.googleapis.com/auth/orgstore'
GEOCODING_URI = 'http://maps.googleapis.com/maps/api/geocode/json?sensor=false'

# Constants used in rack/device templates.
DL_CODE_INSTANCE = 'INSTANCE'
DL_CODE_TEMPLATE = 'TEMPLATE'
TEMPLATE_KEY_NAME = 'template_key_name'

# ACL file.
ACL_FILE = 'authz.yaml'
SERVER_BASE_PATH = 'google3/ops/netdeploy/netdesign/server'
# The value of SERVER_PATH changes for tests.
SERVER_PATH = SERVER_BASE_PATH

# Bundle file names.
RIBBON_FILENAME = 'ribbon.yaml'
METADATA_FILE_END = '_metadata.yaml'
METADATA_FILE_LIST = 'metadata_file_list.yaml'
UNMANAGED_FILE_LIST = 'training/data/unmanaged_file_list.yaml'

# BigQuery query related settings.
BIGQUERY_CATALOG = 'double_helix_tables'
BIGQUERY_TABLEVIEW_KIND = 'BigQuery'
# Increment this prefix anytime the content format changes.
BIGQUERY_MEMCACHE_PREFIX = BIGQUERY_TABLEVIEW_KIND + 'V2:'
BIGQUERY_MEMCACHE_TIMEOUT = 60 * 60  # 1 hour.
BIGQUERY_MAX_MEMCACHE_TIMEOUT = 24 * 60 * 60  # 24 hours
BIGQUERY_IMPORT_TABLE_PREFIX = 'bq_'

# Project ID for BigQuery.
BIGQUERY_PROJECT_ID_MAP = collections.defaultdict(
    lambda: APP_IDENTITY_TESTBED,  # Default factory.
    **{
        APP_IDENTITY_DEV: APP_IDENTITY_DEV,
        APP_IDENTITY_TEST: APP_IDENTITY_TEST,
        APP_IDENTITY_DEMO: APP_IDENTITY_DEMO,
        APP_IDENTITY_STAGING: APP_IDENTITY_STAGING,
        APP_IDENTITY_PRODBACKUP: APP_IDENTITY_PRODBACKUP,
        APP_IDENTITY_ACT: APP_IDENTITY_ACT,
        APP_IDENTITY_ANT: APP_IDENTITY_ANT,
        APP_IDENTITY_ANTBOM: APP_IDENTITY_ANTBOM,
        APP_IDENTITY_ACT2: APP_IDENTITY_ACT2,
        APP_IDENTITY_PROD: 'google.com:googlenetdesign',
    })

#
# Google Cloud Storage related settings.
#

GS = 'gs'
GS_ARCHIVE = '/archive/'
GS_DELIMITER = '/'
GS_BACKUP = 'BACKUP'
GS_CSVIMPORT = 'CSVIMPORT'
GS_DOWNLOADS = 'DOWNLOADS'
GS_EXPORT = 'EXPORTS'
GS_LEASEDINVENTORY = 'LEASEDINVENTORY'

# Bucket name for cloud storage backup.
GS_BACKUP_BUCKET_MAP = collections.defaultdict(
    lambda: 'doublehelixbackup_local',  # Default factory.
    **{
        APP_IDENTITY_PROD: 'doublehelixbackup',
        APP_IDENTITY_DEV: 'doublehelixbackup_dev',
        APP_IDENTITY_DEMO: 'doublehelixbackup_demo',
        APP_IDENTITY_TEST: 'doublehelixbackup_test',
        APP_IDENTITY_STAGING: 'doublehelixbackup_staging',
        APP_IDENTITY_PRODBACKUP: 'doublehelixbackup_prodbackup',
        APP_IDENTITY_ACT: 'doublehelixbackup_act',
        APP_IDENTITY_ACT2: 'doublehelixbackup_act2',
        APP_IDENTITY_ANT: 'doublehelixbackup_ant',
        APP_IDENTITY_ANTBOM: 'doublehelixbackup_antbom',
    })

GS_CSVIMPORT_BUCKET_MAP = collections.defaultdict(
    lambda: 'doublehelix-csvimport-local',  # Default factory.
    **{
        APP_IDENTITY_PROD: 'doublehelix-csvimport',
        APP_IDENTITY_DEV: 'doublehelix-csvimport-dev',
        APP_IDENTITY_DEMO: 'doublehelix-csvimport-demo',
        APP_IDENTITY_TEST: 'doublehelix-csvimport-test',
        APP_IDENTITY_STAGING: 'doublehelix-csvimport-staging',
        APP_IDENTITY_PRODBACKUP: 'doublehelix-csvimport-prodbackup',
        APP_IDENTITY_ACT: 'doublehelix-csvimport-act',
        APP_IDENTITY_ACT2: 'doublehelix-csvimport-act2',
        APP_IDENTITY_ANT: 'doublehelix-csvimport-ant',
        APP_IDENTITY_ANTBOM: 'doublehelix-csvimport-antbom',
    })

# Cloud storage bucket location for cron job outputs.
GS_DOWNLOADS_BUCKET_MAP = collections.defaultdict(
    lambda: 'doublehelixdownloads_local',  # Default factory.
    **{
        APP_IDENTITY_PROD: 'doublehelixdownloads',
        APP_IDENTITY_DEV: 'doublehelixdownloads_dev',
        APP_IDENTITY_DEMO: 'doublehelixdownloads_demo',
        APP_IDENTITY_TEST: 'doublehelixdownloads_test',
        APP_IDENTITY_STAGING: 'doublehelixdownloads_staging',
        APP_IDENTITY_PRODBACKUP: 'doublehelixdownloads_prodbackup',
        APP_IDENTITY_ACT: 'doublehelixdownloads_act',
        APP_IDENTITY_ACT2: 'doublehelixdownloads_act2',
        APP_IDENTITY_ANT: 'doublehelixdownloads_ant',
        APP_IDENTITY_ANTBOM: 'doublehelixdownloads_antbom',
    })

# Cloud storage bucket location for user triggered export/download items.
GS_EXPORT_BUCKET_MAP = collections.defaultdict(
    lambda: 'doublehelixexport_local',  # Default factory.
    **{
        APP_IDENTITY_PROD: 'doublehelixexport',
        APP_IDENTITY_DEV: 'doublehelixexport_dev',
        APP_IDENTITY_DEMO: 'doublehelixexport_demo',
        APP_IDENTITY_TEST: 'doublehelixexport_test',
        APP_IDENTITY_STAGING: 'doublehelixexport_staging',
        APP_IDENTITY_PRODBACKUP: 'doublehelixexport_prodbackup',
        APP_IDENTITY_ACT: 'doublehelixexport_act',
        APP_IDENTITY_ACT2: 'doublehelixexport_act2',
        APP_IDENTITY_ANT: 'doublehelixexport_ant',
        APP_IDENTITY_ANTBOM: 'doublehelixexport_antbom',
    })

GS_EXPERIMENTAL_BUCKET_MAP = collections.defaultdict(
    lambda: 'doublehelixexperimental',
    **{
        APP_IDENTITY_PROD: 'doublehelixexperimental',
    })

GS_LEASEDINVENTORY_BUCKET_MAP = collections.defaultdict(
    lambda: 'doublehelixleasedinventory_local',  # Default factory.
    **{
        APP_IDENTITY_PROD: 'doublehelixleasedinventory',
        APP_IDENTITY_DEV: 'doublehelixleasedinventory_dev',
        APP_IDENTITY_DEMO: 'doublehelixleasedinventory_demo',
        APP_IDENTITY_TEST: 'doublehelixleasedinventory_test',
        APP_IDENTITY_STAGING: 'doublehelixleasedinventory_staging',
        APP_IDENTITY_PRODBACKUP: 'doublehelixleasedinventory_prodbackup',
        APP_IDENTITY_ACT: 'doublehelixleasedinventory_act',
        APP_IDENTITY_ACT2: 'doublehelixleasedinventory_act2',
        APP_IDENTITY_ANT: 'doublehelixleasedinventory_ant',
        APP_IDENTITY_ANTBOM: 'doublehelixleasedinventory_antbom',
    })

# Bucket locations from which users can download files from UI.
GS_REPORT_BUCKET_MAPS = (GS_DOWNLOADS_BUCKET_MAP,
                         GS_EXPORT_BUCKET_MAP,
                         GS_LEASEDINVENTORY_BUCKET_MAP)

GS_BUCKET_MAPS = collections.defaultdict(
    lambda: GS_EXPERIMENTAL_BUCKET_MAP,
    **{
        GS_BACKUP: GS_BACKUP_BUCKET_MAP,
        GS_DOWNLOADS: GS_DOWNLOADS_BUCKET_MAP,
        GS_CSVIMPORT: GS_CSVIMPORT_BUCKET_MAP,
        GS_EXPORT: GS_EXPORT_BUCKET_MAP,
        GS_LEASEDINVENTORY: GS_LEASEDINVENTORY_BUCKET_MAP,
    })

APP_ID_BUCKET_SUFFIXES = {
    APP_IDENTITY_DEV: 'dev',
    APP_IDENTITY_TEST: 'test',
    APP_IDENTITY_DEMO: 'demo',
    APP_IDENTITY_PROD: 'prod',
    APP_IDENTITY_STAGING: 'staging',
    APP_IDENTITY_PRODBACKUP: 'prodbackup',
    APP_IDENTITY_ACT: 'act',
    APP_IDENTITY_ACT2: 'act2',
    APP_IDENTITY_ANT: 'ant',
    APP_IDENTITY_ANTBOM: 'antbom',
    APP_IDENTITY_TESTBED: 'testbed-test',
    # For file attachments on local devappserver.
    APP_IDENTITY_DEVAPPSERVER: 'auto',
}

ATTACHMENTS_BUCKET_PREFIX = '/doublehelix-attachments-'

#
# Foreign Key related settings.
#
# Value propagated when parent entity doesn't exist.
FK_ERROR_VALUE = '[none]'
# Value propagated when parent entity property doesn't exist.
FK_MISSING_VALUE = None  # Value
# Limit for how many times we'll retry transactions.
FK_TRANSACTION_RETRIES = 5
# The number of transactions to run in parallel.
FK_TRANSACTION_SIZE = 10
# Fetch limit for entity queries.
FK_BATCH_SIZE = FK_TRANSACTION_SIZE * 10
# How many times to recurse when updating self-loops.
FK_MAX_RECURSION = 10
# Memcache key for foreign key references.
FK_MEMCACHE_KEY = 'ForeignKeyReferences'
# How long to cache foreign key references.
FK_MEMCACHE_TIMEOUT = 60 * 30  # 30 minutes.

# Fetch limit for materialized view mapper queries.
MV_BATCH_SIZE = 1000

# ASCII characters in the range 33 to 126 inclusive.
VISIBLE_PRINTABLE_ASCII = frozenset(
    set(string.printable) - set(string.whitespace))

# Boolean string alternatives.
TRUE_VALUES = {'true', 'yes', 'y', '1'}
FALSE_VALUES = {'false', 'no', 'n', '0'}

# TableView related settings.
TABLEVIEW_VALID_ALIASES = {'$key_kind', '$key_name'}

# Base model constants.
CREATED_BY = 'created_by'
CREATED_ON = 'created_on'
FK_DISPLAY = 'fk_display'
NAME = 'name'
NORMALIZED_NAME = 'normalized_name'
UPDATED_BY = 'updated_by'
UPDATED_ON = 'updated_on'

# The model or the kind of an entity.
MODEL = 'model'

# The row number of a rack.
RACK_ROW_NUMBER = 'row_number'

# The position of a rack in the rack row.
RACK_POSITION = 'position'

# Rack max position.
RACK_MAX_POSITION = 1000

COPY_DEVICES = 'copy_devices'

# The cable key name in a strand.
CABLE_KEY_NAME = 'Cable__key_name'

# The net deploy part number of part.
NDPN = 'ndpn'

# The identifier of an entity.
KEY_NAME = 'key_name'

# The version number of an entity.
KEY_VERSION = 'key_version'

# The version number of an entity.
KEY_SUBTYPE = 'key_subtype'

# The default ordering number of an entity.
KEY_ORDER = 'key_order'

# The kind name of an entity.
KEY_KIND = 'key_kind'

# FK suffix.
FK_KEY_NAME = KEY_NAME
FK_SEP = '__'

# START foreign key name and entity name constants for DH entities.
BUILDING_KEY_NAME = 'Building__key_name'
BUILDING_NAME = 'Building__name'
DEVICES_KEY_NAME = 'Devices__Key_name'
FLOOR_KEY_NAME = 'Floor__key_name'
FLOOR_NAME = 'Floor__name'
LOGICALDEVICE_KEY_NAME = 'LogicalDevice__key_name'
LSOPTICS_KEY_NAME = 'LSOptics__key_name'
MANUFACTURER_KEY_NAME = 'Manufacturer__key_name'
METRO_KEY_NAME = 'Metro__key_name'
NETWORKELEMENT_KEY_NAME = 'NetworkElement__key_name'
PART_KEY_NAME = 'Part__key_name'
POP_KEY_NAME = 'Pop__key_name'
POP_NAME = 'Pop__name'
RACK_KEY_NAME = 'Rack__key_name'
RACK_ROW_KEY_NAME = 'RackRow__key_name'
SPACE_KEY_NAME = 'Space__key_name'
SPACE_NAME = 'Space__name'
VENDOR_KEY_NAME = 'Vendor__key_name'
# END foreign key name and entity name constants for DH entities.

# Represents the uuid of the direct parent of card/slot/port.
PARENT_UUID = 'parent_uuid'

# Represents the root parent of card/slot/port in device hierarchy.
TOP_DEVICE_UUID = 'top_device_uuid'
PORTS = 'ports'
SLOTS = 'slots'
CARDS = 'cards'
CONNECTORS = 'connectors'
SUB_NODE_TYPES = (PORTS, SLOTS, CARDS, CONNECTORS)

# Model names.
MODEL_ACT_PATH_TX = 'ActPathTx'
MODEL_BOM = 'BOM'
MODEL_BOM_ITEM = 'BOMItem'
MODEL_BUILDING = 'Building'
MODEL_BUILDINGCONTENTS = 'BuildingContents'
MODEL_BULK_FIBER_PANEL_CONNECTIONS_VIEW = 'BulkFiberPanelConnectionsView'
MODEL_BTP_KIND = 'BtpKind'
MODEL_BTP_SUMMARY = 'BtpSummary'
MODEL_CABLE = 'Cable'
MODEL_CAPACITY_FUNCTION = 'CapacityFunction'
MODEL_CAPACITY_REFERENCE = 'CapacityReference'
MODEL_CARD = 'Card'
MODEL_CIRCUIT = 'Circuit'
MODEL_CIRCUIT_ELEMENT = 'CircuitElement'
MODEL_CONDUIT_CAPACITY = 'ConduitCapacity'
MODEL_CIRCUIT_PATH = 'CircuitPath'
MODEL_CONNECTION_POINT = 'ConnectionPoint'
MODEL_CRON_ENTRY = 'CronEntry'
MODEL_TRAFFIC_TIRESIAS_INPUT = 'TrafficTiresiasInput'
MODEL_DEVICE = 'Device'
MODEL_DEVICE_CONNECTIVITY_VIEW = 'DeviceConnectivityView'
MODEL_EDGESPLICE = 'Splice'
MODEL_FALLOUT = 'Fallout'
MODEL_FILE_ATTACHMENT = 'FileAttachment'
MODEL_FLOOR = 'Floor'
MODEL_FLOORPLAN_CONTENTS = 'FloorplanContents'
MODEL_HARDWARE_PARTS_MAPPING = 'HardwarePartsMapping'
MODEL_INFRA_CAP = 'InfraCap'
MODEL_INFRA_CAP_RULES = 'InfraCapRules'
MODEL_INTERMETRO = 'InterMetro'
MODEL_INVENTORY_LOCATION = 'InventoryLocation'
MODEL_LEASED_WAVE_ROUTE = 'LeasedWaveRoute'
MODEL_LEASED_WAVE_TO_ROUTE = 'LeasedWaveToRoute'
MODEL_LIGHT_PATH = 'LightPath'
MODEL_LOCALITY = 'Locality'
MODEL_LOCATION = 'Location'
MODEL_LOG = 'Log'
MODEL_LOGICAL_DEVICES = 'LogicalDevice'
MODEL_LOGICAL_LOCATION = 'LogicalLocation'
MODEL_LSOPTICS = 'LSOptics'
MODEL_MANUFACTURER = 'Manufacturer'
MODEL_METRO = 'Metro'
MODEL_METROCONTENTS = 'MetroContents'
MODEL_MOGLOG_RACK = 'MoglogRack'
MODEL_NAMESEQUENCE = 'NameSequence'
MODEL_NETWORKELEMENT = 'NetworkElement'
MODEL_NETWORK_CONNECTION = 'NetworkConnection'
MODEL_OMS = 'OMS'
MODEL_ON_NETWORK_INVENTORY_MAPPING = 'OnNetworkInventoryMapping'
MODEL_ORDER = 'Order'
MODEL_ORDER_ITEM = 'OrderItem'
MODEL_OSPCABLE_SEGMENT = 'OspCableSegment'
MODEL_OSPCONTAINER = 'OspContainer'
MODEL_OSP_LIGHT_PATH_FIBERS = 'OspLightPathFibers'
MODEL_OVERHEAD_CABLE = 'OverheadCable'
MODEL_PANEL_XCON = 'PanelXcon'
MODEL_PART = 'Part'
MODEL_PATH_ELEMENT = 'PathElement'
MODEL_PHYSICAL_SPOF = 'PhysicalSPOF'
MODEL_POP = 'Pop'
MODEL_POPCONTENTS = 'PopContents'
MODEL_PORT = 'Port'
MODEL_CONNECTOR = 'Connector'
MODEL_CONNECTOR_TYPE = 'ConnectorType'
MODEL_PERMISSION = 'Permission'
MODEL_PORT_INTERFACE_TYPE = 'PortInterfaceType'
MODEL_PORT_RESERVATION = 'PortReservation'
MODEL_PORT_STATUS_SUMMARY = 'PortStatusSummary'
MODEL_RACK = 'Rack'
MODEL_RACK_SPACE_POWER = 'RackSpacePower'
MODEL_RACKROW = 'RackRow'
MODEL_RACK_ROLE_TYPE = 'RackRoleType'
MODEL_RACK_ROLE_SUB_TYPE = 'RackRoleSubType'
MODEL_ROLE_PAIR = 'RolePair'
MODEL_SETTING = 'Setting'
MODEL_SLOT = 'Slot'
MODEL_SOCKET = 'Socket'
MODEL_SPACE = 'Space'
MODEL_SPACE_CONTENT = 'SpaceContent'
MODEL_SPECTRUM_DESIGN = 'SpectrumDesign'
MODEL_SPECTRUM_UTILIZATION = 'SpectrumUtilization'
MODEL_STRAND = 'Strand'
MODEL_SPLICE = 'Splice'
MODEL_ALL = 'ALL'
MODEL_SUBBUILDING = 'SubBuilding'
MODEL_SUB_CIRCUIT = 'SubCircuit'
MODEL_SUBMARINE_OMS_OTS = 'SubmarineOMSToOTS'
MODEL_SUBTOPOLOGY = 'SubTopology'
MODEL_THIRDPARTY_TRANSPORT = 'ThirdPartyTransport'
MODEL_TRAFFIC_WEEK_REPORT = 'TrafficWeekReport'
MODEL_TRANSPORT_PORTMAP = 'TransportPortmap'
MODEL_VENDOR = 'Vendor'
MODEL_VIRTUAL_INTERFACE = 'VirtualInterface'
MODEL_VIRTUAL_INTERFACE_PORTS = 'VirtualInterfacePorts'
# Meta models used in device logic.
MODEL_EXISTING = 'Existing'
MODEL_TEMPLATE = 'Template'

# Model names used only by UNM export and ACT Pipeline.
MODEL_UNM_CHASSIS = 'Chassis'
MODEL_UNM_DEVICE_CONNECTIVITY = 'DeviceConnectivity'
MODEL_UNM_PATCH_PANEL = 'PatchPanel'
MODEL_UNM_PARENT_RACK = 'ParentRack'
MODEL_UNM_SERVICE_PROVIDER_DEPRECATED = 'ServiceProvider'

UNKNOWN_NUMBER = 999

# The regular expresssion for the Google Netops Rack.
REGEX_NETOPS_RACK = r'[A-Z]{3}\d{2}-\d{1,2}-\d{1,2}'

# The constant to represent a Google Netops Rack.
GOOGLE_NETOPS_RACK = 'Google Netops Rack'

# The constant to represent a Vendor Rack.
VENDOR_RACK = 'Vendor Rack'

# The constant to represent a Number only Rack.
DC_RACK = 'DC Rack'

OTHER_RACK = 'Other Rack'

# The constant to represent a prefix for Vendor Rack.
VRR_PREFIX = 'VRR-'

# Default number of pins to assume for MPO port tracing.
DEFAULT_MPO_PIN_COUNT = 12

# The setting entity key name for height_ru tolerance.
HEIGHT_RU_TOLERANCE = 'HEIGHT_RU_TOLERANCE'

# The setting entity for import status list view.
IMPORT_STATUS_LIST_PERM = 'GROUPS_ALLOWED_ANY_IMPORT_STATUS'

# The setting entity for allowing validation override for csv import.
ALLOWED_IMPORT_OVERRIDE = 'GROUPS_ALLOWED_IMPORT_OVERRIDE'

# The setting entity for allowing creating new tables via csv import.
CSV_CREATE_GROUPS = 'CSV_CREATE_GROUPS'

# START NetcrackerSync constants.
# The NetCracker object id of the entity.
OBJECT_ID = 'OBJECT_ID'

# The allowed NetCracker update operations.
ACCEPTED_NC_ACTIONS = ('insert', 'update', 'delete')

# Settings.
# The setting entity key name for Grenade dev stubby server.
GRENADE_DEV_HOST_URL = 'GRENADE_DEV_STUBBY_URL'

# The setting entity key name for Grenade staging stubby server.
GRENADE_STAGING_HOST_URL = 'GRENADE_STAGING_STUBBY_URL'

# The setting entity key name for Grenade test stubby server.
GRENADE_TEST_HOST_URL = 'GRENADE_TEST_STUBBY_URL'

# The setting entity key name for Grenade prod stubby server.
GRENADE_PROD_HOST_URL = 'GRENADE_PROD_STUBBY_URL'

# The setting entity key name for Grenade prodbackup stubby server.
GRENADE_PRODBACKUP_HOST_URL = 'GRENADE_PRODBACKUP_STUBBY_URL'

# The setting entity key name for Grenade act stubby server.
GRENADE_ACT_HOST_URL = 'GRENADE_ACT_STUBBY_URL'

# The default Grenade stubby url.
DEFAULT_GRENADE_HOST_URL = ('blade:netops-bazooka-grenade-dev')

# Netcracker sync operations.
NET_CRACKER_DELETE = 'Delete'
NET_CRACKER_INSERT = 'Insert'
NET_CRACKER_UPDATE = 'Update'

# Netcracker Sync queue stats 'Setting' constants.
NCSYNC_QUEUE_THRESHOLD = 'NCSYNC_QUEUE_THRESHOLD'
NCSYNC_QUEUE_DEFAULT_THRESHOLD = 1000

NCSYNC_QUEUE_NOTIFICATION_TO = 'NCSYNC_QUEUE_NOTIFICATION_TO'
NCSYNC_QUEUE_NOTIFICATION_DEFAULT_TO = 'dhops@google.com'
# END NetcrackerSync constants.

# START Bazooka constants.
# Settings for Import related flag names.
# Flag to enable the revision history on the Bazooka imported models.
BZ_REVISIONS = 'BZ_REVISIONS'

# Flag to switch on/off Moglog only entities on Bazooka import.
BZ_MOGLOG_ENTITIES = 'BZ_MOGLOG_ENTITIES'

# Flag to switch on/off to import only the device contents.
BZ_IMPORT_ONLY_CONTENTS = 'BZ_IMPORT_ONLY_DEVICE_CONTENTS'

# Flag to switch on/off Moglog only entities on Bazooka import.
BZ_DISABLE_MOGLOG_ENTITIES = 'BZ_DISABLE_MOGLOG_ENTITIES'

# Bazooka DB's
BAZOOKA_DEV = '/cloudsql/google.com:nc-bazooka:bazooka-dev'
BAZOOKA_PROD_AUTO = '/cloudsql/google.com:nc-bazooka:bazooka-prod-auto'
BAZOOKA_PROD_AUTO_PRODBACKUP_REPLICA = (
    '/cloudsql/google.com:nc-bazooka:bazooka-prod-auto-prodbackup-replica'
)
BAZOOKA_PROD_AUTO_STAGING_REPLICA = (
    '/cloudsql/google.com:nc-bazooka:bazooka-prod-auto-staging-replica'
)

# Bazooka Speckle instances map.
SPECKLE_DB = 'bazooka'

# bazookasync user.
BZ_SYNC = 'bazookasync'
BZ_SYNC_DELTA_HOURS = 'BZ_SYNC_DELTA_HOURS'
BZ_SYNC_DELTA_MINUTES = 'BZ_SYNC_DELTA_MINUTES'

# Bazooka tables.
BZ_CONDUIT_CAPACITY = 'BZ_CONDUIT_CAPACITY'
BZ_CONNECTOR = 'BZ_CONNECTOR'
BZ_DEVICE = 'BZ_DEVICE'
BZ_EDGE_SPLICE = 'BZ_EDGE_SPLICE'
BZ_ISP_WIRE = 'BZ_ISP_WIRE'
BZ_LEASED_WAVE_TO_ROUTE = 'BZ_LEASED_WAVE_TO_ROUTE'
BZ_OSP_CABLE = 'BZ_OSP_CABLE'
BZ_OSP_FIBER = 'BZ_OSP_FIBER'
BZ_PANEL_XCON = 'BZ_PANEL_XCON'
BZ_PORT = 'BZ_PORT'
BZ_SPLICE = 'BZ_SPLICE'
BZ_VIRTUAL_INTERFACE_PORTS = 'BZ_VIRTUAL_INTERFACE_PORTS'

# Bazooka columns.
BZ_NAME = 'NAME'
BZ_GUNS = 'GUNS'
BZ_KEY_NAME = 'KEY_NAME'
BZ_CREATED_BY = 'CREATED_BY'

# END Bazooka constants.

# Common constants.
COLON_DELIMITER = ':'

# Common controllers.
DEP_ERRORS = 'dependency'
CALL_ERRORS = 'call_errors'
ID = 'id'

# Unknown value constant, for setting values that aren't known instead of using
# None.  Displaying an unknown value is more user-friendly.
UNKNOWN_VALUE = 'UNKNOWN'

# History constants.
DEFAULT_HISTORY_LIMIT = 500

# Google Analytics Property ID constants.
GA_PROPERTY_ID_DEFAULT = 'UA-47042903-3'

# These are the status state values used for display purposes. For status
# involving equality checks, used the constants below.
ASBUILT_DISPLAY_STATUS = 'AsBuilt'
INSERVICE_DISPLAY_STATUS = 'InService'
PLANNED_DISPLAY_STATUS = 'Planned'
DECOM_DISPLAY_STATUS = 'Decommissioned'
FORKLIFT_DISPLAY_STATUS = 'Forklift'

# These are the global physical status value list used for status calculations.
PLANNED_STATUS = ('planned', 'btp')
ASBUILT_STATUS = ('asbuilt',)
DECOMMISSIONED_STATUS = ('decommissioned',)

# Physical status field constants.
PHYSICAL_STATUS = 'physical_status'
PHYSICAL_USAGE_STATUS = 'physical_usage_status'  # Representation in Port.
PHYSICAL_STATUS_ASBUILT = 'asbuilt'
PHYSICAL_STATUS_DECOMMISSIONED = 'decommissioned'
PHYSICAL_STATUS_PLANNED = 'planned'

# Logical status.
LOGICAL_STATUS = 'logical_status'
LOGICAL_USAGE_STATUS = 'logical_usage_status'  # Representation in Port.
LOGICAL_STATUS_ASBUILT = 'AsBuilt'
LOGICAL_STATUS_DECOMMISSIONED = 'Decommissioned'


MANAGEMENT_STATUS = 'management_status'
BROKEN_STATUS = 'broken'

# Bazooka report sender email address.
EMAIL_REPORT_SENDER_MAP = collections.defaultdict(
    lambda: None,  # Default factory.
    **{
        APP_IDENTITY_DEV: 'reports@netdesign-dev.appspotmail.com',
        APP_IDENTITY_DEMO: 'reports@netdesign-demo.appspotmail.com',
        APP_IDENTITY_PROD: 'reports@netdesign-prod.appspotmail.com',
        APP_IDENTITY_TEST: 'reports@netdesign-test.appspotmail.com',
        APP_IDENTITY_STAGING: 'reports@netdesign-staging.appspotmail.com',
        APP_IDENTITY_PRODBACKUP: 'reports@netdesign-prodbackup.appspotmail.com',
        APP_IDENTITY_ACT: 'reports@netdesign-act.appspotmail.com',
        APP_IDENTITY_ANTBOM: 'reports@netdesign-antbom.appspotmail.com',
        APP_IDENTITY_ACT2: 'reports@netdesign-act2.appspotmail.com',
    })

# Email template sender email address.
EMAIL_TEMPLATE_SENDER_MAP = collections.defaultdict(
    lambda: 'doublehelix-noreply+unknown@google.com',  # Default factory.
    **{
        APP_IDENTITY_DEMO: 'doublehelix-noreply+demo@google.com',
        APP_IDENTITY_DEV: 'doublehelix-noreply+dev@google.com',
        APP_IDENTITY_PROD: 'doublehelix-noreply+prod@google.com',
        APP_IDENTITY_TEST: 'doublehelix-noreply+test@google.com',
        APP_IDENTITY_STAGING: 'doublehelix-noreply+staging@google.com',
        APP_IDENTITY_PRODBACKUP: 'doublehelix-noreply+prodbackup@google.com',
        APP_IDENTITY_ACT: 'doublehelix-noreply+act@google.com',
        APP_IDENTITY_ACT2: 'doublehelix-noreply+act2@google.com',
        APP_IDENTITY_ANT: 'doublehelix-noreply+ant@google.com',
        APP_IDENTITY_ANTBOM: 'doublehelix-noreply+antbom@google.com',
    })

# Flag for DH training entities.
TRAINING_DATA_FLAG = 'training'

# Size constants.
MM_TO_IN_CONSTANT = 0.0393701
CM_TO_IN_CONSTANT = 0.393701
IN_TO_MM_CONSTANT = 25.4
IN_TO_CM_CONSTANT = 2.54
HEIGHT_RU_CONSTANT = 1.75
# Used to convert floating point ru values to whole number.
RU_FACTOR = 100

# Default list method limit.
LIST_DEFAULT_LIMIT = 250

# Maximum number of results to display in list methods.
LIST_MAX_LIMIT = 5000

# Maximum ndb.StringProperty size.
MAX_NDB_STRING_BYTES = 1500

# Borg service location constants.
CMDATA_ACT = '/abns/netdesign/cmdata_act.server'
CMDATA_ACT2 = '/abns/netdesign/cmdata_act2.server'
CMDATA_DEV = '/abns/netdesign/cmdata_dev.server'
CMDATA_DEMO = '/abns/netdesign/cmdata_demo.server'
CMDATA_PROD = '/abns/netdesign/cmdata.server'
CMDATA_PRODBACKUP = '/abns/netdesign/cmdata_prodbackup.server'
CMDATA_STAGING = '/abns/netdesign/cmdata_staging.server'
CMDATA_ANTBOM = '/abns/netdesign/cmdata_antbom.server'

HARDWARE_PROD = '/abns/netdesign/hardware.server'
HARDWARE_DEMO = '/abns/netdesign/hardware_demo.server'
HARDWARE_DEV = '/abns/netdesign/hardware_dev.server'
HARDWARE_STAGING = '/abns/netdesign/hardware_staging.server'
HARDWARE_PRODBACKUP = '/abns/netdesign/hardware_prodbackup.server'
HARDWARE_ACT = '/abns/netdesign/hardware_act.server'
HARDWARE_ACT2 = '/abns/netdesign/hardware_act2.server'
HARDWARE_ANTBOM = '/abns/netdesign/hardware_antbom.server'

ROBO_PROD = '/abns/netdesign/robo_api.server'
ROBO_DEV = '/abns/netdesign/robo_api_dev.server'
ROBO_STAGING = '/abns/netdesign/robo_api_staging.server'
ROBO_PRODBACKUP = '/abns/netdesign/robo_api_prodbackup.server'

# pylint: disable=line-too-long
PORTS_RESERVE_DEV = '/bns/pa/borg/pa/bns/netdesign/doublehelix_dev_service/0'
PORTS_RESERVE_TEST = '/bns/pa/borg/pa/bns/netdesign/doublehelix_test_service/0'
PORTS_RESERVE_STAGING = 'blade:doublehelix_staging_service'
PORTS_RESERVE_PRODBACKUP = 'blade:doublehelix_prodbackup_service'
PORTS_RESERVE_ACT = 'blade:doublehelix_act_service'
PORTS_RESERVE_ACT2 = 'blade:doublehelix_act2_service'
PORTS_RESERVE_PROD = 'blade:doublehelix_prod_service'
PORTS_RESERVE_ANTBOM = 'blade:doublehelix_antbom_service'
# pylint: enable=line-too-long


# START NEST sync constants.
NEST_PROD = 'blade:netsoft-nest-server'
NEST_SERVICE_LOCATION = NEST_PROD
NEST_SYNC_USER = 'nestsync'
# END NEST sync constants.


# TODO(kyatham): Figure out a better way to handle these scenarios.
CMDATA_SERVICE_LOCATION_MAP = collections.defaultdict(
    lambda: CMDATA_DEMO,  # Default factory.
    **{APP_IDENTITY_PROD: CMDATA_PROD,
       APP_IDENTITY_DEMO: CMDATA_DEMO,
       APP_IDENTITY_DEV: CMDATA_DEV,
       APP_IDENTITY_STAGING: CMDATA_STAGING,
       APP_IDENTITY_ACT: CMDATA_ACT,
       APP_IDENTITY_ACT2: CMDATA_ACT2,
       APP_IDENTITY_ANTBOM: CMDATA_ANTBOM,
       APP_IDENTITY_PRODBACKUP: CMDATA_PRODBACKUP})

HARDWARE_SERVICE_LOCATION_MAP = collections.defaultdict(
    lambda: HARDWARE_DEMO,  # Default factory.
    **{APP_IDENTITY_PROD: HARDWARE_PROD,
       APP_IDENTITY_DEMO: HARDWARE_DEMO,
       APP_IDENTITY_DEV: HARDWARE_DEV,
       APP_IDENTITY_STAGING: HARDWARE_STAGING,
       APP_IDENTITY_ACT: HARDWARE_ACT,
       APP_IDENTITY_ACT2: HARDWARE_ACT2,
       APP_IDENTITY_ANTBOM: HARDWARE_ANTBOM,
       APP_IDENTITY_PRODBACKUP: HARDWARE_PRODBACKUP})

PORTS_RESERVATION_SERVICE_BLADE = collections.defaultdict(
    lambda: PORTS_RESERVE_TEST,  # Default factory.
    **{
        APP_IDENTITY_DEV: PORTS_RESERVE_DEV,
        APP_IDENTITY_TEST: PORTS_RESERVE_TEST,
        APP_IDENTITY_STAGING: PORTS_RESERVE_STAGING,
        APP_IDENTITY_ACT: PORTS_RESERVE_ACT,
        APP_IDENTITY_ACT2: PORTS_RESERVE_ACT2,
        APP_IDENTITY_ANTBOM: PORTS_RESERVE_ANTBOM,
        APP_IDENTITY_PRODBACKUP: PORTS_RESERVE_PRODBACKUP,
        APP_IDENTITY_PROD: PORTS_RESERVE_PROD
    })

ROBO_SERVICE_LOCATION_MAP = collections.defaultdict(
    lambda: ROBO_DEV,  # Default factory.
    **{APP_IDENTITY_PROD: ROBO_PROD,
       APP_IDENTITY_DEV: ROBO_DEV,
       APP_IDENTITY_STAGING: ROBO_STAGING,
       APP_IDENTITY_PRODBACKUP: ROBO_PRODBACKUP})

# Shared error messages.
FILTER_AND_Q_ERROR = 'Request cannot contain both q and filter param.'

# Double Helix rews bucket in Big Store.
REWS_BUCKET_MAP = collections.defaultdict(
    lambda: 'doublehelix-rews-test',  # Default factory.
    **{
        APP_IDENTITY_PROD: 'doublehelix-rews-prod',
        APP_IDENTITY_DEV: 'doublehelix-rews-dev',
        APP_IDENTITY_DEMO: 'doublehelix-rews-demo',
        APP_IDENTITY_TEST: 'doublehelix-rews-test',
        APP_IDENTITY_STAGING: 'doublehelix-rews-staging',
        APP_IDENTITY_PRODBACKUP: 'doublehelix-rews-prodbackup',
        APP_IDENTITY_ACT: 'doublehelix-rews-act',
        APP_IDENTITY_ACT2: 'doublehelix-rews-act2',
        APP_IDENTITY_ANT: 'doublehelix-rews-ant',
        APP_IDENTITY_ANTBOM: 'doublehelix-rews-antbom',
    })

# Toposphere blades.
TOPOSPHERE_BLADE_MAP = collections.defaultdict(
    lambda: 'blade:toposphere-sandbox-client',  # Default factory.
    **{
        APP_IDENTITY_PROD: 'blade:toposphere',
    })

TOPO_BLDG_FILENAME = 'toposphere_buildings.json'
TOPO_SUBBLDG_FILENAME = 'toposphere_sub_buildings.json'
# Toposphere building topology model name.
TOPOSPHERE_BUILDING_MODEL = '/unm/toposphere/corp/buildings'
# Toposphere subbuilding topology model name.
TOPOSPHERE_SUBBUILDING_MODEL = '/unm/toposphere/sos_export'

# How long to cache toposphere responses.
TOPO_MEMCACHE_TIMEOUT = 60 * 60  # 30 minutes.

# SpaceContents keys switch.
MODEL_SPACECONTENTS = 'SpaceContents'
MODEL_RACK_ROW = 'RackRow'
INSERT_ACTION = 'INSERT'
DELETE_ACTION = 'DELETE'
TRUE = 'true'

# The setting key to enable/disable UNM export. Value TRUE/FALSE.
UNM_EXPORT_ENABLED = 'UNM_EXPORT_ENABLED'

# If true, verbose error logging. Can generate *lots* of messages. If False or
# omitted, no verbose logging.
UNM_EXPORT_VERBOSE_LOGGING = 'UNM_EXPORT_VERBOSE_LOGGING'

# If true, enable and report full export memory usage. If False or omitted,
# disabled.
UNM_EXPORT_ENABLE_FULL_EXPORT_MEMORY_MEASUREMENT = (
    'UNM_EXPORT_ENABLE_FULL_EXPORT_MEMORY_MEASUREMENT')

# The setting entity key name for the UNM export proxy server.
# Each instance (prod, staging, demo, ...) can have a distinct value.
UNM_EXPORT_PROXY_URL = 'UNM_EXPORT_PROXY_URL'

# Set this to an int > 0 to override the default shard count for sharded full
# export entities.
UNM_EXPORT_SHARD_COUNT = 'UNM_EXPORT_SHARD_COUNT'

# UNM export logging severity codes.
UNM_LOG_INFO = 'INFO'
UNM_LOG_WARNING = 'WARNING'
UNM_LOG_ERROR = 'ERROR'

# UNM export operation codes
UNM_EXPORT_UPDATE = 'UPDATE'
UNM_EXPORT_RENAME = 'RENAME'
UNM_EXPORT_DELETE = 'DELETE'
UNM_EXPORT_CLEAN_RELATIONSHIPS = 'CLEANREL'

# UNM 'operation' fields for streamz
UNM_OP_PIPELINE = 'Pipeline'  # Success/failure for an entire pipeline.
# kind field is type of pipeline, and for
# full export root how it was initiated.
# Remaining operations give success/warning/error by entity kind when doing
# a specific operation. The 'kind' field is the entity kind.
UNM_OP_CHANGE_UPDATE = 'ChangeUpdate'  # Updates of the given entity kind
UNM_OP_CHANGE_DELETE = 'ChangeDelete'  # Deletes of the given entity kind
UNM_OP_CHANGE_RENAME = 'ChangeRename'  # Renames of the given entity kind
UNM_OP_CHANGE_CLEAN_RELATIONSHIPS = 'ChangeClean'  # Clean_relationships of the
# given entity kind
UNM_OP_FULL_EXPORT = 'FullExport'   # Full exports of the given entity kind

# UNM pipeline types. These are the 'kind' streamz field for
# operation=UNM_OP_PIPELINE.
# Full export root pipeline. Also gives who initiated the full export:
UNM_EXPORT_MANUAL = 'FullExportManual'  # From DH admin console
UNM_EXPORT_AUTOMATIC = 'FullExportAuto'  # From proxy server request
UNM_EXPORT_BIG_UPDATE = 'FullExportBigUpdate'  # From too-big update
# Full export child pipelines:
UNM_PIPE_METROS_POPS = 'Metros/Pops'
UNM_PIPE_LOGICAL_DEVICES = 'LogicalDevices'
UNM_PIPE_ALL_SPACES = 'Buildings/SubBuildings/Floors/Spaces'
UNM_PIPE_RACKS = 'Racks'
UNM_PIPE_CHASSIS = 'Chassis'
UNM_PIPE_PATCH_PANELS = 'PatchPanels/Ports'
UNM_PIPE_PATCH_PANELS_SHARD = 'PatchPanels/Ports_Shard'
UNM_PIPE_CIRCUITS = 'Circuits'
UNM_PIPE_DEVICE_CONNECTIVITY = 'DeviceConnectivity'
# Update pipeline:
UNM_PIPE_UPDATE = 'Update'

# For operations UNM_OP_CHANGE_UPDATE, UNM_OP_CHANGE_DELETE,
# UNM_OP_CHANGE_RENAME, UNM_OP_CHANGE_CLEAN_RELATIONSHIPS, and
# UNM_OP_FULL_EXPORT, the 'kind' field is the entity type, currently one of:
#  MODEL_METRO, MODEL_POP, MODEL_LOGICAL_DEVICES, MODEL_VENDOR, MODEL_BUILDING,
#   MODEL_SUBBUILDING, MODEL_FLOOR, MODEL_SPACE, MODEL_RACK, MODEL_UNM_CHASSIS,
#   MODEL_UNM_PATCH_PANEL, MODEL_PORT, MODEL_PORT_RESERVATION, MODEL_CIRCUIT,
#   MODEL_ACT_PATH_TX, MODEL_UNM_DEVICE_CONNECTIVITY

# The 'status' streamz field is one of
UNM_STATUS_SUCCESS = 'Success'    # Successful pipeline or entity.
UNM_STATUS_FAILURE = 'Failure'    # Only for operation UNM_OP_PIPELINE
# Remaining two are for operations other than UNM_OP_PIPELINE:
UNM_STATUS_WARNING = 'Warnings'
UNM_STATUS_ERROR = 'Errors'
# NOTE THAT SUCCESS, WARNING, AND ERROR ARE MUTUALLY DISTINCT. Each exported
# entity will fall in one and only one status. Entities exported with status
# UNM_STATUS_WARNING are exported; those with UNM_STATUS_ERROR are not.

# Examples:
# (operation, kind, status) =
#     (UNM_OP_PIPELINE, UNM_EXPORT_MANUAL, UNM_STATUS_SUCCESS)
# gives the count of successful runs of the full export root pipeline when
# manually initiated.
#
# (operation, kind, status) =
#     (UNM_OP_PIPELINE, UNM_PIPE_PATCH_PANELS_SHARD, UNM_STATUS_FAILURE)
# gives the count of failed runs of shard pipelines for PatchPanels/Ports.
#
# (operation, kind, status) =
#     (UNM_OP_PIPELINE, UNM_PIPE_UPDATE, UNM_STATUS_SUCCESS)
# gives the count of successful runs of the Update pipeline.
#
# (operation, kind, status) =
#     (UNM_OP_CHANGE_UPDATE, MODEL_POP, UNM_STATUS_ERROR)
# gives the count of Pops which encountered errors during an update operation to
# insert or change a Pop.
#
# (operation, kind, status) =
#     (UNM_OP_CHANGE_RENAME, MODEL_UNM_CHASSIS, UNM_STATUS_SUCCESS)
# gives the count of UNM Chassis (DH devices which aren't patch panels) which
# were succcessfully renamed.
#
# (operation, kind, status) =
#     (UNM_OP_FULL_EXPORT, MODEL_UNM_PATCH_PANEL, UNM_STATUS_WARNING)
# gives the count of exported PatchPanels and their ports with warnings during a
# full export.

# Appengine User constants.
USER_CONTEXT_FIELDS = [
    'AUTH_DOMAIN', 'USER_EMAIL', 'USER_ID', 'FEDERATED_IDENTITY',
    'FEDERATED_PROVIDER'
]

# Authz constants.
AUTH_METHOD_HEADER = 'HTTP_X_DH_OVERRIDE_AUTH_METHOD'
AUTH_METHOD_COOKIE = 'cookie'
AUTH_METHOD_COOKIE_FIRST = 'cookie-first'
AUTH_METHOD_REST = 'rest'

# Email Template for ribbon publish.
RIBBON_PUBLISH_EMAIL_TEMPLATE = {
    'name': 'publish_ribbon',
    'description': 'Email template for ribbon publish.',
    'to': [],
    'cc': [],
    'subject': 'Ribbon published by {{user}}',
    'body': '<html><body>'
            'The ribbon has been modified and published by {{user}}.'
            '</body></html>',
}

SEND_DEV_NOTIFICATIONS = 'SEND_DEV_NOTIFICATIONS'
DH_DEV_NOTIFY_ADDRESS = 'DH_DEV_NOTIFY_ADDRESS'

# Pluggable devices key to look for in application settings.
PLUGGABLE_DEVICES = 'PLUGGABLE_DEVICES'

# Regex for Metro name.
METRO_NAME_RE_STRING = r'(\d{4}-\d{2}-\d{2})?[A-Z]{3}'
METRO_NAME_RE = re.compile(r'^%s$' % METRO_NAME_RE_STRING)

# Regex for Pop name.
POP_NAME_RE_STRING = METRO_NAME_RE_STRING + r'(?:0[1-9]|[1-9][0-9]|[1-9]\d{2})'
POP_NAME_RE = re.compile(r'^%s$' % POP_NAME_RE_STRING)

# Regex for Vendor name.
VENDOR_CODE_RE = re.compile(r'^[A-Z0-9]{5}$')

# Regex for name of patch panels.
# The regexes produce these capturing groups:
# 1) The name of the panel.
# 2) The sequence number of the panel.
# Optionally
# 3) For corp panels the rews-id of the building.

# Corp Panel naming rules are relaxed to allow a '-' or a '.' delimiter.
# This allows existing malformed panel names using a '.' delimiter to be
# considered when naming new panels so that sequence numbers are not re-used.
# Corp panel name example: pp34-us-svl-mp5
# Corp panel with malformed name: pp16-svl-mp5 (note no us-); i.e. the
# panel creation predates the rename of the building rews-id to add the us-
# prefix.
# Corp panel with '.' in the name: pp16.us-svl-mp5 (note '.').
# Collecting groups: name, sequence, rews-id.
CORP_PANEL_NAME_RE = re.compile(
    r'^((?:PP|pp)([0-9]{1,3})(?:-|\.)((?:\w{2}-)*\w{3}-[\w-]+))')

# Hwops non ngf name examples: spp40, pp41.
# Groups: name, sequence.
HWOPS_NON_NGF_PANEL_NAME_RE = re.compile(r'([csg]?pp(\d+))')

# Disable netcracker sync.
NC_SYNC = 'NC_SYNC'
FALSE = 'false'

# Release email notification address.
RELEASE_NOTIFY_TO_ADDRESS = 'RELEASE_NOTIFY_TO_ADDRESS'
RELEASE_NOTIFY_REPLY_ADDRESS = 'RELEASE_NOTIFY_REPLY_ADDRESS'
DEFAULT_RELEASE_NOTIFY_TO_ADDRESS = 'double-helix-team@google.com'
DEFAULT_RELEASE_NOTIFY_REPLY_ADDRESS = ('DoubleHelix Discuss '
                                        '<double-helix-discuss@google.com>')
RELEASE_NOTE_ITEM_PREFIX = r'* '
RELEASE_NOTE_RAPID_MAX_CLS = 'RELEASE_NOTE_RAPID_MAX_CLS'
RELEASE_NOTE_RAPID_RPC_TIMEOUT = 'RELEASE_NOTE_RAPID_RPC_TIMEOUT'
RELEASE_NOTE_RAPID_RELEASE_LIMIT = 'RELEASE_NOTE_RAPID_RELEASE_LIMIT'
DH_BUG_LINK = r'http://go/double-helix-bug'

# Email template name constants.
EMAIL_TEMPLATE_BTP_SUMMARY_REPORT = 'BTP_SUMMARY_REPORT'
EMAIL_TEMPLATE_VERIFY_PATHS_COUNT = 'VERIFY_PATHS_COUNT'

# Email package constants.
EMAIL_BUCKET_NAME = 'doublehelixemail'
RIVER_MINE_EMAIL = ('rm_rpts_to_netops <c19d72eae86a4403a34a6b9a1698c10a@'
                    'netdesign-prod.appspotmail.com>')

# Transport InfraCap.
TOTAL_INFRA_CAP_QUERY = 'TotalInfraCap_'

# Double Helix Tables for BigQuery.
EXPORT_BQ_DATASET = 'EXPORT_BQ_DATASET'
EXPORT_CSV_TARGETS = 'EXPORT_CSV_TARGETS'
EXPORT_BQ_TARGETS = 'EXPORT_BQ_TARGETS'
EXPORT_BQ_EXCLUDED_KINDS = 'EXPORT_BQ_EXCLUDED_KINDS'

# PathElement L1 Transport Vendors.
PE_VENDOR_ALU = 'alcatel-lucent'
PE_VENDOR_BTI = 'bti'
PE_VENDOR_CIE = 'ciena'
PE_VENDOR_INF = 'infinera'
PE_VENDOR_NSN = 'siemens'
PE_VENDOR_SUP = 'supernova'
PE_VENDOR_SIE = PE_VENDOR_NSN
PE_L1_VENDORS = [PE_VENDOR_ALU, PE_VENDOR_BTI, PE_VENDOR_CIE, PE_VENDOR_INF,
                 PE_VENDOR_SUP, PE_VENDOR_NSN]

# Various representation of devices in Device.description/Part__name.
DEVICE_VENDOR_ALU = 'alcatel[- ]*lucent|alu'
DEVICE_VENDOR_JDSU = 'jdsu'

# Manufacturer representation.
MANUFACTURE_ALU = PE_VENDOR_ALU
MANUFACTURE_BTI = PE_VENDOR_BTI
MANUFACTURE_CIE = PE_VENDOR_CIE
MANUFACTURE_INF = PE_VENDOR_INF
MANUFACTURE_NSN = 'nokia siemens networks'
MANUFACTURE_SIE = MANUFACTURE_NSN
MANUFACTURE_SUP = PE_VENDOR_SUP
MANUFACTURE_UTP = 'google'

# PathElement Interface Components.
PE_INTF_CHASSIS = 'chassis'
PE_INTF_LINECARD = 'linecard'
PE_INTF_MODULE = 'module'
PE_INTF_PORT = 'port'

# Device name delimeters.
DEV_NAME_DELIMITERS = r'-: '
DEV_NAME_DELIMITERS_INFINERA = r'-: \.'

# Device Reconciliation.
DEVICE_RECON_DEV_NAME_OPT_OUT_REGEX = 'DEVICE_RECON_DEV_NAME_OPT_OUT_REGEX'
DEVICE_RECON_DEV_TYPE_OPT_OUT_REGEX = 'DEVICE_RECON_DEV_TYPE_OPT_OUT_REGEX'
DEVICE_RECON_PART_NAME_OPT_IN_REGEX = 'DEVICE_RECON_PART_NAME_OPT_IN_REGEX'
DEVICE_RECON_RESET_SEQUENCE = 'DEVICE_RECON_RESET_SEQUENCE'
DEVICE_RECON_MULTI_CHASSIS_DEV_TYPES = 'DEVICE_RECON_MULTI_CHASSIS_DEV_TYPES'
DEVICE_RECON_NETWORKING_POPT_TYPE_REGEX = (
    'DEVICE_RECON_NETWORKING_POPT_TYPE_REGEX')

# Email Subscriptions.
CREATION_NOTIFICATION_EMAILS = 'CREATION_NOTIFICATION_EMAILS_'

# View constants.
JSON_CONTENT_TYPE = 'application/json; charset=utf-8'

# Service account suffix.
SA_ACCOUNT_SUFFIX = 'gserviceaccount.com'

# Cache key qualifiers.
PART_NAME_UNIQUE_CHECK = 'Part.name-uniquecheck'

# Spectrum frequency digits.
SPECTRUM_FREQ_DIGITS = 4

# Force init of SpectrumDesign to set templates.
SPECTRUM_DESIGN_FORCE_INIT_TEMPLATE = 'SPECTRUM_DESIGN_FORCE_INIT_TEMPLATE'

# Default power consumption for Parts.
DEFAULT_POWER_CONSUMPTION = 0.0

# Power fields in searching Part model for power rollups.
PARTS_POWER_FIELDS = ['nebs_25c_watts',
                      'nebs_40c_watts',
                      'nebs_55c_watts',
                      'tested_80f_watts',
                      'tested_90f_watts',
                      'tested_100f_watts',
                      'actual_power_w']

# Maximum number of children to search for child Part in Device Templates.
MAX_DEVICEPART_LEVEL_SEARCH = 10
MIN_RU = 0.5

# The name of a setting in the admin UI, a list of log_codes that will not
# genetate emails.
SETTING_LOGGING_MUTE = 'LOGGING_MUTE'

# The name of a setting in the admin UI, int, duration in seconds over which to
# debounce emails
ERROR_LOGGING_DEBOUNCE_TIME = 'ERROR_LOGGING_DEBOUNCE_TIME'

# Default value for ERROR_LOGGING_DEBOUNCE_TIME setting.
DEFAULT_ERROR_LOGGING_DEBOUNCE_TIME = 60 * 5

FLOOR_NUMBER = 'floor_number'

# Circuit constants.
CIRCUIT_FORCE_INIT = 'CIRCUIT_FORCE_INIT'
CIRCUIT_PE_TO_CE_FILTER_POP_A = 'CIRCUIT_PE_TO_CE_FILTER_POP_A'
CIRCUIT_ID_RESET_SEQUENCE = 'CIRCUIT_ID_RESET_SEQUENCE'

CIRCUIT_ID_PREFIX_FOR_CHIPMUNK = 'C'
CIRCUIT_ID_PREFIX_FOR_DOUBLEHELIX = 'D'
CIRCUIT_ID_DELIM = '-'
CIRCUIT_ACT_PATH_NOTE = 'ACT path'
CIRCUIT_PORT_NAME_PREFIX = r'port-'
CIRCUIT_PORT_NAME_ALPHA_NUMERIC_REGEX = r'^([A-Z]+)(\d+)$'
CIRCUIT_RAW_PATH_DELIM = ':'
CIRCUIT_RAW_PATH_WITH_HWOPS = 'CIRCUIT_RAW_PATH_WITH_HWOPS'
CIRCUIT_ACT_PATH_BUCKET = 'doublehelix-act-path-'
CIRCUIT_ACT_UNM_PATH_MODEL = 'UNM_PATHS_MODEL'

# Settings related to ACT circuit.
ACT_SETTING_STOAT_RPC_DEADLINE = 'ACT_SETTING_STOAT_RPC_DEADLINE'
ACT_SETTING_STOAT_TRANSIENT_ERRORS = 'ACT_SETTING_STOAT_TRANSIENT_ERRORS'
ACT_SETTING_UNM_PATHS_BATCH_SIZE = 'ACT_SETTING_UNM_PATHS_BATCH_SIZE'

ACT_TEST_EK_PHYSICAL_PACKET_LINKS = 'ACT_TEST_EK_PHYSICAL_PACKET_LINKS'
ACT_TEST_PATHS_MODEL_FILE_NAME = 'ACT_TEST_PATHS_MODEL_FILE_NAME'

CHIPMUNK_PROXY_BLADE = 'blade:stoat-chipmunk-proxy-prod'
CHIPMUNK_SANDBOX_BLADE = 'blade:stoat-chipmunk-proxy-sandbox'
PATH_VALIDATION_BLADE = 'blade:stoat-prod-path-validation'
DISABLE_STOAT_VALIDATION_SETTING = 'DISABLE_STOAT_VALIDATION'
USE_STOAT_PROD_PROXY_IN_NON_PROD_SETTING = 'USE_STOAT_PROD_PROXY_IN_NON_PROD'

PORT_STATUS_UPDATE_MUTEX_EXP_TIME_SEC = (
    'PORT_STATUS_UPDATE_MUTEX_EXP_TIME_SEC')
PORT_STATUS_UPDATE_MUTEX_EXP_TIME_SEC_DEFAULT = 300
PORT_STATUS_UPDATE_MUTEX_ACQUIRE_TIME_SEC = (
    'PORT_STATUS_UPDATE_MUTEX_ACQUIRE_TIME_SEC')
PORT_STATUS_UPDATE_MUTEX_ACQUIRE_TIME_SEC_DEFAULT = 900

CIRCUIT_PARENT_UPDATE_MUTEX_EXP_TIME_SEC = (
    'CIRCUIT_PARENT_UPDATE_MUTEX_EXP_TIME_SEC')
CIRCUIT_PARENT_UPDATE_MUTEX_EXP_TIME_SEC_DEFAULT = 300
CIRCUIT_PARENT_UPDATE_MUTEX_ACQUIRE_TIME_SEC = (
    'CIRCUIT_PARENT_UPDATE_MUTEX_ACQUIRE_TIME_SEC')
CIRCUIT_PARENT_UPDATE_MUTEX_ACQUIRE_TIME_SEC_DEFAULT = 900

CIRCUIT_PARENT_CREATE_MUTEX_EXP_TIME_SEC = (
    'CIRCUIT_PARENT_CREATE_MUTEX_EXP_TIME_SEC')
CIRCUIT_PARENT_CREATE_MUTEX_EXP_TIME_SEC_DEFAULT = 100
CIRCUIT_PARENT_CREATE_MUTEX_ACQUIRE_TIME_SEC = (
    'CIRCUIT_PARENT_CREATE_MUTEX_ACQUIRE_TIME_SEC')
CIRCUIT_PARENT_CREATE_MUTEX_ACQUIRE_TIME_SEC_DEFAULT = 100

# Port reservations.
PORT_RESERVATION_MUTEX_EXP_TIME_SEC = (
    'PORT_RESERVATION_MUTEX_EXP_TIME_SEC')
PORT_RESERVATION_MUTEX_EXP_TIME_SEC_DEFAULT = 600
PORT_RESERVATION_MUTEX_ACQUIRE_TIME_SEC = (
    'PORT_RESERVATION_MUTEX_ACQUIRE_TIME_SEC')
PORT_RESERVATION_MUTEX_ACQUIRE_TIME_SEC_DEFAULT = 600
NOT_FOUND = 'Not found'

# Capacity
CAPACITY_TRANSIT_SITE = 'site'

# Constants key for rack copy parameters.
SOURCE_KEY_NAME = 'source_key_name'
TARGET_SPACE_KEY_NAME = 'target_space_key_name'
NUMBER_OF_RACKS = 'number_of_racks'
NEW_RACK_STATUS = 'new_rack_status'
TARGET_NAME = 'target_name'

# Setting constant for groups with default write access.
LDAP_GROUPS_DEFAULT_WRITE = 'LDAP_GROUPS_DEFAULT_WRITE'
EVERYONE_DEFAULT_READ = '%everyone'
ALL_LDAP_GROUPS = 'LDAP_GROUPS'
READ_OP = 'read'
WRITE_OP = 'write'

# Floor name formats.
BASEMENT_NAME_FORMAT = '%s.B%d'
BASEMENT_SUBBUILDING_NAME_FORMAT = '%s.' + BASEMENT_NAME_FORMAT
FLOOR_NAME_FORMAT = '%s.F%d'
FLOOR_SUBBUILDING_NAME_FORMAT = '%s.' + FLOOR_NAME_FORMAT

# Actions.
DELETED = 'deleted'

# Settings for admin groups for updating permissions.
LIST_ADMIN_GROUPS_PERMISSIONS_UPDATE = 'LIST_ADMIN_GROUPS_PERMISSIONS_UPDATE'
DEFAULT_ADMIN_GROUPS_PERMISSIONS_UPDATE = ['doublehelix-admin']

# Setting name of list of email addresses that should receive emails
# about "empty" metadata that can be deleted.
CLEAN_METADATA_EMAIL_RECIPIENTS = 'CLEAN_METADATA_EMAIL_RECIPIENTS'

# Building.
BUILDING_NAME_FORMAT = '%s%d'

# Space.
SPACE_NAME_FORMAT = '%s.S%d'
SPACE_DELIMITER = '.S'

# SubBuilding FQN format.
SUBBUILDING_FQN_FORMAT = '%s:%s'

# Vendor Patch Panel and Splice Closure name format.
VENDOR_CATEGORY_NAME_FORMAT = '%s-%s'

COPPER_PANEL_NAME_FORMAT = VENDOR_CATEGORY_NAME_FORMAT

COMMISSIONING_STATUS = 'commissioning_status'

PROJECT_ID_PATTERN = re.compile(r'^(prj|del|req|pgm|tsk)-\d{1,6}$')

# Mail template names
BOM_CANCEL = 'BOM_CANCEL'
BOM_ORDER = 'BOM_ORDER'
BOM_REVIEW = 'BOM_REVIEW'
CLEAN_METADATA = 'CLEAN_METADATA'
CLEAN_ENTITIES = 'clean_entities'
ENTITY_SUBSCRIPTION = 'ENTITY_SUBSCRIPTION'
KIND_CREATION_NOTIFICATION = 'KIND_CREATION_NOTIFICATION'
LOG_SERVICE_EMAIL_TEMPLATE = 'LOG_SERVICE'
ORDER_STATUS_CHANGE = 'ORDER_STATUS_CHANGE'
ORDER_CURRENT_COMMIT_DATE_CHANGE = 'ORDER_CURRENT_COMMIT_DATE_CHANGE'
ORDER_ONSITE_REQUEST_DATE_CHANGE = 'ORDER_ONSITE_REQUEST_DATE_CHANGE'
ORDER_ITEM_CANCEL = 'ORDER_ITEM_CANCEL'
ORDER_ITEM_CURRENT_COMMIT_DATE_CHANGE = 'ORDER_ITEM_CURRENT_COMMIT_DATE_CHANGE'
ORDER_ITEM_ONSITE_REQUEST_DATE_CHANGE = 'ORDER_ITEM_ONSITE_REQUEST_DATE_CHANGE'
ORDER_STATUS_VALUES = ['Received', 'Scheduled', 'Hold', 'Canceled',
                       'ReleasedToWarehouse', 'ShipPerCommitDate',
                       'ApprovedForPartialShipping', 'Shipped', 'Delivered']

# Device naming related constants.
# Space function values in the db.
SPACE_FUNCTION_VALUE_SERVER_FLOOR = 'DC Server Floor'
SPACE_FUNCTION_VALUE_SSNR = 'SSNR'
SPACE_FUNCTION_VALUE_CNR = 'CNR'  # Logic uses 'in' to handle both CCNR/CNR.
SPACE_FUNCTION_VALUE_CCNR = 'CCNR'
SPACE_FUNCTION_VALUE_CORP = 'Corp'
SPACE_FUNCTION_VALUE_POE = 'Point Of Entry'
# Enable GTAPE and FSA when requested.
SPACE_FUNCTION_VALUE_GTAPE = '-do-not-match'  # 'Gtape'
SPACE_FUNCTION_VALUE_FSA = '-do-not-match'  # 'Fsa'

# Space function prefix used for naming the device.
SPACE_FUNCTION_PREFIX_SERVER_FLOOR = 'SPP'
SPACE_FUNCTION_PREFIX_SSNR = 'PP'  # No prefix before PP.
SPACE_FUNCTION_PREFIX_CNR = 'CPP'
SPACE_FUNCTION_PREFIX_GTAPE = 'GPP'
SPACE_FUNCTION_PREFIX_FSA = 'FPP'

# Mapping of space function naming codes to space function values in db.
SPACE_FUNCTION_DICT = dict(zip(
    (SPACE_FUNCTION_PREFIX_SERVER_FLOOR,
     SPACE_FUNCTION_PREFIX_SSNR,
     SPACE_FUNCTION_PREFIX_CNR,  # Shared for both CNR and CCNR.
     SPACE_FUNCTION_PREFIX_GTAPE,
     SPACE_FUNCTION_PREFIX_FSA),
    (SPACE_FUNCTION_VALUE_SERVER_FLOOR,
     SPACE_FUNCTION_VALUE_SSNR,
     SPACE_FUNCTION_VALUE_CNR,
     SPACE_FUNCTION_VALUE_GTAPE,
     SPACE_FUNCTION_VALUE_FSA)))

# Abbreviations used in the Port Capacity and Usage report.
# At this time only one is abbreviated.
SPACE_FUNCTION_ABBREVIATIONS = dict(zip(
    (SPACE_FUNCTION_VALUE_SERVER_FLOOR,
     SPACE_FUNCTION_VALUE_SSNR,
     SPACE_FUNCTION_VALUE_CNR,
     SPACE_FUNCTION_VALUE_CCNR,
     SPACE_FUNCTION_VALUE_CORP,
     SPACE_FUNCTION_VALUE_GTAPE,
     SPACE_FUNCTION_VALUE_FSA),
    ('SF',
     SPACE_FUNCTION_VALUE_SSNR,
     SPACE_FUNCTION_VALUE_CNR,
     SPACE_FUNCTION_VALUE_CCNR,
     SPACE_FUNCTION_VALUE_CORP,
     SPACE_FUNCTION_VALUE_GTAPE,
     SPACE_FUNCTION_VALUE_FSA)))

# Automated device naming is dependent on the rmu.
MAX_RMU = 45
MAX_NGF_RAILS = 2
# This pair of constants determine the name of the HWOPS device.
RMUS = (36, 29, 22, 15, 8, 1)  # The code depends on decreasing order.
HWOPS_RACK_NAMES = ['ABCDEF', 'GHIJKL']
# Rack type required for HWOPS Splice Closure naming and fqn.
RACK_OMX_CABINET_PREFIX = 'cabinet OMX'

SEQUENCING_ATTR_FORMAT = '%s%06d'

# References constants.
REFERENCE_CLUSTER = 'cluster'
REFERENCE_CLUSTER_ID = 'cluster_id'
REFERENCE_FUNCTION = 'function'
REFERENCE_LEVEL = 'level'
REFERENCE_METRO_PAIR = 'metro_pair'
REFERENCE_METRO_SCOPE = 'metro_scope'
REFERENCE_NEIGHBORHOOD = 'neighborhood'
REFERENCE_POP_SCOPE = 'pop_scope'

REFERENCE_DEVICE = 'device'
REFERENCE_INTER_METRO = 'inter-metro'
REFERENCE_METRO = 'metro'
REFERENCE_NAME = 'name'
REFERENCE_PATH = 'path'
REFERENCE_PEER = 'peer'
REFERENCE_POP = 'pop'
REFERENCE_ROLE = 'role'
REFERENCE_SITE = 'site'
REFERENCE_TRANSIT = 'transit'

REFERENCE_B2_NETWORK = 'b2'
REFERENCE_B4_NETWORK = 'b4'

# Constants for fallout.
RUNTIME_ERROR = '__runtime__'
RUNTIME = 'RUNTIME'
WARNING = 'WARNING'
ERROR = 'ERROR'
VALIDATOR_CONTROLLER = 'CONTROLLER'
VALIDATOR_METADATA = 'METADATA'
FALLOUT_FIELDS = 'FALLOUT_FIELDS'

# Building constants.
BUILDING_TYPE_GOOGLE_DATA_CENTER = 'Google Data Center'

# Supply Chain constants.
LABELS = 'labels'
PIPELINE_ID = 'pipeline_id'

# Bazooka constants.
GUNS = 'GUNS'
PARENT_GUNS = 'PARENT_GUNS'
PARENT_KEY_NAME = 'parent_key_name'
BZ_DELETE_SYNC_HISTORY = 'BZ_DELETE_SYNC_HISTORY'

# DataPropagation Constants.
DPEVENT_VALUECHANGED = 'value_changed'
DPEVENT_VALUEADD = 'value_added'
DPEVENT_VALUEDEL = 'value_deleted'
DPEVENT_VALUEINC = 'value_increased'
DPEVENT_VALUEDEC = 'value_decreased'
DPMETA_TRIGGER = 'trigger'

# Fiber connection constants.
BATCH_FIBER_CONNECTIONS_REQUEST = 'fiber_connections'
FIBER_CONNECTION = 'FiberConnection'
A_SPLICE_KEY_NAME = 'a_splice_key_name'
STRAND_SPLICE_LIST = 'strand_splice_list'
STRAND_KEY_NAME = 'strand_key_name'
SPLICE_KEY_NAME = 'splice_key_name'
FIBER_CONNECTION_FIELDS = (A_SPLICE_KEY_NAME, STRAND_SPLICE_LIST)
TYPE_NAME_FIBER = 'Fiber'
TYPE_NAME_SPLICE_FOR_FIBERS = 'Splice for Fibers'
TYPE_NAME_EDGE_SPLICE = 'Edge Splice'

# Test related constants.
# This environment variable is set during coverage runs.
BULK_COVERAGE_RUN = 'BULK_COVERAGE_RUN'
TEST_METHOD_PREFIX = 'test'  # Prefix of methods that are tests.

# Logging constants.
LOG_CODE = 'log_code'
LOG_TYPE = 'log_type'
MESSAGE = 'message'
ENTITY_KIND = 'entity_kind'
DATA = 'data'
ENVIRONMENT = 'env'
APP_IDENTITY = 'app_id'

CREATE_OP = 'Create'
DELETE_OP = 'Delete'

CONNECTOR_TYPES = 'connector_types'
CSVIMPORT_LOG = 'User %s has performed a legacy CSV import on kind %s.'

# Local devappserver grouper groups
LOCAL_DEVAPPSERVER_GROUPER_FILE = 'localdevappservergrouper.json'
READ_ONLY = 'readonly'
NO_READ = 'noread'
OTHER = 'other'
GROUPS = 'groups'

# Miscellaneous.
NA = 'N/A'

# Patch Panel Notification constants.
NEW_TEMPLATE = 'new_template'
OLD_TEMPLATE = 'old_template'
PATCH_PANEL_TEMPLATE_NOTIFY = 'PATCH_PANEL_TEMPLATE_NOTIFY'
PANEL_NAME = 'panel_name'
PANEL_KEY_NAME = 'panel_key_name'
PATCH_PANEL_NOTIFY_EMAIL_SETTING = 'PATCH_PANEL_NOTIFY_EMAIL'
PATCH_PANEL_NOTIFY_DEFAULT_TO_ADDRESS = 'fnd@google.com'

PATCHPANEL_UPDATE_EMAIL_TEMPLATE = {
    'name': PATCH_PANEL_TEMPLATE_NOTIFY,
    'description': 'Email template for notifying change in patch panel'
                   ' template.',
    'to': [],
    'cc': [],
    'subject': 'Patch Panel Template Updates: {{timestamp}}',
    'body': ('<html><body>'
             'The following updates have been made to Patch Panels.<br>'
             '<table border=1><tr>No.<th>Panel Name</th>'
             '<th>Panel key_name</th><th>Updated On</th><th>Updated By</th>'
             '<th>New Template</th><th>Old Template</th></tr>'
             '{{content}}</table><br>'
             'Please make the corresponding changes in Netcracker.'
             '<br><br>Thank you.'
             '</body></html>')
}

# POR Kinds.
BTP_TABLES = ['B2B4POR_20141223', 'DRPOR_20150102',
              'MetroPOR_20150127', 'FPOR_20150826']

# Flag to decide whether to update stoat paths for
# handling broken ports.
UPDATE_STOAT_PATHS_FOR_BROKEN_PORTS = 'UPDATE_STOAT_PATHS_FOR_BROKEN_PORTS'

# SCULPTOR BLADE ADDRESS
SCULPTOR_PROD = 'blade:network-config-orchestrator'
SCULPTOR_SANDBOX = 'blade:network-config-orchestrator-sandbox'

# Stoat path elements
A_END_OLD_PE = 'a_end_old_pe'
A_END_NEW_PE = 'a_end_new_pe'
Z_END_OLD_PE = 'z_end_old_pe'
Z_END_NEW_PE = 'z_end_new_pe'
SIMPLEX = 'SIMPLEX'
DUPLEX = 'DUPLEX'

Z_ENDS = 'z_ends'
