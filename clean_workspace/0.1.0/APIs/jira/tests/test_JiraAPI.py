import copy
import uuid
import os
import unittest
from unittest.mock import patch
import tempfile
from pydantic import ValidationError

import jira as JiraAPI
from .. import DB
from ..SimulationEngine.db import save_state, load_state

from common_utils.base_case import BaseTestCaseWithErrorHandler
from ..SimulationEngine.custom_errors import EmptyFieldError, MissingRequiredFieldError, UserNotFoundError

from .. import (
    create_user,
    get_project_by_key,
    update_component_by_id,
    assign_issue_to_user,
    get_issue_by_id,
    update_issue_by_id,
    create_project,
    search_issues_for_picker,
    get_component_by_id,
    get_user_by_username_or_account_id,
    get_project_components_by_key,
    create_project_component,
    create_group,
    get_group_by_name,
    delete_group_by_name,
    create_issue_type,
    find_users,
    add_attachment
)

from ..SimulationEngine.custom_errors import EmptyFieldError
from ..SimulationEngine.custom_errors import GroupAlreadyExistsError
from ..SimulationEngine.custom_errors import ProjectInputError
from ..SimulationEngine.custom_errors import ProjectAlreadyExistsError
from ..SimulationEngine.custom_errors import MissingUserIdentifierError
from ..SimulationEngine.custom_errors import ProjectNotFoundError
from ..SimulationEngine.custom_errors import MissingUpdateDataError
from ..SimulationEngine.custom_errors import EmptyInputError
from ..SimulationEngine.custom_errors import ProjectNotFoundError
from ..SimulationEngine.custom_errors import ComponentNotFoundError
from ..SimulationEngine.custom_errors import IssueTypeNotFoundError
from ..SimulationEngine.custom_errors import ResolutionNotFoundError
from ..SimulationEngine.custom_errors import PriorityNotFoundError

class TestMockJiraPyApi(BaseTestCaseWithErrorHandler):
    def setUp(self):
        # Reset the global DB state before each test
        DB.clear()
        DB.update(
            {
                "auth_sessions": {},
                "reindex_info": {"running": False, "type": None},
                "application_properties": {},
                "application_roles": {},
                "avatars": [],
                "components": {},
                "dashboards": {},
                "filters": {},
                "groups": {},
                "issues": {
                    "existing_issue_1": {
                        "id": "existing_issue_1",
                        "fields": {
                            "project": "PROJ",
                            "summary": "An existing issue",
                            "description": "Details here.",
                            "priority": "Medium",
                            "assignee": {"name": "old_user"},
                            "issuetype": "Task"
                        }
                    },
                    "existing_issue_2": {
                        "id": "ISSUE-2",
                        "fields": {
                            "summary": "UI glitch",
                            "description": "Alignment issue on dashboard",
                            "priority": "Low",
                            "project": "TRYDEMO",
                            "issuetype": "Bug",
                            "status": "Open",
                            "created": "2025-01-02T09:30:00"
                        }
                    },
                    "ISSUE-1": {"fields": {"summary": "Issue without subtasks"}},
                    "ISSUE-2": {
                                "fields": {
                                    "summary": "Issue with subtasks",
                                    "sub-tasks": [{"id": "SUB-1"}, {"id": "SUB-2"}]
                                }
                            },
                    "SUB-1": {"fields": {"summary": "Subtask 1 of ISSUE-2"}},
                    "SUB-2": {"fields": {"summary": "Subtask 2 of ISSUE-2"}},
                    "ISSUE-3": {"fields": {"summary": "Another issue"}},
                },
                "issue_links": [],
                "issue_link_types": {},
                "issue_types": {},
                "jql_autocomplete_data": {},
                "licenses": {},
                "my_permissions": {},
                "my_preferences": {},
                "permissions": {
                    "CREATE_ISSUE": {
                        "id": "1",
                        "key": "CREATE_ISSUE",
                        "name": "Create Issues",
                        "description": "Ability to create issues.",
                        "havePermission": True
                    },
                    "EDIT_ISSUE": {
                        "id": "2",
                        "key": "EDIT_ISSUE",
                        "name": "Edit Issues",
                        "description": "Ability to edit issues.",
                        "havePermission": True
                    },
                    "DELETE_ISSUE": {
                        "id": "3",
                        "key": "DELETE_ISSUE",
                        "name": "Delete Issues",
                        "description": "Ability to delete issues.",
                        "havePermission": True
                    },
                    "ASSIGN_ISSUE": {
                        "id": "4",
                        "key": "ASSIGN_ISSUE",
                        "name": "Assign Issues",
                        "description": "Ability to assign issues.",
                        "havePermission": True
                    },
                    "CLOSE_ISSUE": {
                        "id": "5",
                        "key": "CLOSE_ISSUE",
                        "name": "Close Issues",
                        "description": "Ability to close issues.",
                        "havePermission": True
                    }
                },
                "permission_schemes": {},
                "priorities": {},
                "projects": {"TRYDEMO": {
                    "key": "TRYDEMO",
                    "name": "Demo Project",
                    "lead": "jdoe"
                }},
                "project_categories": {},
                "resolutions": {},
                "roles": {},
                "webhooks": {},
                "workflows": {},
                "security_levels": {},
                "statuses": {},
                "status_categories": {},
                "users": {},
                "versions": {},
                "attachments": {
                    
            }
            }
        )

    # ------------------------------------------------------------------------
    # Existing Tests
    # ------------------------------------------------------------------------
    def test_issue_lifecycle(self):
        # Create an issue with minimal required fields
        issue_fields = {
            "project": "TEST",
            "summary": "test",
            "description": "Test issue",
            "issuetype": "Task",
            "priority": "Medium",
            "assignee": {"name": "testuser"}
        }
        
        # Create an issue
        created = JiraAPI.IssueApi.create_issue(fields=issue_fields)
        self.assertIn("id", created)
        issue_id = created["id"]

        # Test creating with empty fields raises EmptyFieldError
        with self.assertRaises(EmptyFieldError):
            JiraAPI.IssueApi.create_issue(fields={})

        # Test creating with missing required fields raises MissingRequiredFieldError
        with self.assertRaises(MissingRequiredFieldError):
            JiraAPI.IssueApi.create_issue(fields={"project": "TEST"})

        # Retrieve it
        fetched = JiraAPI.IssueApi.get_issue(issue_id)
        self.assertIn("fields", fetched)
        self.assertEqual(fetched["fields"]["summary"], "test")

        # Update
        updated = JiraAPI.IssueApi.update_issue(
            issue_id, fields={"summary": "updated!"}
        )
        self.assertTrue(updated["updated"])
        fetched = JiraAPI.IssueApi.get_issue(issue_id)
        self.assertEqual(fetched["fields"]["summary"], "updated!")

        # Test updating with invalid ID
        with self.assertRaisesRegex(ValueError, "Issue 'invalid_id' not found."):
            JiraAPI.IssueApi.update_issue("invalid_id", fields={})

        # Assign
        assigned = JiraAPI.IssueApi.assign_issue(issue_id, assignee={"name": "alice"})
        self.assertTrue(assigned["assigned"])
        fetched = JiraAPI.IssueApi.get_issue(issue_id)
        self.assertEqual(fetched["fields"]["assignee"], {"name": "alice"})

        with self.assertRaisesRegex(ValueError, "Issue 'invalid_id' not found."):
            JiraAPI.IssueApi.assign_issue("invalid_id", assignee={"name": "alice"})

        # Delete
        deleted = JiraAPI.IssueApi.delete_issue(issue_id)
        self.assertEqual(deleted["deleted"], issue_id)
        self.assertFalse(deleted["deleteSubtasks"])
        
        with self.assertRaisesRegex(ValueError, f"Issue '{issue_id}' not found."):
            JiraAPI.IssueApi.get_issue(issue_id)

        with self.assertRaises(ValueError) as cm:
            JiraAPI.IssueApi.delete_issue("invalid_id")

        self.assertEqual("Issue with id 'invalid_id' does not exist.", str(cm.exception))

    def test_issue_lifecycle_with_attachments(self):
        # Create an issue with attachments
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write("This is a test file content.")
            temp_file_path = temp_file.name
        issue_fields = {
            "project": "TEST",
            "summary": "test",
            "description": "Test issue",
            "issuetype": "Task",
            "priority": "Medium",
            "status": "Open",
            "assignee": {"name": "testuser"},
        }
        
        # Create an issue
        created = JiraAPI.IssueApi.create_issue(fields=issue_fields)
        issue_id = created["id"]
        add_attachment(issue_id, temp_file_path)

        attachments = JiraAPI.IssueApi.get_issue(issue_id)["fields"]["attachments"]

        self.assertIn(issue_id, DB["issues"])
        for attachment in attachments:
            self.assertIn(str(attachment["id"]), DB["attachments"])

    def test_delete_issue_with_subtasks(self):
        # Create a parent issue with all required fields
        parent_fields = {
            "project": "TEST",
            "summary": "Parent Issue",
            "description": "Parent description",
            "issuetype": "Task",
            "priority": "Medium",
            "assignee": {"name": "testuser"}
        }
        
        # Create a parent issue
        parent_issue = JiraAPI.IssueApi.create_issue(fields=parent_fields)
        parent_id = parent_issue["id"]

        # Create a subtask with all required fields
        subtask_fields = {
            "project": "TEST",
            "summary": "Subtask",
            "description": "Subtask description",
            "issuetype": "Subtask",
            "priority": "Medium",
            "assignee": {"name": "testuser"},
            "parent": {"id": parent_id}
        }
        
        # Create a subtask
        subtask = JiraAPI.IssueApi.create_issue(fields=subtask_fields)
        # Change the logic when creating subtasks is added to create_issue
        DB["issues"][parent_id]["fields"]["sub-tasks"] = [subtask]

        with self.assertRaisesRegex(ValueError, "Subtasks exist, cannot delete issue. Set delete_subtasks=True to delete them."):
            JiraAPI.IssueApi.delete_issue(parent_id)

        # Delete the parent issue
        deleted = JiraAPI.IssueApi.delete_issue(parent_id, delete_subtasks=True)
        self.assertEqual(deleted["deleted"], parent_id)
        self.assertTrue(deleted["deleteSubtasks"])

        with self.assertRaisesRegex(ValueError, f"Issue '{parent_id}' not found."):
            JiraAPI.IssueApi.get_issue(parent_id)

    def test_persistence(self):
        """Test saving and loading application state."""
        # Add an issue with all required fields
        issue_fields = {
            "project": "TEST",
            "summary": "test",
            "description": "Test issue",
            "issuetype": "Task",
            "priority": "Medium",
            "assignee": {"name": "testuser"}
        }
        
        # Create an issue
        created = JiraAPI.IssueApi.create_issue(fields=issue_fields)
        c_id = created["id"]
        # Save the state
        save_state("test_jira_state.json")

        fetched = JiraAPI.IssueApi.get_issue(issue_id=c_id)
        self.assertEqual(fetched["fields"]["summary"], "test")

        # Delete the issue
        JiraAPI.IssueApi.delete_issue(issue_id=c_id)
        # Load the state
        load_state("test_jira_state.json")
        # Verify the issue is still there
        fetched = JiraAPI.IssueApi.get_issue(issue_id=c_id)
        self.assertEqual(fetched["fields"]["summary"], "test")

        # Cleanup file
        if os.path.exists("test_jira_state.json"):
            os.remove("test_jira_state.json")

    def test_group_creation(self):
        create_resp = JiraAPI.GroupApi.create_group(name="developers")
        self.assertIn("created", create_resp)
        self.assertTrue(create_resp["created"])
        group_info = JiraAPI.GroupApi.get_group(groupname="developers")
        self.assertIn("group", group_info)
        self.assertEqual(group_info["group"]["name"], "developers")
    def test_valid_input_creates_group(self):
        """Test that a group is successfully created with a valid name."""
        group_name = "TestGroup"
        
        # Call the function using the alias
        result = create_group(name=group_name)
        
        self.assertIsInstance(result, dict)
        self.assertTrue(result.get("created"))
        self.assertIn("group", result)
        
        group_data = result["group"]
        self.assertIsInstance(group_data, dict)
        self.assertEqual(group_data.get("name"), group_name)
        self.assertEqual(group_data.get("users"), [])
        
        # Verify DB state
        self.assertIn(group_name, DB["groups"])
        self.assertEqual(DB["groups"][group_name]["name"], group_name)
        self.assertEqual(DB["groups"][group_name]["users"], [])

    def test_invalid_name_type_raises_type_error(self):
        """Test that providing a non-string name raises TypeError."""
        invalid_name = 123
        self.assert_error_behavior(
            func_to_call=create_group,
            expected_exception_type=TypeError,
            expected_message="Argument 'name' must be a string.",
            name=invalid_name
        )
        self.assertEqual(DB["groups"], {}, "DB should not be modified on validation error.")

    def test_empty_name_raises_value_error(self):
        """Test that providing an empty string for name raises ValueError."""
        self.assert_error_behavior(
            func_to_call=create_group,
            expected_exception_type=ValueError,
            expected_message="Argument 'name' cannot be empty or consist only of whitespace.",
            name=""
        )
        self.assertEqual(DB["groups"], {}, "DB should not be modified on validation error.")

    def test_whitespace_name_raises_value_error(self):
        """Test that providing a name with only whitespace raises ValueError."""
        self.assert_error_behavior(
            func_to_call=create_group,
            expected_exception_type=ValueError,
            expected_message="Argument 'name' cannot be empty or consist only of whitespace.",
            name="   "
        )
        self.assertEqual(DB["groups"], {}, "DB should not be modified on validation error.")

    def test_existing_group_name_raises_group_already_exists_error(self):
        """Test that creating a group with an existing name raises GroupAlreadyExistsError."""
        group_name = "ExistingGroup"
        # Pre-populate DB for this test case
        DB["groups"][group_name] = {"name": group_name, "users": ["user1"]} 
        
        self.assert_error_behavior(
            func_to_call=create_group,
            expected_exception_type=GroupAlreadyExistsError,
            expected_message=f"Group '{group_name}' already exists.",
            name=group_name
        )
        # Ensure DB state was not altered further by the failed call
        self.assertEqual(DB["groups"][group_name]["users"], ["user1"])


    def test_group_creation_is_persistent_in_db(self):
        """Test that successful group creation correctly updates the DB and persists."""
        group_name1 = "FirstGroup"
        create_group(name=group_name1)
        self.assertIn(group_name1, DB["groups"])
        self.assertEqual(DB["groups"][group_name1]["name"], group_name1)
        
        group_name2 = "SecondGroup"
        create_group(name=group_name2)
        self.assertIn(group_name2, DB["groups"])
        self.assertEqual(DB["groups"][group_name2]["name"], group_name2)
        
        # Ensure first group is still there and DB contains both
        self.assertIn(group_name1, DB["groups"]) 
        self.assertEqual(len(DB["groups"]), 2)

    def test_docstring_example_output_structure(self):
        """Test that the successful output matches the structure described in the docstring."""
        group_name = "DocstringGroup"
        result = create_group(name=group_name)

        self.assertTrue(result['created'])
        self.assertIsInstance(result['group'], dict)
        self.assertEqual(result['group']['name'], group_name)
        self.assertIsInstance(result['group']['users'], list)
        self.assertEqual(len(result['group']['users']), 0)

    def test_webhooks(self):
        # Create
        creation = JiraAPI.WebhookApi.create_or_get_webhooks(
            webhooks=[{"url": "http://test", "events": []}]
        )
        self.assertTrue(creation["registered"])

        self.assertIn("error", JiraAPI.WebhookApi.create_or_get_webhooks(webhooks=[]))
        # Then get
        got = JiraAPI.WebhookApi.get_webhooks()
        self.assertEqual(len(got["webhooks"]), 1)
        # Then delete
        wh_ids = creation["webhookIds"]
        deleted = JiraAPI.WebhookApi.delete_webhooks(webhookIds=wh_ids)
        self.assertEqual(deleted["deleted"], wh_ids)

        self.assertIn("error", JiraAPI.WebhookApi.delete_webhooks(webhookIds=[]))
        # Verify deleted
        got = JiraAPI.WebhookApi.get_webhooks()
        self.assertEqual(len(got["webhooks"]), 0)

    def test_component_creation(self):
        """Ensure components can be created and retrieved."""
        project = JiraAPI.ProjectApi.create_project(
            proj_key="PROJ", proj_name="Project"
        )
        created = JiraAPI.ComponentApi.create_component(project="PROJ", name="Backend")
        self.assertIn("id", created)
        comp_id = created["id"]
        # Retrieve and check
        fetched = JiraAPI.ComponentApi.get_component(comp_id)
        self.assertNotIn("error", fetched)
        self.assertEqual(fetched["name"], "Backend", "Component name should match.")

    def test_component_creation_invalid_project(self):
        """Test component creation with an invalid project."""
        
        self.assert_error_behavior(
            func_to_call=JiraAPI.ComponentApi.create_component,
            expected_exception_type=ProjectNotFoundError,
            expected_message="Project 'nonexistent' not found.",
            project="nonexistent",
            name="Backend"
        )
    def test_component_creation_invalid_project_name_description_length(self):
        """Test that a ValueError is raised when project parameter is not a string."""
        # Create a project first
        JiraAPI.ProjectApi.create_project(proj_key="PROJ", proj_name="Project")

        # Test name length limit
        with self.assertRaises(ValueError) as context:
            JiraAPI.ComponentApi.create_component(project="PROJ", name="a" * 256)
        self.assertEqual(str(context.exception), "name cannot be longer than 255 characters")

        # Test description length limit
        with self.assertRaises(ValueError) as context:
            JiraAPI.ComponentApi.create_component(project="PROJ", name="Backend", description="a" * 1001)
        self.assertEqual(str(context.exception), "description cannot be longer than 1000 characters")

    
    def test_reindex_lifecycle(self):
        """Check that reindex can be started and then we can query its status."""
        # Initially should not be running
        status_before = JiraAPI.ReindexApi.get_reindex_status()
        self.assertFalse(
            status_before["running"], "Reindex should not be running initially."
        )
        # Start reindex
        start_result = JiraAPI.ReindexApi.start_reindex(reindex_type="BACKGROUND")
        self.assertTrue(start_result["started"])
        # Check status again
        status_after = JiraAPI.ReindexApi.get_reindex_status()
        self.assertTrue(
            status_after["running"], "Reindex should be running after start."
        )
        self.assertEqual(status_after["type"], "BACKGROUND")


    def test_valid_deletion(self):
        """Test successful deletion of an existing group."""
        global DB
        DB["groups"]["admins"] = {"description": "Administrator group"}
        
        result = delete_group_by_name(groupname="admins")
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result, {"deleted": "admins"})
        self.assertNotIn("admins", DB["groups"])

    def test_invalid_groupname_type_integer(self):
        """Test that providing an integer for groupname raises TypeError."""
        self.assert_error_behavior(
            func_to_call=delete_group_by_name,
            expected_exception_type=TypeError,
            expected_message="groupname must be a string.",
            groupname=123
        )

    def test_invalid_groupname_type_none(self):
        """Test that providing None for groupname raises TypeError."""
        self.assert_error_behavior(
            func_to_call=delete_group_by_name,
            expected_exception_type=TypeError,
            expected_message="groupname must be a string.",
            groupname=None
        )

    def test_empty_groupname_string(self):
        """Test that providing an empty string for groupname raises ValueError."""
        self.assert_error_behavior(
            func_to_call=delete_group_by_name,
            expected_exception_type=ValueError,
            expected_message="groupname cannot be empty.",
            groupname=""
        )

    def test_group_not_exists(self):
        """Test that attempting to delete a non-existent group raises ValueError."""
        global DB
        DB["groups"]["existing_group"] = {} # Ensure 'groups' key exists and is a dict
        
        self.assert_error_behavior(
            func_to_call=delete_group_by_name,
            expected_exception_type=ValueError,
            expected_message="Group 'non_existent_group' does not exist.", # Message should be exact
            groupname="non_existent_group"
        )

    def test_group_name_with_special_chars_not_exists(self):
        """Test deleting a non-existent group with special characters in its name."""
        group_name_with_special_chars = "group-with-hyphen.and.dot"
        self.assert_error_behavior(
            func_to_call=delete_group_by_name,
            expected_exception_type=ValueError,
            expected_message=f"Group '{group_name_with_special_chars}' does not exist.",
            groupname=group_name_with_special_chars
        )

    def test_successful_deletion_from_populated_db(self):
        """Test successful deletion when other groups exist."""
        global DB
        DB["groups"]["group1"] = {}
        DB["groups"]["group_to_delete"] = {}
        DB["groups"]["group3"] = {}
        
        result = delete_group_by_name(groupname="group_to_delete")
        
        self.assertEqual(result, {"deleted": "group_to_delete"})
        self.assertNotIn("group_to_delete", DB["groups"])
        self.assertIn("group1", DB["groups"]) # Ensure other groups are unaffected
        self.assertIn("group3", DB["groups"])
        self.assertEqual(len(DB["groups"]), 2)

    # ------------------------------------------------------------------------
    # Additional Tests for Complete Coverage
    # ------------------------------------------------------------------------
    def test_application_properties_get(self):
        """Test getting application properties."""
        # Add a property
        DB["application_properties"]["testProp"] = "value"
        JiraAPI.ApplicationPropertiesApi.update_application_property(
            id="testProp", value="testValue"
        )
        # Get all
        all_props = JiraAPI.ApplicationPropertiesApi.get_application_properties()
        self.assertIn("properties", all_props)
        self.assertIn("testProp", all_props["properties"])
        # Get specific
        single_prop = JiraAPI.ApplicationPropertiesApi.get_application_properties(
            key="testProp"
        )
        self.assertIn("key", single_prop)
        self.assertEqual(single_prop["key"], "testProp")
        self.assertEqual(single_prop["value"], "testValue")

    def test_application_properties_update_invalid_id(self):
        """Test updating application properties with an invalid id."""
        JiraAPI.ApplicationPropertiesApi.update_application_property(
            id="nonexistent", value="testValue"
        )
        JiraAPI.ApplicationPropertiesApi.update_application_property(
            id="testProp", value=""
        )

    def test_application_properties_get_invalid_key(self):
        """Test getting application properties with an invalid key."""
        self.assertIn(
            "error",
            JiraAPI.ApplicationPropertiesApi.get_application_properties(
                key="nonexistent"
            ),
        )

    def test_application_roles(self):
        """Test application role retrieval."""
        DB["application_roles"] = {"admin": {"key": "admin", "name": "System Admins"}}

        # Get all roles
        all_roles = JiraAPI.ApplicationRoleApi.get_application_roles()
        self.assertIn("roles", all_roles)
        self.assertEqual(len(all_roles["roles"]), 1)
        self.assertEqual(all_roles["roles"][0]["name"], "System Admins")

        # Get role by key
        single_role = JiraAPI.ApplicationRoleApi.get_application_role_by_key("admin")
        self.assertEqual(single_role["name"], "System Admins")

        # Test non-existent role
        self.assertIn(
            "error",
            JiraAPI.ApplicationRoleApi.get_application_role_by_key("nonexistent"),
        )

    def test_avatar_api(self):
        """Test avatar uploads and cropping."""
        # Upload normal avatar
        up_normal = JiraAPI.AvatarApi.upload_avatar(
            filetype="project", filename="proj.png"
        )
        self.assertTrue(up_normal["uploaded"])
        self.assertIn("avatar", up_normal)
        # Upload temporary
        up_temp = JiraAPI.AvatarApi.upload_temporary_avatar(
            filetype="user", filename="user.png"
        )
        self.assertTrue(up_temp["uploaded"])
        self.assertTrue(up_temp["avatar"]["temporary"])
        # Crop temporary
        crop_res = JiraAPI.AvatarApi.crop_temporary_avatar(
            cropDimensions={"x": 0, "y": 0, "width": 100, "height": 100}
        )
        self.assertTrue(crop_res["cropped"])

    def test_avatar_api_empty_fields(self):
        """Test avatar uploads with empty fields."""
        self.assertIn(
            "error", JiraAPI.AvatarApi.upload_avatar(filetype="", filename="")
        )
        self.assertIn(
            "error", JiraAPI.AvatarApi.upload_temporary_avatar(filetype="", filename="")
        )
        self.assertIn(
            "error", JiraAPI.AvatarApi.crop_temporary_avatar(cropDimensions={})
        )

    def test_component_update_delete(self):
        """Test updating and deleting a component."""
        project = JiraAPI.ProjectApi.create_project(
            proj_key="TEST", proj_name="TEST Project"
        )
        created = JiraAPI.ComponentApi.create_component(project="TEST", name="Comp1")
        comp_id = created["id"]

        # Update
        update_resp = JiraAPI.ComponentApi.update_component(
            comp_id, name="UpdatedComp", description="Updated Description"
        )
        self.assertTrue(update_resp["updated"])
        fetched = JiraAPI.ComponentApi.get_component(comp_id)
        self.assertEqual(fetched["name"], "UpdatedComp")
        self.assertEqual(fetched["description"], "Updated Description")
        # Delete
        del_resp = JiraAPI.ComponentApi.delete_component(comp_id)
        self.assertIn("deleted", del_resp)
        with self.assertRaises(ValueError) as context:
            JiraAPI.ComponentApi.get_component(comp_id)
        self.assertEqual(str(context.exception), f"Component '{comp_id}' not found.")

    def test_component_update_delete_invalid_id(self):
        """Test updating and deleting a component with an invalid id."""
        self.assert_error_behavior(
            func_to_call=JiraAPI.ComponentApi.update_component,
            expected_exception_type=ComponentNotFoundError,
            expected_message="Component 'nonexistentialcomp' not found.",
            comp_id="nonexistentialcomp",
            description="Updated Description"
        )
        self.assertIn(
            "error", JiraAPI.ComponentApi.delete_component(comp_id="nonexistent")
        )

    def test_dashboard_api(self):
        """Test getting dashboards."""
        # Add dashboard data to DB
        DB["dashboards"]["D1"] = {"id": "D1", "name": "Main Dashboard"}

        # Get all dashboards
        all_dash = JiraAPI.DashboardApi.get_dashboards()
        self.assertIn("dashboards", all_dash)
        self.assertEqual(len(all_dash["dashboards"]), 1)
        self.assertEqual(all_dash["dashboards"][0]["name"], "Main Dashboard")

        # Get one dashboard
        one_dash = JiraAPI.DashboardApi.get_dashboard("D1")
        self.assertEqual(one_dash["name"], "Main Dashboard")

        # Test non-existent dashboard
        self.assertIn("error", JiraAPI.DashboardApi.get_dashboard("D2"))

    def test_filter_api(self):
        """Test filter retrieval and update."""
        # Add filter data to DB
        DB["filters"]["F1"] = {
            "id": "F1",
            "name": "All Issues",
            "jql": "ORDER BY created",
        }

        # Get all filters
        all_filters = JiraAPI.FilterApi.get_filters()
        self.assertIn("filters", all_filters)
        self.assertEqual(len(all_filters["filters"]), 1)
        self.assertEqual(all_filters["filters"][0]["name"], "All Issues")

        # Get one filter
        one_filter = JiraAPI.FilterApi.get_filter("F1")
        self.assertEqual(one_filter["name"], "All Issues")

        # Update filter
        upd_filter = JiraAPI.FilterApi.update_filter(
            "F1", name="Updated Filter", jql="ORDER BY updated"
        )
        self.assertTrue(upd_filter["updated"])

        # Verify update
        fetched = JiraAPI.FilterApi.get_filter("F1")
        self.assertEqual(fetched["name"], "Updated Filter")

        # Test non-existent filter
        not_found = JiraAPI.FilterApi.get_filter("ghost")
        self.assertIn("error", not_found)

        upd_filter = JiraAPI.FilterApi.update_filter(
            "F1",
            name="Updated Filter",
            jql="",
            description="Updated Description",
            favorite=True,
            editable=True,
        )
        self.assertTrue(upd_filter["updated"])

    def test_filter_api_update_invalid_id(self):
        """Test updating a filter with an invalid id."""
        self.assertIn(
            "error",
            JiraAPI.FilterApi.update_filter(
                filter_id="nonexistent", name="Updated Filter"
            ),
        )

    def test_group_api_get(self):
        """Test getting group info."""
        # Create a group using the API
        create_resp = JiraAPI.GroupApi.create_group(name="admins")
        self.assertTrue(create_resp["created"])

        # Add users to the group
        update_resp = JiraAPI.GroupApi.update_group(
            groupname="admins", users=["alice", "bob"]
        )
        self.assertIn("admins", update_resp)

        # Test group update with invalid groupname
        self.assertIn(
            "error",
            JiraAPI.GroupApi.update_group(
                groupname="nonexistent", users=["alice", "bob"]
            ),
        )

        # Get group info
        grp_info = JiraAPI.GroupApi.get_group(groupname="admins")
        self.assertIn("group", grp_info)
        self.assertEqual(grp_info["group"]["name"], "admins")
        self.assertEqual(grp_info["group"]["users"], ["alice", "bob"])

    def test_valid_groupname_found(self):
        """Test retrieving an existing group with a valid groupname."""
        create_resp = JiraAPI.GroupApi.create_group(name="admins")
        self.assertTrue(create_resp["created"])
        result = get_group_by_name(groupname="admins")

        self.assertIsInstance(result, dict)
        self.assertIn("group", result)
        self.assertNotIn("error", result)
        self.assertEqual(result["group"]["name"], "admins")

    def test_invalid_type_groupname_int(self):
        """Test providing an integer for groupname raises TypeError."""
        self.assert_error_behavior(
            func_to_call=get_group_by_name,
            expected_exception_type=TypeError,
            expected_message="Expected groupname to be a string, but got int.",
            groupname=123
        )

    def test_invalid_type_groupname_none(self):
        """Test providing None for groupname raises TypeError."""
        self.assert_error_behavior(
            func_to_call=get_group_by_name,
            expected_exception_type=TypeError,
            expected_message="Expected groupname to be a string, but got NoneType.",
            groupname=None
        )

    def test_invalid_value_groupname_empty(self):
        """Test providing an empty string for groupname raises ValueError."""
        self.assert_error_behavior(
            func_to_call=get_group_by_name,
            expected_exception_type=ValueError,
            expected_message="groupname cannot be empty or consist only of whitespace.",
            groupname=""
        )

    def test_invalid_value_groupname_whitespace(self):
        """Test providing a whitespace-only string for groupname raises ValueError."""
        self.assert_error_behavior(
            func_to_call=get_group_by_name,
            expected_exception_type=ValueError,
            expected_message="groupname cannot be empty or consist only of whitespace.",
            groupname="   "
        )

    def test_groups_picker_api(self):
        """Test group picker."""
        # Add groups data to DB
        DB["groups"]["devTeam"] = {"name": "devTeam", "users": []}
        DB["groups"]["designTeam"] = {"name": "designTeam", "users": []}

        # Find with query
        found = JiraAPI.GroupsPickerApi.find_groups(query="dev")
        self.assertIn("groups", found)
        self.assertEqual(found["groups"], ["devTeam"])

        # Test with integer query
        with self.assertRaises(TypeError) as cm:
            JiraAPI.GroupsPickerApi.find_groups(query=123)
        self.assertIn("query must be a string or None", str(cm.exception))
        
        # Test with list query
        with self.assertRaises(TypeError) as cm:
            JiraAPI.GroupsPickerApi.find_groups(query=["group1", "group2"])
        self.assertIn("query must be a string or None", str(cm.exception))

    def test_issue_bulk_operation_and_picker(self):
        """Test bulk issue operation and issue picker."""
        # Create some test issues
        issue_fields = {
            "project": "TEST",
            "summary": "Alpha",
            "description": "Test issue Alpha",
            "issuetype": "Task",
            "priority": "Medium",
            "assignee": {"name": "testuser"}
        }
        i1 = JiraAPI.IssueApi.create_issue(fields=issue_fields)
        
        issue_fields["summary"] = "Beta"
        issue_fields["description"] = "Test issue Beta"
        i2 = JiraAPI.IssueApi.create_issue(fields=issue_fields)
        
        # Run bulk update
        bulk_result = JiraAPI.IssueApi.bulk_issue_operation(
            issueUpdates=[{"id": i1["id"], "fields": {"summary": "Alpha+"}}]
        )
        self.assertTrue(bulk_result["bulkProcessed"])

        # Test picker with specific queries
        alpha_issues = JiraAPI.IssueApi.issue_picker(query="alpha")
        self.assertIn("issues", alpha_issues)
        
        beta_issues = JiraAPI.IssueApi.issue_picker(query="beta")
        self.assertIn("issues", beta_issues)
        
        # Either alpha or beta should return at least one result
        self.assertTrue(
            len(alpha_issues["issues"]) > 0 or len(beta_issues["issues"]) > 0,
            "Issue picker should find at least one issue with alpha or beta in the summary"
        )
        
        # Get all issues using an empty string query
        all_issues = JiraAPI.IssueApi.issue_picker(query="")
        self.assertIn("issues", all_issues)
        self.assertGreaterEqual(len(all_issues["issues"]), 2, 
                              "Issue picker should return at least 2 issues with empty query")

    def test_issue_get_create_meta(self):
        """Test retrieving create meta."""
        cm = JiraAPI.IssueApi.get_create_meta(projectKeys = "TRYDEMO")
        self.assertIn("projects", cm)
        self.assertEqual(cm["projects"][0]["key"], "TRYDEMO")

    def test_issue_link_api(self):
        """Test issue link creation."""
        # Create two issues to link
        issue_fields = {
            "project": "TEST",
            "summary": "Inward",
            "description": "Test issue Inward",
            "issuetype": "Task",
            "priority": "Medium",
            "assignee": {"name": "testuser"}
        }
        i1 = JiraAPI.IssueApi.create_issue(fields=issue_fields)
        
        issue_fields["summary"] = "Outward"
        issue_fields["description"] = "Test issue Outward"
        i2 = JiraAPI.IssueApi.create_issue(fields=issue_fields)

        # Create a link using existing API
        link_result = JiraAPI.IssueLinkApi.create_issue_link(
            type="Relates",
            inwardIssue={"key": i1["id"]},
            outwardIssue={"key": i2["id"]}
        )
        
        self.assertIn("created", link_result)
        self.assertTrue(link_result["created"])
        self.assertEqual(link_result["issueLink"]["type"], "Relates")
        self.assertEqual(link_result["issueLink"]["inwardIssue"]["key"], i1["id"])
        self.assertEqual(link_result["issueLink"]["outwardIssue"]["key"], i2["id"])

    def test_create_issue_backward_compatibility(self):
        """Test backward compatibility for create_issue function."""
        
        # Test 1: Minimal fields (only project and summary) - should work with defaults
        minimal_fields = {
            "project": "COMPAT_TEST",
            "summary": "Minimal issue for compatibility testing"
        }
        created_minimal = JiraAPI.IssueApi.create_issue(fields=minimal_fields)
        
        self.assertIn("id", created_minimal)
        self.assertIn("fields", created_minimal)
        
        # Verify defaults were applied
        fields = created_minimal["fields"]
        self.assertEqual(fields["project"], "COMPAT_TEST")
        self.assertEqual(fields["summary"], "Minimal issue for compatibility testing")
        self.assertEqual(fields["description"], "")  # Default empty string
        self.assertEqual(fields["issuetype"], "Task")  # Default Task
        self.assertEqual(fields["priority"], "P2")  # Default Medium
        self.assertEqual(fields["assignee"], {"name": "Unassigned"})  # Default Unassigned
        self.assertEqual(fields["status"], "Open")  # Default Open
        
        # Test 2: String assignee format (old format) - should be converted to dict
        string_assignee_fields = {
            "project": "COMPAT_TEST",
            "summary": "Issue with string assignee",
            "assignee": "john.doe@example.com"
        }
        created_string_assignee = JiraAPI.IssueApi.create_issue(fields=string_assignee_fields)
        
        self.assertIn("id", created_string_assignee)
        fields = created_string_assignee["fields"]
        self.assertEqual(fields["assignee"], {"name": "john.doe@example.com"})
        
        # Test 3: Dict assignee without name field - should add default name
        dict_no_name_fields = {
            "project": "COMPAT_TEST", 
            "summary": "Issue with incomplete assignee dict",
            "assignee": {"email": "test@example.com"}
        }
        created_dict_no_name = JiraAPI.IssueApi.create_issue(fields=dict_no_name_fields)
        
        self.assertIn("id", created_dict_no_name)
        fields = created_dict_no_name["fields"]
        self.assertEqual(fields["assignee"]["name"], "Unassigned")
        
        # Test 4: Partial fields - should fill in missing ones with defaults
        partial_fields = {
            "project": "COMPAT_TEST",
            "summary": "Partial issue",
            "description": "Custom description",
            "priority": "High"
            # Missing: issuetype, assignee
        }
        created_partial = JiraAPI.IssueApi.create_issue(fields=partial_fields)
        
        self.assertIn("id", created_partial)
        fields = created_partial["fields"]
        self.assertEqual(fields["description"], "Custom description")
        self.assertEqual(fields["priority"], "High")
        self.assertEqual(fields["issuetype"], "Task")  # Default
        self.assertEqual(fields["assignee"], {"name": "Unassigned"})  # Default
        
        # Test 5: All fields provided (new format) - should work as before
        complete_fields = {
            "project": "COMPAT_TEST",
            "summary": "Complete issue",
            "description": "Full description",
            "issuetype": "Bug",
            "priority": "Critical", 
            "assignee": {"name": "alice.smith"},
            "status": "In Progress"
        }
        created_complete = JiraAPI.IssueApi.create_issue(fields=complete_fields)
        
        self.assertIn("id", created_complete)
        fields = created_complete["fields"]
        self.assertEqual(fields["project"], "COMPAT_TEST")
        self.assertEqual(fields["summary"], "Complete issue")
        self.assertEqual(fields["description"], "Full description")
        self.assertEqual(fields["issuetype"], "Bug")
        self.assertEqual(fields["priority"], "Critical")
        self.assertEqual(fields["assignee"], {"name": "alice.smith"})
        self.assertEqual(fields["status"], "In Progress")

    def test_create_issue_validation_errors(self):
        """Test that proper validation errors are still raised for invalid inputs."""
        
        # Test 1: Empty fields dict - should raise EmptyFieldError
        with self.assertRaises(EmptyFieldError):
            JiraAPI.IssueApi.create_issue(fields={})
            
        # Test 2: Missing project - should raise MissingRequiredFieldError
        with self.assertRaises(MissingRequiredFieldError):
            JiraAPI.IssueApi.create_issue(fields={"summary": "No project"})
            
        # Test 3: Missing summary - should raise MissingRequiredFieldError  
        with self.assertRaises(MissingRequiredFieldError):
            JiraAPI.IssueApi.create_issue(fields={"project": "TEST"})
            
        # Test 4: Both missing - should raise MissingRequiredFieldError
        with self.assertRaises(MissingRequiredFieldError):
            JiraAPI.IssueApi.create_issue(fields={"description": "No project or summary"})

    def test_create_issue_edge_cases(self):
        """Test edge cases for backward compatibility."""
        
        # Test 1: Empty string assignee - should be converted to dict
        empty_assignee_fields = {
            "project": "EDGE_TEST",
            "summary": "Empty assignee test",
            "assignee": ""
        }
        created_empty = JiraAPI.IssueApi.create_issue(fields=empty_assignee_fields)
        
        self.assertIn("id", created_empty)
        fields = created_empty["fields"]
        self.assertEqual(fields["assignee"], {"name": ""})
        
        # Test 2: Various string assignee formats
        test_cases = [
            "user123",
            "user@company.com", 
            "User Name",
            "user.name@domain.co.uk"
        ]
        
        for assignee_str in test_cases:
            test_fields = {
                "project": "EDGE_TEST",
                "summary": f"Test assignee: {assignee_str}",
                "assignee": assignee_str
            }
            created = JiraAPI.IssueApi.create_issue(fields=test_fields)
            
            self.assertIn("id", created)
            self.assertEqual(created["fields"]["assignee"], {"name": assignee_str})
            
        # Test 3: Status defaults when not provided vs when provided
        no_status_fields = {
            "project": "EDGE_TEST",
            "summary": "No status field"
        }
        created_no_status = JiraAPI.IssueApi.create_issue(fields=no_status_fields)
        self.assertEqual(created_no_status["fields"]["status"], "Open")
        
        with_status_fields = {
            "project": "EDGE_TEST", 
            "summary": "With status field",
            "status": "Closed"
        }
        created_with_status = JiraAPI.IssueApi.create_issue(fields=with_status_fields)
        self.assertEqual(created_with_status["fields"]["status"], "Closed")

    def test_create_issue_link_validation(self):
        """Test input validation for create_issue_link function."""
        from ..SimulationEngine.custom_errors import IssueNotFoundError
        from pydantic import ValidationError

        # Create test issues first
        issue_fields = {
            "project": "TEST",
            "summary": "Test Issue 1",
            "description": "Test issue for linking",
            "issuetype": "Task",
            "priority": "Medium",
            "assignee": {"name": "testuser"}
        }
        i1 = JiraAPI.IssueApi.create_issue(fields=issue_fields)

        issue_fields["summary"] = "Test Issue 2"
        i2 = JiraAPI.IssueApi.create_issue(fields=issue_fields)

        # Test successful creation
        result = JiraAPI.IssueLinkApi.create_issue_link(
            type="Relates",
            inwardIssue={"key": i1["id"]},
            outwardIssue={"key": i2["id"]}
        )
        self.assertTrue(result["created"])
        self.assertIn("issueLink", result)
        self.assertEqual(result["issueLink"]["type"], "Relates")

        # Test invalid type parameter (integer)
        with self.assertRaises(ValidationError):
            JiraAPI.IssueLinkApi.create_issue_link(
                type=123,
                inwardIssue={"key": i1["id"]},
                outwardIssue={"key": i2["id"]}
            )

        # Test empty type parameter
        with self.assertRaises(ValidationError):
            JiraAPI.IssueLinkApi.create_issue_link(
                type="",
                inwardIssue={"key": i1["id"]},
                outwardIssue={"key": i2["id"]}
            )

        # Test invalid inwardIssue parameter (not a dict)
        with self.assertRaises(ValidationError):
            JiraAPI.IssueLinkApi.create_issue_link(
                type="Relates",
                inwardIssue="not-a-dict",
                outwardIssue={"key": i2["id"]}
            )

        # Test missing key in inwardIssue
        with self.assertRaises(ValidationError):
            JiraAPI.IssueLinkApi.create_issue_link(
                type="Relates",
                inwardIssue={},
                outwardIssue={"key": i2["id"]}
            )

        # Test empty key in inwardIssue
        with self.assertRaises(ValidationError):
            JiraAPI.IssueLinkApi.create_issue_link(
                type="Relates",
                inwardIssue={"key": ""},
                outwardIssue={"key": i2["id"]}
            )

        # Test non-existent inward issue
        with self.assertRaises(IssueNotFoundError) as context:
            JiraAPI.IssueLinkApi.create_issue_link(
                type="Relates",
                inwardIssue={"key": "NONEXISTENT-1"},
                outwardIssue={"key": i2["id"]}
            )
        self.assertEqual(str(context.exception), "Inward issue with key 'NONEXISTENT-1' not found in database.")

        # Test non-existent outward issue
        with self.assertRaises(IssueNotFoundError) as context:
            JiraAPI.IssueLinkApi.create_issue_link(
                type="Relates",
                inwardIssue={"key": i1["id"]},
                outwardIssue={"key": "NONEXISTENT-2"}
            )
        self.assertEqual(str(context.exception), "Outward issue with key 'NONEXISTENT-2' not found in database.")

    def test_issue_link_type_api(self):
        """Test issue link type retrieval."""
        # Add issue link type data to DB
        DB["issue_link_types"]["Relates"] = {"id": "Relates", "name": "Relates"}

        # Get all issue link types
        all_types = JiraAPI.IssueLinkTypeApi.get_issue_link_types()
        self.assertIn("issueLinkTypes", all_types)
        self.assertEqual(len(all_types["issueLinkTypes"]), 1)
        self.assertEqual(all_types["issueLinkTypes"][0]["name"], "Relates")

        # Get one issue link type
        one_type = JiraAPI.IssueLinkTypeApi.get_issue_link_type("Relates")
        self.assertEqual(one_type["name"], "Relates")

        # Test non-existent issue link type
        self.assertIn("error", JiraAPI.IssueLinkTypeApi.get_issue_link_type("Blocks"))

        self.assertIn("error", JiraAPI.IssueLinkTypeApi.get_issue_link_type(""))

    def test_issue_type_api(self):
        """Test issue type retrieval and creation."""
        # Create a new issue type
        new_type = JiraAPI.IssueTypeApi.create_issue_type(
            name="Bug", description="A software bug"
        )
        self.assertIn("created", new_type)
        self.assertTrue(new_type["created"])
        self.assertIn("issueType", new_type)
        self.assertEqual(new_type["issueType"]["name"], "Bug")
        self.assertEqual(new_type["issueType"]["description"], "A software bug")
        self.assertEqual(
            new_type["issueType"]["subtask"], False
        )  # Default type is "standard"


        # Get all issue types
        all_types = JiraAPI.IssueTypeApi.get_issue_types()
        self.assertIn("issueTypes", all_types)
        self.assertEqual(len(all_types["issueTypes"]), 1)
        self.assertEqual(all_types["issueTypes"][0]["name"], "Bug")

        # Get one issue type
        one_type = JiraAPI.IssueTypeApi.get_issue_type(new_type["issueType"]["id"])
        self.assertEqual(one_type["name"], "Bug")

        # Test non-existent issue type
        with self.assertRaises(IssueTypeNotFoundError) as context:
            JiraAPI.IssueTypeApi.get_issue_type("Task")
        self.assertEqual(str(context.exception), "Issue type with ID 'Task' not found in database.")

        # Create a subtask issue type
        subtask_type = JiraAPI.IssueTypeApi.create_issue_type(
            name="Subtask", description="A subtask", type="subtask"
        )
        self.assertIn("created", subtask_type)
        self.assertTrue(subtask_type["created"])
        self.assertIn("issueType", subtask_type)
        self.assertEqual(subtask_type["issueType"]["name"], "Subtask")
        self.assertEqual(subtask_type["issueType"]["description"], "A subtask")
        self.assertEqual(subtask_type["issueType"]["subtask"], True)

    def test_get_issue_type_validation(self):
        """Test input validation for get_issue_type function."""  
        # Create a test issue type first
        new_type = JiraAPI.IssueTypeApi.create_issue_type(
            name="TestType", description="A test type"
        )
        type_id = new_type["issueType"]["id"]
        
        # Test successful retrieval
        result = JiraAPI.IssueTypeApi.get_issue_type(type_id)
        self.assertEqual(result["name"], "TestType")
        self.assertEqual(result["description"], "A test type")
        
        # Test invalid type_id type (integer)
        with self.assertRaises(TypeError) as context:
            JiraAPI.IssueTypeApi.get_issue_type(123)
        self.assertEqual(str(context.exception), "type_id must be a string, got int.")
        
        # Test invalid type_id type (None)
        with self.assertRaises(TypeError) as context:
            JiraAPI.IssueTypeApi.get_issue_type(None)
        self.assertEqual(str(context.exception), "type_id must be a string, got NoneType.")
        
        # Test empty type_id
        with self.assertRaises(ValueError) as context:
            JiraAPI.IssueTypeApi.get_issue_type("")
        self.assertEqual(str(context.exception), "type_id cannot be empty.")
        
        # Test non-existent type_id
        with self.assertRaises(IssueTypeNotFoundError) as context:
            JiraAPI.IssueTypeApi.get_issue_type("NONEXISTENT")
        self.assertEqual(str(context.exception), "Issue type with ID 'NONEXISTENT' not found in database.")


    def test_jql_api_autocomplete_data(self):
        """Test JQL autocomplete data retrieval."""
        ac_data = JiraAPI.JqlApi.get_jql_autocomplete_data()
        self.assertIn("fields", ac_data)
        self.assertIn("operators", ac_data)

    def test_license_validator(self):
        """Test license validation."""
        valid_license = JiraAPI.LicenseValidatorApi.validate_license(
            license="ABC123FAKE"
        )
        self.assertTrue(valid_license["valid"])
        self.assertIn("decoded", valid_license)
        # Missing required field
        self.assertIn("error", JiraAPI.LicenseValidatorApi.validate_license(""))

    def test_my_permissions_api(self):
        """Test current user permissions."""
        perms = JiraAPI.MyPermissionsApi.get_current_user_permissions()
        self.assertIn("permissions", perms)
        self.assertIsInstance(perms["permissions"], list)
        self.assertIn("CREATE_ISSUE", perms["permissions"])
        self.assertIn("EDIT_ISSUE", perms["permissions"])
        self.assertIn("DELETE_ISSUE", perms["permissions"])
        self.assertIn("ASSIGN_ISSUE", perms["permissions"])
        self.assertIn("CLOSE_ISSUE", perms["permissions"])

    def test_my_preferences_api(self):
        """Test getting and updating my preferences."""
        # Initially empty
        prefs = JiraAPI.MyPreferencesApi.get_my_preferences()
        self.assertEqual(prefs, {})
        # Update
        upd = JiraAPI.MyPreferencesApi.update_my_preferences(value={"theme": "dark"})
        self.assertTrue(upd["updated"])
        fetched = JiraAPI.MyPreferencesApi.get_my_preferences()
        self.assertEqual(fetched, {"theme": "dark"})
        # Missing field
        self.assertIn("error", JiraAPI.MyPreferencesApi.update_my_preferences({}))

    def test_permissions_api(self):
        """Test getting permissions."""
        # Add permissions data to DB
        DB["permissions"]["BROWSE"] = {
            "id": "BROWSE",
            "description": "Browse permission",
        }

        # Get all permissions
        perms = JiraAPI.PermissionsApi.get_permissions()
        self.assertIn("permissions", perms)
        self.assertIn("BROWSE", perms["permissions"])
        self.assertEqual(
            perms["permissions"]["BROWSE"]["description"], "Browse permission"
        )

    def test_permission_scheme_api(self):
        """Test getting permission schemes."""
        # Add permission scheme data to DB
        DB["permission_schemes"]["PS1"] = {"id": "PS1", "name": "Default scheme"}

        # Get all permission schemes
        all_schemes = JiraAPI.PermissionSchemeApi.get_permission_schemes()
        self.assertIn("schemes", all_schemes)
        self.assertEqual(len(all_schemes["schemes"]), 1)
        self.assertEqual(all_schemes["schemes"][0]["name"], "Default scheme")

        # Get one permission scheme
        one_scheme = JiraAPI.PermissionSchemeApi.get_permission_scheme("PS1")
        self.assertEqual(one_scheme["name"], "Default scheme")

        # Test non-existent permission scheme
        self.assertIn("error", JiraAPI.PermissionSchemeApi.get_permission_scheme("PS2"))

    def test_priority_api(self):
        """Test getting priorities."""
        # Add priority data to DB
        DB["priorities"]["P1"] = {"id": "P1", "name": "High"}

        # Get all priorities
        all_pri = JiraAPI.PriorityApi.get_priorities()
        self.assertIn("priorities", all_pri)
        self.assertEqual(len(all_pri["priorities"]), 1)
        self.assertEqual(all_pri["priorities"][0]["name"], "High")

        # Get one priority
        one_pri = JiraAPI.PriorityApi.get_priority("P1")
        self.assertEqual(one_pri["name"], "High")

        # Test non-existent priority
        with self.assertRaises(PriorityNotFoundError) as context:
            JiraAPI.PriorityApi.get_priority("P2")
        self.assertEqual(str(context.exception), "Priority with ID 'P2' not found in database.")

    def test_get_priority_validation(self):
        """Test input validation for get_priority function."""
        
        # Create a test priority first
        DB["priorities"]["P1"] = {"id": "P1", "name": "High"}
        
        # Test successful retrieval
        result = JiraAPI.PriorityApi.get_priority("P1")
        self.assertEqual(result["name"], "High")
        self.assertEqual(result["id"], "P1")
        
        # Test invalid priority_id type (integer)
        with self.assertRaises(TypeError) as context:
            JiraAPI.PriorityApi.get_priority(123)
        self.assertEqual(str(context.exception), "priority_id must be a string, got int.")
        
        # Test invalid priority_id type (None)
        with self.assertRaises(TypeError) as context:
            JiraAPI.PriorityApi.get_priority(None)
        self.assertEqual(str(context.exception), "priority_id must be a string, got NoneType.")
        
        # Test empty priority_id
        with self.assertRaises(ValueError) as context:
            JiraAPI.PriorityApi.get_priority("")
        self.assertEqual(str(context.exception), "priority_id cannot be empty.")
        
        # Test non-existent priority_id
        with self.assertRaises(PriorityNotFoundError) as context:
            JiraAPI.PriorityApi.get_priority("NONEXISTENT")
        self.assertEqual(str(context.exception), "Priority with ID 'NONEXISTENT' not found in database.")

    def test_project_api(self):
        """Test project creation and retrieval."""
        # Create a new project
        new_project = JiraAPI.ProjectApi.create_project(
            proj_key="TEST", proj_name="Test Project"
        )
        self.assertIn("created", new_project)
        self.assertTrue(new_project["created"])
        self.assertIn("project", new_project)
        self.assertEqual(new_project["project"]["key"], "TEST")
        self.assertEqual(new_project["project"]["name"], "Test Project")

        with self.assertRaises(ProjectInputError):
            JiraAPI.ProjectApi.create_project(proj_key="", proj_name="Test Project")
        with self.assertRaises(ProjectInputError):
            JiraAPI.ProjectApi.create_project(proj_key="TEST", proj_name="")

        # Get all projects
        all_proj = JiraAPI.ProjectApi.get_projects()
        self.assertIn("projects", all_proj)
        self.assertEqual(len(all_proj["projects"]), 2)
        self.assertEqual(all_proj["projects"][1]["name"], "Test Project")

        # Get one project - success case
        one_proj = JiraAPI.ProjectApi.get_project("TEST")
        self.assertEqual(one_proj["name"], "Test Project")

        # Test non-existent project - ValueError
        self.assert_error_behavior(
            func_to_call=JiraAPI.ProjectApi.get_project,
            expected_exception_type=ValueError,
            expected_message="Project with key 'NONEXISTENT' not found.",
            project_key="NONEXISTENT"
        )

        # Test invalid project_key type - TypeError
        self.assert_error_behavior(
            func_to_call=JiraAPI.ProjectApi.get_project,
            expected_exception_type=TypeError,
            expected_message="project_key must be a string",
            project_key=123
        )

        self.assert_error_behavior(
            func_to_call=JiraAPI.ProjectApi.get_project,
            expected_exception_type=TypeError,
            expected_message="project_key must be a string",
            project_key=None
        )

        self.assert_error_behavior(
            func_to_call=JiraAPI.ProjectApi.get_project,
            expected_exception_type=TypeError,
            expected_message="project_key must be a string",
            project_key=["TEST"]
        )

        # Test empty project_key - ProjectInputError
        self.assert_error_behavior(
            func_to_call=JiraAPI.ProjectApi.get_project,
            expected_exception_type=ProjectInputError,
            expected_message="project_key cannot be empty.",
            project_key=""
        )

        self.assert_error_behavior(
            func_to_call=JiraAPI.ProjectApi.get_project,
            expected_exception_type=ProjectInputError,
            expected_message="project_key cannot be empty.",
            project_key="   "
        )

    def test_project_avatars_api(self):
        """Test project avatars."""
        # Add project avatar data to DB
        DB["avatars"].append(
            {"id": "AVATAR-1", "type": "project", "filename": "avatar1.png"}
        )

        # Get all project avatars
        avatars = JiraAPI.ProjectApi.get_project_avatars("TEST")
        self.assertIn("avatars", avatars)
        self.assertEqual(len(avatars["avatars"]), 1)
        self.assertEqual(avatars["avatars"][0]["filename"], "avatar1.png")

    def test_get_project_avatars_validation(self):
        """Test input validation for get_project_avatars function."""
        # Add test avatar data
        DB["avatars"].append(
            {"id": "AVATAR-1", "type": "project", "filename": "avatar1.png"}
        )
        
        # Test successful retrieval
        result = JiraAPI.ProjectApi.get_project_avatars("TEST")
        self.assertIn("avatars", result)
        self.assertIn("project", result)
        self.assertEqual(result["project"], "TEST")
        self.assertEqual(len(result["avatars"]), 1)
        self.assertEqual(result["avatars"][0]["filename"], "avatar1.png")
        
        # Test invalid project_key type (integer)
        with self.assertRaises(TypeError) as context:
            JiraAPI.ProjectApi.get_project_avatars(123)
        self.assertEqual(str(context.exception), "project_key must be a string, got int.")
        
        # Test invalid project_key type (None)
        with self.assertRaises(TypeError) as context:
            JiraAPI.ProjectApi.get_project_avatars(None)
        self.assertEqual(str(context.exception), "project_key must be a string, got NoneType.")
        
        # Test empty project_key
        with self.assertRaises(ValueError) as context:
            JiraAPI.ProjectApi.get_project_avatars("")
        self.assertEqual(str(context.exception), "project_key cannot be empty.")
        
        # Test with different project key (should still return all project avatars due to mock behavior)
        result2 = JiraAPI.ProjectApi.get_project_avatars("DIFFERENT")
        self.assertEqual(result2["project"], "DIFFERENT")
        self.assertEqual(len(result2["avatars"]), 1)  # Same avatars as mock returns all

    def test_project_components_api(self):
        """Test project components."""
        # Add project component data to DB
        DB["components"]["CMP-1"] = {
            "id": "CMP-1",
            "project": "TEST",
            "name": "Component One",
            "description": "Component One Description",
        }

        # Get all project components
        components = JiraAPI.ProjectApi.get_project_components("TEST")
        self.assertIn("components", components)
        self.assertEqual(len(components["components"]), 1)
        self.assertEqual(components["components"][0]["name"], "Component One")

    def test_delete_project_api(self):
        """Test project deletion."""
        # Create a project
        new_project = JiraAPI.ProjectApi.create_project(
            proj_key="TEST", proj_name="Test Project"
        )
        new_component = JiraAPI.ComponentApi.create_component(
            project="TEST", name="Test Component"
        )
        self.assertIn("created", new_project)
        self.assertTrue(new_project["created"])

        # Delete the project
        del_resp = JiraAPI.ProjectApi.delete_project("TEST")
        self.assertIn("deleted", del_resp)
        self.assertEqual(del_resp["deleted"], "TEST")

        # Test non-existent project
        self.assertIn("error", JiraAPI.ProjectApi.delete_project("NONE"))

    def test_project_category_api(self):
        """Test project categories."""
        # Add project category data to DB
        DB["project_categories"]["CAT1"] = {"id": "CAT1", "name": "Category One"}

        # Get all project categories
        cats = JiraAPI.ProjectCategoryApi.get_project_categories()
        self.assertIn("categories", cats)
        self.assertEqual(len(cats["categories"]), 1)
        self.assertEqual(cats["categories"][0]["name"], "Category One")

        # Get one project category
        one_cat = JiraAPI.ProjectCategoryApi.get_project_category("CAT1")
        self.assertEqual(one_cat["name"], "Category One")

        # Test non-existent project category
        self.assertIn("error", JiraAPI.ProjectCategoryApi.get_project_category("CAT2"))

    def test_resolution_api(self):
        """Test resolution API."""
        # Add resolution data to DB
        DB["resolutions"]["RES1"] = {"id": "RES1", "name": "Done"}

        # Get all resolutions
        res_all = JiraAPI.ResolutionApi.get_resolutions()
        self.assertIn("resolutions", res_all)
        self.assertEqual(len(res_all["resolutions"]), 1)
        self.assertEqual(res_all["resolutions"][0]["name"], "Done")

        # Get one resolution
        res_one = JiraAPI.ResolutionApi.get_resolution("RES1")
        self.assertEqual(res_one["name"], "Done")

        # Test non-existent resolution
        with self.assertRaises(ResolutionNotFoundError) as context:
            JiraAPI.ResolutionApi.get_resolution("RES2")
        self.assertEqual(str(context.exception), "Resolution with ID 'RES2' not found in database.")

    def test_get_resolution_validation(self):
        """Test input validation for get_resolution function."""
    
        # Create a test resolution first
        DB["resolutions"]["RES1"] = {"id": "RES1", "name": "Done"}
        
        # Test successful retrieval
        result = JiraAPI.ResolutionApi.get_resolution("RES1")
        self.assertEqual(result["name"], "Done")
        self.assertEqual(result["id"], "RES1")
        
        # Test invalid res_id type (integer)
        with self.assertRaises(TypeError) as context:
            JiraAPI.ResolutionApi.get_resolution(123)
        self.assertEqual(str(context.exception), "res_id must be a string, got int.")
        
        # Test invalid res_id type (None)
        with self.assertRaises(TypeError) as context:
            JiraAPI.ResolutionApi.get_resolution(None)
        self.assertEqual(str(context.exception), "res_id must be a string, got NoneType.")
        
        # Test empty res_id
        with self.assertRaises(ValueError) as context:
            JiraAPI.ResolutionApi.get_resolution("")
        self.assertEqual(str(context.exception), "res_id cannot be empty.")
        
        # Test non-existent res_id
        with self.assertRaises(ResolutionNotFoundError) as context:
            JiraAPI.ResolutionApi.get_resolution("NONEXISTENT")
        self.assertEqual(str(context.exception), "Resolution with ID 'NONEXISTENT' not found in database.")

    def test_role_api(self):
        """Test role retrieval."""
        # Add role data to DB
        DB["roles"]["R1"] = {"id": "R1", "name": "Developer"}

        # Get all roles
        all_roles = JiraAPI.RoleApi.get_roles()
        self.assertIn("roles", all_roles)
        self.assertEqual(len(all_roles["roles"]), 1)
        self.assertEqual(all_roles["roles"][0]["name"], "Developer")

        # Get one role
        one_role = JiraAPI.RoleApi.get_role("R1")
        self.assertEqual(one_role["name"], "Developer")

        # Test non-existent role
        self.assertIn("error", JiraAPI.RoleApi.get_role("R2"))

    def test_server_info_api(self):
        """Test server info."""
        info = JiraAPI.ServerInfoApi.get_server_info()
        self.assertIn("baseUrl", info)
        self.assertIn("version", info)
        self.assertIn("title", info)

    def test_settings_api(self):
        """Test settings retrieval."""
        sets = JiraAPI.SettingsApi.get_settings()
        self.assertIn("settings", sets)
        self.assertIn("exampleSetting", sets["settings"])

    def test_status_api(self):
        """Test status API."""
        DB["statuses"] = {"S1": {"id": "S1", "name": "In Progress", "description": "In Progress Description"}}
        status = JiraAPI.StatusApi.get_status("S1")
        self.assertEqual(status["name"], "In Progress")
        self.assertEqual(status["description"], "In Progress Description")
        self.assertEqual(status["id"], "S1")
       
        
    def test_status_api_get_status_invalid_input_type(self):
        """Test status API."""
        self.assert_error_behavior(
            func_to_call=JiraAPI.StatusApi.get_status,
            expected_exception_type=TypeError,
            expected_message="status_id must be a string",
            status_id=123
        )

    def test_status_api_get_status_invalid_input_value(self):
        """Test status API."""
        self.assert_error_behavior(
            func_to_call=JiraAPI.StatusApi.get_status,
            expected_exception_type=ValueError,
            expected_message="Status 'S2' not found.",
            status_id="S2"
        )

    def test_status_api_missing_required_field(self):
        """Test status API."""
        self.assert_error_behavior(
            func_to_call=JiraAPI.StatusApi.get_status,
            expected_exception_type=MissingRequiredFieldError,
            expected_message="Missing required field 'status_id'.",
            status_id=None  
        )

    def test_status_category_api(self):
        """Test status category API."""
        DB["status_categories"]["SC1"] = {
            "id": "SC1",
            "name": "To Do",
            "description": "To Do Description",
            "color": "blue",
        }


        # Get all status categories
        all_cat = JiraAPI.StatusCategoryApi.get_status_categories()
        self.assertIn("statusCategories", all_cat)
        self.assertEqual(len(all_cat["statusCategories"]), 1)
        self.assertEqual(all_cat["statusCategories"][0]["name"], "To Do")

        # Get one status category
        one_cat = JiraAPI.StatusCategoryApi.get_status_category("SC1")
        self.assertIn("statusCategory", one_cat)
        self.assertEqual(one_cat["statusCategory"]["name"], "To Do")

    def test_status_category_api_get_status_category_invalid_input_type(self):
        """Test status category API."""
        self.assert_error_behavior(
            func_to_call=JiraAPI.StatusCategoryApi.get_status_category,
            expected_exception_type=TypeError,
            expected_message="cat_id must be a string",
            cat_id=123)

    def test_status_category_api_get_status_category_invalid_input_value(self):
        """Test status category API."""
        self.assert_error_behavior(
            func_to_call=JiraAPI.StatusCategoryApi.get_status_category,
            expected_exception_type=ValueError,
            expected_message="Status category 'SC2' not found.",
            cat_id="SC2")

    def test_status_category_api_get_status_category_missing_required_field(self):
        """Test status category API."""
        self.assert_error_behavior(
            func_to_call=JiraAPI.StatusCategoryApi.get_status_category,
            expected_exception_type=MissingRequiredFieldError,
            expected_message="Missing required field 'cat_id'.",
            cat_id=None)


    def test_user_api(self):
        """Test getting, creating, and deleting a user."""
        # Create
        new_user = JiraAPI.UserApi.create_user(
            {
                "name": "tester",
                "emailAddress": "test@example.com",
                "displayName": "Test User",
            }
        )
        self.assertTrue(new_user["created"])

        # Get
        got_user = get_user_by_username_or_account_id(username="tester")
        self.assertEqual(got_user["displayName"], "Test User")

        got_user_with_key = get_user_by_username_or_account_id(account_id=got_user["key"])
        self.assertEqual(got_user_with_key["displayName"], "Test User")

        self.assert_error_behavior(
            func_to_call=get_user_by_username_or_account_id,
            expected_exception_type=UserNotFoundError,
            expected_message="User not found.",
            username="invalid"
        )
        
        # Finding users
        users = JiraAPI.UserApi.find_users(search_string="test@example.com")
        self.assertEqual(len(users), 1)

        # Test empty username raises ValueError
        self.assert_error_behavior(
            func_to_call=JiraAPI.UserApi.find_users,
            expected_exception_type=ValueError,
            expected_message="search_string cannot be empty.",
            search_string=""
        )
        
        # Test other input validation errors
        self.assert_error_behavior(
            func_to_call=JiraAPI.UserApi.find_users,
            expected_exception_type=ValueError,
            expected_message="startAt must be a non-negative integer.",
            search_string="test@example.com", 
            startAt=-1
        )
        
        self.assert_error_behavior(
            func_to_call=JiraAPI.UserApi.find_users,
            expected_exception_type=ValueError,
            expected_message="maxResults must be a positive integer.",
            search_string="test@example.com", 
            maxResults=0
        )

        inactive_users = JiraAPI.UserApi.find_users(
            search_string="test@example.com",
            startAt=0,
            maxResults=1,
            includeActive=False,
            includeInactive=True,
        )
        self.assertEqual(len(inactive_users), 0)

        # Delete
        del_resp = JiraAPI.UserApi.delete_user(username="tester")
        self.assertIn("deleted", del_resp)

        self.assertIn("error", JiraAPI.UserApi.delete_user(username="tester"))
        # Missing username
        self.assertIn("error", JiraAPI.UserApi.delete_user(""))


    def test_user_duplicate_key(self):
        """Test creating a user with a duplicate key."""
        payload = {
            "name": "tester",
            "emailAddress": "test@example.com",
            "displayName": "Test User",
        }
        # Create a duplicate UUID string that is already in DB.
        duplicate_uuid = uuid.UUID("12345678-1234-5678-1234-567812345678")
        # Pre-populate the DB with the duplicate key.
        DB["users"][str(duplicate_uuid)] = {
            "name": "tester2",
            "emailAddress": "test2@example.com",
            "displayName": "Test User 2",
        }
        # Define a unique UUID to be returned on the second call.
        unique_uuid = uuid.UUID("87654321-4321-8765-4321-876543218765")

        # Use patch to simulate uuid.uuid4 collisions.
        with patch("uuid.uuid4", side_effect=[duplicate_uuid, unique_uuid]):
            result = JiraAPI.UserApi.create_user(payload)
            self.assertTrue(result.get("created"))
            user = result["user"]
            # The returned user key should be the second (unique) UUID.
            self.assertEqual(user["key"], str(unique_uuid))
            # Ensure the DB now has two entries: the pre-existing one and the new one.
            self.assertEqual(len(DB["users"]), 2)

    def test_user_avatars_api(self):
        """Test user avatars retrieval."""
        # Create a user avatar
        JiraAPI.AvatarApi.upload_avatar(filetype="user", filename="avatar1.png")
        # Get
        av = JiraAPI.UserAvatarsApi.get_user_avatars(username="someone")
        self.assertIn("avatars", av)
        self.assertEqual(len(av["avatars"]), 1)

        self.assertIn("error", JiraAPI.UserAvatarsApi.get_user_avatars(username=""))

    def test_version_api(self):
        """Test version API."""

        del DB["versions"]
        self.assertNotIn("versions", DB)
        DB["versions"] = {}
        self.assertIn("error", JiraAPI.VersionApi.get_version("V1"))

        del DB["versions"]
        self.assertNotIn("versions", DB)
        DB["versions"] = {}
        # Create a version using the new flattened method
        created = JiraAPI.VersionApi.create_version(
            name="Version 1",
            description="An excellent version",
            archived=False,
            released=True,
            release_date="2010-07-06",
            user_release_date="6/Jul/2010",
            project="PXA",
            project_id=10000,
        )
        self.assertIn("created", created)
        self.assertTrue(created["created"])
        self.assertIn("version", created)
        version = created["version"]
        self.assertEqual(version["name"], "Version 1")
        self.assertEqual(version["description"], "An excellent version")
        self.assertEqual(version["archived"], False)
        self.assertEqual(version["released"], True)
        self.assertEqual(version["releaseDate"], "2010-07-06")
        self.assertEqual(version["userReleaseDate"], "6/Jul/2010")
        self.assertEqual(version["project"], "PXA")
        self.assertEqual(version["projectId"], 10000)

        self.assertIn(
            "error",
            JiraAPI.VersionApi.create_version(
                description="An excellent version",
                archived=False,
                released=True,
                release_date="2010-07-06",
            ),
        )
        # Get version
        v1 = JiraAPI.VersionApi.get_version(version["id"])
        self.assertEqual(v1["name"], "Version 1")

        # Test non-existent version
        self.assertIn("error", JiraAPI.VersionApi.get_version("V2"))

        # Test related issue counts
        counts = JiraAPI.VersionApi.get_version_related_issue_counts(version["id"])
        self.assertIn("fixCount", counts)
        self.assertIn("affectedCount", counts)

        # Test delete version
        del_resp = JiraAPI.VersionApi.delete_version(version["id"])
        self.assertIn("deleted", del_resp)

        del DB["versions"]
        self.assertNotIn("versions", DB)

        self.assertIn("error", JiraAPI.VersionApi.delete_version(version["id"]))

    def test_workflow_api(self):
        """Test workflow retrieval."""
        # Add workflow data to DB
        DB["workflows"]["WF1"] = {"id": "WF1", "name": "Simple Workflow"}

        # Get all workflows
        wfs = JiraAPI.WorkflowApi.get_workflows()
        self.assertIn("workflows", wfs)
        self.assertEqual(len(wfs["workflows"]), 1)
        self.assertEqual(wfs["workflows"][0]["name"], "Simple Workflow")

    def test_security_level_api(self):
        """Test security level API."""
        # Add security level data to DB
        DB["security_levels"]["SEC1"] = {"id": "SEC1", "name": "Top Secret"}

        # Get all security levels
        all_lvls = JiraAPI.SecurityLevelApi.get_security_levels()
        self.assertIn("securityLevels", all_lvls)
        self.assertEqual(len(all_lvls["securityLevels"]), 1)
        self.assertEqual(all_lvls["securityLevels"][0]["name"], "Top Secret")

        # Get one security level
        one_lvl = JiraAPI.SecurityLevelApi.get_security_level("SEC1")
        self.assertEqual(one_lvl["name"], "Top Secret")

        # Test non-existent security level
        self.assertIn("error", JiraAPI.SecurityLevelApi.get_security_level("SEC2"))

    def test_valid_user_creation(self):
        """Test successful user creation with a valid payload."""
        valid_payload = {
            "name": "charlie_valid",
            "emailAddress": "charlie_valid@example.com",
            "displayName": "Charlie Valid"
        }
        result = create_user(payload=valid_payload)

        self.assertTrue(result.get("created"), "User creation flag should be true.")
        self.assertIn("user", result, "Result should contain user data.")
        user_data = result["user"]
        self.assertEqual(user_data["name"], "charlie_valid")
        self.assertEqual(user_data["emailAddress"], "charlie_valid@example.com")
        self.assertEqual(user_data["displayName"], "Charlie Valid")
        self.assertTrue(user_data["active"], "User should be active by default.")
        self.assertIn(user_data["key"], DB["users"], "User should be added to the DB.")

    def test_valid_user_creation_with_additional_fields_in_payload(self):
        """Test user creation with valid payload that includes additional, optional fields."""
        payload_with_extras = {
            "name": "charlie_extra",
            "emailAddress": "charlie_extra@example.com",
            "displayName": "Charlie Extra",
            "profile": {"bio": "A test user with a bio"},
            "groups": ["testers", "beta_users"],
            "settings": {"theme": "dark"}
        }
        result = create_user(payload=payload_with_extras)

        self.assertTrue(result.get("created"))
        user_data = result["user"]
        self.assertEqual(user_data["name"], "charlie_extra")
        self.assertEqual(user_data["profile"]["bio"], "A test user with a bio")
        self.assertEqual(user_data["groups"], ["testers", "beta_users"])
        self.assertEqual(user_data["settings"]["theme"], "dark")
        self.assertIn(user_data["key"], DB["users"])

    def test_payload_not_a_dict_raises_typeerror(self):
        """Test that providing a non-dictionary payload (e.g., a string) raises TypeError."""
        self.assert_error_behavior(
            func_to_call=create_user,
            expected_exception_type=TypeError,
            expected_message="Expected payload to be a dict, got str",
            payload="this is not a dictionary"  # type: ignore
        )

    def test_payload_is_none_raises_typeerror(self):
        """Test that providing None as payload raises TypeError."""
        self.assert_error_behavior(
            func_to_call=create_user,
            expected_exception_type=TypeError,
            expected_message="Expected payload to be a dict, got NoneType",
            payload=None  # type: ignore
        )

    def test_payload_missing_name_raises_validationerror(self):
        """Test payload missing the required 'name' field raises ValidationError."""
        invalid_payload = {
            # "name": "missing",
            "emailAddress": "test@example.com",
            "displayName": "Test User Incomplete"
        }
        self.assert_error_behavior(
            func_to_call=create_user,
            expected_exception_type=ValidationError,
            expected_message="Field required",
            payload=invalid_payload
        )

    def test_payload_missing_email_raises_validationerror(self):
        """Test payload missing the required 'emailAddress' field raises ValidationError."""
        invalid_payload = {
            "name": "Test User NoEmail",
            # "emailAddress": "missing@example.com",
            "displayName": "Test User Incomplete"
        }
        self.assert_error_behavior(
            func_to_call=create_user,
            expected_exception_type=ValidationError,
            expected_message="Field required",
            payload=invalid_payload
        )

    def test_payload_missing_display_name_raises_validationerror(self):
        """Test payload missing the required 'displayName' field raises ValidationError."""
        invalid_payload = {
            "name": "Test User NoDisplayName",
            "emailAddress": "test@example.com",
            # "displayName": "missing"
        }
        self.assert_error_behavior(
            func_to_call=create_user,
            expected_exception_type=ValidationError,
            expected_message="Field required",
            payload=invalid_payload
        )

    def test_payload_name_incorrect_type_raises_validationerror(self):
        """Test payload with 'name' of an incorrect type (e.g., int) raises ValidationError."""
        invalid_payload = {
            "name": 12345,  # Should be a string
            "emailAddress": "test@example.com",
            "displayName": "Test User BadNameType"
        }
        self.assert_error_behavior(
            func_to_call=create_user,
            expected_exception_type=ValidationError,
            expected_message="Input should be a valid string",
            payload=invalid_payload
        )

    def test_payload_email_incorrect_type_raises_validationerror(self):
        """Test payload with 'emailAddress' of an incorrect type raises ValidationError."""
        invalid_payload = {
            "name": "Test User BadEmailType",
            "emailAddress": 12345,  # Should be a string (specifically, EmailStr)
            "displayName": "Test User"
        }
        self.assert_error_behavior(
            func_to_call=create_user,
            expected_exception_type=ValidationError,
            expected_message="Input should be a valid string",
            payload=invalid_payload
        )

    def test_payload_email_invalid_format_raises_validationerror(self):
        """Test payload with 'emailAddress' having an invalid email format raises ValidationError."""
        invalid_payload = {
            "name": "Test User BadEmailFormat",
            "emailAddress": "not-a-valid-email-address",  # Invalid format
            "displayName": "Test User"
        }
        self.assert_error_behavior(
            func_to_call=create_user,
            expected_exception_type=ValidationError,
            expected_message="value is not a valid email address",
            payload=invalid_payload
        )

    def test_payload_display_name_incorrect_type_raises_validationerror(self):
        """Test payload with 'displayName' of an incorrect type raises ValidationError."""
        invalid_payload = {
            "name": "Test User BadDisplayNameType",
            "emailAddress": "test@example.com",
            "displayName": ["List", "Not", "String"]  # Should be a string
        }
        self.assert_error_behavior(
            func_to_call=create_user,
            expected_exception_type=ValidationError,
            expected_message="Input should be a valid string",
            payload=invalid_payload
        )

    def test_valid_input_no_subtasks_delete_false(self):
        """Test valid input, issue has no subtasks, delete_subtasks=False."""
        result = JiraAPI.IssueApi.delete_issue(issue_id="ISSUE-1", delete_subtasks=False)
        self.assertEqual(result, {"deleted": "ISSUE-1", "deleteSubtasks": False})
        self.assertNotIn("ISSUE-1", DB["issues"])

    def test_valid_input_no_subtasks_delete_true(self):
        """Test valid input, issue has no subtasks, delete_subtasks=True."""
        result = JiraAPI.IssueApi.delete_issue(issue_id="ISSUE-1", delete_subtasks=True)
        self.assertEqual(result, {"deleted": "ISSUE-1", "deleteSubtasks": True})
        self.assertNotIn("ISSUE-1", DB["issues"])

    def test_valid_input_with_subtasks_delete_true(self):
        """Test valid input, issue has subtasks, delete_subtasks=True."""
        result = JiraAPI.IssueApi.delete_issue(issue_id="ISSUE-2", delete_subtasks=True)
        self.assertEqual(result, {"deleted": "ISSUE-2", "deleteSubtasks": True})
        self.assertNotIn("ISSUE-2", DB["issues"])
        self.assertNotIn("SUB-1", DB["issues"])
        self.assertNotIn("SUB-2", DB["issues"])

    def test_valid_input_default_delete_subtasks(self):
        """Test valid input with default delete_subtasks=False (issue has no subtasks)."""
        result = JiraAPI.IssueApi.delete_issue(issue_id="ISSUE-1")  # delete_subtasks defaults to False
        self.assertEqual(result, {"deleted": "ISSUE-1", "deleteSubtasks": False})
        self.assertNotIn("ISSUE-1", DB["issues"])

    def test_invalid_issue_id_type_integer(self):
        """Test that invalid issue_id type (int) raises TypeError."""
        self.assert_error_behavior(
            func_to_call=JiraAPI.IssueApi.delete_issue,
            expected_exception_type=TypeError,
            expected_message="issue_id must be a string, got int",
            issue_id=123,
            delete_subtasks=False
        )

    def test_invalid_issue_id_type_none(self):
        """Test that invalid issue_id type (None) raises TypeError."""
        self.assert_error_behavior(
            func_to_call=JiraAPI.IssueApi.delete_issue,
            expected_exception_type=TypeError,
            expected_message="issue_id must be a string, got NoneType",
            issue_id=None,
            delete_subtasks=False
        )

    def test_invalid_delete_subtasks_type_string(self):
        """Test that invalid delete_subtasks type (str) raises TypeError."""
        self.assert_error_behavior(
            func_to_call=JiraAPI.IssueApi.delete_issue,
            expected_exception_type=TypeError,
            expected_message="delete_subtasks must be a boolean, got str",
            issue_id="ISSUE-1",
            delete_subtasks="False"  # String "False", not boolean False
        )

    def test_invalid_delete_subtasks_type_integer(self):
        """Test that invalid delete_subtasks type (int) raises TypeError."""
        self.assert_error_behavior(
            func_to_call=JiraAPI.IssueApi.delete_issue,
            expected_exception_type=TypeError,
            expected_message="delete_subtasks must be a boolean, got int",
            issue_id="ISSUE-1",
            delete_subtasks=0
        )

    def test_issue_with_subtasks_delete_false_raises_error(self):
        """Test that attempting to delete an issue with subtasks without delete_subtasks=True raises ValueError."""
        self.assert_error_behavior(
            func_to_call=JiraAPI.IssueApi.delete_issue,
            expected_exception_type=ValueError,
            expected_message="Subtasks exist, cannot delete issue. Set delete_subtasks=True to delete them.",
            issue_id="ISSUE-2",
            delete_subtasks=False
        )

    def test_delete_non_existent_issue_raises_error(self):
        """Test that attempting to delete a non-existent issue raises ValueError."""
        self.assert_error_behavior(
            func_to_call=JiraAPI.IssueApi.delete_issue,
            expected_exception_type=ValueError,
            expected_message="Issue with id 'NON-EXISTENT' does not exist.",
            issue_id="NON-EXISTENT"
        )

    def test_invalid_project_key_type_integer(self):
        """Test that an integer project_key raises TypeError."""
        self.assert_error_behavior(
            func_to_call=get_project_by_key,
            expected_exception_type=TypeError,
            expected_message="project_key must be a string",
            project_key=123
        )

    def test_invalid_project_key_type_list(self):
        """Test that a list project_key raises TypeError."""
        self.assert_error_behavior(
            func_to_call=get_project_by_key,
            expected_exception_type=TypeError,
            expected_message="project_key must be a string",
            project_key=["KEY"]
        )

    def test_invalid_project_key_type_none(self):
        """Test that a None project_key raises TypeError."""
        self.assert_error_behavior(
            func_to_call=get_project_by_key,
            expected_exception_type=TypeError,
            expected_message="project_key must be a string",
            project_key=None
        )

    def test_get_user_invalid_username_type(self):
        """Test that providing a non-string username raises TypeError."""
        self.assert_error_behavior(
            func_to_call=get_user_by_username_or_account_id,
            expected_exception_type=TypeError,
            expected_message="username must be a string if provided.",
            username=123
        )

    def test_get_user_invalid_account_id_type(self):
        """Test that providing a non-string account_id raises TypeError."""
        self.assert_error_behavior(
            func_to_call=get_user_by_username_or_account_id,
            expected_exception_type=TypeError,
            expected_message="account_id must be a string if provided.",
            account_id=123
        )

    def test_get_user_invalid_username_and_account_id_types(self):
        """Test that TypeError for username is raised first if both types are invalid."""
        self.assert_error_behavior(
            func_to_call=get_user_by_username_or_account_id,
            expected_exception_type=TypeError,
            expected_message="username must be a string if provided.",  # username check comes first
            username=123,
            account_id=456
        )

    def test_get_user_no_identifiers_provided(self):
        """Test that providing neither username nor account_id raises MissingUserIdentifierError."""
        self.assert_error_behavior(
            func_to_call=get_user_by_username_or_account_id,
            expected_exception_type=MissingUserIdentifierError,
            expected_message="Either username or account_id must be provided."
        )

    def test_valid_assignment(self):
        """Test successful issue assignment with valid inputs."""
        issue_id = "existing_issue_1"
        assignee_data = {"name": "new_user"}

        result = assign_issue_to_user(issue_id=issue_id, assignee=assignee_data)

        self.assertTrue(result.get("assigned"))
        self.assertIn("issue", result)
        self.assertEqual(result["issue"]["fields"]["assignee"], {"name": "new_user"})
        self.assertEqual(DB["issues"][issue_id]["fields"]["assignee"], {"name": "new_user"})

    def test_invalid_issue_id_type_int(self):
        """Test that non-string issue_id (int) raises TypeError."""
        self.assert_error_behavior(
            func_to_call=assign_issue_to_user,
            expected_exception_type=TypeError,
            expected_message="issue_id must be a string, got int.",
            issue_id=123,
            assignee="test_user"
        )

    def test_invalid_issue_id_type_none(self):
        """Test that non-string issue_id (None) raises TypeError."""
        self.assert_error_behavior(
            func_to_call=assign_issue_to_user,
            expected_exception_type=TypeError,
            expected_message="issue_id must be a string, got NoneType.",
            issue_id=None,
            assignee="test_user"
        )

    def test_invalid_assignee_type_str(self):
        """Test that non-dict assignee (str) raises TypeError."""
        self.assert_error_behavior(
            func_to_call=assign_issue_to_user,
            expected_exception_type=TypeError,
            expected_message="assignee must be a dictionary, got str.",
            issue_id="issue_1",
            assignee="not_a_string"
        )

    def test_invalid_assignee_type_none(self):
        """Test that non-string assignee (None) raises TypeError."""
        self.assert_error_behavior(
            func_to_call=assign_issue_to_user,
            expected_exception_type=TypeError,
            expected_message="assignee must be a dictionary, got NoneType.",
            issue_id="issue_1",
            assignee=None
        )

    def test_issue_not_found(self):
        """Test original logic for non-existent issue_id (returns error dict)."""
        issue_id = "non_existent_issue"
        assignee_data = {"name": "any_user"}
        self.assert_error_behavior(
            func_to_call=assign_issue_to_user,
            expected_exception_type=ValueError,
            expected_message=f"Issue '{issue_id}' not found.",
            issue_id=issue_id,
            assignee=assignee_data
        )

    def test_issue_id_not_string_raises_type_error(self):
        """Test that non-string issue_id inputs raise TypeError."""
        invalid_inputs_and_types = [
            (123, "int"),
            (None, "NoneType"),
            (True, "bool"),
            ([], "list"),
            ({}, "dict"),
            (1.23, "float")
        ]

        for invalid_input, type_name in invalid_inputs_and_types:
            with self.subTest(input_value=invalid_input, input_type=type_name):
                self.assert_error_behavior(
                    func_to_call=get_issue_by_id,
                    expected_exception_type=TypeError,
                    expected_message=f"issue_id must be a string, but got {type_name}.",
                    issue_id=invalid_input
                )


class TestUpdateIssueById(BaseTestCaseWithErrorHandler):
    """
    Test suite for the refactored 'update_issue_by_id' function.
    """

    def setUp(self):
        """Reset test state (DB) before each test."""
        global DB
        # Define an initial state for the DB for each test
        DB["issues"] = {
            "ISSUE-1": {
                "id": "ISSUE-1",
                "fields": {
                    "project": "PROJ1",
                    "summary": "Original Summary",
                    "description": "Original Description",
                    "priority": "High",
                    "assignee": {"name": "user.alpha"},
                    "issuetype": "Bug"
                }
            },
            "ISSUE-EXISTING-NO-ASSIGNEE": {
                "id": "ISSUE-EXISTING-NO-ASSIGNEE",
                "fields": {
                    "project": "PROJ2",
                    "summary": "Summary for issue with no assignee",
                    "description": "Description here",
                    "priority": "Medium",
                    "issuetype": "Task"
                }
            }
        }
        # Keep a pristine copy to compare against unintended modifications if necessary
        self._original_db_issues_at_setup = copy.deepcopy(DB["issues"])

    def test_valid_full_update(self):
        """Test updating an issue with a full set of valid fields."""
        issue_id = "ISSUE-1"
        update_fields = {
            "summary": "Updated Summary",
            "description": "Updated Description",
            "priority": "Low",
            "assignee": {"name": "user.beta"},
            "issuetype": "Story",
            "project": "PROJ_NEW"
        }
        result = update_issue_by_id(issue_id, fields=update_fields)

        self.assertTrue(result.get("updated"))
        self.assertEqual(result["issue"]["id"], issue_id)
        # Check that all specified fields were updated
        for key, value in update_fields.items():
            self.assertEqual(result["issue"]["fields"][key], value)
        self.assertEqual(DB["issues"][issue_id]["fields"]["summary"], "Updated Summary")

    def test_valid_partial_update(self):
        """Test updating an issue with a partial set of valid fields (e.g., only summary)."""
        issue_id = "ISSUE-1"
        update_fields = {"summary": "Partially Updated Summary"}
        result = update_issue_by_id(issue_id, fields=update_fields)

        self.assertTrue(result.get("updated"))
        self.assertEqual(result["issue"]["fields"]["summary"], "Partially Updated Summary")
        # Ensure other fields remained unchanged
        self.assertEqual(result["issue"]["fields"]["description"],
                         self._original_db_issues_at_setup[issue_id]["fields"]["description"])
        self.assertEqual(DB["issues"][issue_id]["fields"]["description"], "Original Description")

    def test_valid_update_with_assignee_set_to_none_implicitly(self):
        """Test updating an issue where assignee is not provided in fields (should remain unchanged)."""
        issue_id = "ISSUE-1"  # This issue initially has an assignee
        update_fields = {"summary": "Summary Update, No Assignee Change"}
        result = update_issue_by_id(issue_id, fields=update_fields)

        self.assertTrue(result.get("updated"))
        self.assertEqual(result["issue"]["fields"]["summary"], "Summary Update, No Assignee Change")
        self.assertIn("assignee", result["issue"]["fields"])  # Assignee should still be there
        self.assertEqual(result["issue"]["fields"]["assignee"]["name"], "user.alpha")

    def test_valid_update_setting_assignee_to_new_value(self):
        """Test explicitly updating the assignee."""
        issue_id = "ISSUE-1"
        update_fields = {"assignee": {"name": "user.gamma"}}
        result = update_issue_by_id(issue_id, fields=update_fields)

        self.assertTrue(result.get("updated"))
        self.assertEqual(result["issue"]["fields"]["assignee"]["name"], "user.gamma")

    def test_valid_update_setting_assignee_on_issue_with_no_initial_assignee(self):
        """Test setting an assignee on an issue that initially had none."""
        issue_id = "ISSUE-EXISTING-NO-ASSIGNEE"
        update_fields = {"assignee": {"name": "new.assignee"}}
        result = update_issue_by_id(issue_id, fields=update_fields)

        self.assertTrue(result.get("updated"))
        self.assertEqual(result["issue"]["fields"]["assignee"]["name"], "new.assignee")

    def test_valid_update_with_fields_as_none(self):
        """Test calling update with fields=None (should not change any fields)."""
        issue_id = "ISSUE-1"
        original_fields = copy.deepcopy(DB["issues"][issue_id]["fields"])
        result = update_issue_by_id(issue_id, fields=None)

        self.assertTrue(result.get("updated"))
        self.assertEqual(result["issue"]["fields"], original_fields)  # No changes
        self.assertEqual(DB["issues"][issue_id]["fields"], original_fields)

    def test_valid_update_with_empty_fields_dict(self):
        """Test calling update with fields={} (should not change any fields)."""
        issue_id = "ISSUE-1"
        original_fields = copy.deepcopy(DB["issues"][issue_id]["fields"])
        result = update_issue_by_id(issue_id, fields={})

        self.assertTrue(result.get("updated"))
        self.assertEqual(result["issue"]["fields"], original_fields)  # No changes
        self.assertEqual(DB["issues"][issue_id]["fields"], original_fields)

    def test_invalid_issue_id_type(self):
        """Test providing a non-string issue_id raises TypeError."""
        self.assert_error_behavior(
            func_to_call=update_issue_by_id,
            expected_exception_type=TypeError,
            expected_message="Argument 'issue_id' must be a string.",
            issue_id=12345,  # Invalid type
            fields={"summary": "Test"}
        )

    def test_invalid_fields_type_not_dict(self):
        """Test providing non-dict for 'fields' (when not None) raises TypeError."""
        self.assert_error_behavior(
            func_to_call=update_issue_by_id,
            expected_exception_type=TypeError,
            expected_message="Argument 'fields' must be a dictionary or None.",
            issue_id="ISSUE-1",
            fields="not-a-dictionary"  # Invalid type
        )

    def test_issue_not_found(self):
        """Test updating a non-existent issue returns an error dictionary."""
        non_existent_issue_id = "NON-EXISTENT-ISSUE"

        self.assert_error_behavior(
            func_to_call=update_issue_by_id,
            expected_exception_type=ValueError,
            expected_message=f"Issue '{non_existent_issue_id}' not found.",
            issue_id=non_existent_issue_id,
            fields={"summary": "Test"}
        )

    def test_valid_project_creation(self):
        """Test successful creation of a new project."""
        result = create_project(proj_key="PROJ1", proj_name="Project One")
        self.assertTrue(result.get("created"))
        self.assertIn("project", result)
        self.assertEqual(result["project"]["key"], "PROJ1")
        self.assertEqual(result["project"]["name"], "Project One")
        self.assertIn("PROJ1", DB["projects"])

    def test_invalid_proj_key_type_integer(self):
        """Test that TypeError is raised if proj_key is not a string (e.g., integer)."""
        self.assert_error_behavior(
            func_to_call=create_project,
            expected_exception_type=TypeError,
            expected_message="Project key (proj_key) must be a string.",
            proj_key=123,
            proj_name="Project Name"
        )

    def test_invalid_proj_key_type_none(self):
        """Test that TypeError is raised if proj_key is None."""
        self.assert_error_behavior(
            func_to_call=create_project,
            expected_exception_type=TypeError,
            expected_message="Project key (proj_key) must be a string.",
            proj_key=None,
            proj_name="Project Name"
        )

    def test_empty_proj_key(self):
        """Test that ProjectInputError is raised if proj_key is an empty string."""
        self.assert_error_behavior(
            func_to_call=create_project,
            expected_exception_type=ProjectInputError,
            expected_message="Project key (proj_key) cannot be empty.",
            proj_key="",
            proj_name="Project Name"
        )

    def test_invalid_proj_name_type_integer(self):
        """Test that TypeError is raised if proj_name is not a string (e.g., integer)."""
        self.assert_error_behavior(
            func_to_call=create_project,
            expected_exception_type=TypeError,
            expected_message="Project name (proj_name) must be a string.",
            proj_key="PROJ1",
            proj_name=123
        )

    def test_invalid_proj_name_type_none(self):
        """Test that TypeError is raised if proj_name is None."""
        self.assert_error_behavior(
            func_to_call=create_project,
            expected_exception_type=TypeError,
            expected_message="Project name (proj_name) must be a string.",
            proj_key="PROJ1",
            proj_name=None
        )

    def test_empty_proj_name(self):
        """Test that ProjectInputError is raised if proj_name is an empty string."""
        self.assert_error_behavior(
            func_to_call=create_project,
            expected_exception_type=ProjectInputError,
            expected_message="Project name (proj_name) cannot be empty.",
            proj_key="PROJ1",
            proj_name=""
        )

    def test_valid_project_creation_with_lead(self):
        """Test successful creation of a new project with a lead."""
        DB["users"]["jdoe"] = {
            "name": "jdoe",
            "key": "jdoe",
            "emailAddress": "jdoe@example.com",
            "displayName": "John Doe"
        }
        result = create_project(proj_key="PROJTEST", proj_name="Project One", proj_lead="jdoe")
        self.assertTrue(result.get("created"))
        self.assertIn("project", result)
        self.assertEqual(result["project"]["key"], "PROJTEST")
        self.assertEqual(result["project"]["name"], "Project One")
        self.assertEqual(result["project"]["lead"], "jdoe")
        self.assertIn("PROJTEST", DB["projects"])

    def test_invalid_proj_lead_type_integer(self):
        """Test that TypeError is raised if proj_lead is not a string (e.g., integer)."""
        self.assert_error_behavior(
            func_to_call=create_project,
            expected_exception_type=TypeError,
            expected_message="Project lead (proj_lead) must be a string.",
            proj_key="PROJ1",
            proj_name="Project Name",
            proj_lead=123
        )

    def test_empty_proj_lead(self):
        """Test that ProjectInputError is raised if proj_lead is an empty string."""
        self.assert_error_behavior(
            func_to_call=create_project,
            expected_exception_type=ProjectInputError,
            expected_message="Project lead (proj_lead) cannot be empty.",
            proj_key="PROJ1",
            proj_name="Project Name",
            proj_lead=""
        )

    def test_invalid_proj_lead_user_not_found(self):
        """Test that UserNotFoundError is raised if proj_lead is not a valid user."""
        self.assert_error_behavior(
            func_to_call=create_project,
            expected_exception_type=UserNotFoundError,
            expected_message="Project lead 'jdoe' does not exist.",
            proj_key="PROJ1",
            proj_name="Project Name",
            proj_lead="jdoe"
        )

    def test_project_already_exists(self):
        """Test that ProjectAlreadyExistsError is raised if the project key already exists."""
        # Pre-populate DB
        DB["projects"]["EXISTING_PROJ"] = {"key": "EXISTING_PROJ", "name": "Existing Project"}

        self.assert_error_behavior(
            func_to_call=create_project,
            expected_exception_type=ProjectAlreadyExistsError,
            expected_message="Project 'EXISTING_PROJ' already exists.",
            proj_key="EXISTING_PROJ",
            proj_name="New Name For Existing Project"
        )

    def test_db_state_after_successful_creation(self):
        """Test that the DB state is correctly updated after a successful creation."""
        create_project(proj_key="DB_TEST_PROJ", proj_name="DB Test Project")
        self.assertIn("DB_TEST_PROJ", DB["projects"])
        self.assertEqual(DB["projects"]["DB_TEST_PROJ"]["name"], "DB Test Project")

    def test_multiple_creations(self):
        """Test creating multiple different projects."""
        result1 = create_project(proj_key="MULTI1", proj_name="Multi Project 1")
        self.assertTrue(result1.get("created"))

        result2 = create_project(proj_key="MULTI2", proj_name="Multi Project 2")
        self.assertTrue(result2.get("created"))

        self.assertIn("MULTI1", DB["projects"])
        self.assertIn("MULTI2", DB["projects"])
        

    def test_valid_input_standard_type(self):
        """Test that valid input for a standard issue type is accepted."""
        result = create_issue_type(name="Bug", description="A software defect", type="standard")
        self.assertIsInstance(result, dict)
        self.assertTrue(result.get("created"))
        self.assertIn("issueType", result)
        issue_type = result["issueType"]
        self.assertEqual(issue_type["name"], "Bug")
        self.assertEqual(issue_type["description"], "A software defect")
        self.assertFalse(issue_type["subtask"])
        self.assertIn(issue_type["id"], DB["issue_types"])

    def test_valid_input_subtask_type(self):
        """Test that valid input for a subtask issue type is accepted."""
        result = create_issue_type(name="Sub-Task", description="A smaller piece of work", type="subtask")
        self.assertTrue(result.get("created"))
        issue_type = result["issueType"]
        self.assertEqual(issue_type["name"], "Sub-Task")
        self.assertTrue(issue_type["subtask"])

    def test_valid_input_default_type(self):
        """Test that valid input with default type ('standard') is accepted."""
        result = create_issue_type(name="Task", description="A standard task")
        self.assertTrue(result.get("created"))
        issue_type = result["issueType"]
        self.assertEqual(issue_type["name"], "Task")
        self.assertFalse(issue_type["subtask"]) # Default type is "standard"

    # --- Type Validation Tests ---
    def test_invalid_name_type_int(self):
        """Test that non-string 'name' (int) raises TypeError."""
        self.assert_error_behavior(
            func_to_call=create_issue_type,
            expected_exception_type=TypeError,
            expected_message="Argument 'name' must be a string, not int.",
            name=123,
            description="Valid description"
        )

    def test_invalid_name_type_none(self):
        """Test that non-string 'name' (None) raises TypeError."""
        self.assert_error_behavior(
            func_to_call=create_issue_type,
            expected_exception_type=TypeError,
            expected_message="Argument 'name' must be a string, not NoneType.",
            name=None,
            description="Valid description"
        )

    def test_invalid_description_type_list(self):
        """Test that non-string 'description' (list) raises TypeError."""
        self.assert_error_behavior(
            func_to_call=create_issue_type,
            expected_exception_type=TypeError,
            expected_message="Argument 'description' must be a string, not list.",
            name="Valid Name",
            description=["Not", "a", "string"]
        )

    def test_invalid_type_argument_type_bool(self):
        """Test that non-string 'type' argument (bool) raises TypeError."""
        self.assert_error_behavior(
            func_to_call=create_issue_type,
            expected_exception_type=TypeError,
            expected_message="Argument 'type' must be a string, not bool.",
            name="Valid Name",
            description="Valid description",
            type=True
        )

    # --- Empty Field Validation Tests (EmptyFieldError) ---
    def test_empty_name(self):
        """Test that empty 'name' raises EmptyFieldError."""
        self.assert_error_behavior(
            func_to_call=create_issue_type,
            expected_exception_type=EmptyFieldError,
            expected_message="Argument 'name' cannot be empty.",
            name="",
            description="Valid description"
        )

    def test_empty_description(self):
        """Test that empty 'description' raises EmptyFieldError."""
        self.assert_error_behavior(
            func_to_call=create_issue_type,
            expected_exception_type=EmptyFieldError,
            expected_message="Argument 'description' cannot be empty.",
            name="Valid Name",
            description=""
        )
    
    def test_empty_name_takes_precedence_over_empty_description(self):
        """Test that empty 'name' error is raised before checking empty 'description'."""
        self.assert_error_behavior(
            func_to_call=create_issue_type,
            expected_exception_type=EmptyFieldError,
            expected_message="Argument 'name' cannot be empty.",
            name="",
            description=""
        )

    # --- Core Logic Interaction (Post-Validation) ---
    def test_multiple_creations_increment_id(self):
        """Test that multiple creations result in unique IDs and are stored."""
        result1 = create_issue_type(name="Task 1", description="First task")
        self.assertTrue(result1.get("created"))
        id1 = result1["issueType"]["id"]
        
        result2 = create_issue_type(name="Task 2", description="Second task")
        self.assertTrue(result2.get("created"))
        id2 = result2["issueType"]["id"]
        
        self.assertNotEqual(id1, id2)
        self.assertIn(id1, DB["issue_types"])
        self.assertIn(id2, DB["issue_types"])
        self.assertEqual(len(DB["issue_types"]), 2)


# ================================


    def test_invalid_comp_id_type(self):
        """Test that invalid comp_id type raises TypeError."""
        self.assert_error_behavior(
            func_to_call=update_component_by_id,
            expected_exception_type=TypeError,
            expected_message="comp_id must be a string.",
            comp_id=123, # type: ignore
            name="Test Name"
        )

    def test_invalid_name_type(self):
        """Test that invalid name type raises TypeError."""
        self.assert_error_behavior(
            func_to_call=update_component_by_id,
            expected_exception_type=TypeError,
            expected_message="name must be a string if provided.",
            comp_id="comp123",
            name=12345 # type: ignore
        )

    def test_invalid_description_type(self):
        """Test that invalid description type raises TypeError."""
        self.assert_error_behavior(
            func_to_call=update_component_by_id,
            expected_exception_type=TypeError,
            expected_message="description must be a string if provided.",
            comp_id="comp123",
            description=False # type: ignore
        )

    def test_missing_name_and_description(self):
        """Test that providing neither name nor description raises MissingUpdateDataError."""
        self.assert_error_behavior(
            func_to_call=update_component_by_id,
            expected_exception_type=MissingUpdateDataError,
            expected_message="At least one of name or description must be provided for update.",
            comp_id="comp123"
        )

    def test_valid_string_query_matches_id(self):
        """Test that a valid string query matching an issue ID (case-insensitive) returns the issue."""
        # Add test data to the database
        DB["issues"] = {
            "ISSUE-1": {"fields": {"summary": "Test Summary"}},
            "ISSUE-2": {"fields": {"summary": "Another Issue"}},
            "PROJ-123": {"fields": {"summary": "Project Alpha Task"}},
            "BUG-456": {"fields": {"summary": "Critical Bug"}},
            "feat-007": {"fields": {"summary": "New Feature"}}
        }
        
        result = search_issues_for_picker(query="issue-1")
        self.assertIsInstance(result, dict)
        self.assertIn("issues", result)
        self.assertEqual(result["issues"], ["ISSUE-1"])

    def test_valid_string_query_matches_summary(self):
        """Test that a valid string query matching a summary (case-insensitive) returns the issue."""
        # Add test data to the database
        DB["issues"] = {
            "ISSUE-1": {"fields": {"summary": "Test Summary"}},
            "ISSUE-2": {"fields": {"summary": "Another Issue"}},
            "PROJ-123": {"fields": {"summary": "Project Alpha Task"}},
            "BUG-456": {"fields": {"summary": "Critical Bug"}},
            "feat-007": {"fields": {"summary": "New Feature"}}
        }
        
        result = search_issues_for_picker(query="project alpha")
        self.assertIsInstance(result, dict)
        self.assertIn("issues", result)
        self.assertEqual(result["issues"], ["PROJ-123"])

    def test_valid_string_query_matches_multiple(self):
        """Test that a query matching multiple issues returns all of them."""
        # Add test data to the database
        DB["issues"] = {
            "ISSUE-1": {"fields": {"summary": "Test Summary"}},
            "ISSUE-2": {"fields": {"summary": "Another Issue"}},
            "PROJ-123": {"fields": {"summary": "Project Alpha Task"}},
            "BUG-456": {"fields": {"summary": "Critical Bug"}},
            "feat-007": {"fields": {"summary": "New Feature"}}
        }
        
        result = search_issues_for_picker(query="issue")
        self.assertIsInstance(result, dict)
        self.assertIn("issues", result)
        self.assertCountEqual(result["issues"], ["ISSUE-1", "ISSUE-2"]) # Order may vary

    def test_valid_string_query_no_matches(self):
        """Test that a valid query with no matches returns an empty list."""
        # Add test data to the database
        DB["issues"] = {
            "ISSUE-1": {"fields": {"summary": "Test Summary"}},
            "ISSUE-2": {"fields": {"summary": "Another Issue"}},
            "PROJ-123": {"fields": {"summary": "Project Alpha Task"}},
            "BUG-456": {"fields": {"summary": "Critical Bug"}},
            "feat-007": {"fields": {"summary": "New Feature"}}
        }
        
        result = search_issues_for_picker(query="nonexistent_string_xyz")
        self.assertIsInstance(result, dict)
        self.assertIn("issues", result)
        self.assertEqual(result["issues"], [])

    def test_none_query(self):
        """Test that a None query is accepted and results in no matches."""
        # Add test data to the database
        DB["issues"] = {
            "ISSUE-1": {"fields": {"summary": "Test Summary"}},
            "ISSUE-2": {"fields": {"summary": "Another Issue"}},
            "PROJ-123": {"fields": {"summary": "Project Alpha Task"}},
            "BUG-456": {"fields": {"summary": "Critical Bug"}},
            "feat-007": {"fields": {"summary": "New Feature"}}
        }
        
        result = search_issues_for_picker(query=None)
        self.assertIsInstance(result, dict)
        self.assertIn("issues", result)
        self.assertEqual(result["issues"], [])

    def test_empty_string_query(self):
        """Test that an empty string query matches all issues."""
        # Add test data to the database
        DB["issues"] = {
            "ISSUE-1": {"fields": {"summary": "Test Summary"}},
            "ISSUE-2": {"fields": {"summary": "Another Issue"}},
            "PROJ-123": {"fields": {"summary": "Project Alpha Task"}},
            "BUG-456": {"fields": {"summary": "Critical Bug"}},
            "feat-007": {"fields": {"summary": "New Feature"}}
        }
        
        result = search_issues_for_picker(query="")
        self.assertIsInstance(result, dict)
        self.assertIn("issues", result)
        self.assertCountEqual(result["issues"], ["ISSUE-1", "ISSUE-2", "PROJ-123", "BUG-456", "feat-007"])

    def test_invalid_query_type_int(self):
        """Test that an integer query raises TypeError."""
        self.assert_error_behavior(
            func_to_call=search_issues_for_picker,
            expected_exception_type=TypeError,
            expected_message="Query must be a string or None, but got int.",
            query=123
        )

    def test_invalid_query_type_list(self):
        """Test that a list query raises TypeError."""
        self.assert_error_behavior(
            func_to_call=search_issues_for_picker,
            expected_exception_type=TypeError,
            expected_message="Query must be a string or None, but got list.",
            query=[]
        )

    def test_invalid_query_type_dict(self):
        """Test that a dict query raises TypeError."""
        self.assert_error_behavior(
            func_to_call=search_issues_for_picker,
            expected_exception_type=TypeError,
            expected_message="Query must be a string or None, but got dict.",
            query={"search": "term"}
        )

    def test_db_issues_missing(self):
        """Test behavior when DB['issues'] is missing (should return empty matches)."""
        global DB
        original_db_issues = DB.pop("issues", None)
        try:
            result = search_issues_for_picker(query="test")
            self.assertEqual(result["issues"], [])
        finally:
            if original_db_issues is not None:
                DB["issues"] = original_db_issues # Restore

    def test_db_issues_not_a_dict(self):
        """Test behavior when DB['issues'] is not a dictionary."""
        global DB
        original_db_issues = DB.get("issues")
        DB["issues"] = "not a dict"
        try:
            result = search_issues_for_picker(query="test")
            self.assertEqual(result["issues"], [])
        finally:
            DB["issues"] = original_db_issues # Restore


    def test_invalid_comp_id_type_integer(self):
        """Test that an integer comp_id raises TypeError."""
        invalid_id = 12345
        self.assert_error_behavior(
            func_to_call=get_component_by_id,
            expected_exception_type=TypeError,
            expected_message=f"comp_id must be a string, got {type(invalid_id).__name__}.",
            comp_id=invalid_id
        )

    def test_invalid_comp_id_type_none(self):
        """Test that a None comp_id raises TypeError."""
        invalid_id = None
        self.assert_error_behavior(
            func_to_call=get_component_by_id,
            expected_exception_type=TypeError,
            expected_message=f"comp_id must be a string, got {type(invalid_id).__name__}.",
            comp_id=invalid_id
        )

    def test_invalid_comp_id_type_list(self):
        """Test that a list comp_id raises TypeError."""
        invalid_id = ["id1"]
        self.assert_error_behavior(
            func_to_call=get_component_by_id,
            expected_exception_type=TypeError,
            expected_message=f"comp_id must be a string, got {type(invalid_id).__name__}.",
            comp_id=invalid_id
        )

        
        
# ================================================

    def test_invalid_project_key_type_integer(self):
        """Test that an integer project_key raises TypeError."""
        self.assert_error_behavior(
            func_to_call=get_project_components_by_key,
            expected_exception_type=TypeError,
            expected_message="project_key must be a string, but got int.",
            project_key=123
        )

    def test_invalid_project_key_type_none(self):
        """Test that a None project_key raises TypeError."""
        self.assert_error_behavior(
            func_to_call=get_project_components_by_key,
            expected_exception_type=TypeError,
            expected_message="project_key must be a string, but got NoneType.",
            project_key=None
        )

    def test_invalid_project_key_type_list(self):
        """Test that a list project_key raises TypeError."""
        self.assert_error_behavior(
            func_to_call=get_project_components_by_key,
            expected_exception_type=TypeError,
            expected_message="project_key must be a string, but got list.",
            project_key=["PROJ1"]
        )


# ================================================


    def test_invalid_project_type(self):
        """Test that providing a non-string project raises TypeError."""
        self.assert_error_behavior(
            func_to_call=create_project_component,
            expected_exception_type=TypeError,
            expected_message="Argument 'project' must be a string.",
            project=123, # type: ignore
            name="TestComponent"
        )

    def test_invalid_name_type(self):
        """Test that providing a non-string name raises TypeError."""
        self.assert_error_behavior(
            func_to_call=create_project_component,
            expected_exception_type=TypeError,
            expected_message="Argument 'name' must be a string.",
            project="PRJ1",
            name=False # type: ignore
        )

    def test_invalid_description_type(self):
        """Test that providing a non-string, non-None description raises TypeError."""
        self.assert_error_behavior(
            func_to_call=create_project_component,
            expected_exception_type=TypeError,
            expected_message="Argument 'description' must be a string or None.",
            project="PRJ1",
            name="TestComponent",
            description=123 # type: ignore
        )

    def test_empty_project_string(self):
        """Test that an empty project string raises EmptyInputError."""
        self.assert_error_behavior(
            func_to_call=create_project_component,
            expected_exception_type=EmptyInputError,
            expected_message="Argument 'project' cannot be empty.",
            project="",
            name="TestComponent"
        )

    def test_empty_name_string(self):
        """Test that an empty name string raises EmptyInputError."""
        self.assert_error_behavior(
            func_to_call=create_project_component,
            expected_exception_type=EmptyInputError,
            expected_message="Argument 'name' cannot be empty.",
            project="PRJ1",
            name=""
        )

    def test_project_not_found(self):
        """Test that a non-existent project key raises ProjectNotFoundError."""
        self.assert_error_behavior(
            func_to_call=create_project_component,
            expected_exception_type=ProjectNotFoundError,
            expected_message="Project 'UNKNOWN_PRJ' not found.",
            project="UNKNOWN_PRJ",
            name="TestComponent"
        )

    def test_payload_not_a_dict_raises_typeerror(self):
        """Test that providing a non-dictionary payload (e.g., a string) raises TypeError."""
        self.assert_error_behavior(
            func_to_call=create_user,
            expected_exception_type=TypeError,
            expected_message="Expected payload to be a dict, got str",
            payload="not-a-dict" # type: ignore
        )

    def test_create_user_with_all_optional_fields(self):
        """Test user creation with a payload containing all optional fields."""
        payload = {
            "name": "charlie_extra",
            "emailAddress": "charlie_extra@example.com",
            "displayName": "Charlie Extra",
            "profile": {"bio": "A test user with a bio", "joined": "2024-01-01"},
            "groups": ["testers", "beta_users"],
            "drafts": [{"id": "d1", "subject": "S1", "body": "B1", "timestamp": "T1"}],
            "messages": [{"id": "m1", "from": "f1", "to": "t1", "subject": "S1", "timestamp": "T1"}],
            "threads": [{"id": "t1", "messageIds": ["m1"]}],
            "labels": ["important"],
            "settings": {"theme": "dark", "notifications": False},
            "history": [{"action": "login", "timestamp": "T1"}],
            "watch": ["ISSUE-1"],
            "sendAs": [{"alias": "c.extra@example.com", "default": True}]
        }
        response = JiraAPI.UserApi.create_user(payload)
        self.assertTrue(response['created'])
        user = response['user']

        # Assertions to verify all fields are correctly set
        self.assertEqual(user['name'], 'charlie_extra')
        self.assertEqual(user['profile']['bio'], 'A test user with a bio')
        self.assertEqual(user['groups'], ['testers', 'beta_users'])
        self.assertEqual(user['settings']['theme'], 'dark')
        self.assertFalse(user['settings']['notifications'])
        self.assertEqual(len(user['drafts']), 1)
        self.assertEqual(user['drafts'][0]['subject'], 'S1')

    def test_create_user_missing_fields(self):
        """Verify an error is returned if required fields for user creation are missing."""
        with self.assertRaises(ValidationError):
            JiraAPI.UserApi.create_user({"displayName": "incomplete"})
            
    def test_create_user_invalid_email(self):
        """Test user creation with an invalid email format."""
        with self.assertRaises(ValidationError):
            JiraAPI.UserApi.create_user({
                "name": "tester",
                "emailAddress": "not-an-email",
                "displayName": "Test User"
            })

    def test_reindex_lifecycle(self):
        """Check that reindex can be started and then we can query its status."""
        # Initially should not be running
        status_before = JiraAPI.ReindexApi.get_reindex_status()
        self.assertFalse(
            status_before["running"], "Reindex should not be running initially."
        )
        # Start reindex
        start_result = JiraAPI.ReindexApi.start_reindex(reindex_type="BACKGROUND")
        self.assertTrue(start_result["started"])
        # Check status again
        status_after = JiraAPI.ReindexApi.get_reindex_status()
        self.assertTrue(
            status_after["running"], "Reindex should be running after start."
        )
        self.assertEqual(status_after["type"], "BACKGROUND")

class TestUpdateComponentById(BaseTestCaseWithErrorHandler):
    """
    Test suite for the refactored 'update_component_by_id' function.
    """

    def setUp(self):
        """Reset test state (DB) before each test."""
        global DB
        # Define an initial state for the DB for each test
        DB["components"] = {
            "comp123": {"name": "Component A", "description": "Description A"},
            "comp456": {"name": "Component B", "description": "Description B"}
        }

    # tests to validate name must not be greater than 255 chars and description must not be greater than 1000 chars
    def test_name_length_exceeds_limit(self):
        """Test that name exceeding 255 characters raises ValueError."""
        long_name = "A" * 256
        self.assert_error_behavior(
            func_to_call=update_component_by_id,
            expected_exception_type=ValueError,
            expected_message="name cannot be longer than 255 characters",
            comp_id="comp123",
            name=long_name
        )
    def test_description_length_exceeds_limit(self):
        """Test that description exceeding 1000 characters raises ValueError."""
        long_description = "A" * 1001
        self.assert_error_behavior(
            func_to_call=update_component_by_id,
            expected_exception_type=ValueError,
            expected_message="description cannot be longer than 1000 characters",
            comp_id="comp123",
            description=long_description
        )
    
    # --- Validation Tests for Issue API ---
    def test_get_issue_empty_id(self):
        with self.assertRaisesRegex(ValueError, "issue_id cannot be empty."):
            JiraAPI.IssueApi.get_issue("")

    def test_update_issue_empty_id(self):
        with self.assertRaisesRegex(ValueError, "issue_id cannot be empty."):
            JiraAPI.IssueApi.update_issue("", fields={"summary": "summary"})

    def test_delete_issue_empty_id(self):
        with self.assertRaisesRegex(ValueError, "issue_id cannot be empty."):
            JiraAPI.IssueApi.delete_issue("")

    def test_assign_issue_validations(self):
        issue_fields = {
            "project": "TEST", "summary": "test", "description": "Test issue",
            "issuetype": "Task", "priority": "Medium", "assignee": {"name": "testuser"}
        }
        created = JiraAPI.IssueApi.create_issue(fields=issue_fields)
        issue_id = created["id"]

        with self.assertRaisesRegex(ValueError, "issue_id cannot be empty."):
            JiraAPI.IssueApi.assign_issue("", assignee={"name": "test"})
        
        with self.assertRaises(TypeError):
            JiraAPI.IssueApi.assign_issue(issue_id, assignee="not-a-dict") # type: ignore
        
        with self.assertRaises(ValidationError):
            JiraAPI.IssueApi.assign_issue(issue_id, assignee={}) # missing 'name'

        with self.assertRaises(ValidationError):
            JiraAPI.IssueApi.assign_issue(issue_id, assignee={"name": 123})

    def test_get_issue_with_invalid_db_data(self):
        """Test get_issue with inconsistent data in DB raises ValueError."""
        issue_id = "corrupted-issue"
        # Malformed data: 'summary' field is missing
        DB["issues"][issue_id] = {
            "id": issue_id,
            "fields": {
                "project": "TEST",
                "description": "A corrupted issue.",
                "issuetype": "Bug",
                "priority": "High",
                "status": "Broken",
                "assignee": {"name": "corruption-investigator"}
            }
        }
        with self.assertRaisesRegex(ValueError, f"Issue data for '{issue_id}' is invalid"):
            JiraAPI.IssueApi.get_issue(issue_id)


class TestFindUser(BaseTestCaseWithErrorHandler):
    
    def setUp(self):
        DB['users'] = {}
        self.user1 = create_user({
            "name": "alice", "emailAddress": "alice@example.com", "displayName": "Alice Active"
        })['user']

        self.user2 = create_user({
            "name": "bob", "emailAddress": "bob@example.com", "displayName": "Bob Inactive"
        })['user']
        DB['users'][self.user2['key']]['active'] = False

        self.user3 = create_user({
            "name": "charlie", "emailAddress": "charlie@example.com", "displayName": "Charlie Active"
        })['user']

    def test_find_users_success(self):
        
        results = find_users(search_string="alice")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'alice')

        results = find_users(search_string="bob@example.com")
        # Inactive user should not be returned by default
        self.assertEqual(len(results), 0)

        results = find_users(search_string="Active")
        self.assertEqual(len(results), 2)

        results = find_users(search_string="bob", includeActive=False, includeInactive=True)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'bob')

        results = find_users(search_string="example", includeActive=True, includeInactive=True)
        self.assertEqual(len(results), 3)

    def test_pagination(self):
        results = find_users(search_string="Active", maxResults=1)
        self.assertEqual(len(results), 1)

        results_page2 = find_users(search_string="Active", startAt=1, maxResults=1)
        self.assertEqual(len(results_page2), 1)
        self.assertNotEqual(results[0]['key'], results_page2[0]['key'])

    def test_invalid_input_types(self):
        """Test that find_user raises TypeError for invalid input types."""
        self.assert_error_behavior(
            find_users, TypeError, "search_string must be a string.", search_string=123
        )
        self.assert_error_behavior(
            find_users, TypeError, "startAt must be an integer.", search_string="test", startAt="a"
        )
        self.assert_error_behavior(
            find_users, TypeError, "maxResults must be an integer.", search_string="test", maxResults="a"
        )
        self.assert_error_behavior(
            find_users, TypeError, "includeActive must be a boolean.", search_string="test", includeActive="true"
        )
        self.assert_error_behavior(
            find_users, TypeError, "includeInactive must be a boolean.", search_string="test", includeInactive="false"
        )

    def test_invalid_input_values(self):
        """Test that find_user raises ValueError for invalid input values."""
        self.assert_error_behavior(
            find_users, ValueError, "search_string cannot be empty.", search_string=""
        )
        self.assert_error_behavior(
            find_users, ValueError, "startAt must be a non-negative integer.", search_string="test", startAt=-1
        )
        self.assert_error_behavior(
            find_users, ValueError, "maxResults must be a positive integer.", search_string="test", maxResults=0
        )


class TestJQLEnhancements(BaseTestCaseWithErrorHandler):
    """Test suite for new JQL operators and issue_picker JQL functionality."""
    
    def setUp(self):
        """Set up test data for JQL testing."""
        DB.clear()
        DB.update({
            "issues": {
                "DEMO-1": {
                    "id": "DEMO-1",
                    "fields": {
                        "project": "DEMO",
                        "summary": "Critical bug in login",
                        "description": "Users cannot login with valid credentials",
                        "priority": "High",
                        "status": "Open",
                        "issuetype": "Bug",
                        "assignee": {"name": "alice"},
                        "created": "2024-01-15"
                    }
                },
                "DEMO-2": {
                    "id": "DEMO-2", 
                    "fields": {
                        "project": "DEMO",
                        "summary": "UI glitch on dashboard",
                        "description": "Alignment issues in the main dashboard",
                        "priority": "Low",
                        "status": "Open", 
                        "issuetype": "Bug",
                        "assignee": {"name": "bob"},
                        "created": "2024-02-01"
                    }
                },
                "TEST-1": {
                    "id": "TEST-1",
                    "fields": {
                        "project": "TEST",
                        "summary": "Performance optimization",
                        "description": "Optimize database queries",
                        "priority": "Medium",
                        "status": "In Progress",
                        "issuetype": "Task", 
                        "assignee": {"name": "charlie"},
                        "created": "2024-01-20"
                    }
                },
                "TEST-2": {
                    "id": "TEST-2",
                    "fields": {
                        "project": "TEST", 
                        "summary": "Add new feature",
                        "description": "Implement user preferences",
                        "priority": "High",
                        "status": "Closed",
                        "issuetype": "Story",
                        "created": "2024-01-10"
                    }
                },
                "API-1": {
                    "id": "API-1",
                    "fields": {
                        "project": "API",
                        "summary": "API documentation update", 
                        "description": "Update REST API documentation",
                        "priority": "Medium",
                        "status": "Open",
                        "issuetype": "Task",
                        "assignee": {"name": "alice"},
                        "created": "2024-02-05"
                    }
                }
            },
            "projects": {
                "DEMO": {"key": "DEMO", "name": "Demo Project", "lead": "admin"},
                "TEST": {"key": "TEST", "name": "Test Project", "lead": "admin"},
                "API": {"key": "API", "name": "API Project", "lead": "admin"}
            }
        })

    def test_jql_not_equals_operator(self):
        """Test != (not equals) operator."""
        # Test != with string values
        result = JiraAPI.SearchApi.search_issues('priority != "Low"')
        issue_ids = [issue["id"] for issue in result["issues"]]
        self.assertIn("DEMO-1", issue_ids)  # High priority
        self.assertIn("TEST-1", issue_ids)  # Medium priority  
        self.assertIn("TEST-2", issue_ids)  # High priority
        self.assertIn("API-1", issue_ids)   # Medium priority
        self.assertNotIn("DEMO-2", issue_ids)  # Low priority - should be excluded

    def test_jql_not_contains_operator(self):
        """Test !~ (does not contain) operator."""
        result = JiraAPI.SearchApi.search_issues('summary !~ "bug"')
        issue_ids = [issue["id"] for issue in result["issues"]]
        self.assertNotIn("DEMO-1", issue_ids)  # Contains "bug" - should be excluded
        self.assertIn("DEMO-2", issue_ids)     # Contains "glitch" but not "bug" - should be included
        self.assertIn("TEST-1", issue_ids)     # Performance optimization
        self.assertIn("TEST-2", issue_ids)     # Add new feature
        self.assertIn("API-1", issue_ids)      # API documentation

    def test_jql_in_operator(self):
        """Test IN operator for list membership."""
        result = JiraAPI.SearchApi.search_issues('project IN ("DEMO", "API")')
        issue_ids = [issue["id"] for issue in result["issues"]]
        self.assertIn("DEMO-1", issue_ids)
        self.assertIn("DEMO-2", issue_ids) 
        self.assertIn("API-1", issue_ids)
        self.assertNotIn("TEST-1", issue_ids)  # TEST project excluded
        self.assertNotIn("TEST-2", issue_ids)  # TEST project excluded

    def test_jql_not_in_operator(self):
        """Test NOT IN operator."""
        result = JiraAPI.SearchApi.search_issues('status NOT IN ("Closed", "Done")')
        issue_ids = [issue["id"] for issue in result["issues"]]
        self.assertIn("DEMO-1", issue_ids)     # Open
        self.assertIn("DEMO-2", issue_ids)     # Open
        self.assertIn("TEST-1", issue_ids)     # In Progress
        self.assertIn("API-1", issue_ids)      # Open
        self.assertNotIn("TEST-2", issue_ids)  # Closed - should be excluded

    def test_jql_is_empty_operator(self):
        """Test IS EMPTY operator."""
        result = JiraAPI.SearchApi.search_issues('assignee IS EMPTY')
        issue_ids = [issue["id"] for issue in result["issues"]]
        self.assertNotIn("DEMO-1", issue_ids)  # Has assignee
        self.assertNotIn("DEMO-2", issue_ids)  # Has assignee
        self.assertNotIn("TEST-1", issue_ids)  # Has assignee
        self.assertIn("TEST-2", issue_ids)     # No assignee
        self.assertNotIn("API-1", issue_ids)   # Has assignee

    def test_jql_is_not_empty_operator(self):
        """Test IS NOT EMPTY operator."""
        result = JiraAPI.SearchApi.search_issues('assignee IS NOT EMPTY')
        issue_ids = [issue["id"] for issue in result["issues"]]
        self.assertIn("DEMO-1", issue_ids)     # Has assignee
        self.assertIn("DEMO-2", issue_ids)     # Has assignee
        self.assertIn("TEST-1", issue_ids)     # Has assignee
        self.assertNotIn("TEST-2", issue_ids)  # No assignee - should be excluded
        self.assertIn("API-1", issue_ids)      # Has assignee

    def test_jql_parentheses_grouping(self):
        """Test parentheses for expression grouping."""
        result = JiraAPI.SearchApi.search_issues('(project = "DEMO" OR project = "API") AND priority = "High"')
        issue_ids = [issue["id"] for issue in result["issues"]]
        self.assertIn("DEMO-1", issue_ids)     # DEMO + High priority
        self.assertNotIn("DEMO-2", issue_ids)  # DEMO but Low priority
        self.assertNotIn("TEST-2", issue_ids)  # High priority but TEST project
        self.assertNotIn("API-1", issue_ids)   # API but Medium priority

    def test_jql_complex_expression_with_parentheses(self):
        """Test complex expression with multiple levels of parentheses."""
        result = JiraAPI.SearchApi.search_issues('(priority = "High" OR priority = "Medium") AND (status = "Open" OR status = "In Progress")')
        issue_ids = [issue["id"] for issue in result["issues"]]
        self.assertIn("DEMO-1", issue_ids)     # High + Open
        self.assertIn("TEST-1", issue_ids)     # Medium + In Progress
        self.assertIn("API-1", issue_ids)      # Medium + Open
        self.assertNotIn("DEMO-2", issue_ids)  # Low priority
        self.assertNotIn("TEST-2", issue_ids)  # High but Closed

    def test_jql_legacy_empty_null_operators(self):
        """Test that legacy EMPTY and NULL operators still work."""
        result = JiraAPI.SearchApi.search_issues('assignee EMPTY')
        issue_ids = [issue["id"] for issue in result["issues"]]
        self.assertIn("TEST-2", issue_ids)     # No assignee

        result = JiraAPI.SearchApi.search_issues('assignee NULL') 
        issue_ids = [issue["id"] for issue in result["issues"]]
        self.assertIn("TEST-2", issue_ids)     # No assignee

    def test_issue_picker_with_jql(self):
        """Test issue_picker with JQL filtering."""
        # Test JQL filtering only
        result = JiraAPI.IssueApi.issue_picker(currentJQL='project = "DEMO"')
        self.assertIn("DEMO-1", result["issues"])
        self.assertIn("DEMO-2", result["issues"])
        self.assertNotIn("TEST-1", result["issues"])
        self.assertNotIn("API-1", result["issues"])

    def test_issue_picker_with_jql_and_text_query(self):
        """Test issue_picker with both JQL and text query."""
        # JQL + text query
        result = JiraAPI.IssueApi.issue_picker(query="bug", currentJQL='project = "DEMO"')
        self.assertIn("DEMO-1", result["issues"])  # DEMO project + contains "bug"
        self.assertNotIn("DEMO-2", result["issues"])  # DEMO project but no "bug" in summary
        self.assertNotIn("TEST-1", result["issues"])  # Wrong project
        self.assertNotIn("API-1", result["issues"])   # Wrong project

    def test_issue_picker_jql_with_complex_query(self):
        """Test issue_picker with complex JQL."""
        result = JiraAPI.IssueApi.issue_picker(
            currentJQL='priority IN ("High", "Medium") AND status != "Closed"'
        )
        issue_ids = result["issues"]
        self.assertIn("DEMO-1", issue_ids)     # High + Open
        self.assertIn("TEST-1", issue_ids)     # Medium + In Progress
        self.assertIn("API-1", issue_ids)      # Medium + Open
        self.assertNotIn("DEMO-2", issue_ids)  # Low priority
        self.assertNotIn("TEST-2", issue_ids)  # Closed status

    def test_issue_picker_invalid_jql(self):
        """Test issue_picker with invalid JQL syntax."""
        with self.assertRaises(ValueError) as context:
            JiraAPI.IssueApi.issue_picker(currentJQL='invalid jql syntax !')
        self.assertIn("Invalid JQL syntax", str(context.exception))

    def test_issue_picker_jql_type_validation(self):
        """Test issue_picker JQL parameter type validation."""
        with self.assertRaises(TypeError) as context:
            JiraAPI.IssueApi.issue_picker(currentJQL=123)
        self.assertIn("currentJQL must be a string or None", str(context.exception))

    def test_jql_date_comparison_with_new_operators(self):
        """Test date comparisons work with new operators."""
        result = JiraAPI.SearchApi.search_issues('created >= "2024-01-15" AND priority != "Low"')
        issue_ids = [issue["id"] for issue in result["issues"]]
        self.assertIn("DEMO-1", issue_ids)     # 2024-01-15 + High
        self.assertIn("TEST-1", issue_ids)     # 2024-01-20 + Medium
        self.assertIn("API-1", issue_ids)      # 2024-02-05 + Medium
        self.assertNotIn("DEMO-2", issue_ids)  # 2024-02-01 but Low priority
        self.assertNotIn("TEST-2", issue_ids)  # 2024-01-10 (before date)

    def test_jql_order_by_with_new_operators(self):
        """Test ORDER BY works with new operators."""
        result = JiraAPI.SearchApi.search_issues('priority != "Low" ORDER BY created DESC')
        issue_ids = [issue["id"] for issue in result["issues"]]
        # Should be ordered by created date descending
        self.assertEqual(issue_ids[0], "API-1")    # 2024-02-05 (most recent)
        self.assertEqual(issue_ids[1], "TEST-1")   # 2024-01-20
        self.assertEqual(issue_ids[2], "DEMO-1")   # 2024-01-15
        self.assertEqual(issue_ids[3], "TEST-2")   # 2024-01-10 (oldest)

    def test_jql_mixed_operators(self):
        """Test mixing old and new operators."""
        result = JiraAPI.SearchApi.search_issues('project = "DEMO" AND priority != "Medium" AND summary ~ "bug"')
        issue_ids = [issue["id"] for issue in result["issues"]]
        self.assertIn("DEMO-1", issue_ids)     # DEMO + not Medium + contains "bug"
        self.assertNotIn("DEMO-2", issue_ids)  # DEMO + Low (not Medium) but no "bug"

    def test_jql_error_handling(self):
        """Test JQL error handling for malformed queries."""
        with self.assertRaises(ValueError):
            JiraAPI.SearchApi.search_issues('project = "DEMO" AND (missing closing paren')
        
        with self.assertRaises(ValueError):
            JiraAPI.SearchApi.search_issues('project IN missing_parentheses')
        
        with self.assertRaises(ValueError):
            JiraAPI.SearchApi.search_issues('assignee IS NOT INVALID_KEYWORD')


if __name__ == "__main__":
    unittest.main()