"""
Utility functions for the Airline Service.
"""

from typing import Dict, List, Optional, Any
from .db import DB, reset_db
from .models import Flight, Reservation, User

def get_flight(flight_number: str) -> Optional[Dict[str, Any]]:
    """Get flight by flight number"""
    return DB.get("flights", {}).get(flight_number)

def get_reservation(reservation_id: str) -> Optional[Dict[str, Any]]:
    """Get reservation by reservation ID"""
    return DB.get("reservations", {}).get(reservation_id)

def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by user ID"""
    return DB.get("users", {}).get(user_id)

def search_flights(origin: str, destination: str, date: str) -> List[Dict[str, Any]]:
    """Search for direct flights."""
    flights = DB.get("flights", {})
    results = []
    for flight in flights.values():
        if flight["origin"] == origin and flight["destination"] == destination:
            if date in flight["dates"] and flight["dates"][date]["status"] == "available":
                flight_info = {k: v for k, v in flight.items() if k != "dates"}
                flight_info.update(flight["dates"][date])
                results.append(flight_info)
    return results

from datetime import datetime, timedelta

def search_onestop_flights(origin: str, destination: str, date: str) -> List[List[Dict[str, Any]]]:
    """Search for one-stop flights."""
    flights = DB.get("flights", {})
    results = []
    for flight1 in flights.values():
        if flight1["origin"] == origin:
            for flight2 in flights.values():
                if (
                    flight2["destination"] == destination
                    and flight1["destination"] == flight2["origin"]
                ):
                    date2 = date
                    if "+1" in flight1.get("scheduled_arrival_time_est", ""):
                        try:
                            current_date = datetime.strptime(date, "%Y-%m-%d")
                            next_day = current_date + timedelta(days=1)
                            date2 = next_day.strftime("%Y-%m-%d")
                        except ValueError:
                            # If date format is invalid, skip this flight pair
                            continue
                    
                    if (
                        flight1.get("scheduled_arrival_time_est", "").split("+")[0]
                        > flight2.get("scheduled_departure_time_est", "")
                    ):
                        continue
                    
                    flight1_date_data = flight1.get("dates", {}).get(date)
                    flight2_date_data = flight2.get("dates", {}).get(date2)

                    if (
                        flight1_date_data and flight1_date_data.get("status") == "available"
                        and flight2_date_data and flight2_date_data.get("status") == "available"
                    ):
                        result1 = {
                            k: v for k, v in flight1.items() if k != "dates"
                        }
                        result1.update(flight1_date_data)
                        result1["date"] = date
                        result2 = {
                            k: v for k, v in flight2.items() if k != "dates"
                        }
                        result2.update(flight2_date_data)
                        result2["date"] = date2
                        results.append([result1, result2])
    return results


def create_user(
    user_id: str,
    first_name: str,
    last_name: str,
    email: str,
    dob: str,
    membership: Optional[str] = None,
    address: Optional[Dict[str, str]] = None,
    saved_passengers: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Create a new user with detailed information and add it to the database.

    Args:
        user_id (str): The unique identifier for the user.
        first_name (str): The user's first name.
        last_name (str): The user's last name.
        email (str): The user's email address.
        dob (str): The user's date of birth in "YYYY-MM-DD" format.
        membership (Optional[str]): The user's membership status (e.g., "gold").
        address (Optional[Dict[str, str]]): A dictionary containing the user's
            address with keys like "address1", "city", "state", "zip", "country".
        saved_passengers (Optional[List[Dict[str, Any]]]): A list of pre-saved
            passenger details.

    Returns:
        Dict[str, Any]: The newly created user object.
    """
    users = DB.get("users", {})
    if user_id in users:
        raise ValueError(f"User with ID '{user_id}' already exists.")
    
    new_user = {
        "user_id": user_id,
        "name": f"{first_name} {last_name}",
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "dob": dob,
        "membership": membership,
        "address": address or {},
        "saved_passengers": saved_passengers or [],
        "payment_methods": {},
        "reservations": []
    }
    users[user_id] = new_user
    return new_user


def add_flight(
    flight_number: str, 
    origin: str, 
    destination: str, 
    departure_time: str, 
    arrival_time: str, 
    dates: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """Adds a new flight to the database.

    Args:
        flight_number (str): The unique identifier for the flight (e.g., "UA101").
        origin (str): The IATA code for the origin airport (e.g., "SFO").
        destination (str): The IATA code for the destination airport (e.g., "JFK").
        departure_time (str): The scheduled departure time in "HH:MM" format.
        arrival_time (str): The scheduled arrival time in "HH:MM" format.
        dates (Dict[str, Dict[str, Any]]): A dictionary where keys are dates in
            "YYYY-MM-DD" format and values are details for that date.
            Example:
            {
                "2024-01-01": {
                    "status": "available",
                    "prices": {"economy": 250, "business": 800, "first": 1500},
                    "available_seats": {"economy": 100, "business": 30, "first": 10}
                }
            }

    Returns:
        Dict[str, Any]: The newly created flight object.
    """
    flights = DB.get("flights", {})
    if flight_number in flights:
        raise ValueError(f"Flight with number '{flight_number}' already exists.")
    
    new_flight = {
        "flight_number": flight_number,
        "origin": origin,
        "destination": destination,
        "scheduled_departure_time_est": departure_time,
        "scheduled_arrival_time_est": arrival_time,
        "dates": dates
    }
    flights[flight_number] = new_flight
    return new_flight


def add_payment_method_to_user(
    user_id: str,
    payment_id: str,
    source: str,
    details: Dict[str, Any],
) -> Dict[str, Any]:
    """Adds a payment method to a user.

    Args:
        user_id (str): The ID of the user to add the payment method to.
        payment_id (str): The unique ID for the new payment method.
        source (str): The source of the payment method (e.g., "credit_card", "gift_card").
        details (Dict[str, Any]): A dictionary of details for the payment method.
            - For "credit_card": {"brand": str, "last_four": str}
            - For "gift_card" or "certificate": {"amount": int}

    Returns:
        Dict[str, Any]: The updated user object.
    """
    users = DB.get("users", {})
    user = users.get(user_id)
    if not user:
        raise ValueError(f"User with ID '{user_id}' not found.")
    
    if "payment_methods" not in user:
        user["payment_methods"] = {}
        
    if payment_id in user["payment_methods"]:
        raise ValueError(f"Payment method '{payment_id}' already exists for user '{user_id}'.")

    payment_method: Dict[str, Any] = {"id": payment_id, "source": source}
    payment_method.update(details)
    
    user["payment_methods"][payment_id] = payment_method
    return user
