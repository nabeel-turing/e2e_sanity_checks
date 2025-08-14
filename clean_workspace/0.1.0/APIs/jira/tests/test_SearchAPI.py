from .. import SearchApi as JiraAPI, search_issues_jql
from ..SimulationEngine.db import DB
from common_utils.base_case import BaseTestCaseWithErrorHandler
import unittest 


class TestSearchApi(BaseTestCaseWithErrorHandler):
    def setUp(self):
        """Set up test issues in the DB before each test."""
        # Clear the issues from global DB to ensure a clean slate
        DB["issues"].clear()

        # Insert some test issues
        DB["issues"]["ISSUE-1"] = {
            "id": "ISSUE-1",
            "fields": {
                "project": "DEMO",
                "summary": "Test the search function",
                "description": "This is a sample issue for testing",
                "created": "2024-01-01",
            },
        }
        DB["issues"]["ISSUE-2"] = {
            "id": "ISSUE-2",
            "fields": {
                "project": "DEMO",
                "summary": "Implement JQL search",
                "description": "Another test issue with code",
                "created": "2024-02-01",
            },
        }
        DB["issues"]["ISSUE-3"] = {
            "id": "ISSUE-3",
            "fields": {
                "project": "TEST",
                "summary": "Edge case scenarios",
                "description": "Testing is fun!",
                "created": "2024-03-01",
            },
        }

    def tearDown(self):
        """Clean up after each test."""
        DB["issues"].clear()

    def test_search_no_jql(self):
        """
        If no JQL is provided, should return all issues.
        """
        result = JiraAPI.search_issues()
        self.assertEqual(len(result["issues"]), 3)
        self.assertEqual(result["total"], 3)

    def test_search_exact_match(self):
        """
        Test the '=' operator to find issues where a given field exactly matches a value.
        """
        # Add search data to DB
        DB["issues"]["ISSUE-1"] = {
            "id": "ISSUE-1",
            "fields": {"project": "DEMO", "summary": "Test the search function"},
        }
        DB["issues"]["ISSUE-2"] = {
            "id": "ISSUE-2",
            "fields": {"project": "DEMO", "summary": "Implement JQL search"},
        }

        # Find issues where project = DEMO
        result = JiraAPI.search_issues(jql='project = "DEMO"')
        # ISSUE-1 and ISSUE-2 match (project="DEMO")
        self.assertEqual(len(result["issues"]), 2)
        self.assertEqual(result["issues"][0]["fields"]["project"], "DEMO")
        self.assertEqual(result["issues"][0]["fields"]["summary"], "Test the search function")

    def test_search_multiple_conditions_with_or(self):
        """
        Test multiple conditions joined by 'OR'.
        """
        # Add search data to DB
        DB["issues"]["ISSUE-1"] = {
            "id": "ISSUE-1",
            "fields": {"project": "DEMO", "summary": "Test the search function", "status": "Open"},
        }
        DB["issues"]["ISSUE-2"] = {
            "id": "ISSUE-2",
            "fields": {"project": "DEMO", "summary": "Implement JQL search", "status": "Open"},
        }
        DB["issues"]["ISSUE-3"] = {
            "id": "ISSUE-3",
            "fields": {"project": "TEST", "summary": "Edge case scenarios", "status": "Closed"},
        }
        result = JiraAPI.search_issues(jql='project = "DEMO" OR status = "Closed"')
        self.assertEqual(len(result["issues"]), 3)
        self.assertEqual(result["issues"][0]["id"], "ISSUE-1")
        self.assertEqual(result["issues"][1]["id"], "ISSUE-2")
        self.assertEqual(result["issues"][2]["id"], "ISSUE-3")

    def test_search_substring_match(self):
        """
        Test the '~' operator for case-insensitive substring searches.
        """
        # Search for summary ~ "implement" (ISSUE-2)
        result = JiraAPI.search_issues(jql='summary ~ "implement"')
        self.assertEqual(len(result["issues"]), 1)
        self.assertEqual(result["issues"][0]["id"], "ISSUE-2")

        # Also test a different case to verify case-insensitivity
        result = JiraAPI.search_issues(jql='summary ~ "TEST"')
        # Both ISSUE-1 has "Test" in summary, and ISSUE-3 has "Edge case scenarios" => summary doesn't have "test"?
        # Actually, ISSUE-1 summary is "Test the search function". That should match on substring "Test".
        # ISSUE-3 summary is "Edge case scenarios" => does not contain "test".
        # So we only expect 1 match: ISSUE-1
        self.assertEqual(len(result["issues"]), 1)
        self.assertEqual(result["issues"][0]["id"], "ISSUE-1")

    def test_search_multiple_conditions_with_and(self):
        """
        Test multiple conditions joined by 'AND'.
        """
        # Add search data to DB
        DB["issues"]["ISSUE-1"] = {
            "id": "ISSUE-1",
            "fields": {"project": "DEMO", "summary": "Test the search function"},
        }
        DB["issues"]["ISSUE-2"] = {
            "id": "ISSUE-2",
            "fields": {"project": "DEMO", "summary": "Implement JQL search"},
        }

        # We want project=DEMO AND summary~"JQL"
        # That should match ISSUE-2 only
        result = JiraAPI.search_issues(jql='project = "DEMO" AND summary ~ "JQL"')
        self.assertEqual(len(result["issues"]), 1)
        self.assertEqual(result["issues"][0]["id"], "ISSUE-2")

    def test_search_order_by(self):
        """
        Test that the orderBy parameter is honored.
        """
        # Add search data to DB
        DB["issues"]["ISSUE-1"] = {
            "id": "ISSUE-1",
            "fields": {
                "project": "DEMO",
                "summary": "Test the search function",
                "created": "2025-01-01",
            },
        }
        DB["issues"]["ISSUE-2"] = {
            "id": "ISSUE-2",
            "fields": {
                "project": "DEMO",
                "summary": "Implement JQL search",
                "created": "2025-01-02",
            },
        }
        DB["issues"]["ISSUE-3"] = {
            "id": "ISSUE-3",
            "fields": {
                "project": "TEST",
                "summary": "Edge case scenarios",
                "created": "2025-01-03",
            },
        }

        # Search with orderBy=created
        result = JiraAPI.search_issues(jql='project = "DEMO" ORDER BY created DESC')
        self.assertEqual(len(result["issues"]), 2)
        self.assertEqual(result["issues"][0]["id"], "ISSUE-2")
        self.assertEqual(result["issues"][1]["id"], "ISSUE-1")

    def test_search_pagination(self):
        """
        Test that pagination (startAt, maxResults) is honored.
        """
        # Add search data to DB
        DB["issues"]["ISSUE-1"] = {
            "id": "ISSUE-1",
            "fields": {"project": "DEMO", "summary": "Test the search function"},
        }
        DB["issues"]["ISSUE-2"] = {
            "id": "ISSUE-2",
            "fields": {"project": "DEMO", "summary": "Implement JQL search"},
        }
        DB["issues"]["ISSUE-3"] = {
            "id": "ISSUE-3",
            "fields": {"project": "TEST", "summary": "Edge case scenarios"},
        }

        # Return only 1 result at a time
        result = JiraAPI.search_issues(
            jql="",  # Return everything
            start_at=0,
            max_results=1,
        )
        self.assertEqual(len(result["issues"]), 1)
        self.assertEqual(result["total"], 3)
        self.assertEqual(result["startAt"], 0)
        self.assertEqual(result["maxResults"], 1)

        # Now startAt=1
        result = JiraAPI.search_issues(start_at=1, max_results=1)
        self.assertEqual(len(result["issues"]), 1)
        self.assertEqual(result["startAt"], 1)
        self.assertEqual(result["maxResults"], 1)

        # startAt=2
        result = JiraAPI.search_issues(start_at=2, max_results=1)
        self.assertEqual(len(result["issues"]), 1)
        self.assertEqual(result["startAt"], 2)

        # startAt=3 -> we expect an empty list
        result = JiraAPI.search_issues(start_at=3, max_results=1)
        self.assertEqual(len(result["issues"]), 0)
        self.assertEqual(result["startAt"], 3)

    def test_search_quoted_values(self):
        """
        Test that quoted values are correctly stripped of quotes.
        """
        # We'll explicitly pass single and double quotes
        result = JiraAPI.search_issues(jql="project = 'DEMO'")
        self.assertEqual(len(result["issues"]), 2)  # ISSUE-1 and ISSUE-2

        result = JiraAPI.search_issues(jql='summary ~ "Test the search"')
        self.assertEqual(len(result["issues"]), 1)
        self.assertEqual(result["issues"][0]["id"], "ISSUE-1")

    def test_search_unexpected_token(self):
        """
        Test that unexpected tokens in JQL are handled correctly.
        """
        # Test with an invalid operator
        with self.assertRaises(ValueError) as context:
            JiraAPI.search_issues(jql='project @ "DEMO"')
        self.assertIn("Unexpected token", str(context.exception))

        # Test with an invalid field name containing special characters
        with self.assertRaises(ValueError) as context:
            JiraAPI.search_issues(jql='project# = "DEMO"')
        self.assertIn("Unexpected token", str(context.exception))

    def test_search_logical_operators(self):
        """
        Test that logical operators (AND, OR, NOT) are handled correctly in JQL.
        """
        # Test AND operator
        result = JiraAPI.search_issues(jql='project = "DEMO" AND summary ~ "search"')
        self.assertEqual(len(result["issues"]), 2)  # ISSUE-1 and ISSUE-2

        # Test OR operator
        result = JiraAPI.search_issues(jql='project = "DEMO" OR project = "TEST"')
        self.assertEqual(len(result["issues"]), 3)  # All issues

        # Test NOT operator
        result = JiraAPI.search_issues(jql='NOT project = "TEST"')
        self.assertEqual(len(result["issues"]), 2)  # ISSUE-1 and ISSUE-2

    def test_complex_jql_search(self):
        """
        Test complex JQL search scenarios covering specific utils.py lines.
        """
        # Test basic field comparison (line 106)
        result = JiraAPI.search_issues(jql='project = "DEMO"')
        self.assertEqual(len(result["issues"]), 2)
        self.assertTrue(
            all(issue["fields"]["project"] == "DEMO" for issue in result["issues"])
        )

        # Test case-insensitive substring match (line 120)
        result = JiraAPI.search_issues(jql='summary ~ "test"')
        self.assertEqual(len(result["issues"]), 1)
        self.assertEqual(result["issues"][0]["id"], "ISSUE-1")

        # Test date comparison (line 124)
        result = JiraAPI.search_issues(jql='created < "2024-02-15"')
        self.assertEqual(len(result["issues"]), 2)

        # Test logical AND operator (line 155)
        result = JiraAPI.search_issues(
            jql='project = "DEMO" AND created < "2024-02-15"'
        )
        self.assertEqual(len(result["issues"]), 2)

        # Test logical operators (lines 164-183)
        # Test AND
        result = JiraAPI.search_issues(jql='project = "DEMO" AND summary ~ "search"')
        self.assertEqual(len(result["issues"]), 2)

        # Test OR
        result = JiraAPI.search_issues(jql='project = "DEMO" OR project = "TEST"')
        self.assertEqual(len(result["issues"]), 3)

        # Test NOT
        result = JiraAPI.search_issues(jql='NOT project = "TEST"')
        self.assertEqual(len(result["issues"]), 2)
        self.assertTrue(
            all(issue["fields"]["project"] != "TEST" for issue in result["issues"])
        )

        # Test date field handling (lines 195-197)
        result = JiraAPI.search_issues(jql='created >= "2024-02-01"')
        self.assertEqual(len(result["issues"]), 2)
        self.assertTrue(
            all(
                issue["fields"]["created"] >= "2024-02-01" for issue in result["issues"]
            )
        )

        # Test date parsing with different formats (lines 214-217)
        # ISO format
        result = JiraAPI.search_issues(jql='created = "2024-01-01"')
        self.assertEqual(len(result["issues"]), 1)
        self.assertEqual(result["issues"][0]["id"], "ISSUE-1")

    def test_date_parsing_in_search(self):
        """
        Test date parsing functionality through SearchApi with various date formats.
        """
        # Test ISO format (YYYY-MM-DD)
        result = JiraAPI.search_issues(jql='created = "2024-01-01"')
        self.assertEqual(len(result["issues"]), 1)  # Only ISSUE-1 has this exact date
        self.assertEqual(result["issues"][0]["id"], "ISSUE-1")

        # Test ISO format with time (YYYY-MM-DDTHH:mm:ss)
        result = JiraAPI.search_issues(jql='created = "2024-01-01T12:00:00"')
        self.assertEqual(
            len(result["issues"]), 0
        )  # No issues have this exact timestamp

        # Test date comparison with different formats
        result = JiraAPI.search_issues(jql='created > "2023-12-31"')
        self.assertEqual(len(result["issues"]), 3)  # All dates are in 2024

        # Test date range
        result = JiraAPI.search_issues(
            jql='created >= "2024-01-01" AND created <= "2024-03-31"'
        )
        self.assertEqual(len(result["issues"]), 3)  # All dates are within this range

        # Test with invalid date format
        result = JiraAPI.search_issues(jql='created = "invalid-date"')
        self.assertEqual(len(result["issues"]), 0)

        # Test with empty date
        result = JiraAPI.search_issues(jql='created = ""')
        self.assertEqual(len(result["issues"]), 0)

        # Test with malformed date
        result = JiraAPI.search_issues(jql='created = "2024-13-01"')  # Invalid month
        self.assertEqual(len(result["issues"]), 0)

        # Test date ordering
        result = JiraAPI.search_issues(jql='created <= "2024-02-01"')
        self.assertEqual(len(result["issues"]), 2)  # ISSUE-1 and ISSUE-2
        self.assertTrue(
            all(issue["id"] in ["ISSUE-1", "ISSUE-2"] for issue in result["issues"])
        )

    def test_jql_tokenization_and_evaluation(self):
        """
        Test JQL tokenization, parsing, and evaluation functionality.
        """
        result = JiraAPI.search_issues(jql='project = "DEMO"')
        self.assertEqual(len(result["issues"]), 2)
        self.assertTrue(
            all(issue["fields"]["project"] == "DEMO" for issue in result["issues"])
        )

        result = JiraAPI.search_issues(jql="")
        self.assertEqual(len(result["issues"]), 3)

        with self.assertRaises(ValueError):
            result = JiraAPI.search_issues(jql="   ")

        with self.assertRaises(ValueError) as context:
            JiraAPI.search_issues(jql='project @ "DEMO"')  # Invalid operator @
        self.assertIn("Unexpected token", str(context.exception))

        with self.assertRaises(ValueError) as context:
            JiraAPI.search_issues(
                jql='project# = "DEMO"'
            )  # Invalid field name with special character
        self.assertIn("Unexpected token", str(context.exception))

        with self.assertRaises(ValueError) as context:
            JiraAPI.search_issues(
                jql='project = "DEMO" AND summary ~ test"'
            )  # Missing opening quote
        self.assertIn("Unexpected token", str(context.exception))

        result = JiraAPI.search_issues(jql='summary = "Test the search function"')
        self.assertEqual(len(result["issues"]), 1)
        self.assertEqual(result["issues"][0]["id"], "ISSUE-1")

        result = JiraAPI.search_issues(
            jql='project = "DEMO" AND summary = "Test the search function"'
        )
        self.assertEqual(len(result["issues"]), 1)
        self.assertEqual(result["issues"][0]["id"], "ISSUE-1")

        result = JiraAPI.search_issues(jql='created >= "2024-01-01"')
        self.assertEqual(
            len(result["issues"]), 3
        )  # All issues created on or after 2024-01-01

        # Test with invalid date operator
        result = JiraAPI.search_issues(jql='created = "2024-01-01"')
        self.assertEqual(len(result["issues"]), 1)  # Only ISSUE-1 has exact date match

        result = JiraAPI.search_issues(jql='created > "2024-03-01"')
        self.assertEqual(len(result["issues"]), 0)  # No issues created after 2024-03-01

        result = JiraAPI.search_issues(jql='created < "2024-01-01"')
        self.assertEqual(
            len(result["issues"]), 0
        )  # No issues created before 2024-01-01

        result = JiraAPI.search_issues(
            jql='created >= "2024-01-01" AND created <= "2024-03-01"'
        )
        self.assertEqual(len(result["issues"]), 3)

        result = JiraAPI.search_issues(jql='project = "DEMO" AND summary ~ "test"')
        self.assertEqual(len(result["issues"]), 1)
        self.assertEqual(result["issues"][0]["id"], "ISSUE-1")

        result = JiraAPI.search_issues(jql='project = "DEMO" OR project = "TEST"')
        self.assertEqual(len(result["issues"]), 3)

        result = JiraAPI.search_issues(jql='NOT project = "TEST"')
        self.assertEqual(len(result["issues"]), 2)
        self.assertTrue(
            all(issue["fields"]["project"] != "TEST" for issue in result["issues"])
        )

        with self.assertRaises(ValueError):
            JiraAPI.search_issues(
                jql='project = "DEMO" AND summary ~ test" AND summary ~ "edge'
            )

        with self.assertRaises(ValueError):
            JiraAPI.search_issues(
                jql='project == "DEMO" AND summary ~ test" AND summary ~ "edge'
            )

        # Test parentheses grouping (now supported)
        result = JiraAPI.search_issues(
            jql='(project = "DEMO" AND summary ~ "test") OR (project = "TEST" AND summary ~ "edge")'
        )
        # Should find ISSUE-1 (DEMO project with "test" in summary) and ISSUE-3 (TEST project with "edge" in summary)
        self.assertEqual(len(result["issues"]), 2)
        issue_ids = [issue["id"] for issue in result["issues"]]
        self.assertIn("ISSUE-1", issue_ids)
        self.assertIn("ISSUE-3", issue_ids)

    def test_jql_parse_condition_no_operator(self):
        """Test JQL parsing when no operator is provided (line 103)."""
        # This should treat the condition as an equality check with empty string
        result = JiraAPI.search_issues(jql="summary")
        self.assertEqual(len(result["issues"]), 0)  # No issues match empty summary

    def test_evaluate_empty_null_values(self):
        """Test evaluation of EMPTY and NULL operators (line 130)."""
        # Add an issue with empty/null fields
        DB["issues"]["ISSUE-4"] = {
            "id": "ISSUE-4",
            "fields": {
                "project": "DEMO",
                "summary": "",
                "description": None,
                "created": "2024-01-01",
            },
        }

        # Test EMPTY operator
        result = JiraAPI.search_issues(jql="summary EMPTY")
        self.assertEqual(len(result["issues"]), 1)
        self.assertEqual(result["issues"][0]["id"], "ISSUE-4")

        # Test NULL operator
        result = JiraAPI.search_issues(jql="description NULL")
        self.assertEqual(len(result["issues"]), 1)
        self.assertEqual(result["issues"][0]["id"], "ISSUE-4")

    def test_string_based_operators(self):
        """Test string-based operators = and ~ (line 143)."""
        # Test exact match with = operator
        result = JiraAPI.search_issues(jql='project = "DEMO"')
        self.assertEqual(len(result["issues"]), 2)  # ISSUE-1 and ISSUE-2

        # Test substring match with ~ operator
        result = JiraAPI.search_issues(jql='summary ~ "search"')
        self.assertEqual(len(result["issues"]), 2)  # ISSUE-1 and ISSUE-2

    def test_date_operator_evaluation(self):
        """Test date operator evaluation (lines 151-152)."""
        # Test greater than
        result = JiraAPI.search_issues(jql='created > "2024-02-01"')
        self.assertEqual(len(result["issues"]), 1)  # Only ISSUE-3
        self.assertEqual(result["issues"][0]["id"], "ISSUE-3")

        # Test less than
        result = JiraAPI.search_issues(jql='created < "2024-02-01"')
        self.assertEqual(len(result["issues"]), 1)  # Only ISSUE-1
        self.assertEqual(result["issues"][0]["id"], "ISSUE-1")

        # Test invalid date format
        result = JiraAPI.search_issues(jql='created > "invalid-date"')
        self.assertEqual(len(result["issues"]), 0)

    def test_get_sort_key_non_date(self):
        """Test getting sort key for non-date fields (line 168)."""
        # Test sorting by project (non-date field)
        result = JiraAPI.search_issues(jql="ORDER BY project DESC")
        self.assertEqual(len(result["issues"]), 3)
        self.assertEqual(
            result["issues"][0]["fields"]["project"], "TEST"
        )  # TEST comes after DEMO
        self.assertEqual(result["issues"][1]["fields"]["project"], "DEMO")
        self.assertEqual(result["issues"][2]["fields"]["project"], "DEMO")

    def test_parse_issue_date_formats(self):
        """Test parsing dates with different formats (lines 177-179)."""
        # Add issues with different date formats
        DB["issues"]["ISSUE-5"] = {
            "id": "ISSUE-5",
            "fields": {
                "project": "DEMO",
                "summary": "Date format test 1",
                "created": "2024-01-01T12:00:00",  # ISO format with time
            },
        }
        DB["issues"]["ISSUE-6"] = {
            "id": "ISSUE-6",
            "fields": {
                "project": "DEMO",
                "summary": "Date format test 2",
                "created": "01.01.2024",  # DD.MM.YYYY format
            },
        }

        # Test ISO format with time using >= and < to match the whole day
        result = JiraAPI.search_issues(
            jql='created >= "2024-01-01" AND created < "2024-01-02"'
        )
        self.assertEqual(len(result["issues"]), 3)  # ISSUE-1, ISSUE-5, and ISSUE-6

        # Test DD.MM.YYYY format using >= and < to match the whole day
        result = JiraAPI.search_issues(
            jql='created >= "01.01.2024" AND created < "02.01.2024"'
        )
        self.assertEqual(len(result["issues"]), 3)  # ISSUE-1, ISSUE-5, and ISSUE-6

        # Test invalid date format
        result = JiraAPI.search_issues(jql='created = "invalid-date"')
        self.assertEqual(len(result["issues"]), 0)

    def test_invalid_jql_type(self):
        """Test that jql with an invalid type (e.g., int) raises TypeError."""
        self.assert_error_behavior(
            func_to_call=search_issues_jql,
            expected_exception_type=TypeError,
            expected_message="jql must be a string.",
            jql=123
        )

    def test_invalid_start_at_type(self):
        """Test that start_at with an invalid type (e.g., str) raises TypeError."""
        self.assert_error_behavior(
            func_to_call=search_issues_jql,
            expected_exception_type=TypeError,
            expected_message="start_at must be an integer or None.",
            start_at="not-an-int"
        )

    def test_invalid_start_at_value_negative(self):
        """Test that a negative start_at value raises ValueError."""
        self.assert_error_behavior(
            func_to_call=search_issues_jql,
            expected_exception_type=ValueError,
            expected_message="start_at must be non-negative.",
            start_at=-1
        )

    def test_invalid_max_results_type(self):
        """Test that max_results with an invalid type (e.g., float) raises TypeError."""
        self.assert_error_behavior(
            func_to_call=search_issues_jql,
            expected_exception_type=TypeError,
            expected_message="max_results must be an integer or None.",
            max_results=10.5
        )

    def test_invalid_max_results_value_negative(self):
        """Test that a negative max_results value raises ValueError."""
        self.assert_error_behavior(
            func_to_call=search_issues_jql,
            expected_exception_type=ValueError,
            expected_message="max_results must be non-negative.",
            max_results=-5
        )

    def test_invalid_fields_type(self):
        """Test that fields with an invalid type (e.g., str) raises TypeError."""
        self.assert_error_behavior(
            func_to_call=search_issues_jql,
            expected_exception_type=TypeError,
            expected_message="fields must be a list of strings or None.",
            fields="not-a-list"
        )

    def test_invalid_fields_element_type(self):
        """Test that a fields list containing non-string elements raises ValueError."""
        self.assert_error_behavior(
            func_to_call=search_issues_jql,
            expected_exception_type=ValueError,
            expected_message="All elements in 'fields' must be strings.",
            fields=["valid_field", 123, "another_field"]
        )

    def test_invalid_expand_type(self):
        """Test that expand with an invalid type (e.g., dict) raises TypeError."""
        self.assert_error_behavior(
            func_to_call=search_issues_jql,
            expected_exception_type=TypeError,
            expected_message="expand must be a list of strings or None.",
            expand={"key": "value"}
        )

    def test_invalid_expand_element_type(self):
        """Test that an expand list containing non-string elements raises ValueError."""
        self.assert_error_behavior(
            func_to_call=search_issues_jql,
            expected_exception_type=ValueError,
            expected_message="All elements in 'expand' must be strings.",
            expand=[True, "valid_expand_item", None]
        )

    def test_invalid_validate_query_type(self):
        """Test that validate_query with an invalid type (e.g., str) raises TypeError."""
        self.assert_error_behavior(
            func_to_call=search_issues_jql,
            expected_exception_type=TypeError,
            expected_message="validate_query must be a boolean or None.",
            validate_query="not-a-bool"
        )

if __name__ == "__main__":
    unittest.main()