from .ApplicationPropertiesApi import fetch_system_configuration_settings, modify_system_setting_by_identifier
from .ApplicationRoleApi import find_system_access_role_by_key, list_all_system_access_roles
from .AttachmentApi import fetch_file_attachment_details, get_ticket_file_attachments, remove_file_attachment, retrieve_attachment_binary_data, save_attachment_to_disk, upload_file_to_ticket
from .AvatarApi import resize_staged_profile_image, stage_profile_image, submit_profile_image
from .ComponentApi import add_project_module, fetch_module_by_identifier, modify_project_module_by_id, remove_module_by_identifier
from .DashboardApi import fetch_overview_panel_by_id, retrieve_all_overview_panels
from .FilterApi import get_saved_search_by_id, modify_saved_search_by_id, retrieve_all_saved_searches
from .GroupApi import establish_new_user_collection, fetch_user_collection_by_name, modify_user_collection_membership, remove_user_collection_by_name
from .GroupsPickerApi import search_collections_for_selector
from .IssueApi import batch_remove_tickets, delegate_ticket_to_person, execute_batch_ticket_actions, fetch_ticket_creation_schemas, find_ticket_by_unique_id, find_tickets_for_selection_ui, modify_ticket_details, register_new_ticket, remove_ticket_by_identifier
from .IssueLinkApi import establish_ticket_relationship
from .IssueLinkTypeApi import get_ticket_relationship_kind_by_id, list_all_ticket_relationship_kinds
from .IssueTypeApi import define_new_ticket_variety, find_ticket_variety_by_id, get_all_ticket_varieties
from .JqlApi import fetch_jql_auto_complete_data
from .LicenseValidatorApi import verify_product_license
from .MyPermissionsApi import check_active_user_privileges
from .MyPreferencesApi import adjust_active_user_settings, fetch_active_user_settings
from .PermissionSchemeApi import get_authorization_model_by_id, list_all_authorization_models
from .PermissionsApi import list_all_system_privileges
from .PriorityApi import find_urgency_level_by_id, list_all_urgency_levels
from .ProjectApi import fetch_workspace_icons_by_key, find_workspace_by_key, initialize_new_workspace, list_workspace_modules_by_key, remove_workspace_by_key, retrieve_all_workspaces
from .ProjectCategoryApi import fetch_project_classification_by_identifier, retrieve_all_project_classifications
from .ReindexApi import check_search_index_rebuild_progress, initiate_search_index_rebuild
from .ResolutionApi import find_outcome_type_by_id, retrieve_all_outcome_types
from .RoleApi import fetch_project_role_by_id, list_all_project_roles
from .SearchApi import query_tickets_with_jql
from .SecurityLevelApi import find_confidentiality_tier_by_id, list_all_confidentiality_tiers
from .ServerInfoApi import fetch_instance_details
from .SettingsApi import get_all_system_parameters
from .StatusApi import fetch_workflow_state_by_identifier, retrieve_all_workflow_states
from .StatusCategoryApi import fetch_state_group_by_identifier, retrieve_all_state_groups
from .UserApi import provision_new_account, remove_user_by_login_or_key, retrieve_user_by_login_or_id, search_for_accounts
from .UserAvatarsApi import retrieve_user_profile_images
from .VersionApi import fetch_release_by_identifier, get_release_ticket_statistics, register_new_release, remove_release_by_identifier
from .WebhookApi import list_all_event_listeners, register_or_find_event_listeners, remove_event_listeners_by_id
from .WorkflowApi import retrieve_all_process_flows

_function_map = {
    'add_project_module': 'jira.mutations.m01.ComponentApi.add_project_module',
    'adjust_active_user_settings': 'jira.mutations.m01.MyPreferencesApi.adjust_active_user_settings',
    'batch_remove_tickets': 'jira.mutations.m01.IssueApi.batch_remove_tickets',
    'check_active_user_privileges': 'jira.mutations.m01.MyPermissionsApi.check_active_user_privileges',
    'check_search_index_rebuild_progress': 'jira.mutations.m01.ReindexApi.check_search_index_rebuild_progress',
    'define_new_ticket_variety': 'jira.mutations.m01.IssueTypeApi.define_new_ticket_variety',
    'delegate_ticket_to_person': 'jira.mutations.m01.IssueApi.delegate_ticket_to_person',
    'establish_new_user_collection': 'jira.mutations.m01.GroupApi.establish_new_user_collection',
    'establish_ticket_relationship': 'jira.mutations.m01.IssueLinkApi.establish_ticket_relationship',
    'execute_batch_ticket_actions': 'jira.mutations.m01.IssueApi.execute_batch_ticket_actions',
    'fetch_active_user_settings': 'jira.mutations.m01.MyPreferencesApi.fetch_active_user_settings',
    'fetch_file_attachment_details': 'jira.mutations.m01.AttachmentApi.fetch_file_attachment_details',
    'fetch_instance_details': 'jira.mutations.m01.ServerInfoApi.fetch_instance_details',
    'fetch_jql_auto_complete_data': 'jira.mutations.m01.JqlApi.fetch_jql_auto_complete_data',
    'fetch_module_by_identifier': 'jira.mutations.m01.ComponentApi.fetch_module_by_identifier',
    'fetch_overview_panel_by_id': 'jira.mutations.m01.DashboardApi.fetch_overview_panel_by_id',
    'fetch_project_classification_by_identifier': 'jira.mutations.m01.ProjectCategoryApi.fetch_project_classification_by_identifier',
    'fetch_project_role_by_id': 'jira.mutations.m01.RoleApi.fetch_project_role_by_id',
    'fetch_release_by_identifier': 'jira.mutations.m01.VersionApi.fetch_release_by_identifier',
    'fetch_state_group_by_identifier': 'jira.mutations.m01.StatusCategoryApi.fetch_state_group_by_identifier',
    'fetch_system_configuration_settings': 'jira.mutations.m01.ApplicationPropertiesApi.fetch_system_configuration_settings',
    'fetch_ticket_creation_schemas': 'jira.mutations.m01.IssueApi.fetch_ticket_creation_schemas',
    'fetch_user_collection_by_name': 'jira.mutations.m01.GroupApi.fetch_user_collection_by_name',
    'fetch_workflow_state_by_identifier': 'jira.mutations.m01.StatusApi.fetch_workflow_state_by_identifier',
    'fetch_workspace_icons_by_key': 'jira.mutations.m01.ProjectApi.fetch_workspace_icons_by_key',
    'find_confidentiality_tier_by_id': 'jira.mutations.m01.SecurityLevelApi.find_confidentiality_tier_by_id',
    'find_outcome_type_by_id': 'jira.mutations.m01.ResolutionApi.find_outcome_type_by_id',
    'find_system_access_role_by_key': 'jira.mutations.m01.ApplicationRoleApi.find_system_access_role_by_key',
    'find_ticket_by_unique_id': 'jira.mutations.m01.IssueApi.find_ticket_by_unique_id',
    'find_ticket_variety_by_id': 'jira.mutations.m01.IssueTypeApi.find_ticket_variety_by_id',
    'find_tickets_for_selection_ui': 'jira.mutations.m01.IssueApi.find_tickets_for_selection_ui',
    'find_urgency_level_by_id': 'jira.mutations.m01.PriorityApi.find_urgency_level_by_id',
    'find_workspace_by_key': 'jira.mutations.m01.ProjectApi.find_workspace_by_key',
    'get_all_system_parameters': 'jira.mutations.m01.SettingsApi.get_all_system_parameters',
    'get_all_ticket_varieties': 'jira.mutations.m01.IssueTypeApi.get_all_ticket_varieties',
    'get_authorization_model_by_id': 'jira.mutations.m01.PermissionSchemeApi.get_authorization_model_by_id',
    'get_release_ticket_statistics': 'jira.mutations.m01.VersionApi.get_release_ticket_statistics',
    'get_saved_search_by_id': 'jira.mutations.m01.FilterApi.get_saved_search_by_id',
    'get_ticket_file_attachments': 'jira.mutations.m01.AttachmentApi.get_ticket_file_attachments',
    'get_ticket_relationship_kind_by_id': 'jira.mutations.m01.IssueLinkTypeApi.get_ticket_relationship_kind_by_id',
    'initialize_new_workspace': 'jira.mutations.m01.ProjectApi.initialize_new_workspace',
    'initiate_search_index_rebuild': 'jira.mutations.m01.ReindexApi.initiate_search_index_rebuild',
    'list_all_authorization_models': 'jira.mutations.m01.PermissionSchemeApi.list_all_authorization_models',
    'list_all_confidentiality_tiers': 'jira.mutations.m01.SecurityLevelApi.list_all_confidentiality_tiers',
    'list_all_event_listeners': 'jira.mutations.m01.WebhookApi.list_all_event_listeners',
    'list_all_project_roles': 'jira.mutations.m01.RoleApi.list_all_project_roles',
    'list_all_system_access_roles': 'jira.mutations.m01.ApplicationRoleApi.list_all_system_access_roles',
    'list_all_system_privileges': 'jira.mutations.m01.PermissionsApi.list_all_system_privileges',
    'list_all_ticket_relationship_kinds': 'jira.mutations.m01.IssueLinkTypeApi.list_all_ticket_relationship_kinds',
    'list_all_urgency_levels': 'jira.mutations.m01.PriorityApi.list_all_urgency_levels',
    'list_workspace_modules_by_key': 'jira.mutations.m01.ProjectApi.list_workspace_modules_by_key',
    'modify_project_module_by_id': 'jira.mutations.m01.ComponentApi.modify_project_module_by_id',
    'modify_saved_search_by_id': 'jira.mutations.m01.FilterApi.modify_saved_search_by_id',
    'modify_system_setting_by_identifier': 'jira.mutations.m01.ApplicationPropertiesApi.modify_system_setting_by_identifier',
    'modify_ticket_details': 'jira.mutations.m01.IssueApi.modify_ticket_details',
    'modify_user_collection_membership': 'jira.mutations.m01.GroupApi.modify_user_collection_membership',
    'provision_new_account': 'jira.mutations.m01.UserApi.provision_new_account',
    'query_tickets_with_jql': 'jira.mutations.m01.SearchApi.query_tickets_with_jql',
    'register_new_release': 'jira.mutations.m01.VersionApi.register_new_release',
    'register_new_ticket': 'jira.mutations.m01.IssueApi.register_new_ticket',
    'register_or_find_event_listeners': 'jira.mutations.m01.WebhookApi.register_or_find_event_listeners',
    'remove_event_listeners_by_id': 'jira.mutations.m01.WebhookApi.remove_event_listeners_by_id',
    'remove_file_attachment': 'jira.mutations.m01.AttachmentApi.remove_file_attachment',
    'remove_module_by_identifier': 'jira.mutations.m01.ComponentApi.remove_module_by_identifier',
    'remove_release_by_identifier': 'jira.mutations.m01.VersionApi.remove_release_by_identifier',
    'remove_ticket_by_identifier': 'jira.mutations.m01.IssueApi.remove_ticket_by_identifier',
    'remove_user_by_login_or_key': 'jira.mutations.m01.UserApi.remove_user_by_login_or_key',
    'remove_user_collection_by_name': 'jira.mutations.m01.GroupApi.remove_user_collection_by_name',
    'remove_workspace_by_key': 'jira.mutations.m01.ProjectApi.remove_workspace_by_key',
    'resize_staged_profile_image': 'jira.mutations.m01.AvatarApi.resize_staged_profile_image',
    'retrieve_all_outcome_types': 'jira.mutations.m01.ResolutionApi.retrieve_all_outcome_types',
    'retrieve_all_overview_panels': 'jira.mutations.m01.DashboardApi.retrieve_all_overview_panels',
    'retrieve_all_process_flows': 'jira.mutations.m01.WorkflowApi.retrieve_all_process_flows',
    'retrieve_all_project_classifications': 'jira.mutations.m01.ProjectCategoryApi.retrieve_all_project_classifications',
    'retrieve_all_saved_searches': 'jira.mutations.m01.FilterApi.retrieve_all_saved_searches',
    'retrieve_all_state_groups': 'jira.mutations.m01.StatusCategoryApi.retrieve_all_state_groups',
    'retrieve_all_workflow_states': 'jira.mutations.m01.StatusApi.retrieve_all_workflow_states',
    'retrieve_all_workspaces': 'jira.mutations.m01.ProjectApi.retrieve_all_workspaces',
    'retrieve_attachment_binary_data': 'jira.mutations.m01.AttachmentApi.retrieve_attachment_binary_data',
    'retrieve_user_by_login_or_id': 'jira.mutations.m01.UserApi.retrieve_user_by_login_or_id',
    'retrieve_user_profile_images': 'jira.mutations.m01.UserAvatarsApi.retrieve_user_profile_images',
    'save_attachment_to_disk': 'jira.mutations.m01.AttachmentApi.save_attachment_to_disk',
    'search_collections_for_selector': 'jira.mutations.m01.GroupsPickerApi.search_collections_for_selector',
    'search_for_accounts': 'jira.mutations.m01.UserApi.search_for_accounts',
    'stage_profile_image': 'jira.mutations.m01.AvatarApi.stage_profile_image',
    'submit_profile_image': 'jira.mutations.m01.AvatarApi.submit_profile_image',
    'upload_file_to_ticket': 'jira.mutations.m01.AttachmentApi.upload_file_to_ticket',
    'verify_product_license': 'jira.mutations.m01.LicenseValidatorApi.verify_product_license',
}
