"""
Conversations resource for Slack API simulation.

This module provides functionality for managing conversations (channels) in Slack.
It simulates the conversations-related endpoints of the Slack API.
"""
import time
import hashlib
import random
import string
import base64
from typing import Dict, Any, Optional, List

from .SimulationEngine.custom_errors import (
    ChannelNameMissingError,
    ChannelNameTakenError,
    InvalidLimitError,
    InvalidCursorValueError,
    InvalidUserError,
    TimestampError,
    ChannelNotFoundError,
    MessageNotFoundError,
    CursorOutOfBoundsError,
    UserNotInConversationError,
    MissingUserIDError,
    NotAllowedError,
    MissingPurposeError,
    CurrentUserNotSetError,
)
from .SimulationEngine.db import DB
from .SimulationEngine import utils

def leave(user_id: str, channel: str) -> Dict[str, Any]:
    """
    Leaves a conversation.

    Args:
        user_id (str): User ID of the user leaving the conversation.
        channel (str): Conversation to leave.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - ok (bool): True if the operation was successful.

    Raises:
        TypeError: If 'user_id' or 'channel' is not a string.
        ValueError: If 'user_id' or 'channel' is an empty string.
        ChannelNotFoundError: If the specified 'channel' does not exist in the DB.
        UserNotInConversationError: If the 'user_id' is not a member of the 'channel's' conversation.
    """
    # --- Start of Added Validation Logic ---
    if not isinstance(user_id, str):
        raise TypeError(f"user_id must be a string, got {type(user_id).__name__}.")
    if not user_id:  # Check for empty string after type check
        raise ValueError("user_id cannot be empty.")

    if not isinstance(channel, str):
        raise TypeError(f"channel must be a string, got {type(channel).__name__}.")
    if not channel:  # Check for empty string after type check
        raise ValueError("channel cannot be empty.")
    # --- End of Added Validation Logic ---

    if channel not in DB.get("channels", {}):
        raise ChannelNotFoundError(f"Channel '{channel}' not found.")

    current_channel_data = DB["channels"][channel]
    
    if user_id not in current_channel_data['conversations']["members"]:
        raise UserNotInConversationError(f"User '{user_id}' is not in conversation '{channel}'.")

    current_channel_data['conversations']["members"].remove(user_id)
    return {"ok": True}

def invite(channel: str, users: str, force: bool = False) -> Dict[str, Any]:
    """
    Invites users to a channel.

    Args:
        channel (str): The ID of the channel to invite users to. Must be a non-empty string.
        users (str): A comma separated list of user IDs. Must be a non-empty string.
        force (bool): Continue inviting valid users even if some are invalid. Defaults to False.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - ok (bool): Whether the operation was successful
            - channel (str): Channel ID
            - invited (list): List of successfully invited user IDs
            - invalid_users (Optional[List[str]]): List of invalid user IDs if force is False and errors occur.

    Raises:
        TypeError: If 'channel' or 'users' is not a string or If 'force' is not a boolean.
        ValueError: If 'channel' or 'users' is an empty string.
        InvalidUserError: If any user is not present in the DB and force is false.
        ChannelNotFoundError: If the channel does not exist in the DB.

    """
    # --- Input Validation ---
    if not isinstance(channel, str):
        raise TypeError(f"Argument 'channel' must be a string, but got {type(channel).__name__}")
    if not channel:
        raise ValueError("Argument 'channel' cannot be an empty string.")

    if not isinstance(users, str):
        raise TypeError(f"Argument 'users' must be a string, but got {type(users).__name__}")
    if not users:
        raise ValueError("Argument 'users' cannot be an empty string.")

    if not isinstance(force, bool):
        raise TypeError(f"Argument 'force' must be a boolean, but got {type(force).__name__}")
    # --- End Input Validation ---

    # --- Original Core Logic ---
    user_list = users.split(",")
    valid_users = []
    invalid_users = []

    for user_id in user_list:
        user_id = user_id.strip() # Strip whitespace
        if user_id in DB.get("users", set()):
            valid_users.append(user_id)
        else:
            invalid_users.append(user_id)

    if not force and invalid_users:
        # This is an operational error based on DB content, not initial validation
        raise InvalidUserError('invalid user found.')

    if channel not in DB.get("channels", {}):
         # This is an operational error based on DB content
         raise ChannelNotFoundError("channel not found.")

    # Ensure conversations and members exist (modifying the assumed DB structure)
    channel_data = DB["channels"][channel]
    if 'members' not in channel_data['conversations']:
       channel_data['conversations']['members'] = []

    current_members = set(channel_data['conversations']['members'])
    added_users = []
    for user_id in valid_users:
        if user_id not in current_members:
            channel_data['conversations']['members'].append(user_id)
            added_users.append(user_id)
            current_members.add(user_id) # Update set for efficiency if many users

    return_payload = {"ok": True, "channel": channel, "invited": added_users}
    if invalid_users:
        return_payload["invalid_users"] = invalid_users
    return return_payload

def archive(channel: str) -> Dict[str, Any]:
    """
    Archives a conversation by setting its archived status and closing it.

    Archiving a conversation marks it as archived (is_archived=True) and closes it 
    (is_open=False) in the database. Archived conversations are typically hidden 
    from regular channel lists and are no longer actively used.

    Args:
        channel (str): ID of conversation to archive. Must be a non-empty string.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - ok (bool): Always True if the operation completes successfully.

    Raises:
        TypeError: If 'channel' is not a string.
        ValueError: If 'channel' is an empty string.
        ChannelNotFoundError: If the specified 'channel' does not exist in the database.
        RuntimeError: If the internal database structure for the channel is invalid 
                     (channel data is not a dictionary).
    """
    # 1. Input Validation
    if not isinstance(channel, str):
        raise TypeError(f"Argument 'channel' must be a string, got {type(channel).__name__}.")
    if not channel:  # Handles empty string
        raise ValueError("Argument 'channel' cannot be an empty string.")

    # 2. Core Logic (pre-condition check for channel existence)
    # This part assumes DB is accessible.
    if channel not in DB.get("channels", {}): # Defensive get for "channels" key
        raise ChannelNotFoundError(f"Channel '{channel}' not found.")

    # Ensure the channel entry is a dictionary before trying to set keys
    if not isinstance(DB["channels"][channel], dict):
        # This case indicates an unexpected DB structure, which might be an internal error.
        raise RuntimeError(f"Internal error: Channel data for '{channel}' is not a dictionary.")

    DB["channels"][channel]["is_archived"] = True
    DB["channels"][channel]["is_open"] = False
    
    return {"ok": True}

def join(user_id: str, channel: str) -> Dict[str, Any]:
    """
    Joins an existing conversation.

    Args:
        user_id (str): User ID of the user joining the conversation.
        channel (str): ID of conversation to join.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - ok (bool): Whether the operation was successful (False if user is already in channel)
            - channel (str): Channel ID

    Raises:
        TypeError: If 'user_id' or 'channel' is not a string.
        MissingUserIDError: If 'user_id' is an empty string.
        ChannelNameMissingError: If 'channel' is an empty string.
        ChannelNotFoundError: If the specified 'channel' does not exist in the DB.
    """
    # --- Input Validation Logic ---
    if not isinstance(user_id, str):
        raise TypeError(f"user_id must be a string.")
    if not user_id:  # Check for empty string after type check
        raise MissingUserIDError("user_id cannot be empty.")

    if not isinstance(channel, str):
        raise TypeError(f"channel must be a string.")
    if not channel:  # Check for empty string after type check
        raise ChannelNameMissingError("channel cannot be empty.")
    # --- End of Input Validation Logic ---

    if channel not in DB.get("channels", {}):
        raise ChannelNotFoundError(f"Channel '{channel}' not found.")

    # Ensure conversations and members exist
    DB["channels"][channel].setdefault('conversations', {})
    DB["channels"][channel]['conversations'].setdefault('members', [])

    if user_id in DB["channels"][channel]['conversations']["members"]:
        return {"ok":False, "channel": channel}

    DB["channels"][channel]['conversations']["members"].append(user_id)
    return {"ok": True, "channel": channel}

def kick(channel: str, user_id: str) -> Dict[str, bool]:
    """
    Removes a user from a conversation.

    Args:
        channel (str): ID of conversation to remove user from.
        user_id (str): ID of user to remove from conversation.

    Returns:
        Dict[str, bool]: A dictionary containing:
            - ok (bool): Whether the operation was successful
    
    Raises:
        TypeError: If 'channel' or 'user_id' is not a string.
        ChannelNameMissingError: If 'channel' is an empty string.
        MissingUserIDError: If 'user_id' is an empty string.
        ChannelNotFoundError: If the specified 'channel' does not exist in the DB.
        UserNotInConversationError: If the 'user_id' is not a member of the 'channel's' conversation.
        PermissionError: If the current user is not an admin or not in the channel.
    """
    # --- Input Validation ---
    if not isinstance(channel, str):
        raise TypeError(f"channel must be a string.")

    if not isinstance(user_id, str):
        raise TypeError(f"user_id must be a string.")  
    if not channel:
        raise ChannelNameMissingError("channel cannot be empty.")
    if not user_id:
        raise MissingUserIDError("user_id cannot be empty.")

    if channel not in DB["channels"]:
        raise ChannelNotFoundError(f"Channel '{channel}' not found.")

    # Ensure conversations and members exist
    DB["channels"][channel].setdefault('conversations', {})
    DB["channels"][channel]['conversations'].setdefault('members', [])

    if user_id not in DB["channels"][channel]['conversations']["members"]:
        raise UserNotInConversationError(f"User '{user_id}' is not in conversation '{channel}'.")

    if DB["current_user"]["id"] not in DB["channels"][channel]['conversations']["members"]:
        raise PermissionError("You are not authorized to remove users from this channel.")

    if DB["current_user"]["is_admin"] is False:
        raise PermissionError("You are not authorized to remove users from this channel.")

    DB["channels"][channel]['conversations']["members"].remove(user_id)
    return {"ok": True}

def mark_read(channel: str, ts: str) -> Dict[str, bool]:
    """
    Sets the read cursor in a channel.

    Args:
        channel (str): Channel or conversation ID.
        ts (str): Timestamp of the message to mark as read.

    Returns:
        Dict[str, bool]: A dictionary containing:
            - ok (bool): Whether the operation was successful

    Raises:
        TypeError: If 'channel' or 'ts' is not a string.
        TimestampError: If 'ts' is an empty string or not in valid timestamp format. Required Format : Unix timestamp with fractional seconds (e.g. "1678886400.000000")
        MissingChannelError: If 'channel' is an empty string.
        ChannelNotFoundError: If the specified 'channel' does not exist in the DB.
    """
    if not isinstance(channel, str):
        raise TypeError("channel must be a string.")
    if not channel:
        raise ChannelNameMissingError("channel cannot be empty.")

    if not isinstance(ts, str):
        raise TypeError("ts must be a string.")
    if not ts:
        raise TimestampError("timestamp cannot be empty.")

    try:
        float(ts)
    except ValueError:
        raise TimestampError("timestamp is not a valid timestamp.")

    # Simulate setting the read cursor
    if channel not in DB["channels"]:
        raise ChannelNotFoundError(f"Channel '{channel}' not found.")

    if DB["current_user"]["id"] not in DB["channels"][channel]['conversations']["members"]:
        raise UserNotInConversationError("Current user is not a member of this channel.")

    DB["channels"][channel]['conversations']["read_cursor"] = ts
    return {"ok": True}

def history(
    channel: str,
    cursor: Optional[str] = None,
    include_all_metadata: bool = False,
    inclusive: bool = False,
    latest: Optional[str] = None,
    limit: int = 100,
    oldest: str = "0",
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetches a conversation's history of messages and events.

    Args:
        channel (str): Conversation ID. Must be a non-empty string.
        cursor (Optional[str]): Pagination cursor. Defaults to None. If provided, must be a base64-encoded string
            with the format "user:{user_id}" (e.g., "dXNlcjpleGFtcGxlSWQxMjM=" for "user:exampleId123").
            This matches Slack's cursor format for consistent pagination.
        include_all_metadata (bool): Return all metadata. Defaults to False. Must be a boolean.
        inclusive (bool): Include messages with oldest/latest timestamps.
            Defaults to False.
        latest (Optional[str]): Only messages before this timestamp.
            Defaults to None (current time). If provided, must be a string in Unix timestamp format
            with exactly 6 decimal places for microsecond precision (e.g. "1688683055.556679").
            The timestamp must be a valid Unix timestamp that can be converted to a float.
        limit (int): Maximum number of items to return. Defaults to 100. Must be an integer between 1 and 999.
        oldest (str): Only messages after this timestamp. Defaults to "0". Must be a string in Unix timestamp format
            with exactly 6 decimal places for microsecond precision (e.g. "1688683055.556679").
            The timestamp must be a valid Unix timestamp that can be converted to a float.
        user_id (Optional[str]): If provided, only messages whose ``user`` field matches this ID will be
            returned. Useful for filtering messages sent by a specific user.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - ok (bool): Whether the operation was successful
            - messages (List[Dict[str, Any]]): List of message objects, where each message contains:
                - ts (str): Message timestamp in Unix format with exactly 6 decimal places for microsecond precision
                - user (str): User ID who sent the message
                - text (str): Message content
                - reactions (List[Dict[str, Any]]): List of reaction objects, where each reaction contains:
                    - name (str): Emoji name of the reaction
                    - users (List[str]): List of user IDs who reacted
                    - count (int): Number of users who reacted
            - has_more (bool): Whether there are more messages to fetch
            - response_metadata (Dict[str, Optional[str]]): Pagination metadata containing:
                - next_cursor (Optional[str]): Cursor for next page of results, in base64-encoded format
                    with the format "user:{user_id}" (e.g., "dXNlcjpleGFtcGxlSWQxMjM=")

    Raises:
        TypeError: If any argument is of an incorrect type.
        ValueError: If 'channel' is an empty string.
        InvalidLimitError: If 'limit' is not an integer between 1 and 999 (inclusive).
        ChannelNotFoundError: If channel is not found
        TimestampError: If `oldest` or `latest` timestamps are invalid or not in the correct format
        InvalidCursorValueError: If 'cursor' is provided but cannot be decoded properly.
    """
    # --- Input Validation ---
    if not isinstance(channel, str):
        raise TypeError("channel must be a string.")
    if not channel:
        raise ValueError("channel cannot be empty.")

    if cursor is not None and not isinstance(cursor, str):
        raise TypeError("cursor must be a string if provided.")

    if not isinstance(include_all_metadata, bool):
        raise TypeError("include_all_metadata must be a boolean.")

    if not isinstance(inclusive, bool):
        raise TypeError("inclusive must be a boolean.")

    if latest is not None and not isinstance(latest, str):
        raise TypeError("latest must be a string if provided.")

    if not isinstance(limit, int):
        raise TypeError("limit must be an integer.")
    if not (1 <= limit <= 999):
        raise InvalidLimitError("limit must be an integer between 1 and 999, inclusive.")

    if not isinstance(oldest, str):
        raise TypeError("oldest must be a string.")

    if user_id is not None and not isinstance(user_id, str):
        raise TypeError("user_id must be a string if provided.")
    # --- End of Input Validation ---

    # Check if channels key exists in DB
    if "channels" not in DB:
        raise ChannelNotFoundError(f"Channel '{channel}' not found")
        
    if channel not in DB["channels"]:
        raise ChannelNotFoundError(f"Channel '{channel}' not found")

    # Validate timestamp formats
    try:
        if latest is not None:
            float(latest)
        float(oldest)
    except ValueError:
        raise TimestampError("Invalid timestamp format")

    # Simulate fetching history from DB
    if "messages" not in DB["channels"][channel]:
        DB["channels"][channel]["messages"] = []

    channel_history = DB["channels"][channel]["messages"]

    # Filter by timestamp
    current_latest_ts = latest
    if current_latest_ts is None:
        current_latest_ts = str(time.time())

    # Ensure timestamps are float-convertible before comparison
    if inclusive:
        filtered_history = [
            message for message in channel_history
            if float(oldest) <= float(message['ts']) <= float(current_latest_ts)
        ]
    else:
        filtered_history = [
            message for message in channel_history
            if float(oldest) < float(message['ts']) < float(current_latest_ts)
        ]

    # Filter messages by user_id if requested
    if user_id is not None:
        filtered_history = [m for m in filtered_history if m.get('user') == user_id]

    # Apply limit and cursor
    start_index = 0
    if cursor:
        try:
            decoded_cursor = base64.b64decode(cursor).decode('utf-8')
        except (base64.binascii.Error, UnicodeDecodeError):
            raise InvalidCursorValueError("Invalid base64 cursor format")
        if not decoded_cursor.startswith('user:'):
            raise InvalidCursorValueError("Invalid cursor format")
        user_id = decoded_cursor[5:]
        # Find the first message from this user
        try:
            start_index = next(i for i, v in enumerate(filtered_history) if v['user'] == user_id) + 1
        except StopIteration:
            raise InvalidCursorValueError(f"User ID {user_id} not found in message history")

    end_index = min(start_index + limit, len(filtered_history))
    messages_page = filtered_history[start_index:end_index]

    next_page_cursor = None
    if end_index < len(filtered_history) and messages_page:
        last_message_user = messages_page[-1]['user']
        next_page_cursor = base64.b64encode(f"user:{last_message_user}".encode('utf-8')).decode('utf-8')

    response = {
        "ok": True,
        "messages": messages_page,
        "has_more": end_index < len(filtered_history),
        "response_metadata": {"next_cursor": next_page_cursor}
    }

    return response

def open_conversation(
    channel: Optional[str] = None,
    prevent_creation: bool = False,
    return_im: bool = False,
    users: Optional[str] = None
) -> Dict[str, Any]:
    """
    Opens or resumes a direct message or multi-person direct message.

    This function opens or resumes a conversation between users. When return_im=False (default),
    the function returns minimal channel information containing only the channel ID. When return_im=True,
    it returns the full channel object with all metadata. The function can either resume an existing
    conversation by channel ID or create a new one with specified users.


    Note: Returns existing conversation if same user combination already exists. When creating a new conversation 
    with the `users` parameter, the current user is automatically included in the conversation. You don't need to 
    explicitly include the current user in the users list.


    Args:
        channel (Optional[str]): Resume a conversation by supplying a channel ID.
            Supply either this OR users, not both. Defaults to None.
        prevent_creation (bool): Set to True to prevent creating a new conversation if one doesn't exist.
            Defaults to False.
        return_im (bool): If True, returns the full channel definition including all metadata.
            If False, returns minimal channel information (just ID). Defaults to False.
        users (Optional[str]): Comma-separated list of user IDs to include in the conversation.
            The current user will be automatically included if not already in the list.
            Supply either this OR channel, not both. Defaults to None.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - ok (bool): Whether the operation was successful (always True for success)
            - channel (Dict[str, Any]): Channel information. Content varies based on return_im parameter:

                When `return_im` is False:
                - id (str): Channel ID

                When `return_im` is True:
                - id (str): Channel ID
                - name (str): Channel name (comma-separated, sorted user list)
                - is_private (bool): Whether conversation is private (True for DMs/MPDMs)
                - conversations (Dict[str, Any]): Conversation metadata including:
                    - id (str): Conversation ID (same as channel ID)
                    - members (List[str]): List of user IDs for all conversation members
                    - users (List[str]): Same as members (compatibility field)
                    - is_im (bool): True for 2-person direct messages
                    - is_mpim (bool): True for multi-person direct messages (3+ users)
                    - user (str): Other user's ID (only present for 2-person DMs)
                - messages (List[Dict[str, Any]]): List of message objects (initially empty for new conversations)

    Raises:
        TypeError: If any parameter has incorrect type
        ValueError: If both channel and users are provided, or neither are provided,
                   or channel not found, or conversation not found when prevent_creation is True
        CurrentUserNotSetError: If no current user is set in the database when creating
                               a new conversation. Use utils.set_current_user(user_id) to set one.
    """
    # Type validation
    if channel is not None and not isinstance(channel, str):
        raise TypeError("channel must be a string")
    if not isinstance(prevent_creation, bool):
        raise TypeError("prevent_creation must be a boolean")
    if not isinstance(return_im, bool):
        raise TypeError("return_im must be a boolean")
    if users is not None and not isinstance(users, str):
        raise TypeError("users must be a string")
    
    # Value validation
    if not channel and not users:
        raise ValueError("either channel or users must be provided")

    if channel and users:
        raise ValueError("provide either channel or users, not both")

    if channel:
        # Resume an existing conversation
        conversation = DB["channels"].get(channel)
        if conversation:
            if return_im:
                # Return the full channel definition
                return {"ok": True, "channel": conversation}
            else:
                # Return minimal channel info
                return {"ok": True, "channel": {"id": conversation.get("id", channel)}}
        raise ValueError("channel not found")

    if users:
        user_list = [user.strip() for user in users.split(",")]

        # Get current user from database
        current_user_id = DB.get("current_user", {}).get("id")

        # Check if current user is set - required for conversation creation
        if not current_user_id:
            raise CurrentUserNotSetError(
                "No current user is set. Please set a current user first using set_current_user(user_id)."
            )

        # Automatically include current user if not already present
        # Per Slack API spec: "Don't include the ID of the user you're calling conversations.open on behalf of – we do that for you."
        if current_user_id not in user_list:
            user_list.append(current_user_id)

        user_list = sorted(user_list)  # Ensure consistent ordering for multi-person DMs

        # Check for existing conversation with same users
        existing_id, existing_data = utils.find_existing_conversation(user_list, DB)
        if existing_id:
            if return_im:
                # Return the full channel definition
                return {"ok": True, "channel": existing_data}
            else:
                # Return minimal channel info
                return {"ok": True, "channel": {"id": existing_id}}
        
        if prevent_creation:
            raise ValueError("conversation not found")

        # Create deterministic conversation ID based on users
        user_string = ",".join(user_list)
        conversation_id = "C" + hashlib.sha1(user_string.encode()).hexdigest()[:8].upper()

        # Create a new conversation with proper structure
        new_conversation = {
            "id": conversation_id,
            "members": user_list,
            "users": user_list,  # Keep for compatibility
            "is_im": len(user_list) == 2,
            "is_mpim": len(user_list) > 2
        }
        if len(user_list) == 2:
            new_conversation["user"] = user_list[1] if user_list[0] == user_list[0] else user_list[0]  # The other user

        DB["channels"][conversation_id] = {
            "conversations": new_conversation,
            "messages": [],
            "name": ",".join(user_list),
            "id": conversation_id,
            "is_private": True
        }

        if return_im:
            # Return the full channel definition
            return {"ok": True, "channel": DB["channels"][conversation_id]}
        else:
            # Return minimal channel info
            return {"ok": True, "channel": {"id": conversation_id}}

def list_channels(
    cursor: Optional[str] = None,
    exclude_archived: bool = False,
    limit: int = 100,
    team_id: Optional[str] = None,
    types: str = "public_channel"
) -> Dict[str, Any]:
    """
    Lists all channels in a Slack team.

    Args:
        cursor (Optional[str]): Paginate through collections of data. Must be a string
            representing a non-negative integer if provided. Defaults to None.
        exclude_archived (bool): Set to true to exclude archived channels from the list.
            Defaults to False.
        limit (int): The maximum number of items to return. Must be between 1 and 1000.
            Defaults to 100.
        team_id (Optional[str]): Encoded team id to list channels in. Defaults to None.
        types (str): Mix and match channel types by providing a comma-separated list of any
            combination of public_channel, private_channel, mpim, im.
            Defaults to "public_channel".

    Returns:
        Dict[str, Any]: A dictionary containing:
            - ok (bool): Whether the operation was successful (always True if no exception is raised)
            - channels (list): List of channel objects
            - response_metadata (dict): Pagination metadata containing:
                - next_cursor (Optional[str]): Cursor for next page of results, or None if no more pages

    Raises:
        TypeError: If any argument has an invalid type (e.g., `limit` is not int,
            `exclude_archived` is not bool, `cursor` is not str or None, `team_id`
            is not str or None, `types` is not str).
        ValueError: If `limit` is outside the range [1, 1000].
        ValueError: If `types` contains invalid channel types or is improperly formatted.
        ValueError: If `cursor` is provided but is not a string representing a non-negative integer.
        ValueError: If `cursor` value exceeds the total number of available channels.
    """
    # --- Input Validation ---
    if cursor is not None and not isinstance(cursor, str):
        raise TypeError("cursor must be a string or None.")
    if cursor is not None:
        try:
            cursor_int = int(cursor)
            if cursor_int < 0:
                raise ValueError("cursor must represent a non-negative integer.")
        except ValueError:
            raise ValueError("cursor must be a string representing a non-negative integer.")

    if not isinstance(exclude_archived, bool):
        raise TypeError("exclude_archived must be a boolean.")

    if not isinstance(limit, int):
        raise TypeError("limit must be an integer.")
    if not (1 <= limit <= 1000):
        raise ValueError("limit must be between 1 and 1000.")

    if team_id is not None and not isinstance(team_id, str):
        raise TypeError("team_id must be a string or None.")

    if not isinstance(types, str):
        raise TypeError("types must be a string.")

    valid_types_set = {"public_channel", "private_channel", "mpim", "im"}
    requested_types = []
    if types: # Ensure types is not an empty string before splitting
        try:
            requested_types = [t.strip() for t in types.split(",")]
            if not requested_types: # Handle case like types="," which results in empty list after strip
                 raise ValueError("types string cannot be empty or only contain commas.")
            for t in requested_types:
                if not t: # Handle cases like types="public_channel,,private_channel"
                    raise ValueError("Empty type string found within the comma-separated list.")
                if t not in valid_types_set:
                    raise ValueError(f"Invalid type '{t}' requested. Valid types are: {', '.join(sorted(valid_types_set))}")
        except Exception as e: # Catch potential errors during split/strip if types is unusual but still a string
             raise ValueError(f"Invalid format for types string: {e}")
    else:
        # If types is an empty string, default to public_channel as per original logic/docstring
        requested_types = ["public_channel"]
    # --- End of Input Validation ---

    channels = []
    all_channels = DB.get("channels", {}).values() # Assume DB exists and works
    for channel in all_channels:
        # Apply filters based on arguments (exclude_archived, types, team_id)
        if exclude_archived and channel.get("is_archived", False):
            continue

        # Use the validated requested_types list
        channel_type = channel.get("type", "public_channel") # Assume public_channel if type is not defined
        if channel_type not in requested_types:
            continue
        if team_id is not None and channel.get("team_id") != team_id:
            continue

        channels.append(channel)

    # Check if cursor is out of bounds
    if cursor is not None and int(cursor) >= len(channels):
        raise ValueError(f"Cursor value {cursor} exceeds the total number of available channels ({len(channels)})")

    # Apply limit and cursor for pagination (simplified)
    start_index = 0
    if cursor:
        # The cursor format validation happened above, so we can safely convert
        start_index = int(cursor)

    end_index = min(start_index + limit, len(channels))
    channels_page = channels[start_index:end_index]

    next_cursor = str(end_index) if end_index < len(channels) else None

    response = {
        "ok": True, # Assume success if execution reaches here without exceptions
        "channels": channels_page,
        "response_metadata": {"next_cursor": next_cursor},
    }

    return response

def close(channel: str) -> Dict[str, Any]:
    """
    Closes a direct message or multi-person direct message.

    Args:
        channel (str): Conversation to close.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - ok (bool): Always True for successful operations

    Raises:
        TypeError: If channel is not a string.
        ChannelNotFoundError: If the channel parameter is empty or channel doesn't exist.
        NotAllowedError: If the channel is not a direct message or multi-person direct message.
    """
    if not isinstance(channel, str):
        raise TypeError(f"channel must be a string, got {type(channel).__name__}")
    
    if not channel:
        raise ChannelNotFoundError("Channel parameter is required")

    if channel not in DB.get("channels", {}):
        raise ChannelNotFoundError(f"Channel {channel} not found")

    if DB["channels"][channel].get("type") not in ["im", "mpim"]:
        raise NotAllowedError(f"Cannot close channel {channel}: operation only allowed for direct messages")

    DB["channels"][channel]["is_open"] = False
    return {"ok": True}

def rename(channel: str, name: str) -> Dict[str, Any]:
    """
    Renames a conversation.

    Args:
        channel (str): ID of conversation to rename.
        name (str): New name for conversation.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - ok (bool): Always True for successful operations
            - channel (dict): Channel information containing:
                - id (str): Channel ID
                - name (str): New channel name

    Raises:
        TypeError: If channel or name is not a string.
        ChannelNotFoundError: If the channel parameter is empty or channel doesn't exist.
        ChannelNameMissingError: If the name parameter is empty or None.
        ChannelNameTakenError: If a channel with this name already exists.
    """
    if not isinstance(channel, str):
        raise TypeError(f"channel must be a string, got {type(channel).__name__}")
    if not isinstance(name, str):
        raise TypeError(f"name must be a string, got {type(name).__name__}")
    
    if not channel:
        raise ChannelNotFoundError("Channel parameter is required")
    if not name or not name.strip():
        raise ChannelNameMissingError("Name parameter is required and cannot be empty")

    if channel not in DB["channels"]:
        raise ChannelNotFoundError(f"Channel {channel} not found")

    # Check if name is already taken
    for existing_channel in DB["channels"].values():
        if existing_channel.get("name") == name and existing_channel["id"] != channel:
            raise ChannelNameTakenError(f"Channel name '{name}' is already taken")

    DB["channels"][channel]["name"] = name
    return {"ok": True, "channel": {"id": channel, "name": name}}

def members(
    channel: str,
    cursor: Optional[str] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Retrieve members of a conversation.

    Args:
        channel (str): ID of the conversation.
        cursor (Optional[str]): Pagination cursor encoded in base64 in format "user:{user_id}". Defaults to None.
        limit (int): Maximum number of items to return. Defaults to 100. Must be positive and cannot exceed 10000.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - ok (bool): Whether the operation was successful
            - members (list[str]): List of member user IDs
            - response_metadata (dict): Pagination metadata containing:
                - next_cursor (str): Base64 encoded cursor for next page of results in format "user:{user_id}"

    Raises:
        TypeError: If 'channel' is not a string, 'cursor' (if provided) is not a string,
                   or 'limit' is not an integer.
        ValueError: If 'channel' is an empty string, or 'limit' is not a positive integer or if limit > 10000.
        ChannelNotFoundError: If the specified 'channel' does not exist in the database.
        InvalidCursorValueError: If 'cursor' is provided but cannot be decoded properly.
    """
    # --- Input Validation Logic ---
    if not isinstance(channel, str):
        raise TypeError("channel must be a string.")
    if not channel:
        raise ValueError("channel cannot be an empty string.")

    if cursor is not None and not isinstance(cursor, str):
        raise TypeError("cursor must be a string if provided.")

    if not isinstance(limit, int):
        raise TypeError("limit must be an integer.")
    if limit <= 0:
        raise ValueError("limit must be a positive integer.")
    if limit > 10000:
        raise ValueError(f"limit cannot exceed 10000.") # To prevent abuse or unexpected load
    # --- End of Input Validation Logic ---
    
    if channel not in DB.get("channels", {}):
        raise ChannelNotFoundError(f"Channel '{channel}' not found")
        
    DB["channels"][channel].setdefault('conversations', {})
    DB["channels"][channel]['conversations'].setdefault('members', [])

    member_ids = DB["channels"][channel]['conversations']["members"]

    # Apply pagination
    start_index = 0
    if cursor:
        try:
            # Decode base64 cursor and extract user ID
            decoded_cursor = base64.b64decode(cursor).decode('utf-8')
            if not decoded_cursor.startswith("user:"):
                raise InvalidCursorValueError("Invalid cursor format")
            cursor_user_id = decoded_cursor[5:]
            
            # Find the index after the cursor user
            try:
                start_index = member_ids.index(cursor_user_id) + 1
            except ValueError:
                raise InvalidCursorValueError(f"User ID {cursor_user_id} not found in members list")
                
        except base64.binascii.Error:
            raise InvalidCursorValueError("Invalid base64 cursor format")

    end_index = min(start_index + limit, len(member_ids))
    paged_members = member_ids[start_index:end_index]

    # Create next cursor in base64 format if there are more results
    next_cursor_val = ""
    if end_index < len(member_ids):
        last_user_id = member_ids[end_index - 1]
        cursor_str = f"user:{last_user_id}"
        next_cursor_val = base64.b64encode(cursor_str.encode('utf-8')).decode('utf-8')

    return {
        "ok": True,
        "members": paged_members,
        "response_metadata": {"next_cursor": next_cursor_val},
    }

def create_channel(
        name: str,
        is_private: bool = False,
        team_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Initiates a public or private channel-based conversation.

    Args:
        name (str): Name of the channel. Must be a non-empty string.
        is_private (bool): Create a private channel. Defaults to False. Must be a boolean.
        team_id (Optional[str]): Encoded team id. Defaults to None. Must be a string if provided.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - ok (bool): Whether the operation was successful (always True if no exception).
            - channel (dict): Channel information containing:
                - id (str): Channel ID
                - name (str): Channel name
                - is_private (bool): Whether channel is private
                - team_id (Optional[str]): Team ID
                - conversations (dict): Conversation settings containing:
                    - id (str): Conversation ID
                    - read_cursor (int): Read cursor position (initialized to 0)
                    - members (list): List of channel members (initially empty)
                    - topic (str): Channel topic (initially empty)
                    - purpose (str): Channel purpose (initially empty)
                - messages (list): Initial empty messages list

    Raises:
        TypeError: If 'name' is not a string, 'is_private' is not a boolean,
                   or 'team_id' is not a string (if provided and not None).
        ChannelNameMissingError: If 'name' is an empty string.
        ChannelNameTakenError: If the provided 'name' is already in use by another channel.
    """
    # --- Input Validation Start ---
    if not isinstance(name, str):
        raise TypeError("Argument 'name' must be a string.")
    if not name:  # Check for empty string after type check
        raise ChannelNameMissingError("Argument 'name' cannot be empty.")

    if not isinstance(is_private, bool):
        raise TypeError("Argument 'is_private' must be a boolean.")

    if team_id is not None and not isinstance(team_id, str):
        raise TypeError("Argument 'team_id' must be a string or None.")
    # --- Input Validation End ---

    # Original core logic starts here.
    existing_channels = DB.get("channels", {})
    for channel_data in existing_channels.values():
        if channel_data.get('name') == name:
            raise ChannelNameTakenError(f"Channel name '{name}' is already taken.")

    base_id = hashlib.sha1(name.encode()).hexdigest()[:8].upper()
    channel_id = f"C{base_id}"

    if channel_id in existing_channels:
        random.seed(base_id)  # Seeded to ensure repeatability for deterministic suffix
        suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=2))
        channel_id = f"{channel_id}{suffix}"
        # Note: The original logic doesn't re-check for collision after adding suffix. We preserve this.
    conversation_id = "C" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    channel_data_to_store = {
        "id": channel_id,
        "name": name,
        "is_private": is_private,
        "team_id": team_id,
        "conversations": {
            "id": conversation_id,
            "read_cursor": 0,
            "members": [],
            "topic": "",
            "purpose": ""

        },
        "messages": []
    }

    # Ensure DB["channels"] exists before assignment
    if "channels" not in DB:
        DB["channels"] = {}  # Initialize if it's the very first channel
    DB["channels"][channel_id] = channel_data_to_store

    return {"ok": True, "channel": channel_data_to_store}

def setPurpose(channel: str, purpose: str) -> Dict[str, Any]:
    """
    Sets the channel description.

    Args:
        channel (str): Channel to set the description of.
        purpose (str): The description of the channel.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - ok (bool): Whether the operation was successful
            - purpose (str): The set purpose

    Raises:
        TypeError: If 'channel' or 'purpose' is not a string.
        ChannelNameMissingError: If 'channel' is an empty string.
        MissingPurposeError: If 'purpose' is an empty string.
        PermissionError: If the current user is not an admin.
        UserNotInConversationError: If the current user is not a member of the channel.
        ChannelNotFoundError: If the specified 'channel' does not exist in the DB.
    """

    if not isinstance(channel, str):
        raise TypeError("channel must be a string.")
    if not isinstance(purpose, str):
        raise TypeError("purpose must be a string.")

    if not channel:
        raise ChannelNameMissingError("channel cannot be empty.")
    if not purpose:
        raise MissingPurposeError("purpose cannot be empty.")

    if channel not in DB["channels"]:
        raise ChannelNotFoundError(f"Channel '{channel}' not found.")

    if DB["current_user"]["is_admin"] is False:
        raise PermissionError("You are not authorized to set the purpose of this channel.")

    if DB["current_user"]["id"] not in DB["channels"][channel]["conversations"]["members"]:
        raise UserNotInConversationError("You are not a member of this channel.")

    DB["channels"][channel]['conversations']["purpose"] = purpose
    return {"ok": True,  "purpose": purpose}

def setConversationTopic(channel: str, topic: str) -> Dict[str, Any]:
    """
    Sets the topic for a conversation.

    Args:
        channel (str): Conversation to set the topic of.
        topic (str): The new topic string.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - ok (bool): Whether the operation was successful
            - topic (str): The set topic

    Raises:
        TypeError: If 'channel' or 'topic' is not a string.
        ChannelNameMissingError: If 'channel' is an empty string.
        ValueError: If 'topic' is an empty string.
        ChannelNotFoundError: If the specified 'channel' does not exist in the DB.
        UserNotInConversationError: If the current user is not a member of the channel.
        PermissionError: If the current user is not an admin.
    """
    if not isinstance(channel, str):
        raise TypeError("channel must be a string.")
    if not isinstance(topic, str):
        raise TypeError("topic must be a string.")

    if not channel:
        raise ChannelNameMissingError("channel cannot be empty.")
    if not topic:
        raise ValueError("topic cannot be empty.")

    # Simulate setting the topic in the database
    if channel not in DB["channels"]:
        raise ChannelNotFoundError(f"Channel '{channel}' not found.")

    if DB["current_user"]["id"] not in DB["channels"][channel]['conversations']["members"]:
        raise UserNotInConversationError("Current user is not a member of this channel.")

    if DB["current_user"]["is_admin"] is False:
        raise PermissionError("You are not authorized to set the topic of this channel.")

    DB['channels'][channel]['conversations']['topic'] = topic

    return {"ok": True, "topic": topic}

def replies(
    channel: str,
    ts: str,
    cursor: Optional[str] = None,
    include_all_metadata: bool = False,
    inclusive: bool = False,
    latest: Optional[str] = None,
    limit: int = 1000,
    oldest: str = "0"
) -> Dict[str, Any]:
    """
    Retrieve a thread of messages posted to a conversation.

    Args:
        channel (str): Conversation ID.
        ts (str): Timestamp of the parent message or a message in the thread.
        cursor (Optional[str]): Pagination cursor. Defaults to None.
        include_all_metadata (bool): Return all metadata. Defaults to False. Note: This parameter is currently not implemented and has no effect on the response.
        inclusive (bool): Include messages with oldest/latest timestamps.
            Defaults to False.
        latest (Optional[str]): Only messages before this timestamp.
            Defaults to None.
        limit (int): Maximum number of items to return. Defaults to 1000.
        oldest (str): Only messages after this timestamp. Defaults to "0".

    Returns:
        Dict[str, Any]: A dictionary containing:
            - ok (bool): Whether the operation was successful
            - messages (list): List of thread messages
            - has_more (bool): Whether there are more messages to fetch
            - response_metadata (dict): Pagination metadata containing:
                - next_cursor (str): Cursor for next page of results

    Raises:
        TypeError: If any argument is of an incorrect type.
        MessageNotFoundError: If there is no message found against the given ts
        ChannelNotFoundError: If the given channel name is not present
    """
    # Input Validation
    if not isinstance(channel, str):
        raise TypeError("channel must be a string.")
    if not isinstance(ts, str):
        raise TypeError("ts must be a string.")
    if cursor is not None and not isinstance(cursor, str):
        raise TypeError("cursor must be a string or None.")
    if not isinstance(include_all_metadata, bool):
        raise TypeError("include_all_metadata must be a boolean.")
    if not isinstance(inclusive, bool):
        raise TypeError("inclusive must be a boolean.")
    if latest is not None and not isinstance(latest, str):
        raise TypeError("latest must be a string or None.")
    if not isinstance(limit, int):
        raise TypeError("limit must be an integer.")
    if not isinstance(oldest, str):
        raise TypeError("oldest must be a string.")

    # Original Core Logic (remains unchanged)


    if channel not in DB.get("channels", {}): # Safely access DB
            raise ChannelNotFoundError(f"the {channel} is not present in channels")

    # Simulate fetching replies from the DB based on channel and ts
    if "messages" not in DB["channels"][channel]:
        return {"ok": True, "messages": [], "has_more": False, "response_metadata": {"next_cursor": None}}

    parent_message = None
    for msg in DB["channels"][channel]["messages"]:
        if msg["ts"] == ts:
            parent_message = msg
            break
    if not parent_message:
        raise MessageNotFoundError(f"No message found against the ts: {ts}")

    if "replies" not in parent_message:
        thread_replies = [] # Renamed to avoid conflict with function name
    else:
        thread_replies = parent_message["replies"]

    #Apply TimeStamp Filtering
    current_time_ts = str(time.time())
    effective_latest = latest if latest is not None else current_time_ts

    if inclusive:
        filtered_replies = [
            message for message in thread_replies
            if float(oldest) <= float(message['ts']) <= float(effective_latest)
        ]
    else:
        filtered_replies = [
            message for message in thread_replies
            if float(oldest) < float(message['ts']) < float(effective_latest)
        ]

    # Apply limit and cursor
    start_index = 0
    if cursor:
        try:
            start_index = next(i for i,v in enumerate(filtered_replies) if v['ts'] == cursor) + 1
        except StopIteration:
            raise CursorOutOfBoundsError(f"Cursor {cursor} not found in thread replies")

    end_index = min(start_index + limit, len(filtered_replies))
    messages_to_return = filtered_replies[start_index:end_index] # Renamed to avoid conflict

    next_page_cursor = None # Renamed to avoid conflict
    if end_index < len(filtered_replies):
        next_page_cursor = filtered_replies[end_index]['ts']

    response = {
        "ok": True,
        "messages": messages_to_return,
        "has_more":  end_index < len(filtered_replies),
        "response_metadata":{"next_cursor": next_page_cursor}
    }
    return response
