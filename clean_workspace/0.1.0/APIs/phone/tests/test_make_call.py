#!/usr/bin/env python3
"""
Comprehensive test cases for the make_call function.
Tests all scenarios including valid calls, error conditions, edge cases, and validation.
"""

import unittest
import sys
import os
import time
from unittest.mock import patch, MagicMock
# Add APIs path to sys path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from phone import make_call
from phone.SimulationEngine.models import RecipientModel, RecipientEndpointModel
from common_utils.base_case import BaseTestCaseWithErrorHandler
from phone.SimulationEngine.custom_errors import (
    NoPhoneNumberError, MultipleEndpointsError, MultipleRecipientsError, 
    GeofencingPolicyError, InvalidRecipientError, PhoneAPIError, ValidationError
)


class TestMakeCall(BaseTestCaseWithErrorHandler):
    """Comprehensive test cases for make_call function."""

    def setUp(self):
        """Set up test fixtures."""
        # Clear the database to ensure clean state for each test
        from phone.SimulationEngine.db import DB, DEFAULT_DB_PATH
        import json
        
        # Clear all data from DB
        DB.clear()
        
        # Reinitialize with default data
        with open(DEFAULT_DB_PATH, "r", encoding="utf-8") as f:
            default_data = json.load(f)
        
        # Only load the static data (contacts, businesses, special_contacts)
        static_data = {
            "contacts": default_data.get("contacts", {}),
            "businesses": default_data.get("businesses", {}),
            "special_contacts": default_data.get("special_contacts", {})
        }
        DB.update(static_data)
        
        # Initialize empty dynamic collections
        DB["call_history"] = {}
        DB["prepared_calls"] = {}
        DB["recipient_choices"] = {}
        DB["not_found_records"] = {}
        DB["actions"] = []
        # Sample valid recipient data
        self.valid_recipient = {
            "contact_id": "contact-test-123",
            "contact_name": "Test Contact",
            "recipient_type": "CONTACT",
            "contact_photo_url": "https://example.com/photo.jpg",
            "contact_endpoints": [
                {
                    "endpoint_type": "PHONE_NUMBER",
                    "endpoint_value": "+12125550111",
                    "endpoint_label": "mobile"
                }
            ]
        }
        
        # Sample recipient with multiple endpoints
        self.multiple_endpoints_recipient = {
            "contact_id": "contact-multi-456",
            "contact_name": "Multi Contact",
            "recipient_type": "CONTACT",
            "contact_endpoints": [
                {
                    "endpoint_type": "PHONE_NUMBER",
                    "endpoint_value": "+12125550111",
                    "endpoint_label": "mobile"
                },
                {
                    "endpoint_type": "PHONE_NUMBER",
                    "endpoint_value": "+12125550112",
                    "endpoint_label": "work"
                }
            ]
        }
        
        # Sample business recipient with distance
        self.business_recipient = {
            "contact_id": "business-test-789",
            "contact_name": "Test Business",
            "recipient_type": "BUSINESS",
            "address": "123 Business St, City, State",
            "distance": "60 miles",
            "contact_endpoints": [
                {
                    "endpoint_type": "PHONE_NUMBER",
                    "endpoint_value": "+12125550113",
                    "endpoint_label": "main"
                }
            ]
        }
        
        # Sample recipient with low confidence
        self.low_confidence_recipient = {
            "contact_id": "contact-low-conf-101",
            "contact_name": "Low Confidence Contact",
            "recipient_type": "CONTACT",
            "confidence_level": "LOW",
            "contact_endpoints": [
                {
                    "endpoint_type": "PHONE_NUMBER",
                    "endpoint_value": "+12125550114",
                    "endpoint_label": "mobile"
                }
            ]
        }

    def test_make_call_with_valid_recipient_object(self):
        """Test make_call with a valid recipient object."""
        result = make_call(recipient=self.valid_recipient, on_speakerphone=False)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "success")
        self.assertIn("call_id", result)
        self.assertTrue(len(result["call_id"]) > 0)
        self.assertEqual(result["emitted_action_count"], 1)
        self.assertIn("Calling to Test Contact at +12125550111", result["templated_tts"])
        self.assertIn("Call completed successfully", result["action_card_content_passthrough"])

    def test_make_call_with_individual_parameters(self):
        """Test make_call with individual parameters instead of recipient object."""
        result = make_call(
            recipient_name="John Doe",
            recipient_phone_number="+1234567890",
            recipient_photo_url="https://example.com/john.jpg",
            on_speakerphone=True
        )
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "success")
        self.assertIn("call_id", result)
        self.assertEqual(result["emitted_action_count"], 1)
        self.assertIn("Calling to John Doe at +1234567890 on speakerphone", result["templated_tts"])

    def test_make_call_with_speakerphone_false(self):
        """Test make_call with speakerphone explicitly set to False."""
        result = make_call(
            recipient_name="Jane Smith",
            recipient_phone_number="+1987654321",
            on_speakerphone=False
        )
        
        self.assertEqual(result["status"], "success")
        self.assertNotIn("on speakerphone", result["templated_tts"])

    def test_make_call_with_speakerphone_true(self):
        """Test make_call with speakerphone set to True."""
        result = make_call(
            recipient_name="Bob Wilson",
            recipient_phone_number="+1555123456",
            on_speakerphone=True
        )
        
        self.assertEqual(result["status"], "success")
        self.assertIn("on speakerphone", result["templated_tts"])

    def test_make_call_without_recipient_name(self):
        """Test make_call with phone number but no recipient name."""
        result = make_call(
            recipient_phone_number="+1234567890",
            on_speakerphone=False
        )
        
        self.assertEqual(result["status"], "success")
        self.assertIn("Calling at +1234567890", result["templated_tts"])
        self.assertNotIn("to None", result["templated_tts"])

    def test_make_call_without_phone_number_individual_params(self):
        """Test make_call without phone number using individual parameters."""
        self.assert_error_behavior(
            func_to_call=make_call,
            expected_exception_type=NoPhoneNumberError,
            expected_message="I couldn't determine the phone number to call. Please provide a valid phone number or recipient information.",
            recipient_name="No Phone Contact"
        )

    def test_make_call_without_phone_number_recipient_object(self):
        """Test make_call without phone number using recipient object."""
        recipient_no_phone = {
            "contact_name": "No Phone Contact",
            "recipient_type": "CONTACT"
            # No contact_endpoints
        }
        
        self.assert_error_behavior(
            func_to_call=make_call,
            expected_exception_type=NoPhoneNumberError,
            expected_message="I couldn't determine the phone number to call. Please provide a valid phone number or recipient information.",
            recipient=recipient_no_phone
        )

    def test_make_call_with_empty_recipient_object(self):
        """Test make_call with empty recipient object."""
        self.assert_error_behavior(
            func_to_call=make_call,
            expected_exception_type=NoPhoneNumberError,
            expected_message="I couldn't determine the phone number to call. Please provide a valid phone number or recipient information.",
            recipient={}
        )

    def test_make_call_with_none_recipient(self):
        """Test make_call with None recipient."""
        self.assert_error_behavior(
            func_to_call=make_call,
            expected_exception_type=NoPhoneNumberError,
            expected_message="I couldn't determine the phone number to call. Please provide a valid phone number or recipient information.",
            recipient=None
        )

    def test_make_call_with_multiple_endpoints_recipient(self):
        """Test make_call with recipient having multiple endpoints."""
        self.assert_error_behavior(
            func_to_call=make_call,
            expected_exception_type=MultipleEndpointsError,
            expected_message="I found multiple phone numbers for Multi Contact. Please use show_call_recipient_choices to select the desired endpoint.",
            recipient=self.multiple_endpoints_recipient
        )

    def test_make_call_with_geofencing_policy(self):
        """Test make_call with business that triggers geofencing policy."""
        self.assert_error_behavior(
            func_to_call=make_call,
            expected_exception_type=GeofencingPolicyError,
            expected_message="The business Test Business is 60 miles away. Please use show_call_recipient_choices to confirm you want to call this business.",
            recipient=self.business_recipient
        )

    def test_make_call_with_low_confidence_recipient(self):
        """Test make_call with recipient having low confidence level."""
        self.assert_error_behavior(
            func_to_call=make_call,
            expected_exception_type=InvalidRecipientError,
            expected_message="I found a low confidence match for Low Confidence Contact. Please use show_call_recipient_choices to confirm this is the correct recipient.",
            recipient=self.low_confidence_recipient
        )

    def test_make_call_with_invalid_recipient_data(self):
        """Test make_call with invalid recipient data causing validation errors."""
        invalid_recipient = {
            "contact_name": "",  # Empty string should fail validation
            "contact_endpoints": [
                {
                    "endpoint_type": "INVALID_TYPE",  # Invalid endpoint type
                    "endpoint_value": "not-a-phone-number",
                    "endpoint_label": "invalid"
                }
            ]
        }
        
        self.assert_error_behavior(
            func_to_call=make_call,
            expected_exception_type=ValidationError,
            expected_message="Invalid recipient: 2 validation errors for RecipientModel\ncontact_name\n  Value error, contact_name cannot be empty string [type=value_error, input_value='', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.11/v/value_error\ncontact_endpoints.0.endpoint_type\n  Input should be 'PHONE_NUMBER' [type=literal_error, input_value='INVALID_TYPE', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.11/v/literal_error",
            recipient=invalid_recipient
        )

    def test_make_call_with_empty_contact_name(self):
        """Test make_call with empty contact_name in recipient."""
        recipient_empty_name = {
            "contact_name": "",
            "contact_endpoints": [
                {
                    "endpoint_type": "PHONE_NUMBER",
                    "endpoint_value": "+12125550111",
                    "endpoint_label": "mobile"
                }
            ]
        }
        
        self.assert_error_behavior(
            func_to_call=make_call,
            expected_exception_type=ValidationError,
            expected_message="Invalid recipient: 1 validation error for RecipientModel\ncontact_name\n  Value error, contact_name cannot be empty string [type=value_error, input_value='', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.11/v/value_error",
            recipient=recipient_empty_name
        )

    def test_make_call_with_empty_contact_endpoints(self):
        """Test make_call with empty contact_endpoints list."""
        recipient_empty_endpoints = {
            "contact_name": "Test Contact",
            "contact_endpoints": []
        }
        
        self.assert_error_behavior(
            func_to_call=make_call,
            expected_exception_type=ValidationError,
            expected_message="Invalid recipient: 1 validation error for RecipientModel\ncontact_endpoints\n  Value error, contact_endpoints cannot be empty list [type=value_error, input_value=[], input_type=list]\n    For further information visit https://errors.pydantic.dev/2.11/v/value_error",
            recipient=recipient_empty_endpoints
        )

    def test_make_call_with_invalid_endpoint_type(self):
        """Test make_call with invalid endpoint type."""
        recipient_invalid_endpoint = {
            "contact_name": "Test Contact",
            "contact_endpoints": [
                {
                    "endpoint_type": "EMAIL",  # Invalid type
                    "endpoint_value": "test@example.com",
                    "endpoint_label": "email"
                }
            ]
        }
        
        self.assert_error_behavior(
            func_to_call=make_call,
            expected_exception_type=ValidationError,
            expected_message="Invalid recipient: 1 validation error for RecipientModel\ncontact_endpoints.0.endpoint_type\n  Input should be 'PHONE_NUMBER' [type=literal_error, input_value='EMAIL', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.11/v/literal_error",
            recipient=recipient_invalid_endpoint
        )

    def test_make_call_with_missing_endpoint_value(self):
        """Test make_call with missing endpoint value."""
        recipient_missing_value = {
            "contact_name": "Test Contact",
            "contact_endpoints": [
                {
                    "endpoint_type": "PHONE_NUMBER",
                    "endpoint_label": "mobile"
                    # Missing endpoint_value
                }
            ]
        }
        
        self.assert_error_behavior(
            func_to_call=make_call,
            expected_exception_type=ValidationError,
            expected_message="Invalid recipient: 1 validation error for RecipientModel\ncontact_endpoints.0.endpoint_value\n  Field required [type=missing, input_value={'endpoint_type': 'PHONE_...dpoint_label': 'mobile'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.11/v/missing",
            recipient=recipient_missing_value
        )

    def test_make_call_with_invalid_recipient_type(self):
        """Test make_call with invalid recipient_type."""
        recipient_invalid_type = {
            "contact_name": "Test Contact",
            "recipient_type": "INVALID_TYPE",
            "contact_endpoints": [
                {
                    "endpoint_type": "PHONE_NUMBER",
                    "endpoint_value": "+12125550111",
                    "endpoint_label": "mobile"
                }
            ]
        }
        
        self.assert_error_behavior(
            func_to_call=make_call,
            expected_exception_type=ValidationError,
            expected_message="Invalid recipient: 1 validation error for RecipientModel\nrecipient_type\n  Input should be 'CONTACT', 'BUSINESS', 'DIRECT' or 'VOICEMAIL' [type=literal_error, input_value='INVALID_TYPE', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.11/v/literal_error",
            recipient=recipient_invalid_type
        )

    def test_make_call_with_invalid_confidence_level(self):
        """Test make_call with invalid confidence_level."""
        recipient_invalid_confidence = {
            "contact_name": "Test Contact",
            "confidence_level": "INVALID_LEVEL",
            "contact_endpoints": [
                {
                    "endpoint_type": "PHONE_NUMBER",
                    "endpoint_value": "+12125550111",
                    "endpoint_label": "mobile"
                }
            ]
        }
        
        self.assert_error_behavior(
            func_to_call=make_call,
            expected_exception_type=ValidationError,
            expected_message="Invalid recipient: 1 validation error for RecipientModel\nconfidence_level\n  Input should be 'LOW', 'MEDIUM' or 'HIGH' [type=literal_error, input_value='INVALID_LEVEL', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.11/v/literal_error",
            recipient=recipient_invalid_confidence
        )

    def test_make_call_call_id_uniqueness(self):
        """Test that make_call generates unique call IDs."""
        result1 = make_call(
            recipient_name="Contact 1",
            recipient_phone_number="+1234567890"
        )
        result2 = make_call(
            recipient_name="Contact 2",
            recipient_phone_number="+0987654321"
        )
        
        self.assertNotEqual(result1["call_id"], result2["call_id"])

    def test_make_call_database_integration(self):
        """Test that make_call properly updates the database."""
        from phone.SimulationEngine.db import DB
        
        initial_call_count = len(DB.get("call_history", {}))
        
        result = make_call(
            recipient_name="Database Test",
            recipient_phone_number="+1234567890"
        )
        
        final_call_count = len(DB.get("call_history", {}))
        self.assertEqual(final_call_count, initial_call_count + 1)
        
        # Verify the call record was added
        call_record = DB["call_history"].get(result["call_id"])
        self.assertIsNotNone(call_record)
        self.assertEqual(call_record["phone_number"], "+1234567890")
        self.assertEqual(call_record["recipient_name"], "Database Test")
        self.assertEqual(call_record["status"], "completed")

    def test_make_call_with_voicemail_recipient(self):
        """Test make_call with voicemail recipient type."""
        voicemail_recipient = {
            "contact_name": "Voicemail",
            "recipient_type": "VOICEMAIL",
            "contact_endpoints": [
                {
                    "endpoint_type": "PHONE_NUMBER",
                    "endpoint_value": "+12125550115",
                    "endpoint_label": "voicemail"
                }
            ]
        }
        
        result = make_call(recipient=voicemail_recipient)
        
        self.assertEqual(result["status"], "success")
        self.assertIn("Calling to Voicemail at +12125550115", result["templated_tts"])

    def test_make_call_with_direct_recipient(self):
        """Test make_call with direct recipient type."""
        direct_recipient = {
            "contact_name": "Direct Call",
            "recipient_type": "DIRECT",
            "contact_endpoints": [
                {
                    "endpoint_type": "PHONE_NUMBER",
                    "endpoint_value": "+12125550116",
                    "endpoint_label": "direct"
                }
            ]
        }
        
        result = make_call(recipient=direct_recipient)
        
        self.assertEqual(result["status"], "success")
        self.assertIn("Calling to Direct Call at +12125550116", result["templated_tts"])

    def test_make_call_with_business_recipient_no_distance(self):
        """Test make_call with business recipient that has no distance (should succeed)."""
        business_no_distance = {
            "contact_name": "Local Business",
            "recipient_type": "BUSINESS",
            "address": "123 Local St",
            "contact_endpoints": [
                {
                    "endpoint_type": "PHONE_NUMBER",
                    "endpoint_value": "+12125550117",
                    "endpoint_label": "main"
                }
            ]
        }
        
        result = make_call(recipient=business_no_distance)
        
        self.assertEqual(result["status"], "success")
        self.assertIn("Calling to Local Business at +12125550117", result["templated_tts"])

    def test_make_call_with_high_confidence_recipient(self):
        """Test make_call with recipient having high confidence level."""
        high_confidence_recipient = {
            "contact_name": "High Confidence Contact",
            "recipient_type": "CONTACT",
            "confidence_level": "HIGH",
            "contact_endpoints": [
                {
                    "endpoint_type": "PHONE_NUMBER",
                    "endpoint_value": "+12125550118",
                    "endpoint_label": "mobile"
                }
            ]
        }
        
        result = make_call(recipient=high_confidence_recipient)
        
        self.assertEqual(result["status"], "success")
        self.assertIn("Calling to High Confidence Contact at +12125550118", result["templated_tts"])

    def test_make_call_with_medium_confidence_recipient(self):
        """Test make_call with recipient having medium confidence level."""
        medium_confidence_recipient = {
            "contact_name": "Medium Confidence Contact",
            "recipient_type": "CONTACT",
            "confidence_level": "MEDIUM",
            "contact_endpoints": [
                {
                    "endpoint_type": "PHONE_NUMBER",
                    "endpoint_value": "+12125550119",
                    "endpoint_label": "mobile"
                }
            ]
        }
        
        result = make_call(recipient=medium_confidence_recipient)
        
        self.assertEqual(result["status"], "success")
        self.assertIn("Calling to Medium Confidence Contact at +12125550119", result["templated_tts"])

    def test_make_call_with_distance_in_kilometers(self):
        """Test make_call with distance in kilometers that triggers geofencing."""
        business_km_distance = {
            "contact_name": "Distant Business",
            "recipient_type": "BUSINESS",
            "address": "123 Distant St",
            "distance": "100 kilometers",
            "contact_endpoints": [
                {
                    "endpoint_type": "PHONE_NUMBER",
                    "endpoint_value": "+12125550120",
                    "endpoint_label": "main"
                }
            ]
        }
        
        self.assert_error_behavior(
            func_to_call=make_call,
            expected_exception_type=GeofencingPolicyError,
            expected_message="The business Distant Business is 100 kilometers away. Please use show_call_recipient_choices to confirm you want to call this business.",
            recipient=business_km_distance
        )

    def test_make_call_with_distance_under_limit(self):
        """Test make_call with distance under the geofencing limit."""
        business_close = {
            "contact_name": "Close Business",
            "recipient_type": "BUSINESS",
            "address": "123 Close St",
            "distance": "30 miles",
            "contact_endpoints": [
                {
                    "endpoint_type": "PHONE_NUMBER",
                    "endpoint_value": "+12125550121",
                    "endpoint_label": "main"
                }
            ]
        }
        
        result = make_call(recipient=business_close)
        
        self.assertEqual(result["status"], "success")
        self.assertIn("Calling to Close Business at +12125550121", result["templated_tts"])

    def test_make_call_with_malformed_distance(self):
        """Test make_call with malformed distance string."""
        business_malformed_distance = {
            "contact_name": "Malformed Distance Business",
            "recipient_type": "BUSINESS",
            "address": "123 Malformed St",
            "distance": "invalid distance format",
            "contact_endpoints": [
                {
                    "endpoint_type": "PHONE_NUMBER",
                    "endpoint_value": "+12125550122",
                    "endpoint_label": "main"
                }
            ]
        }
        
        # Should succeed since distance parsing fails gracefully
        result = make_call(recipient=business_malformed_distance)
        
        self.assertEqual(result["status"], "success")
        self.assertIn("Calling to Malformed Distance Business at +12125550122", result["templated_tts"])

    def test_make_call_with_optional_fields_none(self):
        """Test make_call with all optional fields set to None."""
        minimal_recipient = {
            "contact_endpoints": [
                {
                    "endpoint_type": "PHONE_NUMBER",
                    "endpoint_value": "+12125550123"
                    # No optional fields
                }
            ]
        }
        
        result = make_call(recipient=minimal_recipient)
        
        self.assertEqual(result["status"], "success")
        self.assertIn("Calling at +12125550123", result["templated_tts"])

    def test_make_call_with_endpoint_label_none(self):
        """Test make_call with endpoint label set to None."""
        recipient_no_label = {
            "contact_name": "No Label Contact",
            "contact_endpoints": [
                {
                    "endpoint_type": "PHONE_NUMBER",
                    "endpoint_value": "+12125550124",
                    "endpoint_label": None
                }
            ]
        }
        
        result = make_call(recipient=recipient_no_label)
        
        self.assertEqual(result["status"], "success")
        self.assertIn("Calling to No Label Contact at +12125550124", result["templated_tts"])


if __name__ == "__main__":
    unittest.main() 