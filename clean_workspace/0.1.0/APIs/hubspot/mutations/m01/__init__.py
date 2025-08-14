from .Campaigns import fetch_campaign_details_by_id, launch_new_marketing_initiative, revise_marketing_initiative, search_for_marketing_campaigns, shelve_marketing_initiative
from .FormGlobalEvents import establish_global_form_event_webhook, list_global_form_subscription_definitions, remove_global_form_event_webhook, retrieve_global_form_event_webhooks, toggle_global_form_event_webhook
from .Forms import archive_web_form, build_new_web_form, edit_existing_form, find_form_by_identifier, retrieve_marketing_forms
from .MarketingEmails import compose_new_promotional_email, duplicate_promotional_email, erase_promotional_email, modify_promotional_email_content, retrieve_promotional_email_by_id
from .MarketingEvents import fetch_marketing_event_by_external_id, list_all_marketing_events, list_event_attendees, modify_registered_marketing_event, register_external_marketing_event, remove_attendee_from_event, remove_external_marketing_event, upsert_event_attendee_record, void_marketing_event
from .SingleSend import dispatch_templated_transactional_email
from .Templates import add_new_coded_template, fetch_template_by_identifier, list_all_design_templates, mark_template_as_deleted, modify_template_by_identifier, recover_archived_template
from .TransactionalEmails import dispatch_adhoc_transactional_email

_function_map = {
    'add_new_coded_template': 'hubspot.mutations.m01.Templates.add_new_coded_template',
    'archive_web_form': 'hubspot.mutations.m01.Forms.archive_web_form',
    'build_new_web_form': 'hubspot.mutations.m01.Forms.build_new_web_form',
    'compose_new_promotional_email': 'hubspot.mutations.m01.MarketingEmails.compose_new_promotional_email',
    'dispatch_adhoc_transactional_email': 'hubspot.mutations.m01.TransactionalEmails.dispatch_adhoc_transactional_email',
    'dispatch_templated_transactional_email': 'hubspot.mutations.m01.SingleSend.dispatch_templated_transactional_email',
    'duplicate_promotional_email': 'hubspot.mutations.m01.MarketingEmails.duplicate_promotional_email',
    'edit_existing_form': 'hubspot.mutations.m01.Forms.edit_existing_form',
    'erase_promotional_email': 'hubspot.mutations.m01.MarketingEmails.erase_promotional_email',
    'establish_global_form_event_webhook': 'hubspot.mutations.m01.FormGlobalEvents.establish_global_form_event_webhook',
    'fetch_campaign_details_by_id': 'hubspot.mutations.m01.Campaigns.fetch_campaign_details_by_id',
    'fetch_marketing_event_by_external_id': 'hubspot.mutations.m01.MarketingEvents.fetch_marketing_event_by_external_id',
    'fetch_template_by_identifier': 'hubspot.mutations.m01.Templates.fetch_template_by_identifier',
    'find_form_by_identifier': 'hubspot.mutations.m01.Forms.find_form_by_identifier',
    'launch_new_marketing_initiative': 'hubspot.mutations.m01.Campaigns.launch_new_marketing_initiative',
    'list_all_design_templates': 'hubspot.mutations.m01.Templates.list_all_design_templates',
    'list_all_marketing_events': 'hubspot.mutations.m01.MarketingEvents.list_all_marketing_events',
    'list_event_attendees': 'hubspot.mutations.m01.MarketingEvents.list_event_attendees',
    'list_global_form_subscription_definitions': 'hubspot.mutations.m01.FormGlobalEvents.list_global_form_subscription_definitions',
    'mark_template_as_deleted': 'hubspot.mutations.m01.Templates.mark_template_as_deleted',
    'modify_promotional_email_content': 'hubspot.mutations.m01.MarketingEmails.modify_promotional_email_content',
    'modify_registered_marketing_event': 'hubspot.mutations.m01.MarketingEvents.modify_registered_marketing_event',
    'modify_template_by_identifier': 'hubspot.mutations.m01.Templates.modify_template_by_identifier',
    'recover_archived_template': 'hubspot.mutations.m01.Templates.recover_archived_template',
    'register_external_marketing_event': 'hubspot.mutations.m01.MarketingEvents.register_external_marketing_event',
    'remove_attendee_from_event': 'hubspot.mutations.m01.MarketingEvents.remove_attendee_from_event',
    'remove_external_marketing_event': 'hubspot.mutations.m01.MarketingEvents.remove_external_marketing_event',
    'remove_global_form_event_webhook': 'hubspot.mutations.m01.FormGlobalEvents.remove_global_form_event_webhook',
    'retrieve_global_form_event_webhooks': 'hubspot.mutations.m01.FormGlobalEvents.retrieve_global_form_event_webhooks',
    'retrieve_marketing_forms': 'hubspot.mutations.m01.Forms.retrieve_marketing_forms',
    'retrieve_promotional_email_by_id': 'hubspot.mutations.m01.MarketingEmails.retrieve_promotional_email_by_id',
    'revise_marketing_initiative': 'hubspot.mutations.m01.Campaigns.revise_marketing_initiative',
    'search_for_marketing_campaigns': 'hubspot.mutations.m01.Campaigns.search_for_marketing_campaigns',
    'shelve_marketing_initiative': 'hubspot.mutations.m01.Campaigns.shelve_marketing_initiative',
    'toggle_global_form_event_webhook': 'hubspot.mutations.m01.FormGlobalEvents.toggle_global_form_event_webhook',
    'upsert_event_attendee_record': 'hubspot.mutations.m01.MarketingEvents.upsert_event_attendee_record',
    'void_marketing_event': 'hubspot.mutations.m01.MarketingEvents.void_marketing_event',
}
