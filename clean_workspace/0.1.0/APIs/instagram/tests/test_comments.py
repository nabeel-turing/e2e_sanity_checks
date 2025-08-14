# instagram/tests/test_comments.py

import unittest
import datetime
from instagram import User, Media, Comment
import instagram as InstagramAPI
from .common import reset_db
from common_utils.base_case import BaseTestCaseWithErrorHandler
from instagram.SimulationEngine.custom_erros import MediaNotFoundError


class TestCommentAPI(BaseTestCaseWithErrorHandler):
    """Test suite for the Instagram API Comment functionality."""

    def setUp(self):
        """
        Set up method called before each test.
        Resets the global DB to ensure a clean state for every test.
        """
        reset_db()

    def test_add_comment(self):
        """Test adding a comment to existing media."""
        user_id = "301"
        User.create_user(user_id, "Commenter", "commenter")
        media = Media.create_media(user_id, "url_comment")
        media_id = media["id"]
        comment = Comment.add_comment(media_id, user_id, "Nice photo!")
        self.assertNotIn("error", comment)
        self.assertEqual(comment["media_id"], media_id)
        self.assertEqual(comment["user_id"], user_id)
        self.assertEqual(comment["message"], "Nice photo!")
        self.assertIn(comment["id"], InstagramAPI.DB["comments"])

    def test_comment_timestamp(self):
        """Test that comment creation includes a timestamp field."""
        user_id = "301"
        User.create_user(user_id, "Commenter", "commenter")
        media = Media.create_media(user_id, "url_comment")
        media_id = media["id"]

        # Create comment and check timestamp
        comment = Comment.add_comment(media_id, user_id, "Nice photo!")
        self.assertIn("timestamp", comment)
        self.assertIsInstance(comment["timestamp"], str)

        # Verify timestamp is in ISO format
        try:
            # This will raise ValueError if not in ISO format
            datetime.datetime.fromisoformat(comment["timestamp"])
        except ValueError:
            self.fail("Comment timestamp is not in ISO format")

        # Verify timestamp is stored in DB
        self.assertIn("timestamp", InstagramAPI.DB["comments"][comment["id"]])
        self.assertEqual(
            InstagramAPI.DB["comments"][comment["id"]]["timestamp"],
            comment["timestamp"],
        )

        # Verify timestamp is included in list_comments results
        comments_list = Comment.list_comments(media_id)
        comment_from_list = next(c for c in comments_list if c["id"] == comment["id"])
        self.assertIn("timestamp", comment_from_list)
        self.assertEqual(comment_from_list["timestamp"], comment["timestamp"])

    def test_add_comment_no_media(self):
        """Test adding a comment to non-existent media."""
        user_id = "302"
        User.create_user(user_id, "Lost Commenter", "lostcommenter")
        with self.assertRaises(MediaNotFoundError) as context:
            Comment.add_comment("media_999", user_id, "Where is this?")
        self.assertEqual(str(context.exception), "Media does not exist.")

    def test_list_comments(self):
        """Test listing comments for specific media."""
        user_id1 = "303"
        user_id2 = "304"
        User.create_user(user_id1, "Commenter1", "c1")
        User.create_user(user_id2, "Commenter2", "c2")
        media1 = Media.create_media(user_id1, "url_c1")
        media2 = Media.create_media(user_id1, "url_c2")
        media_id1 = media1["id"]
        media_id2 = media2["id"]

        Comment.add_comment(media_id1, user_id1, "Comment 1 on media 1")
        Comment.add_comment(media_id1, user_id2, "Comment 2 on media 1")
        Comment.add_comment(media_id2, user_id1, "Comment 1 on media 2")

        comments_media1 = Comment.list_comments(media_id1)
        self.assertEqual(len(comments_media1), 2)
        comments_media2 = Comment.list_comments(media_id2)
        self.assertEqual(len(comments_media2), 1)
        comments_media_none = Comment.list_comments("media_999")
        self.assertEqual(len(comments_media_none), 0)


if __name__ == "__main__":
    unittest.main()
