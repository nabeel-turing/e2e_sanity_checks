from .cursorAPI import apply_structured_code_change, autofix_linting_errors_from_edit, execute_shell_command, find_code_by_semantic_query, find_file_by_fuzzy_path, generate_mermaid_visualization, get_codebase_guidelines, get_directory_listing, initiate_comprehensive_code_search, remember_codebase_fact, remove_file_from_workspace, retrieve_commit_or_pr_changes, retrieve_file_segment_with_summary, retry_failed_edit, search_contents_with_regex

_function_map = {
    'apply_structured_code_change': 'cursor.mutations.m01.cursorAPI.apply_structured_code_change',
    'autofix_linting_errors_from_edit': 'cursor.mutations.m01.cursorAPI.autofix_linting_errors_from_edit',
    'execute_shell_command': 'cursor.mutations.m01.cursorAPI.execute_shell_command',
    'find_code_by_semantic_query': 'cursor.mutations.m01.cursorAPI.find_code_by_semantic_query',
    'find_file_by_fuzzy_path': 'cursor.mutations.m01.cursorAPI.find_file_by_fuzzy_path',
    'generate_mermaid_visualization': 'cursor.mutations.m01.cursorAPI.generate_mermaid_visualization',
    'get_codebase_guidelines': 'cursor.mutations.m01.cursorAPI.get_codebase_guidelines',
    'get_directory_listing': 'cursor.mutations.m01.cursorAPI.get_directory_listing',
    'initiate_comprehensive_code_search': 'cursor.mutations.m01.cursorAPI.initiate_comprehensive_code_search',
    'remember_codebase_fact': 'cursor.mutations.m01.cursorAPI.remember_codebase_fact',
    'remove_file_from_workspace': 'cursor.mutations.m01.cursorAPI.remove_file_from_workspace',
    'retrieve_commit_or_pr_changes': 'cursor.mutations.m01.cursorAPI.retrieve_commit_or_pr_changes',
    'retrieve_file_segment_with_summary': 'cursor.mutations.m01.cursorAPI.retrieve_file_segment_with_summary',
    'retry_failed_edit': 'cursor.mutations.m01.cursorAPI.retry_failed_edit',
    'search_contents_with_regex': 'cursor.mutations.m01.cursorAPI.search_contents_with_regex',
}
