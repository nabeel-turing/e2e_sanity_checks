import unittest
from unittest.mock import patch, mock_open
import os
import sys
import base64
import hashlib
from datetime import datetime, timedelta, UTC
import copy

from common_utils.base_case import BaseTestCaseWithErrorHandler

from gdrive.SimulationEngine.content_manager import DriveContentManager
from gdrive import get_file_content
from gdrive.SimulationEngine.db import DB

class TestDriveContentManager(BaseTestCaseWithErrorHandler):
    """An extensive, state-based test suite for the DriveContentManager class."""

    def setUp(self):
        """Reset DB to a clean state before each test."""
        self.manager = DriveContentManager()
        DB.clear()
        DB.update({
            'users': {
                'test_user': {
                    'files': {
                        'file1': {
                            'id': 'file1',
                            'name': 'Document.png',
                            'mimeType': 'image/png',
                            'createdTime': '2025-06-26T15:00:00Z',
                            'modifiedTime': '2025-06-26T15:00:00Z',
                            'owners': ['test_user'],
                            'size': '0',
                            'content': None,
                            'revisions': [],
                            'exportFormats': {}
                        },
                        'file_no_revisions': {
                            'id': 'file_no_revisions',
                            'name': 'Document.png',
                            'mimeType': 'image/png',
                            'createdTime': '2025-06-26T15:00:00Z',
                            'modifiedTime': '2025-06-26T15:00:00Z',
                            'owners': ['test_user'],
                            'size': '0',
                            'content': None,
                            'exportFormats': {}
                        },
                        'file_with_content': {
                            'id': 'file_with_content',
                            'name': 'ContentFile.png',
                            'mimeType': 'image/png',
                            'createdTime': '2025-06-26T15:00:00Z',
                            'modifiedTime': '2025-06-27T11:00:00Z',
                            'owners': ['test_user'],
                            'size': '15',
                            'content': {
                                'data': base64.b64encode(b'initial content').decode(),
                                'encoding': 'base64',
                                'checksum': f"sha256:{hashlib.sha256(b'initial content').hexdigest()}",
                                'version': '1.0',
                                'lastContentUpdate': datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
                            },
                            'revisions': [],
                            'exportFormats': {
                                'application/pdf': base64.b64encode(b'cached_data').decode()
                            }
                        },
                        'file_with_content_txt': {
                            'id': 'file_with_content_txt',
                            'name': 'ContentFile.txt',
                            'mimeType': 'text/plain',
                            'createdTime': '2025-06-16T15:00:00Z',
                            'modifiedTime': '2025-06-17T11:00:00Z',
                            'owners': ['test_user'],
                            'size': '15',
                            'content': {
                                'data': 'initial content',
                                'encoding': 'text',
                                'checksum': self.manager.file_processor.calculate_checksum('initial content'.encode('utf-8')),
                                'version': '1.0',
                                'lastContentUpdate': datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
                            },
                            'revisions': [],
                            'exportFormats': {
                                'application/pdf': 'cached_data'
                            }
                        },
                        'file_with_revs': {
                            'id': 'file_with_revs',
                            'name': 'RevisionsTest.txt',
                            'mimeType': 'text/plain',
                            'createdTime': '2025-06-26T20:00:00Z',
                            'modifiedTime': '2025-06-27T10:00:00Z',
                            'owners': ['test_user'],
                            'size': '13',
                            'content': {
                                'data': 'aW5pdGlhbCBjb250ZW50',
                                'checksum': f"sha256:{hashlib.sha256(b'initial content').hexdigest()}",
                                'version': '1.0',
                                'lastContentUpdate': datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
                            },
                            'revisions': [
                                {
                                    'id': 'rev-1',
                                    'keepForever': False,
                                    'originalFilename': 'RevisionsTest.txt',
                                    'size': '10',
                                    'mimeType': 'text/plain',
                                    'modifiedTime': datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ'),
                                    'content': {
                                        'data': base64.b64encode(b'rev-1').decode(),
                                        'encoding': 'base64',
                                        'checksum': f"sha256:{hashlib.sha256(b'rev-1').hexdigest()}",
                                        'version': '1.0',
                                        'lastContentUpdate': datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
                                    }
                                },
                                {
                                    'id': 'rev-2',
                                    'keepForever': True,
                                    'originalFilename': 'RevisionsTest.txt',
                                    'size': '12',
                                    'mimeType': 'text/plain',
                                    'modifiedTime': datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ'),
                                    'content': {
                                        'data': base64.b64encode(b'rev-2').decode(),
                                        'encoding': 'base64',
                                        'checksum': f"sha256:{hashlib.sha256(b'rev-2').hexdigest()}",
                                        'version': '1.0',
                                        'lastContentUpdate': datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
                                    }
                                }
                            ],
                            'exportFormats': {}
                        }
                    }
                    }
                }
            })

    def test_get_file_content_latest_success(self):
        """Test getting the latest content of a file returns correct data."""
        result = get_file_content(user_id='test_user', file_id='file_with_content')
        self.assertIn('content', result)
        self.assertEqual(result['content']['data'], base64.b64encode(b'initial content').decode())

    def test_get_file_content_from_revision_success(self):
        """Test getting content from a specific revision returns correct data."""
        result = get_file_content(user_id='test_user', file_id='file_with_revs', revision_id='rev-1')
        self.assertEqual(result['revision_id'], 'rev-1')
        self.assertEqual(result['content']['data'], base64.b64encode(b'rev-1').decode())

    def test_get_file_content_no_content_error(self):
        """Test ValueError when getting content from a file that has none."""
        self.assert_error_behavior(
            get_file_content, ValueError, "No content found for file 'file1'",
            user_id='test_user', file_id='file1'
        )
    
    def test_get_file_content_file_with_no_revisions_raises_value_error(self):
        """Test ValueError when getting content from a file with no revisions."""
        self.assert_error_behavior(
            get_file_content, ValueError, "No content found for file 'file1'",
            user_id='test_user', file_id='file1'
        )

    def test_get_file_content_non_existing_user_id_raises_value_error(self):
        """Test ValueError when getting content from a non-existing user."""
        self.assert_error_behavior(
            get_file_content, ValueError, "User 'non_existing_user' not found",
            user_id='non_existing_user', file_id='file_with_content'
        )
    
    def test_get_file_content_non_existing_file_id_raises_value_error(self):
        """Test ValueError when getting content from a non-existing file."""
        self.assert_error_behavior(
            get_file_content, ValueError, "File 'non_existing_file' not found for user 'test_user'",
            user_id='test_user', file_id='non_existing_file'
        )
    
    def test_get_file_content_file_with_no_revisions_raises_value_error(self):
        """Test ValueError when getting content from a file with no revisions."""
        self.assert_error_behavior(
            get_file_content, ValueError, "No revisions found for file 'file_no_revisions'",
            user_id='test_user', file_id='file_no_revisions', revision_id='rev-1'
        )
    
    def test_get_file_content_non_existing_revision_id_raises_value_error(self):
        """Test ValueError when getting content from a non-existing revision."""
        self.assert_error_behavior(
            get_file_content, ValueError, "Revision 'non_existing_revision' not found for file 'file_with_revs'",
            user_id='test_user', file_id='file_with_revs', revision_id='non_existing_revision'
        )
    
    def test_get_file_content_with_non_string_user_id_raises_value_error(self):
        """Test ValueError when getting content with a non-string user_id."""
        self.assert_error_behavior(
            get_file_content, ValueError, "user_id must be a string",
            user_id=123, file_id='file_with_content'
        )
    
    def test_get_file_content_with_non_string_file_id_raises_value_error(self):
        """Test ValueError when getting content with a non-string file_id."""
        self.assert_error_behavior(
            get_file_content, ValueError, "file_id must be a string",
            user_id='test_user', file_id=123
        )
    
    def test_get_file_content_with_non_string_revision_id_raises_value_error(self):
        """Test ValueError when getting content with a non-string revision_id."""
        self.assert_error_behavior(
            get_file_content, ValueError, "revision_id must be a string",
            user_id='test_user', file_id='file_with_content', revision_id=123
        )

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
