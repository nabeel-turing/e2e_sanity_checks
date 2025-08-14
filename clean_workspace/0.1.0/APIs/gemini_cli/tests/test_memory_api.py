#!/usr/bin/env python3
"""Test cases for the memory API module.

This module tests the memory functionality including save_memory, get_memories,
update_memory_by_content, and clear_memories functions.
"""

import pytest
import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ensure package root is importable when tests run via py.test
sys.path.append(str(Path(__file__).resolve().parents[2]))

# Import the memory API functions
from gemini_cli.memory import save_memory  # noqa: E402
from gemini_cli.SimulationEngine.utils import get_memories, clear_memories, update_memory_by_content  # noqa: E402
from gemini_cli.SimulationEngine.db import DB  # noqa: E402
from gemini_cli.SimulationEngine.custom_errors import InvalidInputError, WorkspaceNotAvailableError  # noqa: E402


class TestMemoryAPI:
    """Test cases for memory API functions."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Clear the DB before each test
        DB.clear()
        
        # Set up a temporary workspace
        self.temp_workspace = tempfile.mkdtemp(prefix="test_memory_")
        DB["workspace_root"] = self.temp_workspace
        DB["cwd"] = self.temp_workspace
        DB["file_system"] = {}
        DB["memory_storage"] = {}
        
    def teardown_method(self):
        """Clean up after each test method."""
        # Clean up temporary workspace
        if hasattr(self, 'temp_workspace') and os.path.exists(self.temp_workspace):
            shutil.rmtree(self.temp_workspace, ignore_errors=True)
        
        # Clear the DB
        DB.clear()

    def test_save_memory_success(self):
        """Test successfully saving a memory."""
        fact = "User prefers Python over JavaScript"
        
        result = save_memory(fact)
        
        assert result["success"] is True
        assert "remembered" in result["message"].lower()
        assert fact in result["message"]
        
        # Verify memory is stored in memory_storage (not file_system)
        assert "memory_storage" in DB
        memory_storage = DB["memory_storage"]
        
        # Check that a memory file entry was created
        memory_files = [path for path in memory_storage.keys() if path.endswith("GEMINI.md")]
        assert len(memory_files) > 0
        
        # Check the content contains our memory
        memory_file_path = memory_files[0]
        content_lines = memory_storage[memory_file_path]["content_lines"]
        content = "".join(content_lines)
        assert "## Gemini Added Memories" in content
        assert f"- {fact}" in content

    def test_save_memory_multiple_facts(self):
        """Test saving multiple memories."""
        facts = [
            "User likes dark mode",
            "User works on machine learning projects",
            "User's favorite editor is VS Code"
        ]
        
        for fact in facts:
            result = save_memory(fact)
            assert result["success"] is True
        
        # Verify all memories are stored
        memory_storage = DB["memory_storage"]
        memory_files = [path for path in memory_storage.keys() if path.endswith("GEMINI.md")]
        assert len(memory_files) > 0
        
        memory_file_path = memory_files[0]
        content_lines = memory_storage[memory_file_path]["content_lines"]
        content = "".join(content_lines)
        
        for fact in facts:
            assert f"- {fact}" in content

    def test_save_memory_empty_fact(self):
        """Test saving memory with empty fact raises InvalidInputError."""
        with pytest.raises(InvalidInputError, match="must be a non-empty string"):
            save_memory("")
        
        with pytest.raises(InvalidInputError, match="must be a non-empty string"):
            save_memory("   ")

    def test_save_memory_non_string_fact(self):
        """Test saving memory with non-string fact raises InvalidInputError."""
        with pytest.raises(InvalidInputError, match="must be a string"):
            save_memory(123)
        
        with pytest.raises(InvalidInputError, match="must be a string"):
            save_memory(None)
        
        with pytest.raises(InvalidInputError, match="must be a string"):
            save_memory(["fact"])

    def test_save_memory_no_workspace(self):
        """Test saving memory without workspace_root raises WorkspaceNotAvailableError."""
        del DB["workspace_root"]
        
        with pytest.raises(WorkspaceNotAvailableError, match="workspace_root not configured"):
            save_memory("Some fact")

    def test_save_memory_with_special_characters(self):
        """Test saving memory with special characters."""
        fact = "User's password contains @#$%^&*() symbols"
        
        result = save_memory(fact)
        assert result["success"] is True
        
        # Verify content is properly escaped/stored
        memory_storage = DB["memory_storage"]
        memory_files = [path for path in memory_storage.keys() if path.endswith("GEMINI.md")]
        memory_file_path = memory_files[0]
        content_lines = memory_storage[memory_file_path]["content_lines"]
        content = "".join(content_lines)
        assert f"- {fact}" in content

    def test_save_memory_with_leading_hyphen(self):
        """Test saving memory that already has leading hyphen is handled correctly."""
        fact = "- User has a habit of writing todos"
        expected_fact = "User has a habit of writing todos"  # Should strip leading hyphen
        
        result = save_memory(fact)
        assert result["success"] is True
        
        # Verify the hyphen was stripped and re-added properly
        memory_storage = DB["memory_storage"]
        memory_files = [path for path in memory_storage.keys() if path.endswith("GEMINI.md")]
        memory_file_path = memory_files[0]
        content_lines = memory_storage[memory_file_path]["content_lines"]
        content = "".join(content_lines)
        assert f"- {expected_fact}" in content
        assert "- - " not in content  # Should not have double hyphens

    @patch('gemini_cli.memory._persist_db_state')
    def test_save_memory_persistence_failure(self, mock_persist):
        """Test save_memory handles persistence failure gracefully."""
        mock_persist.side_effect = Exception("Database persistence failed")
        
        result = save_memory("Test fact")
        
        assert result["success"] is False
        assert "Failed to save memory" in result["message"]

    def test_get_memories_no_workspace(self):
        """Test get_memories without workspace_root raises WorkspaceNotAvailableError."""
        del DB["workspace_root"]
        
        with pytest.raises(WorkspaceNotAvailableError, match="workspace_root not configured"):
            get_memories()

    def test_get_memories_no_memory_file(self):
        """Test get_memories when no memory file exists."""
        result = get_memories()
        
        assert result["success"] is True
        assert result["memories"] == []
        assert "Memory file does not exist" in result["message"]

    def test_get_memories_invalid_limit(self):
        """Test get_memories with invalid limit raises InvalidInputError."""
        with pytest.raises(InvalidInputError, match="must be a positive integer"):
            get_memories(limit=0)
        
        with pytest.raises(InvalidInputError, match="must be a positive integer"):
            get_memories(limit=-1)
        
        with pytest.raises(InvalidInputError, match="must be a positive integer"):
            get_memories(limit="5")

    def test_clear_memories_no_workspace(self):
        """Test clear_memories without workspace_root raises WorkspaceNotAvailableError."""
        del DB["workspace_root"]
        
        with pytest.raises(WorkspaceNotAvailableError, match="workspace_root not configured"):
            clear_memories()

    def test_clear_memories_no_memory_file(self):
        """Test clear_memories when no memory file exists."""
        result = clear_memories()
        
        assert result["success"] is True
        assert "No memories to clear" in result["message"]

    def test_update_memory_by_content_no_workspace(self):
        """Test update_memory_by_content without workspace_root raises WorkspaceNotAvailableError."""
        del DB["workspace_root"]
        
        with pytest.raises(WorkspaceNotAvailableError, match="workspace_root not configured"):
            update_memory_by_content("old", "new")

    def test_update_memory_by_content_invalid_input(self):
        """Test update_memory_by_content with invalid input raises InvalidInputError."""
        with pytest.raises(InvalidInputError, match="must be a non-empty string"):
            update_memory_by_content("", "new fact")
        
        with pytest.raises(InvalidInputError, match="must be a non-empty string"):
            update_memory_by_content("old fact", "")
        
        with pytest.raises(InvalidInputError, match="must be a non-empty string"):
            update_memory_by_content(123, "new fact")

    def test_update_memory_by_content_no_memory_file(self):
        """Test update_memory_by_content when no memory file exists."""
        result = update_memory_by_content("old fact", "new fact")
        
        assert result["success"] is False
        assert "Memory file does not exist" in result["message"]

    def test_memory_file_path_generation(self):
        """Test that memory file paths are generated correctly."""
        fact = "Test fact for path generation"
        
        result = save_memory(fact)
        assert result["success"] is True
        
        # Check that the memory file path follows expected pattern
        memory_storage = DB["memory_storage"]
        memory_files = [path for path in memory_storage.keys() if path.endswith("GEMINI.md")]
        assert len(memory_files) > 0
        
        memory_file_path = memory_files[0]
        assert ".gemini" in memory_file_path
        assert "GEMINI.md" in memory_file_path

    def test_memory_directory_creation(self):
        """Test that memory directory is created in memory_storage."""
        fact = "Test fact for directory creation"
        
        result = save_memory(fact)
        assert result["success"] is True
        
        # Check that directory entry was created
        memory_storage = DB["memory_storage"]
        directory_entries = [path for path, entry in memory_storage.items() 
                           if entry.get("is_directory", False)]
        assert len(directory_entries) > 0
        
        # Check that .gemini directory exists
        gemini_dirs = [path for path in directory_entries if ".gemini" in path]
        assert len(gemini_dirs) > 0

    def test_memory_content_format(self):
        """Test that memory content is formatted correctly."""
        fact = "Test fact for content format"
        
        result = save_memory(fact)
        assert result["success"] is True
        
        # Get the memory content
        memory_storage = DB["memory_storage"]
        memory_files = [path for path in memory_storage.keys() if path.endswith("GEMINI.md")]
        memory_file_path = memory_files[0]
        content_lines = memory_storage[memory_file_path]["content_lines"]
        content = "".join(content_lines)
        
        # Verify format
        assert "## Gemini Added Memories" in content
        assert f"- {fact}" in content
        assert content.endswith('\n')

    def test_memory_size_calculation(self):
        """Test that memory file size is calculated correctly."""
        fact = "Test fact for size calculation"
        
        result = save_memory(fact)
        assert result["success"] is True
        
        # Check size calculation
        memory_storage = DB["memory_storage"]
        memory_files = [path for path in memory_storage.keys() if path.endswith("GEMINI.md")]
        memory_file_path = memory_files[0]
        entry = memory_storage[memory_file_path]
        
        content = "".join(entry["content_lines"])
        expected_size = len(content.encode('utf-8'))
        assert entry["size_bytes"] == expected_size

    @patch('gemini_cli.memory._get_global_memory_file_path')
    def test_save_memory_path_security_check(self, mock_get_path):
        """Test that memory save respects workspace security boundaries."""
        # Simulate path outside workspace
        mock_get_path.return_value = "/tmp/outside_workspace/memory.md"
        
        fact = "Test fact for security check"
        result = save_memory(fact)
        
        # Should still succeed but use workspace path
        assert result["success"] is True
        
        # Verify the path function was called
        mock_get_path.assert_called()

    def test_memory_error_handling(self):
        """Test memory API error handling for various edge cases."""
        # Test with very long fact
        very_long_fact = "A" * 10000
        result = save_memory(very_long_fact)
        assert result["success"] is True
        
        # Test with unicode characters
        unicode_fact = "User loves 🐍 Python and 🚀 rockets"
        result = save_memory(unicode_fact)
        assert result["success"] is True
        
        # Test with newlines (should be handled properly)
        multiline_fact = "User works on\nmultiple projects"
        result = save_memory(multiline_fact)
        assert result["success"] is True


class TestMemoryAPIIntegration:
    """Integration tests for memory API with common file system functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        DB.clear()
        self.temp_workspace = tempfile.mkdtemp(prefix="test_memory_integration_")
        DB["workspace_root"] = self.temp_workspace
        DB["cwd"] = self.temp_workspace
        DB["file_system"] = {}
        DB["memory_storage"] = {}
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if hasattr(self, 'temp_workspace') and os.path.exists(self.temp_workspace):
            shutil.rmtree(self.temp_workspace, ignore_errors=True)
        DB.clear()

    def test_memory_separation_from_file_system(self):
        """Test that memory storage is separate from file_system."""
        fact = "Test memory separation"
        
        # Save memory
        result = save_memory(fact)
        assert result["success"] is True
        
        # Verify memory is in memory_storage, not file_system
        assert "memory_storage" in DB
        assert len(DB["memory_storage"]) > 0
        
        # Verify memory is NOT in file_system
        file_system = DB.get("file_system", {})
        memory_files_in_fs = [path for path in file_system.keys() if "GEMINI.md" in path]
        assert len(memory_files_in_fs) == 0
        
        # Verify memory is in memory_storage
        memory_storage = DB["memory_storage"]
        memory_files_in_ms = [path for path in memory_storage.keys() if "GEMINI.md" in path]
        assert len(memory_files_in_ms) > 0

    def test_memory_persistence_integration(self):
        """Test memory persistence with DB state."""
        fact = "Test persistence integration"
        
        # Save memory
        result = save_memory(fact)
        assert result["success"] is True
        
        # Simulate DB persistence by checking current state
        memory_storage = DB["memory_storage"]
        assert len(memory_storage) > 0
        
        # Verify memory content persists in memory_storage
        memory_files = [path for path in memory_storage.keys() if "GEMINI.md" in path]
        memory_file_path = memory_files[0]
        content_lines = memory_storage[memory_file_path]["content_lines"]
        content = "".join(content_lines)
        assert f"- {fact}" in content

    def test_complete_memory_workflow(self):
        """Test the complete memory workflow: save, get, update, clear."""
        # Save multiple memories
        facts = [
            "User likes Python programming",
            "User prefers dark mode",
            "User works remotely"
        ]
        
        for fact in facts:
            result = save_memory(fact)
            assert result["success"] is True
        
        # Get all memories
        result = get_memories()
        assert result["success"] is True
        assert len(result["memories"]) == 3
        for fact in facts:
            assert fact in result["memories"]
        
        # Get limited memories
        result = get_memories(limit=2)
        assert result["success"] is True
        assert len(result["memories"]) == 2
        
        # Update a memory
        old_fact = "User likes Python programming"
        new_fact = "User loves Python programming"
        result = update_memory_by_content(old_fact, new_fact)
        assert result["success"] is True
        
        # Verify the update
        result = get_memories()
        assert result["success"] is True
        assert new_fact in result["memories"]
        assert old_fact not in result["memories"]
        
        # Clear all memories
        result = clear_memories()
        assert result["success"] is True
        
        # Verify memories are cleared
        result = get_memories()
        assert result["success"] is True
        assert len(result["memories"]) == 0

    def test_get_memories_with_existing_memories(self):
        """Test get_memories function with pre-existing memories."""
        # Save some memories first
        facts = ["Memory 1", "Memory 2", "Memory 3"]
        for fact in facts:
            save_memory(fact)
        
        # Test getting all memories
        result = get_memories()
        assert result["success"] is True
        assert len(result["memories"]) == 3
        assert "Retrieved 3 memories" in result["message"]
        
        # Test getting limited memories
        result = get_memories(limit=2)
        assert result["success"] is True
        assert len(result["memories"]) == 2
        assert "Retrieved 2 memories" in result["message"]

    def test_clear_memories_with_existing_memories(self):
        """Test clear_memories function with pre-existing memories."""
        # Save some memories first
        fact = "Memory to be cleared"
        save_memory(fact)
        
        # Verify memory exists
        result = get_memories()
        assert result["success"] is True
        assert len(result["memories"]) == 1
        
        # Clear memories
        result = clear_memories()
        assert result["success"] is True
        assert "All memories have been cleared" in result["message"]
        
        # Verify memories are gone
        result = get_memories()
        assert result["success"] is True
        assert len(result["memories"]) == 0

    def test_update_memory_by_content_success(self):
        """Test successful memory update."""
        # Save a memory first
        old_fact = "Original memory content"
        save_memory(old_fact)
        
        # Update the memory
        new_fact = "Updated memory content"
        result = update_memory_by_content(old_fact, new_fact)
        assert result["success"] is True
        assert old_fact in result["message"]
        assert new_fact in result["message"]
        
        # Verify the update
        result = get_memories()
        assert result["success"] is True
        assert new_fact in result["memories"]
        assert old_fact not in result["memories"]

    def test_update_memory_by_content_not_found(self):
        """Test updating a memory that doesn't exist."""
        result = update_memory_by_content("Nonexistent memory", "New content")
        assert result["success"] is False
        assert "No memories found" in result["message"] or "Memory not found" in result["message"]

    def test_memory_content_formatting(self):
        """Test that memory content is properly formatted across all functions."""
        # Save a memory with special formatting
        fact = "Test with special chars: @#$%^&*()"
        save_memory(fact)
        
        # Verify get_memories returns the same content
        result = get_memories()
        assert result["success"] is True
        assert fact in result["memories"]
        
        # Update the memory
        new_fact = "Updated with different chars: !@#$%"
        update_memory_by_content(fact, new_fact)
        
        # Verify the updated content
        result = get_memories()
        assert result["success"] is True
        assert new_fact in result["memories"]
        assert fact not in result["memories"]

    def test_memory_functions_consistency(self):
        """Test that all memory functions work consistently with memory_storage."""
        # This test ensures all functions use memory_storage, not file_system
        fact = "Consistency test memory"
        
        # Save memory (uses memory_storage)
        save_memory(fact)
        
        # Verify memory_storage has the entry but file_system doesn't
        memory_storage = DB.get("memory_storage", {})
        file_system = DB.get("file_system", {})
        
        memory_files_in_storage = [path for path in memory_storage.keys() if "GEMINI.md" in path]
        memory_files_in_fs = [path for path in file_system.keys() if "GEMINI.md" in path]
        
        assert len(memory_files_in_storage) > 0
        assert len(memory_files_in_fs) == 0
        
        # Get memories (should also use memory_storage)
        result = get_memories()
        assert result["success"] is True
        assert fact in result["memories"]
        
        # Update memory (should also use memory_storage)
        new_fact = "Updated consistency test"
        result = update_memory_by_content(fact, new_fact)
        assert result["success"] is True
        
        # Verify update worked
        result = get_memories()
        assert result["success"] is True
        assert new_fact in result["memories"]
        assert fact not in result["memories"]
        
        # Clear memories (should also use memory_storage)
        result = clear_memories()
        assert result["success"] is True
        
        # Verify clear worked
        result = get_memories()
        assert result["success"] is True
        assert len(result["memories"]) == 0 