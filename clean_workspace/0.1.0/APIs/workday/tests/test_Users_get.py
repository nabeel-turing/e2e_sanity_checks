"""
Test module for Users.get() function.

This module contains comprehensive tests for the Users.get() function which retrieves
a list of SCIM users from the Workday Strategic Sourcing system with support for
filtering, pagination, sorting, and attribute selection.
"""

import unittest
from unittest.mock import patch
from typing import Dict, Any, List

# Import the function under test
from ..Users import get
from ..SimulationEngine.custom_errors import (
    InvalidAttributeError, InvalidPaginationParameterError, 
    InvalidSortByValueError, InvalidSortOrderValueError
)
from common_utils.base_case import BaseTestCaseWithErrorHandler


class TestUsersGet(BaseTestCaseWithErrorHandler):
    """Test class for Users.get() function."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Sample user data for testing
        self.sample_users = [
            {
                "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
                "id": "1",
                "externalId": "1",
                "userName": "jdoe@gmail.com",
                "name": {
                    "givenName": "Jane",
                    "familyName": "Doe"
                },
                "active": True,
                "roles": [
                    {
                        "value": "admin",
                        "display": "Admin",
                        "primary": True,
                        "type": "primary"
                    }
                ],
                "meta": {
                    "resourceType": "User",
                    "created": "2024-01-01T00:00:00Z",
                    "lastModified": "2024-06-01T00:00:00Z",
                    "location": "https://api.us.workdayspend.com/scim/v2/Users/1"
                }
            },
            {
                "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
                "id": "2",
                "externalId": "2", 
                "userName": "asmith@gmail.com",
                "name": {
                    "givenName": "Alice",
                    "familyName": "Smith"
                },
                "active": True,
                "roles": [
                    {
                        "value": "manager",
                        "display": "Manager",
                        "primary": True,
                        "type": "primary"
                    }
                ],
                "meta": {
                    "resourceType": "User",
                    "created": "2024-01-02T00:00:00Z",
                    "lastModified": "2024-06-02T00:00:00Z",
                    "location": "https://api.us.workdayspend.com/scim/v2/Users/2"
                }
            }
        ]

    @patch('workday.Users.db')
    def test_get_all_users_success(self, mock_db):
        """Test successful retrieval of all users without filters."""
        # Arrange
        mock_db.DB = {"scim": {"users": self.sample_users.copy()}}
        
        # Act
        result = get()
        
        # Assert
        self.assertIsInstance(result, dict)
        self.assertEqual(result["schemas"], ["urn:ietf:params:scim:api:messages:2.0:ListResponse"])
        self.assertEqual(result["totalResults"], 2)
        self.assertEqual(result["startIndex"], 1)
        self.assertEqual(result["itemsPerPage"], 2)
        self.assertEqual(len(result["Resources"]), 2)

    @patch('workday.Users.db')
    def test_get_with_pagination(self, mock_db):
        """Test user retrieval with pagination parameters."""
        # Arrange
        mock_db.DB = {"scim": {"users": self.sample_users.copy()}}
        
        # Act
        result = get(startIndex=1, count=1)
        
        # Assert
        self.assertEqual(result["startIndex"], 1)
        self.assertEqual(result["itemsPerPage"], 1)
        self.assertEqual(len(result["Resources"]), 1)
        self.assertEqual(result["totalResults"], 2)

    @patch('workday.Users.db')
    def test_get_with_sorting(self, mock_db):
        """Test user retrieval with sorting."""
        # Arrange
        mock_db.DB = {"scim": {"users": self.sample_users.copy()}}
        
        # Act
        result = get(sortBy="id", sortOrder="descending")
        
        # Assert
        self.assertEqual(result["Resources"][0]["id"], "2")
        self.assertEqual(result["Resources"][1]["id"], "1")

    @patch('workday.Users.db')
    def test_get_with_attributes_filter(self, mock_db):
        """Test user retrieval with attribute filtering."""
        # Arrange
        mock_db.DB = {"scim": {"users": self.sample_users.copy()}}
        
        # Act
        result = get(attributes="userName,id")
        
        # Assert
        for user in result["Resources"]:
            self.assertIn("userName", user)
            self.assertIn("id", user)
            self.assertIn("schemas", user)  # Always included for SCIM compliance
            self.assertNotIn("name", user)
            self.assertNotIn("roles", user)

    @patch('workday.Users.db')
    def test_get_with_filter_expression(self, mock_db):
        """Test user retrieval with SCIM filter expression."""
        # Arrange
        mock_db.DB = {"scim": {"users": self.sample_users.copy()}}
        
        # Act
        result = get(filter='userName eq "jdoe@gmail.com"')
        
        # Assert
        self.assertEqual(result["totalResults"], 1)
        self.assertEqual(result["Resources"][0]["userName"], "jdoe@gmail.com")

    def test_invalid_attributes(self):
        """Test validation error for invalid attributes."""
        # Act & Assert
        with self.assertRaises(InvalidAttributeError):
            get(attributes="invalidAttribute")

    def test_invalid_pagination_parameters(self):
        """Test validation errors for invalid pagination parameters."""
        # Test invalid startIndex
        with self.assertRaises(InvalidPaginationParameterError):
            get(startIndex=0)
        
        # Test invalid count
        with self.assertRaises(InvalidPaginationParameterError):
            get(count=-1)
        
        # Test non-integer startIndex
        with self.assertRaises(InvalidPaginationParameterError):
            get(startIndex="invalid")

    def test_invalid_sort_parameters(self):
        """Test validation errors for invalid sort parameters."""
        # Test invalid sortBy
        with self.assertRaises(InvalidSortByValueError):
            get(sortBy="invalidField")
        
        # Test invalid sortOrder
        with self.assertRaises(InvalidSortOrderValueError):
            get(sortOrder="invalidOrder")

    @patch('workday.Users.db')
    def test_empty_result_with_filter(self, mock_db):
        """Test empty result when filter matches no users."""
        # Arrange
        mock_db.DB = {"scim": {"users": self.sample_users.copy()}}
        
        # Act
        result = get(filter='userName eq "nonexistent@example.com"')
        
        # Assert
        self.assertEqual(result["totalResults"], 0)
        self.assertEqual(result["itemsPerPage"], 0)
        self.assertEqual(len(result["Resources"]), 0)

    @patch('workday.Users.db')
    def test_count_zero(self, mock_db):
        """Test behavior when count is set to 0."""
        # Arrange
        mock_db.DB = {"scim": {"users": self.sample_users.copy()}}
        
        # Act
        result = get(count=0)
        
        # Assert
        self.assertEqual(result["itemsPerPage"], 0)
        self.assertEqual(len(result["Resources"]), 0)
        self.assertEqual(result["totalResults"], 2)  # Total should still reflect all users

    def test_invalid_filter_expression(self):
        """Test error handling for invalid filter expressions."""
        # Act & Assert
        with self.assertRaises(ValueError):
            get(filter="invalid filter expression")

    @patch('workday.Users.db')
    def test_complex_filter_expression(self, mock_db):
        """Test complex filter expression with logical operators."""
        # Arrange
        mock_db.DB = {"scim": {"users": self.sample_users.copy()}}
        
        # Act
        result = get(filter='active eq true and userName co "jdoe"')
        
        # Assert
        self.assertEqual(result["totalResults"], 1)
        self.assertEqual(result["Resources"][0]["userName"], "jdoe@gmail.com")

    @patch('workday.Users.db')
    def test_attribute_filtering_with_nested_attributes(self, mock_db):
        """Test attribute filtering with nested attributes."""
        # Arrange
        mock_db.DB = {"scim": {"users": self.sample_users.copy()}}
        
        # Act
        result = get(attributes="name.givenName,meta.created")
        
        # Assert
        for user in result["Resources"]:
            self.assertIn("name", user)
            self.assertIn("givenName", user["name"])
            self.assertNotIn("familyName", user["name"])
            self.assertIn("meta", user)
            self.assertIn("created", user["meta"])
            self.assertNotIn("lastModified", user["meta"])

    @patch('workday.Users.db')
    def test_filter_with_or_logical_operator(self, mock_db):
        """Test filter expression with OR logical operator."""
        # Arrange
        mock_db.DB = {"scim": {"users": self.sample_users.copy()}}
        
        # Act
        result = get(filter='userName eq "jdoe@gmail.com" or userName eq "asmith@gmail.com"')
        
        # Assert
        self.assertEqual(result["totalResults"], 2)
        usernames = [user["userName"] for user in result["Resources"]]
        self.assertIn("jdoe@gmail.com", usernames)
        self.assertIn("asmith@gmail.com", usernames)

    @patch('workday.Users.db')
    def test_filter_with_not_logical_operator(self, mock_db):
        """Test filter expression with NOT logical operator."""
        # Arrange
        mock_db.DB = {"scim": {"users": self.sample_users.copy()}}
        
        # Act
        result = get(filter='not userName eq "jdoe@gmail.com"')
        
        # Assert
        self.assertEqual(result["totalResults"], 1)
        self.assertEqual(result["Resources"][0]["userName"], "asmith@gmail.com")

    @patch('workday.Users.db')
    def test_filter_with_parentheses(self, mock_db):
        """Test filter expression with parentheses for grouping."""
        # Arrange
        mock_db.DB = {"scim": {"users": self.sample_users.copy()}}
        
        # Act
        result = get(filter='(userName eq "jdoe@gmail.com" or userName eq "asmith@gmail.com") and active eq true')
        
        # Assert
        self.assertEqual(result["totalResults"], 2)

    @patch('workday.Users.db')
    def test_filter_with_contains_operator(self, mock_db):
        """Test filter expression with contains (co) operator."""
        # Arrange
        mock_db.DB = {"scim": {"users": self.sample_users.copy()}}
        
        # Act
        result = get(filter='userName co "@gmail.com"')
        
        # Assert
        self.assertEqual(result["totalResults"], 2)

    @patch('workday.Users.db')
    def test_filter_with_starts_with_operator(self, mock_db):
        """Test filter expression with starts with (sw) operator."""
        # Arrange
        mock_db.DB = {"scim": {"users": self.sample_users.copy()}}
        
        # Act
        result = get(filter='userName sw "jdoe"')
        
        # Assert
        self.assertEqual(result["totalResults"], 1)
        self.assertEqual(result["Resources"][0]["userName"], "jdoe@gmail.com")

    @patch('workday.Users.db')
    def test_filter_with_ends_with_operator(self, mock_db):
        """Test filter expression with ends with (ew) operator."""
        # Arrange
        mock_db.DB = {"scim": {"users": self.sample_users.copy()}}
        
        # Act
        result = get(filter='userName ew "gmail.com"')
        
        # Assert
        self.assertEqual(result["totalResults"], 2)

    @patch('workday.Users.db')
    def test_filter_with_present_operator(self, mock_db):
        """Test filter expression with present (pr) operator."""
        # Arrange
        mock_db.DB = {"scim": {"users": self.sample_users.copy()}}
        
        # Act
        result = get(filter='externalId pr')
        
        # Assert
        self.assertEqual(result["totalResults"], 2)  # Both users have externalId

    @patch('workday.Users.db')
    def test_filter_with_not_equal_operator(self, mock_db):
        """Test filter expression with not equal (ne) operator."""
        # Arrange
        mock_db.DB = {"scim": {"users": self.sample_users.copy()}}
        
        # Act
        result = get(filter='userName ne "jdoe@gmail.com"')
        
        # Assert
        self.assertEqual(result["totalResults"], 1)
        self.assertEqual(result["Resources"][0]["userName"], "asmith@gmail.com")

    @patch('workday.Users.db')
    def test_filter_with_greater_than_operator(self, mock_db):
        """Test filter expression with greater than (gt) operator."""
        # Arrange
        mock_db.DB = {"scim": {"users": self.sample_users.copy()}}
        
        # Act
        result = get(filter='meta.created gt "2024-01-01T12:00:00Z"')
        
        # Assert
        self.assertEqual(result["totalResults"], 1)  # Only user 2 created after this time

    @patch('workday.Users.db')
    def test_filter_with_greater_equal_operator(self, mock_db):
        """Test filter expression with greater than or equal (ge) operator."""
        # Arrange
        mock_db.DB = {"scim": {"users": self.sample_users.copy()}}
        
        # Act
        result = get(filter='meta.created ge "2024-01-01T00:00:00Z"')
        
        # Assert
        self.assertEqual(result["totalResults"], 2)  # Both users created on or after this time

    @patch('workday.Users.db')
    def test_filter_with_less_than_operator(self, mock_db):
        """Test filter expression with less than (lt) operator."""
        # Arrange
        mock_db.DB = {"scim": {"users": self.sample_users.copy()}}
        
        # Act
        result = get(filter='meta.created lt "2024-01-02T00:00:00Z"')
        
        # Assert
        self.assertEqual(result["totalResults"], 1)  # Only user 1 created before this time

    @patch('workday.Users.db')
    def test_filter_with_less_equal_operator(self, mock_db):
        """Test filter expression with less than or equal (le) operator."""
        # Arrange
        mock_db.DB = {"scim": {"users": self.sample_users.copy()}}
        
        # Act
        result = get(filter='meta.created le "2024-01-02T00:00:00Z"')
        
        # Assert
        self.assertEqual(result["totalResults"], 2)  # Both users created on or before this time

    @patch('workday.Users.db')
    def test_filter_with_roles_attribute(self, mock_db):
        """Test filter expression with roles attributes."""
        # Arrange
        mock_db.DB = {"scim": {"users": self.sample_users.copy()}}
        
        # Act
        result = get(filter='roles.value eq "admin"')
        
        # Assert
        self.assertEqual(result["totalResults"], 1)
        self.assertEqual(result["Resources"][0]["userName"], "jdoe@gmail.com")

    @patch('workday.Users.db')
    def test_pagination_with_large_start_index(self, mock_db):
        """Test pagination with start index larger than available results."""
        # Arrange
        mock_db.DB = {"scim": {"users": self.sample_users.copy()}}
        
        # Act
        result = get(startIndex=10, count=5)
        
        # Assert
        self.assertEqual(result["startIndex"], 10)
        self.assertEqual(result["itemsPerPage"], 0)
        self.assertEqual(len(result["Resources"]), 0)
        self.assertEqual(result["totalResults"], 2)

    @patch('workday.Users.db')
    def test_pagination_with_exact_count(self, mock_db):
        """Test pagination where count exactly matches remaining items."""
        # Arrange
        mock_db.DB = {"scim": {"users": self.sample_users.copy()}}
        
        # Act
        result = get(startIndex=2, count=1)
        
        # Assert
        self.assertEqual(result["startIndex"], 2)
        self.assertEqual(result["itemsPerPage"], 1)
        self.assertEqual(len(result["Resources"]), 1)
        self.assertEqual(result["Resources"][0]["userName"], "asmith@gmail.com")

    @patch('workday.Users.db')
    def test_sorting_by_external_id_ascending(self, mock_db):
        """Test sorting by externalId in ascending order."""
        # Arrange
        mock_db.DB = {"scim": {"users": self.sample_users.copy()}}
        
        # Act
        result = get(sortBy="externalId", sortOrder="ascending")
        
        # Assert
        self.assertEqual(result["Resources"][0]["externalId"], "1")
        self.assertEqual(result["Resources"][1]["externalId"], "2")

    @patch('workday.Users.db')
    def test_sorting_by_external_id_descending(self, mock_db):
        """Test sorting by externalId in descending order."""
        # Arrange
        mock_db.DB = {"scim": {"users": self.sample_users.copy()}}
        
        # Act
        result = get(sortBy="externalId", sortOrder="descending")
        
        # Assert
        self.assertEqual(result["Resources"][0]["externalId"], "2")
        self.assertEqual(result["Resources"][1]["externalId"], "1")

    @patch('workday.Users.db')
    def test_combined_filter_pagination_sorting(self, mock_db):
        """Test combining filter, pagination, and sorting parameters."""
        # Arrange
        mock_db.DB = {"scim": {"users": self.sample_users.copy()}}
        
        # Act
        result = get(
            filter='active eq true',
            startIndex=1,
            count=1,
            sortBy="id",
            sortOrder="descending"
        )
        
        # Assert
        self.assertEqual(result["totalResults"], 2)
        self.assertEqual(result["itemsPerPage"], 1)
        self.assertEqual(len(result["Resources"]), 1)

    @patch('workday.Users.db')
    def test_attributes_with_all_role_fields(self, mock_db):
        """Test attribute filtering with all role sub-attributes."""
        # Arrange
        mock_db.DB = {"scim": {"users": self.sample_users.copy()}}
        
        # Act
        result = get(attributes="roles.value,roles.display,roles.primary,roles.type")
        
        # Assert
        for user in result["Resources"]:
            self.assertIn("roles", user)
            if user["roles"]:  # If user has roles
                for role in user["roles"]:
                    self.assertIn("value", role)
                    self.assertIn("display", role)
                    self.assertIn("primary", role)
                    self.assertIn("type", role)

    @patch('workday.Users.db')
    def test_attributes_with_complete_meta_object(self, mock_db):
        """Test attribute filtering requesting complete meta object."""
        # Arrange
        mock_db.DB = {"scim": {"users": self.sample_users.copy()}}
        
        # Act
        result = get(attributes="meta")
        
        # Assert
        for user in result["Resources"]:
            self.assertIn("meta", user)
            self.assertIn("resourceType", user["meta"])
            self.assertIn("created", user["meta"])
            self.assertIn("lastModified", user["meta"])
            self.assertIn("location", user["meta"])
            self.assertNotIn("userName", user)
            self.assertNotIn("name", user)

    @patch('workday.Users.db')
    def test_empty_database(self, mock_db):
        """Test behavior when database is empty."""
        # Arrange
        mock_db.DB = {"scim": {"users": []}}
        
        # Act
        result = get()
        
        # Assert
        self.assertEqual(result["totalResults"], 0)
        self.assertEqual(result["itemsPerPage"], 0)
        self.assertEqual(len(result["Resources"]), 0)
        self.assertEqual(result["startIndex"], 1)

    @patch('workday.Users.db')
    def test_filter_with_boolean_true_value(self, mock_db):
        """Test filter with boolean true value."""
        # Arrange
        mock_db.DB = {"scim": {"users": self.sample_users.copy()}}
        
        # Act
        result = get(filter='active eq true')
        
        # Assert
        self.assertEqual(result["totalResults"], 2)
        for user in result["Resources"]:
            self.assertTrue(user["active"])

    @patch('workday.Users.db')
    def test_filter_with_boolean_false_value(self, mock_db):
        """Test filter with boolean false value."""
        # Arrange
        # Add an inactive user to test data
        inactive_user = self.sample_users[0].copy()
        inactive_user["id"] = "3"
        inactive_user["userName"] = "inactive@gmail.com"
        inactive_user["active"] = False
        mock_db.DB = {"scim": {"users": self.sample_users.copy() + [inactive_user]}}
        
        # Act
        result = get(filter='active eq false')
        
        # Assert
        self.assertEqual(result["totalResults"], 1)
        self.assertFalse(result["Resources"][0]["active"])

    @patch('workday.Users.db')
    def test_default_pagination_values(self, mock_db):
        """Test default pagination values when not specified."""
        # Arrange
        mock_db.DB = {"scim": {"users": self.sample_users.copy()}}
        
        # Act
        result = get()
        
        # Assert
        self.assertEqual(result["startIndex"], 1)  # Default startIndex
        self.assertEqual(result["itemsPerPage"], 2)  # Should match total available
        self.assertEqual(result["totalResults"], 2)

    def test_invalid_sort_by_non_string(self):
        """Test validation error for non-string sortBy."""
        # Act & Assert
        with self.assertRaises(InvalidSortByValueError):
            get(sortBy=123)

    def test_invalid_sort_order_non_string(self):
        """Test validation error for non-string sortOrder."""
        # Act & Assert
        with self.assertRaises(InvalidSortOrderValueError):
            get(sortOrder=123)

    def test_invalid_start_index_non_integer(self):
        """Test validation error for non-integer startIndex."""
        # Act & Assert
        with self.assertRaises(InvalidPaginationParameterError):
            get(startIndex="not_an_int")

    def test_invalid_count_non_integer(self):
        """Test validation error for non-integer count."""
        # Act & Assert
        with self.assertRaises(InvalidPaginationParameterError):
            get(count="not_an_int")

    def test_invalid_start_index_zero(self):
        """Test validation error for startIndex of 0."""
        # Act & Assert
        with self.assertRaises(InvalidPaginationParameterError):
            get(startIndex=0)

    def test_invalid_count_negative(self):
        """Test validation error for negative count."""
        # Act & Assert
        with self.assertRaises(InvalidPaginationParameterError):
            get(count=-1)


if __name__ == '__main__':
    unittest.main()
