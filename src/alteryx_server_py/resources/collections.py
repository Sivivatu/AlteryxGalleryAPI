"""Collection resource for API operations."""

import logging
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

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


def _coerce_collection_list(response: object) -> List[Collection]:
    """Normalize collection list responses into model instances.

    Args:
        response: Raw response payload returned by the API client.

    Returns:
        List[Collection]: Parsed collection models.
    """
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

    def list(self, view: Optional[str] = None) -> List[Collection]:
        """List collections visible to the current caller.

        Args:
            view: Optional API-specific collection view filter.

        Returns:
            List[Collection]: Matching collection models.
        """
        params = {"view": view} if view else None
        response = self._client._request("GET", "collections", params=params)
        return _coerce_collection_list(response)

    def get(self, collection_id: CollectionId) -> Collection:
        """Retrieve a collection by identifier.

        Args:
            collection_id: Collection identifier.

        Returns:
            Collection: Resolved collection model.

        Raises:
            CollectionNotFoundError: If the collection does not exist.
        """
        try:
            response = self._client._request("GET", f"collections/{collection_id}")
            return Collection.model_validate(response)
        except NotFoundError as exc:
            raise CollectionNotFoundError(collection_id) from exc

    def create(self, name: str) -> Collection:
        """Create a collection.

        Args:
            name: Collection display name.

        Returns:
            Collection: Newly created collection model.
        """
        request = CollectionCreateRequest(name=name)
        response = self._client._request(
            "POST",
            "collections",
            json_data=request.model_dump(by_alias=True, exclude_none=True),
        )
        return Collection.model_validate(response)

    def update(self, collection_id: CollectionId, name: str, owner_id: UserId) -> Collection:
        """Update collection name and owner.

        Args:
            collection_id: Collection identifier.
            name: Updated collection name.
            owner_id: New owner user identifier.

        Returns:
            Collection: Updated collection model.

        Raises:
            CollectionNotFoundError: If the collection does not exist.
        """
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
        """Delete a collection.

        Args:
            collection_id: Collection identifier.
            force_delete: Whether to force deletion when supported by the API.

        Raises:
            CollectionNotFoundError: If the collection does not exist.
        """
        params = {"forceDelete": str(force_delete).lower()} if force_delete else None
        try:
            self._client._request("DELETE", f"collections/{collection_id}", params=params)
        except NotFoundError as exc:
            raise CollectionNotFoundError(collection_id) from exc

    def add_workflow(self, collection_id: CollectionId, workflow_id: WorkflowId) -> Collection:
        """Add a workflow to a collection.

        Args:
            collection_id: Collection identifier.
            workflow_id: Workflow identifier to add.

        Returns:
            Collection: Updated collection model.

        Raises:
            CollectionNotFoundError: If the collection does not exist.
        """
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
        """Remove a workflow from a collection.

        Args:
            collection_id: Collection identifier.
            workflow_id: Workflow identifier to remove.

        Raises:
            CollectionNotFoundError: If the collection does not exist.
        """
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
        """Add a user to a collection with permissions.

        Args:
            collection_id: Collection identifier.
            user_id: User identifier to share with.
            permissions: Permission set to apply.
            expiration_date: Optional sharing expiration timestamp.

        Returns:
            Collection: Updated collection model.

        Raises:
            CollectionNotFoundError: If the collection does not exist.
        """
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
        """Add a user group to a collection with permissions.

        Args:
            collection_id: Collection identifier.
            user_group_id: User group identifier to share with.
            permissions: Permission set to apply.
            expiration_date: Optional sharing expiration timestamp.

        Returns:
            Collection: Updated collection model.

        Raises:
            CollectionNotFoundError: If the collection does not exist.
        """
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
        """Update collection permissions for a user or user group.

        Args:
            collection_id: Collection identifier.
            permissions: Permission set to apply.
            user_id: Optional user identifier whose permissions should change.
            user_group_id: Optional user group identifier whose permissions should change.
            expiration_date: Optional sharing expiration timestamp.

        Returns:
            Collection: Updated collection model.

        Raises:
            ValidationError: If neither or both target identifiers are supplied.
            CollectionNotFoundError: If the collection does not exist.
        """
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

    async def list(self, view: Optional[str] = None) -> List[Collection]:
        """List collections visible to the current caller.

        Args:
            view: Optional API-specific collection view filter.

        Returns:
            List[Collection]: Matching collection models.
        """
        params = {"view": view} if view else None
        response = await self._client._request("GET", "collections", params=params)
        return _coerce_collection_list(response)

    async def get(self, collection_id: CollectionId) -> Collection:
        """Retrieve a collection by identifier.

        Args:
            collection_id: Collection identifier.

        Returns:
            Collection: Resolved collection model.

        Raises:
            CollectionNotFoundError: If the collection does not exist.
        """
        try:
            response = await self._client._request("GET", f"collections/{collection_id}")
            return Collection.model_validate(response)
        except NotFoundError as exc:
            raise CollectionNotFoundError(collection_id) from exc

    async def create(self, name: str) -> Collection:
        """Create a collection.

        Args:
            name: Collection display name.

        Returns:
            Collection: Newly created collection model.
        """
        request = CollectionCreateRequest(name=name)
        response = await self._client._request(
            "POST",
            "collections",
            json_data=request.model_dump(by_alias=True, exclude_none=True),
        )
        return Collection.model_validate(response)

    async def update(self, collection_id: CollectionId, name: str, owner_id: UserId) -> Collection:
        """Update collection name and owner.

        Args:
            collection_id: Collection identifier.
            name: Updated collection name.
            owner_id: New owner user identifier.

        Returns:
            Collection: Updated collection model.

        Raises:
            CollectionNotFoundError: If the collection does not exist.
        """
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
        """Delete a collection.

        Args:
            collection_id: Collection identifier.
            force_delete: Whether to force deletion when supported by the API.

        Raises:
            CollectionNotFoundError: If the collection does not exist.
        """
        params = {"forceDelete": str(force_delete).lower()} if force_delete else None
        try:
            await self._client._request("DELETE", f"collections/{collection_id}", params=params)
        except NotFoundError as exc:
            raise CollectionNotFoundError(collection_id) from exc

    async def add_workflow(self, collection_id: CollectionId, workflow_id: WorkflowId) -> Collection:
        """Add a workflow to a collection.

        Args:
            collection_id: Collection identifier.
            workflow_id: Workflow identifier to add.

        Returns:
            Collection: Updated collection model.

        Raises:
            CollectionNotFoundError: If the collection does not exist.
        """
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
        """Remove a workflow from a collection.

        Args:
            collection_id: Collection identifier.
            workflow_id: Workflow identifier to remove.

        Raises:
            CollectionNotFoundError: If the collection does not exist.
        """
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
        """Add a user to a collection with permissions.

        Args:
            collection_id: Collection identifier.
            user_id: User identifier to share with.
            permissions: Permission set to apply.
            expiration_date: Optional sharing expiration timestamp.

        Returns:
            Collection: Updated collection model.

        Raises:
            CollectionNotFoundError: If the collection does not exist.
        """
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
        """Add a user group to a collection with permissions.

        Args:
            collection_id: Collection identifier.
            user_group_id: User group identifier to share with.
            permissions: Permission set to apply.
            expiration_date: Optional sharing expiration timestamp.

        Returns:
            Collection: Updated collection model.

        Raises:
            CollectionNotFoundError: If the collection does not exist.
        """
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
        """Update collection permissions for a user or user group.

        Args:
            collection_id: Collection identifier.
            permissions: Permission set to apply.
            user_id: Optional user identifier whose permissions should change.
            user_group_id: Optional user group identifier whose permissions should change.
            expiration_date: Optional sharing expiration timestamp.

        Returns:
            Collection: Updated collection model.

        Raises:
            ValidationError: If neither or both target identifiers are supplied.
            CollectionNotFoundError: If the collection does not exist.
        """
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
