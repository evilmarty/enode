"""The Enode integration."""

from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.config_entry_oauth2_flow import (
    OAuth2Session,
    async_get_config_entry_implementation,
)

from .api import EnodeClient
from .const import CONF_SANDBOX
from .coordinator import EnodeConfigEntry, EnodeCoordinators

_PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.GEO_LOCATION,
    Platform.SENSOR,
    Platform.SWITCH,
]


async def async_setup_entry(hass: HomeAssistant, entry: EnodeConfigEntry) -> bool:
    """Set up Enode from a config entry."""
    implementation = await async_get_config_entry_implementation(hass, entry)
    sandbox = entry.data.get(CONF_SANDBOX, False)
    client = EnodeClient(OAuth2Session(hass, entry, implementation), sandbox=sandbox)
    coordinators = EnodeCoordinators(hass, client)
    await coordinators.async_refresh()

    entry.runtime_data = coordinators
    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: EnodeConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)


async def async_remove_entry(hass: HomeAssistant, entry: EnodeConfigEntry) -> None:
    """Handle removal of an entry."""
