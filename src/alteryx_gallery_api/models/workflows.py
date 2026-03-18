from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import ConfigDict, Field

from .base import BaseApiModel
from .common import (
    CredentialType,
    ExecutionMode,
    SubscriptionId,
    WorkflowId,
)


class PublishWorkflowRequest(BaseApiModel):
    name: str
    owner_id: SubscriptionId = Field(..., alias="ownerId")
    is_public: bool = Field(default=False, alias="isPublic")
    others_may_download: bool = Field(default=True, alias="othersMayDownload")
    others_can_execute: bool = Field(default=True, alias="othersCanExecute")
    execution_mode: ExecutionMode = Field(default=ExecutionMode.STANDARD, alias="executionMode")
    workflow_credential_type: CredentialType = Field(default=CredentialType.DEFAULT, alias="workflowCredentialType")
    # Extra optional fields commonly supported by Gallery:
    is_ready_for_migration: Optional[bool] = Field(default=None, alias="isReadyForMigration")
    # Add other properties as you discover them in responses/spec

    def to_payload(self) -> Dict[str, Any]:
        return self.model_dump(by_alias=True, exclude_none=True)


class GetWorkflowRequest(BaseApiModel):
    id: Optional[WorkflowId] = Field(default=None, alias="id")
    name: Optional[str] = Field(default=None, alias="name")
    owner_id: Optional[SubscriptionId] = Field(default=None, alias="ownerId")


class ViewType(str, Enum):
    DEFAULT = "Default"
    FULL = "Full"


class Workflow(BaseApiModel):
    # Accept additional properties from the API payload to remain forward-compatible
    model_config = ConfigDict(extra="allow")

    id: WorkflowId = Field(..., alias="id")
    source_app_id: str = Field(..., alias="sourceAppId")
    name: str = Field(..., alias="name")
    owner_id: SubscriptionId = Field(..., alias="ownerId")
    date_created: datetime = Field(..., alias="dateCreated")
    published_version_number: int = Field(..., alias="publishedVersionNumber")
    is_amp: bool = Field(..., alias="isAmp")
    execution_mode: ExecutionMode = Field(..., alias="executionMode")


class WorkflowListResponse(BaseApiModel):
    total: Optional[int] = None
    workflows: List[Workflow] = Field(default_factory=list, alias="workflows")
