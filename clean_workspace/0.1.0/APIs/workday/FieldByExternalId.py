"""
Field Management Module for Workday Strategic Sourcing API Simulation.

This module provides functionality for managing fields by their external identifiers
in the Workday Strategic Sourcing system. It supports retrieving, updating, and
deleting specific fields using their external IDs, with comprehensive error
handling for invalid or non-existent external IDs.
"""
from typing import Dict, Optional

from .SimulationEngine import db

def get(external_id: str) -> Dict:
    """Retrieves the details of a specific field by its external ID.

    This function returns the complete details of a field identified by its
    external identifier. The function searches through all fields to find a
    match for the provided external ID.

    Args:
        external_id (str): The external identifier of the field to retrieve.

    Returns:
        Dict: A dictionary containing the field details, including:
            - id (Union[int, str]): Internal unique identifier of the field
            - external_id (str): The provided external identifier
            - name (str): Name of the field
            - type (str): Data type of the field (e.g., 'text', 'number', 'date')
            - required (bool): Whether the field is required
            - description (str): Detailed description of the field
            - created_at (str): Timestamp of field creation
            - updated_at (str): Timestamp of last update
            - configurations (Dict): Field-specific settings
            - Other properties as defined in the database

    Raises:
        ValueError: If no field exists with the given external ID.

    Note:
        The function performs a linear search through all fields to find a match
        for the external ID. The returned field data is read-only and should not
        be modified directly.
    """
    for field in db.DB['fields'].values():
        if field.get('external_id') == external_id:
            return field
    raise ValueError(f"Field with external_id {external_id} not found")

def patch(external_id: str, body: Optional[Dict] = None) -> Dict:
    """Updates the details of an existing field by its external ID.

    This function updates the properties of a field identified by its external
    identifier. The function verifies that the provided body includes the correct
    external ID before performing the update.

    Args:
        external_id (str): The external identifier of the field to update.
        body (Optional[Dict]): A dictionary containing the updated properties
            for the field, including:
            - external_id (str): Must match the external_id in the URL
            - name (str): Updated name of the field
            - type (str): Updated data type of the field
            - required (bool): Updated required status
            - description (str): Updated description
            - configurations (Dict): Updated field-specific settings
            - Other properties as defined in the database
            Defaults to None.

    Returns:
        Dict: The updated field data, including all current properties of the field.

    Raises:
        ValueError: If:
            - No field exists with the given external ID
            - The body is None
            - The body does not contain an 'external_id' field
            - The 'external_id' in the body does not match the URL parameter

    Note:
        The function performs a linear search through all fields to find a match
        for the external ID. The update is performed atomically and will either
        succeed completely or fail without partial updates.
    """
    field = None
    for f in db.DB['fields'].values():
        if f.get('external_id') == external_id:
            field = f
            break
    
    if not field:
        raise ValueError(f"Field with external_id {external_id} not found")
    
    if not body or 'external_id' not in body or body['external_id'] != external_id:
        raise ValueError("Body must contain 'external_id' matching the path parameter")
    
    field.update(body)
    return field

def delete(external_id: str) -> None:
    """Deletes a specific field from the system by its external ID.

    This function removes a field identified by its external identifier from
    the system. The function searches through all fields to find a match for
    the provided external ID before performing the deletion.

    Args:
        external_id (str): The external identifier of the field to delete.

    Raises:
        ValueError: If no field exists with the given external ID.

    Note:
        The function performs a linear search through all fields to find a match
        for the external ID. The deletion is permanent and cannot be undone.
    """
    field_id = None
    for id, field in db.DB['fields'].items():
        if field.get('external_id') == external_id:
            field_id = id
            break
    
    if field_id is None:
        raise ValueError(f"Field with external_id {external_id} not found")
    
    del db.DB['fields'][field_id] 