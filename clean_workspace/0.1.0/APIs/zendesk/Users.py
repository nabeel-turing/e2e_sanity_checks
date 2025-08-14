# zendesk/Users.py

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pydantic import ValidationError
from .SimulationEngine.db import DB
from .SimulationEngine.custom_errors import UserNotFoundError, UserAlreadyExistsError
from .SimulationEngine.models import UserCreateInputData, UserResponseData
from .SimulationEngine.utils import _generate_sequential_id
from .SimulationEngine.models import UserCreateInputData, UserUpdateInputData, UserResponseData

def create_user(
    name: str, 
    email: str, 
    role: str = "end-user",
    organization_id: Optional[int] = None,
    tags: Optional[List[str]] = None,
    photo: Optional[Dict[str, Any]] = None,
    details: Optional[str] = None,
    default_group_id: Optional[int] = None,
    # Additional Zendesk API parameters
    alias: Optional[str] = None,
    custom_role_id: Optional[int] = None,
    external_id: Optional[str] = None,
    locale: Optional[str] = None,
    locale_id: Optional[int] = None,
    moderator: Optional[bool] = None,
    notes: Optional[str] = None,
    only_private_comments: Optional[bool] = None,
    phone: Optional[str] = None,
    remote_photo_url: Optional[str] = None,
    restricted_agent: Optional[bool] = None,
    shared_phone_number: Optional[bool] = None,
    signature: Optional[str] = None,
    suspended: Optional[bool] = None,
    ticket_restriction: Optional[str] = None,
    time_zone: Optional[str] = None,
    verified: Optional[bool] = None,
    user_fields: Optional[Dict[str, Any]] = None
) -> Dict[str, Union[str, int, bool, Dict[str, Any]]]:
    """Creates a new user with comprehensive Zendesk API support.

    Adds a new user to the database if the provided ID does not already exist.
    Supports all standard Zendesk API parameters with robust validation.

    Args:
        name (str): The name of the user (mandatory).
        email (str): The user's primary email address (mandatory).
        role (str): The user's role. Possible values: "end-user", "agent", "admin". Defaults to "end-user".
        organization_id (Optional[int]): The id of the user's organization. Defaults to None.
        tags (Optional[List[str]]): The user's tags. Defaults to None.
        photo (Optional[Dict[str, Any]]): The user's profile picture as Attachment object. Defaults to None.
        details (Optional[str]): Any details about the user. Defaults to None.
        default_group_id (Optional[int]): The id of the user's default group. Defaults to None.
        alias (Optional[str]): An alias displayed to end users. Defaults to None.
        custom_role_id (Optional[int]): A custom role if user is an agent on Enterprise plan. Defaults to None.
        external_id (Optional[str]): A unique identifier from another system. Defaults to None.
        locale (Optional[str]): The user's locale (BCP-47 compliant). Defaults to None.
        locale_id (Optional[int]): The user's language identifier. Defaults to None.
        moderator (Optional[bool]): Whether user has forum moderation capabilities. Defaults to None.
        notes (Optional[str]): Any notes about the user. Defaults to None.
        only_private_comments (Optional[bool]): Whether user can only create private comments. Defaults to None.
        phone (Optional[str]): The user's primary phone number. Defaults to None.
        remote_photo_url (Optional[str]): URL pointing to user's profile picture. Defaults to None.
        restricted_agent (Optional[bool]): If agent has restrictions. Defaults to None.
        shared_phone_number (Optional[bool]): Whether phone number is shared. Defaults to None.
        signature (Optional[str]): The user's signature (agents/admins only). Defaults to None.
        suspended (Optional[bool]): If agent is suspended. Defaults to None.
        ticket_restriction (Optional[str]): Which tickets user has access to. Defaults to None.
        time_zone (Optional[str]): The user's time zone. Defaults to None.
        verified (Optional[bool]): Whether any user identity is verified. Defaults to None.
        user_fields (Optional[Dict[str, Any]]): Values of custom fields in user's profile. Defaults to None.

    Returns:
        Dict[str, Union[str, int, bool, Dict[str, Any]]]: A dictionary indicating the success status and user details.
            - 'success' (bool): True,
            - 'user' (Dict[str, Any]): A dictionary containing the user details.
                - 'id' (int): The unique identifier for the user.
                - 'name' (str): The name of the user.
                - 'email' (str): The email address of the user.
                - 'role' (str): The role of the user.
                - 'organization_id' (int): The id of the user's organization.
                - 'tags' (List[str]): The user's tags.
                - 'photo' (Dict[str, Any]): The user's profile picture as Attachment object.
                - 'details' (str): Any details about the user.
                - 'default_group_id' (int): The id of the user's default group.
                - 'alias' (str): An alias displayed to end users.
                - 'custom_role_id' (int): A custom role if user is an agent on Enterprise plan.
                - 'external_id' (str): A unique identifier from another system.
                - 'locale' (str): The user's locale.
                - 'locale_id' (int): The user's language identifier.
                - 'moderator' (bool): Whether user has forum moderation capabilities.
                - 'notes' (str): Any notes about the user.
                - 'only_private_comments' (bool): Whether user can only create private comments.
                - 'phone' (str): The user's primary phone number.
                - 'remote_photo_url' (str): URL pointing to user's profile picture.
                - 'restricted_agent' (bool): If agent has restrictions.
                - 'shared_phone_number' (bool): Whether phone number is shared.
                - 'signature' (str): The user's signature.
                - 'suspended' (bool): If agent is suspended.
                - 'ticket_restriction' (str): Which tickets user has access to.
                - 'time_zone' (str): The user's time zone.
                - 'verified' (bool): Whether any user identity is verified.
                - 'user_fields' (Dict[str, Any]): Values of custom fields in user's profile.
                - 'active' (bool): Whether the user is active.
                - 'created_at' (str): The timestamp when the user was created.
                - 'updated_at' (str): The timestamp when the user was last updated.
                - 'url' (str): The API URL for the user.
    
    Raises:
        ValidationError: If any parameter fails Pydantic validation.
        UserAlreadyExistsError: If the user ID already exists.
    """
    try:
        # Validate input using Pydantic model
        user_data = UserCreateInputData(
            name=name,
            email=email,
            role=role,
            organization_id=organization_id,
            tags=tags,
            photo=photo,
            details=details,
            default_group_id=default_group_id,
            alias=alias,
            custom_role_id=custom_role_id,
            external_id=external_id,
            locale=locale,
            locale_id=locale_id,
            moderator=moderator,
            notes=notes,
            only_private_comments=only_private_comments,
            phone=phone,
            remote_photo_url=remote_photo_url,
            restricted_agent=restricted_agent,
            shared_phone_number=shared_phone_number,
            signature=signature,
            suspended=suspended,
            ticket_restriction=ticket_restriction,
            time_zone=time_zone,
            verified=verified,
            user_fields=user_fields
        )
    except ValidationError as e:
        # Re-raise the original validation error without trying to create a new one
        raise e
    
    # Create user object with validated data
    user_dict = user_data.model_dump(exclude_none=True)
    
    new_user_id = _generate_sequential_id("user")
    user_dict['id'] = new_user_id
    # Add read-only fields
    current_time = datetime.utcnow().isoformat() + "Z"
    user_dict.update({
        "active": True,
        "created_at": current_time,
        "updated_at": current_time,
        "url": f"/api/v2/users/{new_user_id}.json"
    })
    
    DB["users"][str(new_user_id)] = user_dict
    return {"success": True, "user": DB["users"][str(new_user_id)]}


def list_users() -> List[Dict[str, Any]]:
    """Lists all users in the database.

    Returns a list of all users in the database with comprehensive user details.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing user details.
            Each dictionary includes all user fields from the database:
            - id (int): The unique identifier for the user.
            - name (str): The name of the user.
            - email (str): The email address of the user.
            - role (str): The role of the user (end-user, agent, admin).
            - active (bool): Whether the user account is active.
            - created_at (str): ISO 8601 timestamp of user creation.
            - updated_at (str): ISO 8601 timestamp of last update.
            - url (str): API URL for the user resource.
            - organization_id (Optional[int]): ID of the user's organization.
            - tags (Optional[List[str]]): User's tags for categorization.
            - photo (Optional[Dict[str, Any]]): User's profile picture details with content_url.
            - details (Optional[str]): Additional details about the user.
            - default_group_id (Optional[int]): ID of the user's default group.
            - alias (Optional[str]): Display alias for the user.
            - external_id (Optional[str]): External system identifier.
            - locale (Optional[str]): User's locale (BCP-47 format).
            - locale_id (Optional[int]): User's language identifier.
            - moderator (Optional[bool]): Whether user has forum moderation capabilities.
            - notes (Optional[str]): Internal notes about the user.
            - only_private_comments (Optional[bool]): Whether user can only create private comments.
            - phone (Optional[str]): User's primary phone number.
            - remote_photo_url (Optional[str]): URL to user's profile picture.
            - restricted_agent (Optional[bool]): Whether agent has access restrictions.
            - shared_phone_number (Optional[bool]): Whether phone number is shared.
            - signature (Optional[str]): User's email signature.
            - suspended (Optional[bool]): Whether user account is suspended.
            - ticket_restriction (Optional[str]): Which tickets the user can access.
            - time_zone (Optional[str]): User's time zone.
            - verified (Optional[bool]): Whether user identity is verified.
            - user_fields (Optional[Dict[str, Any]]): Custom field values.
    """
    users = []
    
    # Create deep copies of users to avoid modifying the original database
    for user in DB["users"].values():
        user_copy = user.copy()
        
        # Deep copy nested structures
        if "photo" in user_copy and user_copy["photo"]:
            photo_copy = user_copy["photo"].copy()
            # Convert 'url' to 'content_url' to match the model
            # Only do this if 'content_url' doesn't already exist
            if "url" in photo_copy and "content_url" not in photo_copy:
                photo_copy["content_url"] = photo_copy.pop("url")
            elif "url" in photo_copy:
                # If both exist, just remove the 'url' field and keep 'content_url'
                photo_copy.pop("url")
            user_copy["photo"] = photo_copy
        
        if "user_fields" in user_copy and user_copy["user_fields"]:
            user_copy["user_fields"] = user_copy["user_fields"].copy()
        
        if "tags" in user_copy and user_copy["tags"]:
            user_copy["tags"] = user_copy["tags"].copy()
        
        users.append(user_copy)
    
    return users


def show_user(user_id: int) -> Dict[str, Any]:
    """Shows details of a specific user.

    Returns the details of a user based on their unique identifier.
    Returns comprehensive user information including all Zendesk API fields.

    Args:
        user_id (int): The unique identifier for the user.

    Returns:
        Dict[str, Any]: A dictionary containing comprehensive user details including:
            - 'id' (int): The unique identifier for the user.
            - 'name' (str): The name of the user.
            - 'email' (str): The email address of the user.
            - 'role' (str): The role of the user (end-user, agent, admin).
            - 'active' (bool): Whether the user account is active.
            - 'created_at' (str): ISO 8601 timestamp of user creation.
            - 'updated_at' (str): ISO 8601 timestamp of last update.
            - 'url' (str): API URL for the user resource.
            - 'organization_id' (Optional[int]): ID of the user's organization.
            - 'tags' (Optional[List[str]]): User's tags for categorization.
            - 'photo' (Optional[Dict[str, Any]]): User's profile picture details with content_url.
            - 'details' (Optional[str]): Additional details about the user.
            - 'default_group_id' (Optional[int]): ID of the user's default group.
            - 'alias' (Optional[str]): Display alias for the user.
            - 'external_id' (Optional[str]): External system identifier.
            - 'locale' (Optional[str]): User's locale (BCP-47 format).
            - 'locale_id' (Optional[int]): User's language identifier.
            - 'moderator' (Optional[bool]): Whether user has forum moderation capabilities.
            - 'notes' (Optional[str]): Internal notes about the user.
            - 'only_private_comments' (Optional[bool]): Whether user can only create private comments.
            - 'phone' (Optional[str]): User's primary phone number.
            - 'remote_photo_url' (Optional[str]): URL to user's profile picture.
            - 'restricted_agent' (Optional[bool]): Whether agent has access restrictions.
            - 'shared_phone_number' (Optional[bool]): Whether phone number is shared.
            - 'signature' (Optional[str]): User's email signature.
            - 'suspended' (Optional[bool]): Whether user account is suspended.
            - 'ticket_restriction' (Optional[str]): Which tickets the user can access.
            - 'time_zone' (Optional[str]): User's time zone.
            - 'verified' (Optional[bool]): Whether user identity is verified.
            - 'user_fields' (Optional[Dict[str, Any]]): Custom field values.
    
    Raises:
        TypeError: If the user ID is not an integer.
        ValueError: If the user ID is not positive.
        UserNotFoundError: If the user ID does not exist.
    """
    if isinstance(user_id, bool):
        raise TypeError("User ID must be an integer")
    
    if not isinstance(user_id, int):
        raise TypeError("User ID must be an integer")
    
    if user_id <= 0:
        raise ValueError("User ID must be a positive integer")
    
    if str(user_id) not in DB["users"]:
        raise UserNotFoundError(f"User ID {user_id} not found")
    
    # Get user data from database
    user_data = DB["users"].get(str(user_id))
    
    # Create a deep copy to avoid modifying the original database
    user_copy = user_data.copy()
    
    # Transform photo field to match the model structure
    if "photo" in user_copy and user_copy["photo"]:
        photo_copy = user_copy["photo"].copy()
        # Convert 'url' to 'content_url' to match the UserPhoto model
        # Only do this if 'content_url' doesn't already exist
        if "url" in photo_copy and "content_url" not in photo_copy:
            photo_copy["content_url"] = photo_copy.pop("url")
        elif "url" in photo_copy:
            # If both exist, just remove the 'url' field and keep 'content_url'
            photo_copy.pop("url")
        user_copy["photo"] = photo_copy
    
    # Deep copy nested structures
    if "user_fields" in user_copy and user_copy["user_fields"]:
        user_copy["user_fields"] = user_copy["user_fields"].copy()
    
    if "tags" in user_copy and user_copy["tags"]:
        user_copy["tags"] = user_copy["tags"].copy()
    
    return user_copy


def update_user(
    user_id: int,
    name: Optional[str] = None,
    email: Optional[str] = None,
    role: Optional[str] = None,
    organization_id: Optional[int] = None,
    tags: Optional[List[str]] = None,
    photo: Optional[Dict[str, Any]] = None,
    details: Optional[str] = None,
    default_group_id: Optional[int] = None,
    alias: Optional[str] = None,
    custom_role_id: Optional[int] = None,
    external_id: Optional[str] = None,
    locale: Optional[str] = None,
    locale_id: Optional[int] = None,
    moderator: Optional[bool] = None,
    notes: Optional[str] = None,
    only_private_comments: Optional[bool] = None,
    phone: Optional[str] = None,
    remote_photo_url: Optional[str] = None,
    restricted_agent: Optional[bool] = None,
    shared_phone_number: Optional[bool] = None,
    signature: Optional[str] = None,
    suspended: Optional[bool] = None,
    ticket_restriction: Optional[str] = None,
    time_zone: Optional[str] = None,
    verified: Optional[bool] = None,
    user_fields: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Updates an existing user with comprehensive Zendesk API support.

    This function allows you to update any combination of user fields for an existing user.
    Only the fields you specify will be updated; all other fields remain unchanged.
    The function automatically updates the `updated_at` timestamp when any field is modified.

    Key Features:
    - Partial updates: Only specified fields are updated
    - Comprehensive validation: All fields are validated according to Zendesk API standards
    - Automatic timestamp updates: `updated_at` is automatically set to current time
    - Flexible field combinations: Update any combination of fields in a single call

    Validation Rules:
    - String fields have length limits (e.g., name cannot be empty, details max 1000 chars)
    - Enum fields are validated against allowed values (e.g., role must be "end-user", "agent", or "admin")
    - Numeric IDs must be positive integers
    - Boolean fields must be actual boolean values
    - Tags are limited to 50 items, each under 50 characters

    Args:
        user_id (int): The unique identifier for the user to update. Must be a positive integer.
        name (Optional[str]): The new name of the user. Must be a non-empty string.
        email (Optional[str]): The new email address of the user. Must be a valid email format.
        role (Optional[str]): The new role of the user. Must be one of: "end-user", "agent", "admin".
            - "end-user": Regular user with limited permissions
            - "agent": Support agent with ticket management capabilities
            - "admin": Administrator with full system access
        organization_id (Optional[int]): The new ID of the user's organization. Must be a positive integer.
        tags (Optional[List[str]]): The new list of tags for categorizing the user. 
            Maximum 50 tags, each under 50 characters.
        photo (Optional[Dict[str, Any]]): The new user's profile picture as an Attachment object.
            Should contain fields like "id", "filename", "content_type", "size", "url".
        details (Optional[str]): Any new details about the user. Maximum 1000 characters.
        default_group_id (Optional[int]): The new ID of the user's default group. Must be a positive integer.
        alias (Optional[str]): A new alias displayed to end users. Maximum 100 characters.
        custom_role_id (Optional[int]): A new custom role ID for Enterprise plan agents. Must be a positive integer.
        external_id (Optional[str]): A new unique identifier from another system. Maximum 255 characters.
        locale (Optional[str]): The new user's locale in BCP-47 format.
        locale_id (Optional[int]): The new user's language identifier. Must be a positive integer.
        moderator (Optional[bool]): Whether the user has forum moderation capabilities.
        notes (Optional[str]): Any new internal notes about the user. Maximum 1000 characters.
        only_private_comments (Optional[bool]): Whether the user can only create private comments.
        phone (Optional[str]): The new user's primary phone number.
        remote_photo_url (Optional[str]): New URL pointing to the user's profile picture.
        restricted_agent (Optional[bool]): Whether the agent has access restrictions.
        shared_phone_number (Optional[bool]): Whether the phone number is shared.
        signature (Optional[str]): The new user's email signature (agents/admins only). Maximum 1000 characters.
        suspended (Optional[bool]): Whether the user account is suspended.
        ticket_restriction (Optional[str]): Which tickets the user has access to. Must be one of:
            - "organization": Access to tickets in user's organization
            - "groups": Access to tickets in user's groups
            - "assigned": Access only to assigned tickets
            - "requested": Access only to requested tickets
        time_zone (Optional[str]): The new user's time zone.
        verified (Optional[bool]): Whether any user identity is verified.
        user_fields (Optional[Dict[str, Any]]): New values of custom fields in the user's profile.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - 'success' (bool): True if the update was successful
            - 'user' (Dict[str, Any]): The complete updated user object with all fields            
                The user dictionary includes all standard Zendesk user fields:
                - 'id' (int): User's unique identifier
                - 'name' (str): User's full name
                - 'email' (str): User's email address
                - 'role' (str): User's role ("end-user", "agent", "admin")
                - 'active' (bool): Whether the user account is active
                - 'created_at' (str): ISO 8601 timestamp of user creation
                - 'updated_at' (str): ISO 8601 timestamp of last update (automatically updated)
                - 'url' (str): API URL for the user resource
                - Plus all optional fields that were set during creation/update
    
    Raises:
        ValidationError: If any parameter fails Pydantic validation.
        UserNotFoundError: If the user_id does not exist in the database.
    """
    try:
        # Create validation data dictionary with all provided parameters
        validation_data = {
            "user_id": user_id,
            "name": name,
            "email": email,
            "role": role,
            "organization_id": organization_id,
            "tags": tags,
            "photo": photo,
            "details": details,
            "default_group_id": default_group_id,
            "alias": alias,
            "custom_role_id": custom_role_id,
            "external_id": external_id,
            "locale": locale,
            "locale_id": locale_id,
            "moderator": moderator,
            "notes": notes,
            "only_private_comments": only_private_comments,
            "phone": phone,
            "remote_photo_url": remote_photo_url,
            "restricted_agent": restricted_agent,
            "shared_phone_number": shared_phone_number,
            "signature": signature,
            "suspended": suspended,
            "ticket_restriction": ticket_restriction,
            "time_zone": time_zone,
            "verified": verified,
            "user_fields": user_fields
        }
        
        # Validate input using Pydantic model
        update_data = UserUpdateInputData(**validation_data)
    except ValidationError as e:
        # Re-raise the original validation error without trying to create a new one
        raise e
    
    # Check if user exists
    if str(user_id) not in DB["users"]:
        raise UserNotFoundError(f"User ID {user_id} not found")
    
    # Get current user data
    current_user = DB["users"][str(user_id)]
    
    # Create update dictionary with only provided (non-None) parameters
    # Convert Pydantic model to dict and exclude None values and user_id
    update_dict = update_data.model_dump(exclude_none=True, exclude={'user_id'})
    
    # Update the user in the database
    current_user.update(update_dict)
    
    # Update the updated_at timestamp
    current_user["updated_at"] = datetime.utcnow().isoformat() + "Z"
    
    return {"success": True, "user": current_user}


def delete_user(user_id: int) -> Dict[str, Any]:
    """Deletes an existing user.

    Deletes a user based on their unique identifier and returns the complete user data
    that was deleted. This operation is irreversible.

    Args:
        user_id (int): The unique identifier for the user. Must be a positive integer.

    Returns:
        Dict[str, Any]: A dictionary containing the complete deleted user details including:
            - 'user_id' (int): The unique identifier for the user.
            - 'name' (str): The name of the user.
            - 'email' (str): The email address of the user.
            - 'role' (str): The role of the user (end-user, agent, admin).
            - 'active' (bool): Whether the user account was active.
            - 'created_at' (str): ISO 8601 timestamp of user creation.
            - 'updated_at' (str): ISO 8601 timestamp of last update.
            - 'url' (str): API URL for the user resource.
            - 'organization_id' (Optional[int]): ID of the user's organization.
            - 'tags' (Optional[List[str]]): User's tags for categorization.
            - 'photo' (Optional[Dict]): User's profile picture details with content_url.
            - 'details' (Optional[str]): Additional details about the user.
            - 'default_group_id' (Optional[int]): ID of the user's default group.
            - 'alias' (Optional[str]): Display alias for the user.
            - 'external_id' (Optional[str]): External system identifier.
            - 'locale' (Optional[str]): User's locale (BCP-47 format).
            - 'locale_id' (Optional[int]): User's language identifier.
            - 'moderator' (Optional[bool]): Whether user had forum moderation capabilities.
            - 'notes' (Optional[str]): Internal notes about the user.
            - 'only_private_comments' (Optional[bool]): Whether user could only create private comments.
            - 'phone' (Optional[str]): User's primary phone number.
            - 'remote_photo_url' (Optional[str]): URL to user's profile picture.
            - 'restricted_agent' (Optional[bool]): Whether agent had access restrictions.
            - 'shared_phone_number' (Optional[bool]): Whether phone number was shared.
            - 'signature' (Optional[str]): User's email signature.
            - 'suspended' (Optional[bool]): Whether user account was suspended.
            - 'ticket_restriction' (Optional[str]): Which tickets the user could access.
            - 'time_zone' (Optional[str]): User's time zone.
            - 'verified' (Optional[bool]): Whether user identity was verified.
            - 'user_fields' (Optional[Dict]): Custom field values.
    
    Raises:
        TypeError: 
            - If user_id is not an integer
        ValueError:
            - If user_id is not positive
        UserNotFoundError: If the user_id does not exist in the database
    """
    # Input validation - check for boolean values specifically
    if isinstance(user_id, bool):
        raise TypeError("User ID must be an integer")
    
    if not isinstance(user_id, int):
        raise TypeError("User ID must be an integer")
    
    if user_id <= 0:
        raise ValueError("User ID must be a positive integer")
    
    if str(user_id) not in DB["users"]:
        raise UserNotFoundError(f"User ID {user_id} not found")
    
    # Get the user data before deletion
    user_data = DB["users"][str(user_id)]
    
    # Create a deep copy to avoid modifying the original database
    user_copy = user_data.copy()
    
    # Transform photo field to match the model structure (if it exists)
    if "photo" in user_copy and user_copy["photo"]:
        photo_copy = user_copy["photo"].copy()
        # Convert 'url' to 'content_url' to match the UserPhoto model
        # Only do this if 'content_url' doesn't already exist
        if "url" in photo_copy and "content_url" not in photo_copy:
            photo_copy["content_url"] = photo_copy.pop("url")
        elif "url" in photo_copy:
            # If both exist, just remove the 'url' field and keep 'content_url'
            photo_copy.pop("url")
        user_copy["photo"] = photo_copy
    
    # Deep copy nested structures
    if "user_fields" in user_copy and user_copy["user_fields"]:
        user_copy["user_fields"] = user_copy["user_fields"].copy()
    
    if "tags" in user_copy and user_copy["tags"]:
        user_copy["tags"] = user_copy["tags"].copy()
    
    # Remove the user from the database
    deleted_user = DB["users"].pop(str(user_id))
    
    # Return the complete user data that was deleted
    return user_copy
