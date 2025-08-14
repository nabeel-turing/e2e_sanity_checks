"""In-memory database for the gemini_cli API simulation.

The structure mirrors the pattern used by Cursor and Copilot simulations but
is pared down until concrete tools are implemented.
"""
from __future__ import annotations

import json
import os
import datetime
from typing import Dict, Any


# ---------------------------------------------------------------------------
# Locate default DB snapshot shipped in /DBs/GeminiCliDefaultDB.json
# ---------------------------------------------------------------------------

_DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    "DBs",
    "GeminiCliDefaultDB.json",
)

# Fallback stub if the JSON file is missing
_FALLBACK_DB: Dict[str, Any] = {
    "workspace_root": "/home/user/project",
    "cwd": "/home/user/project",
    "file_system": {},
    "memory_storage": {},
    "last_edit_params": None,
    "background_processes": {},
    "tool_metrics": {},
    "_created": datetime.datetime.now(datetime.UTC).isoformat() + "Z",
}


def _load_default_state() -> Dict[str, Any]:
    try:
        with open(_DEFAULT_DB_PATH, "r", encoding="utf-8") as fh:
            state = json.load(fh)
    except FileNotFoundError:
        state = _FALLBACK_DB.copy()
    
    # Ensure memory_storage is always present
    if "memory_storage" not in state:
        state["memory_storage"] = {}
    
    return state


DB: Dict[str, Any] = _load_default_state()


def save_state(filepath: str) -> None:
    """Persist current DB to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as fh:
        json.dump(DB, fh, indent=2)


def load_state(filepath: str) -> None:
    """Load state from a JSON file, replacing the in-memory DB."""
    global DB
    with open(filepath, "r", encoding="utf-8") as fh:
        new_state = json.load(fh)
    
    # Ensure memory_storage is always present
    if "memory_storage" not in new_state:
        new_state["memory_storage"] = {}
    
    DB.clear()
    DB.update(new_state) 