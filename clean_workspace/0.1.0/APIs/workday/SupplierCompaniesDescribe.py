"""
Supplier Company Field Description Module

This module provides functionality for describing the fields available in the
supplier company object. It allows users to retrieve a list of all available
fields that can be used when working with supplier company data.

The module interfaces with the simulation database to provide field information
for supplier company objects, enabling users to understand the structure and
available attributes of supplier company data.
"""

from typing import List, Tuple, Union, Any
from .SimulationEngine import db

def get() -> Tuple[Union[List[str], List], int]:
    """
    Describes the Supplier Company object fields.

    Returns a list of field names for the Supplier Company resource. This metadata 
    is useful for understanding the available fields that can be used when working 
    with supplier company data.

    Returns:
        Tuple[Union[List[str], List], int]: A tuple containing:
            - List[str]: A list of supplier company field names (strings)
            - int: HTTP status code (200 for success)
    """

    if not db.DB["suppliers"]["supplier_companies"]:
        return [], 200
    return list(db.DB["suppliers"]["supplier_companies"][list(db.DB["suppliers"]["supplier_companies"].keys())[0]].keys()), 200 