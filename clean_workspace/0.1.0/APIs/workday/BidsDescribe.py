"""
This module provides functionality for retrieving the schema and field definitions
of bids in the Workday Strategic Sourcing system. It enables users to understand
the structure and available fields of bid objects. The module supports comprehensive
bid schema discovery and documentation.
"""

from typing import List
from .SimulationEngine import db

def get() -> List[str]:
    """Returns a list of fields for the bid object.

    Returns:    
        List[str]: A list of strings, where each string represents a field name
            available in bid objects. 

    Note:
        The function uses the first bid in the database as a template to
        determine the available fields. This assumes that all bids share
        the same schema structure.
    """
    return list(db.DB['events']['bids'][list(db.DB["events"]["bids"].keys())[0]].keys())