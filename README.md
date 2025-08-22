# Base Configs

1. Create a venv and install the requirement in `requirements.txt`

2. Make sure you have a service account file in the project root. Update the name `SERVICE_ACCOUNT_FILE` in `sanity_orchestrator_with_download.py` & in `docker_orchestrator_colab.ipynb` (in Setup and Auth section)

3. Adjust the max docker containers to run in parallel in `Create Batches and Configuration Files for Docker Runs` section.

4. Run the notebook `download_apis.ipynb` to download apis and relevant files.


4. Create the docker image using the following command
```docker build -t gen-agents-auto-qc .```

----
## To Run with Proto Schema.

  - Move the .pb file to the root folder.
  
  - Open `docker_orchestrator_proto.ipynb` file and update proto_file_name in `Parse Proto` section i.e. `proto_file_name = 'tool_use_metadata_set_v2.pb'`
  
  - Run All Sections in the same notebook one by one. The last cell will store the results as csv, that csv can then be utilised to analyse the response.

---
## To Run with Colab Schema.

  1. Create a googlesheet that must contain `sample_id` and `colab_url`.
  
  2. Update the `sheet_id` and `data_tab` in `Fetch & Download Colabs / Notebooks` section in `docker_orchestrator_colab.ipynb` to reflect the sheet where you created the input data and the relevant tab.
  
  3. Adjust the max docker containers to run in parallel in `Create Batches and Configuration Files for Docker Runs` section.
  
  4. Run All Sections in the same notebook one by one. The last cell will upload the results to the same sheet under the tab `auto_qc_response`, update it if needed.
  
  5. Please ensure that the service account has the rw access to the sheet and the colabs.