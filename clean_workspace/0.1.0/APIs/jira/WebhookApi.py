# APIs/jira/WebhookApi.py
from .SimulationEngine.db import DB
from .SimulationEngine.utils import _check_empty_field, _generate_id
from typing import List, Dict, Any
from typing import List, Dict, Any


def create_or_get_webhooks(webhooks: List[Dict]) -> Dict[str, Any]:
    """
    Create or get webhooks.

    Args:
        webhooks (List[Dict]): The webhooks to create or get.

    Returns:
        Dict[str, Any]: A dictionary containing the webhooks' information.
            - registered (bool): Whether the webhooks were registered.
            - webhookIds (List[str]): The IDs of the webhooks that were registered.

    """
    err = _check_empty_field("webhooks", webhooks)
    if err:
        return {"error": err}
    # For example, store them in DB
    new_ids = []
    for wh in webhooks:
        wh_id = _generate_id("WEBHOOK", DB["webhooks"])
        DB["webhooks"][wh_id] = wh
        new_ids.append(wh_id)
    return {"registered": True, "webhookIds": new_ids}


def get_webhooks() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get all webhooks.

    Returns:
        Dict[str, List[Dict[str, Any]]]: A dictionary containing the webhooks' information.
            - webhooks (List[Dict[str, Any]]): The webhooks' information.
                - id (str): The ID of the webhook.
                - url (str): The URL of the webhook.
                - events (List[str]): The events that the webhook is subscribed to.
    """
    return {"webhooks": list(DB["webhooks"].values())}


def delete_webhooks(webhookIds: List[str]) -> Dict[str, Any]:
    """
    Delete webhooks.

    Args:
        webhookIds (List[str]): The IDs of the webhooks to delete.

    Returns:
        Dict[str, Any]: A dictionary containing the webhooks' information.
            - deleted (List[str]): The IDs of the webhooks that were deleted.
    Raises:
        TypeError: If webhookIds is not a list or contains non-string elements.
    """
    # 1. Type validation - ensures it's a list
    if not isinstance(webhookIds, list):
        raise TypeError("webhookIds must be a list.")
    
    # 2. Content validation - ensures all elements are strings
    if not all(isinstance(wid, str) for wid in webhookIds):
        raise TypeError("All webhookIds must be strings.")

    # 3. Emptiness validation - ensures at least one ID is provided
    err = _check_empty_field("webhookIds", webhookIds)
    if err:
        return {"error": err}

    deleted = []
    for wid in webhookIds:
        if wid in DB["webhooks"]:
            DB["webhooks"].pop(wid)
            deleted.append(wid)

    return {"deleted": deleted}
