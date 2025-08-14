# %%
import os
import shutil
import sys
import ast
import json
import docstring_parser
import importlib
from typing import Dict, List, Tuple, Optional, Any, Union, Set
import re
from google import genai
import concurrent.futures
import threading
import argparse
from pathlib import Path

# --- Pydantic Validation ---
# Add the common_utils path to sys.path to allow importing the models
current_file_dir = Path(__file__).parent
api_gen_dir = current_file_dir.parent
common_utils_dir = api_gen_dir / "APIs" / "common_utils"
sys.path.append(str(api_gen_dir))
# TODO: Check with @Joseph on this 
#from common_utils.models import CentralConfig, ServiceDocumentationConfig, DocMode

DOC_MODE = "raw_docstring"

# --- Configuration & Constants ---
API_KEY = "API KEY HERE"  # In canvas in api team channel
MAX_WORKERS = 10 # Adjust based on system capabilities
print_lock = threading.Lock()

JSON_TYPE_STRING = "string"
JSON_TYPE_INTEGER = "integer"
JSON_TYPE_NUMBER = "number"
JSON_TYPE_BOOLEAN = "boolean"
JSON_TYPE_ARRAY = "array"
JSON_TYPE_OBJECT = "object"
JSON_TYPE_NULL = "null"

# --- Helper Functions ---
# Global variables to track configuration state
_original_doc_mode = DOC_MODE
_applied_config = None
_config_backup = None

def apply_config(config_input: Union[str, dict]) -> bool:
    """
    Applies a configuration to override the default DOC_MODE for specific packages.
    
    Args:
        config_input (Union[str, dict]): Either a path to the configuration JSON file or a config dict
        
    Returns:
        bool: True if configuration was successfully applied, False otherwise
    """
    global _applied_config, _config_backup, DOC_MODE
    
    try:
        # Handle config input - either file path or dict
        if isinstance(config_input, str):
            # Load and validate the configuration file
            with open(config_input, "r") as f:
                config_data = json.load(f)
        elif isinstance(config_input, dict):
            # Use the config dict directly
            config_data = config_input
        else:
            safe_print(f"❌ Invalid config input type: {type(config_input)}. Expected str (file path) or dict")
            return False
        
        # # Validate the structure using Pydantic models
        # validated_config = CentralConfig(**config_data)
        # documentation_config = validated_config.documentation
        
        # if not documentation_config:
        #     safe_print(f"Warning: No 'documentation' section found in config")
        #     return False
        
        # # Backup current configuration
        # _config_backup = {
        #     "doc_mode": DOC_MODE,
        #     "applied_config": _applied_config
        # }
        
        # # Store the applied configuration
        # _applied_config = documentation_config
        
        # if isinstance(config_input, str):
        #     safe_print(f"✅ Configuration applied from {config_input}")
        # else:
        #     safe_print(f"✅ Configuration applied from dict")
        # safe_print(f"   Applied config: {_applied_config}")
        
        return True
        
    except FileNotFoundError:
        safe_print(f"❌ Configuration file not found: {config_input}")
        return False
    except json.JSONDecodeError as e:
        safe_print(f"❌ Invalid JSON in configuration file {config_input}: {e}")
        return False
    except Exception as e:
        safe_print(f"❌ Error applying configuration: {e}")
        return False

def rollback_config() -> bool:
    """
    Reverts the configuration back to the original DOC_MODE for all packages.
    
    Returns:
        bool: True if rollback was successful, False otherwise
    """
    global _applied_config, _config_backup, DOC_MODE
    
    if _config_backup is None:
        safe_print("❌ No configuration to rollback - no config was previously applied")
        return False
    
    # Restore original configuration
    DOC_MODE = _config_backup["doc_mode"]
    _applied_config = _config_backup["applied_config"]
    _config_backup = None
    
    safe_print(f"✅ Configuration rolled back to original DOC_MODE: {DOC_MODE}")
    return True

def get_current_doc_mode(package_name: str) -> str:
    """
    Gets the current doc mode for a specific package, considering applied configuration.
    
    Args:
        package_name (str): Name of the package
        
    Returns:
        str: The doc mode to use for this package
    """
    # If a config was applied, check if this package has a specific doc_mode
    if _applied_config:
        # Check if this package has a specific configuration in services
        if _applied_config.services and package_name in _applied_config.services:
            package_config = _applied_config.services[package_name]
            return package_config.doc_mode.value
        
        # Check if there's a global configuration
        if _applied_config.global_config:
            return _applied_config.global_config.doc_mode.value
    
    # Fall back to the current global DOC_MODE
    return DOC_MODE

def get_config_status() -> Dict[str, Any]:
    """
    Returns the current configuration status.
    
    Returns:
        Dict[str, Any]: Current configuration state
    """
    return {
        "original_doc_mode": _original_doc_mode,
        "current_doc_mode": DOC_MODE,
        "applied_config": _applied_config,
        "has_backup": _config_backup is not None
    }

def safe_print(*args, **kwargs):
    """Thread-safe printing function that uses a lock to prevent output interleaving.
    
    Args:
        *args: Variable length argument list to print
        **kwargs: Arbitrary keyword arguments to pass to print
    """
    with print_lock:
        print(*args, **kwargs)

def get_variable_from_file(filepath: str, variable_name: str) -> Optional[Dict]:
    """Safely extracts a variable from a Python file using AST parsing.
    
    Args:
        filepath (str): Path to the Python file to parse
        variable_name (str): Name of the variable to extract
        
    Returns:
        Optional[Dict]: The value of the variable if found and successfully parsed, None otherwise
    """
    if not os.path.exists(filepath): return None
    with open(filepath, "r", encoding="utf-8") as source_file:
        source_code = source_file.read()
    try:
        tree = ast.parse(source_code, filename=filepath)
    except SyntaxError: return None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == variable_name:
                    try: return ast.literal_eval(node.value)
                    except (ValueError, SyntaxError): return None
        elif isinstance(node, ast.AnnAssign):
            if node.target.id == variable_name:
                try: return ast.literal_eval(node.value)
                except (ValueError, SyntaxError): return None
    return None

def resolve_function_source_path(qualified_name: str, package_root: str) -> Optional[str]:
    """Converts a fully qualified name to a file path.
    
    Args:
        qualified_name (str): The fully qualified name of the function (e.g., 'module.submodule.function')
        package_root (str): The root directory of the package
        
    Returns:
        Optional[str]: The resolved file path if found, None otherwise
    """
    parts = qualified_name.split('.')
    # For a qualified name like 'A.B.C', the module path could be 'A/B/C.py' or 'A/B/C/__init__.py'
    # We start from the full path and go backwards.
    for i in range(len(parts), 0, -1):
        module_parts = parts[:i]
        # The rest of the path is the "inner" path to the function/class
        inner_path_parts = parts[i:]
        
        potential_module_path = os.path.join(package_root, *module_parts)
        
        # Check if it's a .py file
        if os.path.isfile(potential_module_path + ".py"):
            return potential_module_path + ".py"
            
        # Check if it's a package directory
        if os.path.isdir(potential_module_path):
            init_file = os.path.join(potential_module_path, "__init__.py")
            if os.path.isfile(init_file):
                # If the qualified name was just the module, this is the file.
                # If there are more parts, the function is inside this file.
                return init_file

    # Fallback for simple cases where the qualified name directly maps
    simple_path = os.path.join(package_root, *parts)
    if os.path.isfile(simple_path + ".py"):
        return simple_path + ".py"
    init_file = os.path.join(simple_path, "__init__.py")
    if os.path.isfile(init_file):
        return init_file
        
    return None

def extract_specific_function_node(filepath: str, fqn: str) -> Optional[Tuple[ast.FunctionDef, str]]:
    """Extracts the AST node and source code of a specific function.
    
    Args:
        filepath (str): Path to the Python file containing the function
        fqn (str): Fully qualified name of the function to extract
        
    Returns:
        Optional[Tuple[ast.FunctionDef, str]]: Tuple containing the function's AST node and source code if found,
                                             None otherwise
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source_code = f.read()
        tree = ast.parse(source_code, filename=filepath)
        target_path = fqn.split('.')
        function_name, class_name = target_path[-1], target_path[-2] if len(target_path) > 1 else None
        module_name = os.path.splitext(os.path.basename(filepath))[0]
        if class_name == module_name: class_name = None
        
        nodes_to_check = tree.body
        if class_name:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    nodes_to_check = node.body
                    break
        
        for node in nodes_to_check:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name:
                return node, ast.unparse(node)
    except (IOError, SyntaxError): pass
    return None

# --- Deterministic Schema Building Logic ---

def _split_comma_separated_types(params_str: str) -> List[str]:
    """Splits a comma-separated string of types while respecting nested brackets.
    
    Args:
        params_str (str): String containing comma-separated types
        
    Returns:
        List[str]: List of individual type strings
    """
    params, balance, start = [], 0, 0
    for i, char in enumerate(params_str):
        if char in '([': balance += 1
        elif char in ')]': balance -= 1
        elif char == ',' and balance == 0:
            params.append(params_str[start:i].strip())
            start = i + 1
    params.append(params_str[start:].strip())
    return [p for p in params if p]

def is_optional_type_string(type_str: Optional[str]) -> bool:
    """Check if a type string represents an optional type.
    
    Args:
        type_str (Optional[str]): Python type string to check
        
    Returns:
        bool: True if the type is optional (Optional[T] or Union[T, None])
    """
    if not type_str:
        return False
    
    type_str = type_str.strip()
    type_str = type_str.strip("()").strip()
    
    # Check for Optional[T]
    if type_str.startswith("Optional[") and type_str.endswith("]"):
        return True
    
    # Check for Union[T, None] or Union[None, T]
    if type_str.startswith("Union[") and type_str.endswith("]"):
        inner_str = type_str[6:-1]  # Remove "Union[" and "]"
        types = _split_comma_separated_types(inner_str)
        # Check if any type is None or NoneType
        if any(t.strip().lower() in ['none', 'nonetype'] for t in types):
            return True
    
    # 3. As a final check, look for the format "(..., optional)"
    # This logic runs only if the string is NOT a standard Optional/Union.
    
    # Check if stripping parens changed the string, ensuring it was parenthesized.
    inner_parts = type_str.split(',')
    if any(part.strip().lower() == 'optional' for part in inner_parts):
        return True
        
    return False

def map_type(type_str: Optional[str]) -> Dict[str, Any]:
    """Maps a Python type string to a JSON schema object.
    
    Args:
        type_str (Optional[str]): Python type string to map
        
    Returns:
        Dict[str, Any]: JSON schema object representing the type
    """
    type_str = (type_str or "Any").strip()
    
    type_map = {"str": JSON_TYPE_STRING, "int": JSON_TYPE_INTEGER, "float": JSON_TYPE_NUMBER, "bool": JSON_TYPE_BOOLEAN, "list": JSON_TYPE_ARRAY, "dict": JSON_TYPE_OBJECT, "Any": JSON_TYPE_OBJECT}

    if type_str in type_map: return {"type": type_map[type_str]}
    
    if type_str.startswith(("Optional[", "Union[")) and type_str.endswith("]"):
        is_optional = type_str.startswith("Optional[")
        inner_str = type_str[len("Optional["):-1] if is_optional else type_str[len("Union["):-1]
        types = _split_comma_separated_types(inner_str)
        non_null_types = [t for t in types if t.lower() not in ['none', 'nonetype']]
        if non_null_types: return map_type(non_null_types[0])
        return {"type": JSON_TYPE_NULL}

    if type_str.startswith(("List[", "list[")) and type_str.endswith("]"):
        item_type = type_str[5:-1].strip() or "Any"
        return {"type": JSON_TYPE_ARRAY, "items": map_type(item_type)}
        
    if type_str.startswith(("Dict[", "dict[")) and type_str.endswith("]"):
         return {"type": JSON_TYPE_OBJECT, "properties": {}}

    return {"type": JSON_TYPE_OBJECT} # Fallback for custom classes

def parse_object_properties_from_description(description: str) -> Tuple[str, Optional[Dict[str, Any]]]:
    """Recursively parses sub-properties from a description string.
    
    Args:
        description (str): The description string to parse
        
    Returns:
        Tuple[str, Optional[Dict[str, Any]]]: Tuple containing:
            - The main description (text before property definitions)
            - A dictionary with 'properties' and 'required' keys, or None if no properties found
    """
    if not description: return "", None
    prop_regex = re.compile(r"^\s*(?:[-*]\s*)?(?P<name>[\w'\"`]+)\s*\((?P<type>.*?)\):\s*(?P<desc>.*)", re.IGNORECASE)
    def get_indent(line: str) -> int: return len(line) - len(line.lstrip(' '))

    lines = description.splitlines()
    first_prop_index = next((i for i, line in enumerate(lines) if prop_regex.match(line.strip())), -1)
            
    if first_prop_index == -1: return description, None

    main_description = "\n".join(lines[:first_prop_index]).strip()
    prop_lines = lines[first_prop_index:]
    properties, required = {}, []
    
    i = 0
    while i < len(prop_lines):
        line = prop_lines[i]
        match = prop_regex.match(line.strip())
        if not match: i += 1; continue
            
        current_indent = get_indent(line)
        data = match.groupdict()
        name = data["name"].strip().strip("'\"`")
        type_str, desc_on_line = data["type"].strip(), data["desc"].strip()

        child_lines = []
        j = i + 1
        while j < len(prop_lines) and (not prop_lines[j].strip() or get_indent(prop_lines[j]) > current_indent):
            child_lines.append(prop_lines[j])
            j += 1
        
        full_prop_description = desc_on_line + "\n" + "\n".join(child_lines)
        
        # Use the same optional detection logic as top-level parameters
        is_optional_by_type = is_optional_type_string(type_str)
        if not is_optional_by_type: 
            required.append(name)
        
        # Clean the type string by removing Optional[] wrapper or Union[..., None] patterns
        if type_str.startswith("Optional[") and type_str.endswith("]"):
            type_str_cleaned = type_str[9:-1].strip()  # Remove "Optional[" and "]"
        elif type_str.startswith("Union[") and type_str.endswith("]"):
            inner_str = type_str[6:-1]  # Remove "Union[" and "]"
            types = _split_comma_separated_types(inner_str)
            # Remove None/NoneType types and take the first remaining type
            non_null_types = [t.strip() for t in types if t.strip().lower() not in ['none', 'nonetype']]
            type_str_cleaned = non_null_types[0] if non_null_types else "Any"
        else:
            # Fallback to the old simple cleaning for backward compatibility
            type_str_cleaned = re.sub(r',?\s*optional\s*', '', type_str, flags=re.IGNORECASE).strip()
        
        prop_schema = map_type(type_str_cleaned)
        sub_main_desc, sub_props_schema = parse_object_properties_from_description(full_prop_description)
        prop_schema["description"] = sub_main_desc.strip()
        
        # Handle nested properties for both objects and arrays
        if sub_props_schema:
            if prop_schema.get("type") == JSON_TYPE_OBJECT:
                prop_schema["properties"] = sub_props_schema.get("properties", {})
                if sub_props_schema.get("required"): prop_schema["required"] = sub_props_schema.get("required")
            elif prop_schema.get("type") == JSON_TYPE_ARRAY and prop_schema.get("items", {}).get("type") == JSON_TYPE_OBJECT:
                # For List[Dict], populate the items properties
                prop_schema["items"]["properties"] = sub_props_schema.get("properties", {})
                if sub_props_schema.get("required"): prop_schema["items"]["required"] = sub_props_schema.get("required")
        
        properties[name] = prop_schema
        i = j

    result_schema = {"properties": properties}
    if required: result_schema["required"] = sorted(required)
    return main_description, result_schema

def build_initial_schema(doc: docstring_parser.Docstring, func_node: ast.FunctionDef, func_name: str) -> Dict[str, Any]:
    """Builds the entire initial JSON schema from docstring and AST node with raw descriptions.
    
    Args:
        doc (docstring_parser.Docstring): Parsed docstring object
        func_node (ast.FunctionDef): AST node of the function
        func_name (str): Name of the function
        
    Returns:
        Dict[str, Any]: Complete JSON schema for the function
    """
    params_with_defaults = set()
    num_pos_args = len(func_node.args.args)
    num_pos_defaults = len(func_node.args.defaults)
    if num_pos_defaults > 0:
        for arg in func_node.args.args[num_pos_args - num_pos_defaults:]: params_with_defaults.add(arg.arg)
    for i, kw_arg in enumerate(func_node.args.kwonlyargs):
        if i < len(func_node.args.kw_defaults) and func_node.args.kw_defaults[i] is not None: params_with_defaults.add(kw_arg.arg)

    # --- Start of fix ---
    description_parts = []
    if doc.short_description:
        description_parts.append(doc.short_description)
    if doc.long_description:
        description_parts.append(doc.long_description)
    full_description = "\n\n".join(description_parts)
    # --- End of fix ---

    schema = {
        "name": func_name,
        "description": (full_description or ""),
        "parameters": {"type": JSON_TYPE_OBJECT, "properties": {}}
    }
    required_params = []

    for param in doc.params:
        param_schema = map_type(param.type_name)
        
        # Handle different parameter types
        if param_schema.get("type") == JSON_TYPE_ARRAY and param_schema.get("items", {}).get("type") == JSON_TYPE_OBJECT:
            # Handle List[Dict] or List[Object] - parse properties for the items
            main_desc, props_schema = parse_object_properties_from_description(param.description or "")
            param_schema["description"] = main_desc.strip()
            if props_schema:
                param_schema["items"]["properties"] = props_schema.get("properties", {})
                if props_schema.get("required"): param_schema["items"]["required"] = props_schema["required"]
        elif param_schema.get("type") == JSON_TYPE_OBJECT:
            # Handle Dict/Object - parse properties directly
            main_desc, props_schema = parse_object_properties_from_description(param.description or "")
            param_schema["description"] = main_desc.strip()
            if props_schema:
                param_schema["properties"] = props_schema.get("properties", {})
                if props_schema.get("required"): param_schema["required"] = props_schema["required"]
        else:
            # Handle primitive types - just add description
            param_schema["description"] = param.description or ""
        
        schema["parameters"]["properties"][param.arg_name] = param_schema
        
        has_default = param.arg_name in params_with_defaults
        is_optional_by_docstring = param.is_optional or param.default is not None
        is_optional_by_type = is_optional_type_string(param.type_name)
        is_optional = is_optional_by_docstring or is_optional_by_type
        if not has_default and not is_optional: required_params.append(param.arg_name)

    if required_params: schema["parameters"]["required"] = sorted(required_params)
    return schema

def process_single_function(args: Tuple[str, str, str]) -> Optional[Dict[str, Any]]:
    """Processes a single function to generate its schema.
    
    Args: 
        args (Tuple[str, str, str]): Tuple containing:
            - public_name: The public name of the function
            - fqn: Fully qualified name of the function
            - package_root: Root directory of the package
            
    Returns:
        Optional[Dict[str, Any]]: The generated schema if successful, None otherwise
    """
    public_name, fqn, package_root = args

    source_file_path = resolve_function_source_path(fqn, package_root)
    if not source_file_path: return None
    
    node_info = extract_specific_function_node(source_file_path, fqn)
    if not node_info: return None
    func_node, func_src = node_info
    
    docstring_text = ast.get_docstring(func_node)
    if not docstring_text: return None
    parsed_docstring = docstring_parser.parse(docstring_text)

    schema = build_initial_schema(parsed_docstring, func_node, public_name)
    
    type_ = DOC_MODE
    if type_ not in ["concise", "medium_detail", "raw_docstring"]:
        safe_print(f"  - Using raw docstring descriptions for '{public_name}'.")
        return schema

    if type_ != "raw_docstring":
        print("Use agentic_fcspec.py to generate the schema for", public_name)

    # safe_print(f"  ✅ Success! Schema generated for '{public_name}'.")
    return schema

def generate_package_schema(package_path: str,
                            output_folder_path: str, doc_mode = DOC_MODE,
                            package_import_prefix: Optional[str] = None,
                            output_file_name: Optional[str] = None,
                            source_root_path: Optional[str] = None):
    """Generates schemas for all functions in a package.
    
    Args:
        package_path (str): Path to the Python package directory
        output_folder_path (str): Path to the output folder for schema files
        package_import_prefix (str, optional): The prefix to use for package imports. Defaults to None.
        output_file_name (str, optional): The name of the output file. Defaults to None.
        source_root_path (str, optional): The root path for resolving source files. Defaults to None.
    """
    if doc_mode not in ["concise", "medium_detail", "raw_docstring"]:
        safe_print(f"Error: Invalid DOC_MODE: {doc_mode}")
        return
    package_root = source_root_path or os.path.dirname(os.path.abspath(package_path))
    package_name = os.path.basename(package_path)
    
    # Use the provided import prefix or default to the package name
    import_name = package_import_prefix or package_name
    
    init_path = os.path.join(package_path, "__init__.py")
    if not os.path.exists(init_path):
        safe_print(f"Error: __init__.py not found in {package_path}")
        return
    
    if doc_mode == "concise":
        filename = f"concise_{package_name}.json"
    elif doc_mode == "medium_detail":
        filename = f"medium_detail_{package_name}.json"
    else: # raw_docstring
        filename = f"{package_name}.json"

    # output_file_name = f"{package_name}.json"
    # output_file = os.path.join(output_folder_path, output_file_name)
    if output_file_name:
        output_file = os.path.join(output_folder_path, output_file_name)
    else:
        output_file = os.path.join(output_folder_path, filename)

    # Save schema to simulation engine folder if it exists
    if "SimulationEngine" in os.listdir(package_path) and doc_mode != "raw_docstring":
        simulation_engine_path = os.path.join(package_path, "SimulationEngine")
        agentic_scripts_path = os.path.join(simulation_engine_path, "alternate_fcds")
        file_path = os.path.join(agentic_scripts_path, filename)

        # If file path does not exist, print error
        if not os.path.exists(file_path):
            safe_print(f"Error: {doc_mode} schema does not exist for {package_name}, use agentic_fcspec.py to generate the schema")
            return
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        # Copy file in file_path to output_file
        shutil.copy(file_path, output_file)
        safe_print(f"✅ {package_name} Schema generation complete: {output_file}\n")

    elif doc_mode == "raw_docstring":
        function_map = get_variable_from_file(init_path, "_function_map")
        if not function_map:
            safe_print(f"Error: Could not find a valid _function_map in {init_path}.")
            return

        # Adjust the FQNs with the import prefix if provided
        adjusted_function_map = {name: fqn for name, fqn in function_map.items()}
        
        function_args = [(name, fqn, package_root) for name, fqn in adjusted_function_map.items()]
        
        all_schemas = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            results = executor.map(process_single_function, function_args)
            all_schemas = [s for s in results if s]

        if all_schemas:
            all_schemas.sort(key=lambda x: x.get('name', ''))
            

            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_schemas, f, indent=2, ensure_ascii=False)
            safe_print(f"✅ {import_name} Schema generation complete: {output_file}\n")
        else:
            safe_print(f"\n❌ No schemas were generated for {import_name}.")
            return
    else:
        safe_print(f"Error: {doc_mode} schema does not exist for {package_name}, use agentic_fcspec.py to generate the schema")
    
    # Handle mutations if present
    mutations_dir = os.path.join(package_path, "mutations")
    if os.path.isdir(mutations_dir):
        for mutation_name in os.listdir(mutations_dir):
            if mutation_name == "__pycache__":
                continue
            mutation_path = os.path.join(mutations_dir, mutation_name)
            if os.path.isdir(mutation_path):
                output_folder = os.path.join(os.path.dirname(output_folder_path), "MutationSchemas", mutation_name)
                os.makedirs(output_folder, exist_ok=True)
                safe_print(f"\nProcessing mutation {package_name}.mutations.{mutation_name}...")
                generate_package_schema(
                    mutation_path, 
                    output_folder,
                    package_import_prefix=f"{package_name}.mutations.{mutation_name}",
                    output_file_name=filename,
                    source_root_path=package_root
                )


def generate_schemas_for_packages(source_folder: str, schemas_folder: str):
    """
    Generates schemas for all packages found in the source directory.

    Args:
        source_folder (Path): The directory containing the API packages.
        schemas_folder (Path): The directory where generated schemas will be saved.
    """
    # Convert String to Path objects
    source_folder = Path(source_folder)
    schemas_folder = Path(schemas_folder)

    if not source_folder.is_dir():
        raise FileNotFoundError(f"Source folder not found or is not a directory: {source_folder}")

    source_folder_abs = source_folder.resolve()
    schemas_folder_abs = schemas_folder.resolve()

    sys.path.append(str(source_folder_abs))
    os.makedirs(schemas_folder_abs, exist_ok=True)
    os.chdir(source_folder_abs)

    for package_name in os.listdir(source_folder_abs):
        package_path = source_folder_abs / package_name
        if package_path.is_dir():
            package_doc_mode = get_current_doc_mode(package_name)
            generate_package_schema(str(package_path), output_folder_path=str(schemas_folder_abs), doc_mode=package_doc_mode)

def main():
    """Sets up paths and initiates schema generation."""
    # Define source folder for the APIs
    current_file_dir = Path(__file__).parent
    content_dir = current_file_dir.parent
    source_folder = content_dir / "APIs"
    schemas_folder = content_dir / "Schemas"

    # Example usage of configuration management:
    # 
    # 1. Apply a custom configuration
    # apply_config("path/to/custom_config.json")
    #
    # 2. Generate schemas with applied configuration
    # generate_schemas_for_packages(source_folder, schemas_folder)
    #
    # 3. Rollback to original configuration
    # rollback_config()
    #
    # 4. Check configuration status
    # status = get_config_status()
    # print(f"Current config status: {status}")

    generate_schemas_for_packages(source_folder, schemas_folder)

if __name__ == "__main__":
    main()