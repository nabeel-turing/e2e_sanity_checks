from common_utils.print_log import print_log
# APIs/google_chat/Users/Spaces/__init__.py

import sys
from typing import Dict, Any

sys.path.append("APIs")

from google_chat.SimulationEngine.db import DB


def getSpaceReadState(name: str) -> Dict[str, Any]:
    """
    Retrieves the read state of a user within a space.

    Args:
        name (str): Required. Resource name of the space read state to retrieve.
            Only supports getting read state for the calling user.
            To refer to the calling user, set one of the following:
            - The `me` alias. For example, `users/me/spaces/{space}/spaceReadState`.
            - Their Workspace email address. For example, `users/user@example.com/spaces/{space}/spaceReadState`.
            - Their user ID. For example, `users/123456789/spaces/{space}/spaceReadState`.
            Format: users/{user}/spaces/{space}/spaceReadState

    Returns:
        Dict[str, Any]: Dictionary representing the user's space read state with the following keys:
            - 'name' (str): Resource name of the space read state.
            - 'lastReadTime' (str, optional): The time when the user's space read state was updated.
        Returns an empty dictionary if no matching read state is found.
    """
    print_log(f"getSpaceReadState called with name={name}")
    for state in DB["SpaceReadState"]:
        if state.get("name") == name:
            return state
    print_log("SpaceReadState not found.")
    return {}


def updateSpaceReadState(name: str, updateMask: str, requestBody: Dict[str, Any]) -> Dict[str, Any]:
    """
    Updates a user's space read state.

    Args:
        name (str): Resource name of the space read state to update.
            Format: users/{user}/spaces/{space}/spaceReadState
        updateMask (str): Required. Comma-separated list of fields to update.
            Currently only "last_read_time" is supported.
        requestBody (Dict[str, Any]): A dictionary representing the SpaceReadState resource with the following key:
            - 'name' (str): Resource name of the space read state.
                Format: users/{user}/spaces/{space}/spaceReadState
            - 'last_read_time' (str): Optional. The time when the user's space read state was updated.
                This corresponds with either the timestamp of the last read message, or a user-specified timestamp.

    Returns:
        Dict[str, Any]: A dictionary representing the updated SpaceReadState resource with the following keys:
            - 'name' (str): Resource name of the space read state.
                Format: users/{user}/spaces/{space}/spaceReadState
            - 'last_read_time' (str): Optional. The updated timestamp of the space read state.

        Returns an empty dictionary if no matching resource is found.
    """
    print_log(
        f"updateSpaceReadState called with name={name}, updateMask={updateMask}, requestBody={requestBody}"
    )
    # Find the state resource
    state_obj = None
    for state in DB["SpaceReadState"]:
        if state.get("name") == name:
            state_obj = state
            break
    if not state_obj:
        print_log("SpaceReadState not found.")
        return {}

    # Parse updateMask; only "last_read_time" is supported.
    masks = [m.strip() for m in updateMask.split(",")]
    if "last_read_time" in masks or "*" in masks:
        if "last_read_time" in requestBody:
            # The new value is coerced to be later than the latest message's create time (not enforced here).
            state_obj["last_read_time"] = requestBody["last_read_time"]
        else:
            print_log("last_read_time not provided in requestBody.")
    else:
        print_log("No supported field in updateMask.")
    return state_obj
