"""Tests for Enode switches."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.enode.coordinator import EnodeCoordinators
from custom_components.enode.switch import VehicleChargeSwitch, async_setup_entry


@pytest.mark.asyncio
async def test_switch_setup(hass, mock_vehicle):
    """Test switch setup."""
    entry = MagicMock()
    entry.entry_id = "test_entry"

    client = MagicMock()
    coordinators = MagicMock(spec=EnodeCoordinators)
    coordinators.client = client
    coordinators.vehicles = MagicMock()
    coordinators.vehicles.data = [mock_vehicle]
    entry.runtime_data = coordinators

    async_add_entities = MagicMock()

    await async_setup_entry(hass, entry, async_add_entities)

    assert async_add_entities.called
    entities = list(async_add_entities.call_args[0][0])
    assert len(entities) == 1

    switch = entities[0]
    assert isinstance(switch, VehicleChargeSwitch)
    assert switch.is_on is True

@pytest.mark.asyncio
async def test_switch_turn_on(hass, mock_vehicle):
    """Test switch turn on."""
    client = MagicMock()
    client.control_charging = AsyncMock()

    coordinator = SimpleNamespace(data=[mock_vehicle])

    switch = VehicleChargeSwitch(coordinator=coordinator, vehicle=mock_vehicle, client=client)
    switch.hass = hass

    await switch.async_turn_on()

    client.control_charging.assert_called_once_with(vehicle_id="v1", action="START")

@pytest.mark.asyncio
async def test_switch_turn_off(hass, mock_vehicle):
    """Test switch turn off."""
    client = MagicMock()
    client.control_charging = AsyncMock()

    coordinator = SimpleNamespace(data=[mock_vehicle])

    switch = VehicleChargeSwitch(coordinator=coordinator, vehicle=mock_vehicle, client=client)
    switch.hass = hass

    await switch.async_turn_off()

    client.control_charging.assert_called_once_with(vehicle_id="v1", action="STOP")
