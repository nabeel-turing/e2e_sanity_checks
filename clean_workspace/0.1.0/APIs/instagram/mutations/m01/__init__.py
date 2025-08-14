from .Comment import fetch_replies_for_media_item, leave_reply_on_post
from .Media import publish_new_gallery_item, remove_gallery_post, retrieve_entire_media_feed
from .User import enumerate_all_accounts, fetch_account_information, find_profile_id_by_handle, purge_user_profile, register_new_profile

_function_map = {
    'enumerate_all_accounts': 'instagram.mutations.m01.User.enumerate_all_accounts',
    'fetch_account_information': 'instagram.mutations.m01.User.fetch_account_information',
    'fetch_replies_for_media_item': 'instagram.mutations.m01.Comment.fetch_replies_for_media_item',
    'find_profile_id_by_handle': 'instagram.mutations.m01.User.find_profile_id_by_handle',
    'leave_reply_on_post': 'instagram.mutations.m01.Comment.leave_reply_on_post',
    'publish_new_gallery_item': 'instagram.mutations.m01.Media.publish_new_gallery_item',
    'purge_user_profile': 'instagram.mutations.m01.User.purge_user_profile',
    'register_new_profile': 'instagram.mutations.m01.User.register_new_profile',
    'remove_gallery_post': 'instagram.mutations.m01.Media.remove_gallery_post',
    'retrieve_entire_media_feed': 'instagram.mutations.m01.Media.retrieve_entire_media_feed',
}
