from common_utils.print_log import print_log
import json
import os

# Define a global DB for simulation
DB = {
    "buckets": {
        "test-bucket-1": {
            "name": "test-bucket-1",
            "project": "test-project",
            "metageneration": "1",
            "softDeleted": False,
            "objects": [],
            "enableObjectRetention": False,
            "iamPolicy": {"bindings": []},
            "storageLayout": {},
            "generation": "1",
            "retentionPolicyLocked": False
        },
        "test-bucket-2": {
            "name": "test-bucket-2",
            "project": "test-project",
            "metageneration": "2",
            "softDeleted": True,
            "objects": ["file1", "file2"],
            "enableObjectRetention": True,
            "iamPolicy": {"bindings": []},
            "storageLayout": {},
            "generation": "2",
            "retentionPolicyLocked": True
        }
    }
}

# ---------------------------------------------------------------------------------------
# Persistence Class
# ---------------------------------------------------------------------------------------

def save_state(filepath: str) -> None:
    """Saves the current API state to a JSON file."""
    with open(filepath, 'w') as f:
        json.dump(DB, f, indent=4)

def load_state(filepath: str) -> None:
    """Loads the API state from a JSON file."""
    global DB
    try:
        with open(filepath, 'r') as f:
            DB.update(json.load(f))
    except FileNotFoundError:
        print_log(f"File not found: {filepath}. Starting with an empty state.")
        DB = {"buckets": {}}