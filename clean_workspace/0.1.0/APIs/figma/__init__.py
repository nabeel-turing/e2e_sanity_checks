"""
Figma API Simulation

This package provides a simulation of the Figma API functionality.
It allows for fetching figma files and basic operations in a simulated environment.
"""

from .SimulationEngine.db import DB, load_state, save_state
from typing import Optional, Dict, Any, List, Tuple

from .SimulationEngine.utils import filter_none_values_from_dict
from .SimulationEngine.custom_errors import NotFoundError, InvalidInputError, DownloadError

from . import file_management
from . import node_editing
from . import node_creation
from . import document_context
from . import node_reading
from . import annotation_operations
from . import layout_operations

import importlib
import os
import json
import tempfile
from common_utils.error_handling import get_package_error_mode
from .SimulationEngine.db import DB, load_state, save_state
from common_utils.init_utils import create_error_simulator, resolve_function_import
from figma.SimulationEngine import utils

# Get the directory of the current file
_INIT_PY_DIR = os.path.dirname(__file__)

# Create error simulator using the utility function
error_simulator = create_error_simulator(_INIT_PY_DIR)

# Get the error mode for the package
ERROR_MODE = get_package_error_mode()

# Function map
_function_map = {
    'get_figma_data':'figma.file_management.get_figma_data',
    'download_figma_images':'figma.file_management.download_figma_images',
    'move_node':'figma.node_editing.move_node',
    'clone_node':'figma.node_creation.clone_node',
    'resize_node':'figma.node_editing.resize_node',
    'delete_node':'figma.node_editing.delete_node',
    'get_styles':'figma.document_context.get_styles',
    'create_rectangle':'figma.node_creation.create_rectangle',
    'set_fill_color':'figma.node_editing.set_fill_color',
    'delete_multiple_nodes':'figma.node_editing.delete_multiple_nodes',
    'set_text_content':'figma.node_editing.set_text_content',
    'set_stroke_color':'figma.node_editing.set_stroke_color',
    'set_layout_mode':'figma.layout_operations.set_layout_mode',
    'get_local_components': 'figma.document_context.get_local_components',
    'scan_nodes_by_types':'figma.node_reading.scan_nodes_by_types',
    'get_selection':'figma.node_reading.get_selection',
    'get_node_info':'figma.node_reading.get_node_info',
    'get_annotations':'figma.annotation_operations.get_annotations',
    'set_annotation':'figma.annotation_operations.set_annotation',
    'create_frame':'figma.node_creation.create_frame',
    'set_current_file':'figma.file_management.set_current_file',
    'create_text':'figma.node_creation.create_text',
}

# Separate utils map for utility functions
_utils_map = {
    'create_file':'figma.SimulationEngine.utils.create_file',
    'list_available_files':'figma.SimulationEngine.utils.list_available_files',
}

# You could potentially generate this map dynamically by inspecting the package,
# but that adds complexity and potential fragility. A manual map is often safer.
# --- Implement __getattr__ ---

def __getattr__(name: str):
    return resolve_function_import(name, _function_map, error_simulator)

def __dir__():
    return sorted(set(globals().keys()) | set(_function_map.keys()))

__all__ = list(_function_map.keys())