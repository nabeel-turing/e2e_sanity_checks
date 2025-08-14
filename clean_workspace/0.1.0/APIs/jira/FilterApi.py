# APIs/jira/FilterApi.py

from .SimulationEngine.db import DB
from typing import Optional, Dict, Any


def get_filters() -> Dict[str, Any]:
    """
    Retrieve all filters from Jira.

    This method returns a list of all filters in the system. Filters in Jira
    are used to save and share search queries, allowing users to quickly
    access commonly used issue searches.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - filters (List[Dict[str, Any]]): A list of filter objects,
                each containing:
                - id (str): The unique identifier for the filter
                - name (str): The name of the filter
                - description (str): A description of the filter's purpose
                - owner (Dict[str, str]): Information about the filter owner
                - jql (str): The JQL query that defines the filter
                - favoriteCount (int): Number of users who have favorited the filter
                - sharePermissions (List[Dict[str, Any]]): List of sharing permissions of the format
                    - id (str): The unique identifier for the permission
                    - type (str): The type of permission e.g. "group", "project", "global"
                    - view (bool): Whether the permission allows viewing the filter
                    - edit (bool): Whether the permission allows editing the filter
                    - project (Dict[str, str]): Information about the project that the permission applies to, if type is "project"
                        - id (str): The unique identifier for the project
                        - key (str): The key of the project
                        - name (str): The name of the project
                        - avatarUrls (List[str]): The URL of the project's avatar
                        - self (str): The URL of the project
                        - projectCategory (Dict[str, str]): Information about the category of the project
                            - self (str): The URL of the project category
                            - id (str): The unique identifier for the project category
                            - name (str): The name of the project category
                            - description (str): The description of the project category
                        - role (Dict[str, str]): Information about the role that the permission applies to, if type is "project"
                            - id (str): The unique identifier for the role
                            - name (str): The name of the role
                            - description (str): The description of the role
                            - self (str): The URL of the role
                            - actors (List[Dict[str, str]]): The actors that the role applies to
                                - id (str): The unique identifier for the actor
                                - displayName (str): The display name of the actor
                                - type (str): The type of actor e.g. "group", "user"
                                - name (str): The name of the actor
                        - group (Dict[str, str]): Information about the group that the permission applies to, if type is "group"
                            - self (str): The URL of the group
                            - name (str): The name of the group
    """
    return {"filters": list(DB["filters"].values())}


def get_filter(filter_id: str) -> Dict[str, Any]:
    """
    Retrieve a specific filter by its ID.

    This method returns detailed information about a specific filter
    identified by its unique ID.

    Args:
        filter_id (str): The unique identifier of the filter to retrieve

    Returns:
        Dict[str, Any]: A dictionary containing:
            - id (str): The unique identifier for the filter
            - name (str): The name of the filter
            - description (str): A description of the filter's purpose
            - owner (Dict[str, str]): Information about the filter owner
            - jql (str): The JQL query that defines the filter
            - favorite (bool): Whether the filter is a favorite
            - editable (bool): Whether the filter is editable
            - sharePermissions (List[Dict[str, Any]]): List of sharing permissions of the format
                - id (str): The unique identifier for the permission
                - type (str): The type of permission e.g. "group", "project", "global"
                - view (bool): Whether the permission allows viewing the filter
                - edit (bool): Whether the permission allows editing the filter
                - project (Dict[str, str]): Information about the project that the permission applies to, if type is "project"
                    - id (str): The unique identifier for the project
                    - key (str): The key of the project
                    - name (str): The name of the project
                    - avatarUrls (List[str]): The URL of the project's avatar
                    - self (str): The URL of the project
                    - projectCategory (Dict[str, str]): Information about the category of the project
                        - self (str): The URL of the project category
                        - id (str): The unique identifier for the project category
                        - name (str): The name of the project category
                        - description (str): The description of the project category
                - role (Dict[str, str]): Information about the role that the permission applies to, if type is "project"
                    - id (str): The unique identifier for the role
                    - name (str): The name of the role
                    - description (str): The description of the role
                    - self (str): The URL of the role
                    - actors (List[Dict[str, str]]): The actors that the role applies to
                        - id (str): The unique identifier for the actor
                        - displayName (str): The display name of the actor
                        - type (str): The type of actor e.g. "group", "user"
                        - name (str): The name of the actor
                - group (Dict[str, str]): Information about the group that the permission applies to, if type is "group"
                    - self (str): The URL of the group
                    - name (str): The name of the group


    Raises:
        ValueError: If the filter does not exist
    """
    flt = DB["filters"].get(filter_id)
    if not flt:
        return {"error": f"Filter '{filter_id}' not found."}
    return flt


def update_filter(
    filter_id: str,
    name: Optional[str] = None,
    jql: Optional[str] = None,
    description: Optional[str] = None,
    favorite: Optional[bool] = None,
    editable: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Update an existing filter.

    This method allows updating the name and/or JQL query of an existing
    filter. At least one of name or jql must be provided.

    Args:
        filter_id (str): The unique identifier of the filter to update
        name (Optional[str]): The new name for the filter. Defaults to None.
        jql (Optional[str]): The new JQL query for the filter. Defaults to None.
        description (Optional[str]): Description of the filter. Defaults to None.
        favorite (Optional[bool]): Whether the filter is a favorite. Defaults to None.
        editable (Optional[bool]): Whether the filter is editable. Defaults to None.

    Returns:
        Dict[str, Any]: A dictionary containing:
                - updated (bool): True if the filter was successfully updated
                - filter (Dict[str, Any]): The updated filter object
                    - id (str): The unique identifier for the filter
                    - name (str): The name of the filter
                    - jql (str): The JQL query that defines the filter
                    - favorite (bool): Whether the filter is a favorite
                    - editable (bool): Whether the filter is editable
                    - sharePermissions (List[Dict[str, Any]]): List of sharing permissions
                        - id (str): The unique identifier for the permission
                        - type (str): The type of permission e.g. "group", "project", "global"
                        - view (bool): Whether the permission allows viewing the filter
                        - edit (bool): Whether the permission allows editing the filter
                        - project (Dict[str, str]): Information about the project that the permission applies to, if type is "project"
                            - id (str): The unique identifier for the project
                            - key (str): The key of the project
                            - name (str): The name of the project
                            - avatarUrls (List[str]): The URL of the project's avatar
                            - self (str): The URL of the project
                            - projectCategory (Dict[str, str]): Information about the category of the project
                                - self (str): The URL of the project category
                                - id (str): The unique identifier for the project category
                                - name (str): The name of the project category
                                - description (str): The description of the project category
                        - role (Dict[str, str]): Information about the role that the permission applies to, if type is "project"
                            - id (str): The unique identifier for the role
                            - name (str): The name of the role
                            - description (str): The description of the role
                            - self (str): The URL of the role
                            - actors (List[Dict[str, str]]): The actors that the role applies to
                                - id (str): The unique identifier for the actor
                                - displayName (str): The display name of the actor
                                - type (str): The type of actor e.g. "group", "user"
                                - name (str): The name of the actor
                        - group (Dict[str, str]): Information about the group that the permission applies to, if type is "group"
                            - self (str): The URL of the group
                            - name (str): The name of the group


    Raises:
        ValueError: If the filter does not exist
    """
    flt = DB["filters"].get(filter_id)
    if not flt:
        return {"error": f"Filter '{filter_id}' not found."}
    if name:
        flt["name"] = name
    if jql:
        flt["jql"] = jql
    return {"updated": True, "filter": flt}
