"""Device Tracker platform for Enode integration."""

from collections.abc import Generator

from homeassistant.components.device_tracker import (
    TrackerEntity,
    TrackerEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import LOGGER
from .coordinator import EnodeConfigEntry, EnodeCoordinators, EnodeVehiclesCoordinator
from .entity import VehicleEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: EnodeConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Enode sensor platform."""
    async_add_entities(_generate_trackers(config_entry.runtime_data))


def _generate_trackers(
    coordinator: EnodeCoordinators,
) -> Generator[TrackerEntity]:
    """Generate Enode trackers."""
    yield from _generate_vehicle_trackers(coordinator.vehicles)


def _generate_vehicle_trackers(
    coordinator: EnodeVehiclesCoordinator,
) -> Generator[TrackerEntity]:
    """Generate trackers for vehicles."""
    for vehicle in coordinator.data or []:
        LOGGER.debug("Generating tracker for vehicle %s", vehicle.id)
        if vehicle.capabilities.location.is_capable:
            LOGGER.debug("Vehicle %s supports location", vehicle.id)
            yield VehicleTracker(coordinator=coordinator, vehicle=vehicle)


class VehicleTracker(VehicleEntity[EnodeVehiclesCoordinator], TrackerEntity):
    """Representation of a vehicle's location."""

    entity_description = TrackerEntityDescription(
        key="location",
        translation_key="location",
        icon="mdi:map-marker",
    )

    @property
    def latitude(self) -> float | None:
        """Return the latitude of the vehicle."""
        if vehicle := self.vehicle:
            return vehicle.location.latitude
        return None

    @property
    def longitude(self) -> float | None:
        """Return the longitude of the vehicle."""
        if vehicle := self.vehicle:
            return vehicle.location.longitude
        return None

    @property
    def extra_state_attributes(self) -> dict[str, str | None] | None:
        """Return the state attributes of the vehicle."""
        if vehicle := self.vehicle:
            last_updated = (
                str(vehicle.location.last_updated)
                if vehicle.location.last_updated
                else None
            )
            return {
                "location_id": vehicle.location.id,
                "last_updated": last_updated,
            }
        return None
