"""Collection resource for API operations."""

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from ..exceptions import CollectionNotFoundError, NotFoundError, ValidationError
from ..models import (
    Collection,
    CollectionPermission,
    CollectionPermissionUpdateRequest,
    CollectionShareGroupRequest,
    CollectionShareUserRequest,
    CollectionUpdateRequest,
    CollectionWorkflowRequest,
)
from ..models.collections import CollectionCreateRequest
from ..models.common import CollectionId, UserGroupId, UserId, WorkflowId
from ._base import _BaseResource

if TYPE_CHECKING:
    from ..async_client import AsyncAlteryxClient
    from ..client import AlteryxClient

logger = logging.getLogger(__name__)


def _coerce_collection_list(response: object) -> list[Collection]:
    if isinstance(response, list):
        return [Collection.model_validate(item) for item in response]
    if isinstance(response, dict) and "collections" in response:
        return [Collection.model_validate(item) for item in response["collections"]]
    if isinstance(response, dict):
        return [Collection.model_validate(response)]
    return []


class CollectionResource(_BaseResource):
    """Resource for collection operations."""

    _client: "AlteryxClient"

    def list(self, view: Optional[str] = None) -> list[Collection]:
        """List accessible collections."""
        params = {"view": view} if view else None
        response = self._client._request("GET", "collections", params=params)
        return _coerce_collection_list(response)

    def get(self, collection_id: CollectionId) -> Collection:
        """Get a collection by ID."""
        try:
            response = self._client._request("GET", f"collections/{collection_id}")
            return Collection.model_validate(response)
        except NotFoundError as exc:
            raise CollectionNotFoundError(collection_id) from exc

    def create(self, name: str) -> Collection:
        """Create a collection."""
        request = CollectionCreateRequest(name=name)
        response = self._client._request(
            "POST",
            "collections",
            data=request.model_dump(by_alias=True, exclude_none=True),
        )
        return Collection.model_validate(response)

    def update(self, collection_id: CollectionId, name: str, owner_id: UserId) -> Collection:
        """Update collection name and owner."""
        request = CollectionUpdateRequest(name=name, owner_id=owner_id)
        try:
            response = self._client._request(
                "PUT",
                f"collections/{collection_id}",
                data=request.model_dump(by_alias=True, exclude_none=True),
            )
            return Collection.model_validate(response)
        except NotFoundError as exc:
            raise CollectionNotFoundError(collection_id) from exc

    def delete(self, collection_id: CollectionId, force_delete: bool = False) -> None:
        """Delete a collection."""
        params = {"forceDelete": str(force_delete).lower()} if force_delete else None
        try:
            self._client._request("DELETE", f"collections/{collection_id}", params=params)
        except NotFoundError as exc:
            raise CollectionNotFoundError(collection_id) from exc

    def add_workflow(self, collection_id: CollectionId, workflow_id: WorkflowId) -> Collection:
        """Add a workflow to a collection."""
        request = CollectionWorkflowRequest(workflow_id=workflow_id)
        try:
            response = self._client._request(
                "POST",
                f"collections/{collection_id}/workflows",
                data=request.model_dump(by_alias=True, exclude_none=True),
            )
        except NotFoundError as exc:
            raise CollectionNotFoundError(collection_id) from exc

        if isinstance(response, dict):
            return Collection.model_validate(response)
        return self.get(collection_id)

    def remove_workflow(self, collection_id: CollectionId, workflow_id: WorkflowId) -> None:
        """Remove a workflow from a collection."""
        try:
            self._client._request("DELETE", f"collections/{collection_id}/workflows/{workflow_id}")
        except NotFoundError as exc:
            raise CollectionNotFoundError(collection_id) from exc

    def add_user(
        self,
        collection_id: CollectionId,
        user_id: UserId,
        permissions: CollectionPermission,
        expiration_date: Optional[datetime] = None,
    ) -> Collection:
        """Add a user to a collection with permissions."""
        request = CollectionShareUserRequest(
            user_id=user_id,
            expiration_date=expiration_date,
            permissions=permissions,
        )
        try:
            response = self._client._request(
                "POST",
                f"collections/{collection_id}/users",
                data=request.model_dump(by_alias=True, exclude_none=True),
            )
        except NotFoundError as exc:
            raise CollectionNotFoundError(collection_id) from exc

        if isinstance(response, dict):
            return Collection.model_validate(response)
        return self.get(collection_id)

    def add_user_group(
        self,
        collection_id: CollectionId,
        user_group_id: UserGroupId,
        permissions: CollectionPermission,
        expiration_date: Optional[datetime] = None,
    ) -> Collection:
        """Add a user group to a collection with permissions."""
        request = CollectionShareGroupRequest(
            user_group_id=user_group_id,
            expiration_date=expiration_date,
            permissions=permissions,
        )
        try:
            response = self._client._request(
                "POST",
                f"collections/{collection_id}/userGroups",
                data=request.model_dump(by_alias=True, exclude_none=True),
            )
        except NotFoundError as exc:
            raise CollectionNotFoundError(collection_id) from exc

        if isinstance(response, dict):
            return Collection.model_validate(response)
        return self.get(collection_id)

    def set_permissions(
        self,
        collection_id: CollectionId,
        permissions: CollectionPermission,
        user_id: Optional[UserId] = None,
        user_group_id: Optional[UserGroupId] = None,
        expiration_date: Optional[datetime] = None,
    ) -> Collection:
        """Update collection permissions for a user or user group."""
        if bool(user_id) == bool(user_group_id):
            raise ValidationError("Provide exactly one of user_id or user_group_id.")

        request = CollectionPermissionUpdateRequest(
            expiration_date=expiration_date,
            permissions=permissions,
        )
        if user_id:
            endpoint = f"collections/{collection_id}/users/{user_id}/permissions"
        else:
            endpoint = f"collections/{collection_id}/userGroups/{user_group_id}/permissions"

        try:
            response = self._client._request(
                "PUT",
                endpoint,
                data=request.model_dump(by_alias=True, exclude_none=True),
            )
        except NotFoundError as exc:
            raise CollectionNotFoundError(collection_id) from exc

        if isinstance(response, dict):
            return Collection.model_validate(response)
        return self.get(collection_id)


class AsyncCollectionResource(_BaseResource):
    """Asynchronous collection resource."""

    _client: "AsyncAlteryxClient"

    async def list(self, view: Optional[str] = None) -> list[Collection]:
        """List accessible collections."""
        params = {"view": view} if view else None
        response = await self._client._request("GET", "collections", params=params)
        return _coerce_collection_list(response)

    async def get(self, collection_id: CollectionId) -> Collection:
        """Get a collection by ID."""
        try:
            response = await self._client._request("GET", f"collections/{collection_id}")
            return Collection.model_validate(response)
        except NotFoundError as exc:
            raise CollectionNotFoundError(collection_id) from exc

    async def create(self, name: str) -> Collection:
        """Create a collection."""
        request = CollectionCreateRequest(name=name)
        response = await self._client._request(
            "POST",
            "collections",
            data=request.model_dump(by_alias=True, exclude_none=True),
        )
        return Collection.model_validate(response)

    async def update(self, collection_id: CollectionId, name: str, owner_id: UserId) -> Collection:
        """Update collection name and owner."""
        request = CollectionUpdateRequest(name=name, owner_id=owner_id)
        try:
            response = await self._client._request(
                "PUT",
                f"collections/{collection_id}",
                data=request.model_dump(by_alias=True, exclude_none=True),
            )
            return Collection.model_validate(response)
        except NotFoundError as exc:
            raise CollectionNotFoundError(collection_id) from exc

    async def delete(self, collection_id: CollectionId, force_delete: bool = False) -> None:
        """Delete a collection."""
        params = {"forceDelete": str(force_delete).lower()} if force_delete else None
        try:
            await self._client._request("DELETE", f"collections/{collection_id}", params=params)
        except NotFoundError as exc:
            raise CollectionNotFoundError(collection_id) from exc

    async def add_workflow(self, collection_id: CollectionId, workflow_id: WorkflowId) -> Collection:
        """Add a workflow to a collection."""
        request = CollectionWorkflowRequest(workflow_id=workflow_id)
        try:
            response = await self._client._request(
                "POST",
                f"collections/{collection_id}/workflows",
                data=request.model_dump(by_alias=True, exclude_none=True),
            )
        except NotFoundError as exc:
            raise CollectionNotFoundError(collection_id) from exc

        if isinstance(response, dict):
            return Collection.model_validate(response)
        return await self.get(collection_id)

    async def remove_workflow(self, collection_id: CollectionId, workflow_id: WorkflowId) -> None:
        """Remove a workflow from a collection."""
        try:
            await self._client._request("DELETE", f"collections/{collection_id}/workflows/{workflow_id}")
        except NotFoundError as exc:
            raise CollectionNotFoundError(collection_id) from exc

    async def add_user(
        self,
        collection_id: CollectionId,
        user_id: UserId,
        permissions: CollectionPermission,
        expiration_date: Optional[datetime] = None,
    ) -> Collection:
        """Add a user to a collection with permissions."""
        request = CollectionShareUserRequest(
            user_id=user_id,
            expiration_date=expiration_date,
            permissions=permissions,
        )
        try:
            response = await self._client._request(
                "POST",
                f"collections/{collection_id}/users",
                data=request.model_dump(by_alias=True, exclude_none=True),
            )
        except NotFoundError as exc:
            raise CollectionNotFoundError(collection_id) from exc

        if isinstance(response, dict):
            return Collection.model_validate(response)
        return await self.get(collection_id)

    async def add_user_group(
        self,
        collection_id: CollectionId,
        user_group_id: UserGroupId,
        permissions: CollectionPermission,
        expiration_date: Optional[datetime] = None,
    ) -> Collection:
        """Add a user group to a collection with permissions."""
        request = CollectionShareGroupRequest(
            user_group_id=user_group_id,
            expiration_date=expiration_date,
            permissions=permissions,
        )
        try:
            response = await self._client._request(
                "POST",
                f"collections/{collection_id}/userGroups",
                data=request.model_dump(by_alias=True, exclude_none=True),
            )
        except NotFoundError as exc:
            raise CollectionNotFoundError(collection_id) from exc

        if isinstance(response, dict):
            return Collection.model_validate(response)
        return await self.get(collection_id)

    async def set_permissions(
        self,
        collection_id: CollectionId,
        permissions: CollectionPermission,
        user_id: Optional[UserId] = None,
        user_group_id: Optional[UserGroupId] = None,
        expiration_date: Optional[datetime] = None,
    ) -> Collection:
        """Update collection permissions for a user or user group."""
        if bool(user_id) == bool(user_group_id):
            raise ValidationError("Provide exactly one of user_id or user_group_id.")

        request = CollectionPermissionUpdateRequest(
            expiration_date=expiration_date,
            permissions=permissions,
        )
        if user_id:
            endpoint = f"collections/{collection_id}/users/{user_id}/permissions"
        else:
            endpoint = f"collections/{collection_id}/userGroups/{user_group_id}/permissions"

        try:
            response = await self._client._request(
                "PUT",
                endpoint,
                data=request.model_dump(by_alias=True, exclude_none=True),
            )
        except NotFoundError as exc:
            raise CollectionNotFoundError(collection_id) from exc

        if isinstance(response, dict):
            return Collection.model_validate(response)
        return await self.get(collection_id)