"""Tests for Enode binary sensors."""

from unittest.mock import MagicMock

import pytest

from custom_components.enode.binary_sensor import (
    VehicleChargeStateBinarySensor,
    VehicleSmartChargingBinarySensor,
)
from custom_components.enode.models import Vehicle
from homeassistant.components.binary_sensor import BinarySensorEntityDescription


class TestVehicleChargeStateBinarySensor:
    """Test VehicleChargeStateBinarySensor class."""

    def test_is_on(self, mock_vehicle):
        """Test is_on property."""
        coordinator = MagicMock()
        coordinator.data = [mock_vehicle]
        description = BinarySensorEntityDescription(key="is_plugged_in")
        sensor = VehicleChargeStateBinarySensor(
            coordinator, mock_vehicle, description=description
        )

        assert sensor.is_on is True

        mock_vehicle.charge_state.is_plugged_in = False
        assert sensor.is_on is False

    def test_is_on_missing(self, mock_vehicle):
        """Test is_on when value is None."""
        coordinator = MagicMock()
        coordinator.data = [mock_vehicle]
        mock_vehicle.charge_state.is_plugged_in = None
        description = BinarySensorEntityDescription(key="is_plugged_in")
        sensor = VehicleChargeStateBinarySensor(
            coordinator, mock_vehicle, description=description
        )

        assert sensor.is_on is None

    def test_is_on_no_vehicle(self, mock_vehicle):
        """Test is_on when vehicle is None."""
        coordinator = MagicMock()
        coordinator.data = []
        description = BinarySensorEntityDescription(key="is_plugged_in")
        sensor = VehicleChargeStateBinarySensor(
            coordinator, mock_vehicle, description=description
        )

        assert sensor.is_on is None


class TestVehicleSmartChargingBinarySensor:
    """Test VehicleSmartChargingBinarySensor class."""

    def test_is_on(self, mock_vehicle_data):
        """Test is_on property."""
        mock_vehicle_data["capabilities"]["smartCharging"]["isCapable"] = True
        mock_vehicle_data["smartChargingPolicy"] = {
            "deadline": "08:00:00",
            "isEnabled": True,
            "minimumChargeLimit": 20.0,
        }
        vehicle = Vehicle.model_validate(mock_vehicle_data)

        coordinator = MagicMock()
        coordinator.data = [vehicle]
        description = BinarySensorEntityDescription(key="is_enabled")
        sensor = VehicleSmartChargingBinarySensor(
            coordinator, vehicle, description=description
        )

        assert sensor.is_on is True

        vehicle.smart_charging_policy.is_enabled = False
        assert sensor.is_on is False

    def test_is_on_missing_policy(self, mock_vehicle):
        """Test is_on when smart_charging_policy is None."""
        coordinator = MagicMock()
        coordinator.data = [mock_vehicle]
        mock_vehicle.smart_charging_policy = None
        description = BinarySensorEntityDescription(key="is_enabled")
        sensor = VehicleSmartChargingBinarySensor(
            coordinator, mock_vehicle, description=description
        )

        with pytest.raises(AttributeError):
            _ = sensor.is_on

    def test_is_on_no_vehicle(self, mock_vehicle):
        """Test is_on when vehicle is None."""
        coordinator = MagicMock()
        coordinator.data = []
        description = BinarySensorEntityDescription(key="is_enabled")
        sensor = VehicleSmartChargingBinarySensor(
            coordinator, mock_vehicle, description=description
        )

        assert sensor.is_on is None
