from .appconfig import delete_app_configuration_setting, enumerate_app_config_settings, fetch_all_app_config_accounts, remove_readonly_flag_from_app_config_setting, retrieve_app_config_setting_details, set_app_config_setting_to_readonly, upsert_app_configuration_value
from .cosmos import enumerate_cosmos_account_databases, fetch_subscription_cosmosdb_accounts, get_cosmos_database_containers, provision_cosmosdb_service_instance
from .keyvault import create_keyvault_crypto_key, enumerate_keys_in_keyvault, fetch_keyvault_key_details
from .loganalytics import enumerate_log_analytics_workspace_tables, get_all_log_analytics_workspaces, get_log_analytics_workspace_table_types
from .management import get_all_resource_groups, list_all_accessible_subscriptions
from .monitor import fetch_monitor_entity_health_state
from .storage import enumerate_storage_account_containers, enumerate_storage_account_tables, fetch_all_storage_accounts, get_all_blobs_in_storage_container, retrieve_blob_container_properties

_function_map = {
    'create_keyvault_crypto_key': 'azure.mutations.m01.keyvault.create_keyvault_crypto_key',
    'delete_app_configuration_setting': 'azure.mutations.m01.appconfig.delete_app_configuration_setting',
    'enumerate_app_config_settings': 'azure.mutations.m01.appconfig.enumerate_app_config_settings',
    'enumerate_cosmos_account_databases': 'azure.mutations.m01.cosmos.enumerate_cosmos_account_databases',
    'enumerate_keys_in_keyvault': 'azure.mutations.m01.keyvault.enumerate_keys_in_keyvault',
    'enumerate_log_analytics_workspace_tables': 'azure.mutations.m01.loganalytics.enumerate_log_analytics_workspace_tables',
    'enumerate_storage_account_containers': 'azure.mutations.m01.storage.enumerate_storage_account_containers',
    'enumerate_storage_account_tables': 'azure.mutations.m01.storage.enumerate_storage_account_tables',
    'fetch_all_app_config_accounts': 'azure.mutations.m01.appconfig.fetch_all_app_config_accounts',
    'fetch_all_storage_accounts': 'azure.mutations.m01.storage.fetch_all_storage_accounts',
    'fetch_keyvault_key_details': 'azure.mutations.m01.keyvault.fetch_keyvault_key_details',
    'fetch_monitor_entity_health_state': 'azure.mutations.m01.monitor.fetch_monitor_entity_health_state',
    'fetch_subscription_cosmosdb_accounts': 'azure.mutations.m01.cosmos.fetch_subscription_cosmosdb_accounts',
    'get_all_blobs_in_storage_container': 'azure.mutations.m01.storage.get_all_blobs_in_storage_container',
    'get_all_log_analytics_workspaces': 'azure.mutations.m01.loganalytics.get_all_log_analytics_workspaces',
    'get_all_resource_groups': 'azure.mutations.m01.management.get_all_resource_groups',
    'get_cosmos_database_containers': 'azure.mutations.m01.cosmos.get_cosmos_database_containers',
    'get_log_analytics_workspace_table_types': 'azure.mutations.m01.loganalytics.get_log_analytics_workspace_table_types',
    'list_all_accessible_subscriptions': 'azure.mutations.m01.management.list_all_accessible_subscriptions',
    'provision_cosmosdb_service_instance': 'azure.mutations.m01.cosmos.provision_cosmosdb_service_instance',
    'remove_readonly_flag_from_app_config_setting': 'azure.mutations.m01.appconfig.remove_readonly_flag_from_app_config_setting',
    'retrieve_app_config_setting_details': 'azure.mutations.m01.appconfig.retrieve_app_config_setting_details',
    'retrieve_blob_container_properties': 'azure.mutations.m01.storage.retrieve_blob_container_properties',
    'set_app_config_setting_to_readonly': 'azure.mutations.m01.appconfig.set_app_config_setting_to_readonly',
    'upsert_app_configuration_value': 'azure.mutations.m01.appconfig.upsert_app_configuration_value',
}
