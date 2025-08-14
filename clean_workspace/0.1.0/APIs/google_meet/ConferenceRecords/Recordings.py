"""
Recordings API for Google Meet API simulation.
"""

from typing import Dict, Any, List, Optional
from google_meet.SimulationEngine.db import DB
from google_meet.SimulationEngine.utils import paginate_results


def get(name: str) -> Dict[str, Any]:
    """
    Gets a recording by recording ID.

    Args:
        name (str): Resource name of the recording.

    Returns:
        Dict[str, Any]: A dictionary containing the recording object with keys such as:
            - "id" (str): The recording identifier
            - "parent" (str): ID of the parent conference record
            - "start_time" (str): The time when the recording started
            - Additional recording-specific properties

    Raises:
        ValueError: If the name parameter is None, empty, or not a string
        KeyError: If the recording is not found in the database
    """
    # Input validation
    if name is None:
        raise ValueError("Recording name cannot be None")
    
    if not isinstance(name, str):
        raise ValueError("Recording name must be a string")
    
    if not name.strip():
        raise ValueError("Recording name cannot be empty or whitespace")
    
    # Check if recording exists and raise if not found
    if name not in DB["recordings"]:
        raise KeyError(f"Recording not found: {name}")
    
    return DB["recordings"][name]


def list(
    parent: str,
    parent_conference_record: str,
    pageSize: Optional[int] = None,
    pageToken: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Lists the recordings of a conference.

    Args:
        parent (str): The parent resource name. Must be a non-empty string.
        parent_conference_record (str): The parent conference record. Must be a non-empty string.
        pageSize (Optional[int]): The maximum number of recordings to return. Must be a positive integer 
                                 between 1 and 1000. Defaults to None (no limit).
        pageToken (Optional[str]): The token for continued list pagination. Must be a string if provided.

    Returns:
        Dict[str, Any]: A dictionary containing the results.
        - If the parent is invalid, returns a dictionary with:
            - "error" (str): Error message "Invalid parent"
        - On successful retrieval, returns a dictionary with:
            - "recordings" (List[Dict[str, Any]]): List of recording objects, each containing:
                - "id" (str): The recording identifier
                - "parent" (str): ID of the parent conference record
                - "start_time" (str): The time when the recording started (ISO format)
                - "duration" (str): Duration of the recording
                - "state" (str): Current state of the recording (e.g., "completed", "processing")
                - Additional recording-specific properties
            - "nextPageToken" (Optional[str]): Token for the next page of results, if more exist.
              Use this token in subsequent calls to retrieve additional pages.

    Raises:
        ValueError: If parent or parent_conference_record is empty or invalid, or if pageSize 
                   is not a positive integer or exceeds 1000.
        TypeError: If pageSize is not an integer or pageToken is not a string.
    """
    # Input validations
    if not parent or not isinstance(parent, str):
        raise ValueError("parent must be a non-empty string")
    
    if not parent_conference_record or not isinstance(parent_conference_record, str):
        raise ValueError("parent_conference_record must be a non-empty string")
    
    if pageSize is not None:
        if not isinstance(pageSize, int):
            raise TypeError("pageSize must be an integer")
        if pageSize <= 0:
            raise ValueError("pageSize must be a positive integer")
        if pageSize > 1000:
            raise ValueError("pageSize cannot exceed 1000")
    
    if pageToken is not None and not isinstance(pageToken, str):
        raise TypeError("pageToken must be a string")

    # This is a simplified implementation - in a real API, we would validate parent
    # For test compatibility
    if parent.split("/")[-1] != parent_conference_record:
        return {"error": "Invalid parent"}

    # Filter recordings by parent conference record
    filtered_recordings = [
        recording
        for recording in DB["recordings"].values()
        if recording.get("parent") == parent_conference_record
    ]

    # Sort by start_time in ascending order
    filtered_recordings.sort(key=lambda x: x.get("start_time", ""))

    return paginate_results(filtered_recordings, "recordings", pageSize, pageToken)
