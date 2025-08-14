# gmail/SimulationEngine/utils.py
import shlex
from typing import Dict, List, Tuple

from .db import DB
from gmail.SimulationEngine.search_engine import search_engine_manager


def _ensure_user(userId: str) -> None:
    """Ensures that a user exists in the database.
    
    Args:
        userId (str): The user ID to check. Can be 'me' or an email address.
        
    Raises:
        ValueError: If the user does not exist in the database.
    """
    # Check if userId exists directly as a key
    if userId in DB["users"]:
        return
    
    # Check if userId is an email address that matches any user's profile
    for user_key, user_data in DB["users"].items():
        if user_data.get("profile", {}).get("emailAddress") == userId:
            return
    
    # User not found
    raise ValueError(f"User '{userId}' does not exist.")


def _resolve_user_id(userId: str) -> str:
    """Resolves a user ID to the actual database key.
    
    Args:
        userId (str): The user ID to resolve. Can be 'me' or an email address.
        
    Returns:
        str: The actual database key for the user.
        
    Raises:
        ValueError: If the user does not exist in the database.
    """
    # Check if userId exists directly as a key
    if userId in DB["users"]:
        return userId
    
    # Check if userId is an email address that matches any user's profile
    for user_key, user_data in DB["users"].items():
        if user_data.get("profile", {}).get("emailAddress") == userId:
            return user_key
    
    # User not found
    raise ValueError(f"User '{userId}' does not exist.")


def _next_counter(counter_name: str) -> int:
    current_val = DB["counters"].get(counter_name, 0)
    new_val = current_val + 1
    DB["counters"][counter_name] = new_val
    return new_val

def reset_db():
    new_db = {
        "users": {
            "me": {
                "profile": {
                    "emailAddress": "me@gmail.com",
                    "messagesTotal": 0,
                    "threadsTotal": 0,
                    "historyId": "1",
                },
                "drafts": {},
                "messages": {},
                "threads": {},
                "labels": {},
                "settings": {
                    "imap": {"enabled": False},
                    "pop": {"accessWindow": "disabled"},  # default for pop
                    "vacation": {"enableAutoReply": False},
                    "language": {"displayLanguage": "en"},
                    "autoForwarding": {"enabled": False},
                    "sendAs": {},
                },
                "history": [],
                "watch": {},
            }
        },
        "counters": {
            "message": 0,
            "thread": 0,
            "draft": 0,
            "label": 10,
            "history": 0,
            "smime": 0,
        },
        "attachments": {}
    }

    # Add system labels
    system_labels = [
        ("INBOX", "INBOX"), 
        ("UNREAD", "UNREAD"),
        ("IMPORTANT", "IMPORTANT"),
        ("SENT", "SENT"),
        ("DRAFT", "DRAFT"),
        ("TRASH", "TRASH"),
        ("SPAM", "SPAM")
    ]
    
    labels_dict = {}
    for i, (name, label_id) in enumerate(system_labels):
        labels_dict[label_id] = {
            "id": label_id,
            "name": name,
            "type": "system",
            "messageListVisibility": "show",
            "labelListVisibility": "labelShow",
        }
    new_db["users"]["me"]["labels"] = labels_dict

    DB.clear()
    DB.update(new_db)


def _parse_query_string(query_str: str) -> Tuple[Dict[str, List[str]], str]:
    """
    Parses a query string into field-specific queries and a general text query.
    Uses shlex to handle quoted phrases correctly.
    """
    try:
        tokens = shlex.split(query_str)
    except ValueError:
        tokens = query_str.split()

    field_queries, text_parts = {}, []
    field_map = {"from": "sender", "to": "recipient", "label": "labels", "subject": "subject"}

    for token in tokens:
        if ":" in token:
            key, value = token.split(":", 1)
            if key.lower() in field_map:
                field_key = field_map[key.lower()]
                if field_key not in field_queries:
                    field_queries[field_key] = []
                field_queries[field_key].append(value)
            else:
                text_parts.append(token)
        else:
            text_parts.append(token)
            
    return field_queries, " ".join(text_parts)

def search_ids(query_text, filter_kwargs):
    engine = search_engine_manager.get_engine()
    return set(obj["id"] for obj in engine.search(query_text, filter=filter_kwargs))

def label_filter(msg, include_spam_trash, labelIds):
    msg_label_ids = set(msg.get("labelIds", []))
    if not include_spam_trash and (
        "TRASH" in msg_label_ids or "SPAM" in msg_label_ids
    ):
        return False
    if labelIds:
        labelIds_upper = set(l.upper() for l in labelIds)
        if msg_label_ids.isdisjoint(labelIds_upper):
            return False
    return True