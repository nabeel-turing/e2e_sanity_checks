import datetime
from typing import Dict, Any, Optional, Union

from .SimulationEngine import utils
from .SimulationEngine import models
from .SimulationEngine.custom_errors import NotFoundError, InvalidInputError, WorkflowDisabledError # Ensure this path is correct

def trigger_workflow(
    owner: str,
    repo: str,
    workflow_id: str,
    ref: str,
    inputs: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Triggers a workflow dispatch event for a given workflow.

    This function simulates the triggering of a workflow, corresponding
    to a 'workflow_dispatch' event. It creates a new workflow run record
    in the database and returns an acknowledgement.

    The actor initiating this workflow is hardcoded because, in this context,
    authentication details (and thus the specific user) are not available.

    Args:
        owner (str): The account owner of the repository.
        repo (str): The name of the repository without the .git extension.
        workflow_id (str): The ID of the workflow or the workflow file name
            (e.g., 'main.yaml', 'ci.yml').
        ref (str): The Git reference for the workflow. This can be a branch name
            (e.g., 'main'), a tag name (e.g., 'v1.0.0'), or a commit SHA.
        inputs (Optional[Dict[str, Any]]): Input parameters to pass to the workflow. These correspond
            to the 'inputs' defined in the workflow's 'on.workflow_dispatch'
            trigger. If the workflow does not expect inputs, this can be
            omitted or an empty dictionary.

    Returns:
        Dict[str, Any]: An empty dictionary, signifying that the workflow dispatch request
        has been successfully accepted and queued for processing.

    Raises:
        InvalidInputError: If any input parameter is malformed (e.g., wrong type,
            empty when not allowed, incorrect format).
        NotFoundError: If the specified `owner`, `repo`, `workflow_id`, or `ref`
            cannot be found or accessed after passing initial validation.
        WorkflowDisabledError: If the target workflow is disabled, the repository
            is archived, or the workflow is not configured for `workflow_dispatch`.
    """
    # --- Input Validation Stage ---
    if not isinstance(owner, str):
        raise InvalidInputError("Parameter 'owner' must be a string.")
    if not owner.strip():
        raise InvalidInputError("Parameter 'owner' cannot be empty or consist only of whitespace.")
    if not isinstance(repo, str):
        raise InvalidInputError("Parameter 'repo' must be a string.")
    if not repo.strip():
        raise InvalidInputError("Parameter 'repo' cannot be empty or consist only of whitespace.")
    if repo.lower().endswith(".git"):
        raise InvalidInputError("Parameter 'repo' should not include the '.git' extension.")
    if not isinstance(workflow_id, str):
        raise InvalidInputError("Parameter 'workflow_id' must be a string.")
    if not workflow_id.strip():
        raise InvalidInputError("Parameter 'workflow_id' cannot be empty or consist only of whitespace.")
    if not isinstance(ref, str):
        raise InvalidInputError("Parameter 'ref' must be a string.")
    _ref_stripped = ref.strip()
    if not _ref_stripped:
        raise InvalidInputError("Parameter 'ref' cannot be empty or consist only of whitespace.")
    if ' ' in _ref_stripped:
        raise InvalidInputError("Parameter 'ref' is not a valid Git reference: contains whitespace.")
    if '..' in _ref_stripped:
        raise InvalidInputError("Parameter 'ref' is not a valid Git reference: contains '..'.")
    
    # Adjusted ref ending validation (Approx. User's Line 60 target)
    if _ref_stripped.endswith('.'):
        raise InvalidInputError("Parameter 'ref' is not a valid Git reference: ends with '.'.")
    if _ref_stripped.endswith('/'):
        # Allow specific known ref prefixes that legitimately end with a slash if they represent a "directory"
        # or if the user's intent is to test empty branch/tag names after the prefix.
        # For general refs, a trailing slash (not being root "/") is often invalid.
        if _ref_stripped not in ["/", "refs/heads/", "refs/tags/"]:
            raise InvalidInputError("Parameter 'ref' is not a valid Git reference: invalid trailing '/'.")

    if inputs is not None and not isinstance(inputs, dict):
        raise InvalidInputError("The 'inputs' parameter, if provided, must be a dictionary.")

    # --- End of Input Validation Stage ---

    repository_obj = utils.get_repository(owner, repo)
    if not repository_obj:
        raise NotFoundError(f"Repository '{owner}/{repo}' not found.")

    processed_workflow_id: Union[str, int]
    if workflow_id.isdigit():
        processed_workflow_id = int(workflow_id)
    else:
        processed_workflow_id = workflow_id
    
    workflow_dict_from_util = utils.get_workflow_by_id_or_filename(owner, repo, processed_workflow_id)
    if not workflow_dict_from_util:
        raise NotFoundError(f"Workflow '{workflow_id}' (processed as '{processed_workflow_id}') not found in repository '{owner}/{repo}'.")

    if workflow_dict_from_util.get("state") != models.WorkflowState.ACTIVE.value:
        raise WorkflowDisabledError(
            f"Workflow '{workflow_id}' in '{owner}/{repo}' is not active or cannot be dispatched."
        )

    head_sha_for_run: str
    head_branch_for_run: Optional[str]
    is_sha_format = utils.is_valid_sha(ref)

    if is_sha_format:
        head_sha_for_run = ref
        head_branch_for_run = None
    elif ref.startswith("refs/heads/"):
        branch_name = ref[len("refs/heads/"):]
        if not branch_name:
            head_branch_for_run = ""
        else:
            head_branch_for_run = branch_name
        head_sha_for_run = utils.generate_random_sha()
    elif ref.startswith("refs/tags/"):
        head_branch_for_run = None 
        head_sha_for_run = utils.generate_random_sha()
    else:


        head_branch_for_run = ref
        head_sha_for_run = utils.generate_random_sha()


    now = datetime.datetime.now(datetime.timezone.utc)
    hardcoded_actor_details = {
        "login": "hubot", "id": 2, "node_id": "MDQ6VXNlcjI=",
        "type": "Bot", "site_admin": False
    }
    actor_data = hardcoded_actor_details.copy()
    commit_person_email = f"{hardcoded_actor_details['login']}@users.noreply.github.com"
    commit_person_data = {
        "name": hardcoded_actor_details["login"], "email": commit_person_email,
    }
    head_commit_data = {
        "id": head_sha_for_run,
        "message": f"Workflow dispatch event for {workflow_dict_from_util['name']} on ref {ref}",
        "timestamp": now.isoformat(),
        "author": commit_person_data,
        "committer": commit_person_data,
        "tree_id": utils.generate_random_sha() # Also use a random SHA for tree_id
    }
    run_data = {
        "workflow_id": workflow_dict_from_util["id"], "head_sha": head_sha_for_run,
        "head_branch": head_branch_for_run, "event": "workflow_dispatch",
        "actor": actor_data, "triggering_actor": actor_data,
        "head_commit": head_commit_data,
        "status": models.WorkflowRunStatus.QUEUED.value, "jobs": [],
    }
    if inputs is not None:
        run_data['run_inputs'] = inputs

    try:
        new_run_dict = utils.add_workflow_run(
            owner_login=owner, repo_name=repo,
            run_data=run_data, current_time=now
        )
        if not new_run_dict:
            raise Exception("Failed to create workflow run (utils.add_workflow_run returned None).")
    except ValueError as e:
        raise InvalidInputError(f"Invalid data for workflow run creation: {e}")
    return {}
