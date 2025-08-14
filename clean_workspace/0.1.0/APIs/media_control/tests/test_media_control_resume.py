import unittest
from common_utils.base_case import BaseTestCaseWithErrorHandler
from ..SimulationEngine.db import DB, reset_db
from ..SimulationEngine.models import MediaPlayer, MediaItem, PlaybackState, MediaType, ActionSummary
from ..SimulationEngine.custom_errors import NoMediaPlayerError, InvalidPlaybackStateError
from .. import resume

class TestResume(BaseTestCaseWithErrorHandler):
    def setUp(self):
        reset_db()
        self.media_item = MediaItem(
            id="track1", title="Song", artist="Artist", album="Album",
            duration_seconds=200, current_position_seconds=50,
            media_type=MediaType.TRACK, app_name="Spotify"
        )
        self.player = MediaPlayer(
            app_name="Spotify", current_media=self.media_item,
            playback_state=PlaybackState.PAUSED, playlist=[self.media_item], current_playlist_index=0
        )
        DB["media_players"] = {"Spotify": self.player.model_dump()}
        DB["active_media_player"] = "Spotify"

    def tearDown(self):
        reset_db()

    def test_resume_success(self):
        result = resume()
        self.assertIsInstance(result, dict)
        self.assertEqual(result["result"], "Success")
        self.assertEqual(result["app_name"], "Spotify")
        self.assertEqual(result["title"], "Song")

    def test_resume_no_media(self):
        self.player.current_media = None
        DB["media_players"]["Spotify"] = self.player.model_dump()
        self.assert_error_behavior(
            lambda: resume(),
            InvalidPlaybackStateError,
            "Cannot resume media in app: Spotify. Media must be paused."
        )

    def test_resume_no_active_player(self):
        DB["active_media_player"] = None
        self.assert_error_behavior(
            lambda: resume(),
            NoMediaPlayerError,
            "No active media player found"
        )

    def test_resume_no_player_found(self):
        DB["active_media_player"] = "NonExistentApp"
        self.assert_error_behavior(
            lambda: resume(),
            NoMediaPlayerError,
            "No active media player found"
        )

    def test_resume_playing_media(self):
        self.player.playback_state = PlaybackState.PLAYING
        DB["media_players"]["Spotify"] = self.player.model_dump()
        self.assert_error_behavior(
            lambda: resume(),
            InvalidPlaybackStateError,
            "Cannot resume media in app: Spotify. Media must be paused."
        )

    def test_resume_stopped_media(self):
        self.player.playback_state = PlaybackState.STOPPED
        DB["media_players"]["Spotify"] = self.player.model_dump()
        self.assert_error_behavior(
            lambda: resume(),
            InvalidPlaybackStateError,
            "Cannot resume media in app: Spotify. Media must be paused."
        )

if __name__ == "__main__":
    unittest.main() 