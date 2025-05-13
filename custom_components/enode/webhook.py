"""Webhook handling for Enode integration."""

import asyncio

from homeassistant.core import HomeAssistant

from .const import LOGGER
from .coordinator import EnodeConfigEntry
from .models import WebhookEvents, WebhookTestEvent, WebhookUserVehicleUpdatedEvent


async def _complete_test_webhook(
    entry: EnodeConfigEntry, event: WebhookTestEvent
) -> None:
    """Handle test webhook."""
    if test_future := entry.runtime_data.test_future:
        test_future.set_result(True)
        entry.runtime_data.test_future = None


async def _user_vehicle_updated(
    entry: EnodeConfigEntry, event: WebhookUserVehicleUpdatedEvent
) -> None:
    """Handle user vehicle updated webhook."""
    await entry.runtime_data.update_vehicle_data(event.vehicle)


EVENT_HANDLER_MAPPING = {
    WebhookTestEvent: _complete_test_webhook,
    WebhookUserVehicleUpdatedEvent: _user_vehicle_updated,
}


async def process_webhook_events(
    entry: EnodeConfigEntry, events: WebhookEvents
) -> None:
    """Process webhook events."""
    for event in events:
        if handler := EVENT_HANDLER_MAPPING.get(type(event)):
            await handler(entry, event)
        else:
            LOGGER.debug("Received unsupported webhook event: %s", event.event)


def prepare_test_webhook(
    hass: HomeAssistant, entry: EnodeConfigEntry
) -> asyncio.Future[bool]:
    """Prepare test webhook."""
    if entry.runtime_data.test_future:
        entry.runtime_data.test_future.cancel()
    entry.runtime_data.test_future = hass.loop.create_future()
    return entry.runtime_data.test_future
