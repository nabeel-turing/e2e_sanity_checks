from pydantic import ValidationError
from typing import Dict, Any, Optional
from .SimulationEngine import custom_errors
from .SimulationEngine.db import DB
from .SimulationEngine.utils import _get_raw_item_by_id
import re
import shlex


def get_me() -> Dict[str, Any]:
    """Get details of the authenticated user.

    Gets details of the authenticated user.

    Returns:
        Dict[str, Any]: A dictionary containing the authenticated user's details with the following keys:
            login (str): The user's username.
            id (int): The unique ID of the user.
            node_id (str): The global node ID of the user.
            name (Optional[str]): The user's full name.
            email (Optional[str]): The user's publicly visible email address.
            company (Optional[str]): The user's company.
            location (Optional[str]): The user's location.
            bio (Optional[str]): The user's biography.
            public_repos (int): The number of public repositories.
            public_gists (int): The number of public gists.
            followers (int): The number of followers.
            following (int): The number of users the user is following.
            created_at (str): ISO 8601 timestamp for when the account was created.
            updated_at (str): ISO 8601 timestamp for when the account was last updated.
            type (str): The type of account, e.g., 'User' or 'Organization'.

    Raises:
        AuthenticationError: If the request is not authenticated or if the authenticated user cannot be found.
    """
    authenticated_user_id = DB.get('CurrentUser').get('id')

    if authenticated_user_id is None:
        raise custom_errors.AuthenticationError("User is not authenticated.")
    
    user_data = _get_raw_item_by_id(DB, "Users", authenticated_user_id)

    if user_data is None:
        raise custom_errors.AuthenticationError(f"Authenticated user with ID {authenticated_user_id} not found.")
    
    return_data = {
        'login': user_data.get('login'),
        'id': user_data.get('id'),
        'node_id': user_data.get('node_id'),
        'name': user_data.get('name'),
        'email': user_data.get('email'),
        'company': user_data.get('company'),
        'location': user_data.get('location'),
        'bio': user_data.get('bio'),
        'public_repos': user_data.get('public_repos'),
        'public_gists': user_data.get('public_gists'),
        'followers': user_data.get('followers'),
        'following': user_data.get('following'),
        'created_at': user_data.get('created_at'),
        'updated_at': user_data.get('updated_at'),
        'type': user_data.get('type'),
    }
    return return_data


def search_users(q: str, sort: Optional[str] = None, order: str = "desc", page: int = 1, per_page: int = 30) -> Dict[str, Any]:
    """Search for GitHub users.

    Find users via various criteria. This method returns up to 100 results per page.
    The query can contain any combination of search keywords and qualifiers to narrow down the results.

    When no sort is specified, results are sorted by best match.

    Args:
        q (str): The search query string. Can contain any combination of search keywords and qualifiers.
            For example: `q=tom+repos:>42+followers:>1000`.
            Supported qualifiers:
            - `in:login,name,email`: Restricts search to specified fields.
            - `repos:n`: Filters by repository count. Can use `>`, `<`, `>=`, `<=`, and `..` ranges.
            - `followers:n`: Filters by follower count. Can use `>`, `<`, `>=`, `<=`, and `..` ranges.
            - `created:YYYY-MM-DD`: Filters by creation date. Can use `>`, `<`, `>=`, `<=`, and `..` ranges.
            - `location:LOCATION`: Filters by location in the user's profile.
            - `type:user|org`: Restricts search to users or organizations.
            - `language:LANGUAGE`: Filters by the predominant language in the user's repositories.
        sort (Optional[str]): The field to sort the search results by. Can be one of 'followers', 'repositories', 'joined'.
            Defaults to 'None' (best match).
        order (str): The order of sorting ('asc' or 'desc'). Defaults to 'desc'.
        page (int): The page number for paginated results. Defaults to 1.
        per_page (int): The number of results to return per page (max 100). Defaults to 30.

    Returns:
        Dict[str, Any]: A dictionary containing user search results with the following keys:
            total_count (int): The total number of users found.
            incomplete_results (bool): Indicates if the search timed out before finding all results.
            items (List[Dict[str, Any]]): A list of user objects matching the search criteria. Each user object in the list has the following fields:
                login (str): The user's username.
                id (int): The unique ID of the user.
                node_id (str): The global node ID of the user.
                type (str): The type of account, e.g., 'User' or 'Organization'.
                score (float): The search score associated with the user.

    Raises:
        InvalidInputError: If the search query 'q' is missing or invalid, or if pagination parameters are incorrect.
        RateLimitError: If the API rate limit is exceeded.
    """

    # --- Input Validation ---
    if not q or not q.strip():
        raise custom_errors.InvalidInputError("Search query 'q' cannot be empty.")

    valid_sort_fields = ['followers', 'repositories', 'joined']
    if sort is not None and sort not in valid_sort_fields:
        raise custom_errors.InvalidInputError(
            f"Invalid 'sort' parameter. Must be one of {valid_sort_fields}."
        )

    valid_order_values = ['asc', 'desc']
    if order not in valid_order_values:
        raise custom_errors.InvalidInputError(
            f"Invalid 'order' parameter. Must be 'asc' or 'desc'."
        )

    if page is not None:
        if not isinstance(page, int) or page < 1:
            raise custom_errors.InvalidInputError(
                "Page number must be a positive integer."
            )
    
    if per_page is not None:
        if not isinstance(per_page, int) or per_page < 1:
            raise custom_errors.InvalidInputError(
                "Results per page must be a positive integer."
            )
        if per_page > 100:
            # This limit is common in APIs like GitHub's.
            raise custom_errors.InvalidInputError("Maximum 'per_page' is 100.")

    # --- Data Fetching and Filtering ---
    all_users_from_db = DB.get('Users', [])

    # Parse the query 'q' for search terms and qualifiers
    try:
        parts = shlex.split(q)
    except ValueError:
        raise custom_errors.InvalidInputError("Invalid query syntax: Mismatched quotes.")

    search_terms = []
    qualifiers = {}
    
    qualifier_pattern = re.compile(r'(\w+):(.*)')

    for part in parts:
        match = qualifier_pattern.match(part)
        if match:
            key, value = match.groups()
            qualifiers[key.lower()] = value
        else:
            search_terms.append(part.lower())

    # Filter users based on qualifiers and search terms
    matched_users = []
    for user_data in all_users_from_db:
        # Check qualifiers
        qualifiers_match = True
        for key, value in qualifiers.items():
            field_map = {
                'repos': 'public_repos',
                'followers': 'followers',
                'location': 'location',
                'type': 'type',
                'language': 'language', # Assumes a 'language' field from a repo aggregation
                'created': 'created_at',
            }
            
            # The 'in' qualifier is handled with search terms, not here.
            if key == 'in' or key not in field_map:
                continue

            field_name = field_map[key]
            user_value = user_data.get(field_name)

            # --- Type and Location Check (Exact Match) ---
            if key in ['type', 'location']:
                # Strip quotes for location search
                if not user_value or value.strip('"').lower() not in user_value.lower():
                    qualifiers_match = False
                    break
                continue
            
            # --- Date Check ---
            if key == 'created' and user_value:
                # Naive implementation: assuming YYYY-MM-DD format and string comparison
                # A more robust solution would parse dates properly.
                if value.startswith('<='):
                    if not user_value <= value[2:]: qualifiers_match = False
                elif value.startswith('>='):
                    if not user_value >= value[2:]: qualifiers_match = False
                elif value.startswith('<'):
                    if not user_value < value[1:]: qualifiers_match = False
                elif value.startswith('>'):
                    if not user_value > value[1:]: qualifiers_match = False
                elif '..' in value:
                    low, high = value.split('..')
                    if not (low <= user_value <= high): qualifiers_match = False
                else: # exact date match
                    if not user_value.startswith(value): qualifiers_match = False
                if not qualifiers_match: break
                continue

            # --- Numeric Check (repos, followers) ---
            if key in ['repos', 'followers']:
                numeric_user_value = user_data.get(field_map[key], 0)
                
                # Range check (e.g., 10..50)
                if '..' in value:
                    low_str, high_str = value.split('..')
                    low = int(low_str) if low_str != '*' else float('-inf')
                    high = int(high_str) if high_str != '*' else float('inf')
                    if not (low <= numeric_user_value <= high):
                        qualifiers_match = False
                else:
                    # Inequality check (e.g., >10, <=50)
                    op_match = re.match(r'([<>]?=?)(.*)', value)
                    if op_match:
                        op, num_str = op_match.groups()
                        num = int(num_str)
                        
                        if op == '>' and not numeric_user_value > num: qualifiers_match = False
                        elif op == '>=' and not numeric_user_value >= num: qualifiers_match = False
                        elif op == '<' and not numeric_user_value < num: qualifiers_match = False
                        elif op == '<=' and not numeric_user_value <= num: qualifiers_match = False
                        elif op == '' and not numeric_user_value == num: qualifiers_match = False
                    
                if not qualifiers_match:
                    break

        if not qualifiers_match:
            continue

        # Check search terms (against login, name, email based on 'in' qualifier)
        search_fields = ['login', 'name', 'email'] # Default
        if 'in' in qualifiers:
            # Map 'in' value to fields, e.g., in:login,email
            fields_to_search = qualifiers['in'].split(',')
            # Ensure only valid fields are used
            search_fields = [f for f in fields_to_search if f in ['login', 'name', 'email']]

        term_match = False
        if not search_terms:
            term_match = True  # No terms to match, so qualifier match is sufficient
        else:
            for term in search_terms:
                for field in search_fields:
                    if term in user_data.get(field, '' or None).lower():
                        term_match = True
                        break
                if term_match:
                    break
        
        if term_match:
            matched_users.append(user_data)
            
    total_count = len(matched_users)

    # --- Sorting ---
    if sort is None:
        # Default sort by "best match" (score)
        matched_users.sort(key=lambda u: u.get('score', 0), reverse=True)
    else:
        # Map API sort fields to internal DB field names.
        # Assumes these fields exist in the user_data dictionaries if sorting is requested.
        sort_key_map = {
            'followers': 'followers',
            'repositories': 'public_repos',
            'joined': 'created_at'  # Assumed to be an ISO 8601 date string for lexicographical sort.
        }
        sort_field_in_db = sort_key_map[sort]
        
        # Determine sort order: 'desc' by default if 'order' is not 'asc'.
        # This means if 'order' is None (default) or 'desc', sorting is descending.
        is_reverse_sort = (order != 'asc')
        
        # This sort operation assumes that if a sort field is specified,
        # all user_data dictionaries in matched_users contain that field with comparable values.
        # A KeyError will be raised if a field is missing, indicating data inconsistency.
        # A TypeError may occur if field values are not comparable (e.g. mixing None and str).
        # Handle potential None values in sort keys
        matched_users.sort(
            key=lambda u: u.get(sort_field_in_db, 0 if sort_field_in_db != 'created_at' else ''), 
            reverse=is_reverse_sort
        )


    # --- Pagination ---
    # Apply default pagination parameters if not provided, similar to GitHub API behavior.
    current_page = page if page is not None else 1
    # If per_page was None, it defaults to 30. If it was specified, it was already validated.
    items_per_page = per_page if per_page is not None else 30 

    start_index = (current_page - 1) * items_per_page
    end_index = start_index + items_per_page
    paginated_users_data = matched_users[start_index:end_index]

    # --- Formatting Output ---
    response_items = []
    for user_data in paginated_users_data:
        # Transform raw user data to the specified output item structure.
        # Assumes 'login', 'id', 'node_id', 'type' fields exist in user_data.
        # A KeyError will be raised if any of these essential fields are missing.
        item = {
            'login': user_data['login'],
            'id': user_data['id'],
            'node_id': user_data['node_id'],
            'type': user_data['type'],
            'score': user_data.get('score', 1.0)  # Assign a fixed search score as per typical search result structures.
        }
        response_items.append(item)


    # Construct the final response dictionary.
    return {
        'total_count': total_count,
        'incomplete_results': False,  # No timeout simulation is implemented for this function.
        'items': response_items
    }
