"""
Supplier Company Contacts Management Module

This module provides functionality for managing contacts associated with supplier
companies in the Workday Strategic Sourcing system. It supports operations for
retrieving and filtering contacts for a specific supplier company.

The module interfaces with the simulation database to provide comprehensive contact
management capabilities, allowing users to:
- Retrieve all contacts for a specific supplier company
- Filter contacts based on specific criteria
- Include related resources in the response
"""

from typing import Dict, Any, Optional, List, Tuple
from .SimulationEngine import db

def get(company_id: int, _include: Optional[str] = None, 
        filter: Optional[Dict[str, Any]] = None) -> Tuple[List[Dict[str, Any]], int]:
    """
    Retrieves a list of contacts for a specific supplier company.

    This function returns supplier contacts associated with a given supplier company ID.
    Supports detailed filtering, relationship includes, and pagination options.

    Args:
        company_id (int): Required. Unique identifier of the supplier company.
            Example: 1

        _include (Optional[str]): Comma-separated list of related resources to include in the response.
            Allowed values:
                - "supplier_company"
                - "contact_types"
                - "phones"

        filter (Optional[Dict[str, Any]]): Dictionary of filter parameters to narrow down contact results.
            Supported filters include:
                - updated_at_from (str): Return contacts updated on or after this timestamp.
                - updated_at_to (str): Return contacts updated on or before this timestamp.
                - name_contains / name_not_contains (str)
                - first_name_contains / first_name_not_contains (str)
                - last_name_contains / last_name_not_contains (str)
                - email_equals / email_not_equals / email_contains / email_not_contains (str)
                - phone_number_contains / phone_number_not_contains (str)
                - phone_number_empty / phone_number_not_empty (bool)
                - job_title_contains / job_title_not_contains (str)
                - job_title_empty / job_title_not_empty (bool)
                - notes_contains / notes_not_contains (str)
                - notes_empty / notes_not_empty (bool)
                - is_suggested_equals / is_suggested_not_equals (bool)
                - external_id_equals / external_id_not_equals (str)
                - external_id_empty / external_id_not_empty (bool)

    Returns:
        Tuple[List[Dict[str, Any]], int]: A tuple containing:
            - First element (List[Dict[str, Any]]): A list of supplier contacts. It can contain the following keys:
                - type (str): Always "supplier_contacts".
                - id (int): Unique identifier of the contact.
                - attributes (Dict[str, Any]):
                    - name (str): Full name (≤ 255 characters).
                    - first_name (Optional[str]): First name.
                    - last_name (Optional[str]): Last name.
                    - email (str): Contact email (≤ 255 characters).
                    - notes (Optional[str]): Additional notes.
                    - phone_number (Optional[str]): Deprecated field for phone.
                    - job_title (Optional[str]): Contact job title.
                    - external_id (Optional[str]): Internal system ID.
                    - is_suggested (bool): True if contact is a suggestion.
                    - updated_at (str): Last updated timestamp (ISO 8601).

                - relationships (Dict[str, Any]):
                    - supplier_company (Dict): Linked supplier company.
                        - data: { id (int), type (str) }
                    - contact_types (List[Dict]): Associated contact types.
                    - phones (List[Dict]): Linked phone numbers (max 1).

            - Second element (int): HTTP status code. It is 200 for success.

    """

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