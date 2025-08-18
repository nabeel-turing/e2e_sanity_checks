# APIs/tiktokApi/Business/Get/__init__.py

from typing import Any, Dict, Optional, List
from tiktok.SimulationEngine.db import DB
import datetime
from typing import Optional, List, Dict, Any


def get(
    access_token: str,
    business_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    fields: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Get profile data of a TikTok account, including analytics and insights.

    Args:
        access_token (str): Access token authorized by TikTok creators.
        business_id (str): Application specific unique identifier for the TikTok account.
        start_date (Optional[str]): Query start date in YYYY-MM-DD format. Defaults to None.
        end_date (Optional[str]): Query end date in YYYY-MM-DD format. Defaults to None.
        fields (Optional[List[str]]): List of requested fields to include in the response. Defaults to None.
            - username
            - display_name
            - profile
            - analytics
            - settings

    Returns:
        Dict[str, Any]: A dictionary containing:
            - code (int): HTTP status code (200 for success, 400 for bad request, 404 for not found)
            - message (str): Status message describing the result
            - data (Dict[str, Any]): The requested profile data, filtered by fields if specified
                - username (str): The username of the TikTok account
                - display_name (str): The display name of the TikTok account
                - profile (Dict[str, Any]): The profile data of the TikTok account
                    - bio (str): The bio of the TikTok account
                    - followers_count (int): The number of followers of the TikTok account
                    - following_count (int): The number of following of the TikTok account
                    - website (str): The website of the TikTok account
                - analytics (Dict[str, Any]): The analytics data of the TikTok account
                    - total_likes (int): The total number of likes of the TikTok account
                    - total_views (int): The total number of views of the TikTok account
                    - engagement_rate (float): The engagement rate of the TikTok account
                - settings (Dict[str, Any]): The settings of the TikTok account
                    - notifications_enabled (bool): Whether the notifications are enabled for the TikTok account
                    - ads_enabled (bool): Whether the ads are enabled for the TikTok account
                    - language (str): The language of the TikTok account

    """
    # Valid fields that can be requested
    valid_fields = {"username", "display_name", "profile", "analytics", "settings"}

    # Input validation
    if not access_token or not isinstance(access_token, str):
        return {
            "code": 400,
            "message": "Access-Token is required and must be a string",
            "data": None,
        }

    if not business_id or not isinstance(business_id, str):
        return {
            "code": 400,
            "message": "business_id is required and must be a string",
            "data": None,
        }

    # Validate fields parameter
    if fields is not None:
        if not isinstance(fields, list):
            return {"code": 400, "message": "fields must be a list", "data": None}

        # Check if all fields are strings and valid
        for field in fields:
            if not isinstance(field, str):
                return {
                    "code": 400,
                    "message": "All fields must be strings",
                    "data": None,
                }
            if field not in valid_fields:
                return {
                    "code": 400,
                    "message": f"Invalid field '{field}'. Valid fields are: {', '.join(valid_fields)}",
                    "data": None,
                }

    # Parse and validate date parameters
    parsed_start_date = None
    parsed_end_date = None

    if start_date:
        if not isinstance(start_date, str):
            return {"code": 400, "message": "start_date must be a string", "data": None}
        try:
            parsed_start_date = datetime.datetime.strptime(
                start_date, "%Y-%m-%d"
            ).date()
        except ValueError:
            return {
                "code": 400,
                "message": "Invalid start_date format. Use YYYY-MM-DD",
                "data": None,
            }

    if end_date:
        if not isinstance(end_date, str):
            return {"code": 400, "message": "end_date must be a string", "data": None}
        try:
            parsed_end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            return {
                "code": 400,
                "message": "Invalid end_date format. Use YYYY-MM-DD",
                "data": None,
            }

    # Validate date range
    if parsed_start_date and parsed_end_date and parsed_start_date > parsed_end_date:
        return {
            "code": 400,
            "message": "start_date cannot be after end_date",
            "data": None,
        }

    # Simulate data retrieval based on business_id
    account_data = DB.get(business_id)
    if not account_data:
        return {"code": 404, "message": "Account not found", "data": None}

    filtered_data = account_data.copy()  # Create a copy to avoid modifying the original

    # Apply fields filtering if fields are provided
    if fields is not None:
        filtered_data = {
            field: filtered_data.get(field)
            for field in fields
            if field in filtered_data
        }

    return {"code": 200, "message": "OK", "data": filtered_data}
