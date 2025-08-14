from common_utils.print_log import print_log
# APIs/google_chat/SimulationEngine/utils.py

from .db import DB, CURRENT_USER_ID
from datetime import datetime


def _create_user(display_name: str, type: str = None):
    """
    Creates a user.
    """
    print_log(f"create_user called with display_name={display_name}, type={type}")
    user = {
        "name": f"users/user{len(DB['User']) + 1}",
        "displayName": display_name,
        "type": type if type else "HUMAN",
        "createTime": datetime.utcnow().isoformat() + "Z",
    }
    DB["User"].append(user)
    return user


def _change_user(user_id: str) -> None:
    """
    Changes the caller to the specified user.
    """
    global CURRENT_USER_ID
    CURRENT_USER_ID.update({"id": user_id})
    print_log(f"User changed to {CURRENT_USER_ID}")
