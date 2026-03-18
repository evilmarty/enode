"""Tests for Enode switches."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.enode.switch import VehicleChargeSwitch


class TestVehicleChargeSwitch:
    """Test VehicleChargeSwitch class."""

    def test_is_on(self, mock_vehicle):
        """Test is_on property."""
        coordinator = MagicMock()
        coordinator.data = [mock_vehicle]
        client = MagicMock()
        switch = VehicleChargeSwitch(coordinator, mock_vehicle, client=client)

        assert switch.is_on is True

        mock_vehicle.charge_state.is_charging = False
        assert switch.is_on is False

    def test_is_on_missing(self, mock_vehicle):
        """Test is_on when is_charging is None."""
        coordinator = MagicMock()
        coordinator.data = [mock_vehicle]
        mock_vehicle.charge_state.is_charging = None
        client = MagicMock()
        switch = VehicleChargeSwitch(coordinator, mock_vehicle, client=client)

        assert switch.is_on is None

    def test_is_on_no_vehicle(self, mock_vehicle):
        """Test is_on when vehicle is None."""
        coordinator = MagicMock()
        coordinator.data = []
        client = MagicMock()
        switch = VehicleChargeSwitch(coordinator, mock_vehicle, client=client)

        assert switch.is_on is None

    @pytest.mark.asyncio
    async def test_async_turn_on(self, mock_vehicle):
        """Test async_turn_on."""
        coordinator = MagicMock()
        coordinator.data = [mock_vehicle]
        client = MagicMock()
        client.control_charging = AsyncMock()
        switch = VehicleChargeSwitch(coordinator, mock_vehicle, client=client)

        await switch.async_turn_on()
        client.control_charging.assert_called_once_with(
            vehicle_id=mock_vehicle.id, action="START"
        )

    @pytest.mark.asyncio
    async def test_async_turn_off(self, mock_vehicle):
        """Test async_turn_off."""
        coordinator = MagicMock()
        coordinator.data = [mock_vehicle]
        client = MagicMock()
        client.control_charging = AsyncMock()
        switch = VehicleChargeSwitch(coordinator, mock_vehicle, client=client)

        await switch.async_turn_off()
        client.control_charging.assert_called_once_with(
            vehicle_id=mock_vehicle.id, action="STOP"
        )

    @pytest.mark.asyncio
    async def test_async_turn_on_not_capable(self, mock_vehicle):
        """Test async_turn_on when not capable."""
        mock_vehicle.capabilities.start_charging.is_capable = False
        coordinator = MagicMock()
        coordinator.data = [mock_vehicle]
        client = MagicMock()
        client.control_charging = AsyncMock()
        switch = VehicleChargeSwitch(coordinator, mock_vehicle, client=client)

        await switch.async_turn_on()
        client.control_charging.assert_not_called()
