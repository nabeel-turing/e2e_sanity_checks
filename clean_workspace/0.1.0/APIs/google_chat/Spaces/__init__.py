from common_utils.print_log import print_log
# APIs/google_chat/Spaces/__init__.py

import sys
import re
from datetime import datetime
from typing import Dict, Any

sys.path.append("APIs")

from google_chat.SimulationEngine.db import DB, CURRENT_USER_ID

from google_chat.SimulationEngine.custom_errors import InvalidPageSizeError
from google_chat.SimulationEngine.custom_errors import InvalidSpaceNameFormatError
from google_chat.SimulationEngine.custom_errors import MissingDisplayNameError

from google_chat.SimulationEngine.models import SpaceTypeEnum
from google_chat.SimulationEngine.models import SpaceInputModel

from pydantic import ValidationError


def list(pageSize: int = None, pageToken: str = None, filter: str = None) -> Dict[str, Any]:
    """
    Lists spaces the current user is a member of, with optional filtering and pagination.

    Args:
        pageSize (int, optional): Max number of spaces to return (default 100, max 1000).
                                  Must be between 1 and 1000 if provided.
        pageToken (str, optional): Pagination token (used as an offset).
        filter (str, optional): Filter by space type using 'OR' operator only, no 'AND' operator is allowed. Example:
            'spaceType = "SPACE" OR spaceType = "GROUP_CHAT"'.
            Allowed values for spaceType:
                - "SPACE"
                - "GROUP_CHAT"
                - "DIRECT_MESSAGE"

    Returns:
        Dict[str, Any]:
            "spaces": List of space objects. Each includes:
                - name (str): Format "spaces/{space}"
                - spaceType (str): "SPACE", "GROUP_CHAT", or "DIRECT_MESSAGE"
                - displayName (str, optional)
                - externalUserAllowed (bool, optional)
                - spaceThreadingState (str, optional):
                    "SPACE_THREADING_STATE_UNSPECIFIED", "THREADED_MESSAGES",
                    "GROUPED_MESSAGES", "UNTHREADED_MESSAGES"
                - spaceHistoryState (str, optional):
                    "HISTORY_STATE_UNSPECIFIED", "HISTORY_OFF", "HISTORY_ON"
                - createTime (str, optional)
                - lastActiveTime (str, optional)
                - importMode (bool, optional)
                - adminInstalled (bool, optional)
                - spaceUri (str, optional)
                - predefinedPermissionSettings (str, optional):
                    "PREDEFINED_PERMISSION_SETTINGS_UNSPECIFIED",
                    "COLLABORATION_SPACE", "ANNOUNCEMENT_SPACE"
                - spaceDetails (dict, optional):
                    - description (str, optional)
                    - guidelines (str, optional)
                - membershipCount (dict, optional):
                    - joinedDirectHumanUserCount (int)
                    - joinedGroupCount (int)
                - accessSettings (dict, optional):
                    - accessState (str): "ACCESS_STATE_UNSPECIFIED", "PRIVATE", "DISCOVERABLE"
                    - audience (str, optional)
                - singleUserBotDm (bool, optional)

            "nextPageToken" (str): Token for next page if more results.

        If filter string content is invalid (as processed by internal logic):
            { "error": "<description>" } (This is a return value, not an exception)

    Raises:
        TypeError: If pageSize is not an integer, or
                   pageToken is not a string, or
                   filter is not a string.
        InvalidPageSizeError: If pageSize is provided but is not between 1 and 1000 (inclusive).
    """
    # --- Input Validation ---
    if pageSize is not None:
        if not isinstance(pageSize, int):
            raise TypeError("pageSize must be an integer.")
        if not (1 <= pageSize <= 1000):
            raise InvalidPageSizeError("pageSize must be between 1 and 1000, inclusive.")

    if pageToken is not None:
        if not isinstance(pageToken, str):
            raise TypeError("pageToken must be a string.")

    if filter is not None:
        if not isinstance(filter, str): # Note: Pylint might flag 'filter' as shadowing built-in.
            raise TypeError("filter must be a string.")
    # --- End of Input Validation ---

    # --- Original Core Logic (unchanged) ---
    def parse_space_type_filter(filter_str: str): # Parameter name changed to filter_str for clarity, though original `filter` would also work due to scoping.
        ALLOWED_SPACE_TYPES = {"SPACE", "GROUP_CHAT", "DIRECT_MESSAGE"}
        # Normalize by removing spaces around = and operators
        normalized = filter_str.replace("=", " = ").replace("OR", " OR ")
        # Reject if 'AND' is used
        if re.search(r" AND ", filter_str, re.IGNORECASE): # use filter_str
            return {"error": "'AND' operator is not supported. Use 'OR' instead."}
        # Regex to find all spaceType = "VALUE" or space_type = "VALUE"
        pattern = re.compile(r'(spaceType|space_type)\s*=\s*"([^"]+)"')
        matches = pattern.findall(normalized)
        valid = []
        if not matches:
            # This condition might need review based on desired behavior for empty/malformed filters.
            # For example, if the filter string is non-empty but contains no valid expressions.
            # The original code implies that if `filter` is provided, `matches` should not be empty.
            return {"error": "No valid expressions found"}


        for _, value in matches:
            if value in ALLOWED_SPACE_TYPES:
                valid.append(value)
            else:
                return {"error": f"Invalid space type: '{value}'"}
        
        if not valid and filter_str.strip(): # If original filter string was not empty but we found no valid types
             return {"error": "Filter provided but no valid space types extracted after parsing."}


        return {"space_types": valid}

    user_spaces = []
    # This section assumes DB and CURRENT_USER_ID are accessible.
    # For example, they could be global variables or imported.
    # global DB, CURRENT_USER_ID # If they were actual globals from the same module.
    
    # The original code uses .get('name') on sp and .get('id') on CURRENT_USER_ID,
    # implying they are dictionaries. This is preserved.
    for sp in DB.get("Space", []): # Add .get for safety if DB might not have "Space"
        membership_name = f"{sp.get('name')}/members/{CURRENT_USER_ID.get('id')}"
        found_membership = False
        for mem in DB.get("Membership", []): # Add .get for safety
            if mem.get("name") == membership_name:
                found_membership = True
                break
        if found_membership:
            user_spaces.append(sp)

    if filter: # Outer function's `filter` argument
        parsed_filter = parse_space_type_filter(filter) # Pass the original `filter` argument
        if "error" in parsed_filter:
            return {"error": parsed_filter["error"]}
        space_types = parsed_filter.get("space_types", []) # Use .get for safety
        if space_types: # Only filter if space_types were successfully parsed
            user_spaces = [s for s in user_spaces if s.get("spaceType") in space_types]
        # If space_types is empty (e.g. filter was valid but empty like 'spaceType = ""')
        # this implies no filtering or specific handling depending on parse_space_type_filter logic.
        # Current parse_space_type_filter would return an error if matches is empty but filter_str is not.
        # If parse_space_type_filter returns {"space_types": []} for a valid but effectively empty filter,
        # then all spaces would be returned, which might be intended.

    # Build the response
    # The original code does not implement pagination using pageSize or pageToken.
    # This core logic is preserved as per instructions.
    response = {"spaces": user_spaces}
    next_token = "" # Placeholder as in original
    response["nextPageToken"] = next_token

    return response


#


def search(
    useAdminAccess: bool,
    pageSize: int = None,
    pageToken: str = None,
    query: str = None,
    orderBy: str = None,
) -> dict:
    """
    Searches for Chat spaces in a Google Workspace organization using administrator access.

    Supported fields in the query include:
    - display_name: Uses the HAS (`:`) operator.
    - external_user_allowed: Accepts "true" or "false".
    - create_time, last_active_time: Accepts `=`, `<`, `>`, `<=`, `>=` with timestamps in RFC-3339 format.
    - space_history_state: Accepts specific enum values.
    - space_type: Only "SPACE" is allowed (required).
    - customer: Must be "customers/my_customer" (required).

    Args:
        useAdminAccess (bool): Required. Must be `True`. Enables administrator-only
            access. Requires admin scopes such as:
            - `chat.admin.spaces.readonly`
            - `chat.admin.spaces`
        pageSize (int, optional): The maximum number of spaces to return. If unspecified,
            up to 100 spaces are returned. Maximum allowed value is 1000. Values greater
            than 1000 are capped at 1000. Negative values are ignored and default to 100.
        pageToken (str, optional): A token received from a previous search call.
            Used for pagination; represents an offset.
        query (str): Required. A query string combining fields using the `AND` operator.
            Required conditions:
                - customer = "customers/my_customer"
                - space_type = "SPACE"
            Supported query fields:
                - display_name: e.g., `display_name:"hello world"`
                - create_time: e.g., `create_time >= "2022-01-01T00:00:00Z"`
                - last_active_time: e.g., `last_active_time < "2024-12-01T00:00:00Z"`
                - external_user_allowed: "true" or "false"
                - space_history_state: One of the enum values below
            Operators:
                - Allowed: `=`, `<`, `>`, `<=`, `>=`, `:`
                - Only `AND` is supported between conditions
        orderBy (str, optional): Specifies result ordering. Format:
            `field ASC|DESC`. Supported fields:
            - `membership_count.joined_direct_human_user_count`
            - `last_active_time`
            - `create_time`
            Default is `create_time ASC`.

    Returns:
        dict: A dictionary with the following structure:
            - spaces (List[dict]): A list of matching space objects. Each space includes:
                - name (str): Resource name, e.g., "spaces/AAA".
                - spaceType (str): Type of space. One of:
                    - "SPACE"
                    - "GROUP_CHAT"
                    - "DIRECT_MESSAGE"
                - displayName (str): Optional display name of the space.
                - externalUserAllowed (bool): Whether external users are allowed.
                - spaceThreadingState (str): Threading behavior. One of:
                    - "SPACE_THREADING_STATE_UNSPECIFIED"
                    - "THREADED_MESSAGES"
                    - "GROUPED_MESSAGES"
                    - "UNTHREADED_MESSAGES"
                - spaceHistoryState (str): History configuration. One of:
                    - "HISTORY_STATE_UNSPECIFIED"
                    - "HISTORY_OFF"
                    - "HISTORY_ON"
                - createTime (str): RFC-3339 timestamp when the space was created.
                - lastActiveTime (str): RFC-3339 timestamp of last message activity.
                - importMode (bool): Whether the space was created in import mode.
                - adminInstalled (bool): Whether the space was created by an admin.
                - spaceUri (str): Direct URL to open the space.
                - singleUserBotDm (bool): Whether it's a bot-human direct message.
                - predefinedPermissionSettings (str): Optional predefined permissions. One of:
                    - "PREDEFINED_PERMISSION_SETTINGS_UNSPECIFIED"
                    - "COLLABORATION_SPACE"
                    - "ANNOUNCEMENT_SPACE"
                - spaceDetails (dict):
                    - description (str): Description of the space.
                    - guidelines (str): Rules and expectations.
                - membershipCount (dict):
                    - joinedDirectHumanUserCount (int): Count of joined human users.
                    - joinedGroupCount (int): Count of joined groups.
                - accessSettings (dict):
                    - accessState (str): One of:
                        - "ACCESS_STATE_UNSPECIFIED"
                        - "PRIVATE"
                        - "DISCOVERABLE"
                    - audience (str): Resource name of discoverable audience, e.g., "audiences/default".
            - nextPageToken (str, optional): Token for retrieving the next page of results.

    Raises:
        ValueError: If required query parameters (`customer`, `space_type`) are missing
            or invalid.
        PermissionError: If `useAdminAccess` is not `True`.
    """

    print_log(
        f"search called with useAdminAccess={useAdminAccess}, pageSize={pageSize}, pageToken={pageToken}, query={query}, orderBy={orderBy}"
    )

    def parse_page_token(token: str) -> int:
        try:
            off = int(token)
            return max(off, 0)
        except (ValueError, TypeError):
            return 0

    def default_page_size(ps: int) -> int:
        if ps is None:
            return 100
        if ps < 0:
            return 100
        return min(ps, 1000)

    def matches_field(space: dict, field: str, operator: str, value: str) -> bool:
        # For simplicity, assume fields are stored as in our DB:
        # - "display_name" maps to space["displayName"] (case-insensitive substring match)
        # - "external_user_allowed" maps to space["externalUserAllowed"] (boolean)
        # - "space_history_state" maps to space["spaceHistoryState"]
        # - "create_time" maps to space["createTime"]
        # - "last_active_time" maps to space["lastActiveTime"]
        field = field.strip().lower()
        if field == "display_name":
            # Use HAS operator: value should be a substring (case-insensitive)
            return value.lower() in space.get("displayName", "").lower()
        elif field == "external_user_allowed":
            # Compare boolean (value will be "true" or "false")
            bool_val = True if value.lower() == "true" else False
            return space.get("externalUserAllowed") == bool_val
        elif field in ("create_time", "last_active_time"):
            # Use string comparison (assuming ISO8601 format)
            space_val = (
                space.get("createTime")
                if field == "create_time"
                else space.get("lastActiveTime")
            )
            if operator == "=":
                return space_val == value
            elif operator == ">":
                return space_val > value
            elif operator == "<":
                return space_val < value
            elif operator == ">=":
                return space_val >= value
            elif operator == "<=":
                return space_val <= value
            else:
                return False
        elif field == "space_history_state":
            return space.get("spaceHistoryState") == value
        # For unknown fields, assume no match.
        return True

    def parse_filter(query_str: str) -> list:
        # Split query on "AND"
        segments = [seg.strip() for seg in query_str.split("AND")]
        expressions = []
        for seg in segments:
            # We support two types:
            #   display_name:"text"
            #   external_user_allowed = "true"/"false"
            #   space_history_state = "HISTORY_ON" or "HISTORY_OFF"
            #   create_time, last_active_time comparisons: operator can be one of >, <, >=, <=, =
            # We'll detect operator by checking for one of these symbols.
            for op in [">=", "<=", ">", "<", "="]:
                if op in seg:
                    # Split only once.
                    parts_seg = seg.split(op, 1)
                    field = (
                        parts_seg[0].strip().replace("display_name", "display_name")
                    )  # alias as needed
                    value = parts_seg[1].strip().strip('"')
                    expressions.append((field, op, value))
                    break
            else:
                # Special case: display_name:"text" where operator is actually ':'
                if "display_name:" in seg:
                    parts_seg = seg.split("display_name:", 1)
                    field = "display_name"
                    value = parts_seg[1].strip().strip('"')
                    # For display_name, operator is implicitly HAS.
                    expressions.append((field, "HAS", value))
        return expressions

    def apply_filters(spaces: list, expressions: list) -> list:
        filtered = []
        for sp in spaces:
            match_all = True
            for field, op, value in expressions:
                # Skip expressions for required fields that we've already enforced.
                if field in ("customer", "space_type"):
                    continue
                # For HAS operator, treat it like display_name.
                if op == "HAS":
                    if not matches_field(sp, field, op, value):
                        match_all = False
                        break
                else:
                    if not matches_field(sp, field, op, value):
                        match_all = False
                        break
            if match_all:
                filtered.append(sp)
        return filtered

    # --- Main body of search() ---
    if useAdminAccess is not True:
        print_log("Error: Only admin access is supported (useAdminAccess must be true).")
        return {}

    # Validate required query: must include customer = "customers/my_customer" AND space_type = "SPACE"
    query_lower = query.lower() if query else ""
    if "customer =" not in query_lower or "customers/my_customer" not in query_lower:
        print_log('Error: query must include customer = "customers/my_customer".')
        return {}
    if "space_type" not in query_lower or '"space"' not in query_lower:
        print_log('Error: query must include space_type = "SPACE".')
        return {}

    # Set pageSize and pageToken.
    ps = default_page_size(pageSize)
    offset = parse_page_token(pageToken)

    # 1) Filter DB["Space"] by required fields.
    candidate_spaces = []
    for sp in DB["Space"]:
        # if sp.get("customer", "").lower() != "customers/my_customer":
        #     continue
        if sp.get("spaceType") != "SPACE":
            continue
        candidate_spaces.append(sp)

    # 2) Parse additional filters from query.
    expressions = parse_filter(query)
    candidate_spaces = apply_filters(candidate_spaces, expressions)

    # 3) Ordering.
    # Default order: create_time ASC. Otherwise, orderBy string is parsed.
    if orderBy:
        parts_order = orderBy.split()
        sort_field = parts_order[0].strip().lower()
        sort_order = "ASC"
        if len(parts_order) > 1 and parts_order[1].upper() == "DESC":
            sort_order = "DESC"
    else:
        sort_field = "create_time"
        sort_order = "ASC"

    def sort_key(sp):
        if sort_field == "membership_count.joined_direct_human_user_count":
            return sp.get("membershipCount", {}).get(
                "joined_direct_human_user_count", 0
            )
        elif sort_field == "last_active_time":
            return sp.get("lastActiveTime", "")
        elif sort_field == "create_time":
            return sp.get("createTime", "")
        return ""

    candidate_spaces.sort(key=sort_key, reverse=(sort_order == "DESC"))

    # 4) Pagination: slice the list.
    total = len(candidate_spaces)
    end = offset + ps
    page_items = candidate_spaces[offset:end]
    nextPageToken = str(end) if end < total else None

    result = {"spaces": page_items}
    if nextPageToken:
        result["nextPageToken"] = nextPageToken

    print_log(f"SearchSpacesResponse: {result}")
    return result


#


def get(name: str, useAdminAccess: bool = None) -> Dict[str, Any]:
    """
    Returns details of a Chat space by resource name.

    Args:
        name (str): Required. Resource name of the space. Format: "spaces/{space}".
        useAdminAccess (bool, optional): When True, the caller can view any space
            as an admin. Otherwise, the user must be a member.

    Returns:
        Dict[str, Any]: A space object if found and visible. Includes:
            - name (str)
            - spaceType (str): "SPACE", "GROUP_CHAT", "DIRECT_MESSAGE"
            - displayName (str, optional)
            - externalUserAllowed (bool, optional)
            - spaceThreadingState (str, optional):
                "SPACE_THREADING_STATE_UNSPECIFIED", "THREADED_MESSAGES",
                "GROUPED_MESSAGES", "UNTHREADED_MESSAGES"
            - spaceHistoryState (str, optional):
                "HISTORY_STATE_UNSPECIFIED", "HISTORY_OFF", "HISTORY_ON"
            - createTime (str, optional)
            - lastActiveTime (str, optional)
            - importMode (bool, optional)
            - importModeExpireTime (str, optional)
            - adminInstalled (bool, optional)
            - spaceUri (str, optional)
            - predefinedPermissionSettings (str, optional):
                "PREDEFINED_PERMISSION_SETTINGS_UNSPECIFIED",
                "COLLABORATION_SPACE", "ANNOUNCEMENT_SPACE"
            - spaceDetails (dict, optional):
                - description (str, optional)
                - guidelines (str, optional)
            - membershipCount (dict, optional):
                - joinedDirectHumanUserCount (int)
                - joinedGroupCount (int)
            - accessSettings (dict, optional):
                - accessState (str):
                    "ACCESS_STATE_UNSPECIFIED", "PRIVATE", "DISCOVERABLE"
                - audience (str, optional)
            - singleUserBotDm (bool, optional)
            - permissionSettings (dict, optional):
                - manageMembersAndGroups.managersAllowed (bool, optional)
                - manageMembersAndGroups.membersAllowed (bool, optional)

        If the space is not found or access is denied, returns an empty dict.
    """
    # 1) Find the space in DB["Space"]
    found_space = {}
    for sp in DB["Space"]:
        if sp.get("name") == name:
            found_space = sp
            break

    # 3) If admin privileges are used, return the space directly
    if useAdminAccess:
        return found_space

    # 4) Otherwise, check if the CURRENT_USER_ID is a member of the space
    membership_name = f'{name}/members/{CURRENT_USER_ID.get("id")}'
    print_log(f"Checking membership for {membership_name}")
    is_member = False
    for mem in DB["Membership"]:
        if mem.get("name") == membership_name:
            is_member = True
            break

    # 5) Return the space if user is a member; otherwise, empty
    if is_member:
        return found_space
    else:
        return {}


#


from datetime import datetime
# from typing import Dict, Optional # Usually imported in Pydantic section

# Imported DB and CURRENT_USER_ID from SimulationEngine.db are used
# Do not redefine them here

def create(requestId: str = None, space: dict = {}) -> dict:
    """
    Creates a Chat space.

    Args:
        requestId (str, optional): Unique ID for request. If reused, returns existing space.
        space (dict): Space resource to create. Expected structure defined by SpaceInputModel.
            Required fields include:
            - spaceType (str): "SPACE", "GROUP_CHAT", "DIRECT_MESSAGE"
            Optional fields include:
            - displayName (str, optional): Required and cannot be empty if spaceType is "SPACE".
            - externalUserAllowed (bool, optional)
            - importMode (bool, optional)
            - singleUserBotDm (bool, optional)
            - spaceDetails (dict, optional): {"description": str, "guidelines": str}
            - predefinedPermissionSettings (str, optional): e.g., "COLLABORATION_SPACE"
            - accessSettings (dict, optional): {"audience": str}

    Returns:
        dict: Created space object including various fields.
        Returns {} if creation fails due to business logic (e.g., duplicate displayName after validation).

    Raises:
        TypeError: If requestId is not a string, or if space is not a dictionary.
        pydantic.ValidationError: If the 'space' dictionary does not conform to the
                                  SpaceInputModel schema (e.g., missing 'spaceType',
                                  invalid field types).
        MissingDisplayNameError: If 'spaceType' is "SPACE" and 'displayName' is missing or empty.
    """
    # --- Input Validation ---
    if requestId is not None and not isinstance(requestId, str):
        raise TypeError("requestId must be a string.")

    # Determine the data to validate for the 'space' argument
    space_input_data_for_validation: dict
    if space is None: # Handles explicit call with space=None
        space_input_data_for_validation = {}
    elif isinstance(space, dict):
        space_input_data_for_validation = space
    else:
        # This case should ideally be caught by type hint if static analysis is used,
        # but a dynamic check adds robustness. Pydantic would also fail.
        raise TypeError("space argument must be a dictionary or None.")

    try:
        # Pydantic will validate the structure of 'space_input_data_for_validation'.
        # If it's {}, ValidationError will be raised for missing 'spaceType'.
        validated_space_model = SpaceInputModel(**space_input_data_for_validation)
        # Use .model_dump() to get a dict from the validated model.
        # exclude_none=True ensures that fields explicitly set to None are not in the dict,
        # matching closer to original .get() behavior if we want to distinguish between unset and set to None.
        # exclude_unset=True is better if we only want fields that were provided in the input.
        # For this case, exclude_unset is more appropriate to allow downstream logic to apply defaults.
        space_validated_dict = validated_space_model.model_dump(exclude_unset=True)

    except ValidationError as e:
        raise e # Re-raise Pydantic's ValidationError
    except MissingDisplayNameError as e: # Custom error from model_validator
        raise e
    # --- End of Input Validation ---

    # --- Core Logic (largely preserved, uses space_validated_dict) ---

    # Check for existing space with the same requestId
    if requestId:
        for existing_space_item in DB["Space"]:
            if existing_space_item.get("requestId") == requestId:
                print_log(f"Found existing space with requestId {requestId}")
                return existing_space_item

    # Pydantic model ensures spaceType is valid and present.
    # The displayName conditional requirement is also handled by Pydantic model_validator.
    space_type = space_validated_dict["spaceType"] # Known to exist due to Pydantic
    display_name = space_validated_dict.get("displayName", "").strip() # Get validated display name

    # Check for duplicate displayName (Business logic, not input validation)
    if space_type == SpaceTypeEnum.SPACE.value and display_name: # display_name is known to be non-empty here
        for sp_db_item in DB["Space"]:
            if sp_db_item.get("displayName", "").strip().lower() == display_name.lower():
                print_log(
                    f"Error: A space with displayName '{display_name}' already exists."
                )
                return {} # Original behavior for this business rule failure

    # Generate space name
    space_id = f"SPACE_{len(DB['Space']) + 1}"
    
    # Prepare the new space object. Start with the validated dictionary.
    new_space = space_validated_dict.copy()
    new_space["name"] = f"spaces/{space_id}"

    # Apply defaults for fields that were optional in Pydantic model and not set in input
    if "singleUserBotDm" not in new_space:
        new_space["singleUserBotDm"] = False
    if "externalUserAllowed" not in new_space:
        new_space["externalUserAllowed"] = False
    if "importMode" not in new_space:
        new_space["importMode"] = False
    
    new_space["createTime"] = datetime.utcnow().isoformat() + "Z"

    # Store the requestId if provided
    if requestId:
        new_space["requestId"] = requestId

    # Save the space
    DB["Space"].append(new_space)
    print_log(f"Space created: {new_space['name']}")

    # Create membership for the calling user
    if not new_space.get("importMode") and (
        new_space["spaceType"] != SpaceTypeEnum.DIRECT_MESSAGE.value or not new_space.get("singleUserBotDm")
    ):
        membership_name = f"{new_space['name']}/members/{CURRENT_USER_ID.get('id')}"
        
        current_user_record_for_membership = None
        if CURRENT_USER_ID.get('id'):
            current_user_record_for_membership = next(
                (
                    user_db_item for user_db_item in DB["User"]
                    if user_db_item["name"] == CURRENT_USER_ID.get('id')
                ),
                None,
            )

        membership = {
            "name": membership_name,
            "state": "JOINED",
            "role": "ROLE_MANAGER",
            "member": {
                "name": CURRENT_USER_ID.get("id"),
                "displayName": current_user_record_for_membership.get("displayName") if current_user_record_for_membership else None,
                "type": "HUMAN",
            },
            "createTime": datetime.utcnow().isoformat() + "Z",
        }
        DB["Membership"].append(membership)
        print_log(f"Membership created for calling user: {membership_name}")

    return new_space


#


def setup(setup_body: dict) -> dict:
    """
    Sets up a Chat space and adds initial members.

    Args:
        setup_body (dict): Request body with the following fields:
            - space (dict): Required. Space resource:
                - spaceType (str): "SPACE", "GROUP_CHAT", "DIRECT_MESSAGE"
                - displayName (str, optional)
                - externalUserAllowed (bool, optional)
                - importMode (bool, optional)
                - singleUserBotDm (bool, optional)
                - spaceDetails (dict, optional):
                    - description (str, optional)
                    - guidelines (str, optional)
                - predefinedPermissionSettings (str, optional):
                    "PREDEFINED_PERMISSION_SETTINGS_UNSPECIFIED",
                    "COLLABORATION_SPACE", "ANNOUNCEMENT_SPACE"
                - accessSettings (dict, optional):
                    - audience (str, optional)

            - memberships (List[dict], optional): Memberships to add:
                - member (dict):
                    - name (str): e.g. "users/user@example.com"
                    - type (str): "HUMAN" or "BOT"
                    - displayName (str, optional)
                - role (str, optional):
                    "ROLE_MEMBER", "ROLE_MANAGER"
                - state (str, optional):
                    "JOINED", "INVITED"
                - createTime (str, optional)

    Returns:
        dict: Created space resource with fields:
            - name (str): Format "spaces/{space}"
            - spaceType (str)
            - displayName (str, optional)
            - externalUserAllowed (bool, optional)
            - spaceThreadingState (str, optional)
            - spaceHistoryState (str, optional)
            - createTime (str)
            - lastActiveTime (str, optional)
            - importMode (bool, optional)
            - importModeExpireTime (str, optional)
            - adminInstalled (bool, optional)
            - spaceUri (str, optional)
            - spaceDetails (dict, optional)
            - membershipCount (dict, optional)
            - accessSettings (dict, optional)
            - singleUserBotDm (bool, optional)
            - permissionSettings (dict, optional)

        Returns {} if space already exists or an error occurs.
    """
    print_log(f"setup_space called with setup_body={setup_body}")

    # Extract space details and memberships from the request body.
    space_req = setup_body.get("space", {})
    memberships_req = setup_body.get("memberships", [])

    new_space = create(space=space_req)

    # Remove any membership targeting the calling user.
    for mem in memberships_req:
        mem_member = mem.get("member", {}).get("name", "").strip()
        if mem_member.lower() == CURRENT_USER_ID.get("id").lower():
            print_log("Skipping membership for the calling user (already added).")
            continue

        # Build membership resource name: must be in the format "spaces/{space}/members/{member}"
        membership_name = f"{new_space['name']}/members/{mem_member}"
        mem["name"] = membership_name
        mem.setdefault("role", "ROLE_MEMBER")
        mem.setdefault("state", "INVITED")
        mem.setdefault("createTime", datetime.utcnow().isoformat() + "Z")
        DB["Membership"].append(mem)
        print_log(f"Added membership: {membership_name}")

    return new_space


#


def patch(
    name: str, updateMask: str, space_updates: dict, useAdminAccess: bool = False
) -> dict:
    """
    Updates a Chat space.

    Args:
        name (str): Required. Resource name of the space. Format: "spaces/{space}".
        updateMask (str): Required. Comma-separated list of field paths to update, or "*" to update all supported:
            - "space_details"
            - "display_name"
            - "space_type"
            - "space_history_state"
            - "access_settings.audience"
            - "permission_settings"
        space_updates (dict): Space object with updated field values.
        useAdminAccess (bool, optional): Run as admin. Some update masks are restricted.

    Returns:
        dict: Updated space object, including:
            - name (str)
            - displayName (str, optional)
            - spaceType (str): "SPACE", "GROUP_CHAT", "DIRECT_MESSAGE"
            - externalUserAllowed (bool, optional)
            - spaceDetails (dict, optional):
                - description (str, optional)
                - guidelines (str, optional)
            - spaceThreadingState (str, optional)
            - spaceHistoryState (str, optional):
                "HISTORY_STATE_UNSPECIFIED", "HISTORY_OFF", "HISTORY_ON"
            - createTime (str)
            - lastActiveTime (str, optional)
            - accessSettings (dict, optional):
                - audience (str, optional)
                - accessState (str): "PRIVATE", "DISCOVERABLE"
            - permissionSettings (dict, optional)
            - singleUserBotDm (bool, optional)
            - importMode (bool, optional)
            - importModeExpireTime (str, optional)
            - spaceUri (str, optional)
            - adminInstalled (bool, optional)
            - membershipCount (dict, optional)

        Returns {} if space is not found or validation fails.
    """
    print_log(
        f"patch_space called with name={name}, updateMask={updateMask}, useAdminAccess={useAdminAccess}, space_updates={space_updates}"
    )

    # 1) Locate the space in DB by matching the name exactly.
    target_space = None
    for sp in DB["Space"]:
        if sp.get("name") == name:
            target_space = sp
            break
    if not target_space:
        print_log("Space not found.")
        return {}

    # 2) Parse the updateMask.
    if updateMask.strip() == "*":
        # Update all supported fields.
        masks = [
            "space_details",
            "display_name",
            "space_type",
            "space_history_state",
            "access_settings.audience",
            "permission_settings",
        ]
    else:
        masks = [m.strip() for m in updateMask.split(",")]

    # 3) Update each supported field.
    for mask in masks:
        if mask == "space_details":
            # Update the description inside spaceDetails.
            # Check if "spaceDetails" exists in the request body and contains "description".
            if (
                "spaceDetails" in space_updates
                and "description" in space_updates["spaceDetails"]
            ):
                new_desc = space_updates["spaceDetails"]["description"]
                # Limit description to 150 characters.
                target_space.setdefault("spaceDetails", {})["description"] = new_desc[
                    :150
                ]
            else:
                print_log("No spaceDetails.description provided; skipping.")
        elif mask == "display_name":
            # Update displayName if the current spaceType is "SPACE".
            if target_space.get("spaceType") == "SPACE":
                if "displayName" in space_updates:
                    target_space["displayName"] = space_updates["displayName"]
                else:
                    print_log("displayName not provided in updates; skipping.")
            else:
                print_log(
                    "displayName update is only supported for spaces of type SPACE; skipping."
                )
        elif mask == "space_type":
            # Allowed only if current spaceType is GROUP_CHAT and new value is SPACE.
            current_type = target_space.get("spaceType")
            new_type = space_updates.get("spaceType")
            if current_type == "GROUP_CHAT" and new_type == "SPACE":
                # Additionally, if updating displayName along with space_type, ensure it's non-empty.
                if (
                    "displayName" in space_updates
                    and space_updates["displayName"].strip() != ""
                ):
                    target_space["spaceType"] = "SPACE"
                else:
                    print_log(
                        "Invalid update: displayName must be non-empty when changing space_type."
                    )
                    return {}
            else:
                print_log(
                    "Invalid space_type update: Only GROUP_CHAT -> SPACE is supported; skipping."
                )
        elif mask == "space_history_state":
            # Updates the space history state. Per doc, this must be updated alone.
            # (Here, we do not enforce the "alone" requirement.)
            if "spaceHistoryState" in space_updates:
                target_space["spaceHistoryState"] = space_updates["spaceHistoryState"]
            else:
                print_log("spaceHistoryState not provided; skipping.")
        elif mask == "access_settings.audience":
            # Updates accessSettings.audience. Supported only for spaces with type SPACE.
            if target_space.get("spaceType") == "SPACE":
                if (
                    "accessSettings" in space_updates
                    and "audience" in space_updates["accessSettings"]
                ):
                    target_space.setdefault("accessSettings", {})["audience"] = (
                        space_updates["accessSettings"]["audience"]
                    )
                else:
                    print_log("access_settings.audience not provided; skipping.")
            else:
                print_log(
                    "access_settings.audience update is supported only for spaces of type SPACE; skipping."
                )
        elif mask == "permission_settings":
            # Replaces the entire permissionSettings object.
            if "permissionSettings" in space_updates:
                target_space["permissionSettings"] = space_updates["permissionSettings"]
            else:
                print_log("permission_settings not provided; skipping.")
        else:
            print_log(f"Unsupported update mask field: {mask}; skipping.")

    print_log(f"Updated space: {target_space}")
    return target_space


#


def delete(name: str, useAdminAccess: bool = None) -> Dict[str, Any]:
    """
    Deletes a Chat space and all its child resources.

    Args:
        name (str): Required. Resource name of the space. Format: "spaces/{space}".
        useAdminAccess (bool, optional): When True, allows deletion without membership check.

    Returns:
        Dict[str, Any]: {} (empty dict) to indicate success or failure (space not found or unauthorized).

    Behavior:
        - Removes the space from DB.
        - Deletes all related memberships, messages, reactions, and attachments
          whose resource names begin with the space's name.
        - If not admin, caller must be a space member to delete it.

    Raises:
        - TypeError: If 'name' is not a string, or if 'useAdminAccess' is not a boolean or None.
        - ValueError: If 'name' is an empty string.
        - InvalidSpaceNameFormatError: If 'name' does not match the expected format 'spaces/{space_id}'.
    """

    # --- Input Validation ---
    if not isinstance(name, str):
        raise TypeError("Argument 'name' must be a string.")
    if not name:
        raise ValueError("Argument 'name' cannot be an empty string.")
    if not re.match(r"^spaces/[^/]+$", name):
        raise InvalidSpaceNameFormatError(
            f"Argument 'name' ('{name}') is not in the expected format 'spaces/{{space_id}}'."
        )

    if useAdminAccess is not None and not isinstance(useAdminAccess, bool):
        raise TypeError("Argument 'useAdminAccess' must be a boolean or None.")
    # --- End of Input Validation ---

    print_log(
        f"Deleting space: {name}, useAdminAccess={useAdminAccess}, CURRENT_USER_ID={CURRENT_USER_ID.get('id')}"
    )

    # 1) Find the space
    target_space = None
    for sp in DB["Space"]:
        if sp.get("name") == name:
            target_space = sp
            break

    # 2) If space not found, return {}
    if not target_space:
        print_log(f"No space found with name={name}")
        return {}

    # 3) If not admin, user must be a member
    if not useAdminAccess and CURRENT_USER_ID:
        # Check membership
        membership_name = f"{name}/members/{CURRENT_USER_ID.get('id')}"
        is_member = False
        for mem in DB["Membership"]:
            if mem.get("name") == membership_name:
                is_member = True
                break
        if not is_member:
            print_log(
                f"User {CURRENT_USER_ID.get('id')} is not a member of {name} => unauthorized."
            )
            return {}

    # 4) Remove space from DB
    DB["Space"].remove(target_space)
    print_log(f"Space '{name}' removed from DB.")

    # 5) Remove all child resources referencing this space
    #    We'll do it by checking membership, message, reaction names that start with "spaces/SPACE_ID"
    to_remove_memberships = []
    for m in DB["Membership"]:
        if m.get("name", "").startswith(name + "/"):
            to_remove_memberships.append(m)
    for m in to_remove_memberships:
        DB["Membership"].remove(m)
        print_log(f"Removed membership: {m['name']}")

    to_remove_messages = []
    for msg in DB["Message"]:
        if msg.get("name", "").startswith(name + "/"):
            to_remove_messages.append(msg)
    for msg in to_remove_messages:
        DB["Message"].remove(msg)
        print_log(f"Removed message: {msg['name']}")

    # If there are Reaction or Attachment resources, we do similarly
    to_remove_reactions = []
    if "Reaction" in DB:
        for r in DB["Reaction"]:
            if r.get("name", "").startswith(name + "/"):
                to_remove_reactions.append(r)
        for r in to_remove_reactions:
            DB["Reaction"].remove(r)
            print_log(f"Removed reaction: {r['name']}")

    # 6) Return empty response to indicate success
    print_log(f"Space '{name}' and all child resources deleted.")
    return {}
