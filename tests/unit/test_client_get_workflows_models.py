from types import SimpleNamespace
from typing import Any, Dict

import pytest

from alteryx_gallery_api.client import AlteryxClient
from alteryx_gallery_api.models import Workflow


class DummyResponse:
    def __init__(self, payload: Any, status_code: int = 200):
        self._payload = payload
        self.status_code = status_code
        self.text = ""
        self.headers = {}

    def json(self) -> Any:
        return self._payload

    def raise_for_status(self) -> None:
        if not (200 <= self.status_code < 300):
            raise Exception("HTTP error")


@pytest.fixture
def client(monkeypatch):
    c = AlteryxClient(
        base_url="https://example.com/webapi/",
        api_key="key",
        api_secret="secret",
        authenticate_on_init=False,
    )
    return c


def test_get_workflows_list_payload(monkeypatch, client: AlteryxClient):
    payload = [
        {
            "id": "wf-1",
            "sourceAppId": "app-1",
            "name": "One",
            "ownerId": "sub-1",
            "dateCreated": "2024-01-01T00:00:00Z",
            "publishedVersionNumber": 1,
            "isAmp": True,
            "executionMode": "Standard",
        },
        {
            "id": "wf-2",
            "sourceAppId": "app-2",
            "name": "Two",
            "ownerId": "sub-2",
            "dateCreated": "2024-01-02T00:00:00Z",
            "publishedVersionNumber": 2,
            "isAmp": False,
            "executionMode": "Safe",
        },
    ]

    monkeypatch.setattr(client, "_request", lambda *a, **k: DummyResponse(payload))

    result = client.get_workflows()
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
        "sourceAppId": "app-9",
        "name": "Nine",
        "ownerId": "sub-9",
        "dateCreated": "2024-02-02T00:00:00Z",
        "publishedVersionNumber": 9,
        "isAmp": True,
        "executionMode": "SemiSafe",
    }

    monkeypatch.setattr(client, "_request", lambda *a, **k: DummyResponse(payload))

    result = client.get_workflows("wf-9")
    assert isinstance(result, list)
    assert len(result) == 1
    wf = result[0]
    assert isinstance(wf, Workflow)
    assert wf.execution_mode.value == "SemiSafe"
