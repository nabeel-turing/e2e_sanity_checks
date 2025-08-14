from pydantic import ValidationError

from common_utils.base_case import BaseTestCaseWithErrorHandler

from gdrive import _ensure_user

from gdrive import get_drive_account_info

from gdrive.SimulationEngine.db import DB as SimulationDB


class TestGetDriveAccountInfo(BaseTestCaseWithErrorHandler):
    def setUp(self):
        """Reset DB and ensure 'me' user for each test."""
        SimulationDB.clear() # Clear DB for isolation
        SimulationDB.update(
            {
                "users": {
                    "me": {
                        "about": {
                            "kind": "drive#about",
                            "user": {
                                "displayName": "Test User",
                                "emailAddress": "me@example.com",
                                "permissionId": "0123456789",
                                "photoLink": "https://example.com/photo.jpg"
                            },
                            "storageQuota": {
                                "limit": "107374182400",
                                "usage": "5000000000",
                                "usageInDrive": "4000000000",
                                "usageInDriveTrash": "1000000000"
                            },
                            "maxImportSizes": {"application/pdf": "10485760"},
                            "maxUploadSize": "5242880000",
                            "appInstalled": True,
                            "folderColorPalette": "#FF0000, #00FF00",
                            "importFormats": {"text/plain": ["application/vnd.google-apps.document"]},
                            "exportFormats": {"application/vnd.google-apps.document": ["text/plain"]},
                            "canCreateDrives": True,
                            "driveThemes": [
                                {"id": "theme1", "backgroundImageLink": "link1", "colorRgb": "rgb1"}
                            ]
                        },
                        "files": {}, # Other parts of user data not directly used by 'get'
                        "drives": {},
                        "comments": {},
                        "replies": {},
                        "labels": {},
                        "accessproposals": {},
                        "apps": {},
                        "channels": {},
                        "changes": {"startPageToken": "1", "changes": []},
                        "counters": {},
                    }
                }
            }
        )
        _ensure_user("me") # Ensure 'me' user specifically has its structure set up

    def test_valid_fields_asterisk(self):
        """Test with fields='*' to get all account information."""
        info = get_drive_account_info(fields='*')
        self.assertIsInstance(info, dict)
        self.assertEqual(info, SimulationDB['users']['me']['about'])
        self.assertIn('user', info)
        self.assertIn('storageQuota', info)

    def test_valid_fields_single_top_level(self):
        """Test fetching a single top-level field."""
        info = get_drive_account_info(fields='user')
        self.assertIn('user', info)
        self.assertIn('displayName', info['user'])
        self.assertNotIn('storageQuota', info)
        self.assertIn('kind', info) # 'kind' should always be included

    def test_valid_fields_multiple_top_level(self):
        """Test fetching multiple top-level fields."""
        info = get_drive_account_info(fields='user,storageQuota')
        self.assertIn('user', info)
        self.assertIn('storageQuota', info)
        self.assertNotIn('maxUploadSize', info)
        self.assertIn('kind', info)

    def test_valid_fields_single_nested(self):
        """Test fetching a single nested field."""
        info = get_drive_account_info(fields='user.emailAddress')
        self.assertIn('user', info)
        self.assertIn('emailAddress', info['user'])
        self.assertNotIn('displayName', info['user']) # Only emailAddress should be in user
        self.assertNotIn('storageQuota', info)
        self.assertIn('kind', info)

    def test_valid_fields_multiple_nested(self):
        """Test fetching multiple nested fields from different parents."""
        info = get_drive_account_info(fields='user.emailAddress,storageQuota.limit')
        self.assertIn('user', info)
        self.assertIn('emailAddress', info['user'])
        self.assertNotIn('displayName', info['user'])
        self.assertIn('storageQuota', info)
        self.assertIn('limit', info['storageQuota'])
        self.assertNotIn('usage', info['storageQuota'])
        self.assertIn('kind', info)
        
    def test_valid_fields_multiple_nested_same_parent(self):
        """Test fetching multiple nested fields from the same parent."""
        info = get_drive_account_info(fields='user.emailAddress,user.displayName')
        self.assertIn('user', info)
        self.assertIn('emailAddress', info['user'])
        self.assertIn('displayName', info['user'])
        self.assertNotIn('permissionId', info['user']) # Other user fields not requested
        self.assertIn('kind', info)

    def test_fields_with_spaces(self):
        """Test fields parameter with spaces around commas and names."""
        info = get_drive_account_info(fields=' user.emailAddress , storageQuota.limit ')
        self.assertIn('user', info)
        self.assertIn('emailAddress', info['user'])
        self.assertIn('storageQuota', info)
        self.assertIn('limit', info['storageQuota'])
        self.assertIn('kind', info)

    def test_non_existent_top_level_field(self):
        """Test requesting a non-existent top-level field."""
        info = get_drive_account_info(fields='nonExistentField')
        self.assertNotIn('nonExistentField', info)
        self.assertIn('kind', info) # Kind is always there
        self.assertEqual(len(info.keys()), 1) # Only 'kind'

    def test_non_existent_nested_field(self):
        """Test requesting a non-existent nested field."""
        info = get_drive_account_info(fields='user.nonExistentSubField')
        self.assertIn('user', info) # Parent 'user' exists
        self.assertNotIn('nonExistentSubField', info['user'])
        self.assertTrue(not info['user']) # user dict should be empty as subfield not found
        self.assertIn('kind', info)

    def test_non_existent_parent_of_nested_field(self):
        """Test requesting a nested field whose parent does not exist."""
        info = get_drive_account_info(fields='nonExistentParent.child')
        self.assertNotIn('nonExistentParent', info)
        self.assertIn('kind', info)
        self.assertEqual(len(info.keys()), 1)

    def test_multiple_commas_empty_fields(self):
        """Test fields parameter with multiple commas creating empty fields."""
        info = get_drive_account_info(fields='user,,storageQuota,')
        self.assertIn('user', info)
        self.assertIn('storageQuota', info)
        self.assertIn('kind', info)

    def test_invalid_fields_type_integer(self):
        """Test that providing an integer for 'fields' raises TypeError."""
        self.assert_error_behavior(
            func_to_call=get_drive_account_info,
            expected_exception_type=TypeError,
            expected_message="Argument 'fields' must be a string.",
            fields=123
        )

    def test_invalid_fields_type_list(self):
        """Test that providing a list for 'fields' raises TypeError."""
        self.assert_error_behavior(
            func_to_call=get_drive_account_info,
            expected_exception_type=TypeError,
            expected_message="Argument 'fields' must be a string.",
            fields=['user', 'storageQuota']
        )

    def test_invalid_fields_empty_string(self):
        """Test that an empty string for 'fields' raises ValueError."""
        self.assert_error_behavior(
            func_to_call=get_drive_account_info,
            expected_exception_type=ValueError,
            expected_message="Argument 'fields' cannot be an empty string or consist only of whitespace.",
            fields=''
        )

    def test_invalid_fields_whitespace_string(self):
        """Test that a whitespace-only string for 'fields' raises ValueError."""
        self.assert_error_behavior(
            func_to_call=get_drive_account_info,
            expected_exception_type=ValueError,
            expected_message="Argument 'fields' cannot be an empty string or consist only of whitespace.",
            fields='   '
        )

    def test_key_error_if_user_not_in_db(self):
        """Test that KeyError is raised if user 'me' is not in DB (simulated)."""
        SimulationDB.clear() # Clear DB to simulate missing user
        
        self.assert_error_behavior(
            func_to_call=get_drive_account_info,
            expected_exception_type=KeyError,
            expected_message='"User \'me\' not found in database"',
            fields='*'
        )

    def test_key_error_if_about_not_in_user_data(self):
        """Test that KeyError is raised if 'about' data is missing for user 'me'."""
        SimulationDB.clear()
        SimulationDB.update({
            "users": {
                "me": {
                    "files": {},
                    "drives": {},
                    "comments": {},
                    "replies": {},
                    "labels": {},
                    "accessproposals": {},
                    "apps": {},
                    "channels": {},
                    "changes": {"startPageToken": "1", "changes": []},
                    "counters": {},
                }
            }
        })
        
        self.assert_error_behavior(
            func_to_call=get_drive_account_info,
            expected_exception_type=KeyError,
            expected_message='"\'about\' data not found for user \'me\'"',
            fields='*'
        )

    def test_folder_color_palette_string_conversion(self):
        """Test that a string folderColorPalette is converted to a list."""
        # Override the setup data to simulate the DB string format
        SimulationDB['users']['me']['about']['folderColorPalette'] = "#FF0000, #00FF00, #0000FF"
        
        # Test with specific field selection
        info = get_drive_account_info(fields='folderColorPalette')
        self.assertIsInstance(info['folderColorPalette'], list)
        self.assertEqual(info['folderColorPalette'], ['#FF0000', '#00FF00', '#0000FF'])

        # Test with wildcard to ensure conversion happens there too
        info_all = get_drive_account_info(fields='*')
        self.assertIsInstance(info_all['folderColorPalette'], list)
        self.assertEqual(info_all['folderColorPalette'], ['#FF0000', '#00FF00', '#0000FF'])

    def test_requesting_list_field_directly(self):
        """Test fetching a top-level field that is a list of objects."""
        info = get_drive_account_info(fields='driveThemes')
        self.assertIn('driveThemes', info)
        self.assertIsInstance(info['driveThemes'], list)
        self.assertEqual(info['driveThemes'], SimulationDB['users']['me']['about']['driveThemes'])
        self.assertIn('kind', info)

    def test_requesting_nested_field_in_list_is_not_supported(self):
        """Test that nested field selection in a list of objects is not supported and doesn't crash."""
        info = get_drive_account_info(fields='driveThemes.id')
        self.assertIn('driveThemes', info)
        # The current implementation returns an empty dictionary for the parent. This test documents that behavior.
        self.assertEqual(info['driveThemes'], {}) 
        self.assertIn('kind', info)
    
    def test_mixed_valid_and_invalid_fields(self):
        """Test requesting a mix of valid, non-existent, and nested fields."""
        info = get_drive_account_info(fields='user.displayName,storageQuota,nonExistentField')
        self.assertIn('user', info)
        self.assertIn('displayName', info['user'])
        self.assertNotIn('emailAddress', info['user'])
        
        self.assertIn('storageQuota', info)
        self.assertIsInstance(info['storageQuota'], dict)

        self.assertNotIn('nonExistentField', info)
        self.assertIn('kind', info)