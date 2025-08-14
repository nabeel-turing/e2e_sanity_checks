from datetime import datetime
from typing import List, Dict, Optional, Union, Any
from pydantic import BaseModel, Field, validator
from enum import Enum
import uuid

# ---------------------------
# Enum Types
# ---------------------------

class FlightStatus(str, Enum):
    LANDED = "landed"
    CANCELLED = "cancelled"
    AVAILABLE = "available"
    DELAYED = "delayed"
    FLYING = "flying"
    ON_TIME = "on time"

class CabinType(str, Enum):
    BASIC_ECONOMY = "basic_economy"
    ECONOMY = "economy"
    BUSINESS = "business"

class FlightType(str, Enum):
    ONE_WAY = "one_way"
    ROUND_TRIP = "round_trip"

class PaymentSource(str, Enum):
    CREDIT_CARD = "credit_card"
    GIFT_CARD = "gift_card"
    CERTIFICATE = "certificate"

class Membership(str, Enum):
    GOLD = "gold"
    SILVER = "silver"
    REGULAR = "regular"

# ---------------------------
# Core API Models
# ---------------------------

class SeatInfo(BaseModel):
    basic_economy: int
    economy: int
    business: int

class FlightDateDetails(BaseModel):
    status: FlightStatus
    actual_departure_time_est: Optional[str] = None
    actual_arrival_time_est: Optional[str] = None
    estimated_departure_time_est: Optional[str] = None
    estimated_arrival_time_est: Optional[str] = None
    available_seats: Optional[SeatInfo] = None
    prices: Optional[SeatInfo] = None

class Flight(BaseModel):
    flight_number: str
    origin: str
    destination: str
    scheduled_departure_time_est: str
    scheduled_arrival_time_est: str
    dates: Dict[str, FlightDateDetails]

class Passenger(BaseModel):
    first_name: str
    last_name: str
    dob: str

class FlightInReservation(BaseModel):
    origin: str
    destination: str
    flight_number: str
    date: str
    price: int

class PaymentMethodInReservation(BaseModel):
    payment_id: str
    amount: float

class Reservation(BaseModel):
    reservation_id: str
    user_id: str
    origin: str
    destination: str
    flight_type: FlightType
    cabin: CabinType
    flights: List[FlightInReservation]
    passengers: List[Passenger]
    payment_history: List[PaymentMethodInReservation]
    created_at: str
    total_baggages: int
    nonfree_baggages: int
    insurance: str
    status: Optional[str] = None

class PaymentMethod(BaseModel):
    source: PaymentSource
    brand: Optional[str] = None
    last_four: Optional[str] = None
    id: str
    amount: Optional[int] = None

class User(BaseModel):
    name: Dict[str, str]
    address: Dict[str, str]
    email: str
    dob: str
    payment_methods: Dict[str, PaymentMethod]
    saved_passengers: List[Passenger]
    membership: Membership
    reservations: List[str]

# ---------------------------
# Root Database Model
# ---------------------------

class AirlineDB(BaseModel):
    """Validates entire database structure"""
    flights: Dict[str, Flight]
    reservations: Dict[str, Reservation]
    users: Dict[str, User]

    class Config:
        str_strip_whitespace = True
