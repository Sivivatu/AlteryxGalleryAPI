"""
API resource modules.
"""

from ._base import _BaseResource
from .collections import AsyncCollectionResource, CollectionResource
from .credentials import AsyncCredentialResource, CredentialResource
from .jobs import AsyncJobResource, JobResource
from .schedules import AsyncScheduleResource, ScheduleResource
from .server import AsyncServerResource, ServerResource
from .user_groups import AsyncUserGroupResource, UserGroupResource
from .users import AsyncUserResource, UserResource
from .workflows import WorkflowResource

__all__ = [
    "_BaseResource",
    "WorkflowResource",
    "CollectionResource",
    "AsyncCollectionResource",
    "CredentialResource",
    "AsyncCredentialResource",
    "JobResource",
    "AsyncJobResource",
    "ScheduleResource",
    "AsyncScheduleResource",
    "ServerResource",
    "AsyncServerResource",
    "UserResource",
    "AsyncUserResource",
    "UserGroupResource",
    "AsyncUserGroupResource",
]
