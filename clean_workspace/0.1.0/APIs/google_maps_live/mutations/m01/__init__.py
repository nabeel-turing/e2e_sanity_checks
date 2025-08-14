from .directions import get_route_from_here, plan_journey
from .places import display_locations_on_map, get_information_for_places, get_insights_on_locations, search_for_locations

_function_map = {
    'display_locations_on_map': 'google_maps_live.mutations.m01.places.display_locations_on_map',
    'get_information_for_places': 'google_maps_live.mutations.m01.places.get_information_for_places',
    'get_insights_on_locations': 'google_maps_live.mutations.m01.places.get_insights_on_locations',
    'get_route_from_here': 'google_maps_live.mutations.m01.directions.get_route_from_here',
    'plan_journey': 'google_maps_live.mutations.m01.directions.plan_journey',
    'search_for_locations': 'google_maps_live.mutations.m01.places.search_for_locations',
}
