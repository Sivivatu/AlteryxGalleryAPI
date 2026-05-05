from unittest.mock import MagicMock

import pytest

from alteryx_server_py.client import AlteryxClient
from alteryx_server_py.models import Workflow


@pytest.fixture
def client():
    """Create an AlteryxClient with mocked auth."""
    c = AlteryxClient(
        base_url="https://example.com/webapi/",
        client_id="key",
        client_secret="secret",
    )
    c._auth_client = MagicMock()
    c._auth_client.get_token.return_value = "Bearer mock_token"
    return c


def test_get_workflows_list_payload(monkeypatch, client: AlteryxClient):
    # Reason: _request already returns parsed JSON (list/dict), not a Response object.
    payload = [
        {
            "id": "wf-1",
            "name": "One",
            "ownerId": "sub-1",
            "dateCreated": "2024-01-01T00:00:00Z",
            "workflowType": "Standard",
            "executionMode": "Safe",
        },
        {
            "id": "wf-2",
            "name": "Two",
            "ownerId": "sub-2",
            "dateCreated": "2024-01-02T00:00:00Z",
            "workflowType": "Standard",
            "executionMode": "Safe",
        },
    ]

    monkeypatch.setattr(client, "_request", lambda *a, **k: payload)

    result = client.workflows.list()
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(w, Workflow) for w in result)
    ids = {w.id for w in result}
    assert ids == {"wf-1", "wf-2"}
    wf1 = next(w for w in result if w.id == "wf-1")
    assert wf1.name == "One"


def test_get_workflows_single_payload(monkeypatch, client: AlteryxClient):
    payload = {
        "id": "wf-9",
        "name": "Nine",
        "ownerId": "sub-9",
        "dateCreated": "2024-02-02T00:00:00Z",
        "workflowType": "Standard",
        "executionMode": "SemiSafe",
    }

    monkeypatch.setattr(client, "_request", lambda *a, **k: payload)

    result = client.workflows.list()
    assert isinstance(result, list)
    assert len(result) == 1
    wf = result[0]
    assert isinstance(wf, Workflow)
    assert wf.execution_mode.value == "SemiSafe"
