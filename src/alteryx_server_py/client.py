"""Synchronous Alteryx Server API client."""

import logging
from typing import TYPE_CHECKING, Any, Dict, Optional

import httpx

from ._base_client import _BaseClient
from .config import ClientConfig
from .config import from_env as config_from_env
from .resources import WorkflowResource

if TYPE_CHECKING:
    from .resources.collections import CollectionResource
    from .resources.credentials import CredentialResource
    from .resources.jobs import JobResource
    from .resources.schedules import ScheduleResource
    from .resources.server import ServerResource
    from .resources.user_groups import UserGroupResource
    from .resources.users import UserResource

logger = logging.getLogger(__name__)


class AlteryxClient(_BaseClient):
    """Synchronous client for Alteryx Server API.

    Example:
        from alteryx_server_py import AlteryxClient

        # From environment variables
        client = AlteryxClient.from_env()

        # With explicit configuration
        client = AlteryxClient(
            base_url="https://server.com/webapi/",
            client_id="your-id",
            client_secret="your-secret"
        )

        workflows = client.workflows.list()
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
        """Initialize synchronous client.

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

        self._client: Optional[httpx.Client] = None
        self._workflows: Optional[WorkflowResource] = None
        self._jobs: Optional["JobResource"] = None
        self._schedules: Optional["ScheduleResource"] = None
        self._users: Optional["UserResource"] = None
        self._user_groups: Optional["UserGroupResource"] = None
        self._collections: Optional["CollectionResource"] = None
        self._credentials: Optional["CredentialResource"] = None
        self._server: Optional["ServerResource"] = None

        if config_obj.base_url and config_obj.client_id and config_obj.client_secret:
            self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize httpx client with authentication."""
        if self._client is None:
            self._client = httpx.Client(
                verify=self.config.verify_ssl,
                timeout=self.config.timeout,
            )
            logger.debug("HTTP client initialized")

    def __enter__(self):
        """Context manager entry."""
        self._initialize_client()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._client:
            self._client.close()
            logger.debug("HTTP client closed")

    def _request(
        self,
        method: str,
        endpoint: str,
        api_version: str = "v3",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Any:
        """Make authenticated HTTP request.

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
        if files:
            headers.pop("Content-Type", None)
        elif data is not None:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        elif json_data is not None:
            headers["Content-Type"] = "application/json"

        logger.debug(f"{method} {url}")
        logger.debug(f"Params: {params}")
        logger.debug(f"Data: {data}")
        logger.debug(f"JSON: {json_data}")

        if self._client is None:
            self._initialize_client()
        assert self._client is not None

        try:
            response = self._client.request(
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
    ) -> "AlteryxClient":
        """Create client from environment variables.

        Environment variables:
            ALTERYX_BASE_URL: Base URL
            ALTERYX_CLIENT_ID: Client ID
            ALTERYX_CLIENT_SECRET: Client secret
            ALTERYX_VERIFY_SSL: SSL verification (default: true)
            ALTERYX_TIMEOUT: Timeout (default: 30)

        Args:
            env_file: Optional path to .env file

        Returns:
            AlteryxClient: Initialized client

        Raises:
            ConfigurationError: If required env vars are missing
        """
        config = config_from_env(env_file)
        return cls(config=config)

    @classmethod
    def from_dotenv(
        cls,
        env_file: str = ".env",
    ) -> "AlteryxClient":
        """Create client from .env file.

        Args:
            env_file: Path to .env file. Defaults to ".env".

        Returns:
            AlteryxClient: Initialized client
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
            JobResource: Job API operations
        """
        if not hasattr(self, "_jobs") or self._jobs is None:
            from .resources.jobs import JobResource

            self._jobs = JobResource(self)
        return self._jobs

    @property
    def schedules(self) -> object:
        """Access schedule resource.

        Returns:
            ScheduleResource: Schedule API operations
        """
        if self._schedules is None:
            from .resources.schedules import ScheduleResource

            self._schedules = ScheduleResource(self)
        return self._schedules

    @property
    def users(self) -> object:
        """Access user resource.

        Returns:
            UserResource: User API operations
        """
        if self._users is None:
            from .resources.users import UserResource

            self._users = UserResource(self)
        return self._users

    @property
    def user_groups(self) -> object:
        """Access user group resource.

        Returns:
            UserGroupResource: User group API operations
        """
        if self._user_groups is None:
            from .resources.user_groups import UserGroupResource

            self._user_groups = UserGroupResource(self)
        return self._user_groups

    @property
    def collections(self) -> object:
        """Access collection resource.

        Returns:
            CollectionResource: Collection API operations
        """
        if self._collections is None:
            from .resources.collections import CollectionResource

            self._collections = CollectionResource(self)
        return self._collections

    @property
    def credentials(self) -> object:
        """Access credential resource.

        Returns:
            CredentialResource: Credential API operations
        """
        if self._credentials is None:
            from .resources.credentials import CredentialResource

            self._credentials = CredentialResource(self)
        return self._credentials

    @property
    def server(self) -> object:
        """Access server resource.

        Returns:
            ServerResource: Server API operations
        """
        if self._server is None:
            from .resources.server import ServerResource

            self._server = ServerResource(self)
        return self._server
