from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ValidationError
from google_home.SimulationEngine.db import DB
from google_home.SimulationEngine.custom_errors import InvalidInputError, DeviceNotFoundError
from google_home.SimulationEngine.models import (
    MutateTraitCommands,
    MutateTraitResult,
    Action,
    APIName,
)
from google_home.SimulationEngine.utils import update_device_state, process_schedules_and_get_structures


def mutate_traits(
    device_ids: List[str],
    trait_names: List[str],
    command_names: List[str],
    command_values: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Changes traits of smart home devices and returns status of those changes.

    Args:
        device_ids (List[str]): Unique identifiers of smart home devices.
        trait_names (List[str]): Name of the trait to change.
        command_names (List[str]): Name of the command. Valid values for command_names depend on trait_name.
        command_values (Optional[List[str]]): New value of the command_name. Valid values for command_values depend on command_name. Default is None.

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
        commands = MutateTraitCommands(
            device_ids=device_ids,
            commands=[
                {
                    "trait": trait,
                    "command_names": command_names,
                    "command_values": command_values,
                }
                for trait in trait_names
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
    for device_id in device_ids:
        device_found = False
        for device in all_devices:
            if device["id"] == device_id:
                device_found = True
                for command in commands.commands:
                    update_device_state(
                        device, command.command_names[0], command.command_values
                    )
                results.append(
                    MutateTraitResult(
                        commands=commands,
                        result="SUCCESS",
                        device_execution_results={
                            "text_to_speech": f"Successfully mutated {device_id}",
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
        action_type=APIName.MUTATE_TRAITS,
        inputs={
            "device_ids": device_ids,
            "trait_names": trait_names,
            "command_names": command_names,
            "command_values": command_values,
        },
        outputs={"results": results},
    )
    DB["actions"].append(action.model_dump(mode="json"))

    return results