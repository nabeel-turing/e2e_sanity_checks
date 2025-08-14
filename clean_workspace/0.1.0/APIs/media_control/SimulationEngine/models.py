from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Dict, Any
from enum import Enum
from .custom_errors import (
    NoMediaItemError, InvalidPlaybackStateError, NoPlaylistError
)

# Enums directly mapping to the OpenAPI schemas
class PlaybackTargetState(str, Enum):
    """The target playback state (e.g. pause, resume, stop)."""
    STOP = "STOP"
    PAUSE = "PAUSE"
    RESUME = "RESUME"

class PlaybackPositionChangeType(str, Enum):
    """Type of media playback position change."""
    SEEK_TO_POSITION = "SEEK_TO_POSITION"
    SEEK_RELATIVE = "SEEK_RELATIVE"
    SKIP_TO_NEXT = "SKIP_TO_NEXT"
    SKIP_TO_PREVIOUS = "SKIP_TO_PREVIOUS"
    REPLAY = "REPLAY"

class MediaAttributeType(str, Enum):
    """Type of media attribute that can be set."""
    RATING = "RATING"

class MediaRating(str, Enum):
    """Rating for the media (positive or negative)."""
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"

class MediaType(str, Enum):
    """Type of media item."""
    TRACK = "TRACK"
    ALBUM = "ALBUM"
    PLAYLIST = "PLAYLIST"
    MUSIC_STATION = "MUSIC_STATION"
    VIDEO = "VIDEO"
    YOUTUBE_CHANNEL = "YOUTUBE_CHANNEL"
    EPISODE = "EPISODE"
    MOVIE = "MOVIE"
    TV_SHOW_EPISODE = "TV_SHOW_EPISODE"
    AUDIO_BOOK = "AUDIO_BOOK"
    RADIO_STATION = "RADIO_STATION"
    TV_CHANNEL = "TV_CHANNEL"
    NEWS = "NEWS"
    PODCAST_SERIES = "PODCAST_SERIES"
    PODCAST_EPISODE = "PODCAST_EPISODE"
    OTHER = "OTHER"

class ActionSummary(BaseModel):
    """Summary of the media control action."""
    result: str = Field(description="Result of the action.")
    title: str = Field(description="Title of the media item.")
    app_name: str = Field(description="App playing the media")
    media_type: MediaType = Field(description="Type of the media item.")

# --- Entities representing the core simulation state ---

class MediaItem(BaseModel):
    """Represents a single media item."""
    id: str = Field(..., description="Unique identifier for the media item.")
    title: str = Field(..., description="Title of the media item.")
    artist: Optional[str] = None
    album: Optional[str] = None
    duration_seconds: Optional[int] = Field(None, ge=0, description="Total duration of the media item in seconds.")
    current_position_seconds: int = Field(0, ge=0, description="Current playback position in seconds.")
    media_type: MediaType = Field(..., description="Type of the media item.")
    rating: Optional[MediaRating] = Field(None, description="User's rating for the media item.")
    app_name: str = Field(..., description="Name of the application associated with this media item.")

class PlaybackState(str, Enum):
    """Current playback state of a media item."""
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"

class MediaPlayer(BaseModel):
    """Represents a media player, which can play media items."""
    app_name: str = Field(..., description="Name of the media application (e.g., 'Spotify', 'YouTube').")
    current_media: Optional[MediaItem] = Field(None, description="The media item currently being played or paused by this player.")
    playback_state: PlaybackState = Field(PlaybackState.STOPPED, description="The current playback state of the media player.")
    playlist: List[MediaItem] = Field([], description="List of media items in the current playlist.")
    current_playlist_index: int = Field(0, ge=0, description="Index of the currently playing media in the playlist.")

    def _sync_current_media_to_playlist(self):
        """Sync current_media changes to the corresponding playlist item."""
        if (self.current_media and self.playlist and 
            0 <= self.current_playlist_index < len(self.playlist)):
            # Only sync if the current media matches the playlist item at current index
            playlist_item = self.playlist[self.current_playlist_index]
            if (playlist_item.id == self.current_media.id and 
                playlist_item.title == self.current_media.title):
                # Update the playlist item with current_media data
                self.playlist[self.current_playlist_index] = self.current_media

    def play_media(self, media_item: MediaItem):
        self.current_media = media_item
        self.playback_state = PlaybackState.PLAYING
        
        # Only reset position if this is a new media item (not from playlist)
        # Check if this media item is already in the playlist
        is_from_playlist = False
        if self.playlist and 0 <= self.current_playlist_index < len(self.playlist):
            playlist_item = self.playlist[self.current_playlist_index]
            if (playlist_item.id == media_item.id and 
                playlist_item.title == media_item.title):
                is_from_playlist = True
        
        if not is_from_playlist:
            # Reset position if new media starts
            self.current_media.current_position_seconds = 0
        
        # Sync to playlist if this media is from the playlist
        self._sync_current_media_to_playlist()

    def pause_media(self):
        if self.playback_state != PlaybackState.PLAYING:
            raise InvalidPlaybackStateError(f"Cannot pause media in {self.playback_state} state")
        
        self.playback_state = PlaybackState.PAUSED
        # Sync changes to playlist
        self._sync_current_media_to_playlist()
        return ActionSummary(result="Success", title=self.current_media.title, app_name=self.app_name, media_type=self.current_media.media_type)

    def resume_media(self):
        if not self.current_media:
            raise NoMediaItemError(f"No media item loaded in app: {self.app_name}")
        if self.playback_state != PlaybackState.PAUSED:
            raise InvalidPlaybackStateError(f"Cannot resume media in app: {self.app_name}. Media must be paused.")
        
        self.playback_state = PlaybackState.PLAYING
        # Sync changes to playlist
        self._sync_current_media_to_playlist()
        return ActionSummary(result="Success", title=self.current_media.title, app_name=self.app_name, media_type=self.current_media.media_type)

    def stop_media(self):
        if self.playback_state == PlaybackState.STOPPED:
            raise InvalidPlaybackStateError("Media is already stopped")
        
        self.playback_state = PlaybackState.STOPPED
        # Sync changes to playlist before stopping
        self._sync_current_media_to_playlist()
        # Optional: reset current_media or position when stopped
        # self.current_media = None 
        # self.current_media.current_position_seconds = 0
        return ActionSummary(result="Success", title=self.current_media.title, app_name=self.app_name, media_type=self.current_media.media_type)

    def next_media(self):
        if not self.playlist:
            raise NoPlaylistError(f"No playlist available in app: {self.app_name}")
        if not self.current_media:
            raise NoMediaItemError(f"No media item loaded in app: {self.app_name}")
        if self.current_playlist_index >= len(self.playlist) - 1:
            raise InvalidPlaybackStateError("Already at the last item in playlist")
        
        # Sync current changes to playlist before moving to next
        self._sync_current_media_to_playlist()
        
        self.current_playlist_index += 1
        self.play_media(self.playlist[self.current_playlist_index])
        return ActionSummary(result="Success", title=self.current_media.title, app_name=self.app_name, media_type=self.current_media.media_type)

    def previous_media(self):
        if not self.playlist:
            raise NoPlaylistError(f"No playlist available in app: {self.app_name}")
        if not self.current_media:
            raise NoMediaItemError(f"No media item loaded in app: {self.app_name}")
        if self.current_playlist_index <= 0:
            raise InvalidPlaybackStateError("Already at the first item in playlist")
        
        # Sync current changes to playlist before moving to previous
        self._sync_current_media_to_playlist()
        
        self.current_playlist_index -= 1
        self.play_media(self.playlist[self.current_playlist_index])
        return ActionSummary(result="Success", title=self.current_media.title, app_name=self.app_name, media_type=self.current_media.media_type)

    def seek_relative(self, offset: int):
        if not self.current_media:
            raise NoMediaItemError(f"No media item loaded in app: {self.app_name}")
        if self.current_media.duration_seconds is None:
            raise InvalidPlaybackStateError("Cannot seek media without duration information")
        
        new_position = self.current_media.current_position_seconds + offset
        self.current_media.current_position_seconds = max(0, min(new_position, self.current_media.duration_seconds))
        self.playback_state = PlaybackState.PLAYING # Resume playing after seek
        
        # Sync changes to playlist
        self._sync_current_media_to_playlist()
        
        return ActionSummary(result="Success", title=self.current_media.title, app_name=self.app_name, media_type=self.current_media.media_type)

    def seek_absolute(self, position: int):
        if not self.current_media:
            raise NoMediaItemError(f"No media item loaded in app: {self.app_name}")
        if self.current_media.duration_seconds is None:
            raise InvalidPlaybackStateError("Cannot seek media without duration information")
        
        self.current_media.current_position_seconds = max(0, min(position, self.current_media.duration_seconds))
        self.playback_state = PlaybackState.PLAYING # Resume playing after seek
        
        # Sync changes to playlist
        self._sync_current_media_to_playlist()
        
        return ActionSummary(result="Success", title=self.current_media.title, app_name=self.app_name, media_type=self.current_media.media_type)

    def replay_media(self):
        if not self.current_media:
            raise NoMediaItemError(f"No media item loaded in app: {self.app_name}")
        
        self.current_media.current_position_seconds = 0
        self.playback_state = PlaybackState.PLAYING
        
        # Sync changes to playlist
        self._sync_current_media_to_playlist()
        
        return ActionSummary(result="Success", title=self.current_media.title, app_name=self.app_name, media_type=self.current_media.media_type)

    def like_media(self):
        if not self.current_media:
            raise NoMediaItemError(f"No media item loaded in app: {self.app_name}")
        
        self.current_media.rating = MediaRating.POSITIVE
        
        # Sync changes to playlist
        self._sync_current_media_to_playlist()
        
        return ActionSummary(result="Success", title=self.current_media.title, app_name=self.app_name, media_type=self.current_media.media_type)

    def dislike_media(self):
        if not self.current_media:
            raise NoMediaItemError(f"No media item loaded in app: {self.app_name}")
        
        self.current_media.rating = MediaRating.NEGATIVE
        
        # Sync changes to playlist
        self._sync_current_media_to_playlist()
        
        return ActionSummary(result="Success", title=self.current_media.title, app_name=self.app_name, media_type=self.current_media.media_type)


class AndroidDB(BaseModel):
    """
    The main Pydantic class holding all data for the in-memory Android API simulation.
    This will act as our "in-memory JSON database".
    """
    media_players: Dict[str, MediaPlayer] = Field(
        {}, description="A dictionary of media players, keyed by app_name."
    )
    # You could add other global state here, e.g.,
    # active_notifications: List[Notification] = []
    # installed_apps: List[AppInfo] = []
    # device_settings: DeviceSettings = DeviceSettings()

    def get_media_player(self, app_name: str) -> Optional[MediaPlayer]:
        """
        Retrieves a media player by app name.
        
        Args:
            app_name (str): The name of the media application
            
        Returns:
            Optional[MediaPlayer]: The media player or None if not found
        """
        return self.media_players.get(app_name)