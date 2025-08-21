#@title Imports
import os
import re
import asyncio
import copy
import difflib
import json
import nbformat
import threading
import concurrent.futures
import pandas as pd
import importlib # Import importlib

import pytz
import datetime

from abc import ABC, abstractmethod
from enum import Enum
from tqdm.notebook import tqdm
from typing import Optional, Sequence, Literal, Any
# from google.colab import auth
from googleapiclient.discovery import build
from google.protobuf import json_format
from pydantic import BaseModel, computed_field, Field, ValidationError, model_validator

from google.oauth2 import service_account

# import tool_use_task_metadata_pb2 as pb2



#@title Block Level Parsers

class Block(BaseModel, ABC):
    serial_number: int
    logical_section: str

    def parse_block(self) -> "Block":
        raise NotImplementedError

    @computed_field
    @property
    @abstractmethod
    def _block_type_name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def type_key(self) -> Literal['markdown', 'code', 'code_output']:
        raise NotImplementedError

    @computed_field
    @property
    def name(self) -> str:
        return f"Block {self.serial_number}: {self.logical_section} - {self._block_type_name}"

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError

    model_config = {
        "extra": "allow"
    }


class GAMetadata(Block):
    content: str
    metadata: dict = Field(default_factory=dict)
    additional_data: Optional[str] = None

    @computed_field
    @property
    def _block_type_name(self) -> str:
        return "GA Metadata"

    @property
    def type_key(self) -> Literal['markdown', 'code', 'code_output']:
        return "markdown"

    def parse_block(self) -> "GAMetadata":
        content_str = ""
        if isinstance(self.content, list):
            content_str = "\n".join([str(item) for item in self.content if item is not None])
        else:
            content_str = str(self.content)

        metadata_keys = ["Sample ID", "Query", "DB Type", "Case Description", "Global/Context Variables", "APIs", "Databases"]

        try:
            if isinstance(content_str, str):
                metadata = {}
                inside_section = False
                current_section = None
                section_content = []

                for line in content_str.split("\n"):
                    line = line.strip()
                    if not line:
                        continue

                    possible_metadata_label = re.compile(r"(\*\*(.*?)(?::)?\*\*)").match(line)
                    if possible_metadata_label:
                        matched_metadata_label = get_closest_match(possible_metadata_label.group(2), metadata_keys)
                        if matched_metadata_label:
                            if current_section:
                                metadata[current_section] = '\n'.join(section_content) if section_content else ""
                                section_content = []

                            if line.replace(possible_metadata_label.group(1), "").lstrip(": "):
                                section_content.append(line.replace(possible_metadata_label.group(1), "").lstrip(": "))

                            current_section = matched_metadata_label
                            inside_section = True
                            continue

                    elif not possible_metadata_label and inside_section:
                        section_content.append(line)
                        continue

                if current_section and section_content:
                    metadata[current_section] = '\n'.join(section_content)

                self.metadata.update(metadata)


                if "Case Description" in self.metadata:
                    case_desc_content = self.metadata["Case Description"]
                    match = re.search(r"<additional_data>(.*?)</additional_data>", case_desc_content, re.DOTALL)
                    if match:
                        self.additional_data = match.group(1).strip()
                        self.metadata["Case Description"] = re.sub(r"<additional_data>.*?</additional_data>", "", case_desc_content, flags=re.DOTALL).strip()

                if "APIs" in self.metadata:
                    result = {}
                    inside_additional_repo = False
                    additional_repo_content = []
                    additional_repo_cnt = 0

                    for line in self.metadata.get("APIs").split("\n"):
                        stripped = line.strip()

                        if stripped.startswith("-"):
                            label = stripped.lstrip("-").strip()
                            result[label] = label

                        elif "```" in stripped and inside_additional_repo:
                            inside_additional_repo = False
                            additional_repo_content.append(stripped)
                            additional_repo_cnt += 1
                            try:
                                result[f"addition_repo_{additional_repo_cnt}"] = json.loads(('\n'.join(additional_repo_content)).replace("```", ""))
                            except Exception as e:
                                result[f"addition_repo_{additional_repo_cnt}"] = []

                            additional_repo_content = []

                        elif "```" in stripped and not inside_additional_repo:
                            additional_repo_content.append(stripped)
                            inside_additional_repo = True

                        elif inside_additional_repo:
                            additional_repo_content.append(stripped)

                    self.metadata["APIs"] = result

        except Exception as e:
            error_msg = f"Error parsing GA metadata: {str(e)}"
            raise Exception(error_msg, {"block_type": self._block_type_name, "serial_number": self.serial_number, "logical_section": self.logical_section})
        return self

    def __str__(self) -> str:
        separator = "-" * (len(self.name) + 4)
        metadata_str = json.dumps(self.metadata, indent=2)
        return f"{self.name}\n{separator}\nMetadata:\n{metadata_str}\n"


class MarkdownBlock(Block):
    content: str

    def parse_block(self) -> "MarkdownBlock":
        return self

    @computed_field
    @property
    def _block_type_name(self) -> str:
        return "Markdown"

    @property
    def type_key(self) -> Literal['markdown', 'code', 'code_output']:
        return "markdown"

    def __str__(self) -> str:
        return f"{self.name}\n{self.content}\n"

class CodeBlock(Block):
    content: str

    def parse_block(self) -> "CodeBlock":
        return self

    @computed_field
    @property
    def _block_type_name(self) -> str:
        return "Code"

    @property
    def type_key(self) -> Literal['markdown', 'code', 'code_output']:
        return "code"

    def __str__(self) -> str:
        return f"{self.name}\n{self.content}\n"


class CodeOutputItem(BaseModel):
    output_type: str
    name: Optional[str] = None
    text: Optional[str | list[str]] = None

class CodeOutputBlock(Block):
    raw_content: str
    outputs: list[CodeOutputItem] = Field(default_factory=list)

    def parse_block(self) -> "CodeOutputBlock":
        return self

    @model_validator(mode='before')
    @classmethod
    def parse_raw_content_to_outputs(cls, data: Any) -> Any:
        if isinstance(data, dict):
            raw_content_str = data.get('raw_content')
            if isinstance(raw_content_str, str):
                try:
                    parsed_json = json.loads(raw_content_str)
                    if isinstance(parsed_json, list):
                        data['outputs'] = parsed_json
                    else:
                        data['outputs'] = []
                except json.JSONDecodeError:
                    data['outputs'] = []
                except Exception as e:
                    data['outputs'] = []
        return data

    @computed_field
    @property
    def _block_type_name(self) -> str:
        return "Code Output"

    @property
    def type_key(self) -> Literal['markdown', 'code', 'code_output']:
        return "code_output"

    def __str__(self) -> str:
        output_summary = []
        if not self.outputs:
             output_summary.append("  [No parsed output or parse error]")
        else:
            for i, output_item in enumerate(self.outputs):
                item_dict = output_item.model_dump(exclude_none=True)
                otype = item_dict.get('output_type', 'unknown')
                oname = f" ({item_dict.get('name', '')})" if 'name' in item_dict else ""
                text_preview = ""
                if 'text' in item_dict:
                    text_content = item_dict['text']
                    full_text = "".join(text_content) if isinstance(text_content, list) else str(text_content)
                    text_preview = f": {full_text.strip()}" if full_text else ""
                output_summary.append(f"  Output {i+1}: type='{otype}'{oname}{text_preview}")

        return f"{self.name}\n[Raw JSON stored]\nParsed Outputs:\n{''.join(output_summary)}\n"
      

#@title Turn Level Parser

class Turn(BaseModel):
    idx: int
    blocks: list[Block] = Field(default_factory=list)

    def parse_blocks(self) -> None:
        for block in self.blocks:
            block.parse_block()

    def add_block(self, block: Block):
        self.blocks.append(block)

    def get_blocks_by_section(self, section_name: str) -> list[Block]:
        return [block for block in self.blocks if block.logical_section == section_name]

    def get_blocks_by_type(self, block_type: Literal['markdown', 'code', 'code_output']) -> list[Block]:
        return [block for block in self.blocks if block.type_key == block_type]

    def __str__(self) -> str:
        turn_header = f"********** Turn {self.idx} **********"
        separator = "*" * len(turn_header)
        blocks_str = "".join(str(block) for block in self.blocks)
        return f"{separator}\n{turn_header}\n{separator}{blocks_str}\n"
    
  

#@title Colab Parser

class SECTIONS(str, Enum):
    METADATA = "Metadata"
    SETUP = "Set Up"
    DOWNLOAD_FILES = "Download relevant files"
    IMPORT_APIS_AND_INITIATE_DBS = "Import APIs and initiate DBs"
    INSTALL_AND_CLONE_REPO_CODE="Install Dependencies and Clone Repositories"
    INITIAL_ASSERTION = "Initial Assertion"
    ACTION = "Action"
    GOLDEN_ANSWER = "Golden Answer"
    FINAL_ASSERTION = "Final Assertion"


class GAImplementationColabParser:
    """
    Parses a Colab notebook represented as a list of (cell_type, content) tuples
    into Turns and Blocks, associating blocks with logical sections based on specific markdown headers.

    Assumes the structure: Description -> Setup -> Initial Assertion -> Action -> Final Assertion.
    Assumes a single Turn for this structure.
    """

    # Define the CANONICAL names for main sections
    _CANONICAL_MAIN_SECTIONS: list[str] = [
        SECTIONS.SETUP.value,
        SECTIONS.INITIAL_ASSERTION.value,
        SECTIONS.ACTION.value,
        SECTIONS.GOLDEN_ANSWER.value,
        SECTIONS.FINAL_ASSERTION.value
    ]
    _DEFAULT_SECTION_NAME = SECTIONS.METADATA.value
    # Regex to match H1 headers (allows for no space: #Header or space: # Header)
    _MAIN_SECTION_REGEX = re.compile(r"^#\s?([^#].*)") # Optional space after #
    # Regex to match H2+ sub-section headers
    _SUB_SECTION_REGEX = re.compile(r"^(#{2,})\s+(.*)")
    # Cutoff for fuzzy matching (0.0 to 1.0, higher means stricter match)
    _FUZZY_MATCH_CUTOFF = 0.8

    def __init__(self, file_info: dict[str, Any], drive_url: str, nb):
        """Initializes parser, loads notebook, and parses turns."""
        self.file_name: str = file_info["name"]
        self.file_id: str = file_info["id"]
        # self.colab_url: str = drive_url

        # global DRIVE_SERVICE
        # if 'DRIVE_SERVICE' not in globals():
        #      print("Error: DRIVE_SERVICE not initialized. Please authenticate.")
        #      raise RuntimeError("DRIVE_SERVICE is required but not available.")

        self._raw_plan = self.__create_a_plan_from_drive_notebook(self.file_id, nb)

        if not self._raw_plan:
            raise ValueError(f"Failed to load or parse colab notebook content: {self.file_name} ({self.file_id})")

        self.turns: list[Turn] = []
        try:
            self._parse_plan_to_turns()
            self._parse_turns()

        except ValidationError as e:
            print(f"Pydantic validation error during parsing: {e}")
            raise
        except Exception as e:
             print(f"An unexpected error occurred during parsing logic: {e}")
             raise


    def _parse_turns(self) -> None:
        """Parses all turns in the notebook."""
        for turn in self.turns:
            turn.parse_blocks()

    def _parse_plan_to_turns(self) -> None:
        """Iterates through the raw plan, creating blocks and assigning them to a turn,
           using fuzzy matching for H1 headers."""
        current_turn = Turn(idx=1)
        self.turns.append(current_turn)

        current_main_section_name: str = self._DEFAULT_SECTION_NAME
        current_sub_section_name: Optional[str] = None
        serial_number = 1

        for cell_type, raw_content in self._raw_plan:
            content = raw_content.strip()
            block_instance: Optional[Block] = None
            is_new_main_section = False
            is_new_sub_section = False

            # --- Determine Section based on Markdown Headers ---
            if cell_type == 'markdown' and content and serial_number > 1:
                first_line = content.split('\n', 1)[0].strip()

                # Check for H1 Header first (Main Section)
                main_match = self._MAIN_SECTION_REGEX.match(first_line)
                if main_match:
                    extracted_title = main_match.group(1).strip()

                    # Attempt fuzzy match against canonical names
                    matched_canonical_name = get_closest_match(
                        extracted_title,
                        self._CANONICAL_MAIN_SECTIONS,
                        cutoff=self._FUZZY_MATCH_CUTOFF
                    )

                    # Use canonical name if matched, otherwise use the extracted title
                    current_main_section_name = matched_canonical_name if matched_canonical_name else extracted_title
                    current_sub_section_name = None # Reset sub-section
                    is_new_main_section = True
                else:
                    # If not H1, check for H2+ Header (Sub-section)
                    sub_match = self._SUB_SECTION_REGEX.match(first_line)
                    if sub_match:
                         # Assign sub-section only if we are not in the default "Description"
                         if current_main_section_name != self._DEFAULT_SECTION_NAME:
                            current_sub_section_name = sub_match.group(2).strip()
                            is_new_sub_section = True

            if current_sub_section_name:
                block_logical_section = f"{current_main_section_name} - {current_sub_section_name}"
            else:
                block_logical_section = current_main_section_name

            common_args = {
                "serial_number": serial_number,
                "logical_section": block_logical_section,
            }
            try:
                if cell_type == 'markdown':
                    if current_main_section_name == self._DEFAULT_SECTION_NAME:
                        block_instance = GAMetadata(**common_args, content=content)
                    else:
                        block_instance = MarkdownBlock(**common_args, content=content)
                elif cell_type == 'code':
                    block_instance = CodeBlock(**common_args, content=content)
                elif cell_type == 'code_output':
                    block_instance = CodeOutputBlock(**common_args, raw_content=content)
                else:
                    print(f"Warning: Skipping cell with unexpected type '{cell_type}' at serial number {serial_number}")
                    continue
            except ValidationError as e:
                 print(f"Validation Error creating Block {serial_number} ({cell_type}, section: {block_logical_section}):\n{e}")
                 serial_number += 1
                 continue

            if block_instance:
                current_turn.add_block(block_instance)
                serial_number += 1

    def __create_a_plan_from_colab_notebook(self, note_book: nbformat.NotebookNode) -> list[tuple[str, str]]:
        """Creates a plan string from a Colab notebook by extracting markdown and code cells.

        Parameters:
        ----------
        nb : nbformat.NotebookNode
            The notebook object in nbformat that contains the cells to be processed.

        Returns:
        -------
        list[tuple[str, str]]]
            A formatted string with content from markdown cells and labeled code cells.
            Code cells are prefixed with "CODE:\n".

        """
        plan_lines = []

        # Iterate through each cell in the notebook
        for cell in note_book.cells:
            # Check if the cell is of type markdown and contains content
            if cell.cell_type == "markdown":
                # Append the tuple ('markdown', content)
                plan_lines.append(("markdown", cell.source))

            # Check if the cell is of type code and contains content
            elif cell.cell_type == "code":
                # Append the tuple ('code', content)
                plan_lines.append(("code", cell.source))

                # Check if there are outputs associated with the code cell
                if cell.outputs and len(cell.outputs) > 0:
                    cell_out = json.dumps(cell.outputs)

                    # Append the tuple ('code_output', output content)
                    plan_lines.append(("code_output", cell_out))

        # Return the list of tuples (cell_type, content)
        return plan_lines

    def __create_a_plan_from_drive_notebook(self, file_id: str, nb) -> list[tuple[str, str]] | None:
        """Fetches a Jupyter notebook from Google Drive, processes it, and returns a formatted plan.

        Parameters:
        ----------
        file_id : str
            The unique identifier of the file in Google Drive.

        Returns:
        -------
        Optional[list[tuple[str, str]]]
            A formatted string with content from markdown cells and labeled code cells.
            Code cells are prefixed with "CODE:\n".

        Notes:
        -----
        - This function assumes access to the Google Drive API through `DRIVE_SERVICE`.
        - Only files with a MIME type other than 'application/vnd.google-apps.folder' are processed.
        - The notebook is assumed to be in `nbformat` version 4.

        """
        try:
            # Fetch the file metadata to determine the MIME type and name
            # file_metadata = DRIVE_SERVICE.files().get(fileId=file_id, fields="name, mimeType", supportsAllDrives=True).execute()  # noqa
            # file_name, mime_type = file_metadata["name"], file_metadata["mimeType"]

            # Only process if it's not a folder
            # if mime_type != "application/vnd.google-apps.folder":
                # Download the file content
                # file_content = DRIVE_SERVICE.files().get_media(fileId=file_id, supportsAllDrives=True).execute()  # noqa

                # Try to load notebook into nbformat
                try:
                    # nb = nbformat.reads(file_content.decode("utf-8"), as_version=4)
                    # Generate the plan string from the notebook content
                    return self.__create_a_plan_from_colab_notebook(nb)
                except Exception as error:
                    print(f"Failed to load notebook: ({file_id}) - {str(error)}")
                    return None
            # else:
            #     print(f"File {file_name} is a folder.")
            #     return None

        except Exception as error:
            print(f"An error occurred while retrieving the file: {str(error)}")
            return None

    def __str__(self):  # noqa
        print(f"Colab: {self.file_name}")  # noqa: T201
        for turn in self.turns:
            print(turn)  # noqa: T201
        return ""

    @property
    def first_turn(self) -> Optional[Turn]:
        """Returns the first (and likely only) turn."""
        return self.turns[0] if self.turns else None

    def get_all_blocks(self) -> list[Block]:
        """Returns a flat list of all blocks from all turns."""
        all_blocks = []
        for turn in self.turns:
            all_blocks.extend(turn.blocks)
        return all_blocks

def get_closest_match(item: str, valid_items: list[str], cutoff: float = 0.8) -> str | None:
    """Finds the closest matching item from the provided list using difflib,
    performing case-insensitive comparison after stripping whitespace.
    """
    if not item or not valid_items:
        return None

    item_normalized = item.strip().lower()
    if not item_normalized:
        return None

    normalized_to_original_map = {
        v.strip().lower(): v for v in valid_items if v.strip()
    }
    normalized_valid_items = list(normalized_to_original_map.keys())

    if not normalized_valid_items:
        return None

    closest_matches_normalized = difflib.get_close_matches(
        item_normalized,
        normalized_valid_items,
        n=1,
        cutoff=cutoff
    )

    if closest_matches_normalized:
        matched_normalized = closest_matches_normalized[0]
        return normalized_to_original_map.get(matched_normalized)

    return None


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


def get_code_blocks(parsed_colab):
    relevant_sections = [
        f"{SECTIONS.SETUP.value} - {SECTIONS.INSTALL_AND_CLONE_REPO_CODE.value}",
        f"{SECTIONS.SETUP.value} - {SECTIONS.IMPORT_APIS_AND_INITIATE_DBS.value}",
        SECTIONS.INITIAL_ASSERTION.value,
        SECTIONS.ACTION.value,
        SECTIONS.FINAL_ASSERTION.value
    ]
    result_code_blocks = {section: [] for section in relevant_sections}
    result_code_blocks['setup_section'] = [preserve_state]
    all_code_blocks = [block for block in parsed_colab.get_all_blocks() if isinstance(block, CodeBlock)]
    # colab_cells = [
    #     {'cell_type': 'code', 'source': [preserve_state], 'metadata': {}, 'outputs': []}
    #     ]
    for section in relevant_sections:
        # print(f"In {section}")
        # colab_cells.append({'cell_type': 'markdown', 'source': [section], 'metadata': {}, 'outputs': []})

        if section == f"{SECTIONS.SETUP.value} - {SECTIONS.INSTALL_AND_CLONE_REPO_CODE.value}":        
            section_code_blocks = [block for block in all_code_blocks if block.logical_section==section]
            # print(f"Dependencies {section_code_blocks}")
            for section_code_block in section_code_blocks:
                code_without_pip = '\n'.join([line for line in section_code_block.content.split('\n') if not line.startswith('!pip')])
                # print(f"Code withot Pip {code_without_pip}")
                result_code_blocks[section].append(code_without_pip)
                # colab_cells.append({'cell_type': 'code', 'source': [code_without_pip], 'metadata': {}, 'outputs': []})
        elif section == f"{SECTIONS.SETUP.value} - {SECTIONS.IMPORT_APIS_AND_INITIATE_DBS.value}":
            section_code_blocks = [block for block in all_code_blocks if block.logical_section==section]
            section_code_block_count = len(section_code_blocks)
            # print(f"DB Code cells: {section_code_blocks}")
            for idx, section_code_block in enumerate(section_code_blocks):     
                # print(f"DB {idx}: {section_code_block}")       
                # if idx == section_code_block_count-1: # last block
                    # colab_cells.append({'cell_type': 'code', 'source': ['\nstart_block()\n'], 'metadata': {}, 'outputs': []})
                
                # colab_cells.append({'cell_type': 'code', 'source': [section_code_block.content], 'metadata': {}, 'outputs': []})
                if idx == section_code_block_count-1: # last block
                    result_code_blocks[section].append(section_code_block.content)
                else:
                    result_code_blocks['setup_section'].append(section_code_block.content)
                
                # if idx == section_code_block_count-1: # last block
                    # colab_cells.append({'cell_type': 'code', 'source': ['\nend_block()\n'], 'metadata': {}, 'outputs': []})
        else:
            # colab_cells.append({'cell_type': 'code', 'source': ['\nstart_block()\n'], 'metadata': {}, 'outputs': []})
            section_code_blocks = [block for block in all_code_blocks if block.logical_section==section]
            for section_code_block in section_code_blocks:            
                # colab_cells.append({'cell_type': 'code', 'source': [section_code_block.content], 'metadata': {}, 'outputs': []})
                result_code_blocks[section].append(section_code_block.content)
            # colab_cells.append({'cell_type': 'code', 'source': ['\nend_block()\n'], 'metadata': {}, 'outputs': []})
    return result_code_blocks



def create_auto_qc_notebook(code_blocks):
    nb_cells = []
    
    setup_section = "setup_section"
    setup_code_cells = code_blocks[setup_section]
    
    combined_cells = []
    for code_cell in setup_code_cells:
        combined_cells += [code_cell]    
    nb_cells.append({'cell_type': 'markdown', 'source': [setup_section], 'metadata': {}, 'outputs': []})
    nb_cells.append({'cell_type': 'code', 'source': combined_cells, 'metadata': {}, 'outputs': []})

    del code_blocks[setup_section]

    dependencies_section = f"{SECTIONS.SETUP.value} - {SECTIONS.INSTALL_AND_CLONE_REPO_CODE.value}"
    dependencies_code_cells = code_blocks[dependencies_section]
    
    combined_cells = []
    for code_cell in dependencies_code_cells:
        combined_cells += [code_cell]
    nb_cells.append({'cell_type': 'markdown', 'source': [dependencies_section], 'metadata': {}, 'outputs': []})
    nb_cells.append({'cell_type': 'code', 'source': combined_cells, 'metadata': {}, 'outputs': []})

    del code_blocks[dependencies_section]

    init_section = f"{SECTIONS.SETUP.value} - {SECTIONS.IMPORT_APIS_AND_INITIATE_DBS.value}"
    init_code_cells = code_blocks[init_section]
    nb_cells.append({'cell_type': 'markdown', 'source': [init_section], 'metadata': {}, 'outputs': []})
    combined_cells = []
    for cell in init_code_cells:
        combined_cells += [cell]
    nb_cells.append({'cell_type': 'code', 'source': ['\nstart_block()\n'], 'metadata': {}, 'outputs': []})
    nb_cells.append({'cell_type': 'code', 'source': ['\n'.join(combined_cells)], 'metadata': {}, 'outputs': []})
    nb_cells.append({'cell_type': 'code', 'source': ['\nend_block()\n'], 'metadata': {}, 'outputs': []})
    del code_blocks[init_section]

    fa_section = SECTIONS.FINAL_ASSERTION.value
    fa_code_cells = code_blocks[fa_section]
    nb_cells.append({'cell_type': 'markdown', 'source': [f'{fa_section}_NO_ACTION'], 'metadata': {}, 'outputs': []})
    combined_cells = []
    for cell in fa_code_cells:
        combined_cells += [cell]
    nb_cells.append({'cell_type': 'code', 'source': ['\nstart_block()\n'], 'metadata': {}, 'outputs': []})
    nb_cells.append({'cell_type': 'code', 'source': ['\n'.join(combined_cells)], 'metadata': {}, 'outputs': []})
    nb_cells.append({'cell_type': 'code', 'source': ['\nend_block()\n'], 'metadata': {}, 'outputs': []})

    for header in [SECTIONS.INITIAL_ASSERTION.value, SECTIONS.ACTION.value, SECTIONS.FINAL_ASSERTION.value]:
        nb_cells.append({'cell_type': 'markdown', 'source': [header], 'metadata': {}, 'outputs': []})
        combined_cells = []
        for cell in code_blocks[header]:
            combined_cells += [cell]
        nb_cells.append({'cell_type': 'code', 'source': ['\nstart_block()\n'], 'metadata': {}, 'outputs': []})
        nb_cells.append({'cell_type': 'code', 'source': ['\n'.join(combined_cells)], 'metadata': {}, 'outputs': []})
        nb_cells.append({'cell_type': 'code', 'source': ['\nend_block()\n'], 'metadata': {}, 'outputs': []})

    notebook = nbformat.v4.new_notebook()
    notebook.cells = nb_cells
    notebook = nbformat.reads(json.dumps(notebook), as_version=4)
    return notebook