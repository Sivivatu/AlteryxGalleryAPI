"""
Alteryx Gallery API Wrapper

A Python client for interacting with the Alteryx Server API (Gallery API).
"""

__version__ = "0.1.0"

from .client import AlteryxClient
from .exceptions import (
    AlteryxAPIError,
    AuthenticationError,
    JobExecutionError,
    WorkflowNotFoundError,
)

__all__ = [
    "AlteryxAPIError",
    "AlteryxClient",
    "AuthenticationError",
    "JobExecutionError",
    "WorkflowNotFoundError",
]
