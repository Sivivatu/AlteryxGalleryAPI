"""
Pytest unit tests for the AlteryxClient authentication.
"""

import pytest
import responses # TODO: this isnt needed and can be done with mocks from pytest directly using the mocker plugin (https://github.com/vilus/mocker)
import json

from alteryx_gallery_api.client import AlteryxClient
from alteryx_gallery_api.exceptions import AuthenticationError

BASE_URL = "https://mock-gallery.com/webapi/"
API_KEY = "test_key"
API_SECRET = "test_secret"
TOKEN_ENDPOINT = f"{BASE_URL}oauth2/token"
SUBSCRIPTION_ENDPOINT = f"{BASE_URL}v1/workflows/subscription/" # Adjusted endpoint assumption


@responses.activate
def test_successful_authentication():
    """Test successful client initialization with OAuth2 token fetch."""
    # Mock the token endpoint response
    responses.add(
        method=responses.POST,
        url=TOKEN_ENDPOINT,
        json={"access_token": "mock_token", "token_type": "Bearer", "expires_in": 3600},
        status=200,
        content_type="application/json",
    )
    # Mock the subsequent API call made during initialization to test auth
    responses.add(
        method=responses.GET,
        url=SUBSCRIPTION_ENDPOINT, # Assuming this is called by get_subscription_workflows
        json=[{"id": "workflow1", "name": "Test Workflow"}],
        status=200,
    )

    client = AlteryxClient(BASE_URL, API_KEY, API_SECRET)
    assert client.api_key == API_KEY
    assert client.api_secret == API_SECRET

    # Verify that the token request was made correctly
    assert len(responses.calls) == 2
    token_request = responses.calls[0].request
    assert token_request.method == "POST"
    assert token_request.url == TOKEN_ENDPOINT
    # Check that client_id and client_secret are in the request body (requests-oauthlib handles this)
    body_params = json.loads(token_request.body)
    assert body_params["client_id"] == API_KEY
    assert body_params["client_secret"] == API_SECRET
    assert body_params["grant_type"] == "client_credentials"

    # Verify that the subsequent request was correctly authenticated with the Bearer token
    subscription_request = responses.calls[1].request
    assert subscription_request.method == "GET"
    assert subscription_request.url == SUBSCRIPTION_ENDPOINT
    assert "Authorization" in subscription_request.headers
    assert subscription_request.headers["Authorization"] == "Bearer mock_token"


@responses.activate
def test_authentication_failure():
    """Test client initialization failure when token fetch fails."""
    # Mock the token endpoint response to return an error
    responses.add(
        method=responses.POST,
        url=TOKEN_ENDPOINT,
        json={"error": "invalid_client", "error_description": "Invalid client credentials"},
        status=401,
        content_type="application/json",
    )

    with pytest.raises(AuthenticationError) as excinfo:
        AlteryxClient(BASE_URL, API_KEY, API_SECRET)

    assert "Failed to fetch OAuth2 token" in str(excinfo.value)
    assert len(responses.calls) == 1 # Only the token call should be made
    assert responses.calls[0].request.url == TOKEN_ENDPOINT


@responses.activate
def test_failed_authentication():
    """Test client initialization failure due to invalid credentials."""
    responses.add(
        responses.GET,
        f"{BASE_URL}api/workflows/subscription/",
        json={"error": "Invalid credentials", "code": 401, "message": "Invalid credentials"},
        status=401,
    )
    with pytest.raises(AuthenticationError) as exc_info:
        AlteryxClient(BASE_URL, API_KEY, API_SECRET)
    assert "Authentication failed" in str(exc_info.value)


def test_invalid_base_url():
    """Test client initialization with an invalid base URL (missing trailing slash)."""
    with pytest.raises(ValueError) as exc_info:
        AlteryxClient("https://test.alteryx.com/gallery", API_KEY, API_SECRET)
    assert "Base URL must end with a slash" in str(exc_info.value)


def test_invalid_base_url_type():
    """Test client initialization with an invalid base URL (not a string)."""
    with pytest.raises(TypeError) as exc_info:
        AlteryxClient(123, API_KEY, API_SECRET)
    assert "base_url must be a string" in str(exc_info.value)
