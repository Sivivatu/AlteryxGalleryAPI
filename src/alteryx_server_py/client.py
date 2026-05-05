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
        """Create the shared synchronous HTTP client on first use.

        Returns:
            None: This method initializes internal client state in place.
        """
        if self._client is None:
            self._client = httpx.Client(
                verify=self.config.verify_ssl,
                timeout=self.config.timeout,
            )
            logger.debug("HTTP client initialized")

    def __enter__(self):
        """Enter the client context manager.

        Returns:
            AlteryxClient: The initialized client instance.
        """
        self._initialize_client()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the client context manager and close open resources.

        Args:
            exc_type: Exception type raised in the context, if any.
            exc_val: Exception instance raised in the context, if any.
            exc_tb: Traceback associated with the exception, if any.

        Returns:
            None: This method closes the underlying HTTP client in place.
        """
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
        """Make an authenticated HTTP request against the Alteryx API.

        Args:
            method: HTTP method such as GET, POST, PUT, or DELETE.
            endpoint: API endpoint path relative to the version root.
            api_version: API version to use.
            params: URL query parameters.
            data: Form data payload.
            json_data: JSON request body.
            files: Files to upload with multipart form data.
            **kwargs: Additional arguments forwarded to httpx.

        Returns:
            Any: Parsed response payload returned by the API.

        Raises:
            Exception: Propagates request and API response failures.
        """
        url = self._build_endpoint_url(endpoint, api_version)
        headers = self._add_auth_header({})
        if files:
            headers.pop("Content-Type", None)
            if data is not None:
                data = self._serialize_form_data(data)
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
        """Access workflow operations for the current client.

        Returns:
            WorkflowResource: Resource wrapper for workflow endpoints.
        """
        if self._workflows is None:
            from .resources.workflows import WorkflowResource

            self._workflows = WorkflowResource(self)
        return self._workflows

    @property
    def jobs(self) -> "JobResource":
        """Access job operations for the current client.

        Returns:
            JobResource: Resource wrapper for job endpoints.
        """
        if self._jobs is None:
            from .resources.jobs import JobResource

            self._jobs = JobResource(self)
        return self._jobs

    @property
    def schedules(self) -> "ScheduleResource":
        """Access schedule operations for the current client.

        Returns:
            ScheduleResource: Resource wrapper for schedule endpoints.
        """
        if self._schedules is None:
            from .resources.schedules import ScheduleResource

            self._schedules = ScheduleResource(self)
        return self._schedules

    @property
    def users(self) -> "UserResource":
        """Access user operations for the current client.

        Returns:
            UserResource: Resource wrapper for user endpoints.
        """
        if self._users is None:
            from .resources.users import UserResource

            self._users = UserResource(self)
        return self._users

    @property
    def user_groups(self) -> "UserGroupResource":
        """Access user group operations for the current client.

        Returns:
            UserGroupResource: Resource wrapper for user group endpoints.
        """
        if self._user_groups is None:
            from .resources.user_groups import UserGroupResource

            self._user_groups = UserGroupResource(self)
        return self._user_groups

    @property
    def collections(self) -> "CollectionResource":
        """Access collection operations for the current client.

        Returns:
            CollectionResource: Resource wrapper for collection endpoints.
        """
        if self._collections is None:
            from .resources.collections import CollectionResource

            self._collections = CollectionResource(self)
        return self._collections

    @property
    def credentials(self) -> "CredentialResource":
        """Access credential operations for the current client.

        Returns:
            CredentialResource: Resource wrapper for credential endpoints.
        """
        if self._credentials is None:
            from .resources.credentials import CredentialResource

            self._credentials = CredentialResource(self)
        return self._credentials

    @property
    def server(self) -> "ServerResource":
        """Access server metadata operations for the current client.

        Returns:
            ServerResource: Resource wrapper for server endpoints.
        """
        if self._server is None:
            from .resources.server import ServerResource

            self._server = ServerResource(self)
        return self._server
