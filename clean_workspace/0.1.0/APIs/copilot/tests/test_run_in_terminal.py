import unittest
import os
import shutil
import logging
import tempfile
import subprocess
from unittest.mock import patch

# Assuming your project structure allows these imports
# You might need to adjust them based on your project's root and PYTHONPATH
from copilot.SimulationEngine.db import DB
from copilot.SimulationEngine import utils, custom_errors

from copilot import run_in_terminal

# Configure a logger to capture output during tests
logger = logging.getLogger("copilot.command_line")

def minimal_reset_db(workspace_path: str):
    """Resets the in-memory DB to a clean state for each test, using a provided path."""
    DB.clear()
    # The provided path is already absolute and normalized from a temp directory
    workspace_path_for_db = utils._normalize_path_for_db(workspace_path)
    
    # Create the physical directory for the mock workspace. This is now in a temp location.
    os.makedirs(workspace_path_for_db, exist_ok=True)
    
    DB["workspace_root"] = workspace_path_for_db
    DB["cwd"] = workspace_path_for_db
    DB["file_system"] = {
        workspace_path_for_db: {
            "path": workspace_path_for_db,
            "is_directory": True,
            "content_lines": [],
            "size_bytes": 0,
            "last_modified": utils.get_current_timestamp_iso()
        }
    }
    DB["background_processes"] = {}
    DB["_next_pid"] = 1
    DB["last_edit_params"] = None

class TestRunInTerminal(unittest.TestCase):
    """
    A comprehensive test suite for the run_in_terminal function, covering core logic,
    internal commands, foreground execution, and background process launching.
    """

    @classmethod
    def setUpClass(cls):
        """Create a single temporary directory to be used as the base for all tests."""
        cls.base_temp_dir = tempfile.mkdtemp(prefix="copilot_test_runinterminal_")

    @classmethod
    def tearDownClass(cls):
        """Clean up the temporary directory after all tests in this class are done."""
        if os.path.exists(cls.base_temp_dir):
            shutil.rmtree(cls.base_temp_dir)

    def setUp(self):
        """Set up a clean database and a unique workspace for each test."""
        # Create a unique workspace path for each test to ensure isolation
        self.workspace_path = os.path.join(self.base_temp_dir, self.id())
        minimal_reset_db(self.workspace_path)
        self.workspace_root = DB["workspace_root"]

    def tearDown(self):
        """Clear the database and any leftover background process directories after each test."""
        for pid, proc_info in list(DB.get("background_processes", {}).items()):
            if "exec_dir" in proc_info and os.path.exists(proc_info["exec_dir"]):
                shutil.rmtree(proc_info["exec_dir"], ignore_errors=True)
        DB.clear()

    def _get_expected_path_key(self, relative_path: str) -> str:
        """Helper to get a normalized absolute path key for the DB."""
        return utils._normalize_path_for_db(os.path.join(self.workspace_root, relative_path))

    # --- Test Input Validation and Setup ---
    def test_empty_or_whitespace_command_string(self):
        """Test that empty or whitespace-only commands raise InvalidInputError."""
        with self.assertRaisesRegex(custom_errors.InvalidInputError, "Command string cannot be empty"):
            run_in_terminal(command="   ")
        with self.assertRaisesRegex(custom_errors.InvalidInputError, "Command string cannot be empty"):
            run_in_terminal(command="")

    def test_workspace_root_not_configured(self):
        """Test that a missing workspace_root raises TerminalNotAvailableError."""
        DB.clear()
        with self.assertRaisesRegex(custom_errors.TerminalNotAvailableError, "Workspace root is not configured"):
            run_in_terminal(command="echo hello")
            
    # --- Test Internal 'cd' and 'pwd' Commands ---
    def test_internal_pwd_command(self):
        """Test the internal 'pwd' command."""
        result = run_in_terminal("pwd")
        self.assertEqual(result['exit_code'], 0)
        self.assertEqual(result['stdout'], self.workspace_root)

    def test_internal_cd_to_subdir(self):
        """Test the internal 'cd' command to a subdirectory."""
        subdir_path = self._get_expected_path_key("my_dir")
        DB['file_system'][subdir_path] = {"path": subdir_path, "is_directory": True, "content_lines": [], "size_bytes": 0, "last_modified": ""}
        
        result = run_in_terminal("cd my_dir")
        self.assertEqual(result['exit_code'], 0)
        self.assertEqual(DB['cwd'], subdir_path)
        
        pwd_result = run_in_terminal("pwd")
        self.assertEqual(pwd_result['stdout'], subdir_path)

    def test_internal_cd_to_parent(self):
        """Test the internal 'cd ..' command."""
        subdir_path = self._get_expected_path_key("my_dir")
        os.makedirs(subdir_path, exist_ok=True)
        DB['cwd'] = subdir_path
        result = run_in_terminal("cd ..")
        self.assertEqual(result['exit_code'], 0)
        self.assertEqual(DB['cwd'], self.workspace_root)

    def test_internal_cd_failure(self):
        """Test that 'cd' to a non-existent directory fails correctly."""
        with self.assertRaisesRegex(custom_errors.CommandExecutionError, "Failed to change directory"):
            run_in_terminal("cd non_existent_dir")

    # --- Test Error Handling and Mocking ---
    def test_command_shlex_split_error(self):
        """Test that a command with unclosed quotes raises InvalidInputError."""
        with self.assertRaisesRegex(custom_errors.InvalidInputError, "Could not parse command string"):
            run_in_terminal(command="echo 'unclosed quote")

    @patch('copilot.command_line.tempfile.TemporaryDirectory')
    def test_temp_dir_creation_permission_error(self, mock_temp_dir_class):
        """Test that a PermissionError during temp dir creation is handled."""
        # The rest of the test remains the same.
        # We patch the class, and the side_effect applies when an instance is created.
        mock_temp_dir_class.side_effect = PermissionError("Permission denied")
        with self.assertRaisesRegex(custom_errors.TerminalNotAvailableError, "Failed to set up execution environment due to permissions: Permission denied"):
            run_in_terminal(command="echo hello")

    @patch('subprocess.run')
    def test_foreground_command_timeout(self, mock_subprocess_run):
        """Test that a command timeout is handled correctly."""
        mock_subprocess_run.side_effect = subprocess.TimeoutExpired(cmd="sleep 5", timeout=1)
        with self.assertRaisesRegex(custom_errors.CommandExecutionError, "timed out"):
            run_in_terminal(command="sleep 5")

    @patch('subprocess.run')
    def test_foreground_command_exception_restores_fs(self, mock_subprocess_run):
        """Test that the filesystem is restored after a generic command execution error."""
        file_path = self._get_expected_path_key('file.txt')
        DB['file_system'][file_path] = {"path": file_path, "is_directory": False, "content_lines": ["original"], "size_bytes": 8, "last_modified": ""}
        original_fs_copy = DB['file_system'].copy()
        mock_subprocess_run.side_effect = RuntimeError("mocked error")

        with self.assertRaisesRegex(custom_errors.CommandExecutionError, "mocked error"):
            run_in_terminal(command="some_failing_command")
        
        self.assertEqual(DB["file_system"], original_fs_copy)

    def test_command_not_found_logs_warning(self):
        """Test that a warning is logged when a command is not found by the shell."""
        non_existent_cmd = "a_very_unique_and_non_existent_command_123xyz"
        with self.assertLogs(logger, level='WARNING') as log_watcher:
            result = run_in_terminal(command=non_existent_cmd)
        
        self.assertNotEqual(result['exit_code'], 0)
        self.assertTrue(any(f"Command '{non_existent_cmd}' might not be found" in msg for msg in log_watcher.output))
        
    # --- Test Background Process Launching ---
    def test_background_launch_success(self):
        """Test the successful launch of a background process and its effect on the DB."""
        result = run_in_terminal("echo 'hello bg'", is_background=True)

        self.assertIsNotNone(result['terminal_id'])
        self.assertIsNone(result['exit_code'])
        self.assertIsNone(result['stdout'])
        self.assertIsNone(result['stderr'])
        self.assertEqual(len(DB['background_processes']), 1)
        
        pid = result['terminal_id']
        proc_info = DB['background_processes'][pid]
        self.assertEqual(proc_info['command'], "echo 'hello bg'")
        self.assertTrue(os.path.isdir(proc_info['exec_dir']))
        self.assertEqual(proc_info['last_stdout_pos'], 0)

    @patch('subprocess.Popen')
    def test_background_launch_failure_cleans_up(self, mock_popen):
        """Test that a failed background process launch cleans up its temporary directory."""
        mock_popen.side_effect = OSError("Launch failed")
        
        mock_temp_dir = os.path.join(self.base_temp_dir, "failed_launch_dir")

        # Patch mkdtemp to control the directory name, and rmtree to verify it's called
        with patch('tempfile.mkdtemp', return_value=mock_temp_dir) as mock_mkdtemp:
            with patch('shutil.rmtree') as mock_rmtree:
                with self.assertRaisesRegex(custom_errors.CommandExecutionError, "An unexpected error occurred: OSError - Launch failed"):
                    run_in_terminal("some command", is_background=True)
                
                mock_mkdtemp.assert_called_once()
                # Check that cleanup was called on the directory that mkdtemp would have created
                mock_rmtree.assert_called_once_with(mock_temp_dir)
        
        # Ensure no dangling process info was left in the DB
        self.assertEqual(len(DB['background_processes']), 0)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)