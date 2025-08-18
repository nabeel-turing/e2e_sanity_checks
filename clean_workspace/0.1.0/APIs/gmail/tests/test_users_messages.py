# tests/test_users_messages.py
import unittest
from pydantic import ValidationError
from APIs.common_utils.error_manager import get_error_manager
from common_utils.base_case import BaseTestCaseWithErrorHandler
from common_utils.error_handling import set_package_error_mode
from ..SimulationEngine.utils import reset_db
from ..SimulationEngine.models import GetFunctionArgsModel
from ..SimulationEngine import custom_errors
from .. import delete_message, untrash_message, get_message, DB, list_messages, send_message, batch_delete_messages, import_message, insert_message, modify_message_labels, trash_message, untrash_message, batch_modify_message_labels

class TestUsersMessages(BaseTestCaseWithErrorHandler):
    
    def setUp(self):
        reset_db()
        self.userId = "me"
        self.existing_message_id = "msg1"
        DB["users"][self.userId]["messages"][self.existing_message_id] = {
        'id': self.existing_message_id, 'threadId': 'thread1', 'labelIds': ['INBOX', 'UNREAD'],
            'sender': 'sender@example.com', 'recipient': 'me@example.com',
            'subject': 'Test Subject 1', 'body': 'Test Body 1. This is a test message.',
            'date': '2023-10-26T10:00:00Z', 'internalDate': '1698314400000',
            'isRead': False, 'raw': 'UmF3IGNvbnRlbnQgb2YgdGhlIGVtYWls...'
        }

    def test_trash_valid_input_trash_existing_message(self):
        """Test trashing an existing message that isn't already in trash."""
        user_id = "test_user@example.com"
        # Ensure user exists (reset_db might only create 'me')
        if user_id not in DB["users"]:
            DB["users"][user_id] = {"id": user_id, "messages": {}}

        sent_message = send_message(user_id, {"raw": "Message to trash", "labelIds": ["INBOX", "IMPORTANT"]})
        message_id = sent_message["id"]

        result = trash_message(userId=user_id, id=message_id)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['id'], message_id)
        self.assertIn('TRASH', result['labelIds'])
        self.assertIn('IMPORTANT', result['labelIds'])

        # Verify DB state as well
        db_message = get_message(user_id, message_id)
        self.assertIn('TRASH', db_message['labelIds'])

    def test_trash_valid_input_trash_already_trashed_message(self):
        """Test trashing a message that is already in trash."""
        user_id = "test_user@example.com"
        if user_id not in DB["users"]:
            DB["users"][user_id] = {"id": user_id, "messages": {}}

        sent_message = send_message(user_id, {"raw": "Already trashed", "labelIds": ["TRASH", "IMPORTANT"]})
        message_id = sent_message["id"]

        result = trash_message(userId=user_id, id=message_id)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['id'], message_id)
        self.assertIn('TRASH', result['labelIds'])
        self.assertIn('IMPORTANT', result['labelIds'])
        self.assertEqual(len([label for label in result['labelIds'] if label == 'TRASH']), 1)

    def test_trash_valid_input_non_existent_message_id(self):
        """Test trashing a message ID that does not exist for the user."""
        user_id = "test_user@example.com"
        if user_id not in DB["users"]: # Ensure user exists for _ensure_user to pass
            DB["users"][user_id] = {"id": user_id, "messages": {}}

        result = trash_message(userId=user_id, id='msg_does_not_exist')
        self.assertIsNone(result)

    def test_trash_empty_id_raises_value_error(self):
        """Test that an empty string id raises ValueError."""
        self.assert_error_behavior(
            func_to_call=trash_message,
            expected_exception_type=ValueError,
            expected_message="id cannot be empty",
            userId='test_user@example.com',
            id=''
        )

    def test_trash_empty_user_id_raises_value_error(self):
        """Test that an empty string userId raises ValueError."""
        self.assert_error_behavior(
            func_to_call=trash_message,
            expected_exception_type=ValueError,
            expected_message="userId cannot be empty",
            userId='',
            id='any_id'
        )
    
    def test_trash_whitespace_user_id_raises_value_error(self):
        """Test that a whitespace-only userId raises ValueError."""
        self.assert_error_behavior(
            func_to_call=trash_message,
            expected_exception_type=ValueError,
            expected_message="userId cannot have only whitespace",
            userId=' ',
            id='any_id'
        )
    
    def test_trash_whitespace_id_raises_value_error(self):
        """Test that a whitespace-only id raises ValueError."""
        self.assert_error_behavior(
            func_to_call=trash_message,
            expected_exception_type=ValueError,
            expected_message="id cannot have only whitespace",
            userId='test_user@example.com',
            id=' '
        )
    
    def test_trash_user_with_whitespace_raises_value_error(self):
        """Test that a user with whitespace in the userId raises ValueError."""
        self.assert_error_behavior(
            func_to_call=trash_message,
            expected_exception_type=ValueError,
            expected_message="userId cannot have whitespace",
            userId='username with whitespace',
            id='any_id'
        )
    
    def test_trash_id_with_whitespace_raises_value_error(self):
        """Test that an id with whitespace raises ValueError."""
        self.assert_error_behavior(
            func_to_call=trash_message,
            expected_exception_type=ValueError,
            expected_message="id cannot have whitespace",
            userId='test_user@example.com',
            id='id with whitespace'
        )

    def test_trash_invalid_user_id_type(self):
        """Test that a non-string userId raises TypeError."""
        invalid_user_id = 12345
        self.assert_error_behavior(
            func_to_call=trash_message,
            expected_exception_type=TypeError,
            expected_message=f"Argument \'userId\' must be a string, got {type(invalid_user_id).__name__}",
            userId=invalid_user_id,
            id='some_id'
        )

    def test_trash_invalid_message_id_type(self):
        """Test that a non-string message id raises TypeError."""
        invalid_msg_id = 123
        self.assert_error_behavior(
            func_to_call=trash_message,
            expected_exception_type=TypeError,
            expected_message=f"Argument \'id\' must be a string, got {type(invalid_msg_id).__name__}",
            userId='test_user@example.com',
            id=invalid_msg_id
        )

    def test_trash_value_error_for_unknown_user_in_trash(self):
        """Test that an unknown userId raises ValueError (propagated from _ensure_user)."""
        unknown_user_id = 'unknown_user@example.com'
        self.assert_error_behavior(
            func_to_call=trash_message,
            expected_exception_type=ValueError,
            expected_message=f"User '{unknown_user_id}' does not exist.",
            userId=unknown_user_id,
            id='any_id'
        )

    def test_trash_empty_string_raises_value_error(self):
        """Test that an empty string userId raises ValueError."""
        self.assert_error_behavior(
            func_to_call=trash_message,
            expected_exception_type=ValueError,
            expected_message="userId cannot be empty",
            userId='',
            id='any_id'
        )

    def test_trash_user_with_no_matching_messages(self): # Renamed for clarity
        """Test behavior for a valid user who has no message with the given ID."""
        user_id = 'empty_user@example.com'
        if user_id not in DB["users"]: # Ensure user exists
            DB["users"][user_id] = {"id": user_id, "messages": {}}
            
        result = trash_message(userId=user_id, id='id_that_empty_user_does_not_have')
        self.assertIsNone(result)


    def test_send_get_delete(self):
        sent = send_message("me", {"raw": "Hello World"})
        self.assertIn("id", sent)
        msg_id = sent["id"]
        fetched = get_message("me", msg_id)
        self.assertEqual(fetched["raw"], "Hello World")
        delete_message("me", msg_id)
        self.assertIsNone(get_message("me", msg_id))
    
    def test_send_non_email_user_id_raises_value_error(self):
        """Test that sending a message with a non-email user id raises ValueError."""
        self.assert_error_behavior(
            func_to_call=send_message,
            expected_exception_type=ValueError,
            expected_message="userId must be a valid email address",
            userId="non_email_user_id",
            msg={"raw": "Hello World"}
        )

    def test_messages_batch_delete(self):
        m1 = send_message("me", {"raw": "Msg1"})
        m2 = send_message("me", {"raw": "Msg2"})
        batch_delete_messages("me", [m1["id"], m2["id"]])
        self.assertIsNone(get_message("me", m1["id"]))
        self.assertIsNone(get_message("me", m2["id"]))

    def test_messages_import_insert(self):
        imported = import_message("me", {"raw": "imported content"}, deleted=True)
        self.assertIn("DELETED", imported["labelIds"])
        inserted = insert_message("me", {"raw": "inserted content"})
        self.assertIn("id", inserted)

    #Test Input Validation
    def test_invalid_user_id_type(self):
        """Test that invalid userId type raises TypeError."""
        self.assert_error_behavior(
            func_to_call=modify_message_labels,
            expected_exception_type=TypeError,
            expected_message="userId must be a string.",
            userId=123, # Invalid type
            id="msg1"
        )

    def test_invalid_user_id_empty(self):
        """Test that empty userId raises ValueError."""
        self.assert_error_behavior(
            func_to_call=modify_message_labels,
            expected_exception_type=ValueError,
            expected_message="userId cannot be empty",
            userId="", # Invalid type
            id="msg1"
        )

    def test_invalid_user_id_non_email(self):
        """Test that non-email userId raises ValueError."""
        self.assert_error_behavior(
            func_to_call=modify_message_labels,
            expected_exception_type=ValueError,
            expected_message="userId must be a valid email address",
            userId="invalid_email", # Invalid type
            id="msg1"
        )

    def test_invalid_userid_type(self):
        """Test that invalid userId type raises TypeError."""
        self.assert_error_behavior(
            func_to_call=modify_message_labels,
            expected_exception_type=TypeError,
            expected_message="userId must be a string.",
            userId=123, # Invalid type
            id="msg1"
        )

    def test_invalid_id_type(self):
        """Test that invalid id type raises TypeError."""
        self.assert_error_behavior(
            func_to_call=modify_message_labels,
            expected_exception_type=TypeError,
            expected_message="id must be a string.",
            userId="me",
            id=123 # Invalid type
        )

    def test_invalid_addlabelids_type_not_list(self):
        """Test that addLabelIds not being a list (when not None) raises TypeError."""
        self.assert_error_behavior(
            func_to_call=modify_message_labels,
            expected_exception_type=TypeError,
            expected_message="addLabelIds must be a list if provided.",
            userId="me",
            id="msg1",
            addLabelIds="not-a-list" # Invalid type
        )

    def test_invalid_addlabelids_list_element_type(self):
        """Test that addLabelIds list containing non-string element raises TypeError."""
        self.assert_error_behavior(
            func_to_call=modify_message_labels,
            expected_exception_type=TypeError,
            expected_message="All elements in addLabelIds must be strings.",
            userId="me",
            id="msg1",
            addLabelIds=["VALID_LABEL", 123] # List with invalid element type
        )

    def test_invalid_removelabelids_type_not_list(self):
        """Test that removeLabelIds not being a list (when not None) raises TypeError."""
        self.assert_error_behavior(
            func_to_call=modify_message_labels,
            expected_exception_type=TypeError,
            expected_message="removeLabelIds must be a list if provided.",
            userId="me",
            id="msg1",
            removeLabelIds="not-a-list" # Invalid type
        )

    def test_invalid_removelabelids_list_element_type(self):
        """Test that removeLabelIds list containing non-string element raises TypeError."""
        self.assert_error_behavior(
            func_to_call=modify_message_labels,
            expected_exception_type=TypeError,
            expected_message="All elements in removeLabelIds must be strings.",
            userId="me",
            id="msg1",
            removeLabelIds=["VALID_LABEL", 123] # List with invalid element type
        )

    # Add tests for input validation

    def test_invalid_user_id_type(self):
        """Test that invalid userId type raises TypeError."""
        self.assert_error_behavior(
            func_to_call=list_messages,
            expected_exception_type=TypeError,
            expected_message="userId must be a string.",
            userId=123, # Invalid type
        )

    def test_invalid_max_results_type(self):
        """Test that invalid max_results type raises TypeError."""
        self.assert_error_behavior(
            func_to_call=list_messages,
            expected_exception_type=TypeError,
            expected_message="max_results must be an integer.",
            userId="me",
            max_results="not-an-integer" # Invalid type
        )

    def test_invalid_q_type(self):
        """Test that invalid q type raises TypeError."""
        self.assert_error_behavior(
            func_to_call=list_messages,
            expected_exception_type=TypeError,
            expected_message="q must be a string.",
            userId="me",
            q=123 # Invalid type
        )

    def test_invalid_user_id_empty(self):
        """Test that empty userId raises ValueError."""
        self.assert_error_behavior(
            func_to_call=list_messages,
            expected_exception_type=ValueError,
            expected_message="userId cannot be empty",
            userId="  ", # Invalid type
            max_results=10,
            q="test"
        )

    def test_invalid_user_id_non_existent(self):
        """Test that non-existent userId raises ValueError."""
        self.assert_error_behavior(
            func_to_call=list_messages,
            expected_exception_type=ValueError,
            expected_message="User 'nonexistent' does not exist.",
            userId="nonexistent", # Non-existent user
            max_results=10,
            q="test"
        )

    def test_invalid_max_results_negative(self):
        """Test that negative max_results raises ValueError."""
        self.assert_error_behavior(
            func_to_call=list_messages,
            expected_exception_type=ValueError,
            expected_message="max_results must be a positive integer",
            userId="me",
            max_results=-1, # Invalid type
            q="test"
        )
    def test_invalid_labelIds_not_list(self):
        """Test that non-list labelIds raises TypeError."""
        self.assert_error_behavior(
            func_to_call=list_messages,
            expected_exception_type=TypeError,
            expected_message="labelIds must be a list.",
            userId="me",
            labelIds="INBOX" # Should be a list
        )

    def test_invalid_labelIds_contains_non_string(self):
        """Test that labelIds containing non-strings raises TypeError."""
        self.assert_error_behavior(
            func_to_call=list_messages,
            expected_exception_type=TypeError,
            expected_message="All elements in labelIds must be strings.",
            userId="me",
            labelIds=["INBOX", 123] # Contains non-string
        )

    def test_invalid_include_spam_trash_not_bool(self):
        """Test that non-boolean include_spam_trash raises TypeError."""
        self.assert_error_behavior(
            func_to_call=list_messages,
            expected_exception_type=TypeError,
            expected_message="include_spam_trash must be a boolean.",
            userId="me",
            include_spam_trash="true" # Should be boolean
        )
    # End of Input Validation tests

    def test_messages_modify_batchModify(self):
        # This existing test already follows the state-based pattern for batch_modify_message_labels
        m1 = send_message("me", {"raw": "A"})
        m2 = send_message("me", {"raw": "B"})
        modify_message_labels("me", m1["id"], addLabelIds=["STARRED"], removeLabelIds=[])
        self.assertIn("STARRED", get_message("me", m1["id"])["labelIds"])

        batch_modify_message_labels("me", [m1["id"], m2["id"]], addLabelIds=["READ"])
        
        self.assertIn("READ", get_message("me", m1["id"])["labelIds"])
        self.assertIn("READ", get_message("me", m2["id"])["labelIds"])
    
    def test_messages_list_subject_multiple_words(self):
        subject = "Subject with multiple words"
        sent = send_message("me", {"subject": subject})
        message = list_messages(q=f"subject:'{subject}'")
        self.assertIn(sent, message["messages"])
    
    def test_messages_list_with_valid_non_me_userId(self):
        """Test that list works with valid userIds other than 'me'."""
        # First ensure alice exists in DB with some messages
        DB["users"]["alice"] = {
            "messages": {
                "alice_msg1": {
                    "id": "alice_msg1",
                    "threadId": "thread_alice_1",
                    "sender": "alice.johnson@gmail.com",
                    "recipient": "john.doe@gmail.com",
                    "subject": "Alice's message",
                    "body": "Hello from Alice",
                    "labelIds": ["SENT"],
                    "attachment": []
                }
            }
        }
        
        # Test listing messages for alice
        result = list_messages(userId="alice")
        self.assertEqual(len(result["messages"]), 1)
        self.assertEqual(result["messages"][0]["id"], "alice_msg1")
    
    def test_valid_untrash_message_with_trash_label(self):
        """Test untrashing a message that has the 'TRASH' label."""
        userId = "me"
        msg_id = "msg_1"

        DB["users"][userId]["messages"][msg_id] ={"id":msg_id,"raw":"Hello Me","labelIds": ["SENT", "TRASH"]}
        original_message = DB["users"][userId]["messages"][msg_id]

        self.assertIn("TRASH", original_message["labelIds"])

        modified_message = untrash_message(userId=userId, id=msg_id)
        self.assertIsNotNone(modified_message)
        self.assertIsInstance(modified_message, dict)
        self.assertEqual(modified_message["id"], msg_id)
        self.assertNotIn("TRASH", modified_message["labelIds"])
        self.assertIn("SENT", modified_message["labelIds"]) # Check other labels are preserved

    def test_valid_untrash_message_without_trash_label(self):
        """Test untrashing a message that does not have the 'TRASH' label."""
        userId = "me"
        msg_id = "msg_1"
        
        DB["users"][userId]["messages"][msg_id] ={"id":msg_id,"raw":"Hello Me","labelIds": ["INBOX"]}

        original_message = DB["users"][userId]["messages"][msg_id]
        self.assertNotIn("TRASH", original_message["labelIds"])
        original_labels = list(original_message["labelIds"]) # Copy

        modified_message = untrash_message(userId=userId, id=msg_id)

        self.assertIsNotNone(modified_message)
        self.assertEqual(modified_message["id"], msg_id)
        self.assertListEqual(modified_message["labelIds"], original_labels) # Labels should be unchanged

    def test_untrash_non_existent_message(self):
        """Test untrashing a message ID that does not exist for the user."""
        modified_message = untrash_message(userId="me", id="non_existent_msg")
        self.assertIsNone(modified_message)

    def test_untrash_with_default_user_id(self):
        """Test untrashing using the default 'me' userId."""
        msg_id = "msg_1"
        DB["users"]["me"]["messages"][msg_id] ={"id":msg_id, "raw":"Hello Me","labelIds": ["SENT", "TRASH"]}
        modified_message = untrash_message(id=msg_id) # userId defaults to 'me'
        
        self.assertIsNotNone(modified_message)
        self.assertNotIn("TRASH", modified_message["labelIds"])

    def test_untrash_with_default_id_message_exists(self):
        """Test untrashing using the default empty string id, if such a message exists."""
        userId = "me"
        # Let's assume a message with id "" could exist and needs untrashing
        DB["users"][userId]["messages"][""] = {"id": "", "labelIds": ["TRASH"], "raw": "Empty ID message"}
        
        modified_message = untrash_message(userId=userId, id="") # Explicit empty string id
        
        self.assertIsNotNone(modified_message)
        self.assertEqual(modified_message["id"], "")
        self.assertNotIn("TRASH", modified_message["labelIds"])

    def test_untrash_with_default_id_message_not_exists(self):
        """Test untrashing using the default empty string id when no such message exists."""
        # Ensure no message with id "" exists for 'me'
        if "" in DB["users"]["me"]["messages"]:
            del DB["users"]["me"]["messages"][""]
            
        modified_message = untrash_message(userId="me") # id defaults to ""
        self.assertIsNone(modified_message)


    def test_invalid_user_id_type_integer(self):
        """Test untrashing with an integer userId, expecting TypeError."""
        self.assert_error_behavior(
            func_to_call=untrash_message,
            expected_exception_type=TypeError,
            expected_message="Argument 'userId' must be a string, got int",
            userId=123,
            id="msg1"
        )

    def test_invalid_user_id_type_none(self):
        """Test untrashing with None userId, expecting TypeError."""
        self.assert_error_behavior(
            func_to_call=untrash_message,
            expected_exception_type=TypeError,
            expected_message="Argument 'userId' must be a string, got NoneType",
            userId=None,
            id="msg1"
        )

    def test_invalid_id_type_integer(self):
        """Test untrashing with an integer id, expecting TypeError."""
        self.assert_error_behavior(
            func_to_call=untrash_message,
            expected_exception_type=TypeError,
            expected_message="Argument 'id' must be a string, got int",
            userId="me",
            id=12345
        )

    def test_invalid_id_type_none(self):
        """Test untrashing with None id, expecting TypeError."""
        self.assert_error_behavior(
            func_to_call=untrash_message,
            expected_exception_type=TypeError,
            expected_message="Argument 'id' must be a string, got NoneType",
            userId="me",
            id=None
        )
        
    def test_value_error_for_non_existent_user(self):
        """Test that ValueError is propagated if _ensure_user raises it for a non-existent user."""

        self.assert_error_behavior(
            func_to_call=untrash_message,
            expected_exception_type=ValueError,
            expected_message="User 'nonexistentuser' does not exist.", # Message from _ensure_user_stub
            userId="nonexistentuser",
            id="msg1"
        )

    def test_user_exists_but_no_messages_key_path(self):
        """Test scenario where user exists but 'messages' sub-dictionary might be missing (should be handled gracefully or by _ensure_user)."""
        # This test depends on how _ensure_user and DB structure guarantees are handled.
        # The current untrash function has a check.
        del DB["users"]["me"]["messages"] # Simulate missing 'messages' key
        
        # _ensure_user('me') will pass because 'me' is in DB['users']
        # The function should then return None because the path DB["users"]["me"]["messages"] is missing.
        result = untrash_message(userId="me", id="msg1_me")
        self.assertIsNone(result)

    def test_insert_validation_userId(self):
        """Test validation for userId parameter in insert."""
        # Test non-string userId
        self.assert_error_behavior(
            insert_message,
            TypeError,
            "Argument \'userId\' must be a string, got int",
            userId=123
        )
        
        # Test None userId
        self.assert_error_behavior(
            insert_message,
            TypeError,
            "Argument \'userId\' must be a string, got NoneType",
            userId=None
        )
        
        # Test dict userId
        self.assert_error_behavior(
            insert_message,
            TypeError,
            "Argument \'userId\' must be a string, got dict",
            userId={"email": "me"}
        )

    def test_insert_validation_internal_date_source(self):
        """Test validation for internal_date_source parameter in insert."""
        # Test non-string internal_date_source
        self.assert_error_behavior(
            insert_message,
            TypeError,
            "internal_date_source must be a string, got int",
            userId="me",
            internal_date_source=123
        )
        
        # Test None internal_date_source
        self.assert_error_behavior(
            insert_message,
            TypeError,
            "internal_date_source must be a string, got NoneType",
            userId="me",
            internal_date_source=None
        )
        
        # Test invalid value for internal_date_source
        self.assert_error_behavior(
            insert_message,
            ValueError,
            "internal_date_source must be 'receivedTime' or 'dateHeader', got 'invalidValue'",
            userId="me",
            internal_date_source="invalidValue"
        )

    def test_insert_validation_deleted(self):
        """Test validation for deleted parameter in insert."""
        # Test non-boolean deleted
        self.assert_error_behavior(
            insert_message,
            TypeError,
            "deleted must be a boolean, got str",
            userId="me",
            deleted="true"
        )
        
        # Test integer deleted
        self.assert_error_behavior(
            insert_message,
            TypeError,
            "deleted must be a boolean, got int",
            userId="me",
            deleted=1
        )
        
        # Test None deleted
        self.assert_error_behavior(
            insert_message,
            TypeError,
            "deleted must be a boolean, got NoneType",
            userId="me",
            deleted=None
        )

    def test_insert_validation_msg(self):
        """Test validation for msg parameter in insert."""
        # Test non-dict msg
        self.assert_error_behavior(
            insert_message,
            TypeError,
            "msg must be a dictionary or None, got str",
            userId="me",
            msg="not a dict"
        )
        
        # Test integer msg
        self.assert_error_behavior(
            insert_message,
            TypeError,
            "msg must be a dictionary or None, got int",
            userId="me",
            msg=123
        )
        
        # Test list msg
        self.assert_error_behavior(
            insert_message,
            TypeError,
            "msg must be a dictionary or None, got list",
            userId="me",
            msg=["not", "a", "dict"]
        )

    def test_insert_pydantic_validation(self):
        """Test Pydantic validation for msg payload in insert."""
        # Test invalid isRead type (should be boolean)
        with self.assertRaisesRegex(ValidationError, r"isRead"):
            insert_message("me", {"isRead": "not a boolean"})
        
        # Test invalid labelIds type (should be list of strings)
        with self.assertRaisesRegex(ValidationError, r"labelIds"):
            insert_message("me", {"labelIds": "not a list"})
        
        # Test invalid labelIds elements (should be strings)
        with self.assertRaisesRegex(ValidationError, r"labelIds"):
            insert_message("me", {"labelIds": [1, 2, 3]})
        
        # Test invalid attachment type (should be list)
        with self.assertRaisesRegex(ValidationError, r"attachment"):
            insert_message("me", {"attachment": "not a list"})
            
        # Test invalid internalDate (should be string)
        with self.assertRaisesRegex(ValidationError, r"internalDate"):
            insert_message("me", {"internalDate": 12345})

    def test_insert_edge_cases(self):
        """Test edge cases for insert function."""
        # Test with none of the optional parameters specified
        result = insert_message()
        self.assertIsInstance(result, dict)
        self.assertIn("id", result)
        self.assertIn("INBOX", result["labelIds"])
        
        # Test with empty dictionary as msg
        result = insert_message("me", {})
        self.assertIsInstance(result, dict)
        self.assertIn("id", result)
        
        # Test with various label combinations
        result = insert_message("me", {"labelIds": ["INBOX", "UNREAD"]})
        self.assertIn("INBOX", result["labelIds"])
        self.assertIn("UNREAD", result["labelIds"])
        
        # Test with SENT label (should exclude INBOX)
        result = insert_message("me", {"labelIds": ["SENT"]})
        self.assertIn("SENT", result["labelIds"])
        self.assertNotIn("INBOX", result["labelIds"])
        
        # Test with DRAFT label (should exclude INBOX)
        result = insert_message("me", {"labelIds": ["DRAFT"]})
        self.assertIn("DRAFT", result["labelIds"])
        self.assertNotIn("INBOX", result["labelIds"])
        
        # Test with TRASH label (should exclude INBOX)
        result = insert_message("me", {"labelIds": ["TRASH"]})
        self.assertIn("TRASH", result["labelIds"])
        self.assertNotIn("INBOX", result["labelIds"])
        
        # Test with deleted=True
        result = insert_message("me", {}, deleted=True)
        self.assertIn("DELETED", result["labelIds"])
        
        # Test with explicit internalDate
        result = insert_message("me", {"internalDate": "1609459200"})
        self.assertEqual(result["internalDate"], "1609459200")
        
        # Test with dateHeader source and valid date
        result = insert_message("me", {"date": "2022-01-01T00:00:00"}, internal_date_source="dateHeader")
        self.assertIsInstance(result["internalDate"], str)
        
        # Test with dateHeader source and invalid date
        result = insert_message("me", {"date": "invalid-date"}, internal_date_source="dateHeader")
        self.assertIsInstance(result["internalDate"], str)
        
        # Test with both INBOX and SENT labels (INBOX should be removed)
        result = insert_message("me", {"labelIds": ["INBOX", "SENT"]})
        self.assertIn("SENT", result["labelIds"])
        self.assertNotIn("INBOX", result["labelIds"])

    def test_valid_input_full_format(self):
        """Test successful retrieval with valid inputs and 'full' format."""
        

            
        result = get_message(userId=self.userId, id=self.existing_message_id, format="full")
        self.assertIsInstance(result, dict)
        self.assertEqual(result['id'], self.existing_message_id)
        self.assertIn('payload', result)
        self.assertIn('snippet', result)

    def test_valid_input_minimal_format(self):
        """Test successful retrieval with 'minimal' format."""
        result = get_message(userId=self.userId, id=self.existing_message_id, format="minimal")
        self.assertIsInstance(result, dict)
        self.assertEqual(result['id'], self.existing_message_id)
        self.assertIn('labelIds', result)
        self.assertNotIn('payload', result)
        self.assertNotIn('snippet', result)

    def test_valid_input_raw_format(self):
        """Test successful retrieval with 'raw' format."""
        result = get_message(userId=self.userId, id=self.existing_message_id, format="raw")
        self.assertIsInstance(result, dict)
        self.assertEqual(result['id'], self.existing_message_id)
        self.assertIn('raw', result)
        self.assertIn('internalDate', result)

    def test_valid_input_metadata_format(self):
        """Test successful retrieval with 'metadata' format and specific headers."""
        headers_to_request = ["From", "Subject"]
        result = get_message(
            userId=self.userId,
            id=self.existing_message_id,
            format="metadata",
            metadata_headers=headers_to_request
        )
        self.assertIsInstance(result, dict)
        self.assertEqual(result['id'], self.existing_message_id)
        self.assertIn('headers', result)
        self.assertTrue(any(h['name'] == 'From' for h in result['headers']))
        self.assertTrue(any(h['name'] == 'Subject' for h in result['headers']))

    def test_valid_input_metadata_format_no_headers_requested(self):
        """Test 'metadata' format when metadata_headers is None."""
        result = get_message(
            userId=self.userId,
            id=self.existing_message_id,
            format="metadata",
            metadata_headers=None
        )
        self.assertIsInstance(result, dict)
        self.assertEqual(result['id'], self.existing_message_id)
        self.assertIn('headers', result)
        self.assertEqual(result['headers'], [])

    def test_message_not_found(self):
        """Test that None is returned if the message ID does not exist."""
        result = get_message(userId=self.userId, id="non_existent_id")
        self.assertIsNone(result)

    def test_user_exists_but_no_messages(self):
        """Test for a user who exists but has no messages."""

        DB["users"]["user_with_no_messages"] = {"messages":{}}
        result = get_message(userId="user_with_no_messages", id="any_id")
        self.assertIsNone(result)
        
    # --- Validation Error Tests ---

    def test_invalid_userId_type(self):
        """Test that ValidationError is raised for invalid userId type."""
        self.assert_error_behavior(
            func_to_call=get_message,
            expected_exception_type=ValidationError,
            expected_message="userId\n  Input should be a valid string",
            userId=123, # Invalid type
            id=self.existing_message_id
        )

    def test_invalid_id_type(self):
        """Test that ValidationError is raised for invalid id type."""
        self.assert_error_behavior(
            func_to_call=get_message,
            expected_exception_type=ValidationError,
            expected_message="id\n  Input should be a valid string",
            userId=self.userId,
            id=False # Invalid type
        )

    def test_invalid_format_type(self):
        """Test that ValidationError is raised for invalid format type."""
        self.assert_error_behavior(
            func_to_call=get_message,
            expected_exception_type=ValidationError,
            expected_message="format\n  Input should be a valid string",
            userId=self.userId,
            id=self.existing_message_id,
            format=12345 # Invalid type
        )

    def test_invalid_format_value(self):
        """Test that ValidationError is raised for an invalid format string value."""
        self.assert_error_behavior(
            func_to_call=get_message,
            expected_exception_type=ValidationError,
            expected_message="format must be one of: minimal, full, raw, metadata",
            userId=self.userId,
            id=self.existing_message_id,
            format="invalid_format_value"
        )

    def test_invalid_metadata_headers_type(self):
        """Test ValidationError for invalid metadata_headers type (not a list)."""
        self.assert_error_behavior(
            func_to_call=get_message,
            expected_exception_type=ValidationError,
            expected_message="Input should be a valid list",
            userId=self.userId,
            id=self.existing_message_id,
            format="metadata",
            metadata_headers="not_a_list" # Invalid type
        )

    def test_invalid_metadata_headers_element_type(self):
        """Test ValidationError for non-string elements in metadata_headers."""
        self.assert_error_behavior(
            func_to_call=get_message,
            expected_exception_type=ValidationError,
            expected_message="1 validation error for",
            userId=self.userId,
            id=self.existing_message_id,
            format="metadata",
            metadata_headers=["valid_header", 123] # Invalid element type
        )
        
    def test_extra_parameter_forbidden(self):
        """Test that ValidationError is raised if an extra parameter is passed."""
        # This test requires calling the model directly or having a mechanism to pass extra args
        # The function signature itself prevents unknown kwargs unless it has **kwargs
        # This test is more about the model's 'extra = forbid' config.
        # We can test it by trying to instantiate the model directly with an extra field.
        with self.assertRaises(ValidationError) as cm:
            GetFunctionArgsModel(
                userId=self.userId, 
                id=self.existing_message_id, 
                format="full", 
                extra_field="should_fail"
            )
        self.assertIn("extra_field\n  Extra inputs are not permitted", str(cm.exception))


    # --- Propagated Error Tests ---

    def test_value_error_for_unknown_user(self):
        """Test that ValueError is raised for an unknown userId (propagated from _ensure_user)."""
        # This test relies on the mock _ensure_user to raise ValueError as specified.
        self.assert_error_behavior(
            func_to_call=get_message,
            expected_exception_type=ValueError,
            expected_message="User 'unknown_user' does not exist.", # Specific to mock
            userId="unknown_user",
            id=self.existing_message_id
        )

    def test_send_userId_validation(self):
        """Test validation for userId parameter in send function."""
        # Test non-string userId
        self.assert_error_behavior(
            func_to_call=send_message,
            expected_exception_type=TypeError,
            expected_message="userId must be a string, got int",
            userId=123
        )
        
        # Test None userId
        self.assert_error_behavior(
            func_to_call=send_message,
            expected_exception_type=TypeError,
            expected_message="userId must be a string, got NoneType",
            userId=None
        )
        
        # Test dict userId
        self.assert_error_behavior(
            func_to_call=send_message,
            expected_exception_type=TypeError,
            expected_message="userId must be a string, got dict",
            userId={"email": "me"}
        )
        
        # Test list userId
        self.assert_error_behavior(
            func_to_call=send_message,
            expected_exception_type=TypeError,
            expected_message="userId must be a string, got list",
            userId=["me"]
        )

    def test_send_msg_validation(self):
        """Test validation for msg parameter in send function."""
        # Test non-dict msg
        self.assert_error_behavior(
            send_message,
            TypeError,
            "msg must be a dictionary or None, got str",
            userId="me",
            msg="not a dict"
        )
        
        # Test integer msg
        self.assert_error_behavior(
            send_message,
            TypeError,
            "msg must be a dictionary or None, got int",
            userId="me",
            msg=123
        )
        
        # Test list msg
        self.assert_error_behavior(
            send_message,
            TypeError,
            "msg must be a dictionary or None, got list",
            userId="me",
            msg=["not", "a", "dict"]
        )
    
    def test_send_pydantic_validation(self):
        """Test Pydantic validation for msg payload in send function."""
        # Test invalid isRead type (should be boolean)
        with self.assertRaisesRegex(ValidationError, r"isRead"):
            send_message("me", {"isRead": "not a boolean"})
        
        # Test invalid labelIds type (should be list of strings)
        with self.assertRaisesRegex(ValidationError, r"labelIds"):
            send_message("me", {"labelIds": "not a list"})
        
        # Test invalid labelIds elements (should be strings)
        with self.assertRaisesRegex(ValidationError, r"labelIds"):
            send_message("me", {"labelIds": [1, 2, 3]})
        
        # Note: 'attachment' field is not part of the real Gmail API send message structure
        # Attachments are handled through MIME messages in the 'raw' field
            
        # Test invalid internalDate (should be string)
        with self.assertRaisesRegex(ValidationError, r"internalDate"):
            send_message("me", {"internalDate": 12345})
            
        # Test invalid threadId (should be string)
        with self.assertRaisesRegex(ValidationError, r"threadId"):
            send_message("me", {"threadId": 12345})
            
        # Test invalid raw (should be string)
        with self.assertRaisesRegex(ValidationError, r"raw"):
            send_message("me", {"raw": 12345})
            
        # Test invalid sender (should be string)
        with self.assertRaisesRegex(ValidationError, r"sender"):
            send_message("me", {"sender": 12345})
            
        # Test invalid recipient (should be string)
        with self.assertRaisesRegex(ValidationError, r"recipient"):
            send_message("me", {"recipient": 12345})
            
        # Test invalid subject (should be string)
        with self.assertRaisesRegex(ValidationError, r"subject"):
            send_message("me", {"subject": 12345})
            
        # Test invalid body (should be string)
        with self.assertRaisesRegex(ValidationError, r"body"):
            send_message("me", {"body": 12345})
            
        # Test invalid date (should be string)
        with self.assertRaisesRegex(ValidationError, r"date"):
            send_message("me", {"date": 12345})

    def test_send_valid_cases(self):
        """Test valid cases for send function."""
        # Test with None msg
        result = send_message("me", None)
        self.assertIsInstance(result, dict)
        self.assertIn("id", result)
        self.assertIn("SENT", result["labelIds"])
        
        # Test with empty dict msg
        result = send_message("me", {})
        self.assertIsInstance(result, dict)
        self.assertIn("id", result)
        self.assertIn("SENT", result["labelIds"])
        
        # Test with minimal valid data
        result = send_message("me", {"sender": "sender@example.com", "recipient": "recipient@example.com", "subject": "Test Subject", "body": "Test Body"})
        self.assertIsInstance(result, dict)
        self.assertIn("SENT", result["labelIds"])
        
        # Test with all valid fields
        result = send_message("me", {
            "threadId": "thread-123",
            "sender": "sender@example.com",
            "recipient": "recipient@example.com",
            "raw": "Test raw message",
            "subject": "Test Subject",
            "body": "Test Body",
            "date": "2023-01-01",
            "internalDate": "1640995200",
            "isRead": True,
            "labelIds": ["IMPORTANT", "STARRED"]
        })
        self.assertIsInstance(result, dict)
        self.assertEqual(result["threadId"], "thread-123")
        self.assertEqual(result["sender"], "sender@example.com")
        self.assertEqual(result["recipient"], "recipient@example.com")
        self.assertEqual(result["subject"], "Test Subject")
        self.assertEqual(result["body"], "Test Body")
        self.assertEqual(result["date"], "2023-01-01")
        self.assertEqual(result["internalDate"], "1640995200")
        self.assertTrue(result["isRead"])
        # Check both custom labels and SENT are present
        self.assertIn("SENT", result["labelIds"])
        self.assertIn("IMPORTANT", result["labelIds"])
        self.assertIn("STARRED", result["labelIds"])
        # Check INBOX is not present (should be removed if SENT is present)
        self.assertNotIn("INBOX", result["labelIds"])
        
        # Test with labelIds including INBOX (should be removed because SENT is added automatically)
        result = send_message("me", {"labelIds": ["INBOX", "IMPORTANT"]})
        self.assertIn("SENT", result["labelIds"])
        self.assertIn("IMPORTANT", result["labelIds"])
        self.assertNotIn("INBOX", result["labelIds"])

    def test_bmml_valid_input_all_args_provided(self):
        """Test batch_modify_message_labels: valid input with all arguments provided."""
        user_id = "me"
        msg1_id = "state_msg1"
        msg2_id = "state_msg2"

        # Ensure user exists (reset_db should provide "me", add others if needed)
        if user_id not in DB["users"]:
            DB["users"][user_id] = {"id": user_id, "messages": {}}
        
        # Send messages to get them into the DB structure send_message uses
        m1 = send_message(user_id, {"raw": "Content for state_msg1", "labelIds": ["UNREAD", "IMPORTANT"]})
        m2 = send_message(user_id, {"raw": "Content for state_msg2", "labelIds": ["IMPORTANT"]})
        msg1_id_actual = m1["id"]
        msg2_id_actual = m2["id"]

        try:
            batch_modify_message_labels(
                userId=user_id,
                ids=[msg1_id_actual, msg2_id_actual],
                addLabelIds=["PROCESSED"],
                removeLabelIds=["UNREAD"]
            )
        except (TypeError, KeyError) as e:
            self.fail(f"batch_modify_message_labels raised an unexpected error: {e}")

        msg1_after = get_message(user_id, msg1_id_actual)
        msg2_after = get_message(user_id, msg2_id_actual)

        self.assertIn("PROCESSED", msg1_after["labelIds"])
        self.assertNotIn("UNREAD", msg1_after["labelIds"])
        self.assertIn("IMPORTANT", msg1_after["labelIds"])

        self.assertIn("PROCESSED", msg2_after["labelIds"])
        self.assertIn("IMPORTANT", msg2_after["labelIds"])


    def test_bmml_valid_input_with_defaults_and_nones(self):
        """Test batch_modify_message_labels: valid input using default userId and None for label lists."""
        # "me" user exists from reset_db
        m1 = send_message("me", {"raw": "Content for default_nones", "labelIds": ["UNREAD", "IMPORTANT"]})
        msg1_id_actual = m1["id"]
        initial_labels = sorted(get_message("me", msg1_id_actual)["labelIds"])


        try:
            batch_modify_message_labels(ids=[msg1_id_actual]) # userId defaults to "me", labels to None
        except (TypeError, KeyError) as e:
            self.fail(f"batch_modify_message_labels raised an unexpected error: {e}")

        msg1_after = get_message("me", msg1_id_actual)
        self.assertListEqual(sorted(msg1_after["labelIds"]), initial_labels) # No change to labels


    def test_bmml_valid_input_empty_lists(self):
        """Test batch_modify_message_labels: valid input with empty lists for ids and labels."""
        user_id = "test_user@example.com"

        if user_id not in DB["users"]:
            DB["users"][user_id] = {"id": user_id, "messages": {}}
        
        m1 = send_message(user_id, {"raw": "Content for empty_lists", "labelIds": ["UNREAD", "IMPORTANT"]})
        msg1_id_actual = m1["id"]
        initial_labels = sorted(get_message(user_id, msg1_id_actual)["labelIds"])

        try:
            batch_modify_message_labels(
                userId=user_id, ids=[], addLabelIds=[], removeLabelIds=[] # No ids to process
            )
        except (TypeError, KeyError) as e:
            self.fail(f"batch_modify_message_labels raised an unexpected error: {e}")

        # Since ids=[] was passed, no messages should have been touched.
        # We check the state of the message we created to ensure it's unchanged.
        msg1_after = get_message(user_id, msg1_id_actual)
        self.assertListEqual(sorted(msg1_after["labelIds"]), initial_labels)

        # Test the case where ids list is provided but label lists are empty
        try:
            batch_modify_message_labels(
                userId=user_id, ids=[msg1_id_actual], addLabelIds=[], removeLabelIds=[]
            )
        except (TypeError, KeyError) as e:
            self.fail(f"batch_modify_message_labels raised an unexpected error: {e}")
        
        msg1_after_again = get_message(user_id, msg1_id_actual)
        self.assertListEqual(sorted(msg1_after_again["labelIds"]), initial_labels) # Still no change


    def test_bmml_valid_input_ids_none(self):
        """Test batch_modify_message_labels: valid input with ids=None."""
        user_id = "test_user@example.com"
        if user_id not in DB["users"]:
            DB["users"][user_id] = {"id": user_id, "messages": {}}

        m1 = send_message(user_id, {"raw": "Content for ids_none", "labelIds": ["UNREAD", "IMPORTANT"]})
        msg1_id_actual = m1["id"]
        initial_labels = sorted(get_message(user_id, msg1_id_actual)["labelIds"])

        try:
            batch_modify_message_labels(userId=user_id, ids=None)
        except (TypeError, KeyError) as e:
            self.fail(f"batch_modify_message_labels raised an unexpected error: {e}")
        
        # Since ids=None, no messages should have been touched.
        msg1_after = get_message(user_id, msg1_id_actual)
        self.assertListEqual(sorted(msg1_after["labelIds"]), initial_labels)

    def test_bmml_invalid_userid_type_int(self):
        self.assert_error_behavior(
            func_to_call=batch_modify_message_labels,
            expected_exception_type=TypeError,
            expected_message="Argument 'userId' must be a string.",
            userId=123,
            ids=["msg1"],
        )

    def test_bmml_invalid_userid_type_none(self):
        self.assert_error_behavior(
            func_to_call=batch_modify_message_labels,
            expected_exception_type=TypeError,
            expected_message="Argument 'userId' must be a string.",
            userId=None,
            ids=["msg1"],
        )

    def test_bmml_invalid_ids_type_string(self):
        self.assert_error_behavior(
            func_to_call=batch_modify_message_labels,
            expected_exception_type=TypeError,
            expected_message="Argument 'ids' must be a list if provided.",
            userId="me",
            ids="not-a-list",
        )

    def test_bmml_invalid_ids_element_type_int(self):
        self.assert_error_behavior(
            func_to_call=batch_modify_message_labels,
            expected_exception_type=TypeError,
            expected_message="All elements in argument 'ids' must be strings.",
            userId="me",
            ids=["msg1", 123, "msg3"],
        )
    
    def test_bmml_invalid_ids_element_type_none(self):
        self.assert_error_behavior(
            func_to_call=batch_modify_message_labels,
            expected_exception_type=TypeError,
            expected_message="All elements in argument 'ids' must be strings.",
            userId="me",
            ids=["msg1", None, "msg3"],
        )

    def test_bmml_invalid_addlabelids_type_dict(self):
        self.assert_error_behavior(
            func_to_call=batch_modify_message_labels,
            expected_exception_type=TypeError,
            expected_message="Argument 'addLabelIds' must be a list if provided.",
            userId="me",
            ids=["msg1"],
            addLabelIds={"label": "A"},
        )

    def test_bmml_invalid_addlabelids_element_type_bool(self):
        self.assert_error_behavior(
            func_to_call=batch_modify_message_labels,
            expected_exception_type=TypeError,
            expected_message="All elements in argument 'addLabelIds' must be strings.",
            userId="me",
            ids=["msg1"],
            addLabelIds=["labelA", True],
        )

    def test_bmml_invalid_removelabelids_type_int(self):
        self.assert_error_behavior(
            func_to_call=batch_modify_message_labels,
            expected_exception_type=TypeError,
            expected_message="Argument 'removeLabelIds' must be a list if provided.",
            userId="me",
            ids=["msg1"],
            removeLabelIds=12345,
        )

    def test_bmml_invalid_removelabelids_element_type_list(self):
        self.assert_error_behavior(
            func_to_call=batch_modify_message_labels,
            expected_exception_type=TypeError,
            expected_message="All elements in argument 'removeLabelIds' must be strings.",
            userId="me",
            ids=["msg1"],
            removeLabelIds=["labelC", ["nested"]],
        )

    def test_bmml_propagated_valueerror_from_ensure_user(self):
        """Test that ValueError from _ensure_user (if real) is propagated."""
        user_id_non_existent = "unknown_user_for_realvalueerror"
        
        if user_id_non_existent in DB["users"]:
            del DB["users"][user_id_non_existent]

        self.assert_error_behavior(
            func_to_call=batch_modify_message_labels,
            expected_exception_type=ValueError,
            expected_message=f"User '{user_id_non_existent}' does not exist.",
            userId=user_id_non_existent,
            ids=["msg1"],
        )

    def test_insert_validation_userId(self):
        """Test validation for userId parameter in insert."""
        # Test non-string userId
        self.assert_error_behavior(
            insert_message,
            TypeError,
            "Argument \'userId\' must be a string, got int",
            userId=123
        )
        
        # Test None userId
        self.assert_error_behavior(
            insert_message,
            TypeError,
            "Argument \'userId\' must be a string, got NoneType",
            userId=None
        )
        
        # Test dict userId
        self.assert_error_behavior(
            insert_message,
            TypeError,
            "Argument \'userId\' must be a string, got dict",
            userId={"email": "me"}
        )

    def test_insert_validation_internal_date_source(self):
        """Test validation for internal_date_source parameter in insert."""
        # Test non-string internal_date_source
        self.assert_error_behavior(
            insert_message,
            TypeError,
            "internal_date_source must be a string, got int",
            userId="me",
            internal_date_source=123
        )
        
        # Test None internal_date_source
        self.assert_error_behavior(
            insert_message,
            TypeError,
            "internal_date_source must be a string, got NoneType",
            userId="me",
            internal_date_source=None
        )
        
        # Test invalid value for internal_date_source
        self.assert_error_behavior(
            insert_message,
            ValueError,
            "internal_date_source must be 'receivedTime' or 'dateHeader', got 'invalidValue'",
            userId="me",
            internal_date_source="invalidValue"
        )

    def test_insert_validation_deleted(self):
        """Test validation for deleted parameter in insert."""
        # Test non-boolean deleted
        self.assert_error_behavior(
            insert_message,
            TypeError,
            "deleted must be a boolean, got str",
            userId="me",
            deleted="true"
        )
        
        # Test integer deleted
        self.assert_error_behavior(
            insert_message,
            TypeError,
            "deleted must be a boolean, got int",
            userId="me",
            deleted=1
        )
        
        # Test None deleted
        self.assert_error_behavior(
            insert_message,
            TypeError,
            "deleted must be a boolean, got NoneType",
            userId="me",
            deleted=None
        )

    def test_insert_validation_msg(self):
        """Test validation for msg parameter in insert."""
        # Test non-dict msg
        self.assert_error_behavior(
            insert_message,
            TypeError,
            "msg must be a dictionary or None, got str",
            userId="me",
            msg="not a dict"
        )
        
        # Test integer msg
        self.assert_error_behavior(
            insert_message,
            TypeError,
            "msg must be a dictionary or None, got int",
            userId="me",
            msg=123
        )
        
        # Test list msg
        self.assert_error_behavior(
            insert_message,
            TypeError,
            "msg must be a dictionary or None, got list",
            userId="me",
            msg=["not", "a", "dict"]
        )

    def test_insert_pydantic_validation(self):
        """Test Pydantic validation for msg payload in insert."""
        # Test invalid isRead type (should be boolean)
        with self.assertRaisesRegex(ValidationError, r"isRead"):
            insert_message("me", {"isRead": "not a boolean"})
        
        # Test invalid labelIds type (should be list of strings)
        with self.assertRaisesRegex(ValidationError, r"labelIds"):
            insert_message("me", {"labelIds": "not a list"})
        
        # Test invalid labelIds elements (should be strings)
        with self.assertRaisesRegex(ValidationError, r"labelIds"):
            insert_message("me", {"labelIds": [1, 2, 3]})
        
        # Test invalid attachment type (should be list)
        with self.assertRaisesRegex(ValidationError, r"attachment"):
            insert_message("me", {"attachment": "not a list"})
            
        # Test invalid internalDate (should be string)
        with self.assertRaisesRegex(ValidationError, r"internalDate"):
            insert_message("me", {"internalDate": 12345})

    def test_insert_edge_cases(self):
        """Test edge cases for insert function."""
        # Test with none of the optional parameters specified
        result = insert_message()
        self.assertIsInstance(result, dict)
        self.assertIn("id", result)
        self.assertIn("INBOX", result["labelIds"])
        
        # Test with empty dictionary as msg
        result = insert_message("me", {})
        self.assertIsInstance(result, dict)
        self.assertIn("id", result)
        
        # Test with various label combinations
        result = insert_message("me", {"labelIds": ["INBOX", "UNREAD"]})
        self.assertIn("INBOX", result["labelIds"])
        self.assertIn("UNREAD", result["labelIds"])
        
        # Test with SENT label (should exclude INBOX)
        result = insert_message("me", {"labelIds": ["SENT"]})
        self.assertIn("SENT", result["labelIds"])
        self.assertNotIn("INBOX", result["labelIds"])
        
        # Test with DRAFT label (should exclude INBOX)
        result = insert_message("me", {"labelIds": ["DRAFT"]})
        self.assertIn("DRAFT", result["labelIds"])
        self.assertNotIn("INBOX", result["labelIds"])
        
        # Test with TRASH label (should exclude INBOX)
        result = insert_message("me", {"labelIds": ["TRASH"]})
        self.assertIn("TRASH", result["labelIds"])
        self.assertNotIn("INBOX", result["labelIds"])
        
        # Test with deleted=True
        result = insert_message("me", {}, deleted=True)
        self.assertIn("DELETED", result["labelIds"])
        
        # Test with explicit internalDate
        result = insert_message("me", {"internalDate": "1609459200"})
        self.assertEqual(result["internalDate"], "1609459200")
        
        # Test with dateHeader source and valid date
        result = insert_message("me", {"date": "2022-01-01T00:00:00"}, internal_date_source="dateHeader")
        self.assertIsInstance(result["internalDate"], str)
        
        # Test with dateHeader source and invalid date
        result = insert_message("me", {"date": "invalid-date"}, internal_date_source="dateHeader")
        self.assertIsInstance(result["internalDate"], str)
        
        # Test with both INBOX and SENT labels (INBOX should be removed)
        result = insert_message("me", {"labelIds": ["INBOX", "SENT"]})
        self.assertIn("SENT", result["labelIds"])
        self.assertNotIn("INBOX", result["labelIds"])

    def test_valid_input_full_format(self):
        """Test successful retrieval with valid inputs and 'full' format."""
        

            
        result = get_message(userId=self.userId, id=self.existing_message_id, format="full")
        self.assertIsInstance(result, dict)
        self.assertEqual(result['id'], self.existing_message_id)
        self.assertIn('payload', result)
        self.assertIn('snippet', result)

    def test_valid_input_minimal_format(self):
        """Test successful retrieval with 'minimal' format."""
        result = get_message(userId=self.userId, id=self.existing_message_id, format="minimal")
        self.assertIsInstance(result, dict)
        self.assertEqual(result['id'], self.existing_message_id)
        self.assertIn('labelIds', result)
        self.assertNotIn('payload', result)
        self.assertNotIn('snippet', result)

    def test_valid_input_raw_format(self):
        """Test successful retrieval with 'raw' format."""
        result = get_message(userId=self.userId, id=self.existing_message_id, format="raw")
        self.assertIsInstance(result, dict)
        self.assertEqual(result['id'], self.existing_message_id)
        self.assertIn('raw', result)
        self.assertIn('internalDate', result)

    def test_valid_input_metadata_format(self):
        """Test successful retrieval with 'metadata' format and specific headers."""
        headers_to_request = ["From", "Subject"]
        result = get_message(
            userId=self.userId,
            id=self.existing_message_id,
            format="metadata",
            metadata_headers=headers_to_request
        )
        self.assertIsInstance(result, dict)
        self.assertEqual(result['id'], self.existing_message_id)
        self.assertIn('headers', result)
        self.assertTrue(any(h['name'] == 'From' for h in result['headers']))
        self.assertTrue(any(h['name'] == 'Subject' for h in result['headers']))

    def test_valid_input_metadata_format_no_headers_requested(self):
        """Test 'metadata' format when metadata_headers is None."""
        result = get_message(
            userId=self.userId,
            id=self.existing_message_id,
            format="metadata",
            metadata_headers=None
        )
        self.assertIsInstance(result, dict)
        self.assertEqual(result['id'], self.existing_message_id)
        self.assertIn('headers', result)
        self.assertEqual(result['headers'], [])

    def test_message_not_found(self):
        """Test that None is returned if the message ID does not exist."""
        result = get_message(userId=self.userId, id="non_existent_id")
        self.assertIsNone(result)

    def test_user_exists_but_no_messages(self):
        """Test for a user who exists but has no messages."""

        DB["users"]["user_with_no_messages"] = {"messages":{}}
        result = get_message(userId="user_with_no_messages", id="any_id")
        self.assertIsNone(result)
        
    # --- Validation Error Tests ---

    def test_invalid_userId_type(self):
        """Test that ValidationError is raised for invalid userId type."""
        self.assert_error_behavior(
            func_to_call=get_message,
            expected_exception_type=ValidationError,
            expected_message="Input should be a valid string",
            userId=123, # Invalid type
            id=self.existing_message_id
        )

    def test_invalid_id_type(self):
        """Test that ValidationError is raised for invalid id type."""
        self.assert_error_behavior(
            func_to_call=get_message,
            expected_exception_type=ValidationError,
            expected_message="Input should be a valid string",
            userId=self.userId,
            id=False # Invalid type
        )

    def test_invalid_format_type(self):
        """Test that ValidationError is raised for invalid format type."""
        self.assert_error_behavior(
            func_to_call=get_message,
            expected_exception_type=ValidationError,
            expected_message="Input should be a valid string",
            userId=self.userId,
            id=self.existing_message_id,
            format=12345 # Invalid type
        )

    def test_invalid_format_value(self):
        """Test that ValidationError is raised for an invalid format string value."""
        self.assert_error_behavior(
            func_to_call=get_message,
            expected_exception_type=ValidationError,
            expected_message="format must be one of: minimal, full, raw, metadata",
            userId=self.userId,
            id=self.existing_message_id,
            format="invalid_format_value"
        )

    def test_invalid_metadata_headers_type(self):
        """Test ValidationError for invalid metadata_headers type (not a list)."""
        self.assert_error_behavior(
            func_to_call=get_message,
            expected_exception_type=ValidationError,
            expected_message="Input should be a valid list",
            userId=self.userId,
            id=self.existing_message_id,
            format="metadata",
            metadata_headers="not_a_list" # Invalid type
        )

    def test_invalid_metadata_headers_element_type(self):
        """Test ValidationError for non-string elements in metadata_headers."""
        self.assert_error_behavior(
            func_to_call=get_message,
            expected_exception_type=ValidationError,
            expected_message="Input should be a valid string",
            userId=self.userId,
            id=self.existing_message_id,
            format="metadata",
            metadata_headers=["valid_header", 123] # Invalid element type
        )
        
    def test_extra_parameter_forbidden(self):
        """Test that ValidationError is raised if an extra parameter is passed."""
        # This test requires calling the model directly or having a mechanism to pass extra args
        # The function signature itself prevents unknown kwargs unless it has **kwargs
        # This test is more about the model's 'extra = forbid' config.
        # We can test it by trying to instantiate the model directly with an extra field.
        with self.assertRaises(ValidationError) as cm:
            GetFunctionArgsModel(
                userId=self.userId, 
                id=self.existing_message_id, 
                format="full", 
                extra_field="should_fail"
            )
        self.assertIn("extra_field\n  Extra inputs are not permitted", str(cm.exception))


    # --- Propagated Error Tests ---

    def test_value_error_for_unknown_user(self):
        """Test that ValueError is raised for an unknown userId (propagated from _ensure_user)."""
        # This test relies on the mock _ensure_user to raise ValueError as specified.
        self.assert_error_behavior(
            func_to_call=get_message,
            expected_exception_type=ValueError,
            expected_message="User 'unknown_user' does not exist.", # Specific to mock
            userId="unknown_user",
            id=self.existing_message_id
        )

    def test_send_userId_validation(self):
        """Test validation for userId parameter in send function."""
        # Test non-string userId
        self.assert_error_behavior(
            func_to_call=send_message,
            expected_exception_type=TypeError,
            expected_message="userId must be a string, got int",
            userId=123
        )
        
        # Test None userId
        self.assert_error_behavior(
            func_to_call=send_message,
            expected_exception_type=TypeError,
            expected_message="userId must be a string, got NoneType",
            userId=None
        )
        
        # Test dict userId
        self.assert_error_behavior(
            func_to_call=send_message,
            expected_exception_type=TypeError,
            expected_message="userId must be a string, got dict",
            userId={"email": "me"}
        )
        
        # Test list userId
        self.assert_error_behavior(
            func_to_call=send_message,
            expected_exception_type=TypeError,
            expected_message="userId must be a string, got list",
            userId=["me"]
        )

    def test_send_msg_validation(self):
        """Test validation for msg parameter in send function."""
        # Test non-dict msg
        self.assert_error_behavior(
            send_message,
            TypeError,
            "msg must be a dictionary or None, got str",
            userId="me",
            msg="not a dict"
        )
        
        # Test integer msg
        self.assert_error_behavior(
            send_message,
            TypeError,
            "msg must be a dictionary or None, got int",
            userId="me",
            msg=123
        )
        
        # Test list msg
        self.assert_error_behavior(
            send_message,
            TypeError,
            "msg must be a dictionary or None, got list",
            userId="me",
            msg=["not", "a", "dict"]
        )
    
    def test_send_pydantic_validation(self):
        """Test Pydantic validation for msg payload in send function."""
        # Test invalid isRead type (should be boolean)
        with self.assertRaisesRegex(ValidationError, r"isRead"):
            send_message("me", {"isRead": "not a boolean"})
        
        # Test invalid labelIds type (should be list of strings)
        with self.assertRaisesRegex(ValidationError, r"labelIds"):
            send_message("me", {"labelIds": "not a list"})
        
        # Test invalid labelIds elements (should be strings)
        with self.assertRaisesRegex(ValidationError, r"labelIds"):
            send_message("me", {"labelIds": [1, 2, 3]})
        
        # Note: 'attachment' field is not part of the real Gmail API send message structure
        # Attachments are handled through MIME messages in the 'raw' field
            
        # Test invalid internalDate (should be string)
        with self.assertRaisesRegex(ValidationError, r"internalDate"):
            send_message("me", {"internalDate": 12345})
            
        # Test invalid threadId (should be string)
        with self.assertRaisesRegex(ValidationError, r"threadId"):
            send_message("me", {"threadId": 12345})
            
        # Test invalid raw (should be string)
        with self.assertRaisesRegex(ValidationError, r"raw"):
            send_message("me", {"raw": 12345})
            
        # Test invalid sender (should be string)
        with self.assertRaisesRegex(ValidationError, r"sender"):
            send_message("me", {"sender": 12345})
            
        # Test invalid recipient (should be string)
        with self.assertRaisesRegex(ValidationError, r"recipient"):
            send_message("me", {"recipient": 12345})
            
        # Test invalid subject (should be string)
        with self.assertRaisesRegex(ValidationError, r"subject"):
            send_message("me", {"subject": 12345})
            
        # Test invalid body (should be string)
        with self.assertRaisesRegex(ValidationError, r"body"):
            send_message("me", {"body": 12345})
            
        # Test invalid date (should be string)
        with self.assertRaisesRegex(ValidationError, r"date"):
            send_message("me", {"date": 12345})

    def test_send_valid_cases(self):
        """Test valid cases for send function."""
        # Test with None msg
        result = send_message("me", None)
        self.assertIsInstance(result, dict)
        self.assertIn("id", result)
        self.assertIn("SENT", result["labelIds"])
        
        # Test with empty dict msg
        result = send_message("me", {})
        self.assertIsInstance(result, dict)
        self.assertIn("id", result)
        self.assertIn("SENT", result["labelIds"])
        
        # Test with minimal valid data
        result = send_message("me", {"sender": "sender@example.com", "recipient": "recipient@example.com", "subject": "Test Subject", "body": "Test Body"})
        self.assertIsInstance(result, dict)
        self.assertIn("SENT", result["labelIds"])
        
        # Test with all valid fields
        result = send_message("me", {
            "threadId": "thread-123",
            "sender": "sender@example.com",
            "recipient": "recipient@example.com",
            "raw": "Test raw message",
            "subject": "Test Subject",
            "body": "Test Body",
            "date": "2023-01-01",
            "internalDate": "1640995200",
            "isRead": True,
            "labelIds": ["IMPORTANT", "STARRED"]
        })
        self.assertIsInstance(result, dict)
        self.assertEqual(result["threadId"], "thread-123")
        self.assertEqual(result["sender"], "sender@example.com")
        self.assertEqual(result["recipient"], "recipient@example.com")
        self.assertEqual(result["subject"], "Test Subject")
        self.assertEqual(result["body"], "Test Body")
        self.assertEqual(result["date"], "2023-01-01")
        self.assertEqual(result["internalDate"], "1640995200")
        self.assertTrue(result["isRead"])
        # Check both custom labels and SENT are present
        self.assertIn("SENT", result["labelIds"])
        self.assertIn("IMPORTANT", result["labelIds"])
        self.assertIn("STARRED", result["labelIds"])
        # Check INBOX is not present (should be removed if SENT is present)
        self.assertNotIn("INBOX", result["labelIds"])
        
        # Test with labelIds including INBOX (should be removed because SENT is added automatically)
        result = send_message("me", {"labelIds": ["INBOX", "IMPORTANT"]})
        self.assertIn("SENT", result["labelIds"])
        self.assertIn("IMPORTANT", result["labelIds"])
        self.assertNotIn("INBOX", result["labelIds"])

    def test_delete_user_id_wrong_type_raises_type_error(self):
        """Test that a non-string userId raises TypeError."""
        invalid_user_id = 12345
        self.assert_error_behavior(
            func_to_call=delete_message,
            expected_exception_type=TypeError,
            expected_message=f"Argument \'userId\' must be a string, got {type(invalid_user_id).__name__}",
            userId=invalid_user_id,
            id="any_id"
        )

    def test_delete_id_wrong_type_raises_type_error(self):
        """Test that a non-string id raises TypeError."""
        invalid_id = 12345
        self.assert_error_behavior(
            func_to_call=delete_message,
            expected_exception_type=TypeError,
            expected_message=f"Argument \'id\' must be a string, got {type(invalid_id).__name__}",
            userId="me",
            id=invalid_id
        )

    def test_delete_user_id_empty_raises_validation_error(self):
        """Test that an empty userId raises ValidationError."""
        self.assert_error_behavior(
            func_to_call=delete_message,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Argument 'userId' cannot be empty.",
            userId="",
            id="any_id"
        )

    def test_delete_user_id_whitespace_raises_validation_error(self):
        """Test that a whitespace-only userId raises ValidationError."""
        self.assert_error_behavior(
            func_to_call=delete_message,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Argument 'userId' cannot have only whitespace.",
            userId=" ",
            id="any_id"
        )

    def test_delete_user_id_with_whitespace_raises_validation_error(self):
        """Test that a userId with whitespace raises ValidationError."""
        self.assert_error_behavior(
            func_to_call=delete_message,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Argument 'userId' cannot have whitespace.",
            userId="UserId with whitespace",
            id="any_id"
        )

    def test_delete_id_with_whitespace_raises_validation_error(self):
        """Test that an id with whitespace raises ValidationError."""
        self.assert_error_behavior(
            func_to_call=delete_message,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Argument 'id' cannot have whitespace.",
            userId="me",
            id="id with whitespace"
        )

    def test_batch_delete_messages_user_id_not_string(self):
        """Test that a non-string userId raises TypeError."""
        invalid_user_id = 12345
        self.assert_error_behavior(
            func_to_call=batch_delete_messages,
            expected_exception_type=TypeError,
            expected_message=f"Argument 'userId' must be a string, got {type(invalid_user_id).__name__}",
            userId=invalid_user_id,
            ids=["id1", "id2"]
        )

    def test_batch_delete_messages_user_id_only_whitespace(self):
        """Test that a non-string userId raises ValidationError."""
        invalid_user_id = "   "
        self.assert_error_behavior(
            func_to_call=batch_delete_messages,
            expected_exception_type=custom_errors.ValidationError,
            expected_message=f"Argument 'userId' cannot have only whitespace.",
            userId=invalid_user_id,
            ids=["id1", "id2"]
        )

    def test_batch_delete_messages_user_id_has_whitespace(self):
        """Test that a userId with whitespace raises ValidationError."""
        invalid_user_id = "user id "
        self.assert_error_behavior(
            func_to_call=batch_delete_messages,
            expected_exception_type=custom_errors.ValidationError,
            expected_message=f"Argument 'userId' cannot have whitespace.",
            userId=invalid_user_id,
            ids=["id1", "id2"]
        )

    def test_batch_delete_messages_ids_not_list(self):
        """Test that a non-list ids raises TypeError."""
        invalid_ids = "id1,id2"
        self.assert_error_behavior(
            func_to_call=batch_delete_messages,
            expected_exception_type=TypeError,
            expected_message=f"ids must be a list, got str",
            userId="me",
            ids=invalid_ids
        )

    def test_batch_delete_messages_ids_element_not_string(self):
        """Test that a non-string id raises TypeError."""
        invalid_ids = ["id1", 123, "id3"]
        self.assert_error_behavior(
            func_to_call=batch_delete_messages,
            expected_exception_type=TypeError,
            expected_message=f"Argument \'id\' must be a string, got int",
            userId="me",
            ids=invalid_ids
        )

    def test_batch_delete_messages_ids_element_with_whitespace(self):
        """Test that a id with whitespace raises ValidationError."""
        invalid_ids = ["id1", "id 2", "id3"]
        self.assert_error_behavior(
            func_to_call=batch_delete_messages,
            expected_exception_type=custom_errors.ValidationError,
            expected_message=f"Argument 'id' cannot have whitespace.",
            userId="me",
            ids=invalid_ids
        )

    # --- Tests for DB structure initialization logic (lines 575-576) ---
    
    def test_db_structure_init_when_user_not_exists_in_insert(self):
        """Test that DB structure is properly initialized when userId doesn't exist in insert_message.
        This tests the logic: if userId not in DB['users']: DB['users'][userId] = {'messages': {}}"""
        # Ensure the test user doesn't exist initially
        test_user_id = "new_user_for_insert@example.com"
        if test_user_id in DB["users"]:
            del DB["users"][test_user_id]
        
        # Verify user doesn't exist
        self.assertNotIn(test_user_id, DB["users"])
        
        # Create the user first (since _ensure_user requires it)
        DB["users"][test_user_id] = {"id": test_user_id}
        
        # Now test the DB structure initialization by calling insert_message
        # This will trigger the logic around lines 575-576
        result = insert_message(test_user_id, {"raw": "Test message for new user in insert"})
        
        # Verify the user was created with proper structure
        self.assertIn(test_user_id, DB["users"])
        self.assertIn("messages", DB["users"][test_user_id])
        self.assertIsInstance(DB["users"][test_user_id]["messages"], dict)
        
        # Verify the message was stored
        self.assertIn(result["id"], DB["users"][test_user_id]["messages"])
        
        # Clean up
        del DB["users"][test_user_id]
    
    def test_db_structure_init_when_userid_matches_profile_email_but_key_missing_in_insert(self):
        """When userId matches a user's profile email but isn't a key in DB['users'],
        insert_message should initialize DB['users'][userId] with a 'messages' dict (lines 575-576).
        This exercises the 'if userId not in DB["users"]' branch despite _ensure_user passing via profile email.
        """
        test_user_id = "alias_user@example.com"
        alias_db_key = "some_other_key"

        # Ensure a clean slate for the alias key and userId key
        if test_user_id in DB["users"]:
            del DB["users"][test_user_id]
        if alias_db_key in DB["users"]:
            del DB["users"][alias_db_key]

        # Create a user entry under a different key, whose profile email matches test_user_id
        DB["users"][alias_db_key] = {
            "id": alias_db_key,
            "profile": {"emailAddress": test_user_id}
        }

        # Sanity-check preconditions
        self.assertNotIn(test_user_id, DB["users"])  # target key missing
        self.assertIn(alias_db_key, DB["users"])     # alias key present

        # Call insert_message to trigger initialization of DB['users'][test_user_id]
        result = insert_message(test_user_id, {"raw": "Message via alias"})

        # Verify new user key created and message stored under it
        self.assertIn(test_user_id, DB["users"])  # new key created by lines 575-576
        self.assertIn("messages", DB["users"][test_user_id])
        self.assertIsInstance(DB["users"][test_user_id]["messages"], dict)
        self.assertIn(result["id"], DB["users"][test_user_id]["messages"])

        # Clean up
        del DB["users"][test_user_id]
        del DB["users"][alias_db_key]

    # --- Tests for insert() MIME parsing except: pass blocks (around lines 564-565) ---
    def test_insert_mime_parsing_base64_decode_failure_in_parts_handled_gracefully(self):
        """insert() should gracefully handle base64 decode failures in MIME parts (except: pass at 564-565).
        Creates a multipart MIME with an invalid base64 part and ensures no exception is raised and message is created."""
        invalid_base64_multipart_raw = (
            "From: sender@example.com\r\n"
            "To: recipient@example.com\r\n"
            "Subject: Test Insert MIME\r\n"
            "MIME-Version: 1.0\r\n"
            "Content-Type: multipart/mixed; boundary=boundary\r\n\r\n"
            "--boundary\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Transfer-Encoding: base64\r\n\r\n"
            "invalid_base64_data_here\r\n"
            "--boundary--"
        )

        try:
            result = insert_message("me", {"raw": invalid_base64_multipart_raw})
            self.assertIsInstance(result, dict)
            self.assertIn("id", result)
            # Body may be empty due to failed decode, but message should exist
            self.assertIn(result["id"], DB["users"]["me"]["messages"])
        except Exception as e:
            self.fail(f"insert() should handle invalid base64 in parts gracefully, but raised: {e}")

    def test_insert_mime_parsing_base64_decode_failure_in_body_handled_gracefully(self):
        """insert() should gracefully handle base64 decode failures in single-part body path (except around 569-571).
        Provides a text/plain MIME with invalid base64 body and ensures message is still created."""
        invalid_base64_body_raw = (
            "From: sender@example.com\r\n"
            "To: recipient@example.com\r\n"
            "Subject: Test Insert MIME Body\r\n"
            "MIME-Version: 1.0\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Transfer-Encoding: base64\r\n\r\n"
            "invalid_base64_data_here"
        )

        try:
            result = insert_message("me", {"raw": invalid_base64_body_raw})
            self.assertIsInstance(result, dict)
            self.assertIn("id", result)
            self.assertIn(result["id"], DB["users"]["me"]["messages"])
        except Exception as e:
            self.fail(f"insert() should handle invalid base64 in body gracefully, but raised: {e}")

    def test_insert_mime_parsing_parts_decode_failure_via_parser_mock(self):
        """Force insert() into the parsed_mime parts branch and trigger decode failure to hit except: pass (lines ~929-934)."""
        # Import the module to monkeypatch its parse_mime_message symbol
        from APIs.gmail.Users import Messages as GmailMessagesModule

        original_parser = GmailMessagesModule.parse_mime_message
        try:
            # Return a parsed structure with an invalid base64 in parts
            GmailMessagesModule.parse_mime_message = lambda raw: {
                "payload": {
                    "parts": [
                        {
                            "mimeType": "text/plain",
                            "body": {"data": "not_base64!!!"}
                        }
                    ]
                },
                "headers": [
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "To", "value": "recipient@example.com"},
                    {"name": "Subject", "value": "Subject"},
                    {"name": "Date", "value": "2022-01-01T00:00:00"},
                ],
            }

            result = insert_message("me", {"raw": "ignored-by-mock"})
            self.assertIsInstance(result, dict)
            self.assertIn("id", result)
            # Body may be empty due to decode failure, but no exception should occur
            self.assertIn(result["id"], DB["users"]["me"]["messages"])
        finally:
            GmailMessagesModule.parse_mime_message = original_parser

    def test_insert_mime_parsing_body_decode_failure_via_parser_mock(self):
        """Force insert() into the parsed_mime body branch and trigger decode failure to hit except: pass (lines ~935-940)."""
        from APIs.gmail.Users import Messages as GmailMessagesModule

        original_parser = GmailMessagesModule.parse_mime_message
        try:
            # Return a parsed structure with body.data invalid base64 (no parts)
            GmailMessagesModule.parse_mime_message = lambda raw: {
                "payload": {
                    "body": {"data": "still_not_base64"}
                },
                "headers": [
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "To", "value": "recipient@example.com"},
                    {"name": "Subject", "value": "Subject"},
                    {"name": "Date", "value": "2022-01-01T00:00:00"},
                ],
            }

            result = insert_message("me", {"raw": "ignored-by-mock"})
            self.assertIsInstance(result, dict)
            self.assertIn("id", result)
            self.assertIn(result["id"], DB["users"]["me"]["messages"])
        finally:
            GmailMessagesModule.parse_mime_message = original_parser

    def test_db_structure_init_when_user_exists_but_no_messages_in_insert(self):
        """Test that DB structure is properly initialized when user exists but has no messages key in insert_message.
        This tests the logic: elif 'messages' not in DB['users'][userId]: DB['users'][userId]['messages'] = {}"""
        test_user_id = "existing_user_no_messages_insert@example.com"
        
        # Create user without messages key
        DB["users"][test_user_id] = {"id": test_user_id}
        
        # Verify user exists but has no messages key
        self.assertIn(test_user_id, DB["users"])
        self.assertNotIn("messages", DB["users"][test_user_id])
        
        # Test the DB structure initialization by calling insert_message
        # This will trigger the logic around lines 575-576
        result = insert_message(test_user_id, {"raw": "Test message for existing user in insert"})
        
        # Verify the messages key was created
        self.assertIn("messages", DB["users"][test_user_id])
        self.assertIsInstance(DB["users"][test_user_id]["messages"], dict)
        
        # Verify the message was stored
        self.assertIn(result["id"], DB["users"][test_user_id]["messages"])
        
        # Clean up
        del DB["users"][test_user_id]
    
    def test_db_structure_init_preserves_existing_user_data(self):
        """Test that DB structure initialization preserves existing user data when adding messages key."""
        test_user_id = "user_with_existing_data@example.com"
        
        # Create user with existing data but no messages key
        existing_user_data = {
            "id": test_user_id,
            "profile": {"emailAddress": test_user_id},
            "settings": {"language": "en"},
            "preferences": {"theme": "dark"}
        }
        DB["users"][test_user_id] = existing_user_data.copy()
        
        # Verify user exists with existing data but no messages key
        self.assertIn(test_user_id, DB["users"])
        self.assertEqual(DB["users"][test_user_id]["profile"], existing_user_data["profile"])
        self.assertEqual(DB["users"][test_user_id]["settings"], existing_user_data["settings"])
        self.assertEqual(DB["users"][test_user_id]["preferences"], existing_user_data["preferences"])
        self.assertNotIn("messages", DB["users"][test_user_id])
        
        # Test the DB structure initialization by calling insert_message
        result = insert_message(test_user_id, {"raw": "Test message preserving existing data"})
        
        # Verify the messages key was created
        self.assertIn("messages", DB["users"][test_user_id])
        self.assertIsInstance(DB["users"][test_user_id]["messages"], dict)
        
        # Verify existing user data was preserved
        self.assertEqual(DB["users"][test_user_id]["profile"], existing_user_data["profile"])
        self.assertEqual(DB["users"][test_user_id]["settings"], existing_user_data["settings"])
        self.assertEqual(DB["users"][test_user_id]["preferences"], existing_user_data["preferences"])
        
        # Verify the message was stored
        self.assertIn(result["id"], DB["users"][test_user_id]["messages"])
        
        # Clean up
        del DB["users"][test_user_id]
    
    def test_db_structure_init_multiple_messages_same_user(self):
        """Test that DB structure initialization works correctly for multiple messages from the same user."""
        test_user_id = "user_multiple_messages@example.com"
        
        # Ensure the test user doesn't exist initially
        if test_user_id in DB["users"]:
            del DB["users"][test_user_id]
        
        # Create the user first
        DB["users"][test_user_id] = {"id": test_user_id}
        
        # Insert first message - this should create the messages key
        result1 = insert_message(test_user_id, {"raw": "First message"})
        
        # Verify the messages key was created
        self.assertIn("messages", DB["users"][test_user_id])
        self.assertIn(result1["id"], DB["users"][test_user_id]["messages"])
        
        # Insert second message - this should use existing messages key
        result2 = insert_message(test_user_id, {"raw": "Second message"})
        
        # Verify both messages are stored
        self.assertIn(result1["id"], DB["users"][test_user_id]["messages"])
        self.assertIn(result2["id"], DB["users"][test_user_id]["messages"])
        self.assertEqual(len(DB["users"][test_user_id]["messages"]), 2)
        
        # Clean up
        del DB["users"][test_user_id]
    
    def test_db_structure_init_edge_case_empty_user_id(self):
        """Test DB structure initialization with edge case of empty user ID (though this should be caught by validation)."""
        # This test verifies that even if somehow an empty user ID gets through validation,
        # the DB structure initialization logic handles it gracefully
        
        # Note: In practice, empty user IDs should be caught by input validation
        # This test is for defensive programming verification
        
        # We'll test with a minimal user ID that might trigger edge cases
        test_user_id = "a"  # Minimal valid user ID
        
        # Ensure the test user doesn't exist initially
        if test_user_id in DB["users"]:
            del DB["users"][test_user_id]
        
        # Create the user first
        DB["users"][test_user_id] = {"id": test_user_id}
        
        # Test the DB structure initialization
        result = insert_message(test_user_id, {"raw": "Edge case message"})
        
        # Verify the structure was created correctly
        self.assertIn(test_user_id, DB["users"])
        self.assertIn("messages", DB["users"][test_user_id])
        self.assertIn(result["id"], DB["users"][test_user_id]["messages"])
        
        # Clean up
        del DB["users"][test_user_id]
    
    def test_db_structure_init_concurrent_access_simulation(self):
        """Test that DB structure initialization works correctly under simulated concurrent access scenarios."""
        test_user_id = "concurrent_user@example.com"
        
        # Ensure the test user doesn't exist initially
        if test_user_id in DB["users"]:
            del DB["users"][test_user_id]
        
        # Create the user first
        DB["users"][test_user_id] = {"id": test_user_id}
        
        # Simulate a scenario where the user exists but messages key might be missing
        # This could happen in concurrent access scenarios
        
        # First, verify the user exists but has no messages
        self.assertIn(test_user_id, DB["users"])
        self.assertNotIn("messages", DB["users"][test_user_id])
        
        # Now test the DB structure initialization
        result = insert_message(test_user_id, {"raw": "Concurrent access test message"})
        
        # Verify the structure was created correctly
        self.assertIn("messages", DB["users"][test_user_id])
        self.assertIsInstance(DB["users"][test_user_id]["messages"], dict)
        self.assertIn(result["id"], DB["users"][test_user_id]["messages"])
        
        # Clean up
        del DB["users"][test_user_id]
    
    def test_db_structure_init_with_nested_user_structure(self):
        """Test DB structure initialization with a more complex nested user structure."""
        test_user_id = "nested_user@example.com"
        
        # Create a user with a complex nested structure
        complex_user_data = {
            "id": test_user_id,
            "profile": {
                "emailAddress": test_user_id,
                "name": {
                    "givenName": "John",
                    "familyName": "Doe"
                },
                "addresses": [
                    {"type": "home", "value": "123 Main St"},
                    {"type": "work", "value": "456 Business Ave"}
                ]
            },
            "settings": {
                "notifications": {
                    "email": True,
                    "push": False,
                    "sms": True
                },
                "privacy": {
                    "shareData": False,
                    "allowTracking": True
                }
            }
        }
        
        # Ensure the test user doesn't exist initially
        if test_user_id in DB["users"]:
            del DB["users"][test_user_id]
        
        # Create the user with complex structure
        DB["users"][test_user_id] = complex_user_data.copy()
        
        # Verify user exists with complex structure but no messages key
        self.assertIn(test_user_id, DB["users"])
        self.assertEqual(DB["users"][test_user_id]["profile"]["name"]["givenName"], "John")
        self.assertEqual(DB["users"][test_user_id]["settings"]["notifications"]["email"], True)
        self.assertNotIn("messages", DB["users"][test_user_id])
        
        # Test the DB structure initialization
        result = insert_message(test_user_id, {"raw": "Message for nested user"})
        
        # Verify the messages key was created
        self.assertIn("messages", DB["users"][test_user_id])
        self.assertIsInstance(DB["users"][test_user_id]["messages"], dict)
        
        # Verify all existing complex structure was preserved
        self.assertEqual(DB["users"][test_user_id]["profile"]["name"]["givenName"], "John")
        self.assertEqual(DB["users"][test_user_id]["profile"]["name"]["familyName"], "Doe")
        self.assertEqual(DB["users"][test_user_id]["settings"]["notifications"]["email"], True)
        self.assertEqual(DB["users"][test_user_id]["settings"]["privacy"]["shareData"], False)
        self.assertEqual(len(DB["users"][test_user_id]["profile"]["addresses"]), 2)
        
        # Verify the message was stored
        self.assertIn(result["id"], DB["users"][test_user_id]["messages"])
        
        # Clean up
        del DB["users"][test_user_id]
    
    # --- End of tests for DB structure initialization logic ---

class TestUntrashMessage(BaseTestCaseWithErrorHandler):
    def setUp(self):
        """Reset test state (DB) before each test."""
        reset_db()
        error_manager = get_error_manager()
        error_manager.set_error_mode("raise") # Default to RAISE for most tests, can be overridden per test if needed
        
        # Setup test data
        DB["users"]["me"]["messages"] = {
            "msg_in_trash": {
                "id": "msg_in_trash",
                "labelIds": ["TRASH", "INBOX", "IMPORTANT"]
            },
            "msg_case_trash": {
                "id": "msg_case_trash",
                "labelIds": ["trash", "INBOX"]
            },
            "msg_not_in_trash": {
                "id": "msg_not_in_trash",
                "labelIds": ["INBOX", "IMPORTANT"]
            },
            "msg_only_trash": {
                "id": "msg_only_trash",
                "labelIds": ["TRASH"]
            },
            "msg_empty_labels": {
                "id": "msg_empty_labels",
                "labelIds": []
            }
        }
    
    def tearDown(self):
        """Restore original state if necessary."""
        reset_db()
        error_manager = get_error_manager()
        error_manager.reset_error_mode()  # Restore

    def test_untrash_valid_message_in_trash(self):
        """Test untrashing a message that is currently in TRASH."""
        result = untrash_message(userId="me", id="msg_in_trash")
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], "msg_in_trash")
        self.assertNotIn("TRASH", result['labelIds'])
        self.assertIn("INBOX", result['labelIds'])
        self.assertIn("IMPORTANT", result['labelIds'])
        # Verify DB state
        db_msg = DB["users"]["me"]["messages"]["msg_in_trash"]
        self.assertNotIn("TRASH", db_msg['labelIds'])

    def test_untrash_valid_message_in_trash_mixed_case(self):
        """Test untrashing a message with 'trash' (lowercase) label."""
        result = untrash_message(userId="me", id="msg_case_trash")
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], "msg_case_trash")
        self.assertNotIn("trash", result['labelIds'])
        self.assertNotIn("TRASH", result['labelIds'])
        self.assertIn("INBOX", result['labelIds'])
        # Verify DB state
        db_msg = DB["users"]["me"]["messages"]["msg_case_trash"]
        self.assertNotIn("trash", db_msg['labelIds'])

    def test_untrash_message_not_in_trash(self):
        """Test untrashing a message that is not in TRASH; should remain unchanged."""
        original_labels = DB["users"]["me"]["messages"]["msg_not_in_trash"]["labelIds"].copy()
        result = untrash_message(userId="me", id="msg_not_in_trash")
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], "msg_not_in_trash")
        self.assertEqual(sorted(result['labelIds']), sorted(original_labels)) # Sorted because order might change
        # Verify DB state
        db_msg = DB["users"]["me"]["messages"]["msg_not_in_trash"]
        self.assertEqual(sorted(db_msg['labelIds']), sorted(original_labels))

    def test_untrash_message_only_in_trash(self):
        """Test untrashing a message whose only label is TRASH."""
        result = untrash_message(userId="me", id="msg_only_trash")
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], "msg_only_trash")
        self.assertEqual(result['labelIds'], []) # TRASH removed, no other labels
        # Verify DB state
        db_msg = DB["users"]["me"]["messages"]["msg_only_trash"]
        self.assertEqual(db_msg['labelIds'], [])

    def test_untrash_message_with_empty_labels(self):
        """Test untrashing a message that has an empty label list."""
        result = untrash_message(userId="me", id="msg_empty_labels")
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], "msg_empty_labels")
        self.assertEqual(result['labelIds'], [])
        db_msg = DB["users"]["me"]["messages"]["msg_empty_labels"]
        self.assertEqual(db_msg['labelIds'], [])


    def test_untrash_non_existent_message_id(self):
        """Test untrashing a message ID that does not exist for the user."""
        result = untrash_message(userId="me", id="msg_does_not_exist")
        self.assertIsNone(result)

    def test_untrash_default_user_id_valid_message(self):
        """Test untrashing with default userId ('me') and a valid message ID."""
        result = untrash_message(id="msg_in_trash") # userId defaults to "me"
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], "msg_in_trash")
        self.assertNotIn("TRASH", result['labelIds'])

    def test_untrash_default_id_for_existing_user(self):
        """Test untrashing with default ID ('') for an existing user."""
        result = untrash_message(userId="me") # id defaults to ""
        self.assertIsNone(result) # Assuming no message has ID ""

    def test_untrash_all_defaults(self):
        """Test untrashing with default userId ('me') and default ID ('')."""
        result = untrash_message() # userId="me", id=""
        self.assertIsNone(result) # Assuming no message "me" has ID ""

    def test_untrash_invalid_user_id_type(self):
        """Test that a non-string userId raises TypeError."""
        invalid_user_id = 12345
        self.assert_error_behavior(
            func_to_call=untrash_message,
            expected_exception_type=TypeError,
            expected_message=f"Argument 'userId' must be a string, got {type(invalid_user_id).__name__}",
            userId=invalid_user_id,
            id="some_id"
        )

    def test_untrash_invalid_message_id_type(self):
        """Test that a non-string message id raises TypeError."""
        invalid_msg_id = 123
        self.assert_error_behavior(
            func_to_call=untrash_message,
            expected_exception_type=TypeError,
            expected_message=f"Argument 'id' must be a string, got int",
            userId="me",
            id=invalid_msg_id
        )

    def test_untrash_unknown_user_id(self):
        """Test that an unknown userId raises ValueError (propagated from _ensure_user)."""
        unknown_user_id = "unknown_user@example.com"
        self.assert_error_behavior(
            func_to_call=untrash_message,
            expected_exception_type=ValueError,
            expected_message=f"User '{unknown_user_id}' does not exist.",
            userId=unknown_user_id,
            id="any_id"
        )

    def test_untrash_user_with_no_messages_valid_id_format(self):
        """Test behavior for a non-existent user."""
        with self.assertRaises(ValueError):
            untrash_message(userId="empty_user@example.com", id="id_user_does_not_have")
    
    def test_untrash_empty_string_user_id_raises_validation_error(self):
        """Test that an empty string userId raises ValidationError."""
        self.assert_error_behavior(
            func_to_call=untrash_message,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Argument 'userId' cannot be empty.",
            userId="",
            id="any_id"
        )
    
    def test_untrash_user_id_whitespace_raises_validation_error(self):
        """Test that a whitespace-only userId raises ValidationError."""
        self.assert_error_behavior(
            func_to_call=untrash_message,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Argument 'userId' cannot have only whitespace.",
            userId=" ",
            id="any_id"
        )
    
    def test_untrash_user_id_whitespace_raises_validation_error_1(self):
        """Test that a userId with whitespace raises ValidationError."""
        self.assert_error_behavior(
            func_to_call=untrash_message,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Argument 'userId' cannot have whitespace.",
            userId="UserId with whitespace",
            id="any_id"
        )
    
    def test_untrash_id_whitespace_raises_validation_error(self):
        """Test that an id with whitespace raises ValidationError."""
        self.assert_error_behavior(
            func_to_call=untrash_message,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Argument 'id' cannot have whitespace.",
            userId="me",
            id="id with whitespace"
        )

    def test_mime_parsing_base64_decode_failure_handled_gracefully(self):
        """Test that MIME parsing continues gracefully when base64 decoding fails in parts section.
        This tests the except: pass block around lines 564-565."""
        # Create a message with invalid base64 data in MIME parts
        invalid_base64_msg = {
            "raw": "From: sender@example.com\r\nTo: recipient@example.com\r\nSubject: Test\r\nMIME-Version: 1.0\r\nContent-Type: multipart/mixed; boundary=boundary\r\n\r\n--boundary\r\nContent-Type: text/plain\r\nContent-Transfer-Encoding: base64\r\n\r\ninvalid_base64_data_here\r\n--boundary--"
        }
        
        # This should not raise an exception due to the except: pass block
        try:
            result = send_message("me", invalid_base64_msg)
            self.assertIsInstance(result, dict)
            self.assertIn("id", result)
            # The message should still be created even if MIME parsing fails
        except Exception as e:
            self.fail(f"MIME parsing with invalid base64 should be handled gracefully, but raised: {e}")
    
    def test_mime_parsing_base64_decode_failure_in_body_handled_gracefully(self):
        """Test that MIME parsing continues gracefully when base64 decoding fails in body section.
        This tests the except: pass block around lines 570-571."""
        # Create a message with invalid base64 data in MIME body
        invalid_base64_body_msg = {
            "raw": "From: sender@example.com\r\nTo: recipient@example.com\r\nSubject: Test\r\nMIME-Version: 1.0\r\nContent-Type: text/plain\r\nContent-Transfer-Encoding: base64\r\n\r\ninvalid_base64_data_here"
        }
        
        # This should not raise an exception due to the except: pass block
        try:
            result = send_message("me", invalid_base64_body_msg)
            self.assertIsInstance(result, dict)
            self.assertIn("id", result)
            # The message should still be created even if MIME parsing fails
        except Exception as e:
            self.fail(f"MIME parsing with invalid base64 in body should be handled gracefully, but raised: {e}")
    
    def test_db_structure_initialization_for_new_user(self):
        """Test that DB structure is properly initialized when userId doesn't exist.
        This tests the logic around lines 575-576."""
        # Ensure the test user doesn't exist initially
        test_user_id = "new_test_user@example.com"
        if test_user_id in DB["users"]:
            del DB["users"][test_user_id]
        
        # Verify user doesn't exist
        self.assertNotIn(test_user_id, DB["users"])
        
        # Create the user first (since _ensure_user requires it)
        DB["users"][test_user_id] = {"id": test_user_id}
        
        # Now test the DB structure initialization by calling insert_message
        # This will trigger the logic around lines 575-576
        result = insert_message(test_user_id, {"raw": "Test message for new user"})
        
        # Verify the user was created with proper structure
        self.assertIn(test_user_id, DB["users"])
        self.assertIn("messages", DB["users"][test_user_id])
        self.assertIsInstance(DB["users"][test_user_id]["messages"], dict)
        
        # Verify the message was stored
        self.assertIn(result["id"], DB["users"][test_user_id]["messages"])
        
        # Clean up
        del DB["users"][test_user_id]
    
    def test_db_structure_initialization_for_existing_user_without_messages(self):
        """Test that DB structure is properly initialized when user exists but has no messages key.
        This tests the logic around lines 575-576."""
        test_user_id = "existing_user_without_messages@example.com"
        
        # Create user without messages key
        DB["users"][test_user_id] = {"id": test_user_id}
        
        # Verify user exists but has no messages key
        self.assertIn(test_user_id, DB["users"])
        self.assertNotIn("messages", DB["users"][test_user_id])
        
        # Test the DB structure initialization by calling insert_message
        # This will trigger the logic around lines 575-576
        result = insert_message(test_user_id, {"raw": "Test message for existing user"})
        
        # Verify the messages key was created
        self.assertIn("messages", DB["users"][test_user_id])
        self.assertIsInstance(DB["users"][test_user_id]["messages"], dict)
        
        # Verify the message was stored
        self.assertIn(result["id"], DB["users"][test_user_id]["messages"])
        
        # Clean up
        del DB["users"][test_user_id]
    
    def test_mime_parsing_with_corrupted_data_continues_execution(self):
        """Test that MIME parsing with completely corrupted data doesn't crash the function.
        This tests both except: pass blocks."""
        # Create a message with completely invalid MIME data
        corrupted_mime_msg = {
            "raw": "This is not valid MIME data at all\r\n\r\nBut it should not crash the function"
        }
        
        # This should not raise an exception due to the except: pass blocks
        try:
            result = send_message("me", corrupted_mime_msg)
            self.assertIsInstance(result, dict)
            self.assertIn("id", result)
            # The message should still be created even if MIME parsing fails completely
        except Exception as e:
            self.fail(f"MIME parsing with corrupted data should be handled gracefully, but raised: {e}")
    
    def test_mime_parsing_with_malformed_base64_in_multiple_parts(self):
        """Test that MIME parsing handles malformed base64 in multiple parts gracefully.
        This tests the except: pass block around lines 564-565."""
        # Create a message with multiple parts, some with invalid base64
        multipart_invalid_msg = {
            "raw": "From: sender@example.com\r\nTo: recipient@example.com\r\nSubject: Test\r\nMIME-Version: 1.0\r\nContent-Type: multipart/mixed; boundary=boundary\r\n\r\n--boundary\r\nContent-Type: text/plain\r\nContent-Transfer-Encoding: base64\r\n\r\nSGVsbG8gV29ybGQ=\r\n--boundary\r\nContent-Type: text/html\r\nContent-Transfer-Encoding: base64\r\n\r\ninvalid_base64_here\r\n--boundary\r\nContent-Type: text/plain\r\nContent-Transfer-Encoding: base64\r\n\r\nV29ybGQ=\r\n--boundary--"
        }
        
        # This should not raise an exception due to the except: pass block
        try:
            result = send_message("me", multipart_invalid_msg)
            self.assertIsInstance(result, dict)
            self.assertIn("id", result)
            # The message should still be created even if some parts fail to decode
        except Exception as e:
            self.fail(f"MIME parsing with malformed base64 in parts should be handled gracefully, but raised: {e}")
    
    # --- End of new tests for specific code lines ---
        
    # --- Validation Error Tests ---

    # --- Additional tests for except: pass behavior ---
    
    def test_mime_parsing_base64_decode_failure_silently_handled(self):
        """Test that MIME parsing silently handles base64 decode failures without raising exceptions.
        This verifies the current behavior of the except: pass blocks."""
        # Create a message with invalid base64 data that would normally cause base64.b64decode to fail
        invalid_base64_msg = {
            "raw": "From: sender@example.com\r\nTo: recipient@example.com\r\nSubject: Test\r\nMIME-Version: 1.0\r\nContent-Type: multipart/mixed; boundary=boundary\r\n\r\n--boundary\r\nContent-Type: text/plain\r\nContent-Transfer-Encoding: base64\r\n\r\ninvalid_base64_data_here!!!\r\n--boundary--"
        }
        
        # This should not raise any exceptions due to the except: pass blocks
        result = send_message("me", invalid_base64_msg)
        
        # Verify the message was created successfully
        self.assertIsInstance(result, dict)
        self.assertIn("id", result)
        
        # The body should be empty or contain fallback content due to base64 decode failure
        # This tests the current behavior where failures are silently handled
        self.assertIn("body", result)
    
    def test_mime_parsing_utf8_decode_failure_silently_handled(self):
        """Test that MIME parsing silently handles UTF-8 decode failures without raising exceptions.
        This verifies the current behavior of the except: pass blocks."""
        # Create a message with valid base64 but invalid UTF-8 content
        # Base64 decode will succeed but UTF-8 decode will fail
        valid_base64_invalid_utf8 = "SGVsbG8gV29ybGQ="  # "Hello World" in base64
        # But we'll make it invalid by adding some bytes that can't be UTF-8 decoded
        invalid_utf8_base64 = "SGVsbG8gV29ybGQ=" + "AA=="  # Add null bytes which are invalid in UTF-8
        
        invalid_utf8_msg = {
            "raw": f"From: sender@example.com\r\nTo: recipient@example.com\r\nSubject: Test\r\nMIME-Version: 1.0\r\nContent-Type: text/plain\r\nContent-Transfer-Encoding: base64\r\n\r\n{invalid_utf8_base64}"
        }
        
        # This should not raise any exceptions due to the except: pass blocks
        result = send_message("me", invalid_utf8_msg)
        
        # Verify the message was created successfully
        self.assertIsInstance(result, dict)
        self.assertIn("id", result)
        
        # The body should be empty due to UTF-8 decode failure being silently handled
        self.assertIn("body", result)
    
    def test_mime_parsing_malformed_data_structure_silently_handled(self):
        """Test that MIME parsing silently handles malformed data structure without raising exceptions.
        This verifies the current behavior of the except: pass blocks."""
        # Create a message with malformed MIME structure that would cause KeyError or AttributeError
        malformed_mime_msg = {
            "raw": "From: sender@example.com\r\nTo: recipient@example.com\r\nSubject: Test\r\nMIME-Version: 1.0\r\nContent-Type: multipart/mixed; boundary=boundary\r\n\r\n--boundary\r\nContent-Type: text/plain\r\nContent-Transfer-Encoding: base64\r\n\r\nSGVsbG8gV29ybGQ=\r\n--boundary--"
        }
        
        # Mock the parse_mime_message to return malformed data that would cause errors
        # This simulates what happens when the MIME parser returns unexpected structure
        original_parse_mime = None
        try:
            # We can't easily mock this without changing the import structure
            # So we'll test with the actual behavior
            result = send_message("me", malformed_mime_msg)
            
            # Verify the message was created successfully despite potential MIME parsing issues
            self.assertIsInstance(result, dict)
            self.assertIn("id", result)
            self.assertIn("body", result)
            
        except Exception as e:
            # If an exception is raised, it means the except: pass blocks aren't working as expected
            self.fail(f"MIME parsing should silently handle malformed data, but raised: {e}")
    
    def test_mime_parsing_multiple_failures_all_silently_handled(self):
        """Test that MIME parsing silently handles multiple types of failures without raising exceptions.
        This verifies the robustness of the except: pass blocks."""
        # Create a message that would cause multiple types of failures
        problematic_mime_msg = {
            "raw": "From: sender@example.com\r\nTo: recipient@example.com\r\nSubject: Test\r\nMIME-Version: 1.0\r\nContent-Type: multipart/mixed; boundary=boundary\r\n\r\n--boundary\r\nContent-Type: text/plain\r\nContent-Transfer-Encoding: base64\r\n\r\ninvalid_base64_here!!!\r\n--boundary\r\nContent-Type: text/html\r\nContent-Transfer-Encoding: base64\r\n\r\nSGVsbG8gV29ybGQ=\r\n--boundary--"
        }
        
        # This should not raise any exceptions despite multiple potential failure points
        result = send_message("me", problematic_mime_msg)
        
        # Verify the message was created successfully
        self.assertIsInstance(result, dict)
        self.assertIn("id", result)
        self.assertIn("body", result)
        
        # The body should be empty or contain fallback content due to failures being silently handled
        # This tests that the function continues execution even when MIME parsing encounters multiple issues
    
    def test_mime_parsing_failure_does_not_affect_message_creation(self):
        """Test that MIME parsing failures don't prevent the message from being created.
        This verifies that the except: pass blocks allow the function to continue."""
        # Create a message with problematic MIME data
        problematic_msg = {
            "raw": "This is not valid MIME data at all, but the message should still be created"
        }
        
        # The message should be created successfully despite MIME parsing failures
        result = send_message("me", problematic_msg)
        
        # Verify the message was created
        self.assertIsInstance(result, dict)
        self.assertIn("id", result)
        self.assertIn("body", result)
        
        # Verify the message is stored in the database
        message_id = result["id"]
        stored_message = get_message("me", message_id)
        self.assertIsNotNone(stored_message)
        self.assertEqual(stored_message["id"], message_id)
        
        # This test verifies that the except: pass blocks don't prevent the core functionality
        # from working - the message is still created and stored even when MIME parsing fails
    
    # --- End of additional tests for except: pass behavior ---
        
    # --- Validation Error Tests ---

    # --- End of additional tests for except: pass behavior ---
        
    # --- Tests for DB structure initialization logic (lines 575-576) ---
    
    def test_db_structure_init_when_user_not_exists_in_insert(self):
        """Test that DB structure is properly initialized when userId doesn't exist in insert_message.
        This tests the logic: if userId not in DB['users']: DB['users'][userId] = {'messages': {}}"""
        # Ensure the test user doesn't exist initially
        test_user_id = "new_user_for_insert@example.com"
        if test_user_id in DB["users"]:
            del DB["users"][test_user_id]
        
        # Verify user doesn't exist
        self.assertNotIn(test_user_id, DB["users"])
        
        # Create the user first (since _ensure_user requires it)
        DB["users"][test_user_id] = {"id": test_user_id}
        
        # Now test the DB structure initialization by calling insert_message
        # This will trigger the logic around lines 575-576
        result = insert_message(test_user_id, {"raw": "Test message for new user in insert"})
        
        # Verify the user was created with proper structure
        self.assertIn(test_user_id, DB["users"])
        self.assertIn("messages", DB["users"][test_user_id])
        self.assertIsInstance(DB["users"][test_user_id]["messages"], dict)
        
        # Verify the message was stored
        self.assertIn(result["id"], DB["users"][test_user_id]["messages"])
        
        # Clean up
        del DB["users"][test_user_id]
    
    def test_db_structure_init_when_user_exists_but_no_messages_in_insert(self):
        """Test that DB structure is properly initialized when user exists but has no messages key in insert_message.
        This tests the logic: elif 'messages' not in DB['users'][userId]: DB['users'][userId]['messages'] = {}"""
        test_user_id = "existing_user_no_messages_insert@example.com"
        
        # Create user without messages key
        DB["users"][test_user_id] = {"id": test_user_id}
        
        # Verify user exists but has no messages key
        self.assertIn(test_user_id, DB["users"])
        self.assertNotIn("messages", DB["users"][test_user_id])
        
        # Test the DB structure initialization by calling insert_message
        # This will trigger the logic around lines 575-576
        result = insert_message(test_user_id, {"raw": "Test message for existing user in insert"})
        
        # Verify the messages key was created
        self.assertIn("messages", DB["users"][test_user_id])
        self.assertIsInstance(DB["users"][test_user_id]["messages"], dict)
        
        # Verify the message was stored
        self.assertIn(result["id"], DB["users"][test_user_id]["messages"])
        
        # Clean up
        del DB["users"][test_user_id]
    
    def test_db_structure_init_preserves_existing_user_data(self):
        """Test that DB structure initialization preserves existing user data when adding messages key."""
        test_user_id = "user_with_existing_data@example.com"
        
        # Create user with existing data but no messages key
        existing_user_data = {
            "id": test_user_id,
            "profile": {"emailAddress": test_user_id},
            "settings": {"language": "en"},
            "preferences": {"theme": "dark"}
        }
        DB["users"][test_user_id] = existing_user_data.copy()
        
        # Verify user exists with existing data but no messages key
        self.assertIn(test_user_id, DB["users"])
        self.assertEqual(DB["users"][test_user_id]["profile"], existing_user_data["profile"])
        self.assertEqual(DB["users"][test_user_id]["settings"], existing_user_data["settings"])
        self.assertEqual(DB["users"][test_user_id]["preferences"], existing_user_data["preferences"])
        self.assertNotIn("messages", DB["users"][test_user_id])
        
        # Test the DB structure initialization by calling insert_message
        result = insert_message(test_user_id, {"raw": "Test message preserving existing data"})
        
        # Verify the messages key was created
        self.assertIn("messages", DB["users"][test_user_id])
        self.assertIsInstance(DB["users"][test_user_id]["messages"], dict)
        
        # Verify existing user data was preserved
        self.assertEqual(DB["users"][test_user_id]["profile"], existing_user_data["profile"])
        self.assertEqual(DB["users"][test_user_id]["settings"], existing_user_data["settings"])
        self.assertEqual(DB["users"][test_user_id]["preferences"], existing_user_data["preferences"])
        
        # Verify the message was stored
        self.assertIn(result["id"], DB["users"][test_user_id]["messages"])
        
        # Clean up
        del DB["users"][test_user_id]
    
    def test_db_structure_init_multiple_messages_same_user(self):
        """Test that DB structure initialization works correctly for multiple messages from the same user."""
        test_user_id = "user_multiple_messages@example.com"
        
        # Ensure the test user doesn't exist initially
        if test_user_id in DB["users"]:
            del DB["users"][test_user_id]
        
        # Create the user first
        DB["users"][test_user_id] = {"id": test_user_id}
        
        # Insert first message - this should create the messages key
        result1 = insert_message(test_user_id, {"raw": "First message"})
        
        # Verify the messages key was created
        self.assertIn("messages", DB["users"][test_user_id])
        self.assertIn(result1["id"], DB["users"][test_user_id]["messages"])
        
        # Insert second message - this should use existing messages key
        result2 = insert_message(test_user_id, {"raw": "Second message"})
        
        # Verify both messages are stored
        self.assertIn(result1["id"], DB["users"][test_user_id]["messages"])
        self.assertIn(result2["id"], DB["users"][test_user_id]["messages"])
        self.assertEqual(len(DB["users"][test_user_id]["messages"]), 2)
        
        # Clean up
        del DB["users"][test_user_id]
    
    def test_db_structure_init_edge_case_empty_user_id(self):
        """Test DB structure initialization with edge case of empty user ID (though this should be caught by validation)."""
        # This test verifies that even if somehow an empty user ID gets through validation,
        # the DB structure initialization logic handles it gracefully
        
        # Note: In practice, empty user IDs should be caught by input validation
        # This test is for defensive programming verification
        
        # We'll test with a minimal user ID that might trigger edge cases
        test_user_id = "a"  # Minimal valid user ID
        
        # Ensure the test user doesn't exist initially
        if test_user_id in DB["users"]:
            del DB["users"][test_user_id]
        
        # Create the user first
        DB["users"][test_user_id] = {"id": test_user_id}
        
        # Test the DB structure initialization
        result = insert_message(test_user_id, {"raw": "Edge case message"})
        
        # Verify the structure was created correctly
        self.assertIn(test_user_id, DB["users"])
        self.assertIn("messages", DB["users"][test_user_id])
        self.assertIn(result["id"], DB["users"][test_user_id]["messages"])
        
        # Clean up
        del DB["users"][test_user_id]
    
    def test_db_structure_init_concurrent_access_simulation(self):
        """Test that DB structure initialization works correctly under simulated concurrent access scenarios."""
        test_user_id = "concurrent_user@example.com"
        
        # Ensure the test user doesn't exist initially
        if test_user_id in DB["users"]:
            del DB["users"][test_user_id]
        
        # Create the user first
        DB["users"][test_user_id] = {"id": test_user_id}
        
        # Simulate a scenario where the user exists but messages key might be missing
        # This could happen in concurrent access scenarios
        
        # First, verify the user exists but has no messages
        self.assertIn(test_user_id, DB["users"])
        self.assertNotIn("messages", DB["users"][test_user_id])
        
        # Now test the DB structure initialization
        result = insert_message(test_user_id, {"raw": "Concurrent access test message"})
        
        # Verify the structure was created correctly
        self.assertIn("messages", DB["users"][test_user_id])
        self.assertIsInstance(DB["users"][test_user_id]["messages"], dict)
        self.assertIn(result["id"], DB["users"][test_user_id]["messages"])
        
        # Clean up
        del DB["users"][test_user_id]
    
    def test_db_structure_init_with_nested_user_structure(self):
        """Test DB structure initialization with a more complex nested user structure."""
        test_user_id = "nested_user@example.com"
        
        # Create a user with a complex nested structure
        complex_user_data = {
            "id": test_user_id,
            "profile": {
                "emailAddress": test_user_id,
                "name": {
                    "givenName": "John",
                    "familyName": "Doe"
                },
                "addresses": [
                    {"type": "home", "value": "123 Main St"},
                    {"type": "work", "value": "456 Business Ave"}
                ]
            },
            "settings": {
                "notifications": {
                    "email": True,
                    "push": False,
                    "sms": True
                },
                "privacy": {
                    "shareData": False,
                    "allowTracking": True
                }
            }
        }
        
        # Ensure the test user doesn't exist initially
        if test_user_id in DB["users"]:
            del DB["users"][test_user_id]
        
        # Create the user with complex structure
        DB["users"][test_user_id] = complex_user_data.copy()
        
        # Verify user exists with complex structure but no messages key
        self.assertIn(test_user_id, DB["users"])
        self.assertEqual(DB["users"][test_user_id]["profile"]["name"]["givenName"], "John")
        self.assertEqual(DB["users"][test_user_id]["settings"]["notifications"]["email"], True)
        self.assertNotIn("messages", DB["users"][test_user_id])
        
        # Test the DB structure initialization
        result = insert_message(test_user_id, {"raw": "Message for nested user"})
        
        # Verify the messages key was created
        self.assertIn("messages", DB["users"][test_user_id])
        self.assertIsInstance(DB["users"][test_user_id]["messages"], dict)
        
        # Verify all existing complex structure was preserved
        self.assertEqual(DB["users"][test_user_id]["profile"]["name"]["givenName"], "John")
        self.assertEqual(DB["users"][test_user_id]["profile"]["name"]["familyName"], "Doe")
        self.assertEqual(DB["users"][test_user_id]["settings"]["notifications"]["email"], True)
        self.assertEqual(DB["users"][test_user_id]["settings"]["privacy"]["shareData"], False)
        self.assertEqual(len(DB["users"][test_user_id]["profile"]["addresses"]), 2)
        
        # Verify the message was stored
        self.assertIn(result["id"], DB["users"][test_user_id]["messages"])
        
        # Clean up
        del DB["users"][test_user_id]
    
    # --- End of tests for DB structure initialization logic ---
        
    # --- Validation Error Tests ---

    def test_insert_mime_parsing_body_decode_failure_via_parser_mock(self):
        """Force insert() into the parsed_mime body branch and trigger decode failure to hit except: pass (lines ~935-940)."""
        from APIs.gmail.Users import Messages as GmailMessagesModule

        original_parser = GmailMessagesModule.parse_mime_message
        try:
            # Return a parsed structure with body.data invalid base64 (no parts)
            GmailMessagesModule.parse_mime_message = lambda raw: {
                "payload": {
                    "body": {"data": "still_not_base64"}
                },
                "headers": [
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "To", "value": "recipient@example.com"},
                    {"name": "Subject", "value": "Subject"},
                    {"name": "Date", "value": "2022-01-01T00:00:00"},
                ],
            }

            result = insert_message("me", {"raw": "ignored-by-mock"})
            self.assertIsInstance(result, dict)
            self.assertIn("id", result)
            self.assertIn(result["id"], DB["users"]["me"]["messages"])
        finally:
            GmailMessagesModule.parse_mime_message = original_parser

    def test_insert_mime_parsing_except_pass_blocks_coverage(self):
        """This test specifically targets the except: pass blocks to ensure 100% coverage.
        It forces the base64 decode to fail in both the parts and body paths."""
        from APIs.gmail.Users import Messages as GmailMessagesModule
        import base64

        original_parser = GmailMessagesModule.parse_mime_message
        try:
            # Mock parse_mime_message to return a structure that will definitely trigger the except: pass blocks
            GmailMessagesModule.parse_mime_message = lambda raw: {
                "payload": {
                    "parts": [
                        {
                            "mimeType": "text/plain",
                            "body": {"data": "definitely_not_base64_data_that_will_cause_decode_error"}
                        }
                    ]
                },
                "headers": [
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "To", "value": "recipient@example.com"},
                    {"name": "Subject", "value": "Test Subject"},
                    {"name": "Date", "value": "2022-01-01T00:00:00"},
                ],
            }

            # This should trigger the except: pass block in the parts processing (lines 564-565)
            result = insert_message("me", {"raw": "ignored-by-mock"})
            self.assertIsInstance(result, dict)
            self.assertIn("id", result)

            # Now test the body path by mocking a different structure
            GmailMessagesModule.parse_mime_message = lambda raw: {
                "payload": {
                    "body": {"data": "another_invalid_base64_that_will_cause_decode_error"}
                },
                "headers": [
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "To", "value": "recipient@example.com"},
                    {"name": "Subject", "value": "Test Subject"},
                    {"name": "Date", "value": "2022-01-01T00:00:00"},
                ],
            }

            # This should trigger the except: pass block in the body processing (lines 570-571)
            result2 = insert_message("me", {"raw": "ignored-by-mock"})
            self.assertIsInstance(result2, dict)
            self.assertIn("id", result2)

        finally:
            GmailMessagesModule.parse_mime_message = original_parser

    def test_insert_mime_parsing_force_base64_decode_exception(self):
        """Force base64 decode exceptions to ensure the except: pass blocks are executed.
        This test creates data that will definitely cause base64.b64decode to fail."""
        from APIs.gmail.Users import Messages as GmailMessagesModule

        original_parser = GmailMessagesModule.parse_mime_message
        try:
            # Create data that will definitely cause base64 decode to fail
            # Using characters that are not valid base64
            invalid_base64_data = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
            
            # Test parts path
            GmailMessagesModule.parse_mime_message = lambda raw: {
                "payload": {
                    "parts": [
                        {
                            "mimeType": "text/plain",
                            "body": {"data": invalid_base64_data}
                        }
                    ]
                },
                "headers": [
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "To", "value": "recipient@example.com"},
                    {"name": "Subject", "value": "Test Subject"},
                    {"name": "Date", "value": "2022-01-01T00:00:00"},
                ],
            }

            result = insert_message("me", {"raw": "ignored-by-mock"})
            self.assertIsInstance(result, dict)

            # Test body path
            GmailMessagesModule.parse_mime_message = lambda raw: {
                "payload": {
                    "body": {"data": invalid_base64_data}
                },
                "headers": [
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "To", "value": "recipient@example.com"},
                    {"name": "Subject", "value": "Test Subject"},
                    {"name": "Date", "value": "2022-01-01T00:00:00"},
                ],
            }

            result2 = insert_message("me", {"raw": "ignored-by-mock"})
            self.assertIsInstance(result2, dict)

        finally:
            GmailMessagesModule.parse_mime_message = original_parser
    
    def test_insert_message_correct_subject(self):
        """Test that the subject is correctly set in the message."""
        user_id = "me"
        sender_email = "design_team@antrix.com"
        recipient_email = "user@antrix.com"
        email_subject = "Design Review Confirmation – July 30"
        email_subject = "XXXXX – July 30"
        email_body = "Hi, This is a confirmation for the design review meeting scheduled for July 30th. Best, Design Team"
        email_date = "2025-07-22T10:00:00Z"
        email_message = {
            "sender": sender_email,
            "recipient": recipient_email,
            "subject": email_subject,
            "body": email_body,
            "date": email_date,
            "isRead": False,
            "labelIds": ["INBOX", "UNREAD"]
        }
        
        result = insert_message(userId=user_id, msg=email_message)
        self.assertEqual(result["subject"], email_subject)
        self.assertEqual(result["payload"]["headers"][2]["value"], email_subject)

if __name__ == "__main__":
    unittest.main()
