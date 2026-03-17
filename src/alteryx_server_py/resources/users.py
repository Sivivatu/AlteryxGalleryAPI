"""
User resource for API operations.
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ..exceptions import NotFoundError, UserNotFoundError
from ..models.common import UserId, UserRole
from ..models.users import (
    User,
    UserCreateRequest,
    UserUpdateRequest,
)
from ._base import _BaseResource

if TYPE_CHECKING:
    from ..async_client import AsyncAlteryxClient
    from ..client import AlteryxClient

logger = logging.getLogger(__name__)


class UserResource(_BaseResource):
    """Resource for user operations.

    Provides methods for managing users:
        - List users
        - Get user details
        - Create new users
        - Update users
        - Delete (deactivate) users
        - Get user assets
    """

    _client: "AlteryxClient"

    def list(
        self,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> List[User]:
        """List all users.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            List of User objects
        """
        params = {}
        if page:
            params["page"] = page
        if page_size:
            params["pageSize"] = page_size

        logger.debug(f"Listing users with params: {params}")

        response = self._client._request(
            "GET",
            "users/",
            params=params,
        )

        if isinstance(response, list):
            return [User.model_validate(item) for item in response]
        elif isinstance(response, dict) and "users" in response:
            return [User.model_validate(item) for item in response["users"]]
        elif isinstance(response, dict):
            return [User.model_validate(response)]

        return []

    def get(self, user_id: UserId) -> User:
        """Get user details by ID.

        Args:
            user_id: User identifier

        Returns:
            User: User details

        Raises:
            UserNotFoundError: If user not found
        """
        logger.debug(f"Getting user: {user_id}")

        try:
            response = self._client._request(
                "GET",
                f"users/{user_id}",
            )
            return User.model_validate(response)
        except NotFoundError:
            raise UserNotFoundError(user_id)

    def create(
        self,
        email: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        role: str = "Viewer",
        default_worker_tag: Optional[str] = None,
        time_zone: Optional[str] = None,
    ) -> User:
        """Create a new user.

        Args:
            email: User's email address
            first_name: User's first name
            last_name: User's last name
            role: User's role (NoAccess/Viewer/Member/Artisan/Curator/Admin)
            default_worker_tag: Default worker tag assignment
            time_zone: User's preferred time zone

        Returns:
            User: Created user details
        """
        logger.info(f"Creating user: {email}")

        request = UserCreateRequest(
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=UserRole(role),
            default_worker_tag=default_worker_tag,
            time_zone=time_zone,
        )

        data = request.model_dump(by_alias=True, exclude_none=True)

        response = self._client._request(
            "POST",
            "users/",
            json_data=data,
        )

        user = User.model_validate(response)
        logger.info(f"User '{email}' created with ID: {user.id}")
        return user

    def update(
        self,
        user_id: UserId,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        role: Optional[str] = None,
        active: Optional[bool] = None,
        default_worker_tag: Optional[str] = None,
        time_zone: Optional[str] = None,
    ) -> User:
        """Update an existing user.

        Args:
            user_id: User identifier
            first_name: User's first name
            last_name: User's last name
            role: User's role
            active: Whether the user is active
            default_worker_tag: Default worker tag assignment
            time_zone: User's preferred time zone

        Returns:
            User: Updated user details

        Raises:
            UserNotFoundError: If user not found
        """
        logger.info(f"Updating user: {user_id}")

        user_role = UserRole(role) if role else None

        request = UserUpdateRequest(
            first_name=first_name,
            last_name=last_name,
            role=user_role,
            active=active,
            default_worker_tag=default_worker_tag,
            time_zone=time_zone,
        )

        data = request.model_dump(by_alias=True, exclude_none=True)

        try:
            response = self._client._request(
                "PUT",
                f"users/{user_id}",
                json_data=data,
            )
            user = User.model_validate(response)
            logger.info(f"User {user_id} updated")
            return user
        except NotFoundError:
            raise UserNotFoundError(user_id)

    def delete(self, user_id: UserId) -> None:
        """Delete (deactivate) a user.

        Args:
            user_id: User identifier

        Raises:
            UserNotFoundError: If user not found
        """
        logger.info(f"Deleting user: {user_id}")

        try:
            self._client._request(
                "DELETE",
                f"users/{user_id}",
            )
            logger.info(f"Successfully deleted user: {user_id}")
        except NotFoundError:
            raise UserNotFoundError(user_id)

    def get_assets(self, user_id: UserId) -> List[Dict[str, Any]]:
        """Get a user's assets (workflows, schedules, etc.).

        Args:
            user_id: User identifier

        Returns:
            List of asset dictionaries

        Raises:
            UserNotFoundError: If user not found
        """
        logger.debug(f"Getting assets for user: {user_id}")

        try:
            response = self._client._request(
                "GET",
                f"users/{user_id}/assets",
            )

            if isinstance(response, list):
                return response
            elif isinstance(response, dict) and "assets" in response:
                return response["assets"]

            return []
        except NotFoundError:
            raise UserNotFoundError(user_id)


class AsyncUserResource(_BaseResource):
    """Asynchronous user resource.

    Provides async versions of all UserResource methods.
    """

    _client: "AsyncAlteryxClient"

    async def list(
        self,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> List[User]:
        """List all users (async).

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            List of User objects
        """
        params = {}
        if page:
            params["page"] = page
        if page_size:
            params["pageSize"] = page_size

        logger.debug(f"Listing users with params: {params}")

        response = await self._client._request(
            "GET",
            "users/",
            params=params,
        )

        if isinstance(response, list):
            return [User.model_validate(item) for item in response]
        elif isinstance(response, dict) and "users" in response:
            return [User.model_validate(item) for item in response["users"]]
        elif isinstance(response, dict):
            return [User.model_validate(response)]

        return []

    async def get(self, user_id: UserId) -> User:
        """Get user details by ID (async).

        Args:
            user_id: User identifier

        Returns:
            User: User details

        Raises:
            UserNotFoundError: If user not found
        """
        logger.debug(f"Getting user: {user_id}")

        try:
            response = await self._client._request(
                "GET",
                f"users/{user_id}",
            )
            return User.model_validate(response)
        except NotFoundError:
            raise UserNotFoundError(user_id)

    async def create(
        self,
        email: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        role: str = "Viewer",
        default_worker_tag: Optional[str] = None,
        time_zone: Optional[str] = None,
    ) -> User:
        """Create a new user (async).

        Args:
            email: User's email address
            first_name: User's first name
            last_name: User's last name
            role: User's role
            default_worker_tag: Default worker tag assignment
            time_zone: User's preferred time zone

        Returns:
            User: Created user details
        """
        logger.info(f"Creating user: {email}")

        request = UserCreateRequest(
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=UserRole(role),
            default_worker_tag=default_worker_tag,
            time_zone=time_zone,
        )

        data = request.model_dump(by_alias=True, exclude_none=True)

        response = await self._client._request(
            "POST",
            "users/",
            json_data=data,
        )

        user = User.model_validate(response)
        logger.info(f"User '{email}' created with ID: {user.id}")
        return user

    async def update(
        self,
        user_id: UserId,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        role: Optional[str] = None,
        active: Optional[bool] = None,
        default_worker_tag: Optional[str] = None,
        time_zone: Optional[str] = None,
    ) -> User:
        """Update an existing user (async).

        Args:
            user_id: User identifier
            first_name: User's first name
            last_name: User's last name
            role: User's role
            active: Whether the user is active
            default_worker_tag: Default worker tag assignment
            time_zone: User's preferred time zone

        Returns:
            User: Updated user details

        Raises:
            UserNotFoundError: If user not found
        """
        logger.info(f"Updating user: {user_id}")

        user_role = UserRole(role) if role else None

        request = UserUpdateRequest(
            first_name=first_name,
            last_name=last_name,
            role=user_role,
            active=active,
            default_worker_tag=default_worker_tag,
            time_zone=time_zone,
        )

        data = request.model_dump(by_alias=True, exclude_none=True)

        try:
            response = await self._client._request(
                "PUT",
                f"users/{user_id}",
                json_data=data,
            )
            user = User.model_validate(response)
            logger.info(f"User {user_id} updated")
            return user
        except NotFoundError:
            raise UserNotFoundError(user_id)

    async def delete(self, user_id: UserId) -> None:
        """Delete (deactivate) a user (async).

        Args:
            user_id: User identifier

        Raises:
            UserNotFoundError: If user not found
        """
        logger.info(f"Deleting user: {user_id}")

        try:
            await self._client._request(
                "DELETE",
                f"users/{user_id}",
            )
            logger.info(f"Successfully deleted user: {user_id}")
        except NotFoundError:
            raise UserNotFoundError(user_id)

    async def get_assets(self, user_id: UserId) -> List[Dict[str, Any]]:
        """Get a user's assets (async).

        Args:
            user_id: User identifier

        Returns:
            List of asset dictionaries

        Raises:
            UserNotFoundError: If user not found
        """
        logger.debug(f"Getting assets for user: {user_id}")

        try:
            response = await self._client._request(
                "GET",
                f"users/{user_id}/assets",
            )

            if isinstance(response, list):
                return response
            elif isinstance(response, dict) and "assets" in response:
                return response["assets"]

            return []
        except NotFoundError:
            raise UserNotFoundError(user_id)
