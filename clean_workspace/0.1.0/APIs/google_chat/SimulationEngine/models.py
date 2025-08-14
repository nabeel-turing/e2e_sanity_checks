from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, model_validator, ConfigDict, root_validator
from enum import Enum

from google_chat.SimulationEngine.custom_errors import MissingDisplayNameError


class ThreadDetailInput(BaseModel):
    name: Optional[str] = None
    # threadKey is not directly used by the input processing of create,
    # but could be part of the thread object if provided.

class MessageBodyInput(BaseModel):
    text: Optional[str] = None
    attachment: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    thread: Optional[ThreadDetailInput] = None
    # clientAssignedMessageId is handled by the top-level messageId parameter,
    # not typically part of the message_body input structure for this function.
    # cards, cardsV2, etc. are not directly processed by the core logic shown,
    # so they are omitted here for simplicity unless they were used.
    # If they are passed through, they can be added here or handled by extra='allow'.
    
    class Config:
        extra = 'allow' # Allow other fields not explicitly defined, as original code might pass them through



class SpaceTypeEnum(str, Enum):
    SPACE = "SPACE"
    GROUP_CHAT = "GROUP_CHAT"
    DIRECT_MESSAGE = "DIRECT_MESSAGE"

class PredefinedPermissionSettingsEnum(str, Enum):
    UNSPECIFIED = "PREDEFINED_PERMISSION_SETTINGS_UNSPECIFIED"
    COLLABORATION = "COLLABORATION_SPACE"
    ANNOUNCEMENT = "ANNOUNCEMENT_SPACE"

class SpaceDetailsModel(BaseModel):
    model_config = ConfigDict(extra='allow', validate_assignment=True)
    description: Optional[str] = None
    guidelines: Optional[str] = None

class AccessSettingsModel(BaseModel):
    model_config = ConfigDict(extra='allow', validate_assignment=True)
    audience: Optional[str] = None

class SpaceInputModel(BaseModel):
    model_config = ConfigDict(extra='allow', validate_assignment=True)

    spaceType: SpaceTypeEnum = Field(..., description="Type of the space.")
    displayName: Optional[str] = Field(None, description="Display name for the space, required if spaceType is 'SPACE'.")
    externalUserAllowed: Optional[bool] = Field(None, description="Whether external users are allowed.")
    importMode: Optional[bool] = Field(None, description="Whether the space is in import mode.")
    singleUserBotDm: Optional[bool] = Field(None, description="Whether this is a DM with a single bot.")
    spaceDetails: Optional[SpaceDetailsModel] = Field(None, description="Details about the space.")
    predefinedPermissionSettings: Optional[PredefinedPermissionSettingsEnum] = Field(None, description="Predefined permission settings.")
    accessSettings: Optional[AccessSettingsModel] = Field(None, description="Access settings for the space.")

    @model_validator(mode='after')
    def check_displayName_for_space_type(cls, values):
        # In Pydantic V2, 'values' is the model instance itself.
        # Access fields via attribute access on 'values'.
        space_type = values.spaceType
        display_name = values.displayName

        if space_type == SpaceTypeEnum.SPACE:
            if not display_name or not display_name.strip():
                raise MissingDisplayNameError(
                    "displayName is required and cannot be empty when spaceType is 'SPACE'."
                )
        return values        
    

class MemberTypeEnum(str, Enum):
    TYPE_UNSPECIFIED = 'TYPE_UNSPECIFIED'
    HUMAN = 'HUMAN'
    BOT = 'BOT'

class MemberRoleEnum(str, Enum):
    MEMBERSHIP_ROLE_UNSPECIFIED = 'MEMBERSHIP_ROLE_UNSPECIFIED'
    ROLE_MEMBER = 'ROLE_MEMBER'
    ROLE_MANAGER = 'ROLE_MANAGER'

class MemberStateEnum(str, Enum):
    MEMBERSHIP_STATE_UNSPECIFIED = 'MEMBERSHIP_STATE_UNSPECIFIED'
    JOINED = 'JOINED'
    INVITED = 'INVITED'
    NOT_A_MEMBER = 'NOT_A_MEMBER'

class MemberModel(BaseModel):
    name: str = Field(..., pattern=r"^(users/(app|[^/]+))$")
    displayName: Optional[str] = None
    domainId: Optional[str] = None
    type: MemberTypeEnum
    isAnonymous: Optional[bool] = None

class GroupMemberModel(BaseModel):
    name: str = Field(..., pattern=r"^groups/[^/]+$")

class MembershipInputModel(BaseModel):
    role: MemberRoleEnum = MemberRoleEnum.ROLE_MEMBER  # Default from original logic
    state: MemberStateEnum = MemberStateEnum.INVITED    # Default from original logic
    deleteTime: Optional[str] = None
    member: MemberModel
    groupMember: Optional[GroupMemberModel] = None

# New models for patch operations
class MembershipPatchModel(BaseModel):
    """Model for membership patch operations. Only certain fields can be updated."""
    role: Optional[MemberRoleEnum] = None
    
    @root_validator(pre=True, skip_on_failure=True)
    def check_at_least_one_field(cls, values):
        """Ensure at least one field is provided for a patch operation."""
        if not values:
            raise ValueError("At least one field must be provided for a patch operation")
        return values

    @root_validator(skip_on_failure=True)
    def validate_has_updatable_fields(cls, values):
        """Ensure that at least one updatable field is present."""
        # For now, only 'role' is supported to be updated
        if not values.get('role'):
            raise ValueError("The patch operation must include at least one updatable field (role)")
        return values

class MembershipUpdateMaskModel(BaseModel):
    """Model to validate the updateMask field in patch operations."""
    updateMask: str
    
    @root_validator(skip_on_failure=True)
    def validate_update_mask(cls, values):
        """Ensure the updateMask contains valid fields."""
        update_mask = values.get('updateMask', '')
        if not update_mask:
            raise ValueError("updateMask is required")
            
        # Split the updateMask by commas and check if each field is valid
        valid_fields = {'role'}
        fields = [field.strip() for field in update_mask.split(',')]
        
        # Check if any valid field is in the updateMask
        if not any(field in valid_fields for field in fields):
            raise ValueError(f"updateMask must contain at least one valid field: {', '.join(valid_fields)}")
            
        return values    