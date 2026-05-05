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
    """Normalize credential list responses into model instances.

    Args:
        response: Raw response payload returned by the API client.

    Returns:
        list[Credential]: Parsed credential models.
    """
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
        """List credentials visible to the current caller.

        Args:
            view: Optional API-specific credential view filter.
            user_id: Optional user identifier filter.
            user_group_id: Optional user group identifier filter.

        Returns:
            list[Credential]: Matching credential models.
        """
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
        """Retrieve a credential by identifier.

        Args:
            credential_id: Credential identifier.

        Returns:
            Credential: Resolved credential model.

        Raises:
            CredentialNotFoundError: If the credential does not exist.
        """
        try:
            response = self._client._request("GET", f"credentials/{credential_id}")
            return Credential.model_validate(response)
        except NotFoundError as exc:
            raise CredentialNotFoundError(credential_id) from exc

    def create(self, username: str, password: str) -> Credential:
        """Create a shared credential.

        Args:
            username: Credential username.
            password: Credential secret value.

        Returns:
            Credential: Newly created credential model.
        """
        request = CredentialCreateRequest(username=username, password=password)
        response = self._client._request(
            "POST",
            "credentials",
            json_data=request.model_dump(by_alias=True, exclude_none=True),
        )
        return Credential.model_validate(response)

    def update(self, credential_id: CredentialId, new_password: str) -> Credential:
        """Rotate the stored password for a credential.

        Args:
            credential_id: Credential identifier.
            new_password: Replacement password value.

        Returns:
            Credential: Updated credential model.

        Raises:
            CredentialNotFoundError: If the credential does not exist.
        """
        request = CredentialUpdateRequest(new_password=new_password)
        try:
            response = self._client._request(
                "PUT",
                f"credentials/{credential_id}",
                json_data=request.model_dump(by_alias=True, exclude_none=True),
            )
            return Credential.model_validate(response)
        except NotFoundError as exc:
            raise CredentialNotFoundError(credential_id) from exc

    def delete(self, credential_id: CredentialId, force: bool = False) -> None:
        """Delete a credential.

        Args:
            credential_id: Credential identifier.
            force: Whether to force deletion when supported by the API.

        Raises:
            CredentialNotFoundError: If the credential does not exist.
        """
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
        """List credentials visible to the current caller.

        Args:
            view: Optional API-specific credential view filter.
            user_id: Optional user identifier filter.
            user_group_id: Optional user group identifier filter.

        Returns:
            list[Credential]: Matching credential models.
        """
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
        """Retrieve a credential by identifier.

        Args:
            credential_id: Credential identifier.

        Returns:
            Credential: Resolved credential model.

        Raises:
            CredentialNotFoundError: If the credential does not exist.
        """
        try:
            response = await self._client._request("GET", f"credentials/{credential_id}")
            return Credential.model_validate(response)
        except NotFoundError as exc:
            raise CredentialNotFoundError(credential_id) from exc

    async def create(self, username: str, password: str) -> Credential:
        """Create a shared credential.

        Args:
            username: Credential username.
            password: Credential secret value.

        Returns:
            Credential: Newly created credential model.
        """
        request = CredentialCreateRequest(username=username, password=password)
        response = await self._client._request(
            "POST",
            "credentials",
            json_data=request.model_dump(by_alias=True, exclude_none=True),
        )
        return Credential.model_validate(response)

    async def update(self, credential_id: CredentialId, new_password: str) -> Credential:
        """Rotate the stored password for a credential.

        Args:
            credential_id: Credential identifier.
            new_password: Replacement password value.

        Returns:
            Credential: Updated credential model.

        Raises:
            CredentialNotFoundError: If the credential does not exist.
        """
        request = CredentialUpdateRequest(new_password=new_password)
        try:
            response = await self._client._request(
                "PUT",
                f"credentials/{credential_id}",
                json_data=request.model_dump(by_alias=True, exclude_none=True),
            )
            return Credential.model_validate(response)
        except NotFoundError as exc:
            raise CredentialNotFoundError(credential_id) from exc

    async def delete(self, credential_id: CredentialId, force: bool = False) -> None:
        """Delete a credential.

        Args:
            credential_id: Credential identifier.
            force: Whether to force deletion when supported by the API.

        Raises:
            CredentialNotFoundError: If the credential does not exist.
        """
        params = {"force": str(force).lower()} if force else None
        try:
            await self._client._request("DELETE", f"credentials/{credential_id}", params=params)
        except NotFoundError as exc:
            raise CredentialNotFoundError(credential_id) from exc
