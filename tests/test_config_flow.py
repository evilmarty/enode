"""Tests for Enode config flow."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.enode.config_flow import OAuth2FlowHandler


@pytest.mark.asyncio
async def test_flow_init(hass):
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
async def test_flow_auth_submit(hass):
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
            user_input={"user_id": "test_user", "sandbox": True}
        )
        assert result["type"] == "external"
        handler.flow_impl.sandbox_mode.assert_called_once()
        assert handler.user_data == {"user_id": "test_user", "sandbox": True}
        handler.async_set_unique_id.assert_called_once_with("test_client_id")
