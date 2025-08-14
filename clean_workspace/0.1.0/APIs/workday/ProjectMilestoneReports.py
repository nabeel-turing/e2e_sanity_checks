"""
Project Milestone Reports Module

This module provides functionality for managing and retrieving project milestone reports
in the Workday Strategic Sourcing system. It supports operations for retrieving both the
report entries and the associated schema definitions.

The module interfaces with the simulation database to provide access to project milestone
report data, which includes comprehensive information about project milestones, their
status, completion dates, and associated metadata.

Functions:
    get_entries: Retrieves a list of all project milestone report entries
    get_schema: Retrieves the schema definition for project milestone reports
"""

from typing import Any, Dict, List
from .SimulationEngine import db

def get_entries() -> List[Dict[str, Any]]:
    """
    Retrieves a list of project milestone report entries.

    Each milestone entry provides details related to project milestones.

    Returns:
        List[Dict[str, Any]]: A list of project milestone report entries.
            Each entry contains:
                - type (str): Always "project_milestone_report_entries".
                - id (str): Unique identifier of the milestone report entry.
                - attributes (Dict[str, Any]): Attributes of the milestone report entry.
                    (Refer to schema for detailed structure.)
    """

    return db.DB["reports"]["project_milestone_reports_entries"]

def get_schema() -> Dict[str, Any]:
    """
    Retrieves the schema definition for project milestone reports.

    This endpoint provides metadata describing the fields available in project milestone reporting. Useful for dynamically rendering forms or parsing report data.

    Returns:
        Dict[str, Any]: A schema describing project milestone report fields. It can contain the following keys:
            - id (str): Identifier for the schema object, always "project_milestone_schemas".
            - type (str): Always "project_milestone_schemas".
            - attributes (Dict[str, Any]):
                - fields (List[Dict[str, str]]): A list of schema fields.
                    - type (str): Field type.
                        - Enum: "text", "date", "integer", "select", "string"
                    - name (str): Name of the field.

    """

    return db.DB["reports"]["project_milestone_reports_schema"] 