import pytest
from generic_media.search_api import search
from generic_media.SimulationEngine.db import DB, load_initial_db
from generic_media.SimulationEngine.search_engine import search_engine_manager

@pytest.fixture(autouse=True)
def setup_db():
    """
    Reloads the initial DB and re-initializes the search engine before each test.
    """
    DB.clear()
    DB.update(load_initial_db())
    search_engine_manager.reset_all_engines()

class TestSearchAPI:
    def test_search_success(self):
        """
        Test that the search function returns a valid media item.
        """
        result = search("Bohemian Rhapsody", "TRACK")
        assert len(result) == 1
        assert result[0]["media_item_metadata"]["entity_title"] == "Bohemian Rhapsody"
        assert result[0]["media_item_metadata"]["container_title"] == "album1"

    def test_search_not_found(self):
        """
        Test that the search function returns an empty list when no media item is found.
        """
        result = search("Non Existent Song", "TRACK")
        assert len(result) == 0

    def test_search_empty_query(self):
        """
        Test that the search function raises a ValueError for an empty query.
        """
        with pytest.raises(ValueError, match="Query cannot be empty."):
            search("", "TRACK")

    def test_search_invalid_intent_type(self):
        """
        Test that the search function raises a ValueError for an invalid intent_type.
        """
        with pytest.raises(ValueError, match="Invalid intent_type: INVALID"):
            search("test", "INVALID")

    def test_search_with_filtering_type(self):
        """
        Test that the search function works correctly with a filtering_type.
        """
        result = search("A Night at the Opera", "ALBUM", filtering_type="ALBUM")
        assert len(result) == 1
        assert result[0]["media_item_metadata"]["entity_title"] == "A Night at the Opera"
        assert result[0]["media_item_metadata"]["container_title"] is None

    def test_search_invalid_filtering_type(self):
        """
        Test that the search function raises a ValueError for an invalid filtering_type.
        """
        with pytest.raises(ValueError, match="Invalid filtering_type: INVALID"):
            search("test", "TRACK", "INVALID")

    def test_search_liked_songs(self):
        """
        Test searching for liked songs.
        """
        result = search("Bohemian Rhapsody", "LIKED_SONGS")
        assert len(result) == 1
        assert result[0]["media_item_metadata"]["entity_title"] == "Bohemian Rhapsody"
        assert result[0]["media_item_metadata"]["artist_name"] == "Queen"

    def test_search_personal_playlist(self):
        """
        Test searching for a personal playlist.
        """
        result = search("My Rock Favorites", "PERSONAL_PLAYLIST")
        assert len(result) == 1
        assert result[0]["media_item_metadata"]["entity_title"] == "My Rock Favorites"

    def test_search_artist(self):
        """
        Test searching for an artist.
        """
        result = search("Queen", "ARTIST")
        assert len(result) == 1
        assert result[0]["media_item_metadata"]["entity_title"] == "Queen"

    def test_search_podcast_show(self):
        """
        Test searching for a podcast show.
        """
        result = search("The Daily", "PODCAST_SHOW")
        assert len(result) == 1
        assert result[0]["media_item_metadata"]["entity_title"] == "The Daily"
        assert result[0]["media_item_metadata"]["content_type"] == "PODCAST_SHOW"

    def test_search_with_track_filtering(self):
        """
        Test searching with track filtering.
        """
        result = search("Bohemian Rhapsody", "TRACK", "TRACK")
        assert len(result) == 1
        assert result[0]["media_item_metadata"]["entity_title"] == "Bohemian Rhapsody"
        assert result[0]["media_item_metadata"]["content_type"] == "TRACK"

    def test_search_with_playlist_filtering(self):
        """
        Test searching with playlist filtering.
        """
        result = search("My Rock Favorites", "PERSONAL_PLAYLIST", "PLAYLIST")
        assert len(result) == 1
        assert result[0]["media_item_metadata"]["entity_title"] == "My Rock Favorites"
        assert result[0]["media_item_metadata"]["content_type"] == "PLAYLIST"
