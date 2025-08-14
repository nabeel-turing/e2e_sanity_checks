from typing import Optional, List, Dict, Any

from stripe.SimulationEngine import utils
from stripe.SimulationEngine.custom_errors import InvalidRequestError, ApiError, ProductNotFoundError
from stripe.SimulationEngine.db import DB
from stripe.SimulationEngine.models import Product


def create_product(name: str, description: Optional[str] = None) -> Dict[str, Any]:
    """This tool will create a product in Stripe.

    This function creates a product in Stripe. It accepts a name for the product,
    which is mandatory, and an optional description to further detail the product.

    Args:
        name (str): The name of the product.
        description (Optional[str]): The description of the product.

    Returns:
        Dict[str, Any]: A dictionary representing the created Stripe product. Fields include:
            id (str): Unique identifier for the product.
            object (str): String representing the object's type, always "product".
            name (str): The product's name.
            description (Optional[str]): The product's description.
            active (bool): Whether the product is currently active and available for use.
            created (int): Unix timestamp of when the product was created.
            updated (int): Unix timestamp of when the product was last updated.
            livemode (bool): Indicates if the object exists in live mode (true) or test mode (false).
            metadata (Optional[Dict[str, str]]): A set of key-value pairs that you can attach to an object. It can be useful for storing additional information about the object in a structured format.

    Raises:
        InvalidRequestError: If required parameters are missing or invalid (e.g., name is empty).
        ApiError: For other general Stripe API errors (e.g., network issues, authentication problems).
    """
    # Type validation
    if not isinstance(name, str):
        raise InvalidRequestError("Product name must be a string.")
    if description is not None and not isinstance(description, str):
        raise InvalidRequestError("Product description must be a string.")

    # Empty validation
    if not name or not name.strip():
        raise InvalidRequestError("Product name cannot be empty.")

    # Clean input data
    cleaned_name = name.strip()
    cleaned_description = description.strip() if description is not None else None

    new_product = Product(
        name=cleaned_name,
        description=cleaned_description
    )

    DB['products'][new_product.id] = new_product.model_dump()
    return new_product.model_dump()


def list_products(limit: Optional[int] = 10) -> Dict[str, Any]:
    """This tool will fetch a list of Products from Stripe.

    This tool fetches a list of Products from Stripe. It takes one optional argument, `limit`, to specify the number of products to return.

    Args:
        limit (Optional[int]): A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10.

    Returns:
        Dict[str, Any]: A dictionary representing the Stripe list response for products. Contains the following keys:
            object (str): String representing the object's type, typically "list".
            data (List[Dict[str, Any]]): A list of product objects. Each product object includes the following fields:
                id (str): Unique identifier for the product.
                object (str): String representing the object's type, typically "product".
                name (str): The product's name, meant to be displayable to the customer.
                description (Optional[str]): The product's description, meant to be displayable to the customer. Null if not provided.
                active (bool): Whether the product is currently active and available for purchase.
                created (int): Unix timestamp representing when the object was created.
                livemode (bool): True if the object exists in live mode or false if the object exists in test mode.
                metadata (Optional[Dict[str, str]]): A set of key-value pairs that you can attach to an object. It can be useful for storing additional information about the object in a structured format.
            has_more (bool): True if there are more objects available after this list. If false, this list contains all remaining objects.

    Raises:
        InvalidRequestError: If the limit parameter is invalid (e.g., out of range).
        ApiError: For other general Stripe API errors (e.g., network issues, authentication problems).
    """
    effective_limit = limit if limit is not None else 10

    if not isinstance(effective_limit, int) or not (1 <= effective_limit <= 100):
        raise InvalidRequestError("Limit must be an integer between 1 and 100.")

    try:
        products_map: Dict[str, Dict[str, Any]] = utils._get_objects(DB, 'products')
        all_products_list: List[Dict[str, Any]] = list(products_map.values())
        sorted_products = sorted(all_products_list, key=lambda p: p['created'], reverse=True)

        # Apply limit for pagination
        paginated_products = sorted_products[:effective_limit]

        # Determine if there are more products beyond the current page
        has_more = len(sorted_products) > effective_limit

        response_data: List[Dict[str, Any]] = []
        for product_db_data in paginated_products:
            response_data.append(Product(**product_db_data).model_dump())

        return {
            "object": "list",
            "data": response_data,
            "has_more": has_more,
        }

    except KeyError as e:
        raise ApiError(f"Internal data error: Product data is missing an expected field: {str(e)}")
    except TypeError as e:
        raise ApiError(f"Internal data error: Product data has an invalid type for a field: {str(e)}")
    except Exception as e:
        raise ApiError(f"An unexpected error occurred while fetching products: {str(e)}")


def delete_product(product_id: str) -> Dict[str, Any]:
    """This tool will delete a product from Stripe.

    This function deletes a product from Stripe by its ID. The product will be permanently deleted
    and cannot be recovered.

    Args:
        product_id (str): The ID of the product to delete.

    Returns:
        Dict[str, Any]: A dictionary representing the deleted Stripe product. Fields include:
            id (str): Unique identifier for the product.
            object (str): String representing the object's type, always "product".
            deleted (bool): Always true for deleted objects.
            name (str): The product's name.
            description (Optional[str]): The product's description.
            active (bool): Whether the product was active.
            created (int): Unix timestamp of when the product was created.
            updated (int): Unix timestamp of when the product was last updated.
            livemode (bool): Indicates if the object existed in live mode (true) or test mode (false).
            metadata (Optional[Dict[str, str]]): Any metadata that was attached to the product.

    Raises:
        InvalidRequestError: If the product_id is invalid or empty.
        ApiError: If the product doesn't exist or if there are other general Stripe API errors.
        ProductNotFoundError: If the product does not exist.
    """
    # Type validation
    if not isinstance(product_id, str):
        raise InvalidRequestError("Product ID must be a string.")
    
    # Empty validation
    if not product_id or not product_id.strip():
        raise InvalidRequestError("Product ID cannot be empty.")

    # Clean input data
    cleaned_product_id = product_id.strip()

    try:
        # Check if product exists
        if cleaned_product_id not in DB['products']:
            raise ProductNotFoundError(f"No such product: {cleaned_product_id}")

        # Get the product data before deletion
        product_data = DB['products'][cleaned_product_id]
        
        # Delete the product
        del DB['products'][cleaned_product_id]

        # Return the deleted product data with deleted flag
        return {
            **product_data,
            "deleted": True
        }

    except Exception as e:
        raise ApiError(f"An unexpected error occurred while deleting the product: {str(e)}")
