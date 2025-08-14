# APIs/jira/MyPreferencesApi.py
from .SimulationEngine.utils import _check_empty_field
from .SimulationEngine.db import DB
from typing import Dict, Any, Optional


def get_my_preferences() -> Dict[str, Any]:
    """
    Get the current user's preferences.

    This method returns the preferences of the current user.

    Returns:
        Dict[str, Any]: A dictionary containing the current user's preferences
            - theme (str): The theme of the current user
            - notifications (str): The notifications of the current user
    """
    return DB["my_preferences"]


def update_my_preferences(value: Dict[str, Optional[str]]) -> Dict[str, Any]:
    """
    Update the current user's preferences.

    This method updates the preferences of the current user.

    Args:
        value (Dict[str, Optional[str]]): The preferences to update
            - theme (Optional[str]): The theme of the current user
            - notifications (Optional[str]): The notifications of the current user

    Returns:
        Dict[str, Any]: A dictionary containing the updated preferences
            - updated (bool): Whether the preferences were updated successfully
            - preferences (dict): The updated preferences
                - theme (str): The theme of the current user
                - notifications (str): The notifications of the current user

    Raises:
        ValueError: If the value is empty
    """
    err = _check_empty_field("value", value)
    if err:
        return {"error": err}

    DB["my_preferences"].update(value)
    return {"updated": True, "preferences": DB["my_preferences"]}
