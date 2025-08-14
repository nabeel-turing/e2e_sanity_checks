"""
This module provides functionality for managing worksheets within events in the
Workday Strategic Sourcing system.
"""

from typing import List, Dict, Optional
from .SimulationEngine import db

def get(event_id: int) -> List[Dict]:
    """Returns a list of all worksheets.

    Args:
        event_id (int): The unique identifier of the event to which the worksheets belong.

    Returns:
        List[Dict]: A list of dictionaries, where each dictionary represents a worksheet
            containing any of the following keys:
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
    """
    worksheets = []
    for id, worksheet in db.DB["events"]["worksheets"].items():
        if worksheet["event_id"] == event_id:
            worksheets.append(worksheet)
    return worksheets 