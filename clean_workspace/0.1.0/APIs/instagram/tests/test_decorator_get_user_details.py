from typing import Dict, Any

from instagram.User import get_user
from common_utils.base_case import BaseTestCaseWithErrorHandler
from instagram.SimulationEngine.db import DB


get_user_details = get_user

class TestGetUserDetails(BaseTestCaseWithErrorHandler):
    def setUp(self):
        """Reset DB state before each test."""
        DB["users"] = {
            "existing_user_1": {"name": "Ada Lovelace", "username": "ada_l"},
            "existing_user_2": {"name": "Charles Babbage", "username": "charles_b"}
        }

    def test_valid_user_exists(self):
        """Test retrieving an existing user successfully."""
        user_id = "existing_user_1"
        expected_data = {"id": user_id, "name": "Ada Lovelace", "username": "ada_l"}
        
        result = get_user_details(user_id=user_id)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result, expected_data)

    def test_valid_user_does_not_exist(self):
        """Test retrieving a non-existing user."""
        user_id = "non_existing_user"
        expected_response = {"id": user_id, "error": "User not found"}
        
        result = get_user_details(user_id=user_id)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result, expected_response)

    def test_invalid_user_id_type_integer(self):
        """Test that providing an integer user_id raises TypeError."""
        invalid_user_id = 12345
        self.assert_error_behavior(
            func_to_call=get_user_details,
            expected_exception_type=TypeError,
            expected_message="user_id must be a string.",
            user_id=invalid_user_id
        )

    def test_invalid_user_id_type_none(self):
        """Test that providing None as user_id raises TypeError."""
        invalid_user_id = None
        self.assert_error_behavior(
            func_to_call=get_user_details,
            expected_exception_type=TypeError,
            expected_message="user_id must be a string.",
            user_id=invalid_user_id
        )

    def test_empty_user_id_string(self):
        """Test that an empty string user_id raises ValueError."""
        empty_user_id = ""
        self.assert_error_behavior(
            func_to_call=get_user_details,
            expected_exception_type=ValueError,
            expected_message="Field user_id cannot be empty.",
            user_id=empty_user_id
        )
    
    def test_user_id_with_spaces_is_valid_if_not_empty(self):
        """Test that a user_id consisting of only spaces is treated as non-empty (unless business logic changes)."""
        # This test assumes that "  " is not considered "empty" by `if not user_id:`.
        # If business rules state that user_id should be trimmed and then checked for emptiness,
        # this test (and the validation logic) would need adjustment.
        # Current validation only checks `if not user_id:`, which is true for `""` but false for `" "`.
        user_id_with_spaces = "   "
        expected_response = {"id": user_id_with_spaces, "error": "User not found"} # Assuming it won't be in DB
        
        result = get_user_details(user_id=user_id_with_spaces)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result, expected_response)

# To run these tests (if saved in a file, e.g., test_get_user.py):
# Ensure base_case.py is in PYTHONPATH or same directory if BaseTestCaseWithErrorHandler is not mocked.
# python -m unittest test_get_user.py
