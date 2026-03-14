"""
Alteryx Server API Python Client.

A modern, type-safe Python wrapper for the Alteryx Server V3 API
with support for both synchronous and asynchronous operations.

Example:
    from alteryx_server_py import AlteryxClient

    client = AlteryxClient.from_env()
    workflows = client.workflows.list()
    for workflow in workflows:
        print(workflow.name)
"""

from .client import AlteryxClient
from .async_client import AsyncAlteryxClient
from .config import ClientConfig, from_env as config_from_env
from .exceptions import (
    AlteryxError,
    ConfigurationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    WorkflowNotFoundError,
    JobNotFoundError,
    ValidationError,
    RateLimitError,
    ServerError,
    JobExecutionError,
    TimeoutError,
)

__version__ = "0.2.0"
__all__ = [
    # Clients
    "AlteryxClient",
    "AsyncAlteryxClient",
    # Config
    "ClientConfig",
    "config_from_env",
    # Exceptions
    "AlteryxError",
    "ConfigurationError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "WorkflowNotFoundError",
    "JobNotFoundError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
    "JobExecutionError",
    "TimeoutError",
]
