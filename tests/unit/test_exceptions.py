"""
Unit tests for custom exceptions in alteryx_server_py.
"""

import pytest

import importlib.util
import sys

# Load exceptions module directly to avoid broken imports in other modules
_spec = importlib.util.spec_from_file_location(
    "alteryx_server_py.exceptions",
    __file__.replace("tests/unit/test_exceptions.py", "src/alteryx_server_py/exceptions.py"),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
WorkflowNotFoundError = _mod.WorkflowNotFoundError
NotFoundError = _mod.NotFoundError


class TestWorkflowNotFoundError:
    """Tests for WorkflowNotFoundError."""

    def test_default_message(self):
        """Default message is generated from workflow_id when no message provided."""
        error = WorkflowNotFoundError("abc-123")
        assert str(error) == "Workflow 'abc-123' not found"

    def test_custom_message(self):
        """Custom message overrides the default when provided."""
        custom_msg = "Workflow 'abc-123' not found for update"
        error = WorkflowNotFoundError("abc-123", message=custom_msg)
        assert str(error) == custom_msg

    def test_workflow_id_stored(self):
        """workflow_id attribute is always set on the exception."""
        error = WorkflowNotFoundError("abc-123")
        assert error.workflow_id == "abc-123"

    def test_workflow_id_stored_with_custom_message(self):
        """workflow_id attribute is set even when a custom message is provided."""
        error = WorkflowNotFoundError("abc-123", message="Custom message")
        assert error.workflow_id == "abc-123"

    def test_inherits_not_found_error(self):
        """WorkflowNotFoundError is a subclass of NotFoundError."""
        error = WorkflowNotFoundError("abc-123")
        assert isinstance(error, NotFoundError)

    def test_none_message_uses_default(self):
        """Passing message=None explicitly still uses the default format."""
        error = WorkflowNotFoundError("abc-123", message=None)
        assert str(error) == "Workflow 'abc-123' not found"
