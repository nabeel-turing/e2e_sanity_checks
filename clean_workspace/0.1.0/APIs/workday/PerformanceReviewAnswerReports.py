"""
Performance Review Answer Reports Module

This module provides functionality for managing and retrieving performance review answer reports
in the Workday Strategic Sourcing system. It supports operations for retrieving both the
report entries and the associated schema definitions.

The module interfaces with the simulation database to provide access to performance review
answer report data, which includes detailed information about answers provided in performance
reviews and their associated metadata.

Functions:
    get_entries: Retrieves a list of all performance review answer report entries
    get_schema: Retrieves the schema definition for performance review answer reports
"""

from typing import Dict, List, Any
from .SimulationEngine import db

def get_entries() -> List[Dict[str, Any]]:
    """
    Retrieves a list of performance review answer entries.

    This endpoint returns detailed entries from performance review responses, useful for evaluation analysis, tracking progress, and generating summaries. Pagination is supported via `next` and `prev` links.

    Returns:
       List[Dict[str, Any]]: A paginated response containing performance review answer entries.

            - data (List[Dict[str, Any]]): List of performance review answer report entries.
                - type (str): Always "performance_review_answer_report_entries".
                - id (str): Unique identifier for the report entry.
                - attributes (Dict[str, Any]): Core attributes of the answer entry.
                    - [Dynamic schema based on review configuration]

            - links (Dict[str, Optional[str]]):
                - next (str|None): Link to the next page of results.
                - prev (str|None): Link to the previous page of results.
    """

    return db.DB["reports"].get('performance_review_answer_reports_entries', [])

def get_schema() -> Dict[str, Any]:
    """
    Retrieves the schema for performance review answer reports.

    This schema outlines the structure of performance review answers returned by the API, including field names and their respective data types. Useful for dynamic rendering or processing of answer entries.

    Returns:
        Dict[str, Any]: Performance review answer schema definition.

            - data (Dict[str, Any]):
                - id (str): Always "performance_review_answer_schemas".
                - type (str): Always "performance_review_answer_schemas".
                - attributes (Dict[str, Any]):
                    - fields (List[Dict[str, str]]): Schema fields defining the structure of answer entries.
                        - type (str): Field data type.
                            - Enum: "text", "date", "integer", "select", "string"
                        - name (str): Human-readable name of the field.
    """

    return db.DB["reports"].get('performance_review_answer_reports_schema', {}) 