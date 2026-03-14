# Product Requirements Document (PRD)
# Alteryx Server API Python Wrapper

**Version:** 1.0  
**Date:** January 9, 2026  
**Status:** Draft  
**Package Name:** `alteryx-server-py`  
**Target Version:** 0.2.0  

---

## 1. Executive Summary

This PRD outlines the requirements for implementing a comprehensive Python wrapper for the Alteryx Server (Gallery) V3 API. The library will enable automated CI/CD pipelines for workflow deployment, execution, and server management, with both synchronous and asynchronous support. The package will be published to public PyPI as `alteryx-server-py`.

### 1.1 Goals

- Provide complete coverage of Alteryx Server V3 API endpoints
- Enable seamless CI/CD integration for workflow lifecycle management
- Support both sync and async operations for flexibility
- Maintain type safety with Pydantic models
- Ensure production-ready quality with comprehensive testing
- Leverage modern UV tooling for development and distribution

### 1.2 Non-Goals (Out of Scope for v1.0)

- Command-line interface (CLI) - deferred to future release
- V1 API support (deprecated endpoints)
- GUI or web interface
- Alteryx Designer API integration

---

## 2. Target Users

| User Type | Use Case |
|-----------|----------|
| **DevOps Engineers** | Automate workflow deployments in CI/CD pipelines |
| **Data Engineers** | Programmatically manage workflows and schedules |
| **Platform Admins** | Automate user provisioning and server configuration |
| **Analytics Teams** | Integrate Alteryx executions into larger data pipelines |

---

## 3. Technical Requirements

### 3.1 Environment

| Requirement | Specification |
|-------------|---------------|
| Python Version | 3.10, 3.11, 3.12 |
| Alteryx Server Version | 2024.1+ |
| API Version | V3 (primary), V1 (fallback where V3 unavailable) |
| Authentication | OAuth2 Client Credentials (Client ID + Client Secret) |
| Package Manager | UV (>=0.5.0) |
| Build Backend | `uv_build` (>=0.9.22,<0.10.0) |

### 3.2 Dependencies

**Runtime Dependencies:**

| Package | Purpose | Version |
|---------|---------|---------|
| `httpx` | Async and sync HTTP client | >=0.28.1 |
| `pydantic` | Data validation and serialization | >=2.11.0 |
| `python-dotenv` | Environment variable loading | >=1.1.0 |

**Development Dependencies:**

| Package | Purpose | Version |
|---------|---------|---------|
| `pytest` | Testing framework | >=8.3.3 |
| `pytest-cov` | Coverage reporting | >=6.0.0 |
| `pytest-asyncio` | Async test support | >=0.24.0 |
| `respx` | httpx mocking library | >=0.22.0 |
| `ruff` | Linting and formatting | >=0.8.0 |

**Note:** Migration from `requests`/`requests-oauthlib` to `httpx` for unified sync/async support.

### 3.3 Build System

```toml
[build-system]
requires = ["uv_build>=0.9.22,<0.10.0"]
build-backend = "uv_build"
```

### 3.4 UV Commands

| Command | Purpose |
|---------|---------|
| `uv sync` | Install dependencies and sync lock file |
| `uv sync --all-extras --dev` | Install with all optional dependencies |
| `uv run pytest` | Run tests |
| `uv run pytest --cov` | Run tests with coverage |
| `uv run ruff check .` | Lint code |
| `uv run ruff format .` | Format code |
| `uv build` | Build package (wheel + sdist) |
| `uv version --bump minor` | Bump version (0.1.0 → 0.2.0) |
| `uv publish` | Publish to PyPI |
| `uv publish --index-url https://test.pypi.org/simple/` | Publish to TestPyPI |

### 3.5 Package Structure

```
src/alteryx_server_py/
├── __init__.py              # Public API exports
├── client.py                # Main AlteryxClient (sync)
├── async_client.py          # AsyncAlteryxClient (async)
├── _base_client.py          # Shared client logic
├── auth.py                  # OAuth2 authentication handler
├── config.py                # Configuration management
├── exceptions.py            # Custom exception hierarchy
├── _http.py                 # HTTP transport layer (httpx wrapper)
├── models/
│   ├── __init__.py          # Model exports
│   ├── base.py              # BaseApiModel
│   ├── common.py            # Shared types and enums
│   ├── auth.py              # Token models
│   ├── workflows.py         # Workflow models
│   ├── jobs.py              # Job models
│   ├── schedules.py         # Schedule models
│   ├── users.py             # User/Group models
│   ├── collections.py       # Collection models
│   ├── credentials.py       # DCM credential models
│   ├── server.py            # Server info models
│   └── insights.py          # Insights models (if applicable)
├── resources/
│   ├── __init__.py          # Resource exports
│   ├── _base.py             # Base resource class
│   ├── workflows.py         # WorkflowResource
│   ├── jobs.py              # JobResource
│   ├── schedules.py         # ScheduleResource
│   ├── users.py             # UserResource
│   ├── user_groups.py       # UserGroupResource
│   ├── collections.py       # CollectionResource
│   ├── credentials.py       # CredentialResource (DCM)
│   └── server.py            # ServerResource (admin operations)
└── utils/
    ├── __init__.py
    ├── pagination.py        # Pagination helpers
    ├── retry.py             # Retry logic with backoff
    └── file_utils.py        # File handling for uploads
```

---

## 4. API Coverage

### 4.1 Workflows API

| Endpoint | Method | Priority | Description |
|----------|--------|----------|-------------|
| `GET /v3/workflows` | `list()` | P0 | List all accessible workflows |
| `GET /v3/workflows/{id}` | `get()` | P0 | Get workflow details |
| `POST /v3/workflows` | `publish()` | P0 | Upload/publish new workflow |
| `PUT /v3/workflows/{id}` | `update()` | P0 | Update existing workflow |
| `DELETE /v3/workflows/{id}` | `delete()` | P0 | Delete workflow |
| `GET /v3/workflows/{id}/package` | `download()` | P1 | Download workflow package |
| `GET /v3/workflows/{id}/questions` | `get_questions()` | P1 | Get analytic app questions |
| `POST /v3/workflows/{id}/versions` | `publish_version()` | P0 | Publish new version |
| `GET /v3/workflows/{id}/versions` | `list_versions()` | P1 | List workflow versions |

**CI/CD Use Cases:**
- Deploy workflow from source control to server
- Promote workflow between environments
- Version management and rollback

### 4.2 Jobs API

| Endpoint | Method | Priority | Description |
|----------|--------|----------|-------------|
| `POST /v3/workflows/{id}/jobs` | `run()` | P0 | Queue/execute workflow job |
| `GET /v3/jobs/{id}` | `get()` | P0 | Get job status/details |
| `GET /v3/jobs` | `list()` | P1 | List jobs with filters |
| `GET /v3/jobs/{id}/output/{outputId}` | `get_output()` | P0 | Download job output |
| `GET /v3/jobs/{id}/messages` | `get_messages()` | P1 | Get job execution messages |
| `DELETE /v3/jobs/{id}` | `cancel()` | P2 | Cancel running job |

**CI/CD Use Cases:**
- Execute workflow and wait for completion
- Validate job outputs in tests
- Monitor job execution in pipelines

### 4.3 Schedules API

| Endpoint | Method | Priority | Description |
|----------|--------|----------|-------------|
| `GET /v3/schedules` | `list()` | P1 | List all schedules |
| `GET /v3/schedules/{id}` | `get()` | P1 | Get schedule details |
| `POST /v3/schedules` | `create()` | P1 | Create new schedule |
| `PUT /v3/schedules/{id}` | `update()` | P1 | Update schedule |
| `DELETE /v3/schedules/{id}` | `delete()` | P1 | Delete schedule |
| `POST /v3/schedules/{id}/disable` | `disable()` | P2 | Disable schedule |
| `POST /v3/schedules/{id}/enable` | `enable()` | P2 | Enable schedule |

**CI/CD Use Cases:**
- Create/update schedules as part of deployment
- Disable schedules during maintenance windows

### 4.4 Users API

| Endpoint | Method | Priority | Description |
|----------|--------|----------|-------------|
| `GET /v3/users` | `list()` | P1 | List all users |
| `GET /v3/users/{id}` | `get()` | P1 | Get user details |
| `POST /v3/users` | `create()` | P2 | Create new user |
| `PUT /v3/users/{id}` | `update()` | P2 | Update user |
| `DELETE /v3/users/{id}` | `delete()` | P2 | Deactivate user |
| `GET /v3/users/{id}/assets` | `get_assets()` | P2 | Get user's assets |

### 4.5 User Groups API

| Endpoint | Method | Priority | Description |
|----------|--------|----------|-------------|
| `GET /v3/usergroups` | `list()` | P2 | List all user groups |
| `GET /v3/usergroups/{id}` | `get()` | P2 | Get group details |
| `POST /v3/usergroups` | `create()` | P2 | Create new group |
| `PUT /v3/usergroups/{id}` | `update()` | P2 | Update group |
| `DELETE /v3/usergroups/{id}` | `delete()` | P2 | Delete group |
| `POST /v3/usergroups/{id}/users` | `add_users()` | P2 | Add users to group |
| `DELETE /v3/usergroups/{id}/users/{userId}` | `remove_user()` | P2 | Remove user from group |

### 4.6 Collections API

| Endpoint | Method | Priority | Description |
|----------|--------|----------|-------------|
| `GET /v3/collections` | `list()` | P2 | List all collections |
| `GET /v3/collections/{id}` | `get()` | P2 | Get collection details |
| `POST /v3/collections` | `create()` | P2 | Create new collection |
| `PUT /v3/collections/{id}` | `update()` | P2 | Update collection |
| `DELETE /v3/collections/{id}` | `delete()` | P2 | Delete collection |
| `POST /v3/collections/{id}/workflows` | `add_workflow()` | P2 | Add workflow to collection |
| `DELETE /v3/collections/{id}/workflows/{wfId}` | `remove_workflow()` | P2 | Remove workflow |
| `PUT /v3/collections/{id}/permissions` | `set_permissions()` | P2 | Set collection permissions |

### 4.7 Server/Admin API

| Endpoint | Method | Priority | Description |
|----------|--------|----------|-------------|
| `GET /v3/serverinfo` | `get_info()` | P1 | Get server information |
| `GET /v3/admin/settings` | `get_settings()` | P2 | Get server settings (admin) |

### 4.8 Credentials API (DCM)

| Endpoint | Method | Priority | Description |
|----------|--------|----------|-------------|
| `GET /v3/credentials` | `list()` | P2 | List credentials |
| `GET /v3/credentials/{id}` | `get()` | P2 | Get credential details |
| `POST /v3/credentials` | `create()` | P2 | Create credential |
| `PUT /v3/credentials/{id}` | `update()` | P2 | Update credential |
| `DELETE /v3/credentials/{id}` | `delete()` | P2 | Delete credential |

---

## 5. Client Interface Design

### 5.1 Synchronous Client

```python
from alteryx_server_py import AlteryxClient

# Initialize with credentials (from env or explicit)
client = AlteryxClient(
    base_url="https://your-server.com/webapi/",
    client_id="your-client-id",
    client_secret="your-client-secret",
    verify_ssl=True,
    timeout=30.0,
)

# Workflows
workflows = client.workflows.list()
workflow = client.workflows.get("workflow-id")
new_wf = client.workflows.publish("path/to/workflow.yxzp", name="My Workflow")
client.workflows.update("workflow-id", "path/to/updated.yxzp")
client.workflows.delete("workflow-id")

# Jobs
job = client.jobs.run("workflow-id", questions={"param1": "value1"})
status = client.jobs.get(job.id)
output = client.jobs.get_output(job.id, output_id="output-1")

# Wait for job completion (with polling)
completed_job = client.jobs.run_and_wait(
    "workflow-id",
    timeout=300,
    poll_interval=5
)

# Schedules
schedules = client.schedules.list()
schedule = client.schedules.create(
    workflow_id="wf-id",
    name="Daily Run",
    frequency="daily",
    start_time="2024-01-01T08:00:00Z"
)

# Users and Groups
users = client.users.list()
groups = client.user_groups.list()

# Server Info
info = client.server.get_info()
```

### 5.2 Asynchronous Client

```python
from alteryx_server_py import AsyncAlteryxClient
import asyncio

async def main():
    async with AsyncAlteryxClient(
        base_url="https://your-server.com/webapi/",
        client_id="your-client-id",
        client_secret="your-client-secret",
    ) as client:
        # All methods are async
        workflows = await client.workflows.list()
        
        # Run multiple workflows concurrently
        jobs = await asyncio.gather(
            client.jobs.run("workflow-1"),
            client.jobs.run("workflow-2"),
            client.jobs.run("workflow-3"),
        )
        
        # Wait for all to complete
        results = await asyncio.gather(
            *[client.jobs.wait_for_completion(job.id) for job in jobs]
        )

asyncio.run(main())
```

### 5.3 Configuration Options

```python
from alteryx_server_py import AlteryxClient, ClientConfig

# Using config object
config = ClientConfig(
    base_url="https://your-server.com/webapi/",
    client_id="your-client-id",
    client_secret="your-client-secret",
    verify_ssl=True,
    timeout=30.0,
    max_retries=3,
    retry_backoff_factor=0.5,
    log_level="INFO",
)

client = AlteryxClient(config=config)

# Or auto-load from environment variables
# Expects: ALTERYX_BASE_URL, ALTERYX_CLIENT_ID, ALTERYX_CLIENT_SECRET
client = AlteryxClient.from_env()

# Or from .env file
client = AlteryxClient.from_dotenv(".env")
```

---

## 6. Pydantic Models

### 6.1 Core Models

```python
# models/workflows.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class WorkflowType(str, Enum):
    STANDARD = "Standard"
    ANALYTIC_APP = "AnalyticApp"
    MACRO = "Macro"

class ExecutionMode(str, Enum):
    SAFE = "Safe"
    SEMI_SAFE = "SemiSafe"
    UNRESTRICTED = "Unrestricted"

class Workflow(BaseModel):
    id: str = Field(..., alias="id")
    name: str
    version_id: Optional[str] = Field(None, alias="versionId")
    owner_id: str = Field(..., alias="ownerId")
    owner_email: Optional[str] = Field(None, alias="ownerEmail")
    workflow_type: WorkflowType = Field(..., alias="workflowType")
    execution_mode: ExecutionMode = Field(..., alias="executionMode")
    is_public: bool = Field(False, alias="isPublic")
    is_ready_for_migration: bool = Field(False, alias="isReadyForMigration")
    run_count: int = Field(0, alias="runCount")
    created_date: datetime = Field(..., alias="dateCreated")
    updated_date: Optional[datetime] = Field(None, alias="lastUpdated")
    description: Optional[str] = None
    collection_ids: List[str] = Field(default_factory=list, alias="collectionIds")
    
    class Config:
        populate_by_name = True

class WorkflowUploadRequest(BaseModel):
    name: str
    owner_id: str = Field(..., alias="ownerId")
    is_public: bool = Field(False, alias="isPublic")
    execution_mode: ExecutionMode = Field(ExecutionMode.SAFE, alias="executionMode")
    worker_tag: Optional[str] = Field(None, alias="workerTag")
    comments: Optional[str] = None
    
    class Config:
        populate_by_name = True
```

```python
# models/jobs.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    QUEUED = "Queued"
    RUNNING = "Running"
    COMPLETED = "Completed"
    ERROR = "Error"
    CANCELLED = "Cancelled"

class JobOutput(BaseModel):
    id: str
    name: str
    format: str
    size: Optional[int] = None

class Job(BaseModel):
    id: str
    workflow_id: str = Field(..., alias="workflowId")
    status: JobStatus
    disposition: Optional[str] = None
    outputs: List[JobOutput] = Field(default_factory=list)
    messages: List[str] = Field(default_factory=list)
    priority: str = Field("Default")
    worker_tag: Optional[str] = Field(None, alias="workerTag")
    run_as: Optional[str] = Field(None, alias="runAs")
    created_date: datetime = Field(..., alias="createDate")
    queued_date: Optional[datetime] = Field(None, alias="queuedDate")
    start_date: Optional[datetime] = Field(None, alias="startDate")
    end_date: Optional[datetime] = Field(None, alias="endDate")
    
    class Config:
        populate_by_name = True

class JobRunRequest(BaseModel):
    questions: Optional[Dict[str, Any]] = None
    priority: str = Field("Default")
    worker_tag: Optional[str] = Field(None, alias="workerTag")
    
    class Config:
        populate_by_name = True
```

### 6.2 Response Models

```python
# models/common.py
from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List, Optional, Dict, Any

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""
    items: List[T] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = Field(20, alias="pageSize")
    has_more: bool = Field(False, alias="hasMore")
    
    class Config:
        populate_by_name = True

class ApiError(BaseModel):
    """API error response model."""
    message: str
    error_code: Optional[str] = Field(None, alias="errorCode")
    details: Optional[Dict[str, Any]] = None
```

---

## 7. Exception Hierarchy

```python
# exceptions.py

class AlteryxError(Exception):
    """Base exception for all Alteryx API errors."""
    pass

class ConfigurationError(AlteryxError):
    """Raised for configuration/setup issues."""
    pass

class AuthenticationError(AlteryxError):
    """Raised when authentication fails (401)."""
    pass

class AuthorizationError(AlteryxError):
    """Raised when access is denied (403)."""
    pass

class NotFoundError(AlteryxError):
    """Raised when resource is not found (404)."""
    pass

class WorkflowNotFoundError(NotFoundError):
    """Raised when a workflow is not found."""
    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        super().__init__(f"Workflow '{workflow_id}' not found")

class JobNotFoundError(NotFoundError):
    """Raised when a job is not found."""
    def __init__(self, job_id: str):
        self.job_id = job_id
        super().__init__(f"Job '{job_id}' not found")

class ValidationError(AlteryxError):
    """Raised when request validation fails (400)."""
    pass

class RateLimitError(AlteryxError):
    """Raised when rate limit is exceeded (429)."""
    def __init__(self, retry_after: Optional[int] = None):
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded. Retry after {retry_after}s")

class ServerError(AlteryxError):
    """Raised for server-side errors (5xx)."""
    pass

class JobExecutionError(AlteryxError):
    """Raised when job execution fails."""
    def __init__(self, job_id: str, status: str, messages: List[str] = None):
        self.job_id = job_id
        self.status = status
        self.messages = messages or []
        super().__init__(f"Job '{job_id}' failed with status '{status}'")

class TimeoutError(AlteryxError):
    """Raised when an operation times out."""
    pass
```

---

## 8. CI/CD Integration Patterns

### 8.1 GitHub Actions Example

```yaml
# .github/workflows/deploy-workflows.yml
name: Deploy Alteryx Workflows

on:
  push:
    branches: [main]
    paths:
      - 'workflows/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install uv
        uses: astral-sh/setup-uv@v5
        with:
          version: "latest"
      
      - name: Set up Python
        run: uv python install 3.12
      
      - name: Install dependencies
        run: uv pip install alteryx-server-py
      
      - name: Deploy Workflows
        env:
          ALTERYX_BASE_URL: ${{ secrets.ALTERYX_BASE_URL }}
          ALTERYX_CLIENT_ID: ${{ secrets.ALTERYX_CLIENT_ID }}
          ALTERYX_CLIENT_SECRET: ${{ secrets.ALTERYX_CLIENT_SECRET }}
        run: uv run python scripts/deploy_workflows.py
```

```python
# scripts/deploy_workflows.py
from pathlib import Path
from alteryx_server_py import AlteryxClient

def deploy_workflows():
    client = AlteryxClient.from_env()
    
    workflows_dir = Path("workflows")
    for workflow_file in workflows_dir.glob("*.yxzp"):
        print(f"Deploying {workflow_file.name}...")
        
        # Check if workflow exists
        existing = client.workflows.list(name=workflow_file.stem)
        
        if existing:
            # Update existing workflow
            client.workflows.update(
                existing[0].id,
                str(workflow_file),
                comments=f"Updated via CI/CD"
            )
            print(f"  Updated workflow: {existing[0].id}")
        else:
            # Publish new workflow
            new_wf = client.workflows.publish(
                str(workflow_file),
                name=workflow_file.stem
            )
            print(f"  Published new workflow: {new_wf.id}")

if __name__ == "__main__":
    deploy_workflows()
```

### 8.2 Test Execution Pattern

```python
# tests/integration/test_workflow_execution.py
import pytest
from alteryx_server_py import AlteryxClient
from alteryx_server_py.exceptions import JobExecutionError

@pytest.fixture
def client():
    return AlteryxClient.from_env()

def test_workflow_produces_expected_output(client):
    """Test that workflow executes and produces valid output."""
    # Run workflow
    job = client.jobs.run_and_wait(
        workflow_id="test-workflow-id",
        questions={"input_file": "test_data.csv"},
        timeout=300,
    )
    
    # Verify completion
    assert job.status == "Completed"
    assert len(job.outputs) > 0
    
    # Download and validate output
    output_data = client.jobs.get_output(job.id, job.outputs[0].id)
    assert len(output_data) > 0
```

### 8.3 Environment Promotion Pattern

```python
# scripts/promote_workflow.py
import os
from alteryx_server_py import AlteryxClient

def promote_workflow(workflow_id: str, source_env: str, target_env: str):
    """Promote a workflow from one environment to another."""
    
    # Connect to source environment
    source_client = AlteryxClient(
        base_url=f"https://{source_env}.company.com/webapi/",
        client_id=os.getenv(f"{source_env.upper()}_CLIENT_ID"),
        client_secret=os.getenv(f"{source_env.upper()}_CLIENT_SECRET"),
    )
    
    # Connect to target environment
    target_client = AlteryxClient(
        base_url=f"https://{target_env}.company.com/webapi/",
        client_id=os.getenv(f"{target_env.upper()}_CLIENT_ID"),
        client_secret=os.getenv(f"{target_env.upper()}_CLIENT_SECRET"),
    )
    
    # Download workflow from source
    workflow = source_client.workflows.get(workflow_id)
    package_bytes = source_client.workflows.download(workflow_id)
    
    # Save temporarily
    temp_path = f"/tmp/{workflow.name}.yxzp"
    with open(temp_path, "wb") as f:
        f.write(package_bytes)
    
    # Check if exists in target
    existing = target_client.workflows.list(name=workflow.name)
    
    if existing:
        target_client.workflows.update(
            existing[0].id,
            temp_path,
            comments=f"Promoted from {source_env}"
        )
        print(f"Updated {workflow.name} in {target_env}")
    else:
        target_client.workflows.publish(
            temp_path,
            name=workflow.name,
            comments=f"Promoted from {source_env}"
        )
        print(f"Published {workflow.name} to {target_env}")
```

---

## 9. Implementation Plan

### Phase 1: Core Infrastructure (Week 1-2)

| Task | Priority | Description |
|------|----------|-------------|
| 1.1 | P0 | Rename package from `alteryx_gallery_api` to `alteryx_server_py` |
| 1.2 | P0 | Update `pyproject.toml` with UV build backend and new package name |
| 1.3 | P0 | Migrate from `requests` to `httpx` for unified sync/async |
| 1.4 | P0 | Implement `_base_client.py` with shared logic |
| 1.5 | P0 | Implement OAuth2 authentication with token refresh in `auth.py` |
| 1.6 | P0 | Create `AlteryxClient` (sync) class with resource pattern |
| 1.7 | P0 | Create `AsyncAlteryxClient` class |
| 1.8 | P0 | Implement retry logic with exponential backoff in `utils/retry.py` |
| 1.9 | P0 | Update exception hierarchy |
| 1.10 | P0 | Implement configuration management (`config.py`) |
| 1.11 | P0 | Update environment variable names (ALTERYX_*) |

**Deliverables:**
- Working sync and async clients with authentication
- Retry and error handling
- Unit tests for core infrastructure
- Updated package structure

### Phase 2: Workflow and Job Resources (Week 3-4)

| Task | Priority | Description |
|------|----------|-------------|
| 2.1 | P0 | Implement `WorkflowResource` with full CRUD |
| 2.2 | P0 | Implement `JobResource` with run/status/output |
| 2.3 | P0 | Add `run_and_wait()` helper with polling |
| 2.4 | P0 | Create comprehensive Pydantic models for workflows |
| 2.5 | P0 | Create comprehensive Pydantic models for jobs |
| 2.6 | P0 | Implement file upload for workflow publishing |
| 2.7 | P1 | Add pagination support in `utils/pagination.py` |
| 2.8 | P0 | Unit tests with mocked responses (using `respx`) |
| 2.9 | P0 | Integration tests against live server |

**Deliverables:**
- Complete workflow management capabilities
- Job execution and monitoring
- 80%+ test coverage for workflow/job modules

### Phase 3: Schedule and User Management (Week 5-6)

| Task | Priority | Description |
|------|----------|-------------|
| 3.1 | P1 | Implement `ScheduleResource` |
| 3.2 | P1 | Implement `UserResource` |
| 3.3 | P2 | Implement `UserGroupResource` |
| 3.4 | P2 | Create Pydantic models for schedules |
| 3.5 | P2 | Create Pydantic models for users/groups |
| 3.6 | P1 | Unit and integration tests |

**Deliverables:**
- Schedule CRUD operations
- User and group management
- 80%+ test coverage

### Phase 4: Collections, Credentials and Server (Week 7)

| Task | Priority | Description |
|------|----------|-------------|
| 4.1 | P2 | Implement `CollectionResource` |
| 4.2 | P2 | Implement `CredentialResource` (DCM) |
| 4.3 | P1 | Implement `ServerResource` |
| 4.4 | P2 | Create Pydantic models for collections |
| 4.5 | P2 | Create Pydantic models for credentials |
| 4.6 | P2 | Create Pydantic models for server info |
| 4.7 | P2 | Unit and integration tests |

**Deliverables:**
- Collection management
- DCM credential management
- Server info/settings access

### Phase 5: Documentation and Release (Week 8)

| Task | Priority | Description |
|------|----------|-------------|
| 5.1 | P0 | Comprehensive README with examples |
| 5.2 | P0 | Docstrings for all public methods |
| 5.3 | P0 | Update `.env.example` with new variable names |
| 5.4 | P0 | Create CI/CD example scripts |
| 5.5 | P0 | Update GitHub Actions workflow for UV |
| 5.6 | P0 | Bump version to 0.2.0 using `uv version --bump minor` |
| 5.7 | P0 | Build package using `uv build` |
| 5.8 | P0 | Test publish to TestPyPI |
| 5.9 | P0 | Publish to PyPI using `uv publish` |
| 5.10 | P1 | Create CHANGELOG.md |

**Deliverables:**
- Production-ready documentation
- Published to PyPI as `alteryx-server-py`
- CI/CD templates
- Version 0.2.0 release

---

## 10. Testing Strategy

### 10.1 Test Levels

| Level | Coverage Target | Description |
|-------|-----------------|-------------|
| Unit Tests | 85% | Mock HTTP responses using `respx`, test business logic |
| Integration Tests | Key flows | Test against real Alteryx Server (CI environment) |
| E2E Tests | Critical paths | Full workflow: deploy, run, validate |

### 10.2 Test Infrastructure

```python
# tests/conftest.py
import pytest
from unittest.mock import MagicMock
import httpx
import respx

@pytest.fixture
def mock_client():
    """Create a client with mocked HTTP transport."""
    from alteryx_server_py import AlteryxClient
    client = AlteryxClient(
        base_url="https://test.example.com/webapi/",
        client_id="test-id",
        client_secret="test-secret",
        authenticate_on_init=False,
    )
    return client

@pytest.fixture
def respx_mock():
    """Provide respx mock for httpx."""
    with respx.mock:
        yield respx

@pytest.fixture
def live_client():
    """Create a client connected to real server (for integration tests)."""
    import os
    if not os.getenv("ALTERYX_BASE_URL"):
        pytest.skip("Live server credentials not configured")
    
    from alteryx_server_py import AlteryxClient
    return AlteryxClient.from_env()
```

### 10.3 Test Matrix

| Component | Unit | Integration | Notes |
|-----------|------|-------------|-------|
| Authentication | Yes | Yes | Token refresh, expiry handling |
| Workflows CRUD | Yes | Yes | Include file upload |
| Job Execution | Yes | Yes | Include wait/poll logic |
| Schedules | Yes | Yes | Cron expression validation |
| Users/Groups | Yes | Yes | Permission testing |
| Error Handling | Yes | No | All exception types |
| Retry Logic | Yes | No | Backoff verification |
| Async Client | Yes | Yes | Parallel operations |

---

## 11. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| API Coverage | 100% of V3 endpoints | Endpoint tracking spreadsheet |
| Test Coverage | >=85% | `pytest-cov` report |
| Documentation | 100% public API | Docstring coverage tool |
| CI/CD Integration | 3+ examples | Working GitHub Actions/GitLab CI examples |
| PyPI Downloads | 100+ in first month | PyPI stats |
| Issues Resolution | <48hr response | GitHub issue tracking |

---

## 12. Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| V3 API incomplete | High | Medium | Fall back to V1 for missing endpoints, document gaps |
| Breaking API changes | Medium | Low | Version pinning, deprecation warnings |
| Auth token issues | High | Medium | Robust token refresh, clear error messages |
| Rate limiting | Medium | Medium | Built-in retry with backoff, user-configurable |
| Large file uploads | Medium | Low | Streaming uploads, chunking if needed |
| Server version differences | Medium | Medium | Feature detection, graceful degradation |
| UV build compatibility | Low | Low | Pin `uv_build` version, test on CI |

---

## 13. Future Considerations (Post v0.2.0)

1. **CLI Tool**: Command-line interface for non-Python CI/CD systems
2. **Webhook Support**: Register and handle server webhooks
3. **Caching Layer**: Optional response caching for read operations
4. **Batch Operations**: Bulk workflow/schedule management
5. **MkDocs Documentation**: Full documentation site
6. **Insights API**: Analytics and reporting endpoints
7. **Server Administration**: Full admin API coverage
8. **Plugin Architecture**: Extensible middleware/hooks
9. **V1.0.0 Release**: Stabilize API and commit to semantic versioning

---

## 14. Appendix

### A. Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ALTERYX_BASE_URL` | Yes | Base URL of Alteryx Server (e.g., `https://server.com/webapi/`) |
| `ALTERYX_CLIENT_ID` | Yes | OAuth2 Client ID |
| `ALTERYX_CLIENT_SECRET` | Yes | OAuth2 Client Secret |
| `ALTERYX_VERIFY_SSL` | No | SSL verification (default: `true`) |
| `ALTERYX_TIMEOUT` | No | Request timeout in seconds (default: `30`) |
| `ALTERYX_MAX_RETRIES` | No | Max retry attempts (default: `3`) |
| `ALTERYX_LOG_LEVEL` | No | Logging level (default: `INFO`) |

### B. API Reference Links

- Alteryx Server API Overview: https://help.alteryx.com/developer-help/server-api-overview
- V3 API Swagger: `{your-server}/webapi/swagger/ui/index`
- OAuth2 Documentation: https://help.alteryx.com/developer-help/server-api-authentication

### C. Glossary

| Term | Definition |
|------|------------|
| **Gallery** | Legacy name for Alteryx Server's web interface |
| **Workflow** | An Alteryx analytics process (`.yxmd` or `.yxzp` file) |
| **Analytic App** | A workflow with user-facing input questions |
| **Job** | A single execution instance of a workflow |
| **Collection** | A grouping of workflows for organization/permissions |
| **DCM** | Data Connection Manager - credential vault in Alteryx |
| **Worker** | A service that executes workflows |
| **Worker Tag** | Label to route workflows to specific workers |
| **UV** | Modern Python package and project manager by Astral |

### D. Migration Checklist

For migrating from v0.1.0 to v0.2.0:

- [ ] Update package import: `from alteryx_gallery_api` → `from alteryx_server_py`
- [ ] Update environment variables: `BASE_URL` → `ALTERYX_BASE_URL`, `API_KEY` → `ALTERYX_CLIENT_ID`, `API_SECRET` → `ALTERYX_CLIENT_SECRET`
- [ ] Update method calls to use resource pattern: `client.get_workflows()` → `client.workflows.list()`
- [ ] Update exception imports if using specific exceptions
- [ ] Test async operations if migrating to async client

---

**Document Revision History**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-09 | OpenCode | Initial draft with UV build system and updated package name |
