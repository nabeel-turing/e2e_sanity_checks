import unittest
import os
import json
import builtins
from common_utils.base_case import BaseTestCaseWithErrorHandler
from pydantic import ValidationError as PydanticValidationError
from common_utils.error_handling import get_package_error_mode
from gdrive import (
    DB,
    _ensure_user,
    get_file_metadata_or_content
)
from gdrive.SimulationEngine.custom_errors import InvalidPageSizeError
from unittest.mock import patch
from gdrive.SimulationEngine.db import DB as SimulationDB

# Global DB for testing
DB = {}

# Mock functions
def _ensure_user(userId):
    """Minimal mock for _ensure_user, ensuring necessary DB structure."""
    if "users" not in DB:
        DB["users"] = {}
    if userId not in DB["users"]:
        DB["users"][userId] = {}
    if "drives" not in DB["users"][userId]:
        DB["users"][userId]["drives"] = {}
    if "about" not in DB["users"][userId]:
         DB["users"][userId]["about"] = {
            "kind": "drive#about",
            "storageQuota": {"limit": "107374182400", "usageInDrive": "0", "usageInDriveTrash": "0", "usage": "0"},
            "canCreateDrives": True, "user": {"emailAddress": "me@example.com"},
        }
    if "files" not in DB["users"][userId]: 
        DB["users"][userId]["files"] = {}
    if "comments" not in DB["users"][userId]: 
        DB["users"][userId]["comments"] = {}

def _parse_query(q_str):
    """Minimal mock for _parse_query."""
    if "error_on_parse" in q_str:
        raise ValueError("Invalid query string format (mocked error)")
    return []

def _apply_query_filter(drives_list, conditions):
    """Minimal mock for _apply_query_filter."""
    if not conditions:
        return drives_list
    return drives_list

class TestGetFileMetadataOrContent(BaseTestCaseWithErrorHandler):
    def setUp(self):
        """Reset DB and ensure user 'me' exists before each test."""
        # Clear and initialize the SimulationDB
        SimulationDB.clear()
        SimulationDB.update({
            "users": {
                "me": {
                    "files": {
                        "file123": {
                            "id": "file123",
                            "name": "My Test Document",
                            "mimeType": "application/vnd.google-apps.document",
                            "kind": "drive#file",
                            "parents": ["folder456"],
                            "createdTime": "2023-01-01T10:00:00Z",
                            "modifiedTime": "2023-01-02T12:00:00Z",
                            "trashed": False,
                            "starred": True,
                            "owners": ["me@example.com"],
                            "size": "1024",
                            "permissions": [{"id": "perm1", "type": "user", "role": "owner"}]
                        }
                    },
                    "about": {
                        "kind": "drive#about",
                        "storageQuota": {
                            "limit": "107374182400",
                            "usageInDrive": "0",
                            "usageInDriveTrash": "0",
                            "usage": "0"
                        },
                        "canCreateDrives": True,
                        "user": {"emailAddress": "me@example.com"}
                    }
                }
            }
        })
        _ensure_user("me")

    def test_get_existing_file_valid_id(self):
        """Test retrieving an existing file with a valid fileId."""
        file_id = "file123"
        result = get_file_metadata_or_content(fileId=file_id)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["id"], file_id)
        self.assertEqual(result["name"], "My Test Document")
        self.assertIn("mimeType", result)

    def test_get_file_not_found(self):
        """Test retrieving a non-existent file; should return None."""
        non_existent_file_id = "file_not_found_id"
        self.assert_error_behavior(
            func_to_call=get_file_metadata_or_content,
            expected_exception_type=FileNotFoundError,
            expected_message=f"File with ID '{non_existent_file_id}' not found.",
            fileId=non_existent_file_id
        )

    def test_invalid_file_id_type_integer(self):
        """Test that an integer fileId raises TypeError."""
        self.assert_error_behavior(
            func_to_call=get_file_metadata_or_content,
            expected_exception_type=TypeError,
            expected_message="fileId must be a string.",
            fileId=12345
        )

    def test_invalid_file_id_type_none(self):
        """Test that a None fileId raises TypeError."""
        self.assert_error_behavior(
            func_to_call=get_file_metadata_or_content,
            expected_exception_type=ValueError,
            expected_message="fileId cannot be None",
            fileId=None
        )

    def test_invalid_file_id_type_list(self):
        """Test that a list fileId raises TypeError."""
        self.assert_error_behavior(
            func_to_call=get_file_metadata_or_content,
            expected_exception_type=TypeError,
            expected_message="fileId must be a string.",
            fileId=["id1"]
        )

    def test_empty_string_file_id(self):
        """Test behavior with an empty string fileId (should return None if not found)."""
        self.assert_error_behavior(
            func_to_call=get_file_metadata_or_content,
            expected_exception_type=ValueError,
            expected_message="fileId cannot be empty or consist only of whitespace.",
            fileId=""
        )

    def test_none_file_id(self):
        """Test behavior with a None fileId (should return None if not found)."""
        self.assert_error_behavior(
            func_to_call=get_file_metadata_or_content,
            expected_exception_type=ValueError,
            expected_message="fileId cannot be None",
            fileId=None
        )

    def test_key_error_if_user_structure_is_missing(self):
        """Test that KeyError is raised if user structure is missing."""
        SimulationDB.clear()
        # Don't add any users to the DB to trigger the KeyError

        self.assert_error_behavior(
            func_to_call=get_file_metadata_or_content,
            expected_exception_type=KeyError,
            expected_message="'users'",  # The actual error message from the function
            fileId="anyFileId"
        )