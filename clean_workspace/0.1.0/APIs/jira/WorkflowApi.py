# APIs/jira/WorkflowApi.py
from .SimulationEngine.db import DB
from typing import Dict, Any


def get_workflows() -> Dict[str, Any]:
    """
    Get all workflows.

    Returns:
        Dict[str, Any]: A dictionary containing the workflows' information.
            - workflows (List[Dict]): The workflows' information.
                - id (str): The ID of the workflow.
                - name (str): The name of the workflow.
                - steps (List[str]): The steps of the workflow.
    """
    return {"workflows": list(DB["workflows"].values())}
