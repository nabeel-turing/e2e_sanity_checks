# APIs/jira/ApplicationPropertiesApi.py
from .SimulationEngine.db import DB
from .SimulationEngine.utils import _check_empty_field
from typing import Optional, Dict, Any


def get_application_properties(
    key: Optional[str] = None,
    permissionLevel: Optional[str] = None,
    keyFilter: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve application properties from Jira.

    This method allows fetching either all application properties or a specific property
    by its key. Application properties are system-wide settings that control various
    aspects of Jira's behavior.

    Args:
        key (Optional[str]): The key of the specific property to retrieve. If not provided,
            all application properties will be returned.
        permissionLevel (Optional[str]): The permission level required to access the property.
            If not provided, all properties will be returned.
        keyFilter (Optional[str]): A filter to apply to the property keys. If not provided,
            all properties will be returned.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - If key is provided:
                - key (str): The property key
                - value (str): The property value
                    - id (str): The property id
                    - key (str): The property key
                    - value (str): The property value
                    - name (str): The property name
                    - type (str): The property type
                    - defaultValue (str): The default value of the property

            - If key is not provided:
                - properties (Dict[str, Any]): All application properties
                    - id (str): The property id
                    - key (str): The property key
                    - value (str): The property value
                    - name (str): The property name
                    - type (str): The property type
                    - defaultValue (str): The default value of the property

    Raises:
        ValueError: If the specified key does not exist in the application properties
    """
    if key:
        if key not in DB["application_properties"]:
            return {"error": f"Property '{key}' not found."}
        return {"key": key, "value": DB["application_properties"][key]}
    return {"properties": DB["application_properties"]}


def update_application_property(id: str, value: str) -> dict:
    """
    Update an application property in Jira.

    This method allows modifying the value of an existing application property
    or creating a new one if it doesn't exist.

    Args:
        id (str): The identifier of the property to update
        value (str): The new value to set for the property

    Returns:
        dict: A dictionary containing:
            - updated (bool): True if the property was successfully updated
            - property (str): The ID of the updated property
            - newValue (str): The new value that was set

    Raises:
        ValueError: If either id or value is empty or invalid
    """
    err = _check_empty_field("id", id) + _check_empty_field("value", value)
    if err:
        return {"error": err}
    DB["application_properties"][id] = value
    return {"updated": True, "property": id, "newValue": value}
