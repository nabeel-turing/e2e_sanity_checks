import unittest
from common_utils.base_case import BaseTestCaseWithErrorHandler
from gdrive import DB, create_shared_drive, _ensure_user
from pydantic import ValidationError as PydanticValidationError

class TestDrivesCreate(BaseTestCaseWithErrorHandler):
    def setUp(self):
        # Reset DB before each test
        global DB
        DB.update(
            {
                "users": {
                    "me": {
                        "drives": {},
                        "counters": {
                            "drive": 0,
                        },
                    }
                }
            }
        )
        # Ensure the user exists and has all necessary keys
        _ensure_user("me")

    def test_drives_create(self):
        """Test drive creation with various options."""
        # Test basic drive creation
        drive1 = create_shared_drive(requestId="request_1", body={"name": "Test Drive 1"})
        self.assertEqual(drive1["id"], "request_1")
        self.assertEqual(drive1["name"], "Test Drive 1")
        self.assertIn("createdTime", drive1)
        self.assertFalse(drive1["hidden"])

        # Test drive creation with all properties
        drive_properties = {
            "name": "Test Drive 2",
            "hidden": True,
            "themeId": "theme_123",
            "restrictions": {
                "adminManagedRestrictions": True,
                "copyRequiresWriterPermission": True,
                "domainUsersOnly": True,
                "driveMembersOnly": True,
            },
        }
        drive2 = create_shared_drive(requestId="request_2", body=drive_properties)
        self.assertEqual(drive2["id"], "request_2")
        self.assertEqual(drive2["name"], "Test Drive 2")
        self.assertTrue(drive2["hidden"])
        self.assertEqual(drive2["themeId"], "theme_123")
        self.assertTrue(drive2["restrictions"]["adminManagedRestrictions"])

    def test_drives_create_validation(self):
        """Test input validation for drive creation."""
        with self.assertRaisesRegex(TypeError, "requestId must be a string if provided."):
            create_shared_drive(requestId=123, body={"name": "test"})
        
        with self.assertRaisesRegex(TypeError, "body must be a dictionary."):
            create_shared_drive(requestId="test", body="not_a_dict")

        with self.assertRaisesRegex(PydanticValidationError, "Input should be a valid string"):
            create_shared_drive(body={"name": 123})

        with self.assertRaisesRegex(PydanticValidationError, "Input should be a valid boolean"):
            create_shared_drive(body={"hidden": "txrue"})

        with self.assertRaisesRegex(PydanticValidationError, "Input should be a valid string"):
            create_shared_drive(body={"themeId": 456})

        with self.assertRaisesRegex(PydanticValidationError, "Input should be a valid dictionary"):
            create_shared_drive(body={"restrictions": "invalid"})

        with self.assertRaisesRegex(PydanticValidationError, "Input should be a valid boolean"):
            create_shared_drive(body={"restrictions": {"adminManagedRestrictions": "trues"}})

if __name__ == '__main__':
    unittest.main() 