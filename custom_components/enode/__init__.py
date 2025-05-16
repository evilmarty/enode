"""The Enode integration."""

from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .application_credentials import get_client
from .const import CONF_WEBHOOK_ID
from .coordinator import EnodeConfigEntry, EnodeCoordinators
from .views import EnodeWebhookView

_PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.GEO_LOCATION,
    Platform.SENSOR,
    Platform.SWITCH,
]


async def async_setup_entry(hass: HomeAssistant, entry: EnodeConfigEntry) -> bool:
    """Set up Enode from a config entry."""
    has_webhook = entry.data.get(CONF_WEBHOOK_ID) is not None
    if has_webhook:
        hass.http.register_view(EnodeWebhookView)
    client = await get_client(hass, entry)
    coordinators = EnodeCoordinators(hass, client)
    await coordinators.async_refresh()

    entry.runtime_data = coordinators
    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: EnodeConfigEntry) -> bool:
    """Unload a config entry."""
    await entry.runtime_data.async_shutdown()
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)


async def async_remove_entry(hass: HomeAssistant, entry: EnodeConfigEntry) -> None:
    """Handle removal of an entry."""
