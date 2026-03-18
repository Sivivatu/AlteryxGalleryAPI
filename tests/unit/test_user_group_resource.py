"""
Unit tests for UserGroupResource.
"""

from unittest.mock import MagicMock

import pytest
import respx

from alteryx_server_py import AlteryxClient, AsyncAlteryxClient
from alteryx_server_py.exceptions import UserGroupNotFoundError
from alteryx_server_py.models import UserGroup, UserRole


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
def group_data():
    """Sample user group data for testing."""
    return {
        "id": "group-123",
        "name": "Data Engineers",
        "role": "Artisan",
        "description": "Data engineering team",
        "memberIds": ["user-1", "user-2", "user-3"],
        "dateCreated": "2024-01-01T00:00:00Z",
        "lastUpdated": "2024-06-15T10:00:00Z",
    }


class TestUserGroupResource:
    """Test UserGroupResource functionality."""

    @pytest.mark.asyncio
    async def test_list_groups(self, async_client, group_data):
        """Test listing user groups returns valid UserGroup objects."""
        with respx.mock:
            respx.get(
                "https://test.example.com/webapi/v3/usergroups/",
            ).respond(json=[group_data])

            groups = await async_client.user_groups.list()

        assert len(groups) == 1
        assert isinstance(groups[0], UserGroup)
        assert groups[0].id == "group-123"
        assert groups[0].name == "Data Engineers"

    @pytest.mark.asyncio
    async def test_list_groups_empty(self, async_client):
        """Test listing user groups when none exist."""
        with respx.mock:
            respx.get(
                "https://test.example.com/webapi/v3/usergroups/",
            ).respond(json=[])

            groups = await async_client.user_groups.list()

        assert groups == []

    @pytest.mark.asyncio
    async def test_list_groups_wrapped(self, async_client, group_data):
        """Test listing user groups with wrapped response format."""
        with respx.mock:
            respx.get(
                "https://test.example.com/webapi/v3/usergroups/",
            ).respond(json={"userGroups": [group_data]})

            groups = await async_client.user_groups.list()

        assert len(groups) == 1
        assert groups[0].role == UserRole.ARTISAN

    @pytest.mark.asyncio
    async def test_get_group(self, async_client, group_data):
        """Test getting user group details by ID."""
        with respx.mock:
            respx.get(
                "https://test.example.com/webapi/v3/usergroups/group-123",
            ).respond(json=group_data)

            group = await async_client.user_groups.get("group-123")

        assert isinstance(group, UserGroup)
        assert group.id == "group-123"
        assert group.description == "Data engineering team"
        assert len(group.member_ids) == 3

    @pytest.mark.asyncio
    async def test_get_group_not_found(self, async_client):
        """Test getting a user group that doesn't exist."""
        with respx.mock:
            respx.get(
                "https://test.example.com/webapi/v3/usergroups/group-999",
            ).respond(404)

            with pytest.raises(UserGroupNotFoundError):
                await async_client.user_groups.get("group-999")

    @pytest.mark.asyncio
    async def test_create_group(self, async_client, group_data):
        """Test creating a new user group."""
        with respx.mock:
            respx.post(
                "https://test.example.com/webapi/v3/usergroups/",
            ).respond(json=group_data)

            group = await async_client.user_groups.create(
                name="Data Engineers",
                role="Artisan",
                description="Data engineering team",
            )

        assert isinstance(group, UserGroup)
        assert group.name == "Data Engineers"
        assert group.role == UserRole.ARTISAN

    @pytest.mark.asyncio
    async def test_update_group(self, async_client, group_data):
        """Test updating an existing user group."""
        updated_data = {**group_data, "name": "Senior Data Engineers"}

        with respx.mock:
            respx.put(
                "https://test.example.com/webapi/v3/usergroups/group-123",
            ).respond(json=updated_data)

            group = await async_client.user_groups.update(
                "group-123",
                name="Senior Data Engineers",
            )

        assert group.name == "Senior Data Engineers"

    @pytest.mark.asyncio
    async def test_update_group_not_found(self, async_client):
        """Test updating a user group that doesn't exist."""
        with respx.mock:
            respx.put(
                "https://test.example.com/webapi/v3/usergroups/group-999",
            ).respond(404)

            with pytest.raises(UserGroupNotFoundError):
                await async_client.user_groups.update("group-999", name="Test")

    @pytest.mark.asyncio
    async def test_delete_group(self, async_client):
        """Test deleting a user group."""
        with respx.mock:
            respx.delete(
                "https://test.example.com/webapi/v3/usergroups/group-123",
            ).respond(204)

            await async_client.user_groups.delete("group-123")

        # Should not raise
        assert True

    @pytest.mark.asyncio
    async def test_delete_group_not_found(self, async_client):
        """Test deleting a user group that doesn't exist."""
        with respx.mock:
            respx.delete(
                "https://test.example.com/webapi/v3/usergroups/group-999",
            ).respond(404)

            with pytest.raises(UserGroupNotFoundError):
                await async_client.user_groups.delete("group-999")

    @pytest.mark.asyncio
    async def test_add_users_to_group(self, async_client, group_data):
        """Test adding users to a user group."""
        updated_data = {**group_data, "memberIds": ["user-1", "user-2", "user-3", "user-4"]}

        with respx.mock:
            respx.post(
                "https://test.example.com/webapi/v3/usergroups/group-123/users",
            ).respond(json=updated_data)

            group = await async_client.user_groups.add_users(
                "group-123",
                user_ids=["user-4"],
            )

        assert len(group.member_ids) == 4
        assert "user-4" in group.member_ids

    @pytest.mark.asyncio
    async def test_add_users_group_not_found(self, async_client):
        """Test adding users to a user group that doesn't exist."""
        with respx.mock:
            respx.post(
                "https://test.example.com/webapi/v3/usergroups/group-999/users",
            ).respond(404)

            with pytest.raises(UserGroupNotFoundError):
                await async_client.user_groups.add_users("group-999", user_ids=["user-1"])

    @pytest.mark.asyncio
    async def test_remove_user_from_group(self, async_client):
        """Test removing a user from a user group."""
        with respx.mock:
            respx.delete(
                "https://test.example.com/webapi/v3/usergroups/group-123/users/user-1",
            ).respond(204)

            await async_client.user_groups.remove_user("group-123", "user-1")

        # Should not raise
        assert True

    @pytest.mark.asyncio
    async def test_remove_user_group_not_found(self, async_client):
        """Test removing a user from a group that doesn't exist."""
        with respx.mock:
            respx.delete(
                "https://test.example.com/webapi/v3/usergroups/group-999/users/user-1",
            ).respond(404)

            with pytest.raises(UserGroupNotFoundError):
                await async_client.user_groups.remove_user("group-999", "user-1")
