"""
This module provides functionality for managing projects using their unique internal identifiers
in the Workday Strategic Sourcing system.
"""

from typing import Dict, Optional
from pydantic import ValidationError
from .SimulationEngine import db
from .SimulationEngine.custom_errors import ProjectIDMismatchError
from .SimulationEngine.pydantic_models import ProjectDataInputModel
def get(id: int) -> Optional[Dict]:
    """
    Retrieves the details of a specific project using its unique internal identifier.

    Args:
        id (int): The unique internal identifier of the project to retrieve.

    Returns:
        Optional[Dict]: A dictionary containing the project details if found,
                       None if no project exists with the given ID.
                       The project details will be returned with any of the following keys:
                        - type_id (str): Object type
                        - id (str): Project identifier string
                        - external_id (str): Project external identifier string
                        - supplier_companies (List): Array of supplier company objects
                        - supplier_contacts (List): Array of supplier contact objects
                        - status (str): Project status
                        - attributes (Dict[str, Union[str, float, bool, datetime.date, None]]): Project attributes object containing:
                            - name (str): Project name
                            - description (str): Project description
                            - state (str): Project state (draft, requested, planned, active, completed, canceled, on_hold)
                            - target_start_date (datetime.date): Project target start date
                            - target_end_date (datetime.date): Project target end date
                            - actual_spend_amount (float): Project actual spend amount
                            - approved_spend_amount (float): Project approved spend amount
                            - estimated_savings_amount (float): Project estimated savings amount
                            - estimated_spend_amount (float): Project estimated spend amount
                            - canceled_note (Optional[str]): Project cancelation note
                            - canceled_reason (Optional[str]): Project cancelation reason
                            - on_hold_note (Optional[str]): Project on-hold note
                            - on_hold_reason (Optional[str]): Project on-hold reason
                            - needs_attention (bool): Project needs attention status
                            - marked_as_needs_attention_at (Optional[datetime.datetime]): Project marked as needs attention timestamp
                            - needs_attention_note (Optional[str]): Project needs attention note
                            - needs_attention_reason (Optional[str]): Project needs attention reason
                        - relationships (Dict[str, Union[List[Dict], Dict]]): Project relationships object containing:
                            - attachments (List[Dict]): Array of attachment objects
                            - creator (Dict): Project creator stakeholder object
                            - requester (Dict): Project requester stakeholder object
                            - owner (Dict): Project owner stakeholder object
                            - project_type (Dict): Project type object
                        - links (Dict[str, str]): Resource links object containing:
                            - self (str): Normalized link to the resource
    """
    return db.DB["projects"]["projects"].get(str(id))

def patch(id: int, project_data: Dict) -> Optional[Dict]:
    """
    Updates the details of an existing project using its unique internal identifier.

    Args:
        id (int): The unique internal identifier of the project to update.
        project_data (Dict): A dictionary containing the updated project details.
                            Validated against ProjectDataInputModel.
                            Must include an 'id' field whose string representation matches the provided path ID.
                            - type_id (Optional[str]): Object type
                            - id (str): Project identifier string.
                            - external_id (Optional[str]): Project external identifier string
                            - supplier_companies (Optional[List[Dict[str, Any]]]): Array of supplier company objects
                            - supplier_contacts (Optional[List[Dict[str, Any]]]): Array of supplier contact objects
                            - status (Optional[str]): Project status
                            - attributes (Optional[ProjectAttributesInputModel]): Project attributes object.
                            - relationships (Optional[ProjectRelationshipsInputModel]): Project relationships object.

    Returns:
        Optional[Dict]: The updated project details if successful,
                       None if the project doesn't exist.
                       The updated project details will be returned with any of the following keys:
                        - type_id (str): Object type
                        - id (str): Project identifier string.
                        - external_id (str): Project external identifier string
                        - supplier_companies (List): Array of supplier company objects
                        - supplier_contacts (List): Array of supplier contact objects
                        - status (str): Project status
                        - attributes (Dict[str, Union[str, float, bool, datetime.date, None]]): Project attributes object containing:
                            - name (str): Project name
                            - description (str): Project description
                            - state (str): Project state (draft, requested, planned, active, completed, canceled, on_hold)
                            - target_start_date (datetime.date): Project target start date
                            - target_end_date (datetime.date): Project target end date
                            - actual_spend_amount (float): Project actual spend amount
                            - approved_spend_amount (float): Project approved spend amount
                            - estimated_savings_amount (float): Project estimated savings amount
                            - estimated_spend_amount (float): Project estimated spend amount
                            - canceled_note (Optional[str]): Project cancelation note
                            - canceled_reason (Optional[str]): Project cancelation reason
                            - on_hold_note (Optional[str]): Project on-hold note
                            - on_hold_reason (Optional[str]): Project on-hold reason
                            - needs_attention (bool): Project needs attention status
                            - marked_as_needs_attention_at (Optional[datetime.datetime]): Project marked as needs attention timestamp
                            - needs_attention_note (Optional[str]): Project needs attention note
                            - needs_attention_reason (Optional[str]): Project needs attention reason
                        - relationships (Dict[str, Union[List[Dict], Dict]]): Project relationships object containing:
                            - attachments (List[Dict]): Array of attachment objects
                            - creator (Dict): Project creator stakeholder object
                            - requester (Dict): Project requester stakeholder object
                            - owner (Dict): Project owner stakeholder object
                            - project_type (Dict): Project type object
                        - links (Dict[str, str]): Resource links object containing:
                            - self (str): Normalized link to the resource

    Raises:
        TypeError: If 'id' is not an integer.
        pydantic.ValidationError: If 'project_data' does not conform to the ProjectDataInputModel structure.
        ProjectIDMismatchError: If the 'id' in 'project_data' does not match the 'id' provided in the path.
    """
    # Standard type validation for non-dictionary arguments
    if not isinstance(id, int):
        raise TypeError(f"id must be an integer, got {type(id).__name__}")

    # Pydantic validation for dictionary arguments
    try:
        validated_project_data = ProjectDataInputModel(**project_data)
    except ValidationError as e:
        # Re-raise Pydantic's ValidationError.
        # It contains detailed information about the validation failure.
        raise e

    if str(id) != validated_project_data.id:
        raise ProjectIDMismatchError(f"Path ID '{id}' does not match project_data ID '{validated_project_data.id}'")

    if str(id) in db.DB["projects"]["projects"]:
        # Here, using validated_project_data.model_dump() ensures we use the validated & potentially transformed data.
        db.DB["projects"]["projects"][str(id)].update(validated_project_data.model_dump())
        return db.DB["projects"]["projects"][str(id)]
    
    return None

def delete(id: int) -> bool:
    """
    Deletes a project using its unique internal identifier.

    Args:
        id (int): The unique internal identifier of the project to delete.

    Returns:
        bool: True if the project was successfully deleted,
              False if no project exists with the given ID.
    """
    if str(id) in db.DB["projects"]["projects"]:
        del db.DB["projects"]["projects"][str(id)]
        return True
    return False 