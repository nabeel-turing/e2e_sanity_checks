import unittest
from unittest.mock import patch
from common_utils.base_case import BaseTestCaseWithErrorHandler
from ..SimulationEngine.db import DB, reset_db
from ..SimulationEngine.models import MediaPlayer, MediaItem, PlaybackState, MediaType, ActionSummary
from ..SimulationEngine.custom_errors import ValidationError, NoMediaPlayerError, NoMediaPlayingError, InvalidPlaybackStateError
from .. import stop

class TestStop(BaseTestCaseWithErrorHandler):
    def setUp(self):
        reset_db()
        self.media_item = MediaItem(
            id="track1", title="Song", artist="Artist", album="Album",
            duration_seconds=200, current_position_seconds=50,
            media_type=MediaType.TRACK, app_name="Spotify"
        )
        self.player = MediaPlayer(
            app_name="Spotify", current_media=self.media_item,
            playback_state=PlaybackState.PLAYING, playlist=[self.media_item], current_playlist_index=0
        )
        DB["media_players"] = {"Spotify": self.player.model_dump()}
        DB["active_media_player"] = "Spotify"

    def tearDown(self):
        reset_db()

    def test_stop_success(self):
        result = stop()
        self.assertIsInstance(result, dict)
        self.assertEqual(result["result"], "Success")
        self.assertEqual(result["app_name"], "Spotify")
        self.assertEqual(result["title"], "Song")

    def test_stop_no_media(self):
        self.player.current_media = None
        DB["media_players"]["Spotify"] = self.player.model_dump()
        self.assert_error_behavior(
            lambda: stop(),
            NoMediaPlayingError,
            "No media currently playing in the active app"
        )

    def test_stop_no_player_found(self):
        DB["active_media_player"] = "NonExistentApp"
        self.assert_error_behavior(
            lambda: stop(),
            NoMediaPlayerError,
            "No active media player found"
        )

    def test_stop_already_stopped(self):
        self.player.playback_state = PlaybackState.STOPPED
        DB["media_players"]["Spotify"] = self.player.model_dump()
        self.assert_error_behavior(
            lambda: stop(),
            NoMediaPlayingError,
            "No media currently playing in the active app"
        )

    def test_stop_paused_media(self):
        self.player.playback_state = PlaybackState.PAUSED
        DB["media_players"]["Spotify"] = self.player.model_dump()
        result = stop()
        self.assertIsInstance(result, dict)
        self.assertEqual(result["result"], "Success")

    def test_stop_none_app_name(self):
        DB["active_media_player"] = None
        self.assert_error_behavior(
            lambda: stop(),
            NoMediaPlayerError,
            "No active media player found"
        )

    @patch('media_control.SimulationEngine.utils.validate_media_playing')
    def test_stop_media_already_stopped_line_142(self, mock_validate):
        """Test line 142: InvalidPlaybackStateError when media is already stopped"""
        # Set up player with stopped state but current media
        self.player.playback_state = PlaybackState.STOPPED
        DB["media_players"]["Spotify"] = self.player.model_dump()
        
        # Mock validate_media_playing to return True so we can reach line 142
        mock_validate.return_value = True
        
        self.assert_error_behavior(
            lambda: stop(),
            InvalidPlaybackStateError,
            "Media is already stopped"
        )

if __name__ == "__main__":
    unittest.main() 