import logging
import logging.config
import time
from email import header
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import requests

# Set up logging
# Set the logging format
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s"
)

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
        if self.token is None or (
            self.token_expiry is not None and time.time() > self.token_expiry - 60
        ):
            logger.info("Token is expired or about to expire. Renewing token...")
            self.authenticate()

    # TODO: Not needed below as will explicity call the authenticate method which sets headers
    # def _update_auth_header(self) -> Dict[str, Any]:
    #     self._ensure_authenticated()
    #     self.headers["Authorization"] =  f"Bearer {self.token}"
    #     logger.debug("Authorization header updated with the token.")
    #     return self.headers

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
            f"{self.host_url}/{api_version}/{endpoint}", params=params
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
        response = requests.post(
            f"{self.host_url}/{api_version}/{endpoint}", params=params, **kwargs
        )
        response.raise_for_status()
        logger.debug("GET request successful.")
        return response, response.json()

    # def close(self) -> None:
    #     self.http_client.close()

    # def __enter__(self):
    #     return self

    # def __exit__(self, exc_type, exc_value, traceback):
    #     self.close()

    # Workflow Interaction Methods
    def get_all_workflows(self, **kwargs) -> Tuple[requests.Response, Dict[str, Any]]:
        logger.info("Getting all workflows...")
        return self._get("v3", "workflows", params=kwargs)

    # def post_publish_workflow(
    #     self,
    #     file_path: Path,
    #     name: str,
    #     owner_id: str,
    #     is_public: bool = False,
    #     is_ready_for_migration: bool = False,
    #     others_may_download: bool = True,
    #     others_can_execute: bool = True,
    #     execution_mode: str = "Standard",
    #     workflow_credential_type: str = "Default",
    #     **kwargs,
    # ) -> Tuple[httpx.Response, Dict[str, Any]]:
    #     file_path = Path(file_path)
    #     if file_path.suffix.lower() != ".yxzp":
    #         raise ValueError("File extension must be '.yxzp'")

    #     # Check if the execution mode is one of the valid modes
    #     valid_modes = ["Safe", "Semisafe", "Standard"]
    #     if execution_mode not in valid_modes:
    #         raise ValueError(
    #             "execution_mode must be one of: 'Safe', 'Semisafe', 'Standard'"
    #         )
    #     del valid_modes
    #     # Check if the workflow_credential_type mode is one of the valid modes
    #     valid_credential_types = ["Default", "Required", "Specific"]
    #     if workflow_credential_type not in valid_credential_types:
    #         raise ValueError(
    #             "workflow_credential_type must be one of: 'Default', 'Required', 'Specific'"
    #         )
    #     del valid_credential_types

    #     data = {
    #         "name": name,
    #         "ownerId": owner_id,
    #         "isPublic": is_public,
    #         "isReadyForMigration": is_ready_for_migration,
    #         "othersMayDownload": others_may_download,
    #         "othersCanExecute": others_can_execute,
    #         "executionMode": execution_mode,
    #         "workflowCredentialType": workflow_credential_type,
    #     }

    #     # Add keyword arguments to the data dictionary
    #     for key, value in kwargs.items():
    #         data[key] = value

    #     # Update the authorization header
    #     self._update_auth_header()
    #     # Make the POST request
    #     logger.info("Publishing new workflow...")
    #     with open(file_path, "rb") as file:
    #         files = {"file": (file.name, file, "application/yxzp")}
    #         headers = {
    #             **self.http_client.headers,
    #             "Content-Type": "application/x-www-form-urlencoded",  # "multipart/form-data",
    #         }
    #         headers["Accept"] = "application/json"
    #         # headers["Accept-Encoding"] = "gzip, deflate, br, zstd"

    #         # TODO: Move the post method to _post method in same mananer as _get
    #         # from urllib.parse import urlencode

    #         # data["file"] = file

    #         response = self._post(
    #             "v3/workflows",
    #             data=data,
    #             files=files,
    #             # content=content_file,
    #             headers=headers,
    #         )
    #         logger.debug("Workflow published successfully.")
    #         return response

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
