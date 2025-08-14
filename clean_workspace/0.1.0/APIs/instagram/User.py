# instagram/User.py
from .SimulationEngine.custom_erros import EmptyUsernameError
from .SimulationEngine.custom_erros import UserAlreadyExistsError
from .SimulationEngine.db import DB
from typing import Dict, Any, List

"""Handles user-related operations."""


def create_user(user_id: str, name: str, username: str) -> Dict[str, Any]:
    """
    Creates a new user with a given ID, name, and username.

    Args:
        user_id (str): The unique identifier for the user.
        name (str): The name of the user.
        username (str): The username of the user.

    Returns:
        Dict[str, Any]: On successful creation, a dictionary containing the user's details:
            - "id" (str): The user's unique identifier.
            - "name" (str): The user's name.
            - "username" (str): The user's username.

    Raises:
        TypeError: If `user_id`, `name`, or `username` is not a string.
        ValueError: If `user_id`, `name`, or `username` is an empty string.
        UserAlreadyExistsError: If a user with the given `user_id` already exists.
    """
    # Input validation for non-dictionary arguments
    if not isinstance(user_id, str):
        raise TypeError("Argument 'user_id' must be a string.")
    if not user_id:  # Check for empty string
        raise ValueError("Field 'user_id' cannot be empty.")

    if not isinstance(name, str):
        raise TypeError("Argument 'name' must be a string.")
    if not name:  # Check for empty string
        raise ValueError("Field 'name' cannot be empty.")

    if not isinstance(username, str):
        raise TypeError("Argument 'username' must be a string.")
    if not username:  # Check for empty string
        raise ValueError("Field 'username' cannot be empty.")

    # Core logic of the function (preserved)
    # DB is assumed to be an accessible dictionary-like structure.
    if user_id in DB["users"]:
        raise UserAlreadyExistsError(f"User with ID '{user_id}' already exists.")

    DB["users"][user_id] = {"name": name, "username": username}
    return {"id": user_id, "name": name, "username": username}


def get_user(user_id: str) -> Dict[str, Any]:
    """
    Retrieves information about a specific user.

    Args:
        user_id (str): The unique identifier of the user to retrieve. Cannot be empty.

    Returns:
        Dict[str, Any]:
        - If the user does not exist (after passing input validation), returns a dictionary
          with the key "error" and the value "User not found."
        - On successful retrieval, returns a dictionary with the following keys and value types:
            - id (str): The user's unique identifier
            - name (str): The user's name
            - username (str): The user's username

    Raises:
        TypeError: If user_id is not a string.
        ValueError: If user_id is an empty string.
    """
    # --- Input Validation ---
    if not isinstance(user_id, str):
        raise TypeError("user_id must be a string.")
    if not user_id:  # Checks for empty string
        raise ValueError("Field user_id cannot be empty.")
    # --- End of Input Validation ---

    # --- Original Core Logic ---
    # DB is assumed to be an existing global or accessible dictionary-like structure.
    if user_id in DB["users"]:
        return {"id": user_id, **DB["users"][user_id]}
    return {"id": user_id, "error": "User not found"}


def list_users() -> List[Dict[str, Any]]:
    """
    Lists all users in the system.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, where each dictionary contains:
            - id (str): The user's unique identifier
            - name (str): The user's name
            - username (str): The user's username
    """
    return [{"id": user_id, **info} for user_id, info in DB["users"].items()]


def delete_user(user_id: str) -> Dict[str, Any]:
    """
    Deletes a specified user from the system.

    Args:
        user_id (str): The unique identifier of the user to delete.

    Returns:
        Dict[str, Any]:
        - If user_id is missing, returns a dictionary with the key "error" and the value "Field user_id cannot be empty."
        - If the user does not exist, returns a dictionary with the key "error" and the value "User not found."
        - On successful deletion, returns a dictionary with the key "success" and the value True.
    """
    if user_id in DB["users"]:
        del DB["users"][user_id]
        return {"success": True}
    return {"error": "User not found"}


def get_user_id_by_username(username: str) -> str:
    """
    Searches for a user by their username and returns the corresponding user ID.

    Args:
        username (str): The username to look up in the system.
                        This field cannot be an empty string or contain only whitespace.

    Returns:
        str: The user ID as a string if a user with the given username is found.
             If no user is found with the given username, this function returns
             the literal string "User not found" (as per original core logic).

    Raises:
        TypeError: If 'username' is not a string.
        EmptyUsernameError: If 'username' is an empty string or consists only of whitespace.
    """
    # --- Start of Input Validation ---
    if not isinstance(username, str):
        raise TypeError("Username must be a string.")
    
    # Check if username is empty or contains only whitespace characters
    # This validation is derived from the original docstring's requirement:
    # "If username is missing, returns a dictionary with the key "error" and the value "Field username cannot be empty."
    # which is now handled by raising EmptyUsernameError.
    if not username or username.isspace():
        raise EmptyUsernameError("Field username cannot be empty.")
    # --- End of Input Validation ---

    # Original core functionality (preserved)
    # The DB variable is assumed to be defined and accessible in this scope.
    for user_id, user in DB["users"].items():
        # The comparison uses .lower() on both sides, as in the original function.
        # This means that if 'username' has leading/trailing spaces (e.g., " alice "),
        # it will be compared as such, unless the stored username also has them.
        if user.get("username", "").lower() == username.lower():
            return user_id
            
    # This return statement is part of the original function's logic.
    # The original docstring incorrectly stated this would be a dictionary error.
    # The original code (and this refactored version) returns a string.
    return "User not found"
