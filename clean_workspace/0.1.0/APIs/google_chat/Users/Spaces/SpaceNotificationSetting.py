from common_utils.print_log import print_log
# APIs/google_chat/Users/Spaces/SpaceNotificationSetting.py

import sys
from typing import Dict, Any

sys.path.append("APIs")

from google_chat.SimulationEngine.db import DB


def get(name: str) -> Dict[str, Any]:
    """
    Retrieves the space notification setting for a user.

    Args:
        name (str): Required. Resource name of the space notification setting to retrieve.
            Only supports the calling user's identifier.
            Format:
            - users/me/spaces/{space}/spaceNotificationSetting
            - users/user@example.com/spaces/{space}/spaceNotificationSetting
            - users/123456789/spaces/{space}/spaceNotificationSetting

    Returns:
        Dict[str, Any]: A dictionary containing the space notification setting with the following keys:
            - 'name' (str): Resource name of the space notification setting.
            - 'notificationSetting' (str): The notification level. One of:
                - 'NOTIFICATION_SETTING_UNSPECIFIED'
                - 'ALL'
                - 'MAIN_CONVERSATIONS'
                - 'FOR_YOU'
                - 'OFF'
            - 'muteSetting' (str): The mute configuration. One of:
                - 'MUTE_SETTING_UNSPECIFIED'
                - 'UNMUTED'
                - 'MUTED'

        Returns an empty dictionary if no matching setting is found.
    """
    print_log(f"SpaceNotificationSetting.get called with name={name}")
    for setting in DB["SpaceNotificationSetting"]:
        if setting.get("name") == name:
            return setting
    print_log("SpaceNotificationSetting not found.")
    return {}


def patch(name: str, updateMask: str, requestBody: Dict[str, Any]) -> Dict[str, Any]:
    """
    Updates the space notification setting for a user.

    Args:
        name (str): Required. Resource name of the space notification setting to update.
            Format: users/{user}/spaces/{space}/spaceNotificationSetting
        updateMask (str): Required. Comma-separated list of fields to update.
            Supported fields:
            - "notification_setting"
            - "mute_setting"
        requestBody (Dict[str, Any]): A dictionary representing the SpaceNotificationSetting resource with the following keys:
            - 'name' (str): Resource name of the space notification setting.
            - 'notification_setting' (str): New notification level. One of:
                - 'NOTIFICATION_SETTING_UNSPECIFIED'
                - 'ALL'
                - 'MAIN_CONVERSATIONS'
                - 'FOR_YOU'
                - 'OFF'
            - 'mute_setting' (str): New mute setting. One of:
                - 'MUTE_SETTING_UNSPECIFIED'
                - 'UNMUTED'
                - 'MUTED'

    Returns:
        Dict[str, Any]: A dictionary representing the updated space notification setting with the following keys:
            - 'name' (str): Resource name of the space notification setting.
            - 'notification_setting' (str): The updated notification level.
            - 'mute_setting' (str): The updated mute setting.

        Returns an empty dictionary if no matching resource is found.
    """
    print_log(
        f"SpaceNotificationSetting.patch called with name={name}, updateMask={updateMask}, requestBody={requestBody}"
    )
    target = None
    for setting in DB["SpaceNotificationSetting"]:
        if setting.get("name") == name:
            target = setting
            break
    if not target:
        print_log("SpaceNotificationSetting not found.")
        return {}

    masks = [m.strip() for m in updateMask.split(",")]
    if "notification_setting" in masks or "*" in masks:
        if "notification_setting" in requestBody:
            target["notification_setting"] = requestBody["notification_setting"]
    if "mute_setting" in masks or "*" in masks:
        if "mute_setting" in requestBody:
            target["mute_setting"] = requestBody["mute_setting"]

    return target
