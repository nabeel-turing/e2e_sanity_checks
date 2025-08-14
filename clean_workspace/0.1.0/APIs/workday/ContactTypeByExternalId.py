"""
Contact Type Management by External ID Module for Workday Strategic Sourcing API Simulation.

This module provides functionality for managing contact types using their external
identifiers in the Workday Strategic Sourcing system. It supports updating and
deleting contact types through their external IDs, with proper validation and
error handling. The module enables comprehensive contact type management through
external identifiers.
"""

from typing import Dict, Tuple, Optional
from .SimulationEngine import db

def patch(external_id: str, body: Optional[Dict] = None) -> Tuple[Dict, int]:
    """Updates the details of an existing contact type using its external ID.

    This function allows for the modification of an existing contact type's properties
    by searching for it using its external identifier. It performs validation checks
    to ensure the update is valid and the contact type exists before applying the
    changes. The function supports partial updates of contact type properties.

    Args:
        external_id (str): The unique external identifier of the contact type to update.
        body (Optional[Dict]): A dictionary containing the updated properties for
            the contact type. The dictionary must include:
            - type (str): Object type, should always be "contact_types"
            - id (int): Contact type identifier
            - external_id (str): Contact type external identifier (max 255 characters)
            - name (str): Contact type name (max 255 characters)

    Returns:
        Tuple[Dict, int]: A tuple containing:
            - An error message if the body is missing or if the external_id in the body doesn't
                match the URL parameter or if contact type is not found.
                This is a dictionary with the key "error" and the value is the error message.
            - Dict: The updated contact type data if successful, including:
                - id (int): Internal identifier of the contact type
                - external_id (str): External identifier of the contact type
                - All updated fields from the body
            - int: The HTTP status code:
                - 200: Contact type successfully updated
                - 400: Invalid request or mismatched external_id
                - 404: Contact type not found


    Note:
        The function performs a partial update, meaning only the fields provided
        in the body will be updated. All other fields will remain unchanged.
    """
    for contact_type_id, contact_type in db.DB["suppliers"]["contact_types"].items():
        if contact_type.get("external_id") == external_id:
            if not body:
                return {"error": "Body is required"}, 400
            if body.get("external_id") != external_id:
                return {"error": "External id in body must match url"}, 400
            contact_type.update(body)
            db.DB["suppliers"]["contact_types"][contact_type_id] = contact_type
            return contact_type, 200
    return {"error": "Contact type not found"}, 404

def delete(external_id: str) -> Tuple[Dict, int]:
    """Deletes a contact type from the system using its external ID.

    Args:
        external_id (str): The unique external identifier of the contact type to delete.

    Returns:
        Tuple[Dict, int]: A tuple containing:
            - Dict: An empty dictionary if successful, or an error message with the key "error" if the
                contact type is not found.
            - int: The HTTP status code:
                - 204: Contact type successfully deleted
                - 404: Contact type not found
    """
    contact_type_id_to_delete = None
    for contact_type_id, contact_type in db.DB["suppliers"]["contact_types"].items():
        if contact_type.get("external_id") == external_id:
            contact_type_id_to_delete = contact_type_id
            break
    if contact_type_id_to_delete is None:
        return {"error": "Contact type not found"}, 404
    del db.DB["suppliers"]["contact_types"][contact_type_id_to_delete]
    return {}, 204 