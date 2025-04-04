import pytest
import os
from dotenv import load_dotenv
from alteryx_gallery_api.client import AlteryxClient

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

@pytest.mark.skipif(
    not all([BASE_URL, API_KEY, API_SECRET]),
    reason="Missing BASE_URL, API_KEY, or API_SECRET environment variables",
)

def test_live_authentication():
    '''Test successful client initialization with valid credentials against a live system.'''
    client = AlteryxClient(BASE_URL, API_KEY, API_SECRET)
    assert client.api_key == API_KEY
    assert client.api_secret == API_SECRET

    # Attempt to fetch workflows to validate authentication
    workflows = client.get_workflows()
    assert isinstance(workflows, list)
