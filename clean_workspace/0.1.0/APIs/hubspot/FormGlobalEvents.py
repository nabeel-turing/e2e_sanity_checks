# APIs/hubspot/FormGlobalEvents.py
from typing import Optional, Dict, Any, List
import uuid
from hubspot.SimulationEngine.db import DB


def get_subscription_definitions() -> List[Dict[str, Any]]:
    """
    Get all global form event subscription definitions.

    Returns:
        List[Dict[str, Any]]: A list of all global form event subscription definitions.
            - id(str): The id of the subscription definition.
            - endpoint(str): The endpoint of the subscription definition.
            - subscriptionDetails(Dict[str, Any]): The subscription details of the subscription definition.
                - contact_id(str): The id of the contact.
                - subscription_id(str): The id of the subscription.
                - subscribed(bool): Whether the contact is subscribed to the subscription.
                - opt_in_date(str): The date the contact opted in to the subscription.
            - active(bool): Whether the subscription definition is active.
    """
    return DB["subscription_definitions"]


def create_subscription(
    endpoint: str, subscriptionDetails: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Creates a new webhook subscription for global form events.

    Args:
        endpoint(str): The endpoint of the subscription definition.
        subscriptionDetails(Dict[str, Any]): The subscription details of the subscription definition.
            - contact_id(str): The id of the contact.
            - subscription_id(str): The id of the subscription.
            - subscribed(bool): Whether the contact is subscribed to the subscription.
            - opt_in_date(str): The date the contact opted in to the subscription.

    Returns:
        Dict[str, Any]: The new webhook subscription for global form events.
            - id(str): The id of the subscription definition.
            - endpoint(str): The endpoint of the subscription definition.
            - subscriptionDetails(Dict[str, Any]): The subscription details of the subscription definition.
                - contact_id(str): The id of the contact.
                - subscription_id(str): The id of the subscription.
                - subscribed(bool): Whether the contact is subscribed to the subscription.
                - opt_in_date(str): The date the contact opted in to the subscription.
            - active(bool): Whether the subscription definition is active.
    """
    new_subscription_id = str(uuid.uuid4())
    new_subscription = {
        "id": new_subscription_id,
        "endpoint": endpoint,
        "subscriptionDetails": subscriptionDetails,
        "active": True,  # Initially active
    }
    DB["subscriptions"][new_subscription_id] = new_subscription
    return new_subscription


def get_subscriptions() -> List[Dict[str, Any]]:
    """
    Gets all webhook subscriptions for global form events.

    Returns:
        List[Dict[str, Any]]: A list of all webhook subscriptions for global form events.
            - id(str): The id of the subscription definition.
            - endpoint(str): The endpoint of the subscription definition.
            - subscriptionDetails(Dict[str, Any]): The subscription details of the subscription definition.
                - contact_id(str): The id of the contact.
                - subscription_id(str): The id of the subscription.
                - subscribed(bool): Whether the contact is subscribed to the subscription.
                - opt_in_date(str): The date the contact opted in to the subscription.
            - active(bool): Whether the subscription definition is active.
    """
    return list(DB["subscriptions"].values())


def delete_subscription(subscriptionId: int) -> None:
    """
    Deletes (unsubscribes) a webhook subscription.

    Args:
        subscriptionId(int): The id of the subscription definition.

    Returns:
        None

    Raises:
        ValueError: If the subscription with the given id is not found.
    """
    subscriptionId = int(subscriptionId)  # DB has string type for subscription id
    if subscriptionId not in DB["subscriptions"]:
        raise ValueError(f"Subscription with id '{subscriptionId}' not found")
    del DB["subscriptions"][subscriptionId]


def update_subscription(subscriptionId: int, active: bool) -> Dict[str, Any]:
    """
    Updates (specifically, activates or deactivates) a webhook subscription.

    Args:
        subscriptionId(int): The id of the subscription definition.
        active(bool): Whether the subscription definition is active.

    Returns:
        Dict[str, Any]: The updated webhook subscription.
            - id(str): The id of the subscription definition.
            - endpoint(str): The endpoint of the subscription definition.
            - subscriptionDetails(Dict[str, Any]): The subscription details of the subscription definition.
                - contact_id(str): The id of the contact.
                - subscription_id(str): The id of the subscription.
                - subscribed(bool): Whether the contact is subscribed to the subscription.
                - opt_in_date(str): The date the contact opted in to the subscription.
            - active(bool): Whether the subscription definition is active.
    """
    subscriptionId = int(subscriptionId)  # DB has string type for subscription id

    if subscriptionId not in DB["subscriptions"]:
        raise ValueError(f"Subscription with id '{subscriptionId}' not found")

    subscription = DB["subscriptions"][subscriptionId]
    subscription["active"] = active
    return subscription
