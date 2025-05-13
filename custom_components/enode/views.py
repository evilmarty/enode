"""Views for the Enode integration."""

import asyncio
from hashlib import sha1
import hmac

from aiohttp import web, web_exceptions, web_response
from aiohttp.web_exceptions import HTTPBadRequest

from homeassistant.components.http import HomeAssistantView
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import UnknownFlow

from .const import CONF_WEBHOOK_SECRET, DOMAIN, HEADER_SIGNATURE, LOGGER
from .models import WebhookEvents
from .webhook import process_webhook_events


class ConfigFlowExternalCallbackView(HomeAssistantView):
    """Handle external step callbacks."""

    requires_auth = False
    url = "/api/enode/done"
    name = "api:enode:configflow_done"

    async def get(self, request: web.Request) -> None:
        """Handle GET requests."""
        hass: HomeAssistant = request.app["hass"]
        try:
            await hass.config_entries.subentries.async_configure(
                flow_id=request.query["flow_id"],
                user_input=request.query,
            )
        except (KeyError, UnknownFlow) as ex:
            LOGGER.debug("Callback flow_id is invalid")
            raise HTTPBadRequest from ex
        return web_response.Response(
            headers={"content-type": "text/html"},
            text="<script>window.close()</script>Success! This window can be closed",
        )


class EnodeWebhookView(HomeAssistantView):
    """Handle Enode webhooks."""

    requires_auth = False
    url = "/api/enode/webhook"
    name = "api:enode:webhook"

    test_future: asyncio.Future[bool] | None = None

    async def post(self, request: web.Request) -> None:
        """Handle POST requests."""
        hass: HomeAssistant = request.app["hass"]
        try:
            signature = request.headers[HEADER_SIGNATURE]
            content = await request.read()
            LOGGER.debug("Received webhook data: %s", content)
            entry = await self.find_entry_by_signature(hass, signature, content)
            webhook_events = WebhookEvents.model_validate_json(content)
            await process_webhook_events(entry, webhook_events)
        except KeyError:
            LOGGER.debug("Signature header is missing")
            return web_exceptions.HTTPBadRequest(reason="Signature header is missing")
        return web_response.Response(
            status=200,
            text="Webhook received",
        )

    @staticmethod
    def find_entry_by_signature(
        hass: HomeAssistant, signature: str, content: bytes
    ) -> ConfigEntry | None:
        """Find the entry by signature."""
        _, value = signature.split("=", 1)
        raw_value = value.encode("utf-8")
        entries = hass.config_entries.async_entries(
            domain=DOMAIN, include_disabled=False, include_ignore=False
        )
        for entry in entries:
            secret: str | None = entry.data.get(CONF_WEBHOOK_SECRET)
            if not secret:
                continue
            digest = hmac.new(secret.encode("utf-8"), content, sha1).digest()
            if hmac.compare_digest(digest, raw_value):
                LOGGER.debug("Found matching entry for webhook")
                return entry
        LOGGER.debug("No matching entry found for webhook")
        return None
