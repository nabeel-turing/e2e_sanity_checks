"""
This module provides functionality for managing payment types using their internal identifiers.
"""

from typing import Dict, Optional
from .SimulationEngine import db

def patch(id: int, name: str, payment_method: str = None, external_id: str = None) -> Optional[Dict]:
    """
    Updates the details of an existing payment type using its internal identifier.

    Args:
        id (int): The internal identifier of the payment type to update.
        name (str): The new name for the payment type. 
        payment_method (str, optional): The new payment method. One of: "Direct Deposit", "Check", "EFT", "Cash", "Credit Card", "Wire", "Manual", "Direct Debit", "PayPal", "EFT with Reference"
        external_id (str, optional): The new external identifier for the payment type.

    Returns:
        Optional[Dict]: The updated payment type object if found, None if no type exists with the given ID.
        The updated payment type object contains any of the following fields:
            - type (str): The object type, always "payment_types"
            - id (str): The payment type identifier
            - name (str): The name of the payment type
            - payment_method (str): Payment method (one of: "Direct Deposit", "Check", "EFT", "Cash", "Credit Card", "Wire", "Manual", "Direct Debit", "PayPal", "EFT with Reference")
            - external_id (str, optional): Optional external identifier (max 255 characters)
    """
    for type_ in db.DB["payments"]["payment_types"]:
        if type_["id"] == id:
            type_["name"] = name
            if external_id is not None:
                type_["external_id"] = external_id
            if payment_method is not None:
                type_["payment_method"] = payment_method
            return type_
    return None

def delete(id: int) -> bool:
    """
    Deletes a payment type using its internal identifier.

    Args:
        id (int): The internal identifier of the payment type to delete.

    Returns:
        bool: True if the payment type was deleted or did not exist, False if the operation failed.
    """
    db.DB["payments"]["payment_types"] = [type_ for type_ in db.DB["payments"]["payment_types"] if type_["id"] != id]
    return True 