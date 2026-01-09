# Alteryx Server API Python Package - Task Management

**Package Name:** alteryx-server-py  
**Target Version:** 0.2.0  
**Status:** In Development  

---

## Completed Tasks (v0.1.0)

- [x] **Task 0: Initial Project Structure Analysis**
    * [x] Task 0.1: Check for `src`, `tests`, and `docs` folders.
    * [x] Task 0.2: Evaluate existing files in `src` for potential authentication module structure.
    * [x] Task 0.3: Evaluate existing files in `tests` for initial testing framework setup.
    * [x] Task 0.4: Evaluate existing files in `docs` for initial documentation setup.
    * [x] Task 0.5: Document findings and plan for integration with later tasks.
- [x] **Task 1: Project Setup and Initial Structure**
    * [x] Task 1.1: Initialize Git repository.
    * [x] Task 1.2: Create project structure (`src/alteryx_gallery_api`).
    * [x] Task 1.3: Set up dependency management (using `pyproject.toml` with `uv`) and install initial dependencies (`requests`, `requests-oauthlib`).
    * [x] Task 1.4: Create a basic module for API authentication (`client.py` includes `AlteryxClient` with init).
- [x] **Task 2: Authentication Module Development (V1)**
    * [x] Task 2.1: Implement API key/secret-based authentication (OAuth 1.0a via `requests-oauthlib`).
- [x] **Task 3: Basic Workflow Management (V1 API)**
    * [x] Task 3.1: Implement functions for listing workflows (`get_subscription_workflows`).
    * [x] Task 3.2: Implement functions for uploading workflows (`publish_workflow`).
    * [x] Task 3.4: Implement functions for deleting workflows (`delete_workflow`).
    * [x] Task 3.5: Implement functions for updating workflows (`update_workflow`).
- [x] **Task 5: Basic Job Management (V1 API)**
    * [x] Task 5.1: Implement functions for listing jobs (covered by `get_job_status`).
    * [x] Task 5.2: Implement functions for retrieving job results (`get_job_output`).
    * [x] Task 5.3: Implement functions for queuing jobs (`queue_job`).

---

## Phase 1: Core Infrastructure (Week 1-2)

**Status:** In Progress (4/11 complete)  
**Priority:** High  
**Goal:** Migrate to modern architecture with httpx, UV build system, and resource-based API design

- [x] **1.1** Rename package from alteryx_gallery_api to alteryx_server_py
    - Move `src/alteryx_gallery_api/` → `src/alteryx_server_py/`
    - Update all imports across codebase
    - Archive old code to separate branch
- [ ] **1.2** Update pyproject.toml with UV build backend and new package name
    - Change `[build-system]` to use `uv_build>=0.9.22,<0.10.0`
    - Update package name to `alteryx-server-py`
    - Update dependencies list
    - Add respx for httpx mocking
- [x] **1.3** Migrate from requests to httpx for unified sync/async
    - Replace `requests` and `requests-oauthlib` with `httpx`
    - Update all HTTP request calls
    - Implement OAuth2 with httpx
- [ ] **1.4** Implement _base_client.py with shared logic
    - Create base class for common client functionality
    - Implement URL building logic
    - Add request/response handling
- [x] **1.5** Implement OAuth2 authentication with token refresh in auth.py
    - Create `auth.py` module
    - Implement token fetching with Client Credentials flow
    - Add automatic token refresh logic
    - Handle token expiry
- [ ] **1.6** Create AlteryxClient (sync) class with resource pattern
    - Refactor `client.py` to use resource-based pattern
    - Add property accessors: `.workflows`, `.jobs`, `.schedules`, etc.
    - Implement `from_env()` and `from_dotenv()` class methods
- [ ] **1.7** Create AsyncAlteryxClient class
    - Create `async_client.py`
    - Implement async versions of all methods
    - Add context manager support (`async with`)
- [x] **1.8** Implement retry logic with exponential backoff in utils/retry.py
    - Create `utils/retry.py`
    - Implement configurable retry decorator
    - Add exponential backoff with jitter
    - Handle rate limiting (429 responses)
- [x] **1.9** Update exception hierarchy
    - Enhance `exceptions.py` with new exception types
    - Add `AuthorizationError`, `ValidationError`, `RateLimitError`, `TimeoutError`
    - Update existing exceptions to match PRD
- [x] **1.10** Implement configuration management (config.py)
    - Create `config.py` with `ClientConfig` class
    - Support configuration from env vars, .env file, and explicit params
    - Add validation for config values
- [ ] **1.11** Update environment variable names (ALTERYX_*)
    - Rename `BASE_URL` → `ALTERYX_BASE_URL`
    - Rename `API_KEY` → `ALTERYX_CLIENT_ID`
    - Rename `API_SECRET` → `ALTERYX_CLIENT_SECRET`
    - Update `.env.example`
    - Update all tests

**Deliverables:**
- Working sync and async clients with OAuth2 authentication
- Retry and error handling with exponential backoff
- Unit tests for core infrastructure (85% coverage)
- Updated package structure and dependencies

---

## Phase 2: Workflow & Job Resources (Week 3-4)

**Status:** Pending  
**Priority:** High  
**Goal:** Complete workflow and job management for CI/CD pipelines

- [ ] **2.1** Implement WorkflowResource with full CRUD
    - Create `resources/workflows.py`
    - Implement: `list()`, `get()`, `publish()`, `update()`, `delete()`
    - Add: `download()`, `get_questions()`, `publish_version()`, `list_versions()`
- [ ] **2.2** Implement JobResource with run/status/output
    - Create `resources/jobs.py`
    - Implement: `run()`, `get()`, `list()`, `get_output()`, `get_messages()`, `cancel()`
- [ ] **2.3** Add run_and_wait() helper with polling
    - Add polling mechanism to JobResource
    - Implement configurable timeout and poll interval
    - Return completed job with status
- [ ] **2.4** Create comprehensive Pydantic models for workflows
    - Update `models/workflows.py`
    - Add: `Workflow`, `WorkflowUploadRequest`, `WorkflowVersion`, `WorkflowQuestion`
    - Include all V3 API fields with proper aliases
- [ ] **2.5** Create comprehensive Pydantic models for jobs
    - Update `models/jobs.py`
    - Add: `Job`, `JobRunRequest`, `JobOutput`, `JobMessage`, `JobStatus` enum
    - Include all V3 API fields with proper aliases
- [ ] **2.6** Implement file upload for workflow publishing
    - Create `utils/file_utils.py` for file handling
    - Support multipart/form-data uploads with httpx
    - Handle large file streaming
- [ ] **2.7** Add pagination support in utils/pagination.py
    - Create `utils/pagination.py`
    - Implement `PaginatedResponse` model
    - Add iterator for paginated results
- [ ] **2.8** Unit tests with mocked responses (using respx)
    - Create test fixtures using respx
    - Mock OAuth2 token endpoints
    - Mock workflow and job CRUD operations
    - Achieve 85%+ coverage
- [ ] **2.9** Integration tests against live server
    - Update `tests/integration/test_live_client.py`
    - Test workflow publish → job run → output retrieval flow
    - Add skip conditions for missing credentials

**Deliverables:**
- Complete workflow lifecycle management (publish, update, delete, version)
- Job execution with polling and output retrieval
- 80%+ test coverage for workflow/job modules
- Working CI/CD deployment patterns

---

## Phase 3: Schedule & User Management (Week 5-6)

**Status:** Pending  
**Priority:** Medium  
**Goal:** Enable schedule automation and user provisioning

- [ ] **3.1** Implement ScheduleResource
    - Create `resources/schedules.py`
    - Implement: `list()`, `get()`, `create()`, `update()`, `delete()`
    - Add: `enable()`, `disable()`
- [ ] **3.2** Implement UserResource
    - Create `resources/users.py`
    - Implement: `list()`, `get()`, `create()`, `update()`, `delete()`
    - Add: `get_assets()`
- [ ] **3.3** Implement UserGroupResource
    - Create `resources/user_groups.py`
    - Implement: `list()`, `get()`, `create()`, `update()`, `delete()`
    - Add: `add_users()`, `remove_user()`
- [ ] **3.4** Create Pydantic models for schedules
    - Create `models/schedules.py`
    - Add: `Schedule`, `ScheduleCreateRequest`, `ScheduleFrequency` enum
- [ ] **3.5** Create Pydantic models for users/groups
    - Create `models/users.py`
    - Add: `User`, `UserGroup`, `UserCreateRequest`, `UserRole` enum
- [ ] **3.6** Unit and integration tests for schedules/users
    - Create test files for schedule and user resources
    - Mock API responses with respx
    - Test permission scenarios

**Deliverables:**
- Schedule CRUD operations with enable/disable
- User and group management
- 80%+ test coverage

---

## Phase 4: Collections, Credentials & Server (Week 7)

**Status:** Pending  
**Priority:** Low  
**Goal:** Complete remaining API coverage

- [ ] **4.1** Implement CollectionResource
    - Create `resources/collections.py`
    - Implement: `list()`, `get()`, `create()`, `update()`, `delete()`
    - Add: `add_workflow()`, `remove_workflow()`, `set_permissions()`
- [ ] **4.2** Implement CredentialResource (DCM)
    - Create `resources/credentials.py`
    - Implement: `list()`, `get()`, `create()`, `update()`, `delete()`
- [ ] **4.3** Implement ServerResource
    - Create `resources/server.py`
    - Implement: `get_info()`, `get_settings()`
- [ ] **4.4** Create Pydantic models for collections
    - Create `models/collections.py`
    - Add: `Collection`, `CollectionPermission`
- [ ] **4.5** Create Pydantic models for credentials
    - Create `models/credentials.py`
    - Add: `Credential`, `CredentialType` enum
- [ ] **4.6** Create Pydantic models for server info
    - Create `models/server.py`
    - Add: `ServerInfo`, `ServerSettings`
- [ ] **4.7** Unit and integration tests for collections/credentials/server
    - Create test files for remaining resources
    - Achieve 80%+ coverage

**Deliverables:**
- Collection management with permissions
- DCM credential management
- Server info/settings access
- Complete V3 API coverage

---

## Phase 5: Documentation & Release (Week 8)

**Status:** Pending  
**Priority:** High  
**Goal:** Production release to PyPI as v0.2.0

- [ ] **5.1** Comprehensive README with examples
    - Update README.md with new package name
    - Add installation instructions using UV
    - Include sync and async client examples
    - Add CI/CD integration examples
    - Document migration from v0.1.0
- [ ] **5.2** Docstrings for all public methods
    - Add Google-style docstrings to all public APIs
    - Include type hints and return types
    - Add usage examples in docstrings
- [ ] **5.3** Update .env.example with new variable names
    - Update all environment variable names to ALTERYX_*
    - Add descriptions for each variable
    - Include optional variables
- [ ] **5.4** Create CI/CD example scripts
    - Create `examples/` directory
    - Add `deploy_workflows.py` script
    - Add `promote_workflow.py` script
    - Add `run_workflow_tests.py` script
- [ ] **5.5** Update GitHub Actions workflow for UV
    - Update `.github/workflows/python-package.yml`
    - Use `astral-sh/setup-uv@v5` action
    - Add matrix testing for Python 3.10, 3.11, 3.12
    - Add publish workflow for releases
- [ ] **5.6** Bump version to 0.2.0 using uv version --bump minor
    - Run `uv version --bump minor` to update to 0.2.0
    - Verify version in `pyproject.toml`
- [ ] **5.7** Build package using uv build
    - Run `uv build` to create wheel and sdist
    - Verify build artifacts in `dist/`
- [ ] **5.8** Test publish to TestPyPI
    - Publish to TestPyPI first: `uv publish --index-url https://test.pypi.org/simple/`
    - Test installation from TestPyPI
    - Verify functionality
- [ ] **5.9** Publish to PyPI using uv publish
    - Publish to production PyPI: `uv publish`
    - Verify package listing
    - Test installation: `pip install alteryx-server-py`
- [ ] **5.10** Create CHANGELOG.md
    - Document all changes from v0.1.0 → v0.2.0
    - List breaking changes
    - Include migration guide
    - Add contributors

**Deliverables:**
- Production-ready documentation
- Published to PyPI as `alteryx-server-py` v0.2.0
- CI/CD templates and examples
- Complete migration guide

---

## Summary

| Phase | Tasks | Status | Priority |
|-------|-------|--------|----------|
| **Phase 1: Core Infrastructure** | 11 | 4/11 (36%) | High |
| **Phase 2: Workflow & Job Resources** | 9 | Pending | High |
| **Phase 3: Schedule & User Management** | 6 | Pending | Medium |
| **Phase 4: Collections, Credentials & Server** | 7 | Pending | Low |
| **Phase 5: Documentation & Release** | 10 | Pending | High |
| **Total** | **43** | **4/43 (9%)** | - |

---

## Next Steps

1. Start Phase 1: Core Infrastructure
2. Begin with task 1.1: Rename package structure
3. Update pyproject.toml with UV build backend
4. Migrate to httpx for sync/async support

---

**Last Updated:** January 9, 2026  
**Version:** 0.2.0-dev
