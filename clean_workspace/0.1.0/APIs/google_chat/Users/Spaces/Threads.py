from common_utils.print_log import print_log
# APIs/google_chat/Users/Spaces/Threads.py

import sys
import os
from typing import Dict, Any

sys.path.append("APIs")

from google_chat.SimulationEngine.db import DB


def getThreadReadState(name: str) -> Dict[str, Any]:
    """
    Retrieves the read state of a user within a thread.

    Args:
        name (str): Required. Resource name of the thread read state to retrieve.
            Only supports getting read state for the calling user.
            To refer to the calling user, set one of the following:
            - The `me` alias. For example: users/me/spaces/{space}/threads/{thread}/threadReadState
            - Their Workspace email address. For example: users/user@example.com/spaces/{space}/threads/{thread}/threadReadState
            - Their user ID. For example: users/123456789/spaces/{space}/threads/{thread}/threadReadState
            Format: users/{user}/spaces/{space}/threads/{thread}/threadReadState

    Returns:
        Dict[str, Any]: A dictionary representing the user's thread read state with the following keys:
            - 'name' (str): Resource name of the thread read state.
            - 'lastReadTime' (str): The time when the user's thread read state was last updated.

        Returns an empty dictionary if no matching read state is found.
    """

    print_log(f"getThreadReadState called with name={name}")
    for state in DB["ThreadReadState"]:
        if state.get("name") == name:
            return state
    print_log("ThreadReadState not found.")
    return {}
