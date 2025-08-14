from .code_intelligence import find_all_symbol_references, find_string_or_regex_in_files, search_workspace_for_code_snippets
from .code_quality_version_control import get_code_diagnostics, get_git_diff_for_workspace
from .command_line import execute_shell_command, fetch_terminal_process_output
from .file_system import apply_code_changes_to_file, find_files_by_glob, list_directory_contents, read_file_segment
from .project_setup import fetch_project_configuration_details, generate_project_setup_plan, scaffold_new_jupyter_notebook
from .test_file_management import find_corresponding_test_or_source_file
from .vscode_environment import find_vscode_api_documentation, install_vscode_extension_by_id

_function_map = {
    'apply_code_changes_to_file': 'copilot.mutations.m01.file_system.apply_code_changes_to_file',
    'execute_shell_command': 'copilot.mutations.m01.command_line.execute_shell_command',
    'fetch_project_configuration_details': 'copilot.mutations.m01.project_setup.fetch_project_configuration_details',
    'fetch_terminal_process_output': 'copilot.mutations.m01.command_line.fetch_terminal_process_output',
    'find_all_symbol_references': 'copilot.mutations.m01.code_intelligence.find_all_symbol_references',
    'find_corresponding_test_or_source_file': 'copilot.mutations.m01.test_file_management.find_corresponding_test_or_source_file',
    'find_files_by_glob': 'copilot.mutations.m01.file_system.find_files_by_glob',
    'find_string_or_regex_in_files': 'copilot.mutations.m01.code_intelligence.find_string_or_regex_in_files',
    'find_vscode_api_documentation': 'copilot.mutations.m01.vscode_environment.find_vscode_api_documentation',
    'generate_project_setup_plan': 'copilot.mutations.m01.project_setup.generate_project_setup_plan',
    'get_code_diagnostics': 'copilot.mutations.m01.code_quality_version_control.get_code_diagnostics',
    'get_git_diff_for_workspace': 'copilot.mutations.m01.code_quality_version_control.get_git_diff_for_workspace',
    'install_vscode_extension_by_id': 'copilot.mutations.m01.vscode_environment.install_vscode_extension_by_id',
    'list_directory_contents': 'copilot.mutations.m01.file_system.list_directory_contents',
    'read_file_segment': 'copilot.mutations.m01.file_system.read_file_segment',
    'scaffold_new_jupyter_notebook': 'copilot.mutations.m01.project_setup.scaffold_new_jupyter_notebook',
    'search_workspace_for_code_snippets': 'copilot.mutations.m01.code_intelligence.search_workspace_for_code_snippets',
}
