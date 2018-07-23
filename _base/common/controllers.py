"""List of Controllers."""

from google3.ops.netdeploy.netdesign.server.bom import bom_controller
from google3.ops.netdeploy.netdesign.server.bom import bom_item_controller
from google3.ops.netdeploy.netdesign.server.cables import cables_controller
from google3.ops.netdeploy.netdesign.server.cables import strands_controller
from google3.ops.netdeploy.netdesign.server.capacity import capacity_controller
from google3.ops.netdeploy.netdesign.server.capacity import capacity_reference_controller
from google3.ops.netdeploy.netdesign.server.capacity import network_connection_controller
from google3.ops.netdeploy.netdesign.server.capacity import sub_topology_controller
from google3.ops.netdeploy.netdesign.server.circuits import circuit_controller
from google3.ops.netdeploy.netdesign.server.circuits import circuit_element_controller
from google3.ops.netdeploy.netdesign.server.devices import devices_controller
from google3.ops.netdeploy.netdesign.server.devices import logical_devices_controller
from google3.ops.netdeploy.netdesign.server.devices import splice_controller
from google3.ops.netdeploy.netdesign.server.hardware import hardware_controller
from google3.ops.netdeploy.netdesign.server.locations.building import building_controller
from google3.ops.netdeploy.netdesign.server.locations.floor import floor_controller
from google3.ops.netdeploy.netdesign.server.locations.osp_container import osp_container_controller
from google3.ops.netdeploy.netdesign.server.locations.space import overhead_cable_controller
from google3.ops.netdeploy.netdesign.server.locations.space import space_controller
from google3.ops.netdeploy.netdesign.server.locations.subbuilding import subbuilding_controller
from google3.ops.netdeploy.netdesign.server.logical_locations import logical_locations_controller
from google3.ops.netdeploy.netdesign.server.manufacturers import manufacturer_controller
from google3.ops.netdeploy.netdesign.server.on_network_inventory_mapping import on_network_inventory_mapping_controller as onim_controller
from google3.ops.netdeploy.netdesign.server.orders import order_controller
from google3.ops.netdeploy.netdesign.server.orders import order_item_controller
from google3.ops.netdeploy.netdesign.server.parts import parts_controller
from google3.ops.netdeploy.netdesign.server.ports import reservation_controller
from google3.ops.netdeploy.netdesign.server.racks import rackrows_controller
from google3.ops.netdeploy.netdesign.server.racks import racks_controller
from google3.ops.netdeploy.netdesign.server.sockets import sockets_controller
from google3.ops.netdeploy.netdesign.server.transport import ls_optics_controller
from google3.ops.netdeploy.netdesign.server.transport import oms_controller
from google3.ops.netdeploy.netdesign.server.transport.physical_spof import physical_spof_controller
from google3.ops.netdeploy.netdesign.server.transport.submarine_oms_ots import submarine_oms_ots_controller
from google3.ops.netdeploy.netdesign.server.transport.thirdparty_transport import thirdparty_transport_controller
from google3.ops.netdeploy.netdesign.server.vendors import vendors_controller


# Controller mapping.
CONTROLLER_MAP = {
    'BOM':
        bom_controller.BOMController(),
    'BOMItem':
        bom_item_controller.BOMItemController(),
    'Building':
        building_controller.BuildingController(),
    'Cable':
        cables_controller.CableController(),
    'CapacityReference':
        capacity_reference_controller.CapacityReferenceController(),
    'Circuit':
        circuit_controller.CircuitController(),
    'CircuitElement':
        circuit_element_controller.CircuitElementController(),
    'Device':
        devices_controller.DeviceController(),
    'DHTPS':
        capacity_controller.TpsController(),
    'Floor':
        floor_controller.FloorController(),
    'Hardware':
        hardware_controller.HardwareController(),
    'InterMetro':
        capacity_controller.InterMetrosController(),
    'LogicalDevice':
        logical_devices_controller.LogicalDeviceController(),
    'LSOptics':
        ls_optics_controller.LSOpticsController(),
    'Manufacturer':
        manufacturer_controller.ManufacturerController(),
    'Metro':
        logical_locations_controller.MetroController(),
    'NetworkConnection':
        network_connection_controller.NetworkConnectionController(),
    'OMS':
        oms_controller.OMSController(),
    'OnNetworkInventoryMapping':
        onim_controller.OnNetworkInventoryMappingController(),
    'Order':
        order_controller.OrderController(),
    'OrderItem':
        order_item_controller.OrderItemController(),
    'OspContainer':
        osp_container_controller.OSPContainerController(),
    'OverheadCable':
        overhead_cable_controller.OverheadCableController(),
    'Part':
        parts_controller.PartController(),
    'PhysicalSPOF':
        physical_spof_controller.PhysicalSPOFController(),
    'Pop':
        logical_locations_controller.PopController(),
    'PortReservation':
        reservation_controller.PortReservationController(),
    'Rack':
        racks_controller.RackController(),
    'RackRow':
        rackrows_controller.RackRowController(),
    'Socket':
        sockets_controller.SocketController(),
    'Space':
        space_controller.SpaceController(),
    'Splice':
        splice_controller.SpliceController(),
    'Strand':
        strands_controller.StrandController(),
    'SubBuilding':
        subbuilding_controller.SubBuildingController(),
    'SubmarineOMSToOTS':
        submarine_oms_ots_controller.SubmarineOMSToOTSController(),
    'SubTopology':
        sub_topology_controller.SubTopologyController(),
    'ThirdPartyTransport':
        thirdparty_transport_controller.ThirdPartyTransportController(),
    'Vendor':
        vendors_controller.VendorController(),
}
