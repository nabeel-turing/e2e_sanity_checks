#!/usr/bin/env python3
"""
Test cases for the phone API utility functions.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the parent directory to the path to import the modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from APIs.phone.SimulationEngine.utils import (
    get_all_contacts, get_all_businesses, get_special_contacts,
    search_contacts_by_name, search_businesses_by_name,
    get_contact_by_id, get_business_by_id, get_special_contact_by_id,
    get_call_history, add_call_to_history,
    get_prepared_calls, add_prepared_call,
    get_recipient_choices, add_recipient_choice,
    get_not_found_records, add_not_found_record
)
from common_utils.base_case import BaseTestCaseWithErrorHandler


class TestPhoneUtils(BaseTestCaseWithErrorHandler):
    """Test cases for phone API utility functions."""

    def setUp(self):
        """Set up test fixtures."""
        # Sample data for testing with actual DB structure
        self.sample_contact = {
            "resourceName": "people/contact-alex-ray-123",
            "etag": "pHoNeP1EtAg654321",
            "names": [
                {
                    "givenName": "Alex",
                    "familyName": "Ray"
                }
            ],
            "phoneNumbers": [
                {
                    "value": "+12125550111",
                    "type": "mobile",
                    "primary": True
                }
            ],
            "emailAddresses": [],
            "organizations": [],
            "phone": {
                "contact_id": "contact-alex-ray-123",
                "contact_name": "Alex Ray",
                "recipient_type": "CONTACT",
                "contact_photo_url": "https://example.com/photos/alex.jpg",
                "contact_endpoints": [
                    {
                        "endpoint_type": "PHONE_NUMBER",
                        "endpoint_value": "+12125550111",
                        "endpoint_label": "mobile"
                    }
                ]
            }
        }

        self.sample_business = {
            "contact_id": "business-berlin-office-789",
            "contact_name": "Global Tech Inc. - Berlin Office",
            "recipient_type": "BUSINESS",
            "address": "Potsdamer Platz 1, 10785 Berlin, Germany",
            "contact_endpoints": [
                {
                    "endpoint_type": "PHONE_NUMBER",
                    "endpoint_value": "+493012345678",
                    "endpoint_label": "main"
                }
            ]
        }

        self.sample_call_record = {
            "call_id": "test-call-123",
            "timestamp": 1234567890.0,
            "phone_number": "+12125550111",
            "recipient_name": "Alex Ray",
            "recipient_photo_url": "https://example.com/photos/alex.jpg",
            "on_speakerphone": False,
            "status": "completed"
        }

    def test_get_all_contacts(self):
        """Test get_all_contacts function."""
        contacts = get_all_contacts()
        
        self.assertIsInstance(contacts, dict)
        # Should contain the contacts from our database with actual structure
        self.assertIn("people/contact-alex-ray-123", contacts)
        
        # Check that contacts have the actual structure from PhoneDefaultDB.json
        alex_contact = contacts["people/contact-alex-ray-123"]
        self.assertIn("names", alex_contact)
        self.assertIn("phoneNumbers", alex_contact)
        self.assertIn("phone", alex_contact)
        self.assertEqual(alex_contact["phone"]["contact_name"], "Alex Ray")

    def test_get_all_businesses(self):
        """Test get_all_businesses function."""
        businesses = get_all_businesses()
        
        self.assertIsInstance(businesses, dict)
        # Should contain the businesses from our database
        self.assertIn("business-berlin-office-789", businesses)
        self.assertIn("business-tokyo-hq-203", businesses)

    def test_get_special_contacts(self):
        """Test get_special_contacts function."""
        special_contacts = get_special_contacts()
        
        self.assertIsInstance(special_contacts, dict)
        # Should contain the voicemail contact
        self.assertIn("special-voicemail-000", special_contacts)

    def test_get_contact_by_id(self):
        """Test get_contact_by_id function."""
        # Test with existing contact using phone-specific contact_id
        contact = get_contact_by_id("contact-alex-ray-123")
        self.assertIsNotNone(contact)
        self.assertEqual(contact["phone"]["contact_name"], "Alex Ray")
        
        # Test with non-existing contact
        contact = get_contact_by_id("non-existing-id")
        self.assertIsNone(contact)

    def test_get_business_by_id(self):
        """Test get_business_by_id function."""
        # Test with existing business
        business = get_business_by_id("business-berlin-office-789")
        self.assertIsNotNone(business)
        self.assertEqual(business["contact_name"], "Global Tech Inc. - Berlin Office")
        
        # Test with non-existing business
        business = get_business_by_id("non-existing-id")
        self.assertIsNone(business)

    def test_get_special_contact_by_id(self):
        """Test get_special_contact_by_id function."""
        # Test with existing special contact
        voicemail = get_special_contact_by_id("special-voicemail-000")
        self.assertIsNotNone(voicemail)
        self.assertEqual(voicemail["contact_name"], "Voicemail")
        
        # Test with non-existing special contact
        contact = get_special_contact_by_id("non-existing-id")
        self.assertIsNone(contact)

    def test_search_contacts_by_name(self):
        """Test search_contacts_by_name function."""
        # Test exact match using phone-specific contact_name
        matches = search_contacts_by_name("Alex")
        self.assertIsInstance(matches, list)
        self.assertGreater(len(matches), 0)
        self.assertEqual(matches[0]["phone"]["contact_name"], "Alex Ray")
        
        # Test partial match
        matches = search_contacts_by_name("Ray")
        self.assertIsInstance(matches, list)
        self.assertGreater(len(matches), 0)
        self.assertEqual(matches[0]["phone"]["contact_name"], "Alex Ray")
        
        # Test case insensitive
        matches = search_contacts_by_name("alex")
        self.assertIsInstance(matches, list)
        self.assertGreater(len(matches), 0)
        
        # Test search by Google People API names
        matches = search_contacts_by_name("Alex Ray")
        self.assertIsInstance(matches, list)
        self.assertGreater(len(matches), 0)
        
        # Test non-existing name
        matches = search_contacts_by_name("NonExistingName")
        self.assertIsInstance(matches, list)
        self.assertEqual(len(matches), 0)

    def test_search_businesses_by_name(self):
        """Test search_businesses_by_name function."""
        # Test partial match
        matches = search_businesses_by_name("Global")
        self.assertIsInstance(matches, list)
        self.assertGreater(len(matches), 0)
        
        # Test case insensitive
        matches = search_businesses_by_name("global")
        self.assertIsInstance(matches, list)
        self.assertGreater(len(matches), 0)
        
        # Test non-existing name
        matches = search_businesses_by_name("NonExistingBusiness")
        self.assertIsInstance(matches, list)
        self.assertEqual(len(matches), 0)

    def test_get_call_history(self):
        """Test get_call_history function."""
        history = get_call_history()
        
        self.assertIsInstance(history, dict)
        # Should contain call history records from our database

    def test_add_call_to_history(self):
        """Test add_call_to_history function."""
        # Add a test call record
        add_call_to_history(self.sample_call_record)
        
        # Verify it was added
        history = get_call_history()
        self.assertIn("test-call-123", history)
        self.assertEqual(history["test-call-123"]["recipient_name"], "Alex Ray")

    def test_get_prepared_calls(self):
        """Test get_prepared_calls function."""
        prepared_calls = get_prepared_calls()
        
        self.assertIsInstance(prepared_calls, dict)
        # Should contain prepared call records from our database

    def test_add_prepared_call(self):
        """Test add_prepared_call function."""
        prepared_call_record = {
            "call_id": "test-prepared-call-123",
            "timestamp": 1234567890.0,
            "recipients": [self.sample_contact["phone"]]  # Use phone-specific data
        }
        
        # Add a test prepared call record
        add_prepared_call(prepared_call_record)
        
        # Verify it was added
        prepared_calls = get_prepared_calls()
        self.assertIn("test-prepared-call-123", prepared_calls)
        self.assertEqual(prepared_calls["test-prepared-call-123"]["recipients"][0]["contact_name"], "Alex Ray")

    def test_get_recipient_choices(self):
        """Test get_recipient_choices function."""
        choices = get_recipient_choices()
        
        self.assertIsInstance(choices, dict)
        # Should contain recipient choice records from our database

    def test_add_recipient_choice(self):
        """Test add_recipient_choice function."""
        choice_record = {
            "call_id": "test-choice-123",
            "timestamp": 1234567890.0,
            "recipient_options": [self.sample_contact["phone"]]  # Use phone-specific data
        }
        
        # Add a test recipient choice record
        add_recipient_choice(choice_record)
        
        # Verify it was added
        choices = get_recipient_choices()
        self.assertIn("test-choice-123", choices)
        self.assertEqual(choices["test-choice-123"]["recipient_options"][0]["contact_name"], "Alex Ray")

    def test_get_not_found_records(self):
        """Test get_not_found_records function."""
        records = get_not_found_records()
        
        self.assertIsInstance(records, dict)
        # Should contain not found records from our database

    def test_add_not_found_record(self):
        """Test add_not_found_record function."""
        not_found_record = {
            "call_id": "test-not-found-123",
            "timestamp": 1234567890.0,
            "contact_name": "Unknown Person"
        }
        
        # Add a test not found record
        add_not_found_record(not_found_record)
        
        # Verify it was added
        records = get_not_found_records()
        self.assertIn("test-not-found-123", records)
        self.assertEqual(records["test-not-found-123"]["contact_name"], "Unknown Person")

    def test_search_contacts_with_empty_name(self):
        """Test search_contacts_by_name with empty name."""
        matches = search_contacts_by_name("")
        self.assertIsInstance(matches, list)
        # Empty search should return all contacts
        self.assertGreater(len(matches), 0)

    def test_search_businesses_with_empty_name(self):
        """Test search_businesses_by_name with empty name."""
        matches = search_businesses_by_name("")
        self.assertIsInstance(matches, list)
        # Empty search should return all businesses
        self.assertGreater(len(matches), 0)


if __name__ == "__main__":
    unittest.main() 