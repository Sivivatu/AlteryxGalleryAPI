"""
Job resource for API operations.
"""

import logging
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime

from ..models import (
    JobId,
    Job,
    JobStatus,
    JobRunRequest,
)
from ..exceptions import JobNotFoundError, JobExecutionError, NotFoundError
from ._base import _BaseResource

logger = logging.getLogger(__name__)


class JobResource(_BaseResource):
    """Resource for job operations.

    Provides methods for managing workflow executions:
        - Run workflows as jobs
        - Get job status and details
        - List jobs with filters
        - Download job outputs
        - Get job execution messages
        - Cancel jobs
        - Wait for job completion
    """

    def run(
        self,
        workflow_id: str,
        questions: Optional[Dict[str, Any]] = None,
        priority: str = "Default",
        worker_tag: Optional[str] = None,
    ) -> Job:
        """Queue a workflow job to run.

        Args:
            workflow_id: Parent workflow ID
            questions: Answers to analytic app questions (name -> value mapping)
            priority: Job execution priority (Low/Default/Medium/High/Critical)
            worker_tag: Worker assignment tag

        Returns:
            Job: Queued job details

        Raises:
            NotFoundError: If workflow not found
            JobExecutionError: If job queueing fails
        """
        logger.info(f"Queuing job for workflow: {workflow_id}")

        request = JobRunRequest(
            questions=questions,
            priority=priority,
            worker_tag=worker_tag,
        )

        data = request.model_dump(by_alias=True, exclude_none=True)

        response = self._client._request(
            "POST",
            f"workflows/{workflow_id}/jobs",
            json_data=data,
        )

        job = Job.model_validate(response)
        logger.info(f"Job {job.id} queued for workflow {workflow_id}")
        return job

    def get(self, job_id: JobId) -> Job:
        """Get job details by ID.

        Args:
            job_id: Job identifier

        Returns:
            Job: Job details

        Raises:
            JobNotFoundError: If job not found
        """
        logger.debug(f"Getting job: {job_id}")

        try:
            response = self._client._request(
                "GET",
                f"jobs/{job_id}",
            )
            return Job.model_validate(response)
        except Exception as e:
            if "not found" in str(e).lower() or "404" in str(e):
                raise JobNotFoundError(job_id)
            raise

    def list(
        self,
        workflow_id: Optional[str] = None,
        status: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> List[Job]:
        """List jobs with optional filters.

        Args:
            workflow_id: Filter by workflow ID
            status: Filter by job status
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            List of Job objects
        """
        params = {}
        if workflow_id:
            params["workflowId"] = workflow_id
        if status:
            params["status"] = status
        if page:
            params["page"] = page
        if page_size:
            params["pageSize"] = page_size

        logger.debug(f"Listing jobs with params: {params}")

        response = self._client._request(
            "GET",
            "jobs/",
            params=params,
        )

        if isinstance(response, list):
            return [Job.model_validate(item) for item in response]
        elif isinstance(response, dict) and "jobs" in response:
            return [Job.model_validate(item) for item in response["jobs"]]
        elif isinstance(response, dict):
            return [Job.model_validate(response)]

        return []

    def get_output(self, job_id: JobId, output_id: str) -> bytes:
        """Download output file from a completed job.

        Args:
            job_id: Job identifier
            output_id: Output file identifier

        Returns:
            bytes: Output file content

        Raises:
            JobNotFoundError: If job or output not found
        """
        logger.debug(f"Downloading output {output_id} from job {job_id}")

        try:
            response = self._client._request(
                "GET",
                f"jobs/{job_id}/output/{output_id}",
            )

            # The raw response should contain file content
            if hasattr(response, "content"):
                return response.content
            elif isinstance(response, bytes):
                return response
            elif isinstance(response, str):
                return response.encode()

            return response.encode() if isinstance(response, str) else response
        except Exception as e:
            if "not found" in str(e).lower() or "404" in str(e):
                raise JobNotFoundError(job_id, message=f"Output '{output_id}' not found")
            raise

    def get_messages(self, job_id: JobId) -> List[Dict[str, Any]]:
        """Get execution messages from a job.

        Args:
            job_id: Job identifier

        Returns:
            List of message dictionaries

        Raises:
            JobNotFoundError: If job not found
        """
        logger.debug(f"Getting messages for job: {job_id}")

        try:
            response = self._client._request(
                "GET",
                f"jobs/{job_id}/messages",
            )

            if isinstance(response, list):
                return response
            elif isinstance(response, dict) and "messages" in response:
                return response["messages"]

            return []
        except Exception as e:
            if "not found" in str(e).lower() or "404" in str(e):
                raise JobNotFoundError(job_id)
            raise

    def cancel(self, job_id: JobId) -> None:
        """Cancel a running job.

        Args:
            job_id: Job identifier

        Raises:
            JobNotFoundError: If job not found
            JobExecutionError: If job cannot be cancelled
        """
        logger.info(f"Cancelling job: {job_id}")

        try:
            self._client._request(
                "DELETE",
                f"jobs/{job_id}",
            )
            logger.info(f"Successfully cancelled job: {job_id}")
        except Exception as e:
            if "not found" in str(e).lower() or "404" in str(e):
                raise JobNotFoundError(job_id)
            raise JobExecutionError(job_id, "Unknown", messages=[str(e)])

    def run_and_wait(
        self,
        workflow_id: str,
        questions: Optional[Dict[str, Any]] = None,
        priority: str = "Default",
        worker_tag: Optional[str] = None,
        timeout: int = 3600,
        poll_interval: int = 10,
    ) -> Job:
        """Run a workflow job and wait for completion.

        Args:
            workflow_id: Parent workflow ID
            questions: Answers to analytic app questions
            priority: Job execution priority
            worker_tag: Worker assignment tag
            timeout: Maximum wait time in seconds (default: 1 hour)
            poll_interval: Seconds between status checks (default: 10)

        Returns:
            Job: Completed job details

        Raises:
            TimeoutError: If job does not complete within timeout
            JobExecutionError: If job fails during execution
        """
        logger.info(f"Running job for workflow {workflow_id} and waiting for completion")

        # Queue the job
        job = self.run(
            workflow_id=workflow_id,
            questions=questions,
            priority=priority,
            worker_tag=worker_tag,
        )

        # Poll for completion
        start_time = datetime.now()
        elapsed = 0

        while job.status not in [JobStatus.COMPLETED, JobStatus.ERROR, JobStatus.CANCELLED]:
            if elapsed >= timeout:
                from ..exceptions import TimeoutError as JobTimeoutError

                raise JobTimeoutError(f"Job {job.id} did not complete within {timeout} seconds")

            # Wait before polling
            import time

            time.sleep(poll_interval)

            # Refresh job status
            try:
                job = self.get(job.id)
                elapsed = (datetime.now() - start_time).total_seconds()
                logger.debug(f"Job {job.id} status: {job.status} " f"({elapsed}s elapsed)")
            except Exception as e:
                logger.error(f"Error polling job status: {e}")
                raise

        # Check final status
        if job.status == JobStatus.ERROR:
            messages = job.messages or []
            error_details = [msg.message for msg in messages]
            raise JobExecutionError(
                job.id,
                job.status.value,
                error_details,
            )

        logger.info(f"Job {job.id} completed with status: {job.status}")
        return job


class AsyncJobResource(_BaseResource):
    """Asynchronous job resource.

    Provides async versions of all JobResource methods.
    """

    async def run(
        self,
        workflow_id: str,
        questions: Optional[Dict[str, Any]] = None,
        priority: str = "Default",
        worker_tag: Optional[str] = None,
    ) -> Job:
        """Queue a workflow job to run (async).

        Args:
            workflow_id: Parent workflow ID
            questions: Answers to analytic app questions
            priority: Job execution priority
            worker_tag: Worker assignment tag

        Returns:
            Job: Queued job details
        """
        logger.info(f"Queueing job for workflow: {workflow_id}")

        request = JobRunRequest(
            questions=questions,
            priority=priority,
            worker_tag=worker_tag,
        )

        data = request.model_dump(by_alias=True, exclude_none=True)

        response = await self._client._request(
            "POST",
            f"workflows/{workflow_id}/jobs",
            json_data=data,
        )

        job = Job.model_validate(response)
        logger.info(f"Job {job.id} queued for workflow {workflow_id}")
        return job

    async def get(self, job_id: JobId) -> Job:
        """Get job details by ID (async).

        Args:
            job_id: Job identifier

        Returns:
            Job: Job details
        """
        logger.debug(f"Getting job: {job_id}")

        try:
            response = await self._client._request(
                "GET",
                f"jobs/{job_id}",
            )
            return Job.model_validate(response)
        except Exception as e:
            if "not found" in str(e).lower() or "404" in str(e):
                raise JobNotFoundError(job_id)
            raise

    async def list(
        self,
        workflow_id: Optional[str] = None,
        status: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> List[Job]:
        """List jobs with optional filters (async).

        Args:
            workflow_id: Filter by workflow ID
            status: Filter by job status
            page: Page number
            page_size: Number of items per page

        Returns:
            List of Job objects
        """
        params = {}
        if workflow_id:
            params["workflowId"] = workflow_id
        if status:
            params["status"] = status
        if page:
            params["page"] = page
        if page_size:
            params["pageSize"] = page_size

        logger.debug(f"Listing jobs with params: {params}")

        response = await self._client._request(
            "GET",
            "jobs/",
            params=params,
        )

        if isinstance(response, list):
            return [Job.model_validate(item) for item in response]
        elif isinstance(response, dict) and "jobs" in response:
            return [Job.model_validate(item) for item in response["jobs"]]
        elif isinstance(response, dict):
            return [Job.model_validate(response)]

        return []

    async def get_output(self, job_id: JobId, output_id: str) -> bytes:
        """Download output file from a completed job (async).

        Args:
            job_id: Job identifier
            output_id: Output file identifier

        Returns:
            bytes: Output file content
        """
        logger.debug(f"Downloading output {output_id} from job {job_id}")

        try:
            response = await self._client._request(
                "GET",
                f"jobs/{job_id}/output/{output_id}",
            )

            if hasattr(response, "content"):
                return response.content
            elif isinstance(response, bytes):
                return response
            elif isinstance(response, str):
                return response.encode()

            return response.encode() if isinstance(response, str) else response
        except Exception as e:
            if "not found" in str(e).lower() or "404" in str(e):
                raise JobNotFoundError(job_id, message=f"Output '{output_id}' not found")
            raise

    async def get_messages(self, job_id: JobId) -> List[Dict[str, Any]]:
        """Get execution messages from a job (async).

        Args:
            job_id: Job identifier

        Returns:
            List of message dictionaries
        """
        logger.debug(f"Getting messages for job: {job_id}")

        try:
            response = await self._client._request(
                "GET",
                f"jobs/{job_id}/messages",
            )

            if isinstance(response, list):
                return response
            elif isinstance(response, dict) and "messages" in response:
                return response["messages"]

            return []
        except Exception as e:
            if "not found" in str(e).lower() or "404" in str(e):
                raise JobNotFoundError(job_id)
            raise

    async def cancel(self, job_id: JobId) -> None:
        """Cancel a running job (async).

        Args:
            job_id: Job identifier
        """
        logger.info(f"Cancelling job: {job_id}")

        try:
            await self._client._request(
                "DELETE",
                f"jobs/{job_id}",
            )
            logger.info(f"Successfully cancelled job: {job_id}")
        except NotFoundError:
            raise JobNotFoundError(job_id)
        except Exception as e:
            raise JobExecutionError(job_id, "Unknown", messages=[str(e)])

    async def run_and_wait(
        self,
        workflow_id: str,
        questions: Optional[Dict[str, Any]] = None,
        priority: str = "Default",
        worker_tag: Optional[str] = None,
        timeout: int = 3600,
        poll_interval: int = 10,
    ) -> Job:
        """Run a workflow job and wait for completion (async).

        Args:
            workflow_id: Parent workflow ID
            questions: Answers to analytic app questions
            priority: Job execution priority
            worker_tag: Worker assignment tag
            timeout: Maximum wait time in seconds
            poll_interval: Seconds between status checks

        Returns:
            Job: Completed job details
        """
        logger.info(f"Running job for workflow {workflow_id} and waiting for completion")

        # Queue the job
        job = await self.run(
            workflow_id=workflow_id,
            questions=questions,
            priority=priority,
            worker_tag=worker_tag,
        )

        # Poll for completion
        start_time = datetime.now()
        elapsed = 0

        while job.status not in [JobStatus.COMPLETED, JobStatus.ERROR, JobStatus.CANCELLED]:
            if elapsed >= timeout:
                from ..exceptions import TimeoutError as JobTimeoutError

                raise JobTimeoutError(f"Job {job.id} did not complete within {timeout} seconds")

            # Wait before polling
            await asyncio.sleep(poll_interval)

            # Refresh job status
            try:
                job = await self.get(job.id)
                elapsed = (datetime.now() - start_time).total_seconds()
                logger.debug(f"Job {job.id} status: {job.status} " f"({elapsed}s elapsed)")
            except Exception as e:
                logger.error(f"Error polling job status: {e}")
                raise

        # Check final status
        if job.status == JobStatus.ERROR:
            messages = job.messages or []
            error_details = [msg.message for msg in messages]
            raise JobExecutionError(
                job.id,
                job.status.value,
                error_details,
            )

        logger.info(f"Job {job.id} completed with status: {job.status}")
        return job
