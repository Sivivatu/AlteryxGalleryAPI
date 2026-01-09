"""
OAuth2 authentication for Alteryx Server API.
"""

import logging
from typing import Optional
from datetime import datetime, timedelta

import httpx

from .exceptions import AuthenticationError, ConfigurationError

logger = logging.getLogger(__name__)


class OAuth2Token:
    """OAuth2 access token with expiry handling.

    Attributes:
        access_token: The access token string
        expires_at: Datetime when the token expires
        token_type: Type of token (typically "Bearer")
    """

    def __init__(
        self,
        access_token: str,
        expires_in: int,
        token_type: str = "Bearer",
    ):
        self.access_token = access_token
        self.expires_at = datetime.now() + timedelta(seconds=expires_in)
        self.token_type = token_type

    @property
    def is_expired(self) -> bool:
        """Check if token has expired (with 5 minute buffer)."""
        buffer_seconds = 300
        return datetime.now() >= self.expires_at - timedelta(seconds=buffer_seconds)

    @property
    def authorization_header(self) -> str:
        """Get formatted authorization header value."""
        return f"{self.token_type} {self.access_token}"

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "access_token": self.access_token,
            "expires_at": self.expires_at.isoformat(),
            "token_type": self.token_type,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "OAuth2Token":
        """Create token from dictionary."""
        return cls(
            access_token=data["access_token"],
            expires_in=int((datetime.fromisoformat(data["expires_at"]) - datetime.now()).total_seconds()),
            token_type=data.get("token_type", "Bearer"),
        )


class OAuth2Client:
    """OAuth2 client credentials authentication.

    Handles token fetching and automatic refresh for Alteryx Server API.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token_url: str,
        verify_ssl: bool = True,
        timeout: float = 30.0,
    ):
        """Initialize OAuth2 client.

        Args:
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            token_url: URL to fetch OAuth2 token
            verify_ssl: Whether to verify SSL certificates
            timeout: Request timeout in seconds
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self._token: Optional[OAuth2Token] = None

    def fetch_token(self) -> OAuth2Token:
        """Fetch a new OAuth2 access token.

        Uses the Client Credentials flow to obtain an access token.

        Returns:
            OAuth2Token: New access token

        Raises:
            AuthenticationError: If token fetch fails
        """
        logger.debug(f"Fetching OAuth2 token from {self.token_url}")

        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

        try:
            with httpx.Client(verify=self.verify_ssl, timeout=self.timeout) as client:
                response = client.post(
                    self.token_url,
                    data=data,
                    headers=headers,
                )
                response.raise_for_status()

                token_data = response.json()

                self._token = OAuth2Token(
                    access_token=token_data["access_token"],
                    expires_in=token_data.get("expires_in", 3600),
                    token_type=token_data.get("token_type", "Bearer"),
                )

                logger.debug("Successfully fetched OAuth2 token")
                return self._token

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching token: {e.response.status_code}")
            raise AuthenticationError(f"Failed to fetch OAuth2 token: {e.response.status_code}") from e
        except httpx.RequestError as e:
            logger.error(f"Network error fetching token: {e}")
            raise AuthenticationError(f"Network error fetching token: {e}") from e
        except KeyError as e:
            logger.error(f"Invalid token response: missing key {e}")
            raise AuthenticationError(f"Invalid token response from server") from e

    def get_token(self) -> str:
        """Get current valid access token, fetching new one if expired.

        Returns:
            str: Authorization header value
        """
        if self._token is None or self._token.is_expired:
            self.fetch_token()

        return self._token.authorization_header

    def refresh_token(self) -> OAuth2Token:
        """Force refresh the OAuth2 token.

        Returns:
            OAuth2Token: New access token
        """
        logger.debug("Force refreshing OAuth2 token")
        return self.fetch_token()
