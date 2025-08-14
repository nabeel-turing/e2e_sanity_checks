"""
This module provides functionality for managing supplier contacts associated with
specific events in the Workday Strategic Sourcing system. It supports operations
for adding and removing supplier contacts from events, with a focus on RFP-type
events.
"""

from typing import Dict, Optional
from .SimulationEngine import db

def post(event_id: int, data: dict) -> Optional[Dict]:
    """Adds supplier contacts to a specific event. Only events of type RFP are supported.

    Args:
        event_id (int): The unique identifier of the event to which supplier
            contacts will be added.
        data (dict): A dictionary containing the supplier contact information,
            including:
            - supplier_contact_ids (List[str], optional): A list of supplier contact IDs to be
                added to the event
            - type (str): Object type, should always be "supplier_contacts"

    Returns:
        Optional[Dict]: The updated event data if successful, including the newly
            added supplier contacts. Returns None if:
            - The event does not exist
            - The event is not of type RFP
            - The operation fails
    """
    if event_id not in db.DB["events"]["events"]:
        return None
    event = db.DB["events"]["events"][event_id]
    if event.get("type") != "RFP":
        return None
    if "supplier_contacts" not in event:
        event["supplier_contacts"] = []
    event["supplier_contacts"].extend(data.get("supplier_contact_ids", []))
    return event

def delete(event_id: int, data: dict) -> Optional[Dict]:
    """Remove suppliers from an event using supplier contacts. Only events of type RFP are supported.

    Args:
        event_id (int): The unique identifier of the event from which supplier
            contacts will be removed.
        data (dict): A dictionary containing the supplier contact information,
            including:
            - supplier_contact_ids (List[str], optional): A list of supplier contact IDs to be
                removed from the event
            - type (str): Object type, should always be "supplier_contacts"
    Returns:
        Optional[Dict]: The updated event data if successful, with the specified
            supplier contacts removed. Returns None if:
            - The event does not exist
            - The event is not of type RFP
            - The operation fails
    """
    if event_id not in db.DB["events"]["events"]:
        return None
    event = db.DB["events"]["events"][event_id]
    if event.get("type") != "RFP":
        return None
    if "supplier_contacts" in event:
        for supplier_contact_id in data.get("supplier_contact_ids", []):
            if supplier_contact_id in event["supplier_contacts"]:
                event["supplier_contacts"].remove(supplier_contact_id)
        return event
    return None