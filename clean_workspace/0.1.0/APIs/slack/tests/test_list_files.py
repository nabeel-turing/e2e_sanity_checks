"""
Test cases for the list_files function in the Slack Files API.

This module contains comprehensive test cases for the list_files function,
including success scenarios, filter combinations, and all error conditions.
"""

import unittest
from unittest.mock import patch
from common_utils.base_case import BaseTestCaseWithErrorHandler
from ..Files import list_files
from ..SimulationEngine.custom_errors import (
    ChannelNotFoundError,
    UserNotFoundError,
    InvalidCursorFormatError,
    CursorOutOfBoundsError
)


class TestListFiles(BaseTestCaseWithErrorHandler):
    """Test cases for the list_files function."""

    def setUp(self):
        """Set up test fixtures with sample data."""
        self.test_db = {
            "files": {
                "F_TEST_FILE_1": {
                    "id": "F_TEST_FILE_1",
                    "name": "document.pdf",
                    "title": "Test Document",
                    "filetype": "pdf",
                    "mimetype": "application/pdf",
                    "size": 1024,
                    "user": "U_USER_1",
                    "created": 1640995200,  # 2022-01-01 00:00:00
                },
                "F_TEST_FILE_2": {
                    "id": "F_TEST_FILE_2",
                    "name": "image.jpg",
                    "title": "Test Image",
                    "filetype": "jpg",
                    "mimetype": "image/jpeg",
                    "size": 2048,
                    "user": "U_USER_2",
                    "created": 1641081600,  # 2022-01-02 00:00:00
                },
                "F_TEST_FILE_3": {
                    "id": "F_TEST_FILE_3",
                    "name": "spreadsheet.xlsx",
                    "title": "Test Spreadsheet",
                    "filetype": "xlsx",
                    "mimetype": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "size": 4096,
                    "user": "U_USER_1",
                    "created": 1641168000,  # 2022-01-03 00:00:00
                },
                "F_TEST_FILE_4": {
                    "id": "F_TEST_FILE_4",
                    "name": "presentation.pptx",
                    "title": "Test Presentation",
                    "filetype": "pptx",
                    "mimetype": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    "size": 8192,
                    "user": "U_USER_2",
                    "created": 1641254400,  # 2022-01-04 00:00:00
                }
            },
            "channels": {
                "C_CHANNEL_1": {
                    "id": "C_CHANNEL_1",
                    "name": "general",
                    "files": {
                        "F_TEST_FILE_1": True,
                        "F_TEST_FILE_2": True
                    }
                },
                "C_CHANNEL_2": {
                    "id": "C_CHANNEL_2",
                    "name": "random",
                    "files": {
                        "F_TEST_FILE_3": True
                    }
                },
                "C_CHANNEL_3": {
                    "id": "C_CHANNEL_3",
                    "name": "empty",
                    "files": {}
                }
            },
            "users": {
                "U_USER_1": {
                    "id": "U_USER_1",
                    "name": "user1"
                },
                "U_USER_2": {
                    "id": "U_USER_2",
                    "name": "user2"
                }
            }
        }

    # ==================== SUCCESS TEST CASES ====================

    @patch("slack.Files.DB", new_callable=lambda: {})
    def test_list_files_success_all_files_default(self, mock_db):
        """Test successful listing of all files with default parameters."""
        mock_db.update(self.test_db)
        result = list_files()
        
        self.assertIsInstance(result, dict)
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["files"]), 4)
        self.assertIsNone(result["response_metadata"]["next_cursor"])
        
        # Verify all files are returned
        file_ids = [f["id"] for f in result["files"]]
        expected_ids = ["F_TEST_FILE_1", "F_TEST_FILE_2", "F_TEST_FILE_3", "F_TEST_FILE_4"]
        self.assertEqual(set(file_ids), set(expected_ids))

    @patch("slack.Files.DB", new_callable=lambda: {})
    def test_list_files_success_filter_by_channel(self, mock_db):
        """Test successful listing of files filtered by channel."""
        mock_db.update(self.test_db)
        result = list_files(channel_id="C_CHANNEL_1")
        
        self.assertIsInstance(result, dict)
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["files"]), 2)
        
        # Verify correct files are returned
        file_ids = [f["id"] for f in result["files"]]
        expected_ids = ["F_TEST_FILE_1", "F_TEST_FILE_2"]
        self.assertEqual(set(file_ids), set(expected_ids))

    @patch("slack.Files.DB", new_callable=lambda: {})
    def test_list_files_success_filter_by_user(self, mock_db):
        """Test successful listing of files filtered by user."""
        mock_db.update(self.test_db)
        result = list_files(user_id="U_USER_1")
        
        self.assertIsInstance(result, dict)
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["files"]), 2)

    @patch("slack.Files.DB", new_callable=lambda: {})
    def test_list_files_success_filter_by_types(self, mock_db):
        """Test successful listing of files filtered by file types."""
        mock_db.update(self.test_db)
        result = list_files(types="pdf,jpg")
        
        self.assertIsInstance(result, dict)
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["files"]), 2)

    @patch("slack.Files.DB", new_callable=lambda: {})
    def test_list_files_success_combined_filters(self, mock_db):
        """Test successful listing with multiple filters combined."""
        mock_db.update(self.test_db)
        result = list_files(
            channel_id="C_CHANNEL_1",
            user_id="U_USER_1",
            types="pdf"
        )
        
        self.assertIsInstance(result, dict)
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["files"]), 1)
        
        # Verify correct file is returned
        self.assertEqual(result["files"][0]["id"], "F_TEST_FILE_1")

    @patch("slack.Files.DB", new_callable=lambda: {})
    def test_list_files_success_pagination_with_limit(self, mock_db):
        """Test successful pagination with custom limit."""
        mock_db.update(self.test_db)
        result = list_files(limit=2)
        
        self.assertIsInstance(result, dict)
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["files"]), 2)
        self.assertEqual(result["response_metadata"]["next_cursor"], "2")

    @patch("slack.Files.DB", new_callable=lambda: {})
    def test_list_files_success_pagination_with_cursor(self, mock_db):
        """Test successful pagination with cursor."""
        mock_db.update(self.test_db)
        result = list_files(cursor="2", limit=2)
        
        self.assertIsInstance(result, dict)
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["files"]), 2)
        self.assertIsNone(result["response_metadata"]["next_cursor"])

    # ==================== ERROR TEST CASES ====================

    def test_list_files_channel_id_invalid_type_integer(self):
        """Test TypeError when channel_id is an integer."""
        self.assert_error_behavior(
            list_files,
            TypeError,
            "channel_id must be a string or None.",
            None,
            channel_id=123
        )

    def test_list_files_user_id_invalid_type_integer(self):
        """Test TypeError when user_id is an integer."""
        self.assert_error_behavior(
            list_files,
            TypeError,
            "user_id must be a string or None.",
            None,
            user_id=123
        )

    def test_list_files_limit_invalid_type_string(self):
        """Test TypeError when limit is a string."""
        self.assert_error_behavior(
            list_files,
            TypeError,
            "limit must be an integer.",
            None,
            limit="100"
        )

    def test_list_files_limit_invalid_value_zero(self):
        """Test ValueError when limit is zero."""
        self.assert_error_behavior(
            list_files,
            ValueError,
            "limit must be a positive integer.",
            None,
            limit=0
        )

    def test_list_files_limit_invalid_value_negative(self):
        """Test ValueError when limit is negative."""
        self.assert_error_behavior(
            list_files,
            ValueError,
            "limit must be a positive integer.",
            None,
            limit=-5
        )

    @patch("slack.Files.DB", new_callable=lambda: {})
    def test_list_files_ts_from_invalid_format(self, mock_db):
        """Test ValueError when ts_from has invalid format."""
        mock_db.update(self.test_db)
        self.assert_error_behavior(
            list_files,
            ValueError,
            "Invalid ts_from format: not_a_timestamp. Must be a Unix timestamp string.",
            None,
            ts_from="not_a_timestamp"
        )

    @patch("slack.Files.DB", new_callable=lambda: {})
    def test_list_files_channel_not_found(self, mock_db):
        """Test ChannelNotFoundError when channel doesn't exist."""
        mock_db.update(self.test_db)
        self.assert_error_behavior(
            list_files,
            ChannelNotFoundError,
            "Channel 'C_NONEXISTENT' not found.",
            None,
            channel_id="C_NONEXISTENT"
        )

    @patch("slack.Files.DB", new_callable=lambda: {})
    def test_list_files_user_not_found(self, mock_db):
        """Test UserNotFoundError when user doesn't exist."""
        mock_db.update(self.test_db)
        self.assert_error_behavior(
            list_files,
            UserNotFoundError,
            "User 'U_NONEXISTENT' not found.",
            None,
            user_id="U_NONEXISTENT"
        )

    @patch("slack.Files.DB", new_callable=lambda: {})
    def test_list_files_cursor_invalid_format_non_integer(self, mock_db):
        """Test InvalidCursorFormatError when cursor is not an integer."""
        mock_db.update(self.test_db)
        self.assert_error_behavior(
            list_files,
            InvalidCursorFormatError,
            "Invalid cursor format. Must be a string representing an integer.",
            None,
            cursor="not_an_integer"
        )

    @patch("slack.Files.DB", new_callable=lambda: {})
    def test_list_files_cursor_out_of_bounds(self, mock_db):
        """Test CursorOutOfBoundsError when cursor exceeds data length."""
        mock_db.update(self.test_db)
        self.assert_error_behavior(
            list_files,
            CursorOutOfBoundsError,
            "Cursor 10 exceeds available data length (4)",
            None,
            cursor="10"
        )


if __name__ == "__main__":
    unittest.main()
