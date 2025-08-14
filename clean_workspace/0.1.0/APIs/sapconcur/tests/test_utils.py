import unittest
from unittest.mock import patch
import uuid
from pydantic import ValidationError

from .. import DB
from sapconcur.SimulationEngine import utils
from common_utils.base_case import BaseTestCaseWithErrorHandler

class TestCreateUser(BaseTestCaseWithErrorHandler):

    def setUp(self):
        """Set up a clean DB for each test."""
        # Reset database to clean state
        DB.clear()
        DB.update({
            "users": {}
        })

    def test_create_user_with_required_fields(self):
        """Test creating a user with only the required fields."""
        user = utils.create_user(
            given_name="John",
            family_name="Doe",
            user_name="johndoe",
            active=True,
            email="johndoe@example.com",
            locale="en-US",
            timezone="UTC"
        )
        with patch('sapconcur.SimulationEngine.utils.DB', DB):
            user = utils.create_user(
                given_name="John",
                family_name="Doe",
                user_name="johndoe",
                active=True,
                email="johndoe@example.com",
                locale="en-US",
                timezone="UTC"
            )
        self.assertIn(str(user['id']), DB['users'])

    def test_create_user_with_all_fields(self):
        """Test creating a user with all optional fields provided."""
        payment_methods_data = {
            "credit_card_1234": {
                "brand": "visa",
                "last_four": "1234"
            },
            "credit_card_5678": {
                "brand": "mastercard",
                "last_four": "5678"
            }
        }
        
        user_data = {
            "given_name": "Jane",
            "family_name": "Smith",
            "user_name": "janesmith",
            "active": True,
            "email": "jane@example.com",
            "locale": "en-GB",
            "timezone": "Europe/London",
            "external_id": "ext-123",
            "display_name": "Jane S.",
            "membership": "platinum",
            "payment_methods": payment_methods_data
        }
        with patch('sapconcur.SimulationEngine.utils.DB', DB):
            user = utils.create_user(**user_data)
        
        self.assertIn(str(user['id']), DB['users'])
        stored_user = DB['users'][str(user['id'])]
        self.assertEqual(stored_user['display_name'], "Jane S.")
        self.assertEqual(stored_user['external_id'], "ext-123")
        self.assertEqual(stored_user['membership'], "platinum")
        
        # Test payment methods
        self.assertIn('payment_methods', stored_user)
        self.assertEqual(len(stored_user['payment_methods']), 2)
        self.assertIn('credit_card_1234', stored_user['payment_methods'])
        self.assertIn('credit_card_5678', stored_user['payment_methods'])
        
        # Test credit card structures
        credit_card_1 = stored_user['payment_methods']['credit_card_1234']
        self.assertEqual(credit_card_1['source'], 'credit_card')
        self.assertEqual(credit_card_1['brand'], 'visa')
        self.assertEqual(credit_card_1['last_four'], '1234')
        
        credit_card_2 = stored_user['payment_methods']['credit_card_5678']
        self.assertEqual(credit_card_2['source'], 'credit_card')
        self.assertEqual(credit_card_2['brand'], 'mastercard')
        self.assertEqual(credit_card_2['last_four'], '5678')

    def test_create_user_invalid_data_raises_error(self):
        """Test that creating a user with invalid data raises a ValidationError."""
        with patch('sapconcur.SimulationEngine.utils.DB', DB):
            self.assert_error_behavior(
                utils.create_user,
                ValidationError,
                "Input should be a valid string",
                given_name=123,
                family_name="Doe",
                user_name="johndoe",
                active=None,
                email="johndoe@example.com",
                locale="en-US",
                timezone="UTC"
            )
            
            
    def test_create_user_stores_correct_data(self):
        """Test that the data stored in the DB is correct."""
        user_data = {
            "given_name": "Test",
            "family_name": "User",
            "user_name": "testuser",
            "active": False,
            "email": "test@domain.com",
            "locale": "fr-FR",
            "timezone": "Europe/Paris",
        }
        with patch('sapconcur.SimulationEngine.utils.DB', DB):
            created_user = utils.create_user(**user_data)
        
        stored_user = DB['users'][str(created_user['id'])]
        
        self.assertEqual(stored_user['given_name'], user_data['given_name'])
        self.assertEqual(stored_user['active'], user_data['active'])
        self.assertIn('created_at', stored_user)
        self.assertIn('last_modified', stored_user)

    def test_create_user_with_membership_only(self):
        """Test creating a user with membership but no payment methods."""
        user_data = {
            "given_name": "Gold",
            "family_name": "Member",
            "user_name": "goldmember",
            "active": True,
            "email": "gold@example.com",
            "locale": "en-US",
            "timezone": "UTC",
            "membership": "gold"
        }
        with patch('sapconcur.SimulationEngine.utils.DB', DB):
            user = utils.create_user(**user_data)
        
        stored_user = DB['users'][str(user['id'])]
        self.assertEqual(stored_user['membership'], 'gold')
        self.assertEqual(stored_user['payment_methods'], {})

    def test_create_user_no_optional_fields(self):
        """Test creating a user with no optional fields sets correct defaults."""
        user_data = {
            "given_name": "Basic",
            "family_name": "User",
            "user_name": "basicuser",
            "active": True,
            "email": "basic@example.com",
            "locale": "en-US",
            "timezone": "UTC"
        }
        with patch('sapconcur.SimulationEngine.utils.DB', DB):
            user = utils.create_user(**user_data)
        
        stored_user = DB['users'][str(user['id'])]
        self.assertIsNone(stored_user['membership'])
        self.assertEqual(stored_user['payment_methods'], {})
        self.assertIsNone(stored_user['external_id'])
        self.assertIsNone(stored_user['display_name'])

if __name__ == '__main__':
    unittest.main() 