from typing import Dict, List, Optional
from youtube.SimulationEngine.db import DB
from youtube.SimulationEngine.utils import generate_random_string, generate_entity_id
from typing import Optional, Dict, Any, List
from youtube.SimulationEngine.models import VideoUploadModel
from pydantic import ValidationError
import datetime

"""Handles YouTube video resource API operations."""


def list(
    part: str,
    chart: Optional[str] = None,
    id: Optional[str] = None,
    my_rating: Optional[str] = None,
    max_results: Optional[int] = 5,
    page_token: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Retrieves a list of videos with optional filters.

    Args:
        part (str): The part parameter specifies the video resource properties that the API response will include.
        chart (Optional[str]): Set this parameter to retrieve a list of videos that match the criteria specified by the chart parameter value.
        id (Optional[str]): The id parameter specifies a comma-separated list of the YouTube video ID(s) for the resource(s) that are being retrieved.
        my_rating (Optional[str]): Set this parameter to retrieve a list of videos that match the criteria specified by the myRating parameter value.
        max_results (Optional[int]): The maxResults parameter specifies the maximum number of items that should be returned in the result set.
        page_token (Optional[str]): The pageToken parameter identifies a specific page in the result set that should be returned.
        user_id (Optional[str]): The user_id parameter is required when using my_rating parameter.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - kind (str): Resource type ("youtube#videoListResponse").
            - items (List[Dict]): List of video resources matching the filters.
            - pageInfo (Dict): Pagination details:
                - totalResults (int): Total number of results returned.
                - resultsPerPage (int): Number of results per page.
            - error (str, optional): Error message if input validation fails.
    """
    if not part:
        return {"error": "The 'part' parameter is required."}

    filter_params = [chart, id, my_rating]
    if sum(1 for param in filter_params if param is not None) != 1:
        return {
            "error": "Exactly one of 'chart', 'id', or 'my_rating' must be specified."
        }

    # Ensure DB["videos"] exists and is a dictionary
    videos = DB.get("videos", {})
    if not isinstance(videos, dict):
        videos = {}
        DB["videos"] = videos

    filtered_videos = []
    for video_id, video_data in videos.items():
        if isinstance(video_data, dict):
            filtered_videos.append(video_data)
        else:
            # Skip invalid video data
            continue

    results: List[Dict[str, Any]] = []

    if chart:
        if chart != "mostPopular":
            return {
                "error": "Invalid value for 'chart'. Only 'mostPopular' is supported."
            }
        # Convert viewCount to int for proper sorting
        results = sorted(
            filtered_videos,
            key=lambda v: int(v.get("statistics", {}).get("viewCount", "0")),
            reverse=True,
        )

    elif id:
        id_list = [vid.strip() for vid in id.split(",")]
        results = [v for v in filtered_videos if v["id"] in id_list]

    if max_results:
        results = results[: min(max_results, 50)]

    return {
        "kind": "youtube#videoListResponse",
        "items": results,
        "pageInfo": {
            "totalResults": len(results),
            "resultsPerPage": min(max_results, 50),
        },
    }


def rate(
    video_id: str, rating: str, on_behalf_of: Optional[str] = None
) -> Dict[str, Any]:
    """Rates a video by adjusting like/dislike counts directly.

    Args:
        video_id (str): The ID of the video to rate.
        rating (str): Must be one of: "like", "dislike", "none".
        on_behalf_of (Optional[str]): Ignored (no user data is stored).


    Returns:
        Dict[str, Any]: A dictionary indicating success or error:
            - success (bool): True if rating was applied.
            - error (str, optional): Describes why the operation failed.
    """
    if video_id not in DB["videos"]:
        return {"error": "Video not found"}

    if rating not in ["like", "dislike", "none"]:
        return {"error": "Invalid rating"}

    stats = DB["videos"][video_id].get("statistics", {})

    if rating == "like":
        stats["likeCount"] = stats.get("likeCount", 0) + 1
        # If there was a previous dislike, remove it
        if stats.get("dislikeCount", 0) > 0:
            stats["dislikeCount"] = stats["dislikeCount"] - 1
    elif rating == "dislike":
        stats["dislikeCount"] = stats.get("dislikeCount", 0) + 1
        # If there was a previous like, remove it
        if stats.get("likeCount", 0) > 0:
            stats["likeCount"] = stats["likeCount"] - 1
    elif rating == "none":
        # Remove any existing rating
        if stats.get("likeCount", 0) > 0:
            stats["likeCount"] = stats["likeCount"] - 1
        if stats.get("dislikeCount", 0) > 0:
            stats["dislikeCount"] = stats["dislikeCount"] - 1

    return {"success": True}


def report_abuse(
    video_id: str,
    reason_id: str,
    on_behalf_of_content_owner: Optional[str] = None,
) -> Dict[str, Any]:
    """Reports a video for abuse.

    Args:
        video_id (str): The ID of the video to report.
        reason_id (str): The ID of the reason for reporting the video.
        on_behalf_of_content_owner (Optional[str]): The ID of the content owner on whose behalf the report is being made.

    Returns:
        Dict[str, Any]: A dictionary indicating the result:
            - success (bool): True if the report was accepted.
            - error (str, optional): Describes any validation issues.
    """
    if video_id not in DB["videos"]:
        return {"error": "Video not found"}

    if not reason_id:
        return {"error": "Reason ID is required"}

    return {"success": True}


def delete(id: str, on_behalf_of_content_owner: Optional[str] = None) -> Dict[str, Any]:
    """Deletes a video.

    Args:
        id (str): The ID of the video to delete.
        on_behalf_of_content_owner (Optional[str]): The ID of the content owner on whose behalf the deletion is being made.

    Returns:
        Dict[str, Any]: A dictionary indicating success or error:
            - success (bool): True if deletion was successful.
            - error (str, optional): Describes why the operation failed.
    """
    if id not in DB["videos"]:
        return {"error": "Video not found"}

    del DB["videos"][id]
    return {"success": True}


def update(
    part: str,
    body: Dict[str, Any],
    on_behalf_of: Optional[str] = None,
    on_behalf_of_content_owner: Optional[str] = None,
) -> Dict[str, Any]:
    """Updates a video.

    Args:
        part (str): The part parameter specifies the video resource properties that the API request is setting.
        body (Dict[str, Any]): The video resource to update.
        on_behalf_of (Optional[str]): The ID of the user on whose behalf the request is being made.
        on_behalf_of_content_owner (Optional[str]): The ID of the content owner on whose behalf the request is being made.

    Returns:
        Dict[str, Any]: The updated video resource or an error dictionary:
            - If successful: Updated video dictionary.
            - If error: Dictionary with an 'error' message.
    """
    if not part:
        return {"error": "The 'part' parameter is required."}

    if not body or "id" not in body:
        return {"error": "The 'body' parameter must include the video 'id'."}

    valid_parts = [
        "snippet",
        "contentDetails",
        "status",
        "recordingDetails",
        "localizations",
    ]
    parts_list = [p.strip() for p in part.split(",")]

    for p in parts_list:
        if p not in valid_parts:
            return {"error": f"Invalid part parameter: {p}"}

    video_id = body["id"]
    if video_id not in DB["videos"]:
        return {"error": f"Video not found: {video_id}"}

    updated_video = DB["videos"][video_id].copy()

    if "snippet" in parts_list:
        updated_video["snippet"] = body.get("snippet", updated_video.get("snippet", {}))
    if "status" in parts_list:
        updated_video["status"] = body.get("status", {})
    if "contentDetails" in parts_list:
        updated_video["contentDetails"] = body.get("contentDetails", {})
    if "recordingDetails" in parts_list:
        updated_video["recordingDetails"] = body.get("recordingDetails", {})
    if "localizations" in parts_list:
        updated_video["localizations"] = body.get("localizations", {})

    DB["videos"][video_id] = updated_video
    return updated_video

def upload(
    body: Dict[str, Any]
) -> Dict[str, Any]:
    """Uploads a video.
    Args:
        body (Dict[str, Any]): The video resource to upload.
            snippet (Dict[str, Any]): The snippet of the video to upload.
                channelId (str): The ID of the channel that the video is uploaded to.
                title (str): The title of the video.
                description (str): The description of the video.
                thumbnails (Dict[str, Any]): The thumbnails of the video.
                    default (Dict[str, Any]): The default thumbnail of the video.
                        url (str): The URL of the default thumbnail.
                        width (int): The width of the default thumbnail.
                        height (int): The height of the default thumbnail.
                    medium (Dict[str, Any]): The medium thumbnail of the video.
                        url (str): The URL of the medium thumbnail.
                        width (int): The width of the medium thumbnail.
                        height (int): The height of the medium thumbnail.
                    high (Dict[str, Any]): The high thumbnail of the video.
                        url (str): The URL of the high thumbnail.
                        width (int): The width of the high thumbnail.
                        height (int): The height of the high thumbnail.
                channelTitle (str): The title of the channel that the video is uploaded to.
                tags (List[str]): The tags of the video.
                categoryId (str): The ID of the category that the video belongs to.
            status (Dict[str, Any]): The status of the video to upload.
                uploadStatus (str): The upload status of the video. Must be one of ['processed', 'failed', 'rejected', 'uploaded', 'deleted'].
                privacyStatus (str): The privacy status of the video. Must be one of ['public', 'unlisted', 'private'].
                embeddable (bool): Whether the video is embeddable.
                madeForKids (bool): Whether the video is made for kids.
        
    Returns:
        Dict[str, Any]: The uploaded video resource:
            id (str): The ID of the video.
            snippet (Dict[str, Any]): The snippet of the video.
                publishedAt (str): The date and time the video was published.
                channelId (str): The ID of the channel that the video is uploaded to.
                title (str): The title of the video.
                description (str): The description of the video.
                thumbnails (Dict[str, Any]): The thumbnails of the video.
                    default (Dict[str, Any]): The default thumbnail of the video.
                        url (str): The URL of the default thumbnail.
                        width (int): The width of the default thumbnail.
                        height (int): The height of the default thumbnail.
                    medium (Dict[str, Any]): The medium thumbnail of the video.
                        url (str): The URL of the medium thumbnail.
                        width (int): The width of the medium thumbnail.
                        height (int): The height of the medium thumbnail.
                    high (Dict[str, Any]): The high thumbnail of the video.
                        url (str): The URL of the high thumbnail.
                        width (int): The width of the high thumbnail.
                        height (int): The height of the high thumbnail.
            status (Dict[str, Any]): The status of the video.
                uploadStatus (str): The upload status of the video.
                privacyStatus (str): The privacy status of the video.
                embeddable (bool): Whether the video is embeddable.
                madeForKids (bool): Whether the video is made for kids.
            statistics (Dict[str, Any]): The statistics of the video.
                viewCount (int): The view count of the video.
                likeCount (int): The like count of the video.
                commentCount (int): The comment count of the video.
                favoriteCount (int): The favorite count of the video.
    Raises:
        ValueError: If the 'body' parameter is not provided
                    or if the channel_id is not found in the database.
                    or if the category_id is not found in the database.
                    or if the channel_title does not match the channel title in the DB.
                    or if the upload status is not one of ['processed', 'failed', 'rejected', 'uploaded', 'deleted'].
                    or if the privacy status is not one of ['public', 'unlisted', 'private'].
        TypeError: If the 'body' parameter is not a dictionary.
        ValidationError: If the 'body' parameter is not of the correct structure as specified in the docstring.
    """

    if not body:
        raise ValueError("The 'body' parameter is required.")

    if not isinstance(body, dict):
        raise TypeError("The 'body' parameter must be a dictionary.") 

    try:
        verified_video = VideoUploadModel(**body)
    except ValidationError as e:
        raise 

    channels = DB.get("channels", {})
    if body["snippet"]["channelId"] not in channels:
        raise ValueError("Channel not found")

    categories = DB.get("videoCategories", {})
    if body["snippet"]["categoryId"] not in categories:
        raise ValueError("Category not found")

    channel_title = channels[body["snippet"]["channelId"]]["forUsername"]
    if channel_title != body["snippet"]["channelTitle"]:
        raise ValueError("Channel title does not match the channel title in the DB.")

    if body["status"]["uploadStatus"] not in ["processed", "failed", "rejected", "uploaded", "deleted"]:
        raise ValueError("Invalid upload status")

    if body["status"]["privacyStatus"] not in ["public", "unlisted", "private"]:
        raise ValueError("Invalid privacy status")

    video_id = generate_entity_id(entity_type='video')

    if "videos" not in DB:
        DB["videos"] = {}   

    new_video = { "id": video_id }

    for key, value in verified_video.model_dump().items():
        new_video[key] = value

    new_video["snippet"]["publishedAt"] = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    new_video["statistics"] = {
        "viewCount": 0,
        "likeCount": 0,
        "commentCount": 0,
        "favoriteCount": 0,
    }

    DB["videos"][video_id] = new_video
    return new_video
