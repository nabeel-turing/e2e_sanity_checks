from typing import Dict, Any, Union
from pydantic import BaseModel, ConfigDict

class LocationModel(BaseModel):
    """Model for the 'location' part of an insertText request."""
    model_config = ConfigDict(extra='forbid')
    index: int

class InsertTextPayloadModel(BaseModel):
    """Model for the payload of an 'insertText' request."""
    model_config = ConfigDict(extra='forbid')
    text: str
    location: LocationModel

class InsertTextRequestModel(BaseModel):
    """Model for a complete 'insertText' request object."""
    model_config = ConfigDict(extra='forbid')
    insertText: InsertTextPayloadModel

class UpdateDocumentStylePayloadModel(BaseModel):
    """Model for the payload of an 'updateDocumentStyle' request."""
    model_config = ConfigDict(extra='forbid')
    documentStyle: Dict[str, Any]  # The internal structure of documentStyle is not specified.

class UpdateDocumentStyleRequestModel(BaseModel):
    """Model for a complete 'updateDocumentStyle' request object."""
    model_config = ConfigDict(extra='forbid')
    updateDocumentStyle: UpdateDocumentStylePayloadModel

# Union model for items in the 'requests' list.
# An item must be one of the explicitly defined request types.
RequestItemModel = Union[InsertTextRequestModel, UpdateDocumentStyleRequestModel]