"""Config flow for Enode."""

import logging
from typing import Any

import voluptuous as vol
from yarl import URL

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlowResult,
    ConfigSubentryFlow,
    SubentryFlowResult,
)
from homeassistant.core import callback
from homeassistant.data_entry_flow import AbortFlow
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.helpers.network import get_url

from .api import Language, VendorType
from .const import CONF_SANDBOX, CONF_USER_ID, DOMAIN, LOGGER
from .coordinator import EnodeConfigEntry
from .views import ConfigFlowExternalCallbackView


class OAuth2FlowHandler(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN
):
    """Config flow to handle Enode OAuth2 authentication."""

    DOMAIN = DOMAIN

    user_data = None

    @property
    def logger(self) -> logging.Logger:
        """Return logger."""
        return logging.getLogger(__name__)

    def _validate_user_input(self, user_input: dict[str, Any]) -> dict[str, str] | None:
        """Validate user input."""
        try:
            self._abort_if_unique_id_configured()
        except AbortFlow:
            return {"user_id": "already_configured"}
        return None

    async def async_step_auth(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Create an entry for auth."""
        if user_input is not None:
            await self.async_set_unique_id(self.flow_impl.client_id)
            self.user_data = user_input
            if user_input[CONF_SANDBOX]:
                self.flow_impl.sandbox_mode()
            return await self.async_step_creation(user_input=user_input)
        client_id = getattr(self.flow_impl, "client_id", None)
        return self.async_show_form(
            step_id="auth",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USER_ID, default=client_id): str,
                    vol.Optional(CONF_SANDBOX, default=False): bool,
                }
            ),
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any]
    ) -> ConfigFlowResult:
        """Handle the configuration step."""
        entry = self._get_reconfigure_entry()
        if user_input is not None:
            return self.async_update_reload_and_abort(
                entry=entry,
                data_updates=user_input,
            )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USER_ID, default=entry.data[CONF_USER_ID]): str,
                }
            ),
        )

    async def async_oauth_create_entry(self, data: dict) -> ConfigFlowResult:
        """Create an entry for OAuth."""
        if self.user_data is not None:
            data = {**self.user_data, **data}
        return await super().async_oauth_create_entry(data)

    @classmethod
    @callback
    def async_get_supported_subentry_types(
        cls, config_entry: ConfigEntry
    ) -> dict[str, type[ConfigSubentryFlow]]:
        """Return subentries supported by this integration."""
        return {"user_link": UserLinkFlowHandler}


class UserLinkFlowHandler(ConfigSubentryFlow):
    """Handle user link flow."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Handle the user link step."""
        entry: EnodeConfigEntry = self._get_entry()
        user_id = entry.data[CONF_USER_ID]
        view = ConfigFlowExternalCallbackView()
        self.hass.http.register_view(view)
        redirect_uri = (
            URL(get_url(self.hass, require_current_request=True))
            .with_path(view.url)
            .with_query(flow_id=self.flow_id)
        )
        try:
            language = Language(self.hass.config.language)
        except ValueError:
            language = Language.BROWSER
        link = await entry.runtime_data.client.user_link(
            user_id=user_id,
            language=language,
            vendor_type=VendorType.VEHICLE,
            redirect_uri=redirect_uri,
        )
        return self.async_external_step(
            step_id="user_link",
            url=link.url,
        )

    async def async_step_user_link(
        self, user_input: dict[str, Any]
    ) -> SubentryFlowResult:
        """Handle the user link step."""
        LOGGER.debug("User linked successfully: %s", user_input)
        return self.async_external_step_done(next_step_id="user_linked")

    async def async_step_user_linked(
        self, user_input: dict[str, Any]
    ) -> SubentryFlowResult:
        """Handle the user link step."""
        self.hass.config_entries.async_schedule_reload(self._entry_id)
        return self.async_abort(reason="user_linked")
