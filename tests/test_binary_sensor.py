"""Tests for Enode binary sensors."""

from unittest.mock import MagicMock

import pytest

from custom_components.enode.binary_sensor import async_setup_entry
from custom_components.enode.coordinator import EnodeCoordinators


@pytest.mark.asyncio
async def test_binary_sensor_setup(hass, mock_vehicle):
    """Test binary sensor setup."""
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

    plugged_in_sensor = next((e for e in entities if e.entity_description.key == "is_plugged_in"), None)
    assert plugged_in_sensor is not None
    assert plugged_in_sensor.is_on is True

    fully_charged_sensor = next((e for e in entities if e.entity_description.key == "is_fully_charged"), None)
    assert fully_charged_sensor is not None
    assert fully_charged_sensor.is_on is False
