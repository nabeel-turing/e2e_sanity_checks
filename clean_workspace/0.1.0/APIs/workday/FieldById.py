"""
This module provides functionality for managing fields by their unique identifiers
in the Workday Strategic Sourcing system. It supports retrieving, updating, and
deleting specific fields using their internal IDs, with robust error handling
for both string and integer ID formats.
"""

from typing import Dict, Optional, Union
from .SimulationEngine import db

def get(id: Union[int, str]) -> Optional[Dict]:
    """Retrieves the details of an existing field using its internal identifier.
    
    Args:
        id (Union[int, str]): The internal identifier of the field to retrieve.

    Returns:
        Optional[Dict]: The field object containing all its properties or None if the field does not exist. Contains any of the following fields:
            - type (str): Field type
            - id (str): Field identifier string
            - group (str): Field group identifier string
            - name (str): Field name (max 255 characters)
            - attributes (dict): Field attributes containing:
                - name (str): Field name (max 255 characters)
                - target_object (str): Field object type string, one of:
                    - "PROJECT"
                    - "RFP"
                    - "SUPPLIER_COMPANY"
                - data_type (str): OpenAPI data type, one of:
                    - "string"
                    - "number"
                    - "integer"
                    - "boolean"
                    - "array"
                    - "object"
                - type_description (str): Internal name and meaning of each field, one of:
                    - "Checkbox"
                    - "File"
                    - "Short Text"
                    - "Paragraph"
                    - "Date"
                    - "Integer"
                    - "Currency"
                    - "Decimal"
                    - "Single Select"
                    - "Multiple Select"
                    - "URL"
                    - "Lookup"
                    - "Related"
                - position (int): Field order position on the UI
                - required (bool): Identifies whether the field is required
            - relationships (dict): Field relationship containing:
                - group (dict): Reference to the field group where the field belongs to
                    - data (dict): Field group data containing:
                        - type (str): Object type, should always be "field_groups"
                        - id (int): Field group identifier string
            - links (dict): List of related links containing:
                - self (str): Normalized link to the resource
            
    """
    if str(id) in db.DB["fields"]["fields"]:
        return db.DB["fields"]["fields"][str(id)]
    
    try:
        if int(id) in db.DB["fields"]["fields"]:
            return db.DB["fields"]["fields"][int(id)]
        else:
            return None
    except KeyError:
        return None

def patch(id: Union[int, str], options: Dict) -> Optional[Dict]:
    """Updates the details of an existing field using its internal identifier.

    Please note, that request body must include an id attribute with the value of your field unique identifier,the same one you passed as argument.

    Args:
        id (Union[int, str]): The internal identifier of the field to update.
        options (Dict): A dictionary containing the field properties to update.
                        Must include an 'id' field matching the path parameter.
            Contains any of the following fields:
                - type (str): Field type
                - group (str): Field group identifier string
                - name (str): Field name (max 255 characters)
                - attributes (dict): Field attributes containing:
                    - name (str): Field name (max 255 characters)
                    - target_object (str): Field object type, one of:
                        - "PROJECT"
                        - "RFP"
                        - "SUPPLIER_COMPANY"
                    - type_description (str): Internal name and meaning of each field, one of:
                        - "Checkbox"
                        - "File"
                        - "Short Text"
                        - "Paragraph"
                        - "Date"
                        - "Integer"
                        - "Currency"
                        - "Decimal"
                        - "Single Select"
                        - "Multiple Select"
                        - "URL"
                        - "Lookup"
                        - "Related"
                    - required (bool): Identifies whether the field is required
                - relationships (dict): Field relationship containing:
                    - group (dict): Reference to the field group where the field belongs to
                        Note: Must be null for fields with target_object set to RFP, and required for all other fields
    Returns:
        Optional[Dict]: The updated field object or None if the field does not exist. Contains any of the following fields:
            - type (str): Field type
            - id (str): Field identifier string
            - group (str): Field group identifier string
            - name (str): Field name (max 255 characters)
            - attributes (dict): Field attributes containing:
                - name (str): Field name (max 255 characters)
                - target_object (str): Field object type string, one of:
                    - "PROJECT"
                    - "RFP"
                    - "SUPPLIER_COMPANY"
                - data_type (str): OpenAPI data type, one of:
                    - "string"
                    - "number"
                    - "integer"
                    - "boolean"
                    - "array"
                    - "object"
                - type_description (str): Internal name and meaning of each field, one of:
                    - "Checkbox"
                    - "File"
                    - "Short Text"
                    - "Paragraph"
                    - "Date"
                    - "Integer"
                    - "Currency"
                    - "Decimal"
                    - "Single Select"
                    - "Multiple Select"
                    - "URL"
                    - "Lookup"
                    - "Related"
                - position (int): Field order position on the UI
                - required (bool): Identifies whether the field is required
            - relationships (dict): Field relationship containing:
                - group (dict): Reference to the field group where the field belongs to
                    - data (dict): Field group data containing:
                        - type (str): Object type, should always be "field_groups"
                        - id (int): Field group identifier string
            - links (dict): List of related links containing:
                - self (str): Normalized link to the resource
    """
    if str(id) in db.DB["fields"]["fields"]:
        db.DB["fields"]["fields"][id] = options
        return options
    try:
        if int(id) in db.DB["fields"]["fields"]:
            db.DB["fields"]["fields"][int(id)] = options
            return options
        else:
            return None
    except KeyError:
        return None

def delete(id: Union[int, str]) -> bool:
    """Deletes a field using its internal identifier.

    Args:
        id (Union[int, str]): The internal identifier of the field to delete.
    
    Returns:
        bool: True if the field was successfully deleted, False if the field does not exist.

    """
    if str(id) in db.DB["fields"]["fields"]:
        del db.DB["fields"]["fields"][str(id)]
        return True
    try:
        if int(id) in db.DB["fields"]["fields"]:
            del db.DB["fields"]["fields"][int(id)]
            return True
        else:
            return False
    except KeyError:
        return False