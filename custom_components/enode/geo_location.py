"""Geo Location platform for Enode integration."""

from collections.abc import Generator

from homeassistant.components.geo_location import GeolocationEvent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import LOGGER
from .coordinator import EnodeConfigEntry, EnodeCoordinators, EnodeVehiclesCoordinator
from .entity import VehicleEntity

DESCRIPTION = EntityDescription(
    key="location",
    translation_key="location",
    icon="mdi:map-marker",
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: EnodeConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Enode sensor platform."""
    async_add_entities(_generate_sensors(config_entry.runtime_data))


def _generate_sensors(
    coordinator: EnodeCoordinators,
) -> Generator[GeolocationEvent]:
    """Generate Enode sensors."""
    yield from _generate_vehicle_sensors(coordinator.vehicles)


def _generate_vehicle_sensors(
    coordinator: EnodeVehiclesCoordinator,
) -> Generator[GeolocationEvent]:
    """Generate sensors for vehicles."""
    for vehicle in coordinator.data:
        LOGGER.debug("Generating sensors for vehicle %s", vehicle.id)
        if vehicle.capabilities.location.is_capable:
            LOGGER.debug("Vehicle %s supports location", vehicle.id)
            yield VehicleGeolocation(
                coordinator=coordinator, vehicle=vehicle, description=DESCRIPTION
            )


class VehicleGeolocation(VehicleEntity[EnodeVehiclesCoordinator], GeolocationEvent):
    """Representation of a vehicle's geolocation."""

    @property
    def source(self) -> str:
        """Return the source of the geolocation."""
        if vehicle := self.vehicle:
            return vehicle.vendor
        return ""

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
