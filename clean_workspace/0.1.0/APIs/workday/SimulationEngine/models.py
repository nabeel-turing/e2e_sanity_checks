from typing import Optional, List, Dict, Any, Literal, Union
from pydantic import BaseModel, Field, ValidationError as PydanticValidationError, conint
from pydantic import field_validator, model_validator, EmailStr
from pydantic.config import ConfigDict
import datetime

class ProjectAttributes(BaseModel):
    name: str
    description: Optional[str] = None
    state: Optional[Literal["draft", "requested", "planned", "active", "completed", "canceled", "on_hold"]] = None
    target_start_date: Optional[datetime.date] = None
    target_end_date: Optional[datetime.date] = None
    actual_spend_amount: Optional[float] = None
    approved_spend_amount: Optional[float] = None
    estimated_savings_amount: Optional[float] = None
    estimated_spend_amount: Optional[float] = None
    canceled_note: Optional[str] = None
    canceled_reason: Optional[str] = None
    on_hold_note: Optional[str] = None
    on_hold_reason: Optional[str] = None
    needs_attention: Optional[bool] = None
    marked_as_needs_attention_at: Optional[datetime.datetime] = None
    needs_attention_note: Optional[str] = None
    needs_attention_reason: Optional[str] = None

    model_config = ConfigDict(extra='forbid')

class ProjectRelationships(BaseModel):
    attachments: Optional[List[Dict[str, Any]]] = None
    creator: Optional[Dict[str, Any]] = None
    requester: Optional[Dict[str, Any]] = None
    owner: Optional[Dict[str, Any]] = None
    project_type: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(extra='forbid')

class ProjectInput(BaseModel):
    type_id: Optional[str] = "projects" # Defaulting as per common practice, but can be overridden
    id: Optional[str] = None
    external_id: Optional[str] = None
    supplier_companies: Optional[List[Dict[str, Any]]] = None
    supplier_contacts: Optional[List[Dict[str, Any]]] = None
    status: Optional[str] = None
    attributes: ProjectAttributes  # 'attributes' object itself is required
    relationships: Optional[ProjectRelationships] = None

    model_config = ConfigDict(extra='forbid')
        

class ScimNameModel(BaseModel):
    """Pydantic model for a user's name components."""
    givenName: str = Field(..., min_length=1)
    familyName: str = Field(..., min_length=1)

    model_config = ConfigDict(extra='forbid')
        
    @field_validator('givenName')
    def validate_given_name(cls, v: str):
        """Validate givenName field."""
        if not isinstance(v, str):
            raise ValueError("givenName must be a string")
        if not v or not v.strip():
            raise ValueError("givenName cannot be empty")
        return v
        
    @field_validator('familyName')
    def validate_family_name(cls, v: str):
        """Validate familyName field."""
        if not isinstance(v, str):
            raise ValueError("familyName must be a string")
        if not v or not v.strip():
            raise ValueError("familyName cannot be empty")
        return v


class RoleModel(BaseModel):
    """SCIM Role sub-attribute object for Users.

    - value: required
    - display, type, primary: optional
    """
    value: str
    display: Optional[str] = None
    type: Optional[str] = None
    primary: Optional[bool] = None

    model_config = ConfigDict(extra='forbid')
        
    @field_validator('value')
    def validate_value(cls, v: str):
        """Validate value field."""
        if not isinstance(v, str):
            raise ValueError("value must be a string")
        if not v or not v.strip():
            raise ValueError("value cannot be empty")
        return v
        
    @field_validator('display')
    def validate_display(cls, v: Optional[str]):
        """Validate display field."""
        if v is not None and not isinstance(v, str):
            raise ValueError("display must be a string")
        return v
        
    @field_validator('type')
    def validate_type(cls, v: Optional[str]):
        """Validate type field."""
        if v is not None and not isinstance(v, str):
            raise ValueError("type must be a string")
        return v
        
    @field_validator('primary', mode='before')
    def validate_primary(cls, v: Optional[bool]):
        """Validate primary field."""
        if v is not None and not isinstance(v, bool):
            raise ValueError("primary must be a boolean")
        return v


class UserScimInputModel(BaseModel):
    """Pydantic model for validating the SCIM user creation request body.

    Matches Workday Strategic Sourcing SCIM 2.0 Create User input. The server generates
    response-only fields like id and meta.
    """
    schemas: Optional[List[str]] = Field(None, description="SCIM schemas, typically ['urn:ietf:params:scim:schemas:core:2.0:User']")
    externalId: Optional[str] = Field(None, description="External identifier for the user")
    userName: EmailStr = Field(..., description="Unique username, typically an email address")
    name: ScimNameModel = Field(..., description="User's name components")
    active: Optional[bool] = Field(True, description="Whether the user account is active")
    roles: Optional[List[RoleModel]] = Field(None, description="Roles assigned to the user")

    model_config = ConfigDict(extra='forbid')
        
    @field_validator('schemas')
    def validate_schemas(cls, v: Optional[List[str]]):
        """Validate that schemas include the required SCIM User schema if provided."""
        if v is not None:
            if not isinstance(v, list):
                raise ValueError("schemas must be a list")
            if len(v) == 0:
                raise ValueError("schemas cannot be empty")
            for schema in v:
                if not isinstance(schema, str):
                    raise ValueError("All schema items must be strings")
            required_schema = "urn:ietf:params:scim:schemas:core:2.0:User"
            if required_schema not in v:
                raise ValueError(f"schemas must include '{required_schema}'")
        return v

    @field_validator('active', mode='before')
    def validate_active(cls, v: Optional[bool]):
        """Validate active field."""
        if v is not None and not isinstance(v, bool):
            raise ValueError("active must be a boolean")
        return v
        
    @field_validator('externalId')
    def validate_external_id(cls, v: Optional[str]):
        """Validate externalId field."""
        if v is not None and not isinstance(v, str):
            raise ValueError("externalId must be a string")
        return v
        
    @field_validator('roles')
    def validate_roles(cls, v: Optional[List[RoleModel]]):
        """Validate roles field."""
        if v is not None and not isinstance(v, list):
            raise ValueError("roles must be a list")
        return v

# Define Literal types for Enums described in the docstring
EventTypeLiteral = Literal[
    "RFP", "AUCTION", "AUCTION_WITH_LOTS", "AUCTION_LOT",
    "PERFORMANCE_REVIEW_EVENT", "PERFORMANCE_REVIEW_SCORE_CARD_ONLY_EVENT",
    "SUPPLIER_REVIEW_EVENT", "SUPPLIER_REVIEW_MASTER_EVENT"
]

EventStateLiteral = Literal[
    "draft", "scheduled", "published", "live_editing", "closed", "canceled"
]

EventDuplicationStateLiteral = Literal[
    "scheduled", "started", "finished", "failed"
]

class EventAttributesInputModel(BaseModel):
    title: Optional[str] = None
    event_type: Optional[EventTypeLiteral] = None
    state: Optional[EventStateLiteral] = None
    duplication_state: Optional[EventDuplicationStateLiteral] = None
    spend_amount: Optional[float] = None
    request_type: Optional[str] = None
    late_bids: Optional[bool] = None
    revise_bids: Optional[bool] = None
    instant_notifications: Optional[bool] = None
    supplier_rsvp_deadline: Optional[str] = None
    supplier_question_deadline: Optional[str] = None
    bid_submission_deadline: Optional[str] = None
    created_at: Optional[str] = None
    closed_at: Optional[str] = None
    published_at: Optional[str] = None
    external_id: Optional[str] = None
    is_public: Optional[bool] = None
    restricted: Optional[bool] = None
    custom_fields: Optional[List[Any]] = None # Docstring implies list, type of items not specified

    model_config = ConfigDict(extra='forbid')

class EventRelationshipsInputModel(BaseModel):
    attachments: Optional[List[Any]] = None # Type of items not specified
    project: Optional[Dict[str, Any]] = None # Structure not detailed, allowing a dictionary
    spend_category: Optional[Dict[str, Any]] = None # Structure not detailed
    event_template: Optional[Dict[str, Any]] = None # Structure not detailed
    commodity_codes: Optional[List[Any]] = None # Type of items not specified

    model_config = ConfigDict(extra='forbid')

class EventInputModel(BaseModel):
    external_id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[EventTypeLiteral] = None
    suppliers: Optional[List[Any]] = None # Type of items not specified
    supplier_contacts: Optional[List[Any]] = None # Type of items not specified
    attributes: Optional[EventAttributesInputModel] = None
    relationships: Optional[EventRelationshipsInputModel] = None

    model_config = ConfigDict(extra='forbid')


# Define Literals for enum-like fields to enforce specific string values
VALID_EVENT_STATES = Literal[
    "draft", "scheduled", "published", "live_editing", "closed", "canceled"
]
VALID_EVENT_TYPES = Literal[
    "RFP", "AUCTION", "AUCTION_WITH_LOTS", "AUCTION_LOT",
    "PERFORMANCE_REVIEW_EVENT", "PERFORMANCE_REVIEW_SCORE_CARD_ONLY_EVENT",
    "SUPPLIER_REVIEW_EVENT", "SUPPLIER_REVIEW_MASTER_EVENT"
]

class EventFilterModel(BaseModel):
    updated_at_from: Optional[str] = None
    updated_at_to: Optional[str] = None
    title_contains: Optional[str] = None
    title_not_contains: Optional[str] = None
    spend_category_id_equals: Optional[List[int]] = None
    state_equals: Optional[List[VALID_EVENT_STATES]] = None
    event_type_equals: Optional[List[VALID_EVENT_TYPES]] = None
    request_type_equals: Optional[List[str]] = None
    supplier_rsvp_deadline_from: Optional[str] = None
    supplier_rsvp_deadline_to: Optional[str] = None
    supplier_rsvp_deadline_empty: Optional[bool] = None
    supplier_rsvp_deadline_not_empty: Optional[bool] = None
    supplier_question_deadline_from: Optional[str] = None
    supplier_question_deadline_to: Optional[str] = None
    supplier_question_deadline_empty: Optional[bool] = None
    supplier_question_deadline_not_empty: Optional[bool] = None
    bid_submission_deadline_from: Optional[str] = None
    bid_submission_deadline_to: Optional[str] = None
    bid_submission_deadline_empty: Optional[bool] = None
    bid_submission_deadline_not_empty: Optional[bool] = None
    created_at_from: Optional[str] = None
    created_at_to: Optional[str] = None
    published_at_from: Optional[str] = None
    published_at_to: Optional[str] = None
    published_at_empty: Optional[bool] = None
    published_at_not_empty: Optional[bool] = None
    closed_at_from: Optional[str] = None
    closed_at_to: Optional[str] = None
    closed_at_empty: Optional[bool] = None
    closed_at_not_empty: Optional[bool] = None
    spend_amount_from: Optional[float] = None
    spend_amount_to: Optional[float] = None
    spend_amount_empty: Optional[bool] = None
    spend_amount_not_empty: Optional[bool] = None
    external_id_empty: Optional[bool] = None
    external_id_not_empty: Optional[bool] = None
    external_id_equals: Optional[str] = None
    external_id_not_equals: Optional[str] = None

    model_config = ConfigDict(extra='forbid')

class PaginationModel(BaseModel):
    size: Optional[conint(ge=1, le=100)] = None # Value must be between 1 and 100, inclusive. Optional.

    model_config = ConfigDict(extra='forbid')


class PatchOperationModel(BaseModel):
    """SCIM PATCH operation model for individual patch operations."""
    op: Literal["add", "remove", "replace"] = Field(..., description="The kind of operation to perform")
    path: Optional[str] = Field(None, description="Required when op is remove, optional otherwise")
    value: Optional[Union[str, int, float, bool, Dict[str, Any], List[Any]]] = Field(None, description="Can be any value - string, number, boolean, array or object")

    model_config = ConfigDict(extra='forbid')

    @model_validator(mode='after')
    def validate_remove_requires_path(self):
        """Validate that path is required when op is remove."""
        if self.op == 'remove' and not self.path:
            raise ValueError("path is required when op is 'remove'")
        return self


class UserPatchInputModel(BaseModel):
    """Pydantic model for validating SCIM PATCH user request body."""
    schemas: Optional[List[str]] = Field(None, description="Array of strings - SCIM schemas")
    Operations: List[PatchOperationModel] = Field(..., description="Array of objects (PatchOperation) - required")

    model_config = ConfigDict(extra='forbid')


class UserReplaceInputModel(BaseModel):
    """Pydantic model for validating SCIM PUT user request body.
    
    For PUT operations, only provided attributes are replaced. Missing attributes remain unchanged.
    """
    externalId: Optional[str] = Field(default=None, description="External identifier for the user")
    userName: EmailStr = Field(..., description="Unique username, typically an email address")
    name: ScimNameModel = Field(..., description="Required. User's name components")
    active: Optional[bool] = Field(default=None, description="Whether the user account is active")

    model_config = ConfigDict(extra='forbid')
        
    @field_validator('active', mode='before')
    def validate_active(cls, v: Optional[bool]):
        """Validate active field."""
        if v is not None and not isinstance(v, bool):
            raise ValueError("active must be a boolean")
        return v
        
    @field_validator('externalId')
    def validate_external_id(cls, v: Optional[str]):
        """Validate externalId field."""
        if v is not None and not isinstance(v, str):
            raise ValueError("externalId must be a string")
        return v
