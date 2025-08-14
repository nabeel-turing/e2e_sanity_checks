"""
This module provides functionality for managing payment terms used in the Workday Strategic Sourcing system.
It supports operations for retrieving all available payment terms and creating new term entries.
Each payment term is identified by its name and an optional external identifier, which is useful for
integration with external systems that maintain their own payment term identifiers.
"""

from typing import List, Dict
from .SimulationEngine import db

def get() -> List[Dict]:
    """
    Retrieves a list of all available payment terms in the system.

    Returns:
        List[Dict]: A list of payment term objects, each containing any of the following fields:
                   - type (str): Object type, should always be "payment_terms"
                   - id (str): Payment term identifier string
                   - name (str): The name of the payment term
                   - external_id (str, optional): Optional external identifier
                   - attributes (dict): Payment term attributes containing:
                     - name (str): Payment term name (max 255 characters)
                     - external_id (str): Payment term external identifier (max 255 characters)
    """
    return db.DB["payments"]["payment_terms"]

def post(name: str, external_id: str = None) -> Dict:
    """
    Creates a new payment term entry in the system.

    Args:
        name (str): The name of the payment term (e.g., "Net 30", "Net 60").
        external_id (str, optional): An external identifier for the payment term.

    Returns:
        Dict: The newly created payment term object containing any of the following fields:
            - type (str): Object type, should always be "payment_terms"
            - id (str): Payment term identifier string
            - name (str): The name of the payment term
            - external_id (str, optional): Optional external identifier
            - attributes (dict): Payment term attributes containing:
                - name (str): Payment term name (max 255 characters)
                - external_id (str): Payment term external identifier (max 255 characters)
    """
    new_term = {
        "id": db.DB["payments"]["payment_term_id_counter"],
        "name": name,
        "external_id": external_id,
    }
    db.DB["payments"]["payment_terms"].append(new_term)
    db.DB["payments"]["payment_term_id_counter"] += 1
    return new_term 