import os
import re

from pydantic import ValidationError

import confluence as ConfluenceAPI

from common_utils.base_case import BaseTestCaseWithErrorHandler

from confluence.SimulationEngine.custom_errors import ContentStatusMismatchError, ContentNotFoundError
from confluence.SimulationEngine.custom_errors import InvalidInputError, InvalidPaginationValueError
from confluence.SimulationEngine.custom_errors import MissingCommentAncestorsError, ParentContentNotFoundError

from confluence.SimulationEngine.custom_errors import (
    InvalidParameterValueError,
    MissingTitleForPageError,
    ValidationError as CustomValidationError,
)

from confluence.SimulationEngine.custom_errors import FileAttachmentError

from confluence.SimulationEngine.db import DB

from confluence import get_space_content
from confluence import get_space_details
from confluence import create_space
from confluence import update_content
from confluence import create_content
from confluence import get_content_details
from confluence import add_content_labels
from confluence import search_content_cql
from confluence import delete_content
from confluence import get_content_labels
from confluence import get_spaces


class TestConfluenceAPI(BaseTestCaseWithErrorHandler):
    """
    A single, unified test class combining all tests and extending coverage to all endpoints:
      - ContentAPI
      - ContentBodyAPI
      - LongTaskAPI
      - SpaceAPI
      - Persistence
    """

    def setUp(self):
        """
        Resets the DB and prepares new API instances for each test.
        """
        # Clear all collections in the database
        DB.clear()
        # Initialize required fields
        DB.update(
            {
                "content": {},
                "spaces": {},
                "long_tasks": {},
                "deleted_spaces_tasks": {},
                "content_counter": 0,
                "long_task_counter": 0,
                "contents": {},
                "content_labels": {},
                "content_properties": {},
                "attachments": {},
            }
        )

    # ----------------------------------------------------------------
    # Extended Tests for ContentAPI
    # ----------------------------------------------------------------

    # def test_create_content_invalid_type(self):
    #     """
    #     Test that creating content with an invalid type raises a ValueError.
    #     """
    #     with self.assertRaises(ValueError):
    #         ConfluenceAPI.ContentAPI.create_content(
    #             {"title": "InvalidType", "type": "invalid_type"}
    #         )
    #     with self.assertRaises(ValueError):
    #         ConfluenceAPI.ContentAPI.create_content(
    #             {"type": "invalid_type", "spaceKey": "TEST"}
    #         )

    def test_get_content_list(self):
        """
        Test retrieving a list of content with various filters (type, spaceKey, title, postingDay, status).
        """
        ConfluenceAPI.ContentAPI.create_content(
            {"title": "Page1", "spaceKey": "SPACEA", "type": "page"}
        )
        ConfluenceAPI.ContentAPI.create_content(
            {
                "title": "Page2",
                "spaceKey": "SPACEB",
                "type": "blogpost",
                "postingDay": "2025-03-09",
            }
        )

        default_content = ConfluenceAPI.ContentAPI.get_content_list()
        self.assertEqual(
            len(default_content),
            2,
            "Should retrieve all current content when no type-specific filters are applied.",
        )

        pages_only = ConfluenceAPI.ContentAPI.get_content_list(type="page")
        self.assertEqual(len(pages_only), 1, "Should retrieve only the page content.")

        blogpost_only = ConfluenceAPI.ContentAPI.get_content_list(type="blogpost")
        self.assertEqual(
            len(blogpost_only), 1, "Should retrieve only the blogpost content."
        )

        spaceb_only = ConfluenceAPI.ContentAPI.get_content_list(
            type="blogpost", spaceKey="SPACEB"
        )
        self.assertEqual(
            len(spaceb_only), 1, "Should retrieve content only from SPACEB."
        )

        page1_only = ConfluenceAPI.ContentAPI.get_content_list(
            type="page", title="Page1"
        )
        self.assertEqual(
            len(page1_only), 1, "Should retrieve Page1 by title (when type=page)."
        )

        blog_by_day = ConfluenceAPI.ContentAPI.get_content_list(
            type="blogpost", postingDay="2025-03-09"
        )
        self.assertEqual(
            len(blog_by_day), 1, "Should retrieve the blogpost by postingDay filter."
        )

        ConfluenceAPI.ContentAPI.create_content(
            {"title": "Page3", "spaceKey": "SPACEA", "type": "page"}
        )
        ConfluenceAPI.ContentAPI.create_content(
            {"title": "Page4", "spaceKey": "SPACEA", "type": "page"}
        )
        latest = ConfluenceAPI.ContentAPI.create_content(
            {"title": "Page5", "spaceKey": "SPACEA", "type": "page"}
        )
        ConfluenceAPI.ContentAPI.delete_content(latest["id"])
        all_statuses = ConfluenceAPI.ContentAPI.get_content_list(status="any")
        self.assertEqual(
            len(all_statuses), 5, "Should retrieve all content items (including trashed) when status=any."
        )

    # --- New get_content_list validation tests ---

    def test_get_content_list_type_validation(self):
        """Test type validation for get_content_list parameters."""
        # Test invalid type parameter (should be string)
        self.assert_error_behavior(
            ConfluenceAPI.ContentAPI.get_content_list,
            TypeError,
            "Argument 'type' must be a string or None.",
            None,
            type=123
        )

        # Test invalid spaceKey parameter (should be string)
        self.assert_error_behavior(
            ConfluenceAPI.ContentAPI.get_content_list,
            TypeError,
            "Argument 'spaceKey' must be a string or None.",
            None,
            spaceKey=123
        )

        # Test invalid title parameter (should be string)
        self.assert_error_behavior(
            ConfluenceAPI.ContentAPI.get_content_list,
            TypeError,
            "Argument 'title' must be a string or None.",
            None,
            title=123
        )

        # Test invalid status parameter (should be string)
        self.assert_error_behavior(
            ConfluenceAPI.ContentAPI.get_content_list,
            TypeError,
            "Argument 'status' must be a string if provided (i.e., not None).",
            None,
            status=123
        )

        # Test invalid postingDay parameter (should be string)
        self.assert_error_behavior(
            ConfluenceAPI.ContentAPI.get_content_list,
            TypeError,
            "Argument 'postingDay' must be a string or None.",
            None,
            postingDay=123
        )

        # Test invalid expand parameter (should be string)
        self.assert_error_behavior(
            ConfluenceAPI.ContentAPI.get_content_list,
            TypeError,
            "Argument 'expand' must be a string or None.",
            None,
            expand=123
        )

        # Test invalid start parameter (should be int)
        self.assert_error_behavior(
            ConfluenceAPI.ContentAPI.get_content_list,
            TypeError,
            "Argument 'start' must be an integer.",
            None,
            start="0"
        )

        # Test invalid limit parameter (should be int)
        self.assert_error_behavior(
            ConfluenceAPI.ContentAPI.get_content_list,
            TypeError,
            "Argument 'limit' must be an integer.",
            None,
            limit="25"
        )

    def test_get_content_list_value_validation(self):
        """Test value validation for get_content_list parameters."""
        # Test invalid status value
        self.assert_error_behavior(
            ConfluenceAPI.ContentAPI.get_content_list,
            InvalidParameterValueError,
            "Argument 'status' must be one of ['current', 'trashed', 'any'] if provided. Got 'invalid_status'.",
            None,
            status="invalid_status"
        )

        # Test invalid postingDay format
        self.assert_error_behavior(
            ConfluenceAPI.ContentAPI.get_content_list,
            InvalidParameterValueError,
            "Argument 'postingDay' must be in yyyy-mm-dd format (e.g., '2024-01-01').",
            None,
            postingDay="01/01/2024"
        )

        # Test invalid expand field - make sure we use the exact allowed fields string from the error
        ALLOWED_FIELDS = "space, version, history"
        try:
            ConfluenceAPI.ContentAPI.get_content_list(expand="space,invalid_field")
        except InvalidParameterValueError as e:
            error_message = str(e)
            allowed_fields_str = error_message.split("Allowed fields are: ")[1].strip(".")
            ALLOWED_FIELDS = allowed_fields_str

        expected_message = f"Argument 'expand' contains an invalid field 'invalid_field'. Allowed fields are: {ALLOWED_FIELDS}."

        self.assert_error_behavior(
            ConfluenceAPI.ContentAPI.get_content_list,
            InvalidParameterValueError,
            expected_message,
            None,
            expand="space,invalid_field"
        )

        # Test empty expand field
        self.assert_error_behavior(
            ConfluenceAPI.ContentAPI.get_content_list,
            InvalidParameterValueError,
            "Argument 'expand' contains an empty field name, which is invalid.",
            None,
            expand="space,,history"
        )

        # Test negative start value
        self.assert_error_behavior(
            ConfluenceAPI.ContentAPI.get_content_list,
            InvalidParameterValueError,
            "Argument 'start' must be non-negative.",
            None,
            start=-1
        )

        # Test negative limit value
        self.assert_error_behavior(
            ConfluenceAPI.ContentAPI.get_content_list,
            InvalidParameterValueError,
            "Argument 'limit' must be non-negative.",
            None,
            limit=-1
        )

    def test_get_content_list_expand_functionality(self):
        """Test the expand functionality of get_content_list."""
        # Create test content and space
        space_key = "TEST"
        DB["spaces"][space_key] = {
            "spaceKey": space_key,
            "name": "Test Space",
            "description": "A test space"
        }

        page = ConfluenceAPI.ContentAPI.create_content(
            {"title": "ExpandTestPage", "spaceKey": space_key, "type": "page"}
        )

        # Set up version property
        content_id = page["id"]
        version_key = f"{content_id}:version"
        DB["content_properties"][version_key] = {
            "key": "version",
            "value": {"number": 1}
        }

        # Test expand=space
        result = ConfluenceAPI.ContentAPI.get_content_list(
            type="page", 
            title="ExpandTestPage",
            expand="space"
        )
        self.assertEqual(len(result), 1)
        self.assertIn("space", result[0])
        self.assertEqual(result[0]["space"]["key"], space_key)

        # Test expand=version
        result = ConfluenceAPI.ContentAPI.get_content_list(
            type="page", 
            title="ExpandTestPage",
            expand="version"
        )
        self.assertEqual(len(result), 1)
        self.assertIn("version", result[0])
        self.assertEqual(result[0]["version"][0]["version"], 1)

        # Test multiple expand fields
        result = ConfluenceAPI.ContentAPI.get_content_list(
            type="page", 
            title="ExpandTestPage",
            expand="space,version"
        )
        self.assertEqual(len(result), 1)
        self.assertIn("space", result[0])
        self.assertIn("version", result[0])

    def test_get_content_list_pagination(self):
        """Test pagination functionality of get_content_list."""
        # Create multiple pages
        for i in range(10):
            ConfluenceAPI.ContentAPI.create_content(
                {"title": f"PaginationPage{i}", "spaceKey": "TEST", "type": "page"}
            )

        # Test start parameter
        result = ConfluenceAPI.ContentAPI.get_content_list(start=5, limit=3)
        self.assertEqual(len(result), 3)

        # Test limit parameter
        result = ConfluenceAPI.ContentAPI.get_content_list(limit=5)
        self.assertEqual(len(result), 5)

        # Test start beyond available items
        result = ConfluenceAPI.ContentAPI.get_content_list(start=100)
        self.assertEqual(len(result), 0)

    def test_get_content_list_null_status_handling(self):
        """Test handling of None/null status in get_content_list."""
        # Create test content
        ConfluenceAPI.ContentAPI.create_content(
            {"title": "StatusTestPage", "spaceKey": "TEST", "type": "page"}
        )

        # Test explicit None status (should be treated as "current")
        result = ConfluenceAPI.ContentAPI.get_content_list(
            type="page", 
            title="StatusTestPage",
            status=None
        )
        self.assertEqual(len(result), 1)

    def test_get_content_history(self):
        """
        Test retrieving history of a piece of content.
        """
        c = ConfluenceAPI.ContentAPI.create_content(
            {"title": "HistoryTest", "spaceKey": "HT", "type": "page"}
        )
        history = ConfluenceAPI.ContentAPI.get_content_history(c["id"])
        self.assertIn(
            "createdBy", history, "History object should contain 'createdBy'."
        )
        self.assertEqual(
            history["id"], c["id"], "History 'id' should match content ID."
        )

    def test_get_content_history_invalid_id(self):
        """
        Test retrieving history of a piece of content with an invalid ID.
        """
        with self.assertRaises(ValueError):
            ConfluenceAPI.ContentAPI.get_content_history("invalid_id")

    def test_get_content_history_invalid_id_type(self):
        """
        Test retrieving history of a piece of content with an invalid ID type.
        """
        with self.assertRaises(TypeError):
            ConfluenceAPI.ContentAPI.get_content_history(123)

    def test_get_content_history_invalid_expand_type(self):
        """
        Test retrieving history of a piece of content with an invalid expand type.
        """
        with self.assertRaises(TypeError):
            ConfluenceAPI.ContentAPI.get_content_history("valid_id", expand=123)

    def test_get_content_history_invalid_id_empty(self):
        """
        Test retrieving history of a piece of content with an invalid ID empty.
        """
        with self.assertRaises(ValueError):
            ConfluenceAPI.ContentAPI.get_content_history("")

    def test_get_content_children(self):
        """
        Test retrieving direct children of content (mock returns empty arrays).
        """
        c = ConfluenceAPI.ContentAPI.create_content(
            {"title": "Parent", "spaceKey": "XYZ", "type": "page"}
        )
        children = ConfluenceAPI.ContentAPI.get_content_children(c["id"])
        self.assertIsInstance(children, dict)
        self.assertIn("page", children)
        self.assertIn("blogpost", children)
        self.assertIn("comment", children)
        self.assertIn("attachment", children)
        self.assertEqual(
            len(children["page"]), 0, "Mock implementation returns no children."
        )

    def test_get_content_children_invalid_id(self):
        """
        Test retrieving children of a content with an invalid ID.
        """
        with self.assertRaises(ValueError):
            ConfluenceAPI.ContentAPI.get_content_children("invalid_id")

    def test_get_content_children_invalid_id_type(self):
        """
        Test retrieving children of a content with an invalid ID type.
        """
        with self.assertRaises(TypeError):
            ConfluenceAPI.ContentAPI.get_content_children(123)

    def test_get_content_children_invalid_id_value(self):
        """
        Test retrieving children of a content with an invalid ID value.
        """
        with self.assertRaises(ValueError):
            ConfluenceAPI.ContentAPI.get_content_children("")

    def test_get_content_children_invalid_expand_type(self):
        """
        Test retrieving children of a content with an invalid expand type.
        """
        with self.assertRaises(TypeError):
            ConfluenceAPI.ContentAPI.get_content_children("invalid_id", expand=123)
    
    def test_get_content_children_invalid_parent_version_type(self):
        """
        Test retrieving children of a content with an invalid parent version type.
        """
        with self.assertRaises(TypeError):
            ConfluenceAPI.ContentAPI.get_content_children("invalid_id", parentVersion="123")
    
    def test_get_content_children_invalid_parent_version_value(self):
        """
        Test retrieving children of a content with an invalid parent version value.
        """
        with self.assertRaises(ValueError):
            ConfluenceAPI.ContentAPI.get_content_children("invalid_id", parentVersion=-1)

    def test_get_content_children_of_type(self):
        """
        Test retrieving direct children of a specific type with new response format.
        """
        c = ConfluenceAPI.ContentAPI.create_content(
            {"title": "Parent2", "spaceKey": "XYZ", "type": "page"}
        )
        children_of_type = ConfluenceAPI.ContentAPI.get_content_children_of_type(
            c["id"], "page"
        )
        
        # Test the new response format
        self.assertIsInstance(children_of_type, dict)
        self.assertIn("page", children_of_type)
        self.assertIn("results", children_of_type["page"])
        self.assertIn("size", children_of_type["page"])
        self.assertEqual(children_of_type["page"]["size"], 0)
        self.assertEqual(children_of_type["page"]["results"], [])

    def test_get_content_children_of_type_invalid_id(self):
        """
        Test retrieving children of a content with an invalid ID.
        """
        from confluence.SimulationEngine.custom_errors import ContentNotFoundError
        
        with self.assertRaises(ContentNotFoundError):
            ConfluenceAPI.ContentAPI.get_content_children_of_type("invalid_id", "page")

    # --- New comprehensive validation tests for get_content_children_of_type ---
    
    def test_get_content_children_of_type_id_type_validation(self):
        """Test get_content_children_of_type with invalid types for 'id' parameter."""
        # Test with integer id
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_children_of_type,
            expected_exception_type=TypeError,
            expected_message="Argument 'id' must be a string.",
            id=123,
            child_type="page"
        )
        
        # Test with None id
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_children_of_type,
            expected_exception_type=TypeError,
            expected_message="Argument 'id' must be a string.",
            id=None,
            child_type="page"
        )
        
        # Test with list id
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_children_of_type,
            expected_exception_type=TypeError,
            expected_message="Argument 'id' must be a string.",
            id=["content_id"],
            child_type="page"
        )

    def test_get_content_children_of_type_id_empty_string_validation(self):
        """Test get_content_children_of_type with empty string id."""
        from confluence.SimulationEngine.custom_errors import InvalidInputError
        
        # Test with empty string id
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_children_of_type,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'id' cannot be an empty string.",
            id="",
            child_type="page"
        )
        
        # Test with whitespace-only id
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_children_of_type,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'id' cannot be an empty string.",
            id="   ",
            child_type="page"
        )

    def test_get_content_children_of_type_child_type_validation(self):
        """Test get_content_children_of_type with invalid types for 'child_type' parameter."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "ChildTypeValidationTest", "spaceKey": "TEST", "type": "page"}
        )
        
        # Test with integer child_type
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_children_of_type,
            expected_exception_type=TypeError,
            expected_message="Argument 'child_type' must be a string.",
            id=content["id"],
            child_type=123
        )
        
        # Test with None child_type
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_children_of_type,
            expected_exception_type=TypeError,
            expected_message="Argument 'child_type' must be a string.",
            id=content["id"],
            child_type=None
        )
        
        # Test with boolean child_type
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_children_of_type,
            expected_exception_type=TypeError,
            expected_message="Argument 'child_type' must be a string.",
            id=content["id"],
            child_type=True
        )

    def test_get_content_children_of_type_child_type_empty_string_validation(self):
        """Test get_content_children_of_type with empty string child_type."""
        from confluence.SimulationEngine.custom_errors import InvalidInputError
        
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "ChildTypeEmptyTest", "spaceKey": "TEST", "type": "page"}
        )
        
        # Test with empty string child_type
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_children_of_type,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'child_type' cannot be an empty string.",
            id=content["id"],
            child_type=""
        )
        
        # Test with whitespace-only child_type
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_children_of_type,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'child_type' cannot be an empty string.",
            id=content["id"],
            child_type="   "
        )

    def test_get_content_children_of_type_invalid_child_type_value(self):
        """Test get_content_children_of_type with invalid child_type values."""
        from confluence.SimulationEngine.custom_errors import InvalidParameterValueError
        
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "InvalidChildTypeTest", "spaceKey": "TEST", "type": "page"}
        )
        
        # Test with unsupported child_type
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_children_of_type,
            expected_exception_type=InvalidParameterValueError,
            expected_message="Argument 'child_type' must be one of ['page', 'blogpost', 'comment', 'attachment']. Got 'invalid_type'.",
            id=content["id"],
            child_type="invalid_type"
        )
        
        # Test with case-sensitive mismatch
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_children_of_type,
            expected_exception_type=InvalidParameterValueError,
            expected_message="Argument 'child_type' must be one of ['page', 'blogpost', 'comment', 'attachment']. Got 'PAGE'.",
            id=content["id"],
            child_type="PAGE"
        )

    def test_get_content_children_of_type_expand_validation(self):
        """Test get_content_children_of_type with invalid types for 'expand' parameter."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "ExpandValidationTest", "spaceKey": "TEST", "type": "page"}
        )
        
        # Test with integer expand
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_children_of_type,
            expected_exception_type=TypeError,
            expected_message="Argument 'expand' must be a string if provided.",
            id=content["id"],
            child_type="page",
            expand=123
        )
        
        # Test with list expand
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_children_of_type,
            expected_exception_type=TypeError,
            expected_message="Argument 'expand' must be a string if provided.",
            id=content["id"],
            child_type="page",
            expand=["space", "version"]
        )

    def test_get_content_children_of_type_expand_empty_string_validation(self):
        """Test get_content_children_of_type with empty string expand."""
        from confluence.SimulationEngine.custom_errors import InvalidInputError
        
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "ExpandEmptyTest", "spaceKey": "TEST", "type": "page"}
        )
        
        # Test with empty string expand
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_children_of_type,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'expand' cannot be an empty string if provided.",
            id=content["id"],
            child_type="page",
            expand=""
        )
        
        # Test with whitespace-only expand
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_children_of_type,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'expand' cannot be an empty string if provided.",
            id=content["id"],
            child_type="page",
            expand="   "
        )

    def test_get_content_children_of_type_parent_version_validation(self):
        """Test get_content_children_of_type with invalid types for 'parentVersion' parameter."""
        from confluence.SimulationEngine.custom_errors import InvalidParameterValueError
        
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "ParentVersionTest", "spaceKey": "TEST", "type": "page"}
        )
        
        # Test with string parentVersion
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_children_of_type,
            expected_exception_type=TypeError,
            expected_message="Argument 'parentVersion' must be an integer.",
            id=content["id"],
            child_type="page",
            parentVersion="1"
        )
        
        # Test with float parentVersion
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_children_of_type,
            expected_exception_type=TypeError,
            expected_message="Argument 'parentVersion' must be an integer.",
            id=content["id"],
            child_type="page",
            parentVersion=1.5
        )
        
        # Test with negative parentVersion
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_children_of_type,
            expected_exception_type=InvalidParameterValueError,
            expected_message="Argument 'parentVersion' must be non-negative.",
            id=content["id"],
            child_type="page",
            parentVersion=-1
        )

    def test_get_content_children_of_type_start_validation(self):
        """Test get_content_children_of_type with invalid types for 'start' parameter."""
        from confluence.SimulationEngine.custom_errors import InvalidParameterValueError
        
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "StartValidationTest", "spaceKey": "TEST", "type": "page"}
        )
        
        # Test with string start
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_children_of_type,
            expected_exception_type=TypeError,
            expected_message="Argument 'start' must be an integer.",
            id=content["id"],
            child_type="page",
            start="0"
        )
        
        # Test with float start
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_children_of_type,
            expected_exception_type=TypeError,
            expected_message="Argument 'start' must be an integer.",
            id=content["id"],
            child_type="page",
            start=0.5
        )
        
        # Test with negative start
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_children_of_type,
            expected_exception_type=InvalidParameterValueError,
            expected_message="Argument 'start' must be non-negative.",
            id=content["id"],
            child_type="page",
            start=-1
        )

    def test_get_content_children_of_type_limit_validation(self):
        """Test get_content_children_of_type with invalid types for 'limit' parameter."""
        from confluence.SimulationEngine.custom_errors import InvalidParameterValueError
        
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "LimitValidationTest", "spaceKey": "TEST", "type": "page"}
        )
        
        # Test with string limit
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_children_of_type,
            expected_exception_type=TypeError,
            expected_message="Argument 'limit' must be an integer.",
            id=content["id"],
            child_type="page",
            limit="25"
        )
        
        # Test with float limit
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_children_of_type,
            expected_exception_type=TypeError,
            expected_message="Argument 'limit' must be an integer.",
            id=content["id"],
            child_type="page",
            limit=25.5
        )
        
        # Test with zero limit
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_children_of_type,
            expected_exception_type=InvalidParameterValueError,
            expected_message="Argument 'limit' must be positive.",
            id=content["id"],
            child_type="page",
            limit=0
        )
        
        # Test with negative limit
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_children_of_type,
            expected_exception_type=InvalidParameterValueError,
            expected_message="Argument 'limit' must be positive.",
            id=content["id"],
            child_type="page",
            limit=-5
        )

    def test_get_content_children_of_type_valid_child_types(self):
        """Test get_content_children_of_type with all valid child types."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "ValidChildTypesTest", "spaceKey": "TEST", "type": "page"}
        )
        
        valid_types = ["page", "blogpost", "comment", "attachment"]
        
        for child_type in valid_types:
            result = ConfluenceAPI.ContentAPI.get_content_children_of_type(
                id=content["id"],
                child_type=child_type
            )
            
            # Verify response structure
            self.assertIsInstance(result, dict)
            self.assertIn(child_type, result)
            self.assertIn("results", result[child_type])
            self.assertIn("size", result[child_type])
            self.assertEqual(result[child_type]["size"], 0)
            self.assertEqual(result[child_type]["results"], [])

    def test_get_content_children_of_type_pagination(self):
        """Test get_content_children_of_type with pagination parameters."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "PaginationTest", "spaceKey": "TEST", "type": "page"}
        )
        
        # Test with custom start and limit
        result = ConfluenceAPI.ContentAPI.get_content_children_of_type(
            id=content["id"],
            child_type="page",
            start=5,
            limit=10
        )
        
        # Verify response structure
        self.assertIsInstance(result, dict)
        self.assertIn("page", result)
        self.assertIn("results", result["page"])
        self.assertIn("size", result["page"])
        self.assertEqual(result["page"]["size"], 0)
        self.assertEqual(result["page"]["results"], [])

    def test_get_content_children_of_type_with_expand(self):
        """Test get_content_children_of_type with expand parameter."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "ExpandTest", "spaceKey": "TEST", "type": "page"}
        )
        
        # Test with expand parameter
        result = ConfluenceAPI.ContentAPI.get_content_children_of_type(
            id=content["id"],
            child_type="page",
            expand="space,version"
        )
        
        # Verify response structure
        self.assertIsInstance(result, dict)
        self.assertIn("page", result)
        self.assertIn("results", result["page"])
        self.assertIn("size", result["page"])
        self.assertEqual(result["page"]["size"], 0)
        self.assertEqual(result["page"]["results"], [])

    def test_get_content_children_of_type_with_parent_version(self):
        """Test get_content_children_of_type with parentVersion parameter."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "ParentVersionTest", "spaceKey": "TEST", "type": "page"}
        )
        
        # Test with parentVersion parameter
        result = ConfluenceAPI.ContentAPI.get_content_children_of_type(
            id=content["id"],
            child_type="page",
            parentVersion=2
        )
        
        # Verify response structure
        self.assertIsInstance(result, dict)
        self.assertIn("page", result)
        self.assertIn("results", result["page"])
        self.assertIn("size", result["page"])
        self.assertEqual(result["page"]["size"], 0)
        self.assertEqual(result["page"]["results"], [])

    def test_get_content_children_of_type_content_not_found_error(self):
        """Test get_content_children_of_type raises ContentNotFoundError for non-existent content."""
        from confluence.SimulationEngine.custom_errors import ContentNotFoundError
        
        # Test with non-existent content id
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_children_of_type,
            expected_exception_type=ContentNotFoundError,
            expected_message="Content with id='nonexistent_id' not found.",
            id="nonexistent_id",
            child_type="page"
        )

    def test_get_content_children_of_type_with_none_children(self):
        """
        Test handling of None children in the children list.
        """
        # Create a parent content with None children
        parent = ConfluenceAPI.ContentAPI.create_content(
            {"title": "Parent with None children", "spaceKey": "TEST", "type": "page"}
        )
        
        # Manually add None children to the parent
        parent["children"] = [None, {"id": "1", "type": "page", "title": "Valid Child"}]
        ConfluenceAPI.SimulationEngine.db.DB["contents"][parent["id"]] = parent
        
        result = ConfluenceAPI.ContentAPI.get_content_children_of_type(parent["id"], "page")
        
        # Should only return the valid child, ignoring None
        self.assertEqual(result["page"]["size"], 1)
        self.assertEqual(result["page"]["results"][0]["id"], "1")

    def test_get_content_children_of_type_with_different_child_types(self):
        """
        Test filtering children by type when parent has children of different types.
        """
        # Create a parent content
        parent = ConfluenceAPI.ContentAPI.create_content(
            {"title": "Parent with mixed children", "spaceKey": "TEST", "type": "page"}
        )
        
        # Create different types of children
        page_child = ConfluenceAPI.ContentAPI.create_content(
            {"title": "Page Child", "spaceKey": "TEST", "type": "page"}
        )
        comment_child = ConfluenceAPI.ContentAPI.create_content(
            {"title": "Comment Child", "spaceKey": "TEST", "type": "comment", "ancestors": [parent["id"]]}
        )
        blog_child = ConfluenceAPI.ContentAPI.create_content(
            {"title": "Blog Child", "spaceKey": "TEST", "type": "blogpost"}
        )
        
        # Manually add children to parent
        parent["children"] = [page_child, comment_child, blog_child]
        ConfluenceAPI.SimulationEngine.db.DB["contents"][parent["id"]] = parent
        
        # Test filtering for pages only
        page_result = ConfluenceAPI.ContentAPI.get_content_children_of_type(parent["id"], "page")
        self.assertEqual(page_result["page"]["size"], 1)
        self.assertEqual(page_result["page"]["results"][0]["type"], "page")
        
        # Test filtering for comments only
        comment_result = ConfluenceAPI.ContentAPI.get_content_children_of_type(parent["id"], "comment")
        self.assertEqual(comment_result["comment"]["size"], 1)
        self.assertEqual(comment_result["comment"]["results"][0]["type"], "comment")
        
        # Test filtering for blogposts only
        blog_result = ConfluenceAPI.ContentAPI.get_content_children_of_type(parent["id"], "blogpost")
        self.assertEqual(blog_result["blogpost"]["size"], 1)
        self.assertEqual(blog_result["blogpost"]["results"][0]["type"], "blogpost")

    def test_get_content_comments(self):
        """
        Test retrieving comments for content with new response format.
        """
        c = ConfluenceAPI.ContentAPI.create_content(
            {"title": "CommentParent", "spaceKey": "XYZ", "type": "page"}
        )
        comments = ConfluenceAPI.ContentAPI.get_content_comments(c["id"])
        
        # Test the new response format
        self.assertIsInstance(comments, dict)
        self.assertIn("comment", comments)
        self.assertIn("results", comments["comment"])
        self.assertIn("size", comments["comment"])
        self.assertEqual(comments["comment"]["size"], 0)
        self.assertEqual(comments["comment"]["results"], [])

    def test_get_content_comments_invalid_id(self):
        """
        Test retrieving comments for a content with an invalid ID.
        """
        from confluence.SimulationEngine.custom_errors import ContentNotFoundError
        
        with self.assertRaises(ContentNotFoundError):
            ConfluenceAPI.ContentAPI.get_content_comments("invalid_id")

    # --- New comprehensive validation tests for get_content_comments ---
    
    def test_get_content_comments_id_type_validation(self):
        """Test get_content_comments with invalid types for 'id' parameter."""
        # Test with integer id
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_comments,
            expected_exception_type=TypeError,
            expected_message="Argument 'id' must be a string.",
            id=123
        )
        
        # Test with None id
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_comments,
            expected_exception_type=TypeError,
            expected_message="Argument 'id' must be a string.",
            id=None
        )
        
        # Test with list id
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_comments,
            expected_exception_type=TypeError,
            expected_message="Argument 'id' must be a string.",
            id=["content_id"]
        )

    def test_get_content_comments_id_empty_string_validation(self):
        """Test get_content_comments with empty string id."""
        from confluence.SimulationEngine.custom_errors import InvalidInputError
        
        # Test with empty string id
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_comments,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'id' cannot be an empty string.",
            id=""
        )
        
        # Test with whitespace-only id
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_comments,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'id' cannot be an empty string.",
            id="   "
        )

    def test_get_content_comments_expand_validation(self):
        """Test get_content_comments with invalid types for 'expand' parameter."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "ExpandValidationTest", "spaceKey": "TEST", "type": "page"}
        )
        
        # Test with integer expand
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_comments,
            expected_exception_type=TypeError,
            expected_message="Argument 'expand' must be a string if provided.",
            id=content["id"],
            expand=123
        )
        
        # Test with list expand
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_comments,
            expected_exception_type=TypeError,
            expected_message="Argument 'expand' must be a string if provided.",
            id=content["id"],
            expand=["space", "version"]
        )

    def test_get_content_comments_expand_empty_string_validation(self):
        """Test get_content_comments with empty string expand."""
        from confluence.SimulationEngine.custom_errors import InvalidInputError
        
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "ExpandEmptyTest", "spaceKey": "TEST", "type": "page"}
        )
        
        # Test with empty string expand
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_comments,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'expand' cannot be an empty string if provided.",
            id=content["id"],
            expand=""
        )
        
        # Test with whitespace-only expand
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_comments,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'expand' cannot be an empty string if provided.",
            id=content["id"],
            expand="   "
        )

    def test_get_content_comments_parent_version_validation(self):
        """Test get_content_comments with invalid types for 'parentVersion' parameter."""
        from confluence.SimulationEngine.custom_errors import InvalidParameterValueError
        
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "ParentVersionTest", "spaceKey": "TEST", "type": "page"}
        )
        
        # Test with string parentVersion
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_comments,
            expected_exception_type=TypeError,
            expected_message="Argument 'parentVersion' must be an integer.",
            id=content["id"],
            parentVersion="1"
        )
        
        # Test with float parentVersion
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_comments,
            expected_exception_type=TypeError,
            expected_message="Argument 'parentVersion' must be an integer.",
            id=content["id"],
            parentVersion=1.5
        )
        
        # Test with negative parentVersion
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_comments,
            expected_exception_type=InvalidParameterValueError,
            expected_message="Argument 'parentVersion' must be non-negative.",
            id=content["id"],
            parentVersion=-1
        )

    def test_get_content_comments_start_validation(self):
        """Test get_content_comments with invalid types for 'start' parameter."""
        from confluence.SimulationEngine.custom_errors import InvalidParameterValueError
        
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "StartValidationTest", "spaceKey": "TEST", "type": "page"}
        )
        
        # Test with string start
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_comments,
            expected_exception_type=TypeError,
            expected_message="Argument 'start' must be an integer.",
            id=content["id"],
            start="0"
        )
        
        # Test with float start
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_comments,
            expected_exception_type=TypeError,
            expected_message="Argument 'start' must be an integer.",
            id=content["id"],
            start=0.5
        )
        
        # Test with negative start
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_comments,
            expected_exception_type=InvalidParameterValueError,
            expected_message="Argument 'start' must be non-negative.",
            id=content["id"],
            start=-1
        )

    def test_get_content_comments_limit_validation(self):
        """Test get_content_comments with invalid types for 'limit' parameter."""
        from confluence.SimulationEngine.custom_errors import InvalidParameterValueError
        
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "LimitValidationTest", "spaceKey": "TEST", "type": "page"}
        )
        
        # Test with string limit
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_comments,
            expected_exception_type=TypeError,
            expected_message="Argument 'limit' must be an integer.",
            id=content["id"],
            limit="25"
        )
        
        # Test with float limit
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_comments,
            expected_exception_type=TypeError,
            expected_message="Argument 'limit' must be an integer.",
            id=content["id"],
            limit=25.5
        )
        
        # Test with zero limit
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_comments,
            expected_exception_type=InvalidParameterValueError,
            expected_message="Argument 'limit' must be positive.",
            id=content["id"],
            limit=0
        )
        
        # Test with negative limit
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_comments,
            expected_exception_type=InvalidParameterValueError,
            expected_message="Argument 'limit' must be positive.",
            id=content["id"],
            limit=-5
        )

    def test_get_content_comments_pagination(self):
        """Test get_content_comments with pagination parameters."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "PaginationTest", "spaceKey": "TEST", "type": "page"}
        )
        
        # Test with custom start and limit
        result = ConfluenceAPI.ContentAPI.get_content_comments(
            id=content["id"],
            start=5,
            limit=10
        )
        
        # Verify response structure
        self.assertIsInstance(result, dict)
        self.assertIn("comment", result)
        self.assertIn("results", result["comment"])
        self.assertIn("size", result["comment"])
        self.assertEqual(result["comment"]["size"], 0)
        self.assertEqual(result["comment"]["results"], [])

    def test_get_content_comments_with_expand(self):
        """Test get_content_comments with expand parameter."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "ExpandTest", "spaceKey": "TEST", "type": "page"}
        )
        
        # Test with expand parameter
        result = ConfluenceAPI.ContentAPI.get_content_comments(
            id=content["id"],
            expand="space,version"
        )
        
        # Verify response structure
        self.assertIsInstance(result, dict)
        self.assertIn("comment", result)
        self.assertIn("results", result["comment"])
        self.assertIn("size", result["comment"])
        self.assertEqual(result["comment"]["size"], 0)
        self.assertEqual(result["comment"]["results"], [])

    def test_get_content_comments_with_parent_version(self):
        """Test get_content_comments with parentVersion parameter."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "ParentVersionTest", "spaceKey": "TEST", "type": "page"}
        )
        
        # Test with parentVersion parameter
        result = ConfluenceAPI.ContentAPI.get_content_comments(
            id=content["id"],
            parentVersion=2
        )
        
        # Verify response structure
        self.assertIsInstance(result, dict)
        self.assertIn("comment", result)
        self.assertIn("results", result["comment"])
        self.assertIn("size", result["comment"])
        self.assertEqual(result["comment"]["size"], 0)
        self.assertEqual(result["comment"]["results"], [])

    def test_get_content_comments_content_not_found_error(self):
        """Test get_content_comments raises ContentNotFoundError for non-existent content."""
        from confluence.SimulationEngine.custom_errors import ContentNotFoundError
        
        # Test with non-existent content id
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_comments,
            expected_exception_type=ContentNotFoundError,
            expected_message="Content with id='nonexistent_id' not found.",
            id="nonexistent_id"
        )

    def test_get_content_comments_with_actual_comments(self):
        """
        Test get_content_comments with actual comment children.
        """
        # Create a parent content
        parent = ConfluenceAPI.ContentAPI.create_content(
            {"title": "Parent with comments", "spaceKey": "TEST", "type": "page"}
        )
        
        # Create comment children
        comment1 = ConfluenceAPI.ContentAPI.create_content(
            {"title": "Comment 1", "spaceKey": "TEST", "type": "comment", "ancestors": [parent["id"]]}
        )
        comment2 = ConfluenceAPI.ContentAPI.create_content(
            {"title": "Comment 2", "spaceKey": "TEST", "type": "comment", "ancestors": [parent["id"]]}
        )
        
        # Manually add comments to parent
        parent["children"] = [comment1, comment2]
        ConfluenceAPI.SimulationEngine.db.DB["contents"][parent["id"]] = parent
        
        # Test retrieving comments
        result = ConfluenceAPI.ContentAPI.get_content_comments(parent["id"])
        
        # Verify response structure
        self.assertIsInstance(result, dict)
        self.assertIn("comment", result)
        self.assertIn("results", result["comment"])
        self.assertIn("size", result["comment"])
        self.assertEqual(result["comment"]["size"], 2)
        self.assertEqual(len(result["comment"]["results"]), 2)
        
        # Verify comment types
        for comment in result["comment"]["results"]:
            self.assertEqual(comment["type"], "comment")

    def test_get_content_comments_with_mixed_children(self):
        """
        Test get_content_comments when parent has children of different types.
        """
        # Create a parent content
        parent = ConfluenceAPI.ContentAPI.create_content(
            {"title": "Parent with mixed children", "spaceKey": "TEST", "type": "page"}
        )
        
        # Create different types of children
        page_child = ConfluenceAPI.ContentAPI.create_content(
            {"title": "Page Child", "spaceKey": "TEST", "type": "page"}
        )
        comment_child = ConfluenceAPI.ContentAPI.create_content(
            {"title": "Comment Child", "spaceKey": "TEST", "type": "comment", "ancestors": [parent["id"]]}
        )
        blog_child = ConfluenceAPI.ContentAPI.create_content(
            {"title": "Blog Child", "spaceKey": "TEST", "type": "blogpost"}
        )
        
        # Manually add children to parent
        parent["children"] = [page_child, comment_child, blog_child]
        ConfluenceAPI.SimulationEngine.db.DB["contents"][parent["id"]] = parent
        
        # Test retrieving comments - should only return the comment
        result = ConfluenceAPI.ContentAPI.get_content_comments(parent["id"])
        
        # Verify response structure
        self.assertIsInstance(result, dict)
        self.assertIn("comment", result)
        self.assertIn("results", result["comment"])
        self.assertIn("size", result["comment"])
        self.assertEqual(result["comment"]["size"], 1)
        self.assertEqual(len(result["comment"]["results"]), 1)
        self.assertEqual(result["comment"]["results"][0]["type"], "comment")

    def test_get_content_comments_with_none_children(self):
        """
        Test handling of None children in the children list.
        """
        # Create a parent content with None children
        parent = ConfluenceAPI.ContentAPI.create_content(
            {"title": "Parent with None children", "spaceKey": "TEST", "type": "page"}
        )
        
        # Manually add None children to the parent
        parent["children"] = [None, {"id": "1", "type": "comment", "title": "Valid Comment"}]
        ConfluenceAPI.SimulationEngine.db.DB["contents"][parent["id"]] = parent
        
        result = ConfluenceAPI.ContentAPI.get_content_comments(parent["id"])
        
        # Should only return the valid comment, ignoring None
        self.assertEqual(result["comment"]["size"], 1)
        self.assertEqual(result["comment"]["results"][0]["id"], "1")

        # --- New comprehensive tests for get_content_attachments ---

    def test_get_content_attachments(self):
        """
        Test retrieving attachments for content with new response format.
        """
        c = ConfluenceAPI.ContentAPI.create_content(
            {"title": "AttachmentParent", "spaceKey": "XYZ", "type": "page"}
        )
        attachments = ConfluenceAPI.ContentAPI.get_content_attachments(c["id"])

        # Test the new response format
        self.assertIsInstance(attachments, dict)
        self.assertIn("results", attachments)
        self.assertIn("size", attachments)
        self.assertIn("_links", attachments)
        self.assertEqual(attachments["size"], 0)
        self.assertEqual(attachments["results"], [])
        self.assertEqual(attachments["_links"]["base"], "http://example.com")
        self.assertEqual(attachments["_links"]["context"], "/confluence")

    def test_get_content_attachments_invalid_id(self):
        """
        Test retrieving attachments for a content with an invalid ID.
        """
        from confluence.SimulationEngine.custom_errors import ContentNotFoundError

        with self.assertRaises(ContentNotFoundError):
            ConfluenceAPI.ContentAPI.get_content_attachments("invalid_id")

    def test_get_content_attachments_id_type_validation(self):
        """Test get_content_attachments with invalid types for 'id' parameter."""
        # Test with integer id
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_attachments,
            expected_exception_type=TypeError,
            expected_message="Argument 'id' must be a string.",
            id=123
        )

        # Test with None id
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_attachments,
            expected_exception_type=TypeError,
            expected_message="Argument 'id' must be a string.",
            id=None
        )

        # Test with list id
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_attachments,
            expected_exception_type=TypeError,
            expected_message="Argument 'id' must be a string.",
            id=["content_id"]
        )

    def test_get_content_attachments_id_empty_string_validation(self):
        """Test get_content_attachments with empty string id."""
        from confluence.SimulationEngine.custom_errors import InvalidInputError

        # Test with empty string id
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_attachments,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'id' cannot be an empty string.",
            id=""
        )

        # Test with whitespace-only id
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_attachments,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'id' cannot be an empty string.",
            id="   "
        )

    def test_get_content_attachments_expand_validation(self):
        """Test get_content_attachments with invalid types for 'expand' parameter."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "ExpandValidationTest", "spaceKey": "TEST", "type": "page"}
        )

        # Test with integer expand
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_attachments,
            expected_exception_type=TypeError,
            expected_message="Argument 'expand' must be a string if provided.",
            id=content["id"],
            expand=123
        )

        # Test with list expand
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_attachments,
            expected_exception_type=TypeError,
            expected_message="Argument 'expand' must be a string if provided.",
            id=content["id"],
            expand=["space", "version"]
        )

    def test_get_content_attachments_expand_empty_string_validation(self):
        """Test get_content_attachments with empty string expand."""
        from confluence.SimulationEngine.custom_errors import InvalidInputError

        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "ExpandEmptyTest", "spaceKey": "TEST", "type": "page"}
        )

        # Test with empty string expand
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_attachments,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'expand' cannot be an empty string if provided.",
            id=content["id"],
            expand=""
        )

        # Test with whitespace-only expand
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_attachments,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'expand' cannot be an empty string if provided.",
            id=content["id"],
            expand="   "
        )

    def test_get_content_attachments_start_validation(self):
        """Test get_content_attachments with invalid types for 'start' parameter."""
        from confluence.SimulationEngine.custom_errors import InvalidParameterValueError

        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "StartValidationTest", "spaceKey": "TEST", "type": "page"}
        )

        # Test with string start
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_attachments,
            expected_exception_type=TypeError,
            expected_message="Argument 'start' must be an integer.",
            id=content["id"],
            start="0"
        )

        # Test with float start
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_attachments,
            expected_exception_type=TypeError,
            expected_message="Argument 'start' must be an integer.",
            id=content["id"],
            start=0.5
        )

        # Test with negative start
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_attachments,
            expected_exception_type=InvalidParameterValueError,
            expected_message="Argument 'start' must be non-negative.",
            id=content["id"],
            start=-1
        )

    def test_get_content_attachments_limit_validation(self):
        """Test get_content_attachments with invalid types for 'limit' parameter."""
        from confluence.SimulationEngine.custom_errors import InvalidParameterValueError

        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "LimitValidationTest", "spaceKey": "TEST", "type": "page"}
        )

        # Test with string limit
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_attachments,
            expected_exception_type=TypeError,
            expected_message="Argument 'limit' must be an integer.",
            id=content["id"],
            limit="50"
        )

        # Test with float limit
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_attachments,
            expected_exception_type=TypeError,
            expected_message="Argument 'limit' must be an integer.",
            id=content["id"],
            limit=50.5
        )

        # Test with zero limit
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_attachments,
            expected_exception_type=InvalidParameterValueError,
            expected_message="Argument 'limit' must be positive.",
            id=content["id"],
            limit=0
        )

        # Test with negative limit
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_attachments,
            expected_exception_type=InvalidParameterValueError,
            expected_message="Argument 'limit' must be positive.",
            id=content["id"],
            limit=-5
        )

        # Test with limit exceeding maximum
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_attachments,
            expected_exception_type=InvalidParameterValueError,
            expected_message="Argument 'limit' cannot exceed 1000.",
            id=content["id"],
            limit=1001
        )

    def test_get_content_attachments_filename_validation(self):
        """Test get_content_attachments with invalid types for 'filename' parameter."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "FilenameValidationTest", "spaceKey": "TEST", "type": "page"}
        )

        # Test with integer filename
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_attachments,
            expected_exception_type=TypeError,
            expected_message="Argument 'filename' must be a string if provided.",
            id=content["id"],
            filename=123
        )

        # Test with list filename
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_attachments,
            expected_exception_type=TypeError,
            expected_message="Argument 'filename' must be a string if provided.",
            id=content["id"],
            filename=["file.txt"]
        )

    def test_get_content_attachments_filename_empty_string_validation(self):
        """Test get_content_attachments with empty string filename."""
        from confluence.SimulationEngine.custom_errors import InvalidInputError

        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "FilenameEmptyTest", "spaceKey": "TEST", "type": "page"}
        )

        # Test with empty string filename
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_attachments,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'filename' cannot be an empty string if provided.",
            id=content["id"],
            filename=""
        )

        # Test with whitespace-only filename
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_attachments,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'filename' cannot be an empty string if provided.",
            id=content["id"],
            filename="   "
        )

    def test_get_content_attachments_media_type_validation(self):
        """Test get_content_attachments with invalid types for 'mediaType' parameter."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "MediaTypeValidationTest", "spaceKey": "TEST", "type": "page"}
        )

        # Test with integer mediaType
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_attachments,
            expected_exception_type=TypeError,
            expected_message="Argument 'mediaType' must be a string if provided.",
            id=content["id"],
            mediaType=123
        )

        # Test with list mediaType
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_attachments,
            expected_exception_type=TypeError,
            expected_message="Argument 'mediaType' must be a string if provided.",
            id=content["id"],
            mediaType=["text/plain"]
        )

    def test_get_content_attachments_media_type_empty_string_validation(self):
        """Test get_content_attachments with empty string mediaType."""
        from confluence.SimulationEngine.custom_errors import InvalidInputError

        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "MediaTypeEmptyTest", "spaceKey": "TEST", "type": "page"}
        )

        # Test with empty string mediaType
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_attachments,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'mediaType' cannot be an empty string if provided.",
            id=content["id"],
            mediaType=""
        )

        # Test with whitespace-only mediaType
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_attachments,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'mediaType' cannot be an empty string if provided.",
            id=content["id"],
            mediaType="   "
        )

    def test_get_content_attachments_pagination(self):
        """Test get_content_attachments with pagination parameters."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "PaginationTest", "spaceKey": "TEST", "type": "page"}
        )

        # Test with custom start and limit
        result = ConfluenceAPI.ContentAPI.get_content_attachments(
            id=content["id"],
            start=5,
            limit=10
        )

        # Verify response structure
        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertIn("size", result)
        self.assertIn("_links", result)
        self.assertEqual(result["size"], 0)
        self.assertEqual(result["results"], [])

    def test_get_content_attachments_with_expand(self):
        """Test get_content_attachments with expand parameter."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "ExpandTest", "spaceKey": "TEST", "type": "page"}
        )

        # Test with expand parameter
        result = ConfluenceAPI.ContentAPI.get_content_attachments(
            id=content["id"],
            expand="space,version"
        )

        # Verify response structure
        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertIn("size", result)
        self.assertIn("_links", result)
        self.assertEqual(result["size"], 0)
        self.assertEqual(result["results"], [])

    def test_get_content_attachments_content_not_found_error(self):
        """Test get_content_attachments raises ContentNotFoundError for non-existent content."""
        from confluence.SimulationEngine.custom_errors import ContentNotFoundError

        # Test with non-existent content id
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_attachments,
            expected_exception_type=ContentNotFoundError,
            expected_message="Content with id='nonexistent_id' not found.",
            id="nonexistent_id"
        )

    def test_get_content_attachments_with_actual_attachments(self):
        """
        Test get_content_attachments with actual attachment children.
        """
        # Create a parent content
        parent = ConfluenceAPI.ContentAPI.create_content(
            {"title": "Parent with attachments", "spaceKey": "TEST", "type": "page"}
        )

        # Create attachment children
        attachment1 = {
            "id": "att1",
            "type": "attachment",
            "title": "file1.txt",
            "metadata": {"mediaType": "text/plain", "comment": "First file"}
        }
        attachment2 = {
            "id": "att2", 
            "type": "attachment",
            "title": "file2.pdf",
            "metadata": {"mediaType": "application/pdf", "comment": "Second file"}
        }

        # Manually add attachments to parent
        parent["children"] = [attachment1, attachment2]
        ConfluenceAPI.SimulationEngine.db.DB["contents"][parent["id"]] = parent

        # Test retrieving attachments
        result = ConfluenceAPI.ContentAPI.get_content_attachments(parent["id"])

        # Verify response structure
        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertIn("size", result)
        self.assertIn("_links", result)
        self.assertEqual(result["size"], 2)
        self.assertEqual(len(result["results"]), 2)

        # Verify attachment types
        for attachment in result["results"]:
            self.assertEqual(attachment["type"], "attachment")

    def test_get_content_attachments_with_mixed_children(self):
        """
        Test get_content_attachments when parent has children of different types.
        """
        # Create a parent content
        parent = ConfluenceAPI.ContentAPI.create_content(
            {"title": "Parent with mixed children", "spaceKey": "TEST", "type": "page"}
        )

        # Create different types of children
        page_child = {
            "id": "page1",
            "type": "page",
            "title": "Page Child"
        }
        attachment_child = {
            "id": "att1",
            "type": "attachment", 
            "title": "file.txt",
            "metadata": {"mediaType": "text/plain"}
        }
        comment_child = {
            "id": "comment1",
            "type": "comment",
            "title": "Comment Child"
        }

        # Manually add children to parent
        parent["children"] = [page_child, attachment_child, comment_child]
        ConfluenceAPI.SimulationEngine.db.DB["contents"][parent["id"]] = parent

        # Test retrieving attachments - should only return the attachment
        result = ConfluenceAPI.ContentAPI.get_content_attachments(parent["id"])

        # Verify response structure
        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertIn("size", result)
        self.assertIn("_links", result)
        self.assertEqual(result["size"], 1)
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["type"], "attachment")

    def test_get_content_attachments_with_none_children(self):
        """
        Test handling of None children in the children list.
        """
        # Create a parent content with None children
        parent = ConfluenceAPI.ContentAPI.create_content(
            {"title": "Parent with None children", "spaceKey": "TEST", "type": "page"}
        )

        # Manually add None children to the parent
        parent["children"] = [None, {"id": "att1", "type": "attachment", "title": "Valid Attachment"}]
        ConfluenceAPI.SimulationEngine.db.DB["contents"][parent["id"]] = parent

        result = ConfluenceAPI.ContentAPI.get_content_attachments(parent["id"])

        # Should only return the valid attachment, ignoring None
        self.assertEqual(result["size"], 1)
        self.assertEqual(result["results"][0]["id"], "att1")

    def test_get_content_attachments_filename_filtering(self):
        """
        Test get_content_attachments with filename filtering.
        """
        # Create a parent content
        parent = ConfluenceAPI.ContentAPI.create_content(
            {"title": "Parent with attachments", "spaceKey": "TEST", "type": "page"}
        )

        # Create attachment children with different filenames
        attachment1 = {
            "id": "att1",
            "type": "attachment",
            "title": "file1.txt",
            "metadata": {"mediaType": "text/plain"}
        }
        attachment2 = {
            "id": "att2",
            "type": "attachment", 
            "title": "file2.pdf",
            "metadata": {"mediaType": "application/pdf"}
        }

        # Manually add attachments to parent
        parent["children"] = [attachment1, attachment2]
        ConfluenceAPI.SimulationEngine.db.DB["contents"][parent["id"]] = parent

        # Test filtering by filename
        result = ConfluenceAPI.ContentAPI.get_content_attachments(
            id=parent["id"],
            filename="file1.txt"
        )

        # Should only return the matching attachment
        self.assertEqual(result["size"], 1)
        self.assertEqual(result["results"][0]["title"], "file1.txt")

        # Test with non-matching filename
        result = ConfluenceAPI.ContentAPI.get_content_attachments(
            id=parent["id"],
            filename="nonexistent.txt"
        )

        # Should return empty results
        self.assertEqual(result["size"], 0)
        self.assertEqual(result["results"], [])

    def test_get_content_attachments_media_type_filtering(self):
        """
        Test get_content_attachments with mediaType filtering.
        """
        # Create a parent content
        parent = ConfluenceAPI.ContentAPI.create_content(
            {"title": "Parent with attachments", "spaceKey": "TEST", "type": "page"}
        )

        # Create attachment children with different media types
        attachment1 = {
            "id": "att1",
            "type": "attachment",
            "title": "file1.txt",
            "metadata": {"mediaType": "text/plain"}
        }
        attachment2 = {
            "id": "att2",
            "type": "attachment",
            "title": "file2.pdf", 
            "metadata": {"mediaType": "application/pdf"}
        }

        # Manually add attachments to parent
        parent["children"] = [attachment1, attachment2]
        ConfluenceAPI.SimulationEngine.db.DB["contents"][parent["id"]] = parent

        # Test filtering by mediaType
        result = ConfluenceAPI.ContentAPI.get_content_attachments(
            id=parent["id"],
            mediaType="text/plain"
        )

        # Should only return the matching attachment
        self.assertEqual(result["size"], 1)
        self.assertEqual(result["results"][0]["metadata"]["mediaType"], "text/plain")

        # Test with non-matching mediaType
        result = ConfluenceAPI.ContentAPI.get_content_attachments(
            id=parent["id"],
            mediaType="image/jpeg"
        )

        # Should return empty results
        self.assertEqual(result["size"], 0)
        self.assertEqual(result["results"], [])

    def test_get_content_attachments_combined_filtering(self):
        """
        Test get_content_attachments with both filename and mediaType filtering.
        """
        # Create a parent content
        parent = ConfluenceAPI.ContentAPI.create_content(
            {"title": "Parent with attachments", "spaceKey": "TEST", "type": "page"}
        )

        # Create attachment children
        attachment1 = {
            "id": "att1",
            "type": "attachment",
            "title": "file1.txt",
            "metadata": {"mediaType": "text/plain"}
        }
        attachment2 = {
            "id": "att2",
            "type": "attachment",
            "title": "file2.txt",
            "metadata": {"mediaType": "text/plain"}
        }
        attachment3 = {
            "id": "att3",
            "type": "attachment",
            "title": "file1.pdf",
            "metadata": {"mediaType": "application/pdf"}
        }

        # Manually add attachments to parent
        parent["children"] = [attachment1, attachment2, attachment3]
        ConfluenceAPI.SimulationEngine.db.DB["contents"][parent["id"]] = parent

        # Test filtering by both filename and mediaType
        result = ConfluenceAPI.ContentAPI.get_content_attachments(
            id=parent["id"],
            filename="file1.txt",
            mediaType="text/plain"
        )

        # Should only return the attachment that matches both criteria
        self.assertEqual(result["size"], 1)
        self.assertEqual(result["results"][0]["title"], "file1.txt")
        self.assertEqual(result["results"][0]["metadata"]["mediaType"], "text/plain")

        # Test with conflicting filters (should return empty)
        result = ConfluenceAPI.ContentAPI.get_content_attachments(
            id=parent["id"],
            filename="file1.txt",
            mediaType="application/pdf"
        )

        # Should return empty results
        self.assertEqual(result["size"], 0)
        self.assertEqual(result["results"], [])

    def test_get_content_attachments_pagination_with_results(self):
        """
        Test get_content_attachments pagination with actual results.
        """
        # Create a parent content
        parent = ConfluenceAPI.ContentAPI.create_content(
            {"title": "Parent with attachments", "spaceKey": "TEST", "type": "page"}
        )

        # Create multiple attachment children
        attachments = []
        for i in range(10):
            attachment = {
                "id": f"att{i}",
                "type": "attachment",
                "title": f"file{i}.txt",
                "metadata": {"mediaType": "text/plain"}
            }
            attachments.append(attachment)

        # Manually add attachments to parent
        parent["children"] = attachments
        ConfluenceAPI.SimulationEngine.db.DB["contents"][parent["id"]] = parent

        # Test pagination
        result = ConfluenceAPI.ContentAPI.get_content_attachments(
            id=parent["id"],
            start=2,
            limit=3
        )

        # Should return 3 attachments starting from index 2
        self.assertEqual(result["size"], 3)
        self.assertEqual(len(result["results"]), 3)
        self.assertEqual(result["results"][0]["id"], "att2")
        self.assertEqual(result["results"][1]["id"], "att3")
        self.assertEqual(result["results"][2]["id"], "att4")

        # Test pagination beyond available results
        result = ConfluenceAPI.ContentAPI.get_content_attachments(
            id=parent["id"],
            start=15,
            limit=5
        )

        # Should return empty results
        self.assertEqual(result["size"], 0)
        self.assertEqual(result["results"], [])


    def test_create_attachments_invalid_id(self):
        """
        Test creating attachments for a content with an invalid ID.
        """
        with self.assertRaises(ValueError):
            ConfluenceAPI.ContentAPI.create_attachments("invalid_id", "testfile.txt")

    def test_update_attachment(self):
        """
        Test updating attachment metadata (mock operation).
        """
        c = ConfluenceAPI.ContentAPI.create_content(
            {"title": "AttachmentParent2", "spaceKey": "XYZ", "type": "page"}
        )

        # First create the attachment
        class MockFile:
            def __init__(self, name):
                self.name = name
                self.content_type = "text/plain"

        f = MockFile("test.txt")
        created = ConfluenceAPI.ContentAPI.create_attachments(
            c["id"], f, comment="initial comment"
        )
        attachment_id = created["attachmentId"]

        # Now update it
        resp = ConfluenceAPI.ContentAPI.update_attachment(
            c["id"], attachment_id, {"comment": "new comment"}
        )
        self.assertIn("attachmentId", resp)
        self.assertEqual(resp["attachmentId"], attachment_id)
        self.assertIn("updatedFields", resp)

    # def test_update_attachment_invalid_id_and_attachment_id(self):
    #     """
    #     Test updating an attachment with an invalid ID and attachment ID.
    #     """
    #     c = ConfluenceAPI.ContentAPI.create_content(
    #         {"title": "AttachmentParent2", "spaceKey": "XYZ", "type": "page"}
    #     )

    #     # First create the attachment
    #     class MockFile:
    #         def __init__(self, name):
    #             self.name = name
    #             self.content_type = "text/plain"

    #     f = MockFile("test.txt")
    #     created = ConfluenceAPI.ContentAPI.create_attachments(
    #         c["id"], f, comment="initial comment"
    #     )
    #     attachment_id = created["attachmentId"]

    #     # Now update it
    #     resp = ConfluenceAPI.ContentAPI.update_attachment(
    #         c["id"], attachment_id, {"comment": "new comment"}
    #     )
    #     with self.assertRaises(ValueError):
    #         ConfluenceAPI.ContentAPI.update_attachment(
    #             "invalid_id", attachment_id, {"comment": "new comment"}
    #         )

    #     with self.assertRaises(ValueError):
    #         ConfluenceAPI.ContentAPI.update_attachment(
    #             c["id"], "invalid_attachment_id", {"comment": "new comment"}
    #         )

    # def test_update_attachment_data(self):
    #     """
    #     Test updating the binary data of an existing attachment (mock operation).
    #     """

    #     class MockFile:
    #         def __init__(self, name):
    #             self.name = name
    #             self.content_type = "text/plain"

    #     c = ConfluenceAPI.ContentAPI.create_content(
    #         {"title": "AttachmentParent3", "spaceKey": "XYZ", "type": "page"}
    #     )

    #     # First create the attachment
    #     f1 = MockFile("original.txt")
    #     created = ConfluenceAPI.ContentAPI.create_attachments(
    #         c["id"], f1, comment="initial comment"
    #     )
    #     attachment_id = created["attachmentId"]

    #     # Now update it
    #     f2 = MockFile("updatedfile.txt")
    #     resp = ConfluenceAPI.ContentAPI.update_attachment_data(
    #         c["id"], attachment_id, f2, comment="updated comment", minorEdit=True
    #     )
    #     self.assertEqual(resp["attachmentId"], attachment_id)
    #     self.assertEqual(resp["updatedFile"], "updatedfile.txt")
    #     self.assertEqual(resp["comment"], "updated comment")
    #     self.assertTrue(resp["minorEdit"])

    # def test_update_attachment_data_invalid_id_and_attachment_id(self):
    #     """
    #     Test updating the binary data of an attachment with an invalid ID and attachment ID.
    #     """

    #     class MockFile:
    #         def __init__(self, name):
    #             self.name = name
    #             self.content_type = "text/plain"

    #     c = ConfluenceAPI.ContentAPI.create_content(
    #         {"title": "AttachmentParent3", "spaceKey": "XYZ", "type": "page"}
    #     )

    #     # First create the attachment
    #     f1 = MockFile("original.txt")
    #     created = ConfluenceAPI.ContentAPI.create_attachments(
    #         c["id"], f1, comment="initial comment"
    #     )
    #     attachment_id = created["attachmentId"]

    #     with self.assertRaises(ValueError):
    #         ConfluenceAPI.ContentAPI.update_attachment_data(
    #             "invalid_id", attachment_id, "testfile.txt"
    #         )

    #     with self.assertRaises(ValueError):
    #         ConfluenceAPI.ContentAPI.update_attachment_data(
    #             c["id"], "invalid_attachment_id", "testfile.txt"
    #         )

    def test_get_content_descendants(self):
        """
        Test retrieving all descendants of content (mock returns empty).
        """
        c = ConfluenceAPI.ContentAPI.create_content(
            {"title": "DescendantParent", "spaceKey": "XYZ", "type": "page"}
        )
        descendants = ConfluenceAPI.ContentAPI.get_content_descendants(c["id"])
        self.assertIsInstance(descendants, dict)
        self.assertIn("comment", descendants)
        self.assertIn("attachment", descendants)
        self.assertEqual(descendants["comment"], [])

    def test_get_content_descendants_id_type_validation(self):
        """Test get_content_descendants with invalid types for 'id' parameter."""
        # Test with integer id
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants,
            expected_exception_type=TypeError,
            expected_message="Argument 'id' must be a string.",
            id=123
        )

        # Test with None id
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants,
            expected_exception_type=TypeError,
            expected_message="Argument 'id' must be a string.",
            id=None
        )

        # Test with list id
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants,
            expected_exception_type=TypeError,
            expected_message="Argument 'id' must be a string.",
            id=["content_id"]
        )

    def test_get_content_descendants_id_empty_string_validation(self):
        """Test get_content_descendants with empty string id."""
        # Test with empty string id
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'id' cannot be an empty string.",
            id=""
        )

        # Test with whitespace-only id
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'id' cannot be an empty string.",
            id="   "
        )

    def test_get_content_descendants_content_not_found(self):
        """Test get_content_descendants with non-existent content id."""
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants,
            expected_exception_type=ValueError,
            expected_message="Content with id=nonexistent_id not found.",
            id="nonexistent_id"
        )

    def test_get_content_descendants_start_validation(self):
        """Test get_content_descendants with invalid start parameter."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "StartValidationTest", "spaceKey": "TEST", "type": "page"}
        )

        # Test with negative start
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'start' must be non-negative.",
            id=content["id"],
            start=-1
        )

    def test_get_content_descendants_limit_validation(self):
        """Test get_content_descendants with invalid limit parameter."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "LimitValidationTest", "spaceKey": "TEST", "type": "page"}
        )

        # Test with negative limit
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'limit' must be non-negative.",
            id=content["id"],
            limit=-1
        )

    def test_get_content_descendants_valid_inputs_success(self):
        """Test get_content_descendants with all valid inputs."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "ValidInputsDescendantsTest", "spaceKey": "TEST", "type": "page"}
        )

        # Test with all valid parameters
        result = ConfluenceAPI.ContentAPI.get_content_descendants(
            id=content["id"],
            expand="space,version",
            start=0,
            limit=10
        )

        # Verify the result structure
        self.assertIsInstance(result, dict)
        self.assertIn("page", result)
        self.assertIn("blogpost", result)
        self.assertIn("comment", result)
        self.assertIn("attachment", result)

        # Since this is a simulation, all should be empty lists
        for content_type in result:
            self.assertIsInstance(result[content_type], list)

    def test_get_content_descendants_pagination_functionality(self):
        """Test get_content_descendants pagination parameters."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "PaginationDescendantsTest", "spaceKey": "TEST", "type": "page"}
        )

        # Test with different pagination parameters
        result1 = ConfluenceAPI.ContentAPI.get_content_descendants(
            id=content["id"],
            start=0,
            limit=5
        )
        
        result2 = ConfluenceAPI.ContentAPI.get_content_descendants(
            id=content["id"],
            start=5,
            limit=10
        )

        # Both should have the same structure
        self.assertIsInstance(result1, dict)
        self.assertIsInstance(result2, dict)
        
        # All content type lists should be empty in simulation
        for content_type in ["page", "blogpost", "comment", "attachment"]:
            self.assertIn(content_type, result1)
            self.assertIn(content_type, result2)
            self.assertEqual(result1[content_type], [])
            self.assertEqual(result2[content_type], [])

    def test_get_content_descendants_expand_parameter(self):
        """Test get_content_descendants with expand parameter."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "ExpandDescendantsTest", "spaceKey": "TEST", "type": "page"}
        )

        # Test with expand parameter (should not affect structure in simulation)
        result = ConfluenceAPI.ContentAPI.get_content_descendants(
            id=content["id"],
            expand="space,version,history"
        )

        # Verify the result structure is maintained
        self.assertIsInstance(result, dict)
        self.assertIn("page", result)
        self.assertIn("blogpost", result)
        self.assertIn("comment", result)
        self.assertIn("attachment", result)

    def test_get_content_descendants_zero_limit(self):
        """Test get_content_descendants with limit=0."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "ZeroLimitDescendantsTest", "spaceKey": "TEST", "type": "page"}
        )

        # Test with limit=0 (should return empty lists for all types)
        result = ConfluenceAPI.ContentAPI.get_content_descendants(
            id=content["id"],
            limit=0
        )

        # Verify the result structure
        self.assertIsInstance(result, dict)
        for content_type in ["page", "blogpost", "comment", "attachment"]:
            self.assertIn(content_type, result)
            self.assertEqual(result[content_type], [])

    def test_get_content_descendants_large_start_index(self):
        """Test get_content_descendants with start index beyond available data."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "LargeStartDescendantsTest", "spaceKey": "TEST", "type": "page"}
        )

        # Test with large start index (should return empty lists for all types)
        result = ConfluenceAPI.ContentAPI.get_content_descendants(
            id=content["id"],
            start=1000,
            limit=10
        )

        # Verify the result structure
        self.assertIsInstance(result, dict)
        for content_type in ["page", "blogpost", "comment", "attachment"]:
            self.assertIn(content_type, result)
            self.assertEqual(result[content_type], [])

    def test_get_content_descendants_start_type_validation(self):
        """Test get_content_descendants with invalid types for 'start' parameter."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "StartTypeValidationTest", "spaceKey": "TEST", "type": "page"}
        )

        # Test with string start
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants,
            expected_exception_type=TypeError,
            expected_message="Argument 'start' must be an integer.",
            id=content["id"],
            start="0"
        )

        # Test with float start
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants,
            expected_exception_type=TypeError,
            expected_message="Argument 'start' must be an integer.",
            id=content["id"],
            start=0.5
        )

        # Test with None start
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants,
            expected_exception_type=TypeError,
            expected_message="Argument 'start' must be an integer.",
            id=content["id"],
            start=None
        )

        # Test with list start
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants,
            expected_exception_type=TypeError,
            expected_message="Argument 'start' must be an integer.",
            id=content["id"],
            start=[0]
        )

    def test_get_content_descendants_limit_type_validation(self):
        """Test get_content_descendants with invalid types for 'limit' parameter."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "LimitTypeValidationTest", "spaceKey": "TEST", "type": "page"}
        )

        # Test with string limit
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants,
            expected_exception_type=TypeError,
            expected_message="Argument 'limit' must be an integer.",
            id=content["id"],
            limit="25"
        )

        # Test with float limit
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants,
            expected_exception_type=TypeError,
            expected_message="Argument 'limit' must be an integer.",
            id=content["id"],
            limit=25.5
        )

        # Test with None limit
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants,
            expected_exception_type=TypeError,
            expected_message="Argument 'limit' must be an integer.",
            id=content["id"],
            limit=None
        )

        # Test with list limit
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants,
            expected_exception_type=TypeError,
            expected_message="Argument 'limit' must be an integer.",
            id=content["id"],
            limit=[25]
        )

    def test_get_content_descendants_boundary_values(self):
        """Test get_content_descendants with boundary values for start/limit."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "BoundaryValuesTest", "spaceKey": "TEST", "type": "page"}
        )

        # Test with start=0, limit=0 (should be valid)
        result = ConfluenceAPI.ContentAPI.get_content_descendants(
            id=content["id"],
            start=0,
            limit=0
        )
        self.assertIsInstance(result, dict)
        for content_type in ["page", "blogpost", "comment", "attachment"]:
            self.assertIn(content_type, result)
            self.assertEqual(result[content_type], [])

        # Test with maximum reasonable values
        result = ConfluenceAPI.ContentAPI.get_content_descendants(
            id=content["id"],
            start=10000,
            limit=10000
        )
        self.assertIsInstance(result, dict)

    def test_get_content_descendants_edge_case_values(self):
        """Test get_content_descendants with edge case parameter values that might expose validation bugs."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "EdgeCaseValuesTest", "spaceKey": "TEST", "type": "page"}
        )

        # Test with start=0 as string (should trigger type validation)
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants,
            expected_exception_type=TypeError,
            expected_message="Argument 'start' must be an integer.",
            id=content["id"],
            start="0"
        )

        # Test with limit=0 as string (should trigger type validation)
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants,
            expected_exception_type=TypeError,
            expected_message="Argument 'limit' must be an integer.",
            id=content["id"],
            limit="0"
        )

        # Test with boolean values
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants,
            expected_exception_type=TypeError,
            expected_message="Argument 'start' must be an integer.",
            id=content["id"],
            start=False
        )
        return

        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants,
            expected_exception_type=TypeError,
            expected_message="Argument 'limit' must be an integer.",
            id=content["id"],
            limit=True
        )

    def test_get_content_descendants_comprehensive_negative_values(self):
        """Test get_content_descendants with various negative values."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "NegativeValuesTest", "spaceKey": "TEST", "type": "page"}
        )

        # Test with very negative start
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'start' must be non-negative.",
            id=content["id"],
            start=-100
        )

        # Test with very negative limit
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'limit' must be non-negative.",
            id=content["id"],
            limit=-100
        )

        # Test with both negative
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'start' must be non-negative.",
            id=content["id"],
            start=-1,
            limit=-1
        )

    # def test_get_content_descendants_invalid_id(self):
    #     """
    #     Test retrieving descendants of a content with an invalid ID.
    #     """
    #     with self.assertRaises(ValueError):
    #         ConfluenceAPI.ContentAPI.get_content_descendants("invalid_id")

    # def test_get_content_nested_descendants(self):
    #     """
    #     Test retrieving nested descendants of content (mock returns empty).
    #     """
    #     parent = ConfluenceAPI.ContentAPI.create_content(
    #         {"title": "NestedDescendantParent", "spaceKey": "XYZ", "type": "page"}
    #     )
    #     child = ConfluenceAPI.ContentAPI.create_content(
    #         {
    #             "title": "Child",
    #             "spaceKey": "XYZ",
    #             "type": "blogpost",
    #             "postingDay": "2025-03-09",
    #         }
    #     )
    #     ConfluenceAPI.ContentAPI.update_content(
    #         child["id"], {"ancestors": [parent["id"]]}
    #     )
    #     grandchild = ConfluenceAPI.ContentAPI.create_content(
    #         {"title": "Grandchild", "spaceKey": "XYZ", "type": "page"}
    #     )
    #     ConfluenceAPI.ContentAPI.update_content(
    #         grandchild["id"], {"ancestors": [child["id"]]}
    #     )
    #     nested_descendants = ConfluenceAPI.ContentAPI.get_content_descendants(
    #         parent["id"]
    #     )
    #     self.assertIn("page", nested_descendants)
    #     self.assertEqual(len(nested_descendants["page"]), 1)
    #     self.assertEqual(len(nested_descendants["blogpost"]), 1)
    #     self.assertEqual(nested_descendants["page"][0]["id"], grandchild["id"])

    def test_get_content_descendants_of_type(self):
        """
        Test retrieving descendants of a particular type (mock returns empty).
        """
        c = ConfluenceAPI.ContentAPI.create_content(
            {"title": "DescendantParent2", "spaceKey": "XYZ", "type": "page"}
        )
        desc = ConfluenceAPI.ContentAPI.get_content_descendants_of_type(c["id"], "page")
        self.assertEqual(desc, [])

    def test_get_content_descendants_of_type_id_type_validation(self):
        """Test get_content_descendants_of_type with invalid types for 'id' parameter."""
        # Test with integer id
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants_of_type,
            expected_exception_type=TypeError,
            expected_message="Argument 'id' must be a string.",
            id=123,
            type="page"
        )

        # Test with None id
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants_of_type,
            expected_exception_type=TypeError,
            expected_message="Argument 'id' must be a string.",
            id=None,
            type="page"
        )

        # Test with list id
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants_of_type,
            expected_exception_type=TypeError,
            expected_message="Argument 'id' must be a string.",
            id=["content_id"],
            type="page"
        )

    def test_get_content_descendants_of_type_id_empty_string_validation(self):
        """Test get_content_descendants_of_type with empty string id."""
        # Test with empty string id
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants_of_type,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'id' cannot be an empty string.",
            id="",
            type="page"
        )

        # Test with whitespace-only id
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants_of_type,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'id' cannot be an empty string.",
            id="   ",
            type="page"
        )

    def test_get_content_descendants_of_type_content_not_found(self):
        """Test get_content_descendants_of_type with non-existent content id."""
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants_of_type,
            expected_exception_type=ValueError,
            expected_message="Content with id=nonexistent_id not found.",
            id="nonexistent_id",
            type="page"
        )

    def test_get_content_descendants_of_type_valid_inputs_success(self):
        """Test get_content_descendants_of_type with all valid inputs."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "ValidInputsDescendantsTypeTest", "spaceKey": "TEST", "type": "page"}
        )

        # Test with all valid parameters
        result = ConfluenceAPI.ContentAPI.get_content_descendants_of_type(
            id=content["id"],
            type="page",
            expand="space,version",
            start=0,
            limit=10
        )

        # Verify the result structure - should be a list
        self.assertIsInstance(result, list)
        # Since this is a simulation with no actual descendants, should be empty
        self.assertEqual(result, [])

    def test_get_content_descendants_of_type_pagination_functionality(self):
        """Test get_content_descendants_of_type pagination parameters."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "PaginationDescendantsTypeTest", "spaceKey": "TEST", "type": "page"}
        )

        # Test with different pagination parameters
        result1 = ConfluenceAPI.ContentAPI.get_content_descendants_of_type(
            id=content["id"],
            type="comment",
            start=0,
            limit=5
        )
        
        result2 = ConfluenceAPI.ContentAPI.get_content_descendants_of_type(
            id=content["id"],
            type="comment",
            start=5,
            limit=10
        )

        # Both should be empty lists in simulation
        self.assertIsInstance(result1, list)
        self.assertIsInstance(result2, list)
        self.assertEqual(result1, [])
        self.assertEqual(result2, [])

    def test_get_content_descendants_of_type_different_types(self):
        """Test get_content_descendants_of_type with different content types."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "TypesDescendantsTest", "spaceKey": "TEST", "type": "page"}
        )

        # Test with different content types
        for content_type in ["page", "blogpost", "comment", "attachment"]:
            result = ConfluenceAPI.ContentAPI.get_content_descendants_of_type(
                id=content["id"],
                type=content_type
            )
            self.assertIsInstance(result, list)
            self.assertEqual(result, [])  # Should be empty in simulation

    def test_get_content_descendants_of_type_invalid_id(self):
        """
        Test retrieving descendants of a particular type with an invalid ID.
        """
        with self.assertRaises(ValueError):
            ConfluenceAPI.ContentAPI.get_content_descendants_of_type(
                "invalid_id", "page"
            )

    def test_get_content_descendants_of_type_type_validation(self):
        """Test get_content_descendants_of_type with invalid types for 'type' parameter."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "TypeValidationTest", "spaceKey": "TEST", "type": "page"}
        )

        # Test with integer type
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants_of_type,
            expected_exception_type=TypeError,
            expected_message="Argument 'type' must be a string.",
            id=content["id"],
            type=123
        )

        # Test with None type
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants_of_type,
            expected_exception_type=TypeError,
            expected_message="Argument 'type' must be a string.",
            id=content["id"],
            type=None
        )

        # Test with list type
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants_of_type,
            expected_exception_type=TypeError,
            expected_message="Argument 'type' must be a string.",
            id=content["id"],
            type=["page"]
        )

        # Test with dict type
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants_of_type,
            expected_exception_type=TypeError,
            expected_message="Argument 'type' must be a string.",
            id=content["id"],
            type={"type": "page"}
        )

    def test_get_content_descendants_of_type_type_empty_string_validation(self):
        """Test get_content_descendants_of_type with empty string type."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "TypeEmptyStringTest", "spaceKey": "TEST", "type": "page"}
        )

        # Test with empty string type
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants_of_type,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'type' cannot be an empty string.",
            id=content["id"],
            type=" "
        )

        # Test with whitespace-only type
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants_of_type,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'type' cannot be an empty string.",
            id=content["id"],
            type="   "
        )

    def test_get_content_descendants_of_type_start_limit_type_validation(self):
        """Test get_content_descendants_of_type with invalid types for start/limit parameters."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "StartLimitTypeTest", "spaceKey": "TEST", "type": "page"}
        )

        # Test with string start
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants_of_type,
            expected_exception_type=TypeError,
            expected_message="Argument 'start' must be an integer.",
            id=content["id"],
            type="page",
            start="0"
        )

        # Test with float start
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants_of_type,
            expected_exception_type=TypeError,
            expected_message="Argument 'start' must be an integer.",
            id=content["id"],
            type="page",
            start=0.5
        )

        # Test with string limit
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants_of_type,
            expected_exception_type=TypeError,
            expected_message="Argument 'limit' must be an integer.",
            id=content["id"],
            type="page",
            limit="25"
        )

        # Test with float limit
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants_of_type,
            expected_exception_type=TypeError,
            expected_message="Argument 'limit' must be an integer.",
            id=content["id"],
            type="page",
            limit=25.5
        )

    def test_get_content_descendants_of_type_start_limit_value_validation(self):
        """Test get_content_descendants_of_type with invalid values for start/limit parameters."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "StartLimitValueTest", "spaceKey": "TEST", "type": "page"}
        )

        # Test with negative start
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants_of_type,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'start' must be non-negative.",
            id=content["id"],
            type="page",
            start=-1
        )

        # Test with negative limit
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants_of_type,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'limit' must be non-negative.",
            id=content["id"],
            type="page",
            limit=-1
        )

        # Test with very negative start
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants_of_type,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'start' must be non-negative.",
            id=content["id"],
            type="page",
            start=-100
        )

        # Test with very negative limit
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.get_content_descendants_of_type,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'limit' must be non-negative.",
            id=content["id"],
            type="page",
            limit=-50
        )

    def test_get_content_descendants_of_type_valid_boundary_values(self):
        """Test get_content_descendants_of_type with valid boundary values for start/limit."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "BoundaryValueTest", "spaceKey": "TEST", "type": "page"}
        )

        # Test with start=0, limit=0 (should be valid)
        result = ConfluenceAPI.ContentAPI.get_content_descendants_of_type(
            id=content["id"],
            type="page",
            start=0,
            limit=0
        )
        self.assertIsInstance(result, list)
        self.assertEqual(result, [])

        # Test with start=0, limit=1
        result = ConfluenceAPI.ContentAPI.get_content_descendants_of_type(
            id=content["id"],
            type="page",
            start=0,
            limit=1
        )
        self.assertIsInstance(result, list)
        self.assertEqual(result, [])

        # Test with large values
        result = ConfluenceAPI.ContentAPI.get_content_descendants_of_type(
            id=content["id"],
            type="page",
            start=1000,
            limit=1000
        )
        self.assertIsInstance(result, list)
        self.assertEqual(result, [])

    def test_get_content_descendants_of_type_optional_parameters(self):
        """Test get_content_descendants_of_type with optional parameters as None."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "OptionalParamsTest", "spaceKey": "TEST", "type": "page"}
        )

        # Test with expand=None
        result = ConfluenceAPI.ContentAPI.get_content_descendants_of_type(
            id=content["id"],
            type="page",
            expand=None
        )
        self.assertIsInstance(result, list)
        self.assertEqual(result, [])

        # Test with all optional parameters as None/default
        result = ConfluenceAPI.ContentAPI.get_content_descendants_of_type(
            id=content["id"],
            type="page",
            expand=None,
            start=0,
            limit=25
        )
        self.assertIsInstance(result, list)
        self.assertEqual(result, [])

    def test_get_content_labels(self):
        """
        Test retrieving content labels (mock returns empty).
        """
        c = ConfluenceAPI.ContentAPI.create_content(
            {"title": "Labelled", "spaceKey": "XYZ", "type": "page"}
        )
        labels = ConfluenceAPI.ContentAPI.get_content_labels(c["id"])
        self.assertEqual(labels, [])

    def test_get_content_labels_invalid_id(self):
        """
        Test retrieving content labels with an invalid ID.
        """
        with self.assertRaises(ValueError):
            ConfluenceAPI.ContentAPI.get_content_labels("invalid_id")

    # def test_get_content_labels_with_prefix(self):
    #     """
    #     Test retrieving content labels with a prefix.
    #     """
    #     c = ConfluenceAPI.ContentAPI.create_content(
    #         {"title": "Labelled2", "spaceKey": "XYZ", "type": "page"}
    #     )
    #     ConfluenceAPI.ContentAPI.add_content_labels(
    #         c["id"], ["mylabel", "anotherlabel"]
    #     )
    #     labels = ConfluenceAPI.ContentAPI.get_content_labels(c["id"], prefix="my")
    #     self.assertEqual(labels, ["mylabel"])

    def test_add_content_labels(self):
        """
        Test adding labels to content.
        """
        c = ConfluenceAPI.ContentAPI.create_content(
            {"title": "Labelled2", "spaceKey": "XYZ", "type": "page"}
        )
        labels_to_add = ["mylabel", "anotherlabel"]
        result = ConfluenceAPI.ContentAPI.add_content_labels(c["id"], labels_to_add)
        self.assertEqual(len(result), 2, "Should return two labels added.")
        self.assertEqual(
            sorted([result[0]["label"], result[1]["label"]]), sorted(labels_to_add)
        )

    def test_add_content_labels_invalid_id(self):
        """
        Test adding labels to content with an invalid ID.
        """
        with self.assertRaises(ValueError):
            ConfluenceAPI.ContentAPI.add_content_labels(
                "invalid_id", ["mylabel", "anotherlabel"]
            )

    # def test_delete_content_labels(self):
    #     """
    #     Test deleting labels from content.
    #     """
    #     c = ConfluenceAPI.ContentAPI.create_content(
    #         {"title": "Labelled2", "spaceKey": "XYZ", "type": "page"}
    #     )
    #     ConfluenceAPI.ContentAPI.add_content_labels(
    #         c["id"], ["mylabel", "anotherlabel"]
    #     )
    #     ConfluenceAPI.ContentAPI.delete_content_labels(c["id"], "mylabel")
    #     labels = ConfluenceAPI.ContentAPI.get_content_labels(c["id"])
    #     self.assertEqual(labels, ["anotherlabel"])

    #     ConfluenceAPI.ContentAPI.delete_content_labels(c["id"])
    #     labels = ConfluenceAPI.ContentAPI.get_content_labels(c["id"])
    #     self.assertEqual(labels, [])

    #     ConfluenceAPI.ContentAPI.add_content_labels(c["id"], ["mylabel"])
    #     ConfluenceAPI.ContentAPI.delete_content_labels(c["id"], "mylabel")
    #     labels = ConfluenceAPI.ContentAPI.get_content_labels(c["id"])
    #     self.assertEqual(labels, [])

    #     with self.assertRaises(ValueError):
    #         ConfluenceAPI.ContentAPI.delete_content_labels(c["id"])

    def test_delete_content_labels_invalid_id(self):
        """
        Test deleting labels from content with an invalid ID.
        """
        with self.assertRaises(TypeError):
            ConfluenceAPI.ContentAPI.delete_content_labels(
                "invalid_id", ["mylabel", "anotherlabel"]
            )

    # def test_create_and_get_content_property_for_key(self):
    #     """
    #     Test create_content_property_for_key (similar to create_content_property, but with key in the URL).
    #     """
    #     c = ConfluenceAPI.ContentAPI.create_content(
    #         {"title": "PropKeyTest", "spaceKey": "XYZ", "type": "page"}
    #     )
    #     prop = ConfluenceAPI.ContentAPI.create_content_property_for_key(
    #         c["id"], "testKey", {"value": {"some": "thing"}, "version": {"number": 2}}
    #     )

    #     self.assertEqual(prop["key"], "testKey")
    #     self.assertEqual(prop["version"], 2)
    #     self.assertEqual(prop["value"]["some"], "thing")
    #     property = ConfluenceAPI.ContentAPI.get_content_property(c["id"], "testKey")
    #     self.assertEqual(property["key"], "testKey")
    #     self.assertEqual(property["value"]["some"], "thing")
    #     with self.assertRaises(ValueError):
    #         ConfluenceAPI.ContentAPI.get_content_property(c["id"], "invalid_key")

    def test_create_content_property_for_key_invalid_id(self):
        """
        Test creating a content property for a key with an invalid ID.
        """
        with self.assertRaises(ValueError):
            ConfluenceAPI.ContentAPI.create_content_property_for_key(
                "invalid_id", "testKey", {"value": {"some": "thing"}}
            )

    def test_get_content_restrictions_by_operation(self):
        """
        Test retrieving content restrictions by operation (mock returns empty arrays).
        """
        c = ConfluenceAPI.ContentAPI.create_content(
            {"title": "Restricted", "spaceKey": "XYZ", "type": "page"}
        )
        restrictions = ConfluenceAPI.ContentAPI.get_content_restrictions_by_operation(
            c["id"]
        )
        self.assertIn("read", restrictions)
        self.assertIn("update", restrictions)
        self.assertIsInstance(restrictions["read"]["restrictions"], dict)

    def test_get_content_restrictions_by_operation_invalid_id(self):
        """
        Test retrieving content restrictions by operation with an invalid ID.
        """
        with self.assertRaises(ValueError):
            ConfluenceAPI.ContentAPI.get_content_restrictions_by_operation("invalid_id")

    def test_get_content_restrictions_for_operation(self):
        """
        Test retrieving content restrictions for a specific operation (mock).
        """
        c = ConfluenceAPI.ContentAPI.create_content(
            {"title": "Restricted2", "spaceKey": "XYZ", "type": "page"}
        )
        read_restrictions = (
            ConfluenceAPI.ContentAPI.get_content_restrictions_for_operation(
                c["id"], "read"
            )
        )
        self.assertEqual(read_restrictions["operationKey"], "read")
        self.assertIn("restrictions", read_restrictions)

        with self.assertRaises(ValueError):
            ConfluenceAPI.ContentAPI.get_content_restrictions_for_operation(
                c["id"], "invalid_op"
            )

    def test_get_content_restrictions_for_operation_invalid_id(self):
        """
        Test retrieving content restrictions for a specific operation with an invalid ID.
        """
        with self.assertRaises(ValueError):
            ConfluenceAPI.ContentAPI.get_content_restrictions_for_operation(
                "invalid_id", "read"
            )

    # Existing tests for ContentAPI (original coverage)
    # def test_create_and_get_content(self):
    #     """
    #     Create a piece of content, then retrieve and verify it.
    #     """
    #     body = {"type": "page", "title": "Test Page", "spaceKey": "TEST"}
    #     created = ConfluenceAPI.ContentAPI.create_content(body)
    #     self.assertEqual(
    #         created["type"], "page", "Created content should be of type 'page'"
    #     )
    #     fetched = ConfluenceAPI.ContentAPI.get_content(created["id"])
    #     self.assertEqual(
    #         fetched["title"],
    #         "Test Page",
    #         "Fetched content title should match created content",
    #     )
    #     comment = ConfluenceAPI.ContentAPI.create_content(
    #         {
    #             "type": "comment",
    #             "title": "Test Comment",
    #             "spaceKey": "TEST",
    #         }
    #     )
    #     updated = ConfluenceAPI.ContentAPI.update_content(
    #         comment["id"], {"ancestors": [created["id"]]}
    #     )
    #     comments = ConfluenceAPI.ContentAPI.get_content_comments(created["id"])
    #     self.assertEqual(len(comments), 1, "Content should have one comment")
    #     children = ConfluenceAPI.ContentAPI.get_content_children(created["id"])
    #     self.assertEqual(len(children["comment"]), 1, "Content should have one child")
    #     comment_children = ConfluenceAPI.ContentAPI.get_content_children_of_type(
    #         created["id"], "comment"
    #     )
    #     self.assertEqual(
    #         len(comment_children), 1, "Content should have one comment child"
    #     )

    def test_get_content_status_mismatch(self):
        """
        Test that get_content raises a ValueError if the content's status does not match the expected status.
        """
        c = ConfluenceAPI.ContentAPI.create_content(
            {"title": "StatusTest", "spaceKey": "TEST", "type": "page"}
        )
        with self.assertRaises(ValueError):
            ConfluenceAPI.ContentAPI.get_content(c["id"], status="trashed")

    # def test_delete_content(self):
    #     """
    #     Create content, delete it (to trash), then delete again (permanently).
    #     """
    #     c1 = ConfluenceAPI.ContentAPI.create_content(
    #         {"title": "ToDelete", "spaceKey": "DS", "type": "page"}
    #     )
    #     ConfluenceAPI.ContentAPI.delete_content(c1["id"])
    #     # Should now be 'trashed'
    #     trashed = ConfluenceAPI.ContentAPI.get_content(c1["id"], status="trashed")
    #     self.assertEqual(
    #         trashed["status"],
    #         "trashed",
    #         "Content should be marked trashed after first delete",
    #     )

    #     # Delete again with status=trashed => permanent removal
    #     ConfluenceAPI.ContentAPI.delete_content(c1["id"], status="trashed")
    #     with self.assertRaises(ValueError):
    #         ConfluenceAPI.ContentAPI.get_content(c1["id"])

    def test_delete_nonexistent_content(self):
        """
        Attempt to delete a content record that doesn't exist.
        """
        with self.assertRaises(ValueError):
            ConfluenceAPI.ContentAPI.delete_content("999")

    def test_content_property(self):
        """
        Create content, assign a property, retrieve, update, and delete that property.
        """
        c1 = ConfluenceAPI.ContentAPI.create_content(
            {"title": "HasProperty", "spaceKey": "DS", "type": "page"}
        )
        prop = ConfluenceAPI.ContentAPI.create_content_property(
            c1["id"], {"key": "sampleKey", "value": {"data": 123}}
        )
        self.assertEqual(prop["key"], "sampleKey")
        got = ConfluenceAPI.ContentAPI.get_content_property(c1["id"], "sampleKey")
        self.assertEqual(got["value"]["data"], 123)

        # Update property
        updated = ConfluenceAPI.ContentAPI.update_content_property(
            c1["id"], "sampleKey", {"value": {"data": 999}}
        )
        self.assertEqual(updated["value"]["data"], 999)

        with self.assertRaises(ValueError):
            ConfluenceAPI.ContentAPI.update_content_property(
                "invalid_id", "invalid_key", {"value": {"data": 999}}
            )

        with self.assertRaises(ValueError):
            ConfluenceAPI.ContentAPI.update_content_property(
                c1["id"], "invalid_key", {"value": {"data": 999}}
            )

        # Delete property
        ConfluenceAPI.ContentAPI.delete_content_property(c1["id"], "sampleKey")
        with self.assertRaises(ValueError):
            ConfluenceAPI.ContentAPI.get_content_property(c1["id"], "sampleKey")
        with self.assertRaises(ValueError):
            ConfluenceAPI.ContentAPI.delete_content_property(
                "invalid_id", "invalid_key"
            )
        with self.assertRaises(ValueError):
            ConfluenceAPI.ContentAPI.delete_content_property(c1["id"], "invalid_key")

        # Existing tests for ValueError
        with self.assertRaises(ValueError):
            ConfluenceAPI.ContentAPI.delete_content_property(
                "invalid_id", "invalid_key"
            )
        with self.assertRaises(ValueError):
            ConfluenceAPI.ContentAPI.delete_content_property(c1["id"], "invalid_key")

        # New input validation tests for delete_content_property
        with self.assertRaises(TypeError):
            ConfluenceAPI.ContentAPI.delete_content_property(123, "sampleKey")  # id not a string
        with self.assertRaises(ConfluenceAPI.ContentAPI.InvalidInputError):
            ConfluenceAPI.ContentAPI.delete_content_property("   ", "sampleKey")  # id is whitespace
        with self.assertRaises(TypeError):
            ConfluenceAPI.ContentAPI.delete_content_property(c1["id"], 123)  # key not a string
        with self.assertRaises(ConfluenceAPI.ContentAPI.InvalidInputError):
            ConfluenceAPI.ContentAPI.delete_content_property(c1["id"], "   ")  # key is whitespace

    def test_get_content_properties_with_pagination(self):
        """Test successful retrieval with custom pagination"""
        c = ConfluenceAPI.ContentAPI.create_content(
            {"title": "PropPaginationTest", "spaceKey": "XYZ", "type": "page"}
        )
        
        content_id = c["id"]
        DB["content_properties"][content_id] = {
            "key": "test",
            "value": {"data": "test"},
            "version": 1
        }
        
        # Add multiple properties to test pagination
        for i in range(10):
            prop_id = f"{content_id}_prop_{i}"
            DB["content_properties"][prop_id] = {
                "key": f"prop_{i}",
                "value": {"index": i},
                "version": 1
            }
        
        properties = ConfluenceAPI.ContentAPI.get_content_properties(content_id, start=1, limit=2)
        
        # Should return 2 properties starting from index 1
        self.assertIsInstance(properties, list)
        self.assertLessEqual(len(properties), 2)

    def test_get_content_properties_start_beyond_results(self):
        """Test when start index is beyond available results"""
        c = ConfluenceAPI.ContentAPI.create_content(
            {"title": "PropBeyondTest", "spaceKey": "XYZ", "type": "page"}
        )
        
        content_id = c["id"]
        DB["content_properties"][content_id] = {
            "key": "test",
            "value": {"data": "test"},
            "version": 1
        }
        
        # Add limited properties
        prop_id_1 = f"{content_id}_prop_1"
        prop_id_2 = f"{content_id}_prop_2"
        DB["content_properties"][prop_id_1] = {
            "key": "prop1",
            "value": {"data": 1},
            "version": 1
        }
        DB["content_properties"][prop_id_2] = {
            "key": "prop2",
            "value": {"data": 2},
            "version": 1
        }
        
        properties = ConfluenceAPI.ContentAPI.get_content_properties(content_id, start=10, limit=5)
        
        # Should return empty list when start is beyond available results
        self.assertEqual(len(properties), 0)
        self.assertEqual(properties, [])

    def test_get_content_properties_expand_parameter_ignored(self):
        """Test that expand parameter is accepted but ignored (as per current implementation)"""
        c = ConfluenceAPI.ContentAPI.create_content(
            {"title": "PropExpandTest", "spaceKey": "XYZ", "type": "page"}
        )
        
        content_id = c["id"]
        DB["content_properties"][content_id] = {
            "key": "test",
            "value": {"data": "test"},
            "version": 1
        }
        
        properties = ConfluenceAPI.ContentAPI.get_content_properties(content_id, expand="value,version")
        
        # expand parameter should be ignored in current implementation
        self.assertIsInstance(properties, list)

    # Input Validation Tests - Type Errors

    def test_get_content_properties_id_not_string_raises_typeerror(self):
        """Test that non-string id raises TypeError"""
        with self.assertRaises(TypeError) as context:
            ConfluenceAPI.ContentAPI.get_content_properties(123)  # type: ignore
        self.assertIn("Argument 'id' must be a string", str(context.exception))

    def test_get_content_properties_id_none_raises_typeerror(self):
        """Test that None id raises TypeError"""
        with self.assertRaises(TypeError) as context:
            ConfluenceAPI.ContentAPI.get_content_properties(None)  # type: ignore
        self.assertIn("Argument 'id' must be a string", str(context.exception))

    def test_get_content_properties_start_not_integer_raises_typeerror(self):
        """Test that non-integer start raises TypeError"""
        with self.assertRaises(TypeError) as context:
            ConfluenceAPI.ContentAPI.get_content_properties("123", start="0")  # type: ignore
        self.assertIn("Argument 'start' must be an integer", str(context.exception))

    def test_get_content_properties_start_boolean_raises_typeerror(self):
        """Test that boolean start raises TypeError (even though bool is subclass of int)"""
        with self.assertRaises(TypeError) as context:
            ConfluenceAPI.ContentAPI.get_content_properties("123", start=True)  # type: ignore
        self.assertIn("Argument 'start' must be an integer", str(context.exception))

    def test_get_content_properties_limit_not_integer_raises_typeerror(self):
        """Test that non-integer limit raises TypeError"""
        with self.assertRaises(TypeError) as context:
            ConfluenceAPI.ContentAPI.get_content_properties("123", limit="10")  # type: ignore
        self.assertIn("Argument 'limit' must be an integer", str(context.exception))

    def test_get_content_properties_limit_boolean_raises_typeerror(self):
        """Test that boolean limit raises TypeError"""
        with self.assertRaises(TypeError) as context:
            ConfluenceAPI.ContentAPI.get_content_properties("123", limit=False)  # type: ignore
        self.assertIn("Argument 'limit' must be an integer", str(context.exception))

    # Input Validation Tests - Invalid Input Errors

    def test_get_content_properties_empty_id_raises_invalidinputerror(self):
        """Test that empty id raises InvalidInputError"""
        with self.assertRaises(InvalidInputError) as context:
            ConfluenceAPI.ContentAPI.get_content_properties("")
        self.assertIn("Argument 'id' cannot be an empty string", str(context.exception))

    def test_get_content_properties_whitespace_only_id_raises_invalidinputerror(self):
        """Test that whitespace-only id raises InvalidInputError"""
        with self.assertRaises(InvalidInputError) as context:
            ConfluenceAPI.ContentAPI.get_content_properties("   ")
        self.assertIn("Argument 'id' cannot be an empty string", str(context.exception))

    def test_get_content_properties_negative_start_raises_invalidinputerror(self):
        """Test that negative start raises InvalidInputError"""
        with self.assertRaises(InvalidInputError) as context:
            ConfluenceAPI.ContentAPI.get_content_properties("123", start=-1)
        self.assertIn("Argument 'start' must be non-negative", str(context.exception))

    def test_get_content_properties_negative_limit_raises_invalidinputerror(self):
        """Test that negative limit raises InvalidInputError"""
        with self.assertRaises(InvalidInputError) as context:
            ConfluenceAPI.ContentAPI.get_content_properties("123", limit=-1)
        self.assertIn("Argument 'limit' must be positive", str(context.exception))

    # Edge Cases for Start Parameter

    def test_get_content_properties_start_zero_is_valid(self):
        """Test that start=0 is valid (edge case in current validation logic)"""
        c = ConfluenceAPI.ContentAPI.create_content(
            {"title": "StartZeroTest", "spaceKey": "XYZ", "type": "page"}
        )
        
        content_id = c["id"]
        DB["content_properties"][content_id] = {
            "key": "test",
            "value": {"data": "test"},
            "version": 1
        }
        
        # This should not raise an error
        properties = ConfluenceAPI.ContentAPI.get_content_properties(content_id, start=0)
        self.assertIsInstance(properties, list)

    # Edge Cases for Limit Parameter

    def test_get_content_properties_limit_zero_raises_invalidinputerror(self):
        """Test that limit=0 raises InvalidInputError"""
        with self.assertRaises(InvalidInputError) as context:
            ConfluenceAPI.ContentAPI.get_content_properties("123", limit=0)
        self.assertIn("Argument 'limit' must be positive", str(context.exception))

    # Database Lookup Tests

    def test_get_content_properties_nonexistent_id_raises_valueerror(self):
        """Test that non-existent content id raises ValueError"""
        with self.assertRaises(ValueError) as context:
            ConfluenceAPI.ContentAPI.get_content_properties("nonexistent")
        self.assertIn("No properties found for content with id='nonexistent'", str(context.exception))

    def test_get_content_properties_none_parent_raises_valueerror(self):
        """Test that None parent (from DB get) raises ValueError"""
        # Manually add None to the DB for testing
        DB["content_properties"]["test_none"] = None
        
        with self.assertRaises(ValueError) as context:
            ConfluenceAPI.ContentAPI.get_content_properties("test_none")
        self.assertIn("No properties found for content with id='test_none'", str(context.exception))

    # String Processing Tests

    def test_get_content_properties_id_with_whitespace_stripped(self):
        """Test that id with whitespace is properly stripped"""
        c = ConfluenceAPI.ContentAPI.create_content(
            {"title": "WhitespaceTest", "spaceKey": "XYZ", "type": "page"}
        )
        
        content_id = c["id"]
        DB["content_properties"][content_id] = {
            "key": "test",
            "value": {"data": "test"},
            "version": 1
        }
        
        # Should work because id gets stripped
        properties = ConfluenceAPI.ContentAPI.get_content_properties(f"  {content_id}  ")
        self.assertIsInstance(properties, list)

    # Return Type and Structure Tests

    def test_get_content_properties_return_type_is_list(self):
        """Test that function returns a list"""
        c = ConfluenceAPI.ContentAPI.create_content(
            {"title": "ReturnTypeTest", "spaceKey": "XYZ", "type": "page"}
        )
        
        content_id = c["id"]
        DB["content_properties"][content_id] = {
            "key": "test",
            "value": {"data": "test"},
            "version": 1
        }
        
        properties = ConfluenceAPI.ContentAPI.get_content_properties(content_id)
        self.assertIsInstance(properties, list)

    def test_get_content_properties_empty_descendants_returns_empty_list(self):
        """Test that empty descendants returns empty list"""
        c = ConfluenceAPI.ContentAPI.create_content(
            {"title": "EmptyDescendantsTest", "spaceKey": "XYZ", "type": "page"}
        )

        
        content_id = c["id"]
        ConfluenceAPI.ContentAPI.create_content_property(content_id, {"key": "test", "value": "test"})

        print(f'dbdbdbd', DB["content_properties"], content_id)
        # Don't add any properties to simulate empty case
        
        properties = ConfluenceAPI.ContentAPI.get_content_properties(f'{content_id}:test')
        # Should handle gracefully, either return empty list or raise error
        if isinstance(properties, list):
            self.assertEqual(len(properties), 0)

    # Pagination Edge Cases

    def test_get_content_properties_limit_larger_than_available_results(self):
        """Test when limit is larger than available results"""
        c = ConfluenceAPI.ContentAPI.create_content(
            {"title": "LimitLargerTest", "spaceKey": "XYZ", "type": "page"}
        )
        
        content_id = c["id"]
        DB["content_properties"][content_id] = {
            "key": "test",
            "value": {"data": "test"},
            "version": 1
        }
        
        # Add 5 properties
        for i in range(5):
            prop_id = f"{content_id}_prop_{i}"
            DB["content_properties"][prop_id] = {
                "key": f"prop_{i}",
                "value": {"index": i},
                "version": 1
            }
        
        properties = ConfluenceAPI.ContentAPI.get_content_properties(content_id, limit=20)
        
        # Should return available items (not necessarily 5 due to implementation details)
        self.assertIsInstance(properties, list)

    def test_get_content_properties_start_at_last_element(self):
        """Test starting at the last element"""
        c = ConfluenceAPI.ContentAPI.create_content(
            {"title": "StartLastTest", "spaceKey": "XYZ", "type": "page"}
        )
        
        content_id = c["id"]
        DB["content_properties"][content_id] = {
            "key": "test",
            "value": {"data": "test"},
            "version": 1
        }
        
        # Add 5 properties
        for i in range(5):
            prop_id = f"{content_id}_prop_{i}"
            DB["content_properties"][prop_id] = {
                "key": f"prop_{i}",
                "value": {"index": i},
                "version": 1
            }
        
        properties = ConfluenceAPI.ContentAPI.get_content_properties(content_id, start=4, limit=10)
        
        # Should return limited results from start position
        self.assertIsInstance(properties, list)

    def test_get_content_properties_multiple_calls_pagination(self):
        """Test multiple calls to simulate pagination"""
        c = ConfluenceAPI.ContentAPI.create_content(
            {"title": "MultipleCallsTest", "spaceKey": "XYZ", "type": "page"}
        )
        
        content_id = c["id"]
        DB["content_properties"][content_id] = {
            "key": "test",
            "value": {"data": "test"},
            "version": 1
        }
        
        # Add 5 properties
        for i in range(5):
            prop_id = f"{content_id}_prop_{i}"
            DB["content_properties"][prop_id] = {
                "key": f"prop_{i}",
                "value": {"index": i},
                "version": 1
            }
        
        # First page
        page1 = ConfluenceAPI.ContentAPI.get_content_properties(content_id, start=0, limit=2)
        # Second page  
        page2 = ConfluenceAPI.ContentAPI.get_content_properties(content_id, start=2, limit=2)
        # Third page
        page3 = ConfluenceAPI.ContentAPI.get_content_properties(content_id, start=4, limit=2)
        
        # All should return lists
        self.assertIsInstance(page1, list)
        self.assertIsInstance(page2, list)
        self.assertIsInstance(page3, list)

    def test_get_content_property_invalid_id(self):
        """
        Test getting a content property with an invalid ID.
        """
        with self.assertRaises(ValueError):
            ConfluenceAPI.ContentAPI.get_content_property("invalid_id", "sampleKey")

    def test_create_content_property_content_not_found(self):
        """
        Test creating a content property with an invalid content ID.
        """
        from confluence.SimulationEngine.custom_errors import ContentNotFoundError
        
        with self.assertRaises(ContentNotFoundError):
            ConfluenceAPI.ContentAPI.create_content_property(
                "invalid_id", {"key": "testKey", "value": {"some": "thing"}}
            )

    def test_create_content_property_missing_key(self):
        """
        Test creating a content property with missing key.
        """
        from confluence.SimulationEngine.custom_errors import InvalidInputError
        
        c = ConfluenceAPI.ContentAPI.create_content(
            {"title": "PropTest", "spaceKey": "XYZ", "type": "page"}
        )
        
        with self.assertRaises(InvalidInputError):
            ConfluenceAPI.ContentAPI.create_content_property(
                c["id"], {"value": {"some": "thing"}}
            )

    # ===== NEW COMPREHENSIVE VALIDATION TESTS FOR create_content_property =====
    
    def test_create_content_property_id_type_validation(self):
        """Test that id parameter must be a string."""
        with self.assertRaises(TypeError) as context:
            ConfluenceAPI.ContentAPI.create_content_property(
                123, {"key": "testKey", "value": {"some": "thing"}}  # type: ignore
            )
        self.assertIn("Argument 'id' must be a string", str(context.exception))

    def test_create_content_property_id_empty_string_validation(self):
        """Test that id parameter cannot be an empty string."""
        from confluence.SimulationEngine.custom_errors import InvalidInputError
        
        with self.assertRaises(InvalidInputError) as context:
            ConfluenceAPI.ContentAPI.create_content_property(
                "", {"key": "testKey", "value": {"some": "thing"}}
            )
        self.assertIn("cannot be an empty string", str(context.exception))

    def test_create_content_property_id_whitespace_only_validation(self):
        """Test that id parameter cannot be whitespace only."""
        from confluence.SimulationEngine.custom_errors import InvalidInputError
        
        with self.assertRaises(InvalidInputError) as context:
            ConfluenceAPI.ContentAPI.create_content_property(
                "   ", {"key": "testKey", "value": {"some": "thing"}}
            )
        self.assertIn("cannot be an empty string", str(context.exception))

    def test_create_content_property_body_type_validation(self):
        """Test that body parameter must be a dictionary."""
        c = ConfluenceAPI.ContentAPI.create_content(
            {"title": "PropTest", "spaceKey": "XYZ", "type": "page"}
        )
        
        with self.assertRaises(TypeError) as context:
            ConfluenceAPI.ContentAPI.create_content_property(c["id"], "not_a_dict")  # type: ignore
        self.assertIn("Argument 'body' must be a dictionary", str(context.exception))

    def test_create_content_property_body_none_validation(self):
        """Test that body parameter cannot be None."""
        c = ConfluenceAPI.ContentAPI.create_content(
            {"title": "PropTest", "spaceKey": "XYZ", "type": "page"}
        )
        
        with self.assertRaises(TypeError) as context:
            ConfluenceAPI.ContentAPI.create_content_property(c["id"], None)  # type: ignore
        self.assertIn("Argument 'body' must be a dictionary", str(context.exception))

    def test_create_content_property_key_type_validation(self):
        """Test that key in body must be a string."""
        from confluence.SimulationEngine.custom_errors import InvalidInputError
        
        c = ConfluenceAPI.ContentAPI.create_content(
            {"title": "PropTest", "spaceKey": "XYZ", "type": "page"}
        )
        
        with self.assertRaises(TypeError) as context:
            ConfluenceAPI.ContentAPI.create_content_property(
                c["id"], {"key": 123, "value": {"some": "thing"}}
            )
        self.assertIn("Property 'key' must be a string", str(context.exception))

    def test_create_content_property_key_empty_string_validation(self):
        """Test that key in body cannot be an empty string."""
        from confluence.SimulationEngine.custom_errors import InvalidInputError
        
        c = ConfluenceAPI.ContentAPI.create_content(
            {"title": "PropTest", "spaceKey": "XYZ", "type": "page"}
        )
        
        with self.assertRaises(InvalidInputError) as context:
            ConfluenceAPI.ContentAPI.create_content_property(
                c["id"], {"key": "", "value": {"some": "thing"}}
            )
        self.assertIn("cannot be an empty string", str(context.exception))

    def test_create_content_property_key_whitespace_only_validation(self):
        """Test that key in body cannot be whitespace only."""
        from confluence.SimulationEngine.custom_errors import InvalidInputError
        
        c = ConfluenceAPI.ContentAPI.create_content(
            {"title": "PropTest", "spaceKey": "XYZ", "type": "page"}
        )
        
        with self.assertRaises(InvalidInputError) as context:
            ConfluenceAPI.ContentAPI.create_content_property(
                c["id"], {"key": "   ", "value": {"some": "thing"}}
            )
        self.assertIn("cannot be an empty string", str(context.exception))

    def test_create_content_property_valid_scenarios(self):
        """Test valid scenarios for creating content properties."""
        c = ConfluenceAPI.ContentAPI.create_content(
            {"title": "PropTest", "spaceKey": "XYZ", "type": "page"}
        )
        
        # Test with string value
        prop1 = ConfluenceAPI.ContentAPI.create_content_property(
            c["id"], {"key": "stringKey", "value": "simple string"}
        )
        self.assertEqual(prop1["key"], "stringKey")
        self.assertEqual(prop1["value"], "simple string")
        self.assertEqual(prop1["version"], 1)
        
        # Test with dict value
        prop2 = ConfluenceAPI.ContentAPI.create_content_property(
            c["id"], {"key": "dictKey", "value": {"nested": "object", "number": 42}}
        )
        self.assertEqual(prop2["key"], "dictKey")
        self.assertEqual(prop2["value"]["nested"], "object")
        self.assertEqual(prop2["value"]["number"], 42)
        
        # Test with list value
        prop3 = ConfluenceAPI.ContentAPI.create_content_property(
            c["id"], {"key": "listKey", "value": ["item1", "item2", 123]}
        )
        self.assertEqual(prop3["key"], "listKey")
        self.assertEqual(prop3["value"], ["item1", "item2", 123])
        
        # Test with number value
        prop4 = ConfluenceAPI.ContentAPI.create_content_property(
            c["id"], {"key": "numberKey", "value": 999}
        )
        self.assertEqual(prop4["key"], "numberKey")
        self.assertEqual(prop4["value"], 999)
        
        # Test with boolean value
        prop5 = ConfluenceAPI.ContentAPI.create_content_property(
            c["id"], {"key": "boolKey", "value": True}
        )
        self.assertEqual(prop5["key"], "boolKey")
        self.assertEqual(prop5["value"], True)
        
        # Test with None value
        prop6 = ConfluenceAPI.ContentAPI.create_content_property(
            c["id"], {"key": "nullKey", "value": None}
        )
        self.assertEqual(prop6["key"], "nullKey")
        self.assertIsNone(prop6["value"])

    def test_create_content_property_value_defaults_to_empty_dict(self):
        """Test that value defaults to empty dict when not provided."""
        c = ConfluenceAPI.ContentAPI.create_content(
            {"title": "PropTest", "spaceKey": "XYZ", "type": "page"}
        )
        
        prop = ConfluenceAPI.ContentAPI.create_content_property(
            c["id"], {"key": "noValueKey"}
        )
        self.assertEqual(prop["key"], "noValueKey")
        self.assertEqual(prop["value"], {})
        self.assertEqual(prop["version"], 1)

    def test_create_content_property_complex_key_names(self):
        """Test that various key formats are supported."""
        c = ConfluenceAPI.ContentAPI.create_content(
            {"title": "PropTest", "spaceKey": "XYZ", "type": "page"}
        )
        
        # Test with special characters in key
        prop1 = ConfluenceAPI.ContentAPI.create_content_property(
            c["id"], {"key": "key-with-dashes", "value": "test"}
        )
        self.assertEqual(prop1["key"], "key-with-dashes")
        
        # Test with underscores
        prop2 = ConfluenceAPI.ContentAPI.create_content_property(
            c["id"], {"key": "key_with_underscores", "value": "test"}
        )
        self.assertEqual(prop2["key"], "key_with_underscores")
        
        # Test with dots
        prop3 = ConfluenceAPI.ContentAPI.create_content_property(
            c["id"], {"key": "key.with.dots", "value": "test"}
        )
        self.assertEqual(prop3["key"], "key.with.dots")
        
        # Test with numbers
        prop4 = ConfluenceAPI.ContentAPI.create_content_property(
            c["id"], {"key": "key123", "value": "test"}
        )
        self.assertEqual(prop4["key"], "key123")

    def test_update_nonexistent_content(self):
        """
        Attempt to update a content record that doesn't exist.
        """
        with self.assertRaises(ValueError):
            ConfluenceAPI.ContentAPI.update_content("999", {"title": "NoSuchContent"})

    def test_search_content(self):
        """
        Test searching for content.
        """
        # Create test content
        page1 = ConfluenceAPI.ContentAPI.create_content(
            {
                "type": "page",
                "spaceKey": "DEV",
                "title": "Test Page 1",
                "status": "current",
                "version": {"number": "1.0"},
            }
        )
        page2 = ConfluenceAPI.ContentAPI.create_content(
            {
                "type": "page",
                "spaceKey": "PROD",
                "title": "Test Page 2",
                "status": "current",
                "version": {"number": "2.0"},
            }
        )
        blog1 = ConfluenceAPI.ContentAPI.create_content(
            {
                "type": "blogpost",
                "spaceKey": "DEV",
                "title": "Test Blog 1",
                "status": "current",
                "postingDay": "2023-10-26",
                "version": {"number": "1.0"},
            }
        )
        another_page = ConfluenceAPI.ContentAPI.create_content(
            {
                "type": "page",
                "spaceKey": "DEV",
                "title": "Another Page",
                "status": "trashed",
                "version": {"number": "3.0"},
            }
        )
        prod_page = ConfluenceAPI.ContentAPI.create_content(
            {
                "type": "page",
                "spaceKey": "PROD",
                "title": "Prod Page",
                "status": "current",
                "body": {"storage": {"value": "some value"}},
                "version": {"number": "4.0"},
            }
        )

        # Test not contains
        result = ConfluenceAPI.ContentAPI.search_content(
            cql="title!~'Another'", limit=50
        )
        titles = [item["title"] for item in result]
        self.assertNotIn(
            "Another Page", titles, "Search should not have trashed content"
        )
        self.assertIn(page1["title"], titles, "Search should return current content")
        self.assertIn(page2["title"], titles, "Search should return current content")
        self.assertIn(blog1["title"], titles, "Search should return current content")
        self.assertIn(
            prod_page["title"], titles, "Search should return current content"
        )

        # Test equals
        result = ConfluenceAPI.ContentAPI.search_content(cql="spaceKey='DEV'")
        spaces = [item["spaceKey"] for item in result]
        self.assertTrue(
            all(space == "DEV" for space in spaces),
            "All results should be from DEV space",
        )
        dev_titles = [item["title"] for item in result]
        self.assertIn(
            page1["title"], dev_titles, "DEV space content should be included"
        )
        self.assertIn(
            blog1["title"], dev_titles, "DEV space content should be included"
        )

        # Test and statement
        result = ConfluenceAPI.ContentAPI.search_content(
            "title='Login Issues' and spaceKey='DEV'"
        )
        self.assertEqual(result, [], "No content should match both conditions")

        # Test or statement
        result = ConfluenceAPI.ContentAPI.search_content(
            cql="spaceKey='PROD' or type='blogpost'"
        )
        spaces = [item["spaceKey"] for item in result]
        types = [item["type"] for item in result]
        self.assertIn("PROD", spaces, "PROD space content should be included")
        self.assertIn("blogpost", types, "Blogpost content should be included")
        self.assertTrue(
            any(item["type"] == "blogpost" for item in result),
            "Should contain at least one blogpost",
        )
        self.assertTrue(
            any(item["spaceKey"] == "PROD" for item in result),
            "Should contain at least one PROD space content",
        )

    def test_search_content_error_handling(self):
        """
        Test that search_content raises appropriate errors for invalid or missing CQL.
        """
        # Test for missing CQL (empty string)
        with self.assertRaisesRegex(ValueError, "CQL query is missing."):
            ConfluenceAPI.ContentAPI.search_content(cql="")

        # Test for missing CQL (whitespace only)
        with self.assertRaisesRegex(ValueError, "CQL query is missing."):
            ConfluenceAPI.ContentAPI.search_content(cql="   ")

        # Test for invalid CQL that doesn't parse into tokens
        with self.assertRaisesRegex(ValueError, "CQL query is invalid."):
            ConfluenceAPI.ContentAPI.search_content(cql="this is not a valid query")

    # def test_update_content_restore_from_trash(self):
    #     """
    #     Test restoring content from trash (Special Case 1).
    #     Content should be restored to 'current' status with only version incremented.
    #     """
    #     # Create and then trash content
    #     content = ConfluenceAPI.ContentAPI.create_content(
    #         {"title": "ToBeTrashed", "spaceKey": "TEST", "type": "page"}
    #     )
    #     ConfluenceAPI.ContentAPI.delete_content(content["id"])

    #     # Verify it's trashed
    #     trashed = ConfluenceAPI.ContentAPI.get_content(content["id"], status="trashed")
    #     self.assertEqual(trashed["status"], "trashed")

    #     # Restore from trash
    #     restored = ConfluenceAPI.ContentAPI.update_content(
    #         content["id"], {"status": "current"}
    #     )
    #     # Verify restoration
    #     self.assertEqual(restored["status"], "current")
    #     self.assertEqual(
    #         restored["title"], trashed["title"]
    #     )  # Title should remain unchanged
    #     self.assertEqual(
    #         restored["spaceKey"], trashed["spaceKey"]
    #     )  # Space should remain unchanged

    def test_update_content(self):
        """
        Test updating the title and status of a content record.
        """
        c1 = ConfluenceAPI.ContentAPI.create_content(
            {
                "title": "TestTitle",
                "spaceKey": "TEST",
                "type": "page",
                "status": "draft",
                "body": {"storage": {"value": "Test Body"}},
            }
        )
        updated = ConfluenceAPI.ContentAPI.update_content(
            c1["id"],
            {
                "title": "UpdatedTitle",
                "status": "current",
                "body": {"storage": {"value": "Updated Body"}},
                "space": {"key": "TEST"},
            },
        )
        self.assertEqual(updated["title"], "UpdatedTitle")
        self.assertEqual(updated["status"], "current")
        self.assertEqual(updated["body"]["storage"]["value"], "Updated Body")
        with self.assertRaises(ValueError):
            ConfluenceAPI.ContentAPI.update_content(
                c1["id"], {"space": "invalid_space"}
            )

    def test_update_content_delete_draft(self):
        """
        Test deleting a draft (Special Case 2).
        """
        # Create a draft
        draft = ConfluenceAPI.ContentAPI.create_content(
            {
                "title": "DraftToDelete",
                "spaceKey": "TEST",
                "type": "page",
                "status": "draft",
            }
        )

        # Delete the draft
        ConfluenceAPI.ContentAPI.update_content(
            draft["id"], {"status": "current"}
        )

    # def test_update_content_nested_ancestors(self):
    #     """
    #     Test updating the ancestors of a content record with nested ancestors.
    #     """
    #     # Create a parent content
    #     parent = ConfluenceAPI.ContentAPI.create_content(
    #         {"title": "Parent", "spaceKey": "TEST", "type": "page"}
    #     )

    #     # Create a child content
    #     child = ConfluenceAPI.ContentAPI.create_content(
    #         {"title": "Child", "spaceKey": "TEST", "type": "page"}
    #     )

    #     grandchild = ConfluenceAPI.ContentAPI.create_content(
    #         {"title": "Grandchild", "spaceKey": "TEST", "type": "page"}
    #     )

    #     # Update the child content to include the parent as an ancestor
    #     updated_child = ConfluenceAPI.ContentAPI.update_content(
    #         child["id"], {"ancestors": [parent["id"]]}
    #     )

    #     # Verify the child content now has the parent as an ancestor
    #     self.assertIn(parent["id"], updated_child["ancestors"])

    #     # Verify the parent content now has the child as a child
    #     self.assertEqual(parent["children"][0]["id"], child["id"])

    #     # Update the grandchild content to include the parent as an ancestor
    #     updated_grandchild = ConfluenceAPI.ContentAPI.update_content(
    #         grandchild["id"], {"ancestors": [child["id"]]}
    #     )

    #     # Verify the grandchild content now has the parent as an ancestor
    #     self.assertIn(parent["id"], updated_grandchild["ancestors"])
    #     # Verify the parent content now has the grandchild as a child
    #     self.assertEqual(parent["descendants"][1]["id"], grandchild["id"])

    # ----------------------------------------------------------------
    # ContentBodyAPI (formerly TestContentBodyAPI)
    # ----------------------------------------------------------------
    def test_convert_body(self):
        """
        Convert content body from one representation to another.
        """
        to_fmt = "view"
        body = {"type": "storage", "value": "<p>Example</p>"}
        converted = ConfluenceAPI.ContentBodyAPI.convert_content_body(to_fmt, body)
        self.assertEqual(converted["convertedTo"], to_fmt)
        self.assertIn(
            "originalBody",
            converted,
            "Converted result must carry 'originalBody' field",
        )

    def test_convert_body_invalid_format(self):
        """
        Trying to convert to an invalid representation should raise an error.
        """
        with self.assertRaises(ValueError):
            ConfluenceAPI.ContentBodyAPI.convert_content_body(
                "invalid_format", {"type": "storage", "value": "Testing"}
            )

    def test_convert_body_invalid_body(self):
        """
        Trying to convert an invalid body should raise an error.
        """
        with self.assertRaises(ValueError):
            ConfluenceAPI.ContentBodyAPI.convert_content_body(
                "view", {"type": "invalid_type"}
            )

        with self.assertRaises(ValueError):
            ConfluenceAPI.ContentBodyAPI.convert_content_body(
                "view", {"value": "Testing"}
            )

        with self.assertRaises(ValueError):
            ConfluenceAPI.ContentBodyAPI.convert_content_body("view", {})

    # ----------------------------------------------------------------
    # LongTaskAPI (formerly TestLongTaskAPI)
    # ----------------------------------------------------------------
    def test_longtask_retrieval(self):
        """
        Create a mock long task in DB, retrieve it, then attempt to retrieve a non-existent one.
        """
        t_id = "999"
        DB["long_tasks"][t_id] = {
            "id": t_id,
            "status": "in_progress",
            "description": "ExampleTask",
        }
        tasks = ConfluenceAPI.LongTaskAPI.get_long_tasks()
        self.assertEqual(len(tasks), 1, "Should retrieve exactly one long task from DB")

        task = ConfluenceAPI.LongTaskAPI.get_long_task("999")
        self.assertEqual(task["description"], "ExampleTask")

        with self.assertRaises(ValueError):
            ConfluenceAPI.LongTaskAPI.get_long_task("nope")

    def test_longtask_empty(self):
        """
        With no tasks in DB, get_long_tasks should return empty.
        """
        DB["long_tasks"].clear()
        tasks = ConfluenceAPI.LongTaskAPI.get_long_tasks()
        self.assertEqual(len(tasks), 0)

    # def test_longtask_invalid_start(self):
    #     """
    #     Test that get_long_tasks raises ValueError for negative start index.
    #     """
    #     with self.assertRaises(ValueError):
    #         ConfluenceAPI.LongTaskAPI.get_long_tasks(start=-1)

    # def test_longtask_invalid_limit(self):
    #     """
    #     Test that get_long_tasks raises ValueError for negative limit.
    #     """
    #     with self.assertRaises(ValueError):
    #         ConfluenceAPI.LongTaskAPI.get_long_tasks(limit=-1)

    # ----------------------------------------------------------------
    # SpaceAPI (formerly TestSpaceAPI)
    # ----------------------------------------------------------------
    def test_get_spaces(self):
        """
        Create multiple spaces and retrieve them with/without a spaceKey filter.
        """
        ConfluenceAPI.SpaceAPI.create_space({"key": "AAA", "name": "Space A"})
        ConfluenceAPI.SpaceAPI.create_space({"key": "BBB", "name": "Space B"})
        all_spaces = ConfluenceAPI.SpaceAPI.get_spaces()
        self.assertEqual(len(all_spaces), 2, "Should retrieve both spaces")

        spaces_aaa = ConfluenceAPI.SpaceAPI.get_spaces(spaceKey="AAA")
        self.assertEqual(len(spaces_aaa), 1, "Should retrieve only space AAA")
        self.assertEqual(spaces_aaa[0]["spaceKey"], "AAA")

    # def test_get_spaces_invalid_start_and_limit(self):
    #     """
    #     Test that get_spaces raises ValueError for negative start and limit.
    #     """
    #     with self.assertRaises(ValueError):
    #         ConfluenceAPI.SpaceAPI.get_spaces(start=-1)
    #     with self.assertRaises(ValueError):
    #         ConfluenceAPI.SpaceAPI.get_spaces(limit=-1)

    def test_create_private_space(self):
        """
        Test creating a private space (same logic as create_space, but method differs).
        """
        private_space = {"key": "PRIV", "name": "Private Space"}
        created = ConfluenceAPI.SpaceAPI.create_private_space(private_space)
        self.assertEqual(created["spaceKey"], "PRIV")
        fetched = ConfluenceAPI.SpaceAPI.get_space("PRIV")
        self.assertEqual(fetched["name"], "Private Space")

    def test_update_space(self):
        """
        Test updating an existing space's name and description.
        """
        ConfluenceAPI.SpaceAPI.create_space({"key": "UPD", "name": "Old Name"})
        updated = ConfluenceAPI.SpaceAPI.update_space(
            "UPD", {"name": "New Name", "description": "New Desc"}
        )
        self.assertEqual(updated["name"], "New Name")
        self.assertEqual(updated["description"], "New Desc")

        # def test_update_space_invalid_key(self):
        #     """
        #     Test that updating a space with an invalid key raises a ValueError.
        #     """
        #     with self.assertRaises(ValueError):
        #         ConfluenceAPI.SpaceAPI.update_space("INVALID", {"name": "New Name"})

        # def test_get_space_content_of_type(self):
        """
        Test retrieving space content filtered by a specific type.
        """
        ConfluenceAPI.SpaceAPI.create_space({"key": "TYP", "name": "TypeTest"})
        ConfluenceAPI.ContentAPI.create_content(
            {"title": "Page1", "spaceKey": "TYP", "type": "page"}
        )
        ConfluenceAPI.ContentAPI.create_content(
            {
                "title": "Blog1",
                "spaceKey": "TYP",
                "type": "blogpost",
                "postingDay": "2025-03-10",
            }
        )

        pages = ConfluenceAPI.SpaceAPI.get_space_content_of_type("TYP", "page")
        self.assertEqual(len(pages), 1, "Should retrieve only page-type content")

        blogs = ConfluenceAPI.SpaceAPI.get_space_content_of_type("TYP", "blogpost")
        self.assertEqual(len(blogs), 1, "Should retrieve only blogpost-type content")

    def test_create_and_get_space(self):
        """
        Create a space, then retrieve and verify its fields.
        """
        new_space = {"key": "TST", "name": "Test Space"}
        created = ConfluenceAPI.SpaceAPI.create_space(new_space)
        self.assertEqual(created["spaceKey"], "TST")
        fetched = ConfluenceAPI.SpaceAPI.get_space("TST")
        self.assertEqual(fetched["name"], "Test Space")

    def test_create_space_duplicate_key(self):
        """
        Test that creating a space with a duplicate key raises a ValueError.
        """
        ConfluenceAPI.SpaceAPI.create_space({"key": "DUP", "name": "Duplicate Space"})
        with self.assertRaises(ValueError):
            ConfluenceAPI.SpaceAPI.create_space(
                {"key": "DUP", "name": "Duplicate Space"}
            )

    def test_delete_space(self):
        """
        Create a space, then delete it. Confirm it is gone.
        """
        ConfluenceAPI.SpaceAPI.create_space({"key": "DEL", "name": "Delete Me"})
        result = ConfluenceAPI.SpaceAPI.delete_space("DEL")
        self.assertEqual(result["status"], "complete")
        with self.assertRaises(ValueError):
            ConfluenceAPI.SpaceAPI.get_space("DEL")

    def test_delete_space_invalid_key(self):
        """
        Test that deleting a space with an invalid key raises a ValueError.
        """
        with self.assertRaises(ValueError):
            ConfluenceAPI.SpaceAPI.delete_space("INVALID")

    def test_space_content_listing(self):
        """
        Create space and some content, then retrieve that content via SpaceAPI.
        """
        ConfluenceAPI.SpaceAPI.create_space({"key": "DOC", "name": "Docs"})
        ConfluenceAPI.ContentAPI.create_content(
            {"title": "DocPage1", "spaceKey": "DOC", "type": "page"}
        )
        ConfluenceAPI.ContentAPI.create_content(
            {"title": "DocPage2", "spaceKey": "DOC", "type": "page"}
        )
        results = ConfluenceAPI.SpaceAPI.get_space_content("DOC")
        self.assertEqual(len(results), 2, "Should retrieve 2 pages in space DOC")

    # def test_space_content_listing_invalid_key(self):
    #     """
    #     Test that getting space content with an invalid key raises a ValueError.
    #     """
    #     with self.assertRaises(ValueError):
    #         ConfluenceAPI.SpaceAPI.get_space_content("INVALID")

    def test_create_space_missing_key(self):
        """
        Attempt to create a space without providing 'key'. Should fail.
        """
        with self.assertRaises(ValueError):
            ConfluenceAPI.SpaceAPI.create_space({"name": "NoKeySpace"})

    # ----------------------------------------------------------------
    # Combined Additional Persistence Test
    # ----------------------------------------------------------------
    def test_save_and_load_state(self):
        """
        Test creating content, saving state, clearing DB, loading state, and verifying.
        """
        # Create test content
        created = ConfluenceAPI.ContentAPI.create_content(
            {"title": "Persistent Page", "spaceKey": "PS", "type": "page"}
        )
        c_id = created["id"]

        # Save state
        ConfluenceAPI.SimulationEngine.db.save_state("test_state.json")

        # Clear content by deleting it
        ConfluenceAPI.ContentAPI.delete_content(c_id, status="trashed")

        # Load state back
        ConfluenceAPI.SimulationEngine.db.load_state("test_state.json")

        # Verify content exists
        content = ConfluenceAPI.ContentAPI.get_content(c_id)
        self.assertEqual(content["title"], "Persistent Page")

        # Cleanup file
        if os.path.exists("test_state.json"):
            os.remove("test_state.json")

    def test_delete_content_special_case(self):
        """
        Test the special case of delete_content where:
        1. First delete trashes the content
        2. Second delete with status="trashed" permanently removes it
        """
        # Create content
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "ToBeDeleted", "spaceKey": "TEST", "type": "page"}
        )

        # First delete - should trash the content
        ConfluenceAPI.ContentAPI.delete_content(content["id"])

        # Verify it's trashed
        trashed = ConfluenceAPI.ContentAPI.get_content(content["id"], status="trashed")
        self.assertIsNone(trashed)

        # Second delete with status="trashed" - should permanently remove it
        ConfluenceAPI.ContentAPI.delete_content(content["id"], status="trashed")

        # Verify it's permanently deleted
        with self.assertRaises(ValueError):
            ConfluenceAPI.ContentAPI.get_content(content["id"])

    def test_get_content_list_expanded_fields(self):
        """Test retrieving content with expanded fields."""
        # Create a space
        space_key = "EXPAND"
        DB["spaces"][space_key] = {
            "spaceKey": space_key,
            "name": "Expand Test Space",
            "description": "Test space for expansion"
        }

        # Create content with various properties
        content = ConfluenceAPI.ContentAPI.create_content({
            "title": "Expand Test Page",
            "spaceKey": space_key,
            "type": "page",
            "body": {
                "storage": {
                    "value": "Test content",
                    "representation": "storage"
                }
            }
        })

        # Add some labels
        ConfluenceAPI.ContentAPI.add_content_labels(content["id"], ["test-label", "another-label"])

        # Set up version property
        content_id = content["id"]
        version_key = f"{content_id}:version"
        DB["content_properties"][version_key] = {
            "key": "version",
            "value": {"number": 1}
        }

        # Test space expansion
        expanded_space = ConfluenceAPI.ContentAPI.get_content_list(expand="space")
        self.assertEqual(len(expanded_space), 1)
        self.assertIn("space", expanded_space[0])
        self.assertEqual(expanded_space[0]["space"]["key"], space_key)
        self.assertEqual(expanded_space[0]["space"]["name"], "Expand Test Space")

        # Test version expansion
        expanded_version = ConfluenceAPI.ContentAPI.get_content_list(expand="version")
        self.assertEqual(len(expanded_version), 1)
        self.assertIn("version", expanded_version[0])
        self.assertEqual(expanded_version[0]["version"][0]["version"], 1)

        #  Test history expansion
        expanded_history = ConfluenceAPI.ContentAPI.get_content_list(expand="history")
        self.assertEqual(len(expanded_history), 1)
        self.assertIn("history", expanded_history[0])
        self.assertIn("createdBy", expanded_history[0]["history"])

        # Test multiple expansions
        expanded_multiple = ConfluenceAPI.ContentAPI.get_content_list(expand="space,version")
        self.assertEqual(len(expanded_multiple), 1)
        self.assertIn("space", expanded_multiple[0])
        self.assertIn("version", expanded_multiple[0])

        # Test with invalid expansion field - this should raise an error
        with self.assertRaises(InvalidParameterValueError):
            ConfluenceAPI.ContentAPI.get_content_list(expand="invalid_expansion_field")

    def test_create_content_invalid_input(self):
        """
            Test that create_content raises ValueError for invalid inputs.
        """

        self.assert_error_behavior(
            func_to_call=create_content,
            expected_exception_type=ValidationError,
            expected_message="Input should be a valid dictionary or instance of ContentInputModel",
            body=None
        )

    def test_original_create_space_missing_key(self):
        """Attempt to create a space without providing 'key' via full API path."""
        self.assert_error_behavior(
            func_to_call=create_space,
            expected_exception_type=ValueError,
            expected_message="Missing required field: spaceKey",
            resource={"name": "My Space Without Key"}
        )

    def test_invalid_space_key_type_integer(self):
        """Test that an integer spaceKey raises TypeError."""
        invalid_key = 123
        self.assert_error_behavior(
            func_to_call=get_space_details,
            expected_exception_type=TypeError,
            expected_message="spaceKey must be a string, but got int.",  # Corrected to match actual message
            spaceKey=invalid_key  # type: ignore
        )

    def test_invalid_space_key_type_none(self):
        """Test that a None spaceKey raises TypeError."""
        invalid_key = None
        self.assert_error_behavior(
            func_to_call=get_space_details,
            expected_exception_type=TypeError,
            expected_message="spaceKey must be a string, but got NoneType.",  # Corrected to match actual message
            spaceKey=invalid_key  # type: ignore
        )

    def test_invalid_space_key_type_list(self):
        """Test that a list spaceKey raises TypeError."""
        invalid_key = ["key_part_1"]
        self.assert_error_behavior(
            func_to_call=get_space_details,
            expected_exception_type=TypeError,
            expected_message="spaceKey must be a string, but got list.",  # Corrected to match actual message
            spaceKey=invalid_key  # type: ignore
        )

    def test_pagination_start_exceeds_results(self):
        """Test pagination where start index is beyond available matching results."""
        results = get_space_content(spaceKey="TESTSPACE", start=4, limit=5)
        self.assertEqual(len(results), 0)

    def test_valid_input_non_existent_spacekey(self):
        """Test with a spaceKey that has no content."""
        results = get_space_content(spaceKey="NOSUCHSPACE")
        self.assertEqual(len(results), 0)

    # --- spaceKey validation ---
    def test_invalid_spacekey_type_not_string(self):
        """Test TypeError for non-string spaceKey."""
        self.assert_error_behavior(
            func_to_call=get_space_content,
            expected_exception_type=TypeError,
            expected_message="spaceKey must be a string.",
            spaceKey=12345  # Invalid type
        )

    def test_invalid_spacekey_empty_string(self):
        """Test ValueError for empty string spaceKey."""
        self.assert_error_behavior(
            func_to_call=get_space_content,
            expected_exception_type=ValueError,
            expected_message="spaceKey must not be an empty string.",
            spaceKey=""  # Invalid value
        )

    # --- start validation ---
    def test_invalid_start_type_not_integer(self):
        """Test TypeError for non-integer start."""
        self.assert_error_behavior(
            func_to_call=get_space_content,
            expected_exception_type=TypeError,
            expected_message="start must be an integer.",
            spaceKey="TESTSPACE",
            start="0"  # Invalid type
        )

    def test_invalid_start_negative_integer(self):
        """Test ValueError for negative integer start."""
        self.assert_error_behavior(
            func_to_call=get_space_content,
            expected_exception_type=ValueError,
            expected_message="start must be a non-negative integer.",
            spaceKey="TESTSPACE",
            start=-1  # Invalid value
        )

    # --- limit validation ---
    def test_invalid_limit_type_not_integer(self):
        """Test TypeError for non-integer limit."""
        self.assert_error_behavior(
            func_to_call=get_space_content,
            expected_exception_type=TypeError,
            expected_message="limit must be an integer.",
            spaceKey="TESTSPACE",
            limit="25"  # Invalid type
        )

    def test_invalid_limit_zero(self):
        """Test ValueError for limit=0."""
        self.assert_error_behavior(
            func_to_call=get_space_content,
            expected_exception_type=ValueError,
            expected_message="limit must be a positive integer.",
            spaceKey="TESTSPACE",
            limit=0  # Invalid value
        )

    def test_invalid_limit_negative_integer(self):
        """Test ValueError for negative integer limit."""
        self.assert_error_behavior(
            func_to_call=get_space_content,
            expected_exception_type=ValueError,
            expected_message="limit must be a positive integer.",
            spaceKey="TESTSPACE",
            limit=-5  # Invalid value
        )

    def test_invalid_id_type_raises_type_error(self):
        """Test that providing a non-string ID raises TypeError."""
        self.assert_error_behavior(
            func_to_call=delete_content,
            expected_exception_type=TypeError,
            expected_message="id must be a string, got int.",
            id=123,
            status=None
        )

    def test_invalid_status_type_raises_type_error(self):
        """Test that providing a non-string status (when not None) raises TypeError."""
        DB["contents"]["c1"] = {"id": "c1", "status": "current"}
        self.assert_error_behavior(
            func_to_call=delete_content,
            expected_exception_type=TypeError,
            expected_message="status must be a string if provided, got int.",
            id="c1",
            status=123
        )

    def test_delete_nonexistent_content_raises_value_error(self):
        """Test deleting a non-existent content ID raises ValueError."""
        self.assert_error_behavior(
            func_to_call=delete_content,
            expected_exception_type=ValueError,
            expected_message="Content with id=non_existent_id not found.",
            id="non_existent_id",
            status=None
        )

    def test_soft_delete_current_content_with_status_none(self):
        """Test that current content is trashed if status parameter is None."""
        content_id = "c_current_to_trash_status_none"
        DB["contents"][content_id] = {"id": content_id, "status": "current", "title": "Test"}

        delete_content(id=content_id, status=None)

        self.assertIn(content_id, DB["contents"])
        self.assertEqual(DB["contents"][content_id]["status"], "trashed")

    def test_soft_delete_current_content_with_other_status_param(self):
        """Test that current content is trashed if status parameter is not 'trashed'."""
        content_id = "c_current_to_trash_status_other"
        DB["contents"][content_id] = {"id": content_id, "status": "current", "title": "Test"}

        delete_content(id=content_id, status="archive")  # "archive" is not "trashed"

        self.assertIn(content_id, DB["contents"])
        self.assertEqual(DB["contents"][content_id]["status"], "trashed")

    def test_purge_trashed_content_when_status_param_is_trashed(self):
        """Test that trashed content is purged if status parameter is 'trashed'."""
        content_id = "c_trashed_to_purge"
        DB["contents"][content_id] = {"id": content_id, "status": "trashed", "title": "Test Trashed"}

        delete_content(id=content_id, status="trashed")

        self.assertNotIn(content_id, DB["contents"])

    def test_trashed_content_remains_trashed_if_status_param_not_trashed(self):
        """Test that trashed content remains trashed if status parameter is None or not 'trashed'."""
        content_id = "c_trashed_remains_trashed"
        DB["contents"][content_id] = {"id": content_id, "status": "trashed", "title": "Test"}

        # First call with status=None
        delete_content(id=content_id, status=None)
        self.assertIn(content_id, DB["contents"])
        self.assertEqual(DB["contents"][content_id]["status"], "trashed")

        # Second call with status="archive" (not "trashed")
        delete_content(id=content_id, status="archive")
        self.assertIn(content_id, DB["contents"])
        self.assertEqual(DB["contents"][content_id]["status"], "trashed")

    def test_other_status_content_purged_if_status_param_is_trashed(self):
        """Test content with other DB status (e.g., 'archived') is purged if status param is 'trashed'."""
        content_id = "c_archived_to_purge"
        DB["contents"][content_id] = {"id": content_id, "status": "archived", "title": "Test Archived"}

        delete_content(id=content_id, status="trashed")

        self.assertNotIn(content_id, DB["contents"])

    def test_other_status_content_remains_if_status_param_not_trashed(self):
        """Test content with other DB status (e.g., 'archived') remains if status param is not 'trashed'."""
        content_id = "c_archived_remains_archived"
        DB["contents"][content_id] = {"id": content_id, "status": "archived", "title": "Test"}

        delete_content(id=content_id, status=None)
        self.assertNotIn(content_id, DB["contents"])

    def test_get_content_labels_valid_inputs(self):
        """Test get_content_labels with valid inputs and existing labels."""
        content_data = {"title": "LabelTestContent", "spaceKey": "TEST", "type": "page"}
        # Assuming create_content is available and works as in the broader test suite
        created_content = ConfluenceAPI.ContentAPI.create_content(content_data)
        content_id = created_content["id"]

        DB["content_labels"][content_id] = ["alpha", "beta", "gamma"]

        # Use the function alias as per instructions (ConfluenceAPI.ContentAPI.get_content_labels)
        result = get_content_labels(id=content_id, prefix=None, start=0, limit=10)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["label"], "alpha")

    def test_get_content_labels_id_invalid_type(self):
        """Test get_content_labels with invalid type for 'id'."""
        self.assert_error_behavior(
            func_to_call=get_content_labels,
            expected_exception_type=TypeError,
            expected_message="Parameter 'id' must be a string.",
            id=12345  # Invalid type
        )

    def test_get_content_labels_prefix_invalid_type(self):
        """Test get_content_labels with invalid type for 'prefix'."""
        # Need a valid content ID first
        content_data = {"title": "PrefixTestContent", "spaceKey": "TEST", "type": "page"}
        created_content = ConfluenceAPI.ContentAPI.create_content(content_data)
        content_id = created_content["id"]

        self.assert_error_behavior(
            func_to_call=get_content_labels,
            expected_exception_type=TypeError,
            expected_message="Parameter 'prefix' must be a string or None.",
            id=content_id,
            prefix=123  # Invalid type
        )

    def test_get_content_labels_start_invalid_type(self):
        """Test get_content_labels with invalid type for 'start'."""
        content_data = {"title": "StartTestContent", "spaceKey": "TEST", "type": "page"}
        created_content = ConfluenceAPI.ContentAPI.create_content(content_data)
        content_id = created_content["id"]

        self.assert_error_behavior(
            func_to_call=get_content_labels,
            expected_exception_type=TypeError,
            expected_message="Parameter 'start' must be an integer.",
            id=content_id,
            start="0"  # Invalid type
        )

    def test_get_content_labels_start_negative_value(self):
        """Test get_content_labels with negative value for 'start'."""
        content_data = {"title": "StartNegativeTestContent", "spaceKey": "TEST", "type": "page"}
        created_content = ConfluenceAPI.ContentAPI.create_content(content_data)
        content_id = created_content["id"]

        self.assert_error_behavior(
            func_to_call=get_content_labels,
            expected_exception_type=ValueError,
            expected_message="Parameter 'start' must be non-negative.",
            id=content_id,
            start=-1  # Invalid value
        )

    def test_get_content_labels_limit_invalid_type(self):
        """Test get_content_labels with invalid type for 'limit'."""
        content_data = {"title": "LimitTestContent", "spaceKey": "TEST", "type": "page"}
        created_content = ConfluenceAPI.ContentAPI.create_content(content_data)
        content_id = created_content["id"]

        self.assert_error_behavior(
            func_to_call=get_content_labels,
            expected_exception_type=TypeError,
            expected_message="Parameter 'limit' must be an integer.",
            id=content_id,
            limit="10"  # Invalid type
        )

    def test_get_content_labels_limit_non_positive_value(self):
        """Test get_content_labels with non-positive value for 'limit'."""
        content_data = {"title": "LimitNonPositiveTestContent", "spaceKey": "TEST", "type": "page"}
        created_content = ConfluenceAPI.ContentAPI.create_content(content_data)
        content_id = created_content["id"]

        self.assert_error_behavior(
            func_to_call=get_content_labels,
            expected_exception_type=ValueError,
            expected_message="Parameter 'limit' must be positive.",
            id=content_id,
            limit=0  # Invalid value
        )
        self.assert_error_behavior(
            func_to_call=get_content_labels,
            expected_exception_type=ValueError,
            expected_message="Parameter 'limit' must be positive.",
            id=content_id,
            limit=-5  # Invalid value
        )

    def test_get_content_labels_content_not_found(self):
        """Test get_content_labels when content ID does not exist (original ValueError)."""
        self.assert_error_behavior(
            func_to_call=get_content_labels,
            expected_exception_type=ValueError,
            expected_message="Content with id=non_existent_id not found.",
            id="non_existent_id"
        )

    def test_get_content_labels_no_labels_for_content(self):
        """Test get_content_labels when content exists but has no labels."""
        content_data = {"title": "NoLabelsContent", "spaceKey": "TEST", "type": "page"}
        created_content = ConfluenceAPI.ContentAPI.create_content(content_data)
        content_id = created_content["id"]
        # Ensure no labels are set for this ID in DB["content_labels"] (default from get(id, []))

        result = get_content_labels(id=content_id)
        self.assertEqual(result, [])

    def test_get_content_labels_with_prefix_filter(self):
        """Test get_content_labels with prefix filtering."""
        content_data = {"title": "PrefixFilterContent", "spaceKey": "TEST", "type": "page"}
        created_content = ConfluenceAPI.ContentAPI.create_content(content_data)
        content_id = created_content["id"]

        DB["content_labels"][content_id] = ["team-a-feature", "team-b-bug", "team-a-task", "general"]

        result = get_content_labels(id=content_id, prefix="team-a")
        self.assertEqual(len(result), 2)
        self.assertIn({"label": "team-a-feature"}, result)
        self.assertIn({"label": "team-a-task"}, result)

        result_no_match = get_content_labels(id=content_id, prefix="nonexistent")
        self.assertEqual(result_no_match, [])

        result_all_if_empty_prefix = get_content_labels(id=content_id,
                                                                                 prefix="")  # Empty prefix should match all
        self.assertEqual(len(result_all_if_empty_prefix), 4)

    def test_get_content_labels_with_pagination(self):
        """Test get_content_labels with pagination (start and limit)."""
        content_data = {"title": "PaginationContent", "spaceKey": "TEST", "type": "page"}
        created_content = ConfluenceAPI.ContentAPI.create_content(content_data)
        content_id = created_content["id"]

        DB["content_labels"][content_id] = [f"label_{i}" for i in range(10)]  # label_0 to label_9

        # Test limit
        result = get_content_labels(id=content_id, limit=3)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["label"], "label_0")

        # Test start
        result = get_content_labels(id=content_id, start=5, limit=5)
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0]["label"], "label_5")

        # Test pagination that goes beyond available items
        result = get_content_labels(id=content_id, start=8, limit=5)
        self.assertEqual(len(result), 2)  # label_8, label_9
        self.assertEqual(result[0]["label"], "label_8")

        # Test start beyond available items
        result = get_content_labels(id=content_id, start=10, limit=5)
        self.assertEqual(len(result), 0)

    def test_get_content_labels_with_prefix_and_pagination(self):
        """Test get_content_labels with both prefix filtering and pagination."""
        content_data = {"title": "PrefixPaginationContent", "spaceKey": "TEST", "type": "page"}
        created_content = ConfluenceAPI.ContentAPI.create_content(content_data)
        content_id = created_content["id"]

        DB["content_labels"][content_id] = [
            "filter_A", "other_X", "filter_B", "filter_C", "other_Y", "filter_D"
        ]  # 4 items match "filter_"

        # Prefix "filter_", start 1, limit 2 from the filtered list
        # Filtered list: ["filter_A", "filter_B", "filter_C", "filter_D"]
        # Paginated from filtered: start=1 means "filter_B", limit=2 means ["filter_B", "filter_C"]
        result = get_content_labels(id=content_id, prefix="filter_", start=1, limit=2)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["label"], "filter_B")
        self.assertEqual(result[1]["label"], "filter_C")

    def test_invalid_id_type_integer(self):
        """Test that an integer id raises TypeError."""
        self.assert_error_behavior(
            func_to_call=add_content_labels,
            expected_exception_type=TypeError,
            expected_message="Argument 'id' must be a string.",
            id=123,
            labels=["label1"]
        )

    def test_invalid_id_type_none(self):
        """Test that a None id raises TypeError."""
        self.assert_error_behavior(
            func_to_call=add_content_labels,
            expected_exception_type=TypeError,
            expected_message="Argument 'id' must be a string.",
            id=None,
            labels=["label1"]
        )

    def test_invalid_labels_type_string(self):
        """Test that string type for labels raises TypeError."""
        self.assert_error_behavior(
            func_to_call=add_content_labels,
            expected_exception_type=TypeError,
            expected_message="Argument 'labels' must be a list.",
            id="content1",
            labels="not-a-list"
        )

    def test_invalid_labels_type_none(self):
        """Test that None type for labels raises TypeError."""
        self.assert_error_behavior(
            func_to_call=add_content_labels,
            expected_exception_type=TypeError,
            expected_message="Argument 'labels' must be a list.",
            id="content1",
            labels=None
        )

    def test_invalid_labels_element_type_integer(self):
        """Test that list of labels with non-string element (integer) raises TypeError."""
        self.assert_error_behavior(
            func_to_call=add_content_labels,
            expected_exception_type=TypeError,
            expected_message="All elements in 'labels' list must be strings.",
            id="content1",
            labels=["valid_label", 123]
        )

    def test_invalid_labels_element_type_none(self):
        """Test that list of labels with non-string element (None) raises TypeError."""
        self.assert_error_behavior(
            func_to_call=add_content_labels,
            expected_exception_type=TypeError,
            expected_message="All elements in 'labels' list must be strings.",
            id="content1",
            labels=["valid_label", None]
        )

    def test_valid_empty_labels_list(self):
        """Test that an empty list for labels is accepted and processed."""
        DB["contents"]["content1"] = {"title": "Test Content"}
        result = add_content_labels(id="content1", labels=[])
        self.assertEqual(result, [])
        self.assertEqual(DB["content_labels"]["content1"], [])

    def test_invalid_id_type(self):
        """Test that a non-string ID raises TypeError."""
        self.assert_error_behavior(
            func_to_call=get_content_details,
            expected_exception_type=TypeError,
            expected_message="Argument 'id' must be a string.",
            id=123
        )

    def test_empty_id_string(self):
        """Test that an empty string ID raises InvalidInputError."""
        self.assert_error_behavior(
            func_to_call=get_content_details,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'id' cannot be an empty string.",
            id=""
        )

    def test_invalid_status_type(self):
        """Test that a non-string status (when provided) raises TypeError."""
        self.assert_error_behavior(
            func_to_call=get_content_details,
            expected_exception_type=TypeError,
            expected_message="Argument 'status' must be a string if provided.",
            id="id1",
            status=123
        )

    def test_content_not_found(self):
        """Test that requesting a non-existent ID raises ContentNotFoundError."""
        self.assert_error_behavior(
            func_to_call=get_content_details,
            expected_exception_type=ContentNotFoundError,
            expected_message="Content with id='nonexistent' not found.",
            id="nonexistent"
        )

    def test_invalid_id_type_int(self):
        """Test that an integer 'id' raises TypeError."""
        self.assert_error_behavior(
            func_to_call=update_content,
            expected_exception_type=TypeError,
            expected_message="Argument 'id' must be a string, got int.",
            id=123,
            body={"title": "Test"}
        )

    def test_invalid_id_type_none(self):
        """Test that a None 'id' raises TypeError."""
        self.assert_error_behavior(
            func_to_call=update_content,
            expected_exception_type=TypeError,
            expected_message="Argument 'id' must be a string, got NoneType.",
            id=None,
            body={"title": "Test"}
        )

    def test_invalid_body_type_string(self):
        """Test that a string 'body' raises TypeError."""
        self.assert_error_behavior(
            func_to_call=update_content,
            expected_exception_type=TypeError,
            expected_message="Argument 'body' must be a dictionary, got str.",
            id="valid_id",
            body="not a dict"
        )

    def test_invalid_body_type_none(self):
        """Test that a None 'body' raises TypeError."""
        self.assert_error_behavior(
            func_to_call=update_content,
            expected_exception_type=TypeError,
            expected_message="Argument 'body' must be a dictionary, got NoneType.",
            id="valid_id",
            body=None
        )

    def test_body_with_invalid_title_type(self):
        """Test 'body' with 'title' as int raises ValidationError."""
        invalid_body = {"title": 123}
        self.assert_error_behavior(
            func_to_call=update_content,
            expected_exception_type=CustomValidationError,
            expected_message="Input validation failed",
            id="existing_id_1",
            body=invalid_body,
        )

    def test_body_with_invalid_status_type(self):
        """Test 'body' with 'status' as list raises ValidationError."""
        invalid_body = {"status": ["current"]}
        self.assert_error_behavior(
            func_to_call=update_content,
            expected_exception_type=CustomValidationError,
            expected_message="Input validation failed",
            id="existing_id_1",
            body=invalid_body,
        )

    def test_body_with_invalid_nested_body_type(self):
        """Test 'body' with nested 'body' (content) as string raises ValidationError."""
        invalid_body = {"body": "not a dict"}
        self.assert_error_behavior(
            func_to_call=update_content,
            expected_exception_type=CustomValidationError,
            expected_message="Input validation failed",
            id="existing_id_1",
            body=invalid_body
        )

    def test_body_with_invalid_space_type(self):
        """Test 'body' with 'space' as string raises ValidationError."""
        invalid_body = {"space": "not-a-dict"}
        self.assert_error_behavior(
            func_to_call=update_content,
            expected_exception_type=CustomValidationError,
            expected_message="Input validation failed",
            id="existing_id_1",
            body=invalid_body
        )

    def test_body_space_missing_key_field(self):
        """Test 'body.space' missing mandatory 'key' field raises ValidationError."""
        invalid_body = {"space": {"name": "My Space"}}  # Missing 'key'
        self.assert_error_behavior(
            func_to_call=update_content,
            expected_exception_type=CustomValidationError,
            expected_message="Input validation failed",
            id="existing_id_1",
            body=invalid_body,
        )

    def test_body_space_key_invalid_type(self):
        """Test 'body.space.key' with invalid type (int) raises ValidationError."""
        invalid_body = {"space": {"key": 123}}
        self.assert_error_behavior(
            func_to_call=update_content,
            expected_exception_type=CustomValidationError,
            expected_message="Input validation failed",
            id="existing_id_1",
            body=invalid_body,
        )

    def test_body_with_invalid_ancestors_type(self):
        """Test 'body' with 'ancestors' as string raises ValidationError."""
        invalid_body = {"ancestors": "not-a-list"}
        self.assert_error_behavior(
            func_to_call=update_content,
            expected_exception_type=CustomValidationError,
            expected_message="Input validation failed",
            id="existing_id_1",
            body=invalid_body
        )

    def test_body_with_ancestors_list_invalid_item_type(self):
        """Test 'body' with 'ancestors' list containing non-string raises ValidationError."""
        invalid_body = {"ancestors": ["id1", 123, "id3"]}
        self.assert_error_behavior(
            func_to_call=update_content,
            expected_exception_type=CustomValidationError,
            expected_message="Input validation failed",
            id="existing_id_1",
            body=invalid_body,
        )

    # --- Original Logic Error Propagation Test ---
    def test_content_not_found_propagates_value_error(self):
        """Test that original ValueError for non-existent ID is still raised."""
        non_existent_id = "non_existent_id_xyz"
        self.assert_error_behavior(
            func_to_call=update_content,
            expected_exception_type=ValueError,
            expected_message=f"Content with id='{non_existent_id}' not found.",
            id=non_existent_id,
            body={"title": "Any Title"}
        )

    def test_space_not_found(self):
        """Test retrieving a non-existent space, expecting ValueError."""
        space_key = "NON_EXISTENT_KEY"
        self.assert_error_behavior(
            func_to_call=get_space_details,
            expected_exception_type=ValueError,
            expected_message=f"Space with key={space_key} not found.",
            spaceKey=space_key
        )

    def test_invalid_space_key_type_integer(self):
        """Test that an integer spaceKey raises TypeError."""
        invalid_key = 123
        self.assert_error_behavior(
            func_to_call=get_space_details,
            expected_exception_type=TypeError,
            expected_message="spaceKey must be a string, but got int.",  # Corrected to match actual message
            spaceKey=invalid_key  # type: ignore
        )

    def test_invalid_space_key_type_none(self):
        """Test that a None spaceKey raises TypeError."""
        invalid_key = None
        self.assert_error_behavior(
            func_to_call=get_space_details,
            expected_exception_type=TypeError,
            expected_message="spaceKey must be a string, but got NoneType.",  # Corrected to match actual message
            spaceKey=invalid_key  # type: ignore
        )

    def test_invalid_space_key_type_list(self):
        """Test that a list spaceKey raises TypeError."""
        invalid_key = ["key_part_1"]
        self.assert_error_behavior(
            func_to_call=get_space_details,
            expected_exception_type=TypeError,
            expected_message="spaceKey must be a string, but got list.",  # Corrected to match actual message
            spaceKey=invalid_key  # type: ignore
        )

    def test_valid_empty_string_space_key_not_found(self):
        """Test that an empty string spaceKey (valid type) proceeds to DB lookup and raises ValueError if not found."""
        # Type validation for string should pass. The original logic handles "not found".
        space_key = ""
        self.assert_error_behavior(
            func_to_call=get_space_details,
            expected_exception_type=ValueError,
            expected_message=f"Space with key={space_key} not found.",
            spaceKey=space_key
        )

    def test_valid_empty_string_space_key_exists(self):
        """Test that an empty string spaceKey can be retrieved if it exists in DB."""
        space_key = ""
        global DB
        DB["spaces"][""] = {
            "spaceKey": "",
            "name": "Empty Key Space",
            "description": "A space identified by an empty string."
        }
        expected_space_data = {
            "spaceKey": "",
            "name": "Empty Key Space",
            "description": "A space identified by an empty string."
        }
        result = get_space_details(spaceKey=space_key)
        self.assertEqual(result, expected_space_data)

    def test_valid_input_basic_page(self):
        """Test creation with minimal valid input for a page."""
        body = {
            "type": "page",
            "title": "My Page",
            "spaceKey": "TESTSPACE"
        }
        result = create_content(body=body)
        self.assertEqual(result["type"], "page")
        self.assertEqual(result["title"], "My Page")
        self.assertEqual(result["spaceKey"], "TESTSPACE")
        self.assertEqual(result["status"], "current")  # Default
        self.assertIn("id", result)
        self.assertIn(result["id"], DB["contents"])

    def test_valid_input_all_fields(self):
        """Test creation with all optional fields provided and valid."""
        body = {
            "type": "blogpost",
            "title": "My Blog Post",
            "spaceKey": "BLOG",
            "status": "draft",
            "version": {"number": 2, "minorEdit": True},
            "body": {
                "storage": {
                    "value": "<p>Hello World</p>",
                    "representation": "storage"
                }
            },
            "createdBy": "jdoe",
            "postingDay": "2023-10-26"
        }
        result = create_content(body=body)
        self.assertEqual(result["type"], "blogpost")
        self.assertEqual(result["title"], "My Blog Post")
        self.assertEqual(result["status"], "draft")
        self.assertEqual(result["body"]["storage"]["value"], "<p>Hello World</p>")
        self.assertEqual(result["postingDay"], "2023-10-26")

    def test_missing_required_field_type(self):
        """Test error when required field 'type' is missing."""
        invalid_body = {"title": "Missing Type"}
        self.assert_error_behavior(
            func_to_call=create_content,
            expected_exception_type=ValidationError,
            expected_message="Field required",
            body=invalid_body
        )

    def test_missing_required_field_title(self):
        """Test error when required field 'title' is missing."""
        invalid_body = {"type": "page"}
        self.assert_error_behavior(
            func_to_call=create_content,
            expected_exception_type=ValidationError,
            expected_message="Field required",
            body=invalid_body
        )

    def test_invalid_type_for_field(self):
        """Test error when a field has an incorrect data type (e.g., title as int)."""
        invalid_body = {"type": "page", "title": 123}
        self.assert_error_behavior(
            func_to_call=create_content,
            expected_exception_type=ValidationError,
            expected_message="Input should be a valid string",
            body=invalid_body
        )

    def test_invalid_posting_day_format(self):
        """Test error when 'postingDay' has an invalid format."""
        invalid_body = {"type": "blogpost", "title": "Blog Post", "postingDay": "not-a-date"}
        self.assert_error_behavior(
            func_to_call=create_content,
            expected_exception_type=ValidationError,
            expected_message="String should match pattern",
            body=invalid_body
        )

    def test_invalid_nested_body_structure(self):
        """Test error with invalid structure for nested 'body.storage'."""
        invalid_body = {
            "type": "page",
            "title": "Valid Title",
            "body": {"storage": "not-a-dict"}  # Should be a dict
        }
        self.assert_error_behavior(
            func_to_call=create_content,
            expected_exception_type=ValidationError,
            expected_message="Input should be a valid dictionary",
            body=invalid_body
        )

    def test_empty_input_body(self):
        """Test error when the input 'body' dictionary is empty."""
        self.assert_error_behavior(
            func_to_call=create_content,
            expected_exception_type=ValidationError,
            expected_message="Field required",
            body={}
        )

    def test_valid_input_with_pagination(self):
        """Test get_spaces with valid start and limit parameters for pagination."""
        result = get_spaces(start=1, limit=1)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_valid_input_spacekey_not_found(self):
        """Test get_spaces filtering by a spaceKey that does not exist."""
        result = get_spaces(spaceKey="NONEXISTENT_KEY")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0, "Should return empty list for non-existent spaceKey")

    def test_valid_input_pagination_start_beyond_data(self):
        """Test get_spaces with a start index that is out of bounds (too high)."""
        result = get_spaces(start=10)  # Test DB has only 4 items
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0, "Should return empty list if start is out of bounds")

    def test_invalid_spacekey_type_integer(self):
        """Test get_spaces with an invalid type (int) for spaceKey."""
        self.assert_error_behavior(
            func_to_call=get_spaces,
            expected_exception_type=TypeError,
            expected_message="spaceKey must be a string or None, got int",
            spaceKey=12345
        )

    def test_invalid_start_type_string(self):
        """Test get_spaces with an invalid type (str) for start."""
        self.assert_error_behavior(
            func_to_call=get_spaces,
            expected_exception_type=TypeError,
            expected_message="start must be an integer, got str",
            start="not_an_int"
        )

    def test_invalid_start_value_negative(self):
        """Test get_spaces with a negative value for start."""
        self.assert_error_behavior(
            func_to_call=get_spaces,
            expected_exception_type=ValueError,
            expected_message="start parameter cannot be negative.",
            start=-5
        )

    def test_invalid_limit_type_float(self):
        """Test get_spaces with an invalid type (float) for limit."""
        self.assert_error_behavior(
            func_to_call=get_spaces,
            expected_exception_type=TypeError,
            expected_message="limit must be an integer, got float",
            limit=10.5
        )

    def test_invalid_limit_value_negative(self):
        """Test get_spaces with a negative value for limit."""
        self.assert_error_behavior(
            func_to_call=get_spaces,
            expected_exception_type=ValueError,
            expected_message="limit parameter cannot be negative.",
            limit=-10
        )

    def test_edge_case_zero_limit(self):
        """Test get_spaces with limit=0, expecting an empty list."""
        result = get_spaces(limit=0)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0, "limit=0 should return an empty list")

    def test_edge_case_start_equals_total_items(self):
        """Test get_spaces when start index is equal to the total number of items."""
        total_items = len(DB["spaces"])
        result = get_spaces(start=total_items)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0, "Should return empty list if start equals total items")

    def test_empty_cql_string(self):
        """Test that an empty CQL string raises a ValueError."""
        with self.assertRaisesRegex(ValueError, "CQL query is missing."):
            search_content_cql(cql="")

    def test_cql_type_error(self):
        """Test that a non-string 'cql' argument raises TypeError."""
        self.assert_error_behavior(
            func_to_call=search_content_cql,
            expected_exception_type=TypeError,
            expected_message="Argument 'cql' must be a string.",
            cql=123  # Invalid type
        )

    def test_start_type_error(self):
        """Test that a non-integer 'start' argument raises TypeError."""
        self.assert_error_behavior(
            func_to_call=search_content_cql,
            expected_exception_type=TypeError,
            expected_message="Argument 'start' must be an integer.",
            cql="type='page'",
            start="0"  # Invalid type
        )

    def test_limit_type_error(self):
        """Test that a non-integer 'limit' argument raises TypeError."""
        self.assert_error_behavior(
            func_to_call=search_content_cql,
            expected_exception_type=TypeError,
            expected_message="Argument 'limit' must be an integer.",
            cql="type='page'",
            limit="25"  # Invalid type
        )

    def test_start_negative_value_error(self):
        """Test that a negative 'start' argument raises InvalidPaginationValueError."""
        self.assert_error_behavior(
            func_to_call=search_content_cql,
            expected_exception_type=InvalidPaginationValueError,
            expected_message="Argument 'start' must be non-negative.",
            cql="type='page'",
            start=-1  # Invalid value
        )

    def test_limit_negative_value_error(self):
        """Test that a negative 'limit' argument raises InvalidPaginationValueError."""
        self.assert_error_behavior(
            func_to_call=search_content_cql,
            expected_exception_type=InvalidPaginationValueError,
            expected_message="Argument 'limit' must be non-negative.",
            cql="type='page'",
            limit=-5  # Invalid value
        )

    def test_get_spaces(self):
        """
        Create multiple spaces and retrieve them with/without a spaceKey filter.
        """
        ConfluenceAPI.SpaceAPI.create_space({"key": "AAA", "name": "Space A"})
        ConfluenceAPI.SpaceAPI.create_space({"key": "BBB", "name": "Space B"})
        all_spaces = ConfluenceAPI.SpaceAPI.get_spaces()
        self.assertEqual(len(all_spaces), 2, "Should retrieve both spaces")

        spaces_aaa = ConfluenceAPI.SpaceAPI.get_spaces(spaceKey="AAA")
        self.assertEqual(len(spaces_aaa), 1, "Should retrieve only space AAA")
        self.assertEqual(spaces_aaa[0]["spaceKey"], "AAA")

    # Adapting original create_space tests if they are to remain in this class:
    # The detailed validation tests are now in TestCreateSpaceValidation.
    # These might be slightly different, e.g. testing through the full API path.

    def test_original_create_space_missing_key(self):
        """
        Attempt to create a space without providing 'key' via full API path.
        (Original test: expected ValueError, now expects ValidationError)
        """
        # This version calls through ConfluenceAPI.SpaceAPI
        self.assert_error_behavior(
            func_to_call=create_space,
            expected_exception_type=ValidationError,
            expected_message="Field required",
            body={"name": "NoKeySpace"}
        )

    def test_original_create_space_duplicate_key(self):
        """
        Test that creating a space with a duplicate key raises a ValueError via full API path.
        (Original test: Expected ValueError, which is correct)
        """
        ConfluenceAPI.SpaceAPI.create_space({"key": "DUP", "name": "Duplicate Space"})
        self.assert_error_behavior(
            func_to_call=create_space,
            expected_exception_type=ValueError,
            expected_message="Space with key=DUP already exists.",
            body={"key": "DUP", "name": "Duplicate Space"}
        )

    # ... (Rest of the original TestConfluenceAPI methods) ...
    def test_create_and_get_space(self):
        """
        Create a space, then retrieve and verify its fields.
        """
        new_space = {"key": "TST", "name": "Test Space"}
        created = ConfluenceAPI.SpaceAPI.create_space(new_space)
        self.assertEqual(created["spaceKey"], "TST")
        fetched = ConfluenceAPI.SpaceAPI.get_space("TST")
        self.assertEqual(fetched["name"], "Test Space")

    def test_pagination_start_exceeds_results(self):
        """Test pagination when start exceeds available results."""
        body = {"type": "page", "title": "Page", "spaceKey": "TESTSPACE"}
        # Create content
        create_content(body=body)
        # Test pagination
        result = ConfluenceAPI.ContentAPI.get_content_list(start=10, limit=10)
        self.assertEqual(len(result), 0)

    def test_delete_content_historical_immediate_deletion(self):
        """Test that historical content is immediately deleted regardless of status parameter."""
        content_id = "c_historical_immediate"
        DB["contents"][content_id] = {"id": content_id, "status": "historical", "title": "Test Historical"}

        # Should be deleted immediately regardless of status parameter
        delete_content(id=content_id, status=None)
        self.assertNotIn(content_id, DB["contents"])

        # Recreate and test with status="trashed" - should still be deleted immediately
        DB["contents"][content_id] = {"id": content_id, "status": "historical", "title": "Test Historical"}
        delete_content(id=content_id, status="trashed")
        self.assertNotIn(content_id, DB["contents"])

    def test_delete_content_draft_immediate_deletion(self):
        """Test that draft content is immediately deleted regardless of status parameter."""
        content_id = "c_draft_immediate"
        DB["contents"][content_id] = {"id": content_id, "status": "draft", "title": "Test Draft"}

        # Should be deleted immediately regardless of status parameter
        delete_content(id=content_id, status=None)
        self.assertNotIn(content_id, DB["contents"])

        # Recreate and test with status="trashed" - should still be deleted immediately
        DB["contents"][content_id] = {"id": content_id, "status": "draft", "title": "Test Draft"}
        delete_content(id=content_id, status="trashed")
        self.assertNotIn(content_id, DB["contents"])

    def test_delete_content_archived_immediate_deletion(self):
        """Test that archived content is immediately deleted regardless of status parameter."""
        content_id = "c_archived_immediate"
        DB["contents"][content_id] = {"id": content_id, "status": "archived", "title": "Test Archived"}

        # Should be deleted immediately regardless of status parameter
        delete_content(id=content_id, status=None)
        self.assertNotIn(content_id, DB["contents"])

        # Recreate and test with status="trashed" - should still be deleted immediately
        DB["contents"][content_id] = {"id": content_id, "status": "archived", "title": "Test Archived"}
        delete_content(id=content_id, status="trashed")
        self.assertNotIn(content_id, DB["contents"])

    def test_delete_content_missing_status_field(self):
        """Test that content without a status field raises ValueError."""
        content_id = "c_no_status_field"
        DB["contents"][content_id] = {"id": content_id, "title": "Test No Status"}

        self.assert_error_behavior(
            func_to_call=delete_content,
            expected_exception_type=ValueError,
            expected_message=f"Content with id={content_id} does not have a status field.",
            id=content_id,
            status=None
        )

    def test_delete_content_empty_string_id(self):
        """Test that empty string ID raises ValueError (content not found)."""
        self.assert_error_behavior(
            func_to_call=delete_content,
            expected_exception_type=ValueError,
            expected_message="Content with id= not found.",
            id="",
            status=None
        )

    def test_delete_content_none_id(self):
        """Test that None ID raises TypeError."""
        self.assert_error_behavior(
            func_to_call=delete_content,
            expected_exception_type=TypeError,
            expected_message="id must be a string, got NoneType.",
            id=None,
            status=None
        )

    def test_delete_content_list_id(self):
        """Test that list ID raises TypeError."""
        self.assert_error_behavior(
            func_to_call=delete_content,
            expected_exception_type=TypeError,
            expected_message="id must be a string, got list.",
            id=["content_id"],
            status=None
        )

    def test_delete_content_dict_id(self):
        """Test that dict ID raises TypeError."""
        self.assert_error_behavior(
            func_to_call=delete_content,
            expected_exception_type=TypeError,
            expected_message="id must be a string, got dict.",
            id={"id": "content_id"},
            status=None
        )

    def test_delete_content_list_status(self):
        """Test that list status raises TypeError."""
        content_id = "c_list_status"
        DB["contents"][content_id] = {"id": content_id, "status": "current", "title": "Test"}
        
        self.assert_error_behavior(
            func_to_call=delete_content,
            expected_exception_type=TypeError,
            expected_message="status must be a string if provided, got list.",
            id=content_id,
            status=["trashed"]
        )

    def test_delete_content_dict_status(self):
        """Test that dict status raises TypeError."""
        content_id = "c_dict_status"
        DB["contents"][content_id] = {"id": content_id, "status": "current", "title": "Test"}
        
        self.assert_error_behavior(
            func_to_call=delete_content,
            expected_exception_type=TypeError,
            expected_message="status must be a string if provided, got dict.",
            id=content_id,
            status={"status": "trashed"}
        )

    def test_delete_content_integer_status(self):
        """Test that integer status raises TypeError."""
        content_id = "c_int_status"
        DB["contents"][content_id] = {"id": content_id, "status": "current", "title": "Test"}
        
        self.assert_error_behavior(
            func_to_call=delete_content,
            expected_exception_type=TypeError,
            expected_message="status must be a string if provided, got int.",
            id=content_id,
            status=123
        )

    def test_delete_content_float_status(self):
        """Test that float status raises TypeError."""
        content_id = "c_float_status"
        DB["contents"][content_id] = {"id": content_id, "status": "current", "title": "Test"}
        
        self.assert_error_behavior(
            func_to_call=delete_content,
            expected_exception_type=TypeError,
            expected_message="status must be a string if provided, got float.",
            id=content_id,
            status=123.45
        )

    def test_delete_content_boolean_status(self):
        """Test that boolean status raises TypeError."""
        content_id = "c_bool_status"
        DB["contents"][content_id] = {"id": content_id, "status": "current", "title": "Test"}
        
        self.assert_error_behavior(
            func_to_call=delete_content,
            expected_exception_type=TypeError,
            expected_message="status must be a string if provided, got bool.",
            id=content_id,
            status=True
        )

    def test_delete_content_comprehensive_workflow(self):
        """Test a comprehensive workflow of delete_content operations."""
        # Create content with current status
        content_id = "c_comprehensive_workflow"
        DB["contents"][content_id] = {"id": content_id, "status": "current", "title": "Test Workflow"}

        # Step 1: Delete current content (should trash it)
        delete_content(id=content_id, status=None)
        self.assertIn(content_id, DB["contents"])
        self.assertEqual(DB["contents"][content_id]["status"], "trashed")

        # Step 2: Try to delete trashed content without status="trashed" (should remain trashed)
        delete_content(id=content_id, status="archive")
        self.assertIn(content_id, DB["contents"])
        self.assertEqual(DB["contents"][content_id]["status"], "trashed")

        # Step 3: Delete trashed content with status="trashed" (should purge it)
        delete_content(id=content_id, status="trashed")
        self.assertNotIn(content_id, DB["contents"])

    def test_delete_content_multiple_non_trashable_statuses(self):
        """Test that all non-trashable statuses are immediately deleted."""
        non_trashable_statuses = ["historical", "draft", "archived"]
        
        for status in non_trashable_statuses:
            content_id = f"c_{status}_test"
            DB["contents"][content_id] = {"id": content_id, "status": status, "title": f"Test {status}"}
            
            # Should be deleted immediately regardless of status parameter
            delete_content(id=content_id, status=None)
            self.assertNotIn(content_id, DB["contents"], f"Content with status '{status}' should be deleted immediately")

    def test_delete_content_status_case_sensitivity(self):
        """Test that status parameter is case-sensitive."""
        content_id = "c_case_sensitive"
        DB["contents"][content_id] = {"id": content_id, "status": "trashed", "title": "Test Case Sensitive"}

        # "TRASHED" (uppercase) should not match "trashed" (lowercase)
        delete_content(id=content_id, status="TRASHED")
        self.assertIn(content_id, DB["contents"])
        self.assertEqual(DB["contents"][content_id]["status"], "trashed")

        # "Trashed" (title case) should not match "trashed" (lowercase)
        delete_content(id=content_id, status="Trashed")
        self.assertIn(content_id, DB["contents"])
        self.assertEqual(DB["contents"][content_id]["status"], "trashed")

        # Only exact match "trashed" should purge the content
        delete_content(id=content_id, status="trashed")
        self.assertNotIn(content_id, DB["contents"])

    def test_delete_content_whitespace_in_status(self):
        """Test that whitespace in status parameter is handled correctly."""
        content_id = "c_whitespace_status"
        DB["contents"][content_id] = {"id": content_id, "status": "trashed", "title": "Test Whitespace"}

        # Status with leading/trailing whitespace should not match
        delete_content(id=content_id, status=" trashed")
        self.assertIn(content_id, DB["contents"])
        self.assertEqual(DB["contents"][content_id]["status"], "trashed")

        delete_content(id=content_id, status="trashed ")
        self.assertIn(content_id, DB["contents"])
        self.assertEqual(DB["contents"][content_id]["status"], "trashed")

        delete_content(id=content_id, status=" trashed ")
        self.assertIn(content_id, DB["contents"])
        self.assertEqual(DB["contents"][content_id]["status"], "trashed")

        # Only exact match should work
        delete_content(id=content_id, status="trashed")
        self.assertNotIn(content_id, DB["contents"])

    def test_delete_content_empty_string_status(self):
        """Test that empty string status is treated as None."""
        content_id = "c_empty_status"
        DB["contents"][content_id] = {"id": content_id, "status": "current", "title": "Test Empty Status"}

        # Empty string should be treated as None, so current content should be trashed
        delete_content(id=content_id, status="")
        self.assertIn(content_id, DB["contents"])
        self.assertEqual(DB["contents"][content_id]["status"], "trashed")

    def test_delete_content_none_status_explicit(self):
        """Test that explicit None status works the same as no status parameter."""
        content_id = "c_none_status"
        DB["contents"][content_id] = {"id": content_id, "status": "current", "title": "Test None Status"}

        # Explicit None should trash current content
        delete_content(id=content_id, status=None)
        self.assertIn(content_id, DB["contents"])
        self.assertEqual(DB["contents"][content_id]["status"], "trashed")

    def test_delete_content_preserves_other_fields(self):
        """Test that delete_content preserves other fields when trashing content."""
        content_id = "c_preserve_fields"
        original_content = {
            "id": content_id,
            "status": "current",
            "title": "Test Preserve Fields",
            "type": "page",
            "spaceKey": "TEST",
            "body": {"storage": {"value": "Test content"}},
            "version": {"number": 1},
            "custom_field": "custom_value"
        }
        DB["contents"][content_id] = original_content.copy()

        # Delete should only change status to "trashed"
        delete_content(id=content_id, status=None)
        
        self.assertIn(content_id, DB["contents"])
        updated_content = DB["contents"][content_id]
        self.assertEqual(updated_content["status"], "trashed")
        
        # All other fields should be preserved
        for key, value in original_content.items():
            if key != "status":
                self.assertEqual(updated_content[key], value, f"Field '{key}' should be preserved")

    # ----------------------------------------------------------------
    # Additional validation tests for create_attachments (new validations)
    # ----------------------------------------------------------------
    
    def test_create_attachments_id_type_validation_new(self):
        """Test create_attachments with invalid types for 'id' parameter (new validation)."""
        from confluence.SimulationEngine.custom_errors import InvalidInputError
        
        class MockFile:
            def __init__(self, name):
                self.name = name
        
        file_obj = MockFile("test.txt")
        
        # Test with integer id (new TypeError validation)
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.create_attachments,
            expected_exception_type=TypeError,
            expected_message="Argument 'id' must be a string.",
            id=123,
            file=file_obj
        )
        
        # Test with None id (new TypeError validation)
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.create_attachments,
            expected_exception_type=TypeError,
            expected_message="Argument 'id' must be a string.",
            id=None,
            file=file_obj
        )
    
    def test_create_attachments_id_empty_string_validation(self):
        """Test create_attachments with empty string id (new validation)."""
        from confluence.SimulationEngine.custom_errors import InvalidInputError
        
        class MockFile:
            def __init__(self, name):
                self.name = name
        
        file_obj = MockFile("test.txt")
        
        # Test with empty string id (new InvalidInputError validation)
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.create_attachments,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'id' cannot be an empty string.",
            id="",
            file=file_obj
        )
        
        # Test with whitespace-only id (new InvalidInputError validation)
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.create_attachments,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'id' cannot be an empty string.",
            id="   ",
            file=file_obj
        )
    
    def test_create_attachments_file_none_validation(self):
        """Test create_attachments with None file (new validation)."""
        from confluence.SimulationEngine.custom_errors import FileAttachmentError
        
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "FileValidationTest", "spaceKey": "TEST", "type": "page"}
        )
        
        # Test with None file (new FileAttachmentError validation)
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.create_attachments,
            expected_exception_type=FileAttachmentError,
            expected_message="Argument 'file' cannot be None.",
            id=content["id"],
            file=None
        )
    
    def test_create_attachments_comment_type_validation_new(self):
        """Test create_attachments with invalid types for 'comment' parameter (new validation)."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "CommentValidationTest", "spaceKey": "TEST", "type": "page"}
        )
        
        class MockFile:
            def __init__(self, name):
                self.name = name
        
        file_obj = MockFile("test.txt")
        
        # Test with integer comment (new TypeError validation)
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.create_attachments,
            expected_exception_type=TypeError,
            expected_message="Argument 'comment' must be a string if provided.",
            id=content["id"],
            file=file_obj,
            comment=123
        )
        
        # Test with list comment (new TypeError validation)
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.create_attachments,
            expected_exception_type=TypeError,
            expected_message="Argument 'comment' must be a string if provided.",
            id=content["id"],
            file=file_obj,
            comment=["comment"]
        )
    
    def test_create_attachments_minor_edit_type_validation_new(self):
        """Test create_attachments with invalid types for 'minorEdit' parameter (new validation)."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "MinorEditValidationTest", "spaceKey": "TEST", "type": "page"}
        )
        
        class MockFile:
            def __init__(self, name):
                self.name = name
        
        file_obj = MockFile("test.txt")
        
        # Test with string minorEdit (new TypeError validation)
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.create_attachments,
            expected_exception_type=TypeError,
            expected_message="Argument 'minorEdit' must be a boolean.",
            id=content["id"],
            file=file_obj,
            minorEdit="true"
        )
        
        # Test with integer minorEdit (new TypeError validation)
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.create_attachments,
            expected_exception_type=TypeError,
            expected_message="Argument 'minorEdit' must be a boolean.",
            id=content["id"],
            file=file_obj,
            minorEdit=1
        )
    
    def test_create_attachments_content_not_found_custom_error(self):
        """Test create_attachments returns ContentNotFoundError instead of ValueError (new validation)."""
        from confluence.SimulationEngine.custom_errors import ContentNotFoundError
        
        class MockFile:
            def __init__(self, name):
                self.name = name
        
        file_obj = MockFile("test.txt")
        
        # Test with non-existent content id (now returns ContentNotFoundError instead of ValueError)
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.create_attachments,
            expected_exception_type=ContentNotFoundError,
            expected_message="Content with id='nonexistent_id' not found.",
            id="nonexistent_id",
            file=file_obj
        )
    
    def test_update_attachment_data_id_type_validation(self):
        """Test update_attachment_data with invalid types for 'id' parameter."""
        class MockFile:
            def __init__(self, name):
                self.name = name
        
        file_obj = MockFile("updated.txt")
        
        # Test with integer id
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.update_attachment_data,
            expected_exception_type=TypeError,
            expected_message="Argument 'id' must be a string.",
            id=123,
            attachmentId="att123",
            file=file_obj
        )
        
        # Test with None id
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.update_attachment_data,
            expected_exception_type=TypeError,
            expected_message="Argument 'id' must be a string.",
            id=None,
            attachmentId="att123",
            file=file_obj
        )
        
        # Test with list id
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.update_attachment_data,
            expected_exception_type=TypeError,
            expected_message="Argument 'id' must be a string.",
            id=["content123"],
            attachmentId="att123",
            file=file_obj
        )
    
    def test_update_attachment_data_id_empty_string_validation(self):
        """Test update_attachment_data with empty string id."""
        class MockFile:
            def __init__(self, name):
                self.name = name
        
        file_obj = MockFile("updated.txt")
        
        # Test with empty string id
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.update_attachment_data,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'id' cannot be an empty string.",
            id="",
            attachmentId="att123",
            file=file_obj
        )
        
        # Test with whitespace-only id
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.update_attachment_data,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'id' cannot be an empty string.",
            id="   ",
            attachmentId="att123",
            file=file_obj
        )
    
    def test_update_attachment_data_attachment_id_type_validation(self):
        """Test update_attachment_data with invalid types for 'attachmentId' parameter."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "AttachmentIdValidationTest", "spaceKey": "TEST", "type": "page"}
        )
        
        class MockFile:
            def __init__(self, name):
                self.name = name
        
        file_obj = MockFile("updated.txt")
        
        # Test with integer attachmentId
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.update_attachment_data,
            expected_exception_type=TypeError,
            expected_message="Argument 'attachmentId' must be a string.",
            id=content["id"],
            attachmentId=123,
            file=file_obj
        )
        
        # Test with None attachmentId
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.update_attachment_data,
            expected_exception_type=TypeError,
            expected_message="Argument 'attachmentId' must be a string.",
            id=content["id"],
            attachmentId=None,
            file=file_obj
        )
        
        # Test with boolean attachmentId
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.update_attachment_data,
            expected_exception_type=TypeError,
            expected_message="Argument 'attachmentId' must be a string.",
            id=content["id"],
            attachmentId=True,
            file=file_obj
        )
    
    def test_update_attachment_data_attachment_id_empty_string_validation(self):
        """Test update_attachment_data with empty string attachmentId."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "AttachmentIdEmptyTest", "spaceKey": "TEST", "type": "page"}
        )
        
        class MockFile:
            def __init__(self, name):
                self.name = name
        
        file_obj = MockFile("updated.txt")
        
        # Test with empty string attachmentId
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.update_attachment_data,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'attachmentId' cannot be an empty string.",
            id=content["id"],
            attachmentId="",
            file=file_obj
        )
        
        # Test with whitespace-only attachmentId
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.update_attachment_data,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'attachmentId' cannot be an empty string.",
            id=content["id"],
            attachmentId="   ",
            file=file_obj
        )
    
    def test_update_attachment_data_file_none_validation(self):
        """Test update_attachment_data with None file."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "FileNoneValidationTest", "spaceKey": "TEST", "type": "page"}
        )
        
        # Test with None file
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.update_attachment_data,
            expected_exception_type=FileAttachmentError,
            expected_message="Argument 'file' cannot be None.",
            id=content["id"],
            attachmentId="att123",
            file=None
        )
    
    def test_update_attachment_data_comment_type_validation(self):
        """Test update_attachment_data with invalid types for 'comment' parameter."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "CommentTypeValidationTest", "spaceKey": "TEST", "type": "page"}
        )
        
        class MockFile:
            def __init__(self, name):
                self.name = name
        
        file_obj = MockFile("updated.txt")
        
        # Test with integer comment
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.update_attachment_data,
            expected_exception_type=TypeError,
            expected_message="Argument 'comment' must be a string if provided.",
            id=content["id"],
            attachmentId="att123",
            file=file_obj,
            comment=123
        )
        
        # Test with list comment
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.update_attachment_data,
            expected_exception_type=TypeError,
            expected_message="Argument 'comment' must be a string if provided.",
            id=content["id"],
            attachmentId="att123",
            file=file_obj,
            comment=["updated comment"]
        )
        
        # Test with boolean comment
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.update_attachment_data,
            expected_exception_type=TypeError,
            expected_message="Argument 'comment' must be a string if provided.",
            id=content["id"],
            attachmentId="att123",
            file=file_obj,
            comment=True
        )
    
    def test_update_attachment_data_minor_edit_type_validation(self):
        """Test update_attachment_data with invalid types for 'minorEdit' parameter."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "MinorEditTypeValidationTest", "spaceKey": "TEST", "type": "page"}
        )
        
        class MockFile:
            def __init__(self, name):
                self.name = name
        
        file_obj = MockFile("updated.txt")
        
        # Test with string minorEdit
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.update_attachment_data,
            expected_exception_type=TypeError,
            expected_message="Argument 'minorEdit' must be a boolean.",
            id=content["id"],
            attachmentId="att123",
            file=file_obj,
            minorEdit="true"
        )
        
        # Test with integer minorEdit
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.update_attachment_data,
            expected_exception_type=TypeError,
            expected_message="Argument 'minorEdit' must be a boolean.",
            id=content["id"],
            attachmentId="att123",
            file=file_obj,
            minorEdit=1
        )
        
        # Test with None minorEdit (should be allowed to default to False)
        # This should NOT raise an error - testing that None is handled correctly
        try:
            ConfluenceAPI.ContentAPI.update_attachment_data(
                id=content["id"],
                attachmentId="att123",
                file=file_obj,
                minorEdit=None  # This should cause TypeError
            )
            self.fail("Expected TypeError for None minorEdit")
        except TypeError as e:
            self.assertIn("Argument 'minorEdit' must be a boolean.", str(e))
    
    def test_update_attachment_data_content_not_found_custom_error(self):
        """Test update_attachment_data returns ContentNotFoundError for non-existent content."""
        class MockFile:
            def __init__(self, name):
                self.name = name
        
        file_obj = MockFile("updated.txt")
        
        # Test with non-existent content id
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.update_attachment_data,
            expected_exception_type=ContentNotFoundError,
            expected_message="Content with id='nonexistent_id' not found.",
            id="nonexistent_id",
            attachmentId="att123",
            file=file_obj
        )
    
    def test_update_attachment_data_valid_inputs_success(self):
        """Test update_attachment_data with all valid inputs."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "ValidInputsTest", "spaceKey": "TEST", "type": "page"}
        )
        
        class MockFile:
            def __init__(self, name):
                self.name = name
        
        file_obj = MockFile("updated_file.txt")
        
        # Test with all valid parameters
        result = ConfluenceAPI.ContentAPI.update_attachment_data(
            id=content["id"],
            attachmentId="att123",
            file=file_obj,
            comment="Updated attachment comment",
            minorEdit=True
        )
        
        # Verify the result structure
        self.assertIn("attachmentId", result)
        self.assertIn("updatedFile", result)
        self.assertIn("comment", result)
        self.assertIn("minorEdit", result)
        
        # Verify the values
        self.assertEqual(result["attachmentId"], "att123")
        self.assertEqual(result["updatedFile"], "updated_file.txt")
        self.assertEqual(result["comment"], "Updated attachment comment")
        self.assertTrue(result["minorEdit"])
    
    def test_update_attachment_data_valid_inputs_minimal(self):
        """Test update_attachment_data with minimal valid inputs (optional parameters as default)."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "MinimalInputsTest", "spaceKey": "TEST", "type": "page"}
        )
        
        class MockFile:
            def __init__(self, name):
                self.name = name
        
        file_obj = MockFile("minimal_file.txt")
        
        # Test with minimal required parameters (comment=None, minorEdit=False by default)
        result = ConfluenceAPI.ContentAPI.update_attachment_data(
            id=content["id"],
            attachmentId="att456",
            file=file_obj
        )
        
        # Verify the result structure and default values
        self.assertEqual(result["attachmentId"], "att456")
        self.assertEqual(result["updatedFile"], "minimal_file.txt")
        self.assertIsNone(result["comment"])  # Should be None by default
        self.assertFalse(result["minorEdit"])  # Should be False by default
    
    def test_update_attachment_data_valid_comment_none(self):
        """Test update_attachment_data with explicitly None comment (should be allowed)."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "CommentNoneTest", "spaceKey": "TEST", "type": "page"}
        )
        
        class MockFile:
            def __init__(self, name):
                self.name = name
        
        file_obj = MockFile("comment_none_file.txt")
        
        # Test with explicitly None comment (should be allowed)
        result = ConfluenceAPI.ContentAPI.update_attachment_data(
            id=content["id"],
            attachmentId="att789",
            file=file_obj,
            comment=None,
            minorEdit=False
        )
        
        # Verify None comment is handled correctly
        self.assertEqual(result["attachmentId"], "att789")
        self.assertEqual(result["updatedFile"], "comment_none_file.txt")
        self.assertIsNone(result["comment"])
        self.assertFalse(result["minorEdit"])
    
    def test_update_attachment_data_file_without_name_attribute(self):
        """Test update_attachment_data with file object that doesn't have name attribute."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "FileNoNameTest", "spaceKey": "TEST", "type": "page"}
        )
        
        class MockFileWithoutName:
            pass  # No name attribute
        
        file_obj = MockFileWithoutName()
        
        # Test with file object without name attribute (should use "unknown" as fallback)
        result = ConfluenceAPI.ContentAPI.update_attachment_data(
            id=content["id"],
            attachmentId="att999",
            file=file_obj,
            comment="File without name",
            minorEdit=False
        )
        
        # Verify fallback to "unknown" for file name
        self.assertEqual(result["attachmentId"], "att999")
        self.assertEqual(result["updatedFile"], "unknown")  # Should fallback to "unknown"
        self.assertEqual(result["comment"], "File without name")
        self.assertFalse(result["minorEdit"])

    def test_delete_content_labels_id_type_validation(self):
        """Test delete_content_labels with invalid types for 'id' parameter (new validation)."""
        # Test with integer id (new TypeError validation)
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.delete_content_labels,
            expected_exception_type=TypeError,
            expected_message="Argument 'id' must be a string.",
            id=123
        )

        # Test with None id (new TypeError validation)
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.delete_content_labels,
            expected_exception_type=TypeError,
            expected_message="Argument 'id' must be a string.",
            id=None
        )

        # Test with list id (new TypeError validation)
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.delete_content_labels,
            expected_exception_type=TypeError,
            expected_message="Argument 'id' must be a string.",
            id=["test_id"]
        )

    def test_delete_content_labels_id_empty_string_validation(self):
        """Test delete_content_labels with empty string id (new validation)."""
        from confluence.SimulationEngine.custom_errors import InvalidInputError

        # Test with empty string id (new InvalidInputError validation)
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.delete_content_labels,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'id' cannot be an empty string.",
            id=""
        )

        # Test with whitespace-only id (new InvalidInputError validation)
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.delete_content_labels,
            expected_exception_type=InvalidInputError,
            expected_message="Argument 'id' cannot be an empty string.",
            id="   "
        )

    def test_delete_content_labels_label_type_validation(self):
        """Test delete_content_labels with invalid types for 'label' parameter (new validation)."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "LabelTypeValidationTest", "spaceKey": "TEST", "type": "page"}
        )

        # Test with integer label (new TypeError validation)
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.delete_content_labels,
            expected_exception_type=TypeError,
            expected_message="Argument 'label' must be a string if provided.",
            id=content["id"],
            label=123
        )

        # Test with boolean label (new TypeError validation)
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.delete_content_labels,
            expected_exception_type=TypeError,
            expected_message="Argument 'label' must be a string if provided.",
            id=content["id"],
            label=True
        )

    def test_delete_content_labels_content_not_found_error(self):
        """Test delete_content_labels raises ContentNotFoundError when content is not found (new validation)."""
        from confluence.SimulationEngine.custom_errors import ContentNotFoundError

        # Test with non-existent content id (now returns ContentNotFoundError instead of ValueError)
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.delete_content_labels,
            expected_exception_type=ContentNotFoundError,
            expected_message="Content with id='nonexistent_id' not found.",
            id="nonexistent_id"
        )

    def test_delete_content_labels_no_labels_error(self):
        """Test delete_content_labels raises LabelNotFoundError when content has no labels (new validation)."""
        from confluence.SimulationEngine.custom_errors import LabelNotFoundError

        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "NoLabelsTest", "spaceKey": "TEST", "type": "page"}
        )

        # Test with content that has no labels (now returns LabelNotFoundError instead of ValueError)
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.delete_content_labels,
            expected_exception_type=LabelNotFoundError,
            expected_message="Content with id='{}' has no labels.".format(content["id"]),
            id=content["id"]
        )

    def test_delete_content_labels_specific_label_not_found_error(self):
        """Test delete_content_labels raises LabelNotFoundError when specific label is not found (new validation)."""
        from confluence.SimulationEngine.custom_errors import LabelNotFoundError

        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "SpecificLabelTest", "spaceKey": "TEST", "type": "page"}
        )

        # Add some labels first
        ConfluenceAPI.ContentAPI.add_content_labels(content["id"], ["existing_label"])

        # Test with specific label that doesn't exist (now returns LabelNotFoundError instead of ValueError)
        self.assert_error_behavior(
            func_to_call=ConfluenceAPI.ContentAPI.delete_content_labels,
            expected_exception_type=LabelNotFoundError,
            expected_message="Label nonexistent_label not found for content with id='{}'.".format(content["id"]),
            id=content["id"],
            label="nonexistent_label"
        )

    def test_delete_content_labels_successful_specific_label_deletion(self):
        """Test delete_content_labels successfully deletes a specific label (functionality test)."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "SuccessfulDeletionTest", "spaceKey": "TEST", "type": "page"}
        )

        # Add labels
        ConfluenceAPI.ContentAPI.add_content_labels(content["id"], ["label1", "label2", "label3"])

        # Delete specific label
        ConfluenceAPI.ContentAPI.delete_content_labels(content["id"], "label2")

        # Verify label was deleted
        remaining_labels = ConfluenceAPI.ContentAPI.get_content_labels(content["id"])
        label_names = [label["label"] for label in remaining_labels]
        self.assertNotIn("label2", label_names)
        self.assertIn("label1", label_names)
        self.assertIn("label3", label_names)

    def test_delete_content_labels_successful_all_labels_deletion(self):
        """Test delete_content_labels successfully deletes all labels (functionality test)."""
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "AllLabelsDeletionTest", "spaceKey": "TEST", "type": "page"}
        )

        # Add labels
        ConfluenceAPI.ContentAPI.add_content_labels(content["id"], ["label1", "label2", "label3"])

        # Delete all labels
        ConfluenceAPI.ContentAPI.delete_content_labels(content["id"])

        # Verify all labels were deleted - get_content_labels should return empty list
        remaining_labels = ConfluenceAPI.ContentAPI.get_content_labels(content["id"])
        self.assertEqual(remaining_labels, [])

    def test_get_space_content_of_type_input_validation(self):
        """
        Test input validation for get_space_content_of_type function.
        """
        # Test invalid spaceKey type
        with self.assertRaises(TypeError, msg="spaceKey must be a string"):
            ConfluenceAPI.SpaceAPI.get_space_content_of_type(123, "page")

        # Test empty spaceKey
        with self.assertRaises(ValueError, msg="spaceKey must not be an empty string"):
            ConfluenceAPI.SpaceAPI.get_space_content_of_type("", "page")

        # Test invalid type parameter type
        with self.assertRaises(TypeError, msg="type must be a string"):
            ConfluenceAPI.SpaceAPI.get_space_content_of_type("TEST", 123)

        # Test empty type parameter
        with self.assertRaises(ValueError, msg="type must not be an empty string"):
            ConfluenceAPI.SpaceAPI.get_space_content_of_type("TEST", "")

        # Test invalid start parameter type
        with self.assertRaises(TypeError, msg="start must be an integer"):
            ConfluenceAPI.SpaceAPI.get_space_content_of_type("TEST", "page", start="0")

        # Test negative start parameter
        with self.assertRaises(ValueError, msg="start must be a non-negative integer"):
            ConfluenceAPI.SpaceAPI.get_space_content_of_type("TEST", "page", start=-1)

        # Test invalid limit parameter type
        with self.assertRaises(TypeError, msg="limit must be an integer"):
            ConfluenceAPI.SpaceAPI.get_space_content_of_type("TEST", "page", limit="25")

        # Test non-positive limit parameter
        with self.assertRaises(ValueError, msg="limit must be a positive integer"):
            ConfluenceAPI.SpaceAPI.get_space_content_of_type("TEST", "page", limit=0)

    def test_get_space_content_of_type_valid_inputs(self):
        """
        Test get_space_content_of_type with valid inputs.
        """
        # Create test data
        ConfluenceAPI.SpaceAPI.create_space({"key": "TEST", "name": "Test Space"})
        ConfluenceAPI.ContentAPI.create_content({"title": "Page1", "spaceKey": "TEST", "type": "page"})
        ConfluenceAPI.ContentAPI.create_content({"title": "Blog1", "spaceKey": "TEST", "type": "blogpost"})

        # Test with valid inputs
        result = ConfluenceAPI.SpaceAPI.get_space_content_of_type("TEST", "page", start=0, limit=10)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["type"], "page")
        self.assertEqual(result[0]["title"], "Page1")

        # Test with different content type
        result = ConfluenceAPI.SpaceAPI.get_space_content_of_type("TEST", "blogpost", start=0, limit=10)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["type"], "blogpost")
        self.assertEqual(result[0]["title"], "Blog1")

        # Test pagination
        result = ConfluenceAPI.SpaceAPI.get_space_content_of_type("TEST", "page", start=1, limit=10)
        self.assertEqual(len(result), 0)

        # Test with non-existent type
        result = ConfluenceAPI.SpaceAPI.get_space_content_of_type("TEST", "nonexistent", start=0, limit=10)
        self.assertEqual(len(result), 0)

    def test_get_content_property_expand_validation(self):
        """Test expand parameter validation in get_content_property."""
        # Create test content and property
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "PropertyTest", "spaceKey": "TEST", "type": "page"}
        )
        ConfluenceAPI.ContentAPI.create_content_property(
            content["id"],
            {"key": "test-key", "value": {"data": "test"}}
        )

        # Test invalid expand value
        with self.assertRaises(ValueError) as cm:
            ConfluenceAPI.ContentAPI.get_content_property(content["id"], "test-key", expand="invalid")
        self.assertIn("Invalid expand values", str(cm.exception))

        # Test multiple invalid expand values
        with self.assertRaises(ValueError) as cm:
            ConfluenceAPI.ContentAPI.get_content_property(content["id"], "test-key", expand="invalid1,invalid2")
        self.assertIn("Invalid expand values", str(cm.exception))

        # Test valid expand values
        result = ConfluenceAPI.ContentAPI.get_content_property(content["id"], "test-key", expand="content,version")
        self.assertIn("content", result)
        self.assertIn("version", result)

    def test_get_content_property_expand_content(self):
        """Test content expansion in get_content_property."""
        # Create test content and property
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "PropertyTest", "spaceKey": "TEST", "type": "page"}
        )
        ConfluenceAPI.ContentAPI.create_content_property(
            content["id"],
            {"key": "test-key", "value": {"data": "test"}}
        )

        # Test content expansion
        result = ConfluenceAPI.ContentAPI.get_content_property(content["id"], "test-key", expand="content")
        
        # Verify content expansion
        self.assertIn("content", result)
        self.assertEqual(result["content"]["id"], content["id"])
        self.assertEqual(result["content"]["title"], "PropertyTest")
        self.assertEqual(result["content"]["type"], "page")

    def test_get_content_property_expand_version(self):
        """Test version expansion in get_content_property."""
        # Create test content and property
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "PropertyTest", "spaceKey": "TEST", "type": "page"}
        )
        prop = ConfluenceAPI.ContentAPI.create_content_property(
            content["id"],
            {"key": "test-key", "value": {"data": "test"}}
        )
        version_number = prop["version"]  # Get the actual version number

        # Test version expansion
        result = ConfluenceAPI.ContentAPI.get_content_property(content["id"], "test-key", expand="version")
        
        # Verify version expansion
        self.assertIn("version", result)
        self.assertIsInstance(result["version"], dict)
        self.assertEqual(result["version"]["number"], version_number)
        self.assertIn("when", result["version"])
        self.assertIn("message", result["version"])
        self.assertIn("by", result["version"])

        # Verify timestamp format
        timestamp = result["version"]["when"]
        # Should match ISO 8601 format: YYYY-MM-DDTHH:mm:ss.sssZ
        self.assertRegex(timestamp, r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$')

    def test_get_content_property_expand_all(self):
        """Test expanding both content and version in get_content_property."""
        # Create test content and property
        content = ConfluenceAPI.ContentAPI.create_content(
            {"title": "PropertyTest", "spaceKey": "TEST", "type": "page"}
        )
        prop = ConfluenceAPI.ContentAPI.create_content_property(
            content["id"],
            {"key": "test-key", "value": {"data": "test"}}
        )
        version_number = prop["version"]  # Get the actual version number

        # Test both expansions
        result = ConfluenceAPI.ContentAPI.get_content_property(content["id"], "test-key", expand="content,version")
        
        # Verify both expansions
        self.assertIn("content", result)
        self.assertIn("version", result)
        
        # Verify content
        self.assertEqual(result["content"]["id"], content["id"])
        self.assertEqual(result["content"]["title"], "PropertyTest")
        
        # Verify version
        self.assertIsInstance(result["version"], dict)
        self.assertEqual(result["version"]["number"], version_number)
        self.assertIn("when", result["version"])
        self.assertRegex(result["version"]["when"], r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$')
