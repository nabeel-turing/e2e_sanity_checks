"""
Spaces API for Google Meet API simulation.
"""

from typing import Dict, Any, Optional

from pydantic import ValidationError
from .SimulationEngine.custom_errors import InvalidSpaceNameError, SpaceNotFoundError
from .SimulationEngine.models import SpaceContentModel
from google_meet.SimulationEngine.models import SpaceUpdateMaskModel
from google_meet.SimulationEngine.db import DB


def patch(name: str, update_mask: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Updates details about a meeting space.

    Modifies the specified fields of an existing meeting space. Only fields
    that are included in the update_mask will be changed.

    Args:
        name (str): The name of the space to update.
        update_mask (Optional[Dict[str, Any]]): Dictionary containing fields to update
            and their new values. Can include keys:
            - 'accessType' (str): The access level for the space (e.g., "TRUSTED", "RESTRICTED", "OPEN").
            - 'entryPointAccess' (str): Control who can access entry points (e.g., "ALL", "CREATOR_APP_ONLY").
            - 'meetingCode' (str): Code used to join the meeting.
            - 'meetingUri' (str): URI that can be used to join the meeting.
            - 'activeConference' (Optional[Dict[str, Any]]): Optional information about an active conference with keys:
                - 'conferenceId' (str): The unique identifier for the conference.
                - 'details' (Optional[str]): Additional details about the conference.

    Returns:
        Dict[str, Any]: A dictionary containing updated space information with keys:
            - 'id' (str): The space identifier.
            - 'meetingCode' (str): The code used to join the meeting.
            - 'meetingUri' (str): The URI that can be used to join the meeting.
            - 'accessType' (str): The access level for the space (e.g., "TRUSTED", "RESTRICTED", "OPEN").
            - 'entryPointAccess' (str): Who can access the entry points (e.g., "ALL", "CREATOR_APP_ONLY").
            - 'activeConference' (Optional[Dict[str, Any]]): Information about an active conference
              if one exists, including 'conferenceId' and optional 'details'.

    Raises:
        TypeError: If name is not a string.
        InvalidSpaceNameError: If name is empty or contains only whitespace.
        ValidationError: If update_mask contains invalid field types or structures.
        KeyError: If the database is not properly initialized.
        SpaceNotFoundError: If the specified space does not exist.
    """
    # --- Input Validation Start ---
        
    # Validate name parameter
    if not isinstance(name, str):
        raise TypeError("Argument 'name' must be a string.")
    
    if not name.strip():
        raise InvalidSpaceNameError("Space name cannot be empty or whitespace.")

    # Validate update_mask parameter
    if update_mask is not None:
        if not isinstance(update_mask, dict):
            raise TypeError("Argument 'update_mask' must be a dictionary if provided.")
        try:
            # Validate the update_mask using the Pydantic model
            _ = SpaceUpdateMaskModel(**update_mask)
        except ValidationError as e:
            # Re-raise Pydantic's ValidationError to be handled by the caller
            raise e
    
    # Check if space exists
    if name not in DB["spaces"]:
        raise SpaceNotFoundError(f"Space '{name}' not found")
    # --- Input Validation End ---

    # --- Core Logic ---
    space = DB["spaces"][name].copy()
    if update_mask:
        for field, value in update_mask.items():
            space[field] = value

    DB["spaces"][name] = space
    return space


def get(name: str) -> Dict[str, Any]:
    """
    Gets details about a meeting space.

    Retrieves comprehensive information about a specific meeting space.

    Args:
        name (str): The name of the space to retrieve.

    Returns:
        Dict[str, Any]: A dictionary containing the space details with keys:
            - "id" (str): The space identifier
            - "meetingCode" (str): The code used to join the meeting
            - "meetingUri" (str): The URI that can be used to join the meeting
            - "accessType" (str): The access level for the space (e.g., "TRUSTED", "RESTRICTED", "OPEN")
            - "entryPointAccess" (str): Who can access the entry points (e.g., "ALL", "CREATOR_APP_ONLY")
            - "activeConference" (Optional[Dict[str, Any]]): Information about an active conference
              in this space, if one exists, which may include:
                - "conferenceId" (str): The unique identifier for the conference
                - "details" (Optional[str]): Additional details about the conference

    Raises:
        TypeError: If 'name' is not a string.
        ValueError: If the space name is empty.
        KeyError: If the space with the given name is not found in the database.
    """
    # Input validation for non-dictionary arguments
    if not isinstance(name, str):
        raise TypeError("Argument 'name' must be a string.")
    
    if not name.strip():
        raise ValueError("Space name cannot be empty.")

    # Original function logic (remains unchanged)
    # DB is assumed to be an accessible global or context variable.
    if name in DB["spaces"]: # type: ignore
        return DB["spaces"][name] # type: ignore
    else:
        raise KeyError(f"Space with name '{name}' not found.")


def create(space_name: str, space_content: Dict[str, Any]) -> Dict[str, Any]:
    """
    Creates a new meeting space.

    This function adds a new meeting space to the database with the specified
    name and content details.

    Args:
        space_name (str): The name of the new space. Must be a non-empty string.
        space_content (Dict[str, Any]): A dictionary containing the details of the new space.
            - "meetingCode" (str): A unique code for joining the meeting
            - "meetingUri" (str): A URI that can be used to join the meeting
            - "accessType" (str): The access level for the space

    Returns:
        Dict[str, Any]: A dictionary containing the operation result.
            - "message" (str): Success message in the format "Space {space_name} created successfully"

    Raises:
        TypeError: If `space_name` is not a string, or if `space_content` is not a dictionary.
        InvalidSpaceNameError: If `space_name` is an empty string.
        ValidationError: If `space_content` does not conform to the expected structure
                                  (defined by SpaceContentModel).
    """
    # --- Input Validation Start ---

    # Validate space_name
    if not isinstance(space_name, str):
        raise TypeError("space_name must be a string.")
    if not space_name.strip(): # Check if space_name is empty or only whitespace
        raise InvalidSpaceNameError("space_name cannot be empty or whitespace.")

    # Validate space_content type
    if not isinstance(space_content, dict):
        raise TypeError("space_content must be a dictionary.")

    # Validate space_content structure using Pydantic
    try:
        validated_space_content = SpaceContentModel(**space_content)
    except ValidationError as e:
        # Re-raise Pydantic's ValidationError, which contains detailed error messages.
        # You could also wrap it in a custom error if needed, e.g.:
        # raise InvalidSpaceContentError(f"Invalid space_content: {e}") from e
        raise e

    # --- Input Validation End ---


    DB["spaces"][space_name] = validated_space_content.model_dump()

    return {"message": f"Space {space_name} created successfully"}


def endActiveConference(name: str) -> Dict[str, Any]:
    """
    Ends an active conference in a meeting space, if one exists.

    This function removes the activeConference field from the specified space,
    effectively marking any active conference as ended. This operation is
    irreversible and will permanently remove the active conference data from
    the space.

    Args:
        name (str): The name of the space to end the active conference in.

    Returns:
        Dict[str, Any]: A dictionary with a single key "message" containing:
        - "Active conference ended" if an active conference was successfully ended
        - "No active conference to end" if no active conference existed to end

    Raises:
        TypeError: If 'name' is not a string.
        SpaceNotFoundError: If the space with the specified name is not found.
    """
    # Input validation
    if not isinstance(name, str):
        raise TypeError("Argument 'name' must be a string.")

    # Original function logic
    if name not in DB["spaces"]:
        raise SpaceNotFoundError(f"Space '{name}' not found")

    space = DB["spaces"][name]
    if "activeConference" in space:
        del space["activeConference"]
        DB["spaces"][name] = space # In a real DB, this would be an update operation
        return {"message": "Active conference ended"}
    else:
        return {"message": "No active conference to end"}
