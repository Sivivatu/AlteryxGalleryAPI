from __future__ import annotations

from enum import Enum
from typing import NewType, Optional

from pydantic import Field

from .base import BaseApiModel

WorkflowId = NewType("WorkflowId", str)
UserId = NewType("UserId", str)
SubscriptionId = NewType("SubscriptionId", str)


class ExecutionMode(str, Enum):
    SAFE = "Safe"
    SEMISAFE = "SemiSafe"
    STANDARD = "Standard"


class CredentialType(str, Enum):
    DEFAULT = "Default"
    REQUIRED = "Required"
    SPECIFIC = "Specific"


class ApiError(BaseApiModel):
    code: Optional[str] = None
    message: str = Field(..., alias="Message")
