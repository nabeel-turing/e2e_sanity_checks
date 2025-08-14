from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator

class SpaceInputModel(BaseModel):
    """
    Pydantic model for the 'space' object within the update body.
    """
    key: str

class UpdateContentBodyInputModel(BaseModel):
    """
    Pydantic model for the 'body' argument of the update_content function.
    """
    title: Optional[str] = Field(None, description="Content title")
    status: Optional[str] = Field(None, description="Content status")
    # The 'body' field within the input 'body' dictionary
    body: Optional[Dict[str, Any]] = Field(None, description="Content body data")
    space: Optional[SpaceInputModel] = Field(None, description="Space information")
    ancestors: Optional[List[str]] = Field(None, description="List of ancestor content IDs")

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Title cannot be empty or whitespace-only")
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ["current", "trashed", "draft"]
            if v not in valid_statuses:
                raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v

    @field_validator('ancestors')
    @classmethod
    def validate_ancestors(cls, v):
        if v is not None:
            if not isinstance(v, list):
                raise ValueError("Ancestors must be a list")
            for ancestor_id in v:
                if not isinstance(ancestor_id, str) or not ancestor_id.strip():
                    raise ValueError("Each ancestor ID must be a non-empty string")
        return v

    class Config:
        extra = 'allow' # Allow other fields not defined, as original func might use them


from typing import Optional, List
from pydantic import BaseModel, Field, model_validator
from pydantic import BaseModel

from confluence.SimulationEngine.custom_errors import MissingCommentAncestorsError


class VersionModel(BaseModel):
    number: int = 1
    minorEdit: bool = False

class StorageModel(BaseModel):
    value: str
    representation: Optional[str] = None

class ContentBodyPayloadModel(BaseModel): # For the nested "body" key's structure
    storage: StorageModel

class ContentInputModel(BaseModel):
    type: str
    title: str
    spaceKey: str
    status: str = "current"
    version: VersionModel = Field(default_factory=VersionModel)
    # Using alias to map the input key "body" to this field "body_payload"
    # to avoid confusion with the main argument `body` of the function.
    body: Optional[ContentBodyPayloadModel] = Field(default=None, alias="body")
    createdBy: str = "unknown"
    postingDay: Optional[str] = Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    ancestors: Optional[List[str]] = None # List of parent IDs (strings)

    @model_validator(mode='after')
    def check_comment_ancestors(self) -> 'ContentInputModel':
        if self.type == 'comment':
            if not self.ancestors: # Checks for None or empty list
                raise MissingCommentAncestorsError(
                    "For content type 'comment', the 'ancestors' field (a list of parent IDs) is required and cannot be empty."
                )
        return self

    class Config:
        # Pydantic V2: use `model_config` dict
        # Pydantic V1: use `Config` class
        # Assuming Pydantic V2 is preferred for new code.
        # If V1, this would be:
        # populate_by_name = True # To allow alias usage
        # To ensure aliases work correctly for validation and model_dump
        model_config = {
            "populate_by_name": True
        }


class SpaceBodyInputModel(BaseModel):
    """
    Pydantic model for validating the 'body' argument of the create_space function.
    - 'key' is a mandatory string.
    - 'name' is a string; if not provided in the input dictionary, it defaults to an empty string.
    - 'description' is a string; if not provided in the input dictionary, it defaults to an empty string.
    This aligns with the original function's note about default values for 'name' and 'description'.
    """
    key: str
    name: str = ""
    description: str = ""
