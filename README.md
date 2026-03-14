# AlteryxGalleryAPI


AlteryxGalleryAPI is a modern Python client for connecting to the Alteryx Workflow Gallery API.
It supports secure authentication, workflow management, and job execution, and is designed for CI/CD and PyPI publishing.

It includes methods that can request Gallery information, send workflow execution commands, monitor
job status, and retrieving the desired workflow output.

The official Alteryx API documentation can be found at: https://gallery.alteryx.com/api-docs/

## Setup and Install


## Environment Setup

1. **Clone the repository**
2. **Install dependencies** using [UV](https://docs.astral.sh/uv/):
   ```bash
   uv pip install -r requirements.txt
   ```
   Or, for development:
   ```bash
   uv pip install -r requirements.txt -r dev-requirements.txt
   ```

3. **Configure environment variables**:
   - Copy `.env.example` to `.env` and fill in your credentials:
     ```bash
     cp .env.example .env
     # Edit .env and set BASE_URL, API_KEY, API_SECRET, TEST_OWNER_ID
     ```

4. **Run tests**:
   ```bash
   uv pip install pytest
   uv run pytest
   ```

## Environment Variables

The following variables must be set in your `.env` file or your environment:

- `BASE_URL` - The base URL of your Alteryx Gallery (e.g., https://your-gallery-url/webapi/)
- `API_KEY` - Your Alteryx API key
- `API_SECRET` - Your Alteryx API secret
- `TEST_OWNER_ID` - (For tests) The owner ID for test workflows

The client will automatically load these from `.env` using `python-dotenv`.


## Usage

```python
from alteryx_gallery_api.client import AlteryxClient

# Credentials are loaded automatically from .env or environment variables
client = AlteryxClient()

# Or, you can pass credentials directly (overrides .env):
# client = AlteryxClient(base_url="https://your-gallery-url/webapi/", api_key="...", api_secret="...")

# Example: List workflows
workflows = client.get_subscription_workflows()
print(workflows)
```


## Example API Methods

- `get_subscription_workflows()` — List all workflows in your subscription
- `get_workflow_info(workflow_id)` — Get details for a workflow
- `publish_workflow(file_path, name, owner_email, ...)` — Publish a new workflow
- `update_workflow(workflow_id, file_path, ...)` — Update an existing workflow
- `delete_workflow(workflow_id)` — Delete a workflow
- `queue_job(workflow_id, questions=None, priority=None)` — Queue a job for a workflow
- `get_job_status(job_id)` — Get the status of a job
- `get_job_output(job_id, output_id)` — Download job output

See the code and docstrings for full details and parameters.
