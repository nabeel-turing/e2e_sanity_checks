from .app_settings import check_application_notification_state, configure_application_notifications, list_all_installed_applications
from .device_setting import assign_specific_volume_level, disable_device_setting, enable_device_setting, fetch_device_status_summary, modify_volume_level_by_offset, navigate_to_settings_page, restore_volume_stream, retrieve_setting_value, silence_volume_stream

_function_map = {
    'assign_specific_volume_level': 'device_setting.mutations.m01.device_setting.assign_specific_volume_level',
    'check_application_notification_state': 'device_setting.mutations.m01.app_settings.check_application_notification_state',
    'configure_application_notifications': 'device_setting.mutations.m01.app_settings.configure_application_notifications',
    'disable_device_setting': 'device_setting.mutations.m01.device_setting.disable_device_setting',
    'enable_device_setting': 'device_setting.mutations.m01.device_setting.enable_device_setting',
    'fetch_device_status_summary': 'device_setting.mutations.m01.device_setting.fetch_device_status_summary',
    'list_all_installed_applications': 'device_setting.mutations.m01.app_settings.list_all_installed_applications',
    'modify_volume_level_by_offset': 'device_setting.mutations.m01.device_setting.modify_volume_level_by_offset',
    'navigate_to_settings_page': 'device_setting.mutations.m01.device_setting.navigate_to_settings_page',
    'restore_volume_stream': 'device_setting.mutations.m01.device_setting.restore_volume_stream',
    'retrieve_setting_value': 'device_setting.mutations.m01.device_setting.retrieve_setting_value',
    'silence_volume_stream': 'device_setting.mutations.m01.device_setting.silence_volume_stream',
}
