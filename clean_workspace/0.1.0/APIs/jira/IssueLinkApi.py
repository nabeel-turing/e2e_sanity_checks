# APIs/jira/IssueLinkApi.py
from .SimulationEngine.db import DB
from .SimulationEngine.models import IssueLinkCreationInput
from .SimulationEngine.custom_errors import IssueNotFoundError
from typing import Dict, Any
from pydantic import ValidationError


def create_issue_link(type: str, inwardIssue: Dict[str, Any], outwardIssue: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new issue link in Jira.
    This method creates a new issue link between two issues. The link will be
    assigned a unique ID and stored in the system. Both issues must exist in
    the database for the link to be created successfully.

    Args:
        type (str): The type of issue link to create. Must be a non-empty string.
        inwardIssue (Dict[str, Any]): The inward issue reference containing:
            - key (str): The key of the inward issue. Must be a non-empty string.
        outwardIssue (Dict[str, Any]): The outward issue reference containing:
            - key (str): The key of the outward issue. Must be a non-empty string.
    Returns:
        Dict[str, Any]: A dictionary containing the created issue link:
            - created (bool): Always True for successful creation
            - issueLink (Dict[str, Any]): The created issue link containing:
                - id (str): The unique ID of the issue link
                - type (str): The type of issue link
                - inwardIssue (Dict[str, Any]): The inward issue reference
                    - key (str): The key of the inward issue
                - outwardIssue (Dict[str, Any]): The outward issue reference
                    - key (str): The key of the outward issue
    Raises:
        ValidationError: If the input data structure is invalid according to the Pydantic model.
        IssueNotFoundError: If either the inward or outward issue does not exist in the database.
        
    """
    # Input validation using Pydantic model
    try:
        validated_input = IssueLinkCreationInput(
        type=type,
        inwardIssue=inwardIssue,
        outwardIssue=outwardIssue
        )
    except ValidationError as e:
        raise e


    # Check if issues exist in the database
    inward_key = validated_input.inwardIssue.key
    outward_key = validated_input.outwardIssue.key

    if inward_key not in DB.get("issues", {}):
        raise IssueNotFoundError(f"Inward issue with key '{inward_key}' not found in database.")

    if outward_key not in DB.get("issues", {}):
        raise IssueNotFoundError(f"Outward issue with key '{outward_key}' not found in database.")

    # Generate unique link ID
    link_id = f"LINK-{len(DB.get('issue_links', [])) + 1}"

    # Create link data
    link_data = {
        "id": link_id,
        "type": validated_input.type,
        "inwardIssue": {"key": inward_key},
        "outwardIssue": {"key": outward_key},
    }

    # Ensure issue_links collection exists
    if "issue_links" not in DB:
        DB["issue_links"] = []

    # Store the link in the database
    DB["issue_links"].append(link_data)

    return {"created": True, "issueLink": link_data}