"""
This module provides functionality for managing contract awards and their associated
line items in the Workday Strategic Sourcing system. It supports operations for
retrieving award details, listing awards, and managing award line items. The module
enables comprehensive contract award tracking and management capabilities.
"""

from typing import List, Dict, Optional
from .SimulationEngine import db

def list_awards() -> List[Dict]:
    """Retrieves a list of all contract awards in the Workday Strategic Sourcing system.

    This function returns all available contract awards, providing comprehensive
    information about each award including their associated data and configurations.
    The function enables complete visibility into all awards and their current status.

    Returns:
        List[Dict]: A list of dictionaries, where each dictionary represents a
            contract award containing:
            - award_id (int): Unique identifier of the award
            - contract_id (int): ID of the associated contract
            - supplier_id (int): ID of the winning supplier
            - status (str): Current status of the award
            - award_date (str): Date of award issuance
            - start_date (str): Contract start date
            - end_date (str): Contract end date
            - total_value (float): Total award value
            - currency (str): Currency of the award value
            - created_at (str): Timestamp of award creation
            - updated_at (str): Timestamp of last update
            - metrics (Dict): Award-specific performance metrics
            - configurations (Dict): Award-specific settings and options
    """
    return list(db.DB["contracts"]["awards"].values())

def get_award(id: int) -> Dict:
    """Retrieves detailed information about a specific contract award.

    This function returns comprehensive information about a contract award,
    including all its associated data and configurations. The function provides
    complete visibility into award details and associated metrics.

    Args:
        id (int): The unique internal identifier of the award to retrieve.

    Returns:
        Dict: A dictionary containing all the details of the requested award,
            including:
            - award_id (int): Unique identifier of the award
            - contract_id (int): ID of the associated contract
            - supplier_id (int): ID of the winning supplier
            - status (str): Current status of the award
            - award_date (str): Date of award issuance
            - start_date (str): Contract start date
            - end_date (str): Contract end date
            - total_value (float): Total award value
            - currency (str): Currency of the award value
            - created_at (str): Timestamp of award creation
            - updated_at (str): Timestamp of last update
            - metrics (Dict): Award-specific performance metrics
            - configurations (Dict): Award-specific settings and options

    Raises:
        KeyError: If no award is found with the specified ID.

    Note:
        The returned data is read-only and should not be modified directly.
    """
    if id not in db.DB["contracts"]["awards"]:
        raise KeyError(f"Award with id {id} not found.")
    return db.DB["contracts"]["awards"][id]

def list_contract_award_line_items(award_id: int) -> List[Dict]:
    """Retrieves a list of line items associated with a specific contract award.

    This function returns all line items that are linked to the specified award ID,
    allowing for detailed analysis of award components and their associated data.
    The line items provide granular information about the award's components.

    Args:
        award_id (int): The unique identifier of the award for which to retrieve
            line items.

    Returns:
        List[Dict]: A list of dictionaries, where each dictionary represents a
            line item containing:
            - line_item_id (int): Unique identifier of the line item
            - award_id (int): ID of the associated award
            - item_name (str): Name of the line item
            - quantity (int): Quantity of items
            - unit_price (float): Price per unit
            - total_price (float): Total price for the line item
            - currency (str): Currency of the prices
            - description (str): Detailed description of the line item
            - created_at (str): Timestamp of line item creation
            - updated_at (str): Timestamp of last update

    Note:
        The function returns an empty list if no line items are found for the
        specified award. The returned data is read-only and should not be modified
        directly.
    """
    return [item for item in db.DB["contracts"]["award_line_items"] if item.get("award_id") == award_id]

def get_contract_award_line_item(id: str) -> Dict:
    """Retrieves detailed information about a specific award line item.

    This function returns comprehensive information about a contract award line
    item, including all its associated data and configurations. The function
    provides complete visibility into line item details and associated metrics.

    Args:
        id (str): The unique identifier of the award line item to retrieve.

    Returns:
        Dict: A dictionary containing all the details of the requested line item,
            including:
            - line_item_id (int): Unique identifier of the line item
            - award_id (int): ID of the associated award
            - item_name (str): Name of the line item
            - quantity (int): Quantity of items
            - unit_price (float): Price per unit
            - total_price (float): Total price for the line item
            - currency (str): Currency of the prices
            - description (str): Detailed description of the line item
            - created_at (str): Timestamp of line item creation
            - updated_at (str): Timestamp of last update
            - configurations (Dict): Line item-specific settings and options

    Raises:
        KeyError: If no award line item is found with the specified ID.

    Note:
        The returned data is read-only and should not be modified directly.
    """
    for item in db.DB["contracts"]["award_line_items"]:
        if item.get("id") == id:
            return item
    raise KeyError(f"Award line item with id {id} not found.") 