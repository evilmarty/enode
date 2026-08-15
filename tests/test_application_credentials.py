"""Tests for Enode application credentials helpers."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.enode.application_credentials import Oauth2Impl, get_client
from custom_components.enode.const import CONF_SANDBOX


@pytest.mark.asyncio
async def test_get_client_enables_sandbox_oauth_implementation(hass):
    """Apply sandbox mode to OAuth implementation when entry uses sandbox."""
    entry = MagicMock()
    entry.data = {CONF_SANDBOX: True}
    implementation = MagicMock(spec=Oauth2Impl)

    with (
        patch(
            "custom_components.enode.application_credentials.async_get_config_entry_implementation",
            AsyncMock(return_value=implementation),
        ),
        patch(
            "custom_components.enode.application_credentials.OAuth2Session",
            return_value="oauth_session",
        ),
        patch(
            "custom_components.enode.application_credentials.EnodeClient",
            return_value="enode_client",
        ),
    ):
        client = await get_client(hass, entry)

    implementation.sandbox_mode.assert_called_once()
    assert client == "enode_client"


@pytest.mark.asyncio
async def test_get_client_keeps_production_oauth_implementation(hass):
    """Keep production OAuth implementation when sandbox is disabled."""
    entry = MagicMock()
    entry.data = {CONF_SANDBOX: False}
    implementation = MagicMock(spec=Oauth2Impl)

    with patch(
        "custom_components.enode.application_credentials.async_get_config_entry_implementation",
        AsyncMock(return_value=implementation),
    ):
        await get_client(hass, entry)

    implementation.sandbox_mode.assert_not_called()
