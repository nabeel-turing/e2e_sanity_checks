import copy
import unittest
from datetime import datetime, timezone, timedelta

from whatsapp.SimulationEngine.db import DB
from whatsapp.SimulationEngine import custom_errors
from whatsapp.SimulationEngine.models import MediaType
from whatsapp.chats import get_direct_chat_by_contact
from common_utils.base_case import BaseTestCaseWithErrorHandler

from whatsapp import get_last_interaction

def _create_contact_in_db_new_structure(
    jid: str,
    given_name: str = None,
    family_name: str = None,
    phone_number: str = None,
    profile_name: str = None,
    is_whatsapp_user: bool = True
) -> dict:
    """
    Helper function to create a contact dictionary matching the NEW DB structure.
    This replaces the old, flat structure creation.
    """
    # Use the phone number from the JID if not provided explicitly
    actual_phone_number = phone_number or jid.split('@')[0]
    
    # The key for the contacts dictionary is the resourceName
    resource_name = f"people/{jid}"

    contact_data = {
        "resourceName": resource_name,
        "etag": f"etag-for-{jid}",
        "names": [{"givenName": given_name, "familyName": family_name}] if given_name else [],
        "emailAddresses": [],
        "phoneNumbers": [{"value": actual_phone_number, "type": "mobile", "primary": True}],
        "organizations": [],
        "isWorkspaceUser": False,
        "whatsapp": {
            "jid": jid,
            "name_in_address_book": f"{given_name} {family_name}".strip() if given_name else None,
            "profile_name": profile_name,
            "phone_number": actual_phone_number,
            "is_whatsapp_user": is_whatsapp_user,
        },
    }
    DB["contacts"][resource_name] = contact_data
    return contact_data

class TestGetLastInteraction(BaseTestCaseWithErrorHandler):
    MY_JID = "me@s.whatsapp.net"
    CONTACT_JID_1 = "contact1@s.whatsapp.net"
    CONTACT_JID_2 = "contact2@s.whatsapp.net"
    CONTACT_JID_3_NO_INTERACTIONS = "contact3@s.whatsapp.net"
    UNKNOWN_SENDER_JID = "unknown_sender@s.whatsapp.net"
    GROUP_JID_1 = "group1@g.us"

    def setUp(self):
        self._original_DB_state = copy.deepcopy(DB)
        DB.clear()

        # Re-initialize DB with the new, nested structure
        DB["contacts"] = {}
        DB["chats"] = {}
        DB["actions"] = []
        DB["current_user_jid"] = self.MY_JID

        # Use the new helper to create contacts with the correct structure
        _create_contact_in_db_new_structure(self.MY_JID, given_name="Me", profile_name="My Profile")
        _create_contact_in_db_new_structure(self.CONTACT_JID_1, given_name="Contact", family_name="1", profile_name="C1 Profile")
        _create_contact_in_db_new_structure(self.CONTACT_JID_2, given_name="Contact", family_name="2", profile_name="C2 Profile")
        _create_contact_in_db_new_structure(self.CONTACT_JID_3_NO_INTERACTIONS, given_name="Contact", family_name="3")
        _create_contact_in_db_new_structure(self.UNKNOWN_SENDER_JID, profile_name="Unknown User")


        # Timestamps for ordering
        self.ts_now = datetime.now(timezone.utc)
        self.ts_very_old = (self.ts_now - timedelta(days=1)).isoformat()
        self.ts1 = (self.ts_now - timedelta(minutes=30)).isoformat()
        self.ts2 = (self.ts_now - timedelta(minutes=20)).isoformat()
        self.ts3 = (self.ts_now - timedelta(minutes=10)).isoformat()
        self.ts4 = (self.ts_now - timedelta(minutes=5)).isoformat()
        self.ts_latest = (self.ts_now - timedelta(minutes=1)).isoformat()

    def tearDown(self):
        DB.clear()
        DB.update(self._original_DB_state)

    def _get_contact_display_name(self, jid):
        """Updated to read from the new contact structure."""
        resource_name = f"people/{jid}"
        contact = DB["contacts"].get(resource_name)
        if contact and contact.get("whatsapp"):
            # Prefer name in address book, fall back to profile name
            return contact["whatsapp"].get("name_in_address_book") or contact["whatsapp"].get("profile_name")
        return None

    def _create_message(self, msg_id, chat_jid, sender_jid, timestamp, text_content, is_outgoing,
                        media_info=None, quoted_message_info=None, sender_name_override=None):
        sender_name = sender_name_override
        if sender_name is None:
            sender_name = self._get_contact_display_name(sender_jid)

        return {
            "message_id": msg_id,
            "chat_jid": str(chat_jid),
            "sender_jid": str(sender_jid),
            "sender_name": sender_name,
            "timestamp": timestamp,
            "text_content": text_content,
            "is_outgoing": is_outgoing,
            "media_info": media_info,
            "quoted_message_info": quoted_message_info,
            "reaction": None,
            "status": "read",
            "forwarded": False
        }

    def test_invalid_jid_format_raises_invalid_jid_error(self):
        self.assert_error_behavior(
            func_to_call=get_last_interaction,
            expected_exception_type=custom_errors.InvalidJIDError,
            expected_message="The provided JID has an invalid format.",
            jid="thisisnotavalidjid"
        )

    def test_non_string_jid_raises_validation_error(self):
        self.assert_error_behavior(
            func_to_call=get_last_interaction,
            expected_exception_type=custom_errors.InvalidParameterError,
            expected_message="Input should be a valid string.",
            jid=12345
        )

    def test_contact_not_found_raises_contact_not_found_error(self):
        non_existent_jid = "00000@s.whatsapp.net"
        self.assert_error_behavior(
            func_to_call=get_last_interaction,
            expected_exception_type=custom_errors.ContactNotFoundError,
            expected_message="The specified contact could not be found.",
            jid=non_existent_jid
        )

    def test_no_chats_in_db_returns_none(self):
        DB["chats"].clear() # Ensure no chats exist
        result = get_last_interaction(jid=self.CONTACT_JID_1)
        self.assertIsNone(result)

    def test_contact_exists_but_no_relevant_messages_returns_none(self):
        # Chat exists, messages exist, but none involve CONTACT_JID_1
        other_chat_id = self.CONTACT_JID_2
        DB["chats"][other_chat_id] = {
            "chat_jid": other_chat_id, "name": "Chat with C2", "is_group": False,
            "messages": [
                self._create_message("msg1", other_chat_id, self.MY_JID, self.ts1, "Hi C2", True),
                self._create_message("msg2", other_chat_id, self.CONTACT_JID_2, self.ts2, "Hello Me", False)
            ]
        }
        result = get_last_interaction(jid=self.CONTACT_JID_1)
        self.assertIsNone(result)

    def test_contact_with_no_interactions_returns_none(self):
        # CONTACT_JID_3_NO_INTERACTIONS exists but has no messages
        result = get_last_interaction(jid=self.CONTACT_JID_3_NO_INTERACTIONS)
        self.assertIsNone(result)

    def test_last_interaction_is_outgoing_message(self):
        chat_id_c1 = self.CONTACT_JID_1
        msg_outgoing_older = self._create_message("msg_out_old", chat_id_c1, self.MY_JID, self.ts1, "Old hi to C1", True)
        msg_incoming_middle = self._create_message("msg_in_mid", chat_id_c1, self.CONTACT_JID_1, self.ts2, "Hello from C1", False)
        msg_outgoing_latest = self._create_message("msg_out_latest", chat_id_c1, self.MY_JID, self.ts3, "Latest hi to C1", True)

        DB["chats"][chat_id_c1] = {
            "chat_jid": chat_id_c1, "name": "Chat C1", "is_group": False,
            "messages": [msg_outgoing_older, msg_incoming_middle, msg_outgoing_latest]
        }
        
        result = get_last_interaction(jid=self.CONTACT_JID_1)
        self.assertIsNotNone(result)
        self.assertEqual(result["message_id"], "msg_out_latest")
        self.assertTrue(result["is_outgoing"])
        self.assertEqual(result["text_content"], "Latest hi to C1")
        self.assertEqual(result["sender_jid"], self.MY_JID)
        self.assertEqual(result["chat_jid"], chat_id_c1)
        self.assertEqual(result["sender_name"], self._get_contact_display_name(self.MY_JID))

    def test_last_interaction_is_incoming_message(self):
        chat_id_c1 = self.CONTACT_JID_1
        msg_incoming_older = self._create_message("msg_in_old", chat_id_c1, self.CONTACT_JID_1, self.ts1, "Old hello from C1", False)
        msg_outgoing_middle = self._create_message("msg_out_mid", chat_id_c1, self.MY_JID, self.ts2, "Hi to C1", True)
        msg_incoming_latest = self._create_message("msg_in_latest", chat_id_c1, self.CONTACT_JID_1, self.ts3, "New hello from C1", False)

        DB["chats"][chat_id_c1] = {
            "chat_jid": chat_id_c1, "name": "Chat C1", "is_group": False,
            "messages": [msg_incoming_older, msg_outgoing_middle, msg_incoming_latest]
        }

        result = get_last_interaction(jid=self.CONTACT_JID_1)
        self.assertIsNotNone(result)
        self.assertEqual(result["message_id"], "msg_in_latest")
        self.assertFalse(result["is_outgoing"])
        self.assertEqual(result["text_content"], "New hello from C1")
        self.assertEqual(result["sender_jid"], self.CONTACT_JID_1)
        self.assertEqual(result["chat_jid"], chat_id_c1)
        self.assertEqual(result["sender_name"], self._get_contact_display_name(self.CONTACT_JID_1))

    def test_last_interaction_across_multiple_chats_for_same_contact(self):
        # Chat 1: 1-on-1 with CONTACT_JID_1
        chat_id_c1_direct = self.CONTACT_JID_1
        msg1_direct = self._create_message("msg1_direct", chat_id_c1_direct, self.CONTACT_JID_1, self.ts1, "Hello in 1-1", False)
        
        # Chat 2: Group chat where MY_JID and CONTACT_JID_1 are participants
        # An incoming message from CONTACT_JID_1 in a group chat is an interaction.
        msg2_group_from_c1 = self._create_message("msg2_grp_c1", self.GROUP_JID_1, self.CONTACT_JID_1, self.ts2, "C1 in group", False)
        
        # Chat 3: Another message in 1-on-1 with CONTACT_JID_1, outgoing, latest overall
        msg3_direct_outgoing_latest = self._create_message("msg3_direct_out", chat_id_c1_direct, self.MY_JID, self.ts3, "Bye C1", True)

        DB["chats"] = {
            chat_id_c1_direct: {"chat_jid": chat_id_c1_direct, "is_group": False, "messages": [msg1_direct, msg3_direct_outgoing_latest]},
            self.GROUP_JID_1: {"chat_jid": self.GROUP_JID_1, "is_group": True, 
                               "messages": [
                                   msg2_group_from_c1, 
                                   self._create_message("grp_other", self.GROUP_JID_1, self.CONTACT_JID_2, self.ts_latest, "C2 in group", False) # Irrelevant sender
                                ]}
        }

        result = get_last_interaction(jid=self.CONTACT_JID_1)
        self.assertIsNotNone(result)
        self.assertEqual(result["message_id"], "msg3_direct_out")
        self.assertTrue(result["is_outgoing"])
        self.assertEqual(result["text_content"], "Bye C1")

        # Now make the group message from C1 the latest
        msg4_group_from_c1_latest = self._create_message("msg4_grp_c1_latest", self.GROUP_JID_1, self.CONTACT_JID_1, self.ts4, "C1 latest in group", False)
        DB["chats"][self.GROUP_JID_1]["messages"].append(msg4_group_from_c1_latest)
        
        result = get_last_interaction(jid=self.CONTACT_JID_1)
        self.assertIsNotNone(result)
        self.assertEqual(result["message_id"], "msg4_grp_c1_latest")
        self.assertFalse(result["is_outgoing"])
        self.assertEqual(result["text_content"], "C1 latest in group")
        self.assertEqual(result["sender_jid"], self.CONTACT_JID_1)
        self.assertEqual(result["chat_jid"], self.GROUP_JID_1)


    def test_all_message_fields_propagated_correctly(self):
        # --- THIS TEST IS MODIFIED ---
        chat_id_c1 = self.CONTACT_JID_1

        # The input data from the DB uses a string for media_type
        media_details_input = {"media_type": "image", "file_name": "photo.jpg", "caption": "A pic", "mime_type": "image/jpeg"}
        quoted_details = {"quoted_message_id": "q_msg_1", "quoted_sender_jid": self.MY_JID, "quoted_text_preview": "Previous text..."}

        full_msg = self._create_message(
            msg_id="full_msg1",
            chat_jid=chat_id_c1,
            sender_jid=self.CONTACT_JID_1,
            timestamp=self.ts_latest,
            text_content="Detailed message with media and quote",
            is_outgoing=False,
            sender_name_override="Contact1 Custom Name",
            media_info=media_details_input,
            quoted_message_info=quoted_details
        )
        DB["chats"][chat_id_c1] = {
            "chat_jid": chat_id_c1, "name": "Chat C1", "is_group": False,
            "messages": [
                self._create_message("older_msg", chat_id_c1, self.MY_JID, self.ts_very_old, "very old", True),
                full_msg
            ]
        }

        # The expected output dictionary now has a string for media_type and includes the default field.
        expected_media_info = {
            "media_type": "image",  # We expect a string in the output
            "file_name": "photo.jpg",
            "caption": "A pic",
            "mime_type": "image/jpeg",
            "simulated_file_size_bytes": None,
            "simulated_local_path": None
        }

        result = get_last_interaction(jid=self.CONTACT_JID_1)

        self.assertIsNotNone(result)
        # Assert on all other fields
        self.assertEqual(result["message_id"], "full_msg1")
        self.assertEqual(result["sender_name"], "Contact1 Custom Name")
        self.assertFalse(result["is_outgoing"])

        # Assert that the returned media_info dictionary matches the expected structure
        self.assertEqual(result["media_info"], expected_media_info)
        self.assertEqual(result["quoted_message_info"], quoted_details)

    def test_minimal_message_fields_propagated_correctly(self):
        # Message with only essential fields, optionals are None
        chat_id_c1 = self.CONTACT_JID_1
        minimal_msg = self._create_message(
            msg_id="min_msg1",
            chat_jid=chat_id_c1,
            sender_jid=self.MY_JID, # Outgoing
            timestamp=self.ts_latest,
            text_content=None, 
            is_outgoing=True,
            media_info=None,
            quoted_message_info=None
            # sender_name will be auto-populated by _create_message
        )
        DB["chats"][chat_id_c1] = {
            "chat_jid": chat_id_c1, "name": "Chat C1", "is_group": False,
            "messages": [minimal_msg]
        }
        result = get_last_interaction(jid=self.CONTACT_JID_1)
        self.assertIsNotNone(result)
        self.assertEqual(result["message_id"], "min_msg1")
        self.assertTrue(result["is_outgoing"])
        self.assertIsNone(result["text_content"])
        self.assertIsNone(result["media_info"])
        self.assertIsNone(result["quoted_message_info"])
        self.assertEqual(result["sender_name"], self._get_contact_display_name(self.MY_JID))

    def test_sender_name_from_message_if_sender_not_in_contacts_or_override(self):
        # UNKNOWN_SENDER_JID is in DB["contacts"] but might have a different name on the message itself.
        # The function should prioritize the sender_name from the message object.
        chat_with_unknown = self.UNKNOWN_SENDER_JID # Chat JID for 1-1
        
        msg_from_unknown = self._create_message(
            msg_id="msg_unknown",
            chat_jid=chat_with_unknown, 
            sender_jid=self.UNKNOWN_SENDER_JID,
            timestamp=self.ts_latest,
            text_content="Message from an unknown entity",
            is_outgoing=False, # Incoming from UNKNOWN_SENDER_JID
            sender_name_override="Special Sender Name In Message" # This should be used
        )
        DB["chats"][chat_with_unknown] = {
             "chat_jid": chat_with_unknown, "name": "Chat with Unknown", "is_group": False,
             "messages": [msg_from_unknown]
        }

        result = get_last_interaction(jid=self.UNKNOWN_SENDER_JID)
        self.assertIsNotNone(result)
        self.assertEqual(result["message_id"], "msg_unknown")
        self.assertEqual(result["sender_jid"], self.UNKNOWN_SENDER_JID)
        self.assertEqual(result["sender_name"], "Special Sender Name In Message")
        self.assertFalse(result["is_outgoing"])

    def test_empty_messages_list_in_relevant_chat_returns_none(self):
        chat_id_c1 = self.CONTACT_JID_1
        DB["chats"][chat_id_c1] = {
            "chat_jid": chat_id_c1, "name": "Chat C1", "is_group": False,
            "messages": [] # Empty messages list
        }
        result = get_last_interaction(jid=self.CONTACT_JID_1)
        self.assertIsNone(result)
    
    def test_malformed_message_in_db_raises_internal_simulation_error(self):
        """
        Tests that an InternalSimulationError is raised if the latest message
        found in the DB is malformed and fails the final Pydantic validation step.
        """
        chat_id_c1 = self.CONTACT_JID_1

        # Create a message that is valid enough to pass initial checks, but will
        # fail the final Pydantic model validation. Here, 'media_info' is a string
        # instead of the expected dictionary, which will cause a validation error.
        malformed_message = {
            "message_id": "malformed_msg_1",
            "chat_jid": str(chat_id_c1),
            "sender_jid": str(self.CONTACT_JID_1),
            "sender_name": "Contact 1",
            "timestamp": self.ts_latest,
            "is_outgoing": False, # This field is now present and valid
            "text_content": "This message has a type error in one of its fields.",
            "media_info": "should-be-a-dictionary", # This will cause PydanticValidationError
            "quoted_message_info": None,
            "reaction": None,
            "status": "read",
            "forwarded": False
        }

        # Place the malformed message in the database. It's the latest one.
        DB["chats"][chat_id_c1] = {
            "chat_jid": chat_id_c1,
            "name": "Chat C1",
            "is_group": False,
            "messages": [malformed_message]
        }

        self.assert_error_behavior(
            func_to_call=get_last_interaction,
            expected_exception_type=custom_errors.InternalSimulationError,
            expected_message="Failed to validate the structure of the found message from the database.",
            jid=self.CONTACT_JID_1
        )

class TestGetDirectChatByContact(BaseTestCaseWithErrorHandler):

    def setUp(self):
        """
        Set up a consistent, new-structure DB state before each test.
        """
        self._original_DB_state = copy.deepcopy(DB)
        DB.clear()

        DB['current_user_jid'] = "0000000000@s.whatsapp.net"
        DB['contacts'] = {}
        DB['chats'] = {}
        DB['actions'] = []

        self.now_iso = datetime.now(timezone.utc).isoformat()
        self.past_iso = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        self.future_iso = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat() # Added missing attribute

    def tearDown(self):
        """Restore the original DB state after each test."""
        DB.clear()
        DB.update(self._original_DB_state)

    def _create_contact_in_db(self, jid: str, given_name: str, family_name: str, profile_name: str = None, is_whatsapp_user: bool = True) -> dict:
        """Helper function to create a contact using the NEW DB structure."""
        resource_name = f"people/{jid}"
        actual_phone_number = jid.split('@')[0]
        
        contact_data = {
            "resourceName": resource_name,
            "etag": f"etag-for-{jid}",
            "names": [{"givenName": given_name, "familyName": family_name}],
            "phoneNumbers": [{"value": actual_phone_number, "type": "mobile", "primary": True}],
            "emailAddresses": [],
            "organizations": [],
            "isWorkspaceUser": False,
            "whatsapp": {
                "jid": jid,
                "name_in_address_book": f"{given_name} {family_name}".strip(),
                "profile_name": profile_name,
                "phone_number": actual_phone_number,
                "is_whatsapp_user": is_whatsapp_user,
            },
        }
        DB["contacts"][resource_name] = contact_data
        return contact_data

    def _create_chat_in_db(self, chat_jid: str, name: str = None, is_group: bool = False, unread_count: int = 0, is_archived: bool = False, is_muted_until: str = None, messages: list = None) -> dict:
        """Helper to create a chat in the DB."""
        messages = messages if messages is not None else []
        last_active = max(msg['timestamp'] for msg in messages) if messages else None
        
        chat_data = {
            "chat_jid": chat_jid, "name": name, "is_group": is_group,
            "last_active_timestamp": last_active, "unread_count": unread_count,
            "is_archived": is_archived, "is_pinned": False, "is_muted_until": is_muted_until,
            "group_metadata": None, "messages": messages,
        }
        DB['chats'][chat_jid] = chat_data
        return chat_data

    def _create_message_dict(self, message_id: str, chat_jid: str, sender_jid: str, text_content: str, timestamp: str, is_outgoing: bool = False, sender_name: str = None, media_info: dict = None, quoted_message_info: dict = None, reaction: str = None, status: str = None, forwarded: bool = False) -> dict:
        """Helper to create a message dictionary."""
        return {
            "message_id": message_id, "chat_jid": chat_jid, "sender_jid": sender_jid,
            "sender_name": sender_name, "timestamp": timestamp, "text_content": text_content,
            "is_outgoing": is_outgoing, "media_info": media_info,
            "quoted_message_info": quoted_message_info, "reaction": reaction,
            "status": status or ("read" if not is_outgoing else "sent"), "forwarded": forwarded
        }

    # Success Cases
    def test_get_direct_chat_success_basic_with_address_book_name(self):
        phone = "1234567890"
        contact_jid = f"{phone}@s.whatsapp.net"
        self._create_contact_in_db(jid=contact_jid, given_name="John", family_name="Doe")
        self._create_chat_in_db(chat_jid=contact_jid)
        
        result = get_direct_chat_by_contact(sender_phone_number=phone)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['chat_jid'], contact_jid)
        self.assertEqual(result['name'], "John Doe")
        self.assertIsNone(result.get('last_message'))

    def test_get_direct_chat_success_with_profile_name_only(self):
        phone = "1234567891"
        contact_jid = f"{phone}@s.whatsapp.net"
        # Create contact with no primary name, but with a profile name to test fallback
        self._create_contact_in_db(jid=contact_jid, given_name="", family_name="", profile_name="Johnny Profile")
        self._create_chat_in_db(chat_jid=contact_jid)

        result = get_direct_chat_by_contact(sender_phone_number=phone)
        self.assertEqual(result['name'], "Johnny Profile")

    def test_get_direct_chat_success_name_precedence_address_book_over_profile(self):
        phone = "1234567892"
        contact_jid = f"{phone}@s.whatsapp.net"
        self._create_contact_in_db(jid=contact_jid, given_name="Addr", family_name="Book Name", profile_name="Profile Name")
        self._create_chat_in_db(chat_jid=contact_jid)

        result = get_direct_chat_by_contact(sender_phone_number=phone)
        self.assertEqual(result['name'], "Addr Book Name")

    def test_get_direct_chat_success_no_contact_name_available(self):
        phone = "1234567893"
        contact_jid = f"{phone}@s.whatsapp.net"
        self._create_contact_in_db(jid=contact_jid, given_name="", family_name="")
        self._create_chat_in_db(chat_jid=contact_jid)

        result = get_direct_chat_by_contact(sender_phone_number=phone)
        self.assertIsNone(result['name'])

    def test_get_direct_chat_success_all_fields_populated(self):
        phone = "2345678901"
        contact_jid = f"{phone}@s.whatsapp.net"
        contact_name = "Alice Wonderland"
        self._create_contact_in_db(jid=contact_jid, given_name="Alice", family_name="Wonderland")

        last_msg_ts = datetime(2023, 10, 26, 10, 0, 0, tzinfo=timezone.utc).isoformat()
        message1 = self._create_message_dict("msg1", contact_jid, contact_jid, "Hello", last_msg_ts, sender_name=contact_name)

        self._create_chat_in_db(
            chat_jid=contact_jid, name=contact_name, unread_count=5, is_archived=True,
            is_muted_until=self.future_iso, messages=[message1]
        )

        result = get_direct_chat_by_contact(sender_phone_number=phone)

        self.assertEqual(result['name'], contact_name)
        self.assertEqual(result['unread_count'], 5)
        self.assertTrue(result['is_archived'])
        self.assertEqual(result['is_muted_until'], self.future_iso)
        self.assertIsNotNone(result['last_message'])
        self.assertEqual(result['last_message']['message_id'], "msg1")

    def test_get_direct_chat_success_muted_indefinitely(self):
        phone = "3456789012"
        contact_jid = f"{phone}@s.whatsapp.net"
        self._create_contact_in_db(jid=contact_jid, given_name="Bob", family_name="The Builder")
        self._create_chat_in_db(chat_jid=contact_jid, is_muted_until="indefinitely")

        result = get_direct_chat_by_contact(sender_phone_number=phone)
        self.assertEqual(result['is_muted_until'], "indefinitely")

    def test_get_direct_chat_success_no_messages_last_message_is_none(self):
        phone = "4567890123"
        contact_jid = f"{phone}@s.whatsapp.net"
        self._create_contact_in_db(jid=contact_jid, given_name="Carol", family_name="Danvers")
        self._create_chat_in_db(chat_jid=contact_jid, messages=[])

        result = get_direct_chat_by_contact(sender_phone_number=phone)
        self.assertIsNone(result['last_message'])

    def test_get_direct_chat_success_multiple_messages_gets_latest_by_timestamp(self):
        phone = "5678901234"
        contact_jid = f"{phone}@s.whatsapp.net"
        self._create_contact_in_db(jid=contact_jid, given_name="Dave", family_name="Grohl")

        ts_old = datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc).isoformat()
        ts_new = datetime(2023, 1, 2, 0, 0, 0, tzinfo=timezone.utc).isoformat()
        ts_newest = datetime(2023, 1, 3, 0, 0, 0, tzinfo=timezone.utc).isoformat()

        msg_old = self._create_message_dict("msg_old", contact_jid, contact_jid, "Old message", ts_old)
        msg_new = self._create_message_dict("msg_new", contact_jid, contact_jid, "New message", ts_new)
        msg_newest = self._create_message_dict("msg_newest", contact_jid, contact_jid, "Newest message", ts_newest)

        # Messages in non-chronological order in the list
        self._create_chat_in_db(chat_jid=contact_jid, messages=[msg_new, msg_old, msg_newest])

        result = get_direct_chat_by_contact(sender_phone_number=phone)
        self.assertIsNotNone(result['last_message'])
        self.assertEqual(result['last_message']['message_id'], "msg_newest")
        self.assertEqual(result['last_message']['text_content'], "Newest message")

    def test_last_message_full_structure_check(self):
        phone = "7778889999"
        contact_jid = f"{phone}@s.whatsapp.net"
        contact_name = "Detailed User"
        self._create_contact_in_db(jid=contact_jid, given_name="Detailed", family_name="User")

        message_ts = datetime(2023, 11, 1, 12, 0, 0, tzinfo=timezone.utc).isoformat()
        media_data = {
            "media_type": MediaType.IMAGE,
            "file_name": "photo.jpg", "caption": "A nice photo", "mime_type": "image/jpeg",
            "simulated_local_path": "/sim/path/photo.jpg",
            "simulated_file_size_bytes": None
        }
        quoted_data = {
            "quoted_message_id": "msg_prev", "quoted_sender_jid": DB['current_user_jid'],
            "quoted_text_preview": "Previous text..."
        }
        last_msg_obj = self._create_message_dict(
            message_id="msg_detail_1", chat_jid=contact_jid, sender_jid=contact_jid,
            text_content="Detailed message.", timestamp=message_ts, is_outgoing=False,
            sender_name=contact_name, media_info=media_data, quoted_message_info=quoted_data,
            reaction="", status="read", forwarded=True
        )
        self._create_chat_in_db(chat_jid=contact_jid, messages=[last_msg_obj])

        result = get_direct_chat_by_contact(sender_phone_number=phone)
        self.assertIsNotNone(result['last_message'])
        self.assertDictEqual(result['last_message'], last_msg_obj)


    # Error Cases: ContactNotFoundError
    def test_contact_not_found_error_no_contact_for_phone_number(self):
        self._create_contact_in_db(jid="1112223333@s.whatsapp.net", given_name="Some", family_name="One")
        self.assert_error_behavior(
            func_to_call=get_direct_chat_by_contact,
            sender_phone_number="9999999999", # Non-existent phone
            expected_exception_type=custom_errors.ContactNotFoundError,
            expected_message="The specified contact could not be found."
        )

    def test_contact_not_found_error_contact_exists_but_no_chat_entry(self):
        phone = "6789012345"
        contact_jid = f"{phone}@s.whatsapp.net"
        self._create_contact_in_db(jid=contact_jid, given_name="Eve", family_name="MissingChat")

        self.assert_error_behavior(
            func_to_call=get_direct_chat_by_contact,
            sender_phone_number=phone,
            expected_exception_type=custom_errors.ContactNotFoundError,
            expected_message="No direct chat found for the specified contact." # Corrected message
        )

    def test_contact_not_found_error_chat_exists_for_contact_jid_but_is_group(self):
        phone = "7890123456"
        contact_jid = f"{phone}@s.whatsapp.net"
        self._create_contact_in_db(jid=contact_jid, given_name="Frank", family_name="Groupie")
        self._create_chat_in_db(chat_jid=contact_jid, is_group=True) # Chat is a group

        self.assert_error_behavior(
            func_to_call=get_direct_chat_by_contact,
            sender_phone_number=phone,
            expected_exception_type=custom_errors.ContactNotFoundError,
            expected_message="No direct chat found for the specified contact." # Corrected message
        )

    # Error Cases: InvalidPhoneNumberError
    def test_invalid_phone_number_error_malformed_too_short(self):
        self.assert_error_behavior(
            func_to_call=get_direct_chat_by_contact,
            sender_phone_number="123",
            expected_exception_type=custom_errors.InvalidPhoneNumberError,
            expected_message="The provided phone number has an invalid format."
        )

    def test_invalid_phone_number_error_malformed_contains_non_digits(self):
        self.assert_error_behavior(
            func_to_call=get_direct_chat_by_contact,
            sender_phone_number="abcdefghij",
            expected_exception_type=custom_errors.InvalidPhoneNumberError,
            expected_message="The provided phone number has an invalid format."
        )

    def test_invalid_phone_number_error_malformed_contains_symbols_not_just_digits(self):
        self.assert_error_behavior(
            func_to_call=get_direct_chat_by_contact,
            sender_phone_number="+123-456-7890", # Assuming strict digit-only validation for this specific error
            expected_exception_type=custom_errors.InvalidPhoneNumberError,
            expected_message="The provided phone number has an invalid format."
        )

    def test_invalid_phone_number_error_contact_exists_but_not_whatsapp_user(self):
        phone = "8901234567"
        contact_jid = f"{phone}@s.whatsapp.net"
        self._create_contact_in_db(jid=contact_jid, given_name="Grace", family_name="NonWA", is_whatsapp_user=False)
        self._create_chat_in_db(chat_jid=contact_jid)

        self.assert_error_behavior(
            func_to_call=get_direct_chat_by_contact,
            sender_phone_number=phone,
            expected_exception_type=custom_errors.InvalidPhoneNumberError,
            expected_message="The provided phone number does not belong to a WhatsApp user." # Corrected message
        )

    # Error Cases: ValidationError (custom_errors.ValidationError)
    def test_validation_error_sender_phone_number_is_none(self):
        self.assert_error_behavior(
            func_to_call=get_direct_chat_by_contact,
            sender_phone_number=None,
            expected_exception_type=custom_errors.InvalidPhoneNumberError,
            expected_message="Input validation failed, sender_phone_number should be a valid string."
        )

    def test_validation_error_sender_phone_number_is_not_string(self):
        self.assert_error_behavior(
            func_to_call=get_direct_chat_by_contact,
            sender_phone_number=1234567890, # Integer
            expected_exception_type=custom_errors.InvalidPhoneNumberError,
            expected_message="Input validation failed, sender_phone_number should be a valid string."
        )

    def test_validation_error_sender_phone_number_is_empty_string(self):
        self.assert_error_behavior(
            func_to_call=get_direct_chat_by_contact,
            sender_phone_number="", # Empty string
            expected_exception_type=custom_errors.InvalidPhoneNumberError, # Or InvalidPhoneNumberError depending on implementation
            expected_message="Input validation failed." # Assuming generic validation message
        )

    # Edge Cases
    def test_edge_case_db_contacts_or_chats_is_none_or_malformed(self):
        # Scenario 1: DB['contacts'] is None
        DB['contacts'] = None
        DB['chats'] = {}
        self.assert_error_behavior(
            func_to_call=get_direct_chat_by_contact,
            sender_phone_number="1234567890",
            expected_message = "The specified contact could not be found.",
            expected_exception_type=custom_errors.ContactNotFoundError # Function should handle gracefully
        )
        DB['contacts'] = {} # Reset for next part

        # Scenario 2: DB['chats'] is None
        DB['chats'] = None
        phone = "1234567890"
        contact_jid = f"{phone}@s.whatsapp.net"
        self._create_contact_in_db(jid=contact_jid, given_name="Some", family_name="One")
        self.assert_error_behavior(
            func_to_call=get_direct_chat_by_contact,
            sender_phone_number="1234567890",
            expected_message = "No direct chat found for the specified contact.",
            expected_exception_type=custom_errors.ContactNotFoundError # Function should handle gracefully
        )

    def test_edge_case_contact_in_db_missing_phone_number_field(self):
        phone_to_search = "1234500000"
        contact_jid = f"{phone_to_search}@s.whatsapp.net"

        # Contact exists by JID, but 'phone_number' field is missing or None
        DB['contacts'][contact_jid] = {
            "jid": contact_jid,
            # "phone_number": phone_to_search, # Field is missing
            "name_in_address_book": "No Phone Field User",
            "is_whatsapp_user": True
        }
        # No chat needed, as contact lookup by phone_number should fail
        self.assert_error_behavior(
            func_to_call=get_direct_chat_by_contact,
            sender_phone_number=phone_to_search,
            expected_message = "The specified contact could not be found.",
            expected_exception_type=custom_errors.ContactNotFoundError
        )

        # Contact has phone_number field but it's None
        DB['contacts'][contact_jid]["phone_number"] = None
        self.assert_error_behavior(
            func_to_call=get_direct_chat_by_contact,
            sender_phone_number=phone_to_search,
            expected_message = "The specified contact could not be found.",
            expected_exception_type=custom_errors.ContactNotFoundError
        )

    def test_internal_error_on_pydantic_validation_failure_from_malformed_db_data(self):
        phone = "9876543210"
        contact_jid = f"{phone}@s.whatsapp.net"
        self._create_contact_in_db(jid=contact_jid, given_name="Pydantic", family_name="Test User")

        malformed_chat_data = {
            "chat_jid": contact_jid, "is_group": False,
            "is_archived": "this-is-not-a-boolean", # Invalid type
            "messages": []
        }
        DB['chats'][contact_jid] = malformed_chat_data

        with self.assertRaises(custom_errors.InternalSimulationError) as cm:
            get_direct_chat_by_contact(sender_phone_number=phone)
        
        exception_message = str(cm.exception)
        self.assertIn("Internal data validation failed", exception_message)
        self.assertIn("is_archived", exception_message)
        self.assertIn("Input should be a valid boolean", exception_message)

if __name__ == '__main__':
    unittest.main()
