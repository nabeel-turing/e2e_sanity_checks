"""
NotesAndLists API Simulation

This package provides a simulation of the NotesAndLists API functionality.
It allows for basic query execution and data manipulation in a simulated environment.
"""

import importlib
import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pydantic import ValidationError
from .SimulationEngine.db import DB, load_state, save_state
from common_utils.init_utils import create_error_simulator, resolve_function_import
from common_utils.error_handling import get_package_error_mode
from notes_and_lists.SimulationEngine import utils

# Get the directory of the current file
_INIT_PY_DIR = os.path.dirname(__file__)

# Create error simulator using the utility function
error_simulator = create_error_simulator(_INIT_PY_DIR)

# Get the error mode for the package
ERROR_MODE = get_package_error_mode()

# Function map
_function_map = {
    "create_list": "notes_and_lists.lists.create_list",
    "create_note": "notes_and_lists.notes_and_lists.create_note",
    "add_to_list": "notes_and_lists.lists.add_to_list",
    "show_all": "notes_and_lists.notes_and_lists.show_all",
    "show_notes_and_lists": "notes_and_lists.notes_and_lists.show_notes_and_lists",
    "get_notes_and_lists": "notes_and_lists.notes_and_lists.get_notes_and_lists",
    "delete_notes_and_lists": "notes_and_lists.notes_and_lists.delete_notes_and_lists",
    "delete_list_item": "notes_and_lists.notes_and_lists.delete_list_item",
    "update_title": "notes_and_lists.notes_and_lists.update_title",
    "update_list_item": "notes_and_lists.notes_and_lists.update_list_item",
    "append_to_note": "notes_and_lists.notes_and_lists.append_to_note",
    "share_notes_and_lists": "notes_and_lists.notes_and_lists.share_notes_and_lists",
    "update_note": "notes_and_lists.notes_and_lists.update_note",
    "undo": "notes_and_lists.notes_and_lists.undo",
    "search_notes_and_lists": "notes_and_lists.SimulationEngine.utils.search_notes_and_lists"
}

def __getattr__(name: str):
    return resolve_function_import(name, _function_map, error_simulator)

def __dir__():
    return sorted(set(globals().keys()) | set(_function_map.keys()))

__all__ = list(_function_map.keys())