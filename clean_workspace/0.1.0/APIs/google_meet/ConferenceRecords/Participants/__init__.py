"""
Participants API for Google Meet API simulation.
"""

from typing import Dict, Any, Optional
from pydantic import ValidationError
from google_meet.SimulationEngine.db import DB
from google_meet.SimulationEngine.utils import paginate_results
from google_meet.SimulationEngine.models import ParticipantsListParams


def get(name: str) -> Dict[str, Any]:
    """
    Gets a participant by ID.

    Args:
        name (str): Resource name of the participant.

    Returns:
        Dict[str, Any]: A dictionary.
        - If the participant is found, returns a participant object with keys such as:
            - "id" (str): The participant identifier
            - "conferenceRecordId" (str): ID of the parent conference record
            - "join_time" (str): The time when the participant joined
            - Additional participant-specific properties like:
                - "email" (Optional[str]): Participant's email address
                - "displayName" (Optional[str]): Participant's display name
    Raises:
        ValueError: If the name parameter is None, empty, or not a string
        ValueError: If the participant is not found
    """
    # Validate required parameter
    if not name or not isinstance(name, str):
        raise TypeError("Name parameter is required and must be a non-empty string")

    if name not in DB["participants"]:
        raise ValueError(f"Participant {name} not found")

    return DB["participants"][name]


def list(
    parent: str, pageSize: int = 100, pageToken: Optional[str] = None
) -> Dict[str, Any]:
    """
    Lists participants of a conference record.

    Args:
        parent (str): The parent conference record resource name.
        pageSize (int): The maximum number of participants to return, defaults to 100.
        pageToken (Optional[str]): The token for continued list pagination.

    Returns:
        Dict[str, Any]: A dictionary.
        - If validation fails, returns a dictionary with the key "error" and an appropriate error message.
        - On successful retrieval, returns a dictionary with:
            - "participants" (List[Dict[str, Any]]): List of participant objects, each containing:
                - "id" (str): The participant identifier
                - "conferenceRecordId" (str): ID of the parent conference record
                - "join_time" (str): The time when the participant joined
                - Additional participant-specific properties
            - "nextPageToken" (Optional[str]): Token for the next page of results, if more exist

    Raises:
        ValidationError: If input arguments fail validation.
    """
    # Validate parameters using pydantic
    try:
        validated_params = ParticipantsListParams(
            parent=parent,
            pageSize=pageSize,
            pageToken=pageToken
        )
    except ValidationError as e:
        return {"error": f"Parameter validation failed: {str(e)}"}

    # Filter participants by parent conference record
    filtered_participants = [
        participant
        for participant in DB["participants"].values()
        if participant.get("parent") == validated_params.parent
    ]

    return paginate_results(filtered_participants, "participants", validated_params.pageSize, validated_params.pageToken)
