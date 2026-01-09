from alteryx_gallery_api.client import AlteryxClient

def test_env_loading(monkeypatch):
    # Set environment variables
    monkeypatch.setenv("BASE_URL", "https://env-gallery.com/webapi/")
    monkeypatch.setenv("API_KEY", "env_key")
    monkeypatch.setenv("API_SECRET", "env_secret")

    # Should load from environment if not provided
    client = AlteryxClient(authenticate_on_init=False)
    assert client.base_webapi_url == "https://env-gallery.com/webapi/"
    assert client.api_key == "env_key"
    assert client.api_secret == "env_secret"

    # Should override environment if provided directly
    client2 = AlteryxClient(base_url="https://direct.com/webapi/", api_key="direct_key", api_secret="direct_secret", authenticate_on_init=False)
    assert client2.base_webapi_url == "https://direct.com/webapi/"
    assert client2.api_key == "direct_key"
    assert client2.api_secret == "direct_secret"
