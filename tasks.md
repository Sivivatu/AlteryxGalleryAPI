# Alteryx Server API Python Package - Task Management

## Current Tasks

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
- [x] **Task 2: Authentication Module Development**
    * [x] Task 2.1: Implement API key/secret-based authentication (OAuth 1.0a via `requests-oauthlib`).
    * [ ] Task 2.2: Implement token based authentication (V3 style - *Deferred, V1 uses OAuth1*).
    * [ ] Task 2.3: Implement function to retrieve authentication token (*Deferred, V1 uses OAuth1*).
    * [ ] Task 2.4: Add unit tests for authentication.
- [x] **Task 3: Workflow Management Module (V1 API)**
    * [x] Task 3.1: Implement functions for listing workflows (`get_subscription_workflows`).
    * [x] Task 3.2: Implement functions for uploading workflows (`publish_workflow`).
    * [ ] Task 3.3: Implement functions for downloading workflows.
    * [x] Task 3.4: Implement functions for deleting workflows (`delete_workflow`).
    * [x] Task 3.5: Implement functions for updating workflows (`update_workflow`).
    * [ ] Task 3.6: Add unit tests for workflow management.

## Backlog

- [ ] **Task 4: Schedule Management Module**
    * [ ] Task 4.1: Implement functions for creating schedules.
    * [ ] Task 4.2: Implement functions for listing schedules.
    * [ ] Task 4.3: Implement functions for updating schedules.
    * [ ] Task 4.4: Implement functions for deleting schedules.
    * [ ] Task 4.5: Add unit tests for schedule management.
- [x] **Task 5: Job Management Module (V1 API)**
    * [x] Task 5.1: Implement functions for listing jobs (covered by `get_job_status`).
    * [x] Task 5.2: Implement functions for retrieving job results (`get_job_output`).
    * [x] Task 5.3: Implement functions for queuing jobs (`queue_job`).
    * [ ] Task 5.4: Implement functions for cancelling jobs.
    * [ ] Task 5.5: Add unit tests for job management.
- [ ] **Task 6: User and Group Management Module**
    * [ ] Task 6.1: Implement functions for listing users.
    * [ ] Task 6.2: Implement functions for creating users.
- [ ] **Task 7: Configuration Management**
    * [ ] Task 7.1: Implement configuration file parsing.
    * [ ] Task 7.2: Implement environment variable configuration.
    * [ ] Task 7.3: Implement in-code configuration.
- [ ] **Task 8: Documentation**
    * [ ] Task 8.1: Write API documentation using Sphinx or MkDocs.
    * [ ] Task 8.2: Create usage examples and tutorials.
    * [ ] Task 8.3: Document error handling and best practices.
- [ ] **Task 9: CI/CD Integration**
    * [ ] Task 9.1: Set up CI pipeline for automated testing.
    * [ ] Task 9.2: Set up CD pipeline for package deployment.
- [ ] **Task 10: Rate Limit Handling**
    * [ ] Task 10.1: Implement rate limit detection.
    * [ ] Task 10.2: Implement retry logic with exponential backoff.
- [ ] **Task 11: Pydantic/dataclasses implementation**
    * [ ] Task 11.1: Implement pydantic or dataclasses for request and response validation.
    * [ ] Task 11.2: Add tests for validation.