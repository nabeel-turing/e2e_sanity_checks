# APIs/google_calendar/CalendarListResource/__init__.py
import uuid
from typing import Dict, Any, List, Optional

from pydantic import ValidationError

from .SimulationEngine.models import CalendarListResourceInput
from .SimulationEngine.db import DB
from .SimulationEngine.utils import get_primary_calendar_list_entry

def delete_calendar_list(calendarId: str) -> Dict[str, Any]:
    """
    Deletes a calendar list entry from the user's calendar list.

    Args:
        calendarId (str): The ID of the calendar list entry to delete.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - success (bool): True if the calendar list entry was deleted successfully.
            - message (str): A message indicating the result of the operation.

    Raises:
        TypeError: If calendarId is not a string.
        ValueError: If calendarId is empty or None, or if the calendar list entry is not found.
    """

    # Input validation
    if not isinstance(calendarId, str):
        raise TypeError("calendarId must be a string")
    if not calendarId or not calendarId.strip():
        raise ValueError("calendarId cannot be empty or None")
    
    # Check if calendar list entry exists
    if calendarId not in DB["calendar_list"]:
        raise ValueError(f"CalendarList entry '{calendarId}' not found.")
    
    primary_calendar_id = get_primary_calendar_list_entry()["id"]
    if calendarId == "primary" or calendarId == primary_calendar_id:
        raise ValueError("Cannot delete the primary calendar.")
    
    # Delete the calendar list entry
    del DB["calendar_list"][calendarId]
    return {"success": True, "message": f"CalendarList entry {calendarId} deleted."}


def get_calendar_list(calendarId: str) -> Dict[str, Any]:
    """
    Retrieves a calendar list entry from the user's calendar list.

    Args:
        calendarId (str): The ID of the calendar list entry to retrieve. If "primary" is provided, the primary calendar will be returned.

    Returns:
        Dict[str, Any]: A dictionary containing the calendar list entry details:
            - id (str): The ID of the calendar list entry.
            - summary (str): The summary of the calendar list entry.
            - description (str): The description of the calendar list entry.
            - timeZone (str): The time zone of the calendar list entry (e.g. "America/New_York").

    Raises:
        TypeError: If calendarId is not a string.
        ValueError: If the calendar list entry is not found.
    """
    if not isinstance(calendarId, str):
        raise TypeError(f"calendarId must be a string, but got {type(calendarId).__name__}.")
    if calendarId == "primary":
        calendarId = get_primary_calendar_list_entry()["id"]
    if calendarId not in DB["calendar_list"]:
        raise ValueError(f"CalendarList entry '{calendarId}' not found.")
        
    entry = DB["calendar_list"][calendarId]

    # Ensure the 'id' field is present, using calendarId as the source of truth.
    if "id" not in entry:
        entry["id"] = calendarId
        
    return entry

def create_calendar_list(resource: Dict[str, Any]) -> Dict[str, Any]:
    """
    Creates a new calendar list entry in the user's calendar list.

    Args:
        resource (Dict[str, Any]): The resource to create the calendar list entry with.
            - id (Optional[str]): The ID of the calendar list entry. If not provided, a UUID will be generated.
            - summary (str): The summary of the calendar list entry.
            - description (str): The description of the calendar list entry.
            - timeZone (str): The time zone of the calendar list entry (e.g. "America/New_York").

    Returns:
        Dict[str, Any]: A dictionary containing the created calendar list entry.
            - id (str): The ID of the calendar list entry.
            - summary (str): The summary of the calendar list entry.
            - description (str): The description of the calendar list entry.
            - timeZone (str): The time zone of the calendar list entry (e.g. "America/New_York").
            - primary (bool): Whether the calendar list entry is the primary calendar.

    Raises:
        ValueError: If the resource is not provided.
        ValidationError: If the resource structure is invalid.
    """
    if resource is None:
        raise ValueError("Resource is required to create a calendar list entry.")

    try:
        validated_resource_model = CalendarListResourceInput(**resource)
    except ValidationError as e:
        raise e

    cal_id = validated_resource_model.id or str(uuid.uuid4())

    resource_data_to_store = validated_resource_model.model_dump(exclude_none=True)
    resource_data_to_store["id"] = cal_id

    DB["calendar_list"][cal_id] = resource_data_to_store
    
    return DB["calendar_list"][cal_id]


def list_calendar_lists(maxResults: int = 100) -> Dict[str, Any]:
    """
    Lists all calendar list entries in the user's calendar list.

    Args:
        maxResults (int): Maximum number of calendar list entries to return.
            Must be a positive integer. Defaults to 100.
            
    Returns:
        Dict[str, Any]: A dictionary containing the calendar list entries.
            - items (List[Dict[str, Any]]): A list of calendar list entries.
                - id (str): The ID of the calendar list entry.
                - summary (str): The summary of the calendar list entry.
                - description (str): The description of the calendar list entry.
                - timeZone (str): The time zone of the calendar list entry.
                - primary (bool): Whether the calendar list entry is the primary calendar.
            - nextPageToken (str): The next page token to use for pagination. Not implemented.

    Raises:
        TypeError: If maxResults is not an integer.
        ValueError: If maxResults is not a positive integer.
    """

    # --- Input Validation ---
    if not isinstance(maxResults, int):
        raise TypeError("maxResults must be an integer.")
    if maxResults <= 0:
        # Business rule: maxResults should be a positive number.
        raise ValueError("maxResults must be a positive integer.")
    # --- End of Input Validation ---
    all_items = list(DB["calendar_list"].values())
    result = all_items[:maxResults]
    return {"items": result, "nextPageToken": None}


def patch_calendar_list(
    calendarId: str,
    colorRgbFormat: bool = False,
    resource: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Updates specific fields of an existing calendar list entry.

    Args:
        calendarId (str): The ID of the calendar list entry to patch. If "primary" is provided, the primary calendar will be patched.
        colorRgbFormat (bool): Whether to use RGB color format. Defaults to False.
        resource (Dict[str, Any]): The resource to patch the calendar list entry with.
            - summary (str): The summary of the calendar list entry.
            - description (str): The description of the calendar list entry.
            - timeZone (str): The time zone of the calendar list entry (e.g. "America/New_York").

    Returns:
        Dict[str, Any]: A dictionary containing the complete patched calendar list entry with all fields,
                       including both updated and unchanged fields. The structure includes:
            - id (str): The ID of the calendar list entry.
            - summary (str): The summary of the calendar list entry.
            - description (str): The description of the calendar list entry.
            - timeZone (str): The time zone of the calendar list entry (e.g. "America/New_York").
            - primary (bool): Whether the calendar list entry is the primary calendar.
    Raises:
        TypeError: If calendarId is not a string, if colorRgbFormat is not a boolean,
                  or if resource is not a dictionary.
        ValueError: If calendarId is empty or None, if the calendar list entry is not found,
                   or if resource contains invalid field types for known fields.
    """
    if colorRgbFormat is None:
        colorRgbFormat = False

    # Input validation
    if not isinstance(calendarId, str):
        raise TypeError("calendarId must be a string")
    if not isinstance(colorRgbFormat, bool):
        raise TypeError("colorRgbFormat must be a boolean")
    if resource is not None and not isinstance(resource, dict):
        raise TypeError("resource must be a dictionary")
    
    if not calendarId or not calendarId.strip():
        raise ValueError("calendarId cannot be empty or None")
    
    if calendarId == "primary":
        calendarId = get_primary_calendar_list_entry()["id"]
    
    # Check if calendar list entry exists
    if calendarId not in DB["calendar_list"]:
        raise ValueError(f"CalendarList entry '{calendarId}' not found.")
    
    existing = DB["calendar_list"][calendarId]
    
    # Validate and apply resource updates if provided
    if resource:
        # Validate known field types
        if "summary" in resource:
            if not isinstance(resource["summary"], str):
                raise ValueError("Field 'summary' must be a string")
        
        if "description" in resource:
            if not isinstance(resource["description"], str):
                raise ValueError("Field 'description' must be a string")
        
        if "timeZone" in resource:
            if not isinstance(resource["timeZone"], str):
                raise ValueError("Field 'timeZone' must be a string")
        
        if "id" in resource:
            if not isinstance(resource["id"], str):
                raise ValueError("Field 'id' must be a string")
        
        # Security: Prevent modification of the ID field
        if "id" in resource and resource["id"] != calendarId:
            raise ValueError("Cannot modify the 'id' field of an existing calendar list entry")
        
        # Apply updates
        for k, v in resource.items():
            existing[k] = v
    
    # Note: colorRgbFormat parameter is accepted for API compatibility but not implemented in simulation
    
    DB["calendar_list"][calendarId] = existing
    return existing


def update_calendar_list(
    calendarId: str,
    colorRgbFormat: bool = False,
    resource: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Replaces an existing calendar list entry with new data.

    Args:
        calendarId (str): The ID of the calendar list entry to replace. If "primary" is provided, the primary calendar will be replaced.
        colorRgbFormat (bool): Whether to use RGB color format. Defaults to False.
        resource (Dict[str, Any]): The resource to replace the calendar list entry with.
            - summary (str): The summary of the calendar list entry.
            - description (str): The description of the calendar list entry.
            - timeZone (str): The time zone of the calendar list entry (e.g. "America/New_York").

    Returns:
        Dict[str, Any]: A dictionary containing the replaced calendar list entry.
            - id (str): The ID of the calendar list entry.
            - summary (str): The summary of the calendar list entry.
            - description (str): The description of the calendar list entry.
            - timeZone (str): The time zone of the calendar list entry (e.g. "America/New_York").
            - primary (bool): Whether the calendar list entry is the primary calendar.
    Raises:
        TypeError: If calendarId is not a string, if colorRgbFormat is not a boolean,
                  or if resource is not a dictionary.
        ValueError: If calendarId is empty or None, if the calendar list entry is not found,
                   if resource is not provided, or if resource contains invalid field types
                   for known fields.
    """
    # Input validation
    if not isinstance(calendarId, str):
        raise TypeError("calendarId must be a string")
    if not isinstance(colorRgbFormat, bool):
        raise TypeError("colorRgbFormat must be a boolean")
    if resource is not None and not isinstance(resource, dict):
        raise TypeError("resource must be a dictionary")
    
    if not calendarId or not calendarId.strip():
        raise ValueError("calendarId cannot be empty or None")
    
    if resource is None:
        raise ValueError("Resource is required for full update.")

    if calendarId == "primary":
        calendarId = get_primary_calendar_list_entry()["id"]

    if calendarId not in DB["calendar_list"]:
        raise ValueError(f"CalendarList entry '{calendarId}' not found.")
    
    # Check if calendar list entry exists
    if calendarId not in DB["calendar_list"]:
        raise ValueError(f"CalendarList entry '{calendarId}' not found.")
    
    # Create a copy to avoid modifying the original input
    updated_resource = resource.copy()
    
    # Validate known field types
    if "summary" in updated_resource:
        if not isinstance(updated_resource["summary"], str):
            raise ValueError("Field 'summary' must be a string")
    
    if "description" in updated_resource:
        if not isinstance(updated_resource["description"], str):
            raise ValueError("Field 'description' must be a string")
    
    if "timeZone" in updated_resource:
        if not isinstance(updated_resource["timeZone"], str):
            raise ValueError("Field 'timeZone' must be a string")
    
    # Security: Prevent or validate ID field modification
    if "id" in updated_resource:
        if not isinstance(updated_resource["id"], str):
            raise ValueError("Field 'id' must be a string")
        if updated_resource["id"] != calendarId:
            raise ValueError("Cannot set 'id' field to a different value than calendarId")
    
    # Set the ID to match the calendarId (this replaces the entire entry)
    updated_resource["id"] = calendarId
    
    # Note: colorRgbFormat parameter is accepted for API compatibility but not implemented in simulation
    
    # Replace the entire entry in the database
    DB["calendar_list"][calendarId] = updated_resource
    return updated_resource


def watch_calendar_lists(
    maxResults: Optional[int] = 100,
    minAccessRole: Optional[str] = None,
    pageToken: Optional[str] = None,
    showDeleted: Optional[bool] = False,
    showHidden: Optional[bool] = False,
    syncToken: Optional[str] = None,
    resource: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Sets up a watch for changes to calendar list entries.

    Args:
        maxResults (Optional[int]): Maximum number of calendar list entries to return.
            Must be between 1 and 250. Defaults to 100.
        minAccessRole (Optional[str]): The minimum access role required to view the
            calendar list entries. Must be one of: "freeBusyReader", "owner", "reader", "writer".
        pageToken (Optional[str]): Token specifying which result page to return.
        showDeleted (Optional[bool]): Whether to include deleted calendar list entries
            in the result. Defaults to False.
        showHidden (Optional[bool]): Whether to show hidden entries. Defaults to False.
        syncToken (Optional[str]): Token obtained from the nextSyncToken field returned
            on the last page of results from the previous list request. Cannot be used
            together with minAccessRole.
        resource (Optional[Dict[str, Any]]): Watch configuration:
            - id (str): Channel ID. If not provided, one will be generated.
            - type (str): Type of watch. Defaults to "web_hook".

    Returns:
        Dict[str, Any]: A dictionary containing the watch channel details.
            - id (str): The ID of the watch channel.
            - type (str): The type of watch to use.
            - resource (str): The resource to watch.
            - calendarId (str): The ID of the calendar list entry.
            - primary (bool): Whether the calendar list entry is the primary calendar.
    Raises:
        TypeError: If any parameter has an incorrect type.
        ValueError: If the resource is not provided, if parameter values are invalid,
                   or if syncToken is used together with minAccessRole.
    """
    # Input validation
    if not isinstance(maxResults, int):
        raise TypeError("maxResults must be an integer")
    if minAccessRole is not None and not isinstance(minAccessRole, str):
        raise TypeError("minAccessRole must be a string")
    if pageToken is not None and not isinstance(pageToken, str):
        raise TypeError("pageToken must be a string")
    if not isinstance(showDeleted, bool):
        raise TypeError("showDeleted must be a boolean")
    if not isinstance(showHidden, bool):
        raise TypeError("showHidden must be a boolean")
    if syncToken is not None and not isinstance(syncToken, str):
        raise TypeError("syncToken must be a string")
    if resource is not None and not isinstance(resource, dict):
        raise TypeError("resource must be a dictionary")
    
    # Value validation
    if maxResults < 1 or maxResults > 250:
        raise ValueError("maxResults must be between 1 and 250")
    
    if minAccessRole is not None:
        valid_roles = {"freeBusyReader", "owner", "reader", "writer"}
        if minAccessRole not in valid_roles:
            raise ValueError(f"minAccessRole must be one of: {', '.join(sorted(valid_roles))}")
    
    if resource is None:
        raise ValueError("Channel resource is required.")
    
    # Business rule validation
    if syncToken is not None and minAccessRole is not None:
        raise ValueError("syncToken cannot be used together with minAccessRole")
    
    # Validate resource structure and fields
    if "id" in resource:
        if not isinstance(resource["id"], str):
            raise ValueError("Channel 'id' must be a string")
        if not resource["id"].strip():
            raise ValueError("Channel 'id' cannot be empty")
    
    if "type" in resource:
        if not isinstance(resource["type"], str):
            raise ValueError("Channel 'type' must be a string")
        if not resource["type"].strip():
            raise ValueError("Channel 'type' cannot be empty")
    

    
    # Initialize channels storage if needed
    if "channels" not in DB:
        DB["channels"] = {}
    
    # Generate channel info
    channel_id = resource.get("id") or str(uuid.uuid4())
    channel_info = {
        "id": channel_id,
        "type": resource.get("type", "web_hook"),
        "resource": "calendar_list",
        "calendarId": "primary",  # Default calendar list being watched
    }
    
    # Store channel information
    DB["channels"][channel_id] = channel_info
    return channel_info
