"""
This module provides functionality for managing payment types using their external identifiers.
"""

from typing import Dict, Optional
from .SimulationEngine import db

def patch(external_id: str, name: str, payment_method: str = None) -> Optional[Dict]:
    """
    Updates the details of an existing payment type using its external identifier.

    Args:
        external_id (str): The external identifier of the payment type to update.
        name (str): The new name for the payment type.
        payment_method (str, optional): The new payment method. One of: "Direct Deposit", "Check", "EFT", "Cash", "Credit Card", "Wire", "Manual", "Direct Debit", "PayPal", "EFT with Reference"

    Returns:
        Optional[Dict]: The updated payment type object if found, None if no type exists with the given external ID.
        The updated payment type object contains any of the following fields:
            - type (str): The object type, always "payment_types"
            - id (str): The payment type identifier
            - name (str): The name of the payment type
            - payment_method (str): Payment method (one of: "Direct Deposit", "Check", "EFT", "Cash", "Credit Card", "Wire", "Manual", "Direct Debit", "PayPal", "EFT with Reference")
            - external_id (str, optional): Optional external identifier (max 255 characters)
    """
    for type_ in db.DB["payments"]["payment_types"]:
        if type_.get("external_id") == external_id:
            type_["name"] = name
            if payment_method is not None:
                type_["payment_method"] = payment_method
            return type_
    return None

def delete(external_id: str) -> bool:
    """
    Deletes a payment type using its external identifier.

    Args:
        external_id (str): The external identifier of the payment type to delete.

    Returns:
        bool: True if the payment type was deleted or did not exist, False if the operation failed.
    """
    db.DB["payments"]["payment_types"] = [
        type_ for type_ in db.DB["payments"]["payment_types"] if type_.get("external_id") != external_id
    ]
    return True 