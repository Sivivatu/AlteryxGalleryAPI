"""
User and user group models for API.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .base import BaseApiModel
from .common import (
    UserGroupId,
    UserId,
    UserRole,
)


class User(BaseApiModel):
    """User model representing an Alteryx Server user.

    Attributes:
        id: Unique user identifier
        email: User's email address
        first_name: User's first name
        last_name: User's last name
        role: User's role on the server
        active: Whether the user is active
        default_worker_tag: Default worker tag assignment
        time_zone: User's preferred time zone
        is_api_enabled: Whether API access is enabled
        created_date: Account creation timestamp
        updated_date: Last update timestamp
        last_login_date: Last login timestamp
    """

    id: UserId
    email: str
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    role: UserRole = Field(UserRole.VIEWER)
    active: bool = True
    default_worker_tag: Optional[str] = Field(None, alias="defaultWorkerTag")
    time_zone: Optional[str] = Field(None, alias="timeZone")
    is_api_enabled: Optional[bool] = Field(None, alias="isApiEnabled")
    created_date: Optional[datetime] = Field(None, alias="dateCreated")
    updated_date: Optional[datetime] = Field(None, alias="lastUpdated")
    last_login_date: Optional[datetime] = Field(None, alias="lastLoginDate")


class UserCreateRequest(BaseModel):
    """Request model for creating a new user.

    Attributes:
        email: User's email address
        first_name: User's first name
        last_name: User's last name
        role: User's role on the server
        default_worker_tag: Default worker tag assignment
        time_zone: User's preferred time zone
    """

    model_config = ConfigDict(populate_by_name=True)

    email: str
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    role: UserRole = Field(UserRole.VIEWER)
    default_worker_tag: Optional[str] = Field(None, alias="defaultWorkerTag")
    time_zone: Optional[str] = Field(None, alias="timeZone")


class UserUpdateRequest(BaseModel):
    """Request model for updating an existing user.

    Attributes:
        first_name: User's first name
        last_name: User's last name
        role: User's role on the server
        active: Whether the user is active
        default_worker_tag: Default worker tag assignment
        time_zone: User's preferred time zone
    """

    model_config = ConfigDict(populate_by_name=True)

    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    role: Optional[UserRole] = None
    active: Optional[bool] = None
    default_worker_tag: Optional[str] = Field(None, alias="defaultWorkerTag")
    time_zone: Optional[str] = Field(None, alias="timeZone")


class UserGroup(BaseApiModel):
    """User group model representing an Alteryx Server user group.

    Attributes:
        id: Unique group identifier
        name: Group name
        role: Group role on the server
        description: Group description
        member_ids: List of user IDs in the group
        created_date: Group creation timestamp
        updated_date: Last update timestamp
    """

    id: UserGroupId
    name: str
    role: Optional[UserRole] = None
    description: Optional[str] = None
    member_ids: List[UserId] = Field(default_factory=list, alias="memberIds")
    created_date: Optional[datetime] = Field(None, alias="dateCreated")
    updated_date: Optional[datetime] = Field(None, alias="lastUpdated")


class UserGroupCreateRequest(BaseModel):
    """Request model for creating a new user group.

    Attributes:
        name: Group name
        role: Group role on the server
        description: Group description
    """

    model_config = ConfigDict(populate_by_name=True)

    name: str
    role: Optional[UserRole] = None
    description: Optional[str] = None


class UserGroupUpdateRequest(BaseModel):
    """Request model for updating an existing user group.

    Attributes:
        name: Group name
        role: Group role on the server
        description: Group description
    """

    model_config = ConfigDict(populate_by_name=True)

    name: Optional[str] = None
    role: Optional[UserRole] = None
    description: Optional[str] = None
