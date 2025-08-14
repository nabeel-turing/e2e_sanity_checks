"""Test cases for Supabase organization-related functions."""
import unittest
import copy
from typing import Dict, Any

from ..SimulationEngine.db import DB
from ..SimulationEngine import custom_errors
from ..organization import get_organization
from common_utils.base_case import BaseTestCaseWithErrorHandler


# Initial database state for get_organization tests
GET_ORGANIZATION_INITIAL_DB_STATE = {
    "organizations": [
        {
            "id": "org_abc123",
            "name": "Acme Corp",
            "created_at": "2023-01-15T10:00:00Z",
            "subscription_plan": {
                "id": "plan_pro",
                "name": "Pro Plan",
                "price": 25.00,
                "currency": "USD",
                "features": [
                    "unlimited_projects",
                    "priority_support",
                    "daily_backups",
                    "branching_enabled"
                ]
            }
        },
        {
            "id": "org_xyz789",
            "name": "Innovate Solutions",
            "created_at": "2022-05-20T14:30:00Z",
            "subscription_plan": {
                "id": "plan_free",
                "name": "Free Tier",
                "price": 0.00,
                "currency": "USD",
                "features": [
                    "limited_projects",
                    "community_support"
                ]
            }
        },
        {
            "id": "org_special123",
            "name": "Test & Special-Chars Inc!",
            "created_at": "2023-06-10T08:45:00Z",
            "subscription_plan": {
                "id": "plan_enterprise",
                "name": "Enterprise",
                "price": 199.99,
                "currency": "USD",
                "features": [
                    "unlimited_everything",
                    "24/7_support",
                    "custom_integrations",
                    "sla_guarantee"
                ]
            }
        }
    ],
    "projects": [],
    "tables": {},
    "extensions": {},
    "migrations": {},
    "edge_functions": {},
    "branches": {},
    "costs": {},
    "unconfirmed_costs": {},
    "project_urls": {},
    "project_anon_keys": {},
    "project_ts_types": {},
    "logs": {}
}


class TestGetOrganization(BaseTestCaseWithErrorHandler):
    """Test suite for the get_organization function."""

    @classmethod
    def setUpClass(cls):
        """Save original DB state and set up initial test state."""
        cls.original_db_state = copy.deepcopy(DB)
        DB.clear()
        DB.update(copy.deepcopy(GET_ORGANIZATION_INITIAL_DB_STATE))

    @classmethod
    def tearDownClass(cls):
        """Restore original DB state."""
        DB.clear()
        DB.update(cls.original_db_state)

    def test_get_organization_success_pro_plan(self):
        """Test successful retrieval of organization with Pro plan."""
        org_info = get_organization(id='org_abc123')
        expected = {
            'id': 'org_abc123',
            'name': 'Acme Corp',
            'slug': 'acme-corp',
            'created_at': '2023-01-15T10:00:00Z',
            'subscription_plan': {
                'id': 'plan_pro',
                'name': 'Pro Plan',
                'price': 25.00,
                'currency': 'USD',
                'features': [
                    'unlimited_projects',
                    'priority_support',
                    'daily_backups',
                    'branching_enabled'
                ]
            }
        }
        self.assertEqual(org_info, expected)

    def test_get_organization_success_free_tier(self):
        """Test successful retrieval of organization with Free tier."""
        org_info = get_organization(id='org_xyz789')
        expected = {
            'id': 'org_xyz789',
            'name': 'Innovate Solutions',
            'slug': 'innovate-solutions',
            'created_at': '2022-05-20T14:30:00Z',
            'subscription_plan': {
                'id': 'plan_free',
                'name': 'Free Tier',
                'price': 0.00,
                'currency': 'USD',
                'features': [
                    'limited_projects',
                    'community_support'
                ]
            }
        }
        self.assertEqual(org_info, expected)

    def test_get_organization_special_chars_in_name(self):
        """Test organization name with special characters converts to proper slug."""
        org_info = get_organization(id='org_special123')
        self.assertEqual(org_info['name'], 'Test & Special-Chars Inc!')
        self.assertEqual(org_info['slug'], 'test-special-chars-inc')

    def test_get_organization_not_found(self):
        """Test error when organization ID does not exist."""
        self.assert_error_behavior(
            get_organization,
            custom_errors.NotFoundError,
            'No organization found against this id: org_nonexistent',
            id='org_nonexistent'
        )

    def test_get_organization_empty_id(self):
        """Test error when ID is empty string."""
        self.assert_error_behavior(
            get_organization,
            custom_errors.ValidationError,
            'The id parameter can not be null or empty',
            id=''
        )

    def test_get_organization_none_id(self):
        """Test error when ID is None."""
        self.assert_error_behavior(
            get_organization,
            custom_errors.ValidationError,
            'The id parameter can not be null or empty',
            id=None
        )

    def test_get_organization_non_string_id(self):
        """Test error when ID is not a string."""
        self.assert_error_behavior(
            get_organization,
            custom_errors.ValidationError,
            'id must be string type',
            id=123
        )

    def test_get_organization_list_id(self):
        """Test error when ID is a list."""
        self.assert_error_behavior(
            get_organization,
            custom_errors.ValidationError,
            'id must be string type',
            id=['org_abc123']
        )

    def test_get_organization_dict_id(self):
        """Test error when ID is a dictionary."""
        self.assert_error_behavior(
            get_organization,
            custom_errors.ValidationError,
            'id must be string type',
            id={'id': 'org_abc123'}
        )

    def test_get_organization_response_structure(self):
        """Test that response matches expected structure with all required fields."""
        org_info = get_organization(id='org_abc123')
        
        # Check top-level keys
        required_keys = {'id', 'name', 'slug', 'created_at', 'subscription_plan'}
        self.assertEqual(set(org_info.keys()), required_keys)
        
        # Check subscription_plan structure
        subscription_keys = {'id', 'name', 'price', 'currency', 'features'}
        self.assertEqual(set(org_info['subscription_plan'].keys()), subscription_keys)
        
        # Check data types
        self.assertIsInstance(org_info['id'], str)
        self.assertIsInstance(org_info['name'], str)
        self.assertIsInstance(org_info['slug'], str)
        self.assertIsInstance(org_info['created_at'], str)
        self.assertIsInstance(org_info['subscription_plan'], dict)
        self.assertIsInstance(org_info['subscription_plan']['features'], list)
        self.assertIsInstance(org_info['subscription_plan']['price'], float)

    def test_get_organization_enterprise_plan(self):
        """Test organization with enterprise plan and complex features."""
        org_info = get_organization(id='org_special123')
        
        # Verify enterprise plan details
        self.assertEqual(org_info['subscription_plan']['id'], 'plan_enterprise')
        self.assertEqual(org_info['subscription_plan']['name'], 'Enterprise')
        self.assertEqual(org_info['subscription_plan']['price'], 199.99)
        self.assertEqual(len(org_info['subscription_plan']['features']), 4)
        self.assertIn('sla_guarantee', org_info['subscription_plan']['features'])

    def test_get_organization_iso_timestamp_format(self):
        """Test that created_at field is in ISO 8601 format."""
        org_info = get_organization(id='org_abc123')
        created_at = org_info['created_at']
        
        # Should match ISO 8601 format with 'Z' timezone
        self.assertTrue(created_at.endswith('Z'))
        self.assertIn('T', created_at)
        self.assertEqual(len(created_at), 20)  # YYYY-MM-DDTHH:MM:SSZ

    def test_get_organization_float_price_precision(self):
        """Test that price maintains proper decimal precision."""
        org_info = get_organization(id='org_xyz789')
        self.assertEqual(org_info['subscription_plan']['price'], 0.00)
        self.assertIsInstance(org_info['subscription_plan']['price'], float)
        
        org_info2 = get_organization(id='org_special123')
        self.assertEqual(org_info2['subscription_plan']['price'], 199.99)


if __name__ == '__main__':
    unittest.main()