"""Credential resource for API operations."""

import logging
from typing import TYPE_CHECKING, Optional

from ..exceptions import CredentialNotFoundError, NotFoundError
from ..models import (
    Credential,
    CredentialCreateRequest,
    CredentialUpdateRequest,
)
from ..models.common import CredentialId, UserGroupId, UserId
from ._base import _BaseResource

if TYPE_CHECKING:
    from ..async_client import AsyncAlteryxClient
    from ..client import AlteryxClient

logger = logging.getLogger(__name__)


def _coerce_credential_list(response: object) -> list[Credential]:
    if isinstance(response, list):
        return [Credential.model_validate(item) for item in response]
    if isinstance(response, dict) and "credentials" in response:
        return [Credential.model_validate(item) for item in response["credentials"]]
    if isinstance(response, dict):
        return [Credential.model_validate(response)]
    return []


class CredentialResource(_BaseResource):
    """Resource for credential operations."""

    _client: "AlteryxClient"

    def list(
        self,
        view: Optional[str] = None,
        user_id: Optional[UserId] = None,
        user_group_id: Optional[UserGroupId] = None,
    ) -> list[Credential]:
        """List accessible credentials."""
        params = {}
        if view:
            params["view"] = view
        if user_id:
            params["userId"] = user_id
        if user_group_id:
            params["userGroupId"] = user_group_id
        response = self._client._request("GET", "credentials", params=params or None)
        return _coerce_credential_list(response)

    def get(self, credential_id: CredentialId) -> Credential:
        """Get a credential by ID."""
        try:
            response = self._client._request("GET", f"credentials/{credential_id}")
            return Credential.model_validate(response)
        except NotFoundError as exc:
            raise CredentialNotFoundError(credential_id) from exc

    def create(self, username: str, password: str) -> Credential:
        """Create a credential."""
        request = CredentialCreateRequest(username=username, password=password)
        response = self._client._request(
            "POST",
            "credentials",
            data=request.model_dump(by_alias=True, exclude_none=True),
        )
        return Credential.model_validate(response)

    def update(self, credential_id: CredentialId, new_password: str) -> Credential:
        """Update a credential password."""
        request = CredentialUpdateRequest(new_password=new_password)
        try:
            response = self._client._request(
                "PUT",
                f"credentials/{credential_id}",
                data=request.model_dump(by_alias=True, exclude_none=True),
            )
            return Credential.model_validate(response)
        except NotFoundError as exc:
            raise CredentialNotFoundError(credential_id) from exc

    def delete(self, credential_id: CredentialId, force: bool = False) -> None:
        """Delete a credential."""
        params = {"force": str(force).lower()} if force else None
        try:
            self._client._request("DELETE", f"credentials/{credential_id}", params=params)
        except NotFoundError as exc:
            raise CredentialNotFoundError(credential_id) from exc


class AsyncCredentialResource(_BaseResource):
    """Asynchronous credential resource."""

    _client: "AsyncAlteryxClient"

    async def list(
        self,
        view: Optional[str] = None,
        user_id: Optional[UserId] = None,
        user_group_id: Optional[UserGroupId] = None,
    ) -> list[Credential]:
        """List accessible credentials."""
        params = {}
        if view:
            params["view"] = view
        if user_id:
            params["userId"] = user_id
        if user_group_id:
            params["userGroupId"] = user_group_id
        response = await self._client._request("GET", "credentials", params=params or None)
        return _coerce_credential_list(response)

    async def get(self, credential_id: CredentialId) -> Credential:
        """Get a credential by ID."""
        try:
            response = await self._client._request("GET", f"credentials/{credential_id}")
            return Credential.model_validate(response)
        except NotFoundError as exc:
            raise CredentialNotFoundError(credential_id) from exc

    async def create(self, username: str, password: str) -> Credential:
        """Create a credential."""
        request = CredentialCreateRequest(username=username, password=password)
        response = await self._client._request(
            "POST",
            "credentials",
            data=request.model_dump(by_alias=True, exclude_none=True),
        )
        return Credential.model_validate(response)

    async def update(self, credential_id: CredentialId, new_password: str) -> Credential:
        """Update a credential password."""
        request = CredentialUpdateRequest(new_password=new_password)
        try:
            response = await self._client._request(
                "PUT",
                f"credentials/{credential_id}",
                data=request.model_dump(by_alias=True, exclude_none=True),
            )
            return Credential.model_validate(response)
        except NotFoundError as exc:
            raise CredentialNotFoundError(credential_id) from exc

    async def delete(self, credential_id: CredentialId, force: bool = False) -> None:
        """Delete a credential."""
        params = {"force": str(force).lower()} if force else None
        try:
            await self._client._request("DELETE", f"credentials/{credential_id}", params=params)
        except NotFoundError as exc:
            raise CredentialNotFoundError(credential_id) from exc