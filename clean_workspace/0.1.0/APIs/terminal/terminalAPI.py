import os
import logging
from typing import Any, Dict, Optional, Union  # Common type hints
import tempfile
import subprocess
import shlex
import inspect
from pathlib import Path

# Import the DB object and utility functions
from .SimulationEngine.db import DB
from .SimulationEngine.custom_errors import CommandExecutionError
from .SimulationEngine import utils
from .SimulationEngine.custom_errors import MetadataError
from .SimulationEngine.utils import with_common_file_system  # Import the decorator

# Import the environment manager
from .SimulationEngine.env_manager import (
    prepare_command_environment,
    expand_variables,
    handle_env_command
)

# --- Logger Setup for this __init__.py module ---
# Get a logger instance specific to this top-level module.
logger = logging.getLogger(__name__) # Will typically be 'terminal' if run as package

def _log_init_message(level: int, message: str, exc_info: bool = False) -> None:
    """Logs a message with caller info (function:lineno) from within this module."""
    log_message = message
    try:
        # Get the frame of the function within __init__.py that called this helper.
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


# --- Function Implementations ---
@with_common_file_system
def run_command(command: str, is_background: bool = False) -> Dict[str, Any]:
    """Executes the provided terminal command in the current workspace context.

    Use this function to run shell commands. You need to provide the exact
    command string to be executed. Note that commands like 'cd', 'pwd', and
    environment commands ('export', 'unset', 'env') are handled internally;
    other commands are executed externally and may modify the workspace files.

    IMPORTANT: For any command that expects user interaction or uses a pager
    (like git diff, git log, less, more, etc.), you MUST append
    ' | cat' to the command string yourself before passing it to this function.
    Failure to do so will cause the command to hang or fail.

    For commands that are intended to run for a long time or indefinitely
    (e.g., starting a server, running a watch process), set the
    `is_background` parameter to True.

    Args:
        command (str): The exact terminal command string to execute. Remember
                       to append ' | cat' for interactive/pager commands.
        is_background (bool, optional): Set to True to run the command as a
            background process (e.g., for servers or watchers). Defaults to False,
            running the command in the foreground and waiting for completion.

    Returns:
        Dict[str, Any]: A dictionary describing the outcome:
            - 'message' (str): A status message about the execution.
            - 'stdout' (str): Captured standard output (foreground only).
            - 'stderr' (str): Captured standard error (foreground only).
            - 'returncode' (Optional[int]): The command's exit code
                                           (foreground only).
            - 'pid' (Optional[int]): The process ID if run in the background.

    Raises:
        ValueError: If workspace_root is not configured or the command string is empty/invalid.
        CommandExecutionError: If a command fails to launch, `cd` fails, or a foreground command returns a non-zero exit code.
    """
    # Use global DB state and utils module
    global DB, utils

    result_dict: Dict[str, Any] = {
        'message': "Initialization error.",
        'stdout': "", 'stderr': "", 'returncode': None, 'pid': None
    }

    # --- Get current workspace root and CWD ---
    current_workspace_root = DB.get("workspace_root")
    if not current_workspace_root:
        result_dict['message'] = "Operation failed: workspace_root is not configured."
        _log_init_message(logging.ERROR, result_dict['message'])
        raise ValueError(result_dict['message'])

    # Normalize paths for internal use
    current_workspace_root_norm = utils._normalize_path_for_db(current_workspace_root)
    current_cwd_norm = utils._normalize_path_for_db(DB.get("cwd", current_workspace_root_norm))

    # --- Handle internal commands ---
    stripped_command = command.strip()

    # Handle environment variable commands
    if stripped_command in ('env',) or stripped_command.startswith(('export ', 'unset ')):
        return handle_env_command(stripped_command, DB)

    # Handle cd and pwd as before
    if stripped_command == "cd" or stripped_command.startswith("cd "):
        _log_init_message(logging.INFO, f"Handling internal 'cd': {command}")
        parts = stripped_command.split(maxsplit=1)
        target_arg = parts[1] if len(parts) > 1 else "/" # Default 'cd' target

        # Resolve target path within the workspace
        new_cwd_path = utils.resolve_target_path_for_cd(
            current_cwd_norm,
            target_arg,
            current_workspace_root_norm,
            DB.get("file_system", {})
        )
        if new_cwd_path:
            DB["cwd"] = new_cwd_path # Update current working directory state
            result_dict['message'] = f"Current directory changed to {utils._normalize_path_for_db(DB.get('cwd'))}"
            result_dict['returncode'] = 0
            return result_dict
        else:
            result_dict['message'] = f"cd: Failed to change directory to '{target_arg}'. Path may be invalid or outside workspace."
            result_dict['returncode'] = 1
            _log_init_message(logging.WARNING, result_dict['message'])
            raise CommandExecutionError(result_dict['message'])

    if stripped_command == "pwd":
        _log_init_message(logging.INFO, "Handling internal 'pwd'")
        pwd_path = utils._normalize_path_for_db(DB.get('cwd', current_workspace_root_norm))
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
        exec_env_root = utils._normalize_path_for_db(temp_dir_obj.name)
        _log_init_message(logging.INFO, f"Preparing execution environment in: {exec_env_root}")

        # Copy workspace state to the execution environment
        utils.dehydrate_db_to_directory(DB, exec_env_root)
        pre_command_state_temp = {
            path: {"metadata": utils._collect_file_metadata(path)}
            for path, _ in DB.get("file_system", {}).items()
        }
        _log_init_message(logging.INFO, "Workspace state copied to execution environment.")

        # Determine the correct CWD within the execution environment
        if current_cwd_norm.startswith(current_workspace_root_norm):
            relative_cwd = os.path.relpath(current_cwd_norm, current_workspace_root_norm)
        else:
            # Fallback if CWD was somehow outside root
            _log_init_message(logging.WARNING, f"Current directory '{current_cwd_norm}' is outside workspace root '{current_workspace_root_norm}'. Using environment root for command.")
            relative_cwd = "."

        # Construct the path for the subprocess CWD
        subprocess_cwd_physical = utils._normalize_path_for_db(os.path.join(exec_env_root, relative_cwd))

        # Verify the execution CWD exists
        if not os.path.isdir(subprocess_cwd_physical):
            _log_init_message(logging.WARNING, f"Execution environment CWD '{subprocess_cwd_physical}' does not exist. Creating directory structure.")
            # Create the missing directory structure
            try:
                os.makedirs(subprocess_cwd_physical, exist_ok=True)
                _log_init_message(logging.INFO, f"Created missing directory: {subprocess_cwd_physical}")
            except Exception as e:
                _log_init_message(logging.ERROR, f"Failed to create directory '{subprocess_cwd_physical}': {e}")
                # Fall back to using the temp directory root
                subprocess_cwd_physical = exec_env_root
                if not os.path.isdir(subprocess_cwd_physical):
                    _log_init_message(logging.ERROR, f"Even temp directory root '{exec_env_root}' does not exist!")
                    raise CommandExecutionError(f"Execution environment setup failed: temp directory '{exec_env_root}' does not exist")

        # Create any missing parent directories for output redirection
        try:
            redir_target = utils._extract_last_unquoted_redirection_target(stripped_command)
        except Exception:
            redir_target = None
        if redir_target:
            output_file = redir_target
            # Convert relative path to absolute
            if not os.path.isabs(output_file):
                output_file = os.path.join(subprocess_cwd_physical, output_file)
            # Create parent directory if needed
            parent_dir = os.path.dirname(output_file)
            if parent_dir and not os.path.exists(parent_dir):
                try:
                    os.makedirs(parent_dir, exist_ok=True)
                    _log_init_message(logging.INFO, f"Created parent directory for output redirection: {parent_dir}")
                except Exception as e:
                    _log_init_message(logging.ERROR, f"Failed to create parent directory '{parent_dir}': {e}")
                    raise CommandExecutionError(f"Failed to create parent directory for output redirection: {e}")

        _log_init_message(logging.INFO, f"Executing command '{command}' in CWD '{subprocess_cwd_physical}' (Background: {is_background})")

        # Prepare environment and expand variables
        cmd_env = prepare_command_environment(DB, subprocess_cwd_physical)

        # Don't expand variables in the command string, let bash handle it
        expanded_command = command.strip()

        if not expanded_command:
            result_dict['message'] = "Operation failed: Command string is empty."
            _log_init_message(logging.ERROR, result_dict['message'])
            raise ValueError(result_dict['message'])

        # --- Execute the command ---
        process_obj: Union[subprocess.Popen, subprocess.CompletedProcess, None] = None
        if is_background:
            try:
                # Launch background process with environment
                with open(os.devnull, 'wb') as devnull:
                    process_obj = subprocess.Popen(
                        ['/bin/bash', '-c', expanded_command],
                        cwd=subprocess_cwd_physical,
                        stdout=devnull,
                        stderr=devnull,
                        env=cmd_env
                    )
                process_executed_without_launch_error = True
                result_dict['pid'] = process_obj.pid
                result_dict['returncode'] = None
                command_message = f"Command '{command}' launched successfully in background (PID: {process_obj.pid})."
            except FileNotFoundError:
                command_message = f"Launch failed: Command not found."
                _log_init_message(logging.ERROR, command_message)
                result_dict['message'] = command_message; result_dict['returncode'] = 127
                raise CommandExecutionError(result_dict['message'])
            except Exception as e:
                command_message = f"Launch failed for background process '{command}': {type(e).__name__} - {e}"
                _log_init_message(logging.ERROR, command_message, exc_info=True)
                result_dict['message'] = command_message; result_dict['returncode'] = 1
                raise CommandExecutionError(result_dict['message'])
        else: # Foreground execution
            try:
                # Run foreground process with environment
                process_obj = subprocess.run(
                    ['/bin/bash', '-c', expanded_command],
                    cwd=subprocess_cwd_physical,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    check=False,
                    env=cmd_env
                )
                process_executed_without_launch_error = True
                command_message = f"Command completed with exit code {process_obj.returncode}."
                result_dict['stdout'] = process_obj.stdout
                result_dict['stderr'] = process_obj.stderr
                result_dict['returncode'] = process_obj.returncode
                if process_obj.returncode != 0:
                    result_dict['message'] = f"Command failed with exit code {process_obj.returncode}. Workspace state updated.\nStderr: {process_obj.stderr}"
                    # Restore workspace state before raising exception for failed commands
                    _log_init_message(logging.WARNING, f"Command '{command}' failed with exit code {process_obj.returncode}. Restoring pre-execution workspace state.")
                    DB["workspace_root"] = current_workspace_root_norm
                    DB["cwd"] = current_cwd_norm
                    DB["file_system"] = original_filesystem_state
                    raise CommandExecutionError(result_dict['message'])
            except FileNotFoundError:
                command_message = f"Execution failed: Command not found."
                _log_init_message(logging.ERROR, command_message)
                result_dict['message'] = command_message; result_dict['returncode'] = 127
                raise CommandExecutionError(result_dict['message'])
            except Exception as e:
                command_message = f"Execution failed for foreground process '{command}': {type(e).__name__} - {e}"
                _log_init_message(logging.ERROR, command_message, exc_info=True)
                result_dict['message'] = command_message
                if result_dict.get('returncode') is None: result_dict['returncode'] = 1
                raise CommandExecutionError(result_dict['message'])

        # --- Post-execution state update ---
        if process_executed_without_launch_error:
            _log_init_message(logging.INFO, f"Command '{command}' execution finished. Updating workspace state.")
            try:
                post_command_state_temp = {
                    path: {"metadata": utils._collect_file_metadata(path)}
                    for path, _ in DB.get("file_system", {}).items()
                }
                # Update the main workspace state from the execution environment
                utils.update_db_file_system_from_temp(
                    exec_env_root,
                    original_filesystem_state,
                    current_workspace_root_norm,
                    command=command
                )

                # Only sync 'change_time' if it changed during command execution (e.g., 'echo "hello {time.time()}" > Datasets/test.txt' changes it, 'pwd' or 'ls -la' does not).
                for path, file_info in DB.get("file_system", {}).items():
                    # Safely construct the corresponding path inside the execution environment.
                    # Use realpath/commonpath to avoid ValueError from Path.relative_to when roots differ
                    # (e.g., macOS /var vs /private/var or test temp roots).
                    try:
                        real_path = os.path.realpath(path)
                        real_ws_root = os.path.realpath(current_workspace_root_norm)

                        # Only attempt mapping if the file is within the logical workspace root
                        if os.path.commonpath([real_path, real_ws_root]) != real_ws_root:
                            continue

                        rel_from_ws = os.path.relpath(real_path, start=real_ws_root)
                        tmp_path = utils._normalize_path_for_db(os.path.join(exec_env_root, rel_from_ws))
                    except Exception:
                        # If anything goes wrong, skip mapping for this file
                        continue

                    pre_change_time = pre_command_state_temp.get(tmp_path, {}).get("metadata", {}).get("timestamps", {}).get("change_time")
                    post_change_time = post_command_state_temp.get(tmp_path, {}).get("metadata", {}).get("timestamps", {}).get("change_time")
                    if pre_change_time == post_change_time:
                        file_info["metadata"]["timestamps"]["change_time"] = original_filesystem_state.get(path, {}).get("metadata", {}).get("timestamps", {}).get("change_time")
            except MetadataError as me:
                # Handle metadata operation failures in strict mode
                result_dict['message'] = f"Command failed: {str(me)}"
                result_dict['returncode'] = 1
                raise CommandExecutionError(result_dict['message'])

            # Determine final success status
            if is_background:
                if result_dict['pid'] is not None:
                    result_dict['message'] = command_message + " Workspace state updated."
            else:
                if result_dict['returncode'] is not None and isinstance(process_obj, subprocess.CompletedProcess):
                    result_dict['message'] = command_message + " Workspace state updated."
                    # Restore cwd, as external commands don't persistently change the directory
                    DB["cwd"] = current_cwd_norm
                    if process_obj.returncode != 0:
                        result_dict['message'] += f" (Note: Non-zero exit code {process_obj.returncode})."
        else:
            # Command failed to launch; restore pre-execution state
            _log_init_message(logging.WARNING, f"Command '{command}' failed to launch. Restoring pre-execution workspace state.")
            DB["workspace_root"] = current_workspace_root_norm
            DB["cwd"] = current_cwd_norm
            DB["file_system"] = original_filesystem_state

    except PermissionError as e:
        # Errors related to execution environment setup/cleanup
        _log_init_message(logging.ERROR, f"Execution environment error: {type(e).__name__} - {e}", exc_info=True)
        additional_msg = f" Error managing execution environment ({type(e).__name__})."
        result_dict['message'] = (result_dict.get('message') or f"Operation failed (environment error: {type(e).__name__})") + additional_msg
        if result_dict.get('returncode') is None: result_dict['returncode'] = 1
        raise CommandExecutionError(result_dict['message'])
    except Exception as e:
         # Catch-all for other unexpected errors
        _log_init_message(logging.ERROR, f"Unexpected error during command execution phase for '{command}': {type(e).__name__} - {e}", exc_info=True)
        result_dict['message'] = f"Operation failed unexpectedly: {type(e).__name__} - {e}"
        if result_dict.get('returncode') is None: result_dict['returncode'] = 1

        # Attempt emergency state restoration
        _log_init_message(logging.INFO, "Attempting emergency restoration of workspace state.")
        DB["workspace_root"] = current_workspace_root_norm
        DB["cwd"] = current_cwd_norm
        DB["file_system"] = original_filesystem_state
        raise CommandExecutionError(result_dict['message'])

    finally:
        # Always clean up the temporary directory
        if temp_dir_obj:
            try:
                temp_dir_obj.cleanup()
            except Exception as e:
                _log_init_message(logging.WARNING, f"Failed to clean up temporary directory: {e}")

    return result_dict

