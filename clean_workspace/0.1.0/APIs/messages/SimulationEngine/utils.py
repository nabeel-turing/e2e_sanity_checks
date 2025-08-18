from typing import Any, Dict, List, Optional
from datetime import datetime
from dateutil import parser as dateutil_parser
from .db import DB
from .models import APIName, Action

VALID_STATUSES = {"sent", "failed", "pending"}

def _ensure_recipient_exists(resource_name: str) -> None:
    """Ensures that a recipient exists in the database by their resource name.
    
    Args:
        resource_name (str): The resource name to check (e.g., 'people/c1a2b3c4...').
        
    Raises:
        ValueError: If the recipient does not exist in the database.
    """
    if resource_name not in DB["recipients"]:
        raise ValueError(f"Recipient with resource name '{resource_name}' does not exist.")


def _next_counter(counter_name: str) -> int:
    """Get the next counter value and increment it.
    
    Args:
        counter_name (str): The name of the counter to increment.
        
    Returns:
        int: The next counter value.
    """
    current_val = DB["counters"].get(counter_name, 0)
    new_val = current_val + 1
    DB["counters"][counter_name] = new_val
    return new_val


def _validate_phone_number(phone_number: str) -> bool:
    """Basic validation for phone number format.
    
    Args:
        phone_number (str): The phone number to validate.
        
    Returns:
        bool: True if valid format, False otherwise.
    """
    if not phone_number:
        return False
    
    # Basic validation - should start with + or contain only digits, spaces, hyphens, parentheses
    import re
    pattern = r'^[\+]?[1-9][\d\s\-\(\)]{7,}$'
    return bool(re.match(pattern, phone_number.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')))


def _get_recipient_by_phone(phone_number: str) -> Optional[dict]:
    """Find a recipient's phone-specific data object by phone number.
    
    Args:
        phone_number (str): The phone number to search for.
        
    Returns:
        Optional[dict]: The recipient's 'phone' data if found, None otherwise.
    """
    for contact_data in DB["recipients"].values():
        for number_info in contact_data.get("phoneNumbers", []):
            if number_info.get("value") == phone_number:
                # Return the nested 'phone' object which matches the Recipient model
                return contact_data.get("phone")
    return None


def _add_message_to_history(message_data: dict) -> None:
    """Add a message to the message history.
    
    Args:
        message_data (dict): The message data to add to history.
    """
    DB["message_history"].append(message_data)


def _list_messages(
    recipient_id: Optional[str] = None,
    recipient_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Lists messages from the database with optional filters.

    Args:
        recipient_id (Optional[str]): Filter messages by the recipient's contact ID.
        recipient_name (Optional[str]): Filter messages by the recipient's name (case-insensitive).
        start_date (Optional[str]): Filter messages sent on or after this date (ISO 8601 format).
        end_date (Optional[str]): Filter messages sent on or before this date (ISO 8601 format).
        status (Optional[str]): Filter messages by status (e.g., "sent", "failed").

    Returns:
        List[Dict[str, Any]]: A list of message objects matching the criteria. Each dict contains:
            - id (str): The unique message ID.
            - recipient (Dict): Information about the recipient.
                - contact_id (str): The contact's unique ID.
                - contact_name (str): The contact's name.
            - timestamp (str): The message timestamp in ISO 8601 format.
            - status (str): The message status (e.g., "sent").
        
    Raises:
        TypeError: If `recipient_id`, `recipient_name`, `start_date`, `end_date`, or `status`
                   are provided but are not strings.
        ValueError: If `start_date` or `end_date` are provided with an invalid ISO 8601 format.
    """
    # --- Input Validation ---
    if recipient_id is not None and not isinstance(recipient_id, str):
        raise TypeError("recipient_id must be a string.")
    if recipient_name is not None and not isinstance(recipient_name, str):
        raise TypeError("recipient_name must be a string.")
    if start_date is not None and not isinstance(start_date, str):
        raise TypeError("start_date must be a string.")
    if end_date is not None and not isinstance(end_date, str):
        raise TypeError("end_date must be a string.")
    if status is not None and not isinstance(status, str):
        raise TypeError("status must be a string.")

    if status and status not in VALID_STATUSES:
        raise ValueError(f"Invalid status '{status}'. Must be one of {sorted(list(VALID_STATUSES))}.")

    if recipient_id and recipient_id not in DB.get("recipients", {}):
        raise ValueError(f"Recipient with id '{recipient_id}' not found.")

    all_recipients = DB.get("recipients", {}).values()

    # Build a list of known recipient names from the recipients DB
    searchable_names: List[str] = []
    if recipient_name:
        for recipient_record in all_recipients:
            if not isinstance(recipient_record, dict):
                continue
            # Top-level contact_name
            top_level_name = recipient_record.get("contact_name")
            if isinstance(top_level_name, str):
                searchable_names.append(top_level_name)
            # Nested phone.contact_name (Contacts-linked shape)
            phone_obj = recipient_record.get("phone")
            if isinstance(phone_obj, dict):
                phone_name = phone_obj.get("contact_name")
                if isinstance(phone_name, str):
                    searchable_names.append(phone_name)
            # Derive from names[0].givenName/familyName or displayName if present
            names_list = recipient_record.get("names")
            if isinstance(names_list, list) and names_list:
                primary_name = names_list[0] if isinstance(names_list[0], dict) else None
                if isinstance(primary_name, dict):
                    display_name = primary_name.get("displayName") or ""
                    given = primary_name.get("givenName") or ""
                    family = primary_name.get("familyName") or ""
                    combined = f"{given} {family}".strip()
                    if display_name:
                        searchable_names.append(display_name)   
                    elif combined:
                        searchable_names.append(combined)

        # Raise only if we have any known names and none match
        if searchable_names and not any(
            recipient_name.lower() in name.lower() for name in searchable_names
        ):
            raise ValueError(f"Recipient with name containing '{recipient_name}' not found.")

    messages = list(DB.get("messages", {}).values())
    
    if recipient_id:
        messages = [m for m in messages if m.get("recipient", {}).get("contact_id") == recipient_id]

    if recipient_name:
        messages = [
            m for m in messages
            if recipient_name.lower() in m.get("recipient", {}).get("contact_name", "").lower()
        ]

    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            messages = [
                m for m in messages
                if datetime.fromisoformat(m["timestamp"].replace("Z", "+00:00")) >= start_dt
            ]
        except (ValueError, KeyError):
            raise ValueError("Invalid start_date format. Use ISO 8601 format.")

    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
            messages = [
                m for m in messages
                if datetime.fromisoformat(m["timestamp"].replace("Z", "+00:00")) <= end_dt
            ]
        except (ValueError, KeyError):
            raise ValueError("Invalid end_date format. Use ISO 8601 format.")

    if status:
        messages = [m for m in messages if m.get("status") == status]

    return messages


def _delete_message(message_id: str) -> bool:
    """Deletes a message from the database and its history.

    Args:
        message_id (str): The ID of the message to delete.

    Returns:
        bool: True if the message was successfully deleted.
        
    Raises:
        TypeError: If `message_id` is not a string.
        ValueError: If `message_id` is an empty string or the message is not found.
    """
    # --- Input Validation ---
    if not isinstance(message_id, str):
        raise TypeError("message_id must be a string.")
    if not message_id:
        raise ValueError("message_id cannot be an empty string.")

    if message_id not in DB.get("messages", {}):
        raise ValueError(f"Message with id '{message_id}' not found.")

    del DB["messages"][message_id]
    
    # Also remove from message history
    DB["message_history"] = [
        item for item in DB.get("message_history", []) if item.get("id") != message_id
    ]
    
    return True 



 