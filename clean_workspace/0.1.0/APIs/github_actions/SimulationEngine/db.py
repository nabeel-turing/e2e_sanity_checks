# File: Project/APIs/github_actions/SimulationsEngine/db.py

import json
import os
from typing import Optional



# Define the default path to your JSON DB file
DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ),
    "DBs",
    "GithubActionsDB.json",
)

DB = None
with open(DEFAULT_DB_PATH, "r", encoding="utf-8") as f:
    DB = json.load(f)

def save_state(filepath: str) -> None:
    """Save the current state to a JSON file.

    Args:
        filepath: Path to save the state file.
    """
    with open(filepath, "w") as f:
        json.dump(DB, f)

def load_state(filepath: str) -> None:
    """Load state from a JSON file.

    Args:
        filepath: Path to load the state file from.
    """
    global DB
    with open(filepath, "r") as f:
        new_data = json.load(f)
        DB.clear()
        DB.update(new_data)