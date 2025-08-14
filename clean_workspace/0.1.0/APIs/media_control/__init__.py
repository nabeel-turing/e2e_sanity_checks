"""
Media Control API Simulation

This package provides a simulation of the Android Media Control API functionality.
It allows for controlling media playback, seeking, and rating in a simulated environment.
"""

import importlib
import os
import json
import tempfile
from . import media_control

from common_utils.init_utils import create_error_simulator, resolve_function_import
from common_utils.error_handling import get_package_error_mode
from .SimulationEngine.db import DB, load_state, save_state
from media_control.SimulationEngine import utils

# Get the directory of the current file
_INIT_PY_DIR = os.path.dirname(__file__)

# Create error simulator using the utility function
error_simulator = create_error_simulator(_INIT_PY_DIR)

# Get the error mode for the package
ERROR_MODE = get_package_error_mode()

# Function map
_function_map = {
    # Core media control operations
    "change_playback_state": "media_control.media_control.change_playback_state",
    "pause": "media_control.media_control.pause",
    "stop": "media_control.media_control.stop",
    "resume": "media_control.media_control.resume",
    "next": "media_control.media_control.next",
    "previous": "media_control.media_control.previous",
    "replay": "media_control.media_control.replay",
    "seek_relative": "media_control.media_control.seek_relative",
    "seek_absolute": "media_control.media_control.seek_absolute",
    "like": "media_control.media_control.like",
    "dislike": "media_control.media_control.dislike",
}

def __getattr__(name: str):
    return resolve_function_import(name, _function_map, error_simulator)

def __dir__():
    return sorted(set(globals().keys()) | set(_function_map.keys()))

__all__ = list(_function_map.keys())