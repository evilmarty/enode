"""Tests for Enode API client."""

from unittest.mock import AsyncMock, MagicMock

from aiohttp import ClientResponse
import pytest

from custom_components.enode.api import EnodeClient
from custom_components.enode.models import Vehicle


@pytest.fixture
def mock_oauth_session():
    """Mock OAuth2Session."""
    session = MagicMock()
    session.async_request = AsyncMock()
    return session

@pytest.mark.asyncio
async def test_list_vehicles(mock_oauth_session, mock_vehicle_data):
    """Test listing vehicles."""
    client = EnodeClient(mock_oauth_session)

    mock_response = AsyncMock(spec=ClientResponse)
    mock_response.status = 200
    mock_response.ok = True
    mock_response.json = AsyncMock(return_value={
        "data": [mock_vehicle_data],
        "pagination": {"before": None, "after": None}
    })

    mock_oauth_session.async_request.return_value = mock_response

    vehicles = await client.list_vehicles()

    assert len(vehicles) == 1
    assert isinstance(vehicles[0], Vehicle)
    assert vehicles[0].id == "v1"
    assert vehicles[0].vendor == "Tesla"

    mock_oauth_session.async_request.assert_called_once()
    args, kwargs = mock_oauth_session.async_request.call_args
    assert kwargs["method"] == "GET"
    assert "/vehicles" in str(kwargs["url"])

@pytest.mark.asyncio
async def test_refresh_vehicle_data(mock_oauth_session):
    """Test refreshing vehicle data."""
    client = EnodeClient(mock_oauth_session)

    mock_response = AsyncMock(spec=ClientResponse)
    mock_response.status = 204
    mock_response.ok = True

    mock_oauth_session.async_request.return_value = mock_response

    await client.refresh_vehicle_data("v1")

    mock_oauth_session.async_request.assert_called_once()
    args, kwargs = mock_oauth_session.async_request.call_args
    assert kwargs["method"] == "POST"
    assert "/vehicles/v1/refresh-hint" in str(kwargs["url"])
