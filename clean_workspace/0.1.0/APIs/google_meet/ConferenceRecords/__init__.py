"""
ConferenceRecords API for Google Meet API simulation.
"""

from typing import Dict, Any, Optional
from google_meet.SimulationEngine.db import DB
from google_meet.SimulationEngine.utils import paginate_results


def get(name: str) -> Dict[str, Any]:
    """
    Gets a conference record by conference ID.

    Retrieves detailed information about a specific conference record.

    Args:
        name (str): Resource name of the conference to retrieve.

    Returns:
        Dict[str, Any]: A dictionary.
        - On successful retrieval, returns a dictionary with the following keys and value types:
            - "id" (str): The conference record identifier
            - "start_time" (str): The time when the conference started
            - Additional conference-specific properties, which may include:
                - meeting_code (Optional[str])
                - name (Optional[str])
                - end_time (Optional[str])

    Raises:
        TypeError: If the conference record name is not a string.
        ValueError: If the conference record name is empty or whitespace-only.
        KeyError: If the conference record is not found.
    """
    if not isinstance(name, str):
        raise TypeError(f"Conference record name must be a string, got {type(name).__name__}")
    name = name.strip()
    if not name:
        raise ValueError("Conference record name is required and cannot be empty or whitespace-only")
    if name not in DB["conferenceRecords"]:
        raise KeyError(f"Conference record not found: {name}")
    return DB["conferenceRecords"][name]


def list(
    filter: Optional[str] = None,
    pageSize: int = 100,
    pageToken: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Lists the conference records.

    Retrieves a list of conference records with optional filtering and pagination.
    By default, results are ordered by start time in descending order (most recent first).

    Args:
        filter (Optional[str]): An optional filter string to apply to the records. The filter is applied
                to the string representation of each record object.
        pageSize (int): An optional maximum number of records to return per page, defaults to 100.
        pageToken (Optional[str]): An optional token for pagination, representing the start index.

    Returns:
        Dict[str, Any]: A dictionary.
        - On successful retrieval, returns a dictionary with the following keys and value types:
            - "conferenceRecords" (List[Dict[str, Any]]): A list of conference record objects,
                each containing:
                - "id" (str): The conference record identifier
                - "start_time" (str): The time when the conference started
                - Additional conference-specific properties
            - "nextPageToken" (Optional[str]): A token for the next page of results,
                if more results exist

    Raises:
        TypeError: If input arguments fail validation.
        ValueError: If input arguments fail validation.
    """
    if filter:
        if not isinstance(filter, str):
            raise TypeError("filter must be a string")

        filter = filter.strip()
        if not filter:
            raise ValueError("Filter cannot be empty")

    if not isinstance(pageSize, int):
        raise TypeError("pageSize must be an integer")

    if pageSize <= 0:
        raise ValueError("pageSize must be positive")

    if pageToken:
        if not isinstance(pageToken, str):
            raise TypeError("pageToken must be a string")

        pageToken = pageToken.strip()
        if not pageToken:
            raise ValueError("pageToken cannot be empty")

    records = [value for value in DB["conferenceRecords"].values()]

    if filter:
        records = [r for r in records if filter in str(r)]

    # Sort by start_time in descending order
    records.sort(key=lambda x: x.get("start_time", ""), reverse=True)

    return paginate_results(records, "conferenceRecords", pageSize, pageToken)
