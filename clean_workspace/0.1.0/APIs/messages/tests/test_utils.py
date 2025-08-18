import unittest
from copy import deepcopy
import pytest
from ..SimulationEngine.utils import _list_messages, _delete_message
from ..SimulationEngine.db import DB as SIM_DB


class TestMessageUtils(unittest.TestCase):
    def setUp(self):
        SIM_DB['messages'] = {
            "msg_1": {
                "id": "msg_1",
                "recipient": {"contact_id": "contact_1", "contact_name": "John Doe"},
                "timestamp": "2024-01-01T12:00:00Z",
                "status": "sent"
            },
            "msg_2": {
                "id": "msg_2",
                "recipient": {"contact_id": "contact_2", "contact_name": "Jane Smith"},
                "timestamp": "2024-01-01T14:30:00Z",
                "status": "sent"
            }
        }
        SIM_DB['recipients'] = {
            "contact_1": {"contact_id": "contact_1", "contact_name": "John Doe"},
            "contact_2": {"contact_id": "contact_2", "contact_name": "Jane Smith"},
            # Add Contacts-shaped recipient for Penny Robinson
            "people/penny": {
                "resourceName": "people/penny",
                "names": [{"givenName": "Penny", "familyName": "Robinson"}],
                "phone": {
                    "contact_id": "contact_penny",
                    "contact_name": "Penny Robinson",
                    "contact_endpoints": [
                        {"endpoint_type": "PHONE_NUMBER", "endpoint_value": "+10123456789", "endpoint_label": "mobile"}
                    ]
                }
            }
        }
        SIM_DB['message_history'] = [
            {"id": "msg_1", "action": "sent"},
            {"id": "msg_2", "action": "sent"}
        ]

    def tearDown(self):
        # Clear the DB after each test
        SIM_DB.clear()

    # Tests for _list_messages
    def test_list_messages_no_filters(self):
        messages = _list_messages()
        self.assertEqual(len(messages), 2)

    def test_list_messages_by_recipient_id(self):
        messages = _list_messages(recipient_id="contact_1")
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["id"], "msg_1")

    def test_list_messages_by_recipient_name(self):
        messages = _list_messages(recipient_name="Jane")
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["id"], "msg_2")

    def test_list_messages_by_full_recipient_name(self):
        messages = _list_messages(recipient_name="Jane Smith")
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["id"], "msg_2")

    def test_list_messages_recipient_name_nested_contacts_shape_no_messages(self):
        # With a recipient existing in recipients DB but no messages for Penny, should not raise and return []
        messages = _list_messages(recipient_name="Penny Robinson")
        self.assertIsInstance(messages, list)
        self.assertEqual(len(messages), 0)

    def test_list_messages_by_status(self):
        SIM_DB["messages"]["msg_1"]["status"] = "sent"
        messages = _list_messages(status="sent")
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["id"], "msg_1")

    def test_list_messages_by_date_range(self):
        messages = _list_messages(start_date="2024-01-01T13:00:00Z", end_date="2024-01-01T15:00:00Z")
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["id"], "msg_2")

    def test_list_messages_all_filters(self):
        messages = _list_messages(
            recipient_id="contact_2",
            recipient_name="Smith",
            status="sent",
            start_date="2024-01-01T14:00:00Z"
        )
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["id"], "msg_2")
        
    def test_list_messages_no_results(self):
        with pytest.raises(ValueError, match="Recipient with name containing 'No One' not found."):
            _list_messages(recipient_name="No One")

    def test_list_messages_invalid_date_format(self):
        with self.assertRaises(ValueError):
            _list_messages(start_date="invalid-date")

    def test_list_messages_invalid_recipient_id_type(self):
        with self.assertRaises(TypeError):
            _list_messages(recipient_id=123)

    def test_list_messages_invalid_status(self):
        with pytest.raises(ValueError, match="Invalid status 'archived'"):
            _list_messages(status="archived")

    def test_list_messages_non_existent_recipient_id(self):
        with pytest.raises(ValueError, match="Recipient with id 'contact_99' not found."):
            _list_messages(recipient_id="contact_99")
            
    def test_list_messages_non_existent_recipient_name(self):
        with pytest.raises(ValueError, match="Recipient with name containing 'NotARealName' not found."):
            _list_messages(recipient_name="NotARealName")

    # Tests for _delete_message
    def test_delete_message_success(self):
        self.assertIn("msg_1", SIM_DB["messages"])
        result = _delete_message("msg_1")
        self.assertTrue(result)
        self.assertNotIn("msg_1", SIM_DB["messages"])
        
        history_ids = [item.get("id") for item in SIM_DB["message_history"]]
        self.assertNotIn("msg_1", history_ids)

    def test_delete_message_not_found(self):
        with pytest.raises(ValueError, match="Message with id 'msg_999' not found."):
            _delete_message("msg_999")

    def test_delete_message_invalid_id_type(self):
        with self.assertRaises(TypeError):
            _delete_message(123)
            
    def test_delete_message_empty_id(self):
        with self.assertRaises(ValueError):
            _delete_message("")

if __name__ == '__main__':
    unittest.main() 