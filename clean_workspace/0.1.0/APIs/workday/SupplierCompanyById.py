"""
Supplier Company Management by ID Module

This module provides functionality for managing individual supplier companies using
their unique internal identifiers in the Workday Strategic Sourcing system. It
supports operations for retrieving, updating, and deleting supplier company records.

The module interfaces with the simulation database to provide comprehensive supplier
company management capabilities, allowing users to:
- Retrieve detailed supplier company information
- Update existing supplier company records
- Delete supplier company entries
- Handle related resource inclusion where applicable

Functions:
    get: Retrieves supplier company details by ID
    patch: Updates supplier company details by ID
    delete: Deletes a supplier company by ID
"""

from typing import Dict, Any, Optional, Tuple, Union
from .SimulationEngine import db

def get(id: int, _include: Optional[str] = None) -> Tuple[Union[Dict[str, Any], Dict[str, str]], int]:
    """
    Retrieves the details of an existing supplier company.

    This function fetches all metadata and linked relationships for a supplier
    company using its unique identifier. Related resources can optionally be
    included using the `include` query parameter.

    Args:
        id (int): Required. Unique identifier of the supplier company.
            Example: 1

        _include (Optional[str]): Comma-separated list of related resources to include.
            Allowed values:
                - "attachments"
                - "supplier_category"
                - "supplier_groups"
                - "default_payment_term"
                - "payment_types"
                - "default_payment_type"
                - "payment_currencies"
                - "default_payment_currency"
                - "supplier_classification_values"

    Returns:
        Tuple[Union[Dict[str, Any], Dict[str, str]], int]: A tuple containing the supplier company details or an error message and the HTTP status code.
            If successful:
                - First element (Dict[str, Any]):
                    - type (str): Always "supplier_companies".
                    - id (int): Unique supplier company ID.
                    - attributes (Dict[str, Any]):
                        - name (str): Supplier company name (≤ 255 characters).
                        - description (Optional[str]): Company description.
                        - is_suggested (bool): True if the supplier was suggested.
                        - public (bool): Indicates if the supplier is public.
                        - risk (Optional[str]): Supplier risk slug value.
                        - segmentation (Optional[str]): Segmentation slug.
                        - segmentation_status (Optional[str]): Segmentation status slug.
                        - segmentation_notes (Optional[str]): Notes regarding segmentation.
                        - tags (List[str]): List of tags.
                        - url (Optional[str]): Supplier website URL.
                        - duns_number (Optional[str]): D-U-N-S® number.
                        - external_id (Optional[str]): Internal database ID.
                        - self_registered (bool): Indicates self-registration status.
                        - onboarding_form_completion_status (Optional[str]):
                            One of: null, 'not_started', 'in_progress', 'completed'
                        - accept_all_currencies (bool): Whether all currencies are accepted.
                        - updated_at (str): ISO date-time of last modification.
    
                        - custom_fields (List[Dict[str, Any]]): List of custom field entries. Each entry can be of multiple supported types.
                            Note: File-type custom fields are only accessible via UI and return `null` in the API.

                            Supported types include:
                                - Checkbox
                                - Short Text
                                - Paragraph
                                - Date
                                - Integer
                                - Currency
                                - Decimal
                                - Single Select
                                - Multiple Select
                                - URL
                                - Lookup
                                - Related

                            Shared structure for each field:
                                - name (str): Name of the custom field.
                                - value (Union[str, int, float, bool, List[Any], None]): Value of the custom field, type varies depending on field kind.


                    - relationships (Dict[str, Any]):
                        - supplier_category
                        - supplier_groups
                        - default_payment_term
                        - payment_types
                        - default_payment_type
                        - payment_currencies
                        - default_payment_currency
                        - attachments
                        - supplier_classification_values

                - Second element (int):
                    - HTTP status code: 200.
                    
            - If error:
                - First element (Dict[str, str]):
                    - error (str): Error message.
                - Second element (int):
                    - HTTP status code: 404.
    """

    company = db.DB["suppliers"]["supplier_companies"].get(id)
    if not company:
        return {"error": "Company not found"}, 404
    if _include:
        # Simulate include logic (not fully implemented)
        pass
    return company, 200

def patch(id: int, _include: Optional[str] = None, 
          body: Optional[Dict[str, Any]] = None) -> Tuple[Union[Dict[str, Any], Dict[str, str]], int]:
    """
    Updates the details of an existing supplier company.

    This endpoint allows modification of a supplier company's attributes and relationships. You must provide the unique identifier of the supplier company (same as in the path) in the request body. When updating relationships, the entire existing relationship is replaced by the provided values.

    Args:
        id (int): Required. Unique identifier of the supplier company.
            Example: 1

        _include (Optional[str]): Comma-separated list of related resources to include in the response.
            Allowed values:
                - "attachments"
                - "supplier_category"
                - "supplier_groups"
                - "default_payment_term"
                - "payment_types"
                - "default_payment_type"
                - "payment_currencies"
                - "default_payment_currency"
                - "supplier_classification_values"

        body (Optional[Dict[str, Any]]): SupplierCompanyUpdate object containing:
            - type (str): Must be "supplier_companies".
            - id (int): Supplier company ID (must match the path parameter).

            - attributes (Dict[str, Any]):
                - name (str): Required. Name of the supplier (≤ 255 characters).
                - description (Optional[str]): Company description.
                - public (bool): Whether the company is publicly listed.
                - risk (Optional[str]): Risk slug defined by your organization.
                - segmentation (Optional[str]): Segmentation slug.
                - segmentation_status (Optional[str]): Segmentation status slug.
                - segmentation_notes (Optional[str]): Notes about the segmentation.
                - tags (List[str]): Tags assigned to the supplier.
                - url (Optional[str]): Website of the supplier.
                - duns_number (Optional[str]): D-U-N-S® Number.
                - external_id (Optional[str]): Your internal system ID for the supplier.
                - self_registered (bool): Whether the supplier self-registered.
                - onboarding_form_completion_status (str): One of: null, 'not_started', 'in_progress', 'completed'.
                - accept_all_currencies (bool): Whether all currencies are accepted.
                - custom_fields (List[Dict[str, Any]]): List of custom field entries. Each entry can be of multiple supported types.
                    Note: File-type custom fields are only accessible via UI and return `null` in the API.

                    Supported types include:
                        - Checkbox
                        - Short Text
                        - Paragraph
                        - Date
                        - Integer
                        - Currency
                        - Decimal
                        - Single Select
                        - Multiple Select
                        - URL
                        - Lookup
                        - Related

            - relationships (Dict[str, Any]): Supplier relationships (replaces existing data).
                - supplier_category
                - supplier_groups
                - default_payment_term
                - payment_types
                - default_payment_type
                - payment_currencies
                - default_payment_currency
                - attachments
                - supplier_classification_values

            - external_*: You may use external references for relationships using external_* keys.
                - external_supplier_category
                - external_supplier_groups
                - external_default_payment_term
                - external_payment_types
                - external_default_payment_type
                - external_payment_currencies
                - external_default_payment_currency
                - external_supplier_classification_values

    Returns:
        Tuple[Union[Dict[str, Any], Dict[str, str]], int]: A tuple containing:
            - Union[Dict[str, Any], Dict[str, str]]: Either the updated supplier company data or an error message.
                If successful, contains:
                    - data (Dict[str, Any]):
                        - type (str): Always "supplier_companies".
                        - id (int): Supplier company ID.
                        - attributes (Dict[str, Any]):
                            - name (str)
                            - description (Optional[str])
                            - is_suggested (bool)
                            - public (bool)
                            - risk (Optional[str])
                            - segmentation (Optional[str])
                            - segmentation_status (Optional[str])
                            - segmentation_notes (Optional[str])
                            - tags (List[str])
                            - url (Optional[str])
                            - duns_number (Optional[str])
                            - external_id (Optional[str])
                            - self_registered (bool)
                            - onboarding_form_completion_status (str)
                            - accept_all_currencies (bool)
                            - updated_at (str): ISO timestamp
                            - custom_fields (List[Dict[str, Any]]): Same as in request
                        - relationships (Dict[str, Any]): All linked resources included.
                    - links (Dict[str, str]):
                        - self (str): Link to the resource.
                If error, contains error message.
            - int: HTTP status code (200 for success, 400, 401, 404, or 409 for errors).
    """

    company = db.DB["suppliers"]["supplier_companies"].get(id)
    if not company:
        return {"error": "Company not found"}, 404
    if not body:
        return {"error": "Body is required"}, 400
    company.update(body)
    if _include:
        # Simulate include logic (not fully implemented)
        pass
    return company, 200

def delete(id: int) -> Tuple[Union[Dict[str, Any], Dict[str, str]], int]:
    """
    Deletes a supplier company by its unique identifier.

    This operation permanently removes the supplier company record from the system.
    You must provide the supplier company ID that was returned upon its creation.

    Args:
        id (int): Required. Unique Supplier Company identifier.
            Example: 1

    Returns:
        Tuple[Union[Dict[str, Any], Dict[str, str]], int]: A tuple containing an empty dictionary and the HTTP status code.
            If successful:
                - First element (Dict[str, Any]):
                    - Empty dictionary.
                - Second element (int):
                    - HTTP status code: 204.
            If error:
                - First element (Dict[str, str]):
                    - error (str): Error message.
                - Second element (int):
                    - HTTP status code: 404.
    """

    if id not in db.DB["suppliers"]["supplier_companies"]:
        return {"error": "Company not found"}, 404
    del db.DB["suppliers"]["supplier_companies"][id]
    return {}, 204 