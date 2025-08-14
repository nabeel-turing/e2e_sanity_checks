"""
This module provides functionality for managing payment currencies using their internal identifiers.
"""

from typing import Dict, Optional
from .SimulationEngine import db

def patch(id: int, alpha: str, numeric: str, external_id: str = None) -> Optional[Dict]:
    """
    Updates the details of an existing payment currency using its internal identifier.

    Args:
        id (int): The internal identifier of the currency to update.
        alpha (str): The new three-letter currency code (e.g., USD, EUR).
        numeric (str): The new numeric currency code.
        external_id (str, optional): The new external identifier for the currency.

    Returns:
        Optional[Dict]: The updated currency object if found, None if no currency exists with the given ID.
                        The updated currency object contains any of the following fields:
                            - type: Object type, should always be "payment_currencies"
                            - id: Payment currency identifier string
                            - alpha: Three-letter alphabetic currency code (e.g., USD, EUR)
                            - numeric: Three-digit numeric currency code
                            - external_id: Optional external identifier (max 255 characters)

    """
    for currency in db.DB["payments"]["payment_currencies"]:
        if currency["id"] == id:
            currency["alpha"] = alpha
            currency["numeric"] = numeric
            currency["external_id"] = external_id
            return currency
    return None

def delete(id: int) -> bool:
    """
    Deletes a payment currency using its internal identifier.

    Args:
        id (int): The internal identifier of the currency to delete.

    Returns:
        bool: True if the currency was deleted or did not exist, False if the operation failed.
    """
    db.DB["payments"]["payment_currencies"] = [
        currency for currency in db.DB["payments"]["payment_currencies"] if currency["id"] != id
    ]
    return True 