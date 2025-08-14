from .Media import fetch_media_content, upload_file_to_chat_space
from .Spaces.Members import create_space_membership, delete_space_membership, fetch_membership_details, get_all_space_memberships, modify_existing_membership
from .Spaces.Messages.Attachments import fetch_attachment_metadata
from .Spaces.Messages.Reactions import get_all_reactions_for_message, react_to_message, remove_reaction_from_message
from .Spaces.Messages.__init__ import apply_partial_message_update, edit_existing_message, fetch_message_history, post_new_message, remove_chat_message, retrieve_single_message
from .Spaces.SpaceEvents import get_history_of_space_events, retrieve_specific_space_event
from .Spaces.__init__ import create_space_with_members, enumerate_member_spaces, find_organization_spaces_as_admin, modify_space_attributes, provision_new_space, remove_space_and_contents, retrieve_space_information
from .Users.Spaces.SpaceNotificationSetting import get_user_notification_preferences, set_user_notification_preferences
from .Users.Spaces.Threads import check_user_thread_read_status
from .Users.Spaces.__init__ import fetch_user_space_read_status, set_user_space_read_marker

_function_map = {
    'apply_partial_message_update': 'google_chat.mutations.m01.Spaces.Messages.__init__.apply_partial_message_update',
    'check_user_thread_read_status': 'google_chat.mutations.m01.Users.Spaces.Threads.check_user_thread_read_status',
    'create_space_membership': 'google_chat.mutations.m01.Spaces.Members.create_space_membership',
    'create_space_with_members': 'google_chat.mutations.m01.Spaces.__init__.create_space_with_members',
    'delete_space_membership': 'google_chat.mutations.m01.Spaces.Members.delete_space_membership',
    'edit_existing_message': 'google_chat.mutations.m01.Spaces.Messages.__init__.edit_existing_message',
    'enumerate_member_spaces': 'google_chat.mutations.m01.Spaces.__init__.enumerate_member_spaces',
    'fetch_attachment_metadata': 'google_chat.mutations.m01.Spaces.Messages.Attachments.fetch_attachment_metadata',
    'fetch_media_content': 'google_chat.mutations.m01.Media.fetch_media_content',
    'fetch_membership_details': 'google_chat.mutations.m01.Spaces.Members.fetch_membership_details',
    'fetch_message_history': 'google_chat.mutations.m01.Spaces.Messages.__init__.fetch_message_history',
    'fetch_user_space_read_status': 'google_chat.mutations.m01.Users.Spaces.__init__.fetch_user_space_read_status',
    'find_organization_spaces_as_admin': 'google_chat.mutations.m01.Spaces.__init__.find_organization_spaces_as_admin',
    'get_all_reactions_for_message': 'google_chat.mutations.m01.Spaces.Messages.Reactions.get_all_reactions_for_message',
    'get_all_space_memberships': 'google_chat.mutations.m01.Spaces.Members.get_all_space_memberships',
    'get_history_of_space_events': 'google_chat.mutations.m01.Spaces.SpaceEvents.get_history_of_space_events',
    'get_user_notification_preferences': 'google_chat.mutations.m01.Users.Spaces.SpaceNotificationSetting.get_user_notification_preferences',
    'modify_existing_membership': 'google_chat.mutations.m01.Spaces.Members.modify_existing_membership',
    'modify_space_attributes': 'google_chat.mutations.m01.Spaces.__init__.modify_space_attributes',
    'post_new_message': 'google_chat.mutations.m01.Spaces.Messages.__init__.post_new_message',
    'provision_new_space': 'google_chat.mutations.m01.Spaces.__init__.provision_new_space',
    'react_to_message': 'google_chat.mutations.m01.Spaces.Messages.Reactions.react_to_message',
    'remove_chat_message': 'google_chat.mutations.m01.Spaces.Messages.__init__.remove_chat_message',
    'remove_reaction_from_message': 'google_chat.mutations.m01.Spaces.Messages.Reactions.remove_reaction_from_message',
    'remove_space_and_contents': 'google_chat.mutations.m01.Spaces.__init__.remove_space_and_contents',
    'retrieve_single_message': 'google_chat.mutations.m01.Spaces.Messages.__init__.retrieve_single_message',
    'retrieve_space_information': 'google_chat.mutations.m01.Spaces.__init__.retrieve_space_information',
    'retrieve_specific_space_event': 'google_chat.mutations.m01.Spaces.SpaceEvents.retrieve_specific_space_event',
    'set_user_notification_preferences': 'google_chat.mutations.m01.Users.Spaces.SpaceNotificationSetting.set_user_notification_preferences',
    'set_user_space_read_marker': 'google_chat.mutations.m01.Users.Spaces.__init__.set_user_space_read_marker',
    'upload_file_to_chat_space': 'google_chat.mutations.m01.Media.upload_file_to_chat_space',
}
