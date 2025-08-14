from .albums import add_albums_to_user_library, delete_albums_from_user_library, fetch_current_user_library_albums, fetch_multiple_album_details, fetch_single_album_details, retrieve_tracks_from_album, verify_albums_in_user_library
from .artists import discover_similar_artists, fetch_artist_discography, fetch_artist_hit_songs_by_region, retrieve_multiple_artists_data, retrieve_single_artist_data
from .browse import browse_latest_album_releases, browse_spotify_featured_playlists, fetch_single_category_details, generate_track_recommendations, list_all_content_categories, list_recommendation_genre_seeds, retrieve_playlists_by_category
from .follow import add_entities_to_followed_list, confirm_current_user_follow_status, list_current_user_followed_artists, remove_entities_from_followed_list, subscribe_to_playlist, unsubscribe_from_playlist, verify_playlist_followers_status
from .playlist import append_items_to_playlist, delete_items_from_playlist, fetch_playlist_artwork, fetch_playlist_by_id, generate_new_user_playlist, list_authenticated_user_playlists, list_specific_user_playlists, reorder_or_replace_playlist_tracks, retrieve_playlist_contents, update_playlist_metadata, upload_playlist_cover_jpeg
from .search import execute_catalog_search_query
from .user_profile import fetch_authenticated_user_details, fetch_public_user_information, retrieve_user_listening_favorites

_function_map = {
    'add_albums_to_user_library': 'spotify.mutations.m01.albums.add_albums_to_user_library',
    'add_entities_to_followed_list': 'spotify.mutations.m01.follow.add_entities_to_followed_list',
    'append_items_to_playlist': 'spotify.mutations.m01.playlist.append_items_to_playlist',
    'browse_latest_album_releases': 'spotify.mutations.m01.browse.browse_latest_album_releases',
    'browse_spotify_featured_playlists': 'spotify.mutations.m01.browse.browse_spotify_featured_playlists',
    'confirm_current_user_follow_status': 'spotify.mutations.m01.follow.confirm_current_user_follow_status',
    'delete_albums_from_user_library': 'spotify.mutations.m01.albums.delete_albums_from_user_library',
    'delete_items_from_playlist': 'spotify.mutations.m01.playlist.delete_items_from_playlist',
    'discover_similar_artists': 'spotify.mutations.m01.artists.discover_similar_artists',
    'execute_catalog_search_query': 'spotify.mutations.m01.search.execute_catalog_search_query',
    'fetch_artist_discography': 'spotify.mutations.m01.artists.fetch_artist_discography',
    'fetch_artist_hit_songs_by_region': 'spotify.mutations.m01.artists.fetch_artist_hit_songs_by_region',
    'fetch_authenticated_user_details': 'spotify.mutations.m01.user_profile.fetch_authenticated_user_details',
    'fetch_current_user_library_albums': 'spotify.mutations.m01.albums.fetch_current_user_library_albums',
    'fetch_multiple_album_details': 'spotify.mutations.m01.albums.fetch_multiple_album_details',
    'fetch_playlist_artwork': 'spotify.mutations.m01.playlist.fetch_playlist_artwork',
    'fetch_playlist_by_id': 'spotify.mutations.m01.playlist.fetch_playlist_by_id',
    'fetch_public_user_information': 'spotify.mutations.m01.user_profile.fetch_public_user_information',
    'fetch_single_album_details': 'spotify.mutations.m01.albums.fetch_single_album_details',
    'fetch_single_category_details': 'spotify.mutations.m01.browse.fetch_single_category_details',
    'generate_new_user_playlist': 'spotify.mutations.m01.playlist.generate_new_user_playlist',
    'generate_track_recommendations': 'spotify.mutations.m01.browse.generate_track_recommendations',
    'list_all_content_categories': 'spotify.mutations.m01.browse.list_all_content_categories',
    'list_authenticated_user_playlists': 'spotify.mutations.m01.playlist.list_authenticated_user_playlists',
    'list_current_user_followed_artists': 'spotify.mutations.m01.follow.list_current_user_followed_artists',
    'list_recommendation_genre_seeds': 'spotify.mutations.m01.browse.list_recommendation_genre_seeds',
    'list_specific_user_playlists': 'spotify.mutations.m01.playlist.list_specific_user_playlists',
    'remove_entities_from_followed_list': 'spotify.mutations.m01.follow.remove_entities_from_followed_list',
    'reorder_or_replace_playlist_tracks': 'spotify.mutations.m01.playlist.reorder_or_replace_playlist_tracks',
    'retrieve_multiple_artists_data': 'spotify.mutations.m01.artists.retrieve_multiple_artists_data',
    'retrieve_playlist_contents': 'spotify.mutations.m01.playlist.retrieve_playlist_contents',
    'retrieve_playlists_by_category': 'spotify.mutations.m01.browse.retrieve_playlists_by_category',
    'retrieve_single_artist_data': 'spotify.mutations.m01.artists.retrieve_single_artist_data',
    'retrieve_tracks_from_album': 'spotify.mutations.m01.albums.retrieve_tracks_from_album',
    'retrieve_user_listening_favorites': 'spotify.mutations.m01.user_profile.retrieve_user_listening_favorites',
    'subscribe_to_playlist': 'spotify.mutations.m01.follow.subscribe_to_playlist',
    'unsubscribe_from_playlist': 'spotify.mutations.m01.follow.unsubscribe_from_playlist',
    'update_playlist_metadata': 'spotify.mutations.m01.playlist.update_playlist_metadata',
    'upload_playlist_cover_jpeg': 'spotify.mutations.m01.playlist.upload_playlist_cover_jpeg',
    'verify_albums_in_user_library': 'spotify.mutations.m01.albums.verify_albums_in_user_library',
    'verify_playlist_followers_status': 'spotify.mutations.m01.follow.verify_playlist_followers_status',
}
