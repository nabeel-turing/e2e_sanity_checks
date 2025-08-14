from typing import Dict, List, Optional

from pydantic import ValidationError

from youtube.SimulationEngine.custom_errors import InvalidMaxResultsError, MissingPartParameterError
from youtube.SimulationEngine.custom_errors import InvalidPartParameterError
from youtube.SimulationEngine.models import SnippetInputModel, TopLevelCommentInputModel
from youtube.SimulationEngine.db import DB
from youtube.SimulationEngine.utils import generate_random_string, generate_entity_id
from typing import Optional, Dict, Any, List


def insert(
    part: str, snippet: Optional[Dict] = None, top_level_comment: Optional[Dict] = None
) -> Dict[str, Dict]:
    """
    Inserts a new comment thread.

    Args:
        part (str): The part parameter specifies the commentThread resource properties
                    that the API response will include. Currently, only "snippet" is supported.
        snippet (Optional[Dict]): The snippet object contains details about the comment thread.
                                   This is treated as arbitrary thread metadata.
        top_level_comment (Optional[Dict]): The top-level comment for the thread.
                                            If provided, it's expected to be a dictionary
                                            potentially containing an 'id' (str) key.

    Returns:
        Dict[str, Dict]: A dictionary containing:
            - If insertion is successful:
                - success (bool): True
                - commentThread (Dict): The newly created comment thread object:
                    - id (str): Unique thread ID.
                    - snippet (Dict): Thread metadata.
                    - comments (List[str]): List of comment IDs in the thread.
    Raises:
        TypeError: If 'part' is not a string.
        InvalidPartParameterError: If the 'part' parameter is not "snippet".
        pydantic.ValidationError: If 'snippet' or 'top_level_comment' (when provided)
                                  do not conform to their expected dictionary structures
                                  (e.g., not a dictionary, or 'top_level_comment.id'
                                  is not a string if provided).
    """
    # 1. Standard Type Validation for non-dictionary arguments
    if not isinstance(part, str):
        raise TypeError("Parameter 'part' must be a string.")

    # 2. Business logic / Value validation for 'part'
    if part != "snippet":
        raise InvalidPartParameterError(
            f"Invalid 'part' parameter: '{part}'. Must be 'snippet'."
        )
    
    if snippet is not None and not isinstance(snippet, dict):
        raise TypeError("Parameter 'snippet' must be a dictionary.")
    
    if top_level_comment is not None and not isinstance(top_level_comment, dict):
        raise TypeError("Parameter 'top_level_comment' must be a dictionary.")

    # 3. Pydantic Validation for 'snippet'
    validated_snippet_model: Optional[SnippetInputModel] = None
    if snippet is not None:
        try:
            validated_snippet_model = SnippetInputModel(**snippet)
        except ValidationError as e:
            # Re-raise Pydantic's error. Could be wrapped in a custom error if needed.
            # Add context to the error, e.g., which parameter failed.
            # For now, just re-raising for simplicity as per instructions.
            raise e


    # 4. Pydantic Validation for 'top_level_comment'
    validated_top_level_comment_model: Optional[TopLevelCommentInputModel] = None
    if top_level_comment is not None:
        try:
            validated_top_level_comment_model = TopLevelCommentInputModel(**top_level_comment)
        except ValidationError as e:
            raise e


    # generate_entity_id and DB are assumed to be defined globally or imported
    new_id = generate_entity_id("commentthread")

    # Use validated Pydantic model for snippet data, defaulting to {} if None or empty
    snippet_data_for_thread = {}
    if validated_snippet_model:
        snippet_data_for_thread = validated_snippet_model.model_dump(exclude_none=True)
    # This handles the original `snippet or {}` logic:
    # If snippet was None, validated_snippet_model is None -> snippet_data_for_thread = {}
    # If snippet was {}, validated_snippet_model is SnippetInputModel() -> .model_dump() is {} -> snippet_data_for_thread = {}

    new_thread = {
        "id": new_id,
        "snippet": snippet_data_for_thread,
        "comments": [],
    }

    if "commentThreads" not in DB:
        DB["commentThreads"] = {}

    DB["commentThreads"][new_id] = new_thread

    if validated_top_level_comment_model:
        # Access 'id' via the Pydantic model attribute
        top_level_comment_id = validated_top_level_comment_model.id
        if top_level_comment_id:
            new_thread["comments"].append(top_level_comment_id)

    return {"success": True, "commentThread": new_thread}


def list(
    part: str,
    thread_id: Optional[str] = None,
    channel_id: Optional[str] = None,
    video_id: Optional[str] = None,
    all_threads_related_to_channel_id: Optional[str] = None,
    search_terms: Optional[str] = None,
    moderation_status: Optional[str] = None,
    order: Optional[str] = None,
    max_results: Optional[int] = None,
    page_token: Optional[str] = None,
    text_format: Optional[str] = None,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Retrieves a list of comment threads with optional filters.

    Args:
        part (str): The part parameter specifies the commentThread resource properties that the API response will include. Cannot be empty.
        thread_id (Optional[str]): The id parameter identifies the comment thread that is being retrieved.
        channel_id (Optional[str]): The channelId parameter specifies a YouTube channel ID. The API will only return that channel's comment threads.
        video_id (Optional[str]): The videoId parameter identifies the video for which the API should return comment threads.
        all_threads_related_to_channel_id (Optional[str]): The allThreadsRelatedToChannelId parameter specifies a YouTube channel ID. The API will return all comment threads related to that channel.
        search_terms (Optional[str]): The searchTerms parameter specifies the search terms to use when filtering comment threads.
        moderation_status (Optional[str]): The moderationStatus parameter specifies the moderation status of comments to include in the response.
        order (Optional[str]): The order parameter specifies the order in which the API response should list comment threads.
        max_results (Optional[int]): The maxResults parameter specifies the maximum number of items that should be returned in the result set. Must be a positive integer if provided.
        page_token (Optional[str]): The pageToken parameter identifies a specific page in the result set that should be returned.
        text_format (Optional[str]): The textFormat parameter specifies the format of the text in the comments.

    Returns:
        Dict[str, List[Dict[str, Any]]]: A dictionary containing:
            - items (List[Dict[str, Any]]): List of matching commentThread objects:
                - id (str)
                - snippet (Dict)
                - comments (List[str])

    Raises:
        MissingPartParameterError: If the 'part' parameter is not provided or is an empty string.
        InvalidMaxResultsError: If 'max_results' is provided but is not a positive integer.
        TypeError: If any parameter is of an incorrect type (e.g., 'part' is not a string,
                   'max_results' is not an integer when provided, other string parameters
                   are not strings when provided).
        KeyError: If expected keys (e.g., 'commentThreads') are missing from the DB structure
                  (propagated from internal DB access).
    """
    # --- Input Validation ---
    if not part: # Checks for empty string
        raise MissingPartParameterError("Parameter 'part' is required and cannot be empty.")

    if not isinstance(part, str):
        raise TypeError("Parameter 'part' must be a string.")

    if thread_id is not None and not isinstance(thread_id, str):
        raise TypeError("Parameter 'thread_id' must be a string if provided.")
    if channel_id is not None and not isinstance(channel_id, str):
        raise TypeError("Parameter 'channel_id' must be a string if provided.")
    if video_id is not None and not isinstance(video_id, str):
        raise TypeError("Parameter 'video_id' must be a string if provided.")
    if all_threads_related_to_channel_id is not None and not isinstance(all_threads_related_to_channel_id, str):
        raise TypeError("Parameter 'all_threads_related_to_channel_id' must be a string if provided.")
    if search_terms is not None and not isinstance(search_terms, str):
        raise TypeError("Parameter 'search_terms' must be a string if provided.")
    if moderation_status is not None and not isinstance(moderation_status, str):
        raise TypeError("Parameter 'moderation_status' must be a string if provided.")
    if order is not None and not isinstance(order, str):
        raise TypeError("Parameter 'order' must be a string if provided.")
    if page_token is not None and not isinstance(page_token, str):
        raise TypeError("Parameter 'page_token' must be a string if provided.")
    if text_format is not None and not isinstance(text_format, str):
        raise TypeError("Parameter 'text_format' must be a string if provided.")

    if max_results is not None:
        if not isinstance(max_results, int):
            raise TypeError("Parameter 'max_results' must be an integer if provided.")
        if max_results <= 0:
            raise InvalidMaxResultsError("Parameter 'max_results' must be a positive integer if provided.")
    # --- End of Input Validation ---


    # DB access below assumes DB is defined and populated in the global scope.
    # These operations might raise KeyError if DB or its keys are not structured as expected.
    if "commentThreads" not in DB: # type: ignore
        return {"items": []}

    filtered_threads = []
    for thread in DB["commentThreads"].values():
        filtered_threads.append(thread)

    if thread_id:
        filtered_threads = [
            thread for thread in filtered_threads if thread["id"] == thread_id
        ]

    if channel_id:
        filtered_threads = [
            thread
            for thread in filtered_threads
            if thread.get("snippet", {}).get("channelId") == channel_id
        ]

    if video_id:
        filtered_threads = [
            thread
            for thread in filtered_threads
            if thread.get("snippet", {}).get("videoId") == video_id
        ]

    if all_threads_related_to_channel_id:
        filtered_threads = [
            thread
            for thread in filtered_threads
            if thread.get("snippet", {}).get("channelId")
            == all_threads_related_to_channel_id
            or thread.get("snippet", {}).get("videoId")
            == all_threads_related_to_channel_id
        ]

    if search_terms:
        filtered_threads = [
            thread
            for thread in filtered_threads
            if search_terms.lower() in str(thread.get("snippet", {})).lower()
        ]

    if moderation_status:
        filtered_threads = [
            thread
            for thread in filtered_threads
            if all(
                DB.get("comments", {}).get(comment_id, {}).get("moderationStatus")
                == moderation_status
                for comment_id in thread.get("comments", [])
            )
        ]
    if max_results:
        filtered_threads = filtered_threads[:max_results]

    return {"items": filtered_threads}


def delete(thread_id: str) -> Dict[str, str]:
    """
    Deletes a comment thread by its ID.

    Args:
        thread_id (str): The ID of the comment thread to delete.

    Returns:
        Dict[str, str]: a dictionary with one of these keys:
            success: A message indicating successful deletion.
            error: An error message if the thread is not found.
    """
    if thread_id not in DB.get("commentThreads", {}):
        return {"error": "Thread not found"}

    del DB["commentThreads"][thread_id]
    return {"success": "Thread deleted successfully"}


def update(
    thread_id: str, snippet: Optional[Dict] = None, comments: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Updates an existing comment thread.

    Args:
        thread_id (str): The ID of the comment thread to update.
        snippet (Optional[Dict]): The snippet object contains details about the comment thread.
        comments (Optional[List[str]]): A list of comment IDs associated with the thread.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - If successful:
                - success (str): Success message with thread ID.
                - commentThread (Dict): The updated comment thread object:
                    - id (str)
                    - snippet (Dict)
                    - comments (List[str])
            - If an error occurs:
                - error (str): Error message (e.g., thread not found or no update data).

    """
    if not any([snippet, comments]):
        return {"error": "No update parameters provided"}

    if thread_id not in DB.get("commentThreads", {}):
        return {"error": f"Thread ID: {thread_id} not found in the database."}

    if snippet is not None:
        DB["commentThreads"][thread_id]["snippet"] = snippet
    if comments is not None:
        DB["commentThreads"][thread_id]["comments"] = comments

    return {
        "success": f"Thread ID: {thread_id} updated successfully.",
        "commentThread": DB["commentThreads"][thread_id],
    }
