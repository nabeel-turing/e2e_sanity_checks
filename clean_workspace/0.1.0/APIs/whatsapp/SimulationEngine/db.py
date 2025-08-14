# File: APIs/whatsapp/SimulationEngine/db.py

import json
import os
from typing import Dict, Any, Optional
import threading


# Bring in the live contacts dict from the centralized Contacts API
from contacts import DB as CONTACTS_DB

# Define the default path to your JSON DB file
DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ),
    "DBs",
    "WhatsAppDefaultDB.json",
)

# Load the WhatsApp DB
DB = None
with open(DEFAULT_DB_PATH, "r", encoding="utf-8") as f:
    DB = json.load(f)

# ——— Live-link contacts ———
# Point WhatsApp’s contacts directly at the contacts API’s `myContacts` dict
DB["contacts"] = CONTACTS_DB["myContacts"]

def save_state(filepath: str) -> None:
    """Save the current state to a JSON file.

    Args:
        filepath: Path to save the state file.
    """
    with open(filepath, "w") as f:
        json.dump(DB, f)

def load_state(
    filepath: str,
) -> object:
    """Load state from a JSON file.

    Args:
        filepath: Path to load the state file from.
    """
    global DB
    # Load new data and replace contents
    with open(filepath, "r") as f:
        new_data = json.load(f)
        DB.clear()
        DB.update(new_data)

    # Re-bind to the live contacts dict after reset
    DB["contacts"] = CONTACTS_DB["myContacts"]