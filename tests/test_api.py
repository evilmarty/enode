"""Tests for Enode API client."""

from unittest.mock import AsyncMock, MagicMock

from aiohttp import ClientResponse
import pytest

from custom_components.enode.api import EnodeClient, EnodeError
from custom_components.enode.models import Link, Vehicle, Webhook, WebhookTest


class TestEnodeClient:
    """Test EnodeClient class."""

    @pytest.fixture
    def mock_oauth_session(self):
        """Mock OAuth2Session."""
        session = MagicMock()
        session.async_request = AsyncMock()
        return session

    @pytest.mark.asyncio
    async def test_list_vehicles(self, mock_oauth_session, mock_vehicle_data):
        """Test listing vehicles."""
        client = EnodeClient(mock_oauth_session)

        mock_response = AsyncMock(spec=ClientResponse)
        mock_response.status = 200
        mock_response.ok = True
        mock_response.json = AsyncMock(
            return_value={
                "data": [mock_vehicle_data],
                "pagination": {"before": None, "after": None},
            }
        )

        mock_oauth_session.async_request.return_value = mock_response

        vehicles = await client.list_vehicles()

        assert len(vehicles) == 1
        assert isinstance(vehicles[0], Vehicle)
        assert vehicles[0].id == "v1"

    @pytest.mark.asyncio
    async def test_list_user_vehicles(self, mock_oauth_session, mock_vehicle_data):
        """Test listing user vehicles."""
        client = EnodeClient(mock_oauth_session)

        mock_response = AsyncMock(spec=ClientResponse)
        mock_response.status = 200
        mock_response.ok = True
        mock_response.json = AsyncMock(
            return_value={
                "data": [mock_vehicle_data],
                "pagination": {"before": None, "after": None},
            }
        )

        mock_oauth_session.async_request.return_value = mock_response

        vehicles = await client.list_user_vehicles("test_user")

        assert len(vehicles) == 1
        assert "/users/test_user/vehicles" in str(
            mock_oauth_session.async_request.call_args[1]["url"]
        )

    @pytest.mark.asyncio
    async def test_refresh_vehicle_data(self, mock_oauth_session):
        """Test refreshing vehicle data."""
        client = EnodeClient(mock_oauth_session)

        mock_response = AsyncMock(spec=ClientResponse)
        mock_response.status = 204
        mock_response.ok = True

        mock_oauth_session.async_request.return_value = mock_response

        await client.refresh_vehicle_data("v1")

        assert "/vehicles/v1/refresh-hint" in str(
            mock_oauth_session.async_request.call_args[1]["url"]
        )

    @pytest.mark.asyncio
    async def test_user_link(self, mock_oauth_session):
        """Test user linking."""
        client = EnodeClient(mock_oauth_session)

        mock_response = AsyncMock(spec=ClientResponse)
        mock_response.status = 200
        mock_response.ok = True
        mock_response.json = AsyncMock(
            return_value={"linkUrl": "https://link.url", "linkToken": "test_token"}
        )

        mock_oauth_session.async_request.return_value = mock_response

        link = await client.user_link("test_user", "https://redirect.uri")

        assert isinstance(link, Link)
        assert link.url == "https://link.url"
        assert "/users/test_user/link" in str(
            mock_oauth_session.async_request.call_args[1]["url"]
        )

    @pytest.mark.asyncio
    async def test_control_charging(self, mock_oauth_session):
        """Test control charging."""
        client = EnodeClient(mock_oauth_session)

        mock_response = AsyncMock(spec=ClientResponse)
        mock_response.status = 200
        mock_response.ok = True
        mock_response.json = AsyncMock(
            return_value={
                "id": "act1",
                "userId": "u1",
                "createdAt": "2023-01-01T00:00:00Z",
                "updatedAt": "2023-01-01T00:00:00Z",
                "state": "PENDING",
                "targetId": "v1",
                "targetType": "vehicle",
                "kind": "START",
            }
        )

        mock_oauth_session.async_request.return_value = mock_response

        await client.control_charging("v1", "START")

        assert "/vehicles/v1/charging" in str(
            mock_oauth_session.async_request.call_args[1]["url"]
        )

    @pytest.mark.asyncio
    async def test_webhook_lifecycle(self, mock_oauth_session):
        """Test webhook creation, test and deletion."""
        client = EnodeClient(mock_oauth_session)

        # Create
        mock_response_create = AsyncMock(spec=ClientResponse)
        mock_response_create.status = 201
        mock_response_create.ok = True
        mock_response_create.json = AsyncMock(
            return_value={
                "id": "wh1",
                "url": "https://wh.url",
                "events": ["*"],
                "isActive": True,
                "createdAt": "2023-01-01T00:00:00Z",
                "lastSuccess": "2023-01-01T00:00:00Z",
            }
        )

        mock_oauth_session.async_request.return_value = mock_response_create
        webhook = await client.create_webhook("https://wh.url", "secret")
        assert isinstance(webhook, Webhook)
        assert webhook.id == "wh1"

        # Test
        mock_response_test = AsyncMock(spec=ClientResponse)
        mock_response_test.status = 200
        mock_response_test.ok = True
        mock_response_test.json = AsyncMock(
            return_value={
                "status": "SUCCESS",
                "description": "Webhook test succeeded",
                "response": {"code": 200, "body": "OK"},
            }
        )

        mock_oauth_session.async_request.return_value = mock_response_test
        test_result = await client.test_webhook("wh1")
        assert isinstance(test_result, WebhookTest)
        assert test_result.is_success

        # Delete
        mock_response_delete = AsyncMock(spec=ClientResponse)
        mock_response_delete.status = 204
        mock_response_delete.ok = True

        mock_oauth_session.async_request.return_value = mock_response_delete
        await client.delete_webhook("wh1")
        assert "/webhooks/wh1" in str(
            mock_oauth_session.async_request.call_args[1]["url"]
        )

    @pytest.mark.asyncio
    async def test_enode_error(self, mock_oauth_session):
        """Test EnodeError handling."""
        client = EnodeClient(mock_oauth_session)

        mock_response = AsyncMock(spec=ClientResponse)
        mock_response.status = 400
        mock_response.ok = False
        mock_response.json = AsyncMock(
            return_value={
                "type": "error",
                "title": "Bad Request",
                "detail": "Invalid parameter",
            }
        )

        mock_oauth_session.async_request.return_value = mock_response

        with pytest.raises(EnodeError) as excinfo:
            await client.list_vehicles()

        assert excinfo.value.status == 400
        assert excinfo.value.data.title == "Bad Request"
        assert excinfo.value.data.detail == "Invalid parameter"
