import unittest
import copy
import base64
import time
from datetime import datetime, timezone
from ..SimulationEngine import custom_errors
from .. import update_ticket, create_ticket
from ..SimulationEngine.db import DB
from common_utils.base_case import BaseTestCaseWithErrorHandler
from pydantic import ValidationError as PydanticValidationError


class TestUpdateTicket(BaseTestCaseWithErrorHandler):

    def setUp(self):
        self._original_DB_state = copy.deepcopy(DB)
        DB.clear()

        DB['users'] = {
            '1': {'id': 1, 'name': 'Alice User', 'email': 'alice@example.com', 'active': True, 'role': 'end-user', 'created_at': self._now_iso(), 'updated_at': self._now_iso()},
            '2': {'id': 2, 'name': 'Bob Agent', 'email': 'bob.agent@example.com', 'active': True, 'role': 'agent', 'created_at': self._now_iso(), 'updated_at': self._now_iso()},
            '3': {'id': 3, 'name': 'Charlie Assignee', 'email': 'charlie.assignee@example.com', 'active': True, 'role': 'agent', 'created_at': self._now_iso(), 'updated_at': self._now_iso()},
            '4': {'id': 4, 'name': 'David Collaborator', 'email': 'david.collab@example.com', 'active': True, 'role': 'end-user', 'created_at': self._now_iso(), 'updated_at': self._now_iso()},
            '5': {'id': 5, 'name': 'Eve Submitter', 'email': 'eve.submitter@example.com', 'active': True, 'role': 'agent', 'created_at': self._now_iso(), 'updated_at': self._now_iso()},
        }
        DB['organizations'] = {
            '101': {'id': 101, 'name': 'Org Alpha', 'created_at': self._now_iso(), 'updated_at': self._now_iso()},
        }
        DB['tickets'] = {} 
        DB['next_ticket_id'] = 1
        DB['next_user_id'] = 100 
        DB['next_audit_id'] = 1
        DB['next_comment_id'] = 1 

    def tearDown(self):
        DB.clear()
        DB.update(self._original_DB_state)

    def _now_iso(self):
        return datetime.now(timezone.utc).isoformat()

    def _is_iso_datetime_string(self, date_string):
        if not isinstance(date_string, str):
            return False
        try:
            # Handle 'Z' for UTC
            if date_string.endswith('Z'):
                datetime.fromisoformat(date_string[:-1] + '+00:00')
            else:
                datetime.fromisoformat(date_string)
            return True
        except ValueError:
            return False

    def _verify_new_output_fields(self, ticket):
        """Helper method to verify the four new output fields are present and valid."""
        ticket_id = ticket['id']
        
        # Verify encoded_id
        self.assertIn('encoded_id', ticket)
        expected_encoded_id = base64.b64encode(str(ticket_id).encode()).decode('utf-8')
        self.assertEqual(ticket['encoded_id'], expected_encoded_id)
        
        # Verify followup_ids
        self.assertIn('followup_ids', ticket)
        self.assertIsInstance(ticket['followup_ids'], list)
        
        # Verify generated_timestamp
        self.assertIn('generated_timestamp', ticket)
        self.assertIsInstance(ticket['generated_timestamp'], int)
        self.assertGreater(ticket['generated_timestamp'], 0)
        
        # Verify url
        self.assertIn('url', ticket)
        expected_url = f"https://zendesk.com/agent/tickets/{ticket_id}"
        self.assertEqual(ticket['url'], expected_url)

    def _create_test_ticket(self, ticket_id=1):
        """Helper method to create a test ticket for update operations."""
        payload = {
            'ticket': {
                'requester_id': 1,
                'comment': {'body': 'Original test ticket body.'},
                'subject': 'Original Test Ticket',
                'priority': 'normal',
                'status': 'new',
                'type': 'question'
            }
        }
        response = create_ticket(payload['ticket'])
        return response['ticket']

    def test_update_ticket_subject_only_success(self):
        ticket = self._create_test_ticket()
        ticket_id = ticket['id']
        
        response = update_ticket(ticket_id, {"subject": "Updated Subject"})
        
        self.assertIsInstance(response, dict)
        self.assertIn('success', response)
        self.assertIn('ticket', response)
        self.assertTrue(response['success'])
        
        updated_ticket = response['ticket']
        self.assertEqual(updated_ticket['subject'], "Updated Subject")
        self.assertEqual(updated_ticket['id'], ticket_id)
        self.assertTrue(self._is_iso_datetime_string(updated_ticket['updated_at']))
        
        # Verify new output fields
        self._verify_new_output_fields(updated_ticket)

    def test_update_ticket_comment_body_only_success(self):
        ticket = self._create_test_ticket()
        ticket_id = ticket['id']
        
        response = update_ticket(ticket_id, {"comment_body": "Updated comment body"})
        
        self.assertIsInstance(response, dict)
        self.assertTrue(response['success'])
        
        updated_ticket = response['ticket']
        self.assertEqual(updated_ticket['comment']['body'], "Updated comment body")
        self.assertEqual(updated_ticket['id'], ticket_id)
        
        # Verify new output fields
        self._verify_new_output_fields(updated_ticket)

    def test_update_ticket_priority_only_success(self):
        ticket = self._create_test_ticket()
        ticket_id = ticket['id']
        
        response = update_ticket(ticket_id, {"priority": "high"})
        
        self.assertIsInstance(response, dict)
        self.assertTrue(response['success'])
        
        updated_ticket = response['ticket']
        self.assertEqual(updated_ticket['priority'], "high")
        self.assertEqual(updated_ticket['id'], ticket_id)
        
        # Verify new output fields
        self._verify_new_output_fields(updated_ticket)

    def test_update_ticket_type_only_success(self):
        ticket = self._create_test_ticket()
        ticket_id = ticket['id']
        
        response = update_ticket(ticket_id, {"ticket_type": "incident"})
        
        self.assertIsInstance(response, dict)
        self.assertTrue(response['success'])
        
        updated_ticket = response['ticket']
        self.assertEqual(updated_ticket['type'], "incident")
        self.assertEqual(updated_ticket['id'], ticket_id)
        
        # Verify new output fields
        self._verify_new_output_fields(updated_ticket)

    def test_update_ticket_status_only_success(self):
        ticket = self._create_test_ticket()
        ticket_id = ticket['id']
        
        response = update_ticket(ticket_id, {"status": "open"})
        
        self.assertIsInstance(response, dict)
        self.assertTrue(response['success'])
        
        updated_ticket = response['ticket']
        self.assertEqual(updated_ticket['status'], "open")
        self.assertEqual(updated_ticket['id'], ticket_id)
        
        # Verify new output fields
        self._verify_new_output_fields(updated_ticket)

    def test_update_ticket_all_fields_success(self):
        ticket = self._create_test_ticket()
        ticket_id = ticket['id']
        
        response = update_ticket(
            ticket_id,
            {
                "subject": "Fully Updated Subject",
                "comment_body": "Fully updated comment body",
                "priority": "urgent",
                "ticket_type": "task",
                "status": "closed"
            }
        )
        
        self.assertIsInstance(response, dict)
        self.assertTrue(response['success'])
        
        updated_ticket = response['ticket']
        self.assertEqual(updated_ticket['subject'], "Fully Updated Subject")
        self.assertEqual(updated_ticket['comment']['body'], "Fully updated comment body")
        self.assertEqual(updated_ticket['priority'], "urgent")
        self.assertEqual(updated_ticket['type'], "task")
        self.assertEqual(updated_ticket['status'], "closed")
        self.assertEqual(updated_ticket['id'], ticket_id)
        
        # Verify new output fields
        self._verify_new_output_fields(updated_ticket)

    def test_update_ticket_partial_fields_success(self):
        ticket = self._create_test_ticket()
        ticket_id = ticket['id']
        
        response = update_ticket(
            ticket_id,
            {
                "subject": "Partially Updated Subject",
                "priority": "low",
                "status": "pending"
            }
        )
        
        self.assertIsInstance(response, dict)
        self.assertTrue(response['success'])
        
        updated_ticket = response['ticket']
        self.assertEqual(updated_ticket['subject'], "Partially Updated Subject")
        self.assertEqual(updated_ticket['priority'], "low")
        self.assertEqual(updated_ticket['status'], "pending")
        self.assertEqual(updated_ticket['id'], ticket_id)
        
        # Verify new output fields
        self._verify_new_output_fields(updated_ticket)

    def test_update_ticket_no_changes_success(self):
        ticket = self._create_test_ticket()
        ticket_id = ticket['id']
        original_updated_at = ticket['updated_at']
        
        response = update_ticket(ticket_id, {})
        
        self.assertIsInstance(response, dict)
        self.assertTrue(response['success'])
        
        updated_ticket = response['ticket']
        self.assertEqual(updated_ticket['id'], ticket_id)
        # The updated_at timestamp should still be updated even if no fields are changed
        self.assertNotEqual(updated_ticket['updated_at'], original_updated_at)
        
        # Verify new output fields
        self._verify_new_output_fields(updated_ticket)

    def test_update_ticket_multiple_sequential_updates_success(self):
        ticket = self._create_test_ticket()
        ticket_id = ticket['id']
        
        # First update
        response1 = update_ticket(ticket_id, {"subject": "First Update"})
        self.assertTrue(response1['success'])
        self.assertEqual(response1['ticket']['subject'], "First Update")
        
        # Second update
        response2 = update_ticket(ticket_id, {"priority": "high"})
        self.assertTrue(response2['success'])
        self.assertEqual(response2['ticket']['subject'], "First Update")
        self.assertEqual(response2['ticket']['priority'], "high")
        
        # Third update
        response3 = update_ticket(ticket_id, {"status": "solved"})
        self.assertTrue(response3['success'])
        self.assertEqual(response3['ticket']['subject'], "First Update")
        self.assertEqual(response3['ticket']['priority'], "high")
        self.assertEqual(response3['ticket']['status'], "solved")
        
        # Verify new output fields
        self._verify_new_output_fields(response3['ticket'])

    def test_update_ticket_return_type_and_structure_success(self):
        ticket = self._create_test_ticket()
        ticket_id = ticket['id']
        
        response = update_ticket(ticket_id, {"subject": "Structure Test"})
        
        self.assertIsInstance(response, dict)
        self.assertIn('success', response)
        self.assertIn('ticket', response)
        self.assertTrue(response['success'])
        
        updated_ticket = response['ticket']
        self.assertIsInstance(updated_ticket, dict)
        self.assertIn('id', updated_ticket)
        self.assertIn('subject', updated_ticket)
        self.assertIn('created_at', updated_ticket)
        self.assertIn('updated_at', updated_ticket)
        
        # Verify new output fields structure
        self.assertIn('encoded_id', updated_ticket)
        self.assertIn('followup_ids', updated_ticket)
        self.assertIn('generated_timestamp', updated_ticket)
        self.assertIn('url', updated_ticket)

    def test_update_ticket_different_priorities_success(self):
        valid_priorities = ['urgent', 'high', 'normal', 'low']
        
        for priority in valid_priorities:
            with self.subTest(priority=priority):
                ticket = self._create_test_ticket()
                ticket_id = ticket['id']
                
                response = update_ticket(ticket_id, {"priority": priority})
                
                self.assertTrue(response['success'])
                self.assertEqual(response['ticket']['priority'], priority)
                
                # Verify new output fields
                self._verify_new_output_fields(response['ticket'])

    def test_update_ticket_different_statuses_success(self):
        valid_statuses = ['new', 'open', 'pending', 'hold', 'solved', 'closed']
        
        for status in valid_statuses:
            with self.subTest(status=status):
                ticket = self._create_test_ticket()
                ticket_id = ticket['id']
                
                response = update_ticket(ticket_id, {"status": status})
                
                self.assertTrue(response['success'])
                self.assertEqual(response['ticket']['status'], status)
                
                # Verify new output fields
                self._verify_new_output_fields(response['ticket'])

    def test_update_ticket_different_types_success(self):
        valid_types = ['problem', 'incident', 'question', 'task']
        
        for ticket_type in valid_types:
            with self.subTest(ticket_type=ticket_type):
                ticket = self._create_test_ticket()
                ticket_id = ticket['id']
                
                response = update_ticket(ticket_id, {"ticket_type": ticket_type})
                
                self.assertTrue(response['success'])
                self.assertEqual(response['ticket']['type'], ticket_type)
                
                # Verify new output fields
                self._verify_new_output_fields(response['ticket'])

    def test_update_ticket_database_consistency_success(self):
        ticket = self._create_test_ticket()
        ticket_id = ticket['id']
        
        response = update_ticket(ticket_id, {"subject": "Database Consistency Test"})
        
        self.assertTrue(response['success'])
        
        # Verify database is updated
        db_ticket = DB['tickets'][str(ticket_id)]
        self.assertEqual(db_ticket['subject'], "Database Consistency Test")
        self.assertEqual(db_ticket['id'], ticket_id)
        
        # Verify response matches database
        self.assertEqual(response['ticket'], db_ticket)

    def test_update_ticket_encoded_id_validation_success(self):
        ticket = self._create_test_ticket()
        ticket_id = ticket['id']
        
        response = update_ticket(ticket_id, {"subject": "Encoded ID Test"})
        
        updated_ticket = response['ticket']
        expected_encoded_id = base64.b64encode(str(ticket_id).encode()).decode('utf-8')
        
        self.assertEqual(updated_ticket['encoded_id'], expected_encoded_id)
        
        # Verify decoding works
        decoded_id = base64.b64decode(updated_ticket['encoded_id'].encode()).decode('utf-8')
        self.assertEqual(int(decoded_id), ticket_id)

    def test_update_ticket_followup_ids_empty_success(self):
        ticket = self._create_test_ticket()
        ticket_id = ticket['id']
        
        response = update_ticket(ticket_id, {"subject": "Followup IDs Test"})
        
        updated_ticket = response['ticket']
        self.assertEqual(updated_ticket['followup_ids'], [])
        self.assertIsInstance(updated_ticket['followup_ids'], list)

    def test_update_ticket_timestamp_validation_success(self):
        ticket = self._create_test_ticket()
        ticket_id = ticket['id']
        
        before_update = int(time.time() * 1000)
        response = update_ticket(ticket_id, {"subject": "Timestamp Test"})
        after_update = int(time.time() * 1000)
        
        updated_ticket = response['ticket']
        generated_timestamp = updated_ticket['generated_timestamp']
        
        # Allow small timing differences (within 5 milliseconds)
        self.assertLessEqual(abs(generated_timestamp - before_update), 5)
        self.assertLessEqual(generated_timestamp, after_update)

    def test_update_ticket_url_format_validation_success(self):
        ticket = self._create_test_ticket()
        ticket_id = ticket['id']
        
        response = update_ticket(ticket_id, {"subject": "URL Format Test"})
        
        updated_ticket = response['ticket']
        expected_url = f"https://zendesk.com/agent/tickets/{ticket_id}"
        
        self.assertEqual(updated_ticket['url'], expected_url)
        self.assertTrue(updated_ticket['url'].startswith('https://'))

    def test_update_ticket_with_default_database_success(self):
        # Load the default database
        from ..SimulationEngine.db import DB
        import os
        import json
        
        # Create a temporary backup of current state
        current_state = copy.deepcopy(DB)
        
        try:
            # Load default database
            default_db_path = os.path.join(os.path.dirname(__file__), '..', 'DBs', 'ZendeskDefaultDB.json')
            if os.path.exists(default_db_path):
                with open(default_db_path, 'r') as f:
                    default_data = json.load(f)
                    DB.clear()
                    DB.update(default_data)
                
                # Test updating an existing ticket from default database
                if DB.get('tickets'):
                    ticket_id = int(list(DB['tickets'].keys())[0])
                    response = update_ticket(ticket_id, {"subject": "Updated from Default DB"})
                    
                    self.assertTrue(response['success'])
                    self.assertEqual(response['ticket']['subject'], "Updated from Default DB")
                    
                    # Verify new output fields
                    self._verify_new_output_fields(response['ticket'])
        finally:
            # Restore original state
            DB.clear()
            DB.update(current_state)

    def test_update_ticket_new_output_fields_specific(self):
        ticket = self._create_test_ticket()
        ticket_id = ticket['id']
        
        response = update_ticket(ticket_id, {"subject": "New Fields Test"})
        
        updated_ticket = response['ticket']
        
        # Test encoded_id specifically
        self.assertIn('encoded_id', updated_ticket)
        self.assertIsInstance(updated_ticket['encoded_id'], str)
        self.assertGreater(len(updated_ticket['encoded_id']), 0)
        
        # Test followup_ids specifically
        self.assertIn('followup_ids', updated_ticket)
        self.assertIsInstance(updated_ticket['followup_ids'], list)
        self.assertEqual(len(updated_ticket['followup_ids']), 0)
        
        # Test generated_timestamp specifically
        self.assertIn('generated_timestamp', updated_ticket)
        self.assertIsInstance(updated_ticket['generated_timestamp'], int)
        current_timestamp = int(time.time() * 1000)
        self.assertLess(abs(updated_ticket['generated_timestamp'] - current_timestamp), 5000)
        
        # Test url specifically
        self.assertIn('url', updated_ticket)
        self.assertIsInstance(updated_ticket['url'], str)
        self.assertTrue(updated_ticket['url'].startswith('https://zendesk.com/agent/tickets/'))
        self.assertTrue(updated_ticket['url'].endswith(str(ticket_id)))

    def test_update_ticket_new_fields_different_ids(self):
        # Create multiple tickets and verify fields are different
        tickets = []
        for i in range(3):
            ticket = self._create_test_ticket()
            response = update_ticket(ticket['id'], {"subject": f"Test {i}"})
            tickets.append(response['ticket'])
        
        # Verify encoded_ids are different
        encoded_ids = [t['encoded_id'] for t in tickets]
        self.assertEqual(len(encoded_ids), len(set(encoded_ids)))
        
        # Verify URLs are different
        urls = [t['url'] for t in tickets]
        self.assertEqual(len(urls), len(set(urls)))
        
        # Verify generated_timestamps are close but potentially different
        timestamps = [t['generated_timestamp'] for t in tickets]
        for timestamp in timestamps:
            self.assertIsInstance(timestamp, int)
            self.assertGreater(timestamp, 0)

    # Error condition tests
    def test_update_ticket_nonexistent_ticket_id_raises_value_error(self):
        self.assert_error_behavior(
            func_to_call=update_ticket,
            expected_exception_type=ValueError,
            expected_message="Ticket not found",
            ticket_id=999999,
            ticket_updates={"subject": "This should fail"}
        )

    def test_update_ticket_invalid_ticket_id_string_raises_value_error(self):
        self.assert_error_behavior(
            func_to_call=update_ticket,
            expected_exception_type=ValueError,
            expected_message="ticket_id must be an integer",
            ticket_id="not_an_integer",
            ticket_updates={"subject": "This should fail"}
        )

    def test_update_ticket_invalid_ticket_id_float_raises_value_error(self):
        self.assert_error_behavior(
            func_to_call=update_ticket,
            expected_exception_type=ValueError,
            expected_message="ticket_id must be an integer",
            ticket_id=1.5,
            ticket_updates={"subject": "This should fail"}
        )

    def test_update_ticket_invalid_ticket_id_none_raises_value_error(self):
        self.assert_error_behavior(
            func_to_call=update_ticket,
            expected_exception_type=ValueError,
            expected_message="ticket_id must be an integer",
            ticket_id=None,
            ticket_updates={"subject": "This should fail"}
        )

    def test_update_ticket_negative_ticket_id_raises_value_error(self):
        self.assert_error_behavior(
            func_to_call=update_ticket,
            expected_exception_type=ValueError,
            expected_message="Ticket not found",
            ticket_id=-1,
            ticket_updates={"subject": "This should fail"}
        )

    def test_update_ticket_zero_ticket_id_raises_value_error(self):
        self.assert_error_behavior(
            func_to_call=update_ticket,
            expected_exception_type=ValueError,
            expected_message="Ticket not found",
            ticket_id=0,
            ticket_updates={"subject": "This should fail"}
        )

    def test_update_ticket_empty_subject_raises_validation_error(self):
        ticket = self._create_test_ticket()
        ticket_id = ticket['id']
        
        self.assert_error_behavior(
            func_to_call=update_ticket,
            expected_exception_type=ValueError,
            expected_message="Validation failed: subject: String should have at least 1 character",
            ticket_id=ticket_id,
            ticket_updates={"subject": ""}
        )

    def test_update_ticket_empty_comment_body_raises_validation_error(self):
        ticket = self._create_test_ticket()
        ticket_id = ticket['id']
        
        self.assert_error_behavior(
            func_to_call=update_ticket,
            expected_exception_type=ValueError,
            expected_message="Validation failed: comment_body: String should have at least 1 character",
            ticket_id=ticket_id,
            ticket_updates={"comment_body": ""}
        )

    def test_update_ticket_invalid_priority_raises_validation_error(self):
        ticket = self._create_test_ticket()
        ticket_id = ticket['id']
        
        self.assert_error_behavior(
            func_to_call=update_ticket,
            expected_exception_type=ValueError,
            expected_message="Validation failed: priority: Input should be 'urgent', 'high', 'normal' or 'low'",
            ticket_id=ticket_id,
            ticket_updates={"priority": "invalid_priority"}
        )

    def test_update_ticket_invalid_status_raises_validation_error(self):
        ticket = self._create_test_ticket()
        ticket_id = ticket['id']
        
        self.assert_error_behavior(
            func_to_call=update_ticket,
            expected_exception_type=ValueError,
            expected_message="Validation failed: status: Input should be 'new', 'open', 'pending', 'hold', 'solved' or 'closed'",
            ticket_id=ticket_id,
            ticket_updates={"status": "invalid_status"}
        )

    def test_update_ticket_invalid_type_raises_validation_error(self):
        ticket = self._create_test_ticket()
        ticket_id = ticket['id']
        
        self.assert_error_behavior(
            func_to_call=update_ticket,
            expected_exception_type=ValueError,
            expected_message="Validation failed: ticket_type: Input should be 'problem', 'incident', 'question' or 'task'",
            ticket_id=ticket_id,
            ticket_updates={"ticket_type": "invalid_type"}
        )

    def test_update_ticket_with_new_attributes_success(self):
        """Test updating a ticket with new attributes."""
        ticket = self._create_test_ticket()
        ticket_id = ticket['id']
        
        # Update ticket with new attributes
        update_data = {
            'subject': 'Updated Subject with New Attributes',
            'priority': 'high',
            'status': 'open',
            'attribute_value_ids': [201, 202, 203],
            'custom_status_id': 600,
            'requester': 'updated@example.com',
            'safe_update': True,
            'ticket_form_id': 700,
            'updated_stamp': '2024-02-01T15:30:00Z',
            'via_followup_source_id': 800,
            'via_id': 900,
            'voice_comment': {
                'duration': 180,
                'transcript': 'Updated voice comment transcript',
                'audio_url': 'https://example.com/updated-audio.mp3'
            }
        }
        
        response = update_ticket(ticket_id, update_data)
        
        self.assertIsInstance(response, dict)
        self.assertTrue(response['success'])
        
        updated_ticket = response['ticket']
        
        # Verify basic fields are updated
        self.assertEqual(updated_ticket['subject'], 'Updated Subject with New Attributes')
        self.assertEqual(updated_ticket['priority'], 'high')
        self.assertEqual(updated_ticket['status'], 'open')
        self.assertEqual(updated_ticket['id'], ticket_id)
        
        # Verify new attributes are updated
        self.assertEqual(updated_ticket['attribute_value_ids'], [201, 202, 203])
        self.assertEqual(updated_ticket['custom_status_id'], 600)
        self.assertEqual(updated_ticket['requester'], 'updated@example.com')
        self.assertEqual(updated_ticket['safe_update'], True)
        self.assertEqual(updated_ticket['ticket_form_id'], 700)
        self.assertEqual(updated_ticket['updated_stamp'], '2024-02-01T15:30:00Z')
        self.assertEqual(updated_ticket['via_followup_source_id'], 800)
        self.assertEqual(updated_ticket['via_id'], 900)
        self.assertEqual(updated_ticket['voice_comment'], {
            'duration': 180,
            'transcript': 'Updated voice comment transcript',
            'audio_url': 'https://example.com/updated-audio.mp3'
        })
        
        # Verify ticket is updated in DB
        stored_ticket = DB['tickets'][str(ticket_id)]
        self.assertEqual(stored_ticket['attribute_value_ids'], [201, 202, 203])
        self.assertEqual(stored_ticket['custom_status_id'], 600)
        self.assertEqual(stored_ticket['requester'], 'updated@example.com')
        self.assertEqual(stored_ticket['safe_update'], True)
        self.assertEqual(stored_ticket['ticket_form_id'], 700)
        self.assertEqual(stored_ticket['updated_stamp'], '2024-02-01T15:30:00Z')
        self.assertEqual(stored_ticket['via_followup_source_id'], 800)
        self.assertEqual(stored_ticket['via_id'], 900)
        
        # Verify timestamp was updated
        self.assertTrue(self._is_iso_datetime_string(updated_ticket['updated_at']))

    def test_update_ticket_partial_new_attributes_success(self):
        """Test updating a ticket with only some new attributes."""
        ticket = self._create_test_ticket()
        ticket_id = ticket['id']
        
        # Update ticket with only some new attributes
        update_data = {
            'attribute_value_ids': [101, 102],
            'custom_status_id': 400,
            'safe_update': False
        }
        
        response = update_ticket(ticket_id, update_data)
        
        self.assertIsInstance(response, dict)
        self.assertTrue(response['success'])
        
        updated_ticket = response['ticket']
        
        # Verify only the specified new attributes are updated
        self.assertEqual(updated_ticket['attribute_value_ids'], [101, 102])
        self.assertEqual(updated_ticket['custom_status_id'], 400)
        self.assertEqual(updated_ticket['safe_update'], False)
        
        # Verify other attributes remain unchanged (should be None since not set originally)
        self.assertIsNone(updated_ticket.get('requester'))
        self.assertIsNone(updated_ticket.get('ticket_form_id'))
        self.assertIsNone(updated_ticket.get('updated_stamp'))
        self.assertIsNone(updated_ticket.get('via_followup_source_id'))
        self.assertIsNone(updated_ticket.get('via_id'))
        self.assertIsNone(updated_ticket.get('voice_comment')) 