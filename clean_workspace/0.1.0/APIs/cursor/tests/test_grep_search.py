# # cursor/tests/test_grep_search.py
# import unittest
# import copy
# import os
# from unittest.mock import patch
# from common_utils.base_case import BaseTestCaseWithErrorHandler
# from ..cursorAPI import grep_search
# from ..SimulationEngine.db import DB as GlobalDBSource
# from ..SimulationEngine.custom_errors import InvalidInputError

# # Import the original DB for copying initial state
# from .. import DB as GlobalDBSource


# class TestGrepSearch(BaseTestCaseWithErrorHandler):
#     """
#     Test cases for the grep_search function, which performs regex-based text
#     searches across files defined in the application's internal data store.
#     """

#     # Define potential transient filenames for cleanup, if needed.
#     transient_test_files = []

#     def setUp(self):
#         """Prepares a clean, isolated database state before each test method."""
#         self.pristine_db_state = copy.deepcopy(GlobalDBSource)
#         self.db_for_test = copy.deepcopy(self.pristine_db_state)
#         # Start with an empty file system representation for most tests
#         self.db_for_test["file_system"] = {}
#         ws_root = self.db_for_test.get(
#             "workspace_root", "/test_ws"
#         )  # Ensure a default root
#         self.db_for_test["workspace_root"] = ws_root
#         self._add_dir(ws_root)  # Ensure root directory entry exists

#         # Patch 'DB' in relevant modules
#         self.db_patcher_for_init_module = patch("cursor.DB", self.db_for_test)
#         self.db_patcher_for_init_module.start()
#         self.db_patcher_for_utils_module = patch(
#             "cursor.SimulationEngine.utils.DB", self.db_for_test
#         )
#         self.db_patcher_for_utils_module.start()

#         # Patch 'DB' in the cursorAPI module where the actual function is defined
#         self.db_patcher_for_cursorapi_module = patch(
#             "cursor.cursorAPI.DB", self.db_for_test
#         )
#         self.db_patcher_for_cursorapi_module.start()

#         self.db_for_test["file_system"] = {
#             "/ws/main.py": {
#                 "path": "/ws/main.py",
#                 "is_directory": False,
#                 "content_lines": ["import flask", "app = flask.Flask(__name__)", "app.run()"],
#             },
#             "/ws/utils.py": {
#                 "path": "/ws/utils.py",
#                 "is_directory": False,
#                 "content_lines": ["def helper_function():", "    return 'helper'"],
#             },
#             "/ws/config.txt": {
#                 "path": "/ws/config.txt",
#                 "is_directory": False,
#                 "content_lines": ["HOST=localhost", "PORT=8080"],
#             },
#         }

#         self._cleanup_transient_files()

#     def tearDown(self):
#         """Restores the original state and cleans up transient files."""
#         self._cleanup_transient_files()
#         self.db_patcher_for_cursorapi_module.stop()
#         self.db_patcher_for_utils_module.stop()
#         self.db_patcher_for_init_module.stop()

#     def _cleanup_transient_files(self):
#         """Removes any specified transient files created during testing."""
#         cursor_module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#         for filename in self.transient_test_files:
#             file_path = os.path.join(cursor_module_dir, filename)
#             if os.path.exists(file_path):
#                 try:
#                     os.remove(file_path)
#                 except OSError as e:
#                     print(f"Warning: Could not clean up test file {file_path}: {e}")

#     def _add_file_with_content(self, path, content_lines):
#         """Helper to add a file with specific content lines."""
#         # Ensure parent directories exist
#         dir_name = os.path.dirname(path)
#         if dir_name:
#             current_path = ""
#             root = self.db_for_test.get("workspace_root", "/")
#             parts = dir_name.replace(root, "").strip("/").split("/")
#             current_path = root
#             if root not in self.db_for_test["file_system"]:
#                 self._add_dir(root)
#             for part in parts:
#                 if not part:
#                     continue
#                 if current_path == "/" and not part.startswith("/"):
#                     current_path = "/" + part
#                 elif current_path.endswith("/") and part.startswith("/"):
#                     current_path = current_path + part[1:]
#                 elif not current_path.endswith("/") and not part.startswith("/"):
#                     current_path = current_path + "/" + part
#                 else:
#                     current_path = current_path + part
#                 current_path = os.path.normpath(current_path)
#                 if current_path not in self.db_for_test["file_system"]:
#                     self._add_dir(current_path)

#         # Add file entry
#         self.db_for_test["file_system"][path] = {
#             "path": path,
#             "is_directory": False,
#             "content_lines": content_lines,
#             "size_bytes": sum(len(line.encode("utf-8")) for line in content_lines),
#             "last_modified": "T_FILE",
#         }

#     def _add_dir(self, path):
#         """Helper to add a directory entry if it doesn't exist."""
#         if path not in self.db_for_test["file_system"]:
#             self.db_for_test["file_system"][path] = {
#                 "path": path,
#                 "is_directory": True,
#                 "size_bytes": 0,
#                 "last_modified": "T_DIR",
#             }

#     def _assert_match(
#         self, match_dict, expected_path, expected_line_num, expected_content
#     ):
#         """Helper to assert properties of a single match dictionary."""
#         self.assertEqual(match_dict.get("file_path"), expected_path)
#         self.assertEqual(match_dict.get("line_number"), expected_line_num)
#         self.assertEqual(match_dict.get("line_content"), expected_content)

#     # --- Test Cases ---

#     def test_basic_match(self):
#         """Verify finding a simple string in one file."""
#         path = "/test_ws/file.txt"
#         content = ["Hello world\n", "This is line two\n", "Another Hello\n"]
#         self._add_file_with_content(path, content)
#         results = grep_search(query="Hello")
#         self.assertEqual(len(results), 2)
#         self._assert_match(results[0], path, 1, "Hello world")
#         self._assert_match(results[1], path, 3, "Another Hello")

#     def test_multiple_files(self):
#         """Verify finding matches across different files."""
#         path1 = "/test_ws/one.py"
#         content1 = ["import sys\n", "print('TARGET')\n"]
#         path2 = "/test_ws/two.txt"
#         content2 = ["This TARGET is important\n", "No match here\n"]
#         self._add_file_with_content(path1, content1)
#         self._add_file_with_content(path2, content2)
#         results = grep_search(query="TARGET")
#         self.assertEqual(len(results), 2)
#         # Order depends on sorted path iteration
#         self._assert_match(results[0], path1, 2, "print('TARGET')")
#         self._assert_match(results[1], path2, 1, "This TARGET is important")

#     def test_case_sensitive_default(self):
#         """Verify case-sensitive matching is the default."""
#         path = "/test_ws/case.txt"
#         content = ["MatchThis\n", "matchthis\n", "MATCHTHIS\n"]
#         self._add_file_with_content(path, content)
#         results = grep_search(query="MatchThis")
#         self.assertEqual(len(results), 1)
#         self._assert_match(results[0], path, 1, "MatchThis")

#     def test_case_insensitive_match(self):
#         """Verify case-insensitive matching when specified."""
#         path = "/test_ws/case.txt"
#         content = ["MatchThis\n", "matchthis\n", "MATCHTHIS\n"]
#         self._add_file_with_content(path, content)
#         results = grep_search(query="MatchThis", case_sensitive=False)
#         self.assertEqual(len(results), 3)
#         self._assert_match(results[0], path, 1, "MatchThis")
#         self._assert_match(results[1], path, 2, "matchthis")
#         self._assert_match(results[2], path, 3, "MATCHTHIS")

#     def test_regex_metacharacters(self):
#         """Verify common regex metacharacters function correctly."""
#         path = "/test_ws/regex.txt"
#         content = ["start middle end\n", "abc\n", "a.c\n", "1.0\n"]
#         self._add_file_with_content(path, content)

#         # Test '.' (any character) - Should match 'abc' (line 2) and 'a.c' (line 3)
#         results_dot = grep_search(query="a.c")
#         self.assertEqual(len(results_dot), 2, "Regex 'a.c' should match two lines")
#         # Verify the specific matches found (order depends on line iteration)
#         self._assert_match(results_dot[0], path, 2, "abc")
#         self._assert_match(results_dot[1], path, 3, "a.c")

#         # Test '^' (start anchor)
#         results_start = grep_search(query="^start")
#         self.assertEqual(len(results_start), 1, "Regex '^start' should match one line")
#         self._assert_match(results_start[0], path, 1, "start middle end")

#         # Test '$' (end anchor)
#         results_end = grep_search(query="end$")
#         self.assertEqual(len(results_end), 1, "Regex 'end$' should match one line")
#         self._assert_match(results_end[0], path, 1, "start middle end")

#         # Test escaped literal dot using a raw string for the pattern
#         results_escaped = grep_search(query=r"1\.0")
#         self.assertEqual(len(results_escaped), 1, "Regex '1\\.0' should match one line")
#         self._assert_match(results_escaped[0], path, 4, "1.0")

#     def test_no_match(self):
#         """Verify empty list is returned when the query matches nothing."""
#         path = "/test_ws/data.log"
#         content = ["Log entry one\n", "Another entry\n"]
#         self._add_file_with_content(path, content)
#         results = grep_search(query="non_existent_pattern")
#         self.assertEqual(results, [])

#     def test_invalid_regex_query(self):
#         """Verify ValueError is raised for an invalid regex pattern."""
#         path = "/test_ws/data.log"
#         content = ["Some content\n"]
#         self._add_file_with_content(path, content)
#         with self.assertRaises(ValueError) as cm:
#             grep_search(query="[invalidRegex")  # Unbalanced bracket
#         self.assertIn("Invalid regex pattern", str(cm.exception))

#     def test_empty_query(self):
#         """Verify empty list is returned for an empty query string."""
#         path = "/test_ws/data.log"
#         content = ["Some content\n"]
#         self._add_file_with_content(path, content)
#         results = grep_search(query="")
#         self.assertEqual(results, [])

#     def test_skip_directories(self):
#         """Verify that directories are not searched."""
#         self._add_dir("/test_ws/a_directory")
#         self.db_for_test["file_system"]["/test_ws/a_directory"]["content_lines"] = [
#             "This should not be searched\n"
#         ]  # Add content just in case
#         self._add_file_with_content("/test_ws/a_file.txt", ["Search this instead\n"])
#         results = grep_search(query="Search")
#         self.assertEqual(len(results), 1)
#         self._assert_match(results[0], "/test_ws/a_file.txt", 1, "Search this instead")

#     def test_include_pattern_filter(self):
#         """Verify that only files matching the include pattern are searched."""
#         self._add_file_with_content("/test_ws/include_me.py", ["match_target\n"])
#         self._add_file_with_content("/test_ws/ignore_me.txt", ["match_target\n"])
#         self._add_file_with_content(
#             "/test_ws/scripts/include_me_too.py", ["match_target\n"]
#         )
#         results = grep_search(query="match_target", include_pattern="*.py")
#         self.assertEqual(len(results), 2)
#         self.assertTrue(all(r["file_path"].endswith(".py") for r in results))
#         self.assertCountEqual(
#             [r["file_path"] for r in results],
#             ["/test_ws/include_me.py", "/test_ws/scripts/include_me_too.py"],
#         )

#     def test_exclude_pattern_filter(self):
#         """Verify that files matching the exclude pattern are not searched."""
#         self._add_file_with_content("/test_ws/search_me.py", ["match_target\n"])
#         self._add_file_with_content("/test_ws/temp/exclude_me.log", ["match_target\n"])
#         self._add_file_with_content("/test_ws/exclude_me_also.log", ["match_target\n"])
#         results = grep_search(query="match_target", exclude_pattern="*.log")
#         self.assertEqual(len(results), 1)
#         self._assert_match(results[0], "/test_ws/search_me.py", 1, "match_target")

#     def test_include_exclude_interaction(self):
#         """Verify exclude pattern takes precedence over include pattern."""
#         self._add_file_with_content("/test_ws/src/main.py", ["target\n"])
#         self._add_file_with_content(
#             "/test_ws/src/test_main.py", ["target\n"]
#         )  # Included by *.py, excluded by test_*
#         self._add_file_with_content(
#             "/test_ws/src/config.yaml", ["target\n"]
#         )  # Not included
#         results = grep_search(
#             query="target", include_pattern="*.py", exclude_pattern="test_*.py"
#         )
#         self.assertEqual(len(results), 1)
#         self._assert_match(results[0], "/test_ws/src/main.py", 1, "target")

#     def test_result_capping_at_50(self):
#         """Verify results are capped at 50 matches."""
#         path = "/test_ws/many_matches.txt"
#         content = [f"Match line {i}\n" for i in range(100)]  # 100 lines that match
#         self._add_file_with_content(path, content)
#         results = grep_search(query="Match line")
#         self.assertEqual(len(results), 50)
#         # Check the first and last item expected within the cap
#         self._assert_match(results[0], path, 1, "Match line 0")
#         self._assert_match(results[49], path, 50, "Match line 49")

#     def test_empty_file_content(self):
#         """Verify search handles files with empty content correctly."""
#         self._add_file_with_content("/test_ws/empty.txt", [])
#         results = grep_search(query="anything")
#         self.assertEqual(results, [])

#     def test_invalid_query_type_raises_error(self):
#         with self.assertRaises(InvalidInputError):
#             grep_search(query=123)

#     def test_invalid_explanation_type_raises_error(self):
#         with self.assertRaises(InvalidInputError):
#             grep_search(query="test", explanation=[])

#     def test_invalid_case_sensitive_type_raises_error(self):
#         with self.assertRaises(InvalidInputError):
#             grep_search(query="test", case_sensitive="true")

#     def test_invalid_include_pattern_type_raises_error(self):
#         with self.assertRaises(InvalidInputError):
#             grep_search(query="test", include_pattern=123)

#     def test_invalid_exclude_pattern_type_raises_error(self):
#         with self.assertRaises(InvalidInputError):
#             grep_search(query="test", exclude_pattern=False)

#     def test_basic_search(self):
#         results = grep_search(query="flask")
#         self.assertEqual(len(results), 2)
#         self.assertEqual(results[0]["file_path"], "/ws/main.py")
#         self.assertEqual(results[0]["line_number"], 1)
#         self.assertEqual(results[1]["file_path"], "/ws/main.py")
#         self.assertEqual(results[1]["line_number"], 2)

#     def test_case_insensitive_search(self):
#         results = grep_search(query="HOST", case_sensitive=False)
#         self.assertEqual(len(results), 1)
#         self.assertEqual(results[0]["file_path"], "/ws/config.txt")

#     def test_include_pattern(self):
#         results = grep_search(query="import", include_pattern="*.py")
#         self.assertEqual(len(results), 1)
#         self.assertEqual(results[0]["file_path"], "/ws/main.py")

#     def test_exclude_pattern(self):
#         results = grep_search(query=".", exclude_pattern="*.txt")
#         self.assertEqual(len(results), 5)

#     def test_no_matches(self):
#         results = grep_search(query="nonexistent_string")
#         self.assertEqual(len(results), 0)


# if __name__ == "__main__":
#     unittest.main()