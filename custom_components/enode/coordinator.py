"""Coordinator for various Enode entities."""

import asyncio

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

    test_future: asyncio.Future[bool] | None = None

    def __init__(
        self,
        hass: HomeAssistant,
        client: EnodeClient,
        config_entry: ConfigEntry | None = None,
        use_update_interval: bool = True,
    ) -> None:
        """Initialize Enode Coordinator."""
        self.client = client
        self.user_id = config_entry.data.get(CONF_USER_ID) if config_entry else None
        self.vehicles = DataUpdateCoordinator[list[Vehicle]](
            hass=hass,
            logger=LOGGER,
            config_entry=config_entry,
            name="vehicles",
            update_method=self._fetch_vehicles,
            update_interval=UPDATE_INTERVAL if use_update_interval else None,
        )

    async def _fetch_vehicles(self) -> list[Vehicle]:
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

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator."""
        if self.test_future:
            self.test_future.cancel()
            self.test_future = None

    def update_vehicle_data(self, vehicle: Vehicle) -> None:
        """Update vehicle data."""
        self.vehicles.async_set_updated_data(
            [v for v in self.vehicles.data if v.id != vehicle.id] + [vehicle]
        )
