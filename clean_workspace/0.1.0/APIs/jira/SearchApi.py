from .SimulationEngine.db import DB
from .SimulationEngine.jql_service import jql_service
from .SimulationEngine.search_engine import search_engine_manager

from typing import Optional, List, Dict, Any
import re


def search_issues(
    jql: str = "",
    start_at: Optional[int] = 0,
    max_results: Optional[int] = 50,
    fields: Optional[List[str]] = None,
    expand: Optional[List[str]] = None,
    validate_query: Optional[bool] = True,
) -> Dict[str, Any]:
    """
    Search for issues based on JQL query.

    Args:
        jql (str): The JQL query to search for issues.
                   Strings with spaces must be enclosed in single (') or double (") quotes.
                   Commonly searchable fields include:
                   - `id` / `key` (e.g., `id = "ISSUE-123"`)
                   - `project` (e.g., `project = "DEMO"`)
                   - `summary` (e.g., `summary ~ "critical bug"` or `summary = "Exact phrase"`)
                   - `description` (e.g., `description ~ "detailed steps"`)
                   - `priority` (e.g., `priority = "High"`)
                   - `assignee`:
                       - The `assignee` field is stored as a dictionary with a `name` field (e.g., `{"name": "jdoe"}`), but can be queried directly using the username: `assignee = "jdoe"`.
                       - The JQL parser automatically extracts the `name` field from the assignee dictionary for comparison.
                       - The `name` field corresponds to the user's `name` field from the users table (not email or display name).
                       - Dot notation queries (e.g., `assignee.name = "jdoe"`) are **NOT supported** by the current JQL parser.
                   - `created` (e.g., `created >= "2024-01-01"`)
                   - `issuetype` (e.g., `issuetype = "Bug"`)
                   - `status` (e.g., `status = "Open"`)

                   Supported operators:
                   - `=` (equals), `!=` (not equals)
                   - `~` (contains), `!~` (does not contain)
                   - `<`, `<=`, `>`, `>=` (comparison operators for dates/numbers)
                   - `IN` (e.g., `priority IN ("High", "Critical")`)
                   - `NOT IN` (e.g., `status NOT IN ("Closed", "Done")`)
                   - `IS EMPTY`, `IS NOT EMPTY` (for null/empty checks)
                   - `IS NULL`, `IS NOT NULL` (aliases for empty checks)
                   - `EMPTY`, `NULL` (legacy empty checks)

                   Combining conditions:
                   - Use `AND` and `OR` for multiple conditions (e.g., `project = "WebApp" AND status = "Open" OR priority = "High"`).
                   - `AND` has higher precedence than `OR`.
                   - Parentheses `()` for explicit grouping of conditions are supported (e.g., `(project = "WebApp" OR project = "API") AND status = "Open"`).

                   Ordering results:
                   - Use `ORDER BY fieldName [ASC|DESC]` (e.g., `ORDER BY created DESC`).

                   The exact fields and operators supported depend on the JQL parsing and evaluation logic implemented in the simulation.
        start_at (Optional[int]): The index of the first issue to return. Defaults to 0.
        max_results (Optional[int]): The maximum number of issues to return. Defaults to 50.
        fields (Optional[List[str]]): A list of fields to return. Defaults to None (all fields).
        expand (Optional[List[str]]): A list of fields to expand. Defaults to None.
        validate_query (Optional[bool]): Whether to validate the JQL query. Defaults to True.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - issues (List[Dict[str, Any]]): A list of issues
                - id (str): The id of the issue.
                - fields (Dict[str, Any]): The fields of the issue.
                    - project (str): The project key
                    - summary (str): Issue summary
                    - description (str): Issue description
                    - priority (str): The priority of the issue
                    - assignee (Dict[str, str]): Assignee information
                        - name (str): The assignee's username (e.g., 'jdoe')
                    - created (str): Creation timestamp
            - startAt (int): The index of the first issue to return.
            - maxResults (int): The maximum number of issues to return.
            - total (int): The total number of issues.

    Raises:
        TypeError: If any argument has an invalid type (e.g., jql is not a string,
                   start_at is not an int/None, fields is not a list/None, etc.).
        ValueError: If any argument has an invalid value (e.g., negative start_at or max_results,
                    or non-string elements in fields/expand lists).
    """
    # --- Input Validation ---
    if not isinstance(jql, str):
        raise TypeError("jql must be a string.")

    if start_at is not None:  # Default is 0, an int.
        if not isinstance(start_at, int):
            raise TypeError("start_at must be an integer or None.")
        if start_at < 0:
            raise ValueError("start_at must be non-negative.")

    # Actual value to use for start_at after considering None and default
    current_start_at = 0 if start_at is None else start_at

    if max_results is not None:  # Default is 50, an int.
        if not isinstance(max_results, int):
            raise TypeError("max_results must be an integer or None.")
        if max_results < 0:
            raise ValueError("max_results must be non-negative.")

    # Actual value to use for max_results after considering None and default
    current_max_results = 50 if max_results is None else max_results

    if fields is not None:  # Default is None
        if not isinstance(fields, list):
            raise TypeError("fields must be a list of strings or None.")
        if not all(isinstance(field_item, str) for field_item in fields):
            raise ValueError("All elements in 'fields' must be strings.")

    if expand is not None:  # Default is None
        if not isinstance(expand, list):
            raise TypeError("expand must be a list of strings or None.")
        if not all(isinstance(expand_item, str) for expand_item in expand):
            raise ValueError("All elements in 'expand' must be strings.")

    if validate_query is not None:  # Default is True, a bool
        if not isinstance(validate_query, bool):
            raise TypeError("validate_query must be a boolean or None.")
    # --- End of Input Validation ---

    # Use JQL service to handle JQL parsing and coordinate with generic search strategies
    # The JQL service will parse JQL, use appropriate search strategies, and apply JQL conditions
    current_strategy = search_engine_manager.get_current_strategy_name()
    all_issues = jql_service.search_issues(
        jql=jql,
        strategy_name=current_strategy,  # Use current strategy from engine manager
        limit=None,  # Don't limit at the service level, we'll handle pagination here
        additional_filters=None
    )

    # Apply pagination
    total = len(all_issues)
    # Use current_start_at and current_max_results which account for None inputs and defaults
    end_index = current_start_at + current_max_results
    paged_issues = all_issues[current_start_at:end_index]

    return {
        "issues": paged_issues,
        "startAt": current_start_at,
        "maxResults": current_max_results,
        "total": total,
    }
