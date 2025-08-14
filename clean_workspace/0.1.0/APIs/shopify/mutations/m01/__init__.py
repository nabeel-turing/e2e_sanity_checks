from .customers import fetch_customer_address_book, fetch_single_customer_profile, find_clients_by_criteria, modify_existing_customer_address, register_new_address_for_customer, retrieve_customer_collection, retrieve_specific_customer_address
from .draft_orders import amend_pending_order_details, fetch_single_draft_order, generate_new_draft_purchase, get_all_pending_orders
from .exchanges import process_item_exchange_for_order
from .orders import change_delivery_address_for_open_order, fetch_orders_for_customer, finalize_completed_order, get_total_order_count, reactivate_closed_order, retrieve_filtered_order_list, retrieve_single_order_by_id, submit_new_purchase_order, update_open_order_payment_info, update_unfulfilled_order_contents, void_purchase_and_process_refund
from .products import fetch_product_details_by_id, find_products_by_advanced_filters, get_product_catalog_items
from .returns import initiate_product_return_process
from .transactions import add_payment_transaction_to_order

_function_map = {
    'add_payment_transaction_to_order': 'shopify.mutations.m01.transactions.add_payment_transaction_to_order',
    'amend_pending_order_details': 'shopify.mutations.m01.draft_orders.amend_pending_order_details',
    'change_delivery_address_for_open_order': 'shopify.mutations.m01.orders.change_delivery_address_for_open_order',
    'fetch_customer_address_book': 'shopify.mutations.m01.customers.fetch_customer_address_book',
    'fetch_orders_for_customer': 'shopify.mutations.m01.orders.fetch_orders_for_customer',
    'fetch_product_details_by_id': 'shopify.mutations.m01.products.fetch_product_details_by_id',
    'fetch_single_customer_profile': 'shopify.mutations.m01.customers.fetch_single_customer_profile',
    'fetch_single_draft_order': 'shopify.mutations.m01.draft_orders.fetch_single_draft_order',
    'finalize_completed_order': 'shopify.mutations.m01.orders.finalize_completed_order',
    'find_clients_by_criteria': 'shopify.mutations.m01.customers.find_clients_by_criteria',
    'find_products_by_advanced_filters': 'shopify.mutations.m01.products.find_products_by_advanced_filters',
    'generate_new_draft_purchase': 'shopify.mutations.m01.draft_orders.generate_new_draft_purchase',
    'get_all_pending_orders': 'shopify.mutations.m01.draft_orders.get_all_pending_orders',
    'get_product_catalog_items': 'shopify.mutations.m01.products.get_product_catalog_items',
    'get_total_order_count': 'shopify.mutations.m01.orders.get_total_order_count',
    'initiate_product_return_process': 'shopify.mutations.m01.returns.initiate_product_return_process',
    'modify_existing_customer_address': 'shopify.mutations.m01.customers.modify_existing_customer_address',
    'process_item_exchange_for_order': 'shopify.mutations.m01.exchanges.process_item_exchange_for_order',
    'reactivate_closed_order': 'shopify.mutations.m01.orders.reactivate_closed_order',
    'register_new_address_for_customer': 'shopify.mutations.m01.customers.register_new_address_for_customer',
    'retrieve_customer_collection': 'shopify.mutations.m01.customers.retrieve_customer_collection',
    'retrieve_filtered_order_list': 'shopify.mutations.m01.orders.retrieve_filtered_order_list',
    'retrieve_single_order_by_id': 'shopify.mutations.m01.orders.retrieve_single_order_by_id',
    'retrieve_specific_customer_address': 'shopify.mutations.m01.customers.retrieve_specific_customer_address',
    'submit_new_purchase_order': 'shopify.mutations.m01.orders.submit_new_purchase_order',
    'update_open_order_payment_info': 'shopify.mutations.m01.orders.update_open_order_payment_info',
    'update_unfulfilled_order_contents': 'shopify.mutations.m01.orders.update_unfulfilled_order_contents',
    'void_purchase_and_process_refund': 'shopify.mutations.m01.orders.void_purchase_and_process_refund',
}
