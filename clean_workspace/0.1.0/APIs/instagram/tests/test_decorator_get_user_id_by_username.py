from instagram.SimulationEngine.custom_erros import EmptyUsernameError
from instagram.User import get_user_id_by_username
from common_utils.base_case import BaseTestCaseWithErrorHandler
from instagram.SimulationEngine.db import DB


class TestGetUserIdByUsername(BaseTestCaseWithErrorHandler):
    
    def setUp(self):
        """Reset DB state before each test."""
        DB["users"] = {
            "user1": {"name": "Alice Smith", "username": "alice_smith"},
            "user2": {"name": "Bob Jones", "username": "BOB_JONES"},
            "user3": {"name": "Charlie Brown", "username": "charlie_b"}
        }

    def test_valid_username_found(self):
        """Test finding a user by username (case-insensitive)."""
        # Test exact match
        result = get_user_id_by_username("alice_smith")
        self.assertEqual(result, "user1")
        
        # Test case-insensitive match
        result = get_user_id_by_username("ALICE_SMITH")
        self.assertEqual(result, "user1")
        
        # Test another user with different case
        result = get_user_id_by_username("bob_jones")
        self.assertEqual(result, "user2")
        
        result = get_user_id_by_username("BOB_JONES")
        self.assertEqual(result, "user2")

    def test_username_not_found(self):
        """Test searching for a non-existent username."""
        result = get_user_id_by_username("nonexistent_user")
        self.assertEqual(result, "User not found")

    def test_invalid_username_type_integer(self):
        """Test that providing an integer username raises TypeError."""
        self.assert_error_behavior(
            func_to_call=get_user_id_by_username,
            expected_exception_type=TypeError,
            expected_message="Username must be a string.",
            username=12345
        )

    def test_invalid_username_type_none(self):
        """Test that providing None as username raises TypeError."""
        self.assert_error_behavior(
            func_to_call=get_user_id_by_username,
            expected_exception_type=TypeError,
            expected_message="Username must be a string.",
            username=None
        )

    def test_empty_username_string(self):
        """Test that an empty string username raises EmptyUsernameError."""
        self.assert_error_behavior(
            func_to_call=get_user_id_by_username,
            expected_exception_type=EmptyUsernameError,
            expected_message="Field username cannot be empty.",
            username=""
        )

    def test_username_with_only_spaces(self):
        """Test that a username consisting of only spaces raises EmptyUsernameError."""
        self.assert_error_behavior(
            func_to_call=get_user_id_by_username,
            expected_exception_type=EmptyUsernameError,
            expected_message="Field username cannot be empty.",
            username="   "
        )

    def test_valid_username_found_case_insensitive_lowercase_search(self):
        """Test finding a user with a lowercase username (case-insensitive match)."""
        result = get_user_id_by_username("alice_smith")
        self.assertEqual(result, "user1")
        
    def test_valid_username_found_case_insensitive_uppercase_search(self):
        """Test finding a user with an uppercase username (case-insensitive match)."""
        result = get_user_id_by_username("BOB_JONES")
        self.assertEqual(result, "user2")

    def test_valid_username_found_for_all_caps_stored_username(self):
        """Test finding a user whose username is stored in all caps."""
        result = get_user_id_by_username("BOB_JONES")
        self.assertEqual(result, "user2")
        result_caps = get_user_id_by_username("bob_jones")
        self.assertEqual(result_caps, "user2")

    def test_username_with_internal_spaces_exact_match(self):
        """Test finding a user whose stored username includes leading/trailing spaces."""
        # First add a user with spaces in username
        DB["users"]["user4"] = {"name": "Dave Space", "username": "  dave_space  "}
        result = get_user_id_by_username("  dave_space  ")
        self.assertEqual(result, "user4")

    def test_username_with_internal_spaces_case_insensitive_match(self):
        """Test finding a user whose stored username includes spaces, case-insensitively."""
        # First add a user with spaces in username
        DB["users"]["user4"] = {"name": "Dave Space", "username": "  dave_space  "}
        result = get_user_id_by_username("  DAVE_SPACE  ")
        self.assertEqual(result, "user4")

    def test_trimmed_username_search_for_spaced_db_entry_not_found(self):
        """Test searching with a trimmed username for a DB entry stored with spaces."""
        # "charlie".lower() != "  charlie  ".lower()
        result = get_user_id_by_username("charlie")
        self.assertEqual(result, "User not found")

    def test_spaced_username_search_for_trimmed_db_entry_not_found(self):
        """Test searching with a spaced username for a DB entry stored trimmed."""
        # " alice ".lower() != "alice".lower() (assuming "alice" is stored for "Alice")
        result = get_user_id_by_username(" alice ")
        self.assertEqual(result, "User not found")

    def test_invalid_username_type_list(self):
        """Test that providing a list for username raises TypeError."""
        self.assert_error_behavior(
            func_to_call=get_user_id_by_username,
            expected_exception_type=TypeError,
            expected_message="Username must be a string.",
            username=["alice"]
        )

    def test_whitespace_only_username_raises_error(self):
        """Test that a username consisting only of whitespace raises EmptyUsernameError."""
        self.assert_error_behavior(
            func_to_call=get_user_id_by_username,
            expected_exception_type=EmptyUsernameError,
            expected_message="Field username cannot be empty.",
            username="   "
        )

    def test_username_with_just_one_space_raises_error(self):
        """Test that a username consisting of a single space raises EmptyUsernameError."""
        self.assert_error_behavior(
            func_to_call=get_user_id_by_username,
            expected_exception_type=EmptyUsernameError,
            expected_message="Field username cannot be empty.",
            username=" "
        )
