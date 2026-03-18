"""Tests for Enode entities."""

from unittest.mock import MagicMock

from custom_components.enode.entity import VehicleEntity
from homeassistant.helpers.entity import EntityDescription


class TestVehicleEntity:
    """Test VehicleEntity class."""

    def test_init(self, mock_vehicle):
        """Test initialization."""
        coordinator = MagicMock()
        description = EntityDescription(key="test")
        entity = VehicleEntity(coordinator, mock_vehicle, description=description)

        assert entity.vehicle_id == mock_vehicle.id
        assert entity.unique_id == f"vehicle_{mock_vehicle.id}_test"
        assert entity.extra_state_attributes["vehicle_id"] == mock_vehicle.id
        assert entity.extra_state_attributes["user_id"] == mock_vehicle.user_id

    def test_vehicle_property(self, mock_vehicle):
        """Test vehicle property."""
        coordinator = MagicMock()
        coordinator.data = [mock_vehicle]
        entity = VehicleEntity(
            coordinator, mock_vehicle, description=EntityDescription(key="test")
        )

        assert entity.vehicle == mock_vehicle

        # Test when not in coordinator data
        coordinator.data = []
        assert entity.vehicle is None

    def test_available(self, mock_vehicle):
        """Test available property."""
        coordinator = MagicMock()
        coordinator.data = [mock_vehicle]
        entity = VehicleEntity(
            coordinator, mock_vehicle, description=EntityDescription(key="test")
        )

        assert entity.available is True

        mock_vehicle.is_reachable = False
        assert entity.available is False

        coordinator.data = []
        assert entity.available is False
