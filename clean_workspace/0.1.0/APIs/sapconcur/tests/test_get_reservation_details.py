import unittest
from unittest.mock import patch
from ..bookings import get_reservation_details
from ..SimulationEngine.custom_errors import BookingNotFoundError, ValidationError
from common_utils.base_case import BaseTestCaseWithErrorHandler
from .. import DB
from ..SimulationEngine import models

class TestGetReservationDetails(BaseTestCaseWithErrorHandler):

    def setUp(self):
        """Set up a mock database for testing."""
        DB.clear()
        self.original_db = DB.copy()
        DB.update({
            'users': {
                '550e8400-e29b-41d4-a716-446655441003': {
                    'id': '550e8400-e29b-41d4-a716-446655441003',
                    'external_id': 'test_user_1',
                    'user_name': 'test_user_1',
                    'given_name': 'Test',
                    'family_name': 'UserOne',
                    'email': 'test_user_1@test.com',
                },
                '550e8400-e29b-41d4-a716-446655441004': {
                    'id': '550e8400-e29b-41d4-a716-446655441004',
                    'external_id': 'test_user_2',
                    'user_name': 'test_user_2',
                    'given_name': 'Test',
                    'family_name': 'UserTwo',
                    'email': 'test_user_2@test.com',
                },
            },
            'trips': {
                '550e8400-e29b-41d4-a716-446655441000': {
                    'trip_id': '550e8400-e29b-41d4-a716-446655441000',
                    'user_id': '550e8400-e29b-41d4-a716-446655441003',
                    'trip_name': 'Trip to JFK',
                    'start_date': '2023-01-01',
                    'end_date': '2023-01-05',
                },
                '550e8400-e29b-41d4-a716-446655441001': {
                    'trip_id': '550e8400-e29b-41d4-a716-446655441001',
                    'user_id': '550e8400-e29b-41d4-a716-446655441003',
                    'trip_name': 'Business Trip',
                    'start_date': '2023-01-01',
                    'end_date': '2023-01-05',
                },
                '550e8400-e29b-41d4-a716-446655441002': {
                    'trip_id': '550e8400-e29b-41d4-a716-446655441002',
                    'user_id': '550e8400-e29b-41d4-a716-446655441004',
                    'trip_name': 'Vacation',
                    'start_date': '2023-01-05',
                    'end_date': '2023-01-07',
                }
            },
            'locations': {},
            'notifications': {},
            'user_by_external_id': {},
            'trips_by_user': {},
            'bookings_by_trip': {},
            'booking_by_locator': {
                'AA7B8C': '5a9e3d6e-8f0a-4b7c-882d-1f6a7b8c9d0e',
                'HZ9D8F': '0b5c9a72-7f9a-4e1b-9c7c-4a7b8c9d0e1f',
                'BA4F5E': '3d2e1c9d-0f9a-4b8c-8e7d-6c9d0e1f2a3b'
            },
            'bookings': {
                '5a9e3d6e-8f0a-4b7c-882d-1f6a7b8c9d0e': {
                    'booking_id': '5a9e3d6e-8f0a-4b7c-882d-1f6a7b8c9d0e',
                    'booking_source': 'American Airlines',
                    'record_locator': 'AA7B8C',
                    'trip_id': '550e8400-e29b-41d4-a716-446655441000',
                    'date_booked_local': '2023-07-22T14:30:00Z',
                    'status': 'CONFIRMED',
                    'passengers': [{'passenger_id': '550e8400-e29b-41d4-a716-446655441010', 'name_first': 'John', 'name_last': 'Doe', 'pax_type': 'ADT', "dob": "1964-02-24"}],
                    'segments': [{
                        'segment_id': '550e8400-e29b-41d4-a716-446655441015',
                        'type': 'AIR',
                        'status': 'CONFIRMED',
                        'confirmation_number': 'AA12345',
                        'start_date': '2023-01-01T08:00:00Z',
                        'end_date': '2023-01-01T12:00:00Z',
                        'vendor': 'AA',
                        'vendor_name': 'American Airlines',
                        'currency': 'USD',
                        'total_rate': 450.0,
                        'departure_airport': 'LAX',
                        'arrival_airport': 'JFK',
                        'flight_number': 'AA123',
                        'aircraft_type': 'Boeing 737',
                        'fare_class': 'Y',
                        'is_direct': True
                    }],
                    'warnings': [],
                    'payment_history': [],
                    'created_at': '2023-07-22T14:30:00Z',
                    'last_modified': '2023-07-22T14:30:00Z',
                    'insurance': 'yes'
                },
                '0b5c9a72-7f9a-4e1b-9c7c-4a7b8c9d0e1f': {
                    'booking_id': '0b5c9a72-7f9a-4e1b-9c7c-4a7b8c9d0e1f',
                    'booking_source': 'Hertz',
                    'record_locator': 'HZ9D8F',
                    'trip_id': '550e8400-e29b-41d4-a716-446655441001',
                    'date_booked_local': '2023-07-25T16:45:00Z',
                    'status': 'CONFIRMED',
                    'passengers': [{'passenger_id': '550e8400-e29b-41d4-a716-446655441011', 'name_first': 'John', 'name_last': 'Doe', 'pax_type': 'ADT', "dob": "1964-02-24"}],
                    'segments': [{
                        'segment_id': '550e8400-e29b-41d4-a716-446655441016',
                        'type': 'CAR',
                        'status': 'CONFIRMED',
                        'confirmation_number': 'HZ67890',
                        'start_date': '2023-01-01T12:00:00Z',
                        'end_date': '2023-01-05T10:00:00Z',
                        'vendor': 'HZ',
                        'vendor_name': 'Hertz',
                        'currency': 'USD',
                        'total_rate': 320.0,
                        'pickup_location': 'LAX',
                        'dropoff_location': 'LAX'
                    }],
                    'warnings': [],
                    'payment_history': [],
                    'created_at': '2023-07-25T16:45:00Z',
                    'last_modified': '2023-07-25T16:45:00Z',
                    'insurance': 'no'
                },
                '3d2e1c9d-0f9a-4b8c-8e7d-6c9d0e1f2a3b': {
                    'booking_id': '3d2e1c9d-0f9a-4b8c-8e7d-6c9d0e1f2a3b',
                    'booking_source': 'Grand Hyatt',
                    'record_locator': 'BA4F5E',
                    'trip_id': '550e8400-e29b-41d4-a716-446655441002',
                    'date_booked_local': '2023-08-15T11:20:00Z',
                    'status': 'CONFIRMED',
                    'passengers': [{'passenger_id': '550e8400-e29b-41d4-a716-446655441012', 'name_first': 'Jane', 'name_last': 'Smith', 'pax_type': 'ADT', "dob": "1964-02-24"}],
                    'segments': [{
                        'segment_id': '550e8400-e29b-41d4-a716-446655441017',
                        'type': 'HOTEL',
                        'status': 'CONFIRMED',
                        'confirmation_number': 'HI12345',
                        'start_date': '2023-01-05T15:00:00Z',
                        'end_date': '2023-01-07T11:00:00Z',
                        'vendor': 'HI',
                        'vendor_name': 'Grand Hyatt',
                        'currency': 'USD',
                        'total_rate': 850.0,
                        'location': 'NYC'
                    }],
                    'warnings': [],
                    'payment_history': [],
                    'created_at': '2023-08-15T11:20:00Z',
                    'last_modified': '2023-08-15T11:20:00Z',
                    'insurance': 'no'
                }
            }
        })
        self._validate_db_structure()
    
    def tearDown(self):
        DB.clear()
        DB.update(self.original_db)

    def _validate_db_structure(self):
        """Validate that the DB structure conforms to ConcurAirlineDB model."""
        try:
            # Ensure all required collections exist with defaults
            DB.setdefault('locations', {})
            DB.setdefault('notifications', {})
            DB.setdefault('user_by_external_id', {})
            DB.setdefault('booking_by_locator', {})
            DB.setdefault('trips_by_user', {})
            DB.setdefault('bookings_by_trip', {})
            
            # Use the actual ConcurAirlineDB model for validation
            concur_db = models.ConcurAirlineDB(**DB)
            
        except Exception as e:
            raise AssertionError(f"DB structure validation failed using ConcurAirlineDB model: {str(e)}")

    def test_get_reservation_details_air_success(self):
        """Test successful retrieval of an air reservation."""
        details = get_reservation_details(record_locator='AA7B8C')
        self.assertIsNotNone(details)
        self.assertEqual(details['record_locator'], 'AA7B8C')
        self.assertEqual(details['user_id'], 'test_user_1')
        self.assertEqual(details['segments'][0]['type'], 'AIR')
        self.assertEqual(details['segments'][0]['vendor_name'], 'American Airlines')
        self.assertIn('passengers', details)
        self.assertIsInstance(details['passengers'], list)
        self.assertEqual(len(details['passengers']), 1)
        expected_passenger = {
            'name_first': 'John',
            'name_last': 'Doe',
            'dob': '1964-02-24'
        }
        self.assertDictEqual(details['passengers'][0], expected_passenger)
    
    def test_get_reservation_details_insurance_success(self):
        """Test successful retrieval of an air reservation with insurance."""
        details = get_reservation_details(record_locator='AA7B8C')
        self.assertIsNotNone(details)
        self.assertEqual(details['record_locator'], 'AA7B8C')
        self.assertEqual(details['insurance'], 'yes')

    def test_get_reservation_details_hotel_success(self):
        """Test successful retrieval of a hotel reservation."""
        details = get_reservation_details(record_locator='BA4F5E')
        self.assertIsNotNone(details)
        self.assertEqual(details['record_locator'], 'BA4F5E')
        self.assertEqual(details['user_id'], 'test_user_2')
        self.assertEqual(details['segments'][0]['type'], 'HOTEL')
        self.assertEqual(details['segments'][0]['vendor_name'], 'Grand Hyatt')

    def test_get_reservation_details_car_success(self):
        """Test successful retrieval of a car rental reservation."""
        details = get_reservation_details(record_locator='HZ9D8F')
        self.assertIsNotNone(details)
        self.assertEqual(details['record_locator'], 'HZ9D8F')
        self.assertEqual(details['user_id'], 'test_user_1')
        self.assertEqual(details['segments'][0]['type'], 'CAR')
        self.assertEqual(details['segments'][0]['vendor_name'], 'Hertz')

    def test_get_reservation_details_not_found(self):
        """Tests that a non-existent reservation raises BookingNotFoundError."""
        self.assert_error_behavior(
            get_reservation_details,
            expected_exception_type=BookingNotFoundError,
            expected_message='Booking with record locator WRONGCONFIRM not found',
            record_locator='WRONGCONFIRM'
        )

    def test_get_reservation_details_invalid_input(self):
        """Tests that invalid input raises ValidationError."""
        self.assert_error_behavior(
                get_reservation_details,
                expected_exception_type=ValidationError,
                expected_message='record_locator is required',
                record_locator=''
            )
        self.assert_error_behavior(
            get_reservation_details,
            expected_exception_type=ValidationError,
            expected_message='record_locator is required',
            record_locator=None
        )

if __name__ == '__main__':
    unittest.main() 