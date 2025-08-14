import subprocess
import sys
import os
from typing import Tuple, Dict, Union
from .SimulationEngine.custom_errors import FileWriteError, ValidationError, CodeExecutionError, FileNotFoundError

def write_to_file(file_path: str, content: Union[str, bytes]) -> Tuple[bool, str]:
    """Writes content to a specified file.

    This function automatically detects the content type and opens the file
    in the appropriate mode.
    - If 'content' is a string, it writes in text mode ('w').
    - If 'content' is bytes, it writes in binary mode ('wb').
    This function will overwrite the file if it already exists.

    Args:
        file_path (str): The full path to the file to be written.
        content (Union[str, bytes]): The content to write to the file.

    Returns:
        Tuple[bool, str]: A tuple containing:
            - bool: True if the write was successful, False otherwise.
            - str: A message indicating success or the error encountered.
        
    Raises:
        ValidationError: If the file_path is not a string, content is not a string or bytes,
                       or if either parameter is empty.
        TypeError: If the content is not a string or bytes.
        FileWriteError: If the file writing fails.
    """
    # Input validation
    if not isinstance(file_path, str):
        raise ValidationError(f"file_path must be a string got type {type(file_path)}.")
    if not isinstance(content, (str, bytes)):
        raise ValidationError(f"content must be a string or bytes got type {type(content)}.")
    if not file_path.strip():
        raise ValidationError("file_path cannot be empty.")
    # End of input validation
    
    try:
        if isinstance(content, str):
            # If content is a string, open in text write mode.
            mode = 'w'
            # It's good practice to specify encoding for text files.
            encoding = 'utf-8'
        else:
            # If content is bytes, open in binary write mode.
            mode = 'wb'
            # Encoding is not used for binary mode.
            encoding = None

        with open(file_path, mode, encoding=encoding) as f:
            f.write(content)
        return True, f"Successfully wrote {len(content)} bytes/chars to {file_path}"
    except Exception as e:
        raise FileWriteError(f"Error writing to file {file_path}: {e}")


def execute_script(script_path: str) -> Dict[str, Union[int, str]]:
    """Executes a Python script from a file and captures its output.

    Args:
        script_path (str): The path to the Python script to execute.

    Returns:
        Dict[str, Union[int, str]]: A dictionary containing:
            - exit_code (int): The exit status of the command.
            - stdout (str): The standard output of the command.
            - stderr (str): The standard error of the command.

    Raises:
        ValidationError: If the script_path is not a string or is empty.
        FileNotFoundError: If the script is not found.
        CodeExecutionError: If an unexpected error occurs while executing the script.
    """
    # Input validation
    if not isinstance(script_path, str):
        raise ValidationError(f"script_path must be a string got type {type(script_path)}.")
    if not script_path.strip():
        raise ValidationError(f"script_path cannot be empty.")
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"The script at {script_path} was not found.")
    # Validate that the script is a Python script
    if not script_path.endswith('.py'):
        raise ValidationError(f"The script at {script_path} is not a Python script.")
    # End of input validation

    try:
        # Use the actual Python executable from the environment instead of sys.executable which might point to Cursor
        import subprocess as sp
        python_executable = sp.run(['which', 'python'], capture_output=True, text=True).stdout.strip()
        if not python_executable:
            # Fallback to python3 if python is not found
            python_executable = sp.run(['which', 'python3'], capture_output=True, text=True).stdout.strip()
        
        if not python_executable:
            # Final fallback to sys.executable
            python_executable = sys.executable
        
        command = [python_executable, script_path]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False
        )

        return {
                "exit_code": result.returncode,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip()
            }
    except FileNotFoundError:
        raise FileNotFoundError(f"The script at {script_path} was not found.")
    except Exception as e:
        raise CodeExecutionError(f"An unexpected error occurred while executing the script: {e}")


def execute_code(code_string: str) -> Dict[str, Union[int, str]]:
    """Executes a string of Python code and captures its output.

    Args:
        code_string (str): A string containing the Python code to execute.

    Returns:
        Dict[str, Union[int, str]]: A dictionary containing:
            - exit_code (int): The exit status of the command.
            - stdout (str): The standard output of the command.
            - stderr (str): The standard error of the command.

    Raises:
        ValidationError: If the code_string is not a string or is empty.
        CodeExecutionError: If an unexpected error occurs while executing the code.
    """
    # Input validation
    if not isinstance(code_string, str):
        raise ValidationError(f"code_string must be a string got type {type(code_string)}.")
    if not code_string.strip():
        raise ValidationError(f"code_string cannot be empty.")
    # End of input validation

    try:
        # Use the actual Python executable from the environment instead of sys.executable which might point to Cursor
        import subprocess as sp
        python_executable = sp.run(['which', 'python'], capture_output=True, text=True).stdout.strip()
        if not python_executable:
            # Fallback to python3 if python is not found
            python_executable = sp.run(['which', 'python3'], capture_output=True, text=True).stdout.strip()
        
        if not python_executable:
            # Final fallback to sys.executable
            python_executable = sys.executable
        
        command = [python_executable, "-c", code_string]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False
        )
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip()
        }
    except Exception as e:
        raise CodeExecutionError(f"An unexpected error occurred while executing the code: {e}")
