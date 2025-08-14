from common_utils.base_case import BaseTestCaseWithErrorHandler

from gdrive.SimulationEngine.db import DB
from gdrive.SimulationEngine.utils import _ensure_user
from gdrive.SimulationEngine.custom_errors import ResourceNotFoundError
from gdrive import create_file_or_folder, create_permission, delete_file_permanently
from pydantic import ValidationError

class TestPermissionsCreate(BaseTestCaseWithErrorHandler):
    """
    Test suite for the Permissions.create function.
    """

    def setUp(self):
        """Set up a clean environment for each test."""
        # **THE FIX:** The DB is now reset with the 'about' key, which is
        # required by create_file_or_folder to check storage quotas.
        DB.update({
            'users': {
                'me': {
                    'about': {
                        'storageQuota': {'limit': '107374182400', 'usage': '0'},
                        'user': {'emailAddress': 'me@example.com'}
                    },
                    'files': {},
                    'drives': {},
                    'counters': {
                        'file': 0,
                        'permission': 0
                    }
                }
            }
        })

        # This call will now succeed.
        self.file = create_file_or_folder({"name": "test_file.txt"})
        self.file_id = self.file["id"]

        self.drive_id = "test_drive_1"
        DB['users']['me']['drives'][self.drive_id] = {"id": self.drive_id, "name": "Test Shared Drive", "permissions": []}

    def tearDown(self):
        """Clean up after each test."""
        delete_file_permanently(self.file_id)
        DB['users']['me']['drives'].pop(self.drive_id, None)

    ##
    ## Success and Happy Path Tests
    ##

    def test_create_permission_basic_success(self):
        """Test creating a simple permission on a file."""
        body = {"role": "editor", "type": "user", "emailAddress": "test@example.com"}
        permission = create_permission(self.file_id, body)

        self.assertEqual(permission['role'], 'editor')
        self.assertEqual(permission['emailAddress'], 'test@example.com')
        
        saved_perms = DB['users']['me']['files'][self.file_id]['permissions']

        self.assertEqual(len(saved_perms), 2)
        self.assertEqual(saved_perms[1]['id'], permission['id']) # The new permission is the second one

    def test_create_permission_all_fields_success(self):
        """Test creating a permission with all possible fields."""
        body = {
            "role": "commenter",
            "type": "group",
            "emailAddress": "team@example.com",
            "allowFileDiscovery": True,
            "expirationTime": "2025-12-31T23:59:59Z"
        }
        permission = create_permission(self.file_id, body)

        self.assertEqual(permission['role'], 'commenter')
        self.assertTrue(permission['allowFileDiscovery'])
        self.assertEqual(permission['expirationTime'], "2025-12-31T23:59:59Z")

    def test_create_permission_with_no_body_uses_defaults(self):
        """Test that calling create with no body applies defaults."""
        permission = create_permission(self.file_id, None)

        self.assertEqual(permission['role'], 'reader')
        self.assertEqual(permission['type'], 'user')
        self.assertFalse(permission['allowFileDiscovery'])
        self.assertEqual(permission['emailAddress'], '')

    def test_create_permission_on_drive_success(self):
        """Test creating a permission directly on a shared drive."""
        body = {"role": "organizer", "type": "user", "emailAddress": "admin@example.com"}
        permission = create_permission(self.drive_id, body)
        
        self.assertEqual(permission['role'], 'organizer')
        saved_perms = DB['users']['me']['drives'][self.drive_id]['permissions']
        self.assertEqual(len(saved_perms), 1)
        self.assertEqual(saved_perms[0]['emailAddress'], "admin@example.com")
        
    def test_adding_second_permission(self):
        """Test adding multiple permissions to a single file."""
        create_permission(self.file_id, {"role": "viewer", "type": "user", "emailAddress": "viewer@example.com"})
        create_permission(self.file_id, {"role": "editor", "type": "user", "emailAddress": "editor@example.com"})

        saved_perms = DB['users']['me']['files'][self.file_id]['permissions']

        self.assertEqual(len(saved_perms), 3)
        self.assertEqual(saved_perms[2]['role'], 'editor') # The editor is the third one

    ##
    ## Failure and Edge Case Tests
    ##

    def test_create_fails_with_non_string_fileId(self):
        """Test that a non-string fileId raises TypeError."""
        with self.assertRaisesRegex(TypeError, "fileId must be a string."):
            create_permission(12345, {})

    def test_create_fails_with_empty_fileId(self):
        """Test that an empty string fileId raises ValueError."""
        with self.assertRaisesRegex(ValueError, "fileId cannot be an empty string."):
            create_permission("   ", {})

    def test_create_fails_with_nonexistent_fileId(self):
        """Test that a non-existent fileId raises ResourceNotFoundError."""
        with self.assertRaises(ResourceNotFoundError):
            create_permission("nonexistent-id", {})

    def test_pydantic_fails_with_invalid_role(self):
        """Test Pydantic validation for an invalid 'role' value."""
        with self.assertRaises(ValidationError):
            create_permission(self.file_id, {"role": "invalid_role"})

    def test_pydantic_fails_with_invalid_type(self):
        """Test Pydantic validation for an invalid 'type' value."""
        with self.assertRaises(ValidationError):
            create_permission(self.file_id, {"type": "invalid_type"})

    def test_pydantic_fails_with_invalid_boolean_type(self):
        """Test Pydantic validation for a non-boolean 'allowFileDiscovery'."""
        with self.assertRaises(ValidationError):
            create_permission(self.file_id, {"allowFileDiscovery": "not_a_boolean"})

    def test_pydantic_fails_with_invalid_email_type(self):
        """Test Pydantic validation for a non-string 'emailAddress'."""
        with self.assertRaises(ValidationError):
            create_permission(self.file_id, {"emailAddress": 12345})
