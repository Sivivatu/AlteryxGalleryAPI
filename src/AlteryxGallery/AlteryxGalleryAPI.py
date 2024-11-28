import logging
import logging.config
import time
from math import log
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import requests

# Set up logging
# Set the logging format
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s")

# Create logger instance
logging.config.fileConfig("logging.conf")
# logging.basicConfig(level=logging.INFO)  # Adjust the log level as needed
logger = logging.getLogger(__name__)


class GalleryClient:
    def __init__(self, host_url: str, client_id: str, client_secret: str):
        self.host_url = host_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None
        self.token_expiry = None
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def authenticate(self) -> bool:
        logger.info("Authenticating user...")
        auth_response = requests.request(
            "POST",
            f"{self.host_url}/oauth2/token",
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials",
            },
        )
        if auth_response.status_code == 200:
            auth_data = auth_response.json()
            self.token = auth_data.get("access_token")
            logger.debug(f"Token received at: {time.time()}")
            self.token_expiry = time.time() + auth_data.get("expires_in")
            logger.info("Authentication successful.")
            self.headers["Authorization"] = f"Bearer {self.token}"
            return True
        else:
            logger.error("Authentication failed.")
            return False

    def _ensure_authenticated(self) -> None:
        if self.token is None or (self.token_expiry is not None and time.time() > self.token_expiry - 60):
            logger.info("Token is expired or about to expire. Renewing token...")
            self.authenticate()

    def _get(
        self, api_version: str, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Tuple[requests.Response, Dict[str, Any]]:
        """
        Example usage of _get method:
        def get_data(self) -> dict:
            return self._get("data")
        """
        self._ensure_authenticated()
        params = params or {}  # Ensure params is a dictionary
        api_version = api_version.strip("/")  # Remove leading slash if present
        endpoint = endpoint.strip("/")  # Remove leading slash if present
        logger.info(f"Making GET request to endpoint: {endpoint}")
        response = requests.get(
            f"{self.host_url}/{api_version}/{endpoint}",
            headers=self.headers,
            params=params,
        )
        response.raise_for_status()
        logger.debug("GET request successful.")
        return response, response.json()

    def _post(
        self,
        api_version: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Tuple[requests.Response, Dict[str, Any]]:
        """_summary_

        Args:
            api_version (str): _description_
            endpoint (str): _description_
            params (Optional[Dict[str, Any]], optional): _description_. Defaults to None.

        Returns:
            Tuple[requests.Response, Dict[str, Any]]: _description_
        """
        self._ensure_authenticated()
        params = params or {}  # Ensure params is a dictionary
        api_version = api_version.strip("/")  # Remove leading slash if present
        endpoint = endpoint.strip("/")  # Remove leading slash if present
        logger.info(f"Making POST request to endpoint: {endpoint}")
        # if headers:
        #     headers["Authorization"] = f"Bearer {self.token}"
        # else:
        headers = self.headers

        # remove the content type header as it is not needed for file uploads
        headers.pop("Content-Type", None)
        logger.debug(f"Content-Type header removed. Headers left: {headers.keys()}")

        response = requests.post(
            f"{self.host_url}/{api_version}/{endpoint}",
            headers=headers,
            params=params,
            **kwargs,
        )
        logger.debug(f"POST request completed. Response: {response.content}")
        response.raise_for_status()
        # logger.debug("GET request successful.")
        return response, response.json()

    def _prepare_workflow_data(
        self,
        file_path: Path,
        name: str,
        owner_id: str,
        others_may_download: bool,
        others_can_execute: bool,
        execution_mode: str,
        workflow_credential_type: str,
        **kwargs,
    ) -> Dict[str, Any]:
        file_path = Path(file_path)
        logger.debug(f"File Name: {file_path.name}")
        if file_path.suffix.lower() != ".yxzp":
            raise ValueError("File extension must be '.yxzp'")

        # Check if the execution mode is one of the valid modes
        valid_modes = ["Safe", "Semisafe", "Standard"]
        if execution_mode not in valid_modes:
            raise ValueError("execution_mode must be one of: 'Safe', 'Semisafe', 'Standard'")
        # Check if the workflow_credential_type mode is one of the valid modes
        valid_credential_types = ["Default", "Required", "Specific"]
        if workflow_credential_type not in valid_credential_types:
            raise ValueError("workflow_credential_type must be one of: 'Default', 'Required', 'Specific'")

        logger.debug(f"Preparing workflow data for file: {file_path.name}")
        data = {
            "name": name,
            "ownerId": owner_id,
            "othersMayDownload": others_may_download,
            "othersCanExecute": others_can_execute,
            "executionMode": execution_mode,
            "workflowCredentialType": workflow_credential_type,
        }

        # Add keyword arguments to the data dictionary
        data.update(kwargs)
        return data

    def _check_workflow_id(
        self, workflow_name: str | None, workflow_id: str | None
    ) -> Tuple[requests.Response, Dict[str, Any]]:
        if workflow_id is None and workflow_name is None:
            raise ValueError("Either workflow_id or workflow_name must be provided.")
        if workflow_id:
            response, content = self.get_workflows(
                workflow_id=workflow_id
            )  # FIXME: what if the workflow_id is provided but not found? - throws error?
            logger.debug(f"Number of workflows: {len(content)}")
            logger.debug(f"Workflow Name: {content['name']}")
            logger.debug(f"Workflow ID: {workflow_id}")
            return response, content
        if workflow_name:
            response, content = self.get_workflows(name=workflow_name)
            return response, content
        raise ValueError("Neither workflow_id or workflow_name were found.")

    # def close(self) -> None:
    #     self.http_client.close()

    # def __enter__(self):
    #     return self

    # def __exit__(self, exc_type, exc_value, traceback):
    #     self.close()

    # Workflow Interaction Methods
    def get_workflows(self, **kwargs) -> Tuple[requests.Response, Dict[str, Any]]:
        logger.info("Getting all workflows...")
        return self._get("v3", "workflows", params=kwargs)

    def post_publish_workflow(
        self,
        file_path: Path,
        name: str,
        owner_id: str,
        is_public: bool = False,
        is_ready_for_migration: bool = False,
        others_may_download: bool = True,
        others_can_execute: bool = True,
        execution_mode: str = "Standard",
        workflow_credential_type: str = "Default",
        **kwargs,
    ) -> Tuple[requests.Response, Dict[str, Any]]:
        """
        Publishes a new workflow to the Alteryx Gallery. Currently only supports .yxzp files.
        All keyword additional arguments must be passed individually as they appear in the API documentation.

        """
        api_version = "v3"
        endpoint = "workflows"

        data = self._prepare_workflow_data(
            file_path=file_path,
            name=name,
            owner_id=owner_id,
            others_may_download=others_may_download,
            others_can_execute=others_can_execute,
            execution_mode=execution_mode,
            workflow_credential_type=workflow_credential_type,
            isReadyForMigration=is_ready_for_migration,
            isPublic=is_public,
            **kwargs,
        )

        logger.info("Publishing new workflow...")
        with open(file_path, "rb") as file:
            logger.debug(f"Reading file: {file_path}")
            logger.debug(f"File name: {file.name}")
            files = {
                "file": (
                    file_path.name,
                    file,
                    "application/octet-stream",
                )
            }

            response = self._post(
                api_version=api_version,
                endpoint=endpoint,
                data=data,
                files=files,
            )
            logger.debug("Workflow published successfully.")
            return response

    # TODO: Implement the update post workflow method.
    # this requires extracting the data and file sections for the post request to be extracted into separate methods
    # Check https://chatgpt.com/share/7aeb8931-d627-4561-bcfb-4cc8a0e0825f for example of how to extend the existing post workflow method by extracting common processes

    def post_publish_workflow_version(
        self,
        workflow_id: str,
        file_path: Path,
        name: str,
        owner_id: str,
        others_may_download: bool = True,
        others_can_execute: bool = True,
        execution_mode: str = "Standard",
        workflow_credential_type: str = "Default",
        make_published: bool = True,
        **kwargs,
    ) -> Tuple[requests.Response, Dict[str, Any]]:
        """
        Updates a workflow version to the Alteryx Gallery. Currently only supports .yxzp files.
        All keyword additional arguments must be passed individually as they appear in the API documentation.
        """
        # Check if the workflow_id is a valid workflow id from the Alteryx Gallery
        # if not search for workflow_id by name
        # if not found, raise an error
        self._check_workflow_id(workflow_id=workflow_id, workflow_name=name)

        api_version = "v3"
        endpoint = f"workflows/{workflow_id}/versions"

        data = self._prepare_workflow_data(
            file_path=file_path,
            name=name,
            owner_id=owner_id,
            others_may_download=others_may_download,
            others_can_execute=others_can_execute,
            execution_mode=execution_mode,
            workflow_credential_type=workflow_credential_type,
            makePublished=make_published,
            **kwargs,
        )

        logger.info("updating workflow: {name} workflow with new version...")
        with open(file_path, "rb") as file:
            logger.debug(f"Reading file: {file_path}")
            logger.debug(f"File name: {file.name}")
            files = {
                "file": (
                    file_path.name,
                    file,
                    "application/octet-stream",
                )
            }

            response = self._post(
                api_version=api_version,
                endpoint=endpoint,
                data=data,
                files=files,
            )
            logger.debug("Workflow published successfully.")
            return response


# # Example usage:


# with AlteryxGalleryClient("https://your-alteryx-server/api/v3") as client:
#     if client.authenticate("your_username", "your_password"):
#         logger.info("Authentication successful!")
#         print(client.get_data())
#     else:
#         logger.error("Authentication failed!")


# TODO: Implement the following methods following the requirements of the Alteryx Gallery API
# def subscription(self):
#     """
#     :return: workflows in a subscription
#     """
#     method = 'GET'
#     url = self.api_location + '/workflows/subscription/'
#     params = self.build_oauth_params()
#     signature = self.generate_signature(method, url, params)
#     params.update({'oauth_signature': signature})
#     output = requests.get(url, params=params)
#     output, output_content = output, json.loads(output.content.decode("utf8"))
#     return output, output_content

# def questions(self, app_id):
#     """
#     :return: Returns the questions for the given Alteryx Analytics App
#     """
#     method = 'GET'
#     url = self.api_location + '/workflows/' + app_id + '/questions/'
#     params = self.build_oauth_params()
#     signature = self.generate_signature(method, url, params)
#     params.update({'oauth_signature': signature})
#     output = requests.get(url, params=params)
#     output, output_content = output, json.loads(output.content.decode("utf8"))
#     return output, output_content

# def execute_workflow(self, app_id, **kwargs):
#     """
#     Queue an app execution job.
#     :return:  Returns ID of the job
#     """
#     method = 'POST'
#     url = self.api_location + '/workflows/' + app_id + '/jobs/'
#     params = self.build_oauth_params()
#     signature = self.generate_signature(method, url, params)
#     params.update({'oauth_signature': signature})

#     if 'payload' in kwargs:
#         output = requests.post(url,
#                                json=kwargs['payload'],
#                                headers={'Content-Type': 'application/json'},
#                                params=params)
#     else:
#         output = requests.post(url, params=params)

#     output, output_content = output, json.loads(output.content.decode("utf8"))
#     return output, output_content

# def get_jobs(self, app_id):
#     """
#     :return: Returns the jobs for the given Alteryx Analytics App
#     """
#     method = 'GET'
#     url = self.api_location + '/workflows/' + app_id + '/jobs/'
#     params = self.build_oauth_params()
#     signature = self.generate_signature(method, url, params)
#     params.update({'oauth_signature': signature})
#     output = requests.get(url, params=params)
#     output, output_content = output, json.loads(output.content.decode("utf8"))
#     return output, output_content

# def get_job_status(self, job_id):
#     """
#     :return: Retrieves the job and its current state
#     """
#     method = 'GET'
#     url = self.api_location + '/jobs/' + job_id + '/'
#     params = self.build_oauth_params()
#     signature = self.generate_signature(method, url, params)
#     params.update({'oauth_signature': signature})
#     output = requests.get(url, params=params)
#     output, output_content = output, json.loads(output.content.decode("utf8"))
#     return output, output_content

# def get_job_output(self, job_id, output_id):
#     """
#     :return: Returns the output for a given job (FileURL)
#     """
#     method = 'GET'
#     url = self.api_location + '/jobs/' + job_id + '/output/' + output_id + '/'
#     params = self.build_oauth_params()
#     signature = self.generate_signature(method, url, params)
#     params.update({'oauth_signature': signature})
#     output = requests.get(url, params=params)
#     output, output_content = output, output.content.decode("utf8")
#     return output, output_content

# def get_app(self, app_id, app_name):
#         """
#         Retrieves the requested App from the Alteryx Gallery API and saves it to disk.

#         :param app_id: The ID of the App to retrieve.
#         :param app_name: The name of the App to save the file as.
#         :return: The file path where the App is saved.
#         """
#         method = 'GET'
#         url = self.api_location + '/admin/v1/' + app_id + '/package/'
#         params = self.build_oauth_params()
#         signature = self.generate_signature(method, url, params)
#         params.update({'oauth_signature': signature})
#         output = requests.get(url, params=params)
#         output_content = output.content

#         # Define the path and file name for the downloaded file
#         # Save it in the 'workflow' directory
#         file_path = f"{app_name}.yxzp"

#         # Write the content to a file
#         with open(file_path, 'wb') as file:
#             file.write(output_content)

#         # Optionally return the file_path if needed
#         return file_path
