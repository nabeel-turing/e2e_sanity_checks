import unittest
from common_utils.base_case import BaseTestCaseWithErrorHandler
import linkedin as LinkedinAPI
from .common import reset_db


class TestOrganizations(BaseTestCaseWithErrorHandler):
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

    def test_create_organization(self):
        org_data = {
            "vanityName": "new-org",
            "name": {
                "localized": {"en_US": "New Organization"},
                "preferredLocale": {"country": "US", "language": "en"},
            },
            "primaryOrganizationType": "COMPANY",
        }
        response = LinkedinAPI.Organizations.create_organization(org_data)
        self.assertIn("data", response)
        created_org = response["data"]
        self.assertEqual(created_org["vanityName"], "new-org")
        # The first organization gets id 1.
        self.assertEqual(created_org["id"], 1)

    def test_get_organizations_by_vanity_name_success(self):
        # Create three organizations.
        self.create_org("example-org", "Example Organization")
        self.create_org("tech-inc", "Tech Incorporated")
        self.create_org("edu-foundation", "Education Foundation", org_type="NONPROFIT")
        response = LinkedinAPI.Organizations.get_organizations_by_vanity_name(
            query_field="vanityName", vanity_name="tech-inc"
        )
        self.assertIn("data", response)
        # Expect exactly one organization with vanityName "tech-inc"
        self.assertEqual(len(response["data"]), 1)
        # Since the first org gets id 1, the second organization has id 2.
        self.assertEqual(response["data"][0]["id"], 2)

    def test_get_organizations_by_vanity_name_invalid_query(self):
        self.create_org("tech-inc", "Tech Incorporated")
        response = LinkedinAPI.Organizations.get_organizations_by_vanity_name(
            query_field="invalid", vanity_name="tech-inc"
        )
        self.assertIn("error", response)

    def test_update_organization_success(self):
        org = self.create_org("tech-inc", "Tech Incorporated")
        updated_org = {
            "vanityName": "tech-inc",
            "name": {
                "localized": {"en_US": "Tech Incorporated Updated"},
                "preferredLocale": {"country": "US", "language": "en"},
            },
            "primaryOrganizationType": "COMPANY",
        }
        response = LinkedinAPI.Organizations.update_organization(
            str(org["id"]), updated_org
        )
        self.assertIn("data", response)
        self.assertEqual(
            response["data"]["name"]["localized"]["en_US"], "Tech Incorporated Updated"
        )

    def test_update_organization_failure_nonexistent(self):
        updated_org = {
            "vanityName": "nonexistent-org",
            "name": {
                "localized": {"en_US": "Nonexistent Organization"},
                "preferredLocale": {"country": "US", "language": "en"},
            },
            "primaryOrganizationType": "COMPANY",
        }
        response = LinkedinAPI.Organizations.update_organization("999", updated_org)
        self.assertIn("error", response)

    def test_delete_organization_success(self):
        org = self.create_org("tech-inc", "Tech Incorporated")
        response = LinkedinAPI.Organizations.delete_organization(str(org["id"]))
        self.assertIn("status", response)
        response = LinkedinAPI.Organizations.get_organizations_by_vanity_name(
            query_field="vanityName", vanity_name="tech-inc"
        )
        self.assertEqual(len(response["data"]), 0)

    def test_delete_organization_failure_nonexistent(self):
        response = LinkedinAPI.Organizations.delete_organization("999")
        self.assertIn("error", response)

    def test_delete_organization_by_vanity_name_success(self):
        # Create two organizations with the same vanityName.
        self.create_org("dup-org", "Dup Org 1")
        self.create_org("dup-org", "Dup Org 2")
        response = LinkedinAPI.Organizations.delete_organization_by_vanity_name(
            query_field="vanityName", vanity_name="dup-org"
        )
        self.assertIn("status", response)
        response = LinkedinAPI.Organizations.get_organizations_by_vanity_name(
            query_field="vanityName", vanity_name="dup-org"
        )
        self.assertEqual(len(response["data"]), 0)

    def test_delete_organization_by_vanity_name_failure_invalid_query(self):
        self.create_org("tech-inc", "Tech Incorporated")
        response = LinkedinAPI.Organizations.delete_organization_by_vanity_name(
            query_field="invalid", vanity_name="tech-inc"
        )
        self.assertIn("error", response)
