import base64
import re
import hashlib
import binascii # For base64 decoding errors
import shlex

from typing import Optional, Dict, Any, List, Union
from datetime import datetime, timezone
from collections import deque

from github.SimulationEngine.db import DB
from github.SimulationEngine import utils
from github.SimulationEngine import custom_errors
from github.SimulationEngine import models

# Default number of items per page if not specified by the client.
DEFAULT_PER_PAGE = 30


def search_repositories(query: str, sort: Optional[str] = None, order: str = "desc", page: int = 1, per_page: int = 30) -> Dict[str, Any]:
    """Search for GitHub repositories.
    
    Find repositories via various criteria. This method returns up to 100 results per page.
    The query can contain any combination of search keywords and qualifiers to narrow down the results.

    When no sort is specified, results are sorted by best match.

    Args:
        query (str): The search query string. Can contain any combination of search keywords and qualifiers.
            For example: `q=tetris+language:assembly+fork:true+stars:>=100`.
            Supported qualifiers:
            - `in:name,description`
            - `size:>=N`, `size:N..M`
            - `forks:N`, `stars:N`, `watchers:N` (with ranges)
            - `user:USERNAME`, `org:USERNAME`
            - `language:LANGUAGE`
            - `created:DATE`, `pushed:DATE`, `updated:DATE` (with ranges)
            - `is:public`, `is:private`, `is:archived`, `is:template`
            - `fork:true`, `fork:only`
        sort (Optional[str]): The field to sort by. Can be `stars`, `forks`, `updated`. Defaults to `None`.
        order (str): The direction to sort. Can be `asc` or `desc`. Defaults to `desc`.
        page (int): Page number of the results to fetch. Defaults to 1.
        per_page (int): The number of results per page (max 100). Defaults to 30.

    Returns:
        Dict[str, Any]: A dictionary containing a `search_results` object with the repository search results.
            The `search_results` object has the following keys:
            - total_count (int): The total number of repositories matching the search query.
            - incomplete_results (bool): Indicates whether the search timed out before all results could be gathered.
            - items (List[Dict[str, Any]]): A list of repository objects. Each repository object has the following structure:
                - id (int): The unique identifier for the repository.
                - node_id (str): A global identifier for the repository.
                - name (str): The name of the repository.
                - full_name (str): The full name of the repository, in 'owner_login/repository_name' format.
                - private (bool): Indicates whether the repository is private.
                - owner (Dict[str, Any]): An object describing the owner of the repository, containing:
                    - login (str): The owner's username.
                    - id (int): The unique identifier for the owner.
                    - node_id (str): A global identifier for the owner.
                    - type (str): The type of owner (e.g., 'User', 'Organization').
                    - site_admin (bool): Indicates if the owner is a site administrator.
                - description (Optional[str]): A description of the repository. Null if not provided.
                - fork (bool): Indicates whether the repository is a fork of another repository.
                - created_at (str): The timestamp (ISO 8601 format) for when the repository was created.
                - updated_at (str): The timestamp (ISO 8601 format) for when the repository was last updated.
                - pushed_at (str): The timestamp (ISO 8601 format) for when the repository was last pushed to.
                - stargazers_count (int): The number of users who have starred the repository.
                - watchers_count (int): The number of users watching the repository.
                - forks_count (int): The number of times the repository has been forked.
                - open_issues_count (int): The number of open issues in the repository.
                - language (Optional[str]): The primary programming language of the repository. Null if not detected.
                - score (float): The relevance score assigned to the repository by the search algorithm.

    Raises:
        InvalidInputError: If the query is invalid or pagination parameters are incorrect.
    """
    if not query or not isinstance(query, str):
        raise custom_errors.InvalidInputError("Search query must be a non-empty string.")

    # --- Pagination Validation ---
    if not isinstance(page, int) or page < 1:
        raise custom_errors.InvalidInputError("Page must be a positive integer.")
    if not isinstance(per_page, int) or not 1 <= per_page <= 100:
        raise custom_errors.InvalidInputError("Per_page must be a positive integer between 1 and 100.")

    # --- Query Parsing ---
    try:
        parts = shlex.split(query)
    except ValueError:
        raise custom_errors.InvalidInputError("Invalid query syntax: Mismatched quotes.")

    search_terms = []
    qualifiers = {}
    qualifier_pattern = re.compile(r'([a-zA-Z_]+):(.*)')

    for part in parts:
        match = qualifier_pattern.match(part)
        if match:
            key, value = match.groups()
            qualifiers[key.lower()] = value
        else:
            search_terms.append(part.lower())

    # --- Data Fetching & Filtering ---
    all_repos = DB.get("Repositories", [])
    filtered_repos = []

    for repo in all_repos:
        match = True
        for key, value in qualifiers.items():
            if not utils.check_repo_qualifier(repo, key, value):
                match = False
                break
        if not match:
            continue
        
        if search_terms:
            search_in = qualifiers.get('in', 'name,description').split(',')
            term_match = False
            for term in search_terms:
                # Term must be found in at least one of the specified fields
                if 'name' in search_in and term in repo.get('name', '').lower():
                    term_match = True
                    break
                if 'description' in search_in and repo.get('description') and term in repo['description'].lower():
                    term_match = True
                    break
            if not term_match:
                continue
        
        filtered_repos.append(repo)

    # --- Sorting Logic ---
    reverse_order = (order != 'asc')
    if sort:
        if sort not in ['stars', 'forks', 'updated']:
            raise custom_errors.InvalidInputError("Invalid sort option. Use 'stars', 'forks', or 'updated'.")
        
        sort_key_map = {
            'stars': 'stargazers_count',
            'forks': 'forks_count',
            'updated': 'updated_at'
        }
        sort_key = sort_key_map[sort]
        
        # Handle date sorting
        if sort_key.endswith('_at'):
            filtered_repos.sort(key=lambda r: utils.parse_datetime_data(r.get(sort_key)), reverse=reverse_order)
        else:
            filtered_repos.sort(key=lambda r: r.get(sort_key, 0), reverse=reverse_order)
    else:
        # Default sort by score (best match)
        filtered_repos.sort(key=lambda r: r.get('score', 0.0), reverse=True)

    # --- Pagination ---
    total_count = len(filtered_repos)
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    paginated_repos = filtered_repos[start_index:end_index]

    # --- Formatting Output ---
    formatted_items = [utils.format_repository_response(repo) for repo in paginated_repos]

    return {
        "search_results": {
            "total_count": total_count,
            "incomplete_results": False,
            "items": formatted_items
        }
    }

def list_commits(owner: str, repo: str, sha: Optional[str] = None, path: Optional[str] = None, page: Optional[int] = None, per_page: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get a list of commits of a branch in a repository.

    This function gets a list of commits of a branch in a repository.
    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        sha (Optional[str]): The commit SHA, branch name, or tag name to list commits from.
        path (Optional[str]): Only commits containing this file path will be returned.
        page (Optional[int]): Page number of the results to fetch for pagination.
        per_page (Optional[int]): The number of results per page for pagination.

    Returns:
        List[Dict[str, Any]]: A list of commit objects. Each dictionary in this list
            represents a commit and has the following keys:
            sha (str): The SHA (Secure Hash Algorithm) identifier of the commit.
            node_id (str): The global node ID of the commit.
            commit (Dict[str, Any]): Core commit information. Contains the following fields:
                author (Dict[str, Any]): Details of the original author of the commit
                    (not necessarily the committer). Contains the following fields:
                    name (str): The name of the git author.
                    email (str): The email of the git author.
                    date (str): The timestamp (ISO 8601 format) when this commit
                        was authored.
                committer (Dict[str, Any]): Details of the user who committed the
                    changes. Contains the following fields:
                    name (str): The name of the git committer.
                    email (str): The email of the git committer.
                    date (str): The timestamp (ISO 8601 format) when this commit
                        was committed.
                message (str): The commit message.
                tree (Dict[str, Any]): Details of the tree object associated with this
                    commit. Contains the following fields:
                    sha (str): The SHA of the tree object.
                comment_count (int): The number of comments on the commit.
            author (Optional[Dict[str, Any]]): The GitHub user account that authored the
                commit, if linked to a GitHub account. This can be null if the
                author is not a GitHub user or if the commit author information is
                forged. Contains the following fields:
                login (str): The GitHub username of the author.
                id (int): The unique GitHub ID of the author.
                node_id (str): The global node ID of the author.
                gravatar_id (str): The Gravatar ID for the user (note: this is an
                    ID, not a URL).
                type (str): The type of GitHub account (e.g., 'User', 'Bot').
                site_admin (bool): Indicates if the user is a site administrator
                    on GitHub.
            committer (Optional[Dict[str, Any]]): The GitHub user account that committed
                the changes, if linked to a GitHub account. This can be null if the
                committer is not a GitHub user or if the committer information is
                forged. Contains the following fields:
                login (str): The GitHub username of the committer.
                id (int): The unique GitHub ID of the committer.
                node_id (str): The global node ID of the committer.
                gravatar_id (str): The Gravatar ID for the user (note: this is an
                    ID, not a URL).
                type (str): The type of GitHub account (e.g., 'User', 'Bot').
                site_admin (bool): Indicates if the user is a site administrator
                    on GitHub.
            parents (List[Dict[str, Any]]): A list of parent commit objects. Each parent
                object (a dictionary) in this list contains:
                sha (str): The SHA of a parent commit.
                node_id (str): The global node ID of the parent commit.

    Raises:
        NotFoundError: If the repository doesn't exist, specified SHA/branch/tag isn't found, 
                       path doesn't exist, default branch is not configured, or the starting
                       commit SHA cannot be determined.
    """
    full_repo_name = f"{owner}/{repo}"
    repo_data = utils._find_repository_raw(DB, repo_full_name=full_repo_name)

    if not repo_data:
        raise custom_errors.NotFoundError(f"Repository '{full_repo_name}' not found.")

    repo_id = repo_data["id"]
    default_branch_name = repo_data.get("default_branch")

    start_sha = None
    ref_name_for_error = sha # Store original sha/branch/tag name for error messages

    if sha:
        branches_table = utils._get_table(DB, "Branches")
        found_branch = next(
            (b for b in branches_table if b.get("repository_id") == repo_id and b.get("name") == sha),
            None
        )
        if found_branch:
            start_sha = found_branch.get("commit", {}).get("sha")
            ref_name_for_error = sha # It was a branch name
        else:
            # Not a branch name, or branch not found. Assume sha is a commit SHA.
            start_sha = sha
    else: # No sha provided, use default branch
        if not default_branch_name:
            # This case should ideally not happen for a valid repo, but good to check.
            raise custom_errors.NotFoundError(f"Default branch not configured for repository '{full_repo_name}'.")

        ref_name_for_error = default_branch_name # For error messages
        branches_table = utils._get_table(DB, "Branches")
        default_branch_obj = next(
            (b for b in branches_table if b.get("repository_id") == repo_id and b.get("name") == default_branch_name),
            None
        )
        if not default_branch_obj:
            raise custom_errors.NotFoundError(f"Default branch '{default_branch_name}' not found in repository '{full_repo_name}'.")
        start_sha = default_branch_obj.get("commit", {}).get("sha")

    if not start_sha: # Should be caught by specific errors above, but as a safeguard
        raise custom_errors.NotFoundError(f"Could not determine starting commit SHA for '{ref_name_for_error}' in repository '{full_repo_name}'.")

    all_repo_commits_raw = [c for c in utils._get_table(DB, "Commits") if c.get("repository_id") == repo_id]
    commits_by_sha = {c["sha"]: c for c in all_repo_commits_raw}

    if start_sha not in commits_by_sha:
        raise custom_errors.NotFoundError(f"Commit SHA '{start_sha}' (derived from '{ref_name_for_error}') not found in repository '{full_repo_name}'.")

    # Traverse commit history from start_sha
    collected_commits_data = []
    queue = deque([start_sha])
    visited_shas = set()

    while queue:
        current_commit_sha = queue.popleft()
        if current_commit_sha in visited_shas:
            continue

        commit_data = commits_by_sha.get(current_commit_sha)
        if not commit_data: # Should not happen if DB is consistent and start_sha was valid
            continue

        visited_shas.add(current_commit_sha)
        collected_commits_data.append(commit_data)

        for parent in commit_data.get("parents", []):
            parent_sha = parent.get("sha")
            if parent_sha and parent_sha not in visited_shas: # Add to queue only if not visited yet
                 # Check if parent_sha actually exists in commits_by_sha before adding to queue
                 # This handles cases where parent might be outside the known commits for this repo (e.g. shallow clone)
                 # For this simulation, assume if parent_sha is listed, it's valid or traversal stops there.
                if parent_sha in commits_by_sha:
                    queue.append(parent_sha)


    # Sort commits by committer date (descending)
    # Assuming date is stored as ISO string, string comparison works.
    collected_commits_data.sort(key=lambda c: c.get("commit", {}).get("committer", {}).get("date", ""), reverse=True)

    # Filter by path if provided
    if path:
        path_filtered_commits = []
        for commit_data in collected_commits_data:
            commit_files = commit_data.get("files")
            if isinstance(commit_files, list): # Ensure 'files' is a list
                for file_change in commit_files:
                    if file_change.get("filename") == path:
                        path_filtered_commits.append(commit_data)
                        break
        processed_commits = path_filtered_commits
        # Per docstring: "NotFoundError: ... or path does not exist."
        # This is ambiguous. GitHub API typically returns [] if path filter yields no results.
        # If path parameter itself was invalid (e.g. for /contents/ API), it's a 404.
        # Here, if path filter results in empty list, we'll return empty list.
        # A strict interpretation of "path does not exist" could mean if no commit *ever* touched this path.
        # This is complex to check efficiently. Current behavior: if filter is empty, result is empty.
    else:
        processed_commits = collected_commits_data

    # Pagination
    final_commits_to_format: List[Dict[str, Any]]
    if page is not None:
        current_page = page if page > 0 else 1
        items_per_page = per_page if per_page is not None and per_page > 0 else 30

        start_index = (current_page - 1) * items_per_page
        end_index = start_index + items_per_page
        final_commits_to_format = processed_commits[start_index:end_index]
    elif per_page is not None and per_page > 0: # Only per_page is given
        final_commits_to_format = processed_commits[:per_page]
    else: # No pagination
        final_commits_to_format = processed_commits

    # Format output
    results = []
    for commit_data_raw in final_commits_to_format:

        def format_git_actor(actor_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
            if not actor_data: return {"name": None, "email": None, "date": None} # Should not happen for valid commit
            # Assuming date is already an ISO 8601 string in DB
            return {
                "name": actor_data.get("name"),
                "email": actor_data.get("email"),
                "date": actor_data.get("date"),
            }

        core_commit_data_raw = commit_data_raw.get("commit", {})
        core_commit = {
            "author": format_git_actor(core_commit_data_raw.get("author")),
            "committer": format_git_actor(core_commit_data_raw.get("committer")),
            "message": core_commit_data_raw.get("message"),
            "tree": {
                "sha": core_commit_data_raw.get("tree", {}).get("sha"),
            },
            "comment_count": core_commit_data_raw.get("comment_count", 0),
        }

        def format_github_user(user_data_raw: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
            if not user_data_raw:
                return None
            return {
                "login": user_data_raw.get("login"),
                "id": user_data_raw.get("id"),
                "node_id": user_data_raw.get("node_id"),
                "gravatar_id": user_data_raw.get("gravatar_id", ""), # BaseUser in DB schema lacks gravatar_id
                "type": user_data_raw.get("type"),
                "site_admin": user_data_raw.get("site_admin", False),
            }

        parents_data_raw = commit_data_raw.get("parents", [])
        parents = [
            {
                "sha": p.get("sha"),
                "node_id": p.get("node_id"),
            }
            for p in parents_data_raw
        ]

        commit_item = {
            "sha": commit_data_raw.get("sha"),
            "node_id": commit_data_raw.get("node_id"),
            "commit": core_commit,
            "author": format_github_user(commit_data_raw.get("author")),
            "committer": format_github_user(commit_data_raw.get("committer")),
            "parents": parents,
        }
        results.append(commit_item)

    return results

def get_commit(owner: str, repo: str, sha: str, page: Optional[int] = None, per_page: Optional[int] = None) -> Dict[str, Any]:
    """Get details for a commit from a repository.

    This function gets details for a commit from a repository. The `page` and
    `per_page` parameters can be used to paginate the list of files affected
    by the commit, which is part of the returned details.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        sha (str): The SHA of the commit to retrieve.
        page (Optional[int]): Page number for paginating the list of files affected by the commit. Defaults to None.
        per_page (Optional[int]): The number of files to return per page when paginating. Defaults to None.

    Returns:
        Dict[str, Any]: A dictionary containing details for a specific commit. It includes the following keys:
            sha (str): The SHA of the commit.
            node_id (str): The global node ID of the commit.
            commit (Dict[str, Any]): The raw commit details, containing:
                author (Dict[str, Any]): Details of the original author of the commit:
                    name (str): Author's name.
                    email (str): Author's email address.
                    date (str): Timestamp of when the commit was authored (ISO 8601 format).
                committer (Dict[str, Any]): Details of the person who committed the changes:
                    name (str): Committer's name.
                    email (str): Committer's email address.
                    date (str): Timestamp of when the commit was made (ISO 8601 format).
                message (str): The commit message.
                tree (Dict[str, Any]): Information about the commit's tree:
                    sha (str): The SHA of the tree object.
            author (Optional[Dict[str, Any]]): The GitHub user who authored the commit (if linked to a GitHub account).
                If present, contains:
                    login (str): The GitHub login of the author.
                    id (int): The GitHub ID of the author.
            committer (Optional[Dict[str, Any]]): The GitHub user who committed the changes (if linked to a GitHub account).
                If present, contains:
                    login (str): The GitHub login of the committer.
                    id (int): The GitHub ID of the committer.
            parents (List[Dict[str, Any]]): A list of parent commit objects. Each object in the list contains:
                sha (str): The SHA of the parent commit.
            stats (Optional[Dict[str, Any]]): Commit statistics. If present, contains:
                total (int): Total number of changes (additions + deletions).
                additions (int): Number of lines added.
                deletions (int): Number of lines deleted.
            files (Optional[List[Dict[str, Any]]]): A list of files affected by this commit. This list may be
                paginated if 'page' and 'per_page' parameters are used in the request. Each file
                object in the list contains:
                sha (str): Blob SHA of the file.
                filename (str): Name and path of the file.
                status (str): Status of the file in this commit (e.g., 'added', 'modified', 'removed', 'renamed').
                additions (int): Number of additions made to this file.
                deletions (int): Number of deletions made from this file.
                changes (int): Total number of changes in this file.
                patch (Optional[str]): The patch data (diff) for the file, detailing the changes.

    Raises:
        NotFoundError: If the repository or commit SHA does not exist.
    """

    # Local helper for date formatting, as per docstring requirements
    def format_datetime_to_iso_z(dt_val: Any) -> Optional[str]:
        if isinstance(dt_val, datetime):
            # If naive, assume UTC. Then convert to UTC and format.
            if dt_val.tzinfo is None or dt_val.tzinfo.utcoffset(dt_val) is None:
                dt_val_utc = dt_val.replace(tzinfo=timezone.utc)
            else:
                dt_val_utc = dt_val.astimezone(timezone.utc)
            return dt_val_utc.isoformat().replace("+00:00", "Z")
        elif isinstance(dt_val, str):
            # Assuming string is already in a valid ISO 8601 format.
            # Further validation/transformation could be added if DB strings are inconsistent.
            return dt_val
        return None

    # Find the repository
    repo_full_name = f"{owner}/{repo}"
    repo_data = utils._find_repository_raw(DB, repo_full_name=repo_full_name)
    if not repo_data:
        raise custom_errors.NotFoundError(f"Repository '{repo_full_name}' not found.")

    repo_id = repo_data["id"]

    # Find the commit
    commits_table = utils._get_table(DB, "Commits")
    commit_data_from_db = None
    for c_dict in commits_table:
        # Ensure 'repository_id' exists in commit entry 'c_dict'
        if c_dict.get("repository_id") == repo_id and c_dict.get("sha") == sha:
            commit_data_from_db = c_dict
            break

    if not commit_data_from_db:
        raise custom_errors.NotFoundError(f"Commit with SHA '{sha}' not found in repository '{repo_full_name}'.")

    # Prepare files list with pagination
    files_output: Optional[List[Dict[str, Any]]] = None
    raw_files_list = commit_data_from_db.get("files")

    if raw_files_list is not None and isinstance(raw_files_list, list):
        # Ensure all items in raw_files_list are dictionaries (shallow copy)
        processed_files = [dict(file_item) for file_item in raw_files_list if isinstance(file_item, dict)]

        if page is not None:
            current_page = int(page)
            if current_page < 1:
                current_page = 1

            items_per_page = 30  # Default per_page
            if per_page is not None:
                current_per_page = int(per_page)
                if current_per_page > 0:
                    items_per_page = min(current_per_page, 100) # Cap per_page (GitHub common practice)

            start_index = (current_page - 1) * items_per_page
            end_index = start_index + items_per_page
            files_output = processed_files[start_index:end_index]
        else:
            # If page is None, per_page is ignored, return all files
            files_output = processed_files

    # Format commit sub-dictionary
    raw_commit_details = commit_data_from_db.get("commit", {}) # Default to empty dict if "commit" key is missing

    commit_author_details = raw_commit_details.get("author", {})
    commit_committer_details = raw_commit_details.get("committer", {})
    commit_tree_details = raw_commit_details.get("tree", {})

    formatted_commit_details = {
        "author": {
            "name": commit_author_details.get("name"),
            "email": commit_author_details.get("email"),
            "date": format_datetime_to_iso_z(commit_author_details.get("date")),
        },
        "committer": {
            "name": commit_committer_details.get("name"),
            "email": commit_committer_details.get("email"),
            "date": format_datetime_to_iso_z(commit_committer_details.get("date")),
        },
        "message": raw_commit_details.get("message"),
        "tree": {
            "sha": commit_tree_details.get("sha")
        }
    }

    # Format author (GitHub user)
    author_user_data = commit_data_from_db.get("author")
    formatted_author_user = None
    if isinstance(author_user_data, dict):
        formatted_author_user = {
            "login": author_user_data.get("login"),
            "id": author_user_data.get("id")
        }

    # Format committer (GitHub user)
    committer_user_data = commit_data_from_db.get("committer")
    formatted_committer_user = None
    if isinstance(committer_user_data, dict):
        formatted_committer_user = {
            "login": committer_user_data.get("login"),
            "id": committer_user_data.get("id")
        }

    # Format parents
    raw_parents = commit_data_from_db.get("parents", [])
    formatted_parents = []
    if isinstance(raw_parents, list):
        for p_item in raw_parents:
            if isinstance(p_item, dict): # Ensure parent item is a dictionary
                formatted_parents.append({"sha": p_item.get("sha")})


    # Prepare stats
    stats_data = commit_data_from_db.get("stats")
    formatted_stats = None
    if isinstance(stats_data, dict):
        formatted_stats = {
            "total": stats_data.get("total"),
            "additions": stats_data.get("additions"),
            "deletions": stats_data.get("deletions"),
        }

    # Assemble the final result
    result = {
        "sha": commit_data_from_db.get("sha"),
        "node_id": commit_data_from_db.get("node_id"),
        "commit": formatted_commit_details,
        "author": formatted_author_user,
        "committer": formatted_committer_user,
        "parents": formatted_parents,
        "stats": formatted_stats,
        "files": files_output
    }

    return result

def create_branch(owner: str, repo: str, branch: str, sha: str) -> Dict[str, Any]:
    """Create a new branch.

        This function establishes a new branch of development within the repository.

    Args:
        owner (str): The account owner of the repository.
        repo (str): The name of the repository.
        branch (str): The name of the new branch to create.
        sha (str): The SHA of the commit from which the new branch will be created.

    Returns:
        Dict[str, Any]: A dictionary containing branch creation details with the following keys:
            ref (str): The full Git ref (e.g., 'refs/heads/new-branch').
            node_id (str): The global node ID for the ref.
            object (Dict[str, Any]): Details of the Git object this ref points to. This dictionary contains the following keys:
                type (str): The type of the Git object, usually 'commit'.
                sha (str): The SHA of the commit the new branch points to.

    Raises:
        NotFoundError: If the repository or the source 'sha' does not exist.
        UnprocessableEntityError: If the branch already exists, if the 'sha' is not a valid commit SHA,
                                  or if the branch name is invalid.
    """
    repo_full_name = f"{owner}/{repo}"
    repository_data = utils._find_repository_raw(DB, repo_full_name=repo_full_name)
    if not repository_data:
        raise custom_errors.NotFoundError(f"Repository '{repo_full_name}' not found.")

    repo_id = repository_data["id"]
    
    # Validate SHA format
    if not re.fullmatch(models.SHA_PATTERN, sha):
        raise custom_errors.UnprocessableEntityError(f"SHA '{sha}' is not a valid SHA format.")

    # Validate that the SHA corresponds to an existing commit in this repository
    commits_table = utils._get_table(DB, "Commits")
    source_commit_exists = False
    for c_commit in commits_table:
        if c_commit.get("sha") == sha and c_commit.get("repository_id") == repo_id:
            source_commit_exists = True
            break

    if not source_commit_exists:
        raise custom_errors.NotFoundError(f"Commit with SHA '{sha}' not found in repository '{repo_full_name}'.")

    # Validate branch name format
    if not branch: # Check for empty branch name
        raise custom_errors.UnprocessableEntityError("Branch name cannot be empty.")

    # Check if branch already exists in this repository
    branches_table = utils._get_table(DB, "Branches")
    for b_existing in branches_table:
        if b_existing.get("name") == branch and b_existing.get("repository_id") == repo_id:
            raise custom_errors.UnprocessableEntityError(f"Branch '{branch}' already exists in repository '{repo_full_name}'.")

    # Create the new branch data.
    new_branch_data = {
        "name": branch,
        "commit": {
            "sha": sha
        },
        "protected": False,
        "repository_id": repo_id
    }
    branches_table.append(new_branch_data)

    # Prepare the response object as per the docstring
    full_ref = f"refs/heads/{branch}"
    node_id_source_str = f"ref:{repo_full_name}:{full_ref}"
    node_id = base64.b64encode(node_id_source_str.encode('utf-8')).decode('utf-8')

    response = {
        "ref": full_ref,
        "node_id": node_id,
        "object": {
            "type": "commit",
            "sha": sha
        }
    }

    return response

def create_or_update_file(owner: str, repo: str, path: str, message: str, content: str, branch: Optional[str] = None, sha: Optional[str] = None) -> Dict[str, Any]:
    """Create or update a single file in a repository.

    This function creates a new file or updates an existing file at a specified
    path within a given repository. It requires the repository owner's identifier,
    the repository name, the file's path, a commit message, and the file's
    content. Optional parameters include the branch name and, for file updates,
    the SHA of the existing file blob to ensure the correct file version is modified.

    Args:
        owner (str): The account owner of the repository (e.g., username or organization name).
        repo (str): The name of the repository.
        path (str): The path to the file in the repository.
        message (str): The commit message.
        content (str): The new file content, base64 encoded.
        branch (Optional[str]): The branch name. If not provided, the operation
            typically targets the repository's default branch. Defaults to None.
        sha (Optional[str]): The blob SHA of the file being replaced. This is
            required if updating an existing file and is used to prevent conflicts
            by ensuring the file has not changed since the SHA was obtained.
            Defaults to None.

    Returns:
        Dict[str, Any]: A dictionary containing details about the commit and the file.
            It has the following top-level keys:
            content (Dict[str, Any]): Details of the created/updated file. This dictionary contains:
                name (str): The name of the file.
                path (str): The path of the file in the repository.
                sha (str): The SHA (blob) of the file content.
                size (int): The size of the file in bytes.
                type (str): The type of the object, typically 'file'.
            commit (Dict[str, Any]): Details of the commit that created/updated the file. This dictionary contains:
                sha (str): The SHA of the commit.
                message (str): The commit message.
                author (Dict[str, Any]): The author of the commit. This dictionary contains:
                    name (str): The name of the author.
                    email (str): The email address of the author.
                    date (str): The timestamp of the authorship, in ISO 8601 format (e.g., 'YYYY-MM-DDTHH:MM:SSZ').
                committer (Dict[str, Any]): The committer of the commit. This dictionary contains:
                    name (str): The name of the committer.
                    email (str): The email address of the committer.
                    date (str): The timestamp of the commit, in ISO 8601 format (e.g., 'YYYY-MM-DDTHH:MM:SSZ').

    Raises:
        NotFoundError: If the repository or branch (if specified) does not exist.
        ValidationError: If required fields (path, message, content) are missing
            or if content is not base64 encoded.
        ConflictError: If updating a file and the provided 'sha' does not match
            the latest file SHA (blob SHA).
        ForbiddenError: If the user does not have write access to the repository
            (e.g., repository is archived or branch is protected).
    """
    # --- Input Validation ---
    if not owner: # Added owner validation for completeness, though typically caught by repo lookup
        raise custom_errors.ValidationError("Owner username must be provided.")
    if not repo: # Added repo validation for completeness
        raise custom_errors.ValidationError("Repository name must be provided.")
    if not path:
        raise custom_errors.ValidationError("Path is required.")
    if not message:
        raise custom_errors.ValidationError("Commit message is required.")
    if not content:
        raise custom_errors.ValidationError("Content is required.")

    try:
        decoded_content = base64.b64decode(content)
    except binascii.Error: # More specific exception for invalid base64
        raise custom_errors.ValidationError("Content must be a valid base64 encoded string.")

    path = path.lstrip('/')

    # --- Repository and Branch Resolution ---
    repo_full_name = f"{owner}/{repo}"
    repo_data = utils._find_repository_raw(DB, repo_full_name=repo_full_name)
    if not repo_data:
        raise custom_errors.NotFoundError(f"Repository '{repo_full_name}' not found.")
    repo_id = repo_data["id"]

    # Check if repository is archived (ForbiddenError)
    if repo_data.get("archived", False):
        raise custom_errors.ForbiddenError(f"Repository '{repo_full_name}' is archived and cannot be modified.")

    target_branch_name = branch if branch else repo_data.get("default_branch")
    if not target_branch_name: # Should be caught if default_branch is None and branch is None
        raise custom_errors.NotFoundError(
            f"Repository '{repo_full_name}' has no default branch and no branch was specified."
        )

    branches_table = utils._get_table(DB, "Branches")
    branch_data_tuple = next(
        ((idx, b_item) for idx, b_item in enumerate(branches_table) 
         if b_item.get("repository_id") == repo_id and b_item.get("name") == target_branch_name),
        None
    )

    if not branch_data_tuple:
        raise custom_errors.NotFoundError(f"Branch '{target_branch_name}' not found in repository '{repo_full_name}'.")
    branch_idx, branch_item_data = branch_data_tuple
    parent_commit_sha = branch_item_data["commit"]["sha"]

    # --- Get Committer Details & Check Protected Branch ---
    # Fetch owner_user_details for committer info and permission checks
    owner_user_details = utils._get_user_raw_by_identifier(DB, owner)
    author_name = owner # Default to login if user not in DB['Users']
    # Default noreply email, can be overridden if user email found
    author_email = f"{owner.lower().replace(' ', '').replace('.', '')}@users.noreply.github.com" 
    is_site_admin = False

    if owner_user_details:
        author_name = owner_user_details.get("name") or owner_user_details.get("login", owner)
        author_email = owner_user_details.get("email") or author_email
        is_site_admin = owner_user_details.get("site_admin", False)
    # Note: If owner_user_details is None, it means the 'owner' login performing the action
    # is not in DB['Users']. The function proceeds with generic committer info.
    # This could also be a point to raise an error if the committer must be a known user.

    # Protected Branch Check (ForbiddenError)
    if branch_item_data.get("protected", False):
        # Simplified rule: only site admins can push to protected branches
        if not is_site_admin:
            raise custom_errors.ForbiddenError(
                f"Branch '{target_branch_name}' is protected. "
                "Only site admins can write to this protected branch in this simulation."
            )

    # --- File Existence and SHA Check for Updates ---
    # Adjusted key format to be consistent if utils._generate_file_content_key is used elsewhere
    # Assuming file contents are keyed uniquely, perhaps by repo_id:commit_sha:path
    # The original code used this key format directly:
    file_content_key_parent_commit = f"{repo_id}:{parent_commit_sha}:{path}" 
    
    if "FileContents" not in DB:
        DB["FileContents"] = {}
    existing_file_db_entry = DB["FileContents"].get(file_content_key_parent_commit)
    is_update = existing_file_db_entry is not None

    if is_update:
        if sha is None:
            raise custom_errors.ValidationError("SHA (blob SHA of the file) must be provided when updating an existing file.")
        if existing_file_db_entry.get("sha") != sha:
            raise custom_errors.ConflictError("File SHA does not match. The file has been changed since the SHA was obtained.")
    elif sha is not None: # Creating a new file
        # GitHub API returns 422 if SHA is provided for a new file creation.
        # Here, we can choose to ignore it or raise a ValidationError.
        # For simplicity, current code implicitly ignores it. A stricter check could be:
        # raise ValidationError("SHA must not be provided when creating a new file.")
        pass


    # --- Prepare New File Content Details ---
    # SHA1 of "blob <size>\0<content>" is standard Git blob SHA.
    # The original code used hashlib.sha1(decoded_content).hexdigest() which is not a Git blob SHA.
    # For consistency with how `push_files` might calculate blob SHAs, let's use the Git way.
    new_blob_header = f"blob {len(decoded_content)}\0".encode('utf-8')
    new_blob_sha = hashlib.sha1(new_blob_header + decoded_content).hexdigest()
    file_size = len(decoded_content)
    file_name = path.split('/')[-1]

    # --- Create New Commit ---
    timestamp_iso = utils._get_current_timestamp_iso()
    git_actor_details = {"name": author_name, "email": author_email, "date": timestamp_iso}

    # Using a more deterministic approach for pseudo_tree_sha and commit_sha
    # For tree_sha, it should depend on all files in the tree at that commit.
    # This is highly simplified. A real tree SHA depends on paths and blob SHAs of all files.
    # For a single file change, we can base it on parent tree and the new file.
    # Let's assume a very simplified "tree" containing only this file for this commit's purpose.
    # This is NOT how Git works but provides a changing SHA.
    tree_items_for_sha = f"100644 blob {new_blob_sha}\t{path}\n" 
    # If other files existed, they'd be part of this string too, sorted by path.
    # This is a placeholder for a more complex tree calculation.
    pseudo_tree_sha = hashlib.sha1(tree_items_for_sha.encode('utf-8')).hexdigest()
    
    # Commit SHA calculation (simplified, similar to Git but not identical)
    commit_content_for_hashing_parts = [
        f"tree {pseudo_tree_sha}",
        f"parent {parent_commit_sha}" if parent_commit_sha else "",
        f"author {git_actor_details['name']} <{git_actor_details['email']}> {int(utils.datetime.strptime(timestamp_iso.rstrip('Z'), '%Y-%m-%dT%H:%M:%S.%f' if '.' in timestamp_iso else '%Y-%m-%dT%H:%M:%S').timestamp())} +0000",
        f"committer {git_actor_details['name']} <{git_actor_details['email']}> {int(utils.datetime.strptime(timestamp_iso.rstrip('Z'), '%Y-%m-%dT%H:%M:%S.%f' if '.' in timestamp_iso else '%Y-%m-%dT%H:%M:%S').timestamp())} +0000",
        f"\n{message}"
    ]
    commit_content_for_hashing = "\n".join(filter(None, commit_content_for_hashing_parts))
    new_commit_sha = hashlib.sha1(commit_content_for_hashing.encode('utf-8')).hexdigest()

    # Prepare a user sub-document for the commit's author/committer fields
    # This will be None if owner_user_details was None (user not in DB['Users'])
    prepared_user_subdoc = utils._prepare_user_sub_document(DB, owner, model_type="BaseUser")
    # If user was found (owner_user_details is not None) but subdoc prep failed (e.g., mocked to return None)
    if owner_user_details and not prepared_user_subdoc:
         raise custom_errors.NotFoundError(f"Could not prepare user sub-document for committer '{owner}'.")


    commit_node_id = f"C_NODE_{new_commit_sha[:10]}" # Simplified node_id

    commit_file_change_for_db = {
        "sha": new_blob_sha, "filename": path, "status": "modified" if is_update else "added",
        "additions": len(decoded_content.decode('utf-8', errors='ignore').splitlines()), # Line count
        "deletions": 0, # Simplified, a real diff would be needed for updates
        "changes": len(decoded_content.decode('utf-8', errors='ignore').splitlines()), # Simplified
        "patch": None 
    }
    commit_stats_for_db = {
        "total": commit_file_change_for_db["changes"], 
        "additions": commit_file_change_for_db["additions"], 
        "deletions": commit_file_change_for_db["deletions"]
    }

    new_commit_data_for_db = {
        "id": utils._get_next_id(utils._get_table(DB, "Commits"), "id"), # Auto-increment ID
        "sha": new_commit_sha, "node_id": commit_node_id, "repository_id": repo_id,
        "commit": { 
            "author": git_actor_details, "committer": git_actor_details,
            "message": message, "tree": {"sha": pseudo_tree_sha}, "comment_count": 0,
        },
        "author": prepared_user_subdoc, # Uses the potentially None sub-document
        "committer": prepared_user_subdoc, # Uses the potentially None sub-document
        "parents": [{"sha": parent_commit_sha}] if parent_commit_sha else [],
        "stats": commit_stats_for_db, "files": [commit_file_change_for_db],
        "created_at": timestamp_iso, "updated_at": timestamp_iso # Add timestamps
    }
    
    # Add commit, using "id" as primary and auto-generated. SHA should be unique by content.
    utils._add_raw_item_to_table(DB, "Commits", new_commit_data_for_db, id_field="id")


    # --- Store New FileContent in DB["FileContents"] ---
    new_file_content_data_for_db = {
        "type": "file", "encoding": "base64", "size": file_size,
        "name": file_name, "path": path, "content": content, "sha": new_blob_sha,
    }
    # Using the same keying convention as before (repo_id:commit_sha:path) for this version of the file
    file_content_key_new_commit = f"{repo_id}:{new_commit_sha}:{path}"
    DB["FileContents"][file_content_key_new_commit] = new_file_content_data_for_db

    # --- Update Root Directory Listing ---
    # Get or create root directory listing for this commit
    root_dir_key = f"{repo_id}:{new_commit_sha}:"
    
    # Inherit root directory listing from parent commit if it exists
    parent_root_dir_key = f"{repo_id}:{parent_commit_sha}:"
    existing_root_dir = DB["FileContents"].get(parent_root_dir_key, []).copy() if parent_commit_sha else []
    
    # If this is a new file in a subdirectory, add the directory to root listing
    if "/" in path:
        dir_name = path.split("/")[0]
        dir_exists = any(item.get("name") == dir_name and item.get("type") == "dir" for item in existing_root_dir)
        
        if not dir_exists:
            # Add the directory to root listing
            existing_root_dir.append({
                "type": "dir",
                "name": dir_name,
                "path": dir_name,
                "sha": hashlib.sha1(dir_name.encode('utf-8')).hexdigest()[:10]  # Simplified SHA
            })
    
    # Also add the file itself to root listing if it's in root
    if "/" not in path:
        file_exists = any(item.get("name") == file_name and item.get("type") == "file" for item in existing_root_dir)
        if not file_exists:
            existing_root_dir.append({
                "type": "file",
                "name": file_name,
                "path": path,
                "sha": new_blob_sha
            })
    
    # Update the root directory listing
    DB["FileContents"][root_dir_key] = existing_root_dir

    # --- Update Branch to Point to New Commit & Repository Push Time ---
    DB["Branches"][branch_idx]["commit"]["sha"] = new_commit_sha
    utils._update_raw_item_in_table(DB, "Repositories", repo_id, {"pushed_at": timestamp_iso})


    # --- Prepare Response Data ---
    response_content_details = {
        "name": file_name, "path": path, "sha": new_blob_sha, 
        "size": file_size, "type": "file",
        # Potentially add other fields like download_url, html_url if your model needs them
    }
    response_commit_details = {
        "sha": new_commit_sha, "message": message,
        "author": git_actor_details, "committer": git_actor_details,
        # Potentially add tree, parents, verification, etc.
    }

    return {"content": response_content_details, "commit": response_commit_details}


def create_repository(name: str, description: Optional[str] = None, private: Optional[bool] = False, auto_init: Optional[bool] = False) -> Dict[str, Any]:
    """Create a new GitHub repository.

    Creates a new GitHub repository. The user specifies the name for the
    repository and can optionally provide a description, set its visibility,
    and choose to auto-initialize it.

    Default Repository Settings:
        The following features are enabled by default for new repositories:
        - has_issues: True (Issues are enabled)
        - has_projects: True (Projects are enabled)
        - has_downloads: True (Downloads are enabled)
        - has_wiki: True (Wiki is enabled)
        - has_pages: False (GitHub Pages are disabled)
        - allow_forking: True (Repository can be forked)
        - archived: False (Repository is not archived)
        - disabled: False (Repository is not disabled)
        - is_template: False (Repository is not a template)
        - web_commit_signoff_required: False (Commit signoff not required)
        - visibility: "public" or "private" (based on private parameter)

    Args:
        name (str): The name for the new repository.
        description (Optional[str]): An optional description for the repository. Defaults to None.
        private (Optional[bool]): If True, the repository will be private. Defaults to False.
        auto_init (Optional[bool]): If True, creates an initial commit, potentially with a README. Defaults to False.

    Returns:
        Dict[str, Any]: A dictionary containing the details of the newly created repository with the following keys:
            id (int): Unique identifier for the repository.
            node_id (str): A globally unique identifier for the repository node.
            name (str): The name of the repository.
            full_name (str): The full name of the repository, including the owner (e.g., 'owner/repo').
            private (bool): Indicates whether the repository is private.
            owner (Dict[str, Any]): Details of the repository owner. Key non-URL fields include:
            login (str): the owner's username.
            id (int): the owner's unique ID.
            type (str): e.g., 'User' or 'Organization'.
            description (str): A short description of the repository.
            fork (bool): Indicates if the repository is a fork. This will be false for newly created repositories.
            created_at (str): The ISO 8601 timestamp for when the repository was created.
            updated_at (str): The ISO 8601 timestamp for when the repository was last updated.
            pushed_at (str): The ISO 8601 timestamp for when the repository was last pushed to.
            default_branch (str): The name of the default branch (e.g., 'main'). This is typically present if 'auto_init' was true during creation.

    Raises:
        ValidationError: If required inputs are missing (e.g., repository name) or if inputs are malformed (e.g., invalid characters in the name).
        UnprocessableEntityError: If the repository cannot be created due to semantic reasons, such as the repository name already existing for the user/organization, or other server-side validation failures not related to input format.
        ForbiddenError: If the authenticated user does not have the necessary permissions to create a repository (e.g., insufficient rights for an organization, or account restriction).
    """

    # 1. Input Validation for 'name'
    if not name:
        raise custom_errors.ValidationError("Repository name cannot be empty.")

    # 2. Determine Owner (Simulated Authenticated User)
    users_table = utils._get_table(DB, "Users")
    if not users_table:
        raise custom_errors.ForbiddenError("Cannot create repository: No users found in the system to assign ownership.")

    # For simulation, assume the first user in the DB is the authenticated user.
    owner_data_raw = users_table[0] 

    owner_login = owner_data_raw.get("login")
    owner_id = owner_data_raw.get("id")

    if not owner_login or owner_id is None: # Basic check for valid user data
        raise custom_errors.ForbiddenError("Authenticated user data is invalid or incomplete for repository creation.")

    owner_type = owner_data_raw.get("type", "User") # Default to "User" if not specified in DB

    # 3. Check for Existing Repository with the same name for this owner
    full_name_to_check = f"{owner_login}/{name}"
    repositories_table = utils._get_table(DB, "Repositories")
    for repo_in_db in repositories_table:
        if repo_in_db.get("full_name") == full_name_to_check:
            raise custom_errors.UnprocessableEntityError(f"Repository with name '{name}' already exists for owner '{owner_login}'.")

    # 4. Prepare Repository Data
    repo_id = utils._get_next_id(repositories_table, "id")

    repo_node_id_seed = f"Repository:{repo_id}"
    repo_node_id = base64.b64encode(repo_node_id_seed.encode('utf-8')).decode('utf-8')

    current_time_iso = utils._get_current_timestamp_iso()
    is_private_repo = bool(private) # Converts None to False, True to True

    default_branch_name = None
    if auto_init:
        default_branch_name = "main" # Common default branch name

    new_repo_data = {
        "id": repo_id,
        "node_id": repo_node_id,
        "name": name,
        "full_name": full_name_to_check,
        "private": is_private_repo,
        "owner": { # This structure should align with BaseUser in the schema
            "login": owner_login,
            "id": owner_id,
            "node_id": owner_data_raw.get("node_id"), # Optional field from User model
            "type": owner_type,
            "site_admin": owner_data_raw.get("site_admin", False) # Optional field
        },
        "description": description, # Retains None if not provided
        "fork": False, # New repositories are not forks
        "created_at": current_time_iso,
        "updated_at": current_time_iso,
        "pushed_at": current_time_iso, # Initially, pushed_at is same as created_at
        "size": 0, # Initial size, may increase if auto_init creates files/commits
        "stargazers_count": 0,
        "watchers_count": 0,
        "language": None,
        "has_issues": True,
        "has_projects": True,
        "has_downloads": True,
        "has_wiki": True,
        "has_pages": False,
        "forks_count": 0,
        "archived": False,
        "disabled": False,
        "open_issues_count": 0,
        "license": None,
        "allow_forking": True,
        "is_template": False,
        "web_commit_signoff_required": False,
        "topics": [],
        "visibility": "private" if is_private_repo else "public",
        "default_branch": default_branch_name,
        # Schema defaults for aliased count fields (from Repository model validator)
        "forks": 0,
        "open_issues": 0,
        "watchers": 0,
        "score": None # Not applicable for direct creation response
    }

    # 5. Handle auto_init (create initial commit and default branch)
    if auto_init:
        # Generate SHA for the initial commit (must be 40-char hex)
        # Using current time and repo ID for seed to ensure uniqueness for simulation
        timestamp_for_seed = str(datetime.utcnow().timestamp())
        initial_commit_sha_seed = f"initial_commit_for_repo_{repo_id}_{current_time_iso}_{timestamp_for_seed}"
        initial_commit_sha = hashlib.sha1(initial_commit_sha_seed.encode('utf-8')).hexdigest()

        initial_commit_node_id_seed = f"Commit:{initial_commit_sha}"
        initial_commit_node_id = base64.b64encode(initial_commit_node_id_seed.encode('utf-8')).decode('utf-8')

        # Generate SHA for the initial tree
        initial_tree_sha_seed = f"initial_tree_for_repo_{repo_id}_{current_time_iso}_{timestamp_for_seed}"
        initial_tree_sha = hashlib.sha1(initial_tree_sha_seed.encode('utf-8')).hexdigest()

        # Prepare GitActor (author/committer for the commit itself)
        git_actor_name = owner_data_raw.get("name", owner_login)
        git_actor_email = owner_data_raw.get("email", f"{owner_login}@users.noreply.github.com")

        git_actor_info = {
            "name": git_actor_name,
            "email": git_actor_email,
            "date": current_time_iso
        }

        # Prepare GitHub user object for commit's author/committer fields (links to GitHub user)
        commit_gh_user_info = {
            "login": owner_login,
            "id": owner_id,
            "node_id": owner_data_raw.get("node_id"),
            "type": owner_type,
            "site_admin": owner_data_raw.get("site_admin", False)
        }

        initial_commit_data = {
            "sha": initial_commit_sha,
            "node_id": initial_commit_node_id,
            "repository_id": repo_id, # Link commit to this repository
            "commit": { # Nested commit details
                "author": git_actor_info,
                "committer": git_actor_info,
                "message": "Initial commit",
                "tree": {"sha": initial_tree_sha},
                "comment_count": 0
            },
            "author": commit_gh_user_info, # GitHub user who authored
            "committer": commit_gh_user_info, # GitHub user who committed
            "parents": [], # No parents for initial commit
            "stats": {"total": 0, "additions": 0, "deletions": 0}, # No changes in empty initial commit
            "files": [] # No specific files added in this simplified auto_init
        }
        # Add commit to DB; SHA is the identifier, so no auto-generation of ID.
        utils._add_raw_item_to_table(DB, "Commits", initial_commit_data, id_field="sha", generate_id_if_missing_or_conflict=False)

        # Create the default branch pointing to this commit
        branches_table = utils._get_table(DB, "Branches")
        new_branch_data = {
            "name": default_branch_name, # e.g., "main"
            "commit": {"sha": initial_commit_sha}, # Points to the commit created above
            "protected": False,
            "repository_id": repo_id # Links branch to this repository
        }
        # Branches are typically identified by (name, repo_id), not a single ID.
        # Simple append is used here. A robust system would check for existing branch name for this repo.
        branches_table.append(new_branch_data)

        new_repo_data["size"] = 1 # Simulate a small size due to initialization (e.g. .git folder)
        # new_repo_data["pushed_at"] is already current_time_iso, which is correct.

    # 6. Add Repository to DB
    # utils._add_raw_item_to_table uses 'id' field by default.
    created_repo_in_db = utils._add_raw_item_to_table(DB, "Repositories", new_repo_data)

    # 7. Construct and Return Response Dictionary as per docstring
    # The 'owner' field in the response has a specific, simpler structure.
    response_owner_details = {
        "login": created_repo_in_db["owner"]["login"],
        "id": created_repo_in_db["owner"]["id"],
        "type": created_repo_in_db["owner"]["type"]
    }

    return_dict = {
        "id": created_repo_in_db["id"],
        "node_id": created_repo_in_db["node_id"],
        "name": created_repo_in_db["name"],
        "full_name": created_repo_in_db["full_name"],
        "private": created_repo_in_db["private"],
        "owner": response_owner_details,
        "description": created_repo_in_db["description"],
        "fork": created_repo_in_db["fork"],
        "created_at": created_repo_in_db["created_at"],
        "updated_at": created_repo_in_db["updated_at"],
        "pushed_at": created_repo_in_db["pushed_at"],
        "default_branch": created_repo_in_db["default_branch"] # Will be None if auto_init was False
    }

    return return_dict

def push_files(owner: str, repo: str, branch: str, files: List[Dict[str, str]], 
               message: str, author_date: Optional[str] = None, 
               committer_date: Optional[str] = None) -> Dict[str, Any]:
    """Push multiple files in a single commit.

    This function pushes multiple files in a single commit. It uses the provided
    repository owner's username, repository name, target branch name, a list of
    files (each defined by its path and content), and a commit message to
    perform the operation.

    Args:
        owner (str): The username of the account that owns the repository.
        repo (str): The name of the repository.
        branch (str): The name of the branch to push the files to.
        files (List[Dict[str, str]]): A list of dictionaries, where each dictionary
            represents a file to be pushed. Each dictionary must contain the
            following keys:
            path (str): The full path of the file within the repository.
            content (str): The content of the file.
        message (str): The commit message for the push operation.
        author_date (Optional[str]): Custom author date in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ).
            If not provided, current date will be used.
        committer_date (Optional[str]): Custom committer date in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ).
            If not provided, current date will be used.

    Returns:
        Dict[str, Any]: Details of the successful push operation, including commit
            information. It contains the following fields:
            commit_sha (str): The SHA of the new commit created.
            tree_sha (str): The SHA of the new tree object representing the repository state.
            message (str): A confirmation message regarding the push.

    Raises:
        NotFoundError: If the repository or branch does not exist, or if the
            owner (acting as committer) is not found in the Users table.
        ValidationError: If 'files' list is empty, file structure is invalid
            (e.g., missing 'path' or 'content' in a file dictionary),
            or message is missing.
        ConflictError: If the push cannot be fast-forwarded or if there are
            conflicts with recent changes on the branch.
    """
    # --- Input Validation ---
    if not owner:
        raise custom_errors.ValidationError("Owner username must be provided.")
    if not repo:
        raise custom_errors.ValidationError("Repository name must be provided.")
    if not branch:
        raise custom_errors.ValidationError("Branch name must be provided.")
    if not message:
        raise custom_errors.ValidationError("Commit message must be provided.")
    if not files:
        raise custom_errors.ValidationError("Files list cannot be empty.")

    validated_files_input = []
    for i, file_item in enumerate(files):
        if not isinstance(file_item, dict):
            raise custom_errors.ValidationError(f"File item at index {i} must be a dictionary.")
        path_val = file_item.get("path")
        current_file_content_str = file_item.get("content")
        if not path_val or not isinstance(path_val, str):
            raise custom_errors.ValidationError(f"File item at index {i} is missing 'path' or path is not a valid string.")
        if current_file_content_str is None or not isinstance(current_file_content_str, str):
            raise custom_errors.ValidationError(f"File item at index {i} is missing 'content' or content is not a string.")
        validated_files_input.append({"path": path_val, "content": current_file_content_str})

    # --- Fetch Repository ---
    repo_full_name = f"{owner}/{repo}"
    repo_db_entry = utils._find_repository_raw(DB, repo_full_name=repo_full_name)
    if not repo_db_entry:
        raise custom_errors.NotFoundError(f"Repository '{repo_full_name}' not found.")
    repo_id = repo_db_entry["id"]

    # --- Fetch Branch and Original Parent Commit SHA ---
    branches_table = utils._get_table(DB, "Branches")
    branch_db_entry = None
    branch_idx = -1
    for i, b_entry in enumerate(branches_table):
        if b_entry.get("repository_id") == repo_id and b_entry.get("name") == branch:
            branch_db_entry = b_entry
            branch_idx = i
            break

    if not branch_db_entry:
        raise custom_errors.NotFoundError(f"Branch '{branch}' not found in repository '{repo_full_name}'.")

    original_parent_commit_sha = branch_db_entry["commit"]["sha"]

    # --- Determine Parent Commit's File Blobs ---
    parent_commit_blob_shas = {}
    if original_parent_commit_sha:
        file_contents_table = DB.get("FileContents", {})
        for key, file_content_obj_dict in file_contents_table.items():
            # Check if key matches the new format: repo_id:commit_sha:path
            if key.startswith(f"{repo_id}:{original_parent_commit_sha}:"):
                if isinstance(file_content_obj_dict, dict):
                    item_path = file_content_obj_dict.get("path")
                    item_blob_sha = file_content_obj_dict.get("sha") # This is blob SHA
                    if item_path and item_blob_sha:
                        parent_commit_blob_shas[item_path] = item_blob_sha

    # --- Prepare New Tree Content ---
    new_tree_files_map = parent_commit_blob_shas.copy()
    pushed_files_details = {}
    for file_data in validated_files_input:
        path = file_data["path"]
        content_str = file_data["content"]
        content_bytes = content_str.encode('utf-8')
        blob_header = f"blob {len(content_bytes)}\0".encode('utf-8')
        blob_sha = hashlib.sha1(blob_header + content_bytes).hexdigest()
        new_tree_files_map[path] = blob_sha
        pushed_files_details[path] = {
            "blob_sha": blob_sha,
            "content_str": content_str,
            "content_bytes": content_bytes
        }

    # --- Calculate Tree SHA ---
    sorted_tree_items = sorted(list(new_tree_files_map.items()), key=lambda x: x[0])
    tree_content_for_hashing = ""
    for item_path, item_blob_sha in sorted_tree_items:
        tree_content_for_hashing += f"100644 blob {item_blob_sha}\t{item_path}\n"
    tree_sha = hashlib.sha1(tree_content_for_hashing.encode('utf-8')).hexdigest()

    # --- Determine File Changes for Commit Object ---
    commit_file_changes_list = []
    # Note: Original code had bug where only pushed files are iterated.
    # A true diff would compare new_tree_files_map with parent_commit_blob_shas
    # to identify added, modified, and DELETED files for the commit.
    # For now, sticking to original logic of only reflecting pushed files as added/modified.
    for path, details in pushed_files_details.items(): # Iterates only over *pushed* files
        new_blob_sha = details["blob_sha"]
        content_str = details["content_str"] # Used for num_lines
        num_lines = len(content_str.splitlines())
        status = "added"
        additions = num_lines
        deletions = 0 # Simple assumption for this logic
        changes = num_lines

        original_blob_in_parent = parent_commit_blob_shas.get(path)
        if original_blob_in_parent is not None:
            if original_blob_in_parent == new_blob_sha:
                # File content is identical to parent, so no change for this file
                continue # Skip adding to commit_file_changes_list
            else:
                status = "modified"
                # A more complex diff would calculate actual additions/deletions lines.
                # For simplicity, keeping original "additions=num_lines, deletions=0" for modified.
        
        file_change_data = {
            "sha": new_blob_sha, "filename": path, "status": status,
            "additions": additions, "deletions": deletions, "changes": changes,
            "patch": None # Generating patch data is complex, so keeping as None
        }
        commit_file_changes_list.append(file_change_data)

    # If no files actually changed content compared to parent, technically commit might be empty or not needed.
    # However, Git allows commits that don't change anything if forced (e.g. git commit --allow-empty)
    # Here, we proceed if commit_file_changes_list has items. If it's empty due to all files matching parent,
    # current logic would still create a commit object, but with an empty "files" list in the commit data.
    # This might be acceptable for the simulation.

    # --- Create Commit Object and SHA ---
    # Use provided dates or get current timestamp
    current_time_dt = datetime.now(timezone.utc)
    current_timestamp_iso = utils._get_current_timestamp_iso()

    # Fetch committer details from the Users table using the 'owner' login
    committer_user_raw = utils._get_user_raw_by_identifier(DB, owner) # 'owner' is the login string

    if not committer_user_raw:
        raise custom_errors.NotFoundError(f"User '{owner}' (acting as committer) not found in Users table.")

    committer_name_for_git = committer_user_raw.get("name", owner) # Fallback to login if 'name' not present
    committer_email_for_git = committer_user_raw.get("email")

    # Create author data with custom date if provided
    author_data = {
        "name": committer_name_for_git,
        "email": committer_email_for_git,
        "date": author_date if author_date is not None else current_timestamp_iso
    }

    # Create committer data with custom date if provided
    committer_data = {
        "name": committer_name_for_git,
        "email": committer_email_for_git,
        "date": committer_date if committer_date is not None else current_timestamp_iso
    }

    commit_nested_data = {
        "author": author_data,
        "committer": committer_data,
        "message": message,
        "tree": {"sha": tree_sha},
        "comment_count": 0
    }
    
    parents_list_for_commit = []
    if original_parent_commit_sha:
        parents_list_for_commit.append({"sha": original_parent_commit_sha})

    commit_content_for_hashing_parts = [f"tree {tree_sha}"]
    if original_parent_commit_sha:
        commit_content_for_hashing_parts.append(f"parent {original_parent_commit_sha}")

    # Format timestamps for git format
    author_timestamp_git_format = f"{int(current_time_dt.timestamp())} +0000"
    committer_timestamp_git_format = f"{int(current_time_dt.timestamp())} +0000"
    
    # If custom dates are provided, we need to parse them to get the timestamp
    if author_date is not None:
        try:
            # Parse ISO 8601 date format
            author_dt = datetime.fromisoformat(author_date.replace('Z', '+00:00'))
            author_timestamp_git_format = f"{int(author_dt.timestamp())} +0000"
        except ValueError:
            # If parsing fails, use current time
            pass
            
    if committer_date is not None:
        try:
            # Parse ISO 8601 date format
            committer_dt = datetime.fromisoformat(committer_date.replace('Z', '+00:00'))
            committer_timestamp_git_format = f"{int(committer_dt.timestamp())} +0000"
        except ValueError:
            # If parsing fails, use current time
            pass

    commit_content_for_hashing_parts.extend([
        f"author {author_data['name']} <{author_data['email']}> {author_timestamp_git_format}",
        f"committer {committer_data['name']} <{committer_data['email']}> {committer_timestamp_git_format}",
        f"\n{message}"
    ])
    
    new_commit_sha = hashlib.sha1("\n".join(commit_content_for_hashing_parts).encode('utf-8')).hexdigest()
    new_commit_node_id = f"C_kwDOAAB{utils._get_next_id(utils._get_table(DB, 'Commits'), 'id')}_{new_commit_sha[:20]}" # Example node_id

    commit_author_subdoc = utils._prepare_user_sub_document(DB, owner, model_type="BaseUser")
    if not commit_author_subdoc: # Should be caught by committer_user_raw check earlier
         raise custom_errors.NotFoundError(f"Could not prepare user sub-document for committer '{owner}'.")
    commit_committer_subdoc = commit_author_subdoc

    total_additions = sum(fc["additions"] for fc in commit_file_changes_list)
    total_deletions = sum(fc["deletions"] for fc in commit_file_changes_list)
    commit_stats_data = {"total": total_additions + total_deletions, "additions": total_additions, "deletions": total_deletions}

    new_commit_data = {
        # "id" will be generated by _add_raw_item_to_table
        "sha": new_commit_sha,
        "node_id": new_commit_node_id,
        "repository_id": repo_id,
        "commit": commit_nested_data,
        "author": commit_author_subdoc,
        "committer": commit_committer_subdoc,
        "parents": parents_list_for_commit,
        "stats": commit_stats_data,
        "files": commit_file_changes_list,
        # Use the provided dates or current timestamp
        "created_at": author_data["date"],
        "updated_at": committer_data["date"]
    }
    added_commit_raw_item = utils._add_raw_item_to_table(DB, "Commits", new_commit_data, id_field="id")
    new_commit_data_id = added_commit_raw_item["id"] # Get the auto-generated ID if "id" is the field

    # --- Store FileContents in DB["FileContents"] for the new commit ---
    if "FileContents" not in DB: DB["FileContents"] = {}
    
    for path, blob_sha_for_file in new_tree_files_map.items():
        content_str_for_this_file = ""
        content_bytes_for_this_file = b""

        if path in pushed_files_details:
            content_str_for_this_file = pushed_files_details[path]["content_str"]
            content_bytes_for_this_file = pushed_files_details[path]["content_bytes"]
        else: 
            parent_fc_key = f"{repo_id}:{original_parent_commit_sha}:{path}"
            parent_file_content_entry = DB.get("FileContents", {}).get(parent_fc_key)

            if isinstance(parent_file_content_entry, dict):
                parent_content_value = parent_file_content_entry.get("content")
                parent_encoding = parent_file_content_entry.get("encoding")

                if parent_encoding == "base64" and isinstance(parent_content_value, str):
                    try:
                        decoded_bytes = base64.b64decode(parent_content_value)
                        content_str_for_this_file = decoded_bytes.decode('utf-8')
                        content_bytes_for_this_file = decoded_bytes
                    except (base64.binascii.Error, UnicodeDecodeError):
                        content_str_for_this_file = "" 
                        content_bytes_for_this_file = b""
                elif parent_encoding == "text" and isinstance(parent_content_value, str):
                    content_str_for_this_file = parent_content_value
                    content_bytes_for_this_file = content_str_for_this_file.encode('utf-8')
                elif isinstance(parent_content_value, str): # Default assumption
                    content_str_for_this_file = parent_content_value
                    content_bytes_for_this_file = content_str_for_this_file.encode('utf-8')
            
        file_content_db_key = f"{repo_id}:{new_commit_sha}:{path}"
        file_content_entry_data = {
            "type": "file",
            "encoding": "text", 
            "size": len(content_bytes_for_this_file), 
            "name": path.split('/')[-1],
            "path": path,
            "content": content_str_for_this_file, 
            "sha": blob_sha_for_file 
        }
        DB["FileContents"][file_content_db_key] = file_content_entry_data

    # --- Update Root Directory Listing ---
    # Get or create root directory listing for this commit
    root_dir_key = f"{repo_id}:{new_commit_sha}:"
    existing_root_dir = DB["FileContents"].get(root_dir_key, [])
    
    # Add all files and directories to root listing
    for path, blob_sha_for_file in new_tree_files_map.items():
        file_name = path.split('/')[-1]
        
        if "/" in path:
            # This is a file in a subdirectory
            dir_name = path.split("/")[0]
            dir_exists = any(item.get("name") == dir_name and item.get("type") == "dir" for item in existing_root_dir)
            
            if not dir_exists:
                # Add the directory to root listing
                existing_root_dir.append({
                    "type": "dir",
                    "name": dir_name,
                    "path": dir_name,
                    "sha": hashlib.sha1(dir_name.encode('utf-8')).hexdigest()[:10]  # Simplified SHA
                })
        else:
            # This is a file in root
            file_exists = any(item.get("name") == file_name and item.get("type") == "file" for item in existing_root_dir)
            if not file_exists:
                existing_root_dir.append({
                    "type": "file",
                    "name": file_name,
                    "path": path,
                    "sha": blob_sha_for_file
                })
    
    # Update the root directory listing
    DB["FileContents"][root_dir_key] = existing_root_dir

    # --- Update Branch Pointer (Fast-Forward Check) ---
    current_branch_db_entry_for_update = utils._get_table(DB, "Branches")[branch_idx]
    if current_branch_db_entry_for_update["commit"]["sha"] != original_parent_commit_sha:
        utils._remove_raw_item_from_table(DB, "Commits", new_commit_data_id, id_field="id") # Use generated "id"
        
        keys_to_delete_from_filecontents = []
        for k in DB.get("FileContents", {}).keys():
            # Check if key matches the format: repo_id:commit_sha:path
            if k.startswith(f"{repo_id}:{new_commit_sha}:"):
                keys_to_delete_from_filecontents.append(k)
        
        for k_del in keys_to_delete_from_filecontents:
            if k_del in DB["FileContents"]: # Check existence before deleting
                 del DB["FileContents"][k_del]
        raise custom_errors.ConflictError("Branch has been updated since last fetch. Push cannot be fast-forwarded.")
    
    current_branch_db_entry_for_update["commit"]["sha"] = new_commit_sha
    # If Branches table items have 'id' and 'updated_at', you might want to update them:
    # branch_id_to_update = current_branch_db_entry_for_update.get("id") # Assuming branches have IDs
    # if branch_id_to_update:
    #     utils._update_raw_item_in_table(DB, "Branches", branch_id_to_update, 
    #                                     {"commit": {"sha": new_commit_sha}, "updated_at": git_actor_timestamp_iso})


    # --- Update Repository `pushed_at` timestamp ---
    utils._update_raw_item_in_table(DB, "Repositories", repo_id,
                                    {"pushed_at": committer_data["date"]})

    return {
        "commit_sha": new_commit_sha,
        "tree_sha": tree_sha,
        "message": f"Successfully pushed {len(commit_file_changes_list)} file(s) (with changes) to {repo_full_name}/{branch}."
    }

def list_branches(owner: str, repo: str, page: Optional[int] = None, per_page: Optional[int] = None) -> List[Dict[str, Any]]:
    """List branches in a GitHub repository.

    Lists branches in a GitHub repository, sorted by name. This function allows for pagination
    of the results.

    Args:
        owner (str): The owner of the repository. Must not be empty.
        repo (str): The name of the repository. Must not be empty.
        page (Optional[int]): The page number of the results to fetch. Defaults to 1.
                             Must be a positive integer if provided.
        per_page (Optional[int]): The number of results per page. Defaults to 30.
                                 Must be a positive integer if provided.

    Returns:
        List[Dict[str, Any]]: A list of branch objects from the repository, sorted by name.
            Each dictionary in the list represents a branch object and has the following fields:
            name (str): The name of the branch.
            commit (Dict[str, Any]): A dictionary representing the latest commit on this
                branch. This dictionary contains at least the following field:
                sha (str): The SHA identifier of the commit.
            protected (bool): A boolean indicating if the branch is protected.

    Raises:
        NotFoundError: If the repository does not exist.
        ValueError: If 'owner' or 'repo' are empty, or if 'page' or 'per_page'
                    are provided and are not positive integers.
    """

    # Validate required string inputs
    if not owner: # Checks for empty string, None is caught by type hinting but good for robustness
        raise ValueError("Repository owner name must not be empty.")
    if not repo:  # Checks for empty string
        raise ValueError("Repository name must not be empty.")

    # Validate pagination parameters
    if page is not None and page <= 0:
        raise ValueError("Page number must be a positive integer.")
    if per_page is not None and per_page <= 0:
        raise ValueError("Results per page (per_page) must be a positive integer.")

    # Determine actual page and per_page values for logic
    actual_page = page if page is not None else 1
    actual_per_page = per_page if per_page is not None else DEFAULT_PER_PAGE

    # Find the repository
    repo_full_name = f"{owner}/{repo}"
    repository_data = utils._find_repository_raw(DB, repo_full_name=repo_full_name)
    if not repository_data:
        raise custom_errors.NotFoundError(f"Repository '{repo_full_name}' not found.")

    repo_id = repository_data["id"]

    # Retrieve all branches from the DB for the repository
    all_branches_in_db = DB.get("Branches", [])

    # Filter branches that belong to the specified repository.
    repo_branches_raw = [
        branch_dict for branch_dict in all_branches_in_db
        if branch_dict.get("repository_id") == repo_id
    ]

    # Sort the filtered branches by name
    repo_branches_raw.sort(key=lambda b: b['name'])

    # Apply pagination
    start_index = (actual_page - 1) * actual_per_page
    end_index = start_index + actual_per_page
    paginated_branches_raw = repo_branches_raw[start_index:end_index]

    # Format the branches for the response
    result_list: List[Dict[str, Any]] = []
    for branch_data in paginated_branches_raw:
        formatted_branch = {
            "name": branch_data["name"],
            "commit": {
                "sha": branch_data["commit"]["sha"]
            },
            "protected": branch_data["protected"]
        }
        result_list.append(formatted_branch)

    return result_list

def fork_repository(owner: str, repo: str, organization: Optional[str] = None) -> Dict[str, Any]:
    """Fork a repository.

    Creates a fork for the authenticated user. The user should have 
    `Administration` repository permissions (write) to set up and configure the new repository (users fork) under the users account.
    `Contents` repository permissions (read) to read the `Contents` of the original repository to get all the data.

    Args:
        owner (str): The account owner of the repository. The name is not case sensitive.
        repo (str): The name of the repository without the `.git` extension. The name is not case sensitive.
        organization (Optional[str]): Optional parameter to specify the organization name if forking into an organization.

    Returns:
        Dict[str, Any]: A dictionary containing the details of the newly forked repository. The structure includes the following fields:
            id (int): The unique identifier for the repository.
            name (str): The name of the repository.
            full_name (str): The full name of the repository, in the format 'owner_login/repository_name'.
            owner (Dict[str, Any]): An object describing the owner of the forked repository. It includes the following sub-fields:
                login (str): The login name of the owner.
                id (int): The unique identifier of the owner.
                type (str): The type of owner (e.g., 'User', 'Organization').
            private (bool): True if the repository is private, false otherwise.
            description (Optional[str]): A short description of the repository.
            fork (bool): True, indicating that this repository is a fork.

    Raises:
        TypeError: If any of the input arguments do not match their expected types.
        RuntimeError: If the authenticated user cannot be resolved from the DB.
        NotFoundError: If the source repository does not exist or target organization does not exist.
        UnprocessableEntityError: If the repository has already been forked by the user/organization, or other fork restrictions apply.
        ForbiddenError: If the user does not have permission to read the source repository, 
                        if forking is disabled on the source, or if the user cannot create 
                        repositories in the target organization.
    """
    # --- Input Validation ---

    if not isinstance(owner, str):

        raise TypeError("Argument 'owner' must be a string.")

    if not isinstance(repo, str):

        raise TypeError("Argument 'repo' must be a string.")

    if organization is not None and not isinstance(organization, str):

        raise TypeError("Argument 'organization' must be a string or None.")
    
    # --- Authenticated User (Simulation) ---
    current_user_info = utils.get_current_user()
    AUTH_USER_ID = current_user_info["id"]
    AUTH_USER_LOGIN = current_user_info["login"]
    
    auth_user_raw = utils._get_user_raw_by_identifier(DB, AUTH_USER_ID)
    if not auth_user_raw:
        # This indicates a setup issue if the authenticated user doesn't exist in Users table.
        raise RuntimeError(f"Authenticated user '{AUTH_USER_LOGIN}' (ID: {AUTH_USER_ID}) not found in DB Users table.")

    # --- 1. Find Source Repository (Case-Insensitive) ---
    source_repo_found = None
    repositories_table = utils._get_table(DB, "Repositories")
    for r_data in repositories_table:
        repo_owner_login = r_data.get("owner", {}).get("login", "")
        repo_name_val = r_data.get("name", "")
        if repo_owner_login.lower() == owner.lower() and repo_name_val.lower() == repo.lower():
            source_repo_found = r_data
            break

    if not source_repo_found:
        raise custom_errors.NotFoundError(f"Source repository {owner}/{repo} not found.")
    source_repo = source_repo_found

    # --- 2. Check if Source Repository Allows Forking ---
    if not source_repo.get("allow_forking", True): # Defaults to True if field is missing
        raise custom_errors.ForbiddenError(f"Forking is disabled for the repository {owner}/{repo}.")

    # --- Permission Check: Read Source Repository (Contents permission) ---
    # The user needs at least "read" permission on the source repository.
    # utils._check_repository_permission handles public/private logic internally.
    can_read_source = utils._check_repository_permission(DB, AUTH_USER_ID, source_repo["id"], "read")
    if not can_read_source:
        raise custom_errors.ForbiddenError(f"User '{AUTH_USER_LOGIN}' does not have read permission for the source repository '{owner}/{repo}'.")

    # --- 3. Determine Fork Owner Entity ---
    fork_target_owner_entity_raw: Optional[Dict[str, Any]]
    if organization:
        fork_target_owner_entity_raw = utils._get_user_raw_by_identifier(DB, organization)
        if not fork_target_owner_entity_raw or fork_target_owner_entity_raw.get("type") != "Organization":
            raise custom_errors.NotFoundError(f"Organization '{organization}' not found or is not an organization type.")
        # This is an organization-level permission (e.g., member of a team with repo creation rights, org admin).
        # This simulation assumes if the organization is valid, the user has rights.
    else:
        # Forking to the authenticated user's account.
        # The user inherently has rights to create repositories in their own namespace.
        # They will become the owner of the fork, granting them "Administration repository permissions (write)".
        fork_target_owner_entity_raw = auth_user_raw

    if not fork_target_owner_entity_raw: 
        # Should ideally be caught by earlier checks or auth_user_raw validation
        raise RuntimeError("Failed to determine fork owner entity. This should not happen.")

    fork_target_owner_login = fork_target_owner_entity_raw["login"]

    # --- 4. Determine New Repository Name ---
    new_fork_name = source_repo["name"]

    # --- 5. Check for Existing Fork or Name Collision ---
    for existing_repo in repositories_table:
        if existing_repo.get("owner", {}).get("login") == fork_target_owner_login:
            fork_details = existing_repo.get("fork_details") # Using a simulated field for fork parentage
            if fork_details and fork_details.get("parent_id") == source_repo["id"]:
                raise custom_errors.UnprocessableEntityError(
                    f"Repository '{source_repo['full_name']}' has already been forked by '{fork_target_owner_login}' as '{existing_repo.get('full_name')}'.")
            if existing_repo.get("name") == new_fork_name:
                raise custom_errors.UnprocessableEntityError(
                    f"A repository named '{new_fork_name}' already exists for '{fork_target_owner_login}'.")

    # --- 6. Create New Forked Repository Data ---
    new_repo_id = utils._get_next_id(repositories_table) 
    current_time_iso = utils._get_current_timestamp_iso()

    fork_owner_repo_data = {
        "login": fork_target_owner_entity_raw["login"],
        "id": fork_target_owner_entity_raw["id"],
        "node_id": fork_target_owner_entity_raw.get("node_id"), # User model has node_id
        "type": fork_target_owner_entity_raw["type"],
        "site_admin": fork_target_owner_entity_raw.get("site_admin", False)
    }

    forked_repo_data = {
        "id": new_repo_id,
        "node_id": base64.b64encode(f"Repository:{new_repo_id}".encode('utf-8')).decode('utf-8'), # Simulated unique node_id for repositories
        "name": new_fork_name,
        "full_name": f"{fork_target_owner_login}/{new_fork_name}",
        "owner": fork_owner_repo_data, # Matches BaseUser structure
        "private": source_repo["private"], # Forks inherit privacy status
        "description": source_repo.get("description"),
        "fork": True,
        "created_at": current_time_iso,
        "updated_at": current_time_iso,
        "pushed_at": current_time_iso, # Initial state, effectively "pushed" now
        "size": source_repo.get("size", 0), # Size can be copied or recalculated; copying is simpler
        "language": source_repo.get("language"),
        "has_issues": source_repo.get("has_issues", True),
        "has_projects": source_repo.get("has_projects", True),
        "has_downloads": source_repo.get("has_downloads", True),
        "has_wiki": source_repo.get("has_wiki", True),
        "has_pages": source_repo.get("has_pages", False), # Typically false for new forks
        "stargazers_count": 0,
        "watchers_count": 1, # Forker (owner) usually auto-watches their fork
        "forks_count": 0,    # This new fork has 0 forks of itself initially
        "open_issues_count": 0, # Issues are generally not copied by default
        "license": source_repo.get("license"), 
        "allow_forking": True, # Forks are generally forkable by default
        "is_template": False,  # Forks are not templates
        "default_branch": source_repo.get("default_branch"), # May be updated after branch copy
        "visibility": "public" if not source_repo["private"] else "private",
        "archived": False,
        "disabled": False,
        "web_commit_signoff_required": source_repo.get("web_commit_signoff_required", False),
        "topics": list(source_repo.get("topics", [])), # Copy topics
        # Custom field for simulation to track fork lineage
        "fork_details": {
            "parent_id": source_repo["id"],
            "parent_full_name": source_repo["full_name"],
            "source_id": source_repo.get("fork_details", {}).get("source_id", source_repo["id"]),
            "source_full_name": source_repo.get("fork_details", {}).get("source_full_name", source_repo["full_name"]),
        },
        # Aliased fields from Pydantic model, ensure they are consistent
        "forks": 0,
        "open_issues": 0,
        "watchers": 1,
    }

    # --- 7. Add Forked Repository to DB ---
    utils._add_raw_item_to_table(DB, "Repositories", forked_repo_data)

    # --- 8. Handle Branches ---
    branches_table = utils._get_table(DB, "Branches")
    copied_any_branch = False

    for branch_data in branches_table: # Iterate over a copy if modifying list during iteration
        if branch_data.get("repository_id") == source_repo["id"]:
            new_branch_entry = branch_data.copy()
            new_branch_entry["repository_id"] = new_repo_id
            # The Branch model does not have its own 'id'.
            # Add to DB["Branches"] directly.
            DB["Branches"].append(new_branch_entry)
            copied_any_branch = True

    if not copied_any_branch:
        # If no branches were copied (e.g., source had no branches), 
        # ensure the fork's default_branch is None.
        forked_repo_data["default_branch"] = None 
        utils._update_raw_item_in_table(DB, "Repositories", new_repo_id, {"default_branch": None})

    # --- 9. Update Source Repository's Forks Count & Timestamp ---
    updated_forks_count = source_repo.get("forks_count", 0) + 1
    source_update_payload = {
        "forks_count": updated_forks_count,
        "forks": updated_forks_count, # Pydantic model aliases forks_count to forks
        "updated_at": current_time_iso # Forking action updates the source repo's metadata
    }
    utils._update_raw_item_in_table(DB, "Repositories", source_repo["id"], source_update_payload)

    # --- 10. Prepare and Return Formatted Output ---
    # This structure matches the `ForkedRepository` model described in the docstring.
    owner_details_for_return = {
        "login": fork_target_owner_entity_raw["login"],
        "id": fork_target_owner_entity_raw["id"],
        "type": fork_target_owner_entity_raw["type"]
    }

    return_dict = {
        "id": forked_repo_data["id"],
        "name": forked_repo_data["name"],
        "full_name": forked_repo_data["full_name"],
        "owner": owner_details_for_return, # Matches ForkedRepositoryOwner structure
        "private": forked_repo_data["private"],
        "description": forked_repo_data.get("description"),
        "fork": True # This is a defining characteristic of the returned object
    }

    return return_dict

def get_file_contents(owner: str, repo: str, path: str, ref: Optional[str] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """Get contents of a file or directory.

    This function retrieves the content of a specified file or directory within a
    repository. The nature of the returned data depends on whether the specified
    path points to a file or a directory.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        path (str): The path to the file or directory within the repository.
        ref (Optional[str]): An optional Git reference (e.g., a branch name,
            tag, or commit SHA) specifying the version of the content to retrieve.
            Defaults to None.

    Returns:
        Union[Dict[str, Any], List[Dict[str, Any]]]: The content of the specified path.
        If the path points to a file, this will be a dictionary containing file
        details with the following keys:
            type (str): The type of content, typically 'file'.
            encoding (str): The encoding of the file content, e.g., 'base64'.
            size (int): The size of the file in bytes.
            name (str): The name of the file.
            path (str): The path of the file within the repository.
            content (str): The content of the file, typically base64 encoded.
            sha (str): The Git blob SHA of the file.
        If the path points to a directory, this will be a list of dictionaries.
        Each dictionary in the list represents a file or directory entry and
        contains the following keys:
            type (str): The type of item, either 'file' or 'dir'.
            size (int): The size of the item in bytes. For directories, this may
                        represent the size of the tree object or be 0.
            name (str): The name of the file or directory.
            path (str): The path of the file or directory within the repository.
            sha (str): The Git blob SHA (for files) or tree SHA (for directories).

    Raises:
        ValidationError: If owner, repo, or path are empty.
        NotFoundError: If the repository, branch/ref, or path does not exist.
    """

    # Input Validations for required fields
    if not owner:
        raise custom_errors.ValidationError("Repository owner cannot be empty.")
    if not repo:
        raise custom_errors.ValidationError("Repository name cannot be empty.")
    # Validate path - allow None but not empty string for backward compatibility
    if path is None:
        raise custom_errors.ValidationError("Path cannot be None.")
    if path == "":
        raise custom_errors.ValidationError("Path cannot be empty.")

    # Find Repository
    repo_full_name = f"{owner}/{repo}"
    repository_data = utils._find_repository_raw(DB, repo_full_name=repo_full_name)
    if not repository_data:
        raise custom_errors.NotFoundError(f"Repository '{repo_full_name}' not found.")

    # Get repo_id, which is used by test DB for associating branches/commits
    repo_id: int = repository_data["id"]

    # Determine Target Commit SHA and Reference Name for Key
    ref_for_display: Optional[str] = ref

    ref_to_resolve: Optional[str]
    if ref is None:
        ref_to_resolve = repository_data.get("default_branch")
        if not ref_to_resolve:
            raise custom_errors.NotFoundError(f"Repository '{repo_full_name}' does not have a default branch.")
        ref_for_display = ref_to_resolve
    else:
        ref_to_resolve = ref

    commit_sha: Optional[str] = None

    # Try to resolve ref_to_resolve as a branch name
    branches_in_db: List[Dict[str, Any]] = DB.get("Branches", [])
    for branch_item in branches_in_db:
        if branch_item.get("repository_id") == repo_id and branch_item.get("name") == ref_to_resolve:
            commit_info = branch_item.get("commit")
            if isinstance(commit_info, dict):
                 commit_sha = commit_info.get("sha")
            break

    # If not resolved as a branch, try to resolve ref_to_resolve as a tag name
    if commit_sha is None:
        tags_in_db: List[Dict[str, Any]] = DB.get("Tags", [])
        for tag_item in tags_in_db:
            if tag_item.get("repository_id") == repo_id and tag_item.get("name") == ref_to_resolve:
                commit_info = tag_item.get("commit")
                if isinstance(commit_info, dict):
                    commit_sha = commit_info.get("sha")
                break

    # If not resolved as a branch or tag, try to resolve ref_to_resolve as a commit SHA
    if commit_sha is None:
        commits_in_db: List[Dict[str, Any]] = DB.get("Commits", [])
        for commit_item in commits_in_db:
            if commit_item.get("repository_id") == repo_id and commit_item.get("sha") == ref_to_resolve:
                commit_sha = ref_to_resolve
                # actual_ref_name_for_key is already ref_to_resolve (the SHA string)
                break

    if commit_sha is None:
        is_known_branch_commit = False
        for branch_item_again in branches_in_db: # Re-check branches for the SHA itself
            if branch_item_again.get("repository_id") == repo_id:
                commit_info_again = branch_item_again.get("commit")
                if isinstance(commit_info_again, dict) and commit_info_again.get("sha") == ref_to_resolve:
                    commit_sha = ref_to_resolve # The ref itself is a known commit SHA from a branch
                    is_known_branch_commit = True
                    break
        if not is_known_branch_commit:
            raise custom_errors.NotFoundError(f"Ref '{ref_for_display}' does not exist or could not be resolved to a commit in repository '{repo_full_name}'.")

    # Ensure commit_sha is resolved, vital for the new key format
    if commit_sha is None:
        raise custom_errors.NotFoundError(f"Could not resolve ref '{ref_for_display}' to a valid commit SHA for repository '{repo_full_name}'.")


    # Construct Key for DB["FileContents"]
    # Handle root directory case - convert "/" to empty string for DB key (as that's how it's stored)
    if path == "/":
        path_for_key = ""  # Root directory is stored with empty string key
    else:
        path_for_key = path.strip('/')  # Handle other paths normally

    # Use the format: f"{repository_id}:{commit_sha}:{file_or_dir_path}"
    content_key = f"{repo_id}:{commit_sha}:{path_for_key}"
    
    # Retrieve content from database
    file_contents_map: Dict[str, Any] = DB.get("FileContents", {})

    # Retrieve Content
    content_data = file_contents_map.get(content_key)

    if content_data is None:
        # For root directory, return empty list if not found (empty repository)
        if path == "/":
            return []
        else:
            # Try to dynamically generate directory listing by looking for files that start with this path
            directory_contents = []
            path_prefix = f"{repo_id}:{commit_sha}:{path_for_key}/"
            
            # Find all files/directories that start with this path
            for key, value in file_contents_map.items():
                if key.startswith(path_prefix):
                    # Extract the relative path after our directory
                    relative_path = key[len(path_prefix):]
                    
                    # Only include direct children (no nested paths)
                    if '/' not in relative_path:
                        if isinstance(value, dict):
                            # It's a file
                            directory_contents.append({
                                'type': value.get('type', 'file'),
                                'size': value.get('size', 0),
                                'name': value.get('name', relative_path),
                                'path': value.get('path', f"{path_for_key}/{relative_path}" if path_for_key else relative_path),
                                'sha': value.get('sha', '')
                            })
                    else:
                        # It's a subdirectory - extract just the directory name
                        subdir_name = relative_path.split('/')[0]
                        # Check if we already added this subdirectory
                        if not any(item['name'] == subdir_name and item['type'] == 'dir' for item in directory_contents):
                            directory_contents.append({
                                'type': 'dir',
                                'size': 0,
                                'name': subdir_name,
                                'path': f"{path_for_key}/{subdir_name}" if path_for_key else subdir_name,
                                'sha': ''  # We could generate a placeholder SHA if needed
                            })
            
            # If we found contents, return them; otherwise, raise the original error
            if directory_contents:
                return directory_contents
            else:
                raise custom_errors.NotFoundError(f"Path '{path}' (key: '{content_key}') not found at ref '{ref_for_display}' (commit: {commit_sha}) in repository '{repo_full_name}'.")

    # Handle directory content (list) vs file content (dict)
    if isinstance(content_data, list):
        # Directory content - return as-is (list of file/directory entries)
        return content_data
    elif isinstance(content_data, dict):
        # File content - format the response to match GitHub API expectations
        response_data = content_data.copy()
        
        # If content is stored as text, convert to base64 for API response
        if content_data.get("encoding") == "text":
            text_content = content_data.get("content", "")
            base64_content = base64.b64encode(text_content.encode('utf-8')).decode('utf-8')
            response_data["content"] = base64_content
            response_data["encoding"] = "base64"

        return response_data
    else:
        # Unexpected content type
        raise custom_errors.NotFoundError(f"Invalid content type for path '{path}' in repository '{repo_full_name}'.")

def search_code(
    query: str,
    sort: str = 'best match',
    order: str = 'desc',
    page: int = 1,
    per_page: int = 30
) -> Dict[str, Any]:
    """Search for code within repositories.

    Searches for query terms inside of files. This method returns up to 100 results per page.
    The query can contain any combination of search keywords and qualifiers.

    Note: Due to the complexity of searching code, there are a few restrictions:
    - Only the default branch is considered. In most cases, this will be the master branch.
    - Only files smaller than 384 KB are searchable.
    - You must always include at least one search term when searching source code.
      For example, searching for language:go is not valid, while amazing language:go is.

    Args:
        query (str): The search query string. Can contain any combination of search keywords and qualifiers.
            Examples:
            - `"addClass in:file language:js repo:jquery/jquery"`: Find files containing 'addClass' in the jquery/jquery repository
            - `"repo:octocat/Spoon-Knife css"`: Find instances of 'css' in the octocat/Spoon-Knife repository
            - `"shogun user:heroku language:ruby"`: Find 'shogun' in Ruby files from heroku's repositories
            - `"function size:>10000 language:python"`: Find Python files containing 'function' larger than 10 KB
            
            Supported qualifiers:
            - `in:file,path`: Search in file contents and/or file paths. If not specified, searches in both.
            - `language:LANGUAGE`: Filter by programming language (based on file extension).
                Supported languages: javascript (js), python (py), ruby (rb), go, java, c++ (cpp),
                typescript (ts), php, c# (cs), html, css, shell (sh), markdown (md).
            - `repo:owner/repository`: Restrict search to a specific repository.
            - `user:USERNAME`, `org:USERNAME`: Search within a user's or organization's repositories.
            - `size:n`: Filter by file size (in bytes). Can use `>`, `<`, `>=`, `<=`, and `..` ranges.
            - `path:PATH`: Filter by file path.
            - `extension:EXTENSION`: Filter by file extension.
            - `is:public`, `is:private`: Filter by repository visibility.
            - `fork:true`, `fork:only`: Include forked repositories in the search.
        sort (str): This field is closing down. Can only be 'indexed', which indicates how recently a file has been indexed.
            Default is 'best match'.
        order (str): This field is closing down. The direction to sort. Can be 'asc' or 'desc'.
            Only used when 'sort' is specified. Default is 'desc'.
        page (int): Page number of the results to fetch. Default is 1.
        per_page (int): The number of results per page (max 100). Default is 30.

    Returns:
        Dict[str, Any]: A dictionary containing the search results with the following keys:
            total_count (int): The total number of matching files found.
            incomplete_results (bool): Indicates if the search timed out before finding all results.
            items (List[Dict[str, Any]]): A list of code search result items. Each item contains:
                name (str): The name of the file.
                path (str): The path of the file within the repository.
                sha (str): The SHA (blob) of the file.
                url (str): The API URL to get the file contents.
                git_url (str): The git blob URL.
                html_url (str): The URL to view the file in a web browser.
                repository (Dict[str, Any]): Details about the repository containing the file:
                    id (int): The repository ID.
                    node_id (str): The global node ID of the repository.
                    name (str): The repository name.
                    full_name (str): The full name of the repository (owner/repo).
                    owner (Dict[str, Any]): Details about the repository owner:
                        login (str): The owner's username.
                        id (int): The owner's ID.
                        node_id (str): The owner's global node ID.
                        type (str): The type of owner (User/Organization).
                        site_admin (bool): Whether the owner is a site admin.
                    private (bool): Whether the repository is private.
                    description (str): The repository description.
                    fork (bool): Whether the repository is a fork.
                score (float): The search relevance score.

    Raises:
        InvalidInputError: If the search query is missing or invalid, or if pagination parameters are malformed, not positive integers, or out of acceptable range.
        RateLimitError: If the request exceeds the rate limit. Rate limits for search API:
            - Authenticated requests: 30 requests per minute
            - Unauthenticated requests: 10 requests per minute
    """
    # --- Rate Limit Check ---
    # Check if rate limit simulation is enabled
    if DB.get('simulate_rate_limit_for_code_search', False):
        raise custom_errors.RateLimitError("API rate limit exceeded")

    # Check actual rate limit
    rate_limit = DB.get('RateLimit', {}).get('search', {})
    if rate_limit:
        remaining = rate_limit.get('remaining', 0)
        if remaining <= 0:
            reset_time = rate_limit.get('reset_at')
            raise custom_errors.RateLimitError(
                f"API rate limit exceeded. Reset at {reset_time}"
            )

    # --- Input Validation ---
    if not query or not isinstance(query, str):
        raise custom_errors.InvalidInputError("Search query must be a non-empty string.")

    # --- Query Parsing ---
    # First handle quoted terms
    quoted_terms = []
    remaining_query = query
    quote_pattern = re.compile(r'"([^"]*)"')
    
    while True:
        match = quote_pattern.search(remaining_query)
        if not match:
            break
        quoted_term = match.group(1).strip()  # Get the content between quotes and strip whitespace
        if quoted_term:  # Only add non-empty terms
            quoted_terms.append(quoted_term)
        # Remove the quoted term from the query
        start, end = match.span()
        remaining_query = remaining_query[:start] + ' ' + remaining_query[end:]
    
    # Split remaining query into parts
    parts = [part.strip() for part in remaining_query.split() if part.strip()]
    
    # Check for mismatched quotes
    if '"' in ''.join(parts):
        raise custom_errors.InvalidInputError("Invalid query syntax: Mismatched quotes.")

    # Process qualifiers and search terms
    qualifiers = {}
    qualifier_pattern = re.compile(r'(\w+):(.*)')
    individual_terms = []

    for part in parts:
        match = qualifier_pattern.match(part)
        if match:
            key, value = match.groups()
            qualifiers[key.lower()] = value
        else:
            individual_terms.append(part.lower())

    # Combine both types of terms for validation
    search_terms = quoted_terms + individual_terms
    if not search_terms:
        raise custom_errors.InvalidInputError(
            "Code search must include at least one search term."
        )

    # Validate pagination parameters
    if not isinstance(page, int) or page < 1:
        raise custom_errors.InvalidInputError("Page must be a positive integer.")
    if not isinstance(per_page, int) or not 1 <= per_page <= 100:
        raise custom_errors.InvalidInputError("per_page must be an integer between 1 and 100.")

    # Validate sort and order parameters
    if sort != 'best match' and sort != 'indexed':
        raise custom_errors.InvalidInputError("Sort can only be 'indexed' or 'best match'.")

    valid_order_values = ['asc', 'desc']
    if order not in valid_order_values:
        raise custom_errors.InvalidInputError(
            f"Invalid 'order' parameter. Must be one of {valid_order_values}."
        )

    # --- Data Fetching and Filtering ---
    all_code_results = DB.get('CodeSearchResultsCollection', [])
    file_contents = DB.get('FileContents', {})
    filtered_results = []
    seen_files = set()  # Track unique files to avoid duplicates

    # Get all repositories to find default branch commits
    repositories = DB.get('Repositories', [])
    repo_default_commits = {}
    for repo in repositories:
        # Find the most recent commit on the default branch
        branches = DB.get('Branches', [])
        default_branch = next(
            (b for b in branches if b.get('repository_id') == repo['id'] and b['name'] == repo.get('default_branch', 'main')),
            None
        )
        if default_branch and default_branch.get('commit', {}).get('sha'):
            repo_default_commits[repo['id']] = default_branch['commit']['sha']

    # Determine search scope
    search_in = qualifiers.get('in', 'file,path').lower().split(',')
    search_in_file = 'file' in search_in
    search_in_path = 'path' in search_in

    # Language extension mapping
    lang_map = {
        'js': 'javascript',
        'py': 'python',
        'rb': 'ruby',
        'go': 'go',
        'java': 'java',
        'cpp': 'c++',
        'ts': 'typescript',
        'php': 'php',
        'cs': 'c#',
        'html': 'html',
        'css': 'css',
        'sh': 'shell',
        'md': 'markdown'
    }
    # Reverse mapping for language names to extensions
    ext_map = {v: k for k, v in lang_map.items()}

    for result in all_code_results:
        match = True
        
        # Get file key for content lookup
        repo_id = result['repository']['id']
        commit_sha = repo_default_commits.get(repo_id)
        if not commit_sha:
            continue
        file_key = f"{repo_id}:{commit_sha}:{result['path']}"
        
        # Skip if we've already seen this file
        unique_file_key = f"{result['repository']['full_name']}:{result['path']}"
        if unique_file_key in seen_files:
            continue
        
        # Check file size limit first - files larger than 384KB are not searchable
        file_data = file_contents.get(file_key, {})
        file_size = file_data.get('size', 0)
        if file_size > 393216:  # 384KB in bytes
            continue

        # Apply qualifiers first
        for key, value in qualifiers.items():
            if key == 'language':
                # Get file extension
                file_ext = result['name'].split('.')[-1].lower() if '.' in result['name'] else ''
                value_lower = value.lower()
                
                # Check if value is a language name
                if value_lower in ext_map:
                    if file_ext != ext_map[value_lower]:
                        match = False
                        break
                # Check if value is a file extension
                elif value_lower in lang_map:
                    if file_ext != value_lower:
                        match = False
                        break
                else:
                    match = False
                    break
            elif key == 'repo':
                if result['repository']['full_name'].lower() != value.lower():
                    match = False
                    break
            elif key == 'user' or key == 'org':
                owner = result['repository']['owner']['login'].lower()
                if owner != value.lower():
                    match = False
                    break
            elif key == 'path':
                if value.lower() not in result['path'].lower():
                    match = False
                    break
            elif key == 'extension':
                if not result['name'].lower().endswith(f'.{value.lower()}'):
                    match = False
                    break
            elif key == 'size':
                try:
                    if '..' in value:
                        min_size, max_size = map(int, value.split('..'))
                        if not (min_size <= file_size <= max_size):
                            match = False
                            break
                    elif value.startswith('>='):
                        min_size = int(value[2:])
                        if file_size < min_size:
                            match = False
                            break
                    elif value.startswith('<='):
                        max_size = int(value[2:])
                        if file_size > max_size:
                            match = False
                            break
                    elif value.startswith('>'):
                        min_size = int(value[1:])
                        if file_size <= min_size:
                            match = False
                            break
                    elif value.startswith('<'):
                        max_size = int(value[1:])
                        if file_size >= max_size:
                            match = False
                            break
                    else:
                        exact_size = int(value)
                        if file_size != exact_size:
                            match = False
                            break
                except ValueError:
                    match = False
                    break
            elif key == 'is':
                value_lower = value.lower()
                if value_lower == 'public':
                    if result['repository'].get('private', False):
                        match = False
                        break
                elif value_lower == 'private':
                    if not result['repository'].get('private', False):
                        match = False
                        break
            elif key == 'fork':
                value_lower = value.lower()
                if value_lower == 'true':
                    # Include both forked and non-forked repos
                    pass
                elif value_lower == 'only':
                    if not result['repository'].get('fork', False):
                        match = False
                        break
                else:
                    # Default behavior: exclude forks
                    if result['repository'].get('fork', False):
                        match = False
                        break

        if not match:
            continue

        # Check if any search term matches
        found_match = True  # Changed to True by default
        repo_text = (
            f"{result['repository']['name']} "
            f"{result['repository'].get('description', '')}"
        ).lower()

        # Check if ALL terms match in at least one location
        for term in search_terms:
            term_lower = term.lower()
            term_found = False
            
            # Check repository metadata
            if term_lower in repo_text:
                term_found = True
            
            # Check file path if enabled
            elif search_in_path and term_lower in result['path'].lower():
                term_found = True
            
            # Check file content if enabled
            elif search_in_file:
                file_content = file_data.get('content', '').lower()
                if file_content and term_lower in file_content:
                    term_found = True
                else:
                    # Check patch content if available
                    patch = file_data.get('patch', '')
                    if patch:
                        # Remove diff markers and headers
                        clean_patch = '\n'.join(
                            line for line in patch.split('\n')
                            if not line.startswith(('@@ ', '--- ', '+++ '))
                        ).lower()
                        if term_lower in clean_patch:
                            term_found = True
            
            # If this term wasn't found anywhere, the result doesn't match
            if not term_found:
                found_match = False
                break

        if found_match:
            # Format the result
            formatted_result = {
                'name': result['name'],
                'path': result['path'],
                'sha': result['sha'],
                'url': f"https://api.github.com/repositories/{repo_id}/contents/{result['path']}",
                'git_url': f"https://api.github.com/repositories/{repo_id}/git/blobs/{result['sha']}",
                'html_url': f"https://github.com/{result['repository']['full_name']}/blob/master/{result['path']}",
                'repository': result['repository'],
                'score': result.get('score', 1.0)
            }
            filtered_results.append(formatted_result)
            seen_files.add(unique_file_key)

    # Sort results
    if sort == 'indexed':
        filtered_results.sort(key=lambda x: x['sha'], reverse=(order == 'desc'))
    else:  # 'best match'
        filtered_results.sort(key=lambda x: x['score'], reverse=True)

    # Apply pagination
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_results = filtered_results[start_idx:end_idx]

    return {
        'total_count': len(filtered_results),
        'incomplete_results': False,
        'items': paginated_results
    }
