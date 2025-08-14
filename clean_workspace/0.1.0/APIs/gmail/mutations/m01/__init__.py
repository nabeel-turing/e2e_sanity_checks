from .Users.Drafts import discard_draft_message, dispatch_draft_message, enumerate_draft_messages, modify_existing_draft, retrieve_draft_message, save_new_draft_message
from .Users.History import get_mailbox_change_history
from .Users.Labels import add_new_label, get_all_user_labels, modify_existing_label, partially_update_label, remove_user_label, retrieve_label_details
from .Users.Messages.Attachments import retrieve_attachment_data
from .Users.Messages.__init__ import bulk_erase_emails, bulk_update_email_tags, dispatch_email, fetch_email_by_id, ingest_raw_email, inject_composed_email, move_email_to_trash, permanently_erase_email, restore_email_from_trash, search_mailbox_for_emails, update_email_tags
from .Users.Settings.AutoForwarding import fetch_forwarding_config, modify_forwarding_config
from .Users.Settings.Imap import fetch_imap_configuration, modify_imap_configuration
from .Users.Settings.Language import fetch_display_language, set_display_language
from .Users.Settings.Pop import fetch_pop_configuration, modify_pop_configuration
from .Users.Settings.SendAs.SmimeInfo import add_new_smime_cert_to_alias, enumerate_alias_smime_certs, make_smime_cert_default_for_alias, modify_smime_cert_for_alias, partially_update_smime_cert, remove_smime_cert_from_alias, retrieve_smime_cert_by_id
from .Users.Settings.SendAs.__init__ import confirm_sender_identity_ownership, get_all_sender_identities, modify_existing_sender_identity, partially_update_sender_identity, register_new_sender_identity, remove_sender_identity, retrieve_sender_identity
from .Users.Settings.Vacation import configure_vacation_responder, retrieve_vacation_responder_settings
from .Users.Threads import enumerate_user_threads, move_thread_to_trash, permanently_remove_thread, restore_thread_from_trash, retrieve_thread_details, update_thread_label_assignments
from .Users.__init__ import cancel_mailbox_subscription, fetch_account_summary, provision_new_account, subscribe_to_mailbox_events, verify_user_account_existence

_function_map = {
    'add_new_label': 'gmail.mutations.m01.Users.Labels.add_new_label',
    'add_new_smime_cert_to_alias': 'gmail.mutations.m01.Users.Settings.SendAs.SmimeInfo.add_new_smime_cert_to_alias',
    'bulk_erase_emails': 'gmail.mutations.m01.Users.Messages.__init__.bulk_erase_emails',
    'bulk_update_email_tags': 'gmail.mutations.m01.Users.Messages.__init__.bulk_update_email_tags',
    'cancel_mailbox_subscription': 'gmail.mutations.m01.Users.__init__.cancel_mailbox_subscription',
    'configure_vacation_responder': 'gmail.mutations.m01.Users.Settings.Vacation.configure_vacation_responder',
    'confirm_sender_identity_ownership': 'gmail.mutations.m01.Users.Settings.SendAs.__init__.confirm_sender_identity_ownership',
    'discard_draft_message': 'gmail.mutations.m01.Users.Drafts.discard_draft_message',
    'dispatch_draft_message': 'gmail.mutations.m01.Users.Drafts.dispatch_draft_message',
    'dispatch_email': 'gmail.mutations.m01.Users.Messages.__init__.dispatch_email',
    'enumerate_alias_smime_certs': 'gmail.mutations.m01.Users.Settings.SendAs.SmimeInfo.enumerate_alias_smime_certs',
    'enumerate_draft_messages': 'gmail.mutations.m01.Users.Drafts.enumerate_draft_messages',
    'enumerate_user_threads': 'gmail.mutations.m01.Users.Threads.enumerate_user_threads',
    'fetch_account_summary': 'gmail.mutations.m01.Users.__init__.fetch_account_summary',
    'fetch_display_language': 'gmail.mutations.m01.Users.Settings.Language.fetch_display_language',
    'fetch_email_by_id': 'gmail.mutations.m01.Users.Messages.__init__.fetch_email_by_id',
    'fetch_forwarding_config': 'gmail.mutations.m01.Users.Settings.AutoForwarding.fetch_forwarding_config',
    'fetch_imap_configuration': 'gmail.mutations.m01.Users.Settings.Imap.fetch_imap_configuration',
    'fetch_pop_configuration': 'gmail.mutations.m01.Users.Settings.Pop.fetch_pop_configuration',
    'get_all_sender_identities': 'gmail.mutations.m01.Users.Settings.SendAs.__init__.get_all_sender_identities',
    'get_all_user_labels': 'gmail.mutations.m01.Users.Labels.get_all_user_labels',
    'get_mailbox_change_history': 'gmail.mutations.m01.Users.History.get_mailbox_change_history',
    'ingest_raw_email': 'gmail.mutations.m01.Users.Messages.__init__.ingest_raw_email',
    'inject_composed_email': 'gmail.mutations.m01.Users.Messages.__init__.inject_composed_email',
    'make_smime_cert_default_for_alias': 'gmail.mutations.m01.Users.Settings.SendAs.SmimeInfo.make_smime_cert_default_for_alias',
    'modify_existing_draft': 'gmail.mutations.m01.Users.Drafts.modify_existing_draft',
    'modify_existing_label': 'gmail.mutations.m01.Users.Labels.modify_existing_label',
    'modify_existing_sender_identity': 'gmail.mutations.m01.Users.Settings.SendAs.__init__.modify_existing_sender_identity',
    'modify_forwarding_config': 'gmail.mutations.m01.Users.Settings.AutoForwarding.modify_forwarding_config',
    'modify_imap_configuration': 'gmail.mutations.m01.Users.Settings.Imap.modify_imap_configuration',
    'modify_pop_configuration': 'gmail.mutations.m01.Users.Settings.Pop.modify_pop_configuration',
    'modify_smime_cert_for_alias': 'gmail.mutations.m01.Users.Settings.SendAs.SmimeInfo.modify_smime_cert_for_alias',
    'move_email_to_trash': 'gmail.mutations.m01.Users.Messages.__init__.move_email_to_trash',
    'move_thread_to_trash': 'gmail.mutations.m01.Users.Threads.move_thread_to_trash',
    'partially_update_label': 'gmail.mutations.m01.Users.Labels.partially_update_label',
    'partially_update_sender_identity': 'gmail.mutations.m01.Users.Settings.SendAs.__init__.partially_update_sender_identity',
    'partially_update_smime_cert': 'gmail.mutations.m01.Users.Settings.SendAs.SmimeInfo.partially_update_smime_cert',
    'permanently_erase_email': 'gmail.mutations.m01.Users.Messages.__init__.permanently_erase_email',
    'permanently_remove_thread': 'gmail.mutations.m01.Users.Threads.permanently_remove_thread',
    'provision_new_account': 'gmail.mutations.m01.Users.__init__.provision_new_account',
    'register_new_sender_identity': 'gmail.mutations.m01.Users.Settings.SendAs.__init__.register_new_sender_identity',
    'remove_sender_identity': 'gmail.mutations.m01.Users.Settings.SendAs.__init__.remove_sender_identity',
    'remove_smime_cert_from_alias': 'gmail.mutations.m01.Users.Settings.SendAs.SmimeInfo.remove_smime_cert_from_alias',
    'remove_user_label': 'gmail.mutations.m01.Users.Labels.remove_user_label',
    'restore_email_from_trash': 'gmail.mutations.m01.Users.Messages.__init__.restore_email_from_trash',
    'restore_thread_from_trash': 'gmail.mutations.m01.Users.Threads.restore_thread_from_trash',
    'retrieve_attachment_data': 'gmail.mutations.m01.Users.Messages.Attachments.retrieve_attachment_data',
    'retrieve_draft_message': 'gmail.mutations.m01.Users.Drafts.retrieve_draft_message',
    'retrieve_label_details': 'gmail.mutations.m01.Users.Labels.retrieve_label_details',
    'retrieve_sender_identity': 'gmail.mutations.m01.Users.Settings.SendAs.__init__.retrieve_sender_identity',
    'retrieve_smime_cert_by_id': 'gmail.mutations.m01.Users.Settings.SendAs.SmimeInfo.retrieve_smime_cert_by_id',
    'retrieve_thread_details': 'gmail.mutations.m01.Users.Threads.retrieve_thread_details',
    'retrieve_vacation_responder_settings': 'gmail.mutations.m01.Users.Settings.Vacation.retrieve_vacation_responder_settings',
    'save_new_draft_message': 'gmail.mutations.m01.Users.Drafts.save_new_draft_message',
    'search_mailbox_for_emails': 'gmail.mutations.m01.Users.Messages.__init__.search_mailbox_for_emails',
    'set_display_language': 'gmail.mutations.m01.Users.Settings.Language.set_display_language',
    'subscribe_to_mailbox_events': 'gmail.mutations.m01.Users.__init__.subscribe_to_mailbox_events',
    'update_email_tags': 'gmail.mutations.m01.Users.Messages.__init__.update_email_tags',
    'update_thread_label_assignments': 'gmail.mutations.m01.Users.Threads.update_thread_label_assignments',
    'verify_user_account_existence': 'gmail.mutations.m01.Users.__init__.verify_user_account_existence',
}
