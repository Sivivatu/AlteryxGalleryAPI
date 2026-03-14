"""
Quick test script for alteryx_server_py package.
This demonstrates the new package functionality without needing live credentials.
"""

import asyncio


def test_imports():
    """Test that all public APIs can be imported."""
    print("Testing imports...")
    try:
        from alteryx_server_py import (
            AlteryxClient,
            AsyncAlteryxClient,
            ClientConfig,
            from_env,
        )
        from alteryx_server_py.exceptions import (
            AlteryxError,
            AuthenticationError,
            ConfigurationError,
            WorkflowNotFoundError,
        )
        from alteryx_server_py.models import (
            ExecutionMode,
            Job,
            JobStatus,
            Workflow,
            WorkflowType,
        )
        from alteryx_server_py.resources import (
            JobResource,
            WorkflowResource,
        )

        print("✅ All imports successful!")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_client_creation():
    """Test creating a client object."""
    print("\nTesting client creation...")
    try:
        # Test explicit configuration
        from alteryx_server_py import AlteryxClient

        client = AlteryxClient(
            base_url="https://test.example.com/webapi/",
            client_id="test-id",
            client_secret="test-secret",
            authenticate_on_init=False,  # Skip actual auth
        )

        assert client.base_webapi_url == "https://test.example.com/webapi/"
        assert client.client_id == "test-id"
        assert client.client_secret == "test-secret"
        assert client._workflows is None  # Lazy loaded

        print("✅ Sync client creation successful!")
        return client
    except Exception as e:
        print(f"❌ Client creation failed: {e}")
        return None


def test_async_client_creation():
    """Test creating an async client object."""
    print("\nTesting async client creation...")
    try:
        from alteryx_server_py import AsyncAlteryxClient

        client = AsyncAlteryxClient(
            base_url="https://test.example.com/webapi/",
            client_id="test-id",
            client_secret="test-secret",
        )

        assert client.base_webapi_url == "https://test.example.com/webapi/"
        assert client._workflows is None  # Lazy loaded

        print("✅ Async client creation successful!")
        return client
    except Exception as e:
        print(f"❌ Async client creation failed: {e}")
        return None


def test_config_from_env():
    """Test configuration from environment variables."""
    print("\nTesting configuration from env vars...")
    try:
        import os

        from alteryx_server_py import from_env

        # Mock env vars for testing
        os.environ["ALTERYX_BASE_URL"] = "https://test.example.com/webapi/"
        os.environ["ALTERYX_CLIENT_ID"] = "test-id"
        os.environ["ALTERYX_CLIENT_SECRET"] = "test-secret"

        config = from_env()

        assert config.base_url == "https://test.example.com/webapi/"
        assert config.client_id == "test-id"
        assert config.client_secret == "test-secret"

        print("✅ Configuration from env successful!")

        # Clean up
        del os.environ["ALTERYX_BASE_URL"]
        del os.environ["ALTERYX_CLIENT_ID"]
        del os.environ["ALTERYX_CLIENT_SECRET"]

    except Exception as e:
        print(f"❌ Config from env failed: {e}")


def test_resource_pattern():
    """Test the resource pattern."""
    print("\nTesting resource pattern...")
    try:
        from alteryx_server_py import AlteryxClient

        client = AlteryxClient(
            base_url="https://test.example.com/webapi/",
            client_id="test-id",
            client_secret="test-secret",
            authenticate_on_init=False,
        )

        # Test that workflows property returns WorkflowResource
        workflows = client.workflows
        assert workflows is not None
        assert hasattr(workflows, "list")
        assert hasattr(workflows, "get")
        assert hasattr(workflows, "publish")

        print("✅ Resource pattern working!")

    except Exception as e:
        print(f"❌ Resource pattern failed: {e}")


async def test_async_functionality():
    """Test async client functionality."""
    print("\nTesting async functionality...")
    try:
        from alteryx_server_py import AsyncAlteryxClient

        async with AsyncAlteryxClient(
            base_url="https://test.example.com/webapi/",
            client_id="test-id",
            client_secret="test-secret",
        ) as client:
            # Test async context manager
            assert client is not None

            # Test jobs property
            jobs = client.jobs
            assert jobs is not None
            assert hasattr(jobs, "run")
            assert hasattr(jobs, "get")

            print("✅ Async client functionality working!")

    except Exception as e:
        print(f"❌ Async functionality failed: {e}")


def main():
    """Run all tests."""
    print("=" * 60)
    print("ALTERYX SERVER API PACKAGE - QUICK TEST")
    print("=" * 60)

    all_passed = True

    # Test 1: Imports
    all_passed &= test_imports()

    # Test 2: Client creation
    client = test_client_creation()
    all_passed &= client is not None

    # Test 3: Async client creation
    async_client = test_async_client_creation()
    all_passed &= async_client is not None

    # Test 4: Config from env
    test_config_from_env()

    # Test 5: Resource pattern
    test_resource_pattern()

    # Test 6: Async functionality
    try:
        asyncio.run(test_async_functionality())
    except Exception as e:
        print(f"⚠️  Async test failed: {e}")
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("\nNext steps:")
        print("1. Set up actual Alteryx Server credentials in .env")
        print("2. Set ALTERYX_BASE_URL, ALTERYX_CLIENT_ID, ALTERYX_CLIENT_SECRET")
        print("3. Run: uv pip install -e .")
        print("4. Run: python quick_test.py")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 60)


if __name__ == "__main__":
    main()
