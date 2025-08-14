from pydantic import BaseModel, Field, field_validator, Extra, validator
from typing import List, Dict, Any, Literal, Literal, Optional
from datetime import datetime
from enum import Enum


class ProjectStatus(str, Enum):
    """Enum for Supabase project status values."""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    CREATING = "CREATING"
    INITIALIZING = "INITIALIZING"
    PAUSED = "PAUSED"
    PAUSING = "PAUSING"
    RESTORING = "RESTORING"
    COMING_UP = "COMING_UP"
    CREATING_PROJECT = "CREATING_PROJECT"

VALID_PROJECT_STATUS = [status.value for status in ProjectStatus]

# Project statuses that cannot transition to PAUSED
NON_PAUSABLE_STATUSES = [
    ProjectStatus.PAUSED.value,
    ProjectStatus.PAUSING.value,
    ProjectStatus.CREATING.value,
    ProjectStatus.CREATING_PROJECT.value,
    ProjectStatus.INITIALIZING.value,
    ProjectStatus.RESTORING.value
]

class BranchStatus(str, Enum):
    """Enum for Supabase branch status values."""
    ACTIVE = "ACTIVE"
    CREATING = "CREATING"
    CREATING_PROJECT = "CREATING_PROJECT"
    MERGING = "MERGING"
    REBASING = "REBASING"
    RESETTING = "RESETTING"
    ERROR = "ERROR"

class MigrationStatus(str, Enum):
    """Enum for Supabase migration status values."""
    APPLIED = "applied"
    PENDING = "pending"
    APPLIED_SUCCESSFULLY = "APPLIED_SUCCESSFULLY"
    FAILED = "FAILED"

class EdgeFunctionStatus(str, Enum):
    """Enum for Supabase edge function status values."""
    ACTIVE = "ACTIVE"
    BUILDING = "BUILDING"
    DEPLOYING = "DEPLOYING"
    ERROR = "ERROR"

class LogLevel(str, Enum):
    """Enum for log levels."""
    INFO = "INFO"
    WARN = "WARN" 
    ERROR = "ERROR"
    DEBUG = "DEBUG" 

class Organization(BaseModel):
    """Represents a Supabase organization."""
    id: str
    name: str
    created_at: str  # ISO 8601 timestamp string
    subscription_plan: Optional[Dict[str, Any]] = None # Includes 'id', 'name', 'price', 'currency', 'features'

class SubscriptionPlanDetails(BaseModel):
    """Details of an organization's subscription plan."""
    id: str
    name: str
    price: float
    currency: str
    features: List[str]

class OrganizationDetailsResponse(BaseModel):
    """Organization details including subscription plan, for API response."""
    id: str
    name: str
    slug: str
    created_at: str  # ISO 8601 timestamp
    subscription_plan: SubscriptionPlanDetails

class Project(BaseModel):
    """Represents a Supabase project."""
    id: str
    name: str
    organization_id: str
    region: str
    status: ProjectStatus
    created_at: str  # ISO 8601 timestamp string
    version: Optional[str] = None # Postgres version for projects

class TableColumn(BaseModel):
    """Represents a column within a database table."""
    name: str
    data_type: str
    is_nullable: bool
    default_value: Optional[str] = None

class PrimaryKey(BaseModel):
    """Represents a primary key column."""
    name: str

class Relationship(BaseModel):
    """Represents a foreign key relationship."""
    constraint_name: str
    source_schema: str
    source_table_name: str
    source_column_name: str
    target_table_schema: str
    target_table_name: str
    target_column_name: str

class Table(BaseModel):
    """Represents a database table."""
    name: str
    schema: str = Field(..., alias='schema')
    comment: Optional[str] = None
    columns: List[TableColumn] = []
    primary_keys: List[PrimaryKey] = []
    relationships: List[Relationship] = []

class Extension(BaseModel):
    """Represents a database extension."""
    name: str
    schema: str = Field(..., alias='schema')
    version: str
    description: str

class Migration(BaseModel):
    """Represents a database migration."""
    version: str
    name: str
    status: MigrationStatus
    applied_at: Optional[str] = None  # ISO 8601 timestamp string
    query: Optional[str] = None # Storing the query for simulation purposes

class EdgeFunction(BaseModel):
    """Represents a Supabase Edge Function."""
    id: str
    slug: str
    name: str
    version: str
    status: EdgeFunctionStatus
    created_at: str  # ISO 8601 timestamp string
    updated_at: str  # ISO 8601 timestamp string
    entrypoint_path: Optional[str] = None
    import_map_path: Optional[str] = None
    files: Optional[List[Dict[str, Any]]] = None # Stores file name and content

class LogEntry(BaseModel):
    """Represents a log entry for Supabase services."""
    timestamp: str  # ISO 8601 timestamp
    level: LogLevel
    message: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ProjectLogs(BaseModel):
    """Represents all logs for a specific project organized by service."""
    # Using Dict to maintain compatibility with existing code that accesses logs by service name
    services: Dict[str, List[LogEntry]] = Field(default_factory=dict)

class Branch(BaseModel):
    """Represents a development branch of a Supabase project."""
    id: str
    name: str
    parent_project_id: str # The main project this branch originates from
    branch_project_id: str # The unique project ID for this branch's database
    status: BranchStatus
    created_at: str  # ISO 8601 timestamp string
    last_activity_at: str  # ISO 8601 timestamp string

class CostDetails(BaseModel):
    """Represents the cost details for creating projects or branches."""
    type: Literal["project", "branch"] # Changed from str
    amount: float
    currency: str
    recurrence: Literal["hourly", "monthly"] # Changed from str, and updated comment/enum
    description: str
    confirmation_id: Optional[str] = None

class SupabaseDB(BaseModel):
    """
    Main Pydantic class to hold all in-memory Supabase simulation data.
    """
    organizations: List[Organization] = []
    projects: List[Project] = []
    tables: Dict[str, List[Table]] = Field(default_factory=dict) # project_id -> List[Table]
    extensions: Dict[str, List[Extension]] = Field(default_factory=dict) # project_id -> List[Extension]
    migrations: Dict[str, List[Migration]] = Field(default_factory=dict) # project_id -> List[Migration]
    edge_functions: Dict[str, List[EdgeFunction]] = Field(default_factory=dict) # project_id -> List[EdgeFunction]
    branches: Dict[str, List[Branch]] = Field(default_factory=dict) # parent_project_id -> List[Branch]
    costs: Dict[str, CostDetails] = Field(default_factory=dict) # confirmation_id -> CostDetails (for confirmed costs)
    # This could store temporary cost quotes before confirmation
    unconfirmed_costs: Dict[str, CostDetails] = Field(default_factory=dict) # generated_quote_id -> CostDetails

    # For API keys and URLs, which are project-specific
    project_urls: Dict[str, str] = Field(default_factory=dict) # project_id -> url
    project_anon_keys: Dict[str, str] = Field(default_factory=dict) # project_id -> anon_key
    project_ts_types: Dict[str, str] = Field(default_factory=dict) # project_id -> typescript_types_content

    # This will simulate logs, project_id -> ProjectLogs
    logs: Dict[str, ProjectLogs] = Field(default_factory=dict)

class ListExtensionsInput(BaseModel):
    """
    Pydantic model for validating the input to the list_extensions function.
    Ensures that project_id is a string.
    """
    project_id: str
class MergeBranchResponse(BaseModel):
    """
    Details the status of a branch merge operation.
    """
    branch_id: str
    target_project_id: str
    status: str  # e.g., 'MERGING', 'COMPLETED', 'FAILED', 'CONFLICT'
    merge_request_id: Optional[str] = None

class ProjectApiInfo(BaseModel):
    """
    Represents information for accessing a project's API,
    matching the structure of the dictionary returned by get_project_url.
    """
    project_id: str
    api_url: Optional[str] # The API URL for the project, can be None if not configured.



# SQL Execution Models

class SQLColumn(BaseModel):
    """Represents a column in SQL query results."""
    name: str
    type_oid: int  # PostgreSQL type OID

class SQLSelectResult(BaseModel):
    """Result from a SELECT query."""
    rows: List[Dict[str, Any]]  # List of row dictionaries
    columns: List[SQLColumn]  # Column metadata
    row_count: int


class SQLDMLResult(BaseModel):
    """Result from DML operations (INSERT, UPDATE, DELETE)."""
    row_count: int
    status_message: str  # PostgreSQL-style status message


class SQLDDLResult(BaseModel):
    """Result from DDL operations."""
    row_count: int = 0
    status_message: str = "OK"


class CostConfirmationResponse(BaseModel):
    """
    Represents the response from confirming a cost, containing the confirmation ID.
    """
    confirmation_id: str

class ConfirmCostArgs(BaseModel):
    """
    Pydantic model for validating input arguments to the confirm_cost function.
    Based on the inputSchema provided in the function's docstring.
    """
    type: Literal["project", "branch"]
    recurrence: Literal["hourly", "monthly"]
    amount: float # Pydantic's float type handles JSON "number" type appropriately

class EdgeFunctionResponseItem(BaseModel):
    """
    Represents an Edge Function as returned by the list_edge_functions endpoint.
    Matches the dictionary structure described in the function's docstring.
    """
    id: str
    slug: str
    name: str
    version: str
    status: str  # e.g., 'ACTIVE', 'BUILDING', 'ERROR'
    created_at: str  # ISO 8601 timestamp
    updated_at: str  # ISO 8601 timestamp


class GetCostInputArgs(BaseModel):
    type: Literal['project', 'branch'] # Use Literal for strict enum-like behavior
    organization_id: str = Field(min_length=1)

    class Config:
        extra = "forbid"

class ListMigrationsArgsValidator(BaseModel):
    """
    Input arguments for the list_migrations function, ensuring strict type
    checking and non-empty constraints.
    """
    project_id: str 

    @validator('project_id', pre=True, allow_reuse=True)
    def _project_id_must_be_a_string(cls, v: Any) -> str:
        if not isinstance(v, str):
            # This error message is internal to Pydantic's validation process.
            # The function will catch PydanticValidationError and raise a generic 
            # custom_errors.ValidationError with the message "validation error".
            raise ValueError('Project ID must be a string.')
        return v

    class Config:
        # Configuration to prevent Pydantic from allowing extra fields if project_id
        # were passed as part of a dictionary. For a single argument, less critical.
        extra = "forbid"

class RestoreProjectResponse(BaseModel):
    """
    Response model for the restore_project function.
    Details the status of the restore operation.
    """
    project_id: str
    status: ProjectStatus # Uses ProjectStatus enum from .SimulationEngine.models
    message: str
    

class EdgeFunctionFile(BaseModel):
    """
    Represents a single file to be uploaded for an Edge Function.
    Corresponds to the structure of dictionaries within the 'files' argument list.
    """
    name: str  # The name of the file (e.g., 'index.ts', 'utils/helper.ts')
    content: str  # The string content of the file

class DeployEdgeFunctionInputArgs(BaseModel):
    """
    Pydantic model for validating input arguments to the deploy_edge_function.
    """
    project_id: str
    name: str
    files: List[EdgeFunctionFile] 
    entrypoint_path: str = Field(default="index.ts")
    import_map_path: Optional[str] = Field(default=None)
    # This model does not need Config.extra = "forbid" as it's instantiated from direct args, not a dict.

class DeployEdgeFunctionResponse(BaseModel):
    """
    Represents the details of a deployed Edge Function, as returned by
    the deploy_edge_function operation.
    """
    id: str
    slug: str
    name: str
    version: str
    status: str # e.g., 'DEPLOYING', 'ACTIVE', 'ERROR'
    deployment_id: str

      
CreateProjectRegionEnum = Literal[
    "us-west-1", "us-east-1", "us-east-2", "ca-central-1",
    "eu-west-1", "eu-west-2", "eu-west-3", "eu-central-1", "eu-central-2",
    "eu-north-1", "ap-south-1", "ap-southeast-1", "ap-northeast-1",
    "ap-northeast-2", "ap-southeast-2", "sa-east-1"
]

class CreateProjectArgs(BaseModel):
    """
    Pydantic model for validating input arguments to the create_project function.
    """
    name: str
    organization_id: str
    confirm_cost_id: str
    region: Optional[CreateProjectRegionEnum] = None

class DeleteBranchResponse(BaseModel):
    """
    Represents the status of a branch delete operation.
    """
    branch_id: str
    status: str  # e.g., 'DELETED', 'PENDING_DELETION', 'ERROR'
    message: str

# Helper Pydantic model for input validation, defined before the main function.
class GetProjectInput(BaseModel):
    id: str = Field(..., min_length=1, description="The project ID")
class ProjectResponse(BaseModel):
    """
    Represents the detailed structure of a Supabase project as returned by the get_project function.
    This model reflects the specific fields and types described in the function's docstring for its return dictionary.
    """
    id: str
    name: str
    organization_id: str
    region: str
    status: str
    version: str # Postgres version, as a string.
    created_at: str # ISO 8601 timestamp string.


class ResetBranchInputArgs(BaseModel):
    """
    Input arguments for the reset_branch function, ensuring strict type
    checking and non-empty constraints.
    """
    branch_id: str = Field(..., min_length=1)
    migration_version: Optional[str] = None

    class Config:
        extra = 'forbid'
        validate_assignment = True