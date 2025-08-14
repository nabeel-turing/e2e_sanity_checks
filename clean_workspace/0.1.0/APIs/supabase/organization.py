"""Defines Supabase organization-related functions."""

from typing import List, Dict, Any

from .SimulationEngine.db import DB
from .SimulationEngine import models
from .SimulationEngine import utils
from .SimulationEngine import custom_errors
from pydantic import ValidationError as PydanticValidationError


def list_organizations() -> List[Dict[str, str]]:
    """Lists all organizations that the user is a member of.

    This function retrieves a list of all organizations of which the user is a member.

    Returns:
        List[Dict[str, str]]: A list of dictionaries,
            where each dictionary represents an organization the user is a member of.
            Each organization dictionary contains the following keys:
            id (str): The unique identifier for the organization.
            name (str): The name of the organization.
    """
    # Retrieve the list of organization dictionaries from the DB.
    # If 'organizations' key is not found in DB, default to an empty list.
    organizations_from_db: List[Dict[str, Any]] = DB.get('organizations', [])

    result_org_list: List[Dict[str, Any]] = []
    for org_in_db in organizations_from_db:
        # Extract only the required fields from each organization dictionary
        result_org_list.append({
            "id": org_in_db["id"],
            "name": org_in_db["name"]
        })

    return result_org_list

def get_organization(id: str) -> Dict[str, Any]:
    """Gets details for an organization. Includes subscription plan.

    Gets details for an organization. Includes subscription plan.

    Args:
        id (str): The organization ID.

    Returns:
        Dict[str, Any]: Organization details including:
            id (str): The unique identifier for the organization.
            name (str): The name of the organization.
            slug (str): The URL-friendly slug of the organization.
            created_at (str): ISO 8601 timestamp of when the organization was created.
            subscription_plan (Dict[str, Any]): Details of the organization's subscription plan. The subscription plan object includes:
                id (str): The ID of the plan.
                name (str): The name of the plan.
                price (float): The price of the plan.
                currency (str): The currency of the price (e.g., 'USD').
                features (List[str]): A list of features included in the plan.

    Raises:
        NotFoundError: If the organization with the specified ID does not exist.
        ValidationError: If input arguments fail validation.
    """
    if not id:
        raise custom_errors.ValidationError('The id parameter can not be null or empty')

    if not isinstance(id, str):
        raise custom_errors.ValidationError('id must be string type')
    
    organizations = utils.get_main_entities(DB, "organizations")
    organization = utils.get_entity_by_id(organizations, id)
    
    if not organization:
        raise custom_errors.NotFoundError(f"No organization found against this id: {id}")
    
    try: 
        organization_details_response = organization.copy()
        organization_details_response["slug"] = utils.name_to_slug(organization["name"])
        organization_details_response = models.OrganizationDetailsResponse(**organization_details_response).model_dump()
    except PydanticValidationError as e: 
        raise custom_errors.ValidationError(f"Invalid Structure for return data: {e}")
    
    return organization_details_response
