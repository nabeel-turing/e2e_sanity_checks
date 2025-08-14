from .bigqueryAPI import fetch_table_schema, get_all_table_metadata, run_sql_statement

_function_map = {
    'fetch_table_schema': 'bigquery.mutations.m01.bigqueryAPI.fetch_table_schema',
    'get_all_table_metadata': 'bigquery.mutations.m01.bigqueryAPI.get_all_table_metadata',
    'run_sql_statement': 'bigquery.mutations.m01.bigqueryAPI.run_sql_statement',
}
