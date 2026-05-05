"""
Unit tests for UserResource.
"""

from unittest.mock import MagicMock

import pytest
import respx

from alteryx_server_py import AlteryxClient, AsyncAlteryxClient
from alteryx_server_py.exceptions import UserNotFoundError
from alteryx_server_py.models import User, UserRole


@pytest.fixture
def mock_client():
    """Create a mock sync client for testing."""
    client = AlteryxClient(
        base_url="https://test.example.com/webapi/",
        client_id="test-id",
        client_secret="test-secret",
    )
    client._auth_client = MagicMock()
    client._auth_client.get_token.return_value = "Bearer test-token"
    return client


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
def user_data():
    """Sample user data for testing."""
    return {
        "id": "user-123",
        "email": "testuser@example.com",
        "firstName": "Test",
        "lastName": "User",
        "role": "Member",
        "active": True,
        "defaultWorkerTag": None,
        "timeZone": "America/New_York",
        "isApiEnabled": True,
        "dateCreated": "2024-01-01T00:00:00Z",
        "lastUpdated": "2024-06-15T10:00:00Z",
        "lastLoginDate": "2024-06-15T09:00:00Z",
    }


class TestUserResource:
    """Test UserResource functionality."""

    @pytest.mark.asyncio
    async def test_list_users(self, async_client, user_data):
        """Test listing users returns valid User objects."""
        with respx.mock:
            respx.get(
                "https://test.example.com/webapi/v3/users/",
            ).respond(json=[user_data])

            users = await async_client.users.list()

        assert len(users) == 1
        assert isinstance(users[0], User)
        assert users[0].id == "user-123"
        assert users[0].email == "testuser@example.com"

    @pytest.mark.asyncio
    async def test_list_users_empty(self, async_client):
        """Test listing users when none exist."""
        with respx.mock:
            respx.get(
                "https://test.example.com/webapi/v3/users/",
            ).respond(json=[])

            users = await async_client.users.list()

        assert users == []

    @pytest.mark.asyncio
    async def test_list_users_wrapped(self, async_client, user_data):
        """Test listing users with wrapped response format."""
        with respx.mock:
            respx.get(
                "https://test.example.com/webapi/v3/users/",
            ).respond(json={"users": [user_data]})

            users = await async_client.users.list()

        assert len(users) == 1
        assert users[0].role == UserRole.MEMBER

    @pytest.mark.asyncio
    async def test_get_user(self, async_client, user_data):
        """Test getting user details by ID."""
        with respx.mock:
            respx.get(
                "https://test.example.com/webapi/v3/users/user-123",
            ).respond(json=user_data)

            user = await async_client.users.get("user-123")

        assert isinstance(user, User)
        assert user.id == "user-123"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.role == UserRole.MEMBER

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, async_client):
        """Test getting a user that doesn't exist."""
        with respx.mock:
            respx.get(
                "https://test.example.com/webapi/v3/users/user-999",
            ).respond(404)

            with pytest.raises(UserNotFoundError):
                await async_client.users.get("user-999")

    @pytest.mark.asyncio
    async def test_create_user(self, async_client, user_data):
        """Test creating a new user."""
        with respx.mock:
            respx.post(
                "https://test.example.com/webapi/v3/users/",
            ).respond(json=user_data)

            user = await async_client.users.create(
                email="testuser@example.com",
                first_name="Test",
                last_name="User",
                role="Member",
            )

        assert isinstance(user, User)
        assert user.email == "testuser@example.com"
        assert user.role == UserRole.MEMBER

    @pytest.mark.asyncio
    async def test_update_user(self, async_client, user_data):
        """Test updating an existing user."""
        updated_data = {**user_data, "firstName": "Updated", "role": "Artisan"}

        with respx.mock:
            respx.put(
                "https://test.example.com/webapi/v3/users/user-123",
            ).respond(json=updated_data)

            user = await async_client.users.update(
                "user-123",
                first_name="Updated",
                role="Artisan",
            )

        assert user.first_name == "Updated"
        assert user.role == UserRole.ARTISAN

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, async_client):
        """Test updating a user that doesn't exist."""
        with respx.mock:
            respx.put(
                "https://test.example.com/webapi/v3/users/user-999",
            ).respond(404)

            with pytest.raises(UserNotFoundError):
                await async_client.users.update("user-999", first_name="Test")

    @pytest.mark.asyncio
    async def test_delete_user(self, async_client):
        """Test deleting (deactivating) a user."""
        with respx.mock:
            respx.delete(
                "https://test.example.com/webapi/v3/users/user-123",
            ).respond(204)

            await async_client.users.delete("user-123")

        # Should not raise
        assert True

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, async_client):
        """Test deleting a user that doesn't exist."""
        with respx.mock:
            respx.delete(
                "https://test.example.com/webapi/v3/users/user-999",
            ).respond(404)

            with pytest.raises(UserNotFoundError):
                await async_client.users.delete("user-999")

    @pytest.mark.asyncio
    async def test_get_user_assets(self, async_client):
        """Test getting a user's assets."""
        assets_data = [
            {"id": "wf-1", "type": "workflow", "name": "My Workflow"},
            {"id": "sched-1", "type": "schedule", "name": "Daily Job"},
        ]

        with respx.mock:
            respx.get(
                "https://test.example.com/webapi/v3/users/user-123/assets",
            ).respond(json=assets_data)

            assets = await async_client.users.get_assets("user-123")

        assert len(assets) == 2
        assert assets[0]["type"] == "workflow"

    @pytest.mark.asyncio
    async def test_get_user_assets_not_found(self, async_client):
        """Test getting assets for a user that doesn't exist."""
        with respx.mock:
            respx.get(
                "https://test.example.com/webapi/v3/users/user-999/assets",
            ).respond(404)

            with pytest.raises(UserNotFoundError):
                await async_client.users.get_assets("user-999")
