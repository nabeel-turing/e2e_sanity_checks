# gmail/Users/Settings/SendAs/__init__.py
import builtins
from typing import Optional, Dict, Any

# Use relative imports (go up FOUR levels)
from ....SimulationEngine.db import DB
from ....SimulationEngine.utils import _ensure_user
from ....SimulationEngine.models import SendAsCreatePayloadModel
from pydantic import ValidationError


def list(userId: str = "me") -> Dict[str, Any]:
    """Lists the 'Send as' aliases for the specified user.

    Retrieves all custom 'from' addresses (aliases) associated with the user's
    account from the database.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - 'sendAs' (List[Dict[str, Any]]): List of 'Send as' resources, each containing:
                - 'sendAsEmail' (str): The email address of the alias.
                - 'displayName' (str): The display name for the alias.
                - 'replyToAddress' (str): The reply-to address.
                - 'signature' (str): The email signature for the alias.
                - 'verificationStatus' (str): The verification status of the alias.

    Raises:
        KeyError: If the specified `userId` or their settings structure does not
                  exist in the database.
    """
    _ensure_user(userId)
    sas = DB["users"][userId]["settings"]["sendAs"]
    return {"sendAs": builtins.list(sas.values())}


def get(userId: str = "me", send_as_email: str = "") -> Optional[Dict[str, Any]]:
    """Gets the specified 'Send as' alias configuration.

    Retrieves the details of a specific custom 'from' address (alias)
    identified by its email address.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        send_as_email (str): The email address of the 'Send as' alias to retrieve.
                       Defaults to ''.

    Returns:
        Optional[Dict[str, Any]]: A dictionary representing the 'Send as' resource if found, otherwise None.
        The dictionary contains:
            - 'sendAsEmail' (str): The email address of the alias.
            - 'displayName' (str): The display name for the alias.
            - 'replyToAddress' (str): The reply-to address.
            - 'signature' (str): The email signature for the alias.
            - 'verificationStatus' (str): The verification status of the alias.
                                        Valid values: 'accepted', 'pending', 'rejected', 'expired'

    Raises:
        TypeError: If `userId` or `send_as_email` is not a string.
        ValueError: If `userId` is empty, contains only whitespace, or the user does not exist.
    """
    # --- Input Validation ---
    if not isinstance(userId, str):
        raise TypeError(f"userId must be a string, but got {type(userId).__name__}.")
    
    if not isinstance(send_as_email, str):
        raise TypeError(f"send_as_email must be a string, but got {type(send_as_email).__name__}.")
    
    if not userId.strip():
        raise ValueError("userId cannot be empty or contain only whitespace.")
    # --- End of Input Validation ---

    _ensure_user(userId)
    return DB["users"][userId]["settings"]["sendAs"].get(send_as_email)


def create(
    userId: str = "me", send_as: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Creates a new 'Send as' alias configuration.

    Adds a custom 'from' address (alias) to the user's account. The alias
    email address is used as the key. The verification status is
    typically set based on domain policies or user actions, but may default
    to 'accepted' in some implementations.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        send_as (Optional[Dict[str, Any]]): An optional dictionary containing the properties for the new
                 alias with keys:
                 - 'sendAsEmail' (str): The email address for the alias.
                 - 'displayName' (str): The display name for the alias.
                 - 'replyToAddress' (str): The reply-to address.
                 - 'signature' (str): The email signature for the alias.
                 Defaults to None, using defaults.

    Returns:
        Dict[str, Any]: A dictionary representing the newly created 'Send as' resource with keys:
            - 'sendAsEmail' (str): The email address of the alias.
            - 'displayName' (str): The display name for the alias.
            - 'replyToAddress' (str): The reply-to address.
            - 'signature' (str): The email signature for the alias.
            - 'verificationStatus' (str): The verification status of the alias.
                                        Valid values: 'accepted', 'pending', 'rejected', 'expired'

    Raises:
        TypeError: If `userId` is not a string or `send_as` is not a dictionary or None.
        ValueError: If `userId` is empty, contains only whitespace, or the user does not exist.
        ValidationError: If send_as dictionary contains invalid field types or values.
    """
    # --- Input Validation ---
    if not isinstance(userId, str):
        raise TypeError(f"userId must be a string, but got {type(userId).__name__}.")
    
    if not userId.strip():
        raise ValueError("userId cannot be empty or contain only whitespace.")
    
    # Validate with Pydantic if send_as is provided
    if send_as is not None:
        if not isinstance(send_as, dict):
            raise TypeError(f"send_as must be a dictionary or None, but got {type(send_as).__name__}.")
        send_as_validated = SendAsCreatePayloadModel(**send_as).model_dump(exclude_unset=True)
    else:
        send_as_validated = {}

    _ensure_user(userId)
    alias_count = len(DB["users"][userId]["settings"]["sendAs"]) + 1
    email = send_as_validated.get("sendAsEmail", f"alias{alias_count}@gmail.com")

    DB["users"][userId]["settings"]["sendAs"][email] = {
        "sendAsEmail": email,
        "displayName": send_as_validated.get("displayName", email),
        "replyToAddress": send_as_validated.get("replyToAddress", email),
        "signature": send_as_validated.get("signature", ""),
        "verificationStatus": "accepted",
    }

    return DB["users"][userId]["settings"]["sendAs"][email]


def update(
    userId: str = "me",
    send_as_email: str = "",
    send_as: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """Updates the specified 'Send as' alias configuration.

    Modifies an existing custom 'from' address (alias) identified by its email
    address, using the properties provided in the `send_as` argument.
    This performs a full update.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        send_as_email (str): The email address of the 'Send as' alias to update.
                       Defaults to ''.
        send_as (Optional[Dict[str, Any]]): An optional dictionary containing the updated properties with keys:
                 - 'displayName' (str): The display name for the alias.
                 - 'replyToAddress' (str): The reply-to address.
                 - 'signature' (str): The email signature for the alias.
                 - Other optional send_as properties.
                 Defaults to None.

    Returns:
        Optional[Dict[str, Any]]: A dictionary representing the updated 'Send as' resource if found and
        updated, otherwise None. The dictionary contains:
            - 'sendAsEmail' (str): The email address of the alias.
            - 'displayName' (str): The display name for the alias.
            - 'replyToAddress' (str): The reply-to address.
            - 'signature' (str): The email signature for the alias.
            - 'verificationStatus' (str): The verification status of the alias.

    Raises:
        KeyError: If the specified `userId` or their settings structure does not
                  exist in the database.
    """
    _ensure_user(userId)
    send_as = send_as or {}
    existing = DB["users"][userId]["settings"]["sendAs"].get(send_as_email)
    if not existing:
        return None
    existing.update(send_as)
    return existing


def patch(
    userId: str = "me",
    send_as_email: str = "",
    send_as: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """Updates the specified 'Send as' alias configuration. Alias for update.

    This function is an alias for the `update` function. It modifies an
    existing alias. Note: This implementation performs patch as a full update.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        send_as_email (str): The email address of the alias to update/patch.
                       Defaults to ''.
        send_as (Optional[Dict[str, Any]]): An optional dictionary containing the properties to update with keys:
                 - 'displayName' (str): The display name for the alias.
                 - 'replyToAddress' (str): The reply-to address.
                 - 'signature' (str): The email signature for the alias.
                 - Other optional send_as properties.
                 Defaults to None.

    Returns:
        Optional[Dict[str, Any]]: A dictionary representing the updated 'Send as' resource if found and
        updated, otherwise None. The dictionary contains:
            - 'sendAsEmail' (str): The email address of the alias.
            - 'displayName' (str): The display name for the alias.
            - 'replyToAddress' (str): The reply-to address.
            - 'signature' (str): The email signature for the alias.
            - 'verificationStatus' (str): The verification status of the alias.

    Raises:
        KeyError: If the specified `userId` or their settings structure does not
                  exist in the database.
    """
    return update(userId, send_as_email, send_as)


def delete(userId: str = "me", send_as_email: str = "") -> None:
    """Deletes the specified 'Send as' alias.

    Removes a custom 'from' address (alias) identified by its email address
    from the user's account.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        send_as_email (str): The email address of the 'Send as' alias to delete.
                       Defaults to ''.

    Returns:
        None.

    Raises:
        KeyError: If the specified `userId` or their settings structure does not
                  exist in the database.
    """
    _ensure_user(userId)
    DB["users"][userId]["settings"]["sendAs"].pop(send_as_email, None)


def verify(userId: str = "me", send_as_email: str = "") -> Optional[Dict[str, Any]]:
    """Verifies the specified 'Send as' alias.

    Initiates the verification process for a custom 'from' address. If the alias
    exists and requires verification (e.g., status is 'pending'), its status
    may be updated to 'accepted' upon successful verification.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        send_as_email (str): The email address of the 'Send as' alias to verify.
                       Defaults to ''.

    Returns:
        Optional[Dict[str, Any]]: A dictionary representing the 'Send as' resource after attempting
        verification, otherwise None. The dictionary contains:
            - 'sendAsEmail' (str): The email address of the alias.
            - 'displayName' (str): The display name for the alias.
            - 'replyToAddress' (str): The reply-to address.
            - 'signature' (str): The email signature for the alias.
            - 'verificationStatus' (str): The verification status of the alias.

    Raises:
        KeyError: If the specified `userId` or their settings structure does not
                  exist in the database.
    """
    _ensure_user(userId)
    existing = DB["users"][userId]["settings"]["sendAs"].get(send_as_email)
    if existing and existing.get("verificationStatus") == "pending":
        existing["verificationStatus"] = "accepted"
    return existing
