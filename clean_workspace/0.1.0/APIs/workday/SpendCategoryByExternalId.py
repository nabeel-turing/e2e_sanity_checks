"""
Spend Category Management by External ID Module

This module provides functionality for managing spend categories using their external
identifiers in the Workday Strategic Sourcing system. It supports operations for
retrieving, updating, and deleting spend category details using external IDs.

The module interfaces with the simulation database to provide comprehensive spend
category management capabilities, allowing users to perform CRUD operations on spend
categories using their external IDs. This is particularly useful when integrating
with external systems that maintain their own spend category identifiers.

Functions:
    get: Retrieves spend category details by external ID
    patch: Updates spend category details by external ID
    delete: Deletes a spend category by external ID
"""

from typing import Dict, Any, Optional, List
from .SimulationEngine import db

def get(external_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves the details of a specific spend category by its unique identifier.

    Spend categories define classification for various types of organizational spend such as procurement, expenses, supplier invoices, etc.

    Args:
        external_id (str): Unique identifier of the spend category.

    Returns:
        Optional[Dict[str, Any]]: A spend category object including its attributes.

            - data (Dict[str, Any]):
                - type (str): Always "spend_categories".
                - id (str): Unique identifier of the spend category.
                - attributes (Dict[str, Any]):
                    - name (str): Spend category name.
                    - external_id (str): Optional. External system identifier (max 255 characters).
                    - usages (List[str]): Applicable usage contexts for this category.
                        - Enum: "procurement", "expense", "ad_hoc_payment", "supplier_invoice"

    Raises:
        HTTPError 401: Unauthorized – API credentials are missing or invalid.
        HTTPError 404: Not Found – No spend category found with the provided ID.
    """

    for category in db.DB["spend_categories"].values():
        if category.get("external_id") == external_id:
            return category
    return None

def patch(external_id: str, name: Optional[str] = None, new_external_id: Optional[str] = None, 
          usages: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
    """
    Updates an existing spend category with new attributes.

    The spend category must be identified by its unique ID (same as provided in the path). Only fields passed in the payload will be updated; others remain unchanged.

    Args:
        external_id (str): Unique identifier of the spend category to update.
        name (Optional[str]): Optional. Spend category name (max 255 characters).
        new_external_id (Optional[str]): Optional. External system ID (max 255 characters).
        usages (Optional[List[str]]): Optional. Applicable contexts.
            - Enum: "procurement", "expense", "ad_hoc_payment", "supplier_invoice"
                - name (str): Optional. Spend category name (max 255 characters).
                - external_id (str): Optional. External system ID (max 255 characters).
                - usages (List[str]): Optional. Applicable contexts.
                    - Enum: "procurement", "expense", "ad_hoc_payment", "supplier_invoice"

    Returns:
        Optional[Dict[str, Any]]: Updated spend category object.
            - data (Dict[str, Any]):
                - type (str): "spend_categories"
                - id (str): Spend category ID.
                - attributes (Dict[str, Any]):
                    - name (str): Spend category name.
                    - external_id (str): External system ID.
                    - usages (List[str]): Usage contexts.

    Raises:
        HTTPError 401: Unauthorized – Missing or invalid credentials.
        HTTPError 404: Not Found – No spend category found with the given ID.
        HTTPError 409: Conflict – Conflict during update (e.g., duplicate external ID).
    """

    for id, category in db.DB["spend_categories"].items():
        if category.get("external_id") == external_id:
            if name is not None:
                category["name"] = name
            if new_external_id is not None:
                category["external_id"] = new_external_id
            if usages is not None:
                category["usages"] = usages
            return category
    return None

def delete(external_id: str) -> bool:
    """
    Deletes an existing spend category by its unique identifier.

    The identifier must match the one returned during spend category creation. This operation is irreversible and will permanently remove the category.

    Args:
        external_id (str): Unique ID of the spend category to delete.

    Returns:
        bool: Returns HTTP 204 No Content on successful deletion.

    Raises:
        HTTPError 401: Unauthorized – API credentials are missing or invalid.
        HTTPError 404: Not Found – No spend category found with the provided ID.
    """

    for id, category in db.DB["spend_categories"].items():
        if category.get("external_id") == external_id:
            del db.DB["spend_categories"][id]
            return True
    return False 