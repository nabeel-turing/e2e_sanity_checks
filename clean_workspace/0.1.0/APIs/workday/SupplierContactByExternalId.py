"""
Supplier Contact Management by External ID Module

This module provides functionality for managing supplier contacts using their external
identifiers in the Workday Strategic Sourcing system. It supports operations for
retrieving, updating, and deleting supplier contact records using external IDs.

The module interfaces with the simulation database to provide comprehensive supplier
contact management capabilities, particularly useful when integrating with external
systems that maintain their own identifiers. It allows users to:
- Retrieve detailed supplier contact information using external IDs
- Update existing supplier contact records with external ID validation
- Delete supplier contact entries by external ID
- Handle related resource inclusion where applicable

Functions:
    get: Retrieves supplier contact details by external ID
    patch: Updates supplier contact details by external ID
    delete: Deletes a supplier contact by external ID
"""
from typing import Optional, Dict, Any, Tuple

from .SimulationEngine import db

def get(external_id: str, _include: Optional[str] = None) -> Tuple[Dict[str, Any], int]:
    """
    Retrieves the details of an existing supplier contact by external ID.

    This function returns the full resource representation of a supplier contact
    identified by its external ID, with optional inclusion of related entities.

    Args:
        external_id (str): Required. Unique external identifier of the supplier contact.
            Example: "CNT-17"
        _include (Optional[str]): Comma-separated list of related resources to include in the response.
            Allowed values:
                - "supplier_company"
                - "contact_types"
                - "phones"

    Returns:
        Tuple[Dict[str, Any], int]: A tuple containing the supplier contact and HTTP status code.
            - First element (Dict[str, Any]): A dictionary containing the supplier contact details if successful, else the error message.
            - Second element (int): HTTP status code. It is 200 if successful, 404 if not found.

            If Success, First element is a dictionary containing the supplier contact details.
                - type (str): Always "supplier_contacts".
                - id (int): Unique internal identifier for the supplier contact.
                - attributes (Dict[str, Any]):
                    - name (str): Full name (≤ 255 characters).
                    - first_name (Optional[str]): First name (≤ 255 characters).
                    - last_name (Optional[str]): Last name (≤ 255 characters).
                    - email (str): Contact's email address (≤ 255 characters).
                    - notes (Optional[str]): Notes related to the contact.
                    - phone_number (Optional[str]): Deprecated. Prefer using `phones` relationship.
                    - job_title (Optional[str]): Job title.
                    - external_id (str): The external identifier of the contact.
                    - is_suggested (Optional[bool]): Whether the contact was suggested and unapproved.
                    - updated_at (str): Timestamp of the last update (ISO 8601).

                - relationships (Dict[str, Any]):
                    - supplier_company (Dict[str, Any]):
                        - data: { id (int), type (str) }
                    - contact_types (Optional[Dict[str, Any]]):
                        - data: List[{ id (int), type (str) }]
                    - phones (Optional[Dict[str, Any]]):
                        - data: List[{ id (int), type (str) }]

            If Error, First element is a dictionary containing the error message.  
                - error (str): Error message.
    """

    for contact in db.DB["suppliers"]["supplier_contacts"].values():
        if contact.get("external_id") == external_id:
            if _include:
                # Simulate include logic (not fully implemented)
                pass
            return contact, 200
    return {"error": "Contact not found"}, 404

def patch(external_id: str, _include: Optional[str] = None, body: Optional[Dict[str, Any]] = None
          ) -> Tuple[Dict[str, Any], int]:
    """
    Updates the details of an existing supplier contact using the external ID.

    The function modifies a supplier contact’s attributes and relationships such as contact types
    and phone numbers, identified via the external ID. The request body must include the contact's
    internal `id`, which must match the contact's actual identifier in the system.

    Args:
        external_id (str): Required. Unique external identifier of the supplier contact.
            Example: "CNT-17"
        _include (Optional[str]): Comma-separated list of related resources to include in the response.
            Allowed values:
                - "supplier_company"
                - "contact_types"
                - "phones"
        body (Optional[Dict[str, Any]]): Payload with updated supplier contact details.
            - data (Dict[str, Any]):
                - type (str): Required. Must be "supplier_contacts".
                - id (int): Required. Must match the internal ID of the contact being updated.
                - attributes (Dict[str, Any]):
                    - name (str): Required unless both `first_name` and `last_name` are given. Full name (≤ 255 chars).
                    - first_name (Optional[str]): First name (≤ 255 chars).
                    - last_name (Optional[str]): Last name (≤ 255 chars).
                    - email (str): Required. Email address (≤ 255 chars).
                    - notes (Optional[str]): Optional notes related to the contact.
                    - phone_number (Optional[str]): Deprecated. Prefer using `phones` relationship.
                    - job_title (Optional[str]): Job title of the contact.
                    - external_id (Optional[str]): External ID of the contact.
                    - is_suggested (Optional[bool]): Indicates if the contact was suggested and not yet approved.
                - relationships (Dict[str, Any]):
                    - contact_types (Optional[Dict[str, Any]]):
                        - data: List[{ id (int), type (str) }]
                    - phones (Optional[Dict[str, Any]]):
                        - data: List[{ id (int), type (str) }]

    Returns:
        Tuple[Dict[str, Any], int]: A tuple containing the updated supplier contact resource and HTTP status code.
            - First element (Dict[str, Any]): A dictionary containing the updated supplier contact resource if successful, else the error message.
            - Second element (int): HTTP status code. It is 200 if successful, 400 if body is required, 404 if not found.

            If Success, First element is a dictionary containing the updated supplier contact details.
                - type (str): Always "supplier_contacts".
                - id (int): Internal ID of the supplier contact.
                - attributes (Dict[str, Any]):
                    - name (str): Full contact name.
                    - first_name (Optional[str]): First name.
                    - last_name (Optional[str]): Last name.
                    - email (str): Contact's email.
                    - notes (Optional[str]): Notes.
                    - phone_number (Optional[str]): Deprecated phone number.
                    - job_title (Optional[str]): Job title.
                    - external_id (Optional[str]): External system ID.
                    - is_suggested (Optional[bool]): Indicates if contact is suggested.
                    - updated_at (str): Last updated timestamp (ISO 8601).
                - relationships (Dict[str, Any]):
                    - supplier_company (Dict[str, Any]):
                        - data: { id (int), type (str) }
                    - contact_types (Optional[Dict[str, Any]]):
                        - data: List[{ id (int), type (str) }]
                    - phones (Optional[Dict[str, Any]]):
                        - data: List[{ id (int), type (str) }]

            If Error, First element is a dictionary containing the error message.  
                - error (str): Error message.
    """

    for contact_id, contact in db.DB["suppliers"]["supplier_contacts"].items():
        if contact.get("external_id") == external_id:
            if not body:
                return {"error": "Body is required"}, 400
            contact.update(body)
            if _include:
                # Simulate include logic (not fully implemented)
                pass
            return contact, 200
    return {"error": "Contact not found"}, 404

def delete(external_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Deletes a supplier contact using the external identifier.

    This function permanently removes the specified supplier contact identified by
    its external ID from the system.

    Args:
        external_id (str): Required. The unique external identifier of the supplier contact.
            Example: "CNT-17"

    Returns:    
        Tuple[Dict[str, Any], int]: A tuple containing an empty dictionary or the error dictionary and HTTP status code.
            - First element (Dict[str, Any]): An empty dictionary if successful, else the error     .
            - Second element (int): HTTP status code. It is 204 if successful, 404 if not found.

            If Success, First element is an empty dictionary.
            If Error, First element is a dictionary containing the error message.  
                - error (str): Error message.
    """

    contact_id_to_delete = None
    for contact_id, contact in db.DB["suppliers"]["supplier_contacts"].items():
        if contact.get("external_id") == external_id:
            contact_id_to_delete = contact_id
            break
    if contact_id_to_delete is None:
        return {"error": "Contact not found"}, 404
    del db.DB["suppliers"]["supplier_contacts"][contact_id_to_delete]
    return {}, 204 