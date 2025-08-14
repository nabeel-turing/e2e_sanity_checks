from typing import Dict, List, Optional, Union, Any
from youtube.SimulationEngine.db import DB
from youtube.SimulationEngine.utils import generate_random_string, generate_entity_id

"""
    Handles YouTube Video Categories API operations.
    
    This class provides methods to retrieve information about video categories,
    which are used to organize videos on YouTube.
"""


def list(
    part: str,
    hl: Optional[str] = None,
    id: Optional[str] = None,
    region_code: Optional[str] = None,
    max_results: Optional[int] = None,
) -> Dict[str, Union[List[Dict[str, Any]], str]]:
    """
    Retrieves a list of video categories with optional filters.

    Args:
        part (str): The part parameter specifies the videoCategory resource properties that the API response will include.
        hl (Optional[str]): The hl parameter instructs the API to retrieve localized resource metadata for a specific application language that the YouTube website supports. Currently unused!
        id (Optional[str]): The id parameter identifies the video category that is being retrieved.
        region_code (Optional[str]): The regionCode parameter instructs the API to select a video category available in the specified region.
        max_results (Optional[int]): The maximum number of items that should be returned in the result set.

    Returns:
        Dict[str, Union[List[Dict[str, Any]], str]]: A dictionary containing the video category data or an error message. It can contain the following keys:
            - If part is valid:
                - items (List[Dict[str, Union[str, Dict[str, str]]]]): A list of video category resources, each containing:
                    - id (str): The ID of the video category.
                    - snippet (Dict[str, str]): Metadata for the category, including:
                        - title (str): Name of the video category.
                        - regionCode (str): The region where the category is available.
            - If part is invalid:   
                - error (str): An error message indicating that the `part` parameter is invalid (e.g., "Invalid part parameter").
    """
    if not isinstance(part, str) or part != "snippet":
        return {"error": "Invalid part parameter"}

    categories = DB["videoCategories"]
    result_categories = list(categories.values())

    if id:
        result_categories = [
            category for category in result_categories if category["id"] == id
        ]

    if region_code:
        result_categories = [
            category
            for category in result_categories
            if category.get("snippet", {}).get("regionCode") == region_code
        ]

    if max_results:
        result_categories = result_categories[: min(max_results, 50)]

    return {"items": result_categories}
