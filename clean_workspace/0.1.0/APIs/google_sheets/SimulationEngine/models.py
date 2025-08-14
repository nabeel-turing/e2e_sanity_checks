from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, field_validator
import re

class ValueRangeModel(BaseModel):
    """
    Pydantic model for validating individual items in the 'data' list argument.
    """
    range: str
    values: List[List[Any]] # A list of rows, where each row is a list of cell values

# Common model for sheet properties, allowing extra fields
class SheetPropertiesBaseModel(BaseModel):
    class Config:
        extra = "allow"

class AddSheetPropertiesModel(SheetPropertiesBaseModel):
    sheetId: Any # Type is not strictly defined, could be int or str

class AddSheetRequestPayloadModel(BaseModel):
    properties: AddSheetPropertiesModel

class DeleteSheetRequestPayloadModel(BaseModel):
    sheetId: Any

class UpdateSheetPropertiesInfoModel(SheetPropertiesBaseModel):
    sheetId: Any

class UpdateSheetPropertiesRequestPayloadModel(BaseModel):
    properties: UpdateSheetPropertiesInfoModel
    fields: str # Comma-separated field names

class CellRangeModel(BaseModel):
    sheetId: Any
    startRowIndex: int
    endRowIndex: int
    startColumnIndex: int
    endColumnIndex: int

class UpdateCellsPayloadModel(BaseModel):
    range: CellRangeModel
    rows: List[Any] # Structure of 'rows' items is not detailed, so List[Any]

class UpdateSheetPropertiesSimplePayloadModel(BaseModel):
    properties: UpdateSheetPropertiesInfoModel # properties key and its sheetId are effectively mandatory
    fields: Optional[str] = "" # fields key is optional

class AppendSpecificArgsModel(BaseModel):
    """
    Pydantic model for validating specific arguments of the 'append' function,
    particularly those with enum-like constraints or complex structures.
    """
    valueInputOption: Literal['RAW', 'USER_ENTERED']
    values: List[List[Any]] # Validates that 'values' is a list of lists.
    insertDataOption: Optional[Literal['OVERWRITE', 'INSERT_ROWS']] = None
    responseValueRenderOption: Optional[Literal['FORMATTED_VALUE', 'UNFORMATTED_VALUE', 'FORMULA']] = None
    responseDateTimeRenderOption: Optional[Literal['SERIAL_NUMBER', 'FORMATTED_STRING']] = None
    majorDimension: Literal['ROWS', 'COLUMNS'] = "ROWS"

    class Config:
        extra = 'forbid' # Ensure no unexpected arguments are passed if model is used with **kwargs

#  --- Models for Spreadsheet and its components
class SpreadsheetPropertiesModel(BaseModel):
    title: Optional[str] = "Untitled Spreadsheet"
    locale: Optional[str] = None
    autoRecalc: Optional[str] = None
    timeZone: Optional[str] = None
    defaultFormat: Optional[Dict[str, Any]] = None
    iterativeCalculationSettings: Optional[Dict[str, Any]] = None
    owner: Optional[str] = None
    permissions: Optional[List[Dict[str, Any]]] = None
    parents: Optional[List[str]] = None
    size: Optional[int] = None
    trashed: Optional[bool] = None
    starred: Optional[bool] = None
    createdTime: Optional[str] = None
    modifiedTime: Optional[str] = None

class SheetGridPropertiesModel(BaseModel):
    rowCount: Optional[int] = None
    columnCount: Optional[int] = None

class SheetPropertiesModel(BaseModel):
    sheetId: Optional[str] = None
    title: str
    index: Optional[int] = None
    sheetType: Optional[str] = None
    gridProperties: Optional[Dict[str, Any]] = None

    @field_validator('sheetId', mode='before')
    @classmethod
    def convert_sheetid_to_str(cls, value):
        """Convert int sheetId to str to maintain compatibility."""
        if isinstance(value, int):
            return str(value)
        return value

class SheetModel(BaseModel):
    properties: Optional[SheetPropertiesModel] = None
    data: Optional[List[Dict[str, Any]]] = None
    merges: Optional[List[Dict[str, Any]]] = None
    conditionalFormats: Optional[List[Dict[str, Any]]] = None
    filterViews: Optional[List[Dict[str, Any]]] = None
    protectedRanges: Optional[List[Dict[str, Any]]] = None
    basicFilter: Optional[Dict[str, Any]] = None
    charts: Optional[List[Dict[str, Any]]] = None
    bandedRanges: Optional[List[Dict[str, Any]]] = None
    developerMetadata: Optional[List[Dict[str, Any]]] = None

class SpreadsheetDataModel(BaseModel):
    spreadsheetId: Optional[str] = None
    valueRanges: Optional[List[ValueRangeModel]] = None
    properties: Optional[Dict[str, Any]] = None
    sheets: Optional[List[Dict[str, Any]]] = None

class SpreadsheetModel(BaseModel):
    id: Optional[str] = None
    properties: Optional[SpreadsheetPropertiesModel] = None
    sheets: Optional[List[SheetModel]] = None
    data: Optional[SpreadsheetDataModel] = None

# Common model for sheet properties, allowing extra fields
class SheetPropertiesBaseModel(BaseModel):
    class Config:
        extra = "allow"

class AddSheetPropertiesModel(SheetPropertiesBaseModel):
    sheetId: Any # Type is not strictly defined, could be int or str

class AddSheetRequestPayloadModel(BaseModel):
    properties: AddSheetPropertiesModel

class DeleteSheetRequestPayloadModel(BaseModel):
    sheetId: Any

class UpdateSheetPropertiesInfoModel(SheetPropertiesBaseModel):
    sheetId: Any

class UpdateSheetPropertiesRequestPayloadModel(BaseModel):
    properties: UpdateSheetPropertiesInfoModel
    fields: str # Comma-separated field names

class CellRangeModel(BaseModel):
    sheetId: Any
    startRowIndex: int
    endRowIndex: int
    startColumnIndex: int
    endColumnIndex: int

class UpdateCellsPayloadModel(BaseModel):
    range: CellRangeModel
    rows: List[Any] # Structure of 'rows' items is not detailed, so List[Any]

class UpdateSheetPropertiesSimplePayloadModel(BaseModel):
    properties: UpdateSheetPropertiesInfoModel # properties key and its sheetId are effectively mandatory
    fields: Optional[str] = "" # fields key is optional

class AppendSpecificArgsModel(BaseModel):
    """
    Pydantic model for validating specific arguments of the 'append' function,
    particularly those with enum-like constraints or complex structures.
    """
    valueInputOption: Literal['RAW', 'USER_ENTERED']
    values: List[List[Any]] # Validates that 'values' is a list of lists.
    insertDataOption: Optional[Literal['OVERWRITE', 'INSERT_ROWS']] = None
    responseValueRenderOption: Optional[Literal['FORMATTED_VALUE', 'UNFORMATTED_VALUE', 'FORMULA']] = None
    responseDateTimeRenderOption: Optional[Literal['SERIAL_NUMBER', 'FORMATTED_STRING']] = None
    majorDimension: Literal['ROWS', 'COLUMNS'] = "ROWS"

    class Config:
        extra = 'forbid' # Ensure no unexpected arguments are passed if model is used with **kwargs

class GridRangeModel(BaseModel):
    """
    Pydantic model for grid range specifications.
    """
    sheetId: Optional[int] = None
    startRowIndex: Optional[int] = None
    endRowIndex: Optional[int] = None
    startColumnIndex: Optional[int] = None
    endColumnIndex: Optional[int] = None
    
    class Config:
        extra = "allow"

class DeveloperMetadataLookupModel(BaseModel):
    """
    Pydantic model for developer metadata lookup specifications.
    """
    metadataKey: Optional[str] = None
    metadataValue: Optional[str] = None
    metadataId: Optional[int] = None
    
    class Config:
        extra = "allow"

class A1RangeInput(BaseModel):
    range: str

    @field_validator('range')
    def validate_a1_range(cls, value):
        """
        Validates that the given value is a valid A1 notation, supporting:
        - Single cell: A1
        - Cell range: A1:B2
        - Full column range: A:B
        - Mixed range: A2:Z (cell to column)
        - Optional sheet name: Sheet1!A1, Sheet1!A1:B2, Sheet1!A:B, Sheet1!A2:Z
        - Quoted sheet names: 'My Sheet'!A1:B2, 'John''s Sheet'!A1 (with escaped quotes)
        """
        # Check for empty string
        if not value:
            raise ValueError("Invalid A1 notation: Empty string is not allowed.")
            
        # Modified regex pattern to better handle complex sheet names and edge cases
        pattern = r"""
            ^                                       # Start of string
            (?:                                     # Optional sheet name group (non-capturing)
                (?:                                 # Sheet name can be either:
                    '(?:[^']|'')*'                  # Quoted sheet name (with optional escaped quotes)
                    |                               # OR
                    [A-Za-z0-9_]+                   # Unquoted sheet name (alphanumeric + underscore)
                )
                !                                   # Exclamation mark after sheet name
            )?                                      # Sheet name is optional
            (?:                                     # Range part (non-capturing)
                (?:[A-Za-z]{1,3}\d+)               # Cell reference like A1, AA1, etc.
                (?::[A-Za-z]{1,3}\d+)?             # Optional range end with cell like :B2
                |                                   # OR
                (?:[A-Za-z]{1,3}\d+)               # Cell reference 
                (?::[A-Za-z]{1,3})?                # Optional range end with just column like :B
                |                                   # OR
                (?:[A-Za-z]{1,3})                  # Just column like A
                (?::[A-Za-z]{1,3})?                # Optional range end like :B
            )                                       # End of range part
            $                                       # End of string
        """
        
        match = re.match(pattern, value, re.VERBOSE)
        if not match:
            raise ValueError(
                f"Invalid A1 notation: '{value}'. Must be one of:\n"
                "  - 'A1'\n"
                "  - 'A1:B2'\n"
                "  - 'A1:Z'\n"
                "  - 'A:B'\n"
                "  - 'Sheet1!A1'\n"
                "  - 'Sheet1!A1:B2'\n"
                "  - 'Sheet1!A1:Z'\n"
                "  - 'Sheet1!A:B'\n"
                "  - 'My Sheet'!A1:B2 (quoted sheet names)"
            )

        # Extract range part after '!' (or entire string if no sheet name)
        if '!' in value:
            range_part = value.split('!', 1)[1]
        else:
            range_part = value
            
        # Check for invalid formats like A0 (row 0 doesn't exist)
        if re.search(r'[A-Za-z]{1,3}0', range_part):
            raise ValueError("Invalid A1 notation: Row 0 doesn't exist.")
            
        # Check for invalid formats like AAAA1 (column too long)
        if re.search(r'[A-Za-z]{4,}\d+', range_part):
            raise ValueError("Invalid A1 notation: Column identifier too long (max 3 letters).")
            
        # Check for invalid formats with multiple colons
        if range_part.count(':') > 1:
            raise ValueError("Invalid A1 notation: Too many colons in range.")

        # Validate order in ranges
        if ':' in range_part:
            start_part, end_part = range_part.split(':')
            
            # Empty part after colon
            if not end_part:
                raise ValueError("Invalid A1 notation: Missing end range.")
                
            # For column range (A:B)
            if re.match(r'^[A-Za-z]{1,3}$', start_part) and re.match(r'^[A-Za-z]{1,3}$', end_part):
                if not cls._is_column_before(start_part, end_part):
                    raise ValueError(f"Start column '{start_part}' must come before end column '{end_part}' in A1 notation.")
            
            # For cell range (A1:B2)
            elif re.match(r'^[A-Za-z]{1,3}\d+$', start_part) and re.match(r'^[A-Za-z]{1,3}\d+$', end_part):
                start_col, start_row = cls._extract_col_row(start_part)
                end_col, end_row = cls._extract_col_row(end_part)
                
                if not cls._is_column_before(start_col, end_col):
                    raise ValueError(f"Start column '{start_col}' must come before end column '{end_col}' in A1 notation.")
                if int(start_row) > int(end_row):
                    raise ValueError(f"Start row '{start_row}' must come before end row '{end_row}' in A1 notation.")
            
            # For mixed range (A2:Z) - cell to column
            elif re.match(r'^[A-Za-z]{1,3}\d+$', start_part) and re.match(r'^[A-Za-z]{1,3}$', end_part):
                start_col, _ = cls._extract_col_row(start_part)
                end_col = end_part
                if not cls._is_column_before(start_col, end_col):
                    raise ValueError(f"Start column '{start_col}' must come before end column '{end_col}' in A1 notation.")
                # No row validation needed for open-ended ranges
        
        # Return the original value to preserve the format
        return value

    @staticmethod
    def _extract_col_row(cell_ref):
        """
        Extracts column and row from a cell reference like 'A1'.
        Returns a tuple of (column, row).
        """
        match = re.match(r'([A-Za-z]{1,3})(\d+)', cell_ref)
        if match:
            return match.groups()
        return (cell_ref, None)  # For column-only references like 'A'

    @staticmethod
    def _is_column_before(col1: str, col2: str) -> bool:
        """
        Compares two column references in Google Sheets order.
        Returns True if col1 comes before col2.
        """
        def col_to_num(col: str) -> int:
            result = 0
            for c in col.upper():
                result = result * 26 + (ord(c) - ord('A')) + 1
            return result
        
        return col_to_num(col1) <= col_to_num(col2)

class DataFilterModel(BaseModel):
    a1Range: Optional[str] = None
    gridRange: Optional[GridRangeModel] = None
    developerMetadataLookup: Optional[DeveloperMetadataLookupModel] = None
    # If a filter dict is empty, e.g., {}, it will pass this model as all fields are optional.
    # This seems consistent with how the original code might handle it (filter_dict.get("a1Range") would be None).

    @field_validator('a1Range')
    def validate_a1_range(cls, value):
        """Validate A1 range if provided."""
        if value is not None:
            try:
                A1RangeInput(range=value)
            except ValueError as e:
                raise ValueError(f"Invalid A1 range: {e}")
        return value
    
    def model_post_init(self, __context):
        """Post-initialization validation to ensure at least one filter is provided."""
        # Only validate if this is not an empty filter (which is allowed)
        if any([self.a1Range, self.gridRange, self.developerMetadataLookup]):
            # If any filter is provided, validate that it's properly formed
            pass
