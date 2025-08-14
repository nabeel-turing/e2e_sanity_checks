"""Database structure and state management for Google Sheets API simulation.

This module contains the database structure and state management functions
for the Google Sheets API simulation. It provides functions for saving and
loading the database state.
"""

import sys

sys.path.append("APIs")
from gdrive import DB as DRIVE_DB
import gdrive

# Shared reference to the database
DB = DRIVE_DB

# Database structure for Google Sheets API simulation
# DB = {
#     'users': {
#         'me': {
#             'about': {
#                 'kind': 'drive#about',
#                 'storageQuota': {
#                     'limit': '107374182400',  # 100 GB
#                     'usageInDrive': '0',
#                     'usageInDriveTrash': '0',
#                     'usage': '0'
#                 },
#                 'user': {
#                     'displayName': 'Test User',
#                     'kind': 'drive#user',
#                     'me': True,
#                     'permissionId': 'test-user-1234',
#                     'emailAddress': 'test@example.com'
#                 }
#             },
#             'files': {},
#             'changes': {'changes': [], 'startPageToken': '1'},
#             'drives': {},
#             'permissions': {},
#             'comments': {},
#             'replies': {},
#             'apps': {},
#             'channels': {},
#             'counters': {
#                 'file': 0,
#                 'drive': 0,
#                 'comment': 0,
#                 'reply': 0,
#                 'label': 0,
#                 'accessproposal': 0,
#                 'revision': 0,
#                 'change_token': 0
#             }
#         }
#     }
# }


def save_state(filepath: str) -> None:
    """Saves the current database state to a JSON file.

    Args:
        filepath: Path to save the database state to.
    """
    gdrive.save_state(filepath)
    # with open(filepath, 'w') as f:
    #     json.dump(DB, f, indent=2)


def load_state(filepath: str) -> None:
    """Loads the database state from a JSON file.

    Args:
        filepath: Path to load the database state from.
    """
    gdrive.load_state(filepath)
    # with open(filepath, 'r') as f:
    #     global DB
    #     DB = json.load(f)