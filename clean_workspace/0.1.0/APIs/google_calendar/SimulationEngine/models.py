import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List, Dict, Any, Literal
from pydantic import Field, ValidationError
from .recurrence_validator import validate_recurrence_rules

class CalendarListResourceInput(BaseModel):
    """
    Pydantic model for validating the 'resource' input dictionary
    for creating a calendar list entry.
    """
    
    model_config = ConfigDict(extra="forbid")
    
    id: Optional[str] = None
    summary: str
    description: str = None
    timeZone: str = None
    primary: bool = False

class ConferencePropertiesModel(BaseModel):
    """
    Pydantic model for conference-related properties.
    """
    allowedConferenceSolutionTypes: Optional[List[Literal["eventHangout", "eventNamedHangout", "hangoutsMeet"]]] = None

class CalendarResourceInputModel(BaseModel):
    """
    Pydantic model for the input 'resource' dictionary.
    """
    id: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    timeZone: Optional[str] = None
    location: Optional[str] = None
    etag: Optional[str] = None
    kind: Optional[Literal["calendar#calendar"]] = None
    conferenceProperties: Optional[ConferencePropertiesModel] = None

class EventDateTimeModel(BaseModel):
    """
    Pydantic model for event start/end times.
    """
    dateTime: str = Field(..., description="ISO 8601 datetime string (YYYY-MM-DDTHH:MM:SSZ)")
    timeZone: Optional[str] = None

    @field_validator('dateTime')
    @classmethod
    def validate_datetime_format(cls, v):
        """Validate that dateTime follows ISO 8601 format with Z suffix."""
        if not v:
            raise ValueError("dateTime cannot be empty")

        # Check for ISO 8601 format with Z suffix (UTC)
        iso_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
        if not re.match(iso_pattern, v):
            raise ValueError("dateTime must be in ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ")

        # Validate that it's a valid datetime
        try:
            datetime.strptime(v, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError as e:
            raise ValueError(f"Invalid datetime: {e}")

        return v

    class Config:
        extra = "allow"  # Allow other fields as base type is Dict[str, Any]

class AttendeeModel(BaseModel):
    """Pydantic model for an event attendee."""
    email: Optional[str] = None
    displayName: Optional[str] = None
    organizer: Optional[bool] = None
    self: Optional[bool] = None # Field name 'self' needs alias for Pydantic model if it conflicts
    resource: Optional[bool] = None
    optional: Optional[bool] = None
    responseStatus: Optional[str] = None
    comment: Optional[str] = None
    additionalGuests: Optional[int] = None

    class Config:
        extra = "allow" # Allow other fields as base type is Dict[str, Any]
        
class ReminderOverrideModel(BaseModel):
    """Pydantic model for reminder overrides."""
    method: Optional[str] = None
    minutes: Optional[int] = None

    class Config:
        extra = "allow"

class RemindersModel(BaseModel):
    """Pydantic model for event reminders."""
    useDefault: Optional[bool] = None
    overrides: Optional[List[ReminderOverrideModel]] = None

    class Config:
        extra = "allow" # Allow other fields as base type is Dict[str, Any]

class AttachmentModel(BaseModel):
    """Pydantic model for an event attachment."""
    fileUrl: str

class ExtendedPropertiesModel(BaseModel):
    """Pydantic model for extended properties."""
    private: Optional[Dict[str, Any]] = None
    shared: Optional[Dict[str, Any]] = None

    class Config:
        extra = "forbid"

class EventResourceInputModel(BaseModel):
    """
    Pydantic model for validating the 'resource' argument of the create_event function.
    """
    id: Optional[str] = None
    summary: str
    description: Optional[str] = None
    start: EventDateTimeModel = Field(..., description="Event start time")
    end: EventDateTimeModel = Field(..., description="Event end time")
    recurrence: Optional[List[str]] = None
    attendees: Optional[List[AttendeeModel]] = None
    reminders: Optional[RemindersModel] = None
    location: Optional[str] = None
    attachments: Optional[List[AttachmentModel]] = None
    extendedProperties: Optional[ExtendedPropertiesModel] = None

    @field_validator('recurrence')
    @classmethod
    def validate_recurrence(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """
        Validates recurrence rules using the RecurrenceValidator.
        
        Args:
            v: List of recurrence rule strings or None
            
        Returns:
            The validated recurrence rules
            
        Raises:
            ValueError: If any rule is invalid
        """
        if v is not None:
            try:
                validate_recurrence_rules(v)
            except Exception as e:
                raise ValueError(str(e))
        return v

    class Config:
        extra = "forbid"

class EventPatchResourceModel(BaseModel):
    """Pydantic model for the 'resource' argument of patch_event."""
    summary: Optional[str] = None
    description: Optional[str] = None
    start: Optional[EventDateTimeModel] = None
    end: Optional[EventDateTimeModel] = None
    attendees: Optional[List[AttendeeModel]] = None
    location: Optional[str] = None
    recurrence: Optional[List[str]] = None
    reminders: Optional[RemindersModel] = None
    attachments: Optional[List[AttachmentModel]] = None

    @field_validator('recurrence')
    @classmethod
    def validate_recurrence(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """
        Validates recurrence rules using the RecurrenceValidator.
        
        Args:
            v: List of recurrence rule strings or None
            
        Returns:
            The validated recurrence rules
            
        Raises:
            ValueError: If any rule is invalid
        """
        if v is not None:
            try:
                validate_recurrence_rules(v)
            except Exception as e:
                raise ValueError(str(e))
        return v

    class Config:
        extra = "forbid" # Disallow any fields in 'resource' not defined in this model
