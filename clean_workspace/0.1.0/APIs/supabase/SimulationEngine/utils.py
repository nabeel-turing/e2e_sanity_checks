from typing import List, Dict, Any, Optional
import uuid # For generating realistic IDs
import re  # For name_to_slug function
from . import models
from datetime import datetime, timezone

# Constants for cost calculations
DB_COST_DEFAULTS = {
    "costs": {
        "project_monthly": 10.0,
        "branch_hourly": 0.01344,
        "default_currency": "USD"
    }
}

# Constants for project creation
PROJECT_CREATION_DEFAULTS = {
    "region": "us-west-1",
    "status": "CREATING"
}

### Consistency Maintenance Functions
"""
1.  **Project Status Update and Cascade (e.g., Pause/Restore Project)**

    * **Scenario for Supabase:** When a project's status changes (e.g., from `ACTIVE` to `PAUSING` or `INACTIVE`, or vice versa), this might affect the availability of its associated API URL, anonymous key, or even its ability to execute SQL/functions.
    * **Thoughts:** While the API methods (`pause_project`, `restore_project`) themselves return the updated status, a helper function can encapsulate the logic for cascading this status change to related components in the DB state, ensuring that the URL or keys are marked as unavailable or adjusted if necessary. For a simulation, this might primarily involve updating the `status` field on the `Project` object and potentially clearing/setting associated URLs/keys if they become truly inaccessible.
"""
def update_project_status_and_cascade(
    db: Dict[str, Any], project_id: str, new_status: str
) -> Optional[Dict[str, Any]]:
    """
    Updates a project's status and cascades effects to related attributes
    like API URL/keys if the project becomes inactive/paused.

    Args:
        db: The SupabaseDB instance.
        project_id: The ID of the project to update.
        new_status: The new status for the project (e.g., 'PAUSING', 'INACTIVE', 'ACTIVE').

    Returns:
        The updated Project object if found, otherwise None.
    """
    for project in db["projects"]:
        if project["id"] == project_id:
            project["status"] = new_status
            # Simulate cascading effects for simplified state
            if new_status in ["INACTIVE", "PAUSING", "ERROR"]:
                db["project_urls"].pop(project_id, None)
                db["project_anon_keys"].pop(project_id, None)
            elif new_status == "ACTIVE":
                # Re-populate placeholder if it was removed, or generate if simulating
                if project_id not in db["project_urls"]:
                        db["project_urls"][project_id] = f"https://{project['name'].lower().replace(' ', '')}.supabase.co"
                if project_id not in db["project_anon_keys"]:
                    db["project_anon_keys"][project_id] = f"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InByb2oxYTJiM2MiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTY3MzcxMzYwMCwiZXhwIjoxODMwNTcxMjAwfQ.simulated_key_{project_id}"
            return project
    return None


### Utility/Interaction Functions
"""
1.  **`get_entity_by_id` (Generic Getter)**

    * **Scenario for Supabase:** This is a fundamental utility needed for almost every API call that targets a specific entity (organization, project, branch, etc.) by its ID.
    * **Thoughts:** A generic function to find an object in a list of Pydantic models by a given ID field. This prevents repetitive loop logic across many API simulation methods.
"""
def get_entity_by_id(
    entity_list: List[Dict[str, Any]], entity_id: str
) -> Optional[Dict[str, Any]]:
    """
    Retrieves a model from a list by its 'id' attribute.

    Args:
        entity_list: A list of model (e.g., db.projects, db.organizations).
        entity_id: The ID of the entity to find.

    Returns:
        The found model, or None if not found.
    """
    for entity in entity_list:
        if entity["id"] == entity_id:
            return entity
    return None

def get_entity_from_db(
    db: Dict[str, Any], entity_type: str ,entity_id: str
):
    return db[entity_type].get(entity_id)

def get_entity_by_id_from_db(
    db: Dict[str, Any], entity_type: str, entity_id: str
) -> Optional[Dict[str, Any]]:
    """
    Retrieves an entity by ID from a specific entity type in the database.
    
    This combines get_main_entities and get_entity_by_id functionality.
    
    Args:
        db: The database instance
        entity_type: The type of entity (e.g., 'projects', 'organizations')
        entity_id: The ID of the entity to find
        
    Returns:
        The found entity dict, or None if not found
    """
    entities = get_main_entities(db, entity_type)
    if not entities:
        return None
    return get_entity_by_id(entities, entity_id)

"""
2.  **`get_projects_for_organization`**

    * **Scenario for Supabase:** Many operations (like checking resource limits, or creating new projects/branches) might need to list projects belonging to a specific organization.
    * **Thoughts:** This function helps simulate filtering projects by their `organization_id`.
"""
def get_projects_for_organization(
    db: Dict[str, Any], organization_id: str
) -> List[Dict[str, Any]]:
    """
    Retrieves all projects belonging to a specific organization.

    Args:
        db: The SupabaseDB instance.
        organization_id: The ID of the organization.

    Returns:
        A list of Project objects associated with the given organization ID.
    """
    return [project for project in db["projects"] if project["organization_id"] == organization_id]


"""
3.  **`get_tables_by_project_and_schemas`**

    * **Scenario for Supabase:** The `list_tables` API call allows filtering by schemas, which requires iterating through the project's tables and then filtering by the provided schema list.
    * **Thoughts:** This function encapsulates the logic for retrieving tables for a given project, optionally filtered by specific schemas.
"""
def get_tables_by_project_and_schemas(
    db: Dict[str, Any], project_id: str, schemas: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Retrieves tables for a given project, optionally filtered by schema.

    Args:
        db: The SupabaseDB instance.
        project_id: The ID of the project.
        schemas: An optional list of schema names to filter by. Defaults to ['public']
                    if not provided in the original API, but here we assume None means all in the DB.

    Returns:
        A list of Table objects for the specified project and schemas.
    """
    project_tables = db["tables"].get(project_id, [])
    if schemas is None:
        return project_tables
    return [table for table in project_tables if table["schema"] in schemas]

"""
4.  **`generate_unique_id`**

    * **Scenario for Supabase:** Many entities require unique IDs (organizations, projects, branches, cost confirmations). This centralizes ID generation.
    * **Thoughts:** A simple wrapper around `uuid.uuid4()` to ensure consistent ID generation throughout the simulation. It's marked as a utility for the *simulation logic* rather than operating directly on `SupabaseDB`, but it's essential for creating new entities.
"""
def generate_unique_id(prefix: str = "") -> str:
    """
    Generates a unique identifier with an optional prefix.

    Args:
        prefix: An optional string prefix for the ID (e.g., "org_", "proj_").

    Returns:
        A unique string identifier.
    """
    return f"{prefix}{str(uuid.uuid4()).replace('-', '')}"

def get_main_entities(db: Dict[str, Any], main_entity: str) -> List[Dict[str, Any]]:
    return db[main_entity]

def name_to_slug(name):
    """
    Convert a name to a URL-friendly slug.
    
    Args:
        name (str): The name to convert
        
    Returns:
        str: URL-friendly slug
    """
    # Convert to lowercase
    slug = name.lower()
    
    # Replace special characters with spaces
    slug = re.sub(r'[^\w\s-]', ' ', slug)  # Replace special chars with spaces
    
    # Replace spaces and underscores with hyphens
    slug = re.sub(r'[\s_]+', '-', slug)  # Replace spaces and underscores with hyphens
    
    # Replace multiple hyphens with single hyphen
    slug = re.sub(r'-+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    return slug

def is_branching_enabled_for_project(db: Dict[str, Any], project_id: str) -> bool:
    """
    Check if branching is enabled for a project based on its organization's subscription features.
    
    Args:
        db: The database instance
        project_id: The project ID to check
        
    Returns:
        bool: True if branching is enabled, False otherwise
    """
    # Get the project
    project = get_entity_by_id_from_db(db, "projects", project_id)
    if not project:
        return False
    
    # Get the organization
    organization = get_entity_by_id_from_db(db, "organizations", project.get("organization_id"))
    if not organization:
        return False
    
    # Check subscription features
    subscription_plan = organization.get("subscription_plan", {})
    features = subscription_plan.get("features", [])
    return "branching_enabled" in features


# SQL Execution Utilities

def validate_project_for_sql_execution(db: Dict[str, Any], project_id: str) -> bool:
    """
    Validate that a project exists and is in a state that allows SQL execution.
    
    Args:
        db: The database instance
        project_id: The project ID to validate
        
    Returns:
        bool: True if the project can execute SQL, False otherwise
    """
    project = get_entity_by_id_from_db(db, "projects", project_id)
    if not project:
        return False
    
    # Only active projects can execute SQL
    allowed_statuses = [models.ProjectStatus.ACTIVE.value]
    return project.get("status") in allowed_statuses


def get_project_postgres_version(db: Dict[str, Any], project_id: str) -> str:
    """
    Get the PostgreSQL version for a project.
    
    Args:
        db: The database instance
        project_id: The project ID
        
    Returns:
        str: The PostgreSQL version (e.g., "PostgreSQL 15") or "PostgreSQL 14" as default
    """
    project = get_entity_by_id_from_db(db, "projects", project_id)
    if project and project.get("version"):
        return project["version"]
    return "PostgreSQL 14"  # Default version


def format_sql_error_message(error_type: str, details: str) -> str:
    """
    Format SQL error messages to match PostgreSQL conventions.
    
    Args:
        error_type: The type of error (e.g., "syntax", "undefined_table")
        details: Additional error details
        
    Returns:
        str: Formatted error message
    """
    error_formats = {
        "syntax": f"syntax error at or near \"{details}\"",
        "undefined_table": f'relation "{details}" does not exist',
        "undefined_column": f'column "{details}" does not exist',
        "undefined_schema": f'schema "{details}" does not exist',
        "type_mismatch": f"type mismatch: {details}",
        "constraint_violation": f"constraint violation: {details}",
        "permission_denied": f'permission denied for table "{details}"',
        "invalid_query": f"invalid query: {details}"
    }
    
    return error_formats.get(error_type, f"error: {details}")
def get_cost_parameter(param_name: str, default_value: Any = None) -> Any:
    """
    Retrieves a cost parameter from the DB configuration.
    Example: param_name could be 'project_monthly', 'branch_hourly', 'default_currency'
    """
    if isinstance(DB_COST_DEFAULTS, dict):
        return DB_COST_DEFAULTS.get("costs", {}).get(param_name, default_value)
    return default_value

def update_cost_parameter(param_name: str, new_value: Any) -> bool:
    """
    Updates a cost parameter in the DB configuration.
    Returns True if successful, False otherwise.
    """
    if isinstance(DB_COST_DEFAULTS, dict):
        if "costs" not in DB_COST_DEFAULTS:
            DB_COST_DEFAULTS["costs"] = {}
        DB_COST_DEFAULTS["costs"][param_name] = new_value
        return True
    return False


def map_db_type_to_typescript(db_type_full: str) -> Optional[str]:
    db_type_lower = db_type_full.lower().strip()
    
    is_array = False
    element_type_str = db_type_lower

    if db_type_lower.endswith('[]'):
        element_type_str = db_type_lower[:-2].strip()
        is_array = True
    elif db_type_lower.endswith(' array'):
        element_type_str = db_type_lower[:-6].strip()
        is_array = True
    elif db_type_lower.startswith('_'):
        pg_array_element_map = {
            "_text": "text", "_varchar": "varchar", "_char": "char",
            "_bpchar": "bpchar", "_name": "name", "_citext": "citext",
            "_int2": "smallint", "_int4": "integer", "_int8": "bigint",
            "_float4": "real", "_float8": "double precision",
            "_bool": "boolean", "_numeric": "numeric", "_decimal": "decimal",
            "_date": "date", 
            "_timestamp": "timestamp", "_timestamptz": "timestamp with time zone",
            "_time": "time", "_timetz": "time with time zone",
            "_uuid": "uuid", "_json": "json", "_jsonb": "jsonb", "_bytea": "bytea",
        }
        if element_type_str in pg_array_element_map:
            element_type_str = pg_array_element_map[element_type_str]
            is_array = True
        else:
            # Heuristic for unmapped internal array types (e.g., UDT arrays like _my_enum)
            # This could still lead to an unsupported base type.
            element_type_str = element_type_str[1:] 
            is_array = True 

    base_type_key = element_type_str.split('(')[0].strip()

    ts_type_map = {
        "integer": "number", "int": "number", "smallint": "number", "bigint": "number", 
        "int2": "number", "int4": "number", "int8": "number",
        "serial": "number", "bigserial": "number", "smallserial": "number",
        "real": "number", "float4": "number", 
        "double precision": "number", "float8": "number",
        "numeric": "number", "decimal": "number", "money": "number",
        "text": "string", "varchar": "string", "character varying": "string",
        "char": "string", "character": "string", "name": "string", "bpchar": "string",
        "citext": "string", "uuid": "string", "xml": "string",
        "boolean": "boolean", "bool": "boolean",
        "date": "string", "timestamp": "string", "timestamp without time zone": "string",
        "timestamptz": "string", "timestamp with time zone": "string",
        "time": "string", "time without time zone": "string",
        "timetz": "string", "time with time zone": "string", "interval": "string",
        "json": "any", "jsonb": "any",
        "bytea": "string",
        "point": "string", "line": "string", "lseg": "string", "box": "string",
        "path": "string", "polygon": "string", "circle": "string",
        "cidr": "string", "inet": "string", "macaddr": "string", "macaddr8": "string",
    }

    if base_type_key in ts_type_map:
        ts_base_type = ts_type_map[base_type_key]
    else:
        return None # Indicate unsupported type

    return f"{ts_base_type}[]" if is_array else ts_base_type

def update_project_creation_defaults(param_name: str, new_value: Any) -> bool:
    """
    Updates a cost parameter in the DB configuration.
    Returns True if successful, False otherwise.
    """
    if isinstance(PROJECT_CREATION_DEFAULTS, dict):
        PROJECT_CREATION_DEFAULTS[param_name] = new_value
        return True
    return False

def get_branch_by_id_from_db(DB:Dict, branch_id: str):
    # Helper to find a branch in the DB for assertion purposes
    for project_key in DB.get("branches", {}):
        for branch in DB["branches"].get(project_key, []):
            if branch["id"] == branch_id:
                return branch
    return None

def find_branch_in_db(DB:Dict,branch_id: str) -> Optional[Dict[str, Any]]:
    """
    Finds a branch by its ID in the DB.
    Branches are stored in DB['branches'] as Dict[parent_project_id, List[Branch_Dict]].
    """
    branches_data = DB.get('branches')
    if not isinstance(branches_data, dict):
        # This indicates an unexpected structure for DB['branches'] itself.
        return None

    for parent_project_id_key in branches_data:
        branches_list = branches_data.get(parent_project_id_key)
        # Ensure branches_list is indeed a list.
        if not isinstance(branches_list, list):
            continue # Skip malformed entries under a parent_project_id_key

        for b_dict in branches_list:
            # Ensure b_dict is a dictionary and has an 'id' field matching branch_id.
            if isinstance(b_dict, dict) and b_dict.get('id') == branch_id:
                return b_dict
    return None


def create_extension_in_db(DB:Dict, project_id: str, extension_name: str, extension_version: str, extension_schema: str, extension_description: str) -> dict:
    """
    Creates an extension in the DB.

    Args:
        DB(Dict): The database instance
        project_id(str): The project ID
        extension_name(str): The name of the extension
        extension_version(str): The version of the extension
        extension_schema(str): The schema of the extension
        extension_description(str): The description of the extension

    Returns:
        dict: The extension dictionary that was created. It can have the following keys:
            - name(str): The name of the extension
            - version(str): The version of the extension
            - schema(str): The schema of the extension
            - description(str): The description of the extension

    Raises:
        KeyError: If the extensions or project does not exist.
        TypeError: If the extension name, version, schema, or description is not a string.
    """
    
    if 'extensions' not in DB:  
        # Extensions does not exist. Initialize it.
        raise KeyError("Extensions does not exist. Please initialize it.")
    if project_id not in DB["extensions"]:
        # Project does not exist
        raise KeyError("Project does not exist. Please initialize it.")

    if not isinstance(extension_name, str):    
        # Extension name is not a string
        raise TypeError("Extension name must be a string")
    if not isinstance(extension_version, str):
        # Extension version is not a string
        raise TypeError("Extension version must be a string")
    if not isinstance(extension_schema, str):
        # Extension schema is not a string
        raise TypeError("Extension schema must be a string")
    if not isinstance(extension_description, str):
        # Extension description is not a string
        raise TypeError("Extension description must be a string")
    
    extension_dict = {
        "name": extension_name,
        "version": extension_version,
        "schema": extension_schema,
        "description": extension_description
    }
    DB["extensions"][project_id].append(extension_dict)
    return extension_dict


def add_cost_information_to_project(
    db: Dict[str, Any], 
    project_id: str, 
    cost_type: str = "project",
    amount: float = None,
    currency: str = None,
    recurrence: str = "monthly",
    description: str = None
) -> Optional[Dict[str, Any]]:
    """
    Adds cost information to an existing project.
    
    Args:
        db: The database instance
        project_id: The ID of the project to add cost information to
        cost_type: Type of cost ("project" or "branch")
        amount: Cost amount (if None, uses default from DB_COST_DEFAULTS)
        currency: Currency code (if None, uses default from DB_COST_DEFAULTS)
        recurrence: Cost recurrence ("hourly" or "monthly")
        description: Description of the cost (if None, generates default)
        
    Returns:
        The created CostDetails object if successful, None if project not found
    """
    # Validate project exists
    project = get_entity_by_id_from_db(db, "projects", project_id)
    if not project:
        return None
    
    # Use defaults if not provided
    if amount is None:
        amount = get_cost_parameter("project_monthly", 10.0)
    if currency is None:
        currency = get_cost_parameter("default_currency", "USD")
    if description is None:
        description = f"{cost_type.title()} cost for {project['name']}"
    
    # Generate confirmation ID
    confirmation_id = generate_unique_id("cost_")
    
    # Create cost details
    cost_details = {
        "type": cost_type,
        "amount": amount,
        "currency": currency,
        "recurrence": recurrence,
        "description": description,
        "confirmation_id": confirmation_id
    }
    
    # Add to confirmed costs
    if "costs" not in db:
        db["costs"] = {}
    db["costs"][confirmation_id] = cost_details
    
    return cost_details


def create_new_organization(
    db: Dict[str, Any],
    name: str,
    subscription_plan: Dict[str, Any] = None,
    organization_id: str = None
) -> Optional[Dict[str, Any]]:
    """
    Creates a new organization in the database.
    
    Args:
        db: The database instance
        name: Name of the organization
        subscription_plan: Optional subscription plan details
        organization_id: Optional custom ID (if None, generates one)
        
    Returns:
        The created Organization object if successful, None if creation fails
    """
    # Generate ID if not provided
    if organization_id is None:
        organization_id = generate_unique_id("org_")
    
    # Check if organization with this ID already exists
    # Only check if organizations key exists in the database
    existing_org = None
    if "organizations" in db:
        existing_org = get_entity_by_id_from_db(db, "organizations", organization_id)
    if existing_org:
        return None
    
    # Use default subscription plan if not provided
    if subscription_plan is None:
        subscription_plan = {
            "id": "plan_free",
            "name": "Free Tier",
            "price": 0.00,
            "currency": "USD",
            "features": [
                "limited_projects",
                "community_support"
            ]
        }
    
    # Create organization object
    organization = {
        "id": organization_id,
        "name": name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "subscription_plan": subscription_plan
    }
    
    # Add to database
    if "organizations" not in db:
        db["organizations"] = []
    db["organizations"].append(organization)
    
    return organization

