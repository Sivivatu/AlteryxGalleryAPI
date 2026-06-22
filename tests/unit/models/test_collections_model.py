"""Unit tests for collection Pydantic models."""

from datetime import datetime, timezone

from alteryx_server_py.models.collections import (
    Collection,
    CollectionGroupPermissionUpdateRequest,
    CollectionPermission,
    CollectionShareUserRequest,
    CollectionUserPermissionUpdateRequest,
)


class TestCollectionModel:
    """Test Collection model validation."""

    def test_collection_from_api_response(self):
        """Test creating a collection from API data."""
        data = {
            "id": "collection-1",
            "name": "Accounting",
            "ownerId": "user-1",
            "workflowIds": ["workflow-1"],
            "userIds": ["user-1"],
        }

        collection = Collection.model_validate(data)

        assert collection.id == "collection-1"
        assert collection.owner_id == "user-1"
        assert collection.workflow_ids == ["workflow-1"]

    def test_collection_allows_documented_extra_fields(self):
        """Test collection model remains permissive for undocumented fields."""
        data = {
            "id": "collection-1",
            "name": "Accounting",
            "unexpectedField": "value",
        }

        collection = Collection.model_validate(data)

        assert collection.model_extra["unexpectedField"] == "value"


class TestCollectionPermissionRequests:
    """Test collection permission request serialization."""

    def test_share_user_request_flattens_permissions(self):
        """Test nested permission payloads flatten to the API contract."""
        expiration = datetime(2026, 6, 19, 10, 30, tzinfo=timezone.utc)
        request = CollectionShareUserRequest(
            user_id="user-1",
            expiration_date=expiration,
            permissions=CollectionPermission(
                is_admin=True,
                can_add_assets=True,
                can_update_assets=False,
                can_remove_assets=False,
                can_add_users=True,
                can_remove_users=False,
            ),
        )

        data = request.model_dump(by_alias=True, exclude_none=True)

        assert data["userId"] == "user-1"
        assert data["expirationDate"] == "2026-06-19T10:30:00Z"
        assert data["isAdmin"] is True
        assert data["canAddAssets"] is True
        assert "permissions" not in data

    def test_user_permission_update_request_with_expiration_date(self):
        """Test user permission updates serialise expiry timestamps by API alias."""
        request = CollectionUserPermissionUpdateRequest(
            expiration_date=datetime(2026, 6, 19, 10, 30, tzinfo=timezone.utc),
            permissions=CollectionPermission(can_remove_users=True),
        )

        data = request.model_dump(by_alias=True, exclude_none=True)

        assert data["expirationDate"] == "2026-06-19T10:30:00Z"
        assert data["canRemoveUsers"] is True
        assert "permissions" not in data

    def test_group_permission_update_request_allows_missing_expiration_date(self):
        """Test group permission updates can omit an expiry timestamp."""
        request = CollectionGroupPermissionUpdateRequest(
            permissions=CollectionPermission(can_remove_users=True)
        )

        data = request.model_dump(by_alias=True, exclude_none=True)

        assert data["canRemoveUsers"] is True
        assert "expirationDate" not in data
