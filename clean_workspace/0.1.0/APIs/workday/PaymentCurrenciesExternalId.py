"""
Module for managing payment currencies by external identifier in the Workday Strategic Sourcing system.

This module provides functionality for managing payment currencies using their external identifiers.
It supports operations for updating currency details and deleting currencies based on their external IDs.
This is particularly useful when integrating with external systems that maintain their own currency identifiers.
"""

from typing import Dict, Optional
from .SimulationEngine import db

def patch(external_id: str, alpha: str, numeric: str) -> Optional[Dict]:
    """
    Updates the details of an existing payment currency using its external identifier.

    Args:
        external_id (str): The external identifier of the currency to update.
        alpha (str): The new three-letter currency code (e.g., USD, EUR).
        numeric (str): The new numeric currency code.

    Returns:
        Optional[Dict]: The updated currency object if found, None if no currency exists with the given external ID.
                        The updated currency object contains any of the following fields:
                            - type: Object type, should always be "payment_currencies"
                            - id: Payment currency identifier string
                            - alpha: Three-letter alphabetic currency code (e.g., USD, EUR)
                            - numeric: Three-digit numeric currency code
                            - external_id: Optional external identifier (max 255 characters)
    """
    for currency in db.DB["payments"]["payment_currencies"]:
        if currency.get("external_id") == external_id:
            currency["alpha"] = alpha
            currency["numeric"] = numeric
            return currency
    return None

def delete(external_id: str) -> bool:
    """
    Deletes a payment currency using its external identifier.

    Args:
        external_id (str): The external identifier of the currency to delete.

    Returns:
        bool: True if the currency was deleted or did not exist, False if the operation failed.
    """
    db.DB["payments"]["payment_currencies"] = [
        currency for currency in db.DB["payments"]["payment_currencies"] if currency.get("external_id") != external_id
    ]
    return True 