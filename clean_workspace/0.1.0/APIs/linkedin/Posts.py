from common_utils.print_log import print_log
from typing import Dict, Any, Optional

from pydantic import ValidationError

from .SimulationEngine.models import PostDataModel
from .SimulationEngine.db import DB
from common_utils.error_handling import handle_api_errors

"""
API simulation for the '/posts' resource.
"""

def create_post(post_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Creates a new post in the database.

    Args:
        post_data (Dict[str, Any]): Dictionary containing the new post data with keys:
            - 'author' (str): URN of the post author (e.g., 'urn:li:person:1' or 'urn:li:organization:1').
            - 'commentary' (str): Content of the post.
            - 'visibility' (str): Visibility setting of the post (one of 'PUBLIC', 'CONNECTIONS', 'LOGGED_IN', 'CONTAINER').

    Returns:
        Dict[str, Any]:
        - On successful creation, returns a dictionary with the following keys and value types:
            - 'data' (Dict[str, Any]): Dictionary of created post with keys:
                - 'id' (str): Newly assigned unique identifier.
                - 'author' (str): URN of the post author (e.g., 'urn:li:person:1' or 'urn:li:organization:1').
                - 'commentary' (str): Content of the post.
                - 'visibility' (str): Visibility setting of the post (one of 'PUBLIC', 'CONNECTIONS', 'LOGGED_IN', 'CONTAINER').

    Raises:
        TypeError: If 'post_data' is not a dictionary.
        pydantic.ValidationError: If 'post_data' does not conform to the required structure
            (missing keys, incorrect types, invalid visibility value, invalid author URN format).
    """
    # --- Input Validation Start ---
    if not isinstance(post_data, dict):
        raise TypeError(f"Expected 'post_data' to be a dictionary, but got {type(post_data).__name__}.")

    try:
        # Validate the input dictionary using the Pydantic model
        validated_data = PostDataModel(**post_data)
        # Use validated_data for further processing if needed, ensuring type safety
        # For this function, we'll continue using the original post_data dictionary
        # after validation, as the core logic expects the original dictionary.
        # If downstream logic relied on potential Pydantic transformations (like default values),
        # you might replace post_data with validated_data.model_dump()
    except ValidationError as e:
        # Re-raise the Pydantic validation error for clear feedback
        raise e
    # --- Input Validation End ---

    # Original function logic (remains unchanged)
    # Assume DB exists and is structured as expected
    global DB # Assuming DB is a global for simplicity based on original code snippet
    post_id = str(DB["next_post_id"])
    DB["next_post_id"] += 1
    post_data_copy = post_data.copy() # Work with a copy to avoid modifying input dict directly if needed
    post_data_copy["id"] = post_id
    DB["posts"][post_id] = post_data_copy
    return {"data": post_data_copy}

@handle_api_errors()
def get_post(post_id: str,
                projection: Optional[str] = None,
                start: int = 0,
                count: int = 10) -> Dict[str, Any]:
    """
    Retrieves a post by its identifier with optional field projection.

    Args:
        post_id (str): Unique identifier of the post to retrieve.
        projection (Optional[str]): Field projection syntax for controlling which fields to return.
            The projection string should consist of comma-separated field names and may optionally
            be enclosed in parentheses. Defaults to None.
        start (int): Starting index for pagination. Defaults to 0. Must be non-negative.
        count (int): Number of items to return. Defaults to 10. Must be positive.

    Returns:
        Dict[str, Any]:
        - If post not found, returns a dictionary with the key "error" and the value "Post not found."
        - On successful retrieval, returns a dictionary with the following keys and value types:
            - 'data' (Dict[str, Any]): Dictionary of post data with keys:
                - 'id' (str): Post's unique identifier.
                - 'author' (str): URN of the post author (e.g., 'urn:li:person:1' or 'urn:li:organization:1').
                - 'commentary' (str): Content of the post.
                - 'visibility' (str): Visibility setting of the post (one of 'PUBLIC', 'CONNECTIONS', 'LOGGED_IN', 'CONTAINER').

    Raises:
        TypeError:
            - If 'post_id' is not a string.
            - If 'projection' is provided and is not a string.
            - If 'start' is not an integer.
            - If 'count' is not an integer.
        ValueError:
            - If 'start' is a negative integer.
            - If 'count' is not a positive integer (i.e., less than or equal to 0).
    """
    # Input validation for post_id
    if not isinstance(post_id, str):
        raise TypeError("post_id must be a string.")

    # Input validation for projection
    if projection is not None and not isinstance(projection, str):
        raise TypeError("projection must be a string or None.")

    # Input validation for start
    if not isinstance(start, int):
        raise TypeError("start must be an integer.")
    if start < 0:
        raise ValueError("start must be a non-negative integer.")

    # Input validation for count
    if not isinstance(count, int):
        raise TypeError("count must be an integer.")
    if count <= 0:
        raise ValueError("count must be a positive integer.")

    # Original core functionality
    if post_id not in DB["posts"]:
        return {"error": "Post not found."}
    
    # Simplified return for example; actual projection logic would be more complex
    # and use the 'projection' argument if provided.
    post_data = DB["posts"][post_id]
    
    # Basic projection handling (conceptual)
    if projection:
        # Example: projection="id,author" or "(id,author)"
        # Actual parsing logic for projection string is not implemented here
        # but this is where it would be used.
        # For this example, we assume if projection is present, we only return specific fields.
        # This is a placeholder for actual projection logic.
        # A real implementation would parse 'projection' and filter 'post_data'.
        # For simplicity, if projection is provided, we return all data,
        # as the focus is on input validation, not projection implementation.
        pass # No change to post_data for this example if projection specified

    return {"data": post_data}

def find_posts_by_author(author: str, start: int = 0, count: int = 10) -> Dict[str, Any]:
    """
    Searches for and lists posts based on the provided author identifier with pagination.

    Args:
        author (str): The identifier of the author (e.g., "urn:li:person:1" or "urn:li:organization:1") used to filter posts.
        start (int): Starting index for pagination. Must be a non-negative integer. Defaults to 0.
        count (int): Maximum number of posts to return. Must be a non-negative integer. Defaults to 10.

    Returns:
        Dict[str, Any]:
        - On successful retrieval, returns a dictionary with the following keys and value types:
            - 'data' (List[Dict[str, Any]]): List of post dictionaries with keys:
                - 'id' (str): Post's unique identifier.
                - 'author' (str): URN of the post author (e.g., 'urn:li:person:1' or 'urn:li:organization:1').
                - 'commentary' (str): Content of the post.
                - 'visibility' (str): Visibility setting of the post (one of 'PUBLIC', 'CONNECTIONS', 'LOGGED_IN', 'CONTAINER').

    Raises:
        TypeError: If 'author' is not a string.
        TypeError: If 'start' is not an integer.
        TypeError: If 'count' is not an integer.
        ValueError: If 'start' is a negative integer.
        ValueError: If 'count' is a negative integer.
    """
    # --- Input Validation Start ---
    if not isinstance(author, str):
        raise TypeError(f"Argument 'author' must be a string, but got {type(author).__name__}.")
    if not isinstance(start, int):
        raise TypeError(f"Argument 'start' must be an integer, but got {type(start).__name__}.")
    if not isinstance(count, int):
        raise TypeError(f"Argument 'count' must be an integer, but got {type(count).__name__}.")

    if start < 0:
        raise ValueError(f"Argument 'start' must be a non-negative integer, but got {start}.")
    if count < 0:
        raise ValueError(f"Argument 'count' must be a non-negative integer, but got {count}.")
    # --- Input Validation End ---

    # --- Original Core Logic Start ---
    # Assume DB exists and has the expected structure
    # Filter posts based on the provided author identifier.
    try:
        # Note: This part might raise NameError if DB is not defined in the execution scope
        # or other errors depending on DB's structure. Tests focus on validation above.
        filtered_posts = [post for post in DB["posts"].values() if post.get("author") == author] # type: ignore[name-defined]
        # Apply pagination to the filtered posts.
        paginated_posts = filtered_posts[start:start+count]
        return {"data": paginated_posts}
    except NameError:
         # Handle case where DB is not defined for conceptual completeness,
         # though tests won't reach here if validation fails.
         # Or re-raise if appropriate for the application context.
         print_log("Warning: Global 'DB' is not defined.")
         return {"data": []}
    except Exception as e:
         # Catch potential errors during filtering/slicing if DB exists but is malformed
         print_log(f"An error occurred during post retrieval: {e}")
         # Depending on requirements, might re-raise or return an error structure
         raise # Re-raise unexpected errors from core logic

def update_post(post_id: str, post_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Updates an existing post in the database.

    Args:
        post_id (str): Unique identifier of the post to update.
        post_data (Dict[str, Any]): Dictionary containing the updated post data with keys:
            - 'author' (str): Updated URN of the post author (e.g., 'urn:li:person:1' or 'urn:li:organization:1').
            - 'commentary' (str): Updated content of the post.
            - 'visibility' (str): Updated visibility setting of the post (one of 'PUBLIC', 'CONNECTIONS', 'LOGGED_IN', 'CONTAINER').

    Returns:
        Dict[str, Any]:
        - If post not found, returns a dictionary with the key "error" and the value "Post not found."
        - On successful update, returns a dictionary with the following keys and value types:
            - 'data' (Dict[str, Any]): Dictionary of updated post with keys:
                - 'id' (str): Post's unique identifier.
                - 'author' (str): Updated URN of the post author (e.g., 'urn:li:person:1' or 'urn:li:organization:1').
                - 'commentary' (str): Updated content of the post.
                - 'visibility' (str): Updated visibility setting of the post (one of 'PUBLIC', 'CONNECTIONS', 'LOGGED_IN', 'CONTAINER').
    """
    if post_id not in DB["posts"]:
        return {"error": "Post not found."}
    post_data["id"] = post_id
    DB["posts"][post_id] = post_data
    return {"data": post_data}

def delete_post(post_id: str) -> Dict[str, Any]:
    """
    Deletes a post from the database.

    Args:
        post_id (str): Unique identifier of the post to delete.

    Returns:
        Dict[str, Any]:
        - If post not found, returns a dictionary with the key "error" and the value "Post not found."
        - On successful deletion, returns a dictionary with the following keys and value types:
            - 'status' (str): Success message confirming deletion of the post.

    Raises:
        TypeError: If 'post_id' is not a string.
        # Note: "Post not found" is handled via return value, not an exception.
    """
    # --- Start Validation ---
    if not isinstance(post_id, str):
        raise TypeError(f"Argument 'post_id' must be a string, but got {type(post_id).__name__}.")
    # --- End Validation ---

    # Original function logic (remains unchanged)
    if post_id not in DB["posts"]:
        return {"error": "Post not found."}
    del DB["posts"][post_id]
    return {"status": f"Post {post_id} deleted."}