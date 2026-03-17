"""
Schedule models for API.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .base import BaseApiModel
from .common import (
    ScheduleFrequency,
    ScheduleId,
    ScheduleStatus,
    WorkflowId,
)


class Schedule(BaseApiModel):
    """Schedule model representing a workflow schedule.

    Attributes:
        id: Unique schedule identifier
        workflow_id: Associated workflow ID
        name: Schedule name
        owner_id: Owner's user ID
        comment: Schedule description/comment
        frequency: Execution frequency (Once/Hourly/Daily/Weekly/Monthly/Custom)
        status: Schedule status (Active/Inactive)
        enabled: Whether schedule is enabled
        iteration: Iteration details for recurring schedules
        start_date: Schedule start timestamp
        end_date: Schedule end timestamp
        last_run_date: Last execution timestamp
        next_run_date: Next scheduled execution timestamp
        created_date: Creation timestamp
        updated_date: Last update timestamp
    """

    id: ScheduleId
    workflow_id: WorkflowId = Field(..., alias="workflowId")
    name: str
    owner_id: str = Field(..., alias="ownerId")
    comment: Optional[str] = None
    frequency: ScheduleFrequency = Field(ScheduleFrequency.ONCE)
    status: ScheduleStatus = Field(ScheduleStatus.ACTIVE)
    enabled: bool = True
    iteration: Optional[str] = None
    start_date: Optional[datetime] = Field(None, alias="startDate")
    end_date: Optional[datetime] = Field(None, alias="endDate")
    last_run_date: Optional[datetime] = Field(None, alias="lastRunDate")
    next_run_date: Optional[datetime] = Field(None, alias="nextRunDate")
    created_date: Optional[datetime] = Field(None, alias="dateCreated")
    updated_date: Optional[datetime] = Field(None, alias="lastUpdated")


class ScheduleCreateRequest(BaseModel):
    """Request model for creating a new schedule.

    Attributes:
        workflow_id: Associated workflow ID
        name: Schedule name
        owner_id: Owner's user ID
        comment: Schedule description/comment
        frequency: Execution frequency
        start_date: Schedule start timestamp
        end_date: Schedule end timestamp
        iteration: Iteration details for recurring schedules
    """

    model_config = ConfigDict(populate_by_name=True)

    workflow_id: WorkflowId = Field(..., alias="workflowId")
    name: str
    owner_id: str = Field(..., alias="ownerId")
    comment: Optional[str] = None
    frequency: ScheduleFrequency = Field(ScheduleFrequency.ONCE)
    start_date: Optional[datetime] = Field(None, alias="startDate")
    end_date: Optional[datetime] = Field(None, alias="endDate")
    iteration: Optional[str] = None


class ScheduleUpdateRequest(BaseModel):
    """Request model for updating an existing schedule.

    Attributes:
        name: Schedule name
        comment: Schedule description/comment
        frequency: Execution frequency
        start_date: Schedule start timestamp
        end_date: Schedule end timestamp
        iteration: Iteration details for recurring schedules
        enabled: Whether schedule is enabled
    """

    model_config = ConfigDict(populate_by_name=True)

    name: Optional[str] = None
    comment: Optional[str] = None
    frequency: Optional[ScheduleFrequency] = None
    start_date: Optional[datetime] = Field(None, alias="startDate")
    end_date: Optional[datetime] = Field(None, alias="endDate")
    iteration: Optional[str] = None
    enabled: Optional[bool] = None
