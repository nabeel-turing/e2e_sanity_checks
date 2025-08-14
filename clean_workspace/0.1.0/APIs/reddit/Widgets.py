from .SimulationEngine.db import DB
from typing import Dict, Any, List  

"""
Simulation of /widgets endpoints.
Manages subreddit widget operations.
"""


def post_api_widget(widget_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Creates or updates a subreddit widget.

    Args:
        widget_data (Dict[str, Any]): The widget configuration data. The format varies based on the widget kind:
            - For 'image' widgets:
                {
                    "data": [
                        {
                            "height": int,
                            "linkUrl": str (optional),
                            "url": str,
                            "width": int,
                        },
                        ...
                    ],
                    "kind": "image",
                    "shortName": str (max 30 chars),
                    "styles": {
                        "backgroundColor": str (6-digit hex),
                        "headerColor": str (6-digit hex),
                    },
                }
            - For 'calendar' widgets:
                {
                    "configuration": {
                        "numEvents": int (1-50, default: 10),
                        "showDate": bool,
                        "showDescription": bool,
                        "showLocation": bool,
                        "showTime": bool,
                        "showTitle": bool,
                    },
                    "googleCalendarId": str (email),
                    "kind": "calendar",
                    "requiresSync": bool,
                    "shortName": str (max 30 chars),
                    "styles": {
                        "backgroundColor": str (6-digit hex),
                        "headerColor": str (6-digit hex),
                    },
                }
            - For 'textarea' widgets:
                {
                    "kind": "textarea",
                    "shortName": str (max 30 chars),
                    "styles": {
                        "backgroundColor": str (6-digit hex),
                        "headerColor": str (6-digit hex),
                    },
                    "text": str (markdown),
                }
            - For 'menu' widgets:
                {
                    "data": [
                        {
                            "text": str (max 20 chars),
                            "url": str,
                        }
                        OR
                        {
                            "children": [
                                {
                                    "text": str (max 20 chars),
                                    "url": str,
                                },
                                ...
                            ],
                            "text": str (max 20 chars),
                        },
                        ...
                    ],
                    "kind": "menu",
                    "showWiki": bool,
                }
            - For 'button' widgets:
                {
                    "buttons": [
                        {
                            "color": str (6-digit hex),
                            "fillColor": str (6-digit hex),
                            "hoverState": {
                                "color": str (6-digit hex),
                                "fillColor": str (6-digit hex),
                                "kind": "text",
                                "text": str (max 30 chars),
                                "textColor": str (6-digit hex),
                            }
                            OR
                            {
                                "height": int,
                                "imageUrl": str,
                                "kind": "image",
                                "width": int,
                            },
                            "kind": "text",
                            "text": str (max 30 chars),
                            "textColor": str (6-digit hex),
                            "url": str,
                        }
                        OR
                        {
                            "height": int,
                            "hoverState": {
                                "color": str (6-digit hex),
                                "fillColor": str (6-digit hex),
                                "kind": "text",
                                "text": str (max 30 chars),
                                "textColor": str (6-digit hex),
                            }
                            OR
                            {
                                "height": int,
                                "imageUrl": str,
                                "kind": "image",
                                "width": int,
                            },
                            "imageUrl": str,
                            "kind": "image",
                            "linkUrl": str,
                            "text": str (max 30 chars),
                            "width": int,
                        },
                        ...
                    ],
                    "description": str (markdown),
                    "kind": "button",
                    "shortName": str (max 30 chars),
                    "styles": {
                        "backgroundColor": str (6-digit hex),
                        "headerColor": str (6-digit hex),
                    },
                }
            - For 'community-list' widgets:
                {
                    "data": [
                        str (subreddit name),
                        ...
                    ],
                    "kind": "community-list",
                    "shortName": str (max 30 chars),
                    "styles": {
                        "backgroundColor": str (6-digit hex),
                        "headerColor": str (6-digit hex),
                    },
                }
            - For 'custom' widgets:
                {
                    "css": str (max 100000 chars),
                    "height": int (50-500),
                    "imageData": [
                        {
                            "height": int,
                            "name": str (max 20 chars),
                            "url": str,
                            "width": int,
                        },
                        ...
                    ],
                    "kind": "custom",
                    "shortName": str (max 30 chars),
                    "styles": {
                        "backgroundColor": str (6-digit hex),
                        "headerColor": str (6-digit hex),
                    },
                    "text": str (markdown),
                }
            - For 'post-flair' widgets:
                {
                    "display": str ("cloud" or "list"),
                    "kind": "post-flair",
                    "order": [
                        str (flair template ID),
                        ...
                    ],
                    "shortName": str (max 30 chars),
                    "styles": {
                        "backgroundColor": str (6-digit hex),
                        "headerColor": str (6-digit hex),
                    },
                }

    Returns:
        Dict[str, Any]:
        - If the widget data is invalid, returns a dictionary with the key "error" and the value "Invalid widget data.".
        - On successful creation/update, returns a dictionary with the following keys:
            - status (str): The status of the operation ("widget_created")
            - widget_id (str): The unique identifier for the created/updated widget
    """
    widget_id = f"widget_{len(DB.get('widgets', {}))+1}" # Use .get for safety
    DB.setdefault("widgets", {})[widget_id] = widget_data # Ensure keys exist
    return {"status": "widget_created", "widget_id": widget_id}


def delete_api_widget_widget_id(widget_id: str) -> Dict[str, Any]:
    """
    Deletes a specific widget.

    Args:
        widget_id (str): The identifier of the widget to delete.

    Returns:
        Dict[str, Any]:
        - If the widget ID is invalid, returns a dictionary with the key "error" and the value "Invalid widget ID.".
        - If the widget is not found, returns a dictionary with the key "error" and the value "widget_not_found".
        - On successful deletion, returns a dictionary with the following keys:
            - status (str): The status of the operation ("widget_deleted")
            - widget_id (str): The deleted widget's identifier
    """
    if widget_id in DB.get("widgets", {}):
        del DB["widgets"][widget_id]
        return {"status": "widget_deleted", "widget_id": widget_id}
    return {"error": "widget_not_found"}


def post_api_widget_image_upload_s3(filepath: str, mimetype: str) -> Dict[str, Any]:
    """
    Acquires and returns an upload lease to an S3 temporary bucket for widget image uploads.

    Args:
        filepath (str): The name and extension of the image file (e.g. "widget.png").
        mimetype (str): The MIME type of the image (e.g. "image/png").

    Returns:
        Dict[str, Any]:
        - If the filepath is invalid, returns a dictionary with the key "error" and the value "Invalid filepath.".
        - If the mimetype is invalid, returns a dictionary with the key "error" and the value "Invalid mimetype.".
        - On successful lease acquisition, returns a dictionary with the following keys:
            - credentials (Dict[str, str]): Temporary credentials for uploading assets to S3, containing:
                - access_key_id (str): The temporary access key ID
                - secret_access_key (str): The temporary secret access key
                - session_token (str): The temporary session token
            - s3_url (str): The S3 URL for the upload request
            - key (str): The key to use for uploading, which incorporates the provided filepath
    """
    lease = {
        "credentials": {
            "access_key_id": "EXAMPLEACCESSKEY",
            "secret_access_key": "EXAMPLESECRETACCESSKEY",
            "session_token": "EXAMPLESESSIONTOKEN"
        },
        "s3_url": "https://s3-temp-bucket.example.com/upload",
        "key": f"temp/{filepath}"
    }
    return lease


def patch_api_widget_order_section(section: str, ordered_widgets: List[str]) -> Dict[str, Any]:
    """
    Reorders widgets within a specified section.

    Args:
        section (str): The section name (e.g., "sidebar").
        ordered_widgets (List[str]): An ordered list of widget IDs.

    Returns:
        Dict[str, Any]:
        - If the section is invalid, returns a dictionary with the key "error" and the value "Invalid section.".
        - If the ordered widgets list is invalid, returns a dictionary with the key "error" and the value "Invalid widget order.".
        - On successful reordering, returns a dictionary with the following keys:
            - status (str): The status of the operation ("widget_order_patched")
            - section (str): The section name
            - ordered_widgets (List[str]): The ordered list of widget IDs
    """
    return {"status": "widget_order_patched", "section": section, "ordered_widgets": ordered_widgets}


def get_api_widgets() -> Dict[str, Any]:
    """
    Retrieves all widgets configured for a subreddit.

    Returns:
        Dict[str, Any]:
        - If there are no widgets, returns a dictionary with the key "error" and the value "No widgets found.".
        - On successful retrieval, returns a dictionary with the following keys:
            - widgets (Dict[str, Dict[str, Any]]): A dictionary of widget objects, where each key is a widget ID and each value is the widget configuration
    """
    return {"widgets": DB.get("widgets", {})} # Use .get for safety