import unittest
from linkedin import Me
import linkedin as LinkedinAPI
from .common import reset_db
from common_utils.base_case import BaseTestCaseWithErrorHandler


class TestMeEndpoints(BaseTestCaseWithErrorHandler):
    def setUp(self):
        LinkedinAPI.DB.clear()
        LinkedinAPI.DB.update(
            {
                "people": {},
                "organizations": {},
                "organizationAcls": {},
                "posts": {},
                "next_person_id": 1,
                "next_org_id": 1,
                "next_acl_id": 1,
                "next_post_id": 1,
                "current_person_id": None,
            }
        )

    def create_default_person(self):
        """Create a person and mark them as the current authenticated member."""
        person = {
            "firstName": {
                "localized": {"en_US": "Example"},
                "preferredLocale": {"country": "US", "language": "en"},
            },
            "localizedFirstName": "Example",
            "lastName": {
                "localized": {"en_US": "User"},
                "preferredLocale": {"country": "US", "language": "en"},
            },
            "localizedLastName": "User",
            "vanityName": "example-user",
        }
        person["id"] = "1"
        LinkedinAPI.DB["people"]["1"] = person
        LinkedinAPI.DB["current_person_id"] = "1"
        LinkedinAPI.DB["next_person_id"] = 2
        return person

    def test_get_me_success(self):
        self.create_default_person()
        response = Me.get_me()
        self.assertIn("data", response)
        self.assertEqual(response["data"]["id"], "1")

    def test_get_me_with_projection_success(self):
        self.create_default_person()
        projection = "(id,localizedFirstName)"
        response = Me.get_me(projection=projection)
        self.assertIn("data", response)
        data = response["data"]
        self.assertEqual(set(data.keys()), {"id", "localizedFirstName"})
        self.assertEqual(data["id"], "1")
        self.assertEqual(data["localizedFirstName"], "Example")

    def test_get_me_with_projection_missing_field(self):
        self.create_default_person()
        projection = "(id,nonexistentField)"
        response = Me.get_me(projection=projection)
        self.assertIn("data", response)
        data = response["data"]
        self.assertEqual(set(data.keys()), {"id"})
        self.assertEqual(data["id"], "1")

    def test_get_me_projection_without_parentheses(self):
        self.create_default_person()
        projection = "id, localizedFirstName"
        response = Me.get_me(projection=projection)
        self.assertIn("data", response)
        data = response["data"]
        self.assertEqual(set(data.keys()), {"id", "localizedFirstName"})
        self.assertEqual(data["id"], "1")
        self.assertEqual(data["localizedFirstName"], "Example")

    def test_get_me_empty_projection(self):
        self.create_default_person()
        projection = "()"
        response = Me.get_me(projection=projection)
        self.assertIn("data", response)
        data = response["data"]
        self.assertEqual(data, {})

    def test_get_me_blank_projection(self):
        self.create_default_person()
        projection = "   "
        response = Me.get_me(projection=projection)
        self.assertIn("data", response)
        data = response["data"]
        self.assertEqual(data, {})

    def test_get_me_duplicate_fields_in_projection(self):
        self.create_default_person()
        projection = "(id,id,localizedFirstName)"
        response = Me.get_me(projection=projection)
        self.assertIn("data", response)
        data = response["data"]
        self.assertEqual(set(data.keys()), {"id", "localizedFirstName"})
        self.assertEqual(data["id"], "1")
        self.assertEqual(data["localizedFirstName"], "Example")

    def test_get_me_no_authenticated_member(self):
        response = Me.get_me()
        self.assertIn("error", response)
        self.assertEqual(response["error"], "No authenticated member.")

    def test_get_me_authenticated_person_not_found(self):
        LinkedinAPI.DB["current_person_id"] = "999"
        response = Me.get_me()
        self.assertIn("error", response)
        self.assertEqual(response["error"], "Authenticated person not found.")

    def test_create_me_failure_when_authenticated_exists(self):
        self.create_default_person()
        new_person = {
            "firstName": {
                "localized": {"en_US": "Alice"},
                "preferredLocale": {"country": "US", "language": "en"},
            },
            "localizedFirstName": "Alice",
            "lastName": {
                "localized": {"en_US": "Smith"},
                "preferredLocale": {"country": "US", "language": "en"},
            },
            "localizedLastName": "Smith",
            "vanityName": "alice-smith",
        }
        response = Me.create_me(new_person)
        self.assertIn("error", response)

    def test_create_me_success_when_no_authenticated_member(self):
        LinkedinAPI.DB["current_person_id"] = None
        new_person = {
            "firstName": {
                "localized": {"en_US": "Alice"},
                "preferredLocale": {"country": "US", "language": "en"},
            },
            "localizedFirstName": "Alice",
            "lastName": {
                "localized": {"en_US": "Smith"},
                "preferredLocale": {"country": "US", "language": "en"},
            },
            "localizedLastName": "Smith",
            "vanityName": "alice-smith",
        }
        response = Me.create_me(new_person)
        self.assertIn("data", response)
        self.assertEqual(LinkedinAPI.DB["current_person_id"], response["data"]["id"])
        self.assertEqual(response["data"]["id"], "1")

    def test_update_me_failure_when_no_authenticated_member(self):
        LinkedinAPI.DB["current_person_id"] = None
        updated_person = {
            "firstName": {
                "localized": {"en_US": "Alicia"},
                "preferredLocale": {"country": "US", "language": "en"},
            },
            "localizedFirstName": "Alicia",
            "lastName": {
                "localized": {"en_US": "Smith"},
                "preferredLocale": {"country": "US", "language": "en"},
            },
            "localizedLastName": "Smith",
            "vanityName": "alice-smith",
        }
        response = Me.update_me(updated_person)
        self.assertIn("error", response)

    def test_update_me_success(self):
        self.create_default_person()
        updated_person = {
            "firstName": {
                "localized": {"en_US": "Alicia"},
                "preferredLocale": {"country": "US", "language": "en"},
            },
            "localizedFirstName": "Alicia",
            "lastName": {
                "localized": {"en_US": "Smith"},
                "preferredLocale": {"country": "US", "language": "en"},
            },
            "localizedLastName": "Smith",
            "vanityName": "alice-smith",
        }
        response = Me.update_me(updated_person)
        self.assertIn("data", response)
        self.assertEqual(response["data"]["firstName"]["localized"]["en_US"], "Alicia")

    def test_delete_me_success(self):
        self.create_default_person()
        response = Me.delete_me()
        self.assertIn("status", response)
        response = Me.get_me()
        self.assertIn("error", response)


if __name__ == "__main__":
    unittest.main()
