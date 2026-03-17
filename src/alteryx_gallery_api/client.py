"""
Core client for interacting with the Alteryx Gallery API.
"""

import logging
import os
import sys
from typing import Any, Dict, List, Optional, Union

import requests
from dotenv import load_dotenv
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from .exceptions import (
    AlteryxAPIError,
    AuthenticationError,
    WorkflowNotFoundError,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlteryxClient:
    base_webapi_url: str
    api_key: str
    api_secret: str
    """
    A client for interacting with the Alteryx Server (Gallery) API using OAuth 2.0.

    Handles authentication and provides methods for common API operations like
    managing workflows and jobs.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        verify_ssl: bool = True,
        timeout: int = 30,
        authenticate_on_init: bool = True,
    ):
        """
        Initializes the AlteryxClient.

        Args:
            base_url (str, optional): The base URL of the Alteryx Server instance (e.g., 'https://your-gallery-url/webapi/').
            api_key (str, optional): The API Access Key.
            api_secret (str, optional): The API Access Secret.
            verify_ssl (bool, optional): Whether to verify SSL certificates. Defaults to True.
            timeout (int, optional): Default request timeout in seconds. Defaults to 30.
        """
        load_dotenv()
        _base_webapi_url = base_url or os.getenv("ALTERYX_BASE_URL")
        _api_key = api_key or os.getenv("ALTERYX_CLIENT_ID")
        _api_secret = api_secret or os.getenv("ALTERYX_CLIENT_SECRET")
        if not _base_webapi_url:
            raise ValueError("ALTERYX_BASE_URL must be provided as an argument or environment variable.")
        if not _api_key:
            raise ValueError("ALTERYX_CLIENT_ID must be provided as an argument or environment variable.")
        if not _api_secret:
            raise ValueError("ALTERYX_CLIENT_SECRET must be provided as an argument or environment variable.")
        self.base_webapi_url = _base_webapi_url
        self.api_key = _api_key
        self.api_secret = _api_secret
        self.verify_ssl = verify_ssl
        self.timeout = timeout

        if not isinstance(self.base_webapi_url, str):
            raise TypeError("base_url must be a string.")

        try:
            from urllib.parse import urlparse

            result = urlparse(self.base_webapi_url)
            if not all([result.scheme, result.netloc, result.path]):
                raise ValueError(
                    "Invalid base_url: Must include scheme, domain, and path (e.g., https://your-gallery-url/webapi/)."
                )
        except Exception as e:
            raise ValueError(f"Invalid base_url: {e}")

        logger.info(f"AlteryxClient initialized for {self.base_webapi_url}")
        if authenticate_on_init:
            self._session = self._create_session()
            # Test authentication on initialization
            try:
                # TODO: Replace with a lightweight endpoint currently returning all workflows.
                self.get_workflows()  # A simple call to verify credentials
                logger.info("Authentication successful.")
            except AlteryxAPIError as e:
                logger.error(f"Initial authentication check failed: {e}")
                # Re-raise as AuthenticationError for clarity
                raise AuthenticationError(f"Initial authentication check failed: {e}") from e
        else:
            self._session = None

    def _create_session(self) -> requests.Session:
        """Creates a requests session with OAuth2 authentication."""
        token_url = f"{self.base_webapi_url.rstrip('/')}/oauth2/token"
        logger.debug(f"Attempting to fetch OAuth2 token from {token_url}")

        client = BackendApplicationClient(client_id=self.api_key)
        session = OAuth2Session(client=client)

        try:
            token = session.fetch_token(
                token_url=token_url,
                client_id=self.api_key,
                client_secret=self.api_secret,
                verify=self.verify_ssl,
                timeout=self.timeout,
            )
            logger.debug("Successfully fetched OAuth2 token.")
            # Store the token details if needed for expiry handling later
            self._token = token
            # Set a default header for content type if needed (often application/json)
            session.headers.update({"Content-Type": "application/json"})
            return session
        except Exception as e:
            logger.error(f"OAuth2 token fetch failed: {e}")
            raise AuthenticationError(f"Failed to fetch OAuth2 token: {e}") from e

    def _request(
        self,
        method: str,
        endpoint: str,
        api_version: str = "v3",  # Default to v3 API
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> requests.Response:
        """
        Internal method to make authenticated requests to the Alteryx API.

        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE).
            endpoint (str): API endpoint path (e.g., 'workflows/subscription/').
            api_version (str): The API version path component (e.g., 'v1', 'v3').
            params (Optional[Dict[str, Any]]): URL query parameters.
            data (Optional[Union[Dict[str, Any], str]]): Request body data (form-encoded).
            json_data (Optional[Dict[str, Any]]): Request body data (JSON-encoded).
            files (Optional[Dict[str, Any]]): Files to upload.
            **kwargs: Additional arguments passed to requests.request.

        Returns:
            requests.Response: The raw response object.

        Raises:
            AuthenticationError: If the request results in a 401 Unauthorized.
            AlteryxAPIError: For other non-successful status codes or request errors.
        """
        # Select base URL based on typical V1/V3 usage
        if api_version.lower().startswith("v3") or endpoint.startswith("dcm"):
            base_url_to_use = self.base_webapi_url
            # V3 endpoints often don't include the version in the path itself
            # Construct URL carefully based on endpoint documentation if needed
            if endpoint.startswith("v3/"):
                url = f"{base_url_to_use}{endpoint}"  # Assume full path given
            else:
                url = f"{base_url_to_use}{api_version}/{endpoint}"
        else:
            # V1 endpoints are typically relative to the base webapi url as well
            base_url_to_use = self.base_webapi_url
            url = f"{base_url_to_use}{endpoint}"  # V1 endpoints often include version implicitly or are under /api/

        # Ensure endpoint doesn't start with / if base URL already ends with /
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]

        # Recalculate URL based on final decision
        if api_version.lower().startswith("v3") or endpoint.startswith("dcm"):
            if endpoint.startswith("v3/"):
                url = f"{self.base_webapi_url}{endpoint}"
            else:
                url = f"{self.base_webapi_url}{api_version}/{endpoint}"
        else:
            # Adjust V1 endpoint construction if necessary based on API structure
            # Assuming V1 endpoints are also relative to base_webapi_url
            url = f"{self.base_webapi_url.rstrip('/')}/{endpoint.lstrip('/')}"

        logger.debug(f"Requesting {method} {url}")
        logger.debug(f"Params: {params}")
        logger.debug(f"Data: {data}")
        logger.debug(f"JSON: {json_data}")

        try:
            # Ensure session is initialized
            if self._session is None:
                self._session = self._create_session()
            response = self._session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json_data,
                files=files,
                timeout=self.timeout,
                **kwargs,
            )

            logger.debug(f"Response Status Code: {response.status_code}")
            logger.debug(f"Response Headers: {response.headers}")
            # Limit logging response body size
            response_body_preview = response.text[:500] + ("..." if len(response.text) > 500 else "")
            logger.debug(f"Response Body Preview: {response_body_preview}")

            response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
            return response

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                logger.error(f"Authentication failed for {url}: {e.response.text}")
                raise AuthenticationError() from e
            elif e.response.status_code == 404:
                # Generic 404 handling, specific methods might raise WorkflowNotFoundError
                logger.warning(f"Resource not found (404) for {url}: {e.response.text}")
                raise AlteryxAPIError(
                    f"Resource not found at {endpoint}",
                    status_code=404,
                    response_text=e.response.text,
                ) from e
            else:
                logger.error(f"HTTP error occurred for {url}: {e.response.status_code} - {e.response.text}")
                raise AlteryxAPIError(
                    f"HTTP Error: {e.response.status_code} for endpoint {endpoint}",
                    status_code=e.response.status_code,
                    response_text=e.response.text,
                ) from e
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            raise AlteryxAPIError(f"Request failed for endpoint {endpoint}: {e}") from e

    # --- Workflow Management ---

    def get_workflows(self, workflow_id: Optional[str] = None) -> List[Workflow]:
        """
        Retrieves a list of workflows available to the user (V3 API).
        If workflow_id is provided, retrieves details for that specific workflow.

        Args:
            workflow_id (str, optional): The ID of a specific workflow to retrieve.

        Returns:
            List[Workflow]: A list of Workflow models.

        Raises:
            AuthenticationError: If authentication fails.
            AlteryxAPIError: For other API request errors.
        """
        logger.info("Fetching subscription workflows...")
        if workflow_id is None:
            response = self._request("GET", "workflows")
            payload = response.json()
            result: List[Workflow] = []
            if isinstance(payload, list):
                result = [Workflow.model_validate(item) for item in payload]
            elif isinstance(payload, dict) and isinstance(payload.get("workflows"), list):
                result = [Workflow.model_validate(item) for item in payload["workflows"]]
            else:
                # Attempt to coerce single item
                try:
                    result = [Workflow.model_validate(payload)]
                except Exception:
                    logger.warning("Unexpected workflows payload structure; returning empty list")
                    result = []
            logger.info(f"Found {len(result)} workflows.")
            return result
        else:
            try:
                response = self._request("GET", f"workflows/{workflow_id}")
                payload = response.json()
                wf = Workflow.model_validate(payload)
                logger.info(f"Found {workflow_id}.")
                return [wf]
            except Exception as e:
                logger.error(f"Error fetching workflow {workflow_id}: {e}")
                logger.error(f"Exiting due to error: {e}")
                sys.exit(1)

    def get_workflow_info(self, workflow_id: WorkflowId) -> Dict[str, Any]:
        """
        Retrieves detailed information about a specific workflow (V1 API).

        Args:
            workflow_id (WorkflowId): The ID of the workflow (usually a MongoDB ObjectId).

        Returns:
            Dict[str, Any]: A dictionary containing workflow details.

        Raises:
            WorkflowNotFoundError: If the workflow with the given ID is not found.
            AuthenticationError: If authentication fails.
            AlteryxAPIError: For other API request errors.
        """
        logger.info(f"Fetching details for workflow ID: {workflow_id}")
        endpoint = f"workflows/{workflow_id}/"
        try:
            response = self._request("GET", endpoint)
            info = response.json()
            logger.info(f"Successfully retrieved info for workflow ID: {workflow_id}")
            return info
        except AlteryxAPIError as e:
            if e.status_code == 404:
                raise WorkflowNotFoundError(workflow_id) from e
            raise  # Re-raise other AlteryxAPIErrors

    # def publish_workflow(
    #     self, file_path: str, name: str, owner_email: str, make_public: bool = False, **kwargs
    # ) -> Dict[str, Any]:
    #     """
    #     Publishes a new workflow to the gallery (V1 API).

    #     Note: This endpoint requires form-data, not JSON.

    #     Args:
    #         file_path (str): The local path to the .yxzp or .yxmd file to upload.
    #         name (str): The name to give the workflow in the Gallery.
    #         owner_email (str): The email address of the user who should own the workflow.
    #                             This user must exist on the server.
    #         make_public (bool): Set to True to make the workflow available in the public Gallery.
    #                             Defaults to False (places in user's private studio).
    #         **kwargs: Additional optional parameters accepted by the V1 POST /workflows/ endpoint.
    #                   Common examples include:
    #                   - 'workerTag': Assign a specific worker tag.
    #                   - 'canDownload': (bool) Allow users to download the workflow file.
    #                   - 'description': A description for the workflow.

    #     Returns:
    #         Dict[str, Any]: A dictionary containing details of the newly published workflow,
    #                         including its new ID.

    #     Raises:
    #         FileNotFoundError: If the file_path does not exist.
    #         AuthenticationError: If authentication fails.
    #         AlteryxAPIError: For other API request errors (e.g., invalid owner email,
    #                            upload failure).
    #     """
    #     logger.info(f"Attempting to publish workflow '{name}' from {file_path}")
    #     endpoint = "workflows/"

    #     try:
    #         with open(file_path, "rb") as f:
    #             files = {"file": (file_path.split("\\")[-1], f)}  # Use filename from path
    #             data = {
    #                 "name": name,
    #                 "owner": owner_email,
    #                 "makePublic": str(make_public).lower(),  # API expects 'true' or 'false'
    #                 **kwargs,  # Include any additional parameters
    #             }

    #             logger.debug(f"Publishing with data: {data}")
    #             # Important: V1 publish expects form-data, so use 'data' and 'files', not 'json'
    #             response = self._request("POST", endpoint, data=data, files=files)

    #         result = response.json()
    #         logger.info(f"Successfully published workflow '{name}' with ID: {result.get('id')}")
    #         return result
    #     except FileNotFoundError as e:
    #         logger.error(f"Workflow file not found at path: {file_path}")
    #         raise e
    #     except AlteryxAPIError as e:
    #         logger.error(f"Failed to publish workflow '{name}': {e}")
    #         raise e  # Re-raise the specific API error

    # def update_workflow(self, workflow_id: str, file_path: str, **kwargs) -> Dict[str, Any]:
    #     """
    #     Updates an existing workflow by publishing a new version (V1 API).

    #     Note: This endpoint requires form-data, not JSON.

    #     Args:
    #         workflow_id (str): The ID of the workflow to update.
    #         file_path (str): The local path to the new .yxzp or .yxmd file version.
    #         **kwargs: Additional optional parameters accepted by the V1 PUT /workflows/{appId} endpoint.
    #                   Common examples include:
    #                   - 'makePublic': (bool) Change the public status.
    #                   - 'workerTag': Change the assigned worker tag.
    #                   - 'canDownload': (bool) Change download permission.
    #                   - 'description': Update the description.
    #                   - 'owner': Reassign ownership (provide user email).

    #     Returns:
    #         Dict[str, Any]: A dictionary containing details of the updated workflow.

    #     Raises:
    #         FileNotFoundError: If the file_path does not exist.
    #         WorkflowNotFoundError: If the workflow with the given ID is not found.
    #         AuthenticationError: If authentication fails.
    #         AlteryxAPIError: For other API request errors.
    #     """
    #     logger.info(f"Attempting to update workflow ID: {workflow_id} from {file_path}")
    #     endpoint = f"workflows/{workflow_id}/"

    #     try:
    #         # First, check if workflow exists to provide a better error message
    #         self.get_workflow_info(workflow_id)

    #         with open(file_path, "rb") as f:
    #             files = {"file": (file_path.split("\\")[-1], f)}  # Use filename from path
    #             data = {k: str(v).lower() if isinstance(v, bool) else v for k, v in kwargs.items()}  # Convert bools

    #             logger.debug(f"Updating with data: {data}")
    #             # Important: V1 update expects form-data, so use 'data' and 'files', not 'json'
    #             response = self._request("PUT", endpoint, data=data, files=files)

    #         result = response.json()
    #         logger.info(f"Successfully updated workflow ID: {workflow_id}")
    #         return result
    #     except FileNotFoundError as e:
    #         logger.error(f"New workflow file version not found at path: {file_path}")
    #         raise e
    #     except AlteryxAPIError as e:
    #         if e.status_code == 404:  # Handle 404 from PUT specifically
    #             raise WorkflowNotFoundError(
    #                 workflow_id, message=f"Failed to update: Workflow ID '{workflow_id}' not found."
    #             ) from e
    #         logger.error(f"Failed to update workflow ID {workflow_id}: {e}")
    #         raise e  # Re-raise other API errors

    # def delete_workflow(self, workflow_id: str) -> None:
    #     """
    #     Deletes a workflow from the Gallery (V1 API).

    #     Args:
    #         workflow_id (str): The ID of the workflow to delete.

    #     Returns:
    #         None

    #     Raises:
    #         WorkflowNotFoundError: If the workflow with the given ID is not found.
    #         AuthenticationError: If authentication fails.
    #         AlteryxAPIError: For other API request errors.
    #     """
    #     logger.info(f"Attempting to delete workflow ID: {workflow_id}")
    #     endpoint = f"workflows/{workflow_id}/"
    #     try:
    #         # Use _request directly, expecting 200 OK on success, no JSON body needed
    #         self._request("DELETE", endpoint)
    #         logger.info(f"Successfully deleted workflow ID: {workflow_id}")
    #     except AlteryxAPIError as e:
    #         if e.status_code == 404:
    #             raise WorkflowNotFoundError(
    #                 workflow_id, message=f"Failed to delete: Workflow ID '{workflow_id}' not found."
    #             ) from e
    #         logger.error(f"Failed to delete workflow ID {workflow_id}: {e}")
    #         raise e  # Re-raise other API errors

    # # --- Job Management ---

    # def queue_job(
    #     self, workflow_id: str, questions: Optional[List[Dict[str, Any]]] = None, priority: Optional[str] = None
    # ) -> Dict[str, Any]:
    #     """
    #     Queues a job to run a specific workflow (V1 API).

    #     Args:
    #         workflow_id (str): The ID of the workflow to run.
    #         questions (Optional[List[Dict[str, Any]]]): A list of dictionaries representing answers
    #                                                    to Analytic App questions, if applicable.
    #                                                    Each dict should have 'name' and 'value' keys.
    #                                                    Example: `[{"name": "Input File", "value": "data.csv"}]`
    #         priority (Optional[str]): The priority level for the job (e.g., 'Low', 'Medium', 'High', 'Critical').
    #                                   Server defaults if not provided.

    #     Returns:
    #         Dict[str, Any]: A dictionary containing details of the queued job,
    #                         including the new job ID.

    #     Raises:
    #         WorkflowNotFoundError: If the workflow with the given ID is not found.
    #         JobExecutionError: If there's an error queuing the job (e.g., bad questions,
    #                            permissions).
    #         AuthenticationError: If authentication fails.
    #         AlteryxAPIError: For other API request errors.
    #     """
    #     logger.info(f"Queuing job for workflow ID: {workflow_id}")
    #     endpoint = f"workflows/{workflow_id}/jobs/"
    #     payload: Dict[str, Any] = {}
    #     if questions:
    #         payload["questions"] = questions
    #     if priority:
    #         payload["priority"] = priority

    #     try:
    #         # Jobs endpoint expects JSON payload
    #         response = self._request("POST", endpoint, json_data=payload if payload else None)
    #         job_details = response.json()
    #         logger.info(f"Successfully queued job for workflow {workflow_id}. Job ID: {job_details.get('id')}")
    #         return job_details
    #     except AlteryxAPIError as e:
    #         if e.status_code == 404:
    #             raise WorkflowNotFoundError(
    #                 workflow_id, message=f"Failed to queue job: Workflow ID '{workflow_id}' not found."
    #             ) from e
    #         # Use JobExecutionError for other failures related to queuing
    #         logger.error(f"Failed to queue job for workflow {workflow_id}: {e}")
    #         raise JobExecutionError(
    #             f"Failed to queue job for workflow {workflow_id}: {e}",
    #             status_code=e.status_code,
    #             response_text=e.response_text,
    #         ) from e

    # def get_job_status(self, job_id: str) -> Dict[str, Any]:
    #     """
    #     Retrieves the status and details of a specific job (V1 API).

    #     Args:
    #         job_id (str): The ID of the job.

    #     Returns:
    #         Dict[str, Any]: A dictionary containing job details, including its 'status'
    #                         (e.g., 'Queued', 'Running', 'Complete', 'Error').

    #     Raises:
    #         JobExecutionError: If the job with the given ID is not found (returns 404).
    #         AuthenticationError: If authentication fails.
    #         AlteryxAPIError: For other API request errors.
    #     """
    #     logger.info(f"Fetching status for job ID: {job_id}")
    #     endpoint = f"jobs/{job_id}/"
    #     try:
    #         response = self._request("GET", endpoint)
    #         status = response.json()
    #         logger.info(f"Retrieved status for job ID {job_id}: {status.get('status')}")
    #         return status
    #     except AlteryxAPIError as e:
    #         if e.status_code == 404:
    #             logger.warning(f"Job ID '{job_id}' not found.")
    #             raise JobExecutionError(f"Job ID '{job_id}' not found.", job_id=job_id, status_code=404) from e
    #         logger.error(f"Failed to get status for job ID {job_id}: {e}")
    #         raise e  # Re-raise other errors

    # def get_job_output(self, job_id: str, output_id: str) -> requests.Response:
    #     """
    #     Retrieves a specific output file from a completed job (V1 API).

    #     Note: This returns the raw requests.Response object, allowing the caller
    #           to handle the potentially large output data (stream, save to file, etc.).
    #           Access the content via `response.content` or `response.iter_content()`.

    #     Args:
    #         job_id (str): The ID of the job.
    #         output_id (str): The ID of the specific output anchor/file desired.
    #                          You can find output IDs in the results from `get_job_status`
    #                          for a completed job.

    #     Returns:
    #         requests.Response: The raw response object containing the output file data.

    #     Raises:
    #         JobExecutionError: If the job or output ID is not found (returns 404).
    #         AuthenticationError: If authentication fails.
    #         AlteryxAPIError: For other API request errors.
    #     """
    #     logger.info(f"Fetching output ID '{output_id}' for job ID: {job_id}")
    #     endpoint = f"jobs/{job_id}/output/{output_id}/"
    #     try:
    #         # Stream might be useful here for large outputs, but let caller handle for now
    #         response = self._request("GET", endpoint, stream=True)
    #         logger.info(f"Successfully retrieved stream for output {output_id} of job {job_id}.")
    #         return response
    #     except AlteryxAPIError as e:
    #         if e.status_code == 404:
    #             logger.warning(f"Job ID '{job_id}' or Output ID '{output_id}' not found.")
    #             raise JobExecutionError(
    #                 f"Job ID '{job_id}' or Output ID '{output_id}' not found.", job_id=job_id, status_code=404
    #             ) from e
    #         logger.error(f"Failed to get output {output_id} for job ID {job_id}: {e}")
    #         raise e  # Re-raise other errors
