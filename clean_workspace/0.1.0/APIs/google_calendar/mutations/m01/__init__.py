from .AclResource import add_calendar_access_rule, fetch_permission_rule, get_all_calendar_permission_rules, modify_existing_permission_rule, monitor_permission_rule_modifications, remove_calendar_permission_rule, replace_access_control_rule
from .CalendarListResource import add_calendar_to_my_list, fetch_calendar_from_my_list, modify_my_calendar_list_item, monitor_my_calendar_list_updates, remove_calendar_from_my_list, replace_my_calendar_list_item, retrieve_my_calendar_list
from .CalendarsResource import establish_new_secondary_calendar, fetch_calendar_properties, fully_replace_calendar_details, partially_update_calendar_details, purge_main_calendar, remove_auxiliary_calendar
from .ChannelsResource import terminate_resource_watch
from .ColorsResource import retrieve_color_definitions
from .EventsResource import add_event_from_definition, create_event_from_text_prompt, fetch_event_details, get_recurring_event_occurrences, modify_event_partially, monitor_event_modifications, relocate_event_to_another_calendar, remove_calendar_event, replace_existing_event, retrieve_events_from_calendar, schedule_new_calendar_event

_function_map = {
    'add_calendar_access_rule': 'google_calendar.mutations.m01.AclResource.add_calendar_access_rule',
    'add_calendar_to_my_list': 'google_calendar.mutations.m01.CalendarListResource.add_calendar_to_my_list',
    'add_event_from_definition': 'google_calendar.mutations.m01.EventsResource.add_event_from_definition',
    'create_event_from_text_prompt': 'google_calendar.mutations.m01.EventsResource.create_event_from_text_prompt',
    'establish_new_secondary_calendar': 'google_calendar.mutations.m01.CalendarsResource.establish_new_secondary_calendar',
    'fetch_calendar_from_my_list': 'google_calendar.mutations.m01.CalendarListResource.fetch_calendar_from_my_list',
    'fetch_calendar_properties': 'google_calendar.mutations.m01.CalendarsResource.fetch_calendar_properties',
    'fetch_event_details': 'google_calendar.mutations.m01.EventsResource.fetch_event_details',
    'fetch_permission_rule': 'google_calendar.mutations.m01.AclResource.fetch_permission_rule',
    'fully_replace_calendar_details': 'google_calendar.mutations.m01.CalendarsResource.fully_replace_calendar_details',
    'get_all_calendar_permission_rules': 'google_calendar.mutations.m01.AclResource.get_all_calendar_permission_rules',
    'get_recurring_event_occurrences': 'google_calendar.mutations.m01.EventsResource.get_recurring_event_occurrences',
    'modify_event_partially': 'google_calendar.mutations.m01.EventsResource.modify_event_partially',
    'modify_existing_permission_rule': 'google_calendar.mutations.m01.AclResource.modify_existing_permission_rule',
    'modify_my_calendar_list_item': 'google_calendar.mutations.m01.CalendarListResource.modify_my_calendar_list_item',
    'monitor_event_modifications': 'google_calendar.mutations.m01.EventsResource.monitor_event_modifications',
    'monitor_my_calendar_list_updates': 'google_calendar.mutations.m01.CalendarListResource.monitor_my_calendar_list_updates',
    'monitor_permission_rule_modifications': 'google_calendar.mutations.m01.AclResource.monitor_permission_rule_modifications',
    'partially_update_calendar_details': 'google_calendar.mutations.m01.CalendarsResource.partially_update_calendar_details',
    'purge_main_calendar': 'google_calendar.mutations.m01.CalendarsResource.purge_main_calendar',
    'relocate_event_to_another_calendar': 'google_calendar.mutations.m01.EventsResource.relocate_event_to_another_calendar',
    'remove_auxiliary_calendar': 'google_calendar.mutations.m01.CalendarsResource.remove_auxiliary_calendar',
    'remove_calendar_event': 'google_calendar.mutations.m01.EventsResource.remove_calendar_event',
    'remove_calendar_from_my_list': 'google_calendar.mutations.m01.CalendarListResource.remove_calendar_from_my_list',
    'remove_calendar_permission_rule': 'google_calendar.mutations.m01.AclResource.remove_calendar_permission_rule',
    'replace_access_control_rule': 'google_calendar.mutations.m01.AclResource.replace_access_control_rule',
    'replace_existing_event': 'google_calendar.mutations.m01.EventsResource.replace_existing_event',
    'replace_my_calendar_list_item': 'google_calendar.mutations.m01.CalendarListResource.replace_my_calendar_list_item',
    'retrieve_color_definitions': 'google_calendar.mutations.m01.ColorsResource.retrieve_color_definitions',
    'retrieve_events_from_calendar': 'google_calendar.mutations.m01.EventsResource.retrieve_events_from_calendar',
    'retrieve_my_calendar_list': 'google_calendar.mutations.m01.CalendarListResource.retrieve_my_calendar_list',
    'schedule_new_calendar_event': 'google_calendar.mutations.m01.EventsResource.schedule_new_calendar_event',
    'terminate_resource_watch': 'google_calendar.mutations.m01.ChannelsResource.terminate_resource_watch',
}
