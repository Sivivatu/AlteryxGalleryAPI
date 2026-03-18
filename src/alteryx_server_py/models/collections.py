"""
Collection models for API.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .base import BaseApiModel
from .common import CollectionId, UserGroupId, UserId, WorkflowId


class CollectionPermission(BaseModel):
    """Permission model for collection membership."""

    model_config = ConfigDict(populate_by_name=True)

    is_admin: bool = Field(False, alias="isAdmin")
    can_add_assets: bool = Field(False, alias="canAddAssets")
    can_update_assets: bool = Field(False, alias="canUpdateAssets")
    can_remove_assets: bool = Field(False, alias="canRemoveAssets")
    can_add_users: bool = Field(False, alias="canAddUsers")
    can_remove_users: bool = Field(False, alias="canRemoveUsers")


class Collection(BaseApiModel):
    """Collection model representing a Server collection."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="allow",
        populate_by_name=True,
    )

    id: CollectionId
    name: str
    owner_id: Optional[UserId] = Field(None, alias="ownerId")
    owner_email: Optional[str] = Field(None, alias="ownerEmail")
    created_date: Optional[datetime] = Field(None, alias="dateCreated")
    updated_date: Optional[datetime] = Field(None, alias="lastUpdated")
    user_ids: list[UserId] = Field(default_factory=list, alias="userIds")
    user_group_ids: list[UserGroupId] = Field(default_factory=list, alias="userGroupIds")
    workflow_ids: list[WorkflowId] = Field(default_factory=list, alias="workflowIds")
    schedule_ids: list[str] = Field(default_factory=list, alias="scheduleIds")


class CollectionCreateRequest(BaseModel):
    """Request model for creating a collection."""

    model_config = ConfigDict(populate_by_name=True)

    name: str


class CollectionUpdateRequest(BaseModel):
    """Request model for updating a collection."""

    model_config = ConfigDict(populate_by_name=True)

    name: str
    owner_id: UserId = Field(..., alias="ownerId")


class CollectionShareUserRequest(BaseModel):
    """Request model for adding a user to a collection."""

    model_config = ConfigDict(populate_by_name=True)

    user_id: UserId = Field(..., alias="userId")
    expiration_date: Optional[datetime] = Field(None, alias="expirationDate")
    permissions: CollectionPermission

    def model_dump(self, *args, **kwargs):
        """Flatten nested permissions to match form-encoded API contracts."""
        data = super().model_dump(*args, **kwargs)
        permissions = data.pop("permissions", None)
        if permissions:
            data.update(permissions)
        return data


class CollectionShareGroupRequest(BaseModel):
    """Request model for adding a user group to a collection."""

    model_config = ConfigDict(populate_by_name=True)

    user_group_id: UserGroupId = Field(..., alias="userGroupId")
    expiration_date: Optional[datetime] = Field(None, alias="expirationDate")
    permissions: CollectionPermission

    def model_dump(self, *args, **kwargs):
        """Flatten nested permissions to match form-encoded API contracts."""
        data = super().model_dump(*args, **kwargs)
        permissions = data.pop("permissions", None)
        if permissions:
            data.update(permissions)
        return data


class CollectionPermissionUpdateRequest(BaseModel):
    """Request model for updating collection permissions."""

    model_config = ConfigDict(populate_by_name=True)

    expiration_date: Optional[datetime] = Field(None, alias="expirationDate")
    permissions: CollectionPermission

    def model_dump(self, *args, **kwargs):
        """Flatten nested permissions to match form-encoded API contracts."""
        data = super().model_dump(*args, **kwargs)
        permissions = data.pop("permissions", None)
        if permissions:
            data.update(permissions)
        return data


class CollectionWorkflowRequest(BaseModel):
    """Request model for adding a workflow to a collection."""

    model_config = ConfigDict(populate_by_name=True)

    workflow_id: WorkflowId = Field(..., alias="workflowId")
