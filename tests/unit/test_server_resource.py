"""Unit tests for ServerResource."""

from unittest.mock import MagicMock

import pytest
import respx

from alteryx_server_py import AsyncAlteryxClient
from alteryx_server_py.models import ServerInfo, ServerSettings


@pytest.fixture
def async_client():
    """Create a mock async client for testing."""
    client = AsyncAlteryxClient(
        base_url="https://test.example.com/webapi/",
        client_id="test-id",
        client_secret="test-secret",
    )
    client._auth_client = MagicMock()
    client._auth_client.get_token.return_value = "Bearer test-token"
    return client


class TestServerResource:
    """Test ServerResource functionality."""

    @pytest.mark.asyncio
    async def test_get_server_info(self, async_client):
        """Test retrieving server info uses the generic model."""
        payload = {
            "serverVersion": "2025.2",
            "baseAddress": "https://test.example.com/webapi/",
        }

        with respx.mock:
            respx.get("https://test.example.com/webapi/v3/serverinfo").respond(
                json=payload
            )

            info = await async_client.server.get_info()

        assert isinstance(info, ServerInfo)
        assert info.model_extra["serverVersion"] == "2025.2"

    @pytest.mark.asyncio
    async def test_get_server_settings(self, async_client):
        """Test retrieving server settings uses the generic model."""
        payload = {
            "galleryName": "Test Server",
            "allowApiAccess": True,
        }

        with respx.mock:
            respx.get("https://test.example.com/webapi/v3/admin/settings").respond(
                json=payload
            )

            settings = await async_client.server.get_settings()

        assert isinstance(settings, ServerSettings)
        assert settings.model_extra["galleryName"] == "Test Server"
