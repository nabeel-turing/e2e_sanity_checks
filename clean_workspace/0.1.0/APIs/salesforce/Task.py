# APIs/salesforce/Task.py
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
import re
from salesforce.SimulationEngine.db import DB
from salesforce.SimulationEngine.models import TaskCreateModel, TaskCriteriaModel
from pydantic import ValidationError

"""
Represents the Task resource in the API.
"""


def create(
    Priority: str,
    Status: str,
    Id: Optional[str] = None,
    Name: Optional[str] = None,
    Subject: Optional[str] = None,
    Description: Optional[str] = None,
    ActivityDate: Optional[str] = None,
    DueDate: Optional[str] = None,
    OwnerId: Optional[str] = None,
    WhoId: Optional[str] = None,
    WhatId: Optional[str] = None,
    IsReminderSet: Optional[bool] = None,
    ReminderDateTime: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Creates a new task.

    Args:
        Priority (str): Priority of the task (required).
        Status (str): Status of the task (required).
        Id (Optional[str]): Custom ID for the task. If not provided, a UUID will be generated.
        Name (Optional[str]): The name of the task.
        Subject (Optional[str]): The subject of the task.
        Description (Optional[str]): Description of the task.
        ActivityDate (Optional[str]): Due date of the task.
        DueDate (Optional[str]): Alternative field for task due date.
        OwnerId (Optional[str]): ID of the task owner.
        WhoId (Optional[str]): ID of the related contact.
        WhatId (Optional[str]): ID of the related record.
        IsReminderSet (Optional[bool]): Whether reminder is set.
        ReminderDateTime (Optional[str]): Reminder date and time.

    Returns:
        Dict[str, Any]: The created task object with the following fields:
            - Id (str): Unique identifier for the task
            - CreatedDate (str): ISO format timestamp of creation
            - IsDeleted (bool): Whether the task is deleted
            - SystemModstamp (str): Last modified timestamp
            - Priority (str): Priority of the task
            - Status (str): Status of the task
            - Name (Optional[str]): The name of the task, if provided
            - Subject (Optional[str]): The subject of the task, if provided
            - Description (Optional[str]): Description of the task, if provided
            - ActivityDate (Optional[str]): Due date of the task, if provided
            - DueDate (Optional[str]): Alternative due date field, if provided
            - OwnerId (Optional[str]): ID of the task owner, if provided
            - WhoId (Optional[str]): ID of the related contact, if provided
            - WhatId (Optional[str]): ID of the related record, if provided
            - IsReminderSet (Optional[bool]): Whether reminder is set, if provided
            - ReminderDateTime (Optional[str]): Reminder date and time, if provided

    Raises:
        ValidationError: If 'task_attributes' do not conform to the TaskCreateModel structure
                                 (e.g., missing required fields 'Priority' or 'Status',
                                 or if any field has an invalid type, or if extra unexpected
                                 fields are provided).
    """
    if Priority is None or Status is None:
        raise ValueError("Priority and Status are required for creating a task.")

    new_task = {
        "Id": Id if Id is not None else str(uuid.uuid4()),
        "CreatedDate": datetime.now().isoformat(),
        "IsDeleted": False,
        "SystemModstamp": datetime.now().isoformat(),
        "Priority": Priority,
        "Status": Status,
    }

    # Add optional fields if provided
    if Name is not None:
        new_task["Name"] = Name
    if Subject is not None:
        new_task["Subject"] = Subject
    if Description is not None:
        new_task["Description"] = Description
    if ActivityDate is not None:
        new_task["ActivityDate"] = ActivityDate
    if DueDate is not None:
        new_task["DueDate"] = DueDate
    if OwnerId is not None:
        new_task["OwnerId"] = OwnerId
    if WhoId is not None:
        new_task["WhoId"] = WhoId
    if WhatId is not None:
        new_task["WhatId"] = WhatId
    if IsReminderSet is not None:
        new_task["IsReminderSet"] = IsReminderSet
    if ReminderDateTime is not None:
        new_task["ReminderDateTime"] = ReminderDateTime

    DB.setdefault("Task", {})
    DB["Task"][new_task["Id"]] = new_task

    return new_task


def delete(task_id: str) -> Dict[str, Any]:
    """
    Deletes a task.

    Args:
        task_id (str): The ID of the task to delete.

    Returns:
        Dict[str, Any]: Empty dict on success, or error dict with structure:
            - error (str): Error message if task not found
    """
    if "Task" in DB and task_id in DB["Task"]:
        del DB["Task"][task_id]
        return {}
    else:
        return {"error": "Task not found"}


def describeLayout() -> Dict[str, Any]:
    """
    Describes the layout of a task.

    Returns:
        Dict[str, Any]: Task layout description with structure:
            - layout (str): Description of the task layout
    """
    return {"layout": "Task layout description"}


def describeSObjects() -> Dict[str, Any]:
    """
    Describes Task SObjects.

    Returns:
        Dict[str, Any]: Task object description with structure:
            - object (str): Description of the task object
    """
    return {"object": "Task object description"}


def getDeleted() -> Dict[str, Any]:
    """
    Retrieves deleted tasks.

    Returns:
        Dict[str, Any]: List of deleted tasks with structure:
            - deleted (list): List of deleted task objects
    """
    return {"deleted": []}  # Return an empty list for now


def getUpdated() -> Dict[str, Any]:
    """
    Retrieves updated tasks.

    Returns:
        Dict[str, Any]: List of updated tasks with structure:
            - updated (list): List of updated task objects
    """
    return {"updated": []}  # Return an empty list for now


def query(criteria: Optional[Dict[str, Any]] = None) -> Dict[str, List[Dict[str, Any]]]:
    """
    Queries tasks based on specified criteria.

    Args:
        criteria (Optional[Dict[str, Any]]): Key-value pairs to filter tasks.
            If provided, the dictionary structure is validated. Example:
            {
                "Subject": Optional[str],
                "Priority": Optional[str],
                "Status": Optional[str],
                "ActivityDate": Optional[str] # e.g., "2024-01-01"
            }
            All keys within the criteria dictionary are optional.

    Returns:
        Dict[str, List[Dict[str, Any]]]: A dictionary containing a list of
            task objects matching the criteria under the key 'results'. Example:
            {
                "results": [
                    {"id": "task-1", "Subject": "Review", ...},
                    ...
                ]
            }

    Raises:
        ValidationError: If 'criteria' is provided but does not conform
            to the expected structure or types (e.g., non-string value for Subject).
        TypeError: If criteria is not None and not a dictionary.
    """
    # --- Input Validation ---
    if criteria is not None:
        if not isinstance(criteria, dict):
            raise TypeError("Argument 'criteria' must be a dictionary or None.")
        try:
            TaskCriteriaModel(**criteria)
        except ValidationError as e:
            raise e

    # --- Core Logic ---
    results = []

    # Handle empty DB cases
    if "Task" not in DB or not DB["Task"]:
        return {"results": []}

    for task_id, task in DB["Task"].items():
        # Ensure the task itself is a dictionary before proceeding
        if not isinstance(task, dict):
            continue

        if criteria is None:
            results.append(task)
        else:
            match = True
            for key, value in criteria.items():
                # Check if key exists in task and if the value matches
                if key not in task or task.get(key) != value:
                    match = False
                    break
            if match:
                results.append(task)

    return {"results": results}


def retrieve(task_id: str) -> Dict[str, Any]:
    """
    Retrieves a task.

    Args:
        task_id (str): The ID of the task to retrieve.

    Returns:
        Dict[str, Any]: The task object if found, or error dict with structure:
            - error (str): Error message if task not found
    """
    if "Task" in DB and task_id in DB["Task"]:
        return DB["Task"][task_id]
    else:
        return {"error": "Task not found"}


def search(search_term: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Searches for tasks based on specified search criteria.

    Args:
        search_term (str): The term to search for in task fields.

    Returns:
        Dict[str, List[Dict[str, Any]]]: List of tasks containing the search term with structure:
            - results (list): List of task objects containing the search term

    Raises:
        TypeError: If search_term is not a string
    """
    if not isinstance(search_term, str):
        raise TypeError("search_term must be a string.")

    results = []
    if "Task" in DB and isinstance(DB["Task"], dict):
        # If search term is empty, return all tasks
        if not search_term:
            results = list(DB["Task"].values())
        else:
            search_term_lower = search_term.lower()
            for task in DB["Task"].values():
                # Convert all values to strings and search case-insensitively
                task_values = []
                for value in task.values():
                    if isinstance(value, (str, int, float, bool)):
                        task_values.append(str(value).lower())
                    elif value is not None:
                        task_values.append(str(value).lower())
                task_str = " ".join(task_values)
                if search_term_lower in task_str:
                    results.append(task)
    return {"results": results}


def undelete(task_id: str) -> Dict[str, Any]:
    """
    Recovers deleted tasks. (Placeholder - no actual deletion tracking).

    Args:
        task_id (str): The ID of the task to undelete.

    Returns:
        Dict[str, Any]: The task object if found, or error dict with structure:
            - error (str): Error message if task not found
    """
    if "Task" in DB and task_id in DB["Task"]:
        return DB["Task"][task_id]
    else:
        return {"error": "Task not found"}


def update(
    task_id: str,
    Name: Optional[str] = None,
    Subject: Optional[str] = None,
    Priority: Optional[str] = None,
    Status: Optional[str] = None,
    Description: Optional[str] = None,
    ActivityDate: Optional[str] = None,
    OwnerId: Optional[str] = None,
    WhoId: Optional[str] = None,
    WhatId: Optional[str] = None,
    IsReminderSet: Optional[bool] = None,
    ReminderDateTime: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Updates a task.

    Args:
        task_id (str): The ID of the task to update.
        Name (Optional[str]): The name of the task.
        Subject (Optional[str]): The subject of the task.
        Priority (Optional[str]): Priority of the task.
        Status (Optional[str]): Status of the task.
        Description (Optional[str]): Description of the task.
        ActivityDate (Optional[str]): Due date of the task.
        OwnerId (Optional[str]): ID of the task owner.
        WhoId (Optional[str]): ID of the related contact.
        WhatId (Optional[str]): ID of the related record.
        IsReminderSet (Optional[bool]): Whether reminder is set.
        ReminderDateTime (Optional[str]): Reminder date and time.

    Returns:
        Dict[str, Any]: The updated task object if found, or error dict with structure:
            - error (str): Error message if task not found
            If successful, returns the task object with the following fields:
            - Id (str): Unique identifier for the task
            - CreatedDate (str): ISO format timestamp of creation
            - IsDeleted (bool): Whether the task is deleted
            - SystemModstamp (str): Last modified timestamp
            - Name (Optional[str]): The name of the task, if provided
            - Subject (Optional[str]): The subject of the task, if provided
            - Priority (Optional[str]): Priority of the task, if provided
            - Status (Optional[str]): Status of the task, if provided
            - Description (Optional[str]): Description of the task, if provided
            - ActivityDate (Optional[str]): Due date of the task, if provided
            - OwnerId (Optional[str]): ID of the task owner, if provided
            - WhoId (Optional[str]): ID of the related contact, if provided
            - WhatId (Optional[str]): ID of the related record, if provided
            - IsReminderSet (Optional[bool]): Whether reminder is set, if provided
            - ReminderDateTime (Optional[str]): Reminder date and time, if provided
    """
    if "Task" in DB and task_id in DB["Task"]:
        task = DB["Task"][task_id]

        # Update only provided fields
        if Name is not None:
            task["Name"] = Name
        if Subject is not None:
            task["Subject"] = Subject
        if Priority is not None:
            task["Priority"] = Priority
        if Status is not None:
            task["Status"] = Status
        if Description is not None:
            task["Description"] = Description
        if ActivityDate is not None:
            task["ActivityDate"] = ActivityDate
        if OwnerId is not None:
            task["OwnerId"] = OwnerId
        if WhoId is not None:
            task["WhoId"] = WhoId
        if WhatId is not None:
            task["WhatId"] = WhatId
        if IsReminderSet is not None:
            task["IsReminderSet"] = IsReminderSet
        if ReminderDateTime is not None:
            task["ReminderDateTime"] = ReminderDateTime

        task["SystemModstamp"] = datetime.now().isoformat()
        return task
    else:
        return {"error": "Task not found"}


def upsert(
    Id: Optional[str] = None,
    Name: Optional[str] = None,
    Subject: Optional[str] = None,
    Priority: Optional[str] = None,
    Status: Optional[str] = None,
    Description: Optional[str] = None,
    ActivityDate: Optional[str] = None,
    OwnerId: Optional[str] = None,
    WhoId: Optional[str] = None,
    WhatId: Optional[str] = None,
    IsReminderSet: Optional[bool] = None,
    ReminderDateTime: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Creates or updates a task.

    Args:
        Id (Optional[str]): Task ID (required for update).
        Name (Optional[str]): The name of the task.
        Subject (Optional[str]): The subject of the task.
        Priority (Optional[str]): Priority of the task.
        Status (Optional[str]): Status of the task.
        Description (Optional[str]): Description of the task.
        ActivityDate (Optional[str]): Due date of the task.
        OwnerId (Optional[str]): ID of the task owner.
        WhoId (Optional[str]): ID of the related contact.
        WhatId (Optional[str]): ID of the related record.
        IsReminderSet (Optional[bool]): Whether reminder is set.
        ReminderDateTime (Optional[str]): Reminder date and time.

    Returns:
        Dict[str, Any]: The created or updated task object with the following fields:
            - Id (str): Unique identifier for the task
            - CreatedDate (str): ISO format timestamp of creation
            - IsDeleted (bool): Whether the task is deleted
            - SystemModstamp (str): Last modified timestamp
            - Name (Optional[str]): The name of the task, if provided
            - Subject (Optional[str]): The subject of the task, if provided
            - Priority (Optional[str]): Priority of the task, if provided
            - Status (Optional[str]): Status of the task, if provided
            - Description (Optional[str]): Description of the task, if provided
            - ActivityDate (Optional[str]): Due date of the task, if provided
            - OwnerId (Optional[str]): ID of the task owner, if provided
            - WhoId (Optional[str]): ID of the related contact, if provided
            - WhatId (Optional[str]): ID of the related record, if provided
            - IsReminderSet (Optional[bool]): Whether reminder is set, if provided
            - ReminderDateTime (Optional[str]): Reminder date and time, if provided
    """
    if Id is not None and Id in DB.get("Task", {}):
        return update(
            Id,
            Name=Name,
            Subject=Subject,
            Priority=Priority,
            Status=Status,
            Description=Description,
            ActivityDate=ActivityDate,
            OwnerId=OwnerId,
            WhoId=WhoId,
            WhatId=WhatId,
            IsReminderSet=IsReminderSet,
            ReminderDateTime=ReminderDateTime,
        )
    else:
        return create(
            Priority=Priority,
            Status=Status,
            Name=Name,
            Subject=Subject,
            Description=Description,
            ActivityDate=ActivityDate,
            OwnerId=OwnerId,
            WhoId=WhoId,
            WhatId=WhatId,
            IsReminderSet=IsReminderSet,
            ReminderDateTime=ReminderDateTime,
        )
