from common_utils.print_log import print_log
# gmail/Users/Messages/__init__.py
import builtins
import re
import shlex
import time
import base64

from datetime import datetime

from typing import Optional, List, Dict, Any

from pydantic import ValidationError

from ...SimulationEngine.db import DB
from ...SimulationEngine.utils import (
    _ensure_user,
    _next_counter,
    _parse_query_string,
    label_filter,
    search_ids,
)
from ...SimulationEngine.models import (
    GetFunctionArgsModel,
    MessageSendPayloadModel,
    MessagePayloadModel,
)
from ...SimulationEngine.attachment_utils import (
    get_attachment_metadata_only,
    parse_mime_message,
    create_mime_message_with_attachments,
)
from ...SimulationEngine.attachment_manager import cleanup_attachments_for_message
from ...SimulationEngine import custom_errors
from gmail.SimulationEngine.search_engine import search_engine_manager

def trash(userId: str = 'me', id: str = '') -> Optional[Dict[str, Any]]:
    """Moves the specified message to the trash.

    Adds the 'TRASH' label to the message identified by the given ID.
    If the message already has the 'TRASH' label, it remains unchanged.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        id (str): The ID of the message to trash. Defaults to ''.

    Returns:
        Optional[Dict[str, Any]]: A dictionary representing the modified message resource if found,
        otherwise None. The dictionary contains:
            - id (str): The ID of the message.
            - threadId (str): The ID of the thread the message belongs to.
            - raw (str): The raw content of the message.
            - sender (str): The email address of the sender.
            - recipient (str): The email address of the recipient.
            - subject (str): The subject of the message.
            - body (str): The body of the message.
            - date (str): The date the message was sent.
            - internalDate (str): The internal date of the message.
            - isRead (bool): Whether the message has been read.
            - attachment (List[Dict[str, str]]): A list of attachments (dictionaries) with key:
                - filename (str): The name of the attachment.
            - labelIds (List[str]): A list of labels applied to the message.

    Raises:
        TypeError: If the specified `userId` or `id` is not a string.
        ValidationError: If the specified `userId` or `id` is not a string, or if the specified `userId` does not exist in the database (propagated from _ensure_user).
    """
    # Input validation
    if not isinstance(userId, str):
        raise TypeError(f"Argument 'userId' must be a string, got {type(userId).__name__}")
    if not isinstance(id, str):
        raise TypeError(f"Argument 'id' must be a string, got {type(id).__name__}")
    if not userId:
        raise custom_errors.ValidationError("userId cannot be empty")
    if not id:
        raise custom_errors.ValidationError("id cannot be empty")
    if not userId.strip():
        raise custom_errors.ValidationError("userId cannot have only whitespace")
    if not id.strip():
        raise custom_errors.ValidationError("id cannot have only whitespace")
    if " " in userId:
        raise custom_errors.ValidationError("userId cannot have whitespace")
    if " " in id:
        raise custom_errors.ValidationError("id cannot have whitespace")

    # Core function logic
    _ensure_user(userId)
    msg = DB['users'][userId]['messages'].get(id)
    if msg:
        labels = msg.get('labelIds', [])
        if 'TRASH' not in labels:
            labels.append('TRASH')
        msg['labelIds'] = labels
    return msg


def untrash(userId: str = "me", id: str = "") -> Optional[Dict[str, Any]]:
    """Removes the specified message from the trash.

    Removes the 'TRASH' label (uppercase) from the message.
    If the message does not have 'TRASH', it remains unchanged.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        id (str): The ID of the message to untrash. Defaults to ''.

    Returns:
        Optional[Dict[str, Any]]: A dictionary representing the modified message resource if found,
        otherwise None. The dictionary typically contains:
            - id (str): The ID of the message.
            - threadId (str): The ID of the thread the message belongs to.
            - raw (str): The raw content of the message.
            - sender (str): The email address of the sender.
            - recipient (str): The email address of the recipient.
            - subject (str): The subject of the message.
            - body (str): The body of the message.
            - date (str): The date the message was sent.
            - internalDate (str): The internal date of the message.
            - isRead (bool): Whether the message has been read.
            - attachment (List[Dict[str, str]]): A list of attachments (dictionaries) with key:
                - filename (str): The name of the attachment.
            - labelIds (List[str]): A list of labels applied to the message.

    Raises:
        TypeError: If `userId` or `id` is not a string.
        ValidationError: If the specified `userId` or `id` is not a string, or if the specified `userId` does not exist in the database (propagated from _ensure_user).
    """
    # --- Input Validation ---
    if not isinstance(userId, str):
        raise TypeError(f"Argument 'userId' must be a string, got {type(userId).__name__}")
    if not isinstance(id, str):
        raise TypeError(f"Argument 'id' must be a string, got {type(id).__name__}")
    if not userId:
        raise custom_errors.ValidationError("Argument 'userId' cannot be empty.")
    if not userId.strip():
        raise custom_errors.ValidationError("Argument 'userId' cannot have only whitespace.")
    if " " in userId:
        raise custom_errors.ValidationError("Argument 'userId' cannot have whitespace.")
    if " " in id:
        raise custom_errors.ValidationError("Argument 'id' cannot have whitespace.")
    # --- End of Input Validation ---

    # --- Original Core Logic (preserved) ---
    # These globals (DB, _ensure_user) are assumed to be available in the execution environment.
    # Their definitions are not part of this refactored function's code.
    _ensure_user(userId) # This call can raise ValueError, as documented.
    
    # Ensure DB and path to messages exist before trying to access, to prevent NameError/KeyError
    # This is a defensive check for the core logic to run in isolation if DB is not fully populated.
    # In a real scenario, _ensure_user might also ensure DB["users"][userId] structure.
    if "users" not in DB or userId not in DB["users"] or "messages" not in DB["users"][userId]:
        # This situation might be handled by _ensure_user or imply userId doesn't exist,
        # leading to KeyError from _ensure_user. If _ensure_user passes but this path is missing,
        # it's an inconsistent state. For now, assume _ensure_user handles user existence.
        # If messages are not found for a valid user, it means no such message id.
        return None

    msg = DB["users"][userId]["messages"].get(id)
    if msg:
        labels = msg.setdefault("labelIds", [])
        # Case-insensitively filter out the 'TRASH' label, preserving the case of all other labels.
        msg["labelIds"] = [label for label in labels if label.upper() != "TRASH"]
    return msg

  
def delete(userId: str = "me", id: str = "") -> Optional[Dict[str, Any]]:
    """Immediately and permanently deletes the specified message.

    Removes the message identified by the given ID from the user's mailbox.
    This operation cannot be undone. Also cleans up any attachments that
    are no longer referenced after the message deletion.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        id (str): The ID of the message to delete. Defaults to ''.

    Returns:
        Optional[Dict[str, Any]]: The dictionary representing the deleted message resource if it existed,
        otherwise None. The dictionary contains:
            - id (str): The ID of the message.
            - threadId (str): The ID of the thread the message belongs to.
            - raw (str): The raw content of the message.
            - sender (str): The email address of the sender.
            - recipient (str): The email address of the recipient.
            - subject (str): The subject of the message.
            - body (str): The body of the message.
            - date (str): The date the message was sent.
            - internalDate (str): The internal date of the message.
            - isRead (bool): Whether the message has been read.
            - attachment (List[Dict[str, str]]): A list of attachments (dictionaries) with key:
                - filename (str): The name of the attachment.
            - labelIds (List[str]): A list of labels applied to the message.

    Raises:
        TypeError: If `userId` or `id` is not a string.
        ValidationError: If the specified `userId` or `id` is not a string, or if the specified `userId` does not exist in the database (propagated from _ensure_user).
    """
    # Input validation
    if not isinstance(userId, str):
        raise TypeError(f"Argument 'userId' must be a string, got {type(userId).__name__}")
    if not isinstance(id, str):
        raise TypeError(f"Argument 'id' must be a string, got {type(id).__name__}")
    if not userId:
        raise custom_errors.ValidationError("Argument 'userId' cannot be empty.")
    if not userId.strip():
        raise custom_errors.ValidationError("Argument 'userId' cannot have only whitespace.")
    if " " in userId:
        raise custom_errors.ValidationError("Argument 'userId' cannot have whitespace.")
    if " " in id:
        raise custom_errors.ValidationError("Argument 'id' cannot have whitespace.")
    
    # Core function logic
    _ensure_user(userId)
    
    # Clean up attachments before deleting message
    cleanup_attachments_for_message(userId, id)
    
    # Delete the message
    msg = DB["users"][userId]["messages"].pop(id, None)
    return msg


def batchDelete(userId: str = "me", ids: Optional[List[str]] = None) -> None:
    """Deletes many messages simultaneously.

    Permanently deletes all messages identified by the IDs in the provided list.
    Also cleans up any attachments that are no longer referenced after the
    message deletions.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        ids (Optional[List[str]]): A list of message IDs to delete. Defaults to None.

    Returns:
        None.

    Raises:
        TypeError: If `userId` is not a string or `id` is not a list of strings.
        ValidationError: If `userId` or any id in the `ids` list is empty or contains whitespace.
    """
    # --- Input Validation ---
    if not isinstance(userId, str):
        raise TypeError(f"Argument 'userId' must be a string, got {type(userId).__name__}")
    if not userId.strip():
        raise custom_errors.ValidationError("Argument 'userId' cannot have only whitespace.")
    if " " in userId:
        raise custom_errors.ValidationError("Argument 'userId' cannot have whitespace.")
    if not isinstance(ids, List):
        raise TypeError(f"ids must be a list, got {type(ids).__name__}")
    if ids is None:
        ids = []    
    for mid in ids:
        if not isinstance(mid, str):
            raise TypeError(f"Argument 'id' must be a string, got {type(mid).__name__}")
        if " " in mid:
            raise custom_errors.ValidationError("Argument 'id' cannot have whitespace.")
    # --- End of Input Validation ---
    
    _ensure_user(userId)
    
    # Clean up attachments for each message before deleting
    for mid in ids:
        cleanup_attachments_for_message(userId, mid)
        DB["users"][userId]["messages"].pop(mid, None)
    return None

def import_(
    userId: str = "me",
    msg: Optional[Dict[str, Any]] = None,
    internal_date_source: str = "dateHeader",
    never_mark_spam: bool = False,
    process_for_calendar: bool = False,
    deleted: bool = False,
) -> Dict[str, Any]:
    """Imports a message into the mailbox, applying specified labels.

    Creates a new message entry in the database with a generated ID.
    Primarily uses the `raw` content if provided in `msg`. Adds the 'DELETED'
    label if the `deleted` flag is True.
    Note: `internal_date_source`, `never_mark_spam`, and `process_for_calendar`
    are included for API compatibility but are ignored in this implementation.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        msg (Optional[Dict[str, Any]]): An optional dictionary containing the message data with keys:
            - 'raw' (str): Raw message content.
            - Other optional message properties.
        internal_date_source (str): Specifies how to determine the internal date.
                              Defaults to 'dateHeader'. (Currently ignored).
        never_mark_spam (bool): Whether to prevent the message from being marked as spam.
                         Defaults to False. (Currently ignored).
        process_for_calendar (bool): Whether to process calendar invitations.
                              Defaults to False. (Currently ignored).
        deleted (bool): Mark the imported message as deleted. Defaults to False.

    Returns:
        Dict[str, Any]: A dictionary representing the newly imported message resource with keys:
            - 'id' (str): Generated message ID.
            - 'raw' (str): Raw message content.
            - 'labelIds' (List[str]): List of labels applied to the message in uppercase. 
            - 'internalDate' (str): Internal date of the message.

    Raises:
        KeyError: If the specified `userId` does not exist in the database.
    """
    _ensure_user(userId)
    message_id_num = _next_counter("message")
    message_id = f"msg_{message_id_num}"
    
    processed_label_set = set()
    if msg and "labelIds" in msg:
        for lbl in msg.get("labelIds", []):
            if isinstance(lbl, str): # Ensure label is a string
                processed_label_set.add(lbl.upper())

    if deleted:
        processed_label_set.add("DELETED") # Ensure DELETED is uppercase

    new_msg = {
        "id": message_id,
        "raw": msg.get("raw", "") if msg else "",
        "labelIds": sorted(builtins.list(processed_label_set)),
        "internalDate": "123456789", # Consider making this dynamic or configurable
    }
    DB["users"][userId]["messages"][message_id] = new_msg
    return new_msg


def insert(
    userId: str = "me",
    msg: Optional[Dict[str, Any]] = None,
    internal_date_source: str = "receivedTime",
    deleted: bool = False,
) -> Dict[str, Any]:
    """Directly inserts a message into the mailbox.

    Similar to `import_`, but typically used for messages composed by the user
    (e.g., drafts). Creates a new message with generated ID and thread ID.
    Populates fields based on the `msg` dictionary. Adds 'INBOX' and 'UNREAD'
    labels by default, and 'DELETED' if the flag is set.
    
    Attachment size limits are enforced: individual attachments cannot exceed 25MB,
    and the total message size (including all attachments) cannot exceed 100MB.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        msg (Optional[Dict[str, Any]]): An optional dictionary containing the message data with keys:
            - 'threadId' (str): Thread ID for the message.
            - 'raw' (str): Raw message content. For messages with attachments, this should be a base64url-encoded RFC 2822 compliant MIME message created using create_mime_message_with_attachments().
            - 'sender' (str): Sender email address.
            - 'recipient' (str): Recipient email address.
            - 'subject' (str): Message subject.
            - 'body' (str): Message body.
            - 'date' (str): Message date.
            - 'internalDate' (str): Internal date of the message.
            - 'isRead' (bool): Whether the message has been read.
            - 'labelIds' (List[str]): List of labels to apply to the message in uppercase.
        internal_date_source (str): Determines how the message's `internalDate` is set if `internalDate` is not provided or is None in the `msg` payload.
                                 If `msg` contains a non-None `internalDate` field, that value is used directly (expected as a string Unix timestamp). Otherwise, this parameter applies:
                                 - 'receivedTime' (default): `internalDate` is set to the Unix timestamp of when the message is processed.
                                 - 'dateHeader': `internalDate` is derived from the `msg['date']` field. If `msg['date']` is missing or invalid, it defaults to the processing time.
                                 Defaults to 'receivedTime'.
        deleted (bool): Mark the inserted message as deleted. Defaults to False.

    Returns:
        Dict[str, Any]: A dictionary representing the newly inserted message resource with keys:
            - 'id' (str): Generated message ID.
            - 'threadId' (str): Thread ID for the message.
            - 'raw' (str): Raw message content.
            - 'sender' (str): Sender email address.
            - 'recipient' (str): Recipient email address.
            - 'subject' (str): Message subject.
            - 'body' (str): Message body.
            - 'date' (str): Message date.
            - 'internalDate' (str): The internal date of the message as a Unix timestamp in seconds (string format). This is taken from `msg['internalDate']` if provided and non-None; otherwise, it's determined based on `internal_date_source`.
            - 'isRead' (bool): Whether the message has been read.
            - 'labelIds' (List[str]): List of labels applied to the message in uppercase.
            - 'payload' (Dict[str, Any]): Message payload containing:
                - 'headers' (List[Dict[str, str]]): List of header dictionaries, each containing:
                    - 'name' (str): Header name ('From', 'To', 'Subject', or 'Date')
                    - 'value' (str): Header value
                - 'body' (Dict[str, str]): Message body containing:
                    - 'data' (str): The content of the message body.

    Raises:
        TypeError: If `userId` or `internal_date_source` is not a string,
                   if `deleted` is not a boolean, or if `msg` is provided but is not a dictionary.
        ValueError: If `internal_date_source` is not 'receivedTime' or 'dateHeader'.
                   If any attachment exceeds 25MB or total message size exceeds 100MB.
        pydantic.ValidationError: If `msg` is provided and does not conform to the MessagePayloadModel structure (e.g., incorrect types for fields like 'isRead', 'labelIds').
        KeyError: If the specified `userId` does not exist in the database (propagated from `_ensure_user`).
    """
    # --- Input Validation ---
    if not isinstance(userId, str):
        raise TypeError(f"Argument 'userId' must be a string, got {type(userId).__name__}")
    if not isinstance(internal_date_source, str):
        raise TypeError(f"internal_date_source must be a string, got {type(internal_date_source).__name__}")
    if internal_date_source not in ("receivedTime", "dateHeader"):
        raise ValueError(f"internal_date_source must be 'receivedTime' or 'dateHeader', got {internal_date_source!r}")
    if not isinstance(deleted, bool):
        raise TypeError(f"deleted must be a boolean, got {type(deleted).__name__}")

    msg_payload: Dict[str, Any]
    if msg is not None:
        if not isinstance(msg, dict):
            raise TypeError(f"msg must be a dictionary or None, got {type(msg).__name__}")
        try:
            validated_msg_model = MessagePayloadModel(**msg)
            # exclude_none=True ensures that fields explicitly set to None in input
            # or fields not provided (defaulting to None in model) are not in the dict.
            # This makes msg_payload closely resemble a dict where optional keys might be missing,
            # allowing .get(key, default_value) to work as in the original code.
            msg_payload = validated_msg_model.model_dump(exclude_none=True)

        except ValidationError as e:
            # Re-raise Pydantic's validation error.
            # Error messages will clearly indicate the validation failures.
            raise e
    else:
        msg_payload = {}

    # --- Original Core Logic (minor adjustment for internal_date_source validation) ---
    _ensure_user(userId) # This may raise KeyError, as per original docstring
    message_id_num = _next_counter("message")
    message_id = f"message-{message_id_num}"
    
    # If threadId is not in msg_payload (i.e., not in msg or was None),
    # .get() will return None. The f-string default is then used.
    # If Pydantic model had `threadId: Optional[str] = "some_default"`, and exclude_defaults=False,
    # then msg_payload.get("threadId") would be "some_default".
    # With `Optional[str]=None` and `exclude_none=True`, it's fine.
    thread_id = msg_payload.get("threadId") or f"thread-{message_id_num}" # Adjusted to handle None from .get() explicitly

    final_internal_date: str
    # The check for "internalDate" in msg_payload works fine.
    # If internalDate was None in Pydantic model (not provided or explicit null),
    # exclude_none=True means it won't be in msg_payload.
    if "internalDate" in msg_payload and msg_payload["internalDate"] is not None:
        # Pydantic ensures msg_payload["internalDate"] is a string if present and not None.
        final_internal_date = str(msg_payload["internalDate"])
    elif internal_date_source == "dateHeader":
        # Pydantic ensures msg_payload.get("date") is str or None.
        date_val_from_header = msg_payload.get("date", "") # Default to "" if key missing or value was None
        if date_val_from_header: # Ensure it's not an empty string
            try:
                # Attempt to parse ISO format, common for date strings.
                dt = datetime.fromisoformat(str(date_val_from_header).replace("Z", "+00:00"))
                final_internal_date = str(int(dt.timestamp()))
            except ValueError: # Catches parsing errors for non-ISO format dates
                final_internal_date = str(int(time.time())) # Fallback to current time
        else:
            final_internal_date = str(int(time.time())) # Fallback if date header is empty or not provided
    elif internal_date_source == "receivedTime":
        final_internal_date = str(int(time.time()))
    # The 'else' branch for invalid internal_date_source is removed here,
    # as internal_date_source is validated upfront. If execution reaches here,
    # internal_date_source is guaranteed to be 'dateHeader' or 'receivedTime'.

    processed_label_set = set()
    # Pydantic ensures msg_payload.get("labelIds") is List[str] or None.
    # If None (due to exclude_none=True or explicit null), .get("labelIds") is None.
    user_provided_label_ids = msg_payload.get("labelIds")
    if isinstance(user_provided_label_ids, builtins.list): # Handles if 'labelIds' was actually provided as a list
        for lbl in user_provided_label_ids:
            if isinstance(lbl, str): # Pydantic model should ensure elements are str, but defense in depth
                processed_label_set.add(lbl.upper())
    
    system_labels_that_exclude_inbox = {"SENT", "DRAFT", "TRASH"}
    has_exclusive_system_label = any(lbl.upper() in system_labels_that_exclude_inbox for lbl in processed_label_set)


    if "INBOX" not in processed_label_set and not has_exclusive_system_label:
        processed_label_set.add("INBOX")
    # Ensure "UNREAD" is added if not explicitly "READ" (isRead=True) or if isRead is not specified (defaulting to False)
    # Original code adds UNREAD by default, this is typically handled by label processing logic elsewhere or an initial label set.
    # The provided code does not explicitly add "UNREAD" based on "isRead" status here.
    # For now, following strictly the original label processing related to "INBOX" and system labels:
    elif "INBOX" in processed_label_set and has_exclusive_system_label:
        processed_label_set.discard("INBOX")
        
    if not msg_payload.get("isRead", False) and "UNREAD" not in processed_label_set : # Simplified: if message is not read, add UNREAD
         if not any(lbl.upper() == "DRAFT" for lbl in processed_label_set): # Do not add UNREAD to DRAFTS
            processed_label_set.add("UNREAD")


    if deleted:
        processed_label_set.add("DELETED")
        processed_label_set.discard("INBOX") # Usually, deleted messages are removed from INBOX
        processed_label_set.discard("UNREAD") # DELETED messages are implicitly not UNREAD in some views

    if "raw" not in msg_payload:
        msg_payload["raw"] = create_mime_message_with_attachments(
            to=msg_payload.get("recipient", ""),
            subject=msg_payload.get("subject", ""),
            body=msg_payload.get("body", ""),
            from_email=msg_payload.get("sender", ""),
        )

    # Parse MIME message if raw field is provided
    parsed_mime = None
    if "raw" in msg_payload and msg_payload["raw"]:
        try:
            parsed_mime = parse_mime_message(msg_payload["raw"])
        except Exception as e:
            print_log(f"Warning: MIME parsing failed: {e}")
            import traceback
            traceback.print_exc()
            # Still continue with message creation even if MIME parsing fails

    new_msg = {
        "id": message_id,
        "threadId": thread_id,
        "raw": msg_payload.get("raw", ""),
        "sender": msg_payload.get("sender", ""),
        "recipient": msg_payload.get("recipient", ""),
        "subject": msg_payload.get("subject", ""),
        "body": msg_payload.get("body", ""),
        "date": msg_payload.get("date", ""),
        "internalDate": final_internal_date,
        "isRead": msg_payload.get("isRead", False), # Pydantic model default is False, if key missing get returns False
        "labelIds": sorted(builtins.list(processed_label_set))
    }

    # message_body = base64.b64encode(msg_payload.get("body", "").encode('utf-8')).decode('utf-8')

    new_msg["payload"] = {
        "headers": [
            {"name": "From", "value": msg_payload.get("sender", "")},
            {"name": "To", "value": msg_payload.get("recipient", "")},
            {"name": "Subject", "value": msg_payload.get("subject", "")},
            {"name": "Date", "value": msg_payload.get("date", "")}
        ],
        "body": {
            "data": msg_payload.get("body", "")
        }
    }

    # Process parsed MIME structure if available
    if parsed_mime:
        new_msg["payload"] = parsed_mime["payload"]
        new_msg["headers"] = parsed_mime["headers"]
        
        # Extract headers for convenience
        header_dict = {h["name"].lower(): h["value"] for h in parsed_mime["headers"]}
        new_msg["sender"] = header_dict.get("from", "")
        new_msg["recipient"] = header_dict.get("to", "")
        new_msg["subject"] = header_dict.get("subject", "")
        
        # Extract body text from payload
        body_text = ""
        if "parts" in parsed_mime["payload"]:
            for part in parsed_mime["payload"]["parts"]:
                if part.get("mimeType", "").startswith("text/") and "data" in part.get("body", {}):
                    try:
                        import base64
                        body_text = base64.b64decode(part["body"]["data"]).decode('utf-8')
                        break
                    except:
                        pass
        elif "body" in parsed_mime["payload"] and "data" in parsed_mime["payload"]["body"]:
            try:
                import base64
                body_text = base64.b64decode(parsed_mime["payload"]["body"]["data"]).decode('utf-8')
            except:
                pass
        new_msg["body"] = body_text

    # Ensure DB structure exists (this would typically be handled by _ensure_user or higher level logic)
    if userId not in DB["users"]:
        DB["users"][userId] = {"messages": {}} # Simplified init
    elif "messages" not in DB["users"][userId]:
        DB["users"][userId]["messages"] = {}


    DB["users"][userId]["messages"][message_id] = new_msg
    return new_msg

def get(
    userId: str = "me",
    id: str = "",
    format: str = "full",
    metadata_headers: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    """Gets the specified message.

    Retrieves the message resource identified by the given ID. The response format
    can be customized using the format parameter.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        id (str): The ID of the message to retrieve. Defaults to ''.
        format (str): The format to return the message in. Must be one of:
                - 'minimal': Returns only email message ID and labels
                - 'full': Returns the full email message data with body content
                - 'raw': Returns the full email message data with raw field (RFC 2822 compliant and may include attachments (e.g., as multipart MIME))
                - 'metadata': Returns only email message ID, labels, and email headers
                Defaults to 'full'.
        metadata_headers (Optional[List[str]]): List of headers to include when format='metadata'.
                          All elements in the list must be strings. Defaults to None.

    Returns:
        Optional[Dict[str, Any]]: A dictionary representing the message resource if found, otherwise None.
        The dictionary structure varies based on the format parameter:

        For 'minimal' format:
            - 'id' (str): Message ID
            - 'labelIds' (List[str]): List of labels applied to the message in uppercase

        For 'metadata' format:
            - 'id' (str): Message ID
            - 'labelIds' (List[str]): List of labels applied to the message in uppercase
            - 'headers' (List[Dict[str, str]]): List of header dictionaries, each containing:
                - 'name' (str): Header name ('From', 'To', 'Subject', or 'Date')
                - 'value' (str): Header value

        For 'raw' format:
            - 'id' (str): Message ID
            - 'threadId' (str): Thread ID for the message
            - 'labelIds' (List[str]): List of labels applied to the message in uppercase
            - 'raw' (str): The entire message represented as a base64url-encoded string 
                          (RFC 4648 Section 5). The raw string must be RFC 2822 compliant and may include attachments
                          (e.g., as multipart MIME). 
            - 'internalDate' (str): Internal date of the message

        For 'full' format (default):
            - 'id' (str): Message ID
            - 'threadId' (str): Thread ID for the message
            - 'labelIds' (List[str]): List of labels applied to the message in uppercase
            - 'snippet' (str): First 100 characters of the message body
            - 'internalDate' (str): Internal date of the message
            - 'payload' (Dict[str, Any]): The parsed message payload containing:
                - 'mimeType' (str): The MIME type of the message.
                - 'headers' (List[Dict[str, str]]): List of message headers with 'name' and 'value'.
                - 'parts' (List[Dict[str, Any]]): List of message parts for multipart messages. Each part is a dictionary with the following structure:
                    - 'mimeType' (str): The MIME type of the part (e.g., 'text/plain', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'image/png').
                    - 'filename' (Optional[str]): The filename of the part if it is an attachment (e.g., 'requirements.docx', 'sample_image.png'). Omitted or empty for inline/plain text parts.
                    - 'body' (Dict[str, Any]): The message body data for the part, with possible keys:
                        - 'data' (Optional[str]): The base64url-encoded content of the part (present for inline/plain text parts).
                        - 'attachmentId' (Optional[str]): The ID of the attachment (present for attachments, e.g., 'att_msg4_001').
                        - 'size' (Optional[int]): The size of the attachment in bytes (present for attachments).
                - 'body' (Dict[str, Any]): The message body data.
                    - 'data' (str): The base64url-encoded content of the message body.
            - 'sizeEstimate' (int): Length of the message body
            - 'raw' (str): Raw message content (included for compatibility)

    Raises:
        ValidationError: If any of the input arguments fail validation:
            - If userId is not a string
            - If id is not a string
            - If format is not one of: 'minimal', 'full', 'raw', 'metadata'
            - If metadata_headers is provided but not a list
            - If metadata_headers contains non-string elements
    """
    # --- Input Validation ---
    try:
        # Create a dictionary of the arguments to pass to the Pydantic model
        # This ensures that function defaults are handled correctly before validation
        args_dict = {
            "userId": userId,
            "id": id,
            "format": format, # Pydantic will use the alias 'format_param'
            "metadata_headers": metadata_headers,
        }
        _ = GetFunctionArgsModel(**args_dict) # Validate arguments

    except ValidationError as e:
        # Re-raise Pydantic's ValidationError.
        # The calling code can catch this for detailed error information.
        raise e
    # --- End Input Validation ---

    _ensure_user(userId) 
    
    # Accessing DB is assumed to be handled correctly.
    # If userId is valid but not in DB['users'] (e.g. _ensure_user checks another source),
    # this could also raise a ValueError.
    message = DB['users'][userId]['messages'].get(id)
    if not message:
        return None
        
    if format == 'minimal':
        return {
            'id': message['id'],
            'labelIds': [lbl.upper() for lbl in message['labelIds']]
        }
        
    if format == 'metadata':
        headers = []
        # Ensure metadata_headers is not None before iterating
        if metadata_headers:
            if 'From' in metadata_headers and 'sender' in message:
                headers.append({'name': 'From', 'value': message['sender']})
            if 'To' in metadata_headers and 'recipient' in message:
                headers.append({'name': 'To', 'value': message['recipient']})
            if 'Subject' in metadata_headers and 'subject' in message:
                headers.append({'name': 'Subject', 'value': message['subject']})
            if 'Date' in metadata_headers and 'date' in message:
                headers.append({'name': 'Date', 'value': message['date']})
            
        
        return {
            'id': message['id'],
            'labelIds': [lbl.upper() for lbl in message['labelIds']],
            'headers': headers
        }
        
    if format == 'raw':
        return {
            'id': message['id'],
            'threadId': message['threadId'],
            'labelIds': [lbl.upper() for lbl in message['labelIds']],
            'raw': message['raw'],
            'internalDate': message['internalDate']
        }
        
    # format == 'full' (default)
    # Use existing payload structure from message if available, otherwise create basic payload
    if 'payload' in message:
        payload = message['payload'].copy()
    else:
        # Create basic payload structure for messages without payload
        import base64
        body_data = base64.b64encode(message.get('body', '').encode('utf-8')).decode('utf-8')
        
        payload = {
            'headers': [
                {'name': 'From', 'value': message.get('sender')},
                {'name': 'To', 'value': message.get('recipient')},
                {'name': 'Subject', 'value': message.get('subject')},
                {'name': 'Date', 'value': message.get('date')}
            ],
            'body': {
                'data': body_data
            }
        }
        
        # If message has no payload.parts but has attachments in old format, ignore them
        # The new structure should have payload.parts with attachment references
    
    return {
        'id': message['id'],
        'threadId': message['threadId'],
        'labelIds': [lbl.upper() for lbl in message['labelIds']],
        'snippet': message['body'][:100] if message['body'] else '',
        'internalDate': message['internalDate'],
        'payload': payload,
        'sizeEstimate': len(message['body']) if message.get('body') else 0,
        # The comment notes 'raw' should only be in 'raw' format, but kept for compatibility.
        'raw': message.get('raw')
    }

def send(userId: str = "me", msg: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Sends the specified message to the specified recipient.

    Processes RFC 2822 MIME messages by parsing the base64url-encoded raw message
    to extract headers and payload structure. Automatically extracts and stores
    any attachments, creating the proper Gmail API payload structure with parts references.
    
    Attachment size limits are enforced: individual attachments cannot exceed 25MB,
    and the total message size (including all attachments) cannot exceed 100MB.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        msg (Optional[Dict[str, Any]]): An optional dictionary containing the message data with keys:
            - 'raw' (Optional[str]): The entire message represented as a base64url-encoded string 
                          (RFC 4648 Section 5). The raw string must be RFC 2822 compliant and may include attachments
                          (e.g., as multipart MIME). Individual attachments are limited to 25MB each, with
                          a total message size limit of 100MB. Optional; if not provided, the message will be 
                          constructed from 'sender', 'recipient', 'subject', 'body', etc. For messages with attachments,
                          this should be created using create_mime_message_with_attachments().
            - 'threadId' (str): Thread ID to assign to the message. If not specified,
                               a new thread will be created. Defaults to auto-generated.
            - 'labelIds' (List[str]): List of label IDs to apply to the message.
                                     The 'SENT' label is automatically applied.
            - 'sender' (str): Sender email address.
            - 'recipient' (str): Recipient email address.
            - 'subject' (str): Message subject line.
            - 'body' (str): Plain text message body.
            - 'date' (str): Message date in RFC 2822 format.
            - 'internalDate' (str): Internal timestamp as milliseconds since epoch.
            - 'isRead' (bool): Whether the message has been read.

    Returns:
        Dict[str, Any]: A dictionary representing the sent message resource with keys:
            - 'id' (str): The immutable ID of the message.
            - 'threadId' (str): The ID of the thread the message belongs to.
            - 'labelIds' (List[str]): List of labels applied to the message. Always includes 'SENT'.
            - 'payload' (Dict[str, Any]): The parsed message payload containing:
                - 'mimeType' (str): The MIME type of the message.
                - 'headers' (List[Dict[str, str]]): List of message headers with 'name' and 'value'.
                - 'parts' (List[Dict[str, Any]]): List of message parts for multipart messages. Each part is a dictionary with the following structure:
                    - 'mimeType' (str): The MIME type of the part (e.g., 'text/plain', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'image/png').
                    - 'filename' (Optional[str]): The filename of the part if it is an attachment (e.g., 'requirements.docx', 'sample_image.png'). Omitted or empty for inline/plain text parts.
                    - 'body' (Dict[str, Any]): The message body data for the part, with possible keys:
                        - 'data' (Optional[str]): The base64url-encoded content of the part (present for inline/plain text parts).
                        - 'attachmentId' (Optional[str]): The ID of the attachment (present for attachments, e.g., 'att_msg4_001').
                        - 'size' (Optional[int]): The size of the attachment in bytes (present for attachments, max 25MB per attachment).
                - 'body' (Dict[str, Any]): The message body data.
                    - 'data' (str): The base64url-encoded content of the message body.
            - 'raw' (str): The original base64url-encoded message.
            - 'internalDate' (str): Internal timestamp as milliseconds since Unix epoch.
            - 'headers' (List[Dict[str, str]]): Message headers for easy access.
            - 'sender' (str): Sender email address.
            - 'recipient' (str): Recipient email address.
            - 'subject' (str): Message subject.
            - 'body' (str): Plain text message body.
            - 'date' (str): Message date.
            - 'isRead' (bool): Whether the message has been read.

    Raises:
        TypeError: If `userId` is not a string, or if `msg` is provided and is not a dictionary.
        ValueError: If `userId` is empty, contains whitespace, or is not a valid email address.
                   If the raw MIME message cannot be parsed or is malformed.
                   If any attachment exceeds 25MB or total message size exceeds 100MB.
    """
    # --- Input Validation ---
    if not isinstance(userId, str):
        raise TypeError(f"userId must be a string, got {type(userId).__name__}")
    
    if not userId.strip():
        raise ValueError("Argument 'userId' cannot have only whitespace.")
    
    if " " in userId:
        raise ValueError("Argument 'userId' cannot have whitespace.")
    
    # Check that user id is a valid email address
    if userId != "me" and not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", userId):
        raise ValueError("userId must be a valid email address")

    if msg is None:
        msg_payload_validated = {}
    elif not isinstance(msg, dict):
        raise TypeError(f"msg must be a dictionary or None, got {type(msg).__name__}")
    else:
        try:
            validated_msg_model = MessageSendPayloadModel(**msg)
            msg_payload_validated = validated_msg_model.model_dump(exclude_none=True)
        except ValidationError as e:
            raise e
    # --- End of Input Validation ---

    # --- Enforce raw XOR other fields ---
    has_raw = "raw" in msg_payload_validated and msg_payload_validated["raw"]
    has_other_fields = any(
        k in msg_payload_validated and msg_payload_validated[k]
        for k in ("sender", "recipient", "subject", "body")
    )

        # Parse MIME message if raw field is provided
    parsed_mime = None
    if "raw" in msg_payload_validated and msg_payload_validated["raw"]:
        try:
            parsed_mime = parse_mime_message(msg_payload_validated["raw"])
        except Exception as e:
            print_log(f"Warning: MIME parsing failed: {e}")
            import traceback
            traceback.print_exc()
            # Still continue with message creation even if MIME parsing fails
    

    # If not raw, generate raw using create_mime_message_with_attachments
    if not has_raw and has_other_fields:
        # Compose arguments for the function
        sender = msg_payload_validated.get("sender", "")
        recipient = msg_payload_validated.get("recipient", "")
        subject = msg_payload_validated.get("subject", "")
        body = msg_payload_validated.get("body", "")
        from_email = sender  # for compatibility
        # create_mime_message_with_attachments expects: to, subject, body, from_email=None, cc=None, bcc=None, file_paths=None
        # Note: recipient is 'to'
        raw = create_mime_message_with_attachments(
            to=recipient,
            subject=subject,
            body=body,
            from_email=from_email,
        )
        msg_payload_validated["raw"] = raw
        has_raw = True

    # --- Core Function Logic ---
    _ensure_user(userId) 
    message_id_num = _next_counter("message") 
    message_id = f"msg_{message_id_num}"

    # Process label IDs
    processed_label_set = set()
    processed_label_set.add("SENT")
    if "labelIds" in msg_payload_validated:
        for lbl in msg_payload_validated["labelIds"]:
            processed_label_set.add(lbl.upper())
    
    if "INBOX" in processed_label_set:
        processed_label_set.discard("INBOX")

    # Create message resource
    new_msg = {
        "id": message_id,
        "threadId": msg_payload_validated.get("threadId", f"thread-{message_id_num}"),
        "labelIds": sorted(builtins.list(processed_label_set)),
        "raw": msg_payload_validated.get("raw", ""),
        "internalDate": msg_payload_validated.get("internalDate", str(int(time.time() * 1000))),  # Gmail uses milliseconds
        "date": msg_payload_validated.get("date", ""),
    }
    
    # Process parsed MIME structure
    if parsed_mime:
        new_msg["payload"] = parsed_mime["payload"]
        new_msg["headers"] = parsed_mime["headers"]
        
        # Extract headers for convenience
        header_dict = {h["name"].lower(): h["value"] for h in parsed_mime["headers"]}
        new_msg["sender"] = header_dict.get("from", "")
        new_msg["recipient"] = header_dict.get("to", "")
        new_msg["subject"] = header_dict.get("subject", "")
        
        # Extract body text from payload
        body_text = ""
        if "parts" in parsed_mime["payload"]:
            for part in parsed_mime["payload"]["parts"]:
                if part.get("mimeType", "").startswith("text/") and "data" in part.get("body", {}):
                    try:
                        import base64
                        body_text = base64.b64decode(part["body"]["data"]).decode('utf-8')
                        break
                    except:
                        pass
        elif "body" in parsed_mime["payload"] and "data" in parsed_mime["payload"]["body"]:
            try:
                import base64
                body_text = base64.b64decode(parsed_mime["payload"]["body"]["data"]).decode('utf-8')
            except:
                pass
        new_msg["body"] = body_text
    else:
        # Use provided fields directly and create basic payload structure
        new_msg.update({
            "sender": msg_payload_validated.get("sender", ""),
            "recipient": msg_payload_validated.get("recipient", ""),
            "subject": msg_payload_validated.get("subject", ""),
            "body": msg_payload_validated.get("body", ""),
            "date": msg_payload_validated.get("date", ""),
        })
        
        # Create basic payload structure even when MIME parsing fails
        import base64
        body_data = base64.b64encode(new_msg["body"].encode('utf-8')).decode('utf-8')
        
        new_msg["payload"] = {
            "mimeType": "text/plain",
            "headers": [
                {"name": "From", "value": new_msg["sender"]},
                {"name": "To", "value": new_msg["recipient"]},
                {"name": "Subject", "value": new_msg["subject"]},
                {"name": "Date", "value": new_msg["date"]}
            ],
            "body": {
                "data": body_data
            }
        }
        
        new_msg["headers"] = new_msg["payload"]["headers"]
    
    # Set read status
    new_msg["isRead"] = msg_payload_validated.get("isRead", False)
    
    # Store the message
    DB["users"][userId]["messages"][message_id] = new_msg
    
    # Create or update thread entry
    thread_id = new_msg["threadId"]
    # Ensure threads dict exists (for backwards compatibility)
    if "threads" not in DB["users"][userId]:
        DB["users"][userId]["threads"] = {}
    
    if thread_id not in DB["users"][userId]["threads"]:
        DB["users"][userId]["threads"][thread_id] = {
            "id": thread_id,
            "messageIds": [message_id]
        }
    else:
        # Add message to existing thread if not already present
        if message_id not in DB["users"][userId]["threads"][thread_id]["messageIds"]:
            DB["users"][userId]["threads"][thread_id]["messageIds"].append(message_id)

    return new_msg


def list(
    userId: str = "me",
    max_results: int = 100,
    q: str = "",
    labelIds: Optional[List[str]] = None,
    include_spam_trash: bool = False,
) -> Dict[str, Any]:
    """Lists the messages in the user's mailbox.

    Retrieves a list of messages matching the specified query criteria.
    Supports filtering based on whether the message has the `TRASH` or `SPAM` label,
    and using `q` (keywords, from:, to:, label:, subject:, attachment:) and `labelIds`. 

    Args:
        userId (str): The user ID. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        max_results (int): Maximum number of messages to return. Defaults to 100.
        q (str):
            Query string for filtering messages. Strings with spaces must be enclosed
            in single (') or double (") quotes. Supports space-delimited tokens
            (each one filters the current result set). Supported tokens:
            - `from:<email>`       Exact sender address (case-insensitive)
            - `to:<email>`         Exact recipient address (case-insensitive)
            - `label:<LABEL_ID>`   Uppercase label ID
            - `subject:<text>`     Substring match in the subject (case-insensitive)
            - `<keyword>`          Substring match in subject, body, sender or recipient (case-insensitive)
            - `"<phrase>"`         Exact phrase match in subject or body (case-insensitive)

            Filters are combined by implicit AND; token order does not matter.
            Examples:
                # Messages from bob@example.com with "report" in the subject
                q='from:bob@example.com subject:report'
                # Messages mentioning the exact phrase "urgent fix"
                q='"urgent fix"'
        labelIds (Optional[List[str]]): List of label IDs required on messages. Defaults to None.
        include_spam_trash (bool): Include messages from SPAM and TRASH.
                           Defaults to False.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - 'messages' (List[Dict[str, Any]]): List of message resources matching the query.
              Each message dictionary contains:
                - 'id' (str): Message ID.
                - 'threadId' (str): Thread ID for the message.
                - 'labelIds' (List[str]): List of labels applied to the message in uppercase.
                - 'sender' (str): Sender email address.
                - 'recipient' (str): Recipient email address.
                - 'subject' (str): Message subject.
                - 'body' (str): Message body.
                - 'date' (str): Message date.
                - 'internalDate' (str): Internal date of the message.
                - 'isRead' (bool): Whether the message has been read.
                - 'raw' (str): The entire message represented as a base64url-encoded string 
                          (RFC 4648 Section 5). The raw string must be RFC 2822 compliant and may include attachments
                          (e.g., as multipart MIME). 
                - 'payload' (Dict[str, Any]): The parsed message payload containing:
                    - 'mimeType' (str): The MIME type of the message.
                    - 'headers' (List[Dict[str, str]]): List of message headers with 'name' and 'value'.
                    - 'parts' (List[Dict[str, Any]]): List of message parts for multipart messages. Each part is a dictionary with the following structure:
                        - 'mimeType' (str): The MIME type of the part (e.g., 'text/plain', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'image/png').
                        - 'filename' (Optional[str]): The filename of the part if it is an attachment (e.g., 'requirements.docx', 'sample_image.png'). Omitted or empty for inline/plain text parts.
                        - 'body' (Dict[str, Any]): The message body data for the part, with possible keys:
                            - 'data' (Optional[str]): The base64url-encoded content of the part (present for inline/plain text parts).
                            - 'attachmentId' (Optional[str]): The ID of the attachment (present for attachments, e.g., 'att_msg4_001').
                            - 'size' (Optional[int]): The size of the attachment in bytes (present for attachments).
                    - 'body' (Dict[str, Any]): The message body data.
                        - 'data' (str): The base64url-encoded content of the message body.
            - 'nextPageToken' (None): Currently always None.

    Raises:
        TypeError: If `userId` is not a string, `max_results` is not an integer, 
                   `q` is not a string, `labelIds` is not a list or contains non-strings,
                   or `include_spam_trash` is not a boolean.
        ValueError: If `userId` is empty, `max_results` is not a positive integer,
                    or `userId` does not exist in the database.
    """
        # --- Input Validation ---
    if not isinstance(userId, str):
        raise TypeError("userId must be a string.")
    
    if not userId.strip():
        raise ValueError("userId cannot be empty")
    
    if not isinstance(max_results, int):
        raise TypeError("max_results must be an integer.")
    
    if max_results <= 0:
        raise ValueError("max_results must be a positive integer")
    
    if not isinstance(q, str):
        raise TypeError("q must be a string.")
        
    if labelIds is not None:
        if not isinstance(labelIds, builtins.list):
            raise TypeError("labelIds must be a list.")
        for label in labelIds:
            if not isinstance(label, str):
                raise TypeError("All elements in labelIds must be strings.")
    
    if not isinstance(include_spam_trash, bool):
        raise TypeError("include_spam_trash must be a boolean.")
    # --- End Input Validation ---

    _ensure_user(userId)
    all_user_messages = DB["users"][userId]["messages"]
    potential_matches = []

    # Uppercase query labelIds for consistent comparison
    query_label_ids_upper = set()
    if labelIds:
        for lbl in labelIds:
            if isinstance(lbl, str):
                query_label_ids_upper.add(lbl.upper())

    for msg_id, msg_data in all_user_messages.items():
        # Assumes msg_data['labelIds'] are already uppercase and sorted
        msg_label_ids_set = set(msg_data.get("labelIds", [])) 
        
        if not include_spam_trash and ("TRASH" in msg_label_ids_set or "SPAM" in msg_label_ids_set):
            continue
            
        if query_label_ids_upper and not query_label_ids_upper.issubset(msg_label_ids_set):
            continue
                
        potential_matches.append(msg_data)

    filtered_messages = potential_matches
    
    # Process the query string to properly handle quoted expressions
    if q:
        try:
            # Use shlex to properly parse quoted strings
            tokens = shlex.split(q)
        except ValueError:
            # Fall back to simple splitting if shlex parsing fails
            tokens = q.split()
    else:
        tokens = []

    engine = search_engine_manager.get_engine()

    for token in tokens:
        token_lower = token.lower()
        if token_lower.startswith("from:"):
            target_email = token[5:].strip().lower()
            filtered_messages = [m for m in filtered_messages if m.get("sender", "").lower() == target_email]
        elif token_lower.startswith("to:"):
            target_email = token[3:].strip().lower()
            if target_email:
                filtered_messages = [m for m in filtered_messages if m.get("recipient", "").lower() == target_email]
        elif token_lower.startswith("label:"):
            label_query = token[6:].strip().upper() # Compare with uppercase
            if label_query:
                current_messages = engine.search(label_query, {"resource_type": "message", "content_type": "labels", "user_id": userId})
                current_messages_ids = [m.get("id") for m in current_messages]
                filtered_messages = [m for m in filtered_messages if m.get("id") in current_messages_ids]
        elif token_lower.startswith("subject:"):
            subject = token[8:].strip().lower()
            if subject:
                current_messages = engine.search(subject, {"resource_type": "message", "content_type": "subject", "user_id": userId})
                current_messages_ids = [m.get("id") for m in current_messages]
                filtered_messages = [m for m in filtered_messages if m.get("id") in current_messages_ids]
        else:
            keyword = token_lower
            current_messages_subject = engine.search(keyword, {"resource_type": "message", "content_type": "subject", "user_id": userId})
            current_messages_body = engine.search(keyword, {"resource_type": "message", "content_type": "body", "user_id": userId})
            current_messages_sender = engine.search(keyword, {"resource_type": "message", "content_type": "sender", "user_id": userId})
            current_messages_recipient = engine.search(keyword, {"resource_type": "message", "content_type": "recipient", "user_id": userId})

            current_messages_ids = [m.get("id") for m in current_messages_subject]
            current_messages_ids.extend([m.get("id") for m in current_messages_body])
            current_messages_ids.extend([m.get("id") for m in current_messages_sender])
            current_messages_ids.extend([m.get("id") for m in current_messages_recipient])

            filtered_messages = [m for m in filtered_messages if m.get("id") in current_messages_ids]

    return {
        "messages": filtered_messages[:max_results],
        "nextPageToken": None
    }

def modify(
    userId: str = "me",
    id: str = "",
    addLabelIds: Optional[List[str]] = None,
    removeLabelIds: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    """Modifies the labels on the specified message.

    Adds or removes labels from the message identified by the given ID. All labels are handled
    case-insensitively and stored in their uppercase form. The function enforces label exclusivity
    rules where INBOX is mutually exclusive with SENT, DRAFT, and TRASH. Adding SENT, DRAFT, or TRASH
    will automatically remove INBOX, while adding INBOX will only succeed if none of SENT, DRAFT, or
    TRASH are present. All labels are converted to uppercase before processing, duplicates are
    automatically removed, and labels are stored in a sorted list for consistency. Custom labels can
    be added alongside system labels.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        id (str): The ID of the message to modify. Defaults to ''.
        addLabelIds (Optional[List[str]]): A list of label names to add. Label names are handled
                case-insensitively and stored in their uppercase form. Defaults to None.
        removeLabelIds (Optional[List[str]]): A list of label names to remove. Label names are handled
                case-insensitively and stored in their uppercase form. Defaults to None.

    Returns:
        Optional[Dict[str, Any]]: A dictionary representing the modified message resource if found,
        otherwise None. The dictionary contains:
            - 'id' (str): Message ID.
            - 'labelIds' (List[str]): Updated list of labels (all uppercase) applied to the message.
            - Other message properties as defined in the database.

    Raises:
        TypeError: If userId or id is not a string.
            If addLabelIds or removeLabelIds is provided and is not a list.
            If any element in addLabelIds or removeLabelIds is not a string.
        ValueError: If `userId` is empty or not a valid email address when not "me".
    """
    # --- Input Validation ---
    if not isinstance(userId, str):
        raise TypeError("userId must be a string.")
    
    if not userId.strip():
        raise ValueError("userId cannot be empty")

    if not isinstance(id, str):
        raise TypeError("id must be a string.")
    
    if userId != "me" and not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", userId):
        raise ValueError("userId must be a valid email address")

    if addLabelIds is not None:
        if not isinstance(addLabelIds, builtins.list):
            raise TypeError("addLabelIds must be a list if provided.")
        for label_id in addLabelIds:
            if not isinstance(label_id, str):
                raise TypeError("All elements in addLabelIds must be strings.")

    if removeLabelIds is not None:
        if not isinstance(removeLabelIds, builtins.list):
            raise TypeError("removeLabelIds must be a list if provided.")
        for label_id in removeLabelIds:
            if not isinstance(label_id, str):
                raise TypeError("All elements in removeLabelIds must be strings.")
    # --- End Input Validation ---

    # --- Core Logic ---
    _ensure_user(userId)
    msg = DB["users"][userId]["messages"].get(id)
    if not msg:
        return None
    
    # Work with a set of uppercase labels for efficient modification
    current_labels_upper = set(lbl.upper() for lbl in msg.get("labelIds", []))

    if addLabelIds:
        for l_add in addLabelIds:
            # Validation ensures l_add is str if addLabelIds is a list of str
            # Original code had isinstance check here, which is now covered by upfront validation
            add_label_upper = l_add.upper()
            if add_label_upper == "INBOX":
                system_labels_that_exclude_inbox = {"SENT", "DRAFT", "TRASH"}
                if not any(ex_lbl in current_labels_upper for ex_lbl in system_labels_that_exclude_inbox):
                    current_labels_upper.add("INBOX")
            elif add_label_upper in {"SENT", "DRAFT", "TRASH"}:
                current_labels_upper.add(add_label_upper)
                current_labels_upper.discard("INBOX") # Remove INBOX if adding SENT, DRAFT, or TRASH
            else:
                current_labels_upper.add(add_label_upper)

    if removeLabelIds:
        for l_remove in removeLabelIds:
            # Validation ensures l_remove is str if removeLabelIds is a list of str
            current_labels_upper.discard(l_remove.upper())
    
    msg["labelIds"] = sorted(builtins.list(current_labels_upper))
    return msg
    # --- End Core Logic ---


def batchModify(
    userId: str = "me",
    ids: Optional[List[str]] = None,
    addLabelIds: Optional[List[str]] = None,
    removeLabelIds: Optional[List[str]] = None,
) -> None:
    """Modifies the labels on multiple messages simultaneously.

    Applies the specified label modifications (add/remove) to all messages
    identified by the IDs in the provided list.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        ids (Optional[List[str]]): A list of message IDs to modify. Defaults to None or an empty list.
        addLabelIds (Optional[List[str]]): A list of label IDs to add. Label IDs are handled
                case-insensitively and stored in their uppercase form. Defaults to None.
        removeLabelIds (Optional[List[str]]): A list of label IDs to remove. Label IDs are handled
                case-insensitively and stored in their uppercase form. Defaults to None.

    Returns:
        None.

    Raises:
        TypeError:
            - If `userId` is not a string.
            - If `ids` is provided and is not a list.
            - If `ids` is provided and contains non-string elements.
            - If `addLabelIds` is provided and is not a list.
            - If `addLabelIds` is provided and contains non-string elements.
            - If `removeLabelIds` is provided and is not a list.
            - If `removeLabelIds` is provided and contains non-string elements.
        ValueError: If the specified `userId` does not exist in the database (propagated from _ensure_user).
    """
    # --- Start of validation logic ---
    if not isinstance(userId, str):
        raise TypeError("Argument 'userId' must be a string.")

    if ids is not None:
        if not isinstance(ids, List):
            raise TypeError("Argument 'ids' must be a list if provided.")
        if not all(isinstance(item, str) for item in ids):
            raise TypeError("All elements in argument 'ids' must be strings.")

    if addLabelIds is not None:
        if not isinstance(addLabelIds, List):
            raise TypeError("Argument 'addLabelIds' must be a list if provided.")
        if not all(isinstance(item, str) for item in addLabelIds):
            raise TypeError("All elements in argument 'addLabelIds' must be strings.")

    if removeLabelIds is not None:
        if not isinstance(removeLabelIds, List):
            raise TypeError("Argument 'removeLabelIds' must be a list if provided.")
        if not all(isinstance(item, str) for item in removeLabelIds):
            raise TypeError("All elements in argument 'removeLabelIds' must be strings.")
    # --- End of validation logic ---

    _ensure_user(userId)
    
    processed_ids = []
    if ids is not None: # Check again to satisfy linters/type checkers after validation
        processed_ids = ids # ids is confirmed to be List[str] if not None

    for mid in processed_ids:
        modify(
            userId=userId,
            id=mid,
            addLabelIds=[lbl.upper() for lbl in addLabelIds] if addLabelIds else None,
            removeLabelIds=[lbl.upper() for lbl in removeLabelIds] if removeLabelIds else None,
        )
