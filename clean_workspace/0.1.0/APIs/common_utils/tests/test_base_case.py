#!/usr/bin/env python3
"""
Tests for base_case module.
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import common_utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from common_utils.base_case import BaseTestCaseWithErrorHandler
from common_utils.error_handling import get_package_error_mode
from pydantic import ValidationError


class TestBaseTestCaseWithErrorHandler(BaseTestCaseWithErrorHandler):
    """Test cases for BaseTestCaseWithErrorHandler class."""

    def test_assert_error_behavior_raise_mode(self):
        """Test assert_error_behavior in raise mode."""
        with patch('common_utils.base_case.get_package_error_mode', return_value='raise'):
            def test_function():
                raise ValueError("Test error message")
            
            self.assert_error_behavior(
                test_function,
                ValueError,
                "Test error message"
            )

    def test_assert_error_behavior_error_dict_mode(self):
        """Test assert_error_behavior in error_dict mode."""
        with patch('common_utils.base_case.get_package_error_mode', return_value='error_dict'):
            def test_function():
                return {
                    "exceptionType": "ValueError",
                    "message": "Test error message",
                    "additional_field": "test_value"
                }
            
            self.assert_error_behavior(
                test_function,
                ValueError,
                "Test error message",
                {"additional_field": "test_value"}
            )

    def test_assert_error_behavior_invalid_error_mode(self):
        """Test assert_error_behavior with invalid error mode."""
        with patch('common_utils.base_case.get_package_error_mode', return_value='INVALID'):
            def test_function():
                pass
            
            with self.assertRaises(AssertionError):
                self.assert_error_behavior(
                    test_function,
                    ValueError,
                    "Test error message"
                )

    def test_assert_error_behavior_name_error(self):
        """Test assert_error_behavior when ERROR_MODE is not defined."""
        with patch('common_utils.base_case.get_package_error_mode', side_effect=NameError):
            def test_function():
                pass
            
            with self.assertRaises(AssertionError):
                self.assert_error_behavior(
                    test_function,
                    ValueError,
                    "Test error message"
                )

    def test_assert_error_behavior_no_exception_raises(self):
        """Test assert_error_behavior when function doesn't raise expected exception."""
        with patch('common_utils.base_case.get_package_error_mode', return_value='raise'):
            def test_function():
                return "success"
            
            with self.assertRaises(AssertionError):
                self.assert_error_behavior(
                    test_function,
                    ValueError,
                    "Test error message"
                )

    def test_assert_error_behavior_wrong_message(self):
        """Test assert_error_behavior when wrong error message is raised."""
        with patch('common_utils.base_case.get_package_error_mode', return_value='raise'):
            def test_function():
                raise ValueError("Wrong message")
            
            with self.assertRaises(AssertionError):
                self.assert_error_behavior(
                    test_function,
                    ValueError,
                    "Expected message"
                )

    def test_assert_error_behavior_error_dict_wrong_type(self):
        """Test assert_error_behavior in error_dict mode with wrong return type."""
        with patch('common_utils.base_case.get_package_error_mode', return_value='error_dict'):
            def test_function():
                return "not a dict"
            
            with self.assertRaises(AssertionError):
                self.assert_error_behavior(
                    test_function,
                    ValueError,
                    "Test error message"
                )

    def test_assert_error_behavior_error_dict_missing_fields(self):
        """Test assert_error_behavior in error_dict mode with missing fields."""
        with patch('common_utils.base_case.get_package_error_mode', return_value='error_dict'):
            def test_function():
                return {"message": "Test error message"}  # Missing exceptionType
            
            with self.assertRaises(AssertionError):
                self.assert_error_behavior(
                    test_function,
                    ValueError,
                    "Test error message"
                )


if __name__ == '__main__':
    unittest.main() 