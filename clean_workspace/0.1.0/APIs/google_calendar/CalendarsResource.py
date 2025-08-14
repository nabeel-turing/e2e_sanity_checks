# APIs/google_calendar/CalendarsResource/__init__.py
import uuid
from typing import Dict, Any, Optional, List

from pydantic import ValidationError

from .SimulationEngine.models import CalendarResourceInputModel
from .SimulationEngine.db import DB
from .SimulationEngine.utils import get_primary_calendar_entry

def clear_calendar(calendarId: str) -> Dict[str, Any]:
    """
    Clears a primary calendar. This operation deletes all events associated with the specified calendar.

    Args:
        calendarId (str): The identifier of the calendar.
            - To retrieve calendar IDs, call the `calendarList.list` method.
            - Use the keyword "primary" to access the primary calendar of the currently logged-in user.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - success (bool): Whether the operation was successful.
            - message (str): A message describing the result of the operation.
    """
    if not isinstance(calendarId, str):
        raise TypeError(f"CalendarId must be a string: {calendarId}")

    if calendarId == "primary":
        calendarId = get_primary_calendar_entry()["id"]

    if calendarId not in DB["calendar_list"]:
        raise ValueError(f"Calendar '{calendarId}' not found.")
    
    to_delete = []
    for (cal_id, ev_id), ev_obj in DB["events"].items():
        if cal_id == calendarId:
            to_delete.append((cal_id, ev_id))
    for key in to_delete:
        DB["events"].pop(key)
    return {
        "success": True,
        "message": f"All events deleted for calendar '{calendarId}'.",
    }


def delete_calendar(calendarId: str) -> Dict[str, Any]:
    """
    Deletes a secondary calendar. This operation removes the calendar from the user's calendar list.
    Note: Primary calendars cannot be deleted.

    Args:
        calendarId (str): The identifier of the secondary calendar to delete.
            To retrieve calendar IDs, call the `calendarList.list` method.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - success (bool): Whether the operation was successful.
            - message (str): A message describing the result of the operation.

    Raises:
        ValueError: If the calendar is not found or if attempting to delete a primary calendar.
        TypeError: If the calendar ID is not a string.
    """
    primary_calendar_id = get_primary_calendar_entry()["id"]
    if not isinstance(calendarId, str):
        raise TypeError(f"CalendarId must be a string: {calendarId}")
    if calendarId == "primary" or calendarId == primary_calendar_id:
        raise ValueError("Cannot delete the primary calendar.")
    if calendarId not in DB["calendar_list"]:
        raise ValueError(f"Calendar '{calendarId}' not found.")
    if calendarId in DB["calendar_list"]:
        del DB["calendar_list"][calendarId]
    if calendarId in DB["calendars"]:
        del DB["calendars"][calendarId]
    return {"success": True, "message": f"Calendar '{calendarId}' deleted."}


def get_calendar(calendarId: str) -> Dict[str, Any]:
    """
    Retrieves metadata for a specified calendar.

    Args:
        calendarId (str): The identifier of the calendar.
            - To retrieve calendar IDs, call the `calendarList.list` method.
            - Use the keyword "primary" to access the primary calendar of the currently logged-in user.

    Returns:
        Dict[str, Any]: A dictionary containing the calendar metadata:
            - id (str): The identifier of the calendar.
            - summary (str): The summary of the calendar.
            - description (str): The description of the calendar.
            - timeZone (str): The time zone of the calendar (e.g. "America/New_York").
            - primary (bool): Whether the calendar is the primary calendar.
    Raises:
        TypeError: If calendarId is not a string.
        ValueError: If the calendar is not found
    """
    if not isinstance(calendarId, str):
        raise TypeError("calendarId must be a string.")
    if calendarId == "primary":
        calendarId = get_primary_calendar_entry()["id"]
    if calendarId not in DB["calendar_list"]:
        raise ValueError(f"Calendar '{calendarId}' not found.")
    return DB["calendar_list"][calendarId]


def create_calendar(resource: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Creates a secondary calendar.

    Args:
        resource (Optional[Dict[str, Any]]): The resource to create the calendar with.
            - id (Optional[str]): The identifier of the calendar.
            - summary (Optional[str]): The Title of the calendar.
            - description (Optional[str]): The description of the calendar.
            - timeZone (Optional[str]): The time zone of the calendar (e.g. "America/New_York").
            - location (Optional[str]): Geographic location of the calendar as free-form text.
            - etag (Optional[str]): ETag of the resource. Used for optimistic concurrency control.
            - kind (Optional[str]): Type of the resource ("calendar#calendar").
            - conferenceProperties (Optional[Dict[str, Any]]): Conference-related properties.
                - allowedConferenceSolutionTypes (Optional[List[str]]): List of conference solution types that are supported for this calendar.
                    Each string in the list can be one of:
                    - "eventHangout"
                    - "eventNamedHangout"
                    - "hangoutsMeet"

    Returns:
        Dict[str, Any]: The created calendar.
            - id (str): The identifier of the calendar.
            - summary (Optional[str]): The Title of the calendar.
            - description (Optional[str]): The description of the calendar.
            - timeZone (Optional[str]): The time zone of the calendar (e.g. "America/New_York").
            - location (Optional[str]): The geographic location of the calendar.
            - etag (Optional[str]): ETag of the resource.
            - kind (Optional[str]): Type of the resource ("calendar#calendar").
            - conferenceProperties (Optional[Dict[str, Any]]): Conference-related properties.
                - allowedConferenceSolutionTypes (Optional[List[str]]): List of conference solution types that are supported for this calendar.
            - primary (bool): Whether the calendar is the primary calendar.
    Raises:
        ValueError: If the resource is not provided.
        ValidationError: If the 'resource' dictionary does not conform to the expected validations
    """
    # Original check for resource presence
    if resource is None:
        raise ValueError("Resource is required to create a calendar.")

    # Pydantic validation for the resource dictionary
    try:
        validated_resource_model = CalendarResourceInputModel(**resource)
    except ValidationError as e:
        raise e

    cal_id = validated_resource_model.id or str(uuid.uuid4())
    calendar_data_to_store = validated_resource_model.model_dump(exclude_none=True)
    calendar_data_to_store["id"] = cal_id # Ensure 'id' is set

    if validated_resource_model.kind is None and "kind" in calendar_data_to_store and calendar_data_to_store["kind"] is None:
        pass

    # Original database interaction logic (assuming DB is globally available)
    DB["calendar_list"][cal_id] = calendar_data_to_store
    DB["calendars"][cal_id] = calendar_data_to_store
    
    return calendar_data_to_store


def patch_calendar(
    calendarId: str, resource: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Updates specific fields of an existing calendar.

    Args:
        calendarId (str): The identifier of the calendar.
            - To retrieve calendar IDs, call the `calendarList.list` method.
            - Use the keyword "primary" to access the primary calendar of the currently logged-in user.
        resource (Optional[Dict[str, Any]]): The resource to patch the calendar with.
            - summary (Optional[str]): The summary of the calendar.
            - description (Optional[str]): The description of the calendar.
            - timeZone (Optional[str]): The time zone of the calendar (e.g. "America/New_York").

    Returns:
        Dict[str, Any]: The patched calendar.
            - id (str): The identifier of the calendar.
            - summary (str): The summary of the calendar.
            - description (str): The description of the calendar.
            - timeZone (str): The time zone of the calendar (e.g. "America/New_York").
            - primary (bool): Whether the calendar is the primary calendar.
    Raises:
        TypeError: If calendarId is not a string or if resource values have invalid types.
        ValueError: If the calendar is not found or if resource contains invalid fields.
    """
    # Input validation for calendarId
    if not isinstance(calendarId, str):
        raise TypeError("calendarId must be a string.")
    
    # Check if calendar exists
    if calendarId not in DB["calendar_list"]:
        raise ValueError(f"Calendar '{calendarId}' not found.")

    if calendarId == "primary":
        calendarId = get_primary_calendar_entry()["id"]
    
    # Get existing calendar data
    existing = DB["calendar_list"][calendarId]
    
    # If no resource provided, return existing calendar
    if resource is None:
        return existing
    
    # Validate resource parameter
    if not isinstance(resource, dict):
        raise TypeError("resource must be a dictionary.")
    
    # Define allowed fields for patching
    allowed_fields = {"summary", "description", "timeZone"}
    
    # Validate resource fields and types
    for key, value in resource.items():
        # Check if field is allowed
        if key not in allowed_fields:
            raise ValueError(f"Field '{key}' is not allowed for calendar patching. Allowed fields: {', '.join(sorted(allowed_fields))}")
        
        # Type validation for each field
        if value is not None:  # Allow None values to clear fields
            if not isinstance(value, str):
                raise TypeError(f"Field '{key}' must be a string, got {type(value).__name__}.")
            
            # Additional validation for specific fields
            if key == "timeZone" and value.strip() == "":
                raise ValueError("timeZone cannot be an empty string.")
    
    # Apply patches to existing calendar
    for key, value in resource.items():
        existing[key] = value
    
    # Update both calendar_list and calendars storage
    DB["calendar_list"][calendarId] = existing
    DB["calendars"][calendarId] = existing
    
    return existing


def update_calendar(
    calendarId: str, resource: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Replaces an existing calendar with new data.

    Args:
        calendarId (str): The identifier of the calendar.
            - To retrieve calendar IDs, call the `calendarList.list` method.
            - Use the keyword "primary" to access the primary calendar of the currently logged-in user.
        resource (Optional[Dict[str, Any]]): The resource to update the calendar with.
            - summary (Optional[str]): The summary of the calendar.
            - description (Optional[str]): The description of the calendar.
            - timeZone (Optional[str]): The time zone of the calendar (e.g. "America/New_York").

    Returns:
        Dict[str, Any]: The updated calendar.
            - id (str): The identifier of the calendar.
            - summary (str): The summary of the calendar.
            - description (str): The description of the calendar.
            - timeZone (str): The time zone of the calendar (e.g. "America/New_York").
            - primary (bool): Whether the calendar is the primary calendar.
    Raises:
        ValueError: If the calendar is not found or if the resource is not provided.
    """
    if calendarId == "primary":
        calendarId = get_primary_calendar_entry()["id"]
    if calendarId not in DB["calendar_list"]:
        raise ValueError(f"Calendar '{calendarId}' not found.")
    if resource is None:
        raise ValueError("Resource is required for full update.")
    resource["id"] = calendarId
    DB["calendar_list"][calendarId] = resource
    DB["calendars"][calendarId] = resource
    return resource
