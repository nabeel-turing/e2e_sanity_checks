import json
import os
import sys
from pathlib import Path
from unittest.mock import patch
import datetime

import pytest

# Ensure package root is importable when tests run via py.test
sys.path.append(str(Path(__file__).resolve().parents[2]))

from gemini_cli import glob  # noqa: E402
from gemini_cli.SimulationEngine import db as sim_db  # noqa: E402
from gemini_cli.SimulationEngine.custom_errors import InvalidInputError, WorkspaceNotAvailableError  # noqa: E402

DB_JSON_PATH = Path(__file__).resolve().parents[3] / "DBs" / "GeminiCliDefaultDB.json"


@pytest.fixture(autouse=True)
def reload_db():
    """Load fresh DB snapshot before each test."""
    sim_db.DB.clear()
    with open(DB_JSON_PATH, "r", encoding="utf-8") as fh:
        sim_db.DB.update(json.load(fh))


class TestGlob:
    """Test cases for the glob function."""

    def test_glob_basic_pattern_matching(self):
        """Test basic glob pattern matching functionality."""
        # Test matching Python files
        result = glob("*.py")
        py_files = [f for f in result if f.endswith(".py")]
        assert len(py_files) > 0
        assert "/home/user/project/src/main.py" in result
        assert "/home/user/project/src/utils.py" in result

    def test_glob_markdown_files(self):
        """Test matching markdown files."""
        result = glob("*.md")
        md_files = [f for f in result if f.endswith(".md")]
        assert len(md_files) > 0
        assert "/home/user/project/README.md" in result
        assert "/home/user/project/docs/api.md" in result

    def test_glob_recursive_pattern(self):
        """Test recursive glob patterns with **."""
        result = glob("**/*.py")
        assert "/home/user/project/src/main.py" in result
        assert "/home/user/project/src/utils.py" in result
        assert "/home/user/project/tests/test_main.py" in result

    def test_glob_with_specific_path(self):
        """Test glob with specific search path."""
        result = glob("*.py", path="/home/user/project/src")
        assert "/home/user/project/src/main.py" in result
        assert "/home/user/project/src/utils.py" in result
        # Should not include files from other directories
        assert "/home/user/project/tests/test_main.py" not in result

    def test_glob_case_sensitive_matching(self):
        """Test case-sensitive pattern matching."""
        # Add a file with mixed case to test
        sim_db.DB["file_system"]["/home/user/project/Test.PY"] = {
            "path": "/home/user/project/Test.PY",
            "is_directory": False,
            "content_lines": ["# Test file\n"],
            "size_bytes": 12,
            "last_modified": "2025-01-15T10:45:00Z"
        }

        # Case-insensitive (default)
        result = glob("*.py", case_sensitive=False)
        assert "/home/user/project/Test.PY" in result

        # Case-sensitive
        result = glob("*.py", case_sensitive=True)
        assert "/home/user/project/Test.PY" not in result

        result = glob("*.PY", case_sensitive=True)
        assert "/home/user/project/Test.PY" in result

    def test_glob_respect_git_ignore_disabled(self):
        """Test glob with git ignore disabled."""
        # Add a file that would normally be ignored
        sim_db.DB["file_system"]["/home/user/project/debug.log"] = {
            "path": "/home/user/project/debug.log",
            "is_directory": False,
            "content_lines": ["Log content\n"],
            "size_bytes": 12,
            "last_modified": "2025-01-15T10:45:00Z"
        }

        # With git ignore enabled (default), .log files should be filtered out
        result = glob("*.log", respect_git_ignore=True)
        assert "/home/user/project/debug.log" not in result

        # With git ignore disabled, .log files should be included
        result = glob("*.log", respect_git_ignore=False)
        assert "/home/user/project/debug.log" in result

    def test_glob_sorting_by_modification_time(self):
        """Test that files are sorted by modification time (newest first)."""
        # Add files with different modification times
        now = datetime.datetime.utcnow()
        recent_time = now - datetime.timedelta(hours=2)
        old_time = now - datetime.timedelta(days=5)

        sim_db.DB["file_system"]["/home/user/project/recent.txt"] = {
            "path": "/home/user/project/recent.txt",
            "is_directory": False,
            "content_lines": ["Recent content\n"],
            "size_bytes": 15,
            "last_modified": recent_time.isoformat() + "Z"
        }

        sim_db.DB["file_system"]["/home/user/project/old.txt"] = {
            "path": "/home/user/project/old.txt",
            "is_directory": False,
            "content_lines": ["Old content\n"],
            "size_bytes": 12,
            "last_modified": old_time.isoformat() + "Z"
        }

        result = glob("*.txt")
        
        # Recent files should come first, then older files alphabetically
        recent_index = result.index("/home/user/project/recent.txt")
        old_index = result.index("/home/user/project/old.txt")
        
        # Recent file should come before old file
        assert recent_index < old_index

    def test_glob_no_matches(self):
        """Test glob with pattern that matches no files."""
        result = glob("*.xyz")
        assert result == []

    def test_glob_empty_pattern(self):
        """Test glob with empty pattern."""
        with pytest.raises(InvalidInputError, match="'pattern' must be a non-empty string"):
            glob("")

    def test_glob_non_string_pattern(self):
        """Test glob with non-string pattern."""
        with pytest.raises(InvalidInputError, match="'pattern' must be a non-empty string"):
            glob(123)

    def test_glob_invalid_path_type(self):
        """Test glob with invalid path type."""
        with pytest.raises(InvalidInputError, match="'path' must be a non-empty string or None"):
            glob("*.py", path=123)

    def test_glob_empty_path(self):
        """Test glob with empty path."""
        with pytest.raises(InvalidInputError, match="'path' must be a non-empty string or None"):
            glob("*.py", path="")

    def test_glob_relative_path(self):
        """Test glob with relative path."""
        with pytest.raises(InvalidInputError, match="'path' must be an absolute path"):
            glob("*.py", path="src/")

    def test_glob_path_outside_workspace(self):
        """Test glob with path outside workspace."""
        with pytest.raises(InvalidInputError, match="'path' must be within the workspace root"):
            glob("*.py", path="/outside/workspace")

    def test_glob_invalid_case_sensitive_type(self):
        """Test glob with invalid case_sensitive type."""
        with pytest.raises(InvalidInputError, match="'case_sensitive' must be a boolean or None"):
            glob("*.py", case_sensitive="true")

    def test_glob_invalid_respect_git_ignore_type(self):
        """Test glob with invalid respect_git_ignore type."""
        with pytest.raises(InvalidInputError, match="'respect_git_ignore' must be a boolean or None"):
            glob("*.py", respect_git_ignore="true")

    def test_glob_workspace_not_available(self):
        """Test glob when workspace_root is not configured."""
        # Clear the workspace_root
        original_workspace_root = sim_db.DB.get("workspace_root")
        sim_db.DB.pop("workspace_root", None)

        with pytest.raises(WorkspaceNotAvailableError, match="workspace_root not configured in DB"):
            glob("*.py")

        # Restore for other tests
        sim_db.DB["workspace_root"] = original_workspace_root

    def test_glob_path_not_found(self):
        """Test glob with path that doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Search path does not exist"):
            glob("*.py", path="/home/user/project/nonexistent")

    def test_glob_path_not_directory(self):
        """Test glob with path that points to a file."""
        with pytest.raises(NotADirectoryError, match="Search path is not a directory"):
            glob("*.py", path="/home/user/project/README.md")

    def test_glob_pattern_with_subdirectories(self):
        """Test glob patterns that include subdirectories."""
        result = glob("src/*.py")
        assert "/home/user/project/src/main.py" in result
        assert "/home/user/project/src/utils.py" in result
        # Should not include files from other directories
        assert "/home/user/project/tests/test_main.py" not in result

    def test_glob_all_files_pattern(self):
        """Test glob with pattern that matches all files."""
        result = glob("**/*")
        # Should include all files but not directories
        files = [f for f in result if not sim_db.DB["file_system"][f].get("is_directory", False)]
        assert len(files) > 0
        assert "/home/user/project/README.md" in result
        assert "/home/user/project/src/main.py" in result

    def test_glob_json_files(self):
        """Test glob matching JSON files."""
        result = glob("*.json")
        assert "/home/user/project/package.json" in result

    def test_glob_with_question_mark_wildcard(self):
        """Test glob with ? wildcard."""
        # Add files to test single character wildcard
        sim_db.DB["file_system"]["/home/user/project/file1.txt"] = {
            "path": "/home/user/project/file1.txt",
            "is_directory": False,
            "content_lines": ["Content 1\n"],
            "size_bytes": 10,
            "last_modified": "2025-01-15T10:45:00Z"
        }

        sim_db.DB["file_system"]["/home/user/project/file2.txt"] = {
            "path": "/home/user/project/file2.txt",
            "is_directory": False,
            "content_lines": ["Content 2\n"],
            "size_bytes": 10,
            "last_modified": "2025-01-15T10:46:00Z"
        }

        result = glob("file?.txt")
        assert "/home/user/project/file1.txt" in result
        assert "/home/user/project/file2.txt" in result

    def test_glob_alphabetical_sorting_for_old_files(self):
        """Test that old files are sorted alphabetically."""
        # Add old files with different names
        old_time = datetime.datetime.utcnow() - datetime.timedelta(days=5)

        sim_db.DB["file_system"]["/home/user/project/zebra.txt"] = {
            "path": "/home/user/project/zebra.txt",
            "is_directory": False,
            "content_lines": ["Zebra content\n"],
            "size_bytes": 14,
            "last_modified": old_time.isoformat() + "Z"
        }

        sim_db.DB["file_system"]["/home/user/project/apple.txt"] = {
            "path": "/home/user/project/apple.txt",
            "is_directory": False,
            "content_lines": ["Apple content\n"],
            "size_bytes": 14,
            "last_modified": old_time.isoformat() + "Z"
        }

        result = glob("*.txt")
        
        # Find the indices of our test files
        apple_index = result.index("/home/user/project/apple.txt")
        zebra_index = result.index("/home/user/project/zebra.txt")
        
        # Apple should come before zebra (alphabetical order for old files)
        assert apple_index < zebra_index

    def test_glob_gitignore_patterns(self):
        """Test basic gitignore pattern filtering."""
        # Add files that should be ignored
        sim_db.DB["file_system"]["/home/user/project/cache.pyc"] = {
            "path": "/home/user/project/cache.pyc",
            "is_directory": False,
            "content_lines": ["compiled python\n"],
            "size_bytes": 16,
            "last_modified": "2025-01-15T10:45:00Z"
        }

        sim_db.DB["file_system"]["/home/user/project/.DS_Store"] = {
            "path": "/home/user/project/.DS_Store",
            "is_directory": False,
            "content_lines": ["system file\n"],
            "size_bytes": 12,
            "last_modified": "2025-01-15T10:45:00Z"
        }

        # These should be filtered out by gitignore
        result = glob("*", respect_git_ignore=True)
        assert "/home/user/project/cache.pyc" not in result
        assert "/home/user/project/.DS_Store" not in result

        # But should be included when gitignore is disabled
        result = glob("*", respect_git_ignore=False)
        assert "/home/user/project/cache.pyc" in result
        assert "/home/user/project/.DS_Store" in result 