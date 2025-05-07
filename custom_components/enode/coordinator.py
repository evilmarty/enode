"""Coordinator for various Enode entities."""

from aiohttp import ClientResponseError

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import EnodeClient
from .const import CONF_USER_ID, LOGGER, UPDATE_INTERVAL
from .models import Vehicle

type EnodeConfigEntry = ConfigEntry[EnodeCoordinators]
type EnodeVehiclesCoordinator = DataUpdateCoordinator[list[Vehicle]]


class EnodeCoordinators:
    """Base coordinator for Enode."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: EnodeClient,
        config_entry: ConfigEntry | None = None,
    ) -> None:
        """Initialize Enode Coordinator."""
        self.client = client
        self.user_id = config_entry.data.get(CONF_USER_ID) if config_entry else None
        self.vehicles = DataUpdateCoordinator[list[Vehicle]](
            hass=hass,
            logger=LOGGER,
            config_entry=config_entry,
            name="vehicles",
            update_method=self._update_vehicles,
            update_interval=UPDATE_INTERVAL,
        )

    async def _update_vehicles(self) -> list[Vehicle]:
        """Update vehicles data."""
        try:
            if self.user_id is None:
                return await self.client.list_vehicles()
            return await self.client.list_user_vehicles(self.user_id)
        except ClientResponseError as err:
            raise UpdateFailed from err

    async def async_refresh(self) -> None:
        """Refresh data and log errors."""
        await self.vehicles.async_refresh()

    async def async_config_entry_first_refresh(self) -> None:
        """Refresh data for the first time."""
        await self.vehicles.async_config_entry_first_refresh()
