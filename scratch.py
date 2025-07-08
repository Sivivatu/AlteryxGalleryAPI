import logging
import logging.config
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import requests
from dotenv import load_dotenv

# import requests
from src.archive_AlteryxGallery import AlteryxGalleryAPI

load_dotenv()

host_url: str = os.getenv("HOST_URL", "NoValueFound")

client_id: str = os.getenv("CLIENT_ID", "NoValueFound")
client_secret: str = os.getenv("CLIENT_SECRET", "NoValueFound")
owner_id: str = os.getenv("TEST_OWNER_ID", "NoValueFound")
file_path = Path("tests/Test_Upload.yxzp")
# payload = {"client_id": client_id, "client_secret": client_secret, "grant_type": "client_credentials"}

# response = httpx.post(token_url, data=payload)

# print(response.url)
# print(response.status_code)
# print(response.text)


# with AlteryxGalleryAPI.GalleryClient(host_url=host_url) as client:
#     client.authenticate(client_id, client_secret)
# response, content = client.get_all_workflows(name="00-Octopus Download Pipeline")
# print(f"workflow query status response: {response.status_code}")
# print(f"workflow query content: {content}")
# response, content = client.post_publish_workflow(file_path, "Test_Upload", owner_id)
# print(f"workflow publish query status response: {response.status_code}")
# print(f"workflow publish query content: {content}")


client = AlteryxGalleryAPI.GalleryClient(host_url=host_url, client_id=client_id, client_secret=client_secret)
print(client)

# response = requests.request("GET", url, headers=headers, data=payload)

# print(response.text)


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
        is_public: bool,
        others_may_download: bool,
        others_can_execute: bool,
        execution_mode: str,
        workflow_credential_type: str,
        **kwargs,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
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
            "isPublic": is_public,
            "othersMayDownload": others_may_download,
            "othersCanExecute": others_can_execute,
            "executionMode": execution_mode,
            "workflowCredentialType": workflow_credential_type,
        }

        # Add keyword arguments to the data dictionary
        data.update(kwargs)

        logger.debug(f"opening file: {file_path}")
        with open(file_path, "rb") as file:  # type: ignore
            files = {
                "file": (
                    file_path.name,
                    file,
                    "application/octet-stream",
                )
            }

        return data, files

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

        """
        api_version = "v3"
        endpoint = "workflows"

        data = self._prepare_workflow_data(
            file_path=file_path,
            name=name,
            owner_id=owner_id,
            is_public=is_public,
            others_may_download=others_may_download,
            others_can_execute=others_can_execute,
            execution_mode=execution_mode,
            workflow_credential_type=workflow_credential_type,
            isReadyForMigration=is_ready_for_migration,
            **kwargs,
        )

        logger.debug(f"opening file: {file_path}")
        with open(file_path, "rb") as file:  # type: ignore
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
