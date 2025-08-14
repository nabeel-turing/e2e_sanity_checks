from .branch import enumerate_project_branches, establish_development_branch, integrate_branch_into_production, remove_development_branch, revert_branch_to_migration_version, update_branch_with_production_changes
from .database import execute_schema_migration, fetch_installed_database_extensions, get_all_database_migrations, get_database_tables_by_schema, run_raw_sql_query
from .edge import enumerate_project_edge_functions, publish_edge_function_version
from .logs import retrieve_service_logs
from .organization import fetch_user_organizations, retrieve_organization_details
from .project import create_typescript_definitions_for_project, enumerate_all_user_projects, fetch_project_information, fetch_public_api_key, provision_supabase_project, reactivate_paused_project, retrieve_project_api_endpoint, suspend_project_activity

_function_map = {
    'create_typescript_definitions_for_project': 'supabase.mutations.m01.project.create_typescript_definitions_for_project',
    'enumerate_all_user_projects': 'supabase.mutations.m01.project.enumerate_all_user_projects',
    'enumerate_project_branches': 'supabase.mutations.m01.branch.enumerate_project_branches',
    'enumerate_project_edge_functions': 'supabase.mutations.m01.edge.enumerate_project_edge_functions',
    'establish_development_branch': 'supabase.mutations.m01.branch.establish_development_branch',
    'execute_schema_migration': 'supabase.mutations.m01.database.execute_schema_migration',
    'fetch_installed_database_extensions': 'supabase.mutations.m01.database.fetch_installed_database_extensions',
    'fetch_project_information': 'supabase.mutations.m01.project.fetch_project_information',
    'fetch_public_api_key': 'supabase.mutations.m01.project.fetch_public_api_key',
    'fetch_user_organizations': 'supabase.mutations.m01.organization.fetch_user_organizations',
    'get_all_database_migrations': 'supabase.mutations.m01.database.get_all_database_migrations',
    'get_database_tables_by_schema': 'supabase.mutations.m01.database.get_database_tables_by_schema',
    'integrate_branch_into_production': 'supabase.mutations.m01.branch.integrate_branch_into_production',
    'provision_supabase_project': 'supabase.mutations.m01.project.provision_supabase_project',
    'publish_edge_function_version': 'supabase.mutations.m01.edge.publish_edge_function_version',
    'reactivate_paused_project': 'supabase.mutations.m01.project.reactivate_paused_project',
    'remove_development_branch': 'supabase.mutations.m01.branch.remove_development_branch',
    'retrieve_organization_details': 'supabase.mutations.m01.organization.retrieve_organization_details',
    'retrieve_project_api_endpoint': 'supabase.mutations.m01.project.retrieve_project_api_endpoint',
    'retrieve_service_logs': 'supabase.mutations.m01.logs.retrieve_service_logs',
    'revert_branch_to_migration_version': 'supabase.mutations.m01.branch.revert_branch_to_migration_version',
    'run_raw_sql_query': 'supabase.mutations.m01.database.run_raw_sql_query',
    'suspend_project_activity': 'supabase.mutations.m01.project.suspend_project_activity',
    'update_branch_with_production_changes': 'supabase.mutations.m01.branch.update_branch_with_production_changes',
}
