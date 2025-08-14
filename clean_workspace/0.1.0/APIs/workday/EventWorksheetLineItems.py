"""
This module provides functionality for managing line items within event worksheets
in the Workday Strategic Sourcing system. It supports retrieving all line items
for a specific worksheet, creating individual line items, and bulk creating
multiple line items in a single operation.
"""

from typing import List, Dict, Optional
from .SimulationEngine import db

def get(event_id: int, worksheet_id: int) -> List[Dict]:
    """Returns a list of line items for the specified criteria.

    Args:
        event_id (int): The unique identifier of the event to which the line items belong.
        worksheet_id (int): The unique identifier of the worksheet to which the line items belong.

    Returns:
        List[Dict]: A list of dictionaries, where each dictionary represents a line item
            containing any of the following keys:
            - type (str): Object type, should always be "line_items"
            - id (int): LineItem identifier string
            - event_id (int): ID of the associated event
            - worksheet_id (int): ID of the associated worksheet
            - attributes (dict): LineItem attributes containing:
                - data (dict): A hashmap where keys are data identifier strings for the columns in the worksheet, and values are cell values, where each value contains:
                    - data_identifier (str): Worksheet column identifier string
                    - value (any): Worksheet line item cell value
    """
    line_items = []
    for id, line_item in db.DB["events"]["line_items"].items():
        if line_item["event_id"] == event_id and line_item["worksheet_id"] == worksheet_id:
            line_items.append(line_item)
    return line_items

def post(event_id: int, worksheet_id: int, data: Dict) -> Dict:
    """Create a line item with given cell values.

    Args:
        event_id (int): The unique identifier of the event to which the line item will belong.
        worksheet_id (int): The unique identifier of the worksheet to which the line item will belong.
        data (Dict): A dictionary containing the properties for the new line item, including:
            - type (str): Object type, should always be "line_items"
            - attributes (dict): LineItem attributes containing:
                - data (dict): A hashmap where keys are data identifier strings for the columns in the worksheet, and values are cell values, where each value contains:
                    - data_identifier (str): Worksheet column identifier string
                    - value (any): Worksheet line item cell value
            - relationships (dict): Line item relationships containing:
                - worksheet (dict): Associated worksheet containing:
                    - type (str): Object type, should always be "worksheets"
                    - id (int): Worksheet identifier string

    Returns:
        Dict: The created line item data, including:
            - type (str): Object type, should always be "line_items"
            - event_id (int): ID of the associated event
            - worksheet_id (int): ID of the associated worksheet
            - attributes (dict): LineItem attributes containing:
                - data (dict): A hashmap where keys are data identifier strings for the columns in the worksheet, and values are cell values, where each value contains:
                    - data_identifier (str): Worksheet column identifier string
                    - value (any): Worksheet line item cell value
            - relationships (dict): Line item relationships containing:
                - worksheet (dict): Associated worksheet containing:
                    - type (str): Object type, should always be "worksheets"
                    - id (int): Worksheet identifier string
    """
    new_id = max(db.DB["events"]["line_items"].keys(), default=0) + 1
    new_line_item = {
        "id": new_id,
        "event_id": event_id,
        "worksheet_id": worksheet_id,
        **data
    }
    db.DB["events"]["line_items"][new_id] = new_line_item
    return new_line_item

def post_multiple(event_id: int, worksheet_id: int, data: List[Dict]) -> List[Dict]:
    """Creates multiple line items in the specified event worksheet.

    Args:
        event_id (int): The unique identifier of the event to which the line items will belong.
        worksheet_id (int): The unique identifier of the worksheet to which the line items will belong.
        data (List[Dict]): A list of dictionaries, where each dictionary contains
            the properties for a new line item, including:
            - type (str): Object type, should always be "line_items"
            - attributes (dict): LineItem attributes containing:
                - data (dict): A hashmap where keys are data identifier strings for the columns in the worksheet, and values are cell values, where each value contains:
                    - data_identifier (str): Worksheet column identifier string
                    - value (any): Worksheet line item cell value
            - relationships (dict): Line item relationships containing:
                - worksheet (dict): Associated worksheet containing:
                    - type (str): Object type, should always be "worksheets"
                    - id (int): Worksheet identifier string

    Returns:
        List[Dict]: A list of dictionaries, where each dictionary represents a created
            line item containing:
            - type (str): Object type, should always be "line_items"
            - event_id (int): ID of the associated event
            - worksheet_id (int): ID of the associated worksheet
            - attributes (dict): LineItem attributes containing:
                - data (dict): A hashmap where keys are data identifier strings for the columns in the worksheet, and values are cell values, where each value contains:
                    - data_identifier (str): Worksheet column identifier string
                    - value (any): Worksheet line item cell value
            - relationships (dict): Line item relationships containing:
                - worksheet (dict): Associated worksheet containing:
                    - type (str): Object type, should always be "worksheets"
                    - id (int): Worksheet identifier string
    """
    created_items = []
    for item_data in data:
        new_id = max(db.DB["events"]["line_items"].keys(), default=0) + 1
        new_line_item = {
            "id": new_id,
            "event_id": event_id,
            "worksheet_id": worksheet_id,
            **item_data
        }
        db.DB["events"]["line_items"][new_id] = new_line_item
        created_items.append(new_line_item)
    return created_items 