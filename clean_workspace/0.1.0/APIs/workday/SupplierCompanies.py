"""
Supplier Companies Management Module

This module provides functionality for managing supplier companies in the Workday
Strategic Sourcing system. It supports operations for retrieving and creating
supplier company records with various filtering, inclusion, and pagination options.

The module interfaces with the simulation database to provide comprehensive supplier
company management capabilities. It allows users to:
- Retrieve supplier companies with flexible filtering options
- Create new supplier company records with custom attributes
- Support for related resource inclusion and pagination
- Handle complex relationships and attributes

Functions:
    get: Retrieves supplier companies based on specified criteria
    post: Creates a new supplier company record
"""

from typing import Dict, Any, Optional, List, Tuple, Union
from .SimulationEngine import db

def get(filter: Optional[Dict[str, Any]] = None, _include: Optional[str] = None, 
        page: Optional[Dict[str, Any]] = None) -> Tuple[List[Dict[str, Any]], int]:
    """
    Retrieves a list of supplier companies matching the specified filters and options.

    Supports filtering, pagination, and compound document formatting via the `include` parameter to reduce multiple requests.

    Args:
        filter (Optional[Dict[str, Any]]): Filter supplier companies by criteria. One filter per attribute.
        _include (Optional[str]): Comma-separated list of related resources to include.
            - Enum: "attachments", "supplier_category", "supplier_groups", "default_payment_term",
                    "payment_types", "default_payment_type", "payment_currencies",
                    "default_payment_currency", "supplier_classification_values"
        page (Optional[Dict[str, Any]]): Pagination config.

    Returns:
        Tuple[List[Dict[str, Any]], int]: A tuple containing:
            - First element (List[Dict[str, Any]]): List of supplier companies with their attributes and relationships. Each company contains:
                - type (str): Always "supplier_companies".
                - id (int): Supplier company ID.
                - attributes (Dict[str, Any]): Core attributes of the company.
                    - name (str): Name of the supplier.
                    - description (str): Company description.
                    - is_suggested (bool): True if user-suggested, not yet approved.
                    - public (bool): True if publicly listed.
                    - risk (str): Risk slug from predefined values.
                    - segmentation (str): Segmentation slug.
                    - segmentation_status (str): Segmentation status slug.
                    - segmentation_notes (str): Notes related to segmentation.
                    - tags (List[str]): Tags associated with the supplier.
                    - url (str): Website URL.
                    - duns_number (str): D-U-N-S® identifier.
                    - external_id (str): External system identifier.
                    - self_registered (bool): True if registered by the supplier.
                    - onboarding_form_completion_status (str): Onboarding progress.
                        - Enum: null, 'not_started', 'in_progress', 'completed'
                    - accept_all_currencies (bool): True if accepts all currencies.
                    - updated_at (str): Last modified timestamp.
                    - custom_fields (List[Dict[str, Any]]): List of custom fields.
                        - name (str): Field name.
                        - value (Any): Field value.
                - relationships (Dict[str, Any]): Related entities.
                    - supplier_category
                    - supplier_groups
                    - default_payment_term
                    - payment_types
                    - default_payment_type
                    - payment_currencies
                    - default_payment_currency
                    - attachments
                    - supplier_classification_values
            - Second element (int): HTTP status code. It is 200 for success.
    """

    companies = list(db.DB["suppliers"]["supplier_companies"].values())
    if filter:
        filtered_companies = []
        for company in companies:
            match = True
            for key, value in filter.items():
                if company.get(key) != value:
                    match = False
                    break
            if match:
                filtered_companies.append(company)
        companies = filtered_companies
    if _include:
        # Simulate include logic (not fully implemented)
        pass
    if page:
        # Simulate pagination logic (not fully implemented)
        pass
    return companies, 200

def post(_include: Optional[str] = None, 
         body: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], int]:
    """
    Creates a new supplier company with specified attributes, linked resources, and optional custom fields.

    Supports internal and external ID references via `external_` prefixes for relationships. Allows compound creation via `include` parameter to return related resources in one request.

    Args:
        _include (Optional[str]): Comma-separated list of related resources to include in the response.
            - Enum: "attachments", "supplier_category", "supplier_groups", "default_payment_term",
                    "payment_types", "default_payment_type", "payment_currencies",
                    "default_payment_currency", "supplier_classification_values"

        body (Optional[Dict[str, Any]]): Supplier company payload.
            - type (str): Must be "supplier_companies".
            - attributes (dict): It can contain the following keys:
                - name (str): Required. Supplier company name.
                - description (str): Optional. Company description.
                - public (bool): Optional. Whether the company is public.
                - risk (str): Optional. Risk classification (slug).
                - segmentation (str): Optional. Segmentation type (slug).
                - segmentation_status (str): Optional. Segmentation status (slug).
                - segmentation_notes (str): Optional. Notes for segmentation.
                - tags (List[str]): Optional. Associated tags.
                - url (str): Optional. Supplier website.
                - duns_number (str): Optional. D-U-N-S® number.
                - external_id (str): Optional. Internal database ID.
                - self_registered (bool): Optional. Whether supplier self-registered.
                - onboarding_form_completion_status (str): Optional. Onboarding status.
                    - Enum: null, "not_started", "in_progress", "completed"
                - accept_all_currencies (bool): Optional. Accepts all currencies.
                - custom_fields (List[dict]): Optional. List of custom fields.
                    - name (str): Field name.
                    - value (Any): Field value.
                    - Supported types: "Checkbox", "Short Text", "Paragraph", "Date", "Integer",
                                       "Currency", "Decimal", "Single Select", "Multiple Select",
                                       "URL", "Lookup", "Related"
            - relationships (Dict[str, Any]): Resource links (optional).
                - supplier_category
                - supplier_groups
                - default_payment_term
                - payment_types
                - default_payment_type
                - payment_currencies
                - default_payment_currency
                - attachments
                - supplier_classification_values

            - external_... (dict or list): Use `external_` prefix for external ID references.
                - external_supplier_category
                - external_supplier_groups
                - external_default_payment_term
                - external_payment_types
                - external_default_payment_type
                - external_payment_currencies
                - external_default_payment_currency
                - external_supplier_classification_values

    Returns:
        Tuple[Dict[str, Any], int]: A tuple containing:
            - First element (Dict[str, Any]): The created supplier company.
            - Second element (int): HTTP status code. It is 201 for successful creation, 400 for bad request.

            If Success, First element is a dictionary containing the created supplier company.
                - id (int): Unique supplier company identifier.
                - type (str): Always "supplier_companies".
                - attributes (Dict[str, Any]):
                    - name (str)
                    - description (str)
                    - is_suggested (bool)
                    - public (bool)
                    - risk (str)
                    - segmentation (str)
                    - segmentation_status (str)
                    - segmentation_notes (str)
                    - tags (List[str])
                    - url (str)
                    - duns_number (str)
                    - external_id (str)
                    - self_registered (bool)
                    - onboarding_form_completion_status (str)
                    - accept_all_currencies (bool)
                    - updated_at (str)
                    - custom_fields (List[dict]):
                        - name (str)
                        - value (Any)
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
            If Error, First element is a dictionary containing the error message.  
                - error (str): Error message.
    """


    if not body:
        return {"error": "Body is required"}, 400
    company_id = len(db.DB["suppliers"]["supplier_companies"]) + 1
    company = {"id": company_id, **body}
    db.DB["suppliers"]["supplier_companies"][company_id] = company
    if _include:
        # Simulate include logic (not fully implemented)
        pass
    return company, 201 