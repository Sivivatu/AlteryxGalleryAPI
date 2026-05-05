"""
Credential models for API.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .base import BaseApiModel
from .common import CredentialId, CredentialType, UserGroupId, UserId


class Credential(BaseApiModel):
    """Credential model representing a shared server credential."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="allow",
        populate_by_name=True,
    )

    id: CredentialId
    username: Optional[str] = None
    credential_type: Optional[CredentialType] = Field(None, alias="credentialType")
    owner_id: Optional[UserId] = Field(None, alias="ownerId")
    created_date: Optional[datetime] = Field(None, alias="dateCreated")
    updated_date: Optional[datetime] = Field(None, alias="lastUpdated")
    user_ids: list[UserId] = Field(default_factory=list, alias="userIds")
    user_group_ids: list[UserGroupId] = Field(default_factory=list, alias="userGroupIds")


class CredentialCreateRequest(BaseModel):
    """Request model for creating a credential."""

    model_config = ConfigDict(populate_by_name=True)

    username: str
    password: str


class CredentialUpdateRequest(BaseModel):
    """Request model for updating a credential password."""

    model_config = ConfigDict(populate_by_name=True)

    new_password: str = Field(..., alias="NewPassword")


class CredentialUserShareRequest(BaseModel):
    """Request model for sharing a credential with a user."""

    model_config = ConfigDict(populate_by_name=True)

    user_id: UserId = Field(..., alias="userId")


class CredentialUserGroupShareRequest(BaseModel):
    """Request model for sharing a credential with a user group."""

    model_config = ConfigDict(populate_by_name=True)

    user_group_id: UserGroupId = Field(..., alias="userGroupId")
