from typing import Dict, Any
from unittest.mock import patch
import base64

from .. import get_conversation_history
from ..SimulationEngine.custom_errors import ChannelNotFoundError, InvalidLimitError, TimestampError, InvalidCursorValueError
from common_utils.base_case import BaseTestCaseWithErrorHandler

# This global DB is used by the function being tested.
# It's defined here for the test environment.
DB: Dict[str, Any] = {}

class TestHistoryValidation(BaseTestCaseWithErrorHandler):
    def setUp(self):
        """Setup method to create a fresh DB for each test."""
        self.test_db = {
            "channels": {
                "C123": {
                    "id": "C123",
                    "name": "test-channel",
                    "messages": [
                        {"ts": "1678886400.000000", "text": "Message 1", "user": "U123"},
                        {"ts": "1678886460.000000", "text": "Message 2", "user": "U456"},
                        {"ts": "1678886520.000000", "text": "Message 3", "user": "U123"},
                    ],
                }
            }
        }
        self.patcher = patch("slack.Conversations.DB", self.test_db)
        self.mock_db = self.patcher.start()

    def tearDown(self):
        """Clean up after each test."""
        self.patcher.stop()

    def test_valid_input_defaults(self):
        """Test with valid channel and default optional parameters."""
        result = get_conversation_history(channel="C123")
        self.assertTrue(result["ok"])
        self.assertIsInstance(result["messages"], list)
        self.assertEqual(len(result["messages"]), 3)  # Should return all messages
        self.assertFalse(result["has_more"])  # No more messages to fetch
        self.assertIsNone(result["response_metadata"]["next_cursor"])  # No next page

    def test_cursor_valid_none(self):
        """Test cursor with valid value (None)."""
        result = get_conversation_history(channel="C123", cursor=None)
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["messages"]), 3)
        self.assertFalse(result["has_more"])
        self.assertIsNone(result["response_metadata"]["next_cursor"])

    def test_cursor_not_found_in_messages(self):
        # Create a cursor for a user that doesn't exist in the messages
        cursor = base64.b64encode(b'user:U999').decode('utf-8')
        with self.assertRaises(InvalidCursorValueError):
            get_conversation_history("C123", cursor=cursor)

    def test_limit_valid_max_boundary(self):
        """Test limit with valid maximum boundary value (999)."""
        result = get_conversation_history(channel="C123", limit=999)
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["messages"]), 3)  # We only have 3 messages in our test DB
        self.assertFalse(result["has_more"])
        self.assertIsNone(result["response_metadata"]["next_cursor"])

    def test_limit_valid_min_boundary(self):
        """Test limit with valid minimum boundary value (1)."""
        result = get_conversation_history(channel="C123", limit=1)
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["messages"]), 1)
        self.assertTrue(result["has_more"])  # We have more messages
        # Verify the next_cursor is properly base64 encoded
        if result["response_metadata"]["next_cursor"]:
            try:
                decoded = base64.b64decode(result["response_metadata"]["next_cursor"]).decode('utf-8')
                self.assertTrue(decoded.startswith('user:'))
            except (base64.binascii.Error, UnicodeDecodeError):
                self.fail("next_cursor is not a valid base64-encoded string")

    def test_limit_valid_middle_value(self):
        """Test limit with valid middle value (2)."""
        result = get_conversation_history(channel="C123", limit=2)
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["messages"]), 2)
        self.assertTrue(result["has_more"])  # We have more messages
        # Verify the next_cursor is properly base64 encoded
        if result["response_metadata"]["next_cursor"]:
            try:
                decoded = base64.b64decode(result["response_metadata"]["next_cursor"]).decode('utf-8')
                self.assertTrue(decoded.startswith('user:'))
            except (base64.binascii.Error, UnicodeDecodeError):
                self.fail("next_cursor is not a valid base64-encoded string")

    def test_limit_valid_default(self):
        """Test limit with default value (100)."""
        result = get_conversation_history(channel="C123")  # Default limit is 100
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["messages"]), 3)  # We only have 3 messages
        self.assertFalse(result["has_more"])
        self.assertIsNone(result["response_metadata"]["next_cursor"])

    def test_valid_input_all_params(self):
        # Create a cursor for the first user
        cursor = base64.b64encode(b'user:U123').decode('utf-8')
        result = get_conversation_history(
            "C123",
            cursor=cursor,
            include_all_metadata=True,
            inclusive=True,
            latest="1678886600.000000",
            limit=2,
            oldest="1678886300.000000"
        )
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["messages"]), 2)
        # Verify the next_cursor is properly base64 encoded
        if result["response_metadata"]["next_cursor"]:
            try:
                decoded = base64.b64decode(result["response_metadata"]["next_cursor"]).decode('utf-8')
                self.assertTrue(decoded.startswith('user:'))
            except (base64.binascii.Error, UnicodeDecodeError):
                self.fail("next_cursor is not a valid base64-encoded string")

    def test_channel_not_found(self):
        """Test behavior when channel is not found."""
        with self.assertRaises(ChannelNotFoundError):
            get_conversation_history("non_existent_channel")

    def test_invalid_channel_type(self):
        """Test behavior when channel is not a string."""
        with self.assertRaises(TypeError):
            get_conversation_history(channel=123)

    def test_empty_channel(self):
        """Test behavior when channel is an empty string."""
        with self.assertRaises(ValueError):
            get_conversation_history(channel="")

    def test_invalid_limit_type(self):
        """Test behavior when limit is not an integer."""
        with self.assertRaises(TypeError):
            get_conversation_history("C123", limit="100")

    def test_invalid_limit_value(self):
        """Test behavior when limit is outside valid range."""
        with self.assertRaises(InvalidLimitError):
            get_conversation_history("C123", limit=0)
        with self.assertRaises(InvalidLimitError):
            get_conversation_history("C123", limit=1000)

    def test_invalid_timestamp_format(self):
        """Test behavior when timestamps are invalid."""
        with self.assertRaises(TimestampError):
            get_conversation_history("C123", oldest="invalid_timestamp")
        with self.assertRaises(TimestampError):
            get_conversation_history("C123", latest="invalid_timestamp")

    # Channel validation
    def test_channel_invalid_type_int(self):
        """Test channel with invalid type (int)."""
        self.assert_error_behavior(
            func_to_call=get_conversation_history,
            expected_exception_type=TypeError,
            expected_message="channel must be a string.",
            channel=123
        )

    def test_channel_empty_string(self):
        """Test channel with empty string."""
        self.assert_error_behavior(
            func_to_call=get_conversation_history,
            expected_exception_type=ValueError,
            expected_message="channel cannot be empty.",
            channel=""
        )

    # Cursor validation
    def test_cursor_invalid_type_int(self):
        """Test cursor with invalid type (int)."""
        self.assert_error_behavior(
            func_to_call=get_conversation_history,
            expected_exception_type=TypeError,
            expected_message="cursor must be a string if provided.",
            channel="test_channel",
            cursor=123
        )

    # include_all_metadata validation
    def test_include_all_metadata_invalid_type_str(self):
        """Test include_all_metadata with invalid type (string)."""
        with self.assertRaises(TypeError):
            get_conversation_history(channel="C123", include_all_metadata="true")

    def test_include_all_metadata_invalid_type_int(self):
        """Test include_all_metadata with invalid type (integer)."""
        with self.assertRaises(TypeError):
            get_conversation_history(channel="C123", include_all_metadata=1)

    # inclusive validation
    def test_inclusive_invalid_type_str(self):
        """Test inclusive with invalid type (string)."""
        with self.assertRaises(TypeError):
            get_conversation_history(channel="C123", inclusive="true")

    def test_inclusive_invalid_type_int(self):
        """Test inclusive with invalid type (integer)."""
        with self.assertRaises(TypeError):
            get_conversation_history(channel="C123", inclusive=1)

    # latest validation
    def test_latest_valid_none(self):
        """Test latest with valid value (None)."""
        result = get_conversation_history(channel="C123", latest=None)
        self.assertTrue(result["ok"])
        self.assertIsInstance(result["messages"], list)

    def test_latest_invalid_type_int(self):
        """Test latest with invalid type (integer)."""
        with self.assertRaises(TypeError):
            get_conversation_history(channel="C123", latest=1678886400)

    def test_latest_invalid_type_float(self):
        """Test latest with invalid type (float)."""
        with self.assertRaises(TypeError):
            get_conversation_history(channel="C123", latest=1678886400.0)

    def test_latest_invalid_format(self):
        """Test latest with invalid timestamp format."""
        with self.assertRaises(TimestampError):
            get_conversation_history(channel="C123", latest="invalid_timestamp")

    # oldest validation
    def test_oldest_invalid_type_int(self):
        """Test oldest with invalid type (integer)."""
        with self.assertRaises(TypeError):
            get_conversation_history(channel="C123", oldest=0)

    def test_oldest_invalid_type_float(self):
        """Test oldest with invalid type (float)."""
        with self.assertRaises(TypeError):
            get_conversation_history(channel="C123", oldest=0.0)

    def test_oldest_invalid_format(self):
        """Test oldest with invalid timestamp format."""
        with self.assertRaises(TimestampError):
            get_conversation_history(channel="C123", oldest="invalid_timestamp")

    # limit validation
    def test_limit_invalid_type_str(self):
        """Test limit with invalid type (string)."""
        with self.assertRaises(TypeError):
            get_conversation_history(channel="C123", limit="100")

    def test_limit_invalid_type_float(self):
        """Test limit with invalid type (float)."""
        with self.assertRaises(TypeError):
            get_conversation_history(channel="C123", limit=100.0)

    def test_limit_invalid_value_zero(self):
        """Test limit with invalid value (0)."""
        with self.assertRaises(InvalidLimitError):
            get_conversation_history(channel="C123", limit=0)

    def test_limit_invalid_value_negative(self):
        """Test limit with invalid value (-1)."""
        with self.assertRaises(InvalidLimitError):
            get_conversation_history(channel="C123", limit=-1)

    def test_limit_invalid_value_too_large(self):
        """Test limit with invalid value (1000)."""
        with self.assertRaises(InvalidLimitError):
            get_conversation_history(channel="C123", limit=1000)

    def test_cursor_invalid_format(self):
        """Test behavior when cursor has invalid format (doesn't start with 'user:')."""
        # Create a base64-encoded string that doesn't start with 'user:'
        invalid_cursor = base64.b64encode(b'invalid_format').decode('utf-8')
        with self.assertRaises(InvalidCursorValueError):
            get_conversation_history(channel="C123", cursor=invalid_cursor)

    def test_user_id_filter_messages(self):
        """History should return only messages from the provided user ID."""
        result = get_conversation_history(channel="C123", user_id="U123")
        self.assertTrue(result["ok"])
        # Only messages from U123 should remain
        remaining_users = {m["user"] for m in result["messages"]}
        self.assertEqual(remaining_users, {"U123"})
        # Should have 2 messages from U123
        self.assertEqual(len(result["messages"]), 2)

    def test_user_id_type_validation(self):
        """Non-string user_id should raise TypeError."""
        with self.assertRaises(TypeError):
            get_conversation_history(channel="C123", user_id=123)

    def test_user_id_with_other_filters(self):
        """Test user_id filtering works with other filters like limit and timestamps."""
        result = get_conversation_history(
            channel="C123", 
            user_id="U123",
            limit=1,
            oldest="1678886300.000000",
            latest="1678886600.000000"
        )
        self.assertTrue(result["ok"])
        # Should only have messages from U123
        for message in result["messages"]:
            self.assertEqual(message["user"], "U123")
        # Should respect the limit
        self.assertLessEqual(len(result["messages"]), 1)

    def test_user_id_no_matches(self):
        """Test when user_id doesn't match any messages."""
        result = get_conversation_history(channel="C123", user_id="U999")
        self.assertTrue(result["ok"])
        # Should return empty list when no messages match user_id
        self.assertEqual(len(result["messages"]), 0)
        self.assertFalse(result["has_more"])
        self.assertIsNone(result["response_metadata"]["next_cursor"])
