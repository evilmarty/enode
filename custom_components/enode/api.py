"""API for Enode bound to Home Assistant OAuth."""

from typing import Literal

from aiohttp import ClientResponse, ClientResponseError
from aiohttp.hdrs import METH_DELETE, METH_GET, METH_POST
from yarl import URL

from homeassistant.helpers.config_entry_oauth2_flow import OAuth2Session

from .const import LOGGER, PRODUCTION_API_URL, SANDBOX_API_URL
from .models import (
    ChargeAction,
    ErrorResponse,
    Language,
    Link,
    Response,
    T,
    Vehicle,
    VendorType,
    Webhook,
    WebhookEventType,
    WebhookTestResponse,
)

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


class EnodeError(ClientResponseError):
    """Enode API error."""

    def __init__(self, response: ClientResponse, data: dict) -> None:
        """Initialize Enode error."""
        self.data = ErrorResponse.model_validate(data)
        super().__init__(
            request_info=response.request_info,
            history=response.history,
            status=response.status,
            message=f"{self.data.title}: {self.data.detail}",
            headers=response.headers,
        )


class EnodeClient:
    """Enode API client."""

    def __init__(
        self,
        oauth_session: OAuth2Session,
        sandbox: bool = False,
    ) -> None:
        """Initialize Enode auth."""
        self._oauth_session = oauth_session
        self._api_url = SANDBOX_API_URL if sandbox else PRODUCTION_API_URL

    async def _make_request(self, type_: T, method: str, path: str, **kwargs) -> T:
        """Make a request to the Enode API."""
        url = URL(self._api_url).with_path(path)
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
        is_error = response.status == 400
        if not response.ok and not is_error:
            response.raise_for_status()
        if type_ is None:
            return None
        data = await response.json()
        if is_error:
            raise EnodeError(response, data)
        return type_.model_validate(data)

    @property
    def client_id(self) -> str | None:
        """Return the client ID."""
        return getattr(self._oauth_session.implementation, "client_id", None)

    async def list_vehicles(self) -> list[Vehicle]:
        """List vehicles."""
        response = await self._make_request(
            Response[list[Vehicle]], method=METH_GET, path="/vehicles"
        )
        return response.data

    async def list_user_vehicles(self, user_id: str) -> list[Vehicle]:
        """List vehicles."""
        response = await self._make_request(
            Response[list[Vehicle]],
            method=METH_GET,
            path=f"/users/{user_id}/vehicles",
        )
        return response.data

    async def user_link(
        self,
        user_id: str,
        redirect_uri: str | URL,
        language: Language = Language.BROWSER,
        vendor: str | None = None,
        vendor_type: VendorType | None = None,
    ) -> Link:
        """Link a device to a user."""
        if vendor_type is None:
            scopes = SCOPES
        else:
            scopes = [s for s in SCOPES if s.startswith(f"{vendor_type.value}:")]
        data = {
            "language": language.value,
            "redirectUri": str(redirect_uri),
            "scopes": scopes,
        }
        if vendor:
            data["vendor"] = vendor
        if vendor_type:
            data["vendorType"] = vendor_type.value
        return await self._make_request(
            Link,
            method=METH_POST,
            path=f"/users/{user_id}/link",
            json=data,
        )

    async def control_charging(
        self, vehicle_id: str, action: Literal["START", "STOP"]
    ) -> None:
        """Control charging for a vehicle."""
        data = {
            "action": action,
        }
        await self._make_request(
            ChargeAction,
            method=METH_POST,
            path=f"/vehicles/{vehicle_id}/charging",
            json=data,
        )

    async def create_webhook(
        self,
        url: str | URL,
        secret: str,
        events: list[WebhookEventType] | None = None,
        api_version: str | None = None,
    ) -> Webhook:
        """Create a webhook."""
        if events is None:
            events = ["*"]
        data = {
            "url": str(url),
            "secret": secret,
            "events": events,
        }
        if api_version:
            data["apiVersion"] = api_version
        return await self._make_request(
            Webhook,
            method=METH_POST,
            path="/webhooks",
            json=data,
        )

    async def delete_webhook(self, webhook: str | Webhook) -> None:
        """Delete a webhook."""
        if isinstance(webhook, Webhook):
            webhook = webhook.id
        await self._make_request(
            None,
            method=METH_DELETE,
            path=f"/webhooks/{webhook}",
        )

    async def test_webhook(self, webhook: str | Webhook) -> WebhookTestResponse:
        """Test a webhook."""
        if isinstance(webhook, Webhook):
            webhook = webhook.id
        await self._make_request(
            WebhookTestResponse,
            method=METH_POST,
            path=f"/webhooks/{webhook}/test",
        )
