from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ValidationError, ConfigDict, StrictBool

class SnippetInputModel(BaseModel):
    """
    Pydantic model for the 'snippet' input argument.
    This model allows any arbitrary key-value pairs, effectively validating
    that the input is a dictionary-like structure for thread metadata.
    """
    model_config = ConfigDict(extra="allow")

class ThumbnailObjectModel(BaseModel):
    url:str
    height:int
    width:int


class ThumbnailInputModel(BaseModel):
    """
    Pydantic model for Thumbnail input for playlist
    """
    default : ThumbnailObjectModel
    medium : ThumbnailObjectModel
    high : ThumbnailObjectModel

class TopLevelCommentInputModel(BaseModel):
    """
    Pydantic model for the 'top_level_comment' input argument.
    It expects an optional 'id' field of type string and allows other
    arbitrary fields.
    """
    id: Optional[str] = None
    model_config = ConfigDict(extra="allow")

class ThumbnailRecordUploadModel(BaseModel):
    """
    Pydantic model for thumbnail record upload validation.
    """
    url: str
    width: int
    height: int

class ThumbnailsUploadModel(BaseModel):
    """
    Pydantic model for thumbnails upload validation.
    """
    default: ThumbnailRecordUploadModel
    medium: ThumbnailRecordUploadModel
    high: ThumbnailRecordUploadModel

class SnippetUploadModel(BaseModel):
    """
    Pydantic model for snippet upload validation.
    """
    title: str
    description: str
    channelId: str
    tags: List[str]
    categoryId: str
    channelTitle: str
    thumbnails: ThumbnailsUploadModel

class StatusUploadModel(BaseModel):
    """
    Pydantic model for status upload validation.
    """
    uploadStatus: str
    privacyStatus: str
    embeddable: StrictBool
    madeForKids: StrictBool

class VideoUploadModel(BaseModel):
    """
    Pydantic model for video upload validation.
    """
    snippet: SnippetUploadModel
    status: StatusUploadModel