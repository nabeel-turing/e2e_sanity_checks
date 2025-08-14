from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, validator

class SpaceContentModel(BaseModel):
    """
    Pydantic model for validating the structure of space_content.
    """
    meetingCode: str
    meetingUri: str
    accessType: str

class SpaceUpdateMaskModel(BaseModel):
    """
    Pydantic model for validating the 'update_mask' dictionary.
    It includes known fields of a space object, all optional for patching.
    It also allows for additional, unspecified fields to be present in the mask.
    """
    id: Optional[str] = None
    meetingCode: Optional[str] = None
    meetingUri: Optional[str] = None
    accessType: Optional[str] = None  # E.g., "TRUSTED", "RESTRICTED", "OPEN"
    entryPointAccess: Optional[str] = None  # E.g., "ALL", "CREATOR_APP_ONLY"

    # Pydantic V2 configuration:
    # Allow any other fields to be part of the update_mask,
    # reflecting "Additional fields that were updated" and the original Dict[str, Any] type hint.
    model_config = {
        "extra": "allow"
    }

# Common parameter validation models that can be reused across the API
class ListParamsBase(BaseModel):
    """
    Base model for common list operation parameters.
    """
    pageSize: int = Field(100, ge=1, description="The maximum number of items to return per page")
    pageToken: Optional[str] = Field(None, description="The token for continued list pagination")

class ParentResourceParams(BaseModel):
    """
    Model for validating parent resource parameters.
    """
    parent: str = Field(..., min_length=1, description="The parent resource name")
    
    @validator('parent')
    def validate_parent(cls, v):
        if isinstance(v, str):
            v = v.strip()
        if not v:
            raise ValueError("parent cannot be empty or whitespace only")
        return v

class ResourceNameParams(BaseModel):
    """
    Model for validating resource name parameters.
    """
    name: str = Field(..., min_length=1, description="The resource name")

class ParticipantSessionsListParams(ParentResourceParams, ListParamsBase):
    """
    Pydantic model for validating ParticipantSessions list function parameters.
    """
    filter: Optional[str] = Field(None, description="An optional filter string to apply to the sessions")

class ParticipantSessionsGetParams(ResourceNameParams):
    """
    Pydantic model for validating ParticipantSessions get function parameters.
    """
    pass

class ParticipantsListParams(ParentResourceParams, ListParamsBase):
    """
    Pydantic model for validating Participants list function parameters.
    """
    pass

class ParticipantsGetParams(ResourceNameParams):
    """
    Pydantic model for validating Participants get function parameters.
    """
    pass

class TranscriptsListParams(ParentResourceParams, ListParamsBase):
    """
    Pydantic model for validating Transcripts list function parameters.
    """
    pass

class TranscriptEntriesListParams(ParentResourceParams, ListParamsBase):
    """
    Pydantic model for validating TranscriptEntries list function parameters.
    """
    pass

class TranscriptEntriesGetParams(ResourceNameParams):
    """
    Pydantic model for validating TranscriptEntries get function parameters.
    """
    pass
