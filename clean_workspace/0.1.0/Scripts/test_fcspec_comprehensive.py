#!/usr/bin/env python3
"""
Comprehensive test suite for Documentation/Scripts/FCSpec.py

This test focuses on the actual behavior - docstring parsing and schema generation -
rather than internal implementation details. It uses sample docstrings and tests
the expected output schemas.
"""

import os
import sys
import ast
import unittest
import tempfile
import json
from typing import Optional, Union, List, Dict, Any

# Add Documentation/Scripts to the path
DOC_SCRIPTS_PATH = os.path.abspath('/home/ngota/Turing/Official API stuff/Documentation/Scripts')
if DOC_SCRIPTS_PATH not in sys.path:
    sys.path.insert(0, DOC_SCRIPTS_PATH)

# Import the module and functions from Documentation/Scripts
import FCSpec as doc_fcspec
# Import functions directly from the module
build_initial_schema = doc_fcspec.build_initial_schema
map_type = doc_fcspec.map_type
parse_object_properties_from_description = doc_fcspec.parse_object_properties_from_description


class TestDocstringParsingAndSchemaGeneration(unittest.TestCase):
    """Test cases for docstring parsing and schema generation with sample docstrings."""
    
    def create_function_ast(self, func_def: str) -> ast.FunctionDef:
        """Helper to create AST node from function definition string."""
        tree = ast.parse(func_def)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                return node
        raise ValueError("No FunctionDef found in AST")
    
    def test_basic_optional_parameter_detection(self):
        """Test that Optional parameters are correctly identified as not required."""
        func_def = '''
def process_user_data(user_id: str, name: Optional[str], age: Optional[int], email: str = None):
    """
    Process user data with various parameter types.
    
    Args:
        user_id (str): The unique identifier for the user (required)
        name (Optional[str]): The user's name (optional)
        age (Optional[int]): The user's age (optional)
        email (str, optional): The user's email address (optional, defaults to None)
    """
    pass
'''
        func_node = self.create_function_ast(func_def)
        docstring = ast.get_docstring(func_node)
        parsed_doc = doc_fcspec.docstring_parser.parse(docstring)
        schema = doc_fcspec.build_initial_schema(parsed_doc, func_node, "process_user_data")
        
        # Check required parameters
        required = schema["parameters"].get("required", [])
        self.assertIn("user_id", required, "user_id should be required")
        self.assertNotIn("name", required, "name should not be required (Optional)")
        self.assertNotIn("age", required, "age should not be required (Union with None)")
        self.assertNotIn("email", required, "email should not be required (has default)")
        
        # Check parameter types
        properties = schema["parameters"]["properties"]
        self.assertEqual(properties["user_id"]["type"], doc_fcspec.JSON_TYPE_STRING)
        self.assertEqual(properties["name"]["type"], doc_fcspec.JSON_TYPE_STRING)  # Optional[str] -> str
        self.assertEqual(properties["age"]["type"], doc_fcspec.JSON_TYPE_INTEGER)  # Union[int, None] -> int
        self.assertEqual(properties["email"]["type"], doc_fcspec.JSON_TYPE_STRING)
    
    def test_dict_property_breakdown(self):
        """Test that dict types with properties in docstring are broken down correctly."""
        func_def = '''
def create_user(user_data: dict):
    """
    Create a new user with the provided data.
    
    Args:
        user_data (dict): Dictionary containing user information
            name (str): The user's full name
            age (int): The user's age in years
            email (str, optional): The user's email address
            preferences (dict): User preferences
                theme (str): UI theme preference
                notifications (bool): Whether to send notifications
    """
    pass
'''
        func_node = self.create_function_ast(func_def)
        docstring = ast.get_docstring(func_node)
        parsed_doc = doc_fcspec.docstring_parser.parse(docstring)
        schema = doc_fcspec.build_initial_schema(parsed_doc, func_node, "create_user")
        
        # Check that user_data is an object with properties
        user_data_schema = schema["parameters"]["properties"]["user_data"]
        self.assertEqual(user_data_schema["type"], doc_fcspec.JSON_TYPE_OBJECT)
        self.assertIn("properties", user_data_schema)
        
        # Check top-level properties
        properties = user_data_schema["properties"]
        self.assertIn("name", properties)
        self.assertIn("age", properties)
        self.assertIn("email", properties)
        self.assertIn("preferences", properties)
        
        # Check property types
        self.assertEqual(properties["name"]["type"], doc_fcspec.JSON_TYPE_STRING)
        self.assertEqual(properties["age"]["type"], doc_fcspec.JSON_TYPE_INTEGER)
        self.assertEqual(properties["email"]["type"], doc_fcspec.JSON_TYPE_STRING)
        self.assertEqual(properties["preferences"]["type"], doc_fcspec.JSON_TYPE_OBJECT)
        
        # Check nested properties in preferences
        pref_properties = properties["preferences"]["properties"]
        self.assertIn("theme", pref_properties)
        self.assertIn("notifications", pref_properties)
        self.assertEqual(pref_properties["theme"]["type"], doc_fcspec.JSON_TYPE_STRING)
        self.assertEqual(pref_properties["notifications"]["type"], doc_fcspec.JSON_TYPE_BOOLEAN)
        
        # Check required properties (email should not be required due to "optional")
        required = user_data_schema.get("required", [])
        self.assertIn("name", required, "name should be required")
        self.assertIn("age", required, "age should be required")
        self.assertNotIn("email", required, "email should not be required (marked as optional)")
        self.assertIn("preferences", required, "preferences should be required")
        
        # Check nested required properties
        pref_required = properties["preferences"].get("required", [])
        self.assertIn("theme", pref_required, "theme should be required")
        self.assertIn("notifications", pref_required, "notifications should be required")
    
    def test_complex_nested_dict_structure(self):
        """Test complex nested dictionary structures with multiple levels."""
        func_def = '''
def update_config(config: dict):
    """
    Update application configuration.
    
    Args:
        config (dict): Configuration dictionary
            database (dict): Database configuration
                host (str): Database host
                port (int): Database port
                credentials (dict): Database credentials
                    username (str): Database username
                    password (str): Database password
                    ssl (bool, optional): Use SSL connection
            api (dict): API configuration
                endpoints (list): List of API endpoints
                timeout (int, optional): Request timeout in seconds
                retries (dict): Retry configuration
                    max_attempts (int): Maximum retry attempts
                    backoff_factor (float): Backoff multiplier
    """
    pass
'''
        func_node = self.create_function_ast(func_def)
        docstring = ast.get_docstring(func_node)
        parsed_doc = doc_fcspec.docstring_parser.parse(docstring)
        schema = doc_fcspec.build_initial_schema(parsed_doc, func_node, "update_config")
        
        config_schema = schema["parameters"]["properties"]["config"]
        self.assertEqual(config_schema["type"], doc_fcspec.JSON_TYPE_OBJECT)
        
        # Check top-level properties
        properties = config_schema["properties"]
        self.assertIn("database", properties)
        self.assertIn("api", properties)
        
        # Check database properties
        db_props = properties["database"]["properties"]
        self.assertIn("host", db_props)
        self.assertIn("port", db_props)
        self.assertIn("credentials", db_props)
        self.assertEqual(db_props["host"]["type"], doc_fcspec.JSON_TYPE_STRING)
        self.assertEqual(db_props["port"]["type"], doc_fcspec.JSON_TYPE_INTEGER)
        
        # Check nested credentials
        cred_props = db_props["credentials"]["properties"]
        self.assertIn("username", cred_props)
        self.assertIn("password", cred_props)
        self.assertIn("ssl", cred_props)
        self.assertEqual(cred_props["username"]["type"], doc_fcspec.JSON_TYPE_STRING)
        self.assertEqual(cred_props["password"]["type"], doc_fcspec.JSON_TYPE_STRING)
        self.assertEqual(cred_props["ssl"]["type"], doc_fcspec.JSON_TYPE_BOOLEAN)
        
        # Check API properties
        api_props = properties["api"]["properties"]
        self.assertIn("endpoints", api_props)
        self.assertIn("timeout", api_props)
        self.assertIn("retries", api_props)
        self.assertEqual(api_props["endpoints"]["type"], doc_fcspec.JSON_TYPE_ARRAY)
        self.assertEqual(api_props["timeout"]["type"], doc_fcspec.JSON_TYPE_INTEGER)
        
        # Check retries properties
        retry_props = api_props["retries"]["properties"]
        self.assertIn("max_attempts", retry_props)
        self.assertIn("backoff_factor", retry_props)
        self.assertEqual(retry_props["max_attempts"]["type"], doc_fcspec.JSON_TYPE_INTEGER)
        self.assertEqual(retry_props["backoff_factor"]["type"], doc_fcspec.JSON_TYPE_NUMBER)
        
        # Check required properties
        config_required = config_schema.get("required", [])
        self.assertIn("database", config_required)
        self.assertIn("api", config_required)
        
        db_required = properties["database"].get("required", [])
        self.assertIn("host", db_required)
        self.assertIn("port", db_required)
        self.assertIn("credentials", db_required)
        self.assertNotIn("ssl", db_required)  # Optional
        
        cred_required = db_props["credentials"].get("required", [])
        self.assertIn("username", cred_required)
        self.assertIn("password", cred_required)
        self.assertNotIn("ssl", cred_required)  # Optional
        
        api_required = properties["api"].get("required", [])
        self.assertIn("endpoints", api_required)
        self.assertIn("retries", api_required)
        self.assertNotIn("timeout", api_required)  # Optional
        
        retry_required = api_props["retries"].get("required", [])
        self.assertIn("max_attempts", retry_required)
        self.assertIn("backoff_factor", retry_required)
    
    def test_optional_types(self):
        """Test Optional types that can be None."""
        func_def = '''
def process_data(data: Optional[str], count: Optional[int], items: Optional[List[str]]):
    """
    Process data with Optional types that can be None.
    
    Args:
        data (Optional[str]): String data or None
        count (Optional[int]): Integer count or None
        items (Optional[List[str]]): List of strings or None
    """
    pass
'''
        func_node = self.create_function_ast(func_def)
        docstring = ast.get_docstring(func_node)
        parsed_doc = doc_fcspec.docstring_parser.parse(docstring)
        schema = doc_fcspec.build_initial_schema(parsed_doc, func_node, "process_data")
        
        # Check that all parameters are not required (Optional makes them optional)
        required = schema["parameters"].get("required", [])
        self.assertNotIn("data", required, "data should not be required (Optional)")
        self.assertNotIn("count", required, "count should not be required (Optional)")
        self.assertNotIn("items", required, "items should not be required (Optional)")
        
        # Check parameter types (should be the non-None type)
        properties = schema["parameters"]["properties"]
        self.assertEqual(properties["data"]["type"], doc_fcspec.JSON_TYPE_STRING)
        self.assertEqual(properties["count"]["type"], doc_fcspec.JSON_TYPE_INTEGER)
        self.assertEqual(properties["items"]["type"], doc_fcspec.JSON_TYPE_ARRAY)
    
    def test_optional_none_only(self):
        """Test Optional with only None type."""
        func_def = '''
def no_data(data: Optional[None]):
    """
    Function that only accepts None.
    
    Args:
        data (Optional[None]): Must be None
    """
    pass
'''
        func_node = self.create_function_ast(func_def)
        docstring = ast.get_docstring(func_node)
        parsed_doc = doc_fcspec.docstring_parser.parse(docstring)
        schema = doc_fcspec.build_initial_schema(parsed_doc, func_node, "no_data")
        
        # Check that parameter type is null
        properties = schema["parameters"]["properties"]
        self.assertEqual(properties["data"]["type"], doc_fcspec.JSON_TYPE_NULL)
        
        # Parameter should not be required (it's effectively optional)
        required = schema["parameters"].get("required", [])
        self.assertNotIn("data", required, "Optional[None] parameter should not be required")
    
    def test_mixed_parameter_types(self):
        """Test function with mixed parameter types including defaults."""
        func_def = '''
def complex_function(
    required_str: str,
    optional_str: Optional[str],
    optional_int: Optional[int],
    with_default: str = "default",
    optional_with_default: Optional[str] = None,
    dict_param: dict = None
):
    """
    Function with mixed parameter types.
    
    Args:
        required_str (str): Required string parameter
        optional_str (Optional[str]): Optional string parameter
        optional_int (Optional[int]): Optional integer parameter
        with_default (str): Parameter with default value
        optional_with_default (Optional[str]): Optional parameter with default
        dict_param (dict): Dictionary parameter with default
            key1 (str): First key
            key2 (int, optional): Second key
    """
    pass
'''
        func_node = self.create_function_ast(func_def)
        docstring = ast.get_docstring(func_node)
        parsed_doc = doc_fcspec.docstring_parser.parse(docstring)
        schema = doc_fcspec.build_initial_schema(parsed_doc, func_node, "complex_function")
        
        # Only required_str should be required
        required = schema["parameters"].get("required", [])
        self.assertIn("required_str", required, "required_str should be required")
        self.assertNotIn("optional_str", required, "optional_str should not be required (Optional)")
        self.assertNotIn("optional_int", required, "optional_int should not be required (Optional)")
        self.assertNotIn("with_default", required, "with_default should not be required (has default)")
        self.assertNotIn("optional_with_default", required, "optional_with_default should not be required (Optional with default)")
        self.assertNotIn("dict_param", required, "dict_param should not be required (has default)")
        
        # Check dict_param properties
        dict_schema = schema["parameters"]["properties"]["dict_param"]
        self.assertEqual(dict_schema["type"], doc_fcspec.JSON_TYPE_OBJECT)
        self.assertIn("properties", dict_schema)
        
        dict_props = dict_schema["properties"]
        self.assertIn("key1", dict_props)
        self.assertIn("key2", dict_props)
        self.assertEqual(dict_props["key1"]["type"], doc_fcspec.JSON_TYPE_STRING)
        self.assertEqual(dict_props["key2"]["type"], doc_fcspec.JSON_TYPE_INTEGER)
        
        # Check dict required properties
        dict_required = dict_schema.get("required", [])
        self.assertIn("key1", dict_required, "key1 should be required")
        self.assertNotIn("key2", dict_required, "key2 should not be required (optional)")
    
    def test_edge_cases(self):
        """Test edge cases and error conditions."""
        # Test function with no docstring
        func_def = '''
def no_docstring(param: str):
    pass
'''
        func_node = self.create_function_ast(func_def)
        docstring = ast.get_docstring(func_node)
        self.assertIsNone(docstring)
        
        # Test function with empty docstring
        func_def = '''
def empty_docstring(param: str):
    """
    """
    pass
'''
        func_node = self.create_function_ast(func_def)
        docstring = ast.get_docstring(func_node)
        parsed_doc = doc_fcspec.docstring_parser.parse(docstring)
        schema = doc_fcspec.build_initial_schema(parsed_doc, func_node, "empty_docstring")
        
        # Should still have the parameter in properties
        properties = schema["parameters"]["properties"]
        self.assertNotIn("param", properties)
        
        # # Should be required (no default, no Optional, no Union with None)
        # required = schema["parameters"].get("required", [])
        # self.assertIn("param", required, "param should be required")
        
        # Test function with proper Google-style docstring
        func_def = '''
def proper_docstring(param: str):
    """
    Function with proper Google-style docstring.
    
    Args:
        param (str): A string parameter
    """
    pass
'''
        func_node = self.create_function_ast(func_def)
        docstring = ast.get_docstring(func_node)
        parsed_doc = doc_fcspec.docstring_parser.parse(docstring)
        schema = doc_fcspec.build_initial_schema(parsed_doc, func_node, "proper_docstring")
        
        # Should have the parameter in properties
        properties = schema["parameters"]["properties"]
        self.assertIn("param", properties)
        self.assertEqual(properties["param"]["type"], doc_fcspec.JSON_TYPE_STRING)
        
        # Should be required
        required = schema["parameters"].get("required", [])
        self.assertIn("param", required, "param should be required")
    
    def test_list_and_array_types(self):
        """Test List and array type handling."""
        func_def = '''
def process_lists(
    string_list: List[str],
    int_list: List[int],
    mixed_list: List[Any],
    optional_list: Optional[List[str]]
):
    """
    Process various list types.
    
    Args:
        string_list (List[str]): List of strings
        int_list (List[int]): List of integers
        mixed_list (List[Any]): List of mixed types
        optional_list (Optional[List[str]]): Optional list of strings
    """
    pass
'''
        func_node = self.create_function_ast(func_def)
        docstring = ast.get_docstring(func_node)
        parsed_doc = doc_fcspec.docstring_parser.parse(docstring)
        schema = doc_fcspec.build_initial_schema(parsed_doc, func_node, "process_lists")
        
        properties = schema["parameters"]["properties"]
        
        # Check that all list types are mapped to array
        self.assertEqual(properties["string_list"]["type"], doc_fcspec.JSON_TYPE_ARRAY)
        self.assertEqual(properties["int_list"]["type"], doc_fcspec.JSON_TYPE_ARRAY)
        self.assertEqual(properties["mixed_list"]["type"], doc_fcspec.JSON_TYPE_ARRAY)
        self.assertEqual(properties["optional_list"]["type"], doc_fcspec.JSON_TYPE_ARRAY)
        
        # Check required parameters
        required = schema["parameters"].get("required", [])
        self.assertIn("string_list", required)
        self.assertIn("int_list", required)
        self.assertIn("mixed_list", required)
        self.assertNotIn("optional_list", required, "optional_list should not be required (Optional)")


class TestMapTypeFunction(unittest.TestCase):
    """Test cases for the map_type function directly."""
    
    def test_basic_types(self):
        """Test basic type mapping."""
        test_cases = [
            ("str", doc_fcspec.JSON_TYPE_STRING),
            ("int", doc_fcspec.JSON_TYPE_INTEGER),
            ("float", doc_fcspec.JSON_TYPE_NUMBER),
            ("bool", doc_fcspec.JSON_TYPE_BOOLEAN),
            ("list", doc_fcspec.JSON_TYPE_ARRAY),
            ("dict", doc_fcspec.JSON_TYPE_OBJECT),
            ("Any", doc_fcspec.JSON_TYPE_OBJECT),
            ("", doc_fcspec.JSON_TYPE_OBJECT),  # Empty string
            (None, doc_fcspec.JSON_TYPE_OBJECT),  # None
        ]
        
        for type_str, expected_type in test_cases:
            with self.subTest(type_str=type_str):
                result = doc_fcspec.map_type(type_str)
                self.assertEqual(result["type"], expected_type, f"Failed for '{type_str}'")
    
    def test_optional_types(self):
        """Test Optional type mapping."""
        test_cases = [
            ("Optional[str]", doc_fcspec.JSON_TYPE_STRING),
            ("Optional[int]", doc_fcspec.JSON_TYPE_INTEGER),
            ("Optional[float]", doc_fcspec.JSON_TYPE_NUMBER),
            ("Optional[bool]", doc_fcspec.JSON_TYPE_BOOLEAN),
            ("Optional[Any]", doc_fcspec.JSON_TYPE_OBJECT),
            ("Optional[]", doc_fcspec.JSON_TYPE_NULL),  # Optional[Any]
        ]
        
        for type_str, expected_type in test_cases:
            with self.subTest(type_str=type_str):
                result = doc_fcspec.map_type(type_str)
                self.assertEqual(result["type"], expected_type, f"Failed for '{type_str}'")
    
    def test_union_types(self):
        """Test Union type mapping."""
        test_cases = [
            ("Union[str, None]", doc_fcspec.JSON_TYPE_STRING),
            ("Union[None, str]", doc_fcspec.JSON_TYPE_STRING),
            ("Union[int, None]", doc_fcspec.JSON_TYPE_INTEGER),
            ("Union[str, int, None]", doc_fcspec.JSON_TYPE_STRING),  # First non-null type
            ("Union[None]", doc_fcspec.JSON_TYPE_NULL),
            ("Union[str, int]", doc_fcspec.JSON_TYPE_STRING),  # Multiple non-null types
        ]
        
        for type_str, expected_type in test_cases:
            with self.subTest(type_str=type_str):
                result = doc_fcspec.map_type(type_str)
                self.assertEqual(result["type"], expected_type, f"Failed for '{type_str}'")
    
    def test_list_types(self):
        """Test List type mapping."""
        test_cases = [
            ("List[str]", doc_fcspec.JSON_TYPE_ARRAY),
            ("List[int]", doc_fcspec.JSON_TYPE_ARRAY),
            ("List[Any]", doc_fcspec.JSON_TYPE_ARRAY),
            ("list[str]", doc_fcspec.JSON_TYPE_ARRAY),
            ("list[int]", doc_fcspec.JSON_TYPE_ARRAY),
        ]
        
        for type_str, expected_type in test_cases:
            with self.subTest(type_str=type_str):
                result = doc_fcspec.map_type(type_str)
                self.assertEqual(result["type"], expected_type, f"Failed for '{type_str}'")
    
    def test_dict_types(self):
        """Test Dict type mapping."""
        test_cases = [
            ("Dict[str, Any]", doc_fcspec.JSON_TYPE_OBJECT),
            ("Dict[str, int]", doc_fcspec.JSON_TYPE_OBJECT),
            ("dict[str, Any]", doc_fcspec.JSON_TYPE_OBJECT),
            ("dict[str, int]", doc_fcspec.JSON_TYPE_OBJECT),
        ]
        
        for type_str, expected_type in test_cases:
            with self.subTest(type_str=type_str):
                result = doc_fcspec.map_type(type_str)
                self.assertEqual(result["type"], expected_type, f"Failed for '{type_str}'")
                self.assertIn("properties", result)
                self.assertEqual(result["properties"], {})


if __name__ == "__main__":
    unittest.main(verbosity=2) 