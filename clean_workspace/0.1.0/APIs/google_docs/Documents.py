"""
Document operations for the Google Docs API simulation.

Represents a Google Docs document with methods for document operations.

This class provides methods for creating, retrieving, and updating Google Docs documents,
including handling document content, styles, and collaborative features.

"""

import uuid
from typing import Dict, Any, List, Optional, Tuple

from .SimulationEngine.models import InsertTextRequestModel, UpdateDocumentStyleRequestModel
from .SimulationEngine.db import DB
from .SimulationEngine.utils import _ensure_user, _next_counter


def get(
    documentId: str,
    suggestionsViewMode: Optional[str] = None,
    includeTabsContent: bool = False,
    userId: str = "me",
) -> Dict[str, Any]:
    """Get a document by ID.

    Args:
        documentId (str): The ID of the document to retrieve. Cannot be empty or whitespace.
        suggestionsViewMode (Optional[str]): The mode for viewing suggestions.
            Common values include "DEFAULT" and "SUGGESTIONS_INLINE". 
            If None, the document's existing setting is preserved.
        includeTabsContent (bool): Whether to include tab content. Defaults to False.
        userId (str): The ID of the user performing the action. Defaults to "me".
            Cannot be empty or whitespace.

    Returns:
        Dict[str, Any]: The document data with the following structure:
                Base document fields:
                - id (str): Unique identifier for the document
                - driveId (str): ID of the drive containing the document (can be empty)
                - name (str): Title/name of the document
                - mimeType (str): MIME type ("application/vnd.google-apps.document")
                - createdTime (str): ISO 8601 timestamp when document was created
                - modifiedTime (str): ISO 8601 timestamp when document was last modified
                - parents (List[str]): List of parent folder IDs
                - owners (List[str]): List of owner email addresses
                - content (List[Dict[str, Any]]): Document content with structure:
                    - elementId (str): Unique identifier for the content element
                    - text (str): Text content of the element
                - tabs (List[Dict[str, Any]]): List of document tabs (usually empty)
                - permissions (List[Dict[str, Any]]): List of permission objects with structure:
                    - role (str): Permission level ("owner", "writer", "reader")
                    - type (str): Permission type ("user", "group", "domain", "anyone")
                    - emailAddress (str): Email address of the user/group
                
                Conditionally added fields:
                - suggestionsViewMode (str): Present if suggestionsViewMode parameter was provided
                - includeTabsContent (bool): Present if includeTabsContent parameter was True
                - comments (Dict[str, Any]): Dictionary of comments associated with this document:
                    - Key: comment ID (str)
                    - Value: Comment object with structure:
                        - id (str): Unique comment identifier
                        - fileId (str): ID of the document this comment belongs to
                        - content (str): Comment text content
                        - author (Dict[str, str]): Author information:
                            - displayName (str): Author's display name
                            - emailAddress (str): Author's email address
                        - createdTime (str): ISO 8601 timestamp when comment was created
                - replies (Dict[str, Any]): Dictionary of replies associated with this document:
                    - Key: reply ID (str)
                    - Value: Reply object with structure:
                        - id (str): Unique reply identifier
                        - commentId (str): ID of the comment this reply belongs to
                        - fileId (str): ID of the document this reply belongs to
                        - content (str): Reply text content
                        - author (Dict[str, str]): Author information:
                            - displayName (str): Author's display name
                            - emailAddress (str): Author's email address
                        - createdTime (str): ISO 8601 timestamp when reply was created
                - labels (Dict[str, Any]): Dictionary of labels associated with this document:
                    - Key: label ID (str)
                    - Value: Label object with structure:
                        - id (str): Unique label identifier
                        - fileId (str): ID of the document this label belongs to
                        - name (str): Label name
                        - color (str): Label color in hex format (e.g., "#FF0000")
                - accessproposals (Dict[str, Any]): Dictionary of access proposals for this document:
                    - Key: proposal ID (str)
                    - Value: Access proposal object with structure:
                        - id (str): Unique proposal identifier
                        - fileId (str): ID of the document this proposal is for
                        - role (str): Requested permission level ("reader", "writer", "owner")
                        - state (str): Proposal state ("pending", "approved", "rejected")
                        - requester (Dict[str, str]): Requester information:
                            - displayName (str): Requester's display name
                            - emailAddress (str): Requester's email address
                        - createdTime (str): ISO 8601 timestamp when proposal was created

    Raises:
        TypeError: If `documentId` is not a string.
        TypeError: If `suggestionsViewMode` is provided and is not a string.
        TypeError: If `includeTabsContent` is not a boolean.
        TypeError: If `userId` is not a string.
        ValueError: If `documentId` or `userId` is empty or consists only of whitespace.

        ValueError: If the document is not found.
        KeyError: If the `userId` is not found.
        
    """
    # Input Validation
    if not isinstance(documentId, str):
        raise TypeError("documentId must be a string.")
    if not documentId or not documentId.strip():
        raise ValueError("documentId cannot be empty or consist only of whitespace.")
        
    if suggestionsViewMode is not None and not isinstance(suggestionsViewMode, str):
        raise TypeError("suggestionsViewMode must be a string or None.")
    if not isinstance(includeTabsContent, bool):
        raise TypeError("includeTabsContent must be a boolean.")
    if not isinstance(userId, str):
        raise TypeError("userId must be a string.")
    if not userId or not userId.strip():
        raise ValueError("userId cannot be empty or consist only of whitespace.")

    _ensure_user(userId) # This call is assumed to handle user existence validation or raise an error.

    # The check below assumes _ensure_user has validated userId.
    # If userId itself was invalid and _ensure_user didn't raise,
    # DB["users"][userId] would raise a KeyError.
    if documentId not in DB["users"][userId]["files"]:
        raise ValueError(f"Document '{documentId}' not found")

    document = DB["users"][userId]["files"][documentId].copy()

    if suggestionsViewMode:
        document["suggestionsViewMode"] = suggestionsViewMode

    if includeTabsContent:
        document["includeTabsContent"] = includeTabsContent

    # Attach comments, replies, labels, accessproposals related to this doc
    # These accesses assume the structure of DB is consistent if userId and documentId are valid.
    document["comments"] = {
        cid: c
        for cid, c in DB["users"][userId]["comments"].items()
        if c["fileId"] == documentId
    }
    document["replies"] = {
        rid: r
        for rid, r in DB["users"][userId]["replies"].items()
        if r["fileId"] == documentId
    }
    document["labels"] = {
        lid: l
        for lid, l in DB["users"][userId]["labels"].items()
        if l["fileId"] == documentId
    }
    document["accessproposals"] = {
        pid: p
        for pid, p in DB["users"][userId]["accessproposals"].items()
        if p["fileId"] == documentId
    }

    return document


def create(
    title: str = "Untitled Document", userId: str = "me"
) -> Tuple[Dict[str, Any], int]:
    """Create a new document.

    Args:
        title (str): The title of the document. Defaults to "Untitled Document".
        userId (str): The ID of the user. Defaults to "me".
            Must be a non-empty string.

    Returns:
        Tuple[Dict[str, Any], int]: A tuple containing:
            - document (Dict[str, Any]): The created document data with the following structure:
                - id (str): Unique document identifier (UUID format)
                - driveId (str): Drive identifier (empty string for new documents)
                - name (str): Document title
                - mimeType (str): Document MIME type ("application/vnd.google-apps.document")
                - createdTime (str): Creation timestamp in ISO format
                - modifiedTime (str): Last modification timestamp in ISO format
                - parents (List[str]): List of parent folder IDs
                - owners (List[str]): List of owner email addresses
                - suggestionsViewMode (str): Suggestions viewing mode ("DEFAULT")
                - includeTabsContent (bool): Whether to include tabs content (False)
                - content (List[Dict]): Document content elements (empty for new documents)
                - tabs (List[Dict]): Document tabs (empty for new documents)
                - permissions (List[Dict]): Access permissions with structure:
                    - role (str): Permission role (e.g., "owner")
                    - type (str): Permission type (e.g., "user")
                    - emailAddress (str): User's email address
                - trashed (bool): Whether document is in trash (False)
                - starred (bool): Whether document is starred (False)
                - size (int): Document size in bytes (0 for new documents)
            - status_code (int): HTTP status code (200 for success)

    Raises:
        TypeError: If 'title' or 'userId' is not a string.
        KeyError: If the specified `userId` does not exist in the database or
                  if expected data structures for the user are missing
                  (this error is propagated from internal operations).

    """
    # --- Input Validation ---
    if not isinstance(title, str):
        raise TypeError(f"Argument 'title' must be a string, got {type(title).__name__}.")
    if not isinstance(userId, str):
        raise TypeError(f"Argument 'userId' must be a string, got {type(userId).__name__}.")
    
    # Value validation
    if not userId.strip():
        raise ValueError("Argument 'userId' cannot be empty or only whitespace.")
    # --- End of Input Validation ---

    _ensure_user(userId) # This call is assumed to exist and might raise errors (e.g., KeyError)

    documentId = str(uuid.uuid4())
    # The following DB access can raise KeyError if userId is not in DB or structure is unexpected
    user_data = DB["users"][userId]
    user_email = user_data["about"]["user"]["emailAddress"]

    document = {
        "id": documentId,
        "driveId": "",
        "name": title,
        "mimeType": "application/vnd.google-apps.document",
        "createdTime": "2025-03-11T09:00:00Z",
        "modifiedTime": "2025-03-11T09:00:00Z",
        "parents": [],
        "owners": [user_email],
        "suggestionsViewMode": "DEFAULT",
        "includeTabsContent": False,
        "content": [],
        "tabs": [],
        "permissions": [{"role": "owner", "type": "user", "emailAddress": user_email}],
        "trashed": False,
        "starred": False,
        "size": '0',
    }

    DB["users"][userId]["files"][documentId] = document # This access can also raise KeyError
    _next_counter("file", userId) # This call is assumed to exist

    return document, 200


def batchUpdate(
    documentId: str, requests: List[Dict[str, Any]], userId: str = "me"
) -> Tuple[Dict[str, Any], int]:
    """Apply batch updates to a document.

    Args:
        documentId (str): The ID of the document to update.
        requests (List[Dict[str, Any]]): A list of update requests to apply. Each dictionary
            in the list must be one of the specified request types. Each request
            dictionary typically has a single key identifying the type of request
            (e.g., 'insertText'), and its value is a dictionary containing the
            parameters for that request. The supported request types and their
            structures are:
            - InsertTextRequest: Corresponds to a dictionary with an 'insertText' key.
                'insertText' (Dict[str, Any]): Inserts text into the document.
                    'text' (str): The text to insert.
                    'location' (Dict[str, Any]): Specifies where to insert the text.
                        'index' (int): The zero-based index in the document's content
                                       where the text will be inserted.
            - UpdateDocumentStyleRequest: Corresponds to a dictionary with an
              'updateDocumentStyle' key.
                'updateDocumentStyle' (Dict[str, Any]): Updates the document's style.
                    'documentStyle' (Any): The new document style to apply. The specific
                                           structure of this dictionary will depend on how
                                           document styles are defined in your system.
        userId (str): The ID of the user. Defaults to "me".

    Returns:
        Tuple[Dict[str, Any], int]: The update response and HTTP status code.

    Raises:
        TypeError: If `documentId` or `userId` are not strings or `requests` is not a list
            or any item in `requests` is not a dictionary with a valid request type.
        pydantic.ValidationError: If any item in `requests` does not conform to the defined
            structures (e.g., InsertTextRequestModel, UpdateDocumentStyleRequestModel),
            such as incorrect field types, missing required fields, or including extra fields.
        FileNotFoundError: If the document is not found.

    """
    # --- BEGIN INPUT VALIDATION ---
    if not isinstance(documentId, str):
        raise TypeError("documentId must be a string.")
    if not isinstance(userId, str):
        raise TypeError("userId must be a string.")
    if not isinstance(requests, List):
        raise TypeError("requests must be a list.")

    for request in requests:
        if not isinstance(request, dict):
            raise TypeError("request must be a dictionary.")
        if not any(key in request for key in ["insertText", "updateDocumentStyle"]):
            raise TypeError("Unsupported request type.")
        if "insertText" in request:
            InsertTextRequestModel.model_validate(request)
        if "updateDocumentStyle" in request:
            UpdateDocumentStyleRequestModel.model_validate(request)

    # --- END INPUT VALIDATION ---

    _ensure_user(userId)

    if documentId not in DB["users"][userId]["files"]:
        raise FileNotFoundError(f"Document with ID '{documentId}' not found.")

    document = DB["users"][userId]["files"][documentId]
    replies = []

    for request in requests:
        if "insertText" in request:
            insert_text = request["insertText"]
            text = insert_text["text"]
            location = insert_text["location"]["index"]

            if "content" not in document or document["content"] is None:
                document["content"] = []

            document["content"].insert(location, {"textRun": {"content": text}})

            replies.append({"insertText": {}})

        elif "updateDocumentStyle" in request:
            update_style = request["updateDocumentStyle"]
            document["documentStyle"] = update_style["documentStyle"]
            replies.append({"updateDocumentStyle": {}})
   

    DB["users"][userId]["files"][documentId] = document
    return {"documentId": documentId, "replies": replies}, 200
