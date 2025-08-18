# APIs/jira/UserApi.py
from pydantic import ValidationError
from .SimulationEngine.custom_errors import MissingUserIdentifierError, UserNotFoundError
from .SimulationEngine.db import DB
from .SimulationEngine.models import UserCreationPayload
from typing import Any, Dict, List, Optional
import warnings
import uuid


def get_user(username: Optional[str] = None, account_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get a user by username or account_id(key).

    This function retrieves a single user from the database. It prioritizes
    the `account_id` if both identifiers are provided. If no user is found
    matching the given criteria, it will raise a `UserNotFoundError`.

    Args:
        username (Optional[str]): The username of the user to retrieve. This is deprecated.
        account_id (Optional[str]): The account ID (key) of the user to retrieve.

    Returns:
        Dict[str, Any]: The user object dictionary if a user is found. It contains:
            - name (str): The username of the user.
            - key (str): The unique identifier (account ID) for the user.
            - active (bool): The user's active status.
            - emailAddress (str): The user's primary email address.
            - displayName (str): The user's display name.
            - profile (dict): A dictionary containing `bio` and `joined` date.
            - groups (list): A list of groups the user belongs to.
            - drafts (list): A list of the user's draft messages.
            - messages (list): A list of the user's messages.
            - threads (list): A list of the user's message threads.
            - labels (list): A list of labels associated with the user.
            - settings (dict): A dictionary of user-specific settings,
              including `theme` and `notifications`.
            - history (list): A list of the user's activity history.
            - watch (list): A list of items the user is watching.
            - sendAs (list): A list of aliases the user can send mail as.
    Raises:
        TypeError: If username is provided and is not a string.
        TypeError: If account_id is provided and is not a string.
        MissingUserIdentifierError: If neither username nor account_id is provided.
        UserNotFoundError: If the user is not found.
    """
    # Input Validation
    if username is not None and not isinstance(username, str):
        raise TypeError("username must be a string if provided.")

    if account_id is not None and not isinstance(account_id, str):
        raise TypeError("account_id must be a string if provided.")

    if username is None and account_id is None:
        raise MissingUserIdentifierError("Either username or account_id must be provided.")

    if account_id:
        user = DB.get("users", {}).get(account_id)
        if user:
            return user

    if username:
        warnings.warn("username is deprecated. Use account_id instead.", DeprecationWarning)
        users_map = DB.get("users", {})
        for u in users_map.values():
            if u.get("name") == username:
                return u

    raise UserNotFoundError("User not found.")


def create_user(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new user with all required fields.

    This function validates the input payload to ensure it contains the necessary
    user details and that the email is not already in use. On success, it
    populates a user object with a mix of provided data and sensible defaults.

    Args:
        payload (Dict[str, Any]): A dictionary containing the user's details.
            - name (str): The username for the new user. (Required)
            - emailAddress (str): The user's primary email address. (Required)
            - displayName (str): The name to display in the UI. (Required)
            - profile (Optional[Dict[str, Any]]): A dictionary for profile info.
                - bio (str, optional): The user's biography.
                - joined (str, optional): The date the user joined.
            - groups (Optional[List[str]]): A list of group names.
            - drafts (Optional[List[Dict[str, Any]]]): A list of draft objects.
                - Each object is a dict with the keys:
                    - id (str): The unique ID of the draft.
                    - subject (str): The subject of the draft.
                    - body (str): The content of the draft.
                    - timestamp (str): The creation timestamp of the draft.
            - messages (Optional[List[Dict[str, Any]]]): A list of message objects.
                - Each object is a dict with the keys:
                    - id (str): The unique ID of the message.
                    - from (str): The sender's email address.
                    - to (str): The recipient's email address.
                    - subject (str): The subject of the message.
                    - timestamp (str): The timestamp of the message.
            - threads (Optional[List[Dict[str, Any]]]): A list of thread objects.
                - Each object is a dict with the keys:
                    - id (str): The unique ID of the thread.
                    - messageIds (List[str]): A list of message IDs in the thread.
            - labels (Optional[List[str]]): A list of label strings.
            - settings (Optional[Dict[str, Any]]): A dictionary for user settings.
                - theme (str, optional): The user's theme preference.
                - notifications (bool, optional): The user's notification preference.
            - history (Optional[List[Dict[str, Any]]]): A list of history event objects.
                - Each object is a dict with the keys:
                    - action (str): The action performed.
                    - timestamp (str): The timestamp of the action.
            - watch (Optional[List[str]]): A list of watched item IDs.
            - sendAs (Optional[List[Dict[str, Any]]]): A list of alias objects.
                - Each object is a dict with the keys:
                    - alias (str): The email alias.
                    - default (bool): Whether this is the default alias.

    Returns:
        Dict[str, Any]: A dictionary containing a 'created' flag and the new 'user'
            object. The user object's structure is detailed below.

            - created (bool): Always True on success.
            - user (Dict[str, Any]): The newly created user object, containing:
                - name (str): The username of the user.
                - key (str): The unique identifier for the user.
                - active (bool): User status, always True on creation.
                - emailAddress (str): The user's primary email address.
                - displayName (str): The user's display name.
                - profile (Dict[str, Any]): Contains user profile information.
                    - bio (str): The user's biography.
                    - joined (str): The date the user joined.
                - groups (List[str]): A list of group names the user belongs to.
                - drafts (List[Dict[str, Any]]): A list of the user's draft message objects. Each object is a dict with the keys:
                    - id (str): The unique ID of the draft.
                    - subject (str): The subject of the draft.
                    - body (str): The content of the draft.
                    - timestamp (str): The creation timestamp of the draft.
                - messages (List[Dict[str, Any]]): A list of the user's message objects. Each object is a dict with the keys:
                    - id (str): The unique ID of the message.
                    - from (str): The sender's email address.
                    - to (str): The recipient's email address.
                    - subject (str): The subject of the message.
                    - timestamp (str): The timestamp of the message.
                - threads (List[Dict[str, Any]]): A list of the user's message thread objects. Each object is a dict with the keys:
                    - id (str): The unique ID of the thread.
                    - messageIds (List[str]): A list of message IDs belonging to the thread.
                - labels (List[str]): A list of strings representing labels.
                - settings (Dict[str, Any]): User-specific settings.
                    - theme (str): The user's selected theme (e.g., 'light').
                    - notifications (bool): The user's notification preference.
                - history (List[Dict[str, Any]]): A list of the user's activity history objects. Each object is a dict with the keys:
                    - action (str): The action performed (e.g., 'login').
                    - timestamp (str): The timestamp of the action.
                - watch (List[str]): A list of strings representing watched item IDs.
                - sendAs (List[Dict[str, Any]]): A list of alias objects the user can send mail as. Each object is a dict with the keys:
                    - alias (str): The email alias.
                    - default (bool): Whether this is the default alias.

    Raises:
        TypeError: If the `payload` argument is not a dictionary.
        ValidationError: If the payload fails validation (e.g.,
                                  missing required fields, invalid email format).
    """
    # --- Input Validation ---
    if not isinstance(payload, dict):
        raise TypeError(f"Expected payload to be a dict, got {type(payload).__name__}")

    try:
        validated_payload = UserCreationPayload(**payload)
    except ValidationError as e:
        raise e
    # --- End Input Validation ---

    # Use validated fields from Pydantic model for defined attributes
    uname = validated_payload.name
    email = validated_payload.emailAddress # This is an EmailStr object, but behaves like a str
    display_name = validated_payload.displayName

    user_key = str(uuid.uuid4())
    while user_key in DB["users"]:
        user_key = str(uuid.uuid4())

    user_defaults = {
        "name": uname,
        "key": user_key,
        "active": True,
        "emailAddress": str(email), # Ensure it's a plain string if EmailStr causes issues downstream
        "displayName": display_name,
        "profile": {
            "bio": payload.get("profile", {}).get("bio", ""),
            "joined": payload.get("profile", {}).get("joined", ""),
        },
        "groups": payload.get("groups", []),
        "drafts": payload.get("drafts", []),
        "messages": payload.get("messages", []),
        "threads": payload.get("threads", []),
        "labels": payload.get("labels", []),
        "settings": {
            "theme": payload.get("settings", {}).get("theme", "light"),
            "notifications": payload.get("settings", {}).get("notifications", True),
        },
        "history": payload.get("history", []),
        "watch": payload.get("watch", []),
        "sendAs": payload.get("sendAs", []),
    }

    DB["users"][user_key] = user_defaults
    return {"created": True, "user": DB["users"][user_key]}

def delete_user(username: Optional[str] = None, key: Optional[str] = None) -> Dict[str, Any]:
    """
    Delete a user by username or key.

    Args:
        username (Optional[str]): The username of the user to delete.
        key (Optional[str]): The key of the user to delete.

    Returns:
        Dict[str, Any]: A dictionary containing the user's information.
            - deleted (str): The key of the user that was deleted.
    Raises:
        TypeError: If username or key is not a string.
        ValueError: If the user is not found or both username and key are not provided.
    """
    # input validation
    if username is not None and not isinstance(username, str):
        raise TypeError("username must be a string if provided.")
    if key is not None and not isinstance(key, str):
        raise TypeError("key must be a string if provided.")
    

    if username:
        for u in DB["users"].values():
            if u["name"] == username:
                key = u["key"]
                break
        else:
            raise ValueError("User not found.")
        
    if  key:
        if key not in DB["users"]:
            raise UserNotFoundError("User not found.")
        del DB["users"][key]
    return {"deleted": key}



def find_users(
    search_string: str,
    startAt: Optional[int] = 0,
    maxResults: Optional[int] = 50,
    includeActive: Optional[bool] = True,
    includeInactive: Optional[bool] = False,
) -> List[Dict[str, Any]]:
    """
    Finds users by a string search against their name, display name, and email.

    This function provides a general-purpose search for users and supports
    pagination and filtering by active status. The search is case-insensitive.

    Args:
        search_string (str): The search string to match against user fields name, display name, and email
        startAt (Optional[int]): The index of the first user to return. Defaults to 0.
        maxResults (Optional[int]): The maximum number of users to return. Defaults to 50 (maximum allowed value is 1000). 
                If you specify a value that is higher than 1000, your search results will be truncated.
        includeActive (Optional[bool]): If True, active users are included. Defaults to True.
        includeInactive (Optional[bool]): If True, inactive users are included. Defaults to False.

    Returns:
        List[Dict[str, Any]]: A list of user objects matching the criteria.
            Each user object contains:
            - name (str): The username of the user.
            - key (str): The unique identifier (account ID) for the user.
            - active (bool): The user's active status.
            - emailAddress (str): The user's primary email address.
            - displayName (str): The user's display name.
            - profile (Dict[str, Any]):
                - bio (str): The user's biography.
                - joined (str): The date the user joined.
            - groups (List[str]): A list of group names.
            - drafts (List[Dict[str, Any]]): A list of draft message objects.
                - id (str): The unique ID of the draft.
                - subject (str): The subject of the draft.
                - body (str): The content of the draft.
                - timestamp (str): The creation timestamp of the draft.
            - messages (List[Dict[str, Any]]): A list of message objects.
                - id (str): The unique ID of the message.
                - from (str): The sender's email address.
                - to (str): The recipient's email address.
                - subject (str): The subject of the message.
                - timestamp (str): The timestamp of the message.
            - threads (List[Dict[str, Any]]): A list of thread objects.
                - id (str): The unique ID of the thread.
                - messageIds (List[str]): A list of message IDs in the thread.
            - labels (List[str]): A list of label strings.
            - settings (Dict[str, Any]):
                - theme (str): The user's theme preference.
                - notifications (bool): The user's notification preference.
            - history (List[Dict[str, Any]]): A list of history event objects.
                - action (str): The action performed.
                - timestamp (str): The timestamp of the action.
            - watch (List[str]): A list of watched item IDs.
            - sendAs (List[Dict[str, Any]]): A list of alias objects.
                - alias (str): The email alias.
                - default (bool): Whether this is the default alias.

    Raises:
        TypeError: If 'username' is not a string,
                   'startAt' or 'maxResults' are not integers,
                   or 'includeActive' or 'includeInactive' are not booleans.
        ValueError: If 'username' is an empty string (after stripping whitespace),
                    'startAt' is negative,
                    or 'maxResults' is not a positive integer.
    """
    # --- Input Validation Start ---
    if not isinstance(search_string, str):
        raise TypeError("search_string must be a string.")
    if not search_string.strip():
        raise ValueError("search_string cannot be empty.")

    if not isinstance(startAt, int):
        raise TypeError("startAt must be an integer.")
    if startAt < 0:
        raise ValueError("startAt must be a non-negative integer.")

    if not isinstance(maxResults, int):
        raise TypeError("maxResults must be an integer.")
    if maxResults <= 0:
        raise ValueError("maxResults must be a positive integer.")

    if not isinstance(includeActive, bool):
        raise TypeError("includeActive must be a boolean.")
    if not isinstance(includeInactive, bool):
        raise TypeError("includeInactive must be a boolean.")
    # --- Input Validation End ---

    query_lower = search_string.lower()
    users = [
        user
        for user in DB["users"].values() # Assuming DB is a global or accessible dictionary
        if query_lower in user["name"].lower()
        or query_lower in user["emailAddress"].lower()
        or query_lower in user["displayName"].lower()
    ]
    # Filter based on active/inactive status
    
    # A user is included if their active status matches the corresponding flag.
    # This elegantly handles all four cases (active, inactive, both, or neither).
    filtered_users = [
        user for user in users
        if (user.get("active", True) and includeActive) or \
           (not user.get("active", True) and includeInactive)
    ]
    
    # Paging
    end_index = startAt + min(maxResults, 1000)
    paged_users = filtered_users[startAt:end_index]

    return paged_users