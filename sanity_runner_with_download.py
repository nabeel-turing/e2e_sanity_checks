import io
import re
import sys
import shutil
import json
import copy
import traceback
from tqdm import tqdm
from pathlib import Path

import pandas as pd
import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError
from datetime import datetime

from notebook_parser import GAImplementationColabParser, get_code_blocks, create_auto_qc_notebook, SECTIONS

from googleapiclient.http import MediaIoBaseDownload

CLEAN_SOURCE_DIR = Path("/clean_workspace")
CONTENT_DIR = Path("/content")

RESULTS_DIR = Path("/results")
LOGS_DIR = Path("/logs")
NOTEBOOK_OUTPUTS = Path("/notebook_results")


TASK_FILE_PATH = "/execution_configs.csv"


preserve_state = '''

# SKIPPED ORIGINAL SETUP CELL
# Adding API and DB directories to path instead
import sys
import os
print("Injecting API and DB paths into system path...")
api_dir = "/content/APIs"
db_dir = "/content/DBs"
scripts_dir = "/content"
if api_dir not in sys.path:
    sys.path.append(api_dir)
if db_dir not in sys.path:
    sys.path.append(db_dir)
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)

os.chdir('/content')
print("System paths updated.")

_initial_dir = None

def start_block():
  global _initial_dir
  _initial_dir = set(globals().keys())

def end_block():
  global _initial_dir
  # Compare current dir() to the saved _initial_dir
  for name in set(globals().keys()):
      # Skip anything that was already there originally,
      # or that starts with an underscore, or the function names themselves
      if (
          name not in _initial_dir
          and not name.startswith('_')
          and name not in ['start_block', 'end_block']
      ):
          del globals()[name]'''

def authenticate_with_service_account():
    from googleapiclient.discovery import build
    from google.oauth2 import service_account

    """Authenticate using a service account and return credentials."""
    SECRET_KEY_FILE = "/secrets/gcp_key.json"

    # Combine scopes for both Drive and Sheets
    SCOPES = [
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets",
    ]
    creds = service_account.Credentials.from_service_account_file(
        SECRET_KEY_FILE,
        scopes=SCOPES
    )

    # Build the Drive service using the credentials
    return build("drive", "v3", credentials=creds)

def setup_logging(identifier: str):
    """Redirects all stdout/stderr to a log file for this container's run."""
    log_file_path = LOGS_DIR / f"container_{identifier}.log"
    print(f"Runner script logging to: {log_file_path}")
    sys.stdout = open(log_file_path, "w", encoding="utf-8")
    sys.stderr = sys.stdout

def print_time(text=None):
    timestamp = datetime.now().strftime("%d-%m-%Y :: %H:%M:%S")
    print(f"[{timestamp}]: {text if text else ''}")

def sanitize_workspace():
    """Cleans the /content directory and populates it from the /clean_workspace golden copy."""
    print("Sanitizing workspace for SKIP_SETUP mode...")
    if CONTENT_DIR.exists():
        shutil.rmtree(CONTENT_DIR)
    shutil.copytree(CLEAN_SOURCE_DIR, CONTENT_DIR)
    # install_api_requirements()
    print("Workspace sanitized successfully.")

def remove_ansi_codes(text):
    """
    Removes ANSI escape codes from a string.
    """
    # This regex matches the common patterns for ANSI escape codes
    ansi_escape_pattern = re.compile(r'\x1b\[[0-9;]*[mK]')
    return ansi_escape_pattern.sub('', text)

def execute_notebook(notebook):
    client = NotebookClient(notebook, timeout=600, kernel_name='python3')
    try:
        # Execute the entire notebook at once
        client.execute()
        return {
            "script_success": True,
            "Block": "",
            "Error Type": "",
            "Error Description": "",
            "Error Detail": ""
        }
    except CellExecutionError as e:
        # print_time(e)
        # Check if the exception is due to notebook execution failure
        # and not an error within a cell
        # Fallback to the original logic for cell errors
        current_header = None
        for i, cell in enumerate(notebook.cells):
            if cell.cell_type == "markdown":
                flat_source = ''.join(cell.get('source', []))
                lines = [line.strip() for line in flat_source.splitlines() if line.strip()]

                # Extract header
                if lines and lines[0].startswith("#"):
                    current_header = lines[0]

            if cell['cell_type'] == "code":
                for output in cell.get("outputs", []):
                    if output.get("output_type") == "error":
                        ename = output.get("ename", "Error")
                        evalue = output.get("evalue", "No error message")
                        return {
                            "script_success": True,
                            "Block": current_header,
                            "Error Type": ename,
                            "Error Description": evalue,
                            "Error Detail": remove_ansi_codes(str(e)[:49999])
                        }
    except Exception as e:
        print_time(f"Notebook execution could not be completed due to an error: {e}")
        return {
            "script_success": False,
            "Block": "",
            "Error Type": "",
            "Error Description": "",
            "Error Detail": remove_ansi_codes(str(e)[:49999])
        }

def prune_steps(notebook, remove_action, remove_download=True):
    cells = notebook['cells']
    new_cells = []
    in_skipped_block = False

    for cell in cells:
        # Remove pip install globally if version is known (i.e., not first run)
        if remove_download and cell['cell_type'] == 'code':
            cell['source'] = [
                line for line in cell.get('source', [])
                if "!pip install" not in line
            ]

        # Check markdown headers for skipping logic
        if cell['cell_type'] == 'markdown':
            source_text = ''.join(cell['source']).strip()

            if (remove_action and source_text.startswith("# Action") and not in_skipped_block)\
                    or (remove_download and source_text.startswith("## Download relevant files") and not in_skipped_block):
                in_skipped_block = True
                continue

            if source_text.startswith("#"):
                in_skipped_block = False

        # Keep cell only if it's not in a block we're skipping
        if not in_skipped_block:
            new_cells.append(cell)

    notebook['cells'] = new_cells
    return notebook

def get_modified_colab(nb_data):

    global preserve_state
    ignore_state_instruction = "ignore_state_preservation"
    merged_notebook = nbformat.v4.new_notebook()
    merged_notebook.cells = []  # Initialize empty cell list
    nb_dict = copy.deepcopy(nb_data)
    # nb_dict = prune_steps(nb_dict, remove_action=remove_action)

    cells = nb_dict.get('cells', [])

    # Insert global preserve_state block at top
    cells.insert(0, {'cell_type': 'code', 'source': [preserve_state], 'metadata': {}})

    i = 0
    while i < len(cells):
        cell = cells[i]
        if cell.get('cell_type') == 'markdown':
            flat_source = ''.join(cell.get('source', [])).strip()
            lines = [line.strip() for line in flat_source.splitlines() if line.strip()]

            # --- Merge Import APIs and initiate DBs block ---
            if lines and lines[0].startswith("## Import APIs and initiate DBs"):
                j = i + 1
                while j < len(cells):
                    future_cell = cells[j]
                    if future_cell.get('cell_type') == 'markdown':
                        break
                    j += 1
                code_cells = [''.join(c.get('source', [])) for c in cells[i + 1: j] if c.get('cell_type') == 'code']
                # more than 1 code cell

                if len(code_cells) > 1:
                    cells[i + 1]['source'] = [f"# {ignore_state_instruction}\n" + code_cells[0]]
                    merged_code = '\n'.join(code_cells[1:])
                    cells[i + 2: j] = [{
                        "cell_type": "code",
                        "metadata": {},
                        "source": [merged_code]
                    }]
                i += 1  # Skip to next

            # --- Merge Action block ---
            elif lines and lines[0].startswith("# Action"):
                j = i + 1
                while j < len(cells):
                    future_cell = cells[j]
                    if future_cell.get('cell_type') == 'markdown':
                        future_lines = [line.strip() for line in ''.join(future_cell.get('source', [])).splitlines() if
                                        line.strip()]
                        if future_lines and future_lines[0].startswith("# Final Assertion"):
                            break
                    j += 1

                merged_code = '\n'.join(
                    ''.join(c.get('source', [])) for c in cells[i + 1: j] if c.get('cell_type') == 'code'
                )
                cells[i + 1: j] = [{
                    "cell_type": "code",
                    "metadata": {},
                    "source": [merged_code]
                }]
                i += 1  # Skip to next

            # --- Merge Final Assertion block ---
            elif lines and lines[0].startswith("# Final Assertion"):
                j = i + 1
                while j < len(cells):
                    future_cell = cells[j]
                    if future_cell.get('cell_type') == 'markdown':
                        break
                    j += 1

                merged_code = '\n'.join(
                    ''.join(c.get('source', [])) for c in cells[i + 1: j] if c.get('cell_type') == 'code'
                )
                cells[i + 1: j] = [{
                    "cell_type": "code",
                    "metadata": {},
                    "source": [merged_code]
                }]
                i += 1  # Skip to next

        i += 1

    # --- Add start_block() / end_block() to all code cells ---
    for cell in nb_dict.get('cells', []):
        if cell.get('cell_type') == 'code':
            code = cell.get('source', [])
            if not any(("start_block()" in line or ignore_state_instruction in line) for line in code):
                cell['source'] = ["start_block()\n"] + code + ["\nend_block()"]

    # Add to final merged notebook
    merged_notebook.cells.extend(cells)
    return merged_notebook

def check_execution_errors(nb_json, remove_action=False):

    print_time("starting pruning colab")
    pruned_colab = prune_steps(nb_json, remove_action)
    print_time("finished pruning colab")

    print_time("started injecting code in colab")
    modified_colab = get_modified_colab(pruned_colab)
    print_time("finished injecting code in colab")

    print_time("starting colab execution")
    notebook_to_execute = nbformat.reads(json.dumps(modified_colab), as_version=4)
    error_cells = execute_notebook(notebook_to_execute)
    print_time("finished colab execution")

    return error_cells

def download_notebook(file_id):
    """Downloads a Colab notebook (.ipynb) from Google Drive."""
    drive_service = authenticate_with_service_account()
    request = drive_service.files().get_media(fileId=file_id, supportsAllDrives=True)
    file_stream = io.BytesIO()
    downloader = MediaIoBaseDownload(file_stream, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    file_stream.seek(0)
    return file_stream.read()

def contains_golden_answer(notebook_json):
    pattern = r"^##?\s*Golden\s*Answer"
    regex = re.compile(pattern, re.IGNORECASE)
    
    markdown_cells = [cell for cell in notebook_json['cells'] if cell['cell_type'] == 'markdown']
    for cell in markdown_cells:
        if any([regex.match(line) for line in cell['source']]):
            return True
    return False

def contains_final_assert(notebook_json):
    fa_block_found = False
    for cell in notebook_json['cells']:
        pattern = r"^##?\s*Final\s*Assertion"
        regex_fa = re.compile(pattern, re.IGNORECASE)
        
        pattern = r"^\s*assert\s+.+"
        regex_assert = re.compile(pattern)

        if cell['cell_type'] == 'markdown' and not fa_block_found:
            if any([regex_fa.match(line) for line in cell['source']]):
                fa_block_found = True
            continue
        if fa_block_found and cell['cell_type'] == 'code':
            if any([regex_assert.match(line) for line in cell['source']]) or any(['raise AssertionError' in line for line in cell['source']]):
                return True
    return False

def format_execution_result(result_object):
    
    def format_error_object(error_object):
        if error_object.get('Block', "") == "":
            res_str = ""
        else:
            line1_block = f"Block: {error_object['Block']}"
            line2_type = f"Error Type: {error_object['Error Type']}"
            line3_description = f"Error Description: {error_object['Error Description']}"
            line4_detail = f"Error Detail: {error_object['Error Detail']}"
            res_str = f"{line1_block}\n{line2_type}\n{line3_description}\n{line4_detail}"

        return error_object.get("script_success", False), res_str

    no_action_script_success, no_action_fmt_response = format_error_object(result_object["no_action_error"])
    with_action_script_success, with_action_fmt_response = format_error_object(result_object["with_action_error"])

    return {
        'notebook': result_object['notebook'],
        'no_action_script_success': no_action_script_success,
        'no_action_response': no_action_fmt_response,
        'with_action_script_success': with_action_script_success,
        'with_action_response': with_action_fmt_response,
        'contains_golden_answer': result_object['contains_golden_answer'],
        'contains_final_assert': result_object['contains_final_assert']
    }
    
def parse_colab_sections(notebook_json):


    sections = {}
    current_header = None
    for cell in notebook_json['cells']:
        cell_type = cell['cell_type']
        cell_source = cell['source']
        
        
        if cell_type == 'markdown':
            if cell_source[0].startswith(HEADERS.install_dependencies):
                current_header = HEADERS.install_dependencies
                continue
            if cell_source[0].startswith(HEADERS.initialisation):
                current_header = HEADERS.initialisation
                continue
            if cell_source[0].startswith(HEADERS.initial_assertion):
                current_header = HEADERS.initial_assertion
                continue        
            if cell_source[0].startswith(HEADERS.action):
                current_header = HEADERS.action
                continue        
            if cell_source[0].startswith(HEADERS.final_assertion):
                current_header = HEADERS.final_assertion
                continue            
        
        if cell_type == 'code':
            if current_header in [HEADERS.install_dependencies,
                                  HEADERS.initialisation,
                                  HEADERS.initial_assertion,
                                  HEADERS.action,
                                  HEADERS.final_assertion
                                  ]:
                if current_header not in sections:
                    sections[current_header] = []
                sections[current_header].append(cell_source)

    for key, value in sections.items():
        if key == HEADERS.install_dependencies:
            cells = []
            for block in value:
                cells += [ln for ln in block if not ln.startswith('!pip')]
            sections[key] = cells
        elif key == HEADERS.initialisation:
            total_cells = len(value)
            if total_cells == 1:
                sections[key] = ["\nstart_block()\n"] + value[0] + ["\nend_block()\n"]
            elif total_cells > 1:
                cells = []
                for code_block in value:
                    if code_block[0].startswith('# proto_ignore'):
                        cells += ['\n'] + code_block
                    else:
                        cells += ["\nstart_block()\n"] + code_block + ["\nend_block()\n"]
                sections[key] = cells
        else:
            combined_source = []
            for code_cell in value:
                combined_source += ['\n'] + code_cell
            sections[key] = ["\nstart_block()\n"] + combined_source + ["\nend_block()\n"]

    notebook = nbformat.v4.new_notebook()
    notebook.cells = []  # Initialize empty cell list

    notebook.cells.insert(0, {'cell_type': 'code', 'source': [preserve_state], 'metadata': {}, 'outputs': []})
    for idx, section in enumerate([HEADERS.install_dependencies, HEADERS.initialisation, HEADERS.final_assertion, HEADERS.initial_assertion, HEADERS.action, HEADERS.final_assertion]):
        notebook.cells.insert((idx*2)+1, {'cell_type': 'markdown', 'source': section, 'metadata': {}, 'outputs': []})
        notebook.cells.insert((idx*2)+2, {'cell_type': 'code', 'source': sections.get(section, []), 'metadata': {}, 'outputs': []})

    return notebook


def run_nb_e2e(notebook):

    # notebook = nbformat.reads(json.dumps(notebook_json), as_version=4)            
    client = NotebookClient(notebook, timeout=600, kernel_name='python3', allow_errors=True)
    execution_result = {
        'script_passed': True,
        'script_failure_msg': "N/A",
        
        f"{SECTIONS.SETUP.value} - {SECTIONS.INSTALL_AND_CLONE_REPO_CODE.value}": [],
        f"{SECTIONS.SETUP.value} - {SECTIONS.IMPORT_APIS_AND_INITIATE_DBS.value}": [],
        f"{SECTIONS.FINAL_ASSERTION.value}_NO_ACTION": [],
        SECTIONS.INITIAL_ASSERTION.value: [],
        SECTIONS.ACTION.value: [],
        SECTIONS.FINAL_ASSERTION.value: []
    }          
    try:
        client.execute()
        current_header = None
        for i, cell in enumerate(notebook.cells):
            if cell['cell_type'] == "markdown":
                current_header = ''.join(cell['source']).strip()
            if cell['cell_type'] == "code":
                outputs = cell.get("outputs", [])
                
                error_output = [output for output in outputs if output.get("output_type") == "error"]
                print_time(error_output)
                if not outputs or len(error_output) == 0:
                    pass
                    # execution_result[current_header].append("")
                elif len(error_output) > 0:
                    ename = error_output[0].get("ename", "Error")
                    evalue = error_output[0].get("evalue", "No error message")
                    execution_result[current_header].append(f"ErrorType: {ename}\nError Description: {evalue}")

                    # print_time(remove_ansi_codes(str(e)[:49999]))                        
    except:
        # print_time(f"Notebook execution could not be completed due to an error")
        error_tb = traceback.format_exc()
        execution_result = {
            'script_passed': False,
            'script_failure_msg': error_tb,
            
            f"{SECTIONS.SETUP.value} - {SECTIONS.INSTALL_AND_CLONE_REPO_CODE.value}": [],
            f"{SECTIONS.SETUP.value} - {SECTIONS.IMPORT_APIS_AND_INITIATE_DBS.value}": [],
            f"{SECTIONS.FINAL_ASSERTION.value}_NO_ACTION": [],
            SECTIONS.INITIAL_ASSERTION.value: [],
            SECTIONS.ACTION.value: [],
            SECTIONS.FINAL_ASSERTION.value: []
        }
    finally:
        output_file = str(NOTEBOOK_OUTPUTS / f'{notebook_url_id}.ipynb')
        nbformat.write(notebook, output_file)
    print_time(execution_result)
    separator = f'\n{"-"*40}\n'
    for key in execution_result.keys():
        if key not in ['script_failure_msg', 'script_passed']:
            execution_result[key] = separator.join(execution_result[key])
    return execution_result
    
if __name__ == "__main__":

    run_id = str(sys.argv[1])
    setup_logging(str(run_id))

    print_time(f"Starting Run for ID: {run_id}")

    tasks_df = pd.read_csv(TASK_FILE_PATH)
    batch_df = tasks_df[tasks_df['batch_id']==run_id]
    if len(batch_df) == 0:
        print_time(f"No notebooks to execute for batch {run_id}")
        notebooks_to_run = []
    else:
        notebooks_to_run = batch_df['path'].tolist()

    execution_results = []

    for notebook_url_id in tqdm(notebooks_to_run):
        execution_result = {}
        try:
            print_time(f"Starting colab: {notebook_url_id}")

            print_time("starting sanitizing workspace")
            sanitize_workspace()
            print_time("finished sanitizing workspace")            

            
            notebook_data = download_notebook(notebook_url_id)
            notebook_json = json.loads(notebook_data)

            print_time("starting downloading/parsing colab")
            colab_info = {
                'id': notebook_url_id,
                'name': f'{notebook_url_id}.ipynb'
            }

            colab_id = colab_info['id']
            colab_url = f"https://colab.research.google.com/drive/{colab_id}"

            nb_read = nbformat.reads(json.dumps(notebook_json), as_version=4) 
            parsed_colab = GAImplementationColabParser(colab_info, colab_url, nb_read)
            code_blocks = get_code_blocks(parsed_colab)
            notebook = create_auto_qc_notebook(code_blocks.copy())
            print_time("finished downloading/parsing colab")

            print_time("Started: executing notebook")
            execution_response = run_nb_e2e(notebook)
            print_time("Finished: executing notebook")


            print_time("Started: checking if contains Golden Answer/Final Assert")
            golden_answer_sample = contains_golden_answer(notebook_json)
            final_assert_sample = contains_final_assert(notebook_json)
            print_time("Finished: checking if contains Golden Answer/Final Assert")
                        
            execution_result = {
                'notebook': notebook_url_id,
                'contains_golden_answer': golden_answer_sample,
                'contains_final_assert': final_assert_sample,
                **execution_response
            }
            print_time(execution_result)

        except:
            # print_time(f"Exception in main: {str(e)}")
            error_tb = traceback.format_exc()
            # print_time(traceback.format_exc())
            execution_result = {
                'script_success': False, 
                'script_failure_msg': error_tb,
                'notebook': notebook_url_id,
                f"{SECTIONS.SETUP.value} - {SECTIONS.install_dependencies}": '',
                f"{SECTIONS.SETUP.value} - {SECTIONS.IMPORT_APIS_AND_INITIATE_DBS}": '',
                f"{SECTIONS.FINAL_ASSERTION.value}_NO_ACTION": '',
                SECTIONS.INITIAL_ASSERTION: '',
                SECTIONS.ACTION: '',
                SECTIONS.FINAL_ASSERTION: '',
                'contains_golden_answer': "",
                'contains_final_assert': "",
            }
        finally:
            execution_results.append(execution_result)

    # Define output the filename
    json_output = RESULTS_DIR  / f'output_batch_{run_id}.json'

    print_time("starting writing results")
    with open(json_output, 'w') as f:
        json.dump({'result': execution_results}, f, indent=4)
    print_time("finished writing results")