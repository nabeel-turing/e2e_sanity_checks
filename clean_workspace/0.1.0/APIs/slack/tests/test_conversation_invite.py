from unittest.mock import patch

from .. import invite_to_conversation

from ..SimulationEngine.custom_errors import InvalidUserError, ChannelNotFoundError
from common_utils.base_case import BaseTestCaseWithErrorHandler

DB = {}

class TestConversationsInvite(BaseTestCaseWithErrorHandler):

    def setUp(self):
        """Reset the test DB before each test."""
        global DB
        # Reset DB to a known state for each test
        DB = {
            "users": {"user1", "user2", "user3", "valid_user"},
            "channels": {
                "channel1": {
                    "conversations": {
                        "members": ["user1"]
                    }
                },
                "empty_channel": {},
                "channel_no_conv": {}
            }
        }

    @patch("slack.Conversations.DB", new_callable=lambda: DB)
    def test_valid_input_new_users(self, mock_db):
        """Test inviting valid users not already in the channel."""
        result = invite_to_conversation(channel="channel1", users="user2,user3")
        self.assertTrue(result["ok"])
        self.assertEqual(result["channel"], "channel1")
        self.assertCountEqual(result["invited"], ["user2", "user3"])  # Order doesn't matter
        self.assertNotIn("error", result)
        self.assertCountEqual(DB["channels"]["channel1"]["conversations"]["members"], ["user1", "user2", "user3"])

    @patch("slack.Conversations.DB", new_callable=lambda: DB)
    def test_valid_input_some_existing_users(self, mock_db):
        """Test inviting a mix of existing and new valid users."""
        result = invite_to_conversation(channel="channel1", users="user1,user2")
        self.assertTrue(result["ok"])
        self.assertEqual(result["channel"], "channel1")
        self.assertCountEqual(result["invited"], ["user2"])  # Only user2 was newly added
        self.assertNotIn("error", result)
        self.assertCountEqual(DB["channels"]["channel1"]["conversations"]["members"], ["user1", "user2"])

    @patch("slack.Conversations.DB", new_callable=lambda: DB)
    def test_valid_input_all_existing_users(self, mock_db):
        """Test inviting only users already in the channel."""
        result = invite_to_conversation(channel="channel1", users="user1")
        self.assertTrue(result["ok"])
        self.assertEqual(result["channel"], "channel1")
        self.assertCountEqual(result["invited"], [])  # No users were newly added
        self.assertNotIn("error", result)
        self.assertCountEqual(DB["channels"]["channel1"]["conversations"]["members"], ["user1"])

    @patch("slack.Conversations.DB", new_callable=lambda: DB)
    def test_valid_input_force_false_with_invalid_users(self, mock_db):
        """Test invite fails (returns error) with invalid users when force=False."""
        self.assert_error_behavior(
            func_to_call=invite_to_conversation,
            expected_exception_type=InvalidUserError,
            expected_message="invalid user found.",
            channel="channel1", users="user2,invalid_user", force=False
        )

    @patch("slack.Conversations.DB", new_callable=lambda: DB)
    def test_valid_input_force_true_with_invalid_users(self, mock_db):
        """Test invite succeeds for valid users with invalid users when force=True."""
        result = invite_to_conversation(channel="channel1", users="user2,invalid_user,user3", force=True)
        self.assertTrue(result["ok"])
        self.assertEqual(result["channel"], "channel1")
        self.assertCountEqual(result["invited"], ["user2", "user3"])  # user2 and user3 are valid and added
        self.assertCountEqual(result["invalid_users"], ["invalid_user"])  # user2 and user3 are valid and added
        self.assertCountEqual(DB["channels"]["channel1"]["conversations"]["members"], ["user1", "user2", "user3"])


    @patch("slack.Conversations.DB", new_callable=lambda: DB)
    def test_channel_not_found(self, mock_db):
        """Test inviting to a non-existent channel."""
        self.assert_error_behavior(
            func_to_call=invite_to_conversation,
            expected_exception_type=ChannelNotFoundError,
            expected_message="channel not found.",
            channel="nonexistent_channel",
            users="user1"
        )

    @patch("slack.Conversations.DB", new_callable=lambda: DB)
    def test_channel_exists_but_no_members_key(self, mock_db):
        """Test inviting to a channel that exists with 'conversations' but lacks 'members'."""
        DB["channels"]["channel_no_members"] = {"conversations": {}}  # Add channel for test case
        result = invite_to_conversation(channel="channel_no_members", users="user3")
        self.assertTrue(result["ok"])
        self.assertEqual(result["channel"], "channel_no_members")
        self.assertCountEqual(result["invited"], ["user3"])
        self.assertIn("members", DB["channels"]["channel_no_members"]["conversations"])
        self.assertCountEqual(DB["channels"]["channel_no_members"]["conversations"]["members"], ["user3"])

    # --- Input Validation Tests ---

    def test_invalid_channel_type(self):
        """Test that non-string channel raises TypeError."""
        self.assert_error_behavior(
            func_to_call=invite_to_conversation,
            expected_exception_type=TypeError,
            expected_message="Argument 'channel' must be a string, but got int",
            channel=123,
            users="user1"
        )

    def test_empty_channel_string(self):
        """Test that an empty string channel raises ValueError."""
        self.assert_error_behavior(
            func_to_call=invite_to_conversation,
            expected_exception_type=ValueError,
            expected_message="Argument 'channel' cannot be an empty string.",
            channel="",
            users="user1"
        )

    def test_invalid_users_type(self):
        """Test that non-string users raises TypeError."""
        self.assert_error_behavior(
            func_to_call=invite_to_conversation,
            expected_exception_type=TypeError,
            expected_message="Argument 'users' must be a string, but got list",
            channel="channel1",
            users=["user1"]
        )

    def test_empty_users_string(self):
        """Test that an empty string users raises ValueError."""
        self.assert_error_behavior(
            func_to_call=invite_to_conversation,
            expected_exception_type=ValueError,
            expected_message="Argument 'users' cannot be an empty string.",
            channel="channel1",
            users=""
        )

    def test_invalid_force_type(self):
        """Test that non-boolean force raises TypeError."""
        self.assert_error_behavior(
            func_to_call=invite_to_conversation,
            expected_exception_type=TypeError,
            expected_message="Argument 'force' must be a boolean, but got str",
            channel="channel1",
            users="user1",
            force="not-a-bool"
        )

    def test_force_default_value(self):
        """Test that force defaults to False and invalid users cause failure."""
        self.assert_error_behavior(
            func_to_call=invite_to_conversation,
            expected_exception_type=InvalidUserError,
            expected_message="invalid user found.",
            channel="channel1", users="user2,invalid_user"
        )

    @patch("slack.Conversations.DB", new_callable=lambda: DB)
    def test_users_with_whitespace(self, mock_db):
        """Test that user IDs with surrounding whitespace are handled correctly."""
        result = invite_to_conversation(channel="channel1", users=" user2 , user3 ")
        self.assertTrue(result["ok"])
        self.assertEqual(result["channel"], "channel1")
        self.assertCountEqual(result["invited"], ["user2", "user3"])
        self.assertCountEqual(DB["channels"]["channel1"]["conversations"]["members"], ["user1", "user2", "user3"])
