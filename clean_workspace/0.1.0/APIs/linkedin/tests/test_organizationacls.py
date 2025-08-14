import unittest
from common_utils.base_case import BaseTestCaseWithErrorHandler
import linkedin as LinkedinAPI
from .common import reset_db


class TestOrganizationAcls(BaseTestCaseWithErrorHandler):
    def setUp(self):
        reset_db()

    def create_default_person(self):
        """
        Create a person and mark them as the current authenticated member.
        """
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
        # With next_person_id starting at 1, the new person gets id "1".
        person["id"] = "1"
        LinkedinAPI.DB["people"]["1"] = person
        LinkedinAPI.DB["current_person_id"] = "1"
        LinkedinAPI.DB["next_person_id"] = 2
        return person

    def create_org(self, vanity_name, name_localized, org_type="COMPANY"):
        """
        Create an organization using the Organizations API.
        """
        org = {
            "vanityName": vanity_name,
            "name": {
                "localized": {"en_US": name_localized},
                "preferredLocale": {"country": "US", "language": "en"},
            },
            "primaryOrganizationType": org_type,
        }
        response = LinkedinAPI.Organizations.create_organization(org)
        self.assertIn("data", response)
        return response["data"]

    def create_acl(self, role, organization, role_assignee, state):
        """
        Create an ACL record.
        """
        acl = {
            "role": role,
            "organization": organization,
            "roleAssignee": role_assignee,
            "state": state,
        }
        response = LinkedinAPI.OrganizationAcls.create_organization_acl(acl)
        self.assertIn("data", response)
        return response["data"]

    def test_create_organization_acl(self):
        self.create_default_person()
        acl_data = {
            "role": "ADMINISTRATOR",
            "organization": "urn:li:organization:1",
            "roleAssignee": "urn:li:person:1",
            "state": "ACTIVE",
        }
        response = LinkedinAPI.OrganizationAcls.create_organization_acl(acl_data)
        self.assertIn("data", response)
        created_acl = response["data"]
        self.assertEqual(created_acl["role"], "ADMINISTRATOR")

    def test_get_organization_acls_by_role_assignee_success(self):
        self.create_default_person()
        self.create_acl("EDITOR", "urn:li:organization:1", "urn:li:person:1", "ACTIVE")
        response = LinkedinAPI.OrganizationAcls.get_organization_acls_by_role_assignee(
            query_field="roleAssignee", role_assignee="urn:li:person:1"
        )
        self.assertIn("data", response)
        self.assertTrue(len(response["data"]) >= 1)

    def test_get_organization_acls_by_role_assignee_invalid_query(self):
        self.create_default_person()
        self.create_acl("EDITOR", "urn:li:organization:1", "urn:li:person:1", "ACTIVE")
        response = LinkedinAPI.OrganizationAcls.get_organization_acls_by_role_assignee(
            query_field="invalid", role_assignee="urn:li:person:1"
        )
        self.assertIn("error", response)

    def test_update_organization_acl_success(self):
        self.create_default_person()
        acl = self.create_acl(
            "EDITOR", "urn:li:organization:1", "urn:li:person:1", "ACTIVE"
        )
        updated_acl = {
            "role": "VIEWER",
            "organization": "urn:li:organization:1",
            "roleAssignee": "urn:li:person:1",
            "state": "REQUESTED",
        }
        response = LinkedinAPI.OrganizationAcls.update_organization_acl(
            acl["aclId"], updated_acl
        )
        self.assertIn("data", response)
        self.assertEqual(response["data"]["role"], "VIEWER")

    def test_update_organization_acl_failure_nonexistent(self):
        updated_acl = {
            "role": "VIEWER",
            "organization": "urn:li:organization:1",
            "roleAssignee": "urn:li:person:1",
            "state": "REQUESTED",
        }
        response = LinkedinAPI.OrganizationAcls.update_organization_acl(
            "999", updated_acl
        )
        self.assertIn("error", response)

    def test_delete_organization_acl_success(self):
        self.create_default_person()
        acl = self.create_acl(
            "EDITOR", "urn:li:organization:1", "urn:li:person:1", "ACTIVE"
        )
        response = LinkedinAPI.OrganizationAcls.delete_organization_acl(acl["aclId"])
        self.assertIn("status", response)
        response = LinkedinAPI.OrganizationAcls.get_organization_acls_by_role_assignee(
            query_field="roleAssignee", role_assignee="urn:li:person:1"
        )
        self.assertFalse(
            any(a["aclId"] == acl["aclId"] for a in response.get("data", []))
        )

    def test_delete_organization_acl_failure_nonexistent(self):
        response = LinkedinAPI.OrganizationAcls.delete_organization_acl("999")
        self.assertIn("error", response)
