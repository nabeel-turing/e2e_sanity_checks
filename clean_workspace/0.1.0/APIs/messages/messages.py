from typing import Any, Dict, List, Optional, Union
from .SimulationEngine.db import DB
from .SimulationEngine.models import (
    validate_send_chat_message, 
    validate_prepare_chat_message,
    validate_show_recipient_choices,
    validate_ask_for_message_body,
    Recipient,
    MediaAttachment,
    Observation,
    APIName
)
from .SimulationEngine.utils import _next_counter
from .SimulationEngine.custom_errors import (
    InvalidRecipientError,
    MessageBodyRequiredError,
    InvalidPhoneNumberError,
    InvalidMediaAttachmentError
)

def send_chat_message(
    recipient: Union[Dict[str, Any], Recipient], 
    message_body: str, 
    media_attachments: Optional[List[Union[Dict[str, Any], MediaAttachment]]] = None, 
    get_confirmation: bool = True,
    recipient_name: Optional[str] = None,
    recipient_phone_number: Optional[str] = None,
    recipient_photo_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send a message to a recipient containing a single endpoint.
    
    This method sends a message to a recipient via SMS/MMS. Always invoke this method 
    with `get_confirmation=True`. The method validates the recipient has exactly one 
    endpoint before sending the message.
    
    Args:
        recipient (Union[Dict[str, Any], Recipient]): The recipient object containing 
            contact information. Must have exactly one endpoint for sending messages.
            Expected structure:
            - contact_id (Optional[str]): Unique identifier for the contact
            - contact_name (str): The name of the contact (required)
            - contact_endpoints (List[Dict]): List with exactly one endpoint containing:
                - endpoint_type (str): Must be "PHONE_NUMBER"
                - endpoint_value (str): The phone number
                - endpoint_label (Optional[str]): Label for the endpoint
            - contact_photo_url (Optional[str]): URL to the contact's photo
        message_body (str): The text message content to send to the recipient. 
            This field must be non-empty. Should use correct grammar, capitalization, 
            and punctuation. If the message body contains a list of items, format 
            it as a bulleted list with asterisks.
        media_attachments (Optional[List[Union[Dict[str, Any], MediaAttachment]]]): 
            Metadata associated with media payload. Currently only supports images.
            Each attachment should contain:
            - media_id (str): Unique identifier of the media
            - media_type (str): Type of media, defaults to "IMAGE"
            - source (str): Source of media ("IMAGE_RETRIEVAL", "IMAGE_GENERATION", 
              "IMAGE_UPLOAD", or "GOOGLE_PHOTO")
        get_confirmation (bool): Whether to get confirmation before sending. 
            Defaults to True and should always be True per OpenAPI spec.
        recipient_name (Optional[str]): The recipient's name (legacy parameter).
        recipient_phone_number (Optional[str]): The phone number of the recipient 
            (legacy parameter).
        recipient_photo_url (Optional[str]): URL to the profile photo of the recipient 
            (legacy parameter).
    
    Returns:
        Dict[str, Any]: A dictionary containing the operation result with:
            - status (str): "success" if the message was sent successfully
            - sent_message_id (str): Unique identifier for the sent message
            - emitted_action_count (int): Number of actions generated (always 1)
            - action_card_content_passthrough (Optional[str]): Additional content metadata
    
    Raises:
        TypeError: If recipient is not a dict or Recipient object, if message_body 
            is not a string, if media_attachments is not a list when provided, or 
            if get_confirmation is not a boolean.
        ValueError: If message_body is empty, if recipient is missing required fields,
            if recipient has more than one endpoint, if phone number validation fails,
            or if media attachment validation fails.
        InvalidRecipientError: If the recipient object is malformed or missing 
            required contact information.
        MessageBodyRequiredError: If the message body is empty or None.
        InvalidPhoneNumberError: If the phone number format is invalid.
        InvalidMediaAttachmentError: If media attachment data is malformed.
    """
    # --- Input Validation ---
    if not isinstance(message_body, str):
        raise TypeError(f"message_body must be a string, got {type(message_body).__name__}")
    
    if not message_body.strip():
        raise MessageBodyRequiredError("message_body cannot be empty")
    
    if recipient is None:
        raise InvalidRecipientError("recipient is required and cannot be None")
    
    if not isinstance(recipient, (dict, Recipient)):
        raise TypeError(f"recipient must be a dict or Recipient object, got {type(recipient).__name__}")
    
    if media_attachments is not None and not isinstance(media_attachments, list):
        raise TypeError(f"media_attachments must be a list or None, got {type(media_attachments).__name__}")
    
    if not isinstance(get_confirmation, bool):
        raise TypeError(f"get_confirmation must be a boolean, got {type(get_confirmation).__name__}")
    
    if recipient_name is not None and not isinstance(recipient_name, str):
        raise TypeError(f"recipient_name must be a string or None, got {type(recipient_name).__name__}")
    
    if recipient_phone_number is not None and not isinstance(recipient_phone_number, str):
        raise TypeError(f"recipient_phone_number must be a string or None, got {type(recipient_phone_number).__name__}")
    
    if recipient_photo_url is not None and not isinstance(recipient_photo_url, str):
        raise TypeError(f"recipient_photo_url must be a string or None, got {type(recipient_photo_url).__name__}")
    
    # --- Input Validation (using Pydantic models via helper) ---
    try:
        validated_data = validate_send_chat_message(
            recipient, message_body, media_attachments
        )
    except (TypeError, ValueError, InvalidRecipientError, MessageBodyRequiredError, InvalidMediaAttachmentError) as e:
        # Re-raise validation errors to be handled by the caller
        raise e

    # --- Core Logic ---
    recipient_obj = validated_data["recipient"]
    
    # Ensure recipient has exactly one endpoint for this function
    if len(recipient_obj.contact_endpoints) != 1:
        raise InvalidRecipientError(
            f"Recipient must have exactly one endpoint for sending messages, "
            f"but has {len(recipient_obj.contact_endpoints)} endpoints"
        )

    # Generate the next message ID
    message_id = f"msg_{_next_counter('message')}"
    
    # Create the message data structure for storage
    message_data = {
        "id": message_id,
        "recipient": recipient_obj.model_dump(),
        "message_body": validated_data["message_body"],
        "media_attachments": [
            att.model_dump() for att in validated_data.get("media_attachments", [])
        ],
        "timestamp": "2024-01-01T12:00:00Z",  # Using a fixed timestamp for consistency
        "status": "sent",
    }
    
    # Update the messages table in the DB
    DB["messages"][message_id] = message_data
    

    
    # Return the observation response
    return {
        "status": "success",
        "sent_message_id": message_id,
        "emitted_action_count": 1,
        "action_card_content_passthrough": None
    }

def prepare_chat_message(
    message_body: str, 
    recipients: List[Union[Dict[str, Any], Recipient]]
) -> Dict[str, Any]:
    """
    Prepare to send a message to one or more candidate recipients via SMS/MMS.
    
    This method prepares message cards that show information and can be interacted 
    with to send messages. It validates the message body and recipient list but 
    does not actually send any messages.
    
    Args:
        message_body (str): The text message content to send to the recipients.
            Must be a non-empty string.
        recipients (List[Union[Dict[str, Any], Recipient]]): List of recipient 
            objects. Each recipient should contain:
            - contact_id (Optional[str]): Unique identifier for the contact
            - contact_name (str): The name of the contact (required)
            - contact_endpoints (List[Dict]): List of endpoints for the contact
            - contact_photo_url (Optional[str]): URL to the contact's photo
    
    Returns:
        Dict[str, Any]: A dictionary containing the preparation result with:
            - status (str): "prepared" indicating the message was prepared
            - sent_message_id (Optional[str]): Always None for prepare operations
            - emitted_action_count (int): Number of actions generated (always 0)
            - action_card_content_passthrough (Optional[str]): Additional content metadata
    
    Raises:
        TypeError: If message_body is not a string or if recipients is not a list.
        ValueError: If message_body is empty or if recipients list is empty.
        InvalidRecipientError: If any recipient object is malformed or missing 
            required contact information.
        MessageBodyRequiredError: If the message body is empty or None.
    """
    # --- Input Validation ---
    if not isinstance(message_body, str):
        raise TypeError(f"message_body must be a string, got {type(message_body).__name__}")
    
    if not message_body.strip():
        raise MessageBodyRequiredError("message_body cannot be empty")
    
    if not isinstance(recipients, list):
        raise TypeError(f"recipients must be a list, got {type(recipients).__name__}")
    
    if not recipients:
        raise ValueError("recipients list cannot be empty")
    
    # --- Core Logic ---
    # Validate input using the validation function
    validated_data = validate_prepare_chat_message(message_body, recipients)
    

    
    # Return response matching Observation schema
    return {
        "status": "prepared",
        "sent_message_id": None,
        "emitted_action_count": 0,
        "action_card_content_passthrough": None
    }

def show_message_recipient_choices(
    recipients: List[Union[Dict[str, Any], Recipient]], 
    message_body: Optional[str] = None
) -> Dict[str, Any]:
    """
    Display potential recipients in a card for user selection.
    
    This method displays a list of one or more recipients that the user can choose 
    to send a message to. It is used when there are multiple recipients or when 
    a single recipient has multiple endpoints, requiring user clarification.
    
    Args:
        recipients (List[Union[Dict[str, Any], Recipient]]): List of possible 
            recipients to send the message to. Each recipient should contain:
            - contact_id (Optional[str]): Unique identifier for the contact
            - contact_name (str): The name of the contact (required)
            - contact_endpoints (List[Dict]): List of endpoints for the contact
            - contact_photo_url (Optional[str]): URL to the contact's photo
        message_body (Optional[str]): The text message content to send to the 
            recipient. This may be left empty if the user has not specified 
            this already.
    
    Returns:
        Dict[str, Any]: A dictionary containing the display result with:
            - status (str): "choices_displayed" indicating choices were shown
            - sent_message_id (Optional[str]): Always None for choice operations
            - emitted_action_count (int): Number of actions generated (always 0)
            - action_card_content_passthrough (Optional[str]): Additional content metadata
    
    Raises:
        TypeError: If recipients is not a list or if message_body is not a string 
            when provided.
        ValueError: If recipients list is empty.
        InvalidRecipientError: If any recipient object is malformed or missing 
            required contact information.
    """
    # --- Input Validation ---
    if not isinstance(recipients, list):
        raise TypeError(f"recipients must be a list, got {type(recipients).__name__}")
    
    if not recipients:
        raise ValueError("recipients list cannot be empty")
    
    if message_body is not None and not isinstance(message_body, str):
        raise TypeError(f"message_body must be a string or None, got {type(message_body).__name__}")
    
    # --- Core Logic ---
    # Validate input using the validation function
    validated_data = validate_show_recipient_choices(recipients, message_body)
    

    
    # Return response matching Observation schema
    return {
        "status": "choices_displayed",
        "sent_message_id": None,
        "emitted_action_count": 0,
        "action_card_content_passthrough": None
    }

def ask_for_message_body(recipient: Union[Dict[str, Any], Recipient]) -> Dict[str, Any]:
    """
    Display recipient and ask user for message body.
    
    This method displays the recipient in a card shown to the user, with the intent 
    to ask the user to provide the message body. It is used when there is a single 
    recipient with a single endpoint, but the user has not specified a message body.
    
    Args:
        recipient (Union[Dict[str, Any], Recipient]): The recipient to send the 
            message to. The recipient is auxiliary information that is displayed 
            in the card shown to the user. Should contain:
            - contact_id (Optional[str]): Unique identifier for the contact
            - contact_name (str): The name of the contact (required)
            - contact_endpoints (List[Dict]): List of endpoints for the contact
            - contact_photo_url (Optional[str]): URL to the contact's photo
    
    Returns:
        Dict[str, Any]: A dictionary containing the request result with:
            - status (str): "asking_for_message_body" indicating body was requested
            - sent_message_id (Optional[str]): Always None for request operations
            - emitted_action_count (int): Number of actions generated (always 0)
            - action_card_content_passthrough (Optional[str]): Additional content metadata
    
    Raises:
        TypeError: If recipient is not a dict or Recipient object.
        ValueError: If recipient is None or missing required fields.
        InvalidRecipientError: If the recipient object is malformed or missing 
            required contact information.
    """
    # --- Input Validation ---
    if recipient is None:
        raise InvalidRecipientError("recipient is required and cannot be None")
    
    if not isinstance(recipient, (dict, Recipient)):
        raise TypeError(f"recipient must be a dict or Recipient object, got {type(recipient).__name__}")
    
    # --- Core Logic ---
    # Validate input using the validation function
    validated_data = validate_ask_for_message_body(recipient)
    

    
    # Return response matching Observation schema
    return {
        "status": "asking_for_message_body",
        "sent_message_id": None,
        "emitted_action_count": 0,
        "action_card_content_passthrough": None
    }

def show_message_recipient_not_found_or_specified(
    contact_name: Optional[str] = None, 
    message_body: Optional[str] = None
) -> Dict[str, Any]:
    """
    Inform the user that the message recipient is not found or not specified.
    
    This method is used to inform the user that the message recipient is not found 
    or not specified. It is invoked when there are no contacts returned from contact 
    search or when the user has not specified a contact name in the query.
    
    Args:
        contact_name (Optional[str]): The recipient name that was searched for.
            May be None if no name was provided in the search.
        message_body (Optional[str]): The text message content to send to the 
            recipient. This may be left empty if the user has not specified 
            this already.
    
    Returns:
        Dict[str, Any]: A dictionary containing the notification result with:
            - status (str): "recipient_not_found" indicating no recipient was found
            - sent_message_id (Optional[str]): Always None for notification operations
            - emitted_action_count (int): Number of actions generated (always 0)
            - action_card_content_passthrough (Optional[str]): Additional content metadata
    
    Raises:
        TypeError: If contact_name is not a string when provided, or if message_body 
            is not a string when provided.
    """
    # --- Input Validation ---
    if contact_name is not None and not isinstance(contact_name, str):
        raise TypeError(f"contact_name must be a string or None, got {type(contact_name).__name__}")
    
    if message_body is not None and not isinstance(message_body, str):
        raise TypeError(f"message_body must be a string or None, got {type(message_body).__name__}")
    
    # --- Core Logic ---

    
    # Return response matching Observation schema
    return {
        "status": "recipient_not_found",
        "sent_message_id": None,
        "emitted_action_count": 0,
        "action_card_content_passthrough": None
    }



