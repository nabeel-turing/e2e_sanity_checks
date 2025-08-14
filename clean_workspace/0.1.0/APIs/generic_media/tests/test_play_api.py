import pytest
from generic_media.play_api import play
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

class TestPlayAPI:
    def test_play_by_search(self):
        """
        Test that the play function can search for a media item and play it.
        """
        result = play("Bohemian Rhapsody", "TRACK")
        assert len(result) == 1
        assert result[0]["media_item_metadata"]["entity_title"] == "Bohemian Rhapsody"
        assert result[0]["media_item_metadata"]["container_title"] == "album1"
        assert len(DB["recently_played"]) == 1
        assert DB["recently_played"][0]["uri"] == result[0]["uri"]

    def test_play_by_uri(self):
        """
        Test that the play function can play a media item by its URI.
        """
        result = play("applemusic:track:track1", "TRACK")
        assert len(result) == 1
        assert result[0]["media_item_metadata"]["entity_title"] == "Bohemian Rhapsody"
        assert len(DB["recently_played"]) == 1
        assert DB["recently_played"][0]["uri"] == result[0]["uri"]

    def test_play_with_podcast_uri(self):
        """
        Test playing a podcast episode by URI to cover specific logic for podcasts.
        """
        podcast_show = DB['podcasts'][0]
        episode = podcast_show['episodes'][0]
        uri = f"{episode['provider']}:podcast_episode:{episode['id']}"
        
        result = play(query=uri, intent_type="PODCAST_EPISODE")
        assert len(result) == 1
        assert result[0]['uri'] == uri
        assert result[0]['media_item_metadata']['container_title'] == podcast_show['id']

    def test_play_not_found(self):
        """
        Test that the play function returns an empty list when no media item is found.
        """
        result = play("Non Existent Song", "TRACK")
        assert len(result) == 0
        assert len(DB["recently_played"]) == 0

    def test_play_empty_query(self):
        """
        Test that the play function raises a ValueError for an empty query.
        """
        with pytest.raises(ValueError, match="Query cannot be empty."):
            play("", "TRACK")

    def test_play_invalid_intent_type(self):
        """
        Test that the play function raises a ValueError for an invalid intent_type.
        """
        with pytest.raises(ValueError, match="Invalid intent_type: INVALID"):
            play("test", "INVALID")

    def test_play_with_filtering_type(self):
        """
        Test that the play function works correctly with a filtering_type.
        """
        result = play("A Night at the Opera", "ALBUM", filtering_type="ALBUM")
        assert len(result) == 1
        assert result[0]["media_item_metadata"]["entity_title"] == "A Night at the Opera"
        assert result[0]["media_item_metadata"]["container_title"] is None
        assert len(DB["recently_played"]) == 1
        assert DB["recently_played"][0]["uri"] == "applemusic:album:album1"

    def test_play_invalid_filtering_type(self):
        """
        Test that the play function raises a ValueError for an invalid filtering_type.
        """
        with pytest.raises(ValueError, match="Invalid filtering_type: INVALID_FILTER"):
            play(query="Bohemian Rhapsody", intent_type="TRACK", filtering_type="INVALID_FILTER")

    def test_play_artist(self):
        """
        Test playing an artist.
        """
        result = play("Queen", "ARTIST")
        assert len(result) == 1
        assert result[0]["media_item_metadata"]["entity_title"] == "Queen"
        assert len(DB["recently_played"]) == 1
        assert DB["recently_played"][0]["uri"] == result[0]["uri"]

    def test_play_liked_song(self):
        """
        Test playing a liked song.
        """
        result = play("Bohemian Rhapsody", "LIKED_SONGS")
        assert len(result) == 1
        assert result[0]["media_item_metadata"]["entity_title"] == "Bohemian Rhapsody"
        assert len(DB["recently_played"]) == 1
        assert DB["recently_played"][0]["uri"] == result[0]["uri"]

    def test_play_personal_playlist(self):
        """
        Test playing a personal playlist.
        """
        result = play("My Rock Favorites", "PERSONAL_PLAYLIST")
        assert len(result) == 1
        assert result[0]["media_item_metadata"]["entity_title"] == "My Rock Favorites"
        assert len(DB["recently_played"]) == 1
        assert DB["recently_played"][0]["uri"] == result[0]["uri"]

    def test_play_podcast_show(self):
        """
        Test playing a podcast show.
        """
        result = play("The Daily", "PODCAST_SHOW")
        assert len(result) == 1
        assert result[0]["media_item_metadata"]["entity_title"] == "The Daily"
        assert len(DB["recently_played"]) == 1
        assert DB["recently_played"][0]["uri"] == result[0]["uri"]

    def test_play_album(self):
        """
        Test playing an album.
        """
        result = play("A Night at the Opera", "ALBUM")
        assert len(result) == 1
        assert result[0]["media_item_metadata"]["entity_title"] == "A Night at the Opera"
        assert len(DB["recently_played"]) == 1
        assert DB["recently_played"][0]["uri"] == "applemusic:album:album1"

    def test_play_with_track_filtering(self):
        """
        Test playing a track with track filtering.
        """
        result = play("Bohemian Rhapsody", "TRACK", "TRACK")
        assert len(result) == 1
        assert result[0]["media_item_metadata"]["entity_title"] == "Bohemian Rhapsody"
        assert len(DB["recently_played"]) == 1
        assert DB["recently_played"][0]["uri"] == "applemusic:track:track1"

    def test_play_with_album_filtering(self):
        """
        Test playing a track with album filtering.
        """
        result = play("A Night at the Opera", "TRACK", "ALBUM")
        assert len(result) >= 1
        assert result[0]["media_item_metadata"]["entity_title"] == "A Night at the Opera"
        assert len(DB["recently_played"]) == 1
        assert DB["recently_played"][0]["uri"] in ["applemusic:album:album1", "spotify:album:11628"]
