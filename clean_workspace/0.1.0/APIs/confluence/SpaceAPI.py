# APIs/confluence/SpaceAPI.py
from typing import Dict, List, Any, Optional
from pydantic import ValidationError
from confluence.SimulationEngine.db import DB
from confluence.SimulationEngine.models import SpaceBodyInputModel


def get_spaces(
        spaceKey: Optional[str] = None,
        start: int = 0,
        limit: int = 25,
) -> List[Dict[str, str]]:
    """
    Returns a paginated list of all spaces.

    Retrieves a list of space dictionaries for the provided parameters.

    Args:
        spaceKey (Optional[str]): A unique identifier to filter spaces by.
            Defaults to None.
        start (int): The starting index for pagination.
            Defaults to 0.
        limit (int): The maximum number of spaces to return.
            Defaults to 25.

    Returns:
        List[Dict[str, str]]: A list of space dictionaries, each containing:
            - spaceKey (str): The unique identifier of the space.
            - name (str): The display name of the space.
            - description (str): A description of the space.

    Raises:
        TypeError: If spaceKey is provided and is not a string,
                   or if start or limit are not integers.
        ValueError: If the start or limit parameters are negative.
    """
    # --- Input Validation ---
    if spaceKey is not None and not isinstance(spaceKey, str):
        raise TypeError(f"spaceKey must be a string or None, got {type(spaceKey).__name__}")

    if not isinstance(start, int):
        raise TypeError(f"start must be an integer, got {type(start).__name__}")
    if start < 0:
        raise ValueError("start parameter cannot be negative.")

    if not isinstance(limit, int):
        raise TypeError(f"limit must be an integer, got {type(limit).__name__}")
    if limit < 0:
        raise ValueError("limit parameter cannot be negative.")
    # --- End Input Validation ---

    # Original core logic (assumes DB is accessible in this scope)
    all_spaces = list(DB["spaces"].values())
    if spaceKey:
        # In Confluence, spaceKey can be repeated, but let's do a simple approach:
        all_spaces = [s for s in all_spaces if s["spaceKey"] == spaceKey]


    return all_spaces[start: start + limit]

  
def create_space(body: Dict[str, str | Optional[str]]) -> Dict[str, str]:
    """
    Creates a new space.

    Creates and returns a new space dictionary from the provided data.
    Note: If 'name' or 'description' are not provided in the body, Pydantic model
    validation ensures they default to an empty string.

    Args:
        body (Dict[str, str | Optional[str]]): A dictionary containing:
            - key (str): The unique identifier for the space. (Mandatory)
            - name (str): The display name of the space.
            - description (Optional[str]): An optional description of the space, defaults to empty string

    Returns:
        Dict[str, str]: A dictionary representing the newly created space containing:
            - spaceKey (str): The unique identifier of the space (mirrors body['key']).
            - name (str): The display name of the space.
            - description (str): The description of the space.

    Raises:
        pydantic.ValidationError: If the 'body' argument is not a valid dictionary or does not
                                  conform to the SpaceBodyInputModel (e.g., 'key' is missing,
                                  or 'key', 'name', 'description' have incorrect types).
        ValueError: If a space with the provided key already exists.
    """
    try:
        validated_body_model = SpaceBodyInputModel.model_validate(body)
    except ValidationError as e:
        raise e

    spaceKey = validated_body_model.key
    if spaceKey in DB["spaces"]:
        raise ValueError(f"Space with key={spaceKey} already exists.")
    new_space = {
        "spaceKey": spaceKey,
        "name": validated_body_model.name,
        "description": validated_body_model.description,
    }
    DB["spaces"][spaceKey] = new_space
    return new_space


def create_private_space(body: Dict[str, Any]) -> Dict[str, str]:
    """
    Creates a new private space.

    This function behaves identically to create_space and returns a new private space dictionary.

    Args:
        body (Dict[str, Any]): A dictionary containing:
            - key (str): The unique identifier for the space.
            - name (str): The display name of the space.
            - description (Optional[str]): An optional description of the space.

    Returns:
        Dict[str, str]: A dictionary representing the newly created private space containing:
            - spaceKey (str): The unique identifier of the space.
            - name (str): The display name of the space.
            - description (str): The description of the space.

    Raises:
        ValueError: If the 'key' is missing from the body or if a space with the provided key already exists.
    """
    return create_space(body)


def update_space(spaceKey: str, body: Dict[str, Any]) -> Dict[str, str]:
    """
    Updates an existing space.

    Updates and returns a space dictionary for the space specified by spaceKey.

    Args:
        spaceKey (str): The unique identifier of the space to update.
        body (Dict[str, Any]): A dictionary containing the fields to update:
            - name (str): The new display name of the space.
            - description (str): The new description of the space.

    Returns:
        Dict[str, str]: A dictionary representing the updated space containing:
            - spaceKey (str): The unique identifier of the space.
            - name (str): The updated display name of the space.
            - description (str): The updated description of the space.

    Raises:
        ValueError: If no space with the specified spaceKey is found.
    """
    space = DB["spaces"].get(spaceKey)
    if not space:
        raise ValueError(f"Space with key={spaceKey} not found.")
    # Update fields
    if "name" in body:
        space["name"] = body["name"]
    if "description" in body:
        space["description"] = body["description"]
    # ignoring homepage for brevity
    DB["spaces"][spaceKey] = space
    return space


def delete_space(spaceKey: str) -> Dict[str, str]:
    """
    Deletes a space and tracks the deletion task.

    Deletes the space identified by spaceKey and returns a task dictionary that tracks the deletion process.
    Note: The deletion task is simulated and marked as complete immediately.

    Args:
        spaceKey (str): The unique identifier of the space to delete.

    Returns:
        Dict[str, str]: A dictionary containing:
            - id (str): The task identifier.
            - spaceKey (str): The key of the space being deleted.
            - status (str): The current status of the deletion task ("in_progress" or "complete").
            - description (str): A description of the task.

    Raises:
        ValueError: If no space with the specified spaceKey is found.
    """
    if spaceKey not in DB["spaces"]:
        raise ValueError(f"Space with key={spaceKey} not found.")
    task_id = str(DB["long_task_counter"])
    DB["long_task_counter"] += 1
    DB["deleted_spaces_tasks"][task_id] = {
        "id": task_id,
        "spaceKey": spaceKey,
        "status": "in_progress",
        "description": f"Deleting space '{spaceKey}'",
    }
    # We'll pretend it completes immediately for this simulation:
    del DB["spaces"][spaceKey]
    DB["deleted_spaces_tasks"][task_id]["status"] = "complete"
    return DB["deleted_spaces_tasks"][task_id]

def get_space(
    spaceKey: str
) -> Dict[str, str]:
    """
    Retrieves details about a specific space.

    Returns the space dictionary for the provided spaceKey.

    Args:
        spaceKey (str): The unique identifier of the space.

    Returns:
        Dict[str, str]: A dictionary representing the space containing:
            - spaceKey (str): The unique identifier of the space.
            - name (str): The display name of the space.
            - description (str): The description of the space.

    Raises:
        TypeError: If spaceKey is not a string.
        ValueError: If no space with the specified spaceKey is found.
    """
    # Input validation
    if not isinstance(spaceKey, str):
        raise TypeError(f"spaceKey must be a string, but got {type(spaceKey).__name__}.")

    space = DB["spaces"].get(spaceKey) # type: ignore
    if not space:
        raise ValueError(f"Space with key={spaceKey} not found.")
    return space

def get_space_content(
        spaceKey: str,
        depth: Optional[str] = None,
        expand: Optional[str] = None,
        start: int = 0,
        limit: int = 25,
) -> List[Dict[str, Any]]:
    """
    Retrieves the content within a specific space.

    Returns a list of content item dictionaries for the space identified by spaceKey.
    Note: The 'depth' and 'expand' parameters are included for API compatibility but are not fully implemented.

    Args:
        spaceKey (str): The unique identifier of the space. Must be a non-empty string.
        depth (Optional[str]): The depth of content to retrieve. Defaults to None.
        expand (Optional[str]): A comma-separated list of properties to expand. Defaults to None.
        start (int): The starting index for pagination.
            Defaults to 0. Must be a non-negative integer.
        limit (int): The maximum number of content items to return.
            Defaults to 25. Must be a positive integer.

    Returns:
        List[Dict[str, Any]]: A list of content item dictionaries, each containing:
            - id (str): The unique identifier of the content.
            - type (str): The type of content (e.g., "page", "blogpost").
            - title (str): The title of the content.
            - spaceKey (str): The key of the space containing the content.
            - status (str): The current status of the content.
            - body (Dict[str, Any]): A dictionary representing the content body data containing:
                  - storage (Dict[str, Any]): A dictionary with:
                        - value (str): The content value in storage format.
                        - representation (str): The representation type (e.g., "storage").
            - postingDay (Optional[str]): The posting day for blog posts.
            - link (str): The URL path to the content.
            - children (Optional[List[Dict[str, Any]]]): A list of child content items.
            - ancestors (Optional[List[Dict[str, Any]]]): A list of ancestor content items.

    Raises:
        TypeError: If 'spaceKey' is not a string.
        TypeError: If 'start' is not an integer.
        TypeError: If 'limit' is not an integer.
        ValueError: If 'spaceKey' is an empty string.
        ValueError: If 'start' is a negative integer.
        ValueError: If 'limit' is not a positive integer.
    """
    # --- Input Validation ---
    if not isinstance(spaceKey, str):
        raise TypeError("spaceKey must be a string.")
    if not spaceKey:
        raise ValueError("spaceKey must not be an empty string.")
    if not isinstance(start, int):
        raise TypeError("start must be an integer.")
    if start < 0:
        raise ValueError("start must be a non-negative integer.")
    if not isinstance(limit, int):
        raise TypeError("limit must be an integer.")
    if limit <= 0:
        raise ValueError("limit must be a positive integer.")

    all_contents = list(DB["contents"].values())
    results = [c for c in all_contents if c.get("spaceKey") == spaceKey]
    return results[start : start + limit]

def get_space_content_of_type(
    spaceKey: str,
    type: str,
    depth: Optional[str] = None,
    expand: Optional[str] = None,
    start: int = 0,
    limit: int = 25,
) -> List[Dict[str, Any]]:
    """
    Retrieves content of a specific type within a space.

    Returns a list of content item dictionaries matching the specified type for the given spaceKey.
    Note: The function first retrieves all content for the space and then filters by type.
          The 'depth' and 'expand' parameters are accepted for API compatibility but are not fully implemented.

    Args:
        spaceKey (str): The unique identifier of the space.
        depth (Optional[str]): The depth of content to retrieve. Defaults to None.
        expand (Optional[str]): A comma-separated list of properties to expand. Defaults to None.
        type (str): The type of content to filter (e.g., "page", "blogpost").
        start (int): The starting index for pagination after filtering.
            Defaults to 0.
        limit (int): The maximum number of content items to return after filtering.
            Defaults to 25.

    Returns:
        List[Dict[str, Any]]: A list of content item dictionaries, each containing:
            - id (str): The unique identifier of the content.
            - type (str): The type of content.
            - title (str): The title of the content.
            - spaceKey (str): The key of the space containing the content.
            - status (str): The current status of the content.
            - body (Dict[str, Any]): A dictionary representing the content body data containing:
                  - storage (Dict[str, Any]): A dictionary with:
                        - value (str): The content value in storage format.
                        - representation (str): The representation type (e.g., "storage").
            - postingDay (Optional[str]): The posting day for blog posts.
            - link (str): The URL path to the content.
            - children (Optional[List[Dict[str, Any]]]): A list of child content items.
            - ancestors (Optional[List[Dict[str, Any]]]): A list of ancestor content items.

    Raises:
        TypeError: 
            - If 'spaceKey' is not a string.
            - If 'type' is not a string.
            - If 'start' is not an integer.
            - If 'limit' is not an integer.
        ValueError: 
            - If 'spaceKey' is an empty string.
            - If 'type' is an empty string.
            - If 'start' is a negative integer.
            - If 'limit' is not a positive integer.
    """
    # --- Input Validation ---
    if not isinstance(spaceKey, str):
        raise TypeError("spaceKey must be a string.")
    if not spaceKey:
        raise ValueError("spaceKey must not be an empty string.")

    if not isinstance(type, str):
        raise TypeError("type must be a string.")
    if not type:
        raise ValueError("type must not be an empty string.")

    if not isinstance(start, int):
        raise TypeError("start must be an integer.")
    if start < 0:
        raise ValueError("start must be a non-negative integer.")

    if not isinstance(limit, int):
        raise TypeError("limit must be an integer.")
    if limit <= 0:
        raise ValueError("limit must be a positive integer.")
    # --- End Input Validation ---

    # Get all contents and filter by space first
    all_contents = list(DB["contents"].values())
    space_contents = [c for c in all_contents if c.get("spaceKey") == spaceKey]
    
    # Then filter by type
    filtered = [c for c in space_contents if c.get("type") == type]
    return filtered[start : start + limit]
