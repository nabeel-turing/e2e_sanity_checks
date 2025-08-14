from .get_installed_apps_api import list_installed_applications
from .open_app_api import launch_application
from .open_camera_api import activate_camera
from .open_home_screen_api import navigate_to_device_home
from .open_url_api import access_website
from .open_websearch_api import search_the_web
from .power_off_device_api import show_power_down_menu
from .record_video_api import capture_video
from .restart_device_api import initiate_reboot_sequence
from .ring_phone_api import find_my_phone
from .take_photo_api import snap_picture
from .take_screenshot_api import capture_current_screen
from .turn_off_flashlight_api import disable_torch
from .turn_on_flashlight_api import enable_torch

_function_map = {
    'access_website': 'device_actions.mutations.m01.open_url_api.access_website',
    'activate_camera': 'device_actions.mutations.m01.open_camera_api.activate_camera',
    'capture_current_screen': 'device_actions.mutations.m01.take_screenshot_api.capture_current_screen',
    'capture_video': 'device_actions.mutations.m01.record_video_api.capture_video',
    'disable_torch': 'device_actions.mutations.m01.turn_off_flashlight_api.disable_torch',
    'enable_torch': 'device_actions.mutations.m01.turn_on_flashlight_api.enable_torch',
    'find_my_phone': 'device_actions.mutations.m01.ring_phone_api.find_my_phone',
    'initiate_reboot_sequence': 'device_actions.mutations.m01.restart_device_api.initiate_reboot_sequence',
    'launch_application': 'device_actions.mutations.m01.open_app_api.launch_application',
    'list_installed_applications': 'device_actions.mutations.m01.get_installed_apps_api.list_installed_applications',
    'navigate_to_device_home': 'device_actions.mutations.m01.open_home_screen_api.navigate_to_device_home',
    'search_the_web': 'device_actions.mutations.m01.open_websearch_api.search_the_web',
    'show_power_down_menu': 'device_actions.mutations.m01.power_off_device_api.show_power_down_menu',
    'snap_picture': 'device_actions.mutations.m01.take_photo_api.snap_picture',
}
