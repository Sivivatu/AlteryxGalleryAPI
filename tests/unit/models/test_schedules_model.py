"""
Unit tests for Schedule Pydantic models.
"""

import pytest

from alteryx_server_py.models.common import ScheduleFrequency, ScheduleStatus
from alteryx_server_py.models.schedules import (
    Schedule,
    ScheduleCreateRequest,
    ScheduleUpdateRequest,
)


class TestScheduleModel:
    """Test Schedule model validation."""

    def test_schedule_from_api_response(self):
        """Test creating Schedule from typical API response data."""
        data = {
            "id": "sched-123",
            "workflowId": "wf-456",
            "name": "Daily Run",
            "ownerId": "user-789",
            "frequency": "Daily",
            "status": "Active",
            "enabled": True,
            "startDate": "2024-01-01T08:00:00Z",
            "dateCreated": "2024-01-01T00:00:00Z",
        }
        schedule = Schedule.model_validate(data)

        assert schedule.id == "sched-123"
        assert schedule.workflow_id == "wf-456"
        assert schedule.frequency == ScheduleFrequency.DAILY
        assert schedule.status == ScheduleStatus.ACTIVE
        assert schedule.enabled is True

    def test_schedule_minimal_fields(self):
        """Test Schedule with minimal required fields."""
        data = {
            "id": "sched-1",
            "workflowId": "wf-1",
            "name": "Test",
            "ownerId": "user-1",
            "frequency": "Once",
            "status": "Active",
            "enabled": True,
        }
        schedule = Schedule.model_validate(data)

        assert schedule.id == "sched-1"
        assert schedule.comment is None
        assert schedule.last_run_date is None

    def test_schedule_rejects_unknown_fields(self):
        """Test that Schedule rejects unknown fields (strict mode)."""
        data = {
            "id": "sched-1",
            "workflowId": "wf-1",
            "name": "Test",
            "ownerId": "user-1",
            "frequency": "Once",
            "status": "Active",
            "enabled": True,
            "unknownField": "value",
        }
        with pytest.raises(Exception):
            Schedule.model_validate(data)


class TestScheduleCreateRequest:
    """Test ScheduleCreateRequest model."""

    def test_create_request_serialization(self):
        """Test create request serializes with camelCase aliases."""
        request = ScheduleCreateRequest(
            workflow_id="wf-123",
            name="Test Schedule",
            owner_id="user-456",
            frequency=ScheduleFrequency.DAILY,
        )
        data = request.model_dump(by_alias=True, exclude_none=True)

        assert data["workflowId"] == "wf-123"
        assert data["ownerId"] == "user-456"
        assert data["frequency"] == "Daily"

    def test_create_request_with_all_fields(self):
        """Test create request with all optional fields."""
        request = ScheduleCreateRequest(
            workflow_id="wf-123",
            name="Full Schedule",
            owner_id="user-456",
            frequency=ScheduleFrequency.WEEKLY,
            comment="Runs weekly",
            iteration="every Monday",
        )
        data = request.model_dump(by_alias=True, exclude_none=True)

        assert "comment" in data
        assert "iteration" in data


class TestScheduleUpdateRequest:
    """Test ScheduleUpdateRequest model."""

    def test_update_request_partial(self):
        """Test update request with only some fields."""
        request = ScheduleUpdateRequest(name="New Name")
        data = request.model_dump(by_alias=True, exclude_none=True)

        assert data == {"name": "New Name"}

    def test_update_request_enabled(self):
        """Test update request with enabled flag."""
        request = ScheduleUpdateRequest(enabled=False)
        data = request.model_dump(by_alias=True, exclude_none=True)

        assert data == {"enabled": False}
