"""
This module provides functionality for managing supplier companies associated with
specific events in the Workday Strategic Sourcing system. It supports operations
for adding and removing suppliers from events, with a focus on RFP-type events.
"""

from typing import List, Dict, Optional
from .SimulationEngine import db

def post(event_id: int, data: dict) -> Optional[Dict]:
    """Add suppliers to an event. Only events of type RFP are supported.

    Args:
        event_id (int): The unique identifier of the event to which suppliers
            will be added.
        data (dict): A dictionary containing the supplier information, including:
            - supplier_ids (List[str], optional): A list of supplier IDs to be added to the event
            - type (str): Object type, should always be "supplier_companies"

    Returns:
        Optional[Dict]: The updated event data if successful, including the newly
            added suppliers. Returns None if:
            - The event does not exist
            - The event is not of type RFP
            - The operation fails
    """
    if event_id not in db.DB["events"]["events"]:
        return None
    event = db.DB["events"]["events"][event_id]
    if event.get("type") != "RFP":
        return None
    if "suppliers" not in event:
        event["suppliers"] = []
    event["suppliers"].extend(data.get("supplier_ids", []))
    return event

def delete(event_id: int, data: dict) -> Optional[Dict]:
    """Remove suppliers from an event. Only events of type RFP are supported.

    Args:
        event_id (int): The unique identifier of the event from which suppliers
            will be removed.
        data (dict): A dictionary containing the supplier information, including:
            - supplier_ids (List[str], optional): A list of supplier IDs to be removed from the event
            - type (str): Object type, should always be "supplier_companies"

    Returns:
        Optional[Dict]: The updated event data if successful, with the specified
            suppliers removed. Returns None if:
            - The event does not exist
            - The event is not of type RFP
            - The operation fails
    """
    if event_id not in db.DB["events"]["events"]:
        return None
    event = db.DB["events"]["events"][event_id]
    if event.get("type") != "RFP":
        return None
    if "suppliers" in event:
        for supplier_id in data.get("supplier_ids", []):
            if supplier_id in event["suppliers"]:
                event["suppliers"].remove(supplier_id)
        return event
    return None 