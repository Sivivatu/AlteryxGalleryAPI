import pytest
import os
from dotenv import load_dotenv
from alteryx_gallery_api.client import AlteryxClient

load_dotenv()

HOST_URL = os.getenv("HOST_URL")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

@pytest.mark.skipif(
    not all([HOST_URL, CLIENT_ID, CLIENT_SECRET]),
    reason="Missing HOST_URL, CLIENT_ID, or CLIENT_SECRET environment variables",
)

def test_live_authentication():
    '''Test successful client initialization with valid credentials against a live system.'''
    client = AlteryxClient(HOST_URL, CLIENT_ID, CLIENT_SECRET)
    assert client.api_key == CLIENT_ID
    assert client.api_secret == CLIENT_SECRET

    # Attempt to fetch workflows to validate authentication
    workflows = client.get_workflows()
    assert isinstance(workflows, list)

def test_live_failed_authentication():
    '''Test client initialization with invalid credentials against a live system.'''
    with pytest.raises(Exception) as excinfo:
        AlteryxClient(HOST_URL, "invalid_id", "invalid_secret")
        assert "authentication check failed" in str(excinfo.value)

def test_live_get_all_workflows():
    '''Test fetching workflows from a live system.'''
    client = AlteryxClient(HOST_URL, CLIENT_ID, CLIENT_SECRET)
    workflows = client.get_workflows()
    assert isinstance(workflows, list)
    # Further assertions can be made based on expected workflow properties

def test_live_get_workflow_by_id():
    '''Test fetching a specific workflow by ID from a live system.'''
    client = AlteryxClient(HOST_URL, CLIENT_ID, CLIENT_SECRET)
    workflows = client.get_workflows()
    assert isinstance(workflows, list)
    if workflows:
        workflow_id = workflows[0].id
        workflow = client.get_workflows(workflow_id)
        assert isinstance(workflow, list)
        assert len(workflow) == 1
        assert workflow[0].id == workflow_id