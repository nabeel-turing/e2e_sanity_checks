# APIs/google_calendar/SimulationEngine/db.py
import json
import os

DB = {
    "acl_rules": {},  # Stores ACL rule objects, keyed by ruleId
    "calendar_list": {},  # Stores CalendarList entries, keyed by calendarId
    "calendars": {},  # Stores Calendar objects, keyed by calendarId
    "channels": {},  # Stores Channel objects, keyed by channelId (or random)
    "colors": {  # Colors are usually static in the real API, but we'll store them anyway
        "calendar": {},  # This might store color definitions for calendars
        "event": {},  # This might store color definitions for events
    },
    "events": {},  # Stores events, keyed by (calendarId, eventId) or a combined key
}


def save_state(filepath: str) -> None:
    """
    Save the current in-memory DB state to a JSON file.
    """
    # Create a copy of DB with string keys for events
    db_copy = DB.copy()
    db_copy["events"] = {f"{k[0]}:{k[1]}": v for k, v in DB.get("events", {}).items()}

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(db_copy, f, indent=2)


def load_state(filepath: str) -> None:
    """
    Load DB state from a JSON file, replacing the current in-memory DB.
    """
    global DB
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Convert string keys back to tuples for events
    data["events"] = {
        tuple(key.split(":",maxsplit=1)): value for key, value in data.get("events", {}).items()
    }

    DB.update(data)