import unittest
import os
import tempfile
import shutil

from ..cursorAPI import run_terminal_cmd
from ..import DB
from ..SimulationEngine import utils
from ..SimulationEngine.custom_errors import CommandExecutionError

# --- Common Helper Functions ---

def normalize_for_db(path_string):
    if path_string is None:
        return None
    # Remove any drive letter prefix first
    if len(path_string) > 2 and path_string[1:3] in [':/', ':\\']:
        path_string = path_string[2:]
    # Then normalize and convert slashes
    return os.path.normpath(path_string).replace("\\", "/")

def minimal_reset_db_for_terminal_commands(workspace_path_for_db=None):
    """Creates a fresh minimal DB state for testing, clearing and setting up root."""
    if workspace_path_for_db is None:
        workspace_path_for_db = tempfile.mkdtemp(prefix="test_terminal_commands_workspace_")
    
    # Normalize workspace path
    workspace_path_for_db = normalize_for_db(workspace_path_for_db)
    
    # Initialize common directory to match workspace path
    utils.update_common_directory(workspace_path_for_db)
    
    DB.clear()
    DB["workspace_root"] = workspace_path_for_db
    DB["cwd"] = workspace_path_for_db
    DB["file_system"] = {}
    DB["last_edit_params"] = None
    DB["background_processes"] = {}
    DB["_next_pid"] = 1

    # Create root directory entry
    DB["file_system"][workspace_path_for_db] = {
        "path": workspace_path_for_db,
        "is_directory": True,
        "content_lines": [],
        "size_bytes": 0,
        "last_modified": utils.get_current_timestamp_iso()
    }
    
    return workspace_path_for_db

# --- Test Classes ---

class TestCatCommand(unittest.TestCase):
    """Test cases for cat/type command functionality."""

    def _get_command_for_os(self, command_template):
        if os.name == 'nt':
            shell = os.environ.get('SHELL', '').lower()
            if 'bash' in shell or 'zsh' in shell or 'sh' in shell:
                return command_template['unix']
            else:
                return f"cmd /c {command_template['windows']}"
        else:
            return command_template['unix']

    def setUp(self):
        self.workspace_path = minimal_reset_db_for_terminal_commands()
        workspace_path_for_db = DB["workspace_root"]
        test_files = {
            "test1.txt": ["Line 1\n", "Line 2\n", "Line 3\n"],
            "test2.txt": ["Hello World\n", "This is a test\n"],
            "empty.txt": []
        }
        for filename, content in test_files.items():
            file_path = normalize_for_db(os.path.join(workspace_path_for_db, filename))
            
            # Create the file on filesystem
            full_path = os.path.join(self.workspace_path, filename)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.writelines(content)
            
            DB["file_system"][file_path] = {
                "path": file_path,
                "is_directory": False,
                "content_lines": content,
                "size_bytes": utils.calculate_size_bytes(content),
                "last_modified": utils.get_current_timestamp_iso()
            }

    def tearDown(self):
        DB.clear()
        if hasattr(self, 'workspace_path') and os.path.exists(self.workspace_path):
            shutil.rmtree(self.workspace_path, ignore_errors=True)

    def _get_expected_path_key(self, relative_path: str) -> str:
        current_workspace_root = DB["workspace_root"]
        abs_path = os.path.join(current_workspace_root, relative_path)
        normalized_key = os.path.normpath(abs_path).replace("\\", "/")
        return normalized_key

    def test_cat_single_file(self):
        test_file = "test1.txt"
        expected_path = self._get_expected_path_key(test_file)
        command = self._get_command_for_os({
            'unix': f"cat {test_file}",
            'windows': f"type {test_file}"
        })
        result = run_terminal_cmd(command=command, explanation="Read contents of single file")
        self.assertEqual(result['returncode'], 0)
        expected_content = "".join(DB["file_system"][expected_path]["content_lines"])
        self.assertEqual(result['stdout'], expected_content)

    def test_cat_nonexistent_file(self):
        test_file = "nonexistent.txt"
        command = self._get_command_for_os({
            'unix': f"cat {test_file}",
            'windows': f"type {test_file}"
        })
        with self.assertRaises(CommandExecutionError) as cm:
            run_terminal_cmd(command=command, explanation="Attempt to read non-existent file")
        self.assertTrue(len(str(cm.exception)) > 0)


    def test_cat_empty_file(self):
        test_file = "empty.txt"
        # expected_path = self._get_expected_path_key(test_file) # Not needed for stdout check
        command = self._get_command_for_os({
            'unix': f"cat {test_file}",
            'windows': f"type {test_file}"
        })
        result = run_terminal_cmd(command=command, explanation="Read contents of empty file")
        self.assertEqual(result['returncode'], 0)
        self.assertEqual(result['stdout'], "")

    def test_cat_multiple_files(self):
        test_file1 = "test1.txt"
        test_file2 = "test2.txt"
        expected_path1 = self._get_expected_path_key(test_file1)
        expected_path2 = self._get_expected_path_key(test_file2)
        command = self._get_command_for_os({
            'unix': f"cat {test_file1} {test_file2}",
            'windows': f"type {test_file1} {test_file2}"
        })
        result = run_terminal_cmd(command=command, explanation="Read contents of multiple files")
        self.assertEqual(result['returncode'], 0)
        expected_content = "".join(DB["file_system"][expected_path1]["content_lines"]) + \
                         "".join(DB["file_system"][expected_path2]["content_lines"])
        self.assertEqual(result['stdout'], expected_content)


class TestCopyCommand(unittest.TestCase):
    """Test cases for copy/cp command functionality."""

    def _get_command_for_os(self, command_template):
        if os.name == 'nt':
            shell = os.environ.get('SHELL', '').lower()
            if 'bash' in shell or 'zsh' in shell or 'sh' in shell:
                return command_template['unix']
            else:
                return f"cmd /c {command_template['windows']}"
        else:
            return command_template['unix']

    def setUp(self):
        self.workspace_path = minimal_reset_db_for_terminal_commands()
        workspace_path_for_db = DB["workspace_root"]
        
        # Create source file on filesystem
        source_file_path = normalize_for_db(os.path.join(workspace_path_for_db, "source.txt"))
        source_content = ["This is source file content\n", "Line 2\n"]
        
        full_source_path = os.path.join(self.workspace_path, "source.txt")
        with open(full_source_path, 'w', encoding='utf-8') as f:
            f.writelines(source_content)
        
        DB["file_system"][source_file_path] = {
            "path": source_file_path,
            "is_directory": False,
            "content_lines": source_content,
            "size_bytes": utils.calculate_size_bytes(source_content),
            "last_modified": utils.get_current_timestamp_iso()
        }
        
        # Create test directory on filesystem
        dir_path = normalize_for_db(os.path.join(workspace_path_for_db, "test_dir"))
        full_dir_path = os.path.join(self.workspace_path, "test_dir")
        os.makedirs(full_dir_path, exist_ok=True)
        
        DB["file_system"][dir_path] = {
            "path": dir_path,
            "is_directory": True,
            "content_lines": [],
            "size_bytes": 0,
            "last_modified": utils.get_current_timestamp_iso()
        }

    def tearDown(self):
        DB.clear()
        if hasattr(self, 'workspace_path') and os.path.exists(self.workspace_path):
            shutil.rmtree(self.workspace_path, ignore_errors=True)

    def _get_expected_path_key(self, relative_path: str) -> str:
        current_workspace_root = DB["workspace_root"]
        abs_path = os.path.join(current_workspace_root, relative_path)
        normalized_key = os.path.normpath(abs_path).replace("\\", "/")
        return normalized_key

    def test_copy_file(self):
        source_file = "source.txt"
        target_file = "target.txt"
        source_path = self._get_expected_path_key(source_file)
        target_path = self._get_expected_path_key(target_file)
        command = self._get_command_for_os({
            'unix': f"cp {source_file} {target_file}",
            'windows': f"copy {source_file} {target_file}"
        })
        result = run_terminal_cmd(command=command, explanation="Copy file to new location")
        self.assertEqual(result['returncode'], 0)
        self.assertIn(source_path, DB["file_system"])
        self.assertEqual(DB["file_system"][source_path]["content_lines"], ["This is source file content\n", "Line 2\n"])
        self.assertIn(target_path, DB["file_system"])
        self.assertEqual(DB["file_system"][target_path]["content_lines"], ["This is source file content\n", "Line 2\n"])

    def test_copy_to_directory(self):
        source_file = "source.txt"
        target_dir = "test_dir"
        source_path = self._get_expected_path_key(source_file)
        target_path = self._get_expected_path_key(os.path.join(target_dir, source_file))
        command = self._get_command_for_os({
            'unix': f"cp {source_file} {target_dir}",
            'windows': f"copy {source_file} {target_dir}"
        })
        result = run_terminal_cmd(command=command, explanation="Copy file into directory")
        self.assertEqual(result['returncode'], 0)
        self.assertIn(source_path, DB["file_system"])
        self.assertEqual(DB["file_system"][source_path]["content_lines"], ["This is source file content\n", "Line 2\n"])
        self.assertIn(target_path, DB["file_system"])
        self.assertEqual(DB["file_system"][target_path]["content_lines"], ["This is source file content\n", "Line 2\n"])

    def test_copy_nonexistent_file(self):
        source_file = "nonexistent.txt"
        target_file = "target.txt"
        command = self._get_command_for_os({
            'unix': f"cp {source_file} {target_file}",
            'windows': f"copy {source_file} {target_file}"
        })
        with self.assertRaises(CommandExecutionError):
            run_terminal_cmd(command=command, explanation="Attempt to copy non-existent file")

    def test_copy_to_nonexistent_directory(self):
        source_file = "source.txt"
        target_dir_name = "nonexistent_dir" # The directory that shouldn't exist
        
        # For Unix, target a path *inside* the non-existent directory.
        # A trailing slash implies the target is a directory.
        target_path_for_unix_cp = f"{target_dir_name}/"

        # For Windows, the existing test logic implies 'copy source.txt nonexistent_dir'
        # is expected to create a file named 'nonexistent_dir'. We keep this behavior.
        target_path_for_windows_copy = target_dir_name

        command = self._get_command_for_os({
            'unix': f"cp {source_file} {target_path_for_unix_cp}", # e.g., "cp source.txt nonexistent_dir/"
            'windows': f"copy {source_file} {target_path_for_windows_copy}" # e.g., "copy source.txt nonexistent_dir"
        })
        
        shell = os.environ.get('SHELL', '').lower()
        is_unix_shell = 'bash' in shell or 'zsh' in shell or 'sh' in shell
        if is_unix_shell or os.name != 'nt': # check os.name != 'nt' for non-Windows Unix-like
            with self.assertRaises(CommandExecutionError):
                run_terminal_cmd(command=command, explanation="Attempt to copy to non-existent directory")
        else: # Windows cmd
            result = run_terminal_cmd(command=command, explanation="Attempt to copy to non-existent directory")
            self.assertEqual(result['returncode'], 0)
            target_path = self._get_expected_path_key(target_dir_name)
            self.assertIn(target_path, DB["file_system"])
            self.assertFalse(DB["file_system"][target_path]["is_directory"],
                           "Windows copy should create a file, not a directory")
            self.assertEqual(DB["file_system"][target_path]["content_lines"], ["This is source file content\n", "Line 2\n"])


class TestHeadCommand(unittest.TestCase):
    """Test cases for head command functionality."""

    def _get_command_for_os(self, command_template):
        if os.name == 'nt':
            shell = os.environ.get('SHELL', '').lower()
            if 'bash' in shell or 'zsh' in shell or 'sh' in shell:
                return command_template['unix']
            else:
                return f"cmd /c {command_template['windows']}"
        else:
            return command_template['unix']

    def setUp(self):
        self.workspace_path = minimal_reset_db_for_terminal_commands()
        workspace_path_for_db = DB["workspace_root"]
        test_files = {
            "long.txt": [f"Line {i}\n" for i in range(1, 11)],
            "short.txt": ["First line\n", "Second line\n"],
            "empty.txt": []
        }
        for filename, content in test_files.items():
            file_path = normalize_for_db(os.path.join(workspace_path_for_db, filename))
            
            # Create the file on filesystem
            full_path = os.path.join(self.workspace_path, filename)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.writelines(content)
            
            DB["file_system"][file_path] = {
                "path": file_path,
                "is_directory": False,
                "content_lines": content,
                "size_bytes": utils.calculate_size_bytes(content),
                "last_modified": utils.get_current_timestamp_iso()
            }

    def tearDown(self):
        DB.clear()
        if hasattr(self, 'workspace_path') and os.path.exists(self.workspace_path):
            shutil.rmtree(self.workspace_path, ignore_errors=True)

    def _get_expected_path_key(self, relative_path: str) -> str:
        current_workspace_root = DB["workspace_root"]
        abs_path = os.path.join(current_workspace_root, relative_path)
        normalized_key = os.path.normpath(abs_path).replace("\\", "/")
        return normalized_key

    def test_head_default_lines(self):
        test_file = "long.txt"
        file_path = self._get_expected_path_key(test_file)
        command = self._get_command_for_os({
            'unix': f"head {test_file}",
            'windows': f"powershell -Command \"Get-Content {test_file} | Select-Object -First 10\""
        })
        result = run_terminal_cmd(command=command, explanation="Display first 10 lines of file")
        self.assertEqual(result['returncode'], 0)
        expected_content = "".join(DB["file_system"][file_path]["content_lines"])
        self.assertEqual(result['stdout'], expected_content)

    def test_head_specific_lines(self):
        test_file = "long.txt"
        file_path = self._get_expected_path_key(test_file)
        num_lines = 3
        command = self._get_command_for_os({
            'unix': f"head -n {num_lines} {test_file}",
            'windows': f"powershell -Command \"Get-Content {test_file} | Select-Object -First {num_lines}\""
        })
        result = run_terminal_cmd(command=command, explanation=f"Display first {num_lines} lines of file")
        self.assertEqual(result['returncode'], 0)
        expected_content = "".join(DB["file_system"][file_path]["content_lines"][:num_lines])
        self.assertEqual(result['stdout'], expected_content)

    def test_head_short_file(self):
        test_file = "short.txt"
        file_path = self._get_expected_path_key(test_file)
        num_lines = 5
        command = self._get_command_for_os({
            'unix': f"head -n {num_lines} {test_file}",
            'windows': f"powershell -Command \"Get-Content {test_file} | Select-Object -First {num_lines}\""
        })
        result = run_terminal_cmd(command=command, explanation="Display lines from short file")
        self.assertEqual(result['returncode'], 0)
        expected_content = "".join(DB["file_system"][file_path]["content_lines"])
        self.assertEqual(result['stdout'], expected_content)

    def test_head_empty_file(self):
        test_file = "empty.txt"
        command = self._get_command_for_os({
            'unix': f"head {test_file}",
            'windows': f"powershell -Command \"Get-Content {test_file} | Select-Object -First 10\""
        })
        result = run_terminal_cmd(command=command, explanation="Display lines from empty file")
        self.assertEqual(result['returncode'], 0)
        self.assertEqual(result['stdout'], "")

    def test_head_nonexistent_file(self):
        test_file = "nonexistent.txt"
        command = self._get_command_for_os({
            'unix': f"head {test_file}",
            'windows': f"powershell -Command \"Get-Content {test_file} | Select-Object -First 10\""
        })
        with self.assertRaises(CommandExecutionError):
            run_terminal_cmd(command=command, explanation="Attempt to display lines from non-existent file")


class TestMvCommand(unittest.TestCase):
    """Test cases for mv/move command functionality."""

    def _get_command_for_os(self, command_template):
        if os.name == 'nt':
            shell = os.environ.get('SHELL', '').lower()
            if 'bash' in shell or 'zsh' in shell or 'sh' in shell:
                return command_template['unix']
            else:
                return f"cmd /c {command_template['windows']}"
        else:
            return command_template['unix']

    def setUp(self):
        self.workspace_path = minimal_reset_db_for_terminal_commands()
        workspace_path_for_db = DB["workspace_root"]
        
        test_files = {
            "source.txt": ["This is source file content\n", "Line 2\n"],
            "target.txt": ["This is target file content\n"], # For overwrite test
            "empty.txt": []
        }
        for filename, content in test_files.items():
            file_path = normalize_for_db(os.path.join(workspace_path_for_db, filename))
            
            # Create the file on filesystem
            full_path = os.path.join(self.workspace_path, filename)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.writelines(content)
            
            DB["file_system"][file_path] = {
                "path": file_path, "is_directory": False, "content_lines": content,
                "size_bytes": utils.calculate_size_bytes(content),
                "last_modified": utils.get_current_timestamp_iso()
            }

        test_dirs_setup = {
            "source_dir": {"nested.txt": ["Nested file content\n"]},
            "target_dir": {}
        }
        for dirname, contents in test_dirs_setup.items():
            dir_path = normalize_for_db(os.path.join(workspace_path_for_db, dirname))
            
            # Create the directory on filesystem
            full_dir_path = os.path.join(self.workspace_path, dirname)
            os.makedirs(full_dir_path, exist_ok=True)
            
            DB["file_system"][dir_path] = {
                "path": dir_path, "is_directory": True, "content_lines": [], "size_bytes": 0,
                "last_modified": utils.get_current_timestamp_iso()
            }
            for nested_file, nested_content in contents.items():
                nested_path = normalize_for_db(os.path.join(dir_path, nested_file))
                
                # Create the nested file on filesystem
                full_nested_path = os.path.join(full_dir_path, nested_file)
                with open(full_nested_path, 'w', encoding='utf-8') as f:
                    f.writelines(nested_content)
                
                DB["file_system"][nested_path] = {
                    "path": nested_path, "is_directory": False, "content_lines": nested_content,
                    "size_bytes": utils.calculate_size_bytes(nested_content),
                    "last_modified": utils.get_current_timestamp_iso()
                }

    def tearDown(self):
        DB.clear()
        if hasattr(self, 'workspace_path') and os.path.exists(self.workspace_path):
            shutil.rmtree(self.workspace_path, ignore_errors=True)

    def _get_expected_path_key(self, relative_path: str) -> str:
        current_workspace_root = DB["workspace_root"]
        abs_path = os.path.join(current_workspace_root, relative_path)
        normalized_key = os.path.normpath(abs_path).replace("\\", "/")
        return normalized_key

    def test_mv_file(self):
        source_file = "source.txt"
        target_file = "moved.txt"
        source_path = self._get_expected_path_key(source_file)
        target_path = self._get_expected_path_key(target_file)
        command = self._get_command_for_os({
            'unix': f"mv {source_file} {target_file}",
            'windows': f"move {source_file} {target_file}"
        })
        result = run_terminal_cmd(command=command, explanation="Move file to new location")
        self.assertEqual(result['returncode'], 0)
        self.assertNotIn(source_path, DB["file_system"])
        self.assertIn(target_path, DB["file_system"])
        self.assertEqual(DB["file_system"][target_path]["content_lines"], ["This is source file content\n", "Line 2\n"])

    def test_mv_file_to_directory(self):
        source_file = "source.txt"
        target_dir = "target_dir"
        source_path = self._get_expected_path_key(source_file)
        target_path = self._get_expected_path_key(os.path.join(target_dir, source_file))
        command = self._get_command_for_os({
            'unix': f"mv {source_file} {target_dir}",
            'windows': f"move {source_file} {target_dir}"
        })
        result = run_terminal_cmd(command=command, explanation="Move file into directory")
        self.assertEqual(result['returncode'], 0)
        self.assertNotIn(source_path, DB["file_system"])
        self.assertIn(target_path, DB["file_system"])
        self.assertEqual(DB["file_system"][target_path]["content_lines"], ["This is source file content\n", "Line 2\n"])

    def test_mv_directory(self):
        source_dir = "source_dir"
        target_dir = "moved_dir"
        source_path = self._get_expected_path_key(source_dir)
        target_path = self._get_expected_path_key(target_dir)
        nested_source = self._get_expected_path_key(os.path.join(source_dir, "nested.txt"))
        nested_target = self._get_expected_path_key(os.path.join(target_dir, "nested.txt"))
        command = self._get_command_for_os({
            'unix': f"mv {source_dir} {target_dir}",
            'windows': f"move {source_dir} {target_dir}"
        })
        result = run_terminal_cmd(command=command, explanation="Move directory to new location")
        self.assertEqual(result['returncode'], 0)
        self.assertNotIn(source_path, DB["file_system"])
        self.assertNotIn(nested_source, DB["file_system"])
        self.assertIn(target_path, DB["file_system"])
        self.assertTrue(DB["file_system"][target_path]["is_directory"])
        self.assertIn(nested_target, DB["file_system"])
        self.assertEqual(DB["file_system"][nested_target]["content_lines"], ["Nested file content\n"])

    def test_mv_nonexistent_file(self):
        source_file = "nonexistent.txt"
        target_file = "target.txt"
        command = self._get_command_for_os({
            'unix': f"mv {source_file} {target_file}",
            'windows': f"move {source_file} {target_file}"
        })
        with self.assertRaises(CommandExecutionError):
            run_terminal_cmd(command=command, explanation="Attempt to move non-existent file")

    def test_mv_overwrite_file(self):
        source_file = "source.txt"
        target_file = "target.txt" # This file exists with different content
        source_path = self._get_expected_path_key(source_file)
        target_path = self._get_expected_path_key(target_file)
        command = self._get_command_for_os({
            'unix': f"mv {source_file} {target_file}",
            'windows': f"move {source_file} {target_file}" # Windows 'move' overwrites by default if not moving to a dir
        })
        result = run_terminal_cmd(command=command, explanation="Move file to overwrite existing file")
        self.assertEqual(result['returncode'], 0)
        self.assertNotIn(source_path, DB["file_system"])
        self.assertIn(target_path, DB["file_system"])
        self.assertEqual(DB["file_system"][target_path]["content_lines"], ["This is source file content\n", "Line 2\n"])


class TestRedirectionCommand(unittest.TestCase):
    """Test cases for output redirection operators (> and >>) functionality."""

    def _get_command_for_os(self, command_template):
        if os.name == 'nt':
            shell = os.environ.get('SHELL', '').lower()
            if 'bash' in shell or 'zsh' in shell or 'sh' in shell:
                return command_template['unix']
            else:
                return f"cmd /c {command_template['windows']}"
        else:
            return command_template['unix']

    def setUp(self):
        self.workspace_path = minimal_reset_db_for_terminal_commands()
        workspace_path_for_db = DB["workspace_root"]
        test_files = {
            "existing.txt": ["Original content\n"],
            "empty.txt": []
        }
        for filename, content in test_files.items():
            file_path = normalize_for_db(os.path.join(workspace_path_for_db, filename))
            
            # Create the file on filesystem
            full_path = os.path.join(self.workspace_path, filename)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.writelines(content)
            
            DB["file_system"][file_path] = {
                "path": file_path, "is_directory": False, "content_lines": content,
                "size_bytes": utils.calculate_size_bytes(content),
                "last_modified": utils.get_current_timestamp_iso()
            }

    def tearDown(self):
        DB.clear()
        if hasattr(self, 'workspace_path') and os.path.exists(self.workspace_path):
            shutil.rmtree(self.workspace_path, ignore_errors=True)

    def _get_expected_path_key(self, relative_path: str) -> str:
        current_workspace_root = DB["workspace_root"]
        abs_path = os.path.join(current_workspace_root, relative_path)
        normalized_key = os.path.normpath(abs_path).replace("\\", "/")
        return normalized_key

    # def test_overwrite_redirection(self):
    #     test_file = "existing.txt"
    #     file_path = self._get_expected_path_key(test_file)
    #     new_content = "New content"
    #     command = self._get_command_for_os({
    #         'unix': f'echo "{new_content}" > {test_file}',
    #         'windows': f'echo {new_content} > {test_file}'
    #     })
    #     result = run_terminal_cmd(command=command, explanation="Overwrite file content")
    #     self.assertEqual(result['returncode'], 0)
    #     self.assertIn(file_path, DB["file_system"])
    #     # Sim engine for echo on Windows adds a space before newline
    #     expected_line = f"{new_content}\\n" if os.name != 'nt' or 'bash' in os.environ.get('SHELL', '').lower() else f"{new_content} \\n"
    #     self.assertEqual(DB["file_system"][file_path]["content_lines"], [expected_line])


    # def test_append_redirection(self):
    #     test_file = "existing.txt"
    #     file_path = self._get_expected_path_key(test_file)
    #     original_content_lines = DB["file_system"][file_path]["content_lines"][:] # Get a copy
    #     new_content = "Appended content"
    #     command = self._get_command_for_os({
    #         'unix': f'echo "{new_content}" >> {test_file}',
    #         'windows': f'echo {new_content} >> {test_file}'
    #     })
    #     result = run_terminal_cmd(command=command, explanation="Append to file")
    #     self.assertEqual(result['returncode'], 0)
    #     self.assertIn(file_path, DB["file_system"])
    #     # Sim engine for echo on Windows adds a space before newline
    #     appended_line = f"{new_content}\\n" if os.name != 'nt' or 'bash' in os.environ.get('SHELL', '').lower() else f"{new_content} \\n"
    #     expected_final_content = original_content_lines + [appended_line]
    #     self.assertEqual(DB["file_system"][file_path]["content_lines"], expected_final_content)

    # def test_create_new_file(self):
    #     test_file = "new.txt"
    #     file_path = self._get_expected_path_key(test_file)
    #     content = "New file content"
    #     command = self._get_command_for_os({
    #         'unix': f'echo "{content}" > {test_file}',
    #         'windows': f'echo {content} > {test_file}'
    #     })
    #     result = run_terminal_cmd(command=command, explanation="Create new file")
    #     self.assertEqual(result['returncode'], 0)
    #     self.assertIn(file_path, DB["file_system"])
    #     expected_line = f"{content}\\n" if os.name != 'nt' or 'bash' in os.environ.get('SHELL', '').lower() else f"{content} \\n"
    #     self.assertEqual(DB["file_system"][file_path]["content_lines"], [expected_line])

    # def test_append_to_empty_file(self):
    #     test_file = "empty.txt"
    #     file_path = self._get_expected_path_key(test_file)
    #     content = "First content"
    #     command = self._get_command_for_os({
    #         'unix': f'echo "{content}" >> {test_file}',
    #         'windows': f'echo {content} >> {test_file}'
    #     })
    #     result = run_terminal_cmd(command=command, explanation="Append to empty file")
    #     self.assertEqual(result['returncode'], 0)
    #     self.assertIn(file_path, DB["file_system"])
    #     expected_line = f"{content}\\n" if os.name != 'nt' or 'bash' in os.environ.get('SHELL', '').lower() else f"{content} \\n"
    #     self.assertEqual(DB["file_system"][file_path]["content_lines"], [expected_line])

    def test_multiple_redirects(self):
        test_file = "multi_redirect.txt" # Use a new file to avoid state issues
        file_path = self._get_expected_path_key(test_file)
        content1 = "First line"
        content2 = "Second line"
        
        # Adjusted for how the simulation engine handles echo and redirection chains
        is_cmd_shell = os.name == 'nt' and not ('bash' in os.environ.get('SHELL', '').lower() or 'zsh' in os.environ.get('SHELL', '').lower() or 'sh' in os.environ.get('SHELL', '').lower())

        if is_cmd_shell:
            command = f'cmd /c "(echo {content1} > {test_file}) && (echo {content2} >> {test_file})"'
            # Sim engine's cmd echo adds space, and consecutive echos might have different spacing.
            # First echo > file results in "content1 \n"
            # Second echo >> file results in "content2 \n" (appended)
            expected_db_content = [f"{content1} \n", f"{content2} \n"]
        else: # Unix or Unix-like shell
            command = f'sh -c \'echo "{content1}" > {test_file} && echo "{content2}" >> {test_file}\''
            expected_db_content = [f"{content1}\n", f"{content2}\n"]

        result = run_terminal_cmd(command=command, explanation="Multiple redirects")
        self.assertEqual(result['returncode'], 0)
        self.assertIn(file_path, DB["file_system"])
        self.assertEqual(DB["file_system"][file_path]["content_lines"], expected_db_content)


class TestRmCommand(unittest.TestCase):
    """Test cases for rm/del command functionality."""

    @staticmethod
    def _setup_rm_specific_fs(workspace_path_for_db, workspace_path_real):
        # Create test files
        test_files_to_add = {
            "file1.txt": ["Content of file 1\n"],
            "file2.txt": ["Content of file 2\n"],
            "empty.txt": []
        }
        for filename, content in test_files_to_add.items():
            file_path = normalize_for_db(os.path.join(workspace_path_for_db, filename))
            
            # Create the file on filesystem
            full_path = os.path.join(workspace_path_real, filename)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.writelines(content)
            
            DB["file_system"][file_path] = {
                "path": file_path, "is_directory": False, "content_lines": content,
                "size_bytes": utils.calculate_size_bytes(content),
                "last_modified": utils.get_current_timestamp_iso()
            }

        # Create test directories with nested content
        test_dirs_data = {
            "dir1": {
                "nested1.txt": ["Nested file 1 content\n"],
                "subdir": {"deep.txt": ["Deep nested content\n"]}
            },
            "empty_dir": {}
        }

        # Helper to add directory contents (adapted from original test_rm_command.py)
        def add_dir_contents_recursive(current_dir_abs_path, current_dir_real_path, contents_dict):
            # Ensure current_dir_abs_path itself is in DB as a directory
            if current_dir_abs_path not in DB["file_system"]:
                 DB["file_system"][current_dir_abs_path] = {
                    "path": current_dir_abs_path, "is_directory": True, "content_lines": [], "size_bytes": 0,
                    "last_modified": utils.get_current_timestamp_iso()
                }
            elif not DB["file_system"][current_dir_abs_path]["is_directory"]:
                raise Exception(f"Path conflict: {current_dir_abs_path} expected to be a dir for adding contents.")

            # Create the directory on filesystem
            os.makedirs(current_dir_real_path, exist_ok=True)

            for name, item_content in contents_dict.items():
                item_abs_path = normalize_for_db(os.path.join(current_dir_abs_path, name))
                item_real_path = os.path.join(current_dir_real_path, name)
                
                if isinstance(item_content, dict):  # It's a subdirectory
                    DB["file_system"][item_abs_path] = {
                        "path": item_abs_path, "is_directory": True, "content_lines": [], "size_bytes": 0,
                        "last_modified": utils.get_current_timestamp_iso()
                    }
                    add_dir_contents_recursive(item_abs_path, item_real_path, item_content) # Recursive call
                else:  # It's a file
                    with open(item_real_path, 'w', encoding='utf-8') as f:
                        f.writelines(item_content)
                    
                    DB["file_system"][item_abs_path] = {
                        "path": item_abs_path, "is_directory": False, "content_lines": item_content,
                        "size_bytes": utils.calculate_size_bytes(item_content),
                        "last_modified": utils.get_current_timestamp_iso()
                    }
        
        for dirname, contents in test_dirs_data.items():
            dir_abs_path = normalize_for_db(os.path.join(workspace_path_for_db, dirname))
            dir_real_path = os.path.join(workspace_path_real, dirname)
            
            # Ensure the top-level directory entry is created first
            DB["file_system"][dir_abs_path] = {
                "path": dir_abs_path, "is_directory": True, "content_lines": [], "size_bytes": 0,
                "last_modified": utils.get_current_timestamp_iso()
            }
            add_dir_contents_recursive(dir_abs_path, dir_real_path, contents)

    def _get_command_for_os(self, command_template):
        if os.name == 'nt':
            shell = os.environ.get('SHELL', '').lower()
            if 'bash' in shell or 'zsh' in shell or 'sh' in shell:
                return command_template['unix']
            else:
                return f"cmd /c {command_template['windows']}"
        else:
            return command_template['unix']

    def setUp(self):
        self.workspace_path = minimal_reset_db_for_terminal_commands()
        TestRmCommand._setup_rm_specific_fs(DB["workspace_root"], self.workspace_path)

    def tearDown(self):
        DB.clear()
        if hasattr(self, 'workspace_path') and os.path.exists(self.workspace_path):
            shutil.rmtree(self.workspace_path, ignore_errors=True)

    def _get_expected_path_key(self, relative_path: str) -> str:
        current_workspace_root = DB["workspace_root"]
        abs_path = os.path.join(current_workspace_root, relative_path)
        normalized_key = os.path.normpath(abs_path).replace("\\", "/")
        return normalized_key

    def test_rm_file(self):
        test_file = "file1.txt"
        file_path = self._get_expected_path_key(test_file)
        command = self._get_command_for_os({
            'unix': f"rm {test_file}", 'windows': f"del {test_file}"
        })
        result = run_terminal_cmd(command=command, explanation="Remove single file")
        self.assertEqual(result['returncode'], 0)
        self.assertNotIn(file_path, DB["file_system"])

    def test_rm_multiple_files(self):
        test_files = ["file1.txt", "file2.txt"]
        file_paths = [self._get_expected_path_key(f) for f in test_files]
        command = self._get_command_for_os({
            'unix': f"rm {' '.join(test_files)}",
            'windows': f"del {' '.join(test_files)}"
        })
        result = run_terminal_cmd(command=command, explanation="Remove multiple files")
        self.assertEqual(result['returncode'], 0)
        for path in file_paths:
            self.assertNotIn(path, DB["file_system"])

    def test_rm_nonexistent_file(self):
        test_file = "nonexistent.txt"
        command = self._get_command_for_os({
            'unix': f"rm {test_file}", 'windows': f"del {test_file}"
        })
        shell = os.environ.get('SHELL', '').lower()
        is_unix_shell = 'bash' in shell or 'zsh' in shell or 'sh' in shell
        if is_unix_shell or os.name != 'nt':
            with self.assertRaises(CommandExecutionError):
                run_terminal_cmd(command=command, explanation="Attempt to remove non-existent file")
        else: # Windows cmd
            result = run_terminal_cmd(command=command, explanation="Attempt to remove non-existent file")
            self.assertEqual(result['returncode'], 0)

    def test_rm_directory(self): # Test removing an EMPTY directory
        test_dir = "empty_dir"
        dir_path = self._get_expected_path_key(test_dir)
        command = self._get_command_for_os({
            'unix': f"rmdir {test_dir}", 'windows': f"rd {test_dir}"
        })
        result = run_terminal_cmd(command=command, explanation="Remove empty directory")
        self.assertEqual(result['returncode'], 0)
        self.assertNotIn(dir_path, DB["file_system"])

    def test_rm_recursive_directory(self):
        test_dir = "dir1"
        dir_path = self._get_expected_path_key(test_dir)
        nested_file = self._get_expected_path_key(os.path.join(test_dir, "nested1.txt"))
        deep_file = self._get_expected_path_key(os.path.join(test_dir, "subdir", "deep.txt"))
        subdir_path = self._get_expected_path_key(os.path.join(test_dir, "subdir"))

        command = self._get_command_for_os({
            'unix': f"rm -r {test_dir}", 'windows': f"rd /s /q {test_dir}"
        })
        result = run_terminal_cmd(command=command, explanation="Remove directory recursively")
        # For Windows `rd /s /q`, return code is 0 even if it does nothing (e.g. dir doesn't exist)
        # For Unix `rm -r`, it's also 0 if dir doesn't exist (with -f implied by sim sometimes, or no error by default for non-exist)
        self.assertEqual(result['returncode'], 0)
        self.assertNotIn(dir_path, DB["file_system"])
        self.assertNotIn(nested_file, DB["file_system"])
        self.assertNotIn(subdir_path, DB["file_system"])
        self.assertNotIn(deep_file, DB["file_system"])


    def test_rm_nonempty_directory_without_recursive(self):
        test_dir = "dir1" # This directory is non-empty
        command = self._get_command_for_os({
            'unix': f"rmdir {test_dir}", 'windows': f"rd {test_dir}"
        })
        with self.assertRaises(CommandExecutionError):
            run_terminal_cmd(command=command, explanation="Attempt to remove non-empty directory without recursive flag")


class TestTailCommand(unittest.TestCase):
    """Test cases for tail command functionality."""

    def _get_command_for_os(self, command_template):
        if os.name == 'nt':
            shell = os.environ.get('SHELL', '').lower()
            if 'bash' in shell or 'zsh' in shell or 'sh' in shell:
                return command_template['unix']
            else:
                return f"cmd /c {command_template['windows']}"
        else:
            return command_template['unix']

    def setUp(self):
        self.workspace_path = minimal_reset_db_for_terminal_commands()
        workspace_path_for_db = DB["workspace_root"]
        test_files = {
            "long.txt": [f"Line {i}\n" for i in range(1, 11)],
            "short.txt": ["First line\n", "Second line\n"],
            "empty.txt": []
        }
        for filename, content in test_files.items():
            file_path = normalize_for_db(os.path.join(workspace_path_for_db, filename))
            
            # Create the file on filesystem
            full_path = os.path.join(self.workspace_path, filename)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.writelines(content)
            
            DB["file_system"][file_path] = {
                "path": file_path, "is_directory": False, "content_lines": content,
                "size_bytes": utils.calculate_size_bytes(content),
                "last_modified": utils.get_current_timestamp_iso()
            }

    def tearDown(self):
        DB.clear()
        if hasattr(self, 'workspace_path') and os.path.exists(self.workspace_path):
            shutil.rmtree(self.workspace_path, ignore_errors=True)

    def _get_expected_path_key(self, relative_path: str) -> str:
        current_workspace_root = DB["workspace_root"]
        abs_path = os.path.join(current_workspace_root, relative_path)
        normalized_key = os.path.normpath(abs_path).replace("\\", "/")
        return normalized_key

    def test_tail_default_lines(self):
        test_file = "long.txt"
        file_path = self._get_expected_path_key(test_file)
        command = self._get_command_for_os({
            'unix': f"tail {test_file}",
            'windows': f"powershell -Command \"Get-Content {test_file} | Select-Object -Last 10\""
        })
        result = run_terminal_cmd(command=command, explanation="Display last 10 lines of file")
        self.assertEqual(result['returncode'], 0)
        # Default tail for a 10 line file is all 10 lines
        expected_content = "".join(DB["file_system"][file_path]["content_lines"])
        self.assertEqual(result['stdout'], expected_content)

    def test_tail_specific_lines(self):
        test_file = "long.txt"
        file_path = self._get_expected_path_key(test_file)
        num_lines = 3
        command = self._get_command_for_os({
            'unix': f"tail -n {num_lines} {test_file}",
            'windows': f"powershell -Command \"Get-Content {test_file} | Select-Object -Last {num_lines}\""
        })
        result = run_terminal_cmd(command=command, explanation=f"Display last {num_lines} lines of file")
        self.assertEqual(result['returncode'], 0)
        expected_content = "".join(DB["file_system"][file_path]["content_lines"][-num_lines:])
        self.assertEqual(result['stdout'], expected_content)

    def test_tail_short_file(self):
        test_file = "short.txt" # Has 2 lines
        file_path = self._get_expected_path_key(test_file)
        num_lines = 5 # Request more lines than available
        command = self._get_command_for_os({
            'unix': f"tail -n {num_lines} {test_file}",
            'windows': f"powershell -Command \"Get-Content {test_file} | Select-Object -Last {num_lines}\""
        })
        result = run_terminal_cmd(command=command, explanation="Display lines from short file")
        self.assertEqual(result['returncode'], 0)
        expected_content = "".join(DB["file_system"][file_path]["content_lines"]) # Should return all lines
        self.assertEqual(result['stdout'], expected_content)

    def test_tail_empty_file(self):
        test_file = "empty.txt"
        command = self._get_command_for_os({
            'unix': f"tail {test_file}",
            'windows': f"powershell -Command \"Get-Content {test_file} | Select-Object -Last 10\""
        })
        result = run_terminal_cmd(command=command, explanation="Display lines from empty file")
        self.assertEqual(result['returncode'], 0)
        self.assertEqual(result['stdout'], "")

    def test_tail_nonexistent_file(self):
        test_file = "nonexistent.txt"
        command = self._get_command_for_os({
            'unix': f"tail {test_file}",
            'windows': f"powershell -Command \"Get-Content {test_file} | Select-Object -Last 10\""
        })
        with self.assertRaises(CommandExecutionError):
            run_terminal_cmd(command=command, explanation="Attempt to display lines from non-existent file")


class TestTouchCommand(unittest.TestCase):
    """Test cases for touch command functionality."""

    def _get_command_for_os(self, command_template):
        if os.name == 'nt':
            shell = os.environ.get('SHELL', '').lower()
            if 'bash' in shell or 'zsh' in shell or 'sh' in shell:
                return command_template['unix']
            else:
                return f"cmd /c {command_template['windows']}"
        else:
            return command_template['unix']

    def setUp(self):
        self.workspace_path = minimal_reset_db_for_terminal_commands()
        workspace_path_for_db = DB["workspace_root"]
        test_files = {
            "existing.txt": ["Some content\n"],
            "empty.txt": [] # This will be touched (if it exists) or created
        }
        for filename, content in test_files.items():
            file_path = normalize_for_db(os.path.join(workspace_path_for_db, filename))
            
            # Create the file on filesystem
            full_path = os.path.join(self.workspace_path, filename)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.writelines(content)
            
            DB["file_system"][file_path] = {
                "path": file_path, "is_directory": False, "content_lines": content,
                "size_bytes": utils.calculate_size_bytes(content),
                "last_modified": utils.get_current_timestamp_iso()
            }

    def tearDown(self):
        DB.clear()
        if hasattr(self, 'workspace_path') and os.path.exists(self.workspace_path):
            shutil.rmtree(self.workspace_path, ignore_errors=True)

    def _get_expected_path_key(self, relative_path: str) -> str:
        current_workspace_root = DB["workspace_root"]
        abs_path = os.path.join(current_workspace_root, relative_path)
        normalized_key = os.path.normpath(abs_path).replace("\\", "/")
        return normalized_key

    def test_touch_new_file(self):
        test_file = "newly_touched.txt"
        file_path = self._get_expected_path_key(test_file)
        command = self._get_command_for_os({
            'unix': f"touch {test_file}",
            'windows': f"type nul > {test_file}" # Common way to touch/create empty file
        })
        result = run_terminal_cmd(command=command, explanation="Create new empty file with touch")
        self.assertEqual(result['returncode'], 0)
        self.assertIn(file_path, DB["file_system"])
        self.assertFalse(DB["file_system"][file_path]["is_directory"])
        # Touch creates an empty file if it doesn't exist
        self.assertEqual(DB["file_system"][file_path]["content_lines"], [])
        self.assertEqual(DB["file_system"][file_path]["size_bytes"], 0)

    def test_touch_existing_file(self):
        test_file = "existing.txt"
        file_path = self._get_expected_path_key(test_file)
        original_content = DB["file_system"][file_path]["content_lines"][:]
        original_timestamp = DB["file_system"][file_path]["last_modified"]
        
        # Allow a moment for timestamp to differ
        import time
        time.sleep(0.01)

        # Windows "type nul > existing.txt" would truncate.
        # Unix "touch existing.txt" updates timestamp without changing content.
        # The simulation should ideally mimic the core 'touch' behavior (update timestamp, create if not exists)
        # Let's use the unix version primarily for testing the 'touch' idea.
        # If on windows, `fsutil file createnew existing.txt 0` would be closer, but `type nul` is for creation by `touch`.
        # The simulation of `touch existing.txt` should update timestamp.
        # The simulation of `type nul > existing.txt` (Windows touch equivalent if file exists) *will* truncate.
        # We should test the intended behavior based on the command.
        
        is_unix_like_touch = True
        if os.name == 'nt':
            shell = os.environ.get('SHELL', '').lower()
            if not ('bash' in shell or 'zsh' in shell or 'sh' in shell):
                is_unix_like_touch = False # cmd.exe 'type nul >' behavior

        if is_unix_like_touch:
            command = f"touch {test_file}"
        else: # cmd.exe behavior for "type nul > existing.txt"
            command = f"cmd /c type nul > {test_file}"


        result = run_terminal_cmd(command=command, explanation="Update timestamp of existing file")
        self.assertEqual(result['returncode'], 0)
        self.assertIn(file_path, DB["file_system"])

        if is_unix_like_touch: # Unix touch should preserve content
            self.assertEqual(DB["file_system"][file_path]["content_lines"], original_content)
            self.assertNotEqual(DB["file_system"][file_path]["last_modified"], original_timestamp, "Timestamp should update")
        else: # Windows 'type nul >' truncates
            self.assertEqual(DB["file_system"][file_path]["content_lines"], [])
            self.assertEqual(DB["file_system"][file_path]["size_bytes"], 0)
            # Timestamp also updates
            self.assertNotEqual(DB["file_system"][file_path]["last_modified"], original_timestamp, "Timestamp should update")


    def test_touch_multiple_files(self):
        test_files_to_touch = ["multi1.txt", "multi2.txt"]
        file_paths_expected = [self._get_expected_path_key(f) for f in test_files_to_touch]
        
        command_str_parts = []
        is_cmd_shell = os.name == 'nt' and not ('bash' in os.environ.get('SHELL', '').lower() or 'zsh' in os.environ.get('SHELL', '').lower() or 'sh' in os.environ.get('SHELL', '').lower())

        if is_cmd_shell:
            # cmd.exe doesn't directly support `touch file1 file2`
            # We simulate by chaining `type nul > file` commands
            command = "cmd /c " + " && ".join([f"type nul > {f}" for f in test_files_to_touch])
        else: # Unix or unix-like shell
            command = f"touch {' '.join(test_files_to_touch)}"

        result = run_terminal_cmd(command=command, explanation="Create multiple new files with touch")
        self.assertEqual(result['returncode'], 0)
        for path in file_paths_expected:
            self.assertIn(path, DB["file_system"])
            self.assertFalse(DB["file_system"][path]["is_directory"])
            self.assertEqual(DB["file_system"][path]["content_lines"], [])
            self.assertEqual(DB["file_system"][path]["size_bytes"], 0)

    def test_touch_in_nonexistent_directory(self):
        test_file = "nonexistent_dir/new.txt"
        command = self._get_command_for_os({
            'unix': f"touch {test_file}",
            'windows': f"type nul > {test_file}"
        })
        # This behavior depends on the OS. `touch` on Unix fails. `type nul >` on Windows might also fail depending on shell.
        # The simulation should make it fail as the parent directory doesn't exist.
        with self.assertRaises(CommandExecutionError):
            run_terminal_cmd(command=command, explanation="Attempt to create file in non-existent directory")

    def test_is_background_not_bool(self):
        command = "echo test"
        with self.assertRaises(ValueError) as cm:
            run_terminal_cmd(command=command, explanation="Test non-bool is_background", is_background="not_bool")
        self.assertIn("is_background must be a boolean", str(cm.exception))

# --- Main Execution ---

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)