# APIs/jira/ProjectCategoryApi.py
from .SimulationEngine.db import DB
from typing import Dict, Any

def get_project_categories() -> Dict[str, Any]:
    """
    Get all project categories.

    This method returns all project categories in the system.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - categories (List[Dict[str, Any]]): A list of project categories
                - id (str): The id of the project category
                - name (str): The name of the project category
    """
    return {"categories": list(DB["project_categories"].values())}


def get_project_category(cat_id: str) -> Dict[str, Any]:
    """
    Get a project category by id.

    This method returns a project category by id.

    Args:
        cat_id (str): The id of the project category

    Returns:
        Dict[str, Any]: A dictionary containing:
            - category (Dict[str, Any]): The project category
                - id (str): The id of the project category
                - name (str): The name of the project category

    Raises:
        ValueError: If the project category is not found
    """
    c = DB["project_categories"].get(cat_id)
    if not c:
        return {"error": f"Project category '{cat_id}' not found."}
    return c
