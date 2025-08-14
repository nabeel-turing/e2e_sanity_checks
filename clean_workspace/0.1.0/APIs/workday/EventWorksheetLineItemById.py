"""
This module provides functionality for managing individual line items within event
worksheets in the Workday Strategic Sourcing system. It supports retrieving,
updating, and deleting specific line items by their unique identifiers, with
validation to ensure the line items belong to the correct event and worksheet.
"""

from typing import List, Dict, Optional
from .SimulationEngine import db

def get(event_id: int, worksheet_id: int, id: int) -> Optional[Dict]:
    """Retrieves the details of an existing line item. You need to supply the unique line item identifier that 
    was returned upon line item creation.

    Args:
        event_id (int): The unique identifier of the event to which the line item belongs.
        worksheet_id (int): The unique identifier of the worksheet to which the line item belongs.
        id (int): The unique identifier of the line item to retrieve.

    Returns:
        Optional[Dict]: A dictionary containing the line item details if found,
            including:
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
    if id in db.DB["events"]["line_items"] and db.DB["events"]["line_items"][id]["event_id"] == event_id and db.DB["events"]["line_items"][id]["worksheet_id"] == worksheet_id:
        return db.DB["events"]["line_items"][id]
    else:
        return None

def patch(event_id: int, worksheet_id: int, id: int, data: Dict) -> Optional[Dict]:
    """Updates the details of an existing line item. You need to supply the unique line item that was returned 
    upon line item creation. Please note, that request body must include the id attribute with the value of 
    your line item unique identifier (the same one you passed as argument)

    Args:
        event_id (int): The unique identifier of the event to which the line item belongs.
        worksheet_id (int): The unique identifier of the worksheet to which the line item belongs.
        id (int): The unique identifier of the line item to update.
        data (Dict): A dictionary containing the updated properties for the line item.
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
        Optional[Dict]: The updated line item data if the update was successful,
            including all current properties of the line item. Returns None if:
            - The line item does not exist
            - The line item does not belong to the specified event and worksheet
            - The provided data does not include the correct line item ID
            The line item may contain any of the following keys:
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
    if id in db.DB["events"]["line_items"] and db.DB["events"]["line_items"][id]["event_id"] == event_id and db.DB["events"]["line_items"][id]["worksheet_id"] == worksheet_id and data.get("id") == id:
        db.DB["events"]["line_items"][id].update(data)
        return db.DB["events"]["line_items"][id]
    else:
        return None

def delete(event_id: int, worksheet_id: int, id: int) -> bool:
    """Deletes a specific line item from the system.

    Args:
        event_id (int): The unique identifier of the event to which the line item belongs.
        worksheet_id (int): The unique identifier of the worksheet to which the line item belongs.
        id (int): The unique identifier of the line item to delete.

    Returns:
        bool: True if the line item was successfully deleted, False if:
            - The line item does not exist
            - The line item does not belong to the specified event and worksheet
    """
    if id in db.DB["events"]["line_items"] and db.DB["events"]["line_items"][id]["event_id"] == event_id and db.DB["events"]["line_items"][id]["worksheet_id"] == worksheet_id:
        del db.DB["events"]["line_items"][id]
        return True
    else:
        return False 