from typing import List, Optional, Dict, Any
from pydantic import ValidationError
from google_home.SimulationEngine.db import DB
from google_home.SimulationEngine.custom_errors import InvalidInputError, DeviceNotFoundError
from google_home.SimulationEngine.models import (
    MutateTraitCommands,
    MutateTraitResult,
    Action,
    APIName,
    CommandName,
    MutateParams,
)
from google_home.SimulationEngine.utils import update_device_state, process_schedules_and_get_structures, add_schedule_to_device


def mutate(
    devices: List[str],
    traits: List[str],
    commands: List[str],
    values: List[str],
    time_of_day: Optional[str] = None,
    date: Optional[str] = None,
    am_pm_or_unknown: Optional[str] = None,
    duration: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Changes traits of smart home devices and returns status of those changes.

    Args:
        devices (List[str]): Unique identifiers of smart home devices.
        traits (List[str]): Name of the trait to change.
        commands (List[str]): Name of the command. Valid values for command_names depend on trait_name.
        values (List[str]): New value of the command_name. Valid values for command_values depend on command_name.
        time_of_day (Optional[str]): time in the format of "HH:MM:SS"
        date (Optional[str]): date in the format of "YYYY-MM-DD"
        am_pm_or_unknown (Optional[str]): AM or PM or UNKNOWN
        duration (Optional[str]): duration in the format of 5s, 20m, 1h

    Returns:
        List[Dict[str, Any]]: A list of mutation results for each device.
            - commands (Dict[str, Any]): The commands that were executed.
                - device_ids (List[str]): The IDs of the devices that were mutated.
                - commands (List[Dict[str, Any]]): The commands that were executed.
                    - trait (str): The name of the trait that was changed.
                    - command_names (List[str]): The names of the commands that were executed.
                    - command_values (List[str]): The new values of the commands.
            - result (str): The result of the mutation (e.g., 'SUCCESS', 'FAILURE').
            - device_execution_results (Dict[str, Any]): The execution results for each device.
                - text_to_speech (str): Text to be spoken to the user.
                - results (List[Dict[str, Any]]): The execution results for each device.
                    - device_id (str): The ID of the device.
                    - result (str): The result of the execution (e.g., 'SUCCESS', 'FAILURE').

    Raises:
        InvalidInputError: If the input parameters are invalid.
        DeviceNotFoundError: If any of the requested devices are not found.
    """
    try:
        mutate_params = MutateParams(
            devices=devices,
            traits=traits,
            commands=commands,
            values=values,
            time_of_day=time_of_day,
            date=date,
            am_pm_or_unknown=am_pm_or_unknown,
            duration=duration,
        )

        mutated_commands = MutateTraitCommands(
            device_ids=devices,
            commands=[
                {
                    "trait": trait,
                    "command_names": commands,
                    "command_values": values,
                }
                for trait in traits
            ],
        )
    except ValidationError as e:
        raise InvalidInputError(f"Invalid input: {e}") from e

    structures = process_schedules_and_get_structures()
    all_devices = []
    for structure in structures.values():
        for room in structure.get("rooms", {}).values():
            for device_list in room.get("devices", {}).values():
                all_devices.extend(device_list)

    results = []
    is_schedule = time_of_day or date or duration
    for device_id in devices:
        device_found = False
        for device in all_devices:
            if device["id"] == device_id:
                device_found = True
                for command in mutated_commands.commands:
                    cmd_name = CommandName(command.command_names[0])
                    cmd_values = command.command_values
                    if is_schedule:
                        add_schedule_to_device(
                            device, cmd_name, cmd_values, time_of_day, date, am_pm_or_unknown, None, duration
                        )
                    else:
                        update_device_state(
                            device, cmd_name, cmd_values
                        )
                
                text_to_speech = f"Successfully mutated {device_id}"
                if is_schedule:
                    text_to_speech = f"Successfully scheduled mutation for {device_id}"

                results.append(
                    MutateTraitResult(
                        commands=mutated_commands,
                        result="SUCCESS",
                        device_execution_results={
                            "text_to_speech": text_to_speech,
                            "results": [
                                {"device_id": device_id, "result": "SUCCESS"}
                            ],
                        },
                    ).model_dump(mode="json")
                )
                break
        if not device_found:
            raise DeviceNotFoundError(f"Device with ID '{device_id}' not found.")

    action = Action(
        action_type=APIName.MUTATE,
        inputs={
            "devices": devices,
            "traits": traits,
            "commands": commands,
            "values": values,
            "time_of_day": time_of_day,
            "date": date,
            "am_pm_or_unknown": am_pm_or_unknown,
            "duration": duration,
        },
        outputs={"results": results},
    )
    DB["actions"].append(action.model_dump(mode="json"))

    return results
