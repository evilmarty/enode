"""Tests for Enode coordinator."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.enode.coordinator import EnodeCoordinators
from custom_components.enode.models import Vehicle


class TestEnodeCoordinators:
    """Test EnodeCoordinators class."""

    @pytest.mark.asyncio
    async def test_fetch_vehicles(self, hass, mock_enode_client, mock_vehicle):
        """Test fetching vehicles in the coordinator."""
        mock_enode_client.list_user_vehicles = AsyncMock(return_value=[mock_vehicle])

        config_entry = MagicMock()
        config_entry.data = {"user_id": "test_user"}

        coordinator = EnodeCoordinators(hass, mock_enode_client, config_entry)

        vehicles = await coordinator._fetch_vehicles()  # noqa: SLF001

        assert vehicles == [mock_vehicle]
        assert isinstance(vehicles[0], Vehicle)
        mock_enode_client.list_user_vehicles.assert_called_once_with("test_user")

    @pytest.mark.asyncio
    async def test_fetch_vehicles_no_user_id(
        self, hass, mock_enode_client, mock_vehicle
    ):
        """Test fetching vehicles in the coordinator when no user_id is provided."""
        mock_enode_client.list_vehicles = AsyncMock(return_value=[mock_vehicle])

        config_entry = MagicMock()
        config_entry.data = {}

        coordinator = EnodeCoordinators(hass, mock_enode_client, config_entry)

        vehicles = await coordinator._fetch_vehicles()  # noqa: SLF001

        assert vehicles == [mock_vehicle]
        assert isinstance(vehicles[0], Vehicle)
        mock_enode_client.list_vehicles.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_vehicle_data(self, hass, mock_enode_client, mock_vehicle):
        """Test update_vehicle_data method."""
        config_entry = MagicMock()
        config_entry.data = {"user_id": "test_user"}

        coordinator = EnodeCoordinators(
            hass, mock_enode_client, config_entry, use_update_interval=False
        )
        coordinator.vehicles.async_set_updated_data([mock_vehicle])

        new_vehicle_data = mock_vehicle.model_copy(update={"vendor": "NewVendor"})
        coordinator.update_vehicle_data(new_vehicle_data)

        assert coordinator.vehicles.data[0].vendor == "NewVendor"
        assert len(coordinator.vehicles.data) == 1

    @pytest.mark.asyncio
    async def test_async_shutdown(self, hass, mock_enode_client):
        """Test async_shutdown method."""
        coordinator = EnodeCoordinators(hass, mock_enode_client)
        mock_future = MagicMock()
        coordinator.test_future = mock_future

        await coordinator.async_shutdown()

        mock_future.cancel.assert_called_once()
        assert coordinator.test_future is None
