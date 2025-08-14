"""
This module provides functionality for managing projects using their external identifiers
in the Workday Strategic Sourcing system.
"""

from typing import Dict, Optional

from .SimulationEngine import db

def get(external_id: str) -> Optional[Dict]:
    """
    Retrieves the details of a specific project using its external identifier.

    Args:
        external_id (str): The unique external identifier of the project to retrieve.

    Returns:
        Optional[Dict]: A dictionary containing the project details if found,
                       None if no project exists with the given external ID.
                       The project details will be returned with any of the following keys:
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
    """
    for project in db.DB["projects"]["projects"].values():
        if project.get("external_id") == external_id:
            return project
    return None

def patch(external_id: str, project_data: Dict) -> Optional[Dict]:
    """
    Updates the details of an existing project using its external identifier.

    Args:
        external_id (str): The unique external identifier of the project to update.
        project_data (Dict): A dictionary containing the updated project details.
                            Must include an 'external_id' field matching the provided ID.
                            - type_id (str): Object type
                            - id (str): Project identifier string
                            - external_id (str): Project external identifier string. Same as the provided ID.
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

    Returns:
        Optional[Dict]: The updated project details if successful,
                       None if the project doesn't exist or the external IDs don't match.
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
    """
    if external_id != project_data.get("external_id"):
        return None
    for id, project in db.DB["projects"]["projects"].items():
        if project.get("external_id") == external_id:
            db.DB["projects"]["projects"][id].update(project_data)
            return db.DB["projects"]["projects"][id]
    return None

def delete(external_id: str) -> bool:
    """
    Deletes a project using its external identifier.

    Args:
        external_id (str): The unique external identifier of the project to delete.

    Returns:
        bool: True if the project was successfully deleted,
              False if no project exists with the given external ID.
    """
    for id, project in db.DB["projects"]["projects"].items():
        if project.get("external_id") == external_id:
            del db.DB["projects"]["projects"][id]
            return True
    return False