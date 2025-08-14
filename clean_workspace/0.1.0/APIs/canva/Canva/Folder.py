# canva/Canva/Folder.py
import time
from typing import Optional, Dict, Any, List
import uuid
import sys

sys.path.append("APIs")

from canva.SimulationEngine.db import DB


def create_folder(name: str, parent_folder_id: str) -> Dict[str, Any]:
    """
    Creates a new folder with the given name under the specified parent folder.

    Args:
        name (str): Name of the new folder (1–255 characters).
        parent_folder_id (str): ID of the parent folder (1–50 characters).

    Returns:
        Dict[str, Any]: Metadata of the newly created folder including:
            - id (str): The folder ID.
            - name (str): The folder name.
            - created_at (int): Timestamp of creation (Unix time).
            - updated_at (int): Timestamp of last update (Unix time).
            - thumbnail (dict):
                - width (int): Width of the thumbnail in pixels.
                - height (int): Height of the thumbnail in pixels.
                - url (str): URL to retrieve the thumbnail image.
            - parent_id (str): ID of the parent folder.

    Raises:
        ValueError: If the name or parent_folder_id is invalid or the parent does not exist.
    """
    if not (1 <= len(name) <= 255):
        raise ValueError("Folder name must be between 1 and 255 characters.")

    if not (1 <= len(parent_folder_id) <= 50):
        raise ValueError("Parent folder ID must be between 1 and 50 characters.")

    folder_id = str(uuid.uuid4())
    timestamp = int(time.time())  # Get current timestamp

    folder_data = {
        "id": folder_id,
        "name": name,
        "created_at": timestamp,
        "updated_at": timestamp,
        "thumbnail": {
            "width": 595,
            "height": 335,
            "url": "https://document-export.canva.com/default-thumbnail.png",
        },
        "parent_id": parent_folder_id,
    }

    if parent_folder_id == "root":
        DB["folders"][folder_id] = {
            "assets": [],
            "Designs": [],
            "folders": [],
            "folder": folder_data,
        }
    else:
        if parent_folder_id not in DB["folders"]:
            raise ValueError("Parent folder ID does not exist.")

        DB["folders"][parent_folder_id]["folders"].append(folder_id)
        DB["folders"][folder_id] = {
            "assets": [],
            "Designs": [],
            "folders": [],
            "folder": folder_data,
        }

    return folder_data


def get_folder(folder_id: str) -> Dict[str, Any]:
    """
    Retrieves metadata for a specific folder.

    Args:
        folder_id (str): ID of the folder to retrieve.

    Returns:
        Dict[str, Any]: A dictionary with the key 'folder' containing:
            - id (str): The folder ID.
            - name (str): The folder name.
            - created_at (int): Timestamp of creation (Unix time).
            - updated_at (int): Timestamp of last update (Unix time).
            - thumbnail (dict):
                - width (int): Width of the thumbnail in pixels.
                - height (int): Height of the thumbnail in pixels.
                - url (str): URL to retrieve the thumbnail image.
            - parent_id (str): ID of the parent folder.

    Raises:
        ValueError: If the folder ID does not exist.
    """
    if folder_id not in DB["folders"]:
        raise ValueError("Folder ID does not exist.")

    return {"folder": DB["folders"][folder_id]["folder"]}


def update_folder(folder_id: str, name: str) -> Dict[str, Any]:
    """
    Updates the name of a folder and its modification timestamp.

    Args:
        folder_id (str): ID of the folder to update.
        name (str): New name for the folder (1–255 characters).

    Returns:
        Dict[str, Any]: A dictionary with the key 'folder' containing updated folder metadata:
            - id (str): The folder ID.
            - name (str): The updated folder name.
            - created_at (int): Timestamp of creation (unchanged).
            - updated_at (int): Updated timestamp (Unix time).
            - thumbnail (dict):
                - width (int): Width of the thumbnail in pixels.
                - height (int): Height of the thumbnail in pixels.
                - url (str): URL to retrieve the thumbnail image.
            - parent_id (str): ID of the parent folder.

    Raises:
        ValueError: If the folder does not exist or name is invalid.
    """
    if folder_id not in DB["folders"]:
        raise ValueError("Folder ID does not exist.")

    if not (1 <= len(name) <= 255):
        raise ValueError("Folder name must be between 1 and 255 characters.")

    DB["folders"][folder_id]["folder"]["name"] = name
    DB["folders"][folder_id]["folder"]["updated_at"] = int(time.time())

    return {"folder": DB["folders"][folder_id]["folder"]}


def delete_folder(folder_id: str) -> Dict[str, Any]:
    """
    Deletes a folder and all its contents recursively.

    Args:
        folder_id (str): ID of the folder to delete.

    Returns:
        Dict[str, Any]: Returns a success message on successful deletion with structure:
            - message (str): Success message indicating the folder and its contents were deleted

    Raises:
        ValueError: If the folder ID does not exist.
    """
    if folder_id not in DB["folders"]:
        raise ValueError("Folder ID does not exist.")

    parent_id = DB["folders"][folder_id]["folder"].get("parent_id")

    def recursive_delete(folder_id: str):
        for subfolder_id in DB["folders"][folder_id]["folders"]:
            recursive_delete(subfolder_id)

        for asset_id in DB["folders"][folder_id]["assets"]:
            if asset_id in DB["assets"]:
                del DB["assets"][asset_id]

        del DB["folders"][folder_id]

    recursive_delete(folder_id)

    if parent_id and parent_id in DB["folders"]:
        DB["folders"][parent_id]["folders"].remove(folder_id)

    return {"message": "Folder and its contents deleted successfully."}


def list_folder_items(
    folder_id: str,
    item_types: Optional[List[str]] = None,
    sort_by: Optional[str] = "modified_descending",
    continuation: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Lists items (folders, designs, images) within a specified folder.

    Args:
        folder_id (str): The ID of the folder to list items from.
        item_types (Optional[List[str]]): Comma-delimited list of item types to filter by.
            Valid values: "folder", "design", "image".
        sort_by (Optional[str]): Field used to sort the results.
            Valid values:
                - "created_ascending"
                - "created_descending"
                - "modified_ascending"
                - "modified_descending" (default)
                - "title_ascending"
                - "title_descending"
        continuation (Optional[str]): Continuation token for paginated responses.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - items (List[Dict[str, Any]]): An array of folder items. Each item includes:
                - type (str): The item type ("folder", "design", or "image").

                If type == "folder":
                    - folder (dict):
                        - id (str): The folder ID.
                        - name (str): The folder name.
                        - created_at (int): Creation timestamp (Unix time).
                        - updated_at (int): Last updated timestamp.
                        - thumbnail (dict, optional):
                            - width (int)
                            - height (int)
                            - url (str)

                If type == "design":
                    - design (dict):
                        - id (str)
                        - title (str, optional)
                        - created_at (int)
                        - updated_at (int)
                        - page_count (int, optional)
                        - urls (dict):
                            - edit_url (str)
                            - view_url (str)
                        - thumbnail (dict, optional):
                            - width (int)
                            - height (int)
                            - url (str)

                If type == "image":
                    - image (dict):
                        - id (str)
                        - name (str)
                        - tags (List[str])
                        - type (str)
                        - created_at (int)
                        - updated_at (int)
                        - thumbnail (dict, optional):
                            - width (int)
                            - height (int)
                            - url (str)

            - continuation (Optional[str]): Continuation token to retrieve the next page of results, if available.

    Raises:
        ValueError: If the folder ID does not exist.
    """
    if folder_id not in DB["folders"]:
        raise ValueError("Folder ID does not exist.")

    folder_items = {
        "items": [],
        "continuation": None,  # Placeholder for pagination if needed
    }

    items = []

    if not item_types or "folder" in item_types:
        for subfolder_id in DB["folders"][folder_id]["folders"]:
            items.append(
                {"type": "folder", "folder": DB["folders"][subfolder_id]["folder"]}
            )

    if not item_types or "design" in item_types:
        for design_id in DB["folders"][folder_id]["Designs"]:
            items.append({"type": "design", "design": DB["designs"].get(design_id, {})})

    if not item_types or "image" in item_types:
        for asset_id in DB["folders"][folder_id]["assets"]:
            items.append({"type": "image", "image": DB["assets"].get(asset_id, {})})

    sort_options = {
        "created_ascending": lambda x: x["folder"].get("created_at", 0),
        "created_descending": lambda x: -x["folder"].get("created_at", 0),
        "modified_ascending": lambda x: x["folder"].get("updated_at", 0),
        "modified_descending": lambda x: -x["folder"].get("updated_at", 0),
        "title_ascending": lambda x: x["folder"].get("name", ""),
        "title_descending": lambda x: x["folder"].get("name", ""),
    }

    if sort_by in sort_options:
        items.sort(key=sort_options[sort_by])

    folder_items["items"] = items
    return folder_items
