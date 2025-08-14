from typing import Dict, Any, List

"""
Simulation of /modmail endpoints.
Handles moderator mail conversations.
"""


def post_api_mod_bulk_read(conversation_ids: List[str]) -> Dict[str, Any]:
    """
    Marks multiple modmail conversations as read.

    Args:
        conversation_ids (List[str]): A list of modmail conversation IDs.

    Returns:
        Dict[str, Any]:
        - If the conversation IDs list is empty, returns a dictionary with the key "error" and the value "No conversation IDs provided.".
        - If any conversation ID is invalid, returns a dictionary with the key "error" and the value "Invalid conversation ID.".
        - On successful operation, returns a dictionary with the following keys:
            - status (str): The status of the operation ("bulk_read")
            - count (int): The number of conversations marked as read
    """
    return {"status": "bulk_read", "count": len(conversation_ids)}


def get_api_mod_conversations() -> Dict[str, List[Dict[str, Any]] | int]:
    """
    Retrieves a list of modmail conversations.

    Returns:
        Dict[str, List[Dict[str, Any]] | int]:
        - On successful retrieval, returns a dictionary with the following keys:
            - conversations (List[Dict[str, Any]]): A list of conversation objects
            - total_count (int): The total number of conversations
            - unread_count (int): The number of unread conversations
    Raises:
        ConversationNotFoundError: if there are no conversations
    """
    return {"conversations": [], "total_count": 0, "unread_count": 0}


def get_api_mod_conversations_conversation_id(conversation_id: str) -> Dict[str, Any]:
    """
    Retrieves details of a specific modmail conversation.

    Args:
        conversation_id (str): The ID of the modmail conversation.

    Returns:
        Dict[str, Any]:
        - If the conversation ID is invalid, returns a dictionary with the key "error" and the value "Invalid conversation ID.".
        - If the conversation does not exist, returns a dictionary with the key "error" and the value "Conversation not found.".
        - On successful retrieval, returns a dictionary with the following keys:
            - id (str): The conversation ID
            - subject (str): The conversation subject
            - messages (List[Dict[str, Any]]): A list of messages in the conversation
            - participants (List[str]): A list of participant usernames
            - is_read (bool): Whether the conversation has been read
    """
    return {"id": conversation_id, "subject": "", "messages": [], "participants": [], "is_read": False}


def post_api_mod_conversations_conversation_id_approve(conversation_id: str) -> Dict[str, Any]:
    """
    Approves a modmail conversation.

    Args:
        conversation_id (str): The ID of the modmail conversation.

    Returns:
        Dict[str, Any]:
        - If the conversation ID is invalid, returns a dictionary with the key "error" and the value "Invalid conversation ID.".
        - If the conversation is already approved, returns a dictionary with the key "error" and the value "Conversation already approved.".
        - On successful approval, returns a dictionary with the following keys:
            - status (str): The status of the operation ("approved")
            - conversation_id (str): The ID of the approved conversation
    """
    return {"status": "approved", "conversation_id": conversation_id}


def post_api_mod_conversations_conversation_id_archive(conversation_id: str) -> Dict[str, Any]:
    """
    Archives a modmail conversation.

    Args:
        conversation_id (str): The ID of the modmail conversation.

    Returns:
        Dict[str, Any]:
        - If the conversation ID is invalid, returns a dictionary with the key "error" and the value "Invalid conversation ID.".
        - If the conversation is already archived, returns a dictionary with the key "error" and the value "Conversation already archived.".
        - On successful archiving, returns a dictionary with the following keys:
            - status (str): The status of the operation ("archived")
            - conversation_id (str): The ID of the archived conversation
    """
    return {"status": "archived", "conversation_id": conversation_id}


def post_api_mod_conversations_conversation_id_disapprove(conversation_id: str) -> Dict[str, Any]:
    """
    Disapproves a modmail conversation.

    Args:
        conversation_id (str): The ID of the modmail conversation.

    Returns:
        Dict[str, Any]:
        - If the conversation ID is invalid, returns a dictionary with the key "error" and the value "Invalid conversation ID.".
        - If the conversation is already disapproved, returns a dictionary with the key "error" and the value "Conversation already disapproved.".
        - On successful disapproval, returns a dictionary with the following keys:
            - status (str): The status of the operation ("disapproved")
            - conversation_id (str): The ID of the disapproved conversation
    """
    return {"status": "disapproved", "conversation_id": conversation_id}


def delete_api_mod_conversations_conversation_id_highlight(conversation_id: str) -> Dict[str, Any]:
    """
    Removes a highlight marker from a conversation.

    Args:
        conversation_id (str): The ID of the modmail conversation.

    Returns:
        Dict[str, Any]:
        - If the conversation ID is invalid, returns a dictionary with the key "error" and the value "Invalid conversation ID.".
        - If the conversation is not highlighted, returns a dictionary with the key "error" and the value "Conversation is not highlighted.".
        - On successful operation, returns a dictionary with the following keys:
            - status (str): The status of the operation ("highlight_removed")
            - conversation_id (str): The ID of the conversation
    """
    return {"status": "highlight_removed", "conversation_id": conversation_id}


def post_api_mod_conversations_conversation_id_mute(conversation_id: str) -> Dict[str, Any]:
    """
    Mutes the user in a modmail conversation.

    Args:
        conversation_id (str): The ID of the modmail conversation.

    Returns:
        Dict[str, Any]:
        - If the conversation ID is invalid, returns a dictionary with the key "error" and the value "Invalid conversation ID.".
        - If the user is already muted, returns a dictionary with the key "error" and the value "User already muted.".
        - On successful muting, returns a dictionary with the following keys:
            - status (str): The status of the operation ("muted")
            - conversation_id (str): The ID of the conversation
    """
    return {"status": "muted", "conversation_id": conversation_id}


def post_api_mod_conversations_conversation_id_temp_ban(conversation_id: str) -> Dict[str, Any]:
    """
    Temporarily bans a user via modmail.

    Args:
        conversation_id (str): The ID of the modmail conversation.

    Returns:
        Dict[str, Any]:
        - If the conversation ID is invalid, returns a dictionary with the key "error" and the value "Invalid conversation ID.".
        - If the user is already banned, returns a dictionary with the key "error" and the value "User already banned.".
        - On successful ban, returns a dictionary with the following keys:
            - status (str): The status of the operation ("temp_banned")
            - conversation_id (str): The ID of the conversation
    """
    return {"status": "temp_banned", "conversation_id": conversation_id}


def post_api_mod_conversations_conversation_id_unarchive(conversation_id: str) -> Dict[str, Any]:
    """
    Unarchives a modmail conversation.

    Args:
        conversation_id (str): The ID of the modmail conversation.

    Returns:
        Dict[str, Any]:
        - If the conversation ID is invalid, returns a dictionary with the key "error" and the value "Invalid conversation ID.".
        - If the conversation is not archived, returns a dictionary with the key "error" and the value "Conversation is not archived.".
        - On successful unarchiving, returns a dictionary with the following keys:
            - status (str): The status of the operation ("unarchived")
            - conversation_id (str): The ID of the conversation
    """
    return {"status": "unarchived", "conversation_id": conversation_id}


def post_api_mod_conversations_conversation_id_unban(conversation_id: str) -> Dict[str, Any]:
    """
    Revokes a ban issued via modmail.

    Args:
        conversation_id (str): The ID of the modmail conversation.

    Returns:
        Dict[str, Any]:
        - If the conversation ID is invalid, returns a dictionary with the key "error" and the value "Invalid conversation ID.".
        - If the user is not banned, returns a dictionary with the key "error" and the value "User is not banned.".
        - On successful unban, returns a dictionary with the following keys:
            - status (str): The status of the operation ("unbanned")
            - conversation_id (str): The ID of the conversation
    """
    return {"status": "unbanned", "conversation_id": conversation_id}


def post_api_mod_conversations_conversation_id_unmute(conversation_id: str) -> Dict[str, Any]:
    """
    Unmutes a user in a modmail conversation.

    Args:
        conversation_id (str): The ID of the modmail conversation.

    Returns:
        Dict[str, Any]:
        - If the conversation ID is invalid, returns a dictionary with the key "error" and the value "Invalid conversation ID.".
        - If the user is not muted, returns a dictionary with the key "error" and the value "User is not muted.".
        - On successful unmuting, returns a dictionary with the following keys:
            - status (str): The status of the operation ("unmuted")
            - conversation_id (str): The ID of the conversation
    """
    return {"status": "unmuted", "conversation_id": conversation_id}


def post_api_mod_conversations_read(conversation_ids: List[str]) -> Dict[str, Any]:
    """
    Marks specified modmail conversations as read.

    Args:
        conversation_ids (List[str]): A list of modmail conversation IDs.

    Returns:
        Dict[str, Any]:
        - If the conversation IDs list is empty, returns a dictionary with the key "error" and the value "No conversation IDs provided.".
        - If any conversation ID is invalid, returns a dictionary with the key "error" and the value "Invalid conversation ID.".
        - On successful operation, returns a dictionary with the following keys:
            - status (str): The status of the operation ("read")
            - count (int): The number of conversations marked as read
    """
    return {"status": "read", "count": len(conversation_ids)}


def get_api_mod_conversations_subreddits() -> List[str]:
    """
    Lists subreddits accessible via modmail.

    Returns:
        List[str]:
        - If there are no accessible subreddits, returns an empty list.
        - On successful retrieval, returns a list of subreddit names.
    """
    return []


def post_api_mod_conversations_unread(conversation_ids: List[str]) -> Dict[str, Any]:
    """
    Marks specified modmail conversations as unread.

    Args:
        conversation_ids (List[str]): A list of modmail conversation IDs.

    Returns:
        Dict[str, Any]:
        - If the conversation IDs list is empty, returns a dictionary with the key "error" and the value "No conversation IDs provided.".
        - If any conversation ID is invalid, returns a dictionary with the key "error" and the value "Invalid conversation ID.".
        - On successful operation, returns a dictionary with the following keys:
            - status (str): The status of the operation ("unread")
            - count (int): The number of conversations marked as unread
    """
    return {"status": "unread", "count": len(conversation_ids)}


def get_api_mod_conversations_unread_count() -> Dict[str, str | int]:
    """
    Retrieves the count of unread modmail conversations.

    Returns:
        Dict[str, str | int]:
        - On successful retrieval, returns a dictionary with the following keys:
            - count (int): The number of unread conversations
            - last_updated (str): The timestamp of the last update
    """
    return {"count": 0, "last_updated": "2024-01-01T00:00:00Z"}