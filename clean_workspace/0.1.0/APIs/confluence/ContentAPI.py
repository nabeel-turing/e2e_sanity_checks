from typing import Dict, List, Optional, Any, TypedDict, Set
from confluence.SimulationEngine.custom_errors import ContentNotFoundError, ContentStatusMismatchError, \
    InvalidInputError, FileAttachmentError, LabelNotFoundError, ValidationError
from confluence.SimulationEngine.models import UpdateContentBodyInputModel
from pydantic import ValidationError as PydanticValidationError
from confluence.SimulationEngine.utils import get_iso_timestamp
from confluence.SimulationEngine.custom_errors import InvalidPaginationValueError, InvalidParameterValueError, InvalidPaginationValueError, ParentContentNotFoundError

from confluence.SimulationEngine.db import DB
from confluence.SimulationEngine.models import ContentInputModel
from confluence.SimulationEngine.utils import _evaluate_cql_tree, _collect_descendants
import re
import copy
import os
from datetime import datetime, timezone

def create_content(body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Creates new content.

    This function creates a new content item (page, blogpost, comment, etc.) with the specified
    details and stores it in the database. It handles both basic content creation and special
    cases like comments with ancestor relationships.

    Args:
        body (Dict[str, Any]): Dictionary containing content details
            Required fields:
                - type (str): Content type (e.g., 'page', 'blogpost', 'comment')
                - title (str): Content title
                - spaceKey (str): Space key where content will be created
            Optional fields:
                - status (str): Content status (default: 'current')
                - version (Dict): Content version object with 'number' key
                    - number (int): Version number (default: 1)
                    - minorEdit (bool): Flag indicating a minor edit (default: False)
                - body (Dict): Content body with storage format, structured as:
                      - storage (Dict): A dictionary with:
                            - value (str): The content value in storage format.
                            - representation (str): The representation type (e.g., "storage")
                - createdBy (str): Username of the creator (default: 'unknown')
                - postingDay (Optional[str]): Posting day for blog posts in "YYYY-MM-DD" format

    Returns:
        Dict[str, Any]: A dictionary containing the created content details with keys:
            - id (str): Unique identifier for the content.
            - type (str): Content type.
            - title (str): Content title.
            - spaceKey (str): Space key.
            - status (str): Content status.
            - version (Dict): Content version object with keys:
                  - number (int): Version number.
                  - minorEdit (bool): Minor edit flag.
            - body (Dict): Content body.
            - createdBy (str): Username of the creator.
            - postingDay (Optional[str]): Posting day for blog posts (if provided).


    Raises:
        pydantic.ValidationError: If the input `body` dictionary does not conform to the
                                  ContentInputModel schema (e.g., missing required fields,
                                  incorrect types, invalid format for postingDay).
        MissingCommentAncestorsError: If `type` is 'comment' and `ancestors` list is missing or empty.
        ParentContentNotFoundError: If a parent content ID specified in `ancestors` for a comment
                                    is not found in the database.
    """
    try:
        validated_input = ContentInputModel.model_validate(body)
    except ValidationError as e:
        raise e

    # --- Original core logic starts here, adapted to use validated_input ---
    new_id = str(DB["content_counter"])
    DB["content_counter"] += 1

    # Build default content using validated data
    new_content = {
        "id": new_id,
        "type": validated_input.type,
        "spaceKey": validated_input.spaceKey,
        "title": validated_input.title,
        "status": validated_input.status,
        "body": validated_input.body.model_dump() if validated_input.body else {},
        "postingDay": validated_input.postingDay, # Will be None if not provided or explicitly None
        "link": os.path.join("/content", new_id),
    }

    # Extended behavior for comments
    if new_content["type"] == "comment":
        # The Pydantic model validator 'check_comment_ancestors' already ensures
        # validated_input.ancestors exists and is not empty if type is 'comment'.
        parent_id = validated_input.ancestors[0] # Get the immediate parent's id
        parent = DB["contents"].get(parent_id)
        if not parent:
            raise ParentContentNotFoundError(f"Parent content with ID '{parent_id}' not found.")

        complete_ancestors = []
        if "ancestors" in parent: # Parent itself might have ancestors
            for ancestor_id in parent["ancestors"]:
                ancestor = DB["contents"].get(ancestor_id)
                if ancestor:
                    complete_ancestors.append(copy.deepcopy(ancestor))
        complete_ancestors.append(copy.deepcopy(parent))
        new_content["ancestors"] = complete_ancestors # Store the resolved ancestor objects

        # Update the parent record:
        if "children" not in parent:
            parent["children"] = []
        parent["children"].append(copy.deepcopy(new_content)) # Add new comment as child
        DB["contents"][parent_id] = parent # Save updated parent

        # Cascade up: add the new comment to all ancestors' descendants
        for ancestor_content_obj in complete_ancestors: # Iterate through the resolved ancestor objects
            ancestor_id = ancestor_content_obj["id"]
            # Fetch the most current version of ancestor from DB to update
            current_ancestor_in_db = DB["contents"].get(ancestor_id)
            if current_ancestor_in_db:
                if "descendants" not in current_ancestor_in_db:
                    current_ancestor_in_db["descendants"] = []
                current_ancestor_in_db["descendants"].append(copy.deepcopy(new_content))
                DB["contents"][ancestor_id] = current_ancestor_in_db

    # Save new content in DB
    DB["contents"][new_id] = new_content
    return new_content

def get_content(
        id: str,
        status: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieves content by its unique identifier.

    This function fetches a content item from the database using its ID. It can optionally
    filter the content by its status to ensure the content matches the expected state.

    Args:
        id (str): The unique identifier of the content to retrieve. Must be a non-empty string.
        status (Optional[str]): The expected status of the content. If provided,
            the function will verify that the content's status matches this value.
            If set to "any", the status check is bypassed. Must be a string if provided.

    Returns:
        Dict[str, Any]: A dictionary containing the content details with keys:
            - id (str): Content identifier.
            - type (str): Content type.
            - title (str): Content title.
            - spaceKey (str): Internal space key.
            - status (str): Content status.
            - version (Dict[str, Any]): Content version object, which includes:
                  - number (int): Version number.
                  - minorEdit (bool): Flag indicating a minor edit.
            - body (Dict[str, Any]): Content body as a dictionary with the structure:
                  - storage (Dict[str, Any]): A dictionary containing:
                        - value (str): The actual content value.
                        - representation (str): The content representation format (e.g., "storage").
            - ancestors (Optional[List[str]]): List of ancestor IDs (for comments), if applicable.
            - postingDay (Optional[str]): Posting day for blog posts, if available.

    Raises:
        TypeError: If 'id' is not a string, or if 'status', 'version', or 'expand'
                   are provided but are not of their expected types (str, int, str respectively).
        InvalidInputError: If 'id' is an empty string.
        ContentNotFoundError: If the content with the specified ID is not found.
        ContentStatusMismatchError: If the content's status does not match the expected status.
    """
    # --- Input Validation ---
    if not isinstance(id, str):
        raise TypeError("Argument 'id' must be a string.")
    if not id:
        raise InvalidInputError("Argument 'id' cannot be an empty string.")

    if status is not None and not isinstance(status, str):
        raise TypeError("Argument 'status' must be a string if provided.")

    content = DB["contents"].get(id)
    if not content:
        raise ContentNotFoundError(f"Content with id='{id}' not found.")

    if status and status != "any":  # "any" is a special value to bypass status check
        current_content_status = content.get("status")
        if current_content_status != status:
            raise ContentStatusMismatchError(
                f"Content status mismatch for id='{id}'. Expected: '{status}', Actual: '{current_content_status}'."
            )
    else:
        return content


def update_content(id: str, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Updates existing content.

    This function updates an existing content item with new values.
    Versioning is managed automatically: the version is incremented by one (defaulting to 1 if no version is set).
    The update payload should not include a version object (any provided version data is ignored).

    Special behavior:
      - **Restoring a trashed page:**
        To restore content that is "trashed", the update request must set its status to "current". In that case,
        only the version is incremented and the status updated to "current". No other fields are modified.
      - **Deleting a draft:**
        If the update is intended to delete a draft (signaled by `query_status="draft"`), then the draft is removed and
        the content's body is replaced with the provided body. (Updating a draft is not supported.)

    Args:
        id (str): ID of the content to update.
        body (Dict[str, Any]): Dictionary containing updated content details.
            Optional fields:
                - title (str): New content title.
                - status (str): New content status.
                - body (Dict): New content body.
                - space (Dict[str, str]): New space object containing a "key" field.
                    - key (str): Space key.
                - ancestors (List[str]): List of ancestor IDs.

    Returns:
        Dict[str, Any]: Updated content details with keys:
            - id (str): Unique identifier of the content.
            - type (str): Content type (e.g., "page", "blogpost", "comment").
            - title (str): Updated content title.
            - space (Dict[str, str]): Space object containing:
                    - key (str): Space key.
            - status (str): Updated content status.
            - version (Dict[str, Any]): Version object containing:
                    - number (int): Updated version number.
                    - minorEdit (bool): Indicates if the update is a minor edit.
            - body (Dict[str, Any]): Updated content body.
            - Other metadata from the original content may also be present.

    Raises:
        TypeError: If `id` is not a string or `body` is not a dictionary.
        ValidationError: If the `body` argument does not conform to the expected structure
                         (e.g., incorrect types for fields like 'title', 'space', 'ancestors',
                         or 'space' object missing 'key').
        ContentNotFoundError: If the content with the specified `id` doesn't exist.
        InvalidInputError: If `id` is an empty string or `body` is empty, or if validation fails for specific fields.
    """
    # --- Input Validation Start ---
    if not isinstance(id, str):
        raise TypeError(f"Argument 'id' must be a string, got {type(id).__name__}.")
    
    if not id.strip():
        raise InvalidInputError("Argument 'id' cannot be an empty string.")

    if not isinstance(body, dict):
        raise TypeError(f"Argument 'body' must be a dictionary, got {type(body).__name__}.")
    
    if not body:
        raise InvalidInputError("Argument 'body' cannot be an empty dictionary.")

    # Validate body structure using Pydantic model
    try:
        validated_body_model = UpdateContentBodyInputModel(**body).model_dump()
    except PydanticValidationError as e:
        raise ValidationError(f"Input validation failed")
    # --- Input Validation End ---

    # Check if content exists
    content = DB["contents"].get(id)
    if not content:
        raise ContentNotFoundError(f"Content with id='{id}' not found.")

    # If the body includes a status e.g. 'trashed' or 'current', handle it
    new_status = validated_body_model.get("status")
    if new_status:
        content["status"] = new_status

    # Update title if provided (validation done by Pydantic)
    if "title" in body:
        content["title"] = validated_body_model.get("title")

    # Update content body if provided
    if "body" in body:
        content["body"] = validated_body_model.get("body")
    
    # Update space if provided
    if "space" in body:
        space_data = validated_body_model.get("space")
        if space_data and "key" in space_data:
            content["spaceKey"] = space_data["key"]
    
    # Update ancestors if provided (for comments)
    if "ancestors" in body:
        ancestors = validated_body_model.get("ancestors")
        if ancestors is not None:
            # Validate that all ancestor IDs exist in the database
            for ancestor_id in ancestors:
                if not DB["contents"].get(ancestor_id):
                    raise ContentNotFoundError(f"Ancestor content with id='{ancestor_id}' not found.")
            content["ancestors"] = ancestors

    # Update version number
    current_version = content.get("version", {}).get("number", 0)
    if "version" not in content:
        content["version"] = {}
    content["version"]["number"] = current_version + 1
    content["version"]["minorEdit"] = False

    # Save updated content
    DB["contents"][id] = content
    return content


def delete_content(id: str, status: Optional[str] = None) -> None:
    """
    Deletes a content item from the system.

    This function simulates the deletion of a content item based on its type and status,
    following these cases:
      1. If the status of the content is "current":
         The content is trashed by updating its status to "trashed" (simulating a soft delete).
      2. If the status of the content is "trashed", and the query parameter "status"
         is set to "trashed":
         The content is purged (permanently deleted) from the database.
      3. If the content is not trashable (historical, draft, archived):
         The content is immediately deleted permanently regardless of its status.

    Args:
        id (str): The unique identifier of the content to delete.
        status (Optional[str]): The query parameter "status" from the request.
            When set to "trashed" in the purge scenario, indicates that the content should be
            permanently deleted.

    Returns:
        None

    Raises:
        TypeError: If 'id' is not a string, or if 'status' is provided and is not a string.
        ValueError: If there is no content with the given id (propagated from core logic).
    """
    # Input Validation
    if not isinstance(id, str):
        raise TypeError(f"id must be a string, got {type(id).__name__}.")
    if status is not None and not isinstance(status, str):
        raise TypeError(f"status must be a string if provided, got {type(status).__name__}.")

    content = DB["contents"].get(id)
    if not content:
        raise ValueError(f"Content with id={id} not found.")

    if "status" not in content:
        raise ValueError(f"Content with id={id} does not have a status field.")
    current_status_in_db = content["status"]

    # Case 3: If the content is not trashable (historical, draft, archived) - delete immediately regardless of status
    if current_status_in_db in ["historical", "draft", "archived"]:
        del DB["contents"][id]
    # Case 1: If the status of the content is "current" - trash it
    elif current_status_in_db == "current":
        content["status"] = "trashed"
        DB["contents"][id] = content
    # Case 2: If the status of the content is "trashed", and the query parameter "status" is set to "trashed" - purge it
    elif current_status_in_db == "trashed" and status == "trashed":
        del DB["contents"][id]
    # Otherwise, do nothing (e.g., content is trashed but status parameter is not "trashed")
    else:
        pass


def search_content(
    cql: str,
    start: int = 0,
    limit: int = 25,
) -> List[Dict[str, Any]]:
    """
    Searches for content using Confluence Query Language (CQL) with pagination support.

    This function performs a search across all content items using the provided CQL query.
    It supports complex queries with logical operators and field comparisons, and returns
    paginated results.

    Args:
        cql (str): The Confluence Query Language (CQL) string for the search.
            For example: `cql="type='page' AND space='TEST' AND title~'Urgent'"`.
            Supported fields and operators:
            - `type`: Filters by the type of content (e.g., 'page', 'blogpost', 'comment').
                - Operators: `=`, `!=`
                - Example: `type='page'`
            - `space`/`spaceKey`: Filters by the space the content belongs to.
                - Operators: `=`, `!=`
                - Example: `space='MYSPACE'`
            - `title`: Filters by content title.
                - Operators: `=`, `!=`, `~` (contains), `!~` (does not contain)
                - Example: `title~'Meeting Notes'`
            - `status`: Filters by content status.
                - Operators: `=`, `!=`
                - Example: `status='current'`
            - `ancestor`: Filters by a specific parent page ID.
                - Operators: `=`
                - Example: `ancestor=12345`
            - `label`: Filters by a label on the content.
                - Operators: `=`, `!=`
                - Example: `label='official-docs'`
            - `creator`: Filters by the user who created the content.
                - Operators: `=`, `!=`
                - Example: `creator='jsmith'`
            Logical operators `AND`, `OR`, `NOT` and parentheses `()` can be used to combine expressions.
        start (int): The starting index for pagination. Defaults to 0. Must be non-negative.
        limit (int): The maximum number of results to return. Defaults to 25. Must be non-negative.

    Returns:
        List[Dict[str, Any]]: A list of content items that match the search criteria.
            Each item is a dictionary containing the content details with keys:
            - id (str): Content identifier.
            - type (str): Content type.
            - title (str): Content title.
            - spaceKey (str): Space key.
            - status (str): Content status.
            - version (Dict): Content version object with keys:
                  - number (int): Version number.
                  - minorEdit (bool): Minor edit flag.
            - body (Dict): Content body.
            - ancestors (Optional[List[str]]): List of ancestor IDs (for comments)
    Raises:
        TypeError: If 'cql' is not a string, or 'start' or 'limit' are not integers.
        InvalidPaginationValueError: If 'start' or 'limit' are negative.
        ValueError: If the CQL query is missing or invalid.
    """
    # Input validation
    if not isinstance(cql, str):
        raise TypeError("Argument 'cql' must be a string.")
    if not isinstance(start, int):
        raise TypeError("Argument 'start' must be an integer.")
    if not isinstance(limit, int):
        raise TypeError("Argument 'limit' must be an integer.")

    if start < 0:
        raise InvalidPaginationValueError("Argument 'start' must be non-negative.")
    if limit < 0:
        raise InvalidPaginationValueError("Argument 'limit' must be non-negative.")

    if not cql.strip():
        raise ValueError("CQL query is missing.")

    all_contents = list(DB["contents"].values())

    # Tokenize the CQL query
    # MODIFIED: Regex now supports both single and double quotes for values.
    # It also supports field names that might contain underscores or be a single word.
    # And values can contain spaces if quoted.
    token_pattern = re.compile(
        r"""
        \(|\)|                                # Parentheses
        \b(?:and|or|not)\b|                   # Logical operators (as whole words)
        \w+\s*(?:>=|<=|!=|!~|>|<|=|~)\s* # Field and operator
        (?:'([^']*)'|\"([^\"]*)\")            # Value in single or double quotes
        """,
        re.IGNORECASE | re.VERBOSE,
    )
    
    # We need to find full matches for expressions, not just parts.
    # The previous findall would split "type='page'" into "type='page'" which is fine,
    # but the new regex with capturing groups for quotes needs careful handling.
    # Instead, we'll create a list of tokens that are either operators, parentheses, or full expressions.
    
    # A simpler approach for tokenizing expressions and operators:
    # This regex will find operators, parentheses, or full field-operator-value expressions.
    # The key is that field-operator-value is one alternative.
    tokenizer_regex = r"""
        \b(?:and|or|not)\b|                 # Match 'and', 'or', 'not' as whole words
        \(|\)|                              # Match '(' or ')'
        \w+\s*(?:>=|<=|!=|!~|>|<|=|~)\s* # Match field name and operator part
        (?:                                 # Non-capturing group for quotes
            '[^']*'|                        # Match single-quoted string
            \"[^\"]*\"                      # Match double-quoted string
        )
    """
    tokens = re.findall(tokenizer_regex, cql, re.IGNORECASE | re.VERBOSE)
    
    # UPDATED VALIDATION LOGIC:
    # Check for any part of the CQL string that couldn't be tokenized.
    # We substitute all valid tokens with an empty string and check if anything
    # other than whitespace remains.
    untokenized_remains = re.sub(tokenizer_regex, "", cql, flags=re.IGNORECASE | re.VERBOSE)

    if untokenized_remains.strip():
        raise ValueError("CQL query is invalid.")


    # Filter contents based on the CQL query
    filtered_contents = [
        content for content in all_contents if _evaluate_cql_tree(content, tokens)
    ]

    # Pagination
    paginated = filtered_contents[start : start + limit]
    return paginated


def get_content_list(
    type: Optional[str] = None,
    spaceKey: Optional[str] = None,
    title: Optional[str] = None,
    status: Optional[str] = "current",
    postingDay: Optional[str] = None,
    expand: Optional[str] = None,
    start: int = 0,
    limit: int = 25
) -> List[Dict[str, Any]]:
    """
    Returns a paginated list of content filtered by the specified parameters.

    This function retrieves all content from the database and applies filters based
    on the provided arguments. The results are paginated using the start and limit parameters.

    Args:
        type (Optional[str]): The type of content (e.g., "page", "blogpost", "comment").
            Only content matching this type is returned. If None, no filtering is applied.
        spaceKey (Optional[str]): The key of the space in which the content is located.
            Only content in the specified space is returned.
        title (Optional[str]): The title of the content. Filters to content with a matching title. Required if type is "page".
        status (Optional[str]): The status of the content (e.g., "current", "trashed", or "any").
            Defaults to "current". If explicitly set to None, it's treated like "current" by the core logic.
            If "any", the status filter is ignored.
        postingDay (Optional[str]): The posting day of the content. This filter is only applied
            if the content type is "blogpost". Format: yyyy-mm-dd. Example: "2024-01-01".
        expand (Optional[str]): A comma-separated list of additional fields to include in the
            returned content objects. Supported values:
            - space: Expands the space field with space key
            - version: Expands the version information
            - history: Expands the content history
        start (int): The starting index for pagination. Defaults to 0.
        limit (int): The maximum number of results to return. Defaults to 25.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries representing the filtered content.
            Each dictionary contains the following keys:
            - id (str): Unique identifier for the content.
            - type (str): Content type.
            - spaceKey (str): Key of the space where the content is located.
            - title (str): Title of the content.
            - status (str): Current status of the content.
            - body (Dict): Content body data.
            - postingDay (Optional[str]): Posting day for blog posts.
            - link (str): URL path to the content.
            - children (Optional[List[Dict[str, Any]]]): List of child content items.
            - ancestors (Optional[List[Dict[str, Any]]]): List of ancestor content items.
            Plus any expanded fields specified in the expand parameter.

    Raises:
        TypeError: If any argument has an incorrect type (e.g., 'type' is not a string, 'start' is not an int).
        InvalidParameterValueError: If 'status' has an unsupported value (and is not None), 
            'postingDay' has an invalid format, 'expand' contains unsupported fields, 
            or 'start'/'limit' are negative.
        MissingTitleForPageError: If 'type' is "page" and 'title' is not provided or is an empty string.
        ValueError: Propagated if errors occur during 'expand' processing for 'history' 
                    (e.g., from an internal `get_content_history` call).
    """
    # --- Input Validation Start ---

    # 1. Standard Type Validation for non-dictionary arguments
    if type is not None and not isinstance(type, str):
        raise TypeError("Argument 'type' must be a string or None.")
    if spaceKey is not None and not isinstance(spaceKey, str):
        raise TypeError("Argument 'spaceKey' must be a string or None.")
    if title is not None and not isinstance(title, str):
        raise TypeError("Argument 'title' must be a string or None.")
    
    # Validation for 'status' (type then value)
    # 'status' default is "current". If status=None is passed, it is None here.
    if status is not None:
        if not isinstance(status, str):
            raise TypeError("Argument 'status' must be a string if provided (i.e., not None).")
        VALID_STATUSES = ["current", "trashed", "any"]
        if status not in VALID_STATUSES:
            raise InvalidParameterValueError(
                f"Argument 'status' must be one of {VALID_STATUSES} if provided. Got '{status}'."
            )
    # If status is None, it's valid at this stage; core logic will effectively treat it as 'current'.

    if postingDay is not None and not isinstance(postingDay, str):
        raise TypeError("Argument 'postingDay' must be a string or None.")
    if expand is not None and not isinstance(expand, str):
        raise TypeError("Argument 'expand' must be a string or None.")
    
    if not isinstance(start, int):
        raise TypeError("Argument 'start' must be an integer.")
    if not isinstance(limit, int):
        raise TypeError("Argument 'limit' must be an integer.")

    if postingDay:
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', postingDay):
            raise InvalidParameterValueError("Argument 'postingDay' must be in yyyy-mm-dd format (e.g., '2024-01-01').")

    if expand and expand.strip(): # Process only if expand is not None and not effectively empty
        ALLOWED_EXPAND_FIELDS = {"space", "version", "history"}
        fields = [field.strip() for field in expand.split(',')]
        for f_val in fields:
            if not f_val: # Handles cases like "space,,history" which results in an empty string field
                raise InvalidParameterValueError("Argument 'expand' contains an empty field name, which is invalid.")
            if f_val not in ALLOWED_EXPAND_FIELDS:
                raise InvalidParameterValueError(
                    f"Argument 'expand' contains an invalid field '{f_val}'. "
                    f"Allowed fields are: {', '.join(ALLOWED_EXPAND_FIELDS)}."
                )

    if start < 0:
        raise InvalidParameterValueError("Argument 'start' must be non-negative.")
    if limit < 0:
        raise InvalidParameterValueError("Argument 'limit' must be non-negative.")

        
    # --- Input Validation End ---
    # Collect all content
    all_contents = list(DB["contents"].values())

    # Filter
    if type:
        all_contents = [c for c in all_contents if c.get("type") == type]
    if spaceKey:
        all_contents = [c for c in all_contents if c.get("spaceKey") == spaceKey]
    if title:
        all_contents = [c for c in all_contents if c.get("title") == title]
    if postingDay and type == "blogpost":
        # Simulate a postingDay check
        all_contents = [
            c for c in all_contents
            if c.get("postingDay") == postingDay
        ]
    if status and status != "any":
        # "current" or "trashed"
        all_contents = [c for c in all_contents if c.get("status") == status]
    elif status == "any":
        #No filter for status
        pass
    else:
        # Default to "current" if not specified
        all_contents = [c for c in all_contents if c.get("status") == "current"]

    # Apply pagination
    paginated = all_contents[start:start + limit]
    
    # Process expanded fields if requested
    if expand:
        expanded_results = []
        for content in paginated:
            expanded_content = content.copy()
            for field in expand.split(','):
                field = field.strip()
                if field == "space":
                    # Get space information
                    space_key = content.get("spaceKey")
                    if space_key:
                        space = DB.get("spaces", {}).get(space_key)
                        if space:
                            expanded_content["space"] = {
                                "key": space["spaceKey"],
                                "name": space["name"],
                                "description": space.get("description", "")
                            }
                elif field == "version":
                    # Get version information
                    content_id = content.get("id")
                    if content_id:
                        # Look for version property by key "{id}:version"
                        prop_key = f"{content_id}:version"
                        version = DB.get("content_properties", {}).get(prop_key)
                        if version:
                            expanded_content["version"] = [{"version": version.get("value", {}).get("number", 1)}]
                        else:
                            # Default version if not found
                            expanded_content["version"] = [{"version": 1}]
                elif field == "history":
                    # Get content history
                    content_id = content.get("id")
                    if content_id:
                        try:
                            history = get_content_history(content_id)
                            if history:
                                expanded_content["history"] = history
                        except ValueError:
                            pass
            expanded_results.append(expanded_content)
        return expanded_results
    
    return paginated


def get_content_history(id: str, expand: Optional[str] = None) -> Dict[str, Any]:
    """
    Returns the history of a piece of content.

    This method returns the metadata regarding creation and versioning for the content item
    identified by the given id. It uses a global history store (DB["history"]) that is updated
    whenever content is created or updated. Each history record includes the version number,
    createdBy, createdDate, and lastUpdated timestamp.

    Args:
        id (str): Unique identifier of the content.
        expand (Optional[str], optional): A comma-separated list of additional fields to expand
                                          (e.g., "previousVersion,nextVersion,lastUpdated").
                                          This parameter is not used to filter the output in this simulation.

    Returns:
        Dict[str, Any]: A dictionary representing the content's history with the following structure:
            - id (str): The unique identifier of the content.
            - latest (bool): Indicating whether this is the latest version of the content.
            - createdBy (str): The username of the creator.
            - createdDate (str): The ISO timestamp when the content was created.
            - previousVersion (Optional[Dict[str, Any]]): The previous version record, if available.
            - nextVersion (Optional[Dict[str, Any]]): The next version record, if available.

    Raises:
        ValueError: If no content with the specified id is found or if the id is an empty string.
        TypeError: If the arguments are not of the correct type.
    """
    # --- Input Validation Start ---
    if not isinstance(id, str):
        raise TypeError("Argument 'id' must be a string.")
    
    if not id.strip():
        raise ValueError("Argument 'id' cannot be an empty string.")

    if expand is not None and not isinstance(expand, str):
        raise TypeError("Argument 'expand' must be a string or None.")
    # --- Input Validation End ---

    content = DB["contents"].get(id)
    if not content:
        raise ValueError(f"Content with id={id} not found.")
    # We'll just return a mock dictionary.
    history = {
        "id": id,
        "latest": True,
        "createdBy": "mockuser",
        "createdDate": "2023-01-01T12:00:00.000Z",
        "previousVersion": None,
        "nextVersion": None,
    }
    return history


def get_content_children(
    id: str, expand: Optional[str] = None, parentVersion: int = 0
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Returns a mapping of direct children content grouped by type.

    Args:
        id (str): Unique identifier of the parent content.
        expand (Optional[str]): A comma-separated list of additional fields to include.
            This parameter is not utilized in this simulation. Defaults to None.
        parentVersion (int): The version number of the parent content. This is included
            for potential version-related logic, but is not used in the simulation. Defaults to 0.

    Returns:
        Dict[str, List[Dict[str, Any]]]: A dictionary where each key represents a content type
            (e.g., "page", "blogpost", "comment", "attachment") and the corresponding value is a list
            of child content dictionaries. Each Dict[str, Any] contains:
                - id (str): Unique identifier for the content.
                - type (str): Content type (e.g., "page", "blogpost", "comment", "attachment").
                - title (str): Title of the content.
                - spaceKey (str): Key of the space where the content is located.
                - status (str): Current status of the content (e.g., "current", "trashed").
                - body (Dict[str, Any]): Content body data.
                - postingDay (Optional[str]): Posting day for blog posts.
                - link (str): URL path to the content.
                - children (Optional[List[Dict[str, Any]]]): List of child content.
                - ancestors (Optional[List[Dict[str, Any]]]): List of ancestor content.

    Raises:
        ValueError: If the parent content with the specified id is not found.
        TypeError: If the arguments are not of the correct type.
    """
    # --- Input Validation Start ---
    if not isinstance(id, str):
        raise TypeError("Argument 'id' must be a string.")
    
    if not id.strip():
        raise ValueError("Argument 'id' cannot be an empty string.")
    
    if expand is not None and not isinstance(expand, str):
        raise TypeError("Argument 'expand' must be a string or None.")
    
    if not isinstance(parentVersion, int):
        raise TypeError("Argument 'parentVersion' must be an integer.")
    # --- Input Validation End ---
    
    content = DB["contents"].get(id)
    if not content:
        raise ValueError(f"Content with id={id} not found.")
    # In a real scenario we might track parent->child relationships.
    # We'll just return an empty map for demonstration.
    children_by_type = {"page": [], "blogpost": [], "comment": [], "attachment": []}

    # Get the list of children IDs stored in the parent's "children" field.
    children = content.get("children", [])

    # For each child id, retrieve the full content and group by its type.
    for child in children:
        if child:
            child_type = child.get("type")
            if child_type in children_by_type:
                children_by_type[child_type].append(child)
            else:
                # Optionally, handle unexpected content types here.
                pass

    return children_by_type


def get_content_children_of_type(
    id: str,
    child_type: str,
    expand: Optional[str] = None,
    parentVersion: int = 0,
    start: int = 0,
    limit: int = 25,
) -> Dict[str, Dict[str, Any]]:
    """
    Returns direct children content of a specified type.

    Args:
        id (str): Unique identifier of the parent content.
        child_type (str): The type of child content to retrieve (e.g., "page", "blogpost", "comment", "attachment").
        expand (Optional[str], optional): Additional fields to include in the result. Not used in this simulation.
            Defaults to None.
        parentVersion (int): The version of the parent content. Provided for potential future use; not used
            in this simulation. Defaults to 0.
        start (int): The starting index for pagination. Defaults to 0.
        limit (int): The maximum number of child content items to return. Defaults to 25.

    Returns:
        Dict[str, Dict[str, Any]]: A JSON map representing ordered collections of content children, keyed by content type.
            The structure contains:
            - {child_type} (Dict[str, Any]): A dictionary with keys:
                - results (List[Dict[str, Any]]): Paginated list of child content items, each containing:
                    - id (str): Unique identifier for the content
                    - type (str): Content type (e.g., "page", "blogpost", "comment", "attachment")
                    - title (str): Title of the content
                    - spaceKey (str): Key of the space where the content is located
                    - status (str): Current status of the content (e.g., "current", "trashed")
                    - body (Dict[str, Any]): Content body data with storage format
                    - version (Dict[str, Any]): Content version information
                    - ancestors (Optional[List[Dict[str, Any]]]): List of ancestor content items
                    - children (Optional[List[Dict[str, Any]]]): List of child content items
                    - descendants (Optional[List[Dict[str, Any]]]): List of descendant content items
                    - postingDay (Optional[str]): Posting day for blog posts
                    - link (str): URL path to the content
                - size (int): Number of items in the results array

    Raises:
        TypeError: If 'id' is not a string, 'child_type' is not a string, 'expand' is not a string (when provided),
                   'parentVersion' is not an integer, 'start' is not an integer, or 'limit' is not an integer.
        InvalidInputError: If 'id' is an empty string, 'child_type' is an empty string, or 'expand' is an empty string.
        InvalidParameterValueError: If 'child_type' has an unsupported value, 'start' is negative, or 'limit' is not positive.
        ContentNotFoundError: If the parent content with the given id is not found.
    """
    # --- Input Validation Start ---
    
    # Validate id parameter
    if not isinstance(id, str):
        raise TypeError("Argument 'id' must be a string.")
    if not id.strip():
        raise InvalidInputError("Argument 'id' cannot be an empty string.")
    
    # Validate child_type parameter
    if not isinstance(child_type, str):
        raise TypeError("Argument 'child_type' must be a string.")
    if not child_type.strip():
        raise InvalidInputError("Argument 'child_type' cannot be an empty string.")
    
    # Validate supported child types
    VALID_CHILD_TYPES = ["page", "blogpost", "comment", "attachment"]
    if child_type not in VALID_CHILD_TYPES:
        raise InvalidParameterValueError(
            f"Argument 'child_type' must be one of {VALID_CHILD_TYPES}. Got '{child_type}'."
        )
    
    # Validate expand parameter
    if expand is not None:
        if not isinstance(expand, str):
            raise TypeError("Argument 'expand' must be a string if provided.")
        if not expand.strip():
            raise InvalidInputError("Argument 'expand' cannot be an empty string if provided.")
    
    # Validate parentVersion parameter
    if not isinstance(parentVersion, int):
        raise TypeError("Argument 'parentVersion' must be an integer.")
    if parentVersion < 0:
        raise InvalidParameterValueError("Argument 'parentVersion' must be non-negative.")
    
    # Validate start parameter
    if not isinstance(start, int):
        raise TypeError("Argument 'start' must be an integer.")
    if start < 0:
        raise InvalidParameterValueError("Argument 'start' must be non-negative.")
    
    # Validate limit parameter
    if not isinstance(limit, int):
        raise TypeError("Argument 'limit' must be an integer.")
    if limit <= 0:
        raise InvalidParameterValueError("Argument 'limit' must be positive.")
    
    # --- Input Validation End ---
    
    # Check if parent content exists
    parent = DB["contents"].get(id)
    if not parent:
        raise ContentNotFoundError(f"Content with id='{id}' not found.")

    children = parent.get("children", [])
    filtered_children = []
    for child in children:
        if child and child.get("type") == child_type:
            filtered_children.append(child)

    # Apply pagination
    paginated_results = filtered_children[start : start + limit]
    
    return {
        child_type: {
            "results": paginated_results,
            "size": len(paginated_results)
        }
    }


def get_content_comments(
    id: str,
    expand: Optional[str] = None,
    parentVersion: int = 0,
    start: int = 0,
    limit: int = 25,
    location: Optional[str] = None,
    depth: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Returns the comments associated with a specific content item.

    Args:
        id (str): The unique identifier of the parent content.
        expand (Optional[str]): A comma-separated list of additional fields to include in the
            returned comment objects. Not utilized in this simulation. Defaults to None.
        parentVersion (int): The version of the parent content. This parameter is provided for
            completeness but is not used in this simulation. Defaults to 0.
        start (int): The starting index for pagination. Defaults to 0.
        limit (int): The maximum number of comment objects to return. Defaults to 25.
        location (Optional[str]): An optional parameter to specify a location filter within the
            content hierarchy. Not used in this simulation. Defaults to None.
        depth (Optional[str]): An optional parameter to control the depth of comment retrieval.
            Not used in this simulation. Defaults to None.

    Returns:
        Dict[str, Any]: A JSON map representing ordered collections of comment children, keyed by content type.
            The structure contains:
            - comment (Dict[str, Any]): A dictionary with keys:
                - results (List[Dict[str, Any]]): Paginated list of comment content items, each containing:
                    - id (str): Unique identifier for the content
                    - type (str): Content type (e.g., "comment")
                    - title (str): Title of the content
                    - spaceKey (str): Key of the space where the content is located
                    - status (str): Current status of the content (e.g., "current", "trashed")
                    - body (Dict[str, Any]): Content body data with storage format
                    - version (Dict[str, Any]): Content version information
                    - ancestors (Optional[List[Dict[str, Any]]]): List of ancestor content items
                    - children (Optional[List[Dict[str, Any]]]): List of child content items
                    - descendants (Optional[List[Dict[str, Any]]]): List of descendant content items
                    - postingDay (Optional[str]): Posting day for blog posts
                    - link (str): URL path to the content
                - size (int): Number of items in the results array

    Raises:
        TypeError: If 'id' is not a string, 'expand' is not a string (when provided),
                   'parentVersion' is not an integer, 'start' is not an integer, or 'limit' is not an integer.
        InvalidInputError: If 'id' is an empty string, or 'expand' is an empty string.
        InvalidParameterValueError: If 'start' is negative, or 'limit' is not positive.
        ContentNotFoundError: If the parent content with the given id is not found.
    """
    # --- Input Validation Start ---
    
    # Validate id parameter
    if not isinstance(id, str):
        raise TypeError("Argument 'id' must be a string.")
    if not id.strip():
        raise InvalidInputError("Argument 'id' cannot be an empty string.")
    
    # Validate expand parameter
    if expand is not None:
        if not isinstance(expand, str):
            raise TypeError("Argument 'expand' must be a string if provided.")
        if not expand.strip():
            raise InvalidInputError("Argument 'expand' cannot be an empty string if provided.")
    
    # Validate parentVersion parameter
    if not isinstance(parentVersion, int):
        raise TypeError("Argument 'parentVersion' must be an integer.")
    if parentVersion < 0:
        raise InvalidParameterValueError("Argument 'parentVersion' must be non-negative.")
    
    # Validate start parameter
    if not isinstance(start, int):
        raise TypeError("Argument 'start' must be an integer.")
    if start < 0:
        raise InvalidParameterValueError("Argument 'start' must be non-negative.")
    
    # Validate limit parameter
    if not isinstance(limit, int):
        raise TypeError("Argument 'limit' must be an integer.")
    if limit <= 0:
        raise InvalidParameterValueError("Argument 'limit' must be positive.")
    
    # --- Input Validation End ---
    
    # Check if parent content exists
    parent = DB["contents"].get(id)
    if not parent:
        raise ContentNotFoundError(f"Content with id='{id}' not found.")

    children = parent.get("children", [])
    comments = []
    for child in children:
        if child and child.get("type") == "comment":
            comments.append(child)

    # Apply pagination
    paginated_results = comments[start : start + limit]
    
    return {
        "comment": {
            "results": paginated_results,
            "size": len(paginated_results)
        }
    }


def get_content_attachments(
    id: str,
    expand: Optional[str] = None,
    start: int = 0,
    limit: int = 50,
    filename: Optional[str] = None,
    mediaType: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Returns attachments for a specific content item.

    Args:
        id (str): The unique identifier of the parent content.
        expand (Optional[str]): A comma-separated list of additional fields to include.
            Not utilized in this simulation. Defaults to None.
        start (int): The starting index for pagination. Defaults to 0.
        limit (int): The maximum number of attachments to return. Defaults to 50.
        filename (Optional[str]): Filter attachments by filename. Defaults to None.
        mediaType (Optional[str]): Filter attachments by media type. Defaults to None.

    Returns:
        Dict[str, Any]: A JSON representation of a list of attachment Content entities with structure:
            - results (List[Dict[str, Any]]): Paginated list of attachment content items, each containing:
                - id (str): Unique identifier for the attachment
                - type (str): Content type (always "attachment")
                - title (str): Attachment filename/title
                - version (Dict[str, Any]): Version information with keys:
                    - by (Dict[str, Any]): User who created the version
                    - when (str): ISO timestamp of version creation
                    - message (str): Version change message
                    - number (int): Version number
                    - minorEdit (bool): Whether this was a minor edit
                - container (Dict[str, Any]): Parent content information
                - metadata (Dict[str, Any]): Attachment metadata with keys:
                    - comment (str): Attachment comment/description
                    - mediaType (str): MIME type of the attachment
                - _links (Dict[str, str]): API links
                - _expandable (Dict[str, str]): Expandable fields
            - size (int): Number of items in the results array
            - _links (Dict[str, str]): API base links

    Raises:
        TypeError: If 'id' is not a string, 'expand' is not a string (when provided), 
                   'start' or 'limit' are not integers, 'filename' or 'mediaType' are not strings (when provided).
        InvalidInputError: If 'id' is an empty string, or 'expand', 'filename', or 'mediaType' are empty strings (when provided).
        InvalidParameterValueError: If 'start' is negative, 'limit' is not positive, or 'limit' exceeds maximum value.
        ContentNotFoundError: If the parent content with the given id is not found.
    """
    # --- Input Validation Start ---
    if not isinstance(id, str):
        raise TypeError("Argument 'id' must be a string.")
    if not id.strip():
        raise InvalidInputError("Argument 'id' cannot be an empty string.")
    
    if expand is not None:
        if not isinstance(expand, str):
            raise TypeError("Argument 'expand' must be a string if provided.")
        if not expand.strip():
            raise InvalidInputError("Argument 'expand' cannot be an empty string if provided.")
    
    if not isinstance(start, int):
        raise TypeError("Argument 'start' must be an integer.")
    if start < 0:
        raise InvalidParameterValueError("Argument 'start' must be non-negative.")
    
    if not isinstance(limit, int):
        raise TypeError("Argument 'limit' must be an integer.")
    if limit <= 0:
        raise InvalidParameterValueError("Argument 'limit' must be positive.")
    if limit > 1000:  # Reasonable maximum limit
        raise InvalidParameterValueError("Argument 'limit' cannot exceed 1000.")
    
    if filename is not None:
        if not isinstance(filename, str):
            raise TypeError("Argument 'filename' must be a string if provided.")
        if not filename.strip():
            raise InvalidInputError("Argument 'filename' cannot be an empty string if provided.")
    
    if mediaType is not None:
        if not isinstance(mediaType, str):
            raise TypeError("Argument 'mediaType' must be a string if provided.")
        if not mediaType.strip():
            raise InvalidInputError("Argument 'mediaType' cannot be an empty string if provided.")
    # --- Input Validation End ---
    
    # Check if parent content exists
    parent = DB["contents"].get(id)
    if not parent:
        raise ContentNotFoundError(f"Content with id='{id}' not found.")
    
    # Get children and filter for attachments
    children = parent.get("children", [])
    attachments = []
    
    for child in children:
        if child and child.get("type") == "attachment":
            # Apply filename filter if provided
            if filename and child.get("title") != filename:
                continue
            
            # Apply mediaType filter if provided
            if mediaType and child.get("metadata", {}).get("mediaType") != mediaType:
                continue
            
            attachments.append(child)
    
    # Apply pagination
    paginated_attachments = attachments[start : start + limit]
    
    # Return in the expected API format
    return {
        "results": paginated_attachments,
        "size": len(paginated_attachments),
        "_links": {
            "base": "http://example.com",
            "context": "/confluence"
        }
    }


def create_attachments(
    id: str, file: Any, comment: Optional[str] = None, minorEdit: bool = False
) -> Dict[str, Any]:
    """
    Creates new attachments for a specific content item.

    Args:
        id (str): The unique identifier of the parent content.
        file (Any): The file object to attach.
        comment (Optional[str], optional): A comment describing the attachment. Defaults to None.
        minorEdit (bool, optional): Whether this is a minor edit. Defaults to False.

    Returns:
        Dict[str, Any]: A dictionary containing information about the created attachment:
            - attachmentId (str): The unique identifier of the attachment.
            - fileName (str): The name of the attached file.
            - comment (Optional[str]): The comment describing the attachment.
            - minorEdit (bool): Whether this was a minor edit.

    Raises:
        TypeError: If 'id' is not a string, 'comment' is not a string (when provided), 
                   or 'minorEdit' is not a boolean.
        InvalidInputError: If 'id' is an empty string.
        FileAttachmentError: If 'file' is None or invalid.
        ContentNotFoundError: If the parent content with the given id is not found.
    """
    # --- Input Validation Start ---
    if not isinstance(id, str):
        raise TypeError("Argument 'id' must be a string.")
    if not id.strip():
        raise InvalidInputError("Argument 'id' cannot be an empty string.")
    
    if file is None:
        raise FileAttachmentError("Argument 'file' cannot be None.")
    
    if comment is not None and not isinstance(comment, str):
        raise TypeError("Argument 'comment' must be a string if provided.")
    
    if not isinstance(minorEdit, bool):
        raise TypeError("Argument 'minorEdit' must be a boolean.")
    # --- Input Validation End ---
    
    content = DB["contents"].get(id)
    if not content:
        raise ContentNotFoundError(f"Content with id='{id}' not found.")
    
    # Fake an "attachment" record
    return {
        "attachmentId": "1",
        "fileName": getattr(file, "name", "unknown"),
        "comment": comment,
        "minorEdit": minorEdit,
    }


def update_attachment(
    id: str, attachmentId: str, body: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Updates the metadata of an existing attachment.

    Args:
        id (str): The unique identifier of the parent content.
        attachmentId (str): The unique identifier of the attachment to update.
        body (Dict[str, Any]): The updated metadata for the attachment.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - attachmentId (str): The unique identifier of the attachment.
            - updatedFields (Dict[str, Any]): A dictionary of the fields that were updated.

    Raises:
        ValueError: If the parent content or attachment is not found.
    """
    content = DB["contents"].get(id)
    if not content:
        raise ValueError(f"Content with id={id} not found.")
    return {"attachmentId": attachmentId, "updatedFields": body}


def update_attachment_data(
    id: str,
    attachmentId: str,
    file: Any,
    comment: Optional[str] = None,
    minorEdit: bool = False,
) -> Dict[str, Any]:
    """
    Updates the binary data of an existing attachment.

    Args:
        id (str): The unique identifier of the parent content.
        attachmentId (str): The unique identifier of the attachment to update.
        file (Any): The new file object to replace the existing attachment.
        comment (Optional[str]): A comment describing the update.
        minorEdit (bool): Whether this is a minor edit.

    Returns:
        Dict[str, Any]: A dictionary containing information about the updated attachment:
            - attachmentId (str): The unique identifier of the attachment.
            - updatedFile (str): The name of the updated file.
            - comment (Optional[str]): The comment describing the update.
            - minorEdit (bool): Whether this was a minor edit.

    Raises:
        TypeError: If 'id' is not a string, 'attachmentId' is not a string,
                   'comment' is not a string (when provided), or 'minorEdit' is not a boolean.
        InvalidInputError: If 'id' or 'attachmentId' is an empty string.
        FileAttachmentError: If 'file' is None or invalid.
        ContentNotFoundError: If the parent content with the given id is not found.
    """
    # --- Input Validation Start ---
    if not isinstance(id, str):
        raise TypeError("Argument 'id' must be a string.")
    if not id.strip():
        raise InvalidInputError("Argument 'id' cannot be an empty string.")
    
    if not isinstance(attachmentId, str):
        raise TypeError("Argument 'attachmentId' must be a string.")
    if not attachmentId.strip():
        raise InvalidInputError("Argument 'attachmentId' cannot be an empty string.")
    
    if file is None:
        raise FileAttachmentError("Argument 'file' cannot be None.")
    
    if comment is not None and not isinstance(comment, str):
        raise TypeError("Argument 'comment' must be a string if provided.")
    
    if not isinstance(minorEdit, bool):
        raise TypeError("Argument 'minorEdit' must be a boolean.")
    # --- Input Validation End ---
    
    content = DB["contents"].get(id)
    if not content:
        raise ContentNotFoundError(f"Content with id='{id}' not found.")
    
    return {
        "attachmentId": attachmentId,
        "updatedFile": getattr(file, "name", "unknown"),
        "comment": comment,
        "minorEdit": minorEdit,
    }


def get_content_descendants(
    id: str, expand: Optional[str] = None, start: int = 0, limit: int = 25
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Returns all descendants of a content item, grouped by type.

    Args:
        id (str): The unique identifier of the parent content.
        expand (Optional[str]): A comma-separated list of additional fields to include.
            Not used in this simulation.
        start (int): The starting index for pagination.
        limit (int): The maximum number of descendants to return per type.

    Returns:
        Dict[str, List[Dict[str, Any]]]: A dictionary mapping content types to lists of descendant content.
            Each Dict[str, Any] contains:
                - id (str): Unique identifier for the content.
                - type (str): Content type (e.g., "page", "blogpost", "comment", "attachment").
                - title (str): Title of the content.
                - spaceKey (str): Key of the space where the content is located.
                - status (str): Current status of the content (e.g., "current", "trashed").
                - body (Dict[str, Any]): Content body data.
                - postingDay (Optional[str]): Posting day for blog posts.
                - link (str): URL path to the content.
                - children (Optional[List[Dict[str, Any]]]): List of child content.
                - ancestors (Optional[List[Dict[str, Any]]]): List of ancestor content.

    Raises:
        TypeError: 
            If 'id' is not a string.
            If 'start' or 'limit' is not an integer.
        InvalidInputError: 
            If 'id' is an empty string.
            If 'start' is negative or 'limit' is negative or zero.
        ValueError: If the parent content with the given id is not found.
    """
    if not isinstance(id, str):
        raise TypeError("Argument 'id' must be a string.")
    
    id = id.strip()
    if not id:
        raise InvalidInputError("Argument 'id' cannot be an empty string.")
    
    parent = DB["contents"].get(id)
    if not parent:
        raise ValueError(f"Content with id={id} not found.")

    if not isinstance(start, int) or isinstance(start, bool):
        raise TypeError("Argument 'start' must be an integer.")
    
    if start and start < 0:
        raise InvalidInputError("Argument 'start' must be non-negative.")
    
    if not isinstance(limit, int) or isinstance(limit, bool):
        raise TypeError("Argument 'limit' must be an integer.")
    
    if limit and limit <= 0:
        raise InvalidInputError("Argument 'limit' must be non-negative.")

    # Initialize the result dictionary with empty lists for each content type
    descendants = {"page": [], "blogpost": [], "comment": [], "attachment": []}

    # Collect all descendants
    all_descendants = _collect_descendants(parent)

    # Group descendants by type
    for descendant in all_descendants:
        descendant_type = descendant.get("type")
        if descendant_type in descendants:
            descendants[descendant_type].append(descendant)

    # Apply pagination to each type's list
    for content_type in descendants:
        descendants[content_type] = descendants[content_type][start : start + limit]

    return descendants


def get_content_descendants_of_type(
    id: str, type: str, expand: Optional[str] = None, start: int = 0, limit: int = 25
) -> List[Dict[str, Any]]:
    """
    Returns descendants of a specific type for a content item.

    Args:
        id (str): The unique identifier of the parent content.
        type (str): The type of descendants to retrieve (e.g., "page", "blogpost", "comment", "attachment").
        expand (Optional[str]): A comma-separated list of additional fields to include.
            Not used in this simulation.
        start (int): The starting index for pagination.
        limit (int): The maximum number of descendants to return.

    Returns:
        List[Dict[str, Any]]: A paginated list of descendant content dictionaries of the specified type.
            Each Dict[str, Any] contains:
                - id (str): Unique identifier for the content.
                - type (str): Content type (e.g., "page", "blogpost", "comment", "attachment").
                - title (str): Title of the content.
                - spaceKey (str): Key of the space where the content is located.
                - status (str): Current status of the content (e.g., "current", "trashed").
                - body (Dict[str, Any]): Content body data.
                - postingDay (Optional[str]): Posting day for blog posts.
                - link (str): URL path to the content.
                - children (Optional[List[Dict[str, Any]]]): List of child content.
                - ancestors (Optional[List[Dict[str, Any]]]): List of ancestor content.

    Raises:
        TypeError: 
            If 'id' is not a string.
            If 'type' is not a string.
            If 'start' or 'limit' is not an integer.
        InvalidInputError: 
            If 'id' is an empty string.
            If 'type' is an empty string.
            If 'start' is negative or 'limit' is negative or zero.
        ValueError: If the parent content with the given id is not found.
    """
    if not isinstance(id, str):
        raise TypeError("Argument 'id' must be a string.")

    id = id.strip()
    if not id:
        raise InvalidInputError("Argument 'id' cannot be an empty string.")

    if not isinstance(type, str):
        raise TypeError("Argument 'type' must be a string.")

    type = type.strip()
    if not type:
        raise InvalidInputError("Argument 'type' cannot be an empty string.")

    if not isinstance(start, int) or isinstance(start, bool):
        raise TypeError("Argument 'start' must be an integer.")
    
    if not isinstance(limit, int) or isinstance(limit, bool):
        raise TypeError("Argument 'limit' must be an integer.")

    if start and start < 0:
        raise InvalidInputError("Argument 'start' must be non-negative.")
    
    if limit and limit <= 0:
        raise InvalidInputError("Argument 'limit' must be non-negative.")

    parent = DB["contents"].get(id)
    if not parent:
        raise ValueError(f"Content with id={id} not found.")

    # Collect descendants of the specified type
    type_descendants = _collect_descendants(parent, type)

    # Apply pagination
    return type_descendants[start : start + limit]


def get_content_labels(
        id: str, prefix: Optional[str] = None, start: int = 0, limit: int = 200
) -> List[Dict[str, Any]]:  # Corrected return type annotation based on implementation
    """
    Returns a paginated list of content labels. If a prefix is provided,
    it filters labels that start with the given prefix.

    Args:
        id (str): The ID of the content to get labels for.
        prefix (Optional[str]): Optional prefix to filter labels by.
        start (int): The starting index for pagination. Must be non-negative.
        limit (int): The maximum number of labels to return. Must be positive.

    Returns:
        List[Dict[str, Any]]: List of label objects in the format
            -   label (str): The label name.

    Raises:
        TypeError: If 'id' is not a string, 'prefix' is not a string or None,
                   'start' is not an integer, or 'limit' is not an integer.
        ValueError: If 'start' is negative, 'limit' is not positive,
                    or if the content with the given id is not found (propagated from original logic).
    """
    # Input validation
    if not isinstance(id, str):
        raise TypeError("Parameter 'id' must be a string.")
    if prefix is not None and not isinstance(prefix, str):
        raise TypeError("Parameter 'prefix' must be a string or None.")
    if not isinstance(start, int):
        raise TypeError("Parameter 'start' must be an integer.")
    if start < 0:
        raise ValueError("Parameter 'start' must be non-negative.")
    if not isinstance(limit, int):
        raise TypeError("Parameter 'limit' must be an integer.")
    if limit <= 0:
        raise ValueError("Parameter 'limit' must be positive.")


    content = DB["contents"].get(id)
    if not content:
        raise ValueError(f"Content with id={id} not found.")

    # Retrieve labels or return empty list if none exist
    labels = DB["content_labels"].get(id, [])

    # Apply prefix filter if provided
    if prefix:
        labels = [label for label in labels if label.startswith(prefix)]

    # Apply pagination
    paginated_labels = labels[start: start + limit]

    # Return in expected response format
    return [{"label": label} for label in paginated_labels]


def add_content_labels(id: str, labels: List[str]) -> List[Dict[str, Any]]:
    """
    Adds labels to a content item. If the content does not have existing labels,
    a new entry is created. Returns the updated list of labels.

    Args:
        id (str): The ID of the content to add labels to.
        labels (List[str]): List of labels to add.

    Returns:
        List[Dict[str, Any]]: List of updated label objects in the format
            - label (str): The label name.

    Raises:
        TypeError: If 'id' is not a string.
        TypeError: If 'labels' is not a list or contains non-string elements.
        ValueError: If the content with the given id is not found (from core logic).
    """
    # --- Input Validation ---
    if not isinstance(id, str):
        raise TypeError("Argument 'id' must be a string.")

    if not isinstance(labels, list):
        raise TypeError("Argument 'labels' must be a list.")

    for label_item in labels:
        if not isinstance(label_item, str):
            raise TypeError("All elements in 'labels' list must be strings.")
    # --- End Input Validation ---

    # --- Original Core Logic ---
    content = DB["contents"].get(id)
    if not content:
        raise ValueError(f"Content with id='{id}' not found.")

    # Ensure the content has an entry in the labels dictionary
    if id not in DB["content_labels"]:
        DB["content_labels"][id] = []

    # Add new labels, avoiding duplicates
    existing_labels = set(DB["content_labels"][id])
    new_labels_to_add = set(labels) # Renamed to avoid conflict with outer scope 'labels' if it were mutable and modified
    DB["content_labels"][id] = sorted(list(existing_labels.union(new_labels_to_add))) # sorted for predictable output

    # Return updated label list in expected response format
    return [{"label": label} for label in DB["content_labels"][id]]


def delete_content_labels(id: str, label: Optional[str] = None) -> None:
    """
    Deletes labels from a content item. If a specific label is provided,
    only that label is deleted. Otherwise, all labels are deleted.

    Args:
        id (str): The ID of the content from which labels should be deleted.
        label (Optional[str]): Optional specific label to delete.

    Raises:
        TypeError: If 'id' is not a string, or if 'label' is not a string (when provided).
        InvalidInputError: If 'id' is an empty string.
        ContentNotFoundError: If the content with the given id is not found.
        LabelNotFoundError: If the content has no labels, or if the specified label is not found.
    """
    # --- Input Validation Start ---
    if not isinstance(id, str):
        raise TypeError("Argument 'id' must be a string.")
    if not id.strip():
        raise InvalidInputError("Argument 'id' cannot be an empty string.")
    
    if label is not None and not isinstance(label, str):
        raise TypeError("Argument 'label' must be a string if provided.")
    # --- Input Validation End ---
    
    content = DB["contents"].get(id)
    if not content:
        raise ContentNotFoundError(f"Content with id='{id}' not found.")

    if id not in DB["content_labels"]:
        raise LabelNotFoundError(f"Content with id='{id}' has no labels.")

    if label:
        # Delete the specific label if it exists.
        if label in DB["content_labels"][id]:
            DB["content_labels"][id].remove(label)
            # Remove the key if no labels remain.
            if not DB["content_labels"][id]:
                del DB["content_labels"][id]
        else:
            raise LabelNotFoundError(f"Label {label} not found for content with id='{id}'.")
    else:
        # Delete all labels.
        del DB["content_labels"][id]


def get_content_properties(
    id: str, expand: Optional[str] = None, start: int = 0, limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Returns a paginated list of content properties for the specified content.

    Args:
        id (str): The unique identifier of the content
        expand (Optional[str]): A comma-separated list of properties to expand
        start (int): The starting index for pagination
        limit (int): The maximum number of properties to return

    Returns:
        List[Dict[str, Any]]: A list of content property objects, where each property has:
            - key (str): The property key
            - value (Dict[str, Any]): The property value (can include any key-value pairs)
            - version (int): The property version number

    Raises:
        ValueError: If no properties for the specified content are found.
        TypeError: 
            If 'id' is not a string
            If 'start' or 'limit' is not an integer
        InvalidInputError: 
            If 'id' is an empty string, 
            If 'start' is negative, or 'limit' is negative or zero.
    """
    if not isinstance(id, str):
        raise TypeError("Argument 'id' must be a string.")

    id = id.strip()
    if not id:
        raise InvalidInputError("Argument 'id' cannot be an empty string.")
    
    if not isinstance(start, int) or isinstance(start, bool):
        raise TypeError("Argument 'start' must be an integer.")
    
    if not isinstance(limit, int) or isinstance(limit, bool):
        raise TypeError("Argument 'limit' must be an integer.")
    
    if start and start < 0:
        raise InvalidInputError("Argument 'start' must be non-negative.")
    
    if isinstance(limit, int) and limit <= 0:
        raise InvalidInputError("Argument 'limit' must be positive.")
    
    parent = DB["content_properties"].get(id)

    if not parent:
        raise ValueError(f"No properties found for content with id='{id}'.")

    all_descendants = _collect_descendants(parent)

    return all_descendants[start : start + limit]


def create_content_property(id: str, body: Dict[str, Any]) -> Dict[str, any]:
    """
    Creates a new property for a specified content item.

    Args:
        id (str): The unique identifier of the content
        body (Dict[str, Any]): A JSON object containing the property key and value
            - key (str): The property key
            - value (Dict[str, Any]): The property value, any key-value pair
                - some (str): The property value

    Returns:
        Dict[str, any]: The newly created content property object with:
            - key (str): The property key
            - value (Dict[str, Any]): The property value
            - version (int): The property version number (starts at 1)

    Raises:
        TypeError: If 'id' is not a string or 'body' is not a dictionary.
        InvalidInputError: If 'id' is an empty string or 'key' is missing/empty.
        ContentNotFoundError: If the content with the specified ID is not found.
    """
    if not isinstance(id, str):
        raise TypeError("Argument 'id' must be a string.")
    if not id.strip():
        raise InvalidInputError("Argument 'id' cannot be an empty string.")
    
    if not isinstance(body, dict):
        raise TypeError("Argument 'body' must be a dictionary.")
    
    # Validate that key exists and is not empty
    key = body.get("key")
    if key is None:
        raise InvalidInputError("Missing required property 'key' in body.")
    if not isinstance(key, str):
        raise TypeError("Property 'key' must be a string.")
    if not key.strip():
        raise InvalidInputError("Property 'key' cannot be an empty string.")
    
    # Check if content exists
    content = DB["contents"].get(id)
    if not content:
        raise ContentNotFoundError(f"Content with id='{id}' not found.")
    
    # Extract value (can be any type, defaulting to empty dict for backward compatibility)
    value = body.get("value", {})
    version = 1
    prop_key = f"{id}:{key}"
    DB["content_properties"][prop_key] = {
        "key": key,
        "value": value,
        "version": version,
    }
    return DB["content_properties"][prop_key]





def get_content_property(
    id: str, key: str, expand: Optional[str] = None
) -> Dict[str, any]:
    """
    Retrieves a specific property of a content item by its key.

    Args:
        id (str): The unique identifier of the content
        key (str): The key of the property to retrieve
        expand (Optional[str]): A comma-separated list to expand property details.
            Supported values: 'version', 'content'

    Returns:
        Dict[str, any]: The content property object with:
            - key (str): The property key
            - value (Dict[str, Any]): The property value
            - version (int): The property version number
            If expand includes 'content', also includes:
            - content: The associated content object
            If expand includes 'version', also includes:
            - version: Detailed version information

    Raises:
        TypeError: If id or key are not strings
        ValueError:
            - If id or key are empty strings
            - If the content with the specified ID is not found
            - If the property with the specified key is not found
    """
    # Input validation
    if not isinstance(id, str):
        raise TypeError(f"id must be a string, but got {type(id).__name__}")
    if not isinstance(key, str):
        raise TypeError(f"key must be a string, but got {type(key).__name__}")
    if not id.strip():
        raise ValueError("id must not be empty")
    if not key.strip():
        raise ValueError("key must not be empty")
    
    # Expand validation
    if expand:
        valid_expand_values = {"content", "version"}
        expand_fields = [field.strip() for field in expand.split(",")]
        invalid_fields = set(expand_fields) - valid_expand_values
        if invalid_fields:
            raise ValueError(f"Invalid expand values: {invalid_fields}. Valid values are: {valid_expand_values}")
    
    # Check if content exists first
    content = DB["contents"].get(id)
    if not content:
        raise ValueError(f"Content with id={id} not found.")

    # Get property
    prop_key = f"{id}:{key}"
    prop = DB["content_properties"].get(prop_key)
    if not prop:
        raise ValueError(f"Property '{key}' not found for content {id}.")

    # Create a copy of the property to avoid modifying the stored version
    result = prop.copy()

    # Handle expand parameter
    if expand:
        expand_fields = [field.strip() for field in expand.split(",")]
        if "content" in expand_fields:
            result["content"] = content
        if "version" in expand_fields:
            version_number = result["version"]  # Store the original version number
            result["version"] = {
                "number": version_number,
                "when": get_iso_timestamp(),
                "message": prop.get("version_message", "Property version information"),
                "by": prop.get("last_modified_by", "system")
            }

    return result


def update_content_property(id: str, key: str, body: Dict[str, Any]) -> Dict[str, any]:
    """
    Updates an existing content property with a new value and an incremented version.

    Args:
        id (str): The unique identifier of the content
        key (str): The key of the property to update
        body (Dict[str, Any]): A JSON object containing the updated property value and new version

    Returns:
        Dict[str, any]: The updated content property object with:
            - key (str): The property key
            - value (Dict[str, Any]): The updated property value
            - version (int): The incremented version number

    Raises:
        ValueError: If the content with the specified ID is not found; if the property with the specified key is not found.
    """
    prop_key = f"{id}:{key}"
    prop = DB["content_properties"].get(prop_key)
    if not prop:
        raise ValueError(f"Property '{key}' not found for content {id}.")
    new_version = body.get("version", {}).get("number", prop["version"] + 1)
    value = body.get("value", prop["value"])
    updated = {"key": key, "value": value, "version": new_version}
    DB["content_properties"][prop_key] = updated
    return updated


def delete_content_property(id: str, key: str) -> None:
    """
    Deletes a property from a content item identified by its key.

    Args:
        id (str): The unique identifier of the content.
        key (str): The key of the property to delete

    Raises:
        TypeError: If 'id' or 'key' is not a string.
        InvalidInputError: If 'id' or 'key' is an empty string or only whitespace.
        ValueError: If the property with the specified key for the given content ID is not found.
    """
    # Input validation
    if not isinstance(id, str):
        raise TypeError("Argument 'id' must be a string.")
    if not id.strip():
        raise InvalidInputError("Argument 'id' cannot be an empty string or only whitespace.")
    if not isinstance(key, str):
        raise TypeError("Argument 'key' must be a string.")
    if not key.strip():
        raise InvalidInputError("Argument 'key' cannot be an empty string or only whitespace.")

    prop_key = f"{id}:{key}"
    if prop_key in DB["content_properties"]:
        del DB["content_properties"][prop_key]
    else:
        raise ValueError(f"Property '{key}' not found for content {id}.")


def create_content_property_for_key(
    id: str, key: str, body: Dict[str, Any]
) -> Dict[str, any]:
    """
    Creates a new content property for a specified key when the version is 1.

    Args:
        id (str): The unique identifier of the content.
        key (str): The key for the property.
        body (Dict[str, Any]): A JSON object representing the property, including version=1

    Returns:
        Dict[str, any]: The created content property object with:
            - key (str): The property key
            - value (Dict[str, Any]): The property value
            - version (int): The property version number (must be 1)

    Raises:
        ValueError: If the content with the specified ID is not found.
    """
    # We'll treat it similarly to create_content_property but with the key param
    content = DB["contents"].get(id)
    if not content:
        raise ValueError(f"Content with id={id} not found.")
    version = body.get("version", {}).get("number", 1)
    value = body.get("value", {})
    prop_key = f"{id}:{key}"
    DB["content_properties"][prop_key] = {
        "key": key,
        "value": value,
        "version": version,
    }
    return DB["content_properties"][prop_key]


def get_content_restrictions_by_operation(
    id: str, expand: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieves all restrictions for a content item, grouped by operation type.

    Args:
        id (str): The ID of the content item.
        expand (Optional[str]): A comma-separated list of additional fields to include.
            This parameter is not utilized in this simulation. Defaults to None.

    Returns:
        Dict[str, Any]: A dictionary containing restrictions grouped by operation type.
            The structure is:
            - read (Dict[str, Any]):
                - restrictions (Dict[str, Any]):
                    - user (List[str]): List of usernames with read access.
                    - group (List[str]): List of group names with read access.
            - update (Dict[str, Any]):
                - restrictions (Dict[str, Any]):
                    - user (List[str]): List of usernames with update access.
                    - group (List[str]): List of group names with update access.

    Raises:
        ValueError: If the content with the specified ID is not found.
    """
    if id not in DB["contents"]:
        raise ValueError(f"Content with id={id} not found.")
    return {
        "read": {"restrictions": {"user": [], "group": []}},
        "update": {"restrictions": {"user": [], "group": []}},
    }


def get_content_restrictions_for_operation(
    id: str,
    operationKey: str,
    expand: Optional[str] = None,
    start: Optional[int] = 0,
    limit: Optional[int] = 100,
) -> Dict[str, Any]:
    """
    Retrieves restrictions for a specific operation on a content item.

    Args:
        id (str): The ID of the content item.
        operationKey (str): The operation type (e.g., "read" or "update").
        expand (Optional[str]): A comma-separated list of additional fields to include.
            This parameter is not utilized in this simulation. Defaults to None.
        start (Optional[int]): The starting index for pagination. Defaults to 0.
        limit (Optional[int]): The maximum number of results to return. Defaults to 100.

    Returns:
        Dict[str, Any]: A dictionary representing the restrictions for the specified operation with the structure:
            - operationKey (str): The operation type ("read" or "update").
            - restrictions (Dict[str, Any]): A dictionary containing restrictions for the specified operation with the structure:
                - user (List[str]): A list of usernames with access.
                - group (List[str]): A list of group names with access.

    Raises:
        ValueError: If the content with the specified ID is not found; if the operation key is invalid.
    """
    if id not in DB["contents"]:
        raise ValueError(f"Content with id={id} not found.")
    if operationKey not in ["read", "update"]:
        raise ValueError(f"OperationKey '{operationKey}' not supported.")
    return {"operationKey": operationKey, "restrictions": {"user": [], "group": []}}
