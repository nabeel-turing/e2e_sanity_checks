from .balance import get_account_balance
from .coupon import fetch_available_discounts, generate_new_discount_code
from .customer import register_new_client, retrieve_client_list
from .dispute import get_all_payment_disputes, respond_to_payment_dispute
from .invoice import add_item_to_bill, complete_and_send_bill, issue_new_bill
from .payment import find_all_transactions, generate_purchase_url
from .price import assign_item_price, get_all_pricing_schemes
from .product import add_new_catalog_item, fetch_all_catalog_items
from .refund import process_payment_reversal
from .subscription import modify_recurring_service, retrieve_recurring_services, terminate_customer_subscription

_function_map = {
    'add_item_to_bill': 'stripe.mutations.m01.invoice.add_item_to_bill',
    'add_new_catalog_item': 'stripe.mutations.m01.product.add_new_catalog_item',
    'assign_item_price': 'stripe.mutations.m01.price.assign_item_price',
    'complete_and_send_bill': 'stripe.mutations.m01.invoice.complete_and_send_bill',
    'fetch_all_catalog_items': 'stripe.mutations.m01.product.fetch_all_catalog_items',
    'fetch_available_discounts': 'stripe.mutations.m01.coupon.fetch_available_discounts',
    'find_all_transactions': 'stripe.mutations.m01.payment.find_all_transactions',
    'generate_new_discount_code': 'stripe.mutations.m01.coupon.generate_new_discount_code',
    'generate_purchase_url': 'stripe.mutations.m01.payment.generate_purchase_url',
    'get_account_balance': 'stripe.mutations.m01.balance.get_account_balance',
    'get_all_payment_disputes': 'stripe.mutations.m01.dispute.get_all_payment_disputes',
    'get_all_pricing_schemes': 'stripe.mutations.m01.price.get_all_pricing_schemes',
    'issue_new_bill': 'stripe.mutations.m01.invoice.issue_new_bill',
    'modify_recurring_service': 'stripe.mutations.m01.subscription.modify_recurring_service',
    'process_payment_reversal': 'stripe.mutations.m01.refund.process_payment_reversal',
    'register_new_client': 'stripe.mutations.m01.customer.register_new_client',
    'respond_to_payment_dispute': 'stripe.mutations.m01.dispute.respond_to_payment_dispute',
    'retrieve_client_list': 'stripe.mutations.m01.customer.retrieve_client_list',
    'retrieve_recurring_services': 'stripe.mutations.m01.subscription.retrieve_recurring_services',
    'terminate_customer_subscription': 'stripe.mutations.m01.subscription.terminate_customer_subscription',
}
