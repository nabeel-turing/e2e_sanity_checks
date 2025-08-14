"""
This module provides functionality for retrieving and filtering bid line items in the
Workday Strategic Sourcing system. It supports comprehensive filtering capabilities
to enable precise retrieval of bid line items based on specific criteria.
"""

from .SimulationEngine import db

def get(filter: dict = None) -> list:
    """Returns a list of all bid line items.

    This function returns all bid line items in the system, with the option to
    filter the results based on specific criteria. 

    Args:
        filter (dict, optional): A dictionary containing field-value pairs to filter
            the bid line items. Each key in the dictionary represents a field name,
            and its corresponding value is the exact value to match.
            Example: {"bid_id": 123, "status": "active"}
            Defaults to None, which returns all bid line items.

    Returns:
        list: A list of dictionaries, where each dictionary represents a bid line item.
            Each bid line item contains its associated fields and values as defined
            in the system. If a filter is provided, only items matching all specified
            criteria are returned.
            The dictionary keys can be any of the following:
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
                

    Note:
        The filtering is case-sensitive and requires exact matches for all specified
        fields. If a field specified in the filter does not exist in a bid line item,
        that item will be excluded from the results.
    """
    items = list(db.DB["events"]["bid_line_items"].values())
    if filter:
        filtered_items = []
        for item in items:
            match = True
            for key, value in filter.items():
                if key not in item or item[key] != value:
                    match = False
                    break
            if match:
                filtered_items.append(item)
        items = filtered_items
    return items