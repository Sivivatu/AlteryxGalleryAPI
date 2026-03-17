"""
Configuration management for Alteryx Server API client.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from .exceptions import ConfigurationError


@dataclass
class ClientConfig:
    """Configuration for Alteryx Server API client.

    Attributes:
        base_url: Base URL of Alteryx Server (e.g., 'https://server.com/webapi/')
        client_id: OAuth2 Client ID
        client_secret: OAuth2 Client Secret
        verify_ssl: Whether to verify SSL certificates. Defaults to True.
        timeout: Request timeout in seconds. Defaults to 30.
        max_retries: Maximum number of retry attempts. Defaults to 3.
        retry_backoff_factor: Exponential backoff factor. Defaults to 0.5.
        log_level: Logging level. Defaults to 'INFO'.
    """

    base_url: str
    client_id: str
    client_secret: str
    verify_ssl: bool = True
    timeout: float = 30.0
    max_retries: int = 3
    retry_backoff_factor: float = 0.5
    log_level: str = "INFO"

    def __post_init__(self):
        """Validate and normalize configuration values."""
        if not self.base_url:
            raise ConfigurationError("base_url cannot be empty")

        if not self.client_id:
            raise ConfigurationError("client_id cannot be empty")

        if not self.client_secret:
            raise ConfigurationError("client_secret cannot be empty")

        if not self.base_url.endswith("/"):
            self.base_url = f"{self.base_url}/"

        if self.timeout <= 0:
            raise ConfigurationError("timeout must be positive")

        if self.max_retries < 0:
            raise ConfigurationError("max_retries cannot be negative")


def from_env(env_file: str | None = None) -> ClientConfig:
    """Create configuration from environment variables.

    Environment variables:
        ALTERYX_BASE_URL: Base URL of Alteryx Server
        ALTERYX_CLIENT_ID: OAuth2 Client ID
        ALTERYX_CLIENT_SECRET: OAuth2 Client Secret
        ALTERYX_VERIFY_SSL: SSL verification (default: true)
        ALTERYX_TIMEOUT: Request timeout in seconds (default: 30)
        ALTERYX_MAX_RETRIES: Max retry attempts (default: 3)
        ALTERYX_LOG_LEVEL: Logging level (default: INFO)

    Args:
        env_file: Optional path to .env file to load

    Returns:
        ClientConfig: Configuration loaded from environment

    Raises:
        ConfigurationError: If required environment variables are missing
    """
    if env_file:
        load_dotenv(env_file)
    else:
        load_dotenv()

    base_url = os.getenv("ALTERYX_BASE_URL")
    client_id = os.getenv("ALTERYX_CLIENT_ID")
    client_secret = os.getenv("ALTERYX_CLIENT_SECRET")

    if not base_url:
        raise ConfigurationError("ALTERYX_BASE_URL environment variable is required")
    if not client_id:
        raise ConfigurationError("ALTERYX_CLIENT_ID environment variable is required")
    if not client_secret:
        raise ConfigurationError("ALTERYX_CLIENT_SECRET environment variable is required")

    return ClientConfig(
        base_url=base_url,
        client_id=client_id,
        client_secret=client_secret,
        verify_ssl=os.getenv("ALTERYX_VERIFY_SSL", "true").lower() == "true",
        timeout=float(os.getenv("ALTERYX_TIMEOUT", "30")),
        max_retries=int(os.getenv("ALTERYX_MAX_RETRIES", "3")),
        log_level=os.getenv("ALTERYX_LOG_LEVEL", "INFO"),
    )
