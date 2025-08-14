# APIs/google_calendar/tests/test_patch_calendar_list_entry_verification.py

import unittest
from unittest.mock import patch
import uuid

from .. import patch_calendar_list_entry
from ..SimulationEngine.db import DB


class TestPatchCalendarListVerification(unittest.TestCase):
    """Test cases for patch_calendar_list_entry function validation and security."""

    def setUp(self):
        """Set up test data before each test."""
        DB.clear()
        DB.update({
            "acl_rules": {},
            "calendar_list": {
                "primary": {
                    "id": "primary",
                    "summary": "Primary Calendar",
                    "description": "Default primary calendar",
                    "timeZone": "UTC",
                    "primary": True
                },
                "test_calendar": {
                    "id": "test_calendar",
                    "summary": "Test Calendar",
                    "description": "Test description",
                    "timeZone": "America/New_York"
                }
            },
            "calendars": {},
            "channels": {},
            "colors": {"calendar": {}, "event": {}},
            "events": {}
        })

    # --- Valid Input Tests ---
    def test_valid_patch_with_summary(self):
        """Test successful patch with summary update."""
        result = patch_calendar_list_entry(
            calendarId="test_calendar",
            resource={"summary": "Updated Summary"}
        )
        self.assertEqual(result["summary"], "Updated Summary")
        self.assertEqual(result["id"], "test_calendar")
        self.assertEqual(result["description"], "Test description")  # Unchanged
        self.assertEqual(result["timeZone"], "America/New_York")  # Unchanged

    def test_valid_patch_with_multiple_fields(self):
        """Test successful patch with multiple field updates."""
        result = patch_calendar_list_entry(
            calendarId="primary",
            resource={
                "summary": "New Primary Summary",
                "description": "New description",
                "timeZone": "Europe/London"
            }
        )
        self.assertEqual(result["summary"], "New Primary Summary")
        self.assertEqual(result["description"], "New description")
        self.assertEqual(result["timeZone"], "Europe/London")
        self.assertEqual(result["id"], "primary")

    def test_valid_patch_with_empty_resource(self):
        """Test patch with empty resource dictionary (no changes)."""
        original_entry = DB["calendar_list"]["test_calendar"].copy()
        result = patch_calendar_list_entry(
            calendarId="test_calendar",
            resource={}
        )
        self.assertEqual(result, original_entry)

    def test_valid_patch_with_none_resource(self):
        """Test patch with None resource (no changes)."""
        original_entry = DB["calendar_list"]["test_calendar"].copy()
        result = patch_calendar_list_entry(
            calendarId="test_calendar",
            resource=None
        )
        self.assertEqual(result, original_entry)

    def test_valid_patch_with_color_rgb_format_true(self):
        """Test patch with colorRgbFormat=True (parameter accepted but not implemented)."""
        result = patch_calendar_list_entry(
            calendarId="test_calendar",
            colorRgbFormat=True,
            resource={"summary": "Updated with color format"}
        )
        self.assertEqual(result["summary"], "Updated with color format")

    def test_valid_patch_with_additional_field(self):
        """Test patch with additional custom field."""
        result = patch_calendar_list_entry(
            calendarId="test_calendar",
            resource={"customField": "custom value"}
        )
        self.assertEqual(result["customField"], "custom value")
        self.assertEqual(result["summary"], "Test Calendar")  # Unchanged

    # --- TypeError Tests ---
    def test_calendar_id_not_string(self):
        """Test TypeError when calendarId is not a string."""
        with self.assertRaises(TypeError) as cm:
            patch_calendar_list_entry(calendarId=123, resource={})
        self.assertEqual(str(cm.exception), "calendarId must be a string")

    def test_color_rgb_format_not_boolean(self):
        """Test TypeError when colorRgbFormat is not a boolean."""
        with self.assertRaises(TypeError) as cm:
            patch_calendar_list_entry(
                calendarId="test_calendar",
                colorRgbFormat="true",
                resource={}
            )
        self.assertEqual(str(cm.exception), "colorRgbFormat must be a boolean")

    def test_resource_not_dictionary(self):
        """Test TypeError when resource is not a dictionary."""
        with self.assertRaises(TypeError) as cm:
            patch_calendar_list_entry(
                calendarId="test_calendar",
                resource="not a dict"
            )
        self.assertEqual(str(cm.exception), "resource must be a dictionary")

    def test_resource_list_not_dictionary(self):
        """Test TypeError when resource is a list."""
        with self.assertRaises(TypeError) as cm:
            patch_calendar_list_entry(
                calendarId="test_calendar",
                resource=["not", "a", "dict"]
            )
        self.assertEqual(str(cm.exception), "resource must be a dictionary")

    # --- ValueError Tests ---
    def test_calendar_id_empty_string(self):
        """Test ValueError when calendarId is empty string."""
        with self.assertRaises(ValueError) as cm:
            patch_calendar_list_entry(calendarId="", resource={})
        self.assertEqual(str(cm.exception), "calendarId cannot be empty or None")

    def test_calendar_id_whitespace_only(self):
        """Test ValueError when calendarId is whitespace only."""
        with self.assertRaises(ValueError) as cm:
            patch_calendar_list_entry(calendarId="   ", resource={})
        self.assertEqual(str(cm.exception), "calendarId cannot be empty or None")

    def test_calendar_not_found(self):
        """Test ValueError when calendar list entry doesn't exist."""
        with self.assertRaises(ValueError) as cm:
            patch_calendar_list_entry(calendarId="nonexistent", resource={})
        self.assertEqual(str(cm.exception), "CalendarList entry 'nonexistent' not found.")

    def test_summary_not_string(self):
        """Test ValueError when summary field is not a string."""
        with self.assertRaises(ValueError) as cm:
            patch_calendar_list_entry(
                calendarId="test_calendar",
                resource={"summary": 123}
            )
        self.assertEqual(str(cm.exception), "Field 'summary' must be a string")

    def test_description_not_string(self):
        """Test ValueError when description field is not a string."""
        with self.assertRaises(ValueError) as cm:
            patch_calendar_list_entry(
                calendarId="test_calendar",
                resource={"description": ["not", "string"]}
            )
        self.assertEqual(str(cm.exception), "Field 'description' must be a string")

    def test_timezone_not_string(self):
        """Test ValueError when timeZone field is not a string."""
        with self.assertRaises(ValueError) as cm:
            patch_calendar_list_entry(
                calendarId="test_calendar",
                resource={"timeZone": 123}
            )
        self.assertEqual(str(cm.exception), "Field 'timeZone' must be a string")

    def test_id_field_not_string(self):
        """Test ValueError when id field is not a string."""
        with self.assertRaises(ValueError) as cm:
            patch_calendar_list_entry(
                calendarId="test_calendar",
                resource={"id": 123}
            )
        self.assertEqual(str(cm.exception), "Field 'id' must be a string")

    # --- Security Tests ---
    def test_cannot_modify_id_field_different_value(self):
        """Test that modifying ID field to different value is prevented."""
        with self.assertRaises(ValueError) as cm:
            patch_calendar_list_entry(
                calendarId="test_calendar",
                resource={"id": "different_id"}
            )
        self.assertEqual(str(cm.exception), "Cannot modify the 'id' field of an existing calendar list entry")

    def test_can_set_id_field_same_value(self):
        """Test that setting ID field to same value is allowed."""
        result = patch_calendar_list_entry(
            calendarId="test_calendar",
            resource={"id": "test_calendar", "summary": "Updated"}
        )
        self.assertEqual(result["id"], "test_calendar")
        self.assertEqual(result["summary"], "Updated")

    # --- Edge Cases ---
    def test_patch_with_none_values(self):
        """Test patch with None values in resource."""
        result = patch_calendar_list_entry(
            calendarId="test_calendar",
            resource={"customField": None}
        )
        self.assertIsNone(result["customField"])

    def test_patch_overwrites_existing_field(self):
        """Test that patch overwrites existing field values."""
        # First patch
        patch_calendar_list_entry(
            calendarId="test_calendar",
            resource={"customField": "first_value"}
        )
        
        # Second patch overwrites
        result = patch_calendar_list_entry(
            calendarId="test_calendar",
            resource={"customField": "second_value"}
        )
        self.assertEqual(result["customField"], "second_value")

    def test_multiple_field_type_validations(self):
        """Test multiple field type validations in single call."""
        with self.assertRaises(ValueError) as cm:
            patch_calendar_list_entry(
                calendarId="test_calendar",
                resource={
                    "summary": 123,  # First invalid field
                    "description": "valid description"
                }
            )
        self.assertEqual(str(cm.exception), "Field 'summary' must be a string")

    def test_db_persistence(self):
        """Test that changes are persisted to the database."""
        patch_calendar_list_entry(
            calendarId="test_calendar",
            resource={"summary": "Persisted Summary"}
        )
        
        # Verify change is in DB
        self.assertEqual(DB["calendar_list"]["test_calendar"]["summary"], "Persisted Summary")

    def test_return_complete_entry(self):
        """Test that function returns complete calendar list entry."""
        result = patch_calendar_list_entry(
            calendarId="test_calendar",
            resource={"summary": "New Summary"}
        )
        
        # Should contain all original fields plus updates
        expected_keys = {"id", "summary", "description", "timeZone"}
        self.assertTrue(expected_keys.issubset(set(result.keys())))


if __name__ == "__main__":
    unittest.main() 