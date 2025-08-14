import unittest
from pydantic import ValidationError
from typing import Dict, Any

import linkedin as LinkedinAPI
from linkedin.Posts import create_post
from .common import reset_db
from common_utils.base_case import BaseTestCaseWithErrorHandler

# Function alias for tests
Posts_create_post = create_post

class TestCreatePostValidation(BaseTestCaseWithErrorHandler):
    """Tests input validation for the create_post function."""

    def setUp(self):
        """Reset the DB before each test."""
        reset_db()

    def test_valid_input(self):
        """Test that valid post_data is accepted and processed."""
        valid_data = {
            "author": "urn:li:person:12345",
            "commentary": "This is a valid post.",
            "visibility": "PUBLIC"
        }
        result = Posts_create_post(post_data=valid_data)
        self.assertIsInstance(result, dict)
        self.assertIn("data", result)
        self.assertIsInstance(result["data"], dict)
        self.assertEqual(result["data"]["id"], "1")
        self.assertEqual(result["data"]["author"], valid_data["author"])
        self.assertEqual(result["data"]["commentary"], valid_data["commentary"])
        self.assertEqual(result["data"]["visibility"], valid_data["visibility"])
        self.assertIn("1", LinkedinAPI.DB["posts"])
        self.assertEqual(LinkedinAPI.DB["posts"]["1"], result["data"])

    def test_valid_input_organization_urn(self):
        """Test valid input with an organization URN."""
        valid_data = {
            "author": "urn:li:organization:67890",
            "commentary": "Post from an organization.",
            "visibility": "CONNECTIONS"
        }
        result = Posts_create_post(post_data=valid_data)
        self.assertIsInstance(result, dict)
        self.assertIn("data", result)
        self.assertEqual(result["data"]["author"], valid_data["author"])
        self.assertEqual(LinkedinAPI.DB["next_post_id"], 2) # Check DB state change

    def test_invalid_post_data_type_list(self):
        """Test TypeError when post_data is a list."""
        self.assert_error_behavior(
            func_to_call=Posts_create_post,
            expected_exception_type=TypeError,
            expected_message="Expected 'post_data' to be a dictionary, but got list.",
            post_data=[]
        )

    def test_invalid_post_data_type_string(self):
        """Test TypeError when post_data is a string."""
        self.assert_error_behavior(
            func_to_call=Posts_create_post,
            expected_exception_type=TypeError,
            expected_message="Expected 'post_data' to be a dictionary, but got str.",
            post_data="not a dict"
        )

    def test_missing_author(self):
        """Test ValidationError when 'author' key is missing."""
        invalid_data = {
            # "author": "urn:li:person:1", # Missing
            "commentary": "Missing author post.",
            "visibility": "PUBLIC"
        }
        self.assert_error_behavior(
            func_to_call=Posts_create_post,
            expected_exception_type=ValidationError,
            expected_message="1 validation error for PostDataModel\nauthor\n  Field required [type=missing, input_value={'commentary': 'Missing a... 'visibility': 'PUBLIC'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.11/v/missing",
            post_data=invalid_data
        )

    def test_missing_commentary(self):
        """Test ValidationError when 'commentary' key is missing."""
        invalid_data = {
            "author": "urn:li:person:1",
            # "commentary": "Missing commentary.", # Missing
            "visibility": "CONNECTIONS"
        }
        self.assert_error_behavior(
            func_to_call=Posts_create_post,
            expected_exception_type=ValidationError,
            expected_message="1 validation error for PostDataModel\ncommentary\n  Field required [type=missing, input_value={'author': 'urn:li:person...ibility': 'CONNECTIONS'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.11/v/missing",
            post_data=invalid_data
        )

    def test_missing_visibility(self):
        """Test ValidationError when 'visibility' key is missing."""
        invalid_data = {
            "author": "urn:li:person:1",
            "commentary": "Missing visibility.",
            # "visibility": "LOGGED_IN" # Missing
        }
        self.assert_error_behavior(
            func_to_call=Posts_create_post,
            expected_exception_type=ValidationError,
            expected_message="1 validation error for PostDataModel\nvisibility\n  Field required [type=missing, input_value={'author': 'urn:li:person...: 'Missing visibility.'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.11/v/missing",
            post_data=invalid_data
        )

    def test_invalid_author_type(self):
        """Test ValidationError when 'author' has incorrect type."""
        invalid_data = {
            "author": 12345,  # Incorrect type (int)
            "commentary": "Invalid author type.",
            "visibility": "PUBLIC"
        }
        # Pydantic v2 produces slightly different error messages
        # We match the core part: type str expected
        self.assert_error_behavior(
            func_to_call=Posts_create_post,
            expected_exception_type=ValidationError,
            # Match specific message structure for Pydantic v2
            expected_message='1 validation error for PostDataModel\nauthor\n  Input should be a valid string [type=string_type, input_value=12345, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.11/v/string_type',
            post_data=invalid_data
        )

    def test_invalid_commentary_type(self):
        """Test ValidationError when 'commentary' has incorrect type."""
        invalid_data = {
            "author": "urn:li:person:1",
            "commentary": ["Not", "a", "string"],  # Incorrect type (list)
            "visibility": "PUBLIC"
        }
        self.assert_error_behavior(
            func_to_call=Posts_create_post,
            expected_exception_type=ValidationError,
            expected_message="1 validation error for PostDataModel\ncommentary\n  Input should be a valid string [type=string_type, input_value=['Not', 'a', 'string'], input_type=list]\n    For further information visit https://errors.pydantic.dev/2.11/v/string_type",
            post_data=invalid_data
        )

    def test_invalid_visibility_type(self):
        """Test ValidationError when 'visibility' has incorrect type."""
        invalid_data = {
            "author": "urn:li:person:1",
            "commentary": "Invalid visibility type.",
            "visibility": None  # Incorrect type (NoneType)
        }
        # Literal error message is quite specific
        self.assert_error_behavior(
            func_to_call=Posts_create_post,
            expected_exception_type=ValidationError,
            expected_message="1 validation error for PostDataModel\nvisibility\n  Input should be 'PUBLIC', 'CONNECTIONS', 'LOGGED_IN' or 'CONTAINER' [type=literal_error, input_value=None, input_type=NoneType]\n    For further information visit https://errors.pydantic.dev/2.11/v/literal_error",
            post_data=invalid_data
        )

    def test_invalid_visibility_value(self):
        """Test ValidationError when 'visibility' has an invalid string value."""
        invalid_data = {
            "author": "urn:li:person:1",
            "commentary": "Invalid visibility value.",
            "visibility": "FRIENDS_ONLY"  # Invalid value
        }
        self.assert_error_behavior(
            func_to_call=Posts_create_post,
            expected_exception_type=ValidationError,
            expected_message="1 validation error for PostDataModel\nvisibility\n  Input should be 'PUBLIC', 'CONNECTIONS', 'LOGGED_IN' or 'CONTAINER' [type=literal_error, input_value='FRIENDS_ONLY', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.11/v/literal_error",
            post_data=invalid_data
        )

    def test_invalid_author_urn_format_wrong_prefix(self):
        """Test ValidationError when 'author' URN format is incorrect (prefix)."""
        invalid_data = {
            "author": "user:li:person:1", # Incorrect prefix
            "commentary": "Invalid author URN.",
            "visibility": "PUBLIC"
        }
        self.assert_error_behavior(
            func_to_call=Posts_create_post,
            expected_exception_type=ValidationError,
            expected_message="1 validation error for PostDataModel\nauthor\n  Value error, Invalid author URN format: 'user:li:person:1'. Expected format like 'urn:li:person:1' or 'urn:li:organization:1'. [type=value_error, input_value='user:li:person:1', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.11/v/value_error",
            post_data=invalid_data
        )

    def test_invalid_author_urn_format_wrong_type(self):
        """Test ValidationError when 'author' URN format is incorrect (type)."""
        invalid_data = {
            "author": "urn:li:group:1", # Incorrect type 'group'
            "commentary": "Invalid author URN.",
            "visibility": "PUBLIC"
        }
        self.assert_error_behavior(
            func_to_call=Posts_create_post,
            expected_exception_type=ValidationError,
            expected_message="1 validation error for PostDataModel\nauthor\n  Value error, Invalid author URN format: 'urn:li:group:1'. Expected format like 'urn:li:person:1' or 'urn:li:organization:1'. [type=value_error, input_value='urn:li:group:1', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.11/v/value_error",
            post_data=invalid_data
        )

    def test_invalid_author_urn_format_non_digit_id(self):
        """Test ValidationError when 'author' URN format is incorrect (id)."""
        invalid_data = {
            "author": "urn:li:person:abc", # Incorrect id 'abc'
            "commentary": "Invalid author URN.",
            "visibility": "PUBLIC"
        }
        self.assert_error_behavior(
            func_to_call=Posts_create_post,
            expected_exception_type=ValidationError,
            expected_message="1 validation error for PostDataModel\nauthor\n  Value error, Invalid author URN format: 'urn:li:person:abc'. Expected format like 'urn:li:person:1' or 'urn:li:organization:1'. [type=value_error, input_value='urn:li:person:abc', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.11/v/value_error",
            post_data=invalid_data
        )

    def test_extra_field_ignored(self):
        """Test that extra fields in post_data are ignored by default."""
        valid_data_with_extra = {
            "author": "urn:li:person:123",
            "commentary": "Post with extra field.",
            "visibility": "LOGGED_IN",
            "extra_field": "should be ignored"
        }
        # Pydantic's default behavior ('extra = ignore') means this should pass validation
        result = Posts_create_post(post_data=valid_data_with_extra)
        self.assertIsInstance(result, dict)
        self.assertIn("data", result)
        self.assertEqual(result["data"]["author"], valid_data_with_extra["author"])
        # Check that the extra field is still present in the data returned by the original logic
        self.assertIn("extra_field", result["data"])
        self.assertEqual(result["data"]["extra_field"], "should be ignored")
        # Check that it was stored in the DB as well
        self.assertIn("extra_field", LinkedinAPI.DB["posts"]["1"])
