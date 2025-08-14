import os
import json
from typing import Dict, Any

# Initialize empty database structure
DB: Dict[str, Any] = {
    "reminders": {},
    "operations": {},
    "counters": {"reminder": 0, "operation": 0},
}


def save_state(filepath: str):
    """Save current database state to JSON file"""
    with open(filepath, "w") as f:
        json.dump(DB, f, indent=2)


def load_state(filepath: str) -> None:
    """Load database state from JSON file"""
    global DB
    try:
        with open(filepath, "r") as f:
            loaded_data = json.load(f)
            DB.update(loaded_data)
    except FileNotFoundError:
        pass


def reset_db():
    """Reset database to initial state"""
    global DB
    for key in list(DB.keys()):
        if isinstance(DB[key], dict):
            DB[key].clear()
        elif isinstance(DB[key], list):
            DB[key].clear()

    # Reset counters to initial state
    DB["counters"] = {"reminder": 0, "operation": 0}


# Load default data if available
def load_default_data():
    """Load default database from DBs directory"""
    db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        "DBs",
        "GenericRemindersDefaultDB.json",
    )
    if os.path.exists(db_path):
        load_state(db_path)


# Initialize with default data
load_default_data()
