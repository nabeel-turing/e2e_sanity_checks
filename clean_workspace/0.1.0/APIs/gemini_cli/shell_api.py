"""Gemini-CLI shell tool implementations.

This module provides the main shell API functions for executing commands
in the simulated workspace environment with all advanced features from terminal.
"""
from __future__ import annotations

from typing import Dict, Any, Optional, List, Union
import os
import platform
import subprocess
import time
import uuid
import shutil
import tempfile
import copy  # deep copy for state snapshot
import logging
import inspect

from .SimulationEngine.db import DB
from common_utils.log_complexity import log_complexity
from .SimulationEngine.custom_errors import (
    InvalidInputError, 
    WorkspaceNotAvailableError,
    CommandExecutionError,
    ShellSecurityError,
    ProcessNotFoundError,
    MetadataError
)
from .SimulationEngine.utils import (
    validate_command_security,
    is_command_allowed,
    handle_internal_commands,
    dehydrate_db_to_directory,
    update_db_file_system_from_temp,
    normalize_simulated_path,
    get_shell_command,
    _normalize_path_for_db,
    resolve_target_path_for_cd,
    conditional_common_file_system_wrapper,
    normalize_command_paths,
    conditional_common_file_system_wrapper
)
from .SimulationEngine.env_manager import (
    prepare_command_environment,
    expand_variables,
    handle_env_command
)
from .SimulationEngine.file_utils import _is_within_workspace

# --- Logger Setup for this shell_api.py module ---
logger = logging.getLogger(__name__)

def _log_shell_message(level: int, message: str, exc_info: bool = False) -> None:
    """Logs a message with caller info (function:lineno) from within this module."""
    log_message = message
    try:
        # Get the frame of the function within shell_api.py that called this helper.
        frame = inspect.currentframe()
        caller_frame = frame.f_back
        if caller_frame and caller_frame.f_code:
            func_name = caller_frame.f_code.co_name
            line_no = caller_frame.f_lineno
            log_message = f"{func_name}:{line_no} - {message}"
    except Exception: # Fallback if frame inspection fails.
        pass

    # Log using the standard levels; defaults to DEBUG.
    if level == logging.ERROR: logger.error(log_message, exc_info=exc_info)
    elif level == logging.WARNING: logger.warning(log_message, exc_info=exc_info)
    elif level == logging.INFO: logger.info(log_message)
    else: logger.debug(log_message)


# Shell execution constants
DEFAULT_COMMAND_TIMEOUT = 60  # seconds
MAX_OUTPUT_SIZE = 10 * 1024 * 1024  # 10MB
OUTPUT_UPDATE_INTERVAL = 1.0  # seconds

@log_complexity
@conditional_common_file_system_wrapper
def run_shell_command(
    command: str,
    *,
    description: Optional[str] = None,
    directory: Optional[str] = None,
    background: Optional[bool] = False
) -> Dict[str, Any]:
    """Execute a shell command in the simulated workspace environment with all advanced features.
    
    This function executes shell commands with proper security validation,
    process management, and workspace integration. Commands are executed
    in a temporary environment that mirrors the workspace state.
    
    IMPORTANT: For any command that expects user interaction or uses a pager
    (like git diff, git log, less, head, tail, more, etc.), you MUST append
    ' | cat' to the command string yourself before passing it to this function.
    Failure to do so will cause the command to hang or fail.
    
    Args:
        command (str): The shell command to execute. Must be a valid shell command.
        description (Optional[str]): Brief description of the command's purpose.
        directory (Optional[str]): Directory to execute the command in, relative to
            workspace root. If not provided, uses current working directory.
        background (Optional[bool]): Whether to run the command in background.
            Background commands return immediately with a process ID.
            
    Returns:
        Dict[str, Any]: Dictionary containing execution results:
            - command (str): The executed command
            - directory (str): Directory where command was executed
            - stdout (str): Standard output from the command
            - stderr (str): Standard error from the command
            - returncode (Optional[int]): Exit code (None for background processes)
            - pid (Optional[int]): OS process ID (None for foreground commands)
            - process_group_id (Optional[str]): Process group ID (same as pid for background)
            - signal (Optional[str]): Signal that terminated the process (currently always None)
            - message (str): Human-readable status message
            
    Raises:
        InvalidInputError: If command or parameters are invalid.
        WorkspaceNotAvailableError: If workspace is not properly configured.
        ShellSecurityError: If command is blocked for security reasons.
        CommandExecutionError: If command execution fails.
        MetadataError: If metadata operations fail in strict mode.
    """
    # Use global DB state and utils module
    global DB

    # Initialize result dict with all required keys
    result_dict: Dict[str, Any] = {
        'command': command,
        'directory': "",
        'stdout': "", 
        'stderr': "", 
        'returncode': None, 
        'pid': None,
        'process_group_id': None,
        'signal': None,
        'message': "Initialization error."
    }

    # Parameter validation
    if not isinstance(command, str):
        raise InvalidInputError("'command' must be a string")
    
    if not command.strip():
        raise InvalidInputError("'command' cannot be empty")
    
    if description is not None and not isinstance(description, str):
        raise InvalidInputError("'description' must be a string or None")
    
    if directory is not None:
        if not isinstance(directory, str):
            raise InvalidInputError("'directory' must be a string or None")
        if os.path.isabs(directory):
            raise InvalidInputError("'directory' must be relative to workspace root")
    
    if background is not None and not isinstance(background, bool):
        raise InvalidInputError("'background' must be a boolean or None")
    
    # Set defaults
    background = background if background is not None else False
    
    # --- Get current workspace root and CWD ---
    current_workspace_root = DB.get("workspace_root")
    if not current_workspace_root:
        result_dict['message'] = "Operation failed: workspace_root is not configured."
        _log_shell_message(logging.ERROR, result_dict['message'])
        raise WorkspaceNotAvailableError(result_dict['message'])

    # Normalize paths for internal use
    current_workspace_root_norm = _normalize_path_for_db(current_workspace_root)
    current_cwd_norm = _normalize_path_for_db(DB.get("cwd", current_workspace_root_norm))
    
    # Handle directory parameter
    if directory is not None:
        # Validate directory is relative to workspace root
        if os.path.isabs(directory):
            raise InvalidInputError("'directory' must be relative to workspace root")
        
        # Resolve the target directory
        target_dir = os.path.join(current_workspace_root_norm, directory)
        target_dir_norm = _normalize_path_for_db(target_dir)
        
        # Check if directory exists in file system
        file_system = DB.get("file_system", {})
        if target_dir_norm not in file_system or not file_system[target_dir_norm].get("is_directory", False):
            raise InvalidInputError(f"Directory '{directory}' does not exist in workspace")
        
        # Use the target directory for execution
        execution_cwd = target_dir_norm
    else:
        # Use current working directory
        execution_cwd = current_cwd_norm
    
    # Update directory in result
    result_dict['directory'] = execution_cwd
    
    # Security validation
    validate_command_security(command)

    if not is_command_allowed(command):
        raise ShellSecurityError(f"Command not allowed by configuration: {command}")

    # --- Handle internal commands ---
    stripped_command = command.strip()

    # Handle environment variable commands
    if stripped_command in ('env',) or stripped_command.startswith(('export ', 'unset ')):
        env_result = handle_env_command(stripped_command, DB)
        # Ensure all required keys are present
        for key in ['command', 'directory', 'stdout', 'stderr', 'returncode', 'pid', 'process_group_id', 'signal', 'message']:
            if key not in env_result:
                env_result[key] = result_dict[key] if key in result_dict else (None if key in ['pid', 'returncode'] else "")
        return env_result

    # Handle cd and pwd as before
    if stripped_command == "cd" or stripped_command.startswith("cd "):
        _log_shell_message(logging.INFO, f"Handling internal 'cd': {command}")
        parts = stripped_command.split(maxsplit=1)
        target_arg = parts[1] if len(parts) > 1 else "/" # Default 'cd' target

        # Resolve target path within the workspace
        new_cwd_path = resolve_target_path_for_cd(
            current_cwd_norm,
            target_arg,
            current_workspace_root_norm,
            DB.get("file_system", {})
        )
        if new_cwd_path:
            DB["cwd"] = new_cwd_path # Update current working directory state
            result_dict['directory'] = _normalize_path_for_db(DB.get('cwd'))
            result_dict['message'] = f"Current directory changed to {result_dict['directory']}"
            result_dict['returncode'] = 0
            return result_dict
        else:
            result_dict['message'] = f"cd: Failed to change directory to '{target_arg}'. Path may be invalid or outside workspace."
            result_dict['stderr'] = f"cd: '{target_arg}': No such directory"
            result_dict['returncode'] = 1
            _log_shell_message(logging.WARNING, result_dict['message'])
            return result_dict  # Return error result instead of raising exception

    if stripped_command == "pwd":
        _log_shell_message(logging.INFO, "Handling internal 'pwd'")
        pwd_path = _normalize_path_for_db(DB.get('cwd', current_workspace_root_norm))
        result_dict['message'] = f"Current directory: {pwd_path}"
        result_dict['stdout'] = pwd_path # Output path to stdout
        result_dict['returncode'] = 0
        return result_dict
    # --- End internal command handling ---

    # --- Prepare for external command execution ---
    temp_dir_obj: Optional[tempfile.TemporaryDirectory] = None
    process_executed_without_launch_error = False
    command_message = ""

    # Preserve current workspace state before potential modifications
    original_filesystem_state = DB.get("file_system", {}).copy()
    # current_workspace_root_norm and current_cwd_norm are already captured

    try:
        # Create an execution environment
        temp_dir_obj = tempfile.TemporaryDirectory(prefix="cmd_exec_")
        exec_env_root = _normalize_path_for_db(temp_dir_obj.name)
        _log_shell_message(logging.INFO, f"Preparing execution environment in: {exec_env_root}")

        # Copy workspace state to the execution environment
        dehydrate_db_to_directory(DB, exec_env_root)
        _log_shell_message(logging.INFO, "Workspace state copied to execution environment.")

        # Determine the correct CWD within the execution environment
        if execution_cwd.startswith(current_workspace_root_norm):
            relative_cwd = os.path.relpath(execution_cwd, current_workspace_root_norm)
        else:
            # Fallback if CWD was somehow outside root
            _log_shell_message(logging.WARNING, f"Current directory '{execution_cwd}' is outside workspace root '{current_workspace_root_norm}'. Using environment root for command.")
            relative_cwd = "."

        # Construct the path for the subprocess CWD
        subprocess_cwd_physical = _normalize_path_for_db(os.path.join(exec_env_root, relative_cwd))

        # Verify the execution CWD exists
        if not os.path.isdir(subprocess_cwd_physical):
            _log_shell_message(logging.WARNING, f"Execution environment CWD '{subprocess_cwd_physical}' does not exist. Creating directory structure.")
            # Create the missing directory structure
            try:
                os.makedirs(subprocess_cwd_physical, exist_ok=True)
                _log_shell_message(logging.INFO, f"Created missing directory: {subprocess_cwd_physical}")
            except Exception as e:
                _log_shell_message(logging.ERROR, f"Failed to create directory '{subprocess_cwd_physical}': {e}")
                # Fall back to using the temp directory root
                subprocess_cwd_physical = exec_env_root
                if not os.path.isdir(subprocess_cwd_physical):
                    _log_shell_message(logging.ERROR, f"Even temp directory root '{exec_env_root}' does not exist!")
                    raise CommandExecutionError(f"Execution environment setup failed: temp directory '{exec_env_root}' does not exist")

        _log_shell_message(logging.INFO, f"Executing command '{command}' in CWD '{subprocess_cwd_physical}' (Background: {background})")

        # Prepare environment and expand variables
        cmd_env = prepare_command_environment(DB, subprocess_cwd_physical)

        # Don't expand variables in the command string, let bash handle it
        expanded_command = command.strip()

        if not expanded_command:
            result_dict['message'] = "Operation failed: Command string is empty."
            _log_shell_message(logging.ERROR, result_dict['message'])
            raise InvalidInputError(result_dict['message'])

        # --- Execute the command ---
        process_obj: Union[subprocess.Popen, subprocess.CompletedProcess, None] = None
        
        # Get platform-specific shell command
        shell_cmd = get_shell_command(expanded_command)
        
        if background:
            try:
                # Launch background process with environment
                with open(os.devnull, 'wb') as devnull:
                    process_obj = subprocess.Popen(
                        shell_cmd,
                        cwd=subprocess_cwd_physical,
                        stdout=devnull,
                        stderr=devnull,
                        env=cmd_env,
                        text=True
                    )
                process_executed_without_launch_error = True
                result_dict['pid'] = process_obj.pid
                result_dict['process_group_id'] = str(process_obj.pid)
                result_dict['returncode'] = None
                command_message = f"Command '{command}' launched successfully in background (PID: {process_obj.pid})."
            except FileNotFoundError:
                command_message = f"Launch failed: Command not found."
                _log_shell_message(logging.ERROR, command_message)
                result_dict['message'] = command_message
                result_dict['returncode'] = 127
                raise CommandExecutionError(result_dict['message'])
            except Exception as e:
                command_message = f"Launch failed for background process '{command}': {type(e).__name__} - {e}"
                _log_shell_message(logging.ERROR, command_message, exc_info=True)
                result_dict['message'] = command_message
                result_dict['returncode'] = 1
                raise CommandExecutionError(result_dict['message'])
        else: # Foreground execution
            try:
                # Run foreground process with environment
                process_obj = subprocess.run(
                    shell_cmd,
                    cwd=subprocess_cwd_physical,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    check=False,
                    env=cmd_env,
                    timeout=DEFAULT_COMMAND_TIMEOUT
                )
                process_executed_without_launch_error = True
                command_message = f"Command completed with exit code {process_obj.returncode}."
                result_dict['stdout'] = process_obj.stdout
                result_dict['stderr'] = process_obj.stderr
                result_dict['returncode'] = process_obj.returncode
                if process_obj.returncode != 0:
                    result_dict['message'] = f"Command failed with exit code {process_obj.returncode}. Workspace state updated.\nStderr: {process_obj.stderr}"
                    # Restore workspace state before raising exception for failed commands
                    _log_shell_message(logging.WARNING, f"Command '{command}' failed with exit code {process_obj.returncode}. Restoring pre-execution workspace state.")
                    DB["workspace_root"] = current_workspace_root_norm
                    DB["cwd"] = current_cwd_norm
                    DB["file_system"] = original_filesystem_state
                    raise CommandExecutionError(result_dict['message'])
            except subprocess.TimeoutExpired:
                raise CommandExecutionError(f"Command timed out after {DEFAULT_COMMAND_TIMEOUT} seconds")
            except FileNotFoundError:
                command_message = f"Execution failed: Command not found."
                _log_shell_message(logging.ERROR, command_message)
                result_dict['message'] = command_message
                result_dict['returncode'] = 127
                raise CommandExecutionError(result_dict['message'])
            except Exception as e:
                command_message = f"Execution failed for foreground process '{command}': {type(e).__name__} - {e}"
                _log_shell_message(logging.ERROR, command_message, exc_info=True)
                result_dict['message'] = command_message
                if result_dict.get('returncode') is None: result_dict['returncode'] = 1
                raise CommandExecutionError(result_dict['message'])

        # --- Post-execution state update ---
        if process_executed_without_launch_error:
            _log_shell_message(logging.INFO, f"Command '{command}' execution finished. Updating workspace state.")
            try:
                # Update the main workspace state from the execution environment
                update_db_file_system_from_temp(
                    exec_env_root,
                    original_filesystem_state,
                    current_workspace_root_norm,
                    command=command
                )
            except MetadataError as me:
                # Handle metadata operation failures in strict mode
                result_dict['message'] = f"Command failed: {str(me)}"
                result_dict['returncode'] = 1
                raise CommandExecutionError(result_dict['message'])

            # Determine final success status
            if background:
                if result_dict['pid'] is not None:
                    result_dict['message'] = command_message + " Workspace state updated."
            else:
                if result_dict['returncode'] is not None and isinstance(process_obj, subprocess.CompletedProcess):
                    result_dict['message'] = command_message + " Workspace state updated."
                    if process_obj.returncode != 0:
                        result_dict['message'] += f" (Note: Non-zero exit code {process_obj.returncode})."
        else:
            # Command failed to launch; restore pre-execution state
            _log_shell_message(logging.WARNING, f"Command '{command}' failed to launch. Restoring pre-execution workspace state.")
            DB["workspace_root"] = current_workspace_root_norm
            DB["cwd"] = current_cwd_norm
            DB["file_system"] = original_filesystem_state

    except PermissionError as e:
        # Errors related to execution environment setup/cleanup
        _log_shell_message(logging.ERROR, f"Execution environment error: {type(e).__name__} - {e}", exc_info=True)
        additional_msg = f" Error managing execution environment ({type(e).__name__})."
        result_dict['message'] = (result_dict.get('message') or f"Operation failed (environment error: {type(e).__name__})") + additional_msg
        if result_dict.get('returncode') is None: result_dict['returncode'] = 1
        raise CommandExecutionError(result_dict['message'])
    except Exception as e:
         # Catch-all for other unexpected errors
        _log_shell_message(logging.ERROR, f"Unexpected error during command execution phase for '{command}': {type(e).__name__} - {e}", exc_info=True)
        result_dict['message'] = f"Operation failed unexpectedly: {type(e).__name__} - {e}"
        if result_dict.get('returncode') is None: result_dict['returncode'] = 1

        # Attempt emergency state restoration
        _log_shell_message(logging.INFO, "Attempting emergency restoration of workspace state.")
        DB["workspace_root"] = current_workspace_root_norm
        DB["cwd"] = current_cwd_norm
        DB["file_system"] = original_filesystem_state
        raise CommandExecutionError(result_dict['message'])
    finally:
        # Ensure execution environment is cleaned up
        if temp_dir_obj:
            try:
                temp_dir_obj.cleanup()
                _log_shell_message(logging.DEBUG, f"Execution environment {temp_dir_obj.name} cleaned up.")
            except Exception as cleanup_e:
                 _log_shell_message(logging.ERROR, f"Failed to cleanup execution environment {temp_dir_obj.name}: {cleanup_e}", exc_info=True)

        # Final state restoration safeguard
        if DB.get("cwd") != current_cwd_norm:
            _log_shell_message(logging.WARNING, f"Restoring CWD to '{current_cwd_norm}' (was '{DB.get('cwd')}').")
            DB["cwd"] = current_cwd_norm
        if DB.get("workspace_root") != current_workspace_root_norm:
             _log_shell_message(logging.WARNING, f"Restoring workspace_root to '{current_workspace_root_norm}' (was '{DB.get('workspace_root')}').")
             DB["workspace_root"] = current_workspace_root_norm

        _log_shell_message(logging.DEBUG, f"run_shell_command finished. Final CWD='{DB.get('cwd')}'")

    # Consistency check
    if result_dict.get('pid') is not None and result_dict.get('returncode') is not None:
        _log_shell_message(logging.WARNING, "Result indicates both background (pid) and foreground (returncode) execution.")

    return result_dict

