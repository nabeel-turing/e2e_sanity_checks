"""
Comprehensive test suite for the update_list_item function.
"""
import unittest
import copy
import json
import os
from common_utils.base_case import BaseTestCaseWithErrorHandler
from ..SimulationEngine.db import DB
from ..SimulationEngine.custom_errors import ListNotFoundError, ListItemNotFoundError
from .. import update_list_item

class TestUpdateListItem(BaseTestCaseWithErrorHandler):
    
    def setUp(self):
        """Set up test database with a pristine copy of the default state before each test."""
        # Store original DB state
        self.original_db_state = {
            'notes': copy.deepcopy(DB["notes"]),
            'lists': copy.deepcopy(DB["lists"]),
            'title_index': copy.deepcopy(DB["title_index"]),
            'content_index': copy.deepcopy(DB["content_index"]),
            'operation_log': copy.deepcopy(DB["operation_log"])
        }
        
        # Load the default database state
        default_db_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'DBs', 'NotesAndListsDefaultDB.json')
        with open(default_db_path, 'r') as f:
            default_db = json.load(f)
        
        # Clear and restore to default state
        DB.clear()
        DB.update(default_db)

    def tearDown(self):
        """Restore original DB state after each test."""
        DB.clear()
        DB.update(self.original_db_state)

    def test_successful_update(self):
        """Test a standard, successful call to update a list item."""
        list_id = "list_1"
        item_id = "item_1a"
        new_content = "Fresh Almond Milk"
        
        result = update_list_item(list_id=list_id, list_item_id=item_id, updated_element=new_content)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["items"][item_id]["content"], new_content)
        self.assertNotEqual(result["items"][item_id]["created_at"], result["items"][item_id]["updated_at"])

    def test_update_using_search_term(self):
        """Test updating an item by finding the list via a search term."""
        item_id = "item_2b"
        new_content = "Thoroughly test authentication flow"
        
        result = update_list_item(list_id=None, search_term="Project Tasks", list_item_id=item_id, updated_element=new_content)
        
        self.assertEqual(result["id"], "list_2")
        self.assertEqual(result["items"][item_id]["content"], new_content)

    def test_list_not_found_error(self):
        """Test that a ListNotFoundError is raised for a non-existent list."""
        self.assert_error_behavior(
            lambda: update_list_item(list_id="list_that_does_not_exist", list_item_id="item_1a", updated_element="Any content"),
            ListNotFoundError,
            "No list found with the provided criteria."
        )

    def test_list_item_not_found_error(self):
        """Test that a ListItemNotFoundError is raised for a non-existent item."""
        self.assert_error_behavior(
            lambda: update_list_item(list_id="list_1", list_item_id="item_that_does_not_exist", updated_element="Any content"),
            ListItemNotFoundError,
            "List item 'item_that_does_not_exist' not found in list 'list_1'."
        )

    def test_invalid_parameter_raises_error(self):
        """Test that invalid or missing parameters raise a ValueError."""
        self.assert_error_behavior(
            lambda: update_list_item(list_id="list_1", list_item_id="", updated_element="Some content"),
            ValueError,
            "A valid 'list_item_id' (string) is required."
        )
        self.assert_error_behavior(
            lambda: update_list_item(list_id="list_1", list_item_id="item_1a", updated_element=""),
            ValueError,
            "A valid 'updated_element' (string) is required."
        )
        self.assert_error_behavior(
            lambda: update_list_item(list_id=123, list_item_id="item_1a", updated_element="Content"),
            ValueError,
            "'list_id' must be a string."
        )

if __name__ == "__main__":
    unittest.main()
