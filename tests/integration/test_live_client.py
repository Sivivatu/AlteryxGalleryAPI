import os

import pytest
from dotenv import load_dotenv

from alteryx_server_py import AlteryxClient
from alteryx_server_py.exceptions import AuthenticationError

load_dotenv()

HOST_URL = os.getenv("ALTERYX_BASE_URL")
CLIENT_ID = os.getenv("ALTERYX_CLIENT_ID")
CLIENT_SECRET = os.getenv("ALTERYX_CLIENT_SECRET")

live_credentials = pytest.mark.skipif(
    not all([HOST_URL, CLIENT_ID, CLIENT_SECRET]),
    reason="Missing ALTERYX_BASE_URL, ALTERYX_CLIENT_ID, or ALTERYX_CLIENT_SECRET environment variables",
)

@live_credentials
def test_live_authentication():
    """Test successful client initialization with valid credentials against a live system."""
    client = AlteryxClient(
        base_url=HOST_URL,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )
    assert client.config.client_id == CLIENT_ID
    assert client.config.client_secret == CLIENT_SECRET

    # Attempt to fetch workflows to validate authentication
    workflows = client.workflows.list()
    assert isinstance(workflows, list)


@live_credentials
def test_live_failed_authentication():
    """Test client initialization with invalid credentials against a live system."""
    with pytest.raises((AuthenticationError, Exception)):
        client = AlteryxClient(
            base_url=HOST_URL,
            client_id="invalid_id",
            client_secret="invalid_secret",
        )
        # Force an authenticated request
        client.workflows.list()


@live_credentials
def test_live_get_all_workflows():
    """Test fetching workflows from a live system."""
    client = AlteryxClient(
        base_url=HOST_URL,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )
    workflows = client.workflows.list()
    assert isinstance(workflows, list)


@live_credentials
def test_live_get_workflow_by_id():
    """Test fetching a specific workflow by ID from a live system."""
    client = AlteryxClient(
        base_url=HOST_URL,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )
    workflows = client.workflows.list()
    assert isinstance(workflows, list)
    if workflows:
        workflow_id = workflows[0].id
        workflow = client.workflows.get(workflow_id)
        assert workflow.id == workflow_id
