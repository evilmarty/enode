"""Views for the Enode integration."""

import asyncio
from hashlib import sha1
import hmac

from aiohttp import web, web_response
from aiohttp.web_exceptions import HTTPBadRequest, HTTPNotFound

from homeassistant.components.http import HomeAssistantView
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import UnknownFlow

from .const import CONF_WEBHOOK_SECRET, DOMAIN, LOGGER
from .models import WebhookEvents
from .webhook import process_webhook_events

HEADER_SIGNATURE = "X-Enode-Signature"
QUERY_FLOW_ID = "flow_id"
QUERY_ENTRY_ID = "entry_id"


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
                flow_id=request.query[QUERY_FLOW_ID],
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
        LOGGER.debug(
            "Received webhook request with content length %d", request.content_length
        )
        try:
            entry = hass.config_entries.async_get_entry(request.query[QUERY_ENTRY_ID])
            if entry is None:
                LOGGER.debug("Entry ID is invalid")
                raise HTTPNotFound(reason="Entry ID not found")
        except KeyError as ex:
            LOGGER.debug("Entry ID is missing")
            raise HTTPBadRequest from ex
        try:
            request_signature = request.headers[HEADER_SIGNATURE]
        except KeyError as ex:
            LOGGER.debug("Signature header is missing")
            raise HTTPBadRequest from ex
        content = await request.read()
        LOGGER.debug("Received webhook data: %s", content)
        entry_signature = self.get_signature(entry, content)
        if not hmac.compare_digest(request_signature, entry_signature):
            LOGGER.debug("Signature does not match")
            raise HTTPBadRequest(reason="Signature does not match")
        webhook_events = WebhookEvents.model_validate_json(content)
        entry.async_create_background_task(
            hass=hass,
            target=process_webhook_events(entry, webhook_events),
            name="enode_webhook",
        )
        return web_response.Response(
            status=200,
            text="Webhook events received",
        )

    @staticmethod
    def get_signature(entry: ConfigEntry, content: bytes) -> str | None:
        """Get the signature for the webhook."""
        if secret := entry.data.get(CONF_WEBHOOK_SECRET):
            digest = hmac.new(secret.encode("utf-8"), content, sha1).hexdigest()
            return f"sha1={digest}"
        return None
