"""
Entries API for Google Meet API simulation.
"""

from typing import Dict, Any, Optional
from pydantic import ValidationError
from google_meet.SimulationEngine.db import DB
from google_meet.SimulationEngine.utils import paginate_results
from google_meet.SimulationEngine.models import TranscriptEntriesListParams, TranscriptEntriesGetParams


def get(name: str) -> Dict[str, Any]:
    """
    Gets a transcript entry by entry ID.

    Args:
        name (str): Resource name of the entry.

    Returns:
        Dict[str, Any]: A dictionary.
        - If the entry is found, returns an entry object with keys such as:
            - "id" (str): The entry identifier
            - "parent" (str): ID of the parent transcript
            - "start_time" (str): The time when the entry was created
            - "text" (str): The transcript text content
            - Additional entry-specific properties
    Raises:
        TypeError: If the entry name is not a string
        ValueError: If the entry name is empty or whitespace-only
        ValueError: If the entry is not found
    """
    if not isinstance(name, str):
        raise TypeError(f"Entry name must be a string, got {type(name).__name__}")
    if not name or not name.strip():
        raise ValueError("Entry name is required and cannot be empty or whitespace-only")
    if name not in DB["entries"]:
        raise ValueError(f"Entry {name} not found")
    return DB["entries"][name]


def list(
    parent: str, pageSize: int = 100, pageToken: Optional[str] = None
) -> Dict[str, Any]:
    """
    Lists the entries of a transcript.

    Args:
        parent (str): The parent transcript resource name.
        pageSize (int): The maximum number of entries to return.
        pageToken (Optional[str]): The token for continued list pagination.

    Returns:
        Dict[str, Any]: A dictionary.
        - On successful retrieval, returns a dictionary with:
            - "entries" (List[Dict[str, Any]]): List of entry objects, each containing:
                - "id" (str): The entry identifier
                - "parent" (str): ID of the parent transcript
                - "start_time" (str): The time when the entry was created
                - "text" (str): The transcript text content
                - Additional entry-specific properties
            - "nextPageToken" (Optional[str]): Token for the next page of results, if more exist
    Raises:
        ValidationError: If the parameters are invalid.
    """
    # Validate parameters
    try:
        params = TranscriptEntriesListParams(
            parent=parent, 
            pageSize=pageSize, 
            pageToken=pageToken
        )
    except ValidationError as e:
        raise ValidationError(f"Invalid parameters: {e}")
    
    # Filter entries by parent transcript
    filtered_entries = [
        entry for entry in DB["entries"].values() 
        if entry.get("parent") == params.parent
    ]

    # Sort by start_time in ascending order
    filtered_entries.sort(key=lambda x: x.get("start_time", ""))

    return paginate_results(filtered_entries, "entries", params.pageSize, params.pageToken) 
