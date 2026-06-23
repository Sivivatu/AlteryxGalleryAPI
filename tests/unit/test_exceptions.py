"""
Unit tests for custom exceptions in alteryx_server_py.
"""

import pytest

from alteryx_server_py.exceptions import (
    CollectionNotFoundError,
    CredentialNotFoundError,
    NotFoundError,
    WorkflowNotFoundError,
)


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


@pytest.mark.parametrize(
    ("error_class", "id_attr", "resource_id", "expected_message"),
    [
        (
            CollectionNotFoundError,
            "collection_id",
            "collection-123",
            "Collection 'collection-123' not found",
        ),
        (
            CredentialNotFoundError,
            "credential_id",
            "credential-123",
            "Credential 'credential-123' not found",
        ),
    ],
)
def test_phase_4_not_found_errors(error_class, id_attr, resource_id, expected_message):
    """Collection and credential not-found errors format and store ids."""
    error = error_class(resource_id)

    assert str(error) == expected_message
    assert getattr(error, id_attr) == resource_id
    assert isinstance(error, NotFoundError)
