import os
from http.client import NON_AUTHORITATIVE_INFORMATION

import pytest
from AlteryxGallery import AlteryxGalleryAPI
from dotenv import load_dotenv

load_dotenv()


# Fixture to initialize the HTTPX params
@pytest.fixture(scope="module")
def params():
    params = {}
    params["host_url"] = os.getenv("HOST_URL", "NoValueFound")
    params["client_id"] = os.getenv("CLIENT_ID", "NoValueFound")
    params["client_secret"] = os.getenv("CLIENT_SECRET", "NoValueFound")
    return params



@pytest.fixture(scope="module")
def client(params: dict):
    return AlteryxGalleryAPI.GalleryClient(**params)


class TestHelperMethods:
    def test_no_workflow_provided(self, client: AlteryxGalleryAPI.GalleryClient):
        with pytest.raises(ValueError) as no_value:
            client._check_workflow_id(workflow_name=None, workflow_id=None)
        assert no_value.group_contains(ValueError)
        # assert len(content) == 0

    # def test_check_workflow_by_name(self, client: AlteryxGalleryAPI.GalleryClient):
    #     response, content = client._check_workflow_id(workflow_name="test", workflow_id=None)
    #     assert response.status_code == 200
    #     assert content[0]["name"] == "00-Octopus Download Pipeline"  # type: ignore
    #     assert len(content[0]["name"]) > 0  # type: ignore

    def test_check_workflow_by_id(self, client: AlteryxGalleryAPI.GalleryClient):
        response, content = client._check_workflow_id(workflow_name="test workflow", workflow_id="664e07c7a414ac5c0afe93f7")
        assert response.status_code == 200
        assert content[0]["name"] == self.workflow_name  # type: ignore
        assert len(content[0]["name"]) > 0  # type: ignore

    # def test_check_workflow_not_found(self, client: AlteryxGalleryAPI.GalleryClient):
    #     response, content = client._check_workflow_id(workflow_name="doesnt exist", workflow_id="123456789")
    #     assert response.status_code == 200
    #     assert len(content) == 0


class TestAuthentication:
    # Test case for the authenticate method
    def test_successful_authentication(self, params: dict):
        client = AlteryxGalleryAPI.GalleryClient(**params)
        assert client.authenticate()

    def test_bad_credentials(self):
        params = {}
        params["host_url"] = os.getenv("HOST_URL", "NoValueFound")
        params["client_id"] = "incorrect_username"
        params["client_secret"] = "incorrect_password"
        client = AlteryxGalleryAPI.GalleryClient(**params)
        assert not client.authenticate()


class TestWorkflowMethods:
    # Test case for the get_all_workflows method
    def test_get_workflow(self, client: AlteryxGalleryAPI.GalleryClient):
        response, content = client.get_workflows(name="00-Octopus Download Pipeline")
        assert response.status_code == 200
        assert content[0]["name"] == "00-Octopus Download Pipeline"  # type: ignore
        assert len(content[0]["name"]) > 0  # type: ignore

        response, content = client.get_workflows(name="Non-existent Workflow")
        assert response.status_code == 200
        assert len(content) == 0

    def test_get_all_workflows(self, client: AlteryxGalleryAPI.GalleryClient):
        response, content = client.get_workflows()
        assert response.status_code == 200
        assert len(content[0]["name"]) > 0  # type: ignore


# # Test case for the get_data method
# def test_get_data(http_client: AlteryxGalleryAPI.GalleryClient):
#     response, content = http_client.get_data()
#     assert response.status_code == 200
#     assert len(content) > 0
#     assert "workflows" in content
#     assert "users" in content
#     assert "groups" in content
#     assert "collections" in content
#     assert "tags" in content
#     assert "dataConnections"


# Test case for the publishing new workflow
def test_publish_workflow(client: AlteryxGalleryAPI.GalleryClient):

    from pathlib import Path

    file_path = Path("tests/Test_Upload.yxzp")
    owner_id = os.getenv("TEST_OWNER_ID", "NoValueFound")
    response, content = client.post_publish_workflow(file_path=file_path, name="test workflow", owner_id=owner_id)
    # response, content = http_client.publish_workflow("tests/test.yxzp", "test_workflow")
    assert response.status_code == 200
    # , "Expected status code 200, got {} with a message of {}".format(
    #     response.status_code, response.text
    # )
    # assert content["name"] == "test_workflow"
    # assert content["owner"] == "admin"
    # assert content["type"] == "Workflow"
    # assert content["status"] == "Published"
    # assert content["version"] == 1
    # assert content["description"] == "This is a test workflow"
    # assert content["tags"] == ["test", "workflow"]

