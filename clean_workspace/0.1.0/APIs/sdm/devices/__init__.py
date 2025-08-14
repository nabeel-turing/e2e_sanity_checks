from sdm.SimulationEngine.db import DB
from sdm.SimulationEngine.events import EVENTS
from sdm.SimulationEngine.utils import resolve_callable_from_path, _format_to_sdm_device
from typing import Optional

def execute_command(
    device_id: str,
    project_id: str,
    command_request: dict,
) -> dict:
    """
    Executes a command on a specific device managed by the enterprise.

    Args:
        device_id (str): The unique identifier of the device within the enterprise. For example, "CAM_001"
        project_id (str): The unique identifier of the enterprise or project.
        command_request (dict): The command request payload, Contains the keys:
            - command (str): The name of the command to execute. One of the following (followed by a brief explanation):
                - sdm.devices.commands.generate_camera_event_image (retrieve the image from a camera through a triggered event)
                - sdm.devices.commands.generate_rtsp_stream (start the rtsp stream mode of a camera)
                - sdm.devices.commands.stop_rtsp_stream (stop the rtsp stream mode of a camera)
                - sdm.devices.commands.generate_image_from_rtsp_stream (retrieve the image from a camera through its ongoing rtsp stream)
                - sdm.devices.commands.generate_web_rtc_stream (start the web_rtc stream mode of a camera)
                - sdm.devices.commands.stop_web_rtc_stream (stop the web_rtc stream mode of a camera)
                - sdm.devices.commands.generate_image_from_web_rtc_stream (retrieve the image from a camera through its ongoing web_rtc stream)
            - params (dict): Each command may have its own parameters, represented by key, value dictionaries. If None, the command does not have params. Use these as reference:
                - sdm.devices.commands.generate_camera_event_image: 
                    - event_id: (str): The ID of the triggered event.
                - sdm.devices.commands.generate_rtsp_stream: 
                    - None.
                - sdm.devices.commands.stop_rtsp_stream:
                    - stream_extension_token: (str): The extension token of the stream to stop.
                - sdm.devices.commands.generate_image_from_rtsp_stream: 
                    - rtsp_url: (str): The RTSP URL of the stream.
                - sdm.devices.commands.generate_web_rtc_stream:
                    - offer_sdp: (str): The SDP of the offer.
                - sdm.devices.commands.stop_web_rtc_stream:
                    - stream_media_session_id: (str): The media session ID of the stream to stop.
                - sdm.devices.commands.generate_image_from_web_rtc_stream:
                    - answer_sdp: (str): The SDP of the answer.

    Returns:
        dict: The response from the API, containing the result of the command execution.

    Raises:
        ValueError: If any required parameter is missing or invalid.
    """
    # Input Validation
    if not project_id:
        raise ValueError("project_id is required")
    if not device_id:
        raise ValueError("device_id is required")
    if not command_request:
        raise ValueError("command_request is required")
    if not command_request.get("command"):
        raise ValueError("command is required")
    
    # Execute Command
    command_name = command_request.get("command")
    command_params = command_request.get("params", {})
    command_params["device_id"] = device_id
    command_params["project_id"] = project_id
    command_function = resolve_callable_from_path(command_name)
    if not command_function:
        raise ValueError(f"Command {command_name} not found")
    return command_function(**command_params)

def get_device_info(
    device_id: str,
    project_id: str
) -> dict:
    """
    Retrieves information about an authorized device.

    Args:
        device_id (str): The unique identifier of the device within the enterprise.
        project_id (str): The unique identifier of the enterprise or project.

    Returns:
        dict: The device information including all traits and the parentRelations object. 
            Contains the following keys:
                - name (str): The internal name of the device built from the enterprise and device id.
                - type (str): The type of the device.
                - traits (dict): The traits of the device including the reference name of the device.
                - parentRelations (list): The parent relations of the device.  

    Raises:
        ValueError: If any required parameter is missing or invalid.
    """
    # Input Validation
    if not project_id:
        raise ValueError("project_id is required")
    if not device_id:
        raise ValueError("device_id is required")
    
    # Get Device Info
    device_info = DB.get("environment", {}).get("sdm", {}).get("devices", {}).get(device_id, {})
    if not device_info:
        raise ValueError(f"Device {device_id} not found")
    device = _format_to_sdm_device((device_id, device_info), project_id)
    return device

def list_devices(
) -> dict:
    """
    Makes a GET call to retrieve a list of all devices that the user has authorized
    for a given enterprise. The response typically includes a collection of device objects.

    Returns:
        dict: The response containing a list of device objects.
            Contains the following keys:
                - devices (list): The list of device objects. The list is empty if no devices are found.
                Each device object contains the following keys:
                    - name (str): The internal name of the device built from the enterprise and device id.
                    - type (str): The type of the device.
                    - traits (dict): The traits of the device including the reference name of the device.
                    - project_id (str): The enterprise or project id that the device belongs to.
                    - parentRelations (list): The parent relations of the device.  
    """
    project_id = next(
        (v for k, v in DB.items() if k.lower() == "project_id"), "project_id"
    )

    # Get Devices
    devices = DB.get("environment", {}).get("sdm", {}).get("devices", {})
    devices_list = []
    for device_dict in devices.items():
        device = _format_to_sdm_device(device_dict, project_id)
        devices_list.append(device)
    response = {"devices": devices_list}
    return response


def get_events_list(device_id: Optional[str] = None, event_type: Optional[str] = None) -> list:
    """
    Returns a list of events that were triggered.

    Args:
        device_id (Optional[str]): Optional unique identifier of a device to filter events. For example, "CAM_001".
        event_type (Optional[str]): Optional event_type to filter events.
            Should be one of: "Motion", "Person", "Sound" or "Chime".
            It also accepts formats such as: "sdm.devices.events.CameraMotion.Motion".
            If no device_id or event_type provided, returns all events.

    Returns:
        list: A list containing event payloads.
    """
    # Get Events
    events = EVENTS
    filtered_events = []

    if device_id:
        for event_payload in events:
            payload_device_id = event_payload.get("resourceUpdate").get("name").split("/")[-1]
            if payload_device_id == device_id:
                filtered_events.append(event_payload)
    else:
        filtered_events = events

    events = filtered_events
    filtered_events = []

    if event_type:
        trigger = event_type.split('.')[-1]
        if trigger not in ["Motion", "Person", "Sound", "Chime"]:
            raise ValueError(f"Event_type '{event_type}' not allowed")
        for event_payload in events:
            payload_event_type = next(iter(event_payload.get("resourceUpdate").get("events"))).split(".")[-1]
            if payload_event_type == trigger:
                filtered_events.append(event_payload)
    else:
        filtered_events = events

    return filtered_events

