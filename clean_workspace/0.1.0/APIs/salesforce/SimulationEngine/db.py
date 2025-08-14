# APIs/salesforce/SimulationEngine/db.py

"""
Database structure and persistence helpers for Salesforce API Simulation.
"""
import json
import datetime
from datetime import datetime
from typing import Dict, Any
import os


# ---------------------------------------------------------------------------------------
# In-Memory Database Structure
# ---------------------------------------------------------------------------------------
DB: dict = {"Event": {}, "Task": {}}

# -------------------------------------------------------------------
# Persistence Helpers
# -------------------------------------------------------------------


def save_state(filepath: str) -> None:
    """Saves the current state of the API to a JSON file."""
    with open(filepath, "w") as f:
        json.dump(DB, f)


def load_state(filepath: str) -> None:
    """Loads the API state from a JSON file."""
    global DB
    with open(filepath, "r") as f:
        state = json.load(f)
    # Instead of reassigning DB, update it in place:
    DB.clear()
    DB.update(state)

