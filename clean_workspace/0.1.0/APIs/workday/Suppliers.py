"""
Suppliers Management Module

This module provides functionality for managing suppliers in the Workday Strategic
Sourcing system. It supports operations for retrieving supplier information,
including both bulk retrieval of all suppliers and individual supplier lookup.

The module interfaces with the simulation database to provide comprehensive
supplier management capabilities, allowing users to:
- Retrieve a list of all suppliers in the system
- Look up individual suppliers by their unique identifier
"""

from typing import List, Dict, Any, Optional
from .SimulationEngine import db

def get_suppliers() -> List[Dict[str, Any]]:
    """
    Returns a list of all supplier companies from the database.

    This function retrieves all suppliers stored in the simulation database
    without any filtering or pagination.

    Returns:
        List[Dict[str, Any]]: A list of supplier company objects.
            Each supplier object contains:
                - id (str): Unique supplier company identifier.
                - name (str): Supplier company name.
                - industry (str): Industry category of the supplier.
                - contact_email (str): Contact email address for the supplier.
    """

    return db.DB["reports"].get('suppliers', [])

def get_supplier(supplier_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieves the details of an existing supplier company by its unique ID.

    This function searches for a supplier in the database by their ID and returns
    the supplier object if found, or None if not found.

    Args:
        supplier_id (int): Unique identifier of the supplier company to retrieve.

    Returns:
        Optional[Dict[str, Any]]: The supplier company object if found, None otherwise.
            The supplier object contains:
                - id (str): Unique supplier company identifier.
                - name (str): Supplier company name.
                - industry (str): Industry category of the supplier.
                - contact_email (str): Contact email address for the supplier.
    """

    suppliers = db.DB["reports"].get('suppliers', [])
    for supplier in suppliers:
        if supplier.get('id') == supplier_id:
            return supplier
    return None 

