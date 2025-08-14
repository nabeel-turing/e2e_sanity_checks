"""
This module provides functionality for managing bids associated with specific
events in the Workday Strategic Sourcing system. It supports operations for
retrieving and filtering bids, with support for pagination and optional
inclusion of related data. The module enables efficient bid management and
tracking for RFP-type events.
"""

from typing import List, Dict, Optional
from .SimulationEngine import db

def get(event_id: int, filter: Optional[Dict] = None, _include: Optional[str] = None, page: Optional[Dict] = None) -> List[Dict]:
    """Returns a list of all bids. Only bids for events of type RFP are returned

    This function returns all bids linked to the specified event, with support
    for filtering, pagination, and optional inclusion of related data. Only
    bids for events of type RFP (Request for Proposal) are returned. The function
    supports comprehensive filtering and data inclusion options.

    Args:
        event_id (int): The unique identifier of the event for which to retrieve
            bids.
        filter (Optional[Dict]): A dictionary containing filter criteria for bids. Each key represents a filter field with its corresponding value. Supported filters:
            - id_equals (int): Find bids by specific IDs
            - intend_to_bid_equals (bool): Return bids with specified "intent to bid" status
            - intend_to_bid_not_equals (bool): Return bids with "intent to bid" status not equal to specified value
            - intend_to_bid_answered_at_from (str): Return bids with intend_to_bid updated on or after timestamp
            - intend_to_bid_answered_at_to (str): Return bids with intend_to_bid updated on or before timestamp
            - submitted_at_from (str): Return bids with submitted_at on or after timestamp
            - submitted_at_to (str): Return bids with submitted_at on or before timestamp
            - resubmitted_at_from (str): Return bids with resubmitted_at on or after timestamp
            - resubmitted_at_to (str): Return bids with resubmitted_at on or before timestamp
            - status_equals (List[str]): Find bids with specified statuses (award_retracted, awarded, draft, rejected, rejection_retracted, resubmitted, revising, submitted, unclaimed, update_requested)
            - supplier_company_id_equals (int): Find bids by specific Supplier Company IDs
            - supplier_company_external_id_equals (str): Find bids by specific Supplier Company External IDs
            Defaults to None.
        _include (Optional[str]): A string specifying additional related resources to include in the response. Supported values:
            - "event": Include event details
            - "supplier_company": Include supplier company details
            Defaults to None.
        page (Optional[Dict]): A dictionary containing pagination parameters:
            - size (int): The number of results returned per page. Default is 10, maximum is 100.
            Defaults to None.

    Returns:
        List[Dict]: A list of dictionaries, where each dictionary represents a bid
            associated with the specified event. Each bid contains:
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

    Note:
        The filtering is case-sensitive and requires exact matches for all
        specified fields. If a field specified in the filter does not exist
        in a bid, that bid will be excluded from the results. The function
        returns an empty list if:
            - The event does not exist
            - The event is not of type RFP
            - No bids match the specified filter criteria
    """
    if event_id not in db.DB["events"]["events"] or db.DB["events"]["events"][event_id].get("type") != "RFP":
        return []
    bids = [bid for bid in  db.DB["events"]["bids"].values() if bid.get("event_id") == event_id]

    if filter:
        filtered_bids = []
        for bid in bids:
            match = True
            for key, value in filter.items():
                if key not in bid or bid[key] != value:
                    match = False
                    break
            if match:
                filtered_bids.append(bid)
        bids = filtered_bids

    if page and 'size' in page:
        size = page['size']
        bids = bids[:size]

    return bids