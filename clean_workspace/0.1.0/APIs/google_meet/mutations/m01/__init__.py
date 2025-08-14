from .ConferenceRecords.Participants.ParticipantSessions import catalog_attendee_connections, find_attendee_session_by_id
from .ConferenceRecords.Participants.__init__ import enumerate_all_meeting_attendees, fetch_attendee_information
from .ConferenceRecords.Recordings import enumerate_all_meeting_recordings, retrieve_meeting_recording_by_id
from .ConferenceRecords.Transcripts.Entries import fetch_single_transcript_segment, get_all_transcript_segments
from .ConferenceRecords.Transcripts.__init__ import find_transcript_by_name, get_all_transcripts_for_conference
from .ConferenceRecords.__init__ import fetch_meeting_details_by_id, retrieve_meeting_history_list
from .Spaces import establish_new_virtual_room, fetch_conference_room_info, modify_conference_room, terminate_current_conference

_function_map = {
    'catalog_attendee_connections': 'google_meet.mutations.m01.ConferenceRecords.Participants.ParticipantSessions.catalog_attendee_connections',
    'enumerate_all_meeting_attendees': 'google_meet.mutations.m01.ConferenceRecords.Participants.__init__.enumerate_all_meeting_attendees',
    'enumerate_all_meeting_recordings': 'google_meet.mutations.m01.ConferenceRecords.Recordings.enumerate_all_meeting_recordings',
    'establish_new_virtual_room': 'google_meet.mutations.m01.Spaces.establish_new_virtual_room',
    'fetch_attendee_information': 'google_meet.mutations.m01.ConferenceRecords.Participants.__init__.fetch_attendee_information',
    'fetch_conference_room_info': 'google_meet.mutations.m01.Spaces.fetch_conference_room_info',
    'fetch_meeting_details_by_id': 'google_meet.mutations.m01.ConferenceRecords.__init__.fetch_meeting_details_by_id',
    'fetch_single_transcript_segment': 'google_meet.mutations.m01.ConferenceRecords.Transcripts.Entries.fetch_single_transcript_segment',
    'find_attendee_session_by_id': 'google_meet.mutations.m01.ConferenceRecords.Participants.ParticipantSessions.find_attendee_session_by_id',
    'find_transcript_by_name': 'google_meet.mutations.m01.ConferenceRecords.Transcripts.__init__.find_transcript_by_name',
    'get_all_transcript_segments': 'google_meet.mutations.m01.ConferenceRecords.Transcripts.Entries.get_all_transcript_segments',
    'get_all_transcripts_for_conference': 'google_meet.mutations.m01.ConferenceRecords.Transcripts.__init__.get_all_transcripts_for_conference',
    'modify_conference_room': 'google_meet.mutations.m01.Spaces.modify_conference_room',
    'retrieve_meeting_history_list': 'google_meet.mutations.m01.ConferenceRecords.__init__.retrieve_meeting_history_list',
    'retrieve_meeting_recording_by_id': 'google_meet.mutations.m01.ConferenceRecords.Recordings.retrieve_meeting_recording_by_id',
    'terminate_current_conference': 'google_meet.mutations.m01.Spaces.terminate_current_conference',
}
