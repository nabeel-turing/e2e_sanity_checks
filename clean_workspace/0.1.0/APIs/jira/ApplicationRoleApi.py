# APIs/jira/ApplicationRoleApi.py

from .SimulationEngine.db import DB
from typing import Dict, Any


def get_application_roles() -> Dict[str, Any]:
    """
    Retrieve all application roles from Jira.

    This method returns a list of all application roles defined in the system.
    Application roles are used to control access to specific Jira features and functionality.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - roles (List[Dict[str, Any]]): A list of application role objects, where each role contains:
                - key (str): The unique identifier for the role
                - name (str): The display name of the role
                - description (str): A description of the role's purpose
                - permissions (List[str]): List of permissions granted to this role

    """
    return {"roles": list(DB["application_roles"].values())}


def get_application_role_by_key(key: str) -> Dict[str, Any]:
    """
    Retrieve a specific application role by its key.

    This method returns detailed information about a specific application role
    identified by its unique key.

    Args:
        key (str): The unique identifier of the application role to retrieve

    Returns:
        Dict[str, Any]: A dictionary containing:
            - If role exists:
                - key (str): The unique identifier for the role
                - name (str): The display name of the role
                - description (str): A description of the role's purpose
                - permissions (List[str]): List of permissions granted to this role

    Raises:
        ValueError: If the specified role key does not exist
    """
    role = DB["application_roles"].get(key)
    if role is None:
        return {"error": f"Role '{key}' not found."}
    return role
