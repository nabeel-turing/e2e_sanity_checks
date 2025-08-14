from typing import Dict, List, Optional
from youtube.SimulationEngine.db import DB
from youtube.SimulationEngine.utils import generate_random_string, generate_entity_id
from typing import Optional, Dict, Any, List


"""
    Handles YouTube Subscriptions API operations.
    
    This class provides methods to manage subscriptions to YouTube channels,
    including creating, deleting, and listing subscriptions.
"""


def insert(part: str, snippet: Optional[Dict] = None) -> Dict[str, Optional[Dict]]:
    """
    Inserts a new subscription.

    Args:
        part(str): The part parameter specifies the subscription resource properties that the API response will include.
        snippet(Optional[Dict]): The snippet object contains details about the subscription.

    Returns:
        Dict[str, Optional[Dict]]: A dictionary containing:
            - If successful:
                - success (bool): True
                - subscription (Dict): The newly created subscription object:
                    - id (str): Unique subscription ID.
                    - snippet (Dict): Metadata about the subscription, including:
                        - channelId (str): The subscribing channel's ID.
                        - resourceId (Dict): The ID of the channel being subscribed to.
            - If an error occurs:
                - error (str): Error message (e.g., "Part parameter required").
    """
    if not part:
        return {"error": "Part parameter required"}

    new_id = generate_entity_id("subscription")
    new_subscription = {
        "id": new_id,
        "snippet": snippet or {},
    }
    DB.setdefault("subscriptions", {})[new_id] = new_subscription
    return {"success": True, "subscription": new_subscription}


def delete(subscription_id: str) -> Dict[str, bool]:
    """
    Deletes a subscription.

    Args:
        subscription_id(str): The ID of the subscription to delete.

    Returns:
        Dict[str, bool]: A dictionary containing:
            - If successful:
                - success (bool): True
            - If the subscription ID does not exist:
                - error (str): Error message indicating the subscription was not found.
    """
    if subscription_id not in DB.get("subscriptions", {}):
        return {"error": "Subscription not found"}

    del DB["subscriptions"][subscription_id]
    return {"success": True}


def list(
    part: str,
    channel_id: Optional[str] = None,
    subscription_id: Optional[str] = None,
    mine: bool = False,
    my_recent_subscribers: bool = False,
    my_subscribers: bool = False,
    for_channel_id: Optional[str] = None,
    max_results: Optional[int] = None,
    on_behalf_of_content_owner: Optional[str] = None,
    on_behalf_of_content_owner_channel: Optional[str] = None,
    order: Optional[str] = None,
    page_token: Optional[str] = None,
) -> Dict[str, List[Dict]]:
    """
    Retrieves a list of subscriptions with optional filters.

    Args:
        part(str): The part parameter specifies the subscription resource properties that the API response will include.
        channel_id(Optional[str]): The channelId parameter specifies a YouTube channel ID. The API will only return that channel's subscriptions.
        subscription_id(Optional[str]): The id parameter identifies the subscription that is being retrieved.
        mine(bool): The mine parameter can be used to instruct the API to only return subscriptions owned by the authenticated user.
        my_recent_subscribers(bool): The myRecentSubscribers parameter can be used to instruct the API to only return subscriptions to the authenticated user's channel from the last 30 days.
        my_subscribers(bool): The mySubscribers parameter can be used to instruct the API to only return subscriptions to the authenticated user's channel.
        for_channel_id(Optional[str]): The forChannelId parameter specifies a YouTube channel ID. The API will only return subscriptions to that channel.
        max_results(Optional[int]): The maxResults parameter specifies the maximum number of items that should be returned in the result set.
        on_behalf_of_content_owner(Optional[str]): The onBehalfOfContentOwner parameter indicates that the request's authorization credentials identify a YouTube CMS user who is acting on behalf of the content owner specified in the parameter value.
        on_behalf_of_content_owner_channel(Optional[str]): The onBehalfOfContentOwnerChannel parameter specifies the YouTube channel ID of the channel to which the user is being added.
        order(Optional[str]): The order parameter specifies the order in which the API response should list subscriptions.
        page_token(Optional[str]): The pageToken parameter identifies a specific page in the result set that should be returned.

    Returns:
        Dict[str, List[Dict]]: A dictionary containing:
        - If successful:
            - items (List[Dict]): A list of subscription objects matching the filters:
                - id (str): The subscription ID.
                - snippet (Dict): Contains:
                    - channelId (str): The channel that owns the subscription.
                    - resourceId (Dict): The channel being subscribed to.
                        - kind (str): Type of the resource (e.g., "youtube#channel").
                        - channelId (str): ID of the subscribed channel.
        - If an error occurs:
            - error (str): Description of the issue (e.g., missing part parameter).
    """
    if not part:
        return {"error": "Part parameter required"}

    try:
        # Get all subscriptions from DB
        subscriptions = DB.get("subscriptions", {})
        filtered_subscriptions = []

        # Convert subscriptions dict to list
        for sub_id, sub_data in subscriptions.items():
            if subscription_id and sub_id != subscription_id:
                continue

            # Get the snippet data
            snippet = sub_data.get("snippet", {})

            # Apply filters
            if channel_id and snippet.get("channelId") != channel_id:
                continue

            if (
                for_channel_id
                and snippet.get("resourceId", {}).get("channelId") != for_channel_id
            ):
                continue

            if mine and not snippet.get("mine", False):
                continue

            if my_subscribers and not snippet.get("subscriber", False):
                continue

            filtered_subscriptions.append(sub_data)

        # Apply max_results if specified
        if max_results and max_results > 0:
            filtered_subscriptions = filtered_subscriptions[:max_results]

        return {"items": filtered_subscriptions}
    except Exception as e:
        return {"error": f"Error retrieving subscriptions: {str(e)}"}
