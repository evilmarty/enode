"""Application credentials platform for the Enode integration."""

from json import JSONDecodeError
from typing import Any, cast

from aiohttp import BasicAuth, ClientError

from homeassistant.components.application_credentials import ClientCredential
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.config_entry_oauth2_flow import (
    AbstractOAuth2Implementation,
    LocalOAuth2Implementation,
)

from .const import LOGGER, OAUTH2_AUTHORIZE, OAUTH2_TOKEN


class Oauth2Impl(LocalOAuth2Implementation):
    """OAuth2 implementation for Enode."""

    @property
    def name(self) -> str:
        """Return the name of the OAuth2 implementation."""
        return "Enode"

    async def async_generate_authorize_url(self, flow_id: str) -> str:
        """Redirect back to HA because there is no authorization URL."""
        return self.redirect_uri

    async def async_resolve_external_data(self, external_data: Any) -> dict:
        """Resolve the authorization code to tokens."""
        request_data: dict = {
            "grant_type": "client_credentials",
        }
        request_data.update(self.extra_token_resolve_data)
        return await self._token_request(request_data)

    async def _async_refresh_token(self, token: dict) -> dict:
        """Refresh the token by just repeating the authorize step."""
        return await self.async_resolve_external_data({})

    async def _token_request(self, data: dict) -> dict:
        """Make a token request using basic auth."""
        session = async_get_clientsession(self.hass)

        auth = BasicAuth(self.client_id, self.client_secret)

        LOGGER.debug("Sending token request to %s", self.token_url)
        resp = await session.post(self.token_url, auth=auth, data=data)
        if resp.status >= 400:
            try:
                error_response = await resp.json()
            except (ClientError, JSONDecodeError):
                error_response = {}
            error_code = error_response.get("error", "unknown")
            error_description = error_response.get("error_description", "unknown error")
            LOGGER.error(
                "Token request for %s failed (%s): %s",
                self.domain,
                error_code,
                error_description,
            )
        resp.raise_for_status()
        return cast(dict, await resp.json())


async def async_get_auth_implementation(
    hass: HomeAssistant, auth_domain: str, credential: ClientCredential
) -> AbstractOAuth2Implementation:
    """Return the OAuth2 implementation for Enode."""
    return Oauth2Impl(
        hass=hass,
        domain=auth_domain,
        client_id=credential.client_id,
        client_secret=credential.client_secret,
        authorize_url=OAUTH2_AUTHORIZE,
        token_url=OAUTH2_TOKEN,
    )
