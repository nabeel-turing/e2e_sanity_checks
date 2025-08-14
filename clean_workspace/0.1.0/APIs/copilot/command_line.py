import os
import re
import logging
from typing import Any, Dict, List, Optional, Union
import warnings
import tempfile
import subprocess
import shlex
import logging
import inspect
import shutil

# Assuming these are in the same project/module and imported correctly
from .SimulationEngine.db import DB
from .SimulationEngine import utils
from .SimulationEngine import custom_errors

FOREGROUND_COMMAND_TIMEOUT_SECONDS = 60
logger = logging.getLogger(__name__)

# It's assumed you have this helper function in the same file
def _log_init_message(level: int, message: str, exc_info: bool = False) -> None:
    log_message = message
    try:
        frame = inspect.currentframe()
        caller_frame = frame.f_back
        if caller_frame and caller_frame.f_code:
            func_name = caller_frame.f_code.co_name
            line_no = caller_frame.f_lineno
            log_message = f"{func_name}:{line_no} - {message}"
    except Exception:
        pass
    if level == logging.ERROR: logger.error(log_message, exc_info=exc_info)
    elif level == logging.WARNING: logger.warning(log_message, exc_info=exc_info)
    elif level == logging.INFO: logger.info(log_message)
    else: logger.debug(log_message)


def run_in_terminal(command: str, is_background: bool = False) -> Dict[str, Any]:
    """Run a shell command in a terminal.

    This function runs a shell command in a terminal. The terminal state is persistent across tool calls.
    This tool is intended to be used instead of printing a shell codeblock and asking the user to run it.
    If the command is a long-running background process, the `is_background` parameter must be set to `True`.
    When a command is run in the background, the function returns a terminal ID, which can be used with
    `get_terminal_output` to check the output of the background process.
    If a command typically uses a pager (e.g., `git log`, `man`, `less`), the command MUST be modified
    to disable the pager (e.g., `git --no-pager log`) or its output must be piped to a non-pager
    command (e.g., `git log | cat`). Failure to handle pagers correctly may lead to stalled
    execution or unexpected behavior.

    Args:
        command (str): The shell command to execute. This is a required parameter.
            If the command typically uses a pager (e.g., `git log`, `man`, `less`),
            you MUST modify the command to disable the pager (e.g., `git --no-pager log`)
            or pipe its output to a non-pager command (e.g., `git log | cat`).
            Failure to do so may lead to stalled execution or unexpected behavior.
        is_background (bool): If true, the command runs as a background process, and the
            method returns immediately with a terminal ID. If false (default), the
            command runs in the foreground, and the method waits for completion before
            returning output. Defaults to false.

    Returns:
        Dict[str, Any]: Result of the terminal command execution. This dictionary contains the following keys:
            status_message (str): A message indicating the status of the command execution
                (e.g., 'Command started in background with ID X', 'Command executed successfully').
            terminal_id (Optional[str]): The ID of the terminal if the command is run in the
                background (is_background=True). This ID can be used with 'get_terminal_output'
                to fetch subsequent output. Null for foreground commands.
            stdout (Optional[str]): The standard output of the command if run in the foreground
                and completed. Null or empty for background commands or if there was no output.
            stderr (Optional[str]): The standard error output of the command if run in the
                foreground and completed. Null or empty for background commands or if there
                was no error output.
            exit_code (Optional[int]): The exit code of the command if run in the foreground
                and completed. Null for background commands (which are still running or for
                which the exit code is not immediately available via this method's direct return).

    Raises:
        CommandExecutionError: If the command fails to execute (e.g., command not found,
            syntax error in command, critical runtime error).
        TerminalNotAvailableError: If a terminal instance cannot be allocated or accessed.
        InvalidInputError: If required parameters like 'command' are missing or invalid.
    """

    global DB, utils

    if not command or command.isspace():
        _log_init_message(logging.ERROR, "Command string is empty or whitespace.")
        raise custom_errors.InvalidInputError("Command string cannot be empty.")

    current_workspace_root = DB.get("workspace_root")
    if not current_workspace_root:
        _log_init_message(logging.ERROR, "Operation failed: workspace_root is not configured.")
        raise custom_errors.TerminalNotAvailableError("Workspace root is not configured, terminal unavailable.")

    current_workspace_root_norm = utils._normalize_path_for_db(current_workspace_root)
    current_cwd_norm = utils._normalize_path_for_db(DB.get("cwd", current_workspace_root_norm))

    stripped_command = command.strip()
    if stripped_command == "cd" or stripped_command.startswith("cd "):
        _log_init_message(logging.INFO, f"Handling internal 'cd': {command}")
        parts = stripped_command.split(maxsplit=1)
        target_arg = parts[1] if len(parts) > 1 else "/"
        new_cwd_path = utils.resolve_target_path_for_cd(
            current_cwd_norm, target_arg, current_workspace_root_norm, DB.get("file_system", {})
        )
        if new_cwd_path:
            DB["cwd"] = new_cwd_path
            return {'status_message': f"Current directory changed to {utils._normalize_path_for_db(DB.get('cwd'))}",
                    'terminal_id': None, 'stdout': None, 'stderr': None, 'exit_code': 0}
        else:
            _log_init_message(logging.WARNING, f"cd: Failed to change directory to '{target_arg}'.")
            raise custom_errors.CommandExecutionError(
                f"cd: Failed to change directory to '{target_arg}'. Path may be invalid or outside workspace."
            )

    if stripped_command == "pwd":
        _log_init_message(logging.INFO, "Handling internal 'pwd'")
        pwd_path = utils._normalize_path_for_db(DB.get('cwd', current_workspace_root_norm))
        return {'status_message': f"Current directory: {pwd_path}", 'terminal_id': None,
                'stdout': pwd_path, 'stderr': None, 'exit_code': 0}

    temp_dir_obj: Optional[tempfile.TemporaryDirectory] = None
    temp_dir_path: Optional[str] = None
    exec_env_root: str
    try:
        if not is_background:
            temp_dir_obj = tempfile.TemporaryDirectory(prefix="cmd_exec_")
            exec_env_root = utils._normalize_path_for_db(temp_dir_obj.name)
        else:
            temp_dir_path = tempfile.mkdtemp(prefix="bg_cmd_exec_")
            exec_env_root = utils._normalize_path_for_db(temp_dir_path)
    except PermissionError as e:
        _log_init_message(logging.ERROR, f"Execution environment permission error: {e}", exc_info=True)
        raise custom_errors.TerminalNotAvailableError(f"Failed to set up execution environment due to permissions: {e}")

    original_filesystem_state = {k: v.copy() if isinstance(v, dict) else v for k, v in DB.get("file_system", {}).items()}
    try:
        # Validate command string before execution
        try:
            command_parts_for_validation = shlex.split(command)
            if not command_parts_for_validation:
                raise custom_errors.InvalidInputError("Command string parsed to empty arguments.")
        except ValueError as e:
            _log_init_message(logging.ERROR, f"Could not parse command string for validation: {command}", exc_info=True)
            raise custom_errors.InvalidInputError(f"Could not parse command string for validation: {e}")

        _log_init_message(logging.INFO, f"Preparing execution environment in: {exec_env_root}")
        utils.dehydrate_db_to_directory(DB, exec_env_root)
        _log_init_message(logging.INFO, "Workspace state copied to execution environment.")

        if current_cwd_norm.startswith(current_workspace_root_norm):
            relative_cwd = os.path.relpath(current_cwd_norm, current_workspace_root_norm)
            if relative_cwd == ".": relative_cwd = ""
        else:
            _log_init_message(logging.WARNING, f"Current directory '{current_cwd_norm}' is outside workspace root '{current_workspace_root_norm}'. Using environment root for command.")
            relative_cwd = ""

        subprocess_cwd_physical = utils._normalize_path_for_db(os.path.join(exec_env_root, relative_cwd))
        if not os.path.isdir(subprocess_cwd_physical):
            _log_init_message(logging.WARNING, f"Execution environment CWD '{subprocess_cwd_physical}' does not exist. Using environment root '{exec_env_root}'.")
            subprocess_cwd_physical = exec_env_root

        _log_init_message(logging.INFO, f"Executing command '{command}' in CWD '{subprocess_cwd_physical}' (Background: {is_background}) with shell=True")
        
        # --- Main Execution Logic ---
        status_msg, term_id, std_out, std_err, exit_c = "", None, None, None, None
        cmd_name_for_error = command_parts_for_validation[0]

        if is_background:
            # ... Background execution logic ...
            stdout_log = os.path.join(exec_env_root, 'stdout.log')
            stderr_log = os.path.join(exec_env_root, 'stderr.log')
            exitcode_log = os.path.join(exec_env_root, 'exitcode.log')
            
            # Convert to OS-specific paths and properly escape for shell
            stdout_log_esc = stdout_log.replace('\\', '\\\\').replace('"', '\\"') if os.name == 'nt' else stdout_log
            stderr_log_esc = stderr_log.replace('\\', '\\\\').replace('"', '\\"') if os.name == 'nt' else stderr_log
            exitcode_log_esc = exitcode_log.replace('\\', '\\\\').replace('"', '\\"') if os.name == 'nt' else exitcode_log
            
            # Use OS-appropriate command syntax
            if os.name == 'nt':  # Windows
                # Use Windows batch syntax with absolute paths
                wrapped_command = f'({command}) > "{stdout_log_esc}" 2> "{stderr_log_esc}" & echo %ERRORLEVEL% > "{exitcode_log_esc}"'
            else:  # Unix/Linux/macOS
                wrapped_command = f"exec > \"{stdout_log}\" 2> \"{stderr_log}\"; ({command}); echo $? > \"{exitcode_log}\""
            
            process_obj = subprocess.Popen(
                wrapped_command, cwd=subprocess_cwd_physical, shell=True, start_new_session=True
            )
            term_id = str(process_obj.pid)
            DB["background_processes"][term_id] = {
                "pid": process_obj.pid, "command": command, "exec_dir": exec_env_root,
                "stdout_path": stdout_log, "stderr_path": stderr_log, "exitcode_path": exitcode_log,
                "last_stdout_pos": 0, "last_stderr_pos": 0,
            }
            temp_dir_path = None  # Prevent cleanup in the finally block for successful launch
            status_msg = f"Command '{command}' started in background with ID {term_id}."
            _log_init_message(logging.INFO, status_msg)
        else:
            # ... Foreground execution logic ...
            try:
                process_obj = subprocess.run(
                    command, cwd=subprocess_cwd_physical, capture_output=True, text=True,
                    encoding='utf-8', errors='replace', check=False, shell=True,
                    timeout=FOREGROUND_COMMAND_TIMEOUT_SECONDS
                )
                exit_c, std_out, std_err = process_obj.returncode, process_obj.stdout, process_obj.stderr
                if exit_c == 0:
                    status_msg = f"Command '{command}' executed successfully."
                else:
                    status_msg = f"Command '{command}' completed with exit code {exit_c}."
                    if ("not found" in std_err.lower() or 
                        "no such file" in std_err.lower() or 
                        "is not recognized as an internal or external command" in std_err.lower() or
                        exit_c == 127):
                         _log_init_message(logging.WARNING, f"Command '{cmd_name_for_error}' might not be found or other execution error. Stderr: {std_err.strip()}")
                _log_init_message(logging.INFO, f"{status_msg} Stdout: {len(std_out)} chars, Stderr: {len(std_err)} chars.")
                utils.update_db_file_system_from_temp(exec_env_root, original_filesystem_state, current_workspace_root_norm)
                _log_init_message(logging.INFO, "Workspace state updated after foreground command completion.")
            except subprocess.TimeoutExpired:
                _log_init_message(logging.ERROR, f"Foreground command '{command}' timed out after {FOREGROUND_COMMAND_TIMEOUT_SECONDS} seconds.")
                utils.update_db_file_system_from_temp(exec_env_root, original_filesystem_state, current_workspace_root_norm)
                raise custom_errors.CommandExecutionError(f"Command '{command}' timed out.")
        
        return {
            'status_message': status_msg, 'terminal_id': term_id, 'stdout': std_out if std_out else None,
            'stderr': std_err if std_err else None, 'exit_code': exit_c
        }

    except (custom_errors.InvalidInputError, custom_errors.CommandExecutionError):
        DB["file_system"] = original_filesystem_state
        raise
    except Exception as e:
        _log_init_message(logging.ERROR, f"Unexpected error during command execution for '{command}': {type(e).__name__} - {e}", exc_info=True)
        DB["file_system"] = original_filesystem_state
        raise custom_errors.CommandExecutionError(f"An unexpected error occurred: {type(e).__name__} - {e}")
    finally:
        if temp_dir_obj:
            try:
                temp_dir_obj.cleanup()
                _log_init_message(logging.DEBUG, f"Execution environment {temp_dir_obj.name} cleaned up.")
            except Exception as cleanup_e:
                 _log_init_message(logging.ERROR, f"Failed to cleanup execution environment {temp_dir_obj.name}: {cleanup_e}", exc_info=True)
        elif temp_dir_path:
            try:
                shutil.rmtree(temp_dir_path)
                _log_init_message(logging.DEBUG, f"Cleaned up failed background launch directory {temp_dir_path}.")
            except Exception as cleanup_e:
                _log_init_message(logging.ERROR, f"Failed to cleanup failed background launch directory {temp_dir_path}: {cleanup_e}", exc_info=True)
        
        if "cd " not in stripped_command and stripped_command != "cd":
            if DB.get("cwd") != current_cwd_norm:
                _log_init_message(logging.WARNING, f"Restoring CWD to '{current_cwd_norm}' (was '{DB.get('cwd')}').")
                DB["cwd"] = current_cwd_norm
        if DB.get("workspace_root") != current_workspace_root_norm:
             _log_init_message(logging.WARNING, f"Restoring workspace_root to '{current_workspace_root_norm}' (was '{DB.get('workspace_root')}').")
             DB["workspace_root"] = current_workspace_root_norm
        _log_init_message(logging.DEBUG, f"run_in_terminal finished. Final CWD='{DB.get('cwd')}'")


def get_terminal_output(terminal_id: str) -> Dict[str, Any]:
    """Retrieves the output and status for a terminal process.

    This function is used to get the standard output (stdout), standard error (stderr),
    running status, and exit code of a terminal command that was previously
    started.

    When called, it attempts to read any new output generated by the process
    since the last call for the same `terminal_id`. If the process has finished,
    this function will retrieve any output, the final exit code.

    Args:
        terminal_id (str): The ID of the background terminal process. This ID should
            have been returned by the function that initiated the background process.
            It must be a string containing only digits.

    Returns:
        Dict[str, Any]: A dictionary containing the output and status information:
            - "terminal_id" (str): The ID of the terminal for which output was retrieved.
            - "stdout" (str): A chunk of standard output from the command since the
              last retrieval. If the process just finished, this includes all remaining
              unread output.
            - "stderr" (str): A chunk of standard error output from the command since
              the last retrieval. If the process just finished, this includes all
              remaining unread error output. Can also contain messages if the process
              terminated unexpectedly.
            - "is_still_running" (bool): True if the process is still active,
              False if it has completed or terminated.
            - "exit_code" (Optional[int]): The exit code of the command if it has
              finished. This will be None if the process is still running.
              An exit code of -1 may indicate an unexpected termination where
              the standard exit code could not be retrieved.

    Raises:
        TypeError: If `terminal_id` is not a string.
        InvalidInputError: If `terminal_id` is empty, consists only
            of whitespace, or is not a string containing only digits.
        InvalidTerminalIdError: If the provided `terminal_id` does not
            correspond to any known or active background process.
        OutputRetrievalError: If an error occurs while trying to
            access the output files or if the execution environment for the
            terminal process is found to be in an inconsistent state (e.g.,
            execution directory deleted prematurely). This can also be raised
            for other unexpected errors during output retrieval.
    """
    global DB

    # --- NEW: Input Validation Block ---
    if not isinstance(terminal_id, str):
        raise TypeError("Terminal ID must be a string.")
    
    if not terminal_id or not terminal_id.strip():
        raise custom_errors.InvalidInputError("Terminal ID cannot be empty or whitespace.")

    if not terminal_id.isdigit():
        raise custom_errors.InvalidInputError(f"Terminal ID '{terminal_id}' is invalid; it must be a string containing only digits.")
    # --- END: Input Validation Block ---

    if terminal_id not in DB.get("background_processes", {}):
        raise custom_errors.InvalidTerminalIdError(f"Terminal ID '{terminal_id}' is invalid or does not exist.")

    proc_info = DB["background_processes"][terminal_id]
    stdout_chunk = ""
    stderr_chunk = ""
    is_running = True
    exit_code = None

    try:
        # The signal of completion is the existence of the exitcode file.
        if os.path.exists(proc_info["exitcode_path"]):
            is_running = False
            with open(proc_info["exitcode_path"], "r", encoding='utf-8', errors='replace') as f:
                exit_code = int(f.read().strip())

            # Read any final output that hasn't been consumed
            with open(proc_info["stdout_path"], "r", encoding='utf-8', errors='replace') as f:
                f.seek(proc_info["last_stdout_pos"])
                stdout_chunk = f.read()

            with open(proc_info["stderr_path"], "r", encoding='utf-8', errors='replace') as f:
                f.seek(proc_info["last_stderr_pos"])
                stderr_chunk = f.read()

            # Process is finished, perform cleanup
            shutil.rmtree(proc_info["exec_dir"], ignore_errors=True)
            del DB["background_processes"][terminal_id]
            _log_init_message(logging.INFO, f"Cleaned up resources for finished terminal ID {terminal_id}.")

        else: # Process is still running
            # Check if the process is truly running on the system
            try:
                os.kill(int(terminal_id), 0)
            except OSError:
                # Process doesn't exist, but exitcode file wasn't written. This indicates an abrupt termination.
                is_running = False
                exit_code = -1 # Or some other indicator of an abnormal exit
                stderr_chunk = "Process terminated unexpectedly without writing an exit code."
                
                # Cleanup
                shutil.rmtree(proc_info["exec_dir"], ignore_errors=True)
                del DB["background_processes"][terminal_id]
                _log_init_message(logging.WARNING, f"Process {terminal_id} disappeared. Cleaned up resources.")
            
            if is_running:
                with open(proc_info["stdout_path"], "r", encoding='utf-8', errors='replace') as f:
                    f.seek(proc_info["last_stdout_pos"])
                    stdout_chunk = f.read()
                    proc_info["last_stdout_pos"] = f.tell()

                with open(proc_info["stderr_path"], "r", encoding='utf-8', errors='replace') as f:
                    f.seek(proc_info["last_stderr_pos"])
                    stderr_chunk = f.read()
                    proc_info["last_stderr_pos"] = f.tell()

    except FileNotFoundError:
        # This could happen if the exec_dir was deleted externally
        del DB["background_processes"][terminal_id]
        raise custom_errors.OutputRetrievalError(
            f"Could not retrieve output for terminal {terminal_id}; execution environment may have been manually deleted."
        )
    except Exception as e:
        _log_init_message(logging.ERROR, f"Error retrieving output for {terminal_id}: {e}", exc_info=True)
        raise custom_errors.OutputRetrievalError(f"An unexpected error occurred while retrieving output for terminal {terminal_id}: {e}")

    return {
        "terminal_id": terminal_id,
        "stdout": stdout_chunk,
        "stderr": stderr_chunk,
        "is_still_running": is_running,
        "exit_code": exit_code,
    }