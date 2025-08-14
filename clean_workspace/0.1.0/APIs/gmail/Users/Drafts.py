# gmail/Users/Drafts.py
import shlex
from typing import Optional, Dict, Any
import builtins

from pydantic import ValidationError

from ..SimulationEngine.db import DB
from ..SimulationEngine.models import DraftInputPydanticModel, DraftUpdateInputModel
from ..SimulationEngine.attachment_utils import get_attachment_metadata_only

from ..SimulationEngine import custom_errors
from ..SimulationEngine.utils import _ensure_user, _next_counter, search_ids, _parse_query_string
from .. import Messages  # Relative import for Messages
from gmail.SimulationEngine.search_engine import search_engine_manager
from ..SimulationEngine.attachment_manager import cleanup_attachments_for_draft

def create(
    userId: str = "me", draft: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Creates a new draft message.

    Creates a new draft with the DRAFT label. The draft message content is taken from the `draft`
    argument. If no draft content is provided, an empty draft is created.
    
    Attachment size limits are enforced: individual attachments cannot exceed 25MB,
    and the total message size (including all attachments) cannot exceed 100MB.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        draft (Optional[Dict[str, Any]]): An optional dictionary containing the draft message details with keys:
            - 'id' (Optional[str]): The draft ID. Auto-generated if not provided.
            - 'message' (Dict[str, Any]): The message object with keys:
                - 'threadId' (Optional[str]): The ID of the thread this message belongs to.
                - 'raw' (Optional[str]): The entire message represented as a base64url-encoded string 
                          (RFC 4648 Section 5). The raw string must be RFC 2822 compliant and may include attachments
                          (e.g., as multipart MIME). Individual attachments are limited to 25MB each, with
                          a total message size limit of 100MB. Optional; if not provided, the message will be 
                          constructed from 'sender', 'recipient', 'subject', 'body', etc.
                - 'labelIds' (Optional[List[str]]): List of label IDs applied to this message.
                - 'snippet' (Optional[str]): A short part of the message text.
                - 'historyId' (Optional[str]): The ID of the last history record that modified this message.
                - 'internalDate' (Optional[str]): The internal message creation timestamp (epoch ms).
                - 'sizeEstimate' (Optional[int]): Estimated size in bytes of the message.
                - 'sender' (Optional[str]): The email address of the sender.
                - 'recipient' (Optional[str]): The email address of the recipient.
                - 'subject' (Optional[str]): The message subject.
                - 'body' (Optional[str]): The message body text.
                - 'isRead' (Optional[bool]): Whether the message has been read.
                - 'date' (Optional[str]): The date this message was created.
                - 'payload' (Optional[Dict[str, Any]]): The parsed email structure with keys:
                    - 'mimeType' (str): The MIME type of the message.
                    - 'parts' (List[Dict[str, Any]]): List of message parts for attachments:
                        - 'mimeType' (str): The MIME type of the part.
                        - 'filename' (Optional[str]): The filename for attachment parts.
                        - 'body' (Dict[str, Any]): The body content with keys:
                            - 'attachmentId' (str): The attachment ID reference.
                            - 'size' (int): The size of the attachment in bytes (max 25MB per attachment).
            Defaults to None, creating an empty draft.

    Returns:
        Dict[str, Any]: A dictionary representing the created draft resource with keys:
            - 'id' (str): The unique ID of the draft.
            - 'message' (Dict[str, Any]): The message object with keys:
                - 'id' (str): The message ID (same as draft ID).
                - 'threadId' (str): The thread ID.
                - 'raw' (str): The raw message content.
                - 'labelIds' (List[str]): List of label IDs, including 'DRAFT'.
                - 'snippet' (str): A short part of the message text.
                - 'historyId' (str): The history ID.
                - 'internalDate' (str): The internal date timestamp.
                - 'payload' (Dict[str, Any]): The message payload structure with keys:
                    - 'mimeType' (str): The MIME type of the message.
                    - 'parts' (List[Dict[str, Any]]): List of message parts with keys:
                        - 'mimeType' (str): The MIME type of the part.
                        - 'filename' (Optional[str]): The filename for attachment parts.
                        - 'body' (Dict[str, Any]): The body content with keys:
                            - 'data' (str): Base64 encoded content for text parts.
                            - 'attachmentId' (str): Attachment ID reference for file parts.
                            - 'size' (int): Size in bytes for attachment parts (max 25MB each).
                - 'sizeEstimate' (int): The estimated size in bytes.
                - 'sender' (str): The sender's email address.
                - 'recipient' (str): The recipient's email address.
                - 'subject' (str): The message subject.
                - 'body' (str): The message body text.
                - 'isRead' (bool): Whether the message has been read.
                - 'date' (str): The message date.

    Raises:
        TypeError: If `userId` is not a string.
        ValidationError: If the `draft` argument is provided and does not conform to the
                        `DraftInputPydanticModel` structure (e.g., missing required fields
                        like 'message', or fields have incorrect types).
                        If any attachment exceeds 25MB or total message size exceeds 100MB.
        ValueError: If the specified `userId` does not exist in the database (this error is
                   propagated from an internal helper function `_ensure_user`).
    """
    # --- Input Validation Start ---
    if not isinstance(userId, str):
        raise TypeError("userId must be a string.")

    if draft is not None:
        try:
            validated_draft = DraftInputPydanticModel(**draft).model_dump()
        except ValidationError as e:
            raise e
    # --- Input Validation End ---

    _ensure_user(userId)
    draft_id_num = _next_counter("draft")
    draft_id = f"draft-{draft_id_num}"
    
    current_draft_content = validated_draft if draft else {}
    message_input = current_draft_content.get('message', {})

    message_obj = {
        'id': draft_id, # Message ID is derived from draft_id
        'threadId': message_input.get('threadId', f"thread-{draft_id_num}"),
        'raw': message_input.get('raw', ''),
        'labelIds': message_input.get('labelIds', []),
        'snippet': message_input.get('snippet', ''),
        'historyId': message_input.get('historyId', ''),
        'internalDate': message_input.get('internalDate', '234567890'),
        'payload': message_input.get('payload', {}),
        'sizeEstimate': message_input.get('sizeEstimate', 0),
        # Compatibility fields from original code
        'sender': message_input.get('sender', ''),
        'recipient': message_input.get('recipient', ''),
        'subject': message_input.get('subject', ''),
        'body': message_input.get('body', ''),
        'isRead': message_input.get('isRead', False),
        'date': message_input.get('date', ''),
    }
    
    if 'DRAFT' not in [lbl.upper() for lbl in message_obj.get('labelIds', [])]:
        message_obj.setdefault('labelIds', []).append('DRAFT')
        
    draft_obj = {
        'id': draft_id, # The ID of the draft resource itself
        'message': message_obj
    }
    
    DB['users'][userId]['drafts'][draft_id] = draft_obj

    return draft_obj

def list(userId: str = 'me', max_results: int = 100, q: str = '') -> Dict[str, Any]:
    """Lists the drafts in the user's mailbox.

    Retrieves a list of draft messages for the specified user, optionally
    filtered by a query string. Supports basic filtering based on `from:`, `to:`,
    `subject:`, `body:`, `label:`, and general keywords in the query `q`.
    
    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        max_results (int): Maximum number of drafts to return. Must be positive.
                           Defaults to 100.
        q (str): Query string to filter drafts. Supports terms like `from:`, `to:`,
           `subject:`, `body:`, `label:`, and keywords. Defaults to ''.
           
           Examples:
               - "from:john@example.com" - Find drafts from john@example.com
               - "to:team@company.com" - Find drafts to team@company.com
               - "subject:meeting" - Find drafts with "meeting" in the subject
               - "body:project" - Find drafts containing "project" in the body
               - "label:important" - Find drafts with the "important" label
               - "from:john@example.com subject:meeting" - Combine multiple filters

    Returns:
        Dict[str, Any]: A dictionary containing:
            - 'drafts' (List[Dict[str, Any]]): List of draft resources, each with keys:
                - 'id' (str): The unique ID of the draft.
                - 'message' (Dict[str, Any]): The message object with keys:
                    - 'id' (str): The message ID.
                    - 'threadId' (str): The thread ID.
                    - 'raw' (str): The entire message represented as a base64url-encoded string 
                          (RFC 4648 Section 5). The raw string must be RFC 2822 compliant and may include attachments
                          (e.g., as multipart MIME). 
                    - 'sender' (str): The sender's email address.
                    - 'recipient' (str): The recipient's email address.
                    - 'subject' (str): The message subject.
                    - 'body' (str): The message body text.
                    - 'date' (str): The message date.
                    - 'internalDate' (str): The internal date timestamp.
                    - 'isRead' (bool): Whether the message has been read.
                    - 'labelIds' (List[str]): List of label IDs, including 'DRAFT' in uppercase.
            - 'nextPageToken' (None): Currently always None.

    Raises:
        TypeError: If `userId` or `q` is not a string, or if `max_results` is not an integer.
        InvalidMaxResultsValueError: If `max_results` is not a positive integer.
        ValueError: If the specified `userId` does not exist in the database (propagated from _ensure_user).
    """
    # Input Validation
    if not isinstance(userId, str):
        raise TypeError("userId must be a string.")
    
    if not isinstance(max_results, int):
        raise TypeError("max_results must be an integer.")
    if max_results <= 0:
        raise custom_errors.InvalidMaxResultsValueError("max_results must be a positive integer.")
        
    if not isinstance(q, str):
        raise TypeError("q must be a string.")

    _ensure_user(userId)

    engine = search_engine_manager.get_engine()
    drafts_list = builtins.list(DB["users"][userId]["drafts"].values()) 
    if q:
        tokens = shlex.split(q)
        for token in tokens:
            token_lower = token.lower()
            if token_lower.startswith("from:"):
                target_email = token[5:].strip().lower()
                drafts_list = [
                    d
                    for d in drafts_list
                    if d.get("message", {}).get("sender", "").lower() == target_email
                ]
            elif token_lower.startswith("to:"):
                target_email = token[3:].strip().lower()
                drafts_list = [
                    d
                    for d in drafts_list
                    if d.get("message", {}).get("recipient", "").lower() == target_email
                ]
            elif token_lower.startswith("subject:"):
                subject_query = token[8:].strip().lower()
                current_drafts = engine.search(subject_query, {"resource_type": "draft", "content_type": "subject", "user_id": userId})
                current_drafts_ids = [d.get("id") for d in current_drafts]
                drafts_list = [
                    d
                    for d in drafts_list
                    if d.get("id") in current_drafts_ids
                ]
            elif token_lower.startswith("body:"):
                body_query = token[5:].strip().lower()
                current_drafts = engine.search(body_query, {"resource_type": "draft", "content_type": "body", "user_id": userId})
                current_drafts_ids = [d.get("id") for d in current_drafts]
                drafts_list = [
                    d
                    for d in drafts_list
                    if d.get("id") in current_drafts_ids
                ]
            elif token_lower.startswith("label:"):
                label_name = token[6:].strip().upper()
                current_drafts = engine.search(label_name, {"resource_type": "draft", "content_type": "labels", "user_id": userId})
                current_drafts_ids = [d.get("id") for d in current_drafts]
                drafts_list = [
                    d
                    for d in drafts_list
                    if d.get("id") in current_drafts_ids
                ]
            else:
                keyword = token_lower
                current_drafts_subject = engine.search(keyword, {"resource_type": "draft", "content_type": "subject", "user_id": userId})
                current_drafts_body = engine.search(keyword, {"resource_type": "draft", "content_type": "body", "user_id": userId})
                current_drafts_sender = engine.search(keyword, {"resource_type": "draft", "content_type": "sender", "user_id": userId})
                current_drafts_recipient = engine.search(keyword, {"resource_type": "draft", "content_type": "recipient", "user_id": userId})
                current_drafts_ids = [d.get("id") for d in current_drafts_subject]
                current_drafts_ids.extend([d.get("id") for d in current_drafts_body])
                current_drafts_ids.extend([d.get("id") for d in current_drafts_sender])
                current_drafts_ids.extend([d.get("id") for d in current_drafts_recipient])
                drafts_list = [
                    d
                    for d in drafts_list
                    if d.get("id") in current_drafts_ids
                ]
    return {"drafts": drafts_list[:max_results], "nextPageToken": None}



def update(
    id: str, userId: str = "me", draft: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """Replaces a draft's content.

    Updates an existing draft message identified by its ID with the content
    provided in the `draft` argument. If the draft with the specified ID
    does not exist, it returns None.
    Ensures the 'DRAFT' label is present on the updated message.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        id (str): The ID of the draft to update.
        draft (Optional[Dict[str, Any]]): An optional dictionary containing the updated draft message content with keys:
            - 'message' (Dict[str, Any]): The message updates with keys:
                - 'id' (Optional[str]): The immutable ID of the message.
                - 'threadId' (Optional[str]): The ID of the thread this message belongs to.
                - 'raw' (Optional[str]): The entire message represented as a base64url-encoded string 
                          (RFC 4648 Section 5). The raw string must be RFC 2822 compliant and may include attachments
                          (e.g., as multipart MIME). Optional; if not provided, the message will be constructed from 'sender', 'recipient', 'subject', 'body', etc.
                - 'labelIds' (Optional[List[str]]): List of label IDs applied to this message. If provided,
                  replaces all existing labels except 'DRAFT' (which is always preserved). The 'INBOX' label
                  is explicitly removed if present in the input list.
                - 'snippet' (Optional[str]): A short part of the message text.
                - 'historyId' (Optional[str]): The ID of the last history record that modified this message.
                - 'internalDate' (Optional[str]): The internal message creation timestamp (epoch ms).
                - 'sizeEstimate' (Optional[int]): Estimated size in bytes of the message.
                - 'sender' (Optional[str]): The email address of the sender.
                - 'recipient' (Optional[str]): The email address of the recipient.
                - 'subject' (Optional[str]): The message subject.
                - 'body' (Optional[str]): The message body text.
                - 'isRead' (Optional[bool]): Whether the message has been read.
                - 'date' (Optional[str]): The date this message was created.
                - 'payload' (Optional[Dict[str, Any]]): The parsed email structure with keys:
                    - 'mimeType' (str): The MIME type of the message.
                    - 'parts' (List[Dict[str, Any]]): List of message parts for attachments:
                        - 'mimeType' (str): The MIME type of the part.
                        - 'filename' (Optional[str]): The filename for attachment parts.
                        - 'body' (Dict[str, Any]): The body content with keys:
                            - 'attachmentId' (str): The attachment ID reference.
                            - 'size' (int): The size of the attachment in bytes.
            Defaults to None.

    Returns:
        Optional[Dict[str, Any]]: A dictionary representing the updated draft resource if found and updated with keys:
            - 'id' (str): The unique ID of the draft.
            - 'message' (Dict[str, Any]): The message object with keys:
                - 'id' (str): The message ID.
                - 'threadId' (str): The thread ID.
                - 'raw' (str): The entire message represented as a base64url-encoded string 
                          (RFC 4648 Section 5). The raw string must be RFC 2822 compliant and may include attachments
                          (e.g., as multipart MIME). 
                - 'labelIds' (List[str]): List of label IDs, including 'DRAFT'.
                - 'snippet' (str): A short part of the message text.
                - 'historyId' (str): The history ID.
                - 'internalDate' (str): The internal date timestamp.
                - 'payload' (Dict[str, Any]): The message payload structure with keys:
                    - 'mimeType' (str): The MIME type of the message.
                    - 'parts' (List[Dict[str, Any]]): List of message parts with keys:
                        - 'mimeType' (str): The MIME type of the part.
                        - 'filename' (Optional[str]): The filename for attachment parts.
                        - 'body' (Dict[str, Any]): The body content with keys:
                            - 'data' (str): Base64 encoded content for text parts.
                            - 'attachmentId' (str): Attachment ID reference for file parts.
                            - 'size' (int): Size in bytes for attachment parts.
                - 'sizeEstimate' (int): The estimated size in bytes.
                - 'sender' (str): The sender's email address.
                - 'recipient' (str): The recipient's email address.
                - 'subject' (str): The message subject.
                - 'body' (str): The message body text.
                - 'isRead' (bool): Whether the message has been read.
                - 'date' (str): The message date.
            Returns None if the draft is not found.

    Raises:
        TypeError: If `userId` or `id` is not a string.
        ValueError: If `id` is an empty string or if the specified `userId` does not exist in the database.
        ValidationError: If `draft` is provided and its structure does not conform to DraftUpdateInputModel.
    """
    # --- Input Validation ---
    if not isinstance(userId, str):
        raise TypeError(f"userId must be a string.")
    if not isinstance(id, str):
        raise TypeError(f"id must be a string.")
    if not id:
        raise ValueError("id must be a non-empty string.")

    validated_draft_model: Optional[DraftUpdateInputModel] = None
    if draft is not None:
        try:
            validated_draft_model = DraftUpdateInputModel(**draft)
        except ValidationError as e:
            raise e

    _ensure_user(userId)

    message_update_payload: Dict[str, Any] = {}
    if validated_draft_model and validated_draft_model.message:
        message_update_payload = validated_draft_model.message.model_dump(exclude_unset=True)

    try:
        existing_draft_obj = DB["users"][userId]["drafts"].get(id)
    except KeyError:
        existing_draft_obj = None

    if not existing_draft_obj:
        return None

    existing_message = existing_draft_obj["message"]

    for key in [
        "threadId", "raw", "snippet", "historyId", "internalDate",
        "payload", "sizeEstimate", "sender", "recipient",
        "subject", "body", "isRead", "date"
    ]:
        if key in message_update_payload:
            existing_message[key] = message_update_payload[key]

    current_labels = {"DRAFT"}

    if "labelIds" in existing_message and isinstance(existing_message["labelIds"], builtins.list):
        for lbl in existing_message["labelIds"]:
             if isinstance(lbl, str):
                current_labels.add(lbl.upper())
    
    if "labelIds" in message_update_payload and isinstance(message_update_payload["labelIds"], builtins.list):
        current_labels = {"DRAFT"}
        for lbl_new in message_update_payload["labelIds"]:
            if isinstance(lbl_new, str):
                current_labels.add(lbl_new.upper())
    
    if "INBOX" in current_labels:
        current_labels.discard("INBOX")

    existing_message["labelIds"] = sorted(builtins.list(current_labels))

    return existing_draft_obj

def delete(userId: str = "me", id: str = "") -> Optional[Dict[str, Any]]:
    """Immediately and permanently deletes the specified draft.

    Removes the draft message identified by the given ID from the user's
    mailbox. Also cleans up any attachments that are no longer referenced
    after the draft deletion.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        id (str): The ID of the draft to delete. Defaults to ''.

    Returns:
        Optional[Dict[str, Any]]: The dictionary representing the deleted draft resource if it existed,
        with keys:
            - 'id' (str): The unique ID of the draft.
            - 'message' (Dict[str, Any]): The message object with keys:
                - 'id' (str): The message ID.
                - 'threadId' (str): The thread ID.
                - 'raw' (str): The entire message represented as a base64url-encoded string 
                          (RFC 4648 Section 5). The raw string must be RFC 2822 compliant and may include attachments
                          (e.g., as multipart MIME). 
                - 'sender' (str): The sender's email address.
                - 'recipient' (str): The recipient's email address.
                - 'subject' (str): The message subject.
                - 'body' (str): The message body text.
                - 'date' (str): The message date.
                - 'internalDate' (str): The internal date timestamp.
                - 'isRead' (bool): Whether the message has been read.
                - 'labelIds' (List[str]): List of label IDs, including 'DRAFT' in uppercase.
        Otherwise None.

    Raises:
        TypeError: If `userId` or `id` is not a string.
        ValueError: If the specified `userId` does not exist in the database
    """
    # --- Input Validation ---
    if not isinstance(userId, str):
        raise TypeError(f"userId must be a string, but got {type(userId).__name__}.")
    if not isinstance(id, str):
        raise TypeError(f"id must be a string, but got {type(id).__name__}.")
    # --- End Input Validation ---

    _ensure_user(userId)
    
    # Clean up attachments before deleting draft
    cleanup_attachments_for_draft(userId, id)
    
    # Delete the draft
    return DB["users"][userId]["drafts"].pop(id, None)


def get(
    userId: str = "me", id: str = "", format: str = "full"
) -> Optional[Dict[str, Any]]:
    """Gets the specified draft.

    Retrieves the draft message identified by the given ID.
    The format parameter determines what data is returned:
    - 'minimal': Returns only email message ID and labels
    - 'full': Returns the full email message data with parsed body content
    - 'raw': Returns the full email message data with body content in raw field
    - 'metadata': Returns only email message ID, labels, and email headers

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        id (str): The ID of the draft to retrieve. Defaults to ''.
        format (str): The format to return the message in. One of 'minimal',
                'full', 'raw', or 'metadata'. Defaults to 'full'.

    Returns:
        Optional[Dict[str, Any]]: A dictionary representing the draft resource if found, with keys:
            - 'id' (str): The unique ID of the draft.
            - 'message' (Dict[str, Any]): The message object with keys:
                - 'id' (str): The message ID.
                - 'threadId' (str): The thread ID.
                - 'raw' (str): The entire message represented as a base64url-encoded string 
                          (RFC 4648 Section 5). The raw string must be RFC 2822 compliant and may include attachments
                          (e.g., as multipart MIME). 
                - 'sender' (str): The sender's email address.
                - 'recipient' (str): The recipient's email address.
                - 'subject' (str): The message subject.
                - 'body' (str): The message body text.
                - 'date' (str): The message date.
                - 'internalDate' (str): The internal date timestamp.
                - 'isRead' (bool): Whether the message has been read.
                - 'labelIds' (List[str]): List of label IDs, including 'DRAFT' in uppercase.
        The content varies based on the format parameter:
            - minimal: Only id and labelIds
            - full: Complete draft with parsed body
            - raw: The entire message represented as a base64url-encoded string 
                          (RFC 4648 Section 5). The raw string must be RFC 2822 compliant and may include attachments
                          (e.g., as multipart MIME). 
            - metadata: ID, labels and headers (sender, recipient, subject, date)
        Otherwise None.

    Raises:
        TypeError: If `userId`, `id`, or `format` are not of type string.
        InvalidFormatError: If the provided `format` is not one of 'minimal',
                          'full', 'raw', or 'metadata'.
        ValueError: If the specified `userId` does not exist in the database
    """
    # --- Input Validation ---
    if not isinstance(userId, str):
        raise TypeError(f"userId must be a string, but got {type(userId).__name__}.")
    if not isinstance(id, str):
        raise TypeError(f"id must be a string, but got {type(id).__name__}.")
    if not isinstance(format, str):
        raise TypeError(f"format must be a string, but got {type(format).__name__}.")

    allowed_formats = ['minimal', 'full', 'raw', 'metadata']
    if format not in allowed_formats:
        raise custom_errors.InvalidFormatValueError(
            f"Invalid format '{format}'. Must be one of: {', '.join(allowed_formats)}."
        )
    # --- End of Input Validation ---

    _ensure_user(userId)
    
    draft = DB['users'][userId]['drafts'].get(id)
    
    if not draft:
        return None

    result = {'id': draft['id']}
    
    if format == 'minimal':
        result['message'] = {
            'id': draft['message']['id'],
            'labelIds': [lbl.upper() for lbl in draft['message']['labelIds']]
        }
    elif format == 'raw':
        result['message'] = {
            'id': draft['message']['id'],
            'threadId': draft['message']['threadId'],
            'labelIds': [lbl.upper() for lbl in draft['message']['labelIds']],
            'raw': draft['message']['raw']
        }
    elif format == 'metadata':
        result['message'] = {
            'id': draft['message']['id'],
            'threadId': draft['message']['threadId'],
            'labelIds': [lbl.upper() for lbl in draft['message']['labelIds']],
            'sender': draft['message']['sender'],
            'recipient': draft['message']['recipient'],
            'subject': draft['message']['subject'],
            'date': draft['message']['date']
        }
    else:  # format == 'full'
        result['message'] = {
            'id': draft['message']['id'],
            'threadId': draft['message']['threadId'],
            'sender': draft['message']['sender'],
            'recipient': draft['message']['recipient'],
            'subject': draft['message']['subject'],
            'body': draft['message']['body'],
            'date': draft['message']['date'],
            'internalDate': draft['message']['internalDate'],
            'isRead': draft['message']['isRead'],
            'labelIds': [lbl.upper() for lbl in draft['message']['labelIds']],
            'raw': draft['message']['raw'] # According to the documentation, this parameter should only be present in the 'raw' format. But it was added here to avoid errors in existing code.
        }
    
    return result


def send(userId: str = "me", draft: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Sends the specified draft.

    Sends the message associated with a draft. If the `draft` argument contains
    an `id` corresponding to an existing draft, that draft is sent and then
    deleted. If no `id` is provided, or the `id` doesn't match an existing
    draft, the message content within the `draft` argument (specifically
    `draft['message']['raw']`) is sent directly using `Messages.send`.
    
    Attachment size limits are enforced: individual attachments cannot exceed 25MB,
    and the total message size (including all attachments) cannot exceed 100MB.

    Args:
        userId (str): The user's email address. The special value 'me'
                can be used to indicate the authenticated user. Defaults to 'me'.
        draft (Optional[Dict[str, Any]]): An optional dictionary containing the draft to send with keys:
            - 'id' (Optional[str]): The ID of an existing draft to send.
            - 'message' (Optional[Dict[str, Any]]): The message content to send directly with keys:
                - 'threadId' (Optional[str]): The ID of the thread this message belongs to.
                - 'raw' (Optional[str]): The entire message represented as a base64url-encoded string 
                          (RFC 4648 Section 5). The raw string must be RFC 2822 compliant and may include attachments
                          (e.g., as multipart MIME). Individual attachments are limited to 25MB each, with
                          a total message size limit of 100MB. Optional; if not provided, the message will be 
                          constructed from 'sender', 'recipient', 'subject', 'body', etc.
                - 'internalDate' (Optional[str]): The internal message creation timestamp (epoch ms).
                - 'labelIds' (Optional[List[str]]): List of label IDs applied to this message.
                - 'snippet' (Optional[str]): A short part of the message text.
                - 'historyId' (Optional[str]): The ID of the last history record that modified this message.
                - 'sizeEstimate' (Optional[int]): Estimated size in bytes of the message.
                - 'sender' (Optional[str]): The email address of the sender.
                - 'recipient' (Optional[str]): The email address of the recipient.
                - 'subject' (Optional[str]): The message subject.
                - 'body' (Optional[str]): The message body text.
                - 'isRead' (Optional[bool]): Whether the message has been read.
                - 'date' (Optional[str]): The message date.
                - 'payload' (Optional[Dict[str, Any]]): The parsed email structure with keys:
                    - 'mimeType' (str): The MIME type of the message.
                    - 'parts' (List[Dict[str, Any]]): List of message parts for attachments:
                        - 'mimeType' (str): The MIME type of the part.
                        - 'filename' (Optional[str]): The filename for attachment parts.
                        - 'body' (Dict[str, Any]): The body content with keys:
                            - 'attachmentId' (str): The attachment ID reference.
                            - 'size' (int): The size of the attachment in bytes (max 25MB per attachment).
            Defaults to None.

    Returns:
        Dict[str, Any]: A dictionary representing the sent message resource, as returned by
        `Messages.send`, with keys:
            - 'id' (str): The generated message ID.
            - 'threadId' (str): The thread ID for the message.
            - 'raw' (str): The entire message represented as a base64url-encoded string 
                          (RFC 4648 Section 5). The raw string must be RFC 2822 compliant and may include attachments
                          (e.g., as multipart MIME). 
            - 'sender' (str): The sender email address.
            - 'recipient' (str): The recipient email address.
            - 'subject' (str): The message subject.
            - 'body' (str): The message body text.
            - 'date' (str): The message date.
            - 'internalDate' (str): The internal date timestamp.
            - 'isRead' (bool): Whether the message has been read.
            - 'labelIds' (List[str]): List of label IDs, including 'SENT'.

    Raises:
        TypeError: If `userId` is not a string.
        ValidationError: If the `draft` argument is provided and does not conform to the
                        `DraftInputPydanticModel` structure or if inputs are not valid.
                        If any attachment exceeds 25MB or total message size exceeds 100MB.
        ValueError: If the draft or message is missing required fields for sending.
                   When sending an existing draft or new message without raw content,
                   the following fields are required: `recipient`, `subject`, and `body`.
                   If `raw` content is provided, these individual fields are not required
                   as the raw content contains all necessary message information.
    """
    # --- Input Validation ---
    if not isinstance(userId, str):
        raise TypeError(f"Argument 'userId' must be a string, but got {type(userId).__name__}.")
    if not userId.strip():
        raise custom_errors.ValidationError(f"Argument 'userId' cannot have only whitespace.")
    if " " in userId:
        raise custom_errors.ValidationError(f"Argument 'userId' cannot have whitespace.")
    if draft is None:
        draft = {}
    if not isinstance(draft, dict):
        raise TypeError(f"Argument 'draft' must be a dictionary, but got {type(draft).__name__}.")
    
    # Validate the draft structure with Pydantic model
    # When sending by ID, we don't need the message field in the input
    draft_id = draft.get("id")
    if draft_id:
        # If we have a draft ID, we'll validate it exists later
        # For now, just validate that the ID is a string
        if not isinstance(draft_id, str):
            raise custom_errors.ValidationError(f"Argument 'draft' is not valid.")
    else:
        # If no draft ID, validate the draft structure with message field
        try:
            DraftInputPydanticModel(**draft)
        except:
            raise custom_errors.ValidationError(f"Argument 'draft' is not valid.")

    # --- End of Input Validation ---
    _ensure_user(userId)
    draft = draft or {}
    draft_id = draft.get("id")
    if draft_id and draft_id in DB["users"][userId]["drafts"]:
        draft_obj = DB["users"][userId]["drafts"][draft_id]
        message_data = draft_obj.get("message", {})
        
        # Validate that the draft has required fields for sending
        recipient = (message_data.get('recipient') or '').strip()
        subject = (message_data.get('subject') or '').strip()
        body = (message_data.get('body') or '').strip()
        raw = (message_data.get('raw') or '').strip()
        
        # If no raw content, we need the individual fields
        if not raw and (not recipient or not subject or not body):
            missing_fields = []
            if not recipient:
                missing_fields.append("recipient")
            if not subject:
                missing_fields.append("subject")
            if not body:
                missing_fields.append("body")
            raise ValueError(f"Cannot send draft: missing required fields: {', '.join(missing_fields)}")
        
        # Extract only the fields that Messages.send expects to avoid validation issues
        # and ensure all message details are preserved
        send_message_data = {
            'threadId': message_data.get('threadId'),
            'raw': message_data.get('raw'),
            'sender': message_data.get('sender'),
            'recipient': message_data.get('recipient'),
            'subject': message_data.get('subject'),
            'body': message_data.get('body'),
            'date': message_data.get('date'),
            'internalDate': message_data.get('internalDate'),
            'isRead': message_data.get('isRead'),
            'labelIds': message_data.get('labelIds')
        }
        
        msg = Messages.send(userId=userId, msg=send_message_data)
        DB["users"][userId]["drafts"].pop(draft_id, None)
        return msg
    else:
        msg = draft.get("message", {})
        
        # Validate that the message has required fields for sending
        recipient = (msg.get('recipient') or '').strip()
        subject = (msg.get('subject') or '').strip()
        body = (msg.get('body') or '').strip()
        raw = (msg.get('raw') or '').strip()
        
        # If no raw content, we need the individual fields
        if not raw and (not recipient or not subject or not body):
            missing_fields = []
            if not recipient:
                missing_fields.append("recipient")
            if not subject:
                missing_fields.append("subject")
            if not body:
                missing_fields.append("body")
            raise ValueError(f"Cannot send message: missing required fields: {', '.join(missing_fields)}")
        
        return Messages.send(userId=userId, msg=msg)
