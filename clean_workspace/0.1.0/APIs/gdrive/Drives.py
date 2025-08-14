"""
Drives resource for Google Drive API simulation.

This module provides methods for managing shared drives in the Google Drive API simulation.
"""
import builtins #using this because of the name conflict with the built-in function 'list'    
import base64
import time
import json

import datetime
from typing import Dict, Any, Optional

from pydantic import ValidationError # To catch Pydantic validation errors

from .SimulationEngine.utils import _ensure_user, _parse_query, _apply_query_filter
from .SimulationEngine.counters import _next_counter
from .SimulationEngine.db import DB
from .SimulationEngine.custom_errors import NotFoundError
from .SimulationEngine.models import DriveUpdateBodyModel, CreateDriveBodyInputModel
from .SimulationEngine.custom_errors import NotFoundError
from .SimulationEngine.custom_errors import InvalidQueryError


def create(requestId: Optional[str] = None,
           body: Optional[Dict[str, Any]] = None,
           ) -> Dict[str, Any]:
    """Creates a shared drive. If requestId is provided, it's used as the drive's ID and for idempotency.
    Otherwise, an internal ID is generated.

    Args:
        requestId (Optional[str]): An ID, such as a random UUID. If provided, this ID is used
                                   as the drive's ID. If a drive with this ID already exists,
                                   it is returned. If None or empty, an internal ID is
                                   generated for a new drive.
        body (Optional[Dict[str, Any]]): Dictionary of drive properties. Valid keys:
            - 'name' (Optional[str]): The name of the shared drive.
            - 'restrictions' (Optional[Dict[str, Any]]): A dictionary of restrictions to apply to the drive, with keys:
                - 'adminManagedRestrictions' (bool): Whether administrative privileges on this shared drive are required to modify restrictions.
                - 'copyRequiresWriterPermission' (bool): Whether the options to copy, print, or download files inside this shared drive, should be disabled for readers and commenters.
                - 'domainUsersOnly' (bool): Whether access to this shared drive and items inside this shared drive is restricted to users of the domain to which this shared drive belongs.
                - 'driveMembersOnly' (bool): Whether access to items inside this shared drive is restricted to its members.
            - 'hidden' (Optional[bool]): Whether the shared drive is hidden from default view.
            - 'themeId' (Optional[str]): The ID of the theme to apply to this shared drive.

    Returns:
        Dict[str, Any]:  A dictionary representing the created or existing shared or existing drive, containing the following keys::
            - 'kind' (str): Resource type identifier (e.g., 'drive#drive').
            - 'id' (str): Drive ID (this will be the requestId if provided, otherwise an internally generated ID).
            - 'name' (str): The name of the shared drive.
            - 'restrictions' (Dict[str, Any]): Dictionary of restrictions. Contains keys:
                - 'adminManagedRestrictions' (bool): Whether administrative privileges on this shared drive are required to modify restrictions.
                - 'copyRequiresWriterPermission' (bool): Whether the options to copy, print, or download files inside this shared drive, should be disabled for readers and commenters.
                - 'domainUsersOnly' (bool): Whether access to this shared drive and items inside this shared drive is restricted to users of the domain to which this shared drive belongs.
                - 'driveMembersOnly' (bool): Whether access to items inside this shared drive is restricted to its members.
            - 'hidden' (bool): Whether the shared drive is hidden from default view.
            - 'themeId' (str): The ID of the theme applied to this shared drive.
            - 'createdTime' (str): The time at which the shared drive was created.

    Raises:
        TypeError: If 'requestId' is provided and is not a string.
        ValidationError: If 'body' is provided and does not conform to the expected structure.
        """
    # --- Input Validation Start ---
    if requestId is not None and not isinstance(requestId, str):
        raise TypeError("requestId must be a string if provided.")

    if body is not None and not isinstance(body, dict):
        raise TypeError("body must be a dictionary.")
    
    # Pydantic validation for the 'body' dictionary argument
    validated_body_model: Optional[CreateDriveBodyInputModel] = None
    if body is not None:
        try:
            validated_body_model = CreateDriveBodyInputModel(**body)
        except ValidationError as e:
            # Just re-raise the original error
            raise
    # --- Input Validation End ---

    userId = 'me'
    _ensure_user(userId)

    actual_drive_id: str
    drive_name_default_suffix: str

    if requestId:  # If requestId is provided (not None and not empty string)
        # Check for idempotency: if a drive with this ID (requestId) already exists, return it.
        if requestId in DB['users'][userId]['drives']:
            return DB['users'][userId]['drives'][requestId]

        actual_drive_id = requestId
        drive_name_default_suffix = requestId
    else:  # requestId is None or empty
        drive_id_num = _next_counter('drive')  # Assume this function exists
        actual_drive_id = f"drive_{drive_id_num}"
        drive_name_default_suffix = str(drive_id_num)

    if body is None:
        body = {}

    # Determine the name for the new drive
    # Default name is based on the drive ID suffix
    now = datetime.datetime.now(datetime.UTC).isoformat() + 'Z'
    # Create base drive structure
    new_drive = {
        'kind': 'drive#drive',
        'id': actual_drive_id, 
        'name': body.get('name', f'Drive_{drive_name_default_suffix}'),
        'hidden': body.get('hidden', False),
        'themeId': body.get('themeId', None),
        'restrictions': body.get('restrictions', {}),
        'createdTime': now,
    }

    # Store in DB and return
    if 'drives' not in DB['users'][userId]:
        DB['users'][userId]['drives'] = {}
    DB['users'][userId]['drives'][actual_drive_id] = new_drive
    return new_drive

def delete(driveId: str) -> None:
    """Permanently deletes a shared drive for which the user is an organizer.
    
    This function permanently removes a shared drive from the user's account. The drive
    must be identified by its unique `driveId`. For the operation to succeed, the user
    must have the appropriate permissions (e.g., be an organizer) for the specified drive.
    Once deleted, the drive and all of its contents are irretrievably lost.

    Args:
        driveId (str): The unique identifier of the shared drive to be deleted.

    Returns:
        None

    Raises:
        TypeError: If driveId is not a string.
        NotFoundError: If no drive with the specified `driveId` is found.
    """
    userId = 'me'
    _ensure_user(userId)

    # Input validation
    if not isinstance(driveId, str) or not driveId.strip():
        raise TypeError("driveId must be a non-empty string.")
    
    if driveId not in DB.get('users', {}).get(userId, {}).get('drives', {}):
        raise NotFoundError(f"Drive with ID '{driveId}' not found.")

    DB['users'][userId]['drives'].pop(driveId, None)

    return None

def get(driveId: str) -> Optional[Dict[str, Any]]:
    """Gets a shared drive's metadata by ID.
    
    Args:
        driveId (str): The ID of the shared drive.
        
    Returns:
        Optional[Dict[str, Any]]: Dictionary containing the drive metadata with keys:
            - 'kind' (str): Resource type identifier (e.g., 'drive#drive').
            - 'id' (str): Drive ID.
            - 'name' (str): The name of the shared drive.
            - 'restrictions' (Dict[str, Any]): Dictionary of restrictions with keys:
                - 'adminManagedRestrictions' (bool): Whether administrative privileges on this shared drive are required to modify restrictions.
                - 'copyRequiresWriterPermission' (bool): Whether the options to copy, print, or download files inside this shared drive, should be disabled for readers and commenters.
                - 'domainUsersOnly' (bool): Whether access to this shared drive and items inside this shared drive is restricted to users of the domain to which this shared drive belongs.
                - 'driveMembersOnly' (bool): Whether access to items inside this shared drive is restricted to its members.
            - 'hidden' (bool): Whether the shared drive is hidden from default view.
            - 'themeId' (str): The ID of the theme applied to this shared drive.
            - 'createdTime' (str): The time at which the shared drive was created.
        Returns None if the drive with the specified ID is not found.

    Raises:
        TypeError: If driveId is not a string or is empty.
    """
    # --- Input Validation Start ---
    if not isinstance(driveId, str):
        raise TypeError("driveId must be a string.")
    
    if not driveId.strip():
        raise TypeError("driveId must be a non-empty string.")
    # --- Input Validation End ---
    
    userId = 'me'  # Assuming 'me' for now
    _ensure_user(userId)
    return DB['users'][userId]['drives'].get(driveId)

def hide(driveId: str,
        ) -> Optional[Dict[str, Any]]:
    """Hides a shared drive from the default view.
    
    Args:
        driveId (str): The ID of the shared drive to hide. Must be a non-empty string.
        
    Returns:
        Optional[Dict[str, Any]]: The hidden drive resource object if successful, or None if the drive doesn't exist.
            If successful, the dictionary contains:
            - 'kind' (str): Resource type identifier ('drive#drive').
            - 'id' (str): Drive ID.
            - 'name' (str): The name of the shared drive.
            - 'restrictions' (Dict[str, Any]): Dictionary of restrictions (if present).
            - 'hidden' (bool): Always True after successful hide operation.
            - 'themeId' (str): The ID of the theme applied to this shared drive (if present).
            - 'createdTime' (str): The time at which the shared drive was created (if present).
            
    Raises:
        ValueError: If driveId is None, empty, or not a string.
    """
    # Input validation
    if not isinstance(driveId, str):
        raise ValueError("driveId must be a string")
    if not driveId or not driveId.strip():
        raise ValueError("driveId cannot be empty or whitespace")

    # Normalize driveId by stripping whitespace
    driveId = driveId.strip()

    userId = 'me'  # Assuming 'me' for now
    _ensure_user(userId)

    # Retrieve the drive from the database
    drive = DB['users'][userId]['drives'].get(driveId)

    if drive is None:
        # Drive doesn't exist - return None
        return None

    # Set the hidden flag
    drive['hidden'] = True

    return drive

def list(pageSize: int = 10, q: str = '', pageToken: str = '') -> Dict[str, Any]:
    """Lists the user's shared drives.

    This function returns a list of shared drives that the user is a member of.
    It supports filtering by drive properties through the `q` parameter
    and allows for pagination using `pageSize` and `pageToken`.

    Args:
        pageSize (int): Maximum number of shared drives to return per page.
                        Must be an integer between 1 and 100.
        q (str): Query string for searching shared drives. 
                 The query supports the following fields and operators:
                     - Fields: 'name', 'id', 'createdTime', 'hidden', 'themeId'
                     - Operators: =, !=, <, <=, >, >=, contains, in
                 You can combine conditions with 'and' and 'or'.
                 String values must be quoted. Example queries:
                     "name = 'My Drive'"
                     "name contains 'Project' and hidden = false"
                     "createdTime >= '2023-01-01T00:00:00Z'"
                     "name = 'Team Drive' or themeId = 'blue-theme'"
        pageToken (str): (Optional) A base64-encoded token for pagination. The token encodes a JSON object with:
            - 'last_row_time' (str): The unix timestamp (as a string) when the last page was generated.
            - 'offset' (int): The offset (index) to start the next page from.

    Returns:
        Dict[str, Any]: Dictionary containing the list of shared drives with keys:
            - 'kind' (str): Resource type identifier (e.g., 'drive#driveList').
            - 'nextPageToken' (str): Page token for the next page of results.
            Dict[str, Any]:  A dictionary representing the created or existing shared or existing drive, containing the following keys::
                - 'kind' (str): Resource type identifier (e.g., 'drive#drive').
                - 'id' (str): Drive ID (this will be the requestId if provided, otherwise an internally generated ID).
                - 'name' (str): The name of the shared drive.
                - 'restrictions' (Dict[str, Any]): Dictionary of restrictions. Contains keys:
                    - 'adminManagedRestrictions' (bool): Whether administrative privileges on this shared drive are required to modify restrictions.
                    - 'copyRequiresWriterPermission' (bool): Whether the options to copy, print, or download files inside this shared drive, should be disabled for readers and commenters.
                    - 'domainUsersOnly' (bool): Whether access to this shared drive and items inside this shared drive is restricted to users of the domain to which this shared drive belongs.
                    - 'driveMembersOnly' (bool): Whether access to items inside this shared drive is restricted to its members.
                - 'hidden' (bool): Whether the shared drive is hidden from default view.
                - 'themeId' (str): The ID of the theme applied to this shared drive.
                - 'createdTime' (str): The time at which the shared drive was created.
            - 'drives' (List[Dict[str, Any]]): List of shared drive objects.
    
    Raises:
        TypeError: If `pageSize` is not an integer or `q` is not a string.
        ValueError: If `pageSize` is negative or greater than 100.
        InvalidQueryError: If `q` is provided and is not a valid query string.
    """
    userId = 'me'
    _ensure_user(userId)

    # --- Input Validation ---
    if not isinstance(pageSize, int):
        raise TypeError("pageSize must be an integer.")
    
    if pageSize <= 0 or pageSize > 100:
        raise ValueError("pageSize must be an integer between 1 and 100.")

    if not isinstance(q, str):
        raise TypeError("q must be a string.")
    if not isinstance(pageToken, str):
        raise TypeError("pageToken must be a string.")
    # --- End of Input Validation ---

    # Get all drives for the user
    drives_list = builtins.list(DB['users'][userId]['drives'].values())

    # Apply query filtering if q is provided
    if q:
        try:
            conditions = _parse_query(q)  # This returns a list of condition groups
            drives_list = _apply_query_filter(drives_list, conditions, resource_type='drive')
        except Exception as e:
            raise InvalidQueryError(f"Invalid query string: '{q}' with error: {e}")

    # Pagination logic
    offset = 0
    if pageToken:
        try:
            decoded = base64.urlsafe_b64decode(pageToken.encode('utf-8')).decode('utf-8')
            token_data = json.loads(decoded)
            offset = int(token_data.get('offset', 0))
        except Exception:
            offset = 0  # fallback to 0 if token is invalid

    paged_drives = drives_list[offset:offset + pageSize]
    next_offset = offset + pageSize

    if next_offset < len(drives_list):
        next_token_data = {
            "last_row_time": str(int(time.time())),
            "offset": next_offset
        }
        nextPageToken = base64.urlsafe_b64encode(json.dumps(next_token_data).encode('utf-8')).decode('utf-8')
    else:
        nextPageToken = None

    return {
        'kind': 'drive#driveList',
        'nextPageToken': nextPageToken,
        'drives': paged_drives
    }

def unhide(driveId: str,
          ) -> Optional[Dict[str, Any]]:
    """Restores a shared drive to the default view.
    
    Args:
        driveId (str): The ID of the shared drive.
        
    Returns:
        Optional[Dict[str, Any]]: Dictionary containing the unhidden drive with keys:
            - 'kind' (str): Resource type identifier (e.g., 'drive#drive').
            - 'id' (str): Drive ID.
            - 'name' (str): The name of the shared drive.
            - 'restrictions' (Dict[str, Any]): Dictionary of restrictions with keys:
                - 'adminManagedRestrictions' (bool): Whether administrative privileges on this shared drive are required to modify restrictions.
                - 'copyRequiresWriterPermission' (bool): Whether the options to copy, print, or download files inside this shared drive, should be disabled for readers and commenters.
                - 'domainUsersOnly' (bool): Whether access to this shared drive and items inside this shared drive is restricted to users of the domain to which this shared drive belongs.
                - 'driveMembersOnly' (bool): Whether access to items inside this shared drive is restricted to its members.
            - 'hidden' (bool): Whether the shared drive is hidden from default view.
            - 'themeId' (str): The ID of the theme applied to this shared drive.
            - 'createdTime' (str): The time at which the shared drive was created.
        Returns None if the drive with the specified ID is not found.

    Raises:
        TypeError: If driveId is not a string or is empty.
    """
    # --- Input Validation Start ---
    if not isinstance(driveId, str):
        raise TypeError("driveId must be a string.")
    
    if not driveId.strip():
        raise TypeError("driveId must be a non-empty string.")
    # --- Input Validation End ---
    
    userId = 'me'  # Assuming 'me' for now
    _ensure_user(userId)
    drive = DB['users'][userId]['drives'].get(driveId)
    if drive and drive.get('hidden'):
        drive['hidden'] = False
    return drive

def update(driveId: str,
          body: Optional[Dict[str, Any]] = None,
          ) -> Dict[str, Any]:
    """Updates the metadata for a shared drive.

    This function modifies an existing shared drive's metadata based on the
    provided `body`. The drive is identified by its `driveId`.
    
    Args:
        driveId (str): The ID of the shared drive.
        body (Optional[Dict[str, Any]]): Dictionary of drive properties to update with keys:
            - 'name' (Optional[str]): The name of the shared drive.
            - 'restrictions' (Optional[Dict[str, Any]]): Dictionary of restrictions with keys:
                - 'adminManagedRestrictions' (Optional[bool]): Whether administrative privileges on this shared drive are required to modify restrictions.
                - 'copyRequiresWriterPermission' (Optional[bool]): Whether the options to copy, print, or download files inside this shared drive, should be disabled for readers and commenters.
                - 'domainUsersOnly' (Optional[bool]): Whether access to this shared drive and items inside this shared drive is restricted to users of the domain to which this shared drive belongs.
                - 'driveMembersOnly' (Optional[bool]): Whether access to items inside this shared drive is restricted to its members.
            - 'hidden' (Optional[bool]): Whether the shared drive is hidden from default view.
            - 'themeId' (Optional[str]): The ID of the theme to apply to this shared drive.

    Returns:
        Dict[str, Any]: Dictionary containing the updated drive with keys:
            - 'kind' (str): Resource type identifier (e.g., 'drive#drive').
            - 'id' (str): Drive ID.
            - 'name' (str): The name of the shared drive.
            - 'restrictions' (Dict[str, Any]): Dictionary of restrictions with keys:
                - 'adminManagedRestrictions' (bool): Whether administrative privileges on this shared drive are required to modify restrictions.
                - 'copyRequiresWriterPermission' (bool): Whether the options to copy, print, or download files inside this shared drive, should be disabled for readers and commenters.
                - 'domainUsersOnly' (bool): Whether access to this shared drive and items inside this shared drive is restricted to users of the domain to which this shared drive belongs.
                - 'driveMembersOnly' (bool): Whether access to items inside this shared drive is restricted to its members.
            - 'hidden' (bool): Whether the shared drive is hidden from default view.
            - 'themeId' (str): The ID of the theme applied to this shared drive.
            - 'createdTime' (str): The time at which the shared drive was created.

    Raises:
        TypeError: If 'driveId' is not a non-empty string or 'body' is not a dictionary.
        ValidationError: If 'body' is provided and does not conform to the DriveUpdateBodyModel structure
                                  (e.g., incorrect types for fields, disallowed extra fields).
        NotFoundError: If no drive with the specified `driveId` is found.

    """
    # --- Input Validation Start ---
    userId = 'me'  # Define userId for DB access
    _ensure_user(userId)  # Ensure user exists

    # Standard type validation for non-dictionary arguments
    if not isinstance(driveId, str) or not driveId.strip():
        raise TypeError(f"driveId must be a non-empty string")

    # Pydantic validation for the 'body' dictionary argument
    validated_body = {}
    if body is not None:
        if not isinstance(body, dict):
            raise TypeError(f"body must be a dictionary or None, but got {type(body).__name__}")
        
        try:
            # Validate the structure of the 'body' dictionary using Pydantic
            # The model will handle checking for extra fields since it has model_config = {"extra": "forbid"}
            parsed_body_model = DriveUpdateBodyModel(**body)
            # Get a dictionary of fields that were actually provided in the input,
            # excluding those not set. This is suitable for PATCH-like updates.
            validated_body = parsed_body_model.model_dump(exclude_unset=True)
        except ValidationError as e:
            # Simply pass the Pydantic validation error through our custom ValidationError
            raise e
    
    # --- Input Validation End ---

    existing = DB['users'][userId]['drives'].get(driveId)
    if not existing:
        raise NotFoundError(f"Drive with ID '{driveId}' not found.")

    # Use the validated_body_data for the update operation
    existing.update(validated_body)

    return existing