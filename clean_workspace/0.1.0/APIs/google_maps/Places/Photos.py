# google_maps/Places/Photos.py
from typing import Optional, List, Dict, Any

from google_maps.SimulationEngine.db import DB
import re


def getMedia(name: str, maxWidthPx: Optional[int] = None, maxHeightPx: Optional[int] = None,
             skipHttpRedirect: bool = False) -> List[Dict[str, str]]:
    """
    Retrieves photo media by resource name.

    Args:
        name (str): The resource name of a photo, formatted as
            "places/{place_id}/photos/{photo_reference}/media". (Required)
        maxWidthPx (Optional[int]): The maximum desired photo width (range 1–4800).
        maxHeightPx (Optional[int]): The maximum desired photo height (range 1–4800).
        skipHttpRedirect (bool): If True, skips HTTP redirects and returns JSON data. Defaults to False.

    Returns:
        List[Dict[str, str]]: A list of photo media objects, each containing:
            - photoUri (str): The URL to the photo media.
            - name (str): The full resource name of the photo.

    Raises:
        ValueError: If the resource name does not match the expected format.
        ValueError: If neither maxWidthPx nor maxHeightPx is specified.
    """

    # Validate the resource name pattern.
    pattern = r"^places/[^/]+/photos/[^/]+/media$"
    if not re.match(pattern, name):
        raise ValueError(
            "Resource name must be in the format 'places/{place_id}/photos/{photo_reference}/media'."
        )

    # Ensure at least one dimension is provided.
    if maxWidthPx is None and maxHeightPx is None:
        raise ValueError("At least one of maxWidthPx or maxHeightPx must be specified.")

    # Extract the place_id and photo_reference.
    parts = name.split("/")
    if len(parts) != 5:
        raise ValueError("Invalid resource name format.")
    place_id = parts[1]
    photo_ref = parts[3]

    results = []
    # Search through the static DB.
    place = DB.get(place_id, None)
    if place:
        for photo in place.get("photos", []):
            # Stored photo names are in the format "places/{place_id}/photos/{photo_reference}".
            if photo.get("name") == f"places/{place_id}/photos/{photo_ref}":
                dims = []
                if maxWidthPx is not None:
                    dims.append(f"w{maxWidthPx}")
                if maxHeightPx is not None:
                    dims.append(f"h{maxHeightPx}")
                dims_str = "_".join(dims)
                dummy_photo_uri = f"https://maps.example.com/media/{photo.get('name')}/media?dims={dims_str}"

                results.append({"photoUri": dummy_photo_uri, "name": name})
    return results
