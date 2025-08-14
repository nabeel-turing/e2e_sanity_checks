# --- Step 1: Import your application modules FIRST ---
# This is crucial for ErrorSimulator's _resolve_function_paths to find them in sys.modules
# when it's called during ErrorSimulator initialization or config loading.
from . import Users 
from . import Organizations
from . import Tickets
from . import Attachments
from . import Search
# ... any other of your modules that contain functions to be simulated ...

import os
from common_utils.error_handling import get_package_error_mode
from .SimulationEngine.db import DB, load_state, save_state
from common_utils.init_utils import create_error_simulator, resolve_function_import
from zendesk.SimulationEngine import utils

# Get the directory of the current file
_INIT_PY_DIR = os.path.dirname(__file__)

# Create error simulator using the utility function
error_simulator = create_error_simulator(_INIT_PY_DIR)

# Get the error mode for the package
ERROR_MODE = get_package_error_mode()

# Function map
_function_map = { # This map is for the public API aliasing via __getattr__
  "create_organization": "zendesk.Organizations.create_organization",
  "list_organizations": "zendesk.Organizations.list_organizations",
  "get_organization_details": "zendesk.Organizations.show_organization",
  "update_organization": "zendesk.Organizations.update_organization",
  "delete_organization": "zendesk.Organizations.delete_organization",
  "create_ticket": "zendesk.Tickets.create_ticket",
  "list_tickets": "zendesk.Tickets.list_tickets",
  "get_ticket_details": "zendesk.Tickets.show_ticket",
  "show_ticket": "zendesk.Tickets.show_ticket",
  "update_ticket": "zendesk.Tickets.update_ticket",
  "delete_ticket": "zendesk.Tickets.delete_ticket",
  "create_user": "zendesk.Users.create_user",
  "list_users": "zendesk.Users.list_users",
  "get_user_details": "zendesk.Users.show_user",
  "update_user": "zendesk.Users.update_user",
  "delete_user": "zendesk.Users.delete_user",
  "search": "zendesk.Search.list_search_results",
  "list_ticket_comments": "zendesk.Comments.list_ticket_comments",
  "delete_attachment": "zendesk.Attachments.delete_attachment",
  "show_attachment": "zendesk.Attachments.show_attachment",
  "create_attachment": "zendesk.Attachments.create_attachment"
}

def __getattr__(name: str):
    return resolve_function_import(name, _function_map, error_simulator)

def __dir__():
    return sorted(set(globals().keys()) | set(_function_map.keys()))

__all__ = list(_function_map.keys())