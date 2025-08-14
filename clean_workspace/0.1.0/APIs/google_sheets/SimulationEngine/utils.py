"""Utility functions for Google Sheets API simulation.

This module contains helper functions for managing user and file data
within the database. It provides functions for ensuring user and file
existence, and managing counters.
"""

from typing import List, Tuple
import re
from .db import DB

def _ensure_user(userId: str = "me") -> None:
    """Ensures that a user entry exists in the database.

    Args:
        userId: The ID of the user to ensure exists. Defaults to "me".
    """
    if userId not in DB:
        DB[userId] = {
            "files": {},
            "counters": {
                "spreadsheet": 0,
                "sheet": 0
            }
        }

def _ensure_file(fileId: str, userId: str = "me") -> None:
    """Ensures that a file exists in the user's files.

    Args:
        fileId: The ID of the file to ensure exists.
        userId: The ID of the user who owns the file. Defaults to "me".
    """
    _ensure_user(userId)
    if fileId not in DB[userId]["files"]:
        DB[userId]["files"][fileId] = {
            "spreadsheet": None,
            "sheets": {}
        }

def _next_counter(counter_name: str, userId: str = "me") -> int:
    """Retrieves and increments the next counter value.

    Args:
        counter_name: The name of the counter to increment.
        userId: The ID of the user who owns the counter. Defaults to "me".

    Returns:
        The next counter value.
    """
    _ensure_user(userId)
    DB[userId]["counters"][counter_name] += 1
    return DB[userId]["counters"][counter_name] 


def update_dynamic_data(
    target_range_str: str,
    spreadsheet_data: dict,
    new_values: List[List[str]]
) -> None:
    """
    Dynamically updates a specific range by rebuilding the data grid.

    Args:
        target_range_str (str): The desired range in A1 notation.
        spreadsheet_data (dict): The spreadsheet data to update.
        new_values (List[List[str]]): The values to insert at the target range.

    Returns:
        bool: True if data was updated, False otherwise.
    """
    target_sheet, target_range = split_sheet_and_range(target_range_str)
    target_start_col, target_start_row, _, _ = parse_a1_range(target_range, spreadsheet_data)

    for stored_range_key, stored_values in spreadsheet_data.items():
        stored_sheet, stored_range = split_sheet_and_range(stored_range_key)
        if stored_sheet != target_sheet:
            continue

        stored_start_col, stored_start_row, stored_end_col, stored_end_row = parse_a1_range(stored_range, spreadsheet_data)

        # Check if the target range starts within the stored range
        if (
            stored_start_col <= target_start_col <= stored_end_col and
            stored_start_row <= target_start_row <= stored_end_row
        ):
            row_offset = target_start_row - stored_start_row
            col_offset = target_start_col - stored_start_col

            # 1. Create a deep copy of the grid to modify safely.
            new_grid = [row[:] for row in stored_values]

            # 2. Calculate required dimensions and resize the grid if necessary.
            num_new_rows = len(new_values)
            num_new_cols = max(len(row) for row in new_values) if new_values and any(new_values) else 0

            required_rows = row_offset + num_new_rows
            required_cols = col_offset + num_new_cols

            # Pad rows
            while len(new_grid) < required_rows:
                new_grid.append([])
            
            # Pad columns
            for i in range(len(new_grid)):
                while len(new_grid[i]) < required_cols:
                    new_grid[i].append("")

            # 3. Place new values into the resized grid.
            for i, new_row in enumerate(new_values):
                for j, new_cell in enumerate(new_row):
                    new_grid[row_offset + i][col_offset + j] = new_cell

            # 4. Explicitly replace the old data with the new, updated grid.
            # This is the key fix.
            spreadsheet_data[stored_range_key] = new_grid
            return True

    # If no matching range was found, create a new entry for the data.
    if target_range_str not in spreadsheet_data:
        spreadsheet_data[target_range_str] = new_values
        return True

    return False


def split_sheet_and_range(a1_range: str) -> Tuple[str, str]:
    """
    Splits a range like 'Sheet1!A1:D3' into ('Sheet1', 'A1:D3').
    Handles quoted sheet names like "'Sheet Name'!A1:D3" by preserving the quotes
    but normalizing for comparison.
    """
    match = re.match(r"^(.*?)!(.*)$", a1_range)
    if match:
        sheet_name = match.group(1).lower()
        range_part = match.group(2).lower()
        
        # For comparison purposes, we'll normalize the sheet name
        # by removing quotes and handling escaped quotes
        normalized_sheet_name = sheet_name
        if sheet_name.startswith("'") and sheet_name.endswith("'"):
            normalized_sheet_name = sheet_name[1:-1]
        normalized_sheet_name = normalized_sheet_name.replace("''", "'")
        
        return normalized_sheet_name, range_part
    else:
        return 'sheet1', a1_range.lower()
def parse_a1_range(a1_range: str, spreadsheet_data: dict) -> Tuple[int, int, int, int]:
    def col_to_index(col: str) -> int:
        result = 0
        for c in col:
            result = result * 26 + (ord(c.upper()) - ord('A')) + 1
        return result

    if ':' not in a1_range:
        if re.match(r"^[A-Za-z]+$", a1_range):
            col_idx = col_to_index(a1_range)
            max_rows = max(len(rows) for rows in spreadsheet_data.values()) if spreadsheet_data else 1
            return col_idx, 1, col_idx, max_rows
        elif re.match(r"^[A-Za-z]+\d+$", a1_range):
            col, row = re.match(r"([A-Za-z]+)(\d+)", a1_range).groups()
            return col_to_index(col), int(row), col_to_index(col), int(row)

    start, end = a1_range.split(':')

    if re.match(r"^[A-Za-z]+$", start) and re.match(r"^[A-Za-z]+$", end):
        start_col_idx = col_to_index(start)
        end_col_idx = col_to_index(end)
        max_rows = max(len(rows) for rows in spreadsheet_data.values()) if spreadsheet_data else 1
        return start_col_idx, 1, end_col_idx, max_rows

    start_col, start_row = re.match(r"([A-Za-z]+)(\d+)", start).groups()
    end_col, end_row = re.match(r"([A-Za-z]+)(\d+)", end).groups()

    return (
        col_to_index(start_col), int(start_row),
        col_to_index(end_col), int(end_row)
    )


def get_dynamic_data(target_range_str: str, spreadsheet_data: dict) -> List[List[str]]:
    """
    Retrieves data dynamically from a spreadsheet-like dictionary.

    This function matches the given target range against stored ranges and
    extracts the relevant subset of values, preserving the rest of the data structure.
    It supports:
      - A1 notation ranges with sheet names. The A1 notation is a syntax used to define a cell or range of cells with a string that contains the sheet name plus the starting and ending cell coordinates using column letters and row numbers (e.g., 'Sheet1!A1:D3')
      - Column-only ranges (e.g., 'A:B', treated as all rows)
      - Case-insensitive sheet name matching

    Args:
        target_range_str (str): The target range in A1 notation to fetch. The A1 notation is a syntax used to define a cell or range of cells with a string that contains the sheet name plus the starting and ending cell coordinates using column letters and row numbers like: "Sheet1!A1:D3" or "A1:D3"
        spreadsheet_data (dict): The dictionary containing stored sheet data.

    Returns:
        List[List[str]]: Extracted data as a 2D list. Returns an empty list if no overlap found.
    """
    target_sheet, target_range = split_sheet_and_range(target_range_str)
    target_start_col, target_start_row, target_end_col, target_end_row = parse_a1_range(target_range, spreadsheet_data)

    for stored_range_key, stored_values in spreadsheet_data.items():
        stored_sheet, stored_range = split_sheet_and_range(stored_range_key)
        
        # Compare normalized sheet names for matching
        if stored_sheet.lower() != target_sheet.lower():
            continue

        stored_start_col, stored_start_row, stored_end_col, stored_end_row = parse_a1_range(stored_range, spreadsheet_data)

        # Check for overlap
        if (
            stored_start_col <= target_end_col and stored_end_col >= target_start_col and
            stored_start_row <= target_end_row and stored_end_row >= target_start_row
        ):
            row_offset = target_start_row - stored_start_row
            col_offset = target_start_col - stored_start_col

            num_rows = target_end_row - target_start_row + 1
            num_cols = target_end_col - target_start_col + 1

            extracted_data = []
            for i in range(num_rows):
                stored_row_index = row_offset + i

                if 0 <= stored_row_index < len(stored_values):
                    row = stored_values[stored_row_index]
                    extracted_row = []

                    for j in range(num_cols):
                        stored_col_index = col_offset + j
                        if 0 <= stored_col_index < len(row):
                            extracted_row.append(row[stored_col_index])
                        else:
                            extracted_row.append("")  # Fill missing columns with empty string

                    extracted_data.append(extracted_row)
                else:
                    extracted_data.append([""] * num_cols)  # Fill missing rows

            return extracted_data

    return []

def col_to_index(col: str) -> int:
    result = 0
    for c in col:
        result = result * 26 + (ord(c.upper()) - ord('A')) + 1
    return result
    
def cell2ints(cell: str) -> Tuple[int, int]:
    """
    Converts a cell like 'A1' to a tuple of (row index, column index).
    If a single letter is provided, it is treated as a column index.
    Returns a tuple of Nones if the cell is invalid.
    """
    if re.match(r"^[A-Za-z]+$", cell):
        col_idx = col_to_index(cell)
        return 1, col_idx
    elif re.match(r"^[A-Za-z]+\d+$", cell):
        col, row = re.match(r"([A-Za-z]+)(\d+)", cell).groups()
        return int(row), col_to_index(col)
    else:
        return None, None

def range2ints(a1_range: str) -> Tuple[str, int, int, int, int]:
    """
    Converts a range like 'A1:D3' or 'Sheet1!A1:D3' to a tuple of (sheet name, start row index, start column index, end row index, end column index).
    Must have a colon between the start and end ranges.
    Returns a tuple of Nones if the range is invalid.
    """
    if ':' not in a1_range:
        return None, None, None, None, None

    sheet_name, a1_range = split_sheet_and_range(a1_range)
    
    start, end = a1_range.split(':')

    start_row, start_col = cell2ints(start)
    end_row, end_col = cell2ints(end)

    return sheet_name, start_row, start_col, end_row, end_col

def normalize_for_comparison(range_str: str) -> tuple:
    """
    Normalizes a range string for comparison by extracting and normalizing sheet name and range part.
    
    Args:
        range_str (str): The range string to normalize, e.g., 'Sheet1!A1:B2'
        
    Returns:
        tuple: A tuple of (normalized_sheet_name, normalized_range_part)
    """
    if '!' in range_str:
        sheet_part, range_part = range_str.split('!', 1)
        # Normalize sheet name by removing quotes and handling escaped quotes
        if sheet_part.startswith("'") and sheet_part.endswith("'"):
            sheet_part = sheet_part[1:-1].replace("''", "'")
        return sheet_part.lower(), range_part.lower()
    else:
        return "sheet1", range_str.lower()

def extract_sheet_name(range_str: str) -> str:
    """
    Extracts the sheet name from a range string.
    
    Args:
        range_str (str): The range string, e.g., 'Sheet1!A1:B2'
        
    Returns:
        str: The sheet name, or "Sheet1" if no sheet name is specified
    """
    if '!' in range_str:
        return range_str.split('!', 1)[0]
    return "Sheet1"

def extract_range_part(range_str: str) -> str:
    """
    Extracts the range part from a range string.
    
    Args:
        range_str (str): The range string, e.g., 'Sheet1!A1:B2'
        
    Returns:
        str: The range part (e.g., 'A1:B2')
    """
    if '!' in range_str:
        return range_str.split('!', 1)[1]
    return range_str

def parse_a1_notation_extended(a1_notation: str) -> tuple:
    """
    Parses A1 notation into row and column indices.
    
    Args:
        a1_notation (str): The A1 notation to parse, e.g., 'A1:B2'
        
    Returns:
        tuple: A tuple of (start_row, start_col, end_row, end_col)
    """
    # Convert column letters to index (1-based)
    def col_to_index(col_str):
        result = 0
        for c in col_str:
            result = result * 26 + (ord(c.upper()) - ord('A')) + 1
        return result
    
    # Extract row and column from cell reference
    def extract_row_col(cell):
        # Handle column-only references like 'A' or 'BC'
        if re.match(r'^[A-Za-z]+$', cell):
            return 1, col_to_index(cell)  # Default to row 1
        
        # Handle regular cell references like 'A1' or 'BC123'
        match = re.match(r'([A-Za-z]+)(\d+)', cell)
        if match:
            col_str, row_str = match.groups()
            return int(row_str), col_to_index(col_str)
        
        return None, None
    
    # Remove sheet name if present
    if '!' in a1_notation:
        a1_notation = a1_notation.split('!', 1)[1]
    
    # Parse the range
    if ':' in a1_notation:
        start_cell, end_cell = a1_notation.split(':')
        start_row, start_col = extract_row_col(start_cell)
        end_row, end_col = extract_row_col(end_cell)
        
        # For column-only ranges like 'A:B'
        if start_row is None:
            start_row = 1
        if end_row is None:
            end_row = 1000  # Arbitrary large number
            
        return start_row, start_col, end_row, end_col
    else:
        row, col = extract_row_col(a1_notation)
        return row, col, row, col

def is_range_subset(subset_range: str, full_range: str) -> bool:
    """
    Checks if a range is a subset of another range.
    
    Args:
        subset_range (str): The potential subset range
        full_range (str): The full range to check against
        
    Returns:
        bool: True if subset_range is contained within full_range, False otherwise
    """
    subset_sheet, subset_range_part = normalize_for_comparison(subset_range)
    full_sheet, full_range_part = normalize_for_comparison(full_range)
    
    # Different sheets, not a subset
    if subset_sheet != full_sheet:
        return False
    
    # Parse the ranges
    subset_start_row, subset_start_col, subset_end_row, subset_end_col = parse_a1_notation_extended(subset_range_part)
    full_start_row, full_start_col, full_end_row, full_end_col = parse_a1_notation_extended(full_range_part)
    
    # Check if subset is within the full range
    return (full_start_row <= subset_start_row <= full_end_row and
            full_start_col <= subset_start_col <= full_end_col and
            full_start_row <= subset_end_row <= full_end_row and
            full_start_col <= subset_end_col <= full_end_col)

def validate_sheet_name(range_str: str, spreadsheet_data: dict) -> None:
    """
    Validates that a range string either has an explicit sheet name or the default sheet is "Sheet1".
    
    Args:
        range_str (str): The range string to validate, e.g., 'Sheet1!A1:B2' or 'A1:B2'
        spreadsheet_data (dict): The spreadsheet data dictionary, used to determine default sheet
        
    Raises:
        ValueError: If the range doesn't have an explicit sheet name and the default sheet is not "Sheet1"
    """
    # Check if the range has an explicit sheet name
    has_explicit_sheet = '!' in range_str
    
    if not has_explicit_sheet:
        # If there's no explicit sheet name, check if there are any sheets other than Sheet1
        non_sheet1_exists = False
        for stored_key in spreadsheet_data.keys():
            sheet_name, _ = split_sheet_and_range(stored_key)
            if sheet_name.lower() != 'sheet1':
                non_sheet1_exists = True
                break
        
        # If there are sheets other than Sheet1, reject the range without explicit sheet name
        if non_sheet1_exists:
            raise ValueError("Range without explicit sheet name is only allowed when the default sheet is 'Sheet1'")