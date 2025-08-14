import os
import unittest
import hubspot as HubspotMarketingAPI
from hubspot.SimulationEngine.db import DB, save_state, load_state
from hubspot.SimulationEngine.utils import (
    generate_hubspot_object_id,
)
import hashlib
from common_utils.base_case import BaseTestCaseWithErrorHandler


# ---------------------------------------------------------------------------------------
# Unit Tests
# ---------------------------------------------------------------------------------------
class TestAPI(BaseTestCaseWithErrorHandler):

    def setUp(self):
        """Clears the DB before each test."""
        DB.update(
            {
                "transactional_emails": {},
                "marketing_emails": {},
            }
        )

    def test_transactional_sendSingleEmail(self):
        # Test successful email sending
        result = HubspotMarketingAPI.TransactionalEmails.sendSingleEmail(
            message={
                "to": "test@example.com",
                "from": "sender@example.com",
                "subject": "Test",
                "htmlBody": "<p>Hello</p>",
            }
        )
        self.assertTrue(result["success"])
        self.assertIn(result["email_id"], DB["transactional_emails"])

        # Test missing required fields
        result = HubspotMarketingAPI.TransactionalEmails.sendSingleEmail(
            message={"to": "test@example.com"}
        )
        self.assertFalse(result["success"])
        self.assertIn(
            "Message must contain 'to', 'from', 'subject', and 'htmlBody'.",
            result["message"],
        )

        del DB["transactional_emails"]
        result = HubspotMarketingAPI.TransactionalEmails.sendSingleEmail(
            message={
                "to": "test@example.com",
                "from": "sender@example.com",
                "subject": "Test",
                "htmlBody": "<p>Hello</p>",
            }
        )
        self.assertTrue(result["success"])

    def test_marketing_create(self):
        result = HubspotMarketingAPI.MarketingEmails.create(name="Test Email")
        self.assertTrue(result["success"])
        self.assertTrue(result["email_id"])
        self.assertEqual(
            DB["marketing_emails"][result["email_id"]]["name"], "Test Email"
        )

        result = HubspotMarketingAPI.MarketingEmails.create(name="")
        self.assertFalse(result["success"])
        self.assertIn("Name must be a non-empty string.", result["message"])

    def test_marketing_getById(self):
        result = HubspotMarketingAPI.MarketingEmails.create(
            name="Test Email", subject="Test Subject"
        )
        email = HubspotMarketingAPI.MarketingEmails.getById(result["email_id"])
        self.assertEqual(email["name"], "Test Email")
        self.assertEqual(email["subject"], "Test Subject")

        # test non existant id
        email = HubspotMarketingAPI.MarketingEmails.getById(999)
        self.assertIsNone(email)

        # test invalid id type
        result = HubspotMarketingAPI.MarketingEmails.getById("abc")
        self.assertEqual(None, result)

    def test_marketing_update(self):
        result = HubspotMarketingAPI.MarketingEmails.create(
            name="Test Email", subject="Test Subject"
        )
        id = result["email_id"]
        result = HubspotMarketingAPI.MarketingEmails.update(
            id, subject="Updated Subject"
        )
        self.assertTrue(result["success"])
        self.assertEqual(DB["marketing_emails"][id]["subject"], "Updated Subject")

        # Test updating a non-existent email
        result = HubspotMarketingAPI.MarketingEmails.update(
            999, subject="Updated Subject"
        )
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Marketing email not found.")

        result = HubspotMarketingAPI.MarketingEmails.update(
            "abc", subject="Updated Subject"
        )
        self.assertFalse(result["success"])
        self.assertIn("Marketing email not found.", result["message"])

    def test_marketing_delete(self):
        result = HubspotMarketingAPI.MarketingEmails.create(name="Test Email")
        id = result["email_id"]
        result = HubspotMarketingAPI.MarketingEmails.delete(id)
        self.assertTrue(result["success"])
        self.assertNotIn(id, DB["marketing_emails"])

        # Test deleting a non-existent email
        result = HubspotMarketingAPI.MarketingEmails.delete(999)
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Marketing email not found.")

        result = HubspotMarketingAPI.MarketingEmails.delete("abc")
        self.assertFalse(result["success"])
        self.assertIn("Marketing email not found.", result["message"])

    def test_marketing_clone(self):
        original = HubspotMarketingAPI.MarketingEmails.create(
            name="Original Email", subject="Original Subject"
        )
        result = HubspotMarketingAPI.MarketingEmails.clone(
            original["email_id"], name="Cloned Email"
        )
        result_id = result["email_id"]
        self.assertTrue(result["success"])
        self.assertEqual(DB["marketing_emails"][result_id]["name"], "Cloned Email")
        self.assertEqual(
            DB["marketing_emails"][result_id]["subject"], "Original Subject"
        )  # check subject remains

        # test invalid ID
        result = HubspotMarketingAPI.MarketingEmails.clone(999, name="Cloned Email")
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Marketing email not found.")

        result = HubspotMarketingAPI.MarketingEmails.clone("abc", name="abc")
        self.assertFalse(result["success"])
        self.assertIn("Marketing email not found.", result["message"])

        result = HubspotMarketingAPI.MarketingEmails.clone(email_id=1, name="")
        self.assertFalse(result["success"])
        self.assertIn("Marketing email not found.", result["message"])

    def test_save_and_load_state(self):
        # Create some data
        result_1 = HubspotMarketingAPI.TransactionalEmails.sendSingleEmail(
            message={
                "to": "test@example.com",
                "from": "me@example.com",
                "subject": "test",
                "htmlBody": "body",
            }
        )
        result_2 = HubspotMarketingAPI.MarketingEmails.create(
            name="Test Marketing Email"
        )

        # Save the state
        save_state("test_state.json")

        # Clear the DB
        DB.update(
            {
                "transactional_emails": {},
                "marketing_emails": {},
            }
        )

        # Load the state
        load_state("test_state.json")

        # Check if data was restored correctly
        id = str(result_2["email_id"])
        self.assertIn(result_1["email_id"], DB["transactional_emails"])
        self.assertIn(id, DB["marketing_emails"])
        self.assertEqual(DB["marketing_emails"][id]["name"], "Test Marketing Email")

        # test load from invalid filepath
        load_state("invalid_file.json")  # File doesn't exist
        # Check that DB is still valid after FileNotFoundError
        self.assertIn("transactional_emails", DB)
        self.assertIn("marketing_emails", DB)

        # test save_state with invalid filepath
        with self.assertRaises(IOError) as context:
            save_state("/invalid/path/to/file.json")  # invalid path
        os.remove("test_state.json")


class TestSingleSendAPI(BaseTestCaseWithErrorHandler):
    def setUp(self):
        """Setup method to prepare for each test."""
        DB.update(
            {
                "transactional_emails": {},
                "email_templates": {},
                "contacts": {},
                "marketing_emails": {},
            }
        )  # Reset DB
        self.api = HubspotMarketingAPI.SingleSend
        # Pre-populate with a sample email template
        DB["email_templates"]["template_1"] = {
            "subject": "Welcome!",
            "body": "Hello, {name}!",
        }
        # Pre-populate with a sample contact
        DB["contacts"]["test@example.com"] = {
            "name": "Test User",
            "company": "Example Corp",
        }
        DB["contacts"]["test2@example.com"] = {"name": "Test User 2"}

    def test_sendSingleEmail_success(self):
        """Test successful email sending."""
        to = [{"email": "test@example.com"}]
        from_ = {"email": "sender@example.com", "name": "Sender"}
        message = {"to": to, "cc": None, "bcc": None, "from": from_, "replyTo": None}
        template = HubspotMarketingAPI.Templates.create_template(
            source="Trial Template"
        )
        template_id = template["id"]
        response = self.api.sendSingleEmail(
            template_id, message=message, customProperties={"city": "Boston"}
        )
        self.assertEqual(response["status"], "success")
        self.assertEqual(len(DB["transactional_emails"]), 1)
        # Check for the transactional email ID in the response and DB
        txn_id = response["transactional_email_id"]
        self.assertIn(txn_id, DB["transactional_emails"])
        self.assertEqual(DB["transactional_emails"][txn_id]["template_id"], template_id)
        self.assertEqual(DB["transactional_emails"][txn_id]["message"], message)
        # Check if properties were merged correctly
        self.assertEqual(
            DB["transactional_emails"][txn_id]["properties"],
            {"name": "Test User", "company": "Example Corp", "city": "Boston"},
        )

    def test_sendSingleEmail_success_contact_properties(self):
        """Test successful email sending with contact and custom properties."""
        message = {
            "to": [{"email": "test@example.com"}],  # Contact exists
            "from": {"email": "sender@example.com", "name": "Sender"},
        }

        to = [{"email": "test@example.com"}]
        from_ = {"email": "sender@example.com", "name": "Sender"}
        # custom and contact props, contact props should take precedence
        template = HubspotMarketingAPI.Templates.create_template(
            source="Trial Template 1"
        )
        template_id = template["id"]
        response = self.api.sendSingleEmail(
            template_id,
            message=message,
            customProperties={"name": "Custom Name"},
            contactProperties={"name": "Contact Name"},
        )
        self.assertEqual(response["status"], "success")
        txn_id = response["transactional_email_id"]
        self.assertEqual(
            DB["transactional_emails"][txn_id]["properties"]["name"], "Contact Name"
        )  # contact name takes precedence

    def test_sendSingleEmail_success_multiple_recipients(self):
        """Test with multiple recipients, each having contact data."""
        message = {
            "to": [{"email": "test@example.com"}, {"email": "test2@example.com"}],
            "from": {"email": "sender@example.com"},
        }

        template = HubspotMarketingAPI.Templates.create_template(
            source="Trial Template 2"
        )
        template_id = template["id"]
        to = [{"email": "test@example.com"}, {"email": "test2@example.com"}]
        from_ = {"email": "sender@example.com", "name": "Sender"}
        response = self.api.sendSingleEmail(
            template_id, message=message, customProperties={"city": "Boston"}
        )
        self.assertEqual(response["status"], "success")
        self.assertEqual(
            len(DB["transactional_emails"]), 1
        )  # Still one send, but properties are correct
        txn_id = response["transactional_email_id"]
        # Verify properties (should be from the *first* contact if no recipient-specific handling)
        self.assertEqual(
            DB["transactional_emails"][txn_id]["properties"]["name"], "Test User 2"
        )
        self.assertEqual(
            DB["transactional_emails"][txn_id]["properties"]["city"], "Boston"
        )
        self.assertIn("company", DB["transactional_emails"][txn_id]["properties"])

    def test_sendSingleEmail_template_not_found(self):
        """Test sending email with a non-existent template ID."""
        message = {
            "to": [{"email": "test@example.com"}],
            "from": {"email": "sender@example.com"},
        }
        to = [{"email": "test@example.com"}]
        from_ = {"email": "sender@example.com", "name": "Sender"}
        response = self.api.sendSingleEmail("invalid_template", message=message)
        self.assertEqual(response["status"], "error")
        self.assertEqual(
            response["message"], "Email template with ID 'invalid_template' not found."
        )
        self.assertEqual(
            len(DB["transactional_emails"]), 0
        )  # Ensure no email was logged as sent

    def test_sendSingleEmail_invalid_input(self):
        """Test sending email with invalid input (missing 'to' field)."""
        template = HubspotMarketingAPI.Templates.create_template(
            source="Test Template 1"
        )
        template_id = template["id"]

        result = self.api.sendSingleEmail(template_id, {})  # Missing 'to'
        self.assertTrue(
            "'template_id' and 'message' are required." in result["message"]
        )

        result_2 = self.api.sendSingleEmail(template_id, {"to": []})  # Missing 'to'
        self.assertTrue("'to' entry must be a dictionary" in result_2["message"])

        result_3 = self.api.sendSingleEmail(
            template_id, {"to": [{"email": ""}]}
        )  # invalid to
        self.assertTrue(
            "Each 'to' entry must be a dictionary with a non-empty 'email' string."
            in result_3["message"]
        )

        result_4 = self.api.sendSingleEmail(
            template_id, {"to": [{"email": "asd@asd"}], "from": "invalid"}
        )  # invalid from
        self.assertTrue(
            "'from' field must be a dictionary with 'email' and 'name' properties."
            in result_4["message"]
        )

    def test_sendSingleEmail_no_contact(self):
        """Test email sending when a contact doesn't exist in the DB."""
        message = {
            "to": [{"email": "nonexistent@example.com"}],  # This contact doesn't exist
            "from": {"email": "sender@example.com", "name": "Sender"},
        }
        to = [{"email": "nonexistent@example.com"}]
        from_ = {"email": "sender@example.com", "name": "Sender"}

        template = HubspotMarketingAPI.Templates.create_template(
            source="Test Template 2"
        )
        template_id = template["id"]
        response = self.api.sendSingleEmail(
            template_id, message=message, customProperties={"city": "Boston"}
        )
        self.assertEqual(response["status"], "success")
        txn_id = response["transactional_email_id"]
        # When there's no contact, custom properties should be used
        self.assertEqual(
            DB["transactional_emails"][txn_id]["properties"], {"city": "Boston"}
        )

    def test_sendSingleEmail_empty_contact_properties(self):
        """Test email sending when contact exist but has no properties"""
        DB["contacts"][
            "empty_contact@example.com"
        ] = {}  # add contact with no properties
        message = {
            "to": [{"email": "empty_contact@example.com"}],
            "from": {"email": "sender@example.com", "name": "Sender"},
        }

        to = [{"email": "empty_contact@example.com"}]
        from_ = {"email": "sender@example.com", "name": "Sender"}

        template = HubspotMarketingAPI.Templates.create_template(
            source="Test Template 3"
        )
        template_id = template["id"]
        response = self.api.sendSingleEmail(
            template_id, message=message, customProperties={"city": "Boston"}
        )
        self.assertEqual(response["status"], "success")
        txn_id = response["transactional_email_id"]
        # Only custom properties should be used
        self.assertEqual(
            DB["transactional_emails"][txn_id]["properties"], {"city": "Boston"}
        )

    def test_sendSingleEmail_contact_and_custom_properties_merge(self):
        """Test correct merging of contact and custom properties, contact properties overriding custom properties."""
        message = {
            "to": [{"email": "test@example.com"}],  # Contact exists for this email
            "from": {"email": "sender@example.com", "name": "Sender"},
        }

        to = [{"email": "test@example.com"}]
        from_ = {"email": "sender@example.com", "name": "Sender"}
        # Both customProperties and contactProperties are set, contact should take precedence
        template = HubspotMarketingAPI.Templates.create_template(
            source="Test Template 4"
        )
        template_id = template["id"]
        response = self.api.sendSingleEmail(
            template_id,
            message=message,
            customProperties={
                "city": "Boston",
                "name": "Should Not Appear",
            },  # Will be masked by contact prop
            contactProperties={"role": "Manager"},  # Additional contact prop
        )
        self.assertEqual(response["status"], "success")
        txn_id = response["transactional_email_id"]
        # Properties should be merged correctly, with contact props overriding custom props
        properties = DB["transactional_emails"][txn_id]["properties"]
        self.assertEqual(
            properties["name"], "Test User"
        )  # From contact, not custom prop
        self.assertEqual(properties["company"], "Example Corp")  # From contact
        self.assertEqual(properties["city"], "Boston")  # From custom prop
        self.assertEqual(properties["role"], "Manager")  # From contact prop override

    def test_sendSingleEmail_cc_bcc_replyTo(self):
        message = {
            "to": [{"email": "test@example.com"}],
            "from": {"email": "sender@example.com", "name": "Sender"},
            "cc": [{"email": "cc@example.com"}],
            "bcc": [{"email": "bcc@example.com"}],
            "replyTo": [{"email": "replyTo@example.com"}],
        }

        template = HubspotMarketingAPI.Templates.create_template(
            source="Test Template 5"
        )
        template_id = template["id"]
        response = self.api.sendSingleEmail(template_id, message=message)
        self.assertEqual(response["status"], "success")
        txn_id = response["transactional_email_id"]
        self.assertEqual(
            DB["transactional_emails"][txn_id]["message"]["cc"],
            [{"email": "cc@example.com"}],
        )
        self.assertEqual(
            DB["transactional_emails"][txn_id]["message"]["bcc"],
            [{"email": "bcc@example.com"}],
        )
        self.assertEqual(
            DB["transactional_emails"][txn_id]["message"]["replyTo"],
            [{"email": "replyTo@example.com"}],
        )

        message["cc"] = [{"mailid": "cc2@example.com"}]

        response = self.api.sendSingleEmail(template_id, message=message)
        self.assertEqual(response["status"], "error")
        self.assertEqual(
            response["message"],
            "Each 'cc' entry must be a dictionary with a non-empty 'email' string.",
        )

        message["cc"] = [{"email": "cc2@example.com"}]
        message["bcc"] = [{"mailid": "bcc2@example.com"}]

        response = self.api.sendSingleEmail(template_id, message=message)
        self.assertEqual(response["status"], "error")
        self.assertEqual(
            response["message"],
            "Each 'bcc' entry must be a dictionary with a non-empty 'email' string.",
        )

        message["bcc"] = [{"email": "bcc2@example.com"}]
        message["replyTo"] = [{"mailid": "replyTo2@example.com"}]

        response = self.api.sendSingleEmail(template_id, message=message)
        self.assertEqual(response["status"], "error")
        self.assertEqual(
            response["message"],
            "Each 'replyTo' entry must be a dictionary with a non-empty 'email' string.",
        )

        message["replyTo"] = [{"email": "replyTo2@example.com"}]
        del DB["templates"]
        response = self.api.sendSingleEmail(template_id, message=message)
        self.assertEqual(response["status"], "error")
        self.assertEqual(
            response["message"], f"Email template with ID '{template_id}' not found."
        )

        template = HubspotMarketingAPI.Templates.create_template(
            source="Test Template 6", template_type=11
        )
        response = self.api.sendSingleEmail(template["id"], message=message)
        self.assertEqual(response["status"], "error")
        self.assertEqual(
            response["message"],
            f"Template with ID '{template['id']}' is not an email template.",
        )


class TestCampaignsAPI(BaseTestCaseWithErrorHandler):

    def setUp(self):
        """Setup method to prepare for each test."""
        DB.update(
            {
                "campaigns": {
                    "1": {
                        "id": "1",
                        "name": "Campaign A",
                        "type": "EMAIL",
                        "createdAt": "2023-01-01T12:00:00Z",
                        "updatedAt": "2023-01-02T12:00:00Z",
                    },
                    "2": {
                        "id": "2",
                        "name": "Campaign B",
                        "type": "SOCIAL",
                        "createdAt": "2023-01-05T12:00:00Z",
                        "updatedAt": "2023-01-06T12:00:00Z",
                    },
                    "3": {
                        "id": "3",
                        "name": "Campaign C",
                        "type": "EMAIL",
                        "createdAt": "2023-01-10T12:00:00Z",
                        "updatedAt": "2023-01-11T12:00:00Z",
                    },
                }
            }
        )

    def test_get_campaigns_no_filters(self):
        result = HubspotMarketingAPI.Campaigns.get_campaigns()
        self.assertEqual(len(result["results"]), 3)
        self.assertEqual(result["total"], 3)
        self.assertIsNone(result["limit"])
        self.assertIsNone(result["offset"])

    def test_get_campaigns_limit(self):
        result = HubspotMarketingAPI.Campaigns.get_campaigns(limit=1)
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["total"], 3)
        self.assertEqual(result["limit"], 1)
        self.assertIsNone(result["offset"])

    def test_get_campaigns_offset(self):
        result = HubspotMarketingAPI.Campaigns.get_campaigns(offset=1)
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["total"], 3)
        self.assertIsNone(result["limit"])
        self.assertEqual(result["offset"], 1)

    def test_get_campaigns_limit_and_offset(self):
        result = HubspotMarketingAPI.Campaigns.get_campaigns(limit=1, offset=1)
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["id"], "2")
        self.assertEqual(result["total"], 3)
        self.assertEqual(result["limit"], 1)
        self.assertEqual(result["offset"], 1)

    def test_get_campaigns_id(self):
        result = HubspotMarketingAPI.Campaigns.get_campaigns(id="1")
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["id"], "1")

    def test_get_campaigns_name(self):
        result = HubspotMarketingAPI.Campaigns.get_campaigns(name="Campaign B")
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["id"], "2")

    def test_get_campaigns_type(self):
        result = HubspotMarketingAPI.Campaigns.get_campaigns(type="EMAIL")
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["id"], "1")
        self.assertEqual(result["results"][1]["id"], "3")

    def test_get_all_campaigns(self):
        """Test retrieving all campaigns without filters."""
        response = HubspotMarketingAPI.Campaigns.get_campaigns()
        self.assertEqual(response["total"], 3)
        self.assertEqual(len(response["results"]), 3)

    def test_get_campaigns_by_id(self):
        """Test retrieving campaign by id filter."""
        response = HubspotMarketingAPI.Campaigns.get_campaigns(id="2")
        self.assertEqual(response["total"], 1)
        self.assertEqual(response["results"][0]["name"], "Campaign B")

    def test_get_campaigns_by_name(self):
        """Test retrieving campaign by name filter."""
        response = HubspotMarketingAPI.Campaigns.get_campaigns(name="Campaign A")
        self.assertEqual(response["total"], 1)
        self.assertEqual(response["results"][0]["id"], "1")

    def test_get_campaigns_by_type(self):
        """Test retrieving campaigns by type filter."""
        response = HubspotMarketingAPI.Campaigns.get_campaigns(type="EMAIL")
        self.assertEqual(response["total"], 2)
        campaign_names = [c["name"] for c in response["results"]]
        self.assertIn("Campaign A", campaign_names)
        self.assertIn("Campaign C", campaign_names)

    def test_get_campaigns_with_pagination(self):
        """Test pagination with limit and offset."""
        response = HubspotMarketingAPI.Campaigns.get_campaigns(limit=2)
        self.assertEqual(len(response["results"]), 2)
        self.assertEqual(response["limit"], 2)
        self.assertEqual(response["offset"], None)

        response = HubspotMarketingAPI.Campaigns.get_campaigns(offset=1)
        self.assertEqual(len(response["results"]), 2)
        self.assertEqual(response["offset"], 1)

        response = HubspotMarketingAPI.Campaigns.get_campaigns(limit=1, offset=1)
        self.assertEqual(len(response["results"]), 1)
        self.assertEqual(response["results"][0]["id"], "2")

    def test_get_campaigns_empty_result(self):
        """Test with filter resulting in empty list."""
        response = HubspotMarketingAPI.Campaigns.get_campaigns(
            name="Non Existent Campaign"
        )
        self.assertEqual(response["total"], 0)
        self.assertEqual(response["results"], [])

    def test_get_campaigns_no_filter(self):
        campaigns = HubspotMarketingAPI.Campaigns.get_campaigns()
        self.assertEqual(len(campaigns["results"]), 3)
        self.assertEqual(campaigns["total"], 3)
        self.assertIsNone(campaigns["limit"])
        self.assertIsNone(campaigns["offset"])

    def test_get_campaigns_with_limit(self):
        campaigns = HubspotMarketingAPI.Campaigns.get_campaigns(limit=2)
        self.assertEqual(len(campaigns["results"]), 2)
        self.assertEqual(campaigns["total"], 3)
        self.assertEqual(campaigns["limit"], 2)
        self.assertIsNone(campaigns["offset"])

    def test_get_campaigns_with_offset(self):
        campaigns = HubspotMarketingAPI.Campaigns.get_campaigns(offset=1)
        self.assertEqual(len(campaigns["results"]), 2)
        self.assertEqual(campaigns["total"], 3)
        self.assertIsNone(campaigns["limit"])
        self.assertEqual(campaigns["offset"], 1)

    def test_get_campaigns_with_limit_and_offset(self):
        campaigns = HubspotMarketingAPI.Campaigns.get_campaigns(limit=1, offset=1)
        self.assertEqual(len(campaigns["results"]), 1)
        self.assertEqual(campaigns["total"], 3)
        self.assertEqual(campaigns["limit"], 1)
        self.assertEqual(campaigns["offset"], 1)

    def test_get_campaigns_with_id_filter(self):
        campaigns = HubspotMarketingAPI.Campaigns.get_campaigns(id="2")
        self.assertEqual(len(campaigns["results"]), 1)
        self.assertEqual(campaigns["results"][0]["id"], "2")

    def test_get_campaigns_with_name_filter(self):
        campaigns = HubspotMarketingAPI.Campaigns.get_campaigns(name="Campaign A")
        self.assertEqual(len(campaigns["results"]), 1)
        self.assertEqual(campaigns["results"][0]["name"], "Campaign A")

    def test_get_campaigns_with_type_filter(self):
        campaigns = HubspotMarketingAPI.Campaigns.get_campaigns(type="EMAIL")
        self.assertEqual(len(campaigns["results"]), 2)
        self.assertTrue(all(c["type"] == "EMAIL" for c in campaigns["results"]))

    def test_create_campaign(self):
        new_campaign = HubspotMarketingAPI.Campaigns.create_campaign(
            name="New Campaign"
        )
        self.assertEqual(new_campaign["name"], "New Campaign")
        self.assertIn(new_campaign["id"], DB["campaigns"])

    def test_get_campaign(self):
        campaign = HubspotMarketingAPI.Campaigns.get_campaign("1")
        self.assertEqual(campaign["id"], "1")
        self.assertEqual(campaign["name"], "Campaign A")

    def test_update_campaign(self):
        updated_campaign = HubspotMarketingAPI.Campaigns.update_campaign(
            "1", name="Updated Campaign", description="Updated Description"
        )
        self.assertEqual(updated_campaign["name"], "Updated Campaign")
        self.assertEqual(updated_campaign["description"], "Updated Description")
        self.assertEqual(DB["campaigns"]["1"]["name"], "Updated Campaign")
        self.assertEqual(DB["campaigns"]["1"]["description"], "Updated Description")

        updated_campaign = HubspotMarketingAPI.Campaigns.update_campaign(
            "1",
            name="Updated Campaign",
            description="Updated Description",
            slug="updated-campaign",
            start_year=2024,
            start_month=1,
            start_day=1,
            end_year=2024,
            end_month=1,
            end_day=1,
            theme="Updated Theme",
            resource="Updated Resource",
            color_label="Updated Color Label",
        )
        self.assertEqual(updated_campaign["name"], "Updated Campaign")
        self.assertEqual(updated_campaign["description"], "Updated Description")
        self.assertEqual(updated_campaign["start_year"], 2024)
        self.assertEqual(updated_campaign["start_month"], 1)
        self.assertEqual(updated_campaign["start_day"], 1)

        invalid_campaign = HubspotMarketingAPI.Campaigns.update_campaign(
            "999", name="Invalid Campaign"
        )
        self.assertIsNone(invalid_campaign)

    def test_archive_campaign(self):
        result = HubspotMarketingAPI.Campaigns.archive_campaign("1")
        self.assertTrue(result)
        self.assertTrue(DB["campaigns"]["1"].get("is_archived", False))

    def test_archive_campaign_nonexistent(self):
        result = HubspotMarketingAPI.Campaigns.archive_campaign("4")
        self.assertFalse(result)


class TestFormsAPI(BaseTestCaseWithErrorHandler):

    def setUp(self):
        """Setup method to prepare for each test."""
        DB.update(
            {
                "forms": {
                    "1": {
                        "id": "1",
                        "name": "Form A",
                        "submitText": "Submit A",
                        "fieldGroups": [],
                        "legalConsentOptions": {},
                        "createdAt": "2023-01-01T12:00:00Z",
                        "updatedAt": "2023-01-01T12:00:00Z",
                    },
                    "2": {
                        "id": "2",
                        "name": "Form B",
                        "submitText": "Submit B",
                        "fieldGroups": [],
                        "legalConsentOptions": {},
                        "createdAt": "2023-01-05T12:00:00Z",
                        "updatedAt": "2023-01-05T12:00:00Z",
                    },
                    "3": {
                        "id": "3",
                        "name": "Form C",
                        "submitText": "Submit C",
                        "fieldGroups": [],
                        "legalConsentOptions": {},
                        "createdAt": "2023-01-10T12:00:00Z",
                        "updatedAt": "2023-01-10T12:00:00Z",
                    },
                }
            }
        )

    def test_get_forms_no_filters(self):
        result = HubspotMarketingAPI.Forms.get_forms()
        self.assertEqual(len(result["results"]), 3)
        self.assertEqual(result["total"], 3)
        self.assertIsNone(result.get("paging"))

    def test_get_forms_limit(self):
        result = HubspotMarketingAPI.Forms.get_forms(limit=1)
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["total"], 3)
        self.assertIsNotNone(result.get("paging"))  # Should have paging info
        self.assertEqual(result["paging"]["next"]["after"], "1")

    def test_get_forms_after(self):
        result = HubspotMarketingAPI.Forms.get_forms(after="1")
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["total"], 3)
        self.assertEqual(result["results"][0]["id"], "2")
        self.assertIsNone(result.get("paging"))

    def test_get_forms_after_and_limit(self):
        result = HubspotMarketingAPI.Forms.get_forms(after="1", limit=1)
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["id"], "2")
        self.assertEqual(result["total"], 3)
        self.assertIsNotNone(result.get("paging"))
        self.assertEqual(result["paging"]["next"]["after"], "2")

    def test_get_forms_after_not_found(self):
        # Test case where 'after' ID is not found
        result = HubspotMarketingAPI.Forms.get_forms(after="999")
        self.assertEqual(len(result["results"]), 0)
        self.assertEqual(result["total"], 3)  # Total should still be correct
        self.assertIsNone(result.get("paging"))

    def test_get_forms_created_at(self):
        result = HubspotMarketingAPI.Forms.get_forms(created_at="2023-01-05T12:00:00Z")
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["id"], "2")

    def test_get_forms_created_at_gt(self):
        result = HubspotMarketingAPI.Forms.get_forms(
            created_at__gt="2023-01-05T12:00:00Z"
        )
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["id"], "3")

    def test_get_forms_created_at_gte(self):
        result = HubspotMarketingAPI.Forms.get_forms(
            created_at__gte="2023-01-05T12:00:00Z"
        )
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["id"], "2")
        self.assertEqual(result["results"][1]["id"], "3")

    def test_get_forms_created_at_lt(self):
        result = HubspotMarketingAPI.Forms.get_forms(
            created_at__lt="2023-01-05T12:00:00Z"
        )
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["id"], "1")

    def test_get_forms_created_at_lte(self):
        result = HubspotMarketingAPI.Forms.get_forms(
            created_at__lte="2023-01-05T12:00:00Z"
        )
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["id"], "1")
        self.assertEqual(result["results"][1]["id"], "2")

    def test_get_forms_updated_at(self):
        result = HubspotMarketingAPI.Forms.get_forms(updated_at="2023-01-05T12:00:00Z")
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["id"], "2")

    def test_get_forms_updated_at_gt(self):
        result = HubspotMarketingAPI.Forms.get_forms(
            updated_at__gt="2023-01-05T12:00:00Z"
        )
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["id"], "3")

    def test_get_forms_updated_at_gte(self):
        result = HubspotMarketingAPI.Forms.get_forms(
            updated_at__gte="2023-01-05T12:00:00Z"
        )
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["id"], "2")
        self.assertEqual(result["results"][1]["id"], "3")

    def test_get_forms_updated_at_lt(self):
        result = HubspotMarketingAPI.Forms.get_forms(
            updated_at__lt="2023-01-05T12:00:00Z"
        )
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["id"], "1")

    def test_get_forms_updated_at_lte(self):
        result = HubspotMarketingAPI.Forms.get_forms(
            updated_at__lte="2023-01-05T12:00:00Z"
        )
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["id"], "1")
        self.assertEqual(result["results"][1]["id"], "2")

    def test_get_forms_name(self):
        result = HubspotMarketingAPI.Forms.get_forms(name="Form B")
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["name"], "Form B")

    def test_get_forms_id(self):
        result = HubspotMarketingAPI.Forms.get_forms(id="2")
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["id"], "2")

    def test_create_form(self):
        new_form_data = {
            "name": "New Form",
            "submitText": "Submit Now",
            "fieldGroups": [
                {"fields": [{"name": "email", "label": "Email", "type": "string"}]}
            ],
            "legalConsentOptions": {"consentToProcess": True},
        }
        created_form = HubspotMarketingAPI.Forms.create_form(
            **new_form_data
        )  # Use keyword arguments
        self.assertIn("id", created_form)
        self.assertEqual(created_form["name"], "New Form")
        self.assertEqual(len(DB["forms"]), 4)  # Check if added to DB
        self.assertEqual(
            DB["forms"][created_form["id"]]["name"], "New Form"
        )  # Check DB directly

    def test_get_form(self):
        form = HubspotMarketingAPI.Forms.get_form("1")
        self.assertEqual(form["id"], "1")
        self.assertEqual(form["name"], "Form A")

    def test_get_form_not_found(self):
        with self.assertRaises(ValueError) as context:  # Use assertRaises correctly
            HubspotMarketingAPI.Forms.get_form("999")  # ID that doesn't exist
        self.assertEqual(str(context.exception), "Form with id '999' not found")

    def test_update_form(self):
        updated_form = HubspotMarketingAPI.Forms.update_form(
            "1", name="Updated Form A", submitText="New Submit"
        )
        self.assertEqual(updated_form["name"], "Updated Form A")
        self.assertEqual(updated_form["submitText"], "New Submit")
        self.assertEqual(DB["forms"]["1"]["name"], "Updated Form A")  # Check DB

    def test_update_form_not_found(self):
        with self.assertRaises(ValueError) as context:
            HubspotMarketingAPI.Forms.update_form("99", name="This won't work")
        self.assertEqual(str(context.exception), "Form with ID '99' not found.")

    def test_update_form_field_groups(self):
        updated_form = HubspotMarketingAPI.Forms.update_form(
            "1",
            fieldGroups=[
                {"fields": [{"name": "email", "label": "Email", "type": "string"}]}
            ],
            legalConsentOptions={"consentToProcess": True},
        )
        self.assertEqual(updated_form["fieldGroups"][0]["fields"][0]["name"], "email")
        self.assertEqual(updated_form["legalConsentOptions"]["consentToProcess"], True)

    def test_delete_form(self):
        HubspotMarketingAPI.Forms.delete_form("1")
        self.assertNotIn("1", DB["forms"])  # Check if removed from DB
        self.assertEqual(len(DB["forms"]), 2)

    def test_delete_form_not_found(self):
        result = HubspotMarketingAPI.Forms.delete_form("999")
        self.assertEqual(result["error"], "Form with ID '999' not found.")


class TestFormGlobalEventsAPI(BaseTestCaseWithErrorHandler):

    def setUp(self):
        """Setup method to prepare for each test."""
        DB.update(
            {
                "subscription_definitions": [
                    {
                        "id": 1,
                        "name": "form.submission",
                        "description": "Form submission event",
                    }
                ],
                "subscriptions": {
                    1: {
                        "id": 1,
                        "endpoint": "https://example.com/webhook1",
                        "subscriptionDetails": {},
                        "active": True,
                    },
                    2: {
                        "id": 2,
                        "endpoint": "https://example.com/webhook2",
                        "subscriptionDetails": {},
                        "active": False,
                    },
                },
            }
        )

    def test_get_subscription_definitions(self):
        definitions = (
            HubspotMarketingAPI.FormGlobalEvents.get_subscription_definitions()
        )
        self.assertEqual(len(definitions), 1)
        self.assertEqual(definitions[0]["name"], "form.submission")

    def test_create_subscription(self):
        new_subscription = HubspotMarketingAPI.FormGlobalEvents.create_subscription(
            endpoint="https://example.com/new",
            subscriptionDetails={"subscriptionType": "form.submission"},
        )
        id = new_subscription["id"]
        self.assertIn("id", new_subscription)
        self.assertEqual(new_subscription["endpoint"], "https://example.com/new")
        self.assertTrue(new_subscription["active"])
        self.assertEqual(len(DB["subscriptions"]), 3)  # Check if added
        self.assertEqual(DB["subscriptions"][id]["endpoint"], "https://example.com/new")

    def test_get_subscriptions(self):
        subscriptions = HubspotMarketingAPI.FormGlobalEvents.get_subscriptions()
        self.assertEqual(len(subscriptions), 2)
        self.assertEqual(subscriptions[0]["endpoint"], "https://example.com/webhook1")
        self.assertEqual(subscriptions[1]["endpoint"], "https://example.com/webhook2")

    def test_delete_subscription(self):
        HubspotMarketingAPI.FormGlobalEvents.delete_subscription(1)
        self.assertEqual(len(DB["subscriptions"]), 1)
        self.assertNotIn(1, DB["subscriptions"])

    def test_delete_subscription_not_found(self):
        with self.assertRaises(ValueError) as context:
            HubspotMarketingAPI.FormGlobalEvents.delete_subscription(999)
        self.assertEqual(str(context.exception), "Subscription with id '999' not found")

    def test_update_subscription(self):
        updated_subscription = HubspotMarketingAPI.FormGlobalEvents.update_subscription(
            1, False
        )
        self.assertFalse(updated_subscription["active"])
        self.assertFalse(DB["subscriptions"][1]["active"])  # Check DB

        updated_subscription = HubspotMarketingAPI.FormGlobalEvents.update_subscription(
            1, True
        )
        self.assertTrue(updated_subscription["active"])
        self.assertTrue(DB["subscriptions"][1]["active"])

    def test_update_subscription_not_found(self):
        with self.assertRaises(ValueError) as context:
            HubspotMarketingAPI.FormGlobalEvents.update_subscription(99, True)
        self.assertEqual(str(context.exception), "Subscription with id '99' not found")

    def test_update_subscription_invalid_type(self):
        with self.assertRaises(ValueError) as context:
            HubspotMarketingAPI.FormGlobalEvents.update_subscription(
                "abc", True
            )  # string ID
        # self.assertTrue("invalid literal for int()" in str(context.exception)) # Removed, ValueError is enough

    def test_delete_subscription_invalid_type(self):
        with self.assertRaises(ValueError) as context:
            HubspotMarketingAPI.FormGlobalEvents.delete_subscription("abc")  # string ID
        # self.assertTrue("invalid literal for int()" in str(context.exception)) # Removed, ValueError is enough


class TestMarketingEvents(BaseTestCaseWithErrorHandler):
    """Tests for the MarketingEvents class."""

    def setUp(self):
        """Set up the test environment."""
        DB.update(
            {
                "marketing_events": {},
                "attendees": {},
                "transactional_emails": {},
                "templates": {},
                "contacts": {},
                "marketing_emails": {},
                "campaigns": {},
                "forms": {},
                "subscription_definitions": [],
                "subscriptions": {},
            }
        )
        self.event_id = "event123"
        self.account_id = "account456"
        self.attendee_email = "test@example.com"
        self.attendee_id = hashlib.sha256(
            f"{self.event_id}-{self.attendee_email}".encode()
        ).hexdigest()[:8]

    def test_get_events(self):
        """Test getting all marketing events."""
        HubspotMarketingAPI.MarketingEvents.create_event(
            self.event_id, self.account_id, "Test Event", "Webinar", "Organizer"
        )
        events = HubspotMarketingAPI.MarketingEvents.get_events()
        self.assertEqual(len(events["results"]), 1)
        self.assertEqual(events["results"][0]["eventName"], "Test Event")

    def test_create_event(self):
        """Test creating a marketing event."""
        event = HubspotMarketingAPI.MarketingEvents.create_event(
            self.event_id, self.account_id, "Test Event", "Webinar", "Organizer"
        )
        self.assertEqual(event["eventName"], "Test Event")
        self.assertEqual(event["externalEventId"], self.event_id)
        self.assertEqual(event["externalAccountId"], self.account_id)
        self.assertIn(self.event_id, DB["marketing_events"])

        event = HubspotMarketingAPI.MarketingEvents.create_event(
            externalEventId=None,
            externalAccountId=self.account_id,
            event_name="Test Event",
            event_type="Webinar",
            event_organizer="Organizer",
        )
        self.assertEqual(event["error"], "External Event ID is required.")

        event = HubspotMarketingAPI.MarketingEvents.create_event(
            externalEventId=self.event_id,
            externalAccountId=None,
            event_name="Test Event",
            event_type="Webinar",
            event_organizer="Organizer",
        )
        self.assertEqual(event["error"], "External Account ID is required.")

    def test_get_event(self):
        """Test getting a marketing event."""
        HubspotMarketingAPI.MarketingEvents.create_event(
            self.event_id, self.account_id, "Test Event", "Webinar", "Organizer"
        )
        event = HubspotMarketingAPI.MarketingEvents.get_event(
            self.event_id, self.account_id
        )
        self.assertEqual(event["eventName"], "Test Event")

        event = HubspotMarketingAPI.MarketingEvents.get_event(
            externalEventId=None, externalAccountId=self.account_id
        )
        self.assertEqual(event["error"], "External Event ID is required.")

        event = HubspotMarketingAPI.MarketingEvents.get_event(
            externalEventId=self.event_id, externalAccountId=None
        )
        self.assertEqual(event["error"], "External Account ID is required.")

        event = HubspotMarketingAPI.MarketingEvents.get_event(
            externalEventId="event124", externalAccountId=self.account_id
        )
        self.assertEqual(event, {})

    def test_delete_event(self):
        """Test deleting a marketing event."""
        HubspotMarketingAPI.MarketingEvents.create_event(
            self.event_id, self.account_id, "Test Event", "Webinar", "Organizer"
        )
        HubspotMarketingAPI.MarketingEvents.delete_event(self.event_id, self.account_id)
        self.assertNotIn(self.event_id, DB["marketing_events"])

        event = HubspotMarketingAPI.MarketingEvents.delete_event(
            externalEventId=None, externalAccountId=self.account_id
        )
        self.assertEqual(event["error"], "External Event ID is required.")

        event = HubspotMarketingAPI.MarketingEvents.delete_event(
            externalEventId=self.event_id, externalAccountId=None
        )
        self.assertEqual(event["error"], "External Account ID is required.")

    def test_update_event(self):
        """Test updating a marketing event."""
        HubspotMarketingAPI.MarketingEvents.create_event(
            self.event_id, self.account_id, "Test Event", "Webinar", "Organizer"
        )
        updated_event = HubspotMarketingAPI.MarketingEvents.update_event(
            self.event_id, self.account_id, event_name="Updated Event"
        )
        self.assertEqual(updated_event["eventName"], "Updated Event")

        updated_event = HubspotMarketingAPI.MarketingEvents.update_event(
            externalEventId=None,
            externalAccountId=self.account_id,
            event_name="Updated Event",
        )
        self.assertEqual(updated_event["error"], "External Event ID is required.")

        updated_event = HubspotMarketingAPI.MarketingEvents.update_event(
            externalEventId=self.event_id,
            externalAccountId=None,
            event_name="Updated Event",
        )
        self.assertEqual(updated_event["error"], "External Account ID is required.")

        updated_event = HubspotMarketingAPI.MarketingEvents.update_event(
            externalEventId=self.event_id,
            externalAccountId=self.account_id,
            event_name="Updated Event",
            event_type="Webinar",
            event_organizer="Organizer",
            start_date_time="2023-01-01T10:00:00Z",
            end_date_time="2023-01-01T12:00:00Z",
            event_description="Updated Description",
            event_url="https://example.com/updated",
            custom_properties=[{"name": "custom_property", "value": "custom_value"}],
        )
        self.assertEqual(updated_event["eventName"], "Updated Event")
        self.assertEqual(updated_event["eventType"], "Webinar")
        self.assertEqual(updated_event["eventOrganizer"], "Organizer")
        self.assertEqual(updated_event["startDateTime"], "2023-01-01T10:00:00Z")
        self.assertEqual(updated_event["endDateTime"], "2023-01-01T12:00:00Z")
        self.assertEqual(updated_event["eventDescription"], "Updated Description")
        self.assertEqual(updated_event["eventUrl"], "https://example.com/updated")

        updated_event = HubspotMarketingAPI.MarketingEvents.update_event(
            externalEventId="nonexistent",
            externalAccountId=self.account_id,
            event_name="Updated Event",
            event_type="Webinar",
            event_organizer="Organizer",
        )
        self.assertEqual(updated_event, {})

    def test_cancel_event(self):
        """Test canceling a marketing event."""
        HubspotMarketingAPI.MarketingEvents.create_event(
            self.event_id, self.account_id, "Test Event", "Webinar", "Organizer"
        )
        canceled_event = HubspotMarketingAPI.MarketingEvents.cancel_event(
            self.event_id, self.account_id
        )
        self.assertEqual(canceled_event["eventStatus"], "CANCELED")

        canceled_event = HubspotMarketingAPI.MarketingEvents.cancel_event(
            externalEventId=None, externalAccountId=self.account_id
        )
        self.assertEqual(canceled_event["error"], "External Event ID is required.")

        canceled_event = HubspotMarketingAPI.MarketingEvents.cancel_event(
            externalEventId=self.event_id, externalAccountId=None
        )
        self.assertEqual(canceled_event["error"], "External Account ID is required.")

        canceled_event = HubspotMarketingAPI.MarketingEvents.cancel_event(
            externalEventId="nonexistent", externalAccountId=self.account_id
        )
        self.assertEqual(canceled_event, {})

    def test_create_or_update_attendee(self):
        """Test creating or updating an attendee."""
        HubspotMarketingAPI.MarketingEvents.create_event(
            self.event_id, self.account_id, "Test Event", "Webinar", "Organizer"
        )
        attendee = HubspotMarketingAPI.MarketingEvents.create_or_update_attendee(
            self.event_id,
            self.account_id,
            self.attendee_email,
            "2023-01-01T10:00:00Z",
            "2023-01-01T12:00:00Z",
        )
        self.assertEqual(attendee["email"], self.attendee_email)
        self.assertEqual(attendee["eventId"], self.event_id)
        self.assertIn(
            self.attendee_id, DB["marketing_events"][self.event_id]["attendees"]
        )

        attendee = HubspotMarketingAPI.MarketingEvents.create_or_update_attendee(
            externalEventId=self.event_id,
            externalAccountId=self.account_id,
            email=self.attendee_email,
            joinedAt="2023-01-01T10:00:00Z",
            leftAt="2023-01-01T12:00:00Z",
        )
        self.assertEqual(attendee["email"], self.attendee_email)
        self.assertEqual(attendee["eventId"], self.event_id)
        self.assertIn(
            self.attendee_id, DB["marketing_events"][self.event_id]["attendees"]
        )

        attendee = HubspotMarketingAPI.MarketingEvents.create_or_update_attendee(
            externalEventId=None,
            externalAccountId=self.account_id,
            email=self.attendee_email,
            joinedAt="2023-01-01T10:00:00Z",
            leftAt="2023-01-01T12:00:00Z",
        )
        self.assertEqual(attendee["error"], "Missing required parameters.")

        attendee = HubspotMarketingAPI.MarketingEvents.create_or_update_attendee(
            externalEventId="nonexistent",
            externalAccountId=self.account_id,
            email=self.attendee_email,
            joinedAt="2023-01-01T10:00:00Z",
            leftAt="2023-01-01T12:00:00Z",
        )
        self.assertEqual(attendee, {"error": "Event not found."})

        attendee = HubspotMarketingAPI.MarketingEvents.create_or_update_attendee(
            externalEventId=self.event_id,
            externalAccountId="nonexistent",
            email=self.attendee_email,
            joinedAt="2023-01-01T10:00:00Z",
            leftAt="2023-01-01T12:00:00Z",
        )
        self.assertEqual(attendee, {})

    def test_get_attendees(self):
        """Test getting attendees."""
        HubspotMarketingAPI.MarketingEvents.create_event(
            self.event_id, self.account_id, "Test Event", "Webinar", "Organizer"
        )
        HubspotMarketingAPI.MarketingEvents.create_or_update_attendee(
            self.event_id,
            self.account_id,
            self.attendee_email,
            "2023-01-01T10:00:00Z",
            "2023-01-01T12:00:00Z",
        )
        attendees = HubspotMarketingAPI.MarketingEvents.get_attendees(self.event_id)
        self.assertEqual(len(attendees["results"]), 1)
        self.assertEqual(attendees["results"][0]["email"], self.attendee_email)

        HubspotMarketingAPI.MarketingEvents.create_or_update_attendee(
            externalEventId=self.event_id,
            externalAccountId=self.account_id,
            email="test2@example.com",
            joinedAt="2023-01-01T10:00:00Z",
            leftAt="2023-01-01T12:00:00Z",
        )
        attendees = HubspotMarketingAPI.MarketingEvents.get_attendees(
            externalEventId=self.event_id, limit=1
        )
        self.assertEqual(len(attendees["results"]), 1)
        self.assertEqual(attendees["results"][0]["email"], self.attendee_email)

        attendees = HubspotMarketingAPI.MarketingEvents.get_attendees(
            externalEventId=None
        )
        self.assertEqual(attendees["error"], "Event ID is required.")

        attendees = HubspotMarketingAPI.MarketingEvents.get_attendees(
            externalEventId="nonexistent"
        )
        self.assertEqual(attendees, {"error": "Event not found."})

    def test_delete_attendee(self):
        """Test deleting an attendee."""
        event = HubspotMarketingAPI.MarketingEvents.create_event(
            self.event_id, self.account_id, "Test Event", "Webinar", "Organizer"
        )
        attendee = HubspotMarketingAPI.MarketingEvents.create_or_update_attendee(
            self.event_id,
            self.account_id,
            self.attendee_email,
            "2023-01-01T10:00:00Z",
            "2023-01-01T12:00:00Z",
        )
        state = HubspotMarketingAPI.MarketingEvents.delete_attendee(
            self.event_id, attendee["attendeeId"], self.account_id
        )
        self.assertEqual(len(DB["marketing_events"][self.event_id]["attendees"]), 0)

        state = HubspotMarketingAPI.MarketingEvents.delete_attendee(
            externalEventId=None,
            attendeeId=attendee["attendeeId"],
            externalAccountId=self.account_id,
        )
        self.assertEqual(state["error"], "Event ID is required.")

        state = HubspotMarketingAPI.MarketingEvents.delete_attendee(
            externalEventId=self.event_id,
            attendeeId=attendee["attendeeId"],
            externalAccountId=None,
        )
        self.assertEqual(state["error"], "External Account ID is required.")

        state = HubspotMarketingAPI.MarketingEvents.delete_attendee(
            externalEventId=self.event_id,
            attendeeId=None,
            externalAccountId=self.account_id,
        )
        self.assertEqual(state, {"error": "Attendee ID is required."})

        state = HubspotMarketingAPI.MarketingEvents.delete_attendee(
            externalEventId=self.event_id,
            attendeeId="nonexistent",
            externalAccountId=self.account_id,
        )
        self.assertEqual(state, {"error": "Attendee not found."})

        state = HubspotMarketingAPI.MarketingEvents.delete_attendee(
            externalEventId="nonexistent",
            attendeeId=attendee["attendeeId"],
            externalAccountId=self.account_id,
        )
        self.assertEqual(state, {"error": "Event not found."})

        event = HubspotMarketingAPI.MarketingEvents.create_event(
            "event124", self.account_id, "Test Event", "Webinar", "Organizer"
        )
        state = HubspotMarketingAPI.MarketingEvents.delete_attendee(
            externalEventId="event124",
            attendeeId=attendee["attendeeId"],
            externalAccountId=self.account_id,
        )
        self.assertEqual(state, {"error": "Attendees not found."})

        attendee = HubspotMarketingAPI.MarketingEvents.create_or_update_attendee(
            externalEventId=self.event_id,
            externalAccountId=self.account_id,
            email=self.attendee_email,
            joinedAt="2023-01-01T10:00:00Z",
            leftAt="2023-01-01T12:00:00Z",
        )
        state = HubspotMarketingAPI.MarketingEvents.delete_attendee(
            externalEventId=self.event_id,
            attendeeId=attendee["attendeeId"],
            externalAccountId="nonexistent",
        )
        self.assertEqual(state, {"error": "Invalid external account ID."})


class TestTemplatesAPI(unittest.TestCase):

    def setUp(self):
        DB.clear()
        self.template_id = "1"

    def test_templates_create_template(self):
        new_template = HubspotMarketingAPI.Templates.create_template(
            category_id=1, folder="test_folder", template_type=2, source="test_source"
        )
        self.assertEqual(new_template["category_id"], 1)
        self.assertEqual(new_template["folder"], "test_folder")
        self.assertEqual(new_template["template_type"], 2)
        self.assertEqual(new_template["source"], "test_source")
        self.assertEqual(
            new_template["id"], str(generate_hubspot_object_id("test_source"))
        )
        self.assertEqual(len(DB["templates"]), 1)

    def test_templates_get_templates(self):
        result = HubspotMarketingAPI.Templates.create_template(
            category_id=1, folder="test_folder", template_type=2, source="test_source"
        )
        templates = HubspotMarketingAPI.Templates.get_templates()
        self.assertEqual(len(templates), 1)
        templates = HubspotMarketingAPI.Templates.get_templates(limit=0)
        self.assertEqual(len(templates), 0)
        templates = HubspotMarketingAPI.Templates.get_templates(id=result["id"])
        self.assertEqual(len(templates), 1)
        templates = HubspotMarketingAPI.Templates.get_templates(id="2")
        self.assertEqual(len(templates), 0)

        created = HubspotMarketingAPI.Templates.create_template(
            category_id=1,
            folder="test_folder",
            template_type=2,
            source="Test Template 7",
        )

        templates = HubspotMarketingAPI.Templates.get_templates(
            deleted_at="1719177600000"
        )
        self.assertEqual(len(templates), 0)

        templates = HubspotMarketingAPI.Templates.get_templates(
            is_available_for_new_content="True"
        )
        self.assertEqual(len(templates), 0)

        templates = HubspotMarketingAPI.Templates.get_templates(label="Test Template 7")
        self.assertEqual(len(templates), 0)

        templates = HubspotMarketingAPI.Templates.get_templates(path="/templates/")
        self.assertEqual(len(templates), 0)

    def test_template_by_id_get_template(self):
        result = HubspotMarketingAPI.Templates.create_template(
            category_id=1, folder="test_folder", template_type=2, source="test_source"
        )
        template = HubspotMarketingAPI.Templates.get_template_by_id(result["id"])
        self.assertEqual(template["id"], result["id"])

    def test_template_by_id_update_template(self):
        result = HubspotMarketingAPI.Templates.create_template(
            category_id=1, folder="test_folder", template_type=2, source="test_source"
        )
        updated_template = HubspotMarketingAPI.Templates.update_template_by_id(
            result["id"], folder="updated_folder"
        )
        self.assertEqual(updated_template["folder"], "updated_folder")

        invalid_template = HubspotMarketingAPI.Templates.update_template_by_id(
            "nonexistent", folder="updated_folder"
        )
        self.assertEqual(invalid_template["error"], "Template not found")

    def test_template_by_id_delete_template(self):
        result = HubspotMarketingAPI.Templates.create_template(
            category_id=1, folder="test_folder", template_type=2, source="test_source"
        )
        id = result["id"]
        HubspotMarketingAPI.Templates.delete_template_by_id(id)
        self.assertTrue("deleted_at" in DB["templates"][id])

    def test_template_by_id_restore_deleted_template(self):
        result = HubspotMarketingAPI.Templates.create_template(
            category_id=1, folder="test_folder", template_type=2, source="test_source"
        )
        HubspotMarketingAPI.Templates.delete_template_by_id(result["id"])
        restored_template = HubspotMarketingAPI.Templates.restore_deleted_template(
            result["id"]
        )
        self.assertEqual(restored_template["id"], result["id"])

        invalid_template = HubspotMarketingAPI.Templates.restore_deleted_template(
            "nonexistent"
        )
        self.assertEqual(invalid_template["error"], "Template not found")

    def test_state_persistence(self):
        result = HubspotMarketingAPI.Templates.create_template(
            category_id=1, folder="test_folder", template_type=2, source="test_source"
        )
        save_state("test_state.json")
        DB.clear()
        load_state("test_state.json")
        self.assertEqual(len(DB["templates"]), 1)
        self.assertEqual(DB["templates"][result["id"]]["source"], "test_source")
        os.remove("test_state.json")
