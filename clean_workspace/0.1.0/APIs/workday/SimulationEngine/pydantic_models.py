from pydantic import BaseModel, Field, validator, ConfigDict
from datetime import datetime, date
from typing import Optional, List, Dict, Any, Union, Literal

# Define allowed states for project state filtering
ALLOWED_PROJECT_STATES = {
    "draft", "requested", "planned", "active", "completed", "canceled", "on_hold"
}

class ProjectFilterModel(BaseModel):
    # Timestamps
    updated_at_from: Optional[datetime] = None
    updated_at_to: Optional[datetime] = None
    marked_as_needs_attention_at_from: Optional[datetime] = None
    marked_as_needs_attention_at_to: Optional[datetime] = None

    # Numeric fields
    number_from: Optional[int] = Field(default=None, ge=0)
    number_to: Optional[int] = Field(default=None, ge=0)

    # String contains/not_contains fields
    title_contains: Optional[str] = None
    title_not_contains: Optional[str] = None
    description_contains: Optional[str] = None
    description_not_contains: Optional[str] = None
    canceled_note_contains: Optional[str] = None
    canceled_note_not_contains: Optional[str] = None
    canceled_reason_contains: Optional[str] = None
    canceled_reason_not_contains: Optional[str] = None
    on_hold_note_contains: Optional[str] = None
    on_hold_note_not_contains: Optional[str] = None
    on_hold_reason_contains: Optional[str] = None
    on_hold_reason_not_contains: Optional[str] = None
    needs_attention_note_contains: Optional[str] = None
    needs_attention_note_not_contains: Optional[str] = None
    needs_attention_reason_contains: Optional[str] = None
    needs_attention_reason_not_contains: Optional[str] = None
    
    # External ID fields
    external_id_empty: Optional[bool] = None
    external_id_not_empty: Optional[bool] = None
    external_id_equals: Optional[str] = None
    external_id_not_equals: Optional[str] = None
    external_id: Optional[str] = None

    # Date fields
    actual_start_date_from: Optional[date] = None
    actual_start_date_to: Optional[date] = None
    actual_end_date_from: Optional[date] = None
    actual_end_date_to: Optional[date] = None
    target_start_date_from: Optional[date] = None
    target_start_date_to: Optional[date] = None
    target_end_date_from: Optional[date] = None
    target_end_date_to: Optional[date] = None

    # Amount fields (float)
    actual_spend_amount_from: Optional[float] = Field(default=None, ge=0)
    actual_spend_amount_to: Optional[float] = Field(default=None, ge=0)
    approved_spend_amount_from: Optional[float] = Field(default=None, ge=0)
    approved_spend_amount_to: Optional[float] = Field(default=None, ge=0)
    estimated_savings_amount_from: Optional[float] = Field(default=None) # Savings can be negative
    estimated_savings_amount_to: Optional[float] = Field(default=None)   # Savings can be negative
    estimated_spend_amount_from: Optional[float] = Field(default=None, ge=0)
    estimated_spend_amount_to: Optional[float] = Field(default=None, ge=0)

    # Boolean-like flags (assumed to be boolean despite (str) in original doc for some)
    canceled_note_empty: Optional[bool] = None
    canceled_note_not_empty: Optional[bool] = None
    canceled_reason_empty: Optional[bool] = None
    canceled_reason_not_empty: Optional[bool] = None
    on_hold_note_empty: Optional[bool] = None
    on_hold_note_not_empty: Optional[bool] = None
    on_hold_reason_empty: Optional[bool] = None
    on_hold_reason_not_empty: Optional[bool] = None
    needs_attention_note_empty: Optional[bool] = None
    needs_attention_note_not_empty: Optional[bool] = None
    needs_attention_reason_empty: Optional[bool] = None
    needs_attention_reason_not_empty: Optional[bool] = None
    
    needs_attention_equals: Optional[bool] = None
    needs_attention_not_equals: Optional[bool] = None # Potentially redundant with needs_attention_equals

    # List of strings for state
    state_equals: Optional[List[str]] = None

    @validator("state_equals", each_item=True, allow_reuse=True)
    def check_state_value(cls, v: str) -> str:
        if v not in ALLOWED_PROJECT_STATES:
            raise ValueError(f"State '{v}' is not a valid project state. Allowed states are: {ALLOWED_PROJECT_STATES}")
        return v

    class Config:
        extra = "forbid"  # Disallow any fields not defined in the model

class PageArgumentModel(BaseModel):
    size: Optional[int] = Field(default=None, gt=0, le=100) # Must be > 0 and <= 100

    class Config:
        extra = "forbid" # Disallow other keys like "offset"


class ProjectAttributesInputModel(BaseModel):
    model_config = ConfigDict(extra='forbid')

    name: Optional[str] = None
    description: Optional[str] = None
    state: Optional[Literal["draft", "requested", "planned", "active", "completed", "canceled", "on_hold"]] = None
    target_start_date: Optional[date] = None
    target_end_date: Optional[date] = None
    actual_spend_amount: Optional[float] = None
    approved_spend_amount: Optional[float] = None
    estimated_savings_amount: Optional[float] = None
    estimated_spend_amount: Optional[float] = None
    canceled_note: Optional[str] = None
    canceled_reason: Optional[str] = None
    on_hold_note: Optional[str] = None
    on_hold_reason: Optional[str] = None
    needs_attention: Optional[bool] = None
    marked_as_needs_attention_at: Optional[datetime] = None
    needs_attention_note: Optional[str] = None
    needs_attention_reason: Optional[str] = None

class ProjectRelationshipsInputModel(BaseModel):
    model_config = ConfigDict(extra='forbid')

    attachments: Optional[List[Dict[str, Any]]] = None
    creator: Optional[Dict[str, Any]] = None
    requester: Optional[Dict[str, Any]] = None
    owner: Optional[Dict[str, Any]] = None
    project_type: Optional[Dict[str, Any]] = None

class ProjectDataInputModel(BaseModel):
    model_config = ConfigDict(extra='forbid')

    type_id: Optional[str] = None
    id: str  # Project identifier string, to be compared with the path `id`
    external_id: Optional[str] = None
    supplier_companies: Optional[List[Dict[str, Any]]] = None
    supplier_contacts: Optional[List[Dict[str, Any]]] = None
    status: Optional[str] = None
    attributes: Optional[ProjectAttributesInputModel] = None
    relationships: Optional[ProjectRelationshipsInputModel] = None
