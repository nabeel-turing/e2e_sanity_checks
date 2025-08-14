# phone/SimulationEngine/db.py
import json
import os

# Bring in the live contacts dict from the centralized Contacts API
from contacts import DB as CONTACTS_DB

DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ),
    "DBs",
    "PhoneDefaultDB.json",
)

# Load the Phone DB
DB = {}

with open(DEFAULT_DB_PATH, "r", encoding="utf-8") as f:
    DB = json.load(f)

# ——— Live-link contacts ———
# Point Phone’s contacts directly at the contacts API’s `myContacts` dict
DB["contacts"] = CONTACTS_DB["myContacts"]


def save_state(filepath: str) -> None:
    with open(filepath, "w") as f:
        json.dump(DB, f, indent=2)


def load_state(filepath: str) -> None:
    global DB
    with open(filepath, "r") as f:
        state = json.load(f)
    # Instead of reassigning DB, update it in place:
    DB.clear()
    DB.update(state)

    # Re-bind to the live contacts dict after reset
    DB["contacts"] = CONTACTS_DB["myContacts"]



