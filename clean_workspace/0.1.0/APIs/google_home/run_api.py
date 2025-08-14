from typing import List, Optional, Dict, Any
from pydantic import ValidationError
from google_home.SimulationEngine.db import DB
from google_home.SimulationEngine.custom_errors import InvalidInputError, DeviceNotFoundError
from google_home.SimulationEngine.models import (
    RunParams,
    MutateTraitResult,
    MutateTraitCommands,
    TRAIT_COMMAND_MAP,
    CommandName,
    Action,
    APIName,
)
from google_home.SimulationEngine.utils import update_device_state, process_schedules_and_get_structures, add_schedule_to_device


def run(
    devices: List[str],
    op: str,
    values: Optional[List[str]] = None,
    time_of_day: Optional[str] = None,
    date: Optional[str] = None,
    am_pm_or_unknown: Optional[str] = None,
    delay: Optional[str] = None,
    duration: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Runs a general operation on smart home devices and returns the status.

    Args:
        devices (List[str]): Unique identifiers of smart home devices.
        op (str): Name of the operation to run.
        values (Optional[List[str]]): Optional list of values for the operation.
        time_of_day (Optional[str]): Time to execute the operation, expected in the format of "HH:MM:SS"
        date (Optional[str]): Date to execute the operation, expected in the format of "YYYY-MM-DD"
        am_pm_or_unknown (Optional[str]): Whether time_of_day is AM or PM or UNKNOWN
        delay (Optional[str]): How long to wait before executing the operation. Example format are 5s, 20m, 1h
        duration (Optional[str]): How long the operation should last. Example format are 5s, 20m, 1h

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
        run_params = RunParams(
            devices=devices,
            op=op,
            values=values,
            time_of_day=time_of_day,
            date=date,
            am_pm_or_unknown=am_pm_or_unknown,
            delay=delay,
            duration=duration,
        )
    except ValidationError as e:
        raise InvalidInputError(f"Invalid input: {e}") from e

    trait = None
    command = CommandName(op)
    for trait_name, command_names in TRAIT_COMMAND_MAP.items():
        if command in command_names:
            trait = trait_name
            break

    if not trait:
        raise InvalidInputError(f"Invalid operation: {op}")

    structures = process_schedules_and_get_structures()
    all_devices = []
    for structure in structures.values():
        for room in structure.get("rooms", {}).values():
            for device_list in room.get("devices", {}).values():
                all_devices.extend(device_list)

    results = []
    is_schedule = time_of_day or date or delay or duration
    for device_id in devices:
        device_found = False
        for device in all_devices:
            if device["id"] == device_id:
                device_found = True
                if is_schedule:
                    add_schedule_to_device(
                        device, command, values, time_of_day, date, am_pm_or_unknown, delay, duration
                    )
                else:
                    update_device_state(device, command, values)

                text_to_speech = f"Successfully ran {op} on {device_id}"
                if is_schedule:
                    text_to_speech = f"Successfully scheduled {op} for {device_id}"
                
                results.append(
                    MutateTraitResult(
                        commands=MutateTraitCommands(
                            device_ids=[device_id],
                            commands=[
                                {
                                    "trait": trait,
                                    "command_names": [op],
                                    "command_values": values,
                                }
                            ],
                        ),
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
        action_type=APIName.RUN,
        inputs={
            "devices": devices,
            "op": op,
            "values": values,
            "time_of_day": time_of_day,
            "date": date,
            "am_pm_or_unknown": am_pm_or_unknown,
            "delay": delay,
            "duration": duration,
        },
        outputs={"results": results},
    )
    DB["actions"].append(action.model_dump(mode="json"))

    return results
