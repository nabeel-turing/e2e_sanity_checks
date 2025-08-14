from .Activities import retrieve_channel_activity_feed
from .Caption import fetch_caption_track_file, get_video_caption_tracks, modify_video_caption_track, remove_video_caption_track, upload_new_caption_track
from .ChannelBanners import upload_channel_header_image
from .ChannelSection import add_new_channel_layout_section, modify_channel_layout_section, remove_channel_layout_section, retrieve_channel_layout_sections
from .ChannelStatistics import configure_subscriber_count_visibility, get_or_set_channel_comment_total, get_or_set_channel_subscriber_total, get_or_set_channel_video_total, get_or_set_channel_view_total
from .Channels import edit_channel_properties, find_channels_by_criteria, register_new_channel
from .Comment import edit_existing_comment, flag_comment_as_spam, moderate_single_comment, post_new_comment, remove_individual_comment, retrieve_comments_for_thread
from .CommentThread import initiate_new_comment_discussion, modify_comment_discussion, query_comment_discussions, remove_comment_discussion
from .Memberships import add_new_channel_member, get_channel_members_list, modify_channel_membership_details, remove_channel_membership
from .Playlists import change_playlist_video_sequence, fetch_playlist_by_id, generate_new_playlist, insert_video_into_playlist, modify_playlist_details, remove_playlist_by_id, remove_video_from_playlist_items, retrieve_playlists
from .Search import execute_content_search_query
from .Subscriptions import add_new_channel_subscription, cancel_channel_subscription, retrieve_user_or_channel_subscriptions
from .VideoCategory import fetch_available_video_genres
from .Videos import flag_video_for_abuse, modify_video_details, publish_new_video, remove_video_by_id, search_for_videos, set_video_rating

_function_map = {
    'add_new_channel_layout_section': 'youtube.mutations.m01.ChannelSection.add_new_channel_layout_section',
    'add_new_channel_member': 'youtube.mutations.m01.Memberships.add_new_channel_member',
    'add_new_channel_subscription': 'youtube.mutations.m01.Subscriptions.add_new_channel_subscription',
    'cancel_channel_subscription': 'youtube.mutations.m01.Subscriptions.cancel_channel_subscription',
    'change_playlist_video_sequence': 'youtube.mutations.m01.Playlists.change_playlist_video_sequence',
    'configure_subscriber_count_visibility': 'youtube.mutations.m01.ChannelStatistics.configure_subscriber_count_visibility',
    'edit_channel_properties': 'youtube.mutations.m01.Channels.edit_channel_properties',
    'edit_existing_comment': 'youtube.mutations.m01.Comment.edit_existing_comment',
    'execute_content_search_query': 'youtube.mutations.m01.Search.execute_content_search_query',
    'fetch_available_video_genres': 'youtube.mutations.m01.VideoCategory.fetch_available_video_genres',
    'fetch_caption_track_file': 'youtube.mutations.m01.Caption.fetch_caption_track_file',
    'fetch_playlist_by_id': 'youtube.mutations.m01.Playlists.fetch_playlist_by_id',
    'find_channels_by_criteria': 'youtube.mutations.m01.Channels.find_channels_by_criteria',
    'flag_comment_as_spam': 'youtube.mutations.m01.Comment.flag_comment_as_spam',
    'flag_video_for_abuse': 'youtube.mutations.m01.Videos.flag_video_for_abuse',
    'generate_new_playlist': 'youtube.mutations.m01.Playlists.generate_new_playlist',
    'get_channel_members_list': 'youtube.mutations.m01.Memberships.get_channel_members_list',
    'get_or_set_channel_comment_total': 'youtube.mutations.m01.ChannelStatistics.get_or_set_channel_comment_total',
    'get_or_set_channel_subscriber_total': 'youtube.mutations.m01.ChannelStatistics.get_or_set_channel_subscriber_total',
    'get_or_set_channel_video_total': 'youtube.mutations.m01.ChannelStatistics.get_or_set_channel_video_total',
    'get_or_set_channel_view_total': 'youtube.mutations.m01.ChannelStatistics.get_or_set_channel_view_total',
    'get_video_caption_tracks': 'youtube.mutations.m01.Caption.get_video_caption_tracks',
    'initiate_new_comment_discussion': 'youtube.mutations.m01.CommentThread.initiate_new_comment_discussion',
    'insert_video_into_playlist': 'youtube.mutations.m01.Playlists.insert_video_into_playlist',
    'moderate_single_comment': 'youtube.mutations.m01.Comment.moderate_single_comment',
    'modify_channel_layout_section': 'youtube.mutations.m01.ChannelSection.modify_channel_layout_section',
    'modify_channel_membership_details': 'youtube.mutations.m01.Memberships.modify_channel_membership_details',
    'modify_comment_discussion': 'youtube.mutations.m01.CommentThread.modify_comment_discussion',
    'modify_playlist_details': 'youtube.mutations.m01.Playlists.modify_playlist_details',
    'modify_video_caption_track': 'youtube.mutations.m01.Caption.modify_video_caption_track',
    'modify_video_details': 'youtube.mutations.m01.Videos.modify_video_details',
    'post_new_comment': 'youtube.mutations.m01.Comment.post_new_comment',
    'publish_new_video': 'youtube.mutations.m01.Videos.publish_new_video',
    'query_comment_discussions': 'youtube.mutations.m01.CommentThread.query_comment_discussions',
    'register_new_channel': 'youtube.mutations.m01.Channels.register_new_channel',
    'remove_channel_layout_section': 'youtube.mutations.m01.ChannelSection.remove_channel_layout_section',
    'remove_channel_membership': 'youtube.mutations.m01.Memberships.remove_channel_membership',
    'remove_comment_discussion': 'youtube.mutations.m01.CommentThread.remove_comment_discussion',
    'remove_individual_comment': 'youtube.mutations.m01.Comment.remove_individual_comment',
    'remove_playlist_by_id': 'youtube.mutations.m01.Playlists.remove_playlist_by_id',
    'remove_video_by_id': 'youtube.mutations.m01.Videos.remove_video_by_id',
    'remove_video_caption_track': 'youtube.mutations.m01.Caption.remove_video_caption_track',
    'remove_video_from_playlist_items': 'youtube.mutations.m01.Playlists.remove_video_from_playlist_items',
    'retrieve_channel_activity_feed': 'youtube.mutations.m01.Activities.retrieve_channel_activity_feed',
    'retrieve_channel_layout_sections': 'youtube.mutations.m01.ChannelSection.retrieve_channel_layout_sections',
    'retrieve_comments_for_thread': 'youtube.mutations.m01.Comment.retrieve_comments_for_thread',
    'retrieve_playlists': 'youtube.mutations.m01.Playlists.retrieve_playlists',
    'retrieve_user_or_channel_subscriptions': 'youtube.mutations.m01.Subscriptions.retrieve_user_or_channel_subscriptions',
    'search_for_videos': 'youtube.mutations.m01.Videos.search_for_videos',
    'set_video_rating': 'youtube.mutations.m01.Videos.set_video_rating',
    'upload_channel_header_image': 'youtube.mutations.m01.ChannelBanners.upload_channel_header_image',
    'upload_new_caption_track': 'youtube.mutations.m01.Caption.upload_new_caption_track',
}
