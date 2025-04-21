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

from .const import DATA_USER_ID, DOMAIN, LOGGER
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
        errors = {}
        if user_input is not None:
            await self.async_set_unique_id(user_input["user_id"])
            errors = self._validate_user_input(user_input)
            if not errors:
                self.user_data = user_input
                return await self.async_step_creation(user_input=user_input)
        client_id = getattr(self.flow_impl, "client_id", None)
        return self.async_show_form(
            step_id="auth",
            data_schema=vol.Schema(
                {
                    vol.Required("user_id", default=client_id): str,
                }
            ),
            errors=errors,
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
        user_id = entry.data[DATA_USER_ID]
        view = ConfigFlowExternalCallbackView()
        self.hass.http.register_view(view)
        redirect_uri = (
            URL(get_url(self.hass, require_current_request=True))
            .with_path(view.url)
            .with_query(flow_id=self.flow_id)
        )
        link = await entry.runtime_data.client.user_link(
            user_id=user_id,
            language=self.hass.config.language,
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


#     @staticmethod
#     @callback
#     def async_get_options_flow(
#         config_entry: ConfigEntry,
#     ) -> OptionsFlow:
#         """Create the options flow."""
#         return EnodeOptionsFlowHandler(config_entry)


# class EnodeOptionsFlowHandler(OptionsFlow):
#     """Handle Enode options."""

#     def __init__(self, config_entry: ConfigEntry) -> None:
#         """Initialize the options flow."""
#         self.config_entry = config_entry

#     async def async_step_init(
#         self, user_input: dict[str, Any] | None = None
#     ) -> ConfigFlowResult:
#         """Manage the options."""
#         return self.async_show_menu(
#             step_id="init",
#             menu_options=["link_user", "unlink_user"],
#         )
