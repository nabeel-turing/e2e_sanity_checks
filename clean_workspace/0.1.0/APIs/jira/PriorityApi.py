# APIs/jira/PriorityApi.py
from .SimulationEngine.db import DB
from .SimulationEngine.custom_errors import PriorityNotFoundError
from typing import Dict, Any, List


def get_priorities() -> Dict[str, List[Dict[str, str]]]:
    """
    Get all priorities.

    This method returns all priorities in the system.

    Returns:
        Dict[str, List[Dict[str, str]]]: A dictionary containing:
            - priorities (List[str]): The priorities in the system
                - id (str): The id of the priority
                - name (str): The name of the priority
    """
    return {"priorities": list(DB["priorities"].values())}


def get_priority(priority_id: str) -> Dict[str, Any]:
    """
    Get a priority by id.

    Args:
        priority_id (str): The id of the priority to get. Must be a non-empty string.

    Returns:
        Dict[str, Any]: The priority object containing:
            - id (str): The id of the priority
            - name (str): The name of the priority

    Raises:
        TypeError: If priority_id is not a string.
        ValueError: If priority_id is an empty string.
        PriorityNotFoundError: If the priority with the given ID is not found in the database.
    """
    # Input type validation
    if not isinstance(priority_id, str):
        raise TypeError(f"priority_id must be a string, got {type(priority_id).__name__}.")
    
    # Input value validation
    if not priority_id:
        raise ValueError("priority_id cannot be empty.")

    # Check if priority exists in database
    priority = DB["priorities"].get(priority_id)
    if not priority:
        raise PriorityNotFoundError(f"Priority with ID '{priority_id}' not found in database.")
    
    return priority
