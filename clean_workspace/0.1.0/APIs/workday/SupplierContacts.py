"""
Supplier Contacts Management Module

This module provides functionality for managing supplier contacts in the Workday
Strategic Sourcing system. It supports operations for creating new supplier contact
records with custom attributes and relationships.

The module interfaces with the simulation database to provide supplier contact
management capabilities, allowing users to:
- Create new supplier contact records with custom attributes
- Support for related resource inclusion
- Maintain relationships with supplier companies
- Handle contact information and preferences

Functions:
    post: Creates a new supplier contact record
"""

from typing import Dict, Any, Union, List, Optional, Tuple
from .SimulationEngine import db

def post(_include: Optional[str] = None, body: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], int]:
    """
    Creates a new supplier contact with the provided attributes and relationships.

    This function links the contact to an existing supplier company by ID or external ID.
    You may also assign contact types and a phone reference. The response includes the
    full created contact object with all resolved relationships.

    Args:
        _include (Optional[str]): Comma-separated list of related resources to include in the response.
            Allowed values:
                - "supplier_company"
                - "contact_types"
                - "phones"

        body (Optional[Dict[str, Any]]): The supplier contact creation payload.
            - data (Dict[str, Any]):
                - type (str): Required. Must be "supplier_contacts".
                - attributes (Dict[str, Any]):
                    - name (str): Required unless first_name and last_name are provided. Full name (≤ 255 chars).
                    - first_name (Optional[str]): First name (≤ 255 chars).
                    - last_name (Optional[str]): Last name (≤ 255 chars).
                    - email (str): Required. Contact's email address (≤ 255 chars).
                    - notes (Optional[str]): Additional notes about the contact.
                    - phone_number (Optional[str]): Deprecated. Prefer the `phones` relationship.
                    - job_title (Optional[str]): Contact's job title.
                    - external_id (Optional[str]): Internal system reference.
                    - is_suggested (Optional[bool]): Whether the contact was suggested but unapproved.

                - relationships (Dict[str, Any]):
                    - supplier_company (Dict[str, Any]): Required. Link to a supplier company.
                        - data (Dict[str, Any]):
                            - id (Union[str, int]): Supplier company ID or external ID.
                            - type (str): Must be "supplier_companies".
                    - contact_types (Optional[Dict[str, Any]]):
                        - data (List[Dict[str, Any]]):
                            - id (int): Contact type ID.
                            - type (str): Must be "contact_types".
                    - phones (Optional[Dict[str, Any]]):
                        - data (List[Dict[str, Any]]): Maximum of one phone.
                            - id (int): Phone ID.
                            - type (str): Must be "phones".

    Returns:
        Tuple[Dict[str, Any], int]: A tuple containing:
            - Dictionary with the created supplier contact or error message
            - HTTP status code (201 for success, 400 for error)

            The contact dictionary structure:
            - data (Dict[str, Any]):
                - type (str): Always "supplier_contacts".
                - id (int): Unique identifier of the created contact.
                - attributes (Dict[str, Any]):
                    - name (str): Full name of the contact.
                    - first_name (Optional[str]): First name.
                    - last_name (Optional[str]): Last name.
                    - email (str): Email address.
                    - notes (Optional[str]): Notes field.
                    - phone_number (Optional[str]): Deprecated.
                    - job_title (Optional[str]): Job title.
                    - external_id (Optional[str]): External reference ID.
                    - is_suggested (Optional[bool]): If the contact was suggested.
                    - updated_at (str): Timestamp of last modification (ISO 8601).
                - relationships (Dict[str, Any]):
                    - supplier_company (Dict[str, Any]):
                        - data: { id (int), type (str) }
                    - contact_types (Optional[Dict[str, Any]]):
                        - data: List[{ id (int), type (str) }]
                    - phones (Optional[Dict[str, Any]]):
                        - data: List[{ id (int), type (str) }]
            - links (Dict[str, str]):
                - self (str): Link to the created resource.

    Raises:
        HTTPException: 401 Unauthorized if authentication credentials are missing or invalid.
    """

    if not body:
        return {"error": "Body is required"}, 400
    
    contact_id = len(db.DB["suppliers"]["supplier_contacts"]) + 1
    contact = {"id": contact_id, **body}
    db.DB["suppliers"]["supplier_contacts"][contact_id] = contact
    
    if _include:
        # Simulate include logic (not fully implemented)
        pass
    return contact, 201 