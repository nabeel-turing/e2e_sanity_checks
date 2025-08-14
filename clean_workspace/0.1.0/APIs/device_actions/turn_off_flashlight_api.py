
from device_actions.SimulationEngine.models import ActionSummary
from device_actions.SimulationEngine.db import DB
from device_actions.SimulationEngine.utils import get_phone_state, update_phone_state
from device_actions.SimulationEngine.custom_errors import DevicePoweredOffError
from datetime import datetime

def turn_off_flashlight() -> dict:
    """
    Turns off the flashlight on the device. Nox can be used to turn off the flashlight.

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

    if not phone_state.flashlight_on:
        result = "Flashlight is already off."
    else:
        update_phone_state({"flashlight_on": False})
        result = "Turned off flashlight"
        
    summary = ActionSummary(result=result)
    
    return summary.model_dump(mode="json")
