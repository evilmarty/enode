"""Button platform for Enode integration."""

from collections.abc import Generator

from homeassistant.components import persistent_notification
from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import EnodeClient, EnodeError
from .const import LOGGER
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
        try:
            await self.client.refresh_vehicle_data(self.vehicle_id)
        except EnodeError as err:
            LOGGER.error(
                "Failed to refresh data for vehicle %s: %s - %s",
                self.vehicle_id,
                err.data.title,
                err.data.detail,
            )
            persistent_notification.create(
                hass=self.hass,
                message=err.data.detail,
                title=self._friendly_name_internal(),
                notification_id=f"{self.entity_id}_notification",
            )
