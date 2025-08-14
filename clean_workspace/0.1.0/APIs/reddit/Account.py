from typing import Dict, Any, List, Optional
from .SimulationEngine.db import DB

"""
Simulation of /account endpoints.
Manages user account-related operations such as retrieving identity, preferences, friends, blocked users, and trophies.
"""

def get_api_v1_me() -> Dict[str, Any]:
    """
    Retrieves the identity details of the currently authenticated user.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - username (str): The user's username
            - id (str): The user's unique identifier
    """
    # For demo, return a hard-coded user
    return {"username": "mock_user", "id": "t2_mocked"}

def get_api_v1_me_blocked() -> List[str]:
    """
    Retrieves a list of users blocked by the authenticated user.

    Returns:
        List[str]: A list of usernames that have been blocked by the authenticated user.
    """
    # Mock a short list
    return ["blocked_user_1", "blocked_user_2"]

def get_api_v1_me_friends() -> List[str]:
    """
    Retrieves a list of friends for the authenticated user.

    Returns:
        List[str]: A list of usernames that are friends of the authenticated user.
    """
    return ["friend_user_1", "friend_user_2"]

def get_api_v1_me_karma() -> Dict[str, Any]:
    """
    Retrieves a breakdown of the authenticated user's subreddit karma.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - karma_by_subreddit (List[Dict[str, Any]]): List of subreddit-specific karma
                - subreddit (str): Name of the subreddit
                - karma (int): Karma points in that subreddit
            - total_karma (int): Total karma across all subreddits
    """
    return {
        "karma_by_subreddit": [
            {"subreddit": "python", "karma": 123},
            {"subreddit": "learnprogramming", "karma": 456}
        ],
        "total_karma": 579
    }

def get_api_v1_me_prefs(fields: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieves the preference settings of the authenticated user.

    Args:
        fields (Optional[str]): A comma-separated list of specific preference fields to return.
            If None, returns all preferences.

    Returns:
        Dict[str, Any]: A dictionary containing user preferences. Common fields include:
            - nightmode (bool): Whether night mode is enabled
            - label_nsfw (bool): Whether NSFW content is labeled
            - country_code (str): User's country code
    """
    # Could parse fields, but here we'll just return a mock set of prefs
    all_prefs = {
        "nightmode": True,
        "label_nsfw": False,
        "country_code": "US"
    }
    if not fields:
        return all_prefs
    requested = fields.split(',')
    return {key: value for key, value in all_prefs.items() if key in requested}

def patch_api_v1_me_prefs(new_preferences: Dict[str, Any]) -> Dict[str, Any]:
    """
    Updates the preference settings of the authenticated user.

    Args:
        new_preferences (Dict[str, Any]): A dictionary containing the preference fields to update.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - updated_prefs (Dict[str, Any]): The updated preferences
            - status (str): The status of the update operation
    """
    return {"updated_prefs": new_preferences, "status": "success"}

def get_api_v1_me_trophies() -> List[Dict[str, Any]]:
    """
    Retrieves the trophies (awards) earned by the authenticated user.

    Returns:
        List[Dict[str, Any]]: A list of trophy objects, each containing:
            - trophy_name (str): The name of the trophy
            - description (str): A description of how the trophy was earned
    """
    return [
        {"trophy_name": "Early_Adopter", "description": "Joined early on."},
        {"trophy_name": "Helper", "description": "Provided helpful contributions."}
    ]

def get_prefs_blocked() -> List[str]:
    """
    Retrieves detailed information about blocked users.

    Returns:
        List[str]: A list of usernames that have been blocked by the authenticated user.
    """
    return get_api_v1_me_blocked()

def get_prefs_friends() -> List[str]:
    """
    Retrieves detailed information about friends.

    Returns:
        List[str]: A list of usernames that are friends of the authenticated user.
    """
    return get_api_v1_me_friends()

def get_prefs_messaging() -> Dict[str, Any]:
    """
    Retrieves the messaging preferences of the authenticated user.

    Returns:
        Dict[str, Any]: A dictionary containing messaging preferences:
            - allow_pms (bool): Whether private messages are allowed
            - email_notifications (bool): Whether email notifications are enabled
    """
    return {
        "allow_pms": True,
        "email_notifications": False
    }

def get_prefs_trusted() -> List[str]:
    """
    Retrieves the trusted user list for the authenticated user.

    Returns:
        List[str]: A list of usernames that are trusted by the authenticated user.
    """
    return ["trusted_user_1"]

def get_prefs_where(where: str) -> Any:
    """
    Retrieves specific preference details from various preference categories.

    Args:
        where (str): The preference category to retrieve (e.g., "blocked", "friends").

    Returns:
        Any: The preferences for the specified category. Returns:
            - List[str] for "blocked" and "friends" categories
            - Dict[str, Any] for other preference categories
            - Dict[str, str] with error message if category not found

    Raises:
        ValueError: If the specified category is not supported.
    """
    if where == "blocked":
        return get_prefs_blocked()
    elif where == "friends":
        return get_prefs_friends()
    else:
        return {"detail": f"No mock preferences for category '{where}'"}
