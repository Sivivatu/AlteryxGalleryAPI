"""Unit tests for CollectionResource."""

from unittest.mock import MagicMock

import pytest
import respx

from alteryx_server_py import AsyncAlteryxClient
from alteryx_server_py.exceptions import CollectionNotFoundError, ValidationError
from alteryx_server_py.models import Collection, CollectionPermission


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
def collection_data():
    """Sample collection data for testing."""
    return {
        "id": "collection-123",
        "name": "Accounting",
        "ownerId": "user-123",
        "ownerEmail": "owner@example.com",
        "workflowIds": ["workflow-456"],
        "userIds": ["user-123"],
        "userGroupIds": ["group-789"],
        "scheduleIds": ["schedule-321"],
        "dateCreated": "2024-01-01T00:00:00Z",
        "lastUpdated": "2024-06-15T10:00:00Z",
    }


class TestCollectionResource:
    """Test CollectionResource functionality."""

    @pytest.mark.asyncio
    async def test_list_collections(self, async_client, collection_data):
        """Test listing collections returns Collection objects."""
        with respx.mock:
            respx.get("https://test.example.com/webapi/v3/collections").respond(
                json=[collection_data]
            )

            collections = await async_client.collections.list()

        assert len(collections) == 1
        assert isinstance(collections[0], Collection)
        assert collections[0].id == "collection-123"

    @pytest.mark.asyncio
    async def test_get_collection(self, async_client, collection_data):
        """Test getting a collection by ID."""
        with respx.mock:
            respx.get(
                "https://test.example.com/webapi/v3/collections/collection-123"
            ).respond(json=collection_data)

            collection = await async_client.collections.get("collection-123")

        assert collection.name == "Accounting"
        assert collection.owner_id == "user-123"

    @pytest.mark.asyncio
    async def test_get_collection_not_found(self, async_client):
        """Test collection lookup raises a collection-specific error."""
        with respx.mock:
            respx.get(
                "https://test.example.com/webapi/v3/collections/missing"
            ).respond(404)

            with pytest.raises(CollectionNotFoundError):
                await async_client.collections.get("missing")

    @pytest.mark.asyncio
    async def test_create_collection(self, async_client, collection_data):
        """Test creating a collection."""
        with respx.mock:
            respx.post("https://test.example.com/webapi/v3/collections").respond(
                json=collection_data
            )

            collection = await async_client.collections.create("Accounting")

        assert collection.id == "collection-123"
        assert collection.name == "Accounting"

    @pytest.mark.asyncio
    async def test_update_collection(self, async_client, collection_data):
        """Test updating a collection."""
        updated = {**collection_data, "name": "Finance", "ownerId": "user-999"}

        with respx.mock:
            respx.put(
                "https://test.example.com/webapi/v3/collections/collection-123"
            ).respond(json=updated)

            collection = await async_client.collections.update(
                "collection-123", name="Finance", owner_id="user-999"
            )

        assert collection.name == "Finance"
        assert collection.owner_id == "user-999"

    @pytest.mark.asyncio
    async def test_add_workflow(self, async_client, collection_data):
        """Test adding a workflow to a collection."""
        with respx.mock:
            respx.post(
                "https://test.example.com/webapi/v3/collections/collection-123/workflows"
            ).respond(json=collection_data)

            collection = await async_client.collections.add_workflow(
                "collection-123", "workflow-456"
            )

        assert collection.workflow_ids == ["workflow-456"]

    @pytest.mark.asyncio
    async def test_set_user_permissions(self, async_client, collection_data):
        """Test updating collection permissions for a user."""
        permissions = CollectionPermission(
            is_admin=True,
            can_add_assets=True,
            can_update_assets=True,
            can_remove_assets=False,
            can_add_users=True,
            can_remove_users=False,
        )

        with respx.mock:
            respx.put(
                "https://test.example.com/webapi/v3/collections/collection-123/users/user-123/permissions"
            ).respond(json=collection_data)

            collection = await async_client.collections.set_permissions(
                "collection-123", permissions=permissions, user_id="user-123"
            )

        assert collection.id == "collection-123"

    @pytest.mark.asyncio
    async def test_set_permissions_requires_exactly_one_subject(self, async_client):
        """Test permission updates validate target subject selection."""
        permissions = CollectionPermission()

        with pytest.raises(ValidationError):
            await async_client.collections.set_permissions(
                "collection-123",
                permissions=permissions,
            )

    @pytest.mark.asyncio
    async def test_delete_collection(self, async_client):
        """Test deleting a collection."""
        with respx.mock:
            respx.delete(
                "https://test.example.com/webapi/v3/collections/collection-123"
            ).respond(204)

            await async_client.collections.delete("collection-123")

        assert True
