from datetime import datetime
from alteryx_server_py.models.workflows import Workflow


def test_workflow_parses_reduced_view_payload():
    payload = {
        "id": "wf-123",
        "name": "Demo Workflow",
        "ownerId": "sub-456",
        "dateCreated": "2024-06-01T12:34:56Z",
        "workflowType": "Standard",
        "executionMode": "Safe",
    }

    wf = Workflow.model_validate(payload)

    assert wf.id == "wf-123"
    assert wf.name == "Demo Workflow"
    assert wf.owner_id == "sub-456"
    assert isinstance(wf.created_date, datetime)
    assert wf.execution_mode.value == "Safe"
