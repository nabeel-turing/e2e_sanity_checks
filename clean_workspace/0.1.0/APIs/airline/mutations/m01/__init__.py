from .airline import amend_booking_luggage_details, change_booking_itinerary, create_new_booking, escalate_to_support_agent, evaluate_mathematical_query, fetch_customer_profile, find_connecting_flights, find_nonstop_flights, get_available_airports, issue_travel_voucher, log_internal_thought, modify_booking_travelers, retrieve_booking_information, void_flight_booking

_function_map = {
    'amend_booking_luggage_details': 'airline.mutations.m01.airline.amend_booking_luggage_details',
    'change_booking_itinerary': 'airline.mutations.m01.airline.change_booking_itinerary',
    'create_new_booking': 'airline.mutations.m01.airline.create_new_booking',
    'escalate_to_support_agent': 'airline.mutations.m01.airline.escalate_to_support_agent',
    'evaluate_mathematical_query': 'airline.mutations.m01.airline.evaluate_mathematical_query',
    'fetch_customer_profile': 'airline.mutations.m01.airline.fetch_customer_profile',
    'find_connecting_flights': 'airline.mutations.m01.airline.find_connecting_flights',
    'find_nonstop_flights': 'airline.mutations.m01.airline.find_nonstop_flights',
    'get_available_airports': 'airline.mutations.m01.airline.get_available_airports',
    'issue_travel_voucher': 'airline.mutations.m01.airline.issue_travel_voucher',
    'log_internal_thought': 'airline.mutations.m01.airline.log_internal_thought',
    'modify_booking_travelers': 'airline.mutations.m01.airline.modify_booking_travelers',
    'retrieve_booking_information': 'airline.mutations.m01.airline.retrieve_booking_information',
    'void_flight_booking': 'airline.mutations.m01.airline.void_flight_booking',
}
