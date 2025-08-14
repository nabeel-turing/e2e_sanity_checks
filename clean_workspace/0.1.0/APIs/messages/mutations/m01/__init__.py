from .messages import dispatch_sms_mms_message, notify_recipient_lookup_failure, present_recipient_options, prompt_for_message_content, stage_message_for_sending

_function_map = {
    'dispatch_sms_mms_message': 'messages.mutations.m01.messages.dispatch_sms_mms_message',
    'notify_recipient_lookup_failure': 'messages.mutations.m01.messages.notify_recipient_lookup_failure',
    'present_recipient_options': 'messages.mutations.m01.messages.present_recipient_options',
    'prompt_for_message_content': 'messages.mutations.m01.messages.prompt_for_message_content',
    'stage_message_for_sending': 'messages.mutations.m01.messages.stage_message_for_sending',
}
