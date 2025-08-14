"""
Airline Service Implementation
"""
import re
import random
import string
from typing import Any, Dict, List
from pydantic import TypeAdapter, BaseModel, ValidationError as PydanticValidationError

from .SimulationEngine import utils
from .SimulationEngine.custom_errors import (
    CertificateUpdateError,
    InsufficientFundsError,
    InvalidExpressionError,
    MismatchedPassengerCountError,
    PaymentMethodNotFoundError,
    ReservationNotFoundError,
    SeatsUnavailableError,
    UserNotFoundError,
    ValidationError as CustomValidationError,
    FlightNotFoundError,
)
from .SimulationEngine.db import DB
from .SimulationEngine.models import Passenger, PaymentMethodInReservation, FlightInReservation

# A hardcoded mapping of airport codes to city names, as this is not available in the database.
_AIRPORT_CITY_MAPPING = {
    "SFO": "San Francisco", "JFK": "New York", "LAX": "Los Angeles", "ORD": "Chicago", "DFW": "Dallas",
    "DEN": "Denver", "SEA": "Seattle", "ATL": "Atlanta", "MIA": "Miami", "BOS": "Boston",
    "PHX": "Phoenix", "IAH": "Houston", "LAS": "Las Vegas", "MCO": "Orlando", "EWR": "Newark",
    "CLT": "Charlotte", "MSP": "Minneapolis", "DTW": "Detroit", "PHL": "Philadelphia", "LGA": "LaGuardia",
}

class FlightInput(BaseModel):
    flight_number: str
    date: str

def _generate_random_id(length=6):
    """Generates a random alphanumeric ID."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def list_all_airports() -> Dict[str, str]:
    """
    List all airports and their corresponding cities based on available flights.

    Returns:
        Dict[str, str]: A dictionary mapping airport IATA codes to city names for airports with flights. 
                        Each key represents the city IATA code and value represents the city name.
    """
    flights = DB.get("flights", {})
    airport_codes = set()
    for flight in flights.values():
        airport_codes.add(flight.get("origin"))
        airport_codes.add(flight.get("destination"))

    # Filter the mapping to only include airports that are in our flight data
    return {code: city for code, city in _AIRPORT_CITY_MAPPING.items() if code in airport_codes}


def search_direct_flight(origin: str, destination: str, date: str) -> List[Dict[str, Any]]:
    """
    Search direct flights between two cities on a specific date.

    Args:
        origin (str): The origin city airport in three letters, such as 'JFK'.
        destination (str): The destination city airport in three letters, such as 'LAX'.
        date (str): The date of the flight in the format 'YYYY-MM-DD'.

    Returns:
        List[Dict[str, Any]]: A list of available direct flights. Each flight is a dictionary with the following keys:
            - flight_number(str): The flight number.
            - origin(str): The origin city airport in three letters, such as 'JFK'.
            - destination(str): The destination city airport in three letters, such as 'LAX'.
            - scheduled_departure_time_est(str): The scheduled departure time in EST. Date format is 'HH:MM:SS'.
            - scheduled_arrival_time_est(str): The scheduled arrival time in EST. Date format is 'HH:MM:SS'.
            - status(str): The status of the flight.
            - actual_departure_time_est(str): The actual departure time in EST. Date format is 'YYYY-MM-DDTHH:MM:SS'.
            - actual_arrival_time_est(str): The actual arrival time in EST. Date format is 'YYYY-MM-DDTHH:MM:SS'.
            - available_seats(Dict[str, int]): The number of available seats. It can have following keys:
                - basic_economy(int): The number of available basic economy seats.
                - economy(int): The number of available economy seats.
                - business(int): The number of available business seats.
            - prices(Dict[str, float]): The price of the flight. It can have following keys:
                - basic_economy(float): The price of the basic economy seat.
                - economy(float): The price of the economy seat.
                - business(float): The price of the business seat.

    Raises:
        CustomValidationError: If the origin, destination, or date is not a non-empty string.
    """
    if not isinstance(origin, str) or not origin.strip():
        raise CustomValidationError("Origin must be a non-empty string.")
    if not isinstance(destination, str) or not destination.strip():
        raise CustomValidationError("Destination must be a non-empty string.")
    if not isinstance(date, str) or not date.strip():
        raise CustomValidationError("Date must be a non-empty string.")

    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date):
        raise CustomValidationError("Date must be in YYYY-MM-DD format.")

    return utils.search_flights(origin, destination, date)


def search_onestop_flight(origin: str, destination: str, date: str) -> List[List[Dict[str, Any]]]:
    """
    Search one-stop flights between two cities on a specific date.

    Args:
        origin (str): The origin city airport in three letters, such as 'JFK'.
        destination (str): The destination city airport in three letters, such as 'LAX'.
        date (str): The date of the flight in the format 'YYYY-MM-DD'.

    Returns:
        List[List[Dict[str, Any]]]: A list of available one-stop flight combinations.
            Each flight is a list of two dictionaries, each representing a flight. Each element will have only two flights
            First element is the first flight, second element is the second flight.
            Each flight is a dictionary with the following keys:
                - flight_number(str): The flight number.
                - origin(str): The origin city airport in three letters, such as 'JFK'.
                - destination(str): The destination city airport in three letters, such as 'LAX'.
                - scheduled_departure_time_est(str): The scheduled departure time in EST. Date format is 'HH:MM:SS'.
                - scheduled_arrival_time_est(str): The scheduled arrival time in EST. Date format is 'HH:MM:SS'.
                - status(str): The status of the flight.
                - actual_departure_time_est(str): The actual departure time in EST. Date format is 'YYYY-MM-DDTHH:MM:SS'.
                - actual_arrival_time_est(str): The actual arrival time in EST. Date format is 'YYYY-MM-DDTHH:MM:SS'.
                - available_seats(Dict[str, int]): The number of available seats. It can have following keys:
                    - basic_economy(int): The number of available basic economy seats.
                    - economy(int): The number of available economy seats.
                    - business(int): The number of available business seats.
                - prices(Dict[str, float]): The price of the flight. It can have following keys:
                    - basic_economy(float): The price of the basic economy seat.
                    - economy(float): The price of the economy seat.
                    - business(float): The price of the business seat.

    Raises:
        CustomValidationError: If the origin, destination, or date is not a non-empty string.
    """
    if not isinstance(origin, str) or not origin.strip():
        raise CustomValidationError("Origin must be a non-empty string.")
    if not isinstance(destination, str) or not destination.strip():
        raise CustomValidationError("Destination must be a non-empty string.")
    if not isinstance(date, str) or not date.strip():
        raise CustomValidationError("Date must be a non-empty string.")
    
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date):
        raise CustomValidationError("Date must be in YYYY-MM-DD format.")

    return utils.search_onestop_flights(origin, destination, date)


def get_user_details(user_id: str) -> Dict[str, Any]:
    """
    Get the details of a user, including their reservations.

    Args:
        user_id (str): The user id, such as 'sara_doe_496'.

    Returns:
        Dict[str, Any]: The user's details. The structure is as follows:
            - name (Dict[str, str]): A dictionary containing the user's name.
                - first_name (str): The user's first name (e.g., "Mia").
                - last_name (str): The user's last name (e.g., "Li").
            - address (Dict[str, str]): A dictionary containing the user's address.
                - address1 (str): The primary address line (e.g., "975 Sunset Drive").
                - address2 (str): The secondary address line, if applicable (e.g., "Suite 217").
                - city (str): The city name (e.g., "Austin").
                - state (str): The state code (e.g., "TX").
                - zip (str): The ZIP code (e.g., "78750").
                - country (str): The country name (e.g., "USA").
            - email (str): The user's email address (e.g., "mia.li3818@example.com").
            - dob (str): The user's date of birth in "YYYY-MM-DD" format (e.g., "1990-04-05").
            - payment_methods (Dict[str, Dict[str, Any]]): A mapping of payment method IDs
                to payment method details. Each payment method has the following structure:
                - source (str): The payment source type ("credit_card", "gift_card", or "certificate").
                - id (str): The unique payment method identifier.
                - brand (str, optional): The credit card brand (e.g., "visa") for credit cards.
                - last_four (str, optional): The last four digits of the card for credit cards.
                - amount (int, optional): The available balance for gift cards and certificates.
            - saved_passengers (List[Dict[str, str]]): A list of saved passenger profiles.
                Each passenger has the following structure:
                - first_name (str): The passenger's first name (e.g., "Amelia").
                - last_name (str): The passenger's last name (e.g., "Ahmed").
                - dob (str): The passenger's date of birth in "YYYY-MM-DD" format (e.g., "1957-03-21").
            - membership (str): The user's membership level ("gold", "silver", or "regular").
            - reservations (List[str]): A list of reservation IDs associated with the user
                (e.g., ["NO6JO3", "AIXC49", "HKEG34"]).

    Raises:
        CustomValidationError: If user_id is not a non-empty string.
        UserNotFoundError: If the user with the specified user_id is not found in the system.
    """
    if not isinstance(user_id, str) or not user_id:
        raise CustomValidationError("User ID must be a non-empty string.")
    
    user = utils.get_user(user_id)
    if user:
        return user
    raise UserNotFoundError(f"User with ID '{user_id}' not found.")


def get_reservation_details(reservation_id: str) -> Dict[str, Any]:
    """
    Get the details of a reservation.

    Args:
        reservation_id (str): The reservation id, such as '8JX2WO'.

    Returns:
        Dict[str, Any]: The reservation details.
            It can have following keys:
            - reservation_id(str): The reservation ID.
            - user_id(str): The user ID.
            - origin(str): The origin city airport in three letters, such as 'JFK'.
            - destination(str): The destination city airport in three letters, such as 'LAX'.
            - flight_type(str): The type of flight.
            - cabin(str): The cabin class.
            - flights(List[Dict[str, Any]]): The list of flights. Each flight is a dictionary with the following keys:
                - flight_number(str): The flight number.
                - origin(str): The origin city airport in three letters, such as 'JFK'.
                - destination(str): The destination city airport in three letters, such as 'LAX'.
                - date(str): The date of the flight in the format 'YYYY-MM-DD'.
                - price(float): The price of the flight.
            - passengers(List[Dict[str, str]]): The list of passengers. Each passenger is a dictionary with the following keys:
                - first_name(str): The first name of the passenger.
                - last_name(str): The last name of the passenger.
                - dob(str): The date of birth of the passenger.
            - payment_history(List[Dict[str, Any]]): The list of payment history. Each payment is a dictionary with the following keys:
                - payment_id(str): The ID of the payment.
                - amount(float): The amount of the payment.
            - created_at(str): The creation time of the reservation.
            - total_baggages(int): The total number of baggage items.
            - nonfree_baggages(int): The number of non-free baggage items.
            - insurance(str): The insurance status.

    Raises:
        CustomValidationError: If the reservation ID is not a non-empty string.
        ReservationNotFoundError: If the reservation is not found.
    """
    if not isinstance(reservation_id, str) or not reservation_id:
        raise CustomValidationError("Reservation ID must be a non-empty string.")
        
    reservation = utils.get_reservation(reservation_id)
    if reservation:
        return reservation
    raise ReservationNotFoundError(f"Reservation with ID '{reservation_id}' not found.")


def calculate(expression: str) -> str:
    """
    Calculate the result of a mathematical expression.

    Args:
        expression (str): The mathematical expression to calculate.

    Returns:
        str: The result of the calculation.
    
    Raises:
        CustomValidationError: If the expression is not a non-empty string.
        InvalidExpressionError: If the expression contains invalid characters.
        ValueError: If the expression is invalid.
    """
    if not isinstance(expression, str) or not expression:
        raise CustomValidationError("Expression must be a non-empty string.")
    
    if not all(char in "0123456789+-*/(). " for char in expression):
        raise InvalidExpressionError("Expression contains invalid characters.")
    try:
        return str(round(float(eval(expression, {"__builtins__": None}, {})), 2))
    except Exception as e:
        raise ValueError(f"Error evaluating expression: {e}")


def cancel_reservation(reservation_id: str) -> Dict[str, Any]:
    """
    Cancel the whole reservation.

    Args:
        reservation_id (str): The reservation ID to cancel.

    Returns:
        Dict[str, Any]: The updated reservation with a 'cancelled' status. It can have following keys:
            - reservation_id(str): The reservation ID.
            - user_id(str): The user ID.
            - origin(str): The origin city airport in three letters, such as 'JFK'.
            - destination(str): The destination city airport in three letters, such as 'LAX'.
            - flight_type(str): The type of flight.
            - cabin(str): The cabin class.
            - flights(List[Dict[str, Any]]): The list of flights. Each flight is a dictionary with the following keys:
                - flight_number(str): The flight number.
                - origin(str): The origin city airport in three letters, such as 'JFK'.
                - destination(str): The destination city airport in three letters, such as 'LAX'.
                - date(str): The date of the flight in the format 'YYYY-MM-DD'.
                - price(float): The price of the flight.
            - passengers(List[Dict[str, str]]): The list of passengers. Each passenger is a dictionary with the following keys:
                - first_name(str): The first name of the passenger.
                - last_name(str): The last name of the passenger.
                - dob(str): The date of birth of the passenger.
            - payment_history(List[Dict[str, Any]]): The list of payment history. Each payment is a dictionary with the following keys:
                - payment_id(str): The ID of the payment.
                - amount(float): The amount of the payment.
            - created_at(str): The creation time of the reservation.
            - total_baggages(int): The total number of baggage items.
            - nonfree_baggages(int): The number of non-free baggage items.
            - insurance(str): The insurance status.

    Raises:
        CustomValidationError: If the reservation ID is not a non-empty string.
        ReservationNotFoundError: If the reservation is not found.
    """
    if not isinstance(reservation_id, str) or not reservation_id:
        raise CustomValidationError("Reservation ID must be a non-empty string.")

    reservations = DB.get("reservations", {})
    if reservation_id not in reservations:
        raise ReservationNotFoundError(f"Reservation with ID '{reservation_id}' not found.")
    
    reservation = reservations[reservation_id]

    refunds = []
    for payment in reservation.get("payment_history", []):
        refunds.append(
            {
                "payment_id": payment["payment_id"],
                "amount": -payment["amount"],
            }
        )
    reservation.get("payment_history", []).extend(refunds)
    reservation["status"] = "cancelled"
    return reservation


def update_reservation_passengers(reservation_id: str, passengers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Update the passenger information of a reservation.

    Args:
        reservation_id (str): The reservation ID to update.
        passengers (List[Dict[str, Any]]): The new list of passengers.

    Returns:
        Dict[str, Any]: The updated reservation. It can have following keys:
            - reservation_id(str): The reservation ID.
            - user_id(str): The user ID.
            - origin(str): The origin city airport in three letters, such as 'JFK'.
            - destination(str): The destination city airport in three letters, such as 'LAX'.
            - flight_type(str): The type of flight.
            - cabin(str): The cabin class.
            - flights(List[Dict[str, Any]]): The list of flights. Each flight is a dictionary with the following keys:
                - flight_number(str): The flight number.
                - origin(str): The origin city airport in three letters, such as 'JFK'.
                - destination(str): The destination city airport in three letters, such as 'LAX'.
                - date(str): The date of the flight in the format 'YYYY-MM-DD'.
                - price(float): The price of the flight.
            - passengers(List[Dict[str, str]]): The list of passengers. Each passenger is a dictionary with the following keys:
                - first_name(str): The first name of the passenger.
                - last_name(str): The last name of the passenger.
                - dob(str): The date of birth of the passenger.
            - payment_history(List[Dict[str, Any]]): The list of payment history. Each payment is a dictionary with the following keys:
                - payment_id(str): The ID of the payment.
                - amount(float): The amount of the payment.
            - created_at(str): The creation time of the reservation.
            - total_baggages(int): The total number of baggage items.
            - nonfree_baggages(int): The number of non-free baggage items.
            - insurance(str): The insurance status.
    
    Raises:
        CustomValidationError: If the reservation ID is not a non-empty string.
        PydanticValidationError: If the passengers are not valid.
        ReservationNotFoundError: If the reservation is not found.
        MismatchedPassengerCountError: If the number of passengers does not match.
    """
    if not isinstance(reservation_id, str) or not reservation_id:
        raise CustomValidationError("Reservation ID must be a non-empty string.")
    
    try:
        passengers = [p.model_dump() for p in TypeAdapter(List[Passenger]).validate_python(passengers)]
    except PydanticValidationError as e:
        raise e

    reservations = DB.get("reservations", {})
    if reservation_id not in reservations:
        raise ReservationNotFoundError(f"Reservation with ID '{reservation_id}' not found.")
    
    reservation = reservations[reservation_id]
    if len(passengers) != len(reservation.get("passengers", [])):
        raise MismatchedPassengerCountError("Number of passengers does not match.")
    
    reservation["passengers"] = passengers
    return reservation


def update_reservation_baggages(
    reservation_id: str,
    total_baggages: int,
    nonfree_baggages: int,
    payment_id: str,
) -> Dict[str, Any]:
    """
    Update the baggage information of a reservation.

    Args:
        reservation_id (str): The reservation ID to update.
        total_baggages (int): The new total number of baggage items.
        nonfree_baggages (int): The new number of non-free baggage items.
        payment_id (str): The ID of the payment method to use.

    Returns:
        Dict[str, Any]: The updated reservation. It can have following keys:
            - reservation_id(str): The reservation ID.
            - user_id(str): The user ID.
            - origin(str): The origin city airport in three letters, such as 'JFK'.
            - destination(str): The destination city airport in three letters, such as 'LAX'.
            - flight_type(str): The type of flight.
            - cabin(str): The cabin class.
            - flights(List[Dict[str, Any]]): The list of flights. Each flight is a dictionary with the following keys:
                - flight_number(str): The flight number.
                - origin(str): The origin city airport in three letters, such as 'JFK'.
                - destination(str): The destination city airport in three letters, such as 'LAX'.
                - date(str): The date of the flight in the format 'YYYY-MM-DD'.
                - price(float): The price of the flight.
            - passengers(List[Dict[str, str]]): The list of passengers. Each passenger is a dictionary with the following keys:
                - first_name(str): The first name of the passenger.
                - last_name(str): The last name of the passenger.
                - dob(str): The date of birth of the passenger.
            - payment_history(List[Dict[str, Any]]): The list of payment history. Each payment is a dictionary with the following keys:
                - payment_id(str): The ID of the payment.
                - amount(float): The amount of the payment.
            - created_at(str): The creation time of the reservation.
            - total_baggages(int): The total number of baggage items.
            - nonfree_baggages(int): The number of non-free baggage items.
            - insurance(str): The insurance status.

    Raises:
        CustomValidationError: If the reservation ID, total baggages, non-free baggages, or payment ID is not a non-empty string.
        ReservationNotFoundError: If the reservation is not found.
        UserNotFoundError: If the user is not found.
        PaymentMethodNotFoundError: If the payment method is not found.
        InsufficientFundsError: If the gift card balance is not enough.
    """
    if not isinstance(reservation_id, str) or not reservation_id:
        raise CustomValidationError("Reservation ID must be a non-empty string.")
    if not isinstance(total_baggages, int) or total_baggages < 0:
        raise CustomValidationError("Total baggages must be a non-negative integer.")
    if not isinstance(nonfree_baggages, int) or nonfree_baggages < 0:
        raise CustomValidationError("Non-free baggages must be a non-negative integer.")
    if not isinstance(payment_id, str) or not payment_id:
        raise CustomValidationError("Payment ID must be a non-empty string.")

    users, reservations = DB.get("users", {}), DB.get("reservations", {})
    if reservation_id not in reservations:
        raise ReservationNotFoundError(f"Reservation with ID '{reservation_id}' not found.")
    
    reservation = reservations[reservation_id]
    user = users.get(reservation["user_id"])
    if not user:
        raise UserNotFoundError(f"User for reservation '{reservation_id}' not found.")

    total_price = 50 * max(0, nonfree_baggages - reservation.get("nonfree_baggages", 0))
    
    if "certificate" in payment_id:
        raise CertificateUpdateError("Certificate cannot be used to update reservation.")
    
    payment_methods = user.get("payment_methods", {})
    if payment_id not in payment_methods:
        raise PaymentMethodNotFoundError(f"Payment method '{payment_id}' not found.")
    
    payment_method = payment_methods[payment_id]
    
    if payment_method.get("source") == "gift_card" and payment_method.get("amount", 0) < total_price:
        raise InsufficientFundsError("Gift card balance is not enough.")

    reservation["total_baggages"] = total_baggages
    reservation["nonfree_baggages"] = nonfree_baggages
    
    if payment_method.get("source") == "gift_card":
        payment_method["amount"] -= total_price

    if total_price != 0:
        reservation.get("payment_history", []).append(
            {"payment_id": payment_id, "amount": total_price}
        )

    return reservation


def update_reservation_flights(
    reservation_id: str,
    cabin: str,
    flights: List[Dict[str, Any]],
    payment_id: str,
) -> Dict[str, Any]:
    """
    Update the flight information of a reservation.

    Args:
        reservation_id (str): The reservation ID to update.
        cabin (str): The new cabin class.
        flights (List[Dict[str, Any]]): The new list of flights.
        payment_id (str): The ID of the payment method to use.

    Returns:
        Dict[str, Any]: The updated reservation. It can have following keys:
            - reservation_id(str): The reservation ID.
            - user_id(str): The user ID.
            - origin(str): The origin city airport in three letters, such as 'JFK'.
            - destination(str): The destination city airport in three letters, such as 'LAX'.
            - flight_type(str): The type of flight.
            - cabin(str): The cabin class.
            - flights(List[Dict[str, Any]]): The list of flights. Each flight is a dictionary with the following keys:
                - flight_number(str): The flight number.
                - origin(str): The origin city airport in three letters, such as 'JFK'.
                - destination(str): The destination city airport in three letters, such as 'LAX'.
                - date(str): The date of the flight in the format 'YYYY-MM-DD'.
                - price(float): The price of the flight.
            - passengers(List[Dict[str, Any]]): The list of passengers. Each passenger is a dictionary with the following keys:
                - first_name(str): The first name of the passenger.
                - last_name(str): The last name of the passenger.
                - dob(str): The date of birth of the passenger.
            - payment_history(List[Dict[str, Any]]): The list of payment history. Each payment is a dictionary with the following keys:
                - payment_id(str): The ID of the payment.
                - amount(float): The amount of the payment.
            - created_at(str): The creation time of the reservation.
            - total_baggages(int): The total number of baggage items.
            - nonfree_baggages(int): The number of non-free baggage items.
            - insurance(str): The insurance status.

    Raises:
        CustomValidationError: If the reservation ID, cabin, or payment ID is not a non-empty string.
        PydanticValidationError: If the flights are not valid.
        ReservationNotFoundError: If the reservation is not found.
        UserNotFoundError: If the user is not found.
        FlightNotFoundError: If the flight is not found.
        SeatsUnavailableError: If the seats are not available.
    """
    if not isinstance(reservation_id, str) or not reservation_id:
        raise CustomValidationError("Reservation ID must be a non-empty string.")
    if not isinstance(cabin, str) or not cabin:
        raise CustomValidationError("Cabin must be a non-empty string.")
    if not isinstance(payment_id, str) or not payment_id:
        raise CustomValidationError("Payment ID must be a non-empty string.")
    
    try:
        flights = [f.model_dump() for f in TypeAdapter(List[FlightInput]).validate_python(flights)]
    except PydanticValidationError as e:
        raise e

    users, reservations, flights_db = DB.get("users", {}), DB.get("reservations", {}), DB.get("flights", {})
    if reservation_id not in reservations:
        raise ReservationNotFoundError(f"Reservation with ID '{reservation_id}' not found.")
    
    reservation = reservations[reservation_id]
    user = users.get(reservation["user_id"])
    if not user:
        raise UserNotFoundError(f"User for reservation '{reservation_id}' not found.")

    total_price = 0
    new_flights = []
    num_passengers = len(reservation.get("passengers", []))

    for flight_info in flights:
        flight_number = flight_info.get("flight_number")
        date = flight_info.get("date")
        
        # if existing flight, ignore
        if _ := [
            f
            for f in reservation["flights"]
            if f["flight_number"] == flight_number
            and f["date"] == date
            and cabin == reservation["cabin"]
        ]:
            price = _[0]["price"]
            total_price += price * num_passengers
            new_flights.append({
                "flight_number": flight_number, "date": date, "price": price,
                "origin": _[0]["origin"], "destination": _[0]["destination"],
            })
            continue
        
        flight_data = flights_db.get(flight_number)
        if not flight_data:
            raise FlightNotFoundError(f"Flight '{flight_number}' not found.")
            
        flight_date_data = flight_data.get("dates", {}).get(date)
        if not flight_date_data:
            raise FlightNotFoundError(f"Flight '{flight_number}' not found on date {date}.")

        if flight_date_data.get("status") != "available":
            raise FlightNotFoundError(f"Flight '{flight_number}' is not available on date {date}.")
            
        if flight_date_data.get("available_seats", {}).get(cabin, 0) < num_passengers:
            raise SeatsUnavailableError(f"Not enough seats on flight '{flight_number}'.")
            
        price = flight_date_data.get("prices", {}).get(cabin, 0)
        total_price += price * num_passengers
        
        new_flights.append({
            "flight_number": flight_number, "date": date, "price": price,
            "origin": flight_data.get("origin"), "destination": flight_data.get("destination"),
        })

    total_price -= sum(f.get("price", 0) for f in reservation.get("flights", [])) * num_passengers

    payment_methods = user.get("payment_methods", {})
    if payment_id not in payment_methods:
        raise PaymentMethodNotFoundError(f"Payment method '{payment_id}' not found.")
        
    payment_method = payment_methods[payment_id]
    if payment_method.get("source") == "certificate":
        raise CertificateUpdateError("Certificate cannot be used to update reservation.")
        
    if payment_method.get("source") == "gift_card" and payment_method.get("amount", 0) < total_price:
        raise InsufficientFundsError("Gift card balance is not enough.")

    if payment_method.get("source") == "gift_card":
        payment_method["amount"] -= total_price
        
    reservation["flights"] = new_flights
    if total_price != 0:
        reservation.get("payment_history", []).append(
            {"payment_id": payment_id, "amount": total_price}
        )
    return reservation


def send_certificate(user_id: str, amount: int) -> str:
    """
    Send a certificate to a user.

    Args:
        user_id (str): The ID of the user to send the certificate to.
        amount (int): The amount of the certificate.

    Returns:
        str: A confirmation message.
    
    Raises:
        CustomValidationError: If the user ID is not a non-empty string or amount is not a positive integer.
        UserNotFoundError: If the user is not found.
    """
    if not isinstance(user_id, str) or not user_id:
        raise CustomValidationError("User ID must be a non-empty string.")
    if not isinstance(amount, int) or amount <= 0:
        raise CustomValidationError("Amount must be a positive integer.")

    users = DB.get("users", {})
    if user_id not in users:
        raise UserNotFoundError(f"User with ID '{user_id}' not found.")
    
    user = users[user_id]
    
    payment_id = f"certificate_{_generate_random_id()}"
    while payment_id in user.get("payment_methods", {}):
        payment_id = f"certificate_{_generate_random_id()}"

    user.get("payment_methods", {})[payment_id] = {
        "source": "certificate", "amount": amount, "id": payment_id,
    }
    return f"Certificate {payment_id} added to user {user_id} with amount {amount}."


def think(thought: str) -> str:
    """
    Use the tool to think about something. It will not obtain new information 
    or change the database, but just append the thought to the log.

    Args:
        thought (str): A thought to think about.

    Returns:
        str: An empty string.
    """
    return ""


def transfer_to_human_agents(summary: str) -> str:
    """
    Transfer the user to a human agent, with a summary of the user's issue.

    Args:
        summary (str): A summary of the user's issue.

    Returns:
        str: A confirmation message.
    
    Raises:
        CustomValidationError: If the summary is not a non-empty string.
    """
    if not isinstance(summary, str) or not summary:
        raise CustomValidationError("Summary must be a non-empty string.")
    
    return "Transfer successful"


def book_reservation(
    user_id: str, origin: str, destination: str, flight_type: str, cabin: str,
    flights: List[Dict[str, Any]], passengers: List[Dict[str, Any]],
    payment_methods: List[Dict[str, Any]], total_baggages: int,
    nonfree_baggages: int, insurance: str,
) -> Dict[str, Any]:
    """
    Book a reservation for flights with specified passengers and payment methods.

    Args:
        user_id (str): The ID of the user making the reservation (e.g., "sara_doe_496").
        origin (str): The origin airport code in three letters (e.g., "JFK").
        destination (str): The destination airport code in three letters (e.g., "LAX").
        flight_type (str): The type of flight ("one_way" or "round_trip").
        cabin (str): The cabin class ("basic_economy", "economy", or "business").
        flights (List[Dict[str, Any]]): A list of flight dictionaries. Each flight dictionary
            must contain the following structure:
            - flight_number (str): The unique identifier for the flight (e.g., "HAT001").
            - date (str): The flight date in "YYYY-MM-DD" format (e.g., "2024-05-15").
        passengers (List[Dict[str, Any]]): A list of passenger dictionaries. Each passenger
            dictionary must contain the following structure:
            - first_name (str): The passenger's first name (e.g., "John").
            - last_name (str): The passenger's last name (e.g., "Doe").
            - dob (str): The passenger's date of birth in "YYYY-MM-DD" format (e.g., "1990-01-01").
        payment_methods (List[Dict[str, Any]]): A list of payment method dictionaries. Each
            payment dictionary must contain the following structure:
            - payment_id (str): The ID of the payment method to use (e.g., "credit_card_4421486").
            - amount (float): The amount to be charged for this payment (e.g., 250.0).
        total_baggages (int): The total number of baggage items (non-negative integer, e.g., 2).
        nonfree_baggages (int): The number of non-free baggage items (non-negative integer, e.g., 1).
        insurance (str): Whether to include insurance ("yes" or "no").

    Returns:
        Dict[str, Any]: The newly created reservation. The structure is as follows:
            - reservation_id (str): The unique identifier for the reservation (e.g., "8JX2WO").
            - user_id (str): The ID of the user who made the reservation.
            - origin (str): The origin airport code (e.g., "JFK").
            - destination (str): The destination airport code (e.g., "LAX").
            - flight_type (str): The type of flight ("one_way" or "round_trip").
            - cabin (str): The cabin class ("basic_economy", "economy", or "business").
            - flights (List[Dict[str, Any]]): A list of flight dictionaries. Each flight has
                the following structure:
                - flight_number (str): The unique identifier for the flight (e.g., "HAT001").
                - date (str): The flight date in "YYYY-MM-DD" format (e.g., "2024-05-15").
                - price (int): The price for this flight in dollars.
                - origin (str): The origin airport code (e.g., "JFK").
                - destination (str): The destination airport code (e.g., "LAX").
            - passengers (List[Dict[str, str]]): A list of passenger dictionaries. Each passenger
                has the following structure:
                - first_name (str): The passenger's first name (e.g., "John").
                - last_name (str): The passenger's last name (e.g., "Doe").
                - dob (str): The passenger's date of birth in "YYYY-MM-DD" format (e.g., "1990-01-01").
            - payment_history (List[Dict[str, Any]]): A list of payment dictionaries. Each payment
                has the following structure:
                - payment_id (str): The ID of the payment method used (e.g., "credit_card_4421486").
                - amount (float): The amount charged for this payment.
            - created_at (str): The timestamp when the reservation was created (e.g., "2024-05-15T15:00:00").
            - total_baggages (int): The total number of baggage items.
            - nonfree_baggages (int): The number of non-free baggage items.
            - insurance (str): Whether insurance was included ("yes" or "no").
            - status (str, optional): The reservation status (e.g., "confirmed", "cancelled").

    Raises:
        CustomValidationError: If any string argument (user_id, origin, destination, flight_type, 
                              cabin, insurance) is not a non-empty string, or if total_baggages 
                              or nonfree_baggages is not a non-negative integer.
        PydanticValidationError: If the passengers, flights, or payment_methods lists do not 
                                match their expected model structures (Passenger, FlightInput, 
                                PaymentMethodInReservation respectively).
        UserNotFoundError: If the user with the specified user_id is not found.
        FlightNotFoundError: If any flight in the flights list is not found or not available 
                            on the specified date.
        SeatsUnavailableError: If there are not enough seats available in the specified cabin 
                              class for the number of passengers.
        PaymentMethodNotFoundError: If any payment_id in payment_methods is not found in 
                                   the user's payment methods.
        InsufficientFundsError: If the payment method balance (gift card or certificate) 
                               is insufficient for the required amount.
        ValueError: If the total payment amount does not match the calculated total price 
                   (flight costs + insurance + baggage fees).
    """
    if not all(isinstance(arg, str) and arg for arg in [user_id, origin, destination, flight_type, cabin, insurance]):
        raise CustomValidationError("Invalid string argument provided.")
    if not isinstance(total_baggages, int) or total_baggages < 0:
        raise CustomValidationError("Total baggages must be a non-negative integer.")
    if not isinstance(nonfree_baggages, int) or nonfree_baggages < 0:
        raise CustomValidationError("Non-free baggages must be a non-negative integer.")
    
    try:
        passengers = [p.model_dump() for p in TypeAdapter(List[Passenger]).validate_python(passengers)]
        flights = [f.model_dump() for f in TypeAdapter(List[FlightInput]).validate_python(flights)]
        payment_methods = [p.model_dump() for p in TypeAdapter(List[PaymentMethodInReservation]).validate_python(payment_methods)]
    except PydanticValidationError as e:
        raise e

    reservations, users, flights_db = DB.get("reservations", {}), DB.get("users", {}), DB.get("flights", {})
    if user_id not in users:
        raise UserNotFoundError(f"User with ID '{user_id}' not found.")
    user = users[user_id]

    reservation_id = _generate_random_id()
    while reservation_id in reservations:
        reservation_id = _generate_random_id()

    reservation = {
        "reservation_id": reservation_id, "user_id": user_id, "origin": origin,
        "destination": destination, "flight_type": flight_type, "cabin": cabin,
        "flights": [], "passengers": passengers, "payment_history": payment_methods,
        "created_at": "2024-05-15T15:00:00", "total_baggages": total_baggages,
        "nonfree_baggages": nonfree_baggages, "insurance": insurance,
    }

    total_price = 0
    for flight_info in flights:
        flight_number = flight_info.get("flight_number")
        date = flight_info.get("date")
        flight_data = flights_db.get(flight_number)
        if not flight_data:
            raise FlightNotFoundError(f"Flight '{flight_number}' not found.")
        flight_date_data = flight_data.get("dates", {}).get(date)
        if not flight_date_data:
            raise FlightNotFoundError(f"Flight '{flight_number}' not found on date {date}.")
        if flight_date_data.get("status") != "available":
            raise FlightNotFoundError(f"Flight '{flight_number}' is not available on date {date}.")
        if flight_date_data.get("available_seats", {}).get(cabin, 0) < len(passengers):
            raise SeatsUnavailableError(f"Not enough seats on flight '{flight_number}'.")
        
        price = flight_date_data.get("prices", {}).get(cabin, 0)
        reservation["flights"].append({
            "flight_number": flight_number, "date": date, "price": price,
            "origin": flight_data.get("origin"), "destination": flight_data.get("destination"),
        })
        total_price += price * len(passengers)

    if insurance == "yes":
        total_price += 30 * len(passengers)
    total_price += 50 * nonfree_baggages

    paid_amount = sum(p.get("amount", 0) for p in payment_methods)
    if paid_amount != total_price:
        raise ValueError(f"Payment amount does not add up, total price is {total_price}, but paid {paid_amount}.")

    for payment_method in payment_methods:
        payment_id = payment_method.get("payment_id")
        amount = payment_method.get("amount")
        user_payment_method = user.get("payment_methods", {}).get(payment_id)
        if not user_payment_method:
            raise PaymentMethodNotFoundError(f"Payment method '{payment_id}' not found.")
        if user_payment_method.get("source") in ["gift_card", "certificate"]:
            if user_payment_method.get("amount", 0) < amount:
                raise InsufficientFundsError(f"Not enough balance in payment method '{payment_id}'.")
        
        if user_payment_method.get("source") == "gift_card":
            user_payment_method["amount"] -= amount
        elif user_payment_method.get("source") == "certificate":
            del user["payment_methods"][payment_id]

    reservations[reservation_id] = reservation
    user.get("reservations", []).append(reservation_id)
    return reservation