"""
Pytest unit tests for the AlteryxClient initialization and configuration.
"""


import pytest

from alteryx_server_py.client import AlteryxClient
from alteryx_server_py.exceptions import ConfigurationError

BASE_URL = "https://mock-gallery.com/webapi/"
CLIENT_ID = "test_key"
CLIENT_SECRET = "test_secret"


def test_successful_initialization():
    """Test successful client initialization with proper config."""
    client = AlteryxClient(BASE_URL, CLIENT_ID, CLIENT_SECRET)
    assert client.config.client_id == CLIENT_ID
    assert client.config.client_secret == CLIENT_SECRET
    assert client.config.base_url == BASE_URL


def test_base_url_trailing_slash_added():
    """Test that a trailing slash is added to base URL if missing."""
    client = AlteryxClient("https://test.alteryx.com/gallery", CLIENT_ID, CLIENT_SECRET)
    assert client.config.base_url.endswith("/")


def test_missing_client_id_raises():
    """Test client initialization fails when client_id is empty."""
    with pytest.raises(ConfigurationError):
        AlteryxClient(BASE_URL, "", CLIENT_SECRET)


def test_missing_client_secret_raises():
    """Test client initialization fails when client_secret is empty."""
    with pytest.raises(ConfigurationError):
        AlteryxClient(BASE_URL, CLIENT_ID, "")


def test_missing_base_url_raises():
    """Test client initialization fails when base_url is empty."""
    with pytest.raises(ConfigurationError):
        AlteryxClient("", CLIENT_ID, CLIENT_SECRET)
