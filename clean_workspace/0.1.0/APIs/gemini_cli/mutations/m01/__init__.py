from .file_system_api import fetch_file_content, find_files_by_pattern, find_in_files_regex, get_directory_contents, perform_safe_replacement, update_or_create_file
from .memory import commit_fact_to_memory
from .read_many_files_api import fetch_multiple_files_content
from .shell_api import execute_workspace_command

_function_map = {
    'commit_fact_to_memory': 'gemini_cli.mutations.m01.memory.commit_fact_to_memory',
    'execute_workspace_command': 'gemini_cli.mutations.m01.shell_api.execute_workspace_command',
    'fetch_file_content': 'gemini_cli.mutations.m01.file_system_api.fetch_file_content',
    'fetch_multiple_files_content': 'gemini_cli.mutations.m01.read_many_files_api.fetch_multiple_files_content',
    'find_files_by_pattern': 'gemini_cli.mutations.m01.file_system_api.find_files_by_pattern',
    'find_in_files_regex': 'gemini_cli.mutations.m01.file_system_api.find_in_files_regex',
    'get_directory_contents': 'gemini_cli.mutations.m01.file_system_api.get_directory_contents',
    'perform_safe_replacement': 'gemini_cli.mutations.m01.file_system_api.perform_safe_replacement',
    'update_or_create_file': 'gemini_cli.mutations.m01.file_system_api.update_or_create_file',
}
