# instagram/tests/test_users.py

import unittest
from instagram import User
import instagram as InstagramAPI
from .common import reset_db
from common_utils.base_case import BaseTestCaseWithErrorHandler
from instagram.SimulationEngine.custom_erros import UserAlreadyExistsError


class TestUserAPI(BaseTestCaseWithErrorHandler):
    """Test suite for the Instagram API User functionality."""

    def setUp(self):
        """
        Set up method called before each test.
        Resets the global DB to ensure a clean state for every test.
        """
        reset_db()

    def test_create_user(self):
        """Test creating a new user."""
        user = User.create_user("101", "Alice", "alice")
        self.assertEqual(user["id"], "101")
        self.assertEqual(user["username"], "alice")
        self.assertIn("101", InstagramAPI.DB["users"])
        with self.assertRaises(UserAlreadyExistsError):
            User.create_user("101", "Alice Twin", "alice2")


    def test_get_user(self):
        """Test retrieving an existing user."""
        User.create_user("102", "Bob", "bob")  # Create user first
        user = User.get_user("102")
        self.assertEqual(user["id"], "102")
        self.assertEqual(user["name"], "Bob")
        self.assertNotIn("error", user)

    def test_get_user_not_found(self):
        """Test retrieving a non-existent user."""
        user = User.get_user("999")
        self.assertEqual(user["id"], "999")
        self.assertIn("error", user)
        self.assertEqual(user["error"], "User not found")

    def test_list_users(self):
        """Test listing all users."""
        User.create_user("101", "Alice", "alice")
        User.create_user("102", "Bob", "bob")
        users = User.list_users()
        self.assertEqual(len(users), 2)
        # Check if user IDs are present in the list
        user_ids = {u["id"] for u in users}
        self.assertIn("101", user_ids)
        self.assertIn("102", user_ids)

    def test_delete_user(self):
        """Test deleting a user."""
        User.create_user("103", "Charlie", "charlie")
        self.assertIn("103", InstagramAPI.DB["users"])
        result = User.delete_user("103")
        self.assertTrue(result.get("success"))
        self.assertNotIn("103", InstagramAPI.DB["users"])
        # Test deleting non-existent user
        error_result = User.delete_user("999")
        self.assertIn("error", error_result)

    def test_get_user_id_by_username(self):
        """Test finding user ID by username (case-insensitive)."""
        User.create_user("102", "Bob", "bob")
        User.create_user("104", "David", "DAVID")
        user_id_bob = User.get_user_id_by_username("bob")
        self.assertEqual(user_id_bob, "102")
        user_id_david_lower = User.get_user_id_by_username("david")
        self.assertEqual(user_id_david_lower, "104")
        user_id_david_upper = User.get_user_id_by_username("DAVID")
        self.assertEqual(user_id_david_upper, "104")
        not_found = User.get_user_id_by_username("eve")
        self.assertEqual(not_found, "User not found")


if __name__ == "__main__":
    unittest.main()
