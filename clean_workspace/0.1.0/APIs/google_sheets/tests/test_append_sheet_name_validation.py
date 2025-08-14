"""Unit tests for sheet name validation in Google Sheets API Simulation.

This module contains tests for the sheet name validation functionality
added to the Google Sheets API simulation, specifically focusing on the append function.
It ensures that ranges without explicit sheet names are only allowed when the default sheet is 'Sheet1'.
"""

import unittest
import json
from pydantic import ValidationError

from ..SimulationEngine.db import DB
from ..Spreadsheets import SpreadsheetValues
from ..Spreadsheets.SpreadsheetValues import append as append_spreadsheet_values

from common_utils.base_case import BaseTestCaseWithErrorHandler


class TestAppendSheetNameValidation(BaseTestCaseWithErrorHandler):
    """Tests for sheet name validation in append function of Google Sheets API Simulation."""

    def setUp(self):
        """Sets up the test environment with test spreadsheets."""
        # Reset DB before each test
        DB.clear()
        
        # Create a spreadsheet with only Sheet1
        DB["users"] = {
            "me": {
                "files": {
                    "sheet1_only": {
                        "data": {
                            "Sheet1!A1:B2": [["Name", "Age"], ["Alice", 30]]
                        }
                    },
                    "multiple_sheets": {
                        "data": {
                            "Sheet1!A1:B2": [["Name", "Age"], ["Alice", 30]],
                            "Sheet2!A1:B2": [["City", "Country"], ["New York", "USA"]]
                        }
                    }
                }
            }
        }
        
        self.valid_value_input_option = "RAW"
        self.valid_values = [["new_val1", "new_val2"], ["new_val3", "new_val4"]]

    def test_append_with_explicit_sheet_name_multiple_sheets(self):
        """Test appending to a range with an explicit sheet name when multiple sheets exist."""
        # Using an explicit sheet name should work even when multiple sheets exist
        result = append_spreadsheet_values(
            spreadsheet_id="multiple_sheets",
            range="Sheet1!A3:B4",  # Explicit sheet name
            valueInputOption=self.valid_value_input_option,
            values=self.valid_values
        )
        
        # Verify the function output
        self.assertIsInstance(result, dict)
        self.assertEqual(result["id"], "multiple_sheets")
        self.assertEqual(result["updatedRange"], "Sheet1!A3:B4")
        self.assertEqual(result["updatedRows"], 2)
        self.assertEqual(result["updatedColumns"], 2)
        
        # Verify the data was actually appended in the database
        sheet_data = DB["users"]["me"]["files"]["multiple_sheets"]["data"]
        
        # Check if the new range exists in the data
        self.assertIn("Sheet1!A3:B4", sheet_data)
        
        # Verify the appended values
        self.assertEqual(sheet_data["Sheet1!A3:B4"], self.valid_values)
        
        # Verify the original data is unchanged
        self.assertEqual(sheet_data["Sheet1!A1:B2"], [["Name", "Age"], ["Alice", 30]])
        self.assertEqual(sheet_data["Sheet2!A1:B2"], [["City", "Country"], ["New York", "USA"]])

    def test_append_without_sheet_name_single_sheet(self):
        """Test appending to a range without an explicit sheet name when only Sheet1 exists."""
        # When only Sheet1 exists, not specifying a sheet name should default to Sheet1
        result = append_spreadsheet_values(
            spreadsheet_id="sheet1_only",
            range="A3:B4",  # No explicit sheet name
            valueInputOption=self.valid_value_input_option,
            values=self.valid_values
        )
        
        # Verify the function output
        self.assertIsInstance(result, dict)
        self.assertEqual(result["id"], "sheet1_only")
        self.assertEqual(result["updatedRange"], "A3:B4")  # The API doesn't add Sheet1! prefix in the response
        self.assertEqual(result["updatedRows"], 2)
        self.assertEqual(result["updatedColumns"], 2)
        
        # Verify the data was actually appended in the database
        sheet_data = DB["users"]["me"]["files"]["sheet1_only"]["data"]
        
        # Check if the new range exists in the data (with or without Sheet1! prefix)
        if "A3:B4" in sheet_data:
            self.assertEqual(sheet_data["A3:B4"], self.valid_values)
        elif "Sheet1!A3:B4" in sheet_data:
            self.assertEqual(sheet_data["Sheet1!A3:B4"], self.valid_values)
        else:
            self.fail("Neither A3:B4 nor Sheet1!A3:B4 found in the database")
        
        # Verify the original data is unchanged
        self.assertEqual(sheet_data["Sheet1!A1:B2"], [["Name", "Age"], ["Alice", 30]])

    def test_append_without_sheet_name_multiple_sheets(self):
        """Test appending to a range without an explicit sheet name when multiple sheets exist."""
        # When multiple sheets exist, not specifying a sheet name should raise an error
        with self.assertRaises(ValueError) as context:
            append_spreadsheet_values(
                spreadsheet_id="multiple_sheets",
                range="A3:B4",  # No explicit sheet name
                valueInputOption=self.valid_value_input_option,
                values=self.valid_values
            )
        
        self.assertEqual(
            str(context.exception),
            "Range without explicit sheet name is only allowed when the default sheet is 'Sheet1'"
        )
        
        # Verify the database was not modified
        original_data = {
            "Sheet1!A1:B2": [["Name", "Age"], ["Alice", 30]],
            "Sheet2!A1:B2": [["City", "Country"], ["New York", "USA"]]
        }
        self.assertEqual(DB["users"]["me"]["files"]["multiple_sheets"]["data"], original_data)

    def test_append_with_nonexistent_sheet_name(self):
        """Test appending to a range with an explicit sheet name that doesn't exist."""
        # Using a sheet name that doesn't exist should still work (it will create the sheet)
        # This is the expected behavior in Google Sheets API
        result = append_spreadsheet_values(
            spreadsheet_id="multiple_sheets",
            range="NonExistentSheet!A1:B2",  # Sheet doesn't exist yet
            valueInputOption=self.valid_value_input_option,
            values=self.valid_values
        )
        
        # Verify the function output
        self.assertIsInstance(result, dict)
        self.assertEqual(result["id"], "multiple_sheets")
        self.assertEqual(result["updatedRange"], "NonExistentSheet!A1:B2")
        self.assertEqual(result["updatedRows"], 2)
        self.assertEqual(result["updatedColumns"], 2)
        
        # Verify the new sheet was created in the database
        sheet_data = DB["users"]["me"]["files"]["multiple_sheets"]["data"]
        self.assertIn("NonExistentSheet!A1:B2", sheet_data)
        
        # Verify the data was correctly added
        self.assertEqual(sheet_data["NonExistentSheet!A1:B2"], self.valid_values)
        
        # Verify the original sheets are unchanged
        self.assertEqual(sheet_data["Sheet1!A1:B2"], [["Name", "Age"], ["Alice", 30]])
        self.assertEqual(sheet_data["Sheet2!A1:B2"], [["City", "Country"], ["New York", "USA"]])

    def test_append_with_insert_data_option_overwrite(self):
        """Test appending with insertDataOption=OVERWRITE."""
        # Set up initial data
        initial_range = "Sheet3!A1:B2"
        initial_values = [["Initial1", "Initial2"], ["Initial3", "Initial4"]]
        DB["users"]["me"]["files"]["multiple_sheets"]["data"][initial_range] = initial_values
        
        # Append with OVERWRITE option
        result = append_spreadsheet_values(
            spreadsheet_id="multiple_sheets",
            range=initial_range,
            valueInputOption=self.valid_value_input_option,
            values=self.valid_values,
            insertDataOption="OVERWRITE"
        )
        
        # Verify the function output
        self.assertIsInstance(result, dict)
        self.assertEqual(result["id"], "multiple_sheets")
        self.assertEqual(result["updatedRange"], initial_range)
        self.assertEqual(result["updatedRows"], 2)
        self.assertEqual(result["updatedColumns"], 2)
        
        # Verify the data was overwritten in the database
        sheet_data = DB["users"]["me"]["files"]["multiple_sheets"]["data"]
        self.assertEqual(sheet_data[initial_range], self.valid_values)
        
        # Verify the original sheets are unchanged
        self.assertEqual(sheet_data["Sheet1!A1:B2"], [["Name", "Age"], ["Alice", 30]])
        self.assertEqual(sheet_data["Sheet2!A1:B2"], [["City", "Country"], ["New York", "USA"]])

    def test_append_with_include_values_in_response(self):
        """Test appending with includeValuesInResponse=True."""
        result = append_spreadsheet_values(
            spreadsheet_id="sheet1_only",
            range="Sheet1!A3:B4",
            valueInputOption=self.valid_value_input_option,
            values=self.valid_values,
            includeValuesInResponse=True
        )
        
        # Verify the function output includes values
        self.assertIsInstance(result, dict)
        self.assertEqual(result["id"], "sheet1_only")
        self.assertEqual(result["updatedRange"], "Sheet1!A3:B4")
        self.assertEqual(result["updatedRows"], 2)
        self.assertEqual(result["updatedColumns"], 2)
        self.assertIn("values", result)
        self.assertEqual(result["values"], self.valid_values)
        
        # Verify the data was appended in the database
        sheet_data = DB["users"]["me"]["files"]["sheet1_only"]["data"]
        self.assertIn("Sheet1!A3:B4", sheet_data)
        
        # Verify the appended data
        self.assertEqual(sheet_data["Sheet1!A3:B4"], self.valid_values)
        
        # Verify the original data is unchanged
        self.assertEqual(sheet_data["Sheet1!A1:B2"], [["Name", "Age"], ["Alice", 30]])

    def test_append_with_major_dimension_columns(self):
        """Test appending with majorDimension=COLUMNS."""
        # Column values: first column is ["col1_val1", "col1_val2"], second column is ["col2_val1", "col2_val2"]
        col_values = [["col1_val1", "col1_val2"], ["col2_val1", "col2_val2"]]
        
        result = append_spreadsheet_values(
            spreadsheet_id="sheet1_only",
            range="Sheet1!A3:B4",
            valueInputOption=self.valid_value_input_option,
            values=col_values,
            majorDimension="COLUMNS",
            includeValuesInResponse=True
        )
        
        # Verify the function output
        self.assertIsInstance(result, dict)
        self.assertEqual(result["id"], "sheet1_only")
        self.assertEqual(result["updatedRange"], "Sheet1!A3:B4")
        self.assertEqual(result["updatedRows"], 2)  # 2 rows after transpose
        self.assertEqual(result["updatedColumns"], 2)  # 2 columns after transpose
        
        # Values in response should be in the original column format
        self.assertEqual(result["values"], col_values)
        
        # Verify the data was appended in the database (should be transposed)
        sheet_data = DB["users"]["me"]["files"]["sheet1_only"]["data"]
        self.assertIn("Sheet1!A3:B4", sheet_data)
        
        # Verify the transposed data was correctly added
        expected_transposed_data = [
            ["col1_val1", "col2_val1"],  # Transposed row 1
            ["col1_val2", "col2_val2"]   # Transposed row 2
        ]
        self.assertEqual(sheet_data["Sheet1!A3:B4"], expected_transposed_data)
        
        # Verify the original data is unchanged
        self.assertEqual(sheet_data["Sheet1!A1:B2"], [["Name", "Age"], ["Alice", 30]])

if __name__ == "__main__":
    unittest.main() 