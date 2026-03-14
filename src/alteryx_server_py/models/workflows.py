"""
Workflow models for API.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .base import BaseApiModel
from .common import (
    ExecutionMode,
    WorkflowType,
)


class Workflow(BaseApiModel):
    """Workflow model representing an Alteryx workflow.

    Attributes:
        id: Unique workflow identifier
        name: Workflow name
        version_id: Current version identifier
        owner_id: Owner's user ID
        owner_email: Owner's email address
        workflow_type: Type of workflow (Standard/AnalyticApp/Macro)
        execution_mode: Execution mode (Safe/SemiSafe/Unrestricted)
        is_public: Whether workflow is publicly accessible
        is_ready_for_migration: Migration status
        run_count: Number of times workflow has been executed
        created_date: Creation timestamp
        updated_date: Last update timestamp
        description: Workflow description
        collection_ids: List of collection IDs workflow belongs to
        worker_tag: Tag for worker assignment
        can_download: Whether users can download workflow file
        has_questions: Whether workflow has analytic app questions
    """

    id: str = Field(..., alias="id")
    name: str
    version_id: Optional[str] = Field(None, alias="versionId")
    owner_id: str = Field(..., alias="ownerId")
    owner_email: Optional[str] = Field(None, alias="ownerEmail")
    workflow_type: WorkflowType = Field(..., alias="workflowType")
    execution_mode: ExecutionMode = Field(..., alias="executionMode")
    is_public: bool = Field(False, alias="isPublic")
    is_ready_for_migration: bool = Field(False, alias="isReadyForMigration")
    run_count: int = Field(0, alias="runCount")
    created_date: datetime = Field(..., alias="dateCreated")
    updated_date: Optional[datetime] = Field(None, alias="lastUpdated")
    description: Optional[str] = None
    collection_ids: List[str] = Field(default_factory=list, alias="collectionIds")
    worker_tag: Optional[str] = Field(None, alias="workerTag")
    can_download: Optional[bool] = Field(None, alias="canDownload")
    has_questions: Optional[bool] = Field(None, alias="hasQuestions")


class WorkflowUploadRequest(BaseModel):
    """Request model for publishing a new workflow.

    Attributes:
        name: Workflow name
        owner_id: Owner user ID
        is_public: Public visibility flag
        execution_mode: Execution mode
        worker_tag: Worker assignment tag
        comments: Version comments
        can_download: Allow download permission
    """

    name: str
    owner_id: str = Field(..., alias="ownerId")
    is_public: bool = Field(False, alias="isPublic")
    execution_mode: ExecutionMode = Field(ExecutionMode.SAFE, alias="executionMode")
    worker_tag: Optional[str] = Field(None, alias="workerTag")
    comments: Optional[str] = None
    can_download: Optional[bool] = Field(None, alias="canDownload")

    class Config:
        populate_by_name = True


class WorkflowUpdateRequest(BaseModel):
    """Request model for updating an existing workflow.

    Attributes:
        name: New workflow name
        is_public: Update public visibility
        execution_mode: Update execution mode
        worker_tag: Update worker assignment tag
        comments: Update comments
        can_download: Update download permission
    """

    name: Optional[str] = None
    is_public: Optional[bool] = Field(None, alias="isPublic")
    execution_mode: Optional[ExecutionMode] = Field(None, alias="executionMode")
    worker_tag: Optional[str] = Field(None, alias="workerTag")
    comments: Optional[str] = None
    can_download: Optional[bool] = Field(None, alias="canDownload")

    class Config:
        populate_by_name = True


class WorkflowQuestion(BaseModel):
    """Question from an analytic app workflow.

    Attributes:
        id: Question identifier
        name: Question name
        type: Question data type
        default_value: Default value
        description: Question description
        required: Whether question is required
    """

    id: str
    name: str
    type: str
    default_value: Optional[str] = Field(None, alias="defaultValue")
    description: Optional[str] = None
    required: bool = False


class WorkflowVersion(BaseModel):
    """Workflow version information.

    Attributes:
        id: Version identifier
        version_number: Sequential version number
        created_date: Version creation timestamp
        comments: Version comments
        owner_id: Creator user ID
    """

    id: str
    version_number: int = Field(..., alias="versionNumber")
    created_date: datetime = Field(..., alias="dateCreated")
    comments: Optional[str] = None
    owner_id: str = Field(..., alias="ownerId")

    class Config:
        populate_by_name = True
