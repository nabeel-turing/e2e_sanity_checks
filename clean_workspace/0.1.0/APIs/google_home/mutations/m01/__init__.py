from .cancel_schedules_api import remove_scheduled_actions
from .details_api import fetch_device_status
from .devices_api import find_devices_by_properties
from .generate_home_automation_api import create_automation_script
from .get_all_devices_api import list_all_user_devices
from .get_devices_api import search_for_relevant_devices
from .mutate_api import schedule_device_state_change
from .mutate_traits_api import change_device_properties_immediately
from .run_api import execute_general_operation
from .search_home_events_api import query_home_activity_log
from .see_devices_api import generate_device_info_table
from .view_schedules_api import list_pending_device_actions

_function_map = {
    'change_device_properties_immediately': 'google_home.mutations.m01.mutate_traits_api.change_device_properties_immediately',
    'create_automation_script': 'google_home.mutations.m01.generate_home_automation_api.create_automation_script',
    'execute_general_operation': 'google_home.mutations.m01.run_api.execute_general_operation',
    'fetch_device_status': 'google_home.mutations.m01.details_api.fetch_device_status',
    'find_devices_by_properties': 'google_home.mutations.m01.devices_api.find_devices_by_properties',
    'generate_device_info_table': 'google_home.mutations.m01.see_devices_api.generate_device_info_table',
    'list_all_user_devices': 'google_home.mutations.m01.get_all_devices_api.list_all_user_devices',
    'list_pending_device_actions': 'google_home.mutations.m01.view_schedules_api.list_pending_device_actions',
    'query_home_activity_log': 'google_home.mutations.m01.search_home_events_api.query_home_activity_log',
    'remove_scheduled_actions': 'google_home.mutations.m01.cancel_schedules_api.remove_scheduled_actions',
    'schedule_device_state_change': 'google_home.mutations.m01.mutate_api.schedule_device_state_change',
    'search_for_relevant_devices': 'google_home.mutations.m01.get_devices_api.search_for_relevant_devices',
}
