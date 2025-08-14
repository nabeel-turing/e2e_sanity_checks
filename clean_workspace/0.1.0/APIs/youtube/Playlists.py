from typing import Dict, List, Optional, Any
from youtube.SimulationEngine.db import DB
from youtube.SimulationEngine.utils import generate_random_string, generate_entity_id
import time
from youtube.SimulationEngine.models import ThumbnailInputModel
from pydantic import ValidationError

"""Handles YouTube playlist resource API operations."""

def create(
    ownerId: str,
    title: str,
    description: Optional[str] = "",
    privacyStatus: Optional[str] = "public",
    list_of_videos: Optional[List[str]] = None,
    thumbnails: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Creates a new playlist.

    Args:
        ownerId (str): The ownerId parameter specifies the YouTube channel ID of the user who owns the playlist.
        title (str): The title parameter specifies the title of the playlist.
        description (Optional[str]): The description parameter specifies the description of the playlist. Defaults to empty string.
        privacyStatus (Optional[str]): The privacyStatus parameter specifies the privacy status of the playlist. Defaults to "public". Must be one of ['public', 'private', 'unlisted'].
        list_of_videos (Optional[List[str]]): The list_of_videos parameter specifies the list of videos in the playlist. Defaults to empty list.
        thumbnails (Optional[Dict[str, Any]]): The thumbnails parameter specifies the thumbnails of the playlist. Defaults to empty dictionary or thumbnail of the first video in the list_of_videos if list_of_videos is provided.
            default - Dictionary with default thumbnail
                url - URL of the thumbnail
                height - Height of the thumbnail
                width - Width of the thumbnail
            medium - Dictionary with medium thumbnail
                url - URL of the thumbnail
                height - Height of the thumbnail
                width - Width of the thumbnail
            high - Dictionary with high thumbnail
                url - URL of the thumbnail
                height - Height of the thumbnail
                width - Width of the thumbnail

    Returns:
        Dict[str, Any]: A dictionary containing:
            - kind (str): Resource type ("youtube#playlist").
            - id (str): The playlist ID.
            - snippet (Dict): Playlist metadata.
                - publishedAt (str): The date and time when the playlist was published.
                - channelId (str): The channel ID of the playlist.
                - title (str): The title of the playlist.
                - list_of_videos (List[str]): The list of videos in the playlist.
                - description (str): The description of the playlist.
                - thumbnails (Dict): The thumbnails of the playlist.
                    - default (Dict): The default thumbnail of the playlist.
                        - url (str): The URL of the thumbnail.
                        - height (int): The height of the thumbnail.
                        - width (int): The width of the thumbnail.
                    - medium (Dict): The medium thumbnail of the playlist.
                        - url (str): The URL of the thumbnail.
                        - height (int): The height of the thumbnail.
                        - width (int): The width of the thumbnail.
                    - high (Dict): The high thumbnail of the playlist.
                        - url (str): The URL of the thumbnail.
                        - height (int): The height of the thumbnail.
                        - width (int): The width of the thumbnail.
            - status (Dict): Playlist status information.
                - privacyStatus (str): The privacy status of the playlist.
            - contentDetails (Dict): Playlist content details.
                - itemCount (int): The number of items in the playlist.
    Raises:
        ValueError: If ownerID is not provided or title is not provided 
                    or privacyStatus is not one of ['public', 'private', 'unlisted']
                    or list_of_videos(if provided) contains videos that are not found in the database
                    or ownerId is not found in the database.
        TypeError: If ownerId is not a string or title is not a string 
                    or list_of_videos(if provided) is not a list 
                    or thumbnails(if provided) is not a dictionary 
                    or description(if provided) is not a string 
                    or privacyStatus(if provided) is not a string
        ValidationError: If thumbnails(if provided) is not in the correct format

    """
    if not ownerId:
        raise ValueError("ownerId is required")
    if not title:
        raise ValueError("title is required")
    if not isinstance(ownerId, str):
        raise TypeError("ownerId must be a string")
    if not isinstance(title, str):
        raise TypeError("title must be a string")
    # Handle None defaults
    if list_of_videos is None:
        list_of_videos = []
    if thumbnails is None:
        thumbnails = {}
    
    if not isinstance(list_of_videos, List):
        raise TypeError("list_of_videos must be a list")
    if not isinstance(thumbnails, dict):
        raise TypeError("thumbnails must be a dictionary")
    if not isinstance(description, str):
        raise TypeError("description must be a string")
    if not isinstance(privacyStatus, str):
        raise TypeError("privacyStatus must be a string")
    if privacyStatus not in ["public", "private", "unlisted"]:
        raise ValueError("privacyStatus must be one of ['public', 'private', 'unlisted']")
    channels = DB.get("channels", {})
    if ownerId not in channels:
        raise ValueError(f"Channel with given ID not found in the database.")
    videos = DB.get("videos", {})
    for video_id in list_of_videos:
        if video_id not in videos:
            raise ValueError(f"Video with id {video_id} not found in the database.")
    
    playlist_id = generate_entity_id("playlist")
    current_time = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    if thumbnails != {}:
        try:
            ThumbnailInputModel(**thumbnails)
        except ValidationError as e:
            raise e
    if list_of_videos != [] and thumbnails == {}:
        thumbnails = DB["videos"][list_of_videos[0]]["snippet"]["thumbnails"]
    playlist = {
        "kind": "youtube#playlist",
        "id": playlist_id,
        "snippet": {
            "publishedAt": current_time,
            "channelId": ownerId,
            "title": title,
            "list_of_videos": list_of_videos,
            "description": description,
            "thumbnails": thumbnails,
        },
        "status": {
            "privacyStatus": privacyStatus,
        },
        "contentDetails": {
            "itemCount": len(list_of_videos),
        },
        }

    if "playlists" not in DB:
        DB["playlists"] = {}
    DB["playlists"][playlist_id] = playlist
    return playlist


def list_playlists(
    channel_id: Optional[str] = None,
    max_results: Optional[int] = 50
) -> Dict[str, Any]:
    """Retrieves a list of playlists with optional filters.
    
    Args:
        channel_id (Optional[str]): The channelId parameter specifies a YouTube channel ID. If not provided, all playlists will be returned.
        max_results (Optional[int]): The max_results parameter specifies the maximum number of items that should be returned in the result set. Defaults to 50.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - items (List[Dict]): List of playlist resources matching the filters.
                    - kind (str): Resource type ("youtube#playlist").
                    - id (str): The playlist ID.
                    - snippet (Dict): Playlist metadata.
                        - publishedAt (str): The date and time when the playlist was published.
                        - channelId (str): The channel ID of the playlist.
                        - title (str): The title of the playlist.
                        - list_of_videos (List[str]): The list of videos in the playlist.
                        - description (str): The description of the playlist.
                        - thumbnails (Dict): The thumbnails of the playlist.
                            - default (Dict): The default thumbnail of the playlist.
                                - url (str): The URL of the thumbnail.
                                - height (int): The height of the thumbnail.
                                - width (int): The width of the thumbnail.
                            - medium (Dict): The medium thumbnail of the playlist.
                                - url (str): The URL of the thumbnail.
                                - height (int): The height of the thumbnail.
                                - width (int): The width of the thumbnail.
                            - high (Dict): The high thumbnail of the playlist.
                                - url (str): The URL of the thumbnail.
                                - height (int): The height of the thumbnail.
                                - width (int): The width of the thumbnail.
                    - status (Dict): Playlist status information.
                        - privacyStatus (str): The privacy status of the playlist.
                    - contentDetails (Dict): Playlist content details.
                        - itemCount (int): The number of items in the playlist.
            Or an empty list if no playlists are found.
    Raises:
        ValueError: If channel_id(if provided) is not found in the database
                    or max_results(if provided) is not between 1 and 50
        TypeError: If channel_id(if provided) is not a string 
                    or max_results(if provided) is not an integer.
    """
    if channel_id:
        if not isinstance(channel_id, str):
            raise TypeError("channel_id must be a string")
        channels = DB.get("channels", {})
        if channel_id not in channels:
            raise ValueError(f"Channel with given ID not found in the database.")
    if max_results is not None:
        if not isinstance(max_results, int):
            raise TypeError("max_results must be an integer")
        if max_results <= 0 or max_results > 50:
            raise ValueError("max_results must be an integer between 1 and 50")
    
    playlists = DB.get("playlists", {})
    if playlists == {}:
        return {
            "items": [],
            }

    results= []

    if channel_id:
        # Filter by channel ID
        results = [p for _,p in playlists.items() if p.get("snippet", {}).get("channelId") == channel_id]
    else:
        # Return all playlists if no filter specified
        results = [p for _,p in playlists.items()]

    max_results = min(max_results if max_results is not None else 50, len(results))
    results = results[:max_results]

    return {
        "items": results
    }


def get(playlist_id: str) -> Dict[str, Any]:
    """Retrieves a specific playlist by ID.
    
    Args:
        playlist_id (str): The playlist_id parameter specifies the YouTube playlist ID.

    Returns:
        Dict[str, Any]: A dictionary containing the playlist resource.
            - kind (str): Resource type ("youtube#playlist").
            - id (str): The playlist ID.
            - snippet (Dict): Playlist metadata.
                - publishedAt (str): The date and time when the playlist was published.
                - channelId (str): The channel ID of the playlist.
                - title (str): The title of the playlist.
                - list_of_videos (List[str]): The list of videos in the playlist.
                - description (str): The description of the playlist.
                - thumbnails (Dict): The thumbnails of the playlist.
                    - default (Dict): The default thumbnail of the playlist.
                        - url (str): The URL of the thumbnail.
                        - height (int): The height of the thumbnail.
                        - width (int): The width of the thumbnail.
                    - medium (Dict): The medium thumbnail of the playlist.
                        - url (str): The URL of the thumbnail.
                        - height (int): The height of the thumbnail.
                        - width (int): The width of the thumbnail.
                    - high (Dict): The high thumbnail of the playlist.
                        - url (str): The URL of the thumbnail.
                        - height (int): The height of the thumbnail.
                        - width (int): The width of the thumbnail.
            - status (Dict): Playlist status information.
                - privacyStatus (str): The privacy status of the playlist.
            - contentDetails (Dict): Playlist content details.
                - itemCount (int): The number of items in the playlist.
    Raises:
        ValueError: If playlist_id is not provided or playlist not found.
        TypeError: If playlist_id is not a string.
    """
    if not playlist_id:
        raise ValueError("playlist_id is required")
    if not isinstance(playlist_id, str):
        raise TypeError("playlist_id must be a string")
    
    playlists = DB.get("playlists", {})
    if playlist_id not in playlists:
        raise ValueError(f"Playlist with given ID not found in the database.")
    
    return playlists[playlist_id]


def update(
    playlist_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    privacyStatus: Optional[str] = None,
    thumbnails: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Updates an existing playlist.
    
    Args:
        playlist_id (str): The playlist_id parameter specifies the YouTube playlist ID.
        title (Optional[str]): The title parameter specifies the new title of the playlist.
        description (Optional[str]): The description parameter specifies the new description of the playlist.
        privacyStatus (Optional[str]): The privacyStatus parameter specifies the new privacy status of the playlist. Must be one of ['public', 'private', 'unlisted'].
        thumbnails (Optional[Dict[str, Any]]): The thumbnails parameter specifies the new thumbnails of the playlist.

    Returns:
        Dict[str, Any]: A dictionary containing the updated playlist resource.
            - kind (str): Resource type ("youtube#playlist").
            - id (str): The playlist ID.
            - snippet (Dict): Updated playlist metadata.
                - publishedAt (str): The date and time when the playlist was published.
                - channelId (str): The channel ID of the playlist.
                - title (str): The title of the playlist.
                - list_of_videos (List[str]): The list of videos in the playlist.
                - description (str): The description of the playlist.
                - thumbnails (Optional(Dict)): The thumbnails of the playlist.
                    - default (Dict): The default thumbnail of the playlist.
                        - url (str): The URL of the thumbnail.
                        - height (int): The height of the thumbnail.
                        - width (int): The width of the thumbnail.
                    - medium (Dict): The medium thumbnail of the playlist.
                        - url (str): The URL of the thumbnail.
                        - height (int): The height of the thumbnail.
                        - width (int): The width of the thumbnail.
                    - high (Dict): The high thumbnail of the playlist.
                        - url (str): The URL of the thumbnail.
                        - height (int): The height of the thumbnail.
                        - width (int): The width of the thumbnail.
            - status (Dict): Updated playlist status information.
                - privacyStatus (str): The privacy status of the playlist.
            - contentDetails (Dict): Playlist content details.
                - itemCount (int): The number of items in the playlist.
            
    Raises:
        ValueError: If playlist_id is not provided or playlist not found or privacyStatus is invalid.
        TypeError: If parameters are not of correct types.
        ValidationError: If thumbnails(if provided) is not in the correct format.
    """
    if not playlist_id:
        raise ValueError("playlist_id is required")
    if not isinstance(playlist_id, str):
        raise TypeError("playlist_id must be a string")
    
    playlists = DB.get("playlists", {})
    if playlist_id not in playlists:
        raise ValueError(f"Playlist with given ID not found in the database.")
    
    playlist = playlists[playlist_id]
    
    # Update fields if provided
    if title is not None:
        if not isinstance(title, str):
            raise TypeError("title must be a string")
        if title == "":
            raise ValueError("title cannot be empty")
        playlist["snippet"]["title"] = title
    
    if description is not None:
        if not isinstance(description, str):
            raise TypeError("description must be a string")
        playlist["snippet"]["description"] = description
    
    if privacyStatus is not None:
        if not isinstance(privacyStatus, str):
            raise TypeError("privacyStatus must be a string")
        if privacyStatus not in ["public", "private", "unlisted"]:
            raise ValueError("privacyStatus must be one of ['public', 'private', 'unlisted']")
        playlist["status"]["privacyStatus"] = privacyStatus
    
    if thumbnails is not None:
        if not isinstance(thumbnails, dict):
            raise TypeError("thumbnails must be a dictionary")
        try:
            ThumbnailInputModel(**thumbnails)
        except ValidationError as e:
            raise e
        playlist["snippet"]["thumbnails"] = thumbnails
    
    # Update the playlist in database
    DB["playlists"][playlist_id] = playlist
    
    return playlist


def delete(playlist_id: str) -> bool:
    """Deletes a playlist.
    
    Args:
        playlist_id (str): The playlist_id parameter specifies the YouTube playlist ID.

    Returns:
        bool: True if playlist is deleted.
            
    Raises:
        ValueError: If playlist_id is not provided or playlist not found.
        TypeError: If playlist_id is not a string.
    """
    if not playlist_id:
        raise ValueError("playlist_id is required")
    if not isinstance(playlist_id, str):
        raise TypeError("playlist_id must be a string")
    
    playlists = DB.get("playlists", {})
    if playlist_id not in playlists:
        raise ValueError(f"Playlist with given ID not found in the database.")
    
    # Delete playlist
    del playlists[playlist_id]  
    
    return True


def add_video(playlist_id: str, video_id: str) -> Dict[str, Any]:
    """Adds a video to a playlist.
    
    Args:
        playlist_id (str): The playlist_id parameter specifies the YouTube playlist ID.
        video_id (str): The video_id parameter specifies the YouTube video ID to add.

    Returns:
        Dict[str, Any]: A dictionary containing the updated playlist resource.
            - kind (str): Resource type ("youtube#playlist").
            - id (str): The playlist ID.
            - snippet (Dict): Updated playlist metadata with new video added.
                - publishedAt (str): The date and time when the playlist was published.
                - channelId (str): The channel ID of the playlist.
                - title (str): The title of the playlist.
                - list_of_videos (List[str]): The list of videos in the playlist.
                - description (str): The description of the playlist.
                - thumbnails (Dict): The thumbnails of the playlist.
                    - default (Dict): The default thumbnail of the playlist.
                        - url (str): The URL of the thumbnail.
                        - height (int): The height of the thumbnail.
                        - width (int): The width of the thumbnail.
                    - medium (Dict): The medium thumbnail of the playlist.
                        - url (str): The URL of the thumbnail.
                        - height (int): The height of the thumbnail.
                        - width (int): The width of the thumbnail.
                    - high (Dict): The high thumbnail of the playlist.
                        - url (str): The URL of the thumbnail.
                        - height (int): The height of the thumbnail.
                        - width (int): The width of the thumbnail.
            - status (Dict): Playlist status information.
                - privacyStatus (str): The privacy status of the playlist.
            - contentDetails (Dict): Updated playlist content details with new item count.
                - itemCount (int): The number of items in the playlist.
            
    Raises:
        ValueError: If playlist_id or video_id is not provided, playlist not found, or video not found in the database.
        TypeError: If video_id and playlist_id are not strings.
    """
    if not playlist_id:
        raise ValueError("playlist_id is required")
    if not video_id:
        raise ValueError("video_id is required")
    if not isinstance(playlist_id, str):
        raise TypeError("playlist_id must be a string")
    if not isinstance(video_id, str):
        raise TypeError("video_id must be a string")
    
    playlists = DB.get("playlists", {})
    if playlist_id not in playlists:
        raise ValueError(f"Playlist with given ID not found in the database.")
    
    # Check if video exists
    videos = DB.get("videos", {})
    if video_id not in videos:
        raise ValueError(f"Video with given ID not found in the database.")
    
    playlist = playlists[playlist_id]
    
    # Check if video is already in playlist
    list_of_videos = playlist["snippet"].get("list_of_videos", [])

    
    # Add video to playlist
    list_of_videos.append(video_id)
    playlist["snippet"]["list_of_videos"] = list_of_videos
    playlist["contentDetails"]["itemCount"] = len(list_of_videos)
    
    
    # Update the playlist in database
    DB["playlists"][playlist_id] = playlist
    
    
    return playlist


def delete_video(playlist_id: str, video_id: str) -> bool:
    """Removes a video from a playlist.
    
    Args:
        playlist_id (str): The playlist_id parameter specifies the YouTube playlist ID.
        video_id (str): The video_id parameter specifies the YouTube video ID to remove.

    Returns:
        bool: True if video is removed from playlist.
            
    Raises:
        ValueError: If playlist_id or video_id is not provided, playlist not found, or video not in playlist.
        TypeError: If playlist_id and video_id are not strings.
    """
    if not playlist_id:
        raise ValueError("playlist_id is required")
    if not video_id:
        raise ValueError("video_id is required")
    if not isinstance(playlist_id, str):
        raise TypeError("playlist_id must be a string")
    if not isinstance(video_id, str):
        raise TypeError("video_id must be a string")
    
    playlists = DB.get("playlists", {})
    if playlist_id not in playlists:
        raise ValueError(f"Playlist with given ID not found in the database.")
    
    playlist = playlists[playlist_id]
    # Check if video is in playlist
    list_of_videos = playlist["snippet"].get("list_of_videos", [])

    if video_id not in list_of_videos :
        raise ValueError(f"Video with given ID is not in the playlist.")
    
    # Remove video from playlist
    list_of_videos.remove(video_id)
    playlist["snippet"]["list_of_videos"] = list_of_videos
    playlist["contentDetails"]["itemCount"] = len(list_of_videos)
    
    # Update the playlist in database
    DB["playlists"][playlist_id] = playlist
    
    return True


def reorder(playlist_id: str, video_order: List[str]) -> Dict[str, Any]:
    """Reorders videos in a playlist.
    
    Args:
        playlist_id (str): The playlist_id parameter specifies the YouTube playlist ID.
        video_order (List[str]): The video_order parameter specifies the new order of video IDs.

    Returns:
        Dict[str, Any]: A dictionary containing the updated playlist resource.
            - kind (str): Resource type ("youtube#playlist").
            - id (str): The playlist ID.
            - snippet (Dict): Updated playlist metadata with reordered videos.
                - publishedAt (str): The date and time when the playlist was published.
                - channelId (str): The channel ID of the playlist.
                - title (str): The title of the playlist.
                - list_of_videos (List[str]): The list of videos in the playlist.
                - description (str): The description of the playlist.
                - thumbnails (Dict): The thumbnails of the playlist.
                    - default (Dict): The default thumbnail of the playlist.
                        - url (str): The URL of the thumbnail.
                        - height (int): The height of the thumbnail.
                        - width (int): The width of the thumbnail.
                    - medium (Dict): The medium thumbnail of the playlist.
                        - url (str): The URL of the thumbnail.
                        - height (int): The height of the thumbnail.
                        - width (int): The width of the thumbnail.
                    - high (Dict): The high thumbnail of the playlist.
                        - url (str): The URL of the thumbnail.
                        - height (int): The height of the thumbnail.
                        - width (int): The width of the thumbnail.
            - status (Dict): Playlist status information.
                - privacyStatus (str): The privacy status of the playlist.
            - contentDetails (Dict): Playlist content details.
                - itemCount (int): The number of items in the playlist.
    Raises:
        ValueError: If playlist_id is not provided, playlist not found, 
                    or video_order is not provided or does not contain the same videos as the current playlist.
        TypeError: If playlist_id is not a string or video_order is not a list.
    """
    if not playlist_id:
        raise ValueError("playlist_id is required")
    if not isinstance(playlist_id, str):
        raise TypeError("playlist_id must be a string")
    if not video_order:
        raise ValueError("video_order is required")
    if not isinstance(video_order, List):
        raise TypeError("video_order must be a list")
    
    playlists = DB.get("playlists", {})
    if playlist_id not in playlists:
        raise ValueError(f"Playlist with given ID not found in the database.")
    
    playlist = playlists[playlist_id]
    current_videos = playlist["snippet"].get("list_of_videos", [])
    
    # Validate that video_order contains the same videos as current playlist
    if set(video_order) != set(current_videos):
        raise ValueError("video_order must contain the same videos as the current playlist")
    
    # Update playlist with new order
    playlist["snippet"]["list_of_videos"] = video_order
    
    # Update the playlist in database
    DB["playlists"][playlist_id] = playlist
    
    return playlist

