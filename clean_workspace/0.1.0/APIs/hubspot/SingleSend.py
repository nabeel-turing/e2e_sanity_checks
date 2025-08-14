# APIs/hubspot/SingleSend.py
from typing import Dict, Any, Union, Optional
import uuid
from hubspot.SimulationEngine.db import DB


def sendSingleEmail(
    template_id: str,
    message: Dict[str, Any],
    customProperties: Optional[Dict[str, Union[str, int, bool]]] = None,
    contactProperties: Optional[Dict[str, Union[str, int, bool]]] = None,
) -> Dict[str, Any]:
    """
    Sends a single transactional email based on a pre-existing email template.

    Args:
        template_id (str): The ID of the pre-existing transactional email template to send.
        message (Dict[str, Any]): An object containing email content and recipient info.
            - to (List[Dict[str, str]]): Required. List of recipient objects.
                - email (str): Required. Email address of the recipient.
                - name (Optional[str]): Name of the recipient.
            - cc (Optional[List[Dict[str, str]]]): List of CC recipient objects.
                - email (str): Required. Email address of the CC recipient.
                - name (Optional[str]): Name of the CC recipient.
            - bcc (Optional[List[Dict[str, str]]]): List of BCC recipient objects.
                - email (str): Required. Email address of the BCC recipient.
                - name (Optional[str]): Name of the BCC recipient.
            - from (Optional[Dict[str, str]]): Sender information.
                - email (str): Required. Email address of the sender.
                - name (Optional[str]): Name of the sender.
            - replyTo (Optional[List[Dict[str, str]]]): List of reply-to addresses.
                - email (str): Required. Reply-to email address.
                - name (Optional[str]): Reply-to name.
        customProperties (Optional[Dict[str, Union[str, int, bool]]]): Custom property values for template personalization.
            - customProperty1 (str): Value of custom property 1.
            - customProperty2 (str): Value of custom property 2.
            - ... (additional custom properties)
        contactProperties (Optional[Dict[str, Union[str, int, bool]]]): Contact property values.
            - firstName (str): First name of the contact.
            - lastName (str): Last name of the contact.

    Returns:
        Dict[str, Any]: A dictionary representing the API response with the following structure:
            - status (str): Status of the operation ('success' or 'error').
            - message (str): Description of the operation result.
            - template_id (str): The ID of the template used (only on success).
            - transactional_email_id (str): Unique ID for the sent email (only on success).
            - log (Dict[str, Any]): Log entry containing send details (only on success).
                - template_id (str): The ID of the template used.
                - transactional_email_id (str): Unique ID for the sent email.
                - message (Dict[str, Any]): Original message object.
                    - to (List[Dict[str, str]]): Required. List of recipient objects.
                        - email (str): Required. Email address of the recipient.
                        - name (Optional[str]): Name of the recipient.
                    - cc (Optional[List[Dict[str, str]]]): List of CC recipient objects.
                        - email (str): Required. Email address of the CC recipient.
                        - name (Optional[str]): Name of the CC recipient.
                    - bcc (Optional[List[Dict[str, str]]]): List of BCC recipient objects.
                        - email (str): Required. Email address of the BCC recipient.
                        - name (Optional[str]): Name of the BCC recipient.
                    - from (Optional[Dict[str, str]]): Sender information.
                        - email (str): Required. Email address of the sender.
                        - name (Optional[str]): Name of the sender.
                    - replyTo (Optional[List[Dict[str, str]]]): List of reply-to addresses.
                        - email (str): Required. Reply-to email address.
                        - name (Optional[str]): Reply-to name.
                - properties (Dict[str, Any]): Merged properties used.
                    - firstName (str): First name of the contact.
                    - lastName (str): Last name of the contact.
                    - customProperty1 (str): Value of custom property 1.
                    - customProperty2 (str): Value of custom property 2.
                    - ... (additional custom properties)
                - status (str): Status of the send operation.

    """

    if not all([template_id, message]):
        return {
            "status": "error",
            "message": "'template_id' and 'message' are required.",
        }

    to = message.get("to", None)
    cc = message.get("cc", None)
    bcc = message.get("bcc", None)
    from_ = message.get("from", None)
    replyTo = message.get("replyTo", None)
    if not to:
        return {
            "status": "error",
            "message": "Each 'to' entry must be a dictionary with a non-empty 'email' string.",
        }
    # Validate to
    for recipient in to:
        if (
            not isinstance(recipient, dict)
            or not isinstance(recipient.get("email"), str)
            or not recipient["email"]
        ):
            return {
                "status": "error",
                "message": "Each 'to' entry must be a dictionary with a non-empty 'email' string.",
            }

    # Validate cc
    if cc is not None:
        for recipient in cc:
            if (
                not isinstance(recipient, dict)
                or "email" not in recipient
                or not isinstance(recipient["email"], str)
                or not recipient["email"]
            ):
                return {
                    "status": "error",
                    "message": "Each 'cc' entry must be a dictionary with a non-empty 'email' string.",
                }

    # Validate bcc
    if bcc is not None:
        for recipient in bcc:
            if (
                not isinstance(recipient, dict)
                or "email" not in recipient
                or not isinstance(recipient["email"], str)
                or not recipient["email"]
            ):
                return {
                    "status": "error",
                    "message": "Each 'bcc' entry must be a dictionary with a non-empty 'email' string.",
                }

    # Validate from_
    if from_ is not None:
        if (
            not isinstance(from_, dict)
            or not isinstance(from_.get("email"), str)
            or not from_.get("email")
        ):
            return {
                "status": "error",
                "message": "'from' field must be a dictionary with 'email' and 'name' properties.",
            }

    # Validate replyTo
    if replyTo is not None:
        for recipient in replyTo:
            if (
                not isinstance(recipient, dict)
                or "email" not in recipient
                or not isinstance(recipient["email"], str)
                or not recipient["email"]
            ):
                return {
                    "status": "error",
                    "message": "Each 'replyTo' entry must be a dictionary with a non-empty 'email' string.",
                }

    # Check if the email template exists
    if not DB.get("templates", {}):
        DB["templates"] = {}
    if template_id not in DB["templates"]:
        return {
            "status": "error",
            "message": f"Email template with ID '{template_id}' not found.",
        }

    elif DB["templates"][template_id]["template_type"] != 2:
        return {
            "status": "error",
            "message": f"Template with ID '{template_id}' is not an email template.",
        }

    # --- HubSpot Contact Property Handling ---
    final_properties = customProperties.copy() if customProperties else {}

    # Iterate through recipients to apply contactProperties
    for recipient in to:
        recipient_email = recipient["email"]
        contact = DB["contacts"].get(recipient_email)
        if contact:
            # Merge contact properties with precedence over custom properties
            final_properties.update(contact)
        if contactProperties:
            final_properties.update(contactProperties)

    # Simulate sending the email (no actual sending)
    # Use a unique ID for each transactional email
    transactional_email_id = str(uuid.uuid4())
    log_entry = {
        "template_id": template_id,
        "transactional_email_id": transactional_email_id,  # Unique ID for the send
        "message": message,
        "properties": final_properties,  # Store merged properties
        "status": "sent",  # Assume successful send for simulation
    }
    DB["transactional_emails"][transactional_email_id] = log_entry  # Store by ID

    return {
        "status": "success",
        "message": f"Email sent successfully using template.",
        "template_id": template_id,
        "transactional_email_id": str(transactional_email_id),  # Return the unique ID
        "log": log_entry,
    }
