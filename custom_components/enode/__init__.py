"""The Enode integration."""

from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.config_entry_oauth2_flow import (
    OAuth2Session,
    async_get_config_entry_implementation,
)
from homeassistant.helpers.storage import Store

from .api import EnodeClient
from .const import DATA_COORDINATORS, DATA_STORE, DOMAIN, STORAGE_KEY, STORAGE_VERSION
from .coordinator import EnodeConfigEntry, EnodeCoordinators

_PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.GEO_LOCATION,
    Platform.SENSOR,
]


async def async_setup_entry(hass: HomeAssistant, entry: EnodeConfigEntry) -> bool:
    """Set up Enode from a config entry."""
    data = hass.data.setdefault(DOMAIN, {})
    implementation = await async_get_config_entry_implementation(hass, entry)
    if DATA_STORE not in data:
        data[DATA_STORE] = Store(hass, STORAGE_VERSION, STORAGE_KEY)
    client = EnodeClient(OAuth2Session(hass, entry, implementation))
    if (coordinators := data.get(DATA_COORDINATORS)) is None:
        data[DATA_COORDINATORS] = coordinators = EnodeCoordinators(hass, client, entry)
        await coordinators.async_config_entry_first_refresh()

    entry.runtime_data = coordinators
    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: EnodeConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)


async def async_remove_entry(hass: HomeAssistant, entry: EnodeConfigEntry) -> None:
    """Handle removal of an entry."""
