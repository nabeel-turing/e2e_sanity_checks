from .Event import add_calendar_event, create_or_update_event, fetch_event_object_schema, fetch_specific_event, find_events_by_filter, get_event_layout_structure, locate_events_by_keyword, modify_calendar_event, remove_calendar_event, restore_deleted_event, retrieve_modified_events, retrieve_removed_events
from .Query import decode_where_filter_rules, run_soql_command
from .Task import add_new_task, create_or_modify_task, fetch_single_task_data, fetch_task_object_schema, find_tasks_by_attributes, get_task_ui_configuration, locate_tasks_by_text, modify_existing_task, remove_task_record, restore_deleted_task, retrieve_erased_tasks, retrieve_revised_tasks

_function_map = {
    'add_calendar_event': 'salesforce.mutations.m01.Event.add_calendar_event',
    'add_new_task': 'salesforce.mutations.m01.Task.add_new_task',
    'create_or_modify_task': 'salesforce.mutations.m01.Task.create_or_modify_task',
    'create_or_update_event': 'salesforce.mutations.m01.Event.create_or_update_event',
    'decode_where_filter_rules': 'salesforce.mutations.m01.Query.decode_where_filter_rules',
    'fetch_event_object_schema': 'salesforce.mutations.m01.Event.fetch_event_object_schema',
    'fetch_single_task_data': 'salesforce.mutations.m01.Task.fetch_single_task_data',
    'fetch_specific_event': 'salesforce.mutations.m01.Event.fetch_specific_event',
    'fetch_task_object_schema': 'salesforce.mutations.m01.Task.fetch_task_object_schema',
    'find_events_by_filter': 'salesforce.mutations.m01.Event.find_events_by_filter',
    'find_tasks_by_attributes': 'salesforce.mutations.m01.Task.find_tasks_by_attributes',
    'get_event_layout_structure': 'salesforce.mutations.m01.Event.get_event_layout_structure',
    'get_task_ui_configuration': 'salesforce.mutations.m01.Task.get_task_ui_configuration',
    'locate_events_by_keyword': 'salesforce.mutations.m01.Event.locate_events_by_keyword',
    'locate_tasks_by_text': 'salesforce.mutations.m01.Task.locate_tasks_by_text',
    'modify_calendar_event': 'salesforce.mutations.m01.Event.modify_calendar_event',
    'modify_existing_task': 'salesforce.mutations.m01.Task.modify_existing_task',
    'remove_calendar_event': 'salesforce.mutations.m01.Event.remove_calendar_event',
    'remove_task_record': 'salesforce.mutations.m01.Task.remove_task_record',
    'restore_deleted_event': 'salesforce.mutations.m01.Event.restore_deleted_event',
    'restore_deleted_task': 'salesforce.mutations.m01.Task.restore_deleted_task',
    'retrieve_erased_tasks': 'salesforce.mutations.m01.Task.retrieve_erased_tasks',
    'retrieve_modified_events': 'salesforce.mutations.m01.Event.retrieve_modified_events',
    'retrieve_removed_events': 'salesforce.mutations.m01.Event.retrieve_removed_events',
    'retrieve_revised_tasks': 'salesforce.mutations.m01.Task.retrieve_revised_tasks',
    'run_soql_command': 'salesforce.mutations.m01.Query.run_soql_command',
}
