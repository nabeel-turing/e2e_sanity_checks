from .Places.Photos import fetch_photo_content
from .Places.__init__ import fetch_autocomplete_suggestions, find_proximate_venues, query_locations_by_text_input, retrieve_location_information

_function_map = {
    'fetch_autocomplete_suggestions': 'google_maps.mutations.m01.Places.__init__.fetch_autocomplete_suggestions',
    'fetch_photo_content': 'google_maps.mutations.m01.Places.Photos.fetch_photo_content',
    'find_proximate_venues': 'google_maps.mutations.m01.Places.__init__.find_proximate_venues',
    'query_locations_by_text_input': 'google_maps.mutations.m01.Places.__init__.query_locations_by_text_input',
    'retrieve_location_information': 'google_maps.mutations.m01.Places.__init__.retrieve_location_information',
}
