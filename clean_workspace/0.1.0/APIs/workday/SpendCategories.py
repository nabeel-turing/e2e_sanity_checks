"""
Spend Categories Management Module

This module provides functionality for managing spend categories in the Workday Strategic
Sourcing system. It supports operations for retrieving all spend categories and creating
new spend category entries.

The module interfaces with the simulation database to maintain spend category data, which
is used to categorize and track spending across different areas of procurement and
supplier management.

Functions:
    get: Retrieves all spend categories
    post: Creates a new spend category
"""

from typing import List, Dict, Any, Optional
from .SimulationEngine import db

def get() -> List[Dict[str, Any]]:
    """
    Retrieves a list of spend categories.

    Allows listing of all available spend categories along with optional usage types. Categories can be used to group procurement, expenses, ad-hoc payments, and supplier invoices.

    Returns:
        List[Dict[str, Any]]: A paginated response containing spend categories.

            - data (List[Dict[str, Any]]): List of spend categories.
                - type (str): Always "spend_categories".
                - id (int): Spend category identifier.
                - attributes (dict):
                    - name (str): Name of the spend category.
                    - external_id (str): External system identifier for the spend category.
                    - usages (List[str]): Category usage contexts.
                        - Enum: "procurement", "expense", "ad_hoc_payment", "supplier_invoice"

            - meta (dict):
                - count (int): Number of result pages.

            - links (dict):
                - self (str): Link to current result set.
                - next (str|None): URL to next page of results.
                - prev (str|None): Deprecated. URL to previous page of results.
    """

    return list(db.DB["spend_categories"].values())

def post(name: str, external_id: Optional[str] = None, usages: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Creates a new spend category with specified attributes.

    Spend categories are used to classify spend for procurement, expense, ad-hoc payment, or supplier invoice use cases. Only categories with the "procurement" usage can be used in requisitions.

    Args:
        name (str): Required. Name of the spend category.
        external_id (Optional[str]): External identifier of the category (max 255 characters).
        usages (Optional[List[str]]): List of applicable usage contexts.
            - Allowed values: "procurement", "expense", "ad_hoc_payment", "supplier_invoice"

    Returns:
        Dict[str, Any]: A created spend category object containing:
            - type (str): Always "spend_categories".
            - id (int): Unique identifier of the spend category.
            - attributes (Dict[str, Any]):
                - name (str): Spend category name.
                - external_id (str): External system identifier.
                - usages (List[str]): Category usage types.
                    - Allowed values: "procurement", "expense", "ad_hoc_payment", "supplier_invoice"

    """

    new_id = len(db.DB["spend_categories"]) + 1
    new_category = {
        "id": new_id,
        "name": name,
        "external_id": external_id,
        "usages": usages,
    }
    db.DB["spend_categories"][new_id] = new_category
    return new_category 