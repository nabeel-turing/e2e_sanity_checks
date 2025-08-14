import re
import datetime
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime, timedelta, time as dt_time
import uuid
from .db import DB
    

def _check_required_fields(payload: dict, required: List[str]) -> Optional[str]:
    """
    Check for missing required fields in the payload.
    
    Args:
        payload (dict): The payload to check
        required (List[str]): List of required field names
        
    Returns:
        Optional[str]: Error message if missing fields found, None otherwise
    """
    missing_fields = [field for field in required if field not in payload]
    if missing_fields:
        return f"Missing required fields: {', '.join(missing_fields)}."
    return None


def _check_empty_field(field: str, var: Any) -> Optional[str]:
    """
    Check if the field value is empty.
    
    Args:
        field (str): The field name
        var (Any): The variable to check
        
    Returns:
        Optional[str]: Field name if empty, empty string otherwise
    """
    if var in [None, "", [], {}, set()]:
        return f"{field}"
    return ""


def _generate_id(prefix: str, existing: Dict[str, Any]) -> str:
    """
    Generate a simple ID like prefix-<num> for the resource.
    
    Args:
        prefix (str): The prefix for the ID
        existing (Dict[str, Any]): Dictionary of existing items
        
    Returns:
        str: Generated ID
    """
    return f"{prefix}-{len(existing) + 1}"


def _generate_unique_id(prefix: str = "ID") -> str:
    """
    Generate a unique ID using UUID.
    
    Args:
        prefix (str): The prefix for the ID
        
    Returns:
        str: Unique ID
    """
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _parse_duration(duration_str: str) -> int:
    """
    Parse a duration string and return the total seconds.
    
    Args:
        duration_str (str): Duration string like "5h30m20s", "10m", "2m15s"
        
    Returns:
        int: Total seconds
        
    Raises:
        ValueError: If the duration format is invalid
    """
    if not duration_str:
        return 0
    
    # Pattern to match duration components
    pattern = r'^(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?$'
    match = re.match(pattern, duration_str)
    
    if not match:
        raise ValueError(f"Invalid duration format: {duration_str}")
    
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    
    # At least one component must be present
    if hours == 0 and minutes == 0 and seconds == 0:
        raise ValueError(f"Invalid duration format: {duration_str}")
    
    return hours * 3600 + minutes * 60 + seconds


def _seconds_to_duration(seconds: int) -> str:
    """
    Convert seconds to duration string format.
    
    Args:
        seconds (int): Total seconds
        
    Returns:
        str: Duration string in format "1h30m45s"
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0:
        parts.append(f"{secs}s")
    
    return "".join(parts) if parts else "0s"


def _parse_time(time_str: str) -> Tuple[int, int, int]:
    """
    Parse a time string and return hour, minute, second.
    
    Args:
        time_str (str): Time string like "11:20", "11:20:30", "11:20 AM"
        
    Returns:
        Tuple[int, int, int]: Hour, minute, second
        
    Raises:
        ValueError: If the time format is invalid
    """
    if not time_str:
        raise ValueError("Time string cannot be empty")
    
    # Handle AM/PM
    am_pm = None
    if time_str.upper().endswith(' AM'):
        am_pm = 'AM'
        time_str = time_str[:-3].strip()
    elif time_str.upper().endswith(' PM'):
        am_pm = 'PM'
        time_str = time_str[:-3].strip()
    
    # Parse time components
    time_parts = time_str.split(':')
    if len(time_parts) < 2 or len(time_parts) > 3:
        raise ValueError(f"Invalid time format: {time_str}")
    
    try:
        hour = int(time_parts[0])
        minute = int(time_parts[1])
        second = int(time_parts[2]) if len(time_parts) == 3 else 0
    except ValueError:
        raise ValueError(f"Invalid time format: {time_str}")
    
    # Handle AM/PM conversion
    if am_pm:
        if am_pm == 'PM' and hour != 12:
            hour += 12
        elif am_pm == 'AM' and hour == 12:
            hour = 0
    
    # Validate ranges
    if not (0 <= hour <= 23):
        raise ValueError(f"Invalid hour: {hour}")
    if not (0 <= minute <= 59):
        raise ValueError(f"Invalid minute: {minute}")
    if not (0 <= second <= 59):
        raise ValueError(f"Invalid second: {second}")
    
    return hour, minute, second


def _format_time(hour: int, minute: int, second: int = 0, use_12_hour: bool = True) -> str:
    """
    Format time components into a string.
    
    Args:
        hour (int): Hour (0-23)
        minute (int): Minute (0-59)
        second (int): Second (0-59)
        use_12_hour (bool): Whether to use 12-hour format with AM/PM
        
    Returns:
        str: Formatted time string
    """
    if use_12_hour:
        am_pm = 'AM' if hour < 12 else 'PM'
        display_hour = hour if hour <= 12 else hour - 12
        if display_hour == 0:
            display_hour = 12
        
        if second > 0:
            return f"{display_hour}:{minute:02d}:{second:02d} {am_pm}"
        else:
            return f"{display_hour}:{minute:02d} {am_pm}"
    else:
        if second > 0:
            return f"{hour:02d}:{minute:02d}:{second:02d}"
        else:
            return f"{hour:02d}:{minute:02d}"


def _calculate_alarm_time(duration: Optional[str] = None, time: Optional[str] = None, 
                         date: Optional[str] = None) -> datetime:
    """
    Calculate when an alarm should fire based on duration or time.
    
    Args:
        duration (Optional[str]): Duration from now (e.g., "30m")
        time (Optional[str]): Specific time (e.g., "09:30")
        date (Optional[str]): Specific date (e.g., "2024-01-15")
        
    Returns:
        datetime: When the alarm should fire
        
    Raises:
        ValueError: If neither duration nor time is provided
    """
    now = datetime.now()
    
    if duration:
        seconds = _parse_duration(duration)
        return now + timedelta(seconds=seconds)
    
    if time:
        hour, minute, second = _parse_time(time)
        
        if date:
            # Parse the date
            try:
                target_date = datetime.strptime(date, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError(f"Invalid date format: {date}")
            
            alarm_time = datetime.combine(target_date, dt_time(hour, minute, second))
        else:
            # Use today's date, but if the time has passed, use tomorrow
            alarm_time = datetime.combine(now.date(), dt_time(hour, minute, second))
            if alarm_time <= now:
                alarm_time += timedelta(days=1)
        
        return alarm_time
    
    raise ValueError("Either duration or time must be provided")


def _calculate_timer_time(duration: Optional[str] = None, time: Optional[str] = None) -> Tuple[datetime, int]:
    """
    Calculate when a timer should fire and its original duration.
    
    Args:
        duration (Optional[str]): Duration for the timer (e.g., "30m")
        time (Optional[str]): Specific time when timer should fire (e.g., "09:30")
        
    Returns:
        Tuple[datetime, int]: When the timer should fire and original duration in seconds
        
    Raises:
        ValueError: If neither duration nor time is provided
    """
    now = datetime.now()
    
    if duration:
        seconds = _parse_duration(duration)
        fire_time = now + timedelta(seconds=seconds)
        return fire_time, seconds
    
    if time:
        hour, minute, second = _parse_time(time)
        fire_time = datetime.combine(now.date(), dt_time(hour, minute, second))
        
        # If the time has passed today, assume tomorrow
        if fire_time <= now:
            fire_time += timedelta(days=1)
        
        # Calculate the duration
        duration_seconds = int((fire_time - now).total_seconds())
        return fire_time, duration_seconds
    
    raise ValueError("Either duration or time must be provided")


def _filter_alarms(alarms: Dict[str, Any], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Filter alarms based on provided filters.
    
    Args:
        alarms (Dict[str, Any]): Dictionary of alarms
        filters (Dict[str, Any]): Filter criteria
        
    Returns:
        List[Dict[str, Any]]: List of filtered alarms
    """
    filtered_alarms = []
    
    for alarm_id, alarm_data in alarms.items():
        if _alarm_matches_filter(alarm_data, filters):
            filtered_alarms.append(alarm_data)
    
    return filtered_alarms


def _alarm_matches_filter(alarm: Dict[str, Any], filters: Dict[str, Any]) -> bool:
    """
    Check if an alarm matches the given filters.
    
    Args:
        alarm (Dict[str, Any]): Alarm data
        filters (Dict[str, Any]): Filter criteria
        
    Returns:
        bool: True if alarm matches filters
    """
    # Time filter
    if filters.get("time") and alarm.get("time_of_day") != filters["time"]:
        return False
    
    # Label filter
    if filters.get("label") and alarm.get("label") != filters["label"]:
        return False
    
    # Alarm type filter
    if filters.get("alarm_type"):
        filter_type = filters["alarm_type"].upper()
        stored_state = alarm.get("state", "").upper()

        if filter_type == "UPCOMING":
            fire_time = datetime.fromisoformat(alarm["fire_time"])
            if not (stored_state == "ACTIVE" and fire_time > datetime.now()):
                return False
        elif filter_type == "ACTIVE":
            if stored_state != "ACTIVE":
                return False
        elif filter_type == "DISABLED":
            if stored_state != "DISABLED":
                return False
    
    # Alarm IDs filter
    if filters.get("alarm_ids") and alarm.get("alarm_id") not in filters["alarm_ids"]:
        return False

    # Date filter
    if filters.get("date"):
        alarm_date = alarm.get("date")
        if alarm_date != filters["date"]:
            return False

    # Date range filter
    if "date_range" in filters:
        start_date_str = filters["date_range"].get("start_date")
        end_date_str = filters["date_range"].get("end_date")
        alarm_date_str = alarm.get("date")

        if alarm_date_str:
            alarm_date = datetime.strptime(alarm_date_str, "%Y-%m-%d").date()

            if start_date_str:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                if alarm_date < start_date:
                    return False
            
            if end_date_str:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                if alarm_date > end_date:
                    return False
    
    return True


def _filter_timers(timers: Dict[str, Any], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Filter timers based on provided filters.
    
    Args:
        timers (Dict[str, Any]): Dictionary of timers
        filters (Dict[str, Any]): Filter criteria
        
    Returns:
        List[Dict[str, Any]]: List of filtered timers
    """
    filtered_timers = []
    
    for timer_id, timer_data in timers.items():
        if _timer_matches_filter(timer_data, filters):
            filtered_timers.append(timer_data)
    
    return filtered_timers


def _timer_matches_filter(timer: Dict[str, Any], filters: Dict[str, Any]) -> bool:
    """
    Check if a timer matches the given filters.
    
    Args:
        timer (Dict[str, Any]): Timer data
        filters (Dict[str, Any]): Filter criteria
        
    Returns:
        bool: True if timer matches filters
    """
    # Duration filter
    if filters.get("duration") and timer.get("original_duration") != filters["duration"]:
        return False
    
    # Label filter
    if filters.get("label") and timer.get("label") != filters["label"]:
        return False
    
    # Timer type filter
    if filters.get("timer_type"):
        timer_state = timer.get("state", "").upper()
        filter_type = filters["timer_type"].upper()
        
        if filter_type == "RUNNING" and timer_state != "RUNNING":
            return False
        elif filter_type == "PAUSED" and timer_state != "PAUSED":
            return False
        elif filter_type == "UPCOMING" and timer_state != "UPCOMING":
            return False
    
    # Timer IDs filter
    if filters.get("timer_ids") and timer.get("timer_id") not in filters["timer_ids"]:
        return False
    
    return True


def _get_current_time() -> datetime:
    """
    Get the current time.
    
    Returns:
        datetime: Current time
    """
    return datetime.now()


def _validate_recurrence(recurrence: List[str]) -> bool:
    """
    Validate recurrence days.
    
    Args:
        recurrence (List[str]): List of recurrence days
        
    Returns:
        bool: True if valid
    """
    valid_days = ["SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"]
    return all(day in valid_days for day in recurrence) 

def _get_alarm_state(alarm):
    """
    Determines the current state of an alarm based on its properties and the current time.

    If the alarm's state is not "ACTIVE" or "SNOOZED", returns the current state.
    If the alarm is "ACTIVE" or "SNOOZED" and the current time is greater than or equal to the alarm's fire time,
    returns "FIRING". Otherwise, returns the alarm's current state.

    Args:
        alarm (dict): A dictionary representing the alarm, expected to have at least
                      the keys "state" (str) and "fire_time" (ISO 8601 datetime string).

    Returns:
        str: The evaluated state of the alarm ("FIRING", the original state, or another state).
    """
    if alarm["state"] not in ["ACTIVE", "SNOOZED"]:
        return alarm["state"]

    now = datetime.now()
    fire_time = datetime.fromisoformat(alarm["fire_time"])

    if now >= fire_time:
        return "FIRING"
    return alarm["state"]

