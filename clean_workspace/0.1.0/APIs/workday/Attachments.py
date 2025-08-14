"""
This module provides functionality for managing attachments in the Workday Strategic Sourcing system.
It supports operations for creating, retrieving, updating, and deleting attachments using both
internal IDs and external IDs.
"""

from typing import List, Dict, Any, Optional
from .SimulationEngine import db

def get(filter_id_equals: str) -> List[Dict[str, Any]]:
    """
    Retrieve a filtered list of attachments based on specified IDs.

    This function returns a list of attachments matching the provided IDs, with a maximum
    limit of 50 attachments per request.

    Args:
        filter_id_equals (str): Comma-separated string of attachment IDs to filter by.

    Returns:
        List[Dict[str, Any]]: A list of attachment dictionaries, where each attachment contains:
            - id (int): Attachment identifier string.
            - name (str): Attachment file name.
            - type (str): Object type, should always be attachments.
            - uploaded_by (str): Email or Identifier of the uploader.
            - external_id (str): Attachment external identifier.
            - attributes (dict): Attachment attributes. May contain the following keys:
                - title (str): Attachment title.
                - size (str): Attachment file size in bytes.
                - external_id (str): Attachment external identifier.
                - download_url (str): Attachment download URL.
                - download_url_expires_at (datetime): Download URL expiration time.
                - uploaded_at (datetime): Time of upload.
            - Any other attachment-specific attributes as defined in the system.

    Note:
        The result is limited to 50 attachments regardless of the number of IDs provided.
    """
    ids = filter_id_equals.split(",")
    result = []
    for attachment_id, attachment in db.DB["attachments"].items():
        if str(attachment_id) in ids:
            result.append(attachment)
        if len(result) >= 50:
            break
    return result

def post(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new attachment in the system.

    This function creates a new attachment with the provided data. It checks for duplicate
    external IDs and generates a new unique internal ID for the attachment.

    Args:
        data (Dict[str, Any]): Dictionary containing attachment data with the following keys:

            - type (str, required): Object type, should always be attachments.
            - name (str, required): Attachment file name.
            - uploaded_by (str): Email/identifier of uploader
            - external_id (str, max_length=255): Attachment external identifier.
            - attributes (dict): Attachment attributes which may contain any of the following keys:
                - title (str, max_length=255): Attachment title.
                - size (str): Attachment file size in bytes.
                - external_id (str, max_length=255): Attachment external identifier.
                - download_url (str): Attachment download URL.
                - download_url_expires_at (datetime): Download URL expiration time.
                - uploaded_at (datetime): Upload timestamp
            - relationships (dict): One of Contract, Event, Project, or Supplier Company containing:
                - type (str, required): Object type.
                - id (int, required): Object identifier string.

    Returns:
        Dict[str, Any]: A dictionary containing the attachment data.
            - If an attachment with the provided external_id already exists, returns a dictionary with:
                - "error" (str): "Attachment with this external_id already exists."
            - On successful creation, returns a dictionary with the following keys:
                - "id" (int): Auto-generated unique identifier for the attachment
                - "type" (str): Object type, should be "attachments"
                - "name" (str): Attachment file name
                - "uploaded_by" (str): Email/identifier of uploader
                - "external_id" (str): Attachment external identifier.
                - "attributes" (dict): Attachment attributes. May contain any of the following keys:
                    - title (str): Title (max 255 chars)
                    - size (str): File size in bytes
                    - external_id (str): External identifier (max 255 chars)
                    - download_url (str): Download URL
                    - download_url_expires_at (datetime): URL expiration time
                    - uploaded_at (datetime): Upload timestamp
                - Any other attachment-specific attributes as defined.
    """
    external_id = data.get("external_id")

    # Check if external_id already exists
    if external_id and any(
        attachment.get("external_id") == external_id for attachment in db.DB["attachments"].values()
    ):
        return {"error": "Attachment with this external_id already exists."}

    attachment_id = max(
        [0] + [int(k) for k in db.DB["attachments"].keys()]
    ) + 1

    data["id"] = attachment_id
    db.DB["attachments"][str(attachment_id)] = data
    return data

def list_attachments(filter_id_equals: str = None) -> Dict[str, Any]:
    """
    Returns a filtered list of attachments based on the `filter[id_equals]` param.
    The result is limited to 50 attachments.

    Args:
        filter_id_equals (str): Comma-separated string of attachment IDs to filter by. Defaults to None.
            If None, all attachments are returned (up to the limit).

    Returns:
        Dict[str, Any]: A dictionary containing:
            - data (List[Dict[str, Any]]): List of attachment objects containing any of the following keys:
                - "id" (int): Identifier for the attachment
                - "type" (str): Object type, should be "attachments"
                - "name" (str): Attachment file name
                - "uploaded_by" (str): Email/identifier of uploader
                - "external_id" (str): Attachment external identifier.
                - "attributes" (dict): Attachment attributes containing any of the following keys:
                    - title (str): Title (max 255 chars)
                    - size (str): File size in bytes
                    - external_id (str): External identifier (max 255 chars)
                    - download_url (str): Download URL
                    - download_url_expires_at (datetime): URL expiration time
                    - uploaded_at (datetime): Upload timestamp
                - Any other attachment-specific attributes as defined in the system.
            - links (Dict[str, str]): Resource links
            - meta (Dict[str, int]): Metadata containing the total count of the results

    Note:
        The result is limited to 50 attachments per request.
    """
    attachments = list(db.DB["attachments"].values())
    if filter_id_equals:
        ids = filter_id_equals.split(",")
        attachments = [
            attachment
            for attachment in attachments
            if str(attachment.get("id")) in ids
        ]
    return {
        "data": attachments[:50],
        "links": {
            "self": "services/attachments/v1/attachments"
        },
        "meta": {"count": len(attachments[:50])},
    }

def get_attachment_by_id(id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve a specific attachment by its internal ID.

    Args:
        id (int): The internal ID of the attachment to retrieve.

    Returns:
        Optional[Dict[str, Any]]: The attachment object if found, None otherwise.
            The object contains any of the following keys:
                - "id" (int): Identifier for the attachment
                - "type" (str): Object type, should be "attachments"
                - "name" (str): Attachment file name
                - "uploaded_by" (str): Email/identifier of uploader
                - "external_id" (str): Attachment external identifier.
                - "attributes" (dict): Attachment attributes containing any of the following keys:
                    - title (str): Title (max 255 chars)
                    - size (str): File size in bytes
                    - external_id (str): External identifier (max 255 chars)
                    - download_url (str): Download URL
                    - download_url_expires_at (datetime): URL expiration time
                    - uploaded_at (datetime): Upload timestamp
                - Any other attachment-specific attributes as defined in the system.
    """
    attachment = db.DB["attachments"].get(str(id))
    return attachment

def patch_attachment_by_id(id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Update an existing attachment by its internal ID.

    Args:
        id (int): The internal ID of the attachment to update.
        data (Dict[str, Any]): Dictionary containing the fields to update with their new values.

    Returns:
        Optional[Dict[str, Any]]: The updated attachment object if found and updated. None if the attachment does not exist. 
        The object contains any of the following keys:
            - "id" (int): Identifier for the attachment
            - "type" (str): Object type, should be "attachments"
            - "name" (str): Attachment file name
            - "uploaded_by" (str): Email/identifier of uploader
            - "external_id" (str): Attachment external identifier.
            - "attributes" (dict): Attachment attributes. May contain any of the following keys:
                - title (str): Title (max 255 chars)
                - size (str): File size in bytes
                - external_id (str): External identifier (max 255 chars)
                - download_url (str): Download URL
                - download_url_expires_at (datetime): URL expiration time
                - uploaded_at (datetime): Upload timestamp
            - Any other attachment-specific attributes as defined in the system.
    

    Note:
        The ID field in the data dictionary will be ignored and replaced with the id provided as argument.
    """
    if str(id) in db.DB["attachments"]:
        db.DB["attachments"][str(id)].update(data)
        db.DB["attachments"][str(id)]["id"] = id
        return db.DB["attachments"][str(id)]
    return None

def delete_attachment_by_id(id: int) -> bool:
    """
    Delete an attachment by its internal ID.

    Args:
        id (int): The internal ID of the attachment to delete.

    Returns:
        bool: True if the attachment was successfully deleted, False if the attachment
            does not exist.
    """
    if str(id) in db.DB["attachments"]:
        del db.DB["attachments"][str(id)]
        return True
    return False

def get_attachment_by_external_id(external_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a specific attachment by its external ID.

    Args:
        external_id (str): The external ID of the attachment to retrieve.

    Returns:
        Optional[Dict[str, Any]]: The attachment object if found, None otherwise.
            The object contains any of the following keys:
                - "id" (int): Identifier for the attachment
                - "type" (str): Object type, should be "attachments"
                - "name" (str): Attachment file name
                - "uploaded_by" (str): Email/identifier of uploader
                - "attributes" (dict): Attachment attributes. May contain any of the following keys:
                    - title (str): Title (max 255 chars)
                    - size (str): File size in bytes
                    - external_id (str): External identifier (max 255 chars)
                    - download_url (str): Download URL
                    - download_url_expires_at (datetime): URL expiration time
                    - uploaded_at (datetime): Upload timestamp
                - Any other attachment-specific attributes as defined in the system.
    """
    for attachment in db.DB["attachments"].values():
        if attachment.get("external_id") == external_id:
            return attachment
    return None

def patch_attachment_by_external_id(external_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Update an existing attachment by its external ID.

    Args:
        external_id (str): The external ID of the attachment to update.
        data (Dict[str, Any]): Dictionary containing the fields to update with their new values.

    Returns:
        Optional[Dict[str, Any]]: The updated attachment object if found and updated,
            None if the attachment does not exist.
            The object contains any of the following keys:
                - "id" (int): Identifier for the attachment
                - "type" (str): Object type, should be "attachments"
                - "name" (str): Attachment file name
                - "uploaded_by" (str): Email/identifier of uploader
                - external_id (str): Attachment external identifier.
                - "attributes" (dict): Attachment attributes. May contain any of the following keys:
                    - title (str): Title (max 255 chars)
                    - size (str): File size in bytes
                    - external_id (str): External identifier (max 255 chars)
                    - download_url (str): Download URL
                    - download_url_expires_at (datetime): URL expiration time
                    - uploaded_at (datetime): Upload timestamp
                - Any other attachment-specific attributes as defined in the system.

    Note:
        The external_id field in the data dictionary will be ignored and replaced with
        the provided external_id.
    """
    for attachment_id, attachment in db.DB["attachments"].items():
        if attachment.get("external_id") == external_id:
            db.DB["attachments"][attachment_id].update(data)
            db.DB["attachments"][attachment_id]["external_id"] = external_id
            return db.DB["attachments"][attachment_id]
    return None

def delete_attachment_by_external_id(external_id: str) -> bool:
    """
    Delete an attachment by its external ID.

    Args:
        external_id (str): The external ID of the attachment to delete.

    Returns:
        bool: True if the attachment was successfully deleted, False if the attachment
            does not exist.
    """
    for attachment_id, attachment in db.DB["attachments"].items():
        if attachment.get("external_id") == external_id:
            del db.DB["attachments"][attachment_id]
            return True
    return False 