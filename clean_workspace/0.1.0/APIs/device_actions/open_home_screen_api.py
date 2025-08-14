from device_actions.SimulationEngine.models import ActionSummary
from device_actions.SimulationEngine.db import DB
from device_actions.SimulationEngine.utils import get_phone_state, update_phone_state
from device_actions.SimulationEngine.custom_errors import DevicePoweredOffError
from datetime import datetime

def open_home_screen() -> dict:
    """
    Navigates to home screen on the device.

    Returns:
        dict: A dictionary containing the result of the action.
            - result (str): A message indicating the result of the action.
            - card_id (str): A unique identifier for the action card.

    Raises:
        DevicePoweredOffError: If the device is powered off.
    """
    inputs = {}

    phone_state = get_phone_state()

    if not phone_state.is_on:
        raise DevicePoweredOffError("Device is powered off. This action cannot be performed.")

    home_screen_app = next((app for app in phone_state.installed_apps if app.name == "Home Screen"), None)
    home_screen_package = home_screen_app.app_package_name if home_screen_app else None

    if phone_state.currently_open_app_package == home_screen_package:
        result = "Already on the home screen."
    else:
        update_phone_state({"currently_open_app_package": home_screen_package})
        result = "Successfully navigated to the home screen"
    
    summary = ActionSummary(result=result)
    
    return summary.model_dump(mode="json")