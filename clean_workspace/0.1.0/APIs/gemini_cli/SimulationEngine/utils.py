from common_utils.print_log import print_log
"""Utility helpers for the gemini_cli SimulationEngine."""

import mimetypes
from typing import Dict, Any, List, Optional
import os
import datetime
import shutil
import logging
import time  # Added for hydration helpers
import inspect
import stat  # For file permission constants
import subprocess
import base64  # Added for base64 encoding of binary archive content

from .db import DB
from common_utils.log_complexity import log_complexity
from .custom_errors import InvalidInputError, WorkspaceNotAvailableError
from .file_utils import _is_within_workspace

try:
    from _stat import *
except ImportError:
    pass

logger = logging.getLogger(__name__)

# Constants matching the TypeScript implementation
GEMINI_CONFIG_DIR = ".gemini"
DEFAULT_CONTEXT_FILENAME = "GEMINI.md"
MEMORY_SECTION_HEADER = "## Gemini Added Memories"
ENABLE_COMMON_FILE_SYSTEM = False

# Access time behavior configuration (mirrors real filesystem mount options)
ACCESS_TIME_MODE = "relatime"  # Options: "atime", "noatime", "relatime"
# - "atime": Update on every access (performance heavy, like traditional Unix)
# - "noatime": Never update access time (modern performance optimization)
# - "relatime": Update only if atime is older than mtime/ctime (modern default)

# Global variable to hold the currently configured filename
_current_gemini_md_filename = DEFAULT_CONTEXT_FILENAME

DEFAULT_IGNORE_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    "build",
    "dist",
    "coverage",
    ".pytest_cache",
    ".idea",
    ".vscode",
}

DEFAULT_IGNORE_FILE_PATTERNS = {
    "*.pyc",
    "*.pyo",
    "*.o",
    "*.so",
    "*.dll",
    "*.exe",
    "*.log",
    "*.tmp",
    "*.temp",
    "*.swp",
    "*.swo",
}

MAX_FILE_SIZE_TO_LOAD_CONTENT_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_TO_LOAD_CONTENT_MB * 1024 * 1024

BINARY_CONTENT_PLACEHOLDER = ["<Binary File - Content Not Loaded>"]
LARGE_FILE_CONTENT_PLACEHOLDER = [
    f"<File Exceeds {MAX_FILE_SIZE_TO_LOAD_CONTENT_MB}MB - Content Not Loaded>"
]

ERROR_READING_CONTENT_PLACEHOLDER = ["<Error Reading File Content>"]

# Archive file extensions that should have their binary content preserved
# These files need to be accessible as actual binary data for archive operations
ARCHIVE_EXTENSIONS = {".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar"}

# Maximum size for archive files to preserve binary content (smaller than general binary limit)
MAX_ARCHIVE_SIZE_MB = 10
MAX_ARCHIVE_SIZE_BYTES = MAX_ARCHIVE_SIZE_MB * 1024 * 1024

# Common file system configuration
common_directory = '/content'  # Must be set explicitly when using gemini_cli

def set_enable_common_file_system(enable: bool) -> None:
    """Sets the enable_common_file_system flag.
    
    Args:
        enable (bool): Whether to enable the common file system.
        
    Raises:
        ValueError: If enable is not a boolean.
    """
    global ENABLE_COMMON_FILE_SYSTEM
    if not isinstance(enable, bool):
        raise ValueError("enable must be a boolean")
    ENABLE_COMMON_FILE_SYSTEM = enable


def update_common_directory(new_directory: str) -> None:
    """Update the common directory path and immediately hydrate DB from it.

    Args:
        new_directory (str): The new absolute path for the common directory.

    Raises:
        InvalidInputError: If the path is not absolute, invalid, or doesn't exist.
        RuntimeError: If hydration fails after setting the directory.
    """
    global common_directory
    if not isinstance(new_directory, str) or not new_directory.strip():
        raise InvalidInputError("Common directory path must be a non-empty string")

    # NORMALIZE the path first
    normalized_directory = _normalize_path_for_db(new_directory.strip())
    
    if not os.path.isabs(normalized_directory):
        raise InvalidInputError("Common directory must be an absolute path")

    # Validate that the directory exists - don't auto-create
    if not os.path.exists(normalized_directory):
        raise InvalidInputError(f"Common directory '{normalized_directory}' does not exist")

    if not os.path.isdir(normalized_directory):
        raise InvalidInputError(f"Common directory '{normalized_directory}' is not a directory")

    # Validate that the directory is writable
    if not os.access(normalized_directory, os.W_OK):
        raise InvalidInputError(f"Common directory '{normalized_directory}' is not writable")

    # Update common directory with normalized path
    old_common_directory = common_directory
    common_directory = normalized_directory

    # CRITICAL: Update DB workspace_root and cwd to match normalized common_directory
    DB["workspace_root"] = normalized_directory
    DB["cwd"] = normalized_directory

    logger.info(f"Common directory updated from '{old_common_directory}' to: {normalized_directory}")
    logger.info(f"DB workspace_root and cwd synced to: {normalized_directory}")

    # IMMEDIATELY HYDRATE DB FROM THE NEW COMMON DIRECTORY
    try:
        logger.info(f"Immediately hydrating DB from new common directory: {normalized_directory}")
        hydrate_file_system_from_common_directory()
        logger.info("DB successfully hydrated from new common directory")
        
        # Log what was loaded
        file_system = DB.get("file_system", {})
        git_paths = [path for path in file_system.keys() if "/.git" in path or path.endswith("/.git")]
        
        if git_paths:
            logger.info(f"Loaded {len(file_system)} items including {len(git_paths)} .git paths")
        else:
            logger.info(f"Loaded {len(file_system)} items (no .git repository found)")
            
    except FileNotFoundError as e:
        # If hydration fails due to directory issues, revert the common directory
        common_directory = old_common_directory
        if old_common_directory:
            DB["workspace_root"] = old_common_directory
            DB["cwd"] = old_common_directory
        else:
            # Clear DB if no previous directory
            DB["workspace_root"] = ""
            DB["cwd"] = ""
            DB["file_system"] = {}
        
        error_msg = f"Failed to hydrate DB from new common directory '{normalized_directory}': {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
        
    except Exception as e:
        # For other hydration errors, also revert
        common_directory = old_common_directory
        if old_common_directory:
            DB["workspace_root"] = old_common_directory  
            DB["cwd"] = old_common_directory
        else:
            DB["workspace_root"] = ""
            DB["cwd"] = ""
            DB["file_system"] = {}
            
        error_msg = f"Failed to hydrate DB from new common directory '{normalized_directory}': {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def get_common_directory() -> str:
    """Get the current common directory path.

    Returns:
        str: The current common directory path.

    Raises:
        RuntimeError: If no common directory has been set.
    """
    if common_directory is None:
        raise RuntimeError(
            "No common directory has been set. Call update_common_directory() first."
        )
    return common_directory


def hydrate_file_system_from_common_directory() -> None:
    """Hydrate only file_system from the common directory, preserve workspace_root/cwd alignment.

    This function:
    1. Loads only the file system state from the common directory using existing hydrate function
    2. Ensures workspace_root and cwd remain aligned with common_directory (not contradictory)
    3. Preserves other DB data (memory_storage, tool_metrics, etc.)
    4. Removes unused background_processes if present

    Raises:
        FileNotFoundError: If the common directory doesn't exist.
        RuntimeError: For other errors during hydration.
    """
    current_common_dir = get_common_directory()
    if not os.path.exists(current_common_dir):
        raise FileNotFoundError(f"Common directory not found: {current_common_dir}")

    if not os.path.isdir(current_common_dir):
        raise FileNotFoundError(
            f"Common directory path is not a directory: {current_common_dir}"
        )

    try:
        # Store non-file-system data to preserve it
        preserved_data = {}
        for key in DB.keys():
            if key not in [
                "file_system",
                "workspace_root",
                "cwd",
                "background_processes",
            ]:
                preserved_data[key] = DB[key]

        # Use existing hydrate function to load file system
        # This will set workspace_root and cwd to common_directory automatically
        hydrate_db_from_directory(DB, current_common_dir)

        # Verify that workspace_root and cwd are correctly set to common_directory
        if DB.get("workspace_root") != current_common_dir:
            raise RuntimeError(
                f"Hydration set workspace_root to {DB.get('workspace_root')} instead of {current_common_dir}"
            )
        if DB.get("cwd") != current_common_dir:
            raise RuntimeError(
                f"Hydration set cwd to {DB.get('cwd')} instead of {current_common_dir}"
            )

        # Restore preserved data (memory_storage, tool_metrics, etc.)
        for key, value in preserved_data.items():
            DB[key] = value

        # Remove background_processes if it exists (cleanup)
        if "background_processes" in DB:
            del DB["background_processes"]

        logger.info(f"File system hydrated from common directory: {current_common_dir}")
        logger.info(f"Workspace_root and cwd correctly aligned with common directory")
        logger.info(f"Preserved non-file-system data: {list(preserved_data.keys())}")

    except Exception as e:
        raise RuntimeError(
            f"Failed to hydrate file system from common directory '{current_common_dir}': {e}"
        ) from e


def dehydrate_file_system_to_common_directory() -> None:
    """Dehydrate only file_system to the common directory, maintain workspace_root/cwd alignment.

    This function:
    1. Saves only the file system state to the common directory using safe dehydrate function
    2. Ensures workspace_root and cwd remain aligned with common directory after dehydration
    3. Does NOT save memory_storage or other non-file-system data
    4. Safely handles git repositories without destructive operations

    Raises:
        RuntimeError: If dehydration fails.
    """
    try:
        current_common_dir = get_common_directory()

        # CLEAN-AND-RECREATE: Remove existing directory contents first
        if os.path.exists(current_common_dir):
            # Remove all contents but preserve the directory itself
            # EXCEPT preserve .git directory if it exists
            for item in os.listdir(current_common_dir):
                item_path = os.path.join(current_common_dir, item)
                
                # Skip .git directory to preserve git history
                if item == ".git":
                    _log_util_message(logging.INFO, f"Preserving .git directory during cleanup: {item_path}")
                    continue
                    
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)

        # Create a temporary DB with only file_system data for dehydration
        temp_db = {
            "workspace_root": current_common_dir,
            "cwd": current_common_dir,
            "file_system": DB.get("file_system", {})
        }

        # Use SAFE dehydrate function with clean file_system-only data
        # This handles all the complexity of writing files correctly AND preserves git safely
        dehydrate_db_to_directory(temp_db, current_common_dir)

        # CRITICAL: Ensure the main DB workspace_root and cwd remain aligned with common_directory
        DB["workspace_root"] = current_common_dir
        DB["cwd"] = current_common_dir

        # Verify alignment
        if DB.get("workspace_root") != current_common_dir:
            raise RuntimeError(
                f"After dehydration, workspace_root is {DB.get('workspace_root')} instead of {current_common_dir}"
            )
        if DB.get("cwd") != current_common_dir:
            raise RuntimeError(
                f"After dehydration, cwd is {DB.get('cwd')} instead of {current_common_dir}"
            )

        logger.info(f"File system safely dehydrated to common directory: {current_common_dir}")
        logger.info(f"Workspace_root and cwd maintained alignment with common directory")
        logger.info(f"Git repository preserved safely during dehydration")

    except Exception as e:
        raise RuntimeError(
            f"Failed to dehydrate file system to common directory '{current_common_dir}': {e}"
        ) from e


def with_common_file_system(func):
    """Decorator to sync file_system with common directory before/after operations.

    This decorator ensures that:
    1. Before the function executes, the DB's file_system is hydrated from the common directory
    2. The original function is executed with the current state
    3. After the function executes, the DB's file_system is dehydrated back to the common directory

    Only the 'file_system' part of the DB is synced, other data remains unchanged.

    Args:
        func: The function to wrap with common file system synchronization.

    Returns:
        The wrapped function that automatically syncs file_system with common directory.

    Raises:
        FileNotFoundError: If common directory is unavailable during hydration.
        RuntimeError: If hydration or dehydration fails.
    """

    def wrapper(*args, **kwargs):
        if not ENABLE_COMMON_FILE_SYSTEM:
            return func(*args, **kwargs)
        try:
            # Hydrate file_system from common directory before operation
            _log_util_message(
                logging.DEBUG,
                f"Hydrating file_system from common directory before {func.__name__}",
            )
            hydrate_file_system_from_common_directory()

            # Execute the original function
            result = func(*args, **kwargs)

            # Dehydrate file_system to common directory after operation
            _log_util_message(
                logging.DEBUG,
                f"Dehydrating file_system to common directory after {func.__name__}",
            )
            dehydrate_file_system_to_common_directory()

            return result

        except FileNotFoundError as e:
            # Re-raise FileNotFoundError to skip function execution
            _log_util_message(
                logging.ERROR, f"Common directory unavailable for {func.__name__}: {e}"
            )
            raise e
        except Exception as e:
            # Log other errors but still re-raise
            _log_util_message(
                logging.ERROR,
                f"Error in common file system sync for {func.__name__}: {e}",
            )
            raise e

    # Preserve function metadata
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__module__ = func.__module__

    return wrapper


def _log_util_message(level: int, message: str, exc_info: bool = False) -> None:
    """
    Logs a message with information about the function within utils.py that called it.
    """
    log_message = message
    try:
        # Navigates up the call stack to find the frame of the function in utils.py
        # that called this _log_util_message helper.
        frame = inspect.currentframe()
        caller_frame = frame.f_back  # Frame of the direct caller within utils.py
        if caller_frame and caller_frame.f_code:
            func_name = caller_frame.f_code.co_name
            line_no = caller_frame.f_lineno
            log_message = f"{func_name}:{line_no} - {message}"
    except Exception:  # Fallback if frame inspection fails.
        pass

    # Log using the standard logging levels; default to DEBUG.
    if level == logging.ERROR:
        logger.error(log_message, exc_info=exc_info)
    elif level == logging.WARNING:
        logger.warning(log_message, exc_info=exc_info)
    elif level == logging.INFO:
        logger.info(log_message)
    else:
        logger.debug(log_message)  # Default log level is DEBUG.


def set_gemini_md_filename(new_filename: str) -> None:
    """Set the filename for the GEMINI.md context file.

    Args:
        new_filename (str): The new filename to use for the context file.
    """
    global _current_gemini_md_filename
    if new_filename and new_filename.strip():
        _current_gemini_md_filename = new_filename.strip()


def get_current_gemini_md_filename() -> str:
    """Get the current GEMINI.md filename.

    Returns:
        str: The current filename for the context file.
    """
    return _current_gemini_md_filename


def _get_home_directory() -> str:
    """Get the home directory from the workspace or use a default.

    Returns:
        str: The home directory path.
    """
    workspace_root = DB.get("workspace_root")
    if workspace_root:
        # In simulation, use the workspace root as the base for home directory
        return workspace_root
    return "/home/user"


def _get_global_memory_file_path() -> str:
    """Get the full path to the global memory file.

    Returns:
        str: The absolute path to the memory file.
    """
    home_dir = _get_home_directory()
    return os.path.join(home_dir, GEMINI_CONFIG_DIR, get_current_gemini_md_filename())


def _ensure_newline_separation(current_content: str) -> str:
    """Ensure proper newline separation before appending content.

    Args:
        current_content (str): The current content of the file.

    Returns:
        str: The appropriate separator string.
    """
    if not current_content:
        return ""
    if current_content.endswith("\n\n") or current_content.endswith("\r\n\r\n"):
        return ""
    if current_content.endswith("\n") or current_content.endswith("\r\n"):
        return "\n"
    return "\n\n"


def _persist_db_state():
    """Persist the current DB state to the default JSON file."""
    # Skip persistence during testing to avoid modifying the real database
    if _is_test_environment():
        return

    try:
        from .db import save_state, _DEFAULT_DB_PATH

        save_state(_DEFAULT_DB_PATH)
    except Exception as e:
        # Log the error but don't break the main functionality
        print_log(f"Warning: Could not persist DB state: {e}")


def _is_test_environment() -> bool:
    """Check if we're running in a test environment."""
    import sys
    import os

    # Check for common test runners
    if (
        "pytest" in sys.modules
        or "unittest" in sys.modules
        or "nose" in sys.modules
        or "nose2" in sys.modules
    ):
        return True

    # Check for test environment variables
    if (
        os.getenv("TESTING")
        or os.getenv("TEST_MODE")
        or os.getenv("PYTEST_CURRENT_TEST")
    ):
        return True

    # Check if running via pytest command
    if any("pytest" in arg or "test" in arg for arg in sys.argv):
        return True

    return False


def _is_common_file_system_enabled():
    """Check if common file system is enabled via environment variable.

    Returns True unless explicitly disabled by setting GEMINI_CLI_ENABLE_COMMON_FILE_SYSTEM to 'false'.
    """
    env_value = os.environ.get("GEMINI_CLI_ENABLE_COMMON_FILE_SYSTEM")
    if env_value is None:
        return True  # Default enabled when variable doesn't exist
    return env_value.lower() != "false"  # Disabled only when explicitly set to 'false'


def conditional_common_file_system_wrapper(func):
    """Wrapper that conditionally applies common file system based on runtime environment variable."""

    def wrapper(*args, **kwargs):
        if _is_common_file_system_enabled():
            # Apply the common file system wrapper at runtime
            wrapped_func = with_common_file_system(func)
            return wrapped_func(*args, **kwargs)
        else:
            # Call the original function directly
            return func(*args, **kwargs)

    # Preserve function metadata
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__module__ = func.__module__
    return wrapper


@log_complexity
def get_memories(limit: Optional[int] = None) -> Dict[str, Any]:
    """Retrieve saved memories from the memory file.

    Args:
        limit (Optional[int]): Maximum number of memories to retrieve.
                              If None, returns all memories.

    Returns:
        Dict[str, Any]: A dictionary indicating the outcome:
            - 'success' (bool): True if the memories were retrieved successfully.
            - 'memories' (List[str]): List of retrieved memory items.
            - 'message' (str): A message describing the outcome.

    Raises:
        InvalidInputError: If limit is not a positive integer.
        WorkspaceNotAvailableError: If workspace_root is not configured.
    """
    # Validate input
    if limit is not None and (not isinstance(limit, int) or limit <= 0):
        raise InvalidInputError("Parameter 'limit' must be a positive integer or None.")

    # Check workspace configuration
    workspace_root = DB.get("workspace_root")
    if not workspace_root:
        raise WorkspaceNotAvailableError("workspace_root not configured in DB")

    try:
        memory_file_path = _get_global_memory_file_path()
        memory_storage = DB.get("memory_storage", {})

        # Check if memory file exists
        if memory_file_path not in memory_storage:
            return {
                "success": True,
                "memories": [],
                "message": "No memories found. Memory file does not exist.",
            }

        # Read the memory file
        content_lines = memory_storage[memory_file_path].get("content_lines", [])
        content = "".join(content_lines)

        # Extract memories from the content
        memories = []
        header_index = content.find(MEMORY_SECTION_HEADER)

        if header_index != -1:
            start_of_section_content = header_index + len(MEMORY_SECTION_HEADER)
            end_of_section_index = content.find("\n## ", start_of_section_content)
            if end_of_section_index == -1:
                end_of_section_index = len(content)

            section_content = content[start_of_section_content:end_of_section_index]

            # Parse memory items (lines starting with '- ')
            for line in section_content.split("\n"):
                line = line.strip()
                if line.startswith("- "):
                    memory_text = line[2:].strip()  # Remove '- ' prefix
                    if memory_text:
                        memories.append(memory_text)

        # Apply limit if specified
        if limit is not None:
            memories = memories[:limit]

        return {
            "success": True,
            "memories": memories,
            "message": f"Retrieved {len(memories)} memories.",
        }

    except Exception as error:
        error_message = f"Failed to retrieve memories: {str(error)}"
        return {"success": False, "memories": [], "message": error_message}


@log_complexity
def clear_memories() -> Dict[str, Any]:
    """Clear all saved memories by removing the memory section.

    Returns:
        Dict[str, Any]: A dictionary indicating the outcome:
            - 'success' (bool): True if the memories were cleared successfully.
            - 'message' (str): A message describing the outcome.

    Raises:
        WorkspaceNotAvailableError: If workspace_root is not configured.
    """
    # Check workspace configuration
    workspace_root = DB.get("workspace_root")
    if not workspace_root:
        raise WorkspaceNotAvailableError("workspace_root not configured in DB")

    try:
        memory_file_path = _get_global_memory_file_path()
        memory_storage = DB.get("memory_storage", {})

        # Check if memory file exists
        if memory_file_path not in memory_storage:
            return {
                "success": True,
                "message": "No memories to clear. Memory file does not exist.",
            }

        # Read the memory file
        content_lines = memory_storage[memory_file_path].get("content_lines", [])
        content = "".join(content_lines)

        # Remove the memory section
        header_index = content.find(MEMORY_SECTION_HEADER)

        if header_index != -1:
            start_of_section = header_index
            end_of_section_index = content.find(
                "\n## ", header_index + len(MEMORY_SECTION_HEADER)
            )
            if end_of_section_index == -1:
                end_of_section_index = len(content)

            # Remove the entire memory section
            new_content = content[:start_of_section] + content[end_of_section_index:]
            new_content = new_content.rstrip() + "\n" if new_content.strip() else ""

            # Update the memory storage entry
            if new_content.strip():
                content_lines = new_content.splitlines(keepends=True)
                if content_lines and not content_lines[-1].endswith("\n"):
                    content_lines[-1] += "\n"

                memory_storage[memory_file_path]["content_lines"] = content_lines
                memory_storage[memory_file_path]["size_bytes"] = len(
                    new_content.encode("utf-8")
                )
                memory_storage[memory_file_path][
                    "last_modified"
                ] = "2025-01-01T00:00:00Z"
            else:
                # If file is empty, remove it
                del memory_storage[memory_file_path]

            _persist_db_state()

            return {"success": True, "message": "All memories have been cleared."}
        else:
            return {"success": True, "message": "No memories found to clear."}

    except Exception as error:
        error_message = f"Failed to clear memories: {str(error)}"
        return {"success": False, "message": error_message}


@log_complexity
def update_memory_by_content(old_fact: str, new_fact: str) -> Dict[str, Any]:
    """Update a specific memory by replacing old content with new content.

    Args:
        old_fact (str): The existing fact to replace.
        new_fact (str): The new fact to replace it with.

    Returns:
        Dict[str, Any]: A dictionary indicating the outcome:
            - 'success' (bool): True if the memory was updated successfully.
            - 'message' (str): A message describing the outcome.

    Raises:
        InvalidInputError: If either fact is empty or not a string.
        WorkspaceNotAvailableError: If workspace_root is not configured.
    """
    # Validate input
    if not isinstance(old_fact, str) or not old_fact.strip():
        raise InvalidInputError("Parameter 'old_fact' must be a non-empty string.")

    if not isinstance(new_fact, str) or not new_fact.strip():
        raise InvalidInputError("Parameter 'new_fact' must be a non-empty string.")

    # Check workspace configuration
    workspace_root = DB.get("workspace_root")
    if not workspace_root:
        raise WorkspaceNotAvailableError("workspace_root not configured in DB")

    try:
        memory_file_path = _get_global_memory_file_path()
        memory_storage = DB.get("memory_storage", {})

        # Check if memory file exists
        if memory_file_path not in memory_storage:
            return {
                "success": False,
                "message": "No memories found. Memory file does not exist.",
            }

        # Read the memory file
        content_lines = memory_storage[memory_file_path].get("content_lines", [])
        content = "".join(content_lines)

        # Find and replace the specific memory
        old_memory_item = f"- {old_fact.strip()}"
        new_memory_item = f"- {new_fact.strip()}"

        if old_memory_item in content:
            updated_content = content.replace(old_memory_item, new_memory_item)

            # Update the memory storage entry
            content_lines = updated_content.splitlines(keepends=True)
            if content_lines and not content_lines[-1].endswith("\n"):
                content_lines[-1] += "\n"

            memory_storage[memory_file_path]["content_lines"] = content_lines
            memory_storage[memory_file_path]["size_bytes"] = len(
                updated_content.encode("utf-8")
            )
            memory_storage[memory_file_path]["last_modified"] = "2025-01-01T00:00:00Z"

            _persist_db_state()

            return {
                "success": True,
                "message": f'Memory updated successfully: "{old_fact}" -> "{new_fact}"',
            }
        else:
            return {"success": False, "message": f'Memory not found: "{old_fact}"'}

    except Exception as error:
        error_message = f"Failed to update memory: {str(error)}"
        return {"success": False, "message": error_message}


def normalize_command_paths(command: str, workspace_root: str) -> str:
    """
    Normalize file paths in shell commands to be relative to workspace root.

    Converts absolute paths within workspace to relative paths, while preserving
    command structure and handling quoted arguments correctly.

    Args:
        command (str): The shell command containing potentially absolute paths
        workspace_root (str): The workspace root path to strip from absolute paths

    Returns:
        str: Command with absolute workspace paths converted to relative paths

    Raises:
        ShellSecurityError: If command contains paths outside workspace that would be dangerous
    """
    from .custom_errors import ShellSecurityError
    import shlex
    import re

    if not command or not command.strip():
        return command

    workspace_root_norm = _normalize_path_for_db(workspace_root)
    if not workspace_root_norm.endswith("/"):
        workspace_root_norm += "/"

    # Handle quoted strings separately to avoid breaking them
    def process_token(token):
        # Skip if token is clearly a flag (starts with -)
        if token.startswith("-"):
            return token

        # Check if token looks like a path (contains / or is a filename)
        if "/" not in token and not any(
            token.endswith(ext)
            for ext in [".txt", ".py", ".md", ".json", ".yaml", ".yml", ".sh"]
        ):
            return token

        # Normalize the token path
        token_norm = _normalize_path_for_db(token)

        # If it's an absolute path
        if os.path.isabs(token_norm):
            # Check if it's within workspace - if yes, convert to relative
            if token_norm.startswith(workspace_root_norm) or token_norm == workspace_root_norm.rstrip("/"):
                # Convert to relative path
                if token_norm == workspace_root_norm.rstrip("/"):
                    return "."
                else:
                    rel_path = token_norm[len(workspace_root_norm):]
                    return rel_path if rel_path else "."
            
            # For paths outside workspace, DON'T throw an error here
            # Let the command execution handle it (it might fail naturally or be handled by internal commands)
            # Only throw security error for obviously dangerous patterns
            dangerous_outside_patterns = [
                "/etc/passwd", "/etc/shadow", "/etc/hosts",
                "/dev/", "/proc/", "/sys/",
                "/usr/bin/", "/bin/", "/sbin/",
                "/root/", "/home/"  # But not specific subdirectories
            ]
            
            # Only block clearly dangerous system paths
            for dangerous in dangerous_outside_patterns:
                if token_norm.startswith(dangerous):
                    raise ShellSecurityError(f"Access to system path not allowed: {token}")
            
            # For other outside paths (like test paths), leave them as-is
            # The command execution will handle the failure appropriately
            return token

        return token

    # Split command while preserving quoted strings
    try:
        tokens = shlex.split(command)
        processed_tokens = [process_token(token) for token in tokens]
        return shlex.join(processed_tokens)
    except ValueError:
        # Fallback for commands with unmatched quotes - use regex approach
        def replace_paths(match):
            path = match.group(0)
            return process_token(path)

        # Simple regex to find path-like strings (be conservative)
        path_pattern = r"(?:^|\s)([/][\w\-./]+|[\w\-./]*[/][\w\-./]*)"
        try:
            return re.sub(path_pattern, replace_paths, command)
        except Exception:
            # If regex replacement fails, return original command
            return command

# Shell utility functions
def validate_command_security(command: str) -> None:
    """Validate command for security issues.

    Args:
        command (str): The shell command to validate.

    Raises:
        ShellSecurityError: If the command contains security risks.
        InvalidInputError: If the command is invalid.
    """
    from .custom_errors import ShellSecurityError

    if not isinstance(command, str):
        raise InvalidInputError("Command must be a string")

    if not command.strip():
        raise InvalidInputError("Command cannot be empty")

    # Block command substitution for security
    if '$(' in command:
        raise ShellSecurityError("Command substitution using $() is not allowed for security reasons")
    
    # Block potentially dangerous patterns from DB configuration
    shell_config = DB.get("shell_config", {})
    dangerous_patterns = shell_config.get("dangerous_patterns", [])
    
    # Normalize whitespace for better pattern matching
    import re

    command_normalized = re.sub(r"\s+", " ", command.lower().strip())

    for pattern in dangerous_patterns:
        pattern_normalized = re.sub(r"\s+", " ", pattern.lower().strip())
        if pattern_normalized in command_normalized:
            raise ShellSecurityError(f"Command contains dangerous pattern: {pattern}")


def get_command_restrictions() -> Dict[str, List[str]]:
    """Get command restrictions from database configuration.

    Returns:
        Dict[str, List[str]]: Dictionary with 'allowed' and 'blocked' command lists.
    """
    shell_config = DB.get("shell_config", {})
    return {
        "allowed": shell_config.get("allowed_commands", []),
        "blocked": shell_config.get("blocked_commands", []),
    }


def update_dangerous_patterns(patterns: List[str]) -> Dict[str, Any]:
    """Update dangerous patterns in the shell configuration.
    
    Args:
        patterns (List[str]): List of dangerous patterns to block.
                             Empty list means no patterns will be blocked.
    
    Returns:
        Dict[str, Any]: A dictionary indicating the outcome:
            - 'success' (bool): True if patterns were updated successfully.
            - 'message' (str): A message describing the outcome.
            - 'patterns' (List[str]): The updated patterns list.
    
    Raises:
        InvalidInputError: If patterns is not a list or contains invalid items.
    """
    if not isinstance(patterns, list):
        raise InvalidInputError("Parameter 'patterns' must be a list")
    
    # Validate each pattern is a string
    for i, pattern in enumerate(patterns):
        if not isinstance(pattern, str):
            raise InvalidInputError(f"Pattern at index {i} must be a string, got {type(pattern).__name__}")
        if not pattern.strip():
            raise InvalidInputError(f"Pattern at index {i} cannot be empty")
    
    try:
        # Get current shell config or create if it doesn't exist
        shell_config = DB.get("shell_config", {})
        
        # Update dangerous patterns
        shell_config["dangerous_patterns"] = patterns.copy()
        
        # Update DB
        DB["shell_config"] = shell_config
        
        _log_util_message(logging.INFO, f"Updated dangerous patterns: {patterns}")
        
        return {
            "success": True,
            "message": f"Successfully updated {len(patterns)} dangerous patterns",
            "patterns": patterns.copy()
        }
        
    except Exception as e:
        error_message = f"Failed to update dangerous patterns: {str(e)}"
        _log_util_message(logging.ERROR, error_message)
        return {
            "success": False,
            "message": error_message,
            "patterns": []
        }


def get_dangerous_patterns() -> List[str]:
    """Get current dangerous patterns from shell configuration.
    
    Returns:
        List[str]: List of currently configured dangerous patterns.
    """
    shell_config = DB.get("shell_config", {})
    return shell_config.get("dangerous_patterns", []).copy()


def is_command_allowed(command: str) -> bool:
    """Check if a command is allowed based on configuration.

    Args:
        command (str): The command to check.

    Returns:
        bool: True if the command is allowed, False otherwise.
    """
    import shlex

    restrictions = get_command_restrictions()
    allowed_commands = restrictions["allowed"]
    blocked_commands = restrictions["blocked"]

    # Extract the root command (first word)
    try:
        command_parts = shlex.split(command.strip())
        if not command_parts:
            return False
        root_command = command_parts[0]
    except ValueError:
        return False

    # Check blocklist first (takes precedence)
    for blocked in blocked_commands:
        if root_command.startswith(blocked):
            return False

    # If there are specific allowed commands, check allowlist
    if allowed_commands:
        for allowed in allowed_commands:
            if root_command.startswith(allowed):
                return True
        return False  # Not in allowlist

    # If no specific restrictions, allow by default
    return True


def normalize_simulated_path(path: str) -> str:
    """Normalize path for simulated filesystem (always use forward slashes)."""
    if not path:
        return path
    # Convert to forward slashes for simulated filesystem consistency
    return path.replace("\\", "/")


def handle_internal_commands(command: str) -> Optional[Dict[str, Any]]:
    """Handle internal commands like cd, pwd that don't need external execution.

    Args:
        command (str): The command to check and potentially handle.

    Returns:
        Optional[Dict[str, Any]]: Result dict if handled internally, None otherwise.
    """
    from .custom_errors import ShellSecurityError
    
    workspace_root = DB.get("workspace_root", "")
    current_cwd = DB.get("cwd", workspace_root)

    # Normalize paths for simulated filesystem
    workspace_root = _normalize_path_for_db(workspace_root)
    current_cwd = _normalize_path_for_db(current_cwd)

    stripped_command = command.strip()

    # Handle pwd
    if stripped_command == "pwd":
        return {
            "command": command,
            "directory": current_cwd,
            "stdout": current_cwd,
            "stderr": "",
            "returncode": 0,
            "pid": None,
            "signal": None,
            "process_group_id": None,
            "message": f"Current directory: {current_cwd}",
        }

    # Handle cd
    if stripped_command == "cd" or stripped_command.startswith("cd "):
        parts = stripped_command.split(maxsplit=1)
        target = parts[1] if len(parts) > 1 else "/"  # Default 'cd' target

        # Use the more robust resolve_target_path_for_cd function
        new_cwd_path = resolve_target_path_for_cd(
            current_cwd,
            target,
            workspace_root,
            DB.get("file_system", {})
        )
        
        if new_cwd_path:
            DB["cwd"] = new_cwd_path  # Update current working directory state
            return {
                "command": command,
                "directory": new_cwd_path,
                "stdout": "",
                "stderr": "",
                "returncode": 0,
                "pid": None,
                "signal": None,
                "process_group_id": None,
                "message": f"Changed directory to: {new_cwd_path}",
            }
        else:
            return {
                "command": command,
                "directory": current_cwd,
                "stdout": "",
                "stderr": f"cd: '{target}': No such directory",
                "returncode": 1,
                "pid": None,
                "signal": None,
                "process_group_id": None,
                "message": f"Failed to change directory: path may be invalid or outside workspace",
            }

    # Handle env
    if stripped_command == "env":
        shell_config = DB.get("shell_config", {})
        env_vars = shell_config.get("environment_variables", {})

        output_lines = []
        for key, value in env_vars.items():
            output_lines.append(f"{key}={value}")

        output = "\n".join(output_lines)
        if output:
            output += "\n"

        return {
            "command": command,
            "directory": current_cwd,
            "stdout": output,
            "stderr": "",
            "returncode": 0,
            "pid": None,
            "signal": None,
            "process_group_id": None,
            "message": f"Environment variables: {len(env_vars)} variables",
        }

    # Not an internal command
    return None

def setup_execution_environment(target_directory: Optional[str] = None) -> str:
    """Set up a temporary execution environment with workspace contents.

    Args:
        target_directory (Optional[str]): Target directory for execution.

    Returns:
        str: Path to the temporary execution environment.

    Raises:
        WorkspaceNotAvailableError: If workspace setup fails.
    """
    import tempfile
    import shutil

    workspace_root = DB.get("workspace_root")
    if not workspace_root:
        raise WorkspaceNotAvailableError("workspace_root not configured in DB")

    # Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix="gemini_shell_")

    try:
        # Copy workspace contents to temp directory
        file_system = DB.get("file_system", {})

        for file_path, file_info in file_system.items():
            if not _is_within_workspace(file_path, workspace_root):
                continue

            relative_path = os.path.relpath(file_path, workspace_root)
            temp_file_path = os.path.join(temp_dir, relative_path)

            if file_info.get("is_directory", False):
                os.makedirs(temp_file_path, exist_ok=True)
            else:
                # Create parent directories
                os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)

                # Write file content
                content_lines = file_info.get("content_lines", [])
                content = "".join(content_lines)

                with open(temp_file_path, "w", encoding="utf-8", errors="replace") as f:
                    f.write(content)

        return temp_dir

    except Exception as e:
        # Cleanup on failure
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise WorkspaceNotAvailableError(f"Failed to setup execution environment: {e}")


def update_workspace_from_temp(temp_dir: str) -> None:
    """Update the workspace file system from temporary execution environment.

    Args:
        temp_dir (str): Path to the temporary execution environment.

    Raises:
        WorkspaceNotAvailableError: If workspace update fails.
    """
    import time

    workspace_root = DB.get("workspace_root", "")
    if not workspace_root:
        raise WorkspaceNotAvailableError("workspace_root not configured in DB")

    file_system = DB.setdefault("file_system", {})

    try:
        # Walk through temp directory and update file system
        for root, dirs, files in os.walk(temp_dir):
            for name in dirs + files:
                temp_path = os.path.join(root, name)
                relative_path = os.path.relpath(temp_path, temp_dir)

                # Convert back to absolute workspace path
                workspace_path = os.path.normpath(
                    os.path.join(workspace_root, relative_path)
                )

                # Only update files within workspace
                if not _is_within_workspace(workspace_path, workspace_root):
                    continue

                if os.path.isdir(temp_path):
                    file_system[workspace_path] = {
                        "path": workspace_path,
                        "is_directory": True,
                        "content_lines": [],
                        "size_bytes": 0,
                        "last_modified": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    }
                else:
                    try:
                        with open(
                            temp_path, "r", encoding="utf-8", errors="replace"
                        ) as f:
                            content = f.read()

                        content_lines = [line + "\n" for line in content.splitlines()]
                        if content and not content.endswith("\n"):
                            content_lines[-1] = content_lines[-1].rstrip("\n")

                        file_system[workspace_path] = {
                            "path": workspace_path,
                            "is_directory": False,
                            "content_lines": content_lines,
                            "size_bytes": len(content.encode("utf-8")),
                            "last_modified": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        }

                    except Exception as e:
                        # Log the error but continue with other files
                        print_log(f"Warning: Could not update file {workspace_path}: {e}")
                        continue

        # Persist the updated state
        _persist_db_state()

    except Exception as e:
        raise WorkspaceNotAvailableError(
            f"Failed to update workspace from temp directory: {e}"
        )


# Environment functions are now in env_manager.py


def get_shell_command(command: str) -> List[str]:
    """Get the appropriate shell command based on platform."""
    import platform

    if platform.system() == "Windows":
        return ["cmd.exe", "/c", command]
    else:
        return ["bash", "-c", command]


# ---------------------------------------------------------------------------
# Workspace ↔️ DB Hydration Helpers (mirrors terminal implementation)
# ---------------------------------------------------------------------------


def _collect_file_metadata(file_path: str) -> Dict[str, Any]:
    """Helper function to collect file metadata.

    Args:
        file_path (str): Path to the file to collect metadata from

    Returns:
        Dict[str, Any]: Dictionary containing the file's metadata

    Note:
        change_time (ctime) is collected for informational purposes but cannot be
        restored via _apply_file_metadata since it's managed by the filesystem kernel.
        Only access_time and modify_time can be set via os.utime().
    """
    try:
        stat_info = os.stat(file_path, follow_symlinks=False)

        # Get timestamps
        access_time = (
            datetime.datetime.fromtimestamp(
                stat_info.st_atime, tz=datetime.timezone.utc
            )
            .isoformat()
            .replace("+00:00", "Z")
        )
        modify_time = (
            datetime.datetime.fromtimestamp(
                stat_info.st_mtime, tz=datetime.timezone.utc
            )
            .isoformat()
            .replace("+00:00", "Z")
        )
        change_time = (
            datetime.datetime.fromtimestamp(
                stat_info.st_ctime, tz=datetime.timezone.utc
            )
            .isoformat()
            .replace("+00:00", "Z")
        )  # Cannot be restored, kernel-managed

        # Get file attributes
        is_symlink = os.path.islink(file_path)
        is_hidden = os.path.basename(file_path).startswith(".")

        metadata = {
            "attributes": {
                "is_symlink": is_symlink,
                "is_hidden": is_hidden,
                "is_readonly": not os.access(file_path, os.W_OK),
                "symlink_target": None,  # Initialize to None by default
            },
            "timestamps": {
                "access_time": access_time,
                "modify_time": modify_time,
                "change_time": change_time,
            },
            "permissions": {
                "mode": stat_info.st_mode & 0o777,
                "uid": stat_info.st_uid,
                "gid": stat_info.st_gid,
            },
        }

        # Add symlink target if it's a symlink
        if is_symlink:
            metadata["attributes"]["symlink_target"] = os.readlink(file_path)

        return metadata

    except (OSError, IOError) as e:
        logger.warning(f"Error collecting metadata for '{file_path}': {e}")
        return {
            "attributes": {
                "is_symlink": False,
                "is_hidden": False,
                "is_readonly": False,
                "symlink_target": None,  # Initialize to None in error case
            },
            "timestamps": {
                "access_time": get_current_timestamp_iso(),
                "modify_time": get_current_timestamp_iso(),
                "change_time": get_current_timestamp_iso(),
            },
            "permissions": {
                "mode": 0o644,
                "uid": os.getuid() if hasattr(os, "getuid") else 1000,
                "gid": os.getgid() if hasattr(os, "getgid") else 1000,
            },
        }


def _apply_file_metadata(
    file_path: str, metadata: Dict[str, Any], strict_mode: bool = False
) -> None:
    """Helper function to apply file metadata.

    Args:
        file_path (str): Path to the file to apply metadata to
        metadata (Dict[str, Any]): Metadata to apply
        strict_mode (bool): Whether to raise errors on metadata application failures
    """
    try:
        # Apply permissions (mode, uid, gid) if present
        permissions = metadata.get("permissions", {})
        if permissions and os.path.exists(file_path) and not os.path.islink(file_path):
            mode = permissions.get("mode")
            uid = permissions.get("uid")
            gid = permissions.get("gid")
            try:
                if mode is not None:
                    os.chmod(file_path, mode)
            except Exception as e:
                logger.warning(f"Could not set mode for '{file_path}': {e}")
            try:
                if uid is not None and gid is not None:
                    os.chown(file_path, uid, gid)
            except Exception as e:
                logger.warning(f"Could not set ownership for '{file_path}': {e}")
        # Apply timestamps - restore access_time and modify_time normally during hydration
        timestamps = metadata.get("timestamps", {})
        if timestamps:
            current_time = time.time()

            # Restore modify_time if available
            mtime = current_time
            if "modify_time" in timestamps:
                try:
                    mtime = datetime.datetime.fromisoformat(
                        timestamps["modify_time"].replace("Z", "+00:00")
                    ).timestamp()
                except Exception:
                    pass

            # Restore access_time if available
            atime = current_time
            if "access_time" in timestamps:
                try:
                    atime = datetime.datetime.fromisoformat(
                        timestamps["access_time"].replace("Z", "+00:00")
                    ).timestamp()
                except Exception:
                    atime = mtime  # Fallback to mtime
            else:
                atime = mtime

            # Apply the timestamps normally
            os.utime(file_path, (atime, mtime), follow_symlinks=False)

        # Apply read-only attribute
        attrs = metadata.get("attributes", {})
        if os.path.exists(file_path) and not os.path.islink(file_path):
            is_readonly = attrs.get("is_readonly", False)
            mode = os.stat(file_path).st_mode
            if is_readonly:
                # Remove write permissions for owner, group, others
                new_mode = mode & ~stat.S_IWUSR & ~stat.S_IWGRP & ~stat.S_IWOTH
                os.chmod(file_path, new_mode)
            else:
                # Add write permissions for owner (at least)
                new_mode = mode | stat.S_IWUSR
                os.chmod(file_path, new_mode)

        # Apply hidden attribute (Unix: ensure dot prefix)
        is_hidden = attrs.get("is_hidden", False)
        base = os.path.basename(file_path)
        dir_ = os.path.dirname(file_path)
        if is_hidden and not base.startswith(".") and os.path.exists(file_path):
            # Rename to add dot prefix
            new_path = os.path.join(dir_, "." + base)
            if not os.path.exists(new_path):
                os.rename(file_path, new_path)
        elif not is_hidden and base.startswith(".") and os.path.exists(file_path):
            # Optionally, rename to remove dot (not always safe, so skip)
            pass

    except (OSError, IOError) as e:
        msg = f"Error applying metadata to '{file_path}': {e}"
        if strict_mode:
            raise MetadataError(msg)
        else:
            logger.warning(msg)


def get_current_timestamp_iso() -> str:
    """Returns the current time in ISO 8601 format, UTC (suffixed with 'Z')."""
    return (
        datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    )


def _is_archive_file(filepath: str) -> bool:
    """
    Check if a file is an archive that should have its binary content preserved.

    Args:
        filepath (str): Path to the file

    Returns:
        bool: True if the file is an archive that should preserve binary content
    """
    if not filepath:
        return False

    # Get file extension
    _, ext = os.path.splitext(filepath.lower())

    # Handle compound extensions like .tar.gz, .tar.bz2, etc.
    if ext in {".gz", ".bz2", ".xz"} and filepath.lower().endswith(".tar" + ext):
        return True

    return ext in ARCHIVE_EXTENSIONS


def is_likely_binary_file(filepath, sample_size=1024):
    """
    Heuristic to guess if a file is binary.
    Checks for a significant number of null bytes or non-printable characters
    in a sample of the file. Also uses mimetypes.

    Args:
        filepath (str): Path to the file.
        sample_size (int): Number of bytes to sample from the beginning of the file.

    Returns:
        bool: True if the file is likely binary, False otherwise.
    """
    # Guess MIME type first, as it's often more reliable for known types
    mime_type, _ = mimetypes.guess_type(filepath)
    if mime_type:
        # Explicitly non-text types
        if not mime_type.startswith("text/") and mime_type not in (
            "application/json",
            "application/xml",
            "application/javascript",
            "application/x-sh",
            "application/x-python",
        ):  # Add other text-based app types
            # Consider 'inode/x-empty' as not binary for content loading
            if mime_type == "inode/x-empty":
                return False
            # application/octet-stream is a strong indicator of binary
            if mime_type == "application/octet-stream":
                return True
            # If it's a known non-text type (e.g. image, audio, video, common binary app types)
            # This helps with .zip, .exe, .pdf, .png etc.
            return True

    # Content-based heuristic (fallback or for ambiguous MIME types)
    try:
        with open(filepath, "rb") as f:
            sample = f.read(sample_size)
        if not sample:  # Empty file is not considered binary for content loading
            return False

        # Presence of null bytes is a strong indicator for many binary formats
        if b"\0" in sample:
            # A simple check for any null byte can be effective
            return True

        # Check for a high proportion of non-printable ASCII characters
        # (excluding common whitespace like tab, newline, carriage return)
        text_characters = "".join(map(chr, range(32, 127))) + "\n\r\t"
        non_printable_count = 0
        for byte_val in sample:  # Iterate over byte values (integers)
            if chr(byte_val) not in text_characters:
                non_printable_count += 1

        # If more than a certain percentage of characters are non-printable
        # This threshold might need tuning.
        if (
            len(sample) > 0 and (non_printable_count / len(sample)) > 0.30
        ):  # 30% non-printable
            logger.debug(
                f"File '{filepath}' deemed binary by content heuristic (non-printable ratio: {non_printable_count / len(sample):.2f})"
            )
            return True

    except (IOError, OSError) as e:
        # If we can't read it for heuristic, log it but don't assume binary.
        # The main read attempt in hydrate_db_from_directory will handle and log the read error.
        logger.debug(
            f"Could not perform content-based binary check for '{filepath}': {e}"
        )
        return False  # Default to not binary if heuristic check fails to read
    return False


def hydrate_db_from_directory(db_instance, directory_path):
    """
    Populates the provided db_instance's 'file_system' by recursively scanning
    a local directory structure. It sets the 'workspace_root' and 'cwd'
    to the normalized path of the scanned directory.

    Args:
        db_instance (dict): The application's database, modified in place.
        directory_path (str): Path to the root directory for hydration.

    Returns:
        bool: True if hydration completed successfully.

    Raises:
        FileNotFoundError: If `directory_path` does not exist or is not a directory.
        RuntimeError: For fatal, unrecoverable errors during hydration.
    """
    try:
        # Validate and Normalize Root Directory Path
        if not os.path.isdir(directory_path):
            msg = f"Root directory for hydration not found or is not a directory: '{directory_path}'"
            logger.error(msg)
            raise FileNotFoundError(msg)

        normalized_root_path = os.path.abspath(directory_path).replace("\\", "/")

        # Update Core DB Properties
        db_instance["workspace_root"] = normalized_root_path
        db_instance["cwd"] = normalized_root_path  # Default CWD to workspace root

        # Prepare file_system for New Data
        db_instance["file_system"] = {}

        logger.info(f"Starting hydration from workspace root: {normalized_root_path}")

        # Recursively Scan Directory Structure
        for dirpath, dirnames, filenames in os.walk(
            directory_path, topdown=True, onerror=logger.warning
        ):
            current_normalized_dirpath = os.path.abspath(dirpath).replace("\\", "/")

            logger.debug(
                f"Processing directory for DB entry: {current_normalized_dirpath}"
            )

            # Process the Current Directory (dirpath) Itself
            # Add current_normalized_dirpath to DB if it hasn't been added (os.walk might yield it multiple times if symlinks involved, though less common here)
            # and it's not an ignored component (already checked above for skipping).
            if current_normalized_dirpath not in db_instance["file_system"]:
                try:
                    mtime_timestamp = os.path.getmtime(dirpath)
                    last_modified_iso = (
                        datetime.datetime.fromtimestamp(
                            mtime_timestamp, tz=datetime.timezone.utc
                        )
                        .isoformat()
                        .replace("+00:00", "Z")
                    )

                    # Collect metadata for directory
                    dir_metadata = _collect_file_metadata(dirpath)

                    db_instance["file_system"][current_normalized_dirpath] = {
                        "path": current_normalized_dirpath,
                        "is_directory": True,
                        "content_lines": [],
                        "size_bytes": 0,
                        "last_modified": last_modified_iso,
                        "metadata": dir_metadata,  # Add metadata for directory
                    }
                    logger.debug(
                        f"Added directory entry with metadata to DB: {current_normalized_dirpath}"
                    )
                except Exception as e:
                    logger.warning(
                        f"Could not process directory metadata for '{current_normalized_dirpath}': {e}"
                    )
                    continue

            # Process Files (filenames) in the Current Directory
            for filename in filenames:
                file_full_path = os.path.join(dirpath, filename)
                normalized_file_path = os.path.abspath(file_full_path).replace(
                    "\\", "/"
                )

                logger.debug(f"Processing file for DB entry: {normalized_file_path}")

                content_lines = ERROR_READING_CONTENT_PLACEHOLDER
                size_bytes = 0
                last_modified_iso = get_current_timestamp_iso()  # Default

                try:
                    stat_info = os.stat(file_full_path)
                    size_bytes = stat_info.st_size
                    mtime_timestamp = stat_info.st_mtime
                    last_modified_iso = (
                        datetime.datetime.fromtimestamp(
                            mtime_timestamp, tz=datetime.timezone.utc
                        )
                        .isoformat()
                        .replace("+00:00", "Z")
                    )

                    # Collect metadata for file
                    file_metadata = _collect_file_metadata(file_full_path)

                    if size_bytes == 0:  # Handle empty files explicitly
                        content_lines = []
                        logger.debug(
                            f"File '{normalized_file_path}' is empty. Content set to []."
                        )
                    elif size_bytes > MAX_FILE_SIZE_BYTES:
                        logger.info(
                            f"File '{normalized_file_path}' ({size_bytes / (1024*1024):.2f}MB) exceeds max size {MAX_FILE_SIZE_TO_LOAD_CONTENT_MB}MB. Content not loaded."
                        )
                        content_lines = LARGE_FILE_CONTENT_PLACEHOLDER
                    elif (
                        _is_archive_file(file_full_path)
                        and size_bytes <= MAX_ARCHIVE_SIZE_BYTES
                    ):
                        # Special handling for archive files - store actual binary content
                        logger.info(
                            f"File '{normalized_file_path}' detected as archive. Storing binary content."
                        )
                        try:
                            with open(file_full_path, "rb") as f:
                                binary_content = f.read()

                            # Store binary content as base64-encoded strings to preserve it exactly
                            encoded_content = base64.b64encode(binary_content).decode(
                                "ascii"
                            )
                            # Split into chunks to avoid extremely long lines
                            chunk_size = 76  # Standard base64 line length
                            content_lines = [
                                encoded_content[i : i + chunk_size] + "\n"
                                for i in range(0, len(encoded_content), chunk_size)
                            ]
                            if content_lines and not content_lines[-1].endswith("\n"):
                                content_lines[-1] += "\n"

                            # Mark this as base64-encoded binary content
                            content_lines.insert(0, "# BINARY_ARCHIVE_BASE64_ENCODED\n")

                        except Exception as e_read:
                            logger.warning(
                                f"Error reading archive file '{normalized_file_path}': {e_read}"
                            )
                            content_lines = BINARY_CONTENT_PLACEHOLDER
                    elif is_likely_binary_file(
                        file_full_path
                    ):  # Pass full_path for mimetype guessing
                        logger.info(
                            f"File '{normalized_file_path}' detected as binary. Content not loaded."
                        )
                        content_lines = BINARY_CONTENT_PLACEHOLDER
                    else:
                        # Read ALL text files in binary mode to preserve exact line endings (like real Linux)
                        try:
                            with open(file_full_path, "rb") as f:
                                binary_content = f.read()

                            # Try to decode as text, preserving exact line endings
                            read_success = False
                            for encoding in ["utf-8", "latin-1", "cp1252"]:
                                try:
                                    text_content = binary_content.decode(encoding)
                                    content_lines = text_content.splitlines(
                                        keepends=True
                                    )
                                    if not content_lines and text_content:
                                        content_lines = [text_content]
                                    read_success = True
                                    logger.debug(
                                        f"Successfully read file '{normalized_file_path}' with encoding '{encoding}' preserving exact line endings."
                                    )
                                    break
                                except UnicodeDecodeError:
                                    logger.debug(
                                        f"Failed to decode '{normalized_file_path}' with encoding '{encoding}'. Trying next."
                                    )
                                    continue

                            if not read_success:
                                logger.warning(
                                    f"Could not decode file '{normalized_file_path}' with any encoding, treating as binary."
                                )
                                content_lines = BINARY_CONTENT_PLACEHOLDER

                        except Exception as e_read:
                            logger.warning(
                                f"Error reading file '{normalized_file_path}': {e_read}"
                            )
                            content_lines = [
                                f"Error: Could not read file content. Reason: {type(e_read).__name__}\n"
                            ]

                    db_instance["file_system"][normalized_file_path] = {
                        "path": normalized_file_path,
                        "is_directory": False,
                        "content_lines": content_lines,
                        "size_bytes": size_bytes,
                        "last_modified": last_modified_iso,
                        "metadata": file_metadata,  # Add metadata for file
                    }
                    logger.debug(
                        f"Added file entry with metadata to DB: {normalized_file_path}"
                    )

                except (
                    FileNotFoundError
                ):  # Should be rare if os.walk yielded it, but good for robustness
                    logger.warning(
                        f"File '{normalized_file_path}' was not found during scan (possibly deleted concurrently). Skipping."
                    )
                except PermissionError as pe:
                    logger.warning(
                        f"Permission denied for accessing file '{normalized_file_path}': {pe}. Storing with minimal info."
                    )
                    db_instance["file_system"][normalized_file_path] = {
                        "path": normalized_file_path,
                        "is_directory": False,
                        "content_lines": [
                            f"Error: Permission denied to read file content.\n"
                        ],
                        "size_bytes": 0,
                        "last_modified": get_current_timestamp_iso(),  # Use current time as fallback
                    }
                except Exception as e:
                    logger.warning(
                        f"An unexpected error occurred while processing file '{normalized_file_path}': {e}. Storing with minimal info."
                    )
                    db_instance["file_system"][normalized_file_path] = {
                        "path": normalized_file_path,
                        "is_directory": False,
                        "content_lines": [
                            f"Error: Could not process file due to an unexpected error: {type(e).__name__}\n"
                        ],
                        "size_bytes": 0,
                        "last_modified": get_current_timestamp_iso(),
                    }

        logger.info(
            f"Hydration complete. Total items in file_system: {len(db_instance['file_system'])}"
        )
        return True

    except FileNotFoundError:
        raise  # Re-raise if it's from the root directory check
    except Exception as e:
        msg = f"Fatal error during DB hydration process: {e}"
        logger.critical(msg, exc_info=True)
        db_instance["workspace_root"] = ""
        db_instance["cwd"] = ""
        db_instance["file_system"] = {}
        raise RuntimeError(msg) from e


def _normalize_path_for_db(path_str: str) -> str:
    if path_str is None:
        return None
    return os.path.normpath(path_str).replace("\\", "/")


def map_temp_path_to_db_key(
    temp_path: str, temp_root: str, desired_logical_root: str
) -> Optional[str]:
    # Normalize physical temporary paths
    normalized_temp_path = _normalize_path_for_db(os.path.abspath(temp_path))
    normalized_temp_root = _normalize_path_for_db(os.path.abspath(temp_root))

    # desired_logical_root is the intended base (e.g., "/test_workspace")
    # Ensure it's also in a canonical form using _normalize_path_for_db
    # This does NOT make it OS-absolute.
    normalized_desired_logical_root = _normalize_path_for_db(desired_logical_root)

    if not normalized_temp_path.startswith(normalized_temp_root):
        _log_util_message(
            logging.DEBUG,
            f"Debug map_key: Temp path '{normalized_temp_path}' is not under temp root '{normalized_temp_root}'.",
        )
        return None

    if normalized_temp_path == normalized_temp_root:
        return normalized_desired_logical_root  # Path is the root itself

    relative_path = os.path.relpath(normalized_temp_path, normalized_temp_root)

    # If relpath is '.', it means temp_path and temp_root are the same directory.
    if relative_path == ".":
        return normalized_desired_logical_root

    # Join the desired logical root with the relative path from the temp structure
    final_logical_path = _normalize_path_for_db(
        os.path.join(normalized_desired_logical_root, relative_path)
    )

    # Hierarchical sanity check:
    # The final_logical_path should start with normalized_desired_logical_root (unless root is just "/")
    # or be equal to it.
    if final_logical_path == normalized_desired_logical_root:
        # This happens if relative_path was effectively empty or "."
        return final_logical_path

    # For non-root logical roots, ensure it starts with "root/"
    # For root ("/"), any absolute path (starting with "/") is fine.
    expected_prefix = normalized_desired_logical_root
    if expected_prefix != "/" and not expected_prefix.endswith("/"):
        expected_prefix += "/"

    if (
        not final_logical_path.startswith(expected_prefix)
        and final_logical_path != normalized_desired_logical_root
    ):
        # This handles cases like desired_logical_root="/foo", final_logical_path="/foobar" (not under /foo/)
        # or desired_logical_root="/", final_logical_path="bar" (not absolute) - though join should prevent this.
        _log_util_message(
            logging.ERROR,
            f"Constructed logical path '{final_logical_path}' "
            f"is not hierarchically under desired logical root '{normalized_desired_logical_root}' "
            f"(expected prefix '{expected_prefix}'). Relative path was: '{relative_path}'.",
        )
        return None

    return final_logical_path


# --- Dehydrate Function ---
def dehydrate_db_to_directory(db: Dict[str, Any], target_dir: str) -> bool:
    """Writes workspace file system content to a specified target directory.
    Recreates the directory and file structure from the provided 'db' state
    into 'target_dir'. This function also updates the 'workspace_root' and 'cwd'
    in the 'db' object to reflect this new target directory.
    Args:
        db: The database dictionary containing 'workspace_root' and 'file_system'.
            This dictionary is modified in-place.
        target_dir: The path to the directory where the file system content
                    will be written. It will be created if it doesn't exist.
    Returns:
        True if the process completes successfully.
    Raises:
        ValueError: If 'db' is missing 'workspace_root'.
        OSError: If there are issues creating directories or writing files.
        Exception: For other unexpected errors during the process.
    """
    old_root = db.get("workspace_root")
    if not old_root:
        raise ValueError("DB missing 'workspace_root' for dehydration.")

    new_root = os.path.abspath(target_dir).replace("\\", "/") # Standardize new root path
    file_system = db.get("file_system", {})
    new_file_system = {} # To store updated paths for the DB

    _log_util_message(logging.INFO, f"Writing workspace state to disk: {new_root}")

    try:
        os.makedirs(new_root, exist_ok=True) # Create target root if needed

        # First, check if this is a git repository and handle git state
        original_git_dir = os.path.join(old_root, ".git")
        new_git_dir = os.path.join(new_root, ".git")
        is_git_repo = os.path.exists(original_git_dir) and os.path.isdir(original_git_dir)

        temp_git_backup = None
        if is_git_repo:
            _log_util_message(logging.INFO, "Git repository detected - preserving .git directory")
            # Create a temporary backup location outside of the target directory
            temp_git_backup = os.path.join(os.path.dirname(new_root), ".git_backup_" + str(time.time()))
            try:
                # Move .git directory to the safe temporary location
                shutil.move(original_git_dir, temp_git_backup)
                _log_util_message(logging.INFO, f"Moved .git to {temp_git_backup}")

                # Clean the target directory (now that .git is safe)
                for item in os.listdir(new_root):
                    # Important: Do not touch the new .git directory if it somehow exists
                    if item == ".git":
                        continue
                    item_path = os.path.join(new_root, item)
                    try:
                        if os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                        else:
                            os.unlink(item_path)
                    except OSError as e:
                        _log_util_message(logging.WARNING, f"Could not remove item {item_path} during cleaning: {e}")

                _log_util_message(logging.INFO, f"Cleaned target directory: {new_root}")

            except Exception as e:
                _log_util_message(logging.ERROR, f"Error during .git preservation or directory cleaning: {e}")
                # Attempt to restore .git if it was moved
                if temp_git_backup and os.path.exists(temp_git_backup):
                    shutil.move(temp_git_backup, new_git_dir)
                raise

        # Now process all files from the DB state
        for old_path, entry in file_system.items():
            # Determine relative path from old root to map to new root
            if old_path == old_root:
                rel_path = '.'
            else:
                 try:
                      rel_path = os.path.relpath(old_path, old_root)
                 except ValueError as e:
                      # Log if a path doesn't seem to belong to the old root
                      _log_util_message(logging.ERROR, f"Path '{old_path}' not relative to workspace root '{old_root}': {e}")
                      continue

            new_path = os.path.normpath(os.path.join(new_root, rel_path)).replace("\\", "/")

            # Skip writing to .git directory, as it's handled separately
            if ".git" in new_path.split('/'):
                continue

            # Prepare new entry for the DB reflecting the new physical path
            new_entry_state = entry.copy()
            new_entry_state["path"] = new_path
            new_file_system[new_path] = new_entry_state

            try:
                if new_entry_state.get("is_directory", False):
                    os.makedirs(new_path, exist_ok=True) # Create directory
                else:
                    # Create parent directory for the file if it doesn't exist
                    os.makedirs(os.path.dirname(new_path), exist_ok=True)

                    # Check if this is a symlink
                    is_symlink = entry.get("metadata", {}).get("attributes", {}).get("is_symlink", False)
                    symlink_target = entry.get("metadata", {}).get("attributes", {}).get("symlink_target")

                    if is_symlink and symlink_target:
                        # For symlinks, create a new symlink pointing to the target
                        # First remove any existing file/link
                        if os.path.exists(new_path) or os.path.islink(new_path):
                            os.unlink(new_path)
                        # Create the symlink with the original target
                        os.symlink(symlink_target, new_path)
                    else:
                        # Write ALL files exactly as they were read - no line ending conversion
                        # This preserves the original line endings (CRLF will show as ^M in Linux terminals)
                        content_to_write = entry.get("content_lines", [])

                        # Check if this is a base64-encoded archive file
                        if (content_to_write and 
                            len(content_to_write) > 0 and 
                            content_to_write[0].strip() == "# BINARY_ARCHIVE_BASE64_ENCODED"):

                            # This is a base64-encoded archive file - decode it back to binary
                            try:
                                # Remove the header and join all base64 content
                                base64_content = ''.join(line.rstrip('\n') for line in content_to_write[1:])
                                binary_content = base64.b64decode(base64_content)

                                # Write as binary file
                                with open(new_path, "wb") as f:
                                    f.write(binary_content)
                                _log_util_message(logging.INFO, f"Restored binary archive content for: {new_path}")

                            except Exception as e:
                                _log_util_message(logging.ERROR, f"Failed to decode archive file '{new_path}': {e}")
                                # Fall back to writing as text (will be broken but won't crash)
                                with open(new_path, "w", encoding="utf-8") as f:
                                    f.writelines(content_to_write)
                        else:
                            # Regular text file - write as before
                            with open(new_path, "w", encoding="utf-8") as f:
                                f.writelines(content_to_write)

                # Apply metadata if available
                if "metadata" in entry:
                    _apply_file_metadata(new_path, entry["metadata"], strict_mode=False)

            except OSError as e:
                _log_util_message(logging.ERROR, f"OS error writing to {new_path}: {e}", exc_info=True)
                raise # Re-raise OS errors
            except Exception as e:
                _log_util_message(logging.ERROR, f"Unexpected error writing {new_path}: {e}", exc_info=True)
                raise # Re-raise other unexpected errors

        if is_git_repo and temp_git_backup:
            # Move the .git directory back
            try:
                shutil.move(temp_git_backup, new_git_dir)
                _log_util_message(logging.INFO, f"Restored .git directory to {new_git_dir}")
            except Exception as e:
                _log_util_message(logging.CRITICAL, f"CRITICAL: Failed to restore .git directory from {temp_git_backup} to {new_git_dir}: {e}")
                # This is a critical failure, as the git history is now detached.
                raise RuntimeError(f"Failed to restore .git directory. It is currently located at {temp_git_backup}") from e

        # Update the DB object to reflect the new physical location
        db["workspace_root"] = new_root
        db["cwd"] = new_root # Assume CWD moves with the root for this operation
        db["file_system"] = new_file_system
        _log_util_message(logging.INFO, f"Workspace state successfully written to {new_root}")

        return True

    except (ValueError, OSError, Exception) as e:
        # Log any failure during the overall process
        _log_util_message(logging.ERROR, f"Failed to write workspace state to disk: {e}", exc_info=True)
        raise e # Re-raise the caught exception


def _should_update_access_time(command: str) -> bool:
    """
    Determine if a command should update access time based on realistic filesystem behavior.

    Args:
        command: The command being executed

    Returns:
        bool: True if the command should update access time
    """
    if ACCESS_TIME_MODE == "noatime":
        return False

    if ACCESS_TIME_MODE == "atime":
        return True

    # For "relatime" mode, be more selective about what updates atime
    command = command.strip().split()[0] if command.strip() else ""

    # Commands that typically read file content (should update atime in relatime)
    content_reading_commands = {
        "cat",
        "less",
        "more",
        "head",
        "tail",
        "grep",
        "awk",
        "sed",
        "sort",
        "uniq",
        "wc",
        "diff",
        "cmp",
        "file",
        "strings",
        "hexdump",
        "od",
        "xxd",
        "vim",
        "nano",
        "emacs",
    }

    # Commands that only read metadata or directory listings (shouldn't update atime in relatime)
    metadata_only_commands = {
        "ls",
        "stat",
        "find",
        "du",
        "df",
        "tree",
        "locate",
        "which",
        "whereis",
        "pwd",
        "dirname",
        "basename",
    }

    if command in content_reading_commands:
        return True
    elif command in metadata_only_commands:
        return False
    else:
        # For unknown commands, be conservative and update atime
        return True


def _should_update_access_time(command: str) -> bool:
    """
    Determine if a command should update access time based on realistic filesystem behavior.

    Args:
        command: The command being executed

    Returns:
        bool: True if the command should update access time
    """
    if ACCESS_TIME_MODE == "noatime":
        return False

    if ACCESS_TIME_MODE == "atime":
        return True

    # For "relatime" mode, be more selective about what updates atime
    command = command.strip().split()[0] if command.strip() else ""

    # Commands that typically read file content (should update atime in relatime)
    content_reading_commands = {
        "cat",
        "less",
        "more",
        "head",
        "tail",
        "grep",
        "awk",
        "sed",
        "sort",
        "uniq",
        "wc",
        "diff",
        "cmp",
        "file",
        "strings",
        "hexdump",
        "od",
        "xxd",
        "vim",
        "nano",
        "emacs",
    }

    # Commands that only read metadata or directory listings (shouldn't update atime in relatime)
    metadata_only_commands = {
        "ls",
        "stat",
        "find",
        "du",
        "df",
        "tree",
        "locate",
        "which",
        "whereis",
        "pwd",
        "dirname",
        "basename",
    }

    if command in content_reading_commands:
        return True
    elif command in metadata_only_commands:
        return False
    else:
        # For unknown commands, be conservative and update atime
        return True


def _extract_file_paths_from_command(
    command: str, workspace_root: str, current_cwd: str = None
) -> set:
    """
    Extract file paths that might be accessed by the command.

    Args:
        command: The command string
        workspace_root: The workspace root path
        current_cwd: The current working directory (optional, defaults to workspace_root)

    Returns:
        set: Set of absolute file paths that might be accessed by the command
    """
    if not command or not command.strip():
        return set()

    parts = command.strip().split()
    if not parts:
        return set()

    cmd = parts[0]
    args = parts[1:] if len(parts) > 1 else []

    accessed_files = set()

    # Commands that typically access files mentioned as arguments
    file_reading_commands = {
        "cat",
        "less",
        "more",
        "head",
        "tail",
        "grep",
        "awk",
        "sed",
        "sort",
        "uniq",
        "wc",
        "diff",
        "cmp",
        "file",
        "strings",
        "hexdump",
        "od",
        "xxd",
        "vim",
        "nano",
        "emacs",
        "cp",
        "mv",
    }

    # In "atime" mode, even metadata commands should be considered as accessing files
    metadata_commands = {
        "ls",
        "stat",
        "find",
        "du",
        "df",
        "tree",
        "locate",
        "which",
        "whereis",
    }

    # Determine which commands to process based on ACCESS_TIME_MODE
    commands_to_process = set()
    if ACCESS_TIME_MODE == "atime":
        # In atime mode, both content and metadata commands update access time
        commands_to_process = file_reading_commands | metadata_commands
    else:
        # In noatime/relatime modes, only content-reading commands matter
        commands_to_process = file_reading_commands

    # Special handling for commands with redirection (even if cmd is not in commands_to_process)
    # Commands like "echo content >> file.txt" should update access time of file.txt
    redirection_operators = [">", ">>", "<"]
    has_redirection = any(op in args for op in redirection_operators)

    if cmd in commands_to_process or has_redirection:
        # Use provided current working directory or default to workspace_root
        if current_cwd is None:
            current_cwd = workspace_root

        i = 0
        while i < len(args):
            arg = args[i]

            # Skip flags (arguments starting with -)
            if arg.startswith("-"):
                i += 1
                continue

            # Handle redirection operators
            if arg in redirection_operators:
                # The next argument after redirection operator is the file being accessed
                if i + 1 < len(args):
                    file_arg = args[i + 1]
                    try:
                        if os.path.isabs(file_arg):
                            abs_path = _normalize_path_for_db(file_arg)
                        else:
                            abs_path = _normalize_path_for_db(
                                os.path.join(current_cwd, file_arg)
                            )

                        if abs_path.startswith(workspace_root):
                            accessed_files.add(abs_path)
                    except:
                        pass
                    i += 2  # Skip both the operator and the file argument
                    continue
                else:
                    i += 1
                    continue

            # Skip other shell constructs
            if arg in ["|", "&&", "||", ";"]:
                i += 1
                continue

            # For file-reading commands, also process direct file arguments
            if cmd in commands_to_process:
                try:
                    if os.path.isabs(arg):
                        abs_path = _normalize_path_for_db(arg)
                    else:
                        abs_path = _normalize_path_for_db(
                            os.path.join(current_cwd, arg)
                        )

                    if abs_path.startswith(workspace_root):
                        accessed_files.add(abs_path)
                except:
                    pass

            i += 1

    return accessed_files


def resolve_target_path_for_cd(
    current_cwd_abs: str,
    target_arg: str,
    workspace_root_abs: str,
    file_system_view: Dict[str, Any],
) -> Optional[str]:
    """
    Resolves and validates a target path for 'cd'.
    All input paths (current_cwd_abs, workspace_root_abs) should be absolute and normalized.
    target_arg can be relative or absolute (interpreted relative to workspace_root if starting with '/').
    """
    # Normalize inputs (assuming they are already absolute where specified)
    current_cwd_abs = _normalize_path_for_db(current_cwd_abs)
    workspace_root_abs = _normalize_path_for_db(workspace_root_abs)
    target_arg_normalized = _normalize_path_for_db(target_arg)  # Normalize arg itself

    if target_arg_normalized.startswith("/"):
        # Path is absolute relative to workspace_root
        # e.g., if workspace_root is C:/ws and target_arg is /foo, new_path is C:/ws/foo
        prospective_path = _normalize_path_for_db(
            os.path.join(workspace_root_abs, target_arg_normalized.lstrip("/"))
        )
    elif ":" in target_arg_normalized and os.path.isabs(
        target_arg_normalized
    ):  # Full OS path like C:/...
        # If a full OS path is given, it must be within the workspace
        prospective_path = target_arg_normalized
    else:
        # Path is relative to current_cwd_abs
        prospective_path = _normalize_path_for_db(
            os.path.join(current_cwd_abs, target_arg_normalized)
        )

    # Final normalization (e.g., resolves '..', '.', multiple slashes)
    resolved_path_abs = _normalize_path_for_db(os.path.normpath(prospective_path))

    # Validation:
    # 1. Must be within or same as workspace_root
    #    A simple check is that resolved_path_abs must start with workspace_root_abs.
    #    And commonpath should be workspace_root_abs unless resolved_path_abs is workspace_root_abs.
    if not resolved_path_abs.startswith(workspace_root_abs):
        # Check if it went "above" root. e.g. root C:/a/b, resolved C:/a
        # This can happen if workspace_root_abs itself is a/b and resolved path is just a
        # A more robust check involves ensuring original_root is a prefix of new_path
        if (
            workspace_root_abs != resolved_path_abs
            and not _normalize_path_for_db(
                os.path.commonpath([workspace_root_abs, resolved_path_abs])
            )
            == workspace_root_abs
        ):
            _log_util_message(
                logging.WARNING,
                f"cd: Attempt to navigate outside workspace root. Target: '{resolved_path_abs}', Root: '{workspace_root_abs}'",
            )
            return None  # Path is outside workspace

    # 2. Must exist in file_system_view and be a directory
    if resolved_path_abs in file_system_view and file_system_view[
        resolved_path_abs
    ].get("is_directory", False):
        return resolved_path_abs
    else:
        _log_util_message(
            logging.WARNING,
            f"cd: Target path '{resolved_path_abs}' is not a valid directory in the DB.",
        )
        return None


# --- Update Function ---
def update_db_file_system_from_temp(
    temp_root: str,
    original_state: Dict,
    workspace_root: str,
    preserve_metadata: bool = True,
    command: str = "",
):
    """Update function with metadata preservation and archive file support"""
    try:  # Start of the main try block
        final_logical_root_for_db = _normalize_path_for_db(workspace_root)
        normalized_temp_root = _normalize_path_for_db(os.path.abspath(temp_root))

        # Check if this is a metadata-modifying command
        is_metadata_command = command.strip().startswith(("chmod", "chown"))

        # Determine which files should have their access time updated
        should_update_atime = _should_update_access_time(command)
        # Use logical workspace path for file resolution, not physical temp path
        logical_cwd = DB.get("cwd", workspace_root)
        # Convert physical temp path back to logical path if needed
        if logical_cwd.startswith(temp_root):
            # Map from physical temp path to logical workspace path
            relative_to_temp = os.path.relpath(logical_cwd, temp_root)
            logical_cwd = (
                os.path.join(workspace_root, relative_to_temp)
                if relative_to_temp != "."
                else workspace_root
            )
        accessed_files = (
            _extract_file_paths_from_command(command, workspace_root, logical_cwd)
            if should_update_atime
            else set()
        )

        new_file_system = {}
        processed_paths = set()

        for current_fs_root, dirs, files in os.walk(normalized_temp_root, topdown=True):
            current_physical_dir_path = _normalize_path_for_db(
                os.path.abspath(current_fs_root)
            )

            dir_db_key_path = map_temp_path_to_db_key(
                current_physical_dir_path,
                normalized_temp_root,
                final_logical_root_for_db,
            )

            if dir_db_key_path is None:
                _log_util_message(
                    logging.WARNING,
                    f"Could not map directory temp path '{current_physical_dir_path}' to a logical DB key during DB update.",
                )
                continue

            if dir_db_key_path not in processed_paths:
                old_dir_entry = original_state.get(dir_db_key_path, {})
                last_modified_val = old_dir_entry.get(
                    "last_modified", get_current_timestamp_iso()
                )  # Reuse if possible

                # Check if this specific directory should have its access time updated
                dir_should_update_atime = (
                    should_update_atime and dir_db_key_path in accessed_files
                )

                if not dir_should_update_atime:
                    # Collect fresh metadata but preserve access time
                    temp_metadata = _collect_file_metadata(current_physical_dir_path)
                    dir_metadata = temp_metadata.copy()

                    # Preserve original access time if available
                    original_dir_entry = original_state.get(dir_db_key_path, {})
                    original_dir_metadata = original_dir_entry.get("metadata", {})
                    if (
                        original_dir_metadata
                        and "timestamps" in original_dir_metadata
                        and "access_time" in original_dir_metadata["timestamps"]
                    ):
                        dir_metadata.setdefault("timestamps", {})
                        dir_metadata["timestamps"]["access_time"] = (
                            original_dir_metadata["timestamps"]["access_time"]
                        )
                else:
                    # This directory was accessed, collect fresh metadata (including updated access time)
                    dir_metadata = _collect_file_metadata(current_physical_dir_path)

                # For metadata commands, apply in strict mode
                if is_metadata_command:
                    try:
                        _apply_file_metadata(
                            current_physical_dir_path, dir_metadata, strict_mode=True
                        )
                    except Exception as e:
                        raise MetadataError(
                            f"Failed to apply metadata in strict mode: {str(e)}"
                        ) from e

                new_file_system[dir_db_key_path] = {
                    "path": dir_db_key_path,
                    "is_directory": True,
                    "content_lines": [],  # Directories don't have content lines
                    "size_bytes": 0,  # Directories usually have 0 size in this model
                    "last_modified": last_modified_val,
                    "metadata": dir_metadata,
                }
                processed_paths.add(dir_db_key_path)

            for fname in files:
                temp_file_full_path = os.path.join(
                    current_fs_root, fname
                )  # Physical path to the file in temp dir
                file_physical_path = _normalize_path_for_db(
                    os.path.abspath(temp_file_full_path)
                )

                file_db_key_path = map_temp_path_to_db_key(
                    file_physical_path, normalized_temp_root, final_logical_root_for_db
                )

                if file_db_key_path is None:
                    _log_util_message(
                        logging.WARNING,
                        f"Could not map file temp path '{file_physical_path}' to a logical DB key during DB update.",
                    )
                    continue

                if (
                    file_db_key_path in processed_paths
                ):  # Should not happen if logic is correct, but a safeguard.
                    _log_util_message(
                        logging.WARNING,
                        f"File path '{file_db_key_path}' already processed. Skipping duplicate.",
                    )
                    continue

                content_lines = ERROR_READING_CONTENT_PLACEHOLDER
                size_bytes = 0
                last_modified = get_current_timestamp_iso()  # Default
                file_metadata = None  # Initialize metadata variable

                try:
                    # Check if the file is a symlink first
                    is_symlink = os.path.islink(temp_file_full_path)
                    if is_symlink:
                        # For symlinks, we need special handling
                        symlink_target = os.readlink(temp_file_full_path)
                        # Check if this specific symlink should have its access time updated
                        symlink_should_update_atime = (
                            should_update_atime and file_db_key_path in accessed_files
                        )

                        if not symlink_should_update_atime:
                            # Create fresh symlink metadata but preserve access time
                            file_metadata = {
                                "attributes": {
                                    "is_symlink": True,
                                    "symlink_target": symlink_target,
                                    "is_hidden": os.path.basename(
                                        temp_file_full_path
                                    ).startswith("."),
                                },
                                "timestamps": {
                                    "access_time": get_current_timestamp_iso(),
                                    "modify_time": get_current_timestamp_iso(),
                                    "change_time": get_current_timestamp_iso(),
                                },
                            }

                            # Preserve original access time if available
                            original_entry = original_state.get(file_db_key_path, {})
                            original_metadata = original_entry.get("metadata", {})
                            if (
                                original_metadata
                                and "timestamps" in original_metadata
                                and "access_time" in original_metadata["timestamps"]
                            ):
                                file_metadata["timestamps"]["access_time"] = (
                                    original_metadata["timestamps"]["access_time"]
                                )
                        else:
                            # This symlink was accessed, create fresh metadata with updated access time
                            file_metadata = {
                                "attributes": {
                                    "is_symlink": True,
                                    "symlink_target": symlink_target,
                                    "is_hidden": os.path.basename(
                                        temp_file_full_path
                                    ).startswith("."),
                                },
                                "timestamps": {
                                    "access_time": get_current_timestamp_iso(),  # Updated access time
                                    "modify_time": get_current_timestamp_iso(),
                                    "change_time": get_current_timestamp_iso(),
                                },
                            }
                        content_lines = []  # Symlinks don't have content
                        size_bytes = len(
                            symlink_target
                        )  # Size is the length of the target path
                    else:
                        # Regular file handling
                        stat_info = os.stat(temp_file_full_path)
                        size_bytes = stat_info.st_size
                        last_modified = (
                            datetime.datetime.fromtimestamp(
                                stat_info.st_mtime, tz=datetime.timezone.utc
                            )
                            .isoformat()
                            .replace("+00:00", "Z")
                        )

                        # Check if this specific file should have its access time updated
                        file_should_update_atime = (
                            should_update_atime and file_db_key_path in accessed_files
                        )

                        if not file_should_update_atime:
                            # Collect fresh metadata but preserve access time
                            temp_metadata = _collect_file_metadata(temp_file_full_path)
                            file_metadata = temp_metadata.copy()

                            # Preserve original access time if available
                            original_entry = original_state.get(file_db_key_path, {})
                            original_metadata = original_entry.get("metadata", {})
                            if (
                                original_metadata
                                and "timestamps" in original_metadata
                                and "access_time" in original_metadata["timestamps"]
                            ):
                                file_metadata.setdefault("timestamps", {})
                                file_metadata["timestamps"]["access_time"] = (
                                    original_metadata["timestamps"]["access_time"]
                                )
                        else:
                            # This file was accessed, simulate the access time update that OS should have done
                            file_metadata = _collect_file_metadata(temp_file_full_path)
                            # Manually update access time since our hydration process interferes with natural OS updates
                            file_metadata.setdefault("timestamps", {})
                            file_metadata["timestamps"][
                                "access_time"
                            ] = get_current_timestamp_iso()

                        # For metadata commands, apply in strict mode
                        if is_metadata_command:
                            try:
                                _apply_file_metadata(
                                    temp_file_full_path, file_metadata, strict_mode=True
                                )
                            except Exception as e:
                                # Re-raise as MetadataError to signal strict mode failure
                                raise MetadataError(
                                    f"Failed to apply metadata in strict mode: {str(e)}"
                                ) from e

                    # Reuse old content_lines and metadata if file is unchanged (optional optimization)
                    # For simplicity here, we always re-read, but you could compare with original_file_system_state.get(file_db_key_path)

                    if size_bytes == 0:
                        content_lines = []
                    elif (
                        size_bytes > MAX_FILE_SIZE_BYTES
                    ):  # MAX_FILE_SIZE_BYTES needs to be defined/imported
                        content_lines = LARGE_FILE_CONTENT_PLACEHOLDER  # Needs to be defined/imported
                        _log_util_message(
                            logging.INFO,
                            f"File '{file_db_key_path}' too large ({size_bytes} bytes), using placeholder.",
                        )
                    elif (
                        _is_archive_file(temp_file_full_path)
                        and size_bytes <= MAX_ARCHIVE_SIZE_BYTES
                    ):
                        # Special handling for archive files - store actual binary content
                        _log_util_message(
                            logging.INFO,
                            f"File '{file_db_key_path}' detected as archive. Storing binary content.",
                        )
                        try:
                            with open(temp_file_full_path, "rb") as f:
                                binary_content = f.read()

                            # Store binary content as base64-encoded strings to preserve it exactly
                            encoded_content = base64.b64encode(binary_content).decode(
                                "ascii"
                            )
                            # Split into chunks to avoid extremely long lines
                            chunk_size = 76  # Standard base64 line length
                            content_lines = [
                                encoded_content[i : i + chunk_size] + "\n"
                                for i in range(0, len(encoded_content), chunk_size)
                            ]
                            if content_lines and not content_lines[-1].endswith("\n"):
                                content_lines[-1] += "\n"

                            # Mark this as base64-encoded binary content
                            content_lines.insert(0, "# BINARY_ARCHIVE_BASE64_ENCODED\n")

                        except Exception as e_read:
                            _log_util_message(
                                logging.WARNING,
                                f"Error reading archive file '{file_db_key_path}': {e_read}",
                            )
                            content_lines = BINARY_CONTENT_PLACEHOLDER
                    elif is_likely_binary_file(temp_file_full_path):
                        content_lines = BINARY_CONTENT_PLACEHOLDER
                        _log_util_message(
                            logging.INFO,
                            f"File '{file_db_key_path}' detected as binary, using placeholder.",
                        )
                    else:
                        # Read ALL text files in binary mode to preserve exact line endings (like real Linux)
                        try:
                            with open(temp_file_full_path, "rb") as f:
                                binary_content = f.read()

                            # Try to decode as text, preserving exact line endings
                            read_success = False
                            for encoding in ["utf-8", "latin-1", "cp1252"]:
                                try:
                                    text_content = binary_content.decode(encoding)
                                    content_lines = text_content.splitlines(
                                        keepends=True
                                    )
                                    if not content_lines and text_content:
                                        content_lines = [text_content]
                                    read_success = True
                                    logger.debug(
                                        f"Successfully read file '{file_db_key_path}' with encoding '{encoding}' preserving exact line endings."
                                    )
                                    break
                                except UnicodeDecodeError:
                                    logger.debug(
                                        f"Failed to decode '{file_db_key_path}' with encoding '{encoding}'. Trying next."
                                    )
                                    continue

                            if not read_success:
                                logger.warning(
                                    f"Could not decode file '{file_db_key_path}' with any encoding, treating as binary."
                                )
                                content_lines = BINARY_CONTENT_PLACEHOLDER

                        except Exception as e_read:
                            logger.warning(
                                f"Error reading file '{file_db_key_path}': {e_read}"
                            )
                            content_lines = [
                                f"Error: Could not read file content. Reason: {type(e_read).__name__}\n"
                            ]

                except MetadataError:
                    # Re-raise MetadataError to be caught by outer try block
                    raise
                except FileNotFoundError:
                    _log_util_message(
                        logging.WARNING,
                        f"File '{temp_file_full_path}' not found during DB update (deleted concurrently?).",
                    )
                    content_lines = [
                        f"<Error: File not found during update>"
                    ]  # Or skip adding it
                except Exception as e_stat:
                    _log_util_message(
                        logging.ERROR,
                        f"Error stating or reading file '{temp_file_full_path}': {e_stat}",
                    )
                    content_lines = [
                        f"<Error processing file: {type(e_stat).__name__}>"
                    ]

                # Ensure we have metadata even in error cases
                if file_metadata is None:
                    # Check if this specific file should have its access time updated (even in error case)
                    error_case_should_update_atime = (
                        should_update_atime and file_db_key_path in accessed_files
                    )

                    if not error_case_should_update_atime:
                        # Create default metadata but preserve access time
                        file_metadata = {
                            "attributes": {
                                "is_symlink": False,
                                "is_hidden": False,
                                "is_readonly": False,
                                "symlink_target": None,  # Initialize to None in error case
                            },
                            "timestamps": {
                                "access_time": get_current_timestamp_iso(),
                                "modify_time": get_current_timestamp_iso(),
                                "change_time": get_current_timestamp_iso(),
                            },
                        }

                        # Preserve original access time if available
                        original_entry = original_state.get(file_db_key_path, {})
                        original_metadata = original_entry.get("metadata", {})
                        if (
                            original_metadata
                            and "timestamps" in original_metadata
                            and "access_time" in original_metadata["timestamps"]
                        ):
                            file_metadata["timestamps"]["access_time"] = (
                                original_metadata["timestamps"]["access_time"]
                            )
                    else:
                        # This file was accessed, create fresh metadata with updated access time
                        file_metadata = {
                            "attributes": {
                                "is_symlink": False,
                                "is_hidden": False,
                                "is_readonly": False,
                                "symlink_target": None,  # Initialize to None in error case
                            },
                            "timestamps": {
                                "access_time": get_current_timestamp_iso(),  # Updated access time
                                "modify_time": get_current_timestamp_iso(),
                                "change_time": get_current_timestamp_iso(),
                            },
                        }

                new_file_system[file_db_key_path] = {
                    "path": file_db_key_path,
                    "is_directory": False,
                    "content_lines": content_lines,
                    "size_bytes": size_bytes,
                    "last_modified": last_modified,
                    "metadata": file_metadata,  # Add metadata for file
                }
                processed_paths.add(file_db_key_path)

        # Logic for handling deleted files/directories:
        # Paths in original_file_system_state that are NOT in processed_paths were deleted.
        # new_file_system now contains all existing items.
        original_logical_paths = set(original_state.keys())
        current_logical_paths_found = processed_paths  # More accurate than new_file_system.keys() before assignment

        paths_implicitly_deleted = original_logical_paths - current_logical_paths_found
        if paths_implicitly_deleted:
            _log_util_message(
                logging.INFO,
                f"Paths removed during command execution: {paths_implicitly_deleted}",
            )

        DB["workspace_root"] = final_logical_root_for_db

        # CWD handling (relying on run_terminal_cmd's finally block for most precise restoration)
        # For safety, ensure CWD is at least within the new logical root if it's somehow very off.
        current_logical_cwd = _normalize_path_for_db(
            DB.get("cwd", final_logical_root_for_db)
        )
        if (
            not current_logical_cwd.startswith(final_logical_root_for_db)
            and current_logical_cwd != final_logical_root_for_db
        ):
            if final_logical_root_for_db == "/" and current_logical_cwd.startswith(
                "/"
            ):  # If root is / and CWD is absolute, it's fine
                pass
            else:
                DB["cwd"] = (
                    final_logical_root_for_db  # Reset to root if CWD seems invalid relative to new root.
                )

        DB["file_system"] = new_file_system

        # Access time handling is now done in the main collection loop above

        _log_util_message(
            logging.INFO,
            f"Internal state (global DB) updated from temp dir '{temp_root}'. New logical root: '{final_logical_root_for_db}'. Items: {len(new_file_system)}.",
        )

    except MetadataError as me:
        _log_util_message(
            logging.ERROR,
            f"Metadata operation failed in strict mode: {me}",
            exc_info=True,
        )
        raise  # Re-raise to be caught by run_command
    except Exception as e:
        _log_util_message(
            logging.ERROR,
            f"Update process failed in update_db_file_system_from_temp: {e}",
            exc_info=True,
        )
        raise