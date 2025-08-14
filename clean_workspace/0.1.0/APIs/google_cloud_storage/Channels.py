from typing import Dict, Any, Tuple
def stop() -> Tuple[Dict[str, Any], int]:
    """
    Stops watching resources through the specified notification channel.

    Returns:
        Tuple[Dict[str, Any], int]:
        - On success:
            - A dictionary with a "message" key with value "Channel stopped"
            - A status code of 200 (OK)
    """
    # Simulate stopping a channel
    return {"message": "Channel stopped"}, 200