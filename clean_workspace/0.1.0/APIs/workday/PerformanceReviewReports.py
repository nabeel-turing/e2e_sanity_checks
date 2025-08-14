"""
Performance Review Reports Module

This module provides functionality for managing and retrieving performance review reports
in the Workday Strategic Sourcing system. It supports operations for retrieving both the
report entries and the associated schema definitions.

The module interfaces with the simulation database to provide access to performance review
report data, which includes comprehensive information about performance reviews, their
status, and associated metadata.

Functions:
    get_entries: Retrieves a list of all performance review report entries
    get_schema: Retrieves the schema definition for performance review reports
"""

from .SimulationEngine import db
from typing import Dict, Any, Tuple, List

def get_entries() -> List[Dict[str, Any]]:
    """
    Retrieves a list of performance review report entries.

    Returns detailed performance review report data in a paginated format. Each entry contains attributes related to a performance review. Use pagination links to iterate through results.

    Returns:
        List[Dict[str, Any]]: A list of performance review report entries. It can contain the following fields:
            - type (str): Always "performance_review_report_entries".
            - id (Any): Unique identifier for the report entry.
            - attributes (Dict[str, Any]): Key-value pairs for the report entry data.
    """

    return db.DB["reports"]["performance_review_reports_entries"]

def get_schema() -> Dict[str, Any]:
    """
    Retrieves the schema for the performance review report.

    The schema defines the structure of performance review report entries, including field types and names. This is useful for dynamically building forms, validating input, or rendering reports.

    Returns:
        Dict[str, Any]: Schema definition for performance review report entries. It can contain the following fields:
            - id (str): Should always be "performance_review_schemas".
            - type (str): Should always be "performance_review_schemas".
            - attributes (Dict[str, Any]): It can contain the following keys:
                - fields (List[Dict[str, str]]): List of field definitions. It can contain the following keys:
                    - type (str): Data type of the field.
                        - Enum: "text", "date", "integer", "select", "string"
                    - name (str): Name of the field.
    """

    return db.DB["reports"]["performance_review_reports_schema"] 