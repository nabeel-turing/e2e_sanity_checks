# gmail/Users/__init__.py
# Use relative imports
from pydantic import ValidationError
from ..SimulationEngine.models import ProfileInputModel
from ..SimulationEngine.db import DB
from ..SimulationEngine.utils import _ensure_user
from typing import Dict, Any, Optional


def getProfile(userId: str = "me") -> Dict[str, Any]:
    """Gets the user's Gmail profile information.

    Retrieves the profile data associated with the specified user ID from the database.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.

    Returns:
        Dict[str, Any]: A dictionary containing the user's profile information with keys such as:
            - 'emailAddress' (str): The user's email address
            - 'messagesTotal' (int): Total number of messages in the mailbox
            - 'threadsTotal' (int): Total number of threads in the mailbox
            - 'historyId' (str): The current history ID of the mailbox

    Raises:
        TypeError: If `userId` is not a string.
        ValueError: If `userId` is an empty string or does not exist in the database (propagated from database access).
    """
    # --- Input Validation ---
    if not isinstance(userId, str):
        raise TypeError("userId must be a string.")
    
    if userId.strip() == "":
        raise ValueError("userId cannot be an empty string.")
    # --- End Input Validation ---

    _ensure_user(userId)
    return DB["users"][userId]["profile"]


def watch(
    userId: str = "me", request: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Set up or update a watch on the user's mailbox.

    Stores the watch request configuration for the specified user.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        request (Optional[Dict[str, Any]]): An optional dictionary containing the watch request body.
                The exact structure depends on the watch configuration requirements.
                Defaults to None, resulting in an empty watch configuration.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - 'historyId' (str): The current history ID of the mailbox
            - 'expiration' (str): The expiration timestamp for the watch

    Raises:
        KeyError: If the specified `userId` does not exist in the database.
    """
    _ensure_user(userId)
    request = request or {}
    DB["users"][userId]["watch"] = request
    return {
        "historyId": DB["users"][userId]["profile"].get("historyId", "1"),
        "expiration": "9999999999999",
    }


def stop(userId: str = "me") -> Dict[str, Any]:
    """Stop receiving push notifications for the user's mailbox.

    Clears the stored watch configuration for the specified user.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.

    Returns:
        Dict[str, Any]: An empty dictionary, signifying the successful stop operation.

    Raises:
        KeyError: If the specified `userId` does not exist in the database.
    """
    _ensure_user(userId)
    DB["users"][userId]["watch"] = {}
    return {}


def exists(userId: str) -> bool:
    """Checks if a user exists in the database.

    Args:
        userId (str): The ID of the user to check.

    Returns:
        bool: True if the user exists in the database, False otherwise.

    Raises:
        TypeError: If userId is not a string.
        ValueError: If userId is empty or contains only whitespace.
    """
    # Type validation
    if not isinstance(userId, str):
        raise TypeError("userId must be a string.")

    # Value validation
    if not userId or not userId.strip():
        raise ValueError("userId cannot be empty or contain only whitespace.")

    # Check existence in database
    return userId in DB["users"]


def createUser(userId: str, profile: Dict[str, Any]) -> Dict[str, Any]:
    """Creates a new user entry in the database.

    Initializes the data structure for a new user, including profile,
    empty containers for drafts, messages, threads, labels, settings, history,
    and watch configuration.

    Args:
        userId (str): The unique identifier for the new user.
        profile (Dict[str, Any]): A dictionary containing the initial profile information.
            It must contain an 'emailAddress' (str) key. Other keys are permitted but ignored
            by this function's core logic beyond validation of 'emailAddress'.
            Example: {"emailAddress": "user@example.com", "displayName": "John Doe"}

    Returns:
        Dict[str, Any]: A dictionary representing the newly created user's data structure with keys:
            - 'profile' (Dict[str, Any]): User profile information
            - 'drafts' (Dict[str, Any]): Empty drafts container
            - 'messages' (Dict[str, Any]): Empty messages container
            - 'threads' (Dict[str, Any]): Empty threads container
            - 'labels' (Dict[str, Any]): Empty labels container
            - 'settings' (Dict[str, Any]): User settings with sub-keys:
                - 'imap' (Dict[str, Any]): IMAP settings
                - 'pop' (Dict[str, Any]): POP settings
                - 'vacation' (Dict[str, Any]): Vacation responder settings
                - 'language' (Dict[str, Any]): Language settings
                - 'autoForwarding' (Dict[str, Any]): Auto-forwarding settings
                - 'sendAs' (Dict[str, Any]): Send-as settings
            - 'history' (List[Any]): Empty history list
            - 'watch' (Dict[str, Any]): Empty watch configuration

    Raises:
        TypeError: If `userId` is not a string.
        pydantic.ValidationError: If the `profile` dictionary is invalid (e.g., missing 'emailAddress',
                                  or 'emailAddress' is not a string).
    """
    # --- Input Validation ---
    # Validate non-dictionary arguments
    if not isinstance(userId, str):
        raise TypeError(f"userId must be a string, got {type(userId).__name__}")
    
    if not isinstance(profile, dict):
        raise TypeError("profile must be a dict")
    
    # Validate dictionary arguments using Pydantic
    try:
        validated_profile = ProfileInputModel(**profile)
    except ValidationError as e:
        # Re-raise Pydantic's ValidationError.
        # The error messages from Pydantic are usually descriptive.
        # Example: if 'emailAddress' is missing, it will indicate that.
        # If 'emailAddress' is not a string, it will indicate that.
        raise e
    # --- End of Input Validation ---

    # --- Original Core Functionality ---
    # The global DB variable is assumed to be defined elsewhere in the application.
    # The 'profile' dictionary in the DB will only store 'emailAddress' from the input 'profile',
    # along with other hardcoded default values.
    DB["users"][userId] = {
        "profile": {
            "emailAddress": validated_profile.emailAddress, # Use the validated email address
            "messagesTotal": 0,
            "threadsTotal": 0,
            "historyId": "1",
        },
        "drafts": {},
        "messages": {},
        "threads": {},
        "labels": {},
        "settings": {
            "imap": {},
            "pop": {},
            "vacation": {"enableAutoReply": False},
            "language": {"displayLanguage": "en"},
            "autoForwarding": {"enabled": False},
            "sendAs": {},
        },
        "history": [],
        "watch": {},
    }

    return DB["users"][userId]
