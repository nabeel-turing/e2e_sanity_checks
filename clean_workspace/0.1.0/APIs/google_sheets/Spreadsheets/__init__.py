"""Google Sheets API Simulation.

This package provides a simulation of the Google Sheets API, including resources for
managing spreadsheets and their values. It implements the core functionality of the
Google Sheets API for testing and development purposes.

Available Resources:
- Spreadsheets: For managing spreadsheet documents
- SpreadsheetValues: For managing cell values and ranges
"""

import uuid
from typing import Dict, Any, Optional, List

from pydantic import ValidationError

from . import SpreadsheetValues
from . import Sheets

from ..SimulationEngine.db import DB
from ..SimulationEngine.custom_errors import InvalidRequestError, UnsupportedRequestTypeError
from ..SimulationEngine.models import (AddSheetRequestPayloadModel, DeleteSheetRequestPayloadModel,
                                                   UpdateSheetPropertiesRequestPayloadModel, UpdateCellsPayloadModel,
                                                   UpdateSheetPropertiesSimplePayloadModel, A1RangeInput,
                                                   DataFilterModel, SpreadsheetModel)
from ..SimulationEngine.utils import get_dynamic_data

__all__ = [
    "create",
    "get",
    "getByDataFilter",
    "batchUpdate",
    "SpreadsheetValues",
    "Sheets",
]


def create(spreadsheet: Dict[str, Any]) -> Dict[str, Any]:
    """Creates a new spreadsheet.

    Args:
        spreadsheet (Dict[str, Any]): Dictionary containing:
            - 'id' (Optional[str]): IGNORED - The spreadsheet ID is auto-generated.
            - 'properties' (Optional[Dict[str, Any]]): Dictionary of spreadsheet properties with keys:
                - 'title' (Optional[str]): The title of the spreadsheet (defaults to "Untitled Spreadsheet")
                - 'locale' (Optional[str]): The locale of the spreadsheet
                - 'autoRecalc' (Optional[str]): The auto-recalculation setting
                - 'timeZone' (Optional[str]): The time zone of the spreadsheet
                - 'defaultFormat' (Optional[Dict[str, Any]]): Default cell formatting
                - 'iterativeCalculationSettings' (Optional[Dict[str, Any]]): Iterative calculation settings
            	- 'owner' (Optional[str]): Owner email address
                - 'permissions' (Optional[List[Dict[str, Any]]]): List of permissions
                - 'parents' (Optional[List[str]]): List of parent folder IDs
                - 'size' (Optional[int]): File size in bytes
                - 'trashed' (Optional[bool]): Whether the file is trashed
                - 'starred' (Optional[bool]): Whether the file is starred
                - 'createdTime' (Optional[str]): Creation timestamp
                - 'modifiedTime' (Optional[str]): Last modification timestamp
            - 'sheets' (Optional[List[Dict[str, Any]]]): List of sheet dictionaries. If empty, a default "Sheet1" will be created.
                - 'properties' (Optional[Dict[str, Any]]): Sheet properties including:
                    - 'sheetId' (Optional[str]): Unique identifier for the sheet
                    - 'title' (str): Title of the sheet
                    - 'index' (int): Position of the sheet
                    - 'sheetType' (Optional[str]): Type of the sheet 
                    - 'gridProperties' (Optional[Dict[str, Any]]): Grid properties
                - 'data' (Optional[List[Dict[str, Any]]]): Sheet data using A1 notation. The key is the range in A1 notation. The value is a list of lists of cell values.
                - 'merges' (Optional[List[Dict[str, Any]]]): Cell merges
                - 'conditionalFormats' (Optional[List[Dict[str, Any]]]): Conditional formatting
                - 'filterViews' (Optional[List[Dict[str, Any]]]): Filter views
                - 'protectedRanges' (Optional[List[Dict[str, Any]]]): Protected ranges
                - 'basicFilter' (Optional[Dict[str, Any]]): Basic filter settings
                - 'charts' (Optional[List[Dict[str, Any]]]): Embedded charts
                - 'bandedRanges' (Optional[List[Dict[str, Any]]]): Banded ranges
                - 'developerMetadata' (Optional[List[Dict[str, Any]]]): Developer metadata
            - 'data' (Optional[Dict[str, Any]]): Dictionary of spreadsheet data with the following keys which are required if present:
                - 'spreadsheetId' (str): The spreadsheet ID
                - 'valueRanges' (List[Dict[str, Any]]): List of value ranges
                - 'properties' (Dict[str, Any]): Spreadsheet properties
                - 'sheets' (List[Dict[str, Any]]): List of sheets

    Returns:
        Dict[str, Any]: Dictionary containing the created spreadsheet data with keys:
            - 'id' (str): The spreadsheet ID
            - 'driveId' (str): The drive ID
            - 'name' (str): The spreadsheet name
            - 'mimeType' (str): The MIME type
            - 'properties' (Dict[str, Any]): Spreadsheet properties
            - 'sheets' (List[Dict[str, Any]]): List of sheets
            - 'data' (Dict[str, Any]): Spreadsheet data
            - 'owners' (List[str]): List of owner email addresses
            - 'permissions' (List[Dict[str, Any]]): List of permissions
            - 'parents' (List[str]): List of parent folder IDs
            - 'size' (int): File size in bytes
            - 'trashed' (bool): Whether the file is trashed
            - 'starred' (bool): Whether the file is starred
            - 'createdTime' (str): Creation timestamp
            - 'modifiedTime' (str): Last modification timestamp

    Raises:
        TypeError: If spreadsheet is not a dictionary or its fields have incorrect types.
        pydantic.ValidationError: If spreadsheet data does not conform to expected model structure.


    Note: 
        The 'id' field in the input is ignored - a new UUID is always generated.
        If no sheets are provided, a default "Sheet1" will be created automatically.
    """
    # Input validation
    if not isinstance(spreadsheet, dict):
        raise TypeError("spreadsheet must be a dictionary")
    
    # Validate the spreadsheet input using Pydantic model
    validated_spreadsheet = SpreadsheetModel(**spreadsheet)

    # Generate a new ID and collect input
    spreadsheet_id = str(uuid.uuid4())
    properties = spreadsheet.get("properties", {})
    sheets = spreadsheet.get("sheets", [])
    data = spreadsheet.get("data", {})

    # Default sheet if none provided
    if not sheets:
        sheets = [
            {
                "properties": {
                    "sheetId": "sheet1",
                    "title": "Sheet1",
                    "index": 0,
                    "sheetType": "GRID",
                    "gridProperties": {"rowCount": 1000, "columnCount": 26},
                }
            }
        ]

    # Build spreadsheet dict
    new_spreadsheet = {
        "id": spreadsheet_id,
        "driveId": "",
        "name": properties.get("title", "Untitled Spreadsheet"),
        "mimeType": "application/vnd.google-apps.spreadsheet",
        "properties": properties,
        "sheets": sheets,
        "data": data,
        "owners": [
            properties.get("owner", DB["users"]["me"]["about"]["user"]["emailAddress"])
        ],
        "permissions": properties.get("permissions", []),
        "parents": properties.get("parents", []),
        "size": properties.get("size", 0),
        "trashed": properties.get("trashed", False),
        "starred": properties.get("starred", False),
        "createdTime": properties.get("createdTime", ""),
        "modifiedTime": properties.get("modifiedTime", ""),
    }

    # Persist to in-memory DB
    user_id = "me"
    DB["users"][user_id]["files"][spreadsheet_id] = new_spreadsheet
    return new_spreadsheet


def get(
    spreadsheet_id: str, ranges: Optional[List[str]] = None, includeGridData: bool = False
) -> Dict[str, Any]:
    """Gets the latest version of a specified spreadsheet.

    Args:
        spreadsheet_id (str): The ID of the spreadsheet to retrieve.
        ranges (Optional[List[str]]): The ranges to retrieve, in A1 notation. The A1 notation is a syntax used to define a cell or range of cells with a string that contains the sheet name plus the starting and ending cell coordinates using column letters and row numbers like: "Sheet1!A1:D3" or "A1:D3"
                                                Defaults to None.
        includeGridData (bool): Whether to include grid data.
                                        Defaults to False.

    Returns:
        Dict[str, Any]: Dictionary containing:
            - 'id' (str): The spreadsheet ID
            - 'properties' (Dict[str, Any]): Spreadsheet properties
            - 'sheets' (List[Dict[str, Any]]): List of sheets
            - 'data' (Optional[Dict[str, Any]]): Grid data if includeGridData is True.
                If ranges is provided, returns only specified ranges.
                If ranges is None, returns all grid data.

    Raises:
        TypeError: If `spreadsheet_id` is not a string.
        TypeError: If `ranges` is provided and is not a list.
        TypeError: If `includeGridData` is not a boolean.
        ValueError: If `spreadsheet_id` is empty.
        ValueError: If `ranges` is provided and any of its elements are not strings.
        ValueError: If the spreadsheet is not found.
        ValueError: If the DB is not properly initialized for the user.
        ValueError: If any range string is invalid A1 notation.
    """
    # --- Input Validation ---
    if not isinstance(spreadsheet_id, str):
        raise TypeError("spreadsheet_id must be a string.")
        
    if not spreadsheet_id.strip():
        raise ValueError("spreadsheet_id cannot be empty.")

    if ranges is not None:
        if not isinstance(ranges, list):
            raise TypeError("ranges must be a list if provided.")
        if not all(isinstance(item, str) for item in ranges):
            raise ValueError("All items in ranges must be strings.")

    if not isinstance(includeGridData, bool):
        raise TypeError("includeGridData must be a boolean.")
    # --- End of Input Validation ---

    userId = "me" # This is part of the original function's logic
    # Ensure DB structure is present, for standalone execution of this snippet.
    # In your tests, setUp should handle this.
    if "users" not in DB or userId not in DB["users"] or "files" not in DB["users"][userId]:
        # This case might happen if DB is not set up as expected before calling get
        raise ValueError(f"DB not properly initialized for user {userId}")

    if spreadsheet_id not in DB["users"][userId]["files"]:
        raise ValueError("Spreadsheet not found") # Original error
    
    spreadsheet = DB["users"][userId]["files"][spreadsheet_id]
    
    response = {
        "id": spreadsheet.get("id"),
        "properties": spreadsheet.get("properties"),
        "sheets": spreadsheet.get("sheets"),
    }

    if includeGridData:
        grid_data = {}
        # Retrieve data for specified ranges. If spreadsheet has no 'data' field,
        # spreadsheet.get("data", {}) returns {}, so {}.get(r, []) results in [].
        # If a range doesn't exist in the data, it also defaults to [].
        spreadsheet_data_field = spreadsheet.get("data", {})

        if ranges and len(ranges) > 0:
            # Get data only for specified ranges
            for r in ranges:
                try:
                    validated_range = A1RangeInput(range=r)
                    range_value = validated_range.range
                except ValueError as e:
                    raise ValueError(f"Invalid range: {e}")
                grid_data[range_value] = get_dynamic_data(range_value, spreadsheet_data_field)
        else:
            # Get all grid data when ranges is None
            grid_data = spreadsheet_data_field
        
        response["data"] = grid_data
    
    return response


def getByDataFilter(
    spreadsheet_id: str, 
    includeGridData: bool = False, 
    dataFilters: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Gets spreadsheet data filtered by specified criteria.

    Args:
        spreadsheet_id (str): The ID of the spreadsheet to retrieve.
        includeGridData (bool): Whether to include grid data. Defaults to False.
        dataFilters (Optional[List[Dict[str, Any]]]): List of data filters. Defaults to None.
            Each filter contains:
            - 'a1Range' (Optional[str]): The range in A1 notation
            - 'gridRange' (Optional[Dict[str, Any]]): Grid range specification
            - 'developerMetadataLookup' (Optional[Dict[str, Any]]): Developer metadata lookup with keys:
                - 'metadataKey' (Optional[str]): Key of the metadata to look up
                - 'metadataValue' (Optional[str]): Value of the metadata

    Returns:
        Dict[str, Any]: Dictionary containing:
            - 'id' (str): The spreadsheet ID
            - 'properties' (Dict[str, Any]): Spreadsheet properties
            - 'sheets' (List[Dict[str, Any]]): List of sheets
            - 'data' (Dict[str, Any]): Combined data after applying filters. Only included 
              when both includeGridData is True and valid filters are provided. Or else 'data' is not included.

    Raises:
        TypeError: If spreadsheet_id is not a string.
        TypeError: If includeGridData is not a boolean.
        TypeError: If dataFilters is provided and is not a list.
        ValueError: If the spreadsheet is not found.
        ValueError: If the DB is not properly initialized for the user.
        ValueError: If dataFilters contains invalid filter specifications.
        pydantic.ValidationError: If filter data does not match the expected schema.
    """
    # --- Input Validation ---
    if not isinstance(spreadsheet_id, str):
        raise TypeError("spreadsheet_id must be a string.")
    
    if not isinstance(includeGridData, bool):
        raise TypeError("includeGridData must be a boolean.")
    
    validated_filters = []
    if dataFilters is not None:
        if not isinstance(dataFilters, list):
            raise TypeError("dataFilters must be a list if provided.")
        
        # Validate each filter using Pydantic model
        for i, filter_item in enumerate(dataFilters):
            if not isinstance(filter_item, dict):
                raise ValueError(f"dataFilters[{i}] must be a dictionary.")
            try:
                validated_filter = DataFilterModel(**filter_item)
                validated_filters.append(validated_filter)
            except ValidationError as e:
                raise ValueError(f"Invalid filter at index {i}: {e}")
            
    # --- End of Input Validation ---

    userId = "me"
    
    # Ensure DB structure is present
    if "users" not in DB:
        raise ValueError("DB not properly initialized: missing 'users'")
    
    if userId not in DB["users"]:
        raise ValueError("DB not properly initialized: missing user")
    
    if "files" not in DB["users"][userId]:
        raise ValueError("DB not properly initialized: missing 'files' for user")

    if spreadsheet_id not in DB["users"][userId]["files"]:
        raise ValueError("Spreadsheet not found")

    spreadsheet_dict = DB["users"][userId]["files"][spreadsheet_id]
    response = {
        "id": spreadsheet_dict.get("id"),
        "properties": spreadsheet_dict.get("properties", {}),
        "sheets": spreadsheet_dict.get("sheets", []),
    }

    # Only process data if includeGridData is True and we have valid filters
    if includeGridData and validated_filters:
        filtered_data = {}
        spreadsheet_data_field = spreadsheet_dict.get("data", {})
        
        # Convert column numbers to letters - helper function used by both grid and metadata filters
        def col_num_to_letter(col_num):
            result = ""
            while col_num >= 0:
                result = chr(col_num % 26 + ord('A')) + result
                col_num = col_num // 26 - 1
                if col_num < 0:
                    break
            return result
        
        # Process each validated filter
        for filter_model in validated_filters:
                if filter_model.a1Range:
                    # Handle A1 range filter
                    validated_range = A1RangeInput(range=filter_model.a1Range)
                    range_value = validated_range.range
                    data = get_dynamic_data(range_value, spreadsheet_data_field)
                    filtered_data[range_value] = data

                
                elif filter_model.gridRange:
                    # Handle grid range filter
                    grid_range = filter_model.gridRange
                    # Convert grid range to A1 notation for consistency with existing utils
                    sheet_id = grid_range.sheetId or 0  # Default to first sheet
                    
                    # Find sheet name by sheetId
                    sheet_name = None
                    for sheet in spreadsheet_dict.get("sheets", []):
                        if sheet.get("properties", {}).get("sheetId") == str(sheet_id):
                            sheet_name = sheet.get("properties", {}).get("title", "Sheet1")
                            break
                    
                    if not sheet_name:
                        sheet_name = "Sheet1"  # Default sheet name
                    
                    # Convert grid coordinates to A1 notation
                    start_row = grid_range.startRowIndex or 0
                    end_row = grid_range.endRowIndex or 1000  # Default large range
                    start_col = grid_range.startColumnIndex or 0
                    end_col = grid_range.endColumnIndex or 26  # Default to column Z
                    
                    start_col_letter = col_num_to_letter(start_col)
                    end_col_letter = col_num_to_letter(end_col - 1)  # End is exclusive
                    
                    # Convert to 1-based row numbers for A1 notation
                    a1_range = f"{sheet_name}!{start_col_letter}{start_row + 1}:{end_col_letter}{end_row}"
                    
                    data = get_dynamic_data(a1_range, spreadsheet_data_field)
                    filtered_data[a1_range] = data
                
                elif filter_model.developerMetadataLookup:
                    # Handle developer metadata lookup filter
                    # For now, we'll implement basic metadata filtering
                    # This would typically look through sheet metadata and find matching ranges
                    metadata_lookup = filter_model.developerMetadataLookup
                    
                    # Search through sheets for matching developer metadata
                    for sheet in spreadsheet_dict.get("sheets", []):
                        sheet_metadata = sheet.get("developerMetadata", [])
                        sheet_name = sheet.get("properties", {}).get("title", "Sheet1")
                        
                        for metadata in sheet_metadata:
                            # Check if metadata matches the lookup criteria
                            match = True
                            if metadata_lookup.metadataKey and metadata.get("metadataKey") != metadata_lookup.metadataKey:
                                match = False
                            if metadata_lookup.metadataValue and metadata.get("metadataValue") != metadata_lookup.metadataValue:
                                match = False
                            if metadata_lookup.metadataId and metadata.get("metadataId") != metadata_lookup.metadataId:
                                match = False
                            
                            if match:
                                # If metadata matches, include the associated range
                                # For simplicity, we'll use the entire sheet if no specific range is defined
                                metadata_range = metadata.get("location", {}).get("dimensionRange")
                                if metadata_range:
                                    # Convert metadata range to A1 notation
                                    start_index = metadata_range.get("startIndex", 0)
                                    end_index = metadata_range.get("endIndex", 1000)
                                    dimension = metadata_range.get("dimension", "ROWS")
                                    
                                    if dimension == "ROWS":
                                        a1_range = f"{sheet_name}!A{start_index + 1}:Z{end_index}"
                                    else:  # COLUMNS
                                        start_col = col_num_to_letter(start_index)
                                        end_col = col_num_to_letter(end_index - 1)
                                        a1_range = f"{sheet_name}!{start_col}1:{end_col}1000"
                                else:
                                    # Default to entire sheet
                                    a1_range = f"{sheet_name}!A1:Z1000"
                                
                                data = get_dynamic_data(a1_range, spreadsheet_data_field)
                                filtered_data[a1_range] = data

        response["data"] = filtered_data
    
    return response


def batchUpdate(
    spreadsheet_id: str,
    requests: List[Dict[str, Any]],
    include_spreadsheet_in_response: bool = False,
    response_ranges: Optional[List[str]] = None, 
    response_include_grid_data: bool = False,
) -> Dict[str, Any]:
    """Applies one or more updates to the spreadsheet.

    Description: This function applies one or more updates to the spreadsheet.
    It supports the following request types:
    - addSheetRequest - Adds a new sheet to the spreadsheet.
    - deleteSheetRequest - Deletes an existing sheet from the spreadsheet.
    - updateSheetPropertiesRequest - Updates the properties of an existing sheet.
    - updateCells - Updates the cells in a specified range of the spreadsheet.
    - updateSheetProperties - Updates the properties of an existing sheet.
    The function validates the requests and updates the spreadsheet accordingly.

    Args:
        spreadsheet_id (str): The ID of the spreadsheet to update.
        requests (List[Dict[str, Any]]): List of update requests. Each dictionary
            in the list must contain exactly one key, which specifies the type of
            request. The value for that key is a dictionary payload for the request.
            Supported request keys and their payload structures:
            - 'addSheetRequest': Payload must conform to AddSheetRequestPayloadModel.
                Requires 'properties' with a 'sheetId'.
            - 'deleteSheetRequest': Payload must conform to DeleteSheetRequestPayloadModel.
                Requires 'sheetId'.
            - 'updateSheetPropertiesRequest': Payload must conform to UpdateSheetPropertiesRequestPayloadModel.
                Requires 'properties' (with 'sheetId') and 'fields'.
            - 'updateCells': Payload must conform to UpdateCellsPayloadModel.
                Requires 'range' and 'rows'.
            - 'updateSheetProperties': Payload must conform to UpdateSheetPropertiesSimplePayloadModel.
                Requires 'properties' (with 'sheetId'); 'fields' is optional.
        include_spreadsheet_in_response (bool): Whether to include the
            updated spreadsheet in the response. Defaults to False.
        response_ranges (Optional[List[str]]): The ranges to include in the
            response if include_spreadsheet_in_response is True. Defaults to None.
        response_include_grid_data (bool): Whether to include grid data
            in the response if include_spreadsheet_in_response is True. Defaults to False.

    Returns:
        Dict[str, Any]: Dictionary containing:
            - 'spreadsheetId' (str): The spreadsheet ID
            - 'responses' (List[Dict[str, Any]]): List of update responses
            - 'updatedSpreadsheet' (Optional[Dict[str, Any]]): Updated spreadsheet
              if include_spreadsheet_in_response is True

    Raises:
        TypeError: If any argument has an invalid type as follows:
            - spreadsheet_id is not a string
            - requests is not a list
            - include_spreadsheet_in_response is not a boolean
            - response_ranges is not a list of strings or None
            - response_include_grid_data is not a boolean
            - Request items in requests are not dictionaries
            - Payloads for request items in requests are not dictionaries
        pydantic.ValidationError: If the payload for any request in 'requests'
            does not conform to its expected Pydantic model structure.
        InvalidRequestError: If an item in 'requests' has
            an incorrect number of top-level keys (must be exactly one).
        UnsupportedRequestTypeError: If a request type in 'requests' is not supported.
        ValueError:
            - If the spreadsheet is not found (propagated from DB access).
            - If a business logic rule is violated during processing (e.g., sheet
              already exists, sheet not found for deletion/update, specific request
              constraints like missing sheetId if not covered by Pydantic).
    """
    # --- Input Validation ---
    if not isinstance(spreadsheet_id, str):
        raise TypeError("spreadsheet_id must be a string")
    if not isinstance(requests, list):
        raise TypeError("requests must be a list")
    if not isinstance(include_spreadsheet_in_response, bool):
        raise TypeError("include_spreadsheet_in_response must be a boolean")
    if response_ranges is not None:
        if not isinstance(response_ranges, list):
            raise TypeError("response_ranges must be a list of strings or None")
        for item in response_ranges:
            if not isinstance(item, str):
                raise TypeError("All items in response_ranges must be strings")
    if not isinstance(response_include_grid_data, bool):
        raise TypeError("response_include_grid_data must be a boolean")

    validated_request_payloads = [] # Keep track of validated payloads for debugging or potential use
                                  # The core logic will still use the original 'requests' list.

    for i, req_dict in enumerate(requests):
        if not isinstance(req_dict, dict):
            raise TypeError(f"Request item at index {i} must be a dictionary")
        if len(req_dict) != 1:
            raise InvalidRequestError(
                f"Request item at index {i} must contain exactly one operation key"
            )

        request_type = list(req_dict.keys())[0]
        payload = req_dict[request_type]

        if not isinstance(payload, dict): # Payload itself should be a dictionary
             raise TypeError(
                f"Payload for request type '{request_type}' at index {i} must be a dictionary"
            )

        try:
            if request_type == "addSheetRequest":
                validated_request_payloads.append(AddSheetRequestPayloadModel(**payload))
            elif request_type == "deleteSheetRequest":
                validated_request_payloads.append(DeleteSheetRequestPayloadModel(**payload))
            elif request_type == "updateSheetPropertiesRequest":
                validated_request_payloads.append(UpdateSheetPropertiesRequestPayloadModel(**payload))
            elif request_type == "updateCells":
                validated_request_payloads.append(UpdateCellsPayloadModel(**payload))
            elif request_type == "updateSheetProperties":
                validated_request_payloads.append(UpdateSheetPropertiesSimplePayloadModel(**payload))
            else:
                raise UnsupportedRequestTypeError(f"Unsupported request type at index {i}: '{request_type}'")
        except ValidationError as e:
            # Re-raise the original Pydantic validation error
            raise

    # --- Original Core Logic (Unchanged) ---
    userId = "me" # Assuming 'me' is a valid user context
    # The global DB is accessed here.
    if spreadsheet_id not in DB["users"][userId]["files"]:
        raise ValueError("Spreadsheet not found")

    spreadsheet = DB["users"][userId]["files"][spreadsheet_id]
    response = {"spreadsheetId": spreadsheet_id}
    responses = []

    for req in requests: # Original logic iterates over the original requests list
        if "addSheetRequest" in req:
            properties = req["addSheetRequest"].get("properties", {})
            sheet_id = properties.get("sheetId")

            # This check might seem redundant if Pydantic model enforces sheetId,
            # but it's part of original logic and specific error message.
            # Pydantic AddSheetPropertiesModel already makes sheetId mandatory in properties.
            if sheet_id is None:
                raise ValueError(
                    "addSheetRequest must include a 'sheetId' in 'properties'"
                )

            existing_ids = [s["properties"]["sheetId"] for s in spreadsheet["sheets"]]
            if sheet_id in existing_ids:
                raise ValueError(f"Sheet with sheetId {sheet_id} already exists")

            new_sheet_properties = {"sheetId": sheet_id}
            # Merge any other properties from the request.
            # Pydantic's AddSheetPropertiesModel allows extra fields.
            new_sheet_properties.update(properties)

            new_sheet = {"properties": new_sheet_properties}
            spreadsheet["sheets"].append(new_sheet)
            # Store the original properties in the response
            responses.append({"addSheetResponse": {"properties": properties}})


        elif "deleteSheetRequest" in req:
            sheet_id = req["deleteSheetRequest"].get("sheetId")
            # Pydantic DeleteSheetRequestPayloadModel makes sheetId mandatory.
            if sheet_id is None:
                raise ValueError("deleteSheetRequest must include a 'sheetId'")

            sheets = spreadsheet["sheets"]
            sheet_exists = any(
                sheet["properties"]["sheetId"] == sheet_id for sheet in sheets
            )
            if not sheet_exists:
                raise ValueError(f"Sheet with sheetId {sheet_id} does not exist")

            updated_sheets = [
                sheet for sheet in sheets if sheet["properties"]["sheetId"] != sheet_id
            ]
            spreadsheet["sheets"] = updated_sheets
            responses.append({"deleteSheetResponse": {"sheetId": sheet_id}})

        elif "updateSheetPropertiesRequest" in req:
            # Pydantic UpdateSheetPropertiesRequestPayloadModel makes 'properties' and 'fields' mandatory.
            properties_update = req["updateSheetPropertiesRequest"].get("properties")
            fields = req["updateSheetPropertiesRequest"].get("fields")

            if not properties_update or not fields: # This check is mostly covered by Pydantic
                raise ValueError(
                    "updateSheetPropertiesRequest must include 'properties' and 'fields'"
                )

            sheet_id = properties_update.get("sheetId")
            # Pydantic UpdateSheetPropertiesInfoModel makes sheetId mandatory in properties_update.
            if sheet_id is None:
                raise ValueError(
                    "updateSheetPropertiesRequest must include a 'sheetId' in 'properties'"
                )

            updated = False
            for sheet in spreadsheet["sheets"]:
                if sheet["properties"]["sheetId"] == sheet_id:
                    for field in fields.split(","):
                        field = field.strip()
                        if field in properties_update: # Check if the field to update is actually in the provided properties
                            sheet["properties"][field] = properties_update[field]
                    updated = True
                    responses.append(
                        {
                            "updateSheetPropertiesResponse": {
                                "properties": sheet["properties"]
                            }
                        }
                    )
                    break
            if not updated:
                raise ValueError(f"Sheet with sheetId {sheet_id} does not exist")

        elif "updateCells" in req:
            # Pydantic UpdateCellsPayloadModel validates 'range' and 'rows'.
            update = req["updateCells"]
            # Pydantic CellRangeModel validates sub-fields of 'range'.
            range_info = update['range']
            range_ = (
                f"{range_info['sheetId']}!"
                f"{range_info['startRowIndex']}:{range_info['endRowIndex']}"
                f"{range_info['startColumnIndex']}:{range_info['endColumnIndex']}"
            )
            spreadsheet["data"][range_] = update["rows"]
            responses.append({"updateCellsResponse": {"updatedRange": range_}}) # Added "Response" suffix for consistency

        elif "updateSheetProperties" in req:
            # Pydantic UpdateSheetPropertiesSimplePayloadModel ensures 'properties' (with 'sheetId') exists.
            # 'fields' is optional in the model.
            update_payload = req["updateSheetProperties"]
            properties_update = update_payload.get("properties", {})
            fields = update_payload.get("fields", "") # Default to empty string if not provided
            sheet_id = properties_update.get("sheetId")

            if not sheet_id: # This check is important if properties_update could be {}
                             # Pydantic model UpdateSheetPropertiesInfoModel makes sheetId mandatory within properties.
                raise ValueError("updateSheetProperties must include a sheetId in its properties")


            updated = False
            for sheet in spreadsheet["sheets"]:
                if sheet["properties"]["sheetId"] == sheet_id:
                    if fields: # Only update if fields string is not empty
                        for field in fields.split(","):
                            field = field.strip()
                            if field in properties_update:
                                sheet["properties"][field] = properties_update[field]
                    # If fields is empty, it's a valid request but doesn't change properties based on 'fields'
                    # However, the response should still reflect the (potentially unchanged) properties.
                    updated = True
                    responses.append(
                        {"updateSheetPropertiesResponse": {"properties": sheet["properties"]}} # Added "Response" suffix
                    )
                    break
            if not updated:
                raise ValueError(f"Sheet with sheetId {sheet_id} does not exist")
        else:
            # This case should ideally not be reached if validation catches unsupported types.
            # However, keeping it as a fallback.
            raise ValueError(f"Unsupported request type (should have been caught by validation): {list(req.keys())[0]}")


    response["responses"] = responses

    if include_spreadsheet_in_response:
        updated_spreadsheet_data = {"sheets": spreadsheet["sheets"]} # Only include what's defined in original code

        # Replicating original logic for updatedSpreadsheet structure
        # The original does not include 'id' directly in 'updatedSpreadsheet',
        # it includes 'spreadsheetId' at the top level of the main response.
        # If 'data' should be included, that would need to be specified.

        if response_ranges: # Original code had `responseRanges` key
            updated_spreadsheet_data["responseRanges"] = response_ranges
        if response_include_grid_data: # Original code had `responseIncludeGridData` key
            updated_spreadsheet_data["responseIncludeGridData"] = True

        response["updatedSpreadsheet"] = updated_spreadsheet_data


    return response

