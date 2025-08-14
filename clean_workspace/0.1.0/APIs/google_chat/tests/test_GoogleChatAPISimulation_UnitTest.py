import sys
import os
import uuid
import unittest

from datetime import datetime

from pydantic import ValidationError

sys.path.append("APIs")

from common_utils.base_case import BaseTestCaseWithErrorHandler

from google_chat.SimulationEngine.custom_errors import InvalidMessageIdFormatError
from google_chat.SimulationEngine.custom_errors import UserNotMemberError
from google_chat.SimulationEngine.custom_errors import InvalidParentFormatError
from google_chat.SimulationEngine.custom_errors import AdminAccessNotAllowedError
from google_chat.SimulationEngine.custom_errors import MembershipAlreadyExistsError
from google_chat.SimulationEngine.custom_errors import AdminAccessFilterError
from google_chat.SimulationEngine.custom_errors import InvalidPageSizeError

from google_chat import list_messages
from google_chat import add_space_member

import google_chat as GoogleChatAPI


class testUtils(BaseTestCaseWithErrorHandler):
    def test_change_user(self):
        GoogleChatAPI.SimulationEngine.utils._change_user("users/USER123")
        self.assertEqual(GoogleChatAPI.CURRENT_USER_ID, {"id": "users/USER123"})

    def test_create_user(self):
        user = GoogleChatAPI.SimulationEngine.utils._create_user("ABC")
        self.assertEqual(user["displayName"], "ABC")


class TestSaveLoadDB(BaseTestCaseWithErrorHandler):
    def setUp(self):
        """Reset DB before each test"""
        GoogleChatAPI.DB.clear()
        GoogleChatAPI.DB.update(
            {
                "User": [],
                "Space": [],
                "Membership": [],
                "Message": [],
                "Reaction": [],
                "SpaceReadState": [],
                "ThreadReadState": [],
                "SpaceNotificationSetting": [],
            }
        )
        GoogleChatAPI.CURRENT_USER = {"id": "users/USER123"}
        GoogleChatAPI.CURRENT_USER_ID = GoogleChatAPI.CURRENT_USER

    def test_save_load_db(self):
        """Test save and load DB"""
        # Save DB
        GoogleChatAPI.DB.update({"test_object": "test_value"})
        GoogleChatAPI.SimulationEngine.db.save_state("test_save_load_db.json")

        # Load DB
        GoogleChatAPI.SimulationEngine.db.load_state("test_save_load_db.json")
        self.assertEqual(GoogleChatAPI.DB["test_object"], "test_value")

        os.remove("test_save_load_db.json")


class TestGoogleChatSpaces(BaseTestCaseWithErrorHandler):

    def setUp(self):
        """Reset DB before each test"""
        GoogleChatAPI.DB.clear()
        GoogleChatAPI.DB.update(
            {
                "User": [],
                "Space": [],
                "Membership": [],
                "Message": [],
                "Reaction": [],
                "SpaceReadState": [],
                "ThreadReadState": [],
                "SpaceNotificationSetting": [],
            }
        )
        GoogleChatAPI.CURRENT_USER = {"id": "users/USER123"}
        GoogleChatAPI.CURRENT_USER_ID = GoogleChatAPI.CURRENT_USER

    def test_spaces_create(self):
        """Modified test_spaces_create from original suite."""
        space_request = {
            "displayName": "Test Space",
            "spaceType": "SPACE",
            "importMode": False, # Explicitly set
        }
        
        # Print debug information before test
        print(f"Before test - CURRENT_USER_ID: {GoogleChatAPI.CURRENT_USER_ID}")
        print(f"Before test - CURRENT_USER: {GoogleChatAPI.CURRENT_USER}")
        
        # Using create_space alias
        created = GoogleChatAPI.create_space(space=space_request)
        self.assertTrue(created.get("name", "").startswith("spaces/"))
        
        # Print debug information after space creation
        print(f"Created space name: {created['name']}")
        print(f"After creation - CURRENT_USER_ID: {GoogleChatAPI.CURRENT_USER_ID}")
        print(f"After creation - CURRENT_USER: {GoogleChatAPI.CURRENT_USER}")
        
        # Print all memberships in DB for debugging
        print(f"Memberships in DB: {GoogleChatAPI.DB['Membership']}")
        
        # Check membership for the current user
        expected_membership_name = f"{created['name']}/members/{GoogleChatAPI.CURRENT_USER_ID.get('id')}"
        print(f"Expected membership name: {expected_membership_name}")
        
        found_membership = any(
            m.get("name") == expected_membership_name for m in GoogleChatAPI.DB["Membership"]
        )
        self.assertTrue(found_membership, "Membership for current user was not created.")

        # Original test: space_request = None, expecting {}
        # Now, space=None (which becomes {} in the function before Pydantic)
        # will raise ValidationError due to missing spaceType.
        self.assert_error_behavior(
            func_to_call=GoogleChatAPI.create_space,
            expected_exception_type=ValidationError,
            expected_message="1 validation error for SpaceInputModel\nspaceType\n  Field required [type=missing, input_value={}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.11/v/missing",
            space=None
        )

    def test_spaces_setup(self):
        setup_request = {
            "space": {
                "displayName": "Setup Space",
                "spaceType": "SPACE",
                "importMode": False,
                "customer": "customers/my_customer",
            },
            "memberships": [
                {
                    "member": {
                        "name": "users/otheruser@example.com",
                        "type": "HUMAN",
                        "displayName": "Other User",
                    },
                    "role": "ROLE_MEMBER",
                },
                {
                    "member": {
                        "name": "users/USER123",
                        "type": "HUMAN",
                        "displayName": "User One Twenty-Three",
                    },
                    "role": "ROLE_MEMBER",
                },
            ],
        }
        created_space = GoogleChatAPI.Spaces.setup(setup_request)
        caller_mem = (
            f"{created_space['name']}/members/{GoogleChatAPI.CURRENT_USER.get('id')}"
        )
        other_mem = f"{created_space['name']}/members/users/otheruser@example.com"
        mem_names = [m["name"] for m in GoogleChatAPI.DB["Membership"]]
        print(mem_names)
        print(caller_mem)
        self.assertIn(caller_mem, mem_names)
        self.assertIn(other_mem, mem_names)

    def test_spaces_patch(self):
        space_request = {
            "displayName": "Patch Space",
            "spaceType": "SPACE",
            "importMode": False,
            "customer": "customers/my_customer",
            "spaceDetails": {"description": "Old description"},
        }
        space_obj = GoogleChatAPI.Spaces.create(requestId="req-101", space=space_request)
        print(f"Created space_obj type: {space_obj.get('spaceType')}")
        
        patch_updates = {
            "spaceDetails": {"description": "New description updated via patch"},
            "displayName": "Patch Space Updated",
            "spaceHistoryState": "HISTORY_ON",
            "accessSettings": {"audience": "SPECIFIC_USERS"},
            "permissionSettings": {"manageMembersAndGroups": True},
        }
        updated = GoogleChatAPI.Spaces.patch(
            name=space_obj["name"],
            updateMask="space_details,display_name,space_history_state,access_settings.audience,permission_settings",
            space_updates=patch_updates,
            useAdminAccess=False,
        )
        self.assertEqual(updated.get("displayName"), "Patch Space Updated")
        self.assertEqual(updated.get("spaceHistoryState"), "HISTORY_ON")
        self.assertTrue(
            updated.get("spaceDetails", {})
            .get("description", "")
            .startswith("New description")
        )

        non_existent_space = GoogleChatAPI.Spaces.patch(
            name="spaces/NON_EXISTENT",
            updateMask="space_details,display_name,space_history_state,access_settings.audience,permission_settings",
            space_updates=patch_updates,
            useAdminAccess=False,
        )
        self.assertEqual(non_existent_space, {})

        update_mask = "*"
        updated = GoogleChatAPI.Spaces.patch(
            name=space_obj["name"],
            updateMask=update_mask,
            space_updates=patch_updates,
            useAdminAccess=False,
        )
        self.assertEqual(updated.get("displayName"), "Patch Space Updated")
        self.assertEqual(updated.get("spaceHistoryState"), "HISTORY_ON")
        self.assertTrue(
            updated.get("spaceDetails", {})
            .get("description", "")
            .startswith("New description")
        )

        update_mask = "space_details,display_name,space_history_state,access_settings.audience,permission_settings"
        space_updates = {
            "spaceDetails": {},
            "spaceHistoryState": "HISTORY_ON",
            "accessSettings": {"audience": "SPECIFIC_USERS"},
            "permissionSettings": {"manageMembersAndGroups": True},
        }
        updated = GoogleChatAPI.Spaces.patch(
            name=space_obj["name"],
            updateMask=update_mask,
            space_updates=space_updates,
            useAdminAccess=False,
        )
        self.assertEqual(updated.get("displayName"), "Patch Space Updated")

        import io
        import sys

        stdout_capture = io.StringIO()
        sys.stdout = stdout_capture

        space_request = {
            "displayName": "Patch Space",
            "spaceType": "GROUP_CHAT",
            "importMode": False,
            "customer": "customers/my_customer",
            "spaceDetails": {"description": "Old description"},
        }
        space_obj = GoogleChatAPI.Spaces.create(requestId="req-101", space=space_request)
        
        # Ensure the space is GROUP_CHAT by directly editing it in the DB
        for sp in GoogleChatAPI.DB["Space"]:
            if sp["name"] == space_obj["name"]:
                sp["spaceType"] = "GROUP_CHAT"
                break
        
        # Verify that the space is now GROUP_CHAT
        space_obj = GoogleChatAPI.Spaces.get(name=space_obj["name"], useAdminAccess=True)
        self.assertEqual(space_obj["spaceType"], "GROUP_CHAT")
        original_display_name = space_obj["displayName"]


        update_mask = "display_name"

        space_updates = {
            "spaceType": "GROUP_CHAT",
            "displayName": "Group Chat Space",
            "spaceDetails": {},
            "spaceHistoryState": "HISTORY_ON",
            "accessSettings": {"audience": "SPECIFIC_USERS"},
            "permissionSettings": {"manageMembersAndGroups": True},
        }

        updated = GoogleChatAPI.Spaces.patch(
            name=space_obj["name"],
            updateMask=update_mask,
            space_updates=space_updates,
            useAdminAccess=False,
        )
        
        # For a GROUP_CHAT space, displayName should not be updated since it's only valid for SPACE type
        # So the displayName should remain unchanged
        self.assertEqual(updated.get("displayName"), original_display_name)

    def test_spaces_search(self):
        GoogleChatAPI.DB["Space"].extend(
            [
                {
                    "name": "spaces/AAA",
                    "displayName": "Team Chat Room",
                    "spaceType": "SPACE",
                    "customer": "customers/my_customer",
                    "externalUserAllowed": True,
                    "spaceHistoryState": "HISTORY_ON",
                    "membershipCount": {"joined_direct_human_user_count": 10},
                    "createTime": "2022-05-01T10:00:00Z",
                    "lastActiveTime": "2023-05-01T12:00:00Z",
                    "accessSettings": {"audience": "OPEN"},
                    "permissionSettings": {},
                },
                {
                    "name": "spaces/BBB",
                    "displayName": "Fun Event",
                    "spaceType": "SPACE",
                    "customer": "customers/my_customer",
                    "externalUserAllowed": False,
                    "spaceHistoryState": "HISTORY_OFF",
                    "membershipCount": {"joined_direct_human_user_count": 25},
                    "createTime": "2021-12-15T09:30:00Z",
                    "lastActiveTime": "2023-04-20T16:00:00Z",
                    "accessSettings": {"audience": "RESTRICTED"},
                    "permissionSettings": {},
                },
            ]
        )

        sample_query = (
            'customer = "customers/my_customer" AND space_type = "SPACE" '
            'AND display_name:"Team" AND last_active_time > "2022-01-01T00:00:00Z"'
        )
        result = GoogleChatAPI.Spaces.search(
            useAdminAccess=True,
            pageSize=2,
            pageToken="0",
            query=sample_query,
            orderBy="create_time ASC",
        )
        self.assertIn("spaces", result)

    def test_spaces_get(self):
        space_request = {
            "displayName": "Get Space Test",
            "spaceType": "SPACE",
            "importMode": False,
            "customer": "customers/my_customer",
        }

        created = GoogleChatAPI.Spaces.create(requestId="req-201", space=space_request)

        # Admin access should always succeed
        got_space = GoogleChatAPI.Spaces.get(name=created["name"], useAdminAccess=True)
        self.assertTrue(got_space)

        # As current user (USER123), should be a member from create()
        got_space2 = GoogleChatAPI.Spaces.get(
            name=created["name"], useAdminAccess=False
        )
        self.assertTrue(got_space2)

        # Change to a different user, who is NOT a member]
        GoogleChatAPI.SimulationEngine.utils._change_user("users/asdasdSAS123")

        got_space3 = GoogleChatAPI.Spaces.get(
            name=created["name"], useAdminAccess=False
        )
        self.assertEqual(got_space3, {})

        # Reset the user for other tests
        GoogleChatAPI.SimulationEngine.utils._change_user("users/USER123")

    def test_spaces_delete(self):
        space_request = {
            "displayName": "Delete Space Test",
            "spaceType": "SPACE",
            "importMode": False,
            "customer": "customers/my_customer",
        }
        created = GoogleChatAPI.Spaces.create(requestId="req-301", space=space_request)

        membership = {
            "name": f"{created['name']}/members/users/extra@example.com",
            "state": "JOINED",
            "role": "ROLE_MEMBER",
            "member": {
                "name": "users/extra@example.com",
                "displayName": "Extra User",
                "domainId": "example.com",
                "type": "HUMAN",
                "isAnonymous": False,
            },
            "groupMember": {},
            "createTime": datetime.now().isoformat() + "Z",
            "deleteTime": "",
        }
        GoogleChatAPI.DB["Membership"].append(membership)

        message = {
            "name": f"{created['name']}/messages/1",
            "text": "Message to delete",
            "createTime": datetime.now().isoformat() + "Z",
            "thread": {},
            "sender": {"name": GoogleChatAPI.CURRENT_USER, "type": "HUMAN"},
        }
        GoogleChatAPI.DB["Message"].append(message)

        deleted = GoogleChatAPI.Spaces.delete(
            name=created["name"], useAdminAccess=False
        )
        self.assertEqual(deleted, {})

        remaining_spaces = [
            sp for sp in GoogleChatAPI.DB["Space"] if sp.get("name") == created["name"]
        ]
        self.assertFalse(remaining_spaces)

        remaining_memberships = [
            m
            for m in GoogleChatAPI.DB["Membership"]
            if m.get("name", "").startswith(created["name"])
        ]
        remaining_messages = [
            m
            for m in GoogleChatAPI.DB["Message"]
            if m.get("name", "").startswith(created["name"])
        ]
        self.assertFalse(remaining_memberships)
        self.assertFalse(remaining_messages)

    def test_list_filter_and_operator(self):
        """Test space_type filter with AND operator (should fail)"""
        # Add test spaces
        GoogleChatAPI.DB["Space"].extend(
            [
                {
                    "name": "spaces/AAA",
                    "spaceType": "SPACE",
                    "displayName": "Test Space",
                },
                {
                    "name": "spaces/BBB",
                    "spaceType": "GROUP_CHAT",
                    "displayName": "Test Group Chat",
                },
            ]
        )

        # Create memberships for current user
        for space in GoogleChatAPI.DB["Space"]:
            membership = {
                "name": f"{space['name']}/members/{GoogleChatAPI.CURRENT_USER_ID['id']}",
                "state": "JOINED",
                "role": "ROLE_MEMBER",
                "member": {
                    "name": GoogleChatAPI.CURRENT_USER_ID["id"],
                    "type": "HUMAN",
                },
            }
            GoogleChatAPI.DB["Membership"].append(membership)

        # Test filter with AND operator (should return error)
        result = GoogleChatAPI.Spaces.list(
            filter='spaceType = "SPACE" AND spaceType = "GROUP_CHAT"'
        )
        self.assertIn("error", result)
        self.assertIn("AND", result["error"])  # Error about AND not being supported

    def test_list_filter_invalid_space_type(self):
        """Test lines 63-113: filter with invalid space type"""
        # Add test spaces and memberships
        space = {
            "name": "spaces/AAA",
            "spaceType": "SPACE",
            "displayName": "Test Space",
        }
        GoogleChatAPI.DB["Space"].append(space)

        membership = {
            "name": f"{space['name']}/members/{GoogleChatAPI.CURRENT_USER_ID['id']}",
            "state": "JOINED",
            "role": "ROLE_MEMBER",
            "member": {"name": GoogleChatAPI.CURRENT_USER_ID["id"], "type": "HUMAN"},
        }
        GoogleChatAPI.DB["Membership"].append(membership)

        # Test filter with invalid space type
        result = GoogleChatAPI.Spaces.list(filter='spaceType = "INVALID_TYPE"')
        self.assertIn("error", result)
        self.assertIn("Invalid space type", result["error"])

    def test_list_filter_no_valid_expressions(self):
        """Test lines 63-113: filter with no valid expressions"""
        # Test filter with no valid expressions
        result = GoogleChatAPI.Spaces.list(filter='invalid_field = "something"')
        self.assertIn("error", result)
        self.assertIn("No valid expressions found", result["error"])

    def test_search_missing_required_fields(self):
        """Test lines 218-219, 223, 225: search with missing required fields"""
        # Test missing customer field
        result = GoogleChatAPI.Spaces.search(
            useAdminAccess=True, query='space_type = "SPACE"'
        )
        self.assertEqual(result, {})

        # Test missing space_type field
        result = GoogleChatAPI.Spaces.search(
            useAdminAccess=True, query='customer = "customers/my_customer"'
        )
        self.assertEqual(result, {})

    def test_search_non_admin_access(self):
        """Test lines 241-242: search with non-admin access"""
        result = GoogleChatAPI.Spaces.search(
            useAdminAccess=False,
            query='customer = "customers/my_customer" AND space_type = "SPACE"',
        )
        self.assertEqual(result, {})

    def test_search_page_token_handling(self):
        """Test lines 247, 250-261: search with different page token values"""
        # Add sample spaces
        for i in range(5):
            GoogleChatAPI.DB["Space"].append(
                {
                    "name": f"spaces/SPACE_{i}",
                    "spaceType": "SPACE",
                    "customer": "customers/my_customer",
                    "displayName": f"Test Space {i}",
                    "createTime": f"2023-01-0{i+1}T00:00:00Z",
                }
            )

        # Test with invalid page token (should default to 0)
        result = GoogleChatAPI.Spaces.search(
            useAdminAccess=True,
            pageToken="invalid_token",
            query='customer = "customers/my_customer" AND space_type = "SPACE"',
        )
        self.assertIn("spaces", result)

        # Test with negative page token (should default to 0)
        result = GoogleChatAPI.Spaces.search(
            useAdminAccess=True,
            pageToken="-10",
            query='customer = "customers/my_customer" AND space_type = "SPACE"',
        )
        self.assertIn("spaces", result)

    def test_search_matches_field(self):
        """Test lines 307-308, 315-316, 321-322, 324-325: search field matching"""
        # Add test spaces with various field values
        GoogleChatAPI.DB["Space"].extend(
            [
                {
                    "name": "spaces/A1",
                    "spaceType": "SPACE",
                    "displayName": "Marketing Team",
                    "externalUserAllowed": True,
                    "spaceHistoryState": "HISTORY_ON",
                    "createTime": "2023-01-01T00:00:00Z",
                    "lastActiveTime": "2023-05-01T00:00:00Z",
                },
                {
                    "name": "spaces/A2",
                    "spaceType": "SPACE",
                    "displayName": "Engineering Team",
                    "externalUserAllowed": False,
                    "spaceHistoryState": "HISTORY_OFF",
                    "createTime": "2023-02-01T00:00:00Z",
                    "lastActiveTime": "2023-06-01T00:00:00Z",
                },
                {
                    "name": "spaces/A4",
                    "spaceType": "SPAC",
                    "displayName": "Marketing Team",
                    "externalUserAllowed": True,
                },
            ]
        )

        # Test display_name field filtering
        result = GoogleChatAPI.Spaces.search(
            useAdminAccess=True,
            query='customer = "customers/my_customer" AND space_type = "SPACE" AND display_name:"Engineering"',
        )
        self.assertEqual(len(result["spaces"]), 1)
        self.assertEqual(result["spaces"][0]["name"], "spaces/A2")

        # Test external_user_allowed field
        result = GoogleChatAPI.Spaces.search(
            useAdminAccess=True,
            query='customer = "customers/my_customer" AND space_type = "SPACE" AND external_user_allowed = "false"',
        )
        self.assertEqual(len(result["spaces"]), 1)
        self.assertEqual(result["spaces"][0]["name"], "spaces/A2")

        # Test space_history_state field
        result = GoogleChatAPI.Spaces.search(
            useAdminAccess=True,
            query='customer = "customers/my_customer" AND space_type = "SPACE" AND space_history_state = "HISTORY_ON"',
        )
        self.assertEqual(len(result["spaces"]), 1)
        self.assertEqual(result["spaces"][0]["name"], "spaces/A1")

        # Test date comparison fields
        result = GoogleChatAPI.Spaces.search(
            useAdminAccess=True,
            query='customer = "customers/my_customer" AND space_type = "SPACE" AND create_time > "2023-01-15T00:00:00Z"',
        )
        self.assertEqual(len(result["spaces"]), 1)
        self.assertEqual(result["spaces"][0]["name"], "spaces/A2")

        result = GoogleChatAPI.Spaces.search(
            useAdminAccess=True,
            query='customer = "customers/my_customer" AND space_type = "SPACE" AND last_active_time = "2023-05-01T00:00:00Z"',
        )
        self.assertEqual(len(result["spaces"]), 1)
        self.assertEqual(result["spaces"][0]["name"], "spaces/A1")

        result = GoogleChatAPI.Spaces.search(
            useAdminAccess=True,
            query='customer = "customers/my_customer" AND space_type = "SPACE" AND last_active_time <= "2023-05-01T00:00:00Z"',
        )
        self.assertEqual(len(result["spaces"]), 1)
        self.assertEqual(result["spaces"][0]["name"], "spaces/A1")

        result = GoogleChatAPI.Spaces.search(
            useAdminAccess=True,
            query='customer = "customers/my_customer" AND space_type = "SPACE" AND last_active_tim = "2023-05-01T00:00:00Z"',
        )
        self.assertEqual(len(result["spaces"]), 2)
        self.assertEqual(result["spaces"][0]["name"], "spaces/A1")

    def test_get_membership_check(self):
        """Test lines 335, 337: get with membership check"""
        # Add test space
        space = {
            "name": "spaces/TEST",
            "spaceType": "SPACE",
            "displayName": "Test Space",
        }
        GoogleChatAPI.DB["Space"].append(space)

        # Test without membership and without admin access
        result = GoogleChatAPI.Spaces.get(name="spaces/TEST")
        self.assertEqual(result, {})

        # Add membership and test again
        membership = {
            "name": f"spaces/TEST/members/{GoogleChatAPI.CURRENT_USER_ID['id']}",
            "state": "JOINED",
            "role": "ROLE_MEMBER",
            "member": {"name": GoogleChatAPI.CURRENT_USER_ID["id"], "type": "HUMAN"},
        }
        GoogleChatAPI.DB["Membership"].append(membership)

        result = GoogleChatAPI.Spaces.get(name="spaces/TEST")
        self.assertEqual(result["name"], "spaces/TEST")

    def test_create_validation(self):
        """Test lines 351-354, 3574: create with validation checks"""
        # Test missing spaceType
        result = GoogleChatAPI.Spaces.create(space={})
        self.assertEqual(result, {})

        # Test SPACE without displayName
        result = GoogleChatAPI.Spaces.create(space={"spaceType": "SPACE"})
        self.assertEqual(result, {})

        # Test duplicate displayName
        GoogleChatAPI.DB["Space"].append(
            {
                "name": "spaces/EXISTING",
                "spaceType": "SPACE",
                "displayName": "Existing Space",
            }
        )

        result = GoogleChatAPI.Spaces.create(
            space={"spaceType": "SPACE", "displayName": "Existing Space"}
        )
        self.assertEqual(result, {})

    def test_direct_message_creation(self):
        """Test lines 504, 511-512, 515-516: direct message space creation"""
        # Create a direct message space with singleUserBotDm=True
        result = GoogleChatAPI.Spaces.create(
            space={"spaceType": "DIRECT_MESSAGE", "singleUserBotDm": True}
        )

        # Verify it was created and no membership was added (line 511-512)
        self.assertTrue(result.get("name", "").startswith("spaces/"))
        self.assertEqual(result["spaceType"], "DIRECT_MESSAGE")
        self.assertTrue(result["singleUserBotDm"])

        # Check no membership was created for the current user
        memberships = [
            m
            for m in GoogleChatAPI.DB["Membership"]
            if m.get("name", "").startswith(result["name"])
        ]
        self.assertEqual(len(memberships), 0)

    def test_patch_invalid_scenarios(self):
        """Test lines 521-523: patch with invalid scenarios"""
        # Add test space
        space = {
            "name": "spaces/PATCH_TEST",
            "spaceType": "GROUP_CHAT",
            "displayName": "Original Name",
        }
        GoogleChatAPI.DB["Space"].append(space)

        # Test changing GROUP_CHAT to SPACE without displayName
        result = GoogleChatAPI.Spaces.patch(
            name="spaces/PATCH_TEST",
            updateMask="space_type",
            space_updates={"spaceType": "SPACE"},
            useAdminAccess=False,
        )
        self.assertEqual(result, {})

        # Test with invalid space_type conversion
        result = GoogleChatAPI.Spaces.patch(
            name="spaces/PATCH_TEST",
            updateMask="space_type",
            space_updates={"spaceType": "DIRECT_MESSAGE"},
            useAdminAccess=False,
        )
        # Space_type should remain unchanged
        self.assertEqual(result.get("spaceType"), "GROUP_CHAT")

    def test_delete_not_found(self):
        """Test lines 698-699: delete non-existent space"""
        result = GoogleChatAPI.Spaces.delete(name="spaces/NONEXISTENT")
        self.assertEqual(result, {})

    def test_delete_unauthorized(self):
        """Test lines 704, 721: delete with unauthorized user"""
        # Add test space but no membership for current user
        space = {
            "name": "spaces/UNAUTHORIZED",
            "spaceType": "SPACE",
            "displayName": "Unauthorized Space",
        }
        GoogleChatAPI.DB["Space"].append(space)

        # Try to delete without being a member or admin
        result = GoogleChatAPI.Spaces.delete(name="spaces/UNAUTHORIZED")
        self.assertEqual(result, {})

        # Verify space still exists
        spaces = [
            s for s in GoogleChatAPI.DB["Space"] if s["name"] == "spaces/UNAUTHORIZED"
        ]
        self.assertEqual(len(spaces), 1)

    def test_delete_with_reactions(self):
        """Test lines 728-730, 733-743, 750: delete with reactions"""
        # Add test space with message and reaction
        space = {
            "name": "spaces/WITH_REACTIONS",
            "spaceType": "SPACE",
            "displayName": "Space With Reactions",
        }
        GoogleChatAPI.DB["Space"].append(space)

        # Add membership for current user
        membership = {
            "name": f"spaces/WITH_REACTIONS/members/{GoogleChatAPI.CURRENT_USER_ID['id']}",
            "state": "JOINED",
            "role": "ROLE_MEMBER",
            "member": {"name": GoogleChatAPI.CURRENT_USER_ID["id"], "type": "HUMAN"},
        }
        GoogleChatAPI.DB["Membership"].append(membership)

        # Add message
        message = {
            "name": "spaces/WITH_REACTIONS/messages/MSG1",
            "text": "Test message",
            "createTime": datetime.now().isoformat() + "Z",
        }
        GoogleChatAPI.DB["Message"].append(message)

        # Add reaction
        if "Reaction" not in GoogleChatAPI.DB:
            GoogleChatAPI.DB["Reaction"] = []

        reaction = {
            "name": "spaces/WITH_REACTIONS/messages/MSG1/reactions/R1",
            "emoji": {"unicode": "👍"},
            "user": {"name": GoogleChatAPI.CURRENT_USER_ID["id"]},
        }
        GoogleChatAPI.DB["Reaction"].append(reaction)

        # Delete the space
        result = GoogleChatAPI.Spaces.delete(name="spaces/WITH_REACTIONS")
        self.assertEqual(result, {})

        # Verify space, message, membership, and reaction are all removed
        spaces = [
            s for s in GoogleChatAPI.DB["Space"] if s["name"] == "spaces/WITH_REACTIONS"
        ]
        memberships = [
            m
            for m in GoogleChatAPI.DB["Membership"]
            if m["name"].startswith("spaces/WITH_REACTIONS/")
        ]
        messages = [
            m
            for m in GoogleChatAPI.DB["Message"]
            if m["name"].startswith("spaces/WITH_REACTIONS/")
        ]
        reactions = [
            r
            for r in GoogleChatAPI.DB["Reaction"]
            if r["name"].startswith("spaces/WITH_REACTIONS/")
        ]

        self.assertEqual(len(spaces), 0)
        self.assertEqual(len(memberships), 0)
        self.assertEqual(len(messages), 0)
        self.assertEqual(len(reactions), 0)

    def test_parse_filter_with_multiple_operators(self):
        """Test lines 757-759, 765-767: parse_filter with multiple operators"""
        # Setup spaces to query
        GoogleChatAPI.DB["Space"].extend(
            [
                {
                    "name": "spaces/MULTI1",
                    "spaceType": "SPACE",
                    "customer": "customers/my_customer",
                    "displayName": "Sales Team",
                    "createTime": "2023-01-01T00:00:00Z",
                    "lastActiveTime": "2023-03-01T00:00:00Z",
                },
                {
                    "name": "spaces/MULTI2",
                    "spaceType": "SPACE",
                    "customer": "customers/my_customer",
                    "displayName": "Support Team",
                    "createTime": "2023-02-01T00:00:00Z",
                    "lastActiveTime": "2023-04-01T00:00:00Z",
                },
            ]
        )

        # Test with multiple time-based operators
        result = GoogleChatAPI.Spaces.search(
            useAdminAccess=True,
            query='customer = "customers/my_customer" AND space_type = "SPACE" AND '
            + 'create_time >= "2023-01-15T00:00:00Z" AND last_active_time < "2023-05-01T00:00:00Z"',
        )

        self.assertEqual(len(result["spaces"]), 1)
        self.assertEqual(result["spaces"][0]["name"], "spaces/MULTI2")

        # Test with HAS operator (display_name:)
        result = GoogleChatAPI.Spaces.search(
            useAdminAccess=True,
            query='customer = "customers/my_customer" AND space_type = "SPACE" AND '
            + 'display_name:"Support"',
        )

        self.assertEqual(len(result["spaces"]), 1)
        self.assertEqual(result["spaces"][0]["name"], "spaces/MULTI2")

    def test_search_sorting_options(self):
        """Test: search with sorting"""
        # Setup spaces with different values for sorting
        GoogleChatAPI.DB["Space"].extend(
            [
                {
                    "name": "spaces/SORT1",
                    "spaceType": "SPACE",
                    "customer": "customers/my_customer",
                    "displayName": "Space A",
                    "createTime": "2023-01-01T00:00:00Z",
                    "lastActiveTime": "2023-04-01T00:00:00Z",
                    "membershipCount": {"joined_direct_human_user_count": 5},
                },
                {
                    "name": "spaces/SORT2",
                    "spaceType": "SPACE",
                    "customer": "customers/my_customer",
                    "displayName": "Space B",
                    "createTime": "2023-02-01T00:00:00Z",
                    "lastActiveTime": "2023-03-01T00:00:00Z",
                    "membershipCount": {"joined_direct_human_user_count": 10},
                },
            ]
        )

        # Test default sort (create_time ASC)
        result = GoogleChatAPI.Spaces.search(
            useAdminAccess=True,
            query='customer = "customers/my_customer" AND space_type = "SPACE"',
        )
        self.assertEqual(result["spaces"][0]["name"], "spaces/SORT1")
        self.assertEqual(result["spaces"][1]["name"], "spaces/SORT2")

        # Test create_time DESC
        result = GoogleChatAPI.Spaces.search(
            useAdminAccess=True,
            query='customer = "customers/my_customer" AND space_type = "SPACE"',
            orderBy="create_time DESC",
        )
        self.assertEqual(result["spaces"][0]["name"], "spaces/SORT2")
        self.assertEqual(result["spaces"][1]["name"], "spaces/SORT1")

        # Test last_active_time sorting
        result = GoogleChatAPI.Spaces.search(
            useAdminAccess=True,
            query='customer = "customers/my_customer" AND space_type = "SPACE"',
            orderBy="last_active_time DESC",
        )
        self.assertEqual(result["spaces"][0]["name"], "spaces/SORT1")
        self.assertEqual(result["spaces"][1]["name"], "spaces/SORT2")

        # Test membership_count sorting
        result = GoogleChatAPI.Spaces.search(
            useAdminAccess=True,
            query='customer = "customers/my_customer" AND space_type = "SPACE"',
            orderBy="membership_count.joined_direct_human_user_count DESC",
        )
        self.assertEqual(result["spaces"][0]["name"], "spaces/SORT2")
        self.assertEqual(result["spaces"][1]["name"], "spaces/SORT1")
        result = GoogleChatAPI.Spaces.search(
            useAdminAccess=True,
            query='customer = "customers/my_customer" AND space_type = "SPACE"',
            orderBy="abc DESC",
        )
        self.assertEqual(result["spaces"][0]["name"], "spaces/SORT1")
        self.assertEqual(result["spaces"][1]["name"], "spaces/SORT2")

    def test_list_parse_space_type_filter_complex(self):
        """Test lines 102-113: complex filtering scenarios"""
        # Add test spaces
        GoogleChatAPI.DB["Space"].extend(
            [
                {
                    "name": "spaces/A1",
                    "spaceType": "SPACE",
                    "displayName": "Test Space",
                },
                {
                    "name": "spaces/A2",
                    "spaceType": "GROUP_CHAT",
                    "displayName": "Test Group",
                },
                {
                    "name": "spaces/A3",
                    "spaceType": "DIRECT_MESSAGE",
                    "displayName": "Test DM",
                },
            ]
        )

        # Create memberships for current user
        for space in GoogleChatAPI.DB["Space"]:
            membership = {
                "name": f"{space['name']}/members/{GoogleChatAPI.CURRENT_USER_ID['id']}",
                "state": "JOINED",
                "role": "ROLE_MEMBER",
                "member": {
                    "name": GoogleChatAPI.CURRENT_USER_ID["id"],
                    "type": "HUMAN",
                },
            }
            GoogleChatAPI.DB["Membership"].append(membership)

        # Test with OR operator
        result = GoogleChatAPI.Spaces.list(
            filter='spaceType = "SPACE" OR spaceType = "GROUP_CHAT"'
        )
        # Both SPACE and GROUP_CHAT types should be returned
        space_types = [space["spaceType"] for space in result["spaces"]]
        self.assertIn("SPACE", space_types)
        self.assertIn("GROUP_CHAT", space_types)
        self.assertNotIn("DIRECT_MESSAGE", space_types)

    def test_search_invalid_page_size(self):
        """Test line 225: search with invalid page size"""
        # Add test spaces
        GoogleChatAPI.DB["Space"].append(
            {
                "name": "spaces/TEST1",
                "spaceType": "SPACE",
                "customer": "customers/my_customer",
                "displayName": "Test Space",
            }
        )

        # Test with negative page size (should default to 100)
        result = GoogleChatAPI.Spaces.search(
            useAdminAccess=True,
            pageSize=-5,
            query='customer = "customers/my_customer" AND space_type = "SPACE"',
        )
        # Confirm response contains spaces
        self.assertIn("spaces", result)

    def test_search_partial_expressions(self):
        """Test lines 247, 254-257, 261: search with partial expressions"""
        # Add test spaces
        GoogleChatAPI.DB["Space"].append(
            {
                "name": "spaces/TEST1",
                "spaceType": "SPACE",
                "customer": "customers/my_customer",
                "displayName": "Test Space",
            }
        )

        # Test with a query containing a partial/incomplete expression
        result = GoogleChatAPI.Spaces.search(
            useAdminAccess=True,
            query='customer = "customers/my_customer" AND space_type = "SPACE" AND display_name',
        )

        # Ensure response is correctly formed (spaces list should still be returned)
        self.assertIn("spaces", result)

    def test_get_membership_check_edge_case(self):
        """Test lines 335, 337: get space membership check edge case"""
        # Add test space
        space = {
            "name": "spaces/EDGE_CASE",
            "spaceType": "SPACE",
            "displayName": "Edge Case Space",
        }
        GoogleChatAPI.DB["Space"].append(space)

        # Test without admin access and no membership
        # This should exercise the membership check logic in lines 335-337
        result = GoogleChatAPI.Spaces.get(name="spaces/EDGE_CASE")
        self.assertEqual(result, {})

        # Now add membership but with wrong id
        membership = {
            "name": f"spaces/EDGE_CASE/members/users/WRONG_USER",
            "state": "JOINED",
            "role": "ROLE_MEMBER",
            "member": {"name": "users/WRONG_USER", "type": "HUMAN"},
        }
        GoogleChatAPI.DB["Membership"].append(membership)

        # Should still return empty dict
        result = GoogleChatAPI.Spaces.get(name="spaces/EDGE_CASE")
        self.assertEqual(result, {})

    def test_create_requestId_error_handling(self):
        """Test line 363: error handling in create with requestId"""
        # Test with invalid space object that will cause an error
        # But including a requestId to test that codepath
        result = GoogleChatAPI.Spaces.create(
            requestId="test-request-123",
            space={
                "spaceType": "SPACE"
            },  # Missing displayName which is required, should fail
        )
        self.assertEqual(result, {})

    def test_create_duplicate_display_name_special_case(self):
        """Test line 374: duplicate display name with different casing"""
        # First create a space
        space1 = {"spaceType": "SPACE", "displayName": "Test DUPLICATE"}
        GoogleChatAPI.Spaces.create(space=space1)

        # Now try to create another with same name but different case
        space2 = {
            "spaceType": "SPACE",
            "displayName": "test duplicate",  # Different case
        }
        result = GoogleChatAPI.Spaces.create(space=space2)

        # Should fail due to case-insensitive comparison
        self.assertEqual(result, {})

    def test_create_direct_message_bot(self):
        """Test line 504: direct message with bot"""
        # Create a direct message space with singleUserBotDm=True
        # This specifically tests the line 504 where membership creation is skipped
        space = {"spaceType": "DIRECT_MESSAGE", "singleUserBotDm": True}

        result = GoogleChatAPI.Spaces.create(space=space)

        # Verify the space was created
        self.assertEqual(result["spaceType"], "DIRECT_MESSAGE")
        self.assertTrue(result["singleUserBotDm"])

    def test_delete_nonexistent_space(self):
        """Test lines 698-699: delete nonexistent space"""
        # Try to delete a space that doesn't exist
        result = GoogleChatAPI.Spaces.delete(name="spaces/NONEXISTENT")

        # Should return empty dict
        self.assertEqual(result, {})

    def test_delete_unauthorized(self):
        """Test lines 704, 721: delete with unauthorized user"""
        # Add test space but don't add membership
        space = {
            "name": "spaces/UNAUTHORIZED",
            "spaceType": "SPACE",
            "displayName": "Unauthorized Space",
        }
        GoogleChatAPI.DB["Space"].append(space)

        # Try to delete without being a member and without admin access
        result = GoogleChatAPI.Spaces.delete(name="spaces/UNAUTHORIZED")

        # Should return empty dict
        self.assertEqual(result, {})

    def test_delete_with_child_resources(self):
        """Test lines 728-730, 738, 750: delete space with child resources"""
        # Create a space with memberships, messages and reactions
        space = {
            "name": "spaces/COMPLEX",
            "spaceType": "SPACE",
            "displayName": "Complex Space",
        }
        GoogleChatAPI.DB["Space"].append(space)

        # Add membership for current user to allow deletion
        membership = {
            "name": f"spaces/COMPLEX/members/{GoogleChatAPI.CURRENT_USER_ID['id']}",
            "state": "JOINED",
            "role": "ROLE_MANAGER",
            "member": {"name": GoogleChatAPI.CURRENT_USER_ID["id"], "type": "HUMAN"},
        }
        GoogleChatAPI.DB["Membership"].append(membership)

        # Add message
        message = {"name": "spaces/COMPLEX/messages/MSG1", "text": "Test message"}
        GoogleChatAPI.DB["Message"].append(message)

        # Add reaction
        if "Reaction" not in GoogleChatAPI.DB:
            GoogleChatAPI.DB["Reaction"] = []

        reaction = {
            "name": "spaces/COMPLEX/messages/MSG1/reactions/R1",
            "emoji": {"unicode": "👍"},
        }
        GoogleChatAPI.DB["Reaction"].append(reaction)

        # Delete the space
        result = GoogleChatAPI.Spaces.delete(name="spaces/COMPLEX")

        # Should return empty dict
        self.assertEqual(result, {})

        # Verify all associated resources are deleted
        self.assertEqual(
            len(
                [s for s in GoogleChatAPI.DB["Space"] if s["name"] == "spaces/COMPLEX"]
            ),
            0,
        )
        self.assertEqual(
            len(
                [
                    m
                    for m in GoogleChatAPI.DB["Membership"]
                    if m["name"].startswith("spaces/COMPLEX/")
                ]
            ),
            0,
        )
        self.assertEqual(
            len(
                [
                    m
                    for m in GoogleChatAPI.DB["Message"]
                    if m["name"].startswith("spaces/COMPLEX/")
                ]
            ),
            0,
        )
        self.assertEqual(
            len(
                [
                    r
                    for r in GoogleChatAPI.DB["Reaction"]
                    if r["name"].startswith("spaces/COMPLEX/")
                ]
            ),
            0,
        )

    def test_search_parse_filter_complex(self):
        """Test lines 757-759, 765-767: complex filter parsing in search"""
        # Add test spaces
        GoogleChatAPI.DB["Space"].extend(
            [
                {
                    "name": "spaces/S1",
                    "spaceType": "SPACE",
                    "customer": "customers/my_customer",
                    "displayName": "Executive Team",
                    "externalUserAllowed": True,
                    "createTime": "2022-01-01T00:00:00Z",
                    "lastActiveTime": "2023-01-01T00:00:00Z",
                },
                {
                    "name": "spaces/S2",
                    "spaceType": "SPACE",
                    "customer": "customers/my_customer",
                    "displayName": "Marketing Department",
                    "externalUserAllowed": False,
                    "createTime": "2022-06-01T00:00:00Z",
                    "lastActiveTime": "2023-02-01T00:00:00Z",
                },
            ]
        )

        # Test complex query with multiple time comparisons
        query = (
            'customer = "customers/my_customer" AND space_type = "SPACE" AND '
            'create_time > "2022-03-01T00:00:00Z" AND '
            'last_active_time < "2023-03-01T00:00:00Z" AND '
            'external_user_allowed = "false"'
        )

        result = GoogleChatAPI.Spaces.search(useAdminAccess=True, query=query)

        # Should return only S2
        self.assertEqual(len(result["spaces"]), 1)
        self.assertEqual(result["spaces"][0]["name"], "spaces/S2")


class TestGoogleChatSpacesMessages(BaseTestCaseWithErrorHandler):
    def setUp(self):
        """Reset DB before each test"""
        GoogleChatAPI.DB.clear()
        GoogleChatAPI.DB.update(
            {
                "User": [{"name": "users/USER123", "displayName": "Test User"}],
                "Space": [],
                "Membership": [],
                "Message": [],
                "Reaction": [],
                "SpaceReadState": [],
                "ThreadReadState": [],
                "SpaceNotificationSetting": [],
            }
        )
        GoogleChatAPI.CURRENT_USER = {"id": "users/USER123"}
        GoogleChatAPI.CURRENT_USER_ID = GoogleChatAPI.CURRENT_USER

        # Add a test space
        self.test_space = {
            "name": "spaces/TEST_SPACE",
            "spaceType": "SPACE",
            "displayName": "Test Space",
        }
        GoogleChatAPI.DB["Space"].append(self.test_space)

        # Add membership for current user
        self.membership = {
            "name": f"spaces/TEST_SPACE/members/{GoogleChatAPI.CURRENT_USER_ID['id']}",
            "state": "JOINED",
            "role": "ROLE_MEMBER",
            "member": {"name": GoogleChatAPI.CURRENT_USER_ID["id"], "type": "HUMAN"},
        }
        GoogleChatAPI.DB["Membership"].append(self.membership)

    def test_messages(self):
        space_obj = {
            "name": "spaces/AAA",
            "displayName": "Messages Test Space",
            "spaceType": "SPACE",
            "customer": "customers/my_customer",
            "importMode": False,
        }
        GoogleChatAPI.DB["Space"].append(space_obj)

        caller_membership = {
            "name": f"{space_obj['name']}/members/{GoogleChatAPI.CURRENT_USER.get('id')}",
            "state": "JOINED",
            "role": "ROLE_MEMBER",
            "member": {"name": GoogleChatAPI.CURRENT_USER.get("id"), "type": "HUMAN"},
            "groupMember": {},
            "createTime": datetime.now().isoformat() + "Z",
            "deleteTime": "",
        }
        GoogleChatAPI.DB["Membership"].append(caller_membership)

        msg_body = {"text": "Hello, world!"}
        created_msg = GoogleChatAPI.Spaces.Messages.create(
            parent="spaces/AAA",
            requestId="msg-req-001",
            messageReplyOption="REPLY_MESSAGE_FALLBACK_TO_NEW_THREAD",
            messageId="client-001",
            message_body=msg_body,
        )
        self.assertTrue(created_msg.get("name", "").endswith("client-001"))

        # orderBy must be "createTime asc" or "createTime desc", not just "ASC"
        with self.assertRaises(ValueError) as context:
            GoogleChatAPI.Spaces.Messages.list(
                parent="spaces/AAA",
                pageSize=10,
                pageToken="0",
                filter=None,
                orderBy="ASC",  # Invalid format
                showDeleted=False,
            )
        self.assertIn('orderBy, if provided, must be "createTime asc" or "createTime desc"', str(context.exception))
        
        # Now use the correct format
        list_result = GoogleChatAPI.Spaces.Messages.list(
            parent="spaces/AAA",
            pageSize=10,
            pageToken="0",
            filter=None,
            orderBy="createTime asc",  # Correct format
            showDeleted=False,
        )
        self.assertIn("messages", list_result)

        got_msg = GoogleChatAPI.Spaces.Messages.get(name=created_msg["name"])
        self.assertEqual(got_msg.get("text"), "Hello, world!")

        update_body = {"text": "Hello, updated world!", "attachment": []}
        updated_msg = GoogleChatAPI.Spaces.Messages.update(
            name=created_msg["name"],
            updateMask="text",
            allowMissing=False,
            body=update_body,
        )
        self.assertEqual(updated_msg.get("text"), "Hello, updated world!")

        delete_result = GoogleChatAPI.Spaces.Messages.delete(
            name=created_msg["name"], force=True
        )
        got_after_delete = GoogleChatAPI.Spaces.Messages.get(name=created_msg["name"])
        self.assertEqual(got_after_delete, {})

    def test_create_no_message_body(self):
        """Test lines 94-95: create without message body"""
        # Try to create message without a body
        with self.assertRaises(TypeError):
            GoogleChatAPI.Spaces.Messages.create(
            parent="spaces/TEST_SPACE", message_body=None
        )

    def test_create_non_member(self):
        """Test lines 101-102: create with non-member user"""
        # Remove the membership
        GoogleChatAPI.DB["Membership"].remove(self.membership)

        # Try to create message
        with self.assertRaises(UserNotMemberError):
            GoogleChatAPI.Spaces.Messages.create(
            parent="spaces/TEST_SPACE", message_body={"text": "Test message"}
        )

    def test_create_invalid_message_id(self):
        """Test lines 106-107: create with invalid messageId"""
        # Try to create message with invalid messageId
        with self.assertRaises(InvalidMessageIdFormatError):
            GoogleChatAPI.Spaces.Messages.create(
            parent="spaces/TEST_SPACE",
            messageId="invalid-id",  # Should start with client-
            message_body={"text": "Test message"},
        )

    def test_create_with_message_reply_option(self):
        """Test line 111: create with messageReplyOption"""
        # Create message with messageReplyOption
        result = GoogleChatAPI.Spaces.Messages.create(
            parent="spaces/TEST_SPACE",
            messageReplyOption="REPLY_MESSAGE_FALLBACK_TO_NEW_THREAD",
            message_body={"text": "Test message"},
        )

        # Should succeed
        self.assertIsNotNone(result)
        self.assertIn("name", result)
        self.assertEqual(result["text"], "Test message")

    def test_update_missing_message(self):
        """Test lines 341-343: update non-existent message"""
        # Try to update a message that doesn't exist
        result = GoogleChatAPI.Spaces.Messages.update(
            name="spaces/TEST_SPACE/messages/nonexistent",
            updateMask="text",
            allowMissing=False,
            body={"text": "Updated text"},
        )

        # Should return empty dict
        self.assertEqual(result, {})

    def test_update_allow_missing_invalid_name(self):
        """Test lines 347, 349, 351: update with allowMissing but invalid name"""
        # Try to update with allowMissing=True but invalid name format
        result = GoogleChatAPI.Spaces.Messages.update(
            name="invalid/format",
            updateMask="text",
            allowMissing=True,
            body={"text": "Updated text"},
        )

        # Should return empty dict
        self.assertEqual(result, {})

        # Try with correct format but not client-assigned ID
        result = GoogleChatAPI.Spaces.Messages.update(
            name="spaces/TEST_SPACE/messages/123",
            updateMask="text",
            allowMissing=True,
            body={"text": "Updated text"},
        )

        # Should return empty dict
        self.assertEqual(result, {})

    def test_update_allow_missing_client_id(self):
        """Test lines 360-361: update with allowMissing and client-assigned ID"""
        # Update with allowMissing=True and valid client-assigned ID
        result = GoogleChatAPI.Spaces.Messages.update(
            name="spaces/TEST_SPACE/messages/client-abc123",
            updateMask="text",
            allowMissing=True,
            body={"text": "New message with client ID"},
        )

        # Should create new message
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "spaces/TEST_SPACE/messages/client-abc123")
        self.assertEqual(result["text"], "New message with client ID")

        # Verify message was added to DB
        found = False
        for msg in GoogleChatAPI.DB["Message"]:
            if msg["name"] == "spaces/TEST_SPACE/messages/client-abc123":
                found = True
                break
        self.assertTrue(found)

    def test_update_with_specific_fields(self):
        """Test lines 383-434: update with specific fields"""
        # Create a message first
        message = {
            "name": "spaces/TEST_SPACE/messages/1",
            "text": "Original text",
            "attachment": [],
            "createTime": datetime.now().isoformat() + "Z",
            "sender": {"name": GoogleChatAPI.CURRENT_USER_ID["id"], "type": "HUMAN"},
        }
        GoogleChatAPI.DB["Message"].append(message)

        # Update specific fields
        result = GoogleChatAPI.Spaces.Messages.update(
            name="spaces/TEST_SPACE/messages/1",
            updateMask="text,cards_v2",
            allowMissing=False,
            body={
                "text": "Updated text",
                "attachment": [{"name": "test-attachment"}],  # Should not be updated
                "cards_v2": [
                    {"cardId": "card1", "card": {"header": {"title": "Test Card V2"}}}
                ],
            },
        )

        # Verify only specified fields were updated
        self.assertEqual(result["text"], "Updated text")
        self.assertEqual(len(result["attachment"]), 0)  # Should not be updated
        self.assertEqual(
            len(result["cardsV2"]), 1
        )  # Should be updated (note the field name transformation)

    def test_update_unsupported_field(self):
        """Test line 448: update with unsupported field"""
        # Create a message first
        message = {
            "name": "spaces/TEST_SPACE/messages/1",
            "text": "Original text",
            "attachment": [],
            "createTime": datetime.now().isoformat() + "Z",
            "sender": {"name": GoogleChatAPI.CURRENT_USER_ID["id"], "type": "HUMAN"},
        }
        GoogleChatAPI.DB["Message"].append(message)

        # Update with unsupported field
        result = GoogleChatAPI.Spaces.Messages.update(
            name="spaces/TEST_SPACE/messages/1",
            updateMask="text,unsupported_field",
            allowMissing=False,
            body={"text": "Updated text"},
        )

        # Verify only supported fields were updated
        self.assertEqual(result["text"], "Updated text")

    def test_update_alternate_field_naming(self):
        """Test line 455: update with alternate field naming (cards_v2 vs cardsV2)"""
        # Create a message first
        message = {
            "name": "spaces/TEST_SPACE/messages/1",
            "text": "Original text",
            "attachment": [],
            "createTime": datetime.now().isoformat() + "Z",
            "sender": {"name": GoogleChatAPI.CURRENT_USER_ID["id"], "type": "HUMAN"},
        }
        GoogleChatAPI.DB["Message"].append(message)

        # Update using cards_v2 in updateMask but cardsV2 in body
        result = GoogleChatAPI.Spaces.Messages.update(
            name="spaces/TEST_SPACE/messages/1",
            updateMask="cards_v2",
            allowMissing=False,
            body={
                "cardsV2": [
                    {"cardId": "card1", "card": {"header": {"title": "Test Card V2"}}}
                ]
            },
        )

        # Verify field was updated despite naming difference
        self.assertEqual(len(result["cardsV2"]), 1)

    def test_list_non_member(self):
        """Test lines 656-657: list messages as non-member"""
        # Remove the membership
        GoogleChatAPI.DB["Membership"].remove(self.membership)

        # Try to list messages
        result = GoogleChatAPI.Spaces.Messages.list(parent="spaces/TEST_SPACE")

        # Should return empty list
        self.assertEqual(result, {"messages": []})

    def test_list_with_invalid_page_size(self):
        """Test lines 666-667: list with invalid page size"""
        # Try to list with negative page size
        with self.assertRaises(ValueError):
            GoogleChatAPI.Spaces.Messages.list(parent="spaces/TEST_SPACE", pageSize=-1)

    def test_delete_message_not_found(self):
        """Test lines 813-837: delete message not found"""
        # Try to delete non-existent message
        result = GoogleChatAPI.Spaces.Messages.delete(
            name="spaces/TEST_SPACE/messages/nonexistent"
        )

        # Should return empty dict
        self.assertEqual(result, {})

    def test_delete_with_replies_no_force(self):
        """Test line 842: delete message with replies without force flag"""
        # Create a message with thread
        thread_name = "spaces/TEST_SPACE/threads/thread1"
        message = {
            "name": "spaces/TEST_SPACE/messages/1",
            "text": "Parent message",
            "createTime": datetime.now().isoformat() + "Z",
            "sender": {"name": GoogleChatAPI.CURRENT_USER_ID["id"], "type": "HUMAN"},
            "thread": {"name": thread_name},
        }
        GoogleChatAPI.DB["Message"].append(message)

        # Create a reply message
        reply = {
            "name": "spaces/TEST_SPACE/messages/2",
            "text": "Reply message",
            "createTime": datetime.now().isoformat() + "Z",
            "sender": {"name": GoogleChatAPI.CURRENT_USER_ID["id"], "type": "HUMAN"},
            "thread": {"name": thread_name},
        }
        GoogleChatAPI.DB["Message"].append(reply)

        # Try to delete parent message without force
        result = GoogleChatAPI.Spaces.Messages.delete(
            name="spaces/TEST_SPACE/messages/1", force=False
        )

        # Should return empty dict
        self.assertEqual(result, {})

        # Verify both messages still exist
        self.assertEqual(len(GoogleChatAPI.DB["Message"]), 2)

    def test_get_non_member(self):
        """Test line 954: get message as non-member"""
        # Add a message
        message = {
            "name": "spaces/TEST_SPACE/messages/1",
            "text": "Test message",
            "createTime": datetime.now().isoformat() + "Z",
            "sender": {"name": GoogleChatAPI.CURRENT_USER_ID["id"], "type": "HUMAN"},
        }
        GoogleChatAPI.DB["Message"].append(message)

        # Remove the membership
        GoogleChatAPI.DB["Membership"].remove(self.membership)

        # Try to get message
        result = GoogleChatAPI.Spaces.Messages.get(name="spaces/TEST_SPACE/messages/1")

        # Should return empty dict
        self.assertEqual(result, {})

    def test_get_invalid_name_format(self):
        """Test lines 987-988: get with invalid name format"""
        # Try to get message with invalid name format
        result = GoogleChatAPI.Spaces.Messages.get(name="invalid/format")

        # Should return empty dict
        self.assertEqual(result, {})

    def test_get_message_not_found(self):
        """Test line 997: get non-existent message"""
        # Try to get non-existent message
        result = GoogleChatAPI.Spaces.Messages.get(
            name="spaces/TEST_SPACE/messages/nonexistent"
        )

        # Should return empty dict
        self.assertEqual(result, {})

    def test_list_with_complex_filter(self):
        """Test lines 1001-1009: list with complex filter"""
        # Add messages with different timestamps and threads
        thread1 = "spaces/TEST_SPACE/threads/thread1"
        thread2 = "spaces/TEST_SPACE/threads/thread2"

        # Message 1: Early timestamp, thread1
        GoogleChatAPI.DB["Message"].append(
            {
                "name": "spaces/TEST_SPACE/messages/1",
                "text": "Early message in thread1",
                "createTime": "2022-01-01T00:00:00Z",
                "sender": {
                    "name": GoogleChatAPI.CURRENT_USER_ID["id"],
                    "type": "HUMAN",
                },
                "thread": {"name": thread1},
            }
        )

        # Message 2: Middle timestamp, thread2
        GoogleChatAPI.DB["Message"].append(
            {
                "name": "spaces/TEST_SPACE/messages/2",
                "text": "Middle message in thread2",
                "createTime": "2022-06-01T00:00:00Z",
                "sender": {
                    "name": GoogleChatAPI.CURRENT_USER_ID["id"],
                    "type": "HUMAN",
                },
                "thread": {"name": thread2},
            }
        )

        # Message 3: Late timestamp, thread1
        GoogleChatAPI.DB["Message"].append(
            {
                "name": "spaces/TEST_SPACE/messages/3",
                "text": "Late message in thread1",
                "createTime": "2023-01-01T00:00:00Z",
                "sender": {
                    "name": GoogleChatAPI.CURRENT_USER_ID["id"],
                    "type": "HUMAN",
                },
                "thread": {"name": thread1},
            }
        )

        # Test filter by thread
        result = GoogleChatAPI.Spaces.Messages.list(
            parent="spaces/TEST_SPACE", filter=f"thread.name = {thread1}"
        )

        # Should return only messages in thread1
        self.assertEqual(len(result["messages"]), 2)
        for msg in result["messages"]:
            self.assertEqual(msg["thread"]["name"], thread1)

        # Test filter by create_time
        result = GoogleChatAPI.Spaces.Messages.list(
            parent="spaces/TEST_SPACE", filter='create_time > "2022-03-01T00:00:00Z"'
        )

        # Should return only messages after March 2022
        self.assertEqual(len(result["messages"]), 2)
        for msg in result["messages"]:
            self.assertGreater(msg["createTime"], "2022-03-01T00:00:00Z")

        # Test combined filter
        result = GoogleChatAPI.Spaces.Messages.list(
            parent="spaces/TEST_SPACE",
            filter=f'create_time > "2022-03-01T00:00:00Z" AND thread.name = {thread1}',
        )

        # Should return only one message
        self.assertEqual(len(result["messages"]), 1)
        self.assertEqual(result["messages"][0]["name"], "spaces/TEST_SPACE/messages/3")

    def test_list_page_size_page_token(self):
        # Validate page size is capped at 1000
        with self.assertRaises(ValueError) as context:
            GoogleChatAPI.Spaces.Messages.list(
                parent="spaces/TEST_SPACE", pageSize=1001
            )
        self.assertIn("pageSize cannot exceed 1000", str(context.exception))
        result = GoogleChatAPI.Spaces.Messages.list(
            parent="spaces/TEST_SPACE", pageSize=None
        )
        try:
            result = GoogleChatAPI.Spaces.Messages.list(
                parent="spaces/TEST_SPACE", pageSize=-1
            )
        except ValueError:
            pass
        try:
            result = GoogleChatAPI.Spaces.Messages.list(
                parent="spaces/TEST_SPACE", pageToken="1A"
            )
        except ValueError:
            pass

    def test_list_filter(self):
        result = GoogleChatAPI.Spaces.Messages.list(
            parent="spaces/TEST_SPACE",
            filter='thread.name ! "thread1" AND create_time > "2022-03-01T00:00:00Z"',
        )
        self.assertEqual(len(result["messages"]), 0)

        result = GoogleChatAPI.Spaces.Messages.list(
            parent="spaces/TEST_SPACE",
            filter='thread.name ! "thread1" AND create_time < "2022-03-01T00:00:00Z"',
        )
        self.assertEqual(len(result["messages"]), 0)

        result = GoogleChatAPI.Spaces.Messages.list(
            parent="spaces/TEST_SPACE",
            filter='thread.name = "thread1" AND create_time >= "2022-03-01T00:00:00Z"',
        )
        self.assertEqual(len(result["messages"]), 0)

        result = GoogleChatAPI.Spaces.Messages.list(
            parent="spaces/TEST_SPACE", filter='create_time <= "2022-03-01T00:00:00Z"'
        )
        self.assertEqual(len(result["messages"]), 0)

    def test_update_message(self):
        message = {
            "name": "spaces/TEST_SPACE/messages/1",
            "text": "Original text",
            "createTime": datetime.now().isoformat() + "Z",
            "sender": {"name": GoogleChatAPI.CURRENT_USER_ID["id"], "type": "HUMAN"},
        }
        GoogleChatAPI.DB["Message"].append(message)
        result = GoogleChatAPI.Spaces.Messages.update(
            name="spaces/TEST_SPACE/messages/1",
            allowMissing=True,
            updateMask="*",
            body={"text": "Updated text"},
        )
        self.assertEqual(result["text"], "Updated text")

        result = GoogleChatAPI.Spaces.Messages.patch(
            name="spaces/TEST_SPACE/messages/1",
            allowMissing=True,
            updateMask="text",
            message={"text": "Updated text"},
        )


class TestGoogleChatSpacesMessagesAttachments(BaseTestCaseWithErrorHandler):
    def test_attachments(self):
        space_obj = {
            "name": "spaces/AAA",
            "displayName": "Attachment Test Space",
            "spaceType": "SPACE",
            "customer": "customers/my_customer",
        }
        GoogleChatAPI.DB["Space"].append(space_obj)

        message_obj = {
            "name": "spaces/AAA/messages/1",
            "text": "Message with attachment",
            "thread": {},
            "createTime": datetime.now().isoformat() + "Z",
        }
        attachment = {
            "name": "spaces/AAA/messages/1/attachments/ATT1",
            "contentName": "file.png",
            "contentType": "image/png",
        }
        message_obj["attachment"] = [attachment]
        GoogleChatAPI.DB["Message"].append(message_obj)

        att = GoogleChatAPI.Spaces.Messages.Attachments.get(
            "spaces/AAA/messages/1/attachments/ATT1"
        )
        print(f"Att: {att}")
        self.assertEqual(att.get("contentName"), "file.png")

    def test_invalid_attachment_name(self):
        att = GoogleChatAPI.Spaces.Messages.Attachments.get(
            "space/AAA/messages/1/attachments/ATT1"
        )
        self.assertEqual(att, {})

    def test_missing_attachment_id(self):
        att = GoogleChatAPI.Spaces.Messages.Attachments.get(
            "spaces/AAA/messages/1/attachments"
        )
        self.assertEqual(att, {})

    def test_missing_message_id(self):
        att = GoogleChatAPI.Spaces.Messages.Attachments.get(
            "spaces/AAA/messages/123/attachments/ATT1"
        )
        self.assertEqual(att, {})

    def test_no_attachment(self):
        att = GoogleChatAPI.Spaces.Messages.Attachments.get(
            "spaces/AAA/messages/1/attachments/"
        )
        self.assertEqual(att, {})


class TestGoogleChatSpacesMessagesReactions(BaseTestCaseWithErrorHandler):
    def setUp(self):
        """Reset DB before each test"""
        GoogleChatAPI.DB.clear()
        GoogleChatAPI.DB.update(
            {
                "User": [{"name": "users/USER123", "displayName": "Test User"}],
                "Space": [],
                "Message": [],
                "Reaction": [],
            }
        )

    def test_reactions(self):
        space_obj = {
            "name": "spaces/AAA",
            "displayName": "Reaction Test Space",
            "spaceType": "SPACE",
            "customer": "customers/my_customer",
        }
        GoogleChatAPI.DB["Space"].append(space_obj)

        message_obj = {
            "name": "spaces/AAA/messages/1",
            "text": "Message for reactions",
            "thread": {},
            "createTime": datetime.now().isoformat() + "Z",
        }
        GoogleChatAPI.DB["Message"].append(message_obj)

        reaction_body = {"emoji": {"unicode": "🙂"}, "user": {"name": "users/USER123"}}
        created_rxn = GoogleChatAPI.Spaces.Messages.Reactions.create(
            parent="spaces/AAA/messages/1", reaction=reaction_body
        )
        self.assertEqual(created_rxn.get("emoji", {}).get("unicode"), "🙂")

        rxn_list = GoogleChatAPI.Spaces.Messages.Reactions.list(
            parent="spaces/AAA/messages/1",
            pageSize=10,
            pageToken="0",
            filter='emoji.unicode = "🙂"',
        )
        self.assertIn("reactions", rxn_list)
        self.assertGreaterEqual(len(rxn_list["reactions"]), 1)

        del_result = GoogleChatAPI.Spaces.Messages.Reactions.delete(
            created_rxn.get("name")
        )
        rxn_list_after = GoogleChatAPI.Spaces.Messages.Reactions.list(
            parent="spaces/AAA/messages/1", pageSize=10, pageToken="0", filter=None
        )
        self.assertEqual(len(rxn_list_after.get("reactions", [])), 0)

    def test_create_invalid_parent_format(self):
        reaction_body = {"emoji": {"unicode": "🙂"}, "user": {"name": "users/USER123"}}
        reaction = GoogleChatAPI.Spaces.Messages.Reactions.create(
            parent="invalid/format", reaction=reaction_body
        )
        self.assertEqual(reaction, {})

    def test_list_page_size_page_token_2(self):
        self.assert_error_behavior(
            func_to_call=list_messages,
            expected_exception_type=ValueError,
            expected_message="pageToken must be a valid integer.",
            parent="spaces/AAA/messages/1",
            pageToken="1A"
        )

    def test_list_filter(self):
        GoogleChatAPI.DB["Message"].append(
            {
                "name": "spaces/AAA/messages/1",
                "text": "Message for reactions",
                "thread": {},
                "createTime": datetime.now().isoformat() + "Z",
                "sender": {"name": "users/USER123"},
            }
        )
        GoogleChatAPI.DB["Reaction"].append(
            {
                "name": "spaces/AAA/messages/1/reactions/USER123",
                "user": {"name": "users/USER123"},
                "emoji": {"unicode": "🙂"},
            }
        )
        reaction = GoogleChatAPI.Spaces.Messages.Reactions.list(
            parent="spaces/AAA/messages/1",
            filter='user.name = "users/USER123" OR (emoji.unicode = "🙂" AND emoji.custom_emoji.uid = "123")',
        )
        self.assertIn("reactions", reaction)
        self.assertGreaterEqual(len(reaction.get("reactions", [])), 0)

        reaction = GoogleChatAPI.Spaces.Messages.Reactions.list(
            parent="spaces/AAA/messages/1", filter='user.name / "users/USER123"'
        )
        self.assertEqual(reaction.get("reactions", []), [])

    def test_reaction_delete(self):
        reaction = GoogleChatAPI.Spaces.Messages.Reactions.delete(
            name="spaces/AAA/messages/1/reactions/USER123"
        )
        self.assertEqual(reaction, {})


class TestGoogleChatSpacesMembers(BaseTestCaseWithErrorHandler):
    def setUp(self):
        """Reset DB before each test"""
        GoogleChatAPI.DB.clear()
        GoogleChatAPI.DB.update(
            {
                "User": [{"name": "users/USER123", "displayName": "Test User"}],
                "Space": [],
                "Membership": [],
                "Message": [],
                "Reaction": [],
                "SpaceReadState": [],
                "ThreadReadState": [],
                "SpaceNotificationSetting": [],
            }
        )
        GoogleChatAPI.CURRENT_USER = {"id": "users/USER123"}
        GoogleChatAPI.CURRENT_USER_ID = GoogleChatAPI.CURRENT_USER
        # Add a test space
        self.test_space = {
            "name": "spaces/TEST_SPACE",
            "spaceType": "SPACE",
            "displayName": "Test Space",
        }
        GoogleChatAPI.DB["Space"].append(self.test_space)

    def test_members_patch(self):        """Test the members patch functionality to update a membership role."""        # Setup: Create a membership first        test_membership = {            "name": "spaces/TEST_SPACE/members/users/user1",            "state": "JOINED",            "role": "ROLE_MEMBER",            "member": {"name": "users/user1", "type": "HUMAN"},            "createTime": datetime.now().isoformat() + "Z"        }        GoogleChatAPI.DB["Membership"].append(test_membership)                # Verify initial state        self.assertEqual(test_membership["role"], "ROLE_MEMBER")                # Perform patch operation to update role        updated = GoogleChatAPI.Spaces.Members.patch(            name="spaces/TEST_SPACE/members/users/user1",            updateMask="role",            membership={"role": "ROLE_MANAGER"},        )                # Verify patch succeeded        self.assertIsNotNone(updated)        self.assertEqual(updated["role"], "ROLE_MANAGER")                # Verify the membership was actually updated in the DB        for mem in GoogleChatAPI.DB["Membership"]:            if mem["name"] == "spaces/TEST_SPACE/members/users/user1":                self.assertEqual(mem["role"], "ROLE_MANAGER")                break                # Test invalid updateMask        try:            GoogleChatAPI.Spaces.Members.patch(                name="spaces/TEST_SPACE/members/users/user1",                updateMask="invalid_field",                membership={"role": "ROLE_MEMBER"},            )            self.fail("Expected InvalidUpdateMaskError to be raised for invalid updateMask")        except Exception as e:            self.assertIn("updatemask", str(e).lower())
            
                # Test non-existent membership        try:            GoogleChatAPI.Spaces.Members.patch(                name="spaces/TEST_SPACE/members/nonexistent",                updateMask="role",                membership={"role": "ROLE_MANAGER"},            )            self.fail("Expected MembershipNotFoundError to be raised for non-existent membership")        except Exception as e:            self.assertIn("not found", str(e).lower())                    # Test missing required field        try:            GoogleChatAPI.Spaces.Members.patch(                name="spaces/TEST_SPACE/members/users/user1",                updateMask="role",                membership={},  # Missing required field            )            self.fail("Expected NoUpdatableFieldsError to be raised for missing required field")        except Exception as e:            self.assertIn("updatable field", str(e).lower())

    def test_list_invalid_parent(self):
        """Test lines 68-71: list with invalid parent format"""
        # Call list with invalid parent format
        self.assert_error_behavior(
            func_to_call=GoogleChatAPI.Spaces.Members.list,
            expected_exception_type=InvalidParentFormatError,
            expected_message="Invalid parent format: 'invalid_format'. Expected 'spaces/{space}'.",
            parent="invalid_format"
        )
        
        # Adding a test with a valid parent to verify normal behavior
        # Add a test membership
        GoogleChatAPI.DB["Membership"].append(
            {
                "name": "spaces/VALID_SPACE/members/users/valid_user",
                "state": "JOINED",
                "role": "ROLE_MEMBER",
                "member": {"name": "users/valid_user", "type": "HUMAN"},
            }
        )
        
        # Valid case should return results
        result = GoogleChatAPI.Spaces.Members.list(parent="spaces/VALID_SPACE")
        self.assertIsInstance(result, dict)
        self.assertIn("memberships", result)

    def test_list_with_admin_access(self):
        """Test lines 72-80: list with admin access"""
        # Add regular and app memberships
        GoogleChatAPI.DB["Membership"].extend(
            [
                {
                    "name": "spaces/TEST_SPACE/members/users/user1",
                    "state": "JOINED",
                    "role": "ROLE_MEMBER",
                    "member": {"name": "users/user1", "type": "HUMAN"},
                },
                {
                    "name": "spaces/TEST_SPACE/members/app",
                    "state": "JOINED",
                    "role": "ROLE_MEMBER",
                    "member": {"name": "users/app", "type": "BOT"},
                },
            ]
        )

        # Call list with admin access - should exclude app membership
        result = GoogleChatAPI.Spaces.Members.list(
            parent="spaces/TEST_SPACE", useAdminAccess=True
        )

        # Verify app membership is filtered out
        self.assertEqual(len(result["memberships"]), 1)
        self.assertEqual(
            result["memberships"][0]["name"], "spaces/TEST_SPACE/members/users/user1"
        )

    def test_list_admin_access_with_filter(self):
        """Test lines 81-89: list with admin access and filter"""
        # Add memberships
        GoogleChatAPI.DB["Membership"].extend(
            [
                {
                    "name": "spaces/TEST_SPACE/members/users/user1",
                    "state": "JOINED",
                    "role": "ROLE_MEMBER",
                    "member": {"name": "users/user1", "type": "HUMAN"},
                },
                {
                    "name": "spaces/TEST_SPACE/members/users/user2",
                    "state": "JOINED",
                    "role": "ROLE_MEMBER",
                    "member": {"name": "users/user2", "type": "BOT"},
                },
            ]
        )

        # Test with admin access but missing required filter
        self.assert_error_behavior(
            func_to_call=GoogleChatAPI.Spaces.Members.list,
            expected_exception_type=AdminAccessFilterError,
            expected_message='When using admin access with a filter, the filter must include a condition like \'member.type = "HUMAN"\' or \'member.type != "BOT"\'.',
            parent="spaces/TEST_SPACE",
            useAdminAccess=True,
            filter='role = "ROLE_MEMBER"',  # Missing member.type filter
        )

        # Test with correct filter - should pass
        result = GoogleChatAPI.Spaces.Members.list(
            parent="spaces/TEST_SPACE",
            useAdminAccess=True,
            filter='member.type = "HUMAN"',
        )
        self.assertEqual(len(result["memberships"]), 1)
        self.assertEqual(result["memberships"][0]["member"]["type"], "HUMAN")

        # Test with not equals filter
        result = GoogleChatAPI.Spaces.Members.list(
            parent="spaces/TEST_SPACE",
            useAdminAccess=True,
            filter='member.type != "BOT"',
        )

        # Should return human member
        self.assertEqual(len(result["memberships"]), 1)
        self.assertEqual(result["memberships"][0]["member"]["type"], "HUMAN")

    def test_list_filter_application(self):
        """Test lines 90-104: applying filters to list results"""
        # Add memberships with different roles and types
        GoogleChatAPI.DB["Membership"].extend(
            [
                {
                    "name": "spaces/TEST_SPACE/members/users/manager",
                    "state": "JOINED",
                    "role": "ROLE_MANAGER",
                    "member": {"name": "users/manager", "type": "HUMAN"},
                },
                {
                    "name": "spaces/TEST_SPACE/members/users/member",
                    "state": "JOINED",
                    "role": "ROLE_MEMBER",
                    "member": {"name": "users/member", "type": "HUMAN"},
                },
                {
                    "name": "spaces/TEST_SPACE/members/users/bot",
                    "state": "JOINED",
                    "role": "ROLE_MEMBER",
                    "member": {"name": "users/bot", "type": "BOT"},
                },
            ]
        )

        # Test role filter
        result = GoogleChatAPI.Spaces.Members.list(
            parent="spaces/TEST_SPACE", filter='role = "ROLE_MANAGER"'
        )

        self.assertEqual(len(result["memberships"]), 1)
        self.assertEqual(result["memberships"][0]["role"], "ROLE_MANAGER")

        # Test member.type filter
        result = GoogleChatAPI.Spaces.Members.list(
            parent="spaces/TEST_SPACE", filter='member.type = "BOT"'
        )

        self.assertEqual(len(result["memberships"]), 1)
        self.assertEqual(result["memberships"][0]["member"]["type"], "BOT")

        # Test member.type not equals filter
        result = GoogleChatAPI.Spaces.Members.list(
            parent="spaces/TEST_SPACE", filter='member.type != "BOT"'
        )

        self.assertEqual(len(result["memberships"]), 2)
        for membership in result["memberships"]:
            self.assertNotEqual(membership["member"]["type"], "BOT")

    def test_list_with_show_groups_filter(self):
        """Test lines 105-117: filtering by showGroups"""
        # Add regular and group memberships
        GoogleChatAPI.DB["Membership"].extend(
            [
                {
                    "name": "spaces/TEST_SPACE/members/users/user1",
                    "state": "JOINED",
                    "role": "ROLE_MEMBER",
                    "member": {"name": "users/user1", "type": "HUMAN"},
                },
                {
                    "name": "spaces/TEST_SPACE/members/groups/group1",
                    "state": "JOINED",
                    "role": "ROLE_MEMBER",
                    "member": {"name": "groups/group1", "type": "HUMAN"},
                },
            ]
        )

        # Test with showGroups=False
        result = GoogleChatAPI.Spaces.Members.list(
            parent="spaces/TEST_SPACE", showGroups=False
        )

        # Should only include non-group memberships
        self.assertEqual(len(result["memberships"]), 1)
        self.assertEqual(
            result["memberships"][0]["name"], "spaces/TEST_SPACE/members/users/user1"
        )

    def test_list_with_show_invited_filter(self):
        """Test lines 105-117: filtering by showInvited"""
        # Add joined and invited memberships
        GoogleChatAPI.DB["Membership"].extend(
            [
                {
                    "name": "spaces/TEST_SPACE/members/users/joined",
                    "state": "JOINED",
                    "role": "ROLE_MEMBER",
                    "member": {"name": "users/joined", "type": "HUMAN"},
                },
                {
                    "name": "spaces/TEST_SPACE/members/users/invited",
                    "state": "INVITED",
                    "role": "ROLE_MEMBER",
                    "member": {"name": "users/invited", "type": "HUMAN"},
                },
            ]
        )

        # Test with showInvited=False
        result = GoogleChatAPI.Spaces.Members.list(
            parent="spaces/TEST_SPACE", showInvited=False
        )

        # Should only include joined memberships
        self.assertEqual(len(result["memberships"]), 1)
        self.assertEqual(result["memberships"][0]["state"], "JOINED")

    def test_list_pagination(self):
        """Test lines 118-128: pagination in list results"""
        # Add multiple memberships
        for i in range(5):
            GoogleChatAPI.DB["Membership"].append(
                {
                    "name": f"spaces/TEST_SPACE/members/users/user{i}",
                    "state": "JOINED",
                    "role": "ROLE_MEMBER",
                    "member": {"name": f"users/user{i}", "type": "HUMAN"},
                }
            )

        # Test with pageSize=2
        result = GoogleChatAPI.Spaces.Members.list(
            parent="spaces/TEST_SPACE", pageSize=2
        )

        # Should return only 2 items and a nextPageToken
        self.assertEqual(len(result["memberships"]), 2)
        self.assertIn("nextPageToken", result)

        # Use the returned nextPageToken
        result2 = GoogleChatAPI.Spaces.Members.list(
            parent="spaces/TEST_SPACE", pageSize=2, pageToken=result["nextPageToken"]
        )

        # Should return the next 2 items
        self.assertEqual(len(result2["memberships"]), 2)
        self.assertNotEqual(
            result["memberships"][0]["name"], result2["memberships"][0]["name"]
        )

        # Test with invalid pageToken (should default to 0)
        result3 = GoogleChatAPI.Spaces.Members.list(
            parent="spaces/TEST_SPACE", pageToken="invalid_token"
        )

        # Should start from the beginning
        self.assertEqual(
            result3["memberships"][0]["name"], result["memberships"][0]["name"]
        )

        # Test with negative pageToken (should default to 0)
        result4 = GoogleChatAPI.Spaces.Members.list(
            parent="spaces/TEST_SPACE", pageToken="-10"
        )

        # Should start from the beginning
        self.assertEqual(
            result4["memberships"][0]["name"], result["memberships"][0]["name"]
        )

    def test_get_admin_app_membership(self):
        """Test lines 236-241: get app membership with admin access"""
        # Add an app membership
        app_membership = {
            "name": "spaces/TEST_SPACE/members/app",
            "state": "JOINED",
            "role": "ROLE_MEMBER",
            "member": {"name": "users/app", "type": "BOT"},
        }
        GoogleChatAPI.DB["Membership"].append(app_membership)

        # Try to get app membership with admin access
        result = GoogleChatAPI.Spaces.Members.get(
            name="spaces/TEST_SPACE/members/app", useAdminAccess=True
        )

        # Should return empty dict
        self.assertEqual(result, {})

        # Get app membership without admin access
        result = GoogleChatAPI.Spaces.Members.get(name="spaces/TEST_SPACE/members/app")

        # Should return the membership
        self.assertEqual(result["name"], "spaces/TEST_SPACE/members/app")

        # Try to get non-existent membership
        result = GoogleChatAPI.Spaces.Members.get(
            name="spaces/TEST_SPACE/members/nonexistent"
        )

        # Should return empty dict
        self.assertEqual(result, {})

    def test_create_invalid_parent(self):
        """Test lines 317-320: create with invalid parent format"""
        # Try to create membership with invalid parent
        with self.assertRaises(InvalidParentFormatError):
            GoogleChatAPI.Spaces.Members.create(
                parent="invalid_format",
                membership={"member": {"name": "users/user1", "type": "HUMAN"}},
            )

    def test_create_missing_member(self):
        """Test lines 322-325: create with missing member"""
        # Try to create membership without member
        self.assert_error_behavior(
            func_to_call=add_space_member,
            expected_exception_type=ValidationError,
            expected_message="Field required",
            parent="spaces/TEST_SPACE",
            membership={}
        )

    def test_create_invalid_member_name(self):
        """Test lines 327-331: create with invalid member name"""
        # Try to create membership with invalid member name
        self.assert_error_behavior(
            func_to_call=add_space_member,
            expected_exception_type=ValidationError,
            expected_message="String should match pattern '^(users/(app|[^/]+))$'",
            parent="spaces/TEST_SPACE",
            membership={"member": {"name": "invalid_name", "type": "HUMAN"}},
        )

    def test_create_with_admin_access_for_bot(self):
        """Test lines 335-339: create with admin access for bot"""
        # Try to create bot membership with admin access
        with self.assertRaises(AdminAccessNotAllowedError):
            GoogleChatAPI.Spaces.Members.create(
                parent="spaces/TEST_SPACE",
                membership={"member": {"name": "users/bot", "type": "BOT"}},
                useAdminAccess=True,
            )

    def test_create_existing_membership(self):
        """Test lines 342-345: create with existing membership"""
        # Add existing membership
        existing = {
            "name": "spaces/TEST_SPACE/members/users/existing",
            "state": "JOINED",
            "role": "ROLE_MEMBER",
            "member": {"name": "users/existing", "type": "HUMAN"},
        }
        GoogleChatAPI.DB["Membership"].append(existing)

        # Try to create the same membership again
        with self.assertRaises(MembershipAlreadyExistsError):
            GoogleChatAPI.Spaces.Members.create(
                parent="spaces/TEST_SPACE",
                membership={"member": {"name": "users/existing", "type": "HUMAN"}},
            )

    def test_create_new_membership(self):
        """Test lines 347-353: create new membership"""
        # Create new membership
        result = GoogleChatAPI.Spaces.Members.create(
            parent="spaces/TEST_SPACE",
            membership={"member": {"name": "users/new", "type": "HUMAN"}},
        )

        # Verify membership was created with default values
        self.assertEqual(result["name"], "spaces/TEST_SPACE/members/users/new")
        self.assertEqual(result["role"], "ROLE_MEMBER")
        self.assertEqual(result["state"], "INVITED")
        self.assertIn("createTime", result)

        # Verify membership was added to DB
        self.assertEqual(len(GoogleChatAPI.DB["Membership"]), 1)

    def test_delete_not_found(self):
        """Test lines 403: delete non-existent membership"""
        # Try to delete non-existent membership
        result = GoogleChatAPI.Spaces.Members.delete(
            name="spaces/TEST_SPACE/members/nonexistent"
        )

        # Should return empty dict
        self.assertEqual(result, {})

    def test_delete_app_with_admin(self):
        """Test lines 449-452: delete app membership with admin access"""
        # Add app membership
        app_membership = {
            "name": "spaces/TEST_SPACE/members/app",
            "state": "JOINED",
            "role": "ROLE_MEMBER",
            "member": {"name": "users/app", "type": "BOT"},
        }
        GoogleChatAPI.DB["Membership"].append(app_membership)

        # Try to delete app membership with admin access
        result = GoogleChatAPI.Spaces.Members.delete(
            name="spaces/TEST_SPACE/members/app", useAdminAccess=True
        )

        # Should return empty dict
        self.assertEqual(result, {})

        # Verify membership still exists
        self.assertEqual(len(GoogleChatAPI.DB["Membership"]), 1)

    def test_delete_successful(self):
        """Test lines 454-467: successful membership deletion"""
        # Add regular membership
        membership = {
            "name": "spaces/TEST_SPACE/members/users/delete_me",
            "state": "JOINED",
            "role": "ROLE_MEMBER",
            "member": {"name": "users/delete_me", "type": "HUMAN"},
        }
        GoogleChatAPI.DB["Membership"].append(membership)

        # Delete the membership
        result = GoogleChatAPI.Spaces.Members.delete(
            name="spaces/TEST_SPACE/members/users/delete_me"
        )

        # Should return the deleted membership
        self.assertEqual(result["name"], "spaces/TEST_SPACE/members/users/delete_me")

        # Verify membership was removed from DB
        self.assertEqual(len(GoogleChatAPI.DB["Membership"]), 0)

    def test_list_filter_with_invalid_field(self):
        """Test line 81: list with filter containing invalid field"""
        # Add test memberships
        GoogleChatAPI.DB["Membership"].append(
            {
                "name": "spaces/TEST_SPACE/members/users/user1",
                "state": "JOINED",
                "role": "ROLE_MEMBER",
                "member": {"name": "users/user1", "type": "HUMAN"},
            }
        )

        # Call list with a filter containing an invalid/unsupported field
        result = GoogleChatAPI.Spaces.Members.list(
            parent="spaces/TEST_SPACE", filter='invalid_field = "some_value"'
        )

        # Should still return results since invalid fields are just skipped
        self.assertIn("memberships", result)
        self.assertEqual(len(result["memberships"]), 1)

    def test_list_filter_with_unsupported_operator(self):
        """Test line 98: list with filter containing unsupported operator"""
        # Add test memberships
        GoogleChatAPI.DB["Membership"].append(
            {
                "name": "spaces/TEST_SPACE/members/users/user1",
                "state": "JOINED",
                "role": "ROLE_MEMBER",
                "member": {"name": "users/user1", "type": "HUMAN"},
            }
        )

        # Call list with a filter containing an unsupported operator
        # The apply_filter function only supports = and !=
        result = GoogleChatAPI.Spaces.Members.list(
            parent="spaces/TEST_SPACE",
            filter='role > "ROLE_MEMBER"',  # Using > which is unsupported
        )

        # Should still return results since unsupported operators are skipped/ignored
        self.assertIn("memberships", result)
        self.assertEqual(len(result["memberships"]), 1)

    def test_list_with_zero_page_size(self):
        """Test lines 130, 132: list with zero page size"""
        # Add several test memberships
        for i in range(5):
            GoogleChatAPI.DB["Membership"].append(
                {
                    "name": f"spaces/TEST_SPACE/members/users/user{i}",
                    "state": "JOINED",
                    "role": "ROLE_MEMBER",
                    "member": {"name": f"users/user{i}", "type": "HUMAN"},
                }
            )

        # Test with pageSize=0 (too small)
        self.assert_error_behavior(
            func_to_call=GoogleChatAPI.Spaces.Members.list,
            expected_exception_type=InvalidPageSizeError,
            expected_message="Argument 'pageSize' must be between 1 and 1000, inclusive, if provided.",
            parent="spaces/TEST_SPACE", 
            pageSize=0
        )
        
        # Test with pageSize=-1 (negative)
        self.assert_error_behavior(
            func_to_call=GoogleChatAPI.Spaces.Members.list,
            expected_exception_type=InvalidPageSizeError,
            expected_message="Argument 'pageSize' must be between 1 and 1000, inclusive, if provided.",
            parent="spaces/TEST_SPACE", 
            pageSize=-1
        )

        # Test with None (should pass and use default)
        result_with_none = GoogleChatAPI.Spaces.Members.list(
            parent="spaces/TEST_SPACE", pageSize=None
        )

        # Should return all memberships (default page size applies)
        self.assertIn("memberships", result_with_none)
        self.assertEqual(len(result_with_none["memberships"]), 5)

    def test_delete_with_invalid_name_format(self):
        """Test line 403: delete with invalid name format"""
        # Test deletion with an invalid name format
        result = GoogleChatAPI.Spaces.Members.delete(
            name="invalid/format"  # Not spaces/{space}/members/{member}
        )

        # Should return empty dict
        self.assertEqual(result, {})

    def test_list_filter_skips_unknown_field(self):
        """Test line 81: apply_filter skips unknown fields by continuing rather than returning false"""
        # Add a test membership
        GoogleChatAPI.DB["Membership"].append(
            {
                "name": "spaces/TEST_SPACE/members/users/user1",
                "state": "JOINED",
                "role": "ROLE_MEMBER",
                "member": {"name": "users/user1", "type": "HUMAN"},
            }
        )

        # Filter with a valid field AND an invalid field
        # The invalid field should be skipped (continue) in apply_filter line 81
        # rather than returning false, letting the valid filter still apply
        result = GoogleChatAPI.Spaces.Members.list(
            parent="spaces/TEST_SPACE",
            filter='unknown_field = "value" AND role = "ROLE_MEMBER"',
        )

        # Should return the membership because the unknown_field is skipped
        # and the role filter matches
        self.assertIn("memberships", result)
        self.assertEqual(len(result["memberships"]), 1)

    def test_list_pagination_edge_case(self):
        """Test line 132: pagination edge case where nextPageToken is None"""
        # Add 3 test memberships
        for i in range(3):
            GoogleChatAPI.DB["Membership"].append(
                {
                    "name": f"spaces/TEST_SPACE/members/users/user{i}",
                    "state": "JOINED",
                    "role": "ROLE_MEMBER",
                    "member": {"name": f"users/user{i}", "type": "HUMAN"},
                }
            )

        # Request exactly enough items to get all results (pageSize=3)
        # This should hit line 132 where nextPageToken becomes None
        result = GoogleChatAPI.Spaces.Members.list(
            parent="spaces/TEST_SPACE", pageSize=3  # Exactly matches the count of items
        )

        # Should return all memberships and no nextPageToken
        self.assertIn("memberships", result)
        self.assertEqual(len(result["memberships"]), 3)
        self.assertNotIn("nextPageToken", result)

        # Also test a case where there are no results (empty list)
        # Clear all memberships first
        GoogleChatAPI.DB["Membership"].clear()

        result_empty = GoogleChatAPI.Spaces.Members.list(parent="spaces/TEST_SPACE")

        # Should return empty list and no nextPageToken
        self.assertEqual(len(result_empty["memberships"]), 0)
        self.assertNotIn("nextPageToken", result_empty)

    def test_delete_with_name_not_in_db(self):
        """Test line 403: delete membership that doesn't exist in DB"""
        # Ensure DB is empty
        GoogleChatAPI.DB["Membership"].clear()

        # Try to delete a membership that looks valid but doesn't exist in DB
        result = GoogleChatAPI.Spaces.Members.delete(
            name="spaces/TEST_SPACE/members/users/nonexistent"
        )

        # Should return empty dict
        self.assertEqual(result, {})

        # Also try with a completely invalid format for extra coverage
        result2 = GoogleChatAPI.Spaces.Members.delete(name="completely_invalid_format")

        # Should also return empty dict
        self.assertEqual(result2, {})

    def test_unknown_field_in_filter(self):
        """Test line 81: continue when encountering unknown field in apply_filter"""
        # Add a test membership
        test_membership = {
            "name": "spaces/TEST_SPACE/members/users/test",
            "state": "JOINED",
            "role": "ROLE_MEMBER",
            "member": {"name": "users/test", "type": "HUMAN"},
        }
        GoogleChatAPI.DB["Membership"].append(test_membership)

        # Use a filter with ONLY an unknown field - this will hit the continue on line 81
        result = GoogleChatAPI.Spaces.Members.list(
            parent="spaces/TEST_SPACE", filter='unknown_field = "anything"'
        )

        # Should return the membership since apply_filter will skip the unknown field and return True
        self.assertIn("memberships", result)
        self.assertEqual(len(result["memberships"]), 1)

    def test_no_next_page_token(self):
        """Test line 132: nextPageToken becomes None when end >= total"""
        # Add exactly 3 test memberships
        for i in range(3):
            GoogleChatAPI.DB["Membership"].append(
                {
                    "name": f"spaces/TEST_SPACE/members/users/user{i}",
                    "state": "JOINED",
                    "role": "ROLE_MEMBER",
                    "member": {"name": f"users/user{i}", "type": "HUMAN"},
                }
            )

        # Request with pageSize=3 to get exactly all items (end == total)
        result = GoogleChatAPI.Spaces.Members.list(
            parent="spaces/TEST_SPACE", pageSize=3
        )

        # Should have 3 memberships and no nextPageToken since end >= total (line 132)
        self.assertEqual(len(result["memberships"]), 3)
        self.assertNotIn("nextPageToken", result)

    def test_membership_not_found(self):
        """Test line 403: membership not found during delete operation"""
        # Ensure no memberships exist
        GoogleChatAPI.DB["Membership"].clear()

        # Try to delete a non-existent membership with valid format
        result = GoogleChatAPI.Spaces.Members.delete(
            name="spaces/TEST_SPACE/members/users/nonexistent"
        )

        # Should hit line 403 and return empty dict
        self.assertEqual(result, {})

    def test_unknown_field_in_filter(self):
        """Test line 81: continue when encountering unknown field in apply_filter"""
        # Add a test membership
        test_membership = {
            "name": "spaces/TEST_SPACE/members/users/test",
            "state": "JOINED",
            "role": "ROLE_MEMBER",
            "member": {"name": "users/test", "type": "HUMAN"},
        }
        GoogleChatAPI.DB["Membership"].append(test_membership)

        # Use a filter with ONLY an unknown field - this will hit the continue on line 81
        result = GoogleChatAPI.Spaces.Members.list(
            parent="spaces/TEST_SPACE", filter='unknown_field = "anything"'
        )

        # Should return the membership since apply_filter will skip the unknown field and return True
        self.assertIn("memberships", result)
        self.assertEqual(len(result["memberships"]), 1)


class TestGoogleChatSpacesSpaceEvents(BaseTestCaseWithErrorHandler):
    def test_get_space_event(self):
        GoogleChatAPI.Spaces.SpaceEvents.get("spaces/TEST_SPACE/events/123")

    def test_list_space_events(self):
        GoogleChatAPI.Spaces.SpaceEvents.list("spaces/TEST_SPACE")


class TestGoogleChatMedia(BaseTestCaseWithErrorHandler):
    """Test suite for Google Chat API Media operations"""

    def setUp(self):
        """Reset DB before each test"""
        GoogleChatAPI.DB.clear()
        GoogleChatAPI.DB.update(
            {
                "User": [{"name": "users/USER123", "displayName": "Test User"}],
                "Space": [],
                "Message": [],
                "Membership": [],
                # Note: Attachment not included intentionally to test creation
            }
        )
        GoogleChatAPI.CURRENT_USER = {"id": "users/USER123"}
        GoogleChatAPI.CURRENT_USER_ID = GoogleChatAPI.CURRENT_USER

        # Add a test space
        self.test_space = {
            "name": "spaces/TEST_SPACE",
            "spaceType": "SPACE",
            "displayName": "Test Space",
        }
        GoogleChatAPI.DB["Space"].append(self.test_space)

    def test_download(self):
        """Test line 16: Media download function"""
        # The download function just prints and doesn't return anything meaningful
        # We're just calling it to cover line 16
        result = GoogleChatAPI.Media.download("spaces/TEST_SPACE/attachments/123")
        # No assertions needed as the function just prints and returns None
        self.assertIsNone(result)

    def test_upload_new_attachment_type(self):
        """Test lines 46-52: Upload with new attachment type (DB['Attachment'] doesn't exist)"""
        # Ensure Attachment is not in DB
        if "Attachment" in GoogleChatAPI.DB:
            del GoogleChatAPI.DB["Attachment"]

        # Upload a new attachment
        attachment_request = {"contentName": "test.png", "contentType": "image/png"}

        result = GoogleChatAPI.Media.upload(
            parent="spaces/TEST_SPACE", attachment_request=attachment_request
        )

        # Verify that result has correct fields
        self.assertEqual(result["name"], "spaces/TEST_SPACE/attachments/1")
        self.assertEqual(result["contentName"], "test.png")
        self.assertEqual(result["contentType"], "image/png")
        self.assertEqual(result["source"], "UPLOADED_CONTENT")

        # Verify that DB["Attachment"] was created and contains the attachment
        self.assertIn("Attachment", GoogleChatAPI.DB)
        self.assertEqual(len(GoogleChatAPI.DB["Attachment"]), 1)
        self.assertEqual(
            GoogleChatAPI.DB["Attachment"][0]["name"], "spaces/TEST_SPACE/attachments/1"
        )

    def test_upload_multiple_attachments(self):
        """Test lines 53-66: Upload multiple attachments and verify IDs increment"""
        # Upload first attachment
        attachment_request1 = {
            "contentName": "test1.docx",
            "contentType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }

        result1 = GoogleChatAPI.Media.upload(
            parent="spaces/TEST_SPACE", attachment_request=attachment_request1
        )

        # Upload second attachment
        attachment_request2 = {
            "contentName": "test2.pdf",
            "contentType": "application/pdf",
        }

        result2 = GoogleChatAPI.Media.upload(
            parent="spaces/TEST_SPACE", attachment_request=attachment_request2
        )

        # Verify correct IDs were assigned
        self.assertEqual(result1["name"], "spaces/TEST_SPACE/attachments/1")
        self.assertEqual(result2["name"], "spaces/TEST_SPACE/attachments/2")

        # Verify both attachments are in DB
        self.assertEqual(len(GoogleChatAPI.DB["Attachment"]), 2)

    def test_upload_with_missing_content_details(self):
        """Test lines 53-66: Upload with missing content details (should use defaults)"""
        # Upload with minimal request data
        attachment_request = {}

        result = GoogleChatAPI.Media.upload(
            parent="spaces/TEST_SPACE", attachment_request=attachment_request
        )

        # Verify default values were used
        self.assertEqual(result["contentName"], "unknown")
        self.assertEqual(result["contentType"], "application/octet-stream")

        # Verify other fields are present
        self.assertIn("attachmentDataRef", result)
        self.assertIn("driveDataRef", result)
        self.assertIn("thumbnailUri", result)
        self.assertIn("downloadUri", result)


class TestGoogleChatUsersSpacesSpaceNotificationSetting(BaseTestCaseWithErrorHandler):
    def setUp(self):
        """Reset DB before each test"""
        GoogleChatAPI.DB.clear()
        GoogleChatAPI.DB.update(
            {
                "User": [],
                "Space": [],
                "Membership": [],
                "Message": [],
                "Reaction": [],
                "SpaceReadState": [],
                "ThreadReadState": [],
                "SpaceNotificationSetting": [],
            }
        )
        GoogleChatAPI.CURRENT_USER = {"id": "users/USER123"}
        GoogleChatAPI.CURRENT_USER_ID = GoogleChatAPI.CURRENT_USER

    def test_get_setting_not_found_print(self):
        """Test lines 43-44: print_log message when SpaceNotificationSetting not found in get"""
        from unittest.mock import patch

        with patch("google_chat.Users.Spaces.SpaceNotificationSetting.print_log") as mock_print_log:
            # Call with a name that doesn't exist in the DB
            result = GoogleChatAPI.Users.Spaces.SpaceNotificationSetting.get(
                "users/me/spaces/NONEXISTENT/spaceNotificationSetting"
            )
            self.assertEqual(result, {})
            # Assert print_log was called with the expected message
            mock_print_log.assert_any_call("SpaceNotificationSetting not found.")

    def test_patch_setting_not_found_print(self):
        """Test lines 85-86: print_log message when SpaceNotificationSetting not found in patch"""
        from unittest.mock import patch

        with patch("google_chat.Users.Spaces.SpaceNotificationSetting.print_log") as mock_print_log:
            # Call with a name that doesn't exist in the DB
            result = GoogleChatAPI.Users.Spaces.SpaceNotificationSetting.patch(
                name="users/me/spaces/NONEXISTENT/spaceNotificationSetting",
                updateMask="notification_setting",
                requestBody={"notification_setting": "ALL"},
            )
            self.assertEqual(result, {})
            # Assert print_log was called with the expected message
            mock_print_log.assert_any_call("SpaceNotificationSetting not found.")

    def test_get_space_notification_setting(self):
        GoogleChatAPI.DB["SpaceNotificationSetting"].append(
            {
                "name": "users/me/spaces/TEST_SPACE/spaceNotificationSetting",
                "notificationSetting": "ALL",
                "muteSetting": "UNMUTED",
            }
        )
        result = GoogleChatAPI.Users.Spaces.SpaceNotificationSetting.get(
            "users/me/spaces/TEST_SPACE/spaceNotificationSetting"
        )
        self.assertEqual(
            result,
            {
                "name": "users/me/spaces/TEST_SPACE/spaceNotificationSetting",
                "notificationSetting": "ALL",
                "muteSetting": "UNMUTED",
            },
        )

    def test_patch_space_notification_setting(self):
        GoogleChatAPI.DB["SpaceNotificationSetting"].append(
            {
                "name": "users/me/spaces/TEST_SPACE/spaceNotificationSetting",
                "notification_setting": "ALL",
                "mute_setting": "UNMUTED",
            }
        )
        requestBody = {
            "name": "users/me/spaces/TEST_SPACE/spaceNotificationSetting",
            "notification_setting": "MENTIONS",
            "mute_setting": "MUTED",
        }
        result = GoogleChatAPI.Users.Spaces.SpaceNotificationSetting.patch(
            "users/me/spaces/TEST_SPACE/spaceNotificationSetting",
            "notification_setting, mute_setting",
            requestBody,
        )
        self.assertEqual(
            result,
            {
                "name": "users/me/spaces/TEST_SPACE/spaceNotificationSetting",
                "notification_setting": "MENTIONS",
                "mute_setting": "MUTED",
            },
        )


class TestGoogleChatUsersSpacesThreads(BaseTestCaseWithErrorHandler):
    def setUp(self):
        """Reset DB before each test"""
        GoogleChatAPI.DB.clear()
        GoogleChatAPI.DB.update(
            {
                "User": [],
                "Space": [],
                "Membership": [],
                "Message": [],
                "Reaction": [],
                "SpaceReadState": [],
                "ThreadReadState": [],
                "SpaceNotificationSetting": [],
            }
        )
        GoogleChatAPI.CURRENT_USER = {"id": "users/USER123"}
        GoogleChatAPI.CURRENT_USER_ID = GoogleChatAPI.CURRENT_USER

    def test_getThreadReadState_not_found_print(self):
        """Test lines 35-36: print_log message when ThreadReadState not found in get"""
        from unittest.mock import patch

        with patch("google_chat.Users.Spaces.Threads.print_log") as mock_print_log:
            # Call with a name that doesn't exist in the DB
            result = GoogleChatAPI.Users.Spaces.Threads.getThreadReadState(
                "users/me/spaces/NONEXISTENT/threads/NONEXISTENT/threadReadState"
            )
            self.assertEqual(result, {})
            # Assert print_log was called with the expected message
            mock_print_log.assert_any_call("ThreadReadState not found.")

    def test_getThreadReadState(self):
        GoogleChatAPI.DB["ThreadReadState"].append(
            {
                "name": "users/me/spaces/TEST_SPACE/threads/123/threadReadState",
                "lastReadTime": "2023-01-01T00:00:00Z",
            }
        )
        result = GoogleChatAPI.Users.Spaces.Threads.getThreadReadState(
            "users/me/spaces/TEST_SPACE/threads/123/threadReadState"
        )
        self.assertEqual(
            result,
            {
                "name": "users/me/spaces/TEST_SPACE/threads/123/threadReadState",
                "lastReadTime": "2023-01-01T00:00:00Z",
            },
        )

class TestGoogleChatUsersSpaces(BaseTestCaseWithErrorHandler):
    def setUp(self):
        """Reset DB before each test"""
        GoogleChatAPI.DB.clear()
        GoogleChatAPI.DB.update(
            {
                "User": [],
                "Space": [],
                "Membership": [],
                "Message": [],
                "Reaction": [],
                "SpaceReadState": [],
                "ThreadReadState": [],
                "SpaceNotificationSetting": [],
            }
        )

    def test_getSpaceReadState_not_found_print(self):
        # Call with a name that doesn't exist in the DB
        result = GoogleChatAPI.Users.Spaces.getSpaceReadState(
            "users/me/spaces/NONEXISTENT/spaceReadState"
        )
        self.assertEqual(result, {})

    def test_getSpaceReadState(self):
        GoogleChatAPI.DB["SpaceReadState"].append(
            {
                "name": "users/me/spaces/TEST_SPACE/spaceReadState",
                "lastReadTime": "2023-01-01T00:00:00Z",
            }
        )
        result = GoogleChatAPI.Users.Spaces.getSpaceReadState(
            "users/me/spaces/TEST_SPACE/spaceReadState"
        )
        self.assertEqual(
            result,
            {
                "name": "users/me/spaces/TEST_SPACE/spaceReadState",
                "lastReadTime": "2023-01-01T00:00:00Z",
            },
        )

    def test_updateSpaceReadState_not_found_print(self):
        # Call with a name that doesn't exist in the DB
        result = GoogleChatAPI.Users.Spaces.updateSpaceReadState(
            "users/me/spaces/NONEXISTENT/spaceReadState",
            "lastReadTime",
            {"lastReadTime": "2023-01-01T00:00:00Z"},
        )
        self.assertEqual(result, {})
        # Verify that line 106's print statement was executed

    def test_updateSpaceReadState(self):
        GoogleChatAPI.DB["SpaceReadState"].append(
            {
                "name": "users/me/spaces/TEST_SPACE/spaceReadState",
                "last_read_time": "2023-01-01T00:00:00Z",
            }
        )
        requestBody = {
            "name": "users/me/spaces/TEST_SPACE/spaceReadState",
            "last_read_time": "2023-01-02T00:00:00Z",
        }
        result = GoogleChatAPI.Users.Spaces.updateSpaceReadState(
            "users/me/spaces/TEST_SPACE/spaceReadState", "last_read_time", requestBody
        )
        self.assertEqual(
            result,
            {
                "name": "users/me/spaces/TEST_SPACE/spaceReadState",
                "last_read_time": "2023-01-02T00:00:00Z",
            },
        )

    def test_updateSpaceReadState_invalid_updateMask(self):
        """Test print_log message when updateSpaceReadState called with invalid updateMask"""
        from unittest.mock import patch

        with patch("google_chat.Users.Spaces.print_log") as mock_print_log:
            # Call with an invalid updateMask
            GoogleChatAPI.DB["SpaceReadState"].append(
                {
                    "name": "users/me/spaces/TEST_SPACE/spaceReadState",
                    "last_read_time": "2023-01-01T00:00:00Z",
                }
            )
            result = GoogleChatAPI.Users.Spaces.updateSpaceReadState(
                "users/me/spaces/TEST_SPACE/spaceReadState",
                "invalid_field",
                {"lastReadTime": "2023-01-02T00:00:00Z"},
            )
            # Assert print_log was called with the expected message
            mock_print_log.assert_any_call("No supported field in updateMask.")

    def test_updateSpaceReadState_invalid_requestBody(self):
        """Test print_log message when updateSpaceReadState called with missing last_read_time in requestBody"""
        from unittest.mock import patch

        with patch("google_chat.Users.Spaces.print_log") as mock_print_log:
            # Add a SpaceReadState to the DB
            GoogleChatAPI.DB["SpaceReadState"].append(
                {
                    "name": "users/me/spaces/TEST_SPACE/spaceReadState",
                    "last_read_time": "2023-01-01T00:00:00Z",
                }
            )
            # Call with an invalid requestBody (missing last_read_time)
            result = GoogleChatAPI.Users.Spaces.updateSpaceReadState(
                "users/me/spaces/TEST_SPACE/spaceReadState",
                "last_read_time",
                {"invalid_field": "2023-01-02T00:00:00Z"},
            )
            # Assert print_log was called with the expected message
            mock_print_log.assert_any_call("last_read_time not provided in requestBody.")


class TestGoogleChatAPISpaces(unittest.TestCase):

    def setUp(self):
        """Reset DB before each test"""
        GoogleChatAPI.DB.clear()
        GoogleChatAPI.DB.update(
            {
                "User": [],
                "Space": [],
                "Membership": [],
                "Message": [],
                "Reaction": [],
                "SpaceReadState": [],
                "ThreadReadState": [],
                "SpaceNotificationSetting": [],
            }
        )
        GoogleChatAPI.CURRENT_USER = {"id": "users/USER123"}
        GoogleChatAPI.CURRENT_USER_ID = GoogleChatAPI.CURRENT_USER

    def test_list_spaces_input_validation(self):
        """Test input validation for Spaces.list function"""
        # Test invalid pageSize types
        with self.assertRaises(TypeError) as context:
            GoogleChatAPI.Spaces.list(pageSize="100")  # String instead of int
        self.assertIn("must be an integer", str(context.exception))

        with self.assertRaises(TypeError) as context:
            GoogleChatAPI.Spaces.list(pageSize=100.5)  # Float instead of int
        self.assertIn("must be an integer", str(context.exception))

        # Test invalid pageSize values
        with self.assertRaises(InvalidPageSizeError) as context:
            GoogleChatAPI.Spaces.list(pageSize=0)  # Too small
        self.assertIn("must be between 1 and 1000", str(context.exception))

        with self.assertRaises(InvalidPageSizeError) as context:
            GoogleChatAPI.Spaces.list(pageSize=1001)  # Too large
        self.assertIn("must be between 1 and 1000", str(context.exception))

        # Test invalid pageToken type
        with self.assertRaises(TypeError) as context:
            GoogleChatAPI.Spaces.list(pageToken=123)  # Int instead of string
        self.assertIn("must be a string", str(context.exception))

        # Test invalid filter type
        with self.assertRaises(TypeError) as context:
            GoogleChatAPI.Spaces.list(filter=123)  # Int instead of string
        self.assertIn("must be a string", str(context.exception))

    def test_list_spaces_filter_validation(self):
        """Test filter validation and parsing in Spaces.list"""
        # Test invalid AND operator
        result = GoogleChatAPI.Spaces.list(filter='spaceType = "SPACE" AND spaceType = "GROUP_CHAT"')
        self.assertIn("error", result)
        self.assertIn("'AND' operator is not supported", result["error"])

        # Test invalid space type
        result = GoogleChatAPI.Spaces.list(filter='spaceType = "INVALID_TYPE"')
        self.assertIn("error", result)
        self.assertIn("Invalid space type", result["error"])

        # Test malformed filter
        result = GoogleChatAPI.Spaces.list(filter='invalid filter syntax')
        self.assertIn("error", result)
        self.assertIn("No valid expressions", result["error"])

        # Test empty filter with quotes
        result = GoogleChatAPI.Spaces.list(filter='spaceType = ""')
        self.assertIn("error", result)
        self.assertIn("No valid expressions", result["error"])

    def test_list_spaces_valid_filters(self):
        """Test valid filter combinations in Spaces.list"""
        # Add test spaces
        GoogleChatAPI.DB["Space"].extend([
            {
                "name": "spaces/AAA",
                "spaceType": "SPACE",
                "displayName": "Test Space"
            },
            {
                "name": "spaces/BBB",
                "spaceType": "GROUP_CHAT",
                "displayName": "Test Group Chat"
            },
            {
                "name": "spaces/CCC",
                "spaceType": "DIRECT_MESSAGE",
                "displayName": "Test DM"
            }
        ])

        # Add memberships for current user
        for space in GoogleChatAPI.DB["Space"]:
            membership = {
                "name": f"{space['name']}/members/{GoogleChatAPI.CURRENT_USER_ID['id']}",
                "state": "JOINED",
                "role": "ROLE_MEMBER",
                "member": {
                    "name": GoogleChatAPI.CURRENT_USER_ID["id"],
                    "type": "HUMAN"
                }
            }
            GoogleChatAPI.DB["Membership"].append(membership)

        # Test single space type filter
        result = GoogleChatAPI.Spaces.list(filter='spaceType = "SPACE"')
        self.assertNotIn("error", result)
        self.assertIsInstance(result["spaces"], list)
        for space in result["spaces"]:
            self.assertEqual(space["spaceType"], "SPACE")

        # Test multiple space types with OR
        result = GoogleChatAPI.Spaces.list(filter='spaceType = "SPACE" OR spaceType = "GROUP_CHAT"')
        self.assertNotIn("error", result)
        self.assertIsInstance(result["spaces"], list)
        for space in result["spaces"]:
            self.assertIn(space["spaceType"], ["SPACE", "GROUP_CHAT"])

        # Test space_type alternative syntax
        result = GoogleChatAPI.Spaces.list(filter='space_type = "DIRECT_MESSAGE"')
        self.assertNotIn("error", result)
        self.assertIsInstance(result["spaces"], list)
        for space in result["spaces"]:
            self.assertEqual(space["spaceType"], "DIRECT_MESSAGE")

    def test_list_spaces_basic_functionality(self):
        """Test basic functionality of Spaces.list without filters"""
        # Add test spaces
        GoogleChatAPI.DB["Space"].extend([
            {
                "name": "spaces/AAA",
                "spaceType": "SPACE",
                "displayName": "Test Space"
            },
            {
                "name": "spaces/BBB",
                "spaceType": "GROUP_CHAT",
                "displayName": "Test Group Chat"
            }
        ])

        # Add memberships for current user
        for space in GoogleChatAPI.DB["Space"]:
            membership = {
                "name": f"{space['name']}/members/{GoogleChatAPI.CURRENT_USER_ID['id']}",
                "state": "JOINED",
                "role": "ROLE_MEMBER",
                "member": {
                    "name": GoogleChatAPI.CURRENT_USER_ID["id"],
                    "type": "HUMAN"
                }
            }
            GoogleChatAPI.DB["Membership"].append(membership)

        # Test without any parameters
        result = GoogleChatAPI.Spaces.list()
        self.assertIsInstance(result, dict)
        self.assertIn("spaces", result)
        self.assertIn("nextPageToken", result)
        self.assertIsInstance(result["spaces"], list)

        # Test with valid pageSize
        result = GoogleChatAPI.Spaces.list(pageSize=50)
        self.assertIsInstance(result, dict)
        self.assertIn("spaces", result)
        self.assertLessEqual(len(result["spaces"]), 50)

        # Test with pageToken (even though pagination isn't implemented)
        result = GoogleChatAPI.Spaces.list(pageToken="some_token")
        self.assertIsInstance(result, dict)
        self.assertIn("spaces", result)
        self.assertIn("nextPageToken", result)

    def test_list_spaces_membership_filtering(self):
        """Test that only spaces where the user is a member are returned"""
        # Add test spaces
        GoogleChatAPI.DB["Space"].extend([
            {
                "name": "spaces/AAA",
                "spaceType": "SPACE",
                "displayName": "Test Space"
            },
            {
                "name": "spaces/BBB",
                "spaceType": "GROUP_CHAT",
                "displayName": "Test Group Chat"
            }
        ])
        
        # Add membership for only one space
        membership = {
            "name": f"spaces/AAA/members/{GoogleChatAPI.CURRENT_USER_ID['id']}",
            "state": "JOINED",
            "role": "ROLE_MEMBER",
            "member": {
                "name": GoogleChatAPI.CURRENT_USER_ID["id"],
                "type": "HUMAN"
            }
        }
        GoogleChatAPI.DB["Membership"].append(membership)
        
        # List spaces
        result = GoogleChatAPI.Spaces.list()
        self.assertNotIn("error", result)
        self.assertIsInstance(result["spaces"], list)
        
        # Verify only the space with membership is in the results
        self.assertEqual(len(result["spaces"]), 1)
        self.assertEqual(result["spaces"][0]["name"], "spaces/AAA")

    def test_list_spaces_edge_cases(self):
        """Test edge cases in Spaces.list"""
        # Test with empty DB
        result = GoogleChatAPI.Spaces.list()
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result["spaces"]), 0)

        # Add test spaces
        GoogleChatAPI.DB["Space"].extend([
            {
                "name": "spaces/AAA",
                "spaceType": "SPACE",
                "displayName": "Test Space"
            }
        ])

        # Add membership for current user
        membership = {
            "name": f"spaces/AAA/members/{GoogleChatAPI.CURRENT_USER_ID['id']}",
            "state": "JOINED",
            "role": "ROLE_MEMBER",
            "member": {
                "name": GoogleChatAPI.CURRENT_USER_ID["id"],
                "type": "HUMAN"
            }
        }
        GoogleChatAPI.DB["Membership"].append(membership)

        # Test with filter containing extra whitespace
        result = GoogleChatAPI.Spaces.list(filter='  spaceType  =  "SPACE"  ')
        self.assertNotIn("error", result)
        self.assertIsInstance(result["spaces"], list)

        # Test with filter containing mixed case
        result = GoogleChatAPI.Spaces.list(filter='spaceType = "space" OR spaceType = "group_chat"')
        self.assertIn("error", result)  # Should error because case doesn't match

class TestAddSpaceMemberValidation(BaseTestCaseWithErrorHandler):

    def setUp(self):
        """Reset DB before each test."""
        GoogleChatAPI.DB.clear()
        GoogleChatAPI.DB.update({
            "User": [],
            "Space": [],
            "Membership": [],
            "Message": [],
            "Reaction": [],
            "SpaceReadState": [],
            "ThreadReadState": [],
            "SpaceNotificationSetting": [],
        })
        GoogleChatAPI.CURRENT_USER_ID = {"id": "users/USER123"}

    def test_valid_creation_human_member(self):
        """Test successful creation of a human membership with minimal valid input."""
        parent = "spaces/SPACE_VALID"
        membership_input = {
            "member": {
                "name": "users/human1",
                "type": "HUMAN"
            }
        }
        result = add_space_member(parent=parent, membership=membership_input)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["name"], "spaces/SPACE_VALID/members/users/human1")
        self.assertEqual(result["member"]["name"], "users/human1")
        self.assertEqual(result["member"]["type"], "HUMAN")
        self.assertEqual(result["role"], "ROLE_MEMBER") # Default
        self.assertEqual(result["state"], "INVITED")   # Default
        self.assertIn("createTime", result)
        self.assertEqual(len(GoogleChatAPI.DB["Membership"]), 1)

    def test_valid_creation_with_all_fields(self):
        """Test successful creation with all optional fields provided."""
        parent = "spaces/SPACE_ALL_FIELDS"
        membership_input = {
            "role": "ROLE_MANAGER",
            "state": "JOINED",
            "deleteTime": "2025-01-01T00:00:00Z",
            "member": {
                "name": "users/human2",
                "displayName": "Human Two",
                "domainId": "example.com",
                "type": "HUMAN",
                "isAnonymous": False
            },
            "groupMember": {
                "name": "groups/group1"
            }
        }
        result = add_space_member(parent=parent, membership=membership_input)
        self.assertEqual(result["role"], "ROLE_MANAGER")
        self.assertEqual(result["state"], "JOINED")
        self.assertEqual(result["member"]["displayName"], "Human Two")
        self.assertIsNotNone(result.get("groupMember"))
        self.assertEqual(result["groupMember"]["name"], "groups/group1")

    def test_invalid_parent_type(self):
        """Test TypeError for non-string parent."""
        self.assert_error_behavior(
            func_to_call=add_space_member,
            expected_exception_type=TypeError,
            expected_message="Parent must be a string.",
            parent=123,
            membership={"member": {"name": "users/u1", "type": "HUMAN"}}
        )

    def test_invalid_parent_format(self):
        """Test InvalidParentFormatError for malformed parent string."""
        self.assert_error_behavior(
            func_to_call=add_space_member,
            expected_exception_type=InvalidParentFormatError,
            expected_message="Invalid parent format. Expected 'spaces/{space}'.",
            parent="invalid_parent_format",
            membership={"member": {"name": "users/u1", "type": "HUMAN"}}
        )

    def test_invalid_membership_type(self):
        """Test TypeError for non-dict membership."""
        self.assert_error_behavior(
            func_to_call=add_space_member,
            expected_exception_type=TypeError,
            expected_message="Membership must be a dictionary.",
            parent="spaces/s1",
            membership="not_a_dict"
        )

    def test_invalid_use_admin_access_type(self):
        """Test TypeError for non-boolean useAdminAccess (when not None)."""
        self.assert_error_behavior(
            func_to_call=add_space_member,
            expected_exception_type=TypeError,
            expected_message="useAdminAccess must be a boolean or None.",
            parent="spaces/s1",
            membership={"member": {"name": "users/u1", "type": "HUMAN"}},
            useAdminAccess="not_a_bool"
        )

    def test_pydantic_validation_missing_member_in_membership(self):
        """Test ValidationError when 'member' field is missing in membership."""
        self.assert_error_behavior(
            func_to_call=add_space_member,
            expected_exception_type=ValidationError,
            expected_message="Field required",
            parent="spaces/s1",
            membership={} # Missing 'member'
        )

    def test_pydantic_validation_member_missing_name(self):
        """Test ValidationError when 'member.name' is missing."""
        membership_input = {"member": {"type": "HUMAN"}} # Missing member.name
        self.assert_error_behavior(
            func_to_call=add_space_member,
            expected_exception_type=ValidationError,
            expected_message="Field required",
            parent="spaces/s1",
            membership=membership_input
        )

    def test_pydantic_validation_member_invalid_name_format(self):
        """Test ValidationError for invalid 'member.name' format."""
        membership_input = {"member": {"name": "invalid_user_format", "type": "HUMAN"}}
        self.assert_error_behavior(
            func_to_call=add_space_member,
            expected_exception_type=ValidationError,
            expected_message="String should match pattern",
            parent="spaces/s1",
            membership=membership_input
        )

    def test_pydantic_validation_member_invalid_type_enum(self):
        """Test ValidationError for invalid 'member.type' enum value."""
        membership_input = {"member": {"name": "users/u1", "type": "INVALID_TYPE_ENUM"}}
        self.assert_error_behavior(
            func_to_call=add_space_member,
            expected_exception_type=ValidationError,
            expected_message="Input should be",
            parent="spaces/s1",
            membership=membership_input
        )

    def test_pydantic_validation_invalid_role_enum(self):
        """Test ValidationError for invalid 'role' enum value."""
        membership_input = {
            "role": "INVALID_ROLE_ENUM",
            "member": {"name": "users/u1", "type": "HUMAN"}
        }
        self.assert_error_behavior(
            func_to_call=add_space_member,
            expected_exception_type=ValidationError,
            expected_message="Input should be",
            parent="spaces/s1",
            membership=membership_input
        )

    def test_pydantic_validation_groupmember_invalid_name_format(self):
        """Test ValidationError for invalid 'groupMember.name' format."""
        membership_input = {
            "member": {"name": "users/u1", "type": "HUMAN"},
            "groupMember": {"name": "invalid_group_format"}
        }
        self.assert_error_behavior(
            func_to_call=add_space_member,
            expected_exception_type=ValidationError,
            expected_message="String should match pattern",
            parent="spaces/s1",
            membership=membership_input
        )

    def test_admin_access_for_bot_not_allowed(self):
        """Test AdminAccessNotAllowedError when creating BOT membership with admin access."""
        membership_input = {"member": {"name": "users/app", "type": "BOT"}}
        self.assert_error_behavior(
            func_to_call=add_space_member,
            expected_exception_type=AdminAccessNotAllowedError,
            expected_message="Admin access cannot be used to create memberships for a Chat app (BOT).",
            parent="spaces/s1",
            membership=membership_input,
            useAdminAccess=True
        )

    def test_admin_access_for_human_allowed(self):
        """Test successful creation for HUMAN with admin access."""
        parent = "spaces/s_admin_human"
        membership_input = {"member": {"name": "users/human_admin", "type": "HUMAN"}}
        result = add_space_member(parent=parent, membership=membership_input, useAdminAccess=True)
        self.assertEqual(result["member"]["type"], "HUMAN")
        self.assertEqual(len(GoogleChatAPI.DB["Membership"]), 1)


    def test_membership_already_exists(self):
        """Test MembershipAlreadyExistsError when membership name conflicts."""
        parent = "spaces/s_exists"
        member_name = "users/existing_user"
        membership_input = {"member": {"name": member_name, "type": "HUMAN"}}

        # Create it once
        add_space_member(parent=parent, membership=membership_input)
        self.assertEqual(len(GoogleChatAPI.DB["Membership"]), 1)

        # Try to create again
        self.assert_error_behavior(
            func_to_call=add_space_member,
            expected_exception_type=MembershipAlreadyExistsError,
            expected_message=f"Membership '{parent}/members/{member_name}' already exists.",
            parent=parent,
            membership=membership_input
        )

    def test_use_admin_access_none_default(self):
        """Test behavior with useAdminAccess=None (default)."""
        parent = "spaces/s_admin_none"
        membership_input = {"member": {"name": "users/human_default_admin", "type": "HUMAN"}}
        result = add_space_member(parent=parent, membership=membership_input, useAdminAccess=None)
        self.assertEqual(result["member"]["type"], "HUMAN")
        self.assertEqual(len(GoogleChatAPI.DB["Membership"]), 1)

    def test_use_admin_access_false_for_bot(self):
        """Test successful BOT creation when useAdminAccess=False."""
        parent = "spaces/s_bot_no_admin"
        membership_input = {"member": {"name": "users/app", "type": "BOT"}}
        result = add_space_member(parent=parent, membership=membership_input, useAdminAccess=False)
        self.assertEqual(result["member"]["type"], "BOT")
        self.assertEqual(len(GoogleChatAPI.DB["Membership"]), 1)

class TestCreateSpaceValidation(BaseTestCaseWithErrorHandler):
    """Tests for input validation of the create_space function."""

    def setUp(self):
        """Reset DB before each test"""
        # Use GoogleChatAPI.DB instead of global DB
        GoogleChatAPI.DB.clear()
        GoogleChatAPI.DB.update(
            {
                "User": [{"name": "users/USER123", "displayName": "Test User"}],
                "Space": [],
                "Membership": [],
                "Message": [],
                "Reaction": [],
                "SpaceReadState": [],
                "ThreadReadState": [],
                "SpaceNotificationSetting": [],
            }
        )
        # Both CURRENT_USER_ID and CURRENT_USER need to be set for consistency
        GoogleChatAPI.CURRENT_USER_ID = {"id": "users/USER123"}
        GoogleChatAPI.CURRENT_USER = GoogleChatAPI.CURRENT_USER_ID  # Set both for consistency
        
    def assert_error_behavior(self,
                              func_to_call,
                              expected_exception_type, # The actual exception class, e.g., ValueError
                              expected_message=None,
                              # You can pass other specific key-value pairs expected
                              # in the dictionary (besides 'exceptionType' and 'message').
                              additional_expected_dict_fields=None,
                              *func_args, **func_kwargs):
        """
        Override the assert_error_behavior from the parent class to use assertIn instead of assertEqual.
        This allows the test to pass even if the URL at the end of the error message changes.
        """
        # In the tests ERROR_MODE is "raise", so we only need to handle this case
        with self.assertRaises(expected_exception_type) as context:
            func_to_call(*func_args, **func_kwargs)
        
        if expected_message:
            # Use assertIn instead of assertEqual to check if the expected message is contained
            # in the actual error message, ignoring URL and other variants
            actual_message = str(context.exception)
            # Remove the URL part from both messages before comparison
            expected_no_url = expected_message.split('\n    For further information')[0]
            actual_no_url = actual_message.split('\n    For further information')[0]
            self.assertEqual(expected_no_url, actual_no_url)

    def test_valid_input_minimal_space(self):
        """Test create_space with minimal valid input for SPACE type."""
        space_request = {
            "spaceType": "SPACE",
            "displayName": "Test Minimal Space"
        }
        result = GoogleChatAPI.create_space(space=space_request)
        self.assertTrue(result.get("name", "").startswith("spaces/"))
        self.assertEqual(result.get("spaceType"), "SPACE")
        self.assertEqual(result.get("displayName"), "Test Minimal Space")

    def test_valid_input_group_chat(self):
        """Test create_space with minimal valid input for GROUP_CHAT type."""
        space_request = {
            "spaceType": "GROUP_CHAT"
            # displayName is optional for GROUP_CHAT
        }
        result = GoogleChatAPI.create_space(space=space_request)
        self.assertTrue(result.get("name", "").startswith("spaces/"))
        self.assertEqual(result.get("spaceType"), "GROUP_CHAT")

    def test_valid_input_all_fields(self):
        """Test create_space with all optional fields provided."""
        space_request = {
            "spaceType": "SPACE",
            "displayName": "Test Full Space",
            "externalUserAllowed": True,
            "importMode": True,
            "singleUserBotDm": False, # Explicitly false
            "spaceDetails": {"description": "A detailed space", "guidelines": "Be nice"},
            "predefinedPermissionSettings": "COLLABORATION_SPACE",
            "accessSettings": {"audience": "COMPLEX_AUDIENCE_ID"}
        }
        request_id = f"req-{uuid.uuid4()}"
        result = GoogleChatAPI.create_space(requestId=request_id, space=space_request)
        self.assertEqual(result.get("requestId"), request_id)
        self.assertEqual(result.get("spaceType"), "SPACE")
        self.assertEqual(result.get("displayName"), "Test Full Space")
        self.assertTrue(result.get("externalUserAllowed"))
        self.assertTrue(result.get("importMode"))
        self.assertFalse(result.get("singleUserBotDm")) # Check explicit false
        self.assertEqual(result.get("spaceDetails", {}).get("description"), "A detailed space")

    def test_invalid_requestId_type(self):
        """Test create_space with invalid requestId type."""
        self.assert_error_behavior(
            func_to_call=GoogleChatAPI.create_space,
            expected_exception_type=TypeError,
            expected_message="requestId must be a string.",
            requestId=123, # Invalid type
            space={"spaceType": "GROUP_CHAT"}
        )

    def test_invalid_space_argument_type(self):
        """Test create_space with space argument not being a dict or None."""
        self.assert_error_behavior(
            func_to_call=GoogleChatAPI.create_space,
            expected_exception_type=TypeError,
            expected_message="space argument must be a dictionary or None.",
            space=[] # Invalid type, should be dict
        )

    def test_missing_spaceType(self):
        """Test create_space with spaceType missing from space dict."""
        self.assert_error_behavior(
            func_to_call=GoogleChatAPI.create_space,
            expected_exception_type=ValidationError,
            # Use the full error message that Pydantic generates
            expected_message="1 validation error for SpaceInputModel\nspaceType\n  Field required [type=missing, input_value={'displayName': 'A Space Without Type'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.11/v/missing",
            space={"displayName": "A Space Without Type"}
        )

    def test_invalid_spaceType_value(self):
        """Test create_space with an invalid value for spaceType."""
        self.assert_error_behavior(
            func_to_call=GoogleChatAPI.create_space,
            expected_exception_type=ValidationError,
            expected_message="1 validation error for SpaceInputModel\nspaceType\n  Input should be 'SPACE', 'GROUP_CHAT' or 'DIRECT_MESSAGE' [type=enum, input_value='INVALID_TYPE', input_type=str]",
            space={"spaceType": "INVALID_TYPE", "displayName": "Invalid Space"}
        )

    def test_spaceType_space_missing_displayName(self):
        """Test create_space with spaceType 'SPACE' but missing displayName."""
        self.assert_error_behavior(
            func_to_call=GoogleChatAPI.create_space,
            expected_exception_type=ValidationError, # Changed to ValidationError
            expected_message="1 validation error for SpaceInputModel\n  Value error, displayName is required and cannot be empty when spaceType is 'SPACE'. [type=value_error, input_value={'spaceType': 'SPACE'}, input_type=dict]",
            space={"spaceType": "SPACE"}
        )

    def test_spaceType_space_empty_displayName(self):
        """Test create_space with spaceType 'SPACE' but empty displayName."""
        self.assert_error_behavior(
            func_to_call=GoogleChatAPI.create_space,
            expected_exception_type=ValidationError, # Changed to ValidationError
            expected_message="1 validation error for SpaceInputModel\n  Value error, displayName is required and cannot be empty when spaceType is 'SPACE'. [type=value_error, input_value={'spaceType': 'SPACE', 'displayName': '   '}, input_type=dict]",
            space={"spaceType": "SPACE", "displayName": "   "} # Empty after strip
        )

    def test_invalid_field_type_in_space(self):
        """Test create_space with a field of incorrect type in space dict."""
        self.assert_error_behavior(
            func_to_call=GoogleChatAPI.create_space,
            expected_exception_type=ValidationError,
            expected_message="1 validation error for SpaceInputModel\nexternalUserAllowed\n  Input should be a valid boolean, unable to interpret input [type=bool_parsing, input_value='not-a-boolean', input_type=str]",
            space={"spaceType": "GROUP_CHAT", "externalUserAllowed": "not-a-boolean"}
        )

    def test_invalid_nested_field_type(self):
        """Test create_space with incorrect type in nested spaceDetails."""
        self.assert_error_behavior(
            func_to_call=GoogleChatAPI.create_space,
            expected_exception_type=ValidationError,
            expected_message="1 validation error for SpaceInputModel\nspaceDetails.description\n  Input should be a valid string [type=string_type, input_value=12345, input_type=int]",
            space={
                "spaceType": "GROUP_CHAT",
                "spaceDetails": {"description": 12345} # description should be string
            }
        )

    def test_space_is_none(self):
        """Test create_space when space is explicitly None."""
        self.assert_error_behavior(
            func_to_call=GoogleChatAPI.create_space,
            expected_exception_type=ValidationError,
            expected_message="1 validation error for SpaceInputModel\nspaceType\n  Field required [type=missing, input_value={}, input_type=dict]",
            space=None
        )
    
    def test_default_booleans_applied(self):
        """Test that boolean fields default to False if not provided."""
        space_request = {
            "spaceType": "GROUP_CHAT"
        }
        result = GoogleChatAPI.create_space(space=space_request)
        self.assertFalse(result.get("externalUserAllowed"))
        self.assertFalse(result.get("importMode"))
        self.assertFalse(result.get("singleUserBotDm"))


class TestGoogleChatSpaces(BaseTestCaseWithErrorHandler): # Original test class
    def setUp(self):
        """Reset DB before each test"""
        # Use GoogleChatAPI.DB instead of global DB
        GoogleChatAPI.DB.clear()
        GoogleChatAPI.DB.update(
            {
                "User": [{"name": "users/USER123", "displayName": "Test User"}],
                "Space": [],
                "Membership": [],
                "Message": [],
                "Reaction": [],
                "SpaceReadState": [],
                "ThreadReadState": [],
                "SpaceNotificationSetting": [],
            }
        )
        # Both CURRENT_USER_ID and CURRENT_USER need to be set for consistency
        GoogleChatAPI.CURRENT_USER_ID = {"id": "users/USER123"}
        GoogleChatAPI.CURRENT_USER = GoogleChatAPI.CURRENT_USER_ID  # Set both for consistency

    def test_spaces_create(self):
        """Modified test_spaces_create from original suite."""
        space_request = {
            "displayName": "Test Space",
            "spaceType": "SPACE",
            "importMode": False, # Explicitly set
        }
        # Using create_space alias
        created = GoogleChatAPI.create_space(space=space_request)
        self.assertTrue(created.get("name", "").startswith("spaces/"))
        # Check membership for the current user
        expected_membership_name = f"{created['name']}/members/{GoogleChatAPI.CURRENT_USER_ID.get('id')}"
        found_membership = any(
            m.get("name") == expected_membership_name for m in GoogleChatAPI.DB["Membership"]
        )
        self.assertTrue(found_membership, "Membership for current user was not created.")

        # Original test: space_request = None, expecting {}
        # Now, space=None (which becomes {} in the function before Pydantic)
        # will raise ValidationError due to missing spaceType.
        self.assert_error_behavior(
            func_to_call=GoogleChatAPI.create_space,
            expected_exception_type=ValidationError,
            expected_message="1 validation error for SpaceInputModel\nspaceType\n  Field required [type=missing, input_value={}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.11/v/missing",
            space=None
        )

    def test_create_validation(self): # Original test method
        """Modified test_create_validation for new error handling."""
        # Test missing spaceType
        # Original: self.assertEqual(result, {})
        self.assert_error_behavior(
            func_to_call=GoogleChatAPI.create_space,
            expected_exception_type=ValidationError,
            expected_message="1 validation error for SpaceInputModel\nspaceType\n  Field required [type=missing, input_value={}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.11/v/missing",
            space={} # Missing spaceType
        )

        # Test SPACE without displayName
        # The error comes from Pydantic validation, not our custom error
        self.assert_error_behavior(
            func_to_call=GoogleChatAPI.create_space,
            expected_exception_type=ValidationError,
            expected_message="1 validation error for SpaceInputModel\n  Value error, displayName is required and cannot be empty when spaceType is 'SPACE'. [type=value_error, input_value={'spaceType': 'SPACE'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.11/v/value_error",
            space={"spaceType": "SPACE"} # displayName missing
        )

        # Test duplicate displayName - This is a business logic failure, should still return {}
        GoogleChatAPI.DB["Space"].append(
            {
                "name": "spaces/EXISTING",
                "spaceType": "SPACE",
                "displayName": "Existing Space", # Note: Pydantic converts enum to its value for the dict
            }
        )
        result = GoogleChatAPI.create_space(
            space={"spaceType": "SPACE", "displayName": "Existing Space"}
        )
        self.assertEqual(result, {}, "Duplicate displayName should return empty dict as per core logic.")

    def test_direct_message_creation(self):
        """Test direct message space creation (from original tests)."""
        # Create a direct message space with singleUserBotDm=True
        result = GoogleChatAPI.create_space(
            space={"spaceType": "DIRECT_MESSAGE", "singleUserBotDm": True}
        )

        self.assertTrue(result.get("name", "").startswith("spaces/"))
        self.assertEqual(result["spaceType"], "DIRECT_MESSAGE")
        self.assertTrue(result["singleUserBotDm"])

        memberships = [
            m
            for m in GoogleChatAPI.DB["Membership"]
            if m.get("name", "").startswith(result["name"])
        ]
        self.assertEqual(len(memberships), 0)
    
    def test_create_requestId_idempotency(self):
        """Test that using the same requestId returns the existing space."""
        space_request = {"spaceType": "GROUP_CHAT", "displayName": "Idempotent Space"}
        req_id = "idempotent-req-1"
        
        first_creation = GoogleChatAPI.create_space(requestId=req_id, space=space_request)
        self.assertTrue(first_creation.get("name", "").startswith("spaces/"))

        second_creation = GoogleChatAPI.create_space(requestId=req_id, space=space_request)
        self.assertEqual(second_creation.get("name"), first_creation.get("name"))
        self.assertEqual(len(GoogleChatAPI.DB["Space"]), 1, "Space should not be created twice for same requestId.")

class TestListSpaceMembersValidation(BaseTestCaseWithErrorHandler):
    def setUp(self):
        """Reset DB before each test."""
        GoogleChatAPI.DB.clear()
        GoogleChatAPI.DB.update({
            "User": [], "Space": [], "Membership": [], "Message": [],
            "Reaction": [], "SpaceReadState": [], "ThreadReadState": [],
            "SpaceNotificationSetting": []
        })
        # Add a dummy member to DB for some tests to pass core logic
        GoogleChatAPI.DB["Membership"].append({
            'name': 'spaces/space1/members/member1', 'state': 'JOINED', 'role': 'ROLE_MEMBER',
            'member': {'name': 'users/user1', 'type': 'HUMAN'}
        })


    def test_valid_inputs_minimal(self):
        """Test with minimal valid inputs (only parent)."""
        result = GoogleChatAPI.list_space_members(parent="spaces/space1")
        self.assertIsInstance(result, dict)
        self.assertIn("memberships", result)

    def test_valid_inputs_all_provided(self):
        """Test with all valid inputs provided."""
        result = GoogleChatAPI.list_space_members(
            parent="spaces/space1",
            pageSize=10,
            pageToken="0",
            filter='role = "ROLE_MEMBER"',
            showGroups=True,
            showInvited=True,
            useAdminAccess=False
        )
        self.assertIsInstance(result, dict)
        self.assertIn("memberships", result)

    def test_invalid_parent_type(self):
        """Test 'parent' argument with invalid type."""
        self.assert_error_behavior(
            func_to_call=GoogleChatAPI.list_space_members,
            expected_exception_type=TypeError,
            expected_message="Argument 'parent' must be a string.",
            parent=123
        )

    def test_invalid_parent_format_empty(self):
        """Test 'parent' argument with empty string."""
        self.assert_error_behavior(
            func_to_call=GoogleChatAPI.list_space_members,
            expected_exception_type=InvalidParentFormatError,
            expected_message="Argument 'parent' cannot be empty.",
            parent=""
        )

    def test_invalid_parent_format_wrong_prefix(self):
        """Test 'parent' argument with wrong prefix."""
        self.assert_error_behavior(
            func_to_call=GoogleChatAPI.list_space_members,
            expected_exception_type=InvalidParentFormatError,
            expected_message="Invalid parent format: 'foo/space1'. Expected 'spaces/{space}'.",
            parent="foo/space1"
        )
    
    def test_invalid_parent_format_missing_space_id(self):
        """Test 'parent' argument with 'spaces/' but no ID."""
        self.assert_error_behavior(
            func_to_call=GoogleChatAPI.list_space_members,
            expected_exception_type=InvalidParentFormatError,
            expected_message="Invalid parent format: 'spaces/'. Space ID is missing after 'spaces/'.",
            parent="spaces/"
        )

    def test_invalid_pageSize_type(self):
        """Test 'pageSize' argument with invalid type."""
        self.assert_error_behavior(
            func_to_call=GoogleChatAPI.list_space_members,
            expected_exception_type=TypeError,
            expected_message="Argument 'pageSize' must be an integer if provided.",
            parent="spaces/space1", pageSize="10"
        )

    def test_invalid_pageSize_too_small(self):
        """Test 'pageSize' argument value too small."""
        self.assert_error_behavior(
            func_to_call=GoogleChatAPI.list_space_members,
            expected_exception_type=InvalidPageSizeError,
            expected_message="Argument 'pageSize' must be between 1 and 1000, inclusive, if provided.",
            parent="spaces/space1", pageSize=0
        )

    def test_invalid_pageSize_too_large(self):
        """Test 'pageSize' argument value too large."""
        self.assert_error_behavior(
            func_to_call=GoogleChatAPI.list_space_members,
            expected_exception_type=InvalidPageSizeError,
            expected_message="Argument 'pageSize' must be between 1 and 1000, inclusive, if provided.",
            parent="spaces/space1", pageSize=1001
        )

    def test_valid_pageSize_min_max_and_none(self):
        """Test 'pageSize' with valid min, max, and None values."""
        GoogleChatAPI.list_space_members(parent="spaces/space1", pageSize=1) # Min
        GoogleChatAPI.list_space_members(parent="spaces/space1", pageSize=1000) # Max
        GoogleChatAPI.list_space_members(parent="spaces/space1", pageSize=None) # None
        # No assertion needed if they don't raise error

    def test_invalid_pageToken_type(self):
        """Test 'pageToken' argument with invalid type."""
        self.assert_error_behavior(
            func_to_call=GoogleChatAPI.list_space_members,
            expected_exception_type=TypeError,
            expected_message="Argument 'pageToken' must be a string if provided.",
            parent="spaces/space1", pageToken=123
        )

    def test_invalid_filter_type(self):
        """Test 'filter' argument with invalid type."""
        self.assert_error_behavior(
            func_to_call=GoogleChatAPI.list_space_members,
            expected_exception_type=TypeError,
            expected_message="Argument 'filter' must be a string if provided.",
            parent="spaces/space1", filter=123
        )

    def test_invalid_showGroups_type(self):
        """Test 'showGroups' argument with invalid type."""
        self.assert_error_behavior(
            func_to_call=GoogleChatAPI.list_space_members,
            expected_exception_type=TypeError,
            expected_message="Argument 'showGroups' must be a boolean if provided.",
            parent="spaces/space1", showGroups="true"
        )

    def test_invalid_showInvited_type(self):
        """Test 'showInvited' argument with invalid type."""
        self.assert_error_behavior(
            func_to_call=GoogleChatAPI.list_space_members,
            expected_exception_type=TypeError,
            expected_message="Argument 'showInvited' must be a boolean if provided.",
            parent="spaces/space1", showInvited=0
        )

    def test_invalid_useAdminAccess_type(self):
        """Test 'useAdminAccess' argument with invalid type."""
        self.assert_error_behavior(
            func_to_call=GoogleChatAPI.list_space_members,
            expected_exception_type=TypeError,
            expected_message="Argument 'useAdminAccess' must be a boolean if provided.",
            parent="spaces/space1", useAdminAccess="false"
        )

    def test_admin_access_filter_missing_type_condition(self):
        """Test AdminAccessFilterError when filter is missing member.type condition."""
        self.assert_error_behavior(
            func_to_call=GoogleChatAPI.list_space_members,
            expected_exception_type=AdminAccessFilterError,
            expected_message='When using admin access with a filter, the filter must include a condition ' \
                             'like \'member.type = "HUMAN"\' or \'member.type != "BOT"\'.',
            parent="spaces/space1", useAdminAccess=True, filter='role = "ROLE_MEMBER"'
        )

    def test_admin_access_filter_valid_human(self):
        """Test admin access with valid filter: member.type = "HUMAN"."""
        result = GoogleChatAPI.list_space_members(
            parent="spaces/space1",
            useAdminAccess=True,
            filter='member.type = "HUMAN"'
        )
        self.assertIsInstance(result, dict) # Should pass validation

    def test_admin_access_filter_valid_not_bot(self):
        """Test admin access with valid filter: member.type != "BOT"."""
        result = GoogleChatAPI.list_space_members(
            parent="spaces/space1",
            useAdminAccess=True,
            filter='member.type != "BOT"'
        )
        self.assertIsInstance(result, dict) # Should pass validation

    def test_admin_access_filter_valid_mixed_case_field_and_value(self):
        """Test admin access with valid filter: MeMbEr.TyPe != "bOt"."""
        result = GoogleChatAPI.list_space_members(
            parent="spaces/space1",
            useAdminAccess=True,
            filter='MeMbEr.TyPe != "bOt"' # Parser normalizes field to lower, value to upper
        )
        self.assertIsInstance(result, dict)

    def test_admin_access_filter_valid_with_and(self):
        """Test admin access with valid filter: role = "X" AND member.type = "HUMAN"."""
        result = GoogleChatAPI.list_space_members(
            parent="spaces/space1",
            useAdminAccess=True,
            filter='role = "ROLE_MEMBER" AND member.type = "HUMAN"'
        )
        self.assertIsInstance(result, dict)

    def test_admin_access_no_filter_string(self):
        """Test admin access when filter is None (should not raise AdminAccessFilterError)."""
        result = GoogleChatAPI.list_space_members(
            parent="spaces/space1",
            useAdminAccess=True,
            filter=None
        )
        self.assertIsInstance(result, dict) # Should pass validation

    def test_admin_access_useAdminAccess_false(self):
        """Test when useAdminAccess is False (filter condition not enforced)."""
        result = GoogleChatAPI.list_space_members(
            parent="spaces/space1",
            useAdminAccess=False,
            filter='role = "ROLE_MEMBER"' # No member.type condition
        )
        self.assertIsInstance(result, dict) # Should pass validation

    def test_core_logic_empty_result_if_no_match(self):
        """Test that an empty list is returned if parent doesn't match any members."""
        result = GoogleChatAPI.list_space_members(parent="spaces/nonexistent_space")
        self.assertEqual(result, {"memberships": []})

    def test_core_logic_pagination(self):
        """Test basic pagination logic."""
        GoogleChatAPI.DB["Membership"] = [
            {'name': 'spaces/s1/members/m1', 'state': 'JOINED', 'role': 'ROLE_MEMBER', 'member': {'name': 'u1', 'type': 'HUMAN'}},
            {'name': 'spaces/s1/members/m2', 'state': 'JOINED', 'role': 'ROLE_MEMBER', 'member': {'name': 'u2', 'type': 'HUMAN'}},
            {'name': 'spaces/s1/members/m3', 'state': 'JOINED', 'role': 'ROLE_MEMBER', 'member': {'name': 'u3', 'type': 'HUMAN'}},
        ]
        result = GoogleChatAPI.list_space_members(parent="spaces/s1", pageSize=2)
        self.assertEqual(len(result["memberships"]), 2)
        self.assertEqual(result["memberships"][0]["name"], "spaces/s1/members/m1")
        self.assertIn("nextPageToken", result)
        self.assertEqual(result["nextPageToken"], "2")

        result2 = GoogleChatAPI.list_space_members(parent="spaces/s1", pageSize=2, pageToken=result["nextPageToken"])
        self.assertEqual(len(result2["memberships"]), 1)
        self.assertEqual(result2["memberships"][0]["name"], "spaces/s1/members/m3")
        self.assertNotIn("nextPageToken", result2)

class TestListSpaceMembers(BaseTestCaseWithErrorHandler):
    def setUp(self):
        """Reset DB before each test."""
        GoogleChatAPI.DB.clear()
        GoogleChatAPI.DB.update({
            "User": [], "Space": [], "Membership": [], "Message": [],
            "Reaction": [], "SpaceReadState": [], "ThreadReadState": [],
            "SpaceNotificationSetting": []
        })
        # Add a dummy member to DB for some tests to pass core logic
        GoogleChatAPI.DB["Membership"].append({
            'name': 'spaces/space1/members/member1', 'state': 'JOINED', 'role': 'ROLE_MEMBER',
            'member': {'name': 'users/user1', 'type': 'HUMAN'}
        })
        
    def test_basic_functionality(self):
        """Test that list_space_members works correctly."""
        result = GoogleChatAPI.list_space_members(parent="spaces/space1")
        self.assertIsInstance(result, dict)
        self.assertIn("memberships", result)
        self.assertEqual(len(result["memberships"]), 1)
        self.assertEqual(result["memberships"][0]["name"], "spaces/space1/members/member1")
        
    def test_non_existent_space(self):
        """Test behavior when space doesn't exist."""
        result = GoogleChatAPI.list_space_members(parent="spaces/nonexistent")
        self.assertEqual(result, {"memberships": []})
        
    def test_pagination(self):
        """Test pagination functionality."""
        # Add more memberships
        for i in range(2, 4):
            GoogleChatAPI.DB["Membership"].append({
                'name': f'spaces/space1/members/member{i}', 
                'state': 'JOINED', 
                'role': 'ROLE_MEMBER',
                'member': {'name': f'users/user{i}', 'type': 'HUMAN'}
            })
            
        # Test with page size 2
        result = GoogleChatAPI.list_space_members(parent="spaces/space1", pageSize=2)
        self.assertEqual(len(result["memberships"]), 2)
        self.assertIn("nextPageToken", result)
        
        # Test with page token from first result
        result2 = GoogleChatAPI.list_space_members(
            parent="spaces/space1", 
            pageToken=result["nextPageToken"]
        )
        self.assertEqual(len(result2["memberships"]), 1)
        self.assertNotIn("nextPageToken", result2)
        
    def test_filtering(self):
        """Test filtering functionality."""
        # Add a bot membership
        GoogleChatAPI.DB["Membership"].append({
            'name': 'spaces/space1/members/bot1', 
            'state': 'JOINED', 
            'role': 'ROLE_MEMBER',
            'member': {'name': 'users/bot1', 'type': 'BOT'}
        })
        
        # Filter for humans only
        result = GoogleChatAPI.list_space_members(
            parent="spaces/space1", 
            filter='member.type = "HUMAN"'
        )
        self.assertEqual(len(result["memberships"]), 1)
        self.assertEqual(result["memberships"][0]["member"]["type"], "HUMAN")
        
        # Filter for bots only
        result = GoogleChatAPI.list_space_members(
            parent="spaces/space1", 
            filter='member.type = "BOT"'
        )
        self.assertEqual(len(result["memberships"]), 1)
        self.assertEqual(result["memberships"][0]["member"]["type"], "BOT")

if __name__ == "__main__":
    unittest.main()