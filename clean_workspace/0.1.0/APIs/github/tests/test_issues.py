import unittest
from unittest import main
from unittest.mock import patch
import copy
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List


from github.SimulationEngine.db import DB
from github.SimulationEngine.custom_errors import (
    NotFoundError, 
    ForbiddenError, 
    ValidationError,
)
from github.SimulationEngine.models import UserSimple, AddIssueCommentResponse

from github.SimulationEngine import utils as sim_utils
from github.issues import (
    update_issue,
    get_issue_comments,
    create_issue,
    get_issue,
    add_issue_comment,
)

from common_utils.base_case import BaseTestCaseWithErrorHandler
from github import DB as GITHUB_APP_DB

class TestUpdateIssue(BaseTestCaseWithErrorHandler):

    @classmethod
    def setUpClass(cls):
        cls.original_db = copy.deepcopy(DB)

    @classmethod
    def tearDownClass(cls):
        DB.clear()
        DB.update(cls.original_db)

    def setUp(self):
        self.DB = DB
        self.DB.clear()

        # Common entities
        self.current_user_id = 1
        self.current_user_login = "test_updater"
        self.owner_id = 2
        self.owner_login = "repo_owner"
        self.repo_id = 101
        self.repo_name = "my-app"
        self.repo_full_name = f"{self.owner_login}/{self.repo_name}"

        self.other_repo_id = 102
        self.other_repo_name = "other-app"
        self.other_repo_full_name = f"{self.owner_login}/{self.other_repo_name}"


        self.issue_id_counter = 201
        self.issue_number_counter = 1
        self.label_id_counter = 301
        self.milestone_id_counter = 401

        self.DB['CurrentUser'] = {
            'id': self.current_user_id,
            'login': self.current_user_login,
            'name': 'Test Updater',
        }
        self.DB['Users'] = [
            {'id': self.current_user_id, 'login': self.current_user_login, 'node_id': 'user_node_1', 'type': 'User', 'site_admin': False, 'name': 'Test Updater'},
            {'id': self.owner_id, 'login': self.owner_login, 'node_id': 'user_node_2', 'type': 'User', 'site_admin': False, 'name': 'Repo Owner'},
            {'id': 3, 'login': 'assignee1', 'node_id': 'user_node_3', 'type': 'User', 'site_admin': False, 'name': 'Assignee One'},
            {'id': 4, 'login': 'assignee2', 'node_id': 'user_node_4', 'type': 'User', 'site_admin': False, 'name': 'Assignee Two'},
            {'id': 5, 'login': 'reader_user', 'node_id': 'user_node_5', 'type': 'User', 'site_admin': False, 'name': 'Reader User'},
            {'id': 6, 'login': 'potential_assignee', 'node_id': 'user_node_6', 'type': 'User', 'site_admin': False, 'name': 'Potential Assignee'},
        ]

        repo_owner_user_simple = {'id': self.owner_id, 'login': self.owner_login, 'node_id': 'user_node_2', 'type': 'User', 'site_admin': False}

        self.DB['Repositories'] = [
            {
                'id': self.repo_id, 'node_id': 'repo_node_1', 'name': self.repo_name, 'full_name': self.repo_full_name,
                'private': False, 'owner': repo_owner_user_simple, 'description': 'A test repository', 'fork': False,
                'created_at': datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"),
                'updated_at': datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"),
                'pushed_at': datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"),
                'size': 1024, 'stargazers_count': 10, 'watchers_count': 5, 'language': 'Python',
                'has_issues': True, 'has_projects': True, 'has_downloads': True, 'has_wiki': True, 'has_pages': False,
                'forks_count': 0, 'archived': False, 'disabled': False, 'open_issues_count': 1,
                'allow_forking': True, 'is_template': False, 'web_commit_signoff_required': False,
                'topics': ['testing', 'python'], 'visibility': 'public', 'default_branch': 'main'
            },
            {
                'id': self.other_repo_id, 'node_id': 'repo_node_2', 'name': self.other_repo_name, 'full_name': self.other_repo_full_name,
                'private': False, 'owner': repo_owner_user_simple, 'description': 'Another test repository', 'fork': False,
                'created_at': datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"),
                'updated_at': datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"),
                'pushed_at': datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"),
                'size': 512, 'has_issues': True, 'open_issues_count': 0, 'visibility': 'public', 'default_branch': 'main'
            }
        ]
        self.DB['RepositoryCollaborators'] = [
            {'repository_id': self.repo_id, 'user_id': self.current_user_id, 'permission': 'write'},
            {'repository_id': self.repo_id, 'user_id': self.owner_id, 'permission': 'admin'},
            {'repository_id': self.repo_id, 'user_id': 5, 'permission': 'read'},
            {'repository_id': self.repo_id, 'user_id': 6, 'permission': 'read'},
        ]

        self.label1 = self._create_db_label_dict(self.repo_id, "bug", "d73a4a", "Something isn't working")
        self.label2 = self._create_db_label_dict(self.repo_id, "enhancement", "a2eeef", "New feature or request")
        self.label3 = self._create_db_label_dict(self.repo_id, "documentation", "0075ca", "Improvements or additions to documentation")
        self.DB['RepositoryLabels'] = [self.label1, self.label2, self.label3]

        self.milestone1 = self._create_db_milestone_dict(self.repo_id, 1, "v1.0 Release", "Tasks for version 1.0", "open", creator_id=self.owner_id, creator_login=self.owner_login)
        self.milestone2 = self._create_db_milestone_dict(self.repo_id, 2, "v1.1 Sprint", "Tasks for version 1.1", "open", creator_id=self.owner_id, creator_login=self.owner_login)
        self.DB['Milestones'] = [self.milestone1, self.milestone2]

        self.initial_issue_body = "This is the first issue."
        self.initial_issue = self._create_db_issue_dict(
            repo_id=self.repo_id, issue_number=1, title="Initial Issue", body=self.initial_issue_body,
            user_id=self.owner_id, user_login=self.owner_login, state="open",
            labels_data=[self.label1],
            assignees_data=[{'id': 3, 'login': 'assignee1'}],
            milestone_data=copy.deepcopy(self.milestone1)
        )
        self.DB['Issues'] = [self.initial_issue]

        self.DB['Repositories'][0]['open_issues_count'] = 1
        db_m1_init = next(m for m in self.DB['Milestones'] if m['id'] == self.milestone1['id'])
        db_m1_init['open_issues'] = 1
        db_m1_init['closed_issues'] = 0


    def _get_next_id(self, counter_attr):
        current_id = getattr(self, counter_attr)
        setattr(self, counter_attr, current_id + 1)
        return current_id

    def _create_db_base_user_dict(self, user_id, login):
        user = next((u for u in self.DB['Users'] if u['id'] == user_id and u['login'] == login), None)
        if not user: raise ValueError(f"User {login} (id {user_id}) not found in DB for BaseUser creation.")
        return {
            'id': user['id'], 'login': user['login'], 'node_id': user.get('node_id', f'node_u_{user_id}'),
            'type': user.get('type', 'User'), 'site_admin': user.get('site_admin', False)
        }

    def _create_db_label_dict(self, repo_id, name, color, description=None, is_default=False):
        return {
            'id': self._get_next_id('label_id_counter'), 'node_id': f'label_node_{name.replace(" ", "_")}_{repo_id}', 'repository_id': repo_id,
            'name': name, 'color': color, 'description': description, 'default': is_default
        }

    def _create_db_milestone_dict(self, repo_id, number, title, description, state, creator_id=None, creator_login=None):
        creator_dict = None
        if creator_id and creator_login:
            creator_dict = self._create_db_base_user_dict(creator_id, creator_login)
        ts = datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
        return {
            'id': self._get_next_id('milestone_id_counter'), 'node_id': f'milestone_node_{number}_{repo_id}', 'repository_id': repo_id,
            'number': number, 'title': title, 'description': description,
            'creator': creator_dict, 'open_issues': 0, 'closed_issues': 0, 'state': state,
            'created_at': ts, 'updated_at': ts, 'closed_at': None, 'due_on': None
        }

    def _create_db_issue_dict(self, repo_id, issue_number, title, body, user_id, user_login, state,
                               labels_data=None, assignees_data=None, milestone_data=None, locked=False,
                               author_association="CONTRIBUTOR", comments=0):
        user_dict = self._create_db_base_user_dict(user_id, user_login)
        assignee_list = []
        main_assignee = None
        if assignees_data:
            for ad in assignees_data:
                assignee_list.append(self._create_db_base_user_dict(ad['id'], ad['login']))
            if assignee_list: main_assignee = assignee_list[0]

        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        milestone_dict_for_issue = None
        if milestone_data:
            if isinstance(milestone_data, dict) and 'id' in milestone_data:
                 milestone_dict_for_issue = milestone_data

        return {
            'id': self._get_next_id('issue_id_counter'), 'node_id': f'issue_node_{issue_number}_{repo_id}', 'repository_id': repo_id,
            'number': issue_number, 'title': title, 'user': user_dict,
            'labels': labels_data if labels_data else [], 'state': state, 'locked': locked,
            'assignee': main_assignee, 'assignees': assignee_list, 'milestone': milestone_dict_for_issue,
            'comments': comments, 'created_at': ts, 'updated_at': ts,
            'closed_at': ts if state == "closed" else None, 'body': body,
            'author_association': author_association, 'active_lock_reason': None, 'reactions': None
        }

    def _get_issue_from_db(self, repo_id, issue_number):
        for issue in self.DB.get('Issues', []):
            if issue.get('repository_id') == repo_id and issue.get('number') == issue_number:
                return issue
        return None

    def _get_milestone_from_db(self, milestone_id):
        return next((m for m in self.DB.get("Milestones", []) if m["id"] == milestone_id), None)


    def _assert_issue_response_valid(self, response_data, expected_issue_db_state, check_updated_at_changed=True, initial_updated_at=None):
        self.assertIsInstance(response_data, dict)
        self.assertEqual(response_data['id'], expected_issue_db_state['id'])
        self.assertEqual(response_data['number'], expected_issue_db_state['number'])
        self.assertEqual(response_data['title'], expected_issue_db_state['title'])
        self.assertEqual(response_data['body'], expected_issue_db_state['body'])
        self.assertEqual(response_data['state'], expected_issue_db_state['state'])
        self.assertEqual(response_data['locked'], expected_issue_db_state['locked'])
        self.assertEqual(response_data['comments'], expected_issue_db_state['comments'])
        self.assertEqual(response_data['author_association'], expected_issue_db_state['author_association'])

        self.assertEqual(response_data['user']['id'], expected_issue_db_state['user']['id'])
        self.assertEqual(response_data['user']['login'], expected_issue_db_state['user']['login'])

        self.assertEqual(len(response_data['labels']), len(expected_issue_db_state['labels']))
        resp_label_names = sorted([l['name'] for l in response_data['labels']])
        db_label_names = sorted([l['name'] for l in expected_issue_db_state['labels']])
        self.assertEqual(resp_label_names, db_label_names)


        self.assertEqual(len(response_data['assignees']), len(expected_issue_db_state['assignees']))
        resp_assignee_logins = sorted([a['login'] for a in response_data['assignees']])
        db_assignee_logins = sorted([a['login'] for a in expected_issue_db_state['assignees']])
        self.assertEqual(resp_assignee_logins, db_assignee_logins)


        if expected_issue_db_state['assignee']:
            self.assertIsNotNone(response_data['assignee'])
            self.assertEqual(response_data['assignee']['id'], expected_issue_db_state['assignee']['id'])
            self.assertEqual(response_data['assignee']['login'], expected_issue_db_state['assignee']['login'])
        else:
            self.assertIsNone(response_data['assignee'])

        if expected_issue_db_state['milestone']:
            self.assertIsNotNone(response_data['milestone'], "Response milestone should not be None if DB has one")
            self.assertEqual(response_data['milestone']['id'], expected_issue_db_state['milestone']['id'])
            self.assertEqual(response_data['milestone']['number'], expected_issue_db_state['milestone']['number'])
            self.assertEqual(response_data['milestone']['title'], expected_issue_db_state['milestone']['title'])
        else:
            self.assertIsNone(response_data['milestone'], "Response milestone should be None if DB has no milestone")


        self.assertEqual(response_data['created_at'], expected_issue_db_state['created_at'])
        if check_updated_at_changed and initial_updated_at:
            self.assertTrue(datetime.fromisoformat(response_data['updated_at'].replace("Z", "+00:00")) > datetime.fromisoformat(initial_updated_at.replace("Z", "+00:00")))
        self.assertTrue(response_data['updated_at'] >= expected_issue_db_state['created_at'])

        if expected_issue_db_state['state'] == 'closed':
            self.assertIsNotNone(response_data['closed_at'])
            if expected_issue_db_state.get('closed_at'):
                 self.assertEqual(response_data['closed_at'], expected_issue_db_state['closed_at'])
        else:
            self.assertIsNone(response_data['closed_at'])
            self.assertIsNone(expected_issue_db_state.get('closed_at'))


    # --- Success Cases ---
    def test_update_title_success(self):
        new_title = "Updated Issue Title"
        initial_updated_at = self.initial_issue['updated_at']
        response = update_issue(self.owner_login, self.repo_name, 1, title=new_title)
        updated_db_issue = self._get_issue_from_db(self.repo_id, 1)
        self.assertEqual(updated_db_issue['title'], new_title)
        self._assert_issue_response_valid(response, updated_db_issue, initial_updated_at=initial_updated_at)

    def test_update_body_success(self):
        new_body = "This is the updated body content."
        initial_updated_at = self.initial_issue['updated_at']
        response = update_issue(self.owner_login, self.repo_name, 1, body=new_body)
        updated_db_issue = self._get_issue_from_db(self.repo_id, 1)
        self.assertEqual(updated_db_issue['body'], new_body)
        self._assert_issue_response_valid(response, updated_db_issue, initial_updated_at=initial_updated_at)

    def test_update_body_to_empty_string_success(self):
        initial_updated_at = self.initial_issue['updated_at']
        response = update_issue(self.owner_login, self.repo_name, 1, body="")
        updated_db_issue = self._get_issue_from_db(self.repo_id, 1)
        self.assertEqual(updated_db_issue['body'], "")
        self._assert_issue_response_valid(response, updated_db_issue, initial_updated_at=initial_updated_at)

    def test_update_body_to_none_clears_body_success(self):
        initial_updated_at = self.initial_issue['updated_at']
        response = update_issue(self.owner_login, self.repo_name, 1, body=None)
        updated_db_issue = self._get_issue_from_db(self.repo_id, 1)
        self.assertIsNone(updated_db_issue['body'])
        self._assert_issue_response_valid(response, updated_db_issue, initial_updated_at=initial_updated_at)

    def test_update_state_to_closed_success(self):
        initial_repo_open_issues = self.DB['Repositories'][0]['open_issues_count']
        m1_db = self._get_milestone_from_db(self.milestone1['id'])
        initial_milestone_open_issues = m1_db['open_issues']
        initial_milestone_closed_issues = m1_db['closed_issues']
        initial_updated_at = self.initial_issue['updated_at']

        response = update_issue(self.owner_login, self.repo_name, 1, state="closed")

        updated_db_issue = self._get_issue_from_db(self.repo_id, 1)
        self.assertEqual(updated_db_issue['state'], "closed")
        self.assertIsNotNone(updated_db_issue['closed_at'])
        self.assertIsNone(updated_db_issue['milestone']) # Milestone removed by default

        self._assert_issue_response_valid(response, updated_db_issue, initial_updated_at=initial_updated_at)

        self.assertEqual(self.DB['Repositories'][0]['open_issues_count'], initial_repo_open_issues - 1)

        m1_db_after = self._get_milestone_from_db(self.milestone1['id'])
        self.assertEqual(m1_db_after['open_issues'], initial_milestone_open_issues - 1)
        self.assertEqual(m1_db_after['closed_issues'], initial_milestone_closed_issues)


    def test_update_state_to_open_from_closed_success(self):
        m1_at_start = self._get_milestone_from_db(self.milestone1['id'])
        m1_open_at_start = m1_at_start['open_issues']
        m1_closed_at_start = m1_at_start['closed_issues']
        repo_open_at_start = self.DB['Repositories'][0]['open_issues_count']

        update_issue(self.owner_login, self.repo_name, 1, state="closed") # Milestone removed here

        m1_after_close = self._get_milestone_from_db(self.milestone1['id'])
        self.assertEqual(m1_after_close['open_issues'], m1_open_at_start - 1)
        self.assertEqual(m1_after_close['closed_issues'], m1_closed_at_start)
        self.assertEqual(self.DB['Repositories'][0]['open_issues_count'], repo_open_at_start - 1)

        closed_issue = self._get_issue_from_db(self.repo_id, 1)
        self.assertIsNone(closed_issue['milestone'])
        initial_updated_at_after_close = closed_issue['updated_at']

        response = update_issue(self.owner_login, self.repo_name, 1, state="open")

        updated_db_issue = self._get_issue_from_db(self.repo_id, 1)
        self.assertEqual(updated_db_issue['state'], "open")
        self.assertIsNone(updated_db_issue['closed_at'])
        self.assertIsNone(updated_db_issue['milestone']) # Still None

        self._assert_issue_response_valid(response, updated_db_issue, initial_updated_at=initial_updated_at_after_close)

        self.assertEqual(self.DB['Repositories'][0]['open_issues_count'], repo_open_at_start)

        m1_db_reopened = self._get_milestone_from_db(self.milestone1['id'])
        self.assertEqual(m1_db_reopened['open_issues'], m1_after_close['open_issues'])
        self.assertEqual(m1_db_reopened['closed_issues'], m1_after_close['closed_issues'])


    def test_update_labels_replace_success(self):
        new_label_names = ["enhancement", "documentation"]
        initial_updated_at = self.initial_issue['updated_at']
        response = update_issue(self.owner_login, self.repo_name, 1, labels=new_label_names)
        updated_db_issue = self._get_issue_from_db(self.repo_id, 1)
        self.assertEqual(len(updated_db_issue['labels']), 2)
        db_label_names = sorted([l['name'] for l in updated_db_issue['labels']])
        self.assertEqual(db_label_names, sorted(new_label_names))
        self._assert_issue_response_valid(response, updated_db_issue, initial_updated_at=initial_updated_at)

    def test_update_labels_clear_success(self):
        initial_updated_at = self.initial_issue['updated_at']
        response = update_issue(self.owner_login, self.repo_name, 1, labels=[])
        updated_db_issue = self._get_issue_from_db(self.repo_id, 1)
        self.assertEqual(len(updated_db_issue['labels']), 0)
        self._assert_issue_response_valid(response, updated_db_issue, initial_updated_at=initial_updated_at)

    def test_update_labels_no_change_if_none(self):
        initial_labels = copy.deepcopy(self.initial_issue['labels'])
        initial_updated_at = self.initial_issue['updated_at']
        response = update_issue(self.owner_login, self.repo_name, 1, labels=None)
        updated_db_issue = self._get_issue_from_db(self.repo_id, 1)
        self.assertEqual(len(updated_db_issue['labels']), len(initial_labels))
        resp_label_names = sorted([l['name'] for l in updated_db_issue['labels']])
        initial_label_names = sorted([l['name'] for l in initial_labels])
        self.assertEqual(resp_label_names, initial_label_names)
        self._assert_issue_response_valid(response, updated_db_issue, check_updated_at_changed=True, initial_updated_at=initial_updated_at)


    def test_update_assignees_replace_success(self):
        new_assignee_logins = ["assignee2", self.owner_login]
        initial_updated_at = self.initial_issue['updated_at']
        response = update_issue(self.owner_login, self.repo_name, 1, assignees=new_assignee_logins)
        updated_db_issue = self._get_issue_from_db(self.repo_id, 1)
        self.assertEqual(len(updated_db_issue['assignees']), 2)
        db_assignee_logins = sorted([a['login'] for a in updated_db_issue['assignees']])
        self.assertEqual(db_assignee_logins, sorted(new_assignee_logins))
        self.assertIn(updated_db_issue['assignee']['login'], new_assignee_logins)
        self._assert_issue_response_valid(response, updated_db_issue, initial_updated_at=initial_updated_at)

    def test_update_assignees_clear_success(self):
        initial_updated_at = self.initial_issue['updated_at']
        response = update_issue(self.owner_login, self.repo_name, 1, assignees=[])
        updated_db_issue = self._get_issue_from_db(self.repo_id, 1)
        self.assertEqual(len(updated_db_issue['assignees']), 0)
        self.assertIsNone(updated_db_issue['assignee'])
        self._assert_issue_response_valid(response, updated_db_issue, initial_updated_at=initial_updated_at)

    def test_update_assignees_no_change_if_none(self):
        initial_assignees = copy.deepcopy(self.initial_issue['assignees'])
        initial_updated_at = self.initial_issue['updated_at']
        response = update_issue(self.owner_login, self.repo_name, 1, assignees=None)
        updated_db_issue = self._get_issue_from_db(self.repo_id, 1)
        self.assertEqual(len(updated_db_issue['assignees']), len(initial_assignees))
        if initial_assignees:
            self.assertEqual(updated_db_issue['assignees'][0]['login'], initial_assignees[0]['login'])
        self._assert_issue_response_valid(response, updated_db_issue, check_updated_at_changed=True, initial_updated_at=initial_updated_at)


    def test_update_milestone_add_success(self):
        m1_db = self._get_milestone_from_db(self.milestone1['id'])
        m2_db = self._get_milestone_from_db(self.milestone2['id'])
        initial_m1_open_issues = m1_db['open_issues']
        initial_m2_open_issues = m2_db['open_issues']
        initial_updated_at = self.initial_issue['updated_at']

        response = update_issue(self.owner_login, self.repo_name, 1, milestone=self.milestone2['number'])
        updated_db_issue = self._get_issue_from_db(self.repo_id, 1)
        self.assertIsNotNone(updated_db_issue['milestone'])
        self.assertEqual(updated_db_issue['milestone']['id'], self.milestone2['id'])
        self._assert_issue_response_valid(response, updated_db_issue, initial_updated_at=initial_updated_at)

        m1_db_after = self._get_milestone_from_db(self.milestone1['id'])
        m2_db_after = self._get_milestone_from_db(self.milestone2['id'])
        self.assertEqual(m1_db_after['open_issues'], initial_m1_open_issues - 1)
        self.assertEqual(m2_db_after['open_issues'], initial_m2_open_issues + 1)

    def test_update_milestone_remove_with_none(self):
        m1_db = self._get_milestone_from_db(self.milestone1['id'])
        initial_m1_open_issues = m1_db['open_issues']
        initial_updated_at = self.initial_issue['updated_at']

        response = update_issue(self.owner_login, self.repo_name, 1, milestone=None)

        updated_db_issue = self._get_issue_from_db(self.repo_id, 1)
        self.assertIsNone(updated_db_issue['milestone'])
        self._assert_issue_response_valid(response, updated_db_issue, initial_updated_at=initial_updated_at)

        m1_db_after = self._get_milestone_from_db(self.milestone1['id'])
        self.assertEqual(m1_db_after['open_issues'], initial_m1_open_issues - 1)


    def test_update_multiple_fields_success(self):
        new_title = "Completely Revamped Issue"
        new_body = "All new content here."
        new_state = "closed"
        new_labels = ["documentation"]
        new_assignees = [self.owner_login]
        new_milestone_num = self.milestone2['number']
        initial_updated_at = self.initial_issue['updated_at']

        initial_repo_open_issues = self.DB['Repositories'][0]['open_issues_count']
        m1_db = self._get_milestone_from_db(self.milestone1['id'])
        m2_db = self._get_milestone_from_db(self.milestone2['id'])
        initial_m1_open = m1_db['open_issues']
        initial_m1_closed = m1_db['closed_issues']
        initial_m2_open = m2_db['open_issues']
        initial_m2_closed = m2_db['closed_issues']

        response = update_issue(
            self.owner_login, self.repo_name, 1,
            title=new_title, body=new_body, state=new_state,
            labels=new_labels, assignees=new_assignees, milestone=new_milestone_num
        )
        updated_db_issue = self._get_issue_from_db(self.repo_id, 1)
        self.assertEqual(updated_db_issue['title'], new_title)
        self.assertEqual(updated_db_issue['body'], new_body)
        self.assertEqual(updated_db_issue['state'], new_state)
        self.assertEqual(len(updated_db_issue['labels']), 1)
        self.assertEqual(updated_db_issue['labels'][0]['name'], "documentation")
        self.assertEqual(len(updated_db_issue['assignees']), 1)
        self.assertEqual(updated_db_issue['assignees'][0]['login'], self.owner_login)
        self.assertIsNotNone(updated_db_issue['milestone'])
        self.assertEqual(updated_db_issue['milestone']['number'], new_milestone_num)
        self._assert_issue_response_valid(response, updated_db_issue, initial_updated_at=initial_updated_at)

        self.assertEqual(self.DB['Repositories'][0]['open_issues_count'], initial_repo_open_issues - 1)

        m1_db_after = self._get_milestone_from_db(self.milestone1['id'])
        m2_db_after = self._get_milestone_from_db(self.milestone2['id'])

        self.assertEqual(m1_db_after['open_issues'], initial_m1_open - 1)
        self.assertEqual(m1_db_after['closed_issues'], initial_m1_closed)

        self.assertEqual(m2_db_after['open_issues'], initial_m2_open)
        self.assertEqual(m2_db_after['closed_issues'], initial_m2_closed + 1)


    def test_update_with_no_optional_params_changes_title_body_updated_at(self):
        initial_issue_copy = copy.deepcopy(self.initial_issue)
        initial_updated_at = initial_issue_copy['updated_at']

        m1_db_before = self._get_milestone_from_db(self.milestone1['id'])
        initial_m1_open_issues = m1_db_before['open_issues']

        response = update_issue(self.owner_login, self.repo_name, 1)

        updated_db_issue = self._get_issue_from_db(self.repo_id, 1)

        self.assertIsNone(updated_db_issue['title'])
        self.assertIsNone(updated_db_issue['body'])
        self.assertIsNone(updated_db_issue['milestone'])

        self.assertEqual(updated_db_issue['state'], initial_issue_copy['state'])
        self.assertEqual(len(updated_db_issue['labels']), len(initial_issue_copy['labels']))
        if initial_issue_copy['labels']:
             self.assertEqual(updated_db_issue['labels'][0]['name'], initial_issue_copy['labels'][0]['name'])
        self.assertEqual(len(updated_db_issue['assignees']), len(initial_issue_copy['assignees']))
        if initial_issue_copy['assignees']:
            self.assertEqual(updated_db_issue['assignees'][0]['login'], initial_issue_copy['assignees'][0]['login'])

        self._assert_issue_response_valid(response, updated_db_issue, check_updated_at_changed=True, initial_updated_at=initial_updated_at)

        m1_db_after = self._get_milestone_from_db(self.milestone1['id'])
        self.assertEqual(m1_db_after['open_issues'], initial_m1_open_issues - 1)


    def test_update_owner_repo_case_insensitive(self):
        new_title = "Case Insensitive Update"
        initial_updated_at = self.initial_issue['updated_at']
        response = update_issue(self.owner_login.upper(), self.repo_name.capitalize(), 1, title=new_title)
        updated_db_issue = self._get_issue_from_db(self.repo_id, 1)
        self.assertEqual(updated_db_issue['title'], new_title)
        self._assert_issue_response_valid(response, updated_db_issue, initial_updated_at=initial_updated_at)

    # --- New tests for 100% coverage ---
    def test_update_by_repo_owner_as_current_user(self):
        original_current_user = copy.deepcopy(self.DB['CurrentUser'])
        self.DB['CurrentUser'] = {'id': self.owner_id, 'login': self.owner_login, 'name': 'Repo Owner'}

        new_title = "Owner Update"
        initial_updated_at = self.initial_issue['updated_at']

        try:
            response = update_issue(self.owner_login, self.repo_name, 1, title=new_title)
            updated_db_issue = self._get_issue_from_db(self.repo_id, 1)
            self.assertEqual(updated_db_issue['title'], new_title)
            self._assert_issue_response_valid(response, updated_db_issue, initial_updated_at=initial_updated_at)
        finally:
            self.DB['CurrentUser'] = original_current_user

    @patch('github.issues.utils._prepare_user_sub_document')
    def test_update_assignee_preparation_failure(self, mock_prepare_user):
        mock_prepare_user.return_value = None
        assignee_login_to_fail = "potential_assignee"

        self.assertTrue(any(u['login'] == assignee_login_to_fail for u in self.DB['Users']))

        self.assert_error_behavior(func_to_call=update_issue, expected_exception_type=ValidationError, expected_message=f"Could not prepare assignee data for '{assignee_login_to_fail}'.", owner=self.owner_login, repo=self.repo_name, issue_number=1, assignees=[assignee_login_to_fail])
        mock_prepare_user.assert_called_once_with(self.DB, assignee_login_to_fail, model_type="BaseUser")


    def test_update_milestone_change_from_closed_issue_on_old_milestone(self):
        issue_num_closed_on_m1 = 2
        closed_issue = self._create_db_issue_dict(
            repo_id=self.repo_id, issue_number=issue_num_closed_on_m1, title="Closed on M1", body="Test body",
            user_id=self.owner_id, user_login=self.owner_login, state="closed",
            milestone_data=copy.deepcopy(self.milestone1)
        )
        self.DB['Issues'].append(closed_issue)

        m1_db = self._get_milestone_from_db(self.milestone1['id'])
        m1_db['closed_issues'] += 1
        initial_m1_closed_issues = m1_db['closed_issues']
        initial_m1_open_issues = m1_db['open_issues']

        m2_db = self._get_milestone_from_db(self.milestone2['id'])
        initial_m2_closed_issues = m2_db['closed_issues']
        initial_updated_at = closed_issue['updated_at']

        response = update_issue(self.owner_login, self.repo_name, issue_num_closed_on_m1, milestone=self.milestone2['number'])

        updated_db_issue = self._get_issue_from_db(self.repo_id, issue_num_closed_on_m1)
        self.assertEqual(updated_db_issue['state'], "closed")
        self.assertIsNotNone(updated_db_issue['milestone'])
        self.assertEqual(updated_db_issue['milestone']['id'], self.milestone2['id'])
        self._assert_issue_response_valid(response, updated_db_issue, initial_updated_at=initial_updated_at)

        m1_db_after = self._get_milestone_from_db(self.milestone1['id'])
        m2_db_after = self._get_milestone_from_db(self.milestone2['id'])

        self.assertEqual(m1_db_after['closed_issues'], initial_m1_closed_issues - 1)
        self.assertEqual(m2_db_after['closed_issues'], initial_m2_closed_issues + 1)
        self.assertEqual(m1_db_after['open_issues'], initial_m1_open_issues)
        self.assertEqual(m2_db_after['open_issues'], m2_db['open_issues'])


    def test_update_with_no_actual_changes_updates_timestamp(self):
        issue_num_no_change = 3
        no_change_issue_details = {
            'repo_id': self.repo_id, 'issue_number': issue_num_no_change, 'title': "NoChangeTitle",
            'body': "NoChangeBody", 'user_id': self.owner_id, 'user_login': self.owner_login,
            'state': "open", 'labels_data': [], 'assignees_data': [], 'milestone_data': None
        }
        no_change_issue = self._create_db_issue_dict(**no_change_issue_details)
        self.DB['Issues'].append(no_change_issue)
        self.DB['Repositories'][0]['open_issues_count'] += 1
        initial_updated_at = no_change_issue['updated_at']

        response = update_issue(
            self.owner_login, self.repo_name, issue_num_no_change,
            title=no_change_issue_details['title'],
            body=no_change_issue_details['body'],
            state=no_change_issue_details['state'],
            labels=[],
            assignees=[],
            milestone=None
        )

        updated_db_issue = self._get_issue_from_db(self.repo_id, issue_num_no_change)

        self.assertTrue(datetime.fromisoformat(response['updated_at'].replace("Z", "+00:00")) > datetime.fromisoformat(initial_updated_at.replace("Z", "+00:00")))
        self.assertTrue(datetime.fromisoformat(updated_db_issue['updated_at'].replace("Z", "+00:00")) > datetime.fromisoformat(initial_updated_at.replace("Z", "+00:00")))

        self.assertEqual(updated_db_issue['title'], no_change_issue_details['title'])
        self.assertEqual(updated_db_issue['body'], no_change_issue_details['body'])
        self.assertEqual(updated_db_issue['state'], no_change_issue_details['state'])
        self.assertEqual(len(updated_db_issue['labels']), 0)
        self.assertEqual(len(updated_db_issue['assignees']), 0)
        self.assertIsNone(updated_db_issue['assignee'])
        self.assertIsNone(updated_db_issue['milestone'])

        self._assert_issue_response_valid(response, updated_db_issue, check_updated_at_changed=False)

    @patch('github.issues.utils._update_raw_item_in_table')
    def test_update_fallback_if_db_update_fails_with_changes(self, mock_update_raw_item):
        mock_update_raw_item.return_value = None

        new_title = "A Title That Changes"

        response = update_issue(self.owner_login, self.repo_name, 1, title=new_title)

        self.assertEqual(response['title'], self.initial_issue['title'])
        self.assertEqual(response['id'], self.initial_issue['id'])

        mock_update_raw_item.assert_called_once()
        args, kwargs = mock_update_raw_item.call_args
        self.assertEqual(args[1], "Issues")
        self.assertEqual(args[2], self.initial_issue['id'])
        self.assertIn('title', args[3])
        self.assertEqual(args[3]['title'], new_title)
        self.assertIn('updated_at', args[3])


    @patch('github.issues.utils._update_raw_item_in_table')
    def test_update_fallback_if_db_update_fails_no_changes(self, mock_update_raw_item):
        mock_update_raw_item.return_value = None

        response = update_issue(
            self.owner_login, self.repo_name, 1,
            title=self.initial_issue['title'],
            body=self.initial_issue['body'],
            state=self.initial_issue['state'],
            labels=[l['name'] for l in self.initial_issue['labels']],
            assignees=[a['login'] for a in self.initial_issue['assignees']],
            milestone=self.initial_issue['milestone']['number'] if self.initial_issue['milestone'] else None
        )

        self.assertEqual(response['title'], self.initial_issue['title'])
        self.assertEqual(response['id'], self.initial_issue['id'])

        mock_update_raw_item.assert_called_once()
        args, kwargs = mock_update_raw_item.call_args
        self.assertEqual(args[1], "Issues")
        self.assertEqual(args[2], self.initial_issue['id'])
        self.assertIn('updated_at', args[3])
        self.assertEqual(len(args[3]), 1)


    def test_update_state_change_on_existing_milestone_open_to_closed(self):
        self.assertIsNotNone(self.initial_issue['milestone'])
        self.assertEqual(self.initial_issue['state'], 'open')

        m1_db = self._get_milestone_from_db(self.milestone1['id'])
        initial_m1_open_issues = m1_db['open_issues']
        initial_m1_closed_issues = m1_db['closed_issues']
        initial_repo_open_issues = self.DB['Repositories'][0]['open_issues_count']

        initial_updated_at = self.initial_issue['updated_at']

        response = update_issue(
            self.owner_login, self.repo_name, 1,
            state="closed",
            milestone=self.initial_issue['milestone']['number']
        )

        updated_db_issue = self._get_issue_from_db(self.repo_id, 1)
        self.assertEqual(updated_db_issue['state'], "closed")
        self.assertIsNotNone(updated_db_issue['milestone'])
        self.assertEqual(updated_db_issue['milestone']['id'], self.milestone1['id'])
        self._assert_issue_response_valid(response, updated_db_issue, initial_updated_at=initial_updated_at)

        self.assertEqual(self.DB['Repositories'][0]['open_issues_count'], initial_repo_open_issues - 1)

        m1_db_after = self._get_milestone_from_db(self.milestone1['id'])
        self.assertEqual(m1_db_after['open_issues'], initial_m1_open_issues - 1)
        self.assertEqual(m1_db_after['closed_issues'], initial_m1_closed_issues + 1)


    def test_update_state_change_on_existing_milestone_closed_to_open(self):
        issue_num_closed_on_m1 = 2
        m1_db_before_new_issue = self._get_milestone_from_db(self.milestone1['id'])
        m1_db_before_new_issue['open_issues'] = 1
        m1_db_before_new_issue['closed_issues'] = 0
        self.DB['Repositories'][0]['open_issues_count'] = 1

        closed_issue_on_m1 = self._create_db_issue_dict(
            repo_id=self.repo_id, issue_number=issue_num_closed_on_m1, title="Test Closed on M1", body="...",
            user_id=self.owner_id, user_login=self.owner_login, state="closed",
            milestone_data=copy.deepcopy(self.milestone1)
        )
        self.DB['Issues'].append(closed_issue_on_m1)

        m1_db = self._get_milestone_from_db(self.milestone1['id'])
        m1_db['closed_issues'] += 1

        initial_m1_open_issues = m1_db['open_issues']
        initial_m1_closed_issues = m1_db['closed_issues']
        initial_repo_open_issues = self.DB['Repositories'][0]['open_issues_count']
        initial_updated_at = closed_issue_on_m1['updated_at']

        response = update_issue(
            self.owner_login, self.repo_name, issue_num_closed_on_m1,
            state="open",
            milestone=closed_issue_on_m1['milestone']['number']
        )

        updated_db_issue = self._get_issue_from_db(self.repo_id, issue_num_closed_on_m1)
        self.assertEqual(updated_db_issue['state'], "open")
        self.assertIsNotNone(updated_db_issue['milestone'])
        self.assertEqual(updated_db_issue['milestone']['id'], self.milestone1['id'])
        self._assert_issue_response_valid(response, updated_db_issue, initial_updated_at=initial_updated_at)

        self.assertEqual(self.DB['Repositories'][0]['open_issues_count'], initial_repo_open_issues + 1)

        m1_db_after = self._get_milestone_from_db(self.milestone1['id'])
        self.assertEqual(m1_db_after['open_issues'], initial_m1_open_issues + 1)
        self.assertEqual(m1_db_after['closed_issues'], initial_m1_closed_issues - 1)

    # --- Error Cases: NotFoundError ---
    def test_update_repo_not_found(self):
        self.assert_error_behavior(func_to_call=update_issue, expected_exception_type=NotFoundError, expected_message="Repository 'repo_owner/nonexistent-repo' not found.", owner=self.owner_login, repo="nonexistent-repo", issue_number=1, title="test")

    def test_update_owner_not_found(self):
        self.assert_error_behavior(func_to_call=update_issue, expected_exception_type=NotFoundError, expected_message="Repository 'nonexistent-owner/my-app' not found.", owner="nonexistent-owner", repo=self.repo_name, issue_number=1, title="test")

    def test_update_issue_not_found(self):
        self.assert_error_behavior(func_to_call=update_issue, expected_exception_type=NotFoundError, expected_message="Issue #999 not found in 'repo_owner/my-app'.", owner=self.owner_login, repo=self.repo_name, issue_number=999, title="test")

    # --- Error Cases: ValidationError ---
    def test_update_invalid_state_value(self):
        self.assert_error_behavior(func_to_call=update_issue, expected_exception_type=ValidationError, expected_message="State must be 'open' or 'closed'.", owner=self.owner_login, repo=self.repo_name, issue_number=1, state="invalid_state_value")

    def test_update_invalid_owner_type(self):
        self.assert_error_behavior(func_to_call=update_issue, expected_exception_type=ValidationError, expected_message="Repository owner must be a string.", owner=123, repo=self.repo_name, issue_number=1, title="test")

    def test_update_invalid_repo_type(self):
        self.assert_error_behavior(func_to_call=update_issue, expected_exception_type=ValidationError, expected_message="Repository name must be a string.", owner=self.owner_login, repo=123, issue_number=1, title="test")

    def test_update_invalid_issue_number_type(self):
        self.assert_error_behavior(func_to_call=update_issue, expected_exception_type=ValidationError, expected_message="Issue number must be an integer.", owner=self.owner_login, repo=self.repo_name, issue_number="abc", title="test")

    def test_update_invalid_issue_number_zero(self):
        self.assert_error_behavior(func_to_call=update_issue, expected_exception_type=ValidationError, expected_message="Issue number must be positive.", owner=self.owner_login, repo=self.repo_name, issue_number=0, title="test")

    def test_update_invalid_labels_type(self):
        self.assert_error_behavior(func_to_call=update_issue, expected_exception_type=ValidationError, expected_message="Labels must be a list of strings.", owner=self.owner_login, repo=self.repo_name, issue_number=1, labels="not-a-list")

    def test_update_invalid_labels_content_type(self):
        self.assert_error_behavior(func_to_call=update_issue, expected_exception_type=ValidationError, expected_message="Label names must be strings.", owner=self.owner_login, repo=self.repo_name, issue_number=1, labels=[123])

    def test_update_label_name_not_found_in_repo(self):
        self.assert_error_behavior(func_to_call=update_issue, expected_exception_type=ValidationError, expected_message="Label 'non-existent-label' not found in repository.", owner=self.owner_login, repo=self.repo_name, issue_number=1, labels=["non-existent-label"])

    def test_update_invalid_assignees_type(self):
        self.assert_error_behavior(func_to_call=update_issue, expected_exception_type=ValidationError, expected_message="Assignees must be a list of strings.", owner=self.owner_login, repo=self.repo_name, issue_number=1, assignees="not-a-list")

    def test_update_invalid_assignees_content_type(self):
        self.assert_error_behavior(func_to_call=update_issue, expected_exception_type=ValidationError, expected_message="Assignee logins must be strings.", owner=self.owner_login, repo=self.repo_name, issue_number=1, assignees=[123])

    def test_update_assignee_login_not_found(self):
        self.assert_error_behavior(func_to_call=update_issue, expected_exception_type=ValidationError, expected_message="Assignee login 'non-existent-user-login' not found.", owner=self.owner_login, repo=self.repo_name, issue_number=1, assignees=["non-existent-user-login"])

    def test_update_invalid_milestone_type(self):
        self.assert_error_behavior(func_to_call=update_issue, expected_exception_type=ValidationError, expected_message="Milestone number must be an integer.", owner=self.owner_login, repo=self.repo_name, issue_number=1, milestone="not-an-int")


    def test_update_milestone_number_not_found_in_repo(self):
        self.assert_error_behavior(func_to_call=update_issue, expected_exception_type=ValidationError, expected_message="Milestone number 999 not found in repository.", owner=self.owner_login, repo=self.repo_name, issue_number=1, milestone=999)

    # --- Error Cases: ForbiddenError ---
    def test_update_forbidden_no_write_access_for_title(self):
        original_current_user = self.DB['CurrentUser']
        self.DB['CurrentUser'] = {'id': 5, 'login': 'reader_user', 'name': 'Reader User'}
        try:
            # Only attempt to update title; other fields that reader_user might modify by default (None)
            # should be set to their current values to isolate the title permission.
            self.assert_error_behavior(func_to_call=update_issue, expected_exception_type=ForbiddenError, expected_message="User does not have permission to update issue title.", owner=self.owner_login, repo=self.repo_name, issue_number=1, title="Forbidden Update", # This is the change being attempted
                body=self.initial_issue['body'], # Keep current
                state=self.initial_issue['state'], # Keep current
                labels=[l['name'] for l in self.initial_issue.get('labels', [])], # Keep current
                assignees=[a['login'] for a in self.initial_issue.get('assignees', [])], # Keep current
                milestone=self.initial_issue['milestone']['number'] if self.initial_issue.get('milestone') else None # Keep current
            )
        finally:
            self.DB['CurrentUser'] = original_current_user


    def test_update_forbidden_no_push_access_for_labels(self):
        original_current_user = self.DB['CurrentUser']
        self.DB['CurrentUser'] = {'id': 5, 'login': 'reader_user', 'name': 'Reader User'}
        try:
            self.assert_error_behavior(
                func_to_call=update_issue,
                expected_exception_type=ForbiddenError,
                expected_message="User does not have permission to update issue labels.",
                owner=self.owner_login, repo=self.repo_name, issue_number=1, labels=["bug"], # This is the change being attempted
                title=self.initial_issue['title'], # Keep current to avoid other permission errors
                body=self.initial_issue['body'] # Keep current
            )
        finally:
            self.DB['CurrentUser'] = original_current_user

    def test_update_forbidden_no_push_access_for_assignees(self):
        original_current_user = self.DB['CurrentUser']
        self.DB['CurrentUser'] = {'id': 5, 'login': 'reader_user', 'name': 'Reader User'}
        try:
            self.assert_error_behavior(
                func_to_call=update_issue,
                expected_exception_type=ForbiddenError,
                expected_message="User does not have permission to update issue assignees.",
                owner=self.owner_login, repo=self.repo_name, issue_number=1, assignees=["assignee1"], # This is the change being attempted
                title=self.initial_issue['title'], # Keep current
                body=self.initial_issue['body']   # Keep current
            )
        finally:
            self.DB['CurrentUser'] = original_current_user

    def test_update_forbidden_no_push_access_for_milestone_setting(self):
        original_current_user = self.DB['CurrentUser']
        self.DB['CurrentUser'] = {'id': 5, 'login': 'reader_user', 'name': 'Reader User'}
        try:
            self.assert_error_behavior(
                func_to_call=update_issue,
                expected_exception_type=ForbiddenError,
                expected_message="User does not have permission to update issue milestone.",
                owner=self.owner_login, repo=self.repo_name, issue_number=1, milestone=self.milestone1['number'], # This is the change being attempted
                title=self.initial_issue['title'], # Keep current
                body=self.initial_issue['body']   # Keep current
            )
        finally:
            self.DB['CurrentUser'] = original_current_user

    def test_update_forbidden_no_push_access_for_milestone_removal(self):
        self.assertIsNotNone(self.initial_issue['milestone'])

        original_current_user = self.DB['CurrentUser']
        self.DB['CurrentUser'] = {'id': 5, 'login': 'reader_user', 'name': 'Reader User'}
        try:
            self.assert_error_behavior(
                func_to_call=update_issue,
                expected_exception_type=ForbiddenError,
                expected_message="User does not have permission to update issue milestone.",
                owner=self.owner_login, repo=self.repo_name, issue_number=1, milestone=None, # This is the change being attempted
                title=self.initial_issue['title'], # Keep current
                body=self.initial_issue['body']   # Keep current
            )
        finally:
            self.DB['CurrentUser'] = original_current_user

        db_issue_after = self._get_issue_from_db(self.repo_id, 1)
        self.assertIsNotNone(db_issue_after['milestone'])
        self.assertEqual(db_issue_after['milestone']['id'], self.milestone1['id'])

class TestGetIssueComments(BaseTestCaseWithErrorHandler):

    def setUp(self):
        # Store original DB state
        self.original_db = DB.copy()
        
        self.DB = DB  # Use the global DB instance
        self.DB.clear()

        # Initialize standard tables
        self.DB['Users'] = []
        self.DB['Repositories'] = []
        self.DB['Issues'] = []
        self.DB['IssueComments'] = []

        self.owner_login = "testowner"
        self.repo_name = "testrepo"
        self.issue_number = 1

        # Add default entities to DB via helper methods
        self.default_user_owner = self._add_user_to_db(user_id=1, login=self.owner_login)
        self.default_repo = self._add_repo_to_db(repo_id=101, name=self.repo_name, owner_user_data=self.default_user_owner)
        self.default_issue = self._add_issue_to_db(issue_id=1001, repo_id=self.default_repo['id'], number=self.issue_number, user_data=self.default_user_owner)

    def tearDown(self):
        # Restore original DB state
        self.DB.clear()
        self.DB.update(self.original_db)

    def _add_user_to_db(self, user_id: int, login: str, **kwargs) -> dict:
        user_data = {
            'id': user_id, 
            'login': login, 
            'node_id': f'U_{user_id}', 
            'type': 'User', 
            'site_admin': False, 
            **kwargs
        }
        self.DB['Users'].append(user_data)
        return user_data

    def _add_repo_to_db(self, repo_id: int, name: str, owner_user_data: dict, **kwargs) -> dict:
        repo_data = {
            'id': repo_id, 
            'name': name, 
            'full_name': f"{owner_user_data['login']}/{name}",
            'owner': {'id': owner_user_data['id'], 'login': owner_user_data['login']},
            'private': False, 
            'fork': False,
            'created_at': datetime(2023, 1, 1, 0, 0, 0), 
            'updated_at': datetime(2023, 1, 1, 0, 0, 0), 
            'pushed_at': datetime(2023, 1, 1, 0, 0, 0),
            'size': 100, 
            'has_issues': True, # Default to issues being enabled
            **kwargs
        }
        self.DB['Repositories'].append(repo_data)
        return repo_data

    def _add_issue_to_db(self, issue_id: int, repo_id: int, number: int, user_data: dict, **kwargs) -> dict:
        issue_data = {
            'id': issue_id, 
            'repository_id': repo_id, 
            'number': number, 
            'title': f'Test Issue {number}',
            'user': {'id': user_data['id'], 'login': user_data['login']}, 
            'state': 'open', 
            'locked': False, 
            'comments': 0, 
            'created_at': datetime(2023, 1, 10, 10, 0, 0),
            'updated_at': datetime(2023, 1, 10, 10, 0, 0),
            'author_association': 'OWNER', 
            'body': 'Default issue body content.',
            **kwargs
        }
        self.DB['Issues'].append(issue_data)
        return issue_data

    def _add_comment_to_db(self, comment_id: int, issue_id: int, repo_id: int, user_data: dict, body: str, **kwargs) -> dict:


        comment_data = {
            'id': comment_id, 
            'node_id': f'IC_{comment_id}',
            'issue_id': issue_id, 
            'repository_id': repo_id, 
            'user': {'id': user_data['id'], 'login': user_data['login']}, 
            'created_at': datetime(2023, 1, 10, 11, 0, 0),
            'updated_at': datetime(2023, 1, 10, 11, 0, 0),
            'author_association': 'CONTRIBUTOR', 
            'body': body,
            **kwargs
        }
        self.DB['IssueComments'].append(comment_data)
        return comment_data

    def test_get_comments_success_multiple_comments(self):
        commenter1 = self._add_user_to_db(user_id=201, login="commenter1")
        commenter2 = self._add_user_to_db(user_id=202, login="commenter2")

        comment1_data = self._add_comment_to_db(
            comment_id=3001, issue_id=self.default_issue['id'], repo_id=self.default_repo['id'], 
            user_data=commenter1, body="First comment on the issue."
        )
        comment2_data = self._add_comment_to_db(
            comment_id=3002, issue_id=self.default_issue['id'], repo_id=self.default_repo['id'], 
            user_data=commenter2, body="Second comment on the issue.", 
            created_at=datetime(2023, 1, 10, 12, 0, 0), 
            updated_at=datetime(2023, 1, 10, 12, 0, 0)
        )

        other_user = self._add_user_to_db(user_id=3, login="otherowner")
        other_repo = self._add_repo_to_db(repo_id=102, name="otherrepo", owner_user_data=other_user)
        other_issue = self._add_issue_to_db(issue_id=1002, repo_id=other_repo['id'], number=2, user_data=other_user)
        self._add_comment_to_db(
            comment_id=3003, issue_id=other_issue['id'], repo_id=other_repo['id'], 
            user_data=commenter1, body="Comment on a different issue."
        )

        comments = get_issue_comments(self.owner_login, self.repo_name, self.issue_number)

        self.assertIsInstance(comments, list)
        self.assertEqual(len(comments), 2)

        # Assuming order by created_at
        retrieved_comment1 = comments[0]
        self.assertEqual(retrieved_comment1['id'], comment1_data['id'])
        self.assertEqual(retrieved_comment1['node_id'], comment1_data['node_id'])
        self.assertEqual(retrieved_comment1['user']['login'], commenter1['login'])
        self.assertEqual(retrieved_comment1['user']['id'], commenter1['id'])
        
        # Convert datetime to string format for comparison
        self.assertEqual(retrieved_comment1['created_at'], sim_utils._format_datetime(comment1_data['created_at']))
        self.assertEqual(retrieved_comment1['updated_at'], sim_utils._format_datetime(comment1_data['updated_at']))
        
        self.assertEqual(retrieved_comment1['author_association'], comment1_data['author_association'])
        self.assertEqual(retrieved_comment1['body'], comment1_data['body'])

        retrieved_comment2 = comments[1]
        self.assertEqual(retrieved_comment2['id'], comment2_data['id'])
        self.assertEqual(retrieved_comment2['body'], comment2_data['body'])

    def test_get_comments_no_comments_for_issue(self):
        comments = get_issue_comments(self.owner_login, self.repo_name, self.issue_number)
        self.assertEqual(len(comments), 0)
        self.assertIsInstance(comments, list)

    def test_get_comments_issue_exists_comment_table_empty(self):
        self.DB['IssueComments'] = [] # Explicitly ensure table is empty
        comments = get_issue_comments(self.owner_login, self.repo_name, self.issue_number)
        self.assertEqual(len(comments), 0)

    def test_repository_not_found_wrong_owner(self):
        self.assert_error_behavior(func_to_call=get_issue_comments, expected_exception_type=NotFoundError, expected_message="Repository 'nonexistentowner/testrepo' not found.", owner="nonexistentowner", repo=self.repo_name, issue_number=self.issue_number)

    def test_repository_not_found_wrong_repo_name(self):
        self.assert_error_behavior(func_to_call=get_issue_comments, expected_exception_type=NotFoundError, expected_message="Repository 'testowner/nonexistentrepo' not found.", owner=self.owner_login, repo="nonexistentrepo", issue_number=self.issue_number)

    def test_repository_not_found_no_repos_in_db(self):
        self.DB['Repositories'] = []
        self.DB['Issues'] = [] 
        self.DB['IssueComments'] = []
        self.assert_error_behavior(func_to_call=get_issue_comments, expected_exception_type=NotFoundError, expected_message="Repository 'testowner/testrepo' not found.", owner=self.owner_login, repo=self.repo_name, issue_number=self.issue_number)

    def test_issue_not_found_in_repository(self):
        self.assert_error_behavior(
            func_to_call=get_issue_comments,
            expected_exception_type=NotFoundError,
            expected_message="Issue #999 not found in repository 'testowner/testrepo'.",
            owner=self.owner_login, repo=self.repo_name, issue_number=999 # Non-existent
        )

    def test_issue_not_found_no_issues_in_db_for_repo(self):
        self.DB['Issues'] = [i for i in self.DB['Issues'] if i['repository_id'] != self.default_repo['id']]
        self.DB['IssueComments'] = []
        self.assert_error_behavior(
            func_to_call=get_issue_comments,
            expected_exception_type=NotFoundError,
            expected_message="Issue #1 not found in repository 'testowner/testrepo'.",
            owner=self.owner_login, repo=self.repo_name, issue_number=self.issue_number
        )

    def test_repository_has_issues_disabled(self):
        # Find and modify the default repo in the DB list
        for i, repo_item in enumerate(self.DB['Repositories']):
            if repo_item['id'] == self.default_repo['id']:
                self.DB['Repositories'][i] = {**repo_item, 'has_issues': False}
                break

        self.assert_error_behavior(func_to_call=get_issue_comments, expected_exception_type=NotFoundError, expected_message="Issues are disabled for repository 'testowner/testrepo'.", owner=self.owner_login, repo=self.repo_name, issue_number=self.issue_number)

    def test_invalid_owner_type(self):
        self.assert_error_behavior(func_to_call=get_issue_comments, expected_exception_type=ValidationError, expected_message="Owner must be a non-empty string.", owner=123, repo=self.repo_name, issue_number=self.issue_number)

    def test_invalid_repo_type(self):
        self.assert_error_behavior(func_to_call=get_issue_comments, expected_exception_type=ValidationError, expected_message="Repo must be a non-empty string.", owner=self.owner_login, repo=123, issue_number=self.issue_number)

    def test_invalid_issue_number_type(self):
        self.assert_error_behavior(func_to_call=get_issue_comments, expected_exception_type=ValidationError, expected_message="Issue number must be a positive integer.", owner=self.owner_login, repo=self.repo_name, issue_number="abc")

    def test_empty_owner_string_leads_to_error(self):
        self.assert_error_behavior(func_to_call=get_issue_comments, expected_exception_type=ValidationError, expected_message="Owner must be a non-empty string.", owner="", repo=self.repo_name, issue_number=self.issue_number)

    def test_empty_repo_string_leads_to_error(self):
        self.assert_error_behavior(func_to_call=get_issue_comments, expected_exception_type=ValidationError, expected_message="Repo must be a non-empty string.", owner=self.owner_login, repo="", issue_number=self.issue_number)

    def test_comments_returned_in_correct_order_by_created_at(self):
        self.DB['IssueComments'] = [] 
        commenter = self._add_user_to_db(user_id=205, login="order_commenter")

        # Add comments with explicit timestamps to test ordering
        c2_data = self._add_comment_to_db(
            comment_id=3020, 
            issue_id=self.default_issue['id'], 
            repo_id=self.default_repo['id'], 
            user_data=commenter, 
            body="Middle comment", 
            created_at=datetime(2023, 1, 15, 12, 0, 0), 
            updated_at=datetime(2023, 1, 15, 12, 0, 0)
        )
        c1_data = self._add_comment_to_db(
            comment_id=3015, 
            issue_id=self.default_issue['id'], 
            repo_id=self.default_repo['id'], 
            user_data=commenter, 
            body="Earliest comment", 
            created_at=datetime(2023, 1, 15, 10, 0, 0), 
            updated_at=datetime(2023, 1, 15, 10, 0, 0)
        )
        c3_data = self._add_comment_to_db(
            comment_id=3010, 
            issue_id=self.default_issue['id'], 
            repo_id=self.default_repo['id'], 
            user_data=commenter, 
            body="Latest comment",
            created_at=datetime(2023, 1, 15, 14, 0, 0), 
            updated_at=datetime(2023, 1, 15, 14, 0, 0)
        )

        comments = get_issue_comments(self.owner_login, self.repo_name, self.issue_number)
        self.assertEqual(len(comments), 3)

        # Verify comments are ordered by created_at, not by ID
        self.assertEqual(comments[0]['id'], c1_data['id'])
        self.assertEqual(comments[1]['id'], c2_data['id'])
        self.assertEqual(comments[2]['id'], c3_data['id'])

        first_comment_retrieved = comments[0]
        expected_keys = ['id', 'node_id', 'user', 'created_at', 'updated_at', 'author_association', 'body']
        for key in expected_keys:
            self.assertIn(key, first_comment_retrieved)

        self.assertIsInstance(first_comment_retrieved['user'], dict)
        self.assertIn('login', first_comment_retrieved['user'])
        self.assertIn('id', first_comment_retrieved['user'])

    def test_format_datetime_with_timezone(self):
        """Test _format_datetime function with timezone-aware datetime."""
        # Create a timezone-aware datetime
        aware_dt = datetime(2023, 5, 15, 10, 30, 45, tzinfo=timezone.utc)
        
        # Test with UTC timezone
        formatted_str = sim_utils._format_datetime(aware_dt)
        self.assertEqual(formatted_str, "2023-05-15T10:30:45Z")
        
        # Test with a non-UTC timezone (UTC+2)
        from datetime import timedelta
        tz_plus_2 = timezone(timedelta(hours=2))
        aware_dt_plus_2 = datetime(2023, 5, 15, 12, 30, 45, tzinfo=tz_plus_2)
        
        # This should be converted to UTC (10:30:45Z)
        formatted_str_plus_2 = sim_utils._format_datetime(aware_dt_plus_2)
        self.assertEqual(formatted_str_plus_2, "2023-05-15T10:30:45Z")


# --- INITIAL_DB_STATE ---
# Data is exactly as it's expected to be returned by the function when found.
# Datetimes are ISO strings with 'Z'. Reaction keys are aliased (e.g., "+1").
# Node IDs are Base64-like.
INITIAL_DB_STATE = {
    "Users": [
        {"login": "octocat", "id": 1, "node_id": "MDQ6VXNlcjE=", "type": "User", "site_admin": False},
        {"login": "devjane", "id": 25, "node_id": "MDQ6VXNlcjI1", "type": "User", "site_admin": False},
    ],
    "Repositories": [
        {"id": 1296269, "node_id": "MDEwOlJlcG9zaXRvcnkxMjk2MjY5", "name": "Hello-World",
         "full_name": "octocat/Hello-World", "owner": {"login": "octocat", "id": 1}, "has_issues": True},
        {"id": 2100015, "node_id": "MDEwOlJlcG9zaXRvcnkyMTAwMDE1", "name": "ai-project-alpha",
         "full_name": "devjane/ai-project-alpha", "owner": {"login": "devjane", "id": 25}, "has_issues": True},
    ],
    "Issues": [
        {
            "id": 789, "node_id": "MDU6SXNzdWU3ODk=", "repository_id": 1296269, "number": 1,
            "title": "Documentation unclear on setup",
            "user": {"login": "devjane", "id": 25, "node_id": "MDQ6VXNlcjI1", "type": "User", "site_admin": False},
            "labels": [
                {"id": 208045947, "node_id": "TGFiZWwyMDgwNDU5NDc=", "repository_id": 1296269, "name": "documentation", "color": "0075ca", "description": "Doc improvements", "default": True},
                {"id": 208045948, "node_id": "TGFiZWwyMDgwNDU5NDg=", "repository_id": 1296269, "name": "help wanted", "color": "008672", "description": None, "default": False}
            ],
            "state": "open", "locked": False,
            "assignee": {"login": "octocat", "id": 1, "node_id": "MDQ6VXNlcjE=", "type": "User", "site_admin": False},
            "assignees": [{"login": "octocat", "id": 1, "node_id": "MDQ6VXNlcjE=", "type": "User", "site_admin": False}],
            "milestone": {
                "id": 1002604, "node_id": "MDk6TWlsZXN0b25lMTAwMjYwNA==", "repository_id": 1296269, "number": 3, "title": "Sprint 2.1 Docs Update", "description": "Update all docs for S2.1",
                "creator": {"login": "octocat", "id": 1, "node_id": "MDQ6VXNlcjE=", "type": "User", "site_admin": False},
                "open_issues": 2, "closed_issues": 5, "state": "open",
                "created_at": "2025-04-01T10:00:00Z", "updated_at": "2025-04-05T11:00:00Z",
                "closed_at": None, "due_on": "2025-05-30T23:59:59Z"
            },
            "comments": 1, "created_at": "2025-04-10T14:22:05Z", "updated_at": "2025-04-11T09:10:15Z",
            "closed_at": None, "body": "The README.md file is missing detailed instructions...",
            "author_association": "CONTRIBUTOR", "active_lock_reason": None,
            "reactions": {"url": "https://api.github.com/reactions/1", "total_count": 3, "+1": 2, "-1": 0, "laugh": 0, "hooray": 0, "confused": 0, "heart": 0, "rocket": 0, "eyes": 1},
            "score": 0.92,
        },
        {
            "id": 790, "node_id": "MDU6SXNzdWU3OTA=", "repository_id": 2100015, "number": 42,
            "title": "Model accuracy drops",
            "user": {"login": "devjane", "id": 25, "node_id": "MDQ6VXNlcjI1", "type": "User", "site_admin": False},
            "labels": [{"id": 208045946, "node_id": "TGFiZWwyMDgwNDU5NDY=", "repository_id": 2100015, "name": "bug", "color": "d73a4a", "description": "A bug", "default": True}],
            "state": "closed", "locked": True, "active_lock_reason": "resolved", "assignee": None, "assignees": [],
            "milestone": None, "comments": 5, "created_at": "2024-12-01T10:00:00Z",
            "updated_at": "2025-01-15T11:30:00Z", "closed_at": "2025-01-15T11:30:00Z",
            "body": "Model accuracy dropped significantly.", "author_association": "OWNER",
            "reactions": None,
            "score": 0.75,
        },
    ],
}
# --- End of DB structure ---

class TestGetIssue(BaseTestCaseWithErrorHandler):

    @classmethod
    def setUpClass(cls):
        cls.original_app_db_state = copy.deepcopy(GITHUB_APP_DB)
        GITHUB_APP_DB.clear()
        GITHUB_APP_DB.update(copy.deepcopy(INITIAL_DB_STATE))

    @classmethod
    def tearDownClass(cls):
        GITHUB_APP_DB.clear()
        GITHUB_APP_DB.update(cls.original_app_db_state)

    def setUp(self):
        current_test_db_state = copy.deepcopy(INITIAL_DB_STATE)
        GITHUB_APP_DB.clear()
        GITHUB_APP_DB.update(current_test_db_state)
        self.current_test_db_state = GITHUB_APP_DB

    def tearDown(self):
        GITHUB_APP_DB.clear()
        GITHUB_APP_DB.update(copy.deepcopy(INITIAL_DB_STATE))

    # --- Input Validation Tests ---
    def test_invalid_owner_type(self):
        with self.assertRaisesRegex(TypeError, "Owner must be a string."):
            get_issue(owner=123, repo="Hello-World", issue_number=1) # type: ignore

    def test_empty_owner(self):
        with self.assertRaisesRegex(ValueError, "Owner cannot be empty."):
            get_issue(owner="", repo="Hello-World", issue_number=1)

    def test_invalid_repo_type(self):
        with self.assertRaisesRegex(TypeError, "Repo must be a string."):
            get_issue(owner="octocat", repo=123, issue_number=1) # type: ignore

    def test_empty_repo(self):
        with self.assertRaisesRegex(ValueError, "Repo cannot be empty."):
            get_issue(owner="octocat", repo="", issue_number=1)

    def test_invalid_issue_number_type(self):
        with self.assertRaisesRegex(TypeError, "Issue number must be an integer."):
            get_issue(owner="octocat", repo="Hello-World", issue_number="abc") # type: ignore

    def test_non_positive_issue_number_zero(self):
        with self.assertRaisesRegex(ValueError, "Issue number must be a positive integer."):
            get_issue(owner="octocat", repo="Hello-World", issue_number=0)
            
    def test_non_positive_issue_number_negative(self):
        with self.assertRaisesRegex(ValueError, "Issue number must be a positive integer."):
            get_issue(owner="octocat", repo="Hello-World", issue_number=-1)

    # --- Successful Retrieval Tests ---
    def test_get_existing_issue_full_details(self):
        owner = "octocat"
        repo_name = "Hello-World"
        issue_number = 1
        retrieved_issue_dict = get_issue(owner, repo_name, issue_number)
        expected_dict = copy.deepcopy(next(i for i in INITIAL_DB_STATE["Issues"] if i["id"] == 789))
        self.assertEqual(retrieved_issue_dict, expected_dict)

    def test_get_existing_issue_reactions_none(self):
        owner = "devjane"
        repo_name = "ai-project-alpha"
        issue_number = 42 
        retrieved_issue_dict = get_issue(owner, repo_name, issue_number)
        expected_dict = copy.deepcopy(next(i for i in INITIAL_DB_STATE["Issues"] if i["id"] == 790))
        self.assertEqual(retrieved_issue_dict, expected_dict)
        self.assertIsNone(retrieved_issue_dict["reactions"])

    def test_get_issue_reactions_key_missing_in_db(self):
        issue_no_reactions_key = {
            "id": 1002, "node_id": "SXNzdWUxMDAy", "repository_id": 1296269, "number": 102,
            "title": "Issue with no reactions key",
            "user": {"login": "octocat", "id": 1, "node_id":"MDQ6VXNlcjE=", "type":"User", "site_admin":False},
            "created_at": "2023-05-02T10:00:00Z", "updated_at": "2023-05-02T11:00:00Z", "closed_at": None,
            "state": "open", "locked": False, "comments": 0, "labels": [], "assignees": [], "milestone": None,
            "body": "Test body.", "author_association": "OWNER", "active_lock_reason": None, "score": None,
        }
        self.current_test_db_state["Issues"].append(copy.deepcopy(issue_no_reactions_key))
        retrieved = get_issue("octocat", "Hello-World", 102)
        self.assertNotIn("reactions", retrieved) # Key should be absent if not in source

    # --- NotFoundError Tests ---
    def test_get_issue_repository_not_found(self):
        with self.assertRaisesRegex(NotFoundError, "Repository 'octocat/nonexistent-repo' not found."):
            get_issue("octocat", "nonexistent-repo", 1)

    def test_get_issue_not_found_in_repo(self):
        with self.assertRaisesRegex(NotFoundError, "Issue #9999 not found in repository 'octocat/Hello-World'."):
            get_issue("octocat", "Hello-World", 9999)

class TestCreateIssue(BaseTestCaseWithErrorHandler): # type: ignore

    def setUp(self):
        self.DB = DB # type: ignore
        self.DB.clear()

        # Define users
        self.creator_user_data = {
            'id': 1, 'login': 'issue_creator', 'node_id': 'U_NODE_CRTR', 'type': 'User', 
            'site_admin': False, 'name': 'Creator User', 'email': 'creator@example.com',
            'created_at': datetime(2019, 1, 1), 'updated_at': datetime(2019, 1, 1)
        }
        self.repo_owner_data = {
            'id': 2, 'login': 'owner_login', 'node_id': 'U_NODE_OWNR', 'type': 'User', 
            'site_admin': False, 'name': 'Repo Owner', 'email': 'owner@example.com',
            'created_at': datetime(2019, 1, 1), 'updated_at': datetime(2019, 1, 1)
        }
        self.assignee1_data = {
            'id': 3, 'login': 'assignee_one', 'node_id': 'U_NODE_ASS1', 'type': 'User', 
            'site_admin': False, 'name': 'Assignee One', 'email': 'assignee1@example.com',
            'created_at': datetime(2019, 1, 1), 'updated_at': datetime(2019, 1, 1)
        }
        self.assignee2_data = {
            'id': 4, 'login': 'assignee_two', 'node_id': 'U_NODE_ASS2', 'type': 'User', 
            'site_admin': False, 'name': 'Assignee Two', 'email': 'assignee2@example.com',
            'created_at': datetime(2019, 1, 1), 'updated_at': datetime(2019, 1, 1)
        }
        self.stranger_user_data = {
            'id': 5, 'login': 'stranger_user', 'node_id': 'U_NODE_STRNGR', 'type': 'User',
            'site_admin': False, 'name': 'Stranger User', 'email': 'stranger@example.com',
            'created_at': datetime(2019, 1, 1), 'updated_at': datetime(2019, 1, 1)
        }

        self.DB['Users'] = [
            copy.deepcopy(self.creator_user_data),
            copy.deepcopy(self.repo_owner_data),
            copy.deepcopy(self.assignee1_data),
            copy.deepcopy(self.assignee2_data),
            copy.deepcopy(self.stranger_user_data),
        ]

        self.repo_owner_for_repo_obj = {
            'id': self.repo_owner_data['id'], 'login': self.repo_owner_data['login'],
            'node_id': self.repo_owner_data['node_id'], 'type': self.repo_owner_data['type'],
            'site_admin': self.repo_owner_data['site_admin']
        }
        self.creator_user_for_repo_obj = {
             'id': self.creator_user_data['id'], 'login': self.creator_user_data['login'],
            'node_id': self.creator_user_data['node_id'], 'type': self.creator_user_data['type'],
            'site_admin': self.creator_user_data['site_admin']
        }

        self.repo1_data = {
            'id': 101, 'node_id': 'R_NODE_101', 'name': 'repo1', 'full_name': 'owner_login/repo1',
            'private': False, 'owner': copy.deepcopy(self.repo_owner_for_repo_obj), 
            'description': 'Test repo 1 (public)', 'fork': False, 
            'created_at': datetime(2020, 1, 1), 'updated_at': datetime(2020, 1, 1),
            'pushed_at': datetime(2020, 1, 1), 'size': 100, 'has_issues': True,
            'open_issues_count': 0, 'default_branch': 'main', 'topics': [], 'language': None
        }
        self.repo_private_data = {
            'id': 102, 'node_id': 'R_NODE_102', 'name': 'privaterepo', 'full_name': 'owner_login/privaterepo',
            'private': True, 'owner': copy.deepcopy(self.repo_owner_for_repo_obj), 
            'description': 'Private repo', 'fork': False, 
            'created_at': datetime(2020, 1, 1), 'updated_at': datetime(2020, 1, 1),
            'pushed_at': datetime(2020, 1, 1), 'size': 100, 'has_issues': True,
            'open_issues_count': 0, 'default_branch': 'main', 'topics': [], 'language': None
        }
        self.repo_no_issues_data = {
            'id': 103, 'node_id': 'R_NODE_103', 'name': 'noissuesrepo', 'full_name': 'owner_login/noissuesrepo',
            'private': False, 'owner': copy.deepcopy(self.repo_owner_for_repo_obj), 
            'description': 'Repo with issues disabled', 'fork': False, 
            'created_at': datetime(2020, 1, 1), 'updated_at': datetime(2020, 1, 1),
            'pushed_at': datetime(2020, 1, 1), 'size': 100, 'has_issues': False,
            'open_issues_count': 0, 'default_branch': 'main', 'topics': [], 'language': None
        }
        self.repo_owned_by_creator_data = {
            'id': 104, 'node_id': 'R_NODE_104', 'name': 'creator-owned-repo', 'full_name': 'issue_creator/creator-owned-repo',
            'private': False, 'owner': copy.deepcopy(self.creator_user_for_repo_obj), 
            'description': 'Repo owned by creator', 'fork': False, 
            'created_at': datetime(2020, 1, 1), 'updated_at': datetime(2020, 1, 1),
            'pushed_at': datetime(2020, 1, 1), 'size': 100, 'has_issues': True,
            'open_issues_count': 0, 'default_branch': 'main', 'topics': [], 'language': None
        }

        self.DB['Repositories'] = [
            copy.deepcopy(self.repo1_data), 
            copy.deepcopy(self.repo_private_data), 
            copy.deepcopy(self.repo_no_issues_data),
            copy.deepcopy(self.repo_owned_by_creator_data)
        ]

        self.label_bug_data = {
            'id': 201, 'node_id': 'L_NODE_BUG', 'repository_id': 101, 'name': 'bug',
            'color': 'd73a4a', 'description': "Something isn't working", 'default': True
        }
        self.label_feature_data = {
            'id': 202, 'node_id': 'L_NODE_FEAT', 'repository_id': 101, 'name': 'feature-request',
            'color': 'a2eeef', 'description': 'New feature or request', 'default': False
        }
        self.label_doc_data = {
            'id': 203, 'node_id': 'L_NODE_DOC', 'repository_id': 104, 'name': 'documentation',
            'color': '0075ca', 'description': 'Improvements or additions to documentation', 'default': True
        }
        self.DB['RepositoryLabels'] = [
            copy.deepcopy(self.label_bug_data), 
            copy.deepcopy(self.label_feature_data),
            copy.deepcopy(self.label_doc_data)
        ]

        self.DB['RepositoryCollaborators'] = [
            {'repository_id': self.repo1_data['id'], 'user_id': self.creator_user_data['id'], 'permission': 'write'},
            {'repository_id': self.repo_private_data['id'], 'user_id': self.creator_user_data['id'], 'permission': 'write'},
        ]

        self.DB['Issues'] = []
        self.DB['Milestones'] = []

        # Set the current authenticated user using the proper format
        self.DB['CurrentUser'] = {'id': self.creator_user_data['id'], 'login': self.creator_user_data['login']}


    def _assert_issue_details_valid(self, issue_data: Dict[str, Any], expected_title: str,
                                    expected_body: Optional[str],
                                    expected_creator_login: str,
                                    expected_repo_full_name: str,
                                    expected_assignees_logins: Optional[List[str]] = None,
                                    expected_labels_names: Optional[List[str]] = None,
                                    expected_author_association: str = "MEMBER",
                                    expected_issue_number: int = 1,
                                    expected_open_issues_count_after: int = 1):
        self.assertIsInstance(issue_data, dict)

        # Validate structure based on IssueDetails Pydantic model
        # In a real test harness, you might parse it: validated_issue = IssueDetails(**issue_data)
        self.assertIsInstance(issue_data.get('id'), int)
        self.assertIsInstance(issue_data.get('node_id'), str)
        self.assertEqual(issue_data.get('number'), expected_issue_number)
        self.assertEqual(issue_data.get('title'), expected_title)
        self.assertEqual(issue_data.get('body'), expected_body)

        user_info = issue_data.get('user')
        self.assertIsInstance(user_info, dict)
        self.assertEqual(user_info.get('login'), expected_creator_login)
        self.assertEqual(user_info.get('id'), self.DB['CurrentUser']['id'])

        self.assertEqual(issue_data.get('state'), 'open')
        self.assertEqual(issue_data.get('locked'), False)
        self.assertEqual(issue_data.get('comments'), 0)

        self.assertIsInstance(issue_data.get('created_at'), str)
        self.assertTrue(issue_data['created_at'].endswith('Z'))
        self.assertIsInstance(issue_data.get('updated_at'), str)
        self.assertTrue(issue_data['updated_at'].endswith('Z'))
        self.assertIsNone(issue_data.get('closed_at'))

        self.assertEqual(issue_data.get('author_association'), expected_author_association)

        if expected_assignees_logins:
            self.assertIsNotNone(issue_data.get('assignees'))
            self.assertEqual(len(issue_data['assignees']), len(expected_assignees_logins))
            returned_assignee_logins = sorted([a['login'] for a in issue_data['assignees']])
            self.assertEqual(returned_assignee_logins, sorted(expected_assignees_logins))
            if issue_data['assignees']:
                 self.assertEqual(issue_data['assignee']['login'], issue_data['assignees'][0]['login'])
            else: # Should not happen if expected_assignees_logins is not empty
                 self.assertIsNone(issue_data['assignee'])
        else:
            self.assertEqual(issue_data.get('assignees', []), [])
            self.assertIsNone(issue_data.get('assignee'))

        if expected_labels_names:
            self.assertIsNotNone(issue_data.get('labels'))
            self.assertEqual(len(issue_data['labels']), len(expected_labels_names))
            returned_label_names = sorted([l['name'] for l in issue_data['labels']])
            self.assertEqual(returned_label_names, sorted(expected_labels_names))
        else:
            self.assertEqual(issue_data.get('labels', []), [])

        self.assertIsNone(issue_data.get('milestone'))

        db_issue = next((iss for iss in self.DB['Issues'] if iss['id'] == issue_data['id']), None)
        self.assertIsNotNone(db_issue)
        self.assertEqual(db_issue['title'], expected_title)

        repo_in_db = next(r for r in self.DB['Repositories'] if r['full_name'] == expected_repo_full_name)
        self.assertEqual(repo_in_db['open_issues_count'], expected_open_issues_count_after)

    def test_create_issue_minimal(self):
        owner = 'owner_login'
        repo_name = 'repo1'
        title = "Minimal Test Issue"
        self.DB['CurrentUser'] = {'id': self.creator_user_data['id'], 'login': self.creator_user_data['login']}
        result = create_issue(owner=owner, repo=repo_name, title=title) # type: ignore
        self._assert_issue_details_valid(
            result, title, None, self.creator_user_data['login'], f"{owner}/{repo_name}",
            expected_author_association="MEMBER"
        )

    def test_create_issue_with_body(self):
        owner = 'owner_login'
        repo_name = 'repo1'
        title = "Issue With Body"
        body = "This is the detailed description."
        self.DB['CurrentUser'] = {'id': self.creator_user_data['id'], 'login': self.creator_user_data['login']}
        result = create_issue(owner=owner, repo=repo_name, title=title, body=body) # type: ignore
        self._assert_issue_details_valid(
            result, title, body, self.creator_user_data['login'], f"{owner}/{repo_name}",
            expected_author_association="MEMBER"
        )

    def test_create_issue_with_assignees(self):
        owner = 'owner_login'
        repo_name = 'repo1'
        title = "Issue With Assignees"
        assignees = [self.assignee1_data['login'], self.assignee2_data['login']]
        self.DB['CurrentUser'] = {'id': self.creator_user_data['id'], 'login': self.creator_user_data['login']}
        result = create_issue(owner=owner, repo=repo_name, title=title, assignees=assignees) # type: ignore
        self._assert_issue_details_valid(
            result, title, None, self.creator_user_data['login'], f"{owner}/{repo_name}",
            expected_assignees_logins=assignees, expected_author_association="MEMBER"
        )

    def test_create_issue_with_labels(self):
        owner = 'owner_login'
        repo_name = 'repo1'
        title = "Issue With Labels"
        labels = [self.label_bug_data['name'], self.label_feature_data['name']]
        self.DB['CurrentUser'] = {'id': self.creator_user_data['id'], 'login': self.creator_user_data['login']}
        result = create_issue(owner=owner, repo=repo_name, title=title, labels=labels) # type: ignore
        self._assert_issue_details_valid(
            result, title, None, self.creator_user_data['login'], f"{owner}/{repo_name}",
            expected_labels_names=labels, expected_author_association="MEMBER"
        )

    def test_create_issue_with_all_options(self):
        owner = 'owner_login'
        repo_name = 'repo1'
        title = "Issue Fully Loaded"
        body = "This issue has everything."
        assignees = [self.assignee1_data['login']]
        labels = [self.label_bug_data['name']]
        self.DB['CurrentUser'] = {'id': self.creator_user_data['id'], 'login': self.creator_user_data['login']}
        result = create_issue(owner=owner, repo=repo_name, title=title, body=body, assignees=assignees, labels=labels) # type: ignore
        self._assert_issue_details_valid(
            result, title, body, self.creator_user_data['login'], f"{owner}/{repo_name}",
            assignees, labels, expected_author_association="MEMBER"
        )

    def test_create_issue_repo_not_found(self):
        self.DB['CurrentUser'] = {'id': self.creator_user_data['id'], 'login': self.creator_user_data['login']}
        self.assert_error_behavior(func_to_call=create_issue, expected_exception_type=NotFoundError, expected_message="Repository 'owner_login/nonexistentrepo' not found.", # type: ignore
            owner='owner_login', repo='nonexistentrepo', title="A title")

    def test_create_issue_title_empty(self):
        self.DB['CurrentUser'] = {'id': self.creator_user_data['id'], 'login': self.creator_user_data['login']}
        self.assert_error_behavior(func_to_call=create_issue, expected_exception_type=ValidationError, expected_message="Title is a required field.", # type: ignore
            owner='owner_login', repo='repo1', title="")

    def test_create_issue_owner_empty_or_repo_empty(self):
        self.DB['CurrentUser'] = {'id': self.creator_user_data['id'], 'login': self.creator_user_data['login']}
        self.assert_error_behavior(func_to_call=create_issue, expected_exception_type=ValidationError, expected_message="Owner is a required field.", # type: ignore
            owner='', repo='repo1', title="Valid Title")
        self.assert_error_behavior(func_to_call=create_issue, expected_exception_type=ValidationError, expected_message="Repository name is a required field.", # type: ignore
            owner='owner_login', repo='', title="Valid Title")

    def test_create_issue_non_existent_owner_leads_to_repo_not_found(self):
        self.DB['CurrentUser'] = {'id': self.creator_user_data['id'], 'login': self.creator_user_data['login']}
        self.assert_error_behavior(func_to_call=create_issue, expected_exception_type=NotFoundError, expected_message="Repository 'non_existent_owner/repo1' not found.", # type: ignore
            owner='non_existent_owner', repo='repo1', title="Valid Title")

    def test_create_issue_assignee_not_found(self):
        self.DB['CurrentUser'] = {'id': self.creator_user_data['id'], 'login': self.creator_user_data['login']}
        self.assert_error_behavior(func_to_call=create_issue, expected_exception_type=ValidationError, expected_message="Assignee user 'nonexistent_user_login' not found.", # type: ignore
            owner='owner_login', repo='repo1', title="Issue with bad assignee", assignees=['nonexistent_user_login'])

    def test_create_issue_label_not_found_for_repo(self):
        self.DB['CurrentUser'] = {'id': self.creator_user_data['id'], 'login': self.creator_user_data['login']}
        self.assert_error_behavior(func_to_call=create_issue, expected_exception_type=ValidationError, expected_message="Label 'nonexistent_label_name' not found in repository 'owner_login/repo1'.", # type: ignore
            owner='owner_login', repo='repo1', title="Issue with bad label", labels=['nonexistent_label_name'])

    def test_create_issue_permissions_repo_has_issues_false(self):
        self.DB['CurrentUser'] = {'id': self.creator_user_data['id'], 'login': self.creator_user_data['login']}
        self.assert_error_behavior(func_to_call=create_issue, expected_exception_type=ForbiddenError, expected_message="Issues are not enabled for repository 'owner_login/noissuesrepo'.", # type: ignore
            owner='owner_login', repo='noissuesrepo', title="Cannot create this")

    def test_create_issue_permissions_user_not_collaborator_on_private_repo(self):
        self.DB['CurrentUser'] = {'id': self.stranger_user_data['id'], 'login': self.stranger_user_data['login']}
        self.assert_error_behavior(func_to_call=create_issue, expected_exception_type=ForbiddenError, expected_message="You don't have permission to create issues on 'owner_login/privaterepo'", # type: ignore
            owner='owner_login', repo='privaterepo', title="Access Denied Issue")


    def test_issue_number_increment(self):
        owner = 'owner_login'
        repo_name = 'repo1'
        self.DB['CurrentUser'] = {'id': self.creator_user_data['id'], 'login': self.creator_user_data['login']}

        result1 = create_issue(owner=owner, repo=repo_name, title="First Issue") # type: ignore
        self.assertEqual(result1['number'], 1)
        repo_db_obj = next(r for r in self.DB['Repositories'] if r['full_name'] == f"{owner}/{repo_name}")
        self.assertEqual(repo_db_obj['open_issues_count'], 1)

        result2 = create_issue(owner=owner, repo=repo_name, title="Second Issue") # type: ignore
        self.assertEqual(result2['number'], 2)
        # Get the repository object again to see the updated count
        repo_db_obj = next(r for r in self.DB['Repositories'] if r['full_name'] == f"{owner}/{repo_name}")
        self.assertEqual(repo_db_obj['open_issues_count'], 2)
        self.assertEqual(len(self.DB['Issues']), 2)

    def test_author_association_owner(self):
        owner_login = self.creator_user_data['login']
        repo_name = 'creator-owned-repo'
        title = "Issue by Owner"
        self.DB['CurrentUser'] = {'id': self.creator_user_data['id'], 'login': self.creator_user_data['login']}
        result = create_issue(owner=owner_login, repo=repo_name, title=title) # type: ignore
        self.assertEqual(result['author_association'], "OWNER")

    def test_author_association_member(self):
        owner_login = self.repo_owner_data['login']
        repo_name = 'repo1'
        title = "Issue by Member"
        self.DB['CurrentUser'] = {'id': self.creator_user_data['id'], 'login': self.creator_user_data['login']}
        result = create_issue(owner=owner_login, repo=repo_name, title=title) # type: ignore
        self.assertEqual(result['author_association'], "MEMBER")

    def test_author_association_contributor_or_none_public_repo(self):
        owner_login = self.repo_owner_data['login']
        repo_name = 'repo1'
        title = "Issue by Stranger on Public Repo"
        self.DB['CurrentUser'] = {'id': self.stranger_user_data['id'], 'login': self.stranger_user_data['login']}
        result = create_issue(owner=owner_login, repo=repo_name, title=title) # type: ignore
        self.assertIn(result['author_association'], ["CONTRIBUTOR", "NONE"])

    def test_create_issue_with_empty_assignees_list(self):
        owner = 'owner_login'
        repo_name = 'repo1'
        title = "Issue with empty assignees"
        self.DB['CurrentUser'] = {'id': self.creator_user_data['id'], 'login': self.creator_user_data['login']}
        result = create_issue(owner=owner, repo=repo_name, title=title, assignees=[]) # type: ignore
        self._assert_issue_details_valid(
            result, title, None, self.creator_user_data['login'], f"{owner}/{repo_name}",
            expected_assignees_logins=[], expected_author_association="MEMBER"
        )

    def test_create_issue_with_empty_labels_list(self):
        owner = 'owner_login'
        repo_name = 'repo1'
        title = "Issue with empty labels"
        self.DB['CurrentUser'] = {'id': self.creator_user_data['id'], 'login': self.creator_user_data['login']}
        result = create_issue(owner=owner, repo=repo_name, title=title, labels=[]) # type: ignore
        self._assert_issue_details_valid(
            result, title, None, self.creator_user_data['login'], f"{owner}/{repo_name}",
            expected_labels_names=[], expected_author_association="MEMBER"
        )

    def test_create_issue_duplicate_assignees_are_deduplicated(self):
        owner = 'owner_login'
        repo_name = 'repo1'
        title = "Issue With Duplicate Assignees"
        assignees_with_duplicates = [self.assignee1_data['login'], self.assignee1_data['login'], self.assignee2_data['login']]
        expected_unique_assignees = sorted([self.assignee1_data['login'], self.assignee2_data['login']])
        self.DB['CurrentUser'] = {'id': self.creator_user_data['id'], 'login': self.creator_user_data['login']}
        result = create_issue(owner=owner, repo=repo_name, title=title, assignees=assignees_with_duplicates) # type: ignore

        returned_assignee_logins = sorted([a['login'] for a in result['assignees']])
        self.assertEqual(returned_assignee_logins, expected_unique_assignees)
        self.assertEqual(len(result['assignees']), len(expected_unique_assignees))
        if result['assignees']: # Ensure primary assignee is from the de-duplicated list
            self.assertEqual(result['assignee']['login'], result['assignees'][0]['login'])


    def test_create_issue_duplicate_labels_are_deduplicated(self):
        owner = 'owner_login'
        repo_name = 'repo1'
        title = "Issue With Duplicate Labels"
        labels_with_duplicates = [self.label_bug_data['name'], self.label_bug_data['name'], self.label_feature_data['name']]
        expected_unique_labels = sorted([self.label_bug_data['name'], self.label_feature_data['name']])
        self.DB['CurrentUser'] = {'id': self.creator_user_data['id'], 'login': self.creator_user_data['login']}
        result = create_issue(owner=owner, repo=repo_name, title=title, labels=labels_with_duplicates) # type: ignore

        returned_label_names = sorted([l['name'] for l in result['labels']])
        self.assertEqual(returned_label_names, expected_unique_labels)
        self.assertEqual(len(result['labels']), len(expected_unique_labels))
    def test_no_authenticated_user(self):
        """Test case for when no authenticated user is found in the context."""
        # Clear the user context to trigger the error
        self.DB['CurrentUser'] = {}  # Remove user_id key
        self.assert_error_behavior(func_to_call=create_issue, expected_exception_type=RuntimeError, expected_message="No authenticated user found", owner='owner_login', repo='repo1', title="Issue with no auth user")

    def test_user_not_found_in_db(self):
        """Test case for when user ID exists in context but user doesn't exist in database."""
        # Set a non-existent user ID
        self.DB['CurrentUser'] = {'id': 999, 'login': 'nonexistent_user'}  # ID that doesn't exist in DB
        self.assert_error_behavior(func_to_call=create_issue, expected_exception_type=RuntimeError, expected_message="User with ID 999 not found", owner='owner_login', repo='repo1', title="Issue with non-existent user")

    def test_collaborator_can_create_issue_in_private_repo(self):
        """Test that a collaborator (not owner) can create an issue in a private repo."""
        owner = 'owner_login'
        repo_name = 'privaterepo'
        title = "Issue by collaborator on private repo"
        
        # Ensure user is a collaborator but not the owner
        self.DB['CurrentUser'] = {'id': self.creator_user_data['id'], 'login': self.creator_user_data['login']}
        
        # Verify the setup: creator is not owner but is a collaborator
        repo = next(r for r in self.DB['Repositories'] if r['full_name'] == f"{owner}/{repo_name}")
        self.assertTrue(repo['private'])
        self.assertNotEqual(repo['owner']['id'], self.creator_user_data['id'])
        
        # Verify collaborator relationship exists in DB
        collab_exists = False
        for collab in self.DB['RepositoryCollaborators']:
            if (collab['repository_id'] == repo['id'] and 
                collab['user_id'] == self.creator_user_data['id']):
                collab_exists = True
                break
        self.assertTrue(collab_exists)
        
        # This should succeed because creator is a collaborator
        result = create_issue(owner=owner, repo=repo_name, title=title)
        
        # Basic validations
        self.assertEqual(result['title'], title)
        self.assertEqual(result['state'], 'open')

class TestAddIssueComment(BaseTestCaseWithErrorHandler):

    def setUp(self):
        self.DB = DB  # DB is globally available
        self.DB.clear()

        # Default datetime for consistent testing
        self.fixed_time = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        self.fixed_time_iso = self.fixed_time.isoformat().replace("+00:00", "Z")

        self.owner_user = {
            "id": 1, "login": "owner_user", "node_id": "U_1", "type": "User", "site_admin": False,
            "name": "Owner User", "email": "owner@example.com", "company": "Org",
            "location": "City", "bio": "Owner bio", "public_repos": 1, "public_gists": 0,
            "followers": 10, "following": 5,
            "created_at": self.fixed_time, "updated_at": self.fixed_time
        }
        self.collaborator_user = {
            "id": 2, "login": "collab_user", "node_id": "U_2", "type": "User", "site_admin": False,
            "name": "Collaborator User", "email": "collab@example.com",
            "created_at": self.fixed_time, "updated_at": self.fixed_time
        }
        self.other_user = {
            "id": 3, "login": "other_user", "node_id": "U_3", "type": "User", "site_admin": False,
            "name": "Other User", "email": "other@example.com",
            "created_at": self.fixed_time, "updated_at": self.fixed_time
        }
        # START: New User for CONTRIBUTOR tests
        self.issue_author_user = {
            "id": 4, "login": "issue_author_user", "node_id": "U_4", "type": "User", "site_admin": False,
            "name": "Issue Author User", "email": "issueauthor@example.com",
            "created_at": self.fixed_time, "updated_at": self.fixed_time
        }
        # END: New User
        self.DB["Users"] = [self.owner_user, self.collaborator_user, self.other_user, self.issue_author_user] # Added issue_author_user

        self.repo1 = {
            "id": 101, "node_id": "R_101", "name": "repo1", "full_name": "owner_user/repo1",
            "private": False, "owner": {"id": 1, "login": "owner_user", "node_id": "U_1", "type": "User", "site_admin": False},
            "description": "Test repo 1", "fork": False,
            "created_at": self.fixed_time, "updated_at": self.fixed_time, "pushed_at": self.fixed_time,
            "size": 100, "stargazers_count": 10, "watchers_count": 10, "language": "Python",
            "has_issues": True, "has_projects": True, "has_downloads": True, "has_wiki": True,
            "has_pages": False, "forks_count": 0, "open_issues_count": 1, # This will be affected by new issues
            "archived": False, "disabled": False, "default_branch": "main", "visibility": "public"
        }
        self.repo2_issues_disabled = {
            "id": 102, "node_id": "R_102", "name": "repo2", "full_name": "owner_user/repo2",
            "private": False, "owner": {"id": 1, "login": "owner_user", "node_id": "U_1", "type": "User", "site_admin": False},
            "description": "Test repo 2", "fork": False,
            "created_at": self.fixed_time, "updated_at": self.fixed_time, "pushed_at": self.fixed_time,
            "size": 100, "has_issues": False, "open_issues_count": 0, "visibility": "public"
        }
        self.repo3_private = {
            "id": 103, "node_id": "R_103", "name": "private_repo", "full_name": "owner_user/private_repo",
            "private": True, "owner": {"id": 1, "login": "owner_user", "node_id": "U_1", "type": "User", "site_admin": False},
            "description": "Test repo 3 private", "fork": False,
            "created_at": self.fixed_time, "updated_at": self.fixed_time, "pushed_at": self.fixed_time,
            "size": 100, "has_issues": True, "open_issues_count": 0, "visibility": "private"
        }
        self.DB["Repositories"] = [self.repo1, self.repo2_issues_disabled, self.repo3_private]

        self.issue1_repo1 = {
            "id": 1001, "node_id": "I_1001", "repository_id": 101, "number": 1,
            "title": "Test Issue 1", "user": {"id": 1, "login": "owner_user"}, # simplified user
            "labels": [], "state": "open", "locked": False, "assignee": None, "assignees": [],
            "milestone": None, "comments": 0,
            "created_at": self.fixed_time, "updated_at": self.fixed_time, "closed_at": None,
            "body": "Body of test issue 1", "author_association": "OWNER"
        }
        self.issue2_repo1 = {
            "id": 1002, "node_id": "I_1002", "repository_id": 101, "number": 2,
            "title": "Test Issue 2", "user": {"id": 1, "login": "owner_user"},
            "labels": [], "state": "open", "locked": False, "assignee": None, "assignees": [],
            "milestone": None, "comments": 0,
            "created_at": self.fixed_time, "updated_at": self.fixed_time, "closed_at": None,
            "body": "Body of test issue 2", "author_association": "OWNER"
        }
        # START: New Issues for locked and contributor tests
        self.issue3_repo1_locked = {
            "id": 1003, "node_id": "I_1003", "repository_id": self.repo1["id"], "number": 3,
            "title": "Test Locked Issue", "user": {"id": self.owner_user["id"], "login": self.owner_user["login"]},
            "labels": [], "state": "open", "locked": True, "assignee": None, "assignees": [], # LOCKED
            "milestone": None, "comments": 0,
            "created_at": self.fixed_time, "updated_at": self.fixed_time, "closed_at": None,
            "body": "Body of test locked issue", "author_association": "OWNER"
        }
        self.issue4_repo1_by_issue_author = {
            "id": 1004, "node_id": "I_1004", "repository_id": self.repo1["id"], "number": 4,
            "title": "Issue by Issue Author User",
            "user": {"id": self.issue_author_user["id"], "login": self.issue_author_user["login"]}, # Authored by issue_author_user
            "labels": [], "state": "open", "locked": False, "assignee": None, "assignees": [],
            "milestone": None, "comments": 0,
            "created_at": self.fixed_time, "updated_at": self.fixed_time, "closed_at": None,
            "body": "Body of issue by issue_author_user", "author_association": "NONE" # Issue's own association to repo
        }
        # END: New Issues
        self.DB["Issues"] = [self.issue1_repo1, self.issue2_repo1, self.issue3_repo1_locked, self.issue4_repo1_by_issue_author] # Added new issues

        self.DB["IssueComments"] = []
        self.DB["RepositoryCollaborators"] = [
            {"repository_id": 101, "user_id": 2, "permission": "write"}, # collaborator_user on repo1
            {"repository_id": 103, "user_id": 2, "permission": "read"}
        ]
        self.DB["CurrentUser"] = {"id": self.owner_user["id"], "login": self.owner_user["login"]}

    def _set_current_user(self, user_id: int, login: str):
        self.DB["CurrentUser"] = {"id": user_id, "login": login}

    def test_validate_owner_is_none(self):
        with self.assertRaisesRegex(ValidationError, "Repository owner must be a non-empty string."):
            add_issue_comment(
                owner=None,
                repo=self.repo1["name"], # valid repo
                issue_number=self.issue1_repo1["number"], # valid issue number
                body="Valid body content" # valid body
            )

    def test_validate_owner_is_empty_string(self):
        with self.assertRaisesRegex(ValidationError, "Repository owner must be a non-empty string."):
            add_issue_comment(
                owner="",
                repo=self.repo1["name"],
                issue_number=self.issue1_repo1["number"],
                body="Valid body content"
            )

    def test_validate_owner_is_whitespace_string(self):
        with self.assertRaisesRegex(ValidationError, "Repository owner must be a non-empty string."):
            add_issue_comment(
                owner="   ",
                repo=self.repo1["name"],
                issue_number=self.issue1_repo1["number"],
                body="Valid body content"
            )

    def test_validate_owner_is_not_string(self):
        with self.assertRaisesRegex(ValidationError, "Repository owner must be a non-empty string."):
            add_issue_comment(
                owner=123, # Not a string
                repo=self.repo1["name"],
                issue_number=self.issue1_repo1["number"],
                body="Valid body content"
            )

    # --- Tests for 'repo' validation ---
    def test_validate_repo_is_none(self):
        with self.assertRaisesRegex(ValidationError, "Repository name must be a non-empty string."):
            add_issue_comment(
                owner=self.owner_user["login"], # valid owner
                repo=None,
                issue_number=self.issue1_repo1["number"],
                body="Valid body content"
            )

    def test_validate_repo_is_empty_string(self):
        with self.assertRaisesRegex(ValidationError, "Repository name must be a non-empty string."):
            add_issue_comment(
                owner=self.owner_user["login"],
                repo="",
                issue_number=self.issue1_repo1["number"],
                body="Valid body content"
            )

    def test_validate_repo_is_whitespace_string(self):
        with self.assertRaisesRegex(ValidationError, "Repository name must be a non-empty string."):
            add_issue_comment(
                owner=self.owner_user["login"],
                repo="   ",
                issue_number=self.issue1_repo1["number"],
                body="Valid body content"
            )

    def test_validate_repo_is_not_string(self):
        with self.assertRaisesRegex(ValidationError, "Repository name must be a non-empty string."):
            add_issue_comment(
                owner=self.owner_user["login"],
                repo=123, # Not a string
                issue_number=self.issue1_repo1["number"],
                body="Valid body content"
            )

    # --- Tests for 'issue_number' validation ---
    def test_validate_issue_number_is_zero(self):
        with self.assertRaisesRegex(ValidationError, "Issue number must be a positive integer."):
            add_issue_comment(
                owner=self.owner_user["login"],
                repo=self.repo1["name"],
                issue_number=0, # Zero
                body="Valid body content"
            )

    def test_validate_issue_number_is_negative(self):
        with self.assertRaisesRegex(ValidationError, "Issue number must be a positive integer."):
            add_issue_comment(
                owner=self.owner_user["login"],
                repo=self.repo1["name"],
                issue_number=-5, # Negative
                body="Valid body content"
            )

    def test_validate_issue_number_is_not_int(self):
        with self.assertRaisesRegex(ValidationError, "Issue number must be a positive integer."):
            add_issue_comment(
                owner=self.owner_user["login"],
                repo=self.repo1["name"],
                issue_number="123", # Not an int (string)
                body="Valid body content"
            )
            
    def test_validate_issue_number_is_none(self): # Also not a positive integer
        with self.assertRaisesRegex(ValidationError, "Issue number must be a positive integer."):
            add_issue_comment(
                owner=self.owner_user["login"],
                repo=self.repo1["name"],
                issue_number=None, # Not an int
                body="Valid body content"
            )

    # --- Tests for 'body' validation ---
    def test_validate_body_is_none(self): # This likely matches your existing test_add_comment_body_missing_none
        with self.assertRaisesRegex(ValidationError, "Comment body cannot be empty or consist only of whitespace."):
            add_issue_comment(
                owner=self.owner_user["login"],
                repo=self.repo1["name"],
                issue_number=self.issue1_repo1["number"],
                body=None
            )

    def test_validate_body_is_empty_string(self): # This likely matches your existing test_add_comment_body_empty_string
        with self.assertRaisesRegex(ValidationError, "Comment body cannot be empty or consist only of whitespace."):
            add_issue_comment(
                owner=self.owner_user["login"],
                repo=self.repo1["name"],
                issue_number=self.issue1_repo1["number"],
                body=""
            )

    def test_validate_body_is_whitespace_string(self): # This likely matches your existing test_add_comment_body_whitespace_string
        with self.assertRaisesRegex(ValidationError, "Comment body cannot be empty or consist only of whitespace."):
            add_issue_comment(
                owner=self.owner_user["login"],
                repo=self.repo1["name"],
                issue_number=self.issue1_repo1["number"],
                body="   "
            )

    def test_validate_body_is_not_string(self):
        with self.assertRaisesRegex(ValidationError, "Comment body cannot be empty or consist only of whitespace."):
            add_issue_comment(
                owner=self.owner_user["login"],
                repo=self.repo1["name"],
                issue_number=self.issue1_repo1["number"],
                body=123 # Not a string
            )

    def test_add_comment_success_owner(self):
        self._set_current_user(self.owner_user["id"], self.owner_user["login"])
        comment_body = "This is a comment from the owner."

        response = add_issue_comment(
            owner="owner_user", repo="repo1", issue_number=1, body=comment_body
        )

        self.assertIsInstance(response, dict)
        self.assertEqual(response["body"], comment_body)
        self.assertEqual(response["user"]["login"], self.owner_user["login"])
        self.assertEqual(response["author_association"], "OWNER")

        # Validate with Pydantic model
        AddIssueCommentResponse.model_validate(response)

        self.assertEqual(len(self.DB["IssueComments"]), 1)
        db_comment = self.DB["IssueComments"][0]
        self.assertEqual(db_comment["body"], comment_body)
        self.assertEqual(db_comment["user"]["id"], self.owner_user["id"])
        self.assertEqual(db_comment["author_association"], "OWNER")
        self.assertEqual(db_comment["issue_id"], self.issue1_repo1["id"])
        self.assertEqual(db_comment["repository_id"], self.repo1["id"])

        updated_issue = next(i for i in self.DB["Issues"] if i["id"] == self.issue1_repo1["id"])
        self.assertEqual(updated_issue["comments"], 1)

    def test_add_comment_success_collaborator_write_permission(self):
        self._set_current_user(self.collaborator_user["id"], self.collaborator_user["login"])
        comment_body = "Comment from collaborator with write access."

        response = add_issue_comment(
            owner="owner_user", repo="repo1", issue_number=1, body=comment_body
        )

        self.assertEqual(response["body"], comment_body)
        self.assertEqual(response["user"]["login"], self.collaborator_user["login"])
        self.assertEqual(response["author_association"], "MEMBER")
        AddIssueCommentResponse.model_validate(response)
        self.assertEqual(len(self.DB["IssueComments"]), 1)
        self.assertEqual(self.DB["IssueComments"][0]["author_association"], "MEMBER")
        updated_issue = next(i for i in self.DB["Issues"] if i["id"] == self.issue1_repo1["id"])
        self.assertEqual(updated_issue["comments"], 1)

    def test_add_comment_success_public_repo_other_user(self):
        self._set_current_user(self.other_user["id"], self.other_user["login"])
        comment_body = "Comment from another user on a public repo."

        response = add_issue_comment(
            owner="owner_user", repo="repo1", issue_number=1, body=comment_body
        )

        self.assertEqual(response["body"], comment_body)
        self.assertEqual(response["user"]["login"], self.other_user["login"])
        # Assuming 'NONE' for users without explicit roles or contribution history
        self.assertEqual(response["author_association"], "NONE") 
        AddIssueCommentResponse.model_validate(response)
        self.assertEqual(len(self.DB["IssueComments"]), 1)
        self.assertEqual(self.DB["IssueComments"][0]["author_association"], "NONE")
        updated_issue = next(i for i in self.DB["Issues"] if i["id"] == self.issue1_repo1["id"])
        self.assertEqual(updated_issue["comments"], 1)

    def test_add_comment_response_structure_and_values(self):
        self._set_current_user(self.owner_user["id"], self.owner_user["login"])
        comment_body = "Detailed check comment."

        response = add_issue_comment(
            owner="owner_user", repo="repo1", issue_number=1, body=comment_body
        )

        self.assertIn("id", response)
        self.assertIsInstance(response["id"], int)
        self.assertIn("node_id", response)
        self.assertIsInstance(response["node_id"], str)
        self.assertIn("user", response)
        self.assertIsInstance(response["user"], dict)
        self.assertEqual(response["user"]["login"], self.owner_user["login"])
        self.assertEqual(response["user"]["id"], self.owner_user["id"])
        UserSimple.model_validate(response["user"]) # Validate nested user
        self.assertIn("created_at", response)
        self.assertIsInstance(response["created_at"], str)
        datetime.fromisoformat(response["created_at"].replace("Z", "+00:00")) # Check ISO format
        self.assertIn("updated_at", response)
        self.assertIsInstance(response["updated_at"], str)
        datetime.fromisoformat(response["updated_at"].replace("Z", "+00:00"))
        self.assertEqual(response["created_at"], response["updated_at"]) # For new comment
        self.assertIn("author_association", response)
        self.assertEqual(response["author_association"], "OWNER")
        self.assertIn("body", response)
        self.assertEqual(response["body"], comment_body)

        AddIssueCommentResponse.model_validate(response) # Full validation

    def test_add_comment_multiple_comments_to_same_issue(self):
        self._set_current_user(self.owner_user["id"], self.owner_user["login"])

        add_issue_comment(owner="owner_user", repo="repo1", issue_number=2, body="First comment")
        add_issue_comment(owner="owner_user", repo="repo1", issue_number=2, body="Second comment")

        self.assertEqual(len(self.DB["IssueComments"]), 2)
        comments_for_issue2 = [c for c in self.DB["IssueComments"] if c["issue_id"] == self.issue2_repo1["id"]]
        self.assertEqual(len(comments_for_issue2), 2)
        self.assertNotEqual(comments_for_issue2[0]["id"], comments_for_issue2[1]["id"])

        updated_issue2 = next(i for i in self.DB["Issues"] if i["id"] == self.issue2_repo1["id"])
        self.assertEqual(updated_issue2["comments"], 2)

    def test_add_comment_repo_not_found_owner_mismatch(self):
        self.assert_error_behavior(func_to_call=add_issue_comment, expected_exception_type=NotFoundError, expected_message="Repository 'nonexistent_owner/repo1' not found.", owner="nonexistent_owner", repo="repo1", issue_number=1, body="Test body")

    def test_add_comment_repo_not_found_name_mismatch(self):
        self.assert_error_behavior(func_to_call=add_issue_comment, expected_exception_type=NotFoundError, expected_message="Repository 'owner_user/nonexistent_repo' not found.", owner="owner_user", repo="nonexistent_repo", issue_number=1, body="Test body")

    def test_add_comment_issue_not_found(self):
        self.assert_error_behavior(func_to_call=add_issue_comment, expected_exception_type=NotFoundError, expected_message="Issue #999 not found in repository 'owner_user/repo1'.", owner="owner_user", repo="repo1", issue_number=999, body="Test body")

    def test_add_comment_body_missing_none(self):
        self.assert_error_behavior(func_to_call=add_issue_comment, expected_exception_type=ValidationError, expected_message="Comment body cannot be empty or consist only of whitespace.", owner="owner_user", repo="repo1", issue_number=1, body=None)

    def test_add_comment_body_empty_string(self):
        self.assert_error_behavior(func_to_call=add_issue_comment, expected_exception_type=ValidationError, expected_message="Comment body cannot be empty or consist only of whitespace.", owner="owner_user", repo="repo1", issue_number=1, body="")

    def test_add_comment_body_whitespace_string(self):
        # Assuming whitespace-only body is also considered invalid/empty
        self.assert_error_behavior(func_to_call=add_issue_comment, expected_exception_type=ValidationError, expected_message="Comment body cannot be empty or consist only of whitespace.", owner="owner_user", repo="repo1", issue_number=1, body="   ")

    def test_add_comment_forbidden_issues_disabled(self):
        self._set_current_user(self.owner_user["id"], self.owner_user["login"]) # Owner should still be blocked
        # Create an issue in repo2 for this test
        issue_in_repo2 = {
            "id": 2001, "node_id": "I_2001", "repository_id": self.repo2_issues_disabled["id"], "number": 1,
            "title": "Issue in repo with disabled issues", "user": {"id": 1, "login": "owner_user"},
            "state": "open", "comments": 0, "created_at": self.fixed_time, "updated_at": self.fixed_time,
            "author_association": "OWNER"
        }
        self.DB["Issues"].append(issue_in_repo2)
        self.assert_error_behavior(func_to_call=add_issue_comment, expected_exception_type=ForbiddenError, expected_message="Issues are disabled for repository 'owner_user/repo2'.", owner="owner_user", repo="repo2", issue_number=1, body="Test body")

    def test_add_comment_forbidden_private_repo_no_permission(self):
        self._set_current_user(self.other_user["id"], self.other_user["login"]) # other_user has no access to repo3_private
        # Create an issue in repo3 for this test
        issue_in_repo3 = {
            "id": 3001, "node_id": "I_3001", "repository_id": self.repo3_private["id"], "number": 1,
            "title": "Issue in private repo", "user": {"id": 1, "login": "owner_user"},
            "state": "open", "comments": 0, "created_at": self.fixed_time, "updated_at": self.fixed_time,
            "author_association": "OWNER"
        }
        self.DB["Issues"].append(issue_in_repo3)
        self.assert_error_behavior(func_to_call=add_issue_comment, expected_exception_type=ForbiddenError, expected_message="User does not have permission to access repository 'owner_user/private_repo'.", owner="owner_user", repo="private_repo", issue_number=1, body="Test body")

    def test_add_comment_forbidden_private_repo_read_permission_only(self):
        # collaborator_user has 'read' on repo3_private
        self._set_current_user(self.collaborator_user["id"], self.collaborator_user["login"])
        issue_in_repo3 = {
            "id": 3001, "node_id": "I_3001", "repository_id": self.repo3_private["id"], "number": 1,
            "title": "Issue in private repo", "user": {"id": 1, "login": "owner_user"},
            "state": "open", "comments": 0, "created_at": self.fixed_time, "updated_at": self.fixed_time,
            "author_association": "OWNER"
        }
        self.DB["Issues"].append(issue_in_repo3)
        self.assert_error_behavior(func_to_call=add_issue_comment, expected_exception_type=ForbiddenError, expected_message="You do not have permission to comment on this issue.", owner="owner_user", repo="private_repo", issue_number=1, body="Test body")

    def test_add_comment_timestamps_are_recent(self):
        self._set_current_user(self.owner_user["id"], self.owner_user["login"])
        comment_body = "Timestamp test comment."

        # Ensure current time is after fixed_time used in setUp
        time_before_call = datetime.now(timezone.utc)

        response = add_issue_comment(
            owner="owner_user", repo="repo1", issue_number=1, body=comment_body
        )
        time_after_call = datetime.now(timezone.utc)

        created_at_dt = datetime.fromisoformat(response["created_at"].replace("Z", "+00:00"))
        updated_at_dt = datetime.fromisoformat(response["updated_at"].replace("Z", "+00:00"))

        # Allow a small delta for execution time
        self.assertTrue(time_before_call <= created_at_dt <= time_after_call)
        self.assertTrue(time_before_call <= updated_at_dt <= time_after_call)
        self.assertEqual(created_at_dt, updated_at_dt)

        db_comment = self.DB["IssueComments"][0]
        db_created_at_dt = datetime.fromisoformat(db_comment["created_at"].replace("Z", "+00:00"))
        db_updated_at_dt = datetime.fromisoformat(db_comment["updated_at"].replace("Z", "+00:00"))
        self.assertEqual(created_at_dt, db_created_at_dt)
        self.assertEqual(updated_at_dt, db_updated_at_dt)

    def test_add_comment_issue_number_zero_or_negative_leads_to_notfound(self):
        self.assert_error_behavior(func_to_call=add_issue_comment, expected_exception_type=ValidationError, expected_message="Issue number must be a positive integer.", owner="owner_user", repo="repo1", issue_number=0, body="Test body")
        self.assert_error_behavior(func_to_call=add_issue_comment, expected_exception_type=ValidationError, expected_message="Issue number must be a positive integer.", owner="owner_user", repo="repo1", issue_number=-1, body="Test body")

    def test_add_comment_to_locked_issue_by_owner_success(self):
        self._set_current_user(self.owner_user["id"], self.owner_user["login"])
        comment_body = "Owner comment on locked issue."
        response = add_issue_comment(
            owner="owner_user", repo="repo1", issue_number=self.issue3_repo1_locked["number"], body=comment_body
        )
        self.assertEqual(response["body"], comment_body)
        self.assertEqual(response["user"]["login"], self.owner_user["login"])
        self.assertEqual(response["author_association"], "OWNER")
        AddIssueCommentResponse.model_validate(response)
        self.assertEqual(len(self.DB["IssueComments"]), 1)
        self.assertEqual(self.DB["IssueComments"][0]["issue_id"], self.issue3_repo1_locked["id"])

    def test_add_comment_to_locked_issue_by_collaborator_success(self):
        self._set_current_user(self.collaborator_user["id"], self.collaborator_user["login"])
        comment_body = "Collaborator comment on locked issue."
        response = add_issue_comment(
            owner="owner_user", repo="repo1", issue_number=self.issue3_repo1_locked["number"], body=comment_body
        )
        self.assertEqual(response["body"], comment_body)
        self.assertEqual(response["user"]["login"], self.collaborator_user["login"])
        self.assertEqual(response["author_association"], "MEMBER")
        AddIssueCommentResponse.model_validate(response)
        self.assertEqual(len(self.DB["IssueComments"]), 1)

    def test_add_comment_to_locked_issue_by_other_user_forbidden(self):
        self._set_current_user(self.other_user["id"], self.other_user["login"])
        self.assert_error_behavior(func_to_call=add_issue_comment, expected_exception_type=ForbiddenError, expected_message="Issue is locked and you do not have permission to comment.", owner="owner_user", repo="repo1", issue_number=self.issue3_repo1_locked["number"], body="Other user trying to comment on locked")

    def test_add_comment_to_locked_issue_by_issue_author_contributor_forbidden(self):
        # Set current user to the author of issue4, but try to comment on issue3 (locked)
        # where issue_author_user is NOT owner or member.
        # First, make issue4_repo1_by_issue_author locked for a stronger test case for this user.
        self.issue4_repo1_by_issue_author["locked"] = True # Lock the issue authored by issue_author_user
        sim_utils._update_raw_item_in_table(self.DB, "Issues", self.issue4_repo1_by_issue_author["id"], {"locked": True}, id_field="id")


        self._set_current_user(self.issue_author_user["id"], self.issue_author_user["login"])
        self.assert_error_behavior(func_to_call=add_issue_comment, expected_exception_type=ForbiddenError, expected_message="Issue is locked and you do not have permission to comment.", owner="owner_user", repo="repo1", issue_number=self.issue4_repo1_by_issue_author["number"], body="Issue author (contributor) trying to comment on their own locked issue"
        )
        # Reset lock status for other tests if necessary, or ensure test isolation
        self.issue4_repo1_by_issue_author["locked"] = False 
        sim_utils._update_raw_item_in_table(self.DB, "Issues", self.issue4_repo1_by_issue_author["id"], {"locked": False}, id_field="id")


    # --- Test for "CONTRIBUTOR" author_association ---
    def test_add_comment_by_issue_author_is_contributor_success(self):
        self._set_current_user(self.issue_author_user["id"], self.issue_author_user["login"])
        comment_body = "Comment by the issue author (contributor)."
        # issue4_repo1_by_issue_author is authored by issue_author_user, and it's not locked.
        response = add_issue_comment(
            owner="owner_user", repo="repo1", issue_number=self.issue4_repo1_by_issue_author["number"], body=comment_body
        )
        self.assertEqual(response["body"], comment_body)
        self.assertEqual(response["user"]["login"], self.issue_author_user["login"])
        self.assertEqual(response["author_association"], "CONTRIBUTOR")
        AddIssueCommentResponse.model_validate(response)
        self.assertEqual(len(self.DB["IssueComments"]), 1)
        db_comment = self.DB["IssueComments"][0]
        self.assertEqual(db_comment["author_association"], "CONTRIBUTOR")
        self.assertEqual(db_comment["issue_id"], self.issue4_repo1_by_issue_author["id"])

    # --- Test for Invalid Current User Context ---
    def test_add_comment_invalid_current_user_context_none(self):
        self.DB["CurrentUser"] = None # Simulate no user context
        self.assert_error_behavior(func_to_call=add_issue_comment, expected_exception_type=ForbiddenError, expected_message="Invalid current user context.", owner="owner_user", repo="repo1", issue_number=1, body="Test body")

    def test_add_comment_invalid_current_user_context_empty_dict(self):
        self.DB["CurrentUser"] = {} # Simulate malformed user context
        self.assert_error_behavior(func_to_call=add_issue_comment, expected_exception_type=ForbiddenError, expected_message="Invalid current user context.", owner="owner_user", repo="repo1", issue_number=1, body="Test body")

    def test_add_comment_invalid_current_user_context_missing_id(self):
        self.DB["CurrentUser"] = {"login": "some_user"} # ID is missing
        self.assert_error_behavior(func_to_call=add_issue_comment, expected_exception_type=ForbiddenError, expected_message="Invalid current user context.", owner="owner_user", repo="repo1", issue_number=1, body="Test body")


if __name__ == '__main__':
    main()
