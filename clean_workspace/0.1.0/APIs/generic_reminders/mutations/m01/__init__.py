from .generic_reminders import add_reminder_event, find_and_display_reminders, revert_reminder_operation, search_for_reminders, update_existing_reminder

_function_map = {
    'add_reminder_event': 'generic_reminders.mutations.m01.generic_reminders.add_reminder_event',
    'find_and_display_reminders': 'generic_reminders.mutations.m01.generic_reminders.find_and_display_reminders',
    'revert_reminder_operation': 'generic_reminders.mutations.m01.generic_reminders.revert_reminder_operation',
    'search_for_reminders': 'generic_reminders.mutations.m01.generic_reminders.search_for_reminders',
    'update_existing_reminder': 'generic_reminders.mutations.m01.generic_reminders.update_existing_reminder',
}
