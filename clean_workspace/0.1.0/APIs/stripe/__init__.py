"""
Stripe API Simulation package.
"""

from . import balance
from . import coupon
from . import customer
from . import dispute
from . import invoice
from . import payment
from . import price
from . import product
from . import refund
from . import subscription

import os
from common_utils.error_handling import get_package_error_mode
from .SimulationEngine.db import DB, load_state, save_state
from common_utils.init_utils import create_error_simulator, resolve_function_import
from stripe.SimulationEngine import utils

# Get the directory of the current file
_INIT_PY_DIR = os.path.dirname(__file__)

# Create error simulator using the utility function
error_simulator = create_error_simulator(_INIT_PY_DIR)

# Get the error mode for the package
ERROR_MODE = get_package_error_mode()

# Function map
_function_map = {
        "create_customer": "stripe.customer.create_customer",
        "list_customers": "stripe.customer.list_customers",
        "create_product": "stripe.product.create_product",
        "list_products": "stripe.product.list_products",
        "create_price": "stripe.price.create_price",
        "list_prices": "stripe.price.list_prices",
        "create_payment_link": "stripe.payment.create_payment_link",
        "create_invoice": "stripe.invoice.create_invoice",
        "create_invoice_item": "stripe.invoice.create_invoice_item",
        "finalize_invoice": "stripe.invoice.finalize_invoice",
        "retrieve_balance": "stripe.balance.retrieve_balance",
        "create_refund": "stripe.refund.create_refund",
        "list_payment_intents": "stripe.payment.list_payment_intents",
        "list_subscriptions": "stripe.subscription.list_subscriptions",
        "cancel_subscription": "stripe.subscription.cancel_subscription",
        "update_subscription": "stripe.subscription.update_subscription",
        "list_coupons": "stripe.coupon.list_coupons",
        "create_coupon": "stripe.coupon.create_coupon",
        "update_dispute": "stripe.dispute.update_dispute",
        "list_disputes": "stripe.dispute.list_disputes",
}



def __getattr__(name: str):
    return resolve_function_import(name, _function_map, error_simulator)

def __dir__():
    return sorted(set(globals().keys()) | set(_function_map.keys()))

__all__ = list(_function_map.keys())
