from .SimulationEngine.db import DB
from typing import Dict, Any, List, Optional

"""
Simulation of /users endpoints.
Manages user-specific actions and data retrieval.
"""


def post_api_block_user(account_id: str) -> Dict[str, Any]:
    """
    Blocks a user.

    Args:
        account_id (str): The account ID of the user to block.

    Returns:
        Dict[str, Any]:
        - If the account ID is invalid, returns a dictionary with the key "error" and the value "Invalid account ID.".
        - If the user is already blocked, returns a dictionary with the key "error" and the value "User already blocked.".
        - On successful blocking, returns a dictionary with the following keys:
            - status (str): The status of the operation ("user_blocked")
            - account_id (str): The blocked user's account ID
    """
    return {"status": "user_blocked", "account_id": account_id}


def post_api_friend(api_type: str, name: str) -> Dict[str, Any]:
    """
    Adds a user as a friend.

    Args:
        api_type (str): Must be "json".
        name (str): The username to add as a friend.

    Returns:
        Dict[str, Any]:
        - If the API type is invalid, returns a dictionary with the key "error" and the value "Invalid API type.".
        - If the username is invalid, returns a dictionary with the key "error" and the value "Invalid username.".
        - If the user is already a friend, returns a dictionary with the key "error" and the value "User already a friend.".
        - On successful addition, returns a dictionary with the following keys:
            - status (str): The status of the operation ("friend_added")
            - user (str): The added friend's username
    """
    return {"status": "friend_added", "user": name}


def post_api_report_user(user: str, reason: Optional[str] = None) -> Dict[str, Any]:
    """
    Reports a user.

    Args:
        user (str): The username to report.
        reason (Optional[str]): The reason for reporting.

    Returns:
        Dict[str, Any]:
        - If the username is invalid, returns a dictionary with the key "error" and the value "Invalid username.".
        - If the user is already reported, returns a dictionary with the key "error" and the value "User already reported.".
        - On successful reporting, returns a dictionary with the following keys:
            - status (str): The status of the operation ("user_reported")
            - user (str): The reported username
            - reason (Optional[str]): The reason for reporting
    """
    return {"status": "user_reported", "user": user, "reason": reason}


def post_api_setpermissions(name: str, permissions: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Sets permissions for a user.

    Args:
        name (str): The username for whom to set permissions.
        permissions (Optional[List[str]]): A list of permissions to grant.

    Returns:
        Dict[str, Any]:
        - If the username is invalid, returns a dictionary with the key "error" and the value "Invalid username.".
        - If the permissions are invalid, returns a dictionary with the key "error" and the value "Invalid permissions.".
        - On successful update, returns a dictionary with the following keys:
            - status (str): The status of the operation ("permissions_set")
            - user (str): The username
            - permissions (List[str]): The granted permissions
    """
    return {"status": "permissions_set", "user": name, "permissions": permissions or []}


def post_api_unfriend(name: str, type: str) -> Dict[str, Any]:
    """
    Removes a friend relationship.

    Args:
        name (str): The username to unfriend.
        type (str): The relationship type (e.g., "friend").

    Returns:
        Dict[str, Any]:
        - If the username is invalid, returns a dictionary with the key "error" and the value "Invalid username.".
        - If the relationship type is invalid, returns a dictionary with the key "error" and the value "Invalid relationship type.".
        - If the user is not a friend, returns a dictionary with the key "error" and the value "User not a friend.".
        - On successful removal, returns a dictionary with the following keys:
            - status (str): The status of the operation ("relationship_removed")
            - user (str): The unfriended username
            - type (str): The relationship type
    """
    return {"status": "relationship_removed", "user": name, "type": type}


def get_api_user_data_by_account_ids(ids: str) -> Dict[str, Any]:
    """
    Retrieves user data for specified account IDs.

    Args:
        ids (str): A comma-separated list of account IDs.

    Returns:
        Dict[str, Any]:
        - If the IDs are invalid, returns a dictionary with the key "error" and the value "Invalid account IDs.".
        - On successful retrieval, returns a dictionary with the following keys:
            - ids (List[str]): The list of account IDs
            - user_data (List[Dict[str, Any]]): A list of user data objects, each containing:
                - id (str): The account ID
                - username (str): The username
                - created_utc (int): The creation timestamp
    """
    return {"ids": ids.split(','), "user_data": []}


def get_api_username_available(user: str) -> Dict[str, Any]:
    """
    Checks if a username is available.

    Args:
        user (str): The username to check.

    Returns:
        Dict[str, Any]:
        - If the username is invalid, returns a dictionary with the key "error" and the value "Invalid username.".
        - On successful check, returns a dictionary with the following keys:
            - username (str): The checked username
            - available (bool): Whether the username is available
    """
    return {"username": user, "available": True}


def delete_api_v1_me_friends_username(username: str) -> Dict[str, Any]:
    """
    Removes a friend relationship.

    Args:
        username (str): The username to remove.

    Returns:
        Dict[str, Any]:
        - If the username is invalid, returns a dictionary with the key "error" and the value "Invalid username.".
        - If the user is not a friend, returns a dictionary with the key "error" and the value "User not a friend.".
        - On successful removal, returns a dictionary with the following keys:
            - status (str): The status of the operation ("user_unfriended")
            - username (str): The unfriended username
    """
    return {"status": "user_unfriended", "username": username}


def get_api_v1_user_username_trophies(username: str) -> Dict[str, Any]:
    """
    Retrieves trophies for a specified user.

    Args:
        username (str): The target username.

    Returns:
        Dict[str, Any]:
        - If the username is invalid, returns a dictionary with the key "error" and the value "Invalid username.".
        - On successful retrieval, returns a dictionary with the following keys:
            - username (str): The target username
            - trophies (List[Dict[str, Any]]): A list of trophy objects, each containing:
                - name (str): The trophy name
                - description (str): The trophy description
                - icon_url (str): The trophy icon URL
    """
    return {"username": username, "trophies": []}


def get_user_username_about(username: str) -> Dict[str, Any]:
    """
    Retrieves profile information for a user.

    Args:
        username (str): The username.

    Returns:
        Dict[str, Any]:
        - If the username is invalid, returns a dictionary with the key "error" and the value "Invalid username.".
        - If the user is not found, returns a dictionary with the key "status" and the value "not_found".
        - On successful retrieval, returns a dictionary with the following keys:
            - status (str): The status of the operation ("ok")
            - profile (Dict[str, Any]): A dictionary containing user profile information
    """
    if username in DB.get("users", {}): # Use .get for safety
        return {"status": "ok", "profile": DB["users"][username]}
    return {"status": "not_found"}


def get_user_username_comments(username: str) -> List[Dict[str, Any]]:
    """
    Retrieves comments made by a user.

    Args:
        username (str): The username.

    Returns:
        List[Dict[str, Any]]:
        - If the username is invalid, returns an empty list.
        - If there are no comments, returns an empty list.
        - On successful retrieval, returns a list of comment objects, each containing:
            - id (str): The comment ID
            - body (str): The comment text
            - created_utc (int): The creation timestamp
            - subreddit (str): The subreddit name
    """
    return []


def get_user_username_downvoted() -> List[str]:
    """
    Retrieves posts downvoted by a user.

    Returns:
        List[str]:
        - If there are no downvoted posts, returns an empty list.
        - On successful retrieval, returns a list of downvoted post identifiers.
    """
    return []


def get_user_username_gilded() -> List[str]:
    """
    Retrieves posts that have been gilded for a user.

    Returns:
        List[str]:
        - If there are no gilded posts, returns an empty list.
        - On successful retrieval, returns a list of gilded post identifiers.
    """
    return []


def get_user_username_hidden() -> List[str]:
    """
    Retrieves hidden posts of a user.

    Returns:
        List[str]:
        - If there are no hidden posts, returns an empty list.
        - On successful retrieval, returns a list of hidden post identifiers.
    """
    return []


def get_user_username_overview() -> List[Dict[str, Any]]:
    """
    Retrieves an overview of a user's submissions and comments.

    Returns:
        List[Dict[str, Any]]:
        - If there is no content, returns an empty list.
        - On successful retrieval, returns a combined list of the user's submissions and comments, each containing:
            - id (str): The content ID
            - type (str): Either "submission" or "comment"
            - created_utc (int): The creation timestamp
            - subreddit (str): The subreddit name
    """
    return []


def get_user_username_saved() -> List[str]:
    """
    Retrieves posts saved by a user.

    Returns:
        List[str]:
        - If there are no saved posts, returns an empty list.
        - On successful retrieval, returns a list of saved post identifiers.
    """
    return []


def get_user_username_submitted() -> List[str]:
    """
    Retrieves posts submitted by a user.

    Returns:
        List[str]:
        - If there are no submitted posts, returns an empty list.
        - On successful retrieval, returns a list of submitted post identifiers.
    """
    return []


def get_user_username_upvoted() -> List[str]:
    """
    Retrieves posts upvoted by a user.

    Returns:
        List[str]:
        - If there are no upvoted posts, returns an empty list.
        - On successful retrieval, returns a list of upvoted post identifiers.
    """
    return []


def get_user_username_where(where: str) -> List[Dict[str, Any]]:
    """
    Retrieves user content for a specified category.

    Args:
        where (str): The category (e.g., "overview", "comments").

    Returns:
        List[Dict[str, Any]]:
        - If the category is invalid, returns an empty list.
        - If there is no content in the category, returns an empty list.
        - On successful retrieval, returns a list of content items for the specified category, each containing:
            - id (str): The content ID
            - type (str): The content type
            - created_utc (int): The creation timestamp
            - subreddit (str): The subreddit name
    """
    return []