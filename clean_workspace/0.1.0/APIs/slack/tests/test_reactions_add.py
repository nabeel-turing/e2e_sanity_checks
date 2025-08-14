from unittest.mock import patch

from .. import add_reaction_to_message
from common_utils.base_case import BaseTestCaseWithErrorHandler

DB = {}  # Reset DB for tests


class TestReactionsAdd(BaseTestCaseWithErrorHandler):

    def setUp(self):
        """Reset test state before each test."""
        # Reset a minimal DB structure needed for a basic success case check
        # Note: This setup is minimal and only supports the happy path test case passing the validation stage.
        # It doesn't fully represent real-world DB interactions.
        global DB
        DB = {
            "channels": {
                "C123": {
                    "messages": [
                        {"ts": "12345.67890", "text": "Hello", "reactions": []}
                    ]
                }
            }
        }

    @patch("slack.Reactions.DB", new_callable=lambda: DB)
    def test_valid_input_passes_validation(self, mock_db):
        """Test that valid input types pass the initial validation."""
        # This test mainly verifies that no TypeError or ValueError is raised.
        # It might still fail later due to DB logic or return an error dictionary,
        # but it should pass the validation block added at the start.
        try:
            result = add_reaction_to_message(
                user_id="U1",
                channel_id="C123",
                name="thumbsup",
                message_ts="12345.67890"
            )
            # Check the expected return type (dict) after passing validation and executing logic
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get("ok"))  # Expect success in this basic case
            self.assertIn("message", result)
            self.assertIsInstance(result["message"], dict)
        except (TypeError, ValueError) as e:
            self.fail(f"Validation failed unexpectedly for valid input: {e}")
        except Exception as e:
            # Catch other potential errors from core logic if DB setup is insufficient
            self.fail(f"Core logic failed unexpectedly: {e}")

    # --- Type Validation Tests ---

    @patch("slack.Reactions.DB", new_callable=lambda: DB)
    def test_invalid_user_id_type(self, mock_db):
        """Test that non-string user_id raises TypeError."""
        self.assert_error_behavior(
            func_to_call=add_reaction_to_message,
            expected_exception_type=TypeError,
            expected_message="user_id must be a string, got int",
            user_id=123,
            channel_id="C123",
            name="thumbsup",
            message_ts="12345.67890"
        )

    @patch("slack.Reactions.DB", new_callable=lambda: DB)
    def test_invalid_channel_id_type(self, mock_db):
        """Test that non-string channel_id raises TypeError."""
        self.assert_error_behavior(
            func_to_call=add_reaction_to_message,
            expected_exception_type=TypeError,
            expected_message="channel_id must be a string, got NoneType",
            user_id="U1",
            channel_id=None,
            name="thumbsup",
            message_ts="12345.67890"
        )

    @patch("slack.Reactions.DB", new_callable=lambda: DB)
    def test_invalid_name_type(self, mock_db):
        """Test that non-string name raises TypeError."""
        self.assert_error_behavior(
            func_to_call=add_reaction_to_message,
            expected_exception_type=TypeError,
            expected_message="name must be a string, got list",
            user_id="U1",
            channel_id="C123",
            name=["not", "a", "string"],
            message_ts="12345.67890"
        )

    @patch("slack.Reactions.DB", new_callable=lambda: DB)
    def test_invalid_message_ts_type(self, mock_db):
        """Test that non-string message_ts raises TypeError."""
        self.assert_error_behavior(
            func_to_call=add_reaction_to_message,
            expected_exception_type=TypeError,
            expected_message="message_ts must be a string, got float",
            user_id="U1",
            channel_id="C123",
            name="thumbsup",
            message_ts=12345.67890
        )

    # --- Value Validation Tests (Empty Strings) ---
    @patch("slack.Reactions.DB", new_callable=lambda: DB)
    def test_empty_user_id(self, mock_db):
        """Test that empty string user_id raises ValueError."""
        self.assert_error_behavior(
            func_to_call=add_reaction_to_message,
            expected_exception_type=ValueError,
            expected_message="user_id cannot be empty",
            user_id="",
            channel_id="C123",
            name="thumbsup",
            message_ts="12345.67890"
        )

    @patch("slack.Reactions.DB", new_callable=lambda: DB)
    def test_empty_channel_id(self, mock_db):
        """Test that empty string channel_id raises ValueError."""
        self.assert_error_behavior(
            func_to_call=add_reaction_to_message,
            expected_exception_type=ValueError,
            expected_message="channel_id cannot be empty",
            user_id="U1",
            channel_id="",
            name="thumbsup",
            message_ts="12345.67890"
        )

    @patch("slack.Reactions.DB", new_callable=lambda: DB)
    def test_empty_name(self, mock_db):
        """Test that empty string name raises ValueError."""
        self.assert_error_behavior(
            func_to_call=add_reaction_to_message,
            expected_exception_type=ValueError,
            expected_message="name cannot be empty",
            user_id="U1",
            channel_id="C123",
            name="",
            message_ts="12345.67890"
        )

    @patch("slack.Reactions.DB", new_callable=lambda: DB)
    def test_empty_message_ts(self, mock_db):
        """Test that empty string message_ts raises ValueError."""
        self.assert_error_behavior(
            func_to_call=add_reaction_to_message,
            expected_exception_type=ValueError,
            expected_message="message_ts cannot be empty",
            user_id="U1",
            channel_id="C123",
            name="thumbsup",
            message_ts=""
        )
