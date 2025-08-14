# APIs/hubspot/TransactionalEmails.py
from typing import Dict, Any, Optional
import uuid
from hubspot.SimulationEngine.db import DB


def sendSingleEmail(
    message: Dict[str, Any], customProperties: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Sends a single transactional email.

    Args:
        message (Dict[str, Any]): An object containing email content and recipient info.
            - to (str): Email address of the recipient.
            - from (str): Email address of the sender.
            - subject (str): Subject line of the email.
            - htmlBody (str): HTML content of the email.
            - cc (Optional[List[str]]): CC recipient email address(es).
            - bcc (Optional[List[str]]): BCC recipient email address(es).
            - replyTo (Optional[str]): Reply-to email address.
        customProperties (Optional[Dict[str, Any]]): Custom properties for the email.
            Can include any key-value pairs for email personalization.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - success (bool): Whether the email was sent successfully.
            - message (str): A description of the operation result.
            - email_id (str): A unique identifier for the sent email (only on success).

    """
    if not isinstance(message, dict):
        return {"success": False, "message": "Message must be an object."}
    if not all(key in message for key in ["to", "from", "subject", "htmlBody"]):
        return {
            "success": False,
            "message": "Message must contain 'to', 'from', 'subject', and 'htmlBody'.",
        }

    email_id = str(uuid.uuid4())

    # Simulate sending the email (store in DB)
    if "transactional_emails" not in DB:
        DB["transactional_emails"] = {}

    if email_id not in DB["transactional_emails"]:
        DB["transactional_emails"][email_id] = []

    DB["transactional_emails"][email_id].append(
        {
            "message": message,
            "customProperties": customProperties,
            "status": "sent",
            "email_id": email_id,
        }
    )

    return {
        "success": True,
        "message": f"Transactional email sent successfully.",
        "email_id": email_id,
    }
