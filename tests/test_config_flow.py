"""Tests for Enode config flow."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.enode.config_flow import (
    OAuth2FlowHandler,
    UserLinkFlowHandler,
    WebhookFlowHandler,
)
from custom_components.enode.const import CONF_SANDBOX, CONF_USER_ID
from custom_components.enode.models import Link


class TestOAuth2FlowHandler:
    """Test OAuth2FlowHandler class."""

    @pytest.mark.asyncio
    async def test_flow_init(self, hass):
        """Test the flow initialization."""
        with patch(
            "custom_components.enode.config_flow.OAuth2FlowHandler.async_show_form",
            return_value={"type": "form", "step_id": "auth"},
        ):
            handler = OAuth2FlowHandler()
            handler.hass = hass
            handler.flow_id = "test_flow"
            handler.flow_impl = MagicMock()
            handler.flow_impl.client_id = "test_client_id"

            result = await handler.async_step_auth()
            assert result["type"] == "form"
            assert result["step_id"] == "auth"

    @pytest.mark.asyncio
    async def test_flow_auth_submit(self, hass):
        """Test the flow auth step submission."""
        handler = OAuth2FlowHandler()
        handler.hass = hass
        handler.flow_id = "test_flow"
        handler.flow_impl = MagicMock()
        handler.flow_impl.client_id = "test_client_id"
        handler.flow_impl.sandbox_mode = MagicMock()

        # Mocking internal HA methods to avoid complex setup
        handler.async_set_unique_id = AsyncMock()

        with patch(
            "custom_components.enode.config_flow.OAuth2FlowHandler.async_step_creation",
            return_value={"type": "external", "step_id": "creation"},
        ):
            result = await handler.async_step_auth(
                user_input={CONF_USER_ID: "test_user", CONF_SANDBOX: True}
            )
            assert result["type"] == "external"
            handler.flow_impl.sandbox_mode.assert_called_once()
            assert handler.user_data == {CONF_USER_ID: "test_user", CONF_SANDBOX: True}
            handler.async_set_unique_id.assert_called_once_with("test_client_id")


class TestUserLinkFlowHandler:
    """Test UserLinkFlowHandler class."""

    @pytest.mark.asyncio
    async def test_user_link_flow(self, hass):
        """Test user link flow steps."""
        handler = UserLinkFlowHandler()
        handler.handler = ("test_entry", "")
        handler.hass = hass
        handler.flow_id = "test_flow"

        mock_entry = MagicMock()
        mock_entry.data = {CONF_USER_ID: "test_user"}
        mock_entry.runtime_data.client.user_link = AsyncMock(
            return_value=Link(linkUrl="https://link.url", linkToken="token")
        )

        hass.config_entries.async_get_known_entry.return_value = mock_entry

        with patch(
            "custom_components.enode.config_flow.get_url", return_value="https://ha.url"
        ):
            result = await handler.async_step_user()
            assert result["type"] == "external"
            assert result["url"] == "https://link.url"

        result = await handler.async_step_user_link(user_input={"success": True})
        assert result["type"] == "external_done"
        assert result["step_id"] == "user_linked"

        with patch.object(hass.config_entries, "async_schedule_reload") as mock_reload:
            result = await handler.async_step_user_linked(user_input={})
            assert result["type"] == "abort"
            assert result["reason"] == "user_linked"
            mock_reload.assert_called_once()


class TestWebhookFlowHandler:
    """Test WebhookFlowHandler class."""

    @pytest.mark.asyncio
    async def test_webhook_flow_menu(self, hass):
        """Test webhook flow menu."""
        handler = WebhookFlowHandler()
        handler.hass = hass
        handler.handler = ("test_entry", "")

        with patch(
            "custom_components.enode.config_flow.get_url", return_value="https://ha.url"
        ):
            result = await handler.async_step_user()
            assert result["type"] == "menu"
            assert "create" in result["menu_options"]

    @pytest.mark.asyncio
    async def test_webhook_create_flow(self, hass):
        """Test webhook creation flow."""
        mock_done = MagicMock(return_value=False)

        # Swallow the task creation and return a mock task that we can control
        def mock_async_create_task(coro):
            asyncio.ensure_future(coro).cancel()
            return MagicMock(done=mock_done)

        hass.async_create_task = mock_async_create_task
        handler = WebhookFlowHandler()
        handler.hass = hass
        handler.handler = ("test_entry", "")

        mock_entry = MagicMock()
        mock_entry.data = {}
        mock_client = mock_entry.runtime_data.client
        mock_client.create_webhook = AsyncMock(return_value=MagicMock(id="wh1"))
        hass.config_entries.async_get_known_entry.return_value = mock_entry

        # Test progress
        result = await handler.async_step_create()
        assert result["type"] == "progress"

        # Mock task done
        mock_done.return_value = True
        result = await handler.async_step_create()
        assert result["type"] == "progress_done"
        assert result["step_id"] == "create_done"
