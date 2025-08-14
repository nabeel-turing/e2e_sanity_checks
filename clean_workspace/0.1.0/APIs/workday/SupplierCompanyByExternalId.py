"""
Supplier Company Management by External ID Module

This module provides functionality for managing supplier companies using their external
identifiers in the Workday Strategic Sourcing system. It supports operations for
retrieving, updating, and deleting supplier company records using external IDs.

The module interfaces with the simulation database to provide comprehensive supplier
company management capabilities, particularly useful when integrating with external
systems that maintain their own identifiers. It allows users to:
- Retrieve detailed supplier company information using external IDs
- Update existing supplier company records with external ID validation
- Delete supplier company entries by external ID
- Handle related resource inclusion where applicable

Functions:
    get: Retrieves supplier company details by external ID
    patch: Updates supplier company details by external ID
    delete: Deletes a supplier company by external ID
"""

from typing import Dict, Any, Optional, Tuple, Union
from .SimulationEngine import db

def get(external_id: str, _include: Optional[str] = None) -> Tuple[Union[Dict[str, Any], Dict[str, str]], int]:
    """
    Retrieves a supplier company using its external identifier.

    This endpoint fetches the details of a supplier company by its unique external ID. Related resources can be included using the `include` query parameter.

    Args:
        external_id (str): Required. The external identifier of the supplier company. Example: "1234-5678-abcd-efgh"
        _include (Optional[str]): Comma-separated list of related resources to include in the response. 
            Enum values:
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
                    - type (str): Resource object type, always "supplier_companies".
                    - id (int): Internal identifier of the supplier company.
                    - attributes (Dict[str, Any]): Supplier company metadata.
                        - name (str): Company name.
                        - description (str): Optional company description.
                        - is_suggested (bool): True if suggested by a user but not approved.
                        - public (bool): Indicates if the company is public.
                        - risk (str): Supplier risk (slug from risk object).
                        - segmentation (str): Supplier segmentation (slug from segmentation object).
                        - segmentation_status (str): Segmentation status (slug from segmentation status object).
                        - segmentation_notes (str): Notes related to segmentation.
                        - tags (List[str]): List of user-defined tags.
                        - url (str): Supplier’s website URL.
                        - duns_number (str): D-U-N-S® Number.
                        - external_id (str): External system identifier.
                        - self_registered (bool): True if registered via self-service.
                        - onboarding_form_completion_status (str): Status of onboarding form. Values: null, 'not_started', 'in_progress', 'completed'.
                        - accept_all_currencies (bool): True if all currencies are accepted.
                        - updated_at (str): Last updated timestamp (ISO format).
                        - custom_fields (List[Dict[str, Any]]): List of custom fields.
                            Each field has:
                                - name (str): Field name.
                                - value (Any): Field value depending on type.
                            Supported types:
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
                            Note: File-type custom fields are only accessible via UI and return `null`.

                    - relationships (Dict[str, Any]): Linked resources.
                        - supplier_category (Dict): Assigned category.
                            - data:
                                - type (str): Always "supplier_categories".
                                - id (int): Category ID.
                        - supplier_groups (Dict): Groups assigned to the supplier.
                            - data (List[Dict[str, Any]]): Each with type "supplier_groups" and an integer ID.
                        - default_payment_term, default_payment_type, default_payment_currency (Dict): Payment defaults.
                            - data:
                                - type (str): One of "payment_terms", "payment_types", or "payment_currencies".
                                - id (int): Resource ID.
                        - payment_types, payment_currencies (Dict): Accepted payments.
                            - data (List[Dict]): List of accepted payment method/currency objects.
                        - attachments (List[Dict]): List of attachments.
                            - Each attachment has:
                                - type (str): "attachments"
                                - id (int): Attachment ID.
                        - supplier_classification_values (List[Dict]): Classification values.
                            - Each item:
                                - type (str): "supplier_classification_values"
                                - id (str): Composite ID from supplier and classification.

                    - links (Dict[str, str]): Navigation URLs.
                        - self (str): Canonical URL of the resource.
                - Second element(int):
                    - HTTP status code: 200.

            If error:
                - First element (Dict[str, str]):
                    - error (str): Error message.
                - Second element (int):
                    - HTTP status code: 404.

    """

    for company in db.DB["suppliers"]["supplier_companies"].values():
        if company.get("external_id") == external_id:
            if _include:
                #simulate include
                pass
            return company, 200
    return {"error": "Company not found"}, 404

def patch(external_id: str, _include: Optional[str] = None, 
          body: Optional[Dict[str, Any]] = None) -> Tuple[Union[Dict[str, Any], Dict[str, str]], int]:
    """
    Updates an existing supplier company using its external identifier.

    This endpoint allows updating a supplier company's attributes and relationships using its external ID. The request body must include an `id` that matches the identifier in the path.

    Args:
        external_id (str): Required. External identifier of the supplier company (e.g., "1234-5678-abcd-efgh").
        _include (Optional[str]): Comma-separated list of related resources to include in the response.
            Enum values:
            - "attachments"
            - "supplier_category"
            - "supplier_groups"
            - "default_payment_term"
            - "payment_types"
            - "default_payment_type"
            - "payment_currencies"
            - "default_payment_currency"
            - "supplier_classification_values"
        body (Optional[Dict[str, Any]]): The payload used to update the supplier company.
            - type (str): Must be "supplier_companies".
            - id (int): Supplier company ID.
            - attributes (dict): Fields to update.
                - name (str): Required. Company name (max 255 characters).
                - description (str): Optional description.
                - public (bool): Visibility of the company.
                - risk (str): Slug value for company risk.
                - segmentation (str): Slug value for segmentation.
                - segmentation_status (str): Slug value for segmentation status.
                - segmentation_notes (str): Notes for segmentation.
                - tags (List[str]): Tags for classification.
                - url (str): Supplier's website.
                - duns_number (str): D-U-N-S® Number.
                - external_id (str): Custom external ID.
                - self_registered (bool): Whether the supplier self-registered.
                - onboarding_form_completion_status (str): Onboarding progress: null, 'not_started', 'in_progress', 'completed'.
                - accept_all_currencies (bool): If all currencies are accepted.
                - custom_fields (List[dict]): List of custom fields.
                    - name (str): Name of the custom field.
                    - value (Any): Value, based on field type.
                    Supported types:
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
                    Note: File fields are UI-only and return `null`.

            - relationships (dict): Updated linked resources.
                - supplier_category, external_supplier_category (dict): Supplier category by ID or external ID.
                - supplier_groups, external_supplier_groups (List[dict]): Group associations by ID or external ID.
                - default_payment_term, external_default_payment_term (dict): Default payment term by ID or external ID.
                - payment_types, external_payment_types (List[dict]): Accepted payment types.
                - default_payment_type, external_default_payment_type (dict): Default payment method.
                - payment_currencies, external_payment_currencies (List[dict]): Accepted currencies.
                - default_payment_currency, external_default_payment_currency (dict): Default currency.
                - attachments (List[dict]): Attachments (ID + type = "attachments").
                - supplier_classification_values, external_supplier_classification_values (List[dict]): Classification values.

    Returns:
        Tuple[Union[Dict[str, Any], Dict[str, str]], int]: A tuple containing:
            - First element: A dictionary representing the updated supplier company or error message.
                - type (str): Always "supplier_companies".
                - id (int): Internal identifier of the supplier company.
                - attributes (dict): Updated values for the company (same as described in body).
                - relationships (dict): Updated linked resources (same structure as described above).
                - links (dict):
                    - self (str): Canonical link to the resource.
            - Second element: HTTP status code (200 for success, 400 for bad request, 404 for not found).
    """

    for company_id, company in db.DB["suppliers"]["supplier_companies"].items():
        if company.get("external_id") == external_id:
            if not body:
                return {"error": "Body is required"}, 400
            if body.get("id") != external_id:
                return {"error": "External id in body must match url"}, 400

            company.update(body)
            if _include:
                #simulate include
                pass
            return company, 200
    return {"error": "Company not found"}, 404

def delete(external_id: str) -> Tuple[Union[Dict[str, Any], Dict[str, str]], int]:
    """
    Deletes a supplier company using its external identifier.

    This operation permanently deletes an existing supplier company. You must provide the external identifier used during the supplier company’s creation.

    Args:
        external_id (str): Required. The external ID of the supplier company to delete.
            Example: "1234-5678-abcd-efgh"

    Returns:
        Tuple[Union[Dict[str, Any], Dict[str, str]], int]: A tuple containing an empty or error dictionary and the HTTP status code.
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

    company_id_to_delete = None
    for company_id, company in db.DB["suppliers"]["supplier_companies"].items():
        if company.get("external_id") == external_id:
            company_id_to_delete = company_id
            break
    if company_id_to_delete is None:
        return {"error": "Company not found"}, 404
    del db.DB["suppliers"]["supplier_companies"][company_id_to_delete]
    return {}, 204 