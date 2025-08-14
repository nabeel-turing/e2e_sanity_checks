# APIs/hubspot/Campaigns.py
from typing import Optional, Dict, Any
import uuid
from hubspot.SimulationEngine.db import DB


def get_campaigns(
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    created_at: Optional[str] = None,
    created_at__gt: Optional[str] = None,
    created_at__gte: Optional[str] = None,
    created_at__lt: Optional[str] = None,
    created_at__lte: Optional[str] = None,
    updated_at: Optional[str] = None,
    updated_at__gt: Optional[str] = None,
    updated_at__gte: Optional[str] = None,
    updated_at__lt: Optional[str] = None,
    updated_at__lte: Optional[str] = None,
    name: Optional[str] = None,
    name__contains: Optional[str] = None,
    name__icontains: Optional[str] = None,
    name__ne: Optional[str] = None,
    id: Optional[str] = None,
    id__ne: Optional[str] = None,
    type: Optional[str] = None,
    type__ne: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Returns a list of marketing campaigns (Basic implementation).

    Args:
        limit(Optional[int]): The maximum number of campaigns to return.
        offset(Optional[int]): The number of campaigns to skip.
        created_at(Optional[str]): Filter campaigns by creation date.
        created_at__gt(Optional[str]): Filter campaigns by creation date greater than a specific date.
        created_at__gte(Optional[str]): Filter campaigns by creation date greater than or equal to a specific date.
        created_at__lt(Optional[str]): Filter campaigns by creation date less than a specific date.
        created_at__lte(Optional[str]): Filter campaigns by creation date less than or equal to a specific date.
        updated_at(Optional[str]): Filter campaigns by update date.
        updated_at__gt(Optional[str]): Filter campaigns by update date greater than a specific date.
        updated_at__gte(Optional[str]): Filter campaigns by update date greater than or equal to a specific date.
        updated_at__lt(Optional[str]): Filter campaigns by update date less than a specific date.
        updated_at__lte(Optional[str]): Filter campaigns by update date less than or equal to a specific date.
        name(Optional[str]): Filter campaigns by name.
        name__contains(Optional[str]): Filter campaigns by name containing a specific string.
        name__icontains(Optional[str]): Filter campaigns by name containing a specific string (case insensitive).
        name__ne(Optional[str]): Filter campaigns by name not equal to a specific string.
        id(Optional[str]): Filter campaigns by id.
        id__ne(Optional[str]): Filter campaigns by id not equal to a specific string.
        type(Optional[str]): Filter campaigns by type.
        type__ne(Optional[str]): Filter campaigns by type not equal to a specific string.

    Returns:
        Dict[str, Any]: A dictionary containing the following keys:
        - results(List[Dict[str, Any]]): A list of campaigns matching the filter criteria.
            - id(str): The id of the campaign.
            - name(str): The name of the campaign.
            - type(str): The type of the campaign.
            - start_date(str): The start date of the campaign.
            - end_date(str): The end date of the campaign.
            - status(str): The status of the campaign.
            - budget(float): The budget of the campaign.
            - target_audience(str): The target audience of the campaign.
            - utm_campaign(str): The utm campaign of the campaign.
            - slug(str): The slug of the campaign.
            - description(str): The description of the campaign.
            - start_year(int): The start year of the campaign.
            - start_month(int): The start month of the campaign.
            - start_day(int): The start day of the campaign.
            - end_year(int): The end year of the campaign.
            - end_month(int): The end month of the campaign.
            - end_day(int): The end day of the campaign.
            - theme(str): The theme of the campaign.
            - resource(str): The resource of the campaign.
            - color_label(str): The color label of the campaign.
            - total(int): The total number of campaigns matching the filter criteria.
            - limit(int): The maximum number of campaigns to return.
            - offset(int): The number of campaigns to skip.
    """

    campaigns_list = list(DB["campaigns"].values())

    # Very basic filtering (only id, name, and type for simplicity)
    if id:
        campaigns_list = [c for c in campaigns_list if c.get("id") == id]
    if name:
        campaigns_list = [c for c in campaigns_list if c.get("name") == name]
    if type:
        campaigns_list = [c for c in campaigns_list if c.get("type") == type]

    # Very basic pagination
    total_count = len(campaigns_list)
    if offset is not None:
        campaigns_list = campaigns_list[offset:]
    if limit is not None:
        campaigns_list = campaigns_list[:limit]

    return {
        "results": campaigns_list,
        "total": total_count,
        "limit": limit,
        "offset": offset,
    }


def create_campaign(
    name: str,
    slug: Optional[str] = None,
    description: Optional[str] = None,
    start_year: Optional[int] = None,
    start_month: Optional[int] = None,
    start_day: Optional[int] = None,
    end_year: Optional[int] = None,
    end_month: Optional[int] = None,
    end_day: Optional[int] = None,
    theme: Optional[str] = None,
    resource: Optional[str] = None,
    color_label: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Creates a new campaign.

    Args:
        name(str): The name of the campaign.
        slug(Optional[str]): The slug of the campaign.
        description(Optional[str]): The description of the campaign.
        start_year(Optional[int]): The start year of the campaign.
        start_month(Optional[int]): The start month of the campaign.
        start_day(Optional[int]): The start day of the campaign.
        end_year(Optional[int]): The end year of the campaign.
        end_month(Optional[int]): The end month of the campaign.
        end_day(Optional[int]): The end day of the campaign.
        theme(Optional[str]): The theme of the campaign.
        resource(Optional[str]): The resource of the campaign.
        color_label(Optional[str]): The color label of the campaign.

    Returns:
        Dict[str, Any]: A dictionary containing the following keys:
        - id(str): The id of the campaign.
        - name(str): The name of the campaign.
        - type(str): The type of the campaign.
        - slug(str): The slug of the campaign.
        - description(str): The description of the campaign.
        - start_year(int): The start year of the campaign.
        - start_month(int): The start month of the campaign.
        - start_day(int): The start day of the campaign.
        - end_year(int): The end year of the campaign.
        - end_month(int): The end month of the campaign.
        - end_day(int): The end day of the campaign.
        - theme(str): The theme of the campaign.
        - resource(str): The resource of the campaign.
        - color_label(str): The color label of the campaign.

    """
    campaign_id = str(uuid.uuid4())

    if slug is None:
        slug = f"{name.lower().replace(' ', '-')}-{campaign_id}"

    new_campaign = {
        "id": campaign_id,
        "name": name,
        "slug": slug,
        "description": description,
        "start_year": start_year,
        "start_month": start_month,
        "start_day": start_day,
        "end_year": end_year,
        "end_month": end_month,
        "end_day": end_day,
        "theme": theme,
        "resource": resource,
        "color_label": color_label,
        "created_at": campaign_id,
    }
    DB["campaigns"][campaign_id] = new_campaign
    return new_campaign


def get_campaign(campaign_id: int) -> Optional[Dict[str, Any]]:
    """
    Gets a single campaign by its ID.

    Args:
        campaign_id(int): The id of the campaign.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing the following keys if the campaign exists:
        - id(str): The id of the campaign.
        - name(str): The name of the campaign.
        - type(str): The type of the campaign.
        - start_date(str): The start date of the campaign.
        - end_date(str): The end date of the campaign.
        - status(str): The status of the campaign.
        - budget(float): The budget of the campaign.
        - target_audience(str): The target audience of the campaign.
        - utm_campaign(str): The utm campaign of the campaign.
        - slug(str): The slug of the campaign.
        - description(str): The description of the campaign.
        - start_year(int): The start year of the campaign.
        - start_month(int): The start month of the campaign.
        - start_day(int): The start day of the campaign.
        - end_year(int): The end year of the campaign.
        - end_month(int): The end month of the campaign.
        - end_day(int): The end day of the campaign.
        - theme(str): The theme of the campaign.
        - resource(str): The resource of the campaign.
        - color_label(str): The color label of the campaign.
    """
    return DB["campaigns"].get(campaign_id)


def update_campaign(
    campaign_id: int,
    name: Optional[str] = None,
    slug: Optional[str] = None,
    description: Optional[str] = None,
    start_year: Optional[int] = None,
    start_month: Optional[int] = None,
    start_day: Optional[int] = None,
    end_year: Optional[int] = None,
    end_month: Optional[int] = None,
    end_day: Optional[int] = None,
    theme: Optional[str] = None,
    resource: Optional[str] = None,
    color_label: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Updates a campaign.

    Args:
        campaign_id(int): The id of the campaign.
        name(Optional[str]): The name of the campaign.
        slug(Optional[str]): The slug of the campaign.
        description(Optional[str]): The description of the campaign.
        start_year(Optional[int]): The start year of the campaign.
        start_month(Optional[int]): The start month of the campaign.
        start_day(Optional[int]): The start day of the campaign.
        end_year(Optional[int]): The end year of the campaign.
        end_month(Optional[int]): The end month of the campaign.
        end_day(Optional[int]): The end day of the campaign.
        theme(Optional[str]): The theme of the campaign.
        resource(Optional[str]): The resource of the campaign.
        color_label(Optional[str]): The color label of the campaign.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing the following keys if the campaign exists:
        - id(str): The id of the campaign.
        - name(str): The name of the campaign.
        - type(str): The type of the campaign.
        - slug(str): The slug of the campaign.
        - description(str): The description of the campaign.
        - start_year(int): The start year of the campaign.
        - start_month(int): The start month of the campaign.
        - start_day(int): The start day of the campaign.
        - end_year(int): The end year of the campaign.
        - end_month(int): The end month of the campaign.
        - end_day(int): The end day of the campaign.
        - theme(str): The theme of the campaign.
        - resource(str): The resource of the campaign.
        - color_label(str): The color label of the campaign.

    """
    if campaign_id not in DB["campaigns"]:
        return None
    campaign = DB["campaigns"].get(campaign_id)
    if name is not None:
        campaign["name"] = name
    if slug is not None:
        campaign["slug"] = slug
    if description is not None:
        campaign["description"] = description
    if start_year is not None:
        campaign["start_year"] = start_year
    if start_month is not None:
        campaign["start_month"] = start_month
    if start_day is not None:
        campaign["start_day"] = start_day
    if end_year is not None:
        campaign["end_year"] = end_year
    if end_month is not None:
        campaign["end_month"] = end_month
    if end_day is not None:
        campaign["end_day"] = end_day
    if theme is not None:
        campaign["theme"] = theme
    if resource is not None:
        campaign["resource"] = resource
    if color_label is not None:
        campaign["color_label"] = color_label
    DB["campaigns"][campaign_id] = campaign
    return campaign


def archive_campaign(campaign_id: int) -> bool:
    """
    Archives a campaign. Archived campaigns aren't included in the results when listing campaigns.

    Args:
        campaign_id(int): The id of the campaign.

    Returns:
        bool: True if the campaign was archived, False otherwise.
    """
    if campaign_id in DB["campaigns"]:
        DB["campaigns"][campaign_id]["is_archived"] = True
        return True
    return False
