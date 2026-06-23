"""
Workflow models for API.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

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

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="ignore",
        populate_by_name=True,
    )

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

    @model_validator(mode="before")
    @classmethod
    def _normalize_legacy_payload(cls, data: object) -> object:
        """Normalize older workflow payloads into the current V3 model shape.

        Some live servers return legacy workflow responses where:
        - `workflowType` is omitted
        - `executionMode` contains values like `Standard` or `App`
        - extra fields appear that are not part of the V3 model

        Args:
            data: Raw response payload.

        Returns:
            object: Normalized payload for model validation.
        """

        if not isinstance(data, dict):
            return data

        normalized = dict(data)
        execution_mode = normalized.get("executionMode")
        workflow_type = normalized.get("workflowType")
        package_workflow_type = normalized.get("packageWorkflowType")

        workflow_type_mapping = {
            "Workflow": "Standard",
            "Standard": "Standard",
            "App": "AnalyticApp",
            "AnalyticApp": "AnalyticApp",
            "Macro": "Macro",
        }
        valid_execution_modes = {mode.value for mode in ExecutionMode}

        if workflow_type is None:
            legacy_workflow_type = package_workflow_type or execution_mode
            normalized["workflowType"] = workflow_type_mapping.get(legacy_workflow_type, "Standard")

        if execution_mode not in valid_execution_modes:
            normalized["executionMode"] = "Safe"

        return normalized


class WorkflowUploadRequest(BaseModel):
    """Request model for publishing a new workflow.

    Attributes:
        name: Workflow name
        owner_id: Owner user ID
        is_public: Public visibility flag
        is_ready_for_migration: Migration readiness flag required by some servers
        others_may_download: Whether other users may download the workflow package
        others_can_execute: Whether other users may execute the workflow
        execution_mode: Execution mode
        workflow_credential_type: Workflow credential mode
        worker_tag: Worker assignment tag
        comments: Version comments
        can_download: Allow download permission
    """

    model_config = ConfigDict(populate_by_name=True)

    name: str
    owner_id: str = Field(..., alias="ownerId")
    is_public: bool = Field(False, alias="isPublic")
    is_ready_for_migration: bool = Field(False, alias="isReadyForMigration")
    others_may_download: bool = Field(True, alias="othersMayDownload")
    others_can_execute: bool = Field(True, alias="othersCanExecute")
    execution_mode: ExecutionMode = Field(ExecutionMode.SAFE, alias="executionMode")
    workflow_credential_type: str = Field("Default", alias="workflowCredentialType")
    worker_tag: Optional[str] = Field(None, alias="workerTag")
    comments: Optional[str] = None
    can_download: Optional[bool] = Field(None, alias="canDownload")


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

    model_config = ConfigDict(populate_by_name=True)

    name: Optional[str] = None
    is_public: Optional[bool] = Field(None, alias="isPublic")
    execution_mode: Optional[ExecutionMode] = Field(None, alias="executionMode")
    worker_tag: Optional[str] = Field(None, alias="workerTag")
    comments: Optional[str] = None
    can_download: Optional[bool] = Field(None, alias="canDownload")


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

    model_config = ConfigDict(populate_by_name=True)

    id: str
    version_number: int = Field(..., alias="versionNumber")
    created_date: datetime = Field(..., alias="dateCreated")
    comments: Optional[str] = None
    owner_id: str = Field(..., alias="ownerId")
