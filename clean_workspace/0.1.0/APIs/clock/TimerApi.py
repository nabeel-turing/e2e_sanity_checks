# APIs/clock/TimerApi.py

from typing import Any, Dict, List, Optional
import json
from datetime import datetime, timedelta, time as dt_time
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from .SimulationEngine.db import DB
from .SimulationEngine.models import ClockResult, Timer
from .SimulationEngine.utils import (
    _check_empty_field,
    _check_required_fields,
    _generate_id,
    _parse_duration,
    _parse_time,
    _calculate_timer_time,
    _format_time,
    _filter_timers,
    _get_current_time,
    _seconds_to_duration,

)
from .SimulationEngine.custom_errors import (
    EmptyFieldError, 
    MissingRequiredFieldError,
    InvalidTimeFormatError,
    InvalidDurationFormatError,
    TimerNotFoundError,
    InvalidStateOperationError,
    ValidationError as ClockValidationError
)


def create_timer(
    duration: Optional[str] = None,
    time: Optional[str] = None,
    label: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new timer.

    This method can:
    1) Create a timer with a given duration. (For example, set a timer for 10 minutes.)
    2) Create a timer for a specific time. (For example, set a timer to go off at 10:30.)

    Args:
        duration (Optional[str]): Duration of the timer, in the format such as e.g. 5h30m20s, 10m, 2m15s, etc.
        time (Optional[str]): Time of the day that the timer should fire, in 12-hour format "H[:M[:S]]".
        label (Optional[str]): Label of the timer, if meaningful.

    Returns:
        Dict[str, Any]: A dictionary containing the created timer information.

    Raises:
        TypeError: If parameters are not of the expected type
        ValueError: If validation fails
    """
    # Capture inputs for tracking
    inputs = {
        "duration": duration,
        "time": time,
        "label": label
    }
    
    # Type validation
    if duration is not None and not isinstance(duration, str):
        raise TypeError(f"duration must be a string, but got {type(duration).__name__}")
    
    if time is not None and not isinstance(time, str):
        raise TypeError(f"time must be a string, but got {type(time).__name__}")
    
    if label is not None and not isinstance(label, str):
        raise TypeError(f"label must be a string, but got {type(label).__name__}")

    # Validate that either duration or time is provided
    if not duration and not time:
        raise ValueError("Either duration or time must be provided")

    # Validate duration format if provided
    if duration:
        try:
            _parse_duration(duration)
        except ValueError:
            raise ValueError(f"Invalid duration format: {duration}")

    # Validate time format if provided
    if time:
        try:
            _parse_time(time)
        except ValueError:
            raise ValueError(f"Invalid time format: {time}")

    # Calculate timer time and duration
    fire_time, original_duration = _calculate_timer_time(duration=duration, time=time)

    # Ensure timers dict exists before generating ID
    if not DB.get("timers"):
        DB["timers"] = {}
    
    # Generate timer ID
    new_id = _generate_id("TIMER", DB["timers"])

    # Create timer data
    timer_data = {
        "timer_id": new_id,
        "original_duration": _seconds_to_duration(original_duration),
        "remaining_duration": _seconds_to_duration(original_duration),
        "time_of_day": _format_time(fire_time.hour, fire_time.minute, fire_time.second),
        "label": label or "",
        "state": "RUNNING",
        "created_at": _get_current_time().isoformat(),
        "fire_time": fire_time.isoformat(),
        "start_time": _get_current_time().isoformat()
    }

    # Store in DB
    DB["timers"][new_id] = timer_data

    # Create response
    response_timer_data = timer_data.copy()
    result = ClockResult(
        message=f"Timer created successfully for {timer_data['original_duration']}",
        timer=[Timer(**response_timer_data)]
    )

    outputs = result.model_dump()
    


    return outputs


def show_matching_timers(
    query: Optional[str] = None,
    timer_type: Optional[str] = None,
    timer_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Shows the matching timers to the user.

    Args:
        query (Optional[str]): Either the duration, time_of_day, or the label of the timer.
        timer_type (Optional[str]): Type of the timer to show (UPCOMING, PAUSED, RUNNING).
        timer_ids (Optional[List[str]]): The ids of the timers to be shown to the user.

    Returns:
        Dict[str, Any]: A dictionary containing matching timers.

    Raises:
        TypeError: If parameters are not of the expected type
        ValueError: If validation fails
    """
    # Capture inputs for tracking
    inputs = {
        "query": query,
        "timer_type": timer_type,
        "timer_ids": timer_ids
    }
    
    # Type validation
    if query is not None and not isinstance(query, str):
        raise TypeError(f"query must be a string, but got {type(query).__name__}")
    
    if timer_type is not None and not isinstance(timer_type, str):
        raise TypeError(f"timer_type must be a string, but got {type(timer_type).__name__}")
    
    if timer_ids is not None and not isinstance(timer_ids, list):
        raise TypeError(f"timer_ids must be a list, but got {type(timer_ids).__name__}")

    # Build filters
    filters = {}
    if query:
        # Try to determine if query is duration, time, or label
        try:
            _parse_duration(query)
            filters["duration"] = query
        except ValueError:
            try:
                _parse_time(query)
                filters["time"] = query
            except ValueError:
                filters["label"] = query
    
    if timer_type:
        filters["timer_type"] = timer_type
    
    if timer_ids:
        filters["timer_ids"] = timer_ids

    # Filter timers
    matching_timers = _filter_timers(DB.get("timers", {}), filters)

    # Update remaining duration for running timers
    current_time = _get_current_time()
    for timer_data in matching_timers:
        if timer_data["state"] == "RUNNING":
            start_time = datetime.fromisoformat(timer_data["start_time"])
            elapsed_seconds = int((current_time - start_time).total_seconds())
            original_seconds = _parse_duration(timer_data["original_duration"])
            remaining_seconds = max(0, original_seconds - elapsed_seconds)
            timer_data["remaining_duration"] = _seconds_to_duration(remaining_seconds)

    # Convert to response format
    timer_list = [Timer(**timer) for timer in matching_timers]

    result = ClockResult(
        message=f"Found {len(timer_list)} matching timer(s)",
        timer=timer_list
    )

    outputs = result.model_dump()
    


    return outputs


def modify_timer_v2(
    filters: Optional[Dict[str, Any]] = None,
    modifications: Optional[Dict[str, Any]] = None,
    bulk_operation: bool = False
) -> Dict[str, Any]:
    """
    Modifies a timer or multiple timers' label, duration, or state.

    Args:
        filters (Optional[Dict[str, Any]]): Filters to identify the existing timers that need to be modified.
        modifications (Optional[Dict[str, Any]]): Modifications to make to the existing timers.
        bulk_operation (bool): Only true when the user wants to perform a bulk operation on all timers.

    Returns:
        Dict[str, Any]: A dictionary containing the modified timer information.

    Raises:
        TypeError: If parameters are not of the expected type
        ValueError: If validation fails
    """
    # Capture inputs for tracking
    inputs = {
        "filters": filters,
        "modifications": modifications,
        "bulk_operation": bulk_operation
    }
    
    # Type validation
    if filters is not None and not isinstance(filters, dict):
        raise TypeError(f"filters must be a dict, but got {type(filters).__name__}")
    
    if modifications is not None and not isinstance(modifications, dict):
        raise TypeError(f"modifications must be a dict, but got {type(modifications).__name__}")
    
    if not isinstance(bulk_operation, bool):
        raise TypeError(f"bulk_operation must be a bool, but got {type(bulk_operation).__name__}")

    # If no filters provided, return all timers for clarification
    if not filters:
        all_timers = list(DB.get("timers", {}).values())
        timer_list = [Timer(**timer) for timer in all_timers]
        result = ClockResult(
            message="Please specify which timer you want to modify",
            timer=timer_list
        )
        outputs = result.model_dump()
        

        
        return outputs

    # Find matching timers
    matching_timers = _filter_timers(DB.get("timers", {}), filters)
    
    if not matching_timers:
        result = ClockResult(
            message="No matching timers found",
            timer=[]
        )
        outputs = result.model_dump()
        

        
        return outputs

    # If multiple timers found and not bulk operation, ask for clarification
    if len(matching_timers) > 1 and not bulk_operation:
        timer_list = [Timer(**timer) for timer in matching_timers]
        result = ClockResult(
            message="Multiple timers found. Please be more specific or use bulk operation.",
            timer=timer_list
        )
        outputs = result.model_dump()
        

        
        return outputs

    # Apply modifications
    modified_timers = []
    deleted_timers = []
    
    for timer_data in matching_timers:
        if modifications:
            # Handle state operation first, especially deletion
            if "state_operation" in modifications:
                operation = modifications["state_operation"]
                if operation == "DELETE":
                    if timer_data["timer_id"] in DB["timers"]:
                        deleted_timers.append(timer_data.copy())
                        del DB["timers"][timer_data["timer_id"]]
                    continue  # Skip other modifications for deleted timers

            # Apply duration modification
            if "duration" in modifications:
                try:
                    new_duration_seconds = _parse_duration(modifications["duration"])
                    timer_data["original_duration"] = _seconds_to_duration(new_duration_seconds)
                    timer_data["remaining_duration"] = _seconds_to_duration(new_duration_seconds)
                    
                    current_time = _get_current_time()
                    new_fire_time = current_time + timedelta(seconds=new_duration_seconds)
                    timer_data["fire_time"] = new_fire_time.isoformat()
                    timer_data["time_of_day"] = _format_time(new_fire_time.hour, new_fire_time.minute, new_fire_time.second)
                    timer_data["start_time"] = current_time.isoformat()
                except ValueError:
                    raise ValueError(f"Invalid duration format: {modifications['duration']}")

            # Apply duration addition
            if "duration_to_add" in modifications:
                try:
                    add_seconds = _parse_duration(modifications["duration_to_add"])
                    current_duration = _parse_duration(timer_data["original_duration"]) # Add to original time
                    new_duration_seconds = current_duration + add_seconds
                    
                    timer_data["original_duration"] = _seconds_to_duration(new_duration_seconds)
                    timer_data["remaining_duration"] = _seconds_to_duration(new_duration_seconds)
                    
                    current_time = _get_current_time()
                    new_fire_time = current_time + timedelta(seconds=new_duration_seconds)
                    timer_data["fire_time"] = new_fire_time.isoformat()
                    timer_data["time_of_day"] = _format_time(new_fire_time.hour, new_fire_time.minute, new_fire_time.second)
                    timer_data["start_time"] = current_time.isoformat()
                except ValueError:
                    raise ValueError(f"Invalid duration format: {modifications['duration_to_add']}")

            # Apply label modification
            if "label" in modifications:
                timer_data["label"] = modifications["label"]

            # Apply state operation (excluding DELETE)
            if "state_operation" in modifications:
                operation = modifications["state_operation"]
                valid_operations = ["PAUSE", "RESUME", "RESET", "CANCEL", "DISMISS", "STOP", "DELETE"]
                if operation not in valid_operations:
                    raise ValueError(f"Invalid state operation: {operation}")
                
                if operation in ["PAUSE", "RESUME", "RESET", "CANCEL", "DISMISS", "STOP"]:
                    state_map = {
                        "PAUSE": "PAUSED",
                        "RESUME": "RUNNING",
                        "RESET": "RESET",
                        "CANCEL": "CANCELLED",
                        "DISMISS": "CANCELLED",
                        "STOP": "STOPPED"
                    }
                    timer_data["state"] = state_map.get(operation, "RUNNING")
                    
                    if operation == "RESET":
                        original_seconds = _parse_duration(timer_data["original_duration"])
                        timer_data["remaining_duration"] = _seconds_to_duration(original_seconds)
                        timer_data["start_time"] = _get_current_time().isoformat()
                    
                    elif operation == "RESUME":
                        timer_data["start_time"] = _get_current_time().isoformat()

        # Update in DB
        DB["timers"][timer_data["timer_id"]] = timer_data
        modified_timers.append(timer_data)

    # Create response
    all_affected_timers = modified_timers + deleted_timers
    timer_list = [Timer(**timer) for timer in all_affected_timers]
    
    # Determine appropriate message
    if deleted_timers:
        message = f"Successfully deleted {len(deleted_timers)} timer(s)"
        if modified_timers:
            message += f" and modified {len(modified_timers)} timer(s)"
    else:
        message = f"Successfully modified {len(timer_list)} timer(s)"
    
    result = ClockResult(
        message=message,
        timer=timer_list
    )

    outputs = result.model_dump()
    
    # Determine which timer IDs were affected
    affected_ids = [timer["timer_id"] for timer in modified_timers + deleted_timers]
    


    return outputs


def modify_timer(
    query: Optional[str] = None,
    timer_type: Optional[str] = None,
    new_duration: Optional[str] = None,
    duration_to_add: Optional[str] = None,
    new_label: Optional[str] = None,
    timer_ids: Optional[List[str]] = None,
    bulk_operation: bool = False
) -> Dict[str, Any]:
    """
    Modifies timer(s)'s duration or label.

    Args:
        query (Optional[str]): Either the duration or the label of the timer.
        timer_type (Optional[str]): Either UPCOMING, PAUSED or RUNNING.
        new_duration (Optional[str]): New duration that the timer should be updated to.
        duration_to_add (Optional[str]): The duration to add to the current timer.
        new_label (Optional[str]): The new label to be updated to.
        timer_ids (Optional[List[str]]): Timer ids.
        bulk_operation (bool): Whether to perform a bulk operation on all timers.

    Returns:
        Dict[str, Any]: A dictionary containing the modified timer information.

    Raises:
        TypeError: If parameters are not of the expected type
        ValueError: If validation fails
    """
    # Capture inputs for tracking
    inputs = {
        "query": query,
        "timer_type": timer_type,
        "new_duration": new_duration,
        "duration_to_add": duration_to_add,
        "new_label": new_label,
        "timer_ids": timer_ids,
        "bulk_operation": bulk_operation
    }
    
    # Convert parameters to modify_timer_v2 format
    filters = {}
    modifications = {}
    
    # Build filters
    if query:
        # Try to determine if query is duration or label
        try:
            _parse_duration(query)
            filters["duration"] = query
        except ValueError:
            filters["label"] = query
    
    if timer_type:
        filters["timer_type"] = timer_type
    
    if timer_ids:
        filters["timer_ids"] = timer_ids
    
    # Build modifications
    if new_duration:
        modifications["duration"] = new_duration
    
    if duration_to_add:
        modifications["duration_to_add"] = duration_to_add
    
    if new_label:
        modifications["label"] = new_label
    
    # Use modify_timer_v2
    outputs = modify_timer_v2(filters=filters, modifications=modifications, bulk_operation=bulk_operation)
    

    
    return outputs


def change_timer_state(
    timer_ids: Optional[List[str]] = None,
    timer_type: Optional[str] = None,
    duration: Optional[str] = None,
    label: Optional[str] = None,
    state_operation: Optional[str] = None,
    bulk_operation: bool = False
) -> Dict[str, Any]:
    """
    Changes timers' state such as to resume, pause, reset, cancel, delete, stop, dismiss etc.

    Args:
        timer_ids (Optional[List[str]]): Timer ids.
        timer_type (Optional[str]): Either UPCOMING, PAUSED or RUNNING.
        duration (Optional[str]): Duration of the timer that should be modified.
        label (Optional[str]): The label of the timer that should be modified.
        state_operation (Optional[str]): Operation to change the timer state.
        bulk_operation (bool): Whether to perform a bulk operation on all timers.

    Returns:
        Dict[str, Any]: A dictionary containing the modified timer information.

    Raises:
        TypeError: If parameters are not of the expected type
        ValueError: If validation fails
    """
    # Capture inputs for tracking
    inputs = {
        "timer_ids": timer_ids,
        "timer_type": timer_type,
        "duration": duration,
        "label": label,
        "state_operation": state_operation,
        "bulk_operation": bulk_operation
    }
    
    # Convert parameters to modify_timer_v2 format
    filters = {}
    modifications = {}
    
    # Build filters
    if timer_ids:
        filters["timer_ids"] = timer_ids
    
    if timer_type:
        filters["timer_type"] = timer_type
    
    if duration:
        filters["duration"] = duration
    
    if label:
        filters["label"] = label
    
    # Build modifications
    if state_operation:
        modifications["state_operation"] = state_operation
    
    # Use modify_timer_v2
    outputs = modify_timer_v2(filters=filters, modifications=modifications, bulk_operation=bulk_operation)
    
    
    return outputs 