from typing import Dict, Any, Optional

from stripe.SimulationEngine import utils
from stripe.SimulationEngine.custom_errors import ResourceNotFoundError, InvalidRequestError
from stripe.SimulationEngine.db import DB


def create_payment_link(price: str, quantity: int) -> Dict[str, Any]:
    """Creates a payment link in Stripe.

    This function creates a payment link in Stripe. It takes the ID of the price
    to create the payment link for and the quantity of the product to include
    in the payment link.

    Args:
        price (str): The ID of the price to create the payment link for.
        quantity (int): The quantity of the product to include.

    Returns:
        Dict[str, Any]: A dictionary representing the Stripe payment link object that was created. It contains the following keys:
            id (str): Unique identifier for the payment link.
            object (str): String representing the object's type, typically "payment_link".
            active (bool): Whether the payment link is active and can be used to create new Checkout Sessions.
            livemode (bool): Indicates if the object exists in live mode or test mode.
            metadata (Optional[Dict[str, str]]): A set of key-value pairs that you can attach to an object. It can be useful for storing additional information about the object in a structured format.
            line_items (Dict[str, Any]): A Stripe list object containing the line items for this payment link. This dictionary contains the following keys:
                object (str): String representing the list object's type, typically "list".
                data (List[Dict[str, Any]]): A list of line item objects. Each dictionary in the list represents a line item and contains the following keys:
                    id (str): Unique identifier for the line item.
                    price (Dict[str, Any]): The price object used for this line item. This dictionary contains the following keys:
                        id (str): Unique identifier of the price.
                        product (str): Identifier of the product associated with this price.
                    quantity (int): The quantity of the product for this line item.
                has_more (bool): A flag indicating if there are more line items to be fetched for this list.
            after_completion (Dict[str, Any]): Configuration for behavior after the purchase is complete. This dictionary contains the following keys:
                type (str): The type of an after-completion behavior (e.g., 'redirect', 'hosted_confirmation').
                redirect (Optional[Dict[str, Any]]): If `type` is 'redirect', this hash contains information about the redirect configuration (e.g., a success message).

    Raises:
        InvalidRequestError: If the price ID is invalid, quantity is invalid, or other parameters are malformed.
        ResourceNotFoundError: If the specified price ID does not exist.
    """

    # 1. Input validation
    if not isinstance(price, str):
        raise InvalidRequestError("Price ID must be a string.")
    if not price:  # Check for empty string price ID
        raise InvalidRequestError("Price ID cannot be empty.")

    if not isinstance(quantity, int):
        raise InvalidRequestError("Quantity must be an integer.")
    if quantity <= 0:
        raise InvalidRequestError("Quantity must be greater than 0.")

    # 2. Fetch Price object from DB
    # DB['prices'] is expected to be a Dict[str, Dict[str, Any]] representing Price objects
    price_obj = utils._get_object_by_id(DB, price, "prices")
    if not price_obj:
        raise ResourceNotFoundError(f"No such price: '{price}'")

    # 3. Check if price is active
    # The Price schema indicates 'active' is a boolean field.
    if not price_obj.get('active'):
        raise InvalidRequestError(f"Price '{price}' is not active and cannot be used to create a payment link.")

    # 4. Get product ID from price object
    # The Price schema indicates 'product' is a required string field (Product ID).
    product_id = price_obj.get('product')
    if not product_id:
        # This implies data inconsistency, as 'product' is required by the Price schema.
        raise InvalidRequestError(f"Price '{price}' is malformed: missing product ID.")

    # 5. Construct the PaymentLink object (as a dictionary)
    payment_link_id = utils.generate_id("pl")
    line_item_id = utils.generate_id("sli")  # Simulated Line Item ID

    payment_link_data: Dict[str, Any] = {
        "id": payment_link_id,
        "object": "payment_link",
        "active": True,
        "livemode": False,
        "metadata": None,  # Conforms to Optional[Dict[str, str]] = None in schema
        "line_items": {
            "object": "list",
            "data": [
                {
                    "id": line_item_id,
                    "price": {
                        "id": price,  # The input price ID
                        "product": product_id  # Fetched product ID
                    },
                    "quantity": quantity
                }
            ],
            "has_more": False,
        },
        "after_completion": {
            "type": "hosted_confirmation",
            "redirect": None  # As 'type' is 'hosted_confirmation', 'redirect' is None
        }
    }

    # 6. Store in DB
    # DB['payment_links'] is expected to be Dict[str, Dict[str, Any]]
    # The StripeDB model initializes 'payment_links' as an empty dict if not present.
    DB['payment_links'][payment_link_id] = payment_link_data

    # 7. Return the created object
    return payment_link_data


def list_payment_intents(customer: Optional[str] = None, limit: Optional[int] = None) -> Dict[str, Any]:
    """This tool will list payment intents in Stripe.

    This function lists payment intents in Stripe. It takes an optional customer ID
    to list payment intents for a specific customer, and an optional limit to specify
    the number of payment intents to return.

    Args:
        customer (Optional[str]): The ID of the customer to list payment intents for.
        limit (Optional[int]): A limit on the number of objects to be returned. Limit can range between 1 and 100.

    Returns:
        Dict[str, Any]: A dictionary representing the API response for listing payment intents. This dictionary contains the following keys:
            object (str): String representing the object's type, typically "list".
            data (List[Dict[str, Any]]): A list of payment intent objects. Each payment intent dictionary in this list includes the following fields:
                id (str): Unique identifier for the payment intent.
                object (str): String representing the object's type, typically "payment_intent".
                amount (int): Amount intended to be collected, in cents.
                currency (str): Three-letter ISO currency code.
                customer (Optional[str]): ID of the customer this PaymentIntent belongs to, if one exists.
                status (str): Status of this PaymentIntent (e.g., "requires_payment_method", "succeeded").
                created (int): Unix timestamp of when the payment intent was created.
                livemode (bool): Indicates if the object exists in live mode or test mode.
                metadata (Optional[Dict[str, str]]): A set of key-value pairs associated with the payment intent.
            has_more (bool): True if there are more payment intents to retrieve, false otherwise.

    Raises:
        InvalidRequestError: If filter parameters are invalid.
        ResourceNotFoundError: If the specified customer ID does not exist (when provided).
    """
    # Validate input parameters
    if limit is not None:
        if not isinstance(limit, int):
            raise InvalidRequestError("Limit must be an integer.")
        if limit < 1:
            raise InvalidRequestError("Limit must be at least 1.")
        if limit > 100:
            raise InvalidRequestError("Limit cannot exceed 100.")
    else:
        limit = 10

    # Validate customer if provided
    if customer is not None:
        if not isinstance(customer, str):
            raise InvalidRequestError("Customer ID must be a string.")
        if customer not in DB['customers']:
            raise ResourceNotFoundError("Customer not found.")

    # Get payment intents from DB
    all_intents = utils._get_objects(DB, "payment_intents")

    # Get filtered intents as a list and sort in a single step
    intents = sorted(
        [intent for intent in all_intents.values()
         if customer is None or intent.get('customer') == customer],
        key=lambda x: x.get('created', 0),
        reverse=True
    )
    has_more = limit < len(intents)
    intents = intents[:limit]

    # Return formatted response
    return {
        "object": "list",
        "data": intents,
        "has_more": has_more
    }
