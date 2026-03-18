"""Enode entity module."""

from homeassistant.helpers.entity import DeviceInfo, EntityDescription
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .api import EnodeClient
from .const import DOMAIN
from .models import Vehicle


def _get_vehicle_device_info(
    vehicle: Vehicle,
) -> DeviceInfo:
    """Get device info for a vehicle."""
    indentifiers = {(DOMAIN, vehicle.id)}
    if vehicle.capabilities.information.is_capable:
        if vehicle.information.vin:
            indentifiers.add((DOMAIN, vehicle.information.vin))
        return DeviceInfo(
            identifiers=indentifiers,
            name=(
                vehicle.information.display_name  # Display name can be none
                or f"{vehicle.information.brand} {vehicle.information.model}"
            ),
            manufacturer=vehicle.information.brand,
            model=vehicle.information.model,
            serial_number=vehicle.information.vin,
        )
    return DeviceInfo(identifiers=indentifiers)


class VehicleEntity[_DataUpdateCoordinatorT: DataUpdateCoordinator](
    CoordinatorEntity[_DataUpdateCoordinatorT]
):
    """Base class for vehicle entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: _DataUpdateCoordinatorT,
        vehicle: Vehicle,
        client: EnodeClient | None = None,
        description: EntityDescription | None = None,
    ) -> None:
        """Initialize the vehicle entity."""
        super().__init__(coordinator)
        if description is not None:
            self.entity_description = description
        self.vehicle_id = vehicle.id
        self.client = client
        self.device_info = _get_vehicle_device_info(vehicle)
        self._attr_unique_id = f"vehicle_{vehicle.id}_{self.entity_description.key}"
        self._attr_extra_state_attributes = {
            "vehicle_id": vehicle.id,
            "user_id": vehicle.user_id,
        }

    @property
    def vehicle(self) -> Vehicle | None:
        """Return the vehicle object."""
        for vehicle in self.coordinator.data:
            if vehicle.id == self.vehicle_id:
                return vehicle
        return None

    @property
    def available(self) -> bool:
        """Return True if the entity is available."""
        if vehicle := self.vehicle:
            return vehicle.is_reachable is True
        return False
