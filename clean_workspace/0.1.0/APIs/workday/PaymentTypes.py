"""
This module provides comprehensive functionality for managing payment types
"""

from typing import List, Dict, Optional
from .SimulationEngine import db

def get() -> List[Dict]:
    """
    Retrieves a list of all available payment types in the system.

    Returns:
        List[Dict]: A list of payment type objects, each containing:
                   - type (str): The object type, always "payment_types"
                   - id (str): The payment type identifier
                   - name (str): The name of the payment type
                   - payment_method (str): Payment method (one of: "Direct Deposit", "Check", "EFT", "Cash", "Credit Card", "Wire", "Manual", "Direct Debit", "PayPal", "EFT with Reference")
                   - external_id (str, optional): Optional external identifier (max 255 characters)
    """
    return db.DB["payments"]["payment_types"]

def post(name: str, payment_method: str, external_id: str = None) -> Dict:
    """
    Create a payment type with given parameters.

    Args:
        name (str): The name of the payment type (e.g., "Credit Card", "Bank Transfer").
        payment_method (str): The method of payment (e.g., "card", "transfer").
        external_id (str, optional): An external identifier for the payment type.

    Returns:
        Dict: The newly created payment type object containing any of the following fields:
            - type (str): The object type, always "payment_types"
            - id (str): The payment type identifier
            - name (str): The name of the payment type
            - payment_method (str): Payment method (one of: "Direct Deposit", "Check", "EFT", "Cash", "Credit Card", "Wire", "Manual", "Direct Debit", "PayPal", "EFT with Reference")
            - external_id (str, optional): Optional external identifier (max 255 characters)
    """
    new_type = {
        "id": db.DB["payments"]["payment_type_id_counter"],
        "name": name,
        "external_id": external_id,
        "payment_method": payment_method,
    }
    db.DB["payments"]["payment_types"].append(new_type)
    db.DB["payments"]["payment_type_id_counter"] += 1
    return new_type