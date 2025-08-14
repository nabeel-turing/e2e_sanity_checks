# canva/Canva/Design/Comment.py
from typing import Optional, Dict, Any
import sys
import os

sys.path.append("APIs")

from canva.SimulationEngine.db import DB


def create_thread(
    design_id: str, message: str, assignee_id: Optional[str] = None
) -> dict:
    """
    Creates a new comment thread on a design.

    Args:
        design_id (str): The ID of the design to add a comment to.
        message (str): The plaintext body of the comment. User mentions must follow the format [user_id:team_id].
        assignee_id (Optional[str]): Optional ID of the user to assign the comment to.
                                     The user must be mentioned in the comment message.

    Returns:
        dict: Contains:
            - thread (dict): The created thread object with fields:
                - id (str): Thread ID.
                - design_id (str)
                - thread_type (dict):
                    - type (str): "comment" or "suggestion".
                - content (dict):
                    - plaintext (str)
                    - markdown (str, optional)
                    - mentions (dict): Keys are "user_id:team_id", values include:
                        - tag (str)
                        - user: user_id, team_id, display_name
                - assignee (dict, optional): Assigned user metadata.
                - resolver (dict, optional): Resolver user metadata.
                - suggested_edits (list, optional): Type-specific suggestion info.
                - author (dict, optional): Metadata for the user who authored the comment.
                - created_at (int)
                - updated_at (int)
    """
    pass


def create_reply(design_id: str, thread_id: str, message: str) -> dict:
    """
    Adds a reply to a comment thread on a design.

    Args:
        design_id (str): The ID of the design the thread belongs to.
        thread_id (str): The ID of the thread to reply to.
        message (str): The plaintext message body of the reply. Mentions use [user_id:team_id].

    Returns:
        dict: Contains:
            - reply (dict):
                - id (str)
                - design_id (str)
                - thread_id (str)
                - content (dict):
                    - plaintext (str)
                    - markdown (str, optional)
                    - mentions (dict): Keys as "user_id:team_id", values include tag and user info.
                - author (dict, optional): User metadata.
                - created_at (int)
                - updated_at (int)
    """
    pass


def get_thread(design_id: str, thread_id: str) -> dict:
    """
    Retrieves a specific comment thread from a design.

    Args:
        design_id (str): The design ID.
        thread_id (str): The ID of the thread to retrieve.

    Returns:
        dict: Contains:
            - thread (dict):
                - id (str)
                - design_id (str)
                - thread_type (dict): { type: "comment" | "suggestion" }
                - content (dict): Includes plaintext, markdown (optional), mentions (optional)
                - suggested_edits (list, optional): Edits with type and formatting metadata.
                - assignee (dict, optional)
                - resolver (dict, optional)
                - author (dict, optional)
                - created_at (int)
                - updated_at (int)
    """
    pass


def get_reply(design_id: str, thread_id: str, reply_id: str) -> dict:
    """
    Retrieves a specific reply from a thread on a design.

    Args:
        design_id (str): The ID of the design.
        thread_id (str): The ID of the thread the reply belongs to.
        reply_id (str): The ID of the reply to retrieve.

    Returns:
        dict: Contains:
            - reply (dict):
                - id (str)
                - design_id (str)
                - thread_id (str)
                - content (dict): Includes plaintext, markdown (optional), mentions
                - author (dict, optional): User metadata
                - created_at (int)
                - updated_at (int)
    """
    pass


def list_replies(
    design_id: str,
    thread_id: str,
    limit: Optional[int] = 50,
    continuation: Optional[str] = None,
) -> dict:
    """
    Lists replies from a specific thread on a design.

    Args:
        design_id (str): The ID of the design.
        thread_id (str): The ID of the thread.
        limit (Optional[int]): Max number of replies to return (default: 50, min: 1, max: 100).
        continuation (Optional[str]): Token for paginated results.

    Returns:
        dict: Contains:
            - items (List[dict]): List of reply objects:
                - id (str)
                - design_id (str)
                - thread_id (str)
                - content (dict): plaintext, markdown (optional), mentions
                - author (dict, optional)
                - created_at (int)
                - updated_at (int)
            - continuation (str, optional): Token for fetching the next set of results.
    """
    pass
