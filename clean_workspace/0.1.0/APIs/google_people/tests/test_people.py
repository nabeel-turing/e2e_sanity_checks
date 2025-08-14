import copy
import unittest

from common_utils.base_case import BaseTestCaseWithErrorHandler
from .common import reset_db
from ..people import (
    get_contact, create_contact, update_contact, delete_contact,
    list_connections, search_people, get_batch_get,
    get_directory_person, list_directory_people, search_directory_people
)
from pydantic import ValidationError as PydanticValidationError


class TestPeopleAPI(BaseTestCaseWithErrorHandler):
    """Test class for Google People API functions."""

    def setUp(self):
        """Set up test database with sample data."""
        reset_db()
        from ..SimulationEngine.db import DB
        
        # Initialize test data
        DB.set("people", {
            "people/123456789": {
                "resourceName": "people/123456789",
                "etag": "etag_123456789",
                "names": [{"displayName": "John Doe", "givenName": "John", "familyName": "Doe"}],
                "emailAddresses": [{"value": "john.doe@example.com", "type": "work"}],
                "phoneNumbers": [{"value": "+1-555-123-4567", "type": "mobile"}],
                "addresses": [{"formattedValue": "123 Main St, City, State"}],
                "organizations": [{"name": "Tech Corp", "title": "Developer"}],
                "created": "2023-01-15T10:30:00Z",
                "updated": "2024-01-15T14:20:00Z"
            },
            "people/987654321": {
                "resourceName": "people/987654321",
                "etag": "etag_987654321",
                "names": [{"displayName": "Jane Smith", "givenName": "Jane", "familyName": "Smith"}],
                "emailAddresses": [{"value": "jane.smith@example.com", "type": "personal"}],
                "phoneNumbers": [{"value": "+1-555-987-6543", "type": "home"}],
                "created": "2023-02-20T11:00:00Z",
                "updated": "2024-01-10T09:15:00Z"
            }
        })

        DB.set("directoryPeople", {
            "directoryPeople/111222333": {
                "resourceName": "directoryPeople/111222333",
                "etag": "etag_dir_111222333",
                "names": [{"displayName": "Bob Wilson", "givenName": "Bob", "familyName": "Wilson"}],
                "emailAddresses": [{"value": "bob.wilson@company.com", "type": "work"}],
                "organizations": [{"name": "Company Inc", "title": "Manager"}],
                "created": "2023-03-10T08:00:00Z",
                "updated": "2024-01-05T16:30:00Z"
            }
        })

    def tearDown(self):
        """Clean up after tests."""
        reset_db()

    def test_get_contact_success(self):
        """Test successful retrieval of a contact."""
        result = get_contact("people/123456789")

        self.assertEqual(result["resourceName"], "people/123456789")
        self.assertEqual(result["etag"], "etag_123456789")
        self.assertEqual(len(result["names"]), 1)
        self.assertEqual(result["names"][0]["displayName"], "John Doe")

    def test_get_contact_with_fields_filter(self):
        """Test contact retrieval with field filtering."""
        result = get_contact("people/123456789", person_fields="names,emailAddresses")

        self.assertIn("names", result)
        self.assertIn("emailAddresses", result)
        self.assertNotIn("phoneNumbers", result)
        self.assertNotIn("addresses", result)

    def test_get_contact_not_found(self):
        """Test contact retrieval when contact doesn't exist."""
        self.assert_error_behavior(
            func_to_call=get_contact,
            expected_exception_type=ValueError,
            expected_message="Person with resource name 'people/nonexistent' not found",
            resource_name="people/nonexistent"
        )

    def test_get_contact_invalid_resource_name(self):
        """Test contact retrieval with invalid resource name."""
        self.assert_error_behavior(
            func_to_call=get_contact,
            expected_exception_type=PydanticValidationError,
            expected_message='Resource name must start with "people/"',
            resource_name="invalid_name"
        )

    def test_create_contact_success(self):
        """Test successful contact creation."""
        person_data = {
            "names": [{"displayName": "New Person", "givenName": "New", "familyName": "Person"}],
            "emailAddresses": [{"value": "new.person@example.com", "type": "work"}]
        }

        result = create_contact(person_data)

        self.assertIn("resourceName", result)
        self.assertIn("etag", result)
        self.assertEqual(result["names"][0]["displayName"], "New Person")
        self.assertEqual(result["emailAddresses"][0]["value"], "new.person@example.com")

    def test_create_contact_with_existing_data(self):
        """Test contact creation with existing database data."""
        person_data = {
            "names": [{"displayName": "Another Person", "givenName": "Another", "familyName": "Person"}],
            "emailAddresses": [{"value": "another.person@example.com", "type": "work"}]
        }

        result = create_contact(person_data)

        self.assertIn("resourceName", result)
        self.assertIn("etag", result)
        self.assertEqual(result["names"][0]["displayName"], "Another Person")

    def test_update_contact_success(self):
        """Test successful contact update."""
        update_data = {
            "phoneNumbers": [{"value": "+1-555-999-8888", "type": "mobile"}]
        }

        result = update_contact("people/123456789", update_data)

        self.assertEqual(result["resourceName"], "people/123456789")
        self.assertEqual(result["phoneNumbers"][0]["value"], "+1-555-999-8888")

    def test_update_contact_with_field_filter(self):
        """Test contact update with specific field filtering."""
        update_data = {
            "phoneNumbers": [{"value": "+1-555-999-8888", "type": "mobile"}],
            "organizations": [{"name": "New Company", "title": "Senior Developer"}]
        }

        result = update_contact("people/123456789", update_data, "phoneNumbers")

        self.assertEqual(result["phoneNumbers"][0]["value"], "+1-555-123-4567")
        # Should not update organizations since it's not in the field filter
        self.assertEqual(result["organizations"][0]["name"], "Tech Corp")

    def test_update_contact_not_found(self):
        """Test contact update when contact doesn't exist."""
        update_data = {"names": [{"displayName": "Updated Name"}]}

        self.assert_error_behavior(
            func_to_call=update_contact,
            expected_exception_type=ValueError,
            expected_message="Person with resource name 'people/nonexistent' not found",
            resource_name="people/nonexistent",
            person_data=update_data
        )

    def test_delete_contact_success(self):
        """Test successful contact deletion."""
        result = delete_contact("people/123456789")

        self.assertTrue(result["success"])
        self.assertEqual(result["deletedResourceName"], "people/123456789")
        self.assertEqual(result["message"], "Person deleted successfully")

    def test_delete_contact_not_found(self):
        """Test contact deletion when contact doesn't exist."""
        self.assert_error_behavior(
            func_to_call=delete_contact,
            expected_exception_type=ValueError,
            expected_message="Person with resource name 'people/nonexistent' not found",
            resource_name="people/nonexistent"
        )

    def test_list_connections_success(self):
        """Test successful listing of connections."""
        result = list_connections()

        self.assertIn("connections", result)
        self.assertIn("totalItems", result)
        self.assertEqual(len(result["connections"]), 2)

    def test_list_connections_with_pagination(self):
        """Test listing connections with pagination."""
        result = list_connections(page_size=1)

        self.assertEqual(len(result["connections"]), 1)
        self.assertIn("nextPageToken", result)

    def test_list_connections_with_sorting(self):
        """Test listing connections with sorting."""
        result = list_connections(sort_order="FIRST_NAME_ASCENDING")

        self.assertIn("connections", result)
        self.assertIn("totalItems", result)

    def test_list_connections_with_fields_filter(self):
        """Test listing connections with field filtering."""
        result = list_connections(person_fields="names,emailAddresses")

        for connection in result["connections"]:
            self.assertIn("names", connection)
            self.assertIn("emailAddresses", connection)
            self.assertNotIn("phoneNumbers", connection)

    def test_search_people_success(self):
        """Test successful search of people."""
        result = search_people("john")

        self.assertIn("results", result)
        self.assertIn("totalItems", result)
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["names"][0]["givenName"], "John")

    def test_search_people_by_email(self):
        """Test searching people by email address."""
        result = search_people("john.doe@example.com")

        self.assertIn("results", result)
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["emailAddresses"][0]["value"], "john.doe@example.com")

    def test_search_people_by_organization(self):
        """Test searching people by organization."""
        result = search_people("Tech Corp")

        self.assertIn("results", result)
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["organizations"][0]["name"], "Tech Corp")

    def test_search_people_with_read_mask(self):
        """Test searching people with read mask filtering."""
        result = search_people("john", read_mask="names,emailAddresses")

        for person in result["results"]:
            self.assertIn("names", person)
            self.assertIn("emailAddresses", person)
            self.assertNotIn("phoneNumbers", person)

    def test_get_batch_get_success(self):
        """Test successful batch retrieval of people."""
        result = get_batch_get(["people/123456789", "people/987654321"])

        self.assertIn("responses", result)
        self.assertIn("notFound", result)
        self.assertEqual(len(result["responses"]), 2)
        self.assertEqual(len(result["notFound"]), 0)

    def test_get_batch_get_with_missing_people(self):
        """Test batch retrieval with some missing people."""
        result = get_batch_get(["people/123456789", "people/nonexistent"])

        self.assertEqual(len(result["responses"]), 1)
        self.assertEqual(len(result["notFound"]), 1)
        self.assertIn("people/nonexistent", result["notFound"])

    def test_get_batch_get_with_fields_filter(self):
        """Test batch retrieval with field filtering."""
        result = get_batch_get(["people/123456789"], person_fields="names,emailAddresses")

        person = result["responses"][0]
        self.assertIn("names", person)
        self.assertIn("emailAddresses", person)
        self.assertNotIn("phoneNumbers", person)

    def test_get_directory_person_success(self):
        """Test successful retrieval of a directory person."""
        result = get_directory_person("directoryPeople/111222333")

        self.assertEqual(result["resourceName"], "directoryPeople/111222333")
        self.assertEqual(result["etag"], "etag_dir_111222333")
        self.assertEqual(len(result["names"]), 1)
        self.assertEqual(result["names"][0]["displayName"], "Bob Wilson")

    def test_get_directory_person_not_found(self):
        """Test directory person retrieval when person doesn't exist."""
        self.assert_error_behavior(
            func_to_call=get_directory_person,
            expected_exception_type=ValueError,
            expected_message="Directory person with resource name 'directoryPeople/nonexistent' not found",
            resource_name="directoryPeople/nonexistent"
        )

    def test_get_directory_person_with_read_mask(self):
        """Test directory person retrieval with read mask filtering."""
        result = get_directory_person("directoryPeople/111222333", read_mask="names,emailAddresses")

        self.assertIn("names", result)
        self.assertIn("emailAddresses", result)
        self.assertNotIn("organizations", result)

    def test_list_directory_people_success(self):
        """Test successful listing of directory people."""
        result = list_directory_people(read_mask="names,emailAddresses")

        self.assertIn("people", result)
        self.assertIn("totalItems", result)
        self.assertEqual(len(result["people"]), 1)

    def test_list_directory_people_without_read_mask(self):
        """Test listing directory people without required read_mask."""
        self.assert_error_behavior(
            func_to_call=list_directory_people,
            expected_exception_type=ValueError,
            expected_message="read_mask is required for list_directory_people"
        )

    def test_list_directory_people_with_pagination(self):
        """Test listing directory people with pagination."""
        result = list_directory_people(read_mask="names", page_size=1)

        self.assertEqual(len(result["people"]), 1)
        self.assertIn("nextPageToken", result)

    def test_search_directory_people_success(self):
        """Test successful search of directory people."""
        result = search_directory_people("bob", read_mask="names,emailAddresses")

        self.assertIn("results", result)
        self.assertIn("totalItems", result)
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["names"][0]["givenName"], "Bob")

    def test_search_directory_people_without_read_mask(self):
        """Test searching directory people without required read_mask."""
        self.assert_error_behavior(
            func_to_call=search_directory_people,
            expected_exception_type=ValueError,
            expected_message="read_mask is required for search_directory_people",
            query="bob"
        )

    def test_search_directory_people_with_pagination(self):
        """Test searching directory people with pagination."""
        result = search_directory_people("bob", read_mask="names", page_size=1)

        self.assertEqual(len(result["results"]), 1)
        self.assertIn("nextPageToken", result)

    def test_search_directory_people_by_email(self):
        """Test searching directory people by email address."""
        result = search_directory_people("bob.wilson@company.com", read_mask="names,emailAddresses")

        self.assertIn("results", result)
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["emailAddresses"][0]["value"], "bob.wilson@company.com")

    def test_search_directory_people_by_organization(self):
        """Test searching directory people by organization."""
        result = search_directory_people("Company Inc", read_mask="names,organizations")

        self.assertIn("results", result)
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["organizations"][0]["name"], "Company Inc")


if __name__ == '__main__':
    unittest.main()
