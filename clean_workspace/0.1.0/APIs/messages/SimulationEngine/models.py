from typing import Any, Dict, Optional, List, Literal, Union
from pydantic import BaseModel, Field, ValidationError, field_validator
from datetime import datetime
from enum import Enum
from .custom_errors import (
    InvalidRecipientError,
    MessageBodyRequiredError,
    InvalidPhoneNumberError,
    InvalidMediaAttachmentError
)
import re


class APIName(str, Enum):
    """Enumeration of API action types for messages."""

    SEND_CHAT_MESSAGE = "send_chat_message"
    PREPARE_CHAT_MESSAGE = "prepare_chat_message"
    SHOW_MESSAGE_RECIPIENT_CHOICES = "show_message_recipient_choices"
    ASK_FOR_MESSAGE_BODY = "ask_for_message_body"
    SHOW_MESSAGE_RECIPIENT_NOT_FOUND_OR_SPECIFIED = "show_message_recipient_not_found_or_specified"


class Action(BaseModel):
    """An action record for message operations."""

    action_type: APIName = Field(..., description="The type of action performed")
    inputs: Dict[str, Any] = Field(
        default_factory=dict, description="Input parameters for the action"
    )
    outputs: Dict[str, Any] = Field(
        default_factory=dict, description="Output results from the action"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata about the action"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="When the action occurred",
    )
    message_id: Optional[str] = Field(
        None, description="ID of the message affected by this action"
    )

    @field_validator("timestamp")
    def validate_timestamp(cls, v):
        """Validate timestamp format."""
        if v:
            try:
                datetime.fromisoformat(v.replace("Z", "+00:00"))
            except ValueError:
                raise ValueError("Timestamp must be in ISO format")
        return v


class Endpoint(BaseModel):
    """
    Represents one single phone number corresponding to a user.
    """
    endpoint_type: str = Field(
        default="PHONE_NUMBER", 
        description="The endpoint type. Always populate this field with 'PHONE_NUMBER' when using the messages tool."
    )
    endpoint_value: str = Field(description="The phone number value")
    endpoint_label: Optional[str] = Field(
        default=None, 
        description="Label for the endpoint (e.g., 'mobile', 'work')"
    )

    @field_validator('endpoint_type')
    def validate_endpoint_type(cls, v):
        if v != "PHONE_NUMBER":
            raise ValueError("endpoint_type must be 'PHONE_NUMBER'")
        return v

    # Define a field validator for validating a phone number
    @field_validator('endpoint_value')
    def validate_phone_number(cls, v):
        # Check if the input is a non-empty string
        if not v or not isinstance(v, str):
            raise InvalidPhoneNumberError("endpoint_value must be a non-empty string")
        
        # Step 1: Remove all non-digit characters (except +, spaces, parentheses, hyphens)
        # This is used to extract only the digits from the input string
        digits = re.sub(r'\D', '', v)

        # Step 2: Validate the length of the digits (must be at least 10 digits)
        # and check if the original string matches the allowed phone number format
        # The format should allow:
        # - Optional '+' at the start (for international numbers)
        # - Digits, spaces, parentheses, and hyphens
        # The string should match the pattern and contain at least 10 digits
        if len(digits) < 10 or not re.match(r'^\+?[\d\s\-\(\)]+$', v.strip()):
            raise InvalidPhoneNumberError(f"Invalid phone number format: {v}")
        
        # Step 3: If validation passes, return the stripped version of the phone number
        # to remove any leading or trailing spaces
        return v.strip()


class Recipient(BaseModel):
    """
    The recipient of the message, representing a contact.
    """
    contact_id: Optional[str] = Field(
        default=None, 
        description="A unique identifier for the contact associated with this recipient."
    )
    contact_name: str = Field(
        description="The name of the contact. This is strictly necessary."
    )
    contact_endpoints: List[Endpoint] = Field(
        description="One or more endpoints for the contact."
    )
    contact_photo_url: Optional[str] = Field(
        default=None, 
        description="The URL to the profile photo of the contact."
    )

    @field_validator('contact_name')
    def validate_contact_name(cls, v):
        if not v or not isinstance(v, str) or not v.strip():
            raise InvalidRecipientError("contact_name is required and cannot be empty")
        return v.strip()

    @field_validator('contact_endpoints')
    def validate_contact_endpoints(cls, v):
        if not v or not isinstance(v, list):
            raise InvalidRecipientError("contact_endpoints must be a non-empty list")
        if len(v) == 0:
            raise InvalidRecipientError("contact_endpoints cannot be empty")
        return v

    @field_validator('contact_photo_url')
    def validate_photo_url(cls, v):
        if v is not None and (not isinstance(v, str) or not v.strip()):
            raise ValueError("contact_photo_url must be a valid URL string when provided")
        return v.strip() if v else v


class MediaAttachment(BaseModel):
    """
    Metadata associated with media payload. Currently only supports images.
    """
    media_id: str = Field(description="Unique identifier of the media.")
    media_type: Literal["IMAGE"] = Field(
        default="IMAGE", 
        description="Type of the media, default to IMAGE."
    )
    source: Literal["IMAGE_RETRIEVAL", "IMAGE_GENERATION", "IMAGE_UPLOAD", "GOOGLE_PHOTO"] = Field(
        description="Source of the media."
    )

    @field_validator('media_id')
    def validate_media_id(cls, v):
        if not v or not isinstance(v, str) or not v.strip():
            raise InvalidMediaAttachmentError("media_id is required and cannot be empty")
        return v.strip()

# --- New Models for the updated DB structure ---

class PeopleName(BaseModel):
    """Represents a name in the People API format."""
    givenName: Optional[str] = None
    familyName: Optional[str] = None

class PeoplePhoneNumber(BaseModel):
    """Represents a phone number in the People API format."""
    value: str
    type: Optional[str] = None
    primary: Optional[bool] = False

class PeopleApiContact(BaseModel):
    """
    Represents a full contact structure as stored in the 'recipients' DB,
    aligning with a People API-like schema.
    """
    resourceName: str = Field(description="The unique resource name for the contact.")
    etag: str = Field(description="The ETag of the resource.")
    names: List[PeopleName] = Field(description="A list of names for the contact.")
    phoneNumbers: List[PeoplePhoneNumber] = Field(description="A list of phone numbers for the contact.")
    phone: Recipient = Field(description="The nested recipient object containing detailed phone contact info.")

class PostSendChatMessageRequest(BaseModel):
    """
    Send a message to a recipient via SMS/MMS, given the recipient and message body.
    """
    recipient_name: Optional[str] = Field(
        default=None, 
        description="The recipient's name, e.g. 'Jane Doe'."
    )
    recipient_phone_number: Optional[str] = Field(
        default=None, 
        description="The phone number of the recipient to send a message to."
    )
    recipient_photo_url: Optional[str] = Field(
        default=None, 
        description="The URL to the profile photo of the recipient."
    )
    recipient: Optional[Recipient] = Field(
        default=None, 
        description="The recipient object"
    )
    message_body: str = Field(
        description="The text message content to send to the recipient. This field must be non-empty. Please use correct grammar, capitalization, and punctuation. If the message body contains a list of items, please format it as a bulleted list, with an asterisk preceding each item. Make sure the message body is user-friendly. DO NOT hallucinate message body. Wait for the user to provide the message body before sending the message."
    )
    media_attachments: Optional[List[MediaAttachment]] = Field(
        default=None, 
        description="Metadata associated with media payload. Currently only supports images."
    )

    @field_validator('message_body')
    def validate_message_body(cls, v):
        if not v or not isinstance(v, str) or not v.strip():
            raise MessageBodyRequiredError("message_body is required and cannot be empty")
        return v.strip()

class PostPrepareChatMessageRequest(BaseModel):
    """
    Prepare message cards that show information and can be interacted with to send message.
    """
    message_body: str = Field(description="The text message content to send to the recipient")
    recipients: List[Recipient] = Field(description="List of recipients")


class PostShowMessageRecipientChoicesRequest(BaseModel):
    """
    Show a list of one or more recipients that the user can choose to send a message to.
    """
    message_body: Optional[str] = Field(
        default=None, 
        description="The text message content to send to the recipient. This may be left empty if the user has not specified this already."
    )
    recipients: List[Recipient] = Field(
        description="Possible recipient(s) to send the message to."
    )



class PostAskForMessageBodyRequest(BaseModel):
    """
    Show a card to the user, with the intent to ask the user for the message body.
    """
    recipient: Recipient = Field(
        description="The recipient to send the message to. The recipient is auxiliary information that is displayed in the card shown to the user."
    )


class Observation(BaseModel):
    """
    Observations from the tool call.
    """
    action_card_content_passthrough: Optional[str] = Field(default=None)
    sent_message_id: Optional[str] = Field(
        default=None, 
        description="A unique identifier for the operation associated with this observation."
    )
    emitted_action_count: Optional[int] = Field(
        default=None, 
        description="The number of actions generated as a result of calling a function."
    )
    status: str = Field(description="Whether the operation was successful or not.")


# Validation functions for the main operations
def validate_send_chat_message(
    recipient: Union[Dict[str, Any], Recipient], 
    message_body: str, 
    media_attachments: Optional[List[Union[Dict[str, Any], MediaAttachment]]] = None
) -> Dict[str, Any]:
    """
    Validate input for send_chat_message operation.
    
    Args:
        recipient: The recipient object or dictionary
        message_body: The message content to send
        media_attachments: Optional list of media attachments
        
    Returns:
        Dict containing validated recipient, message_body, and media_attachments
        
    Raises:
        TypeError: If inputs are not of expected types
        ValueError: If validation fails
        InvalidRecipientError: If recipient validation fails
        MessageBodyRequiredError: If message body is invalid
        InvalidMediaAttachmentError: If media attachment validation fails
    """
    # Validate message body
    if not isinstance(message_body, str):
        raise TypeError(f"message_body must be a string, got {type(message_body).__name__}")
    
    if not message_body.strip():
        raise MessageBodyRequiredError("message_body is required and cannot be empty")
    
    # Validate recipient
    if not recipient:
        raise InvalidRecipientError("recipient is required")
    
    try:
        if isinstance(recipient, dict):
            recipient_obj = Recipient(**recipient)
        elif isinstance(recipient, Recipient):
            recipient_obj = recipient
        else:
            raise TypeError(f"recipient must be a dict or Recipient object, got {type(recipient).__name__}")
    except ValidationError as e:
        raise InvalidRecipientError(f"Invalid recipient data: {e}")
    
    # Validate media attachments if provided
    media_attachments_obj = []
    if media_attachments:
        if not isinstance(media_attachments, list):
            raise TypeError(f"media_attachments must be a list when provided, got {type(media_attachments).__name__}")
        
        for i, attachment in enumerate(media_attachments):
            try:
                if isinstance(attachment, dict):
                    media_attachments_obj.append(MediaAttachment(**attachment))
                elif isinstance(attachment, MediaAttachment):
                    media_attachments_obj.append(attachment)
                else:
                    raise TypeError(f"media_attachments[{i}] must be a dict or MediaAttachment object")
            except ValidationError as e:
                raise InvalidMediaAttachmentError(f"Invalid media attachment at index {i}: {e}")
    
    return {
        "recipient": recipient_obj,
        "message_body": message_body.strip(),
        "media_attachments": media_attachments_obj
    }


def validate_prepare_chat_message(
    message_body: str, 
    recipients: List[Union[Dict[str, Any], Recipient]]
) -> Dict[str, Any]:
    """
    Validate input for prepare_chat_message operation.
    
    Args:
        message_body: The message content to prepare
        recipients: List of recipient objects or dictionaries
        
    Returns:
        Dict containing validated message_body and recipients
        
    Raises:
        TypeError: If inputs are not of expected types
        ValueError: If validation fails
        InvalidRecipientError: If recipient validation fails
        MessageBodyRequiredError: If message body is invalid
    """
    # Validate message body
    if not isinstance(message_body, str):
        raise TypeError(f"message_body must be a string, got {type(message_body).__name__}")
    
    if not message_body.strip():
        raise MessageBodyRequiredError("message_body is required and cannot be empty")
    
    # Validate recipients
    if not isinstance(recipients, list):
        raise TypeError(f"recipients must be a list, got {type(recipients).__name__}")
    
    if not recipients:
        raise InvalidRecipientError("recipients list is required and cannot be empty")
    
    recipients_obj = []
    for i, recipient in enumerate(recipients):
        try:
            if isinstance(recipient, dict):
                recipients_obj.append(Recipient(**recipient))
            elif isinstance(recipient, Recipient):
                recipients_obj.append(recipient)
            else:
                raise TypeError(f"recipients[{i}] must be a dict or Recipient object")
        except ValidationError as e:
            raise InvalidRecipientError(f"Invalid recipient at index {i}: {e}")
    
    return {
        "message_body": message_body.strip(),
        "recipients": recipients_obj
    }


def validate_show_recipient_choices(
    recipients: List[Union[Dict[str, Any], Recipient]], 
    message_body: Optional[str] = None
) -> Dict[str, Any]:
    """
    Validate input for show_message_recipient_choices operation.
    
    Args:
        recipients: List of recipient objects or dictionaries
        message_body: Optional message content
        
    Returns:
        Dict containing validated recipients and message_body
        
    Raises:
        TypeError: If inputs are not of expected types
        ValueError: If validation fails
        InvalidRecipientError: If recipient validation fails
    """
    # Validate recipients
    if not isinstance(recipients, list):
        raise TypeError(f"recipients must be a list, got {type(recipients).__name__}")
    
    if not recipients:
        raise InvalidRecipientError("recipients list is required and cannot be empty")
    
    recipients_obj = []
    for i, recipient in enumerate(recipients):
        try:
            if isinstance(recipient, dict):
                recipients_obj.append(Recipient(**recipient))
            elif isinstance(recipient, Recipient):
                recipients_obj.append(recipient)
            else:
                raise TypeError(f"recipients[{i}] must be a dict or Recipient object")
        except ValidationError as e:
            raise InvalidRecipientError(f"Invalid recipient at index {i}: {e}")
    
    # Validate message body if provided
    if message_body is not None:
        if not isinstance(message_body, str):
            raise TypeError(f"message_body must be a string when provided, got {type(message_body).__name__}")
        message_body = message_body.strip() if message_body else None
    
    return {
        "recipients": recipients_obj,
        "message_body": message_body
    }


def validate_ask_for_message_body(recipient: Union[Dict[str, Any], Recipient]) -> Dict[str, Any]:
    """
    Validate input for ask_for_message_body operation.
    
    Args:
        recipient: The recipient object or dictionary
        
    Returns:
        Dict containing validated recipient
        
    Raises:
        TypeError: If recipient is not of expected type
        ValueError: If validation fails
        InvalidRecipientError: If recipient validation fails
    """
    # Validate recipient
    if not recipient:
        raise InvalidRecipientError("recipient is required")
    
    try:
        if isinstance(recipient, dict):
            recipient_obj = Recipient(**recipient)
        elif isinstance(recipient, Recipient):
            recipient_obj = recipient
        else:
            raise TypeError(f"recipient must be a dict or Recipient object, got {type(recipient).__name__}")
    except ValidationError as e:
        raise InvalidRecipientError(f"Invalid recipient data: {e}")
    
    return {
        "recipient": recipient_obj
    } 