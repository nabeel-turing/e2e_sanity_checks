from typing import Optional, Dict, Any
from .SimulationEngine.db import DB
from .SimulationEngine import utils 
from .SimulationEngine import custom_errors, models
from uuid import UUID
import uuid
import datetime
from datetime import timezone, date, timedelta
from pydantic import ValidationError


def get_trip_summaries(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    created_after_date: Optional[str] = None,
    created_before_date: Optional[str] = None,
    last_modified_date: Optional[str] = None,
    booking_type: Optional[str] = None,
    userid_value: Optional[str] = None,
    include_metadata: Optional[bool] = False,
    items_per_page: Optional[int] = None,
    include_virtual_trip: Optional[int] = None, 
    include_canceled_trips: Optional[bool] = False,
    include_guest_bookings: Optional[bool] = False
) -> Dict[str, Any]:
    """Retrieves trip summaries for a user or company.

    This function retrieves trip summaries based on specified filter criteria.
    It requires the ITINER scope for authorization. To access company-wide trip data
    (by setting `userid_value` to 'ALL'), the authenticated user must possess either
    'Web Services Administrator' or 'Can Administer' roles. All parameters for filtering
    are optional. It is important to note that this function is not recommended for
    extracting large volumes of historical data. For comprehensive company-wide data needs,
    using Itinerary v4 is advised.

    Args:
        start_date (Optional[str]): UTC start date for trips (YYYY-MM-DD). Default: today - 30 days. Defaults to None.
        end_date (Optional[str]): UTC end date for trips (YYYY-MM-DD). Default: today + 12 months. Defaults to None.
        created_after_date (Optional[str]): UTC date for trips created on/after (YYYY-MM-DD). Defaults to None.
        created_before_date (Optional[str]): UTC date for trips created on/before (YYYY-MM-DD). Defaults to None.
        last_modified_date (Optional[str]): UTC last modified date/time of trips (format: date-time). Defaults to None.
        booking_type (Optional[str]): Filter by booking type. Possible values: 'Air', 'Car', 'Dining', 'Hotel', 'Parking', 'Rail', 'Ride'. Defaults to None.
        userid_value (Optional[str]): User's login ID or 'ALL' for company-wide access. Defaults to None(company-wide access).
        include_metadata (Optional[bool]): Include paging metadata in response. Defaults to False.
        items_per_page (Optional[int]): Number of items per page (default: 200 if page provided). Defaults to None.
        include_virtual_trip (Optional[int]): 1 to include virtual trips. Possible values: 0, 1. Defaults to None (treated as 0).
        include_canceled_trips (Optional[bool]): Include trips with Canceled status. Defaults to False.
        include_guest_bookings (Optional[bool]): Include guest bookings. Defaults to False.

    Returns:
        Dict[str, Any]: A dictionary containing a list of trip summaries and optional metadata.

    Raises:
        ValidationError: If input arguments fail validation.
    """
    # --- Argument Validation and Defaulting ---
    if userid_value == "":
        raise custom_errors.ValidationError("userid_value cannot be an empty string.")

    parsed_start_date = utils._parse_date_optional(start_date, "start_date")
    parsed_end_date = utils._parse_date_optional(end_date, "end_date")
    parsed_created_after_date = utils._parse_date_optional(created_after_date, "created_after_date")
    parsed_created_before_date = utils._parse_date_optional(created_before_date, "created_before_date")
    parsed_last_modified_date = utils._parse_datetime_optional(last_modified_date, "last_modified_date")

    if parsed_start_date and parsed_end_date and parsed_start_date > parsed_end_date:
        raise custom_errors.ValidationError("start_date cannot be after end_date.")
    if parsed_created_after_date and parsed_created_before_date and parsed_created_after_date > parsed_created_before_date:
        raise custom_errors.ValidationError("created_after_date cannot be after created_before_date.")

    if parsed_start_date is None:
        parsed_start_date = datetime.date.today() - datetime.timedelta(days=30)
    
    if parsed_end_date is None:
        today = datetime.date.today()
        try:
            parsed_end_date = datetime.date(today.year + 1, today.month, today.day)
        except ValueError:
            parsed_end_date = datetime.date(today.year + 1, 3, 1) - datetime.timedelta(days=1)

    allowed_booking_types = ['Air', 'Car', 'Dining', 'Hotel', 'Parking', 'Rail', 'Ride']
    booking_type_upper = None
    if booking_type:
        if booking_type not in allowed_booking_types:
            raise custom_errors.ValidationError(f"Invalid booking_type. Allowed values: {allowed_booking_types}")
        booking_type_upper = booking_type.upper()

    if include_virtual_trip is not None and include_virtual_trip not in [0, 1]:
        raise custom_errors.ValidationError("include_virtual_trip must be 0 or 1.")
    
    if items_per_page is not None and items_per_page <= 0:
        raise custom_errors.ValidationError("items_per_page must be a positive integer.")
    
    # --- Data Retrieval Strategy ---
    initial_trip_list = []
    target_user_uuid = None
    
    if userid_value and userid_value != 'ALL':
        # Since we don't have user_by_username, we need to find user by searching through users
        # or implement a proper userid lookup mechanism
        target_user_uuid = None
        for user_uuid, user_data in DB.get('users', {}).items():
            if user_data.get('user_name') == userid_value:
                target_user_uuid = user_uuid
                break
        
        if target_user_uuid:
            user_trip_ids = DB.get('trips_by_user', {}).get(target_user_uuid, [])
            all_trips_table = DB.get('trips', {})
            initial_trip_list = [all_trips_table[trip_id] for trip_id in user_trip_ids if trip_id in all_trips_table]
        else:
            initial_trip_list = []
    else:
        initial_trip_list = list(DB.get('trips', {}).values())

    # --- Filtering ---
    filtered_trips = []
    for trip in initial_trip_list:
        try:
            trip_start_date = datetime.date.fromisoformat(trip['start_date'])
            trip_end_date = datetime.date.fromisoformat(trip['end_date'])
            trip_created_dt = datetime.datetime.fromisoformat(trip['created_date'].replace('Z', '+00:00'))
            trip_last_modified_dt = datetime.datetime.fromisoformat(trip['last_modified_date'].replace('Z', '+00:00'))
        except (ValueError, TypeError, KeyError):
            continue

        if not (trip_start_date <= parsed_end_date and trip_end_date >= parsed_start_date):
            continue
        
        if parsed_created_after_date and trip_created_dt.date() < parsed_created_after_date:
            continue
        if parsed_created_before_date and trip_created_dt.date() > parsed_created_before_date:
            continue
        if parsed_last_modified_date and trip_last_modified_dt < parsed_last_modified_date:
            continue

        if booking_type_upper and trip.get('booking_type') != booking_type_upper:
            continue
        
        if trip.get('is_virtual_trip', False) and include_virtual_trip != 1:
            continue
        if trip.get('is_canceled', False) and not include_canceled_trips:
            continue
        if trip.get('is_guest_booking', False) and not include_guest_bookings:
            continue
            
        filtered_trips.append(trip)

    # --- Sorting ---
    filtered_trips.sort(key=lambda t: (datetime.date.fromisoformat(t['start_date']), t['trip_id']))

    # --- Pagination ---
    total_count = len(filtered_trips)
    limit = items_per_page
    if include_metadata and limit is None:
        limit = 200

    paginated_trips = filtered_trips
    if limit is not None:
        paginated_trips = filtered_trips[:limit]

    # --- Final Response Assembly ---
    output_summaries = [utils._format_trip_summary(trip) for trip in paginated_trips]
    response: Dict[str, Any] = {"summaries": output_summaries}

    if include_metadata:
        offset_marker = None
        if total_count > len(paginated_trips):
            last_trip = paginated_trips[-1]
            offset_marker = f"{last_trip['start_date']}_{last_trip['trip_id']}"

        response["metadata"] = {
            "total_count": total_count,
            "limit": limit,
            "offset_marker": offset_marker
        }
    
    if userid_value and userid_value != 'ALL' and not target_user_uuid:
         response["summaries"] = []
         if include_metadata:
             response["metadata"]["total_count"] = 0
             response["metadata"]["offset_marker"] = None
    
    return models.TripSummariesResponse(**response).model_dump(exclude_none=True)

def create_or_update_trip(user_id: UUID, raw_trip_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Creates a new trip or updates an existing one based on the provided input.

    This function serves as a central point for trip management. If an `ItinLocator`
    (trip ID) is provided and exists, the corresponding trip will be updated.
    Otherwise, a new trip will be created. The update process is destructive;
    it replaces all existing bookings on the trip with the new ones provided.

    Args:
        user_id (UUID): The unique identifier of the user performing the action.
        raw_trip_input (Dict[str, Any]): A dictionary containing the trip details,
            which will be validated against the `CreateOrUpdateTripInput` model.
            Expected keys include:
            - `ItinLocator` (Optional[str]): Unique identifier for the trip. If provided and exists, updates the trip; otherwise creates a new one.
            - `TripName` (str): Name of the trip.
            - `StartDateLocal` (str): Start date of the trip in YYYY-MM-DD format.
            - `EndDateLocal` (str): End date of the trip in YYYY-MM-DD format.
            - `Comments` (Optional[str]): Additional comments about the trip.
            - `IsVirtualTrip` (bool): Whether this is a virtual trip.
            - `IsGuestBooking` (bool): Whether this is a guest booking.
            - `Bookings` (List[Dict]): List of booking dictionaries, each containing:
                - `RecordLocator` (str): Booking record locator.
                - `BookingSource` (str): Source of the booking.
                - `ConfirmationNumber` (str): Confirmation number for the booking.
                - `Status` (str): Status of the booking (e.g., "CONFIRMED").
                - `FormOfPaymentName` (str): Name of the payment method.
                - `FormOfPaymentType` (str): Type of payment method.
                - `Delivery` (str): Delivery method for the booking.
                - `Passengers` (List[Dict]): List of passenger information dictionaries.
                - `Segments` (Optional[Dict]): Optional segments containing Air, Car, or Hotel bookings.

    Returns:
        Dict[str, Any]: A dictionary representing the created or updated trip,
            formatted for the API response.

    Raises:
        custom_errors.UserNotFoundError: If the user with the given `user_id` is not found.
        custom_errors.TripNotFoundError: If an `ItinLocator` is provided but the trip is not found.
        PydanticValidationError: If the input data in `raw_trip_input` fails validation.
    """
    try:
        trip_input = models.CreateOrUpdateTripInput.model_validate(raw_trip_input)
    except ValidationError as e:
        raise e

    if str(user_id) not in DB['users']:
        raise custom_errors.UserNotFoundError(f"User with ID '{user_id}' not found.")

    trip_id_str = trip_input.ItinLocator
    now_utc = datetime.datetime.now(timezone.utc)
    all_segments = []
    
    if trip_id_str and trip_id_str in DB['trips']:
        trip = DB['trips'][trip_id_str]
        trip_id = UUID(trip_id_str)
        for booking_id in trip.get('booking_ids', []):
            if booking_id in DB['bookings']:
                del DB['bookings'][booking_id]
        created_bookings, all_segments, new_booking_ids = utils._process_trip_bookings(trip_id, trip_input.Bookings)
        trip.update({
            'trip_name': trip_input.TripName,
            'last_modified_date': now_utc.isoformat(),
            'booking_ids': new_booking_ids
        })
        final_trip_state = trip
    else:
        if trip_id_str:
            raise custom_errors.TripNotFoundError(f"Trip with ItinLocator '{trip_id_str}' not found for update.")
        trip_id = uuid.uuid4()
        created_bookings, all_segments, new_booking_ids = utils._process_trip_bookings(trip_id, trip_input.Bookings)
        final_trip_state = {
            "trip_id": str(trip_id),
            "trip_name": trip_input.TripName,
            "user_id": str(user_id),
            "status": models.TripStatus.CONFIRMED.value,
            "created_date": now_utc.isoformat(),
            "last_modified_date": now_utc.isoformat(),
            "booking_ids": new_booking_ids,
            "is_virtual_trip": trip_input.is_virtual_trip,
            "is_guest_booking": trip_input.is_guest_booking,
            "destination_summary": "", # Default empty string
            "booking_type": None, # Default value, will be updated based on segments
        }

    # Derive trip properties from segments
    start_date, end_date = utils._get_trip_dates_from_segments(all_segments)
    final_trip_state['start_date'] = trip_input.StartDateLocal or start_date
    final_trip_state['end_date'] = trip_input.EndDateLocal or end_date
    
    air_segments = [s for s in all_segments if s.get('type') == 'AIR']
    if air_segments:
        final_trip_state['destination_summary'] = air_segments[-1].get('arrival_airport')
        final_trip_state['booking_type'] = 'AIR'
    else:
        # Fallback logic for other segment types if necessary
        final_trip_state['booking_type'] = all_segments[0].get('type') if all_segments else None

    # Ensure a default value for destination_summary to prevent downstream validation errors.
    final_trip_state.setdefault('destination_summary', '')

    DB['trips'][str(trip_id)] = final_trip_state
    
    # Update the trips_by_user index, ensuring no duplicates
    if str(user_id) not in DB['trips_by_user']:
        DB['trips_by_user'][str(user_id)] = []
    if str(trip_id) not in DB['trips_by_user'][str(user_id)]:
        DB['trips_by_user'][str(user_id)].append(str(trip_id))
    
    if final_trip_state['booking_ids']:
        utils.update_trip_on_booking_change(UUID(final_trip_state['booking_ids'][0]))
    
    # Associate all created bookings with the trip
    for booking in created_bookings:
        DB.setdefault('bookings_by_trip', {}).setdefault(str(trip_id), []).append(str(booking['booking_id']))

    # --- Assemble Response ---
    response_bookings = []
    for booking in created_bookings:
        response_bookings.append({
            "RecordLocator": booking['record_locator'],
            "BookingSource": booking['booking_source'],
            "DateModifiedUtc": booking['last_modified'],
            "DateBookedLocal": booking['date_booked_local'],
            "Passengers": booking['passengers'],
            "Segments": booking['segments']
        })

    return {
        "TripId": str(trip_id),
        "TripUri": f"/api/v3.0/itinerary/trips/{trip_id}",
        "TripName": final_trip_state['trip_name'],
        "Comments": trip_input.Comments,
        "StartDateLocal": final_trip_state['start_date'],
        "EndDateLocal": final_trip_state['end_date'],
        "DateModifiedUtc": final_trip_state['last_modified_date'],
        "Bookings": response_bookings
    }