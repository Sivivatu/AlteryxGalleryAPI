"""Unit tests for CredentialResource."""

from unittest.mock import MagicMock

import pytest
import respx

from alteryx_server_py import AsyncAlteryxClient
from alteryx_server_py.exceptions import CredentialNotFoundError
from alteryx_server_py.models import Credential


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


@pytest.fixture
def credential_data():
    """Sample credential data for testing."""
    return {
        "id": "cred-123",
        "username": "CONTOSO\\svc-alteryx",
        "ownerId": "user-123",
        "userIds": ["user-123"],
        "userGroupIds": ["group-123"],
        "dateCreated": "2024-01-01T00:00:00Z",
        "lastUpdated": "2024-06-15T10:00:00Z",
    }


class TestCredentialResource:
    """Test CredentialResource functionality."""

    @pytest.mark.asyncio
    async def test_list_credentials(self, async_client, credential_data):
        """Test listing credentials returns Credential objects."""
        with respx.mock:
            respx.get("https://test.example.com/webapi/v3/credentials").respond(
                json=[credential_data]
            )

            credentials = await async_client.credentials.list()

        assert len(credentials) == 1
        assert isinstance(credentials[0], Credential)
        assert credentials[0].id == "cred-123"

    @pytest.mark.asyncio
    async def test_get_credential(self, async_client, credential_data):
        """Test getting a credential by ID."""
        with respx.mock:
            respx.get(
                "https://test.example.com/webapi/v3/credentials/cred-123"
            ).respond(json=credential_data)

            credential = await async_client.credentials.get("cred-123")

        assert credential.username == "CONTOSO\\svc-alteryx"

    @pytest.mark.asyncio
    async def test_get_credential_not_found(self, async_client):
        """Test missing credential lookup raises a credential-specific error."""
        with respx.mock:
            respx.get(
                "https://test.example.com/webapi/v3/credentials/missing"
            ).respond(404)

            with pytest.raises(CredentialNotFoundError):
                await async_client.credentials.get("missing")

    @pytest.mark.asyncio
    async def test_create_credential(self, async_client, credential_data):
        """Test creating a credential."""
        with respx.mock:
            respx.post("https://test.example.com/webapi/v3/credentials").respond(
                json=credential_data
            )

            credential = await async_client.credentials.create(
                username="CONTOSO\\svc-alteryx",
                password="secret",
            )

        assert credential.id == "cred-123"

    @pytest.mark.asyncio
    async def test_update_credential(self, async_client, credential_data):
        """Test updating a credential password."""
        with respx.mock:
            respx.put(
                "https://test.example.com/webapi/v3/credentials/cred-123"
            ).respond(json=credential_data)

            credential = await async_client.credentials.update(
                "cred-123", new_password="new-secret"
            )

        assert credential.owner_id == "user-123"

    @pytest.mark.asyncio
    async def test_delete_credential(self, async_client):
        """Test deleting a credential."""
        with respx.mock:
            respx.delete(
                "https://test.example.com/webapi/v3/credentials/cred-123"
            ).respond(204)

            await async_client.credentials.delete("cred-123")

        assert True
