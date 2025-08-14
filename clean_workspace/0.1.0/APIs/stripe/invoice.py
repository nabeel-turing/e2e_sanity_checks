from typing import Dict, Any, Optional
from stripe.SimulationEngine import utils
from stripe.SimulationEngine.custom_errors import ApiError, InvalidRequestError, ResourceNotFoundError, ValidationError
from pydantic import ValidationError as PydanticValidationError
from stripe.SimulationEngine.db import DB
from stripe.SimulationEngine.models import Invoice
from datetime import datetime, timedelta


def create_invoice(customer: str, days_until_due: Optional[int] = None) -> Dict[str, Any]:
    """This tool will create an invoice in Stripe.

    This tool creates an invoice in Stripe. It takes the ID of the customer (`customer`) for whom to create the invoice, and an optional number of days (`days_until_due`) until the invoice is due.

    Args:
        customer (str): The ID of the customer to create the invoice for.
        days_until_due (Optional[int]): The number of days until the invoice is due.

    Returns:
        Dict[str, Any]: The Stripe invoice object created. This dictionary contains the following keys:
            id (str): Unique identifier for the invoice.
            object (str): String representing the object's type, typically "invoice".
            customer (str): The ID of the customer this invoice is for.
            status (str): The status of the invoice (e.g., "draft", "open", "paid", "void", "uncollectible").
            total (int): Total amount due in cents.
            amount_due (int): The amount due on the invoice, in cents.
            currency (str): Three-letter ISO currency code.
            created (int): Unix timestamp of when the invoice was created.
            due_date (Optional[int]): Unix timestamp of the date on which payment for this invoice is due.
            livemode (bool): Indicates if the object exists in live mode or test mode.
            metadata (Optional[Dict[str, str]]): A set of key-value pairs attached to the invoice.
            lines (Dict[str, Any]): A list object representing the individual line items of the invoice. This dictionary contains:
                object (str): String representing the object's type, typically "list".
                data (List[Dict[str, Any]]): A list where each element is an invoice line item dictionary. Each such dictionary contains:
                    id (str): Unique identifier for the line item.
                    amount (int): The amount of the line item, in cents.
                    description (Optional[str]): An arbitrary string description for the line item.
                    price (Optional[Dict[str, Any]]): The price object used for this line item. This dictionary may contain:
                        id (str): Unique identifier of the price object.
                        product (str): ID of the product associated with this price.
                    quantity (Optional[int]): The quantity of the line item.
                has_more (bool): True if there are more line items to be fetched for this invoice (pagination).

    Raises:
        InvalidRequestError: If the customer ID is invalid or other parameters are malformed.
        ResourceNotFoundError: If the specified customer ID does not exist.
        ValidationError: If input arguments fail validation.
    """
# --- Input Validation performed within the function ---
    if not isinstance(customer, str):
        raise ValidationError("Customer ID must be a string.")
    if not customer:
        raise InvalidRequestError("Customer ID cannot be empty.")

    # Ensure 'customers' key exists in DB and that the customer ID is found.
    if customer not in DB['customers']:
        raise ResourceNotFoundError(f"Customer with ID '{customer}' not found.")

    due_date_timestamp: Optional[int] = None
    # `created_timestamp` will be set by Pydantic's default factory for `Invoice.created`
    # but we need a base for due_date calculation if `days_until_due` is provided.
    current_ts_for_due_date_calc = utils.get_current_timestamp()

    if days_until_due is not None:
        if not isinstance(days_until_due, int):
            raise ValidationError("Days until due must be an integer.")
        if days_until_due < 0:
            raise ValidationError("Days until due cannot be negative.")
        
        created_datetime = datetime.fromtimestamp(current_ts_for_due_date_calc)
        due_datetime = created_datetime + timedelta(days=days_until_due)
        due_date_timestamp = int(due_datetime.timestamp())

    # --- Prepare data for Pydantic Model ---
    # Pydantic model will handle default values for id, object, status, total,
    # amount_due, currency, created, livemode, lines.
    # We only need to pass fields that don't have defaults or that we want to override.
    invoice_creation_data: Dict[str, Any] = {
        "customer": customer,
    }

    if due_date_timestamp is not None:
        invoice_creation_data["due_date"] = due_date_timestamp
    
    # --- Create Invoice using Pydantic Model for structure and defaults ---
    try:
        new_invoice_model = Invoice(**invoice_creation_data)

    except PydanticValidationError as e:
        raise ValidationError(f"Invoice data validation failed by model: {e.errors()}")

    invoice_data_dict = new_invoice_model.model_dump(exclude_none=True)
    
    invoice_id = new_invoice_model.id

    DB['invoices'][invoice_id] = invoice_data_dict

    return invoice_data_dict


def create_invoice_item(customer: str, price: str, invoice: str) -> Dict[str, Any]:
    """This tool will create an invoice item in Stripe.

    This function creates an invoice item in Stripe. It uses the provided customer ID,
    price ID, and invoice ID to define the new invoice item's associations and
    link it to the respective customer, product/service price, and invoice.

    Args:
        customer (str): The ID of the customer to create the invoice item for.
        price (str): The ID of the price for the item.
        invoice (str): The ID of the invoice to create the item for.

    Returns:
        Dict[str, Any]: A dictionary representing the Stripe invoice item object that was created, with the following keys:
            id (str): Unique identifier for the invoice item.
            object (str): String representing the object's type, typically "invoiceitem".
            customer (str): The ID of the customer this invoice item is associated with.
            invoice (Optional[str]): The ID of the invoice this invoice item belongs to (if any).
            price (Optional[Dict[str, Any]]): The price object related to this invoice item. If present, it contains:
                id (str): The ID of the price.
                product (str): The ID of the product this price is for.
                unit_amount (Optional[int]): The unit amount in cents (if applicable).
                currency (str): Three-letter ISO currency code.
            amount (int): The amount in cents.
            currency (str): Three-letter ISO currency code.
            quantity (int): Quantity of the item.
            livemode (bool): Indicates if the object exists in live mode or test mode.
            metadata (Optional[Dict[str, str]]): A set of key-value pairs.

    Raises:
        InvalidRequestError: If customer ID, price ID, or invoice ID are invalid or parameters are malformed.
        ResourceNotFoundError: If any of the specified IDs (customer, price, invoice) do not exist.
        ApiError: For other general Stripe API errors.
    """
    if not (isinstance(customer, str) and customer.strip()):
        raise InvalidRequestError("Customer ID must be a non-empty string.")
    if not (isinstance(price, str) and price.strip()):
        raise InvalidRequestError("Price ID must be a non-empty string.")
    if not (isinstance(invoice, str) and invoice.strip()):
        raise InvalidRequestError("Invoice ID must be a non-empty string.")

    customer_obj = utils._get_object_by_id(DB, customer, 'customers')
    if not customer_obj:
        raise ResourceNotFoundError(f"Customer with ID '{customer}' not found.")

    price_obj = utils._get_object_by_id(DB, price, 'prices')
    if not price_obj:
        raise ResourceNotFoundError(f"Price with ID '{price}' not found.")

    invoice_obj = utils._get_object_by_id(DB, invoice, 'invoices')
    if not invoice_obj:
        raise ResourceNotFoundError(f"Invoice with ID '{invoice}' not found.")

    # Check if the price is active and retrieve essential fields

    if not price_obj['active']:
        raise InvalidRequestError(f"Price with ID '{price}' is not active and cannot be used.")

    price_unit_amount = price_obj['unit_amount']
    price_currency = price_obj['currency']
    price_product_id = price_obj['product']

    # Default quantity for the invoice item (as it's not an argument)
    quantity = 1

    # Calculate amount for the invoice item
    item_amount = price_unit_amount * quantity

    # Prepare the nested price data for the invoice item, as per return spec
    invoice_item_price_data = {
        "id": price_obj['id'],
        "product": price_product_id,
        "unit_amount": price_unit_amount,
        "currency": price_currency
    }

    # Create the new invoice item dictionary
    new_invoice_item_id = utils.generate_id("inv")
    new_invoice_item = {
        "id": new_invoice_item_id,
        "object": "invoiceitem",
        "customer": customer_obj['id'],
        "invoice": invoice_obj['id'],
        "price": invoice_item_price_data,
        "amount": item_amount,
        "currency": price_currency,
        "quantity": quantity,
        "livemode": False,
        "metadata": None
    }

    DB['invoice_items'][new_invoice_item_id] = new_invoice_item

    # Recalculate totals for the associated invoice using the helper function
    try:
        utils._recalculate_invoice_totals(DB, invoice_obj['id'])
    except Exception as e:
        DB['invoice_items'].pop(new_invoice_item_id, None)  # Attempt to clean up
        raise ApiError(f"Failed to update invoice totals after creating invoice item: {str(e)}")

    return new_invoice_item


def finalize_invoice(invoice: str) -> Dict[str, Any]:
    """This tool will finalize an invoice in Stripe.

    This function finalizes an invoice in Stripe. It takes the ID of the invoice to finalize as an argument.

    Args:
        invoice (str): The ID of the invoice to finalize.

    Returns:
        Dict[str, Any]: A dictionary containing the Stripe invoice object that was finalized. Its structure is similar to the invoice object from `create_invoice`, with an updated status (e.g., "open"). It includes the following keys:
            id (str): Unique identifier for the invoice.
            object (str): String representing the object's type, typically "invoice".
            status (str): The status of the invoice, typically "open" after finalization.
            total (int): Total amount due in cents.
            customer (str): The ID of the customer.
            currency (str): Three-letter ISO currency code.
            due_date (Optional[int]): Unix timestamp of the due date. This field may not be present if no due date is set.
            lines (Dict[str, Any]): A Stripe list object containing invoice line items. This object includes:
                object (str): The type of object, typically "list".
                data (List[Dict[str, Any]]): An array of invoice line item objects. (The structure of these line items is detailed in the `create_invoice` method's documentation).
                has_more (bool): A flag indicating true if there are more line items to be fetched.
            livemode (bool): Indicates if the object exists in live mode (true) or test mode (false).

    Raises:
        InvalidRequestError: If the invoice ID is invalid, the invoice cannot be finalized (e.g., already finalized, no line items, or customer has no payment method for auto-payment).
        ResourceNotFoundError: If the specified invoice ID does not exist.
    """
    if not (invoice and isinstance(invoice, str)):
        raise InvalidRequestError("invoice must be a string and not empty")

    invoice_obj = utils._get_object_by_id(DB, invoice, "invoices")
    if invoice_obj is None:
        raise ResourceNotFoundError(f"invoice {invoice} does not exist")

    if invoice_obj["status"] != "draft":
        raise InvalidRequestError("invoice must be in draft status to be finalized")

    # Find all invoice items for this invoice
    invoice_line_items = []
    total = 0

    for item in utils._get_objects(DB, "invoice_items").values():
        if item.get('invoice') == invoice:
            # Create line item from invoice item
            line_item = {
                "id": item['id'],
                "amount": item['amount'],
                "description": f"Invoice item {item['id']}",  # Auto-generated description
                "price": {
                    "id": item['price']['id'],
                    "product": item['price']['product']
                },
                "quantity": item.get('quantity', 1)
            }
            invoice_line_items.append(line_item)
            total += item['amount']

    # Check if there are any line items
    if not invoice_line_items:
        raise InvalidRequestError("invoice cannot be finalized without line items")

    # Update the invoice with line items and totals
    invoice_obj["status"] = "open"
    invoice_obj["total"] = total
    invoice_obj["amount_due"] = total
    invoice_obj["lines"] = {
        "object": "list",
        "data": invoice_line_items,
        "has_more": False
    }

    DB['invoices'][invoice] = invoice_obj
    return invoice_obj
