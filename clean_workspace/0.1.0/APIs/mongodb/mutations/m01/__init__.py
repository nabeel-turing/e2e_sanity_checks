from .collection_management import analyze_collection_structure, build_collection_index, describe_collection_indices, enumerate_collections_in_database, establish_new_collection, get_collection_disk_usage, relabel_collection, remove_collection_from_db
from .connection_server_management import change_active_mongodb_server
from .data_operations import add_multiple_documents, count_documents_matching_query, erase_documents_by_filter, execute_aggregation_pipeline, modify_matching_documents, query_documents_in_collection
from .database_operations import delete_database_permanently, get_all_database_names

_function_map = {
    'add_multiple_documents': 'mongodb.mutations.m01.data_operations.add_multiple_documents',
    'analyze_collection_structure': 'mongodb.mutations.m01.collection_management.analyze_collection_structure',
    'build_collection_index': 'mongodb.mutations.m01.collection_management.build_collection_index',
    'change_active_mongodb_server': 'mongodb.mutations.m01.connection_server_management.change_active_mongodb_server',
    'count_documents_matching_query': 'mongodb.mutations.m01.data_operations.count_documents_matching_query',
    'delete_database_permanently': 'mongodb.mutations.m01.database_operations.delete_database_permanently',
    'describe_collection_indices': 'mongodb.mutations.m01.collection_management.describe_collection_indices',
    'enumerate_collections_in_database': 'mongodb.mutations.m01.collection_management.enumerate_collections_in_database',
    'erase_documents_by_filter': 'mongodb.mutations.m01.data_operations.erase_documents_by_filter',
    'establish_new_collection': 'mongodb.mutations.m01.collection_management.establish_new_collection',
    'execute_aggregation_pipeline': 'mongodb.mutations.m01.data_operations.execute_aggregation_pipeline',
    'get_all_database_names': 'mongodb.mutations.m01.database_operations.get_all_database_names',
    'get_collection_disk_usage': 'mongodb.mutations.m01.collection_management.get_collection_disk_usage',
    'modify_matching_documents': 'mongodb.mutations.m01.data_operations.modify_matching_documents',
    'query_documents_in_collection': 'mongodb.mutations.m01.data_operations.query_documents_in_collection',
    'relabel_collection': 'mongodb.mutations.m01.collection_management.relabel_collection',
    'remove_collection_from_db': 'mongodb.mutations.m01.collection_management.remove_collection_from_db',
}
