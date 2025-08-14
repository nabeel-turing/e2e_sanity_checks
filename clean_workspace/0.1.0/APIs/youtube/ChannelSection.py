from typing import Dict, List, Optional
from youtube.SimulationEngine.custom_errors import InvalidPartParameterError
from youtube.SimulationEngine.db import DB
from youtube.SimulationEngine.utils import generate_random_string, generate_entity_id
from typing import Optional, Dict, Any, List


"""
    Handles YouTube Channel Sections API operations.
    
    This class provides methods to manage channel sections, which are customizable
    sections that appear on a YouTube channel page.
"""


def list(
    part: str,
    channel_id: Optional[str] = None,
    hl: Optional[str] = None,
    section_id: Optional[str] = None,
    mine: bool = False,
    on_behalf_of_content_owner: Optional[str] = None,
) -> Dict[str, List[Dict]]:
    """
    Retrieves a list of channel sections with optional filters.

    Args:
        part (str): The part parameter specifies the channelSection resource properties that the API response will include.
              It should be a comma-separated string of valid parts (e.g., "id,snippet,contentDetails").
              At least one specified part must be valid. An empty string, a string consisting only of
              commas/whitespace, or a string with no valid parts after parsing will raise an error.
        channel_id (Optional[str]): The channelId parameter specifies a YouTube channel ID.
                    The API will only return that channel's sections.
        hl (Optional[str]): The hl parameter instructs the API to retrieve localized resource metadata
            for a specific application language that the YouTube website supports.
        section_id (Optional[str]): The id parameter specifies a comma-separated list of the YouTube channel section ID(s)
                    for the resource(s) that are being retrieved. This is expected as a single string.
                    The original core logic appears to treat this as a single ID for filtering if provided,
                    rather than parsing a list of IDs from this string.
        mine (bool): The mine parameter can be used to instruct the API to only return channel sections
              owned by the authenticated user.
        on_behalf_of_content_owner (Optional[str]): The onBehalfOfContentOwner parameter indicates that the request's
                                     authorization credentials identify a YouTube CMS user who is acting
                                     on behalf of the content owner specified in the parameter value.

    Returns:
        Dict[str, List[Dict]]: A dictionary containing:
            - items: List of channel section objects matching the filter criteria.
            Each channel section object's structure depends on the 'part' parameter and API specifics. Example fields:
                - id: Unique section identifier
                - snippet: Section details (channelId, title, position, type)
                - contentDetails: Additional section content details.

    Raises:
        TypeError: If any argument is of an incorrect type (e.g., 'part' is not a string,
                   'mine' is not a boolean).
        InvalidPartParameterError: If the 'part' parameter is an empty string, malformed (e.g., consists
                                   only of commas or whitespace), or if none of its comma-separated components
                                   are valid. Valid part components are "id", "snippet", "contentDetails".
        KeyError: If the database interaction leads to a KeyError (e.g., if `DB.get` raises it,
                  potentially indicating the database is not properly initialized or an essential
                  key is missing). This error is propagated from the underlying database access.
    """
    

    # --- Core Logic (preserved from original function) ---
    # The original function's initial validation for 'part' (which returned a dict)
    # is now replaced by the more robust validation section above (which raises exceptions).
    # The 'part' string argument itself is passed to the core logic as is; its content validity
    # and basic format are ensured by the preceding checks.

    # --- Input Validation ---
    if not isinstance(part, str):
        raise TypeError("Parameter 'part' must be a string.")
    
    # Check if part is effectively empty after stripping whitespace
    if not part.strip():
        raise InvalidPartParameterError(
            "Parameter 'part' cannot be empty or consist only of whitespace."
        )

    valid_parts = ["id", "snippet", "contentDetails"]
    # Parse 'part' into components: split by comma, strip whitespace from each, filter out empty strings
    # (e.g., from "part1,,part2" or " part1 , part2 ").
    parsed_part_components = [p.strip() for p in part.split(",") if p.strip()]

    if not parsed_part_components:
        # This case handles inputs like "," or ", , ," which result in no valid components after parsing.
        raise InvalidPartParameterError(
            f"Parameter 'part' resulted in no valid components after parsing. Original value: '{part}'"
        )

    if not any(p_comp in valid_parts for p_comp in parsed_part_components):
        raise InvalidPartParameterError(
            f"Invalid part parameter"
        )

    if channel_id is not None and not isinstance(channel_id, str):
        raise TypeError("Parameter 'channel_id' must be a string or None.")
    if hl is not None and not isinstance(hl, str):
        raise TypeError("Parameter 'hl' must be a string or None.")
    if section_id is not None and not isinstance(section_id, str):
        # The docstring implies section_id could be a "comma-separated list", but the type hint is str.
        # The core logic treats it as a single ID. Validation here just checks it's a string if provided.
        raise TypeError("Parameter 'section_id' must be a string or None.")
    if not isinstance(mine, bool):
        raise TypeError("Parameter 'mine' must be a boolean.")
    if on_behalf_of_content_owner is not None and not isinstance(on_behalf_of_content_owner, str):
        raise TypeError("Parameter 'on_behalf_of_content_owner' must be a string or None.")

    filtered_sections = []
    # DB is assumed to be an existing database interface object, globally available or imported.
    sections = DB.get("channelSections", {}) # This call might raise KeyError as per original docstring.

    # Apply filters
    for section_id_key, section_data in sections.items():
        if section_id and section_id != section_id_key:
            continue
        if (
            channel_id
            and section_data.get("snippet", {}).get("channelId") != channel_id
        ):
            continue
        if mine and not section_data.get("snippet", {}).get("mine"): # Handles 'mine' key possibly missing
            continue
        
        # Note: 'on_behalf_of_content_owner' is not used in the provided filtering logic. This is preserved.
        # Note: The 'part' parameter is typically used to determine which fields to include in the response items.
        # The provided core logic snippet does not show 'part' being used to shape 'section_data' before appending.
        # This behavior (or lack thereof) is preserved.
        filtered_sections.append(section_data)

    return {"items": filtered_sections}


def delete(
    section_id: str, on_behalf_of_content_owner: Optional[str] = None
) -> Dict[str, bool]:
    """
    Deletes a channel section from the simulated database.

    Args:
        section_id (str): The unique identifier of the channel section to delete.
        on_behalf_of_content_owner (Optional[str]): Content owner ID for CMS user operations.

    Returns:
        Dict[str, bool]: A dictionary indicating the outcome.
            - success (bool): if the operation was successful.
            
    Raises:
        TypeError: If 'section_id' is not a string.
        TypeError: If 'on_behalf_of_content_owner' is provided and is not a string.
    """
    # --- Input Validation ---
    if not isinstance(section_id, str):
        raise TypeError("section_id must be a string.")

    if on_behalf_of_content_owner is not None and not isinstance(on_behalf_of_content_owner, str):
        raise TypeError("on_behalf_of_content_owner must be a string if provided.")
    # --- End of Input Validation ---

    # Assuming DB is a dictionary-like structure accessible in this scope.
    # Example: DB = {"channelSections": {"some_id": {}}}
    if section_id not in DB.get("channelSections", {}):
        # This KeyError is handled internally by the function's original logic
        # and converted into a dictionary response. It does not propagate as
        # a KeyError exception that the caller needs to catch.
        raise KeyError(
            f"Channel section ID: {section_id} not found in the database."
        )

    del DB["channelSections"][section_id]
    return {"success": True}


def insert(
    part: str,
    snippet: str,
    on_behalf_of_content_owner: Optional[str] = None,
    on_behalf_of_content_owner_channel: Optional[str] = None,
) -> Dict[str, any]:
    """
    Inserts a new channel section.

    Args:
        part (str): The part parameter specifies the channelSection resource properties that the API response will include.
        snippet (str): The snippet object contains details about the channel section.
        on_behalf_of_content_owner (Optional[str]): The onBehalfOfContentOwner parameter indicates that the request's authorization credentials identify a YouTube CMS user who is acting on behalf of the content owner specified in the parameter value. Currently not used!
        on_behalf_of_content_owner_channel (Optional[str]): The onBehalfOfContentOwnerChannel parameter specifies the YouTube channel ID of the channel to which the user is being added. Currently not used!

    Returns:
        Dict[str, any]: A dictionary containing:
            on success
                - success (bool): Whether the operation was successful
                - channelSection (Dict): The newly created channel section object
            on error
                - error (str): Error message if the operation failed

    Raises:
        ValueError: If part parameter is invalid or snippet is malformed
        KeyError: If the database is not properly initialized
    """
    try:
        if part not in ["snippet", "contentDetails"]:
            raise ValueError(
                "Invalid part parameter. Must be one of: snippet, contentDetails"
            )

        new_id = generate_entity_id("channelSection")
        new_section = {"id": new_id, "snippet": snippet}
        DB.setdefault("channelSections", {})[new_id] = new_section
        return {"success": True, "channelSection": new_section}
    except KeyError as e:
        return {"error": f"Database error: {str(e)}"}
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def update(
    part: str,
    section_id: str,
    snippet: Optional[str] = None,
    on_behalf_of_content_owner: Optional[str] = None,
) -> Dict[str, str]:
    """
    Updates a channel section.

    Args:
        part (str): The part parameter specifies the channelSection resource properties that the API response will include.
        section_id (str): The ID of the channel section to update.
        snippet (Optional[str]): The snippet object contains details about the channel section.
        on_behalf_of_content_owner (Optional[str]): The onBehalfOfContentOwner parameter indicates that the request's authorization credentials identify a YouTube CMS user who is acting on behalf of the content owner specified in the parameter value. Currently not used !

    Returns:
        Dict[str, str]: A dictionary containing:
            - success (str): Success message if the update was successful
            - error (str): Error message if the update failed

    Raises:
        ValueError: If part parameter is invalid or snippet is malformed
        KeyError: If the section_id doesn't exist in the database
    """
    try:
        if part not in ["snippet", "contentDetails"]:
            raise ValueError(
                "Invalid part parameter. Must be one of: snippet, contentDetails"
            )

        if section_id not in DB.get("channelSections", {}):
            raise KeyError(
                f"Channel section ID: {section_id} not found in the database."
            )

        if snippet:
            DB["channelSections"][section_id]["snippet"] = snippet

        return {"success": f"Channel section ID: {section_id} updated successfully."}
    except KeyError as e:
        return {"error": str(e)}
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
