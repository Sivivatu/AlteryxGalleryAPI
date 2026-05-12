"""Live integration tests for the synchronous Alteryx client."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator
from uuid import uuid4

import pytest
from dotenv import load_dotenv

from alteryx_server_py import AlteryxClient
from alteryx_server_py.exceptions import AuthenticationError, WorkflowNotFoundError
from alteryx_server_py.models.common import JobStatus

load_dotenv()

pytestmark = pytest.mark.live

LIVE_ENV_VARS = (
    "ALTERYX_BASE_URL",
    "ALTERYX_CLIENT_ID",
    "ALTERYX_CLIENT_SECRET",
)
TEST_OWNER_ID_ENV = "ALTERYX_TEST_OWNER_ID"
KNOWN_WORKFLOW_ID_ENV = "ALTERYX_TEST_WORKFLOW_ID"
JOB_TIMEOUT_ENV = "ALTERYX_TEST_JOB_TIMEOUT"
POLL_INTERVAL_ENV = "ALTERYX_TEST_POLL_INTERVAL"
DEFAULT_JOB_TIMEOUT = 600
DEFAULT_POLL_INTERVAL = 10
TEST_PACKAGE_PATH = Path(__file__).resolve().parents[1] / "Test_Upload.yxzp"


@dataclass(frozen=True)
class LiveServerSettings:
    """Settings required for any live server test.

    Attributes:
        base_url: Base URL of the target Alteryx Server.
        client_id: OAuth2 client identifier.
        client_secret: OAuth2 client secret.
        known_workflow_id: Optional workflow ID reserved for smoke reads.
    """

    base_url: str
    client_id: str
    client_secret: str
    known_workflow_id: str | None = None


@dataclass(frozen=True)
class LiveMutationSettings:
    """Settings required for destructive live tests.

    Attributes:
        owner_id: Owner ID used when publishing test workflows.
        job_timeout: Maximum number of seconds to wait for job completion.
        poll_interval: Seconds between job status checks.
    """

    owner_id: str
    job_timeout: int = DEFAULT_JOB_TIMEOUT
    poll_interval: int = DEFAULT_POLL_INTERVAL


def _missing_env_vars(variable_names: tuple[str, ...]) -> list[str]:
    """Return the list of missing environment variables.

    Args:
        variable_names: Environment variable names to inspect.

    Returns:
        list[str]: Missing variable names.
    """

    return [variable_name for variable_name in variable_names if not os.getenv(variable_name)]


def _read_int_env(variable_name: str, default: int) -> int:
    """Read an optional integer environment variable.

    Args:
        variable_name: Name of the environment variable.
        default: Default value when the variable is not set.

    Returns:
        int: Parsed integer value.

    Raises:
        ValueError: If the provided value cannot be parsed as an integer.
    """

    raw_value = os.getenv(variable_name)
    if raw_value is None:
        return default

    try:
        return int(raw_value)
    except ValueError as exc:
        raise ValueError(f"{variable_name} must be an integer, got {raw_value!r}") from exc


def _build_client(settings: LiveServerSettings) -> AlteryxClient:
    """Build a live client from resolved settings.

    Args:
        settings: Live server configuration.

    Returns:
        AlteryxClient: Configured synchronous client.
    """

    return AlteryxClient(
        base_url=settings.base_url,
        client_id=settings.client_id,
        client_secret=settings.client_secret,
    )


@pytest.fixture(scope="session")
def live_settings() -> LiveServerSettings:
    """Resolve environment variables for live smoke tests.

    Returns:
        LiveServerSettings: Resolved live server settings.
    """

    missing = _missing_env_vars(LIVE_ENV_VARS)
    if missing:
        pytest.skip(f"Missing live test environment variables: {', '.join(missing)}")

    return LiveServerSettings(
        base_url=os.environ["ALTERYX_BASE_URL"],
        client_id=os.environ["ALTERYX_CLIENT_ID"],
        client_secret=os.environ["ALTERYX_CLIENT_SECRET"],
        known_workflow_id=os.getenv(KNOWN_WORKFLOW_ID_ENV),
    )


@pytest.fixture(scope="session")
def mutation_settings() -> LiveMutationSettings:
    """Resolve environment variables for destructive live tests.

    Returns:
        LiveMutationSettings: Resolved mutation test settings.
    """

    owner_id = os.getenv(TEST_OWNER_ID_ENV)
    if not owner_id:
        pytest.skip(f"Missing destructive live test environment variable: {TEST_OWNER_ID_ENV}")

    return LiveMutationSettings(
        owner_id=owner_id,
        job_timeout=_read_int_env(JOB_TIMEOUT_ENV, DEFAULT_JOB_TIMEOUT),
        poll_interval=_read_int_env(POLL_INTERVAL_ENV, DEFAULT_POLL_INTERVAL),
    )


@pytest.fixture(scope="session")
def live_client(live_settings: LiveServerSettings) -> Iterator[AlteryxClient]:
    """Create a shared live client for test execution.

    Args:
        live_settings: Resolved live server settings.

    Yields:
        Iterator[AlteryxClient]: Initialized client instance.
    """

    with _build_client(live_settings) as client:
        yield client


@pytest.fixture
def unique_workflow_name(request: pytest.FixtureRequest) -> str:
    """Generate a unique workflow name for an individual test.

    Args:
        request: Pytest fixture request object.

    Returns:
        str: Unique workflow name.
    """

    suffix = uuid4().hex[:8]
    return f"copilot-live-{request.node.name}-{suffix}"


@pytest.fixture
def test_package_path() -> Path:
    """Return the packaged workflow used by destructive live tests.

    Returns:
        Path: Path to the test package.
    """

    if not TEST_PACKAGE_PATH.exists():
        raise FileNotFoundError(f"Live test package not found: {TEST_PACKAGE_PATH}")
    return TEST_PACKAGE_PATH


@pytest.fixture
def cleanup_workflow_ids(live_client: AlteryxClient) -> Iterator[list[str]]:
    """Track workflows that must be deleted during teardown.

    Args:
        live_client: Initialized live client.

    Yields:
        Iterator[list[str]]: Mutable list of workflow IDs to clean up.
    """

    workflow_ids: list[str] = []
    yield workflow_ids

    cleanup_errors: list[str] = []
    for workflow_id in reversed(workflow_ids):
        try:
            live_client.workflows.delete(workflow_id)
        except WorkflowNotFoundError:
            continue
        except Exception as exc:
            cleanup_errors.append(f"{workflow_id}: {exc}")

    if cleanup_errors:
        pytest.fail("Failed to clean up live workflows: " + "; ".join(cleanup_errors))


@pytest.fixture
def published_workflow(
    live_client: AlteryxClient,
    mutation_settings: LiveMutationSettings,
    unique_workflow_name: str,
    test_package_path: Path,
    cleanup_workflow_ids: list[str],
):
    """Publish a sandbox workflow and register it for cleanup.

    Args:
        live_client: Initialized live client.
        mutation_settings: Destructive test configuration.
        unique_workflow_name: Unique workflow name for this test.
        test_package_path: Packaged workflow path.
        cleanup_workflow_ids: Workflow IDs to delete after the test.

    Returns:
        Workflow: Published workflow model.
    """

    workflow = live_client.workflows.publish(
        file_path=str(test_package_path),
        name=unique_workflow_name,
        owner_id=mutation_settings.owner_id,
        comments="Live integration test publish",
    )
    cleanup_workflow_ids.append(workflow.id)
    return workflow


@pytest.fixture
def completed_job(live_client: AlteryxClient, mutation_settings: LiveMutationSettings, published_workflow):
    """Run a published workflow to completion.

    Args:
        live_client: Initialized live client.
        mutation_settings: Destructive test configuration.
        published_workflow: Published workflow fixture.

    Returns:
        Job: Completed job model.
    """

    return live_client.jobs.run_and_wait(
        workflow_id=published_workflow.id,
        timeout=mutation_settings.job_timeout,
        poll_interval=mutation_settings.poll_interval,
    )


@pytest.mark.smoke
def test_live_authentication_smoke(live_client: AlteryxClient) -> None:
    """Authenticate successfully and reach a live workflow endpoint.

    Args:
        live_client: Initialized live client.
    """

    workflows = live_client.workflows.list(page_size=1)

    assert isinstance(workflows, list)


@pytest.mark.smoke
def test_live_invalid_credentials_fail_with_auth_error(live_settings: LiveServerSettings) -> None:
    """Reject invalid OAuth credentials with an authentication-specific exception.

    Args:
        live_settings: Resolved live server settings.
    """

    with pytest.raises(AuthenticationError):
        with AlteryxClient(
            base_url=live_settings.base_url,
            client_id="invalid-client-id",
            client_secret="invalid-client-secret",
        ) as client:
            client.workflows.list(page_size=1)


@pytest.mark.smoke
def test_live_list_workflows_smoke(live_client: AlteryxClient) -> None:
    """List workflows from the live server and validate basic model fields.

    Args:
        live_client: Initialized live client.
    """

    workflows = live_client.workflows.list(page_size=5)

    assert isinstance(workflows, list)
    for workflow in workflows:
        assert workflow.id
        assert workflow.name


@pytest.mark.smoke
def test_live_get_workflow_by_id_smoke(live_client: AlteryxClient, live_settings: LiveServerSettings) -> None:
    """Fetch a single workflow by ID from the live server.

    Args:
        live_client: Initialized live client.
        live_settings: Resolved live server settings.
    """

    workflow_id = live_settings.known_workflow_id
    if workflow_id is None:
        workflows = live_client.workflows.list(page_size=1)
        if not workflows:
            pytest.skip(f"Set {KNOWN_WORKFLOW_ID_ENV} or ensure at least one workflow exists for read-only smoke validation")
        workflow_id = workflows[0].id

    workflow = live_client.workflows.get(workflow_id)

    assert workflow.id == workflow_id
    assert workflow.name


@pytest.mark.destructive
def test_live_publish_workflow_round_trip(
    live_client: AlteryxClient,
    mutation_settings: LiveMutationSettings,
    published_workflow,
) -> None:
    """Publish a workflow package and verify the resource can be read back.

    Args:
        live_client: Initialized live client.
        mutation_settings: Destructive test configuration.
        published_workflow: Published workflow fixture.
    """

    fetched_workflow = live_client.workflows.get(published_workflow.id)

    assert fetched_workflow.id == published_workflow.id
    assert fetched_workflow.name == published_workflow.name
    assert fetched_workflow.owner_id == mutation_settings.owner_id


@pytest.mark.destructive
def test_live_run_workflow_and_wait(live_client: AlteryxClient, published_workflow, completed_job) -> None:
    """Run the published workflow to completion and verify the terminal job state.

    Args:
        live_client: Initialized live client.
        published_workflow: Published workflow fixture.
        completed_job: Completed job fixture.
    """

    refreshed_job = live_client.jobs.get(completed_job.id)

    assert completed_job.workflow_id == published_workflow.id
    assert completed_job.status == JobStatus.COMPLETED
    assert refreshed_job.id == completed_job.id
    assert refreshed_job.status == JobStatus.COMPLETED
    assert isinstance(refreshed_job.messages, list)


@pytest.mark.destructive
def test_live_download_job_output(live_client: AlteryxClient, completed_job) -> None:
    """Download a job output artifact when the workflow emits one.

    Args:
        live_client: Initialized live client.
        completed_job: Completed job fixture.
    """

    if not completed_job.outputs:
        pytest.skip("Published live test workflow completed without downloadable outputs")

    first_output = completed_job.outputs[0]
    output_content = live_client.jobs.get_output(completed_job.id, first_output.id)

    assert first_output.id
    assert isinstance(output_content, bytes)
    assert len(output_content) > 0


@pytest.mark.destructive
def test_live_delete_workflow_round_trip(
    live_client: AlteryxClient,
    mutation_settings: LiveMutationSettings,
    test_package_path: Path,
    unique_workflow_name: str,
) -> None:
    """Delete a published workflow and verify it no longer appears in filtered listings.

    Args:
        live_client: Initialized live client.
        mutation_settings: Destructive test configuration.
        test_package_path: Packaged workflow path.
        unique_workflow_name: Unique workflow name for this test.
    """

    workflow = None
    deleted = False

    try:
        workflow = live_client.workflows.publish(
            file_path=str(test_package_path),
            name=unique_workflow_name,
            owner_id=mutation_settings.owner_id,
            comments="Live integration test delete",
        )

        matching_before_delete = live_client.workflows.list(name=unique_workflow_name)
        assert any(candidate.id == workflow.id for candidate in matching_before_delete)

        live_client.workflows.delete(workflow.id)
        deleted = True

        matching_after_delete = live_client.workflows.list(name=unique_workflow_name)
        assert all(candidate.id != workflow.id for candidate in matching_after_delete)
    finally:
        if workflow is not None and not deleted:
            try:
                live_client.workflows.delete(workflow.id)
            except WorkflowNotFoundError:
                pass
