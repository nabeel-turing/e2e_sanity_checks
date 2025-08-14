"""
Module for managing payment currencies in the Workday Strategic Sourcing system.

This module provides functionality for managing payment currencies used in the Workday Strategic Sourcing system.
It supports operations for retrieving all available payment currencies and creating new currency entries.
Each currency is identified by its alpha code (e.g., USD, EUR) and numeric code, with an optional external identifier.
"""

from typing import List, Dict

from .SimulationEngine import db

def get() -> List[Dict]:
    """
    Retrieves a list of all available payment currencies in the system.

    Returns:
        List[Dict]: A list of payment currency objects, each containing:
                   - type: Object type, should always be "payment_currencies"
                   - id: Payment currency identifier string
                   - alpha: Three-letter alphabetic currency code (e.g., USD, EUR)
                   - numeric: Three-digit numeric currency code
                   - external_id: Optional external identifier (max 255 characters)
    """
    return db.DB["payments"]["payment_currencies"]

def post(alpha: str, numeric: str, external_id: str = None) -> Dict:
    """
    Creates a new payment currency entry in the system.

    Args:
        alpha (str): The three-letter currency code (e.g., USD, EUR).
        numeric (str): The numeric currency code.
        external_id (str, optional): An external identifier for the currency.

    Returns:
        Dict: The newly created payment currency object.
              The newly created payment currency object contains any of the following fields:
                  - type: Object type, should always be "payment_currencies"
                  - id: Payment currency identifier string
                  - alpha: Three-letter alphabetic currency code (e.g., USD, EUR)
                  - numeric: Three-digit numeric currency code
                  - external_id: Optional external identifier (max 255 characters)
    """
    new_currency = {
        "id": db.DB["payments"]["payment_currency_id_counter"],
        "alpha": alpha,
        "numeric": numeric,
        "external_id": external_id,
    }
    db.DB["payments"]["payment_currencies"].append(new_currency)
    db.DB["payments"]["payment_currency_id_counter"] += 1
    return new_currency 