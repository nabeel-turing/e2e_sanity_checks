# APIs/jira/ProjectApi.py
from .SimulationEngine.custom_errors import ProjectInputError, ProjectAlreadyExistsError, UserNotFoundError
from .SimulationEngine.db import DB
from typing import Dict, Any, List, Optional


def create_project(proj_key: str, proj_name: str, proj_lead: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a new project.

    This method creates a new project with the given key and name.

    Args:
        proj_key (str): The key of the project. Cannot be empty.
        proj_name (str): The name of the project. Cannot be empty.
        proj_lead (Optional[str]): The name of the project lead. Must be a valid user name if provided.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - created (bool): Whether the project was created successfully
            - project (dict): The project
                - key (str): The key of the project
                - name (str): The name of the project
                - lead (str): The name of the project lead.

    Raises:
        TypeError: If proj_key or proj_name or proj_lead(if provided) is not a string.
        ProjectInputError: If proj_key or proj_name or proj_lead(if provided) is an empty string.
        ProjectAlreadyExistsError: If a project with the given proj_key already exists.
        UserNotFoundError: If the project lead is provided and does not exist in the database.
    """
    # Input validation for proj_key
    if not isinstance(proj_key, str):
        raise TypeError("Project key (proj_key) must be a string.")
    if not proj_key: # Check for empty string
        raise ProjectInputError("Project key (proj_key) cannot be empty.")

    # Input validation for proj_name
    if not isinstance(proj_name, str):
        raise TypeError("Project name (proj_name) must be a string.")
    if not proj_name: # Check for empty string
        raise ProjectInputError("Project name (proj_name) cannot be empty.")

    if proj_key in DB["projects"]:
        raise ProjectAlreadyExistsError(f"Project '{proj_key}' already exists.")

    if proj_lead is not None:
        if not isinstance(proj_lead, str):
            raise TypeError("Project lead (proj_lead) must be a string.")
        if not proj_lead.strip():
            raise ProjectInputError("Project lead (proj_lead) cannot be empty.")
        users = DB.get("users", {})
        found = False
        for user in users.values():
            if user["name"] == proj_lead:
                found = True
                break
        if not found:
            raise UserNotFoundError(f"Project lead '{proj_lead}' does not exist.")

    DB["projects"][proj_key] = {"key": proj_key, "name": proj_name, "lead": proj_lead}
    return {"created": True, "project": DB["projects"][proj_key]}

def get_projects() -> Dict[str, List[Dict[str, str]]]:
    """
    Get all projects.

    This method returns all projects in the system.

    Returns:
        Dict[str, List[Dict[str, str]]]: A dictionary containing:
            - projects (List[Dict[str, str]]): A list of projects
                - key (str): The key of the project
                - name (str): The name of the project
    """
    return {"projects": list(DB["projects"].values())}

def get_project(project_key: str) -> Dict[str, Any]:
    """
    Get a project by key.

    This method retrieves a specific project using its key.

    Args:
        project_key (str): The key of the project. Cannot be empty.

    Returns:
        Dict[str, Any]: A dictionary representing the project, containing:
            - key (str): The key of the project.
            - name (str): The name of the project.

    Raises:
        TypeError: If project_key is not a string.
        ProjectInputError: If project_key is an empty string.
        ValueError: If the project_key is not found.
    """
    # Input validation for project_key
    if not isinstance(project_key, str):
        raise TypeError("project_key must be a string")
    if not project_key.strip():  # Check for empty string and whitespace-only strings
        raise ProjectInputError("project_key cannot be empty.")

    proj = DB["projects"].get(project_key)
    if not proj:
        raise ValueError(f"Project with key '{project_key}' not found.")
    return proj


def get_project_avatars(project_key: str) -> Dict[str, Any]:
    """
    Get all avatars for a project.

    Note: This returns all avatars with type 'project' 

    Args:
        project_key (str): The key of the project. Must be a non-empty string.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - project (str): The project key that was requested
            - avatars (List[Dict[str, Any]]): A list of avatar objects with type 'project'.
                Each avatar dictionary contains:
                - id (str): The unique identifier of the avatar
                - type (str): The type of avatar (always 'project' for this function)
                - filename (str): The filename of the avatar image

    Raises:
        TypeError: If project_key is not a string.
        ValueError: If project_key is an empty string.
    """
    # Input type validation
    if not isinstance(project_key, str):
        raise TypeError(f"project_key must be a string, got {type(project_key).__name__}.")
    
    # Input value validation
    if not project_key:
        raise ValueError("project_key cannot be empty.")

    # Implementation: return all avatars with type 'project'
    matched = [a for a in DB["avatars"] if a.get("type") == "project"]
    return {"project": project_key, "avatars": matched}


def get_project_components(project_key: str) -> Dict[str, Any]:
    """
    Get all components for a project.

    This method returns all components for a project.

    Args:
        project_key (str): The key of the project.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - components (List[Dict[str, Any]]): A list of components.
                Each component dictionary has:
                - id (str): The id of the component.
                - project (str): The project key of the component.
                - name (str): The name of the component.
                - description (str): The description of the component.

    Raises:
        TypeError: If project_key is not a string.
    """
    # Input validation
    if not isinstance(project_key, str):
        raise TypeError(f"project_key must be a string, but got {type(project_key).__name__}.")

    # Original core functionality (assumes DB is defined and structured correctly)
    # Return components that mention the project
    # Note: This part may raise KeyError if DB or DB["components"] is missing,
    # or AttributeError if DB["components"] doesn't have .values(),
    # or KeyError if a component dict c doesn't have "project".
    # These are runtime errors based on DB state, not input validation errors handled above.
    
    comps = [c for c in DB["components"].values() if c["project"] == project_key]
    return {"components": comps}


def delete_project(project_key: str) -> Dict[str, str]:
    """
    Delete a project.

    This method deletes a project.

    Args:
        project_key (str): The key of the project

    Returns:
        Dict[str, str]: A dictionary containing:
            - deleted (str): The key of the deleted project

    Raises:
        ValueError: If the project_key is not found
    """
    if project_key not in DB["projects"]:
        return {"error": f"Project '{project_key}' does not exist."}

    # Remove the project from DB
    DB["projects"].pop(project_key)

    # Delete components associated with the project
    components_to_delete = [
        cmp_id
        for cmp_id, component in DB["components"].items()
        if component["project"] == project_key
    ]

    for cmp_id in components_to_delete:
        DB["components"].pop(cmp_id)

    return {"deleted": project_key}
