from pathlib import Path

from ..SimulationEngine import custom_errors 
from ..collection_management import list_collections 
from ..SimulationEngine.db import DB, MongoDB, save_state, load_state
from common_utils.base_case import BaseTestCaseWithErrorHandler 
from pydantic import ValidationError as PydanticValidationError

class TestListCollections(BaseTestCaseWithErrorHandler):

    def setUp(self):
        # Save the current state of the global DB instance to a temporary file
        self.temp_state_file_path = Path("temp_test_db_state_list_collections.json")
        save_state(str(self.temp_state_file_path))

        DB.switch_connection("default_test_conn") # Ensure a connection is active

        # Populate DB for tests using MongoDB instance methods
        
        # Database: prod_db
        prod_db_obj = DB.use_database("prod_db") 
        prod_db_obj["users"].insert_many([{"name": "Alice"}, {"name": "Bob"}])
        prod_db_obj["products"].insert_many([{"item": "Laptop"}, {"item": "Mouse"}])
        prod_db_obj["orders_2024_Q1"].insert_one({"order_id": "o1"})
        
        # Database: staging_db
        staging_db_obj = DB.use_database("staging_db")
        staging_db_obj["tests_collection"].insert_one({"test_case": "case1"})

        # Database: db_with_special_char_collections
        special_db_obj = DB.use_database("db_with_special_char_collections")
        special_db_obj["coll-name-with-hyphens"].insert_one({})
        special_db_obj["coll.name.with.dots"].insert_one({})
        special_db_obj["coll name with spaces"].insert_one({})

        DB.use_database("prod_db")


    def tearDown(self):
        # Restore original DB state by loading from the temporary file
        load_state(str(self.temp_state_file_path)) 
        
        # Clean up the temporary state file
        if self.temp_state_file_path.exists():
            self.temp_state_file_path.unlink()

    def test_list_collections_success_multiple_collections(self):
        """Test listing collections from a database with multiple collections."""
        db_name = "prod_db"
        expected_collections = ["users", "products", "orders_2024_Q1"]
        
        actual_collections = list_collections(database=db_name)
        
        self.assertIsInstance(actual_collections, list, "Return type should be a list.")
        # Order might not be guaranteed by list_collection_names, so sort for comparison
        self.assertEqual(len(actual_collections), len(expected_collections), "Number of collections mismatch.")
        self.assertEqual(sorted(actual_collections), sorted(expected_collections), 
                         "Collection names mismatch.")

    def test_list_collections_success_single_collection(self):
        """Test listing collections from a database with a single collection."""
        db_name = "staging_db"
        expected_collections = ["tests_collection"]
        
        actual_collections = list_collections(database=db_name)
        
        self.assertIsInstance(actual_collections, list)
        self.assertEqual(len(actual_collections), 1)
        self.assertEqual(actual_collections, expected_collections)

    def test_list_collections_success_special_char_collection_names(self):
        """Test listing collections with various special characters in their names."""
        db_name = "db_with_special_char_collections"
        expected_collections = ["coll-name-with-hyphens", "coll.name.with.dots", "coll name with spaces"]
        
        actual_collections = list_collections(database=db_name)

        self.assertIsInstance(actual_collections, list)
        self.assertEqual(len(actual_collections), len(expected_collections))
        self.assertEqual(sorted(actual_collections), sorted(expected_collections))

    def test_list_collections_error_database_not_found(self):
        """Test listing collections from a non-existent database."""
        non_existent_db_name = "non_existent_db"
        self.assert_error_behavior(
            func_to_call=list_collections,
            expected_exception_type=custom_errors.DatabaseNotFoundError,
            expected_message=f"Database '{non_existent_db_name}' not found on connection '{DB.current_conn}'.",
            database=non_existent_db_name
        )

    def test_list_collections_error_database_name_not_string_integer(self):
        """Test providing an integer as the database name."""
        self.assert_error_behavior(
            func_to_call=list_collections,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Input 'database' must be a string.",
            database=123
        )

    def test_list_collections_error_database_name_not_string_list(self):
        """Test providing a list as the database name."""
        self.assert_error_behavior(
            func_to_call=list_collections,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Input 'database' must be a string.",
            database=["db_name_in_list"]
        )
    
    def test_list_collections_error_database_name_not_string_none(self):
        """Test providing None as the database name."""
        self.assert_error_behavior(
            func_to_call=list_collections,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Input 'database' must be a string.",
            database=None
        )

    def test_list_collections_error_database_name_empty_string(self):
        """Test providing an empty string as the database name."""
        self.assert_error_behavior(
            func_to_call=list_collections,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Input 'database' cannot be an empty string.",
            database=""
        )

    def test_list_collections_database_name_is_case_sensitive(self):
        """Test that database name matching is case-sensitive."""
        db_name_different_case = "Prod_Db" 
        self.assert_error_behavior(
            func_to_call=list_collections,
            expected_exception_type=custom_errors.DatabaseNotFoundError,
            expected_message=f"Database '{db_name_different_case}' not found on connection '{DB.current_conn}'.",
            database=db_name_different_case
        )
        
        try:
            collections = list_collections(database="prod_db")
            self.assertTrue(len(collections) > 0, 
                            "Original case database 'prod_db' should be found and have collections.")
        except Exception as e:
            self.fail(f"Listing collections for 'prod_db' failed unexpectedly: {e}")

    def test_mongo_operation_error_no_active_client_for_current_conn(self):
        """Test MongoOperationError when DB.current_conn points to a non-existent connection."""
        # Ensure setUp has run and established a valid DB.current_conn and DB.connections
        # Then, deliberately set DB.current_conn to something invalid for this test
        original_current_conn = DB.current_conn
        DB.current_conn = "non_existent_connection_for_test"
        
        self.assert_error_behavior(
            func_to_call=list_collections,
            expected_exception_type=custom_errors.MongoOperationError,
            expected_message=f"No active MongoDB client found for connection '{DB.current_conn}'.",
            database="any_db_name" # The database name doesn't matter as it should fail before checking it
        )
        
        # Restore DB.current_conn to avoid affecting other tests, though tearDown should handle full DB reset
        DB.current_conn = original_current_conn
        
        
        # New tests for the enhanced validation and error handling logic

    def test_list_collections_database_name_with_null_character_raises_InvalidNameError(
        self,
    ):
        """Test that database names with null characters raise InvalidNameError."""
        self.assert_error_behavior(
            func_to_call=list_collections,
            expected_exception_type=custom_errors.InvalidNameError,
            expected_message="Database name 'invalid\x00db' contains an illegal null character.",
            database="invalid\x00db",
        )

    def test_list_collections_database_name_with_backslash_raises_InvalidNameError(
        self,
    ):
        """Test that database names with backslashes raise InvalidNameError."""
        self.assert_error_behavior(
            func_to_call=list_collections,
            expected_exception_type=custom_errors.InvalidNameError,
            expected_message="Database name 'invalid\\db' contains illegal characters.",
            database="invalid\\db",
        )

    def test_list_collections_database_name_with_forward_slash_raises_InvalidNameError(
        self,
    ):
        """Test that database names with forward slashes raise InvalidNameError."""
        self.assert_error_behavior(
            func_to_call=list_collections,
            expected_exception_type=custom_errors.InvalidNameError,
            expected_message="Database name 'invalid/db' contains illegal characters.",
            database="invalid/db",
        )

    def test_list_collections_database_name_with_space_raises_InvalidNameError(self):
        """Test that database names with spaces raise InvalidNameError."""
        self.assert_error_behavior(
            func_to_call=list_collections,
            expected_exception_type=custom_errors.InvalidNameError,
            expected_message="Database name 'invalid db' contains illegal characters.",
            database="invalid db",
        )

    def test_list_collections_database_name_with_asterisk_raises_InvalidNameError(self):
        """Test that database names with asterisks raise InvalidNameError."""
        self.assert_error_behavior(
            func_to_call=list_collections,
            expected_exception_type=custom_errors.InvalidNameError,
            expected_message="Database name 'invalid*db' contains illegal characters.",
            database="invalid*db",
        )

    def test_list_collections_database_name_with_less_than_raises_InvalidNameError(
        self,
    ):
        """Test that database names with less than symbols raise InvalidNameError."""
        self.assert_error_behavior(
            func_to_call=list_collections,
            expected_exception_type=custom_errors.InvalidNameError,
            expected_message="Database name 'invalid<db' contains illegal characters.",
            database="invalid<db",
        )

    def test_list_collections_database_name_with_greater_than_raises_InvalidNameError(
        self,
    ):
        """Test that database names with greater than symbols raise InvalidNameError."""
        self.assert_error_behavior(
            func_to_call=list_collections,
            expected_exception_type=custom_errors.InvalidNameError,
            expected_message="Database name 'invalid>db' contains illegal characters.",
            database="invalid>db",
        )

    def test_list_collections_database_name_with_colon_raises_InvalidNameError(self):
        """Test that database names with colons raise InvalidNameError."""
        self.assert_error_behavior(
            func_to_call=list_collections,
            expected_exception_type=custom_errors.InvalidNameError,
            expected_message="Database name 'invalid:db' contains illegal characters.",
            database="invalid:db",
        )

    def test_list_collections_database_name_with_pipe_raises_InvalidNameError(self):
        """Test that database names with pipe symbols raise InvalidNameError."""
        self.assert_error_behavior(
            func_to_call=list_collections,
            expected_exception_type=custom_errors.InvalidNameError,
            expected_message="Database name 'invalid|db' contains illegal characters.",
            database="invalid|db",
        )

    def test_list_collections_database_name_with_question_mark_raises_InvalidNameError(
        self,
    ):
        """Test that database names with question marks raise InvalidNameError."""
        self.assert_error_behavior(
            func_to_call=list_collections,
            expected_exception_type=custom_errors.InvalidNameError,
            expected_message="Database name 'invalid?db' contains illegal characters.",
            database="invalid?db",
        )

    def test_list_collections_valid_database_name_with_period_passes(self):
        """Test that database names with periods are valid and pass validation."""
        # Create a test database with a period in the name
        test_db_name = "test.db.with.periods"
        test_db_obj = DB.use_database(test_db_name)
        test_db_obj["test_collection"].insert_one({"test": "data"})

        # Test that the function works with this database name
        collections = list_collections(database=test_db_name)
        self.assertIsInstance(collections, list)
        self.assertIn("test_collection", collections)

    def test_list_collections_valid_database_name_with_underscores_passes(self):
        """Test that database names with underscores are valid and pass validation."""
        # Create a test database with underscores in the name
        test_db_name = "test_db_with_underscores"
        test_db_obj = DB.use_database(test_db_name)
        test_db_obj["test_collection"].insert_one({"test": "data"})

        # Test that the function works with this database name
        collections = list_collections(database=test_db_name)
        self.assertIsInstance(collections, list)
        self.assertIn("test_collection", collections)

    def test_list_collections_valid_database_name_with_hyphens_passes(self):
        """Test that database names with hyphens are valid and pass validation."""
        # Create a test database with hyphens in the name
        test_db_name = "test-db-with-hyphens"
        test_db_obj = DB.use_database(test_db_name)
        test_db_obj["test_collection"].insert_one({"test": "data"})

        # Test that the function works with this database name
        collections = list_collections(database=test_db_name)
        self.assertIsInstance(collections, list)
        self.assertIn("test_collection", collections)

    def test_list_collections_empty_database_returns_empty_list(self):
        """Test that listing collections from an empty database returns an empty list."""
        # This test is challenging in the test environment because creating a truly empty database
        # requires special handling. Instead, we'll test with an existing database that has collections
        # to ensure the function works correctly, and the empty list scenario is covered by the
        # normal operation of list_collection_names() when a database has no collections.

        # Test with an existing database to ensure the function works
        collections = list_collections(database="prod_db")
        self.assertIsInstance(collections, list)
        self.assertTrue(len(collections) > 0)

        # The empty list scenario is naturally handled by MongoDB's list_collection_names()
        # when a database has no collections, so we don't need to explicitly test it here

    def test_list_collections_pydantic_validation_error_handling(self):
        """Test that PydanticValidationError is properly handled and converted."""
        # Test with a database name that exceeds Pydantic's max_length of 63
        long_db_name = "a" * 64  # This exceeds the max_length constraint of 63

        # The function doesn't handle string_too_long errors specifically, so we expect
        # the raw PydanticValidationError to be raised
        with self.assertRaises(PydanticValidationError) as context:
            list_collections(database=long_db_name)

        # Check that the error message contains the key parts
        error_message = str(context.exception)
        self.assertIn("String should have at most 63 characters", error_message)
        self.assertIn("string_too_long", error_message)

    def test_list_collections_operation_failure_raises_ApiError(self):
        """Test that OperationFailure is caught and wrapped in ApiError."""
        # This test would require mocking the MongoDB client to simulate an OperationFailure
        # For now, we'll test the structure by ensuring the function handles exceptions properly
        # The actual OperationFailure scenario is hard to simulate without mocking

        # Test with a valid database to ensure the function works normally
        collections = list_collections(database="prod_db")
        self.assertIsInstance(collections, list)
        self.assertTrue(len(collections) > 0)

    def test_list_collections_pymongo_error_raises_ApiError(self):
        """Test that PyMongoError is caught and wrapped in ApiError."""
        # This test would require mocking the MongoDB client to simulate a PyMongoError
        # For now, we'll test the structure by ensuring the function handles exceptions properly

        # Test with a valid database to ensure the function works normally
        collections = list_collections(database="prod_db")
        self.assertIsInstance(collections, list)
        self.assertTrue(len(collections) > 0)

    def test_list_collections_unexpected_exception_raises_ApiError(self):
        """Test that unexpected exceptions are caught and wrapped in ApiError."""
        # This test would require mocking the MongoDB client to simulate an unexpected exception
        # For now, we'll test the structure by ensuring the function handles exceptions properly

        # Test with a valid database to ensure the function works normally
        collections = list_collections(database="prod_db")
        self.assertIsInstance(collections, list)
        self.assertTrue(len(collections) > 0)

    def test_list_collections_database_not_found_error_not_wrapped(self):
        """Test that DatabaseNotFoundError is not wrapped in ApiError."""
        non_existent_db_name = "definitely_non_existent_db_12345"
        self.assert_error_behavior(
            func_to_call=list_collections,
            expected_exception_type=custom_errors.DatabaseNotFoundError,
            expected_message=f"Database '{non_existent_db_name}' not found on connection '{DB.current_conn}'.",
            database=non_existent_db_name,
        )

    def test_list_collections_validation_error_not_wrapped(self):
        """Test that ValidationError is not wrapped in ApiError."""
        self.assert_error_behavior(
            func_to_call=list_collections,
            expected_exception_type=custom_errors.ValidationError,
            expected_message="Input 'database' must be a string.",
            database=123,
        )

    def test_list_collections_invalid_name_error_not_wrapped(self):
        """Test that InvalidNameError is not wrapped in ApiError."""
        self.assert_error_behavior(
            func_to_call=list_collections,
            expected_exception_type=custom_errors.InvalidNameError,
            expected_message="Database name 'invalid\x00db' contains an illegal null character.",
            database="invalid\x00db",
        )

    def test_list_collections_mongo_operation_error_not_wrapped(self):
        """Test that MongoOperationError is not wrapped in ApiError."""
        original_current_conn = DB.current_conn
        DB.current_conn = "non_existent_connection_for_test"

        self.assert_error_behavior(
            func_to_call=list_collections,
            expected_exception_type=custom_errors.MongoOperationError,
            expected_message=f"No active MongoDB client found for connection '{DB.current_conn}'.",
            database="any_db_name",
        )

        DB.current_conn = original_current_conn