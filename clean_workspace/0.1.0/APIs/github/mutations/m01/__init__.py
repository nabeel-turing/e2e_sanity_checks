from .issues import fetch_all_issue_comments, find_issues_and_prs, find_repository_issues_by_filter, modify_existing_issue, open_new_github_issue, post_comment_to_issue, retrieve_issue_details
from .pull_requests import check_pr_combined_status, execute_pull_request_merge, fetch_pr_review_discussions, fetch_pull_request_data, initiate_pull_request, list_changed_files_in_pr, modify_pull_request_attributes, post_pr_line_comment, query_repository_pull_requests, retrieve_all_pr_reviews, submit_pull_request_feedback, sync_pr_branch_with_base
from .repositories import commit_file_change, commit_multiple_files, create_repository_fork, discover_repositories_by_query, enumerate_repo_branches, establish_new_branch, fetch_repository_path_content, find_code_in_repositories, get_commit_history, initialize_new_repository, retrieve_single_commit_data
from .users import fetch_current_user_profile, find_github_users

_function_map = {
    'check_pr_combined_status': 'github.mutations.m01.pull_requests.check_pr_combined_status',
    'commit_file_change': 'github.mutations.m01.repositories.commit_file_change',
    'commit_multiple_files': 'github.mutations.m01.repositories.commit_multiple_files',
    'create_repository_fork': 'github.mutations.m01.repositories.create_repository_fork',
    'discover_repositories_by_query': 'github.mutations.m01.repositories.discover_repositories_by_query',
    'enumerate_repo_branches': 'github.mutations.m01.repositories.enumerate_repo_branches',
    'establish_new_branch': 'github.mutations.m01.repositories.establish_new_branch',
    'execute_pull_request_merge': 'github.mutations.m01.pull_requests.execute_pull_request_merge',
    'fetch_all_issue_comments': 'github.mutations.m01.issues.fetch_all_issue_comments',
    'fetch_current_user_profile': 'github.mutations.m01.users.fetch_current_user_profile',
    'fetch_pr_review_discussions': 'github.mutations.m01.pull_requests.fetch_pr_review_discussions',
    'fetch_pull_request_data': 'github.mutations.m01.pull_requests.fetch_pull_request_data',
    'fetch_repository_path_content': 'github.mutations.m01.repositories.fetch_repository_path_content',
    'find_code_in_repositories': 'github.mutations.m01.repositories.find_code_in_repositories',
    'find_github_users': 'github.mutations.m01.users.find_github_users',
    'find_issues_and_prs': 'github.mutations.m01.issues.find_issues_and_prs',
    'find_repository_issues_by_filter': 'github.mutations.m01.issues.find_repository_issues_by_filter',
    'get_commit_history': 'github.mutations.m01.repositories.get_commit_history',
    'initialize_new_repository': 'github.mutations.m01.repositories.initialize_new_repository',
    'initiate_pull_request': 'github.mutations.m01.pull_requests.initiate_pull_request',
    'list_changed_files_in_pr': 'github.mutations.m01.pull_requests.list_changed_files_in_pr',
    'modify_existing_issue': 'github.mutations.m01.issues.modify_existing_issue',
    'modify_pull_request_attributes': 'github.mutations.m01.pull_requests.modify_pull_request_attributes',
    'open_new_github_issue': 'github.mutations.m01.issues.open_new_github_issue',
    'post_comment_to_issue': 'github.mutations.m01.issues.post_comment_to_issue',
    'post_pr_line_comment': 'github.mutations.m01.pull_requests.post_pr_line_comment',
    'query_repository_pull_requests': 'github.mutations.m01.pull_requests.query_repository_pull_requests',
    'retrieve_all_pr_reviews': 'github.mutations.m01.pull_requests.retrieve_all_pr_reviews',
    'retrieve_issue_details': 'github.mutations.m01.issues.retrieve_issue_details',
    'retrieve_single_commit_data': 'github.mutations.m01.repositories.retrieve_single_commit_data',
    'submit_pull_request_feedback': 'github.mutations.m01.pull_requests.submit_pull_request_feedback',
    'sync_pr_branch_with_base': 'github.mutations.m01.pull_requests.sync_pr_branch_with_base',
}
