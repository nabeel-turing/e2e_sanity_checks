#APIs/JiraAPISimulation/IssueLinkTypeApi.py
from .SimulationEngine.db import DB
from typing import Dict, Any, List

def get_issue_link_types() -> Dict[str, List[Dict[str, str]]]:
    """
    Retrieve all issue link types from Jira.

    This method returns a list of all issue link types defined in the system.
    Issue link types are used to categorize and manage relationships between issues.

    Returns:
        Dict[str, List[Dict[str, str]]]: A dictionary containing:
            - issueLinkTypes (List[Dict[str, str]]): A list of issue link type objects, where each type contains:
                - id (str): The unique identifier for the issue link type
                - name (str): The display name of the issue link type

    """
    return {"issueLinkTypes": list(DB.get("issue_link_types", {}).values())}


def get_issue_link_type(link_type_id: str) -> Dict[str, Any]:
    """
    Retrieve a specific issue link type by its ID.

    This method returns detailed information about a specific issue link type
    identified by its unique ID.

    Args:
        link_type_id (str): The unique identifier of the issue link type to retrieve

    Returns:
        Dict[str, Any]: A dictionary containing:
            - issueLinkType (Dict[str, Any]): The issue link type object
                - id (str): The unique identifier for the issue link type
                - name (str): The display name of the issue link type
    
    Raises:
        ValueError: If the link_type_id is empty or not found
    """
    lt = DB["issue_link_types"].get(link_type_id)
    if not lt:
        return {"error": f"Link type '{link_type_id}' not found."}
    return lt