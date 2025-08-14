"""
This module provides functionality for managing field groups in the Workday
Strategic Sourcing system. It supports retrieving a list of all field groups
and creating new field groups with specified parameters. The module enables
comprehensive field group management and configuration capabilities.
"""

from typing import Dict, List, Optional
from .SimulationEngine import db

def get() -> List[Dict]:
    """Returns a list of field groups.

    Returns:
        List[Dict]: A list of dictionaries, where each dictionary represents
            a field group containing any of the following fields:
                - type (str): Object type, should always be "field_groups"
                - id (str): Field group identifier string
                - fields (List): List of fields belonging to this group
                - name (str): Field group name (max 255 characters)
                - description (str): Field group description (max 255 characters)
                - attributes (dict): Field group attributes containing:
                    - target_object (str): Field group object type string, one of:
                        - "PROJECT"
                        - "SUPPLIER_COMPANY"
                        - "RFP"
                    - name (str): Field group name (max 255 characters)
                    - position (int): Field group position on the UI
    """
    return list(db.DB["fields"]["field_groups"].values())

def post(name: str, description: str = "", data: Dict = {}) -> Dict:
    """Creates a new field group with the specified parameters.

    Args:
        name (str): The name of the field group to be created.
        description (str, optional): A detailed description of the field group.
            Defaults to an empty string.
        data (Dict, optional): A dictionary containing the field group configuration options. Can contain any of the following fields:
            - type (str): Object type, should always be "field_groups"
            - name (str): Field group name (max 255 characters)
            - fields (List): List of fields belonging to this group
            - attributes (dict): Field group attributes containing:
                - target_object (str): Field group object type string, one of:
                    - "PROJECT"
                    - "SUPPLIER_COMPANY"
                    - "RFP"
                - name (str): Field group name (max 255 characters)

    Returns:
        Dict: The created field group data, including:
            - type (str): Object type, should always be "field_groups"
            - id (str): Field group identifier string
            - fields (List): List of fields belonging to this group
            - name (str): Field group name (max 255 characters)
            - description (str): Field group description (max 255 characters)
            - attributes (dict): Field group attributes containing:
                - target_object (str): Field group object type string, one of:
                    - "PROJECT"
                    - "SUPPLIER_COMPANY"
                    - "RFP"
                - name (str): Field group name (max 255 characters)
                - position (int): Field group position on the UI
    """
    new_id = str(max(map(int, db.DB.get("fields", {}).get("field_groups", {}).keys()), default=0) + 1)
    new_field_group = {"id": new_id, "name": name, "description": description}
    db.DB["fields"]["field_groups"][new_id] = new_field_group
    return new_field_group