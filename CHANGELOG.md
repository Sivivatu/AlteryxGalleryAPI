# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-04-30

### Added

- Added a modern `alteryx_server_py` package with typed sync and async clients.
- Added OAuth2 client-credentials authentication with automatic token refresh.
- Added resource modules for workflows, jobs, schedules, users, user groups, collections, credentials, and server metadata.
- Added comprehensive Pydantic models for V3 API responses and request payloads.
- Added file upload helpers, pagination utilities, retry handling, and richer exception types.
- Added unit and live-integration test coverage across the V3 API surface.
- Added CI/CD example scripts for deployment, promotion, workflow test execution, and admin resource inspection.
- Added GitHub Actions workflows for branch validation, main-branch validation, package builds, and automated release publishing.

### Changed

- Renamed the primary distribution to `alteryx-server-py`.
- Moved active development from the legacy `alteryx_gallery_api` implementation to `src/alteryx_server_py`.
- Switched HTTP transport from `requests` to `httpx` to support both sync and async clients consistently.
- Standardised environment configuration on `ALTERYX_*` variable names.
- Updated local development, testing, and packaging workflows around `uv`.
- Reworked the public API around resource accessors such as `client.workflows`, `client.jobs`, and `client.collections`.

### Fixed

- Repaired branch fallout from merge-conflict markers committed into source, tests, and project instructions.
- Corrected request content-type handling for endpoints that expect form-encoded payloads.
- Restored missing sync accessors for jobs, schedules, users, and user groups.
- Fixed stale tests that still referenced the archived `alteryx_gallery_api` package or outdated client methods.
- Corrected async test/resource mismatches and improved not-found handling in async job cancellation.

### Breaking Changes

- Imports should now target `alteryx_server_py` instead of `alteryx_gallery_api`.
- Authentication now uses OAuth2 client credentials instead of the earlier API key and secret flow.
- The preferred client API is resource-based. For example, use `client.workflows.list()` instead of older top-level helper patterns.
- Environment variables now use the `ALTERYX_*` prefix, including `ALTERYX_BASE_URL`, `ALTERYX_CLIENT_ID`, and `ALTERYX_CLIENT_SECRET`.
- Supported Python versions are now 3.10 through 3.12.

### Migration Guide

1. Update imports from `alteryx_gallery_api` to `alteryx_server_py`.
2. Replace legacy credential environment variables with the new `ALTERYX_*` names.
3. Move any direct helper-method calls to the resource-based client surface.
4. Rebuild automation or deployment jobs to use `uv sync`, `uv run pytest`, and `uv build` where applicable.
5. Revalidate workflow deployment and scheduling code against the V3 request and model shapes before promoting to production.

### Contributors

- Paul Houghton
- Theamazingdp
- Cavin Dsouza
- warped-quasar
- Copilot and copilot-swe-agent[bot]
- dependabot[bot]
