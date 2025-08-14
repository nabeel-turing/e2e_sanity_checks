import datetime
import re
import random
import string
from typing import Dict, Any
from .db import DB

# -------------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------------

def _convert_timestamp_to_utc_date(ts: str) -> datetime.date:
    """Convert a Unix timestamp to a UTC date.
    
    Args:
        ts (str): Unix timestamp as string
        
    Returns:
        datetime.date: The UTC date
        
    Raises:
        ValueError: If timestamp cannot be converted
    """
    try:
        ts_value = float(ts)
        # Use fromtimestamp with timezone.utc for compatibility with older Python versions
        return datetime.datetime.fromtimestamp(ts_value, datetime.timezone.utc).date()
    except (ValueError, TypeError, OverflowError) as e:
        raise ValueError(f"Invalid timestamp format: {ts}") from e

def _parse_query(query: str) -> Dict[str, Any]:
    """Parses the Slack Query Language into structured filters.

    Args:
        query (str): The Slack Query Language string.

    Returns:
        Dict[str, Any]: A dictionary containing the parsed filters.
    """
    filters = {
        "text": [],
        "excluded": [],
        "filetype": None,
        "user": None,
        "channel": None,
        "date_after": None,
        "date_before": None,
        "date_during": None,
        "has": set(),
        "to": None,
        "wildcard": None,
        "boolean": "AND"
    }

    tokens = query.split()
    for token in tokens:
        if token.startswith("from:@"):
            filters["user"] = token.split("from:@")[1]
        elif token.startswith("in:#"):
            filters["channel"] = token.split("in:#")[1]
        elif token.startswith("after:"):
            filters["date_after"] = token.split("after:")[1]
        elif token.startswith("before:"):
            filters["date_before"] = token.split("before:")[1]
        elif token.startswith("during:"):
            filters["date_during"] = token.split("during:")[1]
        elif token.startswith("filetype:"):
            filters["filetype"] = token.split("filetype:")[1]
        elif token.startswith("has:"):
            filters["has"].add(token.split("has:")[1])
        elif token.startswith("to:"):
            filters["to"] = token.split("to:")[1]
        elif '*' in token:
            filters["wildcard"] = token
        elif token == "OR":
            filters["boolean"] = "OR"
        elif token.startswith("-"):
            filters["excluded"].append(token[1:])
        else:
            filters["text"].append(token)

    return filters

def _matches_filters(msg: Dict[str, Any], filters: Dict[str, Any], channel_name: str) -> bool:
    """Checks if a message matches the parsed filters.

    Args:
        msg (Dict[str, Any]): The message to check.
        filters (Dict[str, Any]): The parsed filters (output of _parse_query).
        channel_name (str): The name of the channel.

    Returns:
        bool: True if the message matches the filters, False otherwise.
    """
    # Channel filter
    if filters["channel"] and channel_name != filters["channel"]:
        return False

    # User filter
    if filters["user"] and msg.get("user") != filters["user"]:
        return False

    # Handle messages that might not have all necessary fields
    if "text" not in msg:
        return False

    # Convert timestamp to UTC date
    try:
        msg_date = _convert_timestamp_to_utc_date(msg["ts"])
    except ValueError:
        return False

    # Date filters
    if filters["date_after"]:
        try:
            date_after = datetime.datetime.strptime(filters["date_after"], "%Y-%m-%d").date()
            if msg_date <= date_after:
                return False
        except ValueError:
            return False
            
    if filters["date_before"]:
        try:
            date_before = datetime.datetime.strptime(filters["date_before"], "%Y-%m-%d").date()
            if msg_date >= date_before:
                return False
        except ValueError:
            return False
            
    if filters["date_during"]:
        during_value = filters["date_during"]
        try:
            # Year-only filter (e.g., during:2024)
            if re.fullmatch(r"\d{4}", during_value):
                msg_year = msg_date.year
                if msg_year != int(during_value):
                    return False

            # Year and Month filter (e.g., during:2024-03)
            elif re.fullmatch(r"\d{4}-\d{2}", during_value):
                year, month = map(int, during_value.split("-"))
                msg_year, msg_month = msg_date.year, msg_date.month
                if msg_year != year or msg_month != month:
                    return False

            # Full Date filter (e.g., during:2024-03-23)
            elif re.fullmatch(r"\d{4}-\d{2}-\d{2}", during_value):
                date_during = datetime.datetime.strptime(during_value, "%Y-%m-%d").date()
                if msg_date != date_during:
                    return False
        except ValueError:
            return False

    # Text filters
    if filters["text"]:
        if filters["boolean"] == "AND":
            # All words must be present for an AND search
            if not all(word.lower() in msg["text"].lower() for word in filters["text"]):
                return False
        elif filters["boolean"] == "OR":
            # Any word can be present for an OR search
            if not any(word.lower() in msg["text"].lower() for word in filters["text"]):
                return False

    # Check for excluded text
    if filters["excluded"]:
        excluded_match = any(word.lower() in msg["text"].lower() for word in filters["excluded"])
        if excluded_match:
            return False

    # Has filters
    if "link" in filters["has"] and not msg.get("links"):
        return False
    if "reaction" in filters["has"] and not msg.get("reactions"):
        return False
    if "star" in filters["has"] and not msg.get("is_starred"):
        return False

    # Wildcard search
    if filters["wildcard"]:
        pattern = filters["wildcard"].replace('*', '.*')
        if not re.search(pattern, msg["text"], re.IGNORECASE):
            return False

    # If we've passed all the filters, the message matches
    return True

def find_existing_conversation(user_list, db):
    """Find existing conversation with same users.
    
    Args:
        user_list (list): Sorted list of user IDs
        db (dict): Database dictionary containing channels
        
    Returns:
        tuple: (channel_id, channel_data) if found, (None, None) if not found
    """
    sorted_users = sorted(user_list)
    for channel_id, channel_data in db["channels"].items():
        # Check both members (new structure) and users (old structure)
        members = channel_data.get("conversations", {}).get("members", [])
        users_field = channel_data.get("conversations", {}).get("users", [])
        existing_users = members if members else users_field
        if sorted(existing_users) == sorted_users:
            return channel_id, channel_data
    return None, None

def _generate_slack_file_id() -> str:
    """
    Generate a Slack-style file ID.
    
    Returns:
        str: A 9-character file ID starting with 'F' followed by 8 alphanumeric characters.
    """
    # Generate 8 random alphanumeric characters (uppercase letters and digits)
    chars = string.ascii_uppercase + string.digits
    random_part = ''.join(random.choice(chars) for _ in range(8))
    return f"F{random_part}"

def _check_and_delete_pending_file(file_id: str):
    """
    Checks a file's status after a delay and deletes it if it's still pending.
    This function is intended to be run in a separate thread (e.g., via threading.Timer).
    """
    if file_id in DB.get("files", {}) and DB["files"][file_id].get("status") == "pending_upload":
        del DB["files"][file_id]


def infer_channel_type(channel: Dict[str, Any]) -> str:
    """Infer channel type from channel properties.
    
    Args:
        channel (Dict[str, Any]): Channel object
        
    Returns:
        str: Channel type - one of 'im', 'mpim', 'private_channel', or 'public_channel'
    """
    # Check if it's a direct message (im) - typically has 2 users and specific naming pattern
    if channel.get("is_im", False):
        return "im"
    
    # Check if it's a multi-party instant message (mpim) - typically has 3+ users and specific naming pattern
    if channel.get("is_mpim", False):
        return "mpim"
    
    # Check if it's a private channel
    if channel.get("is_private", False):
        return "private_channel"
    
    # Default to public channel
    return "public_channel"


def get_channel_members(channel: Dict[str, Any]) -> list:
    """Infer channel membership from messages and reactions.
    
    Args:
        channel (Dict[str, Any]): Channel object
        
    Returns:
        list: List of user IDs who are members of the channel
    """
    members = set()
    
    # Add users who have posted messages
    for message in channel.get("messages", []):
        if "user" in message:
            members.add(message["user"])
        
        # Add users who have reacted to messages
        for reaction in message.get("reactions", []):
            for user in reaction.get("users", []):
                members.add(user)
    
    return [member for member in members]