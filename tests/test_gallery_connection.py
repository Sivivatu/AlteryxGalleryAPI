import os

import pytest
from AlteryxGallery import AlteryxGalleryAPI
from dotenv import load_dotenv

load_dotenv()


# Fixture to initialize the HTTPX client
@pytest.fixture(scope="module")
def http_client():
    base_url = os.getenv("BASE_URL", "NoValueFound")
    with AlteryxGalleryAPI.GalleryClient(base_url) as client:
        client.client_id = os.getenv("CLIENT_ID", "NoValueFound")
        client.client_secret = os.getenv("CLIENT_SECRET", "NoValueFound")
        yield client


# Test case for the authenticate method
def test_authenticate(http_client: AlteryxGalleryAPI.GalleryClient):
    # Test successful authentication
    assert http_client.authenticate(http_client.client_id, http_client.client_secret)

    # Test unsuccessful authentication
    assert not http_client.authenticate("incorrect_username", "incorrect_password")


# Test case for the get_all_workflows method
def test_get_all_workflows(http_client: AlteryxGalleryAPI.GalleryClient):
    response, content = http_client.get_all_workflows(
        name="00-Octopus Download Pipeline"
    )
    assert response.status_code == 200
    assert content[0]["name"] == "00-Octopus Download Pipeline"  # type: ignore
    assert len(content[0]["name"]) > 0  # type: ignore

    response, content = http_client.get_all_workflows(name="Non-existent Workflow")
    assert response.status_code == 200
    assert len(content) == 0


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

# # Test case for the publishing new workflow
# def test_publish_workflow(http_client: AlteryxGalleryAPI.GalleryClient):
#     response, content = http_client.publish_workflow("tests/test.yxzp", "test_workflow")
#     assert response.status_code == 200
# assert content["name"] == "test_workflow"
# assert content["owner"] == "admin"
# assert content["type"] == "Workflow"
# assert content["status"] == "Published"
# assert content["version"] == 1
# assert content["description"] == "This is a test workflow"
# assert content["tags"] == ["test", "workflow"]
