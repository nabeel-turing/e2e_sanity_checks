from .calls import display_contact_selection_ui, generate_call_previews, initiate_phone_call, report_missing_recipient

_function_map = {
    'display_contact_selection_ui': 'phone.mutations.m01.calls.display_contact_selection_ui',
    'generate_call_previews': 'phone.mutations.m01.calls.generate_call_previews',
    'initiate_phone_call': 'phone.mutations.m01.calls.initiate_phone_call',
    'report_missing_recipient': 'phone.mutations.m01.calls.report_missing_recipient',
}
