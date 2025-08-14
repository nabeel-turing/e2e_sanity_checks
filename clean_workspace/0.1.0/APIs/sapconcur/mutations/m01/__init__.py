from .bookings import adjust_booking_baggage, alter_booking_flight_details, process_reservation_update, retrieve_booking_by_record_locator, revoke_reservation, update_booking_travelers
from .flights import query_connecting_flights, query_nonstop_flights
from .locations import fetch_airport_city_map, find_corporate_sites, retrieve_location_data
from .trips import process_itinerary_submission, query_trip_overviews
from .users import dispatch_user_certificate, escalate_to_support_specialist, find_user_by_login

_function_map = {
    'adjust_booking_baggage': 'sapconcur.mutations.m01.bookings.adjust_booking_baggage',
    'alter_booking_flight_details': 'sapconcur.mutations.m01.bookings.alter_booking_flight_details',
    'dispatch_user_certificate': 'sapconcur.mutations.m01.users.dispatch_user_certificate',
    'escalate_to_support_specialist': 'sapconcur.mutations.m01.users.escalate_to_support_specialist',
    'fetch_airport_city_map': 'sapconcur.mutations.m01.locations.fetch_airport_city_map',
    'find_corporate_sites': 'sapconcur.mutations.m01.locations.find_corporate_sites',
    'find_user_by_login': 'sapconcur.mutations.m01.users.find_user_by_login',
    'process_itinerary_submission': 'sapconcur.mutations.m01.trips.process_itinerary_submission',
    'process_reservation_update': 'sapconcur.mutations.m01.bookings.process_reservation_update',
    'query_connecting_flights': 'sapconcur.mutations.m01.flights.query_connecting_flights',
    'query_nonstop_flights': 'sapconcur.mutations.m01.flights.query_nonstop_flights',
    'query_trip_overviews': 'sapconcur.mutations.m01.trips.query_trip_overviews',
    'retrieve_booking_by_record_locator': 'sapconcur.mutations.m01.bookings.retrieve_booking_by_record_locator',
    'retrieve_location_data': 'sapconcur.mutations.m01.locations.retrieve_location_data',
    'revoke_reservation': 'sapconcur.mutations.m01.bookings.revoke_reservation',
    'update_booking_travelers': 'sapconcur.mutations.m01.bookings.update_booking_travelers',
}
