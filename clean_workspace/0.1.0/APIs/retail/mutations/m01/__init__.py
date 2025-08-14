from .calculate_tool import evaluate_mathematical_query
from .cancel_pending_order_tool import void_unfulfilled_purchase
from .exchange_delivered_order_items_tool import swap_items_from_completed_shipment
from .find_user_id_by_email_tool import locate_account_id_with_email
from .find_user_id_by_name_zip_tool import retrieve_account_id_by_name_and_zip
from .get_order_details_tool import fetch_purchase_summary
from .get_product_details_tool import retrieve_product_inventory_info
from .get_user_details_tool import fetch_customer_account_information
from .list_all_product_types_tool import enumerate_all_product_categories
from .modify_pending_order_address_tool import update_shipping_destination_for_pending_order
from .modify_pending_order_items_tool import amend_products_in_unprocessed_order
from .modify_pending_order_payment_tool import alter_payment_source_for_pending_order
from .modify_user_address_tool import update_customer_default_shipping_address
from .return_delivered_order_items_tool import initiate_refund_for_received_goods
from .think_tool import record_internal_monologue
from .transfer_to_human_agents_tool import escalate_to_live_support_agent

_function_map = {
    'alter_payment_source_for_pending_order': 'retail.mutations.m01.modify_pending_order_payment_tool.alter_payment_source_for_pending_order',
    'amend_products_in_unprocessed_order': 'retail.mutations.m01.modify_pending_order_items_tool.amend_products_in_unprocessed_order',
    'enumerate_all_product_categories': 'retail.mutations.m01.list_all_product_types_tool.enumerate_all_product_categories',
    'escalate_to_live_support_agent': 'retail.mutations.m01.transfer_to_human_agents_tool.escalate_to_live_support_agent',
    'evaluate_mathematical_query': 'retail.mutations.m01.calculate_tool.evaluate_mathematical_query',
    'fetch_customer_account_information': 'retail.mutations.m01.get_user_details_tool.fetch_customer_account_information',
    'fetch_purchase_summary': 'retail.mutations.m01.get_order_details_tool.fetch_purchase_summary',
    'initiate_refund_for_received_goods': 'retail.mutations.m01.return_delivered_order_items_tool.initiate_refund_for_received_goods',
    'locate_account_id_with_email': 'retail.mutations.m01.find_user_id_by_email_tool.locate_account_id_with_email',
    'record_internal_monologue': 'retail.mutations.m01.think_tool.record_internal_monologue',
    'retrieve_account_id_by_name_and_zip': 'retail.mutations.m01.find_user_id_by_name_zip_tool.retrieve_account_id_by_name_and_zip',
    'retrieve_product_inventory_info': 'retail.mutations.m01.get_product_details_tool.retrieve_product_inventory_info',
    'swap_items_from_completed_shipment': 'retail.mutations.m01.exchange_delivered_order_items_tool.swap_items_from_completed_shipment',
    'update_customer_default_shipping_address': 'retail.mutations.m01.modify_user_address_tool.update_customer_default_shipping_address',
    'update_shipping_destination_for_pending_order': 'retail.mutations.m01.modify_pending_order_address_tool.update_shipping_destination_for_pending_order',
    'void_unfulfilled_purchase': 'retail.mutations.m01.cancel_pending_order_tool.void_unfulfilled_purchase',
}
