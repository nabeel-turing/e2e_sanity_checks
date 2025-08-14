from typing import Optional, List, Dict, Any
from pydantic import (
    BaseModel, 
    ConfigDict, 
    Field, 
    validator, 
    ValidationError, 
    field_validator, 
    EmailStr, 
    TypeAdapter
)
import json
from datetime import datetime
validate_email = lambda email: TypeAdapter(EmailStr).validate_python(email)


class AddReminderInput(BaseModel):
    user_id: str = Field(..., min_length=1, description="User ID to remind. Cannot be empty.")
    text: str = Field(..., min_length=1, description="The content of the reminder. Cannot be empty.")
    ts: str = Field(..., min_length=1, description="When this reminder should happen (unix timestamp as string). Cannot be empty.")
    channel_id: Optional[str] = Field(None, description="Channel ID to remind in. Can be None. If a string is provided, it can be empty.")

    @validator("ts")
    def validate_timestamp_format(cls, value: str) -> str:
        """Ensures 'ts' is a string representing a number, parsable by int(float())."""
        # The field 'ts' is already confirmed by Pydantic to be a string and non-empty (due to min_length=1)
        # before this validator runs for string-based checks.
        try:
            int(float(value))  # Original logic allowed float strings then converted to int
        except ValueError:
            # This ValueError will be wrapped by Pydantic into a ValidationError,
            # providing context about which field failed.
            raise ValueError("must be a string representing a valid numeric timestamp (e.g., '1678886400' or '1678886400.5')")
        return value

class ParsedMetadataModel(BaseModel):
    """
    Represents the expected structure of the parsed 'metadata' JSON string.
    """
    event_type: str
    event_payload: Dict[str, Any]

class ScheduleMessageInputModel(BaseModel):
    """
    Pydantic model for validating the input arguments of the scheduleMessage function.
    """
    user_id: str = Field(..., min_length=1, description="User ID, cannot be empty.")
    channel: str = Field(..., min_length=1, description="Channel to send the message to, cannot be empty.")
    post_at: int # Validated by a custom validator to match original logic and ensure it's positive.

    attachments: Optional[str] = None
    blocks: Optional[List[Dict[str, Any]]] = None
    text: Optional[str] = None
    as_user: bool = False
    link_names: bool = False
    markdown_text: Optional[str] = None
    metadata: Optional[str] = None # Custom validator will parse and check internal structure.
    parse: Optional[str] = None
    reply_broadcast: bool = False
    thread_ts: Optional[str] = None
    unfurl_links: bool = True
    unfurl_media: bool = False

    @validator('post_at', pre=True, always=True)
    def validate_and_coerce_post_at(cls, v):
        if v is None:
            raise ValueError("Invalid format or value for post_at: None")

        if isinstance(v, (int, float)) and v <= 0:
             raise ValueError("post_at must be a positive timestamp")

        try:
            # Replicate original int(float(val)) coercion
            val_float = float(v)
            val_int = int(val_float)
            if val_int <= 0: # Check after successful coercion
                raise ValueError("post_at must be a positive timestamp")
            return val_int
        except (ValueError, TypeError) as e: # Handles float conversion error or int conversion error
            raise ValueError(f"Invalid format or value for post_at: {v}")


    @validator('attachments')
    def validate_attachments_string_is_json_array_of_objects(cls, v: Optional[str]):
        if v is not None:
            try:
                data = json.loads(v)
                if not isinstance(data, list):
                    raise ValueError("Attachments JSON string must decode to an array")
                for item in data:
                    if not isinstance(item, dict):
                        raise ValueError("Each item in the attachments array must be an object")
                # If AttachmentItemModel had specific fields, validation would be:
                # [AttachmentItemModel(**item) for item in data]
            except json.JSONDecodeError as e:
                raise ValueError("Attachments string is not valid JSON")
            # ValidationError would be caught if AttachmentItemModel was used and failed
        return v

    @validator('metadata')
    def validate_metadata_string_is_json_object_with_structure(cls, v: Optional[str]):
        if v is not None:
            try:
                data = json.loads(v)
                if not isinstance(data, dict): # Ensure it's an object, not array/scalar
                    raise ValueError("Metadata JSON string must decode to an object")
                # Use a try-except to get a simpler error message format
                try:
                    ParsedMetadataModel(**data) # Validate against the specific structure
                except ValidationError:
                    raise ValueError("Metadata JSON structure is invalid")
            except json.JSONDecodeError as e:
                raise ValueError("Metadata string is not valid JSON")
        return v

    # Add validators for user_id and channel to provide simple error messages
    @validator('user_id')
    def validate_user_id(cls, v):
        if not v:  # Empty string check (min_length should handle this, but for clarity)
            raise ValueError("String should have at least 1 character")
        return v

    @validator('channel')
    def validate_channel(cls, v):
        if not v:  # Empty string check (min_length should handle this, but for clarity)
            raise ValueError("String should have at least 1 character")
        return v

    @validator('blocks', each_item=True)
    def validate_blocks_items(cls, v):
        if not isinstance(v, dict):
            # Use manual error message to match test expectations
            raise ValueError("Input should be a valid dictionary")
        return v

    class Config:
        # Fail if extra fields are passed that are not defined in the model
        extra = "forbid"
        # This makes error messages simpler, matching test expectations better
        error_msg_templates = {
            "string_too_short": "String should have at least 1 character"
        }

class BlockItemStructure(BaseModel):
    """
    Represents the expected structure for an individual item within the 'blocks' list.
    As the specific structure of a block is not detailed in the original docstring,
    this model is configured to allow any fields. A more specific application
    might define concrete fields like 'type: str', 'text: dict', etc.
    """

    class Config:
        # For Pydantic V1:
        extra = "allow"
        # For Pydantic V2, you would use:
        # from pydantic import ConfigDict
        # model_config = ConfigDict(extra='allow')



class DeleteMessageInput(BaseModel):
    channel: str
    ts: str

    @field_validator("channel", mode="before")
    def validate_channel(cls, v):
        if not v:
            raise ValueError("channel is required")
        if not isinstance(v, str):
            raise ValueError("channel must be a string")
        return v

    @field_validator("ts", mode="before")
    def validate_ts(cls, v):
        if not v:
            raise ValueError("ts is required")
        if not isinstance(v, str):
            raise ValueError("ts must be a string")
        
        try:
            ts_float = float(v)
        except ValueError:
            raise ValueError("ts must be a string representing a number")

        if ts_float < 0:
            raise ValueError("ts must be a positive Unix timestamp")

        try:
            datetime.fromtimestamp(ts_float)  # Validates it is a valid timestamp
        except (OverflowError, OSError):
            raise ValueError("ts is not a valid Unix timestamp")

        return v

    model_config = ConfigDict(
        use_enum_values=True,
        extra="forbid",  # Forbid unexpected fields
    )



class DeleteMessageResponse(BaseModel):
    ok: bool
    channel: Optional[str] = None
    ts: Optional[str] = None

    model_config = ConfigDict(
        strict=True,
        use_enum_values=True,
        extra="forbid",
    )


class DeleteScheduledMessageInput(BaseModel):
    channel: str
    scheduled_message_id: str

    @field_validator("channel", mode="before")
    def validate_channel(cls, v):
        if not v:
            raise ValueError("channel is required")
        if not isinstance(v, str):
            raise ValueError("channel must be a string")
        return v

    @field_validator("scheduled_message_id", mode="before")
    def validate_scheduled_message_id(cls, v):
        if not v:
            raise ValueError("scheduled_message_id is required")
        if not isinstance(v, str):
            raise ValueError("scheduled_message_id must be a string")
        return v
    

    model_config = ConfigDict(
        use_enum_values=True,
        extra="forbid",
    )


class DeleteScheduledMessageResponse(BaseModel):
    ok: bool
    channel: Optional[str] = None
    scheduled_message_id: Optional[str] = None

    model_config = ConfigDict(
        strict=True,
        use_enum_values=True,
        extra="forbid",
    )


class UserProfile(BaseModel):
    """Model for user profile data."""
    display_name: Optional[str] = Field(None, description="The user's display name")
    real_name: Optional[str] = Field(None, description="The user's real name")
    email: Optional[str] = Field(None, description="The user's email address")
    phone: Optional[str] = Field(None, description="The user's phone number")
    status_emoji: Optional[str] = Field(None, description="The user's status emoji")
    status_text: Optional[str] = Field(None, description="The user's status text")
    title: Optional[str] = Field(None, description="The user's title")
    team: Optional[str] = Field(None, description="The user's team")
    skype: Optional[str] = Field(None, description="The user's Skype handle")
    first_name: Optional[str] = Field(None, description="The user's first name")
    last_name: Optional[str] = Field(None, description="The user's last name")

    class Config:
        extra = "forbid"  # Reject extra fields

    @validator('email')
    def validate_email(cls, v):
        if v is not None and '@' not in v:
            raise ValueError('Invalid email format')
        return v

    @validator('phone')
    def validate_phone(cls, v):
        if v is not None and not v.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise ValueError('Invalid phone number format')
        return v

class FileInfo(BaseModel):
    """Pydantic model for file information in finish_external_upload requests."""
    id: str = Field(..., description="The ID of the file")
    title: Optional[str] = Field(None, description="The title of the file")
    # Add other optional fields as needed

class FinishExternalUploadRequest(BaseModel):
    """Pydantic model for finish_external_upload request parameters."""
    files: List[FileInfo] = Field(..., description="List of file objects to upload")
    channel_id: Optional[str] = Field(None, description="Channel ID where the file will be shared")
    initial_comment: Optional[str] = Field(None, description="Initial comment for the file")
    thread_ts: Optional[str] = Field(None, description="Parent message timestamp for threading")

class SlackMessageForSearch(BaseModel):
    """Model for Slack messages adapted for search indexing."""
    ts: str
    text: str
    user: str
    channel: str
    channel_name: Optional[str] = None
    reactions: Optional[List[Dict[str, Any]]] = None
    is_starred: Optional[bool] = False
    links: Optional[List[str]] = None
    
    class Config:
        extra = "allow"


class SlackFileForSearch(BaseModel):
    """Model for Slack files adapted for search indexing."""
    id: str
    name: str
    title: Optional[str] = None
    filetype: str
    channels: List[str]
    is_starred: Optional[bool] = False
    
    class Config:
        extra = "allow"
