
from typing import Optional, List, Dict, Any
from stripe.SimulationEngine.db import DB
from stripe.SimulationEngine.custom_errors import InvalidRequestError, ValidationError
from stripe.SimulationEngine import utils


def list_coupons(limit: Optional[int] = None) -> Dict[str, Any]:
    """This tool will fetch a list of Coupons from Stripe.

    This function fetches a list of Coupons from Stripe. It takes one optional argument,
    `limit`, which is an integer used to specify the number of coupons to return.

    Args:
        limit (Optional[int]): A limit on the number of objects to be returned. Limit can range between 1 and 100.

    Returns:
        Dict[str, Any]: A dictionary containing the list of coupons and related information. It includes the following keys:
            object (str): String representing the object's type, typically "list".
            data (List[Dict[str, Any]]): A list of coupon objects. Each dictionary in the list represents a coupon and contains the following keys:
                id (str): Unique identifier for the coupon.
                object (str): String representing the object's type, typically "coupon".
                name (Optional[str]): Name of the coupon.
                percent_off (Optional[float]): Percent-off discount of the coupon.
                amount_off (Optional[int]): Amount (in cents) that will be taken off the subtotal of any invoices for this customer.
                currency (Optional[str]): If `amount_off` is present, the currency of the amount to take off.
                duration (str): Describes how long a customer who applies this coupon will get the discount (e.g., 'once', 'repeating', 'forever').
                duration_in_months (Optional[int]): If `duration` is 'repeating', the number of months the coupon applies.
                livemode (bool): Indicates if the object exists in live mode or test mode.
                valid (bool): Whether the coupon is currently valid and can be used.
                metadata (Optional[Dict[str, str]]): A set of key-value pairs.
            has_more (bool): True if there are more coupons to retrieve.

    Raises:
        InvalidRequestError: If the limit parameter is invalid (e.g., not an integer or out of range).
        ValidationError: If input arguments fail validation.
    """

    # Validate the 'limit' argument if provided.
    if limit is not None:
        if not isinstance(limit, int):
            # The docstring for InvalidRequestError specifies it covers "not an integer".
            raise InvalidRequestError("Limit must be an integer.")
        if not (1 <= limit <= 100):
            # The docstring for InvalidRequestError specifies it covers "out of range".
            raise InvalidRequestError("Limit must be an integer between 1 and 100.")

    # Retrieve all coupon data from the DB.
    coupons_map: Dict[str, Dict[str, Any]] = DB.get('coupons', {})
    
    # Convert the map values (coupon dictionaries) into a list.
    all_coupons_list: List[Dict[str, Any]] = list(coupons_map.values())

    # Sort the list of coupons. Sorting by 'id' ensures a consistent order,
    all_coupons_list.sort(key=lambda coupon: coupon['id'])
    
    # Prepare the list of coupons to be returned and the 'has_more' flag.
    data_to_return: List[Dict[str, Any]]
    has_more: bool = False

    if limit is None:
        # If no limit is specified, return all coupons.
        data_to_return = all_coupons_list
    else:
        # If a limit is specified, slice the sorted list to get the desired number of coupons.
        data_to_return = all_coupons_list[:limit]
        # Determine if there are more coupons available than what is being returned.
        if len(all_coupons_list) > limit:
            has_more = True
            
    # Construct the final response dictionary according to the specified structure.
    response: Dict[str, Any] = {
        "object": "list",
        "data": data_to_return,
        "has_more": has_more,
    }

    return response

def create_coupon(
        name: str,
        amount_off: int,
        currency: Optional[str] = "USD",
        duration: Optional[str] = "once",
        percent_off: Optional[float] = None,
        duration_in_months: Optional[int] = None
) -> Dict[str, Any]:
    """
    This function creates a coupon in Stripe. The discount can be specified either as a percentage off via `percent_off`
    or as a fixed amount off via `amount_off`. It is essential that only one of these, `percent_off` or `amount_off`,
    is used to define the discount; providing values for both, or values for neither
    that define a valid discount, will result in an error. If `amount_off` is used as the discount method,
    the `currency` parameter must also be appropriately set (it defaults to 'USD').
    The function also supports optional parameters to define the coupon's duration. The `duration`
    parameter specifies how long the discount remains active and accepts 'once', 'repeating', or 'forever'
    (defaulting to 'once'). If `duration` is 'repeating', the `duration_in_months` parameter is
    required to indicate the number of months the coupon applies.

    Args:
        name (str): Name of the coupon displayed to customers on invoices or receipts.
        amount_off (int): A positive integer representing the amount to subtract from an
            invoice total. This parameter is required by the function signature.
        currency (Optional[str]): Three-letter ISO code for the currency of the `amount_off`
            parameter (e.g., 'USD', 'EUR'). This is required if `amount_off` is used to
            specify the discount and `percent_off` is not provided. Defaults to 'USD'.
        duration (Optional[str]): Specifies how long the discount will last. Valid values
            are 'once', 'repeating', or 'forever'. Defaults to 'once'.
        percent_off (Optional[float]): A positive float greater than or equal to 0 and less than or
            equal to 100, representing the percentage discount the coupon will apply.
            If provided, this defines the coupon's discount instead of `amount_off`.
        duration_in_months (Optional[int]): If `duration` is 'repeating', this specifies
            the number of months the discount will apply.

    Returns:
        Dict[str, Any]: A dictionary representing the Stripe coupon object that was created.
            This dictionary contains information about the coupon, including its ID,
            discount details, duration, and validity. The structure includes the
            following keys:
            id (str): Unique identifier for the coupon.
            object (str): String representing the object's type, always "coupon".
            name (Optional[str]): Name of the coupon.
            percent_off (Optional[float]): Percent-off discount of the coupon. A positive
                float between 0 (exclusive) and 100 (inclusive). Null if
                'amount_off' is set as the discount method.
            amount_off (Optional[int]): Amount (in cents) that will be taken off the
                subtotal. A positive integer. Null if 'percent_off' is set as the
                discount method.
            currency (Optional[str]): If 'amount_off' is present and used for the discount,
                the three-letter ISO currency code (e.g., 'usd', 'eur') for the amount.
            duration (str): Describes how long a customer who applies this coupon will
                get the discount. One of 'once', 'repeating', or 'forever'.
            duration_in_months (Optional[int]): If 'duration' is 'repeating', this is
                the number of months the coupon applies.
            livemode (bool): True if the object exists in live mode, or false if the
                object exists in test mode.
            valid (bool): True if the coupon is currently valid and can be used,
                false otherwise.
            metadata (Optional[Dict[str, str]]): A set of key-value pairs that you can
                attach to an object. Useful for storing additional information.

    Raises:
        InvalidRequestError: If parameters are invalid
        ValidationError: If input arguments fail validation.
    """

    # 1. Type Validations
    if not isinstance(name, str):
        raise ValidationError("Argument 'name' must be a string.")
    if not isinstance(amount_off, int):
        raise ValidationError("Argument 'amount_off' must be an integer.")
    if currency is not None and not isinstance(currency, str):
        raise ValidationError("Argument 'currency' must be a string or None.")
    if duration is not None and not isinstance(duration, str):
        raise ValidationError("Argument 'duration' must be a string or None.")
    if percent_off is not None and not isinstance(percent_off, float):
        raise ValidationError("Argument 'percent_off' must be a float or None.")
    if duration_in_months is not None and not isinstance(duration_in_months, int):
        raise ValidationError("Argument 'duration_in_months' must be an integer or None.")

    # 2. Value and Logic Validations

    # Name validation
    if not name.strip():  # Check if name is empty or consists only of whitespace
        raise InvalidRequestError("Coupon name cannot be empty.")

    has_percent_discount = percent_off is not None
    has_amount_discount = amount_off > 0
    coupon_data_percent_off: Optional[float] = None
    coupon_data_amount_off: Optional[int] = None
    coupon_data_currency: Optional[str] = None

    if has_percent_discount and has_amount_discount:
        raise InvalidRequestError(
            "Cannot specify both 'percent_off' and a positive 'amount_off'. Provide only one discount method."
        )
    elif not has_percent_discount and not has_amount_discount:
        raise InvalidRequestError(
            "A discount must be specified. Provide either 'percent_off' or a positive 'amount_off'."
        )
    elif has_percent_discount:
        # percent_off is already validated as float if not None.
        if not (0 <= percent_off <= 100):
            raise InvalidRequestError(
                "'percent_off' must be a positive float greater than 0 and up to 100."
            )
        coupon_data_percent_off = percent_off
    else:
        if currency is None or not currency.strip():
            raise InvalidRequestError(
                "'currency' is required when 'amount_off' is used for the discount."
            )
        coupon_data_amount_off = amount_off
        coupon_data_currency = currency.lower()

    final_duration = duration if duration is not None else "once"

    valid_durations = {"once", "repeating", "forever"}
    if final_duration not in valid_durations:
        raise InvalidRequestError(
            f"Invalid duration: '{final_duration}'. Must be one of {', '.join(sorted(list(valid_durations)))}."
        )

    coupon_data_duration_in_months: Optional[int] = None
    if final_duration == "repeating":
        if duration_in_months is None:
            raise InvalidRequestError(
                "'duration_in_months' is required when duration is 'repeating'."
            )
        if duration_in_months <= 0:
            raise InvalidRequestError(
                "'duration_in_months' must be a positive integer for repeating duration."
            )
        coupon_data_duration_in_months = duration_in_months

    # 3. Create Coupon Object
    coupon_id = utils.generate_id("cou")

    coupon_object: Dict[str, Any] = {
        "id": coupon_id,
        "object": "coupon",
        "name": name,
        "percent_off": coupon_data_percent_off,
        "amount_off": coupon_data_amount_off,
        "currency": coupon_data_currency,
        "duration": final_duration,
        "duration_in_months": coupon_data_duration_in_months,
        "livemode": False,
        "valid": True,
        "metadata": None
    }

    DB['coupons'][coupon_id] = coupon_object

    return coupon_object