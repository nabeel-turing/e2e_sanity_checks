from typing import Dict, List, Optional
from youtube.SimulationEngine.custom_errors import MaxResultsOutOfRangeError
from youtube.SimulationEngine.db import DB
from youtube.SimulationEngine.utils import generate_random_string, generate_entity_id
from typing import Optional, Dict, Any, List, Union


"""
    Handles YouTube Channels API operations.
    
    This class provides methods to manage YouTube channels, including retrieving
    channel information, creating new channels, and updating channel metadata.
"""


def list(
    category_id: Optional[str] = None,
    for_username: Optional[str] = None,
    hl: Optional[str] = None,
    channel_id: Optional[str] = None,
    managed_by_me: Optional[bool] = None,
    max_results: Optional[int] = None,
    mine: Optional[bool] = None,
    my_subscribers: Optional[bool] = None,
    on_behalf_of_content_owner: Optional[str] = None,
) -> Dict[str, List[Dict]]:
    """
    Retrieves a list of channels with optional filters.

    Args:
        category_id (Optional[str]): The categoryId parameter specifies a YouTube guide category ID.
                     The API response will only include channels from that category.
        for_username (Optional[str]): The forUsername parameter specifies a YouTube username.
                      The API response will only include the channel associated with that username.
        hl (Optional[str]): The hl parameter instructs the API to retrieve localized resource metadata
            for a specific application language that the YouTube website supports.
        channel_id (Optional[str]): The id parameter specifies a comma-separated list of the YouTube channel ID(s)
                    for the resource(s) that are being retrieved.
        managed_by_me (Optional[bool]): The managedByMe parameter can be used to instruct the API
                       to only return channels that the user is allowed to manage.
        max_results (Optional[int]): The maxResults parameter specifies the maximum number of items
                     that should be returned in the result set. Must be between 1 and 50.
        mine (Optional[bool]): The mine parameter can be used to instruct the API to only return
              channels owned by the authenticated user.
        my_subscribers (Optional[bool]): The mySubscribers parameter can be used to instruct the API
                        to only return channels to which the authenticated user has subscribed.
        on_behalf_of_content_owner (Optional[str]): The onBehalfOfContentOwner parameter indicates that the
                                   request's authorization credentials identify a YouTube CMS user
                                   who is acting on behalf of the content owner specified
                                   in the parameter value.

    Returns:
        Dict[str, List[Dict]]: A dictionary containing:
            - items: List of channel objects matching the filter criteria
            Each channel object contains:
                - id (str): Unique channel identifier
                - categoryId (str): Channel category
                - forUsername (str): Channel username
                - hl (str): Language setting
                - managedByMe (bool): Management status
                - mine (bool): Ownership status
                - mySubscribers (str): Subscription status
                - onBehalfOfContentOwner (str): CMS user information

    Raises:
        TypeError: If any input argument has an incorrect type.
        MaxResultsOutOfRangeError: If max_results is provided and is not between 1 and 50 (inclusive).
        KeyError: If the database is not properly initialized or a critical key is missing
                  (propagated from DB access).
    """
    
    # Input Validation
    if category_id is not None and not isinstance(category_id, str):
        raise TypeError("category_id must be a string or None.")
    if for_username is not None and not isinstance(for_username, str):
        raise TypeError("for_username must be a string or None.")
    if hl is not None and not isinstance(hl, str):
        raise TypeError("hl must be a string or None.")
    if channel_id is not None and not isinstance(channel_id, str):
        raise TypeError("channel_id must be a string or None.")
    if managed_by_me is not None and not isinstance(managed_by_me, bool):
        raise TypeError("managed_by_me must be a boolean or None.")
    if mine is not None and not isinstance(mine, bool):
        raise TypeError("mine must be a boolean or None.")
    if my_subscribers is not None and not isinstance(my_subscribers, bool):
        raise TypeError("my_subscribers must be a boolean or None.")
    if on_behalf_of_content_owner is not None and not isinstance(on_behalf_of_content_owner, str):
        raise TypeError("on_behalf_of_content_owner must be a string or None.")

    if max_results is not None:
        if not isinstance(max_results, int):
            raise TypeError("max_results must be an integer or None.")
        if not (1 <= max_results <= 50):
            raise MaxResultsOutOfRangeError("max_results must be between 1 and 50, inclusive.")


    # Core Logic (original logic preserved, error dictionary returns removed)
    # A KeyError from DB.get will propagate naturally.
    channels = DB.get("channels", {})
    results = []

    for channel_data in channels.values(): # Renamed 'channel' to 'channel_data' to avoid conflict if 'channel_id' was meant to be used directly
        if category_id is not None and channel_data.get("categoryId") != category_id:
            continue
        if for_username is not None and channel_data.get("forUsername") != for_username:
            continue
        # Assuming channel_id is for filtering a specific channel by its ID if provided
        # The original code had 'channel.get("id") != channel_id'. If channel_id is a
        # comma-separated list as per docstring, this logic would need adjustment.
        # For now, keeping it as single ID check as per original code structure.
        if channel_id is not None and channel_data.get("id") != channel_id:
            continue
        if hl is not None and channel_data.get("hl") != hl:
            continue
        if (
            managed_by_me is not None
            and channel_data.get("managedByMe") != managed_by_me
        ):
            continue
        if mine is not None and channel_data.get("mine") != mine:
            continue
        if (
            my_subscribers is not None
            and channel_data.get("mySubscribers") != my_subscribers
        ):
            continue
        if (
            on_behalf_of_content_owner is not None
            and channel_data.get("onBehalfOfContentOwner") != on_behalf_of_content_owner
        ):
            continue

        results.append(channel_data)

    if max_results is not None: # max_results is validated to be between 1 and 50
        results = results[:max_results]
    # The original code had `results = results[: min(max_results, 50)]`.
    # Since max_results is now guaranteed to be <= 50 (if not None),
    # min(max_results, 50) simplifies to max_results.

    return {"items": results}

def insert(
    part: str,
    category_id: Optional[str] = None,
    for_username: Optional[str] = None,
    hl: Optional[str] = None,
    channel_id: Optional[str] = None,
    managed_by_me: Optional[bool] = None,
    max_results: Optional[int] = None,
    mine: Optional[bool] = None,
    my_subscribers: Optional[bool] = None,
    on_behalf_of_content_owner: Optional[str] = None,
) -> Union[Dict[str, Any], Dict[str, str]]:
    """
    Creates a new channel resource in the simulated database.

    Args:
        part (str): The part parameter specifies the channel resource properties that the API response will include.
        category_id (Optional[str]): The categoryId parameter specifies a YouTube guide category ID for the new channel.
        for_username (Optional[str]): The forUsername parameter specifies a YouTube username for the new channel.
        hl (Optional[str]): The hl parameter instructs the API to retrieve localized resource metadata for a specific application language that the YouTube website supports.
        channel_id (Optional[str]): The id parameter specifies the YouTube channel ID for the new channel. Currently not used!
        managed_by_me (Optional[bool]): The managedByMe parameter indicates whether the channel is managed by the authenticated user.
        max_results (Optional[int]): The maxResults parameter specifies the maximum number of items that should be returned in the result set.
        mine (Optional[bool]): The mine parameter indicates whether the channel is owned by the authenticated user.
        my_subscribers (Optional[bool]): The mySubscribers parameter indicates whether the authenticated user has subscribed to the channel.
        on_behalf_of_content_owner (Optional[str]): The onBehalfOfContentOwner parameter indicates that the request's authorization credentials identify a YouTube CMS user who is acting on behalf of the content owner specified in the parameter value.

    Returns:
        Union[Dict[str, Any], Dict[str, str]]: 
            A dictionary containing channel data or an error message.
            onsuccess(Dict[str, Any]): 
                - success (bool): Whether the operation was successful
                - channel (Dict[str, Any]): The newly created channel object with all properties
            onerror(Dict[str, str]): 
                - error (str): error message

    Raises:
        ValueError: If part is empty or invalid
        KeyError: If the database is not properly initialized
    """
    try:
        if not part:
            raise ValueError("Invalid part parameter")

        new_id = generate_entity_id("channel")
        new_channel = {
            "id": new_id,
            "categoryId": category_id,
            "forUsername": for_username,
            "hl": hl,
            "managedByMe": managed_by_me,
            "maxResults": max_results,
            "mine": mine,
            "mySubscribers": my_subscribers,
            "onBehalfOfContentOwner": on_behalf_of_content_owner,
        }
        DB.setdefault("channels", {})[new_id] = new_channel
        return {"success": True, "channel": new_channel}
    except KeyError as e:
        return {"error": f"Database error: {str(e)}"}
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def update(channel_id: str, properties: Dict[str, str | bool] = None) -> Dict[str, str]:
    """
    Updates metadata of a YouTube channel.

    Args:
        channel_id (str): The unique identifier of the channel to update.
        properties (Dict[str, str | bool]): Key-value pairs of channel properties to update. Valid properties include:
            - categoryId (str): Channel category
            - forUsername (str): Channel username
            - hl (str): Language setting
            - managedByMe (bool): Management status
            - mine (bool): Ownership status
            - mySubscribers (bool): Subscription status
            - onBehalfOfContentOwner (str): CMS user information
    Returns:
        Dict[str, str]: A dictionary containing:
            onsuccess: 
                - success (str): Success Message
            onerror: 
                - error (str): Error Message

    Raises:
        ValueError: If no update parameters are provided.
        KeyError: If the channel_id doesn't exist in the database.
    """
    try:
        if not properties:
            raise ValueError("No update parameters provided")

        if channel_id not in DB.get("channels", {}):
            raise KeyError(f"Channel ID: {channel_id} not found in the database.")

        DB["channels"][channel_id].update(
            {k: v for k, v in properties.items() if v is not None}
        )
        return {"success": f"Channel ID: {channel_id} updated successfully."}
    except KeyError as e:
        return {"error": str(e)}
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
