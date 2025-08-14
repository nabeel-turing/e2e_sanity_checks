from unittest.mock import patch

from google_chat.SimulationEngine.custom_errors import InvalidSpaceNameFormatError
from google_chat.Spaces import delete
from common_utils.base_case import BaseTestCaseWithErrorHandler

# Function alias for tests
Spaces_delete = delete


class TestSpacesDeleteValidation(BaseTestCaseWithErrorHandler):
    def setUp(self):
        """Reset test state (DB and CURRENT_USER_ID) before each test."""
        global DB, CURRENT_USER_ID
        DB = {
            "Space": [],
            "Membership": [],
            "Message": [],
            "Reaction": [],
            "Attachment": []
        }
        CURRENT_USER_ID = {"id": "test_user_id"}

    @patch("google_chat.Spaces.DB", new_callable=lambda: DB)
    def test_valid_input_admin_access(self, mock_db):
        """Test valid input with admin access deletes the space."""
        space_name = "spaces/s1"
        DB["Space"].append({"name": space_name, "displayName": "Space One"})
        DB["Membership"].append({"name": f"{space_name}/members/other_user", "member": "users/other_user"})
        DB["Message"].append({"name": f"{space_name}/messages/m1", "text": "Hello"})

        result = Spaces_delete(name=space_name, useAdminAccess=True)
        self.assertEqual(result, {})
        self.assertEqual(DB["Membership"], [])
        self.assertEqual(DB["Message"], [])

    @patch("google_chat.Spaces.DB", new_callable=lambda: DB)
    def test_valid_input_member_access(self, mock_db):
        """Test valid input with member access (non-admin) deletes the space."""
        space_name = "spaces/s2"
        CURRENT_USER_ID["id"] = "member_user"
        DB["Space"].append({"name": space_name, "displayName": "Space Two"})
        DB["Membership"].append({"name": f"{space_name}/members/member_user", "member": "users/member_user"})

        result = Spaces_delete(name=space_name, useAdminAccess=False)
        self.assertEqual(result, {})

    @patch("google_chat.Spaces.DB", new_callable=lambda: DB)
    def test_valid_input_use_admin_access_is_none(self, mock_db):
        """Test valid input where useAdminAccess is None (default)."""
        space_name = "spaces/s3"
        CURRENT_USER_ID["id"] = "member_user_for_s3"
        DB["Space"].append({"name": space_name, "displayName": "Space Three"})
        DB["Membership"].append(
            {"name": f"{space_name}/members/member_user_for_s3", "member": "users/member_user_for_s3"})
        # useAdminAccess=None means it will behave like False, requiring membership
        result = Spaces_delete(name=space_name, useAdminAccess=None)
        self.assertEqual(result, {})

    # --- Tests for 'name' argument ---
    def test_invalid_name_type(self):
        """Test that non-string 'name' raises TypeError."""
        self.assert_error_behavior(
            func_to_call=Spaces_delete,
            expected_exception_type=TypeError,
            expected_message="Argument 'name' must be a string.",
            name=123
        )

    def test_invalid_name_empty(self):
        """Test that empty string 'name' raises ValueError."""
        self.assert_error_behavior(
            func_to_call=Spaces_delete,
            expected_exception_type=ValueError,
            expected_message="Argument 'name' cannot be an empty string.",
            name=""
        )

    def test_invalid_name_format_no_prefix(self):
        """Test 'name' with incorrect format (no 'spaces/' prefix) raises InvalidSpaceNameFormatError."""
        self.assert_error_behavior(
            func_to_call=Spaces_delete,
            expected_exception_type=InvalidSpaceNameFormatError,
            expected_message="Argument 'name' ('just_id') is not in the expected format 'spaces/{space_id}'.",
            name="just_id"
        )

    def test_invalid_name_format_trailing_slash(self):
        """Test 'name' with incorrect format (trailing slash) raises InvalidSpaceNameFormatError."""
        self.assert_error_behavior(
            func_to_call=Spaces_delete,
            expected_exception_type=InvalidSpaceNameFormatError,
            expected_message="Argument 'name' ('spaces/id/') is not in the expected format 'spaces/{space_id}'.",
            name="spaces/id/"
        )

    def test_invalid_name_format_multiple_slashes(self):
        """Test 'name' with incorrect format (multiple slashes) raises InvalidSpaceNameFormatError."""
        self.assert_error_behavior(
            func_to_call=Spaces_delete,
            expected_exception_type=InvalidSpaceNameFormatError,
            expected_message="Argument 'name' ('spaces/id/extra') is not in the expected format 'spaces/{space_id}'.",
            name="spaces/id/extra"
        )

    # --- Tests for 'useAdminAccess' argument ---
    def test_invalid_use_admin_access_type(self):
        """Test that non-boolean, non-None 'useAdminAccess' raises TypeError."""
        self.assert_error_behavior(
            func_to_call=Spaces_delete,
            expected_exception_type=TypeError,
            expected_message="Argument 'useAdminAccess' must be a boolean or None.",
            name="spaces/valid_name",
            useAdminAccess="not_a_bool"
        )

    # --- Tests for core logic behavior (non-exception returns) ---
    @patch("google_chat.Spaces.DB", new_callable=lambda: DB)
    def test_space_not_found(self, mock_db):
        """Test that trying to delete a non-existent space returns {}."""
        result = Spaces_delete(name="spaces/non_existent_space", useAdminAccess=True)
        self.assertEqual(result, {})

    @patch("google_chat.Spaces.DB", new_callable=lambda: DB)
    def test_unauthorized_not_member(self, mock_db):
        """Test unauthorized deletion (not admin, not member) returns {}."""
        space_name = "spaces/s4"
        DB["Space"].append({"name": space_name, "displayName": "Space Four"})
        CURRENT_USER_ID["id"] = "non_member_user"  # This user is not a member of s4

        result = Spaces_delete(name=space_name, useAdminAccess=False)
        self.assertEqual(result, {})
        # Ensure space was NOT deleted
        self.assertIn({"name": space_name, "displayName": "Space Four"}, DB["Space"])

    @patch("google_chat.Spaces.DB", new_callable=lambda: DB)
    def test_unauthorized_no_current_user_id_and_not_admin(self, mock_db):
        """Test deletion attempt without admin access when CURRENT_USER_ID is None."""
        global CURRENT_USER_ID
        CURRENT_USER_ID = None
        space_name = "spaces/s5"
        DB["Space"].append({"name": space_name, "displayName": "Space Five"})

        result = Spaces_delete(name=space_name, useAdminAccess=False)
        self.assertEqual(result, {})  # Should successfully delete as per original logic flow

        # Reset CURRENT_USER_ID for other tests
        CURRENT_USER_ID = {"id": "test_user_id"}
