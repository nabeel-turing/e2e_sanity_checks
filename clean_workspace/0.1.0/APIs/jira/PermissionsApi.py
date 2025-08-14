# APIs/jira/PermissionsApi.py
from .SimulationEngine.db import DB
from typing import Dict, Any

def get_permissions() -> Dict[str, Any]:
    """
    Get all permissions.

    This method returns all permissions in the system.
    Not available in the real world API.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - permissions (List[str]): The permissions in the system
                - canCreate (bool): Whether the user can create issues
                - canEdit (bool): Whether the user can edit issues
                - canDelete (bool): Whether the user can delete issues
    """
    return {"permissions": DB["permissions"]}
