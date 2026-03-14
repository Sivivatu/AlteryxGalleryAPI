"""
Pydantic models for API requests and responses.
"""

from .base import BaseApiModel
from .common import (
    WorkflowId,
    UserId,
    SubscriptionId,
    JobId,
    ScheduleId,
    CollectionId,
    CredentialId,
    UserGroupId,
    ExecutionMode,
    WorkflowType,
    JobStatus,
    JobPriority,
    CredentialType,
    ApiError,
)
from .auth import TokenResponse
from .workflows import (
    Workflow,
    WorkflowUploadRequest,
    WorkflowUpdateRequest,
    WorkflowQuestion,
    WorkflowVersion,
)
from .jobs import (
    Job,
    JobOutput,
    JobMessage,
    JobRunRequest,
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
]
