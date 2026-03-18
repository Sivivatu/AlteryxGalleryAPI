"""
Custom exceptions for Alteryx Server API wrapper.
"""


class AlteryxError(Exception):
    """Base exception for all Alteryx API errors."""

    pass


class ConfigurationError(AlteryxError):
    """Raised for configuration/setup issues."""

    pass


class AuthenticationError(AlteryxError):
    """Raised when authentication fails (401)."""

    def __init__(self, message: str = "Authentication failed. Check credentials and permissions."):
        super().__init__(message)


class AuthorizationError(AlteryxError):
    """Raised when access is denied (403)."""

    def __init__(self, message: str = "Access denied. Insufficient permissions."):
        super().__init__(message)


class NotFoundError(AlteryxError):
    """Raised when resource is not found (404)."""

    def __init__(self, message: str = "Resource not found."):
        super().__init__(message)


class WorkflowNotFoundError(NotFoundError):
    """Raised when a workflow is not found."""

    def __init__(self, workflow_id: str, message: str | None = None):
        self.workflow_id = workflow_id
        super().__init__(message or f"Workflow '{workflow_id}' not found")


class JobNotFoundError(NotFoundError):
    """Raised when a job is not found."""

    def __init__(self, job_id: str):
        self.job_id = job_id
        super().__init__(f"Job '{job_id}' not found")


class ScheduleNotFoundError(NotFoundError):
    """Raised when a schedule is not found."""

    def __init__(self, schedule_id: str):
        self.schedule_id = schedule_id
        super().__init__(f"Schedule '{schedule_id}' not found")


class UserNotFoundError(NotFoundError):
    """Raised when a user is not found."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        super().__init__(f"User '{user_id}' not found")


class UserGroupNotFoundError(NotFoundError):
    """Raised when a user group is not found."""

    def __init__(self, group_id: str):
        self.group_id = group_id
        super().__init__(f"User group '{group_id}' not found")


class CollectionNotFoundError(NotFoundError):
    """Raised when a collection is not found."""

    def __init__(self, collection_id: str):
        self.collection_id = collection_id
        super().__init__(f"Collection '{collection_id}' not found")


class CredentialNotFoundError(NotFoundError):
    """Raised when a credential is not found."""

    def __init__(self, credential_id: str):
        self.credential_id = credential_id
        super().__init__(f"Credential '{credential_id}' not found")


class ValidationError(AlteryxError):
    """Raised when request validation fails (400)."""

    def __init__(self, message: str = "Validation failed for request."):
        super().__init__(message)


class RateLimitError(AlteryxError):
    """Raised when rate limit is exceeded (429)."""

    def __init__(self, retry_after: int | None = None):
        self.retry_after = retry_after
        msg = "Rate limit exceeded"
        if retry_after:
            msg += f". Retry after {retry_after}s"
        super().__init__(msg)


class ServerError(AlteryxError):
    """Raised for server-side errors (5xx)."""

    def __init__(self, message: str = "Server error occurred."):
        super().__init__(message)


class JobExecutionError(AlteryxError):
    """Raised when job execution fails."""

    def __init__(self, job_id: str, status: str, messages: list[str] | None = None):
        self.job_id = job_id
        self.status = status
        self.messages = messages or []
        super().__init__(f"Job '{job_id}' failed with status '{status}'")


class TimeoutError(AlteryxError):
    """Raised when an operation times out."""

    def __init__(self, message: str = "Operation timed out."):
        super().__init__(message)
