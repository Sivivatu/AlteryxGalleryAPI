"""
Pytest unit tests for AlteryxClient workflow management methods.
"""

import pytest
import responses
import json
from pathlib import Path

from alteryx_gallery_api.client import AlteryxClient
from alteryx_gallery_api.exceptions import WorkflowNotFoundError, AlteryxAPIError

BASE_URL = "https://mock-gallery.com/webapi/"
API_KEY = "test_key"
API_SECRET = "test_secret"

@pytest.fixture
def client():
    with responses.RequestsMock() as rsps:
        # Mock token endpoint for authentication
        rsps.add(
            responses.POST,
            f"{BASE_URL}oauth2/token",
            json={"access_token": "mock_token", "token_type": "Bearer", "expires_in": 3600},
            status=200,
        )
        # Mock subscription endpoint for initial auth check
        rsps.add(
            responses.GET,
            f"{BASE_URL}v1/workflows/subscription/",
            json=[{"id": "wf1", "name": "Test Workflow"}],
            status=200,
        )
        yield AlteryxClient(BASE_URL, API_KEY, API_SECRET)

@responses.activate
def test_get_subscription_workflows(client):
    responses.add(
        responses.GET,
        f"{BASE_URL}workflows/subscription/",
        json=[{"id": "wf1", "name": "Test Workflow"}],
        status=200,
    )
    workflows = client.get_subscription_workflows()
    assert isinstance(workflows, list)
    assert workflows[0]["id"] == "wf1"

@responses.activate
def test_get_workflow_info_success(client):
    workflow_id = "wf1"
    responses.add(
        responses.GET,
        f"{BASE_URL}workflows/{workflow_id}/",
        json={"id": workflow_id, "name": "Test Workflow"},
        status=200,
    )
    info = client.get_workflow_info(workflow_id)
    assert info["id"] == workflow_id

@responses.activate
def test_get_workflow_info_not_found(client):
    workflow_id = "notfound"
    responses.add(
        responses.GET,
        f"{BASE_URL}workflows/{workflow_id}/",
        json={"error": "Not found"},
        status=404,
    )
    with pytest.raises(WorkflowNotFoundError):
        client.get_workflow_info(workflow_id)

@responses.activate
def test_publish_workflow_file_not_found(client):
    with pytest.raises(FileNotFoundError):
        client.publish_workflow("/no/such/file.yxzp", "Test", "owner@example.com")

@responses.activate
def test_update_workflow_file_not_found(client):
    with pytest.raises(FileNotFoundError):
        client.update_workflow("wf1", "/no/such/file.yxzp")

@responses.activate
def test_delete_workflow_success(client):
    workflow_id = "wf1"
    responses.add(
        responses.DELETE,
        f"{BASE_URL}workflows/{workflow_id}/",
        status=200,
    )
    # Should not raise
    client.delete_workflow(workflow_id)

@responses.activate
def test_delete_workflow_not_found(client):
    workflow_id = "notfound"
    responses.add(
        responses.DELETE,
        f"{BASE_URL}workflows/{workflow_id}/",
        json={"error": "Not found"},
        status=404,
    )
    with pytest.raises(WorkflowNotFoundError):
        client.delete_workflow(workflow_id)

@responses.activate
def test_queue_job_success(client):
    workflow_id = "wf1"
    responses.add(
        responses.POST,
        f"{BASE_URL}workflows/{workflow_id}/jobs/",
        json={"id": "job1", "status": "Queued"},
        status=200,
    )
    job = client.queue_job(workflow_id)
    assert job["id"] == "job1"

@responses.activate
def test_queue_job_not_found(client):
    workflow_id = "notfound"
    responses.add(
        responses.POST,
        f"{BASE_URL}workflows/{workflow_id}/jobs/",
        json={"error": "Not found"},
        status=404,
    )
    with pytest.raises(WorkflowNotFoundError):
        client.queue_job(workflow_id)
