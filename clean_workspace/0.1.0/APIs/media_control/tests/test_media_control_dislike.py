import unittest
from common_utils.base_case import BaseTestCaseWithErrorHandler
from ..SimulationEngine.db import DB, reset_db
from ..SimulationEngine.models import MediaPlayer, MediaItem, PlaybackState, MediaType, MediaRating, ActionSummary
from ..SimulationEngine.custom_errors import ValidationError, NoMediaPlayerError, NoMediaItemError
from .. import dislike

class TestDislike(BaseTestCaseWithErrorHandler):
    def setUp(self):
        reset_db()
        self.media_item = MediaItem(
            id="track1", title="Song", artist="Artist", album="Album",
            duration_seconds=200, current_position_seconds=50,
            media_type=MediaType.TRACK, rating=None, app_name="Spotify"
        )
        self.player = MediaPlayer(
            app_name="Spotify", current_media=self.media_item,
            playback_state=PlaybackState.PLAYING, playlist=[self.media_item], current_playlist_index=0
        )
        DB["media_players"] = {"Spotify": self.player.model_dump()}
        DB["active_media_player"] = "Spotify"

    def tearDown(self):
        reset_db()

    def test_dislike_success(self):
        result = dislike()
        self.assertIsInstance(result, dict)
        self.assertEqual(result["result"], "Success")
        self.assertEqual(result["app_name"], "Spotify")
        self.assertEqual(result["title"], "Song")
        self.assertEqual(DB["media_players"]["Spotify"]["current_media"]["rating"], MediaRating.NEGATIVE.value)

    def test_dislike_no_media(self):
        self.player.current_media = None
        DB["media_players"]["Spotify"] = self.player.model_dump()
        self.assert_error_behavior(
            lambda: dislike(),
            NoMediaItemError,
            "No media item loaded in app: Spotify"
        )

    def test_dislike_already_disliked(self):
        self.player.current_media.rating = MediaRating.NEGATIVE
        DB["media_players"]["Spotify"] = self.player.model_dump()
        result = dislike()
        self.assertIsInstance(result, dict)
        self.assertEqual(result["result"], "Success")
        self.assertEqual(DB["media_players"]["Spotify"]["current_media"]["rating"], MediaRating.NEGATIVE.value)

    def test_dislike_already_liked(self):
        self.player.current_media.rating = MediaRating.POSITIVE
        DB["media_players"]["Spotify"] = self.player.model_dump()
        result = dislike()
        self.assertIsInstance(result, dict)
        self.assertEqual(result["result"], "Success")
        self.assertEqual(DB["media_players"]["Spotify"]["current_media"]["rating"], MediaRating.NEGATIVE.value)

    def test_dislike_no_player_found(self):
        DB["active_media_player"] = "NonExistentApp"
        self.assert_error_behavior(
            lambda: dislike(),
            NoMediaPlayerError,
            "No active media player found"
        )

if __name__ == "__main__":
    unittest.main() 