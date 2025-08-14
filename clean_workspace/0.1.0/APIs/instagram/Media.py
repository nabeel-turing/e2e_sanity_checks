# instagram/Media.py

from .SimulationEngine.custom_erros import InvalidMediaIDError
from .SimulationEngine.custom_erros import UserNotFoundError
from .SimulationEngine.db import DB
from typing import Dict, Any, List
import datetime

# ------------------------------------------------------------------------------
# Media
# ------------------------------------------------------------------------------

"""Handles media-related operations."""


def create_media(user_id: str, image_url: str, caption: str = "") -> Dict[str, Any]:
    """
    Creates a new media post associated with a user.

    Args:
        user_id (str): The ID of the user who owns the media. Must be a non-empty string.
        image_url (str): URL of the media image. Must be a non-empty string.
        caption (str): Caption or description for the media. Must be a string.
                                 Defaults to "".

    Returns:
        Dict[str, Any]:
        - On successful creation, returns a dictionary with the following keys and value types:
            - id (str): The media's unique identifier
            - user_id (str): The ID of the user who owns the media
            - image_url (str): URL of the media image
            - caption (str): Caption or description for the media
            - timestamp (str): ISO format timestamp of when the media was created

    Raises:
        TypeError: If 'user_id', 'image_url', or 'caption' are not of type string.
        ValueError: If 'user_id' or 'image_url' are empty strings.
        UserNotFoundError: If the 'user_id' does not correspond to an existing user.
    """
    # --- Start of new validation logic ---
    if not isinstance(user_id, str):
        raise TypeError("Argument 'user_id' must be a string.")
    if not user_id: # Check for empty string
        raise ValueError("Argument 'user_id' cannot be empty.")

    if not isinstance(image_url, str):
        raise TypeError("Argument 'image_url' must be a string.")
    if not image_url: # Check for empty string
        raise ValueError("Argument 'image_url' cannot be empty.")

    if not isinstance(caption, str):
        raise TypeError("Argument 'caption' must be a string.")
    # --- End of new validation logic ---

    # Core logic (assuming DB and datetime are available in the scope)
    if user_id not in DB["users"]:
        raise UserNotFoundError(f"User with ID '{user_id}' does not exist.")

    # These lines assume 'DB' is a dictionary with 'users' and 'media' keys,
    # and 'datetime' module is available.
    media_id = f"media_{len(DB['media']) + 1}"
    timestamp = datetime.datetime.now().isoformat() # type: ignore

    DB["media"][media_id] = {
        "user_id": user_id,
        "image_url": image_url,
        "caption": caption,
        "timestamp": timestamp,
    }
    return {
        "id": media_id,
        "user_id": user_id,
        "image_url": image_url,
        "caption": caption,
        "timestamp": timestamp,
    }


def list_media() -> List[Dict[str, Any]]:
    """
    Lists all media posts in the system.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, where each dictionary contains:
            - id (str): The media's unique identifier
            - user_id (str): The ID of the user who owns the media
            - image_url (str): URL of the media image
            - caption (str): Caption or description for the media
            - timestamp (str): ISO format timestamp of when the media was created
    """
    return [{"id": media_id, **info} for media_id, info in DB["media"].items()]


def delete_media(media_id: str) -> Dict[str, Any]:
    """
    Deletes a specified media post from the system.

    Args:
        media_id (str): The unique identifier of the media post to delete.
                        Must be a non-empty string.

    Returns:
        Dict[str, Any]:
        - If the media does not exist (after validation passes), returns a dictionary
          with the key "error" and the value "Media not found."
        - On successful deletion, returns a dictionary with the key "success" and the value True.

    Raises:
        TypeError: If media_id is not a string.
        InvalidMediaIDError: If media_id is an empty string.
    """
    # --- Input Validation ---
    if not isinstance(media_id, str):
        raise TypeError("Field media_id must be a string.")
    if not media_id:  # Checks for empty string, e.g., ""
        raise InvalidMediaIDError("Field media_id cannot be empty.")
    # --- End of Input Validation ---

    # Original core functionality
    # DB is assumed to be globally available or otherwise accessible here.
    if media_id in DB["media"]:
        del DB["media"][media_id]
        return {"success": True}
    return {"error": "Media not found"}
