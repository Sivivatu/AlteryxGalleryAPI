"""
Base resource class for API resources.
"""

from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import AlteryxClient
    from ..async_client import AsyncAlteryxClient


class _BaseResource:
    """Base class for API resources.

    Provides common functionality for all resource classes.
    """

    def __init__(self, client: "AlteryxClient | AsyncAlteryxClient"):
        """Initialize resource.

        Args:
            client: Client instance (sync or async)
        """
        self._client = client
