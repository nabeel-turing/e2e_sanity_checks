# APIs/jira/GroupApi.py
from .SimulationEngine.db import DB
from .SimulationEngine.custom_errors import GroupAlreadyExistsError
from typing import Any, Dict, List

def get_group(groupname: str) -> Dict[str, Dict[str, Any]]:
    """
    Retrieve a specific group by its name.

    This method returns detailed information about a specific group
    identified by its name. Groups in Jira are used to manage user permissions
    and access control.

    Args:
        groupname (str): The name of the group to retrieve. Cannot be empty or whitespace-only.

    Returns:
        Dict[str, Dict[str, Any]]: A dictionary containing:
            - group (Dict[str, Any]): The group object containing:
                - name (str): The name of the group
                - users (List[str]): List of names of users in the group

    Raises:
        TypeError: If groupname is not a string.
        ValueError: If the groupname is empty, whitespace-only, or if the group does not exist in the database.
    """
    if not isinstance(groupname, str):
        raise TypeError(f"Expected groupname to be a string, but got {type(groupname).__name__}.")
    if not groupname or groupname.isspace():
        raise ValueError("groupname cannot be empty or consist only of whitespace.")

    group_data = DB["groups"].get(groupname)
    if not group_data:
        raise ValueError(f"Group '{groupname}' not found.")

    return {"group": group_data}


def update_group(groupname: str, users: List[str]) -> Dict[str, Any]:
    """
    Update the members of an existing group.

    This method allows updating the list of users in a specific group.
    The group must exist before it can be updated.

    Args:
        groupname (str): The name of the group to update
        users (List[str]): List of usernames to add to the group

    Returns:
        Dict[str, Any]: A dictionary containing:
            - {groupname} (Dict[str, Any]): The updated group object containing:
                - name (str): The name of the group
                - users (List[str]): List of usernames in the group

    Raises:
        TypeError: If groupname is not a string or users is not a list
        ValueError: If groupname is empty, whitespace-only, or if the group does not exist
        ValueError: If any user in the users list is not a string or is empty/whitespace-only
    """
    # Input validation for groupname
    if not isinstance(groupname, str):
        raise TypeError(f"Expected groupname to be a string, but got {type(groupname).__name__}.")
    if not groupname or groupname.isspace():
        raise ValueError("groupname cannot be empty or consist only of whitespace.")
    
    # Input validation for users
    if not isinstance(users, List):
        raise TypeError(f"Expected users to be a List, but got {type(users).__name__}.")
    
    # Validate each user in the List
    for i, user in enumerate(users):
        if not isinstance(user, str):
            raise TypeError(f"Expected all users to be strings, but user at index {i} is {type(user).__name__}.")
        if not user or user.isspace():
            raise ValueError(f"User at index {i} cannot be empty or consist only of whitespace.")

    # Check if group exists
    if groupname not in DB["groups"]:
        raise ValueError(f"Group '{groupname}' does not exist.")
    
    # Update the group
    updated_group = {"name": groupname, "users": users}
    DB["groups"][groupname] = updated_group
    return {groupname: updated_group}


def create_group(name: str) -> Dict[str, Any]:
    """
    Create a new group.

    This method creates a new group with the specified name. The group
    will initially have no members.

    Args:
        name (str): The name of the group to create.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - created (bool): True if the group was successfully created.
            - group (Dict[str, Any]): The created group object containing:
                - name (str): The name of the group.
                - users (List[str]): Empty list of users.

    Raises:
        TypeError: If 'name' is not a string.
        ValueError: If 'name' is empty or consists only of whitespace.
        GroupAlreadyExistsError: If the group with the given 'name' already exists.
    """
    # Input validation
    if not isinstance(name, str):
        raise TypeError("Argument 'name' must be a string.")
    if not name or name.isspace(): # Check for empty or whitespace-only string
        raise ValueError("Argument 'name' cannot be empty or consist only of whitespace.")

    # Core logic (adapted from original to raise exceptions)
    # DB is assumed to be a globally available dictionary representing the database.
    if name in DB["groups"]:
        raise GroupAlreadyExistsError(f"Group '{name}' already exists.")
    
    DB["groups"][name] = {"name": name, "users": []}
    return {"created": True, "group": DB["groups"][name]}


def delete_group(groupname: str) -> Dict[str, Any]:
    """
    Delete an existing group.

    This method permanently removes a group from the system. All users
    in the group will lose their group-based permissions.

    Args:
        groupname (str): The name of the group to delete

    Returns:
        Dict[str, Any]: A dictionary containing:
            - deleted (str): The name of the deleted group

    Raises:
        TypeError: If groupname is not a string.
        ValueError: If the groupname is empty.
        ValueError: If the group does not exist.
    """
    if not isinstance(groupname, str):
        raise TypeError("groupname must be a string.")
    if not groupname:
        raise ValueError("groupname cannot be empty.")

    if groupname not in DB["groups"]:
        raise ValueError(f"Group '{groupname}' does not exist.")
    
    DB["groups"].pop(groupname)
    
    return {"deleted": groupname}
