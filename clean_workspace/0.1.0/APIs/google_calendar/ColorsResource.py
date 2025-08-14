# APIs/google_calendar/ColorsResource/__init__.py
from .SimulationEngine.db import DB
from typing import Dict, Any


def get_colors() -> Dict[str, Any]:
    """
    Returns the color definitions for calendars and events.

    Returns:
        Dict[str, Any]: A dictionary containing the color definitions for calendars and events.
            - calendar (Dict[str, Any]): A dictionary containing the color definitions for calendars.
                - id (str): The identifier of the calendar.
                - background (str): The background color of the calendar.
                - foreground (str): The foreground color of the calendar.
            - event (Dict[str, Any]): A dictionary containing the color definitions for events.
                - id (str): The identifier of the event.
                - background (str): The background color of the event.
                - foreground (str): The foreground color of the event.
    """
    return DB["colors"]
