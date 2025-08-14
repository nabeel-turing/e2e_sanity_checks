"""
Event Reports Management Module for Workday Strategic Sourcing API Simulation.

This module provides functionality for managing and retrieving event reports
in the Workday Strategic Sourcing system. It supports operations for accessing
report entries, retrieving specific report data, and managing report schemas.
The module enables users to track and analyze event-related data through
comprehensive reporting capabilities.
"""

from typing import List, Dict, Any
from .SimulationEngine import db

def get_entries() -> List[Dict[str, Any]]:
    """
    Retrieves a list of event report entries.

    Event report entries contain detailed records of events captured within the system. These can include audit events, workflow triggers, system updates, etc. The response is paginated and supports traversal through `next` and `prev` links.

    Returns:
        List[Dict[str, Any]]: A list of event report entries. It can contain the following keys:
            - type (str): Always "event_report_entries".
            - id (str): Unique identifier for the event report.
            - attributes (Dict[str, Any]): Properties of the event report. It can contain the following keys:
                - fields (List[Dict[str, str]]): List of fields present in the schema.
                    - type (str): Field data type.
                        - Enum: "text", "date", "integer", "select", "string"
                    - name (str): Field name used in event reports.

    """

    return db.DB["reports"].get('event_reports_entries', [])

def get_event_report_entries(event_report_id: int) -> List[Dict[str, Any]]:
    """
    Retrieves a list of event report entries for a specific event report.

    This endpoint provides detailed entries linked to a single event report, identified by `event_report_id`. It is useful for retrieving scoped data related to a specific event. The response is paginated.

    Args:
        event_report_id (int): Unique identifier for the event report to retrieve entries from.

    Returns:
        List[Dict[str, Any]]: A list of event report entries tied to the provided report ID. It can contain the following keys:
            - type (str): Always "event_report_entries".
            - id (str): Event report entry ID.
            - attributes (Dict[str, Any]): Attributes of each entry. It can contain the following keys:
                - fields (List[Dict[str, str]]): List of fields present in the schema.
                    - type (str): Field data type.
                        - Enum: "text", "date", "integer", "select", "string"
                    - name (str): Field name used in event reports.

    """

    return db.DB["reports"].get(f'event_reports_{event_report_id}_entries', [])

def get_reports() -> List[Dict[str, Any]]:
    """
    Retrieves a list of event report entries owned by the user.

    **Deprecated**: This endpoint is only supported in API version 2018-04-01 and has been deprecated as of 2019-01-01. It returns report entries specific to the authenticated user.

    Returns:
        List[Dict[str, Any]]: A list of event report entries owned by the user. It can contain the following keys:
            - type (str): Always "event_report_entries".
            - id (str): Event report entry ID.
            - attributes (Dict[str, Any]): Attributes of each entry. It can contain the following keys:
                - fields (List[Dict[str, str]]): List of fields present in the schema.
                    - type (str): Field data type.
                        - Enum: "text", "date", "integer", "select", "string"
                    - name (str): Field name used in event reports.
    """

    return db.DB["reports"].get('event_reports', [])

def get_schema() -> Dict[str, Any]:
    """
    Retrieves the schema definition for event report entries.

    This schema provides metadata about the fields available in event report entries, including their names and data types. It can be used to dynamically interpret and render event report data.

    Returns:
        Dict[str, Any]: Schema definition for event report entries. It can contain the following keys:
            - id (str): Always "event_schemas".
            - type (str): Always "event_schemas".
            - attributes (Dict[str, Any]): It can contain the following keys:
                - fields (List[Dict[str, str]]): List of fields present in the schema.
                    - type (str): Field data type.
                        - Enum: "text", "date", "integer", "select", "string"
                    - name (str): Field name used in event reports.
    """

    return db.DB["reports"].get('event_reports_schema', {}) 