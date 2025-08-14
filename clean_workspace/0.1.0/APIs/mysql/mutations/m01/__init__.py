from .mysql_handler import enumerate_database_resources, execute_sql_statement, fetch_table_column_schema

_function_map = {
    'enumerate_database_resources': 'mysql.mutations.m01.mysql_handler.enumerate_database_resources',
    'execute_sql_statement': 'mysql.mutations.m01.mysql_handler.execute_sql_statement',
    'fetch_table_column_schema': 'mysql.mutations.m01.mysql_handler.fetch_table_column_schema',
}
