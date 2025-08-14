from common_utils.print_log import print_log
"""
Database module for Copilot API simulation.
Provides in-memory database functionality and state management.
"""

import json
import datetime

# Initial application state and file system representation.
# This dictionary serves as the in-memory database for the application.
# It is modified by API functions and can be persisted to/loaded from a file.
DB = {
    "workspace_root": "/home/user/project",
    "cwd": "/home/user/project/src",  # Current working directory within the workspace
    "file_system": {
        # Each key is an absolute path within the workspace.
        # 'is_directory': Python boolean True for directories, False for files.
        # 'content_lines': List of strings for file content; empty for directories.
        # 'size_bytes': Integer size; calculated for files, 0 for directories.
        # 'last_modified': ISO 8601 timestamp string.
        "/home/user/project": {
            "path": "/home/user/project",
            "is_directory": True,
            "content_lines": [],
            "size_bytes": 0,
            "last_modified": "2024-03-19T12:00:00Z",
            "is_readonly": False,

        },
        "/home/user/project/src": {
            "path": "/home/user/project/src",
            "is_directory": True,
            "content_lines": [],
            "size_bytes": 0,
            "last_modified": "2024-03-19T12:00:00Z",
            "is_readonly": True,
        }
    },
    "background_processes": {
        "12345": {
            "pid": 12345,
            "command": "sleep 10 && echo 'done'",
            "exec_dir": "/tmp/cmd_exec_abc123", # The persistent temporary directory
            "stdout_path": "/tmp/cmd_exec_abc123/stdout.log",
            "stderr_path": "/tmp/cmd_exec_abc123/stderr.log",
            "exitcode_path": "/tmp/cmd_exec_abc123/exitcode.log",
            "last_stdout_pos": 0, # Tracks how much of the stdout log has been read
            "last_stderr_pos": 0, # Tracks how much of the stderr log has been read
        }
    },
    "vscode_extensions_marketplace": [],
    "vscode_context": {"is_new_workspace_creation": True},
    "installed_vscode_extensions":[],
    "vscode_api_references": [],
    "_next_pid": 1
}

def save_state(filepath: str) -> None:
    """
    Persists the current state of the in-memory 'DB' to a JSON file.

    This function is typically used for saving the application's state for later retrieval,
    effectively creating a snapshot of the workspace and its contents.

    Args:
        filepath (str): The path to the file where the state should be saved.
                        The file will be overwritten if it already exists.
    """
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(DB, f, indent=2)  # Use indent for human-readable JSON output
    except IOError as e:
        raise  # Re-raise the exception if the caller needs to handle it

def load_state(filepath: str) -> None:
    """
    Loads the application state from a specified JSON file, replacing the
    current in-memory 'DB'.

    This is typically used at application startup to restore a previously saved state.
    If the file is not found or cannot be decoded, the existing in-memory 'DB'
    (which might be the default initial state) is preserved, and a warning is issued.

    Args:
        filepath (str): The path to the JSON file from which to load the state.
    """
    global DB  # Declare intent to modify the global DB object
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            loaded_state = json.load(f)
        DB.clear()  # Remove all items from the current DB
        DB.update(loaded_state)  # Populate DB with the loaded state
    except FileNotFoundError:
        print_log(f"Warning: State file '{filepath}' not found. Using current or default DB state.")
    except json.JSONDecodeError as e:
        print_log(f"Error: Could not decode JSON from '{filepath}'. DB state may be invalid or outdated. Details: {e}")
    except Exception as e:
        print_log(f"An unexpected error occurred while loading state from '{filepath}': {e}") 