# APIs/jira/RoleApi.py
from .SimulationEngine.db import DB
from typing import Dict, Any

def get_roles() -> Dict[str, Any]:
    """
    Get all roles.

    This method returns all roles in the system.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - roles (List[Dict[str, Any]]): A list of roles
                - id (str): The id of the role
                - name (str): The name of the role
    """
    return {"roles": list(DB["roles"].values())}


def get_role(role_id: str) -> Dict[str, Any]:
    """
    Get a role by id.

    This method returns a role by id.

    Args:
        role_id (str): The id of the role

    Returns:
        Dict[str, Any]: A dictionary containing:
            - role (Dict[str, Any]): The role
                - id (str): The id of the role
                - name (str): The name of the role

    Raises:
        ValueError: If the role is not found
    """
    r = DB["roles"].get(role_id)
    if not r:
        return {"error": f"Role '{role_id}' not found."}
    return r
