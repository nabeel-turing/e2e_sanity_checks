# canva/Canva/Design/__init__.py
import time
from typing import Optional, Dict, Any, List
import uuid
import sys
import os

sys.path.append("APIs")

from canva.SimulationEngine.db import DB
from canva.SimulationEngine.models import DesignTypeInputModel
from canva.SimulationEngine.custom_errors import InvalidAssetIDError, InvalidTitleError, InvalidQueryError, InvalidOwnershipError, InvalidSortByError
from pydantic import ValidationError

from canva.SimulationEngine.models import DesignTypeInputModel
from canva.SimulationEngine.custom_errors import InvalidAssetIDError, InvalidTitleError, InvalidDesignIDError
from pydantic import ValidationError


def create_design(design_type: dict, asset_id: str, title: str) -> Dict[str, Any]:
    """
    Creates a new design with specified design type, asset, and title.

    Args:
        design_type (dict): The design type to use with the following key:
            - "preset": Accepted values for preset are:
                - doc
                - whiteboard
                - presentation
                - canvas
                - banner
                - flyer
                - social
                - video
                - presentation
                - infographic
                - poster
        asset_id (str): The ID of the asset (e.g., image) to include in the design.
                        Must be a non-empty string.
        title (str): Title of the design. Must be 1–255 characters.

    Returns:
        Dict[str, Any]: Contains metadata for the newly created design:
            - id (str): Design ID.
            - design_type (dict): The validated and processed design_type input.
            - asset_id (str)
            - title (str)
            - created_at (int): Unix timestamp.
            - updated_at (int): Unix timestamp.

    Raises:
        pydantic.ValidationError: If 'design_type' is not a valid dictionary or
                                  does not conform to the DesignTypeInputModel structure.
        TypeError: If 'asset_id' or 'title' are not strings.
        InvalidAssetIDError: If 'asset_id' is an empty string.
        InvalidTitleError: If 'title' length is not between 1 and 255 characters.
    """
    # --- Input Validation ---

    # 1. Validate 'design_type' using Pydantic
    if not isinstance(design_type, dict):
        raise TypeError("Input should be a valid dictionary")
    
    # 2. Validate 'asset_id' (standard type and custom value checks)
    if not isinstance(asset_id, str):
        raise TypeError("asset_id must be a string.")
    if not asset_id:  # Check for empty string
        raise InvalidAssetIDError("asset_id cannot be empty.")

    # 3. Validate 'title' (standard type and custom value checks)
    if not isinstance(title, str):
        raise TypeError("title must be a string.")
    if not (1 <= len(title) <= 255):
        raise InvalidTitleError(
            f"title must be between 1 and 255 characters long. Received length: {len(title)}."
        )

    validated_design_type_model = DesignTypeInputModel.model_validate(design_type)

    # --- Core Function Logic (Preserved) ---
    design_id = str(uuid.uuid4())
    timestamp = int(time.time())

    new_design = {
        "id": design_id,
        # Use the validated Pydantic model's dictionary representation.
        # model_dump() creates a dict from the model.
        # exclude_none=True means fields with None value won't be in the dict.
        "design_type": validated_design_type_model.model_dump(exclude_none=True),
        "asset_id": asset_id,
        "title": title,
        "created_at": timestamp,
        "updated_at": timestamp,
    }

    # DB is assumed to exist in the broader application scope.
    # For example: global DB; or DB passed as dependency.
    # This line remains as per original logic.
    DB["Designs"][design_id] = new_design

    return new_design


def list_designs(
    query: Optional[str] = None,
    ownership: str = "any",
    sort_by: str = "relevance",
) -> List[Dict[str, str]]:
    """
    Lists user-owned and shared designs, optionally filtered and sorted.

    Args:
        query (Optional[str]): Search term to filter designs by title (max length: 255).
        ownership (str): Filter by ownership - "any", "owned", or "shared".
                               Defaults to "any".
        sort_by (str): Sort options - "relevance", "modified_descending", "modified_ascending",
                       "title_descending", "title_ascending". Defaults to "relevance".

    Returns:
        List[Dict[str, str]]: A list of design metadata entries, each containing:
            - id (str)
            - title (str)
            - created_at (int)
            - updated_at (int)
            - thumbnail (dict, optional)
            - owner (dict): { user_id, team_id }
            - urls (dict): { edit_url, view_url }
        Returns None if no designs are found after filtering.

    Raises:
        TypeError: If 'query' (when not None), 'ownership', or 'sort_by' are not strings.
        InvalidQueryError: If 'query' exceeds the maximum length of 255 characters.
        InvalidOwnershipError: If 'ownership' is not one of the allowed values
                               ("any", "owned", "shared").
        InvalidSortByError: If 'sort_by' is not one of the allowed values
                            ("relevance", "modified_descending", "modified_ascending",
                             "title_descending", "title_ascending").
    """
    # --- Input Validation ---
    # Validate 'query'
    if query is not None:
        if not isinstance(query, str):
            raise TypeError("query must be a string.")
        if len(query) > 255:
            raise InvalidQueryError("query exceeds maximum length of 255 characters.")

    # Validate 'ownership'
    if not isinstance(ownership, str):
        raise TypeError("ownership must be a string.")
    allowed_ownership_values = ["any", "owned", "shared"]
    if ownership not in allowed_ownership_values:
        raise InvalidOwnershipError(
            f"ownership must be one of {allowed_ownership_values}. Received: '{ownership}'"
        )

    # Validate 'sort_by'
    if not isinstance(sort_by, str):
        raise TypeError("sort_by must be a string.")
    allowed_sort_by_values = [
        "relevance",
        "modified_descending",
        "modified_ascending",
        "title_descending",
        "title_ascending",
    ]
    if sort_by not in allowed_sort_by_values:
        raise InvalidSortByError(
            f"sort_by must be one of {allowed_sort_by_values}. Received: '{sort_by}'"
        )
    # --- End of Input Validation ---

    # --- Original Core Logic ---
    # This line assumes DB is defined elsewhere and accessible.
    # Per instructions, DB definitions or stubs are not to be generated.
    designs = list(DB["Designs"].values())


    # Filtering by ownership
    if ownership == "owned":
        designs = [d for d in designs if d.get("owner", {}).get("user_id")]
    elif ownership == "shared":
        designs = [d for d in designs if not d.get("owner", {}).get("user_id")]

    # Filtering by search query
    if query:
        designs = [d for d in designs if query.lower() in d["title"].lower()]

    # Sorting options
    # "relevance" is the default and implies no specific sort here,
    # or a sort handled by the data source if `DB` were a real database.
    # Since "relevance" implies no specific key-based sort in this Python code,
    # we only handle other explicit sort options.
    if sort_by == "modified_descending":
        designs.sort(key=lambda x: x["updated_at"], reverse=True)
    elif sort_by == "modified_ascending":
        designs.sort(key=lambda x: x["updated_at"], reverse=False)
    elif sort_by == "title_descending":
        designs.sort(key=lambda x: x["title"], reverse=True)
    elif sort_by == "title_ascending":
        designs.sort(key=lambda x: x["title"], reverse=False)

    # Original return behavior: returns None if designs list is empty
    return designs if designs else None


def get_design(design_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves metadata for a single design.

    Args:
        design_id (str): The ID of the design. Must be a non-empty string.

    Returns:
        Optional[Dict[str, Any]]: If found, returns:
            - design (dict):
                - id (str)
                - title (str, optional)
                - created_at (int)
                - updated_at (int)
                - thumbnail (dict, optional)
                - owner (dict): { user_id, team_id }
                - urls (dict): { edit_url, view_url }
                - page_count (int, optional)
        Otherwise, returns None.

    Raises:
        TypeError: If `design_id` is not a string.
        InvalidDesignIDError: If `design_id` is an empty string.
    """
    # --- Input Validation ---
    if not isinstance(design_id, str):
        raise TypeError("design_id must be a string.")
    if not design_id: # Check for empty string
        raise InvalidDesignIDError("design_id cannot be an empty string.")
    # --- End of Input Validation ---

    design = DB["Designs"].get(design_id)
    if design:
        return {"design": design}
    return None


def get_design_pages(
    design_id: str, offset: int = 1, limit: int = 50
) -> Optional[Dict[str, List[Dict[str, str]]]]:
    """
    Retrieves pages from a design, with support for pagination.

    Args:
        design_id (str): The ID of the design to retrieve pages from.
        offset (int): The index of the first page to return (1-based). Default is 1.
                      Min: 1, Max: 500.
        limit (int): The number of pages to return. Default is 50.
                     Min: 1, Max: 200.

    Returns:
        Optional[Dict[str, List[Dict[str, str]]]]: If pages are found, returns:
            - pages (list of dicts):
                - index (int)
                - thumbnail (dict, optional):
                    - width (int)
                    - height (int)
                    - url (str)
        Otherwise, returns None.
    """
    design = DB["Designs"].get(design_id)
    if design and "pages" in design:
        pages = list(design["pages"].values())
        offset = (
            max(1, min(offset, len(pages))) - 1
        )  # Ensure offset is within valid range
        limit = max(1, min(limit, 200))  # Ensure limit is within allowed range
        return {"pages": pages[offset : offset + limit]}
    return None
