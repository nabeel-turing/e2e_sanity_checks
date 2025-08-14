# APIs/jira/GroupsPickerApi.py

from .SimulationEngine.db import DB
from typing import Optional, Dict, List


def find_groups(query: Optional[str] = None) -> Dict[str, List[str]]:
    """
    Search for groups matching a query string.

    This method searches for groups whose names contain the specified query string.
    The search is case-insensitive and returns all matching group names. This is useful
    for implementing group picker functionality in the UI.

    Args:
        query (Optional[str]): The search string to match against group names.
            If None or not provided, all groups will be returned.
            Must be a string if provided.

    Returns:
        Dict[str, List[str]]: A dictionary containing:
            - groups (List[str]): A list of group names that match the query.
                Each item is a group name as a string.

    Raises:
        TypeError: If query is provided but is not a string.
    """
    # Input type validation
    if query is not None and not isinstance(query, str):
        raise TypeError(f"query must be a string or None, got {type(query).__name__}.")
    
    # Handle None case - return all groups
    if query is None:
        return {"groups": list(DB.get("groups", {}).keys())}
    
    # Handle empty string case - return all groups
    if query == "":
        return {"groups": list(DB.get("groups", {}).keys())}
    
    # Search for matching groups (case-insensitive)
    query_lower = query.lower()
    matched = [group_name for group_name in DB.get("groups", {}) if query_lower in group_name.lower()]
    return {"groups": matched}
