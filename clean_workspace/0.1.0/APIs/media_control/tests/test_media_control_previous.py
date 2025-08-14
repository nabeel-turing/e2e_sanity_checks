import unittest
from common_utils.base_case import BaseTestCaseWithErrorHandler
from ..SimulationEngine.db import DB, reset_db
from ..SimulationEngine.models import MediaPlayer, MediaItem, PlaybackState, MediaType, ActionSummary
from ..SimulationEngine.custom_errors import NoMediaPlayerError, NoPlaylistError, InvalidPlaybackStateError
from .. import previous

class TestPrevious(BaseTestCaseWithErrorHandler):
    def setUp(self):
        reset_db()
        self.media_item1 = MediaItem(
            id="track1", title="Song1", artist="Artist1", album="Album1",
            duration_seconds=200, current_position_seconds=50,
            media_type=MediaType.TRACK, app_name="Spotify"
        )
        self.media_item2 = MediaItem(
            id="track2", title="Song2", artist="Artist2", album="Album2",
            duration_seconds=180, current_position_seconds=0,
            media_type=MediaType.TRACK, app_name="Spotify"
        )
        self.player = MediaPlayer(
            app_name="Spotify", current_media=self.media_item2,
            playback_state=PlaybackState.PLAYING, playlist=[self.media_item1, self.media_item2], current_playlist_index=1
        )
        DB["media_players"] = {"Spotify": self.player.model_dump()}
        DB["active_media_player"] = "Spotify"

    def tearDown(self):
        reset_db()

    def test_previous_success(self):
        result = previous()
        self.assertIsInstance(result, dict)
        self.assertEqual(result["result"], "Success")
        self.assertEqual(result["app_name"], "Spotify")
        self.assertEqual(result["title"], "Song1")

    def test_previous_no_playlist(self):
        self.player.playlist = []
        DB["media_players"]["Spotify"] = self.player.model_dump()
        self.assert_error_behavior(
            lambda: previous(),
            NoPlaylistError,
            "No playlist available in app: Spotify"
        )

    def test_previous_no_media(self):
        self.player.current_media = None
        DB["media_players"]["Spotify"] = self.player.model_dump()
        self.assert_error_behavior(
            lambda: previous(),
            NoPlaylistError,
            "No playlist available in app: Spotify"
        )

    def test_previous_no_active_player(self):
        DB["active_media_player"] = None
        self.assert_error_behavior(
            lambda: previous(),
            NoMediaPlayerError,
            "No active media player found"
        )

    def test_previous_no_player_found(self):
        DB["active_media_player"] = "NonExistentApp"
        self.assert_error_behavior(
            lambda: previous(),
            NoMediaPlayerError,
            "No active media player found"
        )

    def test_previous_first_track(self):
        # Set to first track
        self.player.current_playlist_index = 0
        self.player.current_media = self.media_item1
        DB["media_players"]["Spotify"] = self.player.model_dump()
        self.assert_error_behavior(
            lambda: previous(),
            InvalidPlaybackStateError,
            "Already at the first item in playlist"
        )

if __name__ == "__main__":
    unittest.main() 