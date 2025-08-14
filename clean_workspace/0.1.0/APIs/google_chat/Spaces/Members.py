from common_utils.print_log import print_log
# APIs/google_chat/Spaces/Members.py

import sys
import os
from datetime import datetime

sys.path.append("APIs")

from google_chat.SimulationEngine.db import DB

from typing import Optional, Dict, Any, List as TypingList # Renamed to avoid conflict if built-in list is used
from google_chat.SimulationEngine.custom_errors import (
    InvalidParentFormatError, 
    AdminAccessNotAllowedError, 
    MembershipAlreadyExistsError,
    InvalidUpdateMaskError,
    MembershipNotFoundError,
    NoUpdatableFieldsError,
    InvalidPageSizeError,
    AdminAccessFilterError
)
from google_chat.SimulationEngine.models import (
    MembershipInputModel, 
    MemberTypeEnum,
    MembershipPatchModel,
    MembershipUpdateMaskModel
)
from typing import Dict, Any, Optional
from pydantic import ValidationError as PydanticValidationError

# DB and other external dependencies are assumed to be defined elsewhere and accessible.
# For example, DB might be:
# DB = {
#     "Membership": []
# }

def list(
    parent: str,
    pageSize: Optional[int] = None,
    pageToken: Optional[str] = None,
    filter: Optional[str] = None,
    showGroups: Optional[bool] = None,
    showInvited: Optional[bool] = None,
    useAdminAccess: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Lists memberships in a space.

    Args:
        parent (str): Required. The resource name of the space to list memberships for.
            Format: spaces/{space}
        pageSize (Optional[int]): Maximum number of memberships to return.
            If unspecified, at most 100 are returned. Value must be between 1 and 1000, inclusive, if provided.
        pageToken (Optional[str]): Token to retrieve the next page from a previous response.
        filter (Optional[str]): Query filter string to filter memberships by:
            - role = "ROLE_MEMBER" or "ROLE_MANAGER"
            - member.type = "HUMAN" or "BOT"
            You may also use:
            - member.type != "BOT"
            - AND/OR operators (restrictions apply)
            If 'useAdminAccess' is True and a filter is provided, the filter must include
            a condition on 'member.type' (e.g., 'member.type = "HUMAN"' or 'member.type != "BOT"').
        showGroups (Optional[bool]): If True, includes memberships associated with Google Groups.
        showInvited (Optional[bool]): If True, includes memberships in the INVITED state.
        useAdminAccess (Optional[bool]): If True, enables admin privileges for the listing operation.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - "memberships" (TypingList[Dict[str, Any]]): A list of membership objects, where each object contains:
                - "name" (str): Resource name of the membership in format `spaces/{space}/members/{member}`.
                - "state" (str): Membership state, one of: "MEMBERSHIP_STATE_UNSPECIFIED", "JOINED", "INVITED", "NOT_A_MEMBER".
                - "role" (str): Membership role, one of: "MEMBERSHIP_ROLE_UNSPECIFIED", "ROLE_MEMBER", "ROLE_MANAGER".
                - "createTime" (str): Timestamp when the membership was created.
                - "member" (Dict[str, Any]): User details with keys:
                    - "name" (str): Resource name of the user in format `users/{user}`.
                    - "displayName" (str): Display name of the user.
                    - "domainId" (str): Workspace domain ID.
                    - "type" (str): Type of member, one of: "TYPE_UNSPECIFIED", "HUMAN", "BOT".
                    - "isAnonymous" (bool): True if the user is deleted or profile is hidden.
                - "groupMember" (Dict[str, Any], optional): Present if membership is for a Google Group:
                    - "name" (str): Resource name of the group in format `groups/{group}`.
            - "nextPageToken" (str, optional): A token to retrieve the next page of results. 
                                              Absent if there are no more results.
        If no memberships are found (after filtering), returns {"memberships": []}.

    Raises:
        TypeError: If any argument is of an incorrect type.
        InvalidParentFormatError: If 'parent' is not in the format 'spaces/{space}'.
        InvalidPageSizeError: If 'pageSize' is provided and is not between 1 and 1000 (inclusive).
        AdminAccessFilterError: If 'useAdminAccess' is True, 'filter' is provided, but the filter
                                does not include a valid condition on 'member.type'.
    """
    # --- Standard Input Validation ---
    if not isinstance(parent, str):
        raise TypeError("Argument 'parent' must be a string.")
    if not parent: # Check for empty string
        raise InvalidParentFormatError("Argument 'parent' cannot be empty.")
    if not parent.startswith("spaces/"):
        raise InvalidParentFormatError(f"Invalid parent format: '{parent}'. Expected 'spaces/{{space}}'.")
    # Ensure there's something after "spaces/"
    if len(parent.split("spaces/", 1)) < 2 or not parent.split("spaces/", 1)[1]:
        raise InvalidParentFormatError(f"Invalid parent format: '{parent}'. Space ID is missing after 'spaces/'.")


    if pageSize is not None:
        if not isinstance(pageSize, int):
            raise TypeError("Argument 'pageSize' must be an integer if provided.")
        if not (1 <= pageSize <= 1000):
            raise InvalidPageSizeError("Argument 'pageSize' must be between 1 and 1000, inclusive, if provided.")

    if pageToken is not None and not isinstance(pageToken, str):
        raise TypeError("Argument 'pageToken' must be a string if provided.")

    if filter is not None and not isinstance(filter, str):
        raise TypeError("Argument 'filter' must be a string if provided.")

    if showGroups is not None and not isinstance(showGroups, bool):
        raise TypeError("Argument 'showGroups' must be a boolean if provided.")

    if showInvited is not None and not isinstance(showInvited, bool):
        raise TypeError("Argument 'showInvited' must be a boolean if provided.")

    if useAdminAccess is not None and not isinstance(useAdminAccess, bool):
        raise TypeError("Argument 'useAdminAccess' must be a boolean if provided.")

    # --- Helper functions defined inside the method (as per original structure) ---
    def parse_page_token(token: Optional[str]) -> int: # Modified to accept Optional[str]
        if token is None:
            return 0
        try:
            return max(int(token), 0)
        except (ValueError, TypeError): # TypeError if token is not string/int compatible
            return 0 # Or raise an error if malformed token should be an error

    def default_page_size(ps: Optional[int]) -> int: # ps is already validated if not None
        if ps is None:
            return 100
        # Given prior validation, ps is already 1 <= ps <= 1000 or None.
        # This helper's original logic for ps < 0 is now redundant due to validation.
        # return min(ps, 1000) # Simplified: ps is already <= 1000 if not None
        return ps # If pageSize was provided and validated, use it. If None, it's 100.

    def apply_filter(membership: dict, expressions: list) -> bool:
        for field, op, value in expressions:
            if field == "role":
                field_val = membership.get("role", "")
            elif field == "member.type":
                field_val = membership.get("member", {}).get("type", "")
            else:
                continue # Skip unknown fields

            if op == "=":
                if field_val != value:
                    return False
            elif op == "!=":
                if field_val == value:
                    return False
            # else: skip unknown operators
        return True

    def parse_filter(filter_str: str) -> list:
        """
        Very naive parser for filter.
        Splits on 'AND' and 'OR' is not supported across different fields.
        Returns a list of tuples (field, operator, value).
        For example:
            'role = "ROLE_MANAGER" OR role = "ROLE_MEMBER"' -> we can split into multiple expressions
            but for simplicity, we treat OR as multiple acceptable values for the same field,
            and for filters with AND, all conditions must match.
        Here, we assume conditions are separated by 'AND' (case-insensitive).
        """
        expressions = []
        segments = [seg.strip() for seg in filter_str.split("AND")]
        for seg in segments:
            # Look for "=" or "!=" in the segment.
            if "!=" in seg:
                parts = seg.split("!=")
                operator = "!="
            elif "=" in seg:
                parts = seg.split("=")
                operator = "="
            else:
                continue
            if len(parts) < 2:
                continue
            field = parts[0].strip().lower()  # Normalize field name to lowercase
            value = parts[1].strip().strip('"').upper()  # Normalize value to uppercase
            expressions.append((field, operator, value))
        return expressions
    # --- End of helper functions ---


    # --- Business Logic Input Validation (using helpers) ---
    if useAdminAccess and filter: # filter is already known to be a string here if not None
        exprs = parse_filter(filter)
        type_expr_ok = any(
            (
                field.lower() == "member.type" # Case-insensitive field name comparison
                and (
                    (op == "=" and value.upper() == "HUMAN")
                    or (op == "!=" and value.upper() == "BOT")
                )
            )
            for field, op, value in exprs
        )
        if not type_expr_ok:
            raise AdminAccessFilterError(
                'When using admin access with a filter, the filter must include a condition '
                'like \'member.type = "HUMAN"\' or \'member.type != "BOT"\'.'
            )

    # --- Core Logic (adapted from original, validation print/returns removed) ---
    print_log(
        f"Members.list called with parent={parent}, pageSize={pageSize}, pageToken={pageToken}, filter={filter}, showGroups={showGroups}, showInvited={showInvited}, useAdminAccess={useAdminAccess}"
    )

    # 1) Parent format already validated.

    # 2) Start with memberships whose resource name begins with f"{parent}/members/"
    all_memberships = []
    # Assuming DB is accessible, e.g., global or passed in a class context
    # For standalone function, DB would need to be passed or imported
    global DB # Placeholder for how DB might be accessed; ideally, pass as argument or use class member
    for mem in DB.get("Membership", []): # Use .get for safety
        if mem.get("name", "").startswith(f"{parent}/members/"):
            all_memberships.append(mem)

    # 3) If useAdminAccess is true, filter out app memberships.
    if useAdminAccess:
        all_memberships = [
            m for m in all_memberships if not m.get("name", "").endswith("/members/app")
        ]
        # The filter condition for useAdminAccess already validated above.

    # 4) Apply the query filter if provided.
    if filter: # filter is already known to be a string here if not None
        exprs = parse_filter(filter)
        all_memberships = [m for m in all_memberships if apply_filter(m, exprs)]

    # 5) Filter by showGroups and showInvited.
    if showGroups is not None and not showGroups:
        all_memberships = [
            m
            for m in all_memberships
            if not m.get("member", {}).get("name", "").startswith("groups/")
        ]
    if showInvited is not None and not showInvited:
        all_memberships = [
            m for m in all_memberships if m.get("state", "").upper() != "INVITED"
        ]

    # 6) Set pageSize and pageToken.
    # pageSize validation (1-1000) already done. default_page_size now handles None or validated int.
    current_page_size = 100 # Default if pageSize is None
    if pageSize is not None:
        current_page_size = pageSize # Use validated pageSize
    
    ps = default_page_size(pageSize) # This now uses the validated pageSize or None correctly.
                                     # For clarity, let's use the direct value or default
    effective_page_size = pageSize if pageSize is not None else 100

    offset = parse_page_token(pageToken)


    # 7) Apply pagination.
    total = len(all_memberships)
    end = offset + effective_page_size # Use effective_page_size
    page_items = all_memberships[offset:end]
    nextPageToken_val = str(end) if end < total else None # Renamed to avoid conflict with arg

    response = {"memberships": page_items}
    if nextPageToken_val:
        response["nextPageToken"] = nextPageToken_val

    print_log(f"ListMembershipsResponse: {response}")
    return response


def get(name: str, useAdminAccess: Optional[bool] = None) -> Dict[str, Any]:
    """
    Retrieves details about a specific membership in a Chat space.

    Args:
        name (str): Required. The resource name of the membership to retrieve.
            Format:
            - spaces/{space}/members/{member}
            - spaces/{space}/members/app (for the app itself)
            You can use an email address as an alias for {member}, e.g., spaces/{space}/members/user@example.com.
        useAdminAccess (Optional[bool]): If True, runs with the caller's Workspace admin privileges.
            Note: App memberships (i.e., .../members/app) cannot be fetched with admin access.

    Returns:
        Dict[str, Any]: A dictionary representing the membership with the following keys:
            - 'name' (str): Resource name of the membership.
            - 'state' (str): One of:
                - 'MEMBERSHIP_STATE_UNSPECIFIED'
                - 'JOINED'
                - 'INVITED'
                - 'NOT_A_MEMBER'
            - 'role' (str): One of:
                - 'MEMBERSHIP_ROLE_UNSPECIFIED'
                - 'ROLE_MEMBER'
                - 'ROLE_MANAGER'
            - 'createTime' (str): (Optional) Timestamp when the membership was created.
            - 'deleteTime' (str): (Optional) Timestamp when the membership was deleted.
            - 'member' (Dict[str, Any]): User details:
                - 'name' (str): Format: users/{user}
                - 'displayName' (str): Display name of the user.
                - 'domainId' (str): Workspace domain ID.
                - 'type' (str): One of:
                    - 'TYPE_UNSPECIFIED'
                    - 'HUMAN'
                    - 'BOT'
                - 'isAnonymous' (bool): True if the user is deleted or profile is hidden.
            - 'groupMember' (Dict[str, Any]): (Optional) Google Group details:
                - 'name' (str): Format: groups/{group}

        Returns an empty dictionary if the membership is not found or not accessible.
    """
    print_log(f"Members.get called with name={name}, useAdminAccess={useAdminAccess}")

    # 1) Locate the membership in DB
    found = None
    for mem in DB["Membership"]:
        if mem.get("name") == name:
            found = mem
            break

    # 2) If not found, return {}
    if not found:
        print_log("Membership not found => {}")
        return {}

    # Check if membership is "app" and useAdminAccess == True
    # The doc says: "Getting app memberships in a space isn't supported when using admin access."
    # So we skip returning details in that scenario
    if useAdminAccess:
        # If the membership name ends with "/members/app", it's the app membership
        if name.endswith("/members/app"):
            print_log("Admin access used for app membership => not supported => {}")
            return {}

    print_log(f"Found membership => {found}")
    return found


def create(parent: str, membership: Dict[str, Any], useAdminAccess: Optional[bool] = None) -> Dict[str, Any]:
    """
    Creates a membership for a user or group in the specified Chat space.

    Args:
        parent (str): Required. The resource name of the space.
            Format: spaces/{space}
        membership (Dict[str, Any]): Required. Represents the membership to be created, with the following fields:
            - role (str): Optional. Defaults to 'ROLE_MEMBER'. One of:
                - 'MEMBERSHIP_ROLE_UNSPECIFIED'
                - 'ROLE_MEMBER'
                - 'ROLE_MANAGER'
            - state (str): Optional. Defaults to 'INVITED'. One of:
                - 'MEMBERSHIP_STATE_UNSPECIFIED'
                - 'JOINED'
                - 'INVITED'
                - 'NOT_A_MEMBER'
            - deleteTime (str): Optional. Timestamp of deletion.
            - member (Dict[str, Any]): Required. Member information, with fields:
                - name (str): Format: users/{user} or users/app
                - displayName (str): Optional. The user's display name.
                - domainId (str): Optional. Workspace domain ID.
                - type (str): One of:
                    - 'TYPE_UNSPECIFIED'
                    - 'HUMAN'
                    - 'BOT'
                - isAnonymous (bool): Optional. True if the user is deleted or profile is hidden.
            - groupMember (Dict[str, Any]): Optional. Group information, with field:
                - name (str): Format: groups/{group}
        useAdminAccess (Optional[bool]): If True, uses administrator privileges.
            Admin access cannot be used to create memberships for bots or users outside the domain.

    Returns:
        Dict[str, Any]: The created membership object.
            Includes auto-generated 'name' and 'createTime' fields,
            and applied defaults for 'role' and 'state' if not provided.

    Raises:
        TypeError: If 'parent' is not a string, 'membership' is not a dictionary,
                   or 'useAdminAccess' is not a boolean (if provided).
        InvalidParentFormatError: If 'parent' format is invalid.
        PydanticValidationError: If 'membership' dictionary does not conform to the expected structure
                                 or contains invalid values for its fields.
        AdminAccessNotAllowedError: If 'useAdminAccess' is True and an attempt is made to create
                                    a membership for a BOT.
        MembershipAlreadyExistsError: If the membership to be created already exists.
    """
    # --- Input Validation ---
    if not isinstance(parent, str):
        raise TypeError("Parent must be a string.")
    if not isinstance(membership, dict):
        raise TypeError("Membership must be a dictionary.")
    if useAdminAccess is not None and not isinstance(useAdminAccess, bool):
        raise TypeError("useAdminAccess must be a boolean or None.")

    parts = parent.split("/")
    if len(parts) != 2 or parts[0] != "spaces":
        raise InvalidParentFormatError("Invalid parent format. Expected 'spaces/{space}'.")

    try:
        validated_membership_model = MembershipInputModel(**membership)
    except PydanticValidationError as e:
        raise e

    # Convert Pydantic model to dict to work with it similar to the original function
    # This also applies defaults specified in the Pydantic model
    membership_data = validated_membership_model.model_dump(exclude_none=True)

    # Ensure nested 'member' dictionary is present after model dump
    if "member" not in membership_data: # Should not happen if Pydantic model is correct
        raise PydanticValidationError.from_exception_data(
            title="MembershipInputModel",
            line_errors=[{"loc": ("member",), "msg": "Field required", "type": "missing"}]
        )

    # Validate member name format (already handled by Pydantic pattern, but an explicit check can be kept if desired)
    # mem_name = validated_membership_model.member.name (users/USER999 or users/app)
    # This specific check is now part of Pydantic's pattern validation for member.name

    # Business logic validation using validated data
    if useAdminAccess is True:
        if validated_membership_model.member.type == MemberTypeEnum.BOT:
            raise AdminAccessNotAllowedError(
                "Admin access cannot be used to create memberships for a Chat app (BOT)."
            )

    # --- Core Logic (preserved from original, adapted for validated data) ---
    # Auto-generate membership name
    # Original: mem_name = membership["member"]["name"]
    mem_name = validated_membership_model.member.name
    membership_name = f"{parent}/members/{mem_name}"
    membership_data["name"] = membership_name

    # Check for existing membership
    # Assume DB is accessible globally or passed appropriately in a real application
    global DB  # Using global DB as per original code's context
    for m in DB["Membership"]:
        if m.get("name") == membership_name:
            raise MembershipAlreadyExistsError(f"Membership '{membership_name}' already exists.")

    # Set auto-filled fields (role and state defaults are handled by Pydantic model)
    membership_data.setdefault("createTime", datetime.now().isoformat() + "Z")
    
    # If 'role' or 'state' were not in the input 'membership' dict,
    # Pydantic defaults ensure they are in 'membership_data'.
    # If they were in input, Pydantic validated them.

    DB["Membership"].append(membership_data)
    # print(f"Membership created => {membership_data}") # Original had a print
    return membership_data


def patch(
    name: str, updateMask: str, membership: Dict[str, Any], useAdminAccess: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Updates a membership.

    Args:
        name (str): Required. Resource name of the membership to update.
            Format: spaces/{space}/members/{member}
        updateMask (str): Required. Comma-separated list of fields to update.
            Supported values:
            - 'role'
        membership (Dict[str, Any]): Dictionary containing the updated membership fields. Supported structure:
            - name (str): Resource name of the membership.
                Format: spaces/{space}/members/{member}
            - role (str): Optional. One of:
                - 'MEMBERSHIP_ROLE_UNSPECIFIED'
                - 'ROLE_MEMBER'
                - 'ROLE_MANAGER'
            - state (str): Output only. One of:
                - 'MEMBERSHIP_STATE_UNSPECIFIED'
                - 'JOINED'
                - 'INVITED'
                - 'NOT_A_MEMBER'
            - createTime (str): Output only. Timestamp when the membership was created.
            - deleteTime (str): Output only. Timestamp when the membership was deleted.
            - member (Dict[str, Any]): Member details with the following structure:
                - name (str): Format: users/{user}
                - displayName (str): Output only. Display name of the user.
                - domainId (str): Output only. Workspace domain ID.
                - type (str): One of:
                    - 'TYPE_UNSPECIFIED'
                    - 'HUMAN'
                    - 'BOT'
                - isAnonymous (bool): Output only. True if user is deleted or hidden.
            - groupMember (Dict[str, Any]): Optional group information with the following structure:
                - name (str): Format: groups/{group}
        useAdminAccess (Optional[bool]): If True, runs the method using administrator privileges.

    Returns:
        Dict[str, Any]: The updated membership resource with the following structure:
            - name (str): Resource name of the membership.
                Format: spaces/{space}/members/{member}
            - state (str): Membership state, one of:
                - 'MEMBERSHIP_STATE_UNSPECIFIED'
                - 'JOINED'
                - 'INVITED'
                - 'NOT_A_MEMBER'
            - role (str): Membership role, one of:
                - 'MEMBERSHIP_ROLE_UNSPECIFIED'
                - 'ROLE_MEMBER'
                - 'ROLE_MANAGER'
            - createTime (str): Timestamp when the membership was created.
            - deleteTime (str): (Optional) Timestamp when the membership was deleted.
            - member (Dict[str, Any]): User details with the following structure:
                - name (str): Resource name of the user in format users/{user}
                - displayName (str): Display name of the user.
                - domainId (str): Workspace domain ID.
                - type (str): Type of member, one of:
                    - 'TYPE_UNSPECIFIED'
                    - 'HUMAN'
                    - 'BOT'
                - isAnonymous (bool): True if the user is deleted or profile is hidden.
            - groupMember (Dict[str, Any]): (Optional) Google Group details with the following structure:
                - name (str): Resource name of the group in format groups/{group}

        Returns an empty dictionary if the membership is not found or the update cannot be applied.
    """
    print_log(f"Members.patch called with name={name}, updateMask={updateMask}, membership={membership}, useAdminAccess={useAdminAccess}")
    
    # 1) Validate input parameters
    # Validate updateMask with a Pydantic model
    try:
        validated_update_mask = MembershipUpdateMaskModel(updateMask=updateMask)
    except PydanticValidationError as e:
        print_log(f"Invalid updateMask: {e}")
        raise InvalidUpdateMaskError(str(e))
    
    # Validate membership with a Pydantic model
    try:
        validated_membership = MembershipPatchModel(**membership)
    except PydanticValidationError as e:
        print_log(f"Invalid membership: {e}")
        raise NoUpdatableFieldsError(str(e))
    
    # 2) Locate the membership in DB
    found = None
    for mem in DB["Membership"]:
        if mem.get("name") == name:
            found = mem
            break

    # If not found, raise error
    if not found:
        print_log("Membership not found.")
        raise MembershipNotFoundError(f"Membership '{name}' not found")
    
    # 3) Check if membership is "app" and useAdminAccess == True
    # App memberships cannot be modified with admin access
    if useAdminAccess and name.endswith("/members/app"):
        print_log("Admin access used for app membership => not supported => {}")
        raise AdminAccessNotAllowedError("Admin access cannot be used to modify app memberships")
    
    # 4) Determine which fields to update based on the updateMask
    fields_to_update = [field.strip() for field in updateMask.split(',')]
    
    # 5) Apply each field update
    updated = False
    membership_data = validated_membership.model_dump(exclude_none=True)
    
    for field in fields_to_update:
        if field == 'role' and 'role' in membership_data:
            found['role'] = membership_data['role']
            updated = True
            print_log(f"Updated {field} to {membership_data[field]}")
    
    # If no fields were updated, this is unexpected (validation should have caught this)
    if not updated:
        print_log("No fields were updated despite valid updateMask and membership")
        return {}
    
    # 6) Return the updated membership
    print_log(f"Updated membership => {found}")
    return found


def delete(name: str, useAdminAccess: bool = False) -> Dict[str, Any]:
    """
    Deletes a membership from a space. 

    Args:
        name (str): Required. Resource name of the membership to delete.
            Format: spaces/{space}/members/{member}
            Example values:
            - spaces/AAA/members/user@example.com
            - spaces/AAA/members/app
        useAdminAccess (bool): Optional. If True, uses Workspace admin privileges.
            Note: Deleting app memberships using admin access is not supported.

    Returns:
        Dict[str, Any]: The deleted membership resource with the following fields:
            - name (str): Resource name of the membership.
                Format: spaces/{space}/members/{member}
            - state (str): One of:
                - 'MEMBERSHIP_STATE_UNSPECIFIED'
                - 'JOINED'
                - 'INVITED'
                - 'NOT_A_MEMBER'
            - role (str): One of:
                - 'MEMBERSHIP_ROLE_UNSPECIFIED'
                - 'ROLE_MEMBER'
                - 'ROLE_MANAGER'
            - createTime (str): Timestamp when the membership was created.
            - deleteTime (str): (Optional) Timestamp when the membership was deleted.
            - member (Dict[str, Any]): User details:
                - name (str): Format: users/{user}
                - displayName (str): Output only.
                - domainId (str): Output only.
                - type (str): One of:
                    - 'TYPE_UNSPECIFIED'
                    - 'HUMAN'
                    - 'BOT'
                - isAnonymous (bool): True if the user is deleted or profile is hidden.
            - groupMember (Dict[str, Any]): Optional. Group details:
                - name (str): Format: groups/{group}

        Returns an empty dictionary if the membership is not found or deletion is disallowed.
    """
    # 1) Find the membership in the database.
    target = None
    for m in DB["Membership"]:
        if m.get("name") == name:
            target = m
            break

    if not target:
        print_log("Membership not found.")
        return {}

    # 2) If useAdminAccess is true, then deleting an app membership is not supported.
    if useAdminAccess and name.endswith("/members/app"):
        print_log("Deleting app memberships using admin access is not supported.")
        return {}

    # 3) Remove the membership from DB
    DB["Membership"].remove(target)
    print_log(f"Deleted membership: {target}")
    return target
