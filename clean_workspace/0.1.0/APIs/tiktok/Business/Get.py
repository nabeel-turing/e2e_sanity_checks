# APIs/tiktokApi/Business/Get/__init__.py

from typing import Any, Dict, Optional, List
from tiktok.SimulationEngine.db import DB
import datetime


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
            - data (Dict[str, Any]): The requested profile data, filtered by date range and fields if specified
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
    if not access_token:
        return {"code": 400, "message": "Access-Token is required", "data": None}
    if not business_id:
        return {"code": 400, "message": "business_id is required", "data": None}

    # Simulate data retrieval based on business_id
    account_data = DB.get(business_id)
    if not account_data:
        return {"code": 404, "message": "Account not found", "data": None}

    # Apply date filtering if start_date and end_date are provided
    filtered_data = account_data.copy()  # Create a copy to avoid modifying the original

    if start_date:
        try:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            #  Date filtering logic would go here (if needed)
        except ValueError:
            return {"code": 400, "message": "Invalid start_date format", "data": None}

    if end_date:
        try:
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
            #  Date filtering logic would go here (if needed)
        except ValueError:
            return {"code": 400, "message": "Invalid end_date format", "data": None}

    # Apply fields filtering if fields are provided
    if fields:
        filtered_data = {
            field: filtered_data.get(field)
            for field in fields
            if field in filtered_data
        }

    return {"code": 200, "message": "OK", "data": filtered_data}
