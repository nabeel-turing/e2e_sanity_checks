"""
Channels resource for Google Drive API simulation.

This module provides methods for managing channels in the Google Drive API simulation.
"""
from typing import Dict, Any, Optional
from pydantic import ValidationError as PydanticValidationError
from .SimulationEngine.db import DB
from .SimulationEngine.utils import _ensure_user, _ensure_channels
from .SimulationEngine.models import ChannelResourceModel
from .SimulationEngine.custom_errors import ValidationError, ChannelNotFoundError

def stop(resource: Optional[Dict[str, Any]] = None) -> None:
    """Stops watching resources through this channel.
    
    Args:
        resource (Optional[Dict[str, Any]]): Dictionary of channel properties. 
            If None or empty dictionary, no action is taken. Required key:
            - 'id' (str): The ID of the channel to stop.
            - 'resourceId' (str): The ID of the resource being watched.
            - 'resourceUri' (str): The URI of the resource being watched.
            - 'token' (str): The token used to authenticate the channel.
            - 'expiration' (str): The time at which the channel will expire (RFC3339 format).
            - 'type' (str): The type of the channel.
            - 'address' (str): The address where notifications are delivered.
            - 'payload' (bool): Whether to include the payload in notifications.
            - 'params' (Dict[str, Any]): Additional parameters for the channel.

    Raises:
        ValidationError: If the resource parameter contains invalid data types or formats.
        ChannelNotFoundError: If the specified channel ID does not exist.
    """
    userId = 'me'
    
    # Ensure user and channels structure exists
    _ensure_user(userId)
    _ensure_channels(userId)
    
    # Handle None resource parameter
    if resource is None:
        resource = {}
    
    # Validate resource parameter using Pydantic model
    try:
        validated_resource = ChannelResourceModel(**resource)
    except PydanticValidationError as e:
        error_msg = e.errors()[0]['msg'] if e.errors() else "Invalid channel resource data"
        raise ValidationError(f"Channel validation failed: {error_msg}")
    
    # Get the channel ID from the validated resource
    channel_id = validated_resource.id
    
    # If no channel ID provided, we cannot stop any specific channel
    if not channel_id:
        return
    
    # Check if the channel exists before attempting to stop it
    user_channels = DB['users'][userId]['channels']
    if channel_id not in user_channels:
        raise ChannelNotFoundError(f"Channel '{channel_id}' not found. Cannot stop a non-existent channel.")
    
    # Stop the channel by removing it from the user's active channels
    user_channels.pop(channel_id, None)