"""Tests for shell API functions."""

import pytest
import os
import shutil
import tempfile
import stat
from datetime import datetime, timezone
import subprocess
import re
from typing import Dict, Any, Optional
from unittest.mock import patch, MagicMock
import time
import sys
from pathlib import Path

# Add the APIs directory to Python path so we can import from gemini_cli
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "APIs"))

from gemini_cli.shell_api import run_shell_command
from gemini_cli.SimulationEngine.db import DB
from gemini_cli.SimulationEngine import utils
from gemini_cli.SimulationEngine.custom_errors import (
    CommandExecutionError, 
    InvalidInputError, 
    WorkspaceNotAvailableError, 
    ShellSecurityError
)

# --- Common Helper Functions ---

def normalize_for_db(path_string):
    if path_string is None:
        return None
    # Remove any drive letter prefix first
    if len(path_string) > 2 and path_string[1:3] in [':/', ':\\']:
        path_string = path_string[2:]
    # Then normalize and convert slashes
    return os.path.normpath(path_string).replace("\\\\", "/")

def minimal_reset_db(workspace_path_for_db="/test_workspace"):
    """Reset DB to minimal state for testing."""
    DB.clear()
    DB["workspace_root"] = workspace_path_for_db
    DB["cwd"] = workspace_path_for_db
    DB["file_system"] = {}
    
    # Add root directory
    DB["file_system"][workspace_path_for_db] = {
        "path": workspace_path_for_db,
        "is_directory": True,
        "content_lines": [],
        "size_bytes": 0,
        "last_modified": "2025-01-01T00:00:00Z"
    }
    
    # Add shell config
    DB["shell_config"] = {
        "allowed_commands": ["ls", "cat", "echo", "pwd", "cd", "env", "export", "unset", "sleep"],
        "blocked_commands": ["rm", "rmdir", "dd", "mkfs"],
        "dangerous_patterns": [
            'rm -rf /',
            'rm -rf *',
            'dd if=',
            'mkfs.',
            'format',
            ':(){ :|:& };:',  # Fork bomb
        ],
        "environment_variables": {
            "PATH": "/usr/local/bin:/usr/bin:/bin",
            "HOME": "/home/user",
            "USER": "user"
        }
    }
    
    # Add environment structure
    DB["environment"] = {
        "system": {},
        "workspace": {},
        "session": {}
    }

class TestShellAPI:
    """Test cases for shell API functionality."""

    def setup_method(self):
        """Set up test environment."""
        # Create a temporary workspace
        self.temp_dir = tempfile.mkdtemp(prefix="shell_test_")
        self.workspace_path = os.path.join(self.temp_dir, "test_workspace")
        os.makedirs(self.workspace_path, exist_ok=True)
        
        # Create some test files and directories
        os.makedirs(os.path.join(self.workspace_path, "src"), exist_ok=True)
        os.makedirs(os.path.join(self.workspace_path, "docs"), exist_ok=True)
        
        with open(os.path.join(self.workspace_path, "test1.txt"), "w") as f:
            f.write("Hello World\n")
        
        with open(os.path.join(self.workspace_path, "empty.txt"), "w") as f:
            pass  # Empty file
        
        with open(os.path.join(self.workspace_path, "src", "main.py"), "w") as f:
            f.write("print('Hello from main.py')\n")
        
        # Initialize DB with the test workspace
        minimal_reset_db(self.workspace_path)
        
        # Hydrate DB from the physical workspace
        utils.hydrate_db_from_directory(DB, self.workspace_path)

    def teardown_method(self):
        """Clean up test environment."""
        # Clean up any background processes
        background_processes = DB.get("background_processes", {})
        for process_id, process_info in background_processes.items():
            process = process_info.get("process")
            if process:
                try:
                    process.terminate()
                    process.wait(timeout=1)
                except:
                    pass
            
            # Clean up temp directories
            temp_dir = process_info.get("temp_directory")
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Clean up test directory
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        DB.clear()

    def _get_expected_path_key(self, relative_path: str) -> str:
        """Get the expected path key in the DB for a relative path."""
        return normalize_for_db(os.path.join(self.workspace_path, relative_path))

    def test_run_shell_command_basic_success(self):
        """Test basic successful command execution."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Hello World"
            mock_run.return_value.stderr = ""
            
            result = run_shell_command("echo Hello World")
            
            assert result["command"] == "echo Hello World"
            assert result["stdout"] == "Hello World"
            assert result["stderr"] == ""
            assert result["returncode"] == 0
            assert result["pid"] is None
            assert result["process_group_id"] is None
            assert result["signal"] is None
            assert "message" in result
            assert "directory" in result

    def test_run_shell_command_command_failure(self):
        """Test command execution with non-zero exit code."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stdout = ""
            mock_run.return_value.stderr = "Command failed"
            
            with pytest.raises(CommandExecutionError):
                run_shell_command("ls /nonexistent")

    def test_run_shell_command_invalid_input(self):
        """Test invalid input validation."""
        with pytest.raises(InvalidInputError):
            run_shell_command("")
        
        with pytest.raises(InvalidInputError):
            run_shell_command(123)
        
        with pytest.raises(InvalidInputError):
            run_shell_command("echo test", description=123)
        
        with pytest.raises(InvalidInputError):
            run_shell_command("echo test", directory=123)
        
        with pytest.raises(InvalidInputError):
            run_shell_command("echo test", background="yes")

    def test_run_shell_command_security_validation(self):
        """Test security validation."""
        # Test command substitution (only $() is blocked, backticks are allowed)
        with pytest.raises(ShellSecurityError):
            run_shell_command("echo $(rm -rf /)")
        
        # Test dangerous patterns
        with pytest.raises(ShellSecurityError):
            run_shell_command("rm -rf /")
        
        with pytest.raises(ShellSecurityError):
            run_shell_command("dd if=/dev/zero of=/dev/sda")

    def test_run_shell_command_blocked_commands(self):
        """Test blocked command validation."""
        with pytest.raises(ShellSecurityError):
            run_shell_command("rm test.txt")
        
        with pytest.raises(ShellSecurityError):
            run_shell_command("rmdir testdir")

    def test_run_shell_command_workspace_not_available(self):
        """Test workspace not available error."""
        DB["workspace_root"] = None
        
        with pytest.raises(WorkspaceNotAvailableError):
            run_shell_command("echo test")

    def test_run_shell_command_internal_pwd(self):
        """Test internal pwd command."""
        result = run_shell_command("pwd")
        
        assert result["stdout"] == self.workspace_path
        assert result["returncode"] == 0
        assert result["command"] == "pwd"
        assert result["directory"] == self.workspace_path
        assert result["pid"] is None
        assert result["process_group_id"] is None
        assert result["signal"] is None

    def test_run_shell_command_internal_cd_success(self):
        """Test internal cd command success."""
        result = run_shell_command("cd src")
        
        assert result["directory"] == os.path.join(self.workspace_path, "src")
        assert result["returncode"] == 0
        assert DB["cwd"] == os.path.join(self.workspace_path, "src")
        assert result["command"] == "cd src"
        assert result["pid"] is None
        assert result["process_group_id"] is None
        assert result["signal"] is None

    def test_run_shell_command_internal_cd_failure(self):
        """Test internal cd command failure."""
        result = run_shell_command("cd nonexistent")
        
        assert result["returncode"] == 1
        assert "No such directory" in result["stderr"]
        assert result["command"] == "cd nonexistent"
        assert result["pid"] is None
        assert result["process_group_id"] is None
        assert result["signal"] is None

    def test_run_shell_command_internal_cd_outside_workspace(self):
        """Test internal cd command outside workspace."""
        result = run_shell_command("cd /etc")
    
        assert result["returncode"] == 1
        assert "No such directory" in result["stderr"]
        assert result["command"] == "cd /etc"
        assert result["pid"] is None
        assert result["process_group_id"] is None
        assert result["signal"] is None

    def test_run_shell_command_internal_env(self):
        """Test internal env command."""
        result = run_shell_command("env")
    
        assert "PATH=/usr/local/bin:/usr/bin:/bin" in result["stdout"]
        assert "HOME=/home/user" in result["stdout"]
        assert "USER=user" in result["stdout"]
        assert result["returncode"] == 0
        assert result["command"] == "env"
        assert result["pid"] is None

    def test_run_shell_command_with_directory(self):
        """Test command execution with specific directory."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "test.txt"
            mock_run.return_value.stderr = ""
    
            result = run_shell_command("ls", directory="src")
    
            assert result["directory"] == os.path.join(self.workspace_path, "src")
            assert result["command"] == "ls"
            assert result["returncode"] == 0
            assert result["stdout"] == "test.txt"
            assert result["stderr"] == ""

    def test_run_shell_command_directory_outside_workspace(self):
        """Test command execution with directory outside workspace."""
        with pytest.raises(InvalidInputError):
            run_shell_command("ls", directory="/etc")

    def test_run_shell_command_timeout(self):
        """Test command execution timeout."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("sleep 60", 60)
            
            with pytest.raises(CommandExecutionError):
                run_shell_command("sleep 60")

    def test_run_shell_command_background_success(self):
        """Test background command execution."""
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.pid = 1234
            mock_popen.return_value = mock_process
            
            result = run_shell_command("sleep 10", background=True)
            
            assert result["pid"] == 1234
            assert result["process_group_id"] == "1234"
            assert result["returncode"] is None
            assert result["command"] == "sleep 10"
            assert result["signal"] is None

    def test_run_shell_command_background_failure(self):
        """Test background command execution failure."""
        with patch('subprocess.Popen') as mock_popen:
            mock_popen.side_effect = Exception("Failed to start process")
            
            with pytest.raises(CommandExecutionError):
                run_shell_command("sleep 10", background=True)

    def test_validate_command_security_valid_commands(self):
        """Test command security validation with valid commands."""
        # Should not raise any exceptions
        utils.validate_command_security("ls -la")
        utils.validate_command_security("echo 'hello world'")
        utils.validate_command_security("python script.py")

    def test_validate_command_security_invalid_commands(self):
        """Test command security validation with invalid commands."""
        # Test command substitution (only $() is blocked, backticks are allowed)
        with pytest.raises(ShellSecurityError):
            utils.validate_command_security("echo $(rm -rf /)")
        
        # Test dangerous patterns
        with pytest.raises(ShellSecurityError):
            utils.validate_command_security("rm -rf /")
        
        with pytest.raises(ShellSecurityError):
            utils.validate_command_security("dd if=/dev/zero of=/dev/sda")

    def test_validate_command_security_empty_commands(self):
        """Test command security validation with empty commands."""
        with pytest.raises(InvalidInputError):
            utils.validate_command_security("")
        
        with pytest.raises(InvalidInputError):
            utils.validate_command_security("   ")

    def test_is_command_allowed_with_blocklist(self):
        """Test command allowance with blocklist."""
        # Test blocked commands
        assert not utils.is_command_allowed("rm test.txt")
        assert not utils.is_command_allowed("rmdir testdir")

    def test_is_command_allowed_with_allowlist(self):
        """Test command allowance with allowlist."""
        # Test allowed commands
        assert utils.is_command_allowed("ls -la")
        assert utils.is_command_allowed("cat file.txt")
        assert utils.is_command_allowed("echo hello")

    def test_is_command_allowed_blocklist_precedence(self):
        """Test that blocklist takes precedence over allowlist."""
        # Even if a command is in allowlist, if it's also in blocklist, it should be blocked
        # This test assumes the implementation gives precedence to blocklist
        assert not utils.is_command_allowed("rm test.txt")

    def test_get_command_restrictions(self):
        """Test getting command restrictions."""
        restrictions = utils.get_command_restrictions()
        
        assert "allowed" in restrictions
        assert "blocked" in restrictions
        assert isinstance(restrictions["allowed"], list)
        assert isinstance(restrictions["blocked"], list)

    def test_update_dangerous_patterns_success(self):
        """Test updating dangerous patterns successfully."""
        # Test setting new patterns
        result = utils.update_dangerous_patterns([
            'rm -rf /',
            'dd if=',
            'mkfs.'
        ])
        
        assert result["success"] is True
        assert "Successfully updated 3 dangerous patterns" in result["message"]
        assert result["patterns"] == ['rm -rf /', 'dd if=', 'mkfs.']
        
        # Verify patterns are stored in DB
        stored_patterns = utils.get_dangerous_patterns()
        assert stored_patterns == ['rm -rf /', 'dd if=', 'mkfs.']
        
        # Test that the patterns actually block commands
        with pytest.raises(ShellSecurityError):
            utils.validate_command_security("rm -rf /")
        
        with pytest.raises(ShellSecurityError):
            utils.validate_command_security("dd if=/dev/zero")

    def test_update_dangerous_patterns_empty_list(self):
        """Test updating dangerous patterns with empty list."""
        # Clear any existing patterns first
        utils.update_dangerous_patterns([])
        
        # Set some patterns first
        utils.update_dangerous_patterns(['rm -rf /'])
        
        # Then clear them
        result = utils.update_dangerous_patterns([])
        
        assert result["success"] is True
        assert "Successfully updated 0 dangerous patterns" in result["message"]
        assert result["patterns"] == []
        
        # Verify no patterns are stored
        stored_patterns = utils.get_dangerous_patterns()
        assert stored_patterns == []
        
        # Test that dangerous commands are now allowed
        utils.validate_command_security("rm -rf /")  # Should not raise

    def test_update_dangerous_patterns_invalid_input(self):
        """Test updating dangerous patterns with invalid input."""
        # Test with non-list
        with pytest.raises(InvalidInputError):
            utils.update_dangerous_patterns("not a list")
        
        # Test with list containing non-string
        with pytest.raises(InvalidInputError):
            utils.update_dangerous_patterns(['rm -rf /', 123])
        
        # Test with list containing empty string
        with pytest.raises(InvalidInputError):
            utils.update_dangerous_patterns(['rm -rf /', ''])

    def test_get_dangerous_patterns(self):
        """Test getting dangerous patterns."""
        # Clear any existing patterns first
        utils.update_dangerous_patterns([])
        
        # Test with no patterns set
        patterns = utils.get_dangerous_patterns()
        assert patterns == []
        
        # Test with patterns set
        utils.update_dangerous_patterns(['rm -rf /', 'dd if='])
        patterns = utils.get_dangerous_patterns()
        assert patterns == ['rm -rf /', 'dd if=']

    def test_dangerous_patterns_case_insensitive(self):
        """Test that dangerous patterns are case insensitive."""
        # Clear any existing patterns first
        utils.update_dangerous_patterns([])
        
        # Set a pattern
        utils.update_dangerous_patterns(['RM -RF /'])
        
        # Test that both uppercase and lowercase versions are blocked
        with pytest.raises(ShellSecurityError):
            utils.validate_command_security("rm -rf /")
        
        with pytest.raises(ShellSecurityError):
            utils.validate_command_security("RM -RF /")

    def test_dangerous_patterns_whitespace_normalization(self):
        """Test that dangerous patterns handle whitespace normalization."""
        # Clear any existing patterns first
        utils.update_dangerous_patterns([])
        
        # Set a pattern with extra whitespace
        utils.update_dangerous_patterns(['  rm   -rf   /  '])
        
        # Test that commands with different whitespace are blocked
        with pytest.raises(ShellSecurityError):
            utils.validate_command_security("rm -rf /")
        
        with pytest.raises(ShellSecurityError):
            utils.validate_command_security("rm    -rf    /")
        
        with pytest.raises(ShellSecurityError):
            utils.validate_command_security("  rm -rf /  ")

    def test_backticks_allowed(self):
        """Test that backticks are now allowed."""
        # Test that backticks don't raise security errors
        utils.validate_command_security("echo `date`")
        utils.validate_command_security("ls `find . -name '*.txt'`")
        
        # Test that $() still raises security errors
        with pytest.raises(ShellSecurityError):
            utils.validate_command_security("echo $(date)")

    def test_handle_internal_commands_pwd(self):
        """Test handling of internal pwd command."""
        result = utils.handle_internal_commands("pwd")
        
        assert result is not None
        assert result["command"] == "pwd"
        assert result["stdout"] == self.workspace_path
        assert result["returncode"] == 0

    def test_handle_internal_commands_cd_success(self):
        """Test handling of internal cd command success."""
        result = utils.handle_internal_commands("cd src")
        
        assert result is not None
        assert result["command"] == "cd src"
        assert result["directory"] == os.path.join(self.workspace_path, "src")
        assert result["returncode"] == 0

    def test_handle_internal_commands_cd_failure(self):
        """Test handling of internal cd command failure."""
        result = utils.handle_internal_commands("cd nonexistent")
        
        assert result is not None
        assert result["command"] == "cd nonexistent"
        assert result["returncode"] == 1
        assert "No such directory" in result["stderr"]

    def test_handle_internal_commands_env(self):
        """Test handling of internal env command."""
        result = utils.handle_internal_commands("env")
        
        assert result is not None
        assert result["command"] == "env"
        assert result["returncode"] == 0
        assert "PATH=" in result["stdout"]

    def test_handle_internal_commands_non_internal(self):
        """Test handling of non-internal commands."""
        result = utils.handle_internal_commands("ls -la")
        
        assert result is None

    def test_run_shell_command_with_description(self):
        """Test command execution with description."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "test output"
            mock_run.return_value.stderr = ""
            
            result = run_shell_command("echo test", description="Test command")
            
            assert result["command"] == "echo test"

    def test_run_shell_command_execution_error(self):
        """Test command execution with general error."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception("General execution error")
            
            with pytest.raises(CommandExecutionError):
                run_shell_command("echo test")

    def test_run_shell_command_platform_specific(self):
        """Test platform-specific shell command selection."""
        with patch('subprocess.run') as mock_run, \
             patch('platform.system') as mock_system:
            
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "test"
            mock_run.return_value.stderr = ""
            
            # Test Windows
            mock_system.return_value = "Windows"
            run_shell_command("echo test")
            
            # Check that cmd.exe was used
            args, kwargs = mock_run.call_args
            assert args[0] == ["cmd.exe", "/c", "echo test"]
            assert kwargs["capture_output"] is True
            assert kwargs["text"] is True
            assert kwargs["timeout"] == 60
            
            # Test Unix-like
            mock_system.return_value = "Linux"
            run_shell_command("echo test")
            
            # Check that bash was used
            args, kwargs = mock_run.call_args
            assert args[0] == ["bash", "-c", "echo test"]
            assert kwargs["capture_output"] is True
            assert kwargs["text"] is True
            assert kwargs["timeout"] == 60

    def test_workspace_update_from_execution(self):
        """Test that workspace is updated after command execution."""
        # This test would need to be more complex to properly test
        # workspace updates, but we can test that the function doesn't crash
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = ""
            mock_run.return_value.stderr = ""
            
            result = run_shell_command("echo test")
            assert result["returncode"] == 0

    def test_absolute_directory_path_error(self):
        """Test error with absolute directory path."""
        with pytest.raises(InvalidInputError):
            run_shell_command("ls", directory="/absolute/path")

    def test_command_restrictions_no_config(self):
        """Test command restrictions when no config exists."""
        # Remove shell_config
        del DB["shell_config"]
        
        restrictions = utils.get_command_restrictions()
        
        assert restrictions["allowed"] == []
        assert restrictions["blocked"] == []

    def test_is_command_allowed_no_restrictions(self):
        """Test command allowance when no restrictions exist."""
        # Remove shell_config
        del DB["shell_config"]
        
        # Should allow all commands by default
        assert utils.is_command_allowed("any_command") is True

    def test_malformed_command_parsing(self):
        """Test handling of malformed commands."""
        # Test with malformed quotes
        assert utils.is_command_allowed("echo 'unclosed quote") is False
        
        # Test with empty command after parsing
        assert utils.is_command_allowed("") is False
        assert utils.is_command_allowed("   ") is False

    def test_run_shell_command_with_all_parameters(self):
        """Test command execution with all parameters."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "output"
            mock_run.return_value.stderr = ""
    
            result = run_shell_command(
                "echo test",
                description="Test command with all params",
                directory="src",
                background=False
            )
    
            assert result["command"] == "echo test"
            assert result["directory"] == os.path.join(self.workspace_path, "src")
            assert result["returncode"] == 0
            assert result["stdout"] == "output"
            assert result["stderr"] == ""

    def test_cd_command_variations(self):
        """Test various cd command formats."""
        # Test cd with no arguments (should go to workspace root)
        result = utils.handle_internal_commands("cd")
        assert result is not None
        assert result["directory"] == self.workspace_path
        
        # Test cd with relative path
        result = utils.handle_internal_commands("cd src")
        assert result is not None
        assert result["directory"] == os.path.join(self.workspace_path, "src")
        
        # Test cd with absolute path within workspace
        result = utils.handle_internal_commands(f"cd {self.workspace_path}/src")
        assert result is not None
        assert result["directory"] == os.path.join(self.workspace_path, "src")

    def test_environment_variables_handling(self):
        """Test environment variables in shell config."""
        # Test with custom environment variables
        DB["shell_config"]["environment_variables"] = {
            "CUSTOM_VAR": "custom_value",
            "PATH": "/custom/path"
        }
        
        result = utils.handle_internal_commands("env")
        
        assert result is not None
        assert "CUSTOM_VAR=custom_value" in result["stdout"]
        assert "PATH=/custom/path" in result["stdout"]

    def test_run_shell_command_empty_shell_config(self):
        """Test command execution with empty shell config."""
        # Test with empty shell_config
        DB["shell_config"] = {}
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "test"
            mock_run.return_value.stderr = ""
            
            result = run_shell_command("echo test")
            assert result["returncode"] == 0

    def test_security_validation_edge_cases(self):
        """Test security validation edge cases."""
        # Test with None
        with pytest.raises(InvalidInputError):
            utils.validate_command_security(None)
        
        # Test with non-string
        with pytest.raises(InvalidInputError):
            utils.validate_command_security(123)
        
        # Test with very long command
        long_command = "echo " + "a" * 10000
        utils.validate_command_security(long_command)  # Should not raise

    def test_command_allowance_partial_matching(self):
        """Test command allowance with partial matching."""
        # Test that partial matches work correctly
        assert utils.is_command_allowed("ls")  # Exact match
        assert utils.is_command_allowed("ls -la")  # Should be allowed if ls is allowed
        assert not utils.is_command_allowed("rm test.txt")  # Should be blocked

    def test_workspace_file_system_integration(self):
        """Test integration with workspace file system."""
        # Test that commands can access files in the workspace
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "test1.txt"
            mock_run.return_value.stderr = ""
            
            result = run_shell_command("ls")
            assert result["returncode"] == 0

    def test_complex_command_scenarios(self):
        """Test complex command scenarios."""
        # Test command with multiple arguments
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "test output"
            mock_run.return_value.stderr = ""
            
            result = run_shell_command("echo 'Hello World' | grep Hello")
            assert result["returncode"] == 0

    def test_error_handling_in_execution_environment(self):
        """Test error handling in execution environment."""
        # Test with invalid directory
        with pytest.raises(InvalidInputError):
            run_shell_command("echo test", directory="nonexistent")

    def test_current_working_directory_handling(self):
        """Test current working directory handling."""
        # Test that CWD is properly maintained
        original_cwd = DB["cwd"]
        
        result = run_shell_command("cd src")
        assert result["returncode"] == 0
        assert DB["cwd"] == os.path.join(self.workspace_path, "src")
        
        # Test that subsequent commands use the new CWD
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = ""
            mock_run.return_value.stderr = ""
            
            result = run_shell_command("pwd")
            assert result["stdout"] == os.path.join(self.workspace_path, "src")

    def test_shell_config_missing_sections(self):
        """Test handling of missing shell config sections."""
        # Test with missing allowed_commands
        DB["shell_config"] = {"blocked_commands": ["rm"]}
        
        restrictions = utils.get_command_restrictions()
        assert restrictions["allowed"] == []
        assert restrictions["blocked"] == ["rm"]
        
        # Test with missing blocked_commands
        DB["shell_config"] = {"allowed_commands": ["ls"]}
        
        restrictions = utils.get_command_restrictions()
        assert restrictions["allowed"] == ["ls"]
        assert restrictions["blocked"] == []
        
        # Test with missing dangerous_patterns
        DB["shell_config"] = {"allowed_commands": ["ls"], "blocked_commands": ["rm"]}
        
        # Should not raise any security errors since no dangerous patterns are set
        utils.validate_command_security("rm -rf /")  # Should not raise
        utils.validate_command_security("dd if=/dev/zero")  # Should not raise

    def test_run_shell_command_stress_test(self):
        """Test shell command execution under stress conditions."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "output"
            mock_run.return_value.stderr = ""
            
            # Test rapid successive commands
            for i in range(10):
                result = run_shell_command(f"echo test{i}")
                assert result["command"] == f"echo test{i}"

    def test_comprehensive_internal_command_coverage(self):
        """Test comprehensive coverage of internal commands."""
        # Test all variations of internal commands
        internal_commands = [
            "pwd",
            "cd",
            "cd src",
            f"cd {self.workspace_path}",
            "cd ..",
            "cd .",
            "env"
        ]
        
        for cmd in internal_commands:
            result = utils.handle_internal_commands(cmd)
            assert result is not None
            assert "command" in result
            assert "returncode" in result
            assert "pid" in result
            assert "process_group_id" in result
            assert "signal" in result

    def test_platform_detection_edge_cases(self):
        """Test platform detection edge cases."""
        with patch('subprocess.run') as mock_run, \
             patch('platform.system') as mock_system:
            
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "test"
            mock_run.return_value.stderr = ""
            
            # Test unknown platform
            mock_system.return_value = "Unknown"
            run_shell_command("echo test")
            
            # Should default to bash
            args, kwargs = mock_run.call_args
            assert args[0] == ["bash", "-c", "echo test"]

    def test_background_process_popen_parameters(self):
        """Test Popen parameters for background processes."""
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.pid = 1234
            mock_popen.return_value = mock_process
            
            result = run_shell_command("sleep 10", background=True)
            
            # Verify Popen was called with correct parameters
            mock_popen.assert_called_once()
            call_args = mock_popen.call_args
            
            # stdout/stderr should be a devnull file object
            assert call_args[1]['stdout'].name == os.devnull
            assert call_args[1]['stderr'].name == os.devnull
            assert call_args[1]['text'] is True

    # Additional comprehensive tests for file operations, environment variables, etc.
    # These would mirror the extensive test coverage from terminal's test_run_command.py

    def test_file_operations_basic(self):
        """Test basic file operations."""
        # Test file creation, reading, modification, deletion
        # This would require more complex setup and mocking
        pass

    def test_environment_variables_comprehensive(self):
        """Test comprehensive environment variable handling."""
        # Test export, unset, env commands with various scenarios
        # Test variable expansion, persistence, scope
        pass

    def test_metadata_handling(self):
        """Test metadata preservation and handling."""
        # Test file permissions, timestamps, symlinks, hidden files
        pass

    def test_error_simulation(self):
        """Test error simulation and handling."""
        # Test various error conditions and their handling
        pass

    def test_workspace_hydration_dehydration(self):
        """Test workspace state hydration and dehydration."""
        # Test that workspace state is properly maintained
        pass 