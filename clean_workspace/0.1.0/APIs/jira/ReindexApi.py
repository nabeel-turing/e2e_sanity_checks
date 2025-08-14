# APIs/jira/ReindexApi.py
from .SimulationEngine.db import DB


def start_reindex(reindex_type: str = "FOREGROUND") -> dict:
    """
    Start a reindex operation in Jira.

    This method initiates a reindex operation which rebuilds the search indexes in Jira.
    The reindex can be performed in either FOREGROUND or BACKGROUND mode.

    Args:
        reindex_type (str, optional): The type of reindex to perform.
            - "FOREGROUND": Reindex runs in the foreground, blocking other operations
            - "BACKGROUND": Reindex runs in the background, allowing other operations
            Defaults to "FOREGROUND".

    Returns:
        dict: A dictionary containing:
            - started (bool): True if reindex was successfully started
            - reindexType (str): The type of reindex being performed

    """
    DB["reindex_info"]["running"] = True
    DB["reindex_info"]["type"] = reindex_type
    return {"started": True, "reindexType": reindex_type}


def get_reindex_status() -> dict:
    """
    Get the current status of the reindex operation.

    This method returns information about any ongoing reindex operation,
    including whether it is currently running and its type.

    Returns:
        dict: A dictionary containing:
            - running (bool): True if a reindex operation is currently in progress
            - type (str): The type of the current reindex operation ("FOREGROUND" or "BACKGROUND")

    """
    return {
        "running": DB["reindex_info"]["running"],
        "type": DB["reindex_info"]["type"],
    }
