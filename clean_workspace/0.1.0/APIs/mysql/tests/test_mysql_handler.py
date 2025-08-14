import unittest
import os
import shutil
import sys
import json
from urllib.parse import quote
from unittest.mock import patch, call

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from common_utils.base_case import BaseTestCaseWithErrorHandler
# Import DuckDBManager class for creating a new instance
from mysql.SimulationEngine.duckdb_manager import DuckDBManager
from mysql.SimulationEngine.custom_errors import InternalError

TEST_DIR_ROOT_MH = "test_mysql_handler_isolated_env" # New root for this specific test
MAIN_DB_FILE_MH_FOR_TEST = "handler_main_test.duckdb" # Specific main DB filename for these tests

class TestMySQLHandler(BaseTestCaseWithErrorHandler):
    # Modules that will be imported and used
    mh_module = None
    duckdb_lib = None # For duckdb.Error, duckdb.CatalogException

    # Patches and instances specific to this test class
    _test_dir_root_mh = TEST_DIR_ROOT_MH
    _current_class_test_dir_mh = ""
    _test_db_files_directory_mh = "" # Directory for *.duckdb files for this test
    _test_simulation_state_json_path_mh = "" # Path for the state.json for this test
    
    _original_db_manager_in_sim_db = None # To store the original db_manager from mysql.SimulationEngine.db
    _test_specific_db_manager = None # The new DuckDBManager instance for tests
    _db_manager_patcher = None # The patch object for 'mysql.SimulationEngine.db.db_manager'


    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # 1. Define paths for the isolated test environment
        cls._current_class_test_dir_mh = os.path.join(cls._test_dir_root_mh, cls.__name__)
        if os.path.exists(cls._current_class_test_dir_mh): # pragma: no cover
            shutil.rmtree(cls._current_class_test_dir_mh)
        os.makedirs(cls._current_class_test_dir_mh, exist_ok=True)

        cls._test_db_files_directory_mh = os.path.join(cls._current_class_test_dir_mh, "TestDBs")
        os.makedirs(cls._test_db_files_directory_mh, exist_ok=True)
        
        cls._test_simulation_state_json_path_mh = os.path.join(cls._current_class_test_dir_mh, "handler_simulation_state.json")

        # Ensure state JSON doesn't exist from a previous failed run before creating manager
        if os.path.exists(cls._test_simulation_state_json_path_mh): # pragma: no cover
            try: os.remove(cls._test_simulation_state_json_path_mh)
            except OSError: pass

        # 2. Create a new DuckDBManager instance configured for this isolated environment
        cls._test_specific_db_manager = DuckDBManager(
            main_url=MAIN_DB_FILE_MH_FOR_TEST, # This will be created inside _test_db_files_directory_mh
            database_directory=cls._test_db_files_directory_mh,
            simulation_state_path=cls._test_simulation_state_json_path_mh
        )

        try:
            from mysql.SimulationEngine.db import db_manager as original_global_manager
            cls._original_db_manager_in_sim_db = original_global_manager
        except ImportError: # pragma: no cover
            cls._original_db_manager_in_sim_db = None 

        cls._db_manager_patcher = patch('mysql.SimulationEngine.db.db_manager', cls._test_specific_db_manager)
        cls._db_manager_patcher.start()
        
        # Patch mysql_handler.db_manager as well, in case it was imported before SimulationEngine.db was patched
        # or if it uses `from .SimulationEngine.db import db_manager` directly.
        # This makes the patch more robust.
        cls._mh_db_manager_patcher = patch('mysql.mysql_handler.db_manager', cls._test_specific_db_manager)
        cls._mh_db_manager_patcher.start()


        import mysql.mysql_handler as handler_module
        import duckdb as ddb_lib 

        cls.mh_module = handler_module
        cls.duckdb_lib = ddb_lib


    @classmethod
    def tearDownClass(cls):
        if cls._mh_db_manager_patcher:
            cls._mh_db_manager_patcher.stop()
            cls._mh_db_manager_patcher = None

        if cls._db_manager_patcher:
            cls._db_manager_patcher.stop()
            cls._db_manager_patcher = None 

        if cls._test_specific_db_manager and cls._test_specific_db_manager._main_connection:
            try:
                cls._test_specific_db_manager.close_main_connection()
            except Exception: pass 
        cls._test_specific_db_manager = None 

        if os.path.exists(cls._current_class_test_dir_mh): 
            shutil.rmtree(cls._current_class_test_dir_mh)
        
        try: 
            if os.path.exists(cls._test_dir_root_mh) and not os.listdir(cls._test_dir_root_mh):
                os.rmdir(cls._test_dir_root_mh)
        except OSError: pass 
        
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        db_manager = self.__class__._test_specific_db_manager 

        if not (db_manager and db_manager._main_connection): # pragma: no cover
            self.fail("Test-specific DB Manager not available or connection closed at start of setUp.")

        try:
            if db_manager._current_db_alias != db_manager._main_db_alias:
                db_manager.execute_query(f"USE `{db_manager._main_db_alias}`")
        except Exception as e: # pragma: no cover
            print(f"Warning (setUp): Initial USE main failed: {e}")

        current_attachments = db_manager._attached_aliases.copy()
        for alias in current_attachments:
            try: db_manager.execute_query(f"DETACH DATABASE `{alias}`")
            except Exception as e: # pragma: no cover
                print(f"Warning (setUp): Detach DB '{alias}' failed: {e}.")
        
        db_manager._attached_aliases.clear()
        
        main_db_file_for_this_manager = os.path.join(
            db_manager._database_directory, 
            os.path.basename(db_manager._main_db_url) if db_manager._main_db_url != ":memory:" else ""
        )

        for fname in os.listdir(db_manager._database_directory): 
            file_to_check = os.path.join(db_manager._database_directory, fname)
            if file_to_check.endswith(".duckdb"):
                if db_manager._main_db_url != ":memory:" and file_to_check == main_db_file_for_this_manager:
                    continue
                # Also preserve the main DB file if it's the one defined in MAIN_DB_FILE_MH_FOR_TEST
                # This is more robust if main_url doesn't match its basename due to relative paths.
                expected_main_db_path = os.path.join(db_manager._database_directory, MAIN_DB_FILE_MH_FOR_TEST)
                if file_to_check == expected_main_db_path:
                    continue

                try: os.remove(file_to_check)
                except OSError as e: # pragma: no cover
                    print(f"Warning (setUp): Failed to remove stale DB file {file_to_check}: {e}")
        
        db_manager._current_db_alias = db_manager._main_db_alias
        db_manager._save_state() 

        try:
            conn = db_manager._main_connection
            actual_main_duckdb_name = db_manager._primary_internal_name
            if db_manager._is_main_memory : # pragma: no cover
                actual_main_duckdb_name = "memory"
            
            # Ensure we are in the main database context for table dropping
            current_ctx_query = "SELECT current_database();"
            # Sometimes current_database() might not be the alias, but the internal name.
            # So, using USE `{db_manager._main_db_alias}` is more reliable before SHOW TABLES.
            try:
                conn.execute(f"USE \"{actual_main_duckdb_name}\";")
            except Exception: # pragma: no cover
                 # Fallback if actual_main_duckdb_name is not usable in USE for some reason
                conn.execute(f"USE `{db_manager._main_db_alias}`;")


            tables = conn.execute("SHOW TABLES;").fetchall()
            for (table_name,) in tables:
                conn.execute(f'DROP TABLE IF EXISTS "{table_name}";')
        except Exception as e: # pragma: no cover
            print(f"Warning (setUp): Failed to drop tables from main DB: {e}")

    def tearDown(self):
        db_manager = self.__class__._test_specific_db_manager
        if db_manager and db_manager._main_connection:
            try:
                if db_manager._current_db_alias != db_manager._main_db_alias: # pragma: no cover
                    db_manager.execute_query(f"USE `{db_manager._main_db_alias}`")
            except Exception: pass 
        super().tearDown()

    def _execute_direct_manager(self, sql):
        return self.__class__._test_specific_db_manager.execute_query(sql)

    def _drop_db_if_exists(self, db_name_as_created):
        db_manager = self.__class__._test_specific_db_manager
        try:
            # Ensure context is main before detaching, as DETACH might depend on current context
            # or it's just safer.
            if db_manager._current_db_alias != db_manager._main_db_alias:
                db_manager.execute_query(f"USE `{db_manager._main_db_alias}`")
            
            # DuckDBManager's drop_database handles detach and file removal
            if db_name_as_created in db_manager._attached_aliases:
                db_manager.drop_database(db_name_as_created)
            else: # Fallback if not in _attached_aliases but might exist
                 db_manager.execute_query(f"DETACH DATABASE IF EXISTS `{db_name_as_created}`")
                 db_file_path = os.path.join(db_manager._database_directory, f"{db_name_as_created}.duckdb")
                 if os.path.exists(db_file_path): # pragma: no cover
                     try: os.remove(db_file_path)
                     except OSError: pass
        except Exception as e: # pragma: no cover
            print(f"Warning (_drop_db_if_exists): Failed to drop/detach DB '{db_name_as_created}': {e}")


    # --- Test Methods ---
    def test_mysql_query_insert(self):
        self._execute_direct_manager("CREATE TABLE test_insert (id INT);")
        result = self.mh_module.mysql_query("INSERT INTO test_insert VALUES (10);")
        schema_name = self.__class__._test_specific_db_manager._current_db_alias
        expected_text = f"Insert successful on schema '{schema_name}'. Affected rows: 1, Last insert ID: 1"
        self.assertEqual(result["content"][0]["text"], expected_text)

    def test_mysql_query_with_datetime(self):
        # Test handling of datetime values in query results
        self._execute_direct_manager("CREATE TABLE test_datetime (id INT, dt TIMESTAMP);")
        self._execute_direct_manager("INSERT INTO test_datetime VALUES (1, '2025-06-17 16:11:32');")
        
        # Query the table with datetime column
        result = self.mh_module.mysql_query("SELECT * FROM test_datetime;")
        
        # Verify the result can be parsed as JSON (no serialization errors)
        json_result = json.loads(result["content"][0]["text"])
        
        # Check that the datetime was properly serialized to ISO format string
        self.assertEqual(len(json_result), 1)
        self.assertEqual(len(json_result[0]), 2)  # Two columns
        self.assertEqual(json_result[0][0], 1)    # id column
        
        # The datetime should be serialized as a string in ISO format
        dt_str = json_result[0][1]
        self.assertIsInstance(dt_str, str)
        self.assertTrue(dt_str.startswith("2025-06-17T16:11:32"))

    def test_mysql_query_delete(self): # New test for delete message
        self._execute_direct_manager("CREATE TABLE test_delete (id INT);")
        self._execute_direct_manager("INSERT INTO test_delete VALUES (10);")
        result = self.mh_module.mysql_query("DELETE FROM test_delete WHERE id = 10;")
        schema_name = self.__class__._test_specific_db_manager._current_db_alias
        expected_text = f"Delete successful on schema '{schema_name}'. Affected rows: 1"
        self.assertEqual(result["content"][0]["text"], expected_text)

    def test_mysql_query_drop_table(self): # New test for DDL (DROP)
        self._execute_direct_manager("CREATE TABLE test_to_drop (id INT);")
        result = self.mh_module.mysql_query("DROP TABLE test_to_drop;")
        schema_name = self.__class__._test_specific_db_manager._current_db_alias
        expected_text = f"DDL operation successful on schema '{schema_name}'."
        self.assertEqual(result["content"][0]["text"], expected_text)

    def test_mysql_query_ddl_truncate(self):
        self._execute_direct_manager("CREATE TABLE test_truncate_ddl (id INT);")
        self._execute_direct_manager("INSERT INTO test_truncate_ddl VALUES(1);")
        result = self.mh_module.mysql_query("TRUNCATE TABLE test_truncate_ddl;")
        schema_name = self.__class__._test_specific_db_manager._current_db_alias
        expected_text = f"DDL operation successful on schema '{schema_name}'."
        self.assertEqual(result["content"][0]["text"], expected_text)
        count_res = self.mh_module.mysql_query("SELECT COUNT(*) FROM test_truncate_ddl;")
        data = json.loads(count_res['content'][0]['text'])
        self.assertEqual(data[0][0], 0)
    
    def test_mysql_query_invalid_sql_input(self): # New test for line 79
        with self.assertRaisesRegex(ValueError, "`sql` must be a non-empty string"):
            self.mh_module.mysql_query("")
        with self.assertRaisesRegex(ValueError, "`sql` must be a non-empty string"):
            self.mh_module.mysql_query("   ")
        with self.assertRaisesRegex(ValueError, "`sql` must be a non-empty string"):
            self.mh_module.mysql_query(None)
        with self.assertRaisesRegex(ValueError, "`sql` must be a non-empty string"):
            self.mh_module.mysql_query(123)

    def test_mysql_query_show_statement(self): # New test for line 116
        self._execute_direct_manager("CREATE TABLE test_for_show (id INT);")
        result = self.mh_module.mysql_query("SHOW TABLES;")
        # The result from db_manager for SHOW is like {'columns': [...], 'data': [[...]]}
        # This should be json.dumps(result, indent=2)
        expected_db_manager_result = self.__class__._test_specific_db_manager.execute_query("SHOW TABLES;")
        self.assertEqual(result["content"][0]["text"], json.dumps(expected_db_manager_result, indent=2))


    # Test for _tables_for_db internal helper context restoration (lines 73-74)
    def test_tables_for_db_restores_context(self):
        db_manager = self.__class__._test_specific_db_manager
        main_alias = db_manager._main_db_alias
        other_db_for_ctx_test = "ctx_restore_db"
        
        self._execute_direct_manager(f"CREATE DATABASE `{other_db_for_ctx_test}`")
        self._execute_direct_manager(f"USE `{other_db_for_ctx_test}`")
        self._execute_direct_manager("CREATE TABLE t_other_ctx (id INT)")
        # Explicitly switch back to main_alias before calling _tables_for_db
        self._execute_direct_manager(f"USE `{main_alias}`")
        
        original_current_alias = db_manager._current_db_alias
        self.assertEqual(original_current_alias, main_alias)

        # Call _tables_for_db for other_db_for_ctx_test.
        # Inside _tables_for_db:
        # cur = main_alias
        # db_manager.execute_query(f"USE {other_db_for_ctx_test}") -> _current_db_alias becomes other_db_for_ctx_test
        # finally: if main_alias != other_db_for_ctx_test (true) -> db_manager.execute_query(f"USE {main_alias}")
        tables = self.mh_module._tables_for_db(other_db_for_ctx_test)
        self.assertEqual(tables, ["t_other_ctx"])
        
        # Check that context was restored by _tables_for_db's finally block
        self.assertEqual(db_manager._current_db_alias, main_alias)
        
        self._drop_db_if_exists(other_db_for_ctx_test)

    def test_get_resources_list_with_data(self):
        db_manager = self.__class__._test_specific_db_manager
        main_db_alias = db_manager._main_db_alias
        other_db_name = "otherDbForGetListTest" 
        
        try:
            self._execute_direct_manager(f"USE `{main_db_alias}`")
            self._execute_direct_manager(f"CREATE TABLE {main_db_alias}.tableOneList (id INT);")
            self._execute_direct_manager(f"CREATE TABLE {main_db_alias}.tableTwoList (name VARCHAR);")

            self._execute_direct_manager(f"CREATE DATABASE `{other_db_name}`")
            self._execute_direct_manager(f"USE `{other_db_name}`")
            self._execute_direct_manager(f"CREATE TABLE {other_db_name}.tableOtherInNewDb (data FLOAT);")
            
            self._execute_direct_manager(f"USE `{main_db_alias}`") # Restore context before call
            original_current_context = db_manager._current_db_alias

            result = self.mh_module.get_resources_list()
            # Check context restoration by get_resources_list (via _tables_for_db)
            self.assertEqual(db_manager._current_db_alias, original_current_context)

            resources = result["resources"]
            expected_resources = [
                {"uri": f"{quote(main_db_alias)}/{quote('tableOneList')}/schema", "mimeType": "application/json", "name": f'"{main_db_alias}.tableOneList" database schema'},
                {"uri": f"{quote(main_db_alias)}/{quote('tableTwoList')}/schema", "mimeType": "application/json", "name": f'"{main_db_alias}.tableTwoList" database schema'},
                {"uri": f"{quote(other_db_name)}/{quote('tableOtherInNewDb')}/schema", "mimeType": "application/json", "name": f'"{other_db_name}.tableOtherInNewDb" database schema'},
            ]
            
            # Sort for comparison as order might vary
            resources.sort(key=lambda x: x['uri'])
            expected_resources.sort(key=lambda x: x['uri'])
            self.assertEqual(resources, expected_resources)
        finally:
            self._drop_db_if_exists(other_db_name)

    # New test for lines 127-132 (mocking db query results)
    def test_get_resources_list_mocked_db_query_results(self):
        # Case 1: execute_query returns {"data": None}
        with patch.object(self.__class__._test_specific_db_manager, 'get_db_names') as mock_execute:
            result = self.mh_module.get_resources_list()
            self.assertEqual(result, {"resources": []})
            mock_execute.assert_called_once_with()
            
    # New test for lines 127-132 (main DB exists but has no tables)
    def test_get_resources_list_main_db_no_tables_no_other_dbs(self):
        # Setup ensures main DB is empty and no other DBs are attached.
        # So, _tables_for_db(main_alias) will return [].
        # db_rows will contain main_alias, but the inner loop for tables won't add anything.
        result = self.mh_module.get_resources_list()
        self.assertEqual(result, {"resources": []})

    def test_get_resources_list_db_with_no_tables(self):
        db_manager = self.__class__._test_specific_db_manager
        db_no_tables = "dbEmptyNoTablesTest" 
        main_table_name = "mainT1ForNoTablesList"
        try:
            self._execute_direct_manager(f"CREATE DATABASE `{db_no_tables}`")
            
            self._execute_direct_manager(f"USE `{db_manager._main_db_alias}`")
            self._execute_direct_manager(f"CREATE TABLE {main_table_name} (id int)")

            result = self.mh_module.get_resources_list()
            
            found_main_t1 = any(f"{db_manager._main_db_alias}/{main_table_name}/schema" in r['uri'] 
                                for r in result['resources'])
            self.assertTrue(found_main_t1, f"Expected table {main_table_name} from main DB not found. Resources: {result['resources']}")
            
            found_db_no_tables_resource = any(f"{db_no_tables}/" in r['uri'] for r in result['resources'])
            self.assertFalse(found_db_no_tables_resource, f"DB {db_no_tables} (no tables) should not appear. Resources: {result['resources']}")
        finally:
            # Cleanup: drop table from main, then drop the other DB
            self._execute_direct_manager(f"USE `{db_manager._main_db_alias}`")
            self._execute_direct_manager(f"DROP TABLE IF EXISTS {main_table_name}")
            self._drop_db_if_exists(db_no_tables)

    def test_get_resource_non_existent_db(self):
        with self.assertRaises(InternalError):
             self.mh_module.get_resource("ghost_db_for_resource_test/table/schema")

    def test_get_resource_non_existent_table(self):
        db_manager = self.__class__._test_specific_db_manager
        main_db_alias = db_manager._main_db_alias
        with self.assertRaises(InternalError):
             self.mh_module.get_resource(f"{main_db_alias}/ghost_table_for_resource_test/schema")
    
    # New test for line 158 (mocking DESCRIBE results)
    def test_get_resource_mocked_describe_results(self):
        db_manager = self.__class__._test_specific_db_manager
        db_name = db_manager._main_db_alias
        table_name = "table_for_mock_describe"
        
        # Table must exist for DESCRIBE to be attempted on it (not raise CatalogException for table)
        self._execute_direct_manager(f"USE `{db_name}`")
        self._execute_direct_manager(f"CREATE TABLE {table_name} (id INT);")
        
        uri = f"{db_name}/{table_name}/schema"
        
        original_execute_query_method = db_manager.execute_query

        # Case 1: DESCRIBE returns {"data": None}
        mock_describe_result_none = {"columns": ["column_name", "column_type", "null", "key", "default", "extra"], "data": None}
        
        def side_effect_describe_none(*args, **kwargs):
            query_sql = args[0]
            if query_sql.upper().startswith("USE"):
                return original_execute_query_method(*args, **kwargs)
            if query_sql.upper().startswith(f"DESCRIBE `{table_name.upper()}`") or query_sql.upper().startswith(f"DESCRIBE {table_name.upper()}"):
                return mock_describe_result_none
            return original_execute_query_method(*args, **kwargs) # pragma: no cover

        with patch.object(db_manager, 'execute_query', side_effect=side_effect_describe_none) as mock_execute_qs:
            result = self.mh_module.get_resource(uri)
            self.assertEqual(json.loads(result["contents"][0]["text"]), [])
            # Check calls were made
            expected_calls = [
                 call(f"USE {db_name}"), # Note: get_resource does not quote db_name in USE
                 call(f"DESCRIBE {table_name};")
            ]
            # Allow for db_name to be quoted or not in USE by the manager
            # Check that the USE call happened
            self.assertTrue(any(c[0][0].upper() == f"USE {db_name.upper()}" or c[0][0].upper() == f"USE `{db_name.upper()}`" for c in mock_execute_qs.call_args_list))
            # Check that the DESCRIBE call happened
            self.assertTrue(any(c[0][0].upper() == f"DESCRIBE {table_name.upper()};" or c[0][0].upper() == f"DESCRIBE `{table_name.upper()}`;" for c in mock_execute_qs.call_args_list))


        # Case 2: DESCRIBE returns {"data": []}
        mock_describe_result_empty = {"columns": ["column_name", "column_type", "null", "key", "default", "extra"], "data": []}

        def side_effect_describe_empty(*args, **kwargs):
            query_sql = args[0]
            if query_sql.upper().startswith("USE"):
                return original_execute_query_method(*args, **kwargs)
            if query_sql.upper().startswith(f"DESCRIBE `{table_name.upper()}`") or query_sql.upper().startswith(f"DESCRIBE {table_name.upper()}"):
                return mock_describe_result_empty
            return original_execute_query_method(*args, **kwargs) # pragma: no cover
        
        with patch.object(db_manager, 'execute_query', side_effect=side_effect_describe_empty) as mock_execute_qs:
            result = self.mh_module.get_resource(uri)
            self.assertEqual(json.loads(result["contents"][0]["text"]), [])


    def test_current_schema_default_fallback(self):
        db_manager_under_test = self.__class__._test_specific_db_manager 
        original_alias = db_manager_under_test._current_db_alias
        # Create tables with unique names to avoid conflicts if not dropped by schema name issues
        table_none = "test_schema_fallback_none"
        table_empty = "test_schema_fallback_empty"
        self._execute_direct_manager(f"DROP TABLE IF EXISTS {table_none}")
        self._execute_direct_manager(f"DROP TABLE IF EXISTS {table_empty}")
        try:
            with patch.object(db_manager_under_test, '_current_db_alias', None):
                # Need to be in *some* valid DB for CREATE TABLE to succeed if schema is 'default'
                # but operations are on the actual current connection's database.
                # The 'default' schema name is for display. Actual operations use the current DB.
                self._execute_direct_manager(f"CREATE TABLE {table_none} (id INT);")
                res = self.mh_module.mysql_query(f"INSERT INTO {table_none} VALUES (1);")
                self.assertIn("Insert successful on schema 'default'", res['content'][0]['text'])
            
            with patch.object(db_manager_under_test, '_current_db_alias', ""):
                self._execute_direct_manager(f"CREATE TABLE {table_empty} (id INT);")
                res = self.mh_module.mysql_query(f"INSERT INTO {table_empty} VALUES (1);")
                self.assertIn("Insert successful on schema 'default'", res['content'][0]['text'])
        finally: 
             db_manager_under_test._current_db_alias = original_alias
             # Restore context if original_alias was valid
             if original_alias:
                 try: 
                     # Ensure the alias is valid before trying to USE it
                     if original_alias == db_manager_under_test._main_db_alias or \
                        original_alias in db_manager_under_test._attached_aliases or \
                        any(original_alias == attached_info['alias'] for attached_info in db_manager_under_test._attached_aliases.values()): # More robust check for alias
                         db_manager_under_test.execute_query(f"USE `{original_alias}`")
                     else: # pragma: no cover
                         db_manager_under_test.execute_query(f"USE `{db_manager_under_test._main_db_alias}`")
                 except Exception: # pragma: no cover
                     # Fallback to main if restoration fails
                     try: db_manager_under_test.execute_query(f"USE `{db_manager_under_test._main_db_alias}`")
                     except Exception: pass
             else: # pragma: no cover
                  try: db_manager_under_test.execute_query(f"USE `{db_manager_under_test._main_db_alias}`")
                  except Exception: pass
             # Clean up tables created during test
             self._execute_direct_manager(f"DROP TABLE IF EXISTS {table_none}")
             self._execute_direct_manager(f"DROP TABLE IF EXISTS {table_empty}")


    def test_get_resource_valid_returns_full_schema(self):
        db_manager = self.__class__._test_specific_db_manager
        db_name = db_manager._main_db_alias
        table_name = "res_table_full_schema"
        self._execute_direct_manager(f"USE `{db_name}`")
        self._execute_direct_manager(f"""
            CREATE TABLE {table_name} (
                id INT PRIMARY KEY, name VARCHAR(255) NOT NULL DEFAULT 'Unnamed', 
                description TEXT, quantity INTEGER DEFAULT 0,
                price DECIMAL(10,2) NULL, last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP); """)
        uri = f"{db_name}/{table_name}/schema"
        result = self.mh_module.get_resource(uri)
        content = result["contents"][0]
        self.assertEqual(content["uri"], uri); self.assertEqual(content["mimeType"], "application/json")
        schema_data = json.loads(content["text"])
        expected_schema_data = [
            {"column_name": "id", "data_type": "INTEGER", "is_nullable": "NO", "column_default": None},
            {"column_name": "name", "data_type": "VARCHAR", "is_nullable": "NO", "column_default": "'Unnamed'"},
            {"column_name": "description", "data_type": "VARCHAR", "is_nullable": "YES", "column_default": None}, # TEXT is an alias for VARCHAR in DuckDB describe
            {"column_name": "quantity", "data_type": "INTEGER", "is_nullable": "YES", "column_default": "0"},
            {"column_name": "price", "data_type": "DECIMAL(10,2)", "is_nullable": "YES", "column_default": None},
            {"column_name": "last_updated", "data_type": "TIMESTAMP", "is_nullable": "YES", "column_default": "now()"},] # DuckDB DESCRIBE shows 'now()' for CURRENT_TIMESTAMP
        self.assertEqual(len(schema_data), len(expected_schema_data), "Column count mismatch")
        for i, actual_col in enumerate(schema_data):
            expected_col = expected_schema_data[i]
            self.assertEqual(actual_col["column_name"], expected_col["column_name"])
            actual_base_type = actual_col["data_type"].split("(")[0].upper(); expected_base_type = expected_col["data_type"].split("(")[0].upper()
            if expected_base_type == "TEXT": expected_base_type = "VARCHAR" 
            if expected_base_type == "INT": expected_base_type = "INTEGER"
            if actual_base_type == "INT": actual_base_type = "INTEGER" # Normalize INT to INTEGER from DuckDB
            if expected_base_type == "DECIMAL": self.assertEqual(actual_col["data_type"].upper(), expected_col["data_type"].upper())
            elif expected_base_type == "TIMESTAMP": 
                # Accept both TIMESTAMP and TIMESTAMP WITH TIME ZONE
                self.assertTrue(actual_base_type in ["TIMESTAMP", "TIMESTAMP WITH TIME ZONE"])
            else: self.assertEqual(actual_base_type, expected_base_type)
            self.assertEqual(actual_col["is_nullable"], expected_col["is_nullable"])
            if expected_col["column_default"] is None: self.assertIsNone(actual_col["column_default"])
            elif expected_col["column_default"].lower() in ("now()", "current_timestamp"):
                 self.assertTrue(actual_col["column_default"] and ("now()" in actual_col["column_default"].lower() or "current_timestamp" in actual_col["column_default"].lower() or "duckdb_timestamp" in actual_col["column_default"].lower())) # duckdb specific variations
            else: self.assertEqual(str(actual_col["column_default"]), str(expected_col["column_default"]))

    def test_get_resource_empty_table_returns_full_schema(self):
        db_manager = self.__class__._test_specific_db_manager
        db_name = db_manager._main_db_alias
        table_name = "res_empty_table_full_schema"
        self._execute_direct_manager(f"USE `{db_name}`")
        self._execute_direct_manager(f"CREATE TABLE {table_name} (col_a BIGINT NOT NULL, col_b TEXT DEFAULT 'EMPTY');")
        uri = f"{db_name}/{table_name}/schema"
        result = self.mh_module.get_resource(uri)
        content = result["contents"][0]; schema_data = json.loads(content["text"])
        expected_schema_data = [
            {"column_name": "col_a", "data_type": "BIGINT", "is_nullable": "NO", "column_default": None},
            {"column_name": "col_b", "data_type": "VARCHAR", "is_nullable": "YES", "column_default": "'EMPTY'"},] # TEXT becomes VARCHAR
        self.assertEqual(len(schema_data), len(expected_schema_data))
        for i, actual_col in enumerate(schema_data):
            expected_col = expected_schema_data[i]; self.assertEqual(actual_col["column_name"], expected_col["column_name"])
            actual_base_type = actual_col["data_type"].split("(")[0].upper(); expected_base_type = expected_col["data_type"].split("(")[0].upper()
            if expected_base_type == "TEXT": expected_base_type = "VARCHAR"
            self.assertEqual(actual_base_type, expected_base_type)
            self.assertEqual(actual_col["is_nullable"], expected_col["is_nullable"]); self.assertEqual(actual_col["column_default"], expected_col["column_default"])

    def test_get_resource_invalid_uri_format(self):
        with self.assertRaisesRegex(ValueError, "`uri` must be in the form '<db>/<table>/schema'"): self.mh_module.get_resource("db/table")
        with self.assertRaisesRegex(ValueError, "`uri` must end with '/schema'"): self.mh_module.get_resource("db/table/invalid_tail")
        with self.assertRaisesRegex(ValueError, "`uri` must be in the form '<db>/<table>/schema'"): self.mh_module.get_resource(123) # type: ignore


if __name__ == "__main__": # pragma: no cover
    unittest.main(verbosity=2)