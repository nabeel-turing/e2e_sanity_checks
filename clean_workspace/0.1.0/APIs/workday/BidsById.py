"""
This module provides functionality for retrieving and managing bids using their unique
internal identifiers in the Workday Strategic Sourcing system. It supports detailed
bid information retrieval with optional inclusion of related data. The module ensures
efficient bid lookup and comprehensive data access through direct ID-based queries.
"""

from typing import Dict, Optional
from .SimulationEngine import db

def get(id: int, _include: Optional[str] = None) -> Optional[Dict]:
    """Retrieves the details of an existing bid. You need to supply the unique bid identifier that was returned upon bid creation.

    Args:
        id (int): The unique internal identifier of the bid to retrieve. This ID is
            typically returned when the bid is created in the system. Must be a
            positive integer.
        _include (Optional[str]): A comma-separated string specifying additional
            related data to include in the response. Common options include:
            - 'event': Include associated event details
            - 'supplier_company': Include supplier information
            Defaults to None.

    Returns:
        Optional[Dict]: A dictionary containing all the details of the requested bid,
            structured as follows:
            - type (str): Object type, should always be "bids"
            - id (int): Bid identifier string
            - supplier_id (int): ID of the submitting supplier
            - bid_amount (float): Total bid amount
            - attributes (dict): Bid attributes containing:
                - intend_to_bid (bool): Identifies whether the supplier intends to bid on the event
                - intend_to_bid_answered_at (str): Most recent time the supplier updated intend_to_bid
                - status (str): Current bid status, one of:
                    - "award_retracted"
                    - "awarded"
                    - "draft"
                    - "rejected"
                    - "rejection_retracted"
                    - "resubmitted"
                    - "revising"
                    - "submitted"
                    - "unclaimed"
                    - "update_requested"
                - submitted_at (str): First time the supplier submitted their bid
                - resubmitted_at (str): Most recent time the supplier submitted their bid
            - included (list): Array of included resources, each containing:
                - type (str): Object type, should always be "events" or "supplier_companies"
                - id (int): Resource identifier string
                - Any other resource-specific attributes as defined in the system
        Returns None if no bid is found with the specified ID.

    Note:
        The function performs a direct lookup in the database using the provided ID.
        If the bid does not exist, the function returns None rather than raising an
        exception. The function is optimized for quick lookups using the bid's
        primary key.
    """
    if id in db.DB["events"]["bids"]:
        return db.DB["events"]["bids"][id]
    else:
        return None