"""Unit tests for JobResource."""

from unittest.mock import MagicMock

import pytest
import respx

from alteryx_server_py import AsyncAlteryxClient
from alteryx_server_py.exceptions import JobExecutionError, JobNotFoundError, TimeoutError
from alteryx_server_py.models import Job, JobStatus


@pytest.fixture
def async_client():
    """Create a mock async client for testing."""
    client = AsyncAlteryxClient(
        base_url="https://test.example.com/webapi/",
        client_id="test-id",
        client_secret="test-secret",
    )
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
    async def test_run_job(self, async_client):
        """Test running a workflow job."""
        with respx.mock:
            respx.post(
                "https://test.example.com/webapi/v3/workflows/workflow-456/jobs",
            ).respond(
                json={
                    "id": "job-123",
                    "workflowId": "workflow-456",
                    "status": "Queued",
                    "priority": "Default",
                    "createDate": "2024-01-01T12:00:00Z",
                },
            )

            job = await async_client.jobs.run("workflow-456")

        assert job.id == "job-123"
        assert job.workflow_id == "workflow-456"
        assert job.status == JobStatus.QUEUED

    @pytest.mark.asyncio
    async def test_get_job(self, async_client, job_data):
        """Test getting job details."""
        with respx.mock:
            respx.get(
                "https://test.example.com/webapi/v3/jobs/job-123",
            ).respond(json=job_data)

            job = await async_client.jobs.get("job-123")

        assert isinstance(job, Job)
        assert job.id == "job-123"
        assert job.status == JobStatus.COMPLETED
        assert len(job.outputs) == 1
        assert job.outputs[0].name == "output.csv"

    @pytest.mark.asyncio
    async def test_list_jobs(self, async_client, job_data):
        """Test listing jobs with filters."""
        with respx.mock:
            respx.get(
                "https://test.example.com/webapi/v3/jobs/",
            ).respond(json={"jobs": [job_data]})

            jobs = await async_client.jobs.list()

        assert len(jobs) == 1
        assert jobs[0].id == "job-123"
        assert jobs[0].status == JobStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_get_job_output(self, async_client):
        """Test downloading job output."""
        output_content = b"CSV content here"

        with respx.mock:
            respx.get(
                "https://test.example.com/webapi/v3/jobs/job-123/output/output-1",
            ).respond(content=output_content)

            output = await async_client.jobs.get_output("job-123", "output-1")

        assert output == output_content

    @pytest.mark.asyncio
    async def test_get_job_messages(self, async_client, job_data):
        """Test getting job messages."""
        with respx.mock:
            respx.get(
                "https://test.example.com/webapi/v3/jobs/job-123/messages",
            ).respond(json={"messages": job_data["messages"]})

            messages = await async_client.jobs.get_messages("job-123")

        assert len(messages) == 1
        assert "Job completed successfully" in messages[0]["message"]

    @pytest.mark.asyncio
    async def test_cancel_job(self, async_client):
        """Test cancelling a job."""
        with respx.mock:
            respx.delete(
                "https://test.example.com/webapi/v3/jobs/job-123",
            ).respond(204)

            await async_client.jobs.cancel("job-123")

        # Should not raise if successful
        assert True

    @pytest.mark.asyncio
    async def test_cancel_job_not_found(self, async_client):
        """Test cancelling a job that doesn't exist."""
        with respx.mock:
            respx.delete(
                "https://test.example.com/webapi/v3/jobs/job-999",
            ).respond(404)

            with pytest.raises(JobNotFoundError):
                await async_client.jobs.cancel("job-999")

    @pytest.mark.asyncio
    async def test_run_and_wait_raises_timeout(self, async_client):
        """Test run_and_wait raises TimeoutError when a job never finishes."""
        with respx.mock:
            respx.post(
                "https://test.example.com/webapi/v3/workflows/workflow-456/jobs",
            ).respond(
                json={
                    "id": "job-123",
                    "workflowId": "workflow-456",
                    "status": "Queued",
                    "priority": "Default",
                    "createDate": "2024-01-01T12:00:00Z",
                },
            )
            respx.get(
                "https://test.example.com/webapi/v3/jobs/job-123",
            ).respond(
                json={
                    "id": "job-123",
                    "workflowId": "workflow-456",
                    "status": "Running",
                    "priority": "Default",
                    "createDate": "2024-01-01T12:00:00Z",
                },
            )

            with pytest.raises(TimeoutError):
                await async_client.jobs.run_and_wait(
                    "workflow-456",
                    timeout=0,
                    poll_interval=0,
                )

    @pytest.mark.asyncio
    async def test_run_and_wait_raises_job_execution_error(self, async_client):
        """Test run_and_wait raises JobExecutionError when the job fails."""
        with respx.mock:
            respx.post(
                "https://test.example.com/webapi/v3/workflows/workflow-456/jobs",
            ).respond(
                json={
                    "id": "job-123",
                    "workflowId": "workflow-456",
                    "status": "Queued",
                    "priority": "Default",
                    "createDate": "2024-01-01T12:00:00Z",
                },
            )
            respx.get(
                "https://test.example.com/webapi/v3/jobs/job-123",
            ).respond(
                json={
                    "id": "job-123",
                    "workflowId": "workflow-456",
                    "status": "Error",
                    "priority": "Default",
                    "createDate": "2024-01-01T12:00:00Z",
                    "messages": [{"message": "Job failed", "level": "Error"}],
                },
            )

            with pytest.raises(JobExecutionError):
                await async_client.jobs.run_and_wait(
                    "workflow-456",
                    timeout=1,
                    poll_interval=0,
                )
