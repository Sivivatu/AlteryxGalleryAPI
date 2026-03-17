"""
Workflow resource for API operations.
"""

import logging
from typing import List, Optional

from ..exceptions import WorkflowNotFoundError
from ..models import (
    Workflow,
    WorkflowId,
    WorkflowQuestion,
    WorkflowUpdateRequest,
    WorkflowUploadRequest,
    WorkflowVersion,
)
from ..utils import open_file_for_upload, validate_file_size
from ._base import _BaseResource

logger = logging.getLogger(__name__)


class WorkflowResource(_BaseResource):
    """Resource for workflow operations.

    Provides methods for managing workflows:
        - List workflows
        - Get workflow details
        - Publish new workflows
        - Update workflows
        - Delete workflows
        - Download workflow packages
        - Get workflow questions
        - Manage workflow versions
    """

    def list(
        self,
        name: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> List[Workflow]:
        """List all workflows.

        Args:
            name: Filter by workflow name
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            List of Workflow objects
        """
        params = {}
        if name:
            params["name"] = name
        if page:
            params["page"] = page
        if page_size:
            params["pageSize"] = page_size

        logger.debug(f"Listing workflows with params: {params}")

        response = self._client._request(
            "GET",
            "workflows/",
            params=params,
        )

        if isinstance(response, list):
            return [Workflow.model_validate(item) for item in response]
        elif isinstance(response, dict) and "workflows" in response:
            return [Workflow.model_validate(item) for item in response["workflows"]]
        elif isinstance(response, dict):
            return [Workflow.model_validate(response)]

        return []

    def get(self, workflow_id: WorkflowId) -> Workflow:
        """Get workflow details by ID.

        Args:
            workflow_id: Workflow identifier

        Returns:
            Workflow: Workflow details

        Raises:
            WorkflowNotFoundError: If workflow not found
        """
        logger.debug(f"Getting workflow: {workflow_id}")

        try:
            response = self._client._request(
                "GET",
                f"workflows/{workflow_id}",
            )
            return Workflow.model_validate(response)
        except Exception as e:
            if "not found" in str(e).lower() or "404" in str(e):
                raise WorkflowNotFoundError(workflow_id)
            raise

    def publish(
        self,
        file_path: str,
        name: str,
        owner_id: str,
        is_public: bool = False,
        execution_mode: str = "Safe",
        worker_tag: Optional[str] = None,
        comments: Optional[str] = None,
        can_download: Optional[bool] = None,
    ) -> Workflow:
        """Publish a new workflow.

        Args:
            file_path: Path to .yxzp or .yxmd file
            name: Workflow name
            owner_id: Owner user ID
            is_public: Public visibility flag
            execution_mode: Execution mode (Safe/SemiSafe/Unrestricted)
            worker_tag: Worker assignment tag
            comments: Version comments
            can_download: Allow download permission

        Returns:
            Workflow: Published workflow details
        """
        validate_file_size(file_path)

        filename, file_object, _ = open_file_for_upload(file_path)

        logger.info(f"Publishing workflow '{name}' from {file_path}")

        request = WorkflowUploadRequest(
            name=name,
            owner_id=owner_id,
            is_public=is_public,
            execution_mode=execution_mode,
            worker_tag=worker_tag,
            comments=comments,
            can_download=can_download,
        )

        data = request.model_dump(by_alias=True, exclude_none=True)
        data["makePublic"] = str(is_public).lower()

        files = {
            "file": (filename, file_object),
        }

        response = self._client._request(
            "POST",
            "workflows/",
            data=data,
            files=files,
        )

        logger.info(f"Successfully published workflow '{name}'")
        return Workflow.model_validate(response)

    def update(
        self,
        workflow_id: WorkflowId,
        file_path: str,
        name: Optional[str] = None,
        is_public: Optional[bool] = None,
        execution_mode: Optional[str] = None,
        worker_tag: Optional[str] = None,
        comments: Optional[str] = None,
        can_download: Optional[bool] = None,
    ) -> Workflow:
        """Update an existing workflow.

        Args:
            workflow_id: Workflow identifier
            file_path: Path to new .yxzp or .yxmd file
            name: New workflow name
            is_public: Update public visibility
            execution_mode: Update execution mode
            worker_tag: Update worker assignment tag
            comments: Update comments
            can_download: Update download permission

        Returns:
            Workflow: Updated workflow details

        Raises:
            WorkflowNotFoundError: If workflow not found
        """
        validate_file_size(file_path)

        # Verify workflow exists first
        try:
            self.get(workflow_id)
        except WorkflowNotFoundError:
            raise WorkflowNotFoundError(workflow_id)

        filename, file_object, _ = open_file_for_upload(file_path)

        logger.info(f"Updating workflow '{workflow_id}' from {file_path}")

        request = WorkflowUpdateRequest(
            name=name,
            is_public=is_public,
            execution_mode=execution_mode,
            worker_tag=worker_tag,
            comments=comments,
            can_download=can_download,
        )

        data = request.model_dump(by_alias=True, exclude_none=True)

        files = {
            "file": (filename, file_object),
        }

        response = self._client._request(
            "PUT",
            f"workflows/{workflow_id}",
            data=data,
            files=files,
        )

        logger.info(f"Successfully updated workflow '{workflow_id}'")
        return Workflow.model_validate(response)

    def delete(self, workflow_id: WorkflowId) -> None:
        """Delete a workflow.

        Args:
            workflow_id: Workflow identifier

        Raises:
            WorkflowNotFoundError: If workflow not found
        """
        logger.info(f"Deleting workflow '{workflow_id}'")

        try:
            self._client._request(
                "DELETE",
                f"workflows/{workflow_id}",
            )
            logger.info(f"Successfully deleted workflow '{workflow_id}'")
        except Exception as e:
            if "not found" in str(e).lower() or "404" in str(e):
                raise WorkflowNotFoundError(workflow_id)
            raise

    def download(self, workflow_id: WorkflowId) -> bytes:
        """Download workflow package.

        Args:
            workflow_id: Workflow identifier

        Returns:
            bytes: Workflow package content

        Raises:
            WorkflowNotFoundError: If workflow not found
        """
        logger.debug(f"Downloading workflow '{workflow_id}'")

        response = self._client._request(
            "GET",
            f"workflows/{workflow_id}/package",
        )

        # The raw response should contain file content
        if hasattr(response, "content"):
            return response.content
        elif isinstance(response, bytes):
            return response
        elif isinstance(response, str):
            return response.encode()

        return response.encode() if isinstance(response, str) else response

    def get_questions(self, workflow_id: WorkflowId) -> List[WorkflowQuestion]:
        """Get questions from an analytic app workflow.

        Args:
            workflow_id: Workflow identifier

        Returns:
            List of WorkflowQuestion objects

        Raises:
            WorkflowNotFoundError: If workflow not found
        """
        logger.debug(f"Getting questions for workflow: {workflow_id}")

        try:
            response = self._client._request(
                "GET",
                f"workflows/{workflow_id}/questions",
            )

            if isinstance(response, list):
                return [WorkflowQuestion.model_validate(q) for q in response]
            elif isinstance(response, dict) and "questions" in response:
                return [WorkflowQuestion.model_validate(q) for q in response["questions"]]

            return []
        except Exception as e:
            if "not found" in str(e).lower() or "404" in str(e):
                raise WorkflowNotFoundError(workflow_id)
            raise

    def publish_version(
        self,
        workflow_id: WorkflowId,
        file_path: str,
        comments: Optional[str] = None,
    ) -> WorkflowVersion:
        """Publish a new version of a workflow.

        Args:
            workflow_id: Existing workflow ID
            file_path: Path to new .yxzp or .yxmd file
            comments: Version comments

        Returns:
            WorkflowVersion: New version details

        Raises:
            WorkflowNotFoundError: If workflow not found
        """
        validate_file_size(file_path)

        filename, file_object, _ = open_file_for_upload(file_path)

        logger.info(f"Publishing version for workflow '{workflow_id}' from {file_path}")

        data = {}
        if comments:
            data["comments"] = comments

        files = {
            "file": (filename, file_object),
        }

        response = self._client._request(
            "POST",
            f"workflows/{workflow_id}/versions",
            data=data,
            files=files,
        )

        logger.info(f"Successfully published version for workflow '{workflow_id}'")
        return WorkflowVersion.model_validate(response)

    def list_versions(self, workflow_id: WorkflowId) -> List[WorkflowVersion]:
        """List all versions of a workflow.

        Args:
            workflow_id: Workflow identifier

        Returns:
            List of WorkflowVersion objects

        Raises:
            WorkflowNotFoundError: If workflow not found
        """
        logger.debug(f"Listing versions for workflow: {workflow_id}")

        try:
            response = self._client._request(
                "GET",
                f"workflows/{workflow_id}/versions",
            )

            if isinstance(response, list):
                return [WorkflowVersion.model_validate(v) for v in response]
            elif isinstance(response, dict) and "versions" in response:
                return [WorkflowVersion.model_validate(v) for v in response["versions"]]

            return []
        except Exception as e:
            if "not found" in str(e).lower() or "404" in str(e):
                raise WorkflowNotFoundError(workflow_id)
            raise
