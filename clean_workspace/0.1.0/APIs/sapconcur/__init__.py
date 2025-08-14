"""
SAPConcur API Simulation

This package provides a simulation of the SAPConcur API functionality.
It allows for basic query execution and data manipulation in a simulated environment.
"""

import importlib
import json
import os

from .SimulationEngine.db import DB, load_state, save_state
from common_utils.error_handling import get_package_error_mode

# Define __all__ for 'from sapconcur import *'
# Explicitly lists the public API components intended for import *
import importlib
import os
import json
import tempfile
from common_utils.error_handling import get_package_error_mode
from .SimulationEngine.db import DB, load_state, save_state
from common_utils.init_utils import create_error_simulator, resolve_function_import
from sapconcur.SimulationEngine import utils

# Get the directory of the current file
_INIT_PY_DIR = os.path.dirname(__file__)

# Create error simulator using the utility function
error_simulator = create_error_simulator(_INIT_PY_DIR)

# Get the error mode for the package
ERROR_MODE = get_package_error_mode()

# Function map
_function_map = {
    "cancel_booking": "sapconcur.bookings.cancel_booking",
    "get_location_by_id": "sapconcur.locations.get_location_by_id",
    "get_trips_summary": "sapconcur.trips.get_trip_summaries",
    "create_or_update_booking": "sapconcur.bookings.create_or_update_booking",
    "list_locations": "sapconcur.locations.list_locations",
    "update_reservation_baggages": "sapconcur.bookings.update_reservation_baggages",
    "update_reservation_flights": "sapconcur.bookings.update_reservation_flights",
    "update_reservation_passengers": "sapconcur.bookings.update_reservation_passengers",
    "search_direct_flight": "sapconcur.flights.search_direct_flight",
    "search_onestop_flight": "sapconcur.flights.search_onestop_flight",
    "send_certificate": "sapconcur.users.send_certificate",
    "get_reservation_details": "sapconcur.bookings.get_reservation_details",
    "get_user_details": "sapconcur.users.get_user_details",
    "list_all_airports": "sapconcur.locations.list_all_airports",
    "create_or_update_trip": "sapconcur.trips.create_or_update_trip",
    "transfer_to_human_agents": "sapconcur.users.transfer_to_human_agents"
}

def __getattr__(name: str):
    return resolve_function_import(name, _function_map, error_simulator)

def __dir__():
    return sorted(set(globals().keys()) | set(_function_map.keys()))

__all__ = list(_function_map.keys())