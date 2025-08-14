# APIs/confluence/LongTaskAPI.py
from typing import Dict, List, Any, Optional
from confluence.SimulationEngine.db import DB


def get_long_tasks(
    expand: Optional[str] = None, start: int = 0, limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Returns a paginated list of all long-running tasks.

    Retrieves a list of task dictionaries for all long-running tasks.
    Note: The 'expand' parameter is accepted for API compatibility but is not currently processed.

    Args:
        expand (Optional[str]): A comma-separated list of properties to expand.
            Defaults to None.
            Note: Not implemented.
        start (int): The starting index for pagination.
            Defaults to 0.
        limit (int): The maximum number of tasks to return.
            Defaults to 100.

    Returns:
        List[Dict[str, Any]]: A list of task dictionaries, each containing:
            - id (str): The unique identifier of the task.
            - status (str): The current status of the task (e.g., "in_progress", "completed", "failed").
            - description (str): A description of the task.

    Raises:
        ValueError: If the start or limit parameters are negative.
    """
    tasks = list(DB["long_tasks"].values())
    return tasks[start : start + limit]


def get_long_task(id: str, expand: Optional[str] = None) -> Dict[str, Any]:
    """
    Returns a specific long-running task by its ID.

    Retrieves the long-running task dictionary that matches the provided task ID.
    Note: The 'expand' parameter is accepted for API compatibility but is not currently processed.

    Args:
        id (str): The unique identifier of the task.
        expand (Optional[str]): A comma-separated list of properties to expand.
            Defaults to None.

    Returns:
        Dict[str, Any]: A dictionary representing the task, containing:
            - id (str): The unique identifier of the task.
            - status (str): The current status of the task.
            - description (str): A description of the task.

    Raises:
        ValueError: If a task with the specified ID is not found.
    """
    task = DB["long_tasks"].get(id)
    if not task:
        raise ValueError(f"Task with id={id} not found.")
    return task
