import unittest
import copy
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from unittest import mock

from common_utils.base_case import BaseTestCaseWithErrorHandler
from github_actions.SimulationEngine.custom_errors import NotFoundError, InvalidInputError
from github_actions.list_workflow_runs_module import list_workflow_runs 
from github_actions.SimulationEngine.db import DB
from github_actions.SimulationEngine import utils 
from github_actions.SimulationEngine.models import (
    ActorType, WorkflowState, WorkflowRunStatus, JobStatus, StepStatus,
    WorkflowRunConclusion, JobConclusion, StepConclusion
)
from github_actions.SimulationEngine.utils import _parse_created_filter 

def dt_to_iso_z(dt_obj: Optional[Any]) -> Optional[str]:
    if dt_obj is None: return None
    if isinstance(dt_obj, str): return dt_obj 
    if not isinstance(dt_obj, datetime):
        raise TypeError(f"Expected datetime or string for dt_to_iso_z, got {type(dt_obj)}")
    dt_utc = dt_obj.astimezone(timezone.utc) if dt_obj.tzinfo else dt_obj.replace(tzinfo=timezone.utc)
    return dt_utc.isoformat(timespec='microseconds').replace('+00:00', 'Z')

class TestListWorkflowRuns(BaseTestCaseWithErrorHandler):
    def setUp(self):
        self.DB_backup = copy.deepcopy(DB)
        DB.clear()
        DB['repositories'] = {}
        DB['next_repo_id'] = 1; DB['next_workflow_id'] = 1; DB['next_run_id'] = 1; 
        DB['next_job_id'] = 1; DB['next_user_id'] = 1

        self.owner_login = 'testOwner'
        self.repo_name = 'Test-Repo'
        self.owner_data_dict = {'login': self.owner_login, 'id': 1, 'node_id': 'U_OWNER_1', 'type': ActorType.USER.value, 'site_admin': False}
        self.repo_dict_in_db = utils.add_repository(owner=self.owner_data_dict, repo_name=self.repo_name)
        self.repo_key = f"{self.owner_login.lower()}/{self.repo_name.lower()}"

        self.actor1_data = {'login': 'actorOne', 'id': 10, 'node_id': 'U_ACTOR_10', 'type': ActorType.USER.value, 'site_admin': False}
        self.actor2_data = {'login': 'actorTwo', 'id': 11, 'node_id': 'U_ACTOR_11', 'type': ActorType.USER.value, 'site_admin': False}

        wf1_def = {'name': 'CI Build', 'path': '.github/workflows/ci.yml', 'state': WorkflowState.ACTIVE.value}
        self.wf1 = utils.add_or_update_workflow(self.owner_login, self.repo_name, wf1_def)
        wf2_def = {'name': 'Deploy Prod', 'path': '.github/workflows/deploy.yml', 'state': WorkflowState.ACTIVE.value}
        self.wf2 = utils.add_or_update_workflow(self.owner_login, self.repo_name, wf2_def)

        self.run_inputs_with_datetime_objects = [] 
        self.runs_in_db_after_add = [] 
        
        time_now = datetime.now(timezone.utc)
        
        run1_input_dt = {
            'workflow_id': self.wf1['id'], 'head_sha': 'sha1', 'event': 'pull_request', 'status': WorkflowRunStatus.COMPLETED.value,
            'conclusion': WorkflowRunConclusion.SUCCESS.value, 'actor': self.actor1_data, 'head_branch': 'feature/A',
            'created_at': time_now - timedelta(days=5), 'updated_at': time_now - timedelta(days=5, hours=1),
            'check_suite_id': 1001
        }
        self.run_inputs_with_datetime_objects.append(run1_input_dt)
        self.runs_in_db_after_add.append(utils.add_workflow_run(self.owner_login, self.repo_name, copy.deepcopy(run1_input_dt)))

        run2_input_dt = {
            'workflow_id': self.wf1['id'], 'head_sha': 'sha2', 'event': 'push', 'status': WorkflowRunStatus.IN_PROGRESS.value,
            'actor': self.actor2_data, 'head_branch': 'main',
            'created_at': time_now - timedelta(days=3), 'updated_at': time_now - timedelta(days=2, hours=1)
        }
        self.run_inputs_with_datetime_objects.append(run2_input_dt)
        self.runs_in_db_after_add.append(utils.add_workflow_run(self.owner_login, self.repo_name, copy.deepcopy(run2_input_dt)))

        self.run3_created_at_obj = time_now - timedelta(days=1)
        run3_input_dt = {
            'workflow_id': self.wf2['id'], 'head_sha': 'sha3', 'event': 'schedule', 'status': WorkflowRunStatus.COMPLETED.value,
            'conclusion': WorkflowRunConclusion.FAILURE.value, 'actor': self.actor1_data, 'head_branch': 'main',
            'created_at': self.run3_created_at_obj, 'updated_at': time_now - timedelta(days=1, hours=1)
        }
        self.run_inputs_with_datetime_objects.append(run3_input_dt)
        self.runs_in_db_after_add.append(utils.add_workflow_run(self.owner_login, self.repo_name, copy.deepcopy(run3_input_dt)))
        
        run4_input_dt = {
            'workflow_id': self.wf1['id'], 'head_sha': 'sha4', 'event': 'push', 'status': WorkflowRunStatus.COMPLETED.value,
            'conclusion': WorkflowRunConclusion.SUCCESS.value, 'actor': self.actor1_data, 'head_branch': 'feature/B',
            'created_at': time_now - timedelta(days=10), 'updated_at': time_now - timedelta(days=10, hours=1),
            'check_suite_id': 1002
        }
        self.run_inputs_with_datetime_objects.append(run4_input_dt)
        self.runs_in_db_after_add.append(utils.add_workflow_run(self.owner_login, self.repo_name, copy.deepcopy(run4_input_dt)))

        self.all_runs_sorted_expected_from_db = sorted(self.runs_in_db_after_add, key=lambda r: r['created_at'], reverse=True)

    def tearDown(self):
        DB.clear()
        DB.update(self.DB_backup)

    def assert_run_lists_equal(self, result_runs_api: List[Dict], expected_runs_from_db: List[Dict]):
        self.assertEqual(len(result_runs_api), len(expected_runs_from_db))
        result_ids = {r['id'] for r in result_runs_api}
        expected_ids = {r['id'] for r in expected_runs_from_db}
        self.assertEqual(result_ids, expected_ids, "Mismatch in run IDs")
        for res_run in result_runs_api:
            expected_run_match = next((er for er in expected_runs_from_db if er['id'] == res_run['id']), None)
            self.assertIsNotNone(expected_run_match)
            self.assertEqual(res_run, expected_run_match)

    def test_list_all_runs_default_pagination(self):
        result = list_workflow_runs(owner=self.owner_login, repo=self.repo_name)
        self.assertEqual(result['total_count'], 4)
        self.assertEqual(len(result['workflow_runs']), 4)
        self.assert_run_lists_equal(result['workflow_runs'], self.all_runs_sorted_expected_from_db)

    def test_filter_by_workflow_id_int(self):
        result = list_workflow_runs(owner=self.owner_login, repo=self.repo_name, workflow_id=self.wf1['id'])
        expected = [r for r in self.all_runs_sorted_expected_from_db if r['workflow_id'] == self.wf1['id']]
        self.assertEqual(result['total_count'], len(expected))
        self.assert_run_lists_equal(result['workflow_runs'], expected)

    def test_filter_by_workflow_filename(self):
        result = list_workflow_runs(owner=self.owner_login, repo=self.repo_name, workflow_id=self.wf2['path'])
        expected = [r for r in self.all_runs_sorted_expected_from_db if r['workflow_id'] == self.wf2['id']]
        self.assertEqual(result['total_count'], len(expected))
        self.assert_run_lists_equal(result['workflow_runs'], expected)

    def test_filter_by_workflow_id_string_digit(self):
        result = list_workflow_runs(owner=self.owner_login, repo=self.repo_name, workflow_id=str(self.wf1['id']))
        expected = [r for r in self.all_runs_sorted_expected_from_db if r['workflow_id'] == self.wf1['id']]
        self.assertEqual(result['total_count'], len(expected))
        self.assert_run_lists_equal(result['workflow_runs'], expected)

    def test_filter_by_actor(self):
        result = list_workflow_runs(owner=self.owner_login, repo=self.repo_name, actor='actorTwo')
        expected = [r for r in self.all_runs_sorted_expected_from_db if r.get('actor') and r['actor']['login'] == 'actorTwo']
        self.assertEqual(result['total_count'], len(expected))
        self.assert_run_lists_equal(result['workflow_runs'], expected)

    def test_filter_by_branch(self):
        result = list_workflow_runs(owner=self.owner_login, repo=self.repo_name, branch='feature/A')
        expected = [r for r in self.all_runs_sorted_expected_from_db if r.get('head_branch') == 'feature/A']
        self.assertEqual(result['total_count'], len(expected))
        self.assert_run_lists_equal(result['workflow_runs'], expected)

    def test_filter_by_event(self):
        result = list_workflow_runs(owner=self.owner_login, repo=self.repo_name, event='push')
        expected = [r for r in self.all_runs_sorted_expected_from_db if r['event'] == 'push']
        self.assertEqual(result['total_count'], len(expected))
        self.assert_run_lists_equal(result['workflow_runs'], expected)

    def test_filter_by_status(self):
        result = list_workflow_runs(owner=self.owner_login, repo=self.repo_name, status=WorkflowRunStatus.COMPLETED.value)
        expected = [r for r in self.all_runs_sorted_expected_from_db if r['status'] == WorkflowRunStatus.COMPLETED.value]
        self.assertEqual(result['total_count'], len(expected))
        self.assert_run_lists_equal(result['workflow_runs'], expected)

    def test_filter_exclude_pull_requests(self):
        result = list_workflow_runs(owner=self.owner_login, repo=self.repo_name, exclude_pull_requests=True)
        expected = [r for r in self.all_runs_sorted_expected_from_db if r['event'] != 'pull_request']
        self.assertEqual(result['total_count'], len(expected))
        self.assert_run_lists_equal(result['workflow_runs'], expected)

    def test_filter_by_check_suite_id(self):
        result = list_workflow_runs(owner=self.owner_login, repo=self.repo_name, check_suite_id=1001)
        expected = [r for r in self.all_runs_sorted_expected_from_db if r.get('check_suite_id') == 1001]
        self.assertEqual(result['total_count'], len(expected))
        self.assert_run_lists_equal(result['workflow_runs'], expected)

    def test_filter_by_created_exact_date(self):
        target_date_obj = self.run_inputs_with_datetime_objects[2]['created_at']
        target_date_str = target_date_obj.strftime('%Y-%m-%d')
        
        result = list_workflow_runs(owner=self.owner_login, repo=self.repo_name, created=target_date_str)
        
        run3_id_from_db = self.runs_in_db_after_add[2]['id']
        expected = [r for r in self.all_runs_sorted_expected_from_db if r['id'] == run3_id_from_db]
        
        self.assertEqual(result['total_count'], len(expected))
        self.assert_run_lists_equal(result['workflow_runs'], expected)

    def test_filter_by_created_date_range(self):
        start_date_obj = datetime.now(timezone.utc) - timedelta(days=6)
        end_date_obj = datetime.now(timezone.utc) 
        start_date_str = start_date_obj.strftime('%Y-%m-%d')
        end_date_str = end_date_obj.strftime('%Y-%m-%d')
        
        result = list_workflow_runs(owner=self.owner_login, repo=self.repo_name, created=f"{start_date_str}..{end_date_str}")
        
        parsed_range = utils._parse_created_filter(f"{start_date_str}..{end_date_str}")
        start_dt_range = parsed_range['start_date']
        end_dt_range = parsed_range['end_date']

        expected_from_setup = []
        for i in range(len(self.run_inputs_with_datetime_objects)):
            created_dt_orig_obj = self.run_inputs_with_datetime_objects[i]['created_at']
            created_dt_utc = created_dt_orig_obj.astimezone(timezone.utc) if created_dt_orig_obj.tzinfo else created_dt_orig_obj.replace(tzinfo=timezone.utc)
            if start_dt_range <= created_dt_utc <= end_dt_range:
                expected_from_setup.append(self.runs_in_db_after_add[i])
        
        expected_from_setup_sorted = sorted(expected_from_setup, key=lambda r: r['created_at'], reverse=True)
        self.assertEqual(result['total_count'], len(expected_from_setup_sorted))
        self.assert_run_lists_equal(result['workflow_runs'], expected_from_setup_sorted)

    def test_filter_created_with_corrupted_date_in_db(self):
        valid_filter_date = datetime.now(timezone.utc) - timedelta(days=15)
        valid_run_input = {
            'workflow_id': self.wf1['id'], 'head_sha': 'valid_sha_for_corrupt_test', 'event': 'push', 
            'created_at': valid_filter_date, 'updated_at': valid_filter_date
        }
        valid_run_dict = utils.add_workflow_run(self.owner_login, self.repo_name, valid_run_input)
        valid_run_id = valid_run_dict['id']

        corrupted_run_id = DB['next_run_id']; DB['next_run_id'] +=1
        repo_data_for_brief = DB['repositories'][self.repo_key]
        run_repo_brief = {
            'id': repo_data_for_brief['id'], 'node_id': repo_data_for_brief['node_id'],
            'name': repo_data_for_brief['name'],
            'full_name': f"{repo_data_for_brief['owner']['login']}/{repo_data_for_brief['name']}",
            'private': repo_data_for_brief['private'], 'owner': repo_data_for_brief['owner']
        }
        corrupted_run_data_for_db = {
            'id': corrupted_run_id, 'name': 'Corrupted Run', 'node_id': f'CORRUPT_NODE_{corrupted_run_id}',
            'workflow_id': self.wf1['id'], 'path': self.wf1['path'], 'head_sha': 'corrupt_sha', 'event': 'push', 
            'created_at': "this-is-not-a-date", 
            'updated_at': dt_to_iso_z(valid_filter_date),
            'run_number': corrupted_run_id, 'run_attempt': 1, 'repository': run_repo_brief
        }
        DB['repositories'][self.repo_key]['workflow_runs'][str(corrupted_run_id)] = corrupted_run_data_for_db

        filter_date_str = valid_filter_date.strftime('%Y-%m-%d')
        result = list_workflow_runs(owner=self.owner_login, repo=self.repo_name, created=filter_date_str)
        
        self.assertEqual(result['total_count'], 1)
        self.assertEqual(len(result['workflow_runs']), 1)
        self.assertEqual(result['workflow_runs'][0]['id'], valid_run_id)
        
        del DB['repositories'][self.repo_key]['workflow_runs'][str(valid_run_id)]
        del DB['repositories'][self.repo_key]['workflow_runs'][str(corrupted_run_id)]

    def test_pagination(self):
        all_runs_from_db = list(DB['repositories'][self.repo_key]['workflow_runs'].values())
        sorted_runs_for_pagination = sorted(all_runs_from_db, key=lambda r: (r.get('created_at', "0"), r.get('id', 0)), reverse=True)

        result_p1 = list_workflow_runs(owner=self.owner_login, repo=self.repo_name, per_page=2, page=1)
        self.assertEqual(result_p1['total_count'], len(sorted_runs_for_pagination))
        self.assertEqual(len(result_p1['workflow_runs']), 2)
        self.assert_run_lists_equal(result_p1['workflow_runs'], sorted_runs_for_pagination[0:2])

        result_p2 = list_workflow_runs(owner=self.owner_login, repo=self.repo_name, per_page=2, page=2)
        self.assertEqual(result_p2['total_count'], len(sorted_runs_for_pagination))
        self.assertEqual(len(result_p2['workflow_runs']), 2)
        self.assert_run_lists_equal(result_p2['workflow_runs'], sorted_runs_for_pagination[2:4])

    def test_input_validation(self):
        with self.assertRaisesRegex(InvalidInputError, "Owner must be a non-empty string."):
            list_workflow_runs(owner="", repo=self.repo_name)
        with self.assertRaisesRegex(InvalidInputError, "Repo must be a non-empty string."):
            list_workflow_runs(owner=self.owner_login, repo="")
        with self.assertRaisesRegex(InvalidInputError, "Page number must be a positive integer."):
            list_workflow_runs(owner=self.owner_login, repo=self.repo_name, page=0)
        with self.assertRaisesRegex(InvalidInputError, "Results per page must be an integer between 1 and 100."):
            list_workflow_runs(owner=self.owner_login, repo=self.repo_name, per_page=101)
        
        expected_status_error_msg = f"Invalid status value: 'invalid-status'. Valid statuses are: {[s.value for s in WorkflowRunStatus]}."
        # Need to escape special characters in the expected message for regex
        escaped_expected_msg = expected_status_error_msg.replace('[','\\[').replace(']','\\]').replace("'", "\\'")
        with self.assertRaisesRegex(InvalidInputError, escaped_expected_msg):
            list_workflow_runs(owner=self.owner_login, repo=self.repo_name, status="invalid-status")
        
        # Test created filter format (assuming utils._parse_created_filter handles it and raises InvalidInputError)
        with mock.patch('github_actions.SimulationEngine.utils._parse_created_filter', 
                        side_effect=InvalidInputError("Bad date from util")) as mock_parse:
            with self.assertRaisesRegex(InvalidInputError, "Bad date from util"):
                list_workflow_runs(owner=self.owner_login, repo=self.repo_name, created="bad-date-format")
            mock_parse.assert_called_once_with("bad-date-format")

    def test_not_found_repository(self):
        with self.assertRaisesRegex(NotFoundError, "Repository 'badowner/badrepo' not found."):
            list_workflow_runs(owner="badowner", repo="badrepo")

    def test_not_found_workflow_id(self):
        with self.assertRaisesRegex(NotFoundError, "Workflow with ID/filename '999' not found"):
            list_workflow_runs(owner=self.owner_login, repo=self.repo_name, workflow_id=999)
        with self.assertRaisesRegex(NotFoundError, "Workflow with ID/filename 'nonexistent.yml' not found"):
            list_workflow_runs(owner=self.owner_login, repo=self.repo_name, workflow_id="nonexistent.yml")
            
    def test_empty_runs_for_repo(self):
        empty_owner = "emptyOwner"
        empty_repo_name = "emptyRepo"
        utils.add_repository(owner={'login': empty_owner, 'id': 99, 'type': ActorType.USER.value, 'node_id': 'EU1', 'site_admin': False}, repo_name=empty_repo_name)
        
        result = list_workflow_runs(owner=empty_owner, repo=empty_repo_name)
        self.assertEqual(result['total_count'], 0)
        self.assertEqual(len(result['workflow_runs']), 0)

class TestUtilsParseCreatedFilter(unittest.TestCase):

    def assert_datetime_equal(self, dt1: Optional[datetime], dt2: Optional[datetime], msg: Optional[str] = None):
        """Asserts that two datetimes are equal, ignoring microseconds for simplicity if needed,
           and ensuring they are both UTC for comparison if not None."""
        if dt1 is None and dt2 is None:
            return
        self.assertIsNotNone(dt1, msg)
        self.assertIsNotNone(dt2, msg)
        
        # Ensure both are UTC aware for comparison
        dt1_utc = dt1.astimezone(timezone.utc) if dt1.tzinfo else dt1.replace(tzinfo=timezone.utc)
        dt2_utc = dt2.astimezone(timezone.utc) if dt2.tzinfo else dt2.replace(tzinfo=timezone.utc)

        # Compare year, month, day, hour, minute, second (ignore microsecond for range boundaries)
        self.assertEqual(
            (dt1_utc.year, dt1_utc.month, dt1_utc.day, dt1_utc.hour, dt1_utc.minute, dt1_utc.second),
            (dt2_utc.year, dt2_utc.month, dt2_utc.day, dt2_utc.hour, dt2_utc.minute, dt2_utc.second),
            msg
        )

    def test_parse_created_filter_none_or_empty(self):
        """Test line 272: if not created_filter: return None"""
        self.assertIsNone(_parse_created_filter(None))
        self.assertIsNone(_parse_created_filter(""))

    def test_parse_created_filter_single_date(self):
        result = _parse_created_filter("2023-01-15")
        self.assertIsNotNone(result)
        self.assert_datetime_equal(result.get('start_date'), datetime(2023, 1, 15, 0, 0, 0, tzinfo=timezone.utc))
        self.assert_datetime_equal(result.get('end_date'), datetime(2023, 1, 15, 23, 59, 59, tzinfo=timezone.utc))
        # Check microsecond part of end_date if specifically needed
        self.assertEqual(result.get('end_date').microsecond, 999999)


    def test_parse_created_filter_range(self):
        result = _parse_created_filter("2023-01-10..2023-01-20")
        self.assertIsNotNone(result)
        self.assert_datetime_equal(result.get('start_date'), datetime(2023, 1, 10, 0, 0, 0, tzinfo=timezone.utc))
        self.assert_datetime_equal(result.get('end_date'), datetime(2023, 1, 20, 23, 59, 59, tzinfo=timezone.utc))
        self.assertEqual(result.get('end_date').microsecond, 999999)

    def test_parse_created_filter_greater_equal(self):
        result = _parse_created_filter(">=2023-02-01")
        self.assertIsNotNone(result)
        self.assert_datetime_equal(result.get('start_date'), datetime(2023, 2, 1, 0, 0, 0, tzinfo=timezone.utc))
        self.assertIsNone(result.get('end_date'))

    def test_parse_created_filter_less_equal(self):
        result = _parse_created_filter("<=2023-02-15")
        self.assertIsNotNone(result)
        self.assertIsNone(result.get('start_date'))
        self.assert_datetime_equal(result.get('end_date'), datetime(2023, 2, 15, 23, 59, 59, tzinfo=timezone.utc))
        self.assertEqual(result.get('end_date').microsecond, 999999)

    def test_parse_created_filter_invalid_format_range_incomplete(self):
        """Test line 292-293: except ValueError (for range split)"""
        with self.assertRaisesRegex(InvalidInputError, "Invalid format for 'created' date filter: '2023-01-01..'. Use YYYY-MM-DD or ranges."):
            _parse_created_filter("2023-01-01..")

    def test_parse_created_filter_invalid_format_single_date(self):
        """Test line 292-293: except ValueError (for single date fromisoformat)"""
        with self.assertRaisesRegex(InvalidInputError, "Invalid format for 'created' date filter: 'not-a-date'. Use YYYY-MM-DD or ranges."):
            _parse_created_filter("not-a-date")
        with self.assertRaisesRegex(InvalidInputError, "Invalid format for 'created' date filter: '2023/01/01'. Use YYYY-MM-DD or ranges."):
            _parse_created_filter("2023/01/01")

    def test_parse_created_filter_invalid_format_operator(self):
        """Test line 292-293: except ValueError (for operator date fromisoformat)"""
        with self.assertRaisesRegex(InvalidInputError, "Invalid format for 'created' date filter: '>=notadate'. Use YYYY-MM-DD or ranges."):
            _parse_created_filter(">=notadate")
        with self.assertRaisesRegex(InvalidInputError, "Invalid format for 'created' date filter: '<=2023/02/15'. Use YYYY-MM-DD or ranges."):
            _parse_created_filter("<=2023/02/15")

    def test_parse_created_filter_range_malformed_dates(self):
        """Test line 292-293: except ValueError (for malformed dates within a range)"""
        with self.assertRaisesRegex(InvalidInputError, "Invalid format for 'created' date filter: '2023-01-xx..2023-01-20'. Use YYYY-MM-DD or ranges."):
            _parse_created_filter("2023-01-xx..2023-01-20")
        with self.assertRaisesRegex(InvalidInputError, "Invalid format for 'created' date filter: '2023-01-10..2023-01-yy'. Use YYYY-MM-DD or ranges."):
            _parse_created_filter("2023-01-10..2023-01-yy")
