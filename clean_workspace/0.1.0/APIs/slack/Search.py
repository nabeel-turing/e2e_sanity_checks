"""
Search resource for Slack API simulation.

This module provides functionality for searching messages and files in Slack.
It simulates the search-related endpoints of the Slack API.
"""

from typing import Dict, Any, List
from .SimulationEngine.db import DB
from .SimulationEngine.utils import _parse_query, _matches_filters
from .SimulationEngine.search_engine import search_engine_manager, service_adapter


def search_messages(query: str) -> List[Dict[str, Any]]:
    """
    Searches for messages matching a query.

    The query is a space-separated string of terms and filters. Text terms are
    matched against the message's content. By default, all text terms must be
    present in the message (AND logic).

    Args:
        query (str): The search query. The structure is a space-separated string
            of terms and filters. Supported filters are:
            - `from:@<user>`: Restricts the search to messages from a specific user.
            - `in:#<channel>`: Restricts the search to a specific channel.
            - `has:link`: Narrows search to messages that contain a URL.
            - `has:reaction`: Narrows search to messages that have a reaction.
            - `has:star`: Narrows search to messages that have been starred.
            - `before:YYYY-MM-DD`: Filters for messages sent before a specific date.
            - `after:YYYY-MM-DD`: Filters for messages sent after a specific date.
            - `during:YYYY-MM-DD`: Filters for messages on a specific date. Also
              supports `YYYY` for a year or `YYYY-MM` for a month.
            - `-<word>`: Excludes messages containing the specified word.
            - `some*`: Wildcard support for partial word matching.
            - `OR`: When used between text terms (e.g., "hello OR world"), the
              logic changes to match messages containing any of the terms.

    Returns:
        List[Dict[str, Any]]: List of matching messages, where each message contains:
            - ts (str): Message timestamp
            - text (str): Message content
            - user (str): User ID who sent the message
            - channel (str): Channel ID where message was sent
            - reactions (Optional[List[Dict[str, Any]]]): List of reactions if any

    Raises:
        TypeError: If 'query' is not a string.
    """
    # --- Input Validation Start ---
    if not isinstance(query, str):
        raise TypeError(
            f"Argument 'query' must be a string, but got {type(query).__name__}."
        )
    # --- Input Validation End ---

    # Start with all messages from all channels
    messages_list = []
    for channel_id, channel_data in DB.get("channels", {}).items():
        if "messages" in channel_data:
            for msg in channel_data["messages"]:
                # Add channel info to each message
                msg_with_channel = dict(msg)
                msg_with_channel["channel"] = channel_id
                msg_with_channel["channel_name"] = channel_data.get("name", "")
                messages_list.append(msg_with_channel)

    # If no query, return all messages
    if not query.strip():
        return messages_list

    filters = _parse_query(query)
    
    # Apply filters progressively
    if filters["user"]:
        messages_list = [
            msg for msg in messages_list
            if msg.get("user", "") == filters["user"]
        ]
    
    if filters["channel"]:
        messages_list = [
            msg for msg in messages_list
            if msg.get("channel_name", "") == filters["channel"]
        ]
    
    # Handle has: filters with traditional filtering
    if "link" in filters["has"]:
        messages_list = [
            msg for msg in messages_list
            if msg.get("links") and len(msg.get("links", [])) > 0
        ]
    
    if "reaction" in filters["has"]:
        messages_list = [
            msg for msg in messages_list
            if msg.get("reactions") and len(msg.get("reactions", [])) > 0
        ]
    
    if "star" in filters["has"]:
        messages_list = [
            msg for msg in messages_list
            if msg.get("is_starred", False)
        ]
    
    # Handle date filters with traditional filtering
    if filters["date_before"] or filters["date_after"] or filters["date_during"]:
        messages_list = [
            msg for msg in messages_list
            if _matches_filters(msg, filters, msg.get("channel_name", ""))
        ]
    
    # Handle exclusions with traditional filtering
    if filters["excluded"]:
        for excluded_word in filters["excluded"]:
            messages_list = [
                msg for msg in messages_list
                if excluded_word.lower() not in msg.get("text", "").lower()
            ]
    
    # Handle text queries with search engine
    if filters["text"]:
        engine = search_engine_manager.get_engine()
        
        if filters["boolean"] == "OR":
            # OR logic: find messages matching any text term
            text_matched_ids = set()
            for text_term in filters["text"]:
                search_results = engine.search(text_term, {
                    "resource_type": "message", 
                    "content_type": "text"
                })
                for result in search_results:
                    # The search engine returns the original JSON object directly
                    if result:
                        # Create unique identifier for message
                        msg_id = f"{result.get('ts', '')}_{result.get('channel', '')}"
                        text_matched_ids.add(msg_id)
            
            # Filter messages list to only include those that matched text search
            messages_list = [
                msg for msg in messages_list
                if f"{msg.get('ts', '')}_{msg.get('channel', '')}" in text_matched_ids
            ]
        else:
            # AND logic: find messages matching all text terms
            for text_term in filters["text"]:
                search_results = engine.search(text_term, {
                    "resource_type": "message", 
                    "content_type": "text"
                })
                matched_ids = set()
                for result in search_results:
                    # The search engine returns the original JSON object directly
                    if result:
                        msg_id = f"{result.get('ts', '')}_{result.get('channel', '')}"
                        matched_ids.add(msg_id)
                
                # Filter messages list to only include those that matched this term
                messages_list = [
                    msg for msg in messages_list
                    if f"{msg.get('ts', '')}_{msg.get('channel', '')}" in matched_ids
                ]
    
    # Handle wildcard matching with traditional filtering (fallback)
    if filters["wildcard"]:
        pattern = filters["wildcard"].replace("*", "")
        messages_list = [
            msg for msg in messages_list
            if pattern.lower() in msg.get("text", "").lower()
        ]

    return messages_list


def search_files(query: str) -> List[Dict[str, Any]]:
    """
    Searches for files matching a query.

    The query is a space-separated string of terms and filters. Text terms are
    matched against the file's name and title. If multiple text terms are
    provided, a match occurs if any term is found (OR logic).

    Args:
        query (str): The search query. The structure is a space-separated string
            of terms and filters. Supported filters for files are:
            - `in:#<channel>`: Restricts the search to a specific channel.
            - `filetype:<type>`: Narrows search to a specific file type (e.g., 'pdf', 'image').
            - `has:star`: Narrows search to files that have been starred.
            Note: Date filters, user filters (`from:`), exclusion (`-`), and
            wildcards (`*`) are not applicable to file searches.

    Returns:
        List[Dict[str, Any]]: List of matching files, where each file contains:
            - id (str): File ID
            - name (str): File name
            - title (str): File title
            - filetype (str): File type
            - channels (List[str]): List of channel IDs where file is shared
            - is_starred (bool): Whether the file is starred
    """
    # --- Input Validation Start ---
    if not isinstance(query, str):
        raise TypeError(
            f"Argument 'query' must be a string, but got {type(query).__name__}."
        )
    # --- Input Validation End ---

    # Start with all files from all channels
    files_list = []
    for channel_id, channel_data in DB.get("channels", {}).items():
        if "files" in channel_data:
            for file_id, file_info in channel_data["files"].items():
                # Add file ID and channel info
                file_with_info = dict(file_info)
                if "id" not in file_with_info:
                    file_with_info["id"] = file_id
                file_with_info["channels"] = [channel_id]
                file_with_info["channel_names"] = [channel_data.get("name", "")]
                files_list.append(file_with_info)

    # Also include global files
    for file_id, file_info in DB.get("files", {}).items():
        file_with_info = dict(file_info)
        if "id" not in file_with_info:
            file_with_info["id"] = file_id
        if "channels" not in file_with_info:
            file_with_info["channels"] = []
        file_with_info["channel_names"] = []
        files_list.append(file_with_info)

    # If no query, return all files
    if not query.strip():
        return files_list

    filters = _parse_query(query)

    # Handle channel filter with traditional filtering
    if filters["channel"]:
        files_list = [
            file_info for file_info in files_list
            if filters["channel"] in file_info.get("channel_names", [])
        ]

    # Handle filetype filter with traditional filtering
    if filters["filetype"]:
        files_list = [
            file_info for file_info in files_list
            if file_info.get("filetype", "") == filters["filetype"]
        ]

    # Handle has:star filter with traditional filtering
    if "star" in filters["has"]:
        files_list = [
            file_info for file_info in files_list
            if file_info.get("is_starred", False)
        ]

    # Handle text queries with search engine (OR logic for files)
    if filters["text"]:
        engine = search_engine_manager.get_engine()
        
        text_matched_ids = set()
        for text_term in filters["text"]:
            # Search in file names
            name_results = engine.search(text_term, {
                "resource_type": "file", 
                "content_type": "name"
            })
            # Search in file titles
            title_results = engine.search(text_term, {
                "resource_type": "file", 
                "content_type": "title"
            })

            # Collect matched file IDs
            for result in name_results + title_results:
                # The search engine returns the original JSON object directly
                if result and result.get("id"):
                    text_matched_ids.add(result.get("id"))

        # Filter files list to only include those that matched text search
        files_list = [
            file_info for file_info in files_list
            if file_info.get("id") in text_matched_ids
        ]

    return files_list


def search_all(query: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Searches for messages and files matching a query.

    This function executes a search across both messages and files using a single
    query. The query is a space-separated string of terms and filters. Filters
    are applied to the resource type they are relevant to (e.g., `filetype:`
    only applies to files).

    Args:
        query (str): The search query. The structure is a space-separated string
            of terms and filters.

            For Text Terms:
            - In Messages: Matched against message content. Default logic is AND,
              but `OR` can be used to match any term.
            - In Files: Matched against the file's name and title. The logic is
              always OR (any term match).

            Supported Filters:
            - `in:#<channel>`: (Messages & Files) Restricts search to a channel.
            - `has:star`: (Messages & Files) Narrows to starred items.
            - `from:@<user>`: (Messages-only) Restricts to messages from a user.
            - `has:link`: (Messages-only) Narrows to messages containing a URL.
            - `has:reaction`: (Messages-only) Narrows to messages with reactions.
            - `before:`, `after:`, `during:`: (Messages-only) Date-based filters.
            - `-<word>`: (Messages-only) Excludes messages with the word.
            - `some*`: (Messages-only) Wildcard support.
            - `filetype:<type>`: (Files-only) Narrows to a specific file type.

    Returns:
        Dict[str, List[Dict[str, Any]]]: Dictionary containing:
            - messages (List[Dict[str, Any]]): List of matching messages
            - files (List[Dict[str, Any]]): List of matching files
    """
    if not isinstance(query, str):
        raise TypeError("Search query must be a string.")

    message_results = search_messages(query)
    file_results = search_files(query)

    return {"messages": message_results, "files": file_results}
