# APIs/jira/SettingsApi.py
from typing import Dict, Any

def get_settings() -> Dict[str, Any]:
    """
    Get all settings.

    This method returns all settings in the system.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - settings (Dict[str, Any]): A dictionary containing all settings
                - exampleSetting (bool): An example setting, currently hardcoded to True
    """
    return {"settings": {"exampleSetting": True}}
