"""
Job models for API.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .base import BaseApiModel
from .common import (
    JobId,
    JobPriority,
    JobStatus,
)


class JobOutput(BaseModel):
    """Output file from a completed job.

    Attributes:
        id: Output identifier
        name: Output file name
        format: File format (e.g., "CSV", "Excel")
        size: File size in bytes
    """

    id: str
    name: str
    format: str
    size: Optional[int] = None


class JobMessage(BaseModel):
    """Execution message from a job.

    Attributes:
        message: Message text
        timestamp: Message timestamp
        level: Message level (Info/Warning/Error)
    """

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    message: str
    timestamp: Optional[datetime] = None
    level: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def _normalize_legacy_payload(cls, data: object) -> object:
        """Normalize older job message payloads.

        Args:
            data: Raw response payload.

        Returns:
            object: Normalized payload for model validation.
        """

        if not isinstance(data, dict):
            return data

        normalized = dict(data)
        if "message" not in normalized and "text" in normalized:
            normalized["message"] = normalized["text"]
        if "level" not in normalized and "status" in normalized:
            normalized["level"] = str(normalized["status"])

        return normalized


class Job(BaseApiModel):
    """Job representing a workflow execution.

    Attributes:
        id: Unique job identifier
        workflow_id: Parent workflow ID
        status: Job status (Queued/Running/Completed/Error/Cancelled)
        disposition: Job completion disposition
        outputs: List of output files
        messages: List of execution messages
        priority: Job execution priority
        worker_tag: Worker assignment tag
        run_as: User account job ran as
        created_date: Job creation timestamp
        queued_date: Job queued timestamp
        start_date: Job start timestamp
        end_date: Job completion timestamp
        duration_seconds: Total job duration
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="ignore",
        populate_by_name=True,
    )

    id: JobId
    workflow_id: str = Field(..., alias="workflowId")
    status: JobStatus
    disposition: Optional[str] = None
    outputs: List[JobOutput] = Field(default_factory=list)
    messages: List[JobMessage] = Field(default_factory=list)
    priority: JobPriority = Field(JobPriority.DEFAULT)
    worker_tag: Optional[str] = Field(None, alias="workerTag")
    run_as: Optional[str] = Field(None, alias="runAs")
    created_date: datetime = Field(..., alias="createDate")
    queued_date: Optional[datetime] = Field(None, alias="queuedDate")
    start_date: Optional[datetime] = Field(None, alias="startDate")
    end_date: Optional[datetime] = Field(None, alias="endDate")
    duration_seconds: Optional[float] = Field(None, alias="durationSeconds")

    @model_validator(mode="before")
    @classmethod
    def _normalize_legacy_payload(cls, data: object) -> object:
        """Normalize older job payloads into the current model shape.

        Args:
            data: Raw response payload.

        Returns:
            object: Normalized payload for model validation.
        """

        if not isinstance(data, dict):
            return data

        normalized = dict(data)
        if "workflowId" not in normalized and "appId" in normalized:
            normalized["workflowId"] = normalized["appId"]
        if "createDate" not in normalized and "createDateTime" in normalized:
            normalized["createDate"] = normalized["createDateTime"]

        return normalized


class JobRunRequest(BaseModel):
    """Request model for running a workflow job.

    Attributes:
        questions: Answers to analytic app questions (name -> value mapping)
        priority: Job execution priority
        worker_tag: Worker assignment tag
    """

    model_config = ConfigDict(populate_by_name=True)

    questions: Optional[Dict[str, Any]] = None
    priority: JobPriority = Field(JobPriority.DEFAULT)
    worker_tag: Optional[str] = Field(None, alias="workerTag")
