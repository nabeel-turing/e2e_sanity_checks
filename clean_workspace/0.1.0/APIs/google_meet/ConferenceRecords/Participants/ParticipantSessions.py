"""
ParticipantSessions API for Google Meet API simulation.

This module provides access to participant session data for the Google Meet API simulation.
A participant session represents a single continuous period of participation in a meeting.
"""

from typing import Dict, Any, Optional
from google_meet.SimulationEngine.db import DB
from google_meet.SimulationEngine.utils import paginate_results, ensure_exists
from google_meet.SimulationEngine.models import ParticipantSessionsListParams


def list(
    parent: str,
    filter: Optional[str] = None,
    pageSize: int = 100,
    pageToken: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Lists the sessions of a participant.

    Retrieves all sessions associated with the specified participant, with optional
    filtering and pagination. Results are sorted by join time in ascending order.

    Args:
        parent (str): The parent participant resource name (participant ID).
        filter (Optional[str]): An optional filter string to apply to the sessions. The filter is applied
               to the string representation of each session object.
        pageSize (int): The maximum number of sessions to return per page. Defaults to 100.
        pageToken (Optional[str]): The token for continued list pagination, representing the start index.

    Returns:
        Dict[str, Any]: A dictionary.
        - On successful retrieval, returns a dictionary with the following keys and value types:
            - "participantSessions" (List[Dict[str, Any]]): A list of session objects, each containing:
                - "id" (str): The session identifier
                - "participantId" (str): ID of the parent participant
                - "join_time" (str): Time when the participant joined
                - Additional session-specific properties
            - "nextPageToken" (Optional[str]): A token for the next page of results, if more results exist

    Raises:
        ValidationError: If the parameters are invalid.
        ValueError: If the parent participant does not exist.

    """
    # Validate input using pydantic
    request = ParticipantSessionsListParams(
        parent=parent,
        filter=filter,
        pageSize=pageSize,
        pageToken=pageToken
    )

    # Ensure the parent participant exists
    ensure_exists("participants", request.parent)

    # Filter sessions by parent participant
    filtered_sessions = [
        session
        for session in DB["participantSessions"].values()
        if session.get("participantId") == request.parent
    ]

    # Apply additional filtering if provided
    if request.filter:
        # Normalize filter to lowercase for case-insensitive matching
        filter_lower = request.filter.lower()
        filtered_sessions = [s for s in filtered_sessions if filter_lower in str(s).lower()]

    # Sort by join_time in ascending order
    filtered_sessions.sort(key=lambda x: x.get("join_time", ""))

    return paginate_results(
        filtered_sessions, "participantSessions", request.pageSize, request.pageToken
    )

def get(name: str) -> Dict[str, Any]:
    """
    Gets a participant session by session ID.

    Retrieves detailed information about a specific participant session.

    Args:
        name (str): Resource name (ID) of the session to retrieve.

    Returns:
        Dict[str, Any]: A dictionary.
        - If the session is not found, returns a dictionary with the key "error" and
          the value "Participant session not found".
        - On successful retrieval, returns a dictionary with the following keys and value types:
            - "id" (str): The session identifier
            - "participantId" (str): ID of the parent participant
            - "join_time" (str): Time when the participant joined the meeting
            - Additional session-specific properties, which may vary by session

    Example:
        >>> get("session1")
        {'id': 'session1', 'participantId': 'part1', 'join_time': '09:59'}
    """
    # Type validation for name
    if not isinstance(name, str):
        return {"error": f"Parameter validation failed: name must be a string, got {type(name).__name__}"}

    # Input sanitization for name
    name = name.strip()
    if not name:
        return {"error": "Parameter validation failed: name cannot be empty or whitespace only"}

    if name in DB["participantSessions"]:
        return DB["participantSessions"][name]
    else:
        return {"error": "Participant session not found"}
