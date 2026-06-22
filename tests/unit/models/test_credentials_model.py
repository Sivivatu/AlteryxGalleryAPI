"""Unit tests for credential and server Pydantic models."""

import pytest

from alteryx_server_py.models.credentials import (
    Credential,
    CredentialUserGroupShareRequest,
    CredentialUserShareRequest,
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

    def test_credential_allows_documented_extra_fields(self):
        """Test credential model remains permissive for undocumented fields."""
        data = {
            "id": "cred-1",
            "username": "CONTOSO\\svc-alteryx",
            "undocumentedField": "kept",
        }

        credential = Credential.model_validate(data)

        assert credential.model_extra["undocumentedField"] == "kept"

    def test_user_share_request_serialization(self):
        """Test credential user share request serialization."""
        request = CredentialUserShareRequest(user_id="user-1")
        data = request.model_dump(by_alias=True, exclude_none=True)

        assert data == {"userId": "user-1"}

    def test_user_group_share_request_serialization(self):
        """Test credential user-group share request serialization."""
        request = CredentialUserGroupShareRequest(user_group_id="group-1")
        data = request.model_dump(by_alias=True, exclude_none=True)

        assert data == {"userGroupId": "group-1"}


class TestServerModels:
    """Test generic server models."""

    @pytest.mark.parametrize(
        ("model_class", "payload", "field_name", "expected_value"),
        [
            (ServerInfo, {"serverVersion": "2025.2"}, "server_version", "2025.2"),
            (
                ServerSettings,
                {"galleryName": "Test Server"},
                "gallery_name",
                "Test Server",
            ),
        ],
    )
    def test_server_models_map_aliases_and_allow_extra_fields(
        self,
        model_class,
        payload,
        field_name,
        expected_value,
    ):
        """Test server models map documented aliases and preserve extras."""
        model = model_class.model_validate({**payload, "undocumentedField": "kept"})

        assert getattr(model, field_name) == expected_value
        assert model.model_extra is not None
        assert model.model_extra["undocumentedField"] == "kept"
