# alteryx-server-py

`alteryx-server-py` is a modern Python client for the Alteryx Server API with
typed models, OAuth2 authentication, and both synchronous and asynchronous
clients.

It is designed for automation-heavy workflows such as CI/CD deployments,
scheduled workflow administration, and server management tasks.

## Features

- Sync and async clients backed by `httpx`
- OAuth2 client credentials authentication
- Typed Pydantic models for V3 API resources
- Workflow publishing, versioning, execution, and polling helpers
- Schedule, user, group, collection, credential, and server resource access
- `uv`-friendly local development and packaging workflow

## Install

This repository is currently intended to be used from source.

For local development:

```bash
uv sync --dev
```

For an editable install inside another environment:

```bash
uv pip install -e .
```

## Configuration

Copy `.env.example` to `.env` and fill in your server details:

```bash
cp .env.example .env
```

Environment variables:

- `ALTERYX_BASE_URL`: Base URL of your server, for example `https://server.example.com/webapi/`
- `ALTERYX_CLIENT_ID`: OAuth2 client ID
- `ALTERYX_CLIENT_SECRET`: OAuth2 client secret
- `ALTERYX_VERIFY_SSL`: Optional SSL verification flag, defaults to `true`
- `ALTERYX_TIMEOUT`: Optional request timeout in seconds, defaults to `30`
- `ALTERYX_MAX_RETRIES`: Optional retry count, defaults to `3`
- `ALTERYX_LOG_LEVEL`: Optional log level, defaults to `INFO`

Official documentation:

- Current Alteryx Server docs: `https://help.alteryx.com/current/en/server/`
- Server API overview: `https://help.alteryx.com/current/en/server/api-overview.html`
- Your server Swagger UI: `https://<server>/webapi/swagger`

## Quick Start

### Synchronous client

```python
from alteryx_server_py import AlteryxClient

client = AlteryxClient.from_env()

workflows = client.workflows.list(page_size=10)
for workflow in workflows:
   print(workflow.id, workflow.name)
```

### Asynchronous client

```python
import asyncio

from alteryx_server_py import AsyncAlteryxClient


async def main() -> None:
   async with AsyncAlteryxClient.from_env() as client:
      jobs = await client.jobs.list(page_size=5)
      for job in jobs:
         print(job.id, job.status)


asyncio.run(main())
```

## Resource Overview

The sync and async clients expose the same resource layout:

- `client.workflows`: list, get, publish, update, delete, download, questions, versions
- `client.jobs`: queue jobs, poll until completion, inspect outputs and messages
- `client.schedules`: create, update, enable, disable, and delete schedules
- `client.users`: create, update, delete, and inspect user assets
- `client.user_groups`: create groups and manage membership
- `client.collections`: manage collections, workflows, and collection permissions
- `client.credentials`: manage shared credentials
- `client.server`: retrieve server info and admin settings

## Workflow Examples

### Publish or update a workflow

```python
from alteryx_server_py import AlteryxClient

client = AlteryxClient.from_env()

existing = client.workflows.list(name="Daily Finance ETL")
if existing:
   workflow = client.workflows.update(
      workflow_id=existing[0].id,
      file_path="dist/DailyFinanceETL.yxzp",
      comments="Deploy latest build",
   )
else:
   workflow = client.workflows.publish(
      file_path="dist/DailyFinanceETL.yxzp",
      name="Daily Finance ETL",
      owner_id="owner-id-from-server",
      comments="Initial deployment",
   )

print(workflow.id)
```

### Run a workflow and wait for completion

```python
from alteryx_server_py import AlteryxClient

client = AlteryxClient.from_env()

job = client.jobs.run_and_wait(
   workflow_id="workflow-id",
   questions={"Region": "EMEA", "AsOfDate": "2026-03-18"},
   timeout=1800,
   poll_interval=10,
)

print(job.status)
for output in job.outputs:
   print(output.id, output.name)
```

## Collections, Credentials, and Server Examples

### Create a collection and assign permissions

```python
from alteryx_server_py import AlteryxClient
from alteryx_server_py.models import CollectionPermission

client = AlteryxClient.from_env()

collection = client.collections.create("Finance Automation")
client.collections.add_workflow(collection.id, "workflow-id")
client.collections.set_permissions(
   collection_id=collection.id,
   user_id="user-id",
   permissions=CollectionPermission(
      is_admin=True,
      can_add_assets=True,
      can_update_assets=True,
      can_remove_assets=False,
      can_add_users=True,
      can_remove_users=False,
   ),
)
```

### Create or rotate a shared credential

```python
from alteryx_server_py import AlteryxClient

client = AlteryxClient.from_env()

credential = client.credentials.create(
   username=r"CONTOSO\svc-alteryx",
   password="super-secret-password",
)

rotated = client.credentials.update(
   credential_id=credential.id,
   new_password="new-super-secret-password",
)

print(rotated.id)
```

### Inspect server metadata

```python
from alteryx_server_py import AlteryxClient

client = AlteryxClient.from_env()

server_info = client.server.get_info()
server_settings = client.server.get_settings()

print(server_info.model_dump())
print(server_settings.model_dump())
```

## CI/CD Example Scripts

The repository includes example automation scripts under `examples/`:

- `examples/deploy_workflows.py`: publish a new workflow or update an existing deployment
- `examples/promote_workflow.py`: upload a new version for an existing workflow
- `examples/run_workflow_tests.py`: execute a workflow and fail fast on unsuccessful jobs
- `examples/admin_resources.py`: inspect server info, collections, and credentials

Example usage:

```bash
uv run python examples/deploy_workflows.py \
  --package dist/DailyFinanceETL.yxzp \
  --name "Daily Finance ETL" \
  --owner-id <owner-id>
```

```bash
uv run python examples/promote_workflow.py \
  --workflow-id <workflow-id> \
  --package dist/DailyFinanceETL.yxzp \
  --comments "Promote build 2026.03.18"
```

```bash
uv run python examples/run_workflow_tests.py \
  --workflow-id <workflow-id> \
  --question Region=EMEA \
  --question AsOfDate=2026-03-18
```

## Development

Run the test suite:

```bash
uv run pytest
```

Run only the live smoke suite against a real server:

```bash
uv run pytest tests/integration -m "live and not destructive"
```

Run the full live integration suite against a sandbox server:

```bash
uv run pytest tests/integration -m live
```

Live integration test environment variables:

- `ALTERYX_BASE_URL`, `ALTERYX_CLIENT_ID`, `ALTERYX_CLIENT_SECRET`: required for all live tests
- `ALTERYX_TEST_OWNER_ID`: required for publish, run, and delete tests
- `ALTERYX_TEST_WORKFLOW_ID`: optional workflow ID for smoke read verification
- `ALTERYX_TEST_JOB_TIMEOUT`, `ALTERYX_TEST_POLL_INTERVAL`: optional run-and-wait tuning

Run linting:

```bash
uv run ruff check src tests examples
```

## Migration Notes

This repository has moved from the legacy `alteryx_gallery_api` package surface to
`alteryx_server_py`.

Key changes:

- Package import changed from `alteryx_gallery_api` to `alteryx_server_py`
- Auth variables changed from `BASE_URL`, `API_KEY`, and `API_SECRET` to `ALTERYX_BASE_URL`, `ALTERYX_CLIENT_ID`, and `ALTERYX_CLIENT_SECRET`
- Resource access is now grouped under the client, for example `client.workflows.list()` instead of `get_subscription_workflows()`
- Job execution uses `client.jobs.run()` or `client.jobs.run_and_wait()` instead of legacy queue helpers
- Sync and async clients now share the same model and resource structure

## Status

Phase 1 through Phase 4 are implemented. Phase 5 is focused on documentation,
release automation, and packaging polish.
