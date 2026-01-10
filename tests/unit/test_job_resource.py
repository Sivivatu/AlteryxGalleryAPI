"""
Unit tests for JobResource.
"""

import pytest
from unittest.mock import MagicMock

import respx

from alteryx_server_py import AlteryxClient
from alteryx_server_py.models import Job, JobStatus, JobOutput, JobMessage, JobId
from alteryx_server_py.exceptions import JobNotFoundError, JobExecutionError, TimeoutError


@pytest.fixture
def mock_client():
    """Create a mock client for testing."""
    from alteryx_server_py._base_client import _BaseClient
    from alteryx_server_py.resources import JobResource

    # Create a minimal mock client
    config = MagicMock()
    config.base_url = "https://test.example.com/webapi/"
    config.client_id = "test-client-id"
    config.client_secret = "test-client-secret"

    client = AlteryxClient(
        base_url="https://test.example.com/webapi/",
        client_id="test-id",
        client_secret="test-secret",
    )

    # Monkey patch to avoid authentication
    client._auth_client = MagicMock()
    client._auth_client.get_token.return_value = "Bearer test-token"

    return client


@pytest.fixture
def job_data():
    """Sample job data for testing."""
    return {
        "id": "job-123",
        "workflowId": "workflow-456",
        "status": "Completed",
        "disposition": "Success",
        "priority": "Default",
        "workerTag": None,
        "runAs": None,
        "createDate": "2024-01-01T12:00:00Z",
        "queuedDate": "2024-01-01T12:05:00Z",
        "startDate": "2024-01-01T12:10:00Z",
        "endDate": "2024-01-01T12:30:00Z",
        "durationSeconds": 20.5,
        "outputs": [
            {
                "id": "output-1",
                "name": "output.csv",
                "format": "CSV",
                "size": 1024,
            }
        ],
        "messages": [
            {
                "message": "Job completed successfully",
                "timestamp": "2024-01-01T12:30:00Z",
                "level": "Info",
            }
        ],
    }


class TestJobResource:
    """Test JobResource functionality."""

    @pytest.mark.asyncio
    async def test_run_job(self, mock_client):
        """Test running a workflow job."""
        with respx.mock:
            # Mock the job creation endpoint
            respx.post(
                "https://test.example.com/webapi/v3/workflows/workflow-456/jobs",
                json={
                    "id": "job-123",
                    "workflowId": "workflow-456",
                    "status": "Queued",
                    "priority": "Default",
                },
            ) @ respx.call
            respx.get(
                "https://test.example.com/webapi/oauth2/token",
            ) @ respx.call
            respx.get(
                "https://test.example.com/webapi/v3/workflows/workflow-456/jobs",
                json={
                    "id": "job-123",
                    "workflowId": "workflow-456",
                    "status": "Queued",
                    "priority": "Default",
                },
            )

        job = await mock_client.jobs.run("workflow-456")

        assert job.id == "job-123"
        assert job.workflow_id == "workflow-456"
        assert job.status == JobStatus.QUEUED

    @pytest.mark.asyncio
    async def test_get_job(self, job_data):
        """Test getting job details."""
        from alteryx_server_py import AsyncAlteryxClient

        client = AsyncAlteryxClient(
            base_url="https://test.example.com/webapi/",
            client_id="test-id",
            client_secret="test-secret",
        )

        # Mock to skip authentication
        client._auth_client = MagicMock()
        client._auth_client.get_token.return_value = "Bearer test-token"

        with respx.mock:
            respx.get(
                "https://test.example.com/webapi/oauth2/token",
            )
            respx.get(
                "https://test.example.com/webapi/v3/jobs/job-123",
                json=job_data,
            ) @ respx.call

        job = await client.jobs.get("job-123")

        assert isinstance(job, Job)
        assert job.id == "job-123"
        assert job.status == JobStatus.COMPLETED
        assert len(job.outputs) == 1
        assert job.outputs[0].name == "output.csv"

    @pytest.mark.asyncio
    async def test_list_jobs(self, job_data):
        """Test listing jobs with filters."""
        from alteryx_server_py import AsyncAlteryxClient

        client = AsyncAlteryxClient(
            base_url="https://test.example.com/webapi/",
            client_id="test-id",
            client_secret="test-secret",
        )

        client._auth_client = MagicMock()
        client._auth_client.get_token.return_value = "Bearer test-token"

        with respx.mock:
            respx.get(
                "https://test.example.com/webapi/oauth2/token",
            )
            respx.get(
                "https://test.example.com/webapi/v3/jobs/",
                json={"jobs": [job_data]},
            ) @ respx.call

        jobs = await client.jobs.list()

        assert len(jobs) == 1
        assert jobs[0].id == "job-123"
        assert jobs[0].status == JobStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_get_job_output(self, job_data):
        """Test downloading job output."""
        from alteryx_server_py import AsyncAlteryxClient

        client = AsyncAlteryxClient(
            base_url="https://test.example.com/webapi/",
            client_id="test-id",
            client_secret="test-secret",
        )

        client._auth_client = MagicMock()
        client._auth_client.get_token.return_value = "Bearer test-token"

        output_content = b"CSV content here"

        with respx.mock:
            respx.get(
                "https://test.example.com/webapi/oauth2/token",
            )
            respx.get(
                "https://test.example.com/webapi/v3/jobs/job-123/output/output-1",
                content=output_content,
            ) @ respx.call

        output = await client.jobs.get_output("job-123", "output-1")

        assert output == output_content

    @pytest.mark.asyncio
    async def test_get_job_messages(self, job_data):
        """Test getting job messages."""
        from alteryx_server_py import AsyncAlteryxClient

        client = AsyncAlteryxClient(
            base_url="https://test.example.com/webapi/",
            client_id="test-id",
            client_secret="test-secret",
        )

        client._auth_client = MagicMock()
        client._auth_client.get_token.return_value = "Bearer test-token"

        with respx.mock:
            respx.get(
                "https://test.example.com/webapi/oauth2/token",
            )
            respx.get(
                "https://test.example.com/webapi/v3/jobs/job-123/messages",
                json={"messages": job_data["messages"]},
            ) @ respx.call

        messages = await client.jobs.get_messages("job-123")

        assert len(messages) == 1
        assert "Job completed successfully" in messages[0]["message"]

    @pytest.mark.asyncio
    async def test_cancel_job(self, job_data):
        """Test cancelling a job."""
        from alteryx_server_py import AsyncAlteryxClient

        client = AsyncAlteryxClient(
            base_url="https://test.example.com/webapi/",
            client_id="test-id",
            client_secret="test-secret",
        )

        client._auth_client = MagicMock()
        client._auth_client.get_token.return_value = "Bearer test-token"

        with respx.mock:
            respx.get(
                "https://test.example.com/webapi/oauth2/token",
            )
            respx.delete(
                "https://test.example.com/webapi/v3/jobs/job-123",
            ) @ respx.call

        await client.jobs.cancel("job-123")

        # Should not raise if successful
        assert True

    @pytest.mark.asyncio
    async def test_cancel_job_not_found(self):
        """Test cancelling a job that doesn't exist."""
        from alteryx_server_py import AsyncAlteryxClient

        client = AsyncAlteryxClient(
            base_url="https://test.example.com/webapi/",
            client_id="test-id",
            client_secret="test-secret",
        )

        client._auth_client = MagicMock()
        client._auth_client.get_token.return_value = "Bearer test-token"

        with respx.mock:
            respx.get(
                "https://test.example.com/webapi/oauth2/token",
            )
            respx.delete(
                "https://test.example.com/webapi/v3/jobs/job-999",
                status_code=404,
            ) @ respx.call

        with pytest.raises(JobNotFoundError):
            await client.jobs.cancel("job-999")
