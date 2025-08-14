import json
from typing import List, Dict, Any
from pydantic import ValidationError
from google_home.SimulationEngine.custom_errors import InvalidInputError, DeviceNotFoundError
from google_home.SimulationEngine.utils import process_schedules_and_get_structures
from google_home.SimulationEngine.models import DetailsParams


def details(devices: List[str]) -> Dict[str, Any]:
    """retrieves the state of devices in the user's home, such as the current temperature,
    the current volume, or the current status of a light.

    Args:
        devices (List[str]): Unique identifiers of smart home devices.

    Returns:
        Dict[str, Any]: A dictionary containing the state of the requested devices.
            - devices_info (str): A string representation of the devices' state.

    Raises:
        InvalidInputError: If the input parameters are invalid.
        DeviceNotFoundError: If any of the requested devices are not found.
    """
    try:
        DetailsParams(devices=devices)
    except ValidationError as e:
        raise InvalidInputError(f"Invalid input: {e}") from e

    structures = process_schedules_and_get_structures()
    devices_info = {}
    all_devices = []
    for structure in structures.values():
        for room in structure.get("rooms", {}).values():
            for device_list in room.get("devices", {}).values():
                all_devices.extend(device_list)
    
    if not devices:
        return {"devices_info": json.dumps(structures)}    

    for device_id in devices:
        device_found = False
        for device in all_devices:
            if device["id"] == device_id:
                devices_info[device_id] = device["device_state"]
                device_found = True
                break
        if not device_found:
            raise DeviceNotFoundError(f"Device with ID '{device_id}' not found.")

    return {"devices_info": json.dumps(devices_info)}
