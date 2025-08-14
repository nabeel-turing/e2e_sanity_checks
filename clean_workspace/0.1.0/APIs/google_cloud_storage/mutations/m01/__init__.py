from .Buckets import enumerate_project_buckets, erase_storage_bucket, finalize_bucket_retention_policy, get_bucket_physical_layout, modify_storage_container_properties, provision_new_storage_container, recover_bucket_from_soft_delete, replace_storage_container_configuration, retrieve_bucket_iam_policy, retrieve_bucket_information, start_bucket_relocation, update_bucket_iam_policy, verify_caller_bucket_permissions
from .Channels import cease_notification_channel_monitoring

_function_map = {
    'cease_notification_channel_monitoring': 'google_cloud_storage.mutations.m01.Channels.cease_notification_channel_monitoring',
    'enumerate_project_buckets': 'google_cloud_storage.mutations.m01.Buckets.enumerate_project_buckets',
    'erase_storage_bucket': 'google_cloud_storage.mutations.m01.Buckets.erase_storage_bucket',
    'finalize_bucket_retention_policy': 'google_cloud_storage.mutations.m01.Buckets.finalize_bucket_retention_policy',
    'get_bucket_physical_layout': 'google_cloud_storage.mutations.m01.Buckets.get_bucket_physical_layout',
    'modify_storage_container_properties': 'google_cloud_storage.mutations.m01.Buckets.modify_storage_container_properties',
    'provision_new_storage_container': 'google_cloud_storage.mutations.m01.Buckets.provision_new_storage_container',
    'recover_bucket_from_soft_delete': 'google_cloud_storage.mutations.m01.Buckets.recover_bucket_from_soft_delete',
    'replace_storage_container_configuration': 'google_cloud_storage.mutations.m01.Buckets.replace_storage_container_configuration',
    'retrieve_bucket_iam_policy': 'google_cloud_storage.mutations.m01.Buckets.retrieve_bucket_iam_policy',
    'retrieve_bucket_information': 'google_cloud_storage.mutations.m01.Buckets.retrieve_bucket_information',
    'start_bucket_relocation': 'google_cloud_storage.mutations.m01.Buckets.start_bucket_relocation',
    'update_bucket_iam_policy': 'google_cloud_storage.mutations.m01.Buckets.update_bucket_iam_policy',
    'verify_caller_bucket_permissions': 'google_cloud_storage.mutations.m01.Buckets.verify_caller_bucket_permissions',
}
