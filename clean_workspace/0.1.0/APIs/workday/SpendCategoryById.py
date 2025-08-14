"""
Spend Category Management by ID Module

This module provides functionality for managing spend categories using their unique
internal identifiers in the Workday Strategic Sourcing system. It supports operations
for retrieving, updating, and deleting spend category details.

The module interfaces with the simulation database to provide comprehensive spend
category management capabilities, allowing users to perform CRUD operations on spend
categories using their internal IDs.

Functions:
    get: Retrieves spend category details by ID
    patch: Updates spend category details by ID
    delete: Deletes a spend category by ID
"""

from typing import Dict, Any, Optional, List, Union
from .SimulationEngine import db

def get(id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieves the details of an existing spend category using its internal identifier.

    Internal IDs allow referencing spend categories directly in the database. This is useful for internal operations and direct database access.

    Args:
        id (int): Internal identifier of the spend category.

    Returns:
        Optional[Dict[str, Any]]: The spend category resource if found, None otherwise.
            - type (str): Always "spend_categories".
            - id (int): Unique internal ID.
            - attributes (Dict[str, Any]):
                - name (str): Name of the spend category.
                - external_id (str): External identifier.
                - usages (List[str]): List of usages.
                    - Enum: "procurement", "expense", "ad_hoc_payment", "supplier_invoice"
    """

    return db.DB["spend_categories"].get(id)

def patch(id: int, name: Optional[str] = None, external_id: Optional[str] = None, 
          usages: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
    """
    Updates the details of an existing spend category using its internal identifier.

    The internal ID must match the one provided in the URL path. All parameters are optional and only the provided fields will be updated.

    Args:
        id (int): Internal identifier for the spend category to be updated.
        name (Optional[str]): Updated name (max 255 characters).
        external_id (Optional[str]): New or same external identifier (max 255 characters).
        usages (Optional[List[str]]): Updated list of usages.
            - Enum: "procurement", "expense", "ad_hoc_payment", "supplier_invoice"

    Returns:
        Optional[Dict[str, Any]]: The updated spend category object if found, None otherwise.

            - data (Dict[str, Any]):
                - type (str): Always "spend_categories".
                - id (int): Unique internal ID.
                - attributes (Dict[str, Any]):
                    - name (str): Updated or existing name.
                    - external_id (str): External identifier.
                    - usages (List[str]): Allowed usages.
    """

    if id not in db.DB["spend_categories"]:
        return None
    category = db.DB["spend_categories"][id]
    if name is not None:
        category["name"] = name
    if external_id is not None:
        category["external_id"] = external_id
    if usages is not None:
        category["usages"] = usages
    return category

def delete(id: int) -> bool:
    """
    Deletes an existing spend category using its internal identifier.

    The internal ID must match the one provided in the URL path.

    Args:
        id (int): Internal identifier of the spend category to be deleted.

    Returns:
        bool: True if the spend category was deleted, False otherwise.
    """

    if id in db.DB["spend_categories"]:
        del db.DB["spend_categories"][id]
        return True
    return False 