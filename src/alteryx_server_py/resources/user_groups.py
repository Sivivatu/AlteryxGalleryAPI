"""
User group resource for API operations.
"""

import logging
from typing import TYPE_CHECKING, List, Optional

from ..exceptions import NotFoundError, UserGroupNotFoundError
from ..models.common import UserGroupId, UserId, UserRole
from ..models.users import (
    UserGroup,
    UserGroupCreateRequest,
    UserGroupUpdateRequest,
)
from ._base import _BaseResource

if TYPE_CHECKING:
    from ..async_client import AsyncAlteryxClient
    from ..client import AlteryxClient

logger = logging.getLogger(__name__)


class UserGroupResource(_BaseResource):
    """Resource for user group operations.

    Provides methods for managing user groups:
        - List user groups
        - Get user group details
        - Create new user groups
        - Update user groups
        - Delete user groups
        - Add/remove users from groups
    """

    _client: "AlteryxClient"

    def list(
        self,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> List[UserGroup]:
        """List all user groups.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            List of UserGroup objects
        """
        params = {}
        if page:
            params["page"] = page
        if page_size:
            params["pageSize"] = page_size

        logger.debug(f"Listing user groups with params: {params}")

        response = self._client._request(
            "GET",
            "usergroups/",
            params=params,
        )

        if isinstance(response, list):
            return [UserGroup.model_validate(item) for item in response]
        elif isinstance(response, dict) and "userGroups" in response:
            return [UserGroup.model_validate(item) for item in response["userGroups"]]
        elif isinstance(response, dict):
            return [UserGroup.model_validate(response)]

        return []

    def get(self, group_id: UserGroupId) -> UserGroup:
        """Get user group details by ID.

        Args:
            group_id: User group identifier

        Returns:
            UserGroup: User group details

        Raises:
            UserGroupNotFoundError: If user group not found
        """
        logger.debug(f"Getting user group: {group_id}")

        try:
            response = self._client._request(
                "GET",
                f"usergroups/{group_id}",
            )
            return UserGroup.model_validate(response)
        except NotFoundError:
            raise UserGroupNotFoundError(group_id)

    def create(
        self,
        name: str,
        role: Optional[str] = None,
        description: Optional[str] = None,
    ) -> UserGroup:
        """Create a new user group.

        Args:
            name: Group name
            role: Group role (NoAccess/Viewer/Member/Artisan/Curator/Admin)
            description: Group description

        Returns:
            UserGroup: Created user group details
        """
        logger.info(f"Creating user group: {name}")

        group_role = UserRole(role) if role else None

        request = UserGroupCreateRequest(
            name=name,
            role=group_role,
            description=description,
        )

        data = request.model_dump(by_alias=True, exclude_none=True)

        response = self._client._request(
            "POST",
            "usergroups/",
            json_data=data,
        )

        group = UserGroup.model_validate(response)
        logger.info(f"User group '{name}' created with ID: {group.id}")
        return group

    def update(
        self,
        group_id: UserGroupId,
        name: Optional[str] = None,
        role: Optional[str] = None,
        description: Optional[str] = None,
    ) -> UserGroup:
        """Update an existing user group.

        Args:
            group_id: User group identifier
            name: Group name
            role: Group role
            description: Group description

        Returns:
            UserGroup: Updated user group details

        Raises:
            UserGroupNotFoundError: If user group not found
        """
        logger.info(f"Updating user group: {group_id}")

        group_role = UserRole(role) if role else None

        request = UserGroupUpdateRequest(
            name=name,
            role=group_role,
            description=description,
        )

        data = request.model_dump(by_alias=True, exclude_none=True)

        try:
            response = self._client._request(
                "PUT",
                f"usergroups/{group_id}",
                json_data=data,
            )
            group = UserGroup.model_validate(response)
            logger.info(f"User group {group_id} updated")
            return group
        except NotFoundError:
            raise UserGroupNotFoundError(group_id)

    def delete(self, group_id: UserGroupId) -> None:
        """Delete a user group.

        Args:
            group_id: User group identifier

        Raises:
            UserGroupNotFoundError: If user group not found
        """
        logger.info(f"Deleting user group: {group_id}")

        try:
            self._client._request(
                "DELETE",
                f"usergroups/{group_id}",
            )
            logger.info(f"Successfully deleted user group: {group_id}")
        except NotFoundError:
            raise UserGroupNotFoundError(group_id)

    def add_users(self, group_id: UserGroupId, user_ids: List[UserId]) -> UserGroup:
        """Add users to a user group.

        Args:
            group_id: User group identifier
            user_ids: List of user IDs to add

        Returns:
            UserGroup: Updated user group details

        Raises:
            UserGroupNotFoundError: If user group not found
        """
        logger.info(f"Adding {len(user_ids)} users to group: {group_id}")

        try:
            response = self._client._request(
                "POST",
                f"usergroups/{group_id}/users",
                json_data=user_ids,
            )
            return UserGroup.model_validate(response)
        except NotFoundError:
            raise UserGroupNotFoundError(group_id)

    def remove_user(self, group_id: UserGroupId, user_id: UserId) -> None:
        """Remove a user from a user group.

        Args:
            group_id: User group identifier
            user_id: User ID to remove

        Raises:
            UserGroupNotFoundError: If user group not found
        """
        logger.info(f"Removing user {user_id} from group: {group_id}")

        try:
            self._client._request(
                "DELETE",
                f"usergroups/{group_id}/users/{user_id}",
            )
            logger.info(f"Successfully removed user {user_id} from group {group_id}")
        except NotFoundError:
            raise UserGroupNotFoundError(group_id)


class AsyncUserGroupResource(_BaseResource):
    """Asynchronous user group resource.

    Provides async versions of all UserGroupResource methods.
    """

    _client: "AsyncAlteryxClient"

    async def list(
        self,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> List[UserGroup]:
        """List all user groups (async).

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            List of UserGroup objects
        """
        params = {}
        if page:
            params["page"] = page
        if page_size:
            params["pageSize"] = page_size

        logger.debug(f"Listing user groups with params: {params}")

        response = await self._client._request(
            "GET",
            "usergroups/",
            params=params,
        )

        if isinstance(response, list):
            return [UserGroup.model_validate(item) for item in response]
        elif isinstance(response, dict) and "userGroups" in response:
            return [UserGroup.model_validate(item) for item in response["userGroups"]]
        elif isinstance(response, dict):
            return [UserGroup.model_validate(response)]

        return []

    async def get(self, group_id: UserGroupId) -> UserGroup:
        """Get user group details by ID (async).

        Args:
            group_id: User group identifier

        Returns:
            UserGroup: User group details

        Raises:
            UserGroupNotFoundError: If user group not found
        """
        logger.debug(f"Getting user group: {group_id}")

        try:
            response = await self._client._request(
                "GET",
                f"usergroups/{group_id}",
            )
            return UserGroup.model_validate(response)
        except NotFoundError:
            raise UserGroupNotFoundError(group_id)

    async def create(
        self,
        name: str,
        role: Optional[str] = None,
        description: Optional[str] = None,
    ) -> UserGroup:
        """Create a new user group (async).

        Args:
            name: Group name
            role: Group role
            description: Group description

        Returns:
            UserGroup: Created user group details
        """
        logger.info(f"Creating user group: {name}")

        group_role = UserRole(role) if role else None

        request = UserGroupCreateRequest(
            name=name,
            role=group_role,
            description=description,
        )

        data = request.model_dump(by_alias=True, exclude_none=True)

        response = await self._client._request(
            "POST",
            "usergroups/",
            json_data=data,
        )

        group = UserGroup.model_validate(response)
        logger.info(f"User group '{name}' created with ID: {group.id}")
        return group

    async def update(
        self,
        group_id: UserGroupId,
        name: Optional[str] = None,
        role: Optional[str] = None,
        description: Optional[str] = None,
    ) -> UserGroup:
        """Update an existing user group (async).

        Args:
            group_id: User group identifier
            name: Group name
            role: Group role
            description: Group description

        Returns:
            UserGroup: Updated user group details

        Raises:
            UserGroupNotFoundError: If user group not found
        """
        logger.info(f"Updating user group: {group_id}")

        group_role = UserRole(role) if role else None

        request = UserGroupUpdateRequest(
            name=name,
            role=group_role,
            description=description,
        )

        data = request.model_dump(by_alias=True, exclude_none=True)

        try:
            response = await self._client._request(
                "PUT",
                f"usergroups/{group_id}",
                json_data=data,
            )
            group = UserGroup.model_validate(response)
            logger.info(f"User group {group_id} updated")
            return group
        except NotFoundError:
            raise UserGroupNotFoundError(group_id)

    async def delete(self, group_id: UserGroupId) -> None:
        """Delete a user group (async).

        Args:
            group_id: User group identifier

        Raises:
            UserGroupNotFoundError: If user group not found
        """
        logger.info(f"Deleting user group: {group_id}")

        try:
            await self._client._request(
                "DELETE",
                f"usergroups/{group_id}",
            )
            logger.info(f"Successfully deleted user group: {group_id}")
        except NotFoundError:
            raise UserGroupNotFoundError(group_id)

    async def add_users(self, group_id: UserGroupId, user_ids: List[UserId]) -> UserGroup:
        """Add users to a user group (async).

        Args:
            group_id: User group identifier
            user_ids: List of user IDs to add

        Returns:
            UserGroup: Updated user group details

        Raises:
            UserGroupNotFoundError: If user group not found
        """
        logger.info(f"Adding {len(user_ids)} users to group: {group_id}")

        try:
            response = await self._client._request(
                "POST",
                f"usergroups/{group_id}/users",
                json_data=user_ids,
            )
            return UserGroup.model_validate(response)
        except NotFoundError:
            raise UserGroupNotFoundError(group_id)

    async def remove_user(self, group_id: UserGroupId, user_id: UserId) -> None:
        """Remove a user from a user group (async).

        Args:
            group_id: User group identifier
            user_id: User ID to remove

        Raises:
            UserGroupNotFoundError: If user group not found
        """
        logger.info(f"Removing user {user_id} from group: {group_id}")

        try:
            await self._client._request(
                "DELETE",
                f"usergroups/{group_id}/users/{user_id}",
            )
            logger.info(f"Successfully removed user {user_id} from group {group_id}")
        except NotFoundError:
            raise UserGroupNotFoundError(group_id)
