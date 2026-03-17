"""
Pytest unit tests for AlteryxClient workflow management methods.
"""

from unittest.mock import MagicMock

import pytest

from alteryx_server_py.client import AlteryxClient
from alteryx_server_py.models import Workflow

BASE_URL = "https://mock-gallery.com/webapi/"
CLIENT_ID = "test_key"
CLIENT_SECRET = "test_secret"

@pytest.fixture
def client():
    """Create an AlteryxClient with mocked auth to avoid real HTTP calls."""
    c = AlteryxClient(
        base_url=BASE_URL,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )
    # Monkey-patch auth to avoid real token fetching
    c._auth_client = MagicMock()
    c._auth_client.get_token.return_value = "Bearer mock_token"
    return c


def test_get_workflows(client, monkeypatch):
    """Test listing workflows through the resource-based API."""
    payload = [
        {
            "id": "wf1",
            "name": "Test Workflow",
            "ownerId": "owner-1",
            "workflowType": "Standard",
            "executionMode": "Safe",
            "dateCreated": "2024-01-01T00:00:00Z",
        }
    ]
    monkeypatch.setattr(client, "_request", lambda *a, **k: payload)

    workflows = client.workflows.list()
    assert isinstance(workflows, list)
    assert len(workflows) == 1
    assert isinstance(workflows[0], Workflow)
    assert workflows[0].id == "wf1"

# @responses.activate
# def test_get_workflow_info_success(client):
#     workflow_id = "wf1"
#     responses.add(
#         responses.GET,
#         f"{BASE_URL}workflows/{workflow_id}/",
#         json={"id": workflow_id, "name": "Test Workflow"},
#         status=200,
#     )
#     info = client.get_workflow_info(workflow_id)
#     assert info["id"] == workflow_id

# @responses.activate
# def test_get_workflow_info_not_found(client):
#     workflow_id = "notfound"
#     responses.add(
#         responses.GET,
#         f"{BASE_URL}workflows/{workflow_id}/",
#         json={"error": "Not found"},
#         status=404,
#     )
#     with pytest.raises(WorkflowNotFoundError):
#         client.get_workflow_info(workflow_id)

# @responses.activate
# def test_publish_workflow_file_not_found(client):
#     with pytest.raises(FileNotFoundError):
#         client.publish_workflow("/no/such/file.yxzp", "Test", "owner@example.com")

# @responses.activate
# def test_update_workflow_file_not_found(client):
#     with pytest.raises(FileNotFoundError):
#         client.update_workflow("wf1", "/no/such/file.yxzp")

# @responses.activate
# def test_delete_workflow_success(client):
#     workflow_id = "wf1"
#     responses.add(
#         responses.DELETE,
#         f"{BASE_URL}workflows/{workflow_id}/",
#         status=200,
#     )
#     # Should not raise
#     client.delete_workflow(workflow_id)

# @responses.activate
# def test_delete_workflow_not_found(client):
#     workflow_id = "notfound"
#     responses.add(
#         responses.DELETE,
#         f"{BASE_URL}workflows/{workflow_id}/",
#         json={"error": "Not found"},
#         status=404,
#     )
#     with pytest.raises(WorkflowNotFoundError):
#         client.delete_workflow(workflow_id)

# @responses.activate
# def test_queue_job_success(client):
#     workflow_id = "wf1"
#     responses.add(
#         responses.POST,
#         f"{BASE_URL}workflows/{workflow_id}/jobs/",
#         json={"id": "job1", "status": "Queued"},
#         status=200,
#     )
#     job = client.queue_job(workflow_id)
#     assert job["id"] == "job1"

# @responses.activate
# def test_queue_job_not_found(client):
#     workflow_id = "notfound"
#     responses.add(
#         responses.POST,
#         f"{BASE_URL}workflows/{workflow_id}/jobs/",
#         json={"error": "Not found"},
#         status=404,
#     )
#     with pytest.raises(WorkflowNotFoundError):
#         client.queue_job(workflow_id)
