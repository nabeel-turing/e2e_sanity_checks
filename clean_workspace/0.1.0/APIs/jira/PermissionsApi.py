# APIs/jira/PermissionsApi.py
from typing import Dict, Any
from .SimulationEngine.db import DB
from typing import Dict, Any


def get_permissions() -> Dict[str, Dict[str, bool]]:
    """
    Get all permissions.

    This method returns all permissions in the system.
    Not available in the real world API.

    Returns:
        Dict[str, Dict[str, bool]]: A dictionary containing:
            - permissions (Dict[str, bool]): The permissions in the system with keys:
                - canCreate (bool): Whether the user can create issues
                - canEdit (bool): Whether the user can edit issues
                - canDelete (bool): Whether the user can delete issues
    """
    return {"permissions": DB["permissions"]}
