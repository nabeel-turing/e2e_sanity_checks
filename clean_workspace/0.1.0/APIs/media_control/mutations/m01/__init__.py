from .media_control import adjust_playback_time, advance_to_next_track, continue_playback, flag_as_disliked, jump_to_timestamp, mark_as_liked, restart_current_media, return_to_previous_track, suspend_playback, terminate_playback, update_playback_mode

_function_map = {
    'adjust_playback_time': 'media_control.mutations.m01.media_control.adjust_playback_time',
    'advance_to_next_track': 'media_control.mutations.m01.media_control.advance_to_next_track',
    'continue_playback': 'media_control.mutations.m01.media_control.continue_playback',
    'flag_as_disliked': 'media_control.mutations.m01.media_control.flag_as_disliked',
    'jump_to_timestamp': 'media_control.mutations.m01.media_control.jump_to_timestamp',
    'mark_as_liked': 'media_control.mutations.m01.media_control.mark_as_liked',
    'restart_current_media': 'media_control.mutations.m01.media_control.restart_current_media',
    'return_to_previous_track': 'media_control.mutations.m01.media_control.return_to_previous_track',
    'suspend_playback': 'media_control.mutations.m01.media_control.suspend_playback',
    'terminate_playback': 'media_control.mutations.m01.media_control.terminate_playback',
    'update_playback_mode': 'media_control.mutations.m01.media_control.update_playback_mode',
}
