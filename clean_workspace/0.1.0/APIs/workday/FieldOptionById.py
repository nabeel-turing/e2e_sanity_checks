"""
This module provides functionality for managing field options by their unique
identifiers in the Workday Strategic Sourcing system. It supports updating
and deleting specific field options using their internal IDs.
"""

from typing import Dict, List, Optional, Union, Any
from .SimulationEngine import db

def patch(id: Union[int, str], new_options: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Update a field options with given parameters.

    Args:
        id (Union[int, str]): The unique identifier of the field option to update.
        new_options (List[Dict[str, Any]]): A list of new options to set for the field option.

    Returns:
        Optional[Dict[str, Any]]: The updated field option data if the update was successful,
            including any of the following fields:
            - type (str): Object type, should always be "fields"
            - field_id (str): Field identifier string
            - options (List[Dict[str, Any]]): List of options configured for the field
            - attributes (Dict[str, Any]): Field attributes containing:
                - label (str): Field name (max 255 characters)
                - position (int): Field order position on the UI
            Returns None if no field option exists with the given ID.
    """
    if id in db.DB["fields"]["field_options"]:
        db.DB["fields"]["field_options"][id]["options"] = new_options
        return db.DB["fields"]["field_options"][id]
    else:
        return None

def delete(id: str) -> bool:
    """Deletes a field option from the system.

    Args:
        id (str): The unique identifier of the field option to delete.

    Returns:
        bool: True if the field option was successfully deleted, False if:
            - The field option does not exist
            - The ID format is invalid
    """
    if id in db.DB["fields"]["field_options"]:
        del db.DB["fields"]["field_options"][id]
        return True
    else:
        return False