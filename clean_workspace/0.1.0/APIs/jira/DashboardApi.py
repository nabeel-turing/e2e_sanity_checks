# APIs/jira/DashboardApi.py

from .SimulationEngine.db import DB
from typing import Optional, Dict, Any


def get_dashboards(
    startAt: Optional[int] = 0, maxResults: Optional[int] = None
) -> Dict[str, Any]:
    """
    Retrieve a list of dashboards from Jira.

    This method returns a list of all dashboards in the system, with optional
    pagination support. Dashboards are used to display various Jira data and
    metrics in a customizable layout.

    Args:
        startAt (Optional[int]): The index of the first dashboard to return.
            Defaults to 0.
        maxResults (Optional[int]): The maximum number of dashboards to return.
            If not specified, all dashboards will be returned.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - dashboards (List[Dict[str, Any]]): A list of dashboard objects,
                each containing:
                - id (str): The unique identifier for the dashboard
                - name (str): The name of the dashboard
                - self (str): The URL of the dashboard
                - view (str): The URL of the dashboard

    """
    all_dashboards = list(DB["dashboards"].values())
    return {"dashboards": all_dashboards}


def get_dashboard(dash_id: str) -> Dict[str, Any]:
    """
    Retrieve a specific dashboard by its ID.

    This method returns detailed information about a specific dashboard
    identified by its unique ID.

    Args:
        dash_id (str): The unique identifier of the dashboard to retrieve

    Returns:
        Dict[str, Any]: A dictionary containing:
            - id (str): The unique identifier for the dashboard
            - name (str): The name of the dashboard
            - self (str): The URL of the dashboard
            - view (str): The URL of the dashboard

    Raises:
        ValueError: If the dashboard does not exist
    """
    dash = DB["dashboards"].get(dash_id)
    if not dash:
        return {"error": f"Dashboard '{dash_id}' not found."}
    return dash
