"""Switch platform for Enode integration."""

from collections.abc import Generator

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import EnodeClient
from .const import LOGGER
from .coordinator import EnodeConfigEntry, EnodeCoordinators, EnodeVehiclesCoordinator
from .entity import VehicleEntity
from .models import Vehicle


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: EnodeConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Enode binary sensor platform."""
    async_add_entities(_generate_switches(config_entry.runtime_data))


def _generate_switches(
    coordinator: EnodeCoordinators,
) -> Generator[SwitchEntity]:
    """Generate Enode switches."""
    yield from _generate_vehicle_switches(coordinator.vehicles, coordinator.client)


def _generate_vehicle_switches(
    coordinator: EnodeVehiclesCoordinator,
    client: EnodeClient,
) -> Generator[SwitchEntity]:
    """Generate vehicle switches."""
    for vehicle in coordinator.data or []:
        if (
            vehicle.capabilities.start_charging.is_capable
            or vehicle.capabilities.stop_charging.is_capable
        ):
            LOGGER.debug("Adding vehicle charge switch for %s", vehicle.id)
            yield VehicleChargeSwitch(coordinator, client, vehicle)


class VehicleChargeSwitch(VehicleEntity[EnodeVehiclesCoordinator], SwitchEntity):
    """Switch for vehicle charge state."""

    def __init__(
        self,
        coordinator: EnodeVehiclesCoordinator,
        client: EnodeClient,
        vehicle: Vehicle,
    ) -> None:
        """Initialize the vehicle charge switch."""
        super().__init__(
            coordinator=coordinator,
            vehicle=vehicle,
            description=SwitchEntityDescription(
                key="is_charging",
                translation_key="charge_state_is_charging",
                device_class=SwitchDeviceClass.SWITCH,
            ),
        )
        self.client = client

    @property
    def is_on(self) -> bool | None:
        """Return true if the vehicle is charging."""
        if vehicle := self.vehicle:
            return vehicle.charge_state.is_charging
        return None

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on charging for the vehicle."""
        if (vehicle := self.vehicle) and vehicle.capabilities.start_charging.is_capable:
            await self.client.control_charging(vehicle_id=vehicle.id, action="START")

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off charging for the vehicle."""
        if (vehicle := self.vehicle) and vehicle.capabilities.stop_charging.is_capable:
            await self.client.control_charging(vehicle_id=vehicle.id, action="STOP")
