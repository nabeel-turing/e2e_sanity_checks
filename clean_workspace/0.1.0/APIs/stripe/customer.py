from typing import Optional, Dict, Any, List

from pydantic import ValidationError, validate_email

from stripe.SimulationEngine.custom_errors import InvalidRequestError
from stripe.SimulationEngine.db import DB
from stripe.SimulationEngine.models import Customer
from stripe.SimulationEngine import utils


def create_customer(name: str, email: Optional[str] = None) -> Dict[str, Any]:
    """This tool creates a customer in Stripe.

    Args:
        name (str): The name of the customer.
        email (Optional[str]): The email of the customer.

    Returns:
        Dict[str, Any]: A dictionary representing the created Stripe customer object, with the following keys:
            id (str): Unique identifier for the customer.
            object (str): String representing the object's type, typically "customer".
            name (str): The customer's full name or business name.
            email (Optional[str]): The customer's email address.
            created (int): Unix timestamp of when the customer was created.
            livemode (bool): Indicates if the object exists in live mode or test mode.
            metadata (Optional[Dict[str, str]]): A set of key-value pairs that can be attached to the object.

    Raises:
        InvalidRequestError: If required parameters are missing, or if any parameters are invalid (e.g., malformed email).
    """
    if not name or not name.strip():
        raise InvalidRequestError("Customer name cannot be empty.")

    try:
        customer_init_data = {"name": name}
        if email is not None:
            # Only include email in initialization data if it's provided,
            customer_init_data["email"] = email
        new_customer_obj = Customer(**customer_init_data)

    except ValidationError as e:
        error_messages = []
        for error in e.errors():
            # error['loc'] is a tuple representing the path to the error, e.g., ('email',)
            field_path = " -> ".join(map(str, error['loc']))
            message = error['msg']
            error_messages.append(f"Invalid parameter: '{field_path}' - {message}")
        raise InvalidRequestError(f"Input validation failed: {'; '.join(error_messages)}")

    customer_dict_to_store = new_customer_obj.model_dump()
    DB['customers'][customer_dict_to_store['id']] = customer_dict_to_store
    return customer_dict_to_store


def list_customers(limit: Optional[int] = None, email: Optional[str] = None) -> Dict[str, Any]:
    """This function fetches a list of Customers from Stripe. It processes an optional `limit`
    to control the number of customers retrieved and an optional `email` to filter
    customers by their email address in a case-sensitive manner.

    Args:
        limit (Optional[int]): A limit on the number of objects to be returned. Limit can range between 1 and 100.
        email (Optional[str]): A case-sensitive filter on the list based on the customer's email field. The value must be a string.

    Returns:
        Dict[str, Any]: A dictionary representing the list of customers. It contains the following keys:
            object (str): String representing the object's type, typically "list".
            data (List[Dict[str, Any]]): A list of customer objects. Each customer object within this list contains the following fields:
                id (str): Unique identifier for the customer.
                object (str): String representing the object's type, typically "customer".
                name (str): The customer's full name or business name.
                email (Optional[str]): The customer's email address.
                created (int): Unix timestamp of when the customer was created.
                livemode (bool): Indicates if the object exists in live mode or test mode.
                metadata (Optional[Dict[str, str]]): A set of key-value pairs that can be attached to an object.
            has_more (bool): True if there are more customers to retrieve, false otherwise. This is used for pagination.

    Raises:
        InvalidRequestError: If filter parameters are invalid (e.g., an invalid value for 'limit').
    """

    effective_limit: int
    if limit is not None:
        # Validate the provided limit.
        if not isinstance(limit, int) or not (1 <= limit <= 100):
            # Raise InvalidRequestError if limit is not an int or out of the allowed range.
            raise InvalidRequestError("Limit must be an integer between 1 and 100.")
        effective_limit = limit
    else:
        effective_limit = 10
    all_customer_records: List[Dict[str, Any]] =  list(utils._get_objects(DB, 'customers').values())
    all_customer_records.sort(key=lambda c: c.get('created', 0), reverse=True)

    # Apply email filter if an email string is provided.
    # An empty string for email is a valid filter criterion.
    if email is not None:
        try:
            validated_email = validate_email(email)
        except Exception:
            raise InvalidRequestError("Email is not valid")

        filtered_customer_records = [
            cust for cust in all_customer_records if cust.get('email') == validated_email[1]
        ]
    else:
        # If no email filter is applied, all customers are considered.
        filtered_customer_records = all_customer_records

    # Paginate the filtered results based on the effective_limit.
    customers_page: List[Dict[str, Any]] = filtered_customer_records[:effective_limit]

    # Determine if there are more records available beyond this current page.
    has_more: bool = len(filtered_customer_records) > effective_limit
    response_dict: Dict[str, Any] = {
        "object": "list",
        "data": customers_page,
        "has_more": has_more,
    }
    return response_dict