import urllib.parse

from salesforce import Event, Task, Query

from common_utils.base_case import BaseTestCaseWithErrorHandler
from salesforce.SimulationEngine.db import DB

from pydantic import ValidationError

from salesforce import query_tasks
from salesforce import search_events
from salesforce import create_event
from salesforce import query_events
from salesforce import create_task


###############################################################################
# Unit Tests
###############################################################################
class TestSalesforceSimulationAPI(BaseTestCaseWithErrorHandler):
    def setUp(self):
        """Resets the database before each test."""
        # Re-initialize the DB with sample data
        from salesforce.SimulationEngine.db import DB

        DB.clear()
        DB.update({"Event": {}, "Task": {}})

    def test_event_create(self):
        """Test creating an event"""
        event = Event.create(Subject="Sample Event")
        self.assertIsInstance(event, dict)
        self.assertIn("Id", event)
        self.assertIn("CreatedDate", event)
        self.assertEqual(event["Subject"], "Sample Event")

    def test_event_update(self):
        """Test updating an event"""
        event = Event.create(Subject="Old Event")
        event_id = event["Id"]
        updated_event = Event.update(event_id, Subject="Updated Event")
        self.assertEqual(updated_event["Subject"], "Updated Event")

    def test_event_delete(self):
        """Test deleting an event"""
        event = Event.create(Subject="Sample Event")
        event_id = event["Id"]
        result = Event.delete(event_id)
        self.assertEqual(result, {})
        self.assertNotIn(event_id, Event.DB["Event"])

    def test_event_retrieve(self):
        """Test retrieving an event"""
        event = Event.create(Subject="Sample Event")
        event_id = event["Id"]
        retrieved_event = Event.retrieve(event_id)
        self.assertEqual(retrieved_event["Id"], event_id)

    def test_event_query(self):
        """Test querying events"""
        Event.create(Subject="Event One")
        Event.create(Subject="Event Two")
        results = Event.query({"Subject": "Event One"})
        self.assertEqual(len(results["results"]), 1)
        self.assertEqual(results["results"][0]["Subject"], "Event One")

    def test_event_search(self):
        """Test searching events"""
        Event.create(Subject="Search Event")
        results = Event.search("Search")
        self.assertGreater(len(results["results"]), 0)

    def test_event_upsert_create(self):
        """Test upsert create functionality"""
        event = Event.upsert(Subject="Upsert Event")
        self.assertIn("Id", event)
        self.assertEqual(event["Subject"], "Upsert Event")

    def test_event_upsert_update(self):
        """Test upsert update functionality"""
        event = Event.create(Subject="Upsert Event")
        event_id = event["Id"]
        updated_event = Event.upsert(Id=event_id, Subject="Updated Upsert Event")
        self.assertEqual(updated_event["Subject"], "Updated Upsert Event")

    def test_task_create(self):
        """Test creating a task"""
        task = Task.create(Name="Sample Task", Priority="High", Status="Not Started")
        self.assertIsInstance(task, dict)
        self.assertIn("Id", task)
        self.assertEqual(task["Priority"], "High")

    def test_task_update(self):
        """Test updating a task"""
        task = Task.create(Name="Old Task", Priority="Low", Status="Not Started")
        task_id = task["Id"]
        updated_task = Task.update(task_id, Status="Completed")
        self.assertEqual(updated_task["Status"], "Completed")

    def test_task_delete(self):
        """Test deleting a task"""
        task = Task.create(Name="Sample Task", Priority="High", Status="Not Started")
        task_id = task["Id"]
        result = Task.delete(task_id)
        self.assertEqual(result, {})
        self.assertNotIn(task_id, Task.DB["Task"])

    def test_task_retrieve(self):
        """Test retrieving a task"""
        task = Task.create(Name="Sample Task", Priority="High", Status="Not Started")
        task_id = task["Id"]
        retrieved_task = Task.retrieve(task_id)
        self.assertEqual(retrieved_task["Id"], task_id)

    def test_task_query(self):
        """Test querying tasks"""
        Task.create(Name="Task One", Priority="High", Status="Not Started")
        Task.create(Name="Task Two", Priority="Low", Status="Completed")
        results = Task.query({"Status": "Completed"})
        self.assertEqual(len(results["results"]), 1)
        self.assertEqual(results["results"][0]["Status"], "Completed")

    def test_task_upsert_update(self):
        """Test upsert update functionality"""
        task = Task.create(Name="Upsert Task", Priority="Medium", Status="Not Started")
        task_id = task["Id"]
        updated_task = Task.upsert(
            Id=task_id, Name="Updated Upsert Task", Status="Completed"
        )
        self.assertEqual(updated_task["Status"], "Completed")
        self.assertEqual(updated_task["Name"], "Updated Upsert Task")

    def test_query_get_select_from(self):
        """Test Query.get with basic SELECT and FROM. All selected fields should be present."""
        self.setUp()
        Event.create(
            Name="Event Alpha",
            Location="Meeting Room 1",
            Description="Alpha description",
        )
        Event.create(
            Name="Event Beta",
            Location="Conference Hall",
            Description="Beta description",
        )
        query_string = "SELECT Name, Location FROM Event"
        result = Query.get(query_string)
        self.assertNotIn("error", result, msg=result.get("error"))
        self.assertEqual(len(result["results"]), 2)

        found_alpha = False
        found_beta = False
        for r in result["results"]:
            self.assertIn("Name", r)
            self.assertIn("Location", r)  # Location should now be selected
            self.assertNotIn("Description", r)  # Description was not selected
            if r.get("Name") == "Event Alpha":
                found_alpha = True
                self.assertEqual(r.get("Location"), "Meeting Room 1")
            if r.get("Name") == "Event Beta":
                found_beta = True
                self.assertEqual(r.get("Location"), "Conference Hall")
        self.assertTrue(found_alpha, "Event Alpha not found or fields incorrect")
        self.assertTrue(found_beta, "Event Beta not found or fields incorrect")

    def test_query_get_where_equals(self):
        """Test Query.get with WHERE clause (equals)"""
        self.setUp()
        Event.create(Name="Event Gamma", Location="Office")
        Event.create(Name="Event Delta", Location="Remote")
        query_string = "SELECT Name FROM Event WHERE Location = 'Office'"
        result = Query.get(query_string)
        self.assertNotIn("error", result, msg=result.get("error"))
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["Name"], "Event Gamma")

    def test_query_get_where_greater_than(self):
        """Test Query.get with WHERE clause (greater than) using string comparison"""
        self.setUp()
        Task.create(
            Name="Task Alpha", Subject="Apple Picking", Priority="Low", Status="Open"
        )
        Task.create(
            Name="Task Bravo", Subject="Banana Bread", Priority="Medium", Status="Open"
        )
        Task.create(
            Name="Task Charlie", Subject="Cherry Pie", Priority="High", Status="Open"
        )
        query_string = "SELECT Name FROM Task WHERE Subject > 'Banana Bread'"
        result = Query.get(query_string)
        self.assertNotIn("error", result, msg=result.get("error"))
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["Name"], "Task Charlie")

    def test_query_get_where_less_than(self):
        """Test Query.get with WHERE clause (less than) using string comparison"""
        self.setUp()
        Task.create(Name="Task Dog", Subject="Date Loaf", Priority="Low", Status="Open")
        Task.create(
            Name="Task Elephant",
            Subject="Elderflower Cordial",
            Priority="Medium",
            Status="Open",
        )
        Task.create(Name="Task Fox", Subject="Fig Jam", Priority="High", Status="Open")
        query_string = "SELECT Name FROM Task WHERE Subject < 'Elderflower Cordial'"
        result = Query.get(query_string)
        self.assertNotIn("error", result, msg=result.get("error"))
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["Name"], "Task Dog")

    def test_query_get_where_and(self):
        """Test Query.get with WHERE clause (AND)"""
        self.setUp()
        Event.create(
            Name="Meeting 1", Location="Boardroom", StartDateTime="2024-01-01T10:00:00Z"
        )
        Event.create(
            Name="Meeting 2", Location="Boardroom", StartDateTime="2024-01-05T10:00:00Z"
        )
        Event.create(
            Name="Meeting 3",
            Location="Focus Room",
            StartDateTime="2024-01-01T10:00:00Z",
        )
        query_string = "SELECT Name FROM Event WHERE Location = 'Boardroom' AND StartDateTime > '2024-01-02T00:00:00Z'"
        result = Query.get(query_string)
        self.assertNotIn("error", result, msg=result.get("error"))
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["Name"], "Meeting 2")

    def test_query_get_order_by_asc(self):
        """Test Query.get with ORDER BY ASC"""
        self.setUp()
        Event.create(Name="Charlie Event")
        Event.create(Name="Alpha Event")
        Event.create(Name="Bravo Event")
        query_string = "SELECT Name FROM Event ORDER BY Name ASC"
        result = Query.get(query_string)
        self.assertNotIn("error", result, msg=result.get("error"))
        self.assertEqual(len(result["results"]), 3)
        self.assertEqual(result["results"][0]["Name"], "Alpha Event")
        self.assertEqual(result["results"][1]["Name"], "Bravo Event")
        self.assertEqual(result["results"][2]["Name"], "Charlie Event")

    def test_query_get_order_by_desc(self):
        """Test Query.get with ORDER BY DESC"""
        self.setUp()
        Event.create(Name="Charlie Event D")
        Event.create(Name="Alpha Event D")
        Event.create(Name="Bravo Event D")
        query_string = "SELECT Name FROM Event ORDER BY Name DESC"
        result = Query.get(query_string)
        self.assertNotIn("error", result, msg=result.get("error"))
        self.assertEqual(len(result["results"]), 3)
        self.assertEqual(result["results"][0]["Name"], "Charlie Event D")
        self.assertEqual(result["results"][1]["Name"], "Bravo Event D")
        self.assertEqual(result["results"][2]["Name"], "Alpha Event D")

    def test_query_get_limit(self):
        """Test Query.get with LIMIT"""
        self.setUp()
        for i in range(5):
            Event.create(Name=f"Limit Event {i}")
        query_string = "SELECT Name FROM Event ORDER BY Name ASC LIMIT 3"
        result = Query.get(query_string)
        self.assertNotIn("error", result, msg=result.get("error"))
        self.assertEqual(len(result["results"]), 3)
        self.assertEqual(result["results"][0]["Name"], "Limit Event 0")
        self.assertEqual(result["results"][1]["Name"], "Limit Event 1")
        self.assertEqual(result["results"][2]["Name"], "Limit Event 2")

    def test_query_get_offset(self):
        """Test Query.get with OFFSET"""
        self.setUp()
        for i in range(5):
            Event.create(Name=f"Offset Event {i}")
        query_string = "SELECT Name FROM Event ORDER BY Name ASC OFFSET 2"
        result = Query.get(query_string)
        self.assertNotIn("error", result, msg=result.get("error"))
        self.assertEqual(len(result["results"]), 3)
        self.assertEqual(result["results"][0]["Name"], "Offset Event 2")
        self.assertEqual(result["results"][1]["Name"], "Offset Event 3")
        self.assertEqual(result["results"][2]["Name"], "Offset Event 4")

    def test_query_get_limit_offset(self):
        """Test Query.get with LIMIT and OFFSET (OFFSET then LIMIT)."""
        self.setUp()
        for i in range(10):
            Event.create(Name=f"LimOff Event {i:02d}")
        query_string = "SELECT Name FROM Event ORDER BY Name ASC OFFSET 4 LIMIT 3"
        result = Query.get(query_string)
        self.assertNotIn("error", result, msg=result.get("error"))
        self.assertEqual(len(result["results"]), 3)
        self.assertEqual(result["results"][0]["Name"], "LimOff Event 04")
        self.assertEqual(result["results"][1]["Name"], "LimOff Event 05")
        self.assertEqual(result["results"][2]["Name"], "LimOff Event 06")

    def test_query_get_offset_limit(self):
        """Test Query.get with OFFSET and LIMIT (LIMIT then OFFSET). This should now work."""
        self.setUp()
        for i in range(10):
            Event.create(
                Name=f"OffLim Event {i:02d}"
            )  # Use a different prefix to avoid state issues
        # Query with LIMIT first, then OFFSET
        query_string = "SELECT Name FROM Event ORDER BY Name ASC LIMIT 5 OFFSET 2"
        result = Query.get(query_string)
        self.assertNotIn("error", result, msg=result.get("error"))
        # Records: 00, 01, 02, 03, 04, 05, 06, 07, 08, 09
        # After ORDER BY Name ASC: 00, 01, 02, 03, 04, 05, 06, 07, 08, 09
        # In Query.get, offset is applied first to the full sorted list:
        # results = results[offset:] -> results[2:] -> 02, 03, 04, 05, 06, 07, 08, 09 (8 records)
        # Then limit is applied to this new list:
        # results = results[:limit] -> results[:5] -> 02, 03, 04, 05, 06 (5 records)
        self.assertEqual(
            len(result["results"]),
            5,
            "Should return 5 records after applying OFFSET then LIMIT as per code logic.",
        )
        self.assertEqual(result["results"][0]["Name"], "OffLim Event 02")
        self.assertEqual(result["results"][1]["Name"], "OffLim Event 03")
        self.assertEqual(result["results"][2]["Name"], "OffLim Event 04")
        self.assertEqual(result["results"][3]["Name"], "OffLim Event 05")
        self.assertEqual(result["results"][4]["Name"], "OffLim Event 06")

    def test_query_get_non_existent_object(self):
        """Test Query.get with a non-existent object"""
        self.setUp()
        query_string = "SELECT Name FROM NonExistentObject"
        result = Query.get(query_string)
        self.assertIn("error", result)
        self.assertIn("not found in database", result["error"])

    def test_query_get_malformed_query_no_select(self):
        """Test Query.get with a malformed query (missing SELECT)"""
        self.setUp()
        query_string = "FROM Event"
        result = Query.get(query_string)
        self.assertIn("error", result)
        self.assertIn("Invalid SOQL query", result["error"])

    def test_query_get_malformed_query_no_from(self):
        """Test Query.get with a malformed query (missing FROM)"""
        self.setUp()
        query_string = "SELECT Name"
        result = Query.get(query_string)
        self.assertIn("error", result)

    def test_query_get_select_specific_fields(self):
        """Test Query.get selects only specified fields. All selected fields should be present."""
        self.setUp()
        Event.create(
            Name="Test Event Specific",
            Description="A test event description",
            Location="Office Room 101",
        )
        query_string = (
            "SELECT Name, Location FROM Event WHERE Name = 'Test Event Specific'"
        )
        result = Query.get(query_string)
        self.assertNotIn("error", result, msg=result.get("error"))
        self.assertEqual(len(result["results"]), 1)
        record = result["results"][0]
        self.assertIn("Name", record)
        self.assertEqual(record["Name"], "Test Event Specific")
        self.assertIn("Location", record)  # Location should now be selected
        self.assertEqual(record["Location"], "Office Room 101")
        self.assertNotIn("Description", record)  # Description was not selected

    def test_query_get_where_string_with_spaces(self):
        """Test Query.get with WHERE clause on string with spaces"""
        self.setUp()
        Event.create(Name="Multi Word Event Name")
        query_string = "SELECT Name FROM Event WHERE Name = 'Multi Word Event Name'"
        result = Query.get(query_string)
        self.assertNotIn("error", result, msg=result.get("error"))
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["Name"], "Multi Word Event Name")

    def test_query_get_case_insensitivity_of_keywords(self):
        """Test Query.get with case-insensitive SELECT, but other keywords must be UPPERCASE."""
        self.setUp()
        Event.create(Name="Case Test Event", Location="Active Location")
        # Query.get correctly handles lowercase "select" but not other keywords like "from", "where".
        query_string = "select Name FROM Event WHERE Location = 'Active Location'"  # FROM and WHERE are uppercase
        result = Query.get(query_string)
        self.assertNotIn("error", result, msg=result.get("error"))
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["Name"], "Case Test Event")

        # Test that lowercase from/where will fail as expected
        query_string_lc_fail = (
            "SELECT Name from Event where Location = 'Active Location'"
        )
        result_lc_fail = Query.get(query_string_lc_fail)
        self.assertIn("error", result_lc_fail)
        self.assertTrue(
            "FROM" in result_lc_fail["error"]
            or "from" in result_lc_fail["error"]
            or "index" in result_lc_fail["error"].lower()
        )

    def test_query_get_no_where_clause(self):
        """Test Query.get works without a WHERE clause"""
        self.setUp()
        Event.create(Name="Event X NoWhere")
        Event.create(Name="Event Y NoWhere")
        query_string = "SELECT Name FROM Event"
        result = Query.get(query_string)
        self.assertNotIn("error", result, msg=result.get("error"))
        self.assertEqual(len(result["results"]), 2)
        names = {r["Name"] for r in result["results"]}
        self.assertIn("Event X NoWhere", names)
        self.assertIn("Event Y NoWhere", names)

    def test_query_get_order_by_non_selected_field_demonstrates_bug(self):
        """Test Query.get ORDER BY a non-selected field.
        With fixed SELECT, if a field is not selected, it won't be in the record for sorting.
        The .get(field, "") will result in "" for all records for that sort key,
        leading to an unstable sort (often original insertion order).
        If the field *is* selected, sorting should work as expected.
        """
        self.setUp()
        Event.create(
            Name="E1OrderTest", Description="Sort Z", Location="Loc C"
        )  # Inserted first
        Event.create(
            Name="E2OrderTest", Description="Sort A", Location="Loc B"
        )  # Inserted second
        Event.create(
            Name="E3OrderTest", Description="Sort M", Location="Loc A"
        )  # Inserted third

        # Case 1: ORDER BY a field NOT in SELECT list
        query_string_not_selected_sort_key = (
            "SELECT Name, Location FROM Event ORDER BY Description ASC"
        )
        result_not_selected_sort_key = Query.get(query_string_not_selected_sort_key)
        self.assertNotIn(
            "error",
            result_not_selected_sort_key,
            msg=result_not_selected_sort_key.get("error"),
        )
        self.assertEqual(len(result_not_selected_sort_key["results"]), 3)
        # Description is not selected, so .get('Description', '') will be '' for all.
        # Sort is unstable, order might be original insertion or depend on Python's sort stability for equal keys.
        # We cannot reliably assert a specific order here other than checking if all items are present with correct Name and Location.
        names_found = [r["Name"] for r in result_not_selected_sort_key["results"]]
        self.assertIn("E1OrderTest", names_found)
        self.assertIn("E2OrderTest", names_found)
        self.assertIn("E3OrderTest", names_found)
        for r in result_not_selected_sort_key["results"]:
            self.assertIn("Name", r)
            self.assertIn("Location", r)  # Location was selected
            self.assertNotIn("Description", r)  # Description was not selected

        # Case 2: ORDER BY a field that IS in SELECT list (Description)
        query_string_selected_sort_key = (
            "SELECT Name, Description FROM Event ORDER BY Description ASC"
        )
        result_selected_sort_key = Query.get(query_string_selected_sort_key)
        self.assertNotIn(
            "error", result_selected_sort_key, msg=result_selected_sort_key.get("error")
        )
        self.assertEqual(len(result_selected_sort_key["results"]), 3)
        # Now Description is selected, so sorting should be by Description.
        self.assertEqual(
            result_selected_sort_key["results"][0]["Name"], "E2OrderTest"
        )  # Description "Sort A"
        self.assertEqual(
            result_selected_sort_key["results"][0]["Description"], "Sort A"
        )
        self.assertEqual(
            result_selected_sort_key["results"][1]["Name"], "E3OrderTest"
        )  # Description "Sort M"
        self.assertEqual(
            result_selected_sort_key["results"][1]["Description"], "Sort M"
        )
        self.assertEqual(
            result_selected_sort_key["results"][2]["Name"], "E1OrderTest"
        )  # Description "Sort Z"
        self.assertEqual(
            result_selected_sort_key["results"][2]["Description"], "Sort Z"
        )
        for r in result_selected_sort_key["results"]:
            self.assertIn("Name", r)
            self.assertIn("Description", r)  # Description was selected
            self.assertNotIn("Location", r)  # Location was not selected in this query

        # Case 3: ORDER BY a field that IS in SELECT list (Name) - simple case
        query_string_selected_name_sort = (
            "SELECT Name, Description FROM Event ORDER BY Name DESC"
        )
        result_selected_name_sort = Query.get(query_string_selected_name_sort)
        self.assertNotIn(
            "error",
            result_selected_name_sort,
            msg=result_selected_name_sort.get("error"),
        )
        self.assertEqual(len(result_selected_name_sort["results"]), 3)
        self.assertEqual(result_selected_name_sort["results"][0]["Name"], "E3OrderTest")
        self.assertEqual(result_selected_name_sort["results"][1]["Name"], "E2OrderTest")
        self.assertEqual(result_selected_name_sort["results"][2]["Name"], "E1OrderTest")

    def test_query_get_order_by_field_not_exist(self):
        """Test Query.get ORDER BY a field that does not exist in any record"""
        self.setUp()
        Event.create(Name="NoSortField Event Unique")
        query_string = "SELECT Name FROM Event ORDER BY NonExistentField ASC"
        result = Query.get(query_string)
        self.assertNotIn("error", result, msg=result.get("error"))
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["Name"], "NoSortField Event Unique")

    def test_query_get_where_ends_correctly_before_other_clauses(self):
        """Test that WHERE clause parsing stops before ORDER BY, LIMIT, OFFSET"""
        self.setUp()
        Event.create(Name="Event W1", Location="Room A", Description="Active Event")
        Event.create(Name="Event W2", Location="Room B", Description="Active Event")
        Event.create(Name="Event W3", Location="Room A", Description="Inactive Event")

        # Test 1: WHERE ... ORDER BY
        # Select Name, Location, Description to verify Description field used in WHERE
        query1 = "SELECT Name, Location, Description FROM Event WHERE Description = 'Active Event' ORDER BY Name ASC"
        result1 = Query.get(query1)
        self.assertNotIn("error", result1, msg=result1.get("error"))
        self.assertEqual(len(result1["results"]), 2)
        self.assertEqual(result1["results"][0]["Name"], "Event W1")
        self.assertEqual(result1["results"][1]["Name"], "Event W2")
        for r in result1["results"]:
            self.assertEqual(r["Description"], "Active Event")

        # Test 2: WHERE ... LIMIT
        query2 = "SELECT Name FROM Event WHERE Location = 'Room A' LIMIT 1"
        result2 = Query.get(query2)
        self.assertNotIn("error", result2, msg=result2.get("error"))
        self.assertEqual(len(result2["results"]), 1)
        # To make it deterministic for checking content:
        query2_ordered = (
            "SELECT Name FROM Event WHERE Location = 'Room A' ORDER BY Name ASC LIMIT 1"
        )
        result2_ordered = Query.get(query2_ordered)
        self.assertNotIn("error", result2_ordered, msg=result2_ordered.get("error"))
        self.assertEqual(len(result2_ordered["results"]), 1)
        self.assertEqual(result2_ordered["results"][0]["Name"], "Event W1")

        # Test 3: WHERE ... OFFSET
        # Create more data for offset
        Event.create(
            Name="Event W4", Location="Room A", Description="Another Active Event"
        )  # W1, W3, W4 are in Room A
        query3 = "SELECT Name FROM Event WHERE Location = 'Room A' ORDER BY Name ASC OFFSET 1"
        result3 = Query.get(query3)
        self.assertNotIn("error", result3, msg=result3.get("error"))
        # Sorted Room A by Name: Event W1, Event W3, Event W4
        # OFFSET 1: Event W3, Event W4
        self.assertEqual(len(result3["results"]), 2)
        self.assertEqual(result3["results"][0]["Name"], "Event W3")
        self.assertEqual(result3["results"][1]["Name"], "Event W4")

        # Test 4: WHERE ... AND ... ORDER BY ... LIMIT ... OFFSET
        Event.create(
            Name="Event W5", Location="Room B", Description="Active Event Priority"
        )  # W2 (Active Event), W5 (Active Event Priority) are Room B
        # Query to test multiple conditions and clauses
        # Changed "Description CONTAINS 'Active'" to "Description = 'Active Event Priority'" for compatibility with Query.get
        query4 = "SELECT Name FROM Event WHERE Location = 'Room B' AND Description = 'Active Event Priority' ORDER BY Name DESC OFFSET 0 LIMIT 1"
        # Records matching WHERE (Location='Room B' AND Description = 'Active Event Priority'):
        #   Event W5 (Name="Event W5", Location="Room B", Description="Active Event Priority")
        # ORDER BY Name DESC: W5 (as it's the only one matching)
        # OFFSET 0: W5
        # LIMIT 1: W5
        result4 = Query.get(query4)
        self.assertNotIn("error", result4, msg=result4.get("error"))
        self.assertEqual(len(result4["results"]), 1)
        self.assertEqual(result4["results"][0]["Name"], "Event W5")

    def test_query_get_limit_only(self):
        """Test Query.get with LIMIT clause only."""
        self.setUp()
        for i in range(5):
            Event.create(Name=f"LimitOnly Event {i}")
        query_string = "SELECT Name FROM Event ORDER BY Name ASC LIMIT 2"
        result = Query.get(query_string)
        self.assertNotIn("error", result, msg=result.get("error"))
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["Name"], "LimitOnly Event 0")
        self.assertEqual(result["results"][1]["Name"], "LimitOnly Event 1")

    def test_query_get_offset_only(self):
        """Test Query.get with OFFSET clause only."""
        self.setUp()
        for i in range(5):
            Event.create(Name=f"OffsetOnly Event {i}")
        query_string = "SELECT Name FROM Event ORDER BY Name ASC OFFSET 3"
        result = Query.get(query_string)
        self.assertNotIn("error", result, msg=result.get("error"))
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["Name"], "OffsetOnly Event 3")
        self.assertEqual(result["results"][1]["Name"], "OffsetOnly Event 4")

    def test_query_get_limit_includes_all_offsetted(self):
        """Test LIMIT is large enough to include all records after OFFSET."""
        self.setUp()
        for i in range(5):
            Event.create(Name=f"LimOffAll Event {i}")
        # Offset 2: 2, 3, 4 (3 records). Limit 5 should take all 3.
        query_string = "SELECT Name FROM Event ORDER BY Name ASC OFFSET 2 LIMIT 5"
        result = Query.get(query_string)
        self.assertNotIn("error", result, msg=result.get("error"))
        self.assertEqual(len(result["results"]), 3)
        self.assertEqual(result["results"][0]["Name"], "LimOffAll Event 2")
        self.assertEqual(result["results"][1]["Name"], "LimOffAll Event 3")
        self.assertEqual(result["results"][2]["Name"], "LimOffAll Event 4")

    def test_query_get_offset_greater_than_total(self):
        """Test OFFSET is greater than the total number of records."""
        self.setUp()
        for i in range(3):
            Event.create(Name=f"OffsetTooBig Event {i}")
        query_string = "SELECT Name FROM Event ORDER BY Name ASC OFFSET 5"
        result = Query.get(query_string)
        self.assertNotIn("error", result, msg=result.get("error"))
        self.assertEqual(len(result["results"]), 0)

    def test_query_get_limit_zero(self):
        """Test Query.get with LIMIT 0."""
        self.setUp()
        for i in range(3):
            Event.create(Name=f"LimitZero Event {i}")
        query_string = "SELECT Name FROM Event ORDER BY Name ASC LIMIT 0"
        result = Query.get(query_string)
        self.assertNotIn("error", result, msg=result.get("error"))
        self.assertEqual(len(result["results"]), 0)

    def test_query_get_limit_offset_on_empty_where_result(self):
        """Test LIMIT and OFFSET on an empty set from WHERE clause."""
        self.setUp()
        Event.create(Name="Event A", Location="Room X")
        query_string = "SELECT Name FROM Event WHERE Location = 'NonExistentRoom' ORDER BY Name ASC OFFSET 1 LIMIT 2"
        result = Query.get(query_string)
        self.assertNotIn("error", result, msg=result.get("error"))
        self.assertEqual(len(result["results"]), 0)

    def test_query_get_limit_greater_than_available_with_offset(self):
        """Test LIMIT is greater than available records after OFFSET."""
        self.setUp()
        for i in range(5):  # 0, 1, 2, 3, 4
            Event.create(Name=f"LimLargeOff Event {i}")
        # Records: 0, 1, 2, 3, 4
        # Offset 3: 3, 4 (2 records remaining)
        # Limit 5: Should take all remaining 2 records (3, 4)
        query_string = "SELECT Name FROM Event ORDER BY Name ASC OFFSET 3 LIMIT 5"
        result = Query.get(query_string)
        self.assertNotIn("error", result, msg=result.get("error"))
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["Name"], "LimLargeOff Event 3")
        self.assertEqual(result["results"][1]["Name"], "LimLargeOff Event 4")

    def test_query_with_start_date(self):
        Event.create(Name="Event A", StartDateTime="2024-01-01T00:00:00Z")
        query = {"StartDateTime": "2024-01-01T00:00:00Z"}
        result = Event.query(query)
        self.assertNotIn("error", result, msg=result.get("error"))
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["Name"], "Event A")
        self.assertEqual(result["results"][0]["StartDateTime"], "2024-01-01T00:00:00Z")
    
    def test_query_with_end_date(self):
        Event.create(Name="Event A", EndDateTime="2024-01-01T00:00:00Z")
        query = {"EndDateTime": "2024-01-01T00:00:00Z"}
        result = Event.query(query)
        self.assertNotIn("error", result, msg=result.get("error"))
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["Name"], "Event A")
        self.assertEqual(result["results"][0]["EndDateTime"], "2024-01-01T00:00:00Z")
    
    def test_query_with_start_date_and_end_date_and_name(self):
        Event.create(Name="Event A", StartDateTime="2024-01-01T00:00:00Z", EndDateTime="2024-01-01T00:00:00Z")
        query = {"StartDateTime": "2024-01-01T00:00:00Z", "EndDateTime": "2024-01-01T00:00:00Z", "Name": "Event A"}
        result = Event.query(query)
        self.assertNotIn("error", result, msg=result.get("error"))
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["Name"], "Event A")
        self.assertEqual(result["results"][0]["StartDateTime"], "2024-01-01T00:00:00Z")
        self.assertEqual(result["results"][0]["EndDateTime"], "2024-01-01T00:00:00Z")