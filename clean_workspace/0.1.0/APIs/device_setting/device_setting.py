"""
Device Setting API

A tool that can be used to open, get, and modify settings on the user's current smart device.
"""

from typing import Optional, Dict, Any
import json

from device_setting.SimulationEngine.utils import (
    get_setting, set_setting, 
    get_insight, get_all_insights
)
from device_setting.SimulationEngine.enums import (
    DeviceSettingType,
    GetableDeviceSettingType,
    ToggleableDeviceSettingType,
    VolumeSettingType,
    DeviceStateType,
    ActionType,
    ToggleState,
    VolumeDefaults,
    Constants,
)
from device_setting.SimulationEngine.models import (
    SettingInfo,
    ActionSummary,
    Action,
    volume_mapping,
)
from device_setting.SimulationEngine.utils import generate_card_id, create_action_card


def open(setting_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Navigates to the settings page for a given setting type.
    
    Args:
        setting_type (Optional[str]): Setting to open. Can be a DeviceSettingType enum value as string.
                      Use "UNSPECIFIED" if the user only mentions "settings."
                      If None or UNSPECIFIED, open general device settings page.
                      Valid values include: "UNSPECIFIED", "ACCESSIBILITY", "ACCOUNT", "AIRPLANE_MODE", 
                      "ALARM_VOLUME", "APPLICATION", "APP_DATA_USAGE", "AUTO_ROTATE", "BARD", "BATTERY", 
                      "BATTERY_SAVER", "BIOMETRIC", "BLUETOOTH", "BLUETOOTH_PAIRING", "BRIGHTNESS", 
                      "CALL_VOLUME", "CAST", "DARK_THEME", "DATA_SAVER", "DATE_TIME", "DEVELOPER_OPTION", 
                      "DEVICE_INFO", "DISPLAY", "DO_NOT_DISTURB", "GEMINI", "GOOGLE_ASSISTANT", "HOT_SPOT", 
                      "INTERNAL_STORAGE", "LANGUAGE", "LOCATION", "LOCK_SCREEN", "MEDIA_VOLUME", "NETWORK", 
                      "NFC", "NIGHT_MODE", "NOTIFICATION_VOLUME", "RING_VOLUME", "TALK_BACK", "VOLUME", 
                      "VIBRATION", "WIFI"
    
    Returns:
        Dict[str, Any]: Action summary containing:
            - result (str): Result message of the action
            - card_id (str): Card identifier for UI components
            - action_card_content_passthrough (str): Action card content for UI display
                The action_card_content_passthrough is a JSON string with the following keys:
                    - action (str): The action type, always "open_settings"
                    - timestamp (str): ISO timestamp when the card was generated
                    - setting_type (str): The setting type that was opened, or "UNSPECIFIED" if None
                    - message (str): The same as the 'result' field, describing what was opened
        
    Raises:
        ValueError: If setting_type string is not a valid DeviceSettingType
        
    Example:
        >>> open()  # Opens general settings
        >>> open("WIFI")  # Opens WiFi settings
        >>> open("UNSPECIFIED")  # Opens general settings
    """
    # Convert string to enum if needed
    setting_enum = None
    if isinstance(setting_type, str):
        try:
            setting_enum = DeviceSettingType(setting_type.upper())
        except ValueError:
            raise ValueError(f"Invalid setting_type: '{setting_type}'. Must be one of: {[e.value for e in DeviceSettingType]}")
    
    if setting_type is None or setting_enum == DeviceSettingType.UNSPECIFIED:
        result = "Opened general device settings page."
    else:
        result = f"Opened {setting_enum.value.lower().replace('_', ' ')} settings page."
    
    action_summary = ActionSummary(
        result=result,
        card_id=generate_card_id(),
        action_card_content_passthrough=create_action_card(
            ActionType.OPEN_SETTINGS,
            setting_type=setting_enum.value if setting_enum else Constants.UNSPECIFIED.value,
            message=result
        )
    )
    
    return action_summary.model_dump()


def get(setting_type: str) -> Dict[str, Any]:
    """
    Gets the current value of a device setting.
    
    Args:
        setting_type (str): Setting to get the value of. Must be one of the getable device settings.
                      Valid values include: "AIRPLANE_MODE", "ALARM_VOLUME", "AUTO_ROTATE", "BATTERY", 
                      "BATTERY_SAVER", "BLUETOOTH", "CALL_VOLUME", "DO_NOT_DISTURB", "FLASHLIGHT", 
                      "HOT_SPOT", "MEDIA_VOLUME", "NETWORK", "NFC", "NIGHT_MODE", "NOTIFICATION_VOLUME", 
                      "RING_VOLUME", "TALK_BACK", "VOLUME", "VIBRATION", "WIFI"
    
    Returns:
        Dict[str, Any]: Setting information containing:
            - setting_type (str): The type of the setting
            - percentage_value (Optional[int]): Current percentage value between 0-100 (if applicable)
            - on_or_off (Optional[str]): Current toggle state "on" or "off" (if applicable)
            - card_id (str): Card identifier for UI components
            - action_card_content_passthrough (str): Action card content for UI display
                The action_card_content_passthrough is a JSON string with the following keys:
                    - action (str): The action type, always "get_setting"
                    - timestamp (str): ISO timestamp when the card was generated
                    - setting_type (str): The setting type that was retrieved
                    - message (str): Description of the setting retrieval action
        
    Raises:
        ValueError: If setting_type is None, empty, or not a valid getable setting
        
    Example:
        >>> get("WIFI")  # Get WiFi status
        >>> get("BATTERY")  # Get battery level
        >>> get("MEDIA_VOLUME")  # Get media volume
    """
    # Validate input
    if setting_type is None:
        raise ValueError("setting_type is required")
    
    if not isinstance(setting_type, str) or not setting_type.strip():
        raise ValueError("setting_type is required")
    
    # Convert string to enum for validation
    try:
        setting_enum = GetableDeviceSettingType(setting_type.upper())
    except ValueError:
        raise ValueError(f"Invalid setting_type: '{setting_type}'. Must be one of: {[e.value for e in GetableDeviceSettingType]}")
    
    setting_info = SettingInfo(
        setting_type=setting_enum.value,
        card_id=generate_card_id(),
        action_card_content_passthrough=create_action_card(
            ActionType.GET_SETTING,
            setting_type=setting_enum.value,
            message=f"Retrieved {setting_enum.value.lower().replace('_', ' ')} setting"
        )
    )
    
    setting = get_setting(setting_enum.value)
    if setting:
        if setting_enum == GetableDeviceSettingType.BATTERY:
            if Constants.PERCENTAGE_VALUE.value in setting:
                setting_info.percentage_value = setting[Constants.PERCENTAGE_VALUE.value]
            elif Constants.PERCENTAGE.value in setting:
                setting_info.percentage_value = setting[Constants.PERCENTAGE.value]
        elif Constants.PERCENTAGE_VALUE.value in setting:
            setting_info.percentage_value = setting[Constants.PERCENTAGE_VALUE.value]
        if Constants.ON_OR_OFF.value in setting:
            setting_info.on_or_off = str(setting[Constants.ON_OR_OFF.value]).lower()
    
    return setting_info.model_dump()


def on(setting: str) -> Dict[str, Any]:
    """
    Turns on a device setting.
    
    Args:
        setting (str): Setting to turn on. Must be one of the toggleable device settings.
                      Valid values include: "AIRPLANE_MODE", "AUTO_ROTATE", "BATTERY_SAVER", 
                      "BLUETOOTH", "DO_NOT_DISTURB", "FLASHLIGHT", "HOT_SPOT", "NETWORK", 
                      "NFC", "NIGHT_MODE", "TALK_BACK", "VIBRATION", "WIFI"
    
    Returns:
        Dict[str, Any]: Action summary containing:
            - result (str): Result message of the action
            - card_id (str): Card identifier for UI components
            - action_card_content_passthrough (str): Action card content for UI display
                The action_card_content_passthrough is a JSON string with the following keys:
                    - action (str): The action type, always "toggle_setting"
                    - timestamp (str): ISO timestamp when the card was generated
                    - setting (str): The setting type that was turned on
                    - state (str): The new state, always "on"
                    - message (str): The same as the 'result' field, describing what was turned on
        
    Raises:
        ValueError: If setting is not a valid toggleable setting
        
    Example:
        >>> on("WIFI")  # Turn on WiFi
        >>> on("BLUETOOTH")  # Turn on Bluetooth
        >>> on("AIRPLANE_MODE")  # Turn on airplane mode
    """
    # Convert string to enum for validation
    try:
        setting_enum = ToggleableDeviceSettingType(setting.upper())
    except ValueError:
        valid_settings = [s.value for s in ToggleableDeviceSettingType]
        raise ValueError(f"Invalid setting: '{setting}'. Must be one of: {', '.join(valid_settings)}")
    
    set_setting(setting_enum.value, {Constants.ON_OR_OFF.value: ToggleState.ON.value})
    result = f"Turned on {setting_enum.value.lower().replace('_', ' ')}."
    action_summary = ActionSummary(
        result=result,
        card_id=generate_card_id(),
        action_card_content_passthrough=create_action_card(
            ActionType.TOGGLE_SETTING,
            setting=setting_enum.value,
            state=ToggleState.ON.value,
            message=result
        )
    )
    
    
    return action_summary.model_dump()


def off(setting: str) -> Dict[str, Any]:
    """
    Turns off a device setting.
    
    Args:
        setting (str): Setting to turn off. Must be one of the toggleable device settings.
                      Valid values include: "AIRPLANE_MODE", "AUTO_ROTATE", "BATTERY_SAVER", 
                      "BLUETOOTH", "DO_NOT_DISTURB", "FLASHLIGHT", "HOT_SPOT", "NETWORK", 
                      "NFC", "NIGHT_MODE", "TALK_BACK", "VIBRATION", "WIFI"
    
    Returns:
        Dict[str, Any]: Action summary containing:
            - result (str): Result message of the action
            - card_id (str): Card identifier for UI components
            - action_card_content_passthrough (str): Action card content for UI display
                The action_card_content_passthrough is a JSON string with the following keys:
                    - action (str): The action type, always "toggle_setting"
                    - timestamp (str): ISO timestamp when the card was generated
                    - setting (str): The setting type that was turned off
                    - state (str): The new state, always "off"
                    - message (str): The same as the 'result' field, describing what was turned off
        
    Raises:
        ValueError: If setting is not a valid toggleable setting
        
    Example:
        >>> off("WIFI")  # Turn off WiFi
        >>> off("BLUETOOTH")  # Turn off Bluetooth
        >>> off("AIRPLANE_MODE")  # Turn off airplane mode
    """
    # Convert string to enum for validation
    try:
        setting_enum = ToggleableDeviceSettingType(setting.upper())
    except ValueError:
        valid_settings = [s.value for s in ToggleableDeviceSettingType]
        raise ValueError(f"Invalid setting: '{setting}'. Must be one of: {', '.join(valid_settings)}")
    
    set_setting(setting_enum.value, {Constants.ON_OR_OFF.value: ToggleState.OFF.value})
    result = f"Turned off {setting_enum.value.lower().replace('_', ' ')}."
    action_summary = ActionSummary(
        result=result,
        card_id=generate_card_id(),
        action_card_content_passthrough=create_action_card(
            ActionType.TOGGLE_SETTING,
            setting=setting_enum.value,
            state=ToggleState.OFF.value,
            message=result
        )
    )
    
    return action_summary.model_dump()


def mute(setting: Optional[str] = None) -> Dict[str, Any]:
    """
    Mutes the device volume.
    
    Args:
        setting (Optional[str]): The specific volume setting to mute. If None or "UNSPECIFIED", mutes all volume settings.
                                Valid options: "ALARM", "CALL", "MEDIA", "NOTIFICATION", "RING", "UNSPECIFIED"
    
    Returns:
        Dict[str, Any]: Action summary containing:
            - result (str): Result message of the action
            - card_id (str): Card identifier for UI components
            - action_card_content_passthrough (str): Action card content for UI display
                The action_card_content_passthrough is a JSON string with the following keys:
                    - action (str): The action type, always "mute_volume"
                    - timestamp (str): ISO timestamp when the card was generated
                    - setting (str): The volume setting that was muted, or "UNSPECIFIED" if all volumes
                    - message (str): The same as the 'result' field, describing what was muted
        
    Raises:
        ValueError: If setting is not a valid volume setting
        
    Example:
        >>> mute()  # Mute all volume settings
        >>> mute("MEDIA")  # Mute only media volume
        >>> mute("ALARM")  # Mute only alarm volume
        >>> mute("UNSPECIFIED")  # Mute all volume settings
    """
    # Convert string to enum for validation if provided
    setting_enum = None
    if setting is not None:
        try:
            setting_enum = VolumeSettingType(setting.upper())
        except ValueError:
            raise ValueError(f"Invalid setting: '{setting}'. Must be one of: {[e.value for e in VolumeSettingType]}")
    
    if setting is None or setting == Constants.UNSPECIFIED.value or setting_enum == VolumeSettingType.UNSPECIFIED:
        for vol_setting in volume_mapping.get_all_volume_keys():
            set_setting(vol_setting, {Constants.PERCENTAGE_VALUE.value: 0})
        result = "Muted all device volume."
    else:
        key = volume_mapping.get_database_key(setting_enum)
        if key:
            set_setting(key, {Constants.PERCENTAGE_VALUE.value: 0})
            result = f"Muted {setting_enum.value.lower()} volume."
        else:
            result = "Muted device volume."
    
    action_summary = ActionSummary(
        result=result,
        card_id=generate_card_id(),
        action_card_content_passthrough=create_action_card(
            ActionType.MUTE_VOLUME,
            setting=setting_enum.value if setting_enum else Constants.UNSPECIFIED.value,
            message=result
        )
    )
    
    
    return action_summary.model_dump()


def unmute(setting: Optional[str] = None) -> Dict[str, Any]:
    """
    Unmutes the device volume by setting to default levels.
    
    Args:
        setting (Optional[str]): The specific volume setting to unmute. If None or "UNSPECIFIED", unmutes all volume settings.
                                Valid options: "ALARM", "CALL", "MEDIA", "NOTIFICATION", "RING", "UNSPECIFIED"
                                Default levels: ALARM_VOLUME=50, CALL_VOLUME=70, MEDIA_VOLUME=60, 
                                               NOTIFICATION_VOLUME=40, RING_VOLUME=80, VOLUME=65
    
    Returns:
        Dict[str, Any]: Action summary containing:
            - result (str): Result message of the action
            - card_id (str): Card identifier for UI components
            - action_card_content_passthrough (str): Action card content for UI display
                The action_card_content_passthrough is a JSON string with the following keys:
                    - action (str): The action type, always "unmute_volume"
                    - timestamp (str): ISO timestamp when the card was generated
                    - setting (str): The volume setting that was unmuted, or "UNSPECIFIED" if all volumes
                    - message (str): The same as the 'result' field, describing what was unmuted
        
    Raises:
        ValueError: If setting is not a valid volume setting
        
    Example:
        >>> unmute()  # Unmute all volume settings to defaults
        >>> unmute("MEDIA")  # Unmute media volume to 60%
        >>> unmute("ALARM")  # Unmute alarm volume to 50%
        >>> unmute("UNSPECIFIED")  # Unmute all volume settings to defaults
    """
    defaults = {
        volume_mapping.ALARM: VolumeDefaults.ALARM_VOLUME.value,
        volume_mapping.CALL: VolumeDefaults.CALL_VOLUME.value,
        volume_mapping.MEDIA: VolumeDefaults.MEDIA_VOLUME.value,
        volume_mapping.NOTIFICATION: VolumeDefaults.NOTIFICATION_VOLUME.value,
        volume_mapping.RING: VolumeDefaults.RING_VOLUME.value,
        'VOLUME': VolumeDefaults.VOLUME.value
    }
    
    # Convert string to enum for validation if provided
    setting_enum = None
    if setting is not None:
        try:
            setting_enum = VolumeSettingType(setting.upper())
        except ValueError:
            raise ValueError(f"Invalid setting: '{setting}'. Must be one of: {[e.value for e in VolumeSettingType]}")
    
    if setting is None or setting == Constants.UNSPECIFIED.value or setting_enum == VolumeSettingType.UNSPECIFIED:
        for vol_setting, val in defaults.items():
            set_setting(vol_setting, {Constants.PERCENTAGE_VALUE.value: val})
        result = "Unmuted all device volume."
    else:
        key = volume_mapping.get_database_key(setting_enum)
        if key and key in defaults:
            set_setting(key, {Constants.PERCENTAGE_VALUE.value: defaults[key]})
            result = f"Unmuted {setting_enum.value.lower()} volume."
        else:
            result = "Unmuted device volume."
    
    action_summary = ActionSummary(
        result=result,
        card_id=generate_card_id(),
        action_card_content_passthrough=create_action_card(
            ActionType.UNMUTE_VOLUME,
            setting=setting_enum.value if setting_enum else Constants.UNSPECIFIED.value,
            message=result
        )
    )
    
    
    return action_summary.model_dump()


def adjust_volume(by: int, setting: Optional[str] = None) -> Dict[str, Any]:
    """
    Adjusts the volume by a certain percentage.
    
    Args:
        by (int): The amount to adjust the volume by, in percentage points. Can be positive or negative.
                 Values are clamped between 0 and 100 after adjustment.
        setting (Optional[str]): The specific volume setting to adjust. If None or "UNSPECIFIED", adjusts all volume settings.
                                Valid options: "ALARM", "CALL", "MEDIA", "NOTIFICATION", "RING", "UNSPECIFIED"
    
    Returns:
        Dict[str, Any]: Action summary containing:
            - result (str): Result message of the action
            - card_id (str): Card identifier for UI components
            - action_card_content_passthrough (str): Action card content for UI display
                The action_card_content_passthrough is a JSON string with the following keys:
                    - action (str): The action type, always "adjust_volume"
                    - timestamp (str): ISO timestamp when the card was generated
                    - setting (str): The volume setting that was adjusted, or "UNSPECIFIED" if all volumes
                    - adjustment (int): The percentage amount the volume was adjusted by
                    - message (str): The same as the 'result' field, describing the adjustment
        
    Raises:
        ValueError: If setting is not a valid volume setting
        
    Example:
        >>> adjust_volume(10)  # Increase all volumes by 10%
        >>> adjust_volume(-5)  # Decrease all volumes by 5%
        >>> adjust_volume(15, "MEDIA")  # Increase media volume by 15%
        >>> adjust_volume(-10, "RING")  # Decrease ring volume by 10%
    """
    # Convert string to enum for validation if provided
    setting_enum = None
    if setting is not None:
        try:
            setting_enum = VolumeSettingType(setting.upper())
        except ValueError:
            raise ValueError(f"Invalid setting: '{setting}'. Must be one of: {[e.value for e in VolumeSettingType]}")
    
    if setting is None or setting == Constants.UNSPECIFIED.value or setting_enum == VolumeSettingType.UNSPECIFIED:
        for vol_setting in volume_mapping.get_all_volume_keys():
            current = get_setting(vol_setting)
            cur_val = current.get(Constants.PERCENTAGE_VALUE.value, VolumeDefaults.VOLUME.value) if current else VolumeDefaults.VOLUME.value
            new_val = max(0, min(100, cur_val + by))
            set_setting(vol_setting, {Constants.PERCENTAGE_VALUE.value: new_val})
        result = f"Adjusted all volume settings by {by}%."
    else:
        key = volume_mapping.get_database_key(setting_enum)
        if key:
            current = get_setting(key)
            cur_val = current.get(Constants.PERCENTAGE_VALUE.value, VolumeDefaults.VOLUME.value) if current else VolumeDefaults.VOLUME.value
            new_val = max(0, min(100, cur_val + by))
            set_setting(key, {Constants.PERCENTAGE_VALUE.value: new_val})
            result = f"Adjusted {setting_enum.value.lower()} volume by {by}%."
        else:
            result = f"Adjusted volume by {by}%."
    
    action_summary = ActionSummary(
        result=result,
        card_id=generate_card_id(),
        action_card_content_passthrough=create_action_card(
            ActionType.ADJUST_VOLUME,
            setting=setting_enum.value if setting_enum else Constants.UNSPECIFIED.value,
            adjustment=by,
            message=result
        )
    )
    
    return action_summary.model_dump()


def set_volume(to: int, setting: Optional[str] = None) -> Dict[str, Any]:
    """
    Sets the volume to a specific percentage.
    
    Args:
        to (int): The volume level to set to, in percentage points. Must be between 0 and 100.
        setting (Optional[str]): The specific volume setting to set. If None or "UNSPECIFIED", sets all volume settings.
                                Valid options: "ALARM", "CALL", "MEDIA", "NOTIFICATION", "RING", "UNSPECIFIED"
    
    Returns:
        Dict[str, Any]: Action summary containing:
            - result (str): Result message of the action
            - card_id (str): Card identifier for UI components
            - action_card_content_passthrough (str): Action card content for UI display
                The action_card_content_passthrough is a JSON string with the following keys:
                    - action (str): The action type, always "set_volume"
                    - timestamp (str): ISO timestamp when the card was generated
                    - setting (str): The volume setting that was set, or "UNSPECIFIED" if all volumes
                    - volume (int): The volume level that was set (0-100)
                    - message (str): The same as the 'result' field, describing what was set
        
    Raises:
        ValueError: If volume value is less than 0 or greater than 100, or if setting is not a valid volume setting
        
    Example:
        >>> set_volume(50)  # Set all volumes to 50%
        >>> set_volume(75, "MEDIA")  # Set media volume to 75%
        >>> set_volume(0, "ALARM")  # Set alarm volume to 0%
        >>> set_volume(100, "RING")  # Set ring volume to 100%
    """
    if to < 0 or to > 100:
        raise ValueError("Volume must be between 0 and 100")
    
    # Convert string to enum for validation if provided
    setting_enum = None
    if setting is not None:
        try:
            setting_enum = VolumeSettingType(setting.upper())
        except ValueError:
            raise ValueError(f"Invalid setting: '{setting}'. Must be one of:")
    
    if setting is None or setting == Constants.UNSPECIFIED.value or setting_enum == VolumeSettingType.UNSPECIFIED:
        for vol_setting in volume_mapping.get_all_volume_keys():
            set_setting(vol_setting, {Constants.PERCENTAGE_VALUE.value: to})
        result = f"Set all volume settings to {to}%."
    else:
        key = volume_mapping.get_database_key(setting_enum)
        if key:
            set_setting(key, {Constants.PERCENTAGE_VALUE.value: to})
            result = f"Set {setting_enum.value.lower()} volume to {to}%."
        else:
            result = f"Set volume to {to}%."
    
    action_summary = ActionSummary(
        result=result,
        card_id=generate_card_id(),
        action_card_content_passthrough=create_action_card(
            ActionType.SET_VOLUME,
            setting=setting_enum.value if setting_enum else Constants.UNSPECIFIED.value,
            volume=to,
            message=result
        )
    )
    
    
    return action_summary.model_dump()


def get_device_insights(device_state_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Generates device insights based on user's current device state.
    
    Args:
        device_state_type (Optional[str]): The type of device state to get insights for. If None or "UNCATEGORIZED",
                                          returns general device insights. Valid options: "UNCATEGORIZED", "BATTERY", "STORAGE"
    
    Returns:
        Dict[str, Any]: Action summary containing:
            - result (str): Result message of the action
            - card_id (str): Card identifier for UI components
            - action_card_content_passthrough (str): Action card content for UI display
                The action_card_content_passthrough is a JSON string with the following keys:
                    - action (str): The action type, always "get_device_insights"
                    - timestamp (str): ISO timestamp when the card was generated
                    - setting_type (str): Always "UNSPECIFIED" (for UI compatibility)
                    - insights (List[str]): List of insight strings for the requested device state
                    - message (str): The same as the 'result' field, a summary of the insights
    
    Raises:
        ValueError: If device_state_type is not a valid device state type
    
    Example:
        >>> get_device_insights()  # Get general device insights
        >>> get_device_insights("BATTERY")  # Get battery-specific insights
        >>> get_device_insights("STORAGE")  # Get storage-specific insights
        >>> get_device_insights("UNCATEGORIZED")  # Get general device insights
    """
    insights = []
    all_insights = get_all_insights()

    valid_types = [e.value for e in DeviceStateType]
    # Explicitly check for empty, whitespace-only, or invalid string
    if isinstance(device_state_type, str):
        if device_state_type.strip() == "" or device_state_type not in valid_types:
            raise ValueError(f"Invalid device_state_type: '{device_state_type}'. Must be one of: {valid_types}")

    # Convert string to enum for validation if provided (case-sensitive)
    device_state_enum = None
    if device_state_type is not None:
        device_state_enum = DeviceStateType(device_state_type)

    if device_state_type is None or device_state_type == Constants.UNCATEGORIZED.value or device_state_enum == DeviceStateType.UNCATEGORIZED:
        uncategorized = get_insight(Constants.UNCATEGORIZED.value)
        if uncategorized:
            for k, v in uncategorized.items():
                if k != Constants.LAST_UPDATED.value:
                    insights.append(f"{k.replace('_', ' ').capitalize()}: {v}")

    elif device_state_enum == DeviceStateType.BATTERY:
        battery = get_insight(Constants.BATTERY.value)
        if battery:
            for k, v in battery.items():
                if k != Constants.LAST_UPDATED.value:
                    insights.append(f"{k.replace('_', ' ').capitalize()}: {v}")

    elif device_state_enum == DeviceStateType.STORAGE:
        storage = get_insight(Constants.STORAGE.value)
        if storage:
            for k, v in storage.items():
                if k != Constants.LAST_UPDATED.value:
                    if isinstance(v, dict):
                        insights.append(f"{k.replace('_', ' ').capitalize()}: {json.dumps(v)}")
                    else:
                        insights.append(f"{k.replace('_', ' ').capitalize()}: {v}")

    if not insights:
        insights.append("Device is operating normally.")

    result = " ".join(insights)
    action_summary = ActionSummary(
        result=result,
        card_id=generate_card_id(),
        action_card_content_passthrough=create_action_card(
            ActionType.GET_DEVICE_INSIGHTS,
            device_state_type=device_state_enum.value if device_state_enum else Constants.UNCATEGORIZED.value,
            insights=insights,
            message=result
        )
    )
    
    return action_summary.model_dump() 