# APIs/google_calendar/EventsResource/__init__.py
import uuid
from datetime import datetime

from pydantic import ValidationError

from .SimulationEngine.models import EventResourceInputModel
from .SimulationEngine.models import EventPatchResourceModel
from .SimulationEngine.db import DB
from .SimulationEngine.utils import (
    parse_iso_datetime,
    notify_attendees,
)
from typing import Dict, Any, Optional, List
from .SimulationEngine.custom_errors import InvalidInputError, ResourceNotFoundError, ResourceAlreadyExistsError
from .SimulationEngine.recurrence_expander import expand_recurring_events


def delete_event(
    calendarId: str,
    eventId: str,
    sendUpdates: str = None,
) -> Dict[str, Any]:
    """
    Deletes an event from the specified calendar.

    Args:
        calendarId (str): The identifier of the calendar containing the event to delete. If "primary" is provided, the primary calendar will be used.
        eventId (str): The identifier of the event to delete.
        sendUpdates (str, optional): Whether to send updates about the deletion.
            Possible values: "all", "externalOnly", "none". Defaults to None.
            Note: sendUpdates functionality is not implemented yet.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - success (bool): Whether the event was successfully deleted.
            - message (str): A message describing the result of the operation.

    Raises:
        ValueError: If the event is not found in the calendar.
    """
    # Map "primary" to the user's primary calendar ID
    if calendarId == "primary":
        # Find the actual primary calendar from the DB
        primary_calendar = None
        if "calendar_list" in DB and DB["calendar_list"]:
            for cal_id, cal_data in DB["calendar_list"].items():
                if cal_data.get("primary") is True:
                    primary_calendar = cal_id
                    break

        if primary_calendar:
            calendarId = primary_calendar

    key = (calendarId, eventId)
    if key not in DB["events"]:
        raise ValueError(f"Event '{eventId}' not found in calendar '{calendarId}'.")
    # snapshot for notification
    event_before_delete = DB["events"][key].copy()
    del DB["events"][key]

    try:
        notify_attendees(calendarId, event_before_delete, sendUpdates, subject_prefix="Cancelled")
    except Exception:
        pass
    return {
        "success": True,
        "message": f"Event '{eventId}' deleted from calendar '{calendarId}'.",
    }


def get_event(
    alwaysIncludeEmail: bool = False,
    calendarId: str = "primary",
    eventId: str = None,
    maxAttendees: int = None,
    timeZone: str = None,
) -> Dict[str, Any]:
    """
    Retrieves an event from the specified calendar.

    Args:
        alwaysIncludeEmail (bool, optional): Deprecated. This parameter is ignored as email addresses
            are always included in the response. Defaults to False.
        calendarId (str, optional): The identifier of the calendar. Defaults to "primary".
            To retrieve calendar IDs call the calendarList.list method.
            If you want to access the primary calendar of the currently logged in user,
            use the "primary" keyword.
        eventId (str, optional): The identifier of the event to retrieve. This is mandatory.
        maxAttendees (int, optional): The maximum number of attendees to return (must be non-negative).
            Defaults to None (return all attendees).
        timeZone (str, optional): The time zone to use for the response (e.g. "America/New_York").
            Defaults to the calendar's time zone.

    Returns:
        Dict[str, Any]: The event details containing:
            - id (str): The identifier of the event.
            - summary (str): The summary/title of the event.
            - description (str, optional): The description of the event.
            - start (Dict[str, Any]): The start time of the event.
                - dateTime (str): The date and time of the start time in ISO 8601(YYYY-MM-DDTHH:MM:SSZ) format.
            - end (Dict[str, Any]): The end time of the event.
                - dateTime (str): The date and time of the end time in ISO 8601(YYYY-MM-DDTHH:MM:SSZ) format.
            - organizer (Dict[str, Any]): The organizer of the event.
                - email (str): The email address of the organizer.
            - creator (Dict[str, Any]): The creator of the event.
                - email (str): The email address of the creator.
            - attendees (List[Dict[str, Any]]): The list of attendees.
                - email (str): The email address of the attendee.

    Raises:
        TypeError: If any argument has an invalid type (e.g., `alwaysIncludeEmail` is not bool,
            `calendarId` is not str or None, `eventId` is not str, `maxAttendees` is not int or None,
            `timeZone` is not str or None).
        InvalidInputError: If any argument has an invalid value or format:
            - eventId is None or empty/whitespace
            - calendarId is empty/whitespace
            - maxAttendees is negative
            - timeZone is empty/whitespace or has invalid format
        ResourceNotFoundError: If the calendar or event is not found:
            - Calendar with specified ID does not exist
            - Event with specified ID does not exist in the calendar
    """
    # --- Input Validation ---
    # Validate alwaysIncludeEmail
    if not isinstance(alwaysIncludeEmail, bool):
        raise TypeError("alwaysIncludeEmail must be a boolean.")

    # Validate calendarId
    if calendarId is not None:
        if not isinstance(calendarId, str):
            raise TypeError("calendarId must be a string or None.")
        if not calendarId.strip():
            raise InvalidInputError("calendarId cannot be empty or whitespace.")

    # Validate eventId
    if eventId is None:
        raise InvalidInputError("eventId must be provided as a non-empty string.")
    if not isinstance(eventId, str):
        raise TypeError("eventId must be a string.")
    if not eventId.strip():
        raise InvalidInputError("eventId cannot be empty or whitespace.")

    # Validate maxAttendees
    if maxAttendees is not None:
        if not isinstance(maxAttendees, int):
            raise TypeError("maxAttendees must be an integer or None.")
        if maxAttendees < 0:
            raise InvalidInputError("maxAttendees cannot be negative.")

    # Validate timeZone
    if timeZone is not None:
        if not isinstance(timeZone, str):
            raise TypeError("timeZone must be a string or None.")
        if not timeZone.strip():
            raise InvalidInputError("timeZone cannot be empty or whitespace.")
        # Basic timezone format validation (e.g., "Continent/City")
        if "/" not in timeZone:
            raise InvalidInputError("timeZone must be in format 'Continent/City' (e.g., 'America/New_York').")

    # --- End Input Validation ---

    # --- Core Logic ---
    effective_calendarId = calendarId
    if effective_calendarId is None or effective_calendarId == "":
        effective_calendarId = "primary"

    # Map "primary" to the user's primary calendar ID
    if effective_calendarId == "primary":
        # Find the actual primary calendar from the DB
        primary_calendar = None
        if "calendar_list" in DB and DB["calendar_list"]:
            for cal_id, cal_data in DB["calendar_list"].items():
                if cal_data.get("primary") is True:
                    primary_calendar = cal_id
                    break
        
        if primary_calendar:
            effective_calendarId = primary_calendar

    # Assume DB exists and has the expected structure
    if "calendar_list" not in DB or effective_calendarId not in DB["calendar_list"]:
        raise ResourceNotFoundError(f"Calendar '{effective_calendarId}' not found.")

    key = (effective_calendarId, eventId)
    if "events" not in DB or key not in DB["events"]:
        raise ResourceNotFoundError(f"Event '{eventId}' not found in calendar '{effective_calendarId}'.")

    # Get a copy to avoid modifying the original DB entry directly
    event = DB["events"][key].copy()

    # Handle timeZone parameter (simulated)
    if timeZone is not None:
        # In a real implementation, we would convert the times to the specified timezone
        # For simulation purposes, we'll just add the timezone to the response
        event["timeZone"] = timeZone # Add a distinct field to avoid overwriting event's own timezone

    # Handle maxAttendees parameter
    if "attendees" in event and maxAttendees is not None:
        # Ensure event["attendees"] is actually a list before slicing
        if isinstance(event.get("attendees"), list):
             event["attendees"] = event["attendees"][:maxAttendees]
        # Else: maybe log a warning about unexpected attendee format?

    return event


def import_event(
    calendarId: str,
    conferenceDataVersion: int = 0,
    supportsAttachments: bool = False,
    resource: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Imports an event into the specified calendar.

    Args:
        calendarId (str): The identifier of the calendar.
        conferenceDataVersion (int, optional): The version of the conference data.
            Defaults to 0.
        supportsAttachments (bool, optional): Whether the event supports attachments.
            Defaults to False.
        resource (Dict[str, Any], optional): The event to import:
            - id (str, optional): The identifier of the event. If not provided,
                a new UUID will be generated.
            - summary (str): The summary/title of the event.
            - description (str, optional): The description of the event.
            - start (Dict[str, Any]): The start time of the event.
                - dateTime (str): The date and time of the start time in ISO 8601(YYYY-MM-DDTHH:MM:SSZ) format.
            - end (Dict[str, Any]): The end time of the event.
                - dateTime (str): The date and time of the end time in ISO 8601(YYYY-MM-DDTHH:MM:SSZ) format.

    Returns:
        Dict[str, Any]: The imported event.
            - id (str): The identifier of the event.
            - summary (str): The summary of the event.
            - description (str): The description of the event.
            - start (Dict[str, Any]): The start time of the event.
                - dateTime (str): The date and time of the start time in ISO 8601(YYYY-MM-DDTHH:MM:SSZ) format.
            - end (Dict[str, Any]): The end time of the event.
                - dateTime (str): The date and time of the end time in ISO 8601(YYYY-MM-DDTHH:MM:SSZ) format.

    Raises:
        ValueError: If the resource is not provided.
    """
    if resource is None:
        raise ValueError("Resource is required to import an event.")
    ev_id = resource.get("id") or str(uuid.uuid4())
    resource["id"] = ev_id
    DB["events"][(calendarId, ev_id)] = resource
    return resource

def create_event(calendarId: str = "primary", resource: Dict[str, Any] = None, sendUpdates: str = None) -> Dict[str, Any]:
    """
    Creates a new event in the specified calendar.

    Args:
        calendarId (str, optional): The identifier of the calendar. Defaults to the user's primary calendar.
        resource (Dict[str, Any]): The event to create:
            - id (str, optional): The identifier of the event. If not provided,
                a new UUID will be generated.
            - summary (str): The summary/title of the event.
            - description (str, optional): The description of the event.
            - start (Dict[str, Any]): The start time of the event.
                - dateTime (str): The date and time of the start time in ISO 8601(YYYY-MM-DDTHH:MM:SSZ) format.
            - end (Dict[str, Any]): The end time of the event.
                - dateTime (str): The date and time of the end time.
            - recurrence (Optional[List[str]]): The recurrence rules of the event in RRULE format.
                Examples:
                - Daily for 5 occurrences: ["RRULE:FREQ=DAILY;COUNT=5"]
                - Weekly on Monday and Wednesday: ["RRULE:FREQ=WEEKLY;BYDAY=MO,WE"]
                - Monthly on the 15th: ["RRULE:FREQ=MONTHLY;BYMONTHDAY=15"]
                - Yearly on January 1st: ["RRULE:FREQ=YEARLY;BYMONTH=1;BYMONTHDAY=1"]
                - Every 2 weeks: ["RRULE:FREQ=WEEKLY;INTERVAL=2"]
                - Until a specific date: ["RRULE:FREQ=DAILY;UNTIL=20241231T235959Z"]
                
                Supported RRULE parameters:
                - FREQ: SECONDLY, MINUTELY, HOURLY, DAILY, WEEKLY, MONTHLY, YEARLY (required)
                - INTERVAL: Positive integer (default: 1)
                - COUNT: Positive integer (number of occurrences)
                - UNTIL: YYYYMMDDTHHMMSSZ or YYYYMMDDTHHMMSS format
                - BYDAY: SU,MO,TU,WE,TH,FR,SA (with optional ordinal: 1SU, -1MO)
                - BYMONTH: 1-12
                - BYMONTHDAY: 1-31
                - BYYEARDAY: 1-366
                - BYWEEKNO: 1-53
                - BYHOUR: 0-23
                - BYMINUTE: 0-59
                - BYSECOND: 0-59
                - BYSETPOS: 1-366 or -366 to -1
                - WKST: SU,MO,TU,WE,TH,FR,SA (week start)
                
            - attendees (Optional[List[Dict[str, Any]]]): List of event attendees. Each attendee can have:
                - email (Optional[str]): The attendee's email address
                - displayName (Optional[str]): The attendee's display name
                - organizer (Optional[bool]): Whether the attendee is the organizer
                - self (Optional[bool]): Whether the attendee is the user
                - resource (Optional[bool]): Whether the attendee is a resource
                - optional (Optional[bool]): Whether the attendee's presence is optional
                - responseStatus (Optional[str]): The attendee's response status
                - comment (Optional[str]): The attendee's comment
                - additionalGuests (Optional[int]): Number of additional guests

            - reminders (Optional[Dict[str, Any]]): The reminders of the event.
                - useDefault (bool): Whether to use the default reminders.
                - overrides (Optional[List[Dict[str, Any]]]): The list of overrides.
                    - method (str): The method of the reminder.
                    - minutes (int): The minutes of the reminder.
        
            - location (Optional[str]): The location of the event.

            - attachments (Optional[List[Dict[str, Any]]]): The attachments list contains the dicts and each dict has the following key:
                -fileUrl (str): The URL of the attachment

        sendUpdates (str, optional): Whether to send updates about the creation.
                                     Possible values: "all", "externalOnly", "none". Defaults to None.

    Returns:
        Dict[str, Any]: The created event.
            - id (str): The identifier of the event.
            - summary (str): The summary of the event.
            - description (str): The description of the event.
            - start (Dict[str, Any]): The start time of the event.
                - dateTime (str): The date and time of the start time.
            - end (Dict[str, Any]): The end time of the event.
                - dateTime (str): The date and time of the end time.
            - attendees (List[Dict[str, Any]], optional): List of event attendees with their details.
            - recurrence (Optional[List[str]]): The recurrence rules of the event. e.g. ["RRULE:FREQ=DAILY;COUNT=5"]
            - reminders (Optional[Dict[str, Any]]): The reminders of the event.
            - location (Optional[str]): The location of the event.
            - attachments (Optional[List[Dict[str, Any]]]): The attachments list contains the dicts and each dict has the following key:
                -fileUrl (str): The URL of the attachment

    Raises:
        TypeError: If 'calendarId' is not a string or 'sendUpdates' is not a string (if provided).
        ValueError: If 'resource' is not provided (i.e., is None).
        InvalidInputError: If 'sendUpdates' has an invalid value (not one of: "all", "externalOnly", "none").
        pydantic.ValidationError: If 'resource' is provided but does not conform to the
                                  EventResourceInputModel structure (e.g., missing 'summary',
                                  'start', 'end', or incorrect types for fields like 'dateTime').
                                  This includes validation errors for recurrence rules.

    Examples:
        # Create a simple event
        event = create_event("primary", {
            "summary": "Team Meeting",
            "start": {"dateTime": "2024-01-15T10:00:00Z"},
            "end": {"dateTime": "2024-01-15T11:00:00Z"}
        })
        
        # Create a recurring daily event
        event = create_event("primary", {
            "summary": "Daily Standup",
            "start": {"dateTime": "2024-01-15T09:00:00Z"},
            "end": {"dateTime": "2024-01-15T09:30:00Z"},
            "recurrence": ["RRULE:FREQ=DAILY;COUNT=10"]
        })
        
        # Create a weekly event on specific days
        event = create_event("primary", {
            "summary": "Weekly Review",
            "start": {"dateTime": "2024-01-15T14:00:00Z"},
            "end": {"dateTime": "2024-01-15T15:00:00Z"},
            "recurrence": ["RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR"]
        })

        # Create an event with an attachment
        event = create_event("primary", {
            "summary": "Meeting with attachment",
            "start": {"dateTime": "2024-01-16T10:00:00Z"},
            "end": {"dateTime": "2024-01-16T11:00:00Z"},
            "attachments": [{
                "fileUrl": "https://example.com/mydocument.pdf"
            }]
        })
    """
    # --- Start of Validation Logic ---

    # 1. Standard type validation for non-dictionary arguments
    if calendarId is not None and not isinstance(calendarId, str):
        raise TypeError("calendarId must be a string.")
    if calendarId is None:
        calendarId = "primary"

    # Validate sendUpdates
    if sendUpdates is not None:
        if not isinstance(sendUpdates, str):
            raise TypeError("sendUpdates must be a string if provided.")
        valid_send_updates = ["all", "externalOnly", "none"]
        if sendUpdates not in valid_send_updates:
            raise InvalidInputError(f"sendUpdates must be one of: {', '.join(valid_send_updates)}")

    # 2. Check for mandatory 'resource' (as per original logic and docstring)
    # This must happen before attempting to validate its structure.
    if resource is None:
        raise ValueError("Resource is required to create an event.")
    validated_resource = EventResourceInputModel(**resource)
    
    # Map "primary" to the user's primary calendar ID
    if calendarId == "primary":
        # Find the actual primary calendar from the DB
        primary_calendar = None
        if "calendar_list" in DB and DB["calendar_list"]:
            for cal_id, cal_data in DB["calendar_list"].items():
                if cal_data.get("primary") is True:
                    primary_calendar = cal_id
                    break

        if primary_calendar:
            calendarId = primary_calendar
    
    ev_id = validated_resource.id or str(uuid.uuid4())
    event_dict = validated_resource.model_dump()
    event_dict["id"] = ev_id
    DB["events"][(calendarId, ev_id)] = event_dict

    try:
        notify_attendees(calendarId, event_dict, sendUpdates, subject_prefix="Invitation")
    except Exception:
        # Non-fatal in simulation
        pass

    return event_dict


def list_event_instances(
    alwaysIncludeEmail: bool = False,
    calendarId: str = "primary",
    eventId: str = None,
    maxAttendees: int = None,
    maxResults: int = 250,
    originalStart: str = None,
    pageToken: str = None,
    showDeleted: bool = False,
    timeMax: str = None,
    timeMin: str = None,
    timeZone: str = None,
) -> Dict[str, Any]:
    """
    Returns instances of a specified recurring event.
    This is a mock, so we won't actually expand recurrences.
    We'll pretend the event itself is the only instance.

    Args:
        alwaysIncludeEmail (bool, optional): Whether to include the email address of the event creator.
            Defaults to False.
        calendarId (str, optional): The identifier of the calendar. If not provided, defaults to "primary".
        eventId (str, optional): The identifier of the event.
        maxAttendees (int, optional): The maximum number of attendees to return.
            Must be non-negative. Defaults to None (return all attendees).
        maxResults (int, optional): The maximum number of instances to return.
            Must be a positive integer. Defaults to 250.
        originalStart (str, optional): The original start time of the instance in ISO 8601 format.
        pageToken (str, optional): The token for the next page of results.
        showDeleted (bool, optional): Whether to include deleted instances.
            Defaults to False.
        timeMax (str, optional): The maximum time of the instances to return in ISO 8601(YYYY-MM-DDTHH:MM:SSZ) format.
        timeMin (str, optional): The minimum time of the instances to return in ISO 8601(YYYY-MM-DDTHH:MM:SSZ) format.
        timeZone (str, optional): The time zone to use for the response (e.g. "America/New_York").
            Must be in format 'Continent/City'. Defaults to the calendar's time zone.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - items (List[Dict[str, Any]]): The list of event instances.
                - id (str): The identifier of the event.
                - summary (str): The summary of the event.
                - description (str): The description of the event.
                - start (Dict[str, Any]): The start time of the event.
                    - dateTime (str): The date and time of the start time in ISO 8601(YYYY-MM-DDTHH:MM:SSZ) format.
                - end (Dict[str, Any]): The end time of the event.
                    - dateTime (str): The date and time of the end time in ISO 8601(YYYY-MM-DDTHH:MM:SSZ) format.
                - attendees (List[Dict[str, Any]], optional): List of attendees (limited by maxAttendees).
                - timeZone (str, optional): Applied timezone if timeZone parameter was provided.
            - nextPageToken (str): The next page token. None if there are no more pages.

    Raises:
        TypeError: If any argument has an invalid type.
        InvalidInputError: If any argument has an invalid value or format.
        ResourceNotFoundError: If the calendar or event is not found.
    """
    # --- Input Validation ---
    
    # Validate alwaysIncludeEmail
    if not isinstance(alwaysIncludeEmail, bool):
        raise TypeError("alwaysIncludeEmail must be a boolean")
    
    # Validate calendarId
    if calendarId is not None:
        if not isinstance(calendarId, str):
            raise TypeError("calendarId must be a string")
        if not calendarId.strip():
            raise InvalidInputError("calendarId cannot be empty or whitespace")
    
    # Validate eventId
    if eventId is not None:
        if not isinstance(eventId, str):
            raise TypeError("eventId must be a string")
        if not eventId.strip():
            raise InvalidInputError("eventId cannot be empty or whitespace")
    
    # Validate maxAttendees
    if maxAttendees is not None:
        if not isinstance(maxAttendees, int):
            raise TypeError("maxAttendees must be an integer")
        if maxAttendees < 0:
            raise InvalidInputError("maxAttendees cannot be negative")
    
    # Validate maxResults
    if not isinstance(maxResults, int):
        raise TypeError("maxResults must be an integer")
    if maxResults <= 0:
        raise InvalidInputError("maxResults must be a positive integer")
    
    # Validate originalStart
    if originalStart is not None:
        if not isinstance(originalStart, str):
            raise TypeError("originalStart must be a string")
        if not originalStart.strip():
            raise InvalidInputError("originalStart cannot be empty or whitespace")
        try:
            parsed_start = parse_iso_datetime(originalStart)
            if parsed_start is None:
                raise InvalidInputError("originalStart must be a valid ISO 8601 datetime string")
        except ValueError as e:
            raise InvalidInputError(f"Invalid originalStart format: {str(e)}. Must be in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)")
    
    # Validate pageToken
    if pageToken is not None:
        if not isinstance(pageToken, str):
            raise TypeError("pageToken must be a string")
        if not pageToken.strip():
            raise InvalidInputError("pageToken cannot be empty or whitespace")
    
    # Validate showDeleted
    if not isinstance(showDeleted, bool):
        raise TypeError("showDeleted must be a boolean")
    
    # Validate timeMax
    if timeMax is not None:
        if not isinstance(timeMax, str):
            raise TypeError("timeMax must be a string")
        if not timeMax.strip():
            raise InvalidInputError("timeMax cannot be empty or whitespace")
        try:
            parsed_timeMax = parse_iso_datetime(timeMax)
            if parsed_timeMax is None:
                raise InvalidInputError("timeMax must be a valid ISO 8601 datetime string")
        except ValueError as e:
            raise InvalidInputError(f"Invalid timeMax format: {str(e)}. Must be in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)")
    
    # Validate timeMin
    if timeMin is not None:
        if not isinstance(timeMin, str):
            raise TypeError("timeMin must be a string")
        if not timeMin.strip():
            raise InvalidInputError("timeMin cannot be empty or whitespace")
        try:
            parsed_timeMin = parse_iso_datetime(timeMin)
            if parsed_timeMin is None:
                raise InvalidInputError("timeMin must be a valid ISO 8601 datetime string")
        except ValueError as e:
            raise InvalidInputError(f"Invalid timeMin format: {str(e)}. Must be in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)")
    
    # Validate timeZone
    if timeZone is not None:
        if not isinstance(timeZone, str):
            raise TypeError("timeZone must be a string")
        if not timeZone.strip():
            raise InvalidInputError("timeZone cannot be empty or whitespace")
        # Basic timezone format validation (e.g., "Continent/City")
        if "/" not in timeZone:
            raise InvalidInputError("timeZone must be in format 'Continent/City' (e.g., 'America/New_York')")
    
    # Validate time range consistency
    if timeMin is not None and timeMax is not None:
        try:
            timeMin_dt = parse_iso_datetime(timeMin)
            timeMax_dt = parse_iso_datetime(timeMax)
            if timeMin_dt and timeMax_dt and timeMin_dt >= timeMax_dt:
                raise InvalidInputError("timeMin must be earlier than timeMax")
        except ValueError:
            # Already handled above in individual validations
            pass
    
    # --- End Input Validation ---
    
    # --- Core Logic ---
    
    # Handle calendarId default and primary calendar logic
    effective_calendarId = calendarId
    if effective_calendarId is None or effective_calendarId == "":
        effective_calendarId = "primary"

    # Map "primary" to the user's primary calendar ID
    if effective_calendarId == "primary":
        # Find the actual primary calendar from the DB
        primary_calendar = None
        if "calendar_list" in DB and DB["calendar_list"]:
            for cal_id, cal_data in DB["calendar_list"].items():
                if cal_data.get("primary") is True:
                    primary_calendar = cal_id
                    break
        
        if primary_calendar:
            effective_calendarId = primary_calendar

    # Check if calendar exists
    if "calendar_list" not in DB or effective_calendarId not in DB["calendar_list"]:
        raise ResourceNotFoundError(f"Calendar '{effective_calendarId}' not found.")

    # Check if event exists
    key = (effective_calendarId, eventId)
    if "events" not in DB or key not in DB["events"]:
        raise ResourceNotFoundError(f"Event '{eventId}' not found in calendar '{effective_calendarId}'.")
    
    # Get the event
    event = DB["events"][key].copy()
    
    # Apply time filtering if timeMin/timeMax are provided
    if timeMin is not None or timeMax is not None:
        # Check if event has valid start/end times for filtering
        event_start = None
        event_end = None
        
        if "start" in event and "dateTime" in event["start"]:
            try:
                event_start = parse_iso_datetime(event["start"]["dateTime"])
            except ValueError:
                pass
        
        if "end" in event and "dateTime" in event["end"]:
            try:
                event_end = parse_iso_datetime(event["end"]["dateTime"])
            except ValueError:
                pass
        
        # Filter by timeMin
        if timeMin is not None and event_start is not None:
            timeMin_dt = parse_iso_datetime(timeMin)
            if timeMin_dt and event_start < timeMin_dt:
                # Event starts before timeMin, exclude it
                return {"items": [], "nextPageToken": None}
        
        # Filter by timeMax
        if timeMax is not None and event_end is not None:
            timeMax_dt = parse_iso_datetime(timeMax)
            if timeMax_dt and event_end > timeMax_dt:
                # Event ends after timeMax, exclude it
                return {"items": [], "nextPageToken": None}
    
    # Apply originalStart filtering if provided
    if originalStart is not None:
        original_start_dt = parse_iso_datetime(originalStart)
        if original_start_dt is not None:
            # In a real implementation, this would filter instances based on originalStart
            # For this mock, we'll just check if the event's start time matches
            if "start" in event and "dateTime" in event["start"]:
                try:
                    event_start = parse_iso_datetime(event["start"]["dateTime"])
                    if event_start != original_start_dt:
                        # Event start doesn't match originalStart, exclude it
                        return {"items": [], "nextPageToken": None}
                except ValueError:
                    # If we can't parse the event start time, exclude it
                    return {"items": [], "nextPageToken": None}
    
    # Apply showDeleted filtering
    if not showDeleted and event.get("status") == "cancelled":
        # Event is deleted and showDeleted is False, exclude it
        return {"items": [], "nextPageToken": None}
    
    # Apply timeZone parameter (simulated)
    if timeZone is not None:
        event["timeZone"] = timeZone
    
    # Handle maxAttendees parameter
    if "attendees" in event and maxAttendees is not None:
        if isinstance(event.get("attendees"), list):
            event["attendees"] = event["attendees"][:maxAttendees]
    
    # Apply maxResults (though in this mock we only return 1 item max)
    # In a real implementation, this would limit the number of instances returned
    items = [event]
    if len(items) > maxResults:
        items = items[:maxResults]
    
    # Handle pagination (though in this mock we only return 1 item max)
    # In a real implementation, this would handle pageToken and return nextPageToken
    nextPageToken = None
    if pageToken is not None:
        # In a real implementation, this would validate and use the pageToken
        # For this mock, we'll just ignore it since we only return 1 item
        pass
    
    # Return the event instances
    return {"items": items, "nextPageToken": nextPageToken}


def list_events(
    calendarId: Optional[str] = "primary",  # Changed from `Optional[str] = None` to `Optional[str] = "primary"`
    maxResults: int = 250,
    timeMin: Optional[str] = None,
    timeMax: Optional[str] = None,
    q: Optional[str] = None,
    singleEvents: bool = False,
    orderBy: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Lists events from the specified calendar.

    Args:
        calendarId (Optional[str], optional): The identifier of the calendar. Defaults to "primary".
        maxResults (int, optional): The maximum number of events to return.
            Must be a positive integer. Defaults to 250.
        timeMin (Optional[str], optional): The minimum time of the events to return (ISO datetime string).
        timeMax (Optional[str], optional): The maximum time of the events to return (ISO datetime string).
        q (Optional[str], optional): The query string to filter events by.
        singleEvents (bool, optional): Whether to expand recurring events into individual instances.
            When True, recurring events are expanded into separate instances within the time range.
            When False, only the base recurring event is returned. Defaults to False.
        orderBy (Optional[str], optional): The order of the events.
            Must be one of: "startTime", "updated". Defaults to None.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - items (List[Dict[str, Any]]): The list of events.
                - id (str): The identifier of the event.
                - summary (str): The summary of the event.
                - description (str): The description of the event.
                - start (Dict[str, Any]): The start time of the event.
                    - dateTime (str): The date and time of the start time in ISO 8601(YYYY-MM-DDTHH:MM:SSZ) format.
                - end (Dict[str, Any]): The end time of the event.
                    - dateTime (str): The date and time of the end time in ISO 8601(YYYY-MM-DDTHH:MM:SSZ) format.
                - recurrence (Optional[List[str]]): The recurrence rules (only present for base recurring events).
                - recurringEventId (Optional[str]): The ID of the parent recurring event (only present for instances).
                - originalStartTime (Optional[Dict[str, Any]]): The original start time of the recurring event.

    Raises:
        TypeError: If `calendarId` is provided and is not a string.
        TypeError: If `maxResults` is not an integer.
        TypeError: If `timeMin` is provided and is not a string.
        TypeError: If `timeMax` is provided and is not a string.
        TypeError: If `q` is provided and is not a string.
        TypeError: If `singleEvents` is not a boolean.
        TypeError: If `orderBy` is provided and is not a string.
        InvalidInputError: If `maxResults` is not a positive integer.
        InvalidInputError: If `timeMin` or `timeMax` contains a malformed datetime string that cannot be parsed.
        InvalidInputError: If `orderBy` has an invalid value (not "startTime" or "updated").
                    
    """
    # --- Input Validation ---
    if calendarId is not None and not isinstance(calendarId, str):
        raise TypeError("calendarId must be a string if provided.")

    if not isinstance(maxResults, int):
        raise TypeError("maxResults must be an integer.")
    if maxResults <= 0:
        raise InvalidInputError("maxResults must be a positive integer.")

    if timeMin is not None:
        if not isinstance(timeMin, str):
            raise TypeError("timeMin must be a string if provided (ISO datetime format).")
        try:
            timeMin_dt = parse_iso_datetime(timeMin)
            if timeMin_dt is None:
                raise InvalidInputError("timeMin must be a valid ISO datetime string.")
        except ValueError as e:
            raise InvalidInputError(f"Invalid timeMin format: {str(e)}. Must be in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ).")

    if timeMax is not None:
        if not isinstance(timeMax, str):
            raise TypeError("timeMax must be a string if provided (ISO datetime format).")
        try:
            timeMax_dt = parse_iso_datetime(timeMax)
            if timeMax_dt is None:
                raise InvalidInputError("timeMax must be a valid ISO datetime string.")
        except ValueError as e:
            raise InvalidInputError(f"Invalid timeMax format: {str(e)}. Must be in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ).")

    if q is not None and not isinstance(q, str):
        raise TypeError("q must be a string if provided.")

    if not isinstance(singleEvents, bool):
        raise TypeError("singleEvents must be a boolean.")

    if orderBy is not None:
        if not isinstance(orderBy, str):
            raise TypeError("orderBy must be a string if provided.")
        valid_order_by = ["startTime", "updated"]
        if orderBy not in valid_order_by:
            raise InvalidInputError(f"orderBy must be one of: {', '.join(valid_order_by)}")

    # --- Core Logic ---
    # Handle calendarId default and primary calendar logic
    effective_calendarId = calendarId
    if effective_calendarId is None or effective_calendarId == "":
        effective_calendarId = "primary"
    
    # Map "primary" to the user's primary calendar ID
    if effective_calendarId == "primary":
        # Find the actual primary calendar from the DB
        primary_calendar = None
        if "calendar_list" in DB and DB["calendar_list"]:
            for cal_id, cal_data in DB["calendar_list"].items():
                if cal_data.get("primary") is True:
                    primary_calendar = cal_id
                    break
        
        if primary_calendar:
            effective_calendarId = primary_calendar
    
    # Parse datetime objects for time range filtering
    timeMin_dt = parse_iso_datetime(timeMin) if timeMin is not None else None
    timeMax_dt = parse_iso_datetime(timeMax) if timeMax is not None else None
    results = []

    # Collect base events
    base_events = []
    for (cal_id, ev_id), ev_obj in DB["events"].items():
        # Filter by calendarId
        if cal_id != effective_calendarId:
            continue
        
        # Filter by query string 'q' (only for base events)
        if q is not None:
            # Using lower case comparison for case-insensitive search
            query_lower = q.lower()
            summary = ev_obj.get("summary", "").lower()
            description = ev_obj.get("description", "") or ""
            description = description.lower()
            # If query not found in either field, skip the event.
            if query_lower not in summary and query_lower not in description:
                continue

        base_events.append(ev_obj)

    # Expand recurring events if singleEvents is True
    if singleEvents:
        # Expand recurring events into instances within the time range
        expanded_events = expand_recurring_events(
            base_events, 
            timeMin_dt, 
            timeMax_dt, 
            max_instances_per_event=50  # Limit instances per event to prevent explosion
        )
        
        # Filter expanded events by time range
        for event in expanded_events:
            event_start = parse_iso_datetime(event.get("start", {}).get("dateTime"))
            event_end = parse_iso_datetime(event.get("end", {}).get("dateTime"))
            
            # Filter by timeMin
            if timeMin_dt is not None and event_start is not None:
                if event_start < timeMin_dt:
                    continue
            
            # Filter by timeMax
            if timeMax_dt is not None and event_end is not None:
                if event_end > timeMax_dt:
                    continue
            
            results.append(event)
    else:
        # Original behavior: return base events with time filtering
        for event in base_events:
            # Filter by timeMin
            if timeMin is not None: # timeMin_dt would be None if timeMin was None
                if "start" not in event:
                    continue
                if "dateTime" not in event["start"]:
                    continue
                event_start = parse_iso_datetime(event["start"]["dateTime"])
                if event_start is None or timeMin_dt is None: # Guard against None from parse_iso_datetime
                    continue
                if event_start < timeMin_dt:
                    continue
            # Filter by timeMax
            if timeMax is not None: # timeMax_dt would be None if timeMax was None
                if "end" not in event:
                    continue
                if "dateTime" not in event["end"]:
                    continue
                event_end = parse_iso_datetime(event["end"]["dateTime"])
                if event_end is None or timeMax_dt is None: # Guard against None from parse_iso_datetime
                    continue
                if event_end > timeMax_dt:
                    continue

            results.append(event)

    # Sort results if orderBy is specified
    if orderBy == "startTime":
        results.sort(key=lambda x: parse_iso_datetime(x.get("start", {}).get("dateTime")) or datetime.max)
    elif orderBy == "updated":
        results.sort(key=lambda x: parse_iso_datetime(x.get("start", {}).get("dateTime")) or datetime.max)

    # Truncate at maxResults
    results = results[:maxResults]

    return {"items": results}


def move_event(
    calendarId: str,
    eventId: str,
    destination: str,
    sendUpdates: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Moves an event from one calendar to another. We simulate by removing from old
    and creating in new with same ID.

    Args:
        calendarId (str): The identifier of the source calendar.
        eventId (str): The identifier of the event to move.
        destination (str): The identifier of the destination calendar.
        sendUpdates (Optional[str]): Whether to send updates about the move.
            Possible values: "all", "externalOnly", "none". Defaults to None.

    Returns:
        Dict[str, Any]: The moved event.
            - id (str): The identifier of the event.
            - summary (str): The summary of the event.
            - description (str): The description of the event.
            - start (Dict[str, Any]): The start time of the event.
                - dateTime (str): The date and time of the start time in ISO 8601(YYYY-MM-DDTHH:MM:SSZ) format.
            - end (Dict[str, Any]): The end time of the event.
                - dateTime (str): The date and time of the end time in ISO 8601(YYYY-MM-DDTHH:MM:SSZ) format.

    Raises:
        TypeError: If any argument has an invalid type (e.g., calendarId is not str).
        InvalidInputError: If any argument has an invalid value:
            - calendarId is empty/whitespace
            - eventId is empty/whitespace
            - destination is empty/whitespace
            - sendUpdates has invalid value (not one of: "all", "externalOnly", "none")
        ResourceNotFoundError: If the event is not found in the calendar.
        ResourceAlreadyExistsError: If the event already exists in the destination calendar.
    """
    # --- Input Validation ---
    # Validate calendarId
    if not isinstance(calendarId, str):
        raise TypeError("calendarId must be a string.")
    if not calendarId.strip():
        raise InvalidInputError("calendarId cannot be empty or whitespace.")

    # Validate eventId
    if not isinstance(eventId, str):
        raise TypeError("eventId must be a string.")
    if not eventId.strip():
        raise InvalidInputError("eventId cannot be empty or whitespace.")

    # Validate destination
    if not isinstance(destination, str):
        raise TypeError("destination must be a string.")
    if not destination.strip():
        raise InvalidInputError("destination cannot be empty or whitespace.")

    # Validate sendUpdates
    if sendUpdates is not None:
        if not isinstance(sendUpdates, str):
            raise TypeError("sendUpdates must be a string if provided.")
        valid_send_updates = ["all", "externalOnly", "none"]
        if sendUpdates not in valid_send_updates:
            raise InvalidInputError(f"sendUpdates must be one of: {', '.join(valid_send_updates)}")

    # --- Core Logic ---
    old_key = (calendarId, eventId)
    if old_key not in DB["events"]:
        raise ResourceNotFoundError(f"Event '{eventId}' not found in calendar '{calendarId}'.")
    
    ev_data = DB["events"].pop(old_key)
    new_key = (destination, eventId)
    if new_key in DB["events"]:
        raise ResourceAlreadyExistsError(
            f"Event '{eventId}' already exists in destination calendar '{destination}'."
        )
    DB["events"][new_key] = ev_data

    try:
        notify_attendees(destination, ev_data, sendUpdates, subject_prefix="Moved")
    except Exception:
        pass
    return ev_data

# Placeholder for DB if it's to be accessed globally and needs type hint / definition for linters
# DB: Dict[str, Any] = {"events": {}} # This would typically be defined elsewhere

def patch_event(calendarId: str = "primary", eventId: Optional[str] = None, resource: Optional[Dict[str, Any]] = None, sendUpdates: str = None) -> Dict[str, Any]:
    """
    Updates specific fields of an existing event.

    This function allows partial updates to an event by providing only the fields 
    that need to be changed.
    
    Args:
        calendarId (str): The identifier of the calendar. Defaults to "primary".
        eventId (Optional[str]): The identifier of the event to update.
        resource (Optional[Dict[str, Any]]): The fields to update.
        sendUpdates (str, optional): Whether to send updates about the patch.
            Possible values: "all", "externalOnly", "none". Defaults to None.
            Note: sendUpdates functionality is not implemented yet.
            Validated structure:
            - summary (Optional[str]): The new summary/title of the event.
            - description (Optional[str]): The new description of the event.
            - start (Optional[Dict[str, Any]]): The new start time of the event.
                - dateTime (Optional[str]): The date and time in ISO 8601 format (e.g., "2025-03-10T09:00:00Z").
            - end (Optional[Dict[str, Any]]): The new end time of the event.
                - dateTime (Optional[str]): The date and time in ISO 8601 format (e.g., "2025-03-10T09:30:00Z").
            - attendees (Optional[List[Dict[str, Any]]]): The new list of attendees.
                Each attendee dict contains:
                - email (Optional[str]): The attendee's email address.
                - displayName (Optional[str]): The attendee's name.
                - organizer (Optional[bool]): Whether the attendee is the organizer.
                - self (Optional[bool]): Whether this represents the calendar owner.
                - resource (Optional[bool]): Whether the attendee is a resource (room, equipment).
                - optional (Optional[bool]): Whether this is an optional attendee.
                - responseStatus (Optional[str]): Response status ("needsAction", "declined", "tentative", "accepted").
                - comment (Optional[str]): The attendee's comment.
                - additionalGuests (Optional[int]): Number of additional guests.
            - location (Optional[str]): The new location of the event.
            - recurrence (Optional[List[str]]): The new recurrence rules of the event.
            - reminders (Optional[Dict[str, Any]]): The new reminders of the event.
                - useDefault (Optional[bool]): Whether to use default calendar reminders.
                - overrides (Optional[List[Dict[str, Any]]]): Custom reminder overrides.
                    Each override dict contains:
                    - method (Optional[str]): Reminder method.
                    - minutes (Optional[int]): Minutes before event start.

    Returns:
        Dict[str, Any]: The patched event containing:
            - id (str): The identifier of the event.
            - summary (str): The summary of the event.
            - description (str): The description of the event.
            - start (Dict[str, Any]): The start time of the event.
                - dateTime (str): The date and time in ISO 8601 format.
            - end (Dict[str, Any]): The end time of the event.
                - dateTime (str): The date and time in ISO 8601 format.
            - attendees (Optional[List[Dict[str, Any]]]): List of event attendees containing:
                - email (Optional[str]): The attendee's email address.
                - displayName (Optional[str]): The attendee's name.
                - organizer (Optional[bool]): Whether the attendee is the organizer.
                - self (Optional[bool]): Whether this represents the calendar owner.
                - resource (Optional[bool]): Whether the attendee is a resource.
                - optional (Optional[bool]): Whether this is an optional attendee.
                - responseStatus (Optional[str]): Response status.
                - comment (Optional[str]): The attendee's comment.
                - additionalGuests (Optional[int]): Number of additional guests.
            - location (Optional[str]): The location of the event.
            - recurrence (Optional[List[str]]): The recurrence rules of the event.
            - reminders (Optional[Dict[str, Any]]): The reminders of the event containing:
                - useDefault (Optional[bool]): Whether default calendar reminders are used.
                - overrides (Optional[List[Dict[str, Any]]]): Custom reminder overrides.

    Raises:
        TypeError: If calendarId or eventId is not a string, or sendUpdates is not a string (if provided).
        ValueError: If calendarId is empty/whitespace, eventId is None/empty/whitespace, or event is not found.
        InvalidInputError: If sendUpdates has an invalid value (not one of: "all", "externalOnly", "none").
        ValidationError: If 'resource' does not conform to the EventPatchResourceModel structure.
    """    
    # Validate calendarId type and format
    if not isinstance(calendarId, str):
        raise TypeError(f"calendarId must be a string if provided, got {type(calendarId).__name__}.")
    if not calendarId.strip():
        raise ValueError("calendarId cannot be empty or contain only whitespace.")
    
    # Validate eventId type and format - eventId is required for patch operations
    if eventId is None:
        raise ValueError("eventId is required for patch operations.")
    if not isinstance(eventId, str):
        raise TypeError(f"eventId must be a string if provided, got {type(eventId).__name__}.")
    if not eventId.strip():
        raise ValueError("eventId cannot be empty or contain only whitespace.")

    # Validate sendUpdates
    if sendUpdates is not None:
        if not isinstance(sendUpdates, str):
            raise TypeError("sendUpdates must be a string if provided.")
        valid_send_updates = ["all", "externalOnly", "none"]
        if sendUpdates not in valid_send_updates:
            raise InvalidInputError(f"sendUpdates must be one of: {', '.join(valid_send_updates)}")

    # Validate and process resource using Pydantic model
    validated_resource_data: Dict[str, Any] = {}
    if resource is not None:
        # First check if resource is a dictionary
        if not isinstance(resource, dict):
            raise ValueError("Resource must be a dictionary")
        
        try:
            validated_resource_model = EventPatchResourceModel(**resource)
            # Convert back to dict for the original function logic, excluding unset fields
            validated_resource_data = validated_resource_model.model_dump(exclude_unset=True)
        except ValidationError as e:
            # Re-raise Pydantic's ValidationError for detailed error reporting
            raise e

    # Check if event exists in the specified calendar
    key = (calendarId, eventId)
    if key not in DB["events"]:
        raise ValueError(f"Event '{eventId}' not found in calendar '{calendarId}'.")
    
    # Get the existing event and update it with validated data
    existing = DB["events"][key]
    
    # Use validated_resource_data which contains only the valid fields from the input resource
    for k, v in validated_resource_data.items():
        existing[k] = v
    
    # Save the updated event back to the database
    DB["events"][key] = existing

    try:
        notify_attendees(calendarId, existing, sendUpdates, subject_prefix="Updated")
    except Exception:
        pass
    return existing


def quick_add_event(
    calendarId: str,
    sendUpdates: str = None,
    text: str = None,
) -> Dict[str, Any]:
    """
    Creates an event based on a simple text string.

    Args:
        calendarId (str): The identifier of the calendar.
        sendUpdates (str, optional): Whether to send updates about the creation.
            Possible values: "all", "externalOnly", "none". Defaults to None.
        text (str): The text to parse into an event. This should be a natural language
            description of the event, such as "Lunch with John at noon tomorrow".

    Returns:
        Dict[str, Any]: The created event.
            - id (str): The identifier of the event.
            - summary (str): The summary of the event. The text provided in the 'text' parameter.
            - description (str): The description of the event.
            - start (Dict[str, Any]): The start time of the event.
                - dateTime (str): The date and time of the start time in ISO 8601(YYYY-MM-DDTHH:MM:SSZ) format.
            - end (Dict[str, Any]): The end time of the event.
                - dateTime (str): The date and time of the end time in ISO 8601(YYYY-MM-DDTHH:MM:SSZ) format.

    Raises:
        TypeError: If any argument has an invalid type:
            - calendarId is not str
            - sendUpdates is not str (if provided)
            - text is not str
        InvalidInputError: If any argument has an invalid value:
            - calendarId is empty/whitespace
            - text is empty/whitespace
            - sendUpdates has invalid value (not one of: "all", "externalOnly", "none")
    """
    # Type validations
    if not isinstance(calendarId, str):
        raise TypeError("calendarId must be a string.")
    if sendUpdates is not None and not isinstance(sendUpdates, str):
        raise TypeError("sendUpdates must be a string if provided.")
    if text is not None and not isinstance(text, str):
        raise TypeError("text must be a string if provided.")

    # Value validations
    if not calendarId.strip():
        raise InvalidInputError("calendarId cannot be empty or whitespace.")
    if not text or not text.strip():
        raise InvalidInputError("text parameter is required and cannot be empty or whitespace.")
    if sendUpdates is not None:
        valid_send_updates = ["all", "externalOnly", "none"]
        if sendUpdates not in valid_send_updates:
            raise InvalidInputError(f"sendUpdates must be one of: {', '.join(valid_send_updates)}")

    # Create event
    ev_id = str(uuid.uuid4())
    resource = {"id": ev_id, "summary": text}
    DB["events"][(calendarId, ev_id)] = resource

    try:
        notify_attendees(calendarId, resource, sendUpdates, subject_prefix="Invitation")
    except Exception:
        # Non-fatal in simulation
        pass
    return resource

def update_event(eventId: str, calendarId: Optional[str] = None, resource: Optional[Dict[str, Any]] = None, sendUpdates: str = None) -> Dict[str, Any]:
    """
    Replaces an existing event with new data.

    Args:
        eventId (str): The identifier of the event to update.
        calendarId (Optional[str]): The identifier of the calendar.
        resource (Optional[Dict[str, Any]]): The event to update. Must contain:
        sendUpdates (str, optional): Whether to send updates about the update.
            Possible values: "all", "externalOnly", "none". Defaults to None.
            Note: sendUpdates functionality is not implemented yet.
            - summary (str): The summary/title of the event.
            - id (Optional[str]): The identifier of the event.
            - description (Optional[str]): The description of the event.
            - start (Optional[Dict[str, Any]]): The start time of the event.
                - dateTime (Optional[str]): The date and time of the start time in ISO 8601(YYYY-MM-DDTHH:MM:SSZ) format.
                - timeZone (Optional[str]): The time zone of the start time.
            - end (Optional[Dict[str, Any]]): The end time of the event.
                - dateTime (Optional[str]): The date and time of the end time in ISO 8601(YYYY-MM-DDTHH:MM:SSZ) format.
                - timeZone (Optional[str]): The time zone of the end time.
            - recurrence (Optional[List[str]]): The recurrence rules of the event in RRULE format.
                Examples:
                - Daily for 5 occurrences: ["RRULE:FREQ=DAILY;COUNT=5"]
                - Weekly on Monday and Wednesday: ["RRULE:FREQ=WEEKLY;BYDAY=MO,WE"]
                - Monthly on the 15th: ["RRULE:FREQ=MONTHLY;BYMONTHDAY=15"]
                - Yearly on January 1st: ["RRULE:FREQ=YEARLY;BYMONTH=1;BYMONTHDAY=1"]
                - Every 2 weeks: ["RRULE:FREQ=WEEKLY;INTERVAL=2"]
                - Until a specific date: ["RRULE:FREQ=DAILY;UNTIL=20241231T235959Z"]
                
                Supported RRULE parameters:
                - FREQ: SECONDLY, MINUTELY, HOURLY, DAILY, WEEKLY, MONTHLY, YEARLY (required)
                - INTERVAL: Positive integer (default: 1)
                - COUNT: Positive integer (number of occurrences)
                - UNTIL: YYYYMMDDTHHMMSSZ or YYYYMMDDTHHMMSS format
                - BYDAY: SU,MO,TU,WE,TH,FR,SA (with optional ordinal: 1SU, -1MO)
                - BYMONTH: 1-12
                - BYMONTHDAY: 1-31
                - BYYEARDAY: 1-366
                - BYWEEKNO: 1-53
                - BYHOUR: 0-23
                - BYMINUTE: 0-59
                - BYSECOND: 0-59
                - BYSETPOS: 1-366 or -366 to -1
                - WKST: SU,MO,TU,WE,TH,FR,SA (week start)
                
            - attendees (Optional[List[Dict[str, Any]]]): List of event attendees. Each attendee can have:
                - email (Optional[str]): The attendee's email address
                - displayName (Optional[str]): The attendee's display name
                - organizer (Optional[bool]): Whether the attendee is the organizer
                - self (Optional[bool]): Whether the attendee is the user
                - resource (Optional[bool]): Whether the attendee is a resource
                - optional (Optional[bool]): Whether the attendee's presence is optional
                - responseStatus (Optional[str]): The attendee's response status
                - comment (Optional[str]): The attendee's comment
                - additionalGuests (Optional[int]): Number of additional guests
            - reminders (Optional[Dict[str, Any]]): The reminders of the event.
                - useDefault (Optional[bool]): Whether to use the default reminders.
                - overrides (Optional[List[Dict[str, Any]]]): The list of overrides.
                    - method (Optional[str]): The method of the reminder.
                    - minutes (Optional[int]): The minutes of the reminder.
            - location (Optional[str]): The location of the event.

    Returns:
        Dict[str, Any]: The updated event.
            - id (str): The identifier of the event.
            - summary (str): The summary of the event.
            - description (Optional[str]): The description of the event.
            - start (Optional[Dict[str, Any]]): The start time of the event.
                - dateTime (Optional[str]): The date and time of the start time.
                - timeZone (Optional[str]): The time zone of the start time.
            - end (Optional[Dict[str, Any]]): The end time of the event.
                - dateTime (Optional[str]): The date and time of the end time.
                - timeZone (Optional[str]): The time zone of the end time.
            - attendees (Optional[List[Dict[str, Any]]]): List of event attendees with their details.
            - recurrence (Optional[List[str]]): The recurrence rules of the event in RRULE format.
            - reminders (Optional[Dict[str, Any]]): The reminders of the event.
            - location (Optional[str]): The location of the event.

    Raises:
        TypeError: If calendarId or eventId is provided and not a string, or sendUpdates is not a string (if provided).
        InvalidInputError: If eventId is None, calendarId is empty/whitespace, eventId is empty/whitespace,
            resource is not provided, resource data does not match the expected structure,
            or sendUpdates has an invalid value (not one of: "all", "externalOnly", "none").
            This includes validation errors for recurrence rules.
        ResourceNotFoundError: If the event is not found in the calendar.

    Examples:
        # Update an event to be recurring
        event = update_event("event123", "primary", {
            "summary": "Updated Team Meeting",
            "start": {"dateTime": "2024-01-15T10:00:00Z"},
            "end": {"dateTime": "2024-01-15T11:00:00Z"},
            "recurrence": ["RRULE:FREQ=WEEKLY;BYDAY=MO"]
        })
        
        # Update a recurring event to change its pattern
        event = update_event("event456", "primary", {
            "summary": "Bi-weekly Review",
            "recurrence": ["RRULE:FREQ=WEEKLY;INTERVAL=2;BYDAY=FR"]
        })
    """
    # --- Input Validation ---
    # Validate calendarId
    if calendarId is not None:
        if not isinstance(calendarId, str):
            raise TypeError("calendarId must be a string if provided.")
        if not calendarId.strip():
            raise InvalidInputError("calendarId cannot be empty or whitespace.")

    # Validate eventId
    if eventId is None:
        raise InvalidInputError("eventId is required for updating an event.")
    if not isinstance(eventId, str):
        raise TypeError("eventId must be a string if provided.")
    if not eventId.strip():
        raise InvalidInputError("eventId cannot be empty or whitespace.")

    # Validate sendUpdates
    if sendUpdates is not None:
        if not isinstance(sendUpdates, str):
            raise TypeError("sendUpdates must be a string if provided.")
        valid_send_updates = ["all", "externalOnly", "none"]
        if sendUpdates not in valid_send_updates:
            raise InvalidInputError(f"sendUpdates must be one of: {', '.join(valid_send_updates)}")

    # Default calendarId if None
    effective_calendarId = calendarId if calendarId is not None else "primary"

    # Validate resource
    if resource is None:
        raise InvalidInputError("Resource body is required for full update.")

    # Validate resource structure using Pydantic model
    # This includes validation of recurrence rules through the field validator
    try:
        validated_resource_model = EventPatchResourceModel(**resource)
        # Convert back to dict, excluding unset fields
        validated_resource = validated_resource_model.model_dump(exclude_unset=True)
    except ValidationError as e:
        # Convert Pydantic ValidationError to InvalidInputError
        raise InvalidInputError(str(e))

    # Check if event exists
    key = (effective_calendarId, eventId)
    if key not in DB["events"]:
        raise ResourceNotFoundError(f"Event '{eventId}' not found in calendar '{effective_calendarId}'.")

    # Update with validated data
    validated_resource["id"] = eventId
    DB["events"][key] = validated_resource

    try:
        notify_attendees(effective_calendarId, validated_resource, sendUpdates, subject_prefix="Updated")
    except Exception:
        pass
    return validated_resource


def watch_events(
    alwaysIncludeEmail: Optional[bool] = False,
    calendarId: Optional[str] = None,
    eventTypes: Optional[List[str]] = None,
    iCalUID: Optional[str] = None,
    maxAttendees: Optional[int] = None,
    maxResults: Optional[int] = 250,
    orderBy: Optional[str] = None,
    pageToken: Optional[str] = None,
    privateExtendedProperty: Optional[List[str]] = None,
    q: Optional[str] = None,
    sharedExtendedProperty: Optional[List[str]] = None,
    showDeleted: Optional[bool] = False,
    showHiddenInvitations: Optional[bool] = False,
    singleEvents: Optional[bool] = False,
    syncToken: Optional[str] = None,
    timeMax: Optional[str] = None,
    timeMin: Optional[str] = None,
    timeZone: Optional[str] = None,
    updatedMin: Optional[str] = None,
    resource: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Sets up a watch for changes to events in the specified calendar.

    Args:
        alwaysIncludeEmail (Optional[bool]): Whether to always include the email address
            of the event creator. Defaults to False.
        calendarId (Optional[str]): The identifier of the calendar. If not provided,
            defaults to the user's primary calendar.
        eventTypes (Optional[List[str]]): The types of events to watch for.
            Must be one or more of: "default", "focusTime", "outOfOffice".
        iCalUID (Optional[str]): The iCalUID of the event to filter by.
        maxAttendees (Optional[int]): The maximum number of attendees to return per event.
            Must be a positive integer if provided.
        maxResults (Optional[int]): The maximum number of events to return.
            Must be a positive integer. Defaults to 250.
        orderBy (Optional[str]): The order of the events.
            Must be one of: "startTime", "updated".
        pageToken (Optional[str]): Token specifying which result page to return.
        privateExtendedProperty (Optional[List[str]]): Private extended property filters
            in the form "key=value".
        q (Optional[str]): Free text search terms to find events that match.
        sharedExtendedProperty (Optional[List[str]]): Shared extended property filters
            in the form "key=value".
        showDeleted (Optional[bool]): Whether to include deleted events.
            Defaults to False.
        showHiddenInvitations (Optional[bool]): Whether to include hidden invitations.
            Defaults to False.
        singleEvents (Optional[bool]): Whether to expand recurring events into instances.
            Defaults to False.
        syncToken (Optional[str]): Token obtained from the nextSyncToken field returned on the
            last page of results from the previous list request.
        timeMax (Optional[str]): Upper bound (exclusive) for an event's start time in
            ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ).
        timeMin (Optional[str]): Lower bound (inclusive) for an event's end time in
            ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ).
        timeZone (Optional[str]): Time zone used in the response (e.g. "America/New_York").
            The default is the calendar's time zone.
        updatedMin (Optional[str]): Lower bound for an event's last modification time in
            ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ).
        resource (Optional[Dict[str, Any]]): The watch configuration:
            - id (Optional[str]): The identifier of the watch. If not provided,
                a new UUID will be generated.
            - type (Optional[str]): The type of the watch. Defaults to "web_hook".
            - address (Optional[str]): The address to send notifications to.

    Returns:
        Dict[str, Any]: The created watch channel:
            - id (str): The identifier of the watch channel.
            - type (str): The type of the watch.
            - calendarId (str): The identifier of the watched calendar.
            - resource (str): The resource being watched.

    Raises:
        TypeError: If any argument has an invalid type:
            - Boolean parameters are not bool
            - String parameters are not str
            - List parameters are not list
            - Integer parameters are not int
            - resource is not a dict
        InvalidInputError: If any argument has an invalid value:
            - maxResults or maxAttendees is not positive
            - eventTypes contains invalid event type
            - orderBy has invalid value
            - timeMax, timeMin, or updatedMin has invalid format
            - timeZone has invalid format
            - resource is missing required 'address' field
            - resource has invalid 'type' value
    """
    # --- Type validations ---
    # Boolean parameters
    if not isinstance(alwaysIncludeEmail, bool):
        raise TypeError("alwaysIncludeEmail must be a boolean.")
    if not isinstance(showDeleted, bool):
        raise TypeError("showDeleted must be a boolean.")
    if not isinstance(showHiddenInvitations, bool):
        raise TypeError("showHiddenInvitations must be a boolean.")
    if not isinstance(singleEvents, bool):
        raise TypeError("singleEvents must be a boolean.")

    # String parameters
    if calendarId is not None and not isinstance(calendarId, str):
        raise TypeError("calendarId must be a string if provided.")
    if iCalUID is not None and not isinstance(iCalUID, str):
        raise TypeError("iCalUID must be a string if provided.")
    if orderBy is not None and not isinstance(orderBy, str):
        raise TypeError("orderBy must be a string if provided.")
    if pageToken is not None and not isinstance(pageToken, str):
        raise TypeError("pageToken must be a string if provided.")
    if q is not None and not isinstance(q, str):
        raise TypeError("q must be a string if provided.")
    if syncToken is not None and not isinstance(syncToken, str):
        raise TypeError("syncToken must be a string if provided.")
    if timeMax is not None and not isinstance(timeMax, str):
        raise TypeError("timeMax must be a string if provided.")
    if timeMin is not None and not isinstance(timeMin, str):
        raise TypeError("timeMin must be a string if provided.")
    if timeZone is not None and not isinstance(timeZone, str):
        raise TypeError("timeZone must be a string if provided.")
    if updatedMin is not None and not isinstance(updatedMin, str):
        raise TypeError("updatedMin must be a string if provided.")

    # Integer parameters
    if maxAttendees is not None and not isinstance(maxAttendees, int):
        raise TypeError("maxAttendees must be an integer if provided.")
    if not isinstance(maxResults, int):
        raise TypeError("maxResults must be an integer.")

    # List parameters
    if eventTypes is not None and not isinstance(eventTypes, list):
        raise TypeError("eventTypes must be a list if provided.")
    if privateExtendedProperty is not None and not isinstance(
        privateExtendedProperty, list
    ):
        raise TypeError("privateExtendedProperty must be a list if provided.")
    if sharedExtendedProperty is not None and not isinstance(
        sharedExtendedProperty, list
    ):
        raise TypeError("sharedExtendedProperty must be a list if provided.")

    # Resource parameter
    if resource is not None and not isinstance(resource, dict):
        raise TypeError("resource must be a dictionary.")

    # --- Value validations ---
    # Numeric value validations
    if maxAttendees is not None and maxAttendees <= 0:
        raise InvalidInputError("maxAttendees must be a positive integer.")
    if maxResults <= 0:
        raise InvalidInputError("maxResults must be a positive integer.")

    # Event types validation
    valid_event_types = {"default", "focusTime", "outOfOffice"}
    if eventTypes is not None:
        invalid_types = [t for t in eventTypes if t not in valid_event_types]
        if invalid_types:
            raise InvalidInputError(
                f"Invalid event types: {', '.join(invalid_types)}. "
                f"Must be one of: {', '.join(valid_event_types)}"
            )

    # Order by validation
    valid_order_by = {"startTime", "updated"}
    if orderBy is not None and orderBy not in valid_order_by:
        raise InvalidInputError(
            f"Invalid orderBy value: {orderBy}. Must be one of: {', '.join(valid_order_by)}"
        )

    # Time format validations
    for time_param, time_value in [
        ("timeMax", timeMax),
        ("timeMin", timeMin),
        ("updatedMin", updatedMin),
    ]:
        if time_value is not None:
            try:
                parse_iso_datetime(time_value)
            except ValueError as e:
                raise InvalidInputError(
                    f"Invalid {time_param} format: {str(e)}. Must be in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)."
                )

    # Timezone validation
    if timeZone is not None:
        if not timeZone.strip():
            raise InvalidInputError("timeZone cannot be empty or whitespace.")
        # Basic timezone format validation
        if "/" not in timeZone:
            raise InvalidInputError(
                "timeZone must be in format 'Continent/City' (e.g., 'America/New_York')."
            )

    # Resource validation
    if resource is None:
        raise InvalidInputError("Channel resource is required to watch.")

    # Set default calendar ID if not provided
    effective_calendarId = calendarId if calendarId is not None else "primary"

    # Create and store channel
    channel_id = resource.get("id") or str(uuid.uuid4())
    DB["channels"][channel_id] = {
        "id": channel_id,
        "type": resource.get("type", "web_hook"),
        "resource": "events",
        "calendarId": effective_calendarId,
    }
    return DB["channels"][channel_id]
