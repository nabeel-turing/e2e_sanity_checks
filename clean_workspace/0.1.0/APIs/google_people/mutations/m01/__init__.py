from .contact_groups import amend_contact_group_info, establish_new_contact_group, fetch_group_details, get_all_user_groups, remove_contact_group, update_group_membership
from .other_contacts import fetch_all_other_contacts, find_in_other_contacts, retrieve_unlinked_contact
from .people import add_new_person, browse_organization_directory, fetch_contact_list, fetch_organization_user, find_contacts_by_query, modify_existing_person, query_organization_directory, remove_person_record, retrieve_multiple_contacts, retrieve_person_by_id

_function_map = {
    'add_new_person': 'google_people.mutations.m01.people.add_new_person',
    'amend_contact_group_info': 'google_people.mutations.m01.contact_groups.amend_contact_group_info',
    'browse_organization_directory': 'google_people.mutations.m01.people.browse_organization_directory',
    'establish_new_contact_group': 'google_people.mutations.m01.contact_groups.establish_new_contact_group',
    'fetch_all_other_contacts': 'google_people.mutations.m01.other_contacts.fetch_all_other_contacts',
    'fetch_contact_list': 'google_people.mutations.m01.people.fetch_contact_list',
    'fetch_group_details': 'google_people.mutations.m01.contact_groups.fetch_group_details',
    'fetch_organization_user': 'google_people.mutations.m01.people.fetch_organization_user',
    'find_contacts_by_query': 'google_people.mutations.m01.people.find_contacts_by_query',
    'find_in_other_contacts': 'google_people.mutations.m01.other_contacts.find_in_other_contacts',
    'get_all_user_groups': 'google_people.mutations.m01.contact_groups.get_all_user_groups',
    'modify_existing_person': 'google_people.mutations.m01.people.modify_existing_person',
    'query_organization_directory': 'google_people.mutations.m01.people.query_organization_directory',
    'remove_contact_group': 'google_people.mutations.m01.contact_groups.remove_contact_group',
    'remove_person_record': 'google_people.mutations.m01.people.remove_person_record',
    'retrieve_multiple_contacts': 'google_people.mutations.m01.people.retrieve_multiple_contacts',
    'retrieve_person_by_id': 'google_people.mutations.m01.people.retrieve_person_by_id',
    'retrieve_unlinked_contact': 'google_people.mutations.m01.other_contacts.retrieve_unlinked_contact',
    'update_group_membership': 'google_people.mutations.m01.contact_groups.update_group_membership',
}
