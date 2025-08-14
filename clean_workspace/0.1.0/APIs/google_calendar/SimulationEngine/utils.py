# APIs/google_calendar/SimulationEngine/utils.py
from datetime import datetime
from ..SimulationEngine.db import DB

def parse_iso_datetime(iso_string):
    return datetime.strptime(iso_string, "%Y-%m-%dT%H:%M:%SZ") if iso_string else None


def get_primary_calendar_list_entry():
    # The DB["calendar_list"] is a dict of {id: {id, summary, description, timeZone, primary}}
    # Find the entry where "primary" is True
    primary_calendar_list_entry = next(
        (entry for entry in DB["calendar_list"].values() if entry.get("primary") is True),
        None
    )
    if primary_calendar_list_entry is None:
        raise ValueError("Primary calendar list entry not found.")
    return primary_calendar_list_entry

def get_primary_calendar_entry():
    primary_calendar_entry = next(
        (entry for entry in DB["calendars"].values() if entry.get("primary") is True),
        None
    )
    if primary_calendar_entry is None:
        raise ValueError("Primary calendar not found.")
    return primary_calendar_entry