from .devices import discover_entities_by_domain, fetch_entity_status, find_device_id_from_friendly_name, retrieve_full_device_data, set_or_cycle_device_state, update_entity_attributes

_function_map = {
    'discover_entities_by_domain': 'home_assistant.mutations.m01.devices.discover_entities_by_domain',
    'fetch_entity_status': 'home_assistant.mutations.m01.devices.fetch_entity_status',
    'find_device_id_from_friendly_name': 'home_assistant.mutations.m01.devices.find_device_id_from_friendly_name',
    'retrieve_full_device_data': 'home_assistant.mutations.m01.devices.retrieve_full_device_data',
    'set_or_cycle_device_state': 'home_assistant.mutations.m01.devices.set_or_cycle_device_state',
    'update_entity_attributes': 'home_assistant.mutations.m01.devices.update_entity_attributes',
}
