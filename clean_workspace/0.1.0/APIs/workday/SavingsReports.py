"""
Savings Reports Management Module

This module provides functionality for managing savings reports in the Workday Strategic
Sourcing system. It supports operations for retrieving savings report entries and their
associated schema definitions.

The module interfaces with the simulation database to provide access to savings report
data, which includes detailed information about cost savings, financial metrics, and
related reporting information.

Functions:
    get_entries: Retrieves all savings report entries from the system
    get_schema: Retrieves the schema definition for savings reports
"""

from typing import List, Dict, Any
from .SimulationEngine import db

def get_entries() -> List[Dict[str, Any]]:
    """
    Retrieves a list of savings report entries.

    Returns all savings-related entries available to the authenticated user.

    Returns:
        List[Dict[str, Any]]: A list of savings report entries. It can contain the following keys:
            - type (str): Always "savings_report_entries".
            - id (str): Unique identifier for the savings report entry.
            - attributes (Dict[str, Any]): Report-specific fields (see schema for detailed fields). It can contain the following keys:
                - fields (List[Dict[str, str]]): List of fields present in the schema.
                    - type (str): Field data type.
                        - Enum: "text", "date", "integer", "select", "string"
                    - name (str): Field name used in savings reports.

    """

    return db.DB["reports"].get('savings_reports_entries', [])

def get_schema() -> Dict[str, Any]:
    """
    Retrieves the schema definition for the savings report.

    The schema provides a list of fields and their types used in the savings report entries. This is useful for understanding the expected structure and available data fields when creating or interpreting report entries.


    Returns:
        Dict[str, Any]: A dictionary describing the savings report schema.

            - data (Dict[str, Any]):
                - id (str): Static identifier for the schema object. Always "savings_schemas".
                - type (str): Always "savings_schemas".
                - attributes (Dict[str, Any]):
                    - fields (List[Dict[str, Any]]): List of fields present in the schema.
                        - type (str): Field data type.
                            - Enum: "text", "date", "integer", "select", "string"
                        - name (str): Field name used in savings reports.

    Raises:
        HTTPError 401: Unauthorized – Missing or invalid API credentials.
    """

    return db.DB["reports"].get('savings_reports_schema', {}) 