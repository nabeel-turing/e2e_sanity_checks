# File: Dockerfile

# Use the official Python 3.11 slim variant as a parent image.
FROM python:3.11-slim

# Set the working directory in the container to /app.
WORKDIR /app

# ---- Base Dependencies ----
# First, copy and install the primary requirements for the execution engine.
# This includes papermill and the google auth libraries for the container itself.
COPY requirements.docker.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.docker.txt

# sudo apt-get install build-essential

# ---- Notebook-Specific Dependencies ----
# Next, copy and install the requirements specific to the APIs/tools used
# by the notebooks themselves. This layer only rebuilds if these specific
# dependencies change. We copy it to /tmp to keep the final /app dir clean.
# COPY requirements.txt /tmp/api_requirements.txt


RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y build-essential

COPY requirements.txt /tmp/api_requirements.txt
RUN pip install --no-cache-dir -r /tmp/api_requirements.txt
# ---- Runner Script ----
# Copy the runner script that contains the main execution logic.
# COPY runner.py .
# COPY sanity/ sanity/
# COPY sanity_runner.py .
# COPY docker_test.py .
COPY sanity_runner_with_download.py .

# -----------------------------------------------------------------------------
# RUNTIME ENVIRONMENT DOCUMENTATION
# -----------------------------------------------------------------------------
# The container expects the following to be configured at RUNTIME.
#
# Environment Variables:
#   - EXECUTION_MODE=E2E               (or SKIP_SETUP)
#   - GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcp_key.json
#   - CONTAINER_ID=0                   (or 1, 2, ...)
#
# Volume Mounts:
#   - /notebooks (Read-Only): Source .ipynb files.
#   - /clean_workspace (Read-Only): The "golden copy" of the workspace.
#   - /results (Read-Write): For output notebooks and logs.
#   - /secrets (Read-Only): For securely mounting the service-account.json.
# -----------------------------------------------------------------------------