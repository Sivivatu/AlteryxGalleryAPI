"""
Common types and enums for API models.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

# Type aliases
WorkflowId = str
UserId = str
SubscriptionId = str
JobId = str
ScheduleId = str
CollectionId = str
CredentialId = str
UserGroupId = str


class ExecutionMode(str, Enum):
    """Workflow execution mode."""

    SAFE = "Safe"
    SEMI_SAFE = "SemiSafe"
    UNRESTRICTED = "Unrestricted"


class WorkflowType(str, Enum):
    """Type of workflow."""

    STANDARD = "Standard"
    ANALYTIC_APP = "AnalyticApp"
    MACRO = "Macro"


class JobStatus(str, Enum):
    """Job execution status."""

    QUEUED = "Queued"
    RUNNING = "Running"
    COMPLETED = "Completed"
    ERROR = "Error"
    CANCELLED = "Cancelled"


class JobPriority(str, Enum):
    """Job execution priority."""

    LOW = "Low"
    DEFAULT = "Default"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class ScheduleFrequency(str, Enum):
    """Schedule execution frequency."""

    ONCE = "Once"
    HOURLY = "Hourly"
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    CUSTOM = "Custom"


class ScheduleStatus(str, Enum):
    """Schedule status."""

    ACTIVE = "Active"
    INACTIVE = "Inactive"


class UserRole(str, Enum):
    """User role on Alteryx Server."""

    NO_ACCESS = "NoAccess"
    VIEWER = "Viewer"
    MEMBER = "Member"
    ARTISAN = "Artisan"
    CURATOR = "Curator"
    ADMIN = "Admin"


class CredentialType(str, Enum):
    """Type of credential in Data Connection Manager."""

    DATABASE = "Database"
    FILE_SYSTEM = "FileSystem"
    FTP = "FTP"
    SFTP = "SFTP"
    HTTP = "HTTP"
    HDFS = "HDFS"
    HIVE = "Hive"
    MAPR_FS = "MapRFS"
    MAPR_DB = "MapRDB"
    REDSHIFT = "Redshift"
    SNOWFLAKE = "Snowflake"
    SALESFORCE = "Salesforce"
    TABLEAU = "Tableau"
    ODATA = "OData"
    OAUTH2 = "OAuth2"
    CUSTOM = "Custom"


class ApiError(BaseModel):
    """API error response model."""

    model_config = ConfigDict(populate_by_name=True)

    message: str
    error_code: Optional[str] = Field(None, alias="errorCode")
    details: Optional[dict[str, object]] = None
