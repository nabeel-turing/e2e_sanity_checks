"""
Pydantic models for device_setting API
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
import uuid

from device_setting.SimulationEngine.enums import VolumeSettingType, ActionType


class VolumeSettingMapping(BaseModel):
    """Mapping between VolumeSettingType enum and database keys."""
    ALARM: str = "ALARM_VOLUME"
    CALL: str = "CALL_VOLUME"
    MEDIA: str = "MEDIA_VOLUME"
    NOTIFICATION: str = "NOTIFICATION_VOLUME"
    RING: str = "RING_VOLUME"
    UNSPECIFIED: Optional[str] = None
    
    def get_database_key(self, setting_type: VolumeSettingType) -> Optional[str]:
        """Get the database key for a given volume setting type."""
        return getattr(self, setting_type.value, None)
    
    def get_all_volume_keys(self) -> list[str]:
        """Get all volume database keys."""
        return [self.ALARM, self.CALL, self.MEDIA, self.NOTIFICATION, self.RING, "VOLUME"]


class SettingInfo(BaseModel):
    """Detailed information about a specific device setting."""
    setting_type: str = Field(..., description="The type of the setting.")
    percentage_value: Optional[int] = Field(None, description="If the setting type can be adjusted, return the current percentage value of a device setting between [1, 100].")
    on_or_off: Optional[str] = Field(None, description="If the setting type can be toggled, return the current toggled value.")
    action_card_content_passthrough: Optional[str] = Field(None, description="Action card content for UI display.")
    card_id: Optional[str] = Field(None, description="Card identifier for UI components.")

    @field_validator('percentage_value')
    @classmethod
    def validate_percentage(cls, v):
        if v is not None and (v < 1 or v > 100):
            raise ValueError('percentage_value must be between 1 and 100')
        return v

    @field_validator('on_or_off')
    @classmethod
    def validate_on_or_off(cls, v):
        if v is not None and v not in ['on', 'off']:
            raise ValueError('on_or_off must be either "on" or "off"')
        return v


class ActionSummary(BaseModel):
    """The description of the tool action result."""
    result: str = Field(..., description="Result message of the action.")
    action_card_content_passthrough: Optional[str] = Field(None, description="Action card content for UI display.")
    card_id: Optional[str] = Field(None, description="Card identifier for UI components.")


class Action(BaseModel):
    """An action record."""
    action_type: ActionType
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    metadata: Dict[str, Any] = {}
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# Global instance for volume setting mappings
volume_mapping = VolumeSettingMapping() 