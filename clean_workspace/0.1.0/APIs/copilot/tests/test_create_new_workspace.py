import copy
import unittest
import os

from copilot.SimulationEngine import custom_errors
from copilot.SimulationEngine.db import DB
from copilot.project_setup import create_new_workspace
from common_utils.base_case import BaseTestCaseWithErrorHandler

# Decorator to skip tests if API key is not available
def skip_if_no_api_key(func):
    def wrapper(*args, **kwargs):
        if not os.getenv("GOOGLE_API_KEY") and not os.getenv("GEMINI_API_KEY"):
            raise unittest.SkipTest("Skipping real LLM call test: API key not found in environment.")
        return func(*args, **kwargs)
    return wrapper

class TestCreateNewWorkspace(BaseTestCaseWithErrorHandler):
    def setUp(self):
        # Store original DB state
        self._original_DB_state = copy.deepcopy(DB)
        DB.clear()  # Clear the actual global DB

        # Populate DB directly for this test class
        DB['workspace_root'] = '/test_workspace'
        DB['cwd'] = '/test_workspace'
        DB['file_system'] = {
            DB['workspace_root']: {
                'path': DB['workspace_root'],
                'is_directory': True,
                'content_lines': [],
                'size_bytes': 0,
                'last_modified': '2023-01-01T00:00:00Z'
            }
        }

    def tearDown(self):
        # Restore original DB state
        DB.clear()
        DB.update(self._original_DB_state)

    @skip_if_no_api_key
    def test_successful_workspace_creation_basic_query(self):
        query = "Create a simple Python script that prints hello world."
        # As mocking LLM calls is not explicitly permitted by the strict import rules,
        # this test verifies successful execution and the basic expected structure of the response.
        # The content of 'summary' and 'steps' will be LLM-dependent.
        result = create_new_workspace(query=query)

        self.assertIsInstance(result, dict, "Result should be a dictionary.")
        self.assertIn("query", result, "Result should contain the original query.")
        self.assertEqual(result["query"], query)

        self.assertIn("summary", result, "Result should contain a 'summary' field.")
        self.assertIsInstance(result["summary"], str, "'summary' field should be a string.")

        self.assertIn("steps", result, "Result should contain a 'steps' field.")
        self.assertIsInstance(result["steps"], list, "'steps' field should be a list.")

    @skip_if_no_api_key
    def test_successful_workspace_creation_complex_query(self):
        query = "Set up a new Next.js project with TypeScript and Tailwind CSS, including initial git setup."
        result = create_new_workspace(query=query)

        self.assertIsInstance(result, dict, "Result should be a dictionary.")
        self.assertIn("query", result, "Result should contain the original query.")
        self.assertEqual(result["query"], query)

        self.assertIn("summary", result, "Result should contain a 'summary' field.")
        self.assertIsInstance(result["summary"], str, "'summary' field should be a string.")

        self.assertIn("steps", result, "Result should contain a 'steps' field.")
        self.assertIsInstance(result["steps"], list, "'steps' field should be a list.")

    def test_query_empty_string_raises_validation_error(self):
        self.assert_error_behavior(
            func_to_call=create_new_workspace,
            query="",
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Query must be a non-empty string."
        )

    def test_query_whitespace_string_raises_validation_error(self):
        self.assert_error_behavior(
            func_to_call=create_new_workspace,
            query="   ",
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Query must be a non-empty string."
        )

    def test_query_none_raises_validation_error(self):
        self.assert_error_behavior(
            func_to_call=create_new_workspace,
            query=None,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Query must be a non-empty string."
        )

    def test_query_invalid_type_int_raises_validation_error(self):
        self.assert_error_behavior(
            func_to_call=create_new_workspace,
            query=123,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Query must be a non-empty string."
        )

    def test_query_invalid_type_list_raises_validation_error(self):
        self.assert_error_behavior(
            func_to_call=create_new_workspace,
            query=["list", "item"],
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Query must be a non-empty string."
        )

    def test_workspace_root_missing_in_db_raises_workspace_not_available_error(self):
        # This test assumes that create_new_workspace (or utils it calls and error-handles)
        # requires DB['workspace_root'] and raises WorkspaceNotAvailableError if it's missing.
        DB.pop('workspace_root', None)

        # Clean up file_system if workspace_root was used as a key, to avoid downstream issues
        # if the function attempts to access file_system with a now-missing root path.
        # This specific path '/test_workspace' was tied to the original DB['workspace_root'].
        if '/test_workspace' in DB.get('file_system', {}):
            del DB['file_system']['/test_workspace']

        self.assert_error_behavior(
            func_to_call=create_new_workspace,
            query="A valid query.",
            expected_exception_type=custom_errors.WorkspaceNotAvailableError,
            expected_message="Workspace root is not configured."
        )

    @skip_if_no_api_key
    def test_cwd_missing_in_db_still_succeeds_if_workspace_root_exists(self):
        # Assumes that if 'cwd' is missing, it might default to 'workspace_root' internally,
        # allowing the function to proceed if 'workspace_root' is available.
        DB.pop('cwd', None)
        query = "Create a small utility script."

        result = create_new_workspace(query=query)

        self.assertIsInstance(result, dict, "Result should be a dictionary even if cwd was missing but defaulted.")
        self.assertEqual(result.get("query"), query)
        self.assertIn("summary", result)
        self.assertIsInstance(result["summary"], str)
        self.assertIn("steps", result)
        self.assertIsInstance(result["steps"], list)


if __name__ == '__main__':
    unittest.main()
