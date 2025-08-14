"""
Generic Reminders Service Implementation

This module provides the core functionality for managing reminders,
including creation, modification, search, and undo capabilities.
"""

from typing import Dict, Optional, List, Any
from .SimulationEngine.utils import (
    is_future_datetime,
    is_boring_title,
    _generate_reminder_id,
    _current_timestamp,
    format_schedule_string,
    save_reminder_to_db,
    track_operation,
    get_reminders_by_ids,
    search_reminders,
    undo_operation,
)
from .SimulationEngine.custom_errors import (
    ValidationError,
    ReminderNotFoundError,
    InvalidTimeError,
    OperationNotFoundError,
)
from .SimulationEngine.models import (
    validate_create_reminder_input,
    validate_modify_reminder_input,
    validate_optional_type,
    validate_optional_date,
    validate_optional_time,
    validate_date_range,
    validate_time_range,
    validate_string_list,
    validate_retrieval_query,
)


def create_reminder(
    title: Optional[str] = None,
    description: Optional[str] = None,
    start_date: Optional[str] = None,
    time_of_day: Optional[str] = None,
    am_pm_or_unknown: Optional[str] = None,
    end_date: Optional[str] = None,
    repeat_every_n: Optional[int] = 0,
    repeat_interval_unit: Optional[str] = None,
    days_of_week: Optional[List[str]] = None,
    weeks_of_month: Optional[List[str]] = None,
    days_of_month: Optional[List[str]] = None,
    occurrence_count: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Creates a new reminder. Cannot create reminders in the past.

    Args:
        title (Optional[str]): The title of the reminder. Short description of what to be reminded about.
        description (Optional[str]): Additional description for the reminder.
        start_date (Optional[str]): Scheduled date in YYYY-MM-DD format. Must be current date or future.
        time_of_day (Optional[str]): Scheduled time in hh:mm:ss format.
        am_pm_or_unknown (Optional[str]): One of "AM", "PM", or "UNKNOWN".
        end_date (Optional[str]): End date for recurring reminders in YYYY-MM-DD format. Must be >= start_date.
        repeat_every_n (Optional[int]): Number of repeat intervals. Defaults to 0.
        repeat_interval_unit (Optional[str]): Unit of repeat intervals. Accepts MINUTE, HOUR, DAY, WEEK, MONTH, YEAR in any case (e.g., 'minute', 'MINUTE', 'Minute').
        days_of_week (Optional[List[str]]): Days of week for recurring reminders.
                                            Accepts SUNDAY, MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, or SATURDAY in any case (e.g., 'monday', 'MONDAY', or 'Monday').
        weeks_of_month (Optional[List[str]]): Weeks of month for recurring reminders.
                                            Accepts FIRST, SECOND, THIRD, FOURTH, LAST, or the numeric strings '1'-'5'.
        days_of_month (Optional[List[str]]): Days of month for recurring reminders. 
                                            Accepts DAY_1, DAY_2, DAY_3, DAY_4, DAY_5, DAY_6, DAY_7, DAY_8, DAY_9, DAY_10, DAY_11, DAY_12, DAY_13, DAY_14, DAY_15, DAY_16, DAY_17, DAY_18, DAY_19, DAY_20, DAY_21, DAY_22, DAY_23, DAY_24, DAY_25, DAY_26, DAY_27, DAY_28, DAY_29, DAY_30, DAY_31, or the numeric strings '1'-'31'.
                                            Case-insensitive for DAY_X format (e.g., 'day_5', 'Day_10', 'DAY_15' are all valid).
                                            Use LAST if the user wants the reminder to be scheduled on the last day of the month.
        occurrence_count (Optional[int]): Number of times reminder should recur.

    Returns:
        Dict[str, Any]: RemindersResult containing:
            - message (str): Status message about the operation
            - reminders (List[Dict[str, Any]]): List containing the created reminder with fields:
                - id (str): Unique reminder identifier
                - title (str): Reminder title
                - description (str): Reminder description
                - start_date (str): Scheduled date in YYYY-MM-DD format
                - time_of_day (str): Scheduled time in hh:mm:ss format
                - am_pm_or_unknown (str): AM/PM indicator
                - end_date (str): End date for recurring reminders
                - repeat_every_n (int): Repeat interval number
                - repeat_interval_unit (str): Repeat interval unit
                - days_of_week (List[str]): Days of week for recurrence
                - weeks_of_month (List[str]): Weeks of month for recurrence
                - days_of_month (List[str]): Days of month for recurrence
                - occurrence_count (int): Number of occurrences
                - completed (bool): Whether reminder is completed
                - deleted (bool): Whether reminder is deleted
                - created_at (str): Creation timestamp
                - updated_at (str): Last update timestamp
                - schedule (str): Human-readable schedule string
                - uri (str): Reminder URI
            - undo_operation_ids (List[str]): Operation IDs for undo functionality

    Raises:
        ValidationError: If input parameters don't meet validation requirements.
        InvalidTimeError: If the specified time is in the past.
    """
    # Validate all input parameters comprehensively
    try:
        validated_input = validate_create_reminder_input(
            title=title,
            description=description,
            start_date=start_date,
            time_of_day=time_of_day,
            am_pm_or_unknown=am_pm_or_unknown,
            end_date=end_date,
            repeat_every_n=repeat_every_n,
            repeat_interval_unit=repeat_interval_unit,
            days_of_week=days_of_week,
            weeks_of_month=weeks_of_month,
            days_of_month=days_of_month,
            occurrence_count=occurrence_count,
        )
    except ValidationError as e:
        raise ValidationError(f"Input validation failed: {str(e)}")

    # Check if the specified time is in the future
    if not is_future_datetime(
        validated_input["start_date"],
        validated_input["time_of_day"],
        validated_input["am_pm_or_unknown"],
    ):
        raise InvalidTimeError("Cannot create reminders for past dates and times")

    # Check for boring or empty titles
    if is_boring_title(validated_input["title"]):
        raise ValidationError(
            "Your title is too generic or only contains date/time information. Please enter something more specific."
        )

    # Create the reminder data structure directly (inlined from utils.create_reminder_data)
    reminder_id = _generate_reminder_id()
    timestamp = _current_timestamp()

    reminder_data = {
        "id": reminder_id,
        "title": validated_input.get("title"),
        "description": validated_input.get("description"),
        "start_date": validated_input.get("start_date"),
        "time_of_day": validated_input.get("time_of_day"),
        "am_pm_or_unknown": validated_input.get("am_pm_or_unknown"),
        "end_date": validated_input.get("end_date"),
        "repeat_every_n": validated_input.get("repeat_every_n", 0),
        "repeat_interval_unit": validated_input.get("repeat_interval_unit"),
        "days_of_week": validated_input.get("days_of_week"),
        "weeks_of_month": validated_input.get("weeks_of_month"),
        "days_of_month": validated_input.get("days_of_month"),
        "occurrence_count": validated_input.get("occurrence_count"),
        "completed": False,
        "deleted": False,
        "created_at": timestamp,
        "updated_at": timestamp,
        "uri": f"reminder://{reminder_id}",
    }

    # Generate schedule string
    reminder_data["schedule"] = format_schedule_string(reminder_data)

    # Save reminder to database
    save_reminder_to_db(reminder_data)

    # Track operation for undo functionality
    operation_id = track_operation("create", reminder_id)

    return {
        "message": "Reminder created successfully",
        "reminders": [reminder_data],
        "undo_operation_ids": [operation_id],
    }


def modify_reminder(
    reminder_ids: Optional[List[str]] = None,
    retrieval_query: Optional[Dict[str, Any]] = None,
    completed: Optional[bool] = None,
    deleted: Optional[bool] = None,
    ask_for_confirmation: Optional[bool] = None,
    is_bulk_mutation: bool = True,
    title: Optional[str] = None,
    description: Optional[str] = None,
    start_date: Optional[str] = None,
    time_of_day: Optional[str] = None,
    am_pm_or_unknown: Optional[str] = None,
    end_date: Optional[str] = None,
    repeat_every_n: Optional[int] = None,
    repeat_interval_unit: Optional[str] = None,
    days_of_week: Optional[List[str]] = None,
    weeks_of_month: Optional[List[str]] = None,
    days_of_month: Optional[List[str]] = None,
    occurrence_count: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Search for reminders and modify them. At least one of `reminder_ids` or `retrieval_query` must be provided.

    Args:
        reminder_ids (Optional[List[str]]): Specific reminder IDs to modify.
        retrieval_query (Optional[Dict[str, Any]]): Query to find reminders to modify. Keys include:
            - query (str): Keyword search query
            - from_date (str): Start date in YYYY-MM-DD format
            - to_date (str): End date in YYYY-MM-DD format
            - from_time_of_day (str): Start time in hh:mm:ss format
            - to_time_of_day (str): End time in hh:mm:ss format
            - include_completed (bool): Include completed reminders
            - is_recurring (bool): Filter for recurring reminders only
        completed (Optional[bool]): Mark reminders as completed.
        deleted (Optional[bool]): Mark reminders as deleted.
        ask_for_confirmation (Optional[bool]): Whether to ask for user confirmation.
        is_bulk_mutation (bool): Whether this is a bulk operation on multiple reminders.
        title (Optional[str]): New title for the reminder(s).
        description (Optional[str]): New description for the reminder(s).
        start_date (Optional[str]): New start date in YYYY-MM-DD format.
        time_of_day (Optional[str]): New time in hh:mm:ss format.
        am_pm_or_unknown (Optional[str]): AM/PM indicator or UNKNOWN.
        end_date (Optional[str]): New end date for recurring reminders.
        repeat_every_n (Optional[int]): New repeat interval number.
        repeat_interval_unit (Optional[str]): New repeat interval unit. Accepts values in any case (e.g., 'minute', 'MINUTE', 'Minute').
        days_of_week (Optional[List[str]]): Days of week for recurring reminders.
                                            Accepts SUNDAY, MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, or SATURDAY in any case (e.g., 'monday', 'MONDAY', or 'Monday').
        weeks_of_month (Optional[List[str]]): Weeks of month for recurring reminders.
                                            Accepts FIRST, SECOND, THIRD, FOURTH, LAST, or the numeric strings '1'-'5'.
        days_of_month (Optional[List[str]]): Days of month for recurring reminders. 
                                            Accepts DAY_1, DAY_2, DAY_3, DAY_4, DAY_5, DAY_6, DAY_7, DAY_8, DAY_9, DAY_10, DAY_11, DAY_12, DAY_13, DAY_14, DAY_15, DAY_16, DAY_17, DAY_18, DAY_19, DAY_20, DAY_21, DAY_22, DAY_23, DAY_24, DAY_25, DAY_26, DAY_27, DAY_28, DAY_29, DAY_30, DAY_31, or the numeric strings '1'-'31'.
                                            Case-insensitive for DAY_X format (e.g., 'day_5', 'Day_10', 'DAY_15' are all valid).
                                            Use LAST if the user wants the reminder to be scheduled on the last day of the month.
        occurrence_count (Optional[int]): New occurrence count.

    Returns:
        Dict[str, Any]: RemindersResult containing:
            - message (str): Status message about the operation
            - reminders (List[Dict[str, Any]]): List of modified reminders with fields:
                - id (str): Unique reminder identifier
                - title (str): Reminder title
                - description (str): Reminder description
                - completed (bool): Whether reminder is completed
                - deleted (bool): Whether reminder is deleted
                - start_date (str): Scheduled date in YYYY-MM-DD format
                - time_of_day (str): Scheduled time in hh:mm:ss format
                - am_pm_or_unknown (str): AM/PM indicator
                - end_date (str): End date for recurring reminders
                - repeat_every_n (int): Repeat interval number
                - repeat_interval_unit (str): Repeat interval unit
                - days_of_week (List[str]): Days of week for recurrence
                - weeks_of_month (List[str]): Weeks of month for recurrence
                - days_of_month (List[str]): Days of month for recurrence
                - occurrence_count (int): Number of occurrences
                - created_at (str): Creation timestamp
                - updated_at (str): Last update timestamp
                - schedule (str): Human-readable schedule string
                - uri (str): Reminder URI
            - undo_operation_ids (List[str]): Operation IDs for undo functionality

    Raises:
        ValidationError: If input parameters don't meet validation requirements.
        ReminderNotFoundError: If no matching reminders are found.
        InvalidTimeError: If the new specified time is in the past.
    """
    # Validate all input parameters comprehensively
    try:
        validated_input = validate_modify_reminder_input(
            title=title,
            description=description,
            start_date=start_date,
            time_of_day=time_of_day,
            am_pm_or_unknown=am_pm_or_unknown,
            end_date=end_date,
            repeat_every_n=repeat_every_n,
            repeat_interval_unit=repeat_interval_unit,
            days_of_week=days_of_week,
            weeks_of_month=weeks_of_month,
            days_of_month=days_of_month,
            occurrence_count=occurrence_count,
            completed=completed,
            deleted=deleted,
            reminder_ids=reminder_ids,
            retrieval_query=retrieval_query,
            ask_for_confirmation=ask_for_confirmation,
            is_bulk_mutation=is_bulk_mutation,
        )
    except ValidationError as e:
        raise ValidationError(f"Input validation failed: {str(e)}")

    # Extract validated search parameters
    validated_reminder_ids = validated_input.get("reminder_ids")
    validated_retrieval_query = validated_input.get("retrieval_query")

    # Find reminders to modify
    if validated_reminder_ids:
        target_reminders = get_reminders_by_ids(validated_reminder_ids)
    else:
        query = validated_retrieval_query or {}
        target_reminders = search_reminders(query)

    if not target_reminders:
        raise ReminderNotFoundError("No matching reminders found")

    # Check if new time is in the future (if provided)
    new_start_date = validated_input.get("start_date")
    new_time_of_day = validated_input.get("time_of_day")
    new_am_pm = validated_input.get("am_pm_or_unknown")

    if (
        new_start_date is not None or new_time_of_day is not None
    ) and not is_future_datetime(new_start_date, new_time_of_day, new_am_pm):
        raise InvalidTimeError("Cannot modify reminders to past dates and times")

    # Check for boring titles if title is being changed
    new_title = validated_input.get("title")
    if new_title is not None and is_boring_title(new_title):
        raise ValidationError(
            "Your title is too generic or only contains date/time information. Please enter something more specific."
        )

    # Apply modifications
    modified_reminders = []
    operation_ids = []

    # Build modifications dictionary from validated input
    modifications = {
        key: value
        for key, value in validated_input.items()
        if key
        not in [
            "reminder_ids",
            "retrieval_query",
            "ask_for_confirmation",
            "is_bulk_mutation",
        ]
    }

    for reminder in target_reminders:
        original_data = reminder.copy()

        # Apply modifications directly (inlined from utils.apply_modifications)
        modified_reminder = reminder.copy()

        for key, value in modifications.items():
            if value is not None:
                modified_reminder[key] = value

        # Update metadata
        modified_reminder["updated_at"] = _current_timestamp()
        modified_reminder["schedule"] = format_schedule_string(modified_reminder)

        # Save to database
        save_reminder_to_db(modified_reminder)

        # Track operation for undo
        operation_id = track_operation("modify", reminder["id"], original_data)
        operation_ids.append(operation_id)
        modified_reminders.append(modified_reminder)

    # Build appropriate response message
    action = (
        "completed"
        if validated_input.get("completed")
        else "deleted" if validated_input.get("deleted") else "modified"
    )
    count = len(modified_reminders)
    message = f"{count} reminder{'s' if count != 1 else ''} {action} successfully"

    return {
        "message": message,
        "reminders": modified_reminders,
        "undo_operation_ids": operation_ids,
    }


def get_reminders(
    query: Optional[str] = None,
    from_date: Optional[str] = None,
    from_time_of_day: Optional[str] = None,
    to_date: Optional[str] = None,
    to_time_of_day: Optional[str] = None,
    include_completed: bool = False,
    is_recurring: bool = False,
    include_deleted: bool = False,
) -> Dict[str, Any]:
    """
    Fetch reminders context. This is an internal function not visible to the model.

    Args:
        query (Optional[str]): Query string for searching reminders.
        from_date (Optional[str]): Start date filter in YYYY-MM-DD format.
        from_time_of_day (Optional[str]): Start time filter in hh:mm:ss format.
        to_date (Optional[str]): End date filter in YYYY-MM-DD format.
        to_time_of_day (Optional[str]): End time filter in hh:mm:ss format.
        include_completed (bool): Whether to include completed reminders.
        is_recurring (bool): Whether to filter for recurring reminders only.
        include_deleted (bool): Whether to include deleted reminders.

    Returns:
        Dict[str, Any]: RemindersResult containing:
            - message (str): Status message indicating number of reminders found
            - reminders (List[Dict[str, Any]]): List of matching reminder objects, each containing:
                - id (str): Unique reminder identifier
                - title (str): Reminder title
                - description (str): Reminder description
                - start_date (str): Scheduled date in YYYY-MM-DD format
                - time_of_day (str): Scheduled time in hh:mm:ss format
                - am_pm_or_unknown (str): AM/PM indicator
                - end_date (str): End date for recurring reminders
                - repeat_every_n (int): Repeat interval number
                - repeat_interval_unit (str): Repeat interval unit
                - days_of_week (List[str]): Days of week for recurrence
                - weeks_of_month (List[str]): Weeks of month for recurrence
                - days_of_month (List[str]): Days of month for recurrence
                - occurrence_count (int): Number of occurrences
                - completed (bool): Whether reminder is completed
                - deleted (bool): Whether reminder is deleted
                - created_at (str): Creation timestamp
                - updated_at (str): Last update timestamp
                - schedule (str): Human-readable schedule string
                - uri (str): Reminder URI

    Raises:
        ValidationError: If validation fails for any of the following reasons:
            - query is not a string
            - Date parameters (from_date, to_date) are not in YYYY-MM-DD format
            - Time parameters (from_time_of_day, to_time_of_day) are not in hh:mm:ss format
            - Boolean parameters (include_completed, is_recurring, include_deleted) are not boolean
            - from_date is after to_date
            - from_time_of_day is after to_time_of_day (when on the same date)
    """
    # Validate input types and formats
    validate_optional_type(query, str, "query")
    validate_optional_type(include_completed, bool, "include_completed")
    validate_optional_type(is_recurring, bool, "is_recurring")
    validate_optional_type(include_deleted, bool, "include_deleted")

    # Validate date and time formats
    validate_optional_date(from_date, "from_date")
    validate_optional_date(to_date, "to_date")
    validate_optional_time(from_time_of_day, "from_time_of_day")
    validate_optional_time(to_time_of_day, "to_time_of_day")

    # Validate logical relationships
    validate_date_range(from_date, to_date)

    # Only validate time relationship if both dates are the same or not specified
    if from_date == to_date or (from_date is None and to_date is None):
        validate_time_range(from_time_of_day, to_time_of_day)

    search_params = {
        "query": query,
        "from_date": from_date,
        "from_time_of_day": from_time_of_day,
        "to_date": to_date,
        "to_time_of_day": to_time_of_day,
        "include_completed": include_completed,
        "is_recurring": is_recurring,
        "include_deleted": include_deleted,
    }

    # Remove None values
    search_params = {k: v for k, v in search_params.items() if v is not None}

    matching_reminders = search_reminders(search_params)

    return {
        "message": f"Found {len(matching_reminders)} matching reminders",
        "reminders": matching_reminders,
    }


def show_matching_reminders(
    reminder_ids: Optional[List[str]] = None,
    retrieval_query: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Search for and show matching reminders to the user. When using reminder_ids, deleted reminders are included. When using retrieval_query, deleted reminders are excluded by default unless include_deleted=True.

    Args:
        reminder_ids (Optional[List[str]]): Specific reminder IDs to show. Deleted reminders will be included.
        retrieval_query (Optional[Dict[str, Any]]): Query to find reminders to show. Keys include:
            - query (str): Keyword search query
            - from_date (str): Start date in YYYY-MM-DD format
            - to_date (str): End date in YYYY-MM-DD format
            - from_time_of_day (str): Start time in hh:mm:ss format
            - to_time_of_day (str): End time in hh:mm:ss format
            - include_completed (bool): Include completed reminders
            - is_recurring (bool): Filter for recurring reminders only
            - include_deleted (bool): Include deleted reminders

    Returns:
        Dict[str, Any]: RemindersResult containing:
            - message (str): Status message indicating number of reminders found
            - reminders (List[Dict[str, Any]]): List of matching reminder objects, each containing:
                - id (str): Unique reminder identifier
                - title (str): Reminder title
                - description (str): Reminder description
                - start_date (str): Scheduled date in YYYY-MM-DD format
                - time_of_day (str): Scheduled time in hh:mm:ss format
                - am_pm_or_unknown (str): AM/PM indicator
                - end_date (str): End date for recurring reminders
                - repeat_every_n (int): Repeat interval number
                - repeat_interval_unit (str): Repeat interval unit
                - days_of_week (List[str]): Days of week for recurrence
                - weeks_of_month (List[str]): Weeks of month for recurrence
                - days_of_month (List[str]): Days of month for recurrence
                - occurrence_count (int): Number of occurrences
                - completed (bool): Whether reminder is completed
                - deleted (bool): Whether reminder is deleted
                - created_at (str): Creation timestamp
                - updated_at (str): Last update timestamp
                - schedule (str): Human-readable schedule string
                - uri (str): Reminder URI

    Raises:
        ValidationError: If validation fails for any of the following reasons:
            - Both reminder_ids and retrieval_query are provided
            - Neither reminder_ids nor retrieval_query is provided
            - reminder_ids is not a list or contains non-string values
            - reminder_ids is empty
            - retrieval_query is not a dictionary
        ReminderNotFoundError: If any of the provided reminder_ids are not found.
    """
    # Validate that exactly one search method is provided
    if reminder_ids is not None and retrieval_query is not None:
        raise ValidationError(
            "Provide either reminder_ids or retrieval_query, not both"
        )

    if reminder_ids is None and retrieval_query is None:
        raise ValidationError("Must provide either reminder_ids or retrieval_query")

    # Validate input types and values
    try:
        if reminder_ids is not None:
            validate_string_list(reminder_ids, "reminder_ids", allow_empty=False)

        if retrieval_query is not None:
            validate_optional_type(retrieval_query, dict, "retrieval_query")
            # Validate the dictionary structure and contents
            validate_retrieval_query(retrieval_query)
    except ValidationError as e:
        raise ValidationError(f"Input validation failed: {str(e)}")

    # Find reminders to show
    if reminder_ids:
        matching_reminders = get_reminders_by_ids(reminder_ids)

        # Check if all requested IDs were found
        found_ids = {reminder["id"] for reminder in matching_reminders}
        missing_ids = [id_val for id_val in reminder_ids if id_val not in found_ids]

        if missing_ids:
            raise ReminderNotFoundError(
                f"Reminder IDs not found: {', '.join(missing_ids)}"
            )
    else:
        query = retrieval_query or {}
        matching_reminders = search_reminders(query)

    count = len(matching_reminders)
    message = f"Found {count} matching reminder{'s' if count != 1 else ''}"

    return {
        "message": message,
        "reminders": matching_reminders,
    }


def undo(undo_operation_ids: Optional[List[str]] = None) -> str:
    """
    Revert reminder operations from the last turn of conversation.

    Args:
        undo_operation_ids (Optional[List[str]]): IDs of operations to undo.

    Returns:
        str: Status message indicating success or failure of undo operations.

    Raises:
        ValidationError: If validation fails for any of the following reasons:
            - undo_operation_ids is not a list
            - undo_operation_ids contains non-string values
        OperationNotFoundError: If any of the specified operation IDs don't exist in the operations database.
    """
    if not undo_operation_ids:
        return "No operations to undo"

    # Validate operation IDs using validation utilities
    try:
        validate_string_list(
            undo_operation_ids, "undo_operation_ids", allow_empty=False
        )
    except ValidationError as e:
        raise ValidationError(f"Input validation failed: {str(e)}")

    # Perform undo operations
    successful_undos = []
    failed_undos = []

    for operation_id in undo_operation_ids:
        try:
            undo_operation(operation_id)
            successful_undos.append(operation_id)
        except OperationNotFoundError:
            # If there's only one operation ID and it fails, raise the error
            if len(undo_operation_ids) == 1:
                raise
            # Otherwise, add the operation ID to the list of failed undos
            failed_undos.append(operation_id)
        except Exception as e:
            # Catch any other exceptions and add the operation ID to failed undos
            failed_undos.append(operation_id)

    # Build response message
    success_count = len(successful_undos)
    failure_count = len(failed_undos)

    if success_count > 0 and failure_count == 0:
        return f"Successfully reverted {success_count} operation{'s' if success_count != 1 else ''}"
    elif success_count == 0 and failure_count > 0:
        return f"Failed to revert {failure_count} operation{'s' if failure_count != 1 else ''}"
    else:
        return f"Reverted {success_count} operation{'s' if success_count != 1 else ''}, failed to revert {failure_count}"
