from typing import Dict, List, Optional, Any
from youtube.SimulationEngine.db import DB
from youtube.SimulationEngine.utils import generate_random_string, generate_entity_id


"""
    Handles YouTube Channel Statistics API operations.
    
    This class provides methods to retrieve and update various statistics
    associated with a YouTube channel, such as subscriber count, view count, etc.
"""


def comment_count(comment_count: Optional[int] = None) -> Dict[str, int]:
    """
    Retrieves or sets the number of comments for the channel.

    Args:
        comment_count (Optional[int]): If provided, sets the comment count to this value.
                                      If None, retrieves the current comment count.

    Returns:
        Dict[str, int]: A dictionary containing:
        - If `comment_count` is provided:
            - commentCount (int): The newly set comment count for the channel.
        - If `comment_count` is not provided:
            - commentCount (int): The current number of comments on the channel from the database.
    """
    if comment_count is not None:
        return {"commentCount": comment_count}
    return {"commentCount": DB.get("channelStatistics", {}).get("commentCount", 0)}


def hidden_subscriber_count(
    hidden_subscriber_count: Optional[bool] = None,
) -> Dict[str, bool]:
    """
    Checks whether the subscriber count is hidden.

    Args:
        hidden_subscriber_count (Optional[bool]): If provided, sets whether the subscriber count is hidden.
                                                 If None, retrieves the current setting.

    Returns:
        Dict[str, bool]: A dictionary containing:
        - If `hidden_subscriber_count` is provided:
            - hiddenSubscriberCount (bool): The newly set visibility state.
        - If `hidden_subscriber_count` is not provided:
            - hiddenSubscriberCount (bool): The current visibility status from the database.
    """
    if hidden_subscriber_count is not None:
        return {"hiddenSubscriberCount": hidden_subscriber_count}
    return {
        "hiddenSubscriberCount": DB.get("channelStatistics", {}).get(
            "hiddenSubscriberCount", False
        )
    }


def subscriber_count(subscriber_count: Optional[int] = None) -> Dict[str, int]:
    """
    Retrieves or sets the number of subscribers of the channel.

    Args:
        subscriber_count (Optional[int]): If provided, sets the subscriber count to this value.
                                         If None, retrieves the current subscriber count.

    Returns:
        Dict[str, int]: A dictionary containing:
        - If `subscriber_count` is provided:
            - subscriberCount (int): The newly set subscriber count.
        - If `subscriber_count` is not provided:
            - subscriberCount (int): The current subscriber count from the database.
    """
    if subscriber_count is not None:
        return {"subscriberCount": subscriber_count}
    return {
        "subscriberCount": DB.get("channelStatistics", {}).get("subscriberCount", 0)
    }


def video_count(video_count: Optional[int] = None) -> Dict[str, int]:
    """
    Retrieves or sets the number of videos uploaded to the channel.

    Args:
        video_count (Optional[int]): If provided, sets the video count to this value.
                                    If None, retrieves the current video count.

    Returns:
        Dict[str, int]: A dictionary containing:
        - If `video_count` is provided:
            - videoCount (int): The newly set number of uploaded videos.
        - If `video_count` is not provided:
            - videoCount (int): The current number of videos from the database.
    """
    if video_count is not None:
        return {"videoCount": video_count}
    return {"videoCount": DB.get("channelStatistics", {}).get("videoCount", 0)}


def view_count(view_count: Optional[int] = None) -> Dict[str, int]:
    """
    Retrieves or sets the total view count of the channel.

    Args:
        view_count (Optional[int]): If provided, sets the view count to this value.
                                   If None, retrieves the current view count.

    Returns:
        Dict[str, int]: A dictionary containing:
        - If `view_count` is provided:
            - viewCount (int): The newly set total number of views.
        - If `view_count` is not provided:
            - viewCount (int): The current total view count from the database.
    """
    if view_count is not None:
        return {"viewCount": view_count}
    return {"viewCount": DB.get("channelStatistics", {}).get("viewCount", 0)}
