# APIs/salesforce/Event.py
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import uuid
import re
from salesforce.SimulationEngine.db import DB
from pydantic import ValidationError
from salesforce.SimulationEngine.models import (
    EventUpdateKwargsModel,
    EventInputModel,
    QueryCriteriaModel,
)

"""
    Represents the Event resource in the API.
"""


def create(
    Name: Optional[str] = None,
    Subject: Optional[str] = None,
    StartDateTime: Optional[str] = None,
    EndDateTime: Optional[str] = None,
    Description: Optional[str] = None,
    Location: Optional[str] = None,
    IsAllDayEvent: Optional[bool] = None,
    OwnerId: Optional[str] = None,
    WhoId: Optional[str] = None,
    WhatId: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Creates a new event.

    Args:
        Name (Optional[str]): The name of the event.
        Subject (Optional[str]): The subject of the event.
        StartDateTime (Optional[str]): Start time of the event.
        EndDateTime (Optional[str]): End time of the event.
        Description (Optional[str]): Description of the event.
        Location (Optional[str]): Location of the event.
        IsAllDayEvent (Optional[bool]): Whether the event is all day.
        OwnerId (Optional[str]): ID of the event owner.
        WhoId (Optional[str]): ID of the related contact.
        WhatId (Optional[str]): ID of the related record.

    Returns:
        Dict[str, Any]: The created event object with the following fields:
            - Id (str): Unique identifier for the event
            - CreatedDate (str): ISO format timestamp of creation
            - IsDeleted (bool): Whether the event is deleted
            - SystemModstamp (str): Last modified timestamp
            - Name (Optional[str]): The name of the event, if provided
            - Subject (Optional[str]): The subject of the event, if provided
            - StartDateTime (Optional[str]): Start time of the event, if provided
            - EndDateTime (Optional[str]): End time of the event, if provided
            - Description (Optional[str]): Description of the event, if provided
            - Location (Optional[str]): Location of the event, if provided
            - IsAllDayEvent (Optional[bool]): Whether the event is all day, if provided
            - OwnerId (Optional[str]): ID of the event owner, if provided
            - WhoId (Optional[str]): ID of the related contact, if provided
            - WhatId (Optional[str]): ID of the related record, if provided

    Raises:
        ValidationError: If event_attributes contain fields not defined in EventInputModel
                                  or if provided fields do not match their expected types
                                  (e.g., 'Subject' is not a string, 'IsAllDayEvent' is not a boolean).
    """
    # --- Input Validation Start ---
    event_attributes = {
        "Subject": Subject,
        "StartDateTime": StartDateTime,
        "EndDateTime": EndDateTime,
        "Description": Description,
        "Location": Location,
        "IsAllDayEvent": IsAllDayEvent,
        "OwnerId": OwnerId,
        "WhoId": WhoId,
        "WhatId": WhatId
    }
    try:
        validated_event_data = EventInputModel(**event_attributes)
    except ValidationError as e:
        # Re-raise the Pydantic validation error.
        # Error messages will detail the exact validation failures.
        raise e
    # --- Input Validation End ---

    new_event = {
        "Id": str(uuid.uuid4()),  # Generate a unique ID
        "CreatedDate": datetime.now().isoformat(),
        "IsDeleted": False,
        "SystemModstamp": datetime.now().isoformat(),
    }

    # Add optional fields if provided
    if Name is not None:
        new_event["Name"] = Name
    if Subject is not None:
        new_event["Subject"] = Subject
    if StartDateTime is not None:
        new_event["StartDateTime"] = StartDateTime
    if EndDateTime is not None:
        new_event["EndDateTime"] = EndDateTime
    if Description is not None:
        new_event["Description"] = Description
    if Location is not None:
        new_event["Location"] = Location
    if IsAllDayEvent is not None:
        new_event["IsAllDayEvent"] = IsAllDayEvent
    if OwnerId is not None:
        new_event["OwnerId"] = OwnerId
    if WhoId is not None:
        new_event["WhoId"] = WhoId
    if WhatId is not None:
        new_event["WhatId"] = WhatId

    DB.setdefault("Event", {})
    DB["Event"][new_event["Id"]] = new_event
    return new_event


def delete(event_id: str) -> Dict[str, Any]:
    """
    Deletes an event.

    Args:
        event_id (str): The ID of the event to delete.

    Returns:
        Dict[str, Any]: Empty dict on success, or error dict with structure:
            - error (str): Error message if event not found
    """
    if "Event" in DB and event_id in DB["Event"]:
        del DB["Event"][event_id]
        return {}
    else:
        return {"error": "Event not found"}


def describeLayout(event_id: str) -> Dict[str, str]:
    """
    Describes the layout of an event.
    
    Args:
        event_id (str): The ID of the event to describe.

    Returns:
        Dict[str, str]: Event layout description with structure:
            - layout (str): Description of the event layout
    """
    return {"layout": "Event layout description"}


def describeSObjects() -> Dict[str, str]:
    """
    Describes the object (Event).

    Returns:
        Dict[str, str]: Event object description with structure:
            - object (str): Description of the event object
    """
    return {"object": "Event object description"}


def getDeleted() -> Dict[str, List[Dict[str, Any]]]:
    """
    Retrieves deleted events.

    Returns:
        Dict[str, List[Dict[str, Any]]]: List of deleted events with structure:
            - deleted (list): List of deleted event objects
    """
    return {"deleted": []}  # Return an empty list for now


def getUpdated() -> Dict[str, List[Dict[str, Any]]]:
    """
    Retrieves updated events.

    Returns:
        Dict[str, List[Dict[str, Any]]]: List of updated events with structure:
            - updated (list): List of updated event objects
    """
    return {"updated": []}  # Return an empty list for now


def query(criteria: Optional[Dict[str, Any]] = None) -> Dict[str, List[Dict[str, Any]]]:
    """
    Queries events based on specified criteria.

    Args:
        criteria (Optional[Dict[str, Any]]): Key-value pairs to filter events. Example:
            - Subject (str): The subject of the event.
            - IsAllDayEvent (bool): Whether the event is all day.
            - StartDateTime (str): Start time of the event.
            - EndDateTime (str): End time of the event.
            - Description (str): Description of the event.
            - Location (str): Location of the event.
            - OwnerId (str): ID of the event owner.

    Returns:
        Dict[str, List[Dict[str, Any]]]: List of events matching the criteria with structure:
            - results (list): List of event objects matching the criteria

    Raises:
        ValidationError: If 'criteria' is provided and is not a dictionary,
                                  or if any of its known keys like "Subject",
                                  "IsAllDayEvent", or "StartDateTime"
                                  do not match their expected types.
    """
    # --- Input Validation Logic ---
    if criteria is not None:
        try:
            _ = QueryCriteriaModel(**criteria)
        except ValidationError as e:
            # Re-raise Pydantic's validation error to be handled by the caller.
            raise e
    # --- End of Input Validation Logic ---

    results = []

    if "Event" in DB:  # type: ignore
        for event in DB["Event"].values():  # type: ignore
            if criteria is None:
                results.append(event)
            else:
                match = True
                for key, value in criteria.items():
                    if key not in event or event[key] != value:
                        match = False
                        break
                if match:
                    results.append(event)
    return {"results": results}


def retrieve(event_id: str) -> Dict[str, Any]:
    """
    Retrieves details of a specific event.

    Args:
        event_id (str): The ID of the event to retrieve.

    Returns:
        Dict[str, Any]: The event object if found, or error dict with structure:
            - error (str): Error message if event not found
    """
    if "Event" in DB and event_id in DB["Event"]:
        return DB["Event"][event_id]
    else:
        return {"error": "Event not found"}


def search(search_term: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Searches for events based on specified search criteria.

    Args:
        search_term (str): The term to search for in event fields.

    Returns:
        Dict[str, List[Dict[str, Any]]]: List of events containing the search term with structure:
            - results (list): List of event objects containing the search term

    Raises:
        TypeError: If search_term is not a string.
    """
    if not isinstance(search_term, str):
        raise TypeError("search_term must be a string.")

    results = []
    if "Event" in DB and isinstance(DB["Event"], dict):
        # If search term is empty, return all events
        if not search_term:
            results = list(DB["Event"].values())
        else:
            search_term_lower = search_term.lower()
            for event in DB["Event"].values():
                if isinstance(event, dict):
                    # Convert all values to strings and search case-insensitively
                    if any(
                        search_term_lower in str(value).lower()
                        for value in event.values()
                    ):
                        results.append(event)
    return {"results": results}


def undelete(event_id: str) -> Dict[str, Any]:
    """
    Restores a deleted event. (Place holder - no actual deletion tracking).

    Args:
        event_id (str): The ID of the event to undelete.

    Returns:
        Dict[str, Any]: The event object if found, or error dict with structure:
            - error (str): Error message if event not found
    """
    if "Event" in DB and event_id in DB["Event"]:
        return DB["Event"][event_id]
    else:
        return {"error": "Event not found"}


def update(
    event_id: str,
    Name: Optional[str] = None,
    Subject: Optional[str] = None,
    StartDateTime: Optional[str] = None,
    EndDateTime: Optional[str] = None,
    Description: Optional[str] = None,
    Location: Optional[str] = None,
    IsAllDayEvent: Optional[bool] = None,
    OwnerId: Optional[str] = None,
    WhoId: Optional[str] = None,
    WhatId: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Updates an existing event.

    Args:
        event_id (str): The ID of the event to update.
        Name (Optional[str]): The name of the event.
        Subject (Optional[str]): The subject of the event.
        StartDateTime (Optional[str]): Start time of the event.
        EndDateTime (Optional[str]): End time of the event.
        Description (Optional[str]): Description of the event.
        Location (Optional[str]): Location of the event.
        IsAllDayEvent (Optional[bool]): Whether the event is all day.
        OwnerId (Optional[str]): ID of the event owner.
        WhoId (Optional[str]): ID of the related contact.
        WhatId (Optional[str]): ID of the related record.

    Returns:
        Dict[str, Any]: The updated event object if found, or an error dict with the structure:
              `{"error": "Event not found"}` if the event_id does not exist.

    Raises:
        TypeError: If `event_id` is not a string.
        pydantic.ValidationError: If any of the known fields in `kwargs`
                                  (e.g., 'Subject', 'IsAllDayEvent')
                                  are provided with an invalid data type.
    """
    # 1. Validate non-dictionary arguments
    if not isinstance(event_id, str):
        raise TypeError("event_id must be a string.")

    # 2. Validate dictionary arguments (kwargs) using Pydantic
    update_properties = {
        "Subject": Subject,
        "StartDateTime": StartDateTime,
        "EndDateTime": EndDateTime,
        "Description": Description,
        "Location": Location,
        "IsAllDayEvent": IsAllDayEvent,
        "OwnerId": OwnerId,
        "WhoId": WhoId,
        "WhatId": WhatId
    }
    try:
        # This step validates that if any keys in kwargs match the fields
        # defined in EventUpdateKwargsModel, their values have the correct types.
        # It does not prevent unknown keys from being in kwargs, and it does not
        # create a new object to be used by the core logic. The original kwargs
        # is used in the loop below, preserving the function's ability to update
        # arbitrary fields.
        EventUpdateKwargsModel(**update_properties)
    except ValidationError as e:
        # Re-raise the Pydantic validation error.
        # The error message will detail which field(s) failed validation.
        raise e

    # --- Original core logic (remains unchanged) ---
    # Assume DB is globally available as per problem description.
    if "Event" in DB and event_id in DB["Event"]:
        event = DB["Event"][event_id]

        # Update only provided fields
        if Name is not None:
            event["Name"] = Name
        if Subject is not None:
            event["Subject"] = Subject
        if StartDateTime is not None:
            event["StartDateTime"] = StartDateTime
        if EndDateTime is not None:
            event["EndDateTime"] = EndDateTime
        if Description is not None:
            event["Description"] = Description
        if Location is not None:
            event["Location"] = Location
        if IsAllDayEvent is not None:
            event["IsAllDayEvent"] = IsAllDayEvent
        if OwnerId is not None:
            event["OwnerId"] = OwnerId
        if WhoId is not None:
            event["WhoId"] = WhoId
        if WhatId is not None:
            event["WhatId"] = WhatId

        event["SystemModstamp"] = datetime.now().isoformat()
        return event
    else:
        return {"error": "Event not found"}


def upsert(
    Name: Optional[str] = None,
    Id: Optional[str] = None,
    Subject: Optional[str] = None,
    StartDateTime: Optional[str] = None,
    EndDateTime: Optional[str] = None,
    Description: Optional[str] = None,
    Location: Optional[str] = None,
    IsAllDayEvent: Optional[bool] = None,
    OwnerId: Optional[str] = None,
    WhoId: Optional[str] = None,
    WhatId: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Creates or updates an event.

    Args:
        Name (Optional[str]): The name of the event.
        Id (Optional[str]): Event ID (required for update).
        Subject (Optional[str]): The subject of the event.
        StartDateTime (Optional[str]): Start time of the event.
        EndDateTime (Optional[str]): End time of the event.
        Description (Optional[str]): Description of the event.
        Location (Optional[str]): Location of the event.
        IsAllDayEvent (Optional[bool]): Whether the event is all day.
        OwnerId (Optional[str]): ID of the event owner.
        WhoId (Optional[str]): ID of the related contact.
        WhatId (Optional[str]): ID of the related record.

    Returns:
        Dict[str, Any]: The created or updated event object with the following fields:
            - Id (str): Unique identifier for the event
            - CreatedDate (str): ISO format timestamp of creation
            - IsDeleted (bool): Whether the event is deleted
            - SystemModstamp (str): Last modified timestamp
            - Name (Optional[str]): The name of the event, if provided
            - Subject (Optional[str]): The subject of the event, if provided
            - StartDateTime (Optional[str]): Start time of the event, if provided
            - EndDateTime (Optional[str]): End time of the event, if provided
            - Description (Optional[str]): Description of the event, if provided
            - Location (Optional[str]): Location of the event, if provided
            - IsAllDayEvent (Optional[bool]): Whether the event is all day, if provided
            - OwnerId (Optional[str]): ID of the event owner, if provided
            - WhoId (Optional[str]): ID of the related contact, if provided
            - WhatId (Optional[str]): ID of the related record, if provided
    """
    if Id is not None and Id in DB.get("Event", {}):
        return update(
            Id,
            Name=Name,
            Subject=Subject,
            StartDateTime=StartDateTime,
            EndDateTime=EndDateTime,
            Description=Description,
            Location=Location,
            IsAllDayEvent=IsAllDayEvent,
            OwnerId=OwnerId,
            WhoId=WhoId,
            WhatId=WhatId,
        )
    else:
        return create(
            Name=Name,
            Subject=Subject,
            StartDateTime=StartDateTime,
            EndDateTime=EndDateTime,
            Description=Description,
            Location=Location,
            IsAllDayEvent=IsAllDayEvent,
            OwnerId=OwnerId,
            WhoId=WhoId,
            WhatId=WhatId,
        )

