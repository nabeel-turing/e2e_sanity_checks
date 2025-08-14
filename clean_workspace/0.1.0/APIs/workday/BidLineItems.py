"""
This module provides functionality for managing bid line items in the Workday Strategic Sourcing system.
It supports operations for retrieving line items associated with specific bids, enabling detailed
analysis and management of bid components.
"""

from .SimulationEngine import db

def get(bid_id: int) -> list:
    """Returns a list of line items associated with a specific bid.

    This function returns all line items that are linked to the specified bid ID,
    allowing for detailed analysis of bid components and their associated data.

    Args:
        bid_id (int): The unique identifier of the bid for which to retrieve line items.

    Returns:
        list: A list of dictionaries, where each dictionary represents a line item
            associated with the specified bid. Each line item includes any of the following keys:
                - "type" (str): Object type, should always be "bid_line_items"
                - "id" (int): The unique identifier of the bid line item
                - "bid_id" (int): The ID of the associated bid
                - "event_id" (int): The ID of the associated event
                - "description" (str): Description of the line item
                - "amount" (float): The amount of the bid line item
                - "attributes" (dict): Bid line item attributes containing:
                    - "data" (dict): A hashmap where keys are data identifier strings for worksheet columns and values are cell values
                        - "data_identifier" (str): Worksheet column identifier string
                        - "value" (any): Bid line item cell value
                    - "updated_at" (str): Last modification date in ISO 8601 format
                - "relationships" (dict): Bid line item relationships containing:
                    - "event" (dict): Associated event with:
                        - "type" (str): Always "events"
                        - "id" (int): Event identifier
                    - "bid" (dict): Associated bid with:
                        - "type" (str): Always "bids"
                        - "id" (int): Bid identifier
                    - "line_item" (dict): Associated line item with:
                        - "type" (str): Always "line_items"
                        - "id" (int): Line item identifier
                    - "worksheets" (dict): Associated worksheet with:
                        - "type" (str): Always "worksheets"
                        - "id" (int): Worksheet identifier
                - Any other bid line item-specific attributes as defined in the system
            
            If not found, returns an empty list.

    Note:
        The function returns an empty list if no line items are found for the specified bid.
    """
    return [item for item in db.DB["events"]["bid_line_items"].values() if item.get("bid_id") == bid_id]
