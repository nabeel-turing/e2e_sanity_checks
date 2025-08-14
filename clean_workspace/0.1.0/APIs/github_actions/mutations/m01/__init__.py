from .cancel_workflow_run_module import abort_workflow_execution
from .get_workflow_module import retrieve_workflow_details
from .get_workflow_run_jobs_module import list_jobs_for_workflow_execution
from .get_workflow_run_module import retrieve_workflow_execution_details
from .get_workflow_usage_module import fetch_workflow_billing_stats
from .list_workflow_runs_module import search_workflow_run_history
from .list_workflows_module import fetch_repository_workflows
from .rerun_workflow_module import re_execute_workflow_run
from .trigger_workflow_module import initiate_workflow_dispatch

_function_map = {
    'abort_workflow_execution': 'github_actions.mutations.m01.cancel_workflow_run_module.abort_workflow_execution',
    'fetch_repository_workflows': 'github_actions.mutations.m01.list_workflows_module.fetch_repository_workflows',
    'fetch_workflow_billing_stats': 'github_actions.mutations.m01.get_workflow_usage_module.fetch_workflow_billing_stats',
    'initiate_workflow_dispatch': 'github_actions.mutations.m01.trigger_workflow_module.initiate_workflow_dispatch',
    'list_jobs_for_workflow_execution': 'github_actions.mutations.m01.get_workflow_run_jobs_module.list_jobs_for_workflow_execution',
    're_execute_workflow_run': 'github_actions.mutations.m01.rerun_workflow_module.re_execute_workflow_run',
    'retrieve_workflow_details': 'github_actions.mutations.m01.get_workflow_module.retrieve_workflow_details',
    'retrieve_workflow_execution_details': 'github_actions.mutations.m01.get_workflow_run_module.retrieve_workflow_execution_details',
    'search_workflow_run_history': 'github_actions.mutations.m01.list_workflow_runs_module.search_workflow_run_history',
}
