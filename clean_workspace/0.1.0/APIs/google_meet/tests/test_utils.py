import unittest
import os


from google_meet.tests.common import reset_db
from google_meet import DB
from google_meet import utils
from google_meet.SimulationEngine.db import save_state, load_state
from common_utils.base_case import BaseTestCaseWithErrorHandler


class TestSimulationEngineUtils(BaseTestCaseWithErrorHandler):

    def setUp(self):
        reset_db()

    def test_save_and_load_state(self):
        # Add test data
        DB["spaces"]["test_space"] = {"id": "test_space", "name": "Test Space"}
        DB["conferenceRecords"]["conf1"] = {"id": "conf1", "start_time": "10:00"}

        # Save the state
        save_state("test_save_load.json")

        # Clear the DB
        DB.clear()
        self.assertEqual(len(DB), 0)

        # Load the state
        load_state("test_save_load.json")

        # Verify data was restored
        self.assertIn("spaces", DB)
        self.assertIn("test_space", DB["spaces"])
        self.assertEqual(DB["spaces"]["test_space"]["name"], "Test Space")

        self.assertIn("conferenceRecords", DB)
        self.assertIn("conf1", DB["conferenceRecords"])
        self.assertEqual(DB["conferenceRecords"]["conf1"]["start_time"], "10:00")

        # Clean up
        os.remove("test_save_load.json")

    def test_load_state_file_not_found(self):
        """Test loading state from a non-existent file."""
        with self.assertRaises(FileNotFoundError) as context:
            load_state("nonexistent_file.json")
        self.assertEqual(
            str(context.exception),
            "State file nonexistent_file.json not found. Starting with default state.",
        )

    def test_ensure_exists(self):
        # Setup test data
        DB["test_collection"] = {"item1": {"id": "item1"}}

        # Test existing item
        result = utils.ensure_exists("test_collection", "item1")
        self.assertTrue(result)

        # Test non-existent item
        with self.assertRaises(ValueError):
            utils.ensure_exists("test_collection", "nonexistent_item")

        # Test non-existent collection
        with self.assertRaises(ValueError):
            utils.ensure_exists("nonexistent_collection", "item1")

    def test_paginate_results_basic(self):
        # Create test items
        items = [{"id": f"item{i}"} for i in range(1, 6)]

        # Test with no pagination parameters
        result = utils.paginate_results(items, "test_items")
        self.assertEqual(len(result["test_items"]), 5)
        self.assertNotIn("nextPageToken", result)

        # Test with pageSize parameter
        result = utils.paginate_results(items, "test_items", page_size=2)
        self.assertEqual(len(result["test_items"]), 2)
        self.assertEqual(result["test_items"][0]["id"], "item1")
        self.assertEqual(result["test_items"][1]["id"], "item2")
        self.assertIn("nextPageToken", result)
        self.assertEqual(result["nextPageToken"], "2")

    def test_paginate_results_with_token(self):
        # Create test items
        items = [{"id": f"item{i}"} for i in range(1, 6)]

        # Test with pageToken parameter
        result = utils.paginate_results(
            items, "test_items", page_size=2, page_token="2"
        )
        self.assertEqual(len(result["test_items"]), 2)
        self.assertEqual(result["test_items"][0]["id"], "item3")
        self.assertEqual(result["test_items"][1]["id"], "item4")
        self.assertIn("nextPageToken", result)
        self.assertEqual(result["nextPageToken"], "4")

        # Test with last page
        result = utils.paginate_results(
            items, "test_items", page_size=2, page_token="4"
        )
        self.assertEqual(len(result["test_items"]), 1)
        self.assertEqual(result["test_items"][0]["id"], "item5")
        self.assertNotIn("nextPageToken", result)

    def test_paginate_results_edge_cases(self):
        # Create test items
        items = [{"id": f"item{i}"} for i in range(1, 6)]

        # Test with invalid pageToken
        result = utils.paginate_results(
            items, "test_items", page_size=2, page_token="invalid"
        )
        self.assertEqual(len(result["test_items"]), 2)
        self.assertEqual(result["test_items"][0]["id"], "item1")

        # Test with empty items list
        result = utils.paginate_results([], "test_items")
        self.assertEqual(len(result["test_items"]), 0)
        self.assertNotIn("nextPageToken", result)

        # Test with pageSize larger than items count
        result = utils.paginate_results(items, "test_items", page_size=10)
        self.assertEqual(len(result["test_items"]), 5)
        self.assertNotIn("nextPageToken", result)


if __name__ == "__main__":
    unittest.main()
