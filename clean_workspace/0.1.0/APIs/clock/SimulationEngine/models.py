from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Union, Dict, Any
from enum import Enum
import re
from datetime import datetime

class DateRange(BaseModel):
    """Represents a date range. To represent a single date, make start_date and end_date the same."""
    start_date: Optional[str] = Field(None, description="In the format of YYYY-MM-DD. If using start_date, do not use a date in the past.")
    end_date: Optional[str] = Field(None, description="In the format of YYYY-MM-DD. If using end_date, do not use a date in the past.")

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_date_format(cls, v):
        """Validate that the date is in YYYY-MM-DD format."""
        if v is not None:
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Date must be in YYYY-MM-DD format")
        return v

    class Config:
        strict = True


class AlarmFilters(BaseModel):
    """Filters to identify the alarms to be modified."""
    time: Optional[str] = Field(None, description="The time that the alarm will fire, in 12-hour format \"H[:M[:S]]\"")
    label: Optional[str] = Field(None, description="The label of the alarm to filter for")
    date_range: Optional[DateRange] = Field(None, description="Date range to filter alarms")
    alarm_type: Optional[str] = Field(None, description="One of UPCOMING, DISABLED, ACTIVE")
    alarm_ids: Optional[List[str]] = Field(None, description="Alarm ids to filter for")

    @field_validator("alarm_type")
    @classmethod
    def validate_alarm_type(cls, v):
        """Validate alarm type."""
        if v is not None and v not in ["UPCOMING", "DISABLED", "ACTIVE"]:
            raise ValueError("alarm_type must be one of UPCOMING, DISABLED, ACTIVE")
        return v

    class Config:
        strict = True


class AlarmModifications(BaseModel):
    """Modifications to make to the alarms based on the user's request."""
    time: Optional[str] = Field(None, description="New time that the alarm should fire at, in 12-hour format")
    duration_to_add: Optional[str] = Field(None, description="Duration to add to the alarm, e.g. 1h00m00s")
    date: Optional[str] = Field(None, description="Date that the alarm should be updated to, in YYYY-MM-DD format")
    label: Optional[str] = Field(None, description="Label that the alarm should be updated to")
    recurrence: Optional[List[str]] = Field(None, description="Recurrence that the alarm should be updated to")
    state_operation: Optional[str] = Field(None, description="State operation to perform")

    @field_validator("state_operation")
    @classmethod
    def validate_state_operation(cls, v):
        """Validate state operation."""
        if v is not None and v not in ["ENABLE", "DISABLE", "DELETE", "CANCEL", "DISMISS", "STOP", "PAUSE"]:
            raise ValueError("state_operation must be one of ENABLE, DISABLE, DELETE, CANCEL, DISMISS, STOP, PAUSE")
        return v

    @field_validator("recurrence")
    @classmethod
    def validate_recurrence(cls, v):
        """Validate recurrence days."""
        if v is not None:
            valid_days = ["SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"]
            for day in v:
                if day not in valid_days:
                    raise ValueError(f"Invalid recurrence day: {day}")
        return v

    class Config:
        strict = True


class TimerFilters(BaseModel):
    """Filters to identify the timers to be modified."""
    duration: Optional[str] = Field(None, description="Duration of the timer, e.g. 2h00m00s")
    label: Optional[str] = Field(None, description="Label of the timer")
    timer_type: Optional[str] = Field(None, description="One of UPCOMING, PAUSED, RUNNING")
    timer_ids: Optional[List[str]] = Field(None, description="Timer ids to filter for")

    @field_validator("timer_type")
    @classmethod
    def validate_timer_type(cls, v):
        """Validate timer type."""
        if v is not None and v not in ["UPCOMING", "PAUSED", "RUNNING"]:
            raise ValueError("timer_type must be one of UPCOMING, PAUSED, RUNNING")
        return v

    class Config:
        strict = True


class TimerModifications(BaseModel):
    """Modifications to make to the timers based on the user's request."""
    duration: Optional[str] = Field(None, description="Duration that the timer should be updated to")
    duration_to_add: Optional[str] = Field(None, description="Duration to add to the timer")
    label: Optional[str] = Field(None, description="Label that the timer should be updated to")
    state_operation: Optional[str] = Field(None, description="State operation to perform")

    @field_validator("state_operation")
    @classmethod
    def validate_state_operation(cls, v):
        """Validate state operation."""
        if v is not None and v not in ["PAUSE", "RESUME", "RESET", "DELETE", "CANCEL", "DISMISS", "STOP"]:
            raise ValueError("state_operation must be one of PAUSE, RESUME, RESET, DELETE, CANCEL, DISMISS, STOP")
        return v

    class Config:
        strict = True


class Alarm(BaseModel):
    """Represents an alarm."""
    time_of_day: Optional[str] = Field(None, description="Time of day the alarm fires")
    alarm_id: Optional[str] = Field(None, description="Unique identifier for the alarm")
    label: Optional[str] = Field(None, description="Label for the alarm")
    state: Optional[str] = Field(None, description="Current state of the alarm")
    date: Optional[str] = Field(None, description="Date the alarm is scheduled for")
    recurrence: Optional[str] = Field(None, description="Recurrence pattern for the alarm")
    fire_time: Optional[str] = Field(None, description="The ISO timestamp for when the alarm is set to fire")

    class Config:
        strict = True


class Timer(BaseModel):
    """Represents a timer."""
    original_duration: Optional[str] = Field(None, description="Original duration of the timer")
    remaining_duration: Optional[str] = Field(None, description="Remaining duration left on the timer")
    time_of_day: Optional[str] = Field(None, description="Time of day the timer will go off")
    timer_id: Optional[str] = Field(None, description="Unique identifier for the timer")
    label: Optional[str] = Field(None, description="Label for the timer")
    state: Optional[str] = Field(None, description="Current state of the timer")
    fire_time: Optional[str] = Field(None, description="The ISO timestamp for when the timer is set to fire")

    class Config:
        strict = True


class ClockResult(BaseModel):
    """The result of clock operations."""
    message: Optional[str] = Field(None, description="Response message")
    action_card_content_passthrough: Optional[str] = Field(None, description="Action card content")
    card_id: Optional[str] = Field(None, description="Card identifier")
    alarm: Optional[List[Alarm]] = Field(None, description="List of alarms")
    timer: Optional[List[Timer]] = Field(None, description="List of timers")

    class Config:
        strict = True


class AlarmCreationInput(BaseModel):
    """Input model for creating alarms."""
    duration: Optional[str] = Field(None, description="Duration of the alarm")
    time: Optional[str] = Field(None, description="Time of day the alarm should fire")
    date: Optional[str] = Field(None, description="Date the alarm is scheduled for")
    label: Optional[str] = Field(None, description="Label for the alarm")
    recurrence: Optional[List[str]] = Field(None, description="Recurrence pattern")

    @field_validator("recurrence")
    @classmethod
    def validate_recurrence(cls, v):
        """Validate recurrence days."""
        if v is not None:
            valid_days = ["SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"]
            for day in v:
                if day not in valid_days:
                    raise ValueError(f"Invalid recurrence day: {day}")
        return v

    class Config:
        strict = True


class TimerCreationInput(BaseModel):
    """Input model for creating timers."""
    duration: Optional[str] = Field(None, description="Duration of the timer")
    time: Optional[str] = Field(None, description="Time of day the timer should fire")
    label: Optional[str] = Field(None, description="Label for the timer")

    class Config:
        strict = True 