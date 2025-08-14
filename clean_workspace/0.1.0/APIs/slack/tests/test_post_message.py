import time
from typing import Dict, Any
from unittest.mock import patch, MagicMock

from common_utils.base_case import BaseTestCaseWithErrorHandler  # Ensure this file/class exists in your test environment
from .. import post_chat_message
from ..SimulationEngine.custom_errors import ChannelNotFoundError, MessageNotFoundError

# Global DB for testing purposes, as per prompt's implication of DB's existence
DB: Dict[str, Any] = {}

# Original time module reference for patching
original_time_time = time.time


class TestPostMessageValidation(BaseTestCaseWithErrorHandler):
    def setUp(self):
        """Reset test state before each test."""
        global DB
        DB = {
            "channels": {
                "C123": {"name": "general", "messages": []},
                "C_WITH_MSG": {"name": "channel_with_message", "messages": [{"ts": "12345.000", "text": "Original"}]}
            }
        }
        # Mock time.time() for deterministic timestamps
        self.time_patcher = patch('time.time', MagicMock(return_value=1678886400.0))  # Example timestamp
        self.mock_time = self.time_patcher.start()

    def tearDown(self):
        self.time_patcher.stop()
        # Could reset DB here if modifications are persistent across test classes,
        # but setUp handles re-initialization for each test method in this class.

    @patch("slack.Chat.DB", new_callable=lambda: DB)
    def test_valid_input_minimal(self, mock_db):
        """Test postMessage with minimal valid required input."""
        result = post_chat_message(channel="C123", text="Hello")
        self.assertTrue(result["ok"])
        self.assertEqual(result["message"]["channel"], "C123")
        self.assertEqual(result["message"]["text"], "Hello")
        self.assertEqual(result["message"]["ts"], "1678886400.0")  # Mocked time

    @patch("slack.Chat.DB", new_callable=lambda: DB)
    def test_valid_input_all_optional_params_set(self, mock_db):
        """Test postMessage with all optional parameters correctly set."""
        blocks_data = [{"type": "section", "text": {"type": "mrkdwn", "text": "A block"}}]
        # First add the parent message to C123
        DB["channels"]["C123"]["messages"] = [{"ts": "12345.000", "text": "Parent message"}]
        
        result = post_chat_message(
            channel="C123",
            ts="custom_ts_1",
            attachments='[{"text": "attachment text"}]',
            blocks=blocks_data,
            text="Fallback text",
            as_user=True,
            icon_emoji=":smile:",
            icon_url="http://example.com/icon.png",
            link_names=True,
            markdown_text="*Markdown* text",
            metadata='{"event_type": "foo", "event_payload": {"bar": "baz"}}',
            mrkdwn=False,
            parse="full",
            reply_broadcast=True,
            thread_ts="12345.000",  # This thread now exists in C123
            unfurl_links=True,
            unfurl_media=False,
            username="TestBot"
        )

        self.assertTrue(result["ok"])
        self.assertIn("replies", result["message"])
        self.assertEqual(result["message"]["replies"][0]["text"], "Fallback text")

    # Channel validation
    @patch("slack.Chat.DB", new_callable=lambda: DB)
    def test_invalid_channel_type(self, mock_db):
        """Test TypeError for non-string channel."""
        self.assert_error_behavior(
            func_to_call=post_chat_message,
            expected_exception_type=TypeError,
            expected_message="Argument 'channel' must be a string, got int.",
            channel=123, text="Test"
        )

    def test_empty_channel_value(self):
        """Test ValueError for empty string channel."""
        self.assert_error_behavior(
            func_to_call=post_chat_message,
            expected_exception_type=ValueError,
            expected_message="Argument 'channel' cannot be an empty string.",
            channel="", text="Test"
        )

    # Optional string arguments validation
    def test_invalid_ts_type(self):
        """Test TypeError for non-string ts."""
        self.assert_error_behavior(
            func_to_call=post_chat_message,
            expected_exception_type=TypeError,
            expected_message="Argument 'ts' must be a string or None, got int.",
            channel="C123", text="Test", ts=12345
        )

    # Optional boolean arguments validation
    def test_invalid_as_user_type(self):
        """Test TypeError for non-bool as_user."""
        self.assert_error_behavior(
            func_to_call=post_chat_message,
            expected_exception_type=TypeError,
            expected_message="Argument 'as_user' must be a boolean or None, got str.",
            channel="C123", text="Test", as_user="not_a_bool"
        )

    # Blocks validation
    def test_blocks_not_a_list(self):
        """Test TypeError if blocks is not a list."""
        self.assert_error_behavior(
            func_to_call=post_chat_message,
            expected_exception_type=TypeError,
            expected_message="Argument 'blocks' must be a list or None, got str.",
            channel="C123", text="Test", blocks="not_a_list"
        )

    def test_blocks_item_not_a_dict(self):
        """Test TypeError if an item in blocks is not a dictionary."""
        self.assert_error_behavior(
            func_to_call=post_chat_message,
            expected_exception_type=TypeError,
            expected_message="Each item in 'blocks' must be a dictionary. Item at index 0 is str.",
            channel="C123", text="Test", blocks=["not_a_dict_item"]
        )

    @patch("slack.Chat.DB", new_callable=lambda: DB)
    def test_blocks_item_valid_dict_empty(self, mock_db):
        """Test valid empty dict in blocks (passes BlockItemStructure with extra='allow')."""
        result = post_chat_message(channel="C123", text="Test", blocks=[{}])
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["message"]["blocks"]), 1)
        self.assertEqual(result["message"]["blocks"][0], {})

    @patch("slack.Chat.DB", new_callable=lambda: DB)
    def test_blocks_item_valid_dict_with_data(self, mock_db):
        """Test valid dict with data in blocks."""
        block_data = {"type": "section", "text": {"type": "mrkdwn", "text": "Hello"}}
        result = post_chat_message(channel="C123", text="Test", blocks=[block_data])
        self.assertTrue(result["ok"])
        self.assertEqual(result["message"]["blocks"][0], block_data)

    # Core logic error handling (not validation layer)
    def test_channel_not_found(self):
        """Test core logic for channel_not_found error."""
        self.assert_error_behavior(
            func_to_call=post_chat_message,
            expected_exception_type=ChannelNotFoundError,
            expected_message="Channel 'C_NON_EXISTENT' not found in database.",
            channel="C_NON_EXISTENT", text="Test"
        )

    @patch("slack.Chat.DB", new_callable=lambda: DB)
    def test_thread_not_found_if_messages_key_missing(self, mock_db):
        """Test core logic for thread_not_found if 'messages' key is not present in channel data."""
        # Set up channel without 'messages' key
        DB["channels"]["C123"] = {"name": "general"}  # No messages key
        
        self.assert_error_behavior(
            func_to_call=post_chat_message,
            expected_exception_type=MessageNotFoundError,
            expected_message="Message in tread 'any_ts' not found.",
            channel="C123", text="Reply", thread_ts="any_ts"
        )

    @patch("slack.Chat.DB", new_callable=lambda: DB)
    def test_thread_not_found_if_channel_has_no_messages(self, mock_db):
        """Test core logic for thread_not_found if channel has no messages."""
        # C123 is initially empty for messages in DB setup.
        self.assert_error_behavior(
            func_to_call=post_chat_message,
            expected_exception_type=MessageNotFoundError,
            expected_message="Message in tread 'any_ts' not found.",
            channel="C123", text="Reply", thread_ts="any_ts"
        )

    @patch("slack.Chat.DB", new_callable=lambda: DB)
    def test_thread_not_found_if_ts_mismatch(self, mock_db):
        """Test core logic for thread_not_found if thread_ts does not match any message."""
        DB["channels"]["C123"]["messages"] = [{"ts": "existing_ts", "text": "Parent"}]
        self.assert_error_behavior(
            func_to_call=post_chat_message,
            expected_exception_type=MessageNotFoundError,
            expected_message="Message in tread 'non_existing_ts' not found.",
            channel="C123", text="Reply", thread_ts="non_existing_ts"
        )

    @patch("slack.Chat.DB", new_callable=lambda: DB)
    def test_successful_reply_to_thread(self, mock_db):
        """Test successfully posting a reply to an existing thread."""
        parent_ts = "existing_parent_ts"
        DB["channels"]["C123"]["messages"] = [{"ts": parent_ts, "text": "This is a parent message."}]
        result = post_chat_message(channel="C123", text="This is a reply", thread_ts=parent_ts)
        self.assertTrue(result["ok"])
        self.assertIn("message", result)
        self.assertEqual(result["message"]["ts"], parent_ts)  # Returns the parent message
        self.assertIn("replies", result["message"])
        self.assertEqual(len(result["message"]["replies"]), 1)
        self.assertEqual(result["message"]["replies"][0]["text"], "This is a reply")
