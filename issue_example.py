from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import httpx


def _post(
    self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs
) -> Tuple[httpx.Response, Dict[str, Any]]:
    self._update_auth_header()
    params = params or {}  # Ensure params is a dictionary
    endpoint = endpoint.lstrip("/")  # Remove leading slash if present
    response = self.http_client.post(
        f"{self.host_url}/{endpoint}", params=params, **kwargs
    )
    response.raise_for_status()
    return response, response.json()


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
) -> Tuple[httpx.Response, Dict[str, Any]]:
    file_path = Path(file_path)

    ## Removed Validation Code for brevity

    data = {
        "name": name,
        "ownerId": owner_id,
        "isPublic": is_public,
        "isReadyForMigration": is_ready_for_migration,
        "othersMayDownload": others_may_download,
        "othersCanExecute": others_can_execute,
        "executionMode": execution_mode,
        "workflowCredentialType": workflow_credential_type,
    }

    # Add keyword arguments to the data dictionary
    for key, value in kwargs.items():
        data[key] = value

    # Update the authorization header
    self._update_auth_header()
    # Make the POST request
    with open(file_path, "rb") as file:
        # content_file = file
        files = {"file": (file.name, file, "application/yxzp")}
        headers = {
            **self.http_client.headers,
            "Content-Type": "application/x-www-form-urlencoded",  # "multipart/form-data",
        }
        headers["Accept"] = "application/json"

        response = self._post(
            "v3/workflows",
            data=data,
            files=files,
            headers=headers,
        )
        return response
