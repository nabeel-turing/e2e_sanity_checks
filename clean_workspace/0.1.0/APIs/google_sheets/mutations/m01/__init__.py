from .Spreadsheets.Sheets import duplicate_worksheet_to_another_workbook
from .Spreadsheets.SpreadsheetValues import add_rows_to_sheet_range, clear_filtered_sheet_values, erase_content_from_multiple_ranges, erase_range_content, fetch_cell_data, fetch_multiple_ranges_data, modify_cell_contents, modify_multiple_sheet_ranges, retrieve_values_using_filters, update_sheet_data_by_filter
from .Spreadsheets.__init__ import apply_bulk_modifications, initialize_spreadsheet_document, query_spreadsheet_data, retrieve_spreadsheet_by_id

_function_map = {
    'add_rows_to_sheet_range': 'google_sheets.mutations.m01.Spreadsheets.SpreadsheetValues.add_rows_to_sheet_range',
    'apply_bulk_modifications': 'google_sheets.mutations.m01.Spreadsheets.__init__.apply_bulk_modifications',
    'clear_filtered_sheet_values': 'google_sheets.mutations.m01.Spreadsheets.SpreadsheetValues.clear_filtered_sheet_values',
    'duplicate_worksheet_to_another_workbook': 'google_sheets.mutations.m01.Spreadsheets.Sheets.duplicate_worksheet_to_another_workbook',
    'erase_content_from_multiple_ranges': 'google_sheets.mutations.m01.Spreadsheets.SpreadsheetValues.erase_content_from_multiple_ranges',
    'erase_range_content': 'google_sheets.mutations.m01.Spreadsheets.SpreadsheetValues.erase_range_content',
    'fetch_cell_data': 'google_sheets.mutations.m01.Spreadsheets.SpreadsheetValues.fetch_cell_data',
    'fetch_multiple_ranges_data': 'google_sheets.mutations.m01.Spreadsheets.SpreadsheetValues.fetch_multiple_ranges_data',
    'initialize_spreadsheet_document': 'google_sheets.mutations.m01.Spreadsheets.__init__.initialize_spreadsheet_document',
    'modify_cell_contents': 'google_sheets.mutations.m01.Spreadsheets.SpreadsheetValues.modify_cell_contents',
    'modify_multiple_sheet_ranges': 'google_sheets.mutations.m01.Spreadsheets.SpreadsheetValues.modify_multiple_sheet_ranges',
    'query_spreadsheet_data': 'google_sheets.mutations.m01.Spreadsheets.__init__.query_spreadsheet_data',
    'retrieve_spreadsheet_by_id': 'google_sheets.mutations.m01.Spreadsheets.__init__.retrieve_spreadsheet_by_id',
    'retrieve_values_using_filters': 'google_sheets.mutations.m01.Spreadsheets.SpreadsheetValues.retrieve_values_using_filters',
    'update_sheet_data_by_filter': 'google_sheets.mutations.m01.Spreadsheets.SpreadsheetValues.update_sheet_data_by_filter',
}
