import unittest
import copy
from pathlib import Path # For managing temp state file
from typing import Any, Dict, Optional, List

# Assuming relative imports are correct for your project structure
from ..SimulationEngine import custom_errors
from ..collection_management import create_index # Function under test
from ..SimulationEngine.db import DB, MongoDB, save_state, load_state # Import MongoDB class and state functions
from common_utils.base_case import BaseTestCaseWithErrorHandler # For assert_error_behavior
from pydantic import ValidationError # Import Pydantic's ValidationError for specific tests


class TestCreateIndex(BaseTestCaseWithErrorHandler):

    # Define the path to the default state file that might be created
    _DEFAULT_DB_STATE_FILE = Path("db_state.json")

    def setUp(self):
        # Save the current state of the global DB instance to a temporary file
        # This captures the DB state *before* this specific test's setup modifications
        self.temp_state_file_path = Path("temp_test_db_state_create_index.json")
        save_state(str(self.temp_state_file_path))

        # Ensure a specific connection is active for this test suite's setup
        DB.switch_connection("default_test_conn")

        # Populate DB for tests using MongoDB instance methods
        # Database: prod_db
        prod_db_obj = DB.use_database("prod_db")
        prod_db_obj["users"].insert_many([{"name": "Alice"}, {"name": "Bob"}])
        prod_db_obj["products"].insert_many([{"item": "Laptop"}, {"item": "Mouse"}])
        prod_db_obj["orders_2024_Q1"].insert_one({"order_id": "o1"})
        
        # Pre-existing indexes for prod_db.coll1 for testing collision scenarios
        if "coll1" not in prod_db_obj.list_collection_names():
            prod_db_obj.create_collection("coll1")
        
        # Ensure clean state for indexes in coll1 before adding test-specific ones
        # This might involve dropping existing indexes if necessary or ensuring the collection
        # is fresh if tests are sensitive to pre-existing default indexes like _id_
        # For simplicity here, we assume it's okay or that mongomock handles it.
        # If 'idx_A' etc. are added here, they become part of the setup state.
        # The setup in the original question adds them, so we keep that.
        prod_db_obj["coll1"].create_index([("fieldA", 1)], name="idx_A")
        prod_db_obj["coll1"].create_index([("fieldB", -1)], name="idx_B_desc")
        prod_db_obj["coll1"].create_index([("fieldA", 1), ("fieldB", -1)], name="compound_AB")
        
        if "empty_coll" not in prod_db_obj.list_collection_names():
            prod_db_obj.create_collection("empty_coll")
        
        # Database: staging_db
        staging_db_obj = DB.use_database("staging_db")
        staging_db_obj["tests_collection"].insert_one({"test_case": "case1"})

        # Database: db_with_special_char_collections
        special_db_obj = DB.use_database("db_with_special_char_collections")
        special_db_obj["coll-name-with-hyphens"].insert_one({})
        special_db_obj["coll.name.with.dots"].insert_one({})  
        special_db_obj["coll name with spaces"].insert_one({})
        
        DB.use_database("prod_db") # Set current_db back to prod_db for tests

    def tearDown(self):
        load_state(str(self.temp_state_file_path))
        
        if self.temp_state_file_path.exists():
            self.temp_state_file_path.unlink()

    @classmethod
    def tearDownClass(cls):
        if cls._DEFAULT_DB_STATE_FILE.exists():
            try:
                cls._DEFAULT_DB_STATE_FILE.unlink()
            except OSError as e:
                pass

    # Helper methods (_get_collection_object, _assert_index_exists, _get_index_count)
    # remain the same as in your provided code.
    def _get_collection_object(self, db_name, coll_name):
        # Ensure current_conn is valid before trying to access DB.connections[DB.current_conn]
        if DB.current_conn and DB.current_conn in DB.connections:
            conn = DB.connections[DB.current_conn]
            if db_name in conn.list_database_names():
                db_obj = conn[db_name]
                if coll_name in db_obj.list_collection_names():
                    return db_obj[coll_name]
        return None

    def _assert_index_exists(self, db_name, coll_name, index_name, expected_keys_list_of_tuples):
        coll_obj = self._get_collection_object(db_name, coll_name)
        self.assertIsNotNone(coll_obj, f"Collection {db_name}.{coll_name} not found for index assertion.")
        
        index_info = coll_obj.index_information()
        found_index_data = index_info.get(index_name)
        
        self.assertIsNotNone(found_index_data, f"Index '{index_name}' not found in {db_name}.{coll_name}. Existing: {list(index_info.keys())}")
        
        actual_keys = found_index_data.get('key', [])
        # Ensure comparison handles order differences for compound keys if necessary,
        # though PyMongo usually returns them in a consistent order. Sorting both is safest.
        self.assertEqual(sorted(actual_keys), sorted(expected_keys_list_of_tuples),
                         f"Index '{index_name}' has incorrect keys. Expected: {expected_keys_list_of_tuples}, Got: {actual_keys}")

    def _get_index_count(self, db_name, coll_name):
        coll_obj = self._get_collection_object(db_name, coll_name)
        if coll_obj:
            return len(coll_obj.index_information())
        return 0

    # ... Your test methods (test_create_index_success_with_name, etc.) remain here ...
    # Success Cases
    def test_create_index_success_with_name(self):
        db_name, coll_name = "prod_db", "coll1"
        keys_dict = {"new_field_unique": 1}
        keys_list_tuples = [("new_field_unique", 1)]
        index_name = "my_custom_idx_unique"
        
        DB.switch_connection("default_test_conn")
        DB.use_database(db_name)
        initial_index_count = self._get_index_count(db_name, coll_name)

        result = create_index(database=db_name, collection=coll_name, keys=keys_dict, name=index_name)

        self.assertEqual(result["name"], index_name)
        self.assertEqual(result["status_message"], "index created successfully")
        self._assert_index_exists(db_name, coll_name, index_name, keys_list_tuples)
        self.assertEqual(self._get_index_count(db_name, coll_name), initial_index_count + 1)

    def test_create_index_success_without_name_single_key(self):
        db_name, coll_name = "prod_db", "coll1"
        keys_dict = {"another_field_unique": -1}
        keys_list_tuples = [("another_field_unique", -1)]
        expected_auto_name = "another_field_unique_-1" # mongomock/pymongo might generate this
        
        DB.switch_connection("default_test_conn")
        DB.use_database(db_name)
        initial_index_count = self._get_index_count(db_name, coll_name)

        result = create_index(database=db_name, collection=coll_name, keys=keys_dict)

        self.assertIsNotNone(result["name"], "Index name should be auto-generated")
        self.assertEqual(result["status_message"], "index created successfully")
        self._assert_index_exists(db_name, coll_name, result["name"], keys_list_tuples)
        self.assertEqual(self._get_index_count(db_name, coll_name), initial_index_count + 1)


    def test_create_index_success_without_name_compound_key_sorted_auto_name(self):
        db_name, coll_name = "prod_db", "coll1"
        # The order in keys_dict might not be preserved.
        # PyMongo typically generates names based on a canonical representation (e.g., sorted keys).
        keys_dict = {"zeta_field_unique": 1, "alpha_field_unique": -1} 
        keys_list_tuples_for_assertion = sorted(list(keys_dict.items())) # For spec assertion
        # Actual auto-name depends on driver, e.g., "alpha_field_unique_-1_zeta_field_unique_1"
        
        DB.switch_connection("default_test_conn")
        DB.use_database(db_name)
        initial_index_count = self._get_index_count(db_name, coll_name)

        result = create_index(database=db_name, collection=coll_name, keys=keys_dict)

        self.assertIsNotNone(result["name"])
        # Example of how PyMongo might name it (actual might vary based on version/MongoMock)
        # expected_auto_name = "alpha_field_unique_-1_zeta_field_unique_1" 
        # self.assertEqual(result["name"], expected_auto_name)
        self.assertEqual(result["status_message"], "index created successfully")
        self._assert_index_exists(db_name, coll_name, result["name"], keys_list_tuples_for_assertion)
        self.assertEqual(self._get_index_count(db_name, coll_name), initial_index_count + 1)
        
    def test_create_index_on_empty_collection(self):
        db_name, coll_name = "prod_db", "empty_coll"
        keys_dict = {"field_on_empty_coll": 1}
        keys_list_tuples = [("field_on_empty_coll", 1)]
        index_name = "idx_on_empty_coll"

        DB.switch_connection("default_test_conn")
        DB.use_database(db_name)
        # Ensure collection exists (it should from setUp, but good practice)
        if coll_name not in DB.connections[DB.current_conn][db_name].list_collection_names(): # type: ignore
            DB.connections[DB.current_conn][db_name].create_collection(coll_name) # type: ignore

        initial_index_count = self._get_index_count(db_name, coll_name) # Should be 1 (_id_ index)

        result = create_index(database=db_name, collection=coll_name, keys=keys_dict, name=index_name)
        
        self.assertEqual(result["name"], index_name)
        self.assertEqual(result["status_message"], "index created successfully")
        self._assert_index_exists(db_name, coll_name, index_name, keys_list_tuples)
        self.assertEqual(self._get_index_count(db_name, coll_name), initial_index_count + 1)

    # Cases for existing indexes
    def test_create_index_spec_exists_no_name_provided_reports_existing(self):
        db_name, coll_name = "prod_db", "coll1"
        keys_dict = {"fieldA": 1} # This spec matches an index set up as 'idx_A'
        # Function is expected to find an index by spec and return its actual name.
        expected_name_of_existing_index = "idx_A" # Corrected: Expecting the custom name

        DB.switch_connection("default_test_conn")
        DB.use_database(db_name)
        initial_index_count = self._get_index_count(db_name, coll_name)

        result = create_index(database=db_name, collection=coll_name, keys=keys_dict)

        self.assertEqual(result["name"], expected_name_of_existing_index)
        self.assertIn("already exists", result["status_message"])
        self.assertIn(f"(name: '{expected_name_of_existing_index}')", result["status_message"])
        self.assertIn("no action taken", result["status_message"])
        self.assertEqual(self._get_index_count(db_name, coll_name), initial_index_count)

    def test_create_index_spec_exists_same_name_provided_reports_existing(self):
        db_name, coll_name = "prod_db", "coll1"
        keys_dict = {"fieldA": 1} # Matches spec of 'idx_A'
        provided_index_name = "idx_A" # User provides the original custom name
        # Function should find the index by name and spec.
        expected_returned_name = "idx_A" # Corrected: Expecting the custom name

        DB.switch_connection("default_test_conn")
        DB.use_database(db_name)
        initial_index_count = self._get_index_count(db_name, coll_name)

        result = create_index(database=db_name, collection=coll_name, keys=keys_dict, name=provided_index_name)

        self.assertEqual(result["name"], expected_returned_name)
        # This specific path should yield the "name and specification already exists" message
        self.assertIn("index with this name and specification already exists", result["status_message"])
        self.assertIn("no action taken", result["status_message"])
        self.assertEqual(self._get_index_count(db_name, coll_name), initial_index_count)

    def test_create_index_spec_exists_different_name_provided_reports_existing(self):
        db_name, coll_name = "prod_db", "coll1"
        keys_dict = {"fieldA": 1} # Matches spec of 'idx_A'
        new_name_for_existing_spec = "alt_name_for_idx_A" # Different name provided
        # The function finds an index by spec and reports its actual name from index_information().
        expected_actual_name_of_existing_index_with_spec = "idx_A" # Corrected

        DB.switch_connection("default_test_conn")
        DB.use_database(db_name)
        initial_index_count = self._get_index_count(db_name, coll_name)

        result = create_index(database=db_name, collection=coll_name, keys=keys_dict, name=new_name_for_existing_spec)

        self.assertEqual(result["name"], expected_actual_name_of_existing_index_with_spec)
        self.assertIn("specification already exists", result["status_message"].lower())
        self.assertIn(f"(name: '{expected_actual_name_of_existing_index_with_spec}')", result["status_message"])
        self.assertIn("no action taken", result["status_message"])
        self.assertEqual(self._get_index_count(db_name, coll_name), initial_index_count)


    # Error Cases: IndexExistsError (name collision, different spec)
    def test_create_index_raises_IndexExistsError_name_collision_different_spec(self):
        DB.switch_connection("default_test_conn")
        DB.use_database("prod_db")
        # Existing index 'idx_A' has key [("fieldA", 1)]
        # We try to create an index named 'idx_A' but with a different key.
        self.assert_error_behavior(
            func_to_call=create_index,
            expected_exception_type=custom_errors.IndexExistsError,
            # The message from your function for this case:
            expected_message="An index with name 'idx_A' already exists but with a different key specification: [('fieldA', 1)].",
            database="prod_db",
            collection="coll1",
            keys={"some_other_field_for_collision_test": 1}, # Different spec
            name="idx_A" # Same name as existing index
        )

    # Error Cases: InvalidIndexSpecificationError for 'keys'
    def test_create_index_raises_InvalidIndexSpecificationError_keys_empty(self):
        self.assert_error_behavior(
            func_to_call=create_index,
            expected_exception_type=custom_errors.InvalidIndexSpecificationError,
            expected_message="Index 'keys' definition cannot be empty.",
            database="prod_db", collection="coll1", keys={}
        )

    def test_create_index_raises_ValidationError_keys_non_string_key_in_dict(self):
        # This is caught by Pydantic validation on CreateIndexInput.keys
        # where keys of the dict must be str.
        self.assert_error_behavior(
            func_to_call=create_index,
            expected_exception_type=custom_errors.ValidationError, 
            expected_message="Input validation failed", # Pydantic raises this
            database="prod_db", collection="coll1", keys={123: 1}
        )

    def test_create_index_raises_InvalidIndexSpecificationError_keys_invalid_direction_value_zero(self):
        self.assert_error_behavior(
            func_to_call=create_index,
            expected_exception_type=custom_errors.InvalidIndexSpecificationError,
            # Updated expected message based on function's IndexTypeEnum logic
            expected_message="Invalid index type '0' for field 'fieldA'. Supported integer values are: [1, -1] (e.g., 1 for ascending, -1 for descending).",
            database="prod_db", collection="coll1", keys={"fieldA": 0}
        )
    
    def test_create_index_raises_InvalidIndexSpecificationError_keys_invalid_direction_value_string(self):
        self.assert_error_behavior(
            func_to_call=create_index,
            expected_exception_type=custom_errors.InvalidIndexSpecificationError,
            expected_message="Invalid index type 'ascending' for field 'fieldA'. Supported integer values are: [1, -1] (e.g., 1 for ascending, -1 for descending).",
            database="prod_db", collection="coll1", keys={"fieldA": "ascending"}
        )

    def test_create_index_raises_InvalidIndexSpecificationError_keys_value_not_simple_type(self):
        self.assert_error_behavior(
            func_to_call=create_index,
            expected_exception_type=custom_errors.InvalidIndexSpecificationError,
            # Updated expected message based on function's IndexTypeEnum logic
            expected_message="Invalid index type '[1]' for field 'fieldA'. Supported integer values are: [1, -1] (e.g., 1 for ascending, -1 for descending).",
            database="prod_db", collection="coll1", keys={"fieldA": [1]}
        )
    
    def test_create_index_raises_InvalidIndexSpecificationError_empty_field_name_in_keys(self):
        self.assert_error_behavior(
            func_to_call=create_index,
            expected_exception_type=custom_errors.InvalidIndexSpecificationError,
            expected_message="Index field names must be non-empty strings.",
            database="prod_db", collection="coll1", keys={" ": 1} # Field name is whitespace
        )


    # Error Cases: ValidationError (Pydantic CreateIndexInput validation)
    def test_create_index_raises_ValidationError_database_name_empty(self):
        self.assert_error_behavior(
            func_to_call=create_index,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Input validation failed", # Generic message from Pydantic wrapper
            database="", collection="coll1", keys={"field": 1}
        )

    def test_create_index_raises_ValidationError_database_name_too_long(self):
        long_db_name = "a" * 64 # Assuming max length is 63 for DB names
        self.assert_error_behavior(
            func_to_call=create_index,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Input validation failed",
            database=long_db_name, collection="coll1", keys={"field": 1}
        )

    def test_create_index_raises_ValidationError_collection_name_empty(self):
        self.assert_error_behavior(
            func_to_call=create_index,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Input validation failed",
            database="prod_db", collection="", keys={"field": 1}
        )

    def test_create_index_raises_ValidationError_collection_name_too_long(self):
        # Assuming max length 255 for collection names based on Pydantic model
        long_coll_name = "a" * 256 
        self.assert_error_behavior(
            func_to_call=create_index,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Input validation failed",
            database="prod_db", collection=long_coll_name, keys={"field": 1}
        )

    def test_create_index_raises_ValidationError_keys_not_dict(self):
        self.assert_error_behavior(
            func_to_call=create_index,
            expected_exception_type=custom_errors.ValidationError, # Pydantic catches this
            expected_message="Input validation failed",
            database="prod_db", collection="coll1", keys="not_a_dictionary" # type: ignore
        )

    def test_create_index_raises_ValidationError_index_name_empty_string(self):
        self.assert_error_behavior(
            func_to_call=create_index,
            expected_exception_type=custom_errors.ValidationError, # Pydantic catches this
            expected_message="Input validation failed",
            database="prod_db", collection="coll1", keys={"field": 1}, name=""
        )

    def test_create_index_raises_ValidationError_index_name_too_long(self):
        # Assuming max length 128 for index names based on Pydantic model
        long_index_name = "a" * 129
        self.assert_error_behavior(
            func_to_call=create_index,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Input validation failed",
            database="prod_db", collection="coll1", keys={"field": 1}, name=long_index_name
        )

    def test_create_index_with_valid_max_length_names(self):
        db_name = "a" * 63
        coll_name = "b" * 120 # Reduced to pass typical MongoDB collection name limits if they are shorter than 255
        index_name = "c" * 127 # Reduced to pass typical MongoDB index name limits if they are shorter than 128

        keys = {"unique_max_len_field_test": 1}
        keys_list_tuples = [("unique_max_len_field_test", 1)]

        DB.switch_connection("default_test_conn")
        db_obj = DB.use_database(db_name) # type: ignore
        
        # Clean up collection if it exists from a previous failed run or different test
        if coll_name in db_obj.list_collection_names():
            db_obj.drop_collection(coll_name)
        db_obj.create_collection(coll_name) # type: ignore
        
        initial_index_count = self._get_index_count(db_name, coll_name)
        result = create_index(database=db_name, collection=coll_name, keys=keys, name=index_name)

        self.assertEqual(result["name"], index_name, f"Expected index name '{index_name}', got '{result['name']}'")
        self.assertEqual(result["status_message"], "index created successfully")
        self._assert_index_exists(db_name, coll_name, index_name, keys_list_tuples)
        self.assertEqual(self._get_index_count(db_name, coll_name), initial_index_count + 1)


    def test_create_index_invalid_name_contains_dollar(self):
        self.assert_error_behavior(
            func_to_call=create_index,
            expected_exception_type=custom_errors.InvalidIndexSpecificationError,
            expected_message="Index name cannot contain '$' character.",
            database="prod_db", collection="coll1", keys={"f":1}, name="my$index"
        )

    def test_create_index_invalid_name_is_id(self):
        self.assert_error_behavior(
            func_to_call=create_index,
            expected_exception_type=custom_errors.InvalidIndexSpecificationError,
            expected_message="The index name '_id_' is reserved and cannot be used for a user-defined index.",
            database="prod_db", collection="coll1", keys={"f":1}, name="_id_"
        )

if __name__ == '__main__':
    unittest.main()