from typing import Type, Dict, Any, Optional
from .SimulationEngine.db import DB

"""
API simulation for the '/me' resource.
"""
def get_me(projection: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieves the authenticated member's profile data from the database.

    Args:
        projection (Optional[str]): Field projection syntax for controlling which fields to return.
            The projection string should consist of comma-separated field names and may optionally
            be enclosed in parentheses. Defaults to None.

    Returns:
        Dict[str, Any]:
        - If no authenticated member exists, returns a dictionary with the key "error" and the value "No authenticated member."
        - If the authenticated member's profile is not found, returns a dictionary with the key "error" and the value "Authenticated person not found."
        - On successful retrieval, returns a dictionary with the following keys and value types:
            - 'data' (Dict[str, Any]): Dictionary of member profile data with keys:
                - 'id' (str): Unique identifier of the member.
                - 'localizedFirstName' (str): Member's first name.
                - 'localizedLastName' (str): Member's last name.
                - 'vanityName' (str): URL-friendly version of the member's name.
                - 'firstName' (Dict[str, Any]): Localized first name with keys:
                    - 'localized' (Dict[str, str]): Dictionary with locale keys mapping to the localized name:
                        - 'en_US' (str): English (US) localized name.
                    - 'preferredLocale' (Dict[str, str]): Dictionary with keys:
                        - 'country' (str): Country code (e.g., 'US').
                        - 'language' (str): Language code (e.g., 'en').
                - 'lastName' (Dict[str, Any]): Localized last name with keys:
                    - 'localized' (Dict[str, str]): Dictionary with locale keys mapping to the localized name:
                        - 'en_US' (str): English (US) localized name.
                    - 'preferredLocale' (Dict[str, str]): Dictionary with keys:
                        - 'country' (str): Country code (e.g., 'US').
                        - 'language' (str): Language code (e.g., 'en').
    """
    current_id = DB.get("current_person_id")
    if current_id is None:
        return {"error": "No authenticated member."}
    person = DB["people"].get(current_id)
    if person is None:
        return {"error": "Authenticated person not found."}

    if projection:
        projection = projection.strip()
        if projection.startswith("(") and projection.endswith(")"):
            projection = projection[1:-1]
        # Split by comma to get individual field names and strip spaces
        fields = [field.strip() for field in projection.split(",")]
        # Create a new dictionary with only the requested fields that exist in the person data
        projected_person = {field: person.get(field) for field in fields if field in person}
        return {"data": projected_person}

    return {"data": person}

def create_me(person_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Creates a new member profile and sets it as the current authenticated member.

    Args:
        person_data (Dict[str, Any]): Dictionary containing the new member's profile data with keys:
            - 'localizedFirstName' (str): Member's first name.
            - 'localizedLastName' (str): Member's last name.
            - 'vanityName' (str): URL-friendly version of the member's name.
            - 'firstName' (Dict[str, Any]): Localized first name with keys:
                - 'localized' (Dict[str, str]): Dictionary with locale keys mapping to the localized name:
                    - 'en_US' (str): English (US) localized name.
                - 'preferredLocale' (Dict[str, str]): Dictionary with keys:
                    - 'country' (str): Country code (e.g., 'US').
                    - 'language' (str): Language code (e.g., 'en').
            - 'lastName' (Dict[str, Any]): Localized last name with keys:
                - 'localized' (Dict[str, str]): Dictionary with locale keys mapping to the localized name:
                    - 'en_US' (str): English (US) localized name.
                - 'preferredLocale' (Dict[str, str]): Dictionary with keys:
                    - 'country' (str): Country code (e.g., 'US').
                    - 'language' (str): Language code (e.g., 'en').

    Returns:
        Dict[str, Any]:
        - If required fields ('localizedFirstName' or 'localizedLastName') are missing, returns a dictionary with the key "error" and a string value containing "Field {field} cannot be empty." separated by spaces for each missing field.
        - If an authenticated member already exists, returns a dictionary with the key "error" and the value "Authenticated member already exists."
        - On successful creation, returns a dictionary with the following keys and value types:
            - 'data' (Dict[str, Any]): Dictionary of created member profile with keys:
                - 'id' (str): Newly assigned unique identifier.
                - 'localizedFirstName' (str): Member's first name.
                - 'localizedLastName' (str): Member's last name.
                - 'vanityName' (str): URL-friendly version of the member's name.
                - 'firstName' (Dict[str, Any]): Localized first name with keys:
                    - 'localized' (Dict[str, str]): Dictionary with locale keys mapping to the localized name:
                        - 'en_US' (str): English (US) localized name.
                    - 'preferredLocale' (Dict[str, str]): Dictionary with keys:
                        - 'country' (str): Country code (e.g., 'US').
                        - 'language' (str): Language code (e.g., 'en').
                - 'lastName' (Dict[str, Any]): Localized last name with keys:
                    - 'localized' (Dict[str, str]): Dictionary with locale keys mapping to the localized name:
                        - 'en_US' (str): English (US) localized name.
                    - 'preferredLocale' (Dict[str, str]): Dictionary with keys:
                        - 'country' (str): Country code (e.g., 'US').
                        - 'language' (str): Language code (e.g., 'en').

    Raises:
        None: This function handles errors internally and returns them in the response.
    """
    if DB.get("current_person_id") is not None:
        return {"error": "Authenticated member already exists."}
    new_id = str(DB["next_person_id"])
    DB["next_person_id"] += 1
    person_data["id"] = new_id
    DB["people"][new_id] = person_data
    DB["current_person_id"] = new_id
    return {"data": person_data}

def update_me(person_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Updates the authenticated member's profile data in the database.

    Args:
        person_data (Dict[str, Any]): Dictionary containing the updated member profile data with keys:
            - 'localizedFirstName' (str): Updated first name.
            - 'localizedLastName' (str): Updated last name.
            - 'vanityName' (str): URL-friendly version of the member's name.
            - 'firstName' (Dict[str, Any]): Localized first name with keys:
                - 'localized' (Dict[str, str]): Dictionary with locale keys mapping to the localized name:
                    - 'en_US' (str): English (US) localized name.
                - 'preferredLocale' (Dict[str, str]): Dictionary with keys:
                    - 'country' (str): Country code (e.g., 'US').
                    - 'language' (str): Language code (e.g., 'en').
            - 'lastName' (Dict[str, Any]): Localized last name with keys:
                - 'localized' (Dict[str, str]): Dictionary with locale keys mapping to the localized name:
                    - 'en_US' (str): English (US) localized name.
                - 'preferredLocale' (Dict[str, str]): Dictionary with keys:
                    - 'country' (str): Country code (e.g., 'US').
                    - 'language' (str): Language code (e.g., 'en').

    Returns:
        Dict[str, Any]:
        - If no authenticated member exists, returns a dictionary with the key "error" and the value "No authenticated member."
        - If the authenticated member's profile is not found, returns a dictionary with the key "error" and the value "Authenticated member not found."
        - On successful update, returns a dictionary with the following keys and value types:
            - 'data' (Dict[str, Any]): Dictionary of updated member profile with keys:
                - 'id' (str): Member's unique identifier.
                - 'localizedFirstName' (str): Updated first name.
                - 'localizedLastName' (str): Updated last name.
                - 'vanityName' (str): URL-friendly version of the member's name.
                - 'firstName' (Dict[str, Any]): Localized first name with keys:
                    - 'localized' (Dict[str, str]): Dictionary with locale keys mapping to the localized name:
                        - 'en_US' (str): English (US) localized name.
                    - 'preferredLocale' (Dict[str, str]): Dictionary with keys:
                        - 'country' (str): Country code (e.g., 'US').
                        - 'language' (str): Language code (e.g., 'en').
                - 'lastName' (Dict[str, Any]): Localized last name with keys:
                    - 'localized' (Dict[str, str]): Dictionary with locale keys mapping to the localized name:
                        - 'en_US' (str): English (US) localized name.
                    - 'preferredLocale' (Dict[str, str]): Dictionary with keys:
                        - 'country' (str): Country code (e.g., 'US').
                        - 'language' (str): Language code (e.g., 'en').

    Raises:
        None: This function handles errors internally and returns them in the response.
    """
    current_id = DB.get("current_person_id")
    if current_id is None or current_id not in DB["people"]:
        return {"error": "Authenticated member not found."}
    person_data["id"] = current_id
    DB["people"][current_id] = person_data
    return {"data": person_data}

def delete_me() -> Dict[str, Any]:
    """
    Deletes the authenticated member's profile from the database.

    Returns:
        Dict[str, Any]:
        - If no authenticated member exists, returns a dictionary with the key "error" and the value "No authenticated member."
        - If the authenticated member's profile is not found, returns a dictionary with the key "error" and the value "Authenticated member not found."
        - On successful deletion, returns a dictionary with the following keys and value types:
            - 'status' (str): Success message confirming deletion.

    Raises:
        None: This function handles errors internally and returns them in the response.
    """
    current_id = DB.get("current_person_id")
    if current_id is None or current_id not in DB["people"]:
        return {"error": "Authenticated member not found."}
    del DB["people"][current_id]
    DB["current_person_id"] = None
    return {"status": "Authenticated member deleted."}