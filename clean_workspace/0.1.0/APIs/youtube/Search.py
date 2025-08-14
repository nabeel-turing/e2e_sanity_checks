from typing import Dict, List, Optional
from youtube.SimulationEngine.db import DB
from youtube.SimulationEngine.utils import generate_random_string, generate_entity_id
from typing import Optional, Dict, Any, List

"""Handles YouTube search API operations."""


def list(
    part: str,
    q: Optional[str] = None,
    channel_id: Optional[str] = None,
    channel_type: Optional[str] = None,
    max_results: Optional[int] = 25,
    order: Optional[str] = "relevance",
    type: Optional[str] = "video,channel,playlist",
    video_caption: Optional[str] = None,
    video_category_id: Optional[str] = None,
    video_definition: Optional[str] = None,
    video_duration: Optional[str] = None,
    video_embeddable: Optional[str] = None,
    video_license: Optional[str] = None,
    video_syndicated: Optional[str] = None,
    video_type: Optional[str] = None,
) -> Dict[str, Any]:
    """Returns a collection of search results that match the query parameters.

    Args:
        part (str): The part parameter specifies a comma-separated list of one or more search resource properties.
        q (Optional[str]): The query term to search for.
        channel_id (Optional[str]): Filter results to only contain resources created by the specified channel.
        channel_type (Optional[str]): Filter results to only contain channels of a particular type.
        max_results (Optional[int]): The maximum number of items that should be returned in the result set.
        order (Optional[str]): The order in which to sort the returned resources.
        type (Optional[str]): A comma-separated list of resource types that should be included in the search response.
        video_caption (Optional[str]): Filter videos based on the presence, absence, or type of captions.
        video_category_id (Optional[str]): Filter videos by category ID.
        video_definition (Optional[str]): Filter videos by definition (high or standard).
        video_duration (Optional[str]): Filter videos by duration.
        video_embeddable (Optional[str]): Filter videos that can be embedded.
        video_license (Optional[str]): Filter videos by license type.
        video_syndicated (Optional[str]): Filter videos by syndication status.
        video_type (Optional[str]): Filter videos by type.

    Returns:
         Dict[str, Any]: A dictionary simulating the YouTube API search list response:
            - kind (str): Resource type ("youtube#searchListResponse").
            - etag (str): Etag of the result set.
            - items (List[Dict]): List of matched resources based on query and filters.
            - pageInfo (Dict): Includes 'totalResults' and 'resultsPerPage' counts.
            - error (str, optional): Present only if validation fails for parameters.
    """
    if not part:
        return {"error": "The 'part' parameter is required."}

    valid_parts = ["snippet", "id"]
    for p in part.split(","):
        if p.strip() not in valid_parts:
            return {"error": f"Invalid part parameter: {p}"}

    # Handle multiple types
    search_types = (
        [t.strip() for t in type.split(",")]
        if type
        else ["video", "channel", "playlist"]
    )

    results = []
    for search_type in search_types:
        if search_type == "video":
            videos = DB["videos"].values()
            filtered_videos = videos
            if q:
                filtered_videos = [
                    v
                    for v in filtered_videos
                    if q.lower() in v["snippet"]["title"].lower()
                    or q.lower() in v["snippet"]["description"].lower()
                ]
            if channel_id:
                filtered_videos = [
                    v
                    for v in filtered_videos
                    if v["snippet"]["channelId"] == channel_id
                ]
            if video_caption:
                if video_caption == "any":
                    filtered_videos = [
                        v
                        for v in filtered_videos
                        if v["contentDetails"]["caption"] == "true"
                    ]
                elif video_caption == "closedCaption":
                    filtered_videos = [
                        v
                        for v in filtered_videos
                        if v["contentDetails"]["caption"] == "true"
                    ]
                elif video_caption == "none":
                    filtered_videos = [
                        v
                        for v in filtered_videos
                        if v["contentDetails"]["caption"] == "false"
                    ]
            if video_category_id:
                filtered_videos = [
                    v
                    for v in filtered_videos
                    if v["snippet"]["categoryId"] == video_category_id
                ]
            if video_definition:
                filtered_videos = [
                    v
                    for v in filtered_videos
                    if v["contentDetails"]["definition"] == video_definition
                ]
            if video_duration:
                filtered_videos = [
                    v
                    for v in filtered_videos
                    if v["contentDetails"]["duration"].startswith(video_duration)
                ]
            if video_embeddable:
                filtered_videos = [
                    v
                    for v in filtered_videos
                    if v["status"]["embeddable"] == (video_embeddable == "true")
                ]
            if video_license:
                filtered_videos = [
                    v
                    for v in filtered_videos
                    if v["status"]["license"] == video_license
                ]
            if video_syndicated:
                filtered_videos = [
                    v
                    for v in filtered_videos
                    if v["status"].get("syndicated", False)
                    == (video_syndicated == "true")
                ]
            if video_type:
                filtered_videos = [
                    v
                    for v in filtered_videos
                    if v["status"].get("type", "") == video_type
                ]

            for video in filtered_videos:
                item = {
                    "kind": "youtube#searchResult",
                    "etag": "etag_value",
                    "id": {"kind": "youtube#video", "videoId": video["id"]},
                }
                if "snippet" in part:
                    snippet = video.get("snippet", {})
                    item["snippet"] = {
                        "channelId": snippet.get("channelId", ""),
                        "title": snippet.get("title", ""),
                        "description": snippet.get("description", ""),
                        "publishedAt": snippet.get("publishedAt", ""),
                        "categoryId": snippet.get("categoryId", ""),
                    }

        elif search_type == "channel":
            channels = DB["channels"].values()
            filtered_channels = channels
            if q:
                filtered_channels = [
                    c
                    for c in filtered_channels
                    if q.lower() in c.get("snippet", {}).get("title", "").lower()
                    or q.lower() in c.get("snippet", {}).get("description", "").lower()
                ]
            if channel_id:
                filtered_channels = [
                    c for c in filtered_channels if c["id"] == channel_id
                ]
            if channel_type:
                filtered_channels = [
                    c
                    for c in filtered_channels
                    if c.get("snippet", {}).get("type", "") == channel_type
                ]

            for channel in filtered_channels:
                item = {
                    "kind": "youtube#searchResult",
                    "etag": "etag_value",
                    "id": {"kind": "youtube#channel", "channelId": channel["id"]},
                }
                if "snippet" in part:
                    item["snippet"] = channel.get("snippet", {})
                results.append(item)

        elif search_type == "playlist":
            playlists = DB.get("playlists", {}).values()
            filtered_playlists = playlists
            if q:
                filtered_playlists = [
                    p
                    for p in filtered_playlists
                    if q.lower() in p["snippet"]["title"].lower()
                    or q.lower() in p["snippet"]["description"].lower()
                ]
            if channel_id:
                filtered_playlists = [
                    p
                    for p in filtered_playlists
                    if p["snippet"]["channelId"] == channel_id
                ]

            for playlist in filtered_playlists:
                item = {
                    "kind": "youtube#searchResult",
                    "etag": "etag_value",
                    "id": {"kind": "youtube#playlist", "playlistId": playlist["id"]},
                }
                if "snippet" in part:
                    item["snippet"] = playlist["snippet"]
                results.append(item)

    # Order the results
    if order == "relevance":
        pass  # Default order
    elif order == "viewCount":
        results = sorted(
            results,
            key=lambda x: DB["videos"]
            .get(x["id"].get("videoId", ""), {})
            .get("statistics", {})
            .get("viewCount", 0),
            reverse=True,
        )
    elif order == "date":
        results = sorted(
            results,
            key=lambda x: x.get("snippet", {}).get("publishedAt", "0000-00-00"),
            reverse=True,
        )
    elif order == "title":
        results = sorted(
            results, key=lambda x: x.get("snippet", {}).get("title", "").lower()
        )
    else:
        return {"error": f"Invalid order parameter: {order}"}

    if max_results:
        results = results[: min(max_results, 50)]

    return {
        "kind": "youtube#searchListResponse",
        "etag": "etag_value",
        "items": results,
        "pageInfo": {"totalResults": len(results), "resultsPerPage": len(results)},
    }
