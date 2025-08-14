# APIs/jira/StatusApi.py
from .SimulationEngine.db import DB
from .SimulationEngine.custom_errors import MissingRequiredFieldError
from typing import Dict, Any

def get_statuses() -> Dict[str, Any]:
    """
    Get all statuses.

    This method returns all statuses in the system.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - statuses (List[Dict[str, Any]]): A list of statuses.
                Each status dictionary has:
                - id (str): The id of the status.
                - name (str): The name of the status.
                - description (str): The description of the status.
                - statusCategory (Dict[str, Any]): not implemented in the simulation
    """
    # We'll store statuses in DB["statuses"] for convenience
    if "statuses" not in DB:
        DB["statuses"] = {}  # Initialize the statuses dictionary
    return {"statuses": list(DB["statuses"].values())}


def get_status(status_id: str) -> Dict[str, Any]:
    """
    Get a status by id.

    This method returns a status by id.

    Args:
        status_id (str): The id of the status

    Returns:
        Dict[str, Any]: A dictionary containing:
            - status (Dict[str, Any]): The status
                - id (str): The id of the status
                - name (str): The name of the status
                - description (str): The description of the status
                - statusCategory (Dict[str, Any]): The category of the status - not implemented in the simulation
                    - id (str): The id of the status category
                    - key (str): The key of the status category
                    - name (str): The name of the status category
                    - colorName (str): The color name of the status category

    Raises:
        MissingRequiredFieldError: If status_id is not provided.
        TypeError: If status_id is not a string.
        ValueError: If the status is not found.
    """
    if not status_id:
        raise MissingRequiredFieldError(field_name="status_id")
    if not isinstance(status_id, str):
        raise TypeError("status_id must be a string")
    
    if "statuses" not in DB:
        DB["statuses"] = {}
    
    if status_id not in DB["statuses"]:
        raise ValueError(f"Status '{status_id}' not found.")
    
    return DB["statuses"][status_id]    
