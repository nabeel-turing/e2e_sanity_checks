"""
Test file for list_events functionality with recurring event expansion.
"""

from datetime import datetime, timedelta
from ..EventsResource import create_event, list_events
from ..SimulationEngine.custom_errors import InvalidInputError
from common_utils.base_case import BaseTestCaseWithErrorHandler
from ..SimulationEngine.db import DB


class TestListEventsRecurrence(BaseTestCaseWithErrorHandler):
    """Test cases for list_events with recurring event expansion."""
    
    def setup_method(self, method):
        """Set up test data before each test."""
        # Clear existing events

        DB["events"] = {}
        
        # Create some test events
        # 1. Simple non-recurring event
        self.simple_event = create_event("primary", {
            "summary": "One-time Meeting",
            "start": {"dateTime": "2024-01-15T10:00:00Z"},
            "end": {"dateTime": "2024-01-15T11:00:00Z"}
        })
        
        # 2. Daily recurring event for 5 occurrences
        self.daily_event = create_event("primary", {
            "summary": "Daily Standup",
            "start": {"dateTime": "2024-01-15T09:00:00Z"},
            "end": {"dateTime": "2024-01-15T09:30:00Z"},
            "recurrence": ["RRULE:FREQ=DAILY;COUNT=5"]
        })
        
        # 3. Weekly recurring event
        self.weekly_event = create_event("primary", {
            "summary": "Weekly Review",
            "start": {"dateTime": "2024-01-15T14:00:00Z"},
            "end": {"dateTime": "2024-01-15T15:00:00Z"},
            "recurrence": ["RRULE:FREQ=WEEKLY;BYDAY=MO"]
        })
    
    def test_list_events_without_expansion(self):
        """Test listing events without expanding recurring events."""
        result = list_events("primary")
        
        self.assertEqual(len(result["items"]), 3)
        # Should return base events only
        summaries = [event["summary"] for event in result["items"]]
        self.assertIn("One-time Meeting", summaries)
        self.assertIn("Daily Standup", summaries)
        self.assertIn("Weekly Review", summaries)
        
        # Check that recurring events have recurrence field
        for event in result["items"]:
            if event["summary"] in ["Daily Standup", "Weekly Review"]:
                self.assertIn("recurrence", event)
                self.assertIsInstance(event["recurrence"], list)
    
    def test_list_events_with_expansion(self):
        """Test listing events with recurring events expanded."""
        result = list_events("primary", singleEvents=True)
        
        # Should have more than 3 events due to expansion
        self.assertGreater(len(result["items"]), 3)
        
        # Check that expanded events have instance-specific fields
        expanded_events = [e for e in result["items"] if "recurringEventId" in e]
        self.assertGreater(len(expanded_events), 0)
        
        for event in expanded_events:
            self.assertIn("recurringEventId", event)
            self.assertIn("originalStartTime", event)
            self.assertNotIn("recurrence", event)  # Instances shouldn't have recurrence field
    
    def test_list_events_with_time_range(self):
        """Test listing events with time range filtering."""
        # List events for a specific week
        result = list_events(
            "primary", 
            timeMin="2024-01-15T00:00:00Z",
            timeMax="2024-01-21T23:59:59Z",
            singleEvents=True
        )
        
        # Should include instances within the time range
        self.assertGreater(len(result["items"]), 0)
        
        for event in result["items"]:
            start_time = datetime.fromisoformat(event["start"]["dateTime"].replace("Z", "+00:00"))
            self.assertGreaterEqual(start_time, datetime.fromisoformat("2024-01-15T00:00:00+00:00"))
            self.assertLessEqual(start_time, datetime.fromisoformat("2024-01-21T23:59:59+00:00"))
    
    def test_list_events_with_query(self):
        """Test listing events with query filtering."""
        result = list_events("primary", q="Standup", singleEvents=True)
        
        # Should only return events containing "Standup"
        self.assertGreater(len(result["items"]), 0)
        
        for event in result["items"]:
            self.assertIn("Standup", event["summary"])
    
    def test_list_events_with_ordering(self):
        """Test listing events with ordering."""
        result = list_events("primary", singleEvents=True, orderBy="startTime")
        
        # Events should be sorted by start time
        start_times = []
        for event in result["items"]:
            start_time = datetime.fromisoformat(event["start"]["dateTime"].replace("Z", "+00:00"))
            start_times.append(start_time)
        
        # Check if sorted
        self.assertEqual(start_times, sorted(start_times))
    
    def test_list_events_max_results(self):
        """Test that maxResults limits the number of returned events."""
        result = list_events("primary", singleEvents=True, maxResults=5)
        
        self.assertLessEqual(len(result["items"]), 5)
    
    def test_list_events_different_calendar(self):
        """Test listing events from a different calendar."""
        # Create event in a different calendar
        create_event("work", {
            "summary": "Work Meeting",
            "start": {"dateTime": "2024-01-15T10:00:00Z"},
            "end": {"dateTime": "2024-01-15T11:00:00Z"}
        })
        
        # List events from work calendar
        result = list_events("work")
        
        self.assertEqual(len(result["items"]), 1)
        self.assertEqual(result["items"][0]["summary"], "Work Meeting")
    
    def test_list_events_invalid_parameters(self):
        """Test that invalid parameters raise appropriate errors."""
        # Test invalid singleEvents type
        self.assert_error_behavior(
            list_events,
            TypeError,
            "singleEvents must be a boolean.",
            "primary",
            singleEvents="invalid"
        )
        
        # Test invalid orderBy value
        self.assert_error_behavior(
            list_events,
            InvalidInputError,
            "orderBy must be one of: startTime, updated",
            "primary",
            orderBy="invalid"
        )
        
        # Test invalid maxResults
        self.assert_error_behavior(
            list_events,
            InvalidInputError,
            "maxResults must be a positive integer.",
            "primary",
            maxResults=0
        )
        
        # Test invalid timeMin format
        self.assert_error_behavior(
            list_events,
            InvalidInputError,
            "Invalid timeMin format: time data 'invalid' does not match format '%Y-%m-%dT%H:%M:%SZ'. Must be in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ).",
            "primary",
            timeMin="invalid"
        )
    
    def test_recurring_event_instances_structure(self):
        """Test that expanded recurring event instances have correct structure."""
        result = list_events("primary", singleEvents=True)
        
        # Find an expanded instance
        instances = [e for e in result["items"] if "recurringEventId" in e]
        self.assertGreater(len(instances), 0)
        
        instance = instances[0]
        
        # Check required fields
        self.assertIn("id", instance)
        self.assertIn("summary", instance)
        self.assertIn("start", instance)
        self.assertIn("end", instance)
        self.assertIn("recurringEventId", instance)
        self.assertIn("originalStartTime", instance)
        
        # Check that start/end times are valid ISO format
        start_time = instance["start"]["dateTime"]
        end_time = instance["end"]["dateTime"]
        self.assertTrue(start_time.endswith("Z"))
        self.assertTrue(end_time.endswith("Z"))
        
        # Check that originalStartTime is valid
        original_start = instance["originalStartTime"]["dateTime"]
        self.assertTrue(original_start.endswith("Z"))
    
    def test_daily_recurrence_expansion(self):
        """Test specific daily recurrence expansion."""
        result = list_events(
            "primary", 
            singleEvents=True,
            timeMin="2024-01-15T00:00:00Z",
            timeMax="2024-01-20T23:59:59Z"
        )
        
        # Should have 5 instances of daily standup (Jan 15-19)
        daily_instances = [e for e in result["items"] if e["summary"] == "Daily Standup"]
        self.assertEqual(len(daily_instances), 5)
        
        # Check that instances are on consecutive days
        start_times = []
        for instance in daily_instances:
            start_time = datetime.fromisoformat(instance["start"]["dateTime"].replace("Z", "+00:00"))
            start_times.append(start_time)
        
        # Sort and check they're consecutive
        start_times.sort()
        for i in range(1, len(start_times)):
            time_diff = start_times[i] - start_times[i-1]
            self.assertEqual(time_diff, timedelta(days=1))
    
    def test_weekly_recurrence_expansion(self):
        """Test specific weekly recurrence expansion."""
        result = list_events(
            "primary", 
            singleEvents=True,
            timeMin="2024-01-15T00:00:00Z",
            timeMax="2024-02-15T23:59:59Z"
        )
        
        # Should have multiple instances of weekly review
        weekly_instances = [e for e in result["items"] if e["summary"] == "Weekly Review"]
        self.assertGreater(len(weekly_instances), 1)
        
        # Check that instances are weekly (7 days apart)
        start_times = []
        for instance in weekly_instances:
            start_time = datetime.fromisoformat(instance["start"]["dateTime"].replace("Z", "+00:00"))
            start_times.append(start_time)
        
        # Sort and check they're weekly
        start_times.sort()
        for i in range(1, len(start_times)):
            time_diff = start_times[i] - start_times[i-1]
            self.assertEqual(time_diff, timedelta(days=7))

    def test_list_events_edge_cases_and_truncation(self):
        """Test edge cases for event filtering and maxResults truncation in list_events."""
        # Clear and set up edge case events
        DB["events"] = {}
        cal_id = "primary"
        
        # Create events with various missing or invalid fields
        # Event missing 'start'
        DB["events"][(cal_id, "no_start")] = {"id": "no_start", "summary": "No Start"}
        
        # Event with 'start' but missing 'dateTime'
        DB["events"][(cal_id, "no_start_datetime")] = {
            "id": "no_start_datetime", 
            "summary": "No Start DateTime", 
            "start": {}
        }
        
        # Event with 'start.dateTime' that is None (will cause parse_iso_datetime to return None)
        DB["events"][(cal_id, "none_start_datetime")] = {
            "id": "none_start_datetime", 
            "summary": "None Start DateTime", 
            "start": {"dateTime": None}
        }
        
        # Event missing 'end'
        DB["events"][(cal_id, "no_end")] = {
            "id": "no_end", 
            "summary": "No End", 
            "start": {"dateTime": "2024-01-15T10:00:00Z"}
        }
        
        # Event with 'end' but missing 'dateTime'
        DB["events"][(cal_id, "no_end_datetime")] = {
            "id": "no_end_datetime", 
            "summary": "No End DateTime", 
            "start": {"dateTime": "2024-01-15T10:00:00Z"}, 
            "end": {}
        }
        
        # Event with 'end.dateTime' that is None (will cause parse_iso_datetime to return None)
        DB["events"][(cal_id, "none_end_datetime")] = {
            "id": "none_end_datetime", 
            "summary": "None End DateTime", 
            "start": {"dateTime": "2024-01-15T10:00:00Z"}, 
            "end": {"dateTime": None}
        }
        
        # Valid event for control
        DB["events"][(cal_id, "valid")] = {
            "id": "valid", 
            "summary": "Valid Event", 
            "start": {"dateTime": "2024-01-15T10:00:00Z"}, 
            "end": {"dateTime": "2024-01-15T11:00:00Z"}
        }

        # Test that when filtering by timeMin/timeMax, only the valid event is returned
        # The other events should be filtered out due to missing/invalid start/end times
        result = list_events(cal_id, timeMin="2024-01-15T00:00:00Z", timeMax="2024-01-15T23:59:59Z")
        self.assertEqual(len(result["items"]), 1)
        self.assertEqual(result["items"][0]["id"], "valid")

        # Test that when not filtering by time, all events are returned
        result_all = list_events(cal_id)
        self.assertEqual(len(result_all["items"]), 7)
        ids = {e["id"] for e in result_all["items"]}
        self.assertIn("no_start", ids)
        self.assertIn("no_start_datetime", ids)
        self.assertIn("none_start_datetime", ids)
        self.assertIn("no_end", ids)
        self.assertIn("no_end_datetime", ids)
        self.assertIn("none_end_datetime", ids)
        self.assertIn("valid", ids)

        # Test maxResults truncation
        result_trunc = list_events(cal_id, maxResults=3)
        self.assertEqual(len(result_trunc["items"]), 3)


if __name__ == "__main__":
    # Run a simple test
    print("Testing list_events with recurrence expansion...")
    
    # Create test events
    create_event("primary", {
        "summary": "Test Daily Event",
        "start": {"dateTime": "2024-01-15T10:00:00Z"},
        "end": {"dateTime": "2024-01-15T11:00:00Z"},
        "recurrence": ["RRULE:FREQ=DAILY;COUNT=3"]
    })
    
    # Test without expansion
    result1 = list_events("primary")
    print(f"Without expansion: {len(result1['items'])} events")
    
    # Test with expansion
    result2 = list_events("primary", singleEvents=True)
    print(f"With expansion: {len(result2['items'])} events")
