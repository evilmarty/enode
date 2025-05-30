"""Geo Location platform for Enode integration."""

from collections.abc import Generator

from homeassistant.components.geo_location import GeolocationEvent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import LOGGER, STATE_REACHABLE, STATE_UNREACHABLE
from .coordinator import EnodeConfigEntry, EnodeCoordinators, EnodeVehiclesCoordinator
from .entity import VehicleEntity


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
    for vehicle in coordinator.data or []:
        LOGGER.debug("Generating sensors for vehicle %s", vehicle.id)
        if vehicle.capabilities.location.is_capable:
            LOGGER.debug("Vehicle %s supports location", vehicle.id)
            yield VehicleGeolocation(coordinator=coordinator, vehicle=vehicle)


class VehicleGeolocation(VehicleEntity[EnodeVehiclesCoordinator], GeolocationEvent):
    """Representation of a vehicle's geolocation."""

    entity_description = EntityDescription(
        key="location",
        translation_key="location",
        icon="mdi:map-marker",
        entity_registry_enabled_default=False,
    )

    @property
    def state(self) -> str | None:
        """Return the state of the geolocation."""
        if vehicle := self.vehicle:
            return STATE_REACHABLE if vehicle.is_reachable else STATE_UNREACHABLE
        return None

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
