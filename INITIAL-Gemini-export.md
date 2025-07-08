name: "Alteryx Server API Python Wrapper for CI/CD and PyPI Publication"  
description: |

## **Purpose**

Build a robust and secure Python wrapper for the Alteryx Server API to enable automated Continuous Integration/Continuous Delivery (CI/CD) pipelines for publishing the resulting Python package to PyPI. This project leverages modern Python tooling: UV for package/environment management, Ruff for linting/formatting, and Pytest for testing.

## **Core Principles**

1. **Context is King**: Include ALL necessary documentation, examples, and caveats.  
2. **Validation Loops**: Provide executable tests/lints the AI can run and fix.  
3. **Information Dense**: Use keywords and patterns from the codebase.  
4. **Progressive Success**: Start simple, validate, then enhance.  
5. **Global rules**: Be sure to follow all rules in .github/copilot-instructions.md (referring to internal guidelines).

## **Goal**

Create a production-ready Python client library for the Alteryx Server API (compatible with versions 2021.4 and newer) that is securely published to PyPI via an automated CI/CD pipeline. The library should facilitate programmatic interaction and automation of Alteryx workflows, enhancing developer productivity and ensuring high code quality.

## **Why**

* **Business value**: Automates interaction with Alteryx Server, enabling CI/CD for Alteryx workflows and simplifying Python integration.  
* **Integration**: Modernizes the existing AlteryxGalleryAPI project by making it PyPI-distributable and integrating modern Python tooling.  
* **Problems solved**: Reduces manual effort for Alteryx Server interactions, improves code quality through automated checks, ensures reproducible development environments, and establishes a secure, automated release process for the Python package.

## **What**

A Python library that:

* Provides comprehensive methods for key Alteryx Server API functionalities (e.g., workflow listing, execution, job status, output retrieval).  
* Supports API Key and OAuth2.0 authentication.  
* Is built and managed using UV for dependencies and virtual environments.  
* Adheres to code quality standards enforced by Ruff.  
* Is thoroughly tested using Pytest (unit and integration tests).  
* Is type-checked using Mypy or Pyright (with future consideration for ty).  
* Is published securely to PyPI via an automated CI/CD pipeline (e.g., GitHub Actions) using Trusted Publishers and OIDC.  
* Includes essential documentation for installation and usage.

### **Success Criteria**

* \[ \] Core Alteryx API functionalities (listing, execution, status, output) are implemented and tested.  
* \[ \] UV is fully integrated for package and environment management, with uv.lock for reproducible builds.  
* \[ \] Ruff is configured and integrated for linting and formatting, enforced in CI.  
* \[ \] Pytest suite provides comprehensive unit and integration test coverage (target: 80%+).  
* \[ \] A mature type checker (Mypy/Pyright) is integrated into the CI pipeline.  
* \[ \] Automated CI/CD pipeline successfully builds, tests, lints, type-checks, signs, and securely publishes the package to PyPI using OIDC/Trusted Publishers.  
* \[ \] Documentation for installation, API usage, and CI/CD setup is clear and available.  
* \[ \] All sensitive credentials are handled securely via CI/CD secrets management.  
* \[ \] Built artifacts are cryptographically signed.

All Needed Context:

### **Documentation & References**

\- url: https://github.com/Sivivatu/AlteryxGalleryAPI/tree/workflow-methods  
  why: Existing project codebase to build upon, including current development branch.

\- url: https://help.alteryx.com/current/en/server.html  
  why: Official Alteryx Server Help pages for API documentation and general server information.

\- url: https://spider.theinformationlab.co.uk/webapi//swagger/ui/index  
  why: Example Alteryx Server API Swagger documentation for endpoint details and schemas.

\- url: https://docs.astral.sh/uv/  
  why: Official UV documentation for package and environment management.

\- url: https://docs.astral.sh/ruff/  
  why: Official Ruff documentation for linting and formatting.

\- url: https://docs.astral.sh/ty  
  why: Documentation for \`ty\` (Red Knot), the experimental type checker from Astral, for evaluation.

\- url: https://github.com/coleam00/context-engineering-intro  
  why: Context Engineering repository for planning and development steps.

Validation Loops:

### **Level 1: Unit Test**

\# tests/unit/test\_connection.py  
import pytest  
from unittest.mock import MagicMock  
from your\_package\_name.connection import AlteryxConnection

def test\_alteryx\_connection\_initialization():  
    """  
    Test that AlteryxConnection initializes correctly with API key and secret.  
    """  
    mock\_api\_key \= "test\_key"  
    mock\_api\_secret \= "test\_secret"  
    conn \= AlteryxConnection(base\_url="http://localhost", api\_key=mock\_api\_key, api\_secret=mock\_api\_secret)  
    assert conn.api\_key \== mock\_api\_key  
    assert conn.api\_secret \== mock\_api\_secret  
    assert conn.base\_url \== "http://localhost"

def test\_alteryx\_connection\_oauth\_token\_set():  
    """  
    Test that AlteryxConnection can be initialized with an OAuth token.  
    """  
    mock\_oauth\_token \= "mock\_oauth\_token\_123"  
    conn \= AlteryxConnection(base\_url="http://localhost", oauth\_token=mock\_oauth\_token)  
    assert conn.oauth\_token \== mock\_oauth\_token  
    assert conn.api\_key is None \# Should not set api\_key if oauth\_token is provided

def test\_alteryx\_connection\_request\_headers():  
    """  
    Test that the correct headers are generated for API key authentication.  
    """  
    conn \= AlteryxConnection(base\_url="http://localhost", api\_key="test\_key", api\_secret="test\_secret")  
    headers \= conn.\_get\_headers() \# Assuming an internal method for header generation  
    assert "Authorization" in headers  
    assert "oauth\_consumer\_key" in headers  
    assert "oauth\_signature\_method" in headers  
    assert "oauth\_timestamp" in headers  
    assert "oauth\_nonce" in headers  
    assert "oauth\_version" in headers  
    assert headers\["oauth\_consumer\_key"\] \== "test\_key"

def test\_alteryx\_connection\_request\_headers\_oauth():  
    """  
    Test that the correct headers are generated for OAuth token authentication.  
    """  
    conn \= AlteryxConnection(base\_url="http://localhost", oauth\_token="mock\_oauth\_token\_123")  
    headers \= conn.\_get\_headers()  
    assert "Authorization" in headers  
    assert headers\["Authorization"\] \== "Bearer mock\_oauth\_token\_123"  
    assert "oauth\_consumer\_key" not in headers \# Should not have API key specific headers  
\`\`\`bash  
\# Run unit tests  
uv run pytest tests/unit/ \-v  
\# If failing: Read error, understand root cause, fix code, re-run (never mock to pass)

### **Level 2: Integration Test**

\# tests/integration/test\_workflows.py  
import pytest  
import requests\_mock \# For mocking HTTP requests in integration tests  
from your\_package\_name.connection import AlteryxConnection  
from your\_package\_name.workflows import WorkflowManager \# Assuming a WorkflowManager class

@pytest.fixture  
def mock\_alteryx\_connection():  
    """Fixture to provide a mocked AlteryxConnection for integration tests."""  
    with requests\_mock.Mocker() as m:  
        \# Mock the base URL for all requests  
        m.get("\[http://mock-alteryx-server.com/webapi/v1/workflows/subscription/\](http://mock-alteryx-server.com/webapi/v1/workflows/subscription/)", json={"workflows": \[\]})  
        m.post("\[http://mock-alteryx-server.com/webapi/v1/workflows/123/jobs/\](http://mock-alteryx-server.com/webapi/v1/workflows/123/jobs/)", json={"id": "job123"})  
        m.get("\[http://mock-alteryx-server.com/webapi/v1/jobs/job123/\](http://mock-alteryx-server.com/webapi/v1/jobs/job123/)", json={"status": "Complete"})  
        yield AlteryxConnection(base\_url="\[http://mock-alteryx-server.com/webapi/\](http://mock-alteryx-server.com/webapi/)", api\_key="test", api\_secret="test")

def test\_list\_workflows\_integration(mock\_alteryx\_connection):  
    """  
    Test listing workflows via a mocked Alteryx API endpoint.  
    """  
    workflow\_manager \= WorkflowManager(mock\_alteryx\_connection)  
    workflows \= workflow\_manager.list\_workflows()  
    assert isinstance(workflows, list)  
    \# Add more specific assertions based on expected mocked response

def test\_execute\_workflow\_integration(mock\_alteryx\_connection):  
    """  
    Test executing a workflow and getting a job ID via a mocked Alteryx API.  
    """  
    workflow\_manager \= WorkflowManager(mock\_alteryx\_connection)  
    app\_id \= "123"  
    payload \= {"questions": \[\]}  
    job\_id \= workflow\_manager.execute\_workflow(app\_id, payload)  
    assert job\_id \== "job123"

def test\_get\_job\_status\_integration(mock\_alteryx\_connection):  
    """  
    Test retrieving job status via a mocked Alteryx API.  
    """  
    workflow\_manager \= WorkflowManager(mock\_alteryx\_connection)  
    job\_id \= "job123"  
    status \= workflow\_manager.get\_job\_status(job\_id)  
    assert status \== "Complete"  
\`\`\`bash  
\# Run integration tests  
uv run pytest tests/integration/ \-v  
\# If failing: Check mocked responses, network calls, and API wrapper logic. Fix code, re-run.

### **Level 3: End-to-End Test (Manual/CLI Simulation)**

\# Example of a manual end-to-end test using a simple Python script  
\# This assumes your\_package\_name is installed and configured with environment variables  
\# for Alteryx API key/secret or OAuth token.

\# 1\. Install the package (after building it locally)  
\# uv pip install .

\# 2\. Set environment variables (replace with your actual Alteryx Server details)  
\# export ALTERYX\_BASE\_URL="https://your-alteryx-server.com/webapi/"  
\# export ALTERYX\_API\_KEY="YOUR\_API\_KEY"  
\# export ALTERYX\_API\_SECRET="YOUR\_API\_SECRET"  
\# OR export ALTERYX\_OAUTH\_TOKEN="YOUR\_OAUTH\_TOKEN"

\# 3\. Run a simple script to list workflows and execute one  
\# python \-c "  
\# from your\_package\_name.connection import AlteryxConnection  
\# from your\_package\_name.workflows import WorkflowManager  
\# import os  
\#  
\# try:  
\#     base\_url \= os.getenv('ALTERYX\_BASE\_URL')  
\#     api\_key \= os.getenv('ALTERYX\_API\_KEY')  
\#     api\_secret \= os.getenv('ALTERYX\_API\_SECRET')  
\#     oauth\_token \= os.getenv('ALTERYX\_OAUTH\_TOKEN')  
\#  
\#     if oauth\_token:  
\#         conn \= AlteryxConnection(base\_url=base\_url, oauth\_token=oauth\_token)  
\#     elif api\_key and api\_secret:  
\#         conn \= AlteryxConnection(base\_url=base\_url, api\_key=api\_key, api\_secret=api\_secret)  
\#     else:  
\#         raise ValueError('Alteryx API credentials not found in environment variables.')  
\#  
\#     wf\_manager \= WorkflowManager(conn)  
\#  
\#     print('Listing workflows...')  
\#     workflows \= wf\_manager.list\_workflows()  
\#     if workflows:  
\#         print(f'Found {len(workflows)} workflows. First workflow: {workflows\[0\].get("name")}')  
\#         \# Pick a known analytical app ID for execution (replace with a real one)  
\#         example\_app\_id \= 'YOUR\_ANALYTICAL\_APP\_ID'  
\#         print(f'Executing analytical app ID: {example\_app\_id}...')  
\#         job\_id \= wf\_manager.execute\_workflow(example\_app\_id, {}) \# Empty payload for simplicity  
\#         print(f'Job started with ID: {job\_id}')  
\#  
\#         status \= wf\_manager.get\_job\_status(job\_id)  
\#         print(f'Job {job\_id} status: {status}')  
\#         \# In a real scenario, you'd poll the status until complete  
\#  
\#     else:  
\#         print('No workflows found.')  
\#  
\# except Exception as e:  
\#     print(f'An error occurred: {e}')  
\# "

\# Expected: Successful connection, listing of workflows, and a job ID for the executed workflow.  
\# If error: Check environment variables, Alteryx Server status, and network connectivity.  
\# Check logs for detailed API errors.

Final Validation Checklist:

* \[ \] All tests pass: uv run pytest tests/ \-v  
* \[ \] No linting errors: uv run ruff check src/  
* \[ \] No type errors: uv run mypy src/ (or uv run pyright src/)  
* \[ \] Manual end-to-end test successful against a live Alteryx Server instance.  
* \[ \] CI/CD pipeline runs successfully on push/PR, including linting, testing, type-checking, SAST, and artifact signing.  
* \[ \] Package is securely published to PyPI upon new version tag.  
* \[ \] All sensitive data (API keys, secrets) are handled via CI/CD secrets and not hardcoded.  
* \[ \] Documentation is complete and accurate for installation and API usage.  
* \[ \] pyproject.toml and uv.lock are up-to-date and reflect all dependencies.

Anti-Patterns to Avoid:

* ❌ Don't hardcode Alteryx API keys or secrets directly in source code. Always use environment variables or a secure secrets management system.  
* ❌ Don't skip type hints. They improve code readability, maintainability, and allow for static analysis.  
* ❌ Don't ignore error handling for API responses (e.g., 4xx, 5xx status codes). Implement robust error reporting.  
* ❌ Don't commit uv.lock files that are not consistent with pyproject.toml. Always run uv lock after dependency changes.  
* ❌ Don't use traditional long-lived PyPI API tokens for publication. Leverage OIDC and Trusted Publishers for enhanced security.  
* ❌ Don't neglect comprehensive testing. Unit, integration, and end-to-end tests are crucial for reliability.  
* ❌ Don't rely solely on manual testing; automate as much as possible through CI/CD.  
* ❌ Don't expose sensitive information in CI/CD logs. Ensure secrets are masked.

## **Confidence Score: 9/10**

High confidence due to:

* Clear, well-defined project scope and objectives.  
* Strong foundation in existing AlteryxGalleryAPI project.  
* Adoption of modern, high-performance Python tooling (UV, Ruff, Pytest) which streamlines development and ensures quality.  
* Explicit focus on robust security measures for PyPI publication (OIDC, Trusted Publishers, artifact signing).  
* Comprehensive validation loops and checklist for iterative development and quality assurance.  
* Access to necessary documentation for Alteryx Server API and chosen tools.

Minor uncertainty remains regarding:

* The exact current state and compatibility of the AlteryxGalleryAPI codebase with modern Python 3.9+ and new tooling, which might require initial refactoring effort.  
* The "early experimental preview" status of ty for type checking, necessitating a fallback to more mature tools initially.