import unittest
import os
import tempfile
import base64
import json
from datetime import datetime, UTC
from common_utils.base_case import BaseTestCaseWithErrorHandler
from gdrive.Files import create, get
from gdrive.SimulationEngine.db import DB, save_state, load_state
from pydantic import ValidationError
from gdrive.SimulationEngine.custom_errors import QuotaExceededError

class TestFilesCreate(BaseTestCaseWithErrorHandler):
    def setUp(self):
        """Reset DB to a clean state with proper quota settings."""
        # Clear and initialize DB with proper structure
        DB.clear()
        DB.update({
            'users': {
                'me': {
                    'about': {
                        'kind': 'drive#about',
                        'storageQuota': {
                            'limit': str(1024 * 1024 * 1024),  # 1GB
                            'usageInDrive': '0',
                            'usageInDriveTrash': '0',
                            'usage': '0'
                        },
                        'driveThemes': False,
                        'canCreateDrives': False,
                        'importFormats': {},
                        'exportFormats': {},
                        'appInstalled': False,
                        'user': {
                            'displayName': 'Test User',
                            'kind': 'drive#user',
                            'me': True,
                            'permissionId': 'perm_1',
                            'emailAddress': 'test@example.com'
                        },
                        'folderColorPalette': "",
                        'maxImportSizes': {},
                        'maxUploadSize': str(50 * 1024 * 1024)  # 50MB
                    },
                    'files': {},
                    'drives': {},
                    'comments': {},
                    'replies': {},
                    'labels': {},
                    'accessproposals': {},
                    'counters': {
                        'file': 0,
                        'drive': 0,
                        'comment': 0,
                        'reply': 0,
                        'label': 0,
                        'accessproposal': 0,
                        'revision': 0
                    }
                }
            }
        })

    def test_create_metadata_only(self):
        """Test creating a file with metadata only (no content upload)."""
        body = {
            'name': 'test_file.txt',
            'mimeType': 'text/plain',
            'size': '0',
            'parents': [],
        }
        
        # Verify there are no files in the DB
        self.assertEqual(len(DB['users']['me']['files']), 0)
        
        # Create file
        result = create(body=body)
        
        # Verify returned result
        self.assertEqual(result['name'], 'test_file.txt')
        self.assertEqual(result['mimeType'], 'text/plain')
        self.assertEqual(result['size'], '0')
        self.assertNotIn('content', result)
        self.assertNotIn('revisions', result)

        # Verify file exists in DB using get()
        file_id = result['id']
        file_from_db = get(file_id)
        self.assertEqual(file_from_db['name'], 'test_file.txt')
        self.assertEqual(file_from_db['mimeType'], 'text/plain')
        self.assertEqual(file_from_db['size'], '0')
        self.assertNotIn('content', file_from_db)
        self.assertNotIn('revisions', file_from_db)

    def test_create_with_content_upload(self):
        """Test creating a file with content upload and verify DB storage."""
        # Create temporary file for upload
        with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmp:
            tmp.write('hello world')
            tmp.flush()
            file_path = tmp.name
            
        try:
            body = {
                'name': 'file_with_content.txt',
                'mimeType': 'text/plain',
                'parents': []
            }
            media_body = {'filePath': file_path}
            
            # Create file with content
            result = create(body=body, media_body=media_body)
            
            # Verify returned result
            self.assertEqual(result['name'], 'file_with_content.txt')
            self.assertEqual(result['mimeType'], 'text/plain')
            self.assertIn('content', result)
            self.assertIn('revisions', result)
            self.assertEqual(len(result['revisions']), 1)
            
            # Verify main content structure - should have all 5 fields
            content = result['content']
            self.assertIn('data', content)
            self.assertIn('encoding', content)
            self.assertIn('checksum', content)
            self.assertIn('version', content)
            self.assertIn('lastContentUpdate', content)
            self.assertEqual(content['encoding'], 'base64')
            self.assertEqual(content['version'], '1.0')
            
            # Verify content data is valid base64
            self.assertIsInstance(content['data'], str)
            self.assertTrue(len(content['data']) > 0)
            
            # Verify checksum format
            self.assertTrue(content['checksum'].startswith('sha256:'))
            self.assertEqual(len(content['checksum']), 71)  # sha256: + 64 hex chars
            
            # Verify timestamp format
            self.assertIsInstance(content['lastContentUpdate'], str)
            self.assertTrue(content['lastContentUpdate'].endswith('Z'))
            
            # Verify revision structure
            revision = result['revisions'][0]
            self.assertEqual(revision['id'], 'rev-1')
            self.assertEqual(revision['mimeType'], 'text/plain')
            self.assertEqual(revision['originalFilename'], 'file_with_content.txt')
            self.assertIn('content', revision)
            self.assertIn('modifiedTime', revision)
            self.assertIn('keepForever', revision)
            self.assertIn('size', revision)
            
            # Verify revision content - should have only 3 fields (no version/lastContentUpdate)
            rev_content = revision['content']
            self.assertIn('data', rev_content)
            self.assertIn('encoding', rev_content)
            self.assertIn('checksum', rev_content)
            self.assertNotIn('version', rev_content)
            self.assertNotIn('lastContentUpdate', rev_content)
            
            # Verify revision content data matches main content
            self.assertEqual(rev_content['data'], content['data'])
            self.assertEqual(rev_content['encoding'], content['encoding'])
            self.assertEqual(rev_content['checksum'], content['checksum'])
            
            # Verify file exists in DB using get()
            file_id = result['id']
            file_from_db = get(file_id)
            self.assertEqual(file_from_db['name'], 'file_with_content.txt')
            self.assertIn('content', file_from_db)
            self.assertIn('revisions', file_from_db)
            self.assertEqual(len(file_from_db['revisions']), 1)
            
            # Verify content in DB matches exactly
            db_content = file_from_db['content']
            self.assertEqual(db_content['data'], content['data'])
            self.assertEqual(db_content['encoding'], content['encoding'])
            self.assertEqual(db_content['checksum'], content['checksum'])
            self.assertEqual(db_content['version'], content['version'])
            self.assertEqual(db_content['lastContentUpdate'], content['lastContentUpdate'])
            
            # Verify revision in DB matches exactly
            db_revision = file_from_db['revisions'][0]
            self.assertEqual(db_revision['id'], revision['id'])
            self.assertEqual(db_revision['mimeType'], revision['mimeType'])
            self.assertEqual(db_revision['originalFilename'], revision['originalFilename'])
            self.assertEqual(db_revision['size'], revision['size'])
            self.assertEqual(db_revision['keepForever'], revision['keepForever'])
            
            # Verify revision content in DB matches exactly
            db_rev_content = db_revision['content']
            self.assertEqual(db_rev_content['data'], rev_content['data'])
            self.assertEqual(db_rev_content['encoding'], rev_content['encoding'])
            self.assertEqual(db_rev_content['checksum'], rev_content['checksum'])
            self.assertNotIn('version', db_rev_content)
            self.assertNotIn('lastContentUpdate', db_rev_content)
            
        finally:
            # Clean up temporary file
            os.remove(file_path)

    def test_create_with_all_parameters(self):
        """Test creating a file with all parameters and content upload."""
        # Create temporary file for upload
        with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmp:
            tmp.write('test content with params')
            tmp.flush()
            file_path = tmp.name
            
        try:
            body = {
                'name': 'full_params.txt',
                'mimeType': 'text/plain',
                'parents': ['parent1'],
                'permissions': [{
                    'id': 'perm1', 
                    'role': 'owner', 
                    'type': 'user', 
                    'emailAddress': 'test@example.com'
                }]
            }
            media_body = {'filePath': file_path}
            
            # Create file with all parameters
            result = create(
                body=body,
                media_body=media_body,
                enforceSingleParent=True,
                ignoreDefaultVisibility=True,
                keepRevisionForever=True,
                ocrLanguage='en',
                supportsAllDrives=True,
                supportsTeamDrives=True,
                useContentAsIndexableText=True,
                includePermissionsForView='anyone',
                includeLabels='test,label'
            )
            
            # Verify returned result
            self.assertEqual(result['name'], 'full_params.txt')
            self.assertTrue(result['enforceSingleParent'])
            self.assertTrue(result['ignoreDefaultVisibility'])
            self.assertTrue(result['keepRevisionForever'])
            self.assertEqual(result['ocrLanguage'], 'en')
            self.assertTrue(result['supportsAllDrives'])
            self.assertTrue(result['supportsTeamDrives'])
            self.assertTrue(result['useContentAsIndexableText'])
            self.assertEqual(result['includePermissionsForView'], 'anyone')
            self.assertEqual(result['includeLabels'], 'test,label')
            self.assertIn('labels', result)
            self.assertEqual(result['labels'], ['test', 'label'])
            self.assertIn('content', result)
            self.assertIn('revisions', result)
            
            # Verify file exists in DB using get()
            file_id = result['id']
            file_from_db = get(file_id)
            self.assertEqual(file_from_db['name'], 'full_params.txt')
            self.assertTrue(file_from_db['enforceSingleParent'])
            self.assertTrue(file_from_db['keepRevisionForever'])
            self.assertEqual(file_from_db['ocrLanguage'], 'en')
            self.assertEqual(file_from_db['labels'], ['test', 'label'])
            self.assertIn('content', file_from_db)
            
        finally:
            # Clean up temporary file
            os.remove(file_path)

    def test_create_google_workspace_document(self):
        """Test creating a Google Workspace document (metadata only)."""
        body = {
            'name': 'test_document',
            'mimeType': 'application/vnd.google-apps.document',
            'parents': []
        }
        
        # Create Google Workspace document
        result = create(body=body)
        
        # Verify returned result
        self.assertEqual(result['name'], 'test_document')
        self.assertEqual(result['mimeType'], 'application/vnd.google-apps.document')
        self.assertIn('content', result)  # Google Workspace docs have empty content array
        self.assertIn('tabs', result)
        self.assertEqual(result['suggestionsViewMode'], 'DEFAULT')
        self.assertFalse(result['includeTabsContent'])
        
        # Verify file exists in DB using get()
        file_id = result['id']
        file_from_db = get(file_id)
        self.assertEqual(file_from_db['name'], 'test_document')
        self.assertEqual(file_from_db['mimeType'], 'application/vnd.google-apps.document')
        self.assertIn('content', file_from_db)
        self.assertIn('tabs', file_from_db)

    def test_create_spreadsheet(self):
        """Test creating a Google Sheets document."""
        body = {
            'name': 'test_spreadsheet',
            'mimeType': 'application/vnd.google-apps.spreadsheet',
            'parents': []
        }
        
        # Create spreadsheet
        result = create(body=body)
        
        # Verify returned result
        self.assertEqual(result['name'], 'test_spreadsheet')
        self.assertEqual(result['mimeType'], 'application/vnd.google-apps.spreadsheet')
        self.assertIn('sheets', result)
        self.assertIn('data', result)
        self.assertEqual(len(result['sheets']), 1)
        self.assertEqual(result['sheets'][0]['properties']['title'], 'Sheet1')
        
        # Verify file exists in DB using get()
        file_id = result['id']
        file_from_db = get(file_id)
        self.assertEqual(file_from_db['name'], 'test_spreadsheet')
        self.assertIn('sheets', file_from_db)
        self.assertIn('data', file_from_db)

    def test_create_invalid_body_type(self):
        """Test error handling for invalid body type."""
        self.assert_error_behavior(
            func_to_call=create,
            expected_exception_type=TypeError,
            expected_message="Argument 'body' must be a dictionary or None, got str",
            body='not_a_dict'
        )

    def test_create_invalid_media_body_type(self):
        """Test error handling for invalid media_body type."""
        self.assert_error_behavior(
            func_to_call=create,
            expected_exception_type=TypeError,
            expected_message="Argument 'media_body' must be a dictionary or None, got str",
            media_body='not_a_dict'
        )

    def test_create_invalid_bool_param(self):
        """Test error handling for invalid boolean parameter."""
        self.assert_error_behavior(
            func_to_call=create,
            expected_exception_type=TypeError,
            expected_message="Argument 'enforceSingleParent' must be a boolean, got str",
            enforceSingleParent='not_bool'
        )

    def test_create_invalid_str_param(self):
        """Test error handling for invalid string parameter."""
        self.assert_error_behavior(
            func_to_call=create,
            expected_exception_type=TypeError,
            expected_message="Argument 'ocrLanguage' must be a string, got int",
            ocrLanguage=123
        )

    def test_create_invalid_body_schema(self):
        """Test error handling for invalid body schema."""
        self.assert_error_behavior(
            func_to_call=create,
            expected_exception_type=ValidationError,
            expected_message="1 validation error for FileBodyModel",
            body={'name': 123, 'mimeType': 'text/plain'}
        )

    def test_create_invalid_media_body_schema(self):
        """Test error handling for invalid media_body schema."""
        self.assert_error_behavior(
            func_to_call=create,
            expected_exception_type=ValidationError,
            expected_message="1 validation error for MediaBodyModel",
            media_body={'filePath': 123}
        )

    def test_create_quota_exceeded(self):
        """Test error handling when quota is exceeded."""
        # Set quota to 1 byte
        DB['users']['me']['about']['storageQuota']['limit'] = '1'
        
        with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmp:
            tmp.write('abc')
            tmp.flush()
            file_path = tmp.name
            
        try:
            body = {'name': 'bigfile.txt', 'mimeType': 'text/plain'}
            media_body = {'filePath': file_path}
            
            self.assert_error_behavior(
                func_to_call=create,
                expected_exception_type=QuotaExceededError,
                expected_message="Quota exceeded. Cannot create the file.",
                body=body,
                media_body=media_body
            )
        finally:
            os.remove(file_path)

    def test_create_file_not_found(self):
        """Test error handling when file path doesn't exist."""
        body = {'name': 'nofile.txt', 'mimeType': 'text/plain'}
        media_body = {'filePath': '/nonexistent/path.txt'}
        
        self.assert_error_behavior(
            func_to_call=create,
            expected_exception_type=FileNotFoundError,
            expected_message="File not found: /nonexistent/path.txt",
            body=body,
            media_body=media_body
        )

    def test_create_with_enforce_single_parent(self):
        """Test enforceSingleParent parameter behavior."""
        body = {
            'name': 'test_file.txt',
            'mimeType': 'text/plain',
            'parents': ['parent1', 'parent2', 'parent3']
        }
        
        # Test with enforceSingleParent=True
        result = create(body=body, enforceSingleParent=True)
        self.assertTrue(result['enforceSingleParent'])
        self.assertEqual(result['parents'], ['parent3'])  # Should keep only the last parent
        
        # Verify in DB
        file_id = result['id']
        file_from_db = get(file_id)
        self.assertEqual(file_from_db['parents'], ['parent3'])

    def test_create_with_ignore_default_visibility(self):
        """Test ignoreDefaultVisibility parameter behavior."""
        body = {
            'name': 'test_file.txt',
            'mimeType': 'text/plain',
            'parents': []
        }
        
        # Test with ignoreDefaultVisibility=True
        result = create(body=body, ignoreDefaultVisibility=True)
        self.assertTrue(result['ignoreDefaultVisibility'])
        
        # Should have owner permission added
        self.assertIn('permissions', result)
        owner_perms = [p for p in result['permissions'] if p['role'] == 'owner']
        self.assertEqual(len(owner_perms), 1)
        self.assertEqual(owner_perms[0]['emailAddress'], 'test@example.com')

    def test_content_structure_matches_db_schema(self):
        """Test that content structure exactly matches the GdriveDefaultDB.json schema."""
        # Create temporary file for upload
        with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmp:
            tmp.write('test content for schema validation')
            tmp.flush()
            file_path = tmp.name
            
        try:
            body = {
                'name': 'schema_test.txt',
                'mimeType': 'text/plain',
                'parents': []
            }
            media_body = {'filePath': file_path}
            
            # Create file with content
            result = create(body=body, media_body=media_body)
            
            # Verify main content structure matches GdriveDefaultDB.json schema
            content = result['content']
            expected_content_keys = {'data', 'encoding', 'checksum', 'version', 'lastContentUpdate'}
            actual_content_keys = set(content.keys())
            self.assertEqual(actual_content_keys, expected_content_keys, 
                           f"Main content keys mismatch. Expected: {expected_content_keys}, Got: {actual_content_keys}")
            
            # Verify each field has correct type and format
            self.assertIsInstance(content['data'], str)
            self.assertIsInstance(content['encoding'], str)
            self.assertIsInstance(content['checksum'], str)
            self.assertIsInstance(content['version'], str)
            self.assertIsInstance(content['lastContentUpdate'], str)
            
            # Verify specific format requirements
            self.assertEqual(content['encoding'], 'base64')
            self.assertEqual(content['version'], '1.0')
            self.assertTrue(content['checksum'].startswith('sha256:'))
            self.assertTrue(content['lastContentUpdate'].endswith('Z'))
            
            # Verify revision structure matches GdriveDefaultDB.json schema
            self.assertEqual(len(result['revisions']), 1)
            revision = result['revisions'][0]
            
            # Verify revision top-level keys
            expected_revision_keys = {'id', 'mimeType', 'modifiedTime', 'keepForever', 'originalFilename', 'size', 'content'}
            actual_revision_keys = set(revision.keys())
            self.assertEqual(actual_revision_keys, expected_revision_keys,
                           f"Revision keys mismatch. Expected: {expected_revision_keys}, Got: {actual_revision_keys}")
            
            # Verify revision content structure (should have only 3 fields)
            rev_content = revision['content']
            expected_rev_content_keys = {'data', 'encoding', 'checksum'}
            actual_rev_content_keys = set(rev_content.keys())
            self.assertEqual(actual_rev_content_keys, expected_rev_content_keys,
                           f"Revision content keys mismatch. Expected: {expected_rev_content_keys}, Got: {actual_rev_content_keys}")
            
            # Verify revision content data matches main content exactly
            self.assertEqual(rev_content['data'], content['data'])
            self.assertEqual(rev_content['encoding'], content['encoding'])
            self.assertEqual(rev_content['checksum'], content['checksum'])
            
            # Verify through get() that DB storage maintains exact structure
            file_id = result['id']
            file_from_db = get(file_id)
            
            # Verify main content in DB has exact same structure
            db_content = file_from_db['content']
            db_content_keys = set(db_content.keys())
            self.assertEqual(db_content_keys, expected_content_keys,
                           f"DB main content keys mismatch. Expected: {expected_content_keys}, Got: {db_content_keys}")
            
            # Verify revision content in DB has exact same structure
            db_revision = file_from_db['revisions'][0]
            db_rev_content = db_revision['content']
            db_rev_content_keys = set(db_rev_content.keys())
            self.assertEqual(db_rev_content_keys, expected_rev_content_keys,
                           f"DB revision content keys mismatch. Expected: {expected_rev_content_keys}, Got: {db_rev_content_keys}")
            
            # Verify all values are preserved exactly in DB
            for key in expected_content_keys:
                self.assertEqual(db_content[key], content[key], f"DB content field '{key}' mismatch")
            
            for key in expected_rev_content_keys:
                self.assertEqual(db_rev_content[key], rev_content[key], f"DB revision content field '{key}' mismatch")
                
        finally:
            # Clean up temporary file
            os.remove(file_path)

    def test_db_persistence(self):
        """Test that created files persist in the database across operations."""
        # Create first file
        body1 = {'name': 'file1.txt', 'mimeType': 'text/plain'}
        result1 = create(body=body1)
        file_id1 = result1['id']
        
        # Create second file
        body2 = {'name': 'file2.txt', 'mimeType': 'text/plain'}
        result2 = create(body=body2)
        file_id2 = result2['id']
        
        # Verify both files exist in DB
        file1_from_db = get(file_id1)
        file2_from_db = get(file_id2)
        
        self.assertEqual(file1_from_db['name'], 'file1.txt')
        self.assertEqual(file2_from_db['name'], 'file2.txt')
        
        # Verify they have different IDs
        self.assertNotEqual(file_id1, file_id2)

    def test_create_file_with_modified_time(self):
        """Test that the modified time is included in the response."""
        file_metadata = {
            'name': 'Test File Name',
            'mimeType': 'application/vnd.google-apps.document',
            'modifiedTime': '2024-05-01T00:00:00Z',
        }
        result = create(body=file_metadata)
        self.assertIn('modifiedTime', result)
        self.assertIsInstance(result['modifiedTime'], str)
        self.assertEqual(result['modifiedTime'], '2024-05-01T00:00:00Z')
    
    def test_create_file_with_modified_time_and_includeLabels(self):
        """Test that the modified time is included in the response and includeLabels is included."""
        file_metadata = {
            'name': 'Test File Name',
            'mimeType': 'application/vnd.google-apps.document',
            'modifiedTime': '2024-05-01T00:00:00Z',
        }
        result = create(body=file_metadata, includeLabels='Archived')
        self.assertIn('modifiedTime', result)
        self.assertIsInstance(result['modifiedTime'], str)
        self.assertEqual(result['modifiedTime'], '2024-05-01T00:00:00Z')
        self.assertIn('labels', result)
        self.assertEqual(result['labels'], ['Archived'])

if __name__ == '__main__':
    unittest.main() 