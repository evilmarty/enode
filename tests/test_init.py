"""Tests for Enode integration."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.enode import async_setup_entry, async_unload_entry
from custom_components.enode.coordinator import EnodeConfigEntry


@pytest.mark.asyncio
async def test_setup_unload_entry(hass):
    """Test setting up and unloading the entry."""
    entry = MagicMock(spec=EnodeConfigEntry)
    entry.data = {"user_id": "test_user"}
    entry.runtime_data = None
    entry.entry_id = "test_entry"

    hass.config_entries.async_forward_entry_setups = AsyncMock()
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)

    with (
        patch("custom_components.enode.get_client", new_callable=AsyncMock),
        patch(
            "custom_components.enode.EnodeCoordinators", autospec=True
        ) as mock_coordinators_class,
    ):
        mock_coordinators = mock_coordinators_class.return_value
        mock_coordinators.async_refresh = AsyncMock()
        mock_coordinators.async_shutdown = AsyncMock()

        # Setup
        assert await async_setup_entry(hass, entry) is True
        assert entry.runtime_data == mock_coordinators

        # Unload
        assert await async_unload_entry(hass, entry) is True
        mock_coordinators.async_shutdown.assert_called_once()
