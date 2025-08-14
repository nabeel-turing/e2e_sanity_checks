from typing import Dict, List, Optional
from youtube.SimulationEngine.db import DB
from youtube.SimulationEngine.utils import generate_random_string, generate_entity_id
from typing import Optional, Dict, Any, List

"""
    Handles YouTube Comment API operations.
    
    This class provides methods to manage comments on YouTube videos,
    including creating, updating, deleting, and moderating comments.
"""


def set_moderation_status(
    comment_id: str, moderation_status: str, ban_author: bool = False
) -> Dict[str, Any]:
    """
    Sets the moderation status of a comment.

    Args:
        comment_id (str): The ID of the comment to moderate.
        moderation_status (str): The new moderation status. Valid values:
            - "heldForReview"
            - "published"
            - "rejected"
        ban_author (bool): If True, bans the author of the comment when rejecting it. Default to false

    Returns:
        Dict[str, Any]: A dictionary containing:
            - If the comment is found and updated:
                - success (bool): True
                - comment (Dict): The updated comment object:
                    - id (str)
                    - snippet (Dict)
                    - moderationStatus (str)
                    - bannedAuthor (bool)
            - If an error occurs:
                - error (str): Error message
    """
    if comment_id not in DB["comments"]:
        return {"error": "Comment not found"}

    if moderation_status not in ["heldForReview", "published", "rejected"]:
        return {"error": "Invalid moderation status"}

    DB["comments"][comment_id]["moderationStatus"] = moderation_status

    if ban_author and moderation_status == "rejected":
        DB["comments"][comment_id]["bannedAuthor"] = True

    return {"success": True, "comment": DB["comments"][comment_id]}


def delete(comment_id: str) -> Dict[str, bool | str]:
    """
    Deletes a comment.

    Args:
        comment_id (str): The ID of the comment to delete.

    Returns:
        Dict[str, bool | str]: A dictionary containing:
            - If the comment is successfully deleted:
                - success (bool): True
            - If the comment is not found:
                - error (str): Error message
    """
    if comment_id not in DB["comments"]:
        return {"error": "Comment not found"}

    del DB["comments"][comment_id]
    return {"success": True}


def insert(
    part: str,
    snippet: Optional[Dict] = None,
    moderation_status: str = "published",
    banned_author: bool = False,
) -> Dict[str, Any]:
    """
    Inserts a new comment.

    Args:
        part (str): The part parameter specifies the comment resource properties that the API response will include.
        snippet (Optional[Dict]): The snippet object contains details about the comment.
        moderation_status (str): The initial moderation status for the comment.
                          Defaults to "published".
        banned_author (bool): Whether the author of the comment is banned.
                      Defaults to False.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - If insertion is successful:
                - success (bool): True
                - comment (Dict): The newly created comment:
                    - id (str)
                    - snippet (Dict)
                    - moderationStatus (str)
                    - bannedAuthor (bool)
            - If an error occurs:
                - error (str): Error message
    """
    if not part:
        return {"error": "Invalid part parameter"}

    num = str(len(DB["comments"]) + 1)
    new_id = generate_entity_id("comment")
    new_comment = {
        "id": new_id,
        "snippet": snippet or {},
        "moderationStatus": moderation_status,
        "bannedAuthor": banned_author,
    }
    DB["comments"][new_id] = new_comment
    return {"success": True, "comment": new_comment}


def list(
    part: str,
    comment_id: Optional[str] = None,
    parent_id: Optional[str] = None,
    max_results: Optional[int] = None,
    page_token: Optional[str] = None,
    text_format: Optional[str] = None,
) -> Dict[str, List[Dict] | str]:
    """
    Retrieves a list of comments with optional filters.

    Args:
        part (str): The part parameter specifies the comment resource properties that the API response will include.
        comment_id (Optional[str]): The id parameter identifies the comment that is being retrieved.
        parent_id (Optional[str]): The parentId parameter identifies the comment for which replies should be retrieved.
        max_results (Optional[int]): The maxResults parameter specifies the maximum number of items that should be returned in the result set.
        page_token (Optional[str]): The pageToken parameter identifies a specific page in the result set that should be returned. Currently not used !
        text_format (Optional[str]): The textFormat parameter specifies the format of the text in the comment. Currently not used !

    Returns:
        Dict[str, List[Dict] | str]: A dictionary containing:
        - If successful:
            - items (List[Dict]): A list of comment resources matching the filters:
                - id (str)
                - snippet (Dict)
                - moderationStatus (str)
                - bannedAuthor (bool)
        - If an error occurs:
            - error (str): Error message
    """
    if not part:
        return {"error": "Part parameter required"}

    # Access comments directly from DB
    comments_dict = dict(DB.get("comments", {}))
    filtered_comments = []

    # Convert dictionary values to list
    for comment_key, comment_data in comments_dict.items():
        if comment_id and comment_data["id"] != comment_id:
            continue
        if parent_id and comment_data.get("snippet", {}).get("parentId") != parent_id:
            continue
        filtered_comments.append(comment_data)

    if max_results:
        filtered_comments = filtered_comments[:max_results]

    return {"items": filtered_comments}


def mark_as_spam(comment_id: str) -> Dict[str, Any]:
    """
    Marks a comment as spam.

    Args:
        comment_id (str): The ID of the comment to mark as spam.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - If successful:
                - success (bool): True
                - comment (Dict): The updated comment object
            - If the comment is not found:
                - error (str): Error message
    """
    if comment_id not in DB.get("comments", {}):
        return {"error": "Comment not found"}

    DB["comments"][comment_id]["moderationStatus"] = "heldForReview"
    return {"success": True, "comment": DB["comments"][comment_id]}


def update(
    comment_id: str,
    snippet: Optional[Dict] = None,
    moderation_status: Optional[str] = None,
    banned_author: Optional[bool] = None,
) -> Dict[str, str]:
    """
    Updates an existing comment.

    Args:
        comment_id (str): The ID of the comment to update.
        snippet (Optional[Dict]): The snippet object contains details about the comment.
        moderation_status (Optional[str]): The new moderation status for the comment.
        banned_author (Optional[bool]): Whether the author of the comment is banned.

    Returns:
        Dict[str, str]: A dictionary containing:
            - If successful:
                - success (str): A success message with comment ID.
            - If comment not found or no fields provided:
                - error (str): Error message.
    """
    if not any([snippet, moderation_status, banned_author]):
        return {"error": "No update parameters provided"}

    if comment_id not in DB.get("comments", {}):
        return {"error": f"Comment ID: {comment_id} not found in the database."}

    if snippet is not None:
        DB["comments"][comment_id]["snippet"] = snippet
    if moderation_status is not None:
        DB["comments"][comment_id]["moderationStatus"] = moderation_status
    if banned_author is not None:
        DB["comments"][comment_id]["bannedAuthor"] = banned_author

    return {"success": f"Comment ID: {comment_id} updated successfully."}
