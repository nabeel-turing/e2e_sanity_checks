# instagram/Comment.py

from .SimulationEngine.custom_erros import MediaNotFoundError
from .SimulationEngine.db import DB
from typing import Dict, Any, List
import datetime

"""Handles comment-related operations."""


def add_comment(media_id: str, user_id: str, message: str) -> Dict[str, Any]:
    """
    Adds a comment to a media post.

    Args:
        media_id (str): The ID of the media post being commented on.
        user_id (str): The ID of the user making the comment.
        message (str): The comment text.

    Returns:
        Dict[str, Any]: On successful creation, a dictionary with the following keys and value types:
            - id (str): The comment's unique identifier
            - media_id (str): The ID of the media post being commented on
            - user_id (str): The ID of the user making the comment
            - message (str): The comment text
            - timestamp (str): ISO format timestamp of when the comment was created

    Raises:
        TypeError: If 'media_id', 'user_id', or 'message' is not a string.
        ValueError: If 'media_id', 'user_id', or 'message' is an empty string.
        MediaNotFoundError: If the media post specified by 'media_id' does not exist.
    """
    # Input Validation for argument types and values
    if not isinstance(media_id, str):
        raise TypeError("Argument 'media_id' must be a string.")
    if not media_id:
        raise ValueError("Field media_id cannot be empty.")

    if not isinstance(user_id, str):
        raise TypeError("Argument 'user_id' must be a string.")
    if not user_id:
        raise ValueError("Field user_id cannot be empty.")

    if not isinstance(message, str):
        raise TypeError("Argument 'message' must be a string.")
    if not message:
        raise ValueError("Field message cannot be empty.")

    # Core Logic (with modification for MediaNotFoundError)
    if media_id not in DB["media"]:
        raise MediaNotFoundError("Media does not exist.") # Matched original error message text

    comment_id = f"comment_{len(DB['comments']) + 1}"
    timestamp = datetime.datetime.now().isoformat()

    DB["comments"][comment_id] = {
        "media_id": media_id,
        "user_id": user_id,
        "message": message,
        "timestamp": timestamp,
    }
    return {
        "id": comment_id,
        "media_id": media_id,
        "user_id": user_id,
        "message": message,
        "timestamp": timestamp,
    }


def list_comments(media_id: str) -> List[Dict[str, Any]]:
    """
    Lists all comments on a specific media post.

    Args:
        media_id (str): The ID of the media post to retrieve comments for.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, where each dictionary contains:
            - id (str): The comment's unique identifier
            - media_id (str): The ID of the media post being commented on
            - user_id (str): The ID of the user who made the comment
            - message (str): The comment text
            - timestamp (str): ISO format timestamp of when the comment was created

    Raises:
        TypeError: If media_id is not a string.
        ValueError: If media_id is an empty string.
    """
    # Input validation for media_id
    if not isinstance(media_id, str):
        raise TypeError("media_id must be a string.")
    if not media_id:  # Check for empty string
        raise ValueError("media_id cannot be an empty string.")

    # Original function logic
    # This part assumes DB is a globally available dictionary-like structure.
    # Potential KeyError if DB["comments"] does not exist or if an item in
    # DB["comments"].values() does not have a "media_id" key.
    # These are not explicitly listed in Raises as they are part of the original
    # function's behavior with its external dependencies rather than input validation failures.
    return [
        {"id": comment_id, **info}
        for comment_id, info in DB["comments"].items() # type: ignore[name-defined]
        if info["media_id"] == media_id
    ]
