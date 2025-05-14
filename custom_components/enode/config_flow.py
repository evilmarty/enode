"""Config flow for Enode."""

import asyncio
from contextlib import suppress
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
from homeassistant.helpers.config_entry_oauth2_flow import AbstractOAuth2FlowHandler
from homeassistant.helpers.network import NoURLAvailableError, get_url
from homeassistant.util import get_random_string

from .api import Language, VendorType, WebhookEventType
from .const import (
    CONF_SANDBOX,
    CONF_USER_ID,
    CONF_WEBHOOK_ID,
    CONF_WEBHOOK_SECRET,
    DOMAIN,
    LOGGER,
)
from .coordinator import EnodeConfigEntry
from .views import ConfigFlowExternalCallbackView, EnodeWebhookView
from .webhook import prepare_test_webhook

TEST_TIMEOUT = 20
RAND_LENGTH = 32
SUPPORTED_WEBHOOK_EVENTS = [
    WebhookEventType.ENODE_WEBHOOK_TEST,
    *VendorType.VEHICLE.webhook_events,
]


class OAuth2FlowHandler(AbstractOAuth2FlowHandler, domain=DOMAIN):
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
        client_id = getattr(self.flow_impl, "client_id", None)
        if user_input is not None:
            if client_id is not None:
                await self.async_set_unique_id(client_id)
            self.user_data = user_input
            if user_input.get(CONF_SANDBOX, False):
                self.flow_impl.sandbox_mode()
            return await self.async_step_creation(user_input=user_input)
        data_schema = {
            vol.Required(CONF_USER_ID, default=client_id): str,
        }
        if self.show_advanced_options:
            data_schema[vol.Optional(CONF_SANDBOX, default=False)] = bool
        return self.async_show_form(
            step_id="auth",
            data_schema=vol.Schema(data_schema),
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
        return {"user_link": UserLinkFlowHandler, "webhook": WebhookFlowHandler}


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


class WebhookFlowHandler(ConfigSubentryFlow):
    """Handle webhook flow."""

    _task: asyncio.Task[None] | None = None
    _done_task: asyncio.Task[None] | None = None
    _url: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Handle the user step."""
        self._task = None
        self._done_task = None
        with suppress(NoURLAvailableError):
            self._url = (
                URL(get_url(self.hass, allow_internal=False, require_ssl=True))
                .with_path(EnodeWebhookView.url)
                .with_query(entry_id=self._entry_id)
            )
        if self._url:
            return self.async_show_menu(
                step_id="user", menu_options=["create", "test", "delete"]
            )
        return self.async_abort(reason="external_url_unavailable")

    async def async_step_create(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Handle the create webhook step."""
        if not self._task:
            self._task = self.hass.async_create_task(self._create_webhook())
        if not self._task.done():
            return self.async_show_progress(
                progress_action="creating_webhook",
                progress_task=self._task,
            )
        return self.async_show_progress_done(next_step_id="create_done")

    async def async_step_create_done(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Handle the create webhook done step."""
        return self._async_step_done(
            success_action="create_webhook_succeeded",
            failure_action="create_webhook_failed",
        )

    async def async_step_test(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Handle the test webhook step."""
        if not self._task:
            self._task = self.hass.async_create_task(self._test_webhook())
        if not self._task.done():
            return self.async_show_progress(
                progress_action="testing_webhook",
                progress_task=self._task,
            )
        return self.async_show_progress_done(next_step_id="test_done")

    async def async_step_test_done(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Handle the test webhook done step."""
        return self._async_step_done(
            success_action="test_webhook_succeeded",
            failure_action="test_webhook_failed",
        )

    async def async_step_delete(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Handle the delete webhook step."""
        if not self._task:
            self._task = self.hass.async_create_task(self._delete_webhook())
        if not self._task.done():
            return self.async_show_progress(
                progress_action="deleting_webhook",
                progress_task=self._task,
            )
        return self.async_show_progress_done(next_step_id="user")

    async def async_step_delete_done(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Handle the delete webhook done step."""
        return self._async_step_done(
            success_action="delete_webhook_succeeded",
            failure_action="delete_webhook_failed",
        )

    async def _create_webhook(self) -> None:
        """Create a webhook."""
        entry: EnodeConfigEntry = self._get_entry()
        if entry.data.get(CONF_WEBHOOK_ID):
            return
        self.hass.http.register_view(EnodeWebhookView)
        LOGGER.debug("Creating webhook with URL: %s", self._url)
        secret = get_random_string(RAND_LENGTH)
        webhook = await entry.runtime_data.client.create_webhook(
            url=self._url,
            secret=secret,
            events=SUPPORTED_WEBHOOK_EVENTS,
        )
        LOGGER.debug("Webhook created: %s", webhook.id)
        self.hass.config_entries.async_update_entry(
            entry=entry,
            data={
                **entry.data,
                CONF_WEBHOOK_ID: webhook.id,
                CONF_WEBHOOK_SECRET: secret,
            },
        )

    async def _test_webhook(self) -> None:
        """Test the webhook."""
        entry: EnodeConfigEntry = self._get_entry()
        if webhook_id := entry.data.get(CONF_WEBHOOK_ID):
            test_future = prepare_test_webhook(self.hass, entry)
            resp = await entry.runtime_data.client.test_webhook(webhook_id)
            LOGGER.info("Webhook test response: %s", resp)
            if not resp.is_success:
                raise ValueError(resp.description)
            async with self.hass.timeout.async_timeout(TEST_TIMEOUT):
                await test_future
        else:
            raise ValueError("Webhook ID not found in entry data")

    async def _delete_webhook(self) -> None:
        """Delete the webhook."""
        entry: EnodeConfigEntry = self._get_entry()
        data = entry.data.copy()
        webhook_id = data.pop(CONF_WEBHOOK_ID, None)
        data.pop(CONF_WEBHOOK_SECRET, None)
        self.hass.config_entries.async_update_entry(
            entry=entry,
            data=data,
        )
        if webhook_id:
            await entry.runtime_data.client.delete_webhook(webhook_id)
            LOGGER.debug("Webhook deleted: %s", webhook_id)

    def _async_step_done(
        self, success_action: str, failure_action: str
    ) -> SubentryFlowResult:
        """Handle the create webhook done step."""
        if not self._done_task:
            self._done_task = self.hass.async_create_task(asyncio.sleep(5))
        if not self._done_task.done():
            placeholders = {}
            progress_action = success_action
            if ex := self._task.exception():
                progress_action = failure_action
                placeholders["error"] = str(ex)
            return self.async_show_progress(
                progress_action=progress_action,
                progress_task=self._done_task,
                description_placeholders=placeholders,
            )
        return self.async_show_progress_done(next_step_id="user")
