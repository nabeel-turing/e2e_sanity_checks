# gmail/Users/Settings/SendAs/SmimeInfo.py
import builtins
from typing import Optional, Dict, Any

# Use relative imports (go up FOUR levels)
from ....SimulationEngine.db import DB
from ....SimulationEngine.utils import _ensure_user, _next_counter


def list(userId: str = "me", send_as_email: str = "") -> Dict[str, Any]:
    """Lists the S/MIME info for a specific 'Send as' alias.

    Retrieves all S/MIME certificate configurations associated with the given
    user ID and 'Send as' email address from the database.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        send_as_email (str): The email address of the 'Send as' alias.
                       Defaults to ''.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - 'smimeInfo' (List[Dict[str, Any]]): List of S/MIME info resources.
            If the 'Send as' alias is not found or has no S/MIME info, the list
            within the dictionary will be empty. Otherwise, the list will contain
            dictionaries with the S/MIME properties as defined in the database.

    Raises:
        KeyError: If the specified `userId` does not exist in the database.
    """
    _ensure_user(userId)
    send_as_entry = DB["users"][userId]["settings"]["sendAs"].get(send_as_email)
    if send_as_entry is None:
        return {"smimeInfo": []}
    smime_info_dict = send_as_entry.setdefault("smimeInfo", {})
    return {"smimeInfo": builtins.list(smime_info_dict.values())}


def get(
    userId: str = "me", send_as_email: str = "", smime_id: str = ""
) -> Optional[Dict[str, Any]]:
    """Gets the specified S/MIME info for a specific 'Send as' alias.

    Retrieves a specific S/MIME certificate configuration identified by its ID,
    associated with the given user ID and 'Send as' email address.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        send_as_email (str): The email address of the 'Send as' alias.
                       Defaults to ''.
        smime_id (str): The ID of the S/MIME info to retrieve. Defaults to ''.

    Returns:
        Optional[Dict[str, Any]]: A dictionary representing the S/MIME info resource if found,
        otherwise None. The dictionary contains:
            - 'id' (str): The ID of the S/MIME info.
            - Other S/MIME properties as defined in the database.

    Raises:
        KeyError: If the specified `userId` does not exist in the database.
    """
    _ensure_user(userId)
    send_as_entry = DB["users"][userId]["settings"]["sendAs"].get(send_as_email)
    if not send_as_entry:
        return None
    return send_as_entry.setdefault("smimeInfo", {}).get(smime_id)


def insert(
    userId: str = "me", send_as_email: str = "", smime: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Inserts a new S/MIME info configuration for the specified 'Send as' alias.

    Creates and stores a new S/MIME certificate configuration. Generates a
    unique ID for the new S/MIME info.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        send_as_email (str): The email address of the 'Send as' alias to associate
                       the S/MIME info with. Defaults to ''.
        smime (Optional[Dict[str, Any]]): An optional dictionary containing the S/MIME properties with keys:
                - 'encryptedKey' (str): The encrypted key for the S/MIME certificate.
                - Other optional S/MIME properties.
                Defaults to None.

    Returns:
        Dict[str, Any]: A dictionary representing the newly inserted S/MIME info resource with keys:
            - 'id' (str): The ID of the S/MIME info.
            - 'encryptedKey' (str): The encrypted key for the S/MIME certificate.
            - Other S/MIME properties as defined in the database.

    Raises:
        KeyError: If the specified `userId` does not exist in the database.
    """
    _ensure_user(userId)
    smime = smime or {}
    send_as_entry = DB["users"][userId]["settings"]["sendAs"].setdefault(
        send_as_email, {}
    )
    smime_dict = send_as_entry.setdefault("smimeInfo", {})
    sid_num = _next_counter("smime")
    sid = f"smime_{sid_num}"
    new_smime = {
        "id": sid,
        "encryptedKey": smime.get("encryptedKey", ""),
    }
    smime_dict[sid] = new_smime
    return new_smime


def update(
    userId: str = "me",
    send_as_email: str = "",
    id: str = "",
    smime: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """Updates the specified S/MIME info.

    Modifies an existing S/MIME certificate configuration identified by its ID.
    This performs a full update, replacing existing properties.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        send_as_email (str): The email address of the 'Send as' alias associated
                       with the S/MIME info. Defaults to ''.
        id (str): The ID of the S/MIME info to update. Defaults to ''.
        smime (Optional[Dict[str, Any]]): An optional dictionary containing the updated S/MIME properties with keys:
                - 'encryptedKey' (str): The encrypted key for the S/MIME certificate.
                - Other optional S/MIME properties.
                Defaults to None.

    Returns:
        Optional[Dict[str, Any]]: A dictionary representing the updated S/MIME info resource if found and
        updated, otherwise None. The dictionary contains:
            - 'id' (str): The ID of the S/MIME info.
            - Other S/MIME properties as defined in the database.

    Raises:
        KeyError: If the specified `userId` does not exist in the database.
    """
    _ensure_user(userId)
    smime = smime or {}
    send_as_entry = DB["users"][userId]["settings"]["sendAs"].get(send_as_email)
    if not send_as_entry:
        return None
    smime_dict = send_as_entry.setdefault("smimeInfo", {})
    existing = smime_dict.get(id)
    if not existing:
        return None
    existing.update(smime)
    return existing


def patch(
    userId: str = "me",
    send_as_email: str = "",
    id: str = "",
    smime: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """Updates the specified S/MIME info. Alias for update.

    This function is an alias for the `update` function. It modifies an
    existing S/MIME certificate configuration. Note: Implemented as a full update.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        send_as_email (str): The email address of the 'Send as' alias. Defaults to ''.
        id (str): The ID of the S/MIME info to update/patch. Defaults to ''.
        smime (Optional[Dict[str, Any]]): An optional dictionary containing the properties to update with keys:
                - 'encryptedKey' (str): The encrypted key for the S/MIME certificate.
                - Other optional S/MIME properties.
                Defaults to None.

    Returns:
        Optional[Dict[str, Any]]: A dictionary representing the updated S/MIME info resource if found and
        updated, otherwise None. The dictionary contains:
            - 'id' (str): The ID of the S/MIME info.
            - Other S/MIME properties as defined in the database.

    Raises:
        KeyError: If the specified `userId` does not exist in the database.
    """
    return update(userId, send_as_email, id, smime)


def delete(userId: str = "me", send_as_email: str = "", id: str = "") -> None:
    """Deletes the specified S/MIME certificate configuration.

    Removes the S/MIME info identified by its ID from the specified
    'Send as' alias configuration.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        send_as_email (str): The email address of the 'Send as' alias from which
                       to delete the S/MIME info. Defaults to ''.
        id (str): The ID of the S/MIME info to delete. Defaults to ''.

    Returns:
        None.

    Raises:
        KeyError: If the specified `userId` does not exist in the database.
    """
    _ensure_user(userId)
    send_as_entry = DB["users"][userId]["settings"]["sendAs"].get(send_as_email)
    if send_as_entry:
        smime_dict = send_as_entry.setdefault("smimeInfo", {})
        smime_dict.pop(id, None)


def setDefault(
    userId: str = "me", send_as_email: str = "", id: str = ""
) -> Optional[Dict[str, Any]]:
    """Sets the specified S/MIME certificate as the default for the alias.

    Marks the S/MIME info identified by `id` as the default configuration
    for the given 'Send as' alias, removing the default status from any other
    S/MIME configurations for that alias.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        send_as_email (str): The email address of the 'Send as' alias. Defaults to ''.
        id (str): The ID of the S/MIME info to set as default. Defaults to ''.

    Returns:
        Optional[Dict[str, Any]]: A dictionary representing the S/MIME info resource that was set as
        default, if found. Returns None if the 'Send as' alias or the
        specific S/MIME info ID is not found. The dictionary contains:
            - 'id' (str): The ID of the S/MIME info.
            - Other S/MIME properties as defined in the database.

    Raises:
        KeyError: If the specified `userId` does not exist in the database.
    """
    _ensure_user(userId)
    send_as_entry = DB["users"][userId]["settings"]["sendAs"].get(send_as_email)
    if not send_as_entry:
        return None
    smime_dict = send_as_entry.setdefault("smimeInfo", {})
    existing = smime_dict.get(id)
    if not existing:
        return None
    for _, val in smime_dict.items():
        val.pop("default", None)
    existing["default"] = True
    return existing
