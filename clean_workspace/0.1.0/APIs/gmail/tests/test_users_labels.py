# tests/test_users_labels.py
import unittest
import builtins

from pydantic import ValidationError

from ..SimulationEngine.db import DB
from common_utils.base_case import BaseTestCaseWithErrorHandler
from ..SimulationEngine.utils import reset_db
from .. import list_labels, create_label, update_label, patch_label, delete_label, get_label
from ..SimulationEngine import custom_errors

class TestUsersLabels(BaseTestCaseWithErrorHandler): # First class name and base
    # --- Content from the 1st Class (TestUsersLabels) - UNCHANGED ---
    def setUp(self):
        reset_db() # This sets up the DB for all tests in this class

    def test_create_update_patch_get_list_delete_label(self):
        label = create_label("me", {"name": "Work"})
        self.assertIn("id", label)
        lbl_id = label["id"]

        # Get the label
        fetched = get_label("me", lbl_id)
        self.assertEqual(fetched["name"], "Work")

        # Update label name
        update_label("me", lbl_id, {"name": "Work Updated"})
        self.assertEqual(get_label("me", lbl_id)["name"], "Work Updated")

        # Patch the label
        patch_label("me", lbl_id, {"labelListVisibility": "labelHide"})
        self.assertEqual(get_label("me", lbl_id)["labelListVisibility"], "labelHide")

        # List labels
        all_labels = list_labels("me")
        self.assertEqual(len(all_labels["labels"]), 8)

        # Delete label
        delete_label("me", lbl_id)

        # List again to confirm deletion
        all_labels_after_delete = list_labels("me")
        self.assertEqual(len(all_labels_after_delete["labels"]), 7)

    # Custom assert_error_behavior from the second class's context
    def assert_error_behavior(self, func_to_call, expected_exception_type, expected_message, *args, **kwargs):
        with self.assertRaises(expected_exception_type) as cm:
            func_to_call(*args, **kwargs)
        self.assertIn(expected_message.lower(), str(cm.exception).lower())

    # Original test method names from the second class are preserved:
    def test_valid_input_specific_user(self):
        """Test that a valid userId string is accepted and returns data."""
        # reset_db() only creates user "me".
        # This test needs to be adapted or common.reset_db() modified
        # if "test@example.com" with specific labels is expected to exist.
        # Adapting to test "me" after creating a label:
        create_label(userId="me", label={"name": "SpecificUserTestLabel"})
        result = list_labels(userId="me") # Changed from Spaces_delete/list_labels
        self.assertIsInstance(result, dict)
        self.assertIn("labels", result)
        self.assertIsInstance(result["labels"], builtins.list)
        # Should have 7 system labels + 1 created label = 8 total
        self.assertEqual(len(result["labels"]), 8)
        # Check that our created label is in the results
        label_names = [label['name'] for label in result['labels']]
        self.assertIn("SpecificUserTestLabel", label_names)

    def test_valid_input_default_user(self):
        """Test that calling with default userId 'me' is accepted."""
        create_label(userId="me", label={"name": "DefaultUserLabel1"})
        create_label(userId="me", label={"name": "DefaultUserLabel2"})

        result = list_labels() # Changed from Spaces_delete/list_labels
        self.assertIsInstance(result, dict)
        self.assertIn("labels", result)
        self.assertIsInstance(result["labels"], builtins.list)
        # Should have 7 system labels + 2 created labels = 9 total
        self.assertEqual(len(result["labels"]), 9)
        label_names = sorted([label['name'] for label in result['labels']])
        self.assertIn("DefaultUserLabel1", label_names)
        self.assertIn("DefaultUserLabel2", label_names)

    def test_user_with_no_labels(self):
        """Test 'me' (who exists after reset_db) when they have only system labels."""
        result = list_labels(userId="me") # Changed from Spaces_delete/list_labels
        self.assertIsInstance(result, dict)
        self.assertIn("labels", result)
        self.assertIsInstance(result["labels"], builtins.list)
        # Should have 7 system labels (INBOX, UNREAD, IMPORTANT, SENT, DRAFT, TRASH, SPAM)
        self.assertEqual(len(result["labels"]), 7)
        # Verify all labels are system labels
        for label in result["labels"]:
            self.assertEqual(label.get("type"), "system")

    def test_invalid_userid_type_integer(self):
        """Test list_labels with an integer userId raises ValueError."""
        self.assert_error_behavior(
            func_to_call=list_labels,
            expected_exception_type=TypeError,
            expected_message="userid must be a string, but got int.",
            userId=123 # type: ignore
        )

    def test_invalid_userid_type_list(self):
        """Test list_labels with a list userId raises TypeError."""
        self.assert_error_behavior(
            func_to_call=list_labels,
            expected_exception_type=TypeError,
            expected_message="userid must be a string, but got list.",
            userId=["me"] # type: ignore
        )

    def test_invalid_userid_type_none(self):
        """Test list_labels with a None userId raises ValueError."""
        self.assert_error_behavior(
            func_to_call=list_labels,
            expected_exception_type=TypeError,
            expected_message="userId must be a string, but got NoneType.",
            userId=None # type: ignore
        )

    def test_non_existent_user_keyerror(self):
        """Test list_labels with a non-existent userId string raises ValueError."""
        self.assert_error_behavior(
            func_to_call=list_labels,
            expected_exception_type=ValueError,
            expected_message="User 'nonexistentuser' does not exist",
            userId="nonexistentuser"
        )
    
    def test_invalid_userid_empty(self):
        """Test list_labels with an empty userId string raises ValueError."""
        self.assert_error_behavior(
            func_to_call=list_labels,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="userId cannot be empty.",
            userId=""
        )
    
    def test_invalid_userid_only_whitespace(self):
        """Test list_labels with an userId string that only contains whitespace raises ValueError."""
        self.assert_error_behavior(
            func_to_call=list_labels,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="userId cannot have only whitespace.",
            userId="   "
        )
    
    def test_invalid_userid_whitespace(self):
        """Test list_labels with an userId string that contains whitespace raises ValueError."""
        self.assert_error_behavior(
            func_to_call=list_labels,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="userId cannot have whitespace.",
            userId="me   "
        )

    def test_create_label_invalid_user_id_type(self):
        self.assert_error_behavior(
            func_to_call=create_label,
            expected_exception_type=TypeError,
            expected_message="userId must be a string.",
            userId=123,
            label={"name": "Test Label"}
        )

    def test_create_label_user_id_only_whitespace(self):
        self.assert_error_behavior(
            func_to_call=create_label,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Argument 'userId' cannot have only whitespace.",
            userId="   ",
            label={"name": "Test Label"}
        )

    def test_create_label_user_id_with_whitespace(self):
        self.assert_error_behavior(
            func_to_call=create_label,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Argument 'userId' cannot have whitespace.",
            userId="user id",
            label={"name": "Test Label"}
        )

    def test_create_label_label_not_dict(self):
        self.assert_error_behavior(
            func_to_call=create_label,
            expected_exception_type=TypeError,
            expected_message="label must be a dictionary.",
            userId="me",
            label="not a dict"
        )

    def test_delete_label_user_id_only_whitespace(self):
        self.assert_error_behavior(
            func_to_call=delete_label,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Argument 'userId' cannot have only whitespace.",
            userId="   ",
            id="label_id"
        )

    def test_delete_label_user_id_with_whitespace(self):
        self.assert_error_behavior(
            func_to_call=delete_label,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Argument 'userId' cannot have whitespace.",
            userId="user id",
            id="label_id"
        )

    def test_delete_label_id_with_whitespace(self):
        self.assert_error_behavior(
            func_to_call=delete_label,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Argument 'id' cannot have whitespace.",
            userId="me",
            id="label id"
        )

    def test_get_label_valid_input(self):
        """Test get_label with valid userId and id returns the correct label."""
        # Create a label first
        label = create_label("me", {"name": "TestLabel"})
        label_id = label["id"]
        
        # Get the label
        result = get_label("me", label_id)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["id"], label_id)
        self.assertEqual(result["name"], "TestLabel")

    def test_get_label_default_parameters(self):
        """Test get_label with default parameters."""
        result = get_label()
        self.assertIsNone(result)  # Should return None for empty id

    def test_get_label_non_existent_id(self):
        """Test get_label with non-existent label id returns None."""
        result = get_label("me", "non_existent_id")
        self.assertIsNone(result)

    def test_get_label_empty_id(self):
        """Test get_label with empty id returns None."""
        result = get_label("me", "")
        self.assertIsNone(result)

    def test_get_label_invalid_userid_type_integer(self):
        """Test get_label with integer userId raises TypeError."""
        self.assert_error_behavior(
            func_to_call=get_label,
            expected_exception_type=TypeError,
            expected_message="userId must be a string, but got int.",
            userId=123,
            id="test_id"
        )

    def test_get_label_invalid_userid_type_none(self):
        """Test get_label with None userId raises TypeError."""
        self.assert_error_behavior(
            func_to_call=get_label,
            expected_exception_type=TypeError,
            expected_message="userId must be a string, but got NoneType.",
            userId=None,
            id="test_id"
        )

    def test_get_label_invalid_userid_type_list(self):
        """Test get_label with list userId raises TypeError."""
        self.assert_error_behavior(
            func_to_call=get_label,
            expected_exception_type=TypeError,
            expected_message="userId must be a string, but got list.",
            userId=["me"],
            id="test_id"
        )

    def test_get_label_invalid_id_type_integer(self):
        """Test get_label with integer id raises TypeError."""
        self.assert_error_behavior(
            func_to_call=get_label,
            expected_exception_type=TypeError,
            expected_message="id must be a string, but got int.",
            userId="me",
            id=123
        )

    def test_get_label_invalid_id_type_none(self):
        """Test get_label with None id raises TypeError."""
        self.assert_error_behavior(
            func_to_call=get_label,
            expected_exception_type=TypeError,
            expected_message="id must be a string, but got NoneType.",
            userId="me",
            id=None
        )

    def test_get_label_invalid_id_type_list(self):
        """Test get_label with list id raises TypeError."""
        self.assert_error_behavior(
            func_to_call=get_label,
            expected_exception_type=TypeError,
            expected_message="id must be a string, but got list.",
            userId="me",
            id=["test_id"]
        )

    def test_get_label_userid_only_whitespace(self):
        """Test get_label with userId containing only whitespace raises ValidationError."""
        self.assert_error_behavior(
            func_to_call=get_label,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Argument 'userId' cannot have only whitespace.",
            userId="   ",
            id="test_id"
        )

    def test_get_label_userid_with_whitespace(self):
        """Test get_label with userId containing whitespace raises ValidationError."""
        self.assert_error_behavior(
            func_to_call=get_label,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Argument 'userId' cannot have whitespace.",
            userId="user id",
            id="test_id"
        )

    def test_get_label_userid_with_leading_whitespace(self):
        """Test get_label with userId containing leading whitespace raises ValidationError."""
        self.assert_error_behavior(
            func_to_call=get_label,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Argument 'userId' cannot have whitespace.",
            userId=" me",
            id="test_id"
        )

    def test_get_label_userid_with_trailing_whitespace(self):
        """Test get_label with userId containing trailing whitespace raises ValidationError."""
        self.assert_error_behavior(
            func_to_call=get_label,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Argument 'userId' cannot have whitespace.",
            userId="me ",
            id="test_id"
        )

    def test_get_label_id_with_whitespace(self):
        """Test get_label with id containing whitespace raises ValidationError."""
        self.assert_error_behavior(
            func_to_call=get_label,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Argument 'id' cannot have whitespace.",
            userId="me",
            id="test id"
        )

    def test_get_label_id_with_leading_whitespace(self):
        """Test get_label with id containing leading whitespace raises ValidationError."""
        self.assert_error_behavior(
            func_to_call=get_label,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Argument 'id' cannot have whitespace.",
            userId="me",
            id=" test_id"
        )

    def test_get_label_id_with_trailing_whitespace(self):
        """Test get_label with id containing trailing whitespace raises ValidationError."""
        self.assert_error_behavior(
            func_to_call=get_label,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Argument 'id' cannot have whitespace.",
            userId="me",
            id="test_id "
        )

    def test_get_label_id_with_tabs_and_spaces(self):
        """Test get_label with id containing tabs and spaces raises ValidationError."""
        self.assert_error_behavior(
            func_to_call=get_label,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Argument 'id' cannot have whitespace.",
            userId="me",
            id="test\tid"
        )

    def test_get_label_non_existent_user(self):
        """Test get_label with non-existent userId raises ValueError."""
        self.assert_error_behavior(
            func_to_call=get_label,
            expected_exception_type=ValueError,
            expected_message="User 'nonexistentuser' does not exist",
            userId="nonexistentuser",
            id="test_id"
        )

    def test_get_label_valid_complex_scenario(self):
        """Test get_label in a complex scenario with multiple labels."""
        # Create multiple labels
        label1 = create_label("me", {"name": "Work", "messageListVisibility": "show"})
        label2 = create_label("me", {"name": "Personal", "messageListVisibility": "hide"})
        
        # Get each label and verify
        result1 = get_label("me", label1["id"])
        result2 = get_label("me", label2["id"])
        
        self.assertEqual(result1["name"], "Work")
        self.assertEqual(result1["messageListVisibility"], "show")
        self.assertEqual(result2["name"], "Personal")
        self.assertEqual(result2["messageListVisibility"], "hide")

    # ===== COMPREHENSIVE UPDATE METHOD TEST COVERAGE =====

    # --- Input Validation Tests for userId ---
    
    def test_update_invalid_userid_type_integer(self):
        """Test update_label with integer userId raises TypeError."""
        label = create_label("me", {"name": "TestLabel"})
        self.assert_error_behavior(
            func_to_call=update_label,
            expected_exception_type=TypeError,
            expected_message="userId must be a string.",
            userId=123,
            id=label["id"],
            label={"name": "Updated"}
        )

    def test_update_invalid_userid_type_none(self):
        """Test update_label with None userId raises TypeError."""
        label = create_label("me", {"name": "TestLabel"})
        self.assert_error_behavior(
            func_to_call=update_label,
            expected_exception_type=TypeError,
            expected_message="userId must be a string.",
            userId=None,
            id=label["id"],
            label={"name": "Updated"}
        )

    def test_update_invalid_userid_type_list(self):
        """Test update_label with list userId raises TypeError."""
        label = create_label("me", {"name": "TestLabel"})
        self.assert_error_behavior(
            func_to_call=update_label,
            expected_exception_type=TypeError,
            expected_message="userId must be a string.",
            userId=["me"],
            id=label["id"],
            label={"name": "Updated"}
        )

    def test_update_userid_empty_string(self):
        """Test update_label with empty userId string raises ValueError."""
        label = create_label("me", {"name": "TestLabel"})
        self.assert_error_behavior(
            func_to_call=update_label,
            expected_exception_type=ValueError,
            expected_message="userId cannot be empty or contain only whitespace.",
            userId="",
            id=label["id"],
            label={"name": "Updated"}
        )

    def test_update_userid_whitespace_only(self):
        """Test update_label with whitespace-only userId raises ValueError."""
        label = create_label("me", {"name": "TestLabel"})
        self.assert_error_behavior(
            func_to_call=update_label,
            expected_exception_type=ValueError,
            expected_message="userId cannot be empty or contain only whitespace.",
            userId="   ",
            id=label["id"],
            label={"name": "Updated"}
        )

    def test_update_userid_contains_whitespace(self):
        """Test update_label with userId containing whitespace raises ValueError."""
        label = create_label("me", {"name": "TestLabel"})
        self.assert_error_behavior(
            func_to_call=update_label,
            expected_exception_type=ValueError,
            expected_message="userId cannot contain whitespace.",
            userId="user id",
            id=label["id"],
            label={"name": "Updated"}
        )

    # --- Input Validation Tests for id ---

    def test_update_invalid_id_type_integer(self):
        """Test update_label with integer id raises TypeError."""
        self.assert_error_behavior(
            func_to_call=update_label,
            expected_exception_type=TypeError,
            expected_message="id must be a string.",
            userId="me",
            id=123,
            label={"name": "Updated"}
        )

    def test_update_invalid_id_type_none(self):
        """Test update_label with None id raises TypeError."""
        self.assert_error_behavior(
            func_to_call=update_label,
            expected_exception_type=TypeError,
            expected_message="id must be a string.",
            userId="me",
            id=None,
            label={"name": "Updated"}
        )

    def test_update_invalid_id_type_list(self):
        """Test update_label with list id raises TypeError."""
        self.assert_error_behavior(
            func_to_call=update_label,
            expected_exception_type=TypeError,
            expected_message="id must be a string.",
            userId="me",
            id=["label_id"],
            label={"name": "Updated"}
        )

    def test_update_id_empty_string(self):
        """Test update_label with empty id string raises ValueError."""
        self.assert_error_behavior(
            func_to_call=update_label,
            expected_exception_type=ValueError,
            expected_message="id cannot be empty or contain only whitespace.",
            userId="me",
            id="",
            label={"name": "Updated"}
        )

    def test_update_id_whitespace_only(self):
        """Test update_label with whitespace-only id raises ValueError."""
        self.assert_error_behavior(
            func_to_call=update_label,
            expected_exception_type=ValueError,
            expected_message="id cannot be empty or contain only whitespace.",
            userId="me",
            id="   ",
            label={"name": "Updated"}
        )

    def test_update_id_contains_whitespace(self):
        """Test update_label with id containing whitespace raises ValueError."""
        self.assert_error_behavior(
            func_to_call=update_label,
            expected_exception_type=ValueError,
            expected_message="id cannot contain whitespace.",
            userId="me",
            id="label id",
            label={"name": "Updated"}
        )

    # --- Input Validation Tests for label parameter ---

    def test_update_invalid_label_type_string(self):
        """Test update_label with string label raises TypeError."""
        label = create_label("me", {"name": "TestLabel"})
        self.assert_error_behavior(
            func_to_call=update_label,
            expected_exception_type=TypeError,
            expected_message="label must be a dictionary when provided.",
            userId="me",
            id=label["id"],
            label="not a dictionary"
        )

    def test_update_invalid_label_type_integer(self):
        """Test update_label with integer label raises TypeError."""
        label = create_label("me", {"name": "TestLabel"})
        self.assert_error_behavior(
            func_to_call=update_label,
            expected_exception_type=TypeError,
            expected_message="label must be a dictionary when provided.",
            userId="me",
            id=label["id"],
            label=123
        )

    def test_update_invalid_label_type_list(self):
        """Test update_label with list label raises TypeError."""
        label = create_label("me", {"name": "TestLabel"})
        self.assert_error_behavior(
            func_to_call=update_label,
            expected_exception_type=TypeError,
            expected_message="label must be a dictionary when provided.",
            userId="me",
            id=label["id"],
            label=["name", "Updated"]
        )

    # --- User and Label Existence Tests ---

    def test_update_non_existent_user(self):
        """Test update_label with non-existent userId raises ValueError."""
        self.assert_error_behavior(
            func_to_call=update_label,
            expected_exception_type=ValueError,
            expected_message="User 'nonexistentuser' does not exist",
            userId="nonexistentuser",
            id="label_id",
            label={"name": "Updated"}
        )

    def test_update_non_existent_label(self):
        """Test update_label with non-existent label id raises NotFoundError."""
        self.assert_error_behavior(
            func_to_call=update_label,
            expected_exception_type=custom_errors.NotFoundError,
            expected_message="Label with id 'non_existent_label' not found.",
            userId="me",
            id="non_existent_label",
            label={"name": "Updated"}
        )

    # --- Pydantic Validation Tests ---

    def test_update_label_invalid_name_type(self):
        """Test update_label with invalid name type raises ValidationError."""
        label = create_label("me", {"name": "TestLabel"})
        self.assert_error_behavior(
            func_to_call=update_label,
            expected_exception_type=ValidationError,
            expected_message="Input should be a valid string",
            userId="me",
            id=label["id"],
            label={"name": 123}
        )

    def test_update_label_invalid_message_list_visibility(self):
        """Test update_label with invalid messageListVisibility raises ValidationError."""
        label = create_label("me", {"name": "TestLabel"})
        self.assert_error_behavior(
            func_to_call=update_label,
            expected_exception_type=ValidationError,
            expected_message="Input should be 'show' or 'hide'",
            userId="me",
            id=label["id"],
            label={"messageListVisibility": "invalid_option"}
        )

    def test_update_label_invalid_label_list_visibility(self):
        """Test update_label with invalid labelListVisibility raises ValidationError."""
        label = create_label("me", {"name": "TestLabel"})
        self.assert_error_behavior(
            func_to_call=update_label,
            expected_exception_type=ValidationError,
            expected_message="Input should be 'labelShow', 'labelShowIfUnread' or 'labelHide'",
            userId="me",
            id=label["id"],
            label={"labelListVisibility": "invalid_option"}
        )

    def test_update_label_invalid_type(self):
        """Test update_label with invalid type field raises ValidationError."""
        label = create_label("me", {"name": "TestLabel"})
        self.assert_error_behavior(
            func_to_call=update_label,
            expected_exception_type=ValidationError,
            expected_message="Input should be 'user' or 'system'",
            userId="me",
            id=label["id"],
            label={"type": "admin"}
        )

    def test_update_label_invalid_color_type(self):
        """Test update_label with invalid color type raises ValidationError."""
        label = create_label("me", {"name": "TestLabel"})
        self.assert_error_behavior(
            func_to_call=update_label,
            expected_exception_type=ValidationError,
            expected_message="Input should be a valid dictionary",
            userId="me",
            id=label["id"],
            label={"color": "not_a_dict"}
        )

    def test_update_label_color_missing_text_color(self):
        """Test update_label with color missing textColor raises ValidationError."""
        label = create_label("me", {"name": "TestLabel"})
        self.assert_error_behavior(
            func_to_call=update_label,
            expected_exception_type=ValidationError,
            expected_message="Field required",
            userId="me",
            id=label["id"],
            label={"color": {"backgroundColor": "#FF0000"}}
        )

    def test_update_label_color_missing_background_color(self):
        """Test update_label with color missing backgroundColor raises ValidationError."""
        label = create_label("me", {"name": "TestLabel"})
        self.assert_error_behavior(
            func_to_call=update_label,
            expected_exception_type=ValidationError,
            expected_message="Field required",
            userId="me",
            id=label["id"],
            label={"color": {"textColor": "#FFFFFF"}}
        )

    def test_update_label_color_invalid_text_color_type(self):
        """Test update_label with invalid textColor type raises ValidationError."""
        label = create_label("me", {"name": "TestLabel"})
        self.assert_error_behavior(
            func_to_call=update_label,
            expected_exception_type=ValidationError,
            expected_message="Input should be a valid string",
            userId="me",
            id=label["id"],
            label={"color": {"textColor": 123, "backgroundColor": "#FF0000"}}
        )

    def test_update_label_color_invalid_background_color_format(self):
        """Test update_label with invalid backgroundColor format raises ValidationError."""
        label = create_label("me", {"name": "TestLabel"})
        self.assert_error_behavior(
            func_to_call=update_label,
            expected_exception_type=ValidationError,
            expected_message="String should match pattern",
            userId="me",
            id=label["id"],
            label={"color": {"textColor": "#FFFFFF", "backgroundColor": "invalid_hex"}}
        )

    # --- Business Logic Tests ---

    def test_update_label_with_none_returns_existing(self):
        """Test update_label with None label returns existing label unchanged."""
        original_label = create_label("me", {"name": "TestLabel"})
        label_id = original_label["id"]
        
        result = update_label("me", label_id, None)
        
        self.assertEqual(result, original_label)
        self.assertEqual(result["name"], "TestLabel")

    def test_update_label_name_only(self):
        """Test update_label updating only the name field."""
        label = create_label("me", {"name": "OriginalName"})
        label_id = label["id"]
        
        result = update_label("me", label_id, {"name": "UpdatedName"})
        
        self.assertEqual(result["name"], "UpdatedName")
        self.assertEqual(result["id"], label_id)
        # Verify other fields remain unchanged
        self.assertEqual(result["messageListVisibility"], "show")
        self.assertEqual(result["labelListVisibility"], "labelShow")
        self.assertEqual(result["type"], "user")

    def test_update_label_all_fields(self):
        """Test update_label updating all fields simultaneously."""
        label = create_label("me", {"name": "OriginalName"})
        label_id = label["id"]
        
        update_data = {
            "name": "UpdatedName",
            "messageListVisibility": "hide",
            "labelListVisibility": "labelHide", 
            "type": "user",
            "color": {"textColor": "#000000", "backgroundColor": "#FFFFFF"}
        }
        
        result = update_label("me", label_id, update_data)
        
        self.assertEqual(result["name"], "UpdatedName")
        self.assertEqual(result["messageListVisibility"], "hide")
        self.assertEqual(result["labelListVisibility"], "labelHide")
        self.assertEqual(result["type"], "user")
        self.assertEqual(result["color"], {"textColor": "#000000", "backgroundColor": "#FFFFFF"})
        # System fields should be preserved
        self.assertEqual(result["id"], label_id)
        self.assertEqual(result["messagesTotal"], 0)
        self.assertEqual(result["messagesUnread"], 0)
        self.assertEqual(result["threadsTotal"], 0)
        self.assertEqual(result["threadsUnread"], 0)

    def test_update_label_message_list_visibility_options(self):
        """Test update_label with all valid messageListVisibility options."""
        label = create_label("me", {"name": "TestLabel"})
        label_id = label["id"]
        
        # Test 'show'
        result = update_label("me", label_id, {"messageListVisibility": "show"})
        self.assertEqual(result["messageListVisibility"], "show")
        
        # Test 'hide'
        result = update_label("me", label_id, {"messageListVisibility": "hide"})
        self.assertEqual(result["messageListVisibility"], "hide")

    def test_update_label_list_visibility_options(self):
        """Test update_label with all valid labelListVisibility options."""
        label = create_label("me", {"name": "TestLabel"})
        label_id = label["id"]
        
        # Test 'labelShow'
        result = update_label("me", label_id, {"labelListVisibility": "labelShow"})
        self.assertEqual(result["labelListVisibility"], "labelShow")
        
        # Test 'labelShowIfUnread'
        result = update_label("me", label_id, {"labelListVisibility": "labelShowIfUnread"})
        self.assertEqual(result["labelListVisibility"], "labelShowIfUnread")
        
        # Test 'labelHide'
        result = update_label("me", label_id, {"labelListVisibility": "labelHide"})
        self.assertEqual(result["labelListVisibility"], "labelHide")

    def test_update_label_type_options(self):
        """Test update_label with all valid type options."""
        label = create_label("me", {"name": "TestLabel"})
        label_id = label["id"]
        
        # Test 'user'
        result = update_label("me", label_id, {"type": "user"})
        self.assertEqual(result["type"], "user")
        
        # Test 'system'
        result = update_label("me", label_id, {"type": "system"})
        self.assertEqual(result["type"], "system")

    def test_update_label_color_valid(self):
        """Test update_label with valid color object."""
        label = create_label("me", {"name": "TestLabel"})
        label_id = label["id"]
        
        color_data = {"textColor": "#FF0000", "backgroundColor": "#00FF00"}
        result = update_label("me", label_id, {"color": color_data})
        
        self.assertEqual(result["color"], color_data)

    def test_update_label_preserves_system_fields(self):
        """Test update_label preserves system fields like counts."""
        from ..SimulationEngine.db import DB
        
        # Create label and modify its system fields directly
        label = create_label("me", {"name": "TestLabel"})
        label_id = label["id"]
        
        # Simulate system updating counts
        DB["users"]["me"]["labels"][label_id]["messagesTotal"] = 5
        DB["users"]["me"]["labels"][label_id]["messagesUnread"] = 2
        DB["users"]["me"]["labels"][label_id]["threadsTotal"] = 3
        DB["users"]["me"]["labels"][label_id]["threadsUnread"] = 1
        
        # Update the label
        result = update_label("me", label_id, {"name": "UpdatedName"})
        
        # Verify system fields are preserved
        self.assertEqual(result["messagesTotal"], 5)
        self.assertEqual(result["messagesUnread"], 2)
        self.assertEqual(result["threadsTotal"], 3)
        self.assertEqual(result["threadsUnread"], 1)
        self.assertEqual(result["name"], "UpdatedName")

    def test_update_label_name_none_preserves_existing(self):
        """Test update_label with name=None preserves existing name."""
        label = create_label("me", {"name": "OriginalName"})
        label_id = label["id"]
        
        result = update_label("me", label_id, {"name": None, "messageListVisibility": "hide"})
        
        self.assertEqual(result["name"], "OriginalName")  # Should preserve existing name
        self.assertEqual(result["messageListVisibility"], "hide")  # Should update other fields

    def test_update_label_empty_dictionary(self):
        """Test update_label with empty dictionary uses defaults."""
        label = create_label("me", {"name": "TestLabel", "messageListVisibility": "hide"})
        label_id = label["id"]
        
        result = update_label("me", label_id, {})
        
        # Should use defaults from LabelInputModel
        self.assertEqual(result["name"], "TestLabel")  # Preserved since name was None in empty dict
        self.assertEqual(result["messageListVisibility"], "show")  # Default value
        self.assertEqual(result["labelListVisibility"], "labelShow")  # Default value
        self.assertEqual(result["type"], "user")  # Default value

    def test_update_label_color_handling_existing_empty_dict(self):
        """Test update_label color handling when existing label has empty dict color."""
        label = create_label("me", {"name": "TestLabel"})  # Creates with color: {}
        label_id = label["id"]
        
        result = update_label("me", label_id, {"name": "Updated"})
        
        self.assertEqual(result["color"], {})  # Should preserve existing empty dict

    def test_update_label_database_persistence(self):
        """Test update_label actually persists changes to database."""
        from ..SimulationEngine.db import DB
        
        label = create_label("me", {"name": "OriginalName"})
        label_id = label["id"]
        
        update_label("me", label_id, {"name": "UpdatedName"})
        
        # Verify changes are persisted in database
        db_label = DB["users"]["me"]["labels"][label_id]
        self.assertEqual(db_label["name"], "UpdatedName")

    def test_update_label_default_user_me(self):
        """Test update_label works with default userId 'me'."""
        label = create_label()  # Uses default "me"
        label_id = label["id"]
        
        result = update_label(id=label_id, label={"name": "UpdatedWithDefaults"})
        
        self.assertEqual(result["name"], "UpdatedWithDefaults")

    def test_update_label_default_empty_id(self):
        """Test update_label with default empty id raises ValueError."""
        self.assert_error_behavior(
            func_to_call=update_label,
            expected_exception_type=ValueError,
            expected_message="id cannot be empty or contain only whitespace.",
            label={"name": "Updated"}
        )

    def test_update_system_label_name_converts_to_uppercase(self):
        """Test that updating a system label's name automatically converts it to uppercase."""
        # First create a system label (using the DB directly since we can't create system labels via API)
        test_label_id = "TEST_SYSTEM"
        DB["users"]["me"]["labels"][test_label_id] = {
            "id": test_label_id,
            "name": "TEST_SYSTEM",
            "type": "system",
            "labelListVisibility": "labelShow",
            "messageListVisibility": "show"
        }
        
        # Try to update with lowercase name
        updated = update_label("me", test_label_id, {
            "name": "test_system",
            "type": "system"  # Must keep type as system
        })
        
        # Verify name was converted to uppercase
        self.assertEqual(updated["name"], "TEST_SYSTEM")
        # Verify it's persisted in DB
        self.assertEqual(DB["users"]["me"]["labels"][test_label_id]["name"], "TEST_SYSTEM")

    def test_update_system_label_name_mixed_case_converts_to_uppercase(self):
        """Test that updating a system label's name with mixed case converts to uppercase."""
        # First create a system label
        test_label_id = "TEST_MIXED"
        DB["users"]["me"]["labels"][test_label_id] = {
            "id": test_label_id,
            "name": "TEST_MIXED",
            "type": "system",
            "labelListVisibility": "labelShow",
            "messageListVisibility": "show"
        }
        
        # Try to update with mixed case name
        updated = update_label("me", test_label_id, {
            "name": "Test_Mixed",
            "type": "system"
        })
        
        # Verify name was converted to uppercase
        self.assertEqual(updated["name"], "TEST_MIXED")
        # Verify it's persisted in DB
        self.assertEqual(DB["users"]["me"]["labels"][test_label_id]["name"], "TEST_MIXED")

    def test_update_system_label_preserves_uppercase_name(self):
        """Test that updating a system label with an already uppercase name keeps it uppercase."""
        # First create a system label
        test_label_id = "TEST_UPPER"
        DB["users"]["me"]["labels"][test_label_id] = {
            "id": test_label_id,
            "name": "TEST_UPPER",
            "type": "system",
            "labelListVisibility": "labelShow",
            "messageListVisibility": "show"
        }
        
        # Update with already uppercase name
        updated = update_label("me", test_label_id, {
            "name": "TEST_UPPER",
            "type": "system"
        })
        
        # Verify name remained uppercase
        self.assertEqual(updated["name"], "TEST_UPPER")
        # Verify it's persisted in DB
        self.assertEqual(DB["users"]["me"]["labels"][test_label_id]["name"], "TEST_UPPER")

    def test_update_user_label_preserves_case(self):
        """Test that updating a user label preserves the original case."""
        # Create a user label
        label = create_label("me", {
            "name": "Test_User_Label",
            "type": "user"
        })
        
        # Update the label with mixed case
        updated = update_label("me", label["id"], {
            "name": "New_Test_Label",
            "type": "user"
        })
        
        # Verify case was preserved
        self.assertEqual(updated["name"], "New_Test_Label")
        # Verify it's persisted in DB
        self.assertEqual(DB["users"]["me"]["labels"][label["id"]]["name"], "New_Test_Label")

    def test_update_system_label_type_change_not_allowed(self):
        """Test that attempting to change a system label's type to 'user' raises an error."""
        # First create a system label
        test_label_id = "TEST_SYSTEM_TYPE"
        DB["users"]["me"]["labels"][test_label_id] = {
            "id": test_label_id,
            "name": "TEST_SYSTEM_TYPE",
            "type": "system",
            "labelListVisibility": "labelShow",
            "messageListVisibility": "show"
        }
        
        # Try to change type to user
        with self.assertRaises(custom_errors.ValidationError) as cm:
            update_label("me", test_label_id, {
                "name": "TEST_SYSTEM_TYPE",
                "type": "user"
            })
        
        self.assertIn("Cannot change type of system label", str(cm.exception))
        # Verify type remained system in DB
        self.assertEqual(DB["users"]["me"]["labels"][test_label_id]["type"], "system")

if __name__ == "__main__":
    unittest.main()
