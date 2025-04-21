"""Views for the Enode integration."""

from aiohttp import web, web_response
from aiohttp.web_exceptions import HTTPBadRequest

from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import UnknownFlow

from .const import LOGGER


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
