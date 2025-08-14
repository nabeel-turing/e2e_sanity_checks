# gmail/Users/Settings/Vacation.py
from typing import Dict, Any
from ...SimulationEngine.db import DB
from ...SimulationEngine.utils import _ensure_user


def getVacation(userId: str = "me") -> Dict[str, Any]:
    """Gets the vacation responder settings for the specified user.

    Retrieves the current vacation auto-reply configuration associated with the
    user's account from the database.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.

    Returns:
        Dict[str, Any]: A dictionary containing the user's vacation responder settings with keys:
            - 'enableAutoReply' (bool): Whether the vacation auto-reply is enabled.
            - 'responseSubject' (str): Subject line of the auto-reply message.
            - 'responseBodyHtml' (str): HTML body of the auto-reply message.
            - 'restrictToContacts' (bool): Whether to only send to contacts.
            - 'restrictToDomain' (bool): Whether to only send within domain.
            - 'startTime' (str): Unix timestamp (ms) when auto-reply starts.
            - 'endTime' (str): Unix timestamp (ms) when auto-reply ends.
            - Other vacation settings as defined in the database.

    Raises:
        KeyError: If the specified `userId` or their settings structure does not
                  exist in the database.
    """
    _ensure_user(userId)
    return DB["users"][userId]["settings"]["vacation"]


def updateVacation(
    userId: str = "me", vacation_settings: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Updates the vacation responder settings for the specified user.

    Modifies the vacation auto-reply configuration for the user's account based
    on the provided `vacation_settings`. Only the fields present in the input
    dictionary are updated.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        vacation_settings (Dict[str, Any]): An optional dictionary containing the vacation settings
                           to update with keys:
                           - 'enableAutoReply' (bool): Whether to enable vacation auto-reply.
                           - 'responseSubject' (str): Subject line of the auto-reply message.
                           - 'responseBodyHtml' (str): HTML body of the auto-reply message.
                           - Other optional vacation settings.
                           Defaults to None, resulting in no changes.

    Returns:
        Dict[str, Any]: A dictionary containing the complete, updated vacation settings for the user with keys:
            - 'enableAutoReply' (bool): Whether the vacation auto-reply is enabled.
            - 'responseSubject' (str): Subject line of the auto-reply message.
            - 'responseBodyHtml' (str): HTML body of the auto-reply message.
            - 'restrictToContacts' (bool): Whether to only send to contacts.
            - 'restrictToDomain' (bool): Whether to only send within domain.
            - 'startTime' (str): Unix timestamp (ms) when auto-reply starts.
            - 'endTime' (str): Unix timestamp (ms) when auto-reply ends.
            - Other vacation settings as defined in the database.

    Raises:
        KeyError: If the specified `userId` or their settings structure does not
                  exist in the database.
    """
    _ensure_user(userId)
    vacation_settings = vacation_settings or {}
    DB["users"][userId]["settings"]["vacation"].update(vacation_settings)
    return DB["users"][userId]["settings"]["vacation"]
