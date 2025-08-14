"""
Activities module for youtube.
"""

from typing import Dict, List, Optional
from youtube.SimulationEngine.db import DB
from youtube.SimulationEngine.utils import generate_random_string, generate_entity_id
from typing import Optional, Dict, Any, List


def list(
    part: str,
    channelId: Optional[str] = None,
    mine: Optional[bool] = None,
    maxResults: Optional[int] = None,
    pageToken: Optional[str] = None,
    publishedAfter: Optional[str] = None,
    publishedBefore: Optional[str] = None,
    regionCode: Optional[str] = None,
) -> Dict[str, List]:
    """
    Retrieves a list of activities with optional filters.

    This method allows fetching activities from YouTube based on various criteria such as
    channel ID, publication date range, and region code. Activities represent various
    actions that occur on YouTube, such as uploads, likes, comments, etc.

    Args:
        part (str): The part parameter specifies the activity resource properties that
            the API response will include.
        channelId (Optional[str]): The channelId parameter specifies a YouTube channel ID.
            The API will only return that channel's activities.
        mine (Optional[bool]): Set this parameter's value to true to retrieve a feed of
            the authenticated user's activities.
        maxResults (Optional[int]): The maxResults parameter specifies the maximum number
            of items that should be returned in the result set.
        pageToken (Optional[str]): The pageToken parameter identifies a specific page in
            the result set that should be returned.
        publishedAfter (Optional[str]): The publishedAfter parameter specifies the earliest
            date and time that an activity could have occurred.
        publishedBefore (Optional[str]): The publishedBefore parameter specifies the latest
            date and time that an activity could have occurred.
        regionCode (Optional[str]): The regionCode parameter instructs the API to select a
            video chart available in the specified region.

    Returns:
        Dict[str, List]: A dictionary containing:
            - items (List[Dict]): A list of activity items that match the request criteria.
                Each activity item contains:
                - id (str): The ID of the activity
                - snippet (Dict): General information about the basic details about the activity,
                                  including the activity's type and group ID.
                    - publishedAt (str): The date and time the activity occurred
                    - channelId (str): The ID of the channel that performed the activity
                    - title (str): The title of the activity
                    - description (str): A description of the activity
                    - thumbnails (Dict): Thumbnail images for the activity
                        - default (Dict): Default thumbnail with url, width, and height
                        - medium (Dict): Medium thumbnail with url, width, and height
                        - high (Dict): High thumbnail with url, width, and height
                        - standard (Dict): Standard thumbnail with url, width, and height
                        - maxres (Dict): Maximum resolution thumbnail with url, width, and height
                    - channelTitle (str): The title of the channel
                - contentDetails (Dict): Details specific to the type of activity
                    - upload (Dict): For upload activities, contains videoId
                    - like (Dict): For like activities, contains type
                    - comment (Dict): For comment activities, contains commentId
                    - favorite (Dict): For favorite activities, contains type



    """
    results = DB["activities"]
    if channelId:
        results = [a for a in results if a.get("channelId") == channelId]
    if mine is not None:
        results = [a for a in results if a.get("mine") == mine]
    if maxResults:
        results = results[: min(maxResults, 50)]
    if publishedAfter:
        results = [
            a
            for a in results
            if a.get("publishedAfter", "2023-01-01T00:00:00Z") >= publishedAfter
        ]
    if publishedBefore:
        results = [
            a
            for a in results
            if a.get("publishedBefore", "2023-12-31T00:00:00Z") <= publishedBefore
        ]
    if regionCode:
        results = [a for a in results if a.get("regionCode") == regionCode]
    return {"items": results}
