"""
Supplier Company Contact Management by ID Module

This module provides functionality for managing individual contacts associated with
supplier companies in the Workday Strategic Sourcing system using their unique
identifiers. It supports operations for retrieving, updating, and deleting specific
contacts for a supplier company.

The module interfaces with the simulation database to provide comprehensive contact
management capabilities, allowing users to:
- Retrieve specific contact details by company and contact IDs
- Update existing contact information
- Delete contacts from the system
"""

from typing import Dict, Any, Optional, Tuple, Union
from .SimulationEngine import db

def get(company_id: int, contact_id: int, _include: Optional[str] = None) -> Tuple[Union[Dict[str, Any], Dict[str, str]], int]:
    """
    Retrieves the details of an existing supplier company contact.

    This function locates a specific contact using both the company ID and contact ID,
    then returns the complete contact details with optional related resource inclusion.

    Args:
        company_id (int): The unique identifier of the supplier company.
            This is the internal ID used by the system to reference the company.
        contact_id (int): The unique identifier of the contact.
            This is the internal ID used by the system to reference the contact.
        _include (Optional[str]): Comma-separated list of related resources to include
            in the response. Not fully implemented in simulation.

    Returns:
        Tuple[Union[Dict[str, Any], Dict[str, str]], int]: A tuple containing:
            - Dict[str, Any]: Contact details dictionary including:
                - "id" (int): The internal unique identifier
                - "company_id" (int): The ID of the associated supplier company
                - "name" (str): The contact's full name
                - "email" (str): The contact's email address
                - "phone" (Optional[str]): The contact's phone number
                - "role" (str): The contact's role in the company
                - "status" (str): The contact's status
                - Other contact-specific fields
            - int: HTTP status code (200 for success, 404 for not found)
            If contact not found, returns:
            - Dict[str, str]: Error message with key "error"
            - int: 404 status code
    """
    contact = next((c for c in db.DB["suppliers"]["supplier_contacts"].values() 
                   if c.get("company_id") == company_id and c.get("id") == contact_id), None)
    if not contact:
        return {"error": "Contact not found"}, 404
    if _include:
        # Simulate include logic (not fully implemented)
        pass
    return contact, 200

def patch(company_id: int, contact_id: int, _include: Optional[str] = None, 
          body: Optional[Dict[str, Any]] = None) -> Tuple[Union[Dict[str, Any], Dict[str, str]], int]:
    """
    Updates the details of an existing supplier company contact.

    This function allows modification of contact information by providing updated
    values for specific fields. The contact is identified by both company ID and
    contact ID.

    Args:
        company_id (int): The unique identifier of the supplier company.
            This is the internal ID used by the system to reference the company.
        contact_id (int): The unique identifier of the contact.
            This is the internal ID used by the system to reference the contact.
        _include (Optional[str]): Comma-separated list of related resources to include
            in the response. Not fully implemented in simulation.
        body (Optional[Dict[str, Any]]): Dictionary containing the fields to update.
            Required fields:
            - At least one field to update
            Optional fields:
            - "name" (str): The contact's full name
            - "email" (str): The contact's email address
            - "phone" (str): The contact's phone number
            - "role" (str): The contact's role in the company
            - "status" (str): The contact's status
            - Other contact-specific fields

    Returns:
        Tuple[Union[Dict[str, Any], Dict[str, str]], int]: A tuple containing:
            - Dict[str, Any]: Updated contact details dictionary
            - int: HTTP status code (200 for success, 400 for bad request, 404 for not found)
            If request body is missing, returns:
            - Dict[str, str]: Error message with key "error"
            - int: 400 status code
            If contact not found, returns:
            - Dict[str, str]: Error message with key "error"
            - int: 404 status code
    """
    if not body:
        return {"error": "Request body is required"}, 400
    
    contact = next((c for c in db.DB["suppliers"]["supplier_contacts"].values() 
                   if c.get("company_id") == company_id and c.get("id") == contact_id), None)
    if not contact:
        return {"error": "Contact not found"}, 404
    
    # Update contact details
    for key, value in body.items():
        contact[key] = value
    
    if _include:
        # Simulate include logic (not fully implemented)
        pass
    return contact, 200

def delete(company_id: int, contact_id: int) -> Tuple[Optional[None], int]:
    """
    Deletes a supplier company contact.

    This function removes a specific contact from the system using both the company ID
    and contact ID for identification.

    Args:
        company_id (int): The unique identifier of the supplier company.
            This is the internal ID used by the system to reference the company.
        contact_id (int): The unique identifier of the contact.
            This is the internal ID used by the system to reference the contact.

    Returns:
        Tuple[Optional[None], int]: A tuple containing:
            - None: No content returned on successful deletion
            - int: HTTP status code (204 for success, 404 for not found)
            If contact not found, returns:
            - Dict[str, str]: Error message with key "error"
            - int: 404 status code
    """
    contact = next((c for c in db.DB["suppliers"]["supplier_contacts"].values() 
                   if c.get("company_id") == company_id and c.get("id") == contact_id), None)
    if not contact:
        return {"error": "Contact not found"}, 404
    
    # Remove contact from database
    del db.DB["suppliers"]["supplier_contacts"][str(contact_id)]
    return None, 204 