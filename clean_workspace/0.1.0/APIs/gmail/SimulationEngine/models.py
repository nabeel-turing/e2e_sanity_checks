from typing import Optional, Dict, Any, Literal, List
from pydantic import BaseModel, Field, ValidationError, EmailStr, validator, field_validator
from datetime import datetime
import re



class MessageUpdateModel(BaseModel):
    """
    Pydantic model for the 'message' part of the draft update.
    All fields are optional as this model represents an update payload.
    """
    id: Optional[str] = None
    threadId: Optional[str] = None
    raw: Optional[str] = None
    labelIds: Optional[List[str]] = None
    snippet: Optional[str] = None
    historyId: Optional[str] = None
    internalDate: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    sizeEstimate: Optional[int] = None
    # Compatibility fields
    sender: Optional[str] = None
    recipient: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    isRead: Optional[bool] = None


class ColorInputModel(BaseModel):
    """
    Pydantic model for the 'color' dictionary.
    """
    textColor: str  # Docstring: "The text color of the label, represented as hex string."
    backgroundColor: str = Field(pattern=r"^#[0-9a-fA-F]{6}$") # Docstring: "The background color represented as hex string #RRGGBB."

class LabelInputModel(BaseModel):
    """
    Pydantic model for the 'label' input dictionary.
    """
    name: Optional[str] = None
    messageListVisibility: Literal['show', 'hide'] = 'show'
    labelListVisibility: Literal['labelShow', 'labelShowIfUnread', 'labelHide'] = 'labelShow'
    type: Literal['user', 'system'] = 'user' # Original code allowed 'system', Pydantic model reflects this
    color: Optional[ColorInputModel] = None
    

class ProfileInputModel(BaseModel):
    """
    Pydantic model for validating the 'profile' argument of createUser.
    Ensures 'emailAddress' is present and is a valid email string.
    Other fields in the input 'profile' dictionary will be ignored (Pydantic's default behavior).
    """
    emailAddress: EmailStr

class AttachmentModel(BaseModel):
    """
    Pydantic model for validating attachment objects in messages and drafts.
    Represents the enhanced attachment schema with embedded file content.
    """
    attachmentId: str = Field(..., description="Unique identifier for the attachment")
    filename: str = Field(..., description="Name of the attached file")
    fileSize: int = Field(..., ge=0, description="Size of the file in bytes")
    mimeType: str = Field(..., description="MIME type of the file")
    data: str = Field(..., description="Base64-encoded file content")
    checksum: str = Field(..., pattern=r"^sha256:[a-fA-F0-9]{64}$", description="SHA256 checksum of the file")
    uploadDate: str = Field(..., description="ISO 8601 formatted upload timestamp")
    encoding: Literal["base64"] = Field(default="base64", description="Encoding format for the data field")
    
    @validator('mimeType')
    def validate_mime_type(cls, v):
        """Validate MIME type format"""
        mime_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9!#$&\-\^_]*\/[a-zA-Z0-9][a-zA-Z0-9!#$&\-\^_.]*$'
        if not re.match(mime_pattern, v):
            raise ValueError(f'Invalid MIME type format: {v}')
        return v
    
    @validator('uploadDate')
    def validate_upload_date(cls, v):
        """Validate ISO 8601 date format"""
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError(f'Invalid ISO 8601 date format: {v}')
        return v
    
    @validator('filename')
    def validate_filename(cls, v):
        """Validate filename doesn't contain invalid characters"""
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        if any(char in v for char in invalid_chars):
            raise ValueError(f'Filename contains invalid characters: {v}')
        if not v.strip():
            raise ValueError('Filename cannot be empty or whitespace only')
        return v.strip()

    class Config:
        extra = 'forbid'  # Don't allow extra fields


class LegacyAttachmentModel(BaseModel):
    """
    Pydantic model for legacy attachment objects (filename only).
    Used for backward compatibility with existing simple attachment structure.
    """
    filename: str = Field(..., description="Name of the attached file")
    
    @validator('filename')
    def validate_filename(cls, v):
        """Validate filename is not empty"""
        if not v or not v.strip():
            raise ValueError('Filename cannot be empty')
        return v.strip()

    class Config:
        extra = 'allow'  # Allow extra fields for flexibility


class MessageContentModel(BaseModel):
    """
    Pydantic model for the 'message' object within the draft input.
    Fields are derived from the docstring's description of 'draft.message'
    and supplemented by fields observed in the original function's logic
    accessing 'message_input'.
    """
    threadId: Optional[str] = None
    raw: Optional[str] = None
    internalDate: Optional[str] = None
    labelIds: Optional[List[str]] = Field(default_factory=list) # Docstring: "List[str]", original code: .get('labelIds', [])
    snippet: Optional[str] = None  # Docstring: "str, optional"
    historyId: Optional[str] = None # Docstring: "str, optional"
    payload: Optional[Dict[str, Any]] = Field(default_factory=dict) # Docstring: "Dict[str, Any], optional", original code: .get('payload', {})
    sizeEstimate: Optional[int] = None # Docstring: "int, optional", original code: .get('sizeEstimate', 0)
    sender: Optional[str] = None
    recipient: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    isRead: Optional[bool] = None # Original code: .get('isRead', False)
    date: Optional[str] = None   # Original code: .get('date', '')

class DraftInputPydanticModel(BaseModel):
    """
    Pydantic model for the main 'draft' input dictionary.
    """
    # Field explicitly described in docstring for draft input
    id: Optional[str] = None  # Docstring: "'id' (str, optional)"

    # Field 'message' is required in the draft dictionary if 'draft' itself is provided,
    # as per docstring: "'message'(str, required)".
    message: MessageContentModel


class DraftUpdateInputModel(BaseModel):
    """
    Pydantic model for the 'draft' input dictionary.
    """
    message: Optional[MessageUpdateModel] = None
    class Config:
        extra = "allow"
        

class MessagePayloadModel(BaseModel):
    """
    Pydantic model for validating the 'msg' dictionary structure.
    All fields are optional, reflecting that they may or may not be present
    in the input `msg` dictionary.
    """
    threadId: Optional[str] = None
    raw: Optional[str] = None
    sender: Optional[str] = None
    recipient: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    date: Optional[str] = None  # Expected as ISO 8601 string if provided
    internalDate: Optional[str] = None  # Expected as a string Unix timestamp if provided
    isRead: Optional[bool] = None
    labelIds: Optional[List[str]] = None

    class Config:
        extra = 'forbid' # Forbid any extra fields not defined in the model

        
class GetFunctionArgsModel(BaseModel):
    """Pydantic model for validating arguments passed to the 'get' function."""
    userId: str
    id: str
    # Using 'format_param' as field name because 'format' can conflict with method names.
    # The alias 'format' allows the function to be called with 'format' as the keyword argument.
    format_param: str = Field(alias="format")
    metadata_headers: Optional[List[str]] = None

    @validator('format_param')
    def format_param_must_be_valid(cls, value: str) -> str:
        """Validates the 'format' parameter against allowed values."""
        allowed_formats = ['minimal', 'full', 'raw', 'metadata']
        if value not in allowed_formats:
            raise ValueError(f"format must be one of: {', '.join(allowed_formats)}")
        return value

    @validator('metadata_headers',  always=True)
    def check_metadata_headers_elements(cls, v: Optional[List[Any]]) -> Optional[List[str]]:
        """Validates that all elements in metadata_headers are strings, if the list is provided."""
        if v is None:
            return None
        if not isinstance(v, list):
            # This case should ideally be caught by Pydantic's list type check first,
            # but an explicit check can provide a more specific error if needed.
            raise TypeError("metadata_headers must be a list of strings or None.")
        for item in v:
            if not isinstance(item, str):
                raise ValueError("All elements in metadata_headers must be strings.")
        return v

    class Config:
        # Allow Pydantic to work with parameter names like 'format' by using aliases.
        allow_population_by_field_name = True
        # Forbid extra fields not defined in the model
        extra = 'forbid'

        
class MessageSendPayloadModel(BaseModel):
    """
    Pydantic model for validating the 'msg' dictionary in the send function.
    All fields are optional, aligning with the original function's .get() usage.
    """
    threadId: Optional[str] = None
    raw: Optional[str] = None
    sender: Optional[str] = None
    recipient: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    date: Optional[str] = None
    internalDate: Optional[str] = None
    isRead: Optional[bool] = None
    labelIds: Optional[List[str]] = None

    class Config:
        extra = 'allow' # Allow extra fields as the original function uses .get() for known fields        

class GmailMessageForSearch(BaseModel):
    id: Optional[str] = None
    userId: Optional[str] = None
    threadId: Optional[str] = None
    sender: Optional[str] = None
    recipient: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    labelIds: Optional[List[str]] = None

class GmailMessageForDraftSearch(BaseModel):
    id: Optional[str] = None
    threadId: Optional[str] = None
    sender: Optional[str] = None
    recipient: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    labelIds: Optional[List[str]] = None

class GmailDraftForSearch(BaseModel):
    id: Optional[str] = None
    userId: Optional[str] = None
    message: GmailMessageForDraftSearch

class SendAsCreatePayloadModel(BaseModel):
    """
    Pydantic model for validating the 'send_as' dictionary in SendAs create function.
    All fields are optional, aligning with the original function's .get() usage.
    """
    sendAsEmail: Optional[EmailStr] = None
    displayName: Optional[str] = None
    replyToAddress: Optional[EmailStr] = None
    signature: Optional[str] = None
    
    @validator('displayName', 'signature')
    def validate_string_fields(cls, v):
        if v is not None and not isinstance(v, str):
            raise ValueError('Field must be a string')
        return v

    class Config:
        extra = 'allow' # Allow extra fields for future extensibility


class ImapSettingsInputModel(BaseModel):
    """
    Pydantic model for validating the 'imap_settings' dictionary in updateImap function.
    All fields are optional as this is for updating existing settings.
    """
    enabled: Optional[bool] = None
    autoExpunge: Optional[bool] = None
    expungeBehavior: Optional[str] = None
    
    @validator('expungeBehavior')
    def validate_expunge_behavior(cls, v):
        if v is not None:
            allowed_behaviors = ['expungeBehaviorUnspecified', 'archive', 'trash', 'deleteForever']
            if v not in allowed_behaviors:
                raise ValueError(f'expungeBehavior must be one of: {", ".join(allowed_behaviors)}')
        return v

    class Config:
        extra = 'forbid'  # No extra parameters allowed in the dict

class AutoForwardingSettingsModel(BaseModel):
    """
    Pydantic model for validating auto-forwarding settings dictionary.
    All fields are optional for update operations.
    """
    enabled: Optional[bool] = None
    emailAddress: Optional[EmailStr] = None
    disposition: Optional[Literal['dispositionUnspecified', 'leaveInInbox', 'archive', 'trash', 'markRead']] = None

    @field_validator('enabled', mode='before')
    @classmethod
    def validate_enabled(cls, v):
        if v is not None and not isinstance(v, bool):
            raise ValueError('enabled must be a boolean value')
        return v

    @validator('emailAddress')
    def validate_email_address(cls, v):
        if v is not None and not v.strip():
            raise ValueError('emailAddress cannot be empty or contain only whitespace')
        return v

    class Config:
        extra = 'forbid'  # Only allow defined fields

        
