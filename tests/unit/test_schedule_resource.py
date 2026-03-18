"""
Unit tests for ScheduleResource.
"""

from unittest.mock import MagicMock

import pytest
import respx

from alteryx_server_py import AlteryxClient, AsyncAlteryxClient
from alteryx_server_py.exceptions import ScheduleNotFoundError
from alteryx_server_py.models import Schedule, ScheduleFrequency, ScheduleStatus


@pytest.fixture
def mock_client():
    """Create a mock sync client for testing."""
    client = AlteryxClient(
        base_url="https://test.example.com/webapi/",
        client_id="test-id",
        client_secret="test-secret",
    )
    client._auth_client = MagicMock()
    client._auth_client.get_token.return_value = "Bearer test-token"
    return client


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
def schedule_data():
    """Sample schedule data for testing."""
    return {
        "id": "sched-123",
        "workflowId": "workflow-456",
        "name": "Daily Report",
        "ownerId": "user-789",
        "comment": "Runs every day at 8am",
        "frequency": "Daily",
        "status": "Active",
        "enabled": True,
        "iteration": None,
        "startDate": "2024-01-01T08:00:00Z",
        "endDate": None,
        "lastRunDate": "2024-06-15T08:00:00Z",
        "nextRunDate": "2024-06-16T08:00:00Z",
        "dateCreated": "2024-01-01T00:00:00Z",
        "lastUpdated": "2024-06-15T08:05:00Z",
    }


class TestScheduleResource:
    """Test ScheduleResource functionality."""

    @pytest.mark.asyncio
    async def test_list_schedules(self, async_client, schedule_data):
        """Test listing schedules returns valid Schedule objects."""
        with respx.mock:
            respx.get(
                "https://test.example.com/webapi/v3/schedules/",
            ).respond(json=[schedule_data])

            schedules = await async_client.schedules.list()

        assert len(schedules) == 1
        assert isinstance(schedules[0], Schedule)
        assert schedules[0].id == "sched-123"
        assert schedules[0].name == "Daily Report"
        assert schedules[0].frequency == ScheduleFrequency.DAILY

    @pytest.mark.asyncio
    async def test_list_schedules_with_workflow_filter(self, async_client, schedule_data):
        """Test listing schedules filtered by workflow ID."""
        with respx.mock:
            respx.get(
                "https://test.example.com/webapi/v3/schedules/",
            ).respond(json={"schedules": [schedule_data]})

            schedules = await async_client.schedules.list(workflow_id="workflow-456")

        assert len(schedules) == 1
        assert schedules[0].workflow_id == "workflow-456"

    @pytest.mark.asyncio
    async def test_list_schedules_empty(self, async_client):
        """Test listing schedules when none exist."""
        with respx.mock:
            respx.get(
                "https://test.example.com/webapi/v3/schedules/",
            ).respond(json=[])

            schedules = await async_client.schedules.list()

        assert schedules == []

    @pytest.mark.asyncio
    async def test_get_schedule(self, async_client, schedule_data):
        """Test getting schedule details by ID."""
        with respx.mock:
            respx.get(
                "https://test.example.com/webapi/v3/schedules/sched-123",
            ).respond(json=schedule_data)

            schedule = await async_client.schedules.get("sched-123")

        assert isinstance(schedule, Schedule)
        assert schedule.id == "sched-123"
        assert schedule.workflow_id == "workflow-456"
        assert schedule.status == ScheduleStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_get_schedule_not_found(self, async_client):
        """Test getting a schedule that doesn't exist."""
        with respx.mock:
            respx.get(
                "https://test.example.com/webapi/v3/schedules/sched-999",
            ).respond(404)

            with pytest.raises(ScheduleNotFoundError):
                await async_client.schedules.get("sched-999")

    @pytest.mark.asyncio
    async def test_create_schedule(self, async_client, schedule_data):
        """Test creating a new schedule."""
        with respx.mock:
            respx.post(
                "https://test.example.com/webapi/v3/schedules/",
            ).respond(json=schedule_data)

            schedule = await async_client.schedules.create(
                workflow_id="workflow-456",
                name="Daily Report",
                owner_id="user-789",
                frequency="Daily",
                comment="Runs every day at 8am",
            )

        assert isinstance(schedule, Schedule)
        assert schedule.name == "Daily Report"
        assert schedule.frequency == ScheduleFrequency.DAILY

    @pytest.mark.asyncio
    async def test_update_schedule(self, async_client, schedule_data):
        """Test updating an existing schedule."""
        updated_data = {**schedule_data, "name": "Weekly Report", "frequency": "Weekly"}

        with respx.mock:
            respx.put(
                "https://test.example.com/webapi/v3/schedules/sched-123",
            ).respond(json=updated_data)

            schedule = await async_client.schedules.update(
                "sched-123",
                name="Weekly Report",
                frequency="Weekly",
            )

        assert schedule.name == "Weekly Report"
        assert schedule.frequency == ScheduleFrequency.WEEKLY

    @pytest.mark.asyncio
    async def test_update_schedule_not_found(self, async_client):
        """Test updating a schedule that doesn't exist."""
        with respx.mock:
            respx.put(
                "https://test.example.com/webapi/v3/schedules/sched-999",
            ).respond(404)

            with pytest.raises(ScheduleNotFoundError):
                await async_client.schedules.update("sched-999", name="New Name")

    @pytest.mark.asyncio
    async def test_delete_schedule(self, async_client):
        """Test deleting a schedule."""
        with respx.mock:
            respx.delete(
                "https://test.example.com/webapi/v3/schedules/sched-123",
            ).respond(204)

            await async_client.schedules.delete("sched-123")

        # Should not raise
        assert True

    @pytest.mark.asyncio
    async def test_delete_schedule_not_found(self, async_client):
        """Test deleting a schedule that doesn't exist."""
        with respx.mock:
            respx.delete(
                "https://test.example.com/webapi/v3/schedules/sched-999",
            ).respond(404)

            with pytest.raises(ScheduleNotFoundError):
                await async_client.schedules.delete("sched-999")

    @pytest.mark.asyncio
    async def test_enable_schedule(self, async_client, schedule_data):
        """Test enabling a schedule."""
        enabled_data = {**schedule_data, "enabled": True, "status": "Active"}

        with respx.mock:
            respx.post(
                "https://test.example.com/webapi/v3/schedules/sched-123/enable",
            ).respond(json=enabled_data)

            schedule = await async_client.schedules.enable("sched-123")

        assert schedule.enabled is True

    @pytest.mark.asyncio
    async def test_disable_schedule(self, async_client, schedule_data):
        """Test disabling a schedule."""
        disabled_data = {**schedule_data, "enabled": False, "status": "Inactive"}

        with respx.mock:
            respx.post(
                "https://test.example.com/webapi/v3/schedules/sched-123/disable",
            ).respond(json=disabled_data)

            schedule = await async_client.schedules.disable("sched-123")

        assert schedule.enabled is False

    @pytest.mark.asyncio
    async def test_enable_schedule_not_found(self, async_client):
        """Test enabling a schedule that doesn't exist."""
        with respx.mock:
            respx.post(
                "https://test.example.com/webapi/v3/schedules/sched-999/enable",
            ).respond(404)

            with pytest.raises(ScheduleNotFoundError):
                await async_client.schedules.enable("sched-999")
