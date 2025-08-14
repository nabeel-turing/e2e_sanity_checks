"""
This module provides functionality for retrieving the schema and field definitions
of bid line items in the Workday Strategic Sourcing system. It enables users to
understand the structure and available fields of bid line item objects.
"""

from .SimulationEngine import db

def get() -> list:
    """Retrieves the list of available fields for bid line item objects.

    This function returns a comprehensive list of all fields that can be present
    in a bid line item object, based on the schema definition in the system.

    Returns:
        list: A list of strings, where each string represents a field name
            available in bid line item objects. The list includes all possible
            fields that can be present in a bid line item.

    Note:
        The function uses the first bid line item in the database as a template
        to determine the available fields. This assumes that all bid line items
        share the same schema structure.
    """
    return list(db.DB['events']['bid_line_items'][list(db.DB['events']['bid_line_items'].keys())[0]].keys())
