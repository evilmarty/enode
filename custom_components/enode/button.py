"""Button platform for Enode integration."""

from collections.abc import Generator

from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import EnodeClient
from .coordinator import EnodeConfigEntry, EnodeCoordinators, EnodeVehiclesCoordinator
from .entity import VehicleEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: EnodeConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Enode sensor platform."""
    async_add_entities(_generate_buttons(config_entry.runtime_data))


def _generate_buttons(
    coordinator: EnodeCoordinators,
) -> Generator[ButtonEntity]:
    """Generate Enode buttons."""
    yield from _generate_vehicle_buttons(coordinator.vehicles, coordinator.client)


def _generate_vehicle_buttons(
    coordinator: EnodeVehiclesCoordinator,
    client: EnodeClient,
) -> Generator[ButtonEntity]:
    """Generate buttons for vehicles."""
    for vehicle in coordinator.data or []:
        yield VehicleRefreshButton(
            coordinator=coordinator, vehicle=vehicle, client=client
        )


class VehicleRefreshButton(VehicleEntity[EnodeVehiclesCoordinator], ButtonEntity):
    """Button to refresh vehicle data."""

    entity_description = ButtonEntityDescription(
        key="refresh",
        translation_key="vehicle_refresh",
        device_class=ButtonDeviceClass.RESTART,
        entity_category=EntityCategory.DIAGNOSTIC,
    )

    async def async_press(self) -> None:
        """Press the button to refresh vehicle data."""
        await self.client.refresh_vehicle_data(self.vehicle_id)
