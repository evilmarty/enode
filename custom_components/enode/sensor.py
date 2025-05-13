"""Sensor platform for Enode integration."""

from abc import abstractmethod
from collections.abc import Generator
from datetime import datetime, time
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfEnergy,
    UnitOfLength,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import LOGGER
from .coordinator import EnodeConfigEntry, EnodeCoordinators, EnodeVehiclesCoordinator
from .entity import VehicleEntity
from .models import ChargeState, PowerDeliveryState

CHARGE_STATE_DESCRIPTIONS = [
    SensorEntityDescription(
        key="battery_capacity",
        translation_key="charge_state_battery_capacity",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="battery_level",
        translation_key="charge_state_battery_level",
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="charge_limit",
        translation_key="charge_state_charge_limit",
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="charge_time_remaining",
        translation_key="charge_state_charge_time_remaining",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=UnitOfTime.MINUTES,
    ),
    SensorEntityDescription(
        key="max_current",
        translation_key="charge_state_max_current",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=0,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="power_delivery_state",
        translation_key="charge_state_power_delivery_state",
        device_class=SensorDeviceClass.ENUM,
        options=set(PowerDeliveryState),
    ),
    SensorEntityDescription(
        key="range",
        translation_key="charge_state_range",
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        suggested_display_precision=0,
    ),
]

ODOMETER_DESCRIPTIONS = [
    SensorEntityDescription(
        key="distance",
        translation_key="odometer_distance",
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        suggested_display_precision=0,
    ),
]

SMART_CHARGING_DESCRIPTIONS = [
    SensorEntityDescription(
        key="deadline",
        translation_key="smart_charging_deadline",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    SensorEntityDescription(
        key="minimum_charge_limit",
        translation_key="smart_charging_minimum_charge_limit",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0,
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
) -> Generator[SensorEntity]:
    """Generate Enode sensors."""
    yield from _generate_vehicle_sensors(coordinator.vehicles)


def _generate_vehicle_sensors(
    coordinator: EnodeVehiclesCoordinator,
) -> Generator[SensorEntity]:
    """Generate sensors for vehicles."""
    for vehicle in coordinator.data or []:
        LOGGER.debug("Generating sensors for vehicle %s", vehicle.id)
        if vehicle.capabilities.charge_state.is_capable:
            LOGGER.debug("Vehicle %s supports charge state", vehicle.id)
            for description in CHARGE_STATE_DESCRIPTIONS:
                yield VehicleChargeStateSensor(
                    coordinator=coordinator, vehicle=vehicle, description=description
                )
        if vehicle.capabilities.odometer.is_capable:
            LOGGER.debug("Vehicle %s supports odometer", vehicle.id)
            for description in ODOMETER_DESCRIPTIONS:
                yield VehicleOdometerSensor(
                    coordinator=coordinator, vehicle=vehicle, description=description
                )
        if vehicle.capabilities.smart_charging.is_capable:
            LOGGER.debug("Vehicle %s supports smart charging", vehicle.id)
            for description in SMART_CHARGING_DESCRIPTIONS:
                yield VehicleSmartChargingSensor(
                    coordinator=coordinator, vehicle=vehicle, description=description
                )


class VehicleSensor(VehicleEntity[EnodeVehiclesCoordinator], SensorEntity):
    """Sensor for vehicle data."""

    @property
    def last_reset(self) -> datetime | None:
        """Return if the sensor supports last reset."""
        if self.entity_description.state_class == SensorStateClass.TOTAL:
            return self._last_reset
        return None

    @property
    def _last_reset(self) -> datetime | None:
        """Return the last reset time."""
        if vehicle := self.vehicle:
            return vehicle.last_seen
        return None

    @property
    @abstractmethod
    def native_value(self) -> Any:
        """Return the value of the sensor."""


class VehicleChargeStateSensor(VehicleSensor):
    """Sensor for vehicle charge state."""

    @property
    def charge_state(self) -> ChargeState | None:
        """Return the charge state."""
        if vehicle := self.vehicle:
            return vehicle.charge_state
        return None

    @property
    def _last_reset(self) -> datetime | None:
        """Return the last reset time."""
        if charge_state := self.charge_state:
            return charge_state.last_updated
        return None

    @property
    def native_value(self) -> int | float | str | None:
        """Return the value of the sensor."""
        if charge_state := self.charge_state:
            return getattr(charge_state, self.entity_description.key)
        return None


class VehicleOdometerSensor(VehicleSensor):
    """Sensor for vehicle odometer."""

    @property
    def _last_reset(self) -> datetime | None:
        """Return the last reset time."""
        if vehicle := self.vehicle:
            return vehicle.odometer.last_updated
        return None

    @property
    def native_value(self) -> float | None:
        """Return the value of the sensor."""
        if vehicle := self.vehicle:
            return getattr(vehicle.odometer, self.entity_description.key)
        return None


class VehicleSmartChargingSensor(VehicleSensor):
    """Sensor for vehicle smart charging."""

    @property
    def native_value(self) -> float | time | None:
        """Return the value of the sensor."""
        if vehicle := self.vehicle:
            return getattr(vehicle.smart_charging_policy, self.entity_description.key)
        return None
