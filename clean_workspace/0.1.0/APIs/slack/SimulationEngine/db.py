import json
from typing import Dict, Any

# ---------------------------------------------------------------------------------------
# In-Memory Database Structure
# ---------------------------------------------------------------------------------------
# Initialize the DB as a global variable (simulating a JSON file)
DB: Dict[str, Any] = {
  "current_user": {
      "id": "user_123",
      "is_admin": False
  },
  "users": {},
  "channels": {
    "1234": {
      "messages": [
        {
            "ts": "",
            "user": "",
            "text": "",
            "reactions": [],
        }
      ],
      "conversations":{},
      'id':'1234',
      'name': '',
      "files": {}
    }
  },
  "files": {},
  "reminders": {},
  "usergroups": {},
  "scheduled_messages": [],
  "ephemeral_messages": []
}


# -------------------------------------------------------------------
# Persistence Helpers
# -------------------------------------------------------------------
def save_state(filepath: str):
    """Saves the current API state to a JSON file."""
    with open(filepath, 'w') as f:
        json.dump(DB, f)

def load_state(filepath: str) -> None:
    """Loads the API state from a JSON file."""
    global DB
    try:
        with open(filepath, 'r') as f:
            DB.update(json.load(f))
    except FileNotFoundError:
        pass
