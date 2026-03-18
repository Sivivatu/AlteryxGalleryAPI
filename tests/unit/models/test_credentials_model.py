"""Unit tests for credential and server Pydantic models."""

from alteryx_server_py.models.credentials import (
    Credential,
    CredentialCreateRequest,
    CredentialUpdateRequest,
)
from alteryx_server_py.models.server import ServerInfo, ServerSettings


class TestCredentialModel:
    """Test Credential model validation."""

    def test_credential_from_api_response(self):
        """Test creating a credential from API data."""
        data = {
            "id": "cred-1",
            "username": "CONTOSO\\svc-alteryx",
            "ownerId": "user-1",
        }

        credential = Credential.model_validate(data)

        assert credential.id == "cred-1"
        assert credential.username == "CONTOSO\\svc-alteryx"
        assert credential.owner_id == "user-1"

    def test_create_request_serialization(self):
        """Test credential create request serialization."""
        request = CredentialCreateRequest(username="CONTOSO\\svc", password="secret")
        data = request.model_dump(by_alias=True, exclude_none=True)

        assert data == {"username": "CONTOSO\\svc", "password": "secret"}

    def test_update_request_serialization(self):
        """Test credential update request uses documented field name."""
        request = CredentialUpdateRequest(new_password="new-secret")
        data = request.model_dump(by_alias=True, exclude_none=True)

        assert data == {"NewPassword": "new-secret"}


class TestServerModels:
    """Test generic server models."""

    def test_server_info_allows_extra_fields(self):
        """Test server info preserves undocumented fields."""
        model = ServerInfo.model_validate({"serverVersion": "2025.2"})
        assert model.model_extra["serverVersion"] == "2025.2"

    def test_server_settings_allows_extra_fields(self):
        """Test server settings preserves undocumented fields."""
        model = ServerSettings.model_validate({"galleryName": "Test Server"})
        assert model.model_extra["galleryName"] == "Test Server"