# APIs/jira/PermissionSchemeApi.py
from .SimulationEngine.db import DB
from typing import Dict, Any

def get_permission_schemes() -> Dict[str, Any]:
    """
    Get all permission schemes.

    This method returns all permission schemes in the system.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - schemes (List[str]): The permission schemes in the system
                - id (str): The id of the permission scheme
                - name (str): The name of the permission scheme
                - permissions (List[str]): The permissions in the permission scheme
    """
    return {"schemes": list(DB["permission_schemes"].values())}


def get_permission_scheme(scheme_id: str) -> Dict[str, Any]:
    """
    Get a permission scheme by id.

    This method returns a permission scheme by id.

    Args:
        scheme_id (str): The id of the permission scheme to get

    Returns:
        Dict[str, Any]: A dictionary containing:
            - scheme (dict): The permission scheme
                - id (str): The id of the permission scheme
                - name (str): The name of the permission scheme
                - permissions (List[str]): The permissions in the permission scheme

    Raises:
        ValueError: If the scheme_id is not found
    """
    scheme = DB["permission_schemes"].get(scheme_id)
    if not scheme:
        return {"error": f"Permission scheme '{scheme_id}' not found."}
    return scheme
