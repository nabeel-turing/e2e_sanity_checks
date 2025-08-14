"""
This module provides functionality for managing supplier companies associated with
specific events using external identifiers in the Workday Strategic Sourcing system.
It supports operations for adding and removing suppliers from events using external
IDs, with a focus on RFP-type events.
"""

from typing import List, Dict, Optional
from .SimulationEngine import db

def post(event_external_id: str, data: dict) -> Optional[Dict]:
    """Add suppliers to an event using external identifiers. Only events of type RFP are supported.

    Args:
        event_external_id (str): The unique external identifier of the event to
            which suppliers will be added.
        data (dict): A dictionary containing the supplier information, including:
            - supplier_external_ids (List[str], optional): A list of supplier external IDs to be
                added to the event
            - type (str): Object type, should always be "supplier_companies"

    Returns:
        Optional[Dict]: The updated event data if successful, including the newly
            added suppliers. Returns None if:
            - The event does not exist
            - The event is not of type RFP
            - The operation fails
    """
    event = next((event for event in db.DB["events"]["events"].values() if event.get("external_id") == event_external_id), None)

    if not event or event.get("type") != "RFP":
        return None

    if "suppliers" not in event:
        event["suppliers"] = []
    event["suppliers"].extend(data.get("supplier_external_ids", []))
    return event

def delete(event_external_id: str, data: dict) -> Optional[Dict]:
    """Removes supplier companies from a specific event using external identifiers. Only events of type RFP are supported.

    Args:
        event_external_id (str): The unique external identifier of the event from
            which suppliers will be removed.
        data (dict): A dictionary containing the supplier information, including:
            - supplier_external_ids (List[str]): A list of supplier external IDs to be
                removed from the event
            - type (str): Object type, should always be "supplier_companies"
    Returns:
        Optional[Dict]: The updated event data if successful, with the specified
            suppliers removed. Returns None if:
            - The event does not exist
            - The event is not of type RFP
            - The operation fails
    """
    event = next((event for event in db.DB["events"]["events"].values() if event.get("external_id") == event_external_id), None)
    if not event or event.get("type") != "RFP":
        return None

    if "suppliers" in event:
        for supplier_external_id in data.get("supplier_external_ids", []):
            if supplier_external_id in event["suppliers"]:
                event["suppliers"].remove(supplier_external_id)
        return event
    return None