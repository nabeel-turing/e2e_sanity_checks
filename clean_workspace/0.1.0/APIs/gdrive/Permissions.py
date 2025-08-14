"""
Permissions resource for Google Drive API simulation.

This module provides methods for managing permissions in the Google Drive API simulation.
"""

from typing import Dict, Any, Optional, Union, Tuple

from pydantic import ValidationError

from .SimulationEngine.utils import _ensure_user, _ensure_file
from .SimulationEngine.counters import _next_counter
from .SimulationEngine.db import DB

from .SimulationEngine.custom_errors import ResourceNotFoundError, PermissionDeniedError, LastOwnerDeletionError, NotFoundError
from .SimulationEngine.models import PermissionBodyUpdateModel, PermissionBodyModel, PermissionListModel


def create(fileId: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Creates a permission for a file or shared drive.

    Args:
        fileId (str): The ID of the file or shared drive.
        body (Optional[Dict[str, Any]]): Dictionary of permission properties with keys:
            - 'role' (str): The role granted by this permission, defaults to 'reader' (alias for 'viewer'). Possible values:
                - 'viewer': Can view the file
                - 'commenter': Can view and comment on the file
                - 'editor': Can view, comment, and edit the file
                - 'owner': Has full control over the file
            - 'type' (str): The type of the grantee, defaults to 'user'. Possible values:
                - 'user': Permission granted to a specific user
                - 'group': Permission granted to a group
                - 'domain': Permission granted to a domain
                - 'anyone': Permission granted to anyone with the link
            - 'emailAddress' (str): The email address of the user or group to grant the permission to. This will be normalized to lowercase.
            - 'domain' (str): The domain name (e.g. 'example.com') of the entity this permission refers to.
            - 'allowFileDiscovery' (bool): Whether the permission allows the file to be discovered through search, defaults to False.
            - 'expirationTime' (str): The time at which this permission will expire, in RFC 3339 format. Example: `'2025-06-30T12:00:00Z'` (UTC) or `'2025-06-30T08:00:00-04:00'`.

    Returns:
        Dict[str, Any]: Dictionary containing the created permission with keys:
            - 'kind' (str): Resource type identifier (e.g., 'drive#permission').
            - 'id' (str): Permission ID.
            - 'role' (str): The role granted by this permission.
            - 'type' (str): The type of the grantee.
            - 'emailAddress' (str): The email address of the user or group.
            - 'domain' (str): The domain name of the entity this permission refers to.
            - 'allowFileDiscovery' (bool): Whether the permission allows the file to be discovered through search.
            - 'expirationTime' (str): The time at which this permission will expire, in RFC 3339 format.

    Raises:
        TypeError: If `fileId` is not a string.
        ValueError: If `fileId` is an empty string.
        ResourceNotFoundError: If `fileId` is not found in user's files or shared drives.
        ValidationError: If `body` is provided and does not conform to the
            required structure (e.g., invalid 'role' or 'type' values,
            incorrect data type for 'allowFileDiscovery').
    """
    # --- Start of Added Validation Logic ---
    # Validate 'fileId'
    if not isinstance(fileId, str):
        raise TypeError("fileId must be a string.")
    if not fileId.strip():  # Ensure fileId is not empty or just whitespace
        raise ValueError("fileId cannot be an empty string.")

    # Validate 'body' using Pydantic model if it's provided
    if body is not None:
        try:
            PermissionBodyModel(**body)
        except ValidationError as e:
            raise e
    # --- End of Added Validation Logic ---

    userId = 'me'  # Assuming 'me' for now
    _ensure_user(userId)

    target_container = None
    if fileId in DB['users'][userId]['files']:
        target_container = DB['users'][userId]['files']
    elif fileId in DB['users'][userId]['drives']:
        target_container = DB['users'][userId]['drives']
    else:
        raise ResourceNotFoundError(f"Resource with ID '{fileId}' not found.")

    _processed_body = body if body is not None else {}

    permission_id_num = _next_counter('permission')
    permission_id = f"permission_{permission_id_num}"

    new_permission = {
        'kind': 'drive#permission',
        'id': permission_id,
        'role': _processed_body.get('role', 'reader'),
        'type': _processed_body.get('type', 'user'),
        'emailAddress': _processed_body.get('emailAddress', ''),
        'domain': _processed_body.get('domain', ''),
        'allowFileDiscovery': _processed_body.get('allowFileDiscovery', False),
        'expirationTime': _processed_body.get('expirationTime', '')
    }

    # Save the permission
    if 'permissions' not in target_container[fileId]:
        target_container[fileId]['permissions'] = []
    target_container[fileId]['permissions'].append(new_permission)

    return new_permission

def delete(fileId: str,
          permissionId: str,
          supportsAllDrives: Optional[bool] = False,
          supportsTeamDrives: Optional[bool] = False,
          useDomainAdminAccess: Optional[bool] = False) -> None:
    """Deletes a permission.

    Args:
        fileId (str): The ID of the file or shared drive.
        permissionId (str): The ID of the permission to delete.
        supportsAllDrives (Optional[bool]): Whether to support all drives. Defaults to False.
        supportsTeamDrives (Optional[bool]): Whether to support team drives. Defaults to False.
        useDomainAdminAccess (Optional[bool]): Whether to use domain admin access. Defaults to False.

    Returns:
        None: The function returns None on successful deletion.
    
    Raises:
        TypeError: If `fileId` or `permissionId` is not a string, or if any of
                   the boolean flags are not booleans.
        ValueError: If `fileId` or `permissionId` is an empty or whitespace-only string.
        ResourceNotFoundError: If the specified `fileId` or `permissionId` cannot be found.
        PermissionDeniedError: If the user lacks sufficient permissions. For shared drive
                               items, 'organizer' role is required. For other items,
                               'owner' or 'editor' (writer) is required, though editors
                               cannot remove owners.
        LastOwnerDeletionError: If an attempt is made to delete the permission of the
                                last owner of a file.        
    """
    # --- Input Validation ---
    if not isinstance(fileId, str):
        raise TypeError("Argument 'fileId' must be a string.")
    if not fileId.strip():
        raise ValueError("Argument 'fileId' cannot be an empty string.")
    if not isinstance(permissionId, str):
        raise TypeError("Argument 'permissionId' must be a string.")
    if not permissionId.strip():
        raise ValueError("Argument 'permissionId' cannot be an empty string.")
    if not isinstance(supportsAllDrives, bool):
        raise TypeError("Argument 'supportsAllDrives' must be a boolean.")
    if not isinstance(supportsTeamDrives, bool):
        raise TypeError("Argument 'supportsTeamDrives' must be a boolean.")
    if not isinstance(useDomainAdminAccess, bool):
        raise TypeError("Argument 'useDomainAdminAccess' must be a boolean.")

    # --- Core Logic ---
    userId = 'me'
    _ensure_user(userId)
    user_email = DB['users'][userId]['about']['user']['emailAddress']

    # Locate the target file or drive
    target_resource = None
    is_in_shared_drive = False
    if (supportsAllDrives or supportsTeamDrives) and fileId in DB['users'][userId].get('drives', {}):
        target_resource = DB['users'][userId]['drives'][fileId]
        is_in_shared_drive = True
    elif fileId in DB['users'][userId]['files']:
        target_resource = DB['users'][userId]['files'][fileId]
        # Check if the file is in a shared drive via its properties
        if target_resource.get('driveId'):
            is_in_shared_drive = True
    else:
        raise ResourceNotFoundError(f"File or drive with ID '{fileId}' not found.")

    # Find the permission to delete
    permissions = target_resource.get('permissions', [])
    permission_to_delete = None
    permission_index = -1
    for i, p in enumerate(permissions):
        if p.get('id') == permissionId:
            permission_to_delete = p
            permission_index = i
            break

    if not permission_to_delete:
        raise ResourceNotFoundError(f"Permission with ID '{permissionId}' not found on file '{fileId}'.")

    # --- Authorization and Business Rule Checks ---

    # 1. Check if the user has the authority to delete the permission
    can_delete = False
    
    is_owner = any(
        (owner.get('emailAddress') if isinstance(owner, dict) else owner) == user_email
        for owner in target_resource.get('owners', [])
    )
    
    user_permission = next((p for p in permissions if p.get('emailAddress') == user_email), None)
    user_role = user_permission.get('role') if user_permission else None


    if useDomainAdminAccess:
        can_delete = True
    elif is_in_shared_drive:
        # In a shared drive, only an organizer can manage permissions
        if user_role == 'organizer':
            can_delete = True
    else:
        # In "My Drive", owners can delete anyone. Editors can delete non-owners.
        if is_owner:
            can_delete = True
        elif user_role in ['editor', 'writer'] and permission_to_delete.get('role') != 'owner':
            can_delete = True
            
    if not can_delete:
        raise PermissionDeniedError(f"User '{user_email}' does not have sufficient permissions to modify permissions on file '{fileId}'.")

    # 2. Prevent deletion of the last owner (this check is always important)
    if permission_to_delete.get('role') == 'owner':
        owner_permissions = [p for p in permissions if p.get('role') == 'owner']
        if len(owner_permissions) == 1:
            raise LastOwnerDeletionError(
                "Cannot remove the last owner of a file. Transfer ownership first."
            )

    # --- Perform Deletion ---
    del target_resource['permissions'][permission_index]

    return None

def get(fileId: str,
       permissionId: str,
       supportsAllDrives: bool = False,
       supportsTeamDrives: bool = False,
       useDomainAdminAccess: bool = False,
       ) -> Optional[Dict[str, Any]]:
    """Gets a permission by ID.
    
    Retrieves a specific permission by its ID for the specified file. The function
    supports various access patterns including shared drives and domain admin access.
    
    Args:
        fileId (str): The ID of the file or shared drive. Must be a non-empty string.
        permissionId (str): The ID of the permission to retrieve. Must be a non-empty string.
        supportsAllDrives (bool): Whether the requesting application supports both My Drives 
            and shared drives. Defaults to False.
        supportsTeamDrives (bool): Whether to support team drives. Deprecated - use 
            supportsAllDrives instead. Defaults to False.
        useDomainAdminAccess (bool): Issue the request as a domain administrator. If set to 
            true, grants access if the file ID refers to a shared drive and the requester 
            is an administrator of the domain to which the shared drive belongs. Defaults to False.
        
    Returns:
        Optional[Dict[str, Any]]: Dictionary containing the permission with keys:
            - 'kind' (str): Resource type identifier (e.g., 'drive#permission').
            - 'id' (str): Permission ID.
            - 'role' (str): The role granted by this permission.
            - 'type' (str): The type of the grantee.
            - 'emailAddress' (str): The email address of the user or group.
            - 'domain' (str): The domain name of the entity this permission refers to.
            - 'allowFileDiscovery' (bool): Whether the permission allows the file to be discovered through search.
            - 'expirationTime' (str): The time at which this permission will expire.
            
    Raises:
        TypeError: If any parameter is not of the expected type.
        ValueError: If fileId or permissionId is empty or invalid.
    """
    # --- Input Validation ---
    if not isinstance(fileId, str):
        raise TypeError("fileId must be a string.")
    if not isinstance(permissionId, str):
        raise TypeError("permissionId must be a string.")
    if not isinstance(supportsAllDrives, bool):
        raise TypeError("supportsAllDrives must be a boolean.")
    if not isinstance(supportsTeamDrives, bool):
        raise TypeError("supportsTeamDrives must be a boolean.")
    if not isinstance(useDomainAdminAccess, bool):
        raise TypeError("useDomainAdminAccess must be a boolean.")
        
    if not fileId.strip():
        raise ValueError("fileId cannot be empty or whitespace.")
    if not permissionId.strip():
        raise ValueError("permissionId cannot be empty or whitespace.")
    
    userId = 'me'  # Assuming 'me' for now
    _ensure_user(userId)
    
    # Ensure the file exists
    _ensure_file(userId, fileId)
    
    # Get the file entry
    file_entry = DB['users'][userId]['files'][fileId]
    
    # Search for the permission in the current user's file permissions
    for permission in file_entry.get('permissions', []):
        if permission['id'] == permissionId:
            return permission
    
    # If supportsAllDrives or supportsTeamDrives is True, search across shared drives
    if supportsAllDrives or supportsTeamDrives:
        # Search in current user's shared drives
        if 'drives' in DB['users'][userId]:
            for drive_id, drive_data in DB['users'][userId]['drives'].items():
                if fileId in drive_data.get('files', {}):
                    for permission in drive_data['files'][fileId].get('permissions', []):
                        if permission['id'] == permissionId:
                            return permission
        
        # If domain admin access is enabled, search across all users
        if useDomainAdminAccess:
            for user_id, user_data in DB['users'].items():
                if user_id != userId:  # Skip current user (already searched above)
                    # Search in other users' regular files
                    if fileId in user_data.get('files', {}):
                        for permission in user_data['files'][fileId].get('permissions', []):
                            if permission['id'] == permissionId:
                                return permission
                    
                    # Search in other users' shared drives
                    if 'drives' in user_data:
                        for drive_id, drive_data in user_data['drives'].items():
                            if fileId in drive_data.get('files', {}):
                                for permission in drive_data['files'][fileId].get('permissions', []):
                                    if permission['id'] == permissionId:
                                        return permission
    
    return None

def list(fileId: str,
        supportsAllDrives: Optional[bool] = False,
        supportsTeamDrives: Optional[bool] = False,
        useDomainAdminAccess: Optional[bool] = False,
        ) -> Dict[str, Any]:
    """Lists a file's or shared drive's permissions.
    
    Args:
        fileId (str): The ID of the file or shared drive.
        supportsAllDrives (Optional[bool]): Whether to support all drives. If True, includes permissions from all drives. Defaults to False.
        supportsTeamDrives (Optional[bool]): Whether to support team drives. If True, includes team drive specific permissions. Defaults to False.
        useDomainAdminAccess (Optional[bool]): Whether to use domain admin access. If True, includes domain-wide permissions. Defaults to False.
        
    Returns:
        Dict[str, Any]: Dictionary containing the list of permissions with keys:
            - 'kind' (str): Resource type identifier (e.g., 'drive#permissionList').
            - 'permissions' (List[PermissionResourceModel]): List of permission objects, each with the following keys:
                - 'kind' (str): Identifies the resource as 'drive#permission'.
                - 'id' (str): The unique ID for this permission.
                - 'role' (str): The role granted by this permission (e.g., 'owner', 'editor', 'reader').
                - 'type' (str): The type of the grantee (e.g., 'user', 'group', 'domain', 'anyone').
                - 'emailAddress' (Optional[str]): The email address of the user or group this permission refers to.
                - 'domain' (Optional[str]): The domain to which this permission applies.
                - 'allowFileDiscovery' (Optional[bool]): Whether this permission allows the file to be discovered through search. Defaults to False.
                - 'expirationTime' (Optional[str]): The RFC 3339 formatted time at which this permission will expire.
                - 'displayName' (Optional[str]): The display name of the user or group.
    Raises:
        TypeError: If any of the input arguments do not match their expected types
                   (e.g., if fileId is not a string, or boolean flags are not booleans).
        NotFoundError: If no file matching `fileId` exists for the current user.
    """

    # --- Input Validation ---
    if not isinstance(fileId, str):
        raise TypeError("fileId must be a string.")
    if not isinstance(supportsAllDrives, bool):
        raise TypeError("supportsAllDrives must be a boolean.")
    if not isinstance(supportsTeamDrives, bool):
        raise TypeError("supportsTeamDrives must be a boolean.")
    if not isinstance(useDomainAdminAccess, bool):
        raise TypeError("useDomainAdminAccess must be a boolean.")
    # --- End of Input Validation ---

    userId = 'me'  # Assuming 'me' for now
    _ensure_user(userId)

    files = DB['users'][userId]['files']
    if fileId not in files:
        raise NotFoundError(f"Given fileId {fileId!r} not found in user {userId!r} files")

    # Get base permissions (make a copy so we don’t mutate the DB)
    permissions = DB['users'][userId]['files'][fileId].get('permissions', [])[:]

    # If supportsAllDrives is True, include permissions from all drives
    if supportsAllDrives:
        all_drives_permissions = []
        for user_id, user_data in DB['users'].items():
            if user_id != userId:  # Skip current user as we already have their permissions
                if fileId in user_data.get('files', {}):
                    all_drives_permissions.extend(user_data['files'][fileId].get('permissions', []))
        permissions.extend(all_drives_permissions)

    # If supportsTeamDrives is True, include team drive specific permissions
    if supportsTeamDrives:
        team_drive_permissions = []
        # look under "drives" (shared/team drives)
        for user_data in DB['users'].values():
            for drive_data in user_data.get('drives', {}).values():
                if fileId in drive_data.get('files', {}):
                    team_drive_permissions.extend(
                        drive_data['files'][fileId].get('permissions', [])
                    )
        permissions.extend(team_drive_permissions)

    # If useDomainAdminAccess is True, include domain-wide permissions
    if useDomainAdminAccess:
        domain_permissions = []
        for user_id, user_data in DB['users'].items():
            if 'domain_permissions' in user_data:
                if fileId in user_data['domain_permissions']:
                    domain_permissions.extend(user_data['domain_permissions'][fileId])
        permissions.extend(domain_permissions)

    return PermissionListModel(**{
        'kind': 'drive#permissionList',
        'permissions': permissions
    }).model_dump()

def update(fileId: str,
          permissionId: str,
          body: Optional[Dict[str, Any]] = None,
          transferOwnership: bool = False
          ) -> Dict[str, Any]:
    """Updates a permission with patch semantics.

    Args:
        fileId (str): The ID of the file or shared drive.
        permissionId (str): The ID of the permission to update.
        body (Optional[Dict[str, Any]]): Dictionary of permission properties to update with keys:
            - 'role' (str): The role granted by this permission. Possible values:
                - 'viewer': Can view the file, (alias for 'reader')
                - 'commenter': Can view and comment on the file
                - 'editor': Can view, comment, and edit the file (alias for 'writer')
                - 'owner': Has full control over the file
            - 'type' (str): The type of the grantee. Possible values:
                - 'user': Permission granted to a specific user
                - 'group': Permission granted to a group
                - 'domain': Permission granted to a domain
                - 'anyone': Permission granted to anyone with the link
            - 'emailAddress' (str): The email address of the user or group.
            - 'domain' (str): The domain name of the entity this permission refers to.
            - 'allowFileDiscovery' (bool): Whether the permission allows the file to be discovered through search.
            - 'expirationTime' (str): The time at which this permission will expire.
        transferOwnership (bool): Whether to transfer ownership to the specified user and downgrade the current owner to a writer.

    Returns:
        Dict[str, Any]: Dictionary containing the updated permission with keys:
            - 'kind' (str): Resource type identifier (e.g., 'drive#permission').
            - 'id' (str): Permission ID.
            - 'role' (str): The role granted by this permission.
            - 'type' (str): The type of the grantee.
            - 'emailAddress' (str): The email address of the user or group.
            - 'domain' (str): The domain name of the entity this permission refers to.
            - 'allowFileDiscovery' (bool): Whether the permission allows the file to be discovered through search.
            - 'expirationTime' (str): The time at which this permission will expire.

    Raises:
        TypeError: If 'fileId' or 'permissionId' are not strings, or
                   if 'transferOwnership' is not a boolean.
        ValidationError: If 'body' is provided and does not conform to the expected structure.
        LookupError: If the specified 'permissionId' is not found (both for standard updates and ownership transfers),
                    or if the file with the given 'fileId' could not be found or created.
        ValueError: If attempting to transfer ownership to a permission lacking an email address, 
                    or if trying to set 'role' to 'owner' without 'transferOwnership=True'.
    """
    # --- Input Validation ---
    if not isinstance(fileId, str):
        raise TypeError("fileId must be a string.")
    if not isinstance(permissionId, str):
        raise TypeError("permissionId must be a string.")
    if not isinstance(transferOwnership, bool):
        raise TypeError("transferOwnership must be a boolean.")

    validated_body_model: Optional[PermissionBodyUpdateModel] = None
    if body is not None:
        try:
            # Pydantic will raise ValidationError if 'body' does not match the model
            validated_body_model = PermissionBodyUpdateModel(**body)
        except ValidationError as e:
            # Re-raise Pydantic's validation error.
            raise e

    # Prepare the body data for use in the core logic.
    # If body was None, it effectively becomes {}. If body was provided, use its validated form.
    body_data_for_logic: Dict[str, Any]
    if validated_body_model:
        body_data_for_logic = validated_body_model.model_dump(exclude_none=True, by_alias=True)
    else:
        body_data_for_logic = {}
    # --- End of Input Validation ---

    userId = 'me'
    _ensure_user(userId)
    
    # First, ensure the file record and its permissions list exist.
    _ensure_file(userId, fileId) 
    
    # Then, retrieve the file entry from the database.
    file_entry = DB['users'][userId]['files'].get(fileId)

    # A check for robustness, although _ensure_file should prevent this.
    if not file_entry:
        raise LookupError(f"File with ID '{fileId}' could not be found or created.")

    permissions = file_entry.get('permissions', [])
    
    if transferOwnership:
        # --- Ownership Transfer Logic ---
        # The user to be promoted is now identified by permissionId, not the body.
        permission_to_promote = next((p for p in permissions if p.get('id') == permissionId), None)

        if not permission_to_promote:
            raise LookupError(f"Permission with ID '{permissionId}' not found, cannot transfer ownership.")

        new_owner_email = permission_to_promote.get('emailAddress')
        if not new_owner_email:
            raise ValueError("Ownership can only be transferred to a permission with a valid email address.")

        # Demote all existing owners who are not the new owner
        for perm in permissions:
            if perm.get('role') == 'owner' and perm.get('id') != permissionId:
                perm['role'] = 'writer'
        
        # Apply any other updates from the body first
        permission_to_promote.update(body_data_for_logic)
        # Then, ensure the role is set to owner
        permission_to_promote['role'] = 'owner'

        # Update the top-level owners list on the file entry
        file_entry['owners'] = [new_owner_email]
        
        return permission_to_promote
    
    else:
        # --- Standard Permission Update Logic ---
        if body_data_for_logic.get('role') == 'owner':
            raise ValueError("Cannot set role to 'owner' directly. Use the transferOwnership=True flag.")

        permission_to_update = next((p for p in permissions if p.get('id') == permissionId), None)

        if permission_to_update:
            permission_to_update.update(body_data_for_logic)
            return permission_to_update

        raise LookupError(f"Permission with ID '{permissionId}' not found on file '{fileId}'.")