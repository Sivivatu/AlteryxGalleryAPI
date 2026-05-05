"""
Pydantic models for API requests and responses.
"""

from .auth import TokenResponse
from .base import BaseApiModel
from .collections import (
    Collection,
    CollectionCreateRequest,
    CollectionPermission,
    CollectionPermissionUpdateRequest,
    CollectionShareGroupRequest,
    CollectionShareUserRequest,
    CollectionUpdateRequest,
    CollectionWorkflowRequest,
)
from .common import (
    ApiError,
    CollectionId,
    CredentialId,
    CredentialType,
    ExecutionMode,
    JobId,
    JobPriority,
    JobStatus,
    ScheduleFrequency,
    ScheduleId,
    ScheduleStatus,
    SubscriptionId,
    UserGroupId,
    UserId,
    UserRole,
    WorkflowId,
    WorkflowType,
)
from .credentials import (
    Credential,
    CredentialCreateRequest,
    CredentialUpdateRequest,
    CredentialUserGroupShareRequest,
    CredentialUserShareRequest,
)
from .jobs import (
    Job,
    JobMessage,
    JobOutput,
    JobRunRequest,
)
from .schedules import (
    Schedule,
    ScheduleCreateRequest,
    ScheduleUpdateRequest,
)
from .server import ServerInfo, ServerSettings
from .users import (
    User,
    UserCreateRequest,
    UserGroup,
    UserGroupCreateRequest,
    UserGroupUpdateRequest,
    UserUpdateRequest,
)
from .workflows import (
    Workflow,
    WorkflowQuestion,
    WorkflowUpdateRequest,
    WorkflowUploadRequest,
    WorkflowVersion,
)

__all__ = [
    # Base
    "BaseApiModel",
    # Common types
    "WorkflowId",
    "UserId",
    "SubscriptionId",
    "JobId",
    "ScheduleId",
    "CollectionId",
    "CredentialId",
    "UserGroupId",
    # Enums
    "ExecutionMode",
    "WorkflowType",
    "JobStatus",
    "JobPriority",
    "CredentialType",
    "ScheduleFrequency",
    "ScheduleStatus",
    "UserRole",
    "ApiError",
    # Auth models
    "TokenResponse",
    # Collection models
    "Collection",
    "CollectionPermission",
    "CollectionCreateRequest",
    "CollectionUpdateRequest",
    "CollectionShareUserRequest",
    "CollectionShareGroupRequest",
    "CollectionPermissionUpdateRequest",
    "CollectionWorkflowRequest",
    # Credential models
    "Credential",
    "CredentialCreateRequest",
    "CredentialUpdateRequest",
    "CredentialUserShareRequest",
    "CredentialUserGroupShareRequest",
    # Workflow models
    "Workflow",
    "WorkflowUploadRequest",
    "WorkflowUpdateRequest",
    "WorkflowQuestion",
    "WorkflowVersion",
    # Job models
    "Job",
    "JobOutput",
    "JobMessage",
    "JobRunRequest",
    # Schedule models
    "Schedule",
    "ScheduleCreateRequest",
    "ScheduleUpdateRequest",
    # User models
    "User",
    "UserCreateRequest",
    "UserUpdateRequest",
    "UserGroup",
    "UserGroupCreateRequest",
    "UserGroupUpdateRequest",
    # Server models
    "ServerInfo",
    "ServerSettings",
]
