from typing import Dict, List, Optional
from youtube.SimulationEngine.db import DB
from youtube.SimulationEngine.utils import generate_random_string, generate_entity_id
from typing import Optional, Dict, Any, List, Union


"""
    Handles YouTube Memberships API operations.
    
    This class provides methods to manage channel memberships,
    which allow viewers to support their favorite creators with monthly payments.
"""


def list(
    part: str,
    has_access_to_level: Optional[str] = None,
    filter_by_member_channel_id: Optional[str] = None,
    max_results: Optional[int] = None,
    mode: Optional[str] = None,
    page_token: Optional[str] = None,
) -> Dict[str, Union[List[Dict], str]]:
    """
    Retrieves a list of members that match the request criteria for a channel.

    Args:
        part (str): The part parameter specifies the membership resource properties that the API response will include.
        has_access_to_level (Optional[str]): The hasAccessToLevel parameter specifies the membership level that the member has access to.
        filter_by_member_channel_id (Optional[str]): The filterByMemberChannelId parameter specifies a comma-separated list of YouTube channel IDs. The API will only return memberships from those channels.
        max_results (Optional[int]): The maxResults parameter specifies the maximum number of items that should be returned in the result set.
        mode (Optional[str]): The mode parameter specifies the membership mode.
        page_token (Optional[str]): The pageToken parameter identifies a specific page in the result set that should be returned. (Currently not used in implementation)

    Returns:
            Dict[str, Union[List[Dict], str]]: A dictionary containing:
            - If part is valid:
                - items (List[Dict]): A list of membership objects, each containing:
                    - id (str): Unique ID of the member
                    - snippet (Dict): Metadata about the membership containing:
                        - memberChannelId (str): Channel ID of the member
                        - hasAccessToLevel (str): The level the member has access to
                        - mode (str): The mode of the membership (e.g., "fanFunding", "sponsors")
            - If part is invalid:
                - error (str): Error message describing the issue (e.g., "Invalid part parameter").
    """
    if part != "snippet":
        return {"error": "Invalid part parameter"}

    filtered_members = list(DB.get("memberships", {}).values())

    if has_access_to_level:
        filtered_members = [
            member
            for member in filtered_members
            if member.get("snippet", {}).get("hasAccessToLevel") == has_access_to_level
        ]

    if filter_by_member_channel_id:
        filtered_members = [
            member
            for member in filtered_members
            if member.get("snippet", {}).get("memberChannelId")
            == filter_by_member_channel_id
        ]

    if max_results:
        filtered_members = filtered_members[:max_results]

    if mode:
        filtered_members = [
            member
            for member in filtered_members
            if member.get("snippet", {}).get("mode") == mode
        ]

    return {"items": filtered_members}


def insert(part: str, snippet: Dict[str, Any]) -> Dict[str, Union[bool, Dict, str]]:
    """
    Creates a new membership.

    Args:
        part (str): The part parameter specifies the membership resource properties that the API response will include.
        snippet (Dict[str, Any]): The snippet object containing membership details.

    Returns:
        Dict[str, Union[bool, Dict, str]]: A dictionary containing:
            - If part is valid:
                - success (bool): Whether the operation was successful
                - membership (Dict): The created membership object containing:
                    - id (str): Unique ID of the member
                    - snippet (Dict): Metadata about the membership containing:
                        - memberChannelId (str): Channel ID of the member
                        - hasAccessToLevel (str): The level the member has access to
                        - mode (str): The mode of the membership (e.g., "fanFunding", "sponsors")
            - If part is invalid:
                - error (str): Error message describing the issue
    """
    if part != "snippet":
        return {"error": "Invalid part parameter"}

    membership_id = generate_entity_id("member")
    membership = {"id": membership_id, "snippet": snippet}

    DB.set("memberships", membership_id, membership)
    return {"success": True, "membership": membership}


def delete(id: str) -> Dict[str, bool]:
    """
    Deletes a membership.

    Args:
        id (str): The ID of the membership to delete.

    Returns:
        Dict[str, bool]: A dictionary containing:
            - success (bool): Whether the operation was successful
    """
    if id in DB.get("memberships", {}):
        DB.delete("memberships", id)
        return {"success": True}
    return {"success": False}


def update(part: str, id: str, snippet: Dict[str, Any]) -> Dict[str, Union[bool, Dict, str]]:
    """
    Updates an existing membership.

    Args:
        part (str): The part parameter specifies the membership resource properties that the API response will include.
        id (str): The ID of the membership to update.
        snippet (Dict[str, Any]): The updated snippet object containing membership details.

    Returns:
        Dict[str, Union[bool, Dict, str]]: A dictionary containing:
            - If part is valid and membership exists:
                - success (bool): Whether the operation was successful
                - membership (Dict): The updated membership object containing:
                    - id (str): Unique ID of the member
                    - snippet (Dict): Metadata about the membership containing:
                        - memberChannelId (str): Channel ID of the member
                        - hasAccessToLevel (str): The level the member has access to
                        - mode (str): The mode of the membership (e.g., "fanFunding", "sponsors")
            - If part is invalid:
                - error (str): Error message describing the issue
            - If membership not found:
                - success (bool): False
    """
    if part != "snippet":
        return {"error": "Invalid part parameter"}

    memberships = DB.get("memberships", {})
    if id not in memberships:
        return {"success": False}

    membership = memberships[id]
    membership["snippet"].update(snippet)
    DB.set("memberships", id, membership)

    return {"success": True, "membership": membership}
