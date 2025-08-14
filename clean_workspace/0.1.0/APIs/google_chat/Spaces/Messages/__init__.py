from common_utils.print_log import print_log
# APIs/google_chat/Spaces/Messages/__init__.py

import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

sys.path.append("APIs")

from typing import Optional, Dict, Any # Specific types used by the function signature


from google_chat.SimulationEngine.db import DB, CURRENT_USER_ID
from google_chat.SimulationEngine.custom_errors import InvalidMessageReplyOptionError, InvalidMessageIdFormatError, MissingThreadDataError, UserNotMemberError, DuplicateRequestIdError
from google_chat.SimulationEngine.models import MessageBodyInput
from pydantic import ValidationError

# Valid options for messageReplyOption
VALID_MESSAGE_REPLY_OPTIONS = [
    "MESSAGE_REPLY_OPTION_UNSPECIFIED",
    "REPLY_MESSAGE_FALLBACK_TO_NEW_THREAD",
    "REPLY_MESSAGE_OR_FAIL",
    "NEW_THREAD",
]

def create(
    parent: str,
    message_body: Dict[str, Any], # Changed from Optional to Required as per docstring
    requestId: Optional[str] = None,
    messageReplyOption: str = "MESSAGE_REPLY_OPTION_UNSPECIFIED",
    messageId: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Creates a message in a space.

    The space is identified by `parent`, for example, "spaces/AAA". The caller must be a member
    of "spaces/{space}/members/{CURRENT_USER_ID}" to create a message.

    Args:
        parent (str): Required. Resource name of the space to create the message in.
            Format: "spaces/{space}".
        message_body (Dict[str, Any]): Required. A dictionary representing the message resource object. Based on the
            MessageBodyInput model, the following core fields are supported:
            - text (Optional[str]): Plain-text body of the message.
            - thread (Optional[Dict[str, Any]]): Thread information based on ThreadDetailInput model:
                - name (Optional[str]): Resource name of the thread (e.g., "spaces/AAA/threads/BBB").
            - attachment (Optional[List[Dict[str, Any]]]): List of message attachments (defaults to empty list):
                - name (str): Attachment resource name.
                - contentName (str): File name.
                - contentType (str): MIME type.
                - thumbnailUri (str): Thumbnail preview image.
                - downloadUri (str): Direct download URL.
                - source (str): One of "DRIVE_FILE", "UPLOADED_CONTENT".
                - attachmentDataRef (Dict[str, Any]): For uploading files:
                    - resourceName (str): Reference to the media.
                    - attachmentUploadToken (str): Token for uploaded content.
                - driveDataRef (Dict[str, Any]): Drive file metadata:
                    - driveFileId (str): ID of the file in Google Drive.
            
            Additional fields are accepted due to the model's extra='allow' configuration, which may include:
            - cards, cardsV2, annotations, accessoryWidgets, and other message content fields.
            These will be passed through but are not explicitly validated by the MessageBodyInput model.
        requestId (Optional[str]): A unique ID for the message request. If reused by the same user,
            the same message is returned. If reused incorrectly, results in a conflict and returns an
            empty dictionary.
        messageReplyOption (str): Controls whether the message starts a new thread or replies
            to an existing one. Valid values:
            - 'MESSAGE_REPLY_OPTION_UNSPECIFIED': Default behavior
            - 'REPLY_MESSAGE_FALLBACK_TO_NEW_THREAD': Reply to existing thread if specified, otherwise create new thread
            - 'REPLY_MESSAGE_OR_FAIL': Reply to existing thread if specified, otherwise fail
            - 'NEW_THREAD': Always create a new thread
        messageId (Optional[str]): A custom ID that must start with "client-". Included in the message's
            resource name if provided.

    Returns:
        Dict[str, Any]: A dictionary representing the created or existing message resource. The function creates
            and returns a message object with the following core fields:
            - name (str): Resource name of the message. Format: "spaces/{space}/messages/{message}".
            - text (str): Plain-text body of the message from MessageBodyInput.text (defaults to empty string).
            - attachment (List[Dict[str, Any]]): List of message attachments from MessageBodyInput.attachment 
                (defaults to empty array if not provided).
            - createTime (str): RFC-3339 timestamp when the message was created (set by function).
            - thread (Dict[str, Any]): Thread information determined by messageReplyOption and MessageBodyInput.thread:
                - name (str): Resource name of the thread (can be empty string).
                - Additional thread fields as determined by the thread resolution logic.
            - requestId (Optional[str]): The request ID that was used to create this message (if provided).
            - sender (Dict[str, Any]): Information about the user who sent the message (set by function):
                - name (str): Resource name of the sender from CURRENT_USER_ID.
                - type (str): Type of user, defaults to "HUMAN".
            - clientAssignedMessageId (str): Custom ID assigned to the message (only present if messageId was provided).
            
            Additional fields may be present if they were included in the message_body input and processed
            by the MessageBodyInput model's extra='allow' configuration.

    Raises:
        TypeError: If `parent`, `requestId`, `messageReplyOption`, or `messageId` have incorrect types.
        ValueError: If `parent` is empty.
        InvalidMessageIdFormatError: If `messageId` is provided but does not start with "client-".
        InvalidMessageReplyOptionError: If `messageReplyOption` is not one of the valid values.
        pydantic.ValidationError: If `message_body` is not a valid dictionary or does not conform to the expected structure.
        UserNotMemberError: If the current user is not a member of the specified space.
        MissingThreadDataError: If `messageReplyOption` is 'REPLY_MESSAGE_OR_FAIL' and thread information is missing.
        DuplicateRequestIdError: If the `requestId` has been used by the same user for a different message.
    """
    # --- Input Validation ---
    if not isinstance(parent, str):
        raise TypeError("Argument 'parent' must be a string.")
    if not parent:
        raise ValueError("Argument 'parent' cannot be empty.")

    if requestId is not None and not isinstance(requestId, str):
        raise TypeError("Argument 'requestId' must be a string if provided.")

    if not isinstance(messageReplyOption, str):
        raise TypeError("Argument 'messageReplyOption' must be a string.")
    if messageReplyOption not in VALID_MESSAGE_REPLY_OPTIONS:
        raise InvalidMessageReplyOptionError(
            f"Invalid messageReplyOption: '{messageReplyOption}'. "
            f"Valid options are: {', '.join(VALID_MESSAGE_REPLY_OPTIONS)}"
        )

    if messageId is not None:
        if not isinstance(messageId, str):
            raise TypeError("Argument 'messageId' must be a string if provided.")
        if not messageId.startswith("client-"):
            raise InvalidMessageIdFormatError(
                "If 'messageId' is provided, it must start with 'client-'."
            )

    if not isinstance(message_body, dict):
        # This case might be caught by Pydantic as well if it receives non-dict,
        # but an explicit check is clearer for non-dict types.
        raise TypeError("Argument 'message_body' must be a dictionary.")
    try:
        validated_message_body = MessageBodyInput(**message_body)
    except ValidationError as e:
        raise e

    # --- Core Logic (original logic adapted for new error handling) ---

    # Check for duplicate requestId
    if requestId:
        # Ensure CURRENT_USER_ID and DB are accessible
        # These would typically be passed or be instance variables
        for msg in DB.get("Message", []):
            if msg.get("requestId") == requestId and msg.get("sender", {}).get(
                "name"
            ) == CURRENT_USER_ID.get("id"):
                # Original logic returned the message. We can raise a specific error or return as is.
                # For consistency with CRUD, finding an existing item by a unique request ID is often
                # considered a success. However, if the intent is that reusing requestId for a *different*
                # message creation attempt is an error, then an error should be raised.
                # The docstring says "If reused by the same user, the same message is returned".
                # "If reused incorrectly, results in a conflict and returns an empty dictionary."
                # This implies more complex logic than simple input validation.
                # For now, let's assume "reused incorrectly" means some other conflict not just existence.
                # If it's strictly about "message is already there", returning it is fine.
                # Let's keep the original behavior of returning the existing message.
                # print(f"Found existing message with requestId {requestId}") # Original print
                return msg # Return existing message

    # 1) Verify membership => name = "spaces/{parent}/members/{CURRENT_USER_ID}"
    membership_name = f"{parent}/members/{CURRENT_USER_ID.get('id')}"
    is_member = any(m.get("name") == membership_name for m in DB.get("Membership", []))
    if not is_member:
        raise UserNotMemberError(
            f"User {CURRENT_USER_ID.get('id')} is not a member of {parent}."
        )

    if messageId:
        # Validation for messageId format (startswith('client-')) already done above.
        new_msg_name = f"{parent}/messages/{messageId}"
    else:
        # generate a numeric ID
        new_msg_name = f"{parent}/messages/{len(DB.get('Message', [])) + 1}"

    # 3) Handle messageReplyOption
    thread_info_from_body = validated_message_body.thread.model_dump(exclude_none=True) if validated_message_body.thread else {}
    
    final_thread_info = {} # This will hold the thread info for the new message

    if messageReplyOption != "MESSAGE_REPLY_OPTION_UNSPECIFIED":
        if messageReplyOption == "NEW_THREAD":
            # Always create a new thread
            final_thread_info = {"name": f"{parent}/threads/{len(DB.get('Message', [])) + 1000}"} # Use a different counter to avoid ID clashes with messages
        elif messageReplyOption in [
            "REPLY_MESSAGE_FALLBACK_TO_NEW_THREAD",
            "REPLY_MESSAGE_OR_FAIL",
        ]:
            # Check if thread info is provided in message_body
            if not thread_info_from_body or not thread_info_from_body.get("name"):
                if messageReplyOption == "REPLY_MESSAGE_OR_FAIL":
                    raise MissingThreadDataError(
                        "Thread information (thread.name) is required in 'message_body' "
                        "when 'messageReplyOption' is 'REPLY_MESSAGE_OR_FAIL'."
                    )
                else: # REPLY_MESSAGE_FALLBACK_TO_NEW_THREAD
                    # Create new thread as fallback
                    final_thread_info = {"name": f"{parent}/threads/{len(DB.get('Message', [])) + 1000}"}
            else:
                # Use provided thread info
                final_thread_info = thread_info_from_body
    else: # MESSAGE_REPLY_OPTION_UNSPECIFIED
        # If thread info is in message_body, use it. Otherwise, no specific thread (message starts a new logical thread implicitly or is standalone)
        final_thread_info = thread_info_from_body if thread_info_from_body else {}


    # 4) Build the new message object
    new_message = {
        "name": new_msg_name,
        "text": validated_message_body.text or "",
        "attachment": validated_message_body.attachment if validated_message_body.attachment is not None else [],
        "createTime": datetime.now().isoformat() + "Z",
        "thread": final_thread_info, # Use the determined thread_info
        "requestId": requestId, # Store requestId if provided
        # "messageReplyOption": messageReplyOption, # This is usually not part of the stored message resource itself

        # The sender is set from the user ID (in reality, the server would do this)
        "sender": {"name": CURRENT_USER_ID.get("id"), "type": "HUMAN"}, # Assuming type based on typical user
    }
    
    # Add other fields from validated_message_body if they were allowed by extra='allow'
    # and are meant to be part of the message.
    # For example, if cardsV2 were passed in message_body and defined in Pydantic model:
    # if validated_message_body.cardsV2:
    #    new_message["cardsV2"] = validated_message_body.cardsV2


    # If messageId is set, store it as clientAssignedMessageId
    if messageId:
        new_message["clientAssignedMessageId"] = messageId

    # 5) Insert into DB
    if "Message" not in DB: # Ensure 'Message' key exists
        DB["Message"] = []
    DB["Message"].append(new_message)
    # print(f"Message {new_msg_name} created successfully.") # Original print

    return new_message


def list(
    parent: str,
    pageSize: Optional[int] = None,
    pageToken: Optional[str] = None,
    filter: Optional[str] = None,
    orderBy: Optional[str] = None,
    showDeleted: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Lists messages in a space where the caller is a member.

    The space is identified by `parent`, e.g., "spaces/AAA". The caller must be a member of the specified space to retrieve messages.

    Args:
        parent (str): Required. The resource name of the space to list messages from. Format: `spaces/{space}`.
        pageSize (Optional[int]): The maximum number of messages to return. Defaults to 25 if unspecified. Maximum is 1000. Negative values raise an error.
        pageToken (Optional[str]): Token for fetching the next page of results. Should be passed unchanged to retrieve paginated data.
        filter (Optional[str]): A query string for filtering messages by `create_time` and/or `thread.name`. Examples:
            - create_time > "2023-04-21T11:30:00-04:00"
            - create_time > "2023-04-21T11:30:00-04:00" AND thread.name = spaces/AAA/threads/123
        orderBy (Optional[str]): Order of the returned messages. Valid values:
            - "createTime desc": Sort by createTime in descending order (newest first)
            - "createTime asc": Sort by createTime in ascending order (oldest first)
            Defaults to "createTime desc" if unspecified.
        showDeleted (Optional[bool]): Whether to include deleted messages. If False, messages with `deleteTime` are excluded.

    Returns:
        Dict[str, Any]: A dictionary representing the response with the following structure:
            - messages (List[Dict[str, Any]]): A list of message objects. Each message includes:
                - name (str): Resource name of the message. Format: "spaces/{space}/messages/{message}".
                - createTime (str): RFC-3339 timestamp when the message was created.
                - lastUpdateTime (str): RFC-3339 timestamp of last message update.
                - deleteTime (str): RFC-3339 timestamp when the message was deleted, if applicable.
                - text (str): Plain-text body of the message.
                - formattedText (str): Message text with markup formatting.
                - fallbackText (str): Fallback text for cards.
                - argumentText (str): Message text with app mentions stripped out.
                - threadReply (bool): Indicates if the message is a reply in a thread.
                - clientAssignedMessageId (str): Custom ID assigned to the message, if provided.
                - sender (Dict[str, Any]):
                    - name (str): Resource name of the sender, e.g., "users/123".
                    - displayName (str): Display name of the sender.
                    - domainId (str): Google Workspace domain ID.
                    - type (str): Type of user. One of:
                        - "TYPE_UNSPECIFIED"
                        - "HUMAN"
                        - "BOT"
                    - isAnonymous (bool): Indicates if the sender is deleted or hidden.
                - thread (Dict[str, Any]):
                    - name (str): Resource name of the thread.
                    - threadKey (str): Thread key used to create the thread.
                - space (Dict[str, Any]):
                    - name (str): Resource name of the space.
                    - type (str): Deprecated. Use `spaceType` instead.
                    - spaceType (str): Type of space. One of:
                        - "SPACE"
                        - "GROUP_CHAT"
                        - "DIRECT_MESSAGE"
                    - displayName (str): Optional display name of the space.
                    - externalUserAllowed (bool): Whether external users are allowed.
                    - spaceThreadingState (str): Threading behavior. One of:
                        - "SPACE_THREADING_STATE_UNSPECIFIED"
                        - "THREADED_MESSAGES"
                        - "GROUPED_MESSAGES"
                        - "UNTHREADED_MESSAGES"
                    - spaceHistoryState (str): History configuration. One of:
                        - "HISTORY_STATE_UNSPECIFIED"
                        - "HISTORY_OFF"
                        - "HISTORY_ON"
                    - createTime (str): RFC-3339 timestamp when the space was created.
                    - lastActiveTime (str): RFC-3339 timestamp of last message activity.
                    - importMode (bool): Whether the space was created in import mode.
                    - adminInstalled (bool): Whether the space was created by an admin.
                    - spaceUri (str): Direct URL to open the space.
                    - singleUserBotDm (bool): Whether it's a bot-human direct message.
                    - predefinedPermissionSettings (str): Optional predefined permissions. One of:
                        - "PREDEFINED_PERMISSION_SETTINGS_UNSPECIFIED"
                        - "COLLABORATION_SPACE"
                        - "ANNOUNCEMENT_SPACE"
                    - spaceDetails (Dict[str, Any]):
                        - description (str): Description of the space.
                        - guidelines (str): Rules and expectations.
                    - membershipCount (Dict[str, Any]):
                        - joinedDirectHumanUserCount (int): Count of joined human users.
                        - joinedGroupCount (int): Count of joined groups.
                    - accessSettings (Dict[str, Any]):
                        - accessState (str): One of:
                            - "ACCESS_STATE_UNSPECIFIED"
                            - "PRIVATE"
                            - "DISCOVERABLE"
                        - audience (str): Resource name of discoverable audience, e.g., "audiences/default".
            - annotations (List[Dict[str, Any]]): Rich annotations (e.g., mentions, emojis).
                - type (str): Annotation type. One of: "USER_MENTION", "SLASH_COMMAND", "RICH_LINK", "CUSTOM_EMOJI".
                - startIndex (int): Start position in the message text.
                - length (int): Length of the annotated segment.
                - userMention (Dict[str, Any]): Info about mentioned user.
                    - type (str): Mention type. One of: "ADD", "MENTION".
                - slashCommand (Dict[str, Any]): Slash command metadata.
                    - type (str): Command interaction type.
                    - commandName (str): Command name.
                    - commandId (str): Unique command ID.
                    - triggersDialog (bool): If it opens a dialog.
                - richLinkMetadata (Dict[str, Any]): Rich preview link data.
                    - uri (str): URL.
                    - richLinkType (str): E.g., "DRIVE_FILE", "CHAT_SPACE".
                    - driveLinkData.mimeType (str): File type for drive links.
                    - chatSpaceLinkData (Dict[str, Any]): Chat space linking info.
                        - space (str): Space name.
                        - thread (str): Thread name.
                        - message (str): Message name.
                - customEmojiMetadata (Dict[str, Any]): Custom emoji info.
                    - customEmoji (Dict[str, Any]):
                        - name (str): Server-assigned name (e.g., `customEmojis/emoji_id`).
                        - uid (str): Unique ID.
                        - emojiName (str): Emoji name, e.g., `:fire_emoji:`.
                        - temporaryImageUri (str): Temporary image URL.
            - cards (List[Dict[str, Any]]): Legacy UI cards shown in Chat messages.
                - name (str): Identifier for the card.
                - header (Dict[str, Any]): Optional card header.
                    - title (str): Required. Title text.
                    - subtitle (str): Optional subtitle text.
                    - imageUrl (str): Optional header image URL.
                    - imageStyle (str): "IMAGE" or "AVATAR".
                - sections (List[Dict[str, Any]]): Content sections within the card.
                    - header (str): Optional section header.
                    - widgets (List[Dict[str, Any]]): List of visual elements such as text, buttons, images.
                        - textParagraph (Dict[str, Any]): A block of text.
                            - text (str): The paragraph content.
                        - keyValue (Dict[str, Any]): Key-value styled layout.
                            - topLabel (str): Top label.
                            - content (str): Content.
                            - bottomLabel (str): Bottom label.
                            - icon (str): Icon.
                            - iconUrl (str): Icon URL.
                        - image (Dict[str, Any]): Standalone image.
                            - imageUrl (str): Image URL.
                            - aspectRatio (float): Aspect ratio.
                        - buttons (List[Dict[str, Any]]): Button elements for interaction.
                - cardActions (List[Dict[str, Any]]): Actions at the bottom of the card.
                    - actionLabel (str): Text shown for the action.
                    - onClick (Dict[str, Any]): Action handler.
                        - openLink (Dict[str, Any]): URL to open.
                        - action (Dict[str, Any]): Invokes a defined method.
                - fixedFooter (Dict[str, Any]): Optional persistent footer.
                    - primaryButton (Dict[str, Any]): Button element.
                        - text (str): Text.
                        - disabled (bool): Disabled.
                        - altText (str): Alt text.
                        - type (str): Type.
            - cardsV2 (List[Dict[str, Any]]): New generation cards with structured layouts.
                - cardId (str): Identifier used to update this card.
                - card (Dict[str, Any]): Complete structure including headers, sections, actions, and footers.
            - attachment (List[Dict[str, Any]]): Message attachments, such as files.
                - name (str): Attachment resource name.
                - contentName (str): File name.
                - contentType (str): MIME type.
                - thumbnailUri (str): Thumbnail preview image.
                - downloadUri (str): Direct download URL.
                - source (str): One of: "DRIVE_FILE", "UPLOADED_CONTENT".
                - attachmentDataRef (Dict[str, Any]): For uploading files.
                    - resourceName (str): Reference to the media.
                    - attachmentUploadToken (str): Token for uploaded content.
                - driveDataRef (Dict[str, Any]): Drive file metadata.
                    - driveFileId (str): ID of the file in Google Drive.
            - matchedUrl (Dict[str, Any]): Metadata for previewable URLs.
                - url (str): The matched link.
            - emojiReactionSummaries (List[Dict[str, Any]]): Summary of emoji reactions.
                - reactionCount (int): Total count of reactions.
                - emoji (Dict[str, Any]):
                    - unicode (str): The emoji used.
            - deletionMetadata (Dict[str, Any]): Deletion details.
                - deletionType (str): Who deleted it. One of: "CREATOR", "ADMIN", etc.
            - quotedMessageMetadata (Dict[str, Any]): Metadata of quoted messages.
                - name (str): Quoted message resource name.
                - lastUpdateTime (str): Timestamp of last update.
            - attachedGifs (List[Dict[str, Any]]): List of attached GIF previews.
                - uri (str): URL to the GIF image.
            - actionResponse (Dict[str, Any]): Data returned by Chat app message interactions.
                - type (str): Response type, e.g., "NEW_MESSAGE", "UPDATE_MESSAGE".
                - url (str): URL for configuration.
                - dialogAction (Dict[str, Any]):
                    - actionStatus (Dict[str, Any]):
                        - statusCode (str): Action result status.
                        - userFacingMessage (str): Optional message for the user.
            - accessoryWidgets (List[Dict[str, Any]]): Additional UI elements below the main card or message.
                - decoratedText (Dict[str, Any]):
                    - text (str): Content shown.
                    - startIcon (Dict[str, Any]):
                        - iconUrl (str): URL for the icon image.
            - nextPageToken (Optional[str]): Token for retrieving the next page of results.
        
        Returns an empty dictionary `{"messages": []}` if no messages match or the user has no access.

    Raises:
        TypeError: If any argument is of an incorrect type (e.g., parent is not a string, pageSize is not an int).
        ValueError: If 'parent' is an empty string, 'pageSize' is negative or exceeds 1000,
                    or 'orderBy' is provided with an invalid format or value.
    """
    # --- Input Validation ---
    if not isinstance(parent, str):
        raise TypeError("parent must be a string.")
    if not parent:
        raise ValueError("parent cannot be an empty string.")

    if pageSize is not None:
        if not isinstance(pageSize, int):
            raise TypeError("pageSize must be an integer.")
        if pageSize < 0:
            raise ValueError("pageSize cannot be negative.")
        if pageSize > 1000:
            raise ValueError("pageSize cannot exceed 1000. Maximum is 1000.")

    if pageToken is not None:
        if not isinstance(pageToken, str):
            raise TypeError("pageToken must be a string.")
        try:
            int(pageToken)  # Ensure it can be converted to an integer
        except ValueError:
            raise ValueError("pageToken must be a valid integer.")

    if filter is not None:
        if not isinstance(filter, str):
            raise TypeError("filter must be a string.")

    if orderBy is not None:
        if not isinstance(orderBy, str):
            raise TypeError("orderBy must be a string.")
        normalized_orderBy = orderBy.lower()
        parts = normalized_orderBy.split()
        if not (len(parts) == 2 and parts[0] == "createtime" and parts[1] in ["asc", "desc"]):
            raise ValueError('orderBy, if provided, must be "createTime asc" or "createTime desc".')

    if showDeleted is not None:
        if not isinstance(showDeleted, bool):
            raise TypeError("showDeleted must be a boolean.")
    # --- End of Input Validation ---

    # --- Original Core Logic (adapted where validation now handles errors) ---

    # 1) Check membership
    #    Assumes CURRENT_USER_ID and DB are available in the scope.
    membership_name = f"{parent}/members/{CURRENT_USER_ID.get('id')}" # type: ignore
    user_is_member = any(mem.get("name") == membership_name for mem in DB["Membership"]) # type: ignore
    if not user_is_member:
        # In real usage, you'd raise an error (403). We'll return empty for demonstration.
        return {"messages": []}

    # 2) Default pageSize
    effective_pageSize = pageSize
    if effective_pageSize is None:
        effective_pageSize = 25

    # 3) Convert pageToken to offset
    offset = 0
    if pageToken:
        try:
            offset_val = int(pageToken)
            if offset_val >= 0:
                offset = offset_val
        except ValueError:
            pass

    # 4) Gather messages that belong to 'parent'
    all_msgs = []
    for msg in DB["Message"]: # type: ignore
        if msg.get("name", "").startswith(parent + "/messages/"):
            all_msgs.append(msg)

    # 5) If showDeleted != True, skip messages that have a non-empty deleteTime
    if not showDeleted:
        filtered_msgs = []
        for m in all_msgs:
            if not m.get("deleteTime"):
                filtered_msgs.append(m)
        all_msgs = filtered_msgs

    # 6) Filter parse
    if filter:
        segments = filter.split("AND")

        def matches_filter(msg_obj):
            for seg in segments:
                seg_str = seg.strip()
                seg_lower = seg_str.lower()

                if "thread.name" in seg_lower:
                    if "=" not in seg_str:
                        return False # Invalid filter segment
                    lhs, rhs = seg_str.split("=", 1)
                    rhs_val = rhs.strip().strip('"') # Support quoted values
                    if msg_obj.get("thread", {}).get("name", "") != rhs_val:
                        return False

                if "create_time" in seg_lower: # Use underscore as in docstring example
                    possible_ops = [">=", "<=", ">", "<"] # Order matters for parsing (e.g., >= before >)
                    chosen_op = None
                    for op in possible_ops:
                        if op in seg_str:
                            chosen_op = op
                            break
                    if not chosen_op:
                        return False # Invalid filter segment

                    # Ensure comparison is with create_time not some other field
                    lhs_field_part = seg_str.split(chosen_op, 1)[0].strip().lower()
                    if lhs_field_part != "create_time":
                         return False # Filter condition is not on create_time

                    _, rhs = seg_str.split(chosen_op, 1)
                    compare_time = rhs.strip().strip('"')
                    msg_time = msg_obj.get("createTime", "") # Note: Message object uses "createTime"

                    if not msg_time: return False # Message has no createTime to compare

                    if chosen_op == ">":
                        if not (msg_time > compare_time): return False
                    elif chosen_op == "<":
                        if not (msg_time < compare_time): return False
                    elif chosen_op == ">=":
                        if not (msg_time >= compare_time): return False
                    elif chosen_op == "<=":
                        if not (msg_time <= compare_time): return False
            return True

        filtered_msgs = [m for m in all_msgs if matches_filter(m)]
        all_msgs = filtered_msgs

    # 7) Apply ordering based on orderBy parameter
    if orderBy:
        parts = orderBy.lower().split()
        field = "createTime" # parts[0] is "createtime"
        direction = parts[1] # parts[1] is "asc" or "desc"
        all_msgs.sort(key=lambda x: x.get(field, ""), reverse=(direction == "desc"))
    else:
        all_msgs.sort(key=lambda x: x.get("createTime", ""), reverse=True) # Default sort

    # 8) Apply offset + pageSize
    total = len(all_msgs)
    page_end = offset + effective_pageSize
    page_items = all_msgs[offset:page_end]
    next_token = None
    if page_end < total:
        next_token = str(page_end)

    # 9) Build the response
    response = {"messages": page_items}
    if next_token:
        response["nextPageToken"] = next_token

    return response


def get(name: str) -> Dict[str, Any]:
    """
    Returns details about a message by name.

    The `name` should follow the format: "spaces/{space}/messages/{message}".
    This function performs the following steps:
        1. Parses the space portion from the name.
        2. Checks if the current user is a member of the space.
        3. Finds the message in DB["Message"].
        4. Returns the message if found and authorized, else returns {}.

    Args:
        name (str): Required. Resource name of the message.
            Format: "spaces/{space}/messages/{message}" or
            "spaces/{space}/messages/client-custom-id".

    Returns:
        Dict[str, Any]: A dictionary representing the response with the following structure:

            - messages (List[Dict[str, Any]]): A list of message objects. Each message includes:
                - name (str): Resource name of the message. Format: "spaces/{space}/messages/{message}".
                - createTime (str): RFC-3339 timestamp when the message was created.
                - lastUpdateTime (str): RFC-3339 timestamp of last message update.
                - deleteTime (str): RFC-3339 timestamp when the message was deleted, if applicable.
                - text (str): Plain-text body of the message.
                - formattedText (str): Message text with markup formatting.
                - fallbackText (str): Fallback text for cards.
                - argumentText (str): Message text with app mentions stripped out.
                - threadReply (bool): Indicates if the message is a reply in a thread.
                - clientAssignedMessageId (str): Custom ID assigned to the message, if provided.
                - sender (Dict[str, Any]):
                    - name (str): Resource name of the sender, e.g., "users/123".
                    - displayName (str): Display name of the sender.
                    - domainId (str): Google Workspace domain ID.
                    - type (str): Type of user. One of:
                        - "TYPE_UNSPECIFIED"
                        - "HUMAN"
                        - "BOT"
                    - isAnonymous (bool): Indicates if the sender is deleted or hidden.
                - thread (Dict[str, Any]):
                    - name (str): Resource name of the thread.
                    - threadKey (str): Thread key used to create the thread.
                - space (Dict[str, Any]):
                    - name (str): Resource name of the space.
                    - type (str): Deprecated. Use `spaceType` instead.
                    - spaceType (str): Type of space. One of:
                        - "SPACE"
                        - "GROUP_CHAT"
                        - "DIRECT_MESSAGE"
                    - displayName (str): Optional display name of the space.
                    - externalUserAllowed (bool): Whether external users are allowed.
                    - spaceThreadingState (str): Threading behavior. One of:
                        - "SPACE_THREADING_STATE_UNSPECIFIED"
                        - "THREADED_MESSAGES"
                        - "GROUPED_MESSAGES"
                        - "UNTHREADED_MESSAGES"
                    - spaceHistoryState (str): History configuration. One of:
                        - "HISTORY_STATE_UNSPECIFIED"
                        - "HISTORY_OFF"
                        - "HISTORY_ON"
                    - createTime (str): RFC-3339 timestamp when the space was created.
                    - lastActiveTime (str): RFC-3339 timestamp of last message activity.
                    - importMode (bool): Whether the space was created in import mode.
                    - adminInstalled (bool): Whether the space was created by an admin.
                    - spaceUri (str): Direct URL to open the space.
                    - singleUserBotDm (bool): Whether it's a bot-human direct message.
                    - predefinedPermissionSettings (str): Optional predefined permissions. One of:
                        - "PREDEFINED_PERMISSION_SETTINGS_UNSPECIFIED"
                        - "COLLABORATION_SPACE"
                        - "ANNOUNCEMENT_SPACE"
                    - spaceDetails (Dict[str, Any]):
                        - description (str): Description of the space.
                        - guidelines (str): Rules and expectations.
                    - membershipCount (Dict[str, Any]):
                        - joinedDirectHumanUserCount (int): Count of joined human users.
                        - joinedGroupCount (int): Count of joined groups.
                    - accessSettings (Dict[str, Any]):
                        - accessState (str): One of:
                            - "ACCESS_STATE_UNSPECIFIED"
                            - "PRIVATE"
                            - "DISCOVERABLE"
                        - audience (str): Resource name of discoverable audience, e.g., "audiences/default".
            - annotations (List[Dict[str, Any]]): Rich annotations (e.g., mentions, emojis).
                - type (str): Annotation type. One of: "USER_MENTION", "SLASH_COMMAND", "RICH_LINK", "CUSTOM_EMOJI".
                - startIndex (int): Start position in the message text.
                - length (int): Length of the annotated segment.
                - userMention (Dict[str, Any]): Info about mentioned user.
                    - type (str): Mention type. One of: "ADD", "MENTION".
                - slashCommand (Dict[str, Any]): Slash command metadata.
                    - type (str): Command interaction type.
                    - commandName (str): Command name.
                    - commandId (str): Unique command ID.
                    - triggersDialog (bool): If it opens a dialog.
                - richLinkMetadata (Dict[str, Any]): Rich preview link data.
                    - uri (str): URL.
                    - richLinkType (str): E.g., "DRIVE_FILE", "CHAT_SPACE".
                    - driveLinkData.mimeType (str): File type for drive links.
                    - chatSpaceLinkData (Dict[str, Any]): Chat space linking info.
                        - space (str): Space name.
                        - thread (str): Thread name.
                        - message (str): Message name.
                - customEmojiMetadata (Dict[str, Any]): Custom emoji info.
                    - customEmoji (Dict[str, Any]):
                        - name (str): Server-assigned name (e.g., `customEmojis/emoji_id`).
                        - uid (str): Unique ID.
                        - emojiName (str): Emoji name, e.g., `:fire_emoji:`.
                        - temporaryImageUri (str): Temporary image URL.

            - cards (List[Dict[str, Any]]): Legacy UI cards shown in Chat messages.
                - name (str): Identifier for the card.
                - header (Dict[str, Any]): Optional card header.
                    - title (str): Required. Title text.
                    - subtitle (str): Optional subtitle text.
                    - imageUrl (str): Optional header image URL.
                    - imageStyle (str): "IMAGE" or "AVATAR".
                - sections (List[Dict[str, Any]]): Content sections within the card.
                    - header (str): Optional section header.
                    - widgets (List[Dict[str, Any]]): List of visual elements such as text, buttons, images.
                        - textParagraph (Dict[str, Any]): A block of text.
                            - text (str): The paragraph content.
                        - keyValue (Dict[str, Any]): Key-value styled layout.
                            - topLabel (str): Top label.
                            - content (str): Content.
                            - bottomLabel (str): Bottom label.
                            - icon (str): Icon.
                            - iconUrl (str): Icon URL.
                        - image (Dict[str, Any]): Standalone image.
                            - imageUrl (str): Image URL.
                            - aspectRatio (float): Aspect ratio.
                        - buttons (List[Dict[str, Any]]): Button elements for interaction.
                - cardActions (List[Dict[str, Any]]): Actions at the bottom of the card.
                    - actionLabel (str): Text shown for the action.
                    - onClick (Dict[str, Any]): Action handler.
                        - openLink (Dict[str, Any]): URL to open.
                        - action (Dict[str, Any]): Invokes a defined method.
                - fixedFooter (Dict[str, Any]): Optional persistent footer.
                    - primaryButton (Dict[str, Any]): Button element.
                        - text (str): Text.
                        - disabled (bool): Disabled.
                        - altText (str): Alt text.
                        - type (str): Type.
            - cardsV2 (List[Dict[str, Any]]): New generation cards with structured layouts.
                - cardId (str): Identifier used to update this card.
                - card (Dict[str, Any]): Complete structure including headers, sections, actions, and footers.

            - attachment (List[Dict[str, Any]]): Message attachments, such as files.
                - name (str): Attachment resource name.
                - contentName (str): File name.
                - contentType (str): MIME type.
                - thumbnailUri (str): Thumbnail preview image.
                - downloadUri (str): Direct download URL.
                - source (str): One of: "DRIVE_FILE", "UPLOADED_CONTENT".
                - attachmentDataRef (Dict[str, Any]): For uploading files.
                    - resourceName (str): Reference to the media.
                    - attachmentUploadToken (str): Token for uploaded content.
                - driveDataRef (Dict[str, Any]): Drive file metadata.
                    - driveFileId (str): ID of the file in Google Drive.

            - matchedUrl (Dict[str, Any]): Metadata for previewable URLs.
                - url (str): The matched link.

            - emojiReactionSummaries (List[Dict[str, Any]]): Summary of emoji reactions.
                - reactionCount (int): Total count of reactions.
                - emoji (Dict[str, Any]):
                    - unicode (str): The emoji used.

            - deletionMetadata (Dict[str, Any]): Deletion details.
                - deletionType (str): Who deleted it. One of: "CREATOR", "ADMIN", etc.

            - quotedMessageMetadata (Dict[str, Any]): Metadata of quoted messages.
                - name (str): Quoted message resource name.
                - lastUpdateTime (str): Timestamp of last update.

            - attachedGifs (List[Dict[str, Any]]): List of attached GIF previews.
                - uri (str): URL to the GIF image.

            - actionResponse (Dict[str, Any]): Data returned by Chat app message interactions.
                - type (str): Response type, e.g., "NEW_MESSAGE", "UPDATE_MESSAGE".
                - url (str): URL for configuration.
                - dialogAction (Dict[str, Any]):
                    - actionStatus (Dict[str, Any]):
                        - statusCode (str): Action result status.
                        - userFacingMessage (str): Optional message for the user.

            - accessoryWidgets (List[Dict[str, Any]]): Additional UI elements below the main card or message.
                - decoratedText (Dict[str, Any]):
                    - text (str): Content shown.
                    - startIcon (Dict[str, Any]):
                        - iconUrl (str): URL for the icon image.

            - privateMessageViewer (Dict[str, Any]): Viewer for private messages.
                - name (str): User resource name who can view the message (e.g., "users/123").

            - slashCommand (Dict[str, Any]): Slash command info when used to create a message.
                - commandId (str): ID of the executed slash command.

            - nextPageToken (Optional[str]): Token for retrieving the next page of results.

        Returns an empty dictionary `{}` if no messages match or the user has no access.
    """
    print_log(
        f"get_message called with name={name}, CURRENT_USER_ID={CURRENT_USER_ID.get('id')}"
    )

    # 1) Parse out the space portion from name => "spaces/AAA" is the first 2 segments
    parts = name.split("/")
    if len(parts) < 4:
        print_log("Error: invalid message name format.")
        return {}
    # expected: ["spaces", "AAA", "messages", "MESSAGE_ID"]
    # so the space name is e.g. "spaces/AAA" from the first 2 elements
    space_name = "/".join(parts[:2])  # => "spaces/AAA"

    # 2) Check membership => "spaces/AAA/members/{CURRENT_USER_ID}"
    membership_name = f"{space_name}/members/{CURRENT_USER_ID.get('id')}"
    is_member = any(m.get("name") == membership_name for m in DB["Membership"])
    if not is_member:
        print_log(
            f"Caller {CURRENT_USER_ID.get('id')} is not a member of {space_name} => no permission."
        )
        return {}

    # 3) Find the message
    found_msg = None
    for msg in DB["Message"]:
        if msg.get("name") == name:
            found_msg = msg
            break

    # 4) Return the message or {}
    if not found_msg:
        print_log(f"No message found with name={name}")
        return {}

    print_log(f"Found message: {found_msg}")
    return found_msg


def update(name: str, updateMask: str, allowMissing: bool, body: dict) -> dict:
    """
    Updates a message in a Google Chat space or creates a new one if allowed.

    Args:
        name (str): Required. Resource name of the message to update. Format:
            `spaces/{space}/messages/{message}`. If using a client-assigned ID,
            use `spaces/{space}/messages/client-{custom_id}`.
        updateMask (str): Required. Comma-separated list of fields to update. Use `"*"` to update all fields.
            Valid fields: "text", "attachment", "cards", "cards_v2", "accessory_widgets".
        allowMissing (bool): Optional. If True and the message is not found, creates a new message
            (only allowed with a client-assigned message ID).
        body (dict): Required. The message fields to apply updates to. May include any of the following keys:
            - text (str): The plain-text message body.
            - attachment (List[dict]): List of attachments.
            - cards (List[dict]): Legacy UI card structure.
            - cardsV2 (List[dict]): Enhanced modern card structure.
            - accessoryWidgets (List[dict]): Interactive widgets shown below the message.

    Returns:
        dict: The updated or newly created message resource. Fields include:

            - name (str)
            - createTime (str)
            - lastUpdateTime (str)
            - deleteTime (str)
            - text (str)
            - formattedText (str)
            - fallbackText (str)
            - argumentText (str)
            - threadReply (bool)
            - clientAssignedMessageId (str)
            - sender (dict):
                - name (str)
                - displayName (str)
                - domainId (str)
                - type (str): One of "HUMAN", "BOT"
                - isAnonymous (bool)
            - annotations (List[dict]):
                - type (str)
                - startIndex (int)
                - length (int)
                - userMention, slashCommand, richLinkMetadata, customEmojiMetadata (dicts with respective subfields)
            - cards (List[dict]):
                - header (dict): title, subtitle, imageStyle, imageUrl
                - sections (List[dict]):
                    - header (str)
                    - widgets (List[dict]): textParagraph, image, keyValue, buttons
                - cardActions (List[dict])
            - cardsV2 (List[dict]):
                - cardId (str)
                - card (dict):
                    - name (str)
                    - displayStyle (str)
                    - header (dict): title, subtitle, imageType, imageUrl, imageAltText
                    - sectionDividerStyle (str)
                    - sections (List[dict]):
                        - header (str)
                        - collapsible (bool)
                        - uncollapsibleWidgetsCount (int)
                        - widgets (List[dict]): textParagraph, image, decoratedText, keyValue, grid, columns,
                            chipList, selectionInput, textInput, dateTimePicker, divider, carousel
                    - cardActions (List[dict]): openLink, action, overflowMenu
                    - fixedFooter (dict):
                        - primaryButton (dict): text, disabled, altText, type, icon, color
            - attachment (List[dict]):
                - name (str)
                - contentName (str)
                - contentType (str)
                - thumbnailUri (str)
                - downloadUri (str)
                - source (str)
                - attachmentDataRef (dict): resourceName, attachmentUploadToken
                - driveDataRef (dict): driveFileId
            - matchedUrl (dict): url (str)
            - emojiReactionSummaries (List[dict]):
                - reactionCount (int)
                - emoji (dict): unicode (str)
            - deletionMetadata (dict): deletionType (str)
            - quotedMessageMetadata (dict):
                - name (str)
                - lastUpdateTime (str)
            - attachedGifs (List[dict]): uri (str)
            - actionResponse (dict):
                - type (str)
                - url (str)
                - updatedWidget (dict): widget (str), suggestions (dict with items)
                - dialogAction (dict): actionStatus (dict): statusCode, userFacingMessage
            - accessoryWidgets (List[dict]):
                - buttonList (dict): buttons (List[dict])
            - privateMessageViewer (dict): name (str)
            - slashCommand (dict): commandId (str)
            - thread (dict):
                - name (str)
                - threadKey (str)
            - space (dict):
                - name (str)
                - type (str) [Deprecated]
                - spaceType (str)
                - singleUserBotDm (bool)
                - threaded (bool) [Deprecated]
                - displayName (str)
                - externalUserAllowed (bool)
                - spaceThreadingState (str)
                - spaceHistoryState (str)
                - importMode (bool)
                - createTime (str)
                - lastActiveTime (str)
                - adminInstalled (bool)
                - spaceUri (str)
                - predefinedPermissionSettings (str)
                - spaceDetails (dict): description, guidelines
                - membershipCount (dict): joinedDirectHumanUserCount, joinedGroupCount
                - accessSettings (dict): accessState, audience

            Returns `{}` if the message is not found and allowMissing is False, or on invalid parameters.
    """

    print_log(
        f"update_message called: name={name}, updateMask={updateMask}, allowMissing={allowMissing}"
    )

    # 1) Look for existing message
    existing = None
    for msg in DB["Message"]:
        if msg["name"] == name:
            existing = msg
            break

    # 2) If not found => maybe create if allowMissing and client-assigned ID
    if not existing:
        if allowMissing:
            # The doc: "If `true` and the message isn't found, a new message is created and `updateMask` is ignored.
            #           The specified message ID must be client-assigned or the request fails."
            # So we check if the last path segment starts with "client-"
            parts = name.split("/")
            if len(parts) < 4 or parts[2] != "messages":
                print_log("Invalid name format.")
                return {}
            msg_id = parts[3]  # e.g. "client-xyz"

            if not msg_id.startswith("client-"):
                print_log("Not found, allowMissing=True but ID isn't client- => fail.")
                return {}

            print_log("Message not found => create new with client ID.")
            # create minimal new message
            existing = {
                "name": name,
                "text": "",
                "attachment": [],
            }
            DB["Message"].append(existing)
        else:
            print_log("Message not found, allowMissing=False => can't update.")
            return {}

    # 3) Parse updateMask
    valid_fields = ["text", "attachment", "cards", "cards_v2", "accessory_widgets"]
    if updateMask.strip() == "*":
        fields_to_update = valid_fields
    else:
        fields_to_update = [f.strip() for f in updateMask.split(",")]

    # 4) Apply updates from request body
    for field in fields_to_update:
        if field not in valid_fields:
            print_log(f"Skipping unknown or unsupported field '{field}'.")
            continue

        # Note: doc says "cards_v2", but in code we might store it as "cardsV2".
        # We'll unify the naming so that "cards_v2" from doc => "cardsV2" in DB.
        if field == "cards_v2":
            internal_field = "cardsV2"
        else:
            internal_field = field

        # If the body has that field, update. If not, skip it.
        if field in body or internal_field in body:
            # If body uses "cards_v2", we do body.get(field) or body.get(internal_field).
            new_val = body.get(field, body.get(internal_field))
            existing[internal_field] = new_val

    print_log(f"Updated message => {existing}")
    return existing


def patch(
    name: str, updateMask: str, allowMissing: Optional[bool] = None, message: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Updates an existing message resource using the PATCH method.

    This method updates the fields of a Chat message identified by its resource
    name. It supports partial updates via the `updateMask` parameter. If the message
    is not found and `allowMissing` is True, a new message is created (requires a
    client-assigned message ID).

    Args:
        name (str): Required. Resource name of the message to update.
            Format: `spaces/{space}/messages/{message}`.
            Examples:
            - `spaces/AAA/messages/BBB.CCC`
            - `spaces/AAA/messages/client-custom-name`
            See: https://developers.google.com/workspace/chat/create-messages#name_a_created_message
        updateMask (str): Required. Comma-separated list of fields to update, or `*` for all.
            Supported values include:
            - `text`
            - `attachment`
            - `cards`
            - `cards_v2`
            - `accessory_widgets`
        allowMissing (Optional[bool]): Optional. If True, creates the message if not found (requires a
            client-assigned ID). Ignores `updateMask` in that case.
        message (Optional[Dict[str, Any]]): A dictionary representing the fields of the message to update.
            Possible keys include:
            - `text` (str): Plain-text body of the message.
            - `fallbackText` (str): Fallback text for message cards.
            - `cards` (List[Dict[str, Any]]): List of cards to include in the message.
            - `cards_v2` (List[Dict[str, Any]]): List of version 2 cards (advanced formatting).
            - `attachment` (List[Dict[str, Any]]): Attachments such as files or media.
            - `thread` (Dict[str, Any]): Thread info, including `name` or `threadKey`.
            - `annotations` (List[Dict[str, Any]]): Annotations like user mentions, rich links, etc.
            - `clientAssignedMessageId` (str): Optional custom ID to identify the message.

    Returns:
        Dict[str, Any]: A dictionary representing the updated message resource. The response may include:
            - `name` (str): Resource name of the message.
            - `text` (str): Updated plain-text body of the message.
            - `createTime` (str): Time at which the message was created.
            - `lastUpdateTime` (str): Time at which the message was last edited.
            - `deleteTime` (str): Time at which the message was deleted.
            - `formattedText` (str): Text with formatting markup.
            - `fallbackText` (str): Fallback plain-text for message cards.
            - `argumentText` (str): Message text without mentions.
            - `threadReply` (bool): Whether this is a reply in a thread.
            - `clientAssignedMessageId` (str): Custom ID for the message.
            - `sender` (Dict[str, Any]): Information about the user who sent the message:
                - `name` (str)
                - `displayName` (str)
                - `domainId` (str)
                - `type` (str)
                - `isAnonymous` (bool)
            - `cards` (List[Dict[str, Any]]): List of legacy card widgets.
            - `cardsV2` (List[Dict[str, Any]]): List of enhanced card widgets with layout and interaction.
            - `annotations` (List[Dict[str, Any]]): Metadata like mentions, emojis, rich links.
            - `thread` (Dict[str, Any]): Thread information such as:
                - `name` (str)
                - `threadKey` (str)
            - `space` (Dict[str, Any]): Space info:
                - `name` (str)
                - `type` (str)
                - `spaceType` (str)
                - `displayName` (str)
                - `threaded` (bool)
                - `spaceHistoryState` (str)
                - `externalUserAllowed` (bool)
                - `adminInstalled` (bool)
                - `spaceUri` (str)
                - and other space-level configuration and metadata
            - `attachment` (List[Dict[str, Any]]): Attachments such as files or Drive links.
            - `emojiReactionSummaries` (List[Dict[str, Any]]): List of emoji reaction metadata.
            - `quotedMessageMetadata` (Dict[str, Any]): Info about quoted messages.
            - `matchedUrl` (Dict[str, Any]): URLs detected in the message.
            - `actionResponse` (Dict[str, Any]): App-level response types, URLs, or dialog triggers.
            - `deletionMetadata` (Dict[str, Any]): Who deleted the message and how.
            - `accessoryWidgets` (List[Dict[str, Any]]): Optional accessory widgets for enhanced display.
            - Other fields may be present depending on usage and configuration.

        For complete field definitions, see:
        https://developers.google.com/workspace/chat/api/reference/rest/v1/spaces.messages/patch

    """
    print_log(
        f"Patching message {name} with updateMask={updateMask}, "
        f"allowMissing={allowMissing}, message={message}"
    )
    
    # Call update method with the same parameters for simplicity
    # In a real implementation, there might be differences between update and patch
    return update(name=name, updateMask=updateMask, allowMissing=allowMissing, body=message or {})


def delete(name: str, force: bool = None) -> None:
    """
    Deletes a message.

    Args:
        name (str): Required. Resource name of the message.
            Format: `spaces/{space}/messages/{message}`.
            If you've set a custom ID for your message, you can use the value from
            the `clientAssignedMessageId` field for `{message}`. For details, see
            https://developers.google.com/workspace/chat/create-messages#name_a_created_message
        force (bool, optional): When `true`, deleting a message also deletes its threaded
            replies. When `false`, if the message has threaded replies, deletion fails.
            Only applies when authenticating as a user. Has no effect when authenticating
            as a Chat app.

    Returns:
        None: This method does not return a value. Simulates an empty response by returning
        an empty dictionary internally, but the return type is `None`.
    """

    print_log(f"delete_message called with name={name}, force={force}")

    # 1) Locate the message
    target_msg = None
    for idx, m in enumerate(DB["Message"]):
        if m.get("name") == name:
            target_msg = m
            target_idx = idx
            break

    if not target_msg:
        print_log("Message not found => returning empty.")
        return {}

    # 2) Check for threaded replies. We'll say a "reply" is any message whose
    #    thread references target_msg["name"] as "thread.parent"
    message_threads = target_msg.get("thread", {}).get("name", "")
    replies = []
    for m in DB["Message"]:
        thread = m.get("thread", {})
        if thread.get("name") == message_threads:
            replies.append(m)

    if replies and replies != [target_msg]:  # Don't count the target message itself as a reply
        # We have threaded replies
        if not force:
            # fail => can't delete this parent
            print_log(f"Message {name} has replies => need force=true => fail.")
            return {}
        else:
            # force=true => remove the replies too
            for r in replies:
                # Ensure we don't remove the target message itself in this loop
                if r != target_msg:
                    DB["Message"].remove(r)
                    print_log(f"Deleted reply => {r['name']}")

    # 3) Remove the target message (if it wasn't already removed as a reply)
    DB["Message"].remove(target_msg)
    print_log(f"Message {name} deleted.")
    return {}  # simulating an Empty response

