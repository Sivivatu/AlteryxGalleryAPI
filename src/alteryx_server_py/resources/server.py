"""Server resource for API operations."""

from typing import TYPE_CHECKING

from ..models import ServerInfo, ServerSettings
from ._base import _BaseResource

if TYPE_CHECKING:
    from ..async_client import AsyncAlteryxClient
    from ..client import AlteryxClient


class ServerResource(_BaseResource):
    """Resource for server information and settings."""

    _client: "AlteryxClient"

    def get_info(self) -> ServerInfo:
        """Get server information."""
        response = self._client._request("GET", "serverinfo")
        return ServerInfo.model_validate(response)

    def get_settings(self) -> ServerSettings:
        """Get server settings."""
        response = self._client._request("GET", "admin/settings")
        return ServerSettings.model_validate(response)


class AsyncServerResource(_BaseResource):
    """Asynchronous resource for server information and settings."""

    _client: "AsyncAlteryxClient"

    async def get_info(self) -> ServerInfo:
        """Get server information."""
        response = await self._client._request("GET", "serverinfo")
        return ServerInfo.model_validate(response)

    async def get_settings(self) -> ServerSettings:
        """Get server settings."""
        response = await self._client._request("GET", "admin/settings")
        return ServerSettings.model_validate(response)