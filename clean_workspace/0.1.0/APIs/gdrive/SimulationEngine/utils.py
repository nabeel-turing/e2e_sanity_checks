from common_utils.print_log import print_log
"""
Utility functions for Google Drive API simulation.

This module provides helper functions used by the Google Drive API simulation.
"""
import json
import os
import base64
import mimetypes
import hashlib
import re
from typing import Dict, Any, List, Optional, Union, Set
from datetime import datetime, timezone, timedelta, UTC
from dateutil import parser
from .db import DB
from .search_engine import search_engine_manager
from . import models
from .file_utils import read_file, is_binary_file, get_mime_type

METADATA_KEYS_DRIVES = {'id', 'name', 'hidden', 'themeId'}
METADATA_KEYS_FILES = {'id', 'name', 'mimeType', 'trashed', 'starred', 'parents', 'description'}

def _ensure_user(userId: str) -> None:
    """Ensure that the user entry exists in DB, creating if necessary.
    
    Args:
        userId (str): The ID of the user to ensure exists.
    """
    if userId not in DB['users']:
        DB['users'][userId] = {
            'about': {
                'kind': 'drive#about',
                'storageQuota': {
                    'limit': '107374182400',  # Example: 100 GB
                    'usageInDrive': '0',
                    'usageInDriveTrash': '0',
                    'usage': '0'
                },
                'driveThemes': False,
                'canCreateDrives': True,
                'importFormats': {},
                'exportFormats': {},
                'appInstalled': False,
                'user': {
                    'displayName': f'User {userId}',
                    'kind': 'drive#user',
                    'me': True,
                    'permissionId': '1234567890',
                    'emailAddress': f'{userId}@example.com'
                },
                'folderColorPalette': "",
                'maxImportSizes': {},
                'maxUploadSize': '52428800'  # Example: 50 MB
            },
            'files': {},
            'drives': {},
            'comments': {},
            'replies': {},
            'labels': {},
            'accessproposals': {},
            'apps': {},
            'channels': {},
            'changes': {
                'startPageToken': '1',
                'changes': []
            },
            'counters': {
                'file': 0,
                'drive': 0,
                'comment': 0,
                'reply': 0,
                'label': 0,
                'accessproposal': 0,
                'revision': 0,
                'change_token': 0,
                'channel': 0
            }
        }

def _ensure_file(userId: str, fileId: str) -> None:
    """Ensure that the file entry exists in DB, creating if necessary.
    
    Args:
        userId (str): The ID of the user who owns the file.
        fileId (str): The ID of the file to ensure exists.
    """
    if userId not in DB['users']:
        DB['users'][userId] = {'files': {}}
    if 'files' not in DB['users'][userId]:
        DB['users'][userId]['files'] = {}
    if fileId not in DB['users'][userId]['files']:
        DB['users'][userId]['files'][fileId] = {}
    if 'permissions' not in DB['users'][userId]['files'][fileId]:
        DB['users'][userId]['files'][fileId]['permissions'] = []



def _parse_query(q: str) -> List[List[Dict[str, Any]]]:
    """
    Parse a query string into a list of condition groups (OR of ANDs).
    """
    operators = [' contains ', '!=', '<=', '>=', '=', '<', '>', ' in ']
    raw_or = [cond.strip() for cond in q.split(' or ')]
    groups: List[List[Dict[str, Any]]] = []
    for or_group in raw_or:
        raw_and = [cond.strip() for cond in or_group.split(' and ')]
        parsed: List[Dict[str, Any]] = []
        for cond in raw_and:
            for op in operators:
                token = op.strip()
                if token in cond:
                    parts = cond.split(token)
                    if len(parts) != 2:
                        raise ValueError(f"Invalid condition format: '{cond}'")
                    if token == 'in':
                        value, field = parts
                    else:
                        field, value = parts
                    parsed.append({
                        'query_term': field.strip(),
                        'operator': token,
                        'value': value.strip().strip("'\"")
                    })
                    break
            else:
                raise ValueError(f"Unsupported condition or bad format: '{cond}'")
        groups.append(parsed)
    return groups


def _apply_query_filter(items: List[Dict[str, Any]],
                        condition_groups: List[List[Dict[str, str]]],
                        resource_type: str) -> List[Dict[str, Any]]:
    """
    Filter a list of items (drives or files) by condition groups.
    """
    if not condition_groups:
        return items
    filtered: List[Dict[str, Any]] = []
    for item in items:
        for group in condition_groups:
            if _matches_all_conditions(item, group, resource_type):
                filtered.append(item)
                break
    return filtered


def _matches_all_conditions(item: Dict[str, Any],
                            conditions: List[Dict[str, str]],
                            resource_type: str) -> bool:
    """
    Check if a single item satisfies all conditions in one AND-group.
    """
    engine = search_engine_manager.get_engine()
    metadata_keys = METADATA_KEYS_DRIVES if resource_type == 'drive' else METADATA_KEYS_FILES

    for cond in conditions:
        field = cond['query_term']
        op = cond['operator']
        val = cond['value']

        # Field must exist
        if field not in item:
            return False

        # Substring/search semantics for metadata keys
        if field in metadata_keys:
            results = engine.search(val, {
                'resource_type': resource_type,
                'content_type': field
            })
            ids = {r.get('id') for r in results}
            if op in ['=', 'contains', 'in']:
                if item.get('id') not in ids:
                    return False
            elif op == '!=':
                if item.get('id') in ids:
                    return False
            else:
                # unsupported operator on metadata
                return False
            continue

        value = item.get(field)
        # Boolean fields
        if isinstance(value, bool):
            flag = val.lower() == 'true'
            if op in ['=', '=='] and value != flag:
                return False
            if op == '!=' and value == flag:
                return False
            continue

        # Date/time fields
        if field in ['createdTime', 'modifiedTime']:
            try:
                dt_item = parser.parse(value)
                dt_cond = parser.parse(val)
            except Exception:
                return False
            if op == '=' and dt_item != dt_cond:
                return False
            if op == '!=' and dt_item == dt_cond:
                return False
            if op in ['<', '<=', '>', '>=']:
                if op == '<' and not (dt_item < dt_cond): return False
                if op == '<=' and not (dt_item <= dt_cond): return False
                if op == '>' and not (dt_item > dt_cond): return False
                if op == '>=' and not (dt_item >= dt_cond): return False
            continue

        # String contains, in, numeric comparisons
        text = str(value)
        if op == 'contains':
            if val.lower() not in text.lower(): return False
        elif op == 'in':
            if isinstance(value, (list, tuple)):
                if val not in value: return False
            else:
                if val not in text: return False
        elif op == '=':
            if text != val: return False
        elif op == '!=':
            if text == val: return False
        else:
            # numeric comparisons
            try:
                num_item = float(value)
                num_val = float(val)
            except Exception:
                return False
            if op == '<' and not (num_item < num_val): return False
            if op == '<=' and not (num_item <= num_val): return False
            if op == '>' and not (num_item > num_val): return False
            if op == '>=' and not (num_item >= num_val): return False

    return True


def _delete_descendants(userId: str, user_email: str, parent_id: str):
    """Recursively deletes all child files/folders owned by the user.
    
    Args:
        userId (str): The ID of the user performing the deletion.
        user_email (str): The email of the user performing the deletion.
        parent_id (str): The ID of the parent file/folder.
    """
    all_files = DB['users'][userId]['files']
    children = [
        f_id for f_id, f in all_files.items()
        if parent_id in f.get('parents', []) and user_email in f.get('owners', [])
    ]

    for child_id in children:
        child = all_files.get(child_id)
        if child:
            if child.get('mimeType') == 'application/vnd.google-apps.folder':
                _delete_descendants(userId, user_email, child_id)

            file_size = int(child.get('size', 0))
            all_files.pop(child_id, None)
            _update_user_usage(userId, -file_size)

def _has_drive_role(user_email: str, folder: dict, required_role: str = 'organizer') -> bool:
    """Checks if the user has the required role in a folder's permissions.
    
    Args:
        user_email (str): The email of the user to check.
        folder (dict): The folder to check permissions for.
        required_role (str): The required role to check for.
        
    Returns:
        bool: True if the user has the required role, False otherwise.
    """
    for perm in folder.get('permissions', []):
        if perm.get('emailAddress') == user_email and perm.get('role') == required_role:
            return True
    return False

def _ensure_apps(userId: str) -> None:
    """Ensure that the apps structure exists in DB, creating if necessary.
    
    Args:
        userId (str): The ID of the user to ensure apps exist for.
    """
    if userId not in DB['users']:
        DB['users'][userId] = {'apps': {}}
    if 'apps' not in DB['users'][userId]:
        DB['users'][userId]['apps'] = {}

def _ensure_changes(userId: str) -> None:
    """Ensure that the changes structure exists in DB, creating if necessary.
    
    Args:
        userId (str): The ID of the user to ensure changes exist for.
    """
    if userId not in DB['users']:
        DB['users'][userId] = {'changes': {'startPageToken': '1', 'changes': []}}
    if 'changes' not in DB['users'][userId]:
        DB['users'][userId]['changes'] = {'startPageToken': '1', 'changes': []}

def _ensure_channels(userId: str) -> None:
    """Ensure that the channels entry exists in DB, creating if necessary.
    
    Args:
        userId (str): The ID of the user to ensure exists.
    """
    # if userId not in DB['users']:
        # _ensure_user(userId)
    if 'channels' not in DB['users'][userId]:
        DB['users'][userId]['channels'] = {}

def _get_user_quota(userId: str) -> Dict[str, int]:
    """Helper to fetch user quota info.
    
    Args:
        userId (str): The ID of the user to get quota info for.
        
    Returns:
        Dict[str, int]: Dictionary containing quota information with keys:
            - 'limit' (int): The storage limit in bytes.
            - 'usage' (int): The current storage usage in bytes.
    """
    quota = DB['users'][userId]['about']['storageQuota']
    return {
        'limit': int(quota['limit']),
        'usage': int(quota['usage'])
    }

def _update_user_usage(userId: str, size_diff: int) -> None:
    """Update the user's storage quota usage.
    
    Args:
        userId (str): The ID of the user whose usage to update.
        size_diff (int): The difference in size to add (positive) or subtract (negative).
    """
    quota = DB['users'][userId]['about']['storageQuota']
    current_usage = int(quota['usage'])
    new_usage = max(0, current_usage + size_diff)  # Ensure usage doesn't go below 0
    quota['usage'] = str(new_usage)
    quota['usageInDrive'] = str(new_usage)  # For simplicity, we'll use the same value

def _ensure_drives(userId: str) -> None:
    """Ensure that the drives structure exists in DB, creating if necessary.
    
    Args:
        userId (str): The ID of the user to ensure drives exist for.
    """
    if userId not in DB['users']:
        DB['users'][userId] = {'drives': {}}
    if 'drives' not in DB['users'][userId]:
        DB['users'][userId]['drives'] = {}



def _create_raw_file_json(file_path: str) -> Dict[str, Any]:
    """
    Create a JSON representation for a text file (.txt, .html, .css, etc.) that doesn't have a JSON file.
    Text content is stored as raw text without encoding.
    
    Args:
        file_path (str): Path to the text file
        
    Returns:
        Dict[str, Any]: JSON representation of the text file
    """
    file_name = os.path.basename(file_path)
    file_extension = os.path.splitext(file_name)[1].lower()
    file_stats = os.stat(file_path)
    file_id = f"file_{hashlib.md5(file_path.encode()).hexdigest()}"
    current_time = datetime.fromtimestamp(file_stats.st_mtime, UTC).strftime('%Y-%m-%dT%H:%M:%SZ')

    # Get MIME type based on extension for text files
    mime_type_map = {
        '.txt': 'text/plain',
        '.html': 'text/html',
        '.htm': 'text/html',
        '.css': 'text/css',
        '.js': 'application/javascript',
        '.json': 'application/json',
        '.csv': 'text/csv',
        '.md': 'text/markdown',
        '.py': 'text/x-python',
        '.ini': 'text/plain',
        '.log': 'text/plain',
        '.notebook': 'application/json'
    }

    mime_type = mime_type_map.get(file_extension, 'text/plain')

    # Read the text file without encoding
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = f.read()

        content = {
            "data": raw_data,  # Store raw text content without encoding
            "encoding": mime_type,
            "checksum": f"sha256:{hashlib.sha256(raw_data.encode('utf-8')).hexdigest()}",
            "version": "1.0",
            "lastContentUpdate": current_time
        }
    except Exception as e:
        print_log(f"Warning: Failed to read text file {file_name}: {e}")
        content = {
            "data": f"Error reading text file: {e}",
            "encoding": "error",
            "checksum": f"sha256:{hashlib.sha256(f'Error reading text file: {e}'.encode('utf-8')).hexdigest()}",
            "version": "1.0",
            "lastContentUpdate": current_time
        }

    # Create the JSON structure matching the expected format
    json_data = {
        "id": file_id,
        "driveId": "",
        "name": file_name,
        "mimeType": mime_type,
        "createdTime": datetime.fromtimestamp(file_stats.st_ctime, UTC).strftime('%Y-%m-%dT%H:%M:%SZ'),
        "modifiedTime": current_time,
        "trashed": False,
        "starred": False,
        "parents": [],
        "owners": ["john.doe@gmail.com"],
        "size": str(file_stats.st_size),
        "content": content,
        "permissions": [
            {
                "id": f"permission_{file_id}",
                "role": "owner",
                "type": "user",
                "emailAddress": "john.doe@gmail.com"
            }
        ],
        "revisions": [
            {
                "id": f"revision_{file_id}",
                "mimeType": mime_type,
                "modifiedTime": current_time,
                "keepForever": False,
                "originalFilename": file_name,
                "size": str(file_stats.st_size),
                "content": {
                    "data": content["data"],
                    "encoding": content["encoding"],
                    "checksum": content["checksum"]
                }
            }
        ]
    }

    return json_data

def _create_binary_file_json(file_path: str) -> Dict[str, Any]:
    """
    Create a JSON representation for a binary file (PDF, image, etc.) that doesn't have a JSON file.
    
    Args:
        file_path (str): Path to the binary file
        
    Returns:
        Dict[str, Any]: JSON representation of the binary file
    """
    import hashlib
    from datetime import datetime, UTC
    
    file_name = os.path.basename(file_path)
    file_extension = os.path.splitext(file_name)[1].lower()
    file_stats = os.stat(file_path)
    file_id = f"file_{hashlib.md5(file_path.encode()).hexdigest()}"
    current_time = datetime.fromtimestamp(file_stats.st_mtime, UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    # Get MIME type based on extension
    mime_type_map = {
        '.pdf': 'application/pdf',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.tiff': 'image/tiff',
        '.webp': 'image/webp',
        '.svg': 'image/svg+xml',
        '.ico': 'image/x-icon'
    }
    
    mime_type = mime_type_map.get(file_extension, 'application/octet-stream')
    
    # Read the binary file and convert to base64
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
        
        content_data = base64.b64encode(raw_data).decode('utf-8')
        content = {
            "data": content_data,
            "encoding": "base64",
            "checksum": f"sha256:{hashlib.sha256(raw_data).hexdigest()}",
            "version": "1.0",
            "lastContentUpdate": current_time
        }
    except Exception as e:
        print_log(f"Warning: Failed to read binary file {file_name}: {e}")
        content = {
            "data": f"Error reading binary file: {e}",
            "encoding": "error",
            "checksum": f"sha256:{hashlib.sha256(f'Error reading binary file: {e}'.encode('utf-8')).hexdigest()}",
            "version": "1.0",
            "lastContentUpdate": current_time
        }
    
    # Create the JSON structure matching the expected format
    json_data = {
        "id": file_id,
        "driveId": "",
        "name": file_name,
        "mimeType": mime_type,
        "createdTime": datetime.fromtimestamp(file_stats.st_ctime, UTC).strftime('%Y-%m-%dT%H:%M:%SZ'),
        "modifiedTime": current_time,
        "trashed": False,
        "starred": False,
        "parents": [],
        "owners": ["john.doe@gmail.com"],
        "size": str(file_stats.st_size),
        "content": content,
        "permissions": [
            {
                "id": f"permission_{file_id}",
                "role": "owner",
                "type": "user",
                "emailAddress": "john.doe@gmail.com"
            }
        ],
        "revisions": [
            {
                "id": f"revision_{file_id}",
                "mimeType": mime_type,
                "modifiedTime": current_time,
                "keepForever": False,
                "originalFilename": file_name,
                "size": str(file_stats.st_size),
                "content": {
                    "data": content["data"],
                    "encoding": content["encoding"],
                    "checksum": content["checksum"]
                }
            }
        ]
    }
    
    return json_data



def hydrate_db(db_instance, directory_path):
    """
    Reads all JSON files from a folder and its subfolders and returns a list of their contents.
    Also processes binary files (PDF, images, etc.) that don't have JSON representations.
    Converts files to base64 on the fly instead of ignoring them.

    Args:
        db_instance (Dict[str, Any]): The database instance (a dict) to be hydrated.
        directory_path (str): The path to the root folder to start searching from.

    Returns:
        bool: True if hydration was successful.

    Raises:
        FileNotFoundError: If the specified directory_path does not exist.
    """
    if not os.path.isdir(directory_path):
        raise FileNotFoundError(f"Directory not found: '{directory_path}'")
    
    user_id = 'me'
    _ensure_user(user_id)

    db_user = db_instance['users'][user_id]

    all_json_data = []
    binary_files_processed = []  # Track binary files processed in second pass
    processed_files = set()  # Track files we've already processed
    
    # First pass: Process JSON files that are metadata for other files
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                
                # Heuristic: if the filename before .json has an extension, it's metadata.
                filename_stem = file[:-5]  # remove .json
                if os.path.splitext(filename_stem)[1]:  # e.g., '.txt' from 'file.txt'
                    try:
                        # Open and load the JSON file
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            
                            # Track that we've processed this original file and the metadata file
                            original_file_name = data.get('name', filename_stem)
                            processed_files.add(original_file_name)
                            processed_files.add(file) # Add the .json file itself to avoid reprocessing
                            
                            all_json_data.append(data)
                    except json.JSONDecodeError:
                        print_log(f"Warning: Could not decode JSON from file: {file_path}")
                    except Exception as e:
                        print_log(f"An error occurred while reading {file_path}: {e}")
    
    # Second pass: Process files that don't have JSON representations (including standalone .json files)
    # Define text and binary file extensions
    text_extensions = ['.txt', '.html', '.htm', '.css', '.js', '.json', '.csv', '.md', '.py', '.ini', '.log', '.notebook']
    binary_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg', '.ico']
    
    text_files_processed = []  # Track text files processed
    binary_files_processed = []  # Track binary files processed
    
    for root, _, files in os.walk(directory_path):
        for file in files:
            # Skip if this file was already processed via JSON
            if file in processed_files:
                continue
                
            file_extension = os.path.splitext(file)[1].lower()
            file_path = os.path.join(root, file)
            
            # Process text files
            if file_extension in text_extensions:
                try:
                    # Create a JSON representation for the text file
                    data = _create_raw_file_json(file_path)
                    all_json_data.append(data)
                    text_files_processed.append(file)
                    print_log(f"Info: Created JSON representation for text file: {file}")
                except Exception as e:
                    print_log(f"Warning: Failed to process text file {file}: {e}")
            
            # Process binary files
            elif file_extension in binary_extensions:
                try:
                    # Create a JSON representation for the binary file
                    data = _create_binary_file_json(file_path)
                    all_json_data.append(data)
                    binary_files_processed.append(file)
                    print_log(f"Info: Created JSON representation for binary file: {file}")
                except Exception as e:
                    print_log(f"Warning: Failed to process binary file {file}: {e}")
    
    # Log files processed for debugging
    if text_files_processed:
        print_log(f"Info: Processed {len(text_files_processed)} text files during hydration: {', '.join(text_files_processed[:10])}{'...' if len(text_files_processed) > 10 else ''}")
    if binary_files_processed:
        print_log(f"Info: Processed {len(binary_files_processed)} binary files during hydration: {', '.join(binary_files_processed[:10])}{'...' if len(binary_files_processed) > 10 else ''}")
    
    db_user['files'] = {file['id']: file for file in all_json_data}
    return True