import unittest
import uuid
from unittest.mock import patch
from ..users import get_user_details
from .. import DB
from ..SimulationEngine.custom_errors import UserNotFoundError, ValidationError
from ..SimulationEngine import models
from common_utils.base_case import BaseTestCaseWithErrorHandler

class TestGetUserDetails(BaseTestCaseWithErrorHandler):

    def setUp(self):
        """Set up a mock database for testing."""
        # Use proper UUIDs for all entities
        self.user_uuid = uuid.uuid4()
        self.trip_uuid = uuid.uuid4()
        self.booking1_uuid = uuid.uuid4()
        self.booking2_uuid = uuid.uuid4()
        
        self.mock_db = {
            'users': {
                str(self.user_uuid): {
                    'id': str(self.user_uuid),
                    'user_name': 'johndoe',
                    'given_name': 'John',
                    'family_name': 'Doe',
                    'display_name': 'John Doe',
                    'active': True,
                    'email': 'johndoe@example.com',
                    'locale': 'en-US',
                    'timezone': 'UTC',
                    'external_id': 'john_doe_1001',
                    'membership': 'gold',
                    'payment_methods': {
                        'credit_card_1234': {
                            'id': 'credit_card_1234',
                            'source': 'credit_card',
                            'brand': 'visa',
                            'last_four': '1234'
                        },
                        'credit_card_5678': {
                            'id': 'credit_card_5678',
                            'source': 'credit_card',
                            'brand': 'mastercard',
                            'last_four': '5678'
                        }
                    },
                    'created_at': '2023-01-01T00:00:00Z',
                    'last_modified': '2023-01-01T00:00:00Z'
                }
            },
            'trips': {
                str(self.trip_uuid): {
                    'trip_id': str(self.trip_uuid),
                    'trip_name': 'Test Trip',
                    'user_id': str(self.user_uuid),
                    'start_date': '2024-01-01',
                    'end_date': '2024-01-05',
                    'destination_summary': 'Test Destination',
                    'status': 'CONFIRMED',
                    'created_date': '2023-12-01T00:00:00Z',
                    'last_modified_date': '2023-12-01T00:00:00Z',
                    'booking_type': None,
                    'is_virtual_trip': False,
                    'is_canceled': False,
                    'is_guest_booking': False,
                    'booking_ids': [str(self.booking1_uuid), str(self.booking2_uuid)]
                }
            },
            'bookings': {
                str(self.booking1_uuid): {
                    'booking_id': str(self.booking1_uuid),
                    'booking_source': 'TestSupplier',
                    'record_locator': 'AXBDHW',
                    'trip_id': str(self.trip_uuid),
                    'date_booked_local': '2023-12-01T00:00:00Z',
                    'form_of_payment_name': None,
                    'form_of_payment_type': None,
                    'delivery': None,
                    'status': 'ISSUED',
                    'passengers': [
                        {
                            'passenger_id': str(uuid.uuid4()),
                            'name_first': 'John',
                            'name_last': 'Doe',
                            'text_name': None,
                            'pax_type': 'ADT'
                        }
                    ],
                    'segments': [],
                    'warnings': [],
                    'payment_history': [],
                    'created_at': '2023-12-01T00:00:00Z',
                    'last_modified': '2023-12-01T00:00:00Z'
                },
                str(self.booking2_uuid): {
                    'booking_id': str(self.booking2_uuid),
                    'booking_source': 'TestSupplier',
                    'record_locator': 'AXBDH2',
                    'trip_id': str(self.trip_uuid),
                    'date_booked_local': '2023-12-01T00:00:00Z',
                    'form_of_payment_name': None,
                    'form_of_payment_type': None,
                    'delivery': None,
                    'status': 'ISSUED',
                    'passengers': [
                        {
                            'passenger_id': str(uuid.uuid4()),
                            'name_first': 'John',
                            'name_last': 'Doe',
                            'text_name': None,
                            'pax_type': 'ADT'
                        }
                    ],
                    'segments': [],
                    'warnings': [],
                    'payment_history': [],
                    'created_at': '2023-12-01T00:00:00Z',
                    'last_modified': '2023-12-01T00:00:00Z'
                }
            },
            'trips_by_user': {
                str(self.user_uuid): [str(self.trip_uuid)]
            },
            'locations': {},
            'notifications': {
                str(uuid.uuid4()): {
                    'id': str(uuid.uuid4()),
                    'user_id': str(self.user_uuid),
                    'session_id': str(uuid.uuid4()),
                    'template_id': 'certificate_refund_voucher',
                    'context': {
                        'certificate_type': 'refund_voucher',
                        'certificate_number': 'CERT-12345',
                        'amount': 150.0,
                        'currency': 'USD',
                        'issued_date': '2023-11-01T00:00:00Z'
                    },
                    'created_at': '2023-11-01T00:00:00Z',
                    'url': '/certificates/cert-123'
                },
                str(uuid.uuid4()): {
                    'id': str(uuid.uuid4()),
                    'user_id': str(self.user_uuid),
                    'session_id': str(uuid.uuid4()),
                    'template_id': 'certificate_goodwill_gesture',
                    'context': {
                        'certificate_type': 'goodwill_gesture',
                        'certificate_number': 'CERT-67890',
                        'amount': 50.0,
                        'currency': 'USD',
                        'issued_date': '2023-10-15T00:00:00Z'
                    },
                    'created_at': '2023-10-15T00:00:00Z',
                    'url': '/certificates/cert-456'
                },
                str(uuid.uuid4()): {
                    'id': str(uuid.uuid4()),
                    'user_id': str(self.user_uuid),
                    'session_id': str(uuid.uuid4()),
                    'template_id': 'certificate_gift_card',
                    'context': {
                        'certificate_type': 'gift_card',
                        'certificate_number': 'CERT-78901',
                        'amount': 100.0,
                        'currency': 'USD',
                        'issued_date': '2023-09-30T00:00:00Z'
                    },
                    'created_at': '2023-09-30T00:00:00Z',
                    'url': '/certificates/cert-789'
                }
            },
            'user_by_external_id': {
                'john_doe_1001': str(self.user_uuid)
            },
            'booking_by_locator': {
                'AXBDHW': str(self.booking1_uuid),
                'AXBDH2': str(self.booking2_uuid)
            },
            'bookings_by_trip': {
                str(self.trip_uuid): [str(self.booking1_uuid), str(self.booking2_uuid)]
            }
        }
        self._validate_db_structure()

    def _validate_db_structure(self):
        """Validate that the DB structure conforms to ConcurAirlineDB model."""
        try:
            # Use the actual ConcurAirlineDB model for validation
            concur_db = models.ConcurAirlineDB(**self.mock_db)
            
        except Exception as e:
            raise AssertionError(f"DB structure validation failed using ConcurAirlineDB model: {str(e)}")

    def test_get_user_details_success(self):
        """Test successful retrieval of user details."""
        with patch('sapconcur.users.DB', self.mock_db):
            details = get_user_details('johndoe')
            self.assertIsNotNone(details)
            self.assertEqual(details['id'], str(self.user_uuid))
            self.assertIn('booking_locators', details)
            self.assertEqual(len(details['booking_locators']), 2)
            self.assertIn('AXBDHW', details['booking_locators'])
            
            # Test membership field
            self.assertIn('membership', details)
            self.assertEqual(details['membership'], 'gold')
            
            # Test payment methods
            self.assertIn('payment_methods', details)
            self.assertEqual(len(details['payment_methods']), 2)
            self.assertIn('credit_card_1234', details['payment_methods'])
            self.assertIn('credit_card_5678', details['payment_methods'])
            
            # Test payment method structures
            credit_card_1 = details['payment_methods']['credit_card_1234']
            self.assertEqual(credit_card_1['source'], 'credit_card')
            self.assertEqual(credit_card_1['brand'], 'visa')
            self.assertEqual(credit_card_1['last_four'], '1234')
            
            credit_card_2 = details['payment_methods']['credit_card_5678']
            self.assertEqual(credit_card_2['source'], 'credit_card')
            self.assertEqual(credit_card_2['brand'], 'mastercard')
            self.assertEqual(credit_card_2['last_four'], '5678')
            
            # Test certificates from notifications
            self.assertIn('certificates', details)
            self.assertEqual(len(details['certificates']), 3)
            # Check certificate types
            cert_types = [cert['type'] for cert in details['certificates']]
            self.assertIn('refund_voucher', cert_types)
            self.assertIn('goodwill_gesture', cert_types)
            self.assertIn('gift_card', cert_types)

    def test_get_user_details_not_found(self):
        """Test that a non-existent user raises UserNotFoundError."""
        with patch('sapconcur.users.DB', self.mock_db):
            self.assert_error_behavior(
                get_user_details,
                expected_exception_type=UserNotFoundError,
                expected_message="User with username 'janedoe' not found.",
                user_name='janedoe'
            )

    def test_get_user_details_invalid_input(self):
        """Test with invalid or empty inputs raises ValidationError."""
        with patch('sapconcur.users.DB', self.mock_db):
            self.assert_error_behavior(
                get_user_details,
                expected_exception_type=ValidationError,
                expected_message="Username cannot be empty.",
                user_name=''
            )
            self.assert_error_behavior(
                get_user_details,
                expected_exception_type=ValidationError,
                expected_message="Username must be a string.",
                user_name=None
            )

    def test_get_user_details_no_payment_methods_or_certificates(self):
        """Test user details with no payment methods or certificates."""
        # Create a user without payment methods
        user_uuid_2 = uuid.uuid4()
        mock_db_minimal = {
            'users': {
                str(user_uuid_2): {
                    'id': str(user_uuid_2),
                    'user_name': 'minimal_user',
                    'given_name': 'Minimal',
                    'family_name': 'User',
                    'email': 'minimal@example.com',
                    'active': True,
                    'locale': 'en-US',
                    'timezone': 'UTC',
                    'membership': None,
                    'payment_methods': {},
                    'created_at': '2023-01-01T00:00:00Z',
                    'last_modified': '2023-01-01T00:00:00Z'
                }
            },
            'trips_by_user': {},
            'locations': {},
            'notifications': {},
            'user_by_external_id': {},
            'booking_by_locator': {},
            'bookings_by_trip': {}
        }
        
        with patch('sapconcur.users.DB', mock_db_minimal):
            details = get_user_details('minimal_user')
            self.assertIsNotNone(details)
            
            # Test that empty collections are returned
            self.assertEqual(details['payment_methods'], {})
            self.assertEqual(details['certificates'], [])
            self.assertEqual(details['booking_locators'], [])
            self.assertIsNone(details['membership'])

if __name__ == '__main__':
    unittest.main() 