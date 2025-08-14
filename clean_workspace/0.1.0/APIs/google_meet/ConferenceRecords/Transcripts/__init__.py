"""
Transcripts API for Google Meet API simulation.
"""

from typing import Dict, Any, Optional
from google_meet.SimulationEngine.db import DB
from google_meet.SimulationEngine.utils import paginate_results
from google_meet.SimulationEngine.models import TranscriptsListParams
from google_meet.SimulationEngine.custom_errors import InvalidTranscriptNameError, NotFoundError


def get(name: str) -> Dict[str, Any]:
    """
    Gets a transcript by transcript ID.

    Args:
        name (str): Resource name of the transcript.

    Returns:
        Dict[str, Any]: A dictionary.
        - If the transcript is found, returns a transcript object with keys such as:
            - "id" (str): The transcript identifier
            - "parent" (str): ID of the parent conference record
            - "start_time" (str): The time when the transcript started
            - Additional transcript-specific properties
    Raises:
        InvalidTranscriptNameError: If the transcript name is invalid (empty or whitespace-only).
        NotFoundError: If the transcript is not found.
    """
    if not name or not name.strip():
        raise InvalidTranscriptNameError("Transcript name is required and cannot be empty or whitespace-only")
    elif name not in DB["transcripts"]:
        raise NotFoundError(f"Transcript not found: {name}")
    else:
        return DB["transcripts"][name]

def list(
    parent: str,
    pageSize: int = 100,
    pageToken: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Lists the transcripts of a conference.

    Args:
        parent (str): The parent resource name.
        pageSize (int): The maximum number of transcripts to return.
        pageToken (Optional[str]): The token for continued list pagination.

    Returns:
        Dict[str, Any]: A dictionary.
        - On successful retrieval, returns a dictionary with:
            - "transcripts" (List[Dict[str, Any]]): List of transcript objects, each containing:
                - "id" (str): The transcript identifier
                - "parent" (str): ID of the parent conference record
                - "start_time" (str): The time when the transcript started
                - Additional transcript-specific properties
            - "nextPageToken" (Optional[str]): Token for the next page of results, if more exist

    Raises:
        ValidationError: If input arguments fail validation.
        NotFoundError: If no transcripts are found for the given parent.
    """
    # Validate parameters using pydantic
    validated_params = TranscriptsListParams(
        parent=parent,
        pageToken=pageToken,
        pageSize=pageSize
    )

    # Filter transcripts by parent conference record
    filtered_transcripts = [
        transcript
        for transcript in DB["transcripts"].values()
        if transcript.get("parent") == validated_params.parent
    ]

    if not filtered_transcripts:
        raise NotFoundError(f"No transcripts found for parent: {validated_params.parent}")

    # Sort by start_time in ascending order
    filtered_transcripts.sort(key=lambda x: x.get("start_time", ""))

    return paginate_results(filtered_transcripts, "transcripts", validated_params.pageSize, validated_params.pageToken)
