from alteryx_server_py.client import AlteryxClient


def test_env_loading(monkeypatch):
    # Set environment variables
    monkeypatch.setenv("ALTERYX_BASE_URL", "https://env-gallery.com/webapi/")
    monkeypatch.setenv("ALTERYX_CLIENT_ID", "env_key")
    monkeypatch.setenv("ALTERYX_CLIENT_SECRET", "env_secret")

    # Should load from environment if not provided
    client = AlteryxClient.from_env()
    assert client.config.base_url == "https://env-gallery.com/webapi/"
    assert client.config.client_id == "env_key"
    assert client.config.client_secret == "env_secret"

    # Should override environment if provided directly
    client2 = AlteryxClient(base_url="https://direct.com/webapi/", client_id="direct_key", client_secret="direct_secret")
    assert client2.config.base_url == "https://direct.com/webapi/"
    assert client2.config.client_id == "direct_key"
    assert client2.config.client_secret == "direct_secret"
