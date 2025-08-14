"""
This module provides functionality for managing field options in the Workday
Strategic Sourcing system. It supports creating new field options with specified
parameters and associating them with specific fields. The module enables
comprehensive field option management and configuration capabilities.
"""

from typing import Dict, List, Optional, Union
import uuid
from .SimulationEngine import db

def post(new_id: str = None, options: List = None) -> Optional[Dict]:
    """Creates a new field option with given parameters..

    Args:
        new_id (str): The field ID to associate the options with. If not provided, the field ID will be generated.
        options (List): A list of options to be associated with the field. 
        
    Returns:
        Optional[Dict]: The created field option data if successful, including:
            - field_id (str): The provided field ID
            - options (List): The provided list of options
    """
    if not new_id:
        new_id = str(uuid.uuid4())
    if new_id not in db.DB["fields"]["field_options"]:
        new_field_option = {"field_id": new_id, "options": options}
        db.DB["fields"]["field_options"][new_id] = new_field_option
        return new_field_option
    else:
        return None 