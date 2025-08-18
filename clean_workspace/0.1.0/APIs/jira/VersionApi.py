# APIs/jira/VersionApi.py
from .SimulationEngine.db import DB
from .SimulationEngine.utils import _generate_id
from typing import Dict, Any

def get_version(ver_id: str) -> Dict[str, Any]:
    """
    Get a version by ID.

    Args:
        ver_id (str): The ID of the version to get.

    Returns:
        Dict[str, Any]: A dictionary containing the version's information.
            - id (str): The ID of the version.
            - name (str): The name of the version.
            - description (str): The description of the version.
            - archived (bool): Whether the version is archived.
            - released (bool): Whether the version is released.
            - releaseDate (str): The release date of the version.
            - userReleaseDate (str): The user release date of the version.
            - project (str): The project of the version.
            - projectId (int): The project ID of the version.

    Raises:
        ValueError: If the ver_id is empty or not found in the database
        TypeError: If the ver_id is not a string
    """
    # input validation
    if not isinstance(ver_id, str):
        raise TypeError("ver_id must be a string")
    
    if ver_id.strip() == "":
        raise ValueError("ver_id cannot be empty")
    
    # get version from the database by ver_id
    if "versions" not in DB:
        DB["versions"] = {}
        
    v = DB["versions"].get(ver_id)
    if not v:
        raise ValueError(f"Version '{ver_id}' not found.")
    return v


def create_version(
    name: str = "",
    description: str = "",
    archived: bool = False,
    released: bool = False,
    release_date: str = "",
    user_release_date: str = "",
    project: str = "",
    project_id: int = 0,
) -> Dict[str, Any]:
    """
    Create a new version.

    Args:
        name (str): The name of the version.
        description (str): The description of the version.
        archived (bool): Whether the version is archived.
        released (bool): Whether the version is released.
        release_date (str): The release date of the version.
        user_release_date (str): The user release date of the version.
        project (str): The project of the version.
        project_id (int): The project ID of the version.

    Returns:
        Dict[str, Any]: A dictionary containing the version's information.
            - created (bool): Whether the version was created.
            - version (dict): The version's information.
                - id (str): The ID of the version.
                - name (str): The name of the version.
                - description (str): The description of the version.
                - archived (bool): Whether the version is archived.
                - released (bool): Whether the version is released.
                - releaseDate (str): The release date of the version.
                - userReleaseDate (str): The user release date of the version.
                - project (str): The project of the version.
                - projectId (int): The project ID of the version.
    Raises:
        ValueError: If the required field 'name' is missing.
    """
    if not name:
        return {"error": "Missing required field 'name'"}

    # Generate a new version ID
    ver_id = _generate_id("VER", DB["versions"])

    # Create the version object with all provided fields
    version = {
        "id": ver_id,
        "name": name,
        "description": description,
        "archived": archived,
        "released": released,
        "releaseDate": release_date,
        "userReleaseDate": user_release_date,
        "project": project,
        "projectId": project_id,
    }

    # Store in DB
    if "versions" not in DB:
        DB["versions"] = {}
    DB["versions"][ver_id] = version

    return {"created": True, "version": version}


def delete_version(
    ver_id: str, move_fix_issues_to: str = None, move_affected_issues_to: str = None
) -> Dict[str, Any]:
    """
    Delete a version.

    Args:
        ver_id (str): The ID of the version to delete.
        move_fix_issues_to (str): The ID of the version to move the fixed issues to, currently not used.
        move_affected_issues_to (str): The ID of the version to move the affected issues to, currently not used.

    Returns:
        Dict[str, Any]: A dictionary containing the version's information.
            - deleted (str): The ID of the version that was deleted.
            - moveFixIssuesTo (str): The ID of the version to move the fixed issues to.
            - moveAffectedIssuesTo (str): The ID of the version to move the affected issues to.
    Raises:
        ValueError: If the version does not exist.
    """
    if "versions" not in DB:
        DB["versions"] = {}
    if ver_id not in DB["versions"]:
        return {"error": f"Version '{ver_id}' does not exist."}
    DB["versions"].pop(ver_id)
    return {
        "deleted": ver_id,
        "moveFixIssuesTo": move_fix_issues_to,
        "moveAffectedIssuesTo": move_affected_issues_to,
    }


def get_version_related_issue_counts(ver_id: str) -> Dict[str, Any]:
    """
    Get the related issue counts for a version.

    Args:
        ver_id (str): The ID of the version to get the related issue counts for.

    Returns:
        Dict[str, Any]: A dictionary containing the related issue counts, currently returns 0 for both.
            - fixCount (int): The number of issues that reference this version as a fix version.
            - affectedCount (int): The number of issues that reference this version as an affected version.
    """
    # In real usage, we'd count how many issues reference this version
    return {"fixCount": 0, "affectedCount": 0}
