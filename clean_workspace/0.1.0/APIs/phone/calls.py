# phone_client/calls.py

import uuid
import time
from typing import Dict, Any, Optional, List
from phone.SimulationEngine.models import (
    RecipientModel, RecipientEndpointModel, 
    SingleEndpointChoiceModel, MultipleEndpointChoiceModel,
    ChoiceEndpointModel, ShowChoicesResponseModel, PhoneAPIResponseModel
)
from phone.SimulationEngine.db import DB, load_state
from phone.SimulationEngine.utils import (
    add_call_to_history, add_prepared_call, add_recipient_choice, add_not_found_record,
    should_show_recipient_choices, get_recipient_with_single_endpoint
)
from phone.SimulationEngine.custom_errors import (
    PhoneAPIError, InvalidRecipientError, NoPhoneNumberError, 
    MultipleEndpointsError, MultipleRecipientsError, GeofencingPolicyError, ValidationError
)
import os

def make_call(
    *,
    recipient: Optional[Dict[str, Any]] = None,
    on_speakerphone: bool = False,
    recipient_name: Optional[str] = None,
    recipient_phone_number: Optional[str] = None,
    recipient_photo_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Make a call to a single recipient with exactly one phone number endpoint.

    To resolve the phone number endpoint, you may have to call one or more tools
    prior to calling this operation. Before calling this operation, always check
    if the Geofencing Policy applies. If there is a recipient with more than one
    phone number endpoints, ask the user for the intended endpoint by invoking
    show_call_recipient_choices. Do not call this operation until the user has
    chosen a single recipient with exactly one phone number endpoint.

    Args:
        recipient (Optional[Dict[str, Any]]): The recipient of the phone call. Contains:
            - contact_id (Optional[str]): Unique identifier for the contact
            - contact_name (Optional[str]): Name of the contact
            - contact_endpoints (Optional[List[Dict]]): List of endpoints for the contact
            - contact_photo_url (Optional[str]): URL to the contact's profile photo
            - recipient_type (Optional[str]): Type of recipient ("CONTACT", "BUSINESS", "DIRECT", "VOICEMAIL")
            - address (Optional[str]): Address of the recipient
            - distance (Optional[str]): Distance to the recipient
        on_speakerphone (bool): If True, the phone call will be placed on the
            speakerphone. Defaults to False.
        recipient_name (Optional[str]): The recipient's name.
        recipient_phone_number (Optional[str]): The phone number of the
            recipient to make the call to, e.g. "+11234567890".
        recipient_photo_url (Optional[str]): The url to the profile photo
            of the recipient.

    Returns:
        Dict[str, Any]: A dictionary representing the observation from the tool
        call, confirming whether the call was successfully made.
    """
    call_id = str(uuid.uuid4())
    
    # Validate recipient input if provided
    validated_recipient = None
    if recipient is not None:
        try:
            validated_recipient = RecipientModel(**recipient)
        except Exception as e:
            raise ValidationError(
                f"Invalid recipient: {str(e)}",
                details={"recipient": recipient, "error": str(e)}
            )
    
    # Determine the phone number to call
    phone_number = None
    recipient_name_final = None
    recipient_photo_url_final = None
    
    if validated_recipient:
        # Use recipient object data
        # Check if this recipient should trigger choice selection
        should_show, reason = should_show_recipient_choices([validated_recipient.model_dump()])
        if should_show:
            # Raise appropriate errors instead of calling show_call_recipient_choices
            if "Multiple phone numbers found" in reason:
                raise MultipleEndpointsError(
                    f"I found multiple phone numbers for {validated_recipient.contact_name}. Please use show_call_recipient_choices to select the desired endpoint.",
                    details={
                        "recipient": validated_recipient.model_dump(),
                        "reason": reason
                    }
                )
            elif "Multiple recipients found" in reason:
                raise MultipleRecipientsError(
                    f"I found multiple recipients. Please use show_call_recipient_choices to select the desired recipient.",
                    details={
                        "recipient": validated_recipient.model_dump(),
                        "reason": reason
                    }
                )
            elif "Geofencing policy applies" in reason:
                raise GeofencingPolicyError(
                    f"The business {validated_recipient.contact_name} is {validated_recipient.distance} away. Please use show_call_recipient_choices to confirm you want to call this business.",
                    details={
                        "recipient": validated_recipient.model_dump(),
                        "reason": reason
                    }
                )
            elif "Low confidence match" in reason:
                raise InvalidRecipientError(
                    f"I found a low confidence match for {validated_recipient.contact_name}. Please use show_call_recipient_choices to confirm this is the correct recipient.",
                    details={
                        "recipient": validated_recipient.model_dump(),
                        "reason": reason
                    }
                )
        
        # Get recipient with single endpoint
        single_endpoint_recipient = get_recipient_with_single_endpoint([validated_recipient.model_dump()])
        if single_endpoint_recipient and single_endpoint_recipient.get("contact_endpoints", None):
            phone_number = single_endpoint_recipient["contact_endpoints"][0]["endpoint_value"]
        
        recipient_name_final = validated_recipient.contact_name
        recipient_photo_url_final = validated_recipient.contact_photo_url
    else:
        # Use individual parameters
        phone_number = recipient_phone_number
        recipient_name_final = recipient_name
        recipient_photo_url_final = recipient_photo_url
    
    if not phone_number:
        raise NoPhoneNumberError(
            "I couldn't determine the phone number to call. Please provide a valid phone number or recipient information.",
            details={
                "recipient": validated_recipient.model_dump() if validated_recipient else None,
                "recipient_name": recipient_name,
                "recipient_phone_number": recipient_phone_number
            }
        )
    
    # Simulate making the call
    try:
        # Update the database to simulate call history
        call_record = {
            "call_id": call_id,
            "timestamp": time.time(),
            "phone_number": phone_number,
            "recipient_name": recipient_name_final,
            "recipient_photo_url": recipient_photo_url_final,
            "on_speakerphone": on_speakerphone,
            "status": "completed"
        }
        
        # Add to call history in DB
        add_call_to_history(call_record)
    
        # Generate response message
        speakerphone_text = " on speakerphone" if on_speakerphone else ""
        recipient_text = f" to {recipient_name_final}" if recipient_name_final else ""
        
        output = {
            "status": "success",
            "call_id": call_id,
            "emitted_action_count": 1,
            "templated_tts": f"Calling{recipient_text} at {phone_number}{speakerphone_text}.",
            "action_card_content_passthrough": f"Call completed successfully to {phone_number}"
        }

        return output
    
    except PhoneAPIError:
        # Re-raise custom errors as-is
        raise
    except Exception as e:
        # Convert unexpected errors to PhoneAPIError
        raise PhoneAPIError(
            f"Sorry, I encountered an error while making the call: {str(e)}",
            details={
                "phone_number": phone_number,
                "recipient_name": recipient_name_final,
                "on_speakerphone": on_speakerphone,
                "original_error": str(e)
            }
        )


def prepare_call(
    *,
    recipients: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Prepare a call to one or more recipients, given provided recipient information.

    Args:
        recipients (Optional[List[Dict[str, Any]]]): A list of recipient objects to
            prepare call cards for. Each recipient dict contains:
            - contact_id (Optional[str]): Unique identifier for the contact
            - contact_name (Optional[str]): Name of the contact
            - contact_endpoints (Optional[List[Dict]]): List of endpoints for the contact
            - contact_photo_url (Optional[str]): URL to the contact's profile photo
            - recipient_type (Optional[str]): Type of recipient ("CONTACT", "BUSINESS", "DIRECT", "VOICEMAIL")
            - address (Optional[str]): Address of the recipient
            - distance (Optional[str]): Distance to the recipient

    Returns:
        Dict[str, Any]: A dictionary representing the observation from the tool
        call, containing information about the generated call cards.
    """
    call_id = str(uuid.uuid4())
    
    # Validate recipients input if provided
    validated_recipients = []
    if recipients is not None:
        for i, recipient in enumerate(recipients):
            try:
                validated_recipient = RecipientModel(**recipient)
                validated_recipients.append(validated_recipient)

            except Exception as e:
                raise ValidationError(
                    f"Invalid recipient at index {i}: {str(e)}",
                    details={"recipient_index": i, "recipient": recipient, "error": str(e)}
                )
    
    if not validated_recipients:
        raise ValidationError(
            "No recipients provided to prepare call cards for.",
            details={
                "recipients": recipients,
                "validated_count": len(validated_recipients)
            }
        )
    
    # Check if any recipients require user choice or have missing endpoints
    # For prepare_call, we only care about multiple endpoints per recipient, not multiple recipients
    for recipient in validated_recipients:
        # Check if recipient has endpoints (required according to phone.json)
        if not recipient.contact_endpoints or len(recipient.contact_endpoints) == 0:
            raise NoPhoneNumberError(
                f"Recipient {recipient.contact_name} does not have any phone number endpoints. All applicable fields should be populated for prepare_call.",
                details={
                    "recipient": recipient.model_dump(),
                    "missing_field": "contact_endpoints"
                }
            )
        
        recipient_dict = recipient.model_dump()
        should_show, reason = should_show_recipient_choices([recipient_dict])
        if should_show:
            # Raise appropriate errors for individual recipients
            if "Multiple phone numbers found" in reason:
                raise MultipleEndpointsError(
                    f"I found multiple phone numbers for {recipient.contact_name}. Please use show_call_recipient_choices to select the desired endpoint.",
                    details={
                        "recipient": recipient_dict,
                        "reason": reason
                    }
                )
            elif "Geofencing policy applies" in reason:
                raise GeofencingPolicyError(
                    f"The business {recipient.contact_name} is {recipient.distance} away. Please use show_call_recipient_choices to confirm you want to call this business.",
                    details={
                        "recipient": recipient_dict,
                        "reason": reason
                    }
                )
            elif "Low confidence match" in reason:
                raise InvalidRecipientError(
                    f"I found a low confidence match for {recipient.contact_name}. Please use show_call_recipient_choices to confirm this is the correct recipient.",
                    details={
                        "recipient": recipient_dict,
                        "reason": reason
                    }
                )
    
    # Generate call cards for each recipient
    call_cards = []
    for recipient in validated_recipients:
        card = {
            "recipient_name": recipient.contact_name,
            "recipient_photo_url": recipient.contact_photo_url,
            "recipient_type": recipient.recipient_type,
            "address": recipient.address,
            "distance": recipient.distance,
            "endpoints": []
        }
        
        if recipient.contact_endpoints:
            for endpoint in recipient.contact_endpoints:
                card["endpoints"].append({
                    "type": endpoint.endpoint_type,
                    "value": endpoint.endpoint_value,
                    "label": endpoint.endpoint_label
                })
        
        call_cards.append(card)
    
    # Store prepared call cards in DB
    prepared_call_record = {
        "call_id": call_id,
        "timestamp": time.time(),
        "recipients": call_cards
    }
    add_prepared_call(prepared_call_record)
    
    # Note: Changes are kept in memory only, not persisted to file
    
    output = {
        "status": "success",
        "call_id": call_id,
        "emitted_action_count": len(call_cards),
        "templated_tts": f"Prepared {len(call_cards)} call card(s) for you.",
        "action_card_content_passthrough": f"Generated {len(call_cards)} call card(s)"
    }

    return output



def show_call_recipient_choices(
    *,
    recipients: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Show a list of one or more recipients to the user to choose from.

    This operation uses a UI component to show the list of choices. You do not
    need to enumerate the list of choices in your final response. If you call
    this operation, you may not call other operations from this tool before
    drafting the final response.

    Invoke this operation in the following scenarios:
        * There are multiple recipients (contacts or businesses) to choose from.
        * There are multiple phone number endpoints for a business to choose from.
        * There are multiple phone number endpoints for a single contact to choose from.
        * There is a single contact recipient with `confidence_level` LOW.
        * The Geofencing Policy applies.

    Args:
        recipients (Optional[List[Dict[str, Any]]]): A list of recipient objects to
            display as choices. Each recipient dict contains:
            - contact_id (Optional[str]): Unique identifier for the contact
            - contact_name (Optional[str]): Name of the contact
            - contact_endpoints (Optional[List[Dict]]): List of endpoints for the contact
            - contact_photo_url (Optional[str]): URL to the contact's profile photo
            - recipient_type (Optional[str]): Type of recipient ("CONTACT", "BUSINESS", "DIRECT", "VOICEMAIL")
            - address (Optional[str]): Address of the recipient
            - distance (Optional[str]): Distance to the recipient

    Returns:
        Dict[str, Any]: A dictionary representing the observation from the tool
        call for the list of recipients.
    """
    call_id = str(uuid.uuid4())
    
    # Validate recipients input if provided
    validated_recipients = []
    if recipients is not None:
        for i, recipient in enumerate(recipients):
            try:
                validated_recipient = RecipientModel(**recipient)
                validated_recipients.append(validated_recipient)
            except Exception as e:
                raise ValidationError(
                    f"Invalid recipient at index {i}: {str(e)}",
                    details={"recipient_index": i, "recipient": recipient, "error": str(e)}
                )
    
    if not validated_recipients:
        raise ValidationError(
            "No recipients provided to show choices for.",
            details={
                "recipients": recipients,
                "validated_count": len(validated_recipients)
            }
        )
    
    # Prepare choices for display
    choices = []
    for recipient in validated_recipients:
        try:
            if recipient.contact_endpoints and len(recipient.contact_endpoints) > 1:
                # Multiple endpoints for single recipient - create separate choices for each endpoint
                for endpoint in recipient.contact_endpoints:
                    choice_data = {
                        "contact_name": recipient.contact_name,
                        "contact_photo_url": recipient.contact_photo_url,
                        "recipient_type": recipient.recipient_type,
                        "address": recipient.address,
                        "distance": recipient.distance,
                        "endpoint": {
                            "type": endpoint.endpoint_type,
                            "value": endpoint.endpoint_value,
                            "label": endpoint.endpoint_label
                        }
                    }
                    # Validate the choice with Pydantic
                    choice = MultipleEndpointChoiceModel(**choice_data)
                    choices.append(choice)
            else:
                # Single endpoint or no endpoints - create one choice for the recipient
                choice_data = {
                    "contact_name": recipient.contact_name,
                    "contact_photo_url": recipient.contact_photo_url,
                    "recipient_type": recipient.recipient_type,
                    "address": recipient.address,
                    "distance": recipient.distance,
                    "endpoints": []
                }
                
                if recipient.contact_endpoints:
                    for endpoint in recipient.contact_endpoints:
                        choice_data["endpoints"].append({
                            "type": endpoint.endpoint_type,
                            "value": endpoint.endpoint_value,
                            "label": endpoint.endpoint_label
                        })
                
                # Validate the choice with Pydantic
                choice = SingleEndpointChoiceModel(**choice_data)
                choices.append(choice)
        except Exception as e:
            raise ValidationError(
                f"Failed to create choice for recipient {recipient.contact_name}: {str(e)}",
                details={"recipient": recipient.model_dump(), "error": str(e)}
            )
    
    # Generate choice text based on actual number of choices
    choice_count = len(choices)
    if choice_count == 1:
        choice = choices[0]
        contact_name = choice.contact_name or "Unknown Contact"
        if hasattr(choice, 'endpoint'):
            # Single recipient with single endpoint choice
            choice_text = f"Would you like to call {contact_name} at {choice.endpoint.label} ({choice.endpoint.value})?"
        else:
            # Single recipient with single endpoint
            choice_text = f"Would you like to call {contact_name}?"
    else:
        choice_text = f"Please choose from {choice_count} options to call."
    
    # Store the choices in DB
    choice_record = {
        "call_id": call_id,
        "timestamp": time.time(),
        "recipient_options": [choice.model_dump() for choice in choices]
    }
    add_recipient_choice(choice_record)

    # Create response data - match the ShowChoicesResponseModel schema
    response_data = {
        "status": "success",
        "call_id": call_id,
        "emitted_action_count": choice_count,
        "templated_tts": choice_text,
        "action_card_content_passthrough": f"Showing {choice_count} recipient choice(s)",
        "choices": choices
    }
    
    # Validate the final response with Pydantic
    try:
        validated_response = ShowChoicesResponseModel(**response_data)
        output = validated_response.model_dump()

        return output
    
    except Exception as e:
        raise ValidationError(
            f"Failed to validate response: {str(e)}",
            details={"response_data": response_data, "error": str(e)}
        )


def show_call_recipient_not_found_or_specified(
    contact_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Show a message to the user when the call recipient is not found or not specified.

    You must attempt to search for a recipient before calling this operation.
    Call this operation when no match is found for a recipient, or when the user
    expresses an intent to call without specifying a recipient.

    Args:
        contact_name (Optional[str]): The recipient name that was searched for.

    Returns:
        Dict[str, Any]: A dictionary representing the observation from the tool call.
    """
    call_id = str(uuid.uuid4())
    
    # Store the not found record in DB
    not_found_record = {
        "call_id": call_id,
        "timestamp": time.time(),
        "contact_name": contact_name
    }
    add_not_found_record(not_found_record)
    
    # Note: Changes are kept in memory only, not persisted to file
    
    # Generate appropriate message
    if contact_name:
        message = f"I couldn't find a contact or business named '{contact_name}' to call. Could you please provide more details or check the spelling?"
    else:
        message = "I need to know who you'd like to call. Could you please specify a name, phone number, or business?"
    
    output = {
        "status": "success",
        "call_id": call_id,
        "emitted_action_count": 0,
        "templated_tts": message,
        "action_card_content_passthrough": "Recipient not found or not specified"
    }

    return output