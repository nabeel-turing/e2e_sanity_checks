import json
import os

DB = {
    "reindex_info": {
        "running": False,
        "type": None,
    },
    "application_properties": {},
    "application_roles": {},
    "avatars": [],
    "components": {},
    "dashboards": {},
    "filters": {},
    "groups": {},
    "issues": {},
    "issue_links": [],
    "issue_link_types": {},
    "issue_types": {},
    "jql_autocomplete_data": {},
    "licenses": {},
    "my_permissions": {},
    "my_preferences": {},
    "permissions": {},
    "permission_schemes": {},
    "priorities": {},
    "projects": {},
    "project_categories": {},
    "resolutions": {},
    "roles": {},
    "webhooks": {},
    "workflows": {},
    "security_levels": {},
    "statuses": {},
    "status_categories": {},
    "users": {},
    "versions": {},
    # ...
}

###############################################################################
def save_state(filepath: str) -> None:
    """Save the current DB state to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(DB, f, indent=2)

def load_state(filepath: str) -> None:
    """Load DB state from a JSON file, replacing the current in-memory DB."""
    global DB
    if os.path.isfile(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            DB.update(json.load(f))