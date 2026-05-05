"""Inspect server, collection, and credential resources."""

from __future__ import annotations

from alteryx_server_py import AlteryxClient


def main() -> None:
    """Run the admin resource example."""
    client = AlteryxClient.from_env()

    server_info = client.server.get_info()
    print("Server info:")
    print(server_info.model_dump())

    try:
        server_settings = client.server.get_settings()
        print("Server settings:")
        print(server_settings.model_dump())
    except Exception as exc:
        print(f"Unable to fetch server settings: {exc}")

    collections = client.collections.list(view="Full")
    print(f"Collections visible: {len(collections)}")
    for collection in collections[:5]:
        print(f"  - {collection.id}: {collection.name}")

    credentials = client.credentials.list(view="Full")
    print(f"Credentials visible: {len(credentials)}")
    for credential in credentials[:5]:
        print(f"  - {credential.id}: {credential.username}")


if __name__ == "__main__":
    main()
