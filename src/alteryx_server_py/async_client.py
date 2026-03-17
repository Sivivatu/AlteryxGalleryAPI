"""
Asynchronous Alteryx Server API client.
"""

import logging
from typing import Any, Dict, Optional, Union

import httpx

from ._base_client import _BaseClient
from .config import ClientConfig
from .config import from_env as config_from_env
from .resources import WorkflowResource

logger = logging.getLogger(__name__)


class AsyncAlteryxClient(_BaseClient):
    """Asynchronous client for Alteryx Server API.

    Example:
        from alteryx_server_py import AsyncAlteryxClient
        import asyncio

        async def main():
            async with AsyncAlteryxClient.from_env() as client:
                workflows = await client.workflows.list()
                print(workflows)

        asyncio.run(main())
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        verify_ssl: bool = True,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_backoff_factor: float = 0.5,
        config: Optional[ClientConfig] = None,
    ):
        """Initialize asynchronous client.

        Args:
            base_url: Base URL of Alteryx Server
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            verify_ssl: Verify SSL certificates
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            retry_backoff_factor: Exponential backoff factor
            config: Pre-built configuration (overrides individual params)
        """
        if config:
            config_obj = config
        else:
            config_obj = ClientConfig(
                base_url=base_url or "",
                client_id=client_id or "",
                client_secret=client_secret or "",
                verify_ssl=verify_ssl,
                timeout=timeout,
                max_retries=max_retries,
                retry_backoff_factor=retry_backoff_factor,
            )

        super().__init__(config_obj)

        self._client: Optional[httpx.AsyncClient] = None
        self._workflows: Optional[WorkflowResource] = None

        if config_obj.base_url and config_obj.client_id and config_obj.client_secret:
            self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize httpx async client with authentication."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                verify=self.config.verify_ssl,
                timeout=self.config.timeout,
            )
            logger.debug("Async HTTP client initialized")

    async def __aenter__(self):
        """Async context manager entry."""
        self._initialize_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
            logger.debug("Async HTTP client closed")

    async def _request(
        self,
        method: str,
        endpoint: str,
        api_version: str = "v3",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Any:
        """Make authenticated async HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            api_version: API version to use
            params: URL query parameters
            data: Form data
            json_data: JSON request body
            files: Files to upload
            **kwargs: Additional arguments for httpx

        Returns:
            Parsed response data
        """
        url = self._build_endpoint_url(endpoint, api_version)
        headers = self._add_auth_header({})

        logger.debug(f"ASYNC {method} {url}")
        logger.debug(f"Params: {params}")
        logger.debug(f"Data: {data}")
        logger.debug(f"JSON: {json_data}")

        try:
            response = await self._client.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json_data,
                files=files,
                headers=headers,
                **kwargs,
            )

            logger.debug(f"Response status: {response.status_code}")

            return self._process_response(response, endpoint)

        except httpx.HTTPStatusError as e:
            return self._process_response(e.response, endpoint)
        except httpx.RequestError as e:
            logger.error(f"Request failed for {endpoint}: {e}")
            raise Exception(f"Request failed: {e}") from e

    @classmethod
    def from_env(
        cls,
        env_file: Optional[str] = None,
    ) -> "AsyncAlteryxClient":
        """Create async client from environment variables.

        Environment variables:
            ALTERYX_BASE_URL: Base URL
            ALTERYX_CLIENT_ID: Client ID
            ALTERYX_CLIENT_SECRET: Client secret
            ALTERYX_VERIFY_SSL: SSL verification (default: true)
            ALTERYX_TIMEOUT: Timeout (default: 30)

        Args:
            env_file: Optional path to .env file

        Returns:
            AsyncAlteryxClient: Initialized client

        Raises:
            ConfigurationError: If required env vars are missing
        """
        config = config_from_env(env_file)
        return cls(config=config)

    @classmethod
    def from_dotenv(
        cls,
        env_file: str = ".env",
    ) -> "AsyncAlteryxClient":
        """Create async client from .env file.

        Args:
            env_file: Path to .env file. Defaults to ".env".

        Returns:
            AsyncAlteryxClient: Initialized client
        """
        return cls.from_env(env_file=env_file)

    @property
    def workflows(self) -> WorkflowResource:
        """Access workflow resource.

        Returns:
            WorkflowResource: Workflow API operations
        """
        if self._workflows is None:
            from .resources.workflows import WorkflowResource

            self._workflows = WorkflowResource(self)
        return self._workflows

    @property
    def jobs(self) -> object:
        """Access job resource.

        Returns:
            AsyncJobResource: Job API operations
        """
        if not hasattr(self, "_jobs") or self._jobs is None:
            from .resources.jobs import AsyncJobResource

            self._jobs = AsyncJobResource(self)
        return self._jobs

    @property
    def schedules(self) -> object:
        """Access schedule resource.

        Returns:
            AsyncScheduleResource: Schedule API operations
        """
        if not hasattr(self, "_schedules") or self._schedules is None:
            from .resources.schedules import AsyncScheduleResource

            self._schedules = AsyncScheduleResource(self)
        return self._schedules

    @property
    def users(self) -> object:
        """Access user resource.

        Returns:
            AsyncUserResource: User API operations
        """
        if not hasattr(self, "_users") or self._users is None:
            from .resources.users import AsyncUserResource

            self._users = AsyncUserResource(self)
        return self._users

    @property
    def user_groups(self) -> object:
        """Access user group resource.

        Returns:
            AsyncUserGroupResource: User group API operations
        """
        if not hasattr(self, "_user_groups") or self._user_groups is None:
            from .resources.user_groups import AsyncUserGroupResource

            self._user_groups = AsyncUserGroupResource(self)
        return self._user_groups
