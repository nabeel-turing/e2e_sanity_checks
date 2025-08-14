import unittest
from common_utils.base_case import BaseTestCaseWithErrorHandler
from ..SimulationEngine.db import DB, reset_db
from ..SimulationEngine.models import MediaPlayer, MediaItem, PlaybackState, MediaType, MediaRating, ActionSummary
from ..SimulationEngine.custom_errors import ValidationError, NoMediaPlayerError, NoMediaItemError
from .. import like

class TestLike(BaseTestCaseWithErrorHandler):
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

    def test_like_success(self):
        result = like()
        self.assertIsInstance(result, dict)
        self.assertEqual(result["result"], "Success")
        self.assertEqual(result["app_name"], "Spotify")
        self.assertEqual(result["title"], "Song")
        self.assertEqual(DB["media_players"]["Spotify"]["current_media"]["rating"], MediaRating.POSITIVE.value)

    def test_like_no_media(self):
        self.player.current_media = None
        DB["media_players"]["Spotify"] = self.player.model_dump()
        self.assert_error_behavior(
            lambda: like(),
            NoMediaItemError,
            "No media item loaded in app: Spotify"
        )

    def test_like_already_liked(self):
        self.player.current_media.rating = MediaRating.POSITIVE
        DB["media_players"]["Spotify"] = self.player.model_dump()
        result = like()
        self.assertIsInstance(result, dict)
        self.assertEqual(result["result"], "Success")
        self.assertEqual(DB["media_players"]["Spotify"]["current_media"]["rating"], MediaRating.POSITIVE.value)

    def test_like_already_disliked(self):
        self.player.current_media.rating = MediaRating.NEGATIVE
        DB["media_players"]["Spotify"] = self.player.model_dump()
        result = like()
        self.assertIsInstance(result, dict)
        self.assertEqual(result["result"], "Success")
        self.assertEqual(DB["media_players"]["Spotify"]["current_media"]["rating"], MediaRating.POSITIVE.value)

    def test_like_no_player_found(self):
        DB["active_media_player"] = "NonExistentApp"
        self.assert_error_behavior(
            lambda: like(),
            NoMediaPlayerError,
            "No active media player found"
        )

if __name__ == "__main__":
    unittest.main() 