import unittest
from typing import Dict, Any

from common_utils.base_case import BaseTestCaseWithErrorHandler
from instagram.Media import create_media
from instagram.SimulationEngine.custom_erros import UserNotFoundError # Required for type hints in tests
from instagram.SimulationEngine.db import DB

create_media_post = create_media

class TestCreateMedia(BaseTestCaseWithErrorHandler):
    def setUp(self):
        """Reset test state before each test."""
        global DB
        DB["users"] = {"test_user_1": {"name": "Test User One"}}
        DB["media"] = {}

    def test_valid_input_creates_media(self):
        """Test that valid input successfully creates a media post."""
        result = create_media_post(
            user_id="test_user_1",
            image_url="http://example.com/image.jpg",
            caption="A beautiful image."
        )
        self.assertIsInstance(result, dict)
        self.assertEqual(result["user_id"], "test_user_1")
        self.assertEqual(result["image_url"], "http://example.com/image.jpg")
        self.assertEqual(result["caption"], "A beautiful image.")
        self.assertIn("id", result)
        self.assertIn("timestamp", result)
        self.assertIn(result["id"], DB["media"]) # Check if actually stored

    def test_valid_input_with_default_caption(self):
        """Test successful creation with default empty caption."""
        result = create_media_post(
            user_id="test_user_1",
            image_url="http://example.com/image.png"
            # caption defaults to ""
        )
        self.assertEqual(result["caption"], "")
        self.assertIn(result["id"], DB["media"])

    # Tests for user_id validation
    def test_invalid_user_id_type_int(self):
        """Test that non-string user_id (int) raises TypeError."""
        self.assert_error_behavior(
            func_to_call=create_media_post,
            expected_exception_type=TypeError,
            expected_message="Argument 'user_id' must be a string.",
            user_id=123,
            image_url="http://example.com/image.jpg",
            caption="Test"
        )

    def test_invalid_user_id_type_none(self):
        """Test that non-string user_id (None) raises TypeError."""
        self.assert_error_behavior(
            func_to_call=create_media_post,
            expected_exception_type=TypeError,
            expected_message="Argument 'user_id' must be a string.",
            user_id=None,
            image_url="http://example.com/image.jpg",
            caption="Test"
        )

    def test_empty_user_id_raises_value_error(self):
        """Test that an empty string user_id raises ValueError."""
        self.assert_error_behavior(
            func_to_call=create_media_post,
            expected_exception_type=ValueError,
            expected_message="Argument 'user_id' cannot be empty.",
            user_id="",
            image_url="http://example.com/image.jpg",
            caption="Test"
        )

    # Tests for image_url validation
    def test_invalid_image_url_type_int(self):
        """Test that non-string image_url (int) raises TypeError."""
        self.assert_error_behavior(
            func_to_call=create_media_post,
            expected_exception_type=TypeError,
            expected_message="Argument 'image_url' must be a string.",
            user_id="test_user_1",
            image_url=12345,
            caption="Test"
        )

    def test_invalid_image_url_type_none(self):
        """Test that non-string image_url (None) raises TypeError."""
        self.assert_error_behavior(
            func_to_call=create_media_post,
            expected_exception_type=TypeError,
            expected_message="Argument 'image_url' must be a string.",
            user_id="test_user_1",
            image_url=None,
            caption="Test"
        )

    def test_empty_image_url_raises_value_error(self):
        """Test that an empty string image_url raises ValueError."""
        self.assert_error_behavior(
            func_to_call=create_media_post,
            expected_exception_type=ValueError,
            expected_message="Argument 'image_url' cannot be empty.",
            user_id="test_user_1",
            image_url="",
            caption="Test"
        )

    # Tests for caption validation
    def test_invalid_caption_type_int(self):
        """Test that non-string caption (int) raises TypeError."""
        self.assert_error_behavior(
            func_to_call=create_media_post,
            expected_exception_type=TypeError,
            expected_message="Argument 'caption' must be a string.",
            user_id="test_user_1",
            image_url="http://example.com/image.jpg",
            caption=123
        )
    
    def test_invalid_caption_type_none(self):
        """Test that non-string caption (None) raises TypeError."""
        # Note: caption has a default value "", so passing None explicitly would be caught.
        # If function signature allowed caption: Optional[str], this test would be different.
        # Here, None is an invalid type for the parameter.
        self.assert_error_behavior(
            func_to_call=create_media_post,
            expected_exception_type=TypeError,
            expected_message="Argument 'caption' must be a string.",
            user_id="test_user_1",
            image_url="http://example.com/image.jpg",
            caption=None # type: ignore 
        )


    # Test for core logic error (UserNotFoundError)
    def test_non_existent_user_id_raises_user_not_found_error(self):
        """Test that a non-existent user_id raises UserNotFoundError."""
        self.assert_error_behavior(
            func_to_call=create_media_post,
            expected_exception_type=UserNotFoundError,
            expected_message="User with ID 'unknown_user' does not exist.",
            user_id="unknown_user",
            image_url="http://example.com/image.jpg",
            caption="Test"
        )

    def test_media_id_generation_and_storage(self):
        """Test that media IDs are generated sequentially and data is stored."""
        create_media_post(user_id="test_user_1", image_url="url1", caption="cap1")
        self.assertIn("media_1", DB["media"])
        
        create_media_post(user_id="test_user_1", image_url="url2", caption="cap2")
        self.assertIn("media_2", DB["media"])
        self.assertEqual(DB["media"]["media_2"]["image_url"], "url2")

# To run the tests (if this file is executed directly)
if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)