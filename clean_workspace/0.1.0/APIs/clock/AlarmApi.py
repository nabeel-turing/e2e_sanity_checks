# APIs/clock/AlarmApi.py

from typing import Any, Dict, List, Optional
import json
from datetime import datetime, timedelta, time as dt_time
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from .SimulationEngine.db import DB
from .SimulationEngine.models import ClockResult, Alarm
from .SimulationEngine.utils import (
    _check_empty_field,
    _check_required_fields,
    _generate_id,
    _parse_duration,
    _parse_time,
    _calculate_alarm_time,
    _format_time,
    _filter_alarms,
    _get_current_time,
    _validate_recurrence,
    _seconds_to_duration,
    _get_alarm_state,

)
from .SimulationEngine.custom_errors import (
    EmptyFieldError, 
    MissingRequiredFieldError,
    InvalidTimeFormatError,
    InvalidDurationFormatError,
    InvalidDateFormatError,
    AlarmNotFoundError,
    InvalidRecurrenceError,
    InvalidStateOperationError,
    ValidationError as ClockValidationError
)


def create_alarm(
    duration: Optional[str] = None,
    time: Optional[str] = None,
    date: Optional[str] = None,
    label: Optional[str] = None,
    recurrence: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create a new alarm.

    This method can:
    1) Create an alarm with a given duration. (For example, set an alarm for 15 minutes.)
    2) Create an alarm at a specific time of the day. (For example, set an alarm at 10:30am.)

    Args:
        duration (Optional[str]): Duration of the alarm, in the format such as e.g. 5h30m20s, 10m, 2m15s, etc. 
        time (Optional[str]): Time of the day that the alarm should fire, in 12-hour format "H[:M[:S]]", e.g. "11:20".
        date (Optional[str]): Scheduled date in format of YYYY-MM-DD.
        label (Optional[str]): Label of the alarm.
        recurrence (Optional[List[str]]): Should be one or more of SUNDAY, MONDAY, TUESDAY, etc.

    Returns:
        Dict[str, Any]: A dictionary containing the created alarm information.

    Raises:
        TypeError: If parameters are not of the expected type
        ValueError: If validation fails
    """
    # Capture inputs for tracking
    inputs = {
        "duration": duration,
        "time": time,
        "date": date,
        "label": label,
        "recurrence": recurrence
    }
    
    # Type validation
    if duration is not None and not isinstance(duration, str):
        raise TypeError(f"duration must be a string, but got {type(duration).__name__}")
    
    if time is not None and not isinstance(time, str):
        raise TypeError(f"time must be a string, but got {type(time).__name__}")
    
    if date is not None and not isinstance(date, str):
        raise TypeError(f"date must be a string, but got {type(date).__name__}")
    
    if label is not None and not isinstance(label, str):
        raise TypeError(f"label must be a string, but got {type(label).__name__}")
    
    if recurrence is not None and not isinstance(recurrence, list):
        raise TypeError(f"recurrence must be a list, but got {type(recurrence).__name__}")

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

    # Validate date format if provided
    if date:
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid date format: {date}")

    # Validate recurrence if provided
    if recurrence:
        valid_days = ["SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"]
        invalid_days = [day for day in recurrence if day not in valid_days]
        if invalid_days:
            raise ValueError(f"Invalid recurrence days: {invalid_days}")

    # Calculate alarm time
    alarm_time = _calculate_alarm_time(duration=duration, time=time, date=date)

    # Ensure alarms dict exists before generating ID
    if not DB.get("alarms"):
        DB["alarms"] = {}
    
    # Generate alarm ID
    new_id = _generate_id("ALARM", DB["alarms"])

    # Create alarm data
    alarm_data = {
        "alarm_id": new_id,
        "time_of_day": _format_time(alarm_time.hour, alarm_time.minute, alarm_time.second),
        "date": alarm_time.date().isoformat(),
        "label": label or "",
        "state": "ACTIVE",
        "recurrence": ",".join(recurrence) if recurrence else "",
        "created_at": _get_current_time().isoformat(),
        "fire_time": alarm_time.isoformat()
    }

    # Store in DB
    DB["alarms"][new_id] = alarm_data

    # Create response
    result = ClockResult(
        message=f"Alarm created successfully for {alarm_data['time_of_day']}",
        alarm=[Alarm(**alarm_data)]
    )

    outputs = result.model_dump()
    


    return outputs


def show_matching_alarms(
    query: Optional[str] = None,
    alarm_type: Optional[str] = None,
    alarm_ids: Optional[List[str]] = None,
    date: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Shows the matching alarms to the user.

    Args:
        query (Optional[str]): Either the exact time or the label of the alarm.
        alarm_type (Optional[str]): Type of the alarm to show (UPCOMING, DISABLED, ACTIVE).
        alarm_ids (Optional[List[str]]): Alarm ids.
        date (Optional[str]): The date to show alarms for.
        start_date (Optional[str]): Filter for alarm scheduled to fire on or after this date.
        end_date (Optional[str]): Filter for alarm scheduled to fire on or before this date.

    Returns:
        Dict[str, Any]: A dictionary containing matching alarms.

    Raises:
        TypeError: If parameters are not of the expected type
        ValueError: If validation fails
    """
    # Type validation
    if query is not None and not isinstance(query, str):
        raise TypeError(f"query must be a string, but got {type(query).__name__}")
    
    if alarm_type is not None and not isinstance(alarm_type, str):
        raise TypeError(f"alarm_type must be a string, but got {type(alarm_type).__name__}")
    
    if alarm_ids is not None and not isinstance(alarm_ids, list):
        raise TypeError(f"alarm_ids must be a list, but got {type(alarm_ids).__name__}")
    
    if date is not None and not isinstance(date, str):
        raise TypeError(f"date must be a string, but got {type(date).__name__}")
    
    if start_date is not None and not isinstance(start_date, str):
        raise TypeError(f"start_date must be a string, but got {type(start_date).__name__}")
    
    if end_date is not None and not isinstance(end_date, str):
        raise TypeError(f"end_date must be a string, but got {type(end_date).__name__}")

    # Validate date formats
    for date_field, date_value in [("date", date), ("start_date", start_date), ("end_date", end_date)]:
        if date_value:
            try:
                datetime.strptime(date_value, "%Y-%m-%d")
            except ValueError:
                raise ValueError(f"Invalid date format for {date_field}: {date_value}")

    # Build filters
    filters = {}
    if query:
        # Determine if query is a time or label
        try:
            _parse_time(query)
            filters["time"] = query
        except ValueError:
            filters["label"] = query
    
    if alarm_type:
        filters["alarm_type"] = alarm_type
    
    if alarm_ids:
        filters["alarm_ids"] = alarm_ids
    
    if date:
        filters["date"] = date
    
    if start_date or end_date:
        filters["date_range"] = {
            "start_date": start_date,
            "end_date": end_date
        }

    # Filter alarms
    matching_alarms = _filter_alarms(DB["alarms"], filters)

    # Convert to response format
    alarm_list = []
    for alarm_data in matching_alarms:
        alarm_data["state"] = _get_alarm_state(alarm_data)
        alarm = Alarm(**alarm_data)
        alarm_list.append(alarm)

    result = ClockResult(
        message=f"Found {len(alarm_list)} matching alarm(s)",
        alarm=alarm_list
    )

    outputs = result.model_dump()
    


    return outputs


def modify_alarm_v2(
    filters: Optional[Dict[str, Any]] = None,
    modifications: Optional[Dict[str, Any]] = None,
    bulk_operation: bool = False
) -> Dict[str, Any]:
    """
    Modifies an alarm or multiple alarms' label, time, or state.

    Args:
        filters (Optional[Dict[str, Any]]): Filters to identify the existing alarms that need to be modified.
        modifications (Optional[Dict[str, Any]]): Modifications to make to the existing alarms.
        bulk_operation (bool): Set to true ONLY when the user clearly wants to modify multiple alarms.

    Returns:
        Dict[str, Any]: A dictionary containing the modified alarm information.

    Raises:
        TypeError: If parameters are not of the expected type
        ValueError: If validation fails
    """
    # Type validation
    if filters is not None and not isinstance(filters, dict):
        raise TypeError(f"filters must be a dict, but got {type(filters).__name__}")
    
    if modifications is not None and not isinstance(modifications, dict):
        raise TypeError(f"modifications must be a dict, but got {type(modifications).__name__}")
    
    if not isinstance(bulk_operation, bool):
        raise TypeError(f"bulk_operation must be a bool, but got {type(bulk_operation).__name__}")

    # If no filters provided, return all alarms for clarification
    if not filters:
        all_alarms = list(DB["alarms"].values()) if DB["alarms"] else []
        alarm_list = [Alarm(**alarm) for alarm in all_alarms]
        return ClockResult(
            message="Please specify which alarm you want to modify",
            alarm=alarm_list
        ).model_dump()

    # Find matching alarms
    matching_alarms = _filter_alarms(DB["alarms"], filters)
    
    if not matching_alarms:
        return ClockResult(
            message="No matching alarms found",
            alarm=[]
        ).model_dump()

    # If multiple alarms found and not bulk operation, ask for clarification
    if len(matching_alarms) > 1 and not bulk_operation:
        alarm_list = [Alarm(**alarm) for alarm in matching_alarms]
        return ClockResult(
            message="Multiple alarms found. Please be more specific or use bulk operation.",
            alarm=alarm_list
        ).model_dump()

    # Apply modifications
    modified_alarms = []
    deleted_alarms = []
    
    for alarm_data in matching_alarms:
        if modifications:
            # Apply time modification
            if "time" in modifications:
                try:
                    hour, minute, second = _parse_time(modifications["time"])
                    current_date = datetime.fromisoformat(alarm_data["date"])
                    new_alarm_time = current_date.replace(
                        hour=hour,
                        minute=minute,
                        second=second
                    )
                    alarm_data["time_of_day"] = _format_time(new_alarm_time.hour, new_alarm_time.minute, new_alarm_time.second)
                    alarm_data["fire_time"] = new_alarm_time.isoformat()
                except ValueError:
                    raise ValueError(f"Invalid time format: {modifications['time']}")

            # Apply duration addition
            if "duration_to_add" in modifications:
                try:
                    duration_seconds = _parse_duration(modifications["duration_to_add"])
                    current_fire_time = datetime.fromisoformat(alarm_data["fire_time"])
                    new_fire_time = current_fire_time + timedelta(seconds=duration_seconds)
                    alarm_data["fire_time"] = new_fire_time.isoformat()
                    alarm_data["time_of_day"] = _format_time(new_fire_time.hour, new_fire_time.minute, new_fire_time.second)
                except ValueError:
                    raise ValueError(f"Invalid duration format: {modifications['duration_to_add']}")

            # Apply date modification
            if "date" in modifications:
                try:
                    datetime.strptime(modifications["date"], "%Y-%m-%d")
                    alarm_data["date"] = modifications["date"]
                except ValueError:
                    raise ValueError(f"Invalid date format: {modifications['date']}")

            # Apply label modification
            if "label" in modifications:
                alarm_data["label"] = modifications["label"]

            # Apply recurrence modification
            if "recurrence" in modifications:
                if isinstance(modifications["recurrence"], list):
                    valid_days = ["SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"]
                    invalid_days = [day for day in modifications["recurrence"] if day not in valid_days]
                    if invalid_days:
                        raise ValueError(f"Invalid recurrence days: {invalid_days}")
                    alarm_data["recurrence"] = ",".join(modifications["recurrence"])
                else:
                    alarm_data["recurrence"] = modifications["recurrence"]

            # Apply state operation
            if "state_operation" in modifications:
                valid_operations = ["ENABLE", "DISABLE", "DELETE", "CANCEL", "DISMISS", "STOP", "PAUSE"]
                if modifications["state_operation"] not in valid_operations:
                    raise ValueError(f"Invalid state operation: {modifications['state_operation']}")
                
                if modifications["state_operation"] == "DELETE":
                    # Store deleted alarm info before removing
                    deleted_alarms.append(alarm_data.copy())
                    # Remove from DB
                    if alarm_data["alarm_id"] in DB["alarms"]:
                        del DB["alarms"][alarm_data["alarm_id"]]
                    continue
                else:
                    # Update state
                    state_map = {
                        "ENABLE": "ACTIVE",
                        "DISABLE": "DISABLED",
                        "CANCEL": "CANCELLED",
                        "SNOOZED": "SNOOZED",
                        "PAUSED": "PAUSED"
                    }
                    alarm_data["state"] = state_map.get(modifications["state_operation"], "ACTIVE")

        # Update in DB
        DB["alarms"][alarm_data["alarm_id"]] = alarm_data
        modified_alarms.append(alarm_data)

    # Create response
    alarm_list = [Alarm(**alarm) for alarm in modified_alarms]
    
    # Determine appropriate message
    if deleted_alarms:
        message = f"Successfully deleted {len(deleted_alarms)} alarm(s)"
        if modified_alarms:
            message += f" and modified {len(modified_alarms)} alarm(s)"
    else:
        message = f"Successfully modified {len(alarm_list)} alarm(s)"
    
    result = ClockResult(
        message=message,
        alarm=alarm_list
    )

    outputs = result.model_dump()
    
    # Determine which alarm IDs were affected
    affected_ids = [alarm["alarm_id"] for alarm in modified_alarms + deleted_alarms]
    


    return outputs


def snooze(
    time: Optional[str] = None,
    duration: Optional[int] = None
) -> Dict[str, Any]:
    """
    Snoozes an alarm that is firing.

    Args:
        time (Optional[str]): The time to snooze until, in 12-hour format "H[:M[:S]]".
        duration (Optional[int]): Duration to snooze the alarm, in seconds.

    Returns:
        Dict[str, Any]: A dictionary containing the snooze result.

    Raises:
        TypeError: If parameters are not of the expected type
        ValueError: If validation fails
    """
    # Type validation
    if time is not None and not isinstance(time, str):
        raise TypeError(f"time must be a string, but got {type(time).__name__}")
    
    if duration is not None and not isinstance(duration, int):
        raise TypeError(f"duration must be an int, but got {type(duration).__name__}")

    # Validate time format if provided
    if time:
        try:
            _parse_time(time)
        except ValueError:
            raise ValueError(f"Invalid time format: {time}")

    # Default to 10 minutes if no time or duration specified
    if not time and not duration:
        duration = 600  # 10 minutes

    # Find firing alarms
    firing_alarms = [
        alarm for alarm in DB.get("alarms", {}).values() if _get_alarm_state(alarm) == "FIRING"
    ]
    
    if not firing_alarms:
        return ClockResult(
            message="No firing alarms found to snooze.",
            alarm=[]
        ).model_dump()
    
    snoozed_alarms = []
    for alarm_data in firing_alarms:
        if time:
            # Snooze until specific time
            try:
                hour, minute, second = _parse_time(time)
                current_date = datetime.now().date()
                snooze_until = datetime.combine(current_date, dt_time(hour, minute, second))
                
                # If the time is in the past, assume next day
                if snooze_until <= datetime.now():
                    snooze_until += timedelta(days=1)
                    
                alarm_data["fire_time"] = snooze_until.isoformat()
                alarm_data["time_of_day"] = _format_time(snooze_until.hour, snooze_until.minute, snooze_until.second)
                alarm_data["date"] = snooze_until.date().isoformat()
            except ValueError:
                raise ValueError(f"Invalid time format: {time}")
        else:
            # Snooze for duration
            current_time = datetime.now()
            snooze_until = current_time + timedelta(seconds=duration)
            
            alarm_data["fire_time"] = snooze_until.isoformat()
            alarm_data["time_of_day"] = _format_time(snooze_until.hour, snooze_until.minute, snooze_until.second)
            alarm_data["date"] = snooze_until.date().isoformat()

        alarm_data["state"] = "SNOOZED"
        
        # Update in DB
        DB["alarms"][alarm_data["alarm_id"]] = alarm_data
        snoozed_alarms.append(alarm_data)

    # Create response
    alarm_list = [Alarm(**alarm) for alarm in snoozed_alarms]
    result = ClockResult(
        message=f"Successfully snoozed {len(alarm_list)} alarm(s)",
        alarm=alarm_list
    )

    outputs = result.model_dump()
    


    return outputs


def create_clock(
    type: str,
    duration: Optional[str] = None,
    time_of_day: Optional[str] = None,
    am_pm_or_unknown: Optional[str] = None,
    date: Optional[str] = None,
    label: Optional[str] = None,
    recurrence: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Creates a clock object which can either be a timer or an alarm.

    Args:
        type (str): Type of the clock component. Either TIMER or ALARM.
        duration (Optional[str]): Duration of the timer or alarm.
        time_of_day (Optional[str]): Time of the day in HH:MM:SS format.
        am_pm_or_unknown (Optional[str]): One of AM, PM, or UNKNOWN.
        date (Optional[str]): Scheduled date in format of YYYY-MM-DD.
        label (Optional[str]): Label of the timer or alarm.
        recurrence (Optional[List[str]]): Recurrence pattern for alarms.

    Returns:
        Dict[str, Any]: A dictionary containing the created clock component.

    Raises:
        TypeError: If parameters are not of the expected type
        ValueError: If validation fails
    """
    # Capture inputs for tracking
    inputs = {
        "type": type,
        "duration": duration,
        "time_of_day": time_of_day,
        "am_pm_or_unknown": am_pm_or_unknown,
        "date": date,
        "label": label,
        "recurrence": recurrence
    }
    
    # Type validation
    if not isinstance(type, str):
        raise TypeError(f"type must be a string, but got {type(type).__name__}")
    
    if duration is not None and not isinstance(duration, str):
        raise TypeError(f"duration must be a string, but got {type(duration).__name__}")
    
    if time_of_day is not None and not isinstance(time_of_day, str):
        raise TypeError(f"time_of_day must be a string, but got {type(time_of_day).__name__}")
    
    if am_pm_or_unknown is not None and not isinstance(am_pm_or_unknown, str):
        raise TypeError(f"am_pm_or_unknown must be a string, but got {type(am_pm_or_unknown).__name__}")
    
    if date is not None and not isinstance(date, str):
        raise TypeError(f"date must be a string, but got {type(date).__name__}")
    
    if label is not None and not isinstance(label, str):
        raise TypeError(f"label must be a string, but got {type(label).__name__}")
    
    if recurrence is not None and not isinstance(recurrence, list):
        raise TypeError(f"recurrence must be a list, but got {type(recurrence).__name__}")
    
    # ValueError when type is empty
    if not type:
        raise ValueError("type must not be empty")
    

    # Validate type
    if type.upper() not in ["TIMER", "ALARM"]:
        raise ValueError(f"type must be TIMER or ALARM, but got {type}")

    if type.upper() == "TIMER":
        # Import TimerApi locally to avoid circular import at module level
        from . import TimerApi
        
        # Convert create_clock parameters to create_timer parameters
        timer_params = {
            "duration": duration,
            "time": time_of_day,
            "label": label
        }
        outputs = TimerApi.create_timer(**timer_params)
        

        
        return outputs
    
    elif type.upper() == "ALARM":
        # Convert time_of_day to time format if needed
        alarm_time = None
        if time_of_day:
            # Parse HH:MM:SS format and convert to 12-hour format
            try:
                parsed_time = datetime.strptime(time_of_day, "%H:%M:%S")
                if am_pm_or_unknown and am_pm_or_unknown != "UNKNOWN":
                    alarm_time = parsed_time.strftime("%I:%M:%S").lstrip("0") + f" {am_pm_or_unknown}"
                else:
                    alarm_time = parsed_time.strftime("%I:%M:%S").lstrip("0")
            except ValueError:
                raise ValueError(f"Invalid time_of_day format: {time_of_day}")
        
        outputs = create_alarm(
            duration=duration,
            time=alarm_time,
            date=date,
            label=label,
            recurrence=recurrence
        )
        

        
        return outputs


def modify_alarm(
    query: Optional[str] = None,
    alarm_type: Optional[str] = None,
    new_time_of_day: Optional[str] = None,
    new_am_pm_or_unknown: Optional[str] = None,
    new_label: Optional[str] = None,
    alarm_ids: Optional[List[str]] = None,
    duration_to_add: Optional[str] = None,
    date: Optional[str] = None,
    new_date: Optional[str] = None,
    new_recurrence: Optional[List[str]] = None,
    bulk_operation: bool = False
) -> Dict[str, Any]:
    """
    Modifies when alarm(s) should go off.

    Args:
        query (Optional[str]): Alarm's time of day or label.
        alarm_type (Optional[str]): Type of the alarm to be modified.
        new_time_of_day (Optional[str]): The new time of the day.
        new_am_pm_or_unknown (Optional[str]): One of AM, PM or UNKNOWN.
        new_label (Optional[str]): The new label to be updated to.
        alarm_ids (Optional[List[str]]): Alarm ids.
        duration_to_add (Optional[str]): The duration to add to the current alarm.
        date (Optional[str]): The alarm with the date that should modify for.
        new_date (Optional[str]): The new date that the alarm should be updated to.
        new_recurrence (Optional[List[str]]): New recurrence pattern.
        bulk_operation (bool): Whether to perform a bulk operation on all alarms.

    Returns:
        Dict[str, Any]: A dictionary containing the modified alarm information.

    Raises:
        TypeError: If parameters are not of the expected type
        ValueError: If validation fails
    """
    # Capture inputs for tracking
    inputs = {
        "query": query,
        "alarm_type": alarm_type,
        "new_time_of_day": new_time_of_day,
        "new_am_pm_or_unknown": new_am_pm_or_unknown,
        "new_label": new_label,
        "alarm_ids": alarm_ids,
        "duration_to_add": duration_to_add,
        "date": date,
        "new_date": new_date,
        "new_recurrence": new_recurrence,
        "bulk_operation": bulk_operation
    }
    
    # Convert parameters to modify_alarm_v2 format
    filters = {}
    modifications = {}
    
    # Build filters
    if query:
        try:
            _parse_time(query)
            filters["time"] = query
        except ValueError:
            filters["label"] = query
    
    if alarm_type:
        filters["alarm_type"] = alarm_type
    
    if alarm_ids:
        filters["alarm_ids"] = alarm_ids
    
    if date:
        filters["date"] = date
    
    # Build modifications
    if new_time_of_day:
        # Convert HH:MM:SS to 12-hour format
        try:
            parsed_time = datetime.strptime(new_time_of_day, "%H:%M:%S")
            if new_am_pm_or_unknown and new_am_pm_or_unknown != "UNKNOWN":
                modifications["time"] = parsed_time.strftime("%I:%M:%S").lstrip("0") + f" {new_am_pm_or_unknown}"
            else:
                modifications["time"] = parsed_time.strftime("%I:%M:%S").lstrip("0")
        except ValueError:
            raise ValueError(f"Invalid new_time_of_day format: {new_time_of_day}")
    
    if new_label:
        modifications["label"] = new_label
    
    if duration_to_add:
        modifications["duration_to_add"] = duration_to_add
    
    if new_date:
        modifications["date"] = new_date
    
    if new_recurrence:
        modifications["recurrence"] = new_recurrence
    
    # Use modify_alarm_v2
    outputs = modify_alarm_v2(filters=filters, modifications=modifications, bulk_operation=bulk_operation)
    

    
    return outputs


def change_alarm_state(
    alarm_ids: Optional[List[str]] = None,
    alarm_type: Optional[str] = None,
    time_of_day: Optional[str] = None,
    am_pm_or_unknown: Optional[str] = None,
    label: Optional[str] = None,
    state_operation: Optional[str] = None,
    date: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    bulk_operation: bool = False
) -> Dict[str, Any]:
    """
    Changes an alarm's state or bulk changes all alarms' state.

    Args:
        alarm_ids (Optional[List[str]]): Alarm ids.
        alarm_type (Optional[str]): Type of the alarm to be modified.
        time_of_day (Optional[str]): Time of the day of the alarm.
        am_pm_or_unknown (Optional[str]): One of AM, PM or UNKNOWN.
        label (Optional[str]): Alarm label.
        state_operation (Optional[str]): Operation to change the alarm state.
        date (Optional[str]): The date of the alarm to be modified.
        start_date (Optional[str]): Filter for alarm scheduled to fire on or after this date.
        end_date (Optional[str]): Filter for alarm scheduled to fire on or before this date.
        bulk_operation (bool): Whether to perform a bulk operation on all alarms.

    Returns:
        Dict[str, Any]: A dictionary containing the modified alarm information.

    Raises:
        TypeError: If parameters are not of the expected type
        ValueError: If validation fails
    """
    # Capture inputs for tracking
    inputs = {
        "alarm_ids": alarm_ids,
        "alarm_type": alarm_type,
        "time_of_day": time_of_day,
        "am_pm_or_unknown": am_pm_or_unknown,
        "label": label,
        "state_operation": state_operation,
        "date": date,
        "start_date": start_date,
        "end_date": end_date,
        "bulk_operation": bulk_operation
    }
    
    # Convert parameters to modify_alarm_v2 format
    filters = {}
    modifications = {}
    
    # Build filters
    if alarm_ids:
        filters["alarm_ids"] = alarm_ids
    
    if alarm_type:
        filters["alarm_type"] = alarm_type
    
    if time_of_day:
        # Convert HH:MM:SS to 12-hour format
        try:
            parsed_time = datetime.strptime(time_of_day, "%H:%M:%S")
            if am_pm_or_unknown and am_pm_or_unknown != "UNKNOWN":
                filters["time"] = parsed_time.strftime("%I:%M:%S").lstrip("0") + f" {am_pm_or_unknown}"
            else:
                filters["time"] = parsed_time.strftime("%I:%M:%S").lstrip("0")
        except ValueError:
            raise ValueError(f"Invalid time_of_day format: {time_of_day}")
    
    if label:
        filters["label"] = label
    
    if date:
        filters["date"] = date
    
    if start_date or end_date:
        filters["date_range"] = {
            "start_date": start_date,
            "end_date": end_date
        }
    
    # Build modifications
    if state_operation:
        modifications["state_operation"] = state_operation
    
    # Use modify_alarm_v2
    outputs = modify_alarm_v2(filters=filters, modifications=modifications, bulk_operation=bulk_operation)
    

    
    return outputs


def snooze_alarm(
    snooze_duration: Optional[str] = None,
    snooze_till_time_of_day: Optional[str] = None,
    am_pm_or_unknown: Optional[str] = None
) -> Dict[str, Any]:
    """
    Snoozes an alarm that has fired.

    Args:
        snooze_duration (Optional[str]): Duration to snooze the alarm in seconds.
        snooze_till_time_of_day (Optional[str]): The time of day to snooze the alarm until.
        am_pm_or_unknown (Optional[str]): One of AM, PM or UNKNOWN.

    Returns:
        Dict[str, Any]: A dictionary containing the snooze result.

    Raises:
        TypeError: If parameters are not of the expected type
        ValueError: If validation fails
    """
    # Capture inputs for tracking
    inputs = {
        "snooze_duration": snooze_duration,
        "snooze_till_time_of_day": snooze_till_time_of_day,
        "am_pm_or_unknown": am_pm_or_unknown
    }
    
    # Type validation
    if snooze_duration is not None and not isinstance(snooze_duration, str):
        raise TypeError(f"snooze_duration must be a string, but got {type(snooze_duration).__name__}")
    
    if snooze_till_time_of_day is not None and not isinstance(snooze_till_time_of_day, str):
        raise TypeError(f"snooze_till_time_of_day must be a string, but got {type(snooze_till_time_of_day).__name__}")
    
    if am_pm_or_unknown is not None and not isinstance(am_pm_or_unknown, str):
        raise TypeError(f"am_pm_or_unknown must be a string, but got {type(am_pm_or_unknown).__name__}")

    # Convert parameters to snooze format
    duration = None
    time = None
    
    if snooze_duration:
        try:
            duration = int(snooze_duration)
        except ValueError:
            raise ValueError(f"Invalid snooze_duration: {snooze_duration}")
    
    if snooze_till_time_of_day:
        # Convert HH:MM:SS to 12-hour format
        try:
            parsed_time = datetime.strptime(snooze_till_time_of_day, "%H:%M:%S")
            if am_pm_or_unknown and am_pm_or_unknown != "UNKNOWN":
                time = parsed_time.strftime("%I:%M:%S").lstrip("0") + f" {am_pm_or_unknown}"
            else:
                time = parsed_time.strftime("%I:%M:%S").lstrip("0")
        except ValueError:
            raise ValueError(f"Invalid snooze_till_time_of_day format: {snooze_till_time_of_day}")
    
    # Use snooze function
    outputs = snooze(time=time, duration=duration)
    
    
    return outputs 