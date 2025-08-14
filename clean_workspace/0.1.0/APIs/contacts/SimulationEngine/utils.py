# Contacts API Utils

from .db import DB
from typing import Optional, Dict, Any, List
import uuid


def find_contact_by_id(resource_name: str) -> Optional[Dict[str, Any]]:
    """
    Finds any contact or user by its unique resourceName.
    
    It checks myContacts, otherContacts, and the directory.
    
    Args:
        resource_name: The unique identifier (e.g., "people/c123...").

    Returns:
        The contact dictionary if found, otherwise None.
    """
    for collection_key in ["myContacts", "otherContacts", "directory"]:
        contact = DB[collection_key].get(resource_name)
        if contact:
            return contact
    return None

def find_contact_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Finds a contact or user by their email address.
    
    Searches through all collections. Returns the first match.
    
    Args:
        email: The email address to search for.

    Returns:
        The contact dictionary if a match is found, otherwise None.
    """
    lower_email = email.lower()
    for collection_key in ["myContacts", "otherContacts", "directory"]:
        for contact in DB[collection_key].values():
            if "emailAddresses" in contact:
                for email_obj in contact.get("emailAddresses", []):
                    if email_obj.get("value", "").lower() == lower_email:
                        return contact
    return None

def generate_resource_name(prefix: str = "people/c") -> str:
    """
    Generates a new, unique resourceName using UUID.

    Args:
        prefix: The prefix for the resource name. Defaults to 'people/c'.

    Returns:
        A unique resource name string.
    """
    # Generate a random UUID (version 4)
    unique_id = uuid.uuid4()
    return f"{prefix}{unique_id}"

# --- Search and Filter Helpers ---

def search_collection(
    collection_name: str, query: Optional[str], max_results: int
) -> List[Dict[str, Any]]:
    """
    Searches a collection for a query string or lists all items.
    
    The query is matched against names, emails, and phone numbers.

    Args:
        collection_name: The key of the collection in the DB ('myContacts', etc.).
        query: The search term. If None or empty, lists all items.
        max_results: The maximum number of items to return.

    Returns:
        A list of matching contact dictionaries.
    """
    results = []
    contacts_to_search = list(DB[collection_name].values())
    
    # If no query, just return the first `max_results` items
    if not query:
        return contacts_to_search[:max_results]
        
    lower_query = query.lower()
    
    for contact in contacts_to_search:
        if len(results) >= max_results:
            break

        # Create a searchable string with all relevant fields
        search_haystack = []
        if "names" in contact:
            for name_obj in contact.get("names", []):
                search_haystack.append(name_obj.get("givenName", ""))
                search_haystack.append(name_obj.get("familyName", ""))

        if "emailAddresses" in contact:
            for email_obj in contact.get("emailAddresses", []):
                search_haystack.append(email_obj.get("value", ""))
        
        if "phoneNumbers" in contact:
            for phone_obj in contact.get("phoneNumbers", []):
                search_haystack.append(phone_obj.get("value", ""))

        if lower_query in " ".join(search_haystack).lower():
            results.append(contact)
            
    return results