import unittest
from ..SimulationEngine.custom_errors import (
    ValidationError,
    ReminderNotFoundError,
    InvalidTimeError,
)
from common_utils.base_case import BaseTestCaseWithErrorHandler as BaseCase
import generic_reminders


class TestModifyReminder(BaseCase):
    def setUp(self):
        super().setUp()
        # Create a test reminder first
        self.test_reminder = generic_reminders.create_reminder(
            title="Test Reminder",
            description="Test description",
            start_date="2025-12-25",
            time_of_day="10:00:00",
            am_pm_or_unknown="AM",
        )
        self.reminder_id = self.test_reminder["reminders"][0]["id"]

    def test_modify_reminder_by_id_success(self):
        """Test successful reminder modification by ID."""
        result = generic_reminders.modify_reminder(
            reminder_ids=[self.reminder_id],
            title="Updated Title",
            description="Updated description",
            is_bulk_mutation=False,
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["message"], "1 reminder modified successfully")
        self.assertIn("reminders", result)
        self.assertIn("undo_operation_ids", result)
        self.assertEqual(len(result["reminders"]), 1)

        reminder = result["reminders"][0]
        self.assertEqual(reminder["title"], "Updated Title")
        self.assertEqual(reminder["description"], "Updated description")

    def test_modify_reminder_mark_completed(self):
        """Test marking reminder as completed."""
        result = generic_reminders.modify_reminder(
            reminder_ids=[self.reminder_id], completed=True, is_bulk_mutation=False
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["message"], "1 reminder completed successfully")
        reminder = result["reminders"][0]
        self.assertTrue(reminder["completed"])

    def test_modify_reminder_mark_deleted(self):
        """Test marking reminder as deleted."""
        result = generic_reminders.modify_reminder(
            reminder_ids=[self.reminder_id], deleted=True, is_bulk_mutation=False
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["message"], "1 reminder deleted successfully")
        reminder = result["reminders"][0]
        self.assertTrue(reminder["deleted"])

    def test_modify_reminder_by_query(self):
        """Test modifying reminders using retrieval query."""
        result = generic_reminders.modify_reminder(
            retrieval_query={"query": "Test"},
            title="Modified by Query",
            is_bulk_mutation=True,
        )

        self.assertIsInstance(result, dict)
        self.assertIn("reminder", result["message"])
        self.assertIn("modified successfully", result["message"])

    def test_modify_reminder_not_found(self):
        """Test modifying non-existent reminder."""
        self.assert_error_behavior(
            generic_reminders.modify_reminder,
            ReminderNotFoundError,
            "No matching reminders found",
            reminder_ids=["non_existent_id"],
            is_bulk_mutation=False,
        )

    def test_modify_reminder_invalid_id_type(self):
        """Test modifying reminder with invalid ID type."""
        self.assert_error_behavior(
            generic_reminders.modify_reminder,
            ValidationError,
            "Input validation failed: All reminder_ids must be strings",
            reminder_ids=[123],
            is_bulk_mutation=False,
        )

    def test_modify_reminder_empty_id_list(self):
        """Test modifying reminder with empty ID list."""
        self.assert_error_behavior(
            generic_reminders.modify_reminder,
            ValidationError,
            "Input validation failed: reminder_ids cannot be empty",
            reminder_ids=[],
            is_bulk_mutation=False,
        )

    def test_modify_reminder_both_id_and_query(self):
        """Test providing both reminder_ids and retrieval_query."""
        self.assert_error_behavior(
            generic_reminders.modify_reminder,
            ValidationError,
            "Input validation failed: Provide either reminder_ids or retrieval_query, not both",
            reminder_ids=[self.reminder_id],
            retrieval_query={"query": "test"},
            is_bulk_mutation=False,
        )

    def test_modify_reminder_past_time(self):
        """Test modifying reminder to past time."""
        self.assert_error_behavior(
            generic_reminders.modify_reminder,
            InvalidTimeError,
            "Cannot modify reminders to past dates and times",
            reminder_ids=[self.reminder_id],
            start_date="2020-01-01",
            time_of_day="10:00:00",
            am_pm_or_unknown="AM",
            is_bulk_mutation=False,
        )

    def test_modify_reminder_boring_title(self):
        """Test modifying reminder with boring title."""
        self.assert_error_behavior(
            generic_reminders.modify_reminder,
            ValidationError,
            "Your title is too generic or only contains date/time information. Please enter something more specific.",
            reminder_ids=[self.reminder_id],
            title="reminder",
            is_bulk_mutation=False,
        )

    def test_modify_reminder_invalid_date_format(self):
        """Test modifying reminder with invalid date format."""
        self.assert_error_behavior(
            generic_reminders.modify_reminder,
            ValidationError,
            "Input validation failed: start_date must be in YYYY-MM-DD format",
            reminder_ids=[self.reminder_id],
            start_date="2025/12/25",
            is_bulk_mutation=False,
        )

    def test_modify_reminder_invalid_time_format(self):
        """Test modifying reminder with invalid time format."""
        self.assert_error_behavior(
            generic_reminders.modify_reminder,
            ValidationError,
            "Input validation failed: time_of_day must be in hh:mm:ss format",
            reminder_ids=[self.reminder_id],
            time_of_day="10:30 AM",
            is_bulk_mutation=False,
        )

    def test_modify_reminder_invalid_query_type(self):
        """Test modifying reminder with invalid query type."""
        self.assert_error_behavior(
            generic_reminders.modify_reminder,
            ValidationError,
            "Input validation failed: retrieval_query must be a dict",
            retrieval_query="invalid_query",
            is_bulk_mutation=False,
        )

    def test_modify_reminder_update_schedule(self):
        """Test updating reminder schedule."""
        result = generic_reminders.modify_reminder(
            reminder_ids=[self.reminder_id],
            start_date="2025-12-30",
            time_of_day="15:00:00",
            am_pm_or_unknown="PM",
            repeat_every_n=1,
            repeat_interval_unit="WEEK",
            is_bulk_mutation=False,
        )

        self.assertIsInstance(result, dict)
        reminder = result["reminders"][0]
        self.assertEqual(reminder["start_date"], "2025-12-30")
        self.assertEqual(reminder["time_of_day"], "15:00:00")
        self.assertEqual(reminder["am_pm_or_unknown"], "PM")
        self.assertEqual(reminder["repeat_every_n"], 1)
        self.assertEqual(reminder["repeat_interval_unit"], "WEEK")

    def test_modify_reminder_bulk_operation(self):
        """Test bulk modification operation."""
        # Create additional reminders
        generic_reminders.create_reminder(
            title="Another Test Reminder", start_date="2025-12-26"
        )

        result = generic_reminders.modify_reminder(
            retrieval_query={"query": "Test"}, completed=True, is_bulk_mutation=True
        )

        self.assertIsInstance(result, dict)
        self.assertIn("reminders", result["message"])
        self.assertIn("completed successfully", result["message"])

    def test_modify_reminder_with_occurrence_count(self):
        """Test modifying reminder with occurrence count."""
        result = generic_reminders.modify_reminder(
            reminder_ids=[self.reminder_id],
            repeat_every_n=2,
            repeat_interval_unit="DAY",
            occurrence_count=5,
            is_bulk_mutation=False,
        )

        self.assertIsInstance(result, dict)
        reminder = result["reminders"][0]
        self.assertEqual(reminder["repeat_every_n"], 2)
        self.assertEqual(reminder["repeat_interval_unit"], "DAY")
        self.assertEqual(reminder["occurrence_count"], 5)

    def test_modify_reminder_past_date_without_time(self):
        """Test modifying reminder for past date without time."""
        self.assert_error_behavior(
            generic_reminders.modify_reminder,
            InvalidTimeError,
            "Cannot modify reminders to past dates and times",
            reminder_ids=[self.reminder_id],
            start_date="2000-01-01",
            is_bulk_mutation=False,
        )

    def test_modify_reminder_am_pm_mismatch(self):
        """Test AM/PM mismatch in time conversion during modification."""
        self.assert_error_behavior(
            generic_reminders.modify_reminder,
            ValidationError,
            "Invalid date/time format: AM/PM mismatch: '13:00:00' is > 12:00 but flagged AM",
            reminder_ids=[self.reminder_id],
            start_date="2025-12-25",
            time_of_day="13:00:00",
            am_pm_or_unknown="AM",
            is_bulk_mutation=False,
        )

    def test_modify_reminder_no_search_method(self):
        """Test that modify_reminder requires at least one of reminder_ids or retrieval_query."""
        self.assert_error_behavior(
            generic_reminders.modify_reminder,
            ValidationError,
            "Input validation failed: Must provide either reminder_ids or retrieval_query",
            # Neither reminder_ids nor retrieval_query provided
            title="New Title",
            is_bulk_mutation=False,
        )

    def test_modify_reminder_both_search_methods(self):
        """Test that modify_reminder rejects both reminder_ids and retrieval_query."""
        self.assert_error_behavior(
            generic_reminders.modify_reminder,
            ValidationError,
            "Input validation failed: Provide either reminder_ids or retrieval_query, not both",
            reminder_ids=[self.reminder_id],
            retrieval_query={"query": "test"},
            title="New Title",
            is_bulk_mutation=False,
        )

    # Comprehensive validation tests for case-insensitive inputs in modify_reminder
    def test_modify_repeat_interval_unit_case_insensitive(self):
        """Test that repeat_interval_unit accepts case-insensitive input in modify_reminder."""
        # Test lowercase
        result = generic_reminders.modify_reminder(
            reminder_ids=[self.reminder_id],
            repeat_every_n=2,
            repeat_interval_unit="minute"
        )
        self.assertEqual(result["reminders"][0]["repeat_interval_unit"], "minute")

        # Test mixed case
        result = generic_reminders.modify_reminder(
            reminder_ids=[self.reminder_id],
            repeat_every_n=1, 
            repeat_interval_unit="Day"
        )
        self.assertEqual(result["reminders"][0]["repeat_interval_unit"], "Day")

        # Test all valid units in different cases
        test_cases = [
            ("minute", "minute"),
            ("HOUR", "HOUR"),
            ("dAy", "dAy"),
            ("Week", "Week"),
            ("MONTH", "MONTH"),
            ("year", "year")
        ]
        
        for input_unit, expected_unit in test_cases:
            result = generic_reminders.modify_reminder(
                reminder_ids=[self.reminder_id],
                repeat_every_n=1,
                repeat_interval_unit=input_unit
            )
            self.assertEqual(result["reminders"][0]["repeat_interval_unit"], expected_unit)

    def test_modify_days_of_week_case_insensitive(self):
        """Test that days_of_week accepts case-insensitive input in modify_reminder."""
        # Test lowercase
        result = generic_reminders.modify_reminder(
            reminder_ids=[self.reminder_id],
            days_of_week=["monday", "tuesday"]
        )
        self.assertEqual(result["reminders"][0]["days_of_week"], ["monday", "tuesday"])

        # Test mixed case
        result = generic_reminders.modify_reminder(
            reminder_ids=[self.reminder_id],
            days_of_week=["Friday", "sAtUrDay"]
        )
        self.assertEqual(result["reminders"][0]["days_of_week"], ["Friday", "sAtUrDay"])

        # Test all days in different cases
        input_days = ["sunday", "MONDAY", "tuEsDay", "Wednesday", "thurSDAY", "friday", "SATURDAY"]
        expected_days = ["sunday", "MONDAY", "tuEsDay", "Wednesday", "thurSDAY", "friday", "SATURDAY"]
        
        result = generic_reminders.modify_reminder(
            reminder_ids=[self.reminder_id],
            days_of_week=input_days
        )
        self.assertEqual(result["reminders"][0]["days_of_week"], expected_days)

    def test_modify_weeks_of_month_case_insensitive_and_numeric(self):
        """Test that weeks_of_month accepts case-insensitive and numeric input in modify_reminder."""
        # Test lowercase
        result = generic_reminders.modify_reminder(
            reminder_ids=[self.reminder_id],
            weeks_of_month=["first", "second"]
        )
        self.assertEqual(result["reminders"][0]["weeks_of_month"], ["first", "second"])

        # Test mixed case
        result = generic_reminders.modify_reminder(
            reminder_ids=[self.reminder_id],
            weeks_of_month=["Last", "fiRst"]
        )
        self.assertEqual(result["reminders"][0]["weeks_of_month"], ["Last", "fiRst"])

        # Test numeric strings
        result = generic_reminders.modify_reminder(
            reminder_ids=[self.reminder_id],
            weeks_of_month=["1", "2", "3", "4", "5"]
        )
        self.assertEqual(result["reminders"][0]["weeks_of_month"], ["1", "2", "3", "4", "5"])

        # Test mixed numeric and word forms
        result = generic_reminders.modify_reminder(
            reminder_ids=[self.reminder_id],
            weeks_of_month=["1", "SECOND", "3", "fourth", "5"]
        )
        self.assertEqual(result["reminders"][0]["weeks_of_month"], ["1", "SECOND", "3", "fourth", "5"])

    def test_modify_days_of_month_case_insensitive_day_format(self):
        """Test that days_of_month accepts case-insensitive DAY_X format in modify_reminder."""
        # Test standard uppercase format
        result = generic_reminders.modify_reminder(
            reminder_ids=[self.reminder_id],
            days_of_month=["DAY_1", "DAY_15", "DAY_31"]
        )
        self.assertEqual(result["reminders"][0]["days_of_month"], ["DAY_1", "DAY_15", "DAY_31"])

        # Test lowercase DAY_X format
        result = generic_reminders.modify_reminder(
            reminder_ids=[self.reminder_id],
            days_of_month=["day_5", "day_10"]
        )
        self.assertEqual(result["reminders"][0]["days_of_month"], ["day_5", "day_10"])

        # Test mixed case DAY_X format
        result = generic_reminders.modify_reminder(
            reminder_ids=[self.reminder_id],
            days_of_month=["Day_3", "dAy_20", "DaY_25"]
        )
        self.assertEqual(result["reminders"][0]["days_of_month"], ["Day_3", "dAy_20", "DaY_25"])

        # Test numeric strings
        result = generic_reminders.modify_reminder(
            reminder_ids=[self.reminder_id],
            days_of_month=["1", "15", "31"]
        )
        self.assertEqual(result["reminders"][0]["days_of_month"], ["1", "15", "31"])

        # Test LAST in different cases
        result = generic_reminders.modify_reminder(
            reminder_ids=[self.reminder_id],
            days_of_month=["last", "LAST", "Last"]
        )
        self.assertEqual(result["reminders"][0]["days_of_month"], ["last", "LAST", "Last"])

        # Test mixed formats
        result = generic_reminders.modify_reminder(
            reminder_ids=[self.reminder_id],
            days_of_month=["1", "DAY_5", "day_10", "Day_15", "LAST"]
        )
        self.assertEqual(result["reminders"][0]["days_of_month"], ["1", "DAY_5", "day_10", "Day_15", "LAST"])

    # Validation error tests for modify_reminder
    def test_modify_invalid_repeat_unit(self):
        """Test error handling for invalid repeat_interval_unit in modify_reminder."""
        with self.assertRaises(ValidationError) as context:
            generic_reminders.modify_reminder(
                reminder_ids=[self.reminder_id],
                repeat_every_n=1,
                repeat_interval_unit="invalid_unit"
            )
        
        error_message = str(context.exception)
        self.assertIn("repeat_interval_unit", error_message)
        self.assertIn("must be one of", error_message)
        self.assertIn("MINUTE", error_message)

    def test_modify_invalid_days_of_week(self):
        """Test error handling for invalid days_of_week in modify_reminder."""
        with self.assertRaises(ValidationError) as context:
            generic_reminders.modify_reminder(
                reminder_ids=[self.reminder_id],
                days_of_week=["invalid_day"]
            )
        
        error_message = str(context.exception)
        self.assertIn("Invalid day of week", error_message)
        self.assertIn("invalid_day", error_message)

    def test_modify_invalid_weeks_of_month(self):
        """Test error handling for invalid weeks_of_month in modify_reminder."""
        with self.assertRaises(ValidationError) as context:
            generic_reminders.modify_reminder(
                reminder_ids=[self.reminder_id],
                weeks_of_month=["invalid_week"]
            )
        
        error_message = str(context.exception)
        self.assertIn("Invalid week of month", error_message)
        self.assertIn("invalid_week", error_message)

        # Test invalid numeric
        with self.assertRaises(ValidationError) as context:
            generic_reminders.modify_reminder(
                reminder_ids=[self.reminder_id],
                weeks_of_month=["6"]
            )
        
        error_message = str(context.exception)
        self.assertIn("Invalid week of month", error_message)
        self.assertIn("6", error_message)

    def test_modify_invalid_days_of_month(self):
        """Test error handling for invalid days_of_month in modify_reminder."""
        # Test invalid format
        with self.assertRaises(ValidationError) as context:
            generic_reminders.modify_reminder(
                reminder_ids=[self.reminder_id],
                days_of_month=["invalid_format"]
            )
        
        error_message = str(context.exception)
        self.assertIn("Invalid day of month", error_message)
        self.assertIn("invalid_format", error_message)

        # Test invalid day number in DAY_X format
        with self.assertRaises(ValidationError) as context:
            generic_reminders.modify_reminder(
                reminder_ids=[self.reminder_id],
                days_of_month=["DAY_32"]
            )
        
        error_message = str(context.exception)
        self.assertIn("Invalid day of month", error_message)
        self.assertIn("DAY_32", error_message)

        # Test invalid numeric
        with self.assertRaises(ValidationError) as context:
            generic_reminders.modify_reminder(
                reminder_ids=[self.reminder_id],
                days_of_month=["32"]
            )
        
        error_message = str(context.exception)
        self.assertIn("Invalid day of month", error_message)
        self.assertIn("32", error_message)

        # Test invalid case-insensitive format
        with self.assertRaises(ValidationError) as context:
            generic_reminders.modify_reminder(
                reminder_ids=[self.reminder_id],
                days_of_month=["day_32"]
            )
        
        error_message = str(context.exception)
        self.assertIn("Invalid day of month", error_message)
        self.assertIn("day_32", error_message)

    def test_modify_validation_edge_cases(self):
        """Test edge cases for validation in modify_reminder."""
        # Test empty lists (should be allowed)
        result = generic_reminders.modify_reminder(
            reminder_ids=[self.reminder_id],
            days_of_week=[],
            weeks_of_month=[],
            days_of_month=[]
        )
        self.assertEqual(result["reminders"][0]["days_of_week"], [])
        self.assertEqual(result["reminders"][0]["weeks_of_month"], [])
        self.assertEqual(result["reminders"][0]["days_of_month"], [])

        # Test single values
        result = generic_reminders.modify_reminder(
            reminder_ids=[self.reminder_id],
            days_of_week=["monday"],
            weeks_of_month=["1"],
            days_of_month=["day_1"]
        )
        self.assertEqual(result["reminders"][0]["days_of_week"], ["monday"])
        self.assertEqual(result["reminders"][0]["weeks_of_month"], ["1"])
        self.assertEqual(result["reminders"][0]["days_of_month"], ["day_1"])

    def test_modify_with_retrieval_query_validation(self):
        """Test validation works with retrieval_query search method."""
        # Test case-insensitive validation with retrieval_query
        result = generic_reminders.modify_reminder(
            retrieval_query={"query": "test"},
            days_of_month=["day_5", "Day_10"],
            days_of_week=["monday", "TUESDAY"],
            weeks_of_month=["1", "SECOND"],
            repeat_interval_unit="minute",
            repeat_every_n=1
        )
        
        # Should normalize all case-insensitive inputs
        for reminder in result["reminders"]:
            self.assertEqual(reminder["days_of_month"], ["day_5", "Day_10"])
            self.assertEqual(reminder["days_of_week"], ["monday", "TUESDAY"])
            self.assertEqual(reminder["weeks_of_month"], ["1", "SECOND"])
            self.assertEqual(reminder["repeat_interval_unit"], "minute")


if __name__ == "__main__":
    unittest.main()
