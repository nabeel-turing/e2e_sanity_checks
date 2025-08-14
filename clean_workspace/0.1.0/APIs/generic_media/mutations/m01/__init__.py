from .play_api import initiate_media_playback
from .search_api import find_media_content

_function_map = {
    'find_media_content': 'generic_media.mutations.m01.search_api.find_media_content',
    'initiate_media_playback': 'generic_media.mutations.m01.play_api.initiate_media_playback',
}
