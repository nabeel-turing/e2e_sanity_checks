"""
This module provides functionality for retrieving field options associated with
specific fields in the Workday Strategic Sourcing system. It enables users to
access all options configured for a particular field, supporting comprehensive
field option management and configuration capabilities.
"""

from typing import Dict, List, Union
from .SimulationEngine import db

def get(field_id: str) -> List[Dict]:
    """Returns a list of field options for the specified field.

    Args:
        field_id (str): The unique identifier of the field for which
            to retrieve options.

    Returns:
        List[Dict]: A list of dictionaries, where each dictionary represents a
            field option containing any of the following fields:
            - type (str): Object type, should always be "fields"
            - field_id (str): Field identifier string
            - options (List): List of options configured for the field
            - attributes (dict): Field attributes containing:
                - label (str): Field name (max 255 characters)
                - position (int): Field order position on the UI
    """
    field_options_list = []
    for option_id, option in db.DB["fields"]["field_options"].items():
        if option.get("field_id") == field_id:
            field_options_list.append(option)
    return field_options_list 