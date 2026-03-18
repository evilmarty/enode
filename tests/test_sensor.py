"""Tests for Enode sensors."""

from unittest.mock import MagicMock

import pytest

from custom_components.enode.coordinator import EnodeCoordinators
from custom_components.enode.models import Vehicle
from custom_components.enode.sensor import VehicleChargeStateSensor, async_setup_entry


@pytest.mark.asyncio
async def test_sensor_setup(hass, mock_vehicle):
    """Test sensor setup."""
    entry = MagicMock()
    entry.entry_id = "test_entry"

    coordinators = MagicMock(spec=EnodeCoordinators)
    coordinators.vehicles = MagicMock()
    coordinators.vehicles.data = [mock_vehicle]
    entry.runtime_data = coordinators

    async_add_entities = MagicMock()

    await async_setup_entry(hass, entry, async_add_entities)

    assert async_add_entities.called
    entities = list(async_add_entities.call_args[0][0])
    assert len(entities) > 0

    # Check if we have some sensors
    charge_sensors = [e for e in entities if isinstance(e, VehicleChargeStateSensor)]
    assert len(charge_sensors) > 0

    battery_sensor = next((e for e in charge_sensors if e.entity_description.key == "battery_level"), None)
    assert battery_sensor is not None
    assert isinstance(battery_sensor.vehicle, Vehicle)
    assert battery_sensor.native_value == 50.0
