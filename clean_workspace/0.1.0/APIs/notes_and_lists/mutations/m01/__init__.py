from .SimulationEngine.utils import find_entries
from .lists import append_items_to_list, make_new_list
from .notes_and_lists import add_text_to_note, broadcast_notes_and_lists, compose_new_note, display_all_entries, display_specific_items, modify_list_element, modify_note_content, remove_entries, remove_item_from_list, rename_entry, retrieve_entries, revert_last_action

_function_map = {
    'add_text_to_note': 'notes_and_lists.mutations.m01.notes_and_lists.add_text_to_note',
    'append_items_to_list': 'notes_and_lists.mutations.m01.lists.append_items_to_list',
    'broadcast_notes_and_lists': 'notes_and_lists.mutations.m01.notes_and_lists.broadcast_notes_and_lists',
    'compose_new_note': 'notes_and_lists.mutations.m01.notes_and_lists.compose_new_note',
    'display_all_entries': 'notes_and_lists.mutations.m01.notes_and_lists.display_all_entries',
    'display_specific_items': 'notes_and_lists.mutations.m01.notes_and_lists.display_specific_items',
    'find_entries': 'notes_and_lists.mutations.m01.SimulationEngine.utils.find_entries',
    'make_new_list': 'notes_and_lists.mutations.m01.lists.make_new_list',
    'modify_list_element': 'notes_and_lists.mutations.m01.notes_and_lists.modify_list_element',
    'modify_note_content': 'notes_and_lists.mutations.m01.notes_and_lists.modify_note_content',
    'remove_entries': 'notes_and_lists.mutations.m01.notes_and_lists.remove_entries',
    'remove_item_from_list': 'notes_and_lists.mutations.m01.notes_and_lists.remove_item_from_list',
    'rename_entry': 'notes_and_lists.mutations.m01.notes_and_lists.rename_entry',
    'retrieve_entries': 'notes_and_lists.mutations.m01.notes_and_lists.retrieve_entries',
    'revert_last_action': 'notes_and_lists.mutations.m01.notes_and_lists.revert_last_action',
}
