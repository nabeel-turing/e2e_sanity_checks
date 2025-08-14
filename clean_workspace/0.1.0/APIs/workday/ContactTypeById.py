"""
Contact Type Management by ID Module for Workday Strategic Sourcing API Simulation.

This module provides functionality for managing contact types using their unique
internal identifiers in the Workday Strategic Sourcing system. It supports updating
and deleting contact types, with proper validation and error handling. The module
enables comprehensive contact type management through internal identifiers.
"""

from typing import Dict, Tuple, Optional
from .SimulationEngine import db

def patch(id: int, body: Optional[Dict] = None) -> Tuple[Dict, int]:
    """Updates the details of an existing contact type.

    Args:
        id (int): The unique internal identifier of the contact type to update.
        body (Optional[Dict]): A dictionary containing the updated properties for
            the contact type. The dictionary must include:
            - type (str): Object type, should always be "contact_types"
            - id (int): Contact type identifier
            - external_id (str): Contact type external identifier (max 255 characters)
            - name (str): Contact type name (max 255 characters)
    Returns:
        Tuple[Dict, int]: A tuple containing:
            - An error message if the body is missing or if the id in the body doesn't 
                match the URL parameter or if contact type is not found. 
                This is a dictionary with the key "error" and the value is the error message.
            - The updated contact type data if successful, including:
                - id (int): Internal identifier of the contact type
                - external_id (str): External identifier of the contact type
                - All updated fields from the body
            - int: The HTTP status code:
                - 200: Contact type successfully updated
                - 400: Invalid request or mismatched id
                - 404: Contact type not found
    Note:
        The function performs a partial update, meaning only the fields provided
        in the body will be updated. All other fields will remain unchanged.
    """
    contact_type = db.DB["suppliers"]["contact_types"].get(id)
    if not contact_type:
        return {"error": "Contact type not found"}, 404
    if not body:
        return {"error": "Body is required"}, 400
    if body.get("id") != id:
        return {"error": "Id in body must match url"}, 400
    contact_type.update(body)
    return contact_type, 200

def delete(id: int) -> Tuple[Dict, int]:
    """Deletes a contact type from the system.

    Args:
        id (int): The unique internal identifier of the contact type to delete.

    Returns:
        Tuple[Dict, int]: A tuple containing:
            - Dict: An empty dictionary if successful, or an error message if the contact type is not found. 
                The dictionary contains the key "error" and the value is the error message.
            - int: The HTTP status code:
                - 204: Contact type successfully deleted
                - 404: Contact type not found
    """
    if id not in db.DB["suppliers"]["contact_types"]:
        return {"error": "Contact type not found"}, 404
    del db.DB["suppliers"]["contact_types"][id]
    return {}, 204 