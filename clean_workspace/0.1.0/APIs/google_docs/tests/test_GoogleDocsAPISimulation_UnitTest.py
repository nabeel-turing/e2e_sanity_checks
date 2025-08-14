"""
Unit tests for the Google Docs API simulation.
"""

import unittest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from pydantic import ValidationError
from common_utils.base_case import BaseTestCaseWithErrorHandler
from ..SimulationEngine.db import DB

from .. import create_document, batch_update_document, get_document
from APIs import gdrive


class TestDocuments(BaseTestCaseWithErrorHandler):
    """Test suite for the Documents class."""

    def setUp(self):
        """Reset the database state before each test."""
        DB["users"] = {
            "me": {
                "about": {
                    "user": {
                        "emailAddress": "me@example.com",
                        "displayName": "Test User",
                    },
                    "storageQuota": {"limit": "10000000000", "usage": "0"},
                },
                "files": {},
                "comments": {},
                "replies": {},
                "labels": {},
                "accessproposals": {},
                "counters": {
                    "file": 0,
                    "comment": 0,
                    "reply": 0,
                    "label": 0,
                    "accessproposal": 0,
                },
            }
        }
        
        # Create a test document with ID "doc-valid" for the new tests
        doc_id = "doc-valid"
        DB["users"]["me"]["files"][doc_id] = {
            "id": doc_id,
            "driveId": "",
            "name": "Test Document",
            "mimeType": "application/vnd.google-apps.document",
            "createdTime": "2025-03-11T09:00:00Z",
            "modifiedTime": "2025-03-11T09:00:00Z",
            "parents": [],
            "owners": ["me@example.com"],
            "suggestionsViewMode": "DEFAULT",
            "includeTabsContent": False,
            "content": [],
            "tabs": [],
            "permissions": [{"role": "owner", "type": "user", "emailAddress": "me@example.com"}],
            "trashed": False,
            "starred": False,
            "size": 0,
        }
    
    
    def tearDown(self):
        """Clean up any patched globals."""
        # Restore original _ensure_user if it was patched
        # globals()['_ensure_user'] = _original_ensure_user # If needed
        pass
      

    def test_create_document(self):
        """Test creating a new document."""
        # Test with default title
        doc, status = create_document()
        self.assertEqual(status, 200)
        self.assertEqual(doc["name"], "Untitled Document")
        self.assertEqual(doc["mimeType"], "application/vnd.google-apps.document")
        self.assertEqual(doc["owners"], ["me@example.com"])
        self.assertIn(doc["id"], DB["users"]["me"]["files"])

        # Test with custom title
        doc, status = create_document(title="Test Document")
        self.assertEqual(status, 200)
        self.assertEqual(doc["name"], "Test Document")

    def test_get_document(self):
        """Test retrieving a document."""
        # Create a document first
        doc, _ = create_document(title="Test Document")
        doc_id = doc["id"]

        # Test successful retrieval
        retrieved_doc = get_document(doc_id)
        self.assertEqual(retrieved_doc["name"], "Test Document")
        self.assertEqual(retrieved_doc["id"], doc_id)

        # Test with suggestions view mode
        retrieved_doc = get_document(doc_id, suggestionsViewMode="SUGGESTIONS_INLINE")
        self.assertEqual(retrieved_doc["suggestionsViewMode"], "SUGGESTIONS_INLINE")

        # Test with include tabs content
        retrieved_doc = get_document(doc_id, includeTabsContent=True)
        self.assertTrue(retrieved_doc["includeTabsContent"])

        # Test non-existent document
        with self.assertRaises(ValueError) as context:
            get_document("non-existent-id")
        self.assertEqual(str(context.exception), "Document 'non-existent-id' not found")

    def test_batch_update_document(self):
        """Test updating a document with batch operations."""
        # Create a document first
        doc, _ = create_document(title="Test Document")
        doc_id = doc["id"]

        # Test inserting text
        requests = [{"insertText": {"text": "Hello, World!", "location": {"index": 0}}}]
        response, status = batch_update_document(doc_id, requests)
        self.assertEqual(status, 200)
        self.assertEqual(response["documentId"], doc_id)
        self.assertEqual(len(response["replies"]), 1)

        # Verify the content was inserted
        updated_doc = get_document(doc_id)
        self.assertEqual(len(updated_doc["content"]), 1)
        self.assertEqual(updated_doc["content"][0]["textRun"]["content"], "Hello, World!")

        # Test updating document style
        requests = [
            {
                "updateDocumentStyle": {
                    "documentStyle": {
                        "background": {
                            "color": {"rgbColor": {"red": 1, "green": 1, "blue": 1}}
                        }
                    }
                }
            }
        ]
        response, status = batch_update_document(doc_id, requests)
        self.assertEqual(status, 200)
        self.assertEqual(response["documentId"], doc_id)
        self.assertEqual(len(response["replies"]), 1)

        # Verify the style was updated
        updated_doc = get_document(doc_id)
        self.assertIn("documentStyle", updated_doc)
        self.assertEqual(
            updated_doc["documentStyle"]["background"]["color"]["rgbColor"]["red"], 1
        )

        # Test with non-existent document
        self.assert_error_behavior(
            batch_update_document,
            FileNotFoundError,
            "Document with ID 'non-existent-id' not found.",
            documentId="non-existent-id",
            requests=requests
        )

        # Test with invalid request
        requests = [{"invalidRequest": {}}]
        self.assert_error_behavior(
            batch_update_document,
            TypeError,
            "Unsupported request type.",
            documentId=doc_id,
            requests=requests
        )
        requests = [[1]]
        self.assert_error_behavior(
            batch_update_document,
            TypeError,
            "request must be a dictionary.",
            documentId=doc_id,
            requests=requests
        )

    def test_valid_input_creates_document(self):
        """Test that valid title and userId result in document creation."""
        # Set up a test user in the DB
        userId = "existing_user"
        DB["users"][userId] = {
            "about": {
                "user": {
                    "emailAddress": f"{userId}@example.com",
                    "displayName": "Test User",
                }
            },
            "files": {},
            "comments": {},
            "replies": {},
            "labels": {},
            "accessproposals": {},
            "counters": {
                "file": 0,
                "comment": 0,
                "reply": 0,
                "label": 0,
                "accessproposal": 0,
            },
        }
        
        title = "My Test Document"
        document, status_code = create_document(title=title, userId=userId)

        self.assertIsInstance(document, dict)
        self.assertEqual(status_code, 200)
        self.assertEqual(document["name"], title)
        self.assertIn("id", document)
        self.assertTrue(len(document["id"]) > 0)  # uuid was generated
        self.assertEqual(document["owners"], [f"{userId}@example.com"])
        
        # Clean up
        if userId in DB["users"]:
            del DB["users"][userId]

    def test_default_arguments_create_document(self):
        """Test document creation with default arguments."""
        # Make sure 'me' user exists and is properly set up
        userId = "me"
        if userId not in DB["users"]:
            DB["users"][userId] = {
                "about": {
                    "user": {
                        "emailAddress": f"{userId}@example.com",
                        "displayName": "Default User",
                    }
                },
                "files": {},
                "comments": {},
                "replies": {},
                "labels": {},
                "accessproposals": {},
                "counters": {
                    "file": 0,
                    "comment": 0,
                    "reply": 0,
                    "label": 0,
                    "accessproposal": 0,
                },
            }

        document, status_code = create_document()  # Uses default title and userId

        self.assertIsInstance(document, dict)
        self.assertEqual(status_code, 200)
        self.assertEqual(document["name"], "Untitled Document")  # Default title
        self.assertIn("id", document)
        self.assertEqual(document["owners"], ["me@example.com"])  # Default user "me"

    def test_invalid_title_type_raises_typeerror(self):
        """Test that non-string title raises TypeError."""
        self.assert_error_behavior(
            func_to_call=create_document,
            expected_exception_type=TypeError,
            expected_message="Argument 'title' must be a string, got int.",
            title=123,
            userId="test_user"
        )

    def test_invalid_userid_type_raises_typeerror(self):
        """Test that non-string userId raises TypeError."""
        self.assert_error_behavior(
            func_to_call=create_document,
            expected_exception_type=TypeError,
            expected_message="Argument 'userId' must be a string, got list.",
            title="Valid Title",
            userId=["not", "a", "string"]
        )

    def test_valid_input_insert_text(self):
        """Test valid batch update with insertText requests."""
        requests = [
            {
                "insertText": {
                    "text": "Hello ",
                    "location": {"index": 0}
                }
            },
            {
                "insertText": {
                    "text": "World!",
                    "location": {"index": 1} # Assuming "Hello " is 1 unit in content list
                }
            }
        ]
        response, status_code = batch_update_document(documentId="doc-valid", requests=requests, userId="me")
        self.assertEqual(status_code, 200)
        self.assertEqual(response["documentId"], "doc-valid")
        self.assertEqual(len(response["replies"]), 2)
        self.assertIn("insertText", response["replies"][0])
        self.assertEqual(DB["users"]["me"]["files"]["doc-valid"]["content"][0]["textRun"]["content"], "Hello ")
        self.assertEqual(DB["users"]["me"]["files"]["doc-valid"]["content"][1]["textRun"]["content"], "World!")

    def test_valid_input_update_document_style(self):
        """Test valid batch update with updateDocumentStyle requests."""
        requests = [
            {
                "updateDocumentStyle": {
                    "documentStyle": {"fontSize": 14, "bold": True}
                }
            }
        ]
        response, status_code = batch_update_document(documentId="doc-valid", requests=requests, userId="me")
        self.assertEqual(status_code, 200)
        self.assertEqual(response["documentId"], "doc-valid")
        self.assertEqual(len(response["replies"]), 1)
        self.assertIn("updateDocumentStyle", response["replies"][0])
        self.assertEqual(DB["users"]["me"]["files"]["doc-valid"]["documentStyle"], {"fontSize": 14, "bold": True})

    def test_valid_input_mixed_requests(self):
        """Test valid batch update with mixed request types."""
        requests = [
            {
                "insertText": {
                    "text": "Chapter 1. ",
                    "location": {"index": 0}
                }
            },
            {
                "updateDocumentStyle": {
                    "documentStyle": {"pageColor": "blue"}
                }
            }
        ]
        response, status_code = batch_update_document(documentId="doc-valid", requests=requests, userId="me")
        self.assertEqual(status_code, 200)
        self.assertEqual(len(response["replies"]), 2)
        self.assertIn("insertText", response["replies"][0])
        self.assertIn("updateDocumentStyle", response["replies"][1])
        self.assertEqual(DB["users"]["me"]["files"]["doc-valid"]["content"][0]["textRun"]["content"], "Chapter 1. ")
        self.assertEqual(DB["users"]["me"]["files"]["doc-valid"]["documentStyle"]["pageColor"], "blue")

    def test_valid_input_empty_requests_list(self):
        """Test with an empty list of requests."""
        response, status_code = batch_update_document(documentId="doc-valid", requests=[], userId="me")
        self.assertEqual(status_code, 200)
        self.assertEqual(len(response["replies"]), 0)

    def test_document_not_found(self):
        """Test when the documentId does not exist."""
        requests = [{"insertText": {"text": "Test", "location": {"index": 0}}}]
        self.assert_error_behavior(
            func_to_call=batch_update_document,
            expected_exception_type=FileNotFoundError,
            expected_message="Document with ID 'doc-nonexistent' not found.",
            documentId="doc-nonexistent",
            requests=requests,
            userId="me"
        )

    def test_invalid_document_id_type(self):
        """Test that invalid documentId type raises TypeError."""
        self.assert_error_behavior(
            func_to_call=batch_update_document,
            expected_exception_type=TypeError,
            expected_message="documentId must be a string.",
            documentId=123,
            requests=[],
            userId="me"
        )

    def test_invalid_user_id_type(self):
        """Test that invalid userId type raises TypeError."""
        self.assert_error_behavior(
            func_to_call=batch_update_document,
            expected_exception_type=TypeError,
            expected_message="userId must be a string.",
            documentId="doc-valid",
            requests=[],
            userId=123
        )
    
    def test_user_id_auto_creation(self):
        """Test that an unknown userId is automatically created by _ensure_user."""
        # Make sure the user doesn't exist
        userId = "auto_created_test_user"
        if userId in DB["users"]:
            del DB["users"][userId]
            
        requests = [{"insertText": {"text": "Test", "location": {"index": 0}}}]
        self.assert_error_behavior(
            func_to_call=batch_update_document,
            expected_exception_type=FileNotFoundError,
            expected_message="Document with ID 'doc-nonexistent' not found.",
            documentId="doc-nonexistent",
            requests=requests,
            userId=userId
        )
        
        # Verify the user was auto-created
        self.assertIn(userId, DB["users"])
        self.assertEqual(DB["users"][userId]["about"]["user"]["emailAddress"], f"{userId}@example.com")

    def test_requests_not_a_list(self):
        """Test that non-list requests argument raises TypeError."""
        self.assert_error_behavior(
            func_to_call=batch_update_document,
            expected_exception_type=TypeError,
            expected_message="requests must be a list.",
            documentId="doc-valid",
            requests="not-a-list",
            userId="me"
        )

    def test_insert_text_missing_text_field(self):
        """Test InsertTextRequest with missing 'text' field - should raise ValidationError."""
        requests = [{"insertText": {"location": {"index": 0}}}]  # 'text' is missing
        
        self.assert_error_behavior(
            func_to_call=batch_update_document,
            expected_exception_type=ValidationError,
            expected_message="Field required",
            documentId="doc-valid", 
            requests=requests, 
            userId="me"
        )

    def test_requests_list_with_non_dict_item(self):
        """Test requests list containing a non-dictionary item - causes TypeError."""
        
        self.assert_error_behavior(
            func_to_call=batch_update_document,
            expected_exception_type=TypeError,
            expected_message="request must be a dictionary.",
            documentId="doc-valid",
            requests=[123],  # Item is not a dictionary
            userId="me"
        )

    def test_requests_item_unknown_request_type_key(self):
        """Test request item with an unknown top-level key - should raise TypeError."""
        self.assert_error_behavior(
            func_to_call=batch_update_document,
            expected_exception_type=TypeError,
            expected_message="Unsupported request type.",
            documentId="doc-valid",
            requests=[{"unknownRequest": {"data": "value"}}],
            userId="me"
        )

    # --- InsertTextRequestModel specific validation tests ---
    def test_insert_text_invalid_text_type(self):
        """Test InsertTextRequest with invalid type for 'text' field - should raise ValidationError."""
        requests = [{"insertText": {"text": 123, "location": {"index": 0}}}]  # 'text' is not a string
        
        self.assert_error_behavior(
            func_to_call=batch_update_document,
            expected_exception_type=ValidationError,
            expected_message="Input should be a valid string",
            documentId="doc-valid", 
            requests=requests, 
            userId="me"
        )

    def test_insert_text_location_missing_index(self):
        """Test InsertTextRequest location with missing 'index' field - should raise ValidationError."""
        requests = [{"insertText": {"text": "abc", "location": {}}}]  # 'index' is missing
        
        self.assert_error_behavior(
            func_to_call=batch_update_document,
            expected_exception_type=ValidationError,
            expected_message="Field required",
            documentId="doc-valid",
            requests=requests, 
            userId="me"
        )

    def test_insert_text_location_invalid_index_type(self):
        """Test InsertTextRequest location with invalid type for 'index' - should raise ValidationError."""
        requests = [{"insertText": {"text": "abc", "location": {"index": "zero"}}}]  # 'index' not int
        
        self.assert_error_behavior(
            func_to_call=batch_update_document,
            expected_exception_type=ValidationError,
            expected_message="Input should be a valid integer",
            documentId="doc-valid", 
            requests=requests, 
            userId="me"
        )

    def test_insert_text_request_extra_field_in_detail(self):
        """Test InsertTextRequest detail with an extra field."""
        requests = [{"insertText": {"text": "abc", "location": {"index": 0}, "extraField": "bad"}}]
        
        # Implementation ignores extra fields, so this should process successfully
        self.assert_error_behavior(
            func_to_call=batch_update_document,
            expected_exception_type=ValidationError,
            expected_message="Extra inputs are not permitted",
            documentId="doc-valid", 
            requests=requests, 
            userId="me"
        )

    def test_insert_text_request_extra_field_in_location(self):
        """Test InsertTextRequest location with an extra field."""
        requests = [{"insertText": {"text": "abc", "location": {"index": 0, "extraField": "bad"}}}]
        
        self.assert_error_behavior(
            func_to_call=batch_update_document,
            expected_exception_type=ValidationError,
            expected_message="Extra inputs are not permitted",
            documentId="doc-valid", 
            requests=requests, 
            userId="me"
        )

    def test_insert_text_request_extra_top_level_field(self):
        """Test InsertTextRequest with an extra top-level field."""
        requests = [{"insertText": {"text": "abc", "location": {"index": 0}}, "extraTopField": "bad"}]
        
        self.assert_error_behavior(
            func_to_call=batch_update_document,
            expected_exception_type=ValidationError,
            expected_message="Extra inputs are not permitted",
            documentId="doc-valid", 
            requests=requests, 
            userId="me"
        )

    # --- UpdateDocumentStyleRequestModel specific validation tests ---
    def test_update_document_style_missing_document_style_field(self):
        """Test UpdateDocumentStyleRequest with missing 'documentStyle' field - should raise ValidationError."""
        requests = [{"updateDocumentStyle": {}}]  # 'documentStyle' is missing
        
        self.assert_error_behavior(
            func_to_call=batch_update_document,
            expected_exception_type=ValidationError,
            expected_message="Field required",
            documentId="doc-valid", 
            requests=requests, 
            userId="me"
        )

    def test_update_document_style_invalid_document_style_type(self):
        """Test UpdateDocumentStyleRequest with invalid type for 'documentStyle' - should raise ValidationError."""
        requests = [{"updateDocumentStyle": {"documentStyle": "not-a-dict"}}]
        
        self.assert_error_behavior(
            func_to_call=batch_update_document,
            expected_exception_type=ValidationError,
            expected_message="Input should be a valid dictionary",
            documentId="doc-valid", 
            requests=requests, 
            userId="me"
        )

    def test_update_document_style_request_extra_field_in_detail(self):
        """Test UpdateDocumentStyleRequest detail with an extra field."""
        requests = [{"updateDocumentStyle": {"documentStyle": {}, "extraField": "bad"}}]
        
        self.assert_error_behavior(
            func_to_call=batch_update_document,
            expected_exception_type=ValidationError,
            expected_message="Extra inputs are not permitted",
            documentId="doc-valid", 
            requests=requests, 
            userId="me"
        )   
    def test_update_document_style_request_extra_top_level_field(self):
        """Test UpdateDocumentStyleRequest with an extra top-level field."""
        requests = [{"updateDocumentStyle": {"documentStyle": {}}, "extraTopField": "bad"}]
        
        self.assert_error_behavior(
            func_to_call=batch_update_document,
            expected_exception_type=ValidationError,
            expected_message="Extra inputs are not permitted",
            documentId="doc-valid", 
            requests=requests, 
            userId="me"
        )


    def test_empty_string_title_is_valid(self):
        """Test that an empty string title is accepted (passes validation)."""
        userId = "empty_title_user"
        DB["users"][userId] = {
            "about": {
                "user": {
                    "emailAddress": f"{userId}@example.com",
                    "displayName": "Empty Title User",
                }
            },
            "files": {},
            "comments": {},
            "replies": {},
            "labels": {},
            "accessproposals": {},
            "counters": {
                "file": 0,
                "comment": 0,
                "reply": 0,
                "label": 0,
                "accessproposal": 0,
            },
        }
        
        document, status_code = create_document(title="", userId=userId)
        self.assertEqual(document["name"], "")
        self.assertEqual(status_code, 200)
        
        # Clean up
        if userId in DB["users"]:
            del DB["users"][userId]

    def test_valid_inputs_document_not_found(self):
        """Test retrieval of a non-existing document with valid inputs."""
        # This test assumes DB and _ensure_user are set up for the user, but document is not found.
        with self.assertRaises(ValueError) as context:
            get_document(documentId="non_existent_doc", userId="test_user")
        self.assertEqual(str(context.exception), "Document 'non_existent_doc' not found")

    def test_invalid_documentId_type(self):
        """Test that a non-string documentId raises TypeError."""
        self.assert_error_behavior(
            func_to_call=get_document,
            expected_exception_type=TypeError,
            expected_message="documentId must be a string.",
            documentId=123, # Invalid type
            userId="test_user"
        )

    def test_invalid_suggestionsViewMode_type(self):
        """Test that a non-string suggestionsViewMode (when not None) raises TypeError."""
        self.assert_error_behavior(
            func_to_call=get_document,
            expected_exception_type=TypeError,
            expected_message="suggestionsViewMode must be a string or None.",
            documentId="doc123",
            suggestionsViewMode=123, # Invalid type
            userId="test_user"
        )

    def test_invalid_includeTabsContent_type(self):
        """Test that a non-boolean includeTabsContent raises TypeError."""
        self.assert_error_behavior(
            func_to_call=get_document,
            expected_exception_type=TypeError,
            expected_message="includeTabsContent must be a boolean.",
            documentId="doc123",
            includeTabsContent="not_a_bool", # Invalid type
            userId="test_user"
        )

    def test_invalid_userId_type(self):
        """Test that a non-string userId raises TypeError."""
        self.assert_error_behavior(
            func_to_call=get_document,
            expected_exception_type=TypeError,
            expected_message="userId must be a string.",
            documentId="doc123",
            userId=12345 # Invalid type
        )

    def test_create_userid_empty_raises_valueerror(self):
        """Test that empty userId raises ValueError."""
        self.assert_error_behavior(
            func_to_call=create_document,
            expected_exception_type=ValueError,
            expected_message="Argument 'userId' cannot be empty or only whitespace.",
            title="Valid Title",
            userId=""
        )

    def test_create_userid_whitespace_only_raises_valueerror(self):
        """Test that whitespace-only userId raises ValueError."""
        self.assert_error_behavior(
            func_to_call=create_document,
            expected_exception_type=ValueError,
            expected_message="Argument 'userId' cannot be empty or only whitespace.",
            title="Valid Title",
            userId="   "  # Whitespace-only
        )

    def test_Agent_1000_base_Merged(self):
        DOC_TITLE = "Feature Highlights – This Month"

        # Assert that the Google Doc titled "Feature Highlights – This Month" does not exist.
        GDRIVE_QUERY_DOC_EXISTS = f"name='{DOC_TITLE}' and mimeType='application/vnd.google-apps.document'"
        doc_files = gdrive.list_user_files(q=GDRIVE_QUERY_DOC_EXISTS).get("files", [])
        assert not doc_files, f"Google Doc titled '{DOC_TITLE}' is found."

        # Hardcoded relevant posts from inspection (simulating model output)
        relevant_posts = [
            {
            "commentary": "An important update available for our internal values deck. Please review by Friday."
            },
            {
            "commentary": "We’ve just released our revamped hiring toolkit to help managers onboard better.",
            }
        ]

        response, _ = create_document(title=DOC_TITLE)
        doc_id = response.get("id")

        # Prepare content and insert
        insert_text = ""
        for post in relevant_posts:
            insert_text += f"{post['commentary']}\n"

        batch_update_document(
            documentId=doc_id,
            requests=[{
                "insertText": {
                    "location": {"index": 1},
                    "text": insert_text.strip()
                }
            }]
        )

        # Assert that Google Doc titled "Feature Highlights – This Month" exists
        files = gdrive.list_user_files().get("files", [])
        assert any(f["name"] == DOC_TITLE for f in files), f"Google Doc titled '{DOC_TITLE}' does not already exist."

        target_file = next(f for f in files if f["name"] == DOC_TITLE and f["mimeType"] == 'application/vnd.google-apps.document' )
        doc = get_document(target_file['id'])
        doc_content = doc['content'][0]['textRun']['content'].lower()

        # Verify all relevant LinkedIn posts are in the Google Doc
        assert all(post['commentary'].lower() in doc_content for post in relevant_posts), f"Not all relevant posts are included in the '{DOC_TITLE}' document."

    def test_batch_update_initializes_missing_content(self):
        """batchUpdate should create 'content' list when key is absent."""
        doc, _ = create_document(title="MissingContentDoc")
        doc_id = doc["id"]
        # Remove the content key entirely
        del DB["users"]["me"]["files"][doc_id]["content"]
        requests = [{"insertText": {"text": "Hi", "location": {"index": 0}}}]
        response, status = batch_update_document(documentId=doc_id, requests=requests, userId="me")
        self.assertEqual(status, 200)
        self.assertEqual(DB["users"]["me"]["files"][doc_id]["content"][0]["textRun"]["content"], "Hi")

    def test_batch_update_initializes_none_content(self):
        """batchUpdate should replace None 'content' with list and insert."""
        doc, _ = create_document(title="NoneContentDoc")
        doc_id = doc["id"]
        DB["users"]["me"]["files"][doc_id]["content"] = None
        requests = [{"insertText": {"text": "Hello", "location": {"index": 0}}}]
        response, status = batch_update_document(documentId=doc_id, requests=requests, userId="me")
        self.assertEqual(status, 200)
        self.assertEqual(DB["users"]["me"]["files"][doc_id]["content"][0]["textRun"]["content"], "Hello")


if __name__ == "__main__":
    unittest.main()
