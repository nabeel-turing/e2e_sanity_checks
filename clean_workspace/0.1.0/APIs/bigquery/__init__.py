"""
BigQuery API Simulation

This package provides a simulation of the BigQuery API functionality.
"""

import importlib
import json
import os
import re
import sqlite3
import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from . import bigqueryAPI
from pydantic import ValidationError
from common_utils.init_utils import create_error_simulator, resolve_function_import
from common_utils.error_handling import get_package_error_mode
from .SimulationEngine.db import DB, load_state, save_state
from . import bigqueryAPI
from .SimulationEngine.custom_errors import (
    DatasetNotFoundError,
    InvalidInputError,
    InvalidQueryError,
    ProjectNotFoundError,
    TableNotFoundError,
)
from .SimulationEngine.utils import parse_full_table_name, load_db_dict_to_sqlite
from bigquery.SimulationEngine import utils

# Get the directory of the current file
_INIT_PY_DIR = os.path.dirname(__file__)

# Create error simulator using the utility function
error_simulator = create_error_simulator(_INIT_PY_DIR)

# Get the error mode for the package
ERROR_MODE = get_package_error_mode()

# Function map
_function_map = {
    "list_tables": "bigquery.bigqueryAPI.list_tables",
    "describe_table": "bigquery.bigqueryAPI.describe_table",
    "execute_query": "bigquery.bigqueryAPI.execute_query",
}

def __getattr__(name: str):
    return resolve_function_import(name, _function_map, error_simulator)

def __dir__():
    global _function_map
    return sorted(set(globals().keys()) | set(_function_map.keys()))

__all__ = list(_function_map.keys())
