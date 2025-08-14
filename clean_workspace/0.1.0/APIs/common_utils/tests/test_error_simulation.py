#!/usr/bin/env python3
"""
Tests for ErrorSimulation module.
"""

import unittest
import os
import sys
import tempfile
import json
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import common_utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from common_utils.ErrorSimulation import ErrorSimulator


class TestErrorSimulation(unittest.TestCase):
    """Test cases for ErrorSimulation module."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary files for testing
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        self.definitions_file = os.path.join(self.temp_dir, "test_definitions.json")
        
        # Create test configuration
        test_config = {
            "ValueError": {
                "probability": 0.5
            }
        }
        
        test_definitions = {
            "test.function": [
                {
                    "exception": "ValueError",
                    "message": "Test error message"
                }
            ]
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(test_config, f)
        
        with open(self.definitions_file, 'w') as f:
            json.dump(test_definitions, f)

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temporary files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_error_simulator_initialization(self):
        """Test ErrorSimulator initialization."""
        simulator = ErrorSimulator(self.config_file, self.definitions_file)
        
        # Verify the simulator was created
        self.assertIsInstance(simulator, ErrorSimulator)

    def test_error_simulator_with_nonexistent_files(self):
        """Test ErrorSimulator with nonexistent files."""
        # Should not raise an exception
        simulator = ErrorSimulator("nonexistent_config.json", "nonexistent_definitions.json")
        self.assertIsInstance(simulator, ErrorSimulator)

    def test_get_error_simulation_decorator(self):
        """Test get_error_simulation_decorator method."""
        simulator = ErrorSimulator(self.config_file, self.definitions_file)
        
        decorator = simulator.get_error_simulation_decorator("test.function")
        
        # Verify decorator is callable
        self.assertTrue(callable(decorator))

    def test_error_simulation_decorator_no_error(self):
        """Test error simulation decorator when no error should be raised."""
        simulator = ErrorSimulator(self.config_file, self.definitions_file)
        
        decorator = simulator.get_error_simulation_decorator("test.another_function")
        
        @decorator
        def test_func():
            return "success"
        
        # Should not raise an exception
        result = test_func()
        self.assertEqual(result, "success")

    def test_error_simulation_decorator_with_error(self):
        """Test error simulation decorator when error should be raised."""
        simulator = ErrorSimulator(self.config_file, self.definitions_file)
        
        decorator = simulator.get_error_simulation_decorator("test.function")
        
        @decorator
        def test_func():
            return "success"
        
        # With 50% probability, should either raise an error or return success
        # We can't predict the outcome, but we can test that it doesn't crash
        try:
            result = test_func()
            # If no exception, should return success
            self.assertEqual(result, "success")
        except ValueError as e:
            # If exception, should have the expected message
            self.assertEqual(str(e), "Test error message")

    def test_error_simulation_decorator_with_arguments(self):
        """Test error simulation decorator with function arguments."""
        simulator = ErrorSimulator(self.config_file, self.definitions_file)
        
        decorator = simulator.get_error_simulation_decorator("test.function")
        
        @decorator
        def test_func(arg1, arg2, kwarg1="default"):
            return f"result: {arg1}, {arg2}, {kwarg1}"
        
        # Test with arguments
        try:
            result = test_func("arg1", "arg2", kwarg1="custom")
            self.assertEqual(result, "result: arg1, arg2, custom")
        except ValueError as e:
            self.assertEqual(str(e), "Test error message")

    def test_error_simulation_decorator_function_metadata(self):
        """Test error simulation decorator preserves function metadata."""
        simulator = ErrorSimulator(self.config_file, self.definitions_file)
        
        decorator = simulator.get_error_simulation_decorator("test.function")
        
        @decorator
        def test_func(arg1, arg2, kwarg1="default"):
            """Test function docstring."""
            return "success"
        
        # Verify function metadata is preserved
        self.assertEqual(test_func.__name__, 'test_func')
        self.assertEqual(test_func.__doc__, 'Test function docstring.')

    def test_error_simulator_with_empty_config(self):
        """Test ErrorSimulator with empty configuration."""
        # Create empty config files
        empty_config_file = os.path.join(self.temp_dir, "empty_config.json")
        empty_definitions_file = os.path.join(self.temp_dir, "empty_definitions.json")
        
        with open(empty_config_file, 'w') as f:
            json.dump({}, f)
        
        with open(empty_definitions_file, 'w') as f:
            json.dump({}, f)
        
        simulator = ErrorSimulator(empty_config_file, empty_definitions_file)
        
        decorator = simulator.get_error_simulation_decorator("any.function")
        
        @decorator
        def test_func():
            return "success"
        
        # Should always return success with empty config
        result = test_func()
        self.assertEqual(result, "success")

    def test_error_simulator_with_invalid_json(self):
        """Test ErrorSimulator with invalid JSON files."""
        # Create invalid JSON files
        invalid_config_file = os.path.join(self.temp_dir, "invalid_config.json")
        invalid_definitions_file = os.path.join(self.temp_dir, "invalid_definitions.json")
        
        with open(invalid_config_file, 'w') as f:
            f.write("invalid json content")
        
        with open(invalid_definitions_file, 'w') as f:
            f.write("invalid json content")
        
        # Should not raise an exception
        simulator = ErrorSimulator(invalid_config_file, invalid_definitions_file)
        self.assertIsInstance(simulator, ErrorSimulator)

    def test_error_simulator_with_missing_error_definitions(self):
        """Test ErrorSimulator when error definitions are missing."""
        simulator = ErrorSimulator(self.config_file, self.definitions_file)
        
        # Test with a function that has config but no definitions
        decorator = simulator.get_error_simulation_decorator("test.another_function")
        
        @decorator
        def test_func():
            return "success"
        
        # Should not raise an exception even if definitions are missing
        result = test_func()
        self.assertEqual(result, "success")

    def test_error_simulator_with_0_percent_error_rate(self):
        """Test ErrorSimulator with 0% error rate."""
        # Create config with 0% error rate
        config_0 = {
            "ValueError": {
                "probability": 0.0
            }
        }
        
        config_file_0 = os.path.join(self.temp_dir, "config_0.json")
        with open(config_file_0, 'w') as f:
            json.dump(config_0, f)
        
        simulator = ErrorSimulator(config_file_0, self.definitions_file)
        
        decorator = simulator.get_error_simulation_decorator("test.function")
        
        @decorator
        def test_func():
            return "success"
        
        # Should never raise an exception
        result = test_func()
        self.assertEqual(result, "success")


if __name__ == '__main__':
    unittest.main() 