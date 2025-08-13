# File: orchestrator.py

import os
import shutil
import sys
import argparse
from datetime import datetime
import docker
from pathlib import Path
from typing import List, Dict

import pandas as pd

# --- Configuration ---
DOCKER_IMAGE = "sanity-runner"  # Name of the image built from your Dockerfile

# --- Host Machine Directory Setup ---
PROJECT_ROOT = Path(__file__).parent.resolve()
# NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
CLEAN_WORKSPACE_DIR = PROJECT_ROOT / "clean_workspace"
PARENT_LOG_DIR = PROJECT_ROOT / "execution_logs"
SERVICE_ACCOUNT_FILE = PROJECT_ROOT / "turing-delivery-g-ga-e36eb2300714.json"

TASK_FILE_PATH = PROJECT_ROOT / "execution_configs.csv"
RESULTS_DIR = PROJECT_ROOT / "results"

def _prepare_run_directories(run_name: str) -> (Path, Path):
    """Creates and returns the unique log directory for this run."""
    print("\n--- Step 2: Preparing Host Directories ---")
    run_log_dir = PARENT_LOG_DIR / run_name
    if run_log_dir.exists():
        raise FileExistsError(
            f"A log directory for '{run_name}' already exists. Please use a new run-name."
        )
    run_log_dir.mkdir(parents=True)
    print(f"✅ Created log directory for this run at: {run_log_dir}")

    run_results_dir = RESULTS_DIR / run_name
    if run_results_dir.exists():
        raise FileExistsError(
            f"A result directory for '{run_results_dir}' already exists. Please use a new run-name."
        )
    run_results_dir.mkdir(parents=True)
    print(f"✅ Created result directory for this run at: {run_results_dir}")

    return run_log_dir, run_results_dir

def _validate_host_environment() -> docker.DockerClient:
    """Checks for Docker and service account file, returns an initialized client."""
    print("--- Step 1: Validating Host Environment ---")
    if not SERVICE_ACCOUNT_FILE.exists():
        raise FileNotFoundError(
            f"Service account key not found at: {SERVICE_ACCOUNT_FILE}"
        )

    try:
        client = docker.from_env()
        client.ping()
        print("✅ Docker client connected.")
        return client
    except Exception as e:
        raise ConnectionError(
            f"Could not connect to Docker. Is the Docker daemon running? Error: {e}"
        )

def _launch_containers(
    client: docker.DockerClient,
    run_name: str,
    run_log_dir: Path,
    run_results_dir: Path,
    run_identifiers: list[str]
) -> List[Dict]:
    """Launches a container for each batch and returns a list of container objects."""
    print("\n--- Step 4: Launching Containers in Parallel ---")
    running_containers = []
    for i, run_id in enumerate(run_identifiers):
        api_version  = run_id.split('_')[0]
        container_id = i
        container_name = f"{run_name}-{container_id}"

        print(
            f"  -> Launching container '{container_name}' for batch {container_id}..."
        )
        environment = {
            # "EXECUTION_MODE": mode,
            "CONTAINER_ID": str(container_id),
            "GOOGLE_APPLICATION_CREDENTIALS": "/secrets/gcp_key.json",
        }
        volumes = {
            # str(NOTEBOOKS_DIR): {"bind": "/notebooks", "mode": "ro"},
            str(CLEAN_WORKSPACE_DIR / api_version): {"bind": f"/clean_workspace", "mode": "ro"},
            str(run_log_dir): {"bind": "/logs", "mode": "rw"},
            str(run_results_dir): {"bind": "/results", "mode": "rw"},
            str(TASK_FILE_PATH): {"bind": "/execution_configs.csv", "mode": "rw"},
            # str(OUTPUT_JSONS): {"bind": "/outputs/result_jsons", "mode": "rw"},
            str(SERVICE_ACCOUNT_FILE): {"bind": "/secrets/gcp_key.json", "mode": "ro"},
        }
        # print(str(CLEAN_WORKSPACE_DIR / api_version))
        entry_point_script = "sanity_runner_with_download.py"
        # entry_point_script = "docker_test.py"

        command = ["python3", entry_point_script, run_id]
        # print(command)
        # print(volumes)
        container = client.containers.run(
            DOCKER_IMAGE,
            command=command,
            environment=environment,
            volumes=volumes,
            name=container_name,
            detach=True,
            remove=False,
        )
        running_containers.append({"name": container_name, "container": container})
    return running_containers


def _wait_for_containers(run_log_dir: Path, running_containers: List[Dict]):
    """Waits for containers to finish and saves their stdout logs."""
    print("\n--- Step 5: Waiting for All Containers to Finish ---")
    for item in running_containers:
        container = item["container"]
        name = item["name"]
        result = container.wait()
        exit_code = result["StatusCode"]
        status = "✅ SUCCESS" if exit_code == 0 else "❌ FAILED"
        print(
            f"  -> {status} | Container '{name}' finished with exit code {exit_code}."
        )
        # container_stdout_log = run_log_dir / f"{name}_stdout.log"
        # with open(container_stdout_log, "w") as f:
        #     f.write(container.logs().decode("utf-8"))
        container.remove()


def run_orchestration(run_name: str, run_identifiers: list[str]) -> Path:
    """
    Main entry point to run the entire notebook orchestration process.

    Args:
        run_name: A unique name for this execution run.
        mode: Execution mode, 'E2E' or 'SKIP_SETUP'.
        notebooks_per_batch: Number of notebooks to run sequentially per container.

    Returns:
        The path to the log directory for this run.
    """
    client = _validate_host_environment()
    run_log_dir, run_results_dir = _prepare_run_directories(run_name)

    # try:
    # num_batches = _create_task_batches(run_log_dir, notebooks_per_batch)
    # num_batches = 3
    # if num_batches > 0:
    running_containers = _launch_containers(
        client,
        run_name,
        run_log_dir,
        run_results_dir,
        run_identifiers,
    )
    _wait_for_containers(run_log_dir, running_containers)
    print("\n--- Orchestration Complete ---")
    print(f"📄 All results and logs are stored in: {run_log_dir}")
    return run_log_dir


if __name__ == "__main__":
    
    run_config_df = pd.read_csv('execution_configs.csv')
    run_identifiers = list(set(run_config_df['batch_id']))

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_name = f"sanity_check_{timestamp}"
        run_orchestration(run_name, run_identifiers)
    except (FileNotFoundError, FileExistsError, ConnectionError) as e:
        print(f"\n❌ A critical error occurred: {e}")
