
from device_actions.SimulationEngine.models import ActionSummary, Media
from device_actions.SimulationEngine.db import DB
import uuid
from datetime import datetime
from device_actions.SimulationEngine.custom_errors import DevicePoweredOffError
from device_actions.SimulationEngine.utils import get_phone_state

def take_screenshot() -> dict:
    """
    Takes a screenshot on the device.

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

    result = "Captured a screenshot"
        
    summary = ActionSummary(result=result)
    
    screenshot_name = f"Screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    screenshot = Media(name=screenshot_name)
    DB["phone_state"]["screenshots"].append(screenshot.model_dump(mode="json"))

    return summary.model_dump(mode="json")
