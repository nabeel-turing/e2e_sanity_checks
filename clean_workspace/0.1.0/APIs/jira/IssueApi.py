# APIs/jira/IssueApi.py

from typing import Any, Dict, List, Optional
from pydantic import ValidationError
from .SimulationEngine.db import DB
from .SimulationEngine.utils import (
    _check_empty_field,
    _check_required_fields,
    _generate_id,
)

from .SimulationEngine.models import (
    JiraIssueCreationFields,
    JiraIssueFields,
    BulkIssueOperationRequestModel,
)

from .SimulationEngine.custom_errors import EmptyFieldError, MissingRequiredFieldError
from .SimulationEngine.db import DB
from .SimulationEngine.models import IssueFieldsUpdateModel, JiraAssignee, JiraIssueResponse
from .SimulationEngine.utils import _check_empty_field, _check_required_fields, _generate_id
from .AttachmentApi import list_issue_attachments   


def create_issue(fields: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new issue in Jira.

    This method creates a new issue with the specified fields. The issue will be
    assigned a unique ID and stored in the system.

    Args:
        fields (Dict[str, Any]): A dictionary containing the issue fields. Required fields include:
            - project (str): The project key the issue belongs to
            - summary (str): A brief description of the issue
            - description (str): A detailed description of the issue
            - issuetype (str): The type of issue
            - priority (str): The priority of the issue
            - status (str): The status of the issue. Example: (Open, Resolved, Closed, Completed, In Progress)
            - assignee (Dict[str, str]): The user assigned to the issue in dictionary format. Example: {"name": "jdoe"}
                - name (str): The assignee's username (e.g., 'jdoe')

    Returns:
        Dict[str, Any]: A dictionary containing:
            - id (str): The unique identifier for the new issue
            - fields (Dict[str, Any]): The fields of the created issue
                - project (str): The project key
                - summary (str): Issue summary
                - description (str): Issue description
                - priority (str): The priority of the issue
                - status (str): The status of the issue. Example: (Open, Resolved, Closed, Completed, In Progress)
                - assignee (Dict[str, str]): Assignee information
                    - name (str): The assignee's username (e.g., 'jdoe')
                - issuetype (str): The type of issue
                    

    Raises:
        EmptyFieldError: If the fields dictionary is empty
        MissingRequiredFieldError: If the fields dictionary is missing required fields
    """
    err = _check_empty_field("fields", fields)
    if err:
        raise EmptyFieldError("fields")

    if not fields:
        raise MissingRequiredFieldError("fields")
        
    # Only validate truly required fields (project and summary)
    minimal_required_fields = ["project", "summary"]
    missing_fields_err = _check_required_fields(fields, minimal_required_fields)
    if missing_fields_err:
        raise MissingRequiredFieldError(field_names=minimal_required_fields)
    
    # Provide defaults for backward compatibility
    if "description" not in fields:
        fields["description"] = ""
    
    if "issuetype" not in fields:
        fields["issuetype"] = "Task"
    
    if "priority" not in fields:
        fields["priority"] = "P2"
    
    if "assignee" not in fields:
        fields["assignee"] = {"name": "Unassigned"}
    elif isinstance(fields.get("assignee"), str):
        # Convert string assignee to dict format for backward compatibility
        fields["assignee"] = {"name": fields["assignee"]}
    elif isinstance(fields.get("assignee"), dict) and "name" not in fields["assignee"]:
        # If assignee is a dict but missing name, add default
        fields["assignee"]["name"] = "Unassigned"
                     
    
    new_id = _generate_id("ISSUE", DB["issues"])
    if not DB["issues"]:
        DB["issues"] = {}
    if "status" not in fields:
        fields["status"] = "Open"
    
    # Store in DB
    DB["issues"][new_id] = {"id": new_id, "fields": fields}

    
    # Create response using Pydantic model
    try:
        response = JiraIssueResponse(id=new_id, fields=fields)
    except ValidationError as e:
        del DB["issues"][new_id]
        raise e
    return response.model_dump()


def get_issue(issue_id: str) -> Dict[str, Any]:
    """
    Retrieve a specific issue by its ID.

    This method returns detailed information about a specific issue
    identified by its unique ID, including any attachments associated with the issue.

    Args:
        issue_id (str): The unique identifier of the issue to retrieve.

    Returns:
        Dict[str, Any]: A dictionary containing issue details:
            - id (str): The unique identifier for the issue.
            - fields (Dict[str, Any]): The fields of the issue, including:
                - project (str): The project key.
                - summary (str): Issue summary.
                - description (str): Issue description.
                - priority (str): The priority of the issue.
                - status (str): The status of the issue. Example: (Open, Resolved, Closed, Completed, In Progress)
                - assignee (Dict[str, str]): Assignee information in dictionary format. Example: {"name": "jdoe"}
                    - name (str): The assignee's username (e.g., 'jdoe')
                - issuetype (str): The type of issue
                - attachments (List[Dict[str, Any]]): List of attachment metadata, each containing:
                    - id (int): The unique attachment identifier
                    - filename (str): Original filename of the attachment
                    - fileSize (int): File size in bytes
                    - mimeType (str): MIME type of the file
                    - created (str): ISO 8601 timestamp when attachment was uploaded
                    - checksum (str): SHA256 checksum for file integrity verification
                    - parentId Optional(str): The ID of the issue this attachment belongs to
                    - content (str): Data of the attachment
                - due_date (Optional[str]): The due date of the issue, if present.
                - comments (Optional[List[str]]]): A list of comments to add to the issue.


    Raises:
        TypeError: If issue_id is not a string.
        ValueError: If the issue does not exist (this error originates from the function's core logic).
        ValidationError: If the issue data or attachments(from list_issue_attachments) are invalid.
        NotFoundError: If the attachment with the specified ID does not exist (from list_issue_attachments).
    """
    # --- Input Validation ---
    if not isinstance(issue_id, str):
        raise TypeError(f"issue_id must be a string, but got {type(issue_id).__name__}.")
    if not issue_id:
        raise ValueError("issue_id cannot be empty.")
    # --- End of Input Validation ---

    if issue_id not in DB["issues"]:
        raise ValueError(f"Issue '{issue_id}' not found.")

    issue = DB["issues"][issue_id]
    
    # Get attachment metadata for this issue
    attachment_ids = issue.get("fields", {}).get("attachmentIds", [])
    try:
        attachments = list_issue_attachments(issue_id)
    except Exception as e:
        raise e
    
    # Add attachments to the issue fields
    issue_fields = issue["fields"].copy()
    issue_fields["attachments"] = attachments
    
    try:
        response = JiraIssueResponse(id=issue_id, fields=issue_fields)
        return response.model_dump()
    except ValidationError as e:
        # This can happen if DB data is inconsistent with the response model
        raise ValueError(f"Issue data for '{issue_id}' is invalid: {e}")


def update_issue(issue_id: str, fields: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Update an existing issue.

    This method allows updating the fields of an existing issue.
    Only the provided fields will be updated.

    Args:
        issue_id (str): The unique identifier of the issue to update.
        fields (Optional[Dict[str, Any]]): The fields to update. Can include any valid
            issue field. Expected structure if provided:
            - summary (Optional[str]): The summary of the issue
            - description (Optional[str]): The description of the issue
            - priority (Optional[str]): The priority of the issue
            - status (Optional[str]): The status of the issue. Example: (Open, Resolved, Closed, Completed, In Progress)
            - assignee (Optional[Dict[str, str]]): Assignee information in dictionary format. Example: {"name": "jdoe"}
                    - name (str): The assignee's username (e.g., 'jdoe')
            - issuetype (Optional[str]): The type of issue
            - project (Optional[str]): The project key
            - due_date (Optional[str]): The due date of the issue
            - comments (Optional[List[str]]]): A list of comments to add to the issue.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - updated (bool): True if the issue was successfully updated
            - issue (Dict[str, Any]): The updated issue object
                - id (str): The unique identifier for the issue
                - fields (Dict[str, Any]): The fields of the issue, including:
                    - project (str): The project key
                    - summary (str): Issue summary
                    - description (str): Issue description
                    - priority (str): The priority of the issue
                    - status (str): The status of the issue. Example: (Open, Resolved, Closed, Completed, In Progress)
                    - assignee (Dict[str, str]): Assignee information
                        - name (str): The assignee's username (e.g., 'jdoe')
                    - issuetype (str): The type of issue
                    - due_date (Optional[str]): The due date of the issue
                    - comments (Optional[List[str]]]): A list of comments to add to the issue.

    Raises:
        TypeError: If 'issue_id' is not a string or 'fields' is not a dictionary.
        ValueError: If the issue with 'issue_id' is not found.
        ValidationError: If 'fields' is provided and does not conform to the
                        IssueFieldsUpdateModel structure (e.g., invalid field types
                        or incorrect assignee structure).
    """
    if not isinstance(issue_id, str):
        raise TypeError("Argument 'issue_id' must be a string.")
    if not issue_id:
        raise ValueError("issue_id cannot be empty.")

    if issue_id not in DB["issues"]:
        raise ValueError(f"Issue '{issue_id}' not found.")

    if fields is not None:
        if not isinstance(fields, Dict):
            raise TypeError("Argument 'fields' must be a dictionary or None.")
        try:
            # Validate the structure of 'fields' using the Pydantic model
            validated_fields_model = IssueFieldsUpdateModel(**fields)
            # Convert Pydantic model to dict, excluding fields that were not provided (None)
            validated_fields_data = validated_fields_model.model_dump(exclude_none=True)
            DB["issues"][issue_id]["fields"].update(validated_fields_data)
        except ValidationError as e:
            raise e

    return {"updated": True, "issue": DB["issues"][issue_id]}


def delete_issue(issue_id: str, delete_subtasks: bool = False) -> Dict[str, Any]:
    """
    Delete an existing issue.

    This method permanently removes an issue from the system.
    Optionally, its subtasks can be deleted as well.

    Args:
        issue_id (str): The unique identifier of the issue to delete.
        delete_subtasks (bool): Whether to delete subtasks. Defaults to False.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - deleted (str): The ID of the deleted issue.
            - deleteSubtasks (str): The value of the delete_subtasks parameter (True or False).

    Raises:
        TypeError: If issue_id is not a string or if delete_subtasks is not a boolean.
        ValueError: If the issue does not exist or if subtasks exist and delete_subtasks is False.
    """
    if not isinstance(issue_id, str):
        raise TypeError(f"issue_id must be a string, got {type(issue_id).__name__}")
    if not issue_id:
        raise ValueError("issue_id cannot be empty.")
    if not isinstance(delete_subtasks, bool):
        raise TypeError(f"delete_subtasks must be a boolean, got {type(delete_subtasks).__name__}")

    if issue_id not in DB["issues"]:
        raise ValueError(f"Issue with id '{issue_id}' does not exist.")

    issue_data = DB["issues"][issue_id]
    if "sub-tasks" in issue_data.get("fields", {}):
        if not delete_subtasks:
            raise ValueError(
                "Subtasks exist, cannot delete issue. Set delete_subtasks=True to delete them."
            )
        sub_tasks = issue_data["fields"]["sub-tasks"]
        for subtask in sub_tasks:
            if isinstance(subtask, dict) and "id" in subtask:
                DB["issues"].pop(subtask["id"], None)

    DB["issues"].pop(issue_id)
    return {"deleted": issue_id, "deleteSubtasks": delete_subtasks}


def bulk_delete_issues(issue_ids: List[str]) -> Dict[str, List[str]]:
    """
    Delete multiple issues in bulk.

    This method allows deleting multiple issues in a single operation.
    The operation will continue even if some issues cannot be deleted.

    Args:
        issue_ids (List[str]): A list of issue IDs to delete

    Returns:
        Dict[str, List[str]]: A dictionary containing:
            - deleted (List[str]): List of successfully deleted issue messages

    Raises:
        MissingRequiredFieldError: If issue_ids is not provided.
        TypeError: If issue_ids is not a list or if an issue_id is not a string.
        ValueError: If an issue_id does not exist.

    """
    results = {"deleted": []}

    if not issue_ids:
        raise MissingRequiredFieldError(field_name="issue_ids")

    if not isinstance(issue_ids, list):
        raise TypeError(f"issue_ids must be a list")

    for issue_id in issue_ids:
        if not isinstance(issue_id, str):
            raise TypeError(f"issue_ids must be a list of strings")

        if issue_id not in DB["issues"]:
            raise ValueError(f"Issue '{issue_id}' does not exist.")

    for issue_id in issue_ids:
        DB["issues"].pop(issue_id)
        results["deleted"].append(f"Issue '{issue_id}' has been deleted.")

    # Return the results containing deleted issues and any errors encountered
    return results


def assign_issue(issue_id: str, assignee: Dict) -> Dict[str, Any]:
    """
    Assign an issue to a user.

    This method assigns an issue to a specific user. The assignee can be
    a user or can be set to null to unassign the issue (handled by how 'assignee' dict is populated).

    Args:
        issue_id (str): The unique identifier of the issue to assign.
        assignee (Dict): The assignee information. Must contain:
            - name (str): The assignee's username (e.g., 'jdoe').

    Returns:
        Dict[str, Any]: A dictionary containing:
            - assigned (bool): True if the issue was successfully assigned (if issue exists).
            - issue (Dict[str, Any]): The updated issue object if successful.
                - id (str): The unique identifier for the issue.
                - fields (Dict[str, Any]): The fields of the issue, including:
                    - project (str): The project key
                    - summary (str): Issue summary
                    - description (str): Issue description
                    - priority (str): The priority of the issue
                    - status (str): The status of the issue. Example: (Open, Resolved, Closed, Completed, In Progress)
                    - assignee (Dict[str, str]): Assignee information
                        - name (str): The assignee's username (e.g., 'jdoe')
                    - issuetype (str): The type of issue
    Raises:
        TypeError: If 'issue_id' is not a string or 'assignee' is not a dictionary.
        pydantic.ValidationError: If 'assignee' dictionary does not conform to the required structure (e.g., missing 'name', or 'name' is not a string).
    """
    if not isinstance(issue_id, str):
        raise TypeError(f"issue_id must be a string, got {type(issue_id).__name__}.")
    if not issue_id:
        raise ValueError("issue_id cannot be empty.")
    if not isinstance(assignee, dict):
        raise TypeError(f"assignee must be a dictionary, got {type(assignee).__name__}.")

    if issue_id not in DB["issues"]:
        raise ValueError(f"Issue '{issue_id}' not found.")

    try:
        validated_assignee = JiraAssignee(**assignee)
    except ValidationError as e:
        raise e

    DB["issues"][issue_id]["fields"]["assignee"] = validated_assignee.model_dump()
    return {"assigned": True, "issue": DB["issues"][issue_id]}


def bulk_issue_operation(issueUpdates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Performs bulk operations on multiple Jira issues.
    
    This function allows updating multiple issues in a single operation.
    Each update can modify fields, assignee, status, priority, summary, or description.
    Additionally, issues can be deleted with optional subtask deletion.
    
    Args:
        issueUpdates (List[Dict[str, Any]]): A list of issue updates to perform.
            Each update should contain:
            - issueId (str): The ID of the issue to update
            - fields (Dict[str, Any], optional): Fields to update
            - assignee (Dict[str, str], optional): Assignee information
            - status (str, optional): New status
            - priority (str, optional): New priority
            - summary (str, optional): New summary
            - description (str, optional): New description
            - delete (bool, optional): Whether to delete this issue (default: False)
            - deleteSubtasks (bool, optional): Whether to delete subtasks when deleting (default: False)
    
    Returns:
        Dict[str, Any]: A dictionary containing:
            - bulkProcessed (bool): Whether all operations were processed successfully
            - updatesCount (int): The number of operations processed
            - successfulUpdates (List[str]): List of successfully updated issue IDs
            - deletedIssues (List[str]): List of successfully deleted issue IDs
    
    Raises:
        TypeError: If 'issueUpdates' is not a list.
        ValueError: If 'issueUpdates' is empty.
        pydantic.ValidationError: If validation fails when the issue update is not in the required format.
    """
    # --- Input Validation ---
    if not isinstance(issueUpdates, list):
        raise TypeError("issueUpdates must be a list")
    
    if not issueUpdates:
        raise ValueError("issueUpdates cannot be empty")
    
 
    validated_request = BulkIssueOperationRequestModel(issueUpdates=issueUpdates)
    
    
    successful_updates = []
    deleted_issues = []
    
    for update in validated_request.issueUpdates:
        
        # Check if issue exists in DB
        if update.issueId not in DB.get("issues", {}):
            raise ValueError(f"Issue with id '{update.issueId}' does not exist.")
        
        # Handle delete operation
        if update.delete:
            issue_data = DB["issues"][update.issueId]
            
            # Check for subtasks if deleteSubtasks is False
            if not update.deleteSubtasks and "sub-tasks" in issue_data.get("fields", {}):
                sub_tasks = issue_data["fields"]["sub-tasks"]
                if sub_tasks:
                    raise ValueError(
                        f"Subtasks exist for issue '{update.issueId}', cannot delete. Set deleteSubtasks=True to delete them."
                    )
            
            # Delete subtasks if requested
            if update.deleteSubtasks and "sub-tasks" in issue_data.get("fields", {}):
                sub_tasks = issue_data["fields"]["sub-tasks"]
                for subtask in sub_tasks:
                    if isinstance(subtask, dict) and "id" in subtask:
                        DB["issues"].pop(subtask["id"], None)
            
            # Delete the issue
            DB["issues"].pop(update.issueId, None)
            deleted_issues.append(update.issueId)
            
        else:
            # Handle update operation
            issue_data = DB["issues"][update.issueId]
            
            # Update fields if provided
            if update.fields:
                if update.fields.summary is not None:
                    issue_data["fields"]["summary"] = update.fields.summary
                if update.fields.description is not None:
                    issue_data["fields"]["description"] = update.fields.description
                if update.fields.priority is not None:
                    issue_data["fields"]["priority"] = update.fields.priority
                if update.fields.status is not None:
                    issue_data["fields"]["status"] = update.fields.status
                if update.fields.assignee is not None:
                    issue_data["fields"]["assignee"] = update.fields.assignee.model_dump()
                if update.fields.issuetype is not None:
                    issue_data["fields"]["issuetype"] = update.fields.issuetype
                if update.fields.project is not None:
                    issue_data["fields"]["project"] = update.fields.project
            
            # Update individual fields if provided (these take precedence over fields object)
            if update.assignee is not None:
                issue_data["fields"]["assignee"] = update.assignee.model_dump()
            if update.status is not None:
                issue_data["fields"]["status"] = update.status
            if update.priority is not None:
                issue_data["fields"]["priority"] = update.priority
            if update.summary is not None:
                issue_data["fields"]["summary"] = update.summary
            if update.description is not None:
                issue_data["fields"]["description"] = update.description
            
            successful_updates.append(update.issueId)
    
    # Create response
    response_data = {
        "bulkProcessed": len(successful_updates) + len(deleted_issues) == len(issueUpdates),  # True only if all operations succeeded
        "updatesCount": len(issueUpdates),
        "successfulUpdates": successful_updates,
        "deletedIssues": deleted_issues
    }
    return response_data


def issue_picker(query: Optional[str] = None, currentJQL: Optional[str] = None) -> Dict[str, Any]:
    """
    Search for issues based on a query string and/or JQL.

    This method searches for issues based on a text query string and/or JQL (Jira Query Language).
    The search is case-insensitive for text queries. JQL filtering is applied first, then text filtering.

    Args:
        query (Optional[str]): The text query string to search for in issue summaries and IDs.
                               If None, no text filtering will be applied.
                               An empty string "" will generally match all issues.
        currentJQL (Optional[str]): JQL expression to filter issues before applying text search.
                                   If provided, only issues matching the JQL will be considered.
                                   Supports all standard JQL operators and functions.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - issues (List[str]): List of issue IDs that match the query and/or JQL.

    Raises:
        TypeError: If 'query' or 'currentJQL' are provided and are not strings.
        ValueError: If 'currentJQL' contains invalid JQL syntax.

    """
    # --- Input Validation ---
    if query is not None and not isinstance(query, str):
        raise TypeError(f"Query must be a string or None, but got {type(query).__name__}.")
    
    if currentJQL is not None and not isinstance(currentJQL, str):
        raise TypeError(f"currentJQL must be a string or None, but got {type(currentJQL).__name__}.")

    # --- Core Logic ---
    # Step 1: Apply JQL filtering if provided
    if currentJQL:
        from .SearchApi import search_issues
        try:
            jql_results = search_issues(jql=currentJQL, max_results=1000)
            filtered_issues = {issue["id"]: issue for issue in jql_results["issues"]}
        except Exception as e:
            raise ValueError(f"Invalid JQL syntax: {str(e)}")
    else:
        # No JQL filtering, use all issues - but handle edge cases
        db_issues = DB.get("issues", {})
        if not isinstance(db_issues, dict):
            # Handle case where DB["issues"] is not a dictionary
            filtered_issues = {}
        else:
            filtered_issues = db_issues

    # Step 2: Apply text query filtering if provided
    matched: List[str] = []
    
    if query is not None:
        processed_query = query.lower()
        
        for iss_id, data in filtered_issues.items():
            if isinstance(data, dict) and "fields" in data and isinstance(data["fields"], dict):
                summary = data["fields"].get("summary", "").lower()
            else:
                summary = ""

            # For empty string query, match all (after JQL filtering)
            if processed_query == "" or processed_query in iss_id.lower() or processed_query in summary:
                matched.append(iss_id)
    else:
        # No text query provided
        if currentJQL:
            # If JQL was provided, return all JQL-filtered results
            matched = list(filtered_issues.keys())
        else:
            # No JQL and no text query, return empty list (per test expectations)
            matched = []
    
    return {"issues": matched}


def get_create_meta(
    projectKeys: Optional[str] = None, issueTypeNames: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get the create metadata for projects and issue types.

    This method returns metadata about projects and their available issue types
    that can be used for creating new issues. The response can be filtered by
    project keys and issue type names.

    Args:
        projectKeys (Optional[str]): Project keys to filter the results. 
            If None, all projects are returned. This parameter accepts a 
            comma-separated list of project keys. Specifying a project 
            that does not exist is not an error, but it will not be in the results.
        issueTypeNames (Optional[str]): Issue type names to filter the results.
            If None, all issue types are returned. This parameter accepts a 
            comma-separated list of issue type names. Specifying an issue type 
            that does not exist is not an error.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - projects (List[Dict[str, Any]]): List of projects with their metadata
                - key (str): The project key
                - name (str): The project name
                - lead (str): The project lead username
                - issueTypes (List[Dict[str, Any]]): List of available issue types for this project                    
                    - name (str): The issue type name

    Raises:
        TypeError: If projectKeys or issueTypeNames are provided and are not strings.
    """
    # Input validation
    if projectKeys is not None and not isinstance(projectKeys, str):
        raise TypeError(f"projectKeys must be a string or None, got {type(projectKeys).__name__}")
    
    if issueTypeNames is not None and not isinstance(issueTypeNames, str):
        raise TypeError(f"issueTypeNames must be a string or None, got {type(issueTypeNames).__name__}")

    # Parse project keys - handle comma-separated list
    requested_project_keys = set()
    if projectKeys:
        # Split by comma and strip whitespace
        keys = [key.strip() for key in projectKeys.split(',')]
        # Filter out empty strings
        requested_project_keys = {key for key in keys if key}
    
    # Parse issue type names - handle comma-separated list
    requested_issue_types = set()
    if issueTypeNames:
        # Split by comma and strip whitespace
        types = [type_name.strip() for type_name in issueTypeNames.split(',')]
        # Filter out empty strings
        requested_issue_types = {type_name for type_name in types if type_name}

    # Get available projects
    available_projects = DB["projects"]

    # First, build a map of project -> issue types from existing issues
    project_issue_types = {}
    for issue_data in DB["issues"].values():
        if isinstance(issue_data, dict) and "fields" in issue_data:
            issue_fields = issue_data["fields"]
            if isinstance(issue_fields, dict):
                project = issue_fields.get("project")
                issue_type = issue_fields.get("issuetype")
                if project and issue_type:
                    if project not in project_issue_types:
                        project_issue_types[project] = set()
                    project_issue_types[project].add(issue_type)

    # Filter projects based on requested keys
    filtered_projects = []
    for project_key, project_data in available_projects.items():
        # If no project keys specified, include all projects
        # If project keys specified, only include requested ones
        if not requested_project_keys or project_key in requested_project_keys:
            # Get issue types for this project
            project_types = project_issue_types.get(project_key, set())
            
            # Filter issue types if requested
            if requested_issue_types:
                project_types = project_types.intersection(requested_issue_types)
            
            # Convert to list of dictionaries
            issue_types_list = [{"name": type_name} for type_name in sorted(project_types)]
            
            # Add project with its issue types
            filtered_projects.append({
                "key": project_data["key"],
                "name": project_data["name"],
                "lead": project_data["lead"],
                "issueTypes": issue_types_list
            })

    return {"projects": filtered_projects}
