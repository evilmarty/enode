"""Tests for Enode sensors."""

from unittest.mock import MagicMock

import pytest

from custom_components.enode.models import Vehicle
from custom_components.enode.sensor import (
    VehicleChargeStateSensor,
    VehicleOdometerSensor,
    VehicleSmartChargingSensor,
)
from homeassistant.components.sensor import SensorEntityDescription, SensorStateClass


class TestVehicleChargeStateSensor:
    """Test VehicleChargeStateSensor class."""

    @pytest.fixture
    def description(self):
        """Sensor description."""
        return SensorEntityDescription(
            key="battery_level", state_class=SensorStateClass.TOTAL
        )

    @pytest.fixture
    def coordinator(self, mock_vehicle):
        """Mock coordinator."""
        coordinator = MagicMock()
        coordinator.data = [mock_vehicle]
        return coordinator

    @pytest.fixture
    def sensor(self, coordinator, mock_vehicle, description):
        """VehicleChargeStateSensor instance."""
        return VehicleChargeStateSensor(
            coordinator, mock_vehicle, description=description
        )

    def test_last_reset_with_total_state_class(self, sensor, mock_vehicle):
        """Test last_reset property with TOTAL state class."""
        assert sensor.last_reset == mock_vehicle.last_seen

    def test_last_reset_without_total_state_class(self, sensor):
        """Test last_reset property without TOTAL state class."""
        sensor.entity_description = SensorEntityDescription(
            key="battery_level", state_class=SensorStateClass.MEASUREMENT
        )
        assert sensor.last_reset is None

    def test_last_reset_no_vehicle(self, sensor, coordinator):
        """Test last_reset when vehicle is None."""
        coordinator.data = []
        assert sensor.last_reset is None

    def test_charge_state(self, sensor, mock_vehicle):
        """Test charge_state property."""
        assert sensor.charge_state == mock_vehicle.charge_state

    def test_native_value(self, sensor):
        """Test native_value property."""
        assert sensor.native_value == 50.0

    def test_native_value_missing(self, coordinator, mock_vehicle, description):
        """Test native_value when value is None."""
        mock_vehicle.charge_state.battery_level = None
        sensor = VehicleChargeStateSensor(
            coordinator, mock_vehicle, description=description
        )
        assert sensor.native_value is None

    def test_native_value_no_vehicle(self, mock_vehicle, description):
        """Test native_value when vehicle is None."""
        coordinator = MagicMock()
        coordinator.data = []
        sensor = VehicleChargeStateSensor(
            coordinator, mock_vehicle, description=description
        )
        assert sensor.native_value is None


class TestVehicleOdometerSensor:
    """Test VehicleOdometerSensor class."""

    @pytest.fixture
    def description(self):
        """Sensor description."""
        return SensorEntityDescription(key="distance")

    @pytest.fixture
    def coordinator(self, mock_vehicle):
        """Mock coordinator."""
        coordinator = MagicMock()
        coordinator.data = [mock_vehicle]
        return coordinator

    @pytest.fixture
    def sensor(self, coordinator, mock_vehicle, description):
        """VehicleOdometerSensor instance."""
        return VehicleOdometerSensor(coordinator, mock_vehicle, description=description)

    def test_native_value(self, sensor):
        """Test native_value property."""
        assert sensor.native_value == 10000.0

    def test_last_reset(self, sensor, mock_vehicle):
        """Test _last_reset property."""
        assert sensor._last_reset == mock_vehicle.odometer.last_updated  # noqa: SLF001

    def test_native_value_missing(self, coordinator, mock_vehicle, description):
        """Test native_value when value is None."""
        mock_vehicle.odometer.distance = None
        sensor = VehicleOdometerSensor(
            coordinator, mock_vehicle, description=description
        )
        assert sensor.native_value is None

    def test_native_value_no_vehicle(self, mock_vehicle, description):
        """Test native_value when vehicle is None."""
        coordinator = MagicMock()
        coordinator.data = []
        sensor = VehicleOdometerSensor(
            coordinator, mock_vehicle, description=description
        )
        assert sensor.native_value is None


class TestVehicleSmartChargingSensor:
    """Test VehicleSmartChargingSensor class."""

    @pytest.fixture
    def description(self):
        """Sensor description."""
        return SensorEntityDescription(key="minimum_charge_limit")

    def test_native_value(self, mock_vehicle_data, description):
        """Test VehicleSmartChargingSensor native_value."""
        mock_vehicle_data["smartChargingPolicy"] = {
            "deadline": "08:00:00",
            "isEnabled": True,
            "minimumChargeLimit": 20.0,
        }
        vehicle = Vehicle.model_validate(mock_vehicle_data)

        coordinator = MagicMock()
        coordinator.data = [vehicle]
        sensor = VehicleSmartChargingSensor(
            coordinator, vehicle, description=description
        )
        assert sensor.native_value == 20.0

    def test_native_value_missing_policy(self, mock_vehicle, description):
        """Test native_value when smart_charging_policy is None."""
        coordinator = MagicMock()
        coordinator.data = [mock_vehicle]
        mock_vehicle.smart_charging_policy = None
        sensor = VehicleSmartChargingSensor(
            coordinator, mock_vehicle, description=description
        )
        with pytest.raises(AttributeError):
            _ = sensor.native_value

    def test_native_value_no_vehicle(self, mock_vehicle, description):
        """Test native_value when vehicle is None."""
        coordinator = MagicMock()
        coordinator.data = []
        sensor = VehicleSmartChargingSensor(
            coordinator, mock_vehicle, description=description
        )
        assert sensor.native_value is None
