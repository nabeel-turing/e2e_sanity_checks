from typing import Optional
from device_actions.SimulationEngine.models import OpenAppInput, ActionSummary
from device_actions.SimulationEngine.db import DB
from device_actions.SimulationEngine.utils import get_phone_state, update_phone_state
from device_actions.SimulationEngine.custom_errors import AppNotFoundError, AppNameAndPackageMismatchError, DevicePoweredOffError
from pydantic import ValidationError
from device_actions.SimulationEngine.llm_interface import call_llm

def open_app(app_name: str, app_package_name: Optional[str] = None, extras: Optional[str] = None) -> dict:
    """
    Opens the requested application on the device.

    Alternative app names:
     - If the user wants to open "alarms" or "timers" but there is no app with an
       obviously matching name, open any clock app, if present, as a less-preferred fallback.

    Args:
        app_name (str): The name of the application to open.
            This name has to exactly match one of the names produced by `get_installed_apps`.
        app_package_name (Optional[str]): The package name of the application to open.
        extras (Optional[str]): The extras in json string format to send to the application being opened.
            Note:
             * This should only be populated when opening "Pixel Screenshots".
             * When opening "Pixel Screenshots", always extract the information-seeking part of the user prompt and populate it in the extras field.
             * The key of the extras field is "query". The value of the extras field is the query extracted from the user prompt.
             * The query should be a full question/sentence, unless the original user prompt is too terse to infer one.

    Returns:
        dict: A dictionary containing the result of the action.
            - result (str): A message indicating the result of the action.
            - card_id (str): A unique identifier for the action card.

    Raises:
        ValueError: If the input is invalid.
        AppNotFoundError: If the app is not found.
        AppNameAndPackageMismatchError: If the app name and package name do not match.
        DevicePoweredOffError: If the device is powered off.
    """
    try:
        input_data = OpenAppInput(app_name=app_name, app_package_name=app_package_name, extras=extras)
    except ValidationError as e:
        raise ValueError(f"Invalid input: {e}")

    inputs = {
        "app_name": app_name,
        "app_package_name": app_package_name,
        "extras": extras,
    }

    phone_state = get_phone_state()

    if not phone_state.is_on:
        raise DevicePoweredOffError("Device is powered off. This action cannot be performed.")
    
    app_to_open = next((app for app in phone_state.installed_apps if app.name == input_data.app_name), None)

    if not app_to_open:
        installed_apps = [app.name for app in phone_state.installed_apps]
        prompt = (
            f"Given '{input_data.app_name}', pick the most similar or related app from: {installed_apps}.\n"
            "If no exact match, choose a fallback (e.g., for 'alarms' or 'timers', pick a clock app; for 'maps', pick 'Google Maps').\n"
            "If none are relevant, do not pick any app. Respond with the app name only, or return NOT FOUND if not relevant."
        )
        fallback_app_name = call_llm(prompt)
        fallback_app_name = fallback_app_name.strip().replace("\n", "").replace("\r", "")
        app_to_open = next((app for app in phone_state.installed_apps if app.name == fallback_app_name), None)

    if not app_to_open:
        raise AppNotFoundError(f"App '{input_data.app_name}' not found.")
    
    if input_data.app_package_name and app_to_open.app_package_name != input_data.app_package_name:
        raise AppNameAndPackageMismatchError(f"App name '{input_data.app_name}' and package name '{input_data.app_package_name}' do not match.")

    if phone_state.currently_open_app_package == app_to_open.app_package_name:
        result = f"App '{app_to_open.name}' is already open."
    else:
        update_phone_state({"currently_open_app_package": app_to_open.app_package_name})
        result = f"Opened app: {app_to_open.name}"    
    summary = ActionSummary(result=result)
    
    return summary.model_dump(mode="json")