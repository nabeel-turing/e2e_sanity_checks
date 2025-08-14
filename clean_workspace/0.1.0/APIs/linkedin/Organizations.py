from typing import Type, Dict, Any, Optional
from .SimulationEngine.db import DB

"""
API simulation for the '/organizations' resource.
"""

def get_organizations_by_vanity_name(query_field: str,
                                        vanity_name: str,
                                        projection: Optional[str] = None,
                                        start: int = 0,
                                        count: int = 10) -> Dict[str, Any]:
    """
    Retrieves organization(s) by vanity name with optional field projection and pagination.

    Args:
        query_field (str): Query parameter expected to be 'vanityName'.
        vanity_name (str): The organization's vanity name to search for.
        projection (Optional[str]): Field projection syntax for controlling which fields to return.
            The projection string should consist of comma-separated field names and may optionally
            be enclosed in parentheses. Defaults to None.
        start (int): Starting index for pagination. Defaults to 0.
        count (int): Number of items to return. Defaults to 10.

    Returns:
        Dict[str, Any]:
        - If query_field is not 'vanityName', returns a dictionary with the key "error" and the value "Invalid query parameter. Expected 'vanityName'."
        - On successful retrieval, returns a dictionary with the following keys and value types:
            - 'data' (List[Dict[str, Any]]): List of organization data dictionaries with keys:
                - 'id' (int): Organization's unique identifier.
                - 'vanityName' (str): Organization's vanity name (e.g., 'global-tech').
                - 'name' (Dict[str, Any]): Localized organization name with keys:
                    - 'localized' (Dict[str, str]): Dictionary with locale keys mapping to the localized name, keys are locale codes in the format <language>_<COUNTRY>, for example:
                        - 'en_US' (str): English (US) localized name.
                    - 'preferredLocale' (Dict[str, str]): tells you which language/country version LinkedIn considers the "main" or "default" for that particular localized content. Dictionary with keys:
                        - 'country' (str): Country code (e.g., 'US').
                        - 'language' (str): Language code (e.g., 'en').
                - 'primaryOrganizationType' (str): Type of organization ('COMPANY' or 'SCHOOL').
    """
    if query_field != "vanityName":
        return {"error": "Invalid query parameter. Expected 'vanityName'."}
    results = [org for org in DB["organizations"].values() if org.get("vanityName") == vanity_name]
    paginated = results[start:start+count]
    return {"data": paginated}

def create_organization(organization_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Creates a new organization in the database.

    Args:
        organization_data (Dict[str, Any]): Dictionary containing the new organization's data with keys:
            - 'vanityName' (str): Organization's vanity name (e.g., 'global-tech').
            - 'name' (Dict[str, Any]): Localized organization name with keys:
                - 'localized' (Dict[str, str]): Dictionary with locale keys mapping to the localized name, keys are locale codes in the format <language>_<COUNTRY>, for example:
                    - 'en_US' (str): English (US) localized name.
                - 'preferredLocale' (Dict[str, str]): tells you which language/country version LinkedIn considers the "main" or "default" for that particular localized content.Dictionary with keys:
                    - 'country' (str): Country code (e.g., 'US').
                    - 'language' (str): Language code (e.g., 'en').
            - 'primaryOrganizationType' (str): Type of organization ('COMPANY' or 'SCHOOL').

    Returns:
        Dict[str, Any]:
        - On successful creation, returns a dictionary with the following keys and value types:
            - 'data' (Dict[str, Any]): Dictionary of created organization with keys:
                - 'id' (int): Newly assigned unique identifier.
                - 'vanityName' (str): Organization's vanity name (e.g., 'global-tech').
                - 'name' (Dict[str, Any]): Localized organization name with keys:
                    - 'localized' (Dict[str, str]): Dictionary with locale keys mapping to the localized name, keys are locale codes in the format <language>_<COUNTRY>, for example:
                        - 'en_US' (str): English (US) localized name.
                    - 'preferredLocale' (Dict[str, str]): tells you which language/country version LinkedIn considers the "main" or "default" for that particular localized content. Dictionary with keys:
                        - 'country' (str): Country code (e.g., 'US').
                        - 'language' (str): Language code (e.g., 'en').
                - 'primaryOrganizationType' (str): Type of organization ('COMPANY' or 'SCHOOL').
    """
    org_id = DB["next_org_id"]
    DB["next_org_id"] += 1
    organization_data["id"] = org_id
    DB["organizations"][str(org_id)] = organization_data
    return {"data": organization_data}

def update_organization(organization_id: str,
                        organization_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Updates an existing organization's data in the database.

    Args:
        organization_id (str): Unique identifier of the organization to update.
        organization_data (Dict[str, Any]): Dictionary containing the updated organization data with keys:
            - 'vanityName' (str): Updated vanity name (e.g., 'global-tech').
            - 'name' (Dict[str, Any]): Updated localized organization name with keys:
                - 'localized' (Dict[str, str]): Dictionary with locale keys mapping to the localized name:
                    - 'en_US' (str): English (US) localized name.
                - 'preferredLocale' (Dict[str, str]): tells you which language/country version LinkedIn considers the "main" or "default" for that particular localized content. Dictionary with keys:
                    - 'country' (str): Country code (e.g., 'US').
                    - 'language' (str): Language code (e.g., 'en').
            - 'primaryOrganizationType' (str): Updated type of organization ('COMPANY' or 'SCHOOL').

    Returns:
        Dict[str, Any]:
        - If organization not found, returns a dictionary with the key "error" and the value "Organization not found."
        - On successful update, returns a dictionary with the following keys and value types:
            - 'data' (Dict[str, Any]): Dictionary of updated organization with keys:
                - 'id' (int): Organization's unique identifier.
                - 'vanityName' (str): Updated vanity name (e.g., 'global-tech').
                - 'name' (Dict[str, Any]): Updated localized organization name with keys:
                    - 'localized' (Dict[str, str]): Dictionary with locale keys mapping to the localized name, keys are locale codes in the format <language>_<COUNTRY>, for example:
                        - 'en_US' (str): English (US) localized name.
                    - 'preferredLocale' (Dict[str, str]): tells you which language/country version LinkedIn considers the "main" or "default" for that particular localized content. Dictionary with keys:
                        - 'country' (str): Country code (e.g., 'US').
                        - 'language' (str): Language code (e.g., 'en').
                - 'primaryOrganizationType' (str): Updated type of organization ('COMPANY' or 'SCHOOL').
    """
    if organization_id not in DB["organizations"]:
        return {"error": "Organization not found."}
    organization_data["id"] = DB["organizations"][organization_id]["id"]
    DB["organizations"][organization_id] = organization_data
    return {"data": organization_data}

def delete_organization(organization_id: str) -> Dict[str, Any]:
    """
    Deletes an organization from the database by its ID.

    Args:
        organization_id (str): Unique identifier of the organization to delete.

    Returns:
        Dict[str, Any]:
        - If organization not found, returns a dictionary with the key "error" and the value "Organization not found."
        - On successful deletion, returns a dictionary with the following keys and value types:
            - 'status' (str): Success message confirming deletion of the organization.
    """
    if organization_id not in DB["organizations"]:
        return {"error": "Organization not found."}
    del DB["organizations"][organization_id]
    return {"status": f"Organization {organization_id} deleted."}

def delete_organization_by_vanity_name(query_field: str,
                                        vanity_name: str) -> Dict[str, Any]:
    """
    Deletes organization(s) from the database by vanity name.

    Args:
        query_field (str): Query parameter expected to be 'vanityName'.
        vanity_name (str): The organization's vanity name to delete.

    Returns:
        Dict[str, Any]:
        - If query_field is not 'vanityName', returns a dictionary with the key "error" and the value "Invalid query parameter. Expected 'vanityName'."
        - If organization not found, returns a dictionary with the key "error" and the value "Organization with the given vanity name not found."
        - On successful deletion, returns a dictionary with the following keys and value types:
            - 'status' (str): Success message confirming deletion of organizations with the specified vanity name.
    """
    if query_field != "vanityName":
        return {"error": "Invalid query parameter. Expected 'vanityName'."}
    to_delete = [org_id for org_id, org in DB["organizations"].items() if org.get("vanityName") == vanity_name]
    if not to_delete:
        return {"error": "Organization with the given vanity name not found."}
    for org_id in to_delete:
        del DB["organizations"][org_id]
    return {"status": f"Organizations with vanity name '{vanity_name}' deleted."}

