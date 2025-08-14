from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, time, timedelta
import re
from pydantic import StrictBool, ValidationError
from google_home.SimulationEngine.custom_errors import (
    InvalidInputError,
    DeviceNotFoundError,
)
from google_home.SimulationEngine.models import (
    CommandName,
    StateName,
    COMMAND_STATE_MAP,
    STATE_VALUE_TYPE_MAP,
    COMMAND_RANGE_RULES,
    FAN_SPEED_STRING_TO_INT_MAP,
    COMMANDS_REQUIRING_VALUES,
    COMMAND_VALUE_MAP,
    Structure,
    Room,
    DeviceInfo,
    DeviceType,
)
from google_home.SimulationEngine.db import DB


def string_to_bool(s: str) -> bool:
    s_lower = s.lower()
    if s_lower == 'true':
        return True
    if s_lower == 'false':
        return False
    raise ValueError("must be a valid bool")

def parse_duration_to_timedelta(duration_str: Optional[str]) -> timedelta:
    if not duration_str:
        return timedelta(0)
    parts = re.match(r'(\d+)([smh])', duration_str)
    if not parts:
        raise ValueError(f"Invalid duration format: {duration_str}")
    value, unit = int(parts.group(1)), parts.group(2)
    if unit == 's':
        return timedelta(seconds=value)
    elif unit == 'm':
        return timedelta(minutes=value)
    elif unit == 'h':
        return timedelta(hours=value)
    return timedelta(0)

def calculate_start_time(
    time_of_day: Optional[str], 
    date: Optional[str], 
    am_pm_or_unknown: Optional[str], 
    delay: Optional[str]
) -> datetime:
    now = datetime.now(timezone.utc)
    
    has_time_info = date or time_of_day

    if has_time_info:
        target_date = datetime.fromisoformat(date).date() if date else now.date()
        
        if time_of_day:
            hour, minute, second = map(int, time_of_day.split(':'))
            
            if am_pm_or_unknown:
                am_pm = am_pm_or_unknown.upper()
                if am_pm == 'PM' and 1 <= hour <= 11:
                    hour += 12
                elif am_pm == 'AM' and hour == 12: # 12 AM is 00:00
                    hour = 0
                elif am_pm == 'UNKNOWN': # use am for unknown
                    if hour == 12: # 12 AM is 00:00
                        hour = 0
        else:
            hour, minute, second = 0, 0, 0

        target_time = time(hour, minute, second)
        schedule_time = datetime.combine(target_date, target_time)
        schedule_time = schedule_time.replace(tzinfo=timezone.utc)

        if not date and schedule_time < now:
            schedule_time += timedelta(days=1)
    else:
        schedule_time = now

    if delay:
        delay_td = parse_duration_to_timedelta(delay)
        schedule_time += delay_td
            
    return schedule_time

def add_schedule_to_device(
    device: Dict[str, Any], 
    command: CommandName, 
    values: List[str], 
    time_of_day: Optional[str], 
    date: Optional[str], 
    am_pm_or_unknown: Optional[str], 
    delay: Optional[str], 
    duration: Optional[str]
):
    start_time = calculate_start_time(time_of_day, date, am_pm_or_unknown, delay)
    
    if "schedules" not in device:
        device["schedules"] = []
        
    new_schedule = {
        "action": command.value,
        "values": values,
        "start_time": start_time.isoformat(),
    }
    if duration:
        new_schedule["duration"] = duration
        
    device["schedules"].append(new_schedule)


def process_schedules():
    """
    Processes all schedules in the database and updates the device states accordingly.
    """
    now = datetime.now(timezone.utc)
    for structure in DB.get("structures", {}).values():
        for room in structure.get("rooms", {}).values():
            for device_list in room.get("devices", {}).values():
                for device in device_list:
                    schedules_to_remove = []
                    schedules_to_add = []
                    for schedule in device.get("schedules", []):
                        schedule_time = datetime.fromisoformat(schedule["start_time"])
                        if schedule_time <= now:
                            command_str = schedule["action"]
                            update_device_state(
                                device,
                                command_str,
                                schedule.get("values"),
                            )
                            schedules_to_remove.append(schedule)

                            if "duration" in schedule and schedule["duration"]:
                                duration_td = parse_duration_to_timedelta(schedule["duration"])
                                revert_time = schedule_time + duration_td
                                
                                command = CommandName(command_str)
                                if command == CommandName.ON:
                                    revert_schedule = {
                                        "action": CommandName.OFF.value,
                                        "values": [],
                                        "start_time": revert_time.isoformat()
                                    }
                                    schedules_to_add.append(revert_schedule)
                                elif command == CommandName.OFF:
                                    revert_schedule = {
                                        "action": CommandName.ON.value,
                                        "values": [],
                                        "start_time": revert_time.isoformat()
                                    }
                                    schedules_to_add.append(revert_schedule)
                                elif command == CommandName.TOGGLE_ON_OFF:
                                    revert_schedule = {
                                        "action": command.value,
                                        "values": [],
                                        "start_time": revert_time.isoformat()
                                    }
                                    schedules_to_add.append(revert_schedule)
                    
                    if schedules_to_remove or schedules_to_add:
                        current_schedules = device.get("schedules", [])
                        updated_schedules = [s for s in current_schedules if s not in schedules_to_remove]
                        updated_schedules.extend(schedules_to_add)
                        device["schedules"] = updated_schedules

def process_schedules_and_get_structures():
    """
    Processes all schedules in the database, updates the device states accordingly,
    and returns the updated structures.
    """
    process_schedules()
    return DB.get("structures", {})


def update_device_state(device: Dict[str, Any], command: CommandName, values: List[str]):
    """
    Updates the device state based on the given command.

    Args:
        device: The device to update.
        command: The command to execute.
        values: The values for the command.
    """
    if command not in COMMAND_STATE_MAP:
        raise NotImplementedError(f"Command '{command}' is not implemented.")

    if command in COMMANDS_REQUIRING_VALUES and not values:
        raise ValueError(f"Command '{command}' requires values, but none were provided.")

    for state_name in COMMAND_STATE_MAP[command]:
        for state in device["device_state"]:
            if state["name"] == state_name:
                if command in COMMAND_VALUE_MAP:
                    state["value"] = COMMAND_VALUE_MAP[command]
                elif command == CommandName.TOGGLE_ON_OFF:
                    state["value"] = not state["value"]
                elif command == CommandName.SET_MODE_AND_TEMPERATURE:
                    state["value"] = values[0]
                    for temp_state in device["device_state"]:
                        if (
                            temp_state["name"]
                            == StateName.THERMOSTAT_TEMPERATURE_SETPOINT
                        ):
                            temp_state["value"] = float(values[1])
                else:
                    value_type = STATE_VALUE_TYPE_MAP.get(state_name)
                    if value_type:
                        value_str = values[0]
                        if command == CommandName.SET_FAN_SPEED and value_str in FAN_SPEED_STRING_TO_INT_MAP:
                            value = FAN_SPEED_STRING_TO_INT_MAP[value_str]
                        elif value_type == StrictBool:
                            value = string_to_bool(value_str)
                        else:
                            value = value_type(value_str)

                        if command in COMMAND_RANGE_RULES:
                            min_val, max_val = COMMAND_RANGE_RULES[command]
                            if not (min_val <= value <= max_val):
                                raise ValueError(
                                    f"Value for {command.value} must be between {min_val} and {max_val}, but got {value}."
                                )
                        state["value"] = value
                    else:
                        state["value"] = values[0] if values else None


def get_structure(name: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a structure by its name from the GoogleHomeDB.

    Args:
        name (str): The name of the structure to retrieve.

    Returns:
        Optional[Dict[str, Any]]: The structure as a dictionary if found, otherwise None.
        The dictionary conforms to the `Structure` model. See the model for more details on the fields.
    """
    structure = DB.get("structures", {}).get(name)
    if structure:
        return Structure(**structure).model_dump(mode="json")
    return None

def add_structure(structure_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adds a new structure to the GoogleHomeDB.

    Args:
        structure_data (Dict[str, Any]): The dictionary representing the new structure.
        It must conform to the `Structure` model. See the model for more details on the fields.

    Returns:
        Dict[str, Any]: The added structure as a dictionary, conforming to the `Structure` model.

    Raises:
        InvalidInputError: If the structure_data is invalid or a structure with the same name already exists.
    """
    try:
        structure = Structure(**structure_data)
    except ValidationError as e:
        raise InvalidInputError(f"Invalid structure data: {e}") from e

    if structure.name in DB.get("structures", {}):
        raise InvalidInputError(f"Structure '{structure.name}' already exists.")

    DB.setdefault("structures", {})[structure.name] = structure.model_dump(mode="json")
    return structure.model_dump(mode="json")

def update_structure(name: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Updates an existing structure in the GoogleHomeDB.

    Args:
        name (str): The name of the structure to update.
        update_data (Dict[str, Any]): The dictionary with fields to update. The fields
        should be valid fields of the `Structure` model.

    Returns:
        Dict[str, Any]: The updated structure as a dictionary, conforming to the `Structure` model.

    Raises:
        DeviceNotFoundError: If the structure is not found.
        InvalidInputError: If the update_data is invalid.
    """
    structures = DB.get("structures", {})
    if name not in structures:
        raise DeviceNotFoundError(f"Structure '{name}' not found.")

    try:
        updated_structure_data = structures[name].copy()
        updated_structure_data.update(update_data)
        updated_structure = Structure(**updated_structure_data)
    except ValidationError as e:
        raise InvalidInputError(f"Invalid update data: {e}") from e

    del structures[name]
    structures[updated_structure.name] = updated_structure.model_dump(mode="json")
    return updated_structure.model_dump(mode="json")

def delete_structure(name: str) -> None:
    """
    Deletes a structure from the GoogleHomeDB.

    Args:
        name (str): The name of the structure to delete.

    Raises:
        DeviceNotFoundError: If the structure is not found.
    """
    structures = DB.get("structures", {})
    if name not in structures:
        raise DeviceNotFoundError(f"Structure '{name}' not found.")
    del structures[name]

def get_room(structure_name: str, room_name: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a room from a structure in the GoogleHomeDB.

    Args:
        structure_name (str): The name of the structure containing the room.
        room_name (str): The name of the room to retrieve.

    Returns:
        Optional[Dict[str, Any]]: The room as a dictionary if found, otherwise None.
        The dictionary conforms to the `Room` model. See the model for more details on the fields.
    """
    structure = get_structure(structure_name)
    if not structure:
        return None
    room = structure.get("rooms", {}).get(room_name)
    if room:
        return Room(**room).model_dump(mode="json")
    return None

def add_room(structure_name: str, room_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adds a new room to a structure in the GoogleHomeDB.

    Args:
        structure_name (str): The name of the structure to add the room to.
        room_data (Dict[str, Any]): The dictionary representing the new room.
        It must conform to the `Room` model. See the model for more details on the fields.

    Returns:
        Dict[str, Any]: The added room as a dictionary, conforming to the `Room` model.

    Raises:
        DeviceNotFoundError: If the structure is not found.
        InvalidInputError: If the room_data is invalid or a room with the same name already exists.
    """
    structures = DB.get("structures", {})
    if structure_name not in structures:
        raise DeviceNotFoundError(f"Structure '{structure_name}' not found.")

    try:
        room = Room(**room_data)
    except ValidationError as e:
        raise InvalidInputError(f"Invalid room data: {e}") from e

    if room.name in structures[structure_name].get("rooms", {}):
        raise InvalidInputError(f"Room '{room.name}' already exists in structure '{structure_name}'.")

    structures[structure_name].setdefault("rooms", {})[room.name] = room.model_dump(mode="json")
    return room.model_dump(mode="json")

def update_room(structure_name: str, room_name: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Updates an existing room in a structure.

    Args:
        structure_name (str): The name of the structure containing the room.
        room_name (str): The name of the room to update.
        update_data (Dict[str, Any]): The dictionary with fields to update. The fields
        should be valid fields of the `Room` model.

    Returns:
        Dict[str, Any]: The updated room as a dictionary, conforming to the `Room` model.

    Raises:
        DeviceNotFoundError: If the structure or room is not found.
        InvalidInputError: If the update_data is invalid.
    """
    structures = DB.get("structures", {})
    if structure_name not in structures or room_name not in structures[structure_name].get("rooms", {}):
        raise DeviceNotFoundError(f"Room '{room_name}' in structure '{structure_name}' not found.")

    try:
        updated_room_data = structures[structure_name]["rooms"][room_name].copy()
        updated_room_data.update(update_data)
        updated_room = Room(**updated_room_data)
    except ValidationError as e:
        raise InvalidInputError(f"Invalid update data: {e}") from e

    del structures[structure_name]["rooms"][room_name]
    structures[structure_name]["rooms"][updated_room.name] = updated_room.model_dump(mode="json")
    return updated_room.model_dump(mode="json")

def delete_room(structure_name: str, room_name: str) -> None:
    """
    Deletes a room from a structure.

    Args:
        structure_name (str): The name of the structure containing the room.
        room_name (str): The name of the room to delete.

    Raises:
        DeviceNotFoundError: If the structure or room is not found.
    """
    structures = DB.get("structures", {})
    if structure_name not in structures or room_name not in structures[structure_name].get("rooms", {}):
        raise DeviceNotFoundError(f"Room '{room_name}' in structure '{structure_name}' not found.")
    del structures[structure_name]["rooms"][room_name]

def get_device(device_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a device by its ID from the GoogleHomeDB.

    Args:
        device_id (str): The ID of the device to retrieve.

    Returns:
        Optional[Dict[str, Any]]: The device as a dictionary if found, otherwise None.
        The dictionary conforms to the `DeviceInfo` model. See the model for more details on the fields.
    """
    for structure in DB.get("structures", {}).values():
        for room in structure.get("rooms", {}).values():
            for device_list in room.get("devices", {}).values():
                for device in device_list:
                    if device.get("id") == device_id:
                        return DeviceInfo(**device).model_dump(mode="json")
    return None

def add_device(structure_name: str, room_name: str, device_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adds a new device to a room in the GoogleHomeDB.

    Args:
        structure_name (str): The name of the structure.
        room_name (str): The name of the room.
        device_data (Dict[str, Any]): The dictionary representing the new device.
        It must conform to the `DeviceInfo` model. See the model for more details on the fields.

    Returns:
        Dict[str, Any]: The added device as a dictionary, conforming to the `DeviceInfo` model.

    Raises:
        DeviceNotFoundError: If the structure or room is not found.
        InvalidInputError: If the device_data is invalid or a device with the same ID already exists.
    """
    structures = DB.get("structures", {})
    if structure_name not in structures or room_name not in structures[structure_name].get("rooms", {}):
        raise DeviceNotFoundError(f"Room '{room_name}' in structure '{structure_name}' not found.")

    try:
        device = DeviceInfo(**device_data)
    except ValidationError as e:
        raise InvalidInputError(f"Invalid device data: {e}") from e

    if get_device(device.id):
        raise InvalidInputError(f"Device with ID '{device.id}' already exists.")

    device_type = device.types[0] if device.types else DeviceType.SWITCH
    room = structures[structure_name]["rooms"][room_name]
    room.setdefault("devices", {}).setdefault(device_type, []).append(device.model_dump(mode="json"))
    return device.model_dump(mode="json")

def update_device(device_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Updates an existing device in the GoogleHomeDB.

    Args:
        device_id (str): The ID of the device to update.
        update_data (Dict[str, Any]): The dictionary with fields to update. The fields
        should be valid fields of the `DeviceInfo` model.

    Returns:
        Dict[str, Any]: The updated device as a dictionary, conforming to the `DeviceInfo` model.

    Raises:
        DeviceNotFoundError: If the device is not found.
        InvalidInputError: If the update_data is invalid.
    """
    for structure in DB.get("structures", {}).values():
        for room in structure.get("rooms", {}).values():
            for device_type, device_list in room.get("devices", {}).items():
                for i, device in enumerate(device_list):
                    if device.get("id") == device_id:
                        try:
                            updated_device_data = device.copy()
                            updated_device_data.update(update_data)
                            updated_device = DeviceInfo(**updated_device_data)
                        except ValidationError as e:
                            raise InvalidInputError(f"Invalid update data: {e}") from e
                        
                        device_list[i] = updated_device.model_dump(mode="json")
                        return updated_device.model_dump(mode="json")
    raise DeviceNotFoundError(f"Device with ID '{device_id}' not found.")

def delete_device(device_id: str) -> None:
    """
    Deletes a device from the GoogleHomeDB.

    Args:
        device_id (str): The ID of the device to delete.

    Raises:
        DeviceNotFoundError: If the device is not found.
    """
    for structure in DB.get("structures", {}).values():
        for room in structure.get("rooms", {}).values():
            for device_type, device_list in room.get("devices", {}).items():
                for i, device in enumerate(device_list):
                    if device.get("id") == device_id:
                        del device_list[i]
                        return
    raise DeviceNotFoundError(f"Device with ID '{device_id}' not found.")

