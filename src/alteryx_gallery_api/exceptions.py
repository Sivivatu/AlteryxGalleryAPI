"""
Custom Exceptions for the Alteryx Gallery API Wrapper.
"""

class AlteryxAPIError(Exception):
    """Base exception class for all Alteryx API related errors."""
    def __init__(self, message: str, status_code: int | None = None, response_text: str | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text

    def __str__(self) -> str:
        base_message = super().__str__()
        if self.status_code:
            base_message += f" (Status Code: {self.status_code})"
        if self.response_text:
            # Truncate long responses for readability
            preview = self.response_text[:200] + ("..." if len(self.response_text) > 200 else "")
            base_message += f"\nResponse: {preview}"
        return base_message


class AuthenticationError(AlteryxAPIError):
    """Raised when authentication with the Alteryx Server fails."""
    def __init__(self, message: str = "Authentication failed. Check API key/secret and permissions."):
        super().__init__(message, status_code=401)


class WorkflowNotFoundError(AlteryxAPIError):
    """Raised when a requested workflow cannot be found."""
    def __init__(self, workflow_id: str, message: str | None = None):
        msg = message or f"Workflow with ID '{workflow_id}' not found."
        super().__init__(msg, status_code=404)
        self.workflow_id = workflow_id


class JobExecutionError(AlteryxAPIError):
    """Raised when queuing a job fails or the job itself errors during execution."""
    def __init__(
        self,
        message: str,
        job_id: str | None = None,
        status_code: int | None = None,
        response_text: str | None = None
    ):
        super().__init__(message, status_code, response_text)
        self.job_id = job_id
