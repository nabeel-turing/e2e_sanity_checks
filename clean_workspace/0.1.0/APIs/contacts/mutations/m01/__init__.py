from .contacts import add_new_person, fetch_contact_list, fetch_organization_members, find_contacts_by_keyword, lookup_person_details, modify_contact_info, query_corporate_directory, remove_contact_entry, retrieve_interaction_contacts

_function_map = {
    'add_new_person': 'contacts.mutations.m01.contacts.add_new_person',
    'fetch_contact_list': 'contacts.mutations.m01.contacts.fetch_contact_list',
    'fetch_organization_members': 'contacts.mutations.m01.contacts.fetch_organization_members',
    'find_contacts_by_keyword': 'contacts.mutations.m01.contacts.find_contacts_by_keyword',
    'lookup_person_details': 'contacts.mutations.m01.contacts.lookup_person_details',
    'modify_contact_info': 'contacts.mutations.m01.contacts.modify_contact_info',
    'query_corporate_directory': 'contacts.mutations.m01.contacts.query_corporate_directory',
    'remove_contact_entry': 'contacts.mutations.m01.contacts.remove_contact_entry',
    'retrieve_interaction_contacts': 'contacts.mutations.m01.contacts.retrieve_interaction_contacts',
}
