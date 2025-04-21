"""API for Enode bound to Home Assistant OAuth."""

from aiohttp.hdrs import METH_GET, METH_POST
from yarl import URL

from homeassistant.helpers import config_entry_oauth2_flow

from .const import API_URL, LOGGER
from .models import Link, Response, T, Vehicle

SCOPES = [
    "battery:control:operation_mode",
    "battery:read:location",
    "battery:read:data",
    "charger:control:charging",
    "charger:read:data",
    "hvac:control:mode",
    "hvac:read:data",
    "inverter:read:data",
    "inverter:read:location",
    "meter:read:location",
    "meter:read:data",
    "vehicle:control:charging",
    "vehicle:read:data",
    "vehicle:read:location",
]

LANGUAGES = [
    "da-DK",
    "de-DE",
    "en-US",
    "en-GB",
    "es-ES",
    "fi-FI",
    "fr-FR",
    "it-IT",
    "nb-NO",
    "nl-NL",
    "nl-BE",
    "pt-PT",
    "ro-RO",
    "sv-SE",
]


class EnodeClient:
    """Enode API client."""

    def __init__(
        self,
        oauth_session: config_entry_oauth2_flow.OAuth2Session,
    ) -> None:
        """Initialize Enode auth."""
        self._oauth_session = oauth_session

    async def _make_request(
        self, type_: T, method: str, url: str, **kwargs
    ) -> Response[T]:
        """Make a request to the Enode API."""
        LOGGER.debug("Making %s request to %s", method, url)
        headers = kwargs.pop("headers", {})
        headers["Content-Type"] = "application/json"
        response = await self._oauth_session.async_request(
            method=method, url=url, headers=headers, **kwargs
        )
        LOGGER.debug(
            "Received %d response having content length of %d",
            response.status,
            response.content_length or 0,
        )
        response.raise_for_status()
        data = await response.json()
        return type_.model_validate(data)

    @property
    def client_id(self) -> str | None:
        """Return the client ID."""
        return getattr(self._oauth_session.implementation, "client_id", None)

    async def list_vehicles(self) -> list[Vehicle]:
        """List vehicles."""
        response = await self._make_request(
            Response[list[Vehicle]], METH_GET, f"{API_URL}/vehicles"
        )
        return response.data

    async def list_user_vehicles(self, user_id: str) -> list[Vehicle]:
        """List vehicles."""
        response = await self._make_request(
            Response[list[Vehicle]], METH_GET, f"{API_URL}/users/{user_id}/vehicles"
        )
        return response.data

    async def user_link(
        self,
        user_id: str,
        language: str,
        redirect_uri: str | URL,
        vendor: str | None = None,
        vendor_type: str | None = None,
    ) -> Link:
        """Link a device to a user."""
        if language not in LANGUAGES:
            language = "en-US"
        data = {
            "language": language,
            "redirectUri": str(redirect_uri),
            "scopes": SCOPES,
        }
        if vendor:
            data["vendor"] = vendor
        if vendor_type:
            data["vendorType"] = vendor_type
        return await self._make_request(
            Link,
            method=METH_POST,
            url=f"{API_URL}/users/{user_id}/link",
            json=data,
        )
