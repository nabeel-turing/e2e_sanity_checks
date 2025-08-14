from typing import Dict, Any, Optional
from .SimulationEngine.db import DB

"""
API simulation for the '/organizationAcls' resource.
"""

def get_organization_acls_by_role_assignee(query_field: str,
                                            role_assignee: str,
                                            projection: Optional[str] = None,
                                            start: int = 0,
                                            count: int = 10) -> Dict[str, Any]:
    """
    Retrieves ACL records by roleAssignee URN with optional field projection and pagination. Retrieve information about the roles and permissions that a specific LinkedIn member (the "role assignee") has within one or more organizations on LinkedIn

    Args:
        query_field (str): Query parameter expected to be 'roleAssignee'.
        role_assignee (str): URN of the person whose ACL records are requested.
        projection (Optional[str]): Field projection syntax for controlling which fields to return.
            The projection string should consist of comma-separated field names and may optionally
            be enclosed in parentheses. Defaults to None.
        start (int): Starting index for pagination. Defaults to 0.
        count (int): Number of items to return. Defaults to 10.

    Returns:
        Dict[str, Any]:
        - If query_field is not 'roleAssignee', returns a dictionary with the key "error" and the value "Invalid query parameter. Expected 'roleAssignee'."
        - On successful retrieval, returns a dictionary with the following keys and value types:
            - 'data' (List[Dict[str, Any]]): List of ACL record dictionaries with keys:
                - 'aclId' (str): ACL record's unique identifier.
                - 'roleAssignee' (str): URN of the person assigned the role (e.g., 'urn:li:person:1').
                - 'role' (str): Role assigned to the person (one of 'ADMINISTRATOR', 'DIRECT_SPONSORED_CONTENT_POSTER', 'RECRUITING_POSTER', 'LEAD_CAPTURE_ADMINISTRATOR', 'LEAD_GEN_FORMS_MANAGER', 'ANALYST', 'CURATOR', 'CONTENT_ADMINISTRATOR').
                - 'organization' (str): URN of the organization (e.g., 'urn:li:organization:1').
                - 'state' (str): Current state of the ACL (one of 'ACTIVE', 'REQUESTED', 'REJECTED', 'REVOKED').

    Raises:
        None: This function handles errors internally and returns them in the response.
    """
    if query_field != "roleAssignee":
        return {"error": "Invalid query parameter. Expected 'roleAssignee'."}
    results = [acl for acl in DB["organizationAcls"].values() if acl.get("roleAssignee") == role_assignee]
    paginated = results[start:start+count]
    return {"data": paginated}

def create_organization_acl(acl_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Creates a new organization ACL record in the database.

    Args:
        acl_data (Dict[str, Any]): Dictionary containing the new ACL record data with keys:
            - 'roleAssignee' (str): URN of the person to assign the role to (e.g., 'urn:li:person:1').
            - 'role' (str): Role to assign to the person (one of 'ADMINISTRATOR', 'DIRECT_SPONSORED_CONTENT_POSTER', 'RECRUITING_POSTER', 'LEAD_CAPTURE_ADMINISTRATOR', 'LEAD_GEN_FORMS_MANAGER', 'ANALYST', 'CURATOR', 'CONTENT_ADMINISTRATOR').
            - 'organization' (str): URN of the organization (e.g., 'urn:li:organization:1').
            - 'state' (str): Initial state of the ACL (one of 'ACTIVE', 'REQUESTED', 'REJECTED', 'REVOKED').

    Returns:
        Dict[str, Any]:
        - On successful creation, returns a dictionary with the following keys and value types:
            - 'data' (Dict[str, Any]): Dictionary of created ACL record with keys:
                - 'aclId' (str): Newly assigned unique identifier.
                - 'roleAssignee' (str): URN of the person assigned the role (e.g., 'urn:li:person:1').
                - 'role' (str): Role assigned to the person (one of 'ADMINISTRATOR', 'DIRECT_SPONSORED_CONTENT_POSTER', 'RECRUITING_POSTER', 'LEAD_CAPTURE_ADMINISTRATOR', 'LEAD_GEN_FORMS_MANAGER', 'ANALYST', 'CURATOR', 'CONTENT_ADMINISTRATOR').
                - 'organization' (str): URN of the organization (e.g., 'urn:li:organization:1').
                - 'state' (str): Current state of the ACL (one of 'ACTIVE', 'REQUESTED', 'REJECTED', 'REVOKED').

    Raises:
        None: This function handles errors internally and returns them in the response.
    """
    acl_id = str(DB["next_acl_id"])
    DB["next_acl_id"] += 1
    acl_data["aclId"] = acl_id
    DB["organizationAcls"][acl_id] = acl_data
    return {"data": acl_data}

def update_organization_acl(acl_id: str,
                            acl_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Updates an existing organization ACL record in the database.

    Args:
        acl_id (str): Unique identifier of the ACL record to update.
        acl_data (Dict[str, Any]): Dictionary containing the updated ACL data with keys:
            - 'roleAssignee' (str): Updated URN of the person assigned the role (e.g., 'urn:li:person:1').
            - 'role' (str): Updated role assigned to the person (one of 'ADMINISTRATOR', 'DIRECT_SPONSORED_CONTENT_POSTER', 'RECRUITING_POSTER', 'LEAD_CAPTURE_ADMINISTRATOR', 'LEAD_GEN_FORMS_MANAGER', 'ANALYST', 'CURATOR', 'CONTENT_ADMINISTRATOR').
            - 'organization' (str): Updated URN of the organization (e.g., 'urn:li:organization:1').
            - 'state' (str): Updated state of the ACL (one of 'ACTIVE', 'REQUESTED', 'REJECTED', 'REVOKED').

    Returns:
        Dict[str, Any]:
        - If ACL record not found, returns a dictionary with the key "error" and the value "ACL record not found."
        - On successful update, returns a dictionary with the following keys and value types:
            - 'data' (Dict[str, Any]): Dictionary of updated ACL record with keys:
                - 'aclId' (str): ACL record's unique identifier.
                - 'roleAssignee' (str): Updated URN of the person assigned the role (e.g., 'urn:li:person:1').
                - 'role' (str): Updated role assigned to the person (one of 'ADMINISTRATOR', 'DIRECT_SPONSORED_CONTENT_POSTER', 'RECRUITING_POSTER', 'LEAD_CAPTURE_ADMINISTRATOR', 'LEAD_GEN_FORMS_MANAGER', 'ANALYST', 'CURATOR', 'CONTENT_ADMINISTRATOR').
                - 'organization' (str): Updated URN of the organization (e.g., 'urn:li:organization:1').
                - 'state' (str): Updated state of the ACL (one of 'ACTIVE', 'REQUESTED', 'REJECTED', 'REVOKED').

    Raises:
        None: This function handles errors internally and returns them in the response.
    """
    if acl_id not in DB["organizationAcls"]:
        return {"error": "ACL record not found."}
    acl_data["aclId"] = acl_id
    DB["organizationAcls"][acl_id] = acl_data
    return {"data": acl_data}

def delete_organization_acl(acl_id: str) -> Dict[str, Any]:
    """
    Deletes an organization ACL record from the database.

    Args:
        acl_id (str): Unique identifier of the ACL record to delete.

    Returns:
        Dict[str, Any]:
        - If ACL record not found, returns a dictionary with the key "error" and the value "ACL record not found."
        - On successful deletion, returns a dictionary with the following keys and value types:
            - 'status' (str): Success message confirming deletion of the ACL record.

    Raises:
        None: This function handles errors internally and returns them in the response.
    """
    if acl_id not in DB["organizationAcls"]:
        return {"error": "ACL record not found."}
    del DB["organizationAcls"][acl_id]
    return {"status": f"ACL {acl_id} deleted."}