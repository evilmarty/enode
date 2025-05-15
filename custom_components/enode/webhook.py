"""Webhook handling for Enode integration."""

import asyncio

from homeassistant.core import HomeAssistant

from .const import LOGGER
from .coordinator import EnodeConfigEntry
from .models import (
    WebhookEvents,
    WebhookSystemHeartbeatEvent,
    WebhookTestEvent,
    WebhookUserVehicleUpdatedEvent,
)


class WebhookProcessor:
    """Process webhook events."""

    def __init__(self, entry: EnodeConfigEntry) -> None:
        """Initialize the webhook processor."""
        self.entry = entry

    def handle_user_vehicle_updated(
        self, event: WebhookUserVehicleUpdatedEvent
    ) -> None:
        """Handle user vehicle updated webhook."""
        self.entry.runtime_data.update_vehicle_data(event.vehicle)

    def handle_system_heartbeat(self, event: WebhookSystemHeartbeatEvent) -> None:
        """Handle system heartbeat webhook."""
        LOGGER.debug(
            "Received system heartbeat event with %d pending events",
            event.pending_events,
        )

    def handle_enode_webhook_test(self, event: WebhookTestEvent) -> None:
        """Handle test webhook."""
        if test_future := self.entry.runtime_data.test_future:
            test_future.set_result(True)
            self.entry.runtime_data.test_future = None

    def process(self, events: WebhookEvents) -> None:
        """Process webhook events."""
        for event in events:
            handler_name = f"handle_{event.event.replace(':', '_').lower()}"
            if handler := getattr(self, handler_name, None):
                handler(event)
            else:
                LOGGER.debug("Received unsupported webhook event: %s", event.event)


async def process_webhook_events(
    entry: EnodeConfigEntry, events: WebhookEvents
) -> None:
    """Process webhook events."""
    WebhookProcessor(entry).process(events)


def prepare_test_webhook(
    hass: HomeAssistant, entry: EnodeConfigEntry
) -> asyncio.Future[bool]:
    """Prepare test webhook."""
    if entry.runtime_data.test_future:
        entry.runtime_data.test_future.cancel()
    entry.runtime_data.test_future = hass.loop.create_future()
    return entry.runtime_data.test_future
