"""Binary sensor platform for Enode integration."""

from collections.abc import Generator

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import LOGGER
from .coordinator import EnodeConfigEntry, EnodeCoordinators, EnodeVehiclesCoordinator
from .entity import VehicleEntity

CHARGE_STATE_DESCRIPTIONS = [
    BinarySensorEntityDescription(
        key="is_fully_charged",
        translation_key="charge_state_is_fully_charged",
        icon="mdi:battery",
    ),
    BinarySensorEntityDescription(
        key="is_plugged_in",
        translation_key="charge_state_is_plugged_in",
        device_class=BinarySensorDeviceClass.PLUG,
    ),
    BinarySensorEntityDescription(
        key="is_charging",
        translation_key="charge_state_is_charging",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
    ),
]

SMART_CHARGING_DESCRIPTIONS = [
    BinarySensorEntityDescription(
        key="is_enabled",
        translation_key="smart_charging_is_enabled",
        icon="mdi:car-electric",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: EnodeConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Enode sensor platform."""
    async_add_entities(_generate_sensors(config_entry.runtime_data))


def _generate_sensors(
    coordinator: EnodeCoordinators,
) -> Generator[BinarySensorEntity]:
    """Generate Enode sensors."""
    yield from _generate_vehicle_sensors(coordinator.vehicles)


def _generate_vehicle_sensors(
    coordinator: EnodeVehiclesCoordinator,
) -> Generator[BinarySensorEntity]:
    """Generate sensors for vehicles."""
    for vehicle in coordinator.data:
        LOGGER.debug("Generating binary sensors for vehicle %s", vehicle.id)
        if vehicle.capabilities.charge_state.is_capable:
            LOGGER.debug("Vehicle %s supports charge state", vehicle.id)
            for description in CHARGE_STATE_DESCRIPTIONS:
                yield VehicleChargeStateBinarySensor(
                    coordinator=coordinator, vehicle=vehicle, description=description
                )
        if vehicle.capabilities.smart_charging.is_capable:
            LOGGER.debug("Vehicle %s supports smart charging", vehicle.id)
            for description in SMART_CHARGING_DESCRIPTIONS:
                yield VehicleSmartChargingBinarySensor(
                    coordinator=coordinator, vehicle=vehicle, description=description
                )


class VehicleBinarySensor(VehicleEntity[EnodeVehiclesCoordinator], BinarySensorEntity):
    """Binary sensor for vehicle data."""


class VehicleChargeStateBinarySensor(VehicleBinarySensor):
    """Binary sensor for vehicle charge state."""

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        if vehicle := self.vehicle:
            return getattr(vehicle.charge_state, self.entity_description.key)
        return None


class VehicleSmartChargingBinarySensor(VehicleBinarySensor):
    """Binary sensor for vehicle smart charging."""

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        if vehicle := self.vehicle:
            return getattr(vehicle.smart_charging_policy, self.entity_description.key)
        return None
