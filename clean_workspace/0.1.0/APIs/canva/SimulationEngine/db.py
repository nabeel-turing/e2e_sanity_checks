# canva/SimulationEngine/db.py
import json
import time
import os

DB = {
    "Users": {
        "auDAbliZ2rQNNOsUl5OLu": {
            "user_id": "",
            "team_id": "",
            "profile": {"display_name": "John Doe"},
        }
    },
    "Designs": {
        "DAFVztcvd9z": {
            "id": "",
            "title": "",
            "design_type": {"type": "", "name": ""},
            "owner": {"user_id": "", "team_id": ""},
            "thumbnail": {"width": 0, "height": 0, "url": ""},
            "urls": {"edit_url": "", "view_url": ""},
            "created_at": 0,
            "updated_at": 0,
            "page_count": 0,
            "pages": {
                "0": {"index": 0, "thumbnail": {"width": 0, "height": 0, "url": ""}}
            },
            "comments": {
                "threads": {
                    "KeAbiEAjZEj": {
                        "id": "KeAbiEAjZEj",
                        "design_id": "",
                        "thread_type": {
                            "type": "",
                            "content": {"plaintext": "", "markdown": ""},
                            "mentions": {
                                "oUnPjZ2k2yuhftbWF7873o:oBpVhLW22VrqtwKgaayRbP": {
                                    "tag": "",
                                    "user": {
                                        "user_id": "",
                                        "team_id": "",
                                        "display_name": "",
                                    },
                                }
                            },
                            "assignee": {"id": "", "display_name": ""},
                            "resolver": {"id": "", "display_name": ""},
                        },
                        "author": {"id": "", "display_name": ""},
                        "created_at": 0,
                        "updated_at": 0,
                        "replies": {
                            "KeAZEAjijEb": {
                                "id": "KeAZEAjijEb",
                                "design_id": "DAFVztcvd9z",
                                "thread_id": "KeAbiEAjZEj",
                                "author": {"id": "", "display_name": ""},
                                "content": {"plaintext": "", "markdown": ""},
                                "mentions": {
                                    "oUnPjZ2k2yuhftbWF7873o:oBpVhLW22VrqtwKgaayRbP": {
                                        "tag": "",
                                        "user": {
                                            "user_id": "",
                                            "team_id": "",
                                            "display_name": "",
                                        },
                                    }
                                },
                                "created_at": 0,
                                "updated_at": 0,
                            }
                        },
                    }
                }
            },
        }
    },
    "brand_templates": {
        "DEMzWSwy3BI": {
            "id": "",
            "title": "",
            "design_type": {"type": "", "name": ""},
            "view_url": "",
            "create_url": "",
            "thumbnail": {"width": 0, "height": 0, "url": ""},
            "created_at": 0,
            "updated_at": 0,
            "datasets": {},
        }
    },
    "autofill_jobs": {},
    "asset_upload_jobs": {
        "Msd59349fz": {
            "id": "",
            "name": "",
            "tags": [],
            "thumbnail": {"url": ""},
            "status": "",
            "created_at": 0,
        }
    },
    "design_export_jobs": {},
    "design_import_jobs": {},
    "url_import_jobs": {},
    "assets": {
        "Msd59349ff": {
            "type": "",
            "id": "",
            "name": "",
            "tags": [],
            "created_at": 0,
            "updated_at": 0,
            "thumbnail": {"width": 0, "height": 0, "url": ""},
        }
    },
    "folders": {
        "ede108f5-30e4-4c31-b087-48f994eabeff": {
            "assets": [],
            "Designs": [],
            "folders": [],
            "folder": {
                "id": "",
                "name": "",
                "created_at": 0,
                "updated_at": 0,
                "thumbnail": {"width": 0, "height": 0, "url": "", "parent_id": ""},
            },
        }
    },
}


def save_state(filepath: str) -> None:
    """
    Saves the current state of the database to a file.

    Args:
        filepath (str): Path to the file where the state should be saved.
    """
    with open(filepath, "w") as f:
        json.dump(DB, f)


def load_state(filepath: str) -> None:
    """
    Loads the database state from a file and updates the global DB.

    Args:
        filepath (str): Path to the file from which to load the state.
    """
    global DB
    with open(filepath, "r") as f:
        DB.clear()
        DB.update(json.load(f))

