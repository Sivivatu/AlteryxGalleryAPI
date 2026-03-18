"""
Pydantic models for API requests and responses.
"""

from .auth import TokenResponse
from .base import BaseApiModel
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
]
