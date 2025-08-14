from .notifications import fetch_device_messages, prompt_for_incomplete_reply_info, send_notification_response

_function_map = {
    'fetch_device_messages': 'notifications.mutations.m01.notifications.fetch_device_messages',
    'prompt_for_incomplete_reply_info': 'notifications.mutations.m01.notifications.prompt_for_incomplete_reply_info',
    'send_notification_response': 'notifications.mutations.m01.notifications.send_notification_response',
}
