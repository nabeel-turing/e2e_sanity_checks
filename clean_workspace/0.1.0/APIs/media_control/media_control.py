"""
Media Control Service Implementation

This module provides the core functionality for managing Android Media Control,
including playback control, seeking, and rating capabilities.
"""

from typing import Dict, Optional, Union, Any
from .SimulationEngine import utils
from .SimulationEngine.models import (
    PlaybackTargetState, ActionSummary, MediaPlayer, PlaybackState, MediaType, MediaRating
)
from .SimulationEngine.custom_errors import (
    ValidationError, NoMediaPlayerError, NoMediaPlayingError, 
    NoMediaItemError, InvalidPlaybackStateError, NoPlaylistError
)

def change_playback_state(
    target_state: str,
    app_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Changes the playback state of the currently playing media.
    
    Args:
        target_state (str): The target playback state (STOP, PAUSE, RESUME)
        app_name (Optional[str]): Optional; the name of the media application
        
    Returns:
        Dict[str, Any]: Dictionary containing action summary on success, error message on failure.
        The dictionary contains:
        - result (str): Result of the action
        - title (str): Title of the media item
        - app_name (str): App playing the media
        - media_type (str): Type of the media item
        
    Raises:
        ValidationError: If target_state or app_name is invalid
        NoMediaPlayerError: If no media player is found for the specified app
        NoMediaItemError: If no media item is currently loaded
        InvalidPlaybackStateError: If the requested state change is not valid for current state
    """
    # Validate input parameters
    if not isinstance(target_state, str):
        raise ValidationError(f"target_state must be a string, got {type(target_state).__name__}")
    if target_state == "":
        raise ValidationError("target_state cannot be an empty string")
    
    # Validate target_state is a valid enum value
    valid_states = [state.value for state in PlaybackTargetState]
    if target_state not in valid_states:
        raise ValidationError(f"target_state must be one of {valid_states}, got '{target_state}'")
    
    if app_name is not None:
        if not isinstance(app_name, str):
            raise ValidationError(f"app_name must be a string, got {type(app_name).__name__}")
        if app_name == "":
            raise ValidationError("app_name cannot be an empty string")
    
    # Convert string to enum
    target_state_enum = PlaybackTargetState(target_state)
    
    # Get the media player
    player_data = utils.get_media_player(app_name)
    if not player_data:
        raise NoMediaPlayerError(f"No media player found for app: {app_name or 'Unknown'}")
    
    # Check if there's media to control (for PAUSE and STOP operations)
    if target_state_enum in [PlaybackTargetState.PAUSE, PlaybackTargetState.STOP]:
        if not player_data.get("current_media"):
            raise NoMediaItemError("No media item is currently loaded")
    
    # Convert dictionary to MediaPlayer model
    player = MediaPlayer(**player_data)
    
    # Use the appropriate MediaPlayer method based on target_state
    if target_state_enum == PlaybackTargetState.PAUSE:
        result = player.pause_media()
    elif target_state_enum == PlaybackTargetState.RESUME:
        result = player.resume_media()
    else:  # STOP
        result = player.stop_media()
    
    # Save the updated player state back to database
    utils.save_media_player(player.model_dump())
    
    # Return as dict
    return result.model_dump() if hasattr(result, 'model_dump') else result


def pause() -> Dict[str, Any]:
    """
    Pause the currently playing media.
    
    Returns:
        Dict[str, Any]: Dictionary containing the result of successfully changing the state of media playback.
        The dictionary contains:
        - result (str): Result of the action
        - title (str): Title of the media item
        - app_name (str): App playing the media
        - media_type (str): Type of the media item
    
    Raises:
        NoMediaPlayerError: If there is no active media player
        NoMediaPlayingError: If no media is currently playing in the active app
        InvalidPlaybackStateError: If media cannot be paused in current state
    """
    player_data = utils.get_active_media_player()
    if not player_data:
        raise NoMediaPlayerError("No active media player found")
    
    # Check if there's media playing (original validation logic)
    if not utils.validate_media_playing(player_data):
        raise NoMediaPlayingError("No media currently playing in the active app")
    
    # Convert dictionary to MediaPlayer model
    player = MediaPlayer(**player_data)
    
    # Use MediaPlayer method
    result = player.pause_media()
    
    # Save the updated player state back to database
    utils.save_media_player(player.model_dump())
    return result.model_dump() if hasattr(result, 'model_dump') else result


def stop() -> Dict[str, Any]:
    """
    Stop the currently playing media.
    
    Returns:
        Dict[str, Any]: Dictionary containing the result of successfully changing the state of media playback.
        The dictionary contains:
        - result (str): Result of the action
        - title (str): Title of the media item
        - app_name (str): App playing the media
        - media_type (str): Type of the media item
        
    Raises:
        NoMediaPlayerError: If there is no active media player
        NoMediaPlayingError: If no media is currently playing in the active app
        InvalidPlaybackStateError: If media is already stopped
    """
    player_data = utils.get_active_media_player()
    if not player_data:
        raise NoMediaPlayerError("No active media player found")
    
    # Check if there's media playing (original validation logic)
    if not utils.validate_media_playing(player_data):
        raise NoMediaPlayingError("No media currently playing in the active app")
    
    # Convert dictionary to MediaPlayer model
    player = MediaPlayer(**player_data)
    
    # Use MediaPlayer method
    result = player.stop_media()
    
    # Save the updated player state back to database
    utils.save_media_player(player.model_dump())
    return result.model_dump() if hasattr(result, 'model_dump') else result


def resume() -> Dict[str, Any]:
    """
    Resume the currently paused media.
    
    Returns:
        Dict[str, Any]: Dictionary containing the result of successfully changing the state of media playback.
        The dictionary contains:
        - result (str): Result of the action
        - title (str): Title of the media item
        - app_name (str): App playing the media
        - media_type (str): Type of the media item
        
    Raises:
        NoMediaPlayerError: If there is no active media player
        InvalidPlaybackStateError: If media cannot be resumed (must be paused)
    """
    player_data = utils.get_active_media_player()
    if not player_data:
        raise NoMediaPlayerError("No active media player found")
    
    # Check if there's media to resume
    if not player_data.get("current_media"):
        raise InvalidPlaybackStateError(f"Cannot resume media in app: {player_data['app_name']}. Media must be paused.")
    
    # Convert dictionary to MediaPlayer model
    player = MediaPlayer(**player_data)
    
    # Use MediaPlayer method
    result = player.resume_media()
    
    # Save the updated player state back to database
    utils.save_media_player(player.model_dump())
    return result.model_dump() if hasattr(result, 'model_dump') else result


def next() -> Dict[str, Any]:
    """
    Skip to the next media item.
    
    Returns:
        Dict[str, Any]: Dictionary containing the result of successfully changing the media playback position.
        The dictionary contains:
        - result (str): Result of the action
        - title (str): Title of the media item
        - app_name (str): App playing the media
        - media_type (str): Type of the media item
        
    Raises:
        NoMediaPlayerError: If there is no active media player
        NoPlaylistError: If no playlist is available in the app
        InvalidPlaybackStateError: If already at the last item in playlist
    """
    player_data = utils.get_active_media_player()
    if not player_data:
        raise NoMediaPlayerError("No active media player found")
    
    # Check if there's media and playlist
    if not player_data.get("current_media"):
        raise NoPlaylistError(f"No playlist available in app: {player_data['app_name']}")
    
    # Convert dictionary to MediaPlayer model
    player = MediaPlayer(**player_data)
    
    # Use MediaPlayer method
    result = player.next_media()
    
    # Save the updated player state back to database
    utils.save_media_player(player.model_dump())
    return result.model_dump() if hasattr(result, 'model_dump') else result


def previous() -> Dict[str, Any]:
    """
    Skip to the previous media item.
    
    Returns:
        Dict[str, Any]: Dictionary containing the result of successfully changing the media playback position.
        The dictionary contains:
        - result (str): Result of the action
        - title (str): Title of the media item
        - app_name (str): App playing the media
        - media_type (str): Type of the media item
        
    Raises:
        NoMediaPlayerError: If there is no active media player
        NoPlaylistError: If no playlist is available in the app
        InvalidPlaybackStateError: If already at the first item in playlist
    """
    player_data = utils.get_active_media_player()
    if not player_data:
        raise NoMediaPlayerError("No active media player found")
    
    # Check if there's media and playlist
    if not player_data.get("current_media"):
        raise NoPlaylistError(f"No playlist available in app: {player_data['app_name']}")
    
    # Convert dictionary to MediaPlayer model
    player = MediaPlayer(**player_data)
    
    # Use MediaPlayer method
    result = player.previous_media()
    
    # Save the updated player state back to database
    utils.save_media_player(player.model_dump())
    return result.model_dump() if hasattr(result, 'model_dump') else result


def replay() -> Dict[str, Any]:
    """
    Replay the current media item from the beginning.
    
    Returns:
        Dict[str, Any]: Dictionary containing the result of successfully changing the media playback position.
        The dictionary contains:
        - result (str): Result of the action
        - title (str): Title of the media item
        - app_name (str): App playing the media
        - media_type (str): Type of the media item
        
    Raises:
        NoMediaPlayerError: If there is no active media player
        NoMediaItemError: If no media item is loaded in the app
    """
    player_data = utils.get_active_media_player()
    if not player_data:
        raise NoMediaPlayerError("No active media player found")
    
    # Convert dictionary to MediaPlayer model
    player = MediaPlayer(**player_data)
    
    # Use MediaPlayer method
    result = player.replay_media()
    
    # Save the updated player state back to database
    utils.save_media_player(player.model_dump())
    return result.model_dump() if hasattr(result, 'model_dump') else result


def seek_relative(offset: int) -> Dict[str, Any]:
    """
    Adjusts media playback by a specified duration relative to the current position, then resumes playing.
    
    Args:
        offset (int): Relative offset in seconds from the current playback position.
                     Positive values fast forward; negative values rewind.
    
    Returns:
        Dict[str, Any]: Dictionary containing the result of successfully changing the media playback position.
        The dictionary contains:
        - result (str): Result of the action
        - title (str): Title of the media item
        - app_name (str): App playing the media
        - media_type (str): Type of the media item
        
    Raises:
        ValidationError: If offset is not an integer or invalid
        NoMediaPlayerError: If there is no active media player
        NoMediaItemError: If no media item is loaded in the app
    """
    if not isinstance(offset, int):
        raise ValidationError(f"offset must be an integer, got {type(offset).__name__}")
    
    player_data = utils.get_active_media_player()
    if not player_data:
        raise NoMediaPlayerError("No active media player found")
    
    # Check if there's media to seek
    if not player_data.get("current_media"):
        raise NoMediaItemError(f"No media item loaded in app: {player_data['app_name']}")
    
    # Validate seek offset before calling MediaPlayer method
    if not utils.validate_seek_offset(offset, player_data):
        raise ValidationError(f"Invalid seek offset: {offset}")
    
    # Convert dictionary to MediaPlayer model
    player = MediaPlayer(**player_data)
    
    # Use MediaPlayer method
    result = player.seek_relative(offset)
    
    # Save the updated player state back to database
    utils.save_media_player(player.model_dump())
    return result.model_dump() if hasattr(result, 'model_dump') else result


def seek_absolute(position: int) -> Dict[str, Any]:
    """
    Jumps to a specific position in the media, then resumes playing.
    
    Args:
        position (int): Absolute position in the media in seconds.
    
    Returns:
        Dict[str, Any]: Dictionary containing the result of successfully changing the media playback position.
        The dictionary contains:
        - result (str): Result of the action
        - title (str): Title of the media item
        - app_name (str): App playing the media
        - media_type (str): Type of the media item
        
    Raises:
        ValidationError: If position is not an integer or invalid
        NoMediaPlayerError: If there is no active media player
        NoMediaItemError: If no media item is loaded in the app
    """
    if not isinstance(position, int):
        raise ValidationError(f"position must be an integer, got {type(position).__name__}")
    
    player_data = utils.get_active_media_player()
    if not player_data:
        raise NoMediaPlayerError("No active media player found")
    
    # Check if there's media to seek
    if not player_data.get("current_media"):
        raise NoMediaItemError(f"No media item loaded in app: {player_data['app_name']}")
    
    # Validate seek position before calling MediaPlayer method
    if not utils.validate_seek_position(position, player_data):
        raise ValidationError(f"Invalid seek position: {position}")
    
    # Convert dictionary to MediaPlayer model
    player = MediaPlayer(**player_data)
    
    # Use MediaPlayer method
    result = player.seek_absolute(position)
    
    # Save the updated player state back to database
    utils.save_media_player(player.model_dump())
    return result.model_dump() if hasattr(result, 'model_dump') else result


def like() -> Dict[str, Any]:
    """
    Like the currently playing media.
    
    Returns:
        Dict[str, Any]: Dictionary containing the result of successfully setting the media attribute.
        The dictionary contains:
        - result (str): Result of the action
        - title (str): Title of the media item
        - app_name (str): App playing the media
        - media_type (str): Type of the media item
        
    Raises:
        NoMediaPlayerError: If there is no active media player
        NoMediaItemError: If no media item is loaded in the app
    """
    player_data = utils.get_active_media_player()
    if not player_data:
        raise NoMediaPlayerError("No active media player found")
    
    # Convert dictionary to MediaPlayer model
    player = MediaPlayer(**player_data)
    
    # Use MediaPlayer method
    result = player.like_media()
    
    # Save the updated player state back to database
    utils.save_media_player(player.model_dump())
    return result.model_dump() if hasattr(result, 'model_dump') else result


def dislike() -> Dict[str, Any]:
    """
    Dislike the currently playing media.
    
    Returns:
        Dict[str, Any]: Dictionary containing the result of successfully setting the media attribute.
        The dictionary contains:
        - result (str): Result of the action
        - title (str): Title of the media item
        - app_name (str): App playing the media
        - media_type (str): Type of the media item
        
    Raises:
        NoMediaPlayerError: If there is no active media player
        NoMediaItemError: If no media item is loaded in the app
    """
    player_data = utils.get_active_media_player()
    if not player_data:
        raise NoMediaPlayerError("No active media player found")
    
    # Convert dictionary to MediaPlayer model
    player = MediaPlayer(**player_data)
    
    # Use MediaPlayer method
    result = player.dislike_media()
    
    # Save the updated player state back to database
    utils.save_media_player(player.model_dump())
    return result.model_dump() if hasattr(result, 'model_dump') else result
