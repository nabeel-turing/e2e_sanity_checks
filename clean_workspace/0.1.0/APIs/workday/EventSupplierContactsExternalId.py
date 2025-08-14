"""
This module provides functionality for managing supplier contacts associated with
specific events using external identifiers in the Workday Strategic Sourcing system.
It supports operations for adding and removing suppliers from events using external
IDs, with a focus on RFP-type events.
"""

from typing import Optional, Dict, Any
from .SimulationEngine import db

def post(event_external_id: str, data: dict) -> Optional[Dict[str, Any]]:
    """Add suppliers to an event using supplier contacts. Only events of type RFP are supported. You must supply the unique event external identifier (the one you used when created the event). You must supply the external identifiers of the supplier contacts too. The operation will be rolled back upon any failure, and invitations won't be sent. For best performance, we recommend inviting 10 or less supplier contacts in a single request.
    
    Args:
        event_external_id (str): The unique external identifier of the event to which suppliers will be added.
        data (dict): A dictionary containing the supplier contact information, including:
            - supplier_contact_external_ids (List[str], optional): A list of supplier contact external IDs to be added to the event
            - type (str): Object type, should always be "supplier_contacts"

    Returns:
        Optional[Dict[str, Any]]: The updated event data if successful, including the newly added supplier contacts. Returns None if:
            - The event does not exist
            - The event is not of type RFP
            - The operation fails
    """
    event = next((event for event in  db.DB["events"]["events"].values() if event.get("external_id") == event_external_id), None)
    if not event or event.get("type") != "RFP":
        return None

    if "supplier_contacts" not in event:
        event["supplier_contacts"] = []
    event["supplier_contacts"].extend(data.get("supplier_contact_external_ids", []))
    return event

 
def delete(event_external_id: str, data: dict) -> Optional[Dict[str, Any]]:
    """Remove suppliers from an event using supplier contacts. Only events of type RFP are supported. You must supply the unique event external identifier (the one you used when created the event). You must supply the external identifiers of the supplier contacts too. The operation will be rolled back upon any failure, and invitations won't be removed. For best performance, we recommend removing 10 or less supplier contacts in a single request.
    
    Args:
        event_external_id (str): The unique external identifier of the event from which supplier contacts will be removed.
        data (dict): A dictionary containing the supplier contact information, including:
            - supplier_contact_external_ids (List[str], optional): A list of supplier contact external IDs to be removed from the event
            - type (str): Object type, should always be "supplier_contacts"

    Returns:
        Optional[Dict[str, Any]]: The updated event data if successful, with the specified supplier contacts removed. Returns None if:
            - The event does not exist
            - The event is not of type RFP
            - The operation fails
    """
    event = next((event for event in  db.DB["events"]["events"].values() if event.get("external_id") == event_external_id), None)
    if not event or event.get("type") != "RFP":
        return None

    if "supplier_contacts" in event:
        for supplier_contact_external_id in data.get("supplier_contact_external_ids", []):
            if supplier_contact_external_id in event["supplier_contacts"]:
                event["supplier_contacts"].remove(supplier_contact_external_id)
        return event
    return None