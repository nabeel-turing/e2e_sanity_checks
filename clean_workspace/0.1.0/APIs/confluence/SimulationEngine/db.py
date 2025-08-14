# APIs/confluence/SimulationEngine/db.py
import json
import os
import os

DB = {
    "contents": {},
    "content_counter": 1,
    "content_properties": {},
    "content_labels": {},
    "long_tasks": {},
    "long_task_counter": 1,
    "spaces": {},
    "deleted_spaces_tasks": {},
    "attachments": {},
}


def save_state(filepath: str) -> None:
    """
    Save current in-memory DB state to a JSON file.
    """
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(DB, f, ensure_ascii=False, indent=2)

def load_state(filepath: str) -> None:
    """
    Load DB state from a JSON file into the global DB dictionary.
    """
    global DB
    with open(filepath, "r", encoding="utf-8") as f:
        DB.update(json.load(f))
