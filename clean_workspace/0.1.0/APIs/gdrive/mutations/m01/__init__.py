from .About import retrieve_drive_user_profile
from .Apps import get_user_installed_applications, retrieve_application_information
from .Changes import fetch_drive_modifications, monitor_drive_modifications, request_initial_change_cursor
from .Channels import terminate_notification_channel
from .Comments import add_comment_to_file, edit_file_comment, enumerate_file_comments, fetch_file_comment_by_id, remove_comment_from_file
from .Drives import conceal_shared_drive_from_view, enumerate_user_shared_drives, modify_shared_drive_properties, provision_new_shared_drive, remove_shared_drive_permanently, retrieve_shared_drive_info, reveal_shared_drive_in_view
from .Files import add_new_drive_item, add_new_file_version, convert_and_download_google_file, convert_and_retrieve_file_data, create_new_file_identifiers, download_file_data, duplicate_drive_item, enumerate_file_versions, erase_drive_item_forever, fetch_item_details, modify_drive_item, overwrite_file_data, purge_trash_bin, query_user_drive_items, watch_file_for_updates
from .Permissions import enumerate_file_permissions, fetch_permission_details, grant_file_access, modify_file_access_permission, revoke_file_access
from .Replies import add_reply_to_comment, edit_comment_reply, enumerate_comment_replies, fetch_comment_reply_by_id, remove_reply_from_comment

_function_map = {
    'add_comment_to_file': 'gdrive.mutations.m01.Comments.add_comment_to_file',
    'add_new_drive_item': 'gdrive.mutations.m01.Files.add_new_drive_item',
    'add_new_file_version': 'gdrive.mutations.m01.Files.add_new_file_version',
    'add_reply_to_comment': 'gdrive.mutations.m01.Replies.add_reply_to_comment',
    'conceal_shared_drive_from_view': 'gdrive.mutations.m01.Drives.conceal_shared_drive_from_view',
    'convert_and_download_google_file': 'gdrive.mutations.m01.Files.convert_and_download_google_file',
    'convert_and_retrieve_file_data': 'gdrive.mutations.m01.Files.convert_and_retrieve_file_data',
    'create_new_file_identifiers': 'gdrive.mutations.m01.Files.create_new_file_identifiers',
    'download_file_data': 'gdrive.mutations.m01.Files.download_file_data',
    'duplicate_drive_item': 'gdrive.mutations.m01.Files.duplicate_drive_item',
    'edit_comment_reply': 'gdrive.mutations.m01.Replies.edit_comment_reply',
    'edit_file_comment': 'gdrive.mutations.m01.Comments.edit_file_comment',
    'enumerate_comment_replies': 'gdrive.mutations.m01.Replies.enumerate_comment_replies',
    'enumerate_file_comments': 'gdrive.mutations.m01.Comments.enumerate_file_comments',
    'enumerate_file_permissions': 'gdrive.mutations.m01.Permissions.enumerate_file_permissions',
    'enumerate_file_versions': 'gdrive.mutations.m01.Files.enumerate_file_versions',
    'enumerate_user_shared_drives': 'gdrive.mutations.m01.Drives.enumerate_user_shared_drives',
    'erase_drive_item_forever': 'gdrive.mutations.m01.Files.erase_drive_item_forever',
    'fetch_comment_reply_by_id': 'gdrive.mutations.m01.Replies.fetch_comment_reply_by_id',
    'fetch_drive_modifications': 'gdrive.mutations.m01.Changes.fetch_drive_modifications',
    'fetch_file_comment_by_id': 'gdrive.mutations.m01.Comments.fetch_file_comment_by_id',
    'fetch_item_details': 'gdrive.mutations.m01.Files.fetch_item_details',
    'fetch_permission_details': 'gdrive.mutations.m01.Permissions.fetch_permission_details',
    'get_user_installed_applications': 'gdrive.mutations.m01.Apps.get_user_installed_applications',
    'grant_file_access': 'gdrive.mutations.m01.Permissions.grant_file_access',
    'modify_drive_item': 'gdrive.mutations.m01.Files.modify_drive_item',
    'modify_file_access_permission': 'gdrive.mutations.m01.Permissions.modify_file_access_permission',
    'modify_shared_drive_properties': 'gdrive.mutations.m01.Drives.modify_shared_drive_properties',
    'monitor_drive_modifications': 'gdrive.mutations.m01.Changes.monitor_drive_modifications',
    'overwrite_file_data': 'gdrive.mutations.m01.Files.overwrite_file_data',
    'provision_new_shared_drive': 'gdrive.mutations.m01.Drives.provision_new_shared_drive',
    'purge_trash_bin': 'gdrive.mutations.m01.Files.purge_trash_bin',
    'query_user_drive_items': 'gdrive.mutations.m01.Files.query_user_drive_items',
    'remove_comment_from_file': 'gdrive.mutations.m01.Comments.remove_comment_from_file',
    'remove_reply_from_comment': 'gdrive.mutations.m01.Replies.remove_reply_from_comment',
    'remove_shared_drive_permanently': 'gdrive.mutations.m01.Drives.remove_shared_drive_permanently',
    'request_initial_change_cursor': 'gdrive.mutations.m01.Changes.request_initial_change_cursor',
    'retrieve_application_information': 'gdrive.mutations.m01.Apps.retrieve_application_information',
    'retrieve_drive_user_profile': 'gdrive.mutations.m01.About.retrieve_drive_user_profile',
    'retrieve_shared_drive_info': 'gdrive.mutations.m01.Drives.retrieve_shared_drive_info',
    'reveal_shared_drive_in_view': 'gdrive.mutations.m01.Drives.reveal_shared_drive_in_view',
    'revoke_file_access': 'gdrive.mutations.m01.Permissions.revoke_file_access',
    'terminate_notification_channel': 'gdrive.mutations.m01.Channels.terminate_notification_channel',
    'watch_file_for_updates': 'gdrive.mutations.m01.Files.watch_file_for_updates',
}
