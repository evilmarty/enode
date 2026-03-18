"""Fixtures for Enode tests."""

from unittest.mock import MagicMock, patch

import pytest

from custom_components.enode.models import Vehicle
from homeassistant.core import HomeAssistant


@pytest.fixture
def mock_vehicle_data():
    """Return mock vehicle data."""
    return {
        "id": "v1",
        "userId": "u1",
        "vendor": "Tesla",
        "isReachable": True,
        "lastSeen": "2023-01-01T00:00:00Z",
        "information": {
            "displayName": "My Tesla",
            "vin": "123",
            "brand": "Tesla",
            "model": "Model 3",
            "year": 2022,
        },
        "chargeState": {
            "chargeMode": 10.0,
            "chargeTimeRemaining": 60,
            "isFullyCharged": False,
            "isPluggedIn": True,
            "isCharging": True,
            "batteryLevel": 50.0,
            "range": 200.0,
            "batteryCapacity": 75.0,
            "chargeLimit": 80.0,
            "lastUpdated": "2023-01-01T00:00:00Z",
            "powerDeliveryState": "PLUGGED_IN:CHARGING",
            "maxCurrent": 32.0,
        },
        "location": {
            "id": "l1",
            "latitude": 59.3293,
            "longitude": 18.0686,
            "lastUpdated": "2023-01-01T00:00:00Z",
        },
        "odometer": {"distance": 10000.0, "lastUpdated": "2023-01-01T00:00:00Z"},
        "capabilities": {
            "information": {"isCapable": True, "interventionIds": []},
            "chargeState": {"isCapable": True, "interventionIds": []},
            "location": {"isCapable": True, "interventionIds": []},
            "odometer": {"isCapable": True, "interventionIds": []},
            "setMaxCurrent": {"isCapable": True, "interventionIds": []},
            "startCharging": {"isCapable": True, "interventionIds": []},
            "stopCharging": {"isCapable": True, "interventionIds": []},
            "smartCharging": {"isCapable": True, "interventionIds": []},
        },
        "scopes": ["vehicle:read:data"],
    }


@pytest.fixture
def hass():
    """Mock Home Assistant."""
    hass = MagicMock(spec=HomeAssistant)
    hass.config = MagicMock(language="en")
    hass.data = {}
    hass.config_entries = MagicMock()
    return hass


@pytest.fixture
def mock_enode_client():
    """Mock Enode client."""
    with patch("custom_components.enode.api.EnodeClient", autospec=True) as mock:
        yield mock.return_value


@pytest.fixture
def mock_vehicle(mock_vehicle_data):
    """Return a real Vehicle model instance."""
    return Vehicle.model_validate(mock_vehicle_data)
