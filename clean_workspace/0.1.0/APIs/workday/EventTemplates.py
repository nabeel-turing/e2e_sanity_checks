"""
This module provides functionality for managing event templates in the Workday
Strategic Sourcing system. It supports retrieving a list of all event templates
and getting specific template details by ID.
"""

from typing import List, Dict, Optional
from .SimulationEngine import db

def get() -> List[Dict]:
    """Returns a list of all event templates.

    Returns:
        List[Dict]: A list of dictionaries, where each dictionary represents
            an event template containing any of the following keys:
            - type (str): Object type, should always be "event_templates"
            - id (int): Event template identifier string
            - name (str): Name of the event template
            - description (str): Detailed description of the event template
            - attributes (dict): Event template attributes containing:
                - title (str): Event template title (max 255 characters)
                - event_type (str): Event type enum ("RFP", "AUCTION", "AUCTION_WITH_LOTS", "AUCTION_LOT", "PERFORMANCE_REVIEW_EVENT", "PERFORMANCE_REVIEW_SCORE_CARD_ONLY_EVENT", "SUPPLIER_REVIEW_EVENT", "SUPPLIER_REVIEW_MASTER_EVENT")
            - links (dict): Related links containing:
                - self (str): Normalized link to the resource
    """
    return list(db.DB["events"]["event_templates"].values())

def get_by_id(id: int) -> Optional[Dict]:
    """Retrieves the details of an existing event template by its ID.

    Args:
        id (int): The unique internal identifier of the event template to retrieve.

    Returns:
        Optional[Dict]: A dictionary containing the event template details if found,
            including any of the following keys:
            - type (str): Object type, should always be "event_templates"
            - id (int): Event template identifier string
            - name (str): Name of the event template
            - description (str): Detailed description of the event template
            - attributes (dict): Event template attributes containing:
                - title (str): Event template title (max 255 characters)
                - event_type (str): Event type enum ("RFP", "AUCTION", "AUCTION_WITH_LOTS", "AUCTION_LOT", "PERFORMANCE_REVIEW_EVENT", "PERFORMANCE_REVIEW_SCORE_CARD_ONLY_EVENT", "SUPPLIER_REVIEW_EVENT", "SUPPLIER_REVIEW_MASTER_EVENT")
            - links (dict): Related links containing:
                - self (str): Normalized link to the resource
            Returns None if no template exists with the given ID.
    """
    return db.DB["events"]["event_templates"].get(id, None) 