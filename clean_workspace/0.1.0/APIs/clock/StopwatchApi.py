# APIs/clock/StopwatchApi.py

from typing import Any, Dict, List, Optional
import json
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from .SimulationEngine.db import DB
from .SimulationEngine.models import ClockResult
from .SimulationEngine.utils import (
    _get_current_time,
    _seconds_to_duration,

)
from .SimulationEngine.custom_errors import (
    EmptyFieldError, 
    ValidationError as ClockValidationError
)


def _initialize_stopwatch():
    """Initialize stopwatch in DB if it doesn't exist or is empty"""
    if "stopwatch" not in DB or not DB["stopwatch"]:
        DB["stopwatch"] = {
            "state": "STOPPED",
            "start_time": None,
            "pause_time": None,
            "elapsed_time": 0,
            "lap_times": []
        }
    
    stopwatch = DB["stopwatch"]
    
    # Ensure stopwatch has all required fields
    if "state" not in stopwatch:
        stopwatch["state"] = "STOPPED"
    if "start_time" not in stopwatch:
        stopwatch["start_time"] = None
    if "pause_time" not in stopwatch:
        stopwatch["pause_time"] = None
    if "elapsed_time" not in stopwatch:
        stopwatch["elapsed_time"] = 0
    if "lap_times" not in stopwatch:
        stopwatch["lap_times"] = []
    
    return stopwatch


def start_stopwatch() -> Dict[str, Any]:
    """
    Starts or resumes the stopwatch.

    Returns:
        Dict[str, Any]: A dictionary containing the stopwatch status.

    Raises:
        None: This function should not raise exceptions
    """
    current_time = _get_current_time()
    
    # Initialize stopwatch in DB if it doesn't exist
    stopwatch = _initialize_stopwatch()
    
    if stopwatch["state"] == "STOPPED":
        # Start fresh
        stopwatch.update({
            "state": "RUNNING",
            "start_time": current_time.isoformat(),
            "pause_time": None,
            "elapsed_time": 0,
            "lap_times": []
        })
        message = "Stopwatch started"
    
    elif stopwatch["state"] == "PAUSED":
        # Resume from pause
        pause_duration = (current_time - datetime.fromisoformat(stopwatch["pause_time"])).total_seconds()
        # calculates the new start time of the stopwatch by subtracting the elapsed_time from current_time.
        new_start_time = current_time - timedelta(seconds=stopwatch["elapsed_time"])
        
        stopwatch.update({
            "state": "RUNNING",
            "start_time": new_start_time.isoformat(),
            "pause_time": None
        })
        message = "Stopwatch resumed"
    
    else:
        # Already running
        message = "Stopwatch is already running"
    
    # Calculate current elapsed time
    if stopwatch["state"] == "RUNNING":
        start_time = datetime.fromisoformat(stopwatch["start_time"])
        elapsed_seconds = int((current_time - start_time).total_seconds())
        stopwatch["elapsed_time"] = elapsed_seconds
    
    # Update DB
    DB["stopwatch"] = stopwatch
    
    result = ClockResult(
        message=f"{message}. Elapsed time: {_seconds_to_duration(stopwatch['elapsed_time'])}"
    )
    
    outputs = result.model_dump()
    

    
    return outputs


def show_stopwatch() -> Dict[str, Any]:
    """
    Opens the stopwatch app to show the state of the stopwatch.

    Returns:
        Dict[str, Any]: A dictionary containing the stopwatch status.

    Raises:
        None: This function should not raise exceptions
    """
    current_time = _get_current_time()
    
    # Initialize stopwatch in DB if it doesn't exist
    stopwatch = _initialize_stopwatch()
    
    # Calculate current elapsed time if running
    if stopwatch["state"] == "RUNNING" and stopwatch["start_time"]:
        start_time = datetime.fromisoformat(stopwatch["start_time"])
        elapsed_seconds = int((current_time - start_time).total_seconds())
        stopwatch["elapsed_time"] = elapsed_seconds
    
    # Create status message
    elapsed_duration = _seconds_to_duration(stopwatch["elapsed_time"])
    
    if stopwatch["state"] == "STOPPED":
        message = f"Stopwatch is stopped. Total time: {elapsed_duration}"
    elif stopwatch["state"] == "RUNNING":
        message = f"Stopwatch is running. Elapsed time: {elapsed_duration}"
    elif stopwatch["state"] == "PAUSED":
        message = f"Stopwatch is paused. Elapsed time: {elapsed_duration}"
    else:
        message = f"Stopwatch status: {stopwatch['state']}. Elapsed time: {elapsed_duration}"
    
    # Add lap times if any
    if stopwatch["lap_times"]:
        lap_info = f" Laps: {len(stopwatch['lap_times'])}"
        message += lap_info
    
    # Update DB with current elapsed time
    DB["stopwatch"] = stopwatch
    
    result = ClockResult(
        message=message
    )
    
    outputs = result.model_dump()
    

    
    return outputs


def pause_stopwatch() -> Dict[str, Any]:
    """
    Pauses the stopwatch.

    Returns:
        Dict[str, Any]: A dictionary containing the stopwatch status.

    Raises:
        None: This function should not raise exceptions
    """
    current_time = _get_current_time()
    
    # Initialize stopwatch in DB if it doesn't exist
    stopwatch = _initialize_stopwatch()
    
    if stopwatch["state"] == "RUNNING":
        # Calculate elapsed time and pause
        start_time = datetime.fromisoformat(stopwatch["start_time"])
        elapsed_seconds = int((current_time - start_time).total_seconds())
        
        stopwatch.update({
            "state": "PAUSED",
            "pause_time": current_time.isoformat(),
            "elapsed_time": elapsed_seconds
        })
        message = f"Stopwatch paused at {_seconds_to_duration(elapsed_seconds)}"
    
    elif stopwatch["state"] == "PAUSED":
        message = f"Stopwatch is already paused at {_seconds_to_duration(stopwatch['elapsed_time'])}"
    
    else:
        message = f"Stopwatch is not running. Current state: {stopwatch['state']}"
    
    # Update DB
    DB["stopwatch"] = stopwatch
    
    result = ClockResult(
        message=message
    )
    
    outputs = result.model_dump()



    return outputs


def reset_stopwatch() -> Dict[str, Any]:
    """
    Resets the stopwatch to 00:00:00.

    Returns:
        Dict[str, Any]: A dictionary containing the stopwatch status.

    Raises:
        None: This function should not raise exceptions
    """
    # Reset stopwatch state
    DB["stopwatch"] = {
        "state": "STOPPED",
        "start_time": None,
        "pause_time": None,
        "elapsed_time": 0,
        "lap_times": []
    }
    
    result = ClockResult(
        message="Stopwatch reset to 00:00:00"
    )

    outputs = result.model_dump()


    
    return outputs


def lap_stopwatch() -> Dict[str, Any]:
    """
    Records a lap time for the stopwatch.

    Returns:
        Dict[str, Any]: A dictionary containing the lap information.

    Raises:
        None: This function should not raise exceptions
    """
    current_time = _get_current_time()
    
    # Initialize stopwatch in DB if it doesn't exist
    stopwatch = _initialize_stopwatch()
    
    if stopwatch["state"] == "RUNNING":
        # Calculate current elapsed time
        start_time = datetime.fromisoformat(stopwatch["start_time"])
        elapsed_seconds = int((current_time - start_time).total_seconds())
        
        # Record lap time
        lap_number = len(stopwatch["lap_times"]) + 1
        lap_time = {
            "lap_number": lap_number,
            "lap_time": elapsed_seconds,
            "lap_duration": _seconds_to_duration(elapsed_seconds),
            "timestamp": current_time.isoformat()
        }
        
        # Calculate split time (time since last lap)
        if stopwatch["lap_times"]:
            previous_lap_time = stopwatch["lap_times"][-1]["lap_time"]
            split_seconds = elapsed_seconds - previous_lap_time
            lap_time["split_time"] = split_seconds
            lap_time["split_duration"] = _seconds_to_duration(split_seconds)
        else:
            lap_time["split_time"] = elapsed_seconds
            lap_time["split_duration"] = _seconds_to_duration(elapsed_seconds)
        
        stopwatch["lap_times"].append(lap_time)
        stopwatch["elapsed_time"] = elapsed_seconds
        
        message = f"Lap {lap_number} recorded: {lap_time['split_duration']} (Total: {lap_time['lap_duration']})"
    
    elif stopwatch["state"] == "PAUSED":
        message = "Cannot record lap time while stopwatch is paused. Resume the stopwatch first."
    
    else:
        message = "Cannot record lap time. Stopwatch is not running."
    
    # Update DB
    DB["stopwatch"] = stopwatch
    
    result = ClockResult(
        message=message
    )
    
    outputs = result.model_dump()


    
    return outputs 