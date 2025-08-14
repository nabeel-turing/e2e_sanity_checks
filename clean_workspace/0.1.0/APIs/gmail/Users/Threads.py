# gmail/Users/Threads.py
import builtins

from typing import Optional, Dict, Any, List

from ..SimulationEngine.db import DB
from ..SimulationEngine.utils import _ensure_user
from . import Messages
from ..SimulationEngine.custom_errors import InvalidFormatValueError, ValidationError


def trash(userId: str = "me", id: str = "") -> Optional[Dict[str, Any]]:
    """Moves the specified thread to the trash.

    This operation marks the thread and all messages within it as trashed.
    It utilizes the `Messages.trash` function for each message in the thread.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        id (str): The ID of the thread to trash. Defaults to ''.

    Returns:
        Optional[Dict[str, Any]]: A dictionary representing the trashed thread resource if found,
        otherwise None. The dictionary contains:
            - 'id' (str): The thread ID
            - 'messageIds' (List[str]): List of message IDs in the thread
            - Other message properties as defined in the database.
        Returns None if the thread with the specified ID does not exist.

    Raises:
        TypeError: If userId or id is not a string.
        ValueError: If the specified userId does not exist in the database.
    """
    # Basic input validation
    if not isinstance(userId, str):
        raise TypeError(f"userId must be a string, got {type(userId).__name__}")
    if not isinstance(id, str):
        raise TypeError(f"id must be a string, got {type(id).__name__}")
    
    _ensure_user(userId)
    thr = DB["users"][userId]["threads"].get(id)
    if thr:
        for mid in thr.get("messageIds", []):
            Messages.trash(userId, mid)
    return thr


def untrash(userId: str = "me", id: str = "") -> Optional[Dict[str, Any]]:
    """Removes the specified thread from the trash.

    This operation restores the thread and all messages within it from the trash.
    It utilizes the `Messages.untrash` function for each message in the thread.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        id (str): The ID of the thread to untrash. Defaults to ''.

    Returns:
        Optional[Dict[str, Any]]: A dictionary representing the untrashed thread resource if found,
        otherwise None. The dictionary contains:
            - 'id' (str): The thread ID
            - 'messageIds' (List[str]): List of message IDs in the thread
            - Other message properties as defined in the database.
        Returns None if the thread with the specified ID does not exist.

    Raises:
        TypeError: If userId or id is not a string.
        ValueError: If the specified userId does not exist in the database.
    """
    # Basic input validation
    if not isinstance(userId, str):
        raise TypeError(f"userId must be a string, got {type(userId).__name__}")
    if not isinstance(id, str):
        raise TypeError(f"id must be a string, got {type(id).__name__}")
    
    _ensure_user(userId)
    thr = DB["users"][userId]["threads"].get(id)
    if thr:
        for mid in thr.get("messageIds", []):
            Messages.untrash(userId, mid)
    return thr


def delete(userId: str = "me", id: str = "") -> None:
    """Immediately and permanently deletes the specified thread.

    This operation cannot be undone. It removes the thread and all associated
    messages from the user's mailbox permanently.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        id (str): The ID of the thread to delete. Defaults to ''.

    Returns:
        None: This method does not return any content.

    Raises:
        TypeError: If `userId` or `id` is not a string.
        ValidationError: If `userId` or `id` is empty or contains whitespace.
        KeyError: If the specified `userId` does not exist in the database.
    """
    # Input validation
    if not isinstance(userId, str):
        raise TypeError(f"userId must be a string, but got {type(userId).__name__}.")
    if not isinstance(id, str):
        raise TypeError(f"id must be a string, but got {type(id).__name__}.")
    if not userId:
        raise ValidationError("Argument 'userId' cannot be empty.")
    if not userId.strip():
        raise ValidationError("Argument 'userId' cannot have only whitespace.")
    if " " in userId:
        raise ValidationError("Argument 'userId' cannot have whitespace.")
    if " " in id:
        raise ValidationError("Argument 'id' cannot have whitespace.")
    
    _ensure_user(userId)
    thr = DB["users"][userId]["threads"].pop(id, None)
    if thr:
        for mid in thr.get("messageIds", []):
            DB["users"][userId]["messages"].pop(mid, None)
    return None

def get(
    userId: str = "me",
    id: str = "",
    format: str = "full",
    metadata_headers: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    """Gets the specified thread.

    Retrieves the details of a specific thread identified by its ID.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        id (str): The ID of the thread to retrieve. Defaults to ''.
        format (str): The format to return the messages in. Accepted values are:
                - 'full': Returns the full message data including body and all fields
                - 'metadata': Returns message ID, labels, and headers (either specified or default)
                - 'minimal': Returns only message ID and labels
                - 'raw': Returns the full message data (same as 'full' in this implementation)
                Defaults to 'full'.
        metadata_headers (Optional[List[str]]): A list of headers to include when format is set
                          to 'metadata'. If None, includes default headers (Subject, From, To, Date).
                          Case-insensitive matching is used for common headers. Defaults to None.

    Returns:
        Optional[Dict[str, Any]]: A dictionary representing the thread resource if found, otherwise None.
        The dictionary contains:
            - 'id' (str): The thread ID
            - 'snippet' (str): A short part of the message text (truncated to 100 characters)
            - 'historyId' (str): The ID of the last history record that modified this thread
            - 'messages' (List[Dict]): List of messages in the thread, filtered according to format
            - 'messageIds' (List[str]): List of message IDs in the thread
        Returns None if the thread with the specified ID does not exist.

    Raises:
        TypeError: If `userId`, `id`, or `format` is not a string.
                   If `metadata_headers` is provided and is not a list.
                   If `metadata_headers` is a list but contains non-string elements.
        InvalidFormatValueError: If `format` is not one of 'full', 'metadata', 'minimal', 'raw'.
        ValueError: If the specified `userId` does not exist in the database (propagated from internal logic).
    """
    # --- Input Validation Start ---
    if not isinstance(userId, str):
        raise TypeError(f"Argument 'userId' must be a string, but got {type(userId).__name__}.")
    if not isinstance(id, str):
        raise TypeError(f"Argument 'id' must be a string, but got {type(id).__name__}.")
    if not isinstance(format, str):
        raise TypeError(f"Argument 'format' must be a string, but got {type(format).__name__}.")

    allowed_formats = ['full', 'metadata', 'minimal', 'raw']
    if format not in allowed_formats:
        raise InvalidFormatValueError(
            f"Argument 'format' must be one of {allowed_formats}, but got '{format}'."
        )

    if metadata_headers is not None:
        if not isinstance(metadata_headers, builtins.list):
            raise TypeError(
                f"Argument 'metadata_headers' must be a list of strings or None, but got {type(metadata_headers).__name__}."
            )
        for header in metadata_headers:
            if not isinstance(header, str):
                raise TypeError(
                    f"All elements in 'metadata_headers' must be strings, but found element of type {type(header).__name__}."
                )
    # --- Input Validation End ---

    _ensure_user(userId)
    thread = DB["users"][userId]["threads"].get(id)
    if not thread:
        return None

    # Get the thread's messages
    messages = []
    for msg_id in thread.get("messageIds", []):
        msg = DB["users"][userId]["messages"].get(msg_id)
        if msg:
            if format == "minimal":
                # Only include ID and labels
                messages.append({"id": msg["id"], "labelIds": [lbl.upper() for lbl in msg.get("labelIds", [])]})
            elif format == "metadata":
                # Include ID, labels, and headers
                msg_data = {
                    "id": msg["id"],
                    "labelIds": [lbl.upper() for lbl in msg.get("labelIds", [])],
                    "headers": {},
                }
                if metadata_headers:
                    # Only include specified headers
                    for header_name_requested in metadata_headers: # Renamed to avoid conflict
                        # Case-insensitive matching for common headers
                        if header_name_requested.lower() == "subject":
                            msg_data["headers"]["Subject"] = msg.get("subject", "")
                        elif header_name_requested.lower() == "from":
                            msg_data["headers"]["From"] = msg.get("sender", "")
                        elif header_name_requested.lower() == "to":
                            msg_data["headers"]["To"] = msg.get("recipient", "")
                        elif header_name_requested.lower() == "date":
                            msg_data["headers"]["Date"] = msg.get("date", "")
                        # For other headers, one might need a more generic mapping or direct key access if keys match
                else:
                    # Include all headers if no specific ones requested
                    msg_data["headers"] = {
                        "Subject": msg.get("subject", ""),
                        "From": msg.get("sender", ""),
                        "To": msg.get("recipient", ""),
                        "Date": msg.get("date", ""),
                    }
                messages.append(msg_data)
            else:  # format == 'full' or 'raw'
                # Include full message data
                messages.append(msg)

    # Get the first message's snippet
    snippet = ""
    if messages:
        first_msg = messages[0] # Assuming messages are ordered
        if format in ["full", "raw"]: # 'raw' likely also contains full body
             snippet = str(first_msg.get("body", ""))[:100]
        elif format == "metadata": # For metadata, snippet might not be directly available in simplified msg_data
            # Re-fetch or use original msg if snippet needed and not in msg_data
            original_first_msg = DB["users"][userId]["messages"].get(thread.get("messageIds", [])[0])
            if original_first_msg:
                snippet = str(original_first_msg.get("body", ""))[:100]


    return {
        "id": thread["id"],
        "snippet": snippet,
        "historyId": DB["users"][userId]["profile"].get("historyId", ""),
        "messages": messages,
        "messageIds": thread.get("messageIds", []), # Ensure 'messageIds' is present
    }

def list(
    userId: str = "me",
    max_results: int = 100,
    page_token: str = "",
    q: str = "",
    labelIds: Optional[List[str]] = None,
    include_spam_trash: bool = False,
) -> Dict[str, Any]:
    """Lists the threads in the user's mailbox.

    Retrieves a list of threads matching the specified query criteria.
    Note: Query parameters (`q`, `labelIds`, `include_spam_trash`, `page_token`)
    are included for API compatibility but are not fully implemented.
    The filtering based on these parameters is not performed.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        max_results (int): Maximum number of threads to return. Defaults to 100.
                     Actual results might be fewer if less threads exist. The maximum allowed value is 500.
        page_token (str): Page token to retrieve a specific page of results.
                    Defaults to ''. (Currently ignored).
        q (str): Only return threads matching the specified query. Supports the same
           query format as the Gmail search box. Defaults to ''. (Currently ignored).
        labelIds (Optional[List[str]]): Only return threads with labels that match all of the specified
                  label IDs in uppercase. Defaults to None. (Currently ignored).
        include_spam_trash (bool): Include threads from SPAM and TRASH in the results.
                            Defaults to False. (Currently ignored).

    Returns:
        Dict[str, Any]: A dictionary containing:
            - 'threads' (List[Dict[str, str]]): List of thread resources, each containing:
                - 'id' (str): The thread ID
            - 'nextPageToken' (Optional[str]): Token for retrieving the next page of results.
                Currently always None.
            - 'resultSizeEstimate' (int): Estimated total number of threads matching the query.

    Raises:
        TypeError: If any of the arguments have incorrect types:
            - userId must be a string
            - max_results must be an integer
            - page_token must be a string
            - q must be a string
            - labelIds must be None or a list of strings
            - includeSpamTrash must be a boolean
        ValueError: If max_results is greater than 500
        KeyError: If the specified userId does not exist in the database
    """
    if not isinstance(userId, str):
        raise TypeError(f"Argument 'userId' must be a string, but got {type(userId).__name__}.")
    if not isinstance(max_results, int):
        raise TypeError(f"Argument 'max_results' must be an integer, but got {type(max_results).__name__}.")
    if not isinstance(page_token, str):
        raise TypeError(f"Argument 'page_token' must be a string, but got {type(page_token).__name__}.")
    if not isinstance(q, str):
        raise TypeError(f"Argument 'q' must be a string, but got {type(q).__name__}.")
    if labelIds is not None:
        if not isinstance(labelIds, builtins.list):
            raise TypeError(f"Argument 'labelIds' must be a list of strings or None, but got {type(labelIds).__name__}.")
        for label_id in labelIds:
            if not isinstance(label_id, str):
                raise TypeError(f"All elements in 'labelIds' must be strings, but found element of type {type(label_id).__name__}.")
    if not isinstance(include_spam_trash, bool):
        raise TypeError(f"Argument 'include_spam_trash' must be a boolean, but got {type(include_spam_trash).__name__}.")

    if max_results > 500:
        raise ValueError(f"Argument 'max_results' must be less than or equal to 500, but got {max_results}.")
    
    _ensure_user(userId)

    messages_response = Messages.list(userId, max_results, q, labelIds, include_spam_trash)
    threads_list = []
    threads_map = {}
    for message in messages_response["messages"]:
        thread_id = message["threadId"]
        if thread_id not in threads_map:
            threads_map[thread_id] = {"id": thread_id, "messages": [message["id"]]}
        else:
            threads_map[thread_id]["messages"].append(message["id"])

    threads_list = builtins.list(threads_map.values())

    return {
        "threads": threads_list[:max_results],
        "nextPageToken": None,
        "resultSizeEstimate": len(threads_list),
    }


def modify(
    userId: str = "me",
    id: str = "",
    addLabelIds: Optional[List[str]] = None,
    removeLabelIds: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    """Modifies the labels applied to the specified thread.

    Adds or removes labels from all messages within the specified thread.
    It utilizes the `Messages.modify` function for each message in the thread.

    Args:
        userId (str): The user's email address. The special value 'me' can be used to indicate the authenticated user.
        id (str): The ID of the thread to modify.
        addLabelIds (Optional[List[str]]): A list of IDs of labels to add to this message. You can add up to 100 labels with each update.
        removeLabelIds (Optional[List[str]]): A list of IDs of labels to remove from this message. You can remove up to 100 labels with each update.

    Returns:
        Optional[Dict[str, Any]]: A dictionary representing the modified thread resource if found,
        otherwise None. The dictionary contains:
            - 'id' (str): The thread ID
            - 'messageIds' (List[str]): List of message IDs in the thread

    Raises:
        TypeError: If any of the arguments have incorrect types:
            - userId must be a string
            - id must be a string
            - addLabelIds must be None or a list of strings
            - removeLabelIds must be None or a list of strings
        ValueError: If either addLabelIds or removeLabelIds contains more than 100 elements
        KeyError: If either:
            - The specified userId does not exist in the database
            - The specified thread id does not exist for the given user
    """

    # --- Input Validation Start ---
    if not isinstance(userId, str):
        raise TypeError(f"Argument 'userId' must be a string, but got {type(userId).__name__}.")
    if not isinstance(id, str):
        raise TypeError(f"Argument 'id' must be a string, but got {type(id).__name__}.")
    if addLabelIds is not None:
        if not isinstance(addLabelIds, builtins.list):
            raise TypeError(f"Argument 'addLabelIds' must be a list of strings or None, but got {type(addLabelIds).__name__}.") 
        for label_id in addLabelIds:
            if not isinstance(label_id, str):
                raise TypeError(f"All elements in 'addLabelIds' must be strings, but found element of type {type(label_id).__name__}.")
    if removeLabelIds is not None:
        if not isinstance(removeLabelIds, builtins.list):
            raise TypeError(f"Argument 'removeLabelIds' must be a list of strings or None, but got {type(removeLabelIds).__name__}.")
        for label_id in removeLabelIds:
            if not isinstance(label_id, str):
                raise TypeError(f"All elements in 'removeLabelIds' must be strings, but found element of type {type(label_id).__name__}.")
        
    if addLabelIds is not None and len(addLabelIds) > 100:  
        raise ValueError("Argument 'addLabelIds' cannot have more than 100 elements.")
    if removeLabelIds is not None and len(removeLabelIds) > 100:
        raise ValueError("Argument 'removeLabelIds' cannot have more than 100 elements.")
    
    # --- Input Validation End ---  

    _ensure_user(userId)
    thr = DB.get("users", {}).get(userId, {}).get("threads", {}).get(id)
    if not thr:
        raise KeyError(f"Thread with ID {id} not available for user {userId}.")
    
    addLabelIds = [lbl.upper() for lbl in addLabelIds] if addLabelIds else None
    removeLabelIds = [lbl.upper() for lbl in removeLabelIds] if removeLabelIds else None
    for mid in thr.get("messageIds", []):
        Messages.modify(userId, mid, addLabelIds, removeLabelIds)
    return thr