from typing import List
from device_actions.SimulationEngine.db import DB
from device_actions.SimulationEngine.utils import get_phone_state
from datetime import datetime
from device_actions.SimulationEngine.custom_errors import DevicePoweredOffError

def get_installed_apps() -> List[dict]:
    """
    Gets the list of installed application on the device.

    Returns:
        List[dict]: A list of dictionaries, where each dictionary
            has a "name" field with the application name.

    Raises:
        DevicePoweredOffError: If the device is powered off.
    """

    phone_state = get_phone_state()

    if not phone_state.is_on:
        raise DevicePoweredOffError("Device is powered off. This action cannot be performed.")

    app_names = [{"name": app.name} for app in phone_state.installed_apps]
    return app_names