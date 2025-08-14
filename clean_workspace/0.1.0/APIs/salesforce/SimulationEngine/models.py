from pydantic import BaseModel, ValidationError, Field, Extra
import datetime # Import datetime if date validation is desired
from typing import Optional, Any, Dict, List # Added List, Dict for completeness, though

class EventUpdateKwargsModel(BaseModel):
    """
    Pydantic model for validating the keyword arguments passed to the update function.
    All fields are optional, reflecting that any subset of these can be provided for an update.
    """
    Subject: Optional[str] = None
    StartDateTime: Optional[str] = None
    EndDateTime: Optional[str] = None
    Description: Optional[str] = None
    Location: Optional[str] = None
    IsAllDayEvent: Optional[bool] = None
    OwnerId: Optional[str] = None
    WhoId: Optional[str] = None
    WhatId: Optional[str] = None

    class Config:
        # Default Pydantic behavior is `extra = 'ignore'`, meaning extra fields in the input data
        # (kwargs, in this case) that are not defined in the model are ignored during parsing.
        # This is suitable here as we want to validate known fields if they are present,
        # but allow other fields to pass through to the original function logic unchanged.
        extra = 'ignore'


# Define the Pydantic model for the 'criteria' dictionary
class TaskCriteriaModel(BaseModel):
    """
    Pydantic model for validating the structure of the 'criteria' dictionary
    used for filtering tasks. All fields are optional.
    """
    Subject: Optional[str] = None
    Priority: Optional[str] = None
    Status: Optional[str] = None
    # Example using str as per docstring. Could use date for stricter validation:
    # ActivityDate: Optional[datetime.date] = None
    ActivityDate: Optional[str] = None

    # Configuration to allow extra fields if the intention is just to validate
    # the known ones but permit others (mimicking flexible dictionary use).
    # If only the defined fields should be allowed, use extra = 'forbid'.
    # If extra fields should be ignored, use extra = 'ignore'.
    # Default Pydantic V2 behavior is 'ignore', which fits well here.
    # class Config:
    #     extra = 'allow' # Or 'ignore' or 'forbid' depending on desired strictness


class EventInputModel(BaseModel):  # type: ignore
    Subject: Optional[str] = None
    StartDateTime: Optional[str] = None
    EndDateTime: Optional[str] = None
    Description: Optional[str] = None
    Location: Optional[str] = None
    IsAllDayEvent: Optional[bool] = None
    OwnerId: Optional[str] = None
    WhoId: Optional[str] = None
    WhatId: Optional[str] = None

    class Config:
        extra = Extra.forbid


class QueryCriteriaModel(BaseModel):
    """
    Pydantic model for validating the 'criteria' dictionary.
    Known keys like 'Subject', 'IsAllDayEvent', and 'StartDateTime'
    are validated for their types if present. Additional keys are allowed.
    """
    Subject: Optional[str] = None
    IsAllDayEvent: Optional[bool] = None
    StartDateTime: Optional[str] = None  # Could be pydantic.AwareDatetime for stricter validation
    EndDateTime: Optional[str] = None

    class Config:
        extra = "allow"  # Allow other keys not explicitly defined in the model

class TaskCreateModel(BaseModel):
    """
    Pydantic model for validating the input keyword arguments for task creation.
    """
    # Required fields
    Priority: str
    Status: str

    # Optional fields
    Subject: Optional[str] = None
    Description: Optional[str] = None
    ActivityDate: Optional[str] = None # Could be pydantic.AwareDatetime or date for stricter validation
    OwnerId: Optional[str] = None
    WhoId: Optional[str] = None
    WhatId: Optional[str] = None
    IsReminderSet: Optional[bool] = None
    ReminderDateTime: Optional[str] = None # Could be pydantic.AwareDatetime for stricter validation
