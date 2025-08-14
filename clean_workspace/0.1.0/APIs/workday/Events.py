"""
Event Management Module for Workday Strategic Sourcing API Simulation.

This module provides functionality for managing events in the Workday Strategic Sourcing system.
Events are core components that represent sourcing activities, auctions, and related processes.
The module supports CRUD operations for events and includes features for event filtering,
pagination, and template-based event creation.
"""

from typing import List, Dict, Optional
from .SimulationEngine import db
from .SimulationEngine.models import EventInputModel, PaginationModel, EventFilterModel
from pydantic import ValidationError
from typing import Any


def get(filter: Optional[Dict] = None, page: Optional[Dict] = None) -> List[Dict]:
    """
    Returns a list of events for the specified criteria.

    Args:
        filter (Optional[Dict], optional): Dictionary containing filter criteria where keys are
            event attributes and values are the desired values to match. Supported filters:
            - updated_at_from (str): Return events updated on or after timestamp
            - updated_at_to (str): Return events updated on or before timestamp
            - title_contains (str): Return events with title containing string
            - title_not_contains (str): Return events with title not containing string
            - spend_category_id_equals (List[int]): Find events using specified Spend Category IDs
            - state_equals (List[str]): Find events with specified states ("draft", "scheduled", "published", "live_editing", "closed", "canceled")
            - event_type_equals (List[str]): Find events with specified types ("RFP", "AUCTION", "AUCTION_WITH_LOTS", "AUCTION_LOT", "PERFORMANCE_REVIEW_EVENT", "PERFORMANCE_REVIEW_SCORE_CARD_ONLY_EVENT", "SUPPLIER_REVIEW_EVENT", "SUPPLIER_REVIEW_MASTER_EVENT")
            - request_type_equals (List[str]): Find events with specified request types
            - supplier_rsvp_deadline_from (str): Return events with RSVP deadline on or after date
            - supplier_rsvp_deadline_to (str): Return events with RSVP deadline on or before date
            - supplier_rsvp_deadline_empty (bool): Return events with RSVP deadline not set
            - supplier_rsvp_deadline_not_empty (bool): Return events with RSVP deadline set
            - supplier_question_deadline_from (str): Return events with questions deadline on or after date
            - supplier_question_deadline_to (str): Return events with questions deadline on or before date
            - supplier_question_deadline_empty (bool): Return events with questions deadline not set
            - supplier_question_deadline_not_empty (bool): Return events with questions deadline set
            - bid_submission_deadline_from (str): Return events with bid deadline on or after date
            - bid_submission_deadline_to (str): Return events with bid deadline on or before date
            - bid_submission_deadline_empty (bool): Return events with bid deadline not set
            - bid_submission_deadline_not_empty (bool): Return events with bid deadline set
            - created_at_from (str): Return events created on or after timestamp
            - created_at_to (str): Return events created on or before timestamp
            - published_at_from (str): Return events published on or after timestamp
            - published_at_to (str): Return events published on or before timestamp
            - published_at_empty (bool): Return events without published timestamp
            - published_at_not_empty (bool): Return events with published timestamp
            - closed_at_from (str): Return events closed on or after timestamp
            - closed_at_to (str): Return events closed on or before timestamp
            - closed_at_empty (bool): Return events without closed timestamp
            - closed_at_not_empty (bool): Return events with closed timestamp
            - spend_amount_from (float): Return events with spend amount >= amount
            - spend_amount_to (float): Return events with spend amount <= amount
            - spend_amount_empty (bool): Return events with spend amount not set
            - spend_amount_not_empty (bool): Return events with spend amount set
            - external_id_empty (bool): Return events with blank external_id
            - external_id_not_empty (bool): Return events with non-blank external_id
            - external_id_equals (str): Find events by specific external ID
            - external_id_not_equals (str): Find events excluding specified external ID
        page (Optional[Dict], optional): Dictionary containing pagination parameters:
            - size (int): Number of results per page (default: 10, max: 100)

    Returns:
        List[Dict]: A list of event dictionaries, where each event contains any of the following keys:
            - id (int): Event identifier string
            - name (str): Event name
            - type (str): Event type enum ("RFP", "AUCTION", "AUCTION_WITH_LOTS", "AUCTION_LOT", "PERFORMANCE_REVIEW_EVENT", "PERFORMANCE_REVIEW_SCORE_CARD_ONLY_EVENT", "SUPPLIER_REVIEW_EVENT", "SUPPLIER_REVIEW_MASTER_EVENT")
            - duplication_state (str): Event duplication state enum ("scheduled", "started", "finished", "failed")
            - suppliers (list): List of suppliers
            - supplier_contacts (list): List of supplier contacts
            - attributes (dict): Event attributes containing:
                - title (str): An event title
                - event_type (str): Event type enum ("RFP", "AUCTION", "AUCTION_WITH_LOTS", "AUCTION_LOT", "PERFORMANCE_REVIEW_EVENT", "PERFORMANCE_REVIEW_SCORE_CARD_ONLY_EVENT", "SUPPLIER_REVIEW_EVENT", "SUPPLIER_REVIEW_MASTER_EVENT")
                - state (str): Current event state enum ("draft", "scheduled", "published", "live_editing", "closed", "canceled")
                - duplication_state (str): Event duplication state enum ("scheduled", "started", "finished", "failed")
                - spend_amount (float): Actual spend amount
                - request_type (str): Request type
                - late_bids (bool): Whether late bid submissions are allowed
                - revise_bids (bool): Whether suppliers can re-submit bids
                - instant_notifications (bool): Whether notifications are sent immediately
                - supplier_rsvp_deadline (str): RSVP deadline date-time
                - supplier_question_deadline (str): Questions deadline date-time
                - bid_submission_deadline (str): Bid submission deadline date-time
                - created_at (str): Creation date-time
                - closed_at (str): Closing date-time
                - published_at (str): Publication date-time
                - external_id (str): Event ID in internal database
                - is_public (bool): Whether event is accessible for self-registration
                - restricted (bool): Whether event is invitation only
                - custom_fields (list): Custom field values
            - relationships (dict): Event relationships containing:
                - attachments (list): List of attachments
                - project (dict): Associated project
                - spend_category (dict): Associated spend category
                - event_template (dict): Used event template
                - commodity_codes (list): List of commodity codes
            - links (dict): Related links containing:
                - self (str): URL to the resource
    Raises:
        TypeError: If 'filter' or 'page' are provided but are not dictionaries.
        pydantic.ValidationError: If 'filter' or 'page' dictionary does not conform
                                  to the expected structure (e.g., invalid field types, unknown fields,
                                  values out of constraints like page size limits).
    """
    validated_filter_model = None
    if filter is not None:
        if not isinstance(filter, dict):
            raise TypeError("Argument 'filter' must be a dictionary or None.")
        try:
            validated_filter_model = EventFilterModel(**filter)
        except ValidationError as e:
            raise e

    validated_page_model = None
    if page is not None:
        if not isinstance(page, dict):
            raise TypeError("Argument 'page' must be a dictionary or None.")
        try:
            validated_page_model = PaginationModel(**page)
        except ValidationError as e:
            raise e

    # --- Core Logic (preserved) ---
    events_data = db.DB["events"]["events"]
    if not isinstance(events_data, dict) : # Ensure events_data is a dict before calling .values()
         # Or handle as an error, depending on how db structure is guaranteed
        events = []
    else:
        events = list(events_data.values())


    if filter: # Use the original, validated dictionary for filtering logic
        filtered_events = []
        for event_item in events: # Renamed 'event' to 'event_item' to avoid confusion
            match = True
            for key, value in filter.items():
                if key not in event_item or event_item[key] != value:
                    match = False
                    break
            if match:
                filtered_events.append(event_item)
        events = filtered_events
    
    if validated_page_model and validated_page_model.size is not None:
        size = validated_page_model.size
        events = events[:size]
    
    return events

def post(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new event.

    Args:
        data (Dict[str, Any]): Dictionary containing event creation data. Can contain any of the following keys:
            - external_id (str): Event identifier string
            - name (str): Event name
            - type (str): Event type enum ("RFP", "AUCTION", "AUCTION_WITH_LOTS", "AUCTION_LOT", "PERFORMANCE_REVIEW_EVENT", "PERFORMANCE_REVIEW_SCORE_CARD_ONLY_EVENT", "SUPPLIER_REVIEW_EVENT", "SUPPLIER_REVIEW_MASTER_EVENT")
            - suppliers (List[str], optional): List of suppliers
            - supplier_contacts (List[str], optional): List of supplier contacts
            - attributes (dict): Event attributes containing:
                - title (str): An event title
                - event_type (str): Event type enum ("RFP", "AUCTION", "AUCTION_WITH_LOTS", "AUCTION_LOT", "PERFORMANCE_REVIEW_EVENT", "PERFORMANCE_REVIEW_SCORE_CARD_ONLY_EVENT", "SUPPLIER_REVIEW_EVENT", "SUPPLIER_REVIEW_MASTER_EVENT")
                - state (str): Current event state enum ("draft", "scheduled", "published", "live_editing", "closed", "canceled")
                - duplication_state (str): Event duplication state enum ("scheduled", "started", "finished", "failed")
                - spend_amount (float): Actual spend amount
                - request_type (str): Request type
                - late_bids (bool): Whether late bid submissions are allowed
                - revise_bids (bool): Whether suppliers can re-submit bids
                - instant_notifications (bool): Whether notifications are sent immediately
                - supplier_rsvp_deadline (str): RSVP deadline date-time
                - supplier_question_deadline (str): Questions deadline date-time
                - bid_submission_deadline (str): Bid submission deadline date-time
                - created_at (str): Creation date-time
                - closed_at (str): Closing date-time
                - published_at (str): Publication date-time
                - external_id (str): Event ID in internal database
                - is_public (bool): Whether event is accessible for self-registration
                - restricted (bool): Whether event is invitation only
                - custom_fields (List[Dict[str, Any]], optional): Custom field values
            - relationships (dict): Event relationships containing:
                - attachments (List[Dict[str, Any]], optional): List of attachments
                - project (dict): Associated project
                - spend_category (dict): Associated spend category
                - event_template (dict): Used event template
                - commodity_codes (List[Dict[str, Any]], optional): List of commodity codes

    Returns:
        Dict[str, Any]: The newly created event object containing:
            - id (int): Event identifier string
            - name (str): Event name
            - type (str): Event type enum ("RFP", "AUCTION", "AUCTION_WITH_LOTS", "AUCTION_LOT", "PERFORMANCE_REVIEW_EVENT", "PERFORMANCE_REVIEW_SCORE_CARD_ONLY_EVENT", "SUPPLIER_REVIEW_EVENT", "SUPPLIER_REVIEW_MASTER_EVENT")
            - duplication_state (str): Event duplication state enum ("scheduled", "started", "finished", "failed")
            - suppliers (list): List of suppliers
            - supplier_contacts (list): List of supplier contacts
            - attributes (dict): Event attributes containing:
                - title (str): An event title
                - event_type (str): Event type enum ("RFP", "AUCTION", "AUCTION_WITH_LOTS", "AUCTION_LOT", "PERFORMANCE_REVIEW_EVENT", "PERFORMANCE_REVIEW_SCORE_CARD_ONLY_EVENT", "SUPPLIER_REVIEW_EVENT", "SUPPLIER_REVIEW_MASTER_EVENT")
                - state (str): Current event state enum ("draft", "scheduled", "published", "live_editing", "closed", "canceled")
                - duplication_state (str): Event duplication state enum ("scheduled", "started", "finished", "failed")
                - spend_amount (float): Actual spend amount
                - request_type (str): Request type
                - late_bids (bool): Whether late bid submissions are allowed
                - revise_bids (bool): Whether suppliers can re-submit bids
                - instant_notifications (bool): Whether notifications are sent immediately
                - supplier_rsvp_deadline (str): RSVP deadline date-time
                - supplier_question_deadline (str): Questions deadline date-time
                - bid_submission_deadline (str): Bid submission deadline date-time
                - created_at (str): Creation date-time
                - closed_at (str): Closing date-time
                - published_at (str): Publication date-time
                - external_id (str): Event ID in internal database
                - is_public (bool): Whether event is accessible for self-registration
                - restricted (bool): Whether event is invitation only
                - custom_fields (list): Custom field values
            - relationships (dict): Event relationships containing:
                - attachments (list): List of attachments
                - project (dict): Associated project
                - spend_category (dict): Associated spend category
                - event_template (dict): Used event template
                - commodity_codes (list): List of commodity codes
            - links (dict): Related links containing:
                - self (str): URL to the resource
    Raises:
        TypeError: If the 'data' argument is not a dictionary.
        pydantic.ValidationError: If the 'data' argument does not conform to the EventInputModel structure,
                                  including type errors or invalid enum values within the dictionary.
    """
    # Validate input type for 'data'
    if not isinstance(data, dict):
        raise TypeError("Input 'data' must be a dictionary.")

    try:
        validated_event_input = EventInputModel(**data)
    except ValidationError as e:
        raise e

    validated_data_dict = validated_event_input.model_dump(exclude_none=True)

    new_id = max(db.DB["events"]["events"].keys(), default=0) + 1
    new_event = {
        "id": new_id,
        "duplication_state": "scheduled",
        **validated_data_dict
    }
    db.DB["events"]["events"][new_id] = new_event
    return new_event

def get_by_id(id: int) -> Optional[Dict]:
    """
    Retrieve details of a specific event.

    Args:
        id (int): The unique identifier of the event to retrieve.

    Returns:
        Optional[Dict]: The event object if found, None otherwise. The event object contains any of the following keys:
            - id (int): Event identifier
            - name (str): Event name
            - type (str): Event type enum ("RFP", "AUCTION", "AUCTION_WITH_LOTS", "AUCTION_LOT", "PERFORMANCE_REVIEW_EVENT", "PERFORMANCE_REVIEW_SCORE_CARD_ONLY_EVENT", "SUPPLIER_REVIEW_EVENT", "SUPPLIER_REVIEW_MASTER_EVENT")
            - duplication_state (str): Event duplication state enum ("scheduled", "started", "finished", "failed")
            - suppliers (list): List of suppliers
            - supplier_contacts (list): List of supplier contacts
            - attributes (dict): Event attributes containing:
                - title (str): An event title
                - event_type (str): Event type enum ("RFP", "AUCTION", "AUCTION_WITH_LOTS", "AUCTION_LOT", "PERFORMANCE_REVIEW_EVENT", "PERFORMANCE_REVIEW_SCORE_CARD_ONLY_EVENT", "SUPPLIER_REVIEW_EVENT", "SUPPLIER_REVIEW_MASTER_EVENT")
                - state (str): Current event state enum ("draft", "scheduled", "published", "live_editing", "closed", "canceled")
                - duplication_state (str): Event duplication state enum ("scheduled", "started", "finished", "failed")
                - spend_amount (float): Actual spend amount
                - request_type (str): Request type
                - late_bids (bool): Whether late bid submissions are allowed
                - revise_bids (bool): Whether suppliers can re-submit bids
                - instant_notifications (bool): Whether notifications are sent immediately
                - supplier_rsvp_deadline (str): RSVP deadline date-time
                - supplier_question_deadline (str): Questions deadline date-time
                - bid_submission_deadline (str): Bid submission deadline date-time
                - created_at (str): Creation date-time
                - closed_at (str): Closing date-time
                - published_at (str): Publication date-time
                - external_id (str): Event ID in internal database
                - is_public (bool): Whether event is accessible for self-registration
                - restricted (bool): Whether event is invitation only
                - custom_fields (list): Custom field values
            - relationships (dict): Event relationships containing:
                - attachments (list): List of attachments
                - project (dict): Associated project
                - spend_category (dict): Associated spend category
                - event_template (dict): Used event template
                - commodity_codes (list): List of commodity codes
            - links (dict): Related links containing:
                - self (str): URL to the resource
    """
    if id in db.DB["events"]["events"]:
        return db.DB["events"]["events"][id]
    else:
        return None

def patch(id: int, data: dict) -> Optional[Dict]:
    """
    Update an existing event.

    Args:
        id (int): The unique identifier of the event to update.
        data (dict): Dictionary containing the fields to update. Must include:
            - id (int): Must match the id parameter in the URL
            Can contain any of the following keys:
            - type (str): Event type enum ("RFP", "AUCTION", "AUCTION_WITH_LOTS", "AUCTION_LOT", "PERFORMANCE_REVIEW_EVENT", "PERFORMANCE_REVIEW_SCORE_CARD_ONLY_EVENT", "SUPPLIER_REVIEW_EVENT", "SUPPLIER_REVIEW_MASTER_EVENT")
            - attributes (dict): Event attributes containing:
                - title (str): An event title
                - event_type (str): Event type enum ("RFP", "AUCTION", "AUCTION_WITH_LOTS", "AUCTION_LOT", "PERFORMANCE_REVIEW_EVENT", "PERFORMANCE_REVIEW_SCORE_CARD_ONLY_EVENT", "SUPPLIER_REVIEW_EVENT", "SUPPLIER_REVIEW_MASTER_EVENT")
                - spend_amount (float): Actual spend amount used to calculate savings and keep reporting up to date
                - late_bids (bool): Whether late bid submissions are allowed
                - revise_bids (bool): Whether suppliers are allowed to re-submit bids
                - instant_notifications (bool): When true, notification emails are sent immediately; when false, notifications are delivered every 3 hours in a digest form
                - external_id (str): Event ID in your internal database
                - restricted (bool): Whether event is invitation only even when posted on the public site
                - custom_fields (List[Dict[str, Any]], optional): Custom field values (note: custom fields of type File can only be accessed through the user interface, they will be exposed as null in the public API)

    Returns:
        Optional[Dict]: The updated event object if successful, None otherwise.
        The updated event object contains any of the following keys:
            - id (int): Event identifier string
            - name (str): Event name
            - type (str): Event type enum ("RFP", "AUCTION", "AUCTION_WITH_LOTS", "AUCTION_LOT", "PERFORMANCE_REVIEW_EVENT", "PERFORMANCE_REVIEW_SCORE_CARD_ONLY_EVENT", "SUPPLIER_REVIEW_EVENT", "SUPPLIER_REVIEW_MASTER_EVENT")
            - duplication_state (str): Event duplication state enum ("scheduled", "started", "finished", "failed")
            - suppliers (list): List of suppliers
            - supplier_contacts (list): List of supplier contacts
            - attributes (dict): Event attributes containing:
                - title (str): An event title
                - event_type (str): Event type enum ("RFP", "AUCTION", "AUCTION_WITH_LOTS", "AUCTION_LOT", "PERFORMANCE_REVIEW_EVENT", "PERFORMANCE_REVIEW_SCORE_CARD_ONLY_EVENT", "SUPPLIER_REVIEW_EVENT", "SUPPLIER_REVIEW_MASTER_EVENT")
                - state (str): Current event state enum ("draft", "scheduled", "published", "live_editing", "closed", "canceled")
                - duplication_state (str): Event duplication state enum ("scheduled", "started", "finished", "failed")
                - spend_amount (float): Actual spend amount
                - request_type (str): Request type
                - late_bids (bool): Whether late bid submissions are allowed
                - revise_bids (bool): Whether suppliers can re-submit bids
                - instant_notifications (bool): Whether notifications are sent immediately
                - supplier_rsvp_deadline (str): RSVP deadline date-time
                - supplier_question_deadline (str): Questions deadline date-time
                - bid_submission_deadline (str): Bid submission deadline date-time
                - created_at (str): Creation date-time
                - closed_at (str): Closing date-time
                - published_at (str): Publication date-time
                - external_id (str): Event ID in internal database
                - is_public (bool): Whether event is accessible for self-registration
                - restricted (bool): Whether event is invitation only
                - custom_fields (list): Custom field values
            - relationships (dict): Event relationships containing:
                - attachments (list): List of attachments
                - project (dict): Associated project
                - spend_category (dict): Associated spend category
                - event_template (dict): Used event template
                - commodity_codes (list): List of commodity codes
            - links (dict): Related links containing:
                - self (str): URL to the resource
    """
    if id in db.DB["events"]["events"] and data.get("id") == id:
        db.DB["events"]["events"][id].update(data)
        return db.DB["events"]["events"][id]
    else:
        return None

def delete(id: int) -> bool:
    """
    Delete an event.

    Args:
        id (int): The unique identifier of the event to delete.

    Returns:
        bool: True if the event was successfully deleted, False otherwise.
    """
    if id in db.DB["events"]["events"]:
        del db.DB["events"]["events"][id]
        return True
    else:
        return False