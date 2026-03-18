"""Tests for Enode coordinator."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.enode.coordinator import EnodeCoordinators
from custom_components.enode.models import Vehicle


@pytest.mark.asyncio
async def test_coordinator_fetch_vehicles(hass, mock_enode_client, mock_vehicle):
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
async def test_coordinator_fetch_vehicles_no_user_id(
    hass, mock_enode_client, mock_vehicle
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
