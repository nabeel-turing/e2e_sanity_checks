#!/usr/bin/env python3
"""
Test cases for in-memory database functionality.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the parent directory to the path to import the modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from phone.calls import make_call, prepare_call, show_call_recipient_choices
from phone.SimulationEngine.db import DB
from phone.SimulationEngine.utils import get_call_history, get_prepared_calls, get_recipient_choices
from common_utils.base_case import BaseTestCaseWithErrorHandler


class TestInMemoryDatabase(BaseTestCaseWithErrorHandler):
    """Test cases for in-memory database functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Clear the database to ensure clean state for each test
        from phone.SimulationEngine.db import DB, load_state, save_state, DEFAULT_DB_PATH
        import tempfile
        import os
        
        # Create a temporary file for this test
        self.temp_db_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_db_path = self.temp_db_file.name
        self.temp_db_file.close()
        
        # Clear all data from DB
        DB.clear()
        
        # Load the default state using load_state
        load_state(DEFAULT_DB_PATH)
        
        # Clear dynamic data to start with empty collections
        DB["call_history"] = {}
        DB["prepared_calls"] = {}
        DB["recipient_choices"] = {}
        DB["not_found_records"] = {}
        DB["actions"] = []
        # Save the initial state to temporary file
        save_state(self.temp_db_path)
        
        # Store initial state
        self.initial_call_history = len(get_call_history())
        self.initial_prepared_calls = len(get_prepared_calls())
        self.initial_recipient_choices = len(get_recipient_choices())
        
        self.sample_recipients = [{
            "contact_name": "Test Contact",
            "recipient_type": "CONTACT",
            "contact_endpoints": [{
                "endpoint_type": "PHONE_NUMBER",
                "endpoint_value": "+3333333333",
                "endpoint_label": "mobile"
            }]
        }]

    def tearDown(self):
        """Clean up after each test."""
        from phone.SimulationEngine.db import save_state
        import os
        
        # Save the current state to temporary file
        save_state(self.temp_db_path)
        
        # Clean up temporary file
        if hasattr(self, 'temp_db_path') and os.path.exists(self.temp_db_path):
            os.unlink(self.temp_db_path)

    def test_make_call_updates_in_memory_db(self):
        """Test that make_call updates the in-memory database."""
        # Make a test call
        result = make_call(
            recipient_name="Test User 1",
            recipient_phone_number="+1111111111"
        )
        
        # Verify the call was successful
        self.assertEqual(result["status"], "success")
        self.assertIn("call_id", result)
        
        # Check that call history was updated in memory
        updated_call_history = len(get_call_history())
        self.assertGreater(updated_call_history, self.initial_call_history)
        
        # Verify the new call record exists
        call_history = get_call_history()
        call_ids = list(call_history.keys())
        self.assertIn(result["call_id"], call_ids)
        
        # Verify call details
        call_record = call_history[result["call_id"]]
        self.assertEqual(call_record["phone_number"], "+1111111111")
        self.assertEqual(call_record["recipient_name"], "Test User 1")

    def test_prepare_call_updates_in_memory_db(self):
        """Test that prepare_call updates the in-memory database."""
        # Prepare a test call
        result = prepare_call(recipients=self.sample_recipients)
        
        # Verify the prepare call was successful
        self.assertEqual(result["status"], "success")
        self.assertIn("call_id", result)
        
        # Check that prepared calls were updated in memory
        updated_prepared_calls = len(get_prepared_calls())
        self.assertGreater(updated_prepared_calls, self.initial_prepared_calls)
        
        # Verify the new prepared call record exists
        prepared_calls = get_prepared_calls()
        call_ids = list(prepared_calls.keys())
        self.assertIn(result["call_id"], call_ids)
        
        # Verify prepared call details
        prepared_call_record = prepared_calls[result["call_id"]]
        self.assertEqual(len(prepared_call_record["recipients"]), 1)
        self.assertEqual(prepared_call_record["recipients"][0]["recipient_name"], "Test Contact")

    def test_show_call_recipient_choices_updates_in_memory_db(self):
        """Test that show_call_recipient_choices updates the in-memory database."""
        # Show recipient choices
        result = show_call_recipient_choices(recipients=self.sample_recipients)
        
        # Verify the show choices was successful
        self.assertEqual(result["status"], "success")
        self.assertIn("call_id", result)
        
        # Check that recipient choices were updated in memory
        updated_recipient_choices = len(get_recipient_choices())
        self.assertGreater(updated_recipient_choices, self.initial_recipient_choices)
        
        # Verify the new choice record exists
        recipient_choices = get_recipient_choices()
        call_ids = list(recipient_choices.keys())
        self.assertIn(result["call_id"], call_ids)
        
        # Verify choice details
        choice_record = recipient_choices[result["call_id"]]
        self.assertEqual(len(choice_record["recipient_options"]), 1)
        self.assertEqual(choice_record["recipient_options"][0]["contact_name"], "Test Contact")

    def test_multiple_operations_accumulate_in_memory(self):
        """Test that multiple operations accumulate in the in-memory database."""
        # Make multiple calls
        call1 = make_call(recipient_name="User 1", recipient_phone_number="+1111111111")
        call2 = make_call(recipient_name="User 2", recipient_phone_number="+2222222222")
        
        # Prepare a call
        prepared = prepare_call(recipients=self.sample_recipients)
        
        # Show choices
        choices = show_call_recipient_choices(recipients=self.sample_recipients)
        
        # Verify all operations were successful
        self.assertEqual(call1["status"], "success")
        self.assertEqual(call2["status"], "success")
        self.assertEqual(prepared["status"], "success")
        self.assertEqual(choices["status"], "success")
        
        # Check that all records were added to memory
        final_call_history = len(get_call_history())
        final_prepared_calls = len(get_prepared_calls())
        final_recipient_choices = len(get_recipient_choices())
        
        # Should have added 2 calls, 1 prepared call, and 1 choice record
        self.assertEqual(final_call_history, self.initial_call_history + 2)
        self.assertEqual(final_prepared_calls, self.initial_prepared_calls + 1)
        self.assertEqual(final_recipient_choices, self.initial_recipient_choices + 1)

    def test_database_changes_not_persisted_to_file(self):
        """Test that database changes are not persisted to the file system."""
        # Get the initial file modification time
        db_file_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', 'DBs', 'PhoneDefaultDB.json'
        )
        
        if os.path.exists(db_file_path):
            initial_mtime = os.path.getmtime(db_file_path)
            
            # Make some operations that would update the database
            make_call(recipient_name="File Test User", recipient_phone_number="+9999999999")
            prepare_call(recipients=self.sample_recipients)
            show_call_recipient_choices(recipients=self.sample_recipients)
            
            # Check that the file modification time hasn't changed
            current_mtime = os.path.getmtime(db_file_path)
            self.assertEqual(current_mtime, initial_mtime, 
                           "Database file should not have been modified")

    def test_call_history_structure(self):
        """Test that call history records have the correct structure."""
        # Make a call
        result = make_call(
            recipient_name="Structure Test User",
            recipient_phone_number="+5555555555",
            on_speakerphone=True
        )
        
        # Get the call record from memory
        call_history = get_call_history()
        call_record = call_history[result["call_id"]]
        
        # Verify the structure
        required_fields = ["call_id", "timestamp", "phone_number", "recipient_name", 
                          "recipient_photo_url", "on_speakerphone", "status"]
        
        for field in required_fields:
            self.assertIn(field, call_record, f"Call record should contain {field}")
        
        # Verify specific values
        self.assertEqual(call_record["phone_number"], "+5555555555")
        self.assertEqual(call_record["recipient_name"], "Structure Test User")
        self.assertTrue(call_record["on_speakerphone"])
        self.assertEqual(call_record["status"], "completed")

    def test_prepared_call_structure(self):
        """Test that prepared call records have the correct structure."""
        # Prepare a call
        result = prepare_call(recipients=self.sample_recipients)
        
        # Get the prepared call record from memory
        prepared_calls = get_prepared_calls()
        prepared_call_record = prepared_calls[result["call_id"]]
        
        # Verify the structure
        required_fields = ["call_id", "timestamp", "recipients"]
        for field in required_fields:
            self.assertIn(field, prepared_call_record, f"Prepared call record should contain {field}")
        
        # Verify recipients structure
        recipients = prepared_call_record["recipients"]
        self.assertIsInstance(recipients, list)
        self.assertEqual(len(recipients), 1)
        
        recipient = recipients[0]
        self.assertIn("recipient_name", recipient)
        self.assertIn("recipient_type", recipient)
        self.assertIn("endpoints", recipient)

    def test_recipient_choice_structure(self):
        """Test that recipient choice records have the correct structure."""
        # Show choices
        result = show_call_recipient_choices(recipients=self.sample_recipients)
        
        # Get the choice record from memory
        recipient_choices = get_recipient_choices()
        choice_record = recipient_choices[result["call_id"]]
        
        # Verify the structure
        required_fields = ["call_id", "timestamp", "recipient_options"]
        for field in required_fields:
            self.assertIn(field, choice_record, f"Choice record should contain {field}")
        
        # Verify recipient_options structure
        recipient_options = choice_record["recipient_options"]
        self.assertIsInstance(recipient_options, list)
        self.assertEqual(len(recipient_options), 1)
        
        choice = recipient_options[0]
        self.assertIn("contact_name", choice)
        self.assertIn("recipient_type", choice)
        # Check for either endpoints (single endpoint choice) or endpoint (multiple endpoint choice)
        self.assertTrue("endpoints" in choice or "endpoint" in choice)


if __name__ == "__main__":
    unittest.main() 