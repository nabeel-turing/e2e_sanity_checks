"""
Supplier Company Contacts Management by External ID Module

This module provides functionality for managing contacts associated with supplier
companies in the Workday Strategic Sourcing system using the company's external
identifier. It supports operations for retrieving and filtering contacts for a
specific supplier company.

The module interfaces with the simulation database to provide comprehensive contact
management capabilities, allowing users to:
- Retrieve all contacts for a specific supplier company using its external ID
- Filter contacts based on specific criteria
- Include related resources in the response
"""

from typing import Dict, Any, Optional, List, Tuple, Union
from .SimulationEngine import db

def get(external_id: str, _include: Optional[str] = None, 
        filter: Optional[Dict[str, Any]] = None) -> Tuple[Union[List[Dict[str, Any]], Dict[str, str]], int]:
    """
    Retrieves contacts associated with a supplier company by external identifier.

    This function returns all contacts for a specific supplier company and optionally
    filters them based on provided criteria. The external ID must match the one used
    when the company was created.

    Args:
        external_id (str): Required. External identifier of the supplier company.
            Example: "COMP-001"

        _include (Optional[str]): Comma-separated list of related resources to include.
            Currently not fully implemented.

        filter (Optional[Dict[str, Any]]): Optional filter criteria to apply to contacts.
            Each key-value pair in the dictionary will be used to filter contacts.

    Returns:
        Tuple[Union[List[Dict[str, Any]], Dict[str, str]], int]: A tuple containing:
            - First element (Union[List[Dict[str, Any]], Dict[str, str]]): Either a list of contact dictionaries or an error dictionary
            - Second element (int): HTTP status code (200 for success, 404 for not found)

            Contact dictionary structure:
                - id (int): Internal unique identifier of the contact
                - company_id (int): ID of the associated supplier company
                - name (str): Contact's full name
                - email (str): Contact's email address
                - phone (Optional[str]): Contact's phone number
                - title (Optional[str]): Contact's job title
                - active (bool): Whether the contact is active
    """

    company_id = None
    for company in db.DB["suppliers"]["supplier_companies"].values():
        if company.get("external_id") == external_id:
            company_id = company.get("id")
            break
    if company_id is None:
        return {"error": "Company not found"}, 404
    
    contacts = [c for c in db.DB["suppliers"]["supplier_contacts"].values() if c.get("company_id") == company_id]
    if filter:
        filtered_contacts = []
        for contact in contacts:
            match = True
            for key, value in filter.items():
                if contact.get(key) != value:
                    match = False
                    break
            if match:
                filtered_contacts.append(contact)
        contacts = filtered_contacts
    
    if _include:
        # Simulate include logic (not fully implemented)
        pass
    return contacts, 200 