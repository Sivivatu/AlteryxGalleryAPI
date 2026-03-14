"""
Base client with shared logic for sync and async clients.
"""

import logging
from typing import Optional, Any, Dict
from urllib.parse import urljoin

from .config import ClientConfig
from .auth import OAuth2Client
from .exceptions import (
    AuthenticationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    ServerError,
)
from .utils import retry_with_backoff

logger = logging.getLogger(__name__)


class _BaseClient:
    """Base client with shared logic for sync and async.

    Handles:
        - URL building
        - OAuth2 authentication
        - Request/response processing
        - Error handling
        - Retry logic
    """

    def __init__(self, config: ClientConfig):
        """Initialize base client.

        Args:
            config: Client configuration
        """
        self.config = config
        self._auth_client = OAuth2Client(
            client_id=config.client_id,
            client_secret=config.client_secret,
            token_url=self._build_token_url(),
            verify_ssl=config.verify_ssl,
            timeout=config.timeout,
        )
        logger.info(f"Initialized {self.__class__.__name__} for {config.base_url}")

    def _build_token_url(self) -> str:
        """Build OAuth2 token URL from base URL.

        Returns:
            str: Token endpoint URL
        """
        return f"{self.config.base_url}oauth2/token"

    def _build_endpoint_url(
        self,
        endpoint: str,
        api_version: str = "v3",
    ) -> str:
        """Build full API endpoint URL.

        Args:
            endpoint: API endpoint path (e.g., 'workflows/')
            api_version: API version to use. Defaults to 'v3'.

        Returns:
            str: Full endpoint URL
        """
        return urljoin(self.config.base_url, f"{api_version}/{endpoint}")

    def _process_response(self, response: Any, endpoint: str) -> Any:
        """Process API response, handling errors.

        Args:
            response: HTTP response object
            endpoint: Endpoint being called (for error messages)

        Returns:
            Parsed response data

        Raises:
            AuthenticationError: On 401 status
            NotFoundError: On 404 status
            ValidationError: On 400 status
            RateLimitError: On 429 status
            ServerError: On 5xx status
        """
        status = getattr(response, "status_code", None) or getattr(response, "status_code", 200)

        if status == 200 or status == 201 or status == 204:
            if hasattr(response, "json"):
                try:
                    return response.json()
                except Exception:
                    return response.text
            return response.text

        elif status == 400:
            error_text = self._get_error_text(response)
            logger.error(f"Validation error for {endpoint}: {error_text}")
            raise ValidationError(error_text)

        elif status == 401:
            error_text = self._get_error_text(response)
            logger.error(f"Authentication error for {endpoint}: {error_text}")
            raise AuthenticationError(error_text)

        elif status == 404:
            error_text = self._get_error_text(response)
            logger.warning(f"Not found for {endpoint}: {error_text}")
            raise NotFoundError(error_text)

        elif status == 429:
            retry_after = response.headers.get("Retry-After")
            logger.warning(f"Rate limit exceeded for {endpoint}. " f"Retry after {retry_after}s")
            raise RateLimitError(retry_after=int(retry_after) if retry_after else None)

        elif status >= 500:
            error_text = self._get_error_text(response)
            logger.error(f"Server error for {endpoint}: {error_text}")
            raise ServerError(error_text)

        else:
            error_text = self._get_error_text(response)
            logger.error(f"HTTP error {status} for {endpoint}: {error_text}")
            raise Exception(f"HTTP {status}: {error_text}")

    def _get_error_text(self, response: Any) -> str:
        """Extract error text from response.

        Args:
            response: HTTP response object

        Returns:
            str: Error message
        """
        try:
            if hasattr(response, "json"):
                data = response.json()
                if isinstance(data, dict):
                    return data.get("message", str(data))
                return str(data)
            return response.text or "Unknown error"
        except Exception:
            return response.text or "Unknown error"

    def _add_auth_header(
        self,
        headers: Optional[Dict[str, str]],
    ) -> Dict[str, str]:
        """Add authorization header to request headers.

        Args:
            headers: Existing headers dict

        Returns:
            Headers dict with authorization added
        """
        if headers is None:
            headers = {}

        token = self._auth_client.get_token()
        headers["Authorization"] = token
        headers["Content-Type"] = "application/json"

        return headers
