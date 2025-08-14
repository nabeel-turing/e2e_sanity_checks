"""
This module provides functionality for managing awards and award line items in the Workday
Strategic Sourcing system. It supports operations for retrieving awards, filtering them
by various criteria, and managing award line items with their associated details.
"""

from typing import List, Dict, Any, Optional
from .SimulationEngine import db

def get(
    filter_state_equals: Optional[List[str]] = None,
    filter_updated_at_from: Optional[str] = None,
    filter_updated_at_to: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve a list of awards based on specified filter criteria.

    This function supports filtering awards by their state and update timestamps.
    Multiple filters can be combined to narrow down the results.

    Args:
        filter_state_equals (Optional[List[str]]): List of states to filter awards by.
            Valid states include: "draft" "confirmed" "awaiting_requisition_sync" "requisition_created".
        filter_updated_at_from (Optional[str]): Return awards updated on or after the specified timestamp..
        filter_updated_at_to (Optional[str]): Return awards updated on or before the specified timestamp.

    Returns:
        List[Dict[str, Any]]: A list of award dictionaries, where each award contains any of the following keys:
            - type (str): Object type, should always be "awards"
            - id (int): Unique identifier for the award
            - state (str): Current state of the award
            - updated_at (str): Timestamp of the last update
            - attributes (dict): Award attributes containing:
                - title (str): Award title (max 255 characters)
                - external_id (str): Award ID in your internal database (max 255 characters)
                - state (str): Award state, one of: "draft", "confirmed", "awaiting_requisition_sync", "requisition_created"
                - pros (str): Pros associated with award option
                - cons (str): Cons associated with award option
            - relationships (dict): Award relationships containing:
                - creator (dict): Project creator information
                - project (dict): Associated project information
            - links (dict): Related links containing:
                - self (str): URL to the resource
            - Other award-specific attributes as defined in the system
    """
    results = db.DB["awards"]["awards"][:]

    if filter_state_equals:
        results = [
            award
            for award in results
            if award.get("state") in filter_state_equals
        ]

    if filter_updated_at_from:
        results = [
            award
            for award in results
            if award.get("updated_at", "") >= filter_updated_at_from
        ]

    if filter_updated_at_to:
        results = [
            award
            for award in results
            if award.get("updated_at", "") <= filter_updated_at_to
        ]

    return results

def get_award_line_items(
    award_id: int,
    filter_is_quoted_equals: Optional[bool] = None,
    filter_line_item_type_equals: Optional[List[str]] = None,
    _include: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve line items associated with a specific award.

    Args:
        award_id (int): The unique identifier of the award to retrieve line items for.
        filter_is_quoted_equals (Optional[bool]): Filter line items by their quoted status.
            True for quoted items, False for non-quoted items.
        filter_line_item_type_equals (Optional[List[str]]): Return awards line items with specified line item types.
            Valid types include: "STANDARD", "GOODS", "SERVICES".
        _include (Optional[str]): Use the _include parameter to request related resources along with the primary resource.
            Supported includes: "supplier_company", "worksheet".

    Returns:
        List[Dict[str, Any]]: A list of award line item dictionaries, where each may contain any of the following keys:
            - type (str): Object type, always "award_line_items"
            - id (int): Unique identifier for the award line item
            - award_id (int): Associated award identifier
            - description (str): Description of the line item
            - amount (float): Amount of the award line item
            - attributes (dict): Award line item attributes containing:
                - data (dict): Worksheet column data with:
                    - data_identifier (str): Worksheet column identifier
                    - value (any): Cell value for the line item
                - allocated_quantity (int): Quantity allocated for the line item
                - sought_quantity (int): Quantity sought for the line item
                - price (float): Unit price of the line item
                - total_spend (float): Total spend for the line item
                - net_savings (float): Net savings amount
                - net_savings_percentage (float): Net savings as a percentage
                - line_item_type (str): Type of line item ("STANDARD", "GOODS", or "SERVICES")
                - is_quoted (bool): Whether the line item has been quoted
            - relationships (dict): Related resources containing:
                - supplier_company (dict): Associated supplier company with:
                    - type (str): Always "supplier_companies"
                    - id (int): Supplier company identifier
                - worksheet (dict): Associated worksheet with:
                    - type (str): Always "worksheets"
                    - id (int): Worksheet identifier
            - Any other award line item-specific attributes as defined in the system
    """
    results = [
        item
        for item in db.DB["awards"]["award_line_items"]
        if item.get("award_id") == award_id
    ]

    if filter_is_quoted_equals is not None:
        results = [
            item
            for item in results
            if item.get("is_quoted") == filter_is_quoted_equals
        ]

    if filter_line_item_type_equals:
        results = [
            item
            for item in results
            if item.get("line_item_type") in filter_line_item_type_equals
        ]

    if _include:
        # Simulate include logic
        pass

    return results

def get_award_line_item(
    id: str,
    _include: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Retrieve details of a specific award line item.

    Args:
        id (str): The unique identifier of the award line item to retrieve.
        _include (Optional[str]): Use the _include parameter to request related resources along with the primary resource.
            Supported includes: "supplier_company", "worksheet".

    Returns:
        Optional[Dict[str, Any]]: The award line item object if found, None otherwise.
            The object may contain any of the following keys:
            - type (str): Object type, always "award_line_items"
            - id (int): Unique identifier for the award line item
            - award_id (int): Associated award identifier
            - description (str): Description of the line item
            - amount (float): Amount of the award line item
            - attributes (dict): Award line item attributes containing:
                - data (dict): Worksheet column data with:
                    - data_identifier (str): Worksheet column identifier
                    - value (any): Cell value for the line item
                - allocated_quantity (int): Quantity allocated for the line item
                - sought_quantity (int): Quantity sought for the line item
                - price (float): Unit price of the line item
                - total_spend (float): Total spend for the line item
                - net_savings (float): Net savings amount
                - net_savings_percentage (float): Net savings as a percentage
                - line_item_type (str): Type of line item ("STANDARD", "GOODS", or "SERVICES")
                - is_quoted (bool): Whether the line item has been quoted
            - relationships (dict): Related resources containing:
                - supplier_company (dict): Associated supplier company with:
                    - type (str): Always "supplier_companies"
                    - id (int): Supplier company identifier
                - worksheet (dict): Associated worksheet with:
                    - type (str): Always "worksheets"
                    - id (int): Worksheet identifier
            - Any other award line item-specific attributes as defined in the system

    Raises:
        KeyError: If no award line item exists with the specified ID.
    """
    for item in db.DB["awards"]["award_line_items"]:
        if item.get("id") == id:
            if _include:
                # Simulate include logic
                pass
            return item
    return None 