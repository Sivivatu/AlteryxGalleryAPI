from datetime import datetime
from alteryx_gallery_api.models.workflows import Workflow


def test_workflow_parses_reduced_view_payload():
    payload = {
        "id": "wf-123",
        "sourceAppId": "app-abc",
        "name": "Demo Workflow",
        "ownerId": "sub-456",
        "dateCreated": "2024-06-01T12:34:56Z",
        "publishedVersionNumber": 7,
        "isAmp": True,
        "executionMode": "Standard",
    }

    wf = Workflow.model_validate(payload)

    assert wf.id == "wf-123"
    assert wf.source_app_id == "app-abc"
    assert wf.name == "Demo Workflow"
    assert wf.owner_id == "sub-456"
    assert isinstance(wf.date_created, datetime)
    assert wf.published_version_number == 7
    assert wf.is_amp is True
    assert wf.execution_mode.value == "Standard"
