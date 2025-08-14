import unittest
import copy
from common_utils.base_case import BaseTestCaseWithErrorHandler
from ..SimulationEngine.db import DB
from ..SimulationEngine import custom_errors
from contacts import create_contact

class TestCreateContact(BaseTestCaseWithErrorHandler):
    """
    Test suite for the create_contact function.
    """

    def setUp(self):
        """
        Set up a clean DB state for each test.
        """
        self._original_DB_state = copy.deepcopy(DB)
        DB.clear()
        DB.update({
            "myContacts": {
                "people/c12345": {
                    "resourceName": "people/c12345",
                    "etag": "existingEtag",
                    "names": [{"givenName": "Existing", "familyName": "Contact"}],
                    "emailAddresses": [{"value": "existing.contact@example.com"}]
                }
            },
            "otherContacts": {},
            "directory": {}
        })

    def tearDown(self):
        """
        Restore the original DB state after each test.
        """
        DB.clear()
        DB.update(self._original_DB_state)

    def test_create_contact_success_all_fields(self):
        """
        Test creating a contact with all optional fields provided.
        """
        result = create_contact(
            given_name="Jane",
            family_name="Doe",
            email="jane.doe@example.com",
            phone="+19876543210"
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Contact 'Jane' created successfully.")
        
        # Verify the structure of the returned contact
        created_contact = result["contact"]
        self.assertIn("resourceName", created_contact)
        self.assertTrue(created_contact["resourceName"].startswith("people/c"))
        self.assertIn("etag", created_contact)
        
        self.assertEqual(created_contact["names"][0]["givenName"], "Jane")
        self.assertEqual(created_contact["names"][0]["familyName"], "Doe")
        self.assertEqual(created_contact["emailAddresses"][0]["value"], "jane.doe@example.com")
        self.assertEqual(created_contact["phoneNumbers"][0]["value"], "+19876543210")
        
        # Verify the contact was added to the DB
        resource_name = created_contact["resourceName"]
        self.assertIn(resource_name, DB["myContacts"])
        self.assertEqual(DB["myContacts"][resource_name], created_contact)

    def test_create_contact_success_only_email(self):
        """
        Test creating a contact with only the given name and email.
        """
        result = create_contact(
            given_name="John",
            email="john.smith@example.com"
        )
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Contact 'John' created successfully.")
        
        created_contact = result["contact"]
        self.assertEqual(created_contact["names"][0]["givenName"], "John")
        self.assertNotIn("familyName", created_contact["names"][0])
        self.assertEqual(created_contact["emailAddresses"][0]["value"], "john.smith@example.com")
        self.assertNotIn("phoneNumbers", created_contact)
        
        resource_name = created_contact["resourceName"]
        self.assertIn(resource_name, DB["myContacts"])

    def test_create_contact_success_only_phone(self):
        """
        Test creating a contact with only the given name and phone number.
        """
        result = create_contact(
            given_name="Peter",
            phone="555-1234"
        )
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Contact 'Peter' created successfully.")

        created_contact = result["contact"]
        self.assertEqual(created_contact["names"][0]["givenName"], "Peter")
        self.assertNotIn("emailAddresses", created_contact)
        self.assertEqual(created_contact["phoneNumbers"][0]["value"], "555-1234")

        resource_name = created_contact["resourceName"]
        self.assertIn(resource_name, DB["myContacts"])

    def test_create_contact_success_only_family_name(self):
        """
        Test creating a contact with only the given and family names.
        """
        result = create_contact(
            given_name="Susan",
            family_name="Jones"
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Contact 'Susan' created successfully.")

        created_contact = result["contact"]
        self.assertEqual(created_contact["names"][0]["givenName"], "Susan")
        self.assertEqual(created_contact["names"][0]["familyName"], "Jones")
        self.assertNotIn("emailAddresses", created_contact)
        self.assertNotIn("phoneNumbers", created_contact)
        
        resource_name = created_contact["resourceName"]
        self.assertIn(resource_name, DB["myContacts"])

    def test_create_contact_no_given_name_raises_error(self):
        """
        Test that creating a contact with an empty given_name raises a ValidationError.
        """
        self.assert_error_behavior(
            func_to_call=create_contact,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="The 'given_name' must be a non-empty string.",
            given_name="",
            email="test@test.com"
        )

    def test_create_contact_no_optional_fields_raises_error(self):
        """
        Test that creating a contact with no optional fields raises a ValidationError.
        """
        self.assert_error_behavior(
            func_to_call=create_contact,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="At least one of the optional fields (family_name, email, phone) must be provided.",
            given_name="Justa Name"
        )

    def test_create_contact_invalid_email_raises_error(self):
        """
        Test that creating a contact with an invalid email address raises a ValidationError.
        """
        invalid_email = "not-an-email"
        self.assert_error_behavior(
            func_to_call=create_contact,
            expected_exception_type=custom_errors.ValidationError,
            expected_message=f"The email address '{invalid_email}' is not valid.",
            given_name="Test",
            email=invalid_email
        )

    def test_create_contact_duplicate_email_raises_error(self):
        """
        Test that creating a contact with an already existing email raises a ValidationError.
        """
        existing_email = "existing.contact@example.com"
        self.assert_error_behavior(
            func_to_call=create_contact,
            expected_exception_type=custom_errors.ValidationError,
            expected_message=f"A contact with the email '{existing_email}' already exists.",
            given_name="Another",
            email=existing_email
        )

if __name__ == '__main__':
    unittest.main()