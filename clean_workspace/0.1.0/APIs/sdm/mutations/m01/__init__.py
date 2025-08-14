from .devices.__init__ import catalog_authorized_devices, fetch_device_details, retrieve_triggered_events, send_device_instruction
from .structures.__init__ import enumerate_all_structures

_function_map = {
    'catalog_authorized_devices': 'sdm.mutations.m01.devices.__init__.catalog_authorized_devices',
    'enumerate_all_structures': 'sdm.mutations.m01.structures.__init__.enumerate_all_structures',
    'fetch_device_details': 'sdm.mutations.m01.devices.__init__.fetch_device_details',
    'retrieve_triggered_events': 'sdm.mutations.m01.devices.__init__.retrieve_triggered_events',
    'send_device_instruction': 'sdm.mutations.m01.devices.__init__.send_device_instruction',
}
