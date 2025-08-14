# APIs/jira/ComponentApi.py

from .SimulationEngine.custom_errors import EmptyInputError, ProjectNotFoundError, ComponentNotFoundError, MissingUpdateDataError
from .SimulationEngine.db import DB
from .SimulationEngine.utils import _generate_id
from typing import Optional, Dict, Any


def create_component(
    project: str, name: str, description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new component in a Jira project.

    This method creates a new component within a specified project. Components
    are used to group issues within a project and can be assigned to specific
    team members.

    Args:
        project (str): The key of the project where the component will be created.
            Must be a non-empty string.
        name (str): The name of the component.
            Must be a non-empty string with a maximum length of 255 characters.
        description (Optional[str]): A description of the component's purpose.
            Maximum length is 1000 characters. None if not provided.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - id (str): The unique identifier for the component
            - project (str): The project key
            - name (str): The component name
            - description (str): The component description

    Raises:
        TypeError: If 'project' or 'name' is not a string, or if 'description'
                   is provided and is not a string.
        EmptyInputError: If 'project' or 'name' is an empty string.
        ProjectNotFoundError: If the specified 'project' does not exist in the database.
    """
    # --- Input Validation Start ---
    if not isinstance(project, str):
        raise TypeError("Argument 'project' must be a string.")
    if not isinstance(name, str):
        raise TypeError("Argument 'name' must be a string.")
    if description is not None and not isinstance(description, str):
        raise TypeError("Argument 'description' must be a string or None.")

    if not project:
        raise EmptyInputError("Argument 'project' cannot be empty.")
    if not name:
        raise EmptyInputError("Argument 'name' cannot be empty.")
    
    # Length validation
    if len(name) > 255:
        raise ValueError("name cannot be longer than 255 characters")
    if description is not None and len(description) > 1000:
        raise ValueError("description cannot be longer than 1000 characters")
    # --- Input Validation End ---

    # Core logic:
    # The following lines replace the original error dictionary returns with exceptions
    # and preserve the original functionality otherwise.
    # We assume DB and _generate_id are available in the function's scope.

    # This check is part of the business logic, not just input format validation
    if project not in DB["projects"]: # type: ignore
        raise ProjectNotFoundError(f"Project '{project}' not found.")

    comp_id = _generate_id("CMP", DB["components"]) # type: ignore
    DB["components"][comp_id] = { # type: ignore
        "id": comp_id,
        "project": project,
        "name": name,
        "description": description,
    }
    return DB["components"][comp_id] # type: ignore

def get_component(comp_id: str) -> Dict[str, Any]:
    """
    Retrieve a component by its ID.

    This method returns detailed information about a specific component
    identified by its unique ID.

    Args:
        comp_id (str): The unique identifier of the component to retrieve.

    Returns:
        Dict[str, Any]: A dictionary containing component details:
            - id (str): The component ID
            - project (str): The project key
            - name (str): The component name
            - description (str): The component description

    Raises:
        TypeError: If `comp_id` is not a string.
        ValueError: If the component with the given ID is not found.
    """
    # Input validation for non-dictionary arguments
    if not isinstance(comp_id, str):
        raise TypeError(f"comp_id must be a string, got {type(comp_id).__name__}.")

    # Original core logic (DB is assumed to be globally available)
    # The 'type: ignore' is used because DB's type is not defined in this snippet.
    comp = DB["components"].get(comp_id) # type: ignore
    if not comp:
        raise ValueError(f"Component '{comp_id}' not found.")
    return comp


def update_component(
    comp_id: str, name: Optional[str] = None, description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update an existing component.

    This method allows updating the name and/or description of an existing
    component. At least one of name or description must be provided.

    Args:
        comp_id (str): The unique identifier of the component to update.
        name (Optional[str]): The new name for the component. Defaults to None and maximum length is 255 characters.
        description (Optional[str]): The new description for the component
            Maximum length is 1000 characters.
            Defaults to None.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - updated (bool): True if the component was successfully updated.
            - component (dict): The updated component object.

    Raises:
        TypeError: If comp_id is not a string, or if name/description
                   are provided and are not strings.
        ValueError: If name is provided and is empty or if its length exceeds 255 chars, or if description
                   is provided and is empty or if its length exceeds 1000 chars.
        MissingUpdateDataError: If neither name nor description is provided for the update.
        ComponentNotFoundError: If the specified component does not exist in the DB.
    """
    # --- Input Validation ---
    if not isinstance(comp_id, str):
        raise TypeError("comp_id must be a string.")
    if not comp_id.strip():
        raise ValueError("comp_id cannot be empty.")
        
    if name is not None:
        if not isinstance(name, str):
            raise TypeError("name must be a string if provided.")
        if not name.strip():
            raise ValueError("name cannot be empty if provided.")
        if len(name) > 255:
            raise ValueError("name cannot be longer than 255 characters")
            
    if description is not None:
        if not isinstance(description, str):
            raise TypeError("description must be a string if provided.")
        if not description.strip():
            raise ValueError("description cannot be empty if provided.")
        if len(description) > 1000:
            raise ValueError("description cannot be longer than 1000 characters")

    if name is None and description is None:
        raise MissingUpdateDataError(
            "At least one of name or description must be provided for update."
        )
    # --- End Input Validation ---

    comp = DB["components"].get(comp_id)
    if not comp:
        raise ComponentNotFoundError(f"Component '{comp_id}' not found.")

    if name:
        comp["name"] = name
    if description:
        comp["description"] = description
    DB["components"][comp_id] = comp
    return {"updated": True, "component": comp}


def delete_component(comp_id: str, moveIssuesTo: Optional[str] = None) -> Dict[str, Any]:
    """
    Delete a component from a project.

    This method permanently removes a component from a project. Optionally,
    issues assigned to the component can be moved to another component.

    Args:
        comp_id (str): The unique identifier of the component to delete
        moveIssuesTo (Optional[str]): The ID of the component to move
            existing issues to. If not provided, issues will remain
            unassigned. Defaults to None.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - deleted (str): The ID of the deleted component
            - moveIssuesTo (Optional[str]): The ID of the component
                    issues were moved to

    Raises:
        ValueError: If the component does not exist
    """
    if comp_id not in DB["components"]:
        return {"error": f"Component '{comp_id}' does not exist."}
    DB["components"].pop(comp_id)
    return {"deleted": comp_id, "moveIssuesTo": moveIssuesTo}
