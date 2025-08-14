"""
Comprehensive test suite for change_playback_state function
"""

import unittest
from unittest.mock import patch
from common_utils.base_case import BaseTestCaseWithErrorHandler
from ..SimulationEngine.db import DB, reset_db
from ..SimulationEngine.models import (
    MediaPlayer, MediaItem, PlaybackState, MediaType, MediaRating,
    PlaybackTargetState, ActionSummary
)
from ..SimulationEngine.custom_errors import ValidationError, NoMediaPlayerError, NoMediaPlayingError, InvalidPlaybackStateError, NoMediaItemError
from .. import change_playback_state
import uuid


class TestChangePlaybackState(BaseTestCaseWithErrorHandler):
    
    def setUp(self):
        """Set up test database with sample media players"""
        reset_db()
        
        # Create test media items
        self.test_media_item = MediaItem(
            id="test_track_001",
            title="Test Song",
            artist="Test Artist",
            album="Test Album",
            duration_seconds=180,
            current_position_seconds=60,
            media_type=MediaType.TRACK,
            rating=None,
            app_name="Spotify"
        )
        
        # Create test media player as dictionary
        self.test_player = {
            "app_name": "Spotify",
            "current_media": self.test_media_item.model_dump(),
            "playback_state": PlaybackState.PLAYING.value,
            "playlist": [self.test_media_item.model_dump()],
            "current_playlist_index": 0
        }
        
        # Add to database
        DB["media_players"] = {
            "Spotify": self.test_player
        }
    
    def tearDown(self):
        """Clean up after tests"""
        reset_db()
    
    def test_pause_media_success(self):
        """Test successfully pausing media"""
        result = change_playback_state("PAUSE", "Spotify")
        
        # Should return dict
        self.assertIsInstance(result, dict)
        self.assertEqual(result["result"], "Success")
        self.assertEqual(result["title"], "Test Song")
        self.assertEqual(result["app_name"], "Spotify")
        self.assertEqual(result["media_type"], MediaType.TRACK)
        
        # Check that player state was updated
        updated_player_data = DB["media_players"]["Spotify"]
        self.assertEqual(updated_player_data["playback_state"], PlaybackState.PAUSED.value)
    
    def test_resume_media_success(self):
        """Test successfully resuming media"""
        # First pause the media
        self.test_player["playback_state"] = PlaybackState.PAUSED.value
        DB["media_players"]["Spotify"] = self.test_player
        
        result = change_playback_state("RESUME", "Spotify")
        
        # Should return dict
        self.assertIsInstance(result, dict)
        self.assertEqual(result["result"], "Success")
        self.assertEqual(result["title"], "Test Song")
        self.assertEqual(result["app_name"], "Spotify")
        self.assertEqual(result["media_type"], MediaType.TRACK)
        
        # Check that player state was updated
        updated_player_data = DB["media_players"]["Spotify"]
        self.assertEqual(updated_player_data["playback_state"], PlaybackState.PLAYING.value)
    
    def test_stop_media_success(self):
        """Test successfully stopping media"""
        result = change_playback_state("STOP", "Spotify")
        
        # Should return dict
        self.assertIsInstance(result, dict)
        self.assertEqual(result["result"], "Success")
        self.assertEqual(result["title"], "Test Song")
        self.assertEqual(result["app_name"], "Spotify")
        self.assertEqual(result["media_type"], MediaType.TRACK)
        
        # Check that player state was updated
        updated_player_data = DB["media_players"]["Spotify"]
        self.assertEqual(updated_player_data["playback_state"], PlaybackState.STOPPED.value)
    
    def test_no_media_playing(self):
        """Test when no media is playing"""
        # Remove current media
        self.test_player["current_media"] = None
        self.test_player["playback_state"] = PlaybackState.STOPPED.value
        DB["media_players"]["Spotify"] = self.test_player
        with self.assertRaises(NoMediaItemError):
            change_playback_state("PAUSE", "Spotify")
    
    def test_no_media_player_found(self):
        """Test when no media player is found"""
        with self.assertRaises(NoMediaPlayerError):
            change_playback_state("PAUSE", "NonExistentApp")
    
    def test_no_app_name_specified(self):
        """Test when no app_name is specified"""
        with self.assertRaises(NoMediaPlayerError):
            change_playback_state("PAUSE")
    
    def test_invalid_target_state(self):
        """Test with invalid target state"""
        self.assert_error_behavior(
            lambda: change_playback_state("INVALID_STATE", "Spotify"),
            ValidationError,
            "target_state must be one of ['STOP', 'PAUSE', 'RESUME'], got 'INVALID_STATE'"
        )
    
    def test_empty_target_state(self):
        """Test with empty target state"""
        self.assert_error_behavior(
            lambda: change_playback_state("", "Spotify"),
            ValidationError,
            "target_state cannot be an empty string"
        )
    
    def test_target_state_not_string(self):
        """Test with non-string target state"""
        self.assert_error_behavior(
            lambda: change_playback_state(123, "Spotify"),
            ValidationError,
            "target_state must be a string, got int"
        )
    
    def test_app_name_not_string(self):
        """Test with non-string app_name"""
        self.assert_error_behavior(
            lambda: change_playback_state("PAUSE", 123),
            ValidationError,
            "app_name must be a string, got int"
        )
    
    def test_app_name_empty_string(self):
        """Test with empty app_name"""
        self.assert_error_behavior(
            lambda: change_playback_state("PAUSE", ""),
            ValidationError,
            "app_name cannot be an empty string"
        )
    
    def test_pause_already_paused_media(self):
        """Test pausing already paused media"""
        # Set media to paused state
        self.test_player["playback_state"] = PlaybackState.PAUSED.value
        DB["media_players"]["Spotify"] = self.test_player
        with self.assertRaises(InvalidPlaybackStateError):
            change_playback_state("PAUSE", "Spotify")
    
    def test_resume_playing_media(self):
        """Test resuming already playing media"""
        with self.assertRaises(InvalidPlaybackStateError):
            change_playback_state("RESUME", "Spotify")
    
    def test_stop_stopped_media(self):
        """Test stopping already stopped media"""
        # Set media to stopped state
        self.test_player["playback_state"] = PlaybackState.STOPPED.value
        DB["media_players"]["Spotify"] = self.test_player
        with self.assertRaises(InvalidPlaybackStateError):
            change_playback_state("STOP", "Spotify")
    
    def test_multiple_media_players(self):
        """Test with multiple media players"""
        # Add another media player
        second_media_item = MediaItem(
            id="test_video_001",
            title="Test Video",
            artist="Test Creator",
            album=None,
            duration_seconds=300,
            current_position_seconds=120,
            media_type=MediaType.VIDEO,
            rating=None,
            app_name="YouTube Music"
        )
        
        second_player = {
            "app_name": "YouTube Music",
            "current_media": second_media_item.model_dump(),
            "playback_state": PlaybackState.PLAYING.value,
            "playlist": [],
            "current_playlist_index": 0
        }
        
        DB["media_players"]["YouTube Music"] = second_player
        
        # Test with specific app name
        result = change_playback_state("PAUSE", "YouTube Music")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["result"], "Success")
        self.assertEqual(result["title"], "Test Video")
        self.assertEqual(result["app_name"], "YouTube Music")
    
    def test_case_insensitive_target_state(self):
        """Test that target state is case sensitive"""
        self.assert_error_behavior(
            lambda: change_playback_state("pause", "Spotify"),
            ValidationError,
            "target_state must be one of ['STOP', 'PAUSE', 'RESUME'], got 'pause'"
        )
    
    def test_none_values_valid(self):
        """Test that None values are handled correctly"""
        with self.assertRaises(NoMediaPlayerError):
            change_playback_state("PAUSE", None)
    
    def test_validation_with_boolean_type(self):
        """Test validation with boolean type"""
        self.assert_error_behavior(
            lambda: change_playback_state(True, "Spotify"),
            ValidationError,
            "target_state must be a string, got bool"
        )
    
    def test_validation_with_list_type(self):
        """Test validation with list type"""
        self.assert_error_behavior(
            lambda: change_playback_state(["PAUSE"], "Spotify"),
            ValidationError,
            "target_state must be a string, got list"
        )
    
    def test_validation_with_dict_type(self):
        """Test validation with dict type"""
        self.assert_error_behavior(
            lambda: change_playback_state({"state": "PAUSE"}, "Spotify"),
            ValidationError,
            "target_state must be a string, got dict"
        )


if __name__ == "__main__":
    unittest.main()
