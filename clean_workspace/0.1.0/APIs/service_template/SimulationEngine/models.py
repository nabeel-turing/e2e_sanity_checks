"""
Pydantic Models for the Generic Service

This module defines the data structures for the service using Pydantic, ensuring
data validation and consistency across the API, the simulation engine, and the
database.
"""

from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, validator
from enum import Enum
import uuid

# ---------------------------
# Enum Types
# ---------------------------

class EntityStatus(str, Enum):
    """An example enum for the status of an entity."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"

# ---------------------------
# Input Validation Models
# ---------------------------

class ComplexInput(BaseModel):
    """
    Defines the structure for a complex dictionary input parameter.
    This model is used to validate the structure and types of the data within
    the dictionary passed to a tool.
    """
    config_name: str = Field(..., description="A required configuration name.", min_length=1)
    value: int = Field(..., description="A numerical value for the configuration.", gt=0)
    enabled: bool = Field(default=True, description="A flag to enable or disable this configuration.")

# ---------------------------
# API Response Models
# ---------------------------

class ToolResponseData(BaseModel):
    """
    Defines the structure of the 'data' object within the main tool response.
    This ensures the data payload of the response is consistent.
    """
    entity_id: str = Field(..., description="The ID of the entity that was affected.")
    params_received: Dict[str, Any] = Field(..., description="A dictionary reflecting the parameters that were received by the tool.")

class ToolResponse(BaseModel):
    """
    The specific response model for the main 'tool' function.
    This defines the exact top-level structure of the JSON returned to the user.
    """
    success: bool = Field(..., description="Indicates whether the operation was successful.")
    message: str = Field(..., description="A descriptive message about the outcome.")
    data: ToolResponseData = Field(..., description="The structured data payload of the response.")

# ---------------------------
# Internal Storage Models
# ---------------------------

class EntityStorage(BaseModel):
    """Internal storage model for an entity."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    status: EntityStatus = Field(default=EntityStatus.ACTIVE)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @validator('id')
    def validate_id_format(cls, v: str) -> str:
        """Ensures the ID is a valid UUID4 string."""
        if not v.strip():
            raise ValueError('ID cannot be an empty string')
        try:
            uuid.UUID(v, version=4)
        except ValueError:
            raise ValueError('ID must be a valid UUID4 string')
        return v

# ---------------------------
# Root Database Model
# ---------------------------

class GenericServiceDB(BaseModel):
    """
    The root model for the entire database. It validates the structure of all
    tables and their contents.
    """
    entities: Dict[str, EntityStorage] = Field(default_factory=dict)
    # The 'actions' table has been removed for a more generic template.
    # If you need to audit tool calls, you can add:
    # actions: List[Action] = Field(default_factory=list)
    # ...and define the Action model accordingly.

    class Config:
        str_strip_whitespace = True