"""
Unit tests for User and UserGroup Pydantic models.
"""

import pytest

from alteryx_server_py.models.common import UserRole
from alteryx_server_py.models.users import (
    User,
    UserCreateRequest,
    UserGroup,
    UserGroupCreateRequest,
    UserGroupUpdateRequest,
    UserUpdateRequest,
)


class TestUserModel:
    """Test User model validation."""

    def test_user_from_api_response(self):
        """Test creating User from typical API response data."""
        data = {
            "id": "user-123",
            "email": "test@example.com",
            "firstName": "Jane",
            "lastName": "Doe",
            "role": "Artisan",
            "active": True,
            "timeZone": "UTC",
            "isApiEnabled": True,
            "dateCreated": "2024-01-01T00:00:00Z",
        }
        user = User.model_validate(data)

        assert user.id == "user-123"
        assert user.email == "test@example.com"
        assert user.first_name == "Jane"
        assert user.role == UserRole.ARTISAN
        assert user.active is True

    def test_user_minimal_fields(self):
        """Test User with minimal required fields."""
        data = {
            "id": "user-1",
            "email": "min@example.com",
            "role": "Viewer",
            "active": True,
        }
        user = User.model_validate(data)

        assert user.id == "user-1"
        assert user.first_name is None
        assert user.last_name is None

    def test_user_rejects_unknown_fields(self):
        """Test that User rejects unknown fields (strict mode)."""
        data = {
            "id": "user-1",
            "email": "test@example.com",
            "role": "Viewer",
            "active": True,
            "unknownField": "value",
        }
        with pytest.raises(Exception):
            User.model_validate(data)


class TestUserCreateRequest:
    """Test UserCreateRequest model."""

    def test_create_request_serialization(self):
        """Test create request serializes with camelCase aliases."""
        request = UserCreateRequest(
            email="new@example.com",
            first_name="New",
            last_name="User",
            role=UserRole.MEMBER,
        )
        data = request.model_dump(by_alias=True, exclude_none=True)

        assert data["email"] == "new@example.com"
        assert data["firstName"] == "New"
        assert data["lastName"] == "User"
        assert data["role"] == "Member"

    def test_create_request_defaults(self):
        """Test create request with default role."""
        request = UserCreateRequest(email="default@example.com")
        assert request.role == UserRole.VIEWER


class TestUserUpdateRequest:
    """Test UserUpdateRequest model."""

    def test_update_request_partial(self):
        """Test update request with only some fields."""
        request = UserUpdateRequest(first_name="Updated")
        data = request.model_dump(by_alias=True, exclude_none=True)

        assert data == {"firstName": "Updated"}

    def test_update_request_deactivate(self):
        """Test update request to deactivate user."""
        request = UserUpdateRequest(active=False)
        data = request.model_dump(by_alias=True, exclude_none=True)

        assert data == {"active": False}


class TestUserGroupModel:
    """Test UserGroup model validation."""

    def test_group_from_api_response(self):
        """Test creating UserGroup from typical API response data."""
        data = {
            "id": "group-123",
            "name": "Engineers",
            "role": "Artisan",
            "description": "Engineering team",
            "memberIds": ["user-1", "user-2"],
            "dateCreated": "2024-01-01T00:00:00Z",
        }
        group = UserGroup.model_validate(data)

        assert group.id == "group-123"
        assert group.name == "Engineers"
        assert group.role == UserRole.ARTISAN
        assert len(group.member_ids) == 2

    def test_group_minimal_fields(self):
        """Test UserGroup with minimal required fields."""
        data = {
            "id": "group-1",
            "name": "Test Group",
        }
        group = UserGroup.model_validate(data)

        assert group.id == "group-1"
        assert group.description is None
        assert group.member_ids == []

    def test_group_rejects_unknown_fields(self):
        """Test that UserGroup rejects unknown fields (strict mode)."""
        data = {
            "id": "group-1",
            "name": "Test Group",
            "unknownField": "value",
        }
        with pytest.raises(Exception):
            UserGroup.model_validate(data)


class TestUserGroupCreateRequest:
    """Test UserGroupCreateRequest model."""

    def test_create_request_serialization(self):
        """Test create request serializes correctly."""
        request = UserGroupCreateRequest(
            name="New Group",
            role=UserRole.MEMBER,
            description="A new group",
        )
        data = request.model_dump(by_alias=True, exclude_none=True)

        assert data["name"] == "New Group"
        assert data["role"] == "Member"
        assert data["description"] == "A new group"

    def test_create_request_name_only(self):
        """Test create request with only a name."""
        request = UserGroupCreateRequest(name="Simple Group")
        data = request.model_dump(by_alias=True, exclude_none=True)

        assert data == {"name": "Simple Group"}


class TestUserGroupUpdateRequest:
    """Test UserGroupUpdateRequest model."""

    def test_update_request_partial(self):
        """Test update request with only some fields."""
        request = UserGroupUpdateRequest(name="Updated Group")
        data = request.model_dump(by_alias=True, exclude_none=True)

        assert data == {"name": "Updated Group"}

    def test_update_request_role_change(self):
        """Test update request to change role."""
        request = UserGroupUpdateRequest(role=UserRole.CURATOR)
        data = request.model_dump(by_alias=True, exclude_none=True)

        assert data == {"role": "Curator"}
