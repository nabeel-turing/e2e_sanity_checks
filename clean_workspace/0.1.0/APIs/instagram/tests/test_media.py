# instagram/tests/test_media.py

import unittest
import datetime
from instagram.SimulationEngine.custom_erros import UserNotFoundError
from instagram import User, Media
import instagram as InstagramAPI
from .common import reset_db
from common_utils.base_case import BaseTestCaseWithErrorHandler


class TestMediaAPI(BaseTestCaseWithErrorHandler):
    """Test suite for the Instagram API Media functionality."""

    def setUp(self):
        """
        Set up method called before each test.
        Resets the global DB to ensure a clean state for every test.
        """
        reset_db()

    def test_create_media(self):
        """Test creating media for an existing user."""
        user_id = "201"
        User.create_user(user_id, "Media Maker", "mediamaker")
        media = Media.create_media(
            user_id, "http://example.com/image1.jpg", caption="My first pic"
        )
        self.assertNotIn("error", media)
        self.assertEqual(media["user_id"], user_id)
        self.assertEqual(media["caption"], "My first pic")
        self.assertIn(media["id"], InstagramAPI.DB["media"])

    def test_media_timestamp(self):
        """Test that media creation includes a timestamp field."""
        user_id = "201"
        User.create_user(user_id, "Media Maker", "mediamaker")

        # Create media and check timestamp
        media = Media.create_media(user_id, "http://example.com/image1.jpg")
        self.assertIn("timestamp", media)
        self.assertIsInstance(media["timestamp"], str)

        # Verify timestamp is in ISO format
        try:
            # This will raise ValueError if not in ISO format
            datetime.datetime.fromisoformat(media["timestamp"])
        except ValueError:
            self.fail("Timestamp is not in ISO format")

        # Verify timestamp is stored in DB
        self.assertIn("timestamp", InstagramAPI.DB["media"][media["id"]])
        self.assertEqual(
            InstagramAPI.DB["media"][media["id"]]["timestamp"], media["timestamp"]
        )

        # Verify timestamp is included in list_media results
        media_list = Media.list_media()
        media_from_list = next(m for m in media_list if m["id"] == media["id"])
        self.assertIn("timestamp", media_from_list)
        self.assertEqual(media_from_list["timestamp"], media["timestamp"])

    def test_create_media_no_user(self):
        """Test creating media for a non-existent user."""
        self.assert_error_behavior(
            func_to_call=Media.create_media,
            expected_exception_type=UserNotFoundError,
            expected_message="User with ID '999' does not exist.",
            user_id="999",
            image_url="http://example.com/image2.jpg"
        )

    def test_list_media(self):
        """Test listing all media."""
        user_id = "202"
        User.create_user(user_id, "Pic Poster", "picposter")
        Media.create_media(user_id, "url1")
        Media.create_media(user_id, "url2", caption="Second")
        Media.create_media(user_id, "url3")
        media_list = Media.list_media()
        self.assertEqual(len(media_list), 3)
        media_ids = {m["id"] for m in media_list}
        self.assertEqual(len(media_ids), 3)  # Ensure unique IDs

    def test_delete_media(self):
        """Test deleting media."""
        user_id = "203"
        User.create_user(user_id, "Deleter", "deleter")
        media = Media.create_media(user_id, "url_to_delete")
        media_id = media["id"]
        self.assertIn(media_id, InstagramAPI.DB["media"])
        result = Media.delete_media(media_id)
        self.assertTrue(result.get("success"))
        self.assertNotIn(media_id, InstagramAPI.DB["media"])
        # Test deleting non-existent media
        error_result = Media.delete_media("media_999")
        self.assertIn("error", error_result)


if __name__ == "__main__":
    unittest.main()
