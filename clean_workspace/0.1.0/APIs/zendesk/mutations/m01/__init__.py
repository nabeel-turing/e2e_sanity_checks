from .Attachments import generate_attachment_upload_token, inspect_attachment_metadata, purge_upload_by_token
from .Comments import fetch_ticket_conversation_history
from .Organizations import fetch_organization_by_id, get_all_organizations, modify_organization_details, register_new_organization, remove_organization_record
from .Search import execute_cross_platform_search
from .Tickets import amend_ticket_attributes, erase_ticket_entry, find_ticket_information, retrieve_all_tickets, retrieve_ticket_information, submit_new_support_request
from .Users import deactivate_user_profile, fetch_all_user_profiles, modify_user_account, provision_new_user, retrieve_user_by_id

_function_map = {
    'amend_ticket_attributes': 'zendesk.mutations.m01.Tickets.amend_ticket_attributes',
    'deactivate_user_profile': 'zendesk.mutations.m01.Users.deactivate_user_profile',
    'erase_ticket_entry': 'zendesk.mutations.m01.Tickets.erase_ticket_entry',
    'execute_cross_platform_search': 'zendesk.mutations.m01.Search.execute_cross_platform_search',
    'fetch_all_user_profiles': 'zendesk.mutations.m01.Users.fetch_all_user_profiles',
    'fetch_organization_by_id': 'zendesk.mutations.m01.Organizations.fetch_organization_by_id',
    'fetch_ticket_conversation_history': 'zendesk.mutations.m01.Comments.fetch_ticket_conversation_history',
    'find_ticket_information': 'zendesk.mutations.m01.Tickets.find_ticket_information',
    'generate_attachment_upload_token': 'zendesk.mutations.m01.Attachments.generate_attachment_upload_token',
    'get_all_organizations': 'zendesk.mutations.m01.Organizations.get_all_organizations',
    'inspect_attachment_metadata': 'zendesk.mutations.m01.Attachments.inspect_attachment_metadata',
    'modify_organization_details': 'zendesk.mutations.m01.Organizations.modify_organization_details',
    'modify_user_account': 'zendesk.mutations.m01.Users.modify_user_account',
    'provision_new_user': 'zendesk.mutations.m01.Users.provision_new_user',
    'purge_upload_by_token': 'zendesk.mutations.m01.Attachments.purge_upload_by_token',
    'register_new_organization': 'zendesk.mutations.m01.Organizations.register_new_organization',
    'remove_organization_record': 'zendesk.mutations.m01.Organizations.remove_organization_record',
    'retrieve_all_tickets': 'zendesk.mutations.m01.Tickets.retrieve_all_tickets',
    'retrieve_ticket_information': 'zendesk.mutations.m01.Tickets.retrieve_ticket_information',
    'retrieve_user_by_id': 'zendesk.mutations.m01.Users.retrieve_user_by_id',
    'submit_new_support_request': 'zendesk.mutations.m01.Tickets.submit_new_support_request',
}
