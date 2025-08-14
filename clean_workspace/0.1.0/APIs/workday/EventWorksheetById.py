"""
This module provides functionality for retrieving specific event worksheets by their
unique identifiers in the Workday Strategic Sourcing system.
"""

from typing import List, Dict, Optional
from .SimulationEngine import db

def get(event_id: int, id: int) -> Optional[Dict]:
    """Retrieves the details of an existing worksheet. You need to supply the unique worksheet identifier that was returned upon worksheet creation.

    Args:
        event_id (int): The unique identifier of the event to which the worksheet belongs.
        id (int): The unique identifier of the worksheet to retrieve.

    Returns:
        Optional[Dict]: A dictionary containing the worksheet details if found,
            including any of the following keys:
            - type (str): Object type, should always be "worksheets"
            - id (int): Worksheet identifier string
            - event_id (int): ID of the associated event
            - name (str): Name of the worksheet
            - created_by (str): ID of the user who created the worksheet
            - attributes (dict): Worksheet attributes containing:
                - title (str): Worksheet title (max 255 characters)
                - budget (float): Budget for worksheet
                - notes (str): Notes specific to worksheet
                - updated_at (str): Last modification date-time
                - worksheet_type (str): Worksheet type enum ("standard", "goods", "services")
                - columns (list): List of column field values, each containing:
                    - id (str): Column identifier string
                    - name (str): Column field name
                    - data_identifier (str): Data identifier for line items
                    - mapping_key (str): Column field mapping key
            - links (dict): Related links containing:
                - self (str): URL to the resource
            Returns None if no worksheet exists with the given IDs or if the worksheet
            does not belong to the specified event.
    """
    if id in db.DB["events"]["worksheets"] and db.DB["events"]["worksheets"][id]["event_id"] == event_id:
        return db.DB["events"]["worksheets"][id]
    else:
        return None