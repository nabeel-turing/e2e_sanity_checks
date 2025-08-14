
from typing import Dict, Any, List, Optional
from generic_media.SimulationEngine.models import IntentType, FilteringType
from generic_media.SimulationEngine.db import DB
from generic_media.SimulationEngine.utils import search_media
from datetime import datetime, timezone

def search(query: str, intent_type: str, filtering_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Search for songs, artists, albums, playlists or podcasts on a media provider.

    Args:
        query (str): Content that the user is looking for. Must be a non-empty string, even for generic types.
        intent_type (str): The type of content to search for. One of: "ALBUM", "ARTIST", "GENERIC_MUSIC", "GENERIC_PODCAST", "GENERIC_MUSIC_NEW", "GENERIC_SOMETHING_ELSE", "LIKED_SONGS", "PERSONAL_PLAYLIST", "PODCAST_EPISODE", "PODCAST_SHOW", "PUBLIC_PLAYLIST", "TRACK".
        filtering_type (Optional[str]): The type of content to filter by. One of: "ALBUM", "PLAYLIST", "TRACK".

    Returns:
        List[Dict[str, Any]]: A list of media items that match the search query. Each media item is a dictionary with the following keys:
            uri (str): The URI of the media item.
            media_item_metadata (Dict[str, Any]): Metadata about the media item.
                entity_title (Optional[str]): The title of the media item.
                container_title (Optional[str]): The title of the container of the media item (e.g., album or show).
                description (Optional[str]): A description of the media item.
                artist_name (Optional[str]): The name of the artist.
                content_type (Optional[str]): The type of content.
            provider (Optional[str]): The provider of the media item.
            action_card_content_passthrough (Optional[str]): The URI of the media item.

    Raises:
        ValueError: If the query is empty or if the intent_type or filtering_type are invalid.
    """
    # Input validation
    if not query:
        raise ValueError("Query cannot be empty.")

    try:
        intent = IntentType(intent_type)
    except ValueError:
        raise ValueError(f"Invalid intent_type: {intent_type}")

    if filtering_type:
        try:
            FilteringType(filtering_type)
        except ValueError:
            raise ValueError(f"Invalid filtering_type: {filtering_type}")

    results = search_media(query, intent_type, filtering_type)

    return results
