# google_maps/SimulationEngine/utils.py
import math
from google_maps.SimulationEngine.db import DB
from typing import Dict, Any
import requests
import json
import os
import re
from typing import Optional, List, Dict, Any, Union
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def _create_place(place_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    A helper function that creates a place entry in the in-memory database.

    Args:
        place_data (dict): A dictionary containing the place data. Must include an "id" key.

    Returns:
        dict: The created place dictionary.

    Raises:
        ValueError: If "id" is missing or if a place with the same ID already exists.
    """
    if "id" not in place_data:
        raise ValueError("Place data must contain an 'id' field.")

    if not DB.get(place_data["id"], None):
        DB[place_data["id"]] = place_data
    else:
        raise ValueError(f"Place with id '{place_data['id']}' already exists.")

    return place_data


def _haversine_distance(lat1, lon1, lat2, lon2):
    """
    A helper function that computes the Haversine distance between two geographic points in meters.

    Args:
        lat1 (float): Latitude of the first point.
        lon1 (float): Longitude of the first point.
        lat2 (float): Latitude of the second point.
        lon2 (float): Longitude of the second point.

    Returns:
        float: The distance in meters between the two points.
    """
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c