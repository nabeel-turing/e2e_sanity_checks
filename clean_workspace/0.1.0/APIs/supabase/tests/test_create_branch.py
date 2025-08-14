import unittest
import copy
from datetime import datetime, timezone, timedelta
from ..SimulationEngine import custom_errors
from ..branch import create_branch
from ..SimulationEngine.db import DB
from common_utils.base_case import BaseTestCaseWithErrorHandler

class TestCreateBranch(BaseTestCaseWithErrorHandler):

    def setUp(self):
        self._original_DB_state = copy.deepcopy(DB)
        DB.clear()
        self.org_id_with_branching = 'org_001_branching_enabled'
        self.org_id_without_branching = 'org_002_branching_disabled'
        self.project_id_main = 'proj_main_001'
        self.project_id_no_branching_feature_org = 'proj_main_002'
        self.project_id_org_not_found_in_db = 'proj_main_003'
        current_time = datetime.now(timezone.utc)
        self.iso_current_time_str = current_time.isoformat()
        DB['organizations'] = [{'id': self.org_id_with_branching, 'name': 'Org With Branching', 'created_at': current_time - timedelta(days=10), 'subscription_plan': {'id': 'plan_pro_test', 'name': 'Pro Plan Test', 'price': 25.0, 'currency': 'USD', 'features': ['branching_enabled', 'another_feature']}}, {'id': self.org_id_without_branching, 'name': 'Org No Branching', 'created_at': current_time - timedelta(days=10), 'subscription_plan': {'id': 'plan_free_test', 'name': 'Free Plan Test', 'price': 0.0, 'currency': 'USD', 'features': ['basic_feature']}}]
        DB['projects'] = [{'id': self.project_id_main, 'name': 'Main Project Alpha', 'organization_id': self.org_id_with_branching, 'region': 'us-west-1', 'status': 'ACTIVE', 'created_at': current_time - timedelta(days=5)}, {'id': self.project_id_no_branching_feature_org, 'name': 'Project Beta (No Branching Org)', 'organization_id': self.org_id_without_branching, 'region': 'us-east-1', 'status': 'ACTIVE', 'created_at': current_time - timedelta(days=5)}, {'id': self.project_id_org_not_found_in_db, 'name': 'Project Gamma (Org Not Found)', 'organization_id': 'org_non_existent_004', 'region': 'eu-central-1', 'status': 'ACTIVE', 'created_at': current_time - timedelta(days=5)}]
        DB['branches'] = {}
        self.cost_id_valid_1 = 'cost_confirm_branch_valid_001'
        self.cost_id_valid_2 = 'cost_confirm_branch_valid_002'
        self.cost_id_project_type = 'cost_confirm_project_type_003'
        self.cost_id_to_be_used = 'cost_confirm_branch_reusable_004'
        DB['costs'] = {self.cost_id_valid_1: {'type': 'branch', 'amount': 0.01344, 'currency': 'USD', 'recurrence': 'hourly', 'description': 'Branch creation cost for test 1', 'confirmation_id': self.cost_id_valid_1}, self.cost_id_valid_2: {'type': 'branch', 'amount': 0.01344, 'currency': 'USD', 'recurrence': 'hourly', 'description': 'Branch creation cost for test 2', 'confirmation_id': self.cost_id_valid_2}, self.cost_id_project_type: {'type': 'project', 'amount': 10.0, 'currency': 'USD', 'recurrence': 'monthly', 'description': 'Project creation cost (wrong type)', 'confirmation_id': self.cost_id_project_type}, self.cost_id_to_be_used: {'type': 'branch', 'amount': 0.01344, 'currency': 'USD', 'recurrence': 'hourly', 'description': 'Cost to be marked as used', 'confirmation_id': self.cost_id_to_be_used}}
        DB['used_cost_ids'] = []
        DB['unconfirmed_costs'] = {}
        DB['project_urls'] = {}
        DB['project_anon_keys'] = {}
        DB['project_ts_types'] = {}
        DB['logs'] = {}
        DB['tables'] = {}
        DB['extensions'] = {}
        DB['migrations'] = {}
        DB['edge_functions'] = {}

    def tearDown(self):
        DB.clear()
        DB.update(self._original_DB_state)

    def _assert_iso_format_and_recent(self, timestamp_str, max_delta_seconds=5):
        try:
            if timestamp_str.endswith('Z'):
                dt_obj = datetime.fromisoformat(timestamp_str[:-1] + '+00:00')
            else:
                dt_obj = datetime.fromisoformat(timestamp_str)
            self.assertIsNotNone(dt_obj)
            self.assertEqual(dt_obj.tzinfo, timezone.utc, 'Timestamp should be UTC.')
        except ValueError:
            self.fail(f"Timestamp '{timestamp_str}' is not a valid ISO 8601 string.")

    def test_create_branch_success_default_name(self):
        result = create_branch(project_id=self.project_id_main, confirm_cost_id=self.cost_id_valid_1)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['name'], 'develop')
        self.assertEqual(result['parent_project_id'], self.project_id_main)
        self.assertIsInstance(result['id'], str)
        self.assertTrue(len(result['id']) > 10, 'Branch ID seems too short.')
        self.assertIsInstance(result['branch_project_id'], str)
        self.assertTrue(len(result['branch_project_id']) > 10, 'Branch project ID seems too short.')
        self.assertNotEqual(result['id'], result['branch_project_id'])
        self.assertIn(result['status'], ['CREATING', 'ACTIVE'])
        self._assert_iso_format_and_recent(result['created_at'])
        self.assertIn(self.project_id_main, DB['branches'])
        project_branches = DB['branches'][self.project_id_main]
        self.assertEqual(len(project_branches), 1)
        db_branch = project_branches[0]
        self.assertEqual(db_branch['id'], result['id'])
        self.assertEqual(db_branch['name'], 'develop')
        self.assertEqual(db_branch['parent_project_id'], self.project_id_main)
        self.assertEqual(db_branch['branch_project_id'], result['branch_project_id'])
        self.assertEqual(db_branch['status'], result['status'])
        self.assertIsInstance(db_branch['created_at'], datetime)
        self.assertIsInstance(db_branch['last_activity_at'], datetime)
        self.assertNotIn(self.cost_id_valid_1, DB['costs'], 'Cost ID should be consumed.')

    def test_create_branch_success_custom_name(self):
        custom_name = 'feature-new-ux-final'
        result = create_branch(project_id=self.project_id_main, confirm_cost_id=self.cost_id_valid_2, name=custom_name)
        self.assertEqual(result['name'], custom_name)
        self.assertEqual(result['parent_project_id'], self.project_id_main)
        self.assertIsInstance(result['id'], str)
        self.assertTrue(len(result['id']) > 0)
        self.assertIsInstance(result['branch_project_id'], str)
        self.assertTrue(len(result['branch_project_id']) > 0)
        self.assertIn(result['status'], ['CREATING', 'ACTIVE'])
        self._assert_iso_format_and_recent(result['created_at'])
        self.assertIn(self.project_id_main, DB['branches'])
        db_branch = DB['branches'][self.project_id_main][0]
        self.assertEqual(db_branch['name'], custom_name)
        self.assertNotIn(self.cost_id_valid_2, DB['costs'])

    def test_create_branch_with_existing_schema(self):
        """Test that a new branch correctly inherits the parent's schema."""
        # Setup: Add some schema to the parent project
        parent_project_id = self.project_id_main
        DB['tables'][parent_project_id] = [
            {'name': 'parent_table_1', 'schema': 'public', 'columns': []},
            {'name': 'parent_table_2', 'schema': 'private', 'columns': []},
        ]
        DB['migrations'][parent_project_id] = [
            {'version': '1', 'status': 'APPLIED'},
            {'version': '2', 'status': 'APPLIED'},
        ]
        DB['extensions'][parent_project_id] = [
            {'name': 'pg_cron', 'version': '1.4'},
        ]

        # Act: Create the branch
        result = create_branch(project_id=parent_project_id, confirm_cost_id=self.cost_id_valid_1)
        branch_project_id = result['branch_project_id']

        # Assert: Check that the schema was copied
        self.assertIn(branch_project_id, DB['tables'])
        self.assertEqual(len(DB['tables'][branch_project_id]), 2)
        self.assertEqual(DB['tables'][branch_project_id][0]['name'], 'parent_table_1')

        self.assertIn(branch_project_id, DB['migrations'])
        self.assertEqual(len(DB['migrations'][branch_project_id]), 2)
        self.assertEqual(DB['migrations'][branch_project_id][0]['status'], 'APPLIED_SUCCESSFULLY')

        self.assertIn(branch_project_id, DB['extensions'])
        self.assertEqual(len(DB['extensions'][branch_project_id]), 1)
        self.assertEqual(DB['extensions'][branch_project_id][0]['name'], 'pg_cron')

    def test_create_multiple_branches_for_same_project_generates_unique_ids(self):
        result1 = create_branch(project_id=self.project_id_main, confirm_cost_id=self.cost_id_valid_1, name='branch-alpha')
        cost_id_for_branch_beta = 'cost_temp_beta_005'
        DB['costs'][cost_id_for_branch_beta] = {'type': 'branch', 'amount': 0.01344, 'currency': 'USD', 'recurrence': 'hourly', 'description': 'Cost for branch beta', 'confirmation_id': cost_id_for_branch_beta}
        result2 = create_branch(project_id=self.project_id_main, confirm_cost_id=cost_id_for_branch_beta, name='branch-beta')
        self.assertNotEqual(result1['id'], result2['id'], 'Branch IDs must be unique.')
        self.assertNotEqual(result1['branch_project_id'], result2['branch_project_id'], 'Branch project IDs must be unique.')
        project_branches = DB['branches'][self.project_id_main]
        self.assertEqual(len(project_branches), 2)
        self.assertEqual(project_branches[0]['name'], 'branch-alpha')
        self.assertEqual(project_branches[1]['name'], 'branch-beta')
        self.assertNotIn(self.cost_id_valid_1, DB['costs'])
        self.assertNotIn(cost_id_for_branch_beta, DB['costs'])

    def test_create_branch_error_parent_project_not_found(self):
        non_existent_project_id = 'proj_non_existent_id_123'
        self.assert_error_behavior(func_to_call=create_branch, expected_exception_type=custom_errors.NotFoundError, expected_message=f"Parent project with ID '{non_existent_project_id}' not found.", project_id=non_existent_project_id, confirm_cost_id=self.cost_id_valid_1, name='develop')

    def test_create_branch_error_validation_project_id_is_none(self):
        self.assert_error_behavior(func_to_call=create_branch, expected_exception_type=custom_errors.ValidationError, expected_message='Input validation failed: project_id cannot be None or empty.', project_id=None, confirm_cost_id=self.cost_id_valid_1, name='develop')

    def test_create_branch_error_validation_confirm_cost_id_is_none(self):
        self.assert_error_behavior(func_to_call=create_branch, expected_exception_type=custom_errors.ValidationError, expected_message='Input validation failed: confirm_cost_id cannot be None or empty.', project_id=self.project_id_main, confirm_cost_id=None, name='develop')

    def test_create_branch_error_validation_branch_name_empty(self):
        self.assert_error_behavior(func_to_call=create_branch, expected_exception_type=custom_errors.ValidationError, expected_message='Input validation failed: Branch name cannot be empty.', project_id=self.project_id_main, confirm_cost_id=self.cost_id_valid_1, name='')

    def test_create_branch_error_cost_confirmation_id_not_found(self):
        invalid_cost_id = 'invalid_cost_id_xyz789'
        self.assert_error_behavior(func_to_call=create_branch, expected_exception_type=custom_errors.CostConfirmationError, expected_message=f"Cost confirmation ID '{invalid_cost_id}' not found.", project_id=self.project_id_main, confirm_cost_id=invalid_cost_id, name='develop')

    def test_create_branch_error_cost_confirmation_id_wrong_type(self):
        self.assert_error_behavior(func_to_call=create_branch, expected_exception_type=custom_errors.CostConfirmationError, expected_message=f"Cost confirmation ID '{self.cost_id_project_type}' is for a 'project' operation, not 'branch'.", project_id=self.project_id_main, confirm_cost_id=self.cost_id_project_type, name='develop')

    def test_create_branch_error_branching_not_enabled_for_project_organization(self):
        self.assert_error_behavior(func_to_call=create_branch, expected_exception_type=custom_errors.BranchingNotEnabledError, expected_message=f"Branching feature is not enabled for the organization of project '{self.project_id_no_branching_feature_org}'.", project_id=self.project_id_no_branching_feature_org, confirm_cost_id=self.cost_id_valid_1, name='develop')
        self.assertIn(self.cost_id_valid_1, DB['costs'], 'Cost ID should not be consumed on this type of failure.')

    def test_create_branch_error_project_organization_not_found_in_db(self):
        expected_organization_id = 'org_non_existent_004'
        self.assert_error_behavior(func_to_call=create_branch, expected_exception_type=custom_errors.NotFoundError, expected_message=f"Organization '{expected_organization_id}' associated with project '{self.project_id_org_not_found_in_db}' not found.", project_id=self.project_id_org_not_found_in_db, confirm_cost_id=self.cost_id_valid_1, name='develop')
        self.assertIn(self.cost_id_valid_1, DB['costs'])

if __name__ == '__main__':
    unittest.main()