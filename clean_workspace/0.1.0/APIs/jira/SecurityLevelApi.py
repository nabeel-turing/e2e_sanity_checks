# APIs/jira/SecurityLevelApi.py
from .SimulationEngine.db import DB
from typing import Dict, Any

def get_security_levels() -> Dict[str, Any]:
    """
    Get all security levels.

    This method returns all security levels in the system.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - securityLevels (List[Dict[str, Any]]): A list of security levels
                - id (str): The id of the security level
                - name (str): The name of the security level
                - description (str): The description of the security level
    """
    return {"securityLevels": list(DB["security_levels"].values())}


def get_security_level(sec_id: str) -> Dict[str, Any]:
    """
    Get a security level by id.

    This method returns a security level by id.

    Args:
        sec_id (str): The id of the security level

    Returns:
        Dict[str, Any]: A dictionary containing:
            - securityLevel (Dict[str, Any]): The security level
                - id (str): The id of the security level
                - name (str): The name of the security level
                - description (str): The description of the security level

    Raises:
        ValueError: If the security level is not found
    """
    lvl = DB["security_levels"].get(sec_id)
    if not lvl:
        return {"error": f"Security level '{sec_id}' not found."}
    return lvl
