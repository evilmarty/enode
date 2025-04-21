"""Coordinator for various Enode entities."""

from aiohttp import ClientResponseError

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import EnodeClient
from .const import DATA_USER_ID, LOGGER, UPDATE_INTERVAL
from .models import Vehicle


class EnodeVehiclesCoordinator(DataUpdateCoordinator[list[Vehicle]]):
    """Coordinator for fetching Enode vehicles."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: EnodeClient,
        config_entry: ConfigEntry | None = None,
    ) -> None:
        """Initialize Enode Vehicles Coordinator."""
        super().__init__(
            hass,
            LOGGER,
            config_entry=config_entry,
            name=type(self).__name__,
            update_interval=UPDATE_INTERVAL,
        )
        self.client = client
        self.user_id = config_entry.data.get(DATA_USER_ID) if config_entry else None

    async def _async_update_data(self) -> list[Vehicle]:
        """Fetch data from Enode API."""
        try:
            if self.user_id is None:
                return await self.client.list_vehicles()
            return await self.client.list_user_vehicles(self.user_id)
        except ClientResponseError as err:
            raise UpdateFailed from err


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
        self.vehicles = EnodeVehiclesCoordinator(hass, client, config_entry)

    async def async_config_entry_first_refresh(self) -> None:
        """Refresh data for the first time."""
        await self.vehicles.async_config_entry_first_refresh()


type EnodeConfigEntry = ConfigEntry[EnodeCoordinators]
