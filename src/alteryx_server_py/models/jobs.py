"""
Job models for API.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from .base import BaseApiModel
from .common import (
    JobId,
    JobStatus,
    JobPriority,
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

    message: str
    timestamp: Optional[datetime] = None
    level: Optional[str] = None


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


class JobRunRequest(BaseModel):
    """Request model for running a workflow job.

    Attributes:
        questions: Answers to analytic app questions (name -> value mapping)
        priority: Job execution priority
        worker_tag: Worker assignment tag
    """

    questions: Optional[Dict[str, Any]] = None
    priority: JobPriority = Field(JobPriority.DEFAULT)
    worker_tag: Optional[str] = Field(None, alias="workerTag")

    class Config:
        populate_by_name = True
